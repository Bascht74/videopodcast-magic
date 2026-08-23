# -*- coding: utf-8 -*-
"""Hunt down the last German word, and check the catalogue itself.

language_test.py already reads every name, string and comment above the
catalogue through a German dictionary. This one covers what that cannot
reach and what a dictionary would never notice:

* umlauts and eszett where only English belongs -- the cheapest signal
  there is, and it needs no dictionary
* German abbreviations, which no dictionary holds as words
* the manual, both halves: German words on the English side
* the catalogue as data: entries nobody can reach, placeholders that do
  not match, line breaks that do not match, values still in English

The placeholder check is the one that catches crashes: a German text
missing a %s raises at run time, and only for people running in German.
"""
import ast, io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    ROOT, "videopodcast-magic.py")
import importlib.util
sys.path.insert(0, os.path.dirname(
    os.path.abspath(__file__)))
from fixture_root import fixture
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
source = io.open(SCRIPT, encoding="utf-8").read()
bad = []


def check(what, ok, detail=""):
    print("  %-56s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


#-------------------------------------------------------------- the catalogue
tree = ast.parse(source)
catalogue_node = None
for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Subscript) \
                    and isinstance(target.value, ast.Name) \
                    and target.value.id == "CATALOGUE":
                catalogue_node = node
print("1. The catalogue as data")
check("the catalogue is one assignment at the end",
      catalogue_node is not None)
inside = {id(n) for n in ast.walk(catalogue_node)} if catalogue_node else set()
elsewhere = {n.value for n in ast.walk(tree) if id(n) not in inside
             and isinstance(n, ast.Constant) and isinstance(n.value, str)}
catalogue = vpm.CATALOGUE["de"]
unreachable = [k for k in catalogue if k not in elsewhere]
check("no entry nobody can reach", not unreachable,
      "%d: %s" % (len(unreachable), [repr(x)[:40] for x in unreachable[:3]]))

wanted = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
            and node.func.id in ("T", "TN"):
        for a in node.args:
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                wanted.add(a.value)
absent = sorted(w for w in wanted if w not in catalogue)
check("no text without a translation", not absent,
      "%d: %s" % (len(absent), [repr(x)[:40] for x in absent[:3]]))

FORMAT = re.compile(r"%(?:\((\w+)\))?[-+ #0]*[\d*]*(?:\.\d+)?[hlL]?"
                    r"([diouxXeEfFgGcrsa%])")


def placeholders(text):
    return sorted(m.group(0) for m in FORMAT.finditer(text)
                  if m.group(2) != "%")


off = [(k, placeholders(k), placeholders(v)) for k, v in catalogue.items()
       if placeholders(k) != placeholders(v)]
check("every translation carries the same placeholders", not off,
      str(off[:2]))
breaks = [k for k, v in catalogue.items() if k.count("\n") != v.count("\n")]
check("and the same number of line breaks", not breaks,
      str([repr(x)[:40] for x in breaks[:3]]))
indent = [k for k, v in catalogue.items()
          if len(k) - len(k.lstrip()) != len(v) - len(v.lstrip())]
check("and the same indent", not indent,
      str([repr(x)[:40] for x in indent[:3]]))

# A handful of words are the same in both languages. Anything else that
# comes back unchanged was forgotten rather than translated.
SAME_IN_BOTH = {
    '  Preset:  %s', 'Preset', 'Preset:', 'Start', '  Timecode:        %s',
    '\n    %s  --  %s, %s',
}
untranslated = [k for k, v in catalogue.items()
                if k == v and k not in SAME_IN_BOTH]
check("nothing was left in English by accident", not untranslated,
      str([repr(x)[:40] for x in untranslated[:3]]))

#------------------------------------------------------ umlauts where none belong
print("\n2. Umlauts and eszett only where German lives")
GERMAN_LETTERS = re.compile(r"[äöüÄÖÜß]")
border = source.find('CATALOGUE["de"] = {')
head = source[:border]
hits = []
for i, line in enumerate(head.splitlines(), 1):
    if GERMAN_LETTERS.search(line):
        hits.append((i, line.strip()[:60]))
check("no umlaut in the program above the catalogue", not hits,
      str(hits[:3]))
# Inside the catalogue: only the values may carry them, never the keys.
key_hits = [k for k in catalogue if GERMAN_LETTERS.search(k)]
check("no umlaut in an English catalogue key", not key_hits,
      str([repr(x)[:40] for x in key_hits[:3]]))

