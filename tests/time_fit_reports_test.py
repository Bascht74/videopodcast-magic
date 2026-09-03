# -*- coding: utf-8 -*-
"""The offset fit says how close it came and what it left unexplained.

A fit that says only "failed" makes everybody talking at once look
like bleed too weak to read, and the two need different remedies. A
fit that worked still owes the number saying how well it worked. And
a warning about a weak one owes the name of the file it is about:
with several recordings in a run, warnings without names are a heap
nobody can put back.
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


print("\nA weak match names the file it is about")
# Two curves that have nothing to do with each other: the warning is
# the only line saying so, and with several recordings in one run a
# warning without a name cannot be put back against a file.
import contextlib, io as _io
import numpy as _np
_r = _np.random.RandomState(11)
one, two = _r.randn(4000), _r.randn(4000)


def said_while_aligning(warn):
    caught = _io.StringIO()
    floor_was = vpm.WEAK_MATCH
    vpm.WEAK_MATCH = 1.0
    try:
        with contextlib.redirect_stdout(caught):
            try:
                vpm.align_envelopes(one, two, warn=warn)
            except Exception:
                pass
    finally:
        vpm.WEAK_MATCH = floor_was
    return caught.getvalue()


named = said_while_aligning("Guest_0001.wav")
check("the weak match names the file it is about",
      "Guest_0001.wav" in named,
      repr(named.strip()[:70]))
check("and it is still the warning, not some other line",
      "Guest_0001.wav" in named and vpm.T('this pair of files') not in named,
      repr(named.strip()[:70]))
plain = said_while_aligning(True)
check("with no name to hand it says so rather than naming nothing",
      vpm.T('this pair of files') in plain, repr(plain.strip()[:70]))
quiet = said_while_aligning(False)
check("and where the caller asked for silence there is none of it",
      "0.0" not in quiet and "WARN" not in quiet.upper(),
      repr(quiet.strip()[:70]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
