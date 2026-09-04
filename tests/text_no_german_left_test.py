# -*- coding: utf-8 -*-
"""Hunt down the last German word, and check the catalogue itself.

text_only_texts_change reads the program through a German dictionary;
covers what that cannot: umlauts and eszett where only English belongs,
German abbreviations, German words on the English side of the manual,
and the catalogue as data. A German text missing a %s raises at run
time, and only for people running in German. And one thing has one
German word: a value the interface offers is called the same in every
German text about it, or the log and the field are two names for one
thing.
"""
import ast, io, os, re, sys, time

began = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
import importlib.util
sys.path.insert(0, os.path.dirname(
    os.path.abspath(__file__)))
from fixture_root import fixture
import the_program
SCRIPT = the_program.SCRIPT
# The program is a folder, so its file is called __init__.py and the
# name alone says nothing. What a failing line names is the folder and
# the file together.
SHOWN = os.path.join(os.path.basename(os.path.dirname(SCRIPT)),
                     os.path.basename(SCRIPT))
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
source = io.open(SCRIPT, encoding="utf-8").read()
done = 0
bad = []

#--------------------------------------------------- how much of it really ran
# Every section registers itself here, so the closing lines can say how
# many of them ran. Two kinds of omission want opposite answers: the
# machine's -- no dictionary, no material -- is written down as SKIPPED,
# which run.sh counts; a document that is not there is a check, and red.
SECTIONS = []       # the titles, in the order they are reached
LEFT_OUT = []       # (number, title, what was not done, why)


def section(title):
    """Begin a numbered section and count it."""
    SECTIONS.append(title)
    print("%s%d. %s" % ("" if len(SECTIONS) == 1 else "\n",
                        len(SECTIONS), title))


def left_out(what, why):
    """Write down a piece this machine could not do, and say so at once.

    `what` is "all of it" when the whole section falls away.
    """
    LEFT_OUT.append((len(SECTIONS), SECTIONS[-1], what, why))
    print("  LEFT OUT (%s): %s" % (what, why))


def check(what, ok, detail=""):
    global done
    done += 1
    print("  %-56s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


#-------------------------------------------------------------- the catalogue
tree = ast.parse(source)
catalogue_node = None
catalogue_at = []
for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Subscript) \
                    and isinstance(target.value, ast.Name) \
                    and target.value.id == "CATALOGUE":
                catalogue_node = node
                catalogue_at.append(node.lineno)
section("The catalogue as data")
check("the catalogue is one assignment at the end",
      catalogue_node is not None,
      "%d assignments to CATALOGUE[...] stand at the top level of the "
      "program, at lines %s" % (len(catalogue_at), catalogue_at))
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
    # Player is the ordinary German word too, so both sides are right.
    '  Player: %s',
}
untranslated = [k for k, v in catalogue.items()
                if k == v and k not in SAME_IN_BOTH]
check("nothing was left in English by accident", not untranslated,
      str([repr(x)[:40] for x in untranslated[:3]]))

# One thing, one German word. A value the interface offers carries the
# word the field shows for it, and every German text that names that
# value has to use the same word. Otherwise the log calls the wide shot
# something the field never says, and the reader has to work out that
# the two mean one thing. The English side cannot show this: there the
# field and the text carry the same word already.
offered = sorted(set(vpm.CHOICE_LABELS.values()))
missing = [w for w in offered if w not in catalogue]
check("every value the interface offers has a German word", not missing,
      str(missing))
apart = []
for _english in offered:
    if _english in missing:
        continue
    _german = catalogue[_english]
    named = re.compile(r"(?<![\w-])%s(?![\w-])" % re.escape(_english), re.I)
    spoken = re.compile(r"(?<![\w-])%s" % re.escape(_german), re.I)
    for key, value in catalogue.items():
        # A label entry is the word itself, not a text about it.
        if key in offered or not named.search(key):
            continue
        if not spoken.search(value):
            apart.append("%r wants %r: %r" % (_english, _german, key[:44]))
check("and every German text about it uses that word", not apart,
      "%d: %s" % (len(apart), apart[:2]))

