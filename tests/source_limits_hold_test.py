# -*- coding: utf-8 -*-
"""Style check for comments and docstrings.

Two things must not come back as more gets written: German comments (the
interface stays German, the code does not) and narrating comments that
report what stood there before. Both are counted as ratchets, so the
numbers may fall and never rise.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import ast, io, re, sys, time, tokenize
sys.path.insert(0, HERE)
import ratchet

began = time.time()

STATE = os.path.join(HERE, "state", "style_state.json")
state = ratchet.Ratchet(STATE)
LINE_MAX = 79
BLOCK_MAX = 14          # comment lines in a row -- the hard limit
DOCSTRING_MAX = 23      # lines -- the hard limit
# What the guidelines ask for, shorter than what the file holds today.
# Counted rather than enforced: a comment past these is either saying
# what the code says, telling a story, or two comments written as one.
BLOCK_WANTED = 4
DOCSTRING_WANTED = 8
HEAD_MAX = 79           # first docstring line

done = 0
error = []
def check(name, ok, extra=""):
    global done
    done += 1
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
# German words that do not exist in English. This list is the evidence,
# so it stays German. Umlauts alone will not do: message names and file
# names carry them for good reason.
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
state.announce()

limit = state.number("german", len(german))
check("German passages: %d (ratchet %d)" % (len(german), limit),
        len(german) <= limit,
        "" if len(german) <= limit else "there are more now")
state.note(limit, len(german))

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
# A ratchet while the changeover runs; in the end this stands at zero.
limit_n = state.number("narrating", len(hits))
check("narrating: %d spots (ratchet %d)" % (len(hits), limit_n),
        len(hits) <= limit_n,
        "" if len(hits) <= limit_n else "there are more now")
for line, reason, text in hits[:10]:
    print("      line %-6d %-32s %s" % (line, reason, text))

# ------------------------------------------------------------------ Length
# Text only: code lines that run long are a different building site.
text_lines = set(line for line, _t in comments)
for _n, first, _t, last in docs:
    text_lines.update(range(first, last + 1))
too_long = [(i + 1, len(line)) for i, line in enumerate(lines)
            if len(line) > LINE_MAX and (i + 1) in text_lines]
limit_l = state.number("long_lines", len(too_long))
check("text lines over %d characters: %d (ratchet %d)"
        % (LINE_MAX, len(too_long), limit_l), len(too_long) <= limit_l,
        "" if len(too_long) <= limit_l else "there are more now")
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

runs, run = [], 0
for line in lines:
    if line.strip().startswith("#"):
        run += 1
    else:
        if run: runs.append(run)
        run = 0
if run: runs.append(run)
over_b = [r for r in runs if r > BLOCK_WANTED]
limit_b = state.number("long_blocks", len(over_b))
check("comment blocks over %d lines: %d (ratchet %d)"
        % (BLOCK_WANTED, len(over_b), limit_b), len(over_b) <= limit_b,
        "" if len(over_b) <= limit_b else "there are more now")

long_docs = [(n, len(t.splitlines())) for n, _z, t, _e in docs
             if len(t.splitlines()) > DOCSTRING_MAX]
check("no docstring over %d lines" % DOCSTRING_MAX, not long_docs,
        str(long_docs[:4]))

over_d = [n for n, _z, t, _e in docs
          if len(t.splitlines()) > DOCSTRING_WANTED]
limit_d = state.number("long_docstrings", len(over_d))
check("docstrings over %d lines: %d (ratchet %d)"
        % (DOCSTRING_WANTED, len(over_d), limit_d), len(over_d) <= limit_d,
        "" if len(over_d) <= limit_d else "there are more now")

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
limit_h = state.number("heading", len(bad_head))
check("docstring headings: %d defects (ratchet %d)"
        % (len(bad_head), limit_h), len(bad_head) <= limit_h)
for n, w in bad_head[:8]:
    print("      %-30s %s" % (n, w))

# ------------------------------------------------------------ Lazy plural
# "1 file(s)" is neither singular nor plural, and German cannot glue a
# suffix on in brackets either. TN(count, one, many) exists for this:
# both wordings are separate texts and both get translated.
lazy = []
for node in ast.walk(ast.parse(source)):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        if re.search(r"[A-Za-z\u00c4\u00d6\u00dc\u00e4\u00f6\u00fc\u00df]{3,}"
                     r"\((?:s|n|e|en)\)", node.value):
            lazy.append((node.lineno, node.value.strip()[:58]))
limit_p = state.number("lazy_plural", len(lazy))
check("lazy plurals: %d (ratchet %d)" % (len(lazy), limit_p),
        len(lazy) <= limit_p)
state.note(limit_p, len(lazy))
for line, text in lazy[:8]:
    print("      line %-6d %s" % (line, text))

# ------------------------------------------------- How big a function got
# coding_guidelines.md sets 300 lines and several functions are far over
# it; freezing that number would say it is acceptable. The state holds
# one entry per oversized function, by name: one dropping under the
# limit does not buy room for another to climb over it.
tree = ast.parse(source)
seen = ratchet.owners(tree)
sizes = []
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        end = getattr(node, "end_lineno", None)
        if end:
            sizes.append((end - node.lineno + 1,
                          ratchet.qualified(seen, node), node.lineno))
sizes.sort(reverse=True)
big = [s for s in sizes if s[0] > 300]

held = state.places("over_300",
                    dict((name, (1, line)) for _size, name, line in big))
check("functions over 300 lines: %d (ratchet %d)" % (len(big), held.limit),
        held.ok)
held.report()
if held.tightened:
    print("      ratchet tightened: %d -> %d" % (held.limit, len(big)))
for size, name, line in big[:8]:
    print("      %-28s %5d lines, from line %d" % (name[:28], size, line))

largest = sizes[0][0] if sizes else 0
# Only the biggest is held, as a bare number that has nothing to swap
# against: holding every function to its own size goes red whenever an
# oversized one grows, which finds nothing new. A smaller one ballooning
# while the biggest shrinks is what the entry list above sees.
limit_l = state.number("largest_function", largest)
check("largest function: %d lines (ratchet %d)" % (largest, limit_l),
        largest <= limit_l,
        sizes[0][1] if sizes else "")
state.note(limit_l, largest)

# ------------------------------------------------- Exceptions swallowed
# An except that does nothing hides the reason something did not work.
# Held on the function each one sits in, so moving one is not a free
# trade. The exception type is deliberately not part of the fingerprint:
# narrowing `except Exception` improves the handler and must not go red.
silent = []
for node in ast.walk(tree):
    if not isinstance(node, ast.ExceptHandler):
        continue
    body = [b for b in node.body
            if not (isinstance(b, ast.Expr)
                    and isinstance(b.value, ast.Constant)
                    and isinstance(b.value.value, str))]
    if len(body) == 1 and isinstance(body[0], ast.Pass):
        silent.append((seen.get(id(node), "<module>"), node.lineno))
held = state.places("silent_except", ratchet.tally(silent))
check("except branches that only pass: %d (ratchet %d)"
      % (len(silent), held.limit), held.ok)
held.report()
if held.tightened:
    print("      ratchet tightened: %d -> %d" % (held.limit, len(silent)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("\n%s" % ("All good." if not error
                else "FAIL: %s" % ", ".join(error)))
sys.exit(1 if error else 0)
