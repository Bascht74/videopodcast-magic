# -*- coding: utf-8 -*-
"""Under Sync only no camera is worked out to be the wide shot.

Two cameras, a speaker on one of them. The sections: without Sync only
the camera nobody is on is the wide shot, in grey; under Sync only it
is none, and its Kind field shows its own Kind; a camera marked the wide
shot stays one; and a window over a Sync only project shows that camera
as Content, so the window hands Sync only in.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import the_program

os.environ["QT_QPA_PLATFORM"] = "offscreen"
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


GUEST = "/tmp/GuestCam_01011858_C003.mov"
WIDE = "/tmp/WideCam_01011855_C001.mov"
FILES = [(GUEST, "video"), (WIDE, "video")]
# The window's chooser holds a camera by its path.
TAKEN = {GUEST}


def asked(kind_of_wide, sync):
    """(wide shots, marked) and what WideCam's Kind field shows."""
    kinds = {GUEST: vpm.Value(vpm.TYPE_CONTENT),
             WIDE: vpm.Value(kind_of_wide)}
    wides, said = vpm.wide_cameras_of(FILES, kinds, {}, TAKEN, (),
                                      sync=sync)
    return wides, said, vpm.kind_on_show(kind_of_wide, WIDE, wides, said)


print("1. Cut by speaker: the camera nobody is on is the wide shot")
wides, said, shown = asked(vpm.TYPE_CONTENT, False)
check("without Sync only the camera nobody is on is the wide shot",
      wides == [WIDE] and not said
      and shown[0] == vpm.TYPE_WIDE and shown[2],
      "wide shots %s, marked %s, the field shows %r, wanted "
      "['/tmp/WideCam_01011855_C001.mov'], False and %r worked out"
      % (wides, said, shown, vpm.TYPE_WIDE))

print("\n2. Sync only: nobody is asked, so nobody is missing")
wides, said, shown = asked(vpm.TYPE_CONTENT, True)
check("under Sync only no camera is worked out to be the wide shot",
      wides == [] and not said,
      "wide shots %s, marked %s, wanted [] and False" % (wides, said))
check("and its Kind field shows its own Kind, with no grey reason",
      shown == (vpm.TYPE_CONTENT, "", False),
      "the field shows %r, wanted %r"
      % (shown, (vpm.TYPE_CONTENT, "", False)))

print("\n3. Sync only: a mark still makes one")
wides, said, shown = asked(vpm.TYPE_WIDE, True)
check("a camera marked the wide shot stays one under Sync only",
      wides == [WIDE] and said,
      "wide shots %s, marked %s, wanted ['/tmp/WideCam_01011855_C001.mov'] "
      "and True" % (wides, said))

print("\n4. The window over a Sync only project")


def material(folder):
    """One recording and two cameras, six seconds each."""
    made = {}
    for name, src in (("Room.wav", "sine=frequency=200:duration=6"),
                      ("A_cam.mov", None), ("W_cam.mov", None)):
        made[name] = os.path.join(folder, name)
        what = (["-f", "lavfi", "-i", src] if src else
                ["-f", "lavfi", "-i", "testsrc=size=160x90:rate=25:duration=6",
                 "-f", "lavfi", "-i", "sine=frequency=300:duration=6",
                 "-c:a", "aac", "-c:v", "libx264", "-preset", "ultrafast",
                 "-pix_fmt", "yuv420p", "-shortest"])
        subprocess.run(["ffmpeg", "-v", "error"] + what + ["-y", made[name]],
                       check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    return made


made = material(tempfile.mkdtemp(prefix="vpm_syncwide_"))
project = os.path.join(tempfile.mkdtemp(prefix="vpm_syncwide_p_"),
                       "videopodcast-magic_SyncWide.json")
# Guest on A_cam, nobody on W_cam: cut by speaker, W_cam is the wide shot.
with open(project, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "version": "test",
               "timeline": [], "preset": "", "production": "SyncWide",
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


def kinds_of(file_name):
    """Every Kind field of that camera, in every table that shows one."""
    said = "%s -- %s" % (vpm.T('Kind'), file_name)
    return [w for w in win().findChildren(QtWidgets.QComboBox)
            if w.accessibleName() == said]


def judge():
    """What W_cam's Kind fields show, in every table."""
    fields = kinds_of("W_cam.mov")
    check("the window came up with W_cam's Kind field", bool(fields),
          "no field named %r" % ("%s -- W_cam.mov" % vpm.T('Kind')))
    shown = [w.currentData() for w in fields]
    check("its Kind field shows Content, not a wide shot worked out",
          bool(shown) and all(v == vpm.TYPE_CONTENT for v in shown),
          "the fields show %r, wanted %r in each"
          % (shown, vpm.TYPE_CONTENT))


state = {"round": 0, "still": 0, "seen": None}


def step():
    """Open the project, wait for the Kind fields to stand still, judge."""
    state["round"] += 1
    if state["round"] == 1:
        win().show()
        win().resize(1400, 900)
        for b in win().findChildren(QtWidgets.QPushButton):
            if b.text().strip().startswith(vpm.T('Open project ...')[:8]):
                b.click()
                break
    now = [w.currentData() for w in kinds_of("W_cam.mov")] or None
    state["still"] = state["still"] + 1 if (
        now and now == state["seen"]) else 0
    state["seen"] = now
    if state["still"] < 5 and state["round"] < 240:
        QtCore.QTimer.singleShot(200, step)
        return
    judge()
    app.quit()


def deadline():
    """An outer brake only: the waiting inside is on the fields."""
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
