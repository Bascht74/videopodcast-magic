# -*- coding: utf-8 -*-
"""The window writes down the words of every block of a split recording.

Two voices we spoke, cut in two in the pause after the first turn as a
recorder splits a long take. The sections: the recording heard through
the road the proposals take, naming no blocks -- one file, every turn
of the second block, on the whole recording's time, the joined file
gone afterwards; stored under the whole and read back; and a recording
in one file still stored under its own content. A stand-in recogniser
writes a word where the file it is handed is loud, nothing else.
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
import shutil
import tempfile
import threading
import time
import wave

import numpy as np

# A store of its own, so words another test left behind cannot answer
# here in place of the stand-in below.
os.environ["VPM_CACHE"] = tempfile.mkdtemp(prefix="vpm-all-blocks-store-")
vpm = the_program.load()
vpm.set_language("en")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# How long the recognition may take before this is red. Never reached
# where the program works; the builder is about nine times slower.
PATIENCE = 60.0
LANGUAGE = "eng"
FRAME = 0.1            # one stand-in word per loud tenth of a second
LOUD = 0.01            # the pauses say(1) leaves are digital silence
LENGTH_OFF = 0.1       # how far the heard file may differ from the whole

SAMPLE = os.path.join(HERE, "samples", "twovoices")
truth = []
for line in open(os.path.join(SAMPLE, "truth.txt"), encoding="utf-8"):
    parts = line.split()
    if len(parts) == 3:
        truth.append((parts[0], float(parts[1]), float(parts[2])))
talk = os.path.join(SAMPLE, "talk.wav")
with wave.open(talk, "rb") as w:
    shape, rate = w.getparams(), w.getframerate()
    audio = w.readframes(w.getnframes())
    whole_length = w.getnframes() / float(rate)
step = shape.sampwidth * shape.nchannels

folder = tempfile.mkdtemp(prefix="vpm-all-blocks-")
edge = (truth[0][2] + truth[1][1]) / 2.0
blocks = [os.path.join(folder, "REC_0001.wav"),
          os.path.join(folder, "REC_0002.wav")]
for path, piece in ((blocks[0], audio[:int(edge * rate) * step]),
                    (blocks[1], audio[int(edge * rate) * step:])):
    with wave.open(path, "wb") as w:
        w.setparams(shape)
        w.writeframes(piece)

asked = []


def listening(path, language=""):
    """The recogniser, stood in for: a word where the file is loud."""
    with wave.open(path, "rb") as w:
        here = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), "<i2") / 32768.0
    asked.append((path, len(x) / float(here)))
    n = int(here * FRAME)
    return [{"start": round(i * FRAME, 3), "end": round((i + 1) * FRAME, 3),
             "word": "w"}
            for i in range(len(x) // n)
            if np.sqrt(np.mean(x[i * n:(i + 1) * n] ** 2)) > LOUD]


vpm.macos_words = listening
vpm.whisper_words = lambda p, language="", install=True: None
# The suite runs silent, and silent mode lets the window start no
# recogniser by itself; here the recogniser is stood in and asked.
vpm.listening_unasked = lambda: True


def heard_in_window(state):
    """Start the recognition as the proposals do, and wait for it."""
    arrived = threading.Event()
    got = []

    def done_hearing(result):
        got.append(result)
        arrived.set()

    vpm.speech_words_kick_off(state, LANGUAGE, done_hearing)
    came = arrived.wait(PATIENCE)
    return (got[0][1] if got else None), came


print("1. A recording in two blocks, named by its first")
state = {"speakers_source": blocks[0],
         "blocks_of": vpm.ByFile({blocks[0]: list(blocks)})}
words, came = heard_in_window(state)
check("the recognition comes back",
      came and words is not None,
      "nothing came back within %.0f s" % PATIENCE if not came
      else "%d words" % len(words or ()))
words = words or []
lengths = [round(n, 2) for _p, n in asked]
check("the recogniser hears one file holding every block",
      len(asked) == 1 and abs(asked[0][1] - whole_length) <= LENGTH_OFF,
      "asked %d times, for %s s, the whole is %.2f s"
      % (len(asked), lengths, whole_length))
later = [(a, b) for _who, a, b in truth if a > edge]
found = [(a, b) for a, b in later
         if any(a <= w["start"] and w["end"] <= b for w in words)]
check("the turns spoken in the second block are written down",
      len(later) > 0 and found == later,
      "%d of %d turns after the edge at %.2f s have words; the last "
      "word ends at %.2f s" % (len(found), len(later), edge,
                               max([w["end"] for w in words] or [0.0])))
astray = [w["start"] for w in words
          if not any(a - FRAME <= w["start"] and w["end"] <= b + FRAME
                     for _who, a, b in truth)]
check("and every word lies on the whole recording's time",
      len(words) > 0 and not astray,
      "%d of %d words outside every spoken turn, the first at %s s"
      % (len(astray), len(words), astray[:1] or "-"))
check("the joined file is removed after listening",
      len(asked) == 1 and not os.path.exists(asked[0][0]),
      "the recogniser was handed %s, %s"
      % ([os.path.basename(p) for p, _n in asked],
         "still there" if asked and os.path.exists(asked[0][0])
         else "gone"))

print("\n2. Stored under the whole, and read back")
under_whole, _way = vpm.words_stored(vpm.blocks_content_mark(blocks),
                                     LANGUAGE, ["macOS"])
under_first, _way = vpm.words_stored(vpm.file_content_mark(blocks[0]),
                                     LANGUAGE, ["macOS"])
check("a recording in blocks is stored under the whole, not block one",
      under_whole == words and under_first is None,
      "under the whole %s words, under the first block %s"
      % (None if under_whole is None else len(under_whole),
         None if under_first is None else len(under_first)))
again = {"speakers_source": blocks[0],
         "blocks_of": vpm.ByFile({blocks[0]: list(blocks)})}
words_again, _came = heard_in_window(again)
check("the whole is read back without listening again",
      words_again == words and len(asked) == 1,
      "%s words back against %d, the recogniser asked %d times in all"
      % (None if words_again is None else len(words_again), len(words),
         len(asked)))

print("\n3. A recording in one file")
one = vpm.words_at_hand(talk, LANGUAGE, blocks=[talk])
own, _way = vpm.words_stored(vpm.file_content_mark(talk), LANGUAGE,
                             ["macOS"])
check("a recording in one file is stored under its own content",
      len(one) > 0 and own == one and asked[-1][0] == talk,
      "%d words heard from %s, %s under the file's own content"
      % (len(one), os.path.basename(asked[-1][0]),
         None if own is None else len(own)))

shutil.rmtree(os.environ["VPM_CACHE"], ignore_errors=True)
shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
