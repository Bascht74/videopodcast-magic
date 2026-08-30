# -*- coding: utf-8 -*-
"""A short reaction is speech, not a hole in the conversation.

Sounds under a floor are dropped before the pause search runs. The
floor stood at four tenths of a second from the first version and had
never been measured -- and an "mhm" is shorter than that, so a reaction
read as a pause and a wide shot could land on top of somebody
answering.

Measured 31.8.2026 on 31 minutes of real three-microphone material:

  0.40 s   2710 passages   5643 s speech   115 pauses over 2 s, 21 over 5
  0.20 s   3105 passages   5759 s speech    94 pauses over 2 s, 13 over 5
  0.15 s   3214 passages   5781 s speech

From 0.4 to 0.2, 395 passages come back for 116 seconds -- 0.29 s each,
the length of an "mhm". Twenty-one pauses over two seconds and eight
over five turn out never to have been pauses. Below 0.2 the gain
flattens: 109 more passages for 22 seconds, 0.2 s each, which is breath.

This file holds the floor there. It builds the case the measurement
describes -- two turns with a short reaction between them -- and asks
whether the reaction is speech and whether the pause is one pause or
two.
"""
import os, sys, wave, shutil, tempfile
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

bad = []


def check(what, ok, detail=""):
    print("  %-56s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


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
      hasattr(vpm, "SPEECH_MIN_LEN_S"))
check("and it stands at 0.2 s",
      abs(getattr(vpm, "SPEECH_MIN_LEN_S", 0) - 0.2) < 1e-9,
      str(getattr(vpm, "SPEECH_MIN_LEN_S", None)))
import inspect
sign = inspect.signature(vpm.speakers_from_tracks)
check("and the measurement uses it, not a number of its own",
      sign.parameters["min_len"].default == vpm.SPEECH_MIN_LEN_S,
      str(sign.parameters["min_len"].default))

print("\n2. One asks, the other says 'mhm', the first goes on")
# The shape the measurement describes: a turn, a short reaction on the
# other microphone, then the answer. Between the two turns there is
# nearly three seconds of quiet on one track -- and that is exactly the
# stretch a wide shot would be put into.
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

# What it is worth: the quiet between the two turns is no longer one
# unbroken stretch. That is the whole point -- an unbroken one invites
# a wide shot, and there is somebody answering in the middle of it.


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
# Below the floor nothing is claimed. A tenth of a second is what a
# breath or a click measures, and calling that speech would put a cut
# on somebody who never spoke.
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
print("\n----")
if bad:
    print("FAIL %d of them: %s" % (len(bad), "; ".join(bad)))
    sys.exit(1)
print("All good.")