#------------------------------------------------------ umlauts where none belong
section("Umlauts and eszett only where German lives")
GERMAN_LETTERS = re.compile(r"[äöüÄÖÜß]")
# The German texts live in a file of their own, so the program itself is
# read whole. Everything below rests on it having been read at all: an
# empty string holds no umlaut and no abbreviation either, and the two
# sections would report nothing wrong. Said here, so the cause is named.
check("the program itself was read", source.count("\n") > 1000,
      "%d lines in %s, wanted over 1000" % (source.count("\n"), SHOWN))
hits = []
for i, line in enumerate(source.splitlines(), 1):
    if GERMAN_LETTERS.search(line):
        hits.append((i, line.strip()[:60]))
check("no umlaut in the program", not hits, str(hits[:3]))
# Inside the catalogue: only the values may carry them, never the keys.
key_hits = [k for k in catalogue if GERMAN_LETTERS.search(k)]
check("no umlaut in an English catalogue key", not key_hits,
      str([repr(x)[:40] for x in key_hits[:3]]))

#---------------------------------------------------------- abbreviations
section("German abbreviations")
SHORTHAND = (r"\b(?:z\s?\.?\s?B|bzw|ggf|u\s?\.?\s?a|d\s?\.?\s?h|usw|evtl"
             r"|inkl|bspw|vgl|sog|bzgl|i\s?\.?\s?d\s?\.?\s?R|z\s?\.?\s?T"
             r"|o\s?\.?\s?ä|Abb|Nr|ca)\.")
SHORT = re.compile(SHORTHAND)
found = []
for i, line in enumerate(source.splitlines(), 1):
    m = SHORT.search(line)
    if m:
        found.append((i, m.group(0)))
check("none in the program", not found, str(found[:3]))
in_keys = [k for k in catalogue if SHORT.search(k)]
check("none in an English catalogue key", not in_keys,
      str([repr(x)[:40] for x in in_keys[:3]]))

#------------------------------------------------------------- the manual
section("The English documents carry no German")
# One file per chapter and per language. Every English one is scanned;
# a chapter without its twin is caught by the pairing check below.
NAMED = [os.path.join(ROOT, "README.md")]
DOCS = os.path.join(ROOT, "docs")
# The documents for whoever changes the program are in development/,
# and they are English only.
DEV = os.path.join(ROOT, "development")
# Named by hand, so a rename elsewhere would drop them from the scan in
# silence. A document that is not there is the defect this test is for,
# not a reason to check less, so the answer is red.
NAMED += [os.path.join(DEV, "internals.md"),
          os.path.join(DEV, "measurements.md"),
          os.path.join(DEV, "coding_guidelines.md"),
          os.path.join(DEV, "test_guidelines.md"),
          os.path.join(HERE, "README.md")]
absent_named = [os.path.relpath(p, ROOT) for p in NAMED
                if not os.path.exists(p)]
check("every document this test names by hand is there", not absent_named,
      str(absent_named))
# Gone, the lists below come back nearly empty and everything after
# them passes on the strength of what is missing.
check("docs/ is where the chapters are", os.path.isdir(DOCS), DOCS)

BOOKS = [os.path.join(ROOT, "README.md")]
if os.path.isdir(DOCS):
    BOOKS += [os.path.join(DOCS, n) for n in sorted(os.listdir(DOCS))
              if n.endswith(".md") and not n.endswith(".de.md")]
# The coding guidelines are left out here: they talk about the German
# catalogue. They are checked for umlauts further down.
BOOKS += [os.path.join(DEV, "internals.md"),
          os.path.join(DEV, "measurements.md"),
          os.path.join(DEV, "test_guidelines.md")]
# A chapter deleted with its German twin passes the pairing check and
# stops being scanned here; text_lists_match catches it by the link.
BOOKS = [b for b in BOOKS if os.path.exists(b)]
check("the English documents are there", len(BOOKS) > 5, str(len(BOOKS)))

