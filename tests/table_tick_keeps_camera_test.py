# -*- coding: utf-8 -*-
"""The Multitrack tick neither bars a camera choice nor clears one.

Which camera a recording belongs to is the same question with the tick
and without it, and the run answers it from the assignment file either
way. The tick used to decide both: with it off the column held a grey
sentence instead of a chooser, and every click on it -- in either
direction -- threw the hand-made choice away and wrote "no camera of
its own" into the project, where it stayed for good.

Two windows in one process. The first adds the material with the tick
off, picks a camera in the column, clicks the tick on and off again and
closes; the second opens what was written. What this cannot show is
whether the run then cuts to that camera -- cut_voice_on_its_camera
asks that.
"""
import os
import time
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import json, shutil, subprocess, sys, tempfile, wave
import numpy as np
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
# The window is closed further down, which is how the program writes the
# project file; the last window closing would otherwise take the
# application with it before anything is read back.
app.setQuitOnLastWindowClosed(False)
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.update_offer = lambda *a, **k: None
vpm.say_dialog = lambda *a, **k: True     # no dialog waits for anybody

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


RATE = 48000
folder = tempfile.mkdtemp(prefix="vpm_tick_")
out_folder = os.path.join(folder, "Ergebnis")
os.makedirs(out_folder, exist_ok=True)

# The row that is driven, and the camera it is put on. Neither name
# resembles the other: the row is left without a speaker name, so the
# program derives no camera at all and whatever is picked is a real
# choice by hand -- which is the only kind the project file stores.
DRIVEN = "CoPresenter_REC00018.wav"
OTHER = "Presenter_REC00021.wav"
WIDE = "WideCam_01011855_C001.mov"
TARGET = "GuestCam_01011858_C003.mov"


def tone(name, hz=300.0, seconds=6.0):
    path = os.path.join(folder, name)
    t = np.arange(int(seconds * RATE)) / float(RATE)
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes((0.4 * np.sin(2 * np.pi * hz * t) * 32767)
                      .astype("<i2").tobytes())
    return path


def camera(name, seconds=6):
    path = os.path.join(folder, name)
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                    "smptebars=size=160x90:rate=25:duration=%d" % seconds,
                    "-f", "lavfi", "-i",
                    "sine=frequency=300:duration=%d" % seconds,
                    "-c:v", "libx264", "-preset", "ultrafast",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
                    "-y", path], check=True)
    return path


ALL = [tone(DRIVEN, 420.0), tone(OTHER, 300.0), camera(WIDE),
       camera(TARGET)]

adding = list(ALL)
QtWidgets.QFileDialog.getOpenFileNames = staticmethod(
    lambda *a, **k: (list(adding), ""))
QtWidgets.QFileDialog.getExistingDirectory = staticmethod(
    lambda *a, **k: out_folder)
project_path = [""]
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (project_path[0], ""))
# Nothing may sit and wait for a click: a modal window would hold the
# test until the suite kills it.
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok


# Closing a window does not destroy it: it stays a widget of the top
# rank carrying the same title, so from the second pass on two answer to
# that name. Which of them comes first is a hash order Qt seeds afresh in
# every process, and picking by title then decides nothing the test can
# see. Measured over twelve copies side by side: six read the first
# pass's window all through the second one -- green, and proving nothing,
# because that window already stood on the picked camera; five read the
# new one; and one changed its mind between two steps and went red. So
# the window is chosen once per pass and kept, and the window of a pass
# that is over is put aside by its identity rather than by its title.
held = [None]
put_aside = []


def win():
    """The window of this pass -- chosen once, then kept."""
    if held[0] is None:
        for x in app.topLevelWidgets():
            if ("Video Podcast Magic" in x.windowTitle()
                    and not any(x is old for old in put_aside)):
                held[0] = x
                break
    return held[0]


def pass_over():
    """This pass is done: the next one may not find its window."""
    if held[0] is not None:
        put_aside.append(held[0])
        held[0] = None


