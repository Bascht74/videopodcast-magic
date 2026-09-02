# -*- coding: utf-8 -*-
"""One camera for everybody: the cut still marks the speaker changes.

One camera the old way, then split at the change of speaker; two
cameras, where the shots are the speakers already; a short
interjection; silence. What the detailed cut says about who is talking
is held against written-out names, not against a second reading of the
same tracks. How many fields a row has gets no judgement of its own:
every caller above unpacks them by name, so a row of the wrong width
ends the run before a check could speak.
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
# Everything down to the pair below runs on the defaults, and the ten
# turns hang on them: a moved minimum, a moved lead-in, a changed cut
# rule or a wider unrest window turns this section red without the
# program being wrong. The unrest window is not one of the cut rules,
# so naming rules here would not reach it either.
two_cut = vpm.build_camera_cut(tracks, 80.0, two, "Wide")
after = vpm.split_shots_by_speaker(two_cut, tracks)
check("splitting again changes nothing",
      [(round(a, 4), round(b, 4), c) for a, b, c in two_cut]
      == [(round(a, 4), round(b, 4), c) for a, b, c, _w in after],
      "%d against %d" % (len(two_cut), len(after)))
detail = vpm.camera_cut_detail(tracks, 80.0, two, "Wide")
# Counting the fields said nothing about what stands in the fourth, and
# a cut that named nobody kept every check green. So the names are
# written out: ten turns of eight seconds, the Host first. Read off the
# tracks again they would only repeat the program's own reading.
TURNS = [("Host",), ("Guest",), ("Host",), ("Guest",), ("Host",),
         ("Guest",), ("Host",), ("Guest",), ("Host",), ("Guest",)]
said = [r[3] for r in detail]
# Both lists whole: a merge goes wrong behind the fourth shot as often
# as in front of it, and a cut-off line then puts FAIL beside two
# readings that look the same.
check("while the detailed one says who is talking", said == TURNS,
      "%d shots against %d wanted, %s against %s"
      % (len(said), len(TURNS), said, TURNS))
# Where two talk at once both belong in the shot, and always in the
# same order: split_shots_by_speaker hands out the same four fields and
# sorts the names, and two rows that ordered the same pair differently
# would not compare equal. Host stands before Guest in the tracks and
# after it in the alphabet, so the two orders really differ here. The
# rules are named rather than left to their defaults, so a changed
# default does not turn this one judgement red for the wrong reason --
# it does nothing for the reading above, which passes nothing. Named
# too, and not counted off: a parameter inserted into the signature
# leaves the program right and kills a row of seven positions.
both = [("Host", [(0, 20)]), ("Guest", [(8, 12)])]
pair = vpm.camera_cut_detail(both, 20.0, two, "Wide", min_len=0.5,
                             lead_in=0.0,
                             rules=vpm.cut_rules(min_speech=0.5,
                                                 on_together=vpm.SHOT_WIDE))
WANTED_PAIR = [("Host",), ("Guest", "Host"), ("Host",)]
check("and both are named, in one order, where they talk at once",
      [r[3] for r in pair] == WANTED_PAIR,
      "%d shots against %d wanted, %s against %s"
      % (len(pair), len(WANTED_PAIR), [r[3] for r in pair], WANTED_PAIR))

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
