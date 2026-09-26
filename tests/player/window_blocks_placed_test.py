# -*- coding: utf-8 -*-
"""The preview plays a recording in the block that holds the moment.

A recording that ran in two blocks is placed block by block: the block
whose place on the axis is the last one before the moment, counted from
that block's own start, and silence before the first. Sections: where
block_at puts a moment; the paused preview in the second block and back
in the first; playing from before the first block, silent from the
preview's first tick until the picture reaches the block, and then
sounding from its start. Not seen: the sound start() sets playing
before that first tick, which the tick pauses again.
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
import subprocess
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


POLL = 0.02      # the interval: what a wait costs when the thing comes
STILL = 20.0     # a sign of life unchanged this long: it never comes
PATIENCE = 60.0  # the bound a step that keeps moving reaches only broken


class Wait(object):
    """What a wait came back with, in the shape the FAIL line reads."""

    def __init__(self, took, why_not=""):
        self.took = took
        self.came = took is not None
        self.why_not = why_not

    def __str__(self):
        return "%.2f s" % self.took if self.came else self.why_not


def waited_for(condition, why, alive):
    """Wait on a condition, never on the clock; says what never came.

    What ends a wait that does not come is standstill: the sign of life
    unchanged for STILL seconds. One that keeps moving has PATIENCE. The
    judgement follows either way -- a wait that gave up must not take
    the check with it, only explain the numbers it then reads.
    """
    began_here = time.time()
    last, moved = alive(), began_here
    while True:
        app.processEvents()
        if condition():
            return Wait(time.time() - began_here)
        now = time.time()
        seen = alive()
        if seen != last:
            last, moved = seen, now
        if now - moved >= STILL:
            why_not = ("%.0f s with nothing changing, last %r"
                       % (now - moved, last))
            break
        if now - began_here >= PATIENCE:
            why_not = ("%.0f s still moving, last %r"
                       % (now - began_here, last))
            break
        time.sleep(POLL)
    print("      gave up waiting for %s: %s" % (why, why_not))
    return Wait(None, why_not)


# ------------------------------------------------------------- the material
# A camera of a minute and one recording in two blocks of twenty
# seconds, the second going on where the first ends. On the axis the
# camera starts at 0, the first block at 5 and the second at 25.
FOLDER = tempfile.mkdtemp(prefix="vpm_blocks_")
CAMERA = os.path.join(FOLDER, "Guest_B002.mp4")
FIRST = os.path.join(FOLDER, "Guest_REC0001.wav")
SECOND = os.path.join(FOLDER, "Guest_REC0002.wav")
shutil.copy2(os.path.join(fixture("playertest"), "a.mp4"), CAMERA)
for path, tone in ((FIRST, 300), (SECOND, 500)):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "sine=frequency=%d:duration=20" % tone,
                    "-c:a", "pcm_s16le", path], check=True)
PLACES = {CAMERA: 0.0, FIRST: 5.0, SECOND: 25.0}

state = {"in_point": None, "out_point": None,
         "axis": dict((vpm.path_key(p), t) for p, t in PLACES.items())}
(WindowSlider, VideoSurface, Player, NoPlayer) = vpm.make_player_widgets(
    QtCore, QtGui, QtWidgets, Qt, label, hint,
    lambda *a, **k: None, lambda p: None, state)

player = Player()
player.find_track = lambda path: [FIRST, SECOND]
player.resize(640, 480)
player.setAttribute(Qt.WA_DontShowOnScreen, True)
player.show()
app.processEvents()

PLAYING = QtMultimedia.QMediaPlayer.PlayingState
# How far past the block's start the sound may be first seen: a tick and
# a poll, and on a slow machine some more.
COMES_IN_MS = 400


def sound():
    """Which block the sound is in, and where in it, in ms."""
    return (os.path.basename(player.track_path or ""),
            player.track.position())


def alive():
    """What moves while the preview opens, seeks or plays."""
    return (sound(), player.track.mediaStatus(),
            player.track.playbackState(), player.player.position(),
            player._target_ms)


def in_block(name, ms):
    """Whether the sound stands in block *name*, 40 ms about *ms*.

    And the load has landed: until it has, the preview pulls the picture
    back to where the load aimed, and a jump made before that is undone.
    """
    here = sound()
    return (player._target_ms is None and here[0] == name
            and abs(here[1] - ms) <= 40)


try:
    print("1. Where block_at puts a moment")
    begins = PLACES.get
    got = vpm.block_at([FIRST, SECOND], 33.0, begins)
    check("a moment in the second block is that block, from its start",
          got == (SECOND, 8.0),
          "answered (%s, %r) against (Guest_REC0002.wav, 8.0)"
          % (os.path.basename(got[0] or ""), got[1]))
    got = vpm.block_at([FIRST, SECOND], 2.0, begins)
    check("a moment before the first block is in no block",
          got == (None, None),
          "answered (%s, %r) against (None, None)"
          % (os.path.basename(got[0] or "") or None, got[1]))

    print("\n2. The paused preview across the blocks")
    player.load(CAMERA, 33.0)
    took = waited_for(lambda: in_block("Guest_REC0002.wav", 8000),
                      "the sound in the second block", alive)
    check("at 33 s the preview plays the second block, 8 s into it",
          in_block("Guest_REC0002.wav", 8000),
          "read (block, ms) %r against ('Guest_REC0002.wav', 8000) after %s"
          % (sound(), took))
    player.jump(12000)
    took = waited_for(lambda: in_block("Guest_REC0001.wav", 7000),
                      "the sound back in the first block", alive)
    check("back at 12 s it plays the first block again, 7 s into it",
          in_block("Guest_REC0001.wav", 7000),
          "read (block, ms) %r against ('Guest_REC0001.wav', 7000) after %s"
          % (sound(), took))

    print("\n3. Playing from before the first block")
    player.jump(2000)
    app.processEvents()
    player.start()
    # The slider moves on the preview's own tick, which also places the
    # sound: past 2050 ms it has looked at least once.
    took = waited_for(lambda: player.slider.value() > 2050,
                      "the preview's first tick", alive)
    at = player.player.position()
    check("from the first tick before the first block the sound is quiet",
          took.came and at < 5000
          and player.track.playbackState() != PLAYING,
          "picture at %d ms after %s, sound %r %s"
          % (at, took, sound(), player.track.playbackState()))
    took = waited_for(lambda: player.track.playbackState() == PLAYING,
                      "the sound to come in", alive)
    at, into = player.player.position(), sound()[1]
    # Seen at once: the picture just past 5 s, the sound at its front,
    # and the two 5 s apart -- sound early, late or off in the block.
    check("once the picture reaches the first block its sound comes in",
          player.track.playbackState() == PLAYING
          and sound()[0] == "Guest_REC0001.wav"
          and 5000 <= at <= 5000 + COMES_IN_MS
          and abs(at - 5000 - into) <= COMES_IN_MS,
          "picture at %d ms after %s, sound %r %s, wanted the picture "
          "within %d ms past 5000 and the sound as far into the block"
          % (at, took, sound(), player.track.playbackState(),
             COMES_IN_MS))
finally:
    try:
        # Paused, not stopped: a stop while playback is wanted reports
        # the file loaded, loaded() plays it again inside that stop, and
        # it hung there one run in eighteen.
        player.pause()
    except Exception:
        pass
    shutil.rmtree(FOLDER, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