def button(text):
    top = win()
    for w in ((top.findChildren(QtWidgets.QPushButton)
               + top.findChildren(QtWidgets.QCheckBox)) if top else []):
        if w.text().strip().startswith(text):
            return w


def multitrack_tick():
    """The Multitrack checkbox, by the wording it carries."""
    return button(vpm.T('Multitrack (one track per speaker)')[:10])


def belongs_boxes():
    """Every "belongs to" chooser in the window, by the row it names.

    A field in a table cell is read out as its kind alone, so the
    program puts column and row into the name a screen reader says --
    "belongs to -- CoPresenter_REC00018.wav". That is asked here rather
    than a column number, which changes with what this machine can do.
    """
    said = vpm.T('belongs to')
    out = {}
    top = win()
    for w in (top.findChildren(QtWidgets.QComboBox) if top else []):
        name = w.accessibleName() or ""
        if name.startswith(said):
            out[name.split(" -- ", 1)[-1].strip()] = w
    return out


def belongs_box(file_name):
    """The chooser of one recording, found afresh every time.

    Never held on to: answering rebuilds the whole table, and Qt has
    then deleted the box the last step was looking at.
    """
    for said, box in belongs_boxes().items():
        if file_name in said:
            return box
    return None


def name_field(file_name):
    """The Speaker name field of one recording, by the row it names.

    Waited for rather than the chooser: the field is built whatever the
    tick says, so it tells a table that has not been drawn yet from a
    table that was drawn without a chooser -- which is the fault.
    """
    said = vpm.T('Speaker name')
    top = win()
    for w in (top.findChildren(QtWidgets.QWidget) if top else []):
        name = w.accessibleName() or ""
        if name.startswith(said) and file_name in name:
            return w
    return None


def picked_in(file_name):
    """Which camera that row stands on, as the program stores it."""
    box = belongs_box(file_name)
    return None if box is None else box.currentData()


def offered_in(file_name):
    """What can be picked in that row, as the program stores it."""
    box = belongs_box(file_name)
    return [] if box is None else [box.itemData(i)
                                   for i in range(box.count())]


def rows_shown():
    """The names of the rows that have a chooser -- for the FAIL line."""
    return sorted(belongs_boxes())


def project_files():
    return sorted(f for f in os.listdir(out_folder)
                  if f.startswith(vpm.PROJECT_PREFIX))


# How long a step may find nothing new before it is called red, and how
# long a whole pass may take. Standstill and not the clock: the step
# that never came is named, and a machine nine times slower than this
# one is not punished for being slow. Both are far above what a step
# takes here -- one fell once beside seventeen other tests at 10 s.
POLL = 500
STANDSTILL = 120                 # goes, so 60 s of nothing happening
WHOLE_PASS = 300000              # ms, five minutes for either pass

n = [0]
m = [0]
patience = [0]
over = set()


class NotYet(Exception):
    """The window has not caught up; wait and ask again."""


def needed(what, thing):
    """Give the thing back, or say it is not there yet.

    Fixed waits are what makes a window test flap: fast here, slow on
    the builder, and a step that simply failed there would be a red run
    that means nothing. So a step that does not find what it needs is
    run again, up to twenty times, before it is called red.
    """
    if thing is None or thing is False:
        raise NotYet(what)
    return thing


def deadline(which, at):
    """The whole pass has run out of time: red, and it says where.

    A bare app.quit() here would end the run in the middle and leave
    every check after this point unreached -- and with nothing in `bad`
    the test would print a low count and go out green.
    """
    def fired():
        if which in over:
            return          # the pass is over; this timer is only late
        bad.append("%s never finished: %d s gone, still at step %d"
                   % (which, WHOLE_PASS / 1000, at[0]))
        app.quit()
    return fired


