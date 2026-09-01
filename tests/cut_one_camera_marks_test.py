# -*- coding: utf-8 -*-
"""One camera for everybody: the cut still marks the speaker changes."""
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


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))

# Two people taking turns, eight seconds each, over eighty seconds.
tracks = [("Host", [(0, 8), (16, 24), (32, 40), (48, 56), (64, 72)]),
          ("Guest", [(8, 16), (24, 32), (40, 48), (56, 64), (72, 80)])]
one = {"Host": "Wide", "Guest": "Wide"}
two = {"Host": "CamA", "Guest": "CamB"}

print("1. One camera, the old way")
cut = vpm.build_camera_cut(tracks, 80.0, one, "Wide")
check("everything melts into one shot", len(cut) == 1, str(cut))
check("and it is that camera", cut[0][2] == "Wide", str(cut[0]))

print("\n2. One camera, cut at the change of speaker")
just_one = vpm.one_camera_only(one)
also_two = vpm.one_camera_only(two)
check("the interface can tell there is only one camera",
      just_one and not also_two,
      "%s for one camera and %s for two, wanted True and False"
      % (just_one, also_two))
rich = vpm.split_shots_by_speaker(cut, tracks)
check("several shots now", len(rich) >= 8, len(rich))
check("all of them from the one camera",
      {r[2] for r in rich} == {"Wide"}, str({r[2] for r in rich}))
who = [r[3] for r in rich]
check("and they say who is talking",
      all(len(w) <= 1 for w in who) and ("Host",) in who
      and ("Guest",) in who, str(who[:6]))
check("no two neighbours have the same speaker",
      all(a != b for a, b in zip(who, who[1:])), str(who[:8]))
check("it runs from nothing to the end and has no gap",
      abs(rich[0][0]) < 1e-6 and abs(rich[-1][1] - 80.0) < 1e-6
      and all(abs(a[1] - b[0]) < 1e-6 for a, b in zip(rich, rich[1:])),
      "%.2f .. %.2f" % (rich[0][0], rich[-1][1]))

print("\n3. Two cameras: the shots are already the speakers")
two_cut = vpm.build_camera_cut(tracks, 80.0, two, "Wide")
after = vpm.split_shots_by_speaker(two_cut, tracks)
check("splitting again changes nothing",
      [(round(a, 4), round(b, 4), c) for a, b, c in two_cut]
      == [(round(a, 4), round(b, 4), c) for a, b, c, _w in after],
      "%d against %d" % (len(two_cut), len(after)))
check("and the old function still answers in threes",
      all(len(r) == 3 for r in two_cut),
      "%d of %d shots hold three fields, seen %s"
      % (len([r for r in two_cut if len(r) == 3]), len(two_cut),
         sorted(set(len(r) for r in two_cut))))
detail = vpm.camera_cut_detail(tracks, 80.0, two, "Wide")
check("while the detailed one says who is talking",
      all(len(r) == 4 for r in detail),
      "%d of %d shots hold four fields, seen %s"
      % (len([r for r in detail if len(r) == 4]), len(detail),
         sorted(set(len(r) for r in detail))))

print("\n4. Short interjections still disappear")
quick = [("Host", [(0, 30)]), ("Guest", [(10, 10.4)])]
rich = vpm.split_shots_by_speaker(
    vpm.build_camera_cut(quick, 30.0, one, "Wide"), quick, 1.2)
check("a four tenths interjection makes no shot of its own",
      all(b - a >= 1.2 - 1e-6 for a, b, _c, _w in rich), str(rich))

print("\n5. Silence belongs to nobody")
gap = [("Host", [(0, 5)]), ("Guest", [(20, 25)])]
rich = vpm.split_shots_by_speaker(
    vpm.build_camera_cut(gap, 25.0, one, "Wide"), gap)
check("there is a shot with no speaker",
      any(w == () for _a, _b, _c, w in rich), str([r[3] for r in rich]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
