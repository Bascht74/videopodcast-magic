# -*- coding: utf-8 -*-
"""Loudness: does the range come along, and does it still normalise?"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys, subprocess, tempfile, time
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

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))

def num(v):
    """A number for the log, and the word None where none came back."""
    return "%.1f" % v if isinstance(v, (int, float)) else str(v)

seen = {}
for n in ("a.wav","b.wav"):
    seen[n] = vpm.measure_loudness(os.path.join(T,n))
    print("%-7s I=%s LUFS  Peak=%s dBTP  Range=%s LU"
          % (n, num(seen[n][0]), num(seen[n][1]), seen[n][2]))

print("\n1. The measurement itself")
# The second file is the same tone, pulled down 16 dB half the time.
check("both are measured", all(v[0] is not None for v in seen.values()),
      str(seen))
if bad:
    # Nothing below can be measured without a measurement, so this way
    # out is taken -- and it goes past the closing lines like every
    # other, or the count would be missing exactly where it is needed.
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)
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
check("the gain stays in a plausible range", abs(v) < 30.0, "%+.2f dB" % v)

# Twice as loud a target means six decibels more gain, near enough.
harder, _c = vpm.normalise_loudness(tracks, -10.0, T)
check("a target six louder asks for about six more",
      abs((harder - v) - 6.0) < 0.5, "%+.2f against %+.2f" % (harder, v))

# ------------------------------------------- the same rule without a picture
# A run with no picture joins the blocks and stops. It measures and
# levels like any other: what one way can do, the other can. The target
# went missing here once, between two versions, because the path that
# used to carry it was taken out.
print("\n5. A run with no picture levels too")
import subprocess
D = os.path.join(T, "nopicture")
os.makedirs(D, exist_ok=True)
blocks = []
for i, seconds in enumerate((4, 4)):
    b = os.path.join(D, "Take_%02d.wav" % (i + 1))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "sine=frequency=%d:duration=%d" % (300 + 60 * i, seconds),
                    "-ac", "1", "-c:a", "pcm_s24le", b], check=True)
    blocks.append(b)


def joined_at(target):
    """Run with no picture and read back what the log said and wrote."""
    out = os.path.join(D, "out_%s" % (target or "none"))
    call = [sys.executable, SCRIPT, "--without-auphonic", "--out", out]
    if target is not None:
        call += ["--lufs", str(target)]
    p = subprocess.run(call + blocks, capture_output=True, text=True,
                       env=dict(os.environ, LANG="C", LC_ALL="C",
                                LANGUAGE="en", VPM_SILENT="1",
                                VPM_NO_UPDATE_CHECK="1"))
    made = [os.path.join(out, f) for f in sorted(os.listdir(out))
            if f.endswith(".wav")] if os.path.isdir(out) else []
    return (p.stdout or "") + (p.stderr or ""), made


said, made = joined_at(None)
check("it says what it measured", "Sum of tracks" in said,
      "" if "Sum of tracks" in said else said.strip().splitlines()[-1][:70])
check("and writes the joined file", len(made) == 1,
      str([os.path.basename(x) for x in made]))
plain = vpm.measure_loudness(made[0])[0] if made else None

said, made = joined_at(-16.0)
check("a target is applied, not only reported", "Target:" in said,
      "" if "Target:" in said else "no target line in the log")
if made and plain is not None:
    now = vpm.measure_loudness(made[0])[0]
    check("and the file really lands on it", abs(now + 16.0) <= 1.0,
          "%.2f LUFS, before %.2f" % (now, plain))
    # The clock has to survive the levelling, or the joined file cannot
    # be placed against anything afterwards.
    check("the joined file keeps its timecode where it had one",
          vpm.bext_time_reference(blocks[0]) is None
          or vpm.bext_time_reference(made[0]) is not None,
          "source %s, result %s" % (vpm.bext_time_reference(blocks[0]),
                                    vpm.bext_time_reference(made[0])))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
