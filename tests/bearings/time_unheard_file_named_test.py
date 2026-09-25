# -*- coding: utf-8 -*-
"""A file the axis cannot hear is named as not fitting, never left out.

A camera with no sound track gives no curve to measure. It is named as
the run names it: among the files that do not fit, among those offered
for leaving out, counted in the line under the axis, and placed by its
clock where one places it and by nothing where none does. A file whose
measurement fails is named the same way.

Sections: a camera with no sound and no clock; the same camera with a
clock; beside a single file with sound; a measurement that fails.
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


def turns(seconds, seed):
    """Speech-like turns: noise in irregular pieces with pauses between."""
    rng = np.random.default_rng(seed)
    x = np.zeros(int(seconds * RATE))
    t = 0.2
    while t < seconds - 1.0:
        long_s = float(rng.uniform(0.25, 0.9))
        k, i0 = int(long_s * RATE), int(t * RATE)
        x[i0:i0 + k] = rng.normal(0, 0.25, k) * np.hanning(k)
        t += long_s + float(rng.uniform(0.2, 1.1))
    return x


D = os.path.join(tempfile.mkdtemp(prefix="vpm_run_"), "unheard")
os.makedirs(D)
ROOM, CAM, MUTE = D + "/room.wav", D + "/CamA.mov", D + "/Mute.mov"
with wave.open(ROOM, "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(RATE)
    f.writeframes((np.clip(turns(70, 1), -1, 1) * 32000)
                  .astype("<i2").tobytes())
PICTURE = ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p"]
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "smptebars=size=160x90:rate=25:duration=60", "-i", ROOM,
                "-map", "0:v", "-map", "1:a", "-t", "60"] + PICTURE
               + ["-c:a", "pcm_s16le", CAM,
                  "-map", "0:v", "-an", "-t", "50"] + PICTURE + [MUTE],
               check=True)
KM, KC = vpm.path_key(MUTE), vpm.path_key(CAM)
ONE_OUT = vpm.TN(1, ', %s file does not fit',
                 ', %s files do not fit') % vpm.number_text(1, 0)


def short(row):
    """The file names of a row, without their folders, sorted."""
    return sorted(os.path.basename(p) for p in (row or []))


#--------------------------------------- 1. No sound, and no clock

print("1. A camera with no sound track and no clock")
data, text = vpm.measure_time_axis([ROOM, CAM, MUTE])
print("   %s" % text)
check("a camera with no sound is named as not fitting",
      short((data or {}).get("weak")) == ["Mute.mov"],
      "weak: %s, wanted ['Mute.mov']" % short((data or {}).get("weak")))
check("and as placed by nothing, having no clock",
      short((data or {}).get("no_place")) == ["Mute.mov"],
      "no place: %s, wanted ['Mute.mov']"
      % short((data or {}).get("no_place")))
check("and as under every floor, so it is proposed to be left out",
      short((data or {}).get("unplaceable")) == ["Mute.mov"],
      "unplaceable: %s, wanted ['Mute.mov']"
      % short((data or {}).get("unplaceable")))
check("the line under the axis counts it",
      ONE_OUT in text, "%r, wanted it to hold %r" % (text, ONE_OUT))

#----------------------------------------------- 2. With a clock

print("\n2. The same camera, with a clock the others share")
CLOCKS = {ROOM: 61200.0, CAM: 61200.0, MUTE: 61210.0}
data, text = vpm.measure_time_axis([ROOM, CAM, MUTE],
                                   tc_of=lambda p: CLOCKS.get(p))
print("   %s" % text)
axis = (data or {}).get("axis") or {}
check("a camera with no sound stands at its clock",
      KM in axis and abs(axis[KM] - 61210.0) < 1e-6,
      "Mute.mov at %s, wanted its clock's 61210.0" % (axis.get(KM),))
check("and is not named as placed by nothing",
      short((data or {}).get("no_place")) == [],
      "no place: %s, wanted none" % short((data or {}).get("no_place")))

#------------------------------------- 3. Beside a single file with sound

print("\n3. Two files, one of them with no sound")
data, text = vpm.measure_time_axis([ROOM, MUTE])
print("   %s" % text)
check("beside a single file with sound it is still named",
      short((data or {}).get("weak")) == ["Mute.mov"],
      "weak: %s, wanted ['Mute.mov'] -- text %r"
      % (short((data or {}).get("weak")), text))

#----------------------------------------- 4. A measurement that fails

print("\n4. A measurement that fails outright")
# A stand-in: the one way this is reached with real material is a
# failure inside the arithmetic, which no file here can be made to cause.
real = vpm.bearings.align_envelopes


def refusing(env_a, env_b, *args, **named):
    """The real alignment, but it raises for the pair warned as CamA.mov."""
    if named.get("warn") == "CamA.mov":
        raise RuntimeError("stand-in: this pair cannot be measured")
    return real(env_a, env_b, *args, **named)


vpm.bearings.align_envelopes = refusing
try:
    data, text = vpm.measure_time_axis([ROOM, CAM])
finally:
    vpm.bearings.align_envelopes = real
print("   %s" % text)
check("a file whose measurement fails is named, not left out",
      short((data or {}).get("weak")) == ["CamA.mov"],
      "weak: %s, wanted ['CamA.mov'] -- text %r"
      % (short((data or {}).get("weak")), text))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
