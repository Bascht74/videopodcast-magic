# -*- coding: utf-8 -*-
"""The cut rules: when the camera follows, and what it shows instead."""
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
error = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append("%s [%s]" % (name, extra or "no numbers"))


def word(start, end, text):
    return vpm.speech_word(start, end, text)


def sentence(start, step, count, text="wort", close="."):
    """Build one spoken sentence as a row of words."""
    out = []
    for i in range(count):
        piece = text + (close if i == count - 1 else "")
        out.append(word(start + i * step, start + i * step + step * 0.9,
                        piece))
    return out


print("1. Minimum speaking time -- a short yes does not move the camera")
tracks = [("Host", [(0.0, 20.0), (30.0, 50.0)]),
          ("Guest", [(20.5, 20.9), (50.0, 70.0)])]
camera_of = {"Host": "CamA", "Guest": "CamB"}
cut = vpm.build_camera_cut(tracks, 70.0, camera_of, "Wide", 3.0, -0.3,
                           vpm.cut_rules(min_speech=1.5))
check("the 0.4 s block gets no shot of its own",
      not any(who == "CamB" and b < 45.0 for _a, b, who in cut), str(cut))
off = vpm.build_camera_cut(tracks, 70.0, camera_of, "Wide", 0.0, -0.3,
                           vpm.cut_rules(min_speech=0.0))
check("switched off, the same block does reach the picture",
      any(who == "CamB" and b < 45.0 for _a, b, who in off), str(off))
longer = [("Host", [(0.0, 20.0), (30.0, 50.0)]),
          ("Guest", [(20.5, 24.0), (50.0, 70.0)])]
cut = vpm.build_camera_cut(longer, 70.0, camera_of, "Wide", 3.0, -0.3,
                           vpm.cut_rules(min_speech=1.5))
check("a 3.5 s block does move it",
      any(who == "CamB" and b < 45.0 for _a, b, who in cut), str(cut))

print("\n2. Short shots are glued to the following one")
band = [(0.0, 10.0, "A"), (10.0, 11.0, "B"), (11.0, 20.0, "C")]
check("the short piece goes to the one after it",
      vpm.merge_short_shots(band, 3.0)
      == [[0.0, 10.0, "A"], [10.0, 20.0, "C"]],
      str(vpm.merge_short_shots(band, 3.0)))
check("the last one has nothing after it and falls back",
      vpm.merge_short_shots([(0.0, 10.0, "A"), (10.0, 11.0, "B")], 3.0)
      == [[0.0, 11.0, "A"]])
check("two of the same camera never end up side by side",
      vpm.merge_short_shots(
          [(0.0, 10.0, "A"), (10.0, 11.0, "B"), (11.0, 20.0, "A")], 3.0)
      == [[0.0, 20.0, "A"]])
check("nothing under the minimum is left over",
      all(b - a >= 3.0 for a, b, _w in vpm.merge_short_shots(
          [(0.0, 4.0, "A"), (4.0, 5.0, "B"), (5.0, 6.0, "C"),
           (6.0, 12.0, "D")], 3.0)))

print("\n3. The wide shot where the recognition is not sure")
heap = [("Host", [(0.0, 100.0)]), ("Guest", [(100.0, 200.0)]),
        ("Scraps", [(200.0 + i, 200.4 + i) for i in range(20)])]
check("the leftover heap is found", vpm.stray_labels(heap) == {"Scraps"},
      str(vpm.stray_labels(heap)))
big_heap = [("Host", [(0.0, 2000.0)]),
            ("Guest", [(2000.0, 3000.0)]),
            ("Long", [(3000.0 + i * 2, 3000.9 + i * 2) for i in range(120)])]
check("total duration does not tell them apart -- segment length does",
      vpm.stray_labels(big_heap) == {"Long"},
      "%.0f s of scraps against %.0f s"
      % (sum(b - a for a, b in big_heap[2][1]), 1000.0))
