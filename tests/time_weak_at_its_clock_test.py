# -*- coding: utf-8 -*-
"""A file the sound did not place stands at its clock, not at what failed.

Two files do not fit: one whose sound has nothing in common with the
rest, and a camera that fits the sound recording and not the other
cameras. Both carry a clock, and the note beside each says it was
placed by its timecode. The axis held nothing for the first and the
failed measurement for the second, a hundred seconds from its clock.

Sections: both named as not fitting; each at its clock where the axis
hangs off one; the failed measurement casts no vote on where the axis
hangs; and in a relative axis a clock reading is not laid in at all.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import subprocess, sys, tempfile, time, wave
import numpy as np

vpm = the_program.load()

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
    n = int(seconds * RATE)
    x = np.zeros(n)
    t = 0.2
    while t < seconds - 1.0:
        long_s = float(rng.uniform(0.25, 0.9))
        k, i0 = int(long_s * RATE), int(t * RATE)
        shape = np.hanning(k) if k > 2 else 1.0
        x[i0:i0 + k] = rng.normal(0, 0.25, k) * shape
        t += long_s + float(rng.uniform(0.2, 1.1))
    return x


def write(path, x):
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())


# Its own folder under the run's TMPDIR, which the run throws away.
D = os.path.join(tempfile.mkdtemp(prefix="vpm_run_"), "weakclock")
os.makedirs(D)
room = turns(70, 1)
write(D + "/room.wav", room)
# The camera that fits the sound and not the other camera: the room
# under noise, so that it reads about 0.27 against both -- above the
# floor for a sound recording, below the one for a camera.
write(D + "/noisy.wav", 0.15 * room[:60 * RATE]
      + np.random.default_rng(9).normal(0, 0.05, 60 * RATE))
# And the one that fits nothing: a tone with no turns to align on.
t = np.arange(30 * RATE) / float(RATE)
write(D + "/foreign.wav", 0.3 * np.sin(2 * np.pi * 200 * t))
PICTURE = ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
           "-c:a", "pcm_s16le"]
# The clean camera is the longer of the two, so it is the one the
# other camera is held against.
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "smptebars=size=160x90:rate=25:duration=60",
                "-i", D + "/room.wav", "-i", D + "/noisy.wav",
                "-map", "0:v", "-map", "1:a", "-t", "60"] + PICTURE
               + [D + "/CamA.mov",
                  "-map", "0:v", "-map", "2:a", "-t", "58"] + PICTURE
               + [D + "/CamB.mov"], check=True)
ROOM, CAM_A, CAM_B = D + "/room.wav", D + "/CamA.mov", D + "/CamB.mov"
FOREIGN = D + "/foreign.wav"
FILES = [ROOM, CAM_A, CAM_B, FOREIGN]
KR, KB, KF = vpm.path_key(ROOM), vpm.path_key(CAM_B), vpm.path_key(FOREIGN)


def short(row):
    return sorted(os.path.basename(p) for p in (row or []))


def places(d):
    return dict((k.rsplit("/", 1)[-1], round(float(v), 3))
                for k, v in ((d or {}).get("axis") or {}).items())


#------------------------------------------- 1. Both named as not fitting

print("1. Two files that do not fit, each with a clock")
CLOCKS = {ROOM: 61200.0, CAM_A: 61200.0, CAM_B: 61300.0, FOREIGN: 61230.0}
data, text = vpm.measure_time_axis(FILES, tc_of=lambda p: CLOCKS.get(p))
print("   %s" % text)
print("   %s" % places(data))
check("both files are named as not fitting",
      short(data.get("weak")) == ["CamB.mov", "foreign.wav"],
      "weak: %s" % short(data.get("weak")))
check("and neither is refused, each having a clock the others share",
      short(data.get("no_place")) == [],
      "no place: %s" % short(data.get("no_place")))

#------------------------------------------------ 2. Each at its clock

print("\n2. Each stands at its clock")
axis = (data or {}).get("axis") or {}
check("a file whose sound fits nothing stands at its clock",
      KF in axis and abs(axis[KF] - 61230.0) < 1e-6,
      "foreign.wav at %s, wanted its clock's 61230.0"
      % (axis.get(KF),))
check("a camera that fits the sound and not the other cameras stands at "
      "its clock too",
      KB in axis and abs(axis[KB] - 61300.0) < 1e-6,
      "CamB.mov at %s, wanted its clock's 61300.0 and not the failed "
      "measurement near 61200" % (axis.get(KB),))

#----------------------------------------------------- 3. No vote

print("\n3. The failed measurement casts no vote on where the axis hangs")
# One honest clock and the weak camera's: the middle of two is the
# larger, and with the failed measurement voting the whole axis moved
# a hundred seconds to where nothing was found.
ONE = {ROOM: 61200.0, CAM_B: 61300.0}
data, _text = vpm.measure_time_axis(FILES, tc_of=lambda p: ONE.get(p))
print("   %s" % places(data))
axis = (data or {}).get("axis") or {}
check("the failed measurement casts no vote on where the axis hangs",
      KR in axis and abs(axis[KR] - 61200.0) < 0.01,
      "room.wav at %s, wanted its own clock's 61200.0" % (axis.get(KR),))

#---------------------------------------------- 4. A relative axis

print("\n4. In a relative axis a clock reading is not laid in")
# Clocks on the two weak files alone: nothing placed hangs off one, so
# the axis is relative and a reading of 61230 means nothing in it.
WEAK_ONLY = {CAM_B: 61300.0, FOREIGN: 61230.0}
data, _text = vpm.measure_time_axis(FILES, tc_of=lambda p: WEAK_ONLY.get(p))
print("   %s" % places(data))
axis = (data or {}).get("axis") or {}
check("in a relative axis a clock reading is not laid in",
      KF not in axis and axis.get(KB, 0.0) < 1000.0,
      "foreign.wav at %s and CamB.mov at %s, wanted no place and a "
      "relative one" % (axis.get(KF), axis.get(KB)))
check("and the axis does not claim to be tied to a clock",
      (data or {}).get("absolute") is False,
      "absolute is %s, wanted False" % ((data or {}).get("absolute"),))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
