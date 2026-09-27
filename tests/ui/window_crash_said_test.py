# -*- coding: utf-8 -*-
"""A window run that breaks unexpectedly says so and gives Start back.

Plain path, the window's own Start; a fault planted in the mix step, one
the run has no answer for. The window names it, says "finished with
errors" and not done, and Start is back, Stop gone. Its traceback is
said to the log file, which is stood in for by one of this test's own,
and not in the window. The limit: one fault, in one place.
"""
PLATFORM_BOUND = True
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import shutil
import tempfile
import time
import the_program
import way_ground as ground

SCRIPT = the_program.SCRIPT
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stop():
    """Nothing further can be asked, so count what there is and go."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


if ground.missing():
    print("SKIPPED: " + ground.missing())
    stop()

STORE = tempfile.mkdtemp(prefix="vpm_crash_store_")
os.environ["VPM_CACHE"] = STORE
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.words_at_hand = lambda *a, **k: []
vpm.recognise_speech = lambda *a, **k: ([], "")

FAULT = "a fault nobody planned for"
real_ffmpeg = vpm.run_ffmpeg_with_progress


def broken(cmd, duration, text):
    """The program's ffmpeg step, which breaks on the full mix."""
    if os.path.basename(str(cmd[-1])).startswith("mix_full"):
        raise ValueError(FAULT)
    return real_ffmpeg(cmd, duration, text)


vpm.run_ffmpeg_with_progress = broken
# The log file stood in for: beside the program it would be shared with
# every test running alongside, and this one reads it back.
LOG = os.path.join(STORE, "window_crash.log")
vpm.logbook.log_path = lambda: LOG


def button(text):
    """The window's button whose text begins with *text*, or None."""
    for x in app.topLevelWidgets():
        if vpm.DISPLAY_NAME in x.windowTitle():
            for w in x.findChildren(QtWidgets.QPushButton):
                if w.text().strip().startswith(text):
                    return w


WORK = ground.own_folder("crash")
OUT = os.path.join(WORK, "out")
try:
    os.makedirs(OUT)
    os.makedirs(os.path.join(WORK, "project"))
    print("The plain path, broken in the mix")
    kept = ground.window_run(vpm, app, ground.project_file(
        vpm, os.path.join(WORK, "project"), OUT), {})
    text = "".join(kept["log"])
    tail = " / ".join(x.strip() for x in text.replace(OUT, "<out>")
                      .splitlines() if x.strip())[-240:]
    named = vpm.T('\nStopped: %s').strip() % FAULT
    check("the window names a fault the run did not expect",
          named in text,
          "'%s' %s; loop %s, %s; the log ends: %s"
          % (named, "said" if named in text else "missing",
             "back" if kept["ended"] else "never back",
             kept["why"] or "nothing given up", tail))
    errors = vpm.T('\nFinished with errors.\n').strip()
    finished = vpm.run_done_text(False).strip()
    check("a run that broke says it finished with errors, not done",
          errors in text and finished not in text,
          "'%s' %s, '%s' %s; the log ends: %s"
          % (errors, "said" if errors in text else "missing",
             finished[:40], "said" if finished in text else "not said",
             tail))
    try:
        with open(LOG, encoding="utf-8", errors="replace") as f:
            logged = f.read()
    except OSError:
        logged = ""
    trace = [x for x in logged.splitlines() if x.startswith("Traceback")]
    last = (logged.strip().splitlines() or ["the log is empty"])[-1]
    check("the log file holds the traceback of a fault the window said",
          bool(trace) and ("ValueError: " + FAULT) in logged,
          "%d traceback lines in %d log lines, its last %r"
          % (len(trace), len(logged.splitlines()), last[:120]))
    shown = [x for x in text.splitlines() if "Traceback" in x]
    check("and the window shows no traceback, only the one line",
          not shown, "%d traceback lines in the window, first %r"
          % (len(shown), (shown or [""])[0][:120]))
    start, halt = button(vpm.T("Start")), button(vpm.T("Stop"))
    check("Start is back and Stop gone after a run broke unexpectedly",
          start is not None and start.isEnabled()
          and (halt is None or halt.isHidden()),
          "Start %s, Stop %s"
          % ("missing" if start is None else
             "enabled" if start.isEnabled() else "disabled",
             "gone" if halt is None or halt.isHidden()
             else "still shown"))
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("the test itself broke off")

shutil.rmtree(WORK, ignore_errors=True)
shutil.rmtree(STORE, ignore_errors=True)
stop()
