# -*- coding: utf-8 -*-
"""Under Sync only the camera table offers a camera its own file stem.

One window over a Sync only project whose recording still carries a
speaker name on a camera, in the columns Sync only hides. The sections:
the sheet comes up with the camera's name field; the speaker name stands
on that camera, hidden; the name the table offers is the camera's stem.
Offscreen, in Qt's own style; the naming rule itself is held by
table_sync_keeps_stem, this holds that the window hands Sync only in.
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
import json
import subprocess
import tempfile
import time
import wave
import the_program

os.environ["QT_QPA_PLATFORM"] = "offscreen"
import numpy as np
from PySide6 import QtCore, QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.update_offer = lambda *a, **k: None
vpm.run_argv = lambda values, assignment_file_path="": (None, None, [])

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def material(folder):
    """One recording and two cameras, twelve seconds each."""
    made = {"Room.wav": os.path.join(folder, "Room.wav")}
    sound = np.random.default_rng(3).normal(0, 0.1, 12 * 48000)
    with wave.open(made["Room.wav"], "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(48000)
        f.writeframes((np.clip(sound, -1, 1) * 32767).astype("<i2").tobytes())
    for name in ("A_cam.mov", "W_cam.mov"):
        made[name] = os.path.join(folder, name)
        subprocess.run(
            ["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
             "testsrc=size=160x90:rate=25:duration=12", "-f", "lavfi",
             "-i", "sine=frequency=300:duration=12", "-c:a", "aac",
             "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
             "yuv420p", "-shortest", "-y", made[name]],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return made


made = material(tempfile.mkdtemp(prefix="vpm_stem_"))
project = os.path.join(tempfile.mkdtemp(prefix="vpm_stem_p_"),
                       "videopodcast-magic_Stem.json")
# Guest on A_cam, kept from before the project became Sync only.
with open(project, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "version": "test",
               "timeline": [], "preset": "", "production": "Stem",
               "multitrack": False, "project_type": "sync",
               "out_folder": os.path.join(os.path.dirname(project),
                                          "Result"),
               "assignment": {
                   "audio:" + made["Room.wav"]: ["Guest", "A_cam.mov"]},
               "files": [{"path": made["Room.wav"], "kind": "audio"}]
               + [{"path": made[n], "kind": "video"}
                  for n in ("A_cam.mov", "W_cam.mov")]}, f)
os.makedirs(os.path.join(os.path.dirname(project), "Result"), exist_ok=True)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (project, ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
_show = QtWidgets.QWidget.show


def offstage(self):
    """Shown for the layout, never on a screen."""
    self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
    _show(self)


QtWidgets.QWidget.show = offstage


def win():
    """The program's window."""
    for w in app.topLevelWidgets():
        if "Video Podcast Magic" in w.windowTitle():
            return w
    return None


def field(what, file_name):
    """The field of that column in that file's row, shown or not."""
    said = "%s -- %s" % (vpm.T(what), file_name)
    for w in win().findChildren(QtWidgets.QWidget):
        if w.accessibleName() == said:
            return w
    return None


def judge():
    """The camera's offered name, beside the speaker Sync only hides."""
    offered = field('new file name', "A_cam.mov")
    name = field('Speaker name', "Room.wav")
    check("the sheet came up with the camera's name field",
          offered is not None and name is not None,
          "name field %s, speaker field %s"
          % (offered is not None, name is not None))
    if offered is None or name is None:
        return
    edit = getattr(name, "lineEdit", None)
    typed = (edit() if callable(edit) else name).text()
    trees = [t for t in win().findChildren(QtWidgets.QTreeView)
             if t.isAncestorOf(name)]
    hidden = bool(trees) and trees[0].isColumnHidden(1)
    # The file wrote the file name; opened, the answer is the path.
    on = getattr(field('belongs to', "Room.wav"), "currentData", str)()
    check("Guest stands on A_cam in a column Sync only hides",
          typed == "Guest" and on == made["A_cam.mov"] and hidden,
          "speaker field reads %r on %r, its column hidden %s"
          % (typed, os.path.basename(str(on)), hidden))
    check("the table offers the camera its own file stem",
          offered.text() == "A_cam",
          "offers %r, wanted 'A_cam'" % offered.text())


state = {"round": 0, "widths": None, "still": 0}


def to_sheet():
    """Bring the assignment sheet to the front."""
    for tw in win().findChildren(QtWidgets.QTabWidget):
        for k in range(tw.count()):
            if vpm.T('Assignment && time window')[:8].lower() \
                    in tw.tabText(k).lower():
                tw.setCurrentIndex(k)


def step():
    """Open the project, wait for the sheet to stand still, judge."""
    state["round"] += 1
    if state["round"] == 1:
        win().show()
        win().resize(1400, 900)
        for b in win().findChildren(QtWidgets.QPushButton):
            if b.text().strip().startswith(vpm.T('Open project ...')[:8]):
                b.click()
                break
    to_sheet()
    offered = field('new file name', "A_cam.mov")
    now = None if offered is None or not offered.isVisible() else [
        w.width() for w in win().findChildren(QtWidgets.QLineEdit)
        if w.isVisible()]
    # Settled: the field is there and the widths held for five turns.
    state["still"] = state["still"] + 1 if (
        now and now == state["widths"]) else 0
    state["widths"] = now
    if state["still"] < 5 and state["round"] < 240:
        QtCore.QTimer.singleShot(200, step)
        return
    judge()
    app.quit()


def deadline():
    """An outer brake only: the waiting inside is on the widths."""
    bad.append("the window never finished: 120 s gone, at turn %d"
               % state["round"])
    app.quit()


QtCore.QTimer.singleShot(300, step)
brake = QtCore.QTimer()
brake.setSingleShot(True)
brake.timeout.connect(deadline)
brake.start(120000)
try:
    vpm.gui()
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("the window never came up: gui() fell over")
brake.stop()

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
