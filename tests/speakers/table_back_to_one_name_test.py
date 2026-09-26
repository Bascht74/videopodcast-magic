# -*- coding: utf-8 -*-
"""Going back from several speakers to one name leaves a fresh layout.

One recording carries a separation of three named voices, two of them
on one camera and one on the other, so "several speakers" moves columns
of both tables: the recordings' and the cameras'. The window opens the
project and every column width is taken; "several speakers" is picked,
the voices are waited for, one name is typed, and the widths are asked
again. The window runs in a process of its own, so what the machine's
speech recogniser says stays out of this test's output.
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
import json
import subprocess
import tempfile
import time
import wave
import the_program

SCRIPT = the_program.SCRIPT

began = time.time()
done = 0
bad = []
FOUND = [("SPEAKER_00", [(1.0, 4.0), (9.0, 11.5)]),
         ("SPEAKER_01", [(5.0, 8.0)]),
         ("SPEAKER_02", [(8.2, 8.8)])]


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def material(folder):
    """One recording and two cameras, twelve seconds each."""
    import numpy as np
    sound = np.zeros(12 * 48000)
    rng = np.random.default_rng(11)
    for _key, parts in FOUND:
        for a, b in parts:
            n = int((b - a) * 48000)
            sound[int(a * 48000):int(a * 48000) + n] = rng.normal(0, 0.2, n)
    with wave.open(os.path.join(folder, "Room.wav"), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(48000)
        f.writeframes((np.clip(sound, -1, 1) * 32767)
                      .astype("<i2").tobytes())
    for name in ("A_camera.mov", "B_camera.mov"):
        subprocess.run(
            ["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
             "testsrc=size=160x90:rate=25:duration=12", "-f", "lavfi",
             "-i", "sine=frequency=300:duration=12", "-c:v", "libx264",
             "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac",
             "-shortest", "-y", os.path.join(folder, name)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def parent():
    """The material, one window, and its judgements carried up here."""
    global done
    media = tempfile.mkdtemp(prefix="vpm_back_")
    material(media)
    try:
        child = subprocess.run(
            [sys.executable, os.path.abspath(__file__)], cwd=HERE,
            env=dict(os.environ, VPM_BACK_MEDIA=media, LANG="C",
                     LC_ALL="C", LANGUAGE="en", PYTHONUNBUFFERED="1"),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            timeout=150)
        out, code = child.stdout, child.returncode
    except subprocess.TimeoutExpired as gone:
        out, code = str(gone.stdout or ""), "none, stopped after 150 s"
    said = ""
    for line in out.splitlines():
        # Its judgements and a traceback; the recogniser stays out.
        if line[61:63] == "ok" or line[61:65] == "FAIL" \
                or line.startswith(("Traceback", "  File ")):
            print(line[:220])
        said = line[6:] if line.startswith("FAIL: ") else said
        head = line.split(" checks in ")[0]
        if " checks in " in line and head.isdigit():
            done += int(head)
    if code != 0:
        bad.append("the window ended with %s: %s"
                   % (code, said or "no FAIL line"))
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


if not os.environ.get("VPM_BACK_MEDIA"):
    parent()

os.environ["QT_QPA_PLATFORM"] = "offscreen"
# The suite switches the separation off, and with it the choice of
# "several speakers"; every way into a separation is shut below instead.
os.environ.pop("VPM_NO_SPEAKER_SPLIT", None)
from PySide6 import QtCore, QtWidgets
from PySide6.QtTest import QTest

app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.update_offer = lambda *a, **k: None
vpm.fetch_model = lambda *a, **k: "not in a test"
vpm.speaker_split_available = lambda deep=False: True
vpm.speaker_split_run = lambda *a, **k: ([], "not in a test")
vpm.speaker_cache_read = lambda key: []
vpm.run_argv = lambda values, assignment_file_path="": (None, None, [])

media = os.environ["VPM_BACK_MEDIA"]
room = os.path.join(media, "Room.wav")
folder = tempfile.mkdtemp(prefix="vpm_back_p_")
stat = os.stat(room)
d = {"format": vpm.FILE_FORMAT, "version": "test", "timeline": [],
     "preset": "", "production": "Back", "multitrack": False,
     "out_folder": os.path.join(folder, "Result"),
     "files": [{"path": room, "kind": "audio"}]
     + [{"path": os.path.join(media, n), "kind": "video"}
        for n in ("A_camera.mov", "B_camera.mov")],
     "speakers": {"source": os.path.abspath(room),
                  "mtime": int(stat.st_mtime), "size": stat.st_size,
                  "model": vpm.SPEAKER_MODEL_NAME, "model_mark": "",
                  "num_speakers": 0,
                  "names": {"SPEAKER_00": "Anna", "SPEAKER_01": "Bo",
                            "SPEAKER_02": "Cem"},
                  "segments": [[k, a, b] for k, parts in FOUND
                               for a, b in parts]},
     "assignment": dict(
         ("voice:%s\n%s" % (os.path.abspath(room), key), camera)
         for key, camera in (("SPEAKER_00", "A_camera.mov"),
                             ("SPEAKER_01", "B_camera.mov"),
                             ("SPEAKER_02", "A_camera.mov")))}
project = os.path.join(folder, "videopodcast-magic_Back.json")
with open(project, "w", encoding="utf-8") as f:
    json.dump(d, f)
os.makedirs(d["out_folder"], exist_ok=True)
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


def name_field():
    """The recording's name field, or None while the sheet is not up."""
    said = "%s -- %s" % (vpm.T('Speaker name'), "Room.wav")
    for w in win().findChildren(QtWidgets.QComboBox):
        if w.accessibleName() == said and w.isVisible():
            return w
    return None