# ----------------------------------------------------- 1. set and write
def step():
    i = n[0]
    print("   step %d" % i, flush=True)
    try:
        if i == 0:
            top = needed("the window of the first pass", win())
            top.show(); top.resize(1400, 900); app.processEvents()
            needed("the Add files button", button("Add files")).click()
        elif i == 1:
            # Without an output folder there is nowhere for the project
            # file to go, so it is chosen the way a person chooses it.
            needed("the output folder button",
                   button("Output folder")).click()
        elif i == 2:
            # Everything that is only waited for comes first: a step
            # that is run again would otherwise judge the same thing
            # twenty times over and print a count nobody can read.
            box = needed("the Multitrack tick", multitrack_tick())
            needed("the row of the recording", name_field(DRIVEN))
            check("the Multitrack tick is off in a fresh window",
                  not box.isChecked(),
                  "the tick reads %s, wanted off" % box.isChecked())
            offered = offered_in(DRIVEN)
            check("a recording offers a camera to belong to with the "
                  "tick off",
                  belongs_box(DRIVEN) is not None,
                  "rows with a chooser: %s, wanted %s among them"
                  % (rows_shown(), DRIVEN))
            check("both cameras stand in the chooser with the tick off",
                  WIDE in offered and TARGET in offered,
                  "wanted %r and %r, the chooser offers %s"
                  % (WIDE, TARGET, offered))
        elif i == 3:
            box = needed("the chooser of the driven row",
                         belongs_box(DRIVEN))
            check("the row stands on no camera of its own before "
                  "anything is picked",
                  picked_in(DRIVEN) == vpm.MIX_ONLY,
                  "wanted %r, the row stands on %r"
                  % (vpm.MIX_ONLY, picked_in(DRIVEN)))
            where = box.findData(TARGET)
            needed("the target camera in the chooser", where >= 0)
            box.setCurrentIndex(where)
            app.processEvents()
        elif i == 4:
            check("a camera picked with the tick off stands in the row",
                  picked_in(DRIVEN) == TARGET,
                  "wanted %r, the row stands on %r"
                  % (TARGET, picked_in(DRIVEN)))
            needed("the Multitrack tick", multitrack_tick()).click()
        elif i == 5:
            box = needed("the Multitrack tick", multitrack_tick())
            check("the tick is on after the first click",
                  box.isChecked(),
                  "the tick reads %s, wanted on" % box.isChecked())
            check("ticking Multitrack leaves the picked camera standing",
                  picked_in(DRIVEN) == TARGET,
                  "wanted %r, the row stands on %r"
                  % (TARGET, picked_in(DRIVEN)))
            box.click()
        elif i == 6:
            box = needed("the Multitrack tick", multitrack_tick())
            check("the tick is off again after the second click",
                  not box.isChecked(),
                  "the tick reads %s, wanted off" % box.isChecked())
            check("unticking Multitrack leaves the picked camera "
                  "standing",
                  picked_in(DRIVEN) == TARGET,
                  "wanted %r, the row stands on %r"
                  % (TARGET, picked_in(DRIVEN)))
            check("the recording nobody touched is still on no camera "
                  "of its own",
                  picked_in(OTHER) == vpm.MIX_ONLY,
                  "wanted %r, the row stands on %r"
                  % (vpm.MIX_ONLY, picked_in(OTHER)))
        elif i == 7:
            win().close()
            app.aboutToQuit.emit()
            app.processEvents()
        elif i == 8:
            # The file is written while the window closes, and the step
            # after that is not the moment it is there: measured, one run
            # in four fell here on this Mac and one builder job of six.
            # What follows then is worse than the fault -- the pass ends,
            # the second pass has no file to open, and its own step waits
            # a minute for a row that cannot come. So the step waits.
            #
            # It waits by giving up, not by refusing: a `needed` here
            # would swallow exactly the case the judgement below asks
            # about, and a file that never came would end the run under a
            # name no register knows. Standstill and then the judgement,
            # which then says how long it waited for nothing.
            if not project_files() and patience[0] < STANDSTILL:
                raise NotYet("the project file the closing window writes")
            names = project_files()
            check("closing the window leaves one project file behind",
                  len(names) == 1,
                  "%d project files against 1 after %.0f s of waiting; "
                  "the folder holds %s"
                  % (len(names), patience[0] * POLL / 1000.0,
                     sorted(os.listdir(out_folder))))
            if not names:
                raise SystemExit
            project_path[0] = os.path.join(out_folder, names[0])
            d = json.loads(open(project_path[0], encoding="utf-8").read())
            stored = (d.get("assignment") or {}).get(
                "audio:" + os.path.join(folder, DRIVEN))
            check("the project file keeps the camera picked with the "
                  "tick off",
                  isinstance(stored, list) and len(stored) > 1
                  and stored[1] == TARGET,
                  "wanted %r in the second field, the file holds %r"
                  % (TARGET, stored))
        else:
            over.add("the first pass")
            app.quit()
            return
        n[0] += 1
        patience[0] = 0
        QtCore.QTimer.singleShot(700, step)
    except NotYet as why:
        patience[0] += 1
        if patience[0] > STANDSTILL:
            bad.append("step %d waited for %s: %d goes over about %d s, "
                       "and it never came"
                       % (i, why, STANDSTILL, STANDSTILL * POLL / 1000))
            over.add("the first pass")
            app.quit()
            return
        QtCore.QTimer.singleShot(POLL, step)
    except SystemExit:
        over.add("the first pass")
        app.quit()
    except Exception:
        import traceback; traceback.print_exc()
        bad.append("step %d fell over" % i)
        over.add("the first pass")
        app.quit()


