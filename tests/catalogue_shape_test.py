# -*- coding: utf-8 -*-
"""No sentence may be glued together out of translated pieces.

On 23.8.2026 the settings window said, in German, "Der Schluessel geht
nie in eine Datei". Every piece of it was translated correctly on its
own. The sentence was wrong all the same, because German settles the
article and the case at the front of a phrase, and a piece that gets
dropped into a slot cannot know what governs it. "a file" is "eine
Datei" standing alone and "einer Datei" after a preposition that takes
the dative, and the piece has no way of telling which one it is in.

The fix was to put the whole sentence into the catalogue, with the one
thing that really varies left as a placeholder at the end. That entry
is still there and reads

    'Both are asked once and then stay. The key goes into the %s,
     never into a file.'

No run of the program can find this class of defect: the pieces exist
and the placeholders match, so nothing raises and nothing looks wrong
from the inside. Only a reader of the finished screen sees it. What a
test can see is the shape that produces it, and that is what this file
looks at, in three grades of severity:

1. Two translated pieces joined with "+" into one sentence. This is
   the shape of the original defect and it is held at zero.
2. A translated piece that carries a German article or preposition,
   substituted into a translated sentence with "%". Same risk, but
   twenty of these stand in the program today and all of them read
   correctly, several because the gender happens to be neuter rather
   than because anybody chose it -- "das voreingestellte Geraet" is
   the same in the nominative and the accusative, a masculine one
   would not have been. A ratchet, so the count may fall and never
   rise.
3. A translated text that is nothing but a function word. Five of
   these exist, all of them list joiners or setting values; they are
   named below with the reason each one is allowed.
"""
import ast, io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    ROOT, "videopodcast-magic.py")
sys.path.insert(0, HERE)
import ratchet

STATE = os.path.join(HERE, "state", "catalogue_shape_state.json")
state = ratchet.Ratchet(STATE)

bad = []


def check(what, ok, detail=""):
    print("  %-56s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


source = io.open(SCRIPT, encoding="utf-8").read()
tree = ast.parse(source)

# The German side is read out of the syntax tree instead of importing the
# program: the catalogue is a plain dictionary of literals, so it can be
# evaluated without running anything, and nothing here can open a window.
catalogue = {}
for node in tree.body:
    if not isinstance(node, ast.Assign):
        continue
    for target in node.targets:
        if isinstance(target, ast.Subscript) \
                and isinstance(target.value, ast.Name) \
                and target.value.id == "CATALOGUE":
            try:
                catalogue = ast.literal_eval(node.value)
            except ValueError:
                catalogue = {}
check("the German catalogue could be read", len(catalogue) > 100,
      "%d entries" % len(catalogue))


def is_call(node):
    """Is this a T() or TN() call?"""
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in ("T", "TN"))


def texts_of(node):
    """The English texts a T() or TN() call names."""
    return [a.value for a in node.args
            if isinstance(a, ast.Constant) and isinstance(a.value, str)]


def translated(node):
    """The texts an expression puts on screen, or None if it is not one.

    A bare T() call counts, and so does T('... %s ...') % something: the
    text still comes from the catalogue, the arguments only fill it in.
    """
    if is_call(node):
        return texts_of(node)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod) \
            and is_call(node.left):
        return texts_of(node.left)
    return None


def flatten(node):
    """A chain of + as a flat list of its operands."""
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return flatten(node.left) + flatten(node.right)
    return [node]


# --------------------------------------------- 1. glued with a plus sign
print("\n1. No sentence built out of translated pieces with +")
ENDS_SENTENCE = (".", "?", "!", ":", "…")


def is_tail(text):
    """Does this text continue a sentence somebody else started?"""
    body = text.strip()
    return bool(body) and body[0].islower()


def is_open(text):
    """Does this text stop in the middle of a sentence?"""
    body = text.strip()
    return bool(body) and not body.endswith(ENDS_SENTENCE)


# Only the outermost chain of each nest is looked at, or a chain of three
# would be reported twice.
inner = set()
chains = []
for node in ast.walk(tree):
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        if id(node) in inner:
            continue
        for sub in ast.walk(node):
            if sub is not node and isinstance(sub, ast.BinOp) \
                    and isinstance(sub.op, ast.Add):
                inner.add(id(sub))
        chains.append(node)