even = [("Host", [(0.0, 100.0)]), ("Guest", [(100.0, 190.0)])]
check("two real speakers raise no alarm", vpm.stray_labels(even) == set(),
      str(vpm.stray_labels(even)))
frayed = [("Host", [(i * 1.2, i * 1.2 + 0.5) for i in range(8)]),
          ("Guest", [(i * 1.2 + 0.6, i * 1.2 + 1.0) for i in range(8)])]
two_cams = {"Host": "CamA", "Guest": "CamB"}
one_cam = {"Host": "CamA", "Guest": "CamA"}
check("seven entries in twelve seconds count as restless",
      vpm.unrest_spans(frayed, two_cams), str(vpm.unrest_spans(frayed,
                                                              two_cams)))
check("on one camera the same to and fro is one picture, not unrest",
      not vpm.unrest_spans(frayed, one_cam))
calm = [("Host", [(0.0, 40.0)]), ("Guest", [(40.0, 80.0)])]
check("a calm recognition raises no alarm",
      not vpm.unrest_spans(calm, two_cams))

print("\n4. Where a cut may sit: the text says roughly, the sound exactly")
check("a sentence beginning within two seconds wins",
      vpm.boundary_near(10.0, [11.5], [9.9]) == 11.5)
check("otherwise a clause break within two seconds",
      vpm.boundary_near(10.0, [14.0], [9.4]) == 9.4)
check("then the sentence beginning within five",
      vpm.boundary_near(10.0, [14.0], [14.5]) == 14.0)
check("and it searches backwards as well",
      vpm.boundary_near(10.0, [6.5], []) == 6.5)
check("beyond five seconds nothing is found",
      vpm.boundary_near(10.0, [17.0], [16.0]) is None)
levels = [900] * 500
for i in range(210, 240):
    levels[i] = 3                       # a real gap of 0.3 s
step = 0.010
found = vpm.sound_dip(levels, step, 2.0, 0.5)
check("the dip in the sound is found", found is not None
      and abs(found - 2.25) < 0.05, str(found))
check("without sound the boundary itself is taken",
      abs(vpm.cut_point(10.0, [9.4], [], (), step) - 9.4) < 1e-9)
check("with sound the point moves onto the gap",
      abs(vpm.cut_point(2.0, [2.0], [], levels, step) - 2.25) < 0.05,
      str(vpm.cut_point(2.0, [2.0], [], levels, step)))
flat = [500] * 500
check("nothing to measure means no dip",
      vpm.sound_dip(flat, step, 2.0, 0.5) is None)

print("\n5. How long the wide shot stands")
check("at least five seconds, then to the end of the sentence",
      vpm.wide_shot_length(0.0, 100.0, [3.0, 9.0, 20.0], [7.0], 5.0,
                           15.0) == 9.0)
check("over fifteen seconds the last clause break before it takes over",
      vpm.wide_shot_length(0.0, 100.0, [30.0], [7.0, 12.0, 14.0], 5.0,
                           15.0) == 14.0)
check("never cut off in the middle of a sentence",
      vpm.wide_shot_length(0.0, 100.0, [30.0], [7.0, 12.0], 5.0, 15.0)
      == 12.0)
check("without any punctuation it holds the minimum",
      vpm.wide_shot_length(0.0, 100.0, [], [], 5.0, 15.0) == 5.0)
check("and never longer than there is room for",
      vpm.wide_shot_length(0.0, 2.0, [], [], 5.0, 15.0) == 2.0)

print("\n6. A change of speaker on one camera is no cut")
same = [("Host", [(0.0, 20.0), (40.0, 60.0)]),
        ("Second", [(20.0, 40.0)])]
cut = vpm.build_camera_cut(same, 60.0, {"Host": "CamA",
                                        "Second": "CamA"}, "Wide", 3.0)
check("one camera for both means one shot", len(cut) == 1, str(cut))

