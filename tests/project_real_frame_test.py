# -*- coding: utf-8 -*-
"""The frame of the project is one a camera really recorded.

Width and height were each taken as their own maximum, so a landscape
and a portrait camera together gave a square frame neither of them had.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys, time
began = time.time()
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
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
check("the larger of two landscape frames",
      vpm.widest_frame({(1920, 1080), (3840, 2160)}) == (3840, 2160))
check("nothing measured", vpm.widest_frame(set()) == (None, None))
check("one camera", vpm.widest_frame({(1280, 720)}) == (1280, 720))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
