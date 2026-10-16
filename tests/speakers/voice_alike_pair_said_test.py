# -*- coding: utf-8 -*-
"""Two voices of one separation that sound alike are said, and only those.

Alike is the line that takes a voice of two recordings for one person.
In order: the pairs of one separation's prints -- over and under the
line, a third voice apart, never a voice with itself; the log's line,
by the names given and by label; the window's road, the row and the
line under the table after the table is built again, the row unchanged
for voices apart; the run's own separation, whose log warns. Prints by
hand, widgets stood in for: what the model makes of voices is measured.
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
import io
import math
import shutil
import tempfile
import time

import the_program

began = time.time()
vpm = the_program.load()
vpm.set_language("en")
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def at(similarity, size=3):
    """A print lying at *similarity* to [1, 0, ...], by its angle."""
    return [similarity, math.sqrt(1.0 - similarity ** 2)] + [0.0] * (size - 2)


def pairs(found):
    """The labels of what was named, without the numbers."""
    return [(a, b) for a, b, _s in found]


LINE = vpm.SPEAKER_SAME_VOICE
OVER, UNDER = LINE + 0.01, LINE - 0.01
SAID = vpm.T('  %s and %s in %s sound alike (similarity %s): the '
             'separation may have confused the two -- check their '
             'assignment.')
print("The line: %.2f" % LINE)

#------------------------------------------------- one separation's pairs

print("\nWhich two voices of one separation are named")
over = vpm.voices_alike_inside({"SPEAKER_00": [1.0, 0.0, 0.0],
                                "SPEAKER_01": at(OVER)})
check("two voices just over the line are named, once",
      pairs(over) == [("SPEAKER_00", "SPEAKER_01")],
      "similarity %.2f against the line %.2f, named: %s"
      % (OVER, LINE, over))
under = vpm.voices_alike_inside({"SPEAKER_00": [1.0, 0.0, 0.0],
                                 "SPEAKER_01": at(UNDER)})
check("two voices just under the line are not", under == [],
      "similarity %.2f against the line %.2f, named: %s"
      % (UNDER, LINE, under))
three = vpm.voices_alike_inside({"SPEAKER_00": [1.0, 0.0, 0.0, 0.0],
                                 "SPEAKER_01": [0.0, 0.0, 1.0, 0.0],
                                 "SPEAKER_02": at(0.95, 4)})
check("a third voice apart from both is left out of it",
      pairs(three) == [("SPEAKER_00", "SPEAKER_02")],
      "00 and 02 at 0.95, 01 at nought to both, named: %s" % three)
alone = vpm.voices_alike_inside({"SPEAKER_00": [1.0, 0.0, 0.0]})
check("a voice is never held against itself", alone == [],
      "one voice, named: %s" % alone)

#--------------------------------------------------------- the log's line

print("\nThe line in the log")
prints = {"SPEAKER_00": [1.0, 0.0, 0.0], "SPEAKER_01": at(OVER)}
named = vpm.voices_alike_said("Room.wav", prints,
                              {"SPEAKER_00": "Presenter",
                               "SPEAKER_01": "Guest"})
wanted = SAID % ("Presenter", "Guest", "Room.wav", "%.2f" % OVER)
check("the log names both voices by the names given them",
      named == [wanted], "wanted %r, got %r" % (wanted, named))
plain = vpm.voices_alike_said("Room.wav", prints, {"SPEAKER_01": "Guest"})
wanted = SAID % ("SPEAKER_00", "Guest", "Room.wav", "%.2f" % OVER)
check("and a voice nobody named by its label",
      plain == [wanted], "wanted %r, got %r" % (wanted, plain))

#------------------------------------------------------ the window's road

folder = tempfile.mkdtemp(prefix="vpm_alike_pair_")
os.environ["VPM_CACHE"] = tempfile.mkdtemp(prefix="vpm_alike_pair_store_")
SEGMENTS = [("SPEAKER_00", [(0.0, 0.4)]), ("SPEAKER_01", [(0.5, 0.9)])]


def recording(name):
    """A file for the store to key on; nothing listens to it."""
    path = os.path.join(folder, name)
    with open(path, "wb") as f:
        f.write(b"0" * (len(name) + 1))
    return path


def keep(path, voices):
    """Store a separation and its prints the way the program does."""
    key = vpm.speaker_cache_key(path, vpm.speaker_model_mark(), 0)
    vpm.speaker_cache_write(key, SEGMENTS)
    vpm.speaker_voices_write(key, voices)


class Signal(object):
    """One of the window's signals: the slot it was connected to."""

    def __init__(self):
        self.slot = None

    def connect(self, slot):
        self.slot = slot


class Widget(object):
    """A label, a button or a line of the window: what it was told."""

    def __init__(self):
        self.text, self.style, self.visible = "", "", False
        self.clicked = Signal()

    def setText(self, text):
        self.text = str(text)

    def setStyleSheet(self, style):
        self.style = str(style)

    def setVisible(self, on):
        self.visible = bool(on)


