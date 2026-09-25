# -*- coding: utf-8 -*-
"""A restart carries the work over, or says plainly that it will not.

The shot opens a production and presses the restart button three times:
first that it walked its whole way, to main() coming back and a return
code 0, held files, and was asked with all three answers. Cancelled,
nothing changes -- files, language, project file, the choice in the box
and the way to restart. Saved, the new window speaks the new language
with the same files, project, In, Out and sheets, the work is written
into the project file, and one window is on the screen. Not saved, it
comes up empty in the new language, and the project file is left
exactly as it lay.
"""
import os
import the_program
SCRIPT = the_program.SCRIPT
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
# The window script is not part of this suite; it is only started here.
SHOT = os.path.join(HERE, "carry_shot.py")
# What is waited for is what the shot reports, never a length of time:
# its line "main came back with ..." says the program's main() returned,
# and after it the process owes its end. The only clock is a standstill
# -- how long nothing at all changed in the shot's own folder: the
# report, the console, and the cache the window fills while it opens a
# project. Measured here 23.9.2026 over three runs: the longest stretch
# without a change 0.5 to 3.1 s; the builder is at most 12.6 times
# slower, so the bound below is never reached in the normal case.
STILL = 120.0           # seconds of nothing changing before it is hung
# A shot that hangs while it keeps writing never stands still, so the
# whole wait has a bound of its own too, under run.sh's 300 s: there the
# test is killed and this FAIL line is lost. Alone on the builder the
# test took 8 s, here 4.
LONGEST = 240.0         # seconds from the start, whatever still moves
LOOK = 0.25             # how often the folder is looked at

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


vpm = the_program.load()
vpm.set_language("en")
MEDIA = os.environ.get("VPM_MEDIA") or ""
PROJECT = os.path.join(MEDIA, "videopodcast-magic_Interview_2.json")
if not os.path.isfile(PROJECT):
    print("SKIPPED: no test project -- point VPM_MEDIA at a folder holding "
          "videopodcast-magic_Interview_2.json")
    raise SystemExit(0)

FOLDER = tempfile.mkdtemp(prefix="vpm_carries_")
# The home folder is fenced beside the settings folder, not instead of
# it: this shot really writes a chosen language down, and a guard that
# gave way would otherwise land in the settings of whoever started it.
OWN = os.path.join(FOLDER, "home")
os.makedirs(OWN)
REPORT = os.path.join(FOLDER, "report.txt")
# The shot's console goes into a file, never into a pipe read only at
# the end: a full pipe stops the writer, and the reader waits for it.
# Whether that is what made this test red on Windows beside the others
# is an open guess, not a finding. Measured here 23.9.2026 with the
# program's log rename refused, so its whole log goes to the console:
# about 4 KB before the first reading, 8 KB when "main came back" is
# written, 12 KB once the process has ended -- the log names the
# program's path, so a longer path gives more (12.4 KB at the end, from
# a refuter's copy). The builder's red line had all ten lines and no
# end, so the guess holds only for a pipe that fills in between, and
# only where the rename is refused -- neither is measured on Windows.
# The file cannot fill either way, and the FAIL line names what never
# came.
CONSOLE = os.path.join(FOLDER, "console.txt")
ENV = dict(os.environ, HOME=OWN, APPDATA=OWN, XDG_CONFIG_HOME=OWN,
           VPM_SETTINGS=OWN, VPM_CACHE=os.path.join(FOLDER, "cache"),
           QT_QPA_PLATFORM="offscreen", VPM_REBUILD_REPORT=REPORT)


def footprint():
    """Every file in the shot's folder with its size: what moves."""
    seen = []
    for root, _, names in os.walk(FOLDER):
        for name in names:
            try:
                seen.append((os.path.join(root, name),
                             os.path.getsize(os.path.join(root, name))))
            except OSError:
                pass        # written and gone between the two looks
    return sorted(seen)


def awaited(lines):
    """What the shot owed next, read off what it has reported so far."""
    if any(line.startswith("main came back with") for line in lines):
        return "the process ending after 'main came back'"
    if "done" in lines:
        return "the line 'main came back with ...' after 'done'"
    return "the shot's next line after %r" % (lines or ["nothing"])[-1][:60]


