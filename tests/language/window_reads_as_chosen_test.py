# -*- coding: utf-8 -*-
"""The window is laid out the way the chosen language reads.

Arabic, Persian, Hebrew and Urdu are the languages on offer that read
from right to left, and the table is asked that first; then the real
window is started twice, in Arabic and in English, and each run is read
for its last word, for a traceback -- a fault in a Qt slot ends a run on a nought -- and for
the direction of the window and of the Settings sheet. Then the labels
each run printed are counted and laid out again here, and read for the
order the eye meets them in: a seek button says "-10 s" and not
"s 10-", a loudness target keeps its number in front -- in the list
and in the preflight's line, which is laid out here too -- a signed
number in a line of the log pane keeps its sign in front of it, read
off the pane's own line direction, and in Arabic every line of that
pane reads right to left, stands against the right edge and keeps a
Latin name inside in its own order -- and a window that reads left to
right carries no direction mark at all -- which is what every other
language rests on.
"""
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import ast, os, re, shutil, subprocess, sys, tempfile, time, types

sys.path.insert(0, HERE)
import the_program

# The window script is not part of this suite; it is only started here.
SHOT = os.path.join(HERE, "reading_shot.py")
# How long one window may take before it is called hung. It waits four
# times and no wait is a second long, so a window still here after two
# minutes never reached its event loop. The builder is about nine times
# slower than this machine, which is what the two minutes are for.
LIMIT = 120

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def readable(what):
    """What a timeout carried with it, as text."""
    if not what:
        return ""
    return what.decode("utf-8", "replace") if isinstance(what, bytes) else what


vpm = the_program.load()

print("1. Which language reads which way")
speaks = vpm.languages()
check("Arabic is among the languages the window offers", "ar" in speaks,
      "languages() gives %s -- %d of them" % (speaks, len(speaks)))
check("Arabic reads from right to left",
      vpm.language.reads_right_to_left("ar"),
      "reads_right_to_left('ar') gives %r"
      % vpm.language.reads_right_to_left("ar"))
# The three whose windows are not started below: the table alone decides
# their direction, so it is asked for each of them by name.
READ_LEFTWARD = ("ar", "fa", "he", "ur")
unturned = [c for c in ("fa", "he", "ur")
            if not vpm.language.reads_right_to_left(c)]
check("Persian, Hebrew and Urdu read from right to left", not unturned,
      "%d of 3 say no: %s" % (len(unturned), unturned or "none"))
# The other way round, which is the direction that bites: a table that
# says yes to everything would leave every check above green and turn
# every window in the program round.
mirrored = [c for c in speaks
            if c not in READ_LEFTWARD and vpm.language.reads_right_to_left(c)]
check("no language on offer beyond those four reads from right to left",
      not mirrored, "%d of the %d offered say yes as well: %s"
      % (len(mirrored), len(speaks), mirrored or "none"))

print("\n2. The window itself, started twice")
# Both at once, because each sits on timers between its steps and they
# would otherwise add up. Every run gets a runtime folder of its own:
# Qt puts lock files and shared memory under the one they would share.
started = []
for code in ("ar", "en"):
    shots = tempfile.mkdtemp(prefix="vpm_reading_")
    alone = tempfile.mkdtemp(prefix="vpm_runtime_")
    os.chmod(alone, 0o700)
    # LANGUAGE and not LANG: the program reads that name first, and the
    # suite has set it to en for every test in the run.
    env = dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE=code,
               QT_QPA_PLATFORM="offscreen", PYTHONUNBUFFERED="1",
               VPM_SHOTS=shots, XDG_RUNTIME_DIR=alone)
    started.append((code, subprocess.Popen(
        [sys.executable, SHOT], stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True, env=env, cwd=HERE),
        shots, alone))

runs = {}
for code, p, shots, alone in started:
    late = ""
    try:
        out = p.communicate(timeout=LIMIT)[0] or ""
    except subprocess.TimeoutExpired as ran_on:
        # A window that never comes up must not hold the suite, and it
        # must not pass either. What it printed before it got stuck is
        # the only trace there is, so it is read here and judged below.
        p.kill()
        late = "still here after %d s" % LIMIT
        try:
            out = p.communicate(timeout=10)[0] or ""
        except subprocess.TimeoutExpired as still_open:
            out = readable(still_open.stdout) or readable(ran_on.stdout)
    runs[code] = (out, late)
    shutil.rmtree(shots, ignore_errors=True)
    shutil.rmtree(alone, ignore_errors=True)


def said(code, word):
    """What that run printed after *word*, or "" where it said nothing."""
    found = re.search(r"^%s (\S+)$" % word, runs[code][0], re.M)
    return found.group(1) if found else ""


def broke(code):
    """The line the first traceback of that run ends on, or "".

    The line under the indented block, which is the fault itself. The
    last line of the whole output is no use: a fault inside a Qt slot
    leaves the loop running, and the run goes on to its last word.
    """
    lines = runs[code][0].split("\n")
    for i, line in enumerate(lines):
        if line.startswith("Traceback"):
            for after in lines[i + 1:]:
                if after.strip() and not after.startswith((" ", "\t")):
                    return after[:90]
            return "a traceback with nothing under it"
    return ""


