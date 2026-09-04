# -*- coding: utf-8 -*-
"""The language machinery: catalogue, detection, switch, log colours.

And the seam itself: every line the program prints goes through the
catalogue, or it comes out English in a German run.

The switch section really starts the program, twice, on a file that is
not there: whether --lang is acted on cannot be read off the parser,
and a wording held against the output would only say what language the
machine itself is set to.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import the_program
SCRIPT = the_program.SCRIPT
# The German texts are a file of their own in the folder "language"
# beside the way in. The program reads them from there, so this test
# looks in the same place and a snapshot run reads the snapshot's own
# texts.
TEXTS_DE = os.path.join(os.path.dirname(SCRIPT), "language", "de.py")
import ast, importlib.util, io, re, subprocess, time, tokenize

began = time.time()

import ratchet

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
STATE = os.path.join(HERE, "state", "language_state.json")
state = ratchet.Ratchet(STATE)
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

done = 0
error = []
def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-54s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

state.announce()

# The code this file uses wherever it needs a language that is not
# there. "qa" is a country, not a language, so no catalogue can ever
# answer to it, and nothing here ships one. French used to stand in
# that place: the day a French catalogue arrived, the check below went
# red and the section under it deleted the real catalogue on its way
# out. A language that exists cannot play a language that does not.
# The checks spell the code out in their names, because the
# counter-proof register reads those as literals.
SPARE = "qa"

print("1. Which languages there are")
check("English is the source", vpm.SOURCE_LANG == "en",
        "SOURCE_LANG is %r, wanted 'en'" % vpm.SOURCE_LANG)
check("German is among them", "de" in vpm.languages(),
        "languages() %s, wanted 'de' among them" % vpm.languages())
got = vpm.known_language("de_DE.UTF-8")
check("de_DE.UTF-8 becomes de", got == "de", "%r, wanted 'de'" % got)
got = vpm.known_language("de-AT")
check("de-AT becomes de", got == "de", "%r, wanted 'de'" % got)
got = vpm.known_language("qa_QA")
check("qa_QA becomes en", got == "en",
        "%r, wanted 'en' -- the program speaks %s, and no %r catalogue is "
        "among them" % (got, vpm.languages(), SPARE))
got = vpm.known_language("")
check("nothing becomes en", got == "en",
        "the empty code gives %r, wanted 'en'" % got)

print("\n2. One more language needs only a catalogue entry")
# A catalogue is put in at run time, under the spare code, and the
# three steps at the head of the program say that is the whole of what
# it takes. It has to be the spare code and not a language the program
# really ships: the entry is taken out again below, and taking a real
# one out would leave every check after this point talking to a program
# with a language missing.
was = vpm.CATALOGUE.get(SPARE)
vpm.CATALOGUE[SPARE] = {"Content": "Content in qa"}
try:
    check("qa is now on offer", SPARE in vpm.languages(),
            "languages() %s, wanted %r among them"
            % (vpm.languages(), SPARE))
    got = vpm.known_language("qa_QA")
    check("qa_QA now becomes qa", got == SPARE,
            "%r, wanted %r" % (got, SPARE))
    vpm.set_language(SPARE)
    got = vpm.T("Content")
    check("translated text comes out of the added catalogue",
            got == "Content in qa",
            "T('Content') under %r is %r, wanted 'Content in qa'"
            % (vpm.LANG, got))
    got = vpm.T("Outro")
    check("missing text stays English", got == "Outro",
            "T('Outro') under %r is %r, wanted 'Outro' -- the %r catalogue "
            "has no entry for it" % (vpm.LANG, got, SPARE))
finally:
    if was is None:
        vpm.CATALOGUE.pop(SPARE, None)
    else:
        vpm.CATALOGUE[SPARE] = was
vpm.set_language("de")

print("\n3. Translating and filling in")
# The German catalogue is the subject here, so this expectation is German.
got = vpm.T("Intro")
check("German comes from the catalogue", got == "Vorspann",
        "T('Intro') under %r is %r, wanted 'Vorspann'" % (vpm.LANG, got))
vpm.set_language("en")
got = vpm.T("Intro")
check("English stays as it stands", got == "Intro",
        "T('Intro') under %r is %r, wanted 'Intro'" % (vpm.LANG, got))
got = vpm.T("a %s c", "b")
check("placeholders get filled", got == "a b c",
        "T('a %%s c', 'b') is %r, wanted 'a b c'" % got)
got = vpm.T("%s-%s", 1, 2)
check("several placeholders", got == "1-2",
        "T('%%s-%%s', 1, 2) is %r, wanted '1-2'" % got)
vpm.set_language("xx")
check("unknown language falls back to English", vpm.LANG == "en",
        "set_language('xx') leaves LANG at %r, wanted 'en'" % vpm.LANG)
vpm.set_language("de")

print("\n4. The --lang switch")
# The three steps at the head of the program say that a catalogue is the
# whole of what it takes to add a language: --lang then offers the new
# code. So one is put into the program here **before the parser is built
# at all**, and stays there while the two directions below are asked.
# Put in first rather than added afterwards with the parser built a
# second time: a program that builds its parser once and hands the same
# one back is right, and rebuilding would have called it broken. What is
# left of that: a program that built its parser as early as import time
# could not see this catalogue either and would be red with nothing
# broken. Nothing in the program points that way today, and a red on the
# two judgements below sends the reader to those three steps first.
# SPARE stands at the head of the file: a code no catalogue answers to.
# Whatever stood under it is put back at once, so a real one would
# survive even if the code ever stopped being spare.
was = vpm.CATALOGUE.get(SPARE)
vpm.CATALOGUE[SPARE] = {"Content": "Content"}
try:
    ap = vpm.build_argument_parser()
    speaks = vpm.languages()
finally:
    if was is None:
        vpm.CATALOGUE.pop(SPARE, None)
    else:
        vpm.CATALOGUE[SPARE] = was
lang = [a for a in ap._actions if "--lang" in (a.option_strings or [])]
check("it is there", bool(lang),
        "%d of the %d actions carry --lang, wanted 1"
        % (len(lang), len(ap._actions)))
# Everything below rests on the switch being there and on its list of
# values existing at all, so both are asked before either is used: a
# switch that is gone, or one that takes anything at all, is then a red
# line of its own instead of a traceback that swallows the fifty checks
# after it.
picks = lang[0].choices if lang else None
check("the switch says which values it takes", picks is not None,
        "--lang has %r for its choices, wanted a list of language codes"
        % (picks,))
offered = sorted(picks or [])
strange = [w for w in offered if w not in speaks]
check("it offers no language the program cannot speak", not strange,
        "--lang offers %s, the program speaks %s, over and above that: %s"
        % (offered, speaks, strange))
# And the other way round, which is the direction that bites on a real
# fault: a language whose catalogue lies in the file but which --lang
# will not take cannot be asked for at all, and no other check here
# would notice. It is asked over every language there is and not over
# the two this file knows by name, so a third catalogue is covered the
# day somebody adds one -- and because the catalogue above was put in
# before the parser, a list of codes written into the switch by hand
# falls here too, which is what "reaches the switch" really means.
absent = [w for w in speaks if w not in offered]
check("every language the program speaks is on the switch", not absent,
        "the program speaks %s (a %r catalogue was put in before the "
        "parser was built), --lang offers %s, not on offer: %s"
        % (speaks, SPARE, offered, absent))
got = ap.parse_args([]).lang
check("without a value: system language", got is None,
        "lang is %r without the switch, wanted None" % got)
got = ap.parse_args(["--lang", "en"]).lang
check("with a value it arrives", got == "en",
        "--lang en gives %r, wanted 'en'" % got)
# Arriving in the parser is not the same as being acted on. A run whose
# --lang goes nowhere falls back on the system's language, and on a
# machine set to German that looks exactly right -- which is why the
# program is really started here, once per language, on a file that is
# not there so nothing is read and nothing is written. The two runs
# only have to differ: no wording is held against anything, so this
# says the same on a German machine and on an English one. Both streams
# together, because the line that names a missing file goes to stderr
# and the banner above it is language-free.
GONE = "/tmp/vpm-no-such-recording.wav"
# The program looks for ffmpeg before it ever looks at --lang, and where
# it finds none it offers the package manager -- asked, and only where
# somebody is there to answer. A question about the language must not
# reach even that, so the run gets no console to be asked on, and a pip
# that can neither reach an index nor write outside a virtual
# environment.
#
# The pip half is kept although the program no longer fetches ffmpeg
# that way. It still fetches numpy and PySide6, and it asks first -- but
# this seal is what an unasked install would have run into, and it is
# not theory: an earlier version of these two runs put a wheel of
# ffmpeg binaries into the system Python. A seal is cheap; taking one
# away because the hole it covers is closed today is how the hole comes
# back.
SEALED = dict(os.environ, VPM_NO_UPDATE_CHECK="1",
              PIP_NO_INDEX="1", PIP_REQUIRE_VIRTUALENV="1", PIP_NO_INPUT="1")
SEALED.pop("VPM_INSTALL_TOOLS", None)
spoken, codes = {}, {}
for _code in ("de", "en"):
    try:
        _r = subprocess.run([sys.executable, SCRIPT, "--lang", _code, GONE],
                            capture_output=True, stdin=subprocess.DEVNULL,
                            timeout=300, env=SEALED)
        spoken[_code] = _r.stdout + _r.stderr
        codes[_code] = _r.returncode
    except subprocess.TimeoutExpired:
        spoken[_code], codes[_code] = b"", "timed out after 300 s"
# Asked before the judgement under it, and not folded into it: a
# machine on which the program cannot start at all prints the same
# thing twice, and that must read as "it did not run" and not as
# "--lang does nothing".
fell_over = b"Traceback" in spoken["de"] + spoken["en"]
check("the program answers on both runs",
        bool(spoken["de"]) and bool(spoken["en"])
        and codes["de"] == codes["en"] and not fell_over,
        "--lang de: %d characters, returned %s; --lang en: %d characters, "
        "returned %s; a traceback in them: %s"
        % (len(spoken["de"]), codes["de"], len(spoken["en"]), codes["en"],
           "yes" if fell_over else "no"))
apart = ""
for _a, _b in zip(spoken["de"].splitlines(), spoken["en"].splitlines()):
    if _a != _b:
        apart = "%s against %s" % (repr(_a[:36]), repr(_b[:36]))
        break
check("--lang is acted on, not only accepted",
        spoken["de"] != spoken["en"],
        "--lang de and --lang en print %d and %d characters; first line "
        "that differs: %s" % (len(spoken["de"]), len(spoken["en"]),
                              apart or "none -- the two runs are the same"))

print("\n5. Values and labels are separate")
# One check per constant, each with its name written out. A name built
# in a loop leaves the register a single wording for seven judgements,
# and the register cannot then say which of the seven was ever seen red
# -- six of these had never been broken while the row said "proved".


def bare(name):
    """Is that constant a value rather than a text, and the evidence."""
    value = getattr(vpm, name, None)
    if not isinstance(value, str):
        return (False, "%s is %r -- not a text at all" % (name, value))
    return (re.match(r"^[a-z][a-z-]*$", value) is not None,
            "%s is %r, wanted lower case letters and dashes only"
            % (name, value))


check("MIX_ONLY is language-free", *bare("MIX_ONLY"))
check("IGNORE_AUDIO is language-free", *bare("IGNORE_AUDIO"))
check("PRESET_NONE is language-free", *bare("PRESET_NONE"))
check("TYPE_CONTENT is language-free", *bare("TYPE_CONTENT"))
check("TYPE_INTRO is language-free", *bare("TYPE_INTRO"))
check("TYPE_OUTRO is language-free", *bare("TYPE_OUTRO"))
check("TYPE_IGNORED is language-free", *bare("TYPE_IGNORED"))
vpm.set_language("de")
got = vpm.label_of(vpm.TYPE_INTRO)
check("German label", got == "Vorspann",
        "label_of(TYPE_INTRO) under %r is %r, wanted 'Vorspann'"
        % (vpm.LANG, got))
vpm.set_language("en")
got = vpm.label_of(vpm.TYPE_INTRO)
check("English label", got == "Intro",
        "label_of(TYPE_INTRO) under %r is %r, wanted 'Intro'"
        % (vpm.LANG, got))
got = vpm.label_of("Camera 1.mov")
check("unknown text stays as it is", got == "Camera 1.mov",
        "label_of('Camera 1.mov') is %r, wanted it handed back unchanged"
        % got)
vpm.set_language("de")

print("\n6. The kind of a log line sits on the text, not in the word")
got = vpm.split_kind(vpm.as_head("X"))
check("heading", got == ("heading", "X"),
        "%r, wanted ('heading', 'X')" % (got,))
got = vpm.split_kind(vpm.as_good("X"))
check("success", got == ("good", "X"), "%r, wanted ('good', 'X')" % (got,))
got = vpm.split_kind(vpm.as_warn("X"))
check("warning", got == ("warning", "X"),
        "%r, wanted ('warning', 'X')" % (got,))
got = vpm.split_kind(vpm.as_bad("X"))
check("error", got == ("error", "X"), "%r, wanted ('error', 'X')" % (got,))
got = vpm.split_kind("CAREFUL: all good")
check("without a marker: plain text",
        got == ("text", "CAREFUL: all good"),
        "%r, wanted ('text', 'CAREFUL: all good')" % (got,))
got = vpm.strip_marks(vpm.as_bad("X") + " " + vpm.as_head("Y"))
check("the marker can be stripped", got == "X Y",
        "%r, wanted 'X Y'" % got)
got = vpm.strip_marks("nothing to do")
check("without a marker the text stays the same", got == "nothing to do",
        "%r, wanted 'nothing to do'" % got)

print("\n7. The terminal colours by that and leaves nothing behind")
class Catch(object):
    def __init__(self): self.text = ""
    def write(self, t): self.text += t
    def flush(self): pass

f = Catch(); w = vpm.ColourWriter(f, colour=True)
w.write(vpm.as_head("RESULT") + "\n")
check("colour for the heading", vpm.ANSI["heading"] in f.text, repr(f.text))
check("the marker is gone", "\x01" not in f.text,
        "written %r, wanted no \\x01 left in it" % f.text)
check("the text stands there untouched", "RESULT" in f.text,
        "written %r, wanted 'RESULT' inside it" % f.text)

f = Catch(); w = vpm.ColourWriter(f, colour=False)
w.write(vpm.as_bad("Abort") + "\n")
check("without colour only the text", f.text == "Abort\n", repr(f.text))

f = Catch(); w = vpm.ColourWriter(f, colour=True)
w.write(vpm.as_head("\nRESULT") + "\n  Line\n")
check("a marker before the break belongs to the next line",
        f.text.startswith("\n" + vpm.ANSI["heading"] + "RESULT"),
        repr(f.text[:40]))
check("the line below stays uncoloured",
        f.text.endswith("  Line\n"), repr(f.text[-20:]))

f = Catch(); w = vpm.ColourWriter(f, colour=True)
w.write("  Done without a marker\n")
check("without a marker no colour", "\033[" not in f.text, repr(f.text))

print("\n8. The log window colours the same way")
# The source is read as text, so no window and no Qt: an application
# built here bought nothing and cost half the run. The branch that
# stood in for a missing PySide6 asserted True and could not fail.
source = io.open(SCRIPT, encoding="utf-8").read()


def sightings(needle):
    """How often a piece of source stands in the program, and where first.

    The evidence for every check that looks for a literal: the count says
    what was found, and the line number says where to go and look. Whole,
    never cut -- a shortened needle hides the half that mattered.
    """
    n = source.count(needle)
    if not n:
        return "stands 0 times in the program"
    return "stands %d %s in the program, first on line %d" % (
        n, "time" if n == 1 else "times",
        source[:source.find(needle)].count("\n") + 1)


check("the log reads the marker",
        "split_kind(part)" in source and "self._kind" in source,
        "split_kind(part) %s; self._kind %s -- wanted both at least once"
        % (sightings("split_kind(part)"), sightings("self._kind")))
check("the file gets the text without the marker",
        "self.having.write(strip_marks(text))" in source,
        "%r %s, wanted at least once"
        % ("self.having.write(strip_marks(text))",
           sightings("self.having.write(strip_marks(text))")))

print("\n9. Every T() text is in the catalogue")
tree = ast.parse(io.open(SCRIPT, encoding="utf-8").read())
asked = []
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
            and node.func.id in ("T", "TN") and node.args:
        # T(text, ...) -- TN(number, singular, plural)
        args = node.args[1:] if node.func.id == "TN" else node.args[:1]
        for a in args:
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                asked.append(a.value)
for t in vpm.CHOICE_LABELS.values():
    asked.append(t)
absent = sorted(set(t for t in asked if t not in vpm.CATALOGUE["de"]))
check("no gap in the German catalogue", not absent,
        "%d missing: %s" % (len(absent), absent[:3]))

print("\n10. No output line guesses its colour from the wording")
OUTPUT = {"print", "write_through", "write", "append_text", "OUTPUT_SINK"}
MARKERS = {"as_head", "as_good", "as_warn", "as_bad"}

def first_text(node):
    while True:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.BinOp) and isinstance(node.op,
                                                      (ast.Mod, ast.Add)):
            node = node.left
            continue
        return None

unmarked = []
for node in ast.walk(tree):
    if not isinstance(node, ast.Call) or not node.args:
        continue
    if isinstance(node.func, ast.Name):
        name = node.func.id
    elif isinstance(node.func, ast.Attribute):
        # f.write(...) writes a file, not the log.
        if isinstance(node.func.value, ast.Name) \
                and node.func.value.id in ("f", "file"):
            continue
        name = node.func.attr
    else:
        name = ""
    if name not in OUTPUT:
        continue
    if isinstance(node.args[0], ast.Call) \
            and isinstance(node.args[0].func, ast.Name) \
            and node.args[0].func.id in MARKERS:
        continue
    t = first_text(node.args[0])
    if t is None:
        continue
    first = ([line for line in t.split("\n") if line.strip()]
             or [""])[0]
    head = first.strip().split(":", 1)[0]
    if first[:1] not in (" ", "\t") and len(head) > 2 \
            and head == head.upper() and re.search(r"[A-Z]", head) \
            and not head.startswith("%"):
        unmarked.append((node.lineno, first[:60]))
old = state.number("uncoloured", len(unmarked))
check("headings without a marker: %d (ratchet %d)" % (len(unmarked), old),
        len(unmarked) <= old, str(unmarked[:3]))

print("\n11. The old word detection is really gone")
source = io.open(SCRIPT, encoding="utf-8").read()
check("no log_line_kind any more", "log_line_kind" not in source,
        "log_line_kind %s, wanted 0 times" % sightings("log_line_kind"))
# The words the old guesser read the colour off, one check each and
# each name written out: a name built in a loop gives the register one
# wording for three judgements, and two of the three were never broken.
check("colour no longer hangs on 'DONE'", "DONE" not in source,
        "%r %s, wanted 0 times" % ("DONE", sightings("DONE")))
check("colour no longer hangs on 'failed\" in'",
        "failed\" in" not in source,
        "%r %s, wanted 0 times"
        % ("failed\" in", sightings("failed\" in")))
check("colour no longer hangs on 'Finished with errors\" in'",
        "Finished with errors\" in" not in source,
        "%r %s, wanted 0 times"
        % ("Finished with errors\" in",
           sightings("Finished with errors\" in")))

print("\n12. Switches and targets are English")
# The list stays German on purpose: it is what must not turn up.
GERMAN = ("ohne", "kein", "totale", "sprache_", "vorne", "hinten",
          "zuordnung", "trotzdem", "dateien", "mindest", "plattform",
          "vorflug", "pruefen", "projekt", "tonspuren", "warten", "weiter",
          "fertig", "schnitt", "spuren", "kennzahlen", "sprecher")
ap = vpm.build_argument_parser()
bad = []
for entry in ap._actions:
    for o in (entry.option_strings or [entry.dest]):
        label = o.lstrip("-").replace("-", "_")
        for d in GERMAN:
            if d in label or d in (entry.dest or ""):
                bad.append((o, entry.dest, d))
check("no German switch, no German target", not bad, str(bad[:3]))
bad_choices = []
for entry in ap._actions:
    for w in (entry.choices or []):
        if not isinstance(w, str):
            continue
        for d in ("ergebnis", "uebernehmen", "hochladen", "abbruch", "neu",
                  "aktualisieren", "verwenden", "rundfunk"):
            if w == d:
                bad_choices.append((entry.dest, w))
check("no German choice values", not bad_choices, str(bad_choices))


print("\n13. Every language writes numbers its own way")
vpm.set_language("de")
got = vpm.decimal_text("%.3f" % 25.0)
check("German: comma", got == "25,000",
        "decimal_text('25.000') under %r is %r, wanted '25,000'"
        % (vpm.LANG, got))
check("German: clock time", vpm.as_hms(3725.5) == "1:02:05,500",
        "as_hms(3725.5) is %r, wanted '1:02:05,500'" % vpm.as_hms(3725.5))
vpm.set_language("en")
got = vpm.decimal_text("%.3f" % 25.0)
check("English: dot", got == "25.000",
        "decimal_text('25.000') under %r is %r, wanted '25.000'"
        % (vpm.LANG, got))
check("English: clock time", vpm.as_hms(3725.5) == "1:02:05.500",
        "as_hms(3725.5) is %r, wanted '1:02:05.500'" % vpm.as_hms(3725.5))
check("no hard-coded comma left in the source",
        'replace(".", ",")' not in source,
        "%r %s, wanted 0 times"
        % ('replace(".", ",")', sightings('replace(".", ",")')))
vpm.set_language("de")
got = vpm.group_text(48000)
check("German: thousands with a dot", got == "48.000",
        "group_text(48000) under %r is %r, wanted '48.000'" % (vpm.LANG, got))
vpm.set_language("en")
got = vpm.group_text(48000)
check("English: thousands with a comma", got == "48,000",
        "group_text(48000) under %r is %r, wanted '48,000'" % (vpm.LANG, got))
check("no hard-coded thousands mark left",
        'format(SR, ",d").replace' not in source,
        "%r %s, wanted 0 times"
        % ('format(SR, ",d").replace', sightings('format(SR, ",d").replace')))
vpm.set_language("de")

print("\n14. No translation as early as import time")
import ast as _ast
_b = _ast.parse(source)
def _module_level(node):
    for k in _ast.iter_child_nodes(node):
        if isinstance(k, (_ast.FunctionDef, _ast.AsyncFunctionDef,
                          _ast.ClassDef)):
            continue
        if isinstance(k, _ast.Call) and isinstance(k.func, _ast.Name) \
                and k.func.id in ("T", "TN"):
            yield k
        for x in _module_level(k):
            yield x
_early = list(_module_level(_b))
check("no T()/TN() at module level", not _early,
        str([k.lineno for k in _early[:3]]))


print("\n15. The marker stays in the log")
import ast as _a2
_b2 = _a2.parse(source)
_MARK = {"as_head", "as_good", "as_warn", "as_bad"}
_in_file = []
for _k in _a2.walk(_b2):
    if isinstance(_k, _a2.Call) and isinstance(_k.func, _a2.Attribute) \
            and _k.func.attr == "write" \
            and isinstance(_k.func.value, _a2.Name) \
            and _k.func.value.id in ("f", "file"):
        for _x in _a2.walk(_k):
            if isinstance(_x, _a2.Call) and isinstance(_x.func, _a2.Name) \
                    and _x.func.id in _MARK:
                _in_file.append(_k.lineno)
check("no marker in a written file", not _in_file, str(_in_file[:3]))

print("\n16. Numbers in files do not hang on the language")
check("the metrics CSV writes with a dot",
        'return "" if x is None else "%.*f" % (spots, x)' in source,
        "the rounding line %r %s, wanted at least once"
        % ('return "" if x is None else "%.*f" % (spots, x)',
           sightings('return "" if x is None else "%.*f" % (spots, x)')))
check("the speakers CSV too", 'as_hms(a, ".")' in source,
        "%r %s, wanted at least once"
        % ('as_hms(a, ".")', sightings('as_hms(a, ".")')))
# The headers go through csv_line() as tuples, so the checks look for
# the tuple rather than for a finished line. The whole header stands in
# the evidence, not the shortened one the name carries: what is cut off
# is where a changed column would sit. And the names are written out
# rather than built in the loop that used to stand here -- one wording
# for three judgements told the register nothing about which of the
# three had ever been seen red.
HEAD_METRICS = '("Area", "Metric", "Before", "After",'
HEAD_SPEAKERS = '("Speaker", "Start TC", "End TC",'
HEAD_SHOTS = '("Shot", "Camera", "Speaker", "Start TC",'
check('CSV header fixed: "Area", "Metric", "Before",',
        HEAD_METRICS in source,
        "%r %s, wanted at least once"
        % (HEAD_METRICS, sightings(HEAD_METRICS)))
check('CSV header fixed: "Speaker", "Start TC", "End',
        HEAD_SPEAKERS in source,
        "%r %s, wanted at least once"
        % (HEAD_SPEAKERS, sightings(HEAD_SPEAKERS)))
check('CSV header fixed: "Shot", "Camera", "Speaker",',
        HEAD_SHOTS in source,
        "%r %s, wanted at least once"
        % (HEAD_SHOTS, sightings(HEAD_SHOTS)))
check("CSV rows are comma separated, never by language",
        'return ",".join(out) + "\\n"' in source,
        "the joining line %r %s, wanted at least once"
        % ('return ",".join(out) + "\\n"',
           sightings('return ",".join(out) + "\\n"')))
check("no semicolon separator left",
        'f.write("%s;' not in source and '";".join(str(x) for x in r)'
        not in source,
        "%r %s; %r %s -- wanted 0 times each"
        % ('f.write("%s;', sightings('f.write("%s;'),
           '";".join(str(x) for x in r)',
           sightings('";".join(str(x) for x in r)')))

print("\n17. No German word outside the catalogue")
# Two dictionaries decide, and the catalogue acts as a third: a word
# German knows and English does not is German, and so is every word the
# German side of the catalogue uses and the English side does not.
german = io.open(TEXTS_DE, encoding="utf-8").read()
GERMAN_KEEP = set("""
bilder dokumente filme musik schreibtisch deutsch
""".split())          # folder names on a German system, on purpose
# "deutsch" stands apart: it marks the German half of a release text and
# a German reader looks for that word and no other, so it has to be the
# German one. A label for readers, not prose in the source.
NOT_GERMAN = set("""
also alt ansi antialiasing api ascii backend byte codec codecs cpu ctrl
eng ext frontend gbr html installation iso lang man marker mpeg multi
normal popen programme sei stand std standard systems url urls xml
""".split())          # technical words a German dictionary happens to know


def word_parts(word):
    """Split a name, a text or a comment into its word parts."""
    out = []
    for piece in re.split(r"[^0-9A-Za-z\u00c0-\u024f]+", word):
        for part in re.findall(r"[A-Z]?[a-z\u00df-\u00ff]+"
                                r"|[A-Z]+(?![a-z])", piece):
            if len(part) > 2:
                out.append(part.lower())
    return out


def catalogue_words():
    """German words the catalogue uses and the English side does not."""
    keys, values = set(), set()
    for node in ast.walk(ast.parse(german)):
        if not isinstance(node, ast.Dict):
            continue
        for a, b in zip(node.keys, node.values):
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                keys.update(word_parts(a.value))
            if isinstance(b, ast.Constant) and isinstance(b.value, str):
                values.update(word_parts(b.value))
    return values - keys


def german_check():
    """A test for "is this word German" -- None without a dictionary."""
    try:
        from spellchecker import SpellChecker
    except ImportError:
        return None
    de, en = SpellChecker(language="de"), SpellChecker(language="en")
    return lambda w: w in de and w not in en


_known = catalogue_words()
_is_german = german_check()
# The whole program, top to bottom: the German it used to carry at the
# end now stands in a file of its own, and nothing in here may be German.
_found = []
for _t in tokenize.generate_tokens(io.StringIO(source).readline):
    if _t.type not in (tokenize.NAME, tokenize.STRING, tokenize.COMMENT):
        continue
    # A long run without a space is data (base64, a hash), not language.
    if _t.type == tokenize.STRING and len(_t.string) > 40 \
            and " " not in _t.string:
        continue
    for _w in word_parts(_t.string):
        if _w in NOT_GERMAN or _w in GERMAN_KEEP:
            continue
        if _w in _known or (_is_german and _is_german(_w)):
            _found.append((_t.start[0], _w))
check("a dictionary is installed", _is_german is not None,
        "" if _is_german else "pip install pyspellchecker")
_limit = state.number("german_words", len(_found))
check("German words: %d (ratchet %d)" % (len(_found), _limit),
        len(_found) <= _limit, str(sorted(set(w for _z, w in _found))[:6]))

print("\n18. No English word forgotten on the German side")
# The mirror of section 17: English left standing in the German
# catalogue. What the catalogue translates elsewhere the project decided
# to translate, so an untranslated place was forgotten -- at least three
# translations, and three times as many as the places kept. A word
# nobody ever translated cannot show up here.
NAMES = re.compile(u"\"[^\"]*\"|„[^“]*“"   # what is quoted
                   u"|<[^>]*>"                            # markup
                   u"|--[a-z][a-z-]*"                     # a switch
                   u"|%\\([A-Za-z_]+\\)"                  # a placeholder
                   u"|[A-Za-z0-9_.-]+\\.[a-z]{2,4}\\b"    # file, host
                   u"|\\b[A-Z][A-Z_]{2,}\\b")             # PATH, HDR


def free_words(text):
    """The words of a text, without what is a quotation or a name."""
    return set(w.lower() for w in
               re.findall(u"[A-Za-zÀ-ɏ]+", NAMES.sub(" ", text))
               if len(w) >= 4)


def english_check():
    """A test for "is this English and not German" -- None without one."""
    try:
        from spellchecker import SpellChecker
    except ImportError:
        return None
    de, en = SpellChecker(language="de"), SpellChecker(language="en")
    return lambda w: w in en and w not in de


_entries = []
for _node in ast.walk(ast.parse(german)):
    if not isinstance(_node, ast.Dict):
        continue
    for _a, _b in zip(_node.keys, _node.values):
        if isinstance(_a, ast.Constant) and isinstance(_a.value, str) \
                and isinstance(_b, ast.Constant) and isinstance(_b.value, str):
            _entries.append((_a.lineno, _a.value, _b.value))
check("the German catalogue can be read as pairs", len(_entries) > 500,
        "%d entries" % len(_entries))

_english = english_check()
_stands, _turned = {}, {}
if _english:
    for _line, _key, _value in _entries:
        _there = free_words(_value)
        for _w in free_words(_key):
            if not _english(_w):
                continue
            if _w in _there:
                _stands.setdefault(_w, []).append((_line, _key))
            else:
                _turned[_w] = _turned.get(_w, 0) + 1

_forgotten = []
for _w, _where in _stands.items():
    _often = _turned.get(_w, 0)
    if _often >= 3 and _often >= 3 * len(_where):
        for _line, _key in _where:
            _forgotten.append((_line, _w, _key))
_forgotten.sort()

if _english is None:
    # Not a judgement any more, and it never was one: it read True, so
    # no change to the program could move it, and it stood in the branch
    # that only runs when there is no dictionary -- that is, when the
    # check above has already gone red. What is left is the piece that
    # was not done, written in the shape run.sh greps for. It is read
    # here by a person and not by run.sh: both places that pick LEFT OUT
    # up sit in the branch for a run already recorded green, and a run
    # without a dictionary is red on the check above.
    print("      LEFT OUT: the German side was not read -- 0 of the %d "
          "catalogue entries, pip install pyspellchecker" % len(_entries))
else:
    # The fingerprint is the word plus the entry it was left in, never
    # the line: every entry added above one shifts it down a row.
    _held = state.places("english_words", ratchet.tally(
        [("%s in %r" % (_w, _key[:48]), _line)
         for _line, _w, _key in _forgotten]))
    check("English words on the German side: %d (ratchet %d)"
            % (len(_forgotten), _held.limit), _held.ok,
            str(sorted(set(w for _z, w, _y in _forgotten))))
    _held.report()

print("\n19. Every printed line goes through the catalogue")
# A print() whose own words never reach T() comes out English in a
# German run, and nothing else here sees it: the words stand in the
# source, so section 17 finds no German in them, and they are not in
# the catalogue, so section 18 has nothing to hold them against.
_WORDY = re.compile(r"[A-Za-z]{3,}")


def _shown(node):
    """The text an expression puts on screen, ignoring what it fills in.

    A plain function -- as_head, as_bad -- hands its argument on to the
    screen, so the text inside it counts. A method call does not:
    state.get("results") names a key nobody ever reads, and following
    it made the check report a dictionary as an untranslated line.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        return _shown(node.left)
    if isinstance(node, ast.JoinedStr):
        return [v.value for v in node.values
                if isinstance(v, ast.Constant) and isinstance(v.value, str)]
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        if node.func.id in ("T", "TN"):
            return []
        out = []
        for a in node.args:
            out += _shown(a)
        return out
    return []


