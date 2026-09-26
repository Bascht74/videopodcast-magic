# -*- coding: utf-8 -*-
"""The preview judges a short camera as the run does, stranger or not.

A six-minute reference camera, a minute of a second camera cut from
its fifth, and twenty seconds from another room whose match clears the
camera floor while a second place fits it nearly as well. Sections:
the right short camera, placed by run and preview at one offset; the
short stranger, its match over the floor, refused by both. Synthetic
material, fixed seeds, no timecode, so a camera the sound refuses has
no place at all.
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

RATE = 8000
# The material of time_short_cam_found, as cameras: the reference, a
# minute cut from its 240th second, and twenty seconds from elsewhere.
LENGTH = 360.0
MIDDLE_AT, MIDDLE_LEN = 240.0, 60.0
STRANGER_SEED, STRANGER_LEN = 202, 20.0
FRAME = 1.0 / 25


def turns(seconds, seed):
    """Speech-like turns: noise in irregular pieces with pauses between."""
    rng = np.random.default_rng(seed)
    n = int(seconds * RATE)
    x = np.zeros(n)
    t = 0.2
    while t < seconds - 1.0:
        long_s = float(rng.uniform(0.3, 3.0))
        k, i0 = int(long_s * RATE), int(t * RATE)
        k = min(k, n - i0)
        if k > 2:
            x[i0:i0 + k] = rng.normal(0, 0.25, k) * np.hanning(k)
        t += long_s + float(rng.uniform(0.2, 2.5))
    return x


def write(path, x):
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())


# Its own folder under the run's TMPDIR, which the run throws away.
D = tempfile.mkdtemp(prefix="vpm_shortasrun_")
one, other = turns(LENGTH, 5), turns(LENGTH, 6)
other = other * (np.abs(one) < 1e-6)
rng = np.random.default_rng(1)
write(D + "/wide.wav",
      0.5 * one + 0.5 * other + rng.normal(0, 0.004, len(one)))
near = other + 0.15 * one + rng.normal(0, 0.003, len(one))
write(D + "/guest.wav",
      near[int(MIDDLE_AT * RATE):int((MIDDLE_AT + MIDDLE_LEN) * RATE)])
write(D + "/jingle.wav", turns(STRANGER_LEN, STRANGER_SEED)
      + np.random.default_rng(STRANGER_SEED).normal(
          0, 0.003, int(STRANGER_LEN * RATE)))
REF = os.path.join(D, "WideCam_C001.mov")
MIDDLE = os.path.join(D, "GuestCam_C002.mov")
STRANGER = os.path.join(D, "JingleCam_C003.mov")
# A tiny picture at five frames: no frame is ever decoded. No timecode.
command = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
           "color=size=64x36:rate=5"]
for name in ("wide", "guest", "jingle"):
    command += ["-i", os.path.join(D, name + ".wav")]
for path, n in ((REF, 1), (MIDDLE, 2), (STRANGER, 3)):
    command += ["-map", "0:v", "-map", "%d:a" % n, "-shortest", "-c:v",
                "libx264", "-preset", "ultrafast", "-c:a", "pcm_s16le", path]
subprocess.run(command, check=True)


def the_run(path):
    """Where align_cameras puts *path* against the reference, or None."""
    with contextlib.redirect_stdout(io.StringIO()):
        _ref, position = vpm.align_cameras(
            [(p, vpm.video_facts(p)) for p in (REF, path)])
    got = position.get(path)
    return (-got[0], got[2]) if got else (None, {})


def the_preview(path):
    """Where measure_time_axis puts *path* after the reference, and lists."""
    with contextlib.redirect_stdout(io.StringIO()):
        data, _text = vpm.measure_time_axis([REF, path])
    axis = data.get("axis") or {}
    r, p = vpm.path_key(REF), vpm.path_key(path)
    at = axis[p] - axis[r] if r in axis and p in axis else None
    return at, [os.path.basename(f) for f in data.get("no_place") or ()]


def figure(value):
    """A number for a failure line, or the word for its absence."""
    return "none" if value is None else "%+.3f" % value


#------------------------------------------- 1. The right short camera

print("1. A minute of the second camera, cut from its fifth minute")
run_at, st = the_run(MIDDLE)
preview_at, nowhere = the_preview(MIDDLE)
print("   run %s s (match %.3f, next place %.3f), preview %s s"
      % (figure(run_at), st.get("quality", 0.0), st.get("next_best", 0.0),
         figure(preview_at)))
check("the run places the right short camera where it was cut out",
      run_at is not None and abs(run_at - MIDDLE_AT) <= FRAME,
      "run %s s, wanted %+.3f s within a frame" % (figure(run_at), MIDDLE_AT))
check("and the preview puts it at the run's offset",
      preview_at is not None and run_at is not None
      and abs(preview_at - run_at) <= FRAME,
      "preview %s s against the run's %s s, no place %s"
      % (figure(preview_at), figure(run_at), nowhere))

#------------------------------------------------ 2. The short stranger

print("\n2. Twenty seconds from another room")
# The pair itself, apart from what either then decides: under the floor
# the old rule refused it too, and nothing here would tell the two apart.
q, nxt = vpm.best_and_next(vpm.video_envelope(REF),
                           vpm.video_envelope(STRANGER))[1:]
check("the stranger's match clears the camera floor",
      q >= vpm.CAMERA_MATCH_ENOUGH,
      "match %.3f against a floor of %.2f, next place %.3f"
      % (q, vpm.CAMERA_MATCH_ENOUGH, nxt))
run_at, st = the_run(STRANGER)
preview_at, nowhere = the_preview(STRANGER)
print("   match %.3f, next place %.3f; run %s s, preview %s s, no place %s"
      % (q, nxt, figure(run_at), figure(preview_at), nowhere))
check("the run refuses the short stranger",
      run_at is None, "run placed it at %s s" % figure(run_at))
check("and the preview refuses it too, naming it as without a place",
      preview_at is None and os.path.basename(STRANGER) in nowhere,
      "preview %s s, no place %s; the run placed it at %s s"
      % (figure(preview_at), nowhere, figure(run_at)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
