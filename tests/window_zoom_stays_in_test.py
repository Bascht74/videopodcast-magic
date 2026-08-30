# -*- coding: utf-8 -*-
"""Zoom on the cut band: in, out, and what the click then means."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

CutBand = vpm.qt_cut_band(QtCore, QtGui, QtWidgets, Qt)
LENGTH = 3600.0
CUT = [(0.0, 1200.0, "Host"), (1200.0, 2400.0, "Guest"),
       (2400.0, LENGTH, "Wide")]

def band():
    b = CutBand()
    b.resize(1000, 24)
    b.set(CUT, {"Host": "#ff0000", "Guest": "#00ff00", "Wide": "#0000ff"},
          LENGTH)
    return b

print("1. To start with, everything is on show")
b = band()
check("the window is the whole length", b.window() == (0.0, LENGTH),
      str(b.window()))
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
      repr(CutBand().zoom_text()))

print("\n2. In by a factor of two, around where we are")
b = band()
b.label_set(2400.0)
b.zoom(0.5)
a, z = b.window()
check("half as much is on show", abs((z - a) - LENGTH / 2) < 1e-6, z - a)
check("and the position is in the middle",
      abs((a + z) / 2 - 2400.0) < 1e-6, (a + z) / 2)
b.zoom(0.5)
a, z = b.window()
check("again halves it", abs((z - a) - LENGTH / 4) < 1e-6, z - a)
check("it says which section", b.zoom_text() != "", b.zoom_text())

# Near an end there is nothing to centre on: the section stops at the
# edge and keeps its size rather than hanging over.
b = band()
b.label_set(60.0)
b.zoom(0.5)
a, z = b.window()
check("near the start it sits against the edge", a == 0.0, a)
check("and keeps its size", abs((z - a) - LENGTH / 2) < 1e-6, z - a)

print("\n3. Out again, and never past the ends")
b = band()
b.label_set(60.0)
for _ in range(4):
    b.zoom(0.5)
a, z = b.window()
check("close to the start it does not run into the negative", a >= 0.0, a)
check("and the section is still the right size",
      abs((z - a) - LENGTH / 16) < 1e-6, z - a)
for _ in range(9):
    b.zoom(2.0)
check("out far enough is everything again", b.window() == (0.0, LENGTH),
      str(b.window()))
check("and it says the whole length again", b.zoom_text() == WHOLE,
      "%r, wanted %r" % (b.zoom_text(), WHOLE))

b = band()
b.label_set(LENGTH - 30.0)
b.zoom(0.5); b.zoom(0.5); b.zoom(0.5)
a, z = b.window()
check("at the end it does not run past it", z <= LENGTH + 1e-9, z)

print("\n4. Not smaller than a syllable")
b = band()
b.label_set(1800.0)
for _ in range(40):
    b.zoom(0.5)
a, z = b.window()
check("it stops at the shortest section",
      abs((z - a) - b.SHORTEST) < 1e-6, z - a)

print("\n5. A click means what is under it")
b = band()
b.label_set(2400.0)
b.zoom(0.5)                    # 1500 .. 3300 on 1000 pixels
a, z = b.window()
got = []
b.selected.connect(got.append)
QtWidgets.QApplication.sendEvent(b, QtGui.QMouseEvent(
    QtCore.QEvent.MouseButtonPress, QtCore.QPointF(500.0, 10.0),
    Qt.LeftButton, Qt.LeftButton, Qt.NoModifier))
check("the middle of the band is the middle of the section",
      got and abs(got[0] - (a + z) / 2) < 2.0, str(got))
check("and not the middle of the whole thing",
      got and abs(got[0] - LENGTH / 2) > 1.0, str(got))

print("\n6. The section follows the position")
b = band()
b.label_set(600.0)
b.zoom(0.5); b.zoom(0.5)       # 150 seconds wide... whatever it is
a0, z0 = b.window()
b.label_set(3000.0)            # far outside
a1, z1 = b.window()
check("it moves along", a1 > a0, "%.0f -> %.0f" % (a0, a1))
check("the position is inside again", a1 <= 3000.0 <= z1,
      "%.0f .. %.0f" % (a1, z1))
check("and the size stayed the same", abs((z1 - a1) - (z0 - a0)) < 1e-6)

print("\n7. New material starts over")
b = band()
b.label_set(600.0)
b.zoom(0.5)
b.set(CUT, {}, LENGTH)
check("the zoom is dropped", b.window() == (0.0, LENGTH), str(b.window()))

print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
