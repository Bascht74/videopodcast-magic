# -*- coding: utf-8 -*-
"""Let the speaker separation really run, on two voices we spoke.

Elsewhere the separation is replaced by stand-ins, since it wants a
model, an environment and minutes of computing -- so a changed return
shape in pyannote.audio broke the program unnoticed. Here it runs on
speech say(1) writes, where every boundary is known exactly; two voices
that never overlap show the machinery works, not how well it does.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
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

import importlib.util
import time
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

# Nearly three times the worst boundary error measured, so a slower
# machine does not turn it red. Further out than a third of a second
# would move a cut into the wrong sentence.
TOLERANCE_S = 0.30

error = []


def check(what, ok, detail=""):
    print("  %-52s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        error.append(what)


def leave(why):
    """Say nothing was checked and why. run.sh counts these apart."""
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
if not vpm.speaker_venv_python():
    leave("the speaker separation is not set up (no environment under "
          "%s) -- it is 218 MB, and a test does not fetch that"
          % vpm.speaker_venv_folder())
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

#----------------------------------------------- 1. does it run at all

print("\n1. The separation runs")
started = time.time()
segments, trouble = vpm.speaker_split_run(talk)
took = time.time() - started
check("the run comes back without a complaint", not trouble, trouble)
check("something came out of it", bool(segments), "nothing did")
print("      %.1f s of computing for %.1f s of material"
      % (took, truth[-1][2]))
if trouble or not segments:
    # This is the shape a broken separation arrives in, so the sentence
    # is the whole finding and gets a line of its own.
    print("\nFAIL: the separation did not run -- %s"
          % (trouble or "no segments came back"))
    sys.exit(1)
shape = all(
    isinstance(label, str) and parts
    and all(isinstance(a, float) and isinstance(b, float) and b > a
            for a, b in parts)
    for label, parts in segments)
check("the shape the rest of the program reads", shape, repr(segments)[:90])

#-------------------------------------------------- 2. how many voices

print("\n2. How many speakers")
for label, parts in segments:
    print("      %-14s %5.1f s in %2d pieces"
          % (label, sum(b - a for a, b in parts), len(parts)))
check("as many voices as spoke: %d" % len(spoke),
      len(segments) == len(spoke),
      "found %d: %s" % (len(segments), [x[0] for x in segments]))

#------------------------------------------------- 3. where the edges are

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
check("one stretch per turn: %d" % len(truth), len(runs) == len(truth),
      "found %d" % len(runs))
if len(runs) == len(truth):
    swapped = []
    carries = {}
    for (_a, _b, label), (who, _x, _y) in zip(runs, truth):
        if carries.setdefault(who, label) != label:
            swapped.append(who)
    check("each voice keeps one label all the way", not swapped,
          "%s changed label" % swapped)
    worst, where = 0.0, ""
    for (a, b, _label), (who, x, y) in zip(runs, truth):
        for edge, found_at, wanted in (("start", a, x), ("end", b, y)):
            if abs(found_at - wanted) > worst:
                worst = abs(found_at - wanted)
                where = "%s of the turn at %.3f s of %s" % (edge, wanted, who)
    print("      worst boundary %.3f s out: %s" % (worst, where))
    check("no boundary further out than %.2f s" % TOLERANCE_S,
          worst <= TOLERANCE_S, "%.3f s, %s" % (worst, where))

print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
