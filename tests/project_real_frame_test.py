# -*- coding: utf-8 -*-
"""The frame of the project is one a camera really recorded.

Width and height were each taken as their own maximum, so a landscape
and a portrait camera together gave a square frame neither of them had.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
bad = []


def check(what, ok, detail=""):
    print("  %-58s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


check("landscape beside portrait",
      vpm.widest_frame({(1920, 1080), (1080, 1920)}) in
      ((1920, 1080), (1080, 1920)),
      str(vpm.widest_frame({(1920, 1080), (1080, 1920)})))
check("the larger of two landscape frames",
      vpm.widest_frame({(1920, 1080), (3840, 2160)}) == (3840, 2160))
check("nothing measured", vpm.widest_frame(set()) == (None, None))
check("one camera", vpm.widest_frame({(1280, 720)}) == (1280, 720))

print("\n%s" % ("ALL OK" if not bad else "FAIL: " + ", ".join(bad)))
sys.exit(1 if bad else 0)