#---------------------------------------------------------- abbreviations
print("\n3. German abbreviations")
SHORTHAND = (r"\b(?:z\s?\.?\s?B|bzw|ggf|u\s?\.?\s?a|d\s?\.?\s?h|usw|evtl"
             r"|inkl|bspw|vgl|sog|bzgl|i\s?\.?\s?d\s?\.?\s?R|z\s?\.?\s?T"
             r"|o\s?\.?\s?ä|Abb|Nr|ca)\.")
SHORT = re.compile(SHORTHAND)
found = []
for i, line in enumerate(head.splitlines(), 1):
    m = SHORT.search(line)
    if m:
        found.append((i, m.group(0)))
check("none in the program", not found, str(found[:3]))
in_keys = [k for k in catalogue if SHORT.search(k)]
check("none in an English catalogue key", not in_keys,
      str([repr(x)[:40] for x in in_keys[:3]]))

#------------------------------------------------------------- the manual
print("\n4. The English documents carry no German")
# The manual used to be one file with an English half and a German half.
# It is now one file per chapter and per language: README.md beside
# docs/*.md in English, README.de.md beside docs/*.de.md in German. Every
# English one is scanned; a chapter added without its translation is
# caught by the pairing check further down.
BOOKS = [os.path.join(ROOT, "README.md")]
DOCS = os.path.join(ROOT, "docs")
# What is not a chapter is not in docs/ any more: the three documents
# for whoever changes the program stand beside it, in development/, and
# they are English only.
DEV = os.path.join(ROOT, "development")
if os.path.isdir(DOCS):
    BOOKS += [os.path.join(DOCS, n) for n in sorted(os.listdir(DOCS))
              if n.endswith(".md") and not n.endswith(".de.md")]
# Two of the three are scanned for German words like a chapter. The
# coding guidelines are left out here: they talk about the German
# catalogue, and they are checked for umlauts further down instead.
BOOKS += [os.path.join(DEV, "internals.md"),
          os.path.join(DEV, "measurements.md")]
BOOKS = [b for b in BOOKS if os.path.exists(b)]
check("the English documents are there", len(BOOKS) > 5, str(len(BOOKS)))

# Every English chapter has a German one beside it, and the other way
# round. A chapter translated on one side only is how a manual drifts.
if os.path.isdir(DOCS):
    # Only chapters are in docs/ itself, so everything found here has to
    # have a twin. The three documents that stand without one are in
    # development/ and are not looked at by this check; they are still
    # scanned for German words above.
    english = set(n[:-3] for n in os.listdir(DOCS)
                  if n.endswith(".md") and not n.endswith(".de.md"))
    german = set(n[:-6] for n in os.listdir(DOCS) if n.endswith(".de.md"))
    check("every chapter has both languages", english == german,
          str(sorted(english ^ german)))

