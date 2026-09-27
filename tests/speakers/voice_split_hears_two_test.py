# -*- coding: utf-8 -*-
"""Let the speaker separation really run, on two voices we spoke.

Elsewhere the separation is replaced by stand-ins, since it wants a
model, an environment and minutes of computing -- so a changed return
shape in pyannote.audio broke the program unnoticed. Here it runs on
speech say(1) writes, where every boundary is known exactly; two voices
that never overlap show the machinery works, not how well it does.

In order: that it runs and hands back the shape the rest of the
program reads, that it hears as many voices as spoke, that every turn
is one stretch under one label with its edges where truth has them,
that the voice print of each voice finds that voice again in a
second recording -- the material cut in two in the pause between two
turns -- and never the other one, and that a recording a recorder
split into two blocks, the second voice only in the second, is one
microphone to window and run, heard whole and stored under the whole,
and puts both voices into the cut after the block's edge.
"""
PLATFORM_BOUND = True
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import the_program

SCRIPT = the_program.SCRIPT
sys.path.insert(0, HERE)
from fixture_root import fixture

# Both of these have to go before the program is loaded. run.sh switches
# the separation off for the whole suite, and the switch is read once,
# at import.
os.environ.pop("VPM_NO_SPEAKER_SPLIT", None)
# run.sh also gives every run a cache folder of its own, but the
# separation environment lives in the real cache where whoever set it up
# put it, so this one test looks where the program looks in earnest.
os.environ.pop("VPM_CACHE", None)

import shutil
import tempfile
import time
import types
import wave
vpm = the_program.load()

# Nearly three times the worst boundary error measured, so a slower
# machine does not turn it red. Further out than a third of a second
# would move a cut into the wrong sentence.
TOLERANCE_S = 0.30

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def finish():
    """The one way out. Every path that judged anything comes past here."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


def leave(why):
    """Say nothing was checked and why. run.sh counts these apart."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("SKIPPED: " + why)
    sys.exit(0)


def pair(x):
    """Two things that can be taken apart, whatever they are wrapped in."""
    return isinstance(x, (tuple, list)) and len(x) == 2


#------------------------------------------------- is this machine able

if os.environ.get("VPM_SKIP_REAL_SPEAKER"):
    leave("VPM_SKIP_REAL_SPEAKER is set")
folder = fixture("twovoices")
talk = os.path.join(folder, "talk.wav")
truth_file = os.path.join(folder, "truth.txt")
if not (os.path.isfile(talk) and os.path.isfile(truth_file)):
    leave("no spoken material in %s -- fixtures.sh builds it where "
          "say(1) is there" % folder)
if not vpm.speaker_split_available(deep=True):
    leave("pyannote does not import under %s -- it comes with the "
          "program now, so pip3 install -U of this package puts it "
          "back; a test does not fetch it" % vpm.speaker_python())
if not vpm.speaker_model_folder():
    leave("no separation model beside %s -- it is 33 MB, and a test "
          "does not fetch that either" % SCRIPT)

truth = []
for line in open(truth_file, encoding="utf-8"):
    parts = line.split()
    if len(parts) == 3:
        truth.append((parts[0], float(parts[1]), float(parts[2])))
if len(truth) < 2:
    leave("the truth file %s holds fewer than two turns" % truth_file)
try:
    voices = open(os.path.join(folder, "voices.txt"),
                  encoding="utf-8").read().split()
except OSError:
    voices = []
spoke = sorted(set(who for who, _a, _b in truth))
print("Spoken by %s: %d turns, %.1f s in all"
      % (" and ".join(voices) or "two voices", len(truth), truth[-1][2]))

#------------------------------------------------- 1. does it run at all

print("\n1. The separation runs")
started = time.time()
segments, trouble = vpm.speaker_split_run(talk)
took = time.time() - started
print("      %.1f s of computing for %.1f s of material"
      % (took, truth[-1][2]))
