# -*- coding: utf-8 -*-
"""The frame of the project is one a camera really recorded.

Width and height were each taken as their own maximum, so a landscape
and a portrait camera together gave a square frame neither of them had.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import sys, time
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


check("landscape beside portrait",
      vpm.widest_frame({(1920, 1080), (1080, 1920)}) in
      ((1920, 1080), (1080, 1920)),
      str(vpm.widest_frame({(1920, 1080), (1080, 1920)})))
larger = vpm.widest_frame({(1920, 1080), (3840, 2160)})
check("the larger of two landscape frames", larger == (3840, 2160),
      "%s, wanted (3840, 2160)" % (larger,))
nothing = vpm.widest_frame(set())
check("nothing measured", nothing == (None, None),
      "%s, wanted (None, None)" % (nothing,))
alone = vpm.widest_frame({(1280, 720)})
check("one camera", alone == (1280, 720), "%s, wanted (1280, 720)" % (alone,))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
