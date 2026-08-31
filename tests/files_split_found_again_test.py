# -*- coding: utf-8 -*-
"""Split blocks are found again by the names they carry today.

The pieces a split writes are looked for by name, so a name the
search no longer knows leaves the recording whole.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys, time
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
began = time.time()
done = 0
bad = []


def check(what, ok, detail=""):
    global done
    done += 1
    print("  %-58s %s %s" % (what, "ok" if ok else "FAIL", detail))
    if not ok:
        bad.append("%s [%s]" % (what, detail or "no numbers"))


# Matching the piece names against an older spelling found nothing, and
# a recording of several blocks then never came apart into tracks.
one = vpm.split_target("/card1/REC0001.WAV", (0,), "/out")
two = vpm.split_target("/card1/REC0002.WAV", (0,), "/out")
pair1 = vpm.split_target("/card1/REC0001.WAV", (1, 2), "/out")
pair2 = vpm.split_target("/card1/REC0002.WAV", (1, 2), "/out")
pieces = {"/card1/REC0001.WAV": [one, pair1],
          "/card1/REC0002.WAV": [two, pair2]}
rows = vpm.expand_chains_to_tracks(
    [(["/card1/REC0001.WAV", "/card1/REC0002.WAV"], [])],
    lambda x: pieces.get(x) or [])
check("two blocks, two channels -> two recordings", len(rows) == 2,
      str(len(rows)))
check("each holding both blocks",
      all(len(r) == 2 for r, _d in rows), str([len(r) for r, _d in rows]))
check("channel 1 with channel 1",
      [os.path.basename(x) for x in rows[0][0]]
      == [os.path.basename(one), os.path.basename(two)],
      str([os.path.basename(x) for x in rows[0][0]]))
mixed = {"/card1/REC0001.WAV": [one, pair1],
         "/card1/REC0002.WAV": [two]}
check("blocks that came apart differently stay whole",
      len(vpm.expand_chains_to_tracks(
          [(["/card1/REC0001.WAV", "/card1/REC0002.WAV"], [])],
          lambda x: mixed.get(x) or [])) == 1)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
