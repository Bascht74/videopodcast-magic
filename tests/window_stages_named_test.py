# -*- coding: utf-8 -*-
"""The footer bar during a run: stages, weights, and the end reached."""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import sys, time
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtWidgets, QtCore
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
sys.path.insert(0, HERE)
from fixture_project import fixture_project
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


PROJECT, MEDIA = fixture_project("runbar")
if PROJECT is None:
    print("SKIPPED: no test project -- point VPM_MEDIA at a folder "
          "holding videopodcast-magic_Interview_2.json (looked in %s)" % MEDIA)
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (PROJECT, ""))
# Offscreen nobody answers a dialog, and the run asks before it starts.
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted

print("1. The stages of a run and what they are worth")
plain = vpm.run_stages(False, 0, False)
check("without cameras there is no camera work",
      not any("camera" in n for n, _w, _c in plain),
      str([n for n, _w, _c in plain]))
with_cams = vpm.run_stages(True, 3, False)
names = [n for n, _w, _c in with_cams]
check("with cameras there is", "cameras" in names, str(names))
weight = dict((n, w) for n, w, _c in with_cams)
check("writing the cameras is the largest single piece",
      weight["cameras"] == max(weight.values()), weight["cameras"])
six = dict((n, w) for n, w, _c in vpm.run_stages(True, 6, False))["cameras"]
check("more cameras means more of the bar", six > weight["cameras"],
      "six cameras weigh %s, three weigh %s" % (six, weight["cameras"]))
check("without auphonic the loudness is measured here",
      "loudness" in names and "auphonic" not in names,
      "%d stages, loudness among them %s, auphonic %s: %s"
      % (len(names), "loudness" in names, "auphonic" in names, names))
with_auphonic = [n for n, _w, _c in vpm.run_stages(True, 1, True)]
check("with auphonic it is not", "auphonic" in with_auphonic,
      "%d stages: %s" % (len(with_auphonic), with_auphonic))
check("every stage says what it is",
      all(c for _n, _w, c in with_cams),
      "%d of %d stages carry a caption; without one: %s"
      % (sum(1 for _n, _w, c in with_cams if c), len(with_cams),
         [n for n, _w, c in with_cams if not c]))

print("\n2. The run reaches the bar")
seen = []
vpm.PROGRESS_SINK = lambda name, share: seen.append((name, share))
vpm.step_begin("time base")
vpm.step_report(0.5)
vpm.show_progress("something", 0.75)
bar = vpm.SharedProgressBar("x", 2)
bar.stream = open(os.devnull, "w")
bar.report("a", 0.5)
vpm.PROGRESS_SINK = None
check("a stage beginning arrives", ("time base", None) in seen, str(seen[:2]))
check("its own report arrives", ("time base", 0.5) in seen,
      "%d reports arrived: %s" % (len(seen), seen[:4]))
check("what show_progress knows arrives", ("time base", 0.75) in seen,
      "%d reports arrived: %s" % (len(seen), seen[:4]))
check("and the shared bar of a parallel batch too",
      any(n == "time base" and s not in (None, 0.5, 0.75) for n, s in seen),
      str(seen))

print("\n3. A dry run, watched from the footer")

def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x

def bar_widget():
    """The footer bar, told apart by its range and not by its size."""
    for w in win().findChildren(QtWidgets.QProgressBar):
        if w.maximum() == 1000:
            return w

def button(text):
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(text):
            return w

STAGES = ('Reading the plan', 'Audio out of the cameras',
          'Common time axis', 'Loudness and levels', 'Who speaks when',
          'Writing the camera files', 'Handover and result')
watch = {"values": [], "captions": set(), "on": False, "was_up": False,
         "gone": False}

def look():
    if not watch["on"]:
        return
    b = bar_widget()
    if b is None:
        return
    if b.isVisible():
        watch["was_up"] = True
        watch["values"].append(b.value())
    elif watch["was_up"]:
        watch["gone"] = True
    # The tooltip counts as much as the text: a line too wide for its
    # field is shortened in the middle and keeps the whole of itself
    # only as a tooltip, so a narrow window has no name in text().
    stages = [vpm.T(x) for x in STAGES]
    for lb in win().findChildren(QtWidgets.QLabel):
        if not lb.isVisible():
            continue
        for said in (lb.text(), lb.toolTip()):
            if said in stages:
                watch["captions"].add(said)

n = [0]
waited = [0]

def step():
    i = n[0]; n[0] += 1
    try:
        if i == 0:
            win().show(); app.processEvents()
            clock = QtCore.QTimer(win())
            clock.timeout.connect(look)
            clock.start(100)
            holder["clock"] = clock
            button("Open project").click()
        elif i == 1:
            k = button("Dry run")
            if k is not None and not k.isEnabled() and waited[0] < 60:
                waited[0] += 1
                n[0] = 1
                QtCore.QTimer.singleShot(1000, step)
                return
            check("the dry run can be started", bool(k and k.isEnabled()),
                  "button found %s, ready %s, after %d s of waiting"
                  % (k is not None, bool(k and k.isEnabled()), waited[0]))
            if not (k and k.isEnabled()):
                app.quit(); return
            # Only from here on is the bar the run's, not the opening's.
            watch["on"] = True
            k.click()
        elif i >= 3 and (watch["gone"] or waited[0] + i > 100):
            holder["clock"].stop()
            values = watch["values"]
            check("the bar moved during the run", len(values) > 3, len(values))
            check("only ever forwards",
                  all(b >= a for a, b in zip(values, values[1:])),
                  str(values[:16]))
            check("and it got to the end", max(values or [0]) >= 1000,
                  max(values or [0]))
            # One is enough: a dry run writes nothing, so most stages
            # are skipped and the bar passes them in a single tick.
            check("it named a stage of the run by name",
                  len(watch["captions"]) >= 1,
                  str(sorted(watch["captions"])))
            app.quit(); return
    except Exception:
        import traceback; traceback.print_exc(); app.quit(); return
    QtCore.QTimer.singleShot(1000, step)

holder = {}

QtCore.QTimer.singleShot(600, step)
QtCore.QTimer.singleShot(180000, app.quit)
sys.argv = ["videopodcast_magic.py"]
vpm.gui()
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