# Before anything is read out of a run: did the run happen? Otherwise
# the lines below say the window was not turned round while in truth no
# window was ever built.
check("the Arabic window ran through to its last word",
      "done" in runs["ar"][0] and not runs["ar"][1],
      "last word said: %s; %s; %d lines printed"
      % ("done" in runs["ar"][0], runs["ar"][1] or "came back by itself",
         len(runs["ar"][0].split("\n"))))
check("the English window ran through to its last word",
      "done" in runs["en"][0] and not runs["en"][1],
      "last word said: %s; %s; %d lines printed"
      % ("done" in runs["en"][0], runs["en"][1] or "came back by itself",
         len(runs["en"][0].split("\n"))))
# Read off the output and not off the return code: a fault inside a Qt
# slot leaves the event loop running and the run ends on a nought, so
# the traceback in the pipe is the only thing that says it happened.
check("neither window run printed a traceback",
      not broke("ar") and not broke("en"),
      "Arabic ended on %r, English on %r"
      % (broke("ar") or "nothing", broke("en") or "nothing"))

print("\n3. Arabic")
check("the window speaks Arabic when the system asks for Arabic",
      said("ar", "language") == "ar",
      "the run settled on %r, wanted 'ar'" % said("ar", "language"))
check("the window reads from right to left in Arabic",
      said("ar", "window") == "right",
      "the window reads %r, wanted 'right'; the application reads %r"
      % (said("ar", "window"), said("ar", "app")))
check("the Settings sheet reads from right to left in Arabic",
      said("ar", "dialog") == "right",
      "Settings reads %r, wanted 'right'" % said("ar", "dialog"))

print("\n4. And taken back again")
check("the window reads from left to right in English",
      said("en", "window") == "left",
      "the window reads %r, wanted 'left'; the application reads %r"
      % (said("en", "window"), said("en", "app")))

print("\n5. What a label carrying a number reads like")
# Qt comes up here too, offscreen and after both windows are done with.
# Laying a label out is the only way to learn what order the eye meets
# it in; reading the string forwards says nothing, because the two
# directions of Unicode move characters and not bytes.
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtGui, QtWidgets

reader = QtWidgets.QApplication(sys.argv[:1])
# The marks that settle a reading. They have no picture and no width,
# so they come out of the order again: what is compared is what is
# read, not where a mark was put.
MARKS = "\u2066\u2067\u2068\u2069\u200e\u200f"
# A seek button is a sign, a number and a unit; a loudness target is a
# negative number in LUFS. Neither wording is translated -- they are
# units -- so the shape finds them in every language.
SEEK = re.compile(r"^[-+]\d+ [sF]$")
LOUD = re.compile(r"^(-\d+ LUFS )\(")


def bare(text):
    """The label without the marks that carry no picture."""
    return "".join(c for c in text if c not in MARKS)


def labels_of(code):
    """Every label that run printed, as the window held it."""
    out = []
    for line in runs[code][0].split("\n"):
        if line.startswith("label "):
            try:
                out.append(ast.literal_eval(line[len("label "):]))
            except (SyntaxError, ValueError):
                pass
    return out


def order(text, way=QtCore.Qt.RightToLeft):
    """The characters of *text* as the eye meets them, in a *way* line.

    Read off the glyphs Qt lays out, so the answer comes from the same
    two-directional engine that draws the window, and not from a second
    one written here. A character carrying no glyph of its own keeps
    the place of the one before it, so nothing drops out silently.
    """
    layout = QtGui.QTextLayout(text)
    option = QtGui.QTextOption()
    option.setTextDirection(way)
    layout.setTextOption(option)
    layout.beginLayout()
    line = layout.createLine()
    line.setLineWidth(100000)
    layout.endLayout()
    at, last = [], 0.0
    for i, sign in enumerate(text):
        seen = [p.x() for r in line.glyphRuns(i, 1) for p in r.positions()]
        at.append((min(seen) if seen else None, sign))
    placed = []
    for x, sign in at:
        placed.append((last if x is None else x, sign))
        if x is not None:
            last = x
    placed.sort(key=lambda p: p[0])
    return "".join(s for _x, s in placed if s not in MARKS)


seek = [x for x in labels_of("ar") if SEEK.match(bare(x))]
loud = [x for x in labels_of("ar") if LOUD.match(bare(x))]
# Before anything is read out of them: were they there? An empty list
# passes every judgement below, and the line would then say the labels
# read well while in truth the window put none up.
check("the Arabic window put up the seek buttons and the loudness targets",
      len(seek) == 12 and len(loud) == 4,
      "%d seek buttons and %d loudness targets out of %d labels"
      % (len(seek), len(loud), len(labels_of("ar"))))

