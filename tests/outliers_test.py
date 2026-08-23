# -*- coding: utf-8 -*-
"""One sample point in the wrong place must not tip the whole line.

The alignment measures the offset at several places over the runtime
and lays a line through them; the slope of that line is the clock
drift. The search window is +/- 2 s, so on periodic material -- a
jingle, a beat -- it finds the neighbouring beat as easily as the right
one, and a single such point used to drag the line with it.

Measured before this test was written (nine points, one hour, real
drift 10 ppm): one point 500 ms out in the middle moved the offset by
56 ms; at the start of the recording by 189 ms, and it turned +10 ppm
into -64 ppm -- the wrong sign, so the drift would have been corrected
the wrong way. A point at the edge pulls harder than one in the middle,
which is where the jingle sits.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
import importlib.util
import numpy as np
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

TIMES = np.linspace(0, 3600, 9)
DRIFT = 10e-6
CLEAN = 0.0 + DRIFT * TIMES

def line_through(tv, dt):
    b, a = np.polyfit(tv, dt, 1)
    return a * 1000, b * 1e6          # offset in ms, drift in ppm

print("1. Nothing is thrown away that does not deserve it")
tv, dt, gone = vpm.without_outliers(TIMES, CLEAN)
check("a clean set keeps every point", len(tv) == len(TIMES), str(len(tv)))
check("and nothing is reported as dropped", not gone, str(gone))
off, ppm = line_through(tv, dt)
check("offset stays at zero", abs(off) < 0.1, "%.3f ms" % off)
check("drift stays at 10 ppm", abs(ppm - 10.0) < 0.01, "%.2f ppm" % ppm)

print("\n2. One point out of place, and where it sits")
# The three places a wrong point can sit. The edges are the dangerous
# ones: a point at the end of a line pulls harder than one in the
# middle, and that is exactly where an opening jingle lies.
for where, name in ((0, "at the start"), (4, "in the middle"),
                    (8, "at the end")):
    bent = CLEAN.copy()
    bent[where] += 0.500
    was_off, was_ppm = line_through(TIMES, bent)
    tv, dt, gone = vpm.without_outliers(TIMES, bent)
    now_off, now_ppm = line_through(tv, dt)
    check("%s: the bad point is found" % name, len(gone) == 1,
          "%d dropped" % len(gone))
    check("%s: the offset comes back" % name, abs(now_off) < 1.0,
          "%.1f ms before, %.1f ms after" % (was_off, now_off))
    check("%s: the drift comes back" % name, abs(now_ppm - 10.0) < 0.1,
          "%.2f ppm before, %.2f ppm after" % (was_ppm, now_ppm))

print("\n3. What it refuses to do")
# Two points always fit a line perfectly. Cleaning down to two would
# turn a broken measurement into a confident one, which is worse than
# the measurement it started from.
scattered = CLEAN + np.array([0, .4, -.4, .5, -.5, .45, -.45, .4, -.4])
tv, dt, gone = vpm.without_outliers(TIMES, scattered)
check("a set that is scattered all over keeps at least three",
      len(tv) >= 3, "%d left" % len(tv))
few = TIMES[:3], CLEAN[:3] + np.array([0, 0.5, 0])
tv, dt, gone = vpm.without_outliers(*few)
check("three points are never cut down further", len(tv) == 3,
      "%d left" % len(tv))

print("\n4. The raw scatter is not lost")
# Cleaning up and then calling the result good would trade a loud fault
# for a quiet one. What was thrown away has to reach the report.
bent = CLEAN.copy()
bent[4] += 0.500
tv, dt, gone = vpm.without_outliers(TIMES, bent)
check("the dropped point is named with its time", gone and gone[0][0] > 0,
      str(gone))
check("and with how far out it was",
      gone and abs(abs(gone[0][1]) - 500) < 120, str(gone))

print("\n5. How much of the runtime is still covered")
check("a full set covers everything",
      abs(vpm._spans_share(TIMES, 3600.0) - 1.0) < 0.01)
check("a set cleaned down to one corner says so",
      vpm._spans_share(TIMES[:3], 3600.0) < 0.3,
      "%.2f" % vpm._spans_share(TIMES[:3], 3600.0))

print("\nAll good." if not error else "\nFAIL: %s" % ", ".join(error))
sys.exit(1 if error else 0)