_whole = ast.parse(source)
_where = ratchet.owners(_whole)
_prints, _raw = 0, []
for _node in ast.walk(_whole):
    if not (isinstance(_node, ast.Call) and isinstance(_node.func, ast.Name)
            and _node.func.id == "print" and _node.args):
        continue
    _prints += 1
    if any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
           and n.func.id in ("T", "TN") for n in ast.walk(_node.args[0])):
        continue
    for _text in _shown(_node.args[0]):
        if _WORDY.search(_text):
            _raw.append(("%s prints %r"
                         % (_where.get(id(_node), "<module>"), _text[:44]),
                         _node.lineno))
# The count before the judgement: a detector that reads no print at all
# would report nothing left in English and look like the best news of
# the run.
check("the print calls were read at all", _prints > 200,
        "%d found, wanted over 200" % _prints)
_held = state.places("untranslated_prints", ratchet.tally(_raw))
check("printed lines outside the catalogue: %d (ratchet %d)"
        % (len(_raw), _held.limit), _held.ok,
        "" if _held.ok else "a printed line that used to go through T() "
        "no longer does, or a new one never did")
_held.report()
if _held.tightened:
    print("      ratchet tightened to %d" % len(_raw))

# The suite runs under LANG=C, so hand the module back in English.
vpm.set_language("en")

print("\n%d checks in %.2f s" % (done, time.time() - began))
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
