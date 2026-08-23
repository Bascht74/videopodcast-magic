# -*- coding: utf-8 -*-
"""Shots of the Resolve cut tab -- tables, speaker box, player."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import sys, importlib.util
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("VPM_SILENT", "1")   # never beep at a person
from PySide6 import QtWidgets, QtCore
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
# No network and no real key for a screenshot: the two functions the
# interface would call for that are stubbed out. (list_presets returns
# (name, uuid, multitrack) triples; load_api_key returns the stored key.)
vpm.list_presets = lambda key: [("Podcast_Multitrack", "u1", True),
                                ("Podcast_Zoom", "u2", False)]
vpm.load_api_key = lambda: "not-a-real-key"
sys.path.insert(0, HERE)
from fixture_project import fixture_project
PROJECT, SRC = fixture_project("previewshot")
OUT = os.environ.get("VPM_SHOTS") or os.path.join(HERE, "shots")
os.makedirs(OUT, exist_ok=True)
if PROJECT is None:
    print("SKIPPED: no test media -- point VPM_MEDIA at a folder "
          "holding videopodcast-magic_Interview_2.json")
    raise SystemExit(0)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (PROJECT, ""))

def win():
    for x in app.topLevelWidgets():
        if x.windowTitle().startswith("Video Podcast"):
            return x

def button(text):
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(text):
            return w

def group(title):
    for w in win().findChildren(QtWidgets.QGroupBox):
        if w.title().startswith(title):
            return w

def shot(name, w=None):
    f = win(); f.resize(1600, 1150); app.processEvents()
    (w or f).grab().save(os.path.join(OUT, name + ".png"))
    print("  ->", name)

def tab(s):
    """Switch to the sheet whose title contains *s*.

    It used to return in silence where nothing matched, and the script
    then carried on photographing the wrong sheet -- with a return code
    of 0, so nothing anywhere went red. When the tab names lost their
    numbers on 23.8.2026 that is exactly what happened. A lookup that
    finds nothing is a defect, and says so.
    """
    for tw in win().findChildren(QtWidgets.QTabWidget):
        for k in range(tw.count()):
            if s.lower() in tw.tabText(k).lower():
                tw.setCurrentIndex(k); app.processEvents(); return
    named = [tw.tabText(k) for tw in win().findChildren(QtWidgets.QTabWidget)
             for k in range(tw.count())]
    raise SystemExit("FAIL: no sheet is called %r. There are: %s"
                     % (s, named))

n = [0]
waited = [0]
before = [None]


def hold(ok, ms=150, limit=200):
    """Wait for a condition instead of waiting for the clock.

    The step comes back every <ms> milliseconds until <ok> is true, at
    most <limit> times -- more than ten times the pause that stood here
    before, so a slow machine only takes longer and is not called red,
    while an interface that never gets there still gives up.
    """
    if ok or waited[0] >= limit:
        waited[0] = 0
        return False
    waited[0] += 1
    n[0] -= 1
    QtCore.QTimer.singleShot(ms, step)
    return True


def showing(text):
    """Is a line beginning with that text on the screen?"""
    return any(w.isVisible() and w.text().startswith(text)
               for w in win().findChildren(QtWidgets.QLabel))


def built():
    """The tables are there and hold rows -- the project is in."""
    return any(tb.rowCount() > 0
               for tb in win().findChildren(QtWidgets.QTableWidget))


def fetching():
    """A still out of a video file is on its way.

    The player fetches the picture it shows in a thread. Taking the
    shot before it arrives would photograph the picture from before.
    """
    return any(getattr(w, "_still_running", False)
               for w in win().findChildren(QtWidgets.QWidget))


def working():
    """A bar in the window says something is still running.

    The prework bar stands there while the envelopes are read, the
    footer bar while anything runs -- and after that it stays full for
    another second and a half so that the end is seen, before it goes
    away by itself. Both are in the picture, so the shot waits until
    they have gone.
    """
    return any(b.isVisible()
               for b in win().findChildren(QtWidgets.QProgressBar))


def ready():
    """Everything the pictures and the printout need is done.

    Both boxes stand on the screen, the time axis is measured -- it
    runs in a thread and moves the player when it lands -- no still is
    on its way, and the boxes measure the same twice in a row, so the
    layout has come to rest.
    """
    boxes = [group(vpm.T('Speaker')), group(vpm.T('Camera cut -- preview'))]
    now = [(b.isVisible(), b.height(), b.width()) if b else None
           for b in boxes]
    was, before[0] = before[0], now
    return (all(b is not None and b.isVisible() for b in boxes)
            and now == was and not fetching()
            and not showing(vpm.T('Measuring time axis ...'))
            and not working())


def step():
    i = n[0]; n[0] += 1
    try:
        if i == 0:
            if hold(win() is not None, 100, 120): return
            win().show(); app.processEvents()
        elif i == 1:
            k = button(vpm.T('Open project ...')[:8])
            if hold(k is not None): return
            print("Load button:", bool(k)); k.click()
        elif i == 2:
            # The tick only wakes up once the project is loaded: that is
            # what the pause here used to sit out.
            multitrack = vpm.T('Multitrack (one track per speaker)')
            boxes = [cb for cb in win().findChildren(QtWidgets.QCheckBox)
                     if cb.text().startswith(multitrack)]
            if hold(any(cb.isEnabled() for cb in boxes)): return
            for cb in boxes:
                print("Multitrack:", cb.isEnabled(), cb.isChecked())
                if cb.isEnabled() and not cb.isChecked():
                    cb.setChecked(True)
        elif i == 3:
            if hold(built()): return
            tab(vpm.T('Resolve cut'))
        elif i == 4:
            if hold(ready(), 150, 250): return
            shot("A_tab")
            # The name of the picture stays English, the lookup does not:
            # the window carries the translated title.
            for name, title in (("Speaker", vpm.T('Speaker')),
                                ("Camera",
                                 vpm.T('Camera cut -- preview'))):
                gb = group(title)
                if gb:
                    shot("B_" + name, gb)
                    print(name, "height", gb.height(),
                          "width", gb.width())
            for tb in win().findChildren(QtWidgets.QTableWidget):
                if tb.isVisible():
                    print("Table", tb.horizontalHeaderItem(0).text(),
                          "widths", [tb.columnWidth(c)
                                     for c in range(tb.columnCount())],
                          "Viewport", tb.viewport().width())
            print("\ndone"); app.quit(); return
    except Exception as e:
        import traceback; traceback.print_exc(); app.quit(); return
    QtCore.QTimer.singleShot(50, step)

QtCore.QTimer.singleShot(50, step)
QtCore.QTimer.singleShot(60000, app.quit)
sys.argv = ["videopodcast-magic.py"]
vpm.gui()
