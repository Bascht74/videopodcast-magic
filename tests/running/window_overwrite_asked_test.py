# -*- coding: utf-8 -*-
"""A camera file already written is asked about before a run starts.

One recording and one camera already called B_camera_audio.mov, written
into its own folder under the typed name B_camera: the run steps aside
to B_camera_audio_2.mov. That file lies there, a list of the production
nobody here made, and three names the run never writes. The question
names the first two and none of the rest; No starts nothing, Yes starts
the run, gui_run_loop stood in. Then the production's record claims
both, and the next Start goes without the question.
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
import the_program
SCRIPT = the_program.SCRIPT
import json, shutil, subprocess, tempfile, time, wave
import numpy as np
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


OVERWRITE, START = vpm.T('Overwrite files'), vpm.T('Start')
# Every dialog the window puts, in order: (title, text, answer). The
# overwrite question is answered from `answer`; everything else yes.
asked = []
answer = [False]


def say_dialog(QtWidgets, window, title, text, do_text="", no_text=""):
    """The window's one dialog, answered here and written down."""
    said = answer[0] if title == OVERWRITE else True
    asked.append((title, text, said))
    return said


vpm.say_dialog = say_dialog
runs = []


def run_stood_in(argv, state, write, ask_user, bridge, bridge_emit, order):
    """Nothing computed: the run is written down and over at once."""
    runs.append(list(argv))
    state["running"] = False


vpm.gui_run_loop = run_stood_in

RATE, SEC = 48000, 4
folder = tempfile.mkdtemp(prefix="vpm_overwrite_")
# Into the material's own folder, so the typed name meets the source.
out_folder = folder
t = np.arange(SEC * RATE) / float(RATE)
audio = os.path.join(folder, "A_speaker.wav")
with wave.open(audio, "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(RATE)
    f.writeframes((0.4 * np.sin(2 * np.pi * 300 * t) * 32767)
                  .astype("<i2").tobytes())
camera = os.path.join(folder, "B_camera_audio.mov")
subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                "testsrc=size=160x90:rate=25:duration=%d" % SEC,
                "-f", "lavfi", "-i", "sine=frequency=300:duration=%d" % SEC,
                "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
                "yuv420p", "-c:a", "aac", "-shortest", "-y", camera],
               check=True)
# Measured on longer material of these names: the run wrote
# B_camera_audio_2.mov, since B_camera_audio.mov is the source. Never
# written: the source itself, the bare name, the file's own stem.
written = "B_camera_audio_2.mov"
never = ["B_camera_audio.mov", "B_camera.mov", "B_camera_audio_audio.mov"]
# One of the six lists a run names after the production, here "Again".
listed = "Again_speakers.csv"
project = os.path.join(folder, "videopodcast-magic_Again.json")
with open(project, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "version": "test", "timeline": [],
               "files": [{"path": audio, "kind": "audio"},
                         {"path": camera, "kind": "video"}],
               "out_folder": out_folder, "production": "Again",
               "multitrack": False, "assignment": {}, "preset": ""}, f)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (project, ""))


def win():
    """The program's main window, or None before it stands."""
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def button(word):
    """The push button whose caption begins with this word."""
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(word):
            return w


def name_field():
    """The camera's new file name, as the window holds it."""
    for w in win().findChildren(QtWidgets.QLineEdit):
        if w.accessibleName().startswith(vpm.T('new file name')):
            return w


class NotYet(Exception):
    """The window has not caught up; wait and ask again."""


push = {}
n = [0]
patience = [0]
over = set()
before, had, waited = [0], [0], [0]


def questions_since(k):
    """The titles of the dialogs put since the k-th."""
    return [title for title, _text, _said in asked[k:]]


