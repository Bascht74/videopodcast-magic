# -*- coding: utf-8 -*-
"""The preview lays a file its sound hardly places where the run lays it.

A recording whose sound barely reaches the camera is laid by the run's
own measurement, never at its clock; a camera the recording does not
place and the other cameras do stands where they put it. Sections: a
weak recording where the run puts it, its clock ten seconds off, and
so beside a camera at its clock; the same with clocks on weak
recordings alone; one the run refuses, refused; the camera. What the
note says is window_note_names_way's.
"""
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import the_program
SCRIPT = the_program.SCRIPT
import subprocess, sys, tempfile, time, wave
import numpy as np

vpm = the_program.load()
vpm.set_language("en")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


#------------------------------------------------------------- Material

RATE = 48000
# The buried recording is the room from its 40th second, 30 dB under
# noise: the curves barely meet, and the phase finds it. Its clock
# says 50, ten seconds off. Both stand here as numbers.
TRUE_AT, CLOCK_AT = 40.0, 50.0


def turns(seconds, seed):
    """Speech-like turns: noise in irregular pieces with pauses between."""
    rng = np.random.default_rng(seed)
    n = int(seconds * RATE)
    x = np.zeros(n)
    t = 0.2
    while t < seconds - 1.0:
        long_s = float(rng.uniform(0.25, 0.9))
        k, i0 = int(long_s * RATE), int(t * RATE)
        x[i0:i0 + k] = rng.normal(0, 0.25, k) * np.hanning(k)
        t += long_s + float(rng.uniform(0.2, 1.1))
    return x


def write(path, x):
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())


PICTURE = ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
           "-c:a", "pcm_s16le"]


def cameras(folder, sounds, lengths):
    """One camera per sound, colour bars over it."""
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
           "smptebars=size=160x90:rate=25:duration=%d" % max(lengths)]
    for s in sounds:
        cmd += ["-i", s]
    for i, (s, n) in enumerate(zip(sounds, lengths)):
        cmd += ["-map", "0:v", "-map", "%d:a" % (i + 1), "-t", str(n)] \
            + PICTURE + [os.path.splitext(s)[0] + ".mov"]
    subprocess.run(cmd, check=True)
    return [os.path.splitext(s)[0] + ".mov" for s in sounds]


# Its own folder under the run's TMPDIR, which the run throws away.
D = tempfile.mkdtemp(prefix="vpm_weakrun_")
room = turns(130, 1)
write(D + "/Cam.wav", room[:120 * RATE])
CAM, = cameras(D, [D + "/Cam.wav"], [120])
BURIED, TONE, HISS = D + "/buried.wav", D + "/tone.wav", D + "/hiss.wav"
write(BURIED, 0.03 * room[40 * RATE:100 * RATE]
      + np.random.default_rng(3).normal(0, 0.05, 60 * RATE))
# A steady tone: nothing in common with the room, and the phase lays it
# somewhere all the same -- in the run as here.
t = np.arange(60 * RATE) / float(RATE)
write(TONE, 0.3 * np.sin(2 * np.pi * 200 * t))
# Faint hiss: no way of the run's places it.
write(HISS, np.random.default_rng(5).normal(0, 0.001, 60 * RATE))


def at(data, path, beside=CAM):
    """Where *path* stands from *beside*, or None where it is missing."""
    axis = (data or {}).get("axis") or {}
    k, c = vpm.path_key(path), vpm.path_key(beside)
    if k not in axis or c not in axis:
        return None
    return float(axis[k] - axis[c])


def where(value):
    return "missing" if value is None else "%+.3f s" % value


def named(data, key):
    return sorted(os.path.basename(p) for p in (data or {}).get(key) or ())


#------------------------------------------ 1. Where the run puts it

print("1. A weak recording, its clock ten seconds off")
a, b, st = vpm.align_audio_to_video(BURIED, CAM, sample_points=20,
                                    distance_s=30.0)
RUN = -a / b
print("   the run: %+.3f s%s" % (RUN, ", by phase" if st.get("from_phase")
                               else ""))
CLOCKS = {CAM: 1000.0, BURIED: 1000.0 + CLOCK_AT}
data, text = vpm.measure_time_axis([CAM, BURIED],
                                   tc_of=lambda p: CLOCKS.get(p))
