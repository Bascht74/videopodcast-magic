# -*- coding: utf-8 -*-
"""Tracks put on the axis sit together, whatever offset they came with.

Three microphones are built with the other two bleeding faintly into
them, each shifted by a known amount, and the program runs its whole
way over them: measure the crosstalk, place on the axis, measure again.
In order: the window every track lands in, whether every pair is still
measurable at the end, the offset left between them, and the clock
drift left. The material is synthetic, so its bleed is cleaner than any
room's and the numbers come out sharper than a recording would give.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import importlib.util, struct, sys, tempfile, time
import numpy as np
began = time.time()
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
SR = vpm.SR
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def wav_seconds(file_path):
    """How long a WAV runs, out of its own chunks; 0.0 if there is none.

    The program asks ffprobe. This walks the header itself, so the
    answer does not come back by the road it is meant to judge.
    """
    if not os.path.exists(file_path):
        return 0.0
    with open(file_path, "rb") as wav:
        head = wav.read(12)
        if head[:4] != b"RIFF" or head[8:12] != b"WAVE":
            return 0.0
        rate = channels = width = 0
        while True:
            header = wav.read(8)
            if len(header) < 8:
                return 0.0
            name, size = header[:4], struct.unpack("<I", header[4:])[0]
            if name == b"fmt ":
                fmt = wav.read(size + (size & 1))
                channels = struct.unpack("<H", fmt[2:4])[0]
                rate = struct.unpack("<I", fmt[4:8])[0]
                width = struct.unpack("<H", fmt[14:16])[0] // 8
            elif name == b"data":
                if not (rate and channels and width):
                    return 0.0
                return size / float(rate * channels * width)
            else:
                wav.seek(size + (size & 1), 1)


T = tempfile.mkdtemp(prefix="onaxis_")
rng = np.random.default_rng(5)
DURATION = 200.0; n = int(DURATION * SR)

def voice(seed):
    r = np.random.default_rng(seed); x = np.zeros(n); t = 0
    while t < n - SR:
        L = int(r.uniform(0.15, 0.45) * SR)
        X = np.fft.rfft(r.normal(size=L)); f = np.fft.rfftfreq(L, 1.0/SR)
        X[(f < r.uniform(150, 500)) | (f > r.uniform(1500, 4000))] = 0
        st = np.fft.irfft(X, L); st /= (np.abs(st).max() or 1.0)
        x[t:t+L] += 0.5 * np.hanning(L) * st
        t += L + int(r.uniform(0.02, 0.35) * SR)
    return x

def shift(x, ms):
    d = int(round(ms/1000.0*SR)); y = np.zeros_like(x)
    if d >= 0: y[d:] = x[:len(x)-d]
    elif d < 0: y[:d] = x[-d:]
    return y

def write(file_path, x):
    b = (np.clip(x, -1, 1)*32767).astype("<i2").tobytes()
    with open(file_path, "wb") as f:
        f.write(b"RIFF"+struct.pack("<I", 36+len(b))+b"WAVE")
        f.write(b"fmt "+struct.pack("<IHHIIHH", 16, 1, 1, SR, SR*2, 2, 16))
        f.write(b"data"+struct.pack("<I", len(b))+b)

voices = [voice(11), voice(22), voice(33)]
sources = []
for i in range(3):
    m = np.zeros(n)
    for j in range(int(DURATION // 20)):
        if j % 3 == i: m[j*20*SR:(j+1)*20*SR] = 1.0
    sources.append(voices[i]*m)
PATH = {(0,1): 3.3, (0,2): 4.8, (1,2): 1.3}
ERROR = [0.0, 18.0, -7.0]        # this far off is where the sources sit
tracks = []
for i in range(3):
    mic = sources[i].copy()
    for j in range(3):
        if j == i: continue
        w = PATH[tuple(sorted((i, j)))]
        mic += 0.12*shift(sources[j], w) + 0.05*shift(sources[j], w+17)
    mic += 0.0015*rng.normal(size=n)
    source = os.path.join(T, "source_%d.wav" % i)
    write(source, shift(mic, ERROR[i]))
    tracks.append({"name": "Track%d" % i, "source": source,
                   "a": 0.0, "b": 1.0})

T0, T1 = 10.0, 190.0
WINDOW = 180.0                   # what T1 - T0 has to come to, as a value
for track in tracks:
    target = os.path.join(T, "axis_%s.wav" % track["name"])
    vpm.place_track_on_axis(track["source"], target, track["a"], track["b"],
                            T0, T1, False)
    track["axis"] = target; track["drift"] = False

lengths = [wav_seconds(track["axis"]) for track in tracks]
check("every track lands on the axis as a file of the full window",
      max(abs(seconds - WINDOW) for seconds in lengths) <= 0.01,
      "shortest %.2f s, longest %.2f s against a window of %.2f s"
      % (min(lengths), max(lengths), WINDOW))

vpm.verify_alignment(tracks, T0, T1)
measured, _ = vpm.measure_offsets_by_crosstalk(tracks)
remaining = {}
for i in range(len(tracks)):
    for j in range(i+1, len(tracks)):
        found = vpm.solve_pair_offsets(measured, i, j)
        if found: remaining["%d/%d" % (i, j)] = (found[1], found[2])
print("\nAt the end: " + ", ".join("%s %+.2f ms %+.2f ppm" % (pair, v[0], v[1])
                                   for pair, v in sorted(remaining.items())))

check("every pair can still be measured against the bleed",
      len(remaining) == 3,
      "%d of 3 pairs came back with a number" % len(remaining))
offsets = [abs(v[0]) for v in remaining.values()] or [0.0]
check("no pair is left further apart than the limit allows",
      max(offsets) < 1.5,
      "furthest apart %.2f ms against a limit of 1.50 ms, over %d pairs"
      % (max(offsets), len(remaining)))
drifts = [abs(v[1]) for v in remaining.values()] or [0.0]
check("no clock drift is left running between two tracks",
      max(drifts) < 0.5,
      "largest drift left %.2f ppm against a limit of 0.50 ppm, over %d pairs"
      % (max(drifts), len(remaining)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
