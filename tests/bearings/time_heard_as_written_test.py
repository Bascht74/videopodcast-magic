# -*- coding: utf-8 -*-
"""The check hears a track off its recording as its file on the axis holds it.

Three microphones built here, each bleeding faintly into the other two,
the bleed of each pair at a known sound path. In order: the three laid
on the axis at places of their own, one with a drift taken out, and the
bleed measured once off the files written there and once off the
recordings at those places -- every pair, its offset and its drift; then
the same three shifted by a known amount and given no file at all, as a
dry run leaves them, and the check straightens them all the same. The
material is synthetic, so its bleed is cleaner than any room's.
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
import shutil
import struct
import tempfile
import time
import numpy as np
import the_program

began = time.time()
vpm = the_program.load()
vpm.set_language("en")
SR = vpm.SR
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


T = tempfile.mkdtemp(prefix="vpm_heard_")
DURATION = 200.0
n = int(DURATION * SR)


def voice(seed):
    """Speech-like bursts, band-limited, with pauses between them."""
    r = np.random.default_rng(seed)
    x = np.zeros(n)
    t = 0
    while t < n - SR:
        k = int(r.uniform(0.15, 0.45) * SR)
        spectrum = np.fft.rfft(r.normal(size=k))
        f = np.fft.rfftfreq(k, 1.0 / SR)
        spectrum[(f < r.uniform(150, 500)) | (f > r.uniform(1500, 4000))] = 0
        burst = np.fft.irfft(spectrum, k)
        burst /= (np.abs(burst).max() or 1.0)
        x[t:t + k] += 0.5 * np.hanning(k) * burst
        t += k + int(r.uniform(0.02, 0.35) * SR)
    return x


def shift(x, ms):
    """*x* later by *ms* milliseconds, the same length."""
    d = int(round(ms / 1000.0 * SR))
    y = np.zeros_like(x)
    if d >= 0:
        y[d:] = x[:len(x) - d]
    else:
        y[:d] = x[-d:]
    return y


def write(path, x):
    """A 16 bit mono WAV, its header written here."""
    data = (np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVE")
        f.write(b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, SR, SR * 2, 2,
                                      16))
        f.write(b"data" + struct.pack("<I", len(data)) + data)


rng = np.random.default_rng(5)
voices = [voice(11), voice(22), voice(33)]
speaking = []
for i in range(3):
    turn = np.zeros(n)
    for j in range(int(DURATION // 20)):
        if j % 3 == i:
            turn[j * 20 * SR:(j + 1) * 20 * SR] = 1.0
    speaking.append(voices[i] * turn)
PATH = {(0, 1): 3.3, (0, 2): 4.8, (1, 2): 1.3}
# How far each recording is put out in the last section, in ms.
ERROR = [0.0, 18.0, -7.0]
microphones = []
for i in range(3):
    mic = speaking[i].copy()
    for j in range(3):
        if j != i:
            w = PATH[tuple(sorted((i, j)))]
            mic += 0.12 * shift(speaking[j], w) + 0.05 * shift(speaking[j],
                                                               w + 17)
    microphones.append(mic + 0.0015 * rng.normal(size=n))

T0, T1 = 10.0, 190.0
WINDOW = (T0, T1)

# ------------------------------------------------- 1. file and recording
print("1. Off the files on the axis, and off the recordings at their place")
# Places of their own, a few milliseconds apart so the bleed still
# fits the search, and one track's drift taken out: each step of the
# way onto the axis has something to get wrong.
PLACES = [(0.0, 1.0, False), (0.004, 1.0, False), (-0.006, 1.0 + 20e-6, True)]
placed = []
for i, (a, b, drift) in enumerate(PLACES):
    source = os.path.join(T, "placed_%d.wav" % i)
    write(source, microphones[i])
    track = {"name": "Track%d" % i, "source": source, "a": a, "b": b,
             "drift": drift}
    track["axis"] = vpm.place_track_on_axis(
        source, os.path.join(T, "axis_%d.wav" % i), a, b, T0, T1, drift)
    placed.append(track)
off_files, _ = vpm.measure_offsets_by_crosstalk(placed)
off_places, _ = vpm.measure_offsets_by_crosstalk(placed, window=WINDOW)


def solved(measured):
    """Every pair's (offset ms, drift ppm), by its two numbers."""
    out = {}
    for i in range(3):
        for j in range(i + 1, 3):
            found = vpm.solve_pair_offsets(measured, i, j)
            if found:
                out["%d/%d" % (i, j)] = (found[1], found[2])
    return out


files, places = solved(off_files), solved(off_places)
print("   off the files:      " + ", ".join(
    "%s %+.3f ms %+.3f ppm" % (k, v[0], v[1]) for k, v in sorted(files.items())))
print("   off the recordings: " + ", ".join(
    "%s %+.3f ms %+.3f ppm" % (k, v[0], v[1]) for k, v in sorted(places.items())))
check("every pair heard off the files is heard off the recordings",
      len(files) == 3 and sorted(places) == sorted(files),
      "pairs off the files %s, off the recordings %s"
      % (sorted(files), sorted(places)))
both = [k for k in files if k in places]
apart_ms = max([abs(files[k][0] - places[k][0]) for k in both] or [0.0])
apart_ppm = max([abs(files[k][1] - places[k][1]) for k in both] or [0.0])
check("the recordings at their place show each pair's offset",
      bool(both) and apart_ms < 0.05,
      "%.3f ms apart at most against 0.050 ms, over %d pairs"
      % (apart_ms, len(both)))
check("and each pair's drift, the one taken out included",
      bool(both) and apart_ppm < 0.05,
      "%.3f ppm apart at most against 0.050 ppm, over %d pairs"
      % (apart_ppm, len(both)))

# --------------------------------------------------- 2. no file at all
print("\n2. No file on the axis, as a dry run leaves its tracks")
loose = []
for i in range(3):
    source = os.path.join(T, "loose_%d.wav" % i)
    write(source, shift(microphones[i], ERROR[i]))
    loose.append({"name": "Track%d" % i, "source": source, "a": 0.0,
                  "b": 1.0, "drift": False})
vpm.verify_alignment(loose, T0, T1)
left = solved(vpm.measure_offsets_by_crosstalk(loose, window=WINDOW)[0])
print("   left over: " + ", ".join(
    "%s %+.2f ms" % (k, v[0]) for k, v in sorted(left.items())))
furthest = max([abs(v[0]) for v in left.values()] or [0.0])
check("tracks with no file are straightened by the check all the same",
      len(left) == 3 and furthest < 1.5,
      "%d of 3 pairs measured, furthest apart %.2f ms against a limit of "
      "1.50 ms, %s ms put in" % (len(left), furthest, ERROR))

shutil.rmtree(T, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
