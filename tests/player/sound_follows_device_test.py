# -*- coding: utf-8 -*-
"""The cut player's sound follows a new output device and keeps its place.

Headphones in or out: the old output plays into nothing. The cut player
is built offscreen, its sound output, its audio player and the seek on
it are stood in for, and the system's default device is answered by
the test; the change is announced through the player's own
QMediaDevices signal. In order: a new device while it plays, the same
device again, no device at all, a new device while it stands. The
limit: no real device is switched, so what is judged is what the player
asks of its output, not what comes out of a speaker.
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


def label(text, colour=None, bold=False):
    return QtWidgets.QLabel(text)


def hint(widget, text):
    widget.setToolTip(text)
    return widget


class Device(object):
    """An output device: a name, and itself to be compared with."""

    def __init__(self, name):
        self.name = name

    def description(self):
        return self.name

    def __repr__(self):
        return self.name


class Output(object):
    """The player's sound output: which device it plays into."""

    def __init__(self, device):
        self.now = device
        self.set_to = []

    def device(self):
        return self.now

    def setDevice(self, device):
        self.set_to.append(device)
        self.now = device

    def setMuted(self, _on):
        pass

    def setVolume(self, _v):
        pass


class Audio(object):
    """The audio player: where it stands, and whether it was started."""

    def __init__(self, ms):
        self.ms = ms
        self.started = 0

    def position(self):
        return self.ms

    def play(self):
        self.started += 1


class Seek(object):
    """The seek on the audio player: where it was sent."""

    def __init__(self):
        self.sent = []

    def seek_to(self, ms, reason=""):
        self.sent.append(ms)


CutPlayer = vpm.qt_cut_player(QtCore, QtGui, QtWidgets, Qt, QtMultimedia,
                              QtMultimediaWidgets, label, hint, vpm.COLOURS)
player = CutPlayer()
player.setAttribute(Qt.WA_DontShowOnScreen, True)
player.resize(640, 480)
player.show()
app.processEvents()

SPEAKER, PHONES = Device("Speaker"), Device("Headphones")
default = [SPEAKER]
real_default = QtMultimedia.QMediaDevices.defaultAudioOutput
QtMultimedia.QMediaDevices.defaultAudioOutput = staticmethod(
    lambda: default[0])


def fresh(playing, ms=42000):
    """Stand-ins put in, the player playing or standing at *ms*."""
    player.audio_out = Output(SPEAKER)
    player.audio = Audio(ms)
    player.audio_seek = Seek()
    player._playing = playing


raised = []


def change(device):
    """The system says its outputs changed; *device* is the default now.

    What the player raises in answer is written down: Qt prints it and
    goes on, so without this a fall would pass for "changed nothing".
    """
    default[0] = device
    if player.devices is None:
        return
    hook = sys.excepthook
    sys.excepthook = lambda kind, value, _tb: raised.append(
        "%s: %s" % (kind.__name__, value))
    try:
        player.devices.audioOutputsChanged.emit()
        app.processEvents()
    finally:
        sys.excepthook = hook


try:
    check("the player listens for a change of output device",
          player.devices is not None, "devices %r" % (player.devices,))

    print("\n1. Headphones in while it plays")
    fresh(True)
    change(PHONES)
    check("the sound switches to the new device",
          player.audio_out.set_to == [PHONES],
          "switched to %r, wanted [Headphones]" % player.audio_out.set_to)
    check("the sound is sent back to where it stood",
          player.audio_seek.sent == [42000],
          "sent to %r ms, wanted [42000]" % player.audio_seek.sent)
    check("playing, it plays on after the switch",
          player.audio.started == 1,
          "started %d times, wanted 1" % player.audio.started)

    print("\n2. The same device again, and none at all")
    fresh(True)
    change(SPEAKER)
    check("the device it already plays into changes nothing",
          player.audio_out.set_to == [] and player.audio_seek.sent == [],
          "switched to %r, sent to %r"
          % (player.audio_out.set_to, player.audio_seek.sent))
    change(None)
    check("no device at all changes nothing",
          player.audio_out.set_to == [] and player.audio_seek.sent == []
          and raised == [],
          "switched to %r, sent to %r, raised %r"
          % (player.audio_out.set_to, player.audio_seek.sent, raised))

    print("\n3. Headphones in while it stands")
    fresh(False, 9000)
    change(PHONES)
    check("standing, it switches and keeps its place without playing",
          player.audio_out.set_to == [PHONES]
          and player.audio_seek.sent == [9000]
          and player.audio.started == 0,
          "switched to %r, sent to %r, started %d times"
          % (player.audio_out.set_to, player.audio_seek.sent,
             player.audio.started))
finally:
    QtMultimedia.QMediaDevices.defaultAudioOutput = real_default
    player._playing = False
    player.clock.stop()

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