def step():
    """One step of the pass; the timer calls it again until it is over."""
    i = n[0]
    try:
        if i == 0:
            win().show()
            win().resize(1400, 900)
            app.processEvents()
            button(vpm.T('Open project ...')).click()
        elif i == 1:
            if os.path.basename(project) not in win().windowTitle():
                raise NotYet("the project in the title bar")
            push[START] = button(START)
            if push[START] is None or not push[START].isEnabled() \
                    or name_field() is None:
                raise NotYet("a live Start button and the camera's name")
            name_field().setText("B_camera")
            for made in [written, listed] + never[1:]:
                open(os.path.join(out_folder, made), "wb").close()
        elif i == 2:
            if name_field() is None or name_field().text() != "B_camera":
                raise NotYet("the typed name in the camera's field")
            print("1. The question comes before anything starts")
            before[0], answer[0] = len(asked), False
            push[START].click()
            app.processEvents()
            put = [x for x in asked[before[0]:] if x[0] == OVERWRITE]
            said = put[0][1] if put else ""
            check("the file the run will write is asked about first",
                  bool(put) and written in said,
                  "questions %s, wanted %r named, the overwrite one says "
                  "%r" % (questions_since(before[0]), written,
                          said[:160] if put else "never put"))
            check("and so is a list of the production nobody here made",
                  listed in said,
                  "wanted %r named, the overwrite one says %r"
                  % (listed, said[:200]))
            check("and no name the run never writes is in it",
                  not [x for x in never if x in said],
                  "%s named, the overwrite one says %r"
                  % ([x for x in never if x in said], said[:200]))
            print("\n2. No starts nothing")
            check("and No starts nothing",
                  push[START].text().strip() == START and not runs,
                  "the button says %r, %d runs started"
                  % (push[START].text(), len(runs)))
        elif i == 3:
            print("\n3. Yes starts the run")
            before[0], answer[0], had[0] = len(asked), True, len(runs)
            push[START].click()
        elif i == 4:
            # Waited for, then judged either way: a run that never comes
            # is the red line below, not a line about waiting.
            if len(runs) == had[0] and waited[0] < 50:
                waited[0] += 1
                raise NotYet("the run to reach gui_run_loop")
            check("and Yes starts the run",
                  OVERWRITE in questions_since(before[0])
                  and len(runs) - had[0] == 1,
                  "questions %s, %d runs started, %d rounds of 200 ms "
                  "waited" % (questions_since(before[0]),
                              len(runs) - had[0], waited[0]))
        elif i == 5:
            print("\n4. An earlier run of this production goes unasked")
            # The record a run leaves: it names the camera file it wrote,
            # and beside it vouches for the production's own lists.
            with open(os.path.join(out_folder, "Again_resolve.json"), "w",
                      encoding="utf-8") as f:
                json.dump({"cameras": [{"camera": "B_camera", "file":
                                        os.path.join(out_folder, written)}]},
                          f)
            before[0], answer[0], had[0], waited[0] = (len(asked), False,
                                                       len(runs), 0)
            push[START].click()
        elif i == 6:
            if len(runs) == had[0] and waited[0] < 50:
                waited[0] += 1
                raise NotYet("the run to reach gui_run_loop")
            check("files an earlier run of this production wrote go unasked",
                  OVERWRITE not in questions_since(before[0])
                  and len(runs) - had[0] == 1,
                  "questions %s, %d runs started, %d rounds of 200 ms "
                  "waited" % (questions_since(before[0]),
                              len(runs) - had[0], waited[0]))
        else:
            over.add("the pass")
            app.quit()
            return
        n[0] += 1
        patience[0] = 0
        QtCore.QTimer.singleShot(200, step)
    except NotYet as why:
        patience[0] += 1
        if patience[0] > 150:
            bad.append("step %d waited 30 s for %s, and it never came"
                       % (i, why))
            over.add("the pass")
            app.quit()
            return
        QtCore.QTimer.singleShot(200, step)
    except Exception:
        import traceback
        traceback.print_exc()
        bad.append("step %d fell over" % i)
        over.add("the pass")
        app.quit()


QtCore.QTimer.singleShot(300, step)
try:
    sys.argv = ["videopodcast_magic.py"]
    vpm.gui()
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("the window never came up: gui() fell over")
if "the pass" not in over:
    bad.append("the window closed before the pass was over, at step %d"
               % n[0])
shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
