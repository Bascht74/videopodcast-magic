# -*- coding: utf-8 -*-
"""The Resolve button finds a handover where a run over the list put it.

No project is open and no output folder chosen, so a run writes beside
the videos, and a handover over exactly these cameras lies there. In
order: the files added take it up; a camera taken out greys the
button, and put back finds it again beside the videos; an output folder
chosen afterwards brings the one lying in it; and reset to beside the
videos, theirs comes back. Read off the button and off the search the
window makes, offscreen.
"""
PLATFORM_BOUND = True
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import wave
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import the_program

import numpy as np

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""


def answered(*a, **k):
    """Every dialog answered yes, but the offer of a project file.

    The window writes one beside the material, and opening it would
    replace the list this test builds.
    """
    return not (len(a) > 2 and a[2] == vpm.T('Project found'))


vpm.say_dialog = answered
# The builder has no Resolve, and this test is not about whether it is
# installed: the button is grey without it whatever the handover says.
vpm.resolve_installed = lambda: True

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


RATE, SEC = 48000, 4
folder = tempfile.mkdtemp(prefix="vpm_found_")
chosen = os.path.join(folder, "Chosen")
os.makedirs(chosen)


def tone(name, hz=300.0):
    """A recording of a plain tone, beside the cameras."""
    path = os.path.join(folder, name)
    t = np.arange(SEC * RATE) / float(RATE)
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes((0.4 * np.sin(2 * np.pi * hz * t) * 32767)
                      .astype("<i2").tobytes())
    return path


def clip(name):
    """A short camera file with picture and sound."""
    path = os.path.join(folder, name)
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                    "testsrc=size=160x90:rate=25:duration=%d" % SEC,
                    "-f", "lavfi", "-i",
                    "sine=frequency=440:duration=%d" % SEC,
                    "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
                    "yuv420p", "-c:a", "aac", "-shortest", "-y", path],
                   check=True)
    return path


audio = tone("A_speaker.wav")
cams = [clip(n) for n in ("B_Presenter.mov", "C_Guest.mov", "D_WideCam.mov")]
LEAVING = cams[2]
LENGTH = 240.0


def handover(where, production):
    """A handover over exactly the three cameras, written into *where*."""
    path = os.path.join(where, production + "_resolve.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"format": vpm.FILE_FORMAT, "created_by": "test",
                   "production": production, "fps": 25, "fps_measured": 25.0,
                   "drop_frame": False, "width": 160, "height": 90,
                   "start_tc": None, "start_s": 0.0, "length_s": LENGTH,
                   "cameras": [{"file": p, "source": p, "camera": n,
                                "track": n, "speakers": [],
                                "audio_tracks": [], "offset": 0.0,
                                "duration": LENGTH, "fps": 25.0,
                                "wide_marked": False, "wide": False}
                               for p, n in zip(cams, ("Presenter", "Guest",
                                                      "WideCam"))],
                   "cut": [], "speakers": [], "audio_files": {},
                   "words": []}, f)
    return path


BESIDE = handover(folder, "Beside")
CHOSEN = handover(chosen, "Chosen")

QtWidgets.QFileDialog.getOpenFileNames = staticmethod(
    lambda *a, **k: ([audio] + cams, ""))
QtWidgets.QFileDialog.getExistingDirectory = staticmethod(
    lambda *a, **k: chosen)
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok

# Read off the search itself: which handover the window took up, each
# time it asked.
found = []
_really_find = vpm.find_handover_file


def _watched(*places, **kw):
    """The window's search, with what it brought back noted."""
    got = _really_find(*places, **kw)
    found.append(got)
    return got


vpm.find_handover_file = _watched


def same(a, b):
    """Two paths the same file, however the platform spells them."""
    return bool(a) and bool(b) and os.path.normcase(os.path.normpath(a)) \
        == os.path.normcase(os.path.normpath(b))


def win():
    """The program's window."""
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def button(word):
    """The window's button whose text begins with *word*."""
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(word):
            return w


def enabled():
    """Whether Create Resolve project can be pressed; None if absent.

    Asked of every widget, not of the window's: the button stands on the
    output sheet, which is not in the window while nothing has run.
    """
    for b in app.allWidgets():
        if isinstance(b, QtWidgets.QPushButton) and b.text().strip() \
                == vpm.T('Create Resolve project'):
            return b.isEnabled()
    return None


