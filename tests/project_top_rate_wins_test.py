# -*- coding: utf-8 -*-
"""The Timeline gets the highest rate in the material, not the longest one's.

Sections against timeline_frame_rate, all from data: which rate wins
among cameras of different rates and that the order they come in does
not matter, that intro and outro are finished clips and no cameras of
the episode, and where no camera rate can be read at all -- then the
reference clip decides as it did before, and with no clip either a 30.
Last, where Resolve has no Timeline at the rate that won, the Timeline
gets the next one up while the files keep counting in their own.
The rates are written out rather than computed, so a wrong comparison
in the program cannot be repeated here.
"""
import argparse
import importlib.util
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
began = time.time()
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.set_language("en")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def video(path, fps, duration):
    """One entry of the videos list, as align_cameras hands it on."""
    return (path, {"fps": fps, "duration": duration})


HOST = video("/m/CamHost24.mov", 24.0, 4000.0)
GUEST = video("/m/CamGuest25.mov", 25.0, 3000.0)
WIDE = video("/m/CamWide30.mov", 30.0, 2000.0)
INTRO = video("/m/Intro60.mov", 60.0, 8.0)
OUTRO = video("/m/Outro50.mov", 50.0, 12.0)
plain = argparse.Namespace(intro=None, outro=None)

print("\n1. The highest of them wins, whichever ran longest")
rate = vpm.timeline_frame_rate(plain, [HOST, GUEST, WIDE], HOST)
check("the highest rate wins over the rate of the longest recording",
      rate == 30.0,
      "%s against 30.0, from 24/25/30 with the 24 running longest" % rate)
rate = vpm.timeline_frame_rate(plain, [WIDE, GUEST, HOST], WIDE)
check("and it does not depend on the order the cameras come in",
      rate == 30.0,
      "%s against 30.0, from the same three in the other order" % rate)
rate = vpm.timeline_frame_rate(plain, [HOST, GUEST], HOST)
check("with no 30 among them the fastest that is there wins",
      rate == 25.0, "%s against 25.0, from 24/25" % rate)
rate = vpm.timeline_frame_rate(plain, [WIDE, WIDE], WIDE)
check("one rate throughout stays that rate",
      rate == 30.0, "%s against 30.0, from 30/30" % rate)

print("\n2. Intro and outro are no cameras of the episode")
edges = argparse.Namespace(intro=INTRO[0], outro=OUTRO[0])
rate = vpm.timeline_frame_rate(edges, [HOST, GUEST, WIDE, INTRO, OUTRO], HOST)
check("a 60 intro does not pull the Timeline up to 60",
      rate == 30.0,
      "%s against 30.0, cameras 24/25/30 with a 60 intro and a 50 outro"
      % rate)
one_edge = argparse.Namespace(intro=None, outro=OUTRO[0])
rate = vpm.timeline_frame_rate(one_edge, [HOST, GUEST, OUTRO], HOST)
check("a 50 outro does not pull it up either",
      rate == 25.0,
      "%s against 25.0, cameras 24/25 with a 50 outro" % rate)
rate = vpm.timeline_frame_rate(edges, [INTRO, OUTRO], HOST)
check("with nothing but intro and outro the reference clip decides",
      rate == 24.0,
      "%s against the 24 of the reference clip, only a 60 intro and a 50 "
      "outro in the list" % rate)

print("\n3. Where nothing can be read the old rule stands")
rate = vpm.timeline_frame_rate(plain, [], GUEST)
check("no cameras at all leaves the rate of the reference clip",
      rate == 25.0, "%s against the 25 of the reference clip" % rate)
rate = vpm.timeline_frame_rate(plain, [("/m/x.mov", {"duration": 10.0})],
                               GUEST)
check("a camera whose rate could not be measured leaves it there too",
      rate == 25.0,
      "%s against the 25 of the reference clip, one camera without a rate"
      % rate)
rate = vpm.timeline_frame_rate(plain, [], None)
check("without a reference clip either it falls back to 30",
      rate == 30.0, "%s against 30.0, nothing to read anywhere" % rate)
rate = vpm.timeline_frame_rate(plain, None, GUEST)
check("no list at all is the same as an empty one",
      rate == 25.0, "%s against the 25 of the reference clip" % rate)

print("\n4. A rate Resolve has no Timeline at gets the next one up")
got = vpm.resolve_timeline_rate(15.0)
check("a 15 camera puts the Timeline on 16, the next rate up",
      got == 16.0, "%s against 16.0, from 15" % got)
got = vpm.resolve_timeline_rate(20.0)
check("the next one up and not the nearest, which for 20 lies below",
      got == 23.976,
      "%s against 23.976, from 20 -- the nearest is 18" % got)
got = vpm.resolve_timeline_rate(240.0)
check("above the fastest rate Resolve has it stops at 120",
      got == 120.0, "%s against 120.0, from 240" % got)
got = vpm.resolve_timeline_rate(25.0)
check("a rate Resolve does have is kept as it is",
      got == 25.0, "%s against 25.0, from 25" % got)
got = vpm.resolve_timeline_rate(23.98)
check("and a measured reading counts as the rate it means",
      got == 23.976, "%s against 23.976, from a measured 23.98" % got)
got = vpm.resolve_timeline_rate(0)
check("nothing to read leaves the Timeline at 30",
      got == 30.0, "%s against 30.0, from no rate at all" % got)
got = vpm.own_frame_rate(15.0)
check("a camera at 15 keeps 15, it is not moved to a rate Resolve has",
      got == 15.0,
      "%s against 15.0 -- the nearest Resolve rate is 16" % got)
got = vpm.own_frame_rate(24.0115)
check("but a measured 24.0115 is the 24 it means",
      got == 24.0, "%s against 24.0, from a measured 24.0115" % got)
got = vpm.known_frame_rate(15.0)
check("15 is named as a rate Resolve has no Timeline at",
      got is None, "%s against None, from 15" % got)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