class Bridge(object):
    """The window's signals, as much of them as this road touches."""

    def __init__(self):
        self.speakers_split_note = Signal()
        self.speakers_split = Signal()
        self.speakers_heard = Signal()


class Plan(object):
    """The overall bar, which this road only reports to."""

    def done(self, *a):
        pass

    def add(self, *a):
        pass

    def begin(self, *a):
        pass

    def report(self, *a):
        pass


vpm.SPEAKER_SPLIT_OFF = False
vpm.cells_laid_out = lambda cells: None
# Never reached while the table finds the separation stored; stood in
# so that nothing is ever separated or recognised here.
vpm.speaker_split_begin = lambda *a, **k: None


def window(path, voices):
    """One separation of *path* come back on the window's road.

    The names stand as somebody gave them before; the table is built
    again in between, as the window does, by the window's own start.
    Returns (cell, colour, line under the table, shown, the log).
    """
    keep(path, voices)
    cell, line, words, never = Widget(), Widget(), Widget(), Widget()
    state = {"speakers_by": vpm.ByFile(), "speakers_wanted": True,
             "split_cells": [(path, Widget(), cell, None)]}
    state["speakers_by"][path] = {
        "segments": [], "count": 0,
        "names": {"SPEAKER_00": "Presenter", "SPEAKER_01": "Guest"}}
    bridge = Bridge()
    kick = vpm.make_speaker_split(
        None, state, bridge, lambda *a: None, Plan(), [(path, "audio")],
        [], [], {}, {"busy": True, "stop": False}, line, words, never,
        lambda axis: None)[0]
    state["assignment_fresh"] = kick
    state["preview_soon"] = lambda: None
    said, kept = io.StringIO(), sys.stdout
    sys.stdout = said
    try:
        bridge.speakers_split.slot((path, 0, SEGMENTS, "", [path]))
    finally:
        sys.stdout = kept
    return cell.text, cell.style, words.text, line.visible, said.getvalue()


print("\nThe window's road")
COUNT = vpm.TN(2, 'Separated: %s speaker', 'Separated: %s speakers') % "2"
warned = vpm.COLOURS["warning"]
good = vpm.COLOURS["good"]
alike = recording("Room_A.wav")
text, style, under_table, shown, log = window(
    alike, {"SPEAKER_00": [1.0, 0.0, 0.0], "SPEAKER_01": at(OVER)})
wanted = (SAID % ("Presenter", "Guest", "Room_A.wav", "%.2f" % OVER))
check("the row says the count in the warning colour",
      text == COUNT and warned in style,
      "the cell says %r in %r, wanted %r in %r"
      % (text, style, COUNT, warned))
check("the line under the table carries the log's line",
      shown and under_table == wanted.strip(),
      "shown %s, saying %r, wanted %r" % (shown, under_table,
                                          wanted.strip()))
check("and the window's log carries it too",
      wanted in log.splitlines(),
      "the log was %r" % log[-200:])

apart = recording("Room_B.wav")
text, style, under_table, shown, _log = window(
    apart, {"SPEAKER_00": [1.0, 0.0, 0.0], "SPEAKER_01": at(UNDER)})
check("voices under the line leave the row as it always was",
      text == COUNT and good in style and not shown,
      "the cell says %r in %r, the line under the table shown %s with "
      "%r, wanted %r in %r and nothing under it"
      % (text, style, shown, under_table, COUNT, good))

#--------------------------------------------------------- the run's road

print("\nThe run's own separation")


class Args(object):
    """As much of the parsed command line as the separation reads."""

    def __init__(self, recording):
        self.speakers_local = recording
        self.speakers_from = None
        self.speakers_count = 0
        self.no_speakers_local = False
        self.dry_run = False
        self._speakers_of = {}
        self._camera_audio = None


def run(path):
    """The run separates *path* -- read back, as stored -- and logs."""
    tracks = [{"name": os.path.basename(path), "source": path,
               "blocks": [path], "a": 0.0, "b": 1.0}]
    said, kept = io.StringIO(), sys.stdout
    sys.stdout = said
    try:
        out, _where = vpm.separation_for_run(Args(path), tracks, {}, 0.0,
                                             1.0, [])
    finally:
        sys.stdout = kept
    return out, said.getvalue()


out, log = run(alike)
wanted = vpm.as_warn(SAID % ("SPEAKER_00", "SPEAKER_01", "Room_A.wav",
                             "%.2f" % OVER))
check("the run's log warns of the two, marked as a warning",
      len(out) == 2 and wanted in log.splitlines(),
      "%d voices came back; wanted %r in a log of %r"
      % (len(out), wanted, log[-300:]))

shutil.rmtree(os.environ["VPM_CACHE"], ignore_errors=True)
shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