wrong = [(bare(x), order(x)) for x in seek if order(x) != bare(x)]
check("every seek button in Arabic reads the way it is written",
      not wrong,
      "%d of %d turned round, first %s"
      % (len(wrong), len(seek),
         "%r reads %r" % wrong[0] if wrong else "none"))

# The bracket carries Arabic, which reads from right to left inside it
# and should. What must not move is the number in front of it.
astray = [(bare(x), order(x)) for x in loud
          if not order(x).startswith(LOUD.match(bare(x)).group(1))]
check("every loudness target in Arabic keeps its number in front",
      not astray,
      "%d of %d lost it, first %s"
      % (len(astray), len(loud),
         "%r reads %r" % astray[0] if astray else "none"))

# The same target as the preflight reports it: a line of its own, with
# and without the bracket, and inside a sentence where it does nothing.
vpm.set_language("ar")
told, lost = 0, []
for lufs, videos, alone, front in ((-16.0, ("a",), False, "-16 LUFS"),
                                   (-18.0, ("a",), False, "-18 LUFS"),
                                   (-16.0, (), True, "-16 LUFS")):
    for found in vpm.check_loudness_target(types.SimpleNamespace(
            lufs=lufs, multitrack=alone, auphonic_key=None), videos):
        told += 1
        if front not in order(found.text):
            lost.append((bare(found.text), order(found.text)))
check("the preflight's loudness line in Arabic keeps its number in front",
      told == 3 and not lost,
      "%d of 3 lines reported, %d lost it, first %s"
      % (told, len(lost), "%r reads %r" % lost[0] if lost else "none"))

# A signed number in a line of the log, which number_text() writes. Each
# line is read the way the pane lays it out, whichever way that is.
reader.setLayoutDirection(QtCore.Qt.RightToLeft)
pane = vpm.make_log_view(QtGui, QtWidgets, QtGui.QTextCursor)()
N = vpm.number_text
logged = [(vpm.hush_reason(2, [None, ("floor", -78.0)]), N(-78, 0)),
          (vpm.T('  Common level:      %s LUFS, the median of the voices')
           % N(-19.4, 1), N(-19.4, 1)),
          (vpm.T('    %-20s shifted by %s ms%s')
           % ("Presenter", N(-40.0, 1, plus=True), ""), N(-40.0, 1, True)),
          (vpm.T('  -->  aligned, clock drift %s ppm taken out')
           % N(12.5, 1, plus=True), N(12.5, 1, True))]
for text, _number in logged:
    pane.append_text(text + "\n")
ways, behind = [], []
block = pane.document().begin()
while block.isValid() and len(ways) < len(logged):
    if block.text().strip():
        text, number = logged[len(ways)]
        ways.append(block.textDirection())
        if bare(number) not in order(block.text(), ways[-1]):
            behind.append((bare(number), order(block.text(), ways[-1])))
    block = block.next()
vpm.set_language("en")
check("a signed number in an Arabic log line keeps its sign in front",
      len(ways) == len(logged) and not behind,
      "%d of %d lines in the pane, %d lost it, first %s"
      % (len(ways), len(logged), len(behind),
         "%r reads %r" % behind[0] if behind else "none"))

# The pane itself: every line reads the language's way whatever letter
# opens it -- a track name opens one of them -- and stands against
# the right edge, and a Latin name inside keeps its own order.
pane.resize(900, 300)
pane.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
pane.show()
reader.processEvents()
edge = pane.viewport().width()
lines, turned, leftish, named = 0, [], [], None
block = pane.document().begin()
while block.isValid():
    if block.text().strip():
        lines += 1
        if block.textDirection() != QtCore.Qt.RightToLeft:
            turned.append(bare(block.text()).strip()[:30])
        room = block.layout().lineAt(0).naturalTextRect()
        if room.left() <= edge - room.right():
            leftish.append("%r %.0f px from the left, %.0f from the right"
                           % (bare(block.text()).strip()[:20], room.left(),
                              edge - room.right()))
        if "Presenter" in block.text():
            named = order(block.text(), block.textDirection())
    block = block.next()
check("every line of the Arabic log pane reads right to left",
      lines == len(logged) and not turned,
      "%d of %d lines, %d of them left to right, first %r"
      % (lines, len(logged), len(turned), turned[0] if turned else "none"))
check("and stands against the right edge of the pane",
      lines == len(logged) and not leftish,
      "%d of %d lines nearer the left edge of %d px, first %s"
      % (len(leftish), lines, edge, leftish[0] if leftish else "none"))
check("a Latin name in an Arabic log line keeps its own order",
      named is not None and "Presenter" in named,
      "the line naming it reads %r" % named)

# The other way round, and it is the one that costs everybody else: a
# mark put in whatever the language would change every width and every
# comparison in the nine languages that never needed one.
marked = [x for x in labels_of("en") if bare(x) != x]
check("no label of an English window carries a direction mark",
      not marked and labels_of("en"),
      "%d of %d labels marked, first %r"
      % (len(marked), len(labels_of("en")),
         marked[0] if marked else "none"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
