# -*- coding: utf-8 -*-
"""Shot of the assignment table after it moved onto its own tab."""
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtWidgets, QtCore
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
sys.path.insert(0, HERE)
from fixture_project import fixture_project
PROJECT, SRC = fixture_project("assignshot")
OUT = os.environ.get("VPM_SHOTS") or os.path.join(HERE, "shots"); os.makedirs(OUT, exist_ok=True)
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
def button(t):
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(t): return w
def tab(s):
    """Switch to the sheet whose title contains *s*, or stop.

    Silence here would mean photographing the wrong sheet with a return
    code of 0 -- see the same function in preview_shot.py.
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


def hold(ok, ms=150, limit=120):
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


def table_text():
    """What the visible tables hold, cell by cell."""
    out = []
    for tb in win().findChildren(QtWidgets.QTableWidget):
        if not tb.isVisible():
            continue
        cells = []
        for r in range(tb.rowCount()):
            for c in range(tb.columnCount()):
                w = tb.cellWidget(r, c)
                if isinstance(w, QtWidgets.QComboBox):
                    cells.append(w.currentText())
                elif isinstance(w, QtWidgets.QLineEdit):
                    cells.append(w.text())
                else:
                    it = tb.item(r, c)
                    cells.append(it.text() if it else "")
        out.append((tb.rowCount(), cells))
    return out


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
    """Everything the picture and the printout need is done.

    Three things at once, and each of them was measured: every visible
    table has rows; nothing runs in the background any more -- the time
    axis is measured in a thread and only its end writes the timecode
    column, and the prework bar stands in the picture while the
    envelopes are read; and the tables read the same twice in a row, so
    nothing arrives late.
    """
    now = table_text()
    was, before[0] = before[0], now
    return (bool(now) and all(rows for rows, _ in now) and now == was
            and not showing(vpm.T('Measuring time axis ...'))
            and not working())


def step():
    i = n[0]; n[0] += 1
    try:
        if i == 0:
            if hold(win() is not None, 100, 100): return
            win().show(); win().resize(1500, 1050); app.processEvents()
        elif i == 1:
            if hold(button(vpm.T('Open project ...')[:8]) is not None): return
            button(vpm.T('Open project ...')[:8]).click()
        elif i == 2:
            # The tick only wakes up once the project is loaded: that is
            # what the pause here used to sit out.
            multitrack = vpm.T('Multitrack (one track per speaker)')
            boxes = [cb for cb in win().findChildren(QtWidgets.QCheckBox)
                     if cb.text().startswith(multitrack)]
            if hold(any(cb.isEnabled() for cb in boxes)): return
            for cb in boxes:
                if cb.isEnabled():
                    cb.setChecked(True)
        elif i == 3:
            if hold(built()): return
            tab(vpm.T('Assignment && time window')[:9])
        elif i == 4:
            if hold(ready(), 150, 240): return
            app.processEvents()
            win().grab().save(OUT + "/assignment.png")
            for tb in win().findChildren(QtWidgets.QTableWidget):
                if not tb.isVisible(): continue
                head = [tb.horizontalHeaderItem(c).text()
                        for c in range(tb.columnCount())]
                print("Table:", " | ".join(head))
                for r in range(tb.rowCount()):
                    row = []
                    for c in range(tb.columnCount()):
                        w = tb.cellWidget(r, c)
                        if isinstance(w, QtWidgets.QComboBox):
                            row.append("[%s]" % w.currentText())
                        elif isinstance(w, QtWidgets.QLineEdit):
                            row.append(w.text())
                        else:
                            it = tb.item(r, c)
                            row.append(it.text() if it else "")
                    print("   " + " | ".join(row))
            print("\ndone"); app.quit(); return
    except Exception:
        import traceback; traceback.print_exc(); app.quit(); return
    QtCore.QTimer.singleShot(50, step)

QtCore.QTimer.singleShot(50, step)
QtCore.QTimer.singleShot(60000, app.quit)
sys.argv = ["videopodcast-magic.py"]
vpm.gui()
