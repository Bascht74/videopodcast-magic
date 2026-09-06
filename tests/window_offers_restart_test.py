# -*- coding: utf-8 -*-
"""The window offers to start again when another language is chosen.

The offer stands only on a real difference and goes when the choice
goes back; while a run is going it does nothing and says so where the
choice was made. Taken, main() builds a window that speaks the new
language and the old one leaves the screen. The sections in the order
the shot walks them: the offer at rest, after a change, on the way
back, under a run, and the window that comes of taking it.
"""
import os
import the_program
SCRIPT = the_program.SCRIPT
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
# The window script is not part of this suite; it is only started here.
SHOT = os.path.join(HERE, "language_shot.py")
# How long the shot may stand still before it is called hung. Standstill
# and not a deadline: the builder is about nine times slower than this
# machine, and a slow machine may take as long as it likes as long as it
# is still writing lines. The shot writes one at every step.
STILL = 90.0
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
STANDS = vpm.T('A language chosen here is spoken from the next start.')
RUNNING = vpm.T('The run is still going. The window can be started again '
                'once it is finished.')

FOLDER = tempfile.mkdtemp(prefix="vpm_restart_")
# The home folder is fenced with the settings folder, not instead of
# it: this shot really writes a chosen language down, and a guard that
# gave way would otherwise land in the settings of whoever started it.
OWN = os.path.join(FOLDER, "home")
os.makedirs(OWN)
REPORT = os.path.join(FOLDER, "report.txt")
ENV = dict(os.environ, HOME=OWN, APPDATA=OWN, XDG_CONFIG_HOME=OWN,
           VPM_SETTINGS=OWN, VPM_CACHE=os.path.join(FOLDER, "cache"),
           QT_QPA_PLATFORM="offscreen", VPM_REBUILD_REPORT=REPORT)


def shot_run():
    """Start the shot and wait on it writing, not on the clock.

    What comes back: the lines it wrote, whatever it printed, and the
    reason it stopped -- "ended", or "stood still" with the seconds.
    """
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


def said(word):
    """What the shot wrote after that word, or "" where it wrote none."""
    for line in LINES:
        if line.startswith(word + " "):
            return line[len(word) + 1:]
    return ""


LINES, PRINTED, WHY = shot_run()
print("  the shot wrote %d lines and %s" % (len(LINES), WHY))
if "done" not in LINES and PRINTED:
    # Only where it did not finish: the console of a window run holds
    # the locale note of every Qt on this machine, and run.sh reads
    # every line of a test's output.
    print("  what the shot printed: %r" % PRINTED)

check("the shot walked its whole way",
      "done" in LINES and WHY == "ended",
      "%s after %d lines, the last of them %s"
      % (WHY, len(LINES), [line[:110] for line in (LINES or ["nothing"])[-3:]]))
check("the settings window carries a way to start again",
      said("offer built") == "True",
      "the shot found the button: %r" % said("offer built"))
check("no way to start again stands there while the language stands",
      said("offer at rest visible") == "False",
      "visible at rest: %r, spoken %r, aimed at %r"
      % (said("offer at rest visible"), said("language at rest"),
         said("aiming at")))
check("the note at rest says the language comes at the next start",
      said("note at rest") == repr(STANDS),
      "it says %s" % (said("note at rest") or "nothing"))
check("choosing another language brings the way to start again up",
      said("offer after change visible") == "True",
      "visible after choosing %r: %r"
      % (said("aiming at"), said("offer after change visible")))
check("the note stops promising the next start once there is a way now",
      said("note after change") not in ("", repr(STANDS)),
      "it says %s" % (said("note after change") or "nothing"))
check("going back to the spoken language takes the way away again",
      said("offer after going back visible") == "False",
      "visible after going back: %r"
      % said("offer after going back visible"))
check("a run still going leaves the window where it is",
      said("windows while running") == "1 visible 1"
      and said("language while running") == said("language at rest"),
      "windows %r, spoken %r, at rest %r"
      % (said("windows while running"), said("language while running"),
         said("language at rest")))
check("a run still going is said where the choice was made",
      said("note while running") == repr(RUNNING),
      "it says %s" % (said("note while running") or "nothing"))
check("nothing is asked where nothing has been added to the window",
      said("question with nothing added") == "False",
      "a question stood there: %r"
      % (said("question with nothing added") or "nobody looked"))
check("taking the offer brings a window speaking the chosen language",
      said("language now") == said("aiming at") != "",
      "aimed at %r, the second window speaks %r"
      % (said("aiming at"), said("language now")))
check("only one window is on the screen once the new one stands",
      said("windows after").endswith("visible 1"),
      "after the rebuild: %r" % said("windows after"))
check("main hands back what the last window answered",
      said("main came back with") == "0",
      "main answered %r" % said("main came back with"))

shutil.rmtree(FOLDER, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
