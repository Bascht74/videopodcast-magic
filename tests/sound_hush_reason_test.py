# -*- coding: utf-8 -*-
"""A channel that carries nothing says which rule caught it.

Two rules can call a channel empty: far under the loudest of its
neighbours, or under -70 dBFS on its own. Without the reason and the
number, the log gives nobody anything to turn a knob by.
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
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


silent, why = vpm.channel_hush([-3.0, -60.0, -6.0])
check("45 dB under the loudest counts as unplugged",
      silent == [False, True, False], str(silent))
check("and the reason is the relative one",
      why[1][0] == "under" and abs(why[1][1] - 57.0) < 0.01, str(why[1]))
line = vpm.hush_reason(2, why)
check("the line names the gap, not a noise floor",
      "57" in line and "noise" not in line, line)
silent, why = vpm.channel_hush([-75.0, -71.0])
check("all quiet is judged on the relative rule alone",
      silent == [False, False], str(silent))
# The absolute rule only gets a turn where the relative one does not
# fire: 31 dB down is not an unplugged input, but -71 dBFS is nothing
# but the converter talking to itself.
silent, why = vpm.channel_hush([-40.0, -71.0])
check("a channel under -70 dBFS is converter noise",
      silent == [False, True] and why[1][0] == "quiet", str(why[1]))
check("and that line says the level",
      "-71" in vpm.hush_reason(2, why), vpm.hush_reason(2, why))
source = open(SCRIPT, encoding="utf-8").read()
check("one rule, not the same rule typed twice",
      source.count("def channel_hush(") == 1
      and source.count("silent, why = channel_hush(level)") == 2,
      "%d definitions, %d callers"
      % (source.count("def channel_hush("),
         source.count("silent, why = channel_hush(level)")))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
