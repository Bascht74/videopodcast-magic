# -*- coding: utf-8 -*-
"""A camera occupied only through the voices table hears that voice.

The preview plays the assigned recording under a camera. A voice heard
inside a recording gets its camera in the voices table, under the
recording, so a camera that only such a voice occupies has to hear the
voice's track: the finished one where it exists, else the recording
the voice was heard in. And the tick that switches the assigned sound
on hangs on that lookup: offered where a voice occupies the camera,
greyed where the lookup answers nothing.

One ground: one camera file, one voice row pointing at it, a finished
track and the recording behind the voice. The lookup is the window's
own; the tables are stood in for.
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
# A camera, the recording a voice was heard in, and the finished track
# that voice came back as. Two seconds of tone stand in for the sound:
# what is asked is which file the player takes, not what it plays.
FOLDER = tempfile.mkdtemp(prefix="vpm_voice_")
CAMERA = os.path.join(FOLDER, "Guest_B002.mp4")
RECORDING = os.path.join(FOLDER, "Guest_REC0002.wav")
FINISHED = os.path.join(FOLDER, "final_Guest_10-12-03-00.wav")
shutil.copy2(os.path.join(fixture("playertest"), "a.mp4"), CAMERA)
for wav in (RECORDING, FINISHED):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "sine=frequency=440:duration=2", "-c:a", "pcm_s16le",
                    wav], check=True)

# The tables as the window keeps them: no recording row names the
# camera, one voice row does. What the finished tracks hold is a
# dictionary here and a folder in the window.
voice_lines = [(vpm.speakers.voice_key(RECORDING, "SPEAKER_00"),
                vpm.Value("Guest"), vpm.Value(os.path.basename(CAMERA)))]
finished = {"Guest": FINISHED}


def lookup(path):
    return vpm.ui.audio_under_camera(path, {}, finished, [], voice_lines,
                                     vpm.ByFile())


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
