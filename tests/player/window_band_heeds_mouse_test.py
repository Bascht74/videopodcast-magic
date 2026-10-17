# -*- coding: utf-8 -*-
"""The cut band names the shot under the mouse, and a click moves there.

The band and the player under it built as the Resolve tab builds them,
offscreen, with a stand-in where the cut player stands, and sent Qt's
own mouse events. In order: hovering over a shot names its camera, its
two times and its length, over a gap or past the last shot it names
nothing; a click sends the player to the moment under the mouse and
marks it on the band, and a player that refuses the jump costs the
band its mark nothing. The limit: the events are made here.
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
from PySide6 import QtCore, QtGui, QtWidgets
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


class StandInPlayer(QtWidgets.QWidget):
    """Where the cut player stands: it writes down where it was sent."""

    refuse = False

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.sent = []

    def jump(self, t):
        self.sent.append(t)
        if self.refuse:
            raise RuntimeError("the stand-in refuses the jump")


class Quiet(object):
    """The preview player beside it, which nothing here starts."""
    _should_play = False


host = QtWidgets.QWidget()
host.setAttribute(Qt.WA_DontShowOnScreen, True)
outer = QtWidgets.QVBoxLayout(host)
(band, player, _band_show,
 _preview_file) = vpm.make_band_and_player(
    Qt, QtCore, QtGui, QtWidgets, None, None, StandInPlayer, {}, [], [], {},
    outer, Quiet())
# Two hundred seconds over four hundred pixels: two pixels a second.
# A gap from 60 to 65 s, and nothing after 130.5 s.
CUT = [(0.0, 60.0, "WideCam"), (65.0, 130.5, "GuestCam")]
band.set(CUT, {"WideCam": "#3366cc", "GuestCam": "#cc6633"}, 200.0)
host.resize(400 + 200, 400)
host.show()
app.processEvents()
band.setFixedWidth(400)
app.processEvents()
assert band.width() == 400, band.width()  # the ground, not a judgement


def mouse(kind, x, button=Qt.NoButton):
    spot = QtCore.QPointF(x, band.height() / 2.0)
    e = QtGui.QMouseEvent(kind, spot, band.mapToGlobal(spot), button,
                          button, Qt.NoModifier)
    QtWidgets.QApplication.sendEvent(band, e)


TIP = vpm.T('%s -- %d:%02d to %d:%02d (%s s)')

try:
    print("1. Hovering")
    mouse(QtCore.QEvent.MouseMove, 200)        # 100 s, inside GuestCam
    wanted = TIP % ("GuestCam", 1, 5, 2, 10, vpm.number_text(65.5))
    check("over a shot the band names its camera, times and length",
          band.toolTip() == wanted,
          "%r against %r" % (band.toolTip(), wanted))
    mouse(QtCore.QEvent.MouseMove, 124)        # 62 s, in the gap
    check("over a gap between shots the band names nothing",
          band.toolTip() == "", "%r against ''" % band.toolTip())
    mouse(QtCore.QEvent.MouseMove, 60)         # 30 s, inside WideCam
    mouse(QtCore.QEvent.MouseMove, 340)        # 170 s, after the last
    check("past the last shot the band names nothing",
          band.toolTip() == "", "%r against ''" % band.toolTip())

    print("\n2. Clicking")
    mouse(QtCore.QEvent.MouseButtonPress, 300, Qt.LeftButton)   # 150 s
    check("a click sends the player to the moment under the mouse",
          player.sent == [150.0], "sent %r, wanted [150.0]" % player.sent)
    check("a click marks the moment on the band", band.spot == 150.0,
          "the mark stands at %r, wanted 150.0" % band.spot)
    player.refuse = True
    mouse(QtCore.QEvent.MouseButtonPress, 100, Qt.LeftButton)   # 50 s
    check("a player that refuses the jump leaves the band its mark",
          player.sent[-1:] == [50.0] and band.spot == 50.0,
          "sent %r, the mark stands at %r, wanted 50.0"
          % (player.sent, band.spot))
finally:
    host.close()

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
