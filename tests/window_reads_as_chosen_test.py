# -*- coding: utf-8 -*-
"""The window is laid out the way the chosen language reads.

Arabic is the only language on offer that reads from right to left.
The table is asked first; then the real window is started twice, in
Arabic and in English, and each run is read for its last word, for a
traceback -- a fault in a Qt slot ends a run on a nought -- and for
the direction of the window and of the Settings sheet. Then the labels
each run printed are counted and laid out again here, and read for the
order the eye meets them in: a seek button says "-10 s" and not
"s 10-", a loudness target keeps its number in front, and a window
that reads left to right carries no direction mark at all -- which is
what every other language rests on.
"""
import ast, os, re, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
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
# The other way round, which is the direction that bites: a table that
# says yes to everything would leave every check above green and turn
# every window in the program round.
mirrored = [c for c in speaks
            if c != "ar" and vpm.language.reads_right_to_left(c)]
check("no other language on offer reads from right to left", not mirrored,
      "%d of the %d offered say yes as well: %s"
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


def order(text):
    """The characters of *text* as the eye meets them, right to left.

    Read off the glyphs Qt lays out, so the answer comes from the same
    two-directional engine that draws the window, and not from a second
    one written here. A character carrying no glyph of its own keeps
    the place of the one before it, so nothing drops out silently.
    """
    layout = QtGui.QTextLayout(text)
    option = QtGui.QTextOption()
    option.setTextDirection(QtCore.Qt.RightToLeft)
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