# Every English chapter has a German one beside it, and the other way
# round. A chapter translated on one side only is how a manual drifts.
if os.path.isdir(DOCS):
    # Only chapters are in docs/, so everything found here has to have
    # a twin; the documents in development/ stand without one.
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
    # The machine's doing, not the repository's: without the dictionary
    # the widest check in this file falls away and the rest goes on.
    left_out("the German dictionary over the whole manual",
             "pyspellchecker is not installed")
else:
    # Names of things stay out: they are the same in both languages.
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
section("The other documents")
# The notes under docs/notes/ are German on purpose and not delivered.
# The English manual is scanned for German words above and for umlauts
# here -- an umlaut is the cheapest sign that a translation slipped in.
ENGLISH_ONLY = BOOKS + [os.path.join(DEV, "coding_guidelines.md"),
                        os.path.join(DEV, "test_guidelines.md"),
                        os.path.join(HERE, "README.md")]
for path in ENGLISH_ONLY:
    # The path from the project root, not just the file name: three of
    # these are called README.md and the report has to say which.
    name = os.path.relpath(path, ROOT)
    if not os.path.exists(path):
        # Not an omission: a document of the manual that is not there
        # is the thing this test is for.
        check("%s: no umlaut and no abbreviation" % name, False,
              "the file is not there at all")
        continue
    body = re.sub(r"`[^`]*`", "", io.open(path, encoding="utf-8").read())
    marks = [i for i, line in enumerate(body.splitlines(), 1)
             if GERMAN_LETTERS.search(line) or SHORT.search(line)]
    check("%s: no umlaut and no abbreviation" % name, not marks,
          str(marks[:4]))

section("The tests are English too")
# The detectors carry the words they look for, and only they may.
DETECTORS = {"text_no_german_left_test.py", "source_limits_hold_test.py",
             "text_only_texts_change_test.py"}
mine = sorted(f for f in os.listdir(HERE)
              if f.endswith(".py") and f not in DETECTORS)
# An empty list finds nothing and passes. Said out loud, so this cannot
# come back green from a folder the run never reached.
check("there are tests to read at all", len(mine) > 20, "%d files" % len(mine))
spotted = []
for f in mine:
    body = io.open(os.path.join(HERE, f), encoding="utf-8").read()
    for i, line in enumerate(body.splitlines(), 1):
        if GERMAN_LETTERS.search(line) or SHORT.search(line):
            spotted.append("%s:%d" % (f, i))
check("no umlaut and no abbreviation in a test", not spotted,
      str(spotted[:4]))

section("The program run in German, read back")
# The strongest check, because it needs no list: a line that never went
# through T() stays English, and English function words give it away.
import subprocess
media = os.environ.get("VPM_MEDIA") or fixture("interview")
job = sorted(f for f in (os.listdir(media) if os.path.isdir(media) else [])
             if f.lower().endswith((".wav", ".mov")))
if len(job) < 2:
    # The machine's doing again: run.sh builds this folder and points
    # VPM_MEDIA at it, so under the suite the section runs.
    left_out("all of it", "no material under %s (%d files of the right "
             "kind, two are needed)" % (media, len(job)))
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
    # Words that are English and not also German, and not a term the
    # German text uses as it stands. A hyphen counts as a letter on
    # both sides, because a word glued to one belongs to a name and
    # not to a sentence: the switch --with-libsoxr, the switch
    # --without-auphonic, the cut rule wide-after. Measured 4.9.2026,
    # so the price is known: of the 4877 lines of the English manual
    # this pattern catches, eight fall out of its reach that way, and
    # all eight are names. The limit is the other side of that -- an
    # English line whose only word from the list is glued to a hyphen
    # now goes through.
    ENGLISH = re.compile(r"(?<![A-Za-z-])(the|and|with|from|into|"
                         r"which|would|there|their|because|"
                         r"before|after|between|through|without)"
                         r"(?![A-Za-z-])")
    left = []
    for line in out.splitlines():
        # Paths and file names carry English words and are not text.
        bare = re.sub(r"[^\s]*[/\\][^\s]*", "", line)
        m = ENGLISH.search(bare)
        if m:
            left.append((m.group(0), bare.strip()[:60]))
    check("and no English sentence is left in it", not left, str(left[:3]))

