# -*- coding: utf-8 -*-
"""A recording of several blocks must not wait for ever to be judged.

The channel rows come from the measurement over all the blocks and hang
on the row of the first one. A redraw asked for by any other block
therefore reached nothing, and the recording said "measurement running
..." with the work long done.
"""
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import the_program
from let_go import clean_up
SCRIPT = the_program.SCRIPT
import sys, tempfile, time, wave
import numpy as np
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""

began = time.time()
# Not "done": that name belongs to the function below, which stops the
# run, and a counter under it would end this file in a traceback where
# a verdict should stand.
judged = 0
bad = []


def check(name, ok, extra=""):
    global judged
    judged += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


RATE, SEC, CH = 48000, 5, 24
folder = tempfile.mkdtemp(prefix="vpm_blockrows_")


def block(name):
    """A mixer file: a stereo pair, two microphones, the rest unused."""
    t = np.arange(RATE * SEC) / float(RATE)
    rows = []
    for c in range(CH):
        if c in (0, 1):
            rows.append(0.4 * np.sin(2 * np.pi * 300 * t))
        elif c == 2:
            rows.append(0.4 * np.sin(2 * np.pi * 800 * t))
        elif c == 3:
            rows.append(0.4 * np.sin(2 * np.pi * 1900 * t))
        else:
            rows.append(np.zeros_like(t))
    x = (np.stack(rows, axis=1) * 32767).astype("<i2")
    path = os.path.join(folder, name)
    with wave.open(path, "wb") as f:
        f.setnchannels(CH); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes(x.tobytes())
    return path


# Five seconds apart on the clock in the name, five seconds long: the
# second block continues the first, so the two are one recording.
FILES = [block("r_260808_185628.wav"), block("r_260808_185633.wav")]
QtWidgets.QFileDialog.getOpenFileNames = staticmethod(
    lambda *a, **k: (FILES, ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted


def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def channel_rows():
    out = []
    for t in win().findChildren(QtWidgets.QTreeWidget):
        it = QtWidgets.QTreeWidgetItemIterator(t)
        while it.value():
            x = it.value()
            if (x.data(0, QtCore.Qt.UserRole + 2) or "") == "channel":
                out.append((x.text(0).strip(), x.text(2)))
            it += 1
    return out


n = [0]
waited = [0]


def done():
    """Nothing more to ask. The verdict stands at the foot of the file."""
    app.quit()


def after_tick(was, bar):
    app.processEvents()
    check("the list stayed where it was", abs(bar.value() - was) <= 2,
          "%d, was %d" % (bar.value(), was))
    done()


def step():
    i = n[0]; n[0] += 1
    try:
        if i == 0:
            win().show(); win().resize(1200, 800); app.processEvents()
            for w in win().findChildren(QtWidgets.QPushButton):
                if "add files" in w.text().lower():
                    w.click()
                    break
        else:
            rows = channel_rows()
            still = [r for r in rows if "..." in r[1] or "not measured" in r[1]]
            if (not rows or still) and waited[0] < 30:
                waited[0] += 1; n[0] = 1
                QtCore.QTimer.singleShot(2000, step); return
            print("   rows: %s" % rows[:3])
            check("the recording was judged, not left waiting",
                  bool(rows) and not still, str(rows[:2]))
            check("one row per channel", len(rows) == CH, str(len(rows)))
            check("the pair was found",
                  any("one stereo track" in r[1] for r in rows), str(rows))
            check("the unused inputs are named",
                  sum(1 for r in rows if "unused" in r[1]) == CH - 4,
                  str(len([1 for r in rows if "unused" in r[1]])))
            print("\n2. A tick does not throw the list back to the top")
            # Ticking a channel replaces every row under the file. The
            # list would otherwise jump to the top at every click, and
            # on a mixer file that means hunting for the place again.
            tree = win().findChildren(QtWidgets.QTreeWidget)[0]
            tree.expandAll()
            # Small enough that two dozen channels do not fit: without a
            # scrollbar there is no position to lose.
            win().resize(1000, 420); app.processEvents()
            bar = tree.verticalScrollBar()
            check("the list is long enough to scroll", bar.maximum() > 0,
                  str(bar.maximum()))
            bar.setValue(bar.maximum()); app.processEvents()
            was = bar.value()
            box = None
            boxes = tree.findChildren(QtWidgets.QCheckBox)
            for w in boxes:
                if w.isVisible():
                    box = w
            check("a tick was found to click", box is not None,
                  "%d ticks in the list, %d of them visible"
                  % (len(boxes), sum(1 for w in boxes if w.isVisible())))
            if box is not None and was:
                box.setChecked(not box.isChecked())
                app.processEvents()
                QtCore.QTimer.singleShot(1500, lambda: after_tick(was, bar))
                return
            done()
            return
    except Exception:
        import traceback; traceback.print_exc()
        bad.append("crash"); app.quit(); return
    QtCore.QTimer.singleShot(2000, step)


QtCore.QTimer.singleShot(800, step)
QtCore.QTimer.singleShot(150000, app.quit)
sys.argv = ["videopodcast_magic.py"]
vpm.gui()
clean_up(folder)
# Here and nowhere else: a window that never got as far as the checks
# quits on the timer above, and this line is what says how few it made.
print("\n%d checks in %.2f s" % (judged, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
