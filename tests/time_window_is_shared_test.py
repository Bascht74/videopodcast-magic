# -*- coding: utf-8 -*-
"""The window is the stretch EVERY camera saw, not the one any saw.

As the union -- first camera on to last camera off -- an In point could
fall before one camera began, where a cut to it has no picture and the
output comes out shorter than the window promised. The intersection is
the answer, and nothing asked this before: the suite stayed green while
the meaning of the window turned round.
"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

began = time.time()
done = 0
bad = []


def check(what, ok, detail=""):
    global done
    done += 1
    print("  %-58s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


print("1. Three cameras that do not begin together")
# One camera comes on late and another stops early, with numbers chosen
# so union and intersection cannot be confused for one another.
THREE = [(-2.0, 118.0, "WideCam.mov"),
         (3.5, 121.0, "PresentersCam.mov"),
         (0.0, 110.0, "Guest.mov")]
t0, late, t1, early = vpm.common_window(THREE)
check("it begins where the last camera came on", abs(t0 - 3.5) < 1e-9,
      "%.3f, wanted 3.5" % t0)
check("it ends where the first camera stopped", abs(t1 - 110.0) < 1e-9,
      "%.3f, wanted 110.0" % t1)
check("and it names the camera that decides the start",
      late == "PresentersCam.mov", late)
check("and the one that decides the end", early == "Guest.mov", early)
# The counter-proof: what the union would have said, so a change back
# is loud.
check("the union would have been wider by 5.5 s at the front",
      abs((t0 - min(x for x, _y, _n in THREE)) - 5.5) < 1e-9,
      "%.3f" % (t0 - min(x for x, _y, _n in THREE)))
check("and by 11.0 s at the back",
      abs((max(y for _x, y, _n in THREE) - t1) - 11.0) < 1e-9,
      "%.3f" % (max(y for _x, y, _n in THREE) - t1))
# What it must never do: begin before the camera it is measured against.
check("it never begins before the latest camera",
      t0 >= max(x for x, _y, _n in THREE) - 1e-9, "%.3f" % t0)

print("\n2. One camera is its own window")
ONE = [(4.0, 99.0, "WideCam.mov")]
t0, late, t1, early = vpm.common_window(ONE)
check("start, end and both names are that camera's",
      (t0, late, t1, early) == (4.0, "WideCam.mov", 99.0, "WideCam.mov"),
      str((t0, late, t1, early)))

print("\n3. Cameras that really do begin together")
# Where nothing is offset, union and intersection are the same window.
SAME = [(0.0, 60.0, "A.mov"), (0.0, 60.0, "B.mov")]
t0, _l, t1, _e = vpm.common_window(SAME)
check("the window is the whole of it", (t0, t1) == (0.0, 60.0),
      str((t0, t1)))
check("and it is what the union would have given too",
      (t0, t1) == (min(x for x, _y, _n in SAME),
                   max(y for _x, y, _n in SAME)), str((t0, t1)))

print("\n4. Two cameras that never overlap")
# Nothing to cut between: the run complains about a window under 30 s,
# and this is what hands it a negative one.
APART = [(0.0, 10.0, "early.mov"), (50.0, 60.0, "late.mov")]
t0, _l, t1, _e = vpm.common_window(APART)
check("the window comes out negative rather than pretending",
      t1 - t0 < 0, "%.3f to %.3f" % (t0, t1))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
