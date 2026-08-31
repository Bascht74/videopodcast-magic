# -*- coding: utf-8 -*-
"""One pair of microphones, or two of them?

Sound needs three milliseconds to travel a metre: one pair hears everything
at the same moment, two clip-on microphones on two people hear each other
late. The delay is built in on purpose, so the answer is known beforehand.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, shutil, struct, sys, tempfile, time, wave
import numpy as np
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))

RATE = 48000
SEC = 12
folder = tempfile.mkdtemp(prefix="vpm_delay_")


def voice(seed, low, high):
    """Filtered noise with a speech-like on and off."""
    r = np.random.default_rng(seed)
    n = SEC * RATE
    x = r.standard_normal(n)
    f = np.fft.rfftfreq(n, 1.0 / RATE)
    X = np.fft.rfft(x)
    X[(f < low) | (f > high)] = 0
    x = np.fft.irfft(X, n)
    env = np.zeros(n)
    t = 0
    while t < n:
        on = int(r.uniform(0.5, 1.5) * RATE)
        off = int(r.uniform(0.2, 0.8) * RATE)
        env[t:t + on] = 1.0
        t += on + off
    k = np.hanning(int(0.05 * RATE))
    env = np.convolve(env, k / k.sum(), mode="same")
    x = x * env
    return x / (np.abs(x).max() + 1e-9)


def later(x, ms):
    n = int(round(ms * RATE / 1000.0))
    return np.concatenate((np.zeros(n), x))[:len(x)] if n > 0 else x.copy()


def build(name, left, right):
    path = os.path.join(folder, name)
    n = min(len(left), len(right))
    both = np.empty(2 * n)
    both[0::2] = left[:n]
    both[1::2] = right[:n]
    both = both / max(1e-9, np.abs(both).max()) * 0.7
    with wave.open(path, "wb") as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes(np.clip(both * 32767, -32768, 32767)
                      .astype("<i2").tobytes())
    return path


def verdict(path):
    facts = vpm.channel_facts(path)
    pairs = vpm.channel_joins(facts)
    _k, stereo, sure, why = pairs[0]
    zero = (facts.get("pair_zero") or [None])[0]
    apart = (facts.get("pair_apart") or [None])[0]
    return stereo, sure, why, zero, apart


a = voice(11, 120, 5000)
b = voice(12, 150, 5500)
quiet = 10 ** (-12.0 / 20.0)

print("1. One pair of microphones, everything arriving together")
for name, ms in (("coincident", 0.0), ("17 cm apart", 0.5),
                 ("30 cm apart", 0.87)):
    path = build("pair_%s.wav" % ms, a + later(0.7 * b, ms),
                 later(0.7 * a, ms) + b)
    stereo, sure, why, zero, _apart = verdict(path)
    check("%-14s is read as one pair" % name, stereo and sure,
          "%s (%.2f)" % (why[:44], zero or 0))

print("\n2. Two microphones, each hearing the other late")
for name, ms, metres in (("0.6 m", 1.2, 0.4), ("1.2 m", 2.9, 1.0),
                         ("2.0 m", 5.2, 1.8)):
    path = build("lavs_%s.wav" % ms, a + quiet * later(b, ms),
                 b + quiet * later(a, ms))
    stereo, sure, why, zero, apart = verdict(path)
    check("%-14s is read as two microphones" % name,
          (not stereo) and sure, "%s (%.2f)" % (why[:44], zero or 0))
    check("   and the distance is about right",
          apart is not None and abs(apart * 0.343 - metres) < 0.25,
          "measured %.2f m" % ((apart or 0) * 0.343))

print("\n3. Even a whisper of bleed is enough")
path = build("faint.wav", a + 10 ** (-26.0 / 20.0) * later(b, 2.9),
             b + 10 ** (-26.0 / 20.0) * later(a, 2.9))
stereo, sure, why, zero, apart = verdict(path)
check("bleed 26 dB down still shows the delay", (not stereo) and sure,
      "%s (%.2f)" % (why[:44], zero or 0))

print("\n4. What cannot be measured is not claimed")
path = build("apart.wav", a, b)          # two channels sharing nothing
stereo, sure, why, zero, _apart = verdict(path)
check("channels sharing nothing: no verdict", not sure, why[:60])
check("and the split is what is proposed", not stereo)

path = build("same.wav", a + b, 0.6 * (a + b))
stereo, sure, why, zero, _apart = verdict(path)
check("mono panned to both sides stays one track", stereo and sure,
      why[:60])

print("\n5. Silence does not become a speaker")
path = build("half.wav", a, np.zeros(len(a)))
stereo, sure, why, zero, _apart = verdict(path)
check("an empty channel is seen as empty", (not stereo) and sure,
      why[:60])

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
