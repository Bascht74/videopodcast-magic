# -*- coding: utf-8 -*-
"""The title bar names the open project's file after a rename too.

A project is opened, and its file name stands in the title bar. Then
the production is renamed in its field, and the project file follows
the new name -- so the title bar has to name the new file. Sections:
a file named otherwise than its production, opened and renamed, which
moves nothing, so the bar names it throughout; then one named after
it, opened and renamed. Read off the window's own title, offscreen.
"""
import json
import os
import shutil
import sys
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
vpm.say_dialog = lambda *a, **k: True     # no dialog waits for anybody

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


folder = tempfile.mkdtemp(prefix="vpm_title_")
run_folder = os.path.join(folder, "Run")
os.makedirs(run_folder)
SOUND = os.path.join(folder, "Presenter_01.wav")
with wave.open(SOUND, "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(48000)
    t = np.arange(4 * 48000) / 48000.0
    f.writeframes((0.3 * np.sin(2 * np.pi * 300 * t) * 32767)
                  .astype("<i2").tobytes())
OPENED = vpm.PROJECT_PREFIX + "Episode.json"
RENAMED = vpm.PROJECT_PREFIX + "Renamed.json"
PROJECT = os.path.join(run_folder, OPENED)
# Named otherwise than its production, in a folder of its own.
OTHER_NAME = vpm.PROJECT_PREFIX + "Other.json"
other_folder = os.path.join(folder, "Other")
os.makedirs(other_folder)
OTHER = os.path.join(other_folder, OTHER_NAME)
for path, out in ((PROJECT, run_folder), (OTHER, other_folder)):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"format": vpm.FILE_FORMAT, "version": "test",
                   "timeline": [], "preset": "", "production": "Episode",
                   "multitrack": False, "project_type": "cut",
                   "out_folder": out, "assignment": {},
                   "files": [{"path": SOUND, "kind": "audio"}]}, f)
chosen = [OTHER]
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (chosen[0], ""))
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


def name_field():
    """The production's name field, found by the name it speaks as."""
    for w in win().findChildren(QtWidgets.QLineEdit):
        if w.accessibleName() == vpm.T('Production name'):
            return w
    return None


state = {"step": 0, "rounds": 0, "over": False}


def title():
    """What the title bar says now; empty while there is no window."""
    return win().windowTitle() if win() else ""


def open_project():
    """Press "Open project ..."; the dialog answers with chosen[0]."""
    for b in win().findChildren(QtWidgets.QPushButton):
        if b.text().strip().startswith(vpm.T('Open project ...')[:8]):
            b.click()
            return


def opened(wanted, heading, what):
    """Wait for the name field to say Episode, then judge the title."""
    field = name_field()
    if state["rounds"] < 100 and (field is None
                                  or field.text() != "Episode"):
        return False
    print(heading)
    check(what, title().startswith(wanted),
          "the title reads %r, wanted it to begin with %r"
          % (title(), wanted))
    if field is not None:
        field.setText("Renamed")
    return True


def step():
    """Open, rename, judge: the file named otherwise first, then the other."""
    state["rounds"] += 1
    s = state["step"]
    if s == 0:
        if win() is None:
            QtCore.QTimer.singleShot(200, step)
            return
        win().show()
        open_project()
    elif s == 1:
        if not opened(OTHER_NAME, "1. A project file named otherwise",
                      "opening it names the file that is on the disk"):
            QtCore.QTimer.singleShot(200, step)
            return
    elif s == 2:
        # The rename is heard at once; a few rounds for anything late.
        if state["rounds"] < 5:
            QtCore.QTimer.singleShot(200, step)
            return
        check("renamed, it still names the file, which nothing moved",
              title().startswith(OTHER_NAME)
              and os.listdir(other_folder) == [OTHER_NAME],
              "the title reads %r, wanted it to begin with %r; the folder "
              "holds %s" % (title(), OTHER_NAME,
                            sorted(os.listdir(other_folder))))
        chosen[0] = PROJECT
        open_project()
    elif s == 3:
        if not opened(OPENED, "\n2. A project file named after it",
                      "opening a project names its file in the title bar"):
            QtCore.QTimer.singleShot(200, step)
            return
    else:
        if state["rounds"] < 100 and not title().startswith(RENAMED):
            QtCore.QTimer.singleShot(200, step)
            return
        check("the title bar names the file the rename moved it to",
              title().startswith(RENAMED),
              "the title reads %r after %d rounds of 200 ms, wanted it to "
              "begin with %r; the folder holds %s"
              % (title(), state["rounds"], RENAMED,
                 sorted(os.listdir(run_folder))))
        state["over"] = True
        app.quit()
        return
    state["step"], state["rounds"] = s + 1, 0
    QtCore.QTimer.singleShot(200, step)


def deadline():
    """An outer brake only: the waiting inside is on rounds of 200 ms."""
    if not state["over"]:
        bad.append("the pass never finished: 120 s gone, at step %d"
                   % state["step"])
        app.quit()


QtCore.QTimer.singleShot(300, step)
QtCore.QTimer.singleShot(120000, deadline)
try:
    vpm.gui()
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("the window never came up: gui() fell over")

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