print("\n7. The reaction cut after a question")
talk = [("Host", [(0.0, 4.2)]), ("Guest", [(5.0, 30.0)])]
asked = sentence(0.0, 0.5, 8, close="?")
told = sentence(0.0, 0.5, 8, close=".")
cams = {"Host": "CamA", "Guest": "CamB"}
check("a question fires it",
      vpm.reaction_cuts(talk, asked, cams) == {5.0: "Guest"},
      str(vpm.reaction_cuts(talk, asked, cams)))
check("a statement does not", vpm.reaction_cuts(talk, told, cams) == {})
check("nothing where both sit on the same camera",
      vpm.reaction_cuts(talk, asked, {"Host": "CamA",
                                      "Guest": "CamA"}) == {})
late = [("Host", [(0.0, 4.2)]), ("Guest", [(12.0, 30.0)])]
check("nothing where the answer comes too late",
      vpm.reaction_cuts(late, asked, cams) == {})
brief = [("Host", [(0.0, 4.2), (6.0, 30.0)]), ("Guest", [(5.0, 5.8)])]
check("nothing where the answer does not keep the floor",
      vpm.reaction_cuts(brief, asked, cams) == {})
main_asks = [("Host", [(0.0, 4.2), (20.0, 200.0)]),
             ("Guest", [(5.0, 20.0)])]
check("nothing where the main speaker is the one asking",
      vpm.reaction_cuts(main_asks, asked, cams) == {})
rules = vpm.cut_rules(words=asked, on_question=vpm.SHOT_ANSWER,
                      reaction_lead=1.5)
early = vpm.build_camera_cut(talk, 30.0, cams, "Wide", 0.0, -0.3, rules)
plain = vpm.build_camera_cut(talk, 30.0, cams, "Wide", 0.0, -0.3,
                             vpm.cut_rules(words=asked,
                                           on_question=vpm.SHOT_OFF))
when_early = [a for a, _b, who in early if who == "CamB"]
when_plain = [a for a, _b, who in plain if who == "CamB"]
# The question's last word ends at 4.0, the answer starts at 5.0, and
# the lead is 1.5. Zero is the end of the question, so the aim is 2.5;
# the sound may move it half a second either way.
check("the answer is on screen earlier",
      when_early and when_plain and when_early[0] < when_plain[0] - 1.0,
      "%s against %s" % (when_early, when_plain))
check("the lead counts from the end of the question, not the start "
      "of the answer",
      when_early and abs(when_early[0] - (4.0 - 1.5)) <= 0.5,
      "%s, wanted 2.5 -- from the answer at 5.0 it would be 3.5"
      % when_early)
check("and the Edit Change Delay is not added a second time",
      when_early and when_early[0] > (4.0 - 1.5) - 0.5 - 0.02,
      "%s, the delay of 0.3 would push it below %.2f"
      % (when_early, (4.0 - 1.5) - 0.5))
check("no new cuts -- if anything one disappears",
      len(early) <= len(plain), "%d against %d" % (len(early), len(plain)))

print("\n8. Every value of every one of the four fields")
# One long monologue, one place where both speak, one heap of scraps
# and one question -- so all four fields have something to decide.
mixed = [("Host", [(0.0, 10.0), (210.0, 230.0), (260.0, 264.0),
                   (305.0, 315.0)]),
         ("Guest", [(40.0, 200.0), (215.0, 225.0), (265.0, 300.0)]),
         ("Scraps", [(230.0 + i * 0.5, 230.45 + i * 0.5)
                     for i in range(40)])]
