# -*- coding: utf-8 -*-
"""A file that fits nothing is still marked after the project is reopened.

The measurement names the file, the file list says beside it that it
does not fit and what became of it, and the project file keeps the
axis so the minutes it took are not spent again. It kept the places
and not the verdict: a reopened project measured everything again or,
where the file had left the cameras, showed it plain. The project is
opened again twice: closed and opened in this session, where closing
used to leave the memory of what was asked about the axis standing,
so the same files never read the stored one; and in a second process,
as it is by somebody who comes back. Both times the measurement is
replaced first by one that finds nothing -- so a mark that stands can
only have come out of the file.

Sections: the mark stands once the axis is measured; the project file
carries the verdict; closed and opened again in this session, the mark
stands; and opened in a second process, it stands and nothing was
measured.
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
import time
import json
import wave
import subprocess
import tempfile
import the_program
import numpy as np

SCRIPT = the_program.SCRIPT
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
os.environ["VPM_NO_SPEAKER_SPLIT"] = "1"
os.environ.pop("AUPHONIC_TOKEN", None)
from PySide6 import QtCore, QtGui, QtWidgets

# The second half runs in a process of its own: --reopen <project> <file>.
REOPEN = sys.argv[1:2] == ["--reopen"]

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
app.setQuitOnLastWindowClosed(False)
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.update_offer = lambda *a, **k: None
vpm.say_dialog = lambda *a, **k: True     # no dialog waits for anybody
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


PATIENCE = 150.0       # the builder is nine times slower than this machine
POLL = 0.02
# The sentence the file list writes beside a file with no place, out of
# the catalogue: the one line of it that names the finding.
REFUSED = vpm.T('%s\n   does not fit the other files: sound not '
                'recognised, no timecode.\n   %s').splitlines()[1].strip()


# ------------------------------------------------------- reading the window
def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def button(word):
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().replace("&", "").strip().startswith(word):
            return w


def menu_action(text):
    for a in win().findChildren(QtGui.QAction):
        if a.text().replace("&", "").strip().startswith(text):
            return a


def name_field():
    """The production name: the only field 340 wide."""
    for w in win().findChildren(QtWidgets.QLineEdit):
        if w.width() == 340 or w.maximumWidth() == 340:
            return w


def file_list():
    """The list of chosen files, found by what a screen reader says of it."""
    for t in win().findChildren(QtWidgets.QTreeWidget):
        if t.accessibleName() == vpm.T('Chosen files'):
            return t


def row_for(path):
    """The item that stands for one file, or None."""
    tree = file_list()
    if tree is None:
        return None
    stack = [tree.topLevelItem(i) for i in range(tree.topLevelItemCount())]
    while stack:
        node = stack.pop(0)
        held = node.data(0, QtCore.Qt.UserRole)
        if held and os.path.abspath(path) in [os.path.abspath(p)
                                              for p in held]:
            return node
        stack += [node.child(i) for i in range(node.childCount())]
    return None


def row_text(path):
    node = row_for(path)
    return None if node is None else node.text(2)


def marked(path):
    return REFUSED in (row_text(path) or "")


def waited_for(condition, why):
    began_here = time.time()
    while time.time() - began_here < PATIENCE:
        app.processEvents()
        if condition():
            return round(time.time() - began_here, 1)
        time.sleep(POLL)
    print("      gave up after %.1f s waiting for %s" % (PATIENCE, why))
    return None


# ------------------------------------------- the second half: opened again
if REOPEN:
    project_path, jingle = sys.argv[2], sys.argv[3]
    measured = [0]

    def nothing_measured(paths, tc_of=None, HOP=5.0):
        """Stricter than the real one: it finds no axis at all."""
        measured[0] += 1
        return {}, ""

    vpm.measure_time_axis = nothing_measured
    QtWidgets.QFileDialog.getOpenFileName = staticmethod(
        lambda *a, **k: (project_path, ""))

    def reopen():
        win().show()
        app.processEvents()
        button("Open project").click()
        took = waited_for(lambda: marked(jingle),
                          "the mark on the file that fits nothing")
        # The last line is the answer; everything above is the program.
        print(json.dumps({"marked": took is not None, "after": took,
                          "measured": measured[0],
                          "row": row_text(jingle)}))
        app.quit()

    QtCore.QTimer.singleShot(700, reopen)
    QtCore.QTimer.singleShot(int(PATIENCE * 1000) + 20000, app.quit)
    sys.argv = ["videopodcast_magic.py"]
    vpm.gui()
    sys.exit(0)


# ------------------------------------------------------------- the material
RATE = 48000
CAM_LEN, JINGLE_LEN = 30.0, 4.0
FOLDER = tempfile.mkdtemp(prefix="vpm_marks_")
OUT = os.path.join(FOLDER, "Result")
os.makedirs(OUT)


def turns(seconds, seed):
    """Speech-like turns: noise in irregular pieces with pauses between."""
    rng = np.random.default_rng(seed)
    n = int(seconds * RATE)
    x = np.zeros(n)
    t = 0.2
    while t < seconds - 1.0:
        long_s = float(rng.uniform(0.25, 0.9))
        k, i0 = int(long_s * RATE), int(t * RATE)
        shape = np.hanning(k) if k > 2 else 1.0
        x[i0:i0 + k] = rng.normal(0, 0.25, k) * shape
        t += long_s + float(rng.uniform(0.2, 1.1))
    return x


def write(path, x):
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())


write(FOLDER + "/room.wav", turns(CAM_LEN + 10, 1))
# A jingle: music, loud all the way through, with no turns to align on.
t = np.arange(int(JINGLE_LEN * RATE)) / float(RATE)
music = 0.1 * (np.sin(2 * np.pi * 220 * t) + np.sin(2 * np.pi * 277 * t)
               + np.sin(2 * np.pi * 330 * t))
write(FOLDER + "/music.wav", music * (1.0 + 0.3 * np.sin(2 * np.pi * 2.0 * t)))
PICTURE = ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
           "-c:a", "pcm_s16le"]
command = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
           "smptebars=size=160x90:rate=25:duration=%.1f" % (CAM_LEN + 10),
           "-i", FOLDER + "/room.wav", "-i", FOLDER + "/music.wav"]
for name, from_s in (("WideCam_C001", 0.0), ("GuestCam_C002", 4.0)):
    command += ["-map", "0:v", "-map", "1:a", "-ss", "%.2f" % from_s,
                "-t", "%.2f" % CAM_LEN] + PICTURE + [FOLDER + "/%s.mov" % name]
command += ["-map", "0:v", "-map", "2:a", "-t", "%.2f" % JINGLE_LEN] \
    + PICTURE + [FOLDER + "/Jingle.mov"]
subprocess.run(command, check=True)
CAM_A, CAM_B = FOLDER + "/WideCam_C001.mov", FOLDER + "/GuestCam_C002.mov"
JINGLE = FOLDER + "/Jingle.mov"

QtWidgets.QFileDialog.getOpenFileNames = staticmethod(
    lambda *a, **k: ([CAM_A, CAM_B, JINGLE], ""))
QtWidgets.QFileDialog.getExistingDirectory = staticmethod(
    lambda *a, **k: OUT)


def project_files():
    return sorted(os.path.join(OUT, n) for n in os.listdir(OUT)
                  if n.startswith(vpm.PROJECT_PREFIX) and n.endswith(".json"))


# -------------------------------------------------------------- the drive
def drive():
    try:
        win().show()
        app.processEvents()
        print("1. The mark once the axis is measured")
        button("Add files").click()
        took = waited_for(lambda: marked(JINGLE),
                          "the mark on the file that fits nothing")
        check("the file that fits nothing is marked once the axis is "
              "measured", took is not None,
              "the row says %r after %s s" % (row_text(JINGLE), took))
        if took is None:
            return

        print("\n2. The project file carries the verdict")
        name_field().setText("Marks")
        app.processEvents()
        button("Output folder").click()
        app.processEvents()
        menu_action("Save project").trigger()
        app.processEvents()
        took = waited_for(lambda: project_files(), "the project file")
        if took is None:
            check("the project file names the file that fits nothing with "
                  "its verdict", False, "no project file under the output "
                  "folder after %.0f s" % PATIENCE)
            return
        written = json.load(open(project_files()[0], encoding="utf-8"))
        about = [e for e in written.get("timeline") or []
                 if os.path.abspath(e.get("path") or "")
                 == os.path.abspath(JINGLE)]
        check("the project file names the file that fits nothing with its "
              "verdict",
              len(about) == 1 and about[0].get("fit") in ("nowhere", "brief"),
              "the timeline says %s of it, among %d entries"
              % (about, len(written.get("timeline") or [])))

        print("\n3. Closed and opened again in this session")
        # From here on nothing is measured: a mark can then only come
        # out of the file. Closing empties the list first, or the row
        # marked above would still be there and read as the answer.
        measured_here = [0]

        def nothing_measured_here(paths, tc_of=None, HOP=5.0):
            measured_here[0] += 1
            return {}, ""

        vpm.measure_time_axis = nothing_measured_here
        QtWidgets.QFileDialog.getOpenFileName = staticmethod(
            lambda *a, **k: (project_files()[0], ""))
        menu_action("Close project").trigger()
        app.processEvents()
        took = waited_for(lambda: row_for(JINGLE) is None, "the list to empty")
        check("closing the project empties the list", took is not None,
              "the row of the file that fits nothing is %s after %.0f s"
              % ("gone" if row_for(JINGLE) is None else "still there",
                 PATIENCE))
        if took is None:
            return
        button("Open project").click()
        took = waited_for(lambda: marked(JINGLE),
                          "the mark after opening the project again")
        check("closed and opened again in one session, the stored axis is "
              "read and the mark stands", took is not None,
              "the row says %r after %s s; the stand-in measurement was "
              "called %d times" % (row_text(JINGLE), took, measured_here[0]))

        print("\n4. Opened again, in a process of its own")
        child = subprocess.run(
            [sys.executable, os.path.abspath(__file__), "--reopen",
             project_files()[0], JINGLE],
            cwd=HERE, env=dict(os.environ), capture_output=True, text=True,
            timeout=PATIENCE + 60)
        lines = child.stdout.strip().splitlines() or ["{}"]
        try:
            said = json.loads(lines[-1])
        except ValueError:
            said = {}
        check("opened again, the mark stands", said.get("marked") is True,
              "the second process said %r; its last lines: %s"
              % (said, [l[:80] for l in lines[-3:]]
                 + [l[:80] for l in child.stderr.strip().splitlines()[-2:]]))
        check("and nothing was measured again: the mark came out of the file",
              said.get("measured") == 0,
              "the stand-in measurement was called %r times"
              % (said.get("measured"),))
    except Exception:
        import traceback
        traceback.print_exc()
        bad.append("crash")
    finally:
        app.quit()


QtCore.QTimer.singleShot(700, drive)
QtCore.QTimer.singleShot(285000, app.quit)
sys.argv = ["videopodcast_magic.py"]
vpm.gui()
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
