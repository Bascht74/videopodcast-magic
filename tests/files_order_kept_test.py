# -*- coding: utf-8 -*-
"""Files put together by hand keep the order they were named in.

Sorting by name is right for what the search found on its own. A row
named by hand carries an order somebody chose, and sorting that row
throws the choice away.
"""
import os
import sys
import tempfile
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
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append("%s [%s]" % (name, extra or "no numbers"))


folder = tempfile.mkdtemp(prefix="vpm_together_")
paths = [os.path.join(folder, x)
         for x in ("Zulu.wav", "Alpha.wav", "Mike.wav")]
for p in paths:
    open(p, "wb").close()
out, _ = vpm.collect_with_continuations(
    paths, True, together=[paths])
check("the hand-forced row is not sorted by name",
      [os.path.basename(x) for x in out]
      == ["Zulu.wav", "Alpha.wav", "Mike.wav"],
      str([os.path.basename(x) for x in out]))
loose = os.path.join(folder, "Bravo.wav")
open(loose, "wb").close()
out, _ = vpm.collect_with_continuations(
    paths + [loose], True, together=[paths])
check("and it lands where its first-named member would",
      [os.path.basename(x) for x in out]
      == ["Zulu.wav", "Alpha.wav", "Mike.wav", "Bravo.wav"],
      str([os.path.basename(x) for x in out]))
out, _ = vpm.collect_with_continuations(paths + [loose], True)
check("without --together everything sorts by name",
      [os.path.basename(x) for x in out]
      == ["Alpha.wav", "Bravo.wav", "Mike.wav", "Zulu.wav"],
      str([os.path.basename(x) for x in out]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