print("   %s; weak %s" % (text, named(data, "weak")))
here = at(data, BURIED)
check("a weak recording stands where the run puts it, not at its clock",
      here is not None and abs(here - RUN) < 0.01,
      "preview %s, run %+.3f s, its clock %+.1f s, truth %+.1f s"
      % (where(here), RUN, CLOCK_AT, TRUE_AT))
# A longer recording with nothing in common is the reference now, so
# the camera fits nothing and stands at its clock -- and the run still
# measures the buried one against the camera.
LONG = D + "/long.wav"
write(LONG, turns(150, 99))
CLOCKS = {LONG: 1000.0, CAM: 1000.0, BURIED: 1000.0 + CLOCK_AT}
data, text = vpm.measure_time_axis([LONG, CAM, BURIED],
                                   tc_of=lambda p: CLOCKS.get(p))
print("   %s; weak %s" % (text, named(data, "weak")))
here = at(data, BURIED)
check("and beside a camera laid at its clock as well",
      here is not None and abs(here - RUN) < 0.01
      and "Cam.mov" in named(data, "weak"),
      "preview %s from the camera, run %+.3f s, its clock %+.1f s; weak %s"
      % (where(here), RUN, CLOCK_AT, named(data, "weak")))

#----------------------------------------- 2. With no clock to hang off

print("\n2. Clocks on the weak recordings alone")
# Nothing placed carries a clock, so the axis is relative -- and the
# recording still has the place the run gives it.
ONLY = {TONE: 1030.0, BURIED: 1000.0 + CLOCK_AT}
data, text = vpm.measure_time_axis([CAM, TONE, BURIED],
                                   tc_of=lambda p: ONLY.get(p))
print("   %s; no place %s" % (text, named(data, "no_place")))
here = at(data, BURIED)
check("and in an axis with no clock it still has a place",
      here is not None and abs(here - TRUE_AT) < 0.05
      and "buried.wav" not in named(data, "no_place"),
      "buried.wav at %s from the camera, wanted %+.1f s; no place %s"
      % (where(here), TRUE_AT, named(data, "no_place")))

#------------------------------------------------- 3. Refused as by the run

print("\n3. A recording the run refuses")
a, b, st = vpm.align_audio_to_video(HISS, CAM, sample_points=20,
                                    distance_s=30.0)
print("   the run: %s" % ("refused" if st.get("unplaceable") else
                          "placed at %+.3f s" % (-a / b)))
data, text = vpm.measure_time_axis([CAM, HISS])
print("   %s" % text)
check("a recording the run refuses is refused here too",
      st.get("unplaceable") and "hiss.wav" in named(data, "no_place"),
      "the run %s; no place %s, at %s"
      % ("refuses it" if st.get("unplaceable") else "places it",
         named(data, "no_place"), where(at(data, HISS))))

#------------------------------------------------------- 4. The camera

print("\n4. A camera the recording does not place and the cameras do")
# A microphone hearing one voice, and two cameras hearing a second
# sound it does not hold, the first faintly. The second camera starts
# five seconds into the first; against the microphone its few points
# scatter and would lay it far off.
voice, other = turns(80, 1), turns(80, 2)
write(D + "/mic.wav", voice + np.random.default_rng(4).normal(0, 0.002,
                                                              len(voice)))
write(D + "/CamA.wav", (0.3 * voice + other)[:60 * RATE])
write(D + "/CamB.wav", other[5 * RATE:55 * RATE])
CAM_A, CAM_B = cameras(D, [D + "/CamA.wav", D + "/CamB.wav"], [60, 50])
data, text = vpm.measure_time_axis([D + "/mic.wav", CAM_A, CAM_B])
print("   %s; weak %s" % (text, named(data, "weak")))
here = at(data, CAM_B, CAM_A)
check("a camera the other cameras place stands where they put it",
      here is not None and abs(here - 5.0) < 0.05
      and "CamB.mov" not in named(data, "weak"),
      "CamB.mov at %s from CamA.mov, wanted +5.0 s; weak %s"
      % (where(here), named(data, "weak")))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
