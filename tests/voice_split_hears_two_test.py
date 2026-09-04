# -*- coding: utf-8 -*-
"""Let the speaker separation really run, on two voices we spoke.

Elsewhere the separation is replaced by stand-ins, since it wants a
model, an environment and minutes of computing -- so a changed return
shape in pyannote.audio broke the program unnoticed. Here it runs on
speech say(1) writes, where every boundary is known exactly; two voices
that never overlap show the machinery works, not how well it does.

Three sections: that it runs and hands back the shape the rest of the
program reads, that it hears as many voices as spoke, and that every
turn is one stretch under one label with its edges where truth has them.
"""
import os
import sys
import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
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

import time
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

finish()
