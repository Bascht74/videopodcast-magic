# -*- coding: utf-8 -*-
"""Nothing in the window takes the picture full screen any more.

Full screen made trouble and is gone from every tab. A negative claim
needs a search at the place, not an empty one, so this asks both sides:
the source, where the four names that could ask for it would stand, and
the picture itself, which is sent the double click and the escape that
used to do it. Last, that no player carries the command by another name.
"""
import ast
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


def label(text, colour=None, bold=False, large=0):
    return QtWidgets.QLabel(text)


def hint(widget, text):
    widget.setToolTip(text)
    return widget


print("1. The four names that would ask for it")
# Read as a tree, not searched for as text: a name inside a comment or a
# catalogue entry is not a call, and a search over the text finds both.
source = the_program.text()
WORDS = ("setFullScreen", "showFullScreen", "isFullScreen",
         "WindowFullScreen")
spots = sorted((node.lineno, node.attr)
               for node in ast.walk(ast.parse(source))
               if isinstance(node, ast.Attribute) and node.attr in WORDS)
check("no line in the program asks a widget for full screen",
      not spots, "%d spots, the first %s" % (len(spots), spots[:3]))

print("\n2. The picture, sent what used to do it")
(WindowSlider, VideoSurface, Player, NoPlayer) = vpm.make_player_widgets(
    QtCore, QtGui, QtWidgets, Qt, label, hint,
    lambda *a, **k: None, lambda *a, **k: None, {})
player = Player()
player.resize(640, 480)
player.show()
app.processEvents()
picture = player.video
was = picture.size()
check("the picture stands in the window and not over the screen",
      not picture.isFullScreen() and was.height() > 0,
      "full screen %s, %d by %d"
      % (picture.isFullScreen(), was.width(), was.height()))

QtWidgets.QApplication.sendEvent(picture, QtGui.QMouseEvent(
    QtCore.QEvent.MouseButtonDblClick, QtCore.QPointF(5.0, 5.0),
    Qt.LeftButton, Qt.LeftButton, Qt.NoModifier))
app.processEvents()
check("a double click on the picture leaves it where it was",
      not picture.isFullScreen() and picture.size() == was,
      "full screen %s, %d by %d against %d by %d"
      % (picture.isFullScreen(), picture.size().width(),
         picture.size().height(), was.width(), was.height()))

QtWidgets.QApplication.sendEvent(picture, QtGui.QKeyEvent(
    QtCore.QEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier))
app.processEvents()
check("escape on the picture leaves it where it was",
      not picture.isFullScreen() and picture.size() == was,
      "full screen %s, %d by %d against %d by %d"
      % (picture.isFullScreen(), picture.size().width(),
         picture.size().height(), was.width(), was.height()))

print("\n3. No player keeps the command under another name")
CutPlayer = vpm.qt_cut_player(QtCore, QtGui, QtWidgets, Qt, QtMultimedia,
                              QtMultimediaWidgets, label, hint, vpm.COLOURS)
kept = [kind.__name__ for kind in (Player, NoPlayer, CutPlayer)
        if hasattr(kind, "large")]
check("no player carries a command that makes the picture large",
      not kept, "%d of 3 still do: %s" % (len(kept), kept))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
