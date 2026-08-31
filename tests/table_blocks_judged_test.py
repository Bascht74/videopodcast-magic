# -*- coding: utf-8 -*-
"""A recording of several blocks must not wait for ever to be judged.

The channel rows come from the measurement over all the blocks and hang
on the row of the first one. A redraw asked for by any other block
therefore reached nothing, and the recording said "measurement running
..." with the work long done.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, shutil, sys, tempfile, time, wave
import numpy as np
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
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
            for w in tree.findChildren(QtWidgets.QCheckBox):
                if w.isVisible():
                    box = w
            check("a tick was found to click", box is not None)
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
def let_go_of(what):
    """Make every player let go of what it has open in there.

    Windows cannot delete a held file, and ignore_errors would hide the
    folder staying behind. Players are found by what they hold, not by
    which player they are, so a second holder cannot slip through. One
    that never started is not stopped: building what lies behind stop()
    waits for a lock a starting player holds. Returns what was let go.
    """
    what = os.path.realpath(what)
    let_go = []
    for top in app.topLevelWidgets():
        for x in top.findChildren(QtCore.QObject):
            if not (hasattr(x, "setSource") and hasattr(x, "source")):
                continue
            where = x.source()
            if not isinstance(where, QtCore.QUrl):
                continue
            where = where.toLocalFile()
            if not where:
                continue
            held = os.path.realpath(where)
            if held != what and not held.startswith(what + os.sep):
                continue
            state = getattr(x, "playbackState", None)
            state = state() if state is not None else None
            if state is not None and state != type(state).StoppedState:
                x.stop()
            x.setSource(QtCore.QUrl())
            let_go.append(os.path.basename(where))
    app.processEvents()
    return sorted(let_go)


def clean_up(what):
    """Close the window, then delete the folder, waiting for the grip.

    Let go, close, delete, in that order, and no ignore_errors: it would
    swallow the one thing that can go wrong, a folder that stays because
    something still holds it. The media backend closes the handle in a
    thread of its own, so the wait is on the handle and not on a fixed
    pause: up to ten seconds, after which what is left is named and does
    not turn the test red.
    """
    print("  let go of %s" % (", ".join(let_go_of(what)) or "nothing"))
    for top in app.topLevelWidgets():
        top.close()
    app.processEvents()
    clock = QtCore.QElapsedTimer()
    clock.start()
    while True:
        left = []
        try:
            shutil.rmtree(what)
        except OSError:
            for here, _, files in os.walk(what):
                left += [os.path.join(here, f) for f in files]
            left = left or ([what] if os.path.exists(what) else [])
        if not left or clock.elapsed() > 10000:
            break
        app.processEvents()
        QtCore.QThread.msleep(50)
    if left:
        print("  the folder stayed: %d still held after %.1f s, first %s"
              % (len(left), clock.elapsed() / 1000.0, left[0]))
    else:
        print("  the folder went away with the window, after %.1f s"
              % (clock.elapsed() / 1000.0))


sys.argv = ["videopodcast-magic.py"]
vpm.gui()
clean_up(folder)
# Here and nowhere else: a window that never got as far as the checks
# quits on the timer above, and this line is what says how few it made.
print("\n%d checks in %.2f s" % (judged, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
