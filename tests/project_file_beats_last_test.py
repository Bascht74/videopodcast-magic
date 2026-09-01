# -*- coding: utf-8 -*-
"""A project opened after another takes its answers from its own file.

Answers a person gives are kept per file for as long as the window
stands, so that the file list and the assignment table show one value
and not two. Opening another project has to throw that store away, or
the answer of the last production wins against the one read out of the
new file -- and from the outside it looks as if what was saved had
been lost.

Two project files over the same material, differing in one answer: the
first says the camera's sound is not material, the second says it is.
Both are opened in the same window, one after the other, and that it
really is the same window is a check of its own -- in a second window
the store is empty and the fault cannot show at all.

The answer is read where it is given, in the Camera audio field of the
file list, and where it takes effect: a camera contributing its sound
gets a row in the assignment tree. The state before is read as a
judgement of its own, so the two readings are not two constants
agreeing.
"""
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
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


RATE, SEC = 48000, 6
folder = tempfile.mkdtemp(prefix="vpm_beats_")
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
                    "sine=frequency=440:duration=%d" % SEC,
                    "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
                    "yuv420p", "-c:a", "aac", "-shortest", "-y", path],
                   check=True)
    return path


audio = tone("A_speaker.wav")
camera, second = clip("B_camera.mov"), clip("C_camera.mov")


def project_file(name, own):
    """One project over this material, with the camera answered so."""
    path = os.path.join(folder, "videopodcast-magic_%s.json" % name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"format": 3, "version": "test", "timeline": [],
                   "call": [],
                   "files": [{"path": audio, "kind": "audio"},
                             {"path": camera, "kind": "video"},
                             {"path": second, "kind": "video"}],
                   "out_folder": out_folder, "production": name,
                   # Multitrack, or the assignment tree has no track of
                   # its own to give the camera and the second reading
                   # would have nowhere to show.
                   "multitrack": True,
                   "assignment": {"own:" + camera: own,
                                  "ownname:" + camera: "Room"},
                   "preset": ""}, f)
    return path


FIRST = project_file("Unused", False)
SECOND = project_file("Used", True)
wanted = [FIRST]
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (wanted[0], ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted


def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def button(word):
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(word):
            return w


def tab_bar():
    """The bar of sheets, found by the one tab that is always there."""
    for tw in win().findChildren(QtWidgets.QTabWidget):
        if tw.count() and tw.tabText(0).startswith(
                vpm.T('Files && production')):
            return tw


def file_list():
    """The list of files, the first tree the window holds."""
    for t in win().findChildren(QtWidgets.QTreeWidget):
        return t


def camera_row():
    """The row of the file list standing for the camera, by its path."""
    t = file_list()
    if t is None:
        return None
    here = os.path.abspath(camera)
    for k in range(t.topLevelItemCount()):
        top = t.topLevelItem(k)
        for j in range(top.childCount()):
            node = top.child(j)
            paths = node.data(0, QtCore.Qt.UserRole) or []
            if here in [os.path.abspath(p) for p in paths]:
                return node
    return None


def audio_answer():
    """What the Camera audio field of that row says, as a stored value."""
    node = camera_row()
    if node is None:
        return None
    cell = file_list().itemWidget(node, 4)
    if cell is None:
        return None
    for box in cell.findChildren(QtWidgets.QComboBox):
        return box.currentData()
    return None


def tracks():
    """The rows of the assignment tree -- a view over a model, not a tree.

    Taken apart from the file list by class and not by order: both
    answer findChildren(QTreeView), and which comes first is Qt's
    business.
    """
    for v in win().findChildren(QtWidgets.QTreeView):
        if isinstance(v, QtWidgets.QTreeWidget):
            continue
        model = v.model()
        if model is None:
            continue
        return [model.data(model.index(r, 0)) or ""
                for r in range(model.rowCount())]
    return []


def camera_tracks():
    """The rows of the assignment tree that name the camera."""
    short = os.path.basename(camera)
    return [r for r in tracks() if short in r]


def named(path):
    """Whether the title bar names this project file."""
    return os.path.basename(path) in win().windowTitle()


def ground():
    """One line naming everything a judgement below rests on."""
    tw = tab_bar()
    return ("%d tabs, the title %r, the Camera audio field says %r, the "
            "assignment tree holds %s"
            % (tw.count() if tw is not None else -1, win().windowTitle(),
               audio_answer(), tracks() or "nothing"))


n = [0]
seen = [-1]
still = [0]
patience = [0]
sign = [None]
over = set()
same = {}


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
    """The whole pass has taken 150 s: red, and it says where.

    A bare app.quit() here would end the run in the middle and leave
    every check after this point unreached -- and with nothing in `bad`
    the test would print a low count and go out green.
    """
    def fired():
        if "the pass" in over:
            return          # the pass is over; this timer is only late
        bad.append("the pass never finished: 150 s gone, still at step %d"
                   % n[0])
        app.quit()
    return fired


def settled():
    """Wait until the tab count has stopped moving.

    Never on what a judgement below reads: an answer that never arrives
    would then end the run here instead of being reported.
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
            same["window"] = win()
            wanted[0] = FIRST
            needed("the Open project button",
                   button(vpm.T('Open project ...'))).click()
        elif i == 1:
            if not named(FIRST):
                raise NotYet("the first project in the title bar, which "
                             "reads %r" % win().windowTitle())
            settled()
            print("1. The first project, which says the camera sound is "
                  "not material")
            check("the first project is open and its camera is in the file "
                  "list before its answer is read",
                  named(FIRST) and camera_row() is not None, ground())
            check("the first project's Camera audio field says the sound "
                  "is unused", audio_answer() == vpm.AUDIO_UNUSED,
                  "the field says %r, wanted %r -- %s"
                  % (audio_answer(), vpm.AUDIO_UNUSED, ground()))
            check("with the first project open no row of the assignment "
                  "tree names the camera, so the reading below is not two "
                  "answers agreeing by chance",
                  not camera_tracks(),
                  "%d rows name %s: %s"
                  % (len(camera_tracks()), os.path.basename(camera),
                     camera_tracks() or "none"))
            wanted[0] = SECOND
            seen[0], still[0] = -1, 0
            needed("the Open project button",
                   button(vpm.T('Open project ...'))).click()
        elif i == 2:
            if not named(SECOND):
                raise NotYet("the second project in the title bar, which "
                             "reads %r" % win().windowTitle())
            settled()
            print("\n2. The second project, which says it is material")
            check("the second project is open in the same window and its "
                  "camera is in the file list before its answer is read",
                  named(SECOND) and win() is same["window"]
                  and camera_row() is not None,
                  "the window is %s the one the first project was opened "
                  "in -- %s"
                  % ("still" if win() is same["window"] else "not",
                     ground()))
            check("the second project's Camera audio field says the sound "
                  "is material", audio_answer() == vpm.AUDIO_MATERIAL,
                  "the field says %r, wanted %r -- %s"
                  % (audio_answer(), vpm.AUDIO_MATERIAL, ground()))
            check("the second project's camera has a row of its own in "
                  "the assignment tree", len(camera_tracks()) == 1,
                  "%d rows name %s, wanted 1; the tree holds %s"
                  % (len(camera_tracks()), os.path.basename(camera),
                     tracks() or "nothing"))
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
QtCore.QTimer.singleShot(150000, deadline())
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
