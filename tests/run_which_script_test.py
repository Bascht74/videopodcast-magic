# -*- coding: utf-8 -*-
"""The log names the copy of the script that is running.

With two copies on one machine and a log that gives only a file name,
there is no telling which one a run used. The path is written out in
full, and it is the file that was loaded.
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


where = vpm.running_from()
check("an absolute path", os.path.isabs(where), where[:40])
check("and it is the file that was loaded",
      os.path.samefile(where, SCRIPT))

print()
if error:
    print("FAIL: %d of the checks" % len(error))
    sys.exit(1)
print("All good.")
