# -*- coding: utf-8 -*-
"""Is the cut true: the right camera, and every time rule kept?

The speech is built here rather than measured, so who ought to be on
screen at any moment is known before the cut is computed.

  1  Whoever speaks is on their own camera, silence is on the wide
     shot, and no shot names a camera that does not exist.
  2  Every setting that is a number holds in the result, the delay
     nobody names is still the one the window offers, and the
     reaction lead counts from the end of the question.
  3  Where no camera is a wide shot, the stand-in is the same one
     wherever the question is asked and does not act as a wide shot.

Every check has a counter-check beside it, the same reading run against
a doctored list or with the setting turned off: a check nobody can make
fail proves nothing.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys, random, time
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

began = time.time()
bad = []
done = 0


def check(name, ok, extra=""):
    """Print one check. What failed carries its numbers on its own line.

    On a build machine only the failing line survives into the report,
    so whatever places the failure belongs in *extra*.
    """
    global done
    done += 1
    print("  %-54s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


#--------------------------------------------------------------- readings
# The same functions serve the checks and the counter-checks, so a
# doctored list has to be caught by the reading that passed the real one.

def gaps_in(cut):
    """Where one shot does not begin where the one before it ends."""
    return [(round(cut[i][1], 3), round(cut[i + 1][0], 3))
            for i in range(len(cut) - 1)
            if abs(cut[i][1] - cut[i + 1][0]) > 1e-6]


def strangers_in(cut, known):
    """Cameras named by the cut that are not among the cameras."""
    return sorted({w for _a, _b, w in cut} - set(known))


def under(cut, limit):
    """Shots shorter than the minimum edit duration."""
    return [(round(a, 2), round(b, 2), w, round(b - a, 2))
            for a, b, w in cut if b - a < limit - 1e-6]


def backwards(cut):
    """Shots that do not run forwards."""
    return [(round(a, 2), round(b, 2), w) for a, b, w in cut if b <= a]


def shown_at(cut, t):
    """Which camera stands at second *t*."""
    for a, b, w in cut:
        if a <= t < b:
            return w
    return None


def inserted_wides(cut, wide):
    """The wide shots put into a long shot, not the ones a silence made.

    An interposed shot has the same camera on both sides of it; one a
    pause produced has two different ones, or stands at an edge.
    """
    return [cut[i] for i in range(1, len(cut) - 1)
            if cut[i][2] == wide and cut[i - 1][2] != wide
            and cut[i - 1][2] == cut[i + 1][2]]


def wrong_camera(cut, tracks, camera_of, delay, margin=0.5):
    """Sample every speech block and report where the wrong camera is up.

    Sampling starts at the block plus the delay, because the picture is
    meant to arrive that much after the sound, and stops *margin* short
    of the end so a boundary is never the thing measured.
    """
    seen = []
    for name, segs in tracks:
        want = camera_of.get(name)
        if not want:
            continue
        for a, b in segs:
            first, last = a + delay + margin, b + delay - margin
            if last <= first:
                continue
            for k in range(9):
                t = first + (last - first) * k / 8.0
                if shown_at(cut, t) != want:
                    seen.append((name, round(t, 2), shown_at(cut, t)))
    return seen


def taking_turns(length, block, gap, names):
    """One speaker after another, each holding the floor for *block*."""
    segs = {n: [] for n in names}
    t, i = 0.0, 0
    while t + block <= length:
        segs[names[i % len(names)]].append((round(t, 3), round(t + block, 3)))
        t += block + gap
        i += 1
    return [(n, segs[n]) for n in names]


def sentences_every(seconds, until, step=1.0):
    """A transcript of five words per sentence, one sentence per period."""
    words, t = [], 0.0
    while t < until:
        for k in range(5):
            when = t + k * step
            words.append(vpm.speech_word(
                when, when + step * 0.9,
                "word" + ("." if k == 4 else "")))
        t += seconds
    return words


NAMES = ["Host", "Guest", "Third"]
CAMERA_OF = {"Host": "CamA", "Guest": "CamB", "Third": "CamC"}
KNOWN = ["CamA", "CamB", "CamC", "Wide"]

# A busy conversation, seeded so every machine sees the same material.
random.seed(11)
busy = {n: [] for n in NAMES}
_t = 0.0
while _t < 900.0:
    _who = NAMES[random.randrange(3)]
    _d = random.uniform(0.4, 25.0)
    busy[_who].append((round(_t, 2), round(min(900.0, _t + _d), 2)))
    _t += _d + random.uniform(0.05, 3.0)
BUSY = [(n, busy[n]) for n in NAMES]

print("1. THE SHAPE OF A CUT")
for min_len in (1.2, 3.0, 6.0):
    cut = vpm.camera_cut(BUSY, 900.0, CAMERA_OF, "Wide", min_len, 0.3,
                         after=40.0, holds=5.0, at_latest=120.0, edge=True,
                         rules=vpm.cut_rules())
    tag = "shortest shot %.1f s" % min_len
    check("%s: shots, and they run forwards" % tag,
          bool(cut) and not backwards(cut),
          "%d shots, %s" % (len(cut), backwards(cut)[:2]))
    check("%s: no gap and no overlap" % tag, not gaps_in(cut),
          str(gaps_in(cut)[:2]))
    check("%s: covers 0 to the end" % tag,
          abs(cut[0][0]) < 1e-6 and abs(cut[-1][1] - 900.0) < 1e-6,
          "%.3f .. %.3f of 900.0" % (cut[0][0], cut[-1][1]))
    check("%s: only cameras that exist" % tag,
          not strangers_in(cut, KNOWN), str(strangers_in(cut, KNOWN)))

print("\n1b. The same readings against lists doctored to break the rule")
whole = vpm.camera_cut(BUSY, 900.0, CAMERA_OF, "Wide", 3.0, 0.3, after=40.0,
                       holds=5.0, at_latest=120.0, edge=True,
                       rules=vpm.cut_rules())
holed = [x for i, x in enumerate(whole) if i != 3]
check("a missing shot is found as a gap", bool(gaps_in(holed)),
      "%d gaps, first %s" % (len(gaps_in(holed)), gaps_in(holed)[:1]))
lapped = [list(x) for x in whole]
lapped[2][1] += 2.0
check("an overlap is found as well", bool(gaps_in(lapped)),
      str(gaps_in(lapped)[:1]))
foreign = list(whole) + [(900.0, 910.0, "CamZ")]
check("a camera nobody has is found",
      strangers_in(foreign, KNOWN) == ["CamZ"],
      str(strangers_in(foreign, KNOWN)))
turned = [(5.0, 5.0, "CamA")] + list(whole)
check("a shot that does not run forwards is found",
      bool(backwards(turned)), str(backwards(turned)))

print("\n2. THE RIGHT CAMERA")
# The wide shot settings are out of the way, so nothing but the
# assignment can decide what is on screen.
turns = taking_turns(300.0, 12.0, 1.0, NAMES)
plain = vpm.camera_cut(turns, 300.0, CAMERA_OF, "Wide", 3.0, 0.3, after=0.0,
                       holds=5.0, at_latest=120.0, edge=False,
                       rules=vpm.cut_rules())
missed = wrong_camera(plain, turns, CAMERA_OF, 0.3)
check("whoever speaks is on their own camera", not missed,
      "%d of %d samples wrong, first %s"
      % (len(missed), 9 * sum(len(s) for _n, s in turns), missed[:2]))
# Counter-check: hold the cut, move the truth one camera along.
moved = {"Host": "CamB", "Guest": "CamC", "Third": "CamA"}
astray = wrong_camera(plain, turns, moved, 0.3)
check("moved one camera along, the same reading catches it",
      len(astray) > 0.9 * 9 * sum(len(s) for _n, s in turns),
      "%d wrong" % len(astray))

quiet = [("Host", [(0.0, 20.0)]), ("Guest", [(40.0, 60.0)])]
lull = vpm.camera_cut(quiet, 80.0, {"Host": "CamA", "Guest": "CamB"}, "Wide",
                      3.0, 0.3, after=0.0, holds=5.0, at_latest=120.0,
                      edge=False, rules=vpm.cut_rules())
check("a silence stands on the wide shot",
      shown_at(lull, 30.0) == "Wide" and shown_at(lull, 70.0) == "Wide",
      "%s at 30 s, %s at 70 s" % (shown_at(lull, 30.0),
                                  shown_at(lull, 70.0)))
free = [("Host", [(0.0, 20.0)]), ("Nobody", [(25.0, 45.0)])]
none = vpm.camera_cut(free, 60.0, {"Host": "CamA"}, "Wide", 3.0, 0.3,
                      after=0.0, holds=5.0, at_latest=120.0, edge=False,
                      rules=vpm.cut_rules())
check("a speaker with no camera goes to the wide shot",
      shown_at(none, 35.0) == "Wide", str(none))
both = [("Host", [(0.0, 20.0)]), ("Co-host", [(10.0, 30.0)]),
        ("Guest", [(35.0, 55.0)])]
pair = vpm.camera_cut(both, 60.0,
                      {"Host": "Hosts", "Co-host": "Hosts", "Guest": "CamG"},
                      "Wide", 3.0, 0.0, after=0.0, holds=5.0, at_latest=120.0,
                      edge=False, rules=vpm.cut_rules())
check("two at once: the camera showing both comes up",
      shown_at(pair, 15.0) == "Hosts", str(pair))

# The same question of the preview, which counts in tenths of a second
# over the whole programme rather than sampling.
sheet = {"speakers": [{"name": n, "sections": s} for n, s in turns],
         "cameras": [{"track": "CamA", "speakers": ["Host"]},
                     {"track": "CamB", "speakers": ["Guest"]},
                     {"track": "CamC", "speakers": ["Third"]},
                     {"track": "Wide", "speakers": []}],
         "length_s": 300.0}
numbers = vpm.cut_statistics(sheet, 3.0, 0.3, 0.0, 5.0, 120.0, False)
check("the preview counts no speech on a wrong camera",
      numbers["off_camera_s"] < 0.05,
      "%.1f s off camera of %.1f s of speech"
      % (numbers["off_camera_s"], numbers["speech_time_s"]))
# Counter-check: three seconds of delay hold the previous speaker on
# screen well into the next turn, and the preview has to say so.
late = vpm.cut_statistics(sheet, 3.0, 3.0, 0.0, 5.0, 120.0, False)
check("and it does count it when the delay is three seconds",
      late["off_camera_s"] > 30.0,
      "%.1f s off camera of %.1f s of speech"
      % (late["off_camera_s"], late["speech_time_s"]))

print("\n3. SHORTEST SHOT (--min-edit-duration)")
for min_len in (1.2, 3.0, 6.0, 10.0):
    cut = vpm.camera_cut(BUSY, 900.0, CAMERA_OF, "Wide", min_len, 0.3,
                         after=0.0, holds=5.0, at_latest=120.0, edge=True,
                         rules=vpm.cut_rules())
    check("nothing under %.1f s stands, wide shot breaks off" % min_len,
          not under(cut, min_len),
          "%d shots, shortest %.3f, under: %s"
          % (len(cut), min(b - a for a, b, _w in cut),
             under(cut, min_len)[:2]))
short = list(whole) + [(900.0, 900.4, "CamA")]
check("a shot of 0.4 s is found by the same reading",
      len(under(short, 3.0)) == 1, str(under(short, 3.0)))

print("\n4. EDIT CHANGE DELAY (--edit-change-delay)")
speech_edges = sorted({t for _n, segs in turns for s in segs for t in s})
for delay in (0.0, 0.3, 1.0, -0.5):
    cut = vpm.camera_cut(turns, 300.0, CAMERA_OF, "Wide", 3.0, delay,
                         after=0.0, holds=5.0, at_latest=120.0, edge=False,
                         rules=vpm.cut_rules())
    want = set(round(e + delay, 6) for e in speech_edges) | {0.0, 300.0}
    off = [round(b, 6) for _a, b, _w in cut[:-1]
           if round(b, 6) not in want]
    check("delay %+.1f s: every cut sits that far after the speech"
          % delay, not off, "%d shots, off the grid: %s" % (len(cut),
                                                            off[:3]))
lead = vpm.camera_cut([("Host", [(0.0, 20.0)]), ("Guest", [(20.0, 40.0)])],
                      40.0, CAMERA_OF, "Wide", 3.0, 1.0, after=0.0, holds=5.0,
                      at_latest=120.0, edge=False, rules=vpm.cut_rules())
check("and the number is the whole of it: 20 s becomes 21 s",
      abs(lead[0][1] - 21.0) < 1e-6, str(lead))
back = vpm.camera_cut([("Host", [(0.0, 20.0)]), ("Guest", [(20.0, 40.0)])],
                      40.0, CAMERA_OF, "Wide", 3.0, -0.5, after=0.0, holds=5.0,
                      at_latest=120.0, edge=False, rules=vpm.cut_rules())
check("negative lets the picture lead: 20 s becomes 19.5 s",
      abs(back[0][1] - 19.5) < 1e-6, str(back))
# And the delay nobody names. Every call above says what it wants, so
# the number the program falls back to could be moved without a check
# noticing -- measured on 2.9.2026 over the seventeen tests that touch
# the cut. It is 0.3 s, the starting value the window offers. The four
# wide shot settings beside it are named even here: they have no
# starting value of their own any more, because the program passes all
# four wherever it asks for a cut.
handover = [("Host", [(0.0, 20.0)]), ("Guest", [(20.0, 40.0)])]
untold = vpm.camera_cut(handover, 40.0, CAMERA_OF, "Wide",
                        after=vpm.WIDE_AFTER_S, holds=5.0, at_latest=120.0,
                        edge=True)
untold_at = untold[0][1] if untold else -1.0
check("with nobody naming a delay the cut still sits 0.3 s late",
      abs(untold_at - 20.3) < 1e-6,
      "%d shots, the first change at %.3f s, wanted 20.300 -- the "
      "speech changes at 20.000" % (len(untold), untold_at))
raw = vpm.build_camera_cut(handover, 40.0, CAMERA_OF, "Wide")
raw_at = raw[0][1] if raw else -1.0
check("the same 0.3 s in the shots before any wide shot is put in",
      abs(raw_at - 20.3) < 1e-6,
      "%d shots, the first change at %.3f s, wanted 20.300 -- the "
      "speech changes at 20.000" % (len(raw), raw_at))

print("\n5. MINIMUM SPEAKING TIME (--min-speech-to-switch)")
# The guest has to hold the floor properly later on, or a single short
# block counts as scraps and the wide shot answers instead of this rule.
brief = [("Host", [(0.0, 20.0), (22.0, 40.0)]),
         ("Guest", [(20.2, 21.0), (45.0, 80.0)])]
early = lambda cut: [w for a, _b, w in cut if a < 40.0]
kept = vpm.build_camera_cut(brief, 80.0, CAMERA_OF, "Wide", min_len=0.5,
                            lead_in=-0.3,
                            rules=vpm.cut_rules(min_speech=1.5))
check("a 0.8 s answer does not move the camera",
      "CamB" not in early(kept), str(kept[:4]))
loose = vpm.build_camera_cut(brief, 80.0, CAMERA_OF, "Wide", min_len=0.5,
                             lead_in=-0.3,
                             rules=vpm.cut_rules(min_speech=0.0))
check("switched off, the same 0.8 s does move it",
      "CamB" in early(loose), str(loose[:4]))
longer = [("Host", [(0.0, 20.0), (24.0, 40.0)]),
          ("Guest", [(20.2, 23.7), (45.0, 80.0)])]
over = vpm.build_camera_cut(longer, 80.0, CAMERA_OF, "Wide", min_len=0.5,
                            lead_in=-0.3,
                            rules=vpm.cut_rules(min_speech=1.5))
check("a 3.5 s answer does move it", "CamB" in early(over),
      str(over[:4]))

print("\n6. THE FOUR WIDE SHOT NUMBERS")
# A sentence boundary every five seconds gives the break somewhere to go.
talk = [("Host", [(0.0, 240.0)]), ("Guest", [(245.0, 280.0)])]
paper = sentences_every(5.0, 240.0)
for after, holds, most in ((40.0, 5.0, 15.0), (30.0, 8.0, 12.0)):
    rules = vpm.cut_rules(words=paper, wide_holds=holds, wide_most=most)
    cut = vpm.camera_cut(talk, 280.0, {"Host": "CamA", "Guest": "CamB"},
                         "Wide", 3.0, 0.3, after=after, holds=holds,
                         at_latest=120.0, edge=False, rules=rules)
    longest = max(b - a for a, b, w in cut if w != "Wide")
    puts = inserted_wides(cut, "Wide")
    check("after %.0f s the camera is left" % after,
          longest <= after + 1e-6,
          "longest on a speaker %.2f s of %.0f allowed" % (longest, after))
    check("an interposed shot stands at least %.0f s" % holds,
          bool(puts) and all(b - a >= holds - 1e-6 for a, b, _w in puts),
          "%d of them, shortest %.2f"
          % (len(puts), min([b - a for a, b, _w in puts] or [0.0])))
    check("and at most %.0f s" % most,
          all(b - a <= most + 1e-6 for a, b, _w in puts),
          "longest %.2f" % max([b - a for a, b, _w in puts] or [0.0]))
off = vpm.camera_cut(talk, 280.0, {"Host": "CamA", "Guest": "CamB"}, "Wide",
                     3.0, 0.3, after=0.0, holds=5.0, at_latest=120.0,
                     edge=False, rules=vpm.cut_rules(words=paper))
check("turned off, the long shot stands the whole way",
      max(b - a for a, b, w in off if w != "Wide") > 200.0,
      "longest %.2f s, %d shots"
      % (max(b - a for a, b, w in off if w != "Wide"), len(off)))

# No transcript and no pause at all: only the upper limit can cut here.
mute = [("Host", [(0.0, 600.0)]), ("Guest", [(600.0, 620.0)])]
for latest in (120.0, 60.0):
    cut = vpm.camera_cut(mute, 620.0, {"Host": "CamA", "Guest": "CamB"},
                         "Wide", 3.0, 0.3, after=40.0, holds=5.0,
                         at_latest=latest, edge=False, rules=vpm.cut_rules())
    longest = max(b - a for a, b, w in cut if w != "Wide")
    check("with nothing to cut on, %.0f s is still the limit" % latest,
          longest <= latest + 1e-6,
          "longest %.2f s, %d shots" % (longest, len(cut)))
free_run = vpm.camera_cut(mute, 620.0, {"Host": "CamA", "Guest": "CamB"},
                          "Wide", 3.0, 0.3, after=0.0, holds=5.0,
                          at_latest=120.0, edge=False, rules=vpm.cut_rules())
check("without the limit the same stretch stands unbroken",
      max(b - a for a, b, w in free_run if w != "Wide") > 500.0,
      "longest %.2f s"
      % max(b - a for a, b, w in free_run if w != "Wide"))

print("\n6b. Where the shortest shot and the interposed shot disagree")
# An open fault: merge_short_shots is the last word everywhere except
# after the wide shots are put in, so an interposed shot arrives at its
# own length and nobody holds it against the minimum. Set the shortest
# shot above the wide shot length -- both are free fields in the window
# -- and a flash of the wide shot reaches the edit.
rules = vpm.cut_rules(words=paper, wide_holds=5.0, wide_most=15.0)
clash = vpm.camera_cut(talk, 280.0, {"Host": "CamA", "Guest": "CamB"}, "Wide",
                       8.0, 0.3, after=40.0, holds=5.0, at_latest=120.0,
                       edge=False, rules=rules)
breach = under(clash, 8.0)
print("     shortest shot 8 s, wide shot length 5 s -> %d shots under "
      "the minimum" % len(breach))
print("     they are %s" % str(breach[:3]))
check("the breach is only where the minimum is above the wide length",
      all(w == "Wide" for _a, _b, w, _d in breach),
      "cameras affected: %s" % sorted({w for _a, _b, w, _d in breach}))
check("it gets no worse than the 5.00 s measured on 29.8.2026",
      all(d >= 5.0 - 1e-6 for _a, _b, _w, d in breach),
      "shortest %.2f s of %d" % (min([d for _a, _b, _w, d in breach]
                                     or [0.0]), len(breach)))
sane = vpm.camera_cut(talk, 280.0, {"Host": "CamA", "Guest": "CamB"}, "Wide",
                      3.0, 0.3, after=40.0, holds=5.0, at_latest=120.0,
                      edge=False, rules=rules)
check("with the minimum below the wide length nothing is short",
      not under(sane, 3.0), str(under(sane, 3.0)[:2]))

print("\n7. REACTION LEAD (--reaction-lead)")
# A question, answered by somebody on another camera. The last word of
# the question ends at 18.8 s and the answer begins at 21.0 s: between
# them lie 2.2 s of pause. The lead is taken off the first of the two,
# so 1.5 s early is 17.3 and 4.0 s early is 14.8 -- counted from the
# answer instead they would be 19.5 and 17.0, and that is the whole
# difference between the two rules.
asked = [vpm.speech_word(t, t + 0.8, "word") for t in range(19)]
asked[-1]["word"] = "word?"
asked += [vpm.speech_word(21.0 + i, 21.8 + i, "word") for i in range(38)]
duo = [("Host", [(0.0, 20.0)]), ("Guest", [(21.0, 60.0)])]
ends = {}
answering = vpm.reaction_cuts(duo, asked, CAMERA_OF, ends=ends)
check("the question's end is reported, not the answer's start",
      sorted(answering) == [21.0] and ends == {21.0: 18.8},
      "answer begins %s, question ended %s, wanted [21.0] and [18.8]"
      % (sorted(answering), sorted(ends.values())))
def early_by(reach):
    """Where the camera changes with this much lead, in seconds."""
    rules = vpm.cut_rules(words=asked, reaction_lead=reach,
                          on_question=vpm.SHOT_ANSWER)
    cut = vpm.camera_cut(duo, 60.0, CAMERA_OF, "Wide", 3.0, 0.3, after=0.0,
                         holds=5.0, at_latest=120.0, edge=False, rules=rules)
    return min([a for a, _b, w in cut if w == "CamB"] or [0.0])


# Written out one by one, not looped: the register that holds the
# counter-proofs reads the first argument of every check out of the
# source, and a name put together while the test runs stands there as
# an expression, not as a sentence.
_when = early_by(1.5)
check("a lead of 1.5 s counts from the end of the question",
      abs(_when - 17.3) < 1e-6,
      "camera changes at %.3f s, wanted 17.300 -- the question ends at "
      "18.800, the answer begins at 21.000" % _when)
_when = early_by(4.0)
check("a lead of 4.0 s counts from there as well",
      abs(_when - 14.8) < 1e-6,
      "camera changes at %.3f s, wanted 14.800 -- the question ends at "
      "18.800, the answer begins at 21.000" % _when)
rules = vpm.cut_rules(words=asked, reaction_lead=0.0,
                      on_question=vpm.SHOT_ANSWER)
none_early = vpm.camera_cut(duo, 60.0, CAMERA_OF, "Wide", 3.0, 0.3, after=0.0,
                            holds=5.0, at_latest=120.0, edge=False,
                            rules=rules)
check("at zero it waits for the delay instead",
      abs(min(a for a, _b, w in none_early if w == "CamB") - 20.3) < 1e-6,
      str(none_early))
rules = vpm.cut_rules(words=asked, reaction_lead=4.0,
                      on_question=vpm.SHOT_OFF)
shut = vpm.camera_cut(duo, 60.0, CAMERA_OF, "Wide", 3.0, 0.3, after=0.0,
                      holds=5.0, at_latest=120.0, edge=False, rules=rules)
check("switched off, nothing comes early at all",
      abs(min(a for a, _b, w in shut if w == "CamB") - 20.3) < 1e-6,
      str(shut))

print("\n8. NO WIDE SHOT: THE STAND-IN")
check("the stand-in does not depend on the order of the list",
      vpm.stand_in_camera(["CamC", "CamA", "CamB"])
      == vpm.stand_in_camera(["CamB", "CamC", "CamA"])
      == vpm.stand_in_camera(["CamA", "CamB", "CamC"]),
      "%s, %s, %s" % (vpm.stand_in_camera(["CamC", "CamA", "CamB"]),
                      vpm.stand_in_camera(["CamB", "CamC", "CamA"]),
                      vpm.stand_in_camera(["CamA", "CamB", "CamC"])))
check("and it answers where the list is empty",
      vpm.stand_in_camera([]) and vpm.stand_in_camera([None, ""]),
      "%s and %s" % (vpm.stand_in_camera([]),
                     vpm.stand_in_camera([None, ""])))

# Every camera carries somebody and none was marked, so there is no wide
# shot; the long silence is the one place a stand-in can be seen at all.
blocks = {"Host": [(0.0, 60.0), (211.0, 271.0)],
          "Guest": [(61.0, 121.0), (272.0, 332.0)],
          "Third": [(122.0, 182.0), (333.0, 393.0)]}
speaking = [{"name": n, "sections": blocks[n]} for n in NAMES]
paper2 = vpm.words_for_handover(sentences_every(5.0, 393.0))
mine = [{"track": "CamA", "speakers": ["Host"]},
        {"track": "CamB", "speakers": ["Guest"]},
        {"track": "CamC", "speakers": ["Third"]}]


def preview(cameras):
    return vpm.cut_statistics(
        {"speakers": speaking, "cameras": cameras, "length_s": 400.0,
         "words": paper2}, 3.0, 0.3, 40.0, 5.0, 120.0, True)


one_way = preview(mine)
other_way = preview(list(reversed(mine)))
check("the same cut whichever way the cameras are listed",
      one_way["cut"] == other_way["cut"],
      "%d shots against %d" % (one_way["shots"], other_way["shots"]))
check("the silence shows the same camera either way",
      shown_at(one_way["cut"], 195.0)
      == shown_at(other_way["cut"], 195.0)
      == vpm.stand_in_camera(["CamA", "CamB", "CamC"])[0],
      "%s and %s, stand-in %s"
      % (shown_at(one_way["cut"], 195.0),
         shown_at(other_way["cut"], 195.0),
         vpm.stand_in_camera(["CamA", "CamB", "CamC"])))
check("the preview says out loud that there is no wide shot",
      one_way["wide"] == "" and one_way["wide_shots"] == [],
      "%r, %s" % (one_way["wide"], one_way["wide_shots"]))
# The expensive part: a stand-in acting as a wide shot would break a
# speaker's block and drop into somebody else's camera.
check("the wide shot settings do nothing without a wide shot",
      not inserted_wides(one_way["cut"], "CamA")
      and one_way["longest"] > 55.0,
      "%d shots, longest %.2f s, %d interposed"
      % (one_way["shots"], one_way["longest"],
         len(inserted_wides(one_way["cut"], "CamA"))))
check("nobody is held on the stand-in while they speak",
      not wrong_camera(one_way["cut"],
                       [(n, blocks[n]) for n in NAMES], CAMERA_OF, 0.3),
      str(wrong_camera(one_way["cut"],
                       [(n, blocks[n]) for n in NAMES],
                       CAMERA_OF, 0.3)[:2]))
# Counter-check: one camera nobody sits in front of.
with_wide = preview(mine + [{"track": "Wide", "speakers": []}])
on_speaker = max(b - a for a, b, w in with_wide["cut"] if w != "Wide")
check("a real wide shot brings the breaks back",
      with_wide["shots"] > one_way["shots"] and on_speaker <= 40.0,
      "%d shots against %d, longest on a speaker %.2f s"
      % (with_wide["shots"], one_way["shots"], on_speaker))
check("and then the preview names it",
      with_wide["wide"] == "Wide" and with_wide["wides"] > 0,
      "%r, %d wide shots in the cut"
      % (with_wide["wide"], with_wide["wides"]))
# A marked camera beats the derivation, so the stand-in is never asked.
marked = preview([dict(mine[0], wide_marked=True)] + mine[1:])
check("a marked camera is the wide shot even with a speaker on it",
      marked["wide"] == "CamA" and marked["wide_shots"] == ["CamA"],
      "%r, %s" % (marked["wide"], marked["wide_shots"]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
