# -*- coding: utf-8 -*-
"""A short reaction is speech, not a hole in the conversation.

Sounds under a floor are dropped before the pause search runs. At four
tenths of a second an "mhm" falls under it, so a reaction reads as a
pause and a wide shot can land on top of somebody answering. On real
material the floor belongs at 0.2 s: down to there whole reactions
come back, and below it the gain is breath. The case built here is two
turns with a short reaction between them.
"""
import os, sys, wave, shutil, tempfile, time
import numpy as np
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
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


RATE = 16000
folder = tempfile.mkdtemp(prefix="vpm_floor_")


def talk(x, at, length, hz, level=0.35):
    """Put a speech-like sound into the track at that second."""
    n = int(length * RATE)
    t = np.arange(n) / float(RATE)
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * 3.1 * t)
    sound = swell * (np.sin(2 * np.pi * hz * t)
                     + 0.5 * np.sin(2 * np.pi * 2 * hz * t)) / 1.5
    a = int(at * RATE)
    x[a:a + n] += level * sound
    return x


def track(name, turns, seconds=16.0):
    """One microphone: a quiet floor with those turns on it."""
    x = np.random.RandomState(7).normal(0, 0.0006, int(seconds * RATE))
    for at, length, hz in turns:
        talk(x, at, length, hz)
    path = os.path.join(folder, name)
    with wave.open(path, "w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes(np.clip(x * 22000, -32000, 32000)
                      .astype("<i2").tobytes())
    return path


print("1. The floor is where the measurement put it")
check("the floor is a named number, not a spelling in a signature",
      hasattr(vpm, "SPEECH_MIN_LEN_S"),
      "SPEECH_MIN_LEN_S is %r, wanted a number"
      % (getattr(vpm, "SPEECH_MIN_LEN_S", None),))
check("and it stands at 0.2 s",
      abs(getattr(vpm, "SPEECH_MIN_LEN_S", 0) - 0.2) < 1e-9,
      str(getattr(vpm, "SPEECH_MIN_LEN_S", None)))
import inspect
sign = inspect.signature(vpm.speakers_from_tracks)
check("and the measurement uses it, not a number of its own",
      sign.parameters["min_len"].default == vpm.SPEECH_MIN_LEN_S,
      str(sign.parameters["min_len"].default))

print("\n2. One asks, the other says 'mhm', the first goes on")
# A turn, a short reaction on the other microphone, then the answer.
# Between the turns lies nearly three seconds of quiet on one track --
# exactly the stretch a wide shot would be put into.
asks = track("asks.wav", [(0.5, 4.0, 130.0), (8.0, 4.0, 130.0)])
answers = track("answers.wav", [(6.0, 0.28, 190.0)])
pair = [("Asks", asks, 0.0), ("Answers", answers, 0.0)]

found = dict(vpm.speakers_from_tracks(pair, separate=False))
short = [(a, b) for a, b in found.get("Answers", [])
         if 5.0 < a < 7.0]
check("the short reaction is found at all", bool(short), str(found))
if short:
    a, b = short[0]
    check("and it is about as long as it was built", 0.15 < b - a < 0.6,
          "%.2f s" % (b - a))

# What it is worth: an unbroken stretch of quiet invites a wide shot,
# and here somebody is answering in the middle of it.


def longest_quiet(min_len):
    """The longest stretch in which nobody is speaking at all."""
    spans = sorted(s for _n, segs in vpm.speakers_from_tracks(
        pair, min_len=min_len, separate=False) for s in segs)
    joined = []
    for a, b in spans:
        if joined and a <= joined[-1][1] + 0.01:
            joined[-1] = (joined[-1][0], max(joined[-1][1], b))
        else:
            joined.append((a, b))
    return max([a2 - b1 for (_a1, b1), (a2, _b2)
                in zip(joined, joined[1:])] or [0.0])


was, now = longest_quiet(0.4), longest_quiet(vpm.SPEECH_MIN_LEN_S)
check("the old floor leaves one long pause where the answer was",
      was > 3.0, "%.2f s" % was)
check("the new floor cuts it in two", now < was - 1.0,
      "%.2f s instead of %.2f s" % (now, was))

print("\n3. Breath is not an answer")
# A tenth of a second is a breath or a click, and calling that speech
# would put a cut on somebody who never spoke.
answers_short = track("breath.wav", [(6.0, 0.10, 190.0)])
found = dict(vpm.speakers_from_tracks(
    [("Asks", asks, 0.0), ("Answers", answers_short, 0.0)], separate=False))
blips = [(a, b) for a, b in found.get("Answers", []) if 5.0 < a < 7.0]
check("a tenth of a second is not counted as speech", not blips,
      str(blips))

print("\n4. The floor can still be raised by whoever wants it raised")
found = dict(vpm.speakers_from_tracks(pair, min_len=0.4, separate=False))
raised = [(a, b) for a, b in found.get("Answers", []) if 5.0 < a < 7.0]
check("at the old floor the same reaction disappears again", not raised,
      str(raised))

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
