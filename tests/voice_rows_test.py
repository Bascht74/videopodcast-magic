# -*- coding: utf-8 -*-
"""A separation stored in the project becomes rows in the window.

The model does not run here: the project file already carries what it
found. What is checked is the way from there to the screen -- a row per
voice with a name, a camera and something to listen to, a button per
recording for a speaker that was missed, and the line under the file
list saying where the separation stands. Nothing is computed again for
a project that is opened a second time; that is the point of storing
it.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, json, subprocess, sys, tempfile, wave
import numpy as np
os.environ["QT_QPA_PLATFORM"] = "offscreen"
# The suite switches the separation off so no test fetches 218 MB or
# computes for minutes. This test needs the way from a stored result
# to the screen, and nothing is measured again for one that is stored.
os.environ.pop("VPM_NO_SPEAKER_SPLIT", None)
from PySide6 import QtCore, QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""

error = []


def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


RATE = 48000
SEC = 12
folder = tempfile.mkdtemp(prefix="vpm_voices_")
rng = np.random.default_rng(11)
sound = np.zeros(SEC * RATE)
for a, b in ((1.0, 4.0), (5.0, 8.0), (9.0, 11.5)):
    n = int((b - a) * RATE)
    sound[int(a * RATE):int(a * RATE) + n] = rng.normal(0, 0.2, n)
recording = os.path.join(folder, "Room.wav")
with wave.open(recording, "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
    f.writeframes((np.clip(sound, -1, 1) * 32767).astype("<i2").tobytes())
video = os.path.join(folder, "A_camera.mov")
subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                "testsrc=size=160x90:rate=25:duration=%d" % SEC,
                "-f", "lavfi", "-i", "sine=frequency=300:duration=%d" % SEC,
                "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
                "yuv420p", "-c:a", "aac", "-shortest", "-y", video],
               check=True)

# What the separation found, as it would have been stored: raw, in the
# time of the recording itself, without the widened edges.
stat = os.stat(recording)
stored = {"source": os.path.abspath(recording), "mtime": int(stat.st_mtime),
          "size": stat.st_size, "model": vpm.SPEAKER_MODEL_NAME,
          "model_mark": "", "num_speakers": 0, "names": {},
          "segments": [["SPEAKER_00", 1.0, 4.0], ["SPEAKER_00", 9.0, 11.5],
                       ["SPEAKER_01", 5.0, 8.0]]}
project = os.path.join(folder, "videopodcast-magic_Voices.json")
with open(project, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "version": "test", "timeline": [],
               "call": [],
               "files": [{"path": recording, "kind": "audio"},
                         {"path": video, "kind": "video"}],
               "out_folder": os.path.join(folder, "Result"),
               "production": "Voices", "multitrack": True,
               "assignment": {}, "preset": "", "speakers": stored}, f)
os.makedirs(os.path.join(folder, "Result"), exist_ok=True)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (project, ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted


def win():
    for x in app.topLevelWidgets():
        if x.windowTitle().startswith("Video Podcast"):
            return x


def voice_table():
    """The table of voices: the one whose first heading is "Voice"."""
    for t in win().findChildren(QtWidgets.QTableWidget):
        head = t.horizontalHeaderItem(0)
        if head is not None and head.text() == "Voice":
            return t
    return None


def buttons(word):
    return [w for w in win().findChildren(QtWidgets.QPushButton)
            if word.lower() in w.text().lower()]


def labels(word):
    return [w for w in win().findChildren(QtWidgets.QLabel)
            if word.lower() in w.text().lower()]


def tab(word):
    for tw in win().findChildren(QtWidgets.QTabWidget):
        for k in range(tw.count()):
            if word.lower() in tw.tabText(k).lower():
                tw.setCurrentIndex(k)
                app.processEvents()
                return True
    return False


n = [0]
waited = [0]


def step():
    i = n[0]; n[0] += 1
    try:
        if i == 0:
            win().show(); win().resize(1400, 900); app.processEvents()
            for w in win().findChildren(QtWidgets.QPushButton):
                if w.text().strip().startswith("Open project"):
                    w.click()
        elif i == 1:
            tab("Assignment")
            table = voice_table()
            # Waiting for the table rather than for a number of
            # seconds: the assignment is built out of a thread and a
            # fixed pause would be wrong on both sides.
            if table is None and waited[0] < 120:
                waited[0] += 1
                n[0] = 1
                QtCore.QTimer.singleShot(250, step)
                return
            check("the stored separation became a table of voices",
                  table is not None)
            if table is None:
                app.quit(); return
            check("one row per voice", table.rowCount() == 2,
                  str(table.rowCount()))
            first = table.cellWidget(0, 1)
            check("the voice heard most is the first speaker",
                  first is not None and first.text() == "Speaker 1",
                  "" if first is None else first.text())
            check("every voice can be listened to",
                  all(table.cellWidget(r, 3) is not None
                      for r in range(table.rowCount())))
            check("and every voice carries a camera of its own",
                  all(isinstance(table.cellWidget(r, 2),
                                 QtWidgets.QComboBox)
                      for r in range(table.rowCount())))
            box = table.cellWidget(0, 2)
            check("the camera list holds the camera and the two "
                  "special cases", box.count() == 3, str(box.count()))
            check("one button per recording for a speaker that was missed",
                  len(buttons("One more speaker in")) == 1,
                  str([b.text() for b in buttons("One more speaker")]))
            check("the recordings are still one row each",
                  len(vpm_assign_rows()) == 1, str(vpm_assign_rows()))
            # Muted by VPM_SILENT; what is checked is that asking to
            # hear a voice does not bring the window down.
            table.cellWidget(0, 3).click()
            app.processEvents()
            check("asking to hear a voice leaves the window standing",
                  win() is not None and voice_table() is not None)
            n[0] = 2
            QtCore.QTimer.singleShot(0, step)
            return
        elif i == 2:
            tab("material")
            check("the line under the file list says what was found",
                  bool(labels("Separated:")),
                  str([x.text() for x in labels("Separated")]))
            check("and nothing is being computed",
                  not any(b.text() == "Break off" and b.isVisible()
                          for b in buttons("Break off")))
            print("\n%s" % ("ALL OK" if not error
                            else "FAIL: " + ", ".join(error)))
            app.quit(); return
    except Exception:
        import traceback
        traceback.print_exc()
        error.append("crash")
        app.quit(); return
    QtCore.QTimer.singleShot(400, step)


def vpm_assign_rows():
    """The first column of the upper assignment table."""
    for t in win().findChildren(QtWidgets.QTableWidget):
        head = t.horizontalHeaderItem(3)
        if head is None or head.text() != "Timecode":
            continue
        return [t.item(r, 0).text() if t.item(r, 0) else ""
                for r in range(t.rowCount())]
    return []


QtCore.QTimer.singleShot(300, step)
vpm.gui()
sys.exit(1 if error else 0)
