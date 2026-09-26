# -*- coding: utf-8 -*-
"""The window looks for finished tracks again after a run and a reset.

One recording, one camera, the result in a folder beside the material.
The first run, gui_run_loop stood in, leaves the processed tracks from
auphonic.com there: once it is over the window says it found them, and
the next run is handed them rather than uploading again. Then the output
folder is put back beside the material, where no tracks lie: the note
goes, and the run after that is handed no tracks of a folder not chosen.
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
import json
import shutil
import subprocess
import tempfile
import time
import wave
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


START, FOUND = vpm.T('Start'), vpm.T('processed tracks found -- nothing '
                                     'is uploaded')
vpm.say_dialog = lambda *a, **k: True

D = tempfile.mkdtemp(prefix="vpm_tracks_anew_")
MEDIA, RESULT = os.path.join(D, "Recordings"), os.path.join(D, "Result")
os.makedirs(MEDIA)
os.makedirs(RESULT)
TRACKS = os.path.join(RESULT, "auphonic-tracks")


def silent_wav(path, seconds=4):
    """A mono recording of silence, as long as the camera."""
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(48000)
        f.writeframes(b"\0\0" * 48000 * seconds)


audio = os.path.join(MEDIA, "A_speaker.wav")
silent_wav(audio)
camera = os.path.join(MEDIA, "B_camera.mov")
subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                "testsrc=size=160x90:rate=25:duration=4", "-c:v", "libx264",
                "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-y", camera],
               check=True)
project = os.path.join(MEDIA, "videopodcast-magic_Anew.json")
with open(project, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "version": "test", "timeline": [],
               "files": [{"path": audio, "kind": "audio"},
                         {"path": camera, "kind": "video"}],
               "out_folder": RESULT, "production": "Anew",
               "multitrack": False, "assignment": {}, "preset": ""}, f)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (project, ""))
runs = []


def run_stood_in(argv, state, write, ask_user, bridge, bridge_emit, order):
    """The run: the first leaves the processed tracks, as auphonic's does."""
    if not runs:
        os.makedirs(TRACKS)
        silent_wav(os.path.join(TRACKS, "final_Guest_19-00-00-00.wav"))
    runs.append(list(argv))
    state["running"] = False


vpm.gui_run_loop = run_stood_in


def win():
    """The program's main window, or None before it stands."""
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def button(word):
    """The push button whose caption is this word."""
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip() == word:
            return w


def found_said():
    """Whether a label in the window says the finished tracks are there."""
    return any(w.text() == FOUND for w in win().findChildren(QtWidgets.QLabel))


def handed(argv):
    """The folder of finished tracks a run was handed, or None."""
    return (argv[argv.index("--auphonic-done") + 1]
            if "--auphonic-done" in argv else None)


def short(path):
    """A path under this test's folder, written from there."""
    return path.replace(D, "<tmp>") if path else path


class NotYet(Exception):
    """The window has not caught up; wait and ask again."""


n, patience, over, had = [0], [0], set(), [0]


def run_over():
    """The last Start reached the run and the window says Start again."""
    return len(runs) > had[0] and button(START) is not None \
        and button(START).isEnabled()


def step():
    """One step of the pass; the timer calls it again until it is over."""
    i = n[0]
    try:
        if i == 0:
            win().show()
            app.processEvents()
            button(vpm.T('Open project ...')).click()
        elif i == 1:
            if button(START) is None or not button(START).isEnabled():
                raise NotYet("a live Start button")
            print("1. A run leaves the tracks")
            check("before the run no finished tracks are said to be there",
                  not found_said() and not os.path.isdir(TRACKS),
                  "note shown %s, folder there %s"
                  % (found_said(), os.path.isdir(TRACKS)))
            had[0] = len(runs)
            button(START).click()
        elif i == 2:
            if not run_over():
                raise NotYet("the first run to be over")
            check("once the run is over the window says it found them",
                  found_said(), "%d runs, folder there %s, no label says %r"
                  % (len(runs), os.path.isdir(TRACKS), FOUND))
            had[0] = len(runs)
            button(START).click()
        elif i == 3:
            if not run_over():
                raise NotYet("the second run to be over")
            check("and the next run is handed them, nothing uploaded",
                  handed(runs[-1]) == TRACKS,
                  "handed %r, wanted <tmp>%s" % (
                      short(handed(runs[-1])), TRACKS[len(D):]))
        elif i == 4:
            reset = button(vpm.T('reset'))
            if reset is None or reset.isHidden():
                raise NotYet("the reset button beside the output folder")
            print("\n2. The output folder back beside the material")
            reset.click()
            app.processEvents()
            check("after the reset the note on the tracks is gone",
                  not found_said(), "a label still says %r" % FOUND)
            had[0] = len(runs)
            button(START).click()
        elif i == 5:
            if not run_over():
                raise NotYet("the third run to be over")
            check("and the next run is handed no tracks of a folder not chosen",
                  handed(runs[-1]) is None,
                  "handed %r" % short(handed(runs[-1])))
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
shutil.rmtree(D, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