mixed_cams = {"Host": "CamA", "Guest": "CamB", "Scraps": "CamA"}
mixed_words = sentence(260.0, 0.5, 8, close="?")
seen = {}
for switch, _caption, default_value, values, _s, _l in vpm.CUT_CHOICES:
    field = switch.replace("-", "_")
    shapes = []
    for value in values:
        made = vpm.camera_cut(
            mixed, 320.0, mixed_cams, "Wide", 3.0, 0.3, 40.0, 5.0,
            120.0, False,
            vpm.cut_rules(words=mixed_words, **{field: value}))
        ok = bool(made) and all(b > a for a, b, _w in made)
        ok = ok and abs(made[0][0]) < 1e-6 and abs(made[-1][1] - 320.0) < 1.0
        ok = ok and all(abs(x[1] - y[0]) < 1e-6
                        for x, y in zip(made, made[1:]))
        check("%s = %s gives a whole cut" % (switch, value), ok,
              "%d shots" % len(made))
        shapes.append(tuple((round(a, 2), w) for a, _b, w in made))
    seen[switch] = shapes
    check("%s: the value makes a difference" % switch,
          len(set(shapes)) > 1, "%d different results" % len(set(shapes)))
check("every value of every field checked, not every combination",
      sum(len(v) for v in seen.values())
      == sum(len(f[3]) for f in vpm.CUT_CHOICES))

print("\n9. Long monologue: what is shown when it is broken up")
# One person holds the floor for five minutes; the other says "mhm"
# every twenty seconds, so the listener is audibly there.
mono = [("Host", [(0.0, 300.0)]),
        ("Guest", [(float(i), i + 1.0) for i in range(20, 300, 20)])]
mono_cams = {"Host": "CamA", "Guest": "CamB"}
one_shot = [(0.0, 300.0, "CamA")]


def broken(way, tracks_used=None):
    return vpm.insert_wide_shots(
        one_shot, tracks_used or mono, "Wide", 40.0, 5.0, 3.0, 120.0,
        mono_cams, vpm.cut_rules(on_monologue=way))


kept = broken(vpm.SHOT_HOLD)
check("no camera change leaves the shot alone", len(kept) == 1, str(kept))
wide = broken(vpm.SHOT_WIDE)
check("the wide shot breaks it up",
      len(wide) > 1 and {w for _a, _b, w in wide} == {"CamA", "Wide"},
      str({w for _a, _b, w in wide}))
check("and every break stands at least five seconds",
      all(b - a >= 5.0 - 1e-6 for a, b, w in wide if w == "Wide"),
      str([round(b - a, 2) for a, b, w in wide if w == "Wide"]))
heard = broken(vpm.SHOT_LISTENER)
check("the listener gets the picture",
      "CamB" in {w for _a, _b, w in heard}, str([w for _a, _b, w in heard]))
turns = broken(vpm.SHOT_ALTERNATE)
row = [w for _a, _b, w in turns if w != "CamA"]
check("alternating remembers and takes turns",
      len(row) > 1 and len(set(row)) > 1, str(row))
silent = [("Host", [(0.0, 300.0)]), ("Guest", [(280.0, 281.0)])]
away = broken(vpm.SHOT_LISTENER, silent)
check("a listener nobody has heard for 20 s does not get it",
      "CamB" not in {w for _a, _b, w in away},
      str({w for _a, _b, w in away}))

print("\n10. The whole cut comes out of one place")
d = {"speakers": [{"name": n, "sections": [list(x) for x in segs]}
                  for n, segs in mixed],
     "cameras": [{"track": "CamA", "speakers": ["Host", "Scraps"]},
                 {"track": "CamB", "speakers": ["Guest"]},
                 {"track": "Wide", "speakers": []}],
     "length_s": 320.0,
     "words": vpm.words_for_handover(mixed_words)}
numbers = vpm.cut_statistics(d, 3.0, 0.3, 40.0, 5.0, 120.0, False)
check("the preview computes", bool(numbers and numbers.get("cut")))
same = vpm.camera_cut(mixed, 320.0, mixed_cams, "Wide", 3.0, 0.3,
                      40.0, 5.0, 120.0, False,
                      vpm.cut_rules(words=mixed_words))
check("and it is the same cut the run builds",
      numbers["cut"] == same, "%d against %d" % (len(numbers["cut"]),
                                                 len(same)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