# Every chapter separately, so a hit names the file it is in.
def english_prose(path):
    """The English text of one document, without code, links or the head."""
    text = io.open(path, encoding="utf-8").read()
    # The pointer to the German file is German on purpose -- a German
    # reader has to be able to find it -- so the first lines go.
    first = text.find("\n## ")
    text = text[first:] if first > 0 else text
    # Code, switches and file names are quoted; those may hold anything.
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`[^`]*`", "", text)
    # A link carries the file name of the German chapter behind it.
    return re.sub(r"\]\([^)]*\)", "]", text)


hits = []
for book in BOOKS:
    for i, line in enumerate(english_prose(book).splitlines(), 1):
        if SHORT.search(line):
            hits.append("%s:%d" % (os.path.basename(book), i))
check("no German abbreviation on the English side", not hits, str(hits[:3]))


def words_of(text):
    out = []
    for piece in re.split(r"[^0-9A-Za-zÀ-ɏ]+", text):
        for part in re.findall(r"[A-Z]?[a-zß-ÿ]+"
                                r"|[A-Z]+(?![a-z])", piece):
            if len(part) > 3:
                out.append(part.lower())
    return out


try:
    from spellchecker import SpellChecker
    de, en = SpellChecker(language="de"), SpellChecker(language="en")
except ImportError:
    de = en = None
if de is None:
    print("  SKIPPED: pyspellchecker is not installed")
else:
    # Words the English manual uses that only German knows. Names of
    # things stay out -- they are the same in both languages.
    KEEP = set("""
    auphonic ffmpeg ffprobe resolve blackmagic quicktime davinci
    multicam smartswitch whisper podcast intro outro codec codecs
    lang html json wave riff bext lufs dbfs dbtp ebur soxr numpy
    lgpl gpl bsd
    pyside python argparse mkdtemp tmpdir uuid ppm hdr sdr hlg
    interview interviews kandidat moderator moderatorin totale
    also normal standard programme man marker stand rate multi
    """.split())
    strange = {}
    for book in BOOKS:
        for w in words_of(english_prose(book)):
            if w in KEEP or w in en:
                continue
            if w in de:
                strange.setdefault(w, os.path.basename(book))
    check("no German word on the English side", not strange,
          str(sorted(strange.items())[:4]))

#-------------------------------------------------------------- the tests
print("\n5. The other documents")
# coding_guidelines.md and the test README are English. The notes under
# docs/notes/ are German on purpose and are not delivered.
# BOOKS from above are the English manual: README.md and the chapters
# under docs/, overview.md among them. They are scanned for German words
# there and for umlauts here -- an umlaut is the cheapest sign that a
# translation slipped in.
ENGLISH_ONLY = BOOKS + [os.path.join(DEV, "coding_guidelines.md"),
                        os.path.join(HERE, "README.md")]
for path in ENGLISH_ONLY:
    # The path from the project root, not just the file name: three of
    # these are called README.md and the report has to say which.
    name = os.path.relpath(path, ROOT)
    if not os.path.exists(path):
        print("  SKIPPED: %s is not there" % name)
        continue
    body = re.sub(r"`[^`]*`", "", io.open(path, encoding="utf-8").read())
    marks = [i for i, line in enumerate(body.splitlines(), 1)
             if GERMAN_LETTERS.search(line) or SHORT.search(line)]
    check("%s: no umlaut and no abbreviation" % name, not marks,
          str(marks[:4]))

print("\n6. The tests are English too")
# The detectors themselves have to carry the words they look for -- this
# file and the two that read the program for German are the exception,
# and they are the only ones.
DETECTORS = {"german_hunt_test.py", "style_test.py", "language_test.py"}
mine = sorted(f for f in os.listdir(HERE)
              if f.endswith(".py") and f not in DETECTORS)
spotted = []
for f in mine:
    body = io.open(os.path.join(HERE, f), encoding="utf-8").read()
    for i, line in enumerate(body.splitlines(), 1):
        if GERMAN_LETTERS.search(line) or SHORT.search(line):
            spotted.append("%s:%d" % (f, i))
check("no umlaut and no abbreviation in a test", not spotted,
      str(spotted[:4]))

print("\n7. The program run in German, read back")
# The strongest check of all, because it needs no list: run the thing and
# look at what comes out. A line that never went through T() stays
# English, and English function words in a German run are the giveaway.
import subprocess
media = os.environ.get("VPM_MEDIA") or fixture("interview")
job = sorted(f for f in (os.listdir(media) if os.path.isdir(media) else [])
             if f.lower().endswith((".wav", ".mov")))
if len(job) < 2:
    print("  SKIPPED: no material under %s" % media)
else:
    # Two runs, so both paths are read: the simple one and multitrack.
    out = ""
    for extra in ([], ["--multitrack", "--without-auphonic"]):
        out += subprocess.run(
            [sys.executable, SCRIPT] + [os.path.join(media, f) for f in job]
            + ["--lang", "de", "--dry-run", "--no-preflight",
               "--no-metrics"] + extra,
            capture_output=True, text=True, timeout=900,
            env=dict(os.environ, LANG="C", LC_ALL="C")).stdout
    check("the German run says something at all", len(out) > 2000,
          "%d characters" % len(out))
    # Words that are English and are not also German, not a file name, and
    # not a technical term the German text uses as it stands.
    ENGLISH = re.compile(r"(?<![A-Za-z])(the|and|with|from|into|"
                         r"which|would|there|their|because|"
                         r"before|after|between|through|without)"
                         r"(?![A-Za-z])")
    left = []
    for line in out.splitlines():
        # Paths and file names carry English words and are not text.
        bare = re.sub(r"[^\s]*[/\\][^\s]*", "", line)
        m = ENGLISH.search(bare)
        if m:
            left.append((m.group(0), bare.strip()[:60]))
    check("and no English sentence is left in it", not left, str(left[:3]))

print()
if bad:
    print("FAIL: %d of the checks" % len(bad))
    sys.exit(1)
print("All good.")
