# -*- coding: utf-8 -*-
"""A file added while the time axis is measured is measured too.

Where no file carries a timecode the window measures how the
recordings lie against each other, in a thread. A second request
arriving while that thread runs was dropped on the floor: the window
bowed out and nobody brought it back, so whoever added a file during
the measurement never got one covering it, and the answer that did
arrive was about the list without it.

The window is driven from outside, and the measurement itself is
replaced by a stand-in that writes down the list it was handed and
waits until it is let go -- so "while it runs" is a state the test
makes rather than a moment it hopes to hit.
"""
import os
import sys
import time
import wave
import shutil
import struct
import random
import tempfile
import threading
import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
os.environ["VPM_NO_SPEAKER_SPLIT"] = "1"
os.environ.pop("AUPHONIC_TOKEN", None)

from PySide6 import QtWidgets, QtCore

app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.update_offer = lambda *a, **k: None
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


PATIENCE = 60.0
POLL = 0.02

# ------------------------------------------------- the measurement, replaced
# Stricter than the real one in the point that matters: it hands back
# no axis at all, so nothing is stored and every request has to be
# measured afresh. What it does hand back is the list it was given.
measured = []
running = threading.Event()
let_go = threading.Event()


def measure_stand_in(paths, tc_of=None, HOP=5.0):
    measured.append([os.path.basename(p) for p in paths])
    running.set()
    let_go.wait(PATIENCE)
    return {}, ""


vpm.measure_time_axis = measure_stand_in

# ------------------------------------------------------------- the material
FOLDER = tempfile.mkdtemp(prefix="vpm_axisagain_")


def a_recording(name, seed):
    """Eight seconds of noise, as a recorder writes it -- and no timecode."""
    path = os.path.join(FOLDER, name)
    rng = random.Random(seed)
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(48000)
        f.writeframes(b"".join(
            struct.pack("<h", rng.randint(-6000, 6000))
            for _ in range(8 * 48000)))
    return path


FIRST = a_recording("Presenter_REC0001.wav", 5)
SECOND = a_recording("CoPresenter_REC0002.wav", 6)
LATE = a_recording("Guest_REC0003.wav", 7)
AT_FIRST = sorted(os.path.basename(p) for p in (FIRST, SECOND))
AFTERWARDS = sorted(os.path.basename(p) for p in (FIRST, SECOND, LATE))

to_add = [[FIRST, SECOND], [LATE]]
QtWidgets.QFileDialog.getOpenFileNames = staticmethod(
    lambda *a, **k: (to_add.pop(0) if to_add else [], ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok

_show = QtWidgets.QWidget.show


def offstage(self):
    self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
    _show(self)


QtWidgets.QWidget.show = offstage
QtWidgets.QDialog.show = offstage


def drawn(text):
    return str(text).replace("&&", "\x00").replace("&", "") \
                    .replace("\x00", "&")


def button_named(text):
    for b in app.allWidgets():
        if isinstance(b, QtWidgets.QPushButton) \
                and drawn(b.text()).strip() == text:
            return b
    return None


def waited_for(condition, why):
    """Wait on a condition, never on the clock; returns how long it took."""
    began_here = time.time()
    while time.time() - began_here < PATIENCE:
        app.processEvents()
        if condition():
            return time.time() - began_here
        time.sleep(POLL)
    print("      gave up after %.1f s waiting for %s" % (PATIENCE, why))
    return None


def drive():
    add = button_named(vpm.T('Add files ...'))
    if add is None:
        check("a measurement is begun over the files that are there",
              False, "no Add button on screen")
        app.quit()
        return
    add.click()
    took = waited_for(lambda: running.is_set(), "the first measurement")
    check("a measurement is begun over the files that are there",
          sorted(measured[0]) == AT_FIRST if measured else False,
          "%r against %r, after %s s"
          % (sorted(measured[0]) if measured else [], AT_FIRST, took))
    if not measured:
        let_go.set()
        app.quit()
        return

    # A file added while the thread is inside the stand-in: it cannot
    # have finished, because it is not let go until the line below.
    # Whether the window drops the running measurement and begins
    # afresh or keeps the request and asks again afterwards is its
    # own business -- what must not happen is that the request is lost.
    add.click()
    app.processEvents()
    let_go.set()
    took = waited_for(lambda: len(measured) > 1, "the measurement asked again")
    covered = sorted(measured[-1]) if len(measured) > 1 else []
    check("and it is caught up over the list with the new file in it",
          covered == AFTERWARDS,
          "%d measurement(s), the last over %r against %r, after %s s"
          % (len(measured), covered, AFTERWARDS, took))
    app.quit()


QtCore.QTimer.singleShot(2500, drive)
QtCore.QTimer.singleShot(180000, app.quit)
sys.argv = ["videopodcast_magic.py"]
try:
    vpm.gui()
finally:
    let_go.set()
    shutil.rmtree(FOLDER, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