def tables():
    """The recordings' tree and the cameras' table on the sheet."""
    field = name_field()
    tree = field
    while tree is not None and not isinstance(tree, QtWidgets.QTreeView):
        tree = tree.parentWidget()
    cameras = [t for t in win().findChildren(QtWidgets.QTableWidget)
               if t.isVisible() and t.columnCount() == 5]
    return tree, (cameras[0] if cameras else None)


def voices():
    """How many rows hang under the recording."""
    tree, _cameras = tables()
    if tree is None:
        return -1
    return tree.model().rowCount(tree.model().index(0, 0))


def widths():
    """Every column width of both tables, the recordings' first."""
    tree, cameras = tables()
    if tree is None or cameras is None:
        return None
    return ([tree.columnWidth(c) for c in range(tree.model().columnCount())],
            [cameras.columnWidth(c) for c in range(cameras.columnCount())])


def to_sheet():
    """Bring the assignment sheet to the front."""
    for tw in win().findChildren(QtWidgets.QTabWidget):
        for k in range(tw.count()):
            if vpm.T('Assignment && time window')[:8].lower() \
                    in tw.tabText(k).lower():
                tw.setCurrentIndex(k)


state = {"turn": 0, "last": None, "still": 0, "stage": "open"}
seen = {}


def settled(ready):
    """True once *ready* holds and the widths stood still five turns."""
    now = widths() if ready else None
    state["still"] = state["still"] + 1 if (
        now is not None and now == state["last"]) else 0
    state["last"] = now
    return state["still"] >= 5


def step():
    """One turn of the plan: open, several, one name, judge."""
    state["turn"] += 1
    stage = state["stage"]
    if stage == "open" and state["turn"] == 1:
        win().show()
        win().resize(1400, 900)
        for b in win().findChildren(QtWidgets.QPushButton):
            if b.text().strip().startswith(vpm.T('Open project ...')[:8]):
                b.click()
                break
    to_sheet()
    ready = {"open": name_field() is not None,
             "several": voices() > 0,
             "back": name_field() is not None and voices() == 0}[stage]
    if not settled(ready) and state["turn"] < 200:
        QtCore.QTimer.singleShot(200, step)
        return
    seen[stage] = (widths(), voices())
    if stage == "open":
        check("the sheet came up with the recording's name field",
              seen["open"][0] is not None,
              "the name field of Room.wav %s after %d turns"
              % ("there" if seen["open"][0] else "missing", state["turn"]))
        if seen["open"][0] is None:
            app.quit()
            return
        QTest.keyClick(name_field(), QtCore.Qt.Key_Down)
    elif stage == "several":
        check("several speakers hung the voices under the recording",
              seen["several"][1] == len(FOUND),
              "%d rows under it, wanted %d" % (seen["several"][1],
                                              len(FOUND)))
        edit = name_field().lineEdit()
        QTest.keyClicks(edit, "Ida")
        QTest.keyClick(edit, QtCore.Qt.Key_Return)
    else:
        judge()
        app.quit()
        return
    state.update(stage={"open": "several", "several": "back"}[stage],
                 turn=1, last=None, still=0)
    QtCore.QTimer.singleShot(200, step)


def judge():
    """The widths after going back, held against the fresh build."""
    fresh, several, back = seen["open"][0], seen["several"][0], seen[
        "back"][0]
    check("one name again took the voices away",
          seen["back"][1] == 0,
          "%d rows still under the recording" % seen["back"][1])
    if back is None or several is None:
        bad.append("no widths to compare after going back")
        return
    check("the recordings' columns are as wide as in a fresh build",
          back[0] == fresh[0],
          "after going back %s, fresh %s, with several speakers %s"
          % (back[0], fresh[0], several[0]))
    check("the cameras' columns are as wide as in a fresh build",
          back[1] == fresh[1],
          "after going back %s, fresh %s, with several speakers %s"
          % (back[1], fresh[1], several[1]))


def deadline():
    """An outer brake only: the waiting inside is on the widths."""
    bad.append("the window never finished: 120 s gone, at %s turn %d"
               % (state["stage"], state["turn"]))
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
