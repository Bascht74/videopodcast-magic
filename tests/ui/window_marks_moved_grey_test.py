# -*- coding: utf-8 -*-
"""A mark moved since the run greys Create Resolve project, and says why.

A handover beside three cameras names the window its run was cut to,
In +0:00:01 and Out +0:00:03. In order: the files added with no marks
set grey the button; the run's own marks make it usable; In moved
greys it with the reason and "press Start again", and the Resolve tab's
preview says the same instead of cutting; In put back frees it; Out
moved greys it with its own reason. The limit: the marks are set on
the window's model, where Mark In puts them, not through the player.
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
# installed: the button is grey without it whatever the marks say.
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
RUN_IN, RUN_OUT = "+0:00:01", "+0:00:03"
MOVED_IN, MOVED_OUT = "+0:00:02", "+0:00:02.5"
folder = tempfile.mkdtemp(prefix="vpm_moved_")


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

# As a run with the two marks writes it: cut to them, and naming them.
with open(os.path.join(folder, "Moved_resolve.json"), "w",
          encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "created_by": "test",
               "production": "Moved", "fps": 25, "fps_measured": 25.0,
               "drop_frame": False, "width": 160, "height": 90,
               "start_tc": None, "start_s": 1.0, "length_s": 2.0,
               "in_point": RUN_IN, "out_point": RUN_OUT,
               "cameras": [{"file": p, "source": p, "camera": n,
                            "track": n, "speakers": [],
                            "audio_tracks": [], "offset": 0.0,
                            "duration": 2.0, "fps": 25.0,
                            "wide_marked": False, "wide": False}
                           for p, n in zip(cams, ("Presenter", "Guest",
                                                  "WideCam"))],
               "cut": [], "speakers": [], "audio_files": {},
               "words": []}, f)

# The reasons as they have to read, from the two catalogue wordings.
IN_SAYS = vpm.T(
    'In point has changed since the last run: %s then, %s now. The cut '
    'and the sound inside the videos still belong to the old window, so '
    'Resolve would not get what the marks say now -- press Start again.')
OUT_SAYS = vpm.T(
    'Out point has changed since the last run: %s then, %s now. The cut '
    'and the sound inside the videos still belong to the old window, so '
    'Resolve would not get what the marks say now -- press Start again.')

QtWidgets.QFileDialog.getOpenFileNames = staticmethod(
    lambda *a, **k: ([audio] + cams, ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok


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


def resolve_button():
    """Create Resolve project, asked of every widget: the output sheet
    is not in the window while nothing has run."""
    for b in app.allWidgets():
        if isinstance(b, QtWidgets.QPushButton) and b.text().strip() \
                == vpm.T('Create Resolve project'):
            return b
    return None


def enabled():
    """Whether Create Resolve project can be pressed; None if absent."""
    b = resolve_button()
    return None if b is None else b.isEnabled()


def said():
    """What the grey button says: the tip of the wrapper it stands in."""
    b = resolve_button()
    up = None if b is None else b.parentWidget()
    return "" if up is None else up.toolTip()


def preview_says(text):
    """Whether a label on the Resolve tab shows exactly *text*."""
    sheet = win().resolve_sheet
    return any(x.text() == text
               for x in sheet.findChildren(QtWidgets.QLabel))


def marks(a, b):
    """Set In and Out where Mark In and Mark Out put them."""
    model = win().assignment_sheet.model
    model.in_point.set(a)
    model.out_point.set(b)


def ground():
    """One line with everything a judgement below rests on."""
    model = win().assignment_sheet.model
    return ("the button is %s, marks %r/%r, it says %r"
            % ({True: "usable", False: "grey", None: "not there"}[
                enabled()], model.in_point.get(), model.out_point.get(),
               said()[:70]))


n = [0]
rounds = [0]
over = set()


class NotYet(Exception):
    """The window has not caught up; wait and ask again."""


def waited_for(what, ok):
    """Wait on a condition, and give up into the judgement after 60 rounds.

    Given up, the check below still runs and says what never came.
    """
    if not ok and rounds[0] < 60:
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
                       enabled() is False and said().startswith(
                           IN_SAYS.split("%s")[0]))
            print("1. The files added, no marks set")
            check("marks cleared since the run leave the button grey",
                  enabled() is False
                  and said() == IN_SAYS % (RUN_IN, vpm.T('Beginning')),
                  ground())
            marks(RUN_IN, RUN_OUT)
        elif i == 2:
            waited_for("the button to come free", enabled() is True)
            print("\n2. The marks the run was cut to")
            check("the run's own marks leave Create Resolve project usable",
                  enabled() is True, ground())
            marks(MOVED_IN, RUN_OUT)
        elif i == 3:
            wanted = IN_SAYS % (RUN_IN, MOVED_IN)
            waited_for("the button to go grey, and the preview to say why",
                       enabled() is False and preview_says(wanted))
            print("\n3. In point moved")
            check("an In point moved since the run greys the button",
                  enabled() is False, ground())
            check("and the grey button says why, and to press Start again",
                  said() == wanted, ground())
            check("the Resolve tab's preview says the same, not a cut",
                  preview_says(wanted),
                  "no label on the Resolve tab reads %r" % wanted[:60])
            marks(RUN_IN, RUN_OUT)
        elif i == 4:
            waited_for("the button to come free again", enabled() is True)
            print("\n4. In point put back")
            check("In point put back frees the button again",
                  enabled() is True, ground())
            marks(RUN_IN, MOVED_OUT)
        elif i == 5:
            wanted = OUT_SAYS % (RUN_OUT, MOVED_OUT)
            waited_for("the button to go grey on Out", enabled() is False)
            print("\n5. Out point moved")
            check("an Out point moved greys it with its own reason",
                  enabled() is False and said() == wanted, ground())
            over.add("the pass")
            app.quit()
            return
        n[0] += 1
        rounds[0] = 0
        QtCore.QTimer.singleShot(300, step)
    except NotYet as why:
        rounds[0] += 1
        if rounds[0] > 80:
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
        bad.append("the pass never finished: 180 s gone, at step %d" % n[0])
        app.quit()


QtCore.QTimer.singleShot(500, step)
QtCore.QTimer.singleShot(180000, deadline)
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
