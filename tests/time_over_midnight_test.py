# -*- coding: utf-8 -*-
"""Midnight is one night, not a day apart.

A recorder started at 00:10 and cameras running since 23:50 are
minutes apart, but their timecodes are almost a whole day. Read
plainly, the run reported an unset clock where the clock was right.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
import importlib.util
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


DAY = 24 * 3600
check("a value moves onto the axis of its neighbour",
      vpm.unwrap_day(600, 85800) == 600 + DAY)
check("and back the other way",
      vpm.unwrap_day(85800, 600) == 85800 - DAY)
check("nothing moves inside the same day",
      vpm.unwrap_day(3600, 3000) == 3600)
check("no timecode, nothing to do", vpm.unwrap_day(None, 5) is None)

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
check("the same evening says nothing at all",
      about(23 * 3600 + 55 * 60) == [])
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
check("a camera that restarts over midnight has no gap",
      vpm.unwrap_day(5.0, 86395.0 + 5.0) - (86395.0 + 5.0) == 0.0
      or abs(vpm.unwrap_day(5.0, 86390.0) - 86390.0 - 15.0) < 0.001)

print()
if error:
    print("FAIL: %d of the checks" % len(error))
    sys.exit(1)
print("All good.")
