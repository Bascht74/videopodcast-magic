# -*- coding: utf-8 -*-
"""A short mono file goes through a real production and comes back as audio.

Against auphonic.com itself, and it spends credit: twenty seconds of
syllables through the account's first single-track preset, or the one
VPM_LIVE_PRESET names. In order -- the program uploads and starts in one
call, waits, and fetches the result; the file the program leaves is as
long as the one sent, whatever auphonic.com put around it; and the
production, found again by its title, is deleted. The title has the
tests' own shape, so a run killed half way is cleared by the sweep
auphonic.sh makes at both ends.

Syllables and not a steady tone: the free plan puts a jingle in front
(26.4 s came back for 20 s, 27.9.2026), and the program finds the sound
it sent by its rises and falls, which a steady tone does not have.

A step that throws is a failed judgement and not a traceback, so the
closing count is reached whatever happens.
"""
import math
import os
import random
import shutil
import struct
import sys
import tempfile
import time
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import auphonic_ground as ground

ground.gate(spends=True)

began = time.time()
done = 0
bad = []
SECONDS = 20
# How far the file left may differ from the one sent: a jingle is
# seconds, a lossy file cut to its frames keeps hundredths.
SLACK_S = 0.1


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def syllables(path, seconds):
    """A mono WAV of voiced syllables with pauses, standard library only.

    Each syllable a pitch of its own with its overtones, faded in and
    out, so the loudness rises and falls the way speech does.
    """
    rate = 48000
    rng = random.Random(3)
    samples = [0.0] * int(seconds * rate)
    t = 0
    while t < len(samples) - rate:
        length = int(rng.uniform(0.3, 1.2) * rate)
        f0 = rng.uniform(90, 190)
        for k in range(length):
            fade = 0.5 - 0.5 * math.cos(2 * math.pi * k / length)
            w = 2 * math.pi * f0 * k / rate
            samples[t + k] = 0.3 * fade * sum(
                math.sin(h * w) / h for h in range(1, 7))
        t += length + int(rng.uniform(0.1, 0.8) * rate)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"".join(struct.pack("<h", int(32767 * max(-1.0, min(
            1.0, x)))) for x in samples))
    return path


def said(e):
    """An exception as one short line."""
    return " ".join(str(e).split())[:200]


vpm = ground.program()
key, origin = ground.the_key(vpm)
preset = ground.a_preset(vpm, key, multitrack=False)
folder = tempfile.mkdtemp(prefix="vpm_auphonic_live_")
title = ground.a_test_title("mono")
try:
    audio = syllables(os.path.join(folder, "syllables.wav"), SECONDS)

    print("1. Upload, start, wait and fetch, the way a run does")
    result, why = None, ""
    try:
        result = vpm.run_single_production(
            audio, preset, "the account's preset", key,
            os.path.join(folder, "back"), wait_s=900, title=title)
    except RuntimeError as e:
        why = said(e)
    check("the production comes back with a file",
          bool(result) and os.path.isfile(result),
          why or "the program returned %r"
          % (os.path.basename(result) if result else result,))

    print("\n2. What the program leaves")
    length = None
    if result and os.path.isfile(result):
        try:
            length = ground.measured(result)[0]
        except (OSError, ValueError) as e:
            why = said(e)
    check("the file the program leaves is as long as the one sent",
          length is not None and abs(length - SECONDS) <= SLACK_S,
          "%s s left against %d s sent, %.1f s allowed%s"
          % (length, SECONDS, SLACK_S,
             (" -- " + why) if length is None else ""))

    print("\n3. The production is taken away again")
    found, why = None, ""
    try:
        found = vpm.find_production_by_title(key, title)
    except RuntimeError as e:
        why = said(e)
    check("the production stands at auphonic.com under the title given",
          bool(found) and bool(found.get("uuid")),
          why or "%s under %s among the last 50"
          % ((found or {}).get("uuid") or "none", title))
    if found and found.get("uuid"):
        gone, why = False, ""
        try:
            gone = ground.delete(vpm, key, found["uuid"])
        except RuntimeError as e:
            why = said(e)
        check("the tests' own production can be deleted again", gone,
              why or "auphonic.com said %s to deleting %s"
              % ("yes" if gone else "no", found["uuid"]))
finally:
    shutil.rmtree(folder, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
