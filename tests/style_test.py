# -*- coding: utf-8 -*-
"""Style check for comments and docstrings.

Two things must not come back when more gets written later: German
comments (the interface stays German, the code does not) and narrating
comments. A comment explains the code, it does not report what stood
there before or how much trouble it was.

The language check runs as a ratchet: the number of German passages
lives in style_state.json and may only fall. While the changeover is
running, that holds the progress without turning the test red.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import ast, io, json, re, sys, tokenize

STATE = os.path.join(HERE, "state", "style_state.json")

def state_is_ours():
    """Whether this run may move the ratchet.

    A ratchet is only worth something while it stands for the file in
    the working tree. VPM_SCRIPT lets a run measure a snapshot instead,
    and every ratchet here writes itself down as soon as a count comes
    out lower -- so one run against an older or shorter copy pulls the
    ratchet down for good, to a number the real file may never reach
    again. Found on 24.8.2026, after a day of running the suite against
    snapshots in /tmp.

    So: measure whatever VPM_SCRIPT points at, but write the state down
    only where that is the file this repository ships.
    """
    named = os.environ.get("VPM_SCRIPT")
    if not named:
        return True
    here = os.path.join(os.path.dirname(HERE), "videopodcast-magic.py")
    try:
        return os.path.samefile(named, here)
    except OSError:
        return False
LINE_MAX = 79
BLOCK_MAX = 14          # comment lines in a row
DOCSTRING_MAX = 23      # lines
HEAD_MAX = 79           # first docstring line

error = []
def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

source = io.open(SCRIPT, encoding="utf-8").read()
lines = source.splitlines()
tree = ast.parse(source)

# ------------------------------------------------------------ Get the texts
def docstring_nodes():
    for k in ast.walk(tree):
        if isinstance(k, (ast.Module, ast.ClassDef, ast.FunctionDef,
                          ast.AsyncFunctionDef)):
            d = ast.get_docstring(k)
            if d:
                node = k.body[0].value
                yield (getattr(k, "name", "<module>"), node.lineno, d,
                       node.end_lineno)

comments = []
with open(SCRIPT, "rb") as f:
    for tok in tokenize.tokenize(f.readline):
        if tok.type == tokenize.COMMENT:
            comments.append((tok.start[0], tok.string.lstrip("# ").strip()))

docs = list(docstring_nodes())
print("%d comment lines, %d docstrings" % (len(comments), len(docs)))

# ---------------------------------------------------------------- Language
# German words that do not exist in English and are common enough to serve
# as proof. This list is the evidence, so it stays German. Umlauts alone
# will not do: message names and file names carry them for good reason.
GERMAN = re.compile(
    r"(?i)(?<![a-z])(der|die|das|dem|den|des|ein|eine|einen|einem|eines|"
    r"und|oder|nicht|noch|schon|dann|sonst|wenn|weil|damit|dass|aber|"
    r"wird|werden|wurde|steht|liegt|gibt|kommt|geht|macht|heisst|heißt|"
    r"sich|sie|ihm|ihr|man|kein|keine|nur|auch|sehr|hier|dort|jetzt|"
    r"immer|nie|alle|jede|jeder|etwas|nichts|mehr|weniger|schnitt|"
    r"kamera|sprecher|datei|ordner|spur|zeile|fenster)(?![a-z])")

# A quotation mark that only closes on the next comment line still opens a
# quote -- the check runs line by line.
QUOTE = re.compile(r'"[^"]*"|"[^"]*$|„[^“]*“|„[^“]*$'
                   r'|`[^`]*`')

def without_quotes(text):
    """What stands in quotes is quoted and may stay German."""
    return QUOTE.sub(" ", text)

def german_spots():
    out = []
    for line, text in comments:
        if GERMAN.search(without_quotes(text)):
            out.append(("Comment", line, text[:60]))
    for name, line, text, _e in docs:
        if GERMAN.search(without_quotes(text)):
            out.append(("Docstring", line, name))
    return out

german = german_spots()
if not os.path.exists(STATE):
    # No baseline means every counter is seeded from what is there now, so
    # the ratchet cannot fail on this run. Say so -- a lost state file must
    # not look like a clean bill of health.
    print("  NOTE: %s is missing. The counters below are being set from\n"
          "        the source as it stands; nothing is being held to\n"
          "        account this run." % os.path.basename(STATE))

old = {}
if os.path.exists(STATE):
    old = json.load(open(STATE))

def remember_state(key, value):
    """Pull along this one value only -- the others stay put."""
    d = json.load(open(STATE)) if os.path.exists(STATE) else {}
    d[key] = value
    if state_is_ours():
        json.dump(d, open(STATE, "w"))
limit = old.get("german", len(german))
check("German passages: %d (ratchet %d)" % (len(german), limit),
        len(german) <= limit,
        "" if len(german) <= limit else "there are more now")
if len(german) < limit or "german" not in old:
    remember_state("german", len(german))
    if len(german) < limit:
        print("      ratchet tightened: %d -> %d"
              % (limit, len(german)))

# --------------------------------------------------------------- Narrating
NARRATING = [
    (r"(?i)\bvorher stand\b", "reports what stood there before"),
    (r"(?i)\bbis (Fassung|version)\b", "reports version history"),
    (r"(?i)\b(früher|frueher)\b", "reports the past"),
    (r"(?i)\bused to (be|read|call|do)\b", "reports former behaviour"),
    (r"(?i)\bpreviously (stood|held|read|was|did|had)\b",
     "reports former behaviour"),
    (r"(?i)\bin the past\b", "reports former behaviour"),
    (r"(?i)\bhistorically\b", "reports former behaviour"),
    (r"(?i)\bthis (used|was) a bug\b", "reports a fixed bug"),
    (r"(?i)\b(unfortunately|sadly|luckily|funnily)\b",
     "judges instead of explaining"),
    (r"(?i)\b(I|we|my|our) (had|have|found|noticed|learned|spent)\b",
     "tells a story in the first person"),
    (r"(?i)\bTODO\b|\bFIXME\b|\bXXX\b", "a note left undone"),
]
hits = []
for pattern, reason in NARRATING:
    r = re.compile(pattern)
    for line, text in comments:
        if r.search(text):
            hits.append((line, reason, text[:60]))
    for name, line, text, _e in docs:
        for t in text.splitlines():
            if r.search(t):
                hits.append((line, reason,
                             "%s: %s" % (name, t.strip()[:50])))
# This too is a ratchet while the changeover runs; in the end it has to
# stand at zero.
limit_n = old.get("narrating", len(hits))
check("narrating: %d spots (ratchet %d)" % (len(hits), limit_n),
        len(hits) <= limit_n,
        "" if len(hits) <= limit_n else "there are more now")
if len(hits) < limit_n or "narrating" not in old:
    remember_state("narrating", len(hits))
for line, reason, text in hits[:10]:
    print("      line %-6d %-32s %s" % (line, reason, text))

# ------------------------------------------------------------------ Length
# Text only: code lines that run long are a different building site.
text_lines = set(line for line, _t in comments)
for _n, first, _t, last in docs:
    text_lines.update(range(first, last + 1))
too_long = [(i + 1, len(line)) for i, line in enumerate(lines)
            if len(line) > LINE_MAX and (i + 1) in text_lines]
limit_l = old.get("long_lines", len(too_long))
check("text lines over %d characters: %d (ratchet %d)"
        % (LINE_MAX, len(too_long), limit_l), len(too_long) <= limit_l,
        "" if len(too_long) <= limit_l else "there are more now")
if len(too_long) < limit_l or "long_lines" not in old:
    remember_state("long_lines", len(too_long))
for line, length in too_long[:5]:
    print("      line %d: %d characters -- %s"
          % (line, length, lines[line-1].strip()[:50]))

blocks, run, from_s = [], 0, 0
for i, line in enumerate(lines, 1):
    if line.strip().startswith("#"):
        if not run: from_s = i
        run += 1
    else:
        if run > BLOCK_MAX: blocks.append((from_s, run))
        run = 0
check("no comment block over %d lines" % BLOCK_MAX, not blocks,
        str(blocks[:4]))

long_docs = [(n, len(t.splitlines())) for n, _z, t, _e in docs
             if len(t.splitlines()) > DOCSTRING_MAX]
check("no docstring over %d lines" % DOCSTRING_MAX, not long_docs,
        str(long_docs[:4]))

# ----------------------------------------------------------------- Heading
bad_head = []
for name, line, text, _e in docs:
    head = text.splitlines()[0].strip()
    if len(head) > HEAD_MAX:
        bad_head.append((name, "first line too long"))
    elif not head.endswith((".", "?", ":")):
        bad_head.append((name, "first line without a mark"))
    elif len(text.splitlines()) > 1 and text.splitlines()[1].strip():
        bad_head.append((name, "no blank line after the first"))
# While the changeover runs, a ratchet here as well.
limit_h = old.get("heading", len(bad_head))
check("docstring headings: %d defects (ratchet %d)"
        % (len(bad_head), limit_h), len(bad_head) <= limit_h)
if len(bad_head) < limit_h or "heading" not in old:
    remember_state("heading", len(bad_head))
for n, w in bad_head[:8]:
    print("      %-30s %s" % (n, w))

# ------------------------------------------------------------ Lazy plural
# "1 file(s)" is neither singular nor plural, and German cannot glue a
# suffix on in brackets either. TN(count, one, many) exists for this: both
# wordings are separate texts and both get translated. A ratchet, so the
# ones still there cannot breed.
lazy = []
for node in ast.walk(ast.parse(source)):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        if re.search(r"[A-Za-z\u00c4\u00d6\u00dc\u00e4\u00f6\u00fc\u00df]{3,}"
                     r"\((?:s|n|e|en)\)", node.value):
            lazy.append((node.lineno, node.value.strip()[:58]))
limit_p = old.get("lazy_plural", len(lazy))
check("lazy plurals: %d (ratchet %d)" % (len(lazy), limit_p),
        len(lazy) <= limit_p)
if len(lazy) < limit_p or "lazy_plural" not in old:
    remember_state("lazy_plural", len(lazy))
    if len(lazy) < limit_p:
        print("      ratchet tightened: %d -> %d" % (limit_p, len(lazy)))
for line, text in lazy[:8]:
    print("      line %-6d %s" % (line, text))

# ------------------------------------------------- How big a function got
# coding_guidelines.md sets 300 lines. Counted on 23.8.2026: eight
# functions are over it and the largest is gui() at 5939 -- twenty times
# the rule this project wrote for itself. Freezing that number would be
# a decision that it is acceptable, and it is not.
#
# So three counters, and the second one is the point. It does not freeze
# anything: it prints the largest function in every single run, so the
# number cannot quietly leave anybody's head, and the moment somebody
# takes a hundred lines out of gui() the ratchet holds the gain.
#
# Splitting gui() is not what this asks for. That is hundreds of
# closures over shared variables and a week of new defects for no new
# ability -- its own decision, for its own day. This is the cheap step
# that stops the bleeding.
tree = ast.parse(source)
sizes = []
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        end = getattr(node, "end_lineno", None)
        if end:
            sizes.append((end - node.lineno + 1, node.name, node.lineno))
sizes.sort(reverse=True)
big = [s for s in sizes if s[0] > 300]

limit_b = old.get("over_300", len(big))
check("functions over 300 lines: %d (ratchet %d)" % (len(big), limit_b),
        len(big) <= limit_b)
if len(big) < limit_b or "over_300" not in old:
    remember_state("over_300", len(big))
    if len(big) < limit_b:
        print("      ratchet tightened: %d -> %d" % (limit_b, len(big)))
for size, name, line in big[:8]:
    print("      %-28s %5d lines, from line %d" % (name, size, line))

largest = sizes[0][0] if sizes else 0
limit_l = old.get("largest_function", largest)
check("largest function: %d lines (ratchet %d)" % (largest, limit_l),
        largest <= limit_l,
        sizes[0][1] if sizes else "")
if largest < limit_l or "largest_function" not in old:
    remember_state("largest_function", largest)
    if largest < limit_l:
        print("      ratchet tightened: %d -> %d" % (limit_l, largest))

# ------------------------------------------------- Exceptions swallowed
# An except that does nothing hides the reason something did not work.
# Counted the same way and held the same way: it may fall, never rise.
silent = []
for node in ast.walk(tree):
    if not isinstance(node, ast.ExceptHandler):
        continue
    body = [b for b in node.body
            if not (isinstance(b, ast.Expr)
                    and isinstance(b.value, ast.Constant)
                    and isinstance(b.value.value, str))]
    if len(body) == 1 and isinstance(body[0], ast.Pass):
        silent.append(node.lineno)
limit_s = old.get("silent_except", len(silent))
check("except branches that only pass: %d (ratchet %d)"
      % (len(silent), limit_s), len(silent) <= limit_s)
if len(silent) < limit_s or "silent_except" not in old:
    remember_state("silent_except", len(silent))
    if len(silent) < limit_s:
        print("      ratchet tightened: %d -> %d" % (limit_s, len(silent)))

print("\n%s" % ("All good." if not error
                else "FAIL: %s" % ", ".join(error)))
sys.exit(1 if error else 0)
