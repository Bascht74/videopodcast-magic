# -*- coding: utf-8 -*-
"""Taking one block out of a recording, and putting it back."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, json, shutil, subprocess, sys, tempfile, wave
import numpy as np
os.environ["QT_QPA_PLATFORM"] = "offscreen"
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
folder = tempfile.mkdtemp(prefix="vpm_blockrm_")


def block(name, hz=300.0, seconds=4.0):
    path = os.path.join(folder, name)
    t = np.arange(int(seconds * RATE)) / float(RATE)
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes((0.4 * np.sin(2 * np.pi * hz * t) * 32767)
                      .astype("<i2").tobytes())
    return path


one, two, three = (block("REC0001.wav"), block("REC0002.wav"),
                   block("REC0003.wav"))
guest = block("Guest0001.wav", hz=700.0)
video = os.path.join(folder, "Cam.mov")
subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                "testsrc=size=160x90:rate=25:duration=4", "-f", "lavfi",
                "-i", "sine=frequency=300:duration=4", "-c:v", "libx264",
                "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a",
                "aac", "-shortest", "-y", video], check=True)
project = os.path.join(folder, "videopodcast-magic_Interview_2.json")
with open(project, "w", encoding="utf-8") as f:
    json.dump({"format": 3, "version": "test", "timeline": [], "call": [],
               "files": [{"path": p, "kind": "audio"}
                         for p in (one, two, three, guest)]
                        + [{"path": video, "kind": "video"}],
               "out_folder": os.path.join(folder, "Ergebnis"),
               "production": "Blocks", "multitrack": False,
               "assignment": {}, "preset": ""}, f)
os.makedirs(os.path.join(folder, "Ergebnis"), exist_ok=True)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (project, ""))
adding = [two]
QtWidgets.QFileDialog.getOpenFileNames = staticmethod(
    lambda *a, **k: (list(adding), ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok


def win():
    for x in app.topLevelWidgets():
        if x.windowTitle().startswith("Video Podcast"):
            return x


def tree():
    for w in win().findChildren(QtWidgets.QTreeWidget):
        if w.columnCount() >= 3:
            return w


def audio_rows():
    """The recordings under the AUDIO header, with their block rows."""
    t = tree()
    out = []
    root = t.invisibleRootItem()
    for i in range(root.childCount()):
        head = root.child(i)
        if head.text(0) != vpm.T('AUDIO'):
            continue
        for k in range(head.childCount()):
            row = head.child(k)
            blocks = [row.child(j).text(0).strip()
                      for j in range(row.childCount())
                      if row.child(j).data(0, QtCore.Qt.UserRole + 3)
                      == "block"]
            out.append((row.text(0).strip(), blocks, row))
    return out


def button(text):
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(text):
            return w


n = [0]
waited = [0]
was = [None]


def shape():
    """The list as it stands: every recording with its blocks.

    None while the window is not up yet.
    """
    if win() is None or tree() is None:
        return None
    return [(r[0], tuple(r[1])) for r in audio_rows()]


def about_to_change():
    """Remember the list, right before a click rebuilds it."""
    was[0] = shape()


def drop_a_recording():
    """Take the first row that is part of the recording out of the list."""
    for name, _blocks, row in audio_rows():
        if "REC" in name:
            tree().setCurrentItem(row)
            app.processEvents()
            about_to_change()
            button("Remove").click()
            return True
    return False


def step():
    # Every step below clicks something that builds the list anew, and
    # the step after it reads that list. So the wait is for the list to
    # look different from the way it stood before the click, not for a
    # fixed second and a half. Six fixed waits were nine of the ten
    # seconds this test took, and the list was ready long before any of
    # them was over. The limit is the more patient one of the two: ten
    # seconds per step instead of one and a half, so a rebuild that
    # really does take its time is still waited for.
    now = shape()
    if now is None or (was[0] is not None and now == was[0]):
        if waited[0] < 400:
            waited[0] += 1
            QtCore.QTimer.singleShot(25, step)
            return
    waited[0] = 0
    was[0] = None
    i = n[0]; n[0] += 1
    try:
        if i == 0:
            win().show(); win().resize(1300, 800); app.processEvents()
            about_to_change()
            button("Open project").click()
        elif i == 1:
            rows = audio_rows()
            print("   before:", [(r[0], r[1]) for r in rows])
            check("two recordings, one of them three blocks",
                  len(rows) == 2 and any(len(r[1]) == 3 for r in rows),
                  str([(r[0], len(r[1])) for r in rows]))
            long_row = [r for r in rows if len(r[1]) == 3][0]
            spot = None
            for j in range(long_row[2].childCount()):
                kid = long_row[2].child(j)
                if "REC0002" in kid.text(0):
                    spot = kid
            check("the middle block has a row of its own", spot is not None)
            tree().setCurrentItem(spot)
            app.processEvents()
            k = button("Remove")
            check("and Remove offers itself for it",
                  bool(k and k.isEnabled()))
            about_to_change()
            k.click()
        elif i == 2:
            rows = audio_rows()
            print("   after:", [(r[0], r[1]) for r in rows])
            names = " ".join(r[0] for r in rows)
            check("the block is gone from the list",
                  "REC0002" not in names
                  and not any("REC0002" in b for r in rows for b in r[1]),
                  names)
            check("the recording now has two blocks",
                  any(len(r[1]) == 2 for r in rows),
                  str([(r[0], len(r[1])) for r in rows]))
            about_to_change()
            button("Add files").click()
        elif i == 3:
            rows = audio_rows()
            print("   back:", [(r[0], r[1]) for r in rows])
            check("putting it back makes a recording of its own",
                  len(rows) == 3, str([(r[0], len(r[1])) for r in rows]))
            alone = [r for r in rows if "REC0002" in r[0]]
            check("it stands there by itself", len(alone) == 1
                  and len(alone[0][1]) <= 1, str(alone))
            check("and the others are still two blocks",
                  any(len(r[1]) == 2 for r in rows),
                  str([(r[0], len(r[1])) for r in rows]))
            # Now the whole recording goes, single block and all. One
            # per step: removing rebuilds the list, and the rows of the
            # old one are gone with it.
            drop_a_recording()
        elif i == 4:
            drop_a_recording()
        elif i == 5:
            rows = audio_rows()
            check("with the recording gone only the guest is left",
                  len(rows) == 1, str([r[0] for r in rows]))
            adding[:] = [one, two, three]
            about_to_change()
            button("Add files").click()
        elif i == 6:
            rows = audio_rows()
            print("   all back:", [(r[0], len(r[1])) for r in rows])
            check("all three back means one recording again",
                  len(rows) == 2 and any(len(r[1]) == 3 for r in rows),
                  str([(r[0], len(r[1])) for r in rows]))
            print("\n%s" % ("ALL OK" if not error
                            else "FAIL: " + ", ".join(error)))
            app.quit(); return
    except Exception:
        import traceback; traceback.print_exc(); app.quit(); return
    QtCore.QTimer.singleShot(25, step)

QtCore.QTimer.singleShot(0, step)
QtCore.QTimer.singleShot(120000, app.quit)
sys.argv = ["videopodcast-magic.py"]
vpm.gui()
shutil.rmtree(folder, ignore_errors=True)
sys.exit(1 if error else 0)