def shot_run():
    """Start the shot and wait on what it reports, not on the clock.

    The wait ends when the process is gone -- "ended" -- or when nothing
    in its folder has changed for STILL seconds, or after LONGEST
    seconds in all: then it is killed, and the reason names what never
    came and how long it was waited for. The process's return code
    comes back last.
    """
    with open(CONSOLE, "wb") as console:
        going = subprocess.Popen([sys.executable, SHOT], env=ENV, cwd=HERE,
                                 stdout=console, stderr=subprocess.STDOUT)
        started = time.time()
        mark, since = None, started
        while going.poll() is None:
            time.sleep(LOOK)
            now = footprint()
            if now != mark:
                mark, since = now, time.time()
            elif time.time() - since > STILL:
                return stopped(going, started,
                               "nothing in its folder changed for %.0f s"
                               % STILL)
            if time.time() - started > LONGEST:
                return stopped(going, started,
                               "its folder still moving, the last change "
                               "%.1f s before" % (time.time() - since))
    return lines_read(), console_tail(), "ended", going.returncode


def stopped(going, started, how):
    """Kill the shot and say what it owed, how long, and how it stood."""
    going.kill()
    going.wait()
    lines = lines_read()
    return lines, console_tail(), (
        "%s never came: %s, %.0f s after the start, the console %d bytes"
        % (awaited(lines), how, time.time() - started,
           os.path.getsize(CONSOLE))), going.returncode


def console_tail():
    with open(CONSOLE, encoding="utf-8", errors="replace") as f:
        return f.read()[-400:]


def unnamed(text):
    """The text with the home folder as ~ and a scratch folder <scratch>."""
    return re.sub(r"(/private)?/tmp/claude-\d+/[^/\s'\"]+", "<scratch>",
                  text.replace(os.path.expanduser("~"), "~"))


def plain(line):
    """A report line for the FAIL line, a traceback kept by its end.

    Of a BROKE traceback the last place and the exception's own line are
    kept: a head cut short keeps only 'File ...' and loses what went
    wrong.
    """
    line = unnamed(line)
    if not line.startswith("BROKE "):
        return line[:110]
    parts = [p.strip() for p in line.split(" | ") if p.strip()]
    places = [p for p in parts if p.startswith("File ")] or ["no place"]
    return "BROKE at %s: %s" % (places[-1][:160], parts[-1][:200])


def lines_read():
    if not os.path.exists(REPORT):
        return []
    with open(REPORT, encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f if line.strip()]


def seen(tag):
    """What the shot read at that point, as a dictionary."""
    for line in LINES:
        if line.startswith(tag + " {"):
            try:
                return json.loads(line[len(tag) + 1:])
            except ValueError:
                return {}
    return {}


def same(one, two, *fields):
    """The fields both readings agree on, and the ones they do not."""
    apart = [f for f in fields if one.get(f) != two.get(f)]
    return not apart, "; ".join(
        "%s %r against %r" % (f, one.get(f), two.get(f)) for f in apart)


LINES, PRINTED, WHY, CODE = shot_run()
BACK = [line for line in LINES if line.startswith("main came back with")]
WALKED = "done" in LINES and bool(BACK) and WHY == "ended" and CODE == 0
print("  the shot wrote %d lines and %s, return code %s"
      % (len(LINES), WHY, CODE))
if not WALKED and PRINTED:
    # Only where it did not end: the console of a window run holds
    # the locale note of every Qt on this machine, and run.sh reads
    # every line of a test's output.
    print("  what the shot printed: %r" % unnamed(PRINTED))

BEFORE, CANCELLED = seen("BEFORE"), seen("CANCELLED")
SAVED, READY, DROPPED = seen("SAVED"), seen("READY"), seen("DROPPED")
# The sheet names are not compared: they are the one thing a restart
# into another language is meant to change. How many stand is what has
# to hold, and that is judged on its own below.
CARRIED = ("rows", "project", "in", "out")

