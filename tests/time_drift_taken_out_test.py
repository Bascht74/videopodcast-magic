# -*- coding: utf-8 -*-
"""A returned track that runs away has to be straightened again.

Built case: a known offset and a known clock drift, laid on speech-like
sound and stretched with ffmpeg. In order: the return is accepted as
matching the upload, a straightened file takes the place of the
returned one, and what is left of the offset and of the clock drift is
measured again by a second route.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, subprocess, sys, tempfile, time
import numpy as np

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def bytes_of(file_path):
    try:
        return os.path.getsize(file_path)
    except OSError:
        return -1


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
LIMIT_MS = 12.0       # this much offset may be left over
LIMIT_PPM = 15.0      # and this much clock drift

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
# Precondition on the material, not a judgement about the program:
# without a stretched file there is nothing here to straighten.
assert bytes_of(os.path.join(T, "done.wav")) > 44, "ffmpeg wrote no return"

track = {"name": "Probe", "axis": os.path.join(T, "axis.wav"),
         "done": os.path.join(T, "done.wav")}
accepted = vpm.verify_returned_tracks([track], WINDOW, T)

print("\nWhat the program measured: offset %s ms, clock drift %s ppm"
      % (track.get("offset_ms", "--"), track.get("drift_ppm", "--")))
spread = track.get("residual_ms")
check("the return is accepted as matching the upload", accepted is True,
      "the answer was %r, spread %s ms against the 150.0 ms above which "
      "a measurement counts as unusable"
      % (accepted, "--" if spread is None else "%.1f" % spread))
ready = track.get("ready") or ""
check("a straightened file takes the place of the returned one",
      bool(ready) and ready != track["done"] and os.path.exists(ready),
      "handed back %s of %d bytes, the return was %s of %d bytes"
      % (os.path.basename(ready) or "--", bytes_of(ready),
         os.path.basename(track["done"]), bytes_of(track["done"])))

# Measure again, by a second route: how well does the result sit on the
# axis? Where nothing was handed back, the return itself is measured --
# then the two lines below carry the numbers instead of a traceback.
came_back = ready or track["done"]


def env_curve(file_path):
    return vpm.envelope(vpm.decode_audio(file_path, rate=4000), 5.0, 4000)


a, b, _st = vpm.align_envelopes(env_curve(track["axis"]),
                                env_curve(came_back),
                                5.0, sample_points=40, distance_s=10.0,
                                points_off="audio")
check("the offset is out of the straightened track",
      abs(a * 1000) < LIMIT_MS,
      "%+.1f ms left against a limit of %.1f ms" % (a * 1000, LIMIT_MS))
check("the clock drift is out of the straightened track",
      abs((b - 1) * 1e6) < LIMIT_PPM,
      "%+.1f ppm left against a limit of %.1f ppm, from a built-in %+.1f ppm"
      % ((b - 1) * 1e6, LIMIT_PPM, DRIFT_PPM))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
