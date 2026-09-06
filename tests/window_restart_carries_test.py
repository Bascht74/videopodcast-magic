# -*- coding: utf-8 -*-
"""A restart carries the work over, or says plainly that it will not.

With files in the window the restart asks first, and the answer decides:
saved, the new window comes back with the same files, project, In and
Out and the same sheets; not saved, it comes up empty and the project
file is left exactly as it lay; cancelled, nothing happens at all and
the choice stays where it was made. The sections follow the shot, which
presses the same button three times and answers it three ways.
"""
import os
import the_program
SCRIPT = the_program.SCRIPT
import json
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
# The window script is not part of this suite; it is only started here.
SHOT = os.path.join(HERE, "carry_shot.py")
# How long the shot may stand still before it is called hung. Standstill
# and not a deadline: the builder is about nine times slower than this
# machine, and a slow machine may take as long as it likes as long as it
# is still writing. The shot writes a line at every reading.
STILL = 120.0
LOOK = 0.25             # how often the report file is looked at

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
ENV = dict(os.environ, HOME=OWN, APPDATA=OWN, XDG_CONFIG_HOME=OWN,
           VPM_SETTINGS=OWN, VPM_CACHE=os.path.join(FOLDER, "cache"),
           QT_QPA_PLATFORM="offscreen", VPM_REBUILD_REPORT=REPORT)


def shot_run():
    """Start the shot and wait on it writing, not on the clock."""
    going = subprocess.Popen([sys.executable, SHOT], env=ENV, cwd=HERE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True)
    size, since = -1, time.time()
    while going.poll() is None:
        time.sleep(LOOK)
        now = os.path.getsize(REPORT) if os.path.exists(REPORT) else 0
        if now != size:
            size, since = now, time.time()
        elif time.time() - since > STILL:
            going.kill()
            going.wait()
            return lines_read(), "", "stood still %.0f s" % STILL
    return lines_read(), (going.stdout.read() or "")[-400:], "ended"


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


LINES, PRINTED, WHY = shot_run()
print("  the shot wrote %d lines and %s" % (len(LINES), WHY))
if "done" not in LINES and PRINTED:
    # Only where it did not finish: the console of a window run holds
    # the locale note of every Qt on this machine, and run.sh reads
    # every line of a test's output.
    print("  what the shot printed: %r" % PRINTED)

BEFORE, CANCELLED = seen("BEFORE"), seen("CANCELLED")
SAVED, READY, DROPPED = seen("SAVED"), seen("READY"), seen("DROPPED")
# The sheet names are not compared: they are the one thing a restart
# into another language is meant to change. How many stand is what has
# to hold, and that is judged on its own below.
CARRIED = ("rows", "project", "in", "out")

check("the shot walked its whole way",
      "done" in LINES and WHY == "ended",
      "%s after %d lines, the last of them %s"
      % (WHY, len(LINES), [line[:110] for line in (LINES or ["none"])[-3:]]))
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
check("saving really writes the work into the project file",
      bool(SAVED.get("file")) and SAVED.get("file") != BEFORE.get("file"),
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
