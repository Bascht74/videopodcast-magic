# -*- coding: utf-8 -*-
"""The cut player runs forward faster on every press, and says how fast.

The same four rates as the preview player, and the rate on the button
that made it. In order: the ladder up to eight and no further, what the
button says at each rate, what puts the rate back to normal, and that
the programme clock runs at the rate that was set -- a clock left
behind would switch the picture where the sound has long gone.
"""
import os
import sys
import time
import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT

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


# No file for the camera: nothing is decoded, and the rate, the button
# and the programme clock are all the player's own arithmetic.
LADDER = [2.0, 4.0, 8.0, 8.0]
CAPTIONS = ["2×", "4×", "8×", "8×"]
CutPlayer = vpm.qt_cut_player(QtCore, QtGui, QtWidgets, Qt, QtMultimedia,
                              QtMultimediaWidgets, label, hint, vpm.COLOURS)
player = CutPlayer()
player.resize(640, 480)
player.show()
app.processEvents()
player.set([(0.0, 600.0, "GuestCam_01011714_C003")], {}, {}, None, 0.0,
           0.0, 600.0)
player.clock.stop()

print("0. Before a press")
check("the player stands at normal speed to start with",
      player._speed == 1.0, "%g against 1" % player._speed)
check("the button says nothing at normal speed",
      player.fast_button.text() == "",
      "%r against %r" % (player.fast_button.text(), ""))

print("\n1. The ladder")
player.play()
rates, said = [], []
for _ in LADDER:
    player.faster()
    rates.append(player._speed)
    said.append(player.fast_button.text())
check("a press while it plays doubles the rate", rates[:2] == LADDER[:2],
      "%s against %s" % (rates[:2], LADDER[:2]))
check("the ladder stops at eight and stays there",
      rates == LADDER, "%s against %s" % (rates, LADDER))
check("the button carries the rate it is running at",
      said == CAPTIONS, "%s against %s" % (said, CAPTIONS))

print("\n2. What puts it back to normal")
player.pause()
check("pausing puts the rate back to normal",
      player._speed == 1.0 and player.fast_button.text() == "",
      "%g and %r" % (player._speed, player.fast_button.text()))
check("a press at a standstill starts it again at normal speed",
      (player.faster() or True) and player._speed == 1.0
      and player.is_running(),
      "%g, running %s" % (player._speed, player.is_running()))
player.faster()
before = player._speed
player.jump(30.0)
player.clock.stop()
check("a jump puts the rate back to normal",
      before == 2.0 and player._speed == 1.0,
      "%g before the jump, %g after" % (before, player._speed))

print("\n3. The programme clock")
# Set going by hand rather than by playing a file: what is measured
# here is the clock's arithmetic, and a decoder in between would
# measure the machine instead.
player._playing = True
player._seeking = False
player.base = 0.0
player.stopwatch.restart()
player.speed_set(2.0)
wall = QtCore.QElapsedTimer()
wall.start()
while player._time() < 1.0 and wall.elapsed() < 4000:
    app.processEvents()
    QtCore.QThread.msleep(5)
took = wall.elapsed()
check("the player reached the second it was waited for",
      player._time() >= 1.0,
      "the clock stands at %.2f s after %d ms" % (player._time(), took))
check("one second of programme takes half a second at twice speed",
      350 <= took <= 800,
      "%d ms of real time for 1.00 s of programme, allowed 350 to 800"
      % took)
player._playing = False

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
