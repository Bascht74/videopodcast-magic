# -*- coding: utf-8 -*-
"""A render never writes over the delivery before it.

The target came from the production name alone, so a second run
replaced the file of the first without asking.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys, tempfile, time
began = time.time()
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
WORK = tempfile.mkdtemp(prefix="rendername_")
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


folder = os.path.join(WORK, "out")
os.makedirs(folder)
check("free name stays as it is",
      vpm.free_render_name(folder, "Episode") == "Episode")
open(os.path.join(folder, "Episode.mp4"), "w").write("x")
check("taken name counts up",
      vpm.free_render_name(folder, "Episode") == "Episode_2")
open(os.path.join(folder, "Episode_2.mp4"), "w").write("x")
check("and counts on",
      vpm.free_render_name(folder, "Episode") == "Episode_3")
check("another extension is its own question",
      vpm.free_render_name(folder, "Episode", ".mov") == "Episode")

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