def file_row(path):
    """The row of the file list that carries this file, or None."""
    name = os.path.basename(path)
    for t in win().findChildren(QtWidgets.QTreeWidget):
        if t.columnCount() < 3:
            continue
        stack = [t.invisibleRootItem()]
        while stack:
            item = stack.pop()
            if item.text(0).strip() == name:
                return t, item
            stack.extend(item.child(i) for i in range(item.childCount()))
    return None


def last_found():
    """The file the window's last search brought back, by name."""
    return os.path.basename(found[-1]) if found and found[-1] else None


def ground():
    """One line with everything a judgement below rests on."""
    return ("the button is %s, %s is %s the list, the searches brought "
            "back %s"
            % ({True: "usable", False: "grey", None: "not there"}[
                enabled()], os.path.basename(LEAVING),
               "in" if file_row(LEAVING) else "not in",
               [os.path.basename(x) if x else None for x in found[-4:]]))


n = [0]
rounds = [0]
over = set()


class NotYet(Exception):
    """The window has not caught up; wait and ask again."""


def waited_for(what, ok):
    """Wait on a condition, and give up into the judgement after 100 rounds.

    Given up, the check below still runs and says what never came.
    """
    if not ok and rounds[0] < 100:
        raise NotYet(what)


def step():
    """One step of the pass; each waits for the window, then judges."""
    i = n[0]
    try:
        if i == 0:
            if win() is None:
                raise NotYet("the window")
            win().show()
            win().resize(1400, 900)
            button(vpm.T('Add files ...')).click()
        elif i == 1:
            waited_for("the files and the handover beside them",
                       file_row(LEAVING) is not None and enabled() is True)
            print("1. The files added, next to each video file")
            check("the files added take up the handover beside the videos",
                  enabled() is True and same(found[-1] if found else "",
                                             BESIDE), ground())
            got = file_row(LEAVING)
            if got is None:
                raise NotYet("the camera in the file list")
            got[0].setCurrentItem(got[1])
            app.processEvents()
            button(vpm.T('Remove')).click()
        elif i == 2:
            waited_for("the camera to leave the list",
                       file_row(LEAVING) is None and enabled() is False)
            print("\n2. One camera taken out of the list")
            check("a camera taken out leaves Create Resolve project grey",
                  file_row(LEAVING) is None and enabled() is False,
                  ground())
            QtWidgets.QFileDialog.getOpenFileNames = staticmethod(
                lambda *a, **k: ([LEAVING], ""))
            button(vpm.T('Add files ...')).click()
        elif i == 3:
            waited_for("the camera to come back with the handover",
                       file_row(LEAVING) is not None and enabled() is True)
            print("\n3. The camera put back")
            check("the camera put back finds the handover beside the videos",
                  file_row(LEAVING) is not None and enabled() is True
                  and last_found() == "Beside_resolve.json", ground())
            button(vpm.T('Output folder ...')).click()
        elif i == 4:
            waited_for("the chosen folder's handover",
                       enabled() is True
                       and last_found() == "Chosen_resolve.json")
            print("\n4. An output folder chosen after the files")
            check("an output folder chosen afterwards brings its handover",
                  enabled() is True and same(found[-1] if found else "",
                                             CHOSEN), ground())
            button(vpm.T('reset')).click()
        elif i == 5:
            waited_for("the handover beside the videos again",
                       enabled() is True
                       and last_found() == "Beside_resolve.json")
            print("\n5. The output folder reset to beside the videos")
            check("the folder reset brings the handover beside the videos",
                  enabled() is True and same(found[-1] if found else "",
                                             BESIDE), ground())
            over.add("the pass")
            app.quit()
            return
        n[0] += 1
        rounds[0] = 0
        QtCore.QTimer.singleShot(300, step)
    except NotYet as why:
        rounds[0] += 1
        if rounds[0] > 120:
            bad.append("step %d waited for %s and it never came -- %s"
                       % (i, why, ground() if win() else "no window"))
            over.add("the pass")
            app.quit()
            return
        QtCore.QTimer.singleShot(300, step)
    except Exception:
        import traceback
        traceback.print_exc()
        bad.append("step %d fell over" % i)
        over.add("the pass")
        app.quit()


def deadline():
    """An outer brake only: the waiting inside is on rounds of 300 ms."""
    if "the pass" not in over:
        bad.append("the pass never finished: 240 s gone, at step %d" % n[0])
        app.quit()


QtCore.QTimer.singleShot(500, step)
QtCore.QTimer.singleShot(240000, deadline)
try:
    vpm.gui()
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("the window never came up: gui() fell over")

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
