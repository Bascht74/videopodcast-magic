# -*- coding: utf-8 -*-
"""Sound path and a track's own offset are told apart out of the bleed.

Three synthetic voices talk in turn into three microphones; each one
carries the others faintly and later -- the sound path between the
seats, with two echoes behind it -- and every track is then shifted by
an offset of its own. In order: that every pair came back measured in
both directions, the sound path of each pair, and the offset of each
track that has one. The material is built here, so both numbers are
known exactly, and the tolerances stay far under the echo: a
measurement that took an echo for the direct path falls.
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
T = tempfile.mkdtemp(prefix="offset_")
rng = np.random.default_rng(7)

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


DURATION = 180.0
n = int(DURATION * SR)

def voice(seed):
    """Speech-like: noise in changing bands, chopped into syllables.

    A stack of overtones repeats every few milliseconds, and a run-time
    measurement can then be off by a whole period.
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

PAIRS = ((0, 1), (0, 2), (1, 2))
# How far a measurement may sit from what was built in. Both stay far
# under the 15 ms echo, so a pair whose direct path was mistaken for an
# echo falls here.
PATH_ALLOWED = 0.30      # ms
OFFSET_ALLOWED = 1.00    # ms

measured, lines = vpm.measure_offsets_by_crosstalk(tracks)
for a, b, why in lines:
    print("  not measured  %-8s -> %-8s %s" % (a, b, why))
solution = {}
for (i, j) in PAIRS:
    solution[(i, j)] = vpm.solve_pair_offsets(measured, i, j)

# Before the numbers: a pair the measurement gave up on comes back as
# nothing at all, and every line below would then report a wrong path
# where in truth nothing was ever measured.
solved = sum(1 for pair in PAIRS if solution[pair] is not None)
check("every pair of microphones came back measured both ways",
      solved == 3,
      "%d of %d pairs solved, %d directions the measurement gave up on"
      % (solved, len(PAIRS), len(lines)))

for (i, j) in PAIRS:
    got = solution[(i, j)][0] if solution[(i, j)] else float("nan")
    check("the sound path between microphone %d and %d is found" % (i, j),
          abs(got - PATH[(i, j)]) <= PATH_ALLOWED,
          "%+.3f ms measured against %+.2f ms built in, %.2f ms allowed"
          % (got, PATH[(i, j)], PATH_ALLOWED))

# Track 0 is the reference, its offset is zero by definition, and a
# check on it could never fall. It is left out on purpose.
for i in (1, 2):
    have = solution[(0, i)][1] if solution[(0, i)] else float("nan")
    want = ERROR[i] - ERROR[0]
    check("the offset built into track %d is found" % i,
          abs(have - want) <= OFFSET_ALLOWED,
          "%+.2f ms measured against %+.2f ms built in, %.2f ms allowed"
          % (have, want, OFFSET_ALLOWED))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
