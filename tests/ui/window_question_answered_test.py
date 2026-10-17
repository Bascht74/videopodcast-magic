# -*- coding: utf-8 -*-
"""A run's question reaches the window, and the run gets the answer chosen.

The road a run takes when it has to ask: a worker thread asks, the
question crosses into the window's thread as a signal, the window puts
up its dialog, and the worker waits until the answer is in. The dialog
is stood in for, offscreen: its exec hands it to the test, which picks
an answer as a user would and presses Continue or shuts it. In order:
what the dialog offers, and that the first answer stands chosen; then
Continue as it stands, another answer chosen, and the dialog shut,
each answered to the waiting thread.
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
import threading
import time
import the_program

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("VPM_SILENT", "1")
from PySide6 import QtCore, QtWidgets
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


# The answers, as a run writes them: the second spread over two lines.
POSSIBLE = [("skip", "Leave this file out"),
            ("join", "Join it to the one before,\n      as one recording")]
OFFERED = ["Leave this file out",
           "Join it to the one before, as one recording"]
TITLE = "Presenter_REC0002.wav"

# What the stood-in dialog does when it is put up: write down what it
# offers, pick an answer, and press Continue or shut it.
seen = []
plan = {"pick": None, "shut": False}


def exec_(dialog):
    radios = dialog.findChildren(QtWidgets.QRadioButton)
    seen.append({"title": dialog.windowTitle(),
                 "offered": [r.text() for r in radios],
                 "checked": [r.text() for r in radios if r.isChecked()],
                 "said": [w.text() for w in
                          dialog.findChildren(QtWidgets.QLabel)]})
    if plan["shut"]:
        return QtWidgets.QDialog.Rejected
    for r in radios:
        if r.text() == plan["pick"]:
            r.setChecked(True)
    return QtWidgets.QDialog.Accepted


QtWidgets.QDialog.exec = exec_
window = QtWidgets.QWidget()
window.setAttribute(Qt.WA_DontShowOnScreen, True)
bridge = vpm.ui.Bridge()
ask_user = vpm.ui.running.user_asker(window, bridge,
                          lambda signal, *values: signal.emit(*values))


def asked(pick=None, shut=False):
    """Ask from a worker thread; the answer, or a note that none came."""
    plan["pick"], plan["shut"] = pick, shut
    got = []
    worker = threading.Thread(
        target=lambda: got.append(ask_user(POSSIBLE, TITLE)), daemon=True)
    worker.start()
    wall = time.time()
    while worker.is_alive() and time.time() - wall < 30:
        app.processEvents()
        worker.join(0.02)
    return got[0] if got else "no answer after %.0f s" % (time.time() - wall)


print("1. What the dialog offers")
answer = asked()
first = seen[0] if seen else {}
check("the question reaches the window as one dialog",
      len(seen) == 1, "%d dialogs put up" % len(seen))
said = vpm.T('%s -- what should happen with it?\nThe details are in the '
             'log.') % TITLE
check("the dialog names what it asks about",
      first.get("title") == TITLE and first.get("said") == [said],
      "title %r, said %r" % (first.get("title"), first.get("said")))
check("the dialog offers every answer, each on one line",
      first.get("offered") == OFFERED,
      "%r against %r" % (first.get("offered"), OFFERED))
check("the first answer stands chosen when the dialog opens",
      first.get("checked") == OFFERED[:1],
      "%r chosen, wanted %r" % (first.get("checked"), OFFERED[:1]))

print("\n2. What the run gets back")
check("Continue as it stands answers the first",
      answer == "skip", "%r against 'skip'" % (answer,))
answer = asked(pick=OFFERED[1])
check("another answer chosen is the one the run gets",
      answer == "join", "%r against 'join'" % (answer,))
answer = asked(shut=True)
check("a dialog shut without Continue tells the run to stop",
      answer == "abort", "%r against 'abort'" % (answer,))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
