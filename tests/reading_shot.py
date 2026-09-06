# -*- coding: utf-8 -*-
"""Shot of the whole window: which way round it reads, and in what language."""
import os, sys
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtWidgets, QtCore
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
OUT = os.environ.get("VPM_SHOTS") or os.path.join(HERE, "shots")
os.makedirs(OUT, exist_ok=True)
# The language is not set here. It comes out of the environment the way
# it does for somebody starting the program, so a catalogue that is not
# loaded shows up as a language that was not settled rather than as a
# direction nobody set.
WHICH = vpm.LANG
RIGHT = QtCore.Qt.RightToLeft


def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def button(text):
    for w in app.allWidgets():
        if (isinstance(w, QtWidgets.QPushButton)
                and w.text().strip().startswith(text)):
            return w


def way(widget):
    """Which way that widget reads, as one word."""
    return "right" if widget.layoutDirection() == RIGHT else "left"


def labels():
    """Print every label of the window that carries its own wording.

    The buttons that carry text rather than an icon, and every entry of
    every drop-down. Printed with repr(), because what this is about --
    the marks that settle a reading -- is invisible and would not
    survive the pipe otherwise. Nothing is judged here: the test lays
    each of them out and reads back what order they come in.
    """
    for w in app.allWidgets():
        if isinstance(w, QtWidgets.QToolButton) and w.text().strip():
            print("label %r" % w.text())
        if isinstance(w, QtWidgets.QComboBox):
            for i in range(w.count()):
                if w.itemText(i).strip():
                    print("label %r" % w.itemText(i))


n = [0]


def step():
    i = n[0]
    n[0] += 1
    try:
        if i == 0:
            win().resize(1180, 860)
            win().show()
            app.processEvents()
        elif i == 1:
            print("language", WHICH)
            print("app", way(app))
            print("window", way(win()))
            boxes = win().findChildren(QtWidgets.QGroupBox)
            print("box", way(boxes[0]) if boxes else "none")
            labels()
            win().grab().save("%s/reading_%s.png" % (OUT, WHICH))
            # The Settings window is the second one the program puts up,
            # and the only one a shot can reach without material: it
            # carries the language field this is all about.
            b = button(vpm.T('Settings ...'))
            if b is None:
                print("FAIL: no settings button in a %s window" % WHICH)
                app.quit()
                return
            QtCore.QTimer.singleShot(0, b.click)
        elif i == 3:
            for d in app.topLevelWidgets():
                if isinstance(d, QtWidgets.QDialog) and d.isVisible():
                    print("dialog", way(d))
                    d.grab().save("%s/reading_%s_settings.png" % (OUT, WHICH))
                    d.reject()
            print("done")
            app.quit()
            return
    except Exception:
        # In a Qt slot an exception goes nowhere: the loop carries on and
        # the run ends on a nought. So it is printed and the run stopped.
        import traceback
        traceback.print_exc()
        app.quit()
        return
    QtCore.QTimer.singleShot(900, step)


QtCore.QTimer.singleShot(900, step)
QtCore.QTimer.singleShot(45000, app.quit)
sys.argv = ["videopodcast_magic.py"]
vpm.gui()
