# -*- coding: utf-8 -*-
"""A returned track that runs away has to be straightened again.

Built case: a known offset and a known clock drift.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, subprocess, sys, tempfile
import numpy as np

spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
SR = vpm.SR
T = tempfile.mkdtemp(prefix="drift_")

def speech_like(duration, seed=3):
    rng = np.random.default_rng(seed)
    n = int(duration * SR)
    x = np.zeros(n)
    t = 0
    while t < n - SR:
        length = int(rng.uniform(0.3, 1.2) * SR)
        f0 = rng.uniform(90, 190)
        k = np.arange(length)
        piece = sum(np.sin(2*np.pi*f0*h*k/SR)/h for h in range(1, 12))
        env_curve = np.hanning(length)
        x[t:t+length] += 0.3 * piece * env_curve
        t += length + int(rng.uniform(0.05, 0.5) * SR)
    return x + 0.001 * rng.normal(size=n)

def write(file_path, x):
    d = np.clip(x, -1, 1)
    import struct
    b = (d * 32767).astype("<i2").tobytes()
    with open(file_path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 36+len(b)) + b"WAVE")
        f.write(b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, SR, SR*2, 2, 16))
        f.write(b"data" + struct.pack("<I", len(b)) + b)

WINDOW = 300.0
OFFSET = 40.0         # this far before our window the return starts
DRIFT_PPM = 200.0     # this much faster it runs

axis = speech_like(WINDOW)
write(os.path.join(T, "axis.wav"), axis)
# The "return": longer, 40 s more at the front, and stretched by DRIFT_PPM
long = speech_like(WINDOW + 2 * OFFSET)
long[int(OFFSET*SR):int(OFFSET*SR)+len(axis)] = axis
write(os.path.join(T, "long.wav"), long)
rate = int(round(SR / (1.0 + DRIFT_PPM * 1e-6)))
subprocess.run(["ffmpeg", "-v", "error", "-y",
                "-i", os.path.join(T, "long.wav"),
                "-af", "asetrate=%d,aresample=%d,asetrate=%d"
                % (SR, rate, SR),
                "-c:a", "pcm_s16le", os.path.join(T, "done.wav")],
               check=True)

track = {"name": "Probe", "axis": os.path.join(T, "axis.wav"),
         "done": os.path.join(T, "done.wav")}
ok = vpm.verify_returned_tracks([track], WINDOW, T)
print("\nThe return check says:", ok)
print("ready:", os.path.basename(track.get("ready", "--")))

# Measure again: how well does the result sit on the axis?
def env_curve(file_path):
    return vpm.envelope(vpm.decode_audio(file_path, rate=4000), 5.0, 4000)
a, b, st = vpm.align_envelopes(env_curve(track["axis"]),
                               env_curve(track["ready"]),
                               5.0, sample_points=40, distance_s=10.0,
                               points_off="audio")
print("\nLeft after the correction: offset %+.1f ms, clock drift %+.1f ppm"
      % (a * 1000, (b - 1) * 1e6))
assert abs(a * 1000) < 12 and abs((b - 1) * 1e6) < 15, "not straight enough"
print("OK -- offset and drift are out.")
