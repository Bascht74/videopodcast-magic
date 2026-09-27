# -*- coding: utf-8 -*-
"""Where the sound fits twice, the clocks show which place, and no more.

A reference camera in which one passage is heard twice, and a camera
holding only that passage. Sections: without clocks the camera is not
placed, two places fitting as well; with clocks two seconds wrong it is
placed at the measured place they point to, not at the clocks' own
reading, and the log says the clock showed where; with clocks 35 s off
either place it is not placed by sound at all. Synthetic material,
fixed seeds, the run's door (align_cameras).
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
LENGTH = 300.0
# A passage of forty seconds heard at the 60th second and again at the
# 200th; the second camera holds only it, from the second time.
FIRST_AT, AGAIN_AT, PASSAGE = 60.0, 200.0, 40.0
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
D = tempfile.mkdtemp(prefix="vpm_clockhint_")
room = turns(LENGTH, 11)
s = lambda t: int(t * RATE)
room[s(AGAIN_AT):s(AGAIN_AT + PASSAGE)] = room[s(FIRST_AT):s(FIRST_AT
                                                             + PASSAGE)]
rng = np.random.default_rng(12)
REF, CAM = D + "/WideCam.wav", D + "/GuestCam.wav"
write(REF, room + rng.normal(0, 0.004, len(room)))
write(CAM, room[s(AGAIN_AT):s(AGAIN_AT + PASSAGE)]
      + rng.normal(0, 0.004, s(PASSAGE)))


def placed(ref_clock=None, cam_clock=None):
    """align_cameras over the two: (the camera's start or None, st, log)."""
    said = io.StringIO()
    facts = lambda seconds, tc: dict(
        {"duration": seconds, "fps": 25.0},
        **({"tc": tc} if tc else {}))
    with contextlib.redirect_stdout(said):
        _ref, position = vpm.align_cameras(
            [(REF, facts(LENGTH, ref_clock)), (CAM, facts(PASSAGE, cam_clock))])
    got = position.get(CAM)
    if not got or got[2].get("by_clock_only"):
        return None, (got or (0, 0, {}))[2], said.getvalue()
    return -got[0] / got[1], got[2], said.getvalue()


def figure(value):
    return "none" if value is None else "%+.3f s" % value


#---------------------------------------------------- 1. Without a clock

print("1. The passage fits twice, and nothing says which")
at, st, _log = placed()
# The pair itself, as the search sees it, for the line.
q, nxt = vpm.best_and_next(vpm.video_envelope(REF),
                           vpm.video_envelope(CAM))[1:3]
print("   %s, match %.3f, next place %.3f" % (figure(at), q, nxt))
check("without clocks the sound places the camera nowhere",
      at is None, "placed at %s, match %.3f, next place %.3f"
      % (figure(at), q, nxt))

#-------------------------------------------- 2. Clocks two seconds off

print("\n2. The clocks point near the second time, two seconds off")
at, st, log = placed("10:00:00:00", "10:03:22:00")
print("   %s, match %.3f" % (figure(at), st.get("quality", 0.0)))
check("the sound places it at the time the clocks point to",
      at is not None and abs(at - AGAIN_AT) <= FRAME,
      "placed at %s, wanted %+.3f s within a frame, the clocks saying "
      "%+.3f s" % (figure(at), AGAIN_AT, AGAIN_AT + 2.0))
hint = vpm.T('found where its timecode pointed')
check("and the camera's axis line says the clock showed where",
      hint in vpm.camera_hint(st), "the hint %r for %r"
      % (vpm.camera_hint(st), hint))

#------------------------------------------ 3. Clocks pointing elsewhere

print("\n3. The clocks point at neither time")
# 35 s short of the second time: just past how far the search looks.
at, st, _log = placed("10:00:00:00", "10:02:45:00")
check("clocks at neither place leave the sound refusing it",
      at is None, "placed at %s, the clocks saying +165.000 s"
      % figure(at))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
