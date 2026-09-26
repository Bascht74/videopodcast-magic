# -*- coding: utf-8 -*-
"""Speakers heard in one shot are named in the order a person reads.

Three people talk at once -- "anna", "Bert" and a name opening on an O
with an umlaut -- where plain sorting puts Bert before anna and the O
after Z. The sections: the detailed cut names them in that order; the
cut split at the change of speaker does too; and a shot too short to
stand, taken into its neighbour, leaves the joined shot in the same
order. The wanted names are written out, not read off name_order.
"""
PLATFORM_BOUND = False
import os
import sys
import time
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import the_program

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


UMLAUT = "\u00d6sten"
READ = ("anna", "Bert", UMLAUT)
# All three on one camera, from the first second to the tenth.
TRACKS = [(UMLAUT, [(0.0, 10.0)]), ("Bert", [(0.0, 10.0)]),
          ("anna", [(0.0, 10.0)])]
ONE = {UMLAUT: "Cam", "Bert": "Cam", "anna": "Cam"}

print("1. The detailed cut")
detail = vpm.camera_cut_detail(TRACKS, 10.0, ONE, "Wide", min_len=0.5,
                               lead_in=0.0,
                               rules=vpm.cut_rules(min_speech=0.5))
named = [r[3] for r in detail]
check("three talking at once stand in the order a person reads",
      named == [READ], "%s, wanted [%s]" % (named, READ))

print("\n2. Split at the change of speaker")
split = vpm.split_shots_by_speaker([(0.0, 10.0, "Cam")], TRACKS, 0.5)
named = [r[3] for r in split]
check("and the cut split at the change of speaker names them so too",
      named == [READ], "%s, wanted [%s]" % (named, READ))

print("\n3. A short shot taken into its neighbour")
# Two on the first camera for ten seconds, then one on another for a
# second -- too short to stand, so it goes back into the shot before.
joined = vpm.merge_short_shots([[0.0, 10.0, "Cam", (UMLAUT, "Bert")],
                                [10.0, 11.0, "CamB", ("anna",)]], 3.0)
named = [tuple(r[3]) for r in joined]
check("and a joined shot names both halves in that order",
      named == [READ], "%s, wanted [%s]" % (named, READ))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
