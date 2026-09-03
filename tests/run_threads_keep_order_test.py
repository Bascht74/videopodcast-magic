# -*- coding: utf-8 -*-
"""Doing several things at once: in order, complete, and honest about errors.

In order: twelve items come back answered and in the order they went in.
Short path: fewer than two items are worked on in the calling thread.
Side by side: eight quarter-second items take under a second together and
leave no thread running behind them. Errors: the work's error comes back
out of the call and every item is still tried. No threads: where none can
be started the work is done anyway. Bounded: three items start three
threads, not the fifty that were asked for. The two timings are wall
clock, with limits wide enough that a busy machine does not turn them red.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
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


MAIN = threading.main_thread().name

print("1. The answers come back where they belong")
# Written out rather than computed: a loop that works out the expectation
# usually works it out as wrongly as the program does.
SQUARES = [0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121]
got = vpm.parallel_map(range(12), lambda x: x * x)
check("twelve items give twelve answers", len(got) == 12,
      "%d answers against 12 items" % len(got))
# The length alone proves nothing: the list is made the right size before
# any work is done, so a place nobody worked on stays a None inside it.
check("every one of the twelve items really was worked on",
      got.count(None) == 0,
      "%d of %d answers still empty" % (got.count(None), len(got)))
check("the answers come back in the order the items went in",
      got == SQUARES, "%s against %s" % (got, SQUARES))

print("\n2. Fewer than two items need no thread at all")
where = []


def note(x):
    where.append(threading.current_thread().name)
    return x + 1


one = vpm.parallel_map([7], note)
check("a single item gives back the one answer the work made",
      one == [8], "%s against [8]" % (one,))
check("a single item is worked on in the calling thread, not a new one",
      where == [MAIN], "%s against ['%s']" % (where, MAIN))
none = vpm.parallel_map([], lambda x: x)
check("no items give no answers", none == [], "%s against []" % (none,))

print("\n3. It really is at the same time")


def slow(_x):
    time.sleep(0.25)
    return 1


EIGHT = [1, 1, 1, 1, 1, 1, 1, 1]
before = threading.active_count()
t0 = time.time()
side_got = vpm.parallel_map(range(8), slow, workers=8)
side = time.time() - t0
running = threading.active_count()
# Asked first: a call that comes back early with half the answers missing
# is quick for the wrong reason, and the clock alone would call it green.
check("eight items run side by side all come back answered",
      side_got == EIGHT, "%s against %s" % (side_got, EIGHT))
check("eight quarter-second items take under a second side by side",
      side < 1.0, "%.2f s against a limit of 1.00 s" % side)
check("no worker thread is still running once the answers are back",
      running == before,
      "%d threads against the %d there were before" % (running, before))
t0 = time.time()
vpm.parallel_map(range(8), slow, workers=1)
row = time.time() - t0
check("the same eight one after another take the whole two seconds",
      row > 1.6, "%.2f s against a floor of 1.60 s" % row)

print("\n4. An error is passed on, and the rest still done")
ALL_SIX = [0, 1, 2, 3, 4, 5]
touched = []


def sometimes(x):
    touched.append(x)
    if x == 3:
        raise ValueError("no")
    return x


raised = None
try:
    vpm.parallel_map(range(6), sometimes, workers=2)
except BaseException as e:      # noqa: BLE001 -- judged below, not swallowed
    raised = e
saw = "nothing raised"
if raised is not None:
    saw = "%s: %s" % (type(raised).__name__, raised)
check("an error in the work does not stay inside the call",
      raised is not None, "%s against the wanted ValueError: no" % saw)
check("the error that comes out is the one the work raised",
      isinstance(raised, ValueError) and str(raised) == "no",
      "%s against the wanted ValueError: no" % saw)
check("every item is still tried after one of them fails",
      sorted(touched) == ALL_SIX,
      "%s against %s" % (sorted(touched), ALL_SIX))

print("\n5. Without threads the work is still done")
HUNDRED = [100, 101, 102, 103, 104]
refused = []
real_thread = threading.Thread


class Refuses(object):
    def __init__(self, *a, **k):
        pass

    def start(self):
        refused.append(1)
        raise RuntimeError("no threads today")

    def join(self, timeout=None):
        pass


threading.Thread = Refuses
try:
    got = vpm.parallel_map(range(5), lambda x: x + 100)
except BaseException as e:      # noqa: BLE001 -- judged below, not swallowed
    got = "%s: %s" % (type(e).__name__, e)
finally:
    threading.Thread = real_thread
# Whether the refusal was reached at all comes first: a run that quietly
# took the short path never met a thread, and the answers would be right
# without any of this having been tried.
check("a run with no thread startable really reaches the refusal",
      len(refused) >= 1, "%d refusals against at least 1" % len(refused))
check("with no thread startable every item is worked on, in order",
      got == HUNDRED, "%s against %s" % (got, HUNDRED))

print("\n6. The count of threads follows the work, not the wish")
THREE = [0, 1, 2]
started = []


class Counted(real_thread):
    # The real thread with a counter on it, so the stand-in can allow
    # nothing the program would not get anyway.
    def start(self):
        started.append(1)
        real_thread.start(self)


threading.Thread = Counted
try:
    got = vpm.parallel_map(range(3), lambda x: x, workers=50)
except BaseException as e:      # noqa: BLE001 -- judged below, not swallowed
    got = "%s: %s" % (type(e).__name__, e)
finally:
    threading.Thread = real_thread
check("three items with fifty workers asked for are all worked on",
      got == THREE, "%s against %s" % (got, THREE))
# Counted as they start, not counted afterwards: the call joins every
# thread it made before it returns, so a look at what is still running
# says the same thing whether three were started or fifty.
check("three items start three threads, not the fifty asked for",
      len(started) == 3,
      "%d threads started for 3 items with 50 asked for, wanted 3"
      % len(started))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