glued = []
for chain in chains:
    parts = flatten(chain)
    spots = [i for i, p in enumerate(parts) if translated(p) is not None]
    for first, second in zip(spots, spots[1:]):
        # Whatever stands between the two pieces. A line break means they
        # are two lines and not one sentence, and so does a full stop:
        # German grammar does not reach across either of them.
        glue = "".join(p.value for p in parts[first + 1:second]
                       if isinstance(p, ast.Constant)
                       and isinstance(p.value, str))
        if "\n" in glue or glue.strip().endswith(ENDS_SENTENCE):
            continue
        left = translated(parts[first])
        right = translated(parts[second])
        why = ""
        if any(is_tail(t) for t in right):
            why = "the second piece starts in lower case"
        elif any(is_open(t) for t in left):
            why = "the first piece stops mid-sentence"
        if why:
            glued.append((chain.lineno, why,
                          (left[0] if left else "")[:34],
                          (right[0] if right else "")[:34]))

check("no translated piece glued onto another", not glued,
      "%d" % len(glued))
for line, why, left, right in glued[:8]:
    print("      line %-6d %s" % (line, why))
    print("          %r + ... + %r" % (left, right))

# ------------------------------- 2. dropped into a slot with a percent sign
print("\n2. No translated piece carrying an article put into a sentence")
# The words German decides a case with. A translated piece that begins
# with one of these has settled its own case before it knows the slot it
# is going into, which is exactly how the sentence of 23.8.2026 came out
# wrong. Three of them are spelled with escapes so this file stays free
# of German letters -- german_hunt_test.py checks the tests for that.
GOVERNING = [
    "der", "die", "das", "den", "dem", "des",
    "ein", "eine", "einen", "einem", "eines", "einer",
    "im", "ins", "in", "an", "am", "auf", "aufs",
    "zu", "zur", "zum", "vom", "von", "bei", "beim",
    "mit", "nach", "aus", "durch", "ohne", "gegen", "um", "seit",
    "f\u00fcr", "\u00fcber", "unter", "w\u00e4hrend",
    "und", "oder", "aber", "denn", "sondern",
]
ARTICLE = re.compile(r"^\W*(?:%s)\b" % "|".join(GOVERNING), re.IGNORECASE)

inserted = []
for node in ast.walk(tree):
    if not (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod)):
        continue
    if not is_call(node.left):
        continue
    host = texts_of(node.left)
    for sub in ast.walk(node.right):
        if not is_call(sub):
            continue
        for text in texts_of(sub):
            german = catalogue.get(text, text)
            if ARTICLE.match(german):
                inserted.append((node.lineno, text,
                                 (host[0] if host else "")[:44]))

state.announce()
# The fingerprint is the piece and the sentence it goes into, both in
# English, and no line number: these two texts are what the find is, and
# they stay themselves wherever in the file they end up standing.
held = state.places("article_fragments", ratchet.tally(
    [("%r into %r" % (text[:40], host), line)
     for line, text, host in inserted]))
check("translated pieces with an article: %d (ratchet %d)"
      % (len(inserted), held.limit), held.ok,
      "one of them is not in the state")
held.report()
if held.tightened:
    print("      ratchet tightened: %d -> %d"
          % (held.limit, len(inserted)))
for line, text, host in sorted(inserted)[:6]:
    print("      line %-6d %-26r into %r" % (line, text[:24], host))

# ------------------------------------------ 3. a text that is only a joiner
print("\n3. No translated text that is nothing but a function word")
FUNCTION_WORD = re.compile(
    r"^\W*(?:the|a|an|and|or|but|of|in|on|off|at|to|for|with|from|by"
    r"|into|onto|over|under|as|than|then)\W*$", re.IGNORECASE)
# Allowed, and why. Keyed by the text, so a new place that uses the same
# word for the same purpose is allowed too.
#
#   ' and '   joins the last two items of a list -- "A, B and C". It
#             stands between whole items, never inside one, so no case
#             of any item depends on it.
#   'on'      the value of a Resolve setting, printed at the end of a
#   'off'     sentence as the state a switch is in. A value, not a word
#             taken out of a sentence.
ALLOWED = {" and ", "on", "off"}

bare = set()
for node in ast.walk(tree):
    if not is_call(node):
        continue
    for text in texts_of(node):
        if FUNCTION_WORD.match(text) and text not in ALLOWED:
            bare.add((node.lineno, text))
check("no text that is only a function word", not bare, "%d" % len(bare))
for line, text in sorted(bare)[:8]:
    print("      line %-6d %r -> %r"
          % (line, text, catalogue.get(text, text)))

print()
if bad:
    print("FAIL: %d of the checks" % len(bad))
    sys.exit(1)
print("All good.")
