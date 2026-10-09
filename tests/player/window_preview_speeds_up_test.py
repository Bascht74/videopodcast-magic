# -*- coding: utf-8 -*-
"""The preview runs forward faster on every press, and says how fast.

The preview player of the second tab, built offscreen on a short
camera file, with the fast forward button pressed as a user presses
it. In order: a press while it stands starts it at normal speed; while
it plays, the ladder up to eight and no further, and what the button
says at each rate; pausing puts it back to normal. The rate is what Qt's player reports, so the
ladder is judged on the player's own answer, not on what was asked.
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
import shutil
import tempfile
import time
import the_program
from fixture_root import fixture

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("VPM_SILENT", "1")
from PySide6 import QtCore, QtGui, QtWidgets, QtMultimedia
from PySide6.QtCore import Qt

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


FOLDER = tempfile.mkdtemp(prefix="vpm_fast_")
CAMERA = os.path.join(FOLDER, "WideCam_C001.mp4")
shutil.copy2(os.path.join(fixture("playertest"), "a.mp4"), CAMERA)
LADDER = [2.0, 4.0, 8.0, 8.0]
CAPTIONS = ["2×", "4×", "8×", "8×"]
PLAYING = QtMultimedia.QMediaPlayer.PlayingState

(_s, _v, Player, _n) = vpm.make_player_widgets(
    QtCore, QtGui, QtWidgets, Qt, label, hint, lambda *a, **k: None,
    lambda *a, **k: None, {"in_point": None, "out_point": None, "axis": {}})
player = Player()
player.setAttribute(Qt.WA_DontShowOnScreen, True)
player.resize(640, 480)
player.show()
app.processEvents()


def until(condition, limit_s=30.0):
    """Wait on *condition* in steps of 20 ms; how long it took, or None."""
    wall = time.time()
    while not condition():
        if time.time() - wall > limit_s:
            return None
        app.processEvents()
        QtCore.QThread.msleep(20)
    return time.time() - wall


try:
    print("1. A press while it stands")
    player.load(CAMERA)
    loaded = until(lambda: player.player.mediaStatus() in (
        QtMultimedia.QMediaPlayer.LoadedMedia,
        QtMultimedia.QMediaPlayer.BufferedMedia))
    check("the camera file opened in the preview", loaded is not None,
          "status %s after %s s" % (player.player.mediaStatus(), loaded))
    player.fast_button.click()
    took = until(lambda: player.player.playbackState() == PLAYING)
    check("a press while it stands starts it at normal speed",
          took is not None and player._speed == 1.0,
          "playing after %s s, at %g" % (took, player._speed))

    print("\n2. Presses while it plays")
    rates, said = [], []
    for _ in LADDER:
        player.fast_button.click()
        rates.append(player._speed)
        said.append(player.fast_button.text())
    check("a press while it plays doubles the rate", rates[:2] == LADDER[:2],
          "%s against %s" % (rates[:2], LADDER[:2]))
    check("the ladder stops at eight and stays there", rates == LADDER,
          "%s against %s" % (rates, LADDER))
    check("the button carries the rate it is running at",
          said == CAPTIONS, "%s against %s" % (said, CAPTIONS))

    print("\n3. Pausing")
    player.pause()
    check("pausing puts the rate back to normal",
          player._speed == 1.0 and player.fast_button.text() == "",
          "%g and %r" % (player._speed, player.fast_button.text()))
finally:
    player.player.stop()
    player.track.stop()
    player.close()
    app.processEvents()
    shutil.rmtree(FOLDER, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
