# -*- coding: utf-8 -*-
"""Does the cut player really jump where it is told to?"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import sys, time
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["VPM_PLAYER_DEBUG"] = "1"
import importlib.util
os.environ.setdefault("VPM_SILENT", "1")   # never beep at a person
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vpm)

from PySide6 import QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets
from PySide6.QtCore import Qt
sys.path.insert(0, os.path.dirname(
    os.path.abspath(__file__)))
from fixture_root import fixture

app = QtWidgets.QApplication([])

COLOURS = {"value": "#fff", "quiet": "#888", "heading": "#fff"}
def label(text, colour, bold=False):
    m = QtWidgets.QLabel(text)
    return m
def hint(w, text):
    w.setToolTip(text)
    return w

CutPlayer = vpm.qt_cut_player(QtCore, QtGui, QtWidgets, Qt, QtMultimedia,
                               QtMultimediaWidgets, label, hint, COLOURS)
s = CutPlayer()
s.resize(400, 400)
s.show()

d = fixture("playertest")
cut = [(0.0, 10.0, "A"), (10.0, 20.0, "B"), (20.0, 30.0, "A"),
           (30.0, 40.0, "B"), (40.0, 50.0, "A")]
files = {"A": d + "/a.mp4", "B": d + "/b.mp4"}
s.set(cut, files, {"A": 0.0, "B": 0.0}, d + "/audio.m4a", 0.0,
         begins=0.0, until=50.0)

began = time.time()
done = 0
bad = []
plan = []

def arrived():
    """The player's own report that every seek has landed.

    A seek given up on leaves the wrong position for the check to find.
    """
    return (not s._seeking and not s.audio_seek.pending()
            and not any(seeker.pending() for seeker in s.seekers))

def wait(ms, until=None, steady=400):
    """Sit out ms -- or stop earlier, once `until` has held for `steady` ms.

    A seek while paused lands quickly and nothing moves after it, so
    waiting out the full time measures nothing. `steady` guards the
    shortcut: the tick after a landed seek is the one that loads the
    coming shot into the other pane.
    """
    end = QtCore.QElapsedTimer(); end.start()
    held = QtCore.QElapsedTimer(); held.start()
    while end.elapsed() < ms:
        app.processEvents()
        if until is None or not until():
            held.restart()
        elif held.elapsed() >= steady:
            return
        QtCore.QThread.msleep(5)

def check(name, want, tolerance=0.6):
    global done
    done += 1
    # While playing the 2.5 s are the measurement itself; while paused
    # nothing moves once the seek has landed, so the player is asked.
    wait(2500, None if s.is_running() else arrived)
    # While playing time moves on: the comparison goes against the clock.
    want = s._time() if s.is_running() else want
    slot = s.stack.currentIndex()
    video = s.videos[slot].position() / 1000.0
    audio = s.audio.position() / 1000.0
    ok = abs(video - want) <= tolerance and abs(audio - want) <= tolerance
    # The allowance belongs beside the three numbers: without it nobody
    # reading the line on a builder can tell 0.4 s out from 0.8 s out.
    print("%-28s want %6.2f  video %6.2f  audio %6.2f  (allowed %.2f)  %s"
          % (name, want, video, audio, tolerance, "ok" if ok else "FAIL"))
    if not ok:
        bad.append("%s [want %.2f, video %.2f (%+.2f), audio %.2f (%+.2f), "
                   "allowed %.2f]"
                   % (name, want, video, video - want, audio, audio - want,
                      tolerance))

print("\n== Jump while paused ==")
s.jump(25.0); check("jump to 25 (paused)", 25.0)
s.jump(5.0);  check("jump to 5 (paused)", 5.0)

print("\n== Jump while playing ==")
s.play()
wait(1200)
s.jump(35.0); check("jump to 35 (playing)", 35.0)
wait(800)
t = s._time()
print("programme time after jump+play: %.2f (expected ~38.3)" % t)
if not (35.0 <= t <= 39.5):
    bad.append("clock after jump")
s.jump(12.0); check("jump to 12 (playing)", 12.0)
s.pause()

print("\n== Nudging ==")
s.jump(20.0); wait(2500, arrived)
s.nudge(10.0); check("+10 s -> 30", 30.0)
s.nudge(-1.0); check("-1 s -> 29", 29.0)

print("\n== Change of shot ==")
s.jump(9.5); wait(2500, arrived)
s.play()
wait(3000)
t = s._time()
print("after the cut: clock %.2f, pane %d, loaded %s"
      % (t, s.stack.currentIndex(), s.loaded))
video = s.videos[s.stack.currentIndex()].position() / 1000.0
print("visible picture sits at %.2f (clock %.2f)" % (video, t))
if abs(video - t) > 1.2:
    bad.append("picture out of step after the cut")
s.pause()

print("\n== Readout line ==")
s.jump(20.0); wait(2500, arrived)
s.play(); wait(800)
text = s.readouts.text()
print("  ", text)
visible = s.readouts.isVisible()
print("  visible while playing:", visible)
if not visible:
    bad.append("readouts not visible while playing")
if "(+" not in text and "(-" not in text:
    bad.append("no deviation in brackets")
import re as _re
numbers = [float(x) for x in _re.findall(r"\(([+-]\d+\.\d+)\)", text)]
# Three brackets: pane 1, pane 2, audio. The hidden pane may run ahead,
# so only the visible one and the audio are checked.
slot = s.stack.currentIndex()
print("  deviations:", numbers, " visible is pane", slot + 1)
if len(numbers) != 3:
    bad.append("not three deviations in the line")
elif abs(numbers[slot]) > 1.0 or abs(numbers[2]) > 1.0:
    bad.append("visible picture or audio out of step")
s.pause(); wait(300)
print("  visible while paused:", s.readouts.isVisible())
if s.readouts.isVisible():
    bad.append("readouts still there while paused")

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
