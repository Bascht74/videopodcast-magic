# -*- coding: utf-8 -*-
"""The language machinery: catalogue, detection, switch, log colours.

And the seam itself: every line the program prints goes through the
catalogue, or it comes out English in a German run.

How a count picks a wording is asked of the catalogue, not of the
program: a PO header carries its language's own rule, and the last
section reads real rules -- German, French, Japanese, Russian, Arabic
-- and holds them against what CLDR says. Then it holds the shipped
Russian catalogue to its own rule: three wordings for every counted
thing it answers for, and the right one of the three at seven counts.
Last of all it asks the same of every language the program offers, so
that a catalogue cannot arrive with a rule and no wordings under it:
Arabic at the six counts it tells apart, French at nought and at two,
where French counts differently from English and where an exchange of
its two forms would otherwise hide.

The switch section really starts the program, twice, on a file that is
not there: whether --lang is acted on cannot be read off the parser,
and a wording held against the output would only say what language the
machine itself is set to.

What is read as text is read out of every piece of the program, not out
of the file it starts in: a word looked for in one file goes missing
the day it moves into another, and a check that asks whether a word is
gone then passes because the file it read no longer holds it.
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
TEXTS_DE = os.path.join(os.path.dirname(SCRIPT), "language", "de.po")
import ast, importlib.util, io, re, shutil, subprocess, tempfile
import time, tokenize

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
# Every piece of the program, not the file it starts in alone: a word
# looked for in one file is not found once it moves into another, and
# a check that only says "it is not there any more" then passes for
# the wrong reason.
PIECES = the_program.pieces()
source = "\n".join(body for _name, body in PIECES)


def sightings(needle):
    """How often a piece of source stands in the program, and where first.

    The evidence for every check that looks for a literal: the count says
    what was found, and the piece and line say where to go and look.
    Whole, never cut -- a shortened needle hides the half that mattered.
    """
    n = sum(body.count(needle) for _name, body in PIECES)
    if not n:
        return "stands 0 times in the program"
    for name, body in PIECES:
        if needle in body:
            return "stands %d %s in the program, first in %s on line %d" % (
                n, "time" if n == 1 else "times", name,
                body[:body.find(needle)].count("\n") + 1)


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
TREES = [(name, ast.parse(body)) for name, body in PIECES]
asked = []
for _name, tree in TREES:
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
# A counted thing lives in PLURALS, not in CATALOGUE: read_po puts a
# msgid with a msgid_plural under it into the wordings and leaves it out
# of the ordinary texts. Looking only in CATALOGUE would report the
# forty German counted things as gaps the day they became blocks.
absent = sorted(set(t for t in asked
                    if t not in vpm.CATALOGUE["de"]
                    and t not in vpm.language.PLURALS.get("de", {})))
check("no gap in the German catalogue", not absent,
        "%d missing: %s" % (len(absent), absent[:3]))

# read_po overwrites the first entry without a word, so a wording that
# stands twice is invisible everywhere else. Measured 5.9.2026: a
# doubled entry ran green through this test, text_no_german_left,
# text_german_arrives and source_no_loose_ends. It is what a merge of
# two catalogues makes when one branch renamed a wording and the other
# laid the new one beside the old.
twice = []
for name in sorted(vpm.CATALOGUE):
    where = os.path.join(os.path.dirname(vpm.__file__), "language",
                         "%s.po" % name)
    if not os.path.exists(where):
        continue
    said = {}
    with io.open(where, encoding="utf-8") as f:
        for line in f:
            if line.startswith("msgid \"") and line.strip() != 'msgid ""':
                said[line.strip()] = said.get(line.strip(), 0) + 1
    twice += ["%s: %s" % (name, k) for k, n in sorted(said.items()) if n > 1]
check("no wording stands twice in a catalogue", not twice,
      "%d doubled: %s" % (len(twice), twice[:3]))

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

def heading_without_marker(node):
    """The first line of an output call that shouts and carries no marker."""
    if not isinstance(node, ast.Call) or not node.args:
        return None
    if isinstance(node.func, ast.Name):
        name = node.func.id
    elif isinstance(node.func, ast.Attribute):
        # f.write(...) writes a file, not the log.
        if isinstance(node.func.value, ast.Name) \
                and node.func.value.id in ("f", "file"):
            return None
        name = node.func.attr
    else:
        name = ""
    if name not in OUTPUT:
        return None
    if isinstance(node.args[0], ast.Call) \
            and isinstance(node.args[0].func, ast.Name) \
            and node.args[0].func.id in MARKERS:
        return None
    t = first_text(node.args[0])
    if t is None:
        return None
    first = ([line for line in t.split("\n") if line.strip()]
             or [""])[0]
    head = first.strip().split(":", 1)[0]
    if first[:1] not in (" ", "\t") and len(head) > 2 \
            and head == head.upper() and re.search(r"[A-Z]", head) \
            and not head.startswith("%"):
        return first[:60]
    return None


unmarked = []
for piece, tree in TREES:
    for node in ast.walk(tree):
        first = heading_without_marker(node)
        if first is not None:
            unmarked.append(("%s %d" % (piece, node.lineno), first))
old = state.number("uncoloured", len(unmarked))
check("headings without a marker: %d (ratchet %d)" % (len(unmarked), old),
        len(unmarked) <= old, str(unmarked[:3]))

print("\n11. The old word detection is really gone")
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
got = vpm.number_text(25.0, 3)
check("German: comma", got == "25,000",
        "number_text(25.0, 3) under %r is %r, wanted '25,000'"
        % (vpm.LANG, got))
check("German: clock time", vpm.as_hms(3725.5) == "1:02:05,500",
        "as_hms(3725.5) is %r, wanted '1:02:05,500'" % vpm.as_hms(3725.5))
vpm.set_language("en")
got = vpm.number_text(25.0, 3)
check("English: dot", got == "25.000",
        "number_text(25.0, 3) under %r is %r, wanted '25.000'"
        % (vpm.LANG, got))
check("English: clock time", vpm.as_hms(3725.5) == "1:02:05.500",
        "as_hms(3725.5) is %r, wanted '1:02:05.500'" % vpm.as_hms(3725.5))
check("no hard-coded comma left in the source",
        'replace(".", ",")' not in source,
        "%r %s, wanted 0 times"
        % ('replace(".", ",")', sightings('replace(".", ",")')))
vpm.set_language("de")
got = vpm.number_text(48000, 0)
check("German: thousands with a dot", got == "48.000",
        "number_text(48000, 0) under %r is %r, wanted '48.000'"
        % (vpm.LANG, got))
vpm.set_language("en")
got = vpm.number_text(48000, 0)
check("English: thousands with a comma", got == "48,000",
        "number_text(48000, 0) under %r is %r, wanted '48,000'"
        % (vpm.LANG, got))
check("no hard-coded thousands mark left",
        'format(SR, ",d").replace' not in source,
        "%r %s, wanted 0 times"
        % ('format(SR, ",d").replace', sightings('format(SR, ",d").replace')))
vpm.set_language("de")

print("\n14. No translation as early as import time")
import ast as _ast
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
_early = [("%s %d" % (_piece, _k.lineno))
          for _piece, _b in TREES for _k in _module_level(_b)]
check("no T()/TN() at module level", not _early,
        str(_early[:3]))


print("\n15. The marker stays in the log")
import ast as _a2
_MARK = {"as_head", "as_good", "as_warn", "as_bad"}
_in_file = []
for _piece, _b2 in TREES:
    for _k in _a2.walk(_b2):
        if not (isinstance(_k, _a2.Call)
                and isinstance(_k.func, _a2.Attribute)
                and _k.func.attr == "write"
                and isinstance(_k.func.value, _a2.Name)
                and _k.func.value.id in ("f", "file")):
            continue
        for _x in _a2.walk(_k):
            if isinstance(_x, _a2.Call) and isinstance(_x.func, _a2.Name) \
                    and _x.func.id in _MARK:
                _in_file.append("%s %d" % (_piece, _k.lineno))
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
german = the_program.po_pairs(TEXTS_DE)
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
    for english, translation, _at in german:
        keys.update(word_parts(english))
        values.update(word_parts(translation))
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


_entries = [(_at, _key, _value) for _key, _value, _at in german]
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


_prints, _raw = 0, []
for _piece, _whole in TREES:
    _where = ratchet.owners(_whole)
    for _node in ast.walk(_whole):
        if not (isinstance(_node, ast.Call)
                and isinstance(_node.func, ast.Name)
                and _node.func.id == "print" and _node.args):
            continue
        _prints += 1
        if any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
               and n.func.id in ("T", "TN")
               for n in ast.walk(_node.args[0])):
            continue
        for _text in _shown(_node.args[0]):
            if _WORDY.search(_text):
                _raw.append(("%s prints %r"
                             % (_where.get(id(_node), "<module>"),
                                _text[:44]),
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

# ------------------------------------------- How a count picks a wording
# English and German want two wordings, Russian three, Arabic six,
# Japanese one. The rule is not in the program: a PO header carries its
# own, and the reader turns it into a tree once per language.
RU_RULE = ("nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && "
           "n%10<=4 && (n%100<12 || n%100>14) ? 1 : 2);")
AR_RULE = ("nplurals=6; plural=(n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : "
           "n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5);")
REAL_RULES = {"de": "nplurals=2; plural=(n != 1);",
              "fr": "nplurals=2; plural=(n > 1);",
              "ja": "nplurals=1; plural=0;",
              "ru": RU_RULE, "ar": AR_RULE}

_read = vpm.language.plural_rule("Plural-Forms: " + RU_RULE + "\nLast: x\n")
check("the rule is read out of a header, not off the last line",
      _read is not None and _read[0] == 3,
      "read %s, wanted three wordings" % (_read and _read[0],))

check("a header with no rule in it gives nothing back",
      vpm.language.plural_rule("Content-Type: text/plain\n") is None,
      "wanted nothing where the header says nothing")

check("a rule that cannot be read gives nothing back rather than falling "
      "over", vpm.language.plural_rule(
          "Plural-Forms: nplurals=2; plural=(n ? ? 1);") is None,
      "wanted nothing from an expression with a hole in it")

# Set by hand out of CLDR, never computed from the same formula: an
# expectation that comes out of what it checks proves nothing.
RU_WANT = {0: 2, 1: 0, 2: 1, 4: 1, 5: 2, 11: 2, 21: 0, 22: 1, 101: 0}
_ru = vpm.language.plural_rule("Plural-Forms: " + RU_RULE)
# `not _ru` first: where the rule was not read at all, Russian asks for
# nothing right, and this must say so rather than fall over on a None.
_wrong = [n for n, want in RU_WANT.items()
          if not _ru or _ru[1](n) != want]
check("Russian asks for the wording CLDR says, over nine counts",
      not _wrong, "wrong at %s" % (sorted(_wrong) or "none",))

_out = []
for _code, _text in sorted(REAL_RULES.items()):
    _how_many, _tree = vpm.language.plural_rule("Plural-Forms: " + _text)
    for _n in range(201):
        _i = _tree(_n)
        if not 0 <= _i < _how_many:
            _out.append("%s n=%d wants %d of %d" % (_code, _n, _i, _how_many))
check("no count from 0 to 200 asks for a wording that is not there",
      not _out, "%d outside, first %s" % (len(_out), _out[:1] or "none"))

_folder = tempfile.mkdtemp()
_po = os.path.join(_folder, "qa.po")
io.open(_po, "w", encoding="utf-8").write(
    'msgid ""\nmsgstr ""\n"Plural-Forms: %s\\n"\n\n'
    'msgid "%%d clip"\nmsgid_plural "%%d clips"\n'
    'msgstr[0] "one"\nmsgstr[1] "few"\nmsgstr[2] "many"\n\n'
    'msgid "Content"\nmsgstr "plain"\n' % RU_RULE)
_texts, _forms, _header = vpm.language.read_po(_po)
check("an entry with msgid_plural is read into its wordings, in order",
      _forms.get("%d clip") == ["one", "few", "many"],
      "read %s" % (_forms.get("%d clip"),))
check("a plural entry is no ordinary text, and the ordinary ones still "
      "arrive", "%d clip" not in _texts and _texts.get("Content") == "plain",
      "%d ordinary entries, plural among them: %s"
      % (len(_texts), "%d clip" in _texts))

_bare = os.path.join(_folder, "qb.po")
io.open(_bare, "w", encoding="utf-8").write(
    'msgid ""\nmsgstr ""\n"Content-Type: text/plain\\n"\n\n'
    'msgid "%d clip"\nmsgid_plural "%d clips"\n'
    'msgstr[0] "one"\nmsgstr[1] "many"\n')
check("wordings without a rule beside them leave the English one standing",
      vpm.language.plural_rule(vpm.language.read_po(_bare)[2]) is None,
      "a file with wordings and no rule must give no rule")
shutil.rmtree(_folder, ignore_errors=True)

# The one that has to stay true after the catalogues gain plurals: it
# forbids the half-done state, not the repair.
_halfway = [code for code, forms in vpm.language.PLURALS.items()
            if forms and code not in vpm.language.PLURAL_RULE]
check("every catalogue with plural wordings carries a rule as well",
      not _halfway, "wordings but no rule in %s" % (_halfway or "none",))

# Everything above reads rules; from here the shipped Russian catalogue
# itself is asked. A rule that is explained in a header and never used
# leaves a reader with one plural for 2, 5 and 21, and nothing above
# would say so: the rule reads fine, the wordings are simply not there.
RU_FORMS = 3          # what Russian has, written out, not read back

# Which of the three a count wants, out of CLDR and not out of the
# formula this checks: [0] where the count ends in 1 but not in 11,
# [1] where it ends in 2, 3 or 4 but not in 12 to 14, [2] the rest.
RU_ONE, RU_FEW, RU_MANY = (1, 21, 101), (2, 22), (5, 11)

# The nine counted things the Russian catalogue answers for: the two
# English wordings TN() is called with, then the three Russian ones.
# Written out as values -- an expectation computed from the catalogue
# would say that the file agrees with itself and nothing else. The last
# row says two of its three the same way, and that is Russian, not a
# slip: after "on" the count and the thing both stand in the
# prepositional, where two and five look alike.
RU_SAYS = [
    ('%s audio recording', '%s audio recordings',
     "%s звукозапись", "%s звукозаписи", "%s звукозаписей"),
    ('%s audio track', '%s audio tracks',
     "%s звуковая дорожка", "%s звуковые дорожки", "%s звуковых дорожек"),
    ('%s camera', '%s cameras',
     "%s камера", "%s камеры", "%s камер"),
    ('%s channel', '%s channels',
     "%s канал", "%s канала", "%s каналов"),
    ('%s clip', '%s clips',
     "%s клип", "%s клипа", "%s клипов"),
    ('%s file', '%s files',
     "%s файл", "%s файла", "%s файлов"),
    ('%s video file', '%s video files',
     "%s видеофайл", "%s видеофайла", "%s видеофайлов"),
    ('%s video track', '%s video tracks',
     "%s видеодорожка", "%s видеодорожки", "%s видеодорожек"),
    ('on %s camera', 'on %s cameras',
     "на %s камере", "на %s камерах", "на %s камерах"),
]

# Every English singular a count picks a wording for, read out of the
# program rather than listed here: one added tomorrow is then counted
# from the day it is written.
_counted = set()
# The plural wording beside each, so a count can be asked for below
# without the English pair being written out a second time here.
_counted_many = {}
for _name, _tree in TREES:
    for _node in ast.walk(_tree):
        if isinstance(_node, ast.Call) and isinstance(_node.func, ast.Name) \
                and _node.func.id == "TN" and len(_node.args) >= 3 \
                and isinstance(_node.args[1], ast.Constant):
            _counted.add(_node.args[1].value)
            if isinstance(_node.args[2], ast.Constant):
                _counted_many[_node.args[1].value] = _node.args[2].value

# A counted thing translated with a single msgstr is the state this
# whole section exists against: Russian then says "5 файл". Untouched
# wordings are passed over -- they come out English, which is a
# different decision -- so this forbids the half-done entry, never the
# thirty-one nobody has translated yet.
_thin = []
for _w in sorted(_counted):
    _forms = vpm.language.PLURALS.get("ru", {}).get(_w, ())
    if _w in vpm.CATALOGUE.get("ru", {}):
        _thin.append("%r: one wording, not %d" % (_w, RU_FORMS))
    elif _forms and len([f for f in _forms if f]) != RU_FORMS:
        _thin.append("%r: %d wordings, %d of them said"
                     % (_w, len(_forms), len([f for f in _forms if f])))
check("a counted wording Russian answers for carries all three forms",
      not _thin, "%d of %d counted wordings thin, first: %s"
      % (len(_thin), len(_counted), _thin[:2] or "none"))


def ru_at(counts, form):
    """Every Russian wording that is not the wanted one, as text."""
    out = []
    for row in RU_SAYS:
        for n in counts:
            got = vpm.TN(n, row[0], row[1])
            if got != row[2 + form]:
                out.append("%r at %d: %r, wanted %r"
                           % (row[0], n, got, row[2 + form]))
    return out


vpm.set_language("ru")
_ones = ru_at(RU_ONE, 0)
check("Russian at 1, 21 and 101 says the wording for a single thing",
      not _ones, "%d of %d wrong, first: %s"
      % (len(_ones), len(RU_ONE) * len(RU_SAYS), _ones[:2] or "none"))
_few = ru_at(RU_FEW, 1)
check("Russian at 2 and 22 says the wording for two to four",
      not _few, "%d of %d wrong, first: %s"
      % (len(_few), len(RU_FEW) * len(RU_SAYS), _few[:2] or "none"))
_many = ru_at(RU_MANY, 2)
check("Russian at 5 and 11 says the wording for many",
      not _many, "%d of %d wrong, first: %s"
      % (len(_many), len(RU_MANY) * len(RU_SAYS), _many[:2] or "none"))

# --------------------------------- Every language, not only Russian
# Everything above asks the Russian catalogue. Nothing above asks the
# other eight anything at all, and that is the hole a tenth language
# walks into: Arabic shipped a rule for six wordings and no wordings,
# so eight different counts came out as two. These four hold every
# language the program offers, present and future, so a catalogue
# cannot arrive half again.

# One count out of each of the six classes Arabic distinguishes, set
# out of CLDR and not read back from the header these check.
AR_SIX = (0, 1, 2, 3, 11, 100)
# French puts nought with the singular -- plural=(n > 1) -- where
# English puts it with the plural. No other language here does that.
FR_ZERO, FR_ONE, FR_TWO = 0, 1, 2

_speaks = [_c for _c in vpm.languages() if _c != vpm.SOURCE_LANG]

_ruleless = [_c for _c in _speaks if _c not in vpm.language.PLURAL_RULE]
check("every language the program offers carries a plural rule of its own",
      not _ruleless, "%d of %d without a rule: %s"
      % (len(_ruleless), len(_speaks), _ruleless or "none"))

# A counted thing standing in a catalogue as one ordinary text is the
# half-done state: the rule in the header is then never consulted, and
# the count falls back on the English two. Things nobody has translated
# are in neither place and are passed over -- they come out English,
# which is a different decision.
_bare = []
for _c in _speaks:
    _has_forms = vpm.language.PLURALS.get(_c, {})
    _plain = vpm.CATALOGUE.get(_c, {})
    for _w in sorted(_counted):
        if _w in _plain and _w not in _has_forms:
            _bare.append("%s %r" % (_c, _w))
check("a counted thing a catalogue answers for carries wordings, not one "
      "text", not _bare, "%d of %d language-and-thing pairs bare, first: %s"
      % (len(_bare), len(_speaks) * len(_counted), _bare[:2] or "none"))

_miscount = []
for _c in _speaks:
    _rule = vpm.language.PLURAL_RULE.get(_c)
    for _w, _forms in sorted(vpm.language.PLURALS.get(_c, {}).items()):
        _said = [_f for _f in _forms if _f]
        if _rule and len(_said) != _rule[0]:
            _miscount.append("%s %r: %d said, header counts %d"
                             % (_c, _w, len(_said), _rule[0]))
check("a catalogue says as many wordings as its own header counts",
      not _miscount, "%d entries off, first: %s"
      % (len(_miscount), _miscount[:2] or "none"))

# From here the two languages whose rule is not the English one are
# asked at the counts where they differ from it. An empty list of
# things is a fall, not a pass: that is the state this exists against.
vpm.set_language("ar")
_ar = sorted(set(_counted) & set(vpm.language.PLURALS.get("ar", {})))
_flat = []
for _w in _ar:
    _said = set(vpm.TN(_n, _w, _counted_many[_w]) for _n in AR_SIX)
    if len(_said) != len(AR_SIX):
        _flat.append("%r: %d of %d at %s"
                     % (_w, len(_said), len(AR_SIX), AR_SIX))
check("Arabic says a different thing at 0, 1, 2, 3, 11 and 100",
      bool(_ar) and not _flat,
      "%d of %d counted things flatter than %d, first: %s"
      % (len(_flat), len(_ar), len(AR_SIX), _flat[:2] or "none"))

vpm.set_language("fr")
_fr = sorted(set(_counted) & set(vpm.language.PLURALS.get("fr", {})))
_zero = []
for _w in _fr:
    _at = [vpm.TN(_n, _w, _counted_many[_w])
           for _n in (FR_ZERO, FR_ONE, FR_TWO)]
    if not (_at[0] == _at[1] != _at[2]):
        _zero.append("%r: 0 %r, 1 %r, 2 %r" % (_w, _at[0], _at[1], _at[2]))
check("French says at nought what it says at one, and not what it says at "
      "two", bool(_fr) and not _zero,
      "%d of %d counted things wrong at nought, first: %s"
      % (len(_zero), len(_fr), _zero[:2] or "none"))

# The one above cannot see the two forms exchanged: with plural=(n > 1)
# nought and one take the same form, so a swap keeps them equal and only
# moves which wording both of them say. So the wording at two is held
# against the ordinary entry the catalogue still carries for the English
# plural -- two roads to the same text, and a swap sends them apart.
_swapped = []
for _w in _fr:
    _plural = vpm.CATALOGUE.get("fr", {}).get(_counted_many[_w])
    if _plural is None:
        _swapped.append("%r: no ordinary entry for its plural" % (_w,))
        continue
    _said = vpm.TN(FR_TWO, _w, _counted_many[_w])
    if _said != _plural:
        _swapped.append("%r: at two %r, catalogue %r" % (_w, _said, _plural))
check("what French says at two is the wording its catalogue holds for the "
      "plural", bool(_fr) and not _swapped,
      "%d of %d wrong at two, first: %s"
      % (len(_swapped), len(_fr), _swapped[:2] or "none"))

# The suite runs under LANG=C, so hand the module back in English.
vpm.set_language("en")

print("\n%d checks in %.2f s" % (done, time.time() - began))
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
