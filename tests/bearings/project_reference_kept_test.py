# -*- coding: utf-8 -*-
"""A reopened project writes marks at the reference camera the run chose.

The run reads every timecode mark at its reference camera's rate: the
longest camera it heard. The window takes that camera from the
measurement; reopened, it measures nothing, so the camera has to come
out of the project file -- by the files alone it would be the longest
camera, here a silent one at 29.97 beside two heard ones at 25.

Sections: measured, the window marks at 25 and the project file names
the heard camera; opened again in a process of its own, marks are at 25
and nothing was measured; a project file written without the name
opens, and marks by the longest camera as before; and the file a run's
start writes again keeps the name.
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
from PySide6 import QtCore, QtGui, QtWidgets

# The second half runs in a process of its own: --reopen <project>.
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
# The heard cameras' rate, and the silent one's: written out here and
# not read off the files, so a reading gone wrong cannot agree with it.
HEARD_FPS = 25.0
SILENT_FPS = 30000.0 / 1001.0
# How long the rate has to hold still before it counts as the answer:
# the stored axis comes in on a thread, after the files are drawn.
STILL = 3.0


# ------------------------------------------------------- reading the window
def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def drawn(text):
    """What ends up on the screen: & marks a key, && draws one &."""
    return str(text).replace("&&", "\x00").replace("&", "") \
                    .replace("\x00", "&")


def button(word):
    for w in win().findChildren(QtWidgets.QPushButton):
        if drawn(w.text()).strip().startswith(word):
            return w


def menu_action(text):
    for a in win().findChildren(QtGui.QAction):
        if drawn(a.text()).strip().startswith(text):
            return a


def name_field():
    """The production name: the only field 340 wide."""
    for w in win().findChildren(QtWidgets.QLineEdit):
        if w.width() == 340 or w.maximumWidth() == 340:
            return w


def listed_files():
    """The files the list holds, found by what a screen reader says of it."""
    held = set()
    for t in win().findChildren(QtWidgets.QTreeWidget):
        if t.accessibleName() != vpm.T('Chosen files'):
            continue
        stack = [t.topLevelItem(i) for i in range(t.topLevelItemCount())]
        while stack:
            node = stack.pop(0)
            held.update(os.path.abspath(p) for p in
                        node.data(0, QtCore.Qt.UserRole) or ())
            stack += [node.child(i) for i in range(node.childCount())]
    return held


def marks_player():
    """The player the mark buttons sit in, found from the button.

    Looked for among all the widgets: before material arrives it is
    built but not yet put into the window.
    """
    for b in app.allWidgets():
        if isinstance(b, QtWidgets.QPushButton) \
                and drawn(b.text()).strip() == vpm.T('Mark In'):
            up = b.parentWidget()
            while up is not None and not hasattr(up, "spot_s"):
                up = up.parentWidget()
            return up
    return None


def marks_fps():
    """The rate the window writes a mark at, or None where it has none."""
    p = marks_player()
    rate = getattr(p, "marks_fps", None)
    try:
        return float(rate()) if rate else None
    except Exception:
        return None


def waited_for(condition, why):
    began_here = time.time()
    while time.time() - began_here < PATIENCE:
        app.processEvents()
        if condition():
            return round(time.time() - began_here, 1)
        time.sleep(POLL)
    print("      gave up after %.1f s waiting for %s" % (PATIENCE, why))
    return None


def settled_rate():
    """The marks' rate once it has held still for STILL seconds.

    It moves when the axis arrives and not after; the wait is on its
    standing still, not on its value, so either answer is judged.
    """
    began_here = time.time()
    last, since = marks_fps(), time.time()
    while time.time() - began_here < PATIENCE:
        app.processEvents()
        now = marks_fps()
        if now != last:
            last, since = now, time.time()
        elif now is not None and time.time() - since >= STILL:
            return now
        time.sleep(POLL)
    return last


# ------------------------------------------- the second half: opened again
if REOPEN:
    project_path = sys.argv[2]
    measured = [0]

    def nothing_measured(paths, tc_of=None, HOP=5.0, phase_of=None,
                         raw=None):
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
        rate = settled_rate()
        listed = len(listed_files())
        # The last line is the answer; everything above is the program.
        print(json.dumps({"fps": rate, "measured": measured[0],
                          "listed": listed}))
        app.quit()

    QtCore.QTimer.singleShot(700, reopen)
    QtCore.QTimer.singleShot(int(PATIENCE * 1000) + 20000, app.quit)
    sys.argv = ["videopodcast_magic.py"]
    vpm.gui()
    sys.exit(0)


# ------------------------------------------------------------- the material
RATE = 48000
FOLDER = tempfile.mkdtemp(prefix="vpm_reference_")
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


with wave.open(FOLDER + "/room.wav", "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(RATE)
    f.writeframes((np.clip(turns(45.0, 1), -1, 1) * 32000)
                  .astype("<i2").tobytes())
PICTURE = ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p"]
WIDE = FOLDER + "/WideCam_C001.mov"
GUEST = FOLDER + "/GuestCam_C002.mov"
# Silent, at 29.97, and longest of the three by its file: by the files
# alone it would be the reference, and the run never takes it.
SILENT = FOLDER + "/CoPresenterCam_C003.mov"
for path, from_s, long_s, clock in ((WIDE, 0.0, 34.0, "10:00:00:00"),
                                    (GUEST, 4.0, 30.0, "10:00:04:00")):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "smptebars=size=160x90:rate=25:duration=45",
                    "-i", FOLDER + "/room.wav", "-map", "0:v", "-map", "1:a",
                    "-ss", "%.2f" % from_s, "-t", "%.2f" % long_s]
                   + PICTURE + ["-c:a", "pcm_s16le", "-timecode", clock, path],
                   check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "testsrc=size=160x90:rate=30000/1001", "-t", "50"]
               + PICTURE + ["-timecode", "09:59:58:00", SILENT], check=True)

QtWidgets.QFileDialog.getOpenFileNames = staticmethod(
    lambda *a, **k: ([WIDE, GUEST, SILENT], ""))
QtWidgets.QFileDialog.getExistingDirectory = staticmethod(
    lambda *a, **k: OUT)


# The production is named "Reference" below; the older file written in
# section three lies beside it under a name of its own.
PROJECT = os.path.join(OUT, vpm.PROJECT_PREFIX + "Reference.json")


def stored():
    """The production's project file as it stands, or {}."""
    try:
        return json.load(open(PROJECT, encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def stored_reference():
    """The reference camera the project file names, as it stands, or None."""
    return stored().get("timeline_reference")


def same_file(a, b):
    """Whether two paths name one file, compared as the program compares.

    The file holds the program's key for a path, which on Windows is
    lower case and has its own separators; so both sides are normalised.
    """
    def norm(p):
        return os.path.normcase(os.path.normpath(os.path.abspath(p)))
    return bool(a) and bool(b) and norm(a) == norm(b)


def reopened(project):
    """Open *project* in a second process; what it answered, as a dict.

    With a store of its own: the window keeps a measured axis there as
    well, and an axis found there would answer for the project file.
    """
    store = tempfile.mkdtemp(prefix="vpm_reference_store_")
    child = subprocess.run(
        [sys.executable, os.path.abspath(__file__), "--reopen", project],
        cwd=HERE, env=dict(os.environ, VPM_CACHE=store),
        capture_output=True, text=True,
        timeout=PATIENCE + 60)
    lines = child.stdout.strip().splitlines() or ["{}"]
    try:
        said = json.loads(lines[-1])
    except ValueError:
        said = {}
    said["tail"] = ([l[:80] for l in lines[-3:]]
                    + [l[:80] for l in child.stderr.strip().splitlines()[-2:]])
    return said


# -------------------------------------------------------------- the drive
def drive():
    try:
        win().show()
        app.processEvents()
        print("1. Measured: the window marks at the heard cameras' rate")
        name_field().setText("Reference")
        app.processEvents()
        button("Output folder").click()
        app.processEvents()
        button("Add files").click()
        took = waited_for(lambda: stored().get("timeline"),
                          "the measured axis in the project file")
        check("the measured axis reaches the project file", took is not None,
              "no timeline in %s after %s s, at most %.0f; the folder "
              "holds %s" % (os.path.basename(PROJECT), took, PATIENCE,
                            os.listdir(OUT)))
        if took is None:
            return
        rate = settled_rate()
        check("measured, the window writes marks at the heard 25",
              rate is not None and abs(rate - HEARD_FPS) < 0.001,
              "marks at %r fps, the heard cameras run at %.3f, the silent "
              "one at %.3f" % (rate, HEARD_FPS, SILENT_FPS))
        check("the project file names the camera the run takes as reference",
              same_file(stored_reference(), WIDE),
              "timeline_reference names %r, the longest heard camera is %r"
              % (stored_reference(), WIDE))

        print("\n2. Opened again, in a process of its own")
        said = reopened(PROJECT)
        check("reopened, marks are written at the stored reference's 25",
              said.get("fps") is not None
              and abs(said["fps"] - HEARD_FPS) < 0.001,
              "marks at %r fps with the file naming %r; the silent camera "
              "runs at %.3f; last lines %s"
              % (said.get("fps"), stored_reference(), SILENT_FPS,
                 said["tail"]))
        check("and nothing was measured again: the reference came out of "
              "the file", said.get("measured") == 0,
              "the stand-in measurement was called %r times"
              % (said.get("measured"),))

        print("\n3. A project file written before the reference was kept")
        older = dict(stored())
        older.pop("timeline_reference", None)
        old_path = os.path.join(OUT, vpm.PROJECT_PREFIX + "Older.json")
        with open(old_path, "w", encoding="utf-8") as f:
            json.dump(dict(older, production="Older"), f)
        said = reopened(old_path)
        check("a project file without the reference camera still opens",
              said.get("listed") == 3,
              "%r files in the list after opening it, 3 in the file; last "
              "lines %s" % (said.get("listed"), said["tail"]))
        check("and marks go by the longest camera, as before: 29.97",
              said.get("fps") is not None
              and abs(said["fps"] - SILENT_FPS) < 0.001,
              "marks at %r fps, the longest camera runs at %.3f"
              % (said.get("fps"), SILENT_FPS))
    except Exception:
        import traceback
        traceback.print_exc()
        bad.append("crash")
    finally:
        app.quit()


def lifted(name):
    """The source of a nested function, dedented to the left margin."""
    lines = the_program.whole().split("\n")
    at = [i for i, x in enumerate(lines)
          if x.strip().startswith("def %s(" % name)]
    if not at:
        return ""
    room = len(lines[at[0]]) - len(lines[at[0]].lstrip())
    out = [lines[at[0]][room:]]
    for x in lines[at[0] + 1:]:
        if x.strip() and len(x) - len(x.lstrip()) <= room:
            break
        out.append(x[room:])
    return "\n".join(out)


def rewritten_at_start():
    """Section four: the file a run's start writes over the measured one.

    project_write sits inside make_project_file() and is reached only by
    a run, so its own body is cut out of the source and run for real,
    handed the project file the window wrote as what stood there before.
    """
    print("\n4. A run's start writes the file again")
    before = stored()
    path = os.path.join(FOLDER, "rewritten.json")
    body = lifted("project_write")
    around = {"project_move": lambda: None,
              "axis_file": lambda: path,
              "project_collect": lambda p: dict(before),
              "settings_extend": lambda d: None,
              "FILE_FORMAT": vpm.FILE_FORMAT, "VERSION": vpm.VERSION,
              "model": type("Production", (), {"files": [
                  (WIDE, "video"), (GUEST, "video"), (SILENT, "video")]}),
              "state": {"axis_absolute": True}, "json": json,
              "write": lambda text: None, "as_head": lambda text: text,
              "T": vpm.T}
    if body:
        exec(compile(body, "project_write", "exec"), around)
        around["project_write"]()
    try:
        after = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        after = {}
    named = after.get("timeline_reference")
    check("a run's start writes the file again and keeps the reference",
          same_file(named, WIDE),
          "timeline_reference names %r after the rewrite, %r before, the "
          "longest heard camera is %r; project_write %s"
          % (named, stored_reference(), WIDE,
             "lifted" if body else "not found"))


QtCore.QTimer.singleShot(700, drive)
QtCore.QTimer.singleShot(285000, app.quit)
sys.argv = ["videopodcast_magic.py"]
vpm.gui()
if "crash" not in bad:
    rewritten_at_start()
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
