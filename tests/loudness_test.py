# -*- coding: utf-8 -*-
"""Loudness: does the range come along, and does it still normalise?"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys, subprocess, tempfile
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
T = tempfile.mkdtemp(prefix="loud_")

def track(file_path, expression):
    subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i",expression,
                    "-ac","1","-ar","48000","-c:a","pcm_s24le", file_path],
                   check=True)

# one at an even level and one with a changing level -> range measurable
track(os.path.join(T,"a.wav"), "sine=frequency=200:duration=30")
subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi",
                "-i","sine=frequency=300:duration=30",
                "-af","volume='if(lt(mod(t,10),5),1,0.15)':eval=frame",
                "-ac","1","-ar","48000","-c:a","pcm_s24le",
                os.path.join(T,"b.wav")], check=True)

error = []
def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

seen = {}
for n in ("a.wav","b.wav"):
    i, p, lra = vpm.measure_loudness(os.path.join(T,n))
    seen[n] = (i, p, lra)
    print("%-7s I=%.1f LUFS  Peak=%.1f dBTP  Range=%s LU" % (n, i, p, lra))

print("\n1. The measurement itself")
# The second file is the same tone, pulled down 16 dB half the time.
check("both are measured", all(v[0] is not None for v in seen.values()),
      str(seen))
# EBU R128 gates: material more than 10 LU under the ungated level does
# not count, so the quiet halves drop out and both files come to the
# same figure -- a pause must not make a recording seem quieter.
check("the gate keeps the quiet halves out of the integrated value",
      abs(seen["a.wav"][0] - seen["b.wav"][0]) < 1.0,
      "%.1f against %.1f" % (seen["a.wav"][0], seen["b.wav"][0]))
check("the peak sits above the integrated level and under zero",
      seen["a.wav"][0] < seen["a.wav"][1] < 0.5,
      "%.1f, peak %.1f" % (seen["a.wav"][0], seen["a.wav"][1]))
try:
    range_a, range_b = float(seen["a.wav"][2]), float(seen["b.wav"][2])
except (TypeError, ValueError):
    range_a = range_b = None
check("the steady one has almost no range",
      range_a is not None and range_a < 2.0, range_a)
check("but the range shows the difference plainly",
      range_b is not None and range_b > range_a + 8.0,
      "%.1f against %.1f LU" % (range_b, range_a))

print("\n2. Normalising to the target")
tracks = [{"ready": os.path.join(T,"a.wav"), "name":"A"},
          {"ready": os.path.join(T,"b.wav"), "name":"B"}]
v, curve = vpm.normalise_loudness(tracks, -16.0, T)
print("Gain: %+.2f dB, curve: %s" % (v, "yes" if curve else "none"))
# The sum of the tracks is brought to the target and every track gets
# the same gain, or the single tracks no longer add up to the mix.
mix = os.path.join(T, "mix.wav")
vpm.mix_tracks([t["ready"] for t in tracks], mix, v, curve)
after = vpm.measure_loudness(mix)[0]
check("the mix lands on the target", abs(after + 16.0) <= 0.6,
      "%.2f LUFS" % after)
check("the gain is the one that gets it there",
      abs(v) < 30.0 and v == v, "%+.2f dB" % v)

# Twice as loud a target means six decibels more gain, near enough.
harder, _c = vpm.normalise_loudness(tracks, -10.0, T)
check("a target six louder asks for about six more",
      abs((harder - v) - 6.0) < 0.5, "%+.2f against %+.2f" % (harder, v))

print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
