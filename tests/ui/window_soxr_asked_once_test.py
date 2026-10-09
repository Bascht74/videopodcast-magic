# -*- coding: utf-8 -*-
"""A finer ffmpeg is offered once per version, and never to a test run.

The box that offers an ffmpeg with soxr where this one has none,
opened offscreen. Its exec hands it to the test, which presses one of
its buttons; the settings, the install and what this machine has are
answered by the test. In order: a test run, a machine with no way to
a better build, and an ffmpeg that has soxr are offered nothing; then
the offer itself, written down before the answer, carry on and get it;
then the same version again. The quiet a test run keeps is lifted for
the offer alone, with every road out of the process stood in for.
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
import time
import the_program

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("VPM_SILENT", "1")
from PySide6 import QtWidgets
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


# Every road out of the process, answered here: what the machine has,
# the settings file, the install itself.
ui = vpm.ui
HOW = "a package manager"
have = {"way": True, "soxr": False, "asked": None}
kept, installs, boxes = [], [], []
plan = {"press": None}
ui.ffmpeg_can_be_had = lambda: have["way"]
ui.soxr_available = lambda: have["soxr"]
ui.settings = lambda: {"soxr-asked": have["asked"]} if have["asked"] else {}
ui.keep_setting = lambda key, value: kept.append((key, value))
ui.how_to_get_ffmpeg = lambda update=False: HOW
ui.install_watched = lambda *a: installs.append(a) or True


def exec_(box):
    """Write down what the box offers, and press the button planned."""
    buttons = [b.text() for b in box.buttons()]
    boxes.append({"buttons": buttons, "kept before": list(kept)})
    for b in box.buttons():
        if b.text() == plan["press"]:
            b.click()
    return 0


QtWidgets.QMessageBox.exec = exec_
window = QtWidgets.QWidget()
window.setAttribute(Qt.WA_DontShowOnScreen, True)
GET = vpm.T('Get it: %s') % HOW
ON = vpm.T('Carry on')


def offered(press=None, quiet=False):
    """soxr_offer as the window calls it; the quiet lifted unless *quiet*."""
    plan["press"] = press
    del boxes[:]
    del kept[:]
    del installs[:]
    held = os.environ.pop("VPM_SILENT", None)
    if quiet:
        os.environ["VPM_SILENT"] = "1"
    try:
        return ui.soxr_offer(window)
    finally:
        os.environ.pop("VPM_SILENT", None)
        if held is not None:
            os.environ["VPM_SILENT"] = held


print("1. Who is offered nothing")
took = offered(GET, quiet=True)
check("a test run is offered nothing",
      took is False and boxes == [] and kept == [],
      "took %r, %d boxes, kept %r" % (took, len(boxes), kept))
have["way"] = False
took = offered(GET)
check("a machine with no way to a better build is offered nothing",
      took is False and boxes == [],
      "took %r, %d boxes" % (took, len(boxes)))
have["way"], have["soxr"] = True, True
took = offered(GET)
check("an ffmpeg that has soxr is offered nothing",
      took is False and boxes == [],
      "took %r, %d boxes" % (took, len(boxes)))
have["soxr"] = False

print("\n2. The offer")
took = offered(ON)
check("an ffmpeg without soxr is offered a finer one, once",
      len(boxes) == 1 and boxes[0]["buttons"] == [GET, ON],
      "%d boxes, buttons %r against %r"
      % (len(boxes), boxes[0]["buttons"] if boxes else None, [GET, ON]))
check("the offer is written down for this version before the answer",
      bool(boxes) and boxes[0]["kept before"]
      == [("soxr-asked", vpm.VERSION)],
      "kept before the answer %r, wanted %r"
      % (boxes[0]["kept before"] if boxes else None,
         [("soxr-asked", vpm.VERSION)]))
check("Carry on gets nothing", took is False and installs == [],
      "took %r, installs %r" % (took, installs))
took = offered(GET)
check("Get it gets the finer ffmpeg where the window can be watched",
      took is True and installs == [(window, None, True)],
      "took %r, installs %r" % (took, installs))

print("\n3. The same version again")
have["asked"] = vpm.VERSION
took = offered(GET)
check("a version that was asked once is not asked again",
      took is False and boxes == [],
      "took %r, %d boxes" % (took, len(boxes)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
