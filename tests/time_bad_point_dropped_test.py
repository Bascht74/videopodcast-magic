# -*- coding: utf-8 -*-
"""One sample point in the wrong place must not tip the whole line.

The alignment lays a line through offsets measured at several places;
its slope is the clock drift. The search window is +/- 2 s, so on
periodic material it can find the neighbouring beat as easily as the
right one, and one such point used to drag the line with it.

The sections: what survives untouched, one point moved and where it
sits, a second point hidden behind a bigger one, what the report says,
how much of the runtime is left. Every set is nine offsets over an
hour, and one of them carries ordinary measurement noise -- a line to
the millisecond is not what a measurement looks like, and a tolerance
read off the scatter has to be tried against scatter.

What it does not reach: a wrong point at the very first or very last
sample, on noisy material. The line tilts to swallow it, and the
program keeps it. Measured over a couple of thousand draws of noise it
stays in more than half of them, against well under one percent in the
middle -- so the edges are tried on a quiet set here, and that is a
gap in the program, written up in the notes rather than papered over.

A rule that closes it weighs how hard each point pulls on the line,
and pays for that: on a bent set the widest ordinary point can go
along with the bent one. This file allows it. One draw of noise cannot
tell such a rule from a tolerance simply tightened too far -- both
throw away the same second point and leave the same line -- so the
bent draw asks only that the bent point is the one reported and taken
out, and over-eagerness is judged on the quiet draw alone.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
import importlib.util
import numpy as np
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))

TIMES = np.linspace(0, 3600, 9)
DRIFT = 10e-6
CLEAN = 0.0 + DRIFT * TIMES

# One draw of ordinary measurement noise, in seconds, written out so
# that the run is the same every time. Measured against the program as
# it stands: the robust spread of these nine is 58.6 ms, and the widest
# of them lies 2.21 spreads out -- inside a tolerance of three spreads,
# outside one of two.
NOISE = CLEAN + np.array(
    [-0.055, 0.105, 0.020, -0.025, -0.080, -0.005, -0.005, 0.045, 0.070])


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
# A measurement is never a line to the millisecond. If the tolerance is
# read off the scatter of the points themselves, ordinary noise has to
# survive it -- and something well outside that noise must still go.
tv, dt, gone = vpm.without_outliers(TIMES, NOISE)
check("ordinary scatter costs no point", len(tv) == len(TIMES) and not gone,
      "%d of 9 kept, %d dropped" % (len(tv), len(gone)))
noisy_far = NOISE.copy()
noisy_far[4] += 0.500
tv, dt, gone = vpm.without_outliers(TIMES, noisy_far)
# Which point goes, and that it really goes -- not how many. On this
# one draw a rule that weighs how hard a point pulls on the line takes
# the widest ordinary point along with the bent one, and so does a
# tolerance tightened to 2.5 spreads: same two points, same line back.
# A count here would read the same for both and turn the first of them
# red. Over-eagerness is judged on the quiet draw above.
gone_at = sorted(round(g[0]) for g in gone)
kept_at = sorted(round(t) for t in tv)
check("and the point beyond that scatter is the one that goes",
      1800 in gone_at and 1800 not in kept_at,
      "dropped at %s s, kept at %s s, wanted 1800 s dropped and not kept"
      % (gone_at, kept_at))

print("\n2. One point out of place, and where it sits")
# The three places a wrong point can sit. Written out one by one: a
# name built in a loop leaves one wording for three judgements, and the
# register cannot then say which of them was ever seen red.
start = CLEAN.copy(); start[0] += 0.500
was_off, was_ppm = line_through(TIMES, start)
tv, dt, gone = vpm.without_outliers(TIMES, start)
now_off, now_ppm = line_through(tv, dt)
check("a bad point at the start is found", len(gone) == 1,
      "%d dropped" % len(gone))
check("at the start the offset comes back", abs(now_off) < 1.0,
      "%.1f ms before, %.1f ms after" % (was_off, now_off))
check("at the start the drift comes back", abs(now_ppm - 10.0) < 0.1,
      "%.2f ppm before, %.2f ppm after" % (was_ppm, now_ppm))

middle = CLEAN.copy(); middle[4] += 0.500
was_off, was_ppm = line_through(TIMES, middle)
tv, dt, gone = vpm.without_outliers(TIMES, middle)
now_off, now_ppm = line_through(tv, dt)
check("a bad point in the middle is found", len(gone) == 1,
      "%d dropped" % len(gone))
check("in the middle the offset comes back", abs(now_off) < 1.0,
      "%.1f ms before, %.1f ms after" % (was_off, now_off))
# There is no third judgement here on purpose. The middle sample sits
# at the mean of the times, so it has no pull on the slope at all: the
# drift reads 10 ppm whether the point is thrown out or left in, and a
# judgement on it would be green against every possible program.

end = CLEAN.copy(); end[8] += 0.500
was_off, was_ppm = line_through(TIMES, end)
tv, dt, gone = vpm.without_outliers(TIMES, end)
now_off, now_ppm = line_through(tv, dt)
check("a bad point at the end is found", len(gone) == 1,
      "%d dropped" % len(gone))
check("at the end the offset comes back", abs(now_off) < 1.0,
      "%.1f ms before, %.1f ms after" % (was_off, now_off))
check("at the end the drift comes back", abs(now_ppm - 10.0) < 0.1,
      "%.2f ppm before, %.2f ppm after" % (was_ppm, now_ppm))

print("\n3. One round is not enough")
# A beat and a half out at 450 s, half a beat out at 3150 s. The big
# one widens the spread so much that the small one still looks ordinary
# -- it only shows once the big one is gone, which takes a second pass.
masked = CLEAN.copy()
masked[1] += 1.500
masked[7] += 0.500
was_off, was_ppm = line_through(TIMES, masked)
tv, dt, gone = vpm.without_outliers(TIMES, masked)
now_off, now_ppm = line_through(tv, dt)
# The times, not the count: the count was green while the two reported
# places were an index and a minute.
gone_at = sorted(round(g[0]) for g in gone)
check("the point hidden behind a bigger one is found as well",
      gone_at == [450, 3150],
      "dropped at %s s, wanted [450, 3150]" % gone_at)
check("and the drift comes back from both", abs(now_ppm - 10.0) < 0.1,
      "%.2f ppm before, %.2f ppm after" % (was_ppm, now_ppm))

print("\n4. The raw scatter is not lost")
# Cleaning silently would trade a loud fault for a quiet one.
bent = CLEAN.copy()
bent[4] += 0.500
tv, dt, gone = vpm.without_outliers(TIMES, bent)
check("the dropped point is named with its time",
      len(gone) == 1 and abs(gone[0][0] - 1800.0) < 1e-9,
      "%s, wanted one at 1800.0 s" % str(gone))
check("and with how far out it was",
      gone and abs(abs(gone[0][1]) - 500) < 120, str(gone))

print("\n5. How much of the runtime is still covered")
# The last three points, not the first three: a share measured from
# zero cannot tell the covered span from the last time in it.
whole = vpm._spans_share(TIMES, 3600.0)
check("a full set covers everything", abs(whole - 1.0) < 0.01,
      "%.3f of the runtime, wanted 1.000" % whole)
corner = vpm._spans_share(TIMES[6:], 3600.0)
check("a set cleaned down to one corner says so", corner < 0.3,
      "%.2f of the runtime over 2700 s to 3600 s, wanted 0.25" % corner)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
