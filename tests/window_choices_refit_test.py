# -*- coding: utf-8 -*-
"""The camera cut's drop-downs hold their longest entry in any font.

The drop-downs under the camera cut share one width. The window is
built, every such box is asked whether it holds what it offers, the
style sheet draws them in a font half as large again, and the same is
asked once more, with the shared width. Offscreen, so the style is not
the one a user sees; the font is what is changed.
"""
import os
import sys
import time
import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtGui, QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.update_offer = lambda *a, **k: None

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def boxes():
    """The camera cut's drop-downs: the ones offering a kind of shot."""
    out = []
    for w in app.allWidgets():
        if isinstance(w, QtWidgets.QComboBox) and any(
                w.itemData(i) in vpm.SHOT_NAMES for i in range(w.count())):
            out.append(w)
    return out


def short(box):
    """How many pixels the box lacks for its widest entry, frame and all."""
    return box.sizeHint().width() - box.width()


def reading():
    """Every box with its width and what it lacks, for a failure line."""
    return ", ".join("%r %d px lacking %d" % (
        max((b.itemText(i) for i in range(b.count())), key=len),
        b.width(), short(b)) for b in boxes())


n = [0]
rounds = [0]
state = {}


def step():
    i = n[0]
    if i == 0:
        if len(boxes()) < 2:
            rounds[0] += 1
            if rounds[0] < 100:
                QtCore.QTimer.singleShot(200, step)
                return
        print("1. As the window was built")
        check("the camera cut offers its drop-downs",
              len(boxes()) >= 2, "%d found" % len(boxes()))
        check("every cut drop-down holds its longest entry as built",
              bool(boxes()) and all(short(b) <= 0 for b in boxes()),
              reading() or "no drop-down to ask")
        if not boxes():
            app.quit()
            return
        # Through the style sheet, as the window's own looks are set:
        # a font handed to the application does not get past one.
        state["was"] = boxes()[0].font().pointSizeF()
        app.setStyleSheet(app.styleSheet() + "\nQComboBox { font-size: "
                          "%.1fpt; }" % (state["was"] * 1.5))
    elif i == 1:
        # Settled when the widths have stopped moving for five rounds.
        now = [b.width() for b in boxes()]
        if now != state.get("widths"):
            state["widths"], rounds[0] = now, 0
        rounds[0] += 1
        if rounds[0] < 5:
            QtCore.QTimer.singleShot(200, step)
            return
        print("\n2. With the font half as large again")
        check("every cut drop-down still holds its longest entry",
              bool(boxes()) and all(short(b) <= 0 for b in boxes()),
              "font %.1f pt, was %.1f pt: %s"
              % (boxes()[0].font().pointSizeF(), state["was"], reading()))
        check("and the cut drop-downs still share one width",
              len(set(b.width() for b in boxes())) == 1,
              reading())
        app.quit()
        return
    n[0] += 1
    rounds[0] = 0
    QtCore.QTimer.singleShot(200, step)


def deadline():
    """An outer brake only: the waiting inside is on the widths."""
    bad.append("the pass never finished: 120 s gone, at step %d" % n[0])
    app.quit()


QtCore.QTimer.singleShot(300, step)
brake = QtCore.QTimer()
brake.setSingleShot(True)
brake.timeout.connect(deadline)
brake.start(120000)
try:
    vpm.gui()
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("the window never came up: gui() fell over")
brake.stop()

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
