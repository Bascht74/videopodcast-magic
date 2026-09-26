# -*- coding: utf-8 -*-
"""The window names the second of a pair '(2)' in its intro sentences.

Two cameras of one file name, the second set to the intro. Sections:
the camera table holds both and the second as the intro; the Intro
entry on the first camera's row names the holder as '(2)'; the second
in the player greys the In and Out buttons, and the hint beside them
names it '(2)'. What the two functions do with a label is held apart;
this asks whether the window hands the labels over at all.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import wave
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
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


folder = tempfile.mkdtemp(prefix="vpm_pairsaid_")
PAIR = []
for card in ("CardA", "CardB"):
    os.makedirs(os.path.join(folder, card))
    PAIR.append(os.path.join(folder, card, "C0003.MP4"))
    subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
         "testsrc=size=160x90:rate=25:duration=6", "-f", "lavfi",
         "-i", "sine=frequency=300:duration=6", "-c:a", "aac",
         "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
         "yuv420p", "-shortest", "-y", PAIR[-1]],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# One recording beside them: without it the sheet holds no camera table.
ROOM = os.path.join(folder, "Room.wav")
with wave.open(ROOM, "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(48000)
    f.writeframes((np.random.default_rng(3).normal(0, 0.1, 6 * 48000)
                   .clip(-1, 1) * 32767).astype("<i2").tobytes())
OUT = os.path.join(folder, "Result")
os.makedirs(OUT)
PROJECT = os.path.join(folder, "videopodcast-magic_Pair.json")
with open(PROJECT, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "version": "test",
               "timeline": [], "preset": "", "production": "Pair",
               "multitrack": False, "out_folder": OUT,
               "assignment": {"kind:" + PAIR[1]: vpm.TYPE_INTRO},
               "files": [{"path": ROOM, "kind": "audio"}]
               + [{"path": p, "kind": "video"} for p in PAIR]}, f)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (PROJECT, ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
_show = QtWidgets.QWidget.show


def offstage(self):
    """Shown for the layout, never on a screen."""
    self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
    _show(self)


QtWidgets.QWidget.show = offstage

# The second of the pair as the window names it, written out here.
SECOND = "C0003.MP4 (2)"
BARRED = vpm.T('%s is already set as %s, and an episode has one of those. '
               'Answer differently here, or take the mark off that file '
               'first.') % (SECOND, vpm.label_of(vpm.TYPE_INTRO))
AWAY_TEMPLATE = vpm.T(
    '%s is not on the axis of the episode: it is set in front of the '
    'material or after it, not cut into it. In point and Out point '
    'belong to what lies between.')
AWAY = AWAY_TEMPLATE % SECOND


def win():
    """The program's window."""
    for w in app.topLevelWidgets():
        if "Video Podcast Magic" in w.windowTitle():
            return w
    return None


def camera_table():
    """The table beside the player, one row per camera, or None."""
    for t in win().findChildren(QtWidgets.QTableWidget):
        head = t.horizontalHeaderItem(1)
        if head is not None and head.text() == vpm.T('new file name'):
            return t
    return None


def row_of(table, path):
    """The row a file stands in, off the whole path on its first cell."""
    for r in range(table.rowCount()):
        first = table.item(r, 0)
        if first is not None and first.toolTip() == path:
            return r
    return -1


def kind_box(table, path):
    """The Kind field on that file's row of the camera table, or None."""
    r = row_of(table, path)
    cell = table.cellWidget(r, 3) if r >= 0 else None
    boxes = cell.findChildren(QtWidgets.QComboBox) if cell else []
    return boxes[0] if boxes else None


def hint_line():
    """The line saying why In and Out are grey; "" where none stands.

    Found by the fixed tail of the sentence, so a wrong name still
    finds it and the judgement below reads what it says.
    """
    tail = AWAY_TEMPLATE.split("%s", 1)[1]
    for w in win().findChildren(QtWidgets.QLabel):
        if tail in w.text():
            return w.text()
    return ""


def button(caption):
    """A push button by its caption, or None."""
    for b in win().findChildren(QtWidgets.QPushButton):
        if b.text().strip() == caption:
            return b
    return None


state = {"round": 0, "phase": 0, "still": 0}


def open_project():
    """Press "Open project ..."; the dialog answers with PROJECT."""
    for b in win().findChildren(QtWidgets.QPushButton):
        if b.text().strip().startswith(vpm.T('Open project ...')[:8]):
            b.click()
            return


def settled():
    """Both rows there, the second's field on the intro, for five turns."""
    t = camera_table()
    second = kind_box(t, PAIR[1]) if t is not None else None
    ready = (t is not None and t.rowCount() == 2 and second is not None
             and second.currentData() == vpm.TYPE_INTRO)
    state["still"] = state["still"] + 1 if ready else 0
    return state["still"] >= 5


def judge_table():
    """The Intro entry on the first camera's row."""
    t = camera_table()
    print("1. The camera table")
    rows = t.rowCount() if t is not None else 0
    second = kind_box(t, PAIR[1]) if t is not None else None
    check("the camera table holds the pair, the second as the intro",
          rows == 2 and second is not None
          and second.currentData() == vpm.TYPE_INTRO,
          "%d rows, the second's field on %r after %d turns"
          % (rows, second.currentData() if second else None,
             state["round"]))
    print("\n2. The Intro entry on the first camera's row")
    first = kind_box(t, PAIR[0]) if t is not None else None
    at = first.findData(vpm.TYPE_INTRO) if first is not None else -1
    said = (first.itemData(at, QtCore.Qt.ToolTipRole) or "") \
        if at >= 0 else ""
    check("the intro entry names the holder as the window numbers it",
          said == BARRED, "the entry says %r, wanted %r" % (said, BARRED))
    if t is not None:
        t.selectRow(row_of(t, PAIR[1]))


def judge_player():
    """The second camera in the player, and the hint beside the buttons."""
    print("\n3. The second of the pair in the player")
    said = hint_line()
    mark_in = button(vpm.T('Mark In'))
    check("with the intro in the player the In and Out buttons are grey",
          bool(said) and mark_in is not None and not mark_in.isEnabled(),
          "hint %r, Mark In enabled %r, after %d turns"
          % (said, mark_in.isEnabled() if mark_in else None,
             state["round"]))
    check("the hint beside them names the file as the window numbers it",
          said == AWAY, "the hint says %r, wanted %r" % (said, AWAY))


def step():
    """Open the project, wait for the table, judge; then the player."""
    state["round"] += 1
    if state["round"] == 1 and not state["phase"]:
        win().show()
        win().resize(1400, 900)
        open_project()
    if not state["phase"]:
        if not settled() and state["round"] < 240:
            QtCore.QTimer.singleShot(200, step)
            return
        judge_table()
        state.update(phase=1, round=0)
        QtCore.QTimer.singleShot(200, step)
        return
    if not hint_line() and state["round"] < 100:
        QtCore.QTimer.singleShot(200, step)
        return
    judge_player()
    app.quit()


def deadline():
    """An outer brake only: the waiting inside is on the window."""
    bad.append("the window never finished: 240 s gone, phase %d turn %d"
               % (state["phase"], state["round"]))
    app.quit()


QtCore.QTimer.singleShot(300, step)
brake = QtCore.QTimer()
brake.setSingleShot(True)
brake.timeout.connect(deadline)
brake.start(240000)
try:
    vpm.gui()
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("the window never came up: gui() fell over")
brake.stop()

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
