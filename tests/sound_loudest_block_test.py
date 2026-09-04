# -*- coding: utf-8 -*-
"""The facts of a recording come from its loudest block.

A recording is measured block by block, and the quiet run-out must
not decide what the show measured.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import sys, time
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


def facts(channels, level, pair_zero, pair_same=None, pair_apart=None):
    """A measured block, as channel_facts hands it out."""
    n = len(level)
    return {"channels": channels, "level": list(level),
            "silent": [False] * n, "readable": True,
            "pair_zero": list(pair_zero),
            "pair_same": list(pair_same or [0.0] * (n - 1)),
            "pair_apart": list(pair_apart or [0.0] * (n - 1))}


# The inner loop reused the name of the list it was filling, so the
# answers landed in the block's own list and the loudest was lost.
show = facts(2, [-6.0, -6.0], [0.90])
runout = facts(2, [-40.0, -40.0], [0.10])
out = vpm.blocks_facts_from([show, runout])
check("two blocks, one answer per pair", len(out["pair_zero"]) == 1,
      str(out["pair_zero"]))
check("and it is the loudest block's", abs(out["pair_zero"][0] - 0.90) < 1e-9,
      str(out["pair_zero"]))
other_way = vpm.blocks_facts_from([runout, show])
check("the order of the blocks does not decide",
      other_way["pair_zero"] == out["pair_zero"],
      "%s vs %s" % (other_way["pair_zero"], out["pair_zero"]))
check("and the block it read is left as it was",
      show["pair_zero"] == [0.90] and runout["pair_zero"] == [0.10],
      "%s %s" % (show["pair_zero"], runout["pair_zero"]))
four_show = facts(4, [-6.0] * 4, [0.95, 0.08, 0.93])
four_quiet = facts(4, [-90.0] * 4, [None, None, None])
out4 = vpm.blocks_facts_from([four_show, four_quiet])
check("a block of pure silence does not erase the show",
      out4["pair_zero"] == [0.95, 0.08, 0.93], str(out4["pair_zero"]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