check("the separation comes back without a complaint", not trouble,
      "%.1f s of computing, and it said: %s" % (took, trouble or "nothing"))
check("the separation finds at least one voice", bool(segments),
      "%d voices back" % len(segments))
if trouble or not segments:
    # Nothing below says anything once the run itself did not happen,
    # and the two lines above already carry what went wrong.
    finish()

# The shape everything under here takes apart, so it is judged before
# it is used: a red line about boundaries would otherwise be the second
# thing that was wrong, and pyannote changing its return is the very
# fault this test was written for.
nameless = [x for x in segments if not (pair(x) and isinstance(x[0], str))]
empty = [x for x in segments if pair(x) and not x[1]]
check("every voice comes back under a name with pieces to it",
      not nameless and not empty,
      "%d voices, %d not a named pair, %d with no pieces: %s"
      % (len(segments), len(nameless), len(empty),
         repr(nameless or empty)[:60]))
pieces = []
for x in segments:
    if pair(x) and isinstance(x[1], (list, tuple)):
        pieces.extend(x[1])
crooked = [p for p in pieces
           if not (pair(p) and isinstance(p[0], float)
                   and isinstance(p[1], float) and p[1] > p[0])]
check("every piece is a pair of seconds that runs forwards",
      bool(pieces) and not crooked,
      "%d pieces, %d of them not a forward pair of seconds: %s"
      % (len(pieces), len(crooked), repr(crooked[:3])[:60]))
if nameless or empty or crooked:
    finish()

#-------------------------------------------------- 2. how many voices

print("\n2. How many speakers")
for label, parts in segments:
    print("      %-14s %5.1f s in %2d pieces"
          % (label, sum(b - a for a, b in parts), len(parts)))
check("as many voices come back as spoke", len(segments) == len(spoke),
      "%d voices against the %d that spoke: %s"
      % (len(segments), len(spoke), [x[0] for x in segments]))

#----------------------------------------------- 3. where the edges are

print("\n3. Where the turns begin and end")
# Neighbours carrying the same label are one turn: what is measured is
# the change of speaker, not every pause inside a voice.
flat = sorted((a, b, label) for label, parts in segments
              for a, b in parts)
runs = []
for a, b, label in flat:
    if runs and runs[-1][2] == label:
        runs[-1][1] = max(runs[-1][1], b)
    else:
        runs.append([a, b, label])
check("each turn comes back as one unbroken stretch",
      len(runs) == len(truth),
      "%d stretches against %d turns spoken" % (len(runs), len(truth)))
if len(runs) == len(truth):
    swapped = []
    carries = {}
    for (_a, _b, label), (who, _x, _y) in zip(runs, truth):
        if carries.setdefault(who, label) != label:
            swapped.append(who)
    check("each voice keeps one label from first turn to last",
          not swapped,
          "%d of %d turns under a label the voice did not keep: %s"
          % (len(swapped), len(truth), sorted(set(swapped))))
    worst, where = 0.0, ""
    for (a, b, _label), (who, x, y) in zip(runs, truth):
        for edge, found_at, wanted in (("start", a, x), ("end", b, y)):
            if abs(found_at - wanted) > worst:
                worst = abs(found_at - wanted)
                where = "%s of the turn at %.3f s of %s" % (edge, wanted, who)
    check("no boundary is further out than the tolerance allows",
          worst <= TOLERANCE_S,
          "worst %.3f s against the %.2f s allowed -- %s"
          % (worst, TOLERANCE_S, where))

#------------------------------------- 4. the same voice, a second time

print("\n4. The same voice in a second recording")
prints = vpm.SPEAKER_VOICES_HEARD.get(talk) or {}
check("every voice comes back with a voice print",
      sorted(prints) == sorted(x[0] for x in segments)
      and len(set(len(v) for v in prints.values())) == 1,
      "prints for %s, lengths %s, voices %s"
      % (sorted(prints), sorted(set(len(v) for v in prints.values())),
         [x[0] for x in segments]))
