# -*- coding: utf-8 -*-
"""Doing several things at once: in order, complete, and honest about errors."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys, threading, time
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

print("1. The answers come back where they belong")
got = vpm.parallel_map(range(12), lambda x: x * x)
check("every item is worked on", len(got) == 12, len(got))
check("and in the order it went in", got == [x * x for x in range(12)],
      str(got))

print("\n2. One item needs no threads at all")
before = threading.active_count()
check("one item", vpm.parallel_map([7], lambda x: x + 1) == [8])
check("nothing left running", threading.active_count() == before)
check("no items", vpm.parallel_map([], lambda x: x) == [])

print("\n3. It really is at the same time")
def slow(_x):
    time.sleep(0.25)
    return 1
t0 = time.time()
vpm.parallel_map(range(8), slow, workers=8)
side = time.time() - t0
t0 = time.time()
vpm.parallel_map(range(8), slow, workers=1)
row = time.time() - t0
check("eight quarter seconds take under a second side by side",
      side < 1.0, "%.2f s" % side)
check("and about two seconds one after another", row > 1.6,
      "%.2f s" % row)

print("\n4. An error is passed on, and the rest still done")
touched = []
def sometimes(x):
    touched.append(x)
    if x == 3:
        raise ValueError("no")
    return x
try:
    vpm.parallel_map(range(6), sometimes, workers=2)
    check("the error comes out", False, "nothing raised")
except ValueError as e:
    check("the error comes out", str(e) == "no", str(e))
check("and everything was still tried", sorted(touched) == list(range(6)),
      str(sorted(touched)))

print("\n5. Without threads the work is still done")
real = threading.Thread
class Refuses(object):
    def __init__(self, *a, **k):
        pass
    def start(self):
        raise RuntimeError("no threads today")
    def join(self, timeout=None):
        pass
threading.Thread = Refuses
try:
    got = vpm.parallel_map(range(5), lambda x: x + 100)
finally:
    threading.Thread = real
check("all of it, in order", got == [100, 101, 102, 103, 104], str(got))

print("\n6. The count of workers is bounded by the work")
before = threading.active_count()
vpm.parallel_map(range(3), lambda x: x, workers=50)
check("three items do not start fifty threads",
      threading.active_count() <= before + 1, threading.active_count())

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
