# -*- coding: utf-8 -*-
"""The separation counts voices as the language does, project files not.

Three sections in the order they come: the line a finished separation
writes, under German, where the count of voices takes the thousands
point; the block the project file carries, whose count of speakers
stays a plain number because the program reads it back with int(); and
the same line again under English, where the count takes the comma.

The worker is a stand-in that answers with a fixed set of labels, so
what is judged is the line the program writes and not what pyannote
would hear. The real separation never starts here.
"""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import time

import numpy

import the_program

began = time.time()
vpm = the_program.load()

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# Four digits, because that is the width at which a thousands mark
# shows at all. Nobody records this many people; the number is here to
# make the mark visible, the same way a four-digit track number is in
# project_amounts_grouped_test.py.
FOUND = 1234

# What the other process would be. It reads its whole input before it
# answers, so the waveform going in can never fill the pipe and stall,
# and it hands back one label per voice -- which is all the line under
# test counts.
STAND_IN = ("import json, sys\n"
            "sys.stdin.buffer.read()\n"
            'print(json.dumps({"segments": [["S%%05d" %% i, 0.0, 1.0]\n'
            "                               for i in range(%d)]}))\n"
            % FOUND)

HOME = tempfile.mkdtemp(prefix="vpm_voice_counts_")
WORKER = os.path.join(HOME, "stand_in_worker.py")
with open(WORKER, "w", encoding="utf-8") as f:
    f.write(STAND_IN)

# A tenth of a second of silence: the length only reaches the line as
# "out of 0:00:00 of audio", and decoding a real recording would say
# nothing more about the count.
SAMPLES = 1600
WAVE = numpy.zeros(SAMPLES, dtype=numpy.float32)
HEAD = json.dumps({"model": "", "sample_rate": vpm.SPEAKER_SPLIT_RATE,
                   "samples": SAMPLES, "speakers": 0})


def one_line(text):
    """The line the separation printed, for the FAIL line to carry.

    Not the line that holds the number wanted: a run that wrote the
    number in the wrong form would then have nothing to show, and the
    failure would say what is missing without saying what is there.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return lines[-1] if lines else ""


def separation_said():
    """One separation against the stand-in: what it printed, and how it went.

    The second half of the answer travels into the failure line: a run
    the stand-in never answered prints nothing at all, and then "no
    thousands point" would name a consequence instead of the cause.
    """
    caught = io.StringIO()
    with contextlib.redirect_stdout(caught):
        voices, trouble = vpm._speaker_split_talk(
            sys.executable, WORKER, HEAD, WAVE, dict(os.environ),
            None, None)
    said = caught.getvalue()
    for line in said.splitlines():
        print("      > %s" % line.rstrip())
    return said, "%d voices came back, and it said: %s" % (
        len(voices), trouble or "nothing")


print("1. A German run writes the count of voices with a point")
vpm.set_language("de")
german, german_went = separation_said()
check("the count of voices takes the German thousands mark",
      "1.234" in german and "1234" not in german,
      "%r -- wanted %r in it and %r not; %s"
      % (one_line(german), "1.234", "1234", german_went))

print("\n2. What the project file carries stays a plain number")
# Still German: a grouped number would show here and nowhere else, and
# the program reads this field back with int(), which "1.234" ends in.
block = vpm.speakers_for_project("no_such_recording.wav",
                                 [("SPEAKER_00", [(0.0, 1.0)])], FOUND, {})
check("the project's count of speakers is not written in words",
      block["num_speakers"] == FOUND,
      "%r in the block, wanted %r" % (block["num_speakers"], FOUND))

print("\n3. An English run writes the same count with a comma")
vpm.set_language("en")
english, english_went = separation_said()
check("the count of voices takes the English thousands mark",
      "1,234" in english and "1234" not in english,
      "%r -- wanted %r in it and %r not; %s"
      % (one_line(english), "1,234", "1234", english_went))

shutil.rmtree(HOME, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
