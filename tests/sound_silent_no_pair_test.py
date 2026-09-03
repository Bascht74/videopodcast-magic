# -*- coding: utf-8 -*-
"""A silent channel is never one side of a stereo track.

A tick set by hand outlives the measurement, and after a block is
taken away the channel it paired may carry nothing at all.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import importlib.util, sys, time
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


# A tick made earlier outlives the measurement: take a block away and a
# channel that carried something may be silent now.
f = {"channels": 3, "silent": [False, False, True], "readable": True,
     "level": [-20.0, -20.0, -120.0],
     "pair_same": [0.0, None], "pair_zero": [0.1, None],
     "pair_apart": [0.0, None]}
check("the stored tick is not honoured against a silent channel",
      vpm.joined_channels(f, {1: True}) == {},
      str(vpm.joined_channels(f, {1: True})))
tracks = vpm.channel_tracks(f, "X", {1: True})
check("so channel 2 stays a track of its own",
      [t[0] for t in tracks] == [(0,), (1,), (2,)],
      str([t[0] for t in tracks]))
live = {"channels": 3, "silent": [False, False, False], "readable": True,
        "level": [-20.0, -20.0, -20.0],
        "pair_same": [0.0, 0.0], "pair_zero": [0.1, 0.1],
        "pair_apart": [0.0, 0.0]}
joined_live = vpm.joined_channels(live, {1: True})
check("where both carry something the tick still counts",
      joined_live == {1: True},
      "%s against an expected {1: True}" % (joined_live,))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
