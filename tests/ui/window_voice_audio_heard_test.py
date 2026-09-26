# -*- coding: utf-8 -*-
"""A camera hears its voice; the wide shot, the one recording of every voice.

The preview plays the assigned recording under a camera. A voice heard
inside a recording gets its camera in the voices table, under the
recording, so a camera that only such a voice occupies has to hear the
voice's track: the finished one where it exists, else the recording
the voice was heard in. And the tick that switches the assigned sound
on hangs on that lookup: offered where a voice occupies the camera,
greyed where the lookup answers nothing. Then the wide shot, before
any mix: it hears the one recording that carries every voice, and
with two such recordings it keeps its own sound.

One ground: a camera and a wide shot, voice rows, a finished track
and the recordings behind the voices. The lookup is the window's own;
the tables are stood in for.
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
# A camera, the recording a voice was heard in, and the finished track
# that voice came back as. Two seconds of tone stand in for the sound:
# what is asked is which file the player takes, not what it plays.
FOLDER = tempfile.mkdtemp(prefix="vpm_voice_")
CAMERA = os.path.join(FOLDER, "Guest_B002.mp4")
RECORDING = os.path.join(FOLDER, "Guest_REC0002.wav")
FINISHED = os.path.join(FOLDER, "final_Guest_10-12-03-00.wav")
# The wide shot and the recordings of the last two sections: a room
# recorder that hears everybody, and a presenter's own recorder.
WIDE = os.path.join(FOLDER, "WideCam_C001.mp4")
ROOM = os.path.join(FOLDER, "Room_REC0001.wav")
OWN = os.path.join(FOLDER, "Presenter_REC0003.wav")
for mp4 in (CAMERA, WIDE):
    shutil.copy2(os.path.join(fixture("playertest"), "a.mp4"), mp4)
for wav in (RECORDING, FINISHED, ROOM, OWN):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "sine=frequency=440:duration=2", "-c:a", "pcm_s16le",
                    wav], check=True)

# The tables as the window keeps them: no recording row names the
# camera, one voice row does. What the finished tracks hold is a
# dictionary here and a folder in the window.
voice_lines = [(vpm.speakers.voice_key(RECORDING, "SPEAKER_00"),
                vpm.Value("Guest"), vpm.Value(os.path.basename(CAMERA)))]
finished = {"Guest": FINISHED}
assign_lines = []


def lookup(path):
    return vpm.ui.audio_under_camera(path, {}, finished, assign_lines,
                                     voice_lines, vpm.ByFile())


state = {"in_point": None, "out_point": None, "axis": {}}
(WindowSlider, VideoSurface, Player, NoPlayer) = vpm.make_player_widgets(
    QtCore, QtGui, QtWidgets, Qt, label, hint,
    lambda *a, **k: None, lambda *a, **k: None, state)

player = Player()
player.find_track = lookup
player.resize(640, 480)
player.setAttribute(Qt.WA_DontShowOnScreen, True)
player.show()
app.processEvents()


def heard():
    """The file the second player was pointed at, or nothing."""
    return player.track.source().toLocalFile()


def same_file(a, b):
    """Whether two spellings name one file.

    Qt hands a local file back with forward slashes, and on Windows the
    path the test built carries backslashes and may differ in the case
    of the drive letter -- measured red there with the two basenames
    printing alike. Compared normalised, so a spelling is not a fault.
    """
    return os.path.normcase(os.path.normpath(a)) \
        == os.path.normcase(os.path.normpath(b))


try:
    print("1. A camera that only a voice occupies, its track finished")
    player.load(CAMERA)
    app.processEvents()
    check("the tick is offered where a voice occupies the camera",
          player.track_checkbox.isEnabled(),
          "enabled %r" % player.track_checkbox.isEnabled())
    check("a camera occupied only through the voices table hears the "
          "voice's finished track",
          same_file(heard(), FINISHED),
          "source %r against %r" % (heard(), FINISHED))

    print("\n2. The same voice before its track is finished")
    finished.clear()
    player.track_adjust()
    app.processEvents()
    check("without a finished track the voice's own recording plays",
          same_file(heard(), RECORDING),
          "source %r against %r" % (heard(), RECORDING))

    print("\n3. A camera nobody occupies, and no mix")
    voice_lines[:] = []
    player.track_adjust()
    app.processEvents()
    check("the tick is greyed where the lookup answers nothing",
          not player.track_checkbox.isEnabled(),
          "enabled %r, source %r"
          % (player.track_checkbox.isEnabled(), os.path.basename(heard())))

    print("\n4. The wide shot, one recording carrying every voice, no mix")
    # The room recorder goes to the mix only; both voices heard in it
    # sit on their cameras. Nobody is on the wide shot.
    assign_lines[:] = [((ROOM,), vpm.Value(""), vpm.Value(vpm.MIX_ONLY))]
    voice_lines[:] = [
        (vpm.speakers.voice_key(ROOM, "SPEAKER_00"), vpm.Value("Guest"),
         vpm.Value(os.path.basename(CAMERA))),
        (vpm.speakers.voice_key(ROOM, "SPEAKER_01"),
         vpm.Value("Presenter"), vpm.Value("Presenter_B004.mp4"))]
    player.load(WIDE)
    app.processEvents()
    check("the wide shot hears the one recording that carries every voice",
          same_file(heard(), ROOM),
          "source %r against %r, tick enabled %r"
          % (heard(), ROOM, player.track_checkbox.isEnabled()))

    print("\n5. The wide shot, two recordings carrying voices, no mix")
    # The presenter now speaks into a recorder of their own.
    assign_lines.append(((OWN,), vpm.Value("Presenter"),
                         vpm.Value("Presenter_B004.mp4")))
    del voice_lines[1:]
    player.track_adjust()
    app.processEvents()
    check("with two recordings carrying voices the wide shot keeps its "
          "own sound",
          heard() == "" and not player.track_checkbox.isEnabled(),
          "source %r, tick enabled %r"
          % (os.path.basename(heard()), player.track_checkbox.isEnabled()))
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
