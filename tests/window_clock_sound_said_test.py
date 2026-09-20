# -*- coding: utf-8 -*-
"""Until the sound is measured in, the line under the picture says so.

The assigned sound is placed by the measured axis where there is one
and by the clocks until then -- a whole clock error off, and nothing
said it. With the assigned sound on under the camera, the line under
the picture says the sound is placed by clock while the measurement is
pending, stays a time where no sound is assigned at all, and gives way
to the time again once the placing is measured.

One ground: one camera file with one assigned track, and a stand-in
for the player's own placing that answers by clock, then measured.
What the real placing answers is not measured here.
"""
import os
import sys
import time
import shutil
import subprocess
import tempfile
import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("VPM_SILENT", "1")


from PySide6 import QtCore, QtGui, QtWidgets
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


# ------------------------------------------------------------- the material
# A camera and the track assigned to it: two seconds of tone, since
# what is asked is the line under the picture, not the sound.
FOLDER = tempfile.mkdtemp(prefix="vpm_clock_")
CAMERA = os.path.join(FOLDER, "Guest_B002.mp4")
TRACK = os.path.join(FOLDER, "Guest_REC0002.wav")
shutil.copy2(os.path.join(fixture("playertest"), "a.mp4"), CAMERA)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "sine=frequency=440:duration=2", "-c:a", "pcm_s16le",
                TRACK], check=True)

state = {"in_point": None, "out_point": None, "axis": {}}
(WindowSlider, VideoSurface, Player, NoPlayer) = vpm.make_player_widgets(
    QtCore, QtGui, QtWidgets, Qt, label, hint,
    lambda *a, **k: None, lambda *a, **k: None, state)

player = Player()
player.find_track = lambda path: [TRACK]
player.resize(640, 480)
player.setAttribute(Qt.WA_DontShowOnScreen, True)
player.show()
app.processEvents()

CLOCK_LINE = vpm.T('sound placed by clock -- measurement pending')
placed_by = ["by clock"]


def placing():
    """The stand-in for the player's own placing of the sound."""
    return TRACK, 1.0, placed_by[0]


def reading():
    """The line under the picture."""
    return player.middle.text()


try:
    print("1. The sound placed by clock")
    player.load(CAMERA)
    app.processEvents()
    check("the assigned sound is on under the camera",
          player.track_blocks == [TRACK],
          "blocks %r" % [os.path.basename(b) for b in player.track_blocks])
    player.track_where = placing
    player.spot(1000)
    check("placed by clock, the line says the measurement is pending",
          reading() == CLOCK_LINE, "the line says %r" % reading())

    print("\n2. The tick off: no sound assigned")
    player.track_checkbox.setChecked(False)
    player.spot(1500)
    check("with no sound assigned the line stays a time",
          reading() != CLOCK_LINE and "0:00:01" in reading(),
          "the line says %r" % reading())

    print("\n3. The placing measured")
    player.track_checkbox.setChecked(True)
    placed_by[0] = "measured"
    player.spot(2000)
    check("once measured the line gives way to the time",
          reading() != CLOCK_LINE and "0:00:02" in reading(),
          "the line says %r" % reading())
finally:
    try:
        player.track.stop()
        player.player.stop()
    except Exception:
        pass
    shutil.rmtree(FOLDER, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
