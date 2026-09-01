# -*- coding: utf-8 -*-
"""The offset fit says how close it came and what it left unexplained.

A fit that says only "failed" makes everybody talking at once look
like bleed too weak to read, and the two need different remedies. A
fit that worked still owes the number saying how well it worked.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
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


print("A failed measurement says how close it came")
# Without the number the two faults -- everybody talking at once, and
# bleed too weak to read -- look the same in the log, and they need
# different remedies.
check("three is the floor for a fit, and it is named",
      vpm.ENOUGH_WINDOWS == 3, str(vpm.ENOUGH_WINDOWS))
check("so is the sharpness a second has to reach",
      vpm.SHARP_ENOUGH == 10.0, str(vpm.SHARP_ENOUGH))
text = vpm.T('only %d seconds where %s speaks alone, %d needed') % (
    1, "Anna", vpm.ENOUGH_WINDOWS)
check("the thin-material line carries both numbers",
      "1" in text and "3" in text, text)
text = vpm.T('bleed too indistinct: %d of %d seconds usable, sharpest '
             '%.1f of %.0f needed') % (1, 9, 4.2, vpm.SHARP_ENOUGH)
check("and so does the indistinct-bleed line",
      "4.2" in text and "10" in text, text)

print("The fit hands back what it could not explain")
points = [(float(t), 10.0 + 0.0 * t) for t in range(8)]
m = {(0, 1): points, (1, 0): [(t, -v) for t, v in points]}
found = vpm.solve_pair_offsets(m, 0, 1)
check("five values come back now, not four",
      found is not None and len(found) == 5, str(found and len(found)))
check("a line that fits exactly leaves nothing over",
      found is not None and found[4] < 1e-6, "%.2e" % found[4])
noisy = list(points)
noisy[3] = (3.0, 40.0)
m = {(0, 1): noisy, (1, 0): [(t, -v) for t, v in points]}
found2 = vpm.solve_pair_offsets(m, 0, 1)
check("and a point out of line shows up in it",
      found2 is not None and found2[4] > 1.0, "%.2f ms" % found2[4])

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
