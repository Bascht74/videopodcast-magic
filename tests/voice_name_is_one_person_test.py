# -*- coding: utf-8 -*-
"""A name that comes twice is one person in the cut, not two.

Since a separation and a microphone can both deliver a speaker, one
name can reach the cut from two directions at once -- her own track and
a voice told apart under a recording. Two entries of one name are two
people to everything downstream: the camera they share stands twice at
different places in the same cut.

In order: one name arriving twice becomes one entry, that entry holds
the passages of both arrivals, its passages stand in the order they
happened whichever order they came in, and two different names stay two.

Held against values written out here rather than against a second pass
over the input: a loop that works the expectation out usually works it
out the way the program does.
"""
import os
import sys
import time

import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT

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


# Anna arrives twice: once out of a separation, once off her own
# microphone. The later arrival is put in front on purpose, so that the
# order of the passages cannot come out right by being left alone.
ROWS = [("Anna", [(30.0, 45.0)]),
        ("Bea", [(15.0, 30.0)]),
        ("Anna", [(0.0, 10.0), (50.0, 60.0)])]
# What has to come out, written down and not computed.
WANTED_NAMES = ["Anna", "Bea"]
WANTED_ANNA = [(0.0, 10.0), (30.0, 45.0), (50.0, 60.0)]
WANTED_BEA = [(15.0, 30.0)]

out = vpm.voices_merged(ROWS)
names = [n for n, _p in out]
parts = dict(out)
print("   ", out)

print("1. One name, one person")
check("a name that came twice stands in the cut once",
      names.count("Anna") == 1, "Anna stands %d times in %s, wanted once"
      % (names.count("Anna"), names))
check("and that one entry holds the passages of both arrivals",
      sorted(parts.get("Anna") or ()) == sorted(WANTED_ANNA),
      "%d passages %s, wanted %d %s"
      % (len(parts.get("Anna") or ()), parts.get("Anna"),
         len(WANTED_ANNA), WANTED_ANNA))
check("and they stand in the order they happened",
      list(parts.get("Anna") or ()) == WANTED_ANNA,
      "in this order %s, wanted %s" % (parts.get("Anna"), WANTED_ANNA))

print("\n2. And two names stay two")
check("a second name is a second person, with its own passages",
      names == WANTED_NAMES and list(parts.get("Bea") or ()) == WANTED_BEA,
      "%d names %s with Bea on %s, wanted %d %s with Bea on %s"
      % (len(names), names, parts.get("Bea"),
         len(WANTED_NAMES), WANTED_NAMES, WANTED_BEA))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
