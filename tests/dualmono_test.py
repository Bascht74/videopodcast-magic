# -*- coding: utf-8 -*-
"""The two channel mix: same signal on both sides, and the right loudness.

A mix is delivered in two channels, and that is also the form its loudness
has to be measured in: the same material read as one channel comes out
about three decibels quieter. Measuring in one and delivering in two is
wrong by exactly that, every time, and nobody notices because the file
sounds fine.

Both channels have to carry the same signal, sample for sample. If they
did not, the mix would be a stereo image nobody asked for.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, json, subprocess, sys, tempfile
import numpy as np
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
WORK = tempfile.mkdtemp(prefix="dualmono_")
bad = []


def check(what, ok, detail=""):
    print("  %-54s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


def track(name, hz):
    path = os.path.join(WORK, name)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                    "-i", "sine=frequency=%d:duration=30" % hz,
                    "-af", "volume=0.3", "-ac", "1", "-ar", "48000",
                    "-c:a", "pcm_s24le", path], check=True)
    return path


def read(path):
    ch = vpm.channel_count(path)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le",
                          "-ac", str(ch), "-ar", "48000", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<f4").reshape(-1, ch)


a, b = track("a.wav", 220), track("b.wav", 330)
mono = vpm.mix_tracks([a, b], os.path.join(WORK, "mono.wav"))
stereo = vpm.mix_tracks([a, b], os.path.join(WORK, "stereo.wav"), channels=2)

print()
print("1. The shape of the two mixes")
check("one channel where one was asked for",
      vpm.channel_count(mono) == 1, str(vpm.channel_count(mono)))
check("two where two were asked for",
      vpm.channel_count(stereo) == 2, str(vpm.channel_count(stereo)))
check("both are the same length",
      vpm.sample_count(mono) == vpm.sample_count(stereo))

print("\n2. The two channels are the same signal")
x = read(stereo)
apart = float(np.max(np.abs(x[:, 0] - x[:, 1])))
check("left minus right is nothing at all", apart < 1e-6,
      "%.3g" % apart)

print("\n3. Two channels measure about three decibels louder")
one = vpm.measure_loudness(mono)[0]
two = vpm.measure_loudness(stereo)[0]
check("both are measurable", one is not None and two is not None)
check("the difference is +3.0 LU, give or take a tenth",
      abs((two - one) - 3.0) <= 0.15, "%+.2f LU" % (two - one))

print("\n4. Normalising hits the target in the delivered form")
tracks = [{"ready": a, "name": "A"}, {"ready": b, "name": "B"}]
gain, curve = vpm.normalise_loudness(tracks, -16.0, WORK, channels=2)
mix = vpm.mix_tracks([a, b], os.path.join(WORK, "done.wav"), gain, curve,
                     channels=2)
after = vpm.measure_loudness(mix)[0]
check("the mix has two channels", vpm.channel_count(mix) == 2)
check("and lands on -16 LUFS", abs(after + 16.0) <= 0.3,
      "%.2f LUFS" % after)
y = read(mix)
check("its two channels are still the same signal",
      float(np.max(np.abs(y[:, 0] - y[:, 1]))) < 1e-6)

print("\n5. The gain is the gain that was computed")
raised = vpm.mix_tracks([a, b], os.path.join(WORK, "plain.wav"), gain,
                        None, channels=2)
check("without the limiter the sum rises by exactly the gain",
      abs((vpm.measure_loudness(raised)[0] - two) - gain) <= 0.2,
      "%+.2f against %+.2f"
      % (vpm.measure_loudness(raised)[0] - two, gain))

print()
if bad:
    print("FAIL: %d of the checks" % len(bad))
    sys.exit(1)
print("All good.")
