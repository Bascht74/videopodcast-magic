# -*- coding: utf-8 -*-
"""The phase way places a file starting past half of the pair's length.

A lag can run from minus the first file's length to plus the second's;
halving the transform instead put such a file a whole transform length
out. In order: a recording that starts late in the camera and shares
only its last minute, and the other way round, the camera starting late
in the recording. Generated noise at a low rate, no file and no ffmpeg;
the gate that decides whether the phase is believed is not asked here.
"""
PLATFORM_BOUND = False
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import time
import numpy as np
import the_program

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


RATE = 1000
rng = np.random.default_rng(193)
# One true time line of 840 s; each file hears it with its own hiss.
line = rng.normal(0, 1, 840 * RATE)


def heard(t0, t1, seed):
    """The stretch t0..t1 s of the line, with a hiss of its own."""
    part = line[t0 * RATE:t1 * RATE]
    return part + np.random.default_rng(seed).normal(0, 0.3, len(part))


camera = heard(0, 600, 1)
# A recording of 300 s beginning 540 s into a 600 s camera: 60 s shared.
where, sharp = vpm.phase_align(camera, heard(540, 840, 2), RATE)
check("a recording starting late in the camera is placed right",
      abs(where - (-540.0)) < 0.01,
      "placed at %+.3f s, wanted -540.000 s (sharpness %.1f)"
      % (where, sharp))

# The same pair the other way round: the camera starts late in it.
where, sharp = vpm.phase_align(heard(540, 840, 3), camera, RATE)
check("a camera starting late in the recording is placed right",
      abs(where - 540.0) < 0.01,
      "placed at %+.3f s, wanted +540.000 s (sharpness %.1f)"
      % (where, sharp))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
