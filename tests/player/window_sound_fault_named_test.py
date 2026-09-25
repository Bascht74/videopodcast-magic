# -*- coding: utf-8 -*-
"""A refused sound track costs neither the picture nor the truth.

Where Qt refuses a codec while it still has a picture on offer, the
fault is the sound track: the button that stands in for a picture is
never put up, the picture runs on from where it was, and the line above
says the sound cannot be played -- not that the app does not know the
format. Where there is no picture on offer, a refusal still names the
format.

One ground: a file that plays, refused by a stand-in error while it
runs, and one that is no media file at all, refused the same way.
Qt's own answer to a real broken sound track is not measured here.
"""
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
# One file that plays and one that is no media file at all: twenty
# thousand bytes of noise under a video name. Both inside this test's
# own folder, the playable one copied out of the shared material.
FOLDER = tempfile.mkdtemp(prefix="vpm_sound_")
PLAYS = os.path.join(FOLDER, "WideCam_A001.mp4")
shutil.copy2(os.path.join(fixture("playertest"), "a.mp4"), PLAYS)
NOTHING = os.path.join(FOLDER, "Guest_B002.mp4")
with open(NOTHING, "wb") as f:
    f.write(os.urandom(20000))

state = {"in_point": None, "out_point": None, "axis": {}}
(WindowSlider, VideoSurface, Player, NoPlayer) = vpm.make_player_widgets(
    QtCore, QtGui, QtWidgets, Qt, label, hint,
    lambda *a, **k: None, lambda *a, **k: None, state)

player = Player()
player.resize(640, 480)
player.setAttribute(Qt.WA_DontShowOnScreen, True)
player.show()
app.processEvents()

pictures = []
player.player.videoSink().videoFrameChanged.connect(
    lambda frame: pictures.append(1))

READY = (QtMultimedia.QMediaPlayer.LoadedMedia,
         QtMultimedia.QMediaPlayer.BufferedMedia)
FORMAT = QtMultimedia.QMediaPlayer.FormatError
INTO_MS = 1000     # how far into the file the refusal comes

SOUND_SAYS = vpm.T('%s   --   the sound cannot be played')
FORMAT_SAYS = vpm.T('%s   --   the app does not know this format')


def said_now():
    """The line above the picture, wherever the preview writes it."""
    return player.title.text()


try:
    print("1. A codec refused while the picture runs")
    player.load(PLAYS)
    waited_for(lambda: player.player.mediaStatus() in READY,
               "the file to open")
    player.start()
    # Well into the file before the refusal: a picture that was stopped
    # and started again runs from the front, and the front is where a
    # freshly opened file stands anyway.
    took = waited_for(lambda: player.player.position() > INTO_MS,
                      "the picture to run into the file")
    check("Qt has a picture on offer before the sound is refused",
          player.player.hasVideo() and took is not None,
          "hasVideo %s, %d ms in after %s s"
          % (player.player.hasVideo(), player.player.position(), took))

    before = player.player.position()
    was = len(pictures)
    player.on_error(FORMAT, "in the test")
    # Asked before any event is handled: a button put up and taken back
    # again once pictures arrive is a button the person saw.
    check("the button that stands in for the picture is never put up",
          not player.extern.isVisible(),
          "button up %s right after the refusal" % player.extern.isVisible())
    took = waited_for(lambda: len(pictures) > was,
                      "the picture to run on after the refused sound")
    check("the picture runs on from where it was, not from the front",
          took is not None and player.player.position() >= before,
          "%d ms against %d ms before, %d pictures more after %s s"
          % (player.player.position(), before, len(pictures) - was, took))
    check("the line above the picture says the sound cannot be played",
          said_now() == SOUND_SAYS % os.path.basename(PLAYS),
          "the line says %r" % said_now()[:70])

    print("\n2. The same refusal with no picture on offer")
    player.load(NOTHING)
    waited_for(lambda: player.player.error()
               != QtMultimedia.QMediaPlayer.NoError,
               "the app to refuse the file")
    player.on_error(FORMAT, "in the test")
    app.processEvents()
    check("a refusal with no picture on offer still names the format",
          said_now() == FORMAT_SAYS % os.path.basename(NOTHING)
          and player.extern.isVisible(),
          "hasVideo %s, button up %s, the line says %r"
          % (player.player.hasVideo(), player.extern.isVisible(),
             said_now()[:70]))
finally:
    try:
        player.player.stop()
    except Exception:
        pass
    shutil.rmtree(FOLDER, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