# Cut in the pause after the fourth turn: both voices speak on either
# side, and the second part says sentences the first never did.
cut_at = (truth[3][2] + truth[4][1]) / 2.0 if len(truth) > 4 else 0.0
halves = tempfile.mkdtemp(prefix="vpm_two_halves_")
with wave.open(talk, "rb") as w:
    shape, rate = w.getparams(), w.getframerate()
    audio = w.readframes(w.getnframes())
step = shape.sampwidth * shape.nchannels
parted, heard = {}, {}
for part, piece in (("first", audio[:int(cut_at * rate) * step]),
                    ("second", audio[int(cut_at * rate) * step:])):
    path = os.path.join(halves, "%s.wav" % part)
    with wave.open(path, "wb") as w:
        w.setparams(shape)
        w.writeframes(piece)
    parted[part], _why = vpm.speaker_split_run(path)
    heard[part] = vpm.SPEAKER_VOICES_HEARD.get(path) or {}
    print("      %-7s %d voices, %d prints" % (part, len(parted[part]),
                                              len(heard[part])))
shutil.rmtree(halves, ignore_errors=True)


def who(label, parts, offset):
    """The voice truth has most of this label's time under."""
    most = {}
    for a, b in parts:
        for voice, x, y in truth:
            most[voice] = most.get(voice, 0.0) + max(
                0.0, min(b + offset, y) - max(a + offset, x))
    return max(most, key=most.get) if most else "?"


first_is = dict((label, who(label, parts, 0.0))
                for label, parts in parted["first"])
second_is = dict((label, who(label, parts, cut_at))
                 for label, parts in parted["second"])
found = vpm.speaker_voices_alike(heard["first"], heard["second"])
said = sorted((first_is.get(a, "?"), second_is.get(b, "?"), alike)
              for a, b, alike in found)
check("each voice is found again in the second recording",
      sorted(set(x for x, y, _s in said if x == y)) == spoke,
      "pairs %s against the voices %s, line %.2f"
      % (said, spoke, vpm.SPEAKER_SAME_VOICE))
check("two voices are never proposed as one",
      not [x for x in said if x[0] != x[1]],
      "pairs %s, line %.2f" % (said, vpm.SPEAKER_SAME_VOICE))

#------------------------------------ 5. one recording in two blocks

print("\n5. One recording a recorder split in two")
# Cut in the pause after the first turn, so the second voice speaks in
# the second block only. A cache of its own, removed with the blocks:
# what is stored here must not be found by a later run.
edge = (truth[0][2] + truth[1][1]) / 2.0
split = tempfile.mkdtemp(prefix="vpm_two_blocks_")
cache_was = os.environ.get("VPM_CACHE")
os.environ["VPM_CACHE"] = os.path.join(split, "cache")
blocks = [os.path.join(split, "REC_0001.wav"),
          os.path.join(split, "REC_0002.wav")]
for path, piece in ((blocks[0], audio[:int(edge * rate) * step]),
                    (blocks[1], audio[int(edge * rate) * step:])):
    with wave.open(path, "wb") as w:
        w.setparams(shape)
        w.writeframes(piece)
later = truth[1][0]
first_voice = truth[0][0]


def heard_of(segs, voice, after=0.0):
    """Seconds of *voice*'s turns after *after* each label lies on."""
    out = {}
    for label, parts in segs:
        for a, b in parts:
            for who_, x, y in truth:
                if who_ == voice:
                    out[label] = out.get(label, 0.0) + max(
                        0.0, min(b, y) - max(a, x, after))
    return out


# Every edge may lie the tolerance out, so each turn may come back that
# much shorter at either end.
spoken_later = sum(y - x for w_, x, y in truth if w_ == later)
short_later = 2 * TOLERANCE_S * len([1 for w_, _x, _y in truth
                                     if w_ == later])
spoken_first_after = sum(y - max(x, edge) for w_, x, y in truth
                         if w_ == first_voice and y > edge)