check("the shot walked its whole way", WALKED,
      "wanted 'done', 'main came back with ...' and return code 0, got "
      "'done' %s, %s, return code %s; %s -- %d lines, the last of them %s"
      % ("written" if "done" in LINES else "missing",
         repr(BACK[0][:60]) if BACK else "no 'main came back'", CODE, WHY,
         len(LINES), [plain(line) for line in (LINES or ["none"])[-3:]]))
check("the window really held a production before any of it",
      BEFORE.get("rows", 0) > 0 and bool(BEFORE.get("project"))
      and bool(BEFORE.get("in")),
      "rows %s, project %r, In %r"
      % (BEFORE.get("rows"), BEFORE.get("project"), BEFORE.get("in")))
check("a restart with files in the window asks before it does anything",
      len([x for x in LINES if x.startswith("question up with")]) == 3,
      "the question came up %d times, wanted 3"
      % len([x for x in LINES if x.startswith("question up with")]))
check("the question offers all three answers",
      len((([x for x in LINES if x.startswith("question up with")] or [""])[0]
           ).split("', '")) == 3,
      ([x for x in LINES if x.startswith("question up with")] or ["none"])[0])

# ------------------------------------------------------- cancel is cancel
check("cancelling leaves the window exactly as it was",
      *same(BEFORE, CANCELLED, *CARRIED))
check("cancelling leaves the language the window was speaking",
      BEFORE.get("language") == CANCELLED.get("language"),
      "spoke %r before, %r after" % (BEFORE.get("language"),
                                     CANCELLED.get("language")))
check("cancelling writes nothing into the project file",
      BEFORE.get("file") == CANCELLED.get("file"),
      "%s against %s" % (BEFORE.get("file"), CANCELLED.get("file")))
check("cancelling leaves the chosen language standing in the box",
      (CANCELLED.get("box") or [None, None])[0] is not None,
      "the box shows %r" % ((CANCELLED.get("box") or [None])[0],))
check("cancelling leaves the way to restart where it was",
      (CANCELLED.get("box") or [None, False])[1] is True,
      "the offer is up: %r" % ((CANCELLED.get("box") or [None, None])[1],))

# --------------------------------------------------------- saved and back
check("saved and restarted, the window speaks the language chosen",
      SAVED.get("language") not in (None, BEFORE.get("language")),
      "spoke %r before, %r after" % (BEFORE.get("language"),
                                     SAVED.get("language")))
check("saved and restarted, the files, project, In and Out all come back",
      *same(BEFORE, SAVED, *CARRIED))
check("saved and restarted, the same sheets stand, in the new language",
      len(SAVED.get("tabs") or []) == len(BEFORE.get("tabs") or [])
      and SAVED.get("tabs") != BEFORE.get("tabs"),
      "%s against %s" % (BEFORE.get("tabs"), SAVED.get("tabs")))
# The shot laid a production name of its own into the file before the
# first restart (the last field of each reading), because a save writes
# the very bytes the time axis wrote when it came: only the window's own
# name standing in its place shows that the save wrote.
check("saving really writes the work into the project file",
      bool((BEFORE.get("file") or [None] * 4)[3])
      and (SAVED.get("file") or [None] * 4)[3]
      not in (None, (BEFORE.get("file") or [None] * 4)[3]),
      "%s against %s" % (BEFORE.get("file"), SAVED.get("file")))
check("only one window is on the screen once the new one stands",
      SAVED.get("visible") == 1,
      "%s windows, %s of them on the screen"
      % (SAVED.get("windows"), SAVED.get("visible")))

# ---------------------------------------------------- not saved, and said
check("restarted without saving, the new window comes up empty",
      DROPPED.get("rows") == 0 and not DROPPED.get("project")
      and not DROPPED.get("in"),
      "rows %s, project %r, In %r" % (DROPPED.get("rows"),
                                      DROPPED.get("project"),
                                      DROPPED.get("in")))
check("restarted without saving, the project file is left as it lay",
      READY.get("file") == DROPPED.get("file") and bool(READY.get("file")),
      "%s against %s" % (READY.get("file"), DROPPED.get("file")))
check("restarted without saving, the language still changes",
      DROPPED.get("language") not in (None, READY.get("language")),
      "spoke %r before, %r after" % (READY.get("language"),
                                     DROPPED.get("language")))

shutil.rmtree(FOLDER, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
