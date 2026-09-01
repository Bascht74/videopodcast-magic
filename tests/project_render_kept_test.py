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
got = vpm.free_render_name(folder, "Episode")
check("free name stays as it is", got == "Episode",
      "got %r, wanted %r, folder holds %s"
      % (got, "Episode", sorted(os.listdir(folder))))
open(os.path.join(folder, "Episode.mp4"), "w").write("x")
got = vpm.free_render_name(folder, "Episode")
check("taken name counts up", got == "Episode_2",
      "got %r, wanted %r, folder holds %s"
      % (got, "Episode_2", sorted(os.listdir(folder))))
open(os.path.join(folder, "Episode_2.mp4"), "w").write("x")
got = vpm.free_render_name(folder, "Episode")
check("and counts on", got == "Episode_3",
      "got %r, wanted %r, folder holds %s"
      % (got, "Episode_3", sorted(os.listdir(folder))))
got = vpm.free_render_name(folder, "Episode", ".mov")
check("another extension is its own question", got == "Episode",
      "got %r, wanted %r for .mov, folder holds %s"
      % (got, "Episode", sorted(os.listdir(folder))))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
