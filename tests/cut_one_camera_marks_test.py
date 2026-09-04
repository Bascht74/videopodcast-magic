# -*- coding: utf-8 -*-
"""One camera for everybody: the cut still marks the speaker changes.

One camera the old way, then split at the change of speaker; two
cameras, where the shots are the speakers already; a short
interjection; silence; and last two shots that become one, which has
to carry the names of both. What the detailed cut says about who is
talking is held against written-out names, not against a second
reading of the same tracks. How wide a row is gets one judgement, and
only for the plain cut list, which may not grow a name field it never
had; everywhere else the callers unpack by name, so a row of the wrong
width ends the run before a check could speak.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import sys, time
vpm = the_program.load()

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

print("\n6. Two shots joined into one name everybody heard in it")
# Measured on 2.9.2026: Host ten seconds, Guest ten seconds, both on
# the same camera. The picture never changes, so it is one shot -- and
# named after the first speaker alone the Guest disappeared from the
# Speaker column of the cut list the user gets, and with one camera for
# everybody from the clip names in the EDL. It happens on three roads,
# and each has its own line here. The wanted values are written out;
# read off the tracks again they would repeat the program's reading.
turn_taking = [("Host", [(0.0, 10.0)]), ("Guest", [(10.0, 20.0)])]
joined = vpm.camera_cut_detail(turn_taking, 20.0, one, "Wide",
                               min_len=3.0, lead_in=0.0,
                               rules=vpm.cut_rules(min_speech=0.5))
check("two turns on one camera come out as one shot",
      [(r[0], r[1], r[2]) for r in joined] == [(0.0, 20.0, "Wide")],
      "%s, wanted one shot of 0.0 .. 20.0 on Wide"
      % ([(r[0], r[1], r[2]) for r in joined],))
check("and that shot names both people heard in it",
      [r[3] for r in joined] == [("Guest", "Host")],
      "%s, wanted [('Guest', 'Host')] -- the Host alone is the fault "
      "this asks about" % ([r[3] for r in joined],))
brief = [("Host", [(0.0, 30.0)]), ("Guest", [(10.0, 10.4)])]
swallowed = vpm.split_shots_by_speaker(
    vpm.build_camera_cut(brief, 30.0, one, "Wide"), brief, 1.2)
check("a shot too short to stand takes its speaker into the one that "
      "swallows it",
      [r[3] for r in swallowed] == [("Host",), ("Guest", "Host")],
      "%s, wanted [('Host',), ('Guest', 'Host')]"
      % ([r[3] for r in swallowed],))
# The last shot has nothing after it, so it goes back into the one
# before -- the other half of the same rule, and it lost the name the
# same way.
tail = vpm.merge_short_shots([[0.0, 10.0, "Wide", ("Host",)],
                              [10.0, 11.0, "CamB", ("Guest",)]], 3.0)
check("and a last shot too short to stand takes its speaker back with it",
      [tuple(r) for r in tail] == [(0.0, 11.0, "Wide", ("Guest", "Host"))],
      "%s, wanted [(0.0, 11.0, 'Wide', ('Guest', 'Host'))]"
      % ([tuple(r) for r in tail],))
# The plain cut list carries three fields and no names at all, and the
# same merging runs over it. It may not grow a fourth.
plain = vpm.merge_short_shots([(0.0, 10.0, "Wide"), (10.0, 11.0, "CamB")],
                              3.0)
check("while a cut list that carries no names is joined as before",
      [tuple(r) for r in plain] == [(0.0, 11.0, "Wide")],
      "%s, wanted [(0.0, 11.0, 'Wide')]" % ([tuple(r) for r in plain],))
# A short shot between two shots of the same camera goes into the one
# after it, and the two left standing are then one shot again. That
# second fold gathers names of its own, and no line above reaches it.
between = vpm.merge_short_shots([[0.0, 10.0, "Wide", ("Host",)],
                                 [10.0, 11.0, "CamB", ("Guest",)],
                                 [11.0, 21.0, "Wide", ("Third",)]], 3.0)
check("and neighbours left side by side become one shot naming all "
      "three",
      [tuple(r) for r in between]
      == [(0.0, 21.0, "Wide", ("Guest", "Host", "Third"))],
      "%s, wanted [(0.0, 21.0, 'Wide', ('Guest', 'Host', 'Third'))]"
      % ([tuple(r) for r in between],))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
