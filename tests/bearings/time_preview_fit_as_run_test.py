# -*- coding: utf-8 -*-
"""The preview places a camera its fit alone places, where the run does.

Two cameras made here, each hearing its own speaker loud and the other
28 dB down, so their correlation stays under the camera floor while the
sample points all lie on one line; neither carries a timecode.
Sections: what the run makes of the pair, and what the preview's axis
makes of it -- placed by its sound, not named as fitting nothing, and
at the run's place. The pair is synthetic, and one length is asked:
14 minutes, where the run's density reaches the fit's count and a
point every two minutes does not.
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
import the_program
import contextlib
import io
import subprocess
import tempfile
import time
import wave
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

RATE = 16000
LENGTH = 840.0
# The second camera starts this much later in the first one's time.
LATE = 5.0
# How far down each camera hears the speaker it is not pointed at.
ACROSS_DB = 28.0
FRAME = 1.0 / 25


def bursts(seconds, seed):
    """Speech-like turns: noise in irregular pieces with pauses between."""
    rng = np.random.default_rng(seed)
    n = int(seconds * RATE)
    x = np.zeros(n)
    t = 0.2
    while t < seconds - 1.0:
        long_s = float(rng.uniform(0.25, 0.9))
        k, i0 = int(long_s * RATE), int(t * RATE)
        x[i0:i0 + k] = (rng.normal(0, float(rng.uniform(0.08, 0.3)), k)
                        * np.hanning(k))
        t += long_s + float(rng.uniform(0.2, 1.1))
    return x + rng.normal(0, 0.0004, n)


def write(path, x):
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())


# Two speakers taking turns of 4 to 25 seconds; each camera hears one.
first, second = bursts(LENGTH, 1), bursts(LENGTH, 501)
rng = np.random.default_rng(78)
gate = np.zeros(len(first))
t, who = 0.0, 0
while t < LENGTH:
    d = float(rng.uniform(4, 25))
    gate[int(t * RATE):int(min(LENGTH, t + d) * RATE)] = who
    who, t = 1 - who, t + d
first, second = first * (1 - gate), second * gate
across = 10 ** (-ACROSS_DB / 20.0)

# Its own folder under the run's TMPDIR, which the run throws away.
D = tempfile.mkdtemp(prefix="vpm_previewfit_")
write(os.path.join(D, "guest.wav"), first + second * across)
write(os.path.join(D, "presenter.wav"),
      (second + first * across)[int(LATE * RATE):int((LENGTH - 3.0) * RATE)])
GUEST = os.path.join(D, "GuestCam_C001.mov")
PRESENTER = os.path.join(D, "PresenterCam_C002.mov")
# A tiny picture at five frames: no frame is ever decoded. No timecode.
command = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
           "color=size=64x36:rate=5", "-i", os.path.join(D, "guest.wav"),
           "-i", os.path.join(D, "presenter.wav")]
for path, n in ((GUEST, 1), (PRESENTER, 2)):
    command += ["-map", "0:v", "-map", "%d:a" % n, "-shortest", "-c:v",
                "libx264", "-preset", "ultrafast", "-c:a", "pcm_s16le", path]
subprocess.run(command, check=True)


def figure(value):
    """A number for a failure line, or the word for its absence."""
    return "none" if value is None else "%+.3f" % value


#------------------------------------------------------- 1. The run

print("1. The run's cameras")
# The pair itself, measured apart from what the run then decides: a
# point every 30 s over 840 s, as the run samples two cameras. Read off
# here, a run that refused the camera cannot hide the reading.
_a, _b, pair = vpm.align_envelopes(vpm.envelope_heard(GUEST),
                                   vpm.envelope_heard(PRESENTER),
                                   sample_points=28, distance_s=30.0,
                                   warn=False)
print("   correlation %.3f, %s of %s points, spread %.1f ms"
      % (pair.get("quality", 0.0), pair.get("points"),
         pair.get("candidates"), pair.get("spread_ms") or 0.0))
check("the pair matches under the camera floor, so only the fit places it",
      pair.get("quality", 1.0) < vpm.CAMERA_MATCH_ENOUGH,
      "correlation %.3f against a floor of %.2f"
      % (pair.get("quality", 1.0), vpm.CAMERA_MATCH_ENOUGH))
said = io.StringIO()
with contextlib.redirect_stdout(said):
    ref, position = vpm.align_cameras(
        [(p, vpm.video_facts(p)) for p in (GUEST, PRESENTER)])
got = position.get(PRESENTER)
st = got[2] if got else {}
run_at = -got[0] if got else None
print("   reference %s, presenter %s s" % (os.path.basename(ref[0]),
                                          figure(run_at)))
check("the run places the camera by its sound, where it started",
      got is not None and not st.get("by_clock_only")
      and abs(run_at - LATE) <= FRAME,
      "%s s by %s, wanted %+.3f by sound"
      % (figure(run_at), "clock" if st.get("by_clock_only") else "sound",
         LATE))

#--------------------------------------------------- 2. The preview

print("\n2. The preview's axis")
with contextlib.redirect_stdout(io.StringIO()):
    data, text = vpm.measure_time_axis([GUEST, PRESENTER])
axis = data.get("axis") or {}
g, p = vpm.path_key(GUEST), vpm.path_key(PRESENTER)
preview_at = axis[p] - axis[g] if g in axis and p in axis else None
names = dict((key, sorted(os.path.basename(f) for f in data.get(key) or ()))
             for key in ("weak", "no_place"))
print("   presenter %s s, weak %s, no place %s"
      % (figure(preview_at), names["weak"], names["no_place"]))
check("the preview names the camera neither weak nor without a place",
      not names["weak"] and not names["no_place"],
      "weak %s, no place %s, wanted neither; the run placed it at %s s"
      % (names["weak"], names["no_place"], figure(run_at)))
check("and puts it where the run does",
      preview_at is not None and run_at is not None
      and abs(preview_at - run_at) <= FRAME,
      "preview %s s against the run's %s s" % (figure(preview_at),
                                               figure(run_at)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
