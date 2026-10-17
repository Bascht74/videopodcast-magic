# -*- coding: utf-8 -*-
"""A clipped run is counted whole where the file is read in two blocks.

The count streams the audio in blocks of eight MiB, so a run of samples
on the stop can begin in one block and end in the next. The material is
three channels written here, a little longer than one block, with a run
placed on each of the ways a block edge can cut it. In order: the
material is longer than one block, a run straddling the edge counts once
at its whole length, a run ending on the edge counts when the channel
clips again later, and when it stays quiet, a run still open at the end
of the file counts, and the milliseconds follow the longest run. Limit:
the block size is written down here as well -- if the program reads in
other blocks, the runs no longer straddle and the first check says so.
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
import shutil
import tempfile
import time
import wave
import the_program

SCRIPT = the_program.SCRIPT
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
vpm = the_program.load()

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


RATE = 48000
CHANNELS = 3
# Eight MiB in whole frames of three 16 bit samples: 1398101 frames.
EDGE = (8 << 20) // (2 * CHANNELS)
FRAMES = EDGE + RATE
TOP, BOTTOM = 32767, -32768
NOTHING = (0, 0, 0.0, -1.0)

folder = tempfile.mkdtemp(prefix="vpm_clipedge_")
path = os.path.join(folder, "three.wav")
np = vpm.np
if np is not None:
    x = np.zeros((FRAMES, CHANNELS), dtype=np.int16)
    # First channel: five samples across the edge, two before and three
    # after, and four more that are still on the stop when the file ends.
    x[EDGE - 2:EDGE + 3, 0] = TOP
    x[FRAMES - 4:, 0] = TOP
    # Second: three ending exactly on the edge, then four further on.
    x[EDGE - 3:EDGE, 1] = BOTTOM
    x[EDGE + 100:EDGE + 104, 1] = BOTTOM
    # Third: three ending exactly on the edge, and quiet after it.
    x[EDGE - 3:EDGE, 2] = TOP
    w = wave.open(path, "wb")
    w.setnchannels(CHANNELS)
    w.setsampwidth(2)
    w.setframerate(RATE)
    w.writeframes(x.tobytes())
    w.close()
    del x

size = os.path.getsize(path) if os.path.exists(path) else 0
check("the material is longer than one read block",
      size > (8 << 20),
      "%d bytes against a block of %d, numpy %s"
      % (size, 8 << 20, "there" if np is not None else "missing"))

got = vpm.clipping_facts(path) if size else {}
shutil.rmtree(folder, ignore_errors=True)
one, two, three = (got.get(0, NOTHING), got.get(1, NOTHING),
                   got.get(2, NOTHING))

check("a run across the block edge counts once at its whole length",
      one[1] == 5 and abs(one[3] - (EDGE - 2) / float(RATE)) < 1e-9,
      "longest %d samples from %.6f s, wanted 5 from %.6f s"
      % (one[1], one[3], (EDGE - 2) / float(RATE)))
check("a run ending on the edge counts when the channel clips again",
      two[0] == 2 and abs(two[3] - (EDGE - 3) / float(RATE)) < 1e-9,
      "%d runs, first at %.6f s, wanted 2 from %.6f s"
      % (two[0], two[3], (EDGE - 3) / float(RATE)))
check("a run ending on the edge counts when the channel stays quiet",
      three[:2] == (1, 3),
      "%d runs, longest %d samples, wanted 1 run of 3"
      % (three[0], three[1]))
check("a run still on the stop when the file ends is counted",
      one[0] == 2,
      "%d runs on the first channel, wanted 2" % one[0])
check("the milliseconds follow the longest run at the file's rate",
      abs(one[2] - 5000.0 / RATE) < 1e-9 and abs(two[2] - 4000.0 / RATE)
      < 1e-9,
      "%.4f ms and %.4f ms, wanted %.4f and %.4f"
      % (one[2], two[2], 5000.0 / RATE, 4000.0 / RATE))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
