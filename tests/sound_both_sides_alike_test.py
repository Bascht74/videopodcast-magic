# -*- coding: utf-8 -*-
"""The two channel mix: same signal on both sides, and the right loudness.

The same material read as one channel comes out about three decibels
quieter, and nothing about the file says so; loudness is therefore
measured in the form the mix is delivered in. Both channels have to
carry the same signal, or the mix is a stereo image nobody asked for.

The source tracks; the shape of the two mixes; the two channels as one
signal; three decibels between one channel and two; normalising to the
target in the form delivered; the computed gain applied whole. Not in
it: a sine at this level needs no limiter, so normalising hands back no
curve and every mix here is built without one.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import subprocess, sys, tempfile, time
import numpy as np
vpm = the_program.load()
WORK = tempfile.mkdtemp(prefix="dualmono_")
TARGET = -16.0
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def lufs(v):
    return "not measurable" if v is None else "%.2f LUFS" % v


def decibel(v):
    return "not measurable" if v is None else "%+.2f dB" % v


def lu(v):
    return "not measurable" if v is None else "%+.2f LU" % v


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

print()
print("1. What the two source tracks are")
# The claims below rest on these two: a stereo source raises the channel
# count of every mix on its own, and tracks of different lengths make
# "as long as what went in" meaningless. So they are asked first, or the
# red line names a mix where the material was already wrong.
ch_a, ch_b = vpm.channel_count(a), vpm.channel_count(b)
check("each of the two source tracks has one channel",
      ch_a == 1 and ch_b == 1,
      "1 wanted, %d and %d found" % (ch_a, ch_b))
n_a, n_b = vpm.sample_count(a), vpm.sample_count(b)
check("the two source tracks are equally long", n_a == n_b,
      "%d samples against %d" % (n_a, n_b))

mono = vpm.mix_tracks([a, b], os.path.join(WORK, "mono.wav"))
stereo = vpm.mix_tracks([a, b], os.path.join(WORK, "stereo.wav"), channels=2)

print("\n2. The shape of the two mixes")
ch_mono, ch_stereo = vpm.channel_count(mono), vpm.channel_count(stereo)
check("one channel where one was asked for", ch_mono == 1,
      "1 asked for, %d in the file" % ch_mono)
check("two channels where two were asked for", ch_stereo == 2,
      "2 asked for, %d in the file" % ch_stereo)
n_mono, n_stereo = vpm.sample_count(mono), vpm.sample_count(stereo)
check("each mix is as long as the tracks that went into it",
      n_mono == n_a and n_stereo == n_a,
      "%d samples in, %d and %d out" % (n_a, n_mono, n_stereo))

print("\n3. The two channels are the same signal")
x = read(stereo)
# Not a check of its own: "two channels where two were asked for" above
# already says this, and a second judgement on it could only ever fall
# together with that one. It is the guard that keeps the line below from
# reaching for a channel that is not there.
wide = x.shape[1] == 2
apart = float(np.max(np.abs(x[:, 0] - x[:, 1]))) if wide else None
check("left minus right is nothing at all",
      apart is not None and apart < 1e-6,
      "%s against 1e-06 allowed"
      % ("%.3g" % apart if apart is not None else "only one channel"))
m = read(mono)
lined_up = m.shape[0] == x.shape[0]
carried = float(np.max(np.abs(x[:, 0] - m[:, 0]))) if lined_up else None
check("each side is the one channel mix, sample for sample",
      carried is not None and carried < 1e-6,
      "%s against 1e-06 allowed"
      % ("%.3g" % carried if carried is not None
         else "%d samples against %d" % (m.shape[0], x.shape[0])))

print("\n4. Two channels measure about three decibels louder")
one = vpm.measure_loudness(mono)[0]
two = vpm.measure_loudness(stereo)[0]
check("both mixes are measurable", one is not None and two is not None,
      "one channel %s, two channels %s" % (lufs(one), lufs(two)))
between = (two - one) if (one is not None and two is not None) else None
check("two channels measure 3.0 LU louder than one",
      between is not None and abs(between - 3.0) <= 0.15,
      "%s against +3.00 LU, allowed 0.15 out" % lu(between))

print("\n5. Normalising hits the target in the delivered form")
tracks = [{"ready": a, "name": "A"}, {"ready": b, "name": "B"}]
gain, curve = vpm.normalise_loudness(tracks, TARGET, WORK, channels=2)
from_two = (TARGET - two) if two is not None else None
from_one = (TARGET - one) if one is not None else None
check("the gain comes from the two channel sum, not from one channel",
      from_two is not None and abs(gain - from_two) <= 0.2,
      "%+.2f dB, wanted %s; from one channel it would be %s"
      % (gain, decibel(from_two), decibel(from_one)))
mix = vpm.mix_tracks([a, b], os.path.join(WORK, "done.wav"), gain, curve,
                     channels=2)
ch_mix = vpm.channel_count(mix)
check("the normalised mix has two channels", ch_mix == 2,
      "2 asked for, %d in the file" % ch_mix)
after = vpm.measure_loudness(mix)[0]
check("the normalised mix is measurable", after is not None,
      "%s, wanted a figure in LUFS" % lufs(after))
check("the normalised mix lands on -16 LUFS",
      after is not None and abs(after - TARGET) <= 0.3,
      "%s against %.2f LUFS, allowed 0.30 out" % (lufs(after), TARGET))
y = read(mix)
wide_mix = y.shape[1] == 2
sides = float(np.max(np.abs(y[:, 0] - y[:, 1]))) if wide_mix else None
check("the normalised mix still has one signal on both sides",
      sides is not None and sides < 1e-6,
      "%s against 1e-06 allowed"
      % ("%.3g" % sides if sides is not None else "only one channel"))

print("\n6. The gain is the gain that was computed")
raised = vpm.mix_tracks([a, b], os.path.join(WORK, "plain.wav"), gain,
                        None, channels=2)
lifted = vpm.measure_loudness(raised)[0]
check("the mix raised without a limiter is measurable", lifted is not None,
      "%s, wanted a figure in LUFS" % lufs(lifted))
risen = (lifted - two) if (lifted is not None and two is not None) else None
check("raising by the gain moves the sum by exactly that much",
      risen is not None and abs(risen - gain) <= 0.2,
      "%s risen against %+.2f dB of gain, allowed 0.20 out"
      % (lu(risen), gain))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
