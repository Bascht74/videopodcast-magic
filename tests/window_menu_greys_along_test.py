# -*- coding: utf-8 -*-
"""The five File entries that switch are as grey as the window.

Save project, Close project, Remove, Start and Dry run stood black and
clickable over an empty window while the buttons that do the same thing
were grey. They are read at six moments: the instant the menu bar is
handed over, with nothing open, with a project open, with a row of the
file list chosen and without one, around a run, and after the project
has been closed again. Remove, Start and Dry run are held against
their own buttons; the two project entries have none in the window, so
each of them is held against a state written out here, and that the
window really is in that state is a check of its own before them --
the title bar and the file list say so.

Two greys agree by chance, so the state of the button is read as a
judgement of its own wherever it differs: without that the readings
above it could be comparing two constants.

The first moment needs the probe on build_menus: the window checks its
buttons in the very next line, so once the window stands the entries
are grey whether they were born grey or not.

The last two moments are only reached when the menu opens. A selection
and a run grey their button and ask the menu nothing, so there the menu
is opened the way somebody at the screen opens it; everywhere else the
entries are read as they stand, which is what the keys hang on. The run
is held still -- gui_run_loop is replaced by one that waits -- so the
state is reached without anything being computed.
"""
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import threading
import wave

import numpy as np

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.say_dialog = lambda *a, **k: True     # no dialog waits for anybody

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# The five entries the window switches. Three of them -- Remove, Start
# and Dry run -- have a button that does the same thing; Save project
# and Close project have none anywhere in the window.
SAVE, CLOSE = vpm.T('Save project'), vpm.T('Close project')
REMOVE = vpm.T('Remove')
START, DRY = vpm.T('Start'), vpm.T('Dry run')
SWITCHED = [SAVE, CLOSE, REMOVE, START, DRY]
WITH_A_BUTTON = [REMOVE, START, DRY]
TABS_WANTED = 4

# The run is held still: what it computes is no part of this, only that
# the buttons are grey while it goes. The wait has an upper bound so
# the thread cannot outlive the test if the release never comes.
run_going = threading.Event()
run_over = threading.Event()


def run_held(argv, state, write, ask_user, bridge, bridge_emit, order):
    run_going.set()
    run_over.wait(90)
    state["running"] = False


vpm.gui_run_loop = run_held

RATE, SEC = 48000, 4
folder = tempfile.mkdtemp(prefix="vpm_greys_")
out_folder = os.path.join(folder, "Ergebnis")
os.makedirs(out_folder, exist_ok=True)


def tone(name, hz=300.0):
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
    path = os.path.join(folder, name)
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                    "testsrc=size=160x90:rate=25:duration=%d" % SEC,
                    "-f", "lavfi", "-i",
                    "sine=frequency=300:duration=%d" % SEC,
                    "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
                    "yuv420p", "-c:a", "aac", "-shortest", "-y", path],
                   check=True)
    return path


