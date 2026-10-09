# -*- coding: utf-8 -*-
"""The empty file list takes files dragged onto it, and only files.

The drop area the window shows while no file is listed, built on its
own offscreen and sent Qt's own drag and drop events. In order: a drag
carrying files is taken and lights the border, a drag carrying text is
not; leaving puts the border back; a drop hands on the local files and
leaves web addresses out, and a drop of web addresses alone hands on
nothing. The limit: the events are made here, not by a mouse.
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
import tempfile
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


FOLDER = tempfile.mkdtemp(prefix="vpm_drop_")
CAMERA = os.path.join(FOLDER, "WideCam_C001.mp4")
SOUND = os.path.join(FOLDER, "Presenter_REC0001.wav")
WEB = "https://example.invalid/Guest_B002.mp4"

handed = []
DropArea = vpm.make_drop_area(QtCore, QtGui, QtWidgets)
area = DropArea(lambda paths: handed.append(list(paths)), lambda: None,
                lambda: None, vpm.COLOURS)
area.setAttribute(Qt.WA_DontShowOnScreen, True)
area.resize(640, 320)
area.show()
app.processEvents()
LIT = vpm.COLOURS["heading"]
PLAIN = vpm.COLOURS["frame"]


def carrying(urls=(), text=None):
    data = QtCore.QMimeData()
    if urls:
        data.setUrls([QtCore.QUrl(u) if "://" in u
                      else QtCore.QUrl.fromLocalFile(u) for u in urls])
    if text is not None:
        data.setText(text)
    return data


def enter(data):
    """A drag coming in over the middle; True if the area took it."""
    e = QtGui.QDragEnterEvent(QtCore.QPointF(320, 160), Qt.CopyAction, data,
                              Qt.LeftButton, Qt.NoModifier)
    e.ignore()
    QtWidgets.QApplication.sendEvent(area, e)
    return e.isAccepted()


def drop(data):
    e = QtGui.QDropEvent(QtCore.QPointF(320, 160), Qt.CopyAction, data,
                         Qt.LeftButton, Qt.NoModifier)
    e.ignore()
    QtWidgets.QApplication.sendEvent(area, e)
    return e.isAccepted()


def same(path):
    """A path spelt the way Windows and Qt can both be held against.

    Qt hands a local file back with forward slashes and may change the
    case of the drive letter; a spelling is not a fault.
    """
    return os.path.normcase(os.path.normpath(path))


def border():
    """Which of the two border colours the area is drawn in now."""
    sheet = area.styleSheet()
    return "lit" if LIT in sheet else "plain" if PLAIN in sheet else sheet


try:
    print("1. A drag coming in")
    check("the area starts with the plain border", border() == "plain",
          "border %r" % border())
    took = enter(carrying(text="Guest_B002.mp4"))
    check("a drag carrying only text is not taken",
          not took and border() == "plain",
          "taken %s, border %r" % (took, border()))
    took = enter(carrying([CAMERA, SOUND]))
    check("a drag carrying files is taken and lights the border",
          took and border() == "lit",
          "taken %s, border %r" % (took, border()))

    print("\n2. A drag leaving")
    QtWidgets.QApplication.sendEvent(area, QtGui.QDragLeaveEvent())
    check("leaving puts the plain border back", border() == "plain",
          "border %r" % border())

    print("\n3. A drop")
    enter(carrying([CAMERA, WEB, SOUND]))
    took = drop(carrying([CAMERA, WEB, SOUND]))
    check("a drop hands on the local files and leaves web addresses out",
          [[same(p) for p in paths] for paths in handed]
          == [[same(CAMERA), same(SOUND)]],
          "handed on %r, wanted [[%r, %r]]" % (handed, CAMERA, SOUND))
    check("a drop puts the plain border back and is taken",
          took and border() == "plain",
          "taken %s, border %r" % (took, border()))
    del handed[:]
    enter(carrying([WEB]))
    took = drop(carrying([WEB]))
    check("a drop of web addresses alone hands on nothing",
          handed == [] and not took,
          "handed on %r, taken %s" % (handed, took))
finally:
    area.close()
    os.rmdir(FOLDER)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
