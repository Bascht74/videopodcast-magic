# -*- coding: utf-8 -*-
"""What the run's sound places, the window never names as not fitting.

The run's verdict is read off its own functions first, then what the
window names. Sections: beside a camera, one the phase places and one
the loudness curve placed at a match of 0.10; beside a camera with a
hum, one the bands that move place; without a picture, the phase's one
against the longest. In each a recording no way places is named, so an
axis naming nothing fails. The limit: no material built here gets the
curve that low, so that measurement is handed over as the run keeps it.
"""
PLATFORM_BOUND = True
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import contextlib
import io
import subprocess
import tempfile
import time
import wave
import numpy as np
import the_program

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


def write(path, x):
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())


# Its own folder under the run's TMPDIR, which the run throws away.
D = tempfile.mkdtemp(prefix="vpm_placedfits_")
ROOM, BURIED, HISS = D + "/room.wav", D + "/buried.wav", D + "/hiss.wav"
LOW, GUEST = D + "/low.wav", D + "/guest.wav"
room = turns(130, 1)
write(ROOM, room)
write(D + "/cam.wav", room[:120 * RATE])
# The room from its 40th second, 30 dB under noise: the curves barely
# meet, and on mixed sound the phase finds it.
write(BURIED, 0.03 * room[40 * RATE:100 * RATE]
      + np.random.default_rng(3).normal(0, 0.05, 60 * RATE))
# Faint hiss: no way of the run's places it.
write(HISS, np.random.default_rng(5).normal(0, 0.001, 60 * RATE))
# Any sound with a curve: its measurement is handed over below.
write(LOW, turns(60, 4))
# A guest far under a 100 Hz hum 40 dB over it on the camera, the
# camera forty seconds of the guest from its fourth: the plain curve
# misses it and the bands that move place it.
guest = turns(60, 11) + np.random.default_rng(9).normal(0, 0.0004,
                                                        60 * RATE)
guest *= 0.8 / np.sqrt(2.0) / 10 ** 2.0 / float(np.sqrt((guest ** 2).mean()))
write(GUEST, guest)
heard = guest[4 * RATE:44 * RATE].copy()
write(D + "/hum.wav", heard + 0.8 * np.sin(
    2 * np.pi * 100.0 * np.arange(len(heard)) / float(RATE)))
PICTURE = ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
           "-c:a", "pcm_s16le"]
CAM, HUM_CAM = D + "/Cam.mov", D + "/HumCam.mov"
subprocess.run(
    ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
     "smptebars=size=160x90:rate=25:duration=120",
     "-i", D + "/cam.wav", "-i", D + "/hum.wav",
     "-map", "0:v", "-map", "1:a", "-t", "120"] + PICTURE + [CAM,
     "-map", "0:v", "-map", "2:a", "-t", "40"] + PICTURE + [HUM_CAM],
    check=True)


def mixed(path):
    """The phase way on, as for a recording somebody marked Mixed."""
    return True


def speech(path):
    """The phase way off, as for every recording nobody marked Mixed."""
    return False


def the_run(path, reference, length, phase):
    """What the run's sound_places says of *path*, in a few words."""
    with contextlib.redirect_stdout(io.StringIO()):
        got = vpm.sound_places(os.path.basename(path), path, reference,
                               length, phase)
    if not got:
        return "no measurement"
    st = got[2]
    return ("refused" if st.get("unplaceable") else "by the bands"
            if st.get("from_bands") else "by its phase"
            if st.get("from_phase") else "by its curve")


def named(data):
    """The files the window names as not fitting, without folders."""
    return sorted(os.path.basename(p) for p in (data or {}).get("weak") or ())


#------------------------------------------------- 1. Beside a camera

print("1. Beside a camera: the phase, and the curve at 0.10")
said = the_run(BURIED, CAM, 120.0, True)
print("   the run: buried.wav %s, hiss.wav %s"
      % (said, the_run(HISS, CAM, 120.0, True)))
check("the run places the buried recording by its phase, beside a camera",
      said == "by its phase", "the run: %s" % said)
# The run's plain way at a match of 0.10: twelve points on one line,
# spread 4 ms, no drift -- a placing sound_places_recording accepts.
KEPT = {"quality": 0.10, "points": 12, "candidates": 20, "spread_ms": 4.0,
        "ppm": 0.0, "ppm_error": 1.0}
print("   the run's plain way takes the handed-over measurement: %s"
      % vpm.sound_places_recording(KEPT))
raw = {"recordings": {vpm.path_key(LOW): [-20.0, 1.0, dict(KEPT)]}}
with contextlib.redirect_stdout(io.StringIO()):
    data, text = vpm.measure_time_axis([CAM, BURIED, LOW, HISS],
                                       phase_of=mixed, raw=raw)
print("   %s; named %s" % (text, named(data)))
check("a recording the phase placed is not named as not fitting",
      "buried.wav" not in named(data) and "hiss.wav" in named(data),
      "named %s, wanted hiss.wav and not buried.wav" % named(data))
check("nor one the curve placed at a match of 0.10",
      "low.wav" not in named(data) and "hiss.wav" in named(data),
      "named %s at a match of %.2f, wanted hiss.wav and not low.wav"
      % (named(data), KEPT["quality"]))

#--------------------------------------------- 2. Beside a humming camera

print("\n2. Beside a camera with a hum: the bands that move")
said = the_run(GUEST, HUM_CAM, 40.0, False)
print("   the run: guest.wav %s, hiss.wav %s"
      % (said, the_run(HISS, HUM_CAM, 40.0, False)))
check("the run places the guest recording on the bands that move",
      said == "by the bands", "the run: %s" % said)
with contextlib.redirect_stdout(io.StringIO()):
    data, text = vpm.measure_time_axis([HUM_CAM, GUEST, HISS],
                                       phase_of=speech)
print("   %s; named %s" % (text, named(data)))
check("a recording the bands placed is not named as not fitting",
      "guest.wav" not in named(data) and "hiss.wav" in named(data),
      "named %s, wanted hiss.wav and not guest.wav" % named(data))

#------------------------------------------------- 3. Without a picture

print("\n3. Without a picture: the phase against the longest recording")
said = the_run(BURIED, ROOM, 130.0, True)
print("   the run: buried.wav %s, hiss.wav %s"
      % (said, the_run(HISS, ROOM, 130.0, True)))
check("without a picture the run places the buried recording by phase",
      said == "by its phase", "the run: %s" % said)
with contextlib.redirect_stdout(io.StringIO()):
    data, text = vpm.measure_time_axis([ROOM, BURIED, HISS],
                                       phase_of=mixed)
print("   %s; named %s" % (text, named(data)))
check("without a picture a recording the phase placed is not named",
      "buried.wav" not in named(data) and "hiss.wav" in named(data),
      "named %s, wanted hiss.wav and not buried.wav" % named(data))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
