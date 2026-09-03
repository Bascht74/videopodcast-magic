# -*- coding: utf-8 -*-
"""The cut rules: when the camera follows, and what it shows instead.

And the values they take when nobody sets one. The fields of the cut
box declare the same numbers a second time, so the last section holds
the two against each other; the few numbers no field shows stand
written out there instead.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
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
cut = vpm.build_camera_cut(tracks, 70.0, camera_of, "Wide", min_len=3.0,
                           lead_in=-0.3,
                           rules=vpm.cut_rules(min_speech=1.5))
check("the 0.4 s block gets no shot of its own",
      not any(who == "CamB" and b < 45.0 for _a, b, who in cut), str(cut))
off = vpm.build_camera_cut(tracks, 70.0, camera_of, "Wide", min_len=0.0,
                           lead_in=-0.3,
                           rules=vpm.cut_rules(min_speech=0.0))
check("switched off, the same block does reach the picture",
      any(who == "CamB" and b < 45.0 for _a, b, who in off), str(off))
longer = [("Host", [(0.0, 20.0), (30.0, 50.0)]),
          ("Guest", [(20.5, 24.0), (50.0, 70.0)])]
cut = vpm.build_camera_cut(longer, 70.0, camera_of, "Wide", min_len=3.0,
                           lead_in=-0.3,
                           rules=vpm.cut_rules(min_speech=1.5))
check("a 3.5 s block does move it",
      any(who == "CamB" and b < 45.0 for _a, b, who in cut), str(cut))

print("\n2. Short shots are glued to the following one")
band = [(0.0, 10.0, "A"), (10.0, 11.0, "B"), (11.0, 20.0, "C")]
check("the short piece goes to the one after it",
      vpm.merge_short_shots(band, 3.0)
      == [[0.0, 10.0, "A"], [10.0, 20.0, "C"]],
      str(vpm.merge_short_shots(band, 3.0)))
tail = vpm.merge_short_shots([(0.0, 10.0, "A"), (10.0, 11.0, "B")], 3.0)
check("the last one has nothing after it and falls back",
      tail == [[0.0, 11.0, "A"]],
      "%r, wanted [[0.0, 11.0, 'A']]" % (tail,))
pair = vpm.merge_short_shots(
    [(0.0, 10.0, "A"), (10.0, 11.0, "B"), (11.0, 20.0, "A")], 3.0)
check("two of the same camera never end up side by side",
      pair == [[0.0, 20.0, "A"]],
      "%r, wanted [[0.0, 20.0, 'A']]" % (pair,))
kept_long = vpm.merge_short_shots(
    [(0.0, 4.0, "A"), (4.0, 5.0, "B"), (5.0, 6.0, "C"),
     (6.0, 12.0, "D")], 3.0)
check("nothing under the minimum is left over",
      all(b - a >= 3.0 for a, b, _w in kept_long),
      "%d shots of lengths %s, none may fall under 3.00 s"
      % (len(kept_long), [round(b - a, 2) for a, b, _w in kept_long]))

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
one_cam_spans = vpm.unrest_spans(frayed, one_cam)
check("on one camera the same to and fro is one picture, not unrest",
      not one_cam_spans,
      "%r, wanted [] -- 16 segments inside 12.0 s, all of them on CamA, "
      "so one picture change" % (one_cam_spans,))
calm = [("Host", [(0.0, 40.0)]), ("Guest", [(40.0, 80.0)])]
calm_spans = vpm.unrest_spans(calm, two_cams)
check("a calm recognition raises no alarm", not calm_spans,
      "%r, wanted [] -- 2 picture changes in 80.0 s, against the 7 in "
      "12.0 s that count as restless" % (calm_spans,))

print("\n4. Where a cut may sit: the text says roughly, the sound exactly")
near_sentence = vpm.boundary_near(10.0, [11.5], [9.9])
check("a sentence beginning within two seconds wins",
      near_sentence == 11.5,
      "%r, wanted 11.5 -- the sentence 1.5 s off beats the clause 0.1 s off"
      % (near_sentence,))
near_clause = vpm.boundary_near(10.0, [14.0], [9.4])
check("otherwise a clause break within two seconds",
      near_clause == 9.4,
      "%r, wanted 9.4 -- the clause is 0.6 s off, the sentence 4.0 s, "
      "and the near reach is 2.0 s" % (near_clause,))
far_sentence = vpm.boundary_near(10.0, [14.0], [14.5])
check("then the sentence beginning within five",
      far_sentence == 14.0,
      "%r, wanted 14.0 -- the sentence is 4.0 s off, the clause 4.5 s, "
      "both past the near reach of 2.0 s" % (far_sentence,))
backwards = vpm.boundary_near(10.0, [6.5], [])
check("and it searches backwards as well", backwards == 6.5,
      "%r, wanted 6.5 -- 3.5 s before the aim of 10.0" % (backwards,))
too_far = vpm.boundary_near(10.0, [17.0], [16.0])
check("beyond five seconds nothing is found", too_far is None,
      "%r, wanted None -- 7.0 s and 6.0 s off, against a far reach of 5.0 s"
      % (too_far,))
levels = [900] * 500
for i in range(210, 240):
    levels[i] = 3                       # a real gap of 0.3 s
step = 0.010
found = vpm.sound_dip(levels, step, 2.0, 0.5)
check("the dip in the sound is found", found is not None
      and abs(found - 2.25) < 0.05, str(found))
dry = vpm.cut_point(10.0, [9.4], [], (), step)
check("without sound the boundary itself is taken",
      abs(dry - 9.4) < 1e-9,
      "%s s, wanted 9.4 s -- the sentence boundary, with no sound to "
      "measure and an aim of 10.0" % (dry,))
check("with sound the point moves onto the gap",
      abs(vpm.cut_point(2.0, [2.0], [], levels, step) - 2.25) < 0.05,
      str(vpm.cut_point(2.0, [2.0], [], levels, step)))
flat = [500] * 500
flat_dip = vpm.sound_dip(flat, step, 2.0, 0.5)
check("nothing to measure means no dip", flat_dip is None,
      "%r, wanted None -- 500 samples all at 500, so no range to find a "
      "dip in" % (flat_dip,))

print("\n5. How long the wide shot stands")
to_sentence = vpm.wide_shot_length(0.0, 100.0, [3.0, 9.0, 20.0], [7.0],
                                   5.0, 15.0)
check("at least five seconds, then to the end of the sentence",
      to_sentence == 9.0,
      "%s s, wanted 9.0 s -- the first sentence end at or after the 5.0 s "
      "floor; 3.0 is under it" % (to_sentence,))
to_clause = vpm.wide_shot_length(0.0, 100.0, [30.0], [7.0, 12.0, 14.0],
                                 5.0, 15.0)
check("over fifteen seconds the last clause break before it takes over",
      to_clause == 14.0,
      "%s s, wanted 14.0 s -- the last clause at or under the 15.0 s "
      "ceiling, not 7.0 or 12.0" % (to_clause,))
not_mid = vpm.wide_shot_length(0.0, 100.0, [30.0], [7.0, 12.0], 5.0, 15.0)
check("never cut off in the middle of a sentence", not_mid == 12.0,
      "%s s, wanted 12.0 s -- the sentence ends at 30.0, well past the "
      "15.0 s ceiling" % (not_mid,))
bare = vpm.wide_shot_length(0.0, 100.0, [], [], 5.0, 15.0)
check("without any punctuation it holds the minimum", bare == 5.0,
      "%s s, wanted 5.0 s -- no sentence and no clause in 100.0 s of room"
      % (bare,))
cramped = vpm.wide_shot_length(0.0, 2.0, [], [], 5.0, 15.0)
check("and never longer than there is room for", cramped == 2.0,
      "%s s, wanted 2.0 s -- only 2.0 s of room for a 5.0 s minimum"
      % (cramped,))

print("\n6. A change of speaker on one camera is no cut")
same = [("Host", [(0.0, 20.0), (40.0, 60.0)]),
        ("Second", [(20.0, 40.0)])]
cut = vpm.build_camera_cut(same, 60.0, {"Host": "CamA",
                                        "Second": "CamA"}, "Wide",
                           min_len=3.0)
check("one camera for both means one shot", len(cut) == 1, str(cut))

print("\n7. The reaction cut after a question")
talk = [("Host", [(0.0, 4.2)]), ("Guest", [(5.0, 30.0)])]
asked = sentence(0.0, 0.5, 8, close="?")
told = sentence(0.0, 0.5, 8, close=".")
cams = {"Host": "CamA", "Guest": "CamB"}
check("a question fires it",
      vpm.reaction_cuts(talk, asked, cams) == {5.0: "Guest"},
      str(vpm.reaction_cuts(talk, asked, cams)))
stated = vpm.reaction_cuts(talk, told, cams)
check("a statement does not", stated == {},
      "%r, wanted {} -- the same eight words, closing on a full stop"
      % (stated,))
one_camera = vpm.reaction_cuts(talk, asked, {"Host": "CamA",
                                             "Guest": "CamA"})
check("nothing where both sit on the same camera", one_camera == {},
      "%r, wanted {} -- asker and answerer both on CamA" % (one_camera,))
late = [("Host", [(0.0, 4.2)]), ("Guest", [(12.0, 30.0)])]
too_late = vpm.reaction_cuts(late, asked, cams)
check("nothing where the answer comes too late", too_late == {},
      "%r, wanted {} -- the question ends at 3.95, the answer starts at "
      "12.0, and 3.0 s are allowed" % (too_late,))
# Host asks and Guest answers with 0.8 s and is gone again. Guest holds
# 140.8 s of the recording against Host's 28.2, so Host is not the main
# speaker and the question really reaches the rule about the floor.
brief = [("Host", [(0.0, 4.2), (6.0, 30.0)]),
         ("Guest", [(5.0, 5.8), (60.0, 200.0)])]
brief_tally = {}
short_answer = vpm.reaction_cuts(brief, asked, cams, tally=brief_tally)
check("nothing where the answer does not keep the floor",
      short_answer == {} and brief_tally.get("did_not_hold") == 1,
      "%r and %s turned away for not keeping the floor, wanted {} and 1 "
      "-- the answer holds 0.8 s of the next 10.0, under the 7.0 asked"
      % (short_answer, brief_tally.get("did_not_hold")))
main_asks = [("Host", [(0.0, 4.2), (20.0, 200.0)]),
             ("Guest", [(5.0, 20.0)])]
by_main = vpm.reaction_cuts(main_asks, asked, cams)
check("nothing where the main speaker is the one asking", by_main == {},
      "%r, wanted {} -- Host asks and holds 184.2 s of 199.2 s" % (by_main,))
rules = vpm.cut_rules(words=asked, on_question=vpm.SHOT_ANSWER,
                      reaction_lead=1.5)
early = vpm.build_camera_cut(talk, 30.0, cams, "Wide", min_len=0.0,
                             lead_in=-0.3, rules=rules)
plain = vpm.build_camera_cut(talk, 30.0, cams, "Wide", min_len=0.0,
                             lead_in=-0.3,
                             rules=vpm.cut_rules(
                                 words=asked,
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

print("\n8. Every value of every one of the choice fields")
# One long monologue, one place where both speak, one heap of scraps,
# one question and holes between them -- so every field has something
# to decide.
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
            mixed, 320.0, mixed_cams, "Wide", 3.0, 0.3, after=40.0, holds=5.0,
            at_latest=120.0, edge=False,
            rules=vpm.cut_rules(words=mixed_words, **{field: value}))
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
      == sum(len(f[3]) for f in vpm.CUT_CHOICES),
      "%d values tried over %d fields, against %d values over %d fields "
      "in CUT_CHOICES" % (sum(len(v) for v in seen.values()), len(seen),
                          sum(len(f[3]) for f in vpm.CUT_CHOICES),
                          len(vpm.CUT_CHOICES)))

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
check("the preview computes", bool(numbers and numbers.get("cut")),
      "%d shots in the cut, %d numbers in the answer, wanted a cut with "
      "shots in it" % (len((numbers or {}).get("cut") or []),
                       len(numbers or {})))
same = vpm.camera_cut(mixed, 320.0, mixed_cams, "Wide", 3.0, 0.3,
                      after=40.0, holds=5.0, at_latest=120.0, edge=False,
                      rules=vpm.cut_rules(words=mixed_words))
check("and it is the same cut the run builds",
      numbers["cut"] == same, "%d against %d" % (len(numbers["cut"]),
                                                 len(same)))

print("\n11. Silence: a breath in a sentence, or the end of a thought")
# One person, two holes in their own speech: a breath of 0.8 s and a
# stop of 2.5 s. Nobody else says a word, so both are silence and the
# wide shot is the only other picture within reach. The shortest shot
# is set to 0.5 s here, or the merging would hide the answer.
breath = [("Host", [(0.0, 20.0), (20.8, 40.0), (42.5, 60.0)]),
          ("Guest", [(60.0, 80.0)])]
gap_cams = {"Host": "CamA", "Guest": "CamB"}
TODAY = [(0.0, 20.0, "CamA"), (20.0, 20.8, "Wide"), (20.8, 40.0, "CamA"),
         (40.0, 42.5, "Wide"), (42.5, 60.0, "CamA"), (60.0, 80.0, "CamB")]


def silence_cut(**over):
    """The cut over the two holes, with one answer to the silence."""
    return vpm.build_camera_cut(breath, 80.0, gap_cams, "Wide",
                                min_len=0.5, lead_in=0.0,
                                rules=vpm.cut_rules(**over))


def camera_at(cut, when):
    """Which camera stands at this second, or None."""
    for a, b, who in cut:
        if a <= when < b:
            return who
    return None


plain = silence_cut()
check("with nothing set both holes go to the wide shot, as before",
      plain == TODAY, "%d shots %s, wanted the %d of %s"
      % (len(plain), [(a, w) for a, _b, w in plain], len(TODAY),
         [(a, w) for a, _b, w in TODAY]))
told_wide = silence_cut(on_silence=vpm.SHOT_WIDE)
check("and asking for the wide shot by name gives that same cut",
      told_wide == TODAY, "%d shots %s, wanted the %d of %s"
      % (len(told_wide), [(a, w) for a, _b, w in told_wide], len(TODAY),
         [(a, w) for a, _b, w in TODAY]))
brief = silence_cut(on_silence=vpm.SHOT_HOLD_BRIEF, silence_hold=1.0)
check("holding up to 1.0 s: the 0.8 s breath leaves the camera standing",
      camera_at(brief, 20.4) == "CamA",
      "%r at 20.4 s, wanted 'CamA' -- the hole is 0.8 s against a limit "
      "of 1.0 s" % (camera_at(brief, 20.4),))
check("holding up to 1.0 s: the 2.5 s stop goes to the wide shot",
      camera_at(brief, 41.0) == "Wide",
      "%r at 41.0 s, wanted 'Wide' -- the hole is 2.5 s against a limit "
      "of 1.0 s" % (camera_at(brief, 41.0),))
raised = silence_cut(on_silence=vpm.SHOT_HOLD_BRIEF, silence_hold=3.0)
check("the limit is a setting: at 3.0 s the same 2.5 s stop is held",
      camera_at(raised, 41.0) == "CamA",
      "%r at 41.0 s, wanted 'CamA' -- the hole is 2.5 s against a limit "
      "of 3.0 s" % (camera_at(raised, 41.0),))
never = silence_cut(on_silence=vpm.SHOT_HOLD)
check("holding without an end keeps the camera through both holes",
      camera_at(never, 20.4) == "CamA" and camera_at(never, 41.0) == "CamA",
      "%r at 20.4 s and %r at 41.0 s, wanted 'CamA' twice"
      % (camera_at(never, 20.4), camera_at(never, 41.0)))
# And the whole way through, at the minimum edit duration the program
# really uses: a 4.0 s hole is long enough to stand as a shot of its
# own, so what the answer decides is not swallowed by the merging.
long_hole = [("Host", [(0.0, 20.0), (24.0, 40.0)]),
             ("Guest", [(40.0, 60.0)])]
WHOLE = [(0.0, 20.0, "CamA"), (20.0, 24.0, "Wide"), (24.0, 40.0, "CamA"),
         (40.0, 60.0, "CamB")]


def whole_cut(**over):
    """The finished cut the run makes, with one answer to the silence."""
    return vpm.camera_cut(long_hole, 60.0, gap_cams, "Wide", 3.0, 0.0,
                          after=0.0, holds=5.0, at_latest=120.0, edge=False,
                          rules=vpm.cut_rules(**over))


by_default = whole_cut()
check("in the finished cut a 4.0 s hole is the wide shot as before",
      by_default == WHOLE, "%d shots %s, wanted the %d of %s"
      % (len(by_default), [(a, w) for a, _b, w in by_default], len(WHOLE),
         [(a, w) for a, _b, w in WHOLE]))
kept = whole_cut(on_silence=vpm.SHOT_HOLD_BRIEF, silence_hold=5.0)
check("and with the limit past it the answer survives the merging",
      kept == [(0.0, 40.0, "CamA"), (40.0, 60.0, "CamB")],
      "%d shots %s, wanted 2 of [(0.0, 'CamA'), (40.0, 'CamB')]"
      % (len(kept), [(a, w) for a, _b, w in kept]))

print("\n12. What the rules are when nobody sets one")
# Every call above says what it wants, so the value the program falls
# back to can be moved without a check noticing. Measured on 2.9.2026
# against the seventeen tests that touch the cut: nine of the rules
# could be moved and all seventeen stayed green.
#
# The fields of the cut box declare the same numbers a second time, so
# they are what the rules are held against: where the two drift apart,
# one of them is lying to whoever reads it.
NUMBER_OF = {"min-speech-to-switch": "min_speech",
             "reaction-lead": "reaction_lead",
             "wide-most": "wide_most"}
in_the_box = sorted(f[0] for f in vpm.CUT_FIELDS if f[0] in NUMBER_OF)
check("every field named here is still a field of the cut box",
      in_the_box == sorted(NUMBER_OF),
      "%s found, wanted %s -- a renamed field would leave the check "
      "below asking nothing" % (in_the_box, sorted(NUMBER_OF)))
plain_rules = vpm.cut_rules()
adrift = sorted((switch, shown, plain_rules[NUMBER_OF[switch]])
                for switch, _label, shown, _unit, _short, _long
                in vpm.CUT_FIELDS if switch in NUMBER_OF
                and abs(float(shown)
                        - plain_rules[NUMBER_OF[switch]]) > 1e-9)
check("the numbers nobody sets are the ones the fields offer",
      not adrift, "%d of %d disagree (field, offered, used): %s"
      % (len(adrift), len(in_the_box), adrift))
astray = sorted((switch, shown,
                 str(plain_rules.get(switch.replace("-", "_"),
                                     "no such rule")))
                for switch, _label, shown, _values, _short, _long
                in vpm.CUT_CHOICES
                if plain_rules.get(switch.replace("-", "_"),
                                   "no such rule") != shown)
check("and every choice falls back to what its own field calls the "
      "default", not astray,
      "%d of %d disagree (field, offered, used): %s"
      % (len(astray), len(vpm.CUT_CHOICES), astray))
# Three of the reaction cut's numbers stand in no field at all, and
# "Short gap up to" writes its own out of the same constant the rules
# read -- so for these four there is nothing to hold them against, and
# they are written out here instead.
ALONE = {"silence_hold": 1.0, "reaction_gap": 3.0,
         "reaction_hold": 0.7, "reaction_over": 10.0}
moved = sorted((rule, wanted, plain_rules[rule])
               for rule, wanted in ALONE.items()
               if abs(plain_rules[rule] - wanted) > 1e-9)
check("the four numbers with nothing to hold them against are unmoved",
      not moved, "%d of %d moved (rule, wanted, found): %s"
      % (len(moved), len(ALONE), moved))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