short_first = 2 * TOLERANCE_S * len([1 for w_, _x, y in truth
                                     if w_ == first_voice and y > edge])
picked = vpm.speaker_source_pick(
    vpm.recordings_of_blocks(blocks, {blocks[0]: blocks}), [], alone=True)
check("the window takes a recording in blocks for one microphone",
      picked == (blocks[0], "one recording"),
      "picked %s as %s, of %s" % (os.path.basename(picked[0]) or "nothing",
                                  picked[1],
                                  [os.path.basename(b) for b in blocks]))
answers = []
vpm.speaker_split_work(blocks[0], 0, lambda t, s: None, lambda: False,
                       answers.append, blocks)
_s, _c, whole, trouble, heard_blocks = (answers or [("", 0, [], "none",
                                                      [])])[0]
last_end = max([b for _l, parts in whole for _a, b in parts] or [0.0])
check("the window's separation hears every block of the recording",
      not trouble and heard_blocks == blocks
      and last_end >= truth[-1][2] - TOLERANCE_S,
      "heard %s, last voice ends at %.2f s against %.2f s spoken, said %s"
      % ([os.path.basename(b) for b in heard_blocks], last_end,
         truth[-1][2], trouble or "nothing"))
on_later = heard_of(whole, later)
label_later = max(on_later, key=on_later.get) if on_later else ""
begins = min([a for label, parts in whole if label == label_later
              for a, _b in parts] or [0.0])
check("a voice speaking only in the second block is found",
      bool(label_later) and len(whole) == len(spoke)
      and begins >= edge - TOLERANCE_S
      and on_later.get(label_later, 0.0) >= spoken_later - short_later,
      "%d voices; %s under %s for %.1f of %.1f s, from %.2f s, the edge "
      "at %.2f s" % (len(whole), later, label_later or "nobody",
                     on_later.get(label_later, 0.0), spoken_later, begins,
                     edge))
stored_whole = vpm.speaker_split_stored(blocks[0], 0, blocks)
stored_first = vpm.speaker_split_stored(blocks[0], 0)
check("a recording in blocks is stored under the whole, not block one",
      bool(stored_whole) and not stored_first,
      "under the whole %d voices, under the first block %d"
      % (len(stored_whole), len(stored_first)))
# The run, with the track as join_the_plan makes it: the blocks, and the
# joined sound, which is the material the blocks were cut from.
run_tracks = [{"name": "Guest", "source": talk, "axis": talk,
               "blocks": list(blocks), "a": 0.0, "b": 1.0}]
run_args = types.SimpleNamespace(speakers_count=0, dry_run=False)
run_pick = vpm.separation_source_of_run(run_args, run_tracks, [])
check("the run takes a recording in blocks for one microphone",
      run_pick == (blocks[0], "one recording"),
      "picked %s as %s" % (os.path.basename(run_pick[0]) or "nothing",
                           run_pick[1]))
run_args._speakers = vpm.separation_for_run(run_args, run_tracks, {}, 0.0,
                                            truth[-1][2] + 1.0)
in_cut = vpm.speakers_for_the_cut(run_args, run_tracks)
cut_later = heard_of(in_cut, later)
cut_first = heard_of(in_cut, first_voice, edge)
best_later = max(cut_later.values() or [0.0])
best_first = max(cut_first.values() or [0.0])
check("the voice of the second block is in the cut",
      best_later >= spoken_later - short_later,
      "%.1f of %.1f s of %s in the cut, by name %s"
      % (best_later, spoken_later, later, sorted(cut_later.items())))
check("the first block's voice is still in the cut after the edge",
      best_first >= spoken_first_after - short_first,
      "%.1f of %.1f s of %s after %.2f s in the cut, by name %s"
      % (best_first, spoken_first_after, first_voice, edge,
         sorted(cut_first.items())))
if cache_was is None:
    os.environ.pop("VPM_CACHE", None)
else:
    os.environ["VPM_CACHE"] = cache_was
shutil.rmtree(split, ignore_errors=True)

finish()
