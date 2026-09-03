# -*- coding: utf-8 -*-
"""Zoom on the cut band: in, out, and what a press then means.

The sections: everything on show, in by a factor of two, out again and
never past the ends, the floor of a syllable, what a press means, the
stretch following the position, new material, the doors a user really
zooms through -- the third button, the wheel, the keys -- and zooming
with a point given or with no position at all.

Every judgement about where the stretch sits holds window() against a
stretch written out in seconds, never against a bound: window() ends in
max(0.0, ...) and min(self.length, ...), so a bound reads that clamp
back against itself and stays green however far over an edge the zoom
hung. A clamped stretch is a different stretch, and that is what shows.
The floor of a syllable is the one exception: it is held against the
program's own SHORTEST, so that floor can move without it noticing.

What a press means is pinned to the pixel as well as to the middle: the
bound there is a fraction of a single pixel, so reading a pixel from its
centre instead of from its left edge is red on purpose.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import importlib.util, sys, time
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))

CutBand = vpm.qt_cut_band(QtCore, QtGui, QtWidgets, Qt)
LENGTH = 3600.0
# The last shot ends five minutes before the recording does, because a
# cut list stops with the last speech. So the length handed to set() is
# not the end of the last shot, and a band that reads the one for the
# other has nowhere to hide.
CUT = [(0.0, 1200.0, "Host"), (1200.0, 2400.0, "Guest"),
       (2400.0, 3300.0, "Wide")]


def band():
    b = CutBand()
    b.resize(1000, 24)
    b.set(CUT, {"Host": "#ff0000", "Guest": "#00ff00", "Wide": "#0000ff"},
          LENGTH)
    return b


def at(b, first, last):
    """Whether the stretch on show is *first* .. *last*, to the second."""
    a, z = b.window()
    return abs(a - first) < 1e-6 and abs(z - last) < 1e-6


def shows(b, first, last):
    """The stretch on show against the one wanted, for the failure line."""
    a, z = b.window()
    return "%.2f .. %.2f, wanted %.2f .. %.2f" % (a, z, first, last)


def clicked(b, x):
    """What a press *x* pixels along the band asks for.

    A press only, no release: where the jump is triggered is part of
    what section five holds.
    """
    got = []
    b.selected.connect(got.append)
    QtWidgets.QApplication.sendEvent(b, QtGui.QMouseEvent(
        QtCore.QEvent.MouseButtonPress, QtCore.QPointF(x, 10.0),
        Qt.LeftButton, Qt.LeftButton, Qt.NoModifier))
    return got


print("1. To start with, everything is on show")
b = band()
check("the window is the whole length", at(b, 0.0, LENGTH),
      shows(b, 0.0, LENGTH))
# Unzoomed the section on show is the whole material, and that is what
# the reading says. Empty it left a hole beside the zoom buttons, and
# nobody could tell what the third one restores.
WHOLE = "0:00:00 -- 1:00:00"
check("and the reading says the whole length", b.zoom_text() == WHOLE,
      "%r, wanted %r" % (b.zoom_text(), WHOLE))

# A band with nothing in it yet reads zero to zero. That is what an
# empty band shows, and the line keeps its shape.
check("an empty band reads zero to zero",
      CutBand().zoom_text() == "0:00:00 -- 0:00:00",
      "%r, wanted '0:00:00 -- 0:00:00'" % CutBand().zoom_text())

print("\n2. In by a factor of two, around where we are")
b = band()
b.label_set(2400.0)
b.zoom(0.5)
a, z = b.window()
check("half as much is on show", abs((z - a) - LENGTH / 2) < 1e-6,
      "%.2f s on show, wanted %.2f s" % (z - a, LENGTH / 2))
check("and the position is in the middle",
      abs((a + z) / 2 - 2400.0) < 1e-6,
      "the middle is %.2f s, wanted 2400.00 s" % ((a + z) / 2))
b.zoom(0.5)
a, z = b.window()
check("again halves it", abs((z - a) - LENGTH / 4) < 1e-6,
      "%.2f s on show, wanted %.2f s" % (z - a, LENGTH / 4))
# The reading is held against the stretch it should name, not against
# "not empty": a reading that goes on naming the whole material while
# a quarter of it is on show is the fault worth catching, and "not
# empty" cannot see it.
QUARTER = "0:32:30 -- 0:47:30"
check("and the reading follows the zoom", b.zoom_text() == QUARTER,
      "%r, wanted %r" % (b.zoom_text(), QUARTER))

# Zooming in on a point at the right of what is on show has to travel
# right with it. The clamp that keeps the stretch inside the material
# and one that would keep it inside the old view are the same
# expression bar one name, so only the numbers tell them apart.
b = band()
b.label_set(600.0)
b.zoom(0.5); b.zoom(0.5)       # 150 .. 1050
b.label_set(900.0)
b.zoom(0.5)
check("zooming in at the right edge stays centred on the point",
      at(b, 675.0, 1125.0), shows(b, 675.0, 1125.0))

# Near an end there is nothing to centre on: the stretch is pushed
# inside whole rather than hanging over. Where it begins is no
# judgement of its own -- window() answers 0.00 for every stretch that
# hangs over the left edge, however far -- so it is the two seconds
# the band should show that are held against it.
b = band()
b.label_set(60.0)
b.zoom(0.5)
check("near the start the whole stretch is pushed inside",
      at(b, 0.0, 1800.0), shows(b, 0.0, 1800.0))

print("\n3. Out again, and never past the ends")
b = band()
b.label_set(60.0)
steps = []
for _ in range(4):
    b.zoom(0.5)
    steps.append(b.window())
starts = [s[0] for s in steps]
spans = [round(s[1] - s[0], 6) for s in steps]
# Every step, not only the last. A stretch that hung over the left
# edge is read back clamped, the next zoom works from the clamped
# reading, and within three turns it has walked itself back inside the
# material -- so the last step alone says nothing.
check("close to the start every step in sits against the edge",
      starts == [0.0, 0.0, 0.0, 0.0],
      "the four steps began at %s, wanted 0.00 each"
      % ", ".join("%.2f" % s for s in starts))
check("and every step in is half of the one before",
      spans == [1800.0, 900.0, 450.0, 225.0],
      "the four steps were %s s wide, wanted 1800, 900, 450, 225"
      % ", ".join("%.2f" % s for s in spans))
for _ in range(9):
    b.zoom(2.0)
check("out far enough is everything again", at(b, 0.0, LENGTH),
      shows(b, 0.0, LENGTH))
check("and it says the whole length again", b.zoom_text() == WHOLE,
      "%r, wanted %r" % (b.zoom_text(), WHOLE))

# At the far end the same, and then out again: there is nothing to the
# right left to take, so zooming out has to let the stretch grow to
# the left instead of staying where it was.
b = band()
b.label_set(LENGTH - 30.0)
b.zoom(0.5); b.zoom(0.5); b.zoom(0.5)
check("zoomed in at the end the stretch stops at the edge",
      at(b, 3150.0, LENGTH), shows(b, 3150.0, LENGTH))
b.zoom(2.0)
check("and zooming out there frees it to the left",
      at(b, 2700.0, LENGTH), shows(b, 2700.0, LENGTH))

print("\n4. Not smaller than a syllable")
b = band()
b.label_set(1800.0)
for _ in range(40):
    b.zoom(0.5)
a, z = b.window()
check("it stops at the shortest section",
      abs((z - a) - b.SHORTEST) < 1e-6,
      "%.4f s on show against a floor of %.4f s" % (z - a, b.SHORTEST))

print("\n5. A press means what is under it")
# All three judgements rest on the band really being a thousand pixels
# wide, because _time divides by the width. A precondition of the
# material, saying nothing about the program, so it is an assert and
# not a check.
b = band()
assert b.width() == 1000, "the band is %d pixels wide, not 1000" % b.width()
got = clicked(b, 500.0)
# What clicked() sends is a press and nothing else, so this asks first
# whether the press asked for a jump at all. Without it, a program that
# seeks on the release instead -- the usual cure for a drag across the
# band jumping about -- makes the two judgements below report that a
# press lands in the wrong place, and sends the next reader into _time
# when in truth the trigger moved.
check("a press on the band asks for a jump at all", bool(got),
      "%d jumps asked for on the press, wanted one" % len(got))
# The bound below is a hundredth of a second on an hour across a
# thousand pixels -- a three-hundred-sixtieth of one pixel. So this
# pins which edge of the pixel a press counts from, not merely that it
# lands near the middle, and the name says so. Measured on 2.9.2026,
# and the reason no wider bound would do: reading the pixel centre,
# (x + 0.5) / width, answers 1801.80 s here, and dividing by width + 1
# -- a mapping that is simply wrong -- answers 1798.20 s. Both are the
# same 1.80 s from the middle, on opposite sides, so a bound that let
# the one through would let the other through with it.
check("unzoomed a press halfway means the middle, to the pixel edge",
      bool(got) and abs(got[0] - 1800.0) < 0.01,
      "%s, wanted 1800.00 s"
      % ("%.2f s" % got[0] if got else "no jump asked for"))

b = band()
b.label_set(2400.0)
b.zoom(0.5)                    # 1500 .. 3300 on 1000 pixels
got = clicked(b, 500.0)
check("zoomed in the same press means the middle, to the pixel edge",
      bool(got) and abs(got[0] - 2400.0) < 0.01,
      "%s, wanted 2400.00 s"
      % ("%.2f s" % got[0] if got else "no jump asked for"))

print("\n6. The section follows the position")
b = band()
b.label_set(600.0)
b.zoom(0.5); b.zoom(0.5)       # 150 .. 1050
a0, z0 = b.window()
b.label_set(3000.0)            # far outside
a1, z1 = b.window()
check("it moves along", a1 > a0,
      "%.0f -> %.0f, wanted further right" % (a0, a1))
check("the position is inside again", a1 <= 3000.0 <= z1,
      "3000.00 s against %.2f .. %.2f" % (a1, z1))
check("and the size stayed the same", abs((z1 - a1) - (z0 - a0)) < 1e-6,
      "%.3f s wide against %.3f s before" % (z1 - a1, z0 - a0))

# Dragged past an end the stretch stops there. label_set clamps on its
# own, and nothing above this reaches that clamp: the two below are
# the only judgements in the file that see it at all.
b = band()
b.label_set(600.0)
b.zoom(0.5); b.zoom(0.5)       # 150 .. 1050
b.label_set(LENGTH - 30.0)
check("dragged past the end the stretch stops at the edge",
      at(b, 2700.0, LENGTH), shows(b, 2700.0, LENGTH))

b = band()
b.label_set(3000.0)
b.zoom(0.5); b.zoom(0.5)       # 2550 .. 3450
b.label_set(30.0)
check("dragged before the start it stops at the edge",
      at(b, 0.0, 900.0), shows(b, 0.0, 900.0))

print("\n7. New material starts over")
b = band()
b.label_set(600.0)
b.zoom(0.5)
b.set(CUT, {}, LENGTH)
check("the zoom is dropped", at(b, 0.0, LENGTH), shows(b, 0.0, LENGTH))

print("\n8. The doors a user really zooms through")
# Everything above turns the zoom by hand. The three ways the manual
# promises -- the third button, the wheel over the band and the keys
# after a click on it -- go through code of their own, and the buttons
# and their connections sit inside gui(), which no test builds. So
# these are the only place that code is entered at all.
b = band()
b.label_set(600.0)
b.zoom(0.5); b.zoom(0.5)
b.zoom_all()
check("the third button brings the whole length back",
      at(b, 0.0, LENGTH), shows(b, 0.0, LENGTH))
# The wheel carries the pointer with it: a turn over the right of the
# band has to magnify what is under the pointer, not what is under the
# playhead. Position 0 s, pointer three quarters along, so the two
# answers lie 1800 s apart and cannot be confused; and a wheel turned
# round would show everything instead of half.
b = band()
b.label_set(0.0)
QtWidgets.QApplication.sendEvent(b, QtGui.QWheelEvent(
    QtCore.QPointF(750.0, 10.0), QtCore.QPointF(750.0, 10.0),
    QtCore.QPoint(0, 0), QtCore.QPoint(0, 120),
    Qt.NoButton, Qt.NoModifier, Qt.NoScrollPhase, False))
check("a turn of the wheel zooms in where the pointer is",
      at(b, 1800.0, LENGTH), shows(b, 1800.0, LENGTH))


def pressed(b, code):
    """One key press on the band."""
    QtWidgets.QApplication.sendEvent(b, QtGui.QKeyEvent(
        QtCore.QEvent.KeyPress, code, Qt.NoModifier))


b = band()
b.label_set(2400.0)
pressed(b, Qt.Key_Plus)
check("plus shows half as much around the position",
      at(b, 1500.0, 3300.0), shows(b, 1500.0, 3300.0))
pressed(b, Qt.Key_Minus)
check("and minus twice as much again", at(b, 0.0, LENGTH),
      shows(b, 0.0, LENGTH))
pressed(b, Qt.Key_Plus)
pressed(b, Qt.Key_Plus)
pressed(b, Qt.Key_0)
check("and nought the whole length", at(b, 0.0, LENGTH),
      shows(b, 0.0, LENGTH))

print("\n9. Zooming with no point given")
# The second argument of zoom() carries a centring rule of its own and
# the wheel is its only caller in the program, so without this the
# difference between "the wheel zooms where the pointer is" and "where
# the playhead is" is unheld. The position is at 600 s and the point
# given is 3000 s, so the two answers do not overlap.
b = band()
b.label_set(600.0)
b.zoom(0.5, 3000.0)
check("a point handed to the zoom beats the position",
      at(b, 1800.0, LENGTH), shows(b, 1800.0, LENGTH))
# And before anything has been clicked there is no position at all.
# That is the band's state right after set(), so a user pressing plus
# first walks into it.
b = band()
b.zoom(0.5)
check("with no position yet it zooms on the middle",
      at(b, 900.0, 2700.0), shows(b, 900.0, 2700.0))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
