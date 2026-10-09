# -*- coding: utf-8 -*-
"""Mute silences both players and gives the sound back, a test run never.

Both players built offscreen with their sound outputs stood in for, and
the mute button pressed as a user presses it. In order: the cut
player, muted and unmuted, with the symbol on its button; the preview,
whose camera sound stays off while the assigned recording plays, and
whose volume reaches both outputs; then a test run, which stays
silent whatever is pressed. The quiet a test run keeps is switched off
in the player piece for the first two sections only, and only the
stand-ins hear it: nothing here reaches a speaker.
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
import the_program

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("VPM_SILENT", "1")
from PySide6 import QtCore, QtGui, QtWidgets, QtMultimedia
from PySide6 import QtMultimediaWidgets
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


class Output(object):
    """A sound output: whether it is muted, and how loud."""

    def __init__(self):
        self.muted, self.volume = None, None

    def setMuted(self, on):
        self.muted = on

    def setVolume(self, value):
        self.volume = value

    def __repr__(self):
        return "muted %s at %s" % (self.muted, self.volume)


# The switch every player reads: on for a test run. Off below for the
# first two sections, where only the stand-ins listen.
PIECE = vpm.qt_cut_player.__globals__
QUIET = PIECE["SILENT_PLAYER"]


def symbol(button):
    """Which of the two volume symbols the button carries."""
    style = button.style()
    shown = button.icon().pixmap(18, 18).toImage()
    for name in ("SP_MediaVolumeMuted", "SP_MediaVolume"):
        icon = style.standardIcon(getattr(QtWidgets.QStyle, name))
        if icon.pixmap(18, 18).toImage() == shown:
            return name
    return "neither"


CutPlayer = vpm.qt_cut_player(QtCore, QtGui, QtWidgets, Qt, QtMultimedia,
                              QtMultimediaWidgets, label, hint, vpm.COLOURS)
cut = CutPlayer()
(_s, _v, Player, _n) = vpm.make_player_widgets(
    QtCore, QtGui, QtWidgets, Qt, label, hint, lambda *a, **k: None,
    lambda *a, **k: None, {"in_point": None, "out_point": None, "axis": {}})
preview = Player()
for w in (cut, preview):
    w.setAttribute(Qt.WA_DontShowOnScreen, True)
    w.resize(640, 480)
    w.show()
app.processEvents()
check("the two volume symbols can be told apart",
      symbol(cut.mute_button) == "SP_MediaVolume",
      "the button carries %r before any press" % symbol(cut.mute_button))

try:
    PIECE["SILENT_PLAYER"] = False
    print("\n1. The cut player")
    cut.audio_out = Output()
    cut.mute_button.click()
    check("a press on mute silences the cut player",
          cut.audio_out.muted is True, "output %r" % cut.audio_out)
    check("the cut player's button then shows the muted symbol",
          symbol(cut.mute_button) == "SP_MediaVolumeMuted",
          "the button carries %r" % symbol(cut.mute_button))
    cut.mute_button.click()
    check("a second press gives the cut player its sound back",
          cut.audio_out.muted is False
          and symbol(cut.mute_button) == "SP_MediaVolume",
          "output %r, the button carries %r"
          % (cut.audio_out, symbol(cut.mute_button)))

    print("\n2. The preview, with a recording assigned")
    preview.audio, preview.track_audio = Output(), Output()
    preview.track_blocks = [("Presenter_REC0001.wav", 0.0, 60.0)]
    preview.mute_button.click()
    check("a press on mute silences camera and recording",
          preview.audio.muted is True and preview.track_audio.muted is True,
          "camera %r, recording %r" % (preview.audio, preview.track_audio))
    preview.mute_button.click()
    check("unmuted, the recording is heard and the camera stays off",
          preview.track_audio.muted is False and preview.audio.muted is True,
          "camera %r, recording %r" % (preview.audio, preview.track_audio))
    preview.track_blocks = []
    preview.loud.setValue(40)
    check("without a recording the camera is heard at the volume set",
          preview.audio.muted is False and preview.audio.volume == 0.4,
          "camera %r, wanted unmuted at 0.4" % preview.audio)
    check("the volume reaches the recording's output too",
          preview.track_audio.volume == 0.4,
          "recording %r, wanted 0.4" % preview.track_audio)
finally:
    PIECE["SILENT_PLAYER"] = QUIET

print("\n3. A test run")
cut.audio_out = Output()
cut.mute_button.click()
cut.mute_button.click()
preview.audio, preview.track_audio = Output(), Output()
preview.mute_button.click()
preview.mute_button.click()
check("a test run stays silent after mute is pressed twice",
      QUIET and cut.audio_out.muted is True
      and preview.audio.muted is True and preview.track_audio.muted is True
      and preview.audio.volume == 0.0,
      "switch %s; cut %r, camera %r, recording %r"
      % (QUIET, cut.audio_out, preview.audio, preview.track_audio))
cut.close()
preview.close()

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
