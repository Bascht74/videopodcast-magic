# -*- coding: utf-8 -*-
"""A recording split into blocks is heard whole by the window and the run.

The speaker separation really runs here, as in voice_split_hears_two, on
the same spoken material -- cut in the pause after the first turn into
two blocks the way a recorder splits a long file, so the second voice
speaks in the second block only. In order: the window takes the blocks
for one microphone, hears every block and finds the voice of the second,
and stores what it heard under the whole rather than block one; then
the run takes them for one microphone too, and both voices reach the
cut after the block's edge.
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
# at import. And the separation environment lives in the real cache, so
# the question whether it can run is asked there; what this test stores
# goes into a folder of its own, set further down.
os.environ.pop("VPM_NO_SPEAKER_SPLIT", None)
os.environ.pop("VPM_CACHE", None)

import shutil
import tempfile
import time
import types
import wave
vpm = the_program.load()

# The same allowance voice_split_hears_two gives every edge: nearly
# three times the worst boundary error measured.
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
spoke = sorted(set(who for who, _a, _b in truth))
print("Spoken: %d turns by %d voices, %.1f s in all"
      % (len(truth), len(spoke), truth[-1][2]))

#------------------------------------ one recording in two blocks

print("\nOne recording a recorder split in two")
# Cut in the pause after the first turn, so the second voice speaks in
# the second block only. A cache of its own, removed with the blocks:
# what is stored here must not be found by a later run.
with wave.open(talk, "rb") as w:
    shape, rate = w.getparams(), w.getframerate()
    audio = w.readframes(w.getnframes())
step = shape.sampwidth * shape.nchannels
edge = (truth[0][2] + truth[1][1]) / 2.0
split = tempfile.mkdtemp(prefix="vpm_two_blocks_")
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
os.environ.pop("VPM_CACHE", None)
shutil.rmtree(split, ignore_errors=True)

finish()
