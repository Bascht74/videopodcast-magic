# -*- coding: utf-8 -*-
"""Three microphones, a known sound path, a known error -- is it found?"""
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
T = tempfile.mkdtemp(prefix="offset_")
rng = np.random.default_rng(7)

DURATION = 180.0
n = int(DURATION * SR)

def voice(seed):
    """Speech-like: noise in changing bands, chopped into syllables.

    A plain stack of overtones will not do -- that repeats every few
    milliseconds, and then any run-time measurement can be off by a
    whole period.
    """
    r = np.random.default_rng(seed)
    x = np.zeros(n); t = 0
    while t < n - SR:
        L = int(r.uniform(0.15, 0.45) * SR)
        raw = r.normal(size=L)
        X = np.fft.rfft(raw); f = np.fft.rfftfreq(L, 1.0/SR)
        low, high = r.uniform(150, 500), r.uniform(1500, 4000)
        X[(f < low) | (f > high)] = 0
        piece = np.fft.irfft(X, L)
        piece /= (np.abs(piece).max() or 1.0)
        x[t:t+L] += 0.5 * np.hanning(L) * piece
        t += L + int(r.uniform(0.02, 0.35) * SR)
    return x

# Who talks when: in turn, 20 s each
voices = [voice(11), voice(22), voice(33)]
mask = [np.zeros(n) for _ in range(3)]
for j in range(int(DURATION // 20)):
    i = j % 3
    mask[i][j*20*SR:(j+1)*20*SR] = 1.0
sources = [s * m for s, m in zip(voices, mask)]

# Sound paths in ms between the seats (symmetric)
PATH = {(0,1): 3.3, (0,2): 4.8, (1,2): 1.3}
# Error per track in ms (track 0 is the reference)
ERROR = [0.0, 18.0, -7.0]

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

tracks = []
for i in range(3):
    mic = sources[i].copy()                       # their own voice, direct
    for j in range(3):
        if j == i: continue
        path_ms = PATH[tuple(sorted((i, j)))]
        mic += 0.12 * shift(sources[j], path_ms)  # bleed, later
        for echo, g in ((15.0, 0.4), (29.0, 0.25)):
            mic += 0.12*g*shift(sources[j], path_ms+echo)
    mic += 0.0015 * rng.normal(size=n)
    mic = shift(mic, ERROR[i])                    # the built-in error
    file_path = os.path.join(T, "axis_%d.wav" % i)
    write(file_path, mic)
    tracks.append({"name": "Track%d" % i, "axis": file_path,
                   "source": file_path, "a": 0.0, "b": 1.0, "drift": False})

measured, lines = vpm.measure_offsets_by_crosstalk(tracks)
solution = {}
for (i, j) in ((0,1),(0,2),(1,2)):
    solution[(i, j)] = vpm.solve_pair_offsets(measured, i, j)
print("Sound paths, expected %s:" % PATH)
for (i, j) in ((0,1),(0,2),(1,2)):
    print("   %d<->%d  %+5.2f ms   (built in %.1f)"
          % (i, j, solution[(i,j)][0], PATH[(i,j)]))
print("\nOffset per track (reference track 0):")
for i in range(3):
    have = 0.0 if i == 0 else solution[(0, i)][1]
    want = ERROR[i]-ERROR[0]
    print("   Track%d  measured %+6.2f ms   built in %+6.2f  %s"
          % (i, have, want, "ok" if abs(have-want) < 1.0 else "OFF"))
    assert abs(have-want) < 1.0
print("\nOK: sound path and error cleanly told apart.")
