# -*- coding: utf-8 -*-
"""Speech is found back where it was put, offset and all.

Two tracks take turns over a quiet floor, at times written here as
values: every track comes back with a row of its own, each holds the
three sections it was made from, no edge moved over a third of a
second, and a track handed in with an offset comes back on the axis it
puts it on; then a third, alone, its breath of 0.6 s bridged and its
pause of 0.9 s not -- written out, as they pin the program's own bridge.
The material is modulated noise: the pattern of loudness is measured,
not speech.
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
import sys, tempfile, time, wave
import numpy as np
sys.path.insert(0, HERE)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def worst_edge(segments, meant, name):
    """How far the furthest edge sits from where it was put, and where.

    Only the pairs that exist are looked at; that there are as many as
    were put in is a judgement of its own and stands before this.
    """
    off, where, edges = 0.0, "", 0
    for (a, b), (sa, sb) in zip(segments, meant):
        for got, want_at, side in ((a, sa, "begins"), (b, sb, "ends")):
            edges += 1
            if abs(got - want_at) > off:
                off, where = abs(got - want_at), (
                    "%s %s at %.2f s instead of %.2f s"
                    % (name, side, got, want_at))
    return off, where, edges


m = the_program.load()

# Written here, so a folder of its own and not the shared fixture root,
# which every other test only reads.
D = tempfile.mkdtemp(prefix="vpm_speakertest_")
SR = 48000
EDGE = 0.3            # how far an edge may sit from where it was put
OFFSET = 100.0        # what the second run hands in as the track's start
# Two tracks that take turns "talking" (noise) over a quiet floor, and a
# third for the bridge.
want = {"A": [(1.0, 4.0), (8.0, 11.5), (16.0, 18.0)],
        "B": [(5.0, 7.5), (12.0, 15.0), (19.0, 22.0)],
        # One passage, a breath of 0.6 s inside it, then a pause of 0.9 s
        # before the next. Built after A and B, so theirs stay as they were.
        "C": [(1.0, 3.0), (3.6, 5.6), (6.5, 8.5)]}
rng = np.random.default_rng(3)
for name, parts in want.items():
    x = rng.normal(0, 0.002, int(24 * SR))          # noise floor
    for a, b in parts:
        n = int((b - a) * SR)
        # Speech: modulated noise, clearly louder
        x[int(a*SR):int(a*SR)+n] += rng.normal(0, 0.12, n) * (
            0.6 + 0.4 * np.sin(np.linspace(0, 40, n)))
    p = "%s/%s.wav" % (D, name)
    with wave.open(p, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())

print("1. The turns are found again")
out = m.speakers_from_tracks([("A", "%s/A.wav" % D, 0.0),
                              ("B", "%s/B.wav" % D, 0.0)], report=print)
rows = [name for name, _segs in out]
found = dict(out)
for name, segs in out:
    print("   %s: %s" % (name, [("%.2f-%.2f" % (a, b)) for a, b in segs]))
check("both tracks come back, each with a row of its own",
      rows == ["A", "B"], "%d rows %s against 2 wanted ['A', 'B']"
      % (len(rows), rows))
check("track A comes back as the three sections it was made from",
      len(found.get("A", [])) == 3,
      "%d sections against 3 put in" % len(found.get("A", [])))
check("track B comes back as the three sections it was made from",
      len(found.get("B", [])) == 3,
      "%d sections against 3 put in" % len(found.get("B", [])))
off_a, where_a, edges_a = worst_edge(found.get("A", []), want["A"], "A")
off_b, where_b, edges_b = worst_edge(found.get("B", []), want["B"], "B")
off, where = max((off_a, where_a), (off_b, where_b))
check("every edge sits within a third of a second of where it was put",
      off <= EDGE, "worst %.2f s against %.2f s allowed, over %d edges of "
      "12 -- %s"
      % (off, EDGE, edges_a + edges_b, where or "no edge moved at all"))

print("\n2. The offset is added on")
v = m.speakers_from_tracks([("A", "%s/A.wav" % D, OFFSET)])
moved = dict(v).get("A", [])
print("   A handed in at %.2f s: %s"
      % (OFFSET, [("%.2f-%.2f" % (a, b)) for a, b in moved]))
check("a track handed in with an offset still comes back as three sections",
      len(moved) == 3, "%d sections against 3 put in" % len(moved))
shifted = [(a + OFFSET, b + OFFSET) for a, b in want["A"]]
off_m, where_m, edges_m = worst_edge(moved, shifted, "A")
check("every section is moved by the offset the track was handed in with",
      off_m <= EDGE, "worst %.2f s against %.2f s allowed, over %d edges of "
      "6 -- %s" % (off_m, EDGE, edges_m, where_m or "no edge moved at all"))

print("\n3. A breath is bridged, a pause is not")
c = dict(m.speakers_from_tracks([("C", "%s/C.wav" % D, 0.0)])).get("C", [])
print("   C: %s" % [("%.2f-%.2f" % (a, b)) for a, b in c])
BRIDGED = [(1.0, 5.6), (6.5, 8.5)]
off_c, where_c, edges_c = worst_edge(c, BRIDGED, "C")
check("a breath of 0.6 s is bridged, a pause of 0.9 s is not",
      len(c) == 2 and off_c <= EDGE,
      "%d sections %s against 2 wanted %s, worst edge %.2f s against %.2f s"
      % (len(c), [("%.2f-%.2f" % (a, b)) for a, b in c],
         [("%.2f-%.2f" % (a, b)) for a, b in BRIDGED], off_c, EDGE))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