print("1. Pick a camera with the tick off, click the tick twice, write it")
QtCore.QTimer.singleShot(500, step)
QtCore.QTimer.singleShot(WHOLE_PASS, deadline("the first pass", n))
vpm.gui()


# ------------------------------------------- 2. open it again, elsewhere
print("\n2. Open it again, in a window that knows nothing")
pass_over()


def again():
    i = m[0]
    print("   step %d" % i, flush=True)
    try:
        if i == 0:
            top = needed("the window of the second pass", win())
            top.show(); top.resize(1400, 900); app.processEvents()
            needed("the Open project button",
                   button("Open project")).click()
        elif i == 1:
            needed("the row of the recording", name_field(DRIVEN))
            needed("the chooser of the driven row", belongs_box(DRIVEN))
            check("the picked camera is back after opening the project "
                  "again",
                  picked_in(DRIVEN) == TARGET,
                  "wanted %r, the row stands on %r; rows with a chooser: "
                  "%s" % (TARGET, picked_in(DRIVEN), rows_shown()))
        else:
            over.add("the second pass")
            app.quit()
            return
        m[0] += 1
        patience[0] = 0
        QtCore.QTimer.singleShot(700, again)
    except NotYet as why:
        patience[0] += 1
        if patience[0] > STANDSTILL:
            bad.append("second pass, step %d waited for %s: %d goes over "
                       "about %d s, and it never came"
                       % (i, why, STANDSTILL, STANDSTILL * POLL / 1000))
            over.add("the second pass")
            app.quit()
            return
        QtCore.QTimer.singleShot(POLL, again)
    except Exception:
        import traceback; traceback.print_exc()
        bad.append("second pass, step %d fell over" % i)
        over.add("the second pass")
        app.quit()


if project_path[0]:
    adding[:] = []
    patience[0] = 0
    QtCore.QTimer.singleShot(500, again)
    QtCore.QTimer.singleShot(WHOLE_PASS, deadline("the second pass", m))
    vpm.gui()
else:
    check("the picked camera is back after opening the project again",
          False, "the first pass never got as far as naming a project "
          "file; the output folder holds %s"
          % (sorted(os.listdir(out_folder)),))

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
