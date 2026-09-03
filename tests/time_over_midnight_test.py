# -*- coding: utf-8 -*-
"""Midnight is one night, not a day apart.

A recorder started at 00:10 and cameras running since 23:50 are
minutes apart, but their timecodes are almost a whole day. Read
plainly, the run reported an unset clock where the clock was right.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
import importlib.util
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

began = time.time()
done = 0
error = []
def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


DAY = 24 * 3600
moved = vpm.unwrap_day(600, 85800)
check("a value moves onto the axis of its neighbour", moved == 600 + DAY,
      "%s s, wanted %d" % (moved, 600 + DAY))
back = vpm.unwrap_day(85800, 600)
check("and back the other way", back == 85800 - DAY,
      "%s s, wanted %d" % (back, 85800 - DAY))
same_day = vpm.unwrap_day(3600, 3000)
check("nothing moves inside the same day", same_day == 3600,
      "%s s, wanted 3600" % (same_day,))
unset = vpm.unwrap_day(None, 5)
check("no timecode, nothing to do", unset is None,
      "%s, wanted nothing" % (unset,))

cameras = [{"tc": 23 * 3600 + 50 * 60, "duration": 1800,
            "name": "CamA", "path": "a"},
           {"tc": 23 * 3600 + 50 * 60, "duration": 1800,
            "name": "CamB", "path": "b"},
           {"tc": 23 * 3600 + 52 * 60, "duration": 1700,
            "name": "CamC", "path": "c"}]

def about(tc, duration=900):
    return vpm.timecode_comparison(
        cameras + [{"tc": tc, "duration": duration,
                    "name": "Rec", "path": "d"}])

found = about(10 * 60)
check("a recording after midnight is not an unset clock",
      len(found) == 1 and found[0].field == vpm.T('Midnight'),
      "; ".join(b.text[:40] for b in found))
evening = about(23 * 3600 + 55 * 60)
check("the same evening says nothing at all", evening == [],
      "%d findings, wanted none: %s"
      % (len(evening), "; ".join(b.text[:40] for b in evening)))
found = about(3 * 3600)
# The unwrap is only kept where it puts the file among the others.
# Here it does not, so the move is taken back and the old finding
# stands.
check("a clock set to the wrong hour is still an unset clock",
      len(found) == 1 and "Timecode" in found[0].text,
      "; ".join(b.text[:40] for b in found))
found = about(0)
check("and 00:00:00 stays the unset clock it has always been",
      len(found) == 1 and "Timecode" in found[0].text,
      "; ".join(b.text[:40] for b in found))
on_the_hour = vpm.unwrap_day(5.0, 86395.0 + 5.0) - (86395.0 + 5.0)
ten_before = vpm.unwrap_day(5.0, 86390.0) - 86390.0
check("a camera that restarts over midnight has no gap",
      on_the_hour == 0.0 or abs(ten_before - 15.0) < 0.001,
      "5 s after 86400.0 lands %.3f s on, after 86390.0 %.3f s on, "
      "wanted 0.000 or 15.000" % (on_the_hour, ten_before))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
