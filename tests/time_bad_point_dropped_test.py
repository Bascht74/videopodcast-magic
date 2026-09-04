# -*- coding: utf-8 -*-
"""One sample point in the wrong place must not tip the whole line.

The alignment lays a line through offsets measured at several places;
its slope is the clock drift. The search window is +/- 2 s, so on
periodic material it can find the neighbouring beat as easily as the
right one, and one such point used to drag the line with it.

The sections: what survives untouched, one point moved and where it
sits, a second point hidden behind a bigger one, what the report says,
how much of the runtime is left, a clock far enough out that the line
itself is steep, and a bend small enough to test the floor under the
tolerance. Every set is nine offsets over an hour, and one of them
carries ordinary measurement noise -- a line to the millisecond is not
what a measurement looks like, and a tolerance read off the scatter has
to be tried against scatter.

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
import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
import numpy as np
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
# The two guards in front of that arithmetic. Both cases really arrive
# -- the cleaning can empty a set, and a file whose length was not read
# comes through as zero -- and neither may be answered with a crash or
# with a number: what is wanted is nothing covered.


def share_of(points, runtime):
    """The share, or what went wrong instead -- never swallowed."""
    try:
        return vpm._spans_share(points, runtime)
    except Exception as why:
        return "raised %s: %s" % (type(why).__name__, why)


empty = share_of(np.array([]), 3600.0)
check("no points left covers nothing rather than failing", empty == 0.0,
      "%s, wanted 0.0" % (empty,))
unread = share_of(TIMES, 0.0)
check("and a runtime nobody read covers nothing either", unread == 0.0,
      "%s, wanted 0.0" % (unread,))

print("\n6. A clock that is badly out, so the line itself is steep")
# Everything above lies within a few hundred milliseconds of flat, and
# on such a set the line and the median of the points are almost the
# same anchor. Then not laying the line at all -- fitting it and
# throwing the answer away, or anchoring on the median of the raw
# values -- changes nothing that any judgement can see. A clock 3000
# ppm out runs 10.8 s over the hour, and there the two anchors are
# nowhere near each other.
steep = 3000e-6 * TIMES
steep[8] += 0.500
tv, dt, gone = vpm.without_outliers(TIMES, steep)
now_off, now_ppm = line_through(tv, dt)
gone_at = sorted(round(g[0]) for g in gone)
check("on a steeply drifting clock the bent point is still the odd one",
      gone_at == [3600],
      "dropped at %s s, wanted [3600]" % gone_at)
check("and the steep drift itself comes back", abs(now_ppm - 3000.0) < 0.5,
      "%.2f ppm, wanted 3000.00 ppm" % now_ppm)

print("\n7. A bend small enough to reach the floor of the tolerance")
# On a quiet line the scatter is nothing, so the tolerance is the floor
# under it and nothing else. Every bend above is 500 ms, which clears
# that floor sixteen times over; this one is 150 ms and comes back as a
# 93 ms residual, so it holds the floor down to about a tenth of a
# second. Above that the point is kept, the drift reads wrong, and
# nothing else in the file notices.
small = CLEAN.copy()
small[8] += 0.150
tv, dt, gone = vpm.without_outliers(TIMES, small)
_off, small_ppm = line_through(tv, dt)
gone_at = sorted(round(g[0]) for g in gone)
check("a bend of 150 ms is found and not swallowed by the floor",
      gone_at == [3600], "dropped at %s s, wanted [3600]" % gone_at)
check("so the drift comes back from that one too",
      abs(small_ppm - 10.0) < 0.1, "%.2f ppm, wanted 10.00 ppm" % small_ppm)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
