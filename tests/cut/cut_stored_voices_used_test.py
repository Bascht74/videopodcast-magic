# -*- coding: utf-8 -*-
"""A stored separation cuts by voice, alike from the line and the window.

On way_ground's production -- one recording, three cameras, a stored
separation with both voices named and seated -- a real run through each
door: the line the test writes, then the window's own Start, offscreen.
Per door: the run ends with a handover, every fixture turn lies in a
shot of its voice's camera, and the window does not ask the model. Then
the doors against each other: the same shots, EDLs and cut lists. Wide
edges are off at both; the limit: the plain path, not multitrack.
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

# The separation runs in the window, so the suite's switch for it goes:
# the model is stood in for below, and counting it means letting it be
# asked. A store of this test's own, so nothing stored elsewhere answers.
os.environ.pop("VPM_NO_SPEAKER_SPLIT", None)
STORE = tempfile.mkdtemp(prefix="vpm_way_store_")
os.environ["VPM_CACHE"] = STORE
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
asked = []


def model(path, count=0, **kw):
    """Stand in for the model, and note that it was asked."""
    asked.append((os.path.basename(path), count))
    return [], ""


vpm.speaker_split_run = model
vpm.speaker_split_available = lambda deep=False: True
vpm.SPEAKER_SPLIT_OFF = False
# Nothing is written down from speech: that would fetch a model, and
# no judgement here is about words.
vpm.words_at_hand = lambda *a, **k: []
vpm.recognise_speech = lambda *a, **k: ([], "")

# Where each turn of fixtures.sh lies on the Timeline: its seconds less
# 5.5, where the last camera rolls and the Timeline begins. The guest's
# first turn ends 0.5 s in, too short for a shot, and is left out.
PLACED = [("Presenter", 2.0, 7.0), ("Guest", 8.5, 14.5),
          ("Presenter", 16.0, 22.0), ("Guest", 23.5, 29.0),
          ("Presenter", 30.5, 36.0), ("Guest", 37.5, 42.5),
          ("Presenter", 44.0, 48.0), ("Guest", 49.5, 54.0)]


def astray(d):
    """The turns no shot of their voice's camera holds, as text."""
    cut = (d or {}).get("cut") or []
    out = []
    for who, a, b in PLACED:
        if not any(e.get("camera") == ground.SEAT[who]
                   and float(e["start"]) <= a and b <= float(e["end"])
                   for e in cut):
            out.append("%s %.1f-%.1f" % (who, a, b))
    return out


def shots(d):
    """The shots of a handover as (start, end, camera)."""
    return [(e.get("start"), e.get("end"), e.get("camera"))
            for e in (d or {}).get("cut") or []]


WORK = ground.own_folder("stored")

print("1. The command line, as a test writes it")
OUT_LINE = os.path.join(WORK, "line")
code, said, stuck = ground.line_run(
    ground.line(SCRIPT, ground.separation_file(vpm, WORK), OUT_LINE), STORE)
tail = [x.strip() for x in said.replace(WORK, "<work>").splitlines()
        if x.strip()][-3:]
by_line = ground.handover(OUT_LINE)
check("the line's run came back with 0 and wrote its handover",
      not stuck and code == 0 and by_line is not None,
      "return code %s%s, handover %s -- the log ends: %s"
      % (code, " after standing still" if stuck else "",
         "there" if by_line else "missing", " / ".join(tail)[-240:]))
check("at the line, every turn is on its voice's camera",
      by_line is not None and not astray(by_line),
      "%d of %d turns astray: %s -- the shots: %s"
      % (len(astray(by_line)), len(PLACED), astray(by_line),
         shots(by_line)))

print("\n2. The window, opened on the same production and started")
OUT_WINDOW = os.path.join(WORK, "window")
os.makedirs(OUT_WINDOW)
os.makedirs(os.path.join(WORK, "project"))
PROJECT = ground.project_file(vpm, os.path.join(WORK, "project"), OUT_WINDOW)
kept = ground.window_run(vpm, app, PROJECT, {})
by_window = ground.handover(OUT_WINDOW)
said = "".join(kept["log"]).replace(WORK, "<work>")
check("the window's Start ran a run to its end, with a handover",
      kept["ended"] and not kept["why"] and by_window is not None,
      "loop %s, %s, handover %s -- the log ends: %s"
      % ("came back" if kept["ended"] else "never came back",
         kept["why"] or "nothing given up",
         "there" if by_window else "missing",
         " / ".join(x.strip() for x in said.splitlines()
                    if x.strip())[-240:]))
check("the window did not ask the model a second time",
      asked == [], "the model was asked %d times: %s" % (len(asked), asked))
check("from the window, every turn is on its voice's camera",
      by_window is not None and not astray(by_window),
      "%d of %d turns astray: %s -- the shots: %s"
      % (len(astray(by_window)), len(PLACED), astray(by_window),
         shots(by_window)))

print("\n3. The two doors against each other")
check("the window cuts the same shots as the line",
      bool(shots(by_line)) and shots(by_window) == shots(by_line),
      "line %s -- window %s" % (shots(by_line), shots(by_window)))
line_files = ground.cut_files(OUT_LINE)
window_files = ground.cut_files(OUT_WINDOW)
differ = sorted(n for n in set(line_files) | set(window_files)
                if line_files.get(n) != window_files.get(n))
check("and writes the same EDLs and cut lists",
      len(line_files) >= 4 and not differ,
      "%d files from the line, %d from the window, differing: %s"
      % (len(line_files), len(window_files), differ or "none"))

shutil.rmtree(WORK, ignore_errors=True)
shutil.rmtree(STORE, ignore_errors=True)
stop()
