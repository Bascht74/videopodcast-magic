# -*- coding: utf-8 -*-
"""The whole way: measure, place on the axis, measure again."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, struct, sys, tempfile
import numpy as np
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
SR = vpm.SR
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
for track in tracks:
    target = os.path.join(T, "axis_%s.wav" % track["name"])
    vpm.place_track_on_axis(track["source"], target, track["a"], track["b"],
                            T0, T1, False)
    track["axis"] = target; track["drift"] = False

vpm.verify_alignment(tracks, T0, T1)
measured, _ = vpm.measure_offsets_by_crosstalk(tracks)
remaining = {}
for i in range(len(tracks)):
    for j in range(i+1, len(tracks)):
        f = vpm.solve_pair_offsets(measured, i, j)
        if f: remaining["%d/%d" % (i, j)] = (round(f[1], 2), round(f[2], 2))
print("\nAt the end (offset ms, drift ppm):", remaining)
assert all(abs(v[0]) < 1.5 for v in remaining.values()), "not straight"
print("OK: all tracks sit together to better than 1.5 ms.")
