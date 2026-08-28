# -*- coding: utf-8 -*-
"""The footer bar during a run: stages, weights, and the end reached."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtWidgets, QtCore
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
sys.path.insert(0, HERE)
from fixture_project import fixture_project
PROJECT, MEDIA = fixture_project("runbar")
if PROJECT is None:
    print("SKIPPED: no test project -- point VPM_MEDIA at a folder "
          "holding videopodcast-magic_Interview_2.json (looked in %s)" % MEDIA)
    sys.exit(0)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (PROJECT, ""))
# Offscreen nobody answers a dialog, and the run asks before it starts.
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted

error = []
def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

# ------------------------------------------------ what a run is made of
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
check("more cameras means more of the bar",
      dict((n, w) for n, w, _c in vpm.run_stages(True, 6, False))["cameras"]
      > weight["cameras"])
check("without auphonic the loudness is measured here",
      "loudness" in names and "auphonic" not in names)
check("with auphonic it is not",
      "auphonic" in [n for n, _w, _c in vpm.run_stages(True, 1, True)])
check("every stage says what it is",
      all(c for _n, _w, c in with_cams))

# ------------------------------------------------ the seam to the bar
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
check("its own report arrives", ("time base", 0.5) in seen)
check("what show_progress knows arrives", ("time base", 0.75) in seen)
check("and the shared bar of a parallel batch too",
      any(n == "time base" and s not in (None, 0.5, 0.75) for n, s in seen),
      str(seen))

# ------------------------------------------------ end to end
print("\n3. A dry run, watched from the footer")

def win():
    for x in app.topLevelWidgets():
        if x.windowTitle().startswith("Video Podcast"):
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
    # The tooltip counts as much as the text. A line too wide for its
    # field is shortened in the middle and keeps the whole of itself as
    # a tooltip, so on a narrow window the name of the stage is there
    # but no longer in text(). Measured 29.8.2026: this went red on
    # both Windows builders and nowhere else, because only there was
    # the field too narrow for the name.
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
            check("the dry run can be started", bool(k and k.isEnabled()))
            if not (k and k.isEnabled()):
                app.quit(); return
            # Only from here on is the bar the run's: what came before it
            # belongs to the measuring after the project was opened.
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
            print("\n%s" % ("ALL OK" if not error
                             else "FAIL: " + ", ".join(error)))
            app.quit(); return
    except Exception:
        import traceback; traceback.print_exc(); app.quit(); return
    QtCore.QTimer.singleShot(1000, step)

holder = {}

QtCore.QTimer.singleShot(600, step)
QtCore.QTimer.singleShot(180000, app.quit)
sys.argv = ["videopodcast-magic.py"]
vpm.gui()
sys.exit(1 if error else 0)
