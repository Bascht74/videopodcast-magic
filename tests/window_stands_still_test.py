# -*- coding: utf-8 -*-
"""Left alone, the window stops measuring and stops moving a Kind.

Measuring the time axis moves the Kind of a file that fits nowhere,
moving a Kind builds the tables again, and building the tables asks for
the axis. That was a closed ring: a measurement a second for as long as
the window stood open, with a line in the file list changing under
nobody's hands.

The measurement is replaced by a stand-in that answers at once and
counts how often it was asked, so "the axis was measured again" is a
number rather than a guess. What is asked is that the counting stops
and that no Kind moves after the first answer -- never how the window
avoids the second question.
"""
import os
import sys
import time
import shutil
import tempfile
import subprocess
import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
os.environ["VPM_NO_SPEAKER_SPLIT"] = "1"
os.environ.pop("AUPHONIC_TOKEN", None)


from PySide6 import QtWidgets, QtCore

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.update_offer = lambda *a, **k: None
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


PATIENCE = 40.0
QUIET_S = 3.0
POLL = 0.05

# ------------------------------------------------------------- the material
# Four cameras and two recordings, none of them carrying a timecode --
# that is what makes the window measure at all.
FOLDER = tempfile.mkdtemp(prefix="vpm_still_")


def a_camera(name, pattern, rate, tone):
    path = os.path.join(FOLDER, name)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y",
         "-f", "lavfi", "-i", "%s=size=160x90:rate=%d:duration=4"
         % (pattern, rate),
         "-f", "lavfi", "-i", "sine=frequency=%d:duration=4" % tone,
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", path],
        check=True, capture_output=True)
    return path


def a_recording(name, tone):
    path = os.path.join(FOLDER, name)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
         "-i", "sine=frequency=%d:duration=4" % tone, path],
        check=True, capture_output=True)
    return path


WIDE = a_camera("WideCam_A001.mp4", "testsrc", 24, 300)
ONE = a_camera("Guest_B002.mp4", "smptebars", 30, 400)
TWO = a_camera("Presenter_C003.mp4", "testsrc2", 30, 500)
THREE = a_camera("CoPresenter_D004.mp4", "testsrc", 34, 600)
EVERYTHING = [WIDE, ONE, TWO, THREE,
              a_recording("Presenter_REC0001.wav", 700),
              a_recording("Guest_REC0002.wav", 800)]
# The two the measurement will say it can place nowhere. Two of them,
# because one alone never showed the ring: they take turns at the Kind
# that only one file may carry, and each turn asked for a measurement.
NO_PLACE = [ONE, TWO]

# ------------------------------------------------- the measurement, replaced
# The same shape the real one answers in, and strict in the point that
# matters: what has no place is not on the axis either, exactly as
# measure_time_axis leaves it out.
asked = []


def measure_stand_in(paths, tc_of=None, HOP=5.0):
    asked.append(time.time())
    lost = set(vpm.path_key(p) for p in NO_PLACE)
    placed = [p for p in paths if vpm.path_key(p) not in lost]
    return ({"axis": dict((vpm.path_key(p), 0.0) for p in placed),
             "clock": dict((vpm.path_key(p), 1.0) for p in placed),
             "absolute": False, "weak": list(NO_PLACE),
             "unplaceable": [], "brief": [], "no_place": list(NO_PLACE)},
            "time axis measured")


vpm.measure_time_axis = measure_stand_in

# The window keeps its Kind values out of reach; this is where they
# pass by, on their way to the rule that moves them.
answers = {}
seen_off = []
_off = vpm.kinds_off_the_axis


def kinds_off_the_axis(values, no_place):
    answers["kinds"] = values
    seen_off.append(1)
    return _off(values, no_place)


vpm.kinds_off_the_axis = kinds_off_the_axis

QtWidgets.QFileDialog.getOpenFileNames = staticmethod(
    lambda *a, **k: (EVERYTHING, ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok

_show = QtWidgets.QWidget.show


def offstage(self):
    self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
    _show(self)


QtWidgets.QWidget.show = offstage
QtWidgets.QDialog.show = offstage


def drawn(text):
    return str(text).replace("&&", "\x00").replace("&", "") \
                    .replace("\x00", "&")


def button_named(text):
    for b in app.allWidgets():
        if isinstance(b, QtWidgets.QPushButton) \
                and drawn(b.text()).strip() == text:
            return b
    return None


def kinds_now():
    """What each video file's Kind says at this moment."""
    return dict((os.path.basename(p), v.get())
                for p, v in (answers.get("kinds") or {}).items())


def waited_for(condition, why, patience=PATIENCE):
    """Wait on a condition, never on the clock; None where it never came."""
    began_here = time.time()
    while time.time() - began_here < patience:
        app.processEvents()
        if condition():
            return time.time() - began_here
        time.sleep(POLL)
    print("      gave up after %.1f s waiting for %s" % (patience, why))
    return None


def drive():
    try:
        add = button_named(vpm.T('Add files ...'))
        if add is None:
            check("the time axis stops being measured while nobody "
                  "touches the window", False, "no Add button on screen")
            check("and no Kind moves by itself after the first answer",
                  False, "no Add button on screen")
            return
        add.click()
        # The sign of life: the first answer has reached the Kinds. It is
        # not what is judged below -- that is what happens afterwards.
        first = waited_for(lambda: bool(seen_off) and bool(kinds_now()),
                           "the first answer to reach the Kind fields")

        # Nobody touches anything from here on. Watched until the count
        # of measurements has stood still, and every Kind sampled along
        # the way, so a value that moved cannot be quietly put back.
        took = {}
        watch_from = time.time()
        stood_since = time.time()
        was = len(asked)
        while time.time() - watch_from < PATIENCE:
            app.processEvents()
            for name, kind in kinds_now().items():
                took.setdefault(name, [])
                if kind not in took[name]:
                    took[name].append(kind)
            if len(asked) != was:
                was = len(asked)
                stood_since = time.time()
            elif time.time() - stood_since >= QUIET_S:
                break
            time.sleep(POLL)
        quiet_for = time.time() - stood_since
        watched = time.time() - watch_from
        check("the time axis stops being measured while nobody touches "
              "the window", quiet_for >= QUIET_S,
              "%d measurements in %.1f s, quiet for the last %.1f s of "
              "%.1f s asked for, first answer after %s s"
              % (len(asked), watched, quiet_for, QUIET_S, first))
        moved = dict((n, v) for n, v in took.items() if len(v) > 1)
        check("and no Kind moves by itself after the first answer",
              not moved,
              "%d of %d files took more than one Kind: %r"
              % (len(moved), len(took), sorted(moved.items())))
    finally:
        app.quit()


QtCore.QTimer.singleShot(2500, drive)
QtCore.QTimer.singleShot(180000, app.quit)
sys.argv = ["videopodcast_magic.py"]
try:
    vpm.gui()
finally:
    shutil.rmtree(FOLDER, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
