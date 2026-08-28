# -*- coding: utf-8 -*-
"""The window is the stretch EVERY camera saw, not the one any saw.

Sebastian, 26.8.2026, on a run over the test interview: *"I did not
change Cut-In and Out, I left them. The length of the output is
shorter. That is not good."* The window had been the union of the
cameras -- from the first one that came on to the last one that
stopped. His In point then lay 12.567 s before one of three cameras
began, and there a cut to that camera has no picture: the output is
shorter than the window promised.

Decided on 29.8.2026: the derived window is the intersection. Whoever
wants the wider stretch sets an In point of their own.

There was no test over this at all -- the whole suite stayed green
while the meaning of the window turned round, because nothing asked.
That is what this file is for.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

bad = []


def check(what, ok, detail=""):
    print("  %-58s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


print("1. Three cameras that do not begin together")
# The shape of the fault as it was measured: one camera comes on late
# and another stops early. Numbers chosen so that union and
# intersection cannot be confused for one another.
THREE = [(-2.0, 118.0, "Totale.mov"),
         (3.5, 121.0, "Moderatoren.mov"),
         (0.0, 110.0, "Kandidat.mov")]
t0, late, t1, early = vpm.common_window(THREE)
check("it begins where the last camera came on", abs(t0 - 3.5) < 1e-9,
      "%.3f, wanted 3.5" % t0)
check("it ends where the first camera stopped", abs(t1 - 110.0) < 1e-9,
      "%.3f, wanted 110.0" % t1)
check("and it names the camera that decides the start",
      late == "Moderatoren.mov", late)
check("and the one that decides the end", early == "Kandidat.mov", early)
# The counter-proof: what the union would have said. Kept as a number
# rather than as a memory, so that a change back would be loud.
check("the union would have been wider by 5.5 s at the front",
      abs((t0 - min(x for x, _y, _n in THREE)) - 5.5) < 1e-9,
      "%.3f" % (t0 - min(x for x, _y, _n in THREE)))
check("and by 11.0 s at the back",
      abs((max(y for _x, y, _n in THREE) - t1) - 11.0) < 1e-9,
      "%.3f" % (max(y for _x, y, _n in THREE) - t1))
# And what it must never do: begin before its own zero. The fixture run
# on 29.8.2026 gave -0:00:00,180 under the union -- a window that starts
# before the camera it is measured against.
check("it never begins before the latest camera",
      t0 >= max(x for x, _y, _n in THREE) - 1e-9, "%.3f" % t0)

print("\n2. One camera is its own window")
ONE = [(4.0, 99.0, "Totale.mov")]
t0, late, t1, early = vpm.common_window(ONE)
check("start, end and both names are that camera's",
      (t0, late, t1, early) == (4.0, "Totale.mov", 99.0, "Totale.mov"),
      str((t0, late, t1, early)))

print("\n3. Cameras that really do begin together")
# Where nothing is offset, union and intersection are the same window,
# and the change decided on 29.8.2026 costs nothing at all.
SAME = [(0.0, 60.0, "A.mov"), (0.0, 60.0, "B.mov")]
t0, _l, t1, _e = vpm.common_window(SAME)
check("the window is the whole of it", (t0, t1) == (0.0, 60.0),
      str((t0, t1)))
check("and it is what the union would have given too",
      (t0, t1) == (min(x for x, _y, _n in SAME),
                   max(y for _x, y, _n in SAME)), str((t0, t1)))

print("\n4. Two cameras that never overlap")
# Nothing to cut between: the run has its own complaint for a window
# under 30 s, and this is what hands it a negative one. Held here so
# that the complaint keeps its cause.
APART = [(0.0, 10.0, "early.mov"), (50.0, 60.0, "late.mov")]
t0, _l, t1, _e = vpm.common_window(APART)
check("the window comes out negative rather than pretending",
      t1 - t0 < 0, "%.3f to %.3f" % (t0, t1))

print("\n%s" % ("ALL OK" if not bad else "FAIL: " + ", ".join(bad)))
sys.exit(1 if bad else 0)
