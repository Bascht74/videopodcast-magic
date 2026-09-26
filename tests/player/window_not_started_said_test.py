# -*- coding: utf-8 -*-
"""A camera switched to before it began says so, and the moment is kept.

Where the second camera starts later than the moment on show, the
switch lands on that camera's front: a reading of zero there says the
camera had begun, and it had not. The line under the picture has to
say the camera has not started yet, the moment kept for the next
switch has to be the one from before, and the sentence has to give
way to a time as soon as that camera runs.

One ground: two copies of the same file, one placed on the measured
axis half a minute after the other. The first stands at a moment, the
second is switched to, and the second is then started.
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
import shutil
import tempfile
import the_program

SCRIPT = the_program.SCRIPT

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("VPM_SILENT", "1")


from PySide6 import QtCore, QtGui, QtWidgets, QtMultimedia
from PySide6.QtCore import Qt

sys.path.insert(0, HERE)
from fixture_root import fixture

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def label(text, colour=None, bold=False, large=0):
    return QtWidgets.QLabel(text)


def hint(widget, text):
    widget.setToolTip(text)
    return widget


PATIENCE = 20.0
POLL = 0.02


def waited_for(condition, why, patience=PATIENCE):
    """Wait on a condition, never on the clock; None where it never came.

    The judgement follows either way -- a wait that gave up must not
    take the check with it, only explain the numbers it then reads.
    """
    began_here = time.time()
    while time.time() - began_here < patience:
        app.processEvents()
        if condition():
            return time.time() - began_here
        time.sleep(POLL)
    print("      gave up after %.1f s waiting for %s" % (patience, why))
    return None


# ------------------------------------------------------------- the material
# The same playable file twice, under two camera names, inside this
# test's own folder. What separates them is the measured axis: the
# second begins half a minute after the first.
FOLDER = tempfile.mkdtemp(prefix="vpm_started_")
FIRST = os.path.join(FOLDER, "WideCam_A001.mp4")
LATER = os.path.join(FOLDER, "Guest_B002.mp4")
shutil.copy2(os.path.join(fixture("playertest"), "a.mp4"), FIRST)
shutil.copy2(os.path.join(fixture("playertest"), "a.mp4"), LATER)

MOMENT = 5.0        # where the first camera stands before the switch
LATER_BEGINS = 30.0  # the second camera's start on the axis

state = {"in_point": None, "out_point": None,
         "axis": {vpm.path_key(FIRST): 0.0,
                  vpm.path_key(LATER): LATER_BEGINS}}
(WindowSlider, VideoSurface, Player, NoPlayer) = vpm.make_player_widgets(
    QtCore, QtGui, QtWidgets, Qt, label, hint,
    lambda *a, **k: None, lambda *a, **k: None, state)

player = Player()
player.resize(640, 480)
player.setAttribute(Qt.WA_DontShowOnScreen, True)
player.show()
app.processEvents()

READY = (QtMultimedia.QMediaPlayer.LoadedMedia,
         QtMultimedia.QMediaPlayer.BufferedMedia)

NOT_STARTED = vpm.T('%s has not started yet') % os.path.basename(LATER)


def reading():
    """The line under the picture: time on the left, position on the right."""
    return player.middle.text()


try:
    print("1. The first camera stands at a moment")
    player.load(FIRST, MOMENT)
    took = waited_for(lambda: player.player.mediaStatus() in READY,
                      "the first camera to open")
    on_axis = player.position()[1]
    check("the first camera stands at the moment before the switch",
          on_axis is not None and abs(on_axis - MOMENT) < 0.05,
          "axis position %r against %.2f s, opened after %s s"
          % (on_axis, MOMENT, took))

    print("\n2. The switch to a camera that begins later")
    player.load(LATER)
    app.processEvents()
    check("the line under the picture says the camera has not started",
          reading() == NOT_STARTED,
          "the line says %r" % reading())
    on_axis = player.position()[1]
    check("the moment kept at the switch is the one from before it",
          on_axis is not None and abs(on_axis - MOMENT) < 0.05,
          "axis position %r against %.2f s" % (on_axis, MOMENT))

    print("\n3. The later camera runs")
    took = waited_for(lambda: player.player.mediaStatus() in READY,
                      "the later camera to open")
    player.start()
    ran = waited_for(lambda: player.player.position() > 0,
                     "the later camera to run")
    app.processEvents()
    check("once the later camera runs the sentence gives way to a time",
          ran is not None and reading() != NOT_STARTED,
          "position %d ms after %s s, the line says %r"
          % (player.player.position(), ran, reading()))
finally:
    try:
        player.player.stop()
    except Exception:
        pass
    shutil.rmtree(FOLDER, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