section("What the German manual quotes in English stays English")
# A German chapter may quote program output in English only where that
# output is not translated. Put such a line into the catalogue and the
# program starts saying it in German while the chapter still shows the
# English -- nothing goes red, and the manual quietly lies.
QUOTED = re.compile(r"`([^`\n]{12,})`")
# Placeholders are filled in before anybody sees the line, so a quote and
# its format string never match letter for letter; the fixed parts do.
PLACE = re.compile(r"%[-+ #0-9.]*[a-z%]|\d+(?:\.\d+)?")


def skeleton(text):
    """The fixed parts of a line, without numbers and placeholders."""
    return " ".join(PLACE.sub(" ", text).split())


keys = {}
for key in catalogue:
    bones = skeleton(key)
    if len(bones) >= 12:
        keys.setdefault(bones, key)

GERMAN_BOOKS = [os.path.join(ROOT, "README.de.md")]
if os.path.isdir(DOCS):
    GERMAN_BOOKS += [os.path.join(DOCS, n) for n in sorted(os.listdir(DOCS))
                     if n.endswith(".de.md")]
GERMAN_BOOKS = [b for b in GERMAN_BOOKS if os.path.exists(b)]

german_quotes = []
unread = []
for path in GERMAN_BOOKS:
    try:
        text = io.open(path, encoding="utf-8").read()
    except OSError as why:
        # An unreadable chapter must not drop out of the scan in silence.
        unread.append("%s (%s)" % (os.path.relpath(path, ROOT), why))
        continue
    for span in QUOTED.findall(text):
        german_quotes.append((os.path.basename(path), span))

check("every German chapter could be opened", not unread, str(unread[:3]))
check("the German chapters are readable at all", bool(german_quotes),
      "%d quoted spans" % len(german_quotes))

# A quote in a German chapter matching an English catalogue key shows
# the reader English for a line the program says in German.
translated = [(name, span) for name, span in german_quotes
              if skeleton(span) in keys]
check("no German chapter quotes a line the program translates",
      not translated,
      "%d: %s" % (len(translated), translated[:2]))

# And the other direction: as long as a German chapter shows that line
# in English, it must stay out of the catalogue.
version_line = [span for name, span in german_quotes
                if "recommended version" in span]
check("the version line is quoted in the German chapter",
      bool(version_line), str(version_line[:1]))
check("and it is not in the catalogue, which is why that is right",
      not any(skeleton(x) in keys for x in version_line),
      str(version_line[:1]))

#--------------------------------------------------------- how much was done
# "All good." is a claim about every section, and a lie when only some
# of them ran, so the size of the claim is printed with it.
print("\n%d checks in %.2f s" % (done, time.time() - began))
state = {}
for number, title, what, why in LEFT_OUT:
    if what == "all of it":
        state[number] = "not at all"
    else:
        state.setdefault(number, "in part")
nowhere = sum(1 for v in state.values() if v == "not at all")
partly = sum(1 for v in state.values() if v == "in part")
fully = len(SECTIONS) - len(state)
print("%d sections: %d ran whole, %d in part, %d not at all."
      % (len(SECTIONS), fully, partly, nowhere))
print("%d English documents read, %d German ones."
      % (len(BOOKS), len(GERMAN_BOOKS)))
for number, title, what, why in LEFT_OUT:
    print("  %d. %s -- %s: %s" % (number, title, what, why))

# run.sh knows two verdicts, ran or skipped, and a test that did most of
# its sections is neither. Skipped is the loud one, and it carries the
# fraction, so nobody reads it as "checked nothing".
if LEFT_OUT:
    print("SKIPPED: %d of %d sections ran in full; %s"
          % (fully, len(SECTIONS),
             "; ".join("%d. %s" % (n, why) for n, t, w, why in LEFT_OUT)))
if bad:
    print("FAIL: %d of the checks" % len(bad))
    sys.exit(1)
# "All good." belongs to a whole run; anything less says how much less.
print("All good." if not LEFT_OUT else
      "Good as far as it went -- %d of %d sections." % (fully, len(SECTIONS)))
