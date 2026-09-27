# -*- coding: utf-8 -*-
"""A voice heard in two recordings is said so, and only above the line.

The separation hands back one voice print per voice; kept beside the
stored separation, two recordings can be held against each other. In
order: which pairs the comparison proposes -- the same voice, the line
from both sides, one voice never for two, a print with no length --
then the prints stored beside a separation, and last the log line the
window writes, and where it stays silent. The prints are written out
here by hand; what the real model makes of real voices is
voice_split_hears_two's.
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
import math
import shutil
import tempfile
import time
import wave

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


def at(similarity):
    """A print that lies at *similarity* to [1, 0, 0], by its angle."""
    return [similarity, math.sqrt(1.0 - similarity ** 2), 0.0]


def pairs(found):
    """The labels of what was proposed, without the numbers."""
    return [(a, b) for a, b, _s in found]


LINE = vpm.SPEAKER_SAME_VOICE
print("The line: %.2f" % LINE)

#------------------------------------------------------- the comparison

print("\nWhich voices are proposed as one")
# Presenter and Guest in both, the labels the other way round in the
# second: the model numbers by speaking time, not by person.
first = {"SPEAKER_00": [1.0, 0.0, 0.0, 0.0],
         "SPEAKER_01": [0.0, 1.0, 0.0, 0.0]}
second = {"SPEAKER_00": [0.1, 0.9, 0.3, 0.0],
          "SPEAKER_01": [0.95, 0.05, 0.2, 0.1]}
found = vpm.speaker_voices_alike(first, second)
check("the same voice in two recordings is proposed as one",
      pairs(found) == [("SPEAKER_00", "SPEAKER_01"),
                       ("SPEAKER_01", "SPEAKER_00")],
      "wanted SPEAKER_00-SPEAKER_01 and SPEAKER_01-SPEAKER_00, got %s"
      % found)
under = vpm.speaker_voices_alike({"A": [1.0, 0.0, 0.0]},
                                 {"B": at(LINE - 0.01)})
check("a pair just under the line is not proposed", under == [],
      "similarity %.2f against the line %.2f, proposed: %s"
      % (LINE - 0.01, LINE, under))
over = vpm.speaker_voices_alike({"A": [1.0, 0.0, 0.0]},
                                {"B": at(LINE + 0.01)})
check("a pair just over the line is proposed", pairs(over) == [("A", "B")],
      "similarity %.2f against the line %.2f, proposed: %s"
      % (LINE + 0.01, LINE, over))
# Both of the first recording's voices lie over the line to the one
# voice of the second; only the closer may have it.
greedy = vpm.speaker_voices_alike({"A": [1.0, 0.0, 0.0], "B": at(0.95)},
                                  {"X": [1.0, 0.0, 0.0]})
check("one voice is never proposed for two", pairs(greedy) == [("A", "X")],
      "A at 1.00 and B at 0.95 to X, proposed: %s" % greedy)
try:
    empty = vpm.speaker_voices_alike({"A": [0.0, 0.0, 0.0]},
                                     {"B": [1.0, 0.0, 0.0]})
except Exception as e:
    empty = "%s: %s" % (e.__class__.__name__, e)
check("a print with no length is passed over, not a failure", empty == [],
      "a print of zeros against [1, 0, 0] gave %s" % (empty,))

#------------------------------------------------------------ the store

print("\nThe prints beside the separation")
folder = tempfile.mkdtemp(prefix="vpm_heard_again_")


def recording(name, seconds):
    """A short silent wav, so the store has a file to key on."""
    path = os.path.join(folder, name)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(b"\0\0" * 16000 * seconds)
    return path


def keep(path, segments, prints):
    """Store a separation and its prints the way the program does."""
    key = vpm.speaker_cache_key(path, vpm.speaker_model_mark(), 0)
    vpm.speaker_cache_write(key, segments)
    vpm.speaker_voices_write(key, prints)


one = recording("Room_A.wav", 1)
two = recording("Room_B.wav", 2)
apart = recording("Room_C.wav", 3)
segments = [("SPEAKER_00", [(0.0, 0.4)]), ("SPEAKER_01", [(0.5, 0.9)])]
keep(one, segments, first)
keep(two, segments, second)
keep(apart, segments, {"SPEAKER_00": [0.0, 0.0, 1.0, 0.0],
                       "SPEAKER_01": [0.0, 0.0, 0.0, 1.0]})
back = vpm.speaker_voices_stored(one)
check("voice prints stored with a separation come back for it",
      back == first, "wanted %s, got %s" % (first, back))
check("the separation stored beside the prints is unchanged",
      vpm.speaker_split_stored(one) == segments,
      "wanted %s, got %s" % (segments, vpm.speaker_split_stored(one)))

#------------------------------------------------------------ the log

print("\nThe line in the log")
Separations = vpm.ByFile


def state_of(*paths):
    """The window's store, each recording with the names it carries."""
    names = {one: {"SPEAKER_00": "Presenter", "SPEAKER_01": "Guest"},
             two: {"SPEAKER_00": "Speaker 3", "SPEAKER_01": "Speaker 4"},
             apart: {"SPEAKER_00": "Speaker 5", "SPEAKER_01": "Speaker 6"}}
    return {"speakers_by": Separations(
        (p, {"segments": segments, "count": 0, "names": names[p]})
        for p in paths)}


said = vpm.speaker_voices_said(state_of(one, two), two)
guest = [s for s in said if "Guest" in s]
check("the log names both recordings and the voice's name there",
      len(said) == 2 and len(guest) == 1 and "Speaker 3" in guest[0]
      and "Room_A.wav" in guest[0] and "Room_B.wav" in guest[0],
      "%d lines, %d naming Guest: %s" % (len(said), len(guest), said))
silent = vpm.speaker_voices_said(state_of(one, apart), apart)
check("voices that lie apart are not said to be one", silent == [],
      "%d lines: %s" % (len(silent), silent))
alone = vpm.speaker_voices_said(state_of(one), one)
check("a recording is not held against itself", alone == [],
      "%d lines: %s" % (len(alone), alone))

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
