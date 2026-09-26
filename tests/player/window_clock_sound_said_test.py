# -*- coding: utf-8 -*-
"""Until the sound is measured in, the line under the picture says so.

The assigned sound is placed by the measured axis where there is one
and by the clocks until then -- a whole clock error off, and nothing
said it. With the assigned sound on under the camera, the line under
the picture says the sound is placed by clock while the measurement is
pending, stays a time where no sound is assigned at all, and gives way
to the time again once the placing is measured. A paused player sends
no position tick, so the line also follows the tick under the picture
being put on and taken off, and the measurement arriving, without one.

One ground: one camera file with one assigned track. A stand-in for
the player's own placing answers by clock, then measured; the last
section places for real, the camera's clock set by hand.
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
# The track's own clock, half a second before the camera's; read by the
# real placing in the last section only.
CAMERA_CLOCK = 100.0
clocks = {TRACK: CAMERA_CLOCK - 0.5}
(WindowSlider, VideoSurface, Player, NoPlayer) = vpm.make_player_widgets(
    QtCore, QtGui, QtWidgets, Qt, label, hint,
    lambda *a, **k: None, lambda p: clocks.get(p), state)

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

    print("\n4. Paused: no position tick, the line follows all the same")
    del player.track_where          # the player's own placing again
    player.tc0 = CAMERA_CLOCK       # the fixture carries no timecode
    state["axis"] = {}
    ticks = []
    player.player.positionChanged.connect(ticks.append)
    player.track_checkbox.setChecked(False)
    player.track_checkbox.setChecked(True)
    app.processEvents()
    check("the tick put on says the sound is placed by clock",
          reading() == CLOCK_LINE and not ticks,
          "the line says %r after %d position ticks"
          % (reading(), len(ticks)))
    before = reading()
    player.track_checkbox.setChecked(False)
    app.processEvents()
    check("the tick taken off gives the line its time back",
          before == CLOCK_LINE and reading() != CLOCK_LINE
          and "0:00:0" in reading() and not ticks,
          "the line said %r, then %r, after %d position ticks"
          % (before, reading(), len(ticks)))

    # The measurement arrives as the window takes it in: through the
    # axis's own presenter, everything round the player a stand-in.
    player.track_checkbox.setChecked(True)
    app.processEvents()
    arrive = []
    bridge = type("Bridge", (), {})()
    bridge.axis = type("Signal", (), {"connect": lambda s, f: arrive.append(f)})()
    plan = type("Plan", (), {"begin": lambda *a: None,
                             "done": lambda *a: None})()
    nothing = lambda *a, **k: None
    vpm.make_time_axis(
        state=state, files=[], plan=plan, bridge=bridge,
        bridge_emit=nothing, assign_lines=nothing, blocks_of=nothing,
        real_tc=lambda p: clocks.get(p), HOP=5.0, prework_busy=nothing,
        out_folder=None, production_var=None, commonest_folder=nothing,
        project_move=nothing, project_collect=nothing,
        settings_extend=nothing, axis_label=QtWidgets.QLabel(),
        player=player, video_kind_again={}, kind_answered=nothing,
        show_weak=nothing, tc_column_show=nothing,
        player_follow_up=nothing, window_enable=nothing,
        window_position_show=nothing)
    before = reading()
    arrive[0]({"axis": {vpm.path_key(CAMERA): 0.0,
                        vpm.path_key(TRACK): -0.5},
               "remembered": True}, "measured")
    app.processEvents()
    check("the measurement arriving gives the line its time back",
          before == CLOCK_LINE and reading() != CLOCK_LINE
          and "0:00:0" in reading() and not ticks,
          "the line said %r, then %r, after %d position ticks"
          % (before, reading(), len(ticks)))
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
