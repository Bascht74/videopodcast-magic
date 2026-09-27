# -*- coding: utf-8 -*-
"""The window's time axis is kept under the run's key, and taken back.

The window and the run build the axis's name in the stage store with
one function, so an axis either side measured is the other's. In order:
the key -- the order files come in changes nothing, a changed file, a
grouping of blocks or the phase way gives another; then the window,
driven from outside -- an axis kept under the key of the files added
is shown and written into the project file without a measurement, and
one the window measures is kept under the key of its files. The
measurement is a stand-in that writes down what it was handed.
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
import glob
import json
import random
import shutil
import struct
import tempfile
import time
import wave
import the_program

SCRIPT = the_program.SCRIPT
FOLDER = tempfile.mkdtemp(prefix="vpm_axiskept_")
os.environ["VPM_CACHE"] = os.path.join(FOLDER, "cache")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
os.environ["VPM_NO_SPEAKER_SPLIT"] = "1"

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
MEDIA = os.path.join(FOLDER, "media")
os.makedirs(MEDIA)


def a_recording(name, seed):
    """Eight seconds of noise, as a recorder writes it -- and no timecode."""
    path = os.path.join(MEDIA, name)
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
TAIL = a_recording("Presenter_REC0004.wav", 8)

#---------------------------------------------------------------- the key

print("the key")
key = vpm.axis_stage_key
same = key([FIRST, SECOND, LATE]) == key([LATE, FIRST, SECOND])
check("the order the files come in leaves the key as it is", same,
      "%s against %s" % (key([FIRST, SECOND, LATE]),
                         key([LATE, FIRST, SECOND])))
before = key([FIRST, TAIL, SECOND], {FIRST: [FIRST, TAIL]})
check("a grouping of the blocks gives another key",
      before != key([FIRST, TAIL, SECOND]), "both %s" % before)
check("the phase way on for a recording gives another key",
      before != key([FIRST, TAIL, SECOND], {FIRST: [FIRST, TAIL]}, [SECOND]),
      "both %s" % before)
st = os.stat(TAIL)
os.utime(TAIL, (st.st_atime, st.st_mtime + 7))
after = key([FIRST, TAIL, SECOND], {FIRST: [FIRST, TAIL]})
check("a file changed on disk gives another key", before != after,
      "both %s" % before)

#------------------------------------------------------------- the window

# What a run kept over the first two files: the second 2.5 s in.
KEPT = {"axis": {vpm.path_key(FIRST): 0.0, vpm.path_key(SECOND): 2.5},
        "clock": {vpm.path_key(FIRST): 1.0, vpm.path_key(SECOND): 1.0},
        "absolute": False, "weak": [], "no_place": [], "unplaceable": [],
        "brief": [], "clock_alone": []}
vpm.stage_put(key([FIRST, SECOND]), KEPT)
measured = []


def measure_stand_in(paths, tc_of=None, HOP=5.0, phase_of=None, raw=None):
    """An axis at once: each file a second and a half after the last."""
    measured.append(sorted(os.path.basename(p) for p in paths))
    ordered = sorted(paths, key=vpm.path_key)
    return ({"axis": dict((vpm.path_key(p), 1.5 * i)
                          for i, p in enumerate(ordered)),
             "clock": dict((vpm.path_key(p), 1.0) for p in ordered),
             "absolute": False, "weak": [], "no_place": [],
             "unplaceable": [], "brief": [], "clock_alone": []},
            vpm.T('time axis measured -- jumps land at the same point'))


vpm.measure_time_axis = measure_stand_in

to_add = [[FIRST, SECOND], [LATE]]
QtWidgets.QFileDialog.getOpenFileNames = staticmethod(
    lambda *a, **k: (to_add.pop(0) if to_add else [], ""))
# The project file the first answer writes is offered when the next
# file comes in; declined, so the list grows instead of being replaced.
vpm.say_dialog = lambda *a, **k: False
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


def kept_places():
    """The places the project file beside the material holds, by name."""
    for path in glob.glob(os.path.join(MEDIA, "videopodcast-magic_*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                rows = json.load(f).get("timeline") or []
        except (OSError, ValueError):
            continue
        return dict((os.path.basename(e["path"]), e.get("start_s"))
                    for e in rows)
    return {}


def drive():
    add = button_named(vpm.T('Add files ...'))
    if add is None:
        check("an axis the run kept reaches the project file unmeasured",
              False, "no Add button on screen")
        app.quit()
        return
    print("\nthe window")
    add.click()
    took = waited_for(lambda: kept_places(), "the project file's axis")
    places = kept_places()
    check("an axis the run kept reaches the project file unmeasured",
          places.get(os.path.basename(SECOND)) == 2.5 and not measured,
          "places %r, measured %r, after %s s" % (places, measured, took))
    add.click()
    wanted = key([FIRST, SECOND, LATE])
    took = waited_for(lambda: os.path.isfile(vpm.stage_file(wanted)),
                      "an entry under the three files' key")
    got = (vpm.stage_get(wanted) or {}).get("axis") or {}
    check("an axis the window measures is kept under the run's key",
          measured and sorted(got.values()) == [0.0, 1.5, 3.0],
          "kept %r after %s s, measured %r"
          % (sorted((os.path.basename(k), v) for k, v in got.items()),
             took, measured))
    app.quit()


QtCore.QTimer.singleShot(2500, drive)
QtCore.QTimer.singleShot(180000, app.quit)
sys.argv = ["videopodcast_magic.py"]
try:
    vpm.gui()
finally:
    shutil.rmtree(FOLDER, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
