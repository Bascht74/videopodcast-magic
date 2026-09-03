# -*- coding: utf-8 -*-
"""No sentence may be glued together out of translated pieces.

German settles the article and the case at the front of a phrase, so a
piece dropped into a slot cannot know what governs it: every piece is
right and the sentence is wrong. No run finds this. Visible is only the
shape that produces it, in three grades: pieces joined with "+", a piece
carrying an article substituted with "%", and a bare function word.
"""
import ast, io, os, re, sys, time

began = time.time()

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    ROOT, "videopodcast_magic.py")
sys.path.insert(0, HERE)
import ratchet

STATE = os.path.join(HERE, "state", "catalogue_shape_state.json")
state = ratchet.Ratchet(STATE)

done = 0
bad = []


def check(what, ok, detail=""):
    global done
    done += 1
    print("  %-56s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


source = io.open(SCRIPT, encoding="utf-8").read()
tree = ast.parse(source)

# The German side is read out of the syntax tree instead of importing
# the program: a dictionary of literals evaluates without running
# anything, so nothing here can open a window.
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

    A bare T() counts, and so does T('... %s ...') % something: the
    text still comes from the catalogue.
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
        # German grammar reaches across neither a line break nor a full
        # stop, so what stands between the two pieces decides.
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
# The words German decides a case with. A piece beginning with one has
# settled its own case before it knows the slot it goes into. Three are
# spelled with escapes so this file stays free of German letters --
# text_no_german_left_test.py checks the tests for that.
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
# English and without a line number, so a find stays itself wherever in
# the file it ends up standing.
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
# Allowed, keyed by the text so the same word for the same purpose is
# allowed again. ' and ' stands between whole items of a list, never
# inside one, so no case depends on it; 'on' and 'off' are the values of
# a Resolve setting, not words taken out of a sentence.
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

print("\n%d checks in %.2f s" % (done, time.time() - began))
if bad:
    print("FAIL: %d of the checks" % len(bad))
    sys.exit(1)
print("All good.")
