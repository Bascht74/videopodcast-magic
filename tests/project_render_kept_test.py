# -*- coding: utf-8 -*-
"""A render never writes over the delivery before it.

The target came from the production name alone, so a second run
replaced the file of the first without asking.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys, tempfile
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
WORK = tempfile.mkdtemp(prefix="rendername_")
bad = []


def check(what, ok, detail=""):
    print("  %-58s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


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

print("\n%s" % ("ALL OK" if not bad else "FAIL: " + ", ".join(bad)))
sys.exit(1 if bad else 0)