audio = tone("A_speaker.wav")
one, two = clip("B_camera.mov"), clip("C_camera.mov")
# A finished video in the output folder is what brings the Output tab
# with the project: the program takes it for results of an earlier run.
shutil.copy(one, os.path.join(out_folder, "Fertig.mov"))
project = os.path.join(folder, "videopodcast-magic_Grey.json")
with open(project, "w", encoding="utf-8") as f:
    json.dump({"format": 3, "version": "test", "timeline": [], "call": [],
               "files": [{"path": audio, "kind": "audio"},
                         {"path": one, "kind": "video"},
                         {"path": two, "kind": "video"}],
               "out_folder": out_folder, "production": "Grey",
               "multitrack": False, "assignment": {}, "preset": ""}, f)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (project, ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted

# The state of the four entries at the moment the menu bar is handed
# back, before the window has checked its buttons once. Nothing else can
# see that moment: the check follows in the very next line of gui().
born = {}
_menus_built = vpm.build_menus


def menus_watched(*a, **k):
    made = _menus_built(*a, **k)
    for m in made.findChildren(QtWidgets.QMenu):
        if m.title() == vpm.T('&File'):
            born.update((x.text(), x.isEnabled())
                        for x in m.actions() if x.text())
    return made


vpm.build_menus = menus_watched


def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def button(word):
    """The push button whose caption begins with this word."""
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(word):
            return w


# The three buttons the entries follow, found once and kept: a running
# Start reads "running ..." and its caption would find nothing.
push = {}


def tab_bar():
    """The bar of sheets, found by the one tab that is always there."""
    for tw in win().findChildren(QtWidgets.QTabWidget):
        if tw.count() and tw.tabText(0).startswith(
                vpm.T('Files && production')):
            return tw


def file_menu():
    for m in win().findChildren(QtWidgets.QMenu):
        if m.title() == vpm.T('&File'):
            return m


def entry(text):
    for a in file_menu().actions():
        if a.text() == text:
            return a


def menu_opened():
    """Open the File menu the way somebody at the screen does.

    A selection and a run grey their button without asking the menu
    anything, and the entries are switched when the menu opens -- as
    in the View and Player menus. A reading taken without this would
    be the state of whenever the buttons were last checked.
    """
    where = file_menu()
    where.popup(QtCore.QPoint(0, 0))
    app.processEvents()
    where.close()
    app.processEvents()


def file_list():
    """The list of files, the first tree the window holds."""
    for t in win().findChildren(QtWidgets.QTreeWidget):
        return t


def rows():
    """How many rows the file list shows -- what there is to save."""
    t = file_list()
    return t.topLevelItemCount() if t is not None else -1


def named():
    """Whether the title bar names the open project file."""
    return os.path.basename(project) in win().windowTitle()


def how(thing):
    return "alive" if thing else "grey"


def ground():
    """One line naming everything a judgement below rests on."""
    tw = tab_bar()
    return ("%d tabs, %d rows in the file list, the title %s the project, "
            "Remove button %s, Start button %s, Dry run button %s"
            % (tw.count() if tw is not None else -1, rows(),
               "names" if named() else "does not name",
               how(push[REMOVE].isEnabled()),
               how(push[START].isEnabled()),
               how(push[DRY].isEnabled())))


def against_button(text):
    """Is this entry as grey as the button that does the same thing?"""
    b = push.get(text)
    return (b is not None and entry(text).isEnabled() == b.isEnabled(),
            "the entry is %s, the button %s -- %s"
            % (how(entry(text).isEnabled()),
               "missing" if b is None else how(b.isEnabled()), ground()))


def stands(text, alive):
    """Is this entry the way the window plainly says it should be?"""
    return (entry(text).isEnabled() == alive,
            "the entry is %s and should be %s -- %s"
            % (how(entry(text).isEnabled()), how(alive), ground()))


n = [0]
seen = [-1]
still = [0]
patience = [0]
sign = [None]
over = set()


def life():
    """A sign that moves only because the window is working.

    Patience is spent on standstill, not on a deadline: the builder is
    up to three times slower than this machine, and a count of rounds
    would punish it for being slow rather than for being stuck.
    """
    where = win()
    tw = tab_bar() if where is not None else None
    return (where.windowTitle() if where is not None else None,
            tw.count() if tw is not None else -1)


class NotYet(Exception):
    """The window has not caught up; wait and ask again."""


def needed(what, thing):
    if thing is None or thing is False:
        raise NotYet(what)
    return thing


def deadline():
    """The whole pass has taken 120 s: red, and it says where.

    A bare app.quit() here would end the run in the middle and leave
    every check after this point unreached -- and with nothing in `bad`
    the test would print a low count and go out green.
    """
    def fired():
        if "the pass" in over:
            return          # the pass is over; this timer is only late
        bad.append("the pass never finished: 120 s gone, still at step %d"
                   % n[0])
        app.quit()
    return fired


def settled():
    """Wait until the tab count has stopped moving.

    Never on the number a judgement below reads: a count that never
    arrives would then end the run here instead of being reported.
    """
    tw = needed("the tab bar", tab_bar())
    if tw.count() != seen[0]:
        seen[0], still[0] = tw.count(), 0
    else:
        still[0] += 1
    if still[0] < 5:
        raise NotYet("the tabs to stop arriving, %d of them for %d rounds"
                     % (tw.count(), still[0]))
    return tw


def step():
    i = n[0]
    print("   step %d" % i, flush=True)
    try:
        if i == 0:
            needed("the window", win()).show()
            win().resize(1400, 900)
            app.processEvents()
            for text in WITH_A_BUTTON:
                push[text] = needed("the %s button" % text, button(text))
            print("1. The menu bar the moment it was handed over")
            missing = [t for t in SWITCHED if t not in born]
            alive = [t for t in SWITCHED if born.get(t)]
            check("the five switched entries are born grey, before the "
                  "window has checked its buttons once",
                  not missing and not alive,
                  "of %d entries %s the menu bar was handed over with %s "
                  "alive and %s not in it at all"
                  % (len(SWITCHED), SWITCHED, alive or "none",
                     missing or "none"))

            print("\n2. A window with nothing open")
            needed("the tab bar", tab_bar())
            ok, why = stands(SAVE, False)
            check("with nothing open Save project is grey", ok, why)
            ok, why = stands(CLOSE, False)
            check("with nothing open Close project is grey", ok, why)
            ok, why = against_button(REMOVE)
            check("with nothing open Remove is as grey as its button",
                  ok, why)
            ok, why = against_button(START)
            check("with nothing open Start is as grey as its button",
                  ok, why)
            ok, why = against_button(DRY)
            check("with nothing open Dry run is as grey as its button",
                  ok, why)
            check("with nothing open the Start button is grey, so the two "
                  "readings above are not two greys agreeing by chance",
                  not push[START].isEnabled(), ground())
            needed("the Open project button",
                   button(vpm.T('Open project ...'))).click()
        elif i == 1:
            # Waited for is the project in the title bar and a tab count
            # that has stopped moving -- never the number a check reads.
            if not named():
                raise NotYet("the project in the title bar, which reads %r"
                             % win().windowTitle())
            tw = settled()
            print("\n3. A project is open")
            check("the project is open before the File menu is read",
                  named() and tw.count() == TABS_WANTED,
                  "%d tabs against %d, and the title %r"
                  % (tw.count(), TABS_WANTED, win().windowTitle()))
            ok, why = stands(SAVE, True)
            check("with a project open Save project is alive", ok, why)
            ok, why = stands(CLOSE, True)
            check("with a project open Close project is alive", ok, why)
            ok, why = against_button(START)
            check("with a project open Start is as grey as its button",
                  ok, why)
            ok, why = against_button(DRY)
            check("with a project open Dry run is as grey as its button",
                  ok, why)
            check("with a whole project open the Start button is alive, so "
                  "the two readings above have something to disagree over",
                  push[START].isEnabled(), ground())
        elif i == 2:
            print("\n4. What is chosen in the file list decides Remove")
            menu_opened()
            check("with nothing chosen the Remove button is grey, so the "
                  "reading below is not two greys agreeing by chance",
                  not push[REMOVE].isEnabled(), ground())
            ok, why = against_button(REMOVE)
            check("with nothing chosen Remove is as grey as its button",
                  ok, why)
            first = needed("a row in the file list",
                           file_list().topLevelItem(0))
            file_list().setCurrentItem(first)
            app.processEvents()
            menu_opened()
            check("with a row chosen the Remove button is alive, so the "
                  "reading below has something to disagree over",
                  push[REMOVE].isEnabled(),
                  "the row chosen is %r -- %s" % (first.text(0), ground()))
            ok, why = against_button(REMOVE)
            check("with a row chosen Remove is as grey as its button",
                  ok, why)
        elif i == 3:
            print("\n5. While a run is going")
            needed("the Start button", push[START]).click()
        elif i == 4:
            if not run_going.is_set():
                raise NotYet("the run to reach the worker, with the Start "
                             "button %s" % how(push[START].isEnabled()))
            menu_opened()
            check("the run is going and both its buttons are grey before "
                  "the File menu is read",
                  run_going.is_set() and not push[START].isEnabled()
                  and not push[DRY].isEnabled(), ground())
            ok, why = against_button(START)
            check("while a run is going Start is as grey as its button",
                  ok, why)
            ok, why = against_button(DRY)
            check("while a run is going Dry run is as grey as its button",
                  ok, why)
            run_over.set()
        elif i == 5:
            # The caption is what the step itself writes back when the run
            # is over, and no judgement below reads it.
            if push[START].text().strip() != START:
                raise NotYet("the Start button to say %r again, and it says "
                             "%r" % (START, push[START].text()))
            menu_opened()
            check("the run is over and its button is alive again before "
                  "the File menu is read",
                  push[START].isEnabled(), ground())
            ok, why = against_button(START)
            check("when the run is over Start is as grey as its button",
                  ok, why)
            needed("the Close project entry", entry(CLOSE)).trigger()
            seen[0], still[0] = -1, 0
        elif i == 6:
            if named():
                raise NotYet("the project to leave the title bar, which "
                             "reads %r" % win().windowTitle())
            settled()
            print("\n6. The project has been closed again")
            check("the project is closed before the File menu is read again",
                  not named() and rows() == 0,
                  "%d rows in the file list against 0, and the title %r"
                  % (rows(), win().windowTitle()))
            ok, why = stands(SAVE, False)
            check("after the project is closed Save project is grey again",
                  ok, why)
            ok, why = stands(CLOSE, False)
            check("after the project is closed Close project is grey again",
                  ok, why)
            ok, why = against_button(START)
            check("after the project is closed Start is as grey as its "
                  "button", ok, why)
            ok, why = against_button(DRY)
            check("after the project is closed Dry run is as grey as its "
                  "button", ok, why)
        else:
            over.add("the pass")
            app.quit()
            return
        n[0] += 1
        patience[0] = 0
        QtCore.QTimer.singleShot(400, step)
    except NotYet as why:
        moved = life()
        if moved != sign[0]:
            sign[0], patience[0] = moved, 0
        patience[0] += 1
        if patience[0] > 60:
            bad.append("step %d waited for %s: 60 rounds of 400 ms with "
                       "the window at %r not moving at all, and it never "
                       "came" % (i, why, sign[0]))
            over.add("the pass")
            app.quit()
            return
        QtCore.QTimer.singleShot(400, step)
    except Exception:
        import traceback
        traceback.print_exc()
        bad.append("step %d fell over" % i)
        over.add("the pass")
        app.quit()


QtCore.QTimer.singleShot(500, step)
QtCore.QTimer.singleShot(120000, deadline())
# A window that falls over while it is being built takes the event loop
# with it, and the closing lines below are the only place that counts.
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
