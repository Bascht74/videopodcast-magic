# -*- coding: utf-8 -*-
"""The limiter holds every peak at the ceiling and backs off where it must.

Two recordings of a quiet tone, normalised to -16 LUFS and mixed the way
a run does it. In the first, three short loud stretches stand four
decibels over the ceiling, under the most the limiter may take: it
takes them, the gain stays whole, and the mix peaks at the ceiling. In
the second, three clicks would need more than that bound: the gain
comes down until the limiter takes the bound exactly, and the ceiling
holds all the same. Ceiling and bound are read from the program. No peak stands in the first block of a file;
whether one there is held is the owner's question, and not asked here.
"""
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
import contextlib, io, re, subprocess, tempfile, time, wave
import numpy as np

began = time.time()
vpm = the_program.load()
vpm.set_language("en")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


D = tempfile.mkdtemp(prefix="vpm_peaks_")
RATE = 48000
t = np.arange(30 * RATE) / float(RATE)
TONE = 0.03 * np.sin(2 * np.pi * 300 * t)
# Loud stretches of a fifth of a second, well clear of the first block.
LOUD = TONE.copy()
for at in (1, 11, 21):
    a, b = int(at * RATE), int(at * RATE) + RATE // 5
    LOUD[a:b] = 0.3 * np.sin(2 * np.pi * 300 * t[a:b])
# Clicks of ten milliseconds at nearly full scale.
CLICKS = TONE.copy()
for at in (5, 15, 25):
    CLICKS[int(at * RATE):int(at * RATE) + 480] = 0.9


def write(name, x):
    """One mono 16-bit WAV in D; hands back its path."""
    path = os.path.join(D, name + ".wav")
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
    return path


def peak_db(path):
    """The highest sample of a file in dBFS, read by ffmpeg as floats."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le",
                          "-"], capture_output=True).stdout
    x = np.frombuffer(raw, "<f4")
    return 20 * np.log10(max(float(np.max(np.abs(x))), 1e-9)) if len(x) \
        else 0.0


def level(name, x):
    """Normalise and mix one recording: (gain, curve, printed, mix peak)."""
    path = write(name, x)
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        gain, curve = vpm.normalise_loudness(
            [{"name": "Host", "ready": path}], -16.0, D)
        mixed = vpm.mix_tracks([path], os.path.join(D, name + "_mix.wav"),
                               gain, curve)
    return gain, curve, said.getvalue(), peak_db(mixed)


def lead(template):
    """The fixed start of one of the program's sentences."""
    return vpm.T(template).split("%s")[0].strip()


LIMITER = lead('  Limiter:           at most %s dB, the same curve on '
               'every track%s')
TOO_MUCH = lead('  Too much:          the limiter would have to take %s '
                'dB away. More than %s dB\n                     sounds '
                'squashed -- %s dB less gain.')
SUM = lead('  Sum of tracks:     %s LUFS, peak %s dBTP%s')
CEILING, BOUND = vpm.CEILING_DBTP, vpm.LIMIT_MAX_DB
# A precondition of the material, not a judgement about the program: the
# loud stretches ask four decibels of the limiter, which must be allowed.
assert BOUND > 4.5, BOUND


def summed(said):
    """The loudness of the sum the program printed, or None."""
    found = re.search(re.escape(SUM) + r"\s*(-?\d+\.\d)", said)
    return float(found.group(1)) if found else None


print("1. Peaks four decibels over the ceiling")
gain, curve, said, top = level("loud", LOUD)
check("peaks over the ceiling get a limiter curve",
      curve is not None and LIMITER in said,
      "curve %s, %r %s" % ("made" if curve else "none", LIMITER,
                           "said" if LIMITER in said else "not said"))
check("the limited mix stays at the ceiling", top <= CEILING + 0.05,
      "mix peaks at %.2f dBFS against at most %.2f" % (top, CEILING + 0.05))
have = summed(said)
check("under the retreat bound the gain is not reduced",
      have is not None and abs(gain - (-16.0 - have)) <= 0.1
      and TOO_MUCH not in said,
      "gain %+.2f dB against %s for a sum at %s LUFS%s"
      % (gain, "%+.1f" % (-16.0 - have) if have is not None else "?",
         have, ", and the gain was cut" if TOO_MUCH in said else ""))

print("\n2. Clicks the limiter may not take alone")
gain, curve, said, top = level("clicks", CLICKS)
# By another route than the program's: the clicks stand at 0.9, and at
# the bound the limiter takes them from there down to the ceiling.
CLICK_DB = 20 * np.log10(0.9)
want = CEILING + BOUND - CLICK_DB
have = summed(said)
# A precondition of the material: with the whole gain the clicks would
# ask more of the limiter than the bound, or nothing here is asked.
assert have is None or -16.0 - have + CLICK_DB - CEILING > BOUND + 1, \
    (have, BOUND)
check("a limiter that would take more than its bound costs gain instead",
      TOO_MUCH in said and abs(gain - want) <= 0.3,
      "gain %+.2f dB against %+.2f +/- 0.3 for a bound of %.1f dB, %r %s"
      % (gain, want, BOUND, TOO_MUCH,
         "said" if TOO_MUCH in said else "not said"))
check("and the ceiling still holds", top <= CEILING + 0.05,
      "mix peaks at %.2f dBFS against at most %.2f" % (top, CEILING + 0.05))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
