# -*- coding: utf-8 -*-
"""A short camera is found anywhere in a long one, and a stranger is not.

In order: a short camera cut from the middle and one from the end of a
long reference, placed where they were cut out; the same search the
other way round, the short curve first; a stranger as long as they are
refused; a short stranger whose match clears the floor refused too,
because another place fits it nearly as well; and the log saying so.
Synthetic material, fixed seeds, one room.
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
SCRIPT = the_program.SCRIPT
import contextlib, io, tempfile, time, wave
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
# A reference camera of six minutes hearing two people taking turns,
# and a second camera nearer one of them. Two short pieces are cut out
# of the second: one from the 240th second, far past its own minute,
# and the last 40 s. Their answers stand here as numbers.
LENGTH = 360.0
MIDDLE_AT, MIDDLE_LEN = 240.0, 60.0
END_AT, END_LEN = 320.0, 40.0
# Twenty seconds of turns from another room. Measured on this seed: its
# match clears the camera floor, and a second place fits it all but as
# well -- so only that second place can refuse it.
SHORT_STRANGER_SEED, SHORT_STRANGER_LEN = 202, 20.0


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
D = tempfile.mkdtemp(prefix="vpm_shortcam_")
one, other = turns(LENGTH, 5), turns(LENGTH, 6)
other = other * (np.abs(one) < 1e-6)
rng = np.random.default_rng(1)
REF = D + "/WideCam.wav"
write(REF, 0.5 * one + 0.5 * other + rng.normal(0, 0.004, len(one)))
near = other + 0.15 * one + rng.normal(0, 0.003, len(one))
MIDDLE, END = D + "/GuestCam.wav", D + "/PresenterCam.wav"
write(MIDDLE, near[int(MIDDLE_AT * RATE):int((MIDDLE_AT + MIDDLE_LEN) * RATE)])
write(END, near[int(END_AT * RATE):int((END_AT + END_LEN) * RATE)])
STRANGER, SHORT_STRANGER = D + "/StrayCam.wav", D + "/JingleCam.wav"
write(STRANGER, turns(MIDDLE_LEN, 77)
      + np.random.default_rng(77).normal(0, 0.003, int(MIDDLE_LEN * RATE)))
write(SHORT_STRANGER, turns(SHORT_STRANGER_LEN, SHORT_STRANGER_SEED)
      + np.random.default_rng(SHORT_STRANGER_SEED).normal(
          0, 0.003, int(SHORT_STRANGER_LEN * RATE)))


def against_reference(path, seconds, facts=None):
    """align_cameras on the reference and one camera: (answer or None, log)."""
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        _ref, position = vpm.align_cameras(
            [(REF, dict({"duration": LENGTH}, **(facts or {}))),
             (path, dict({"duration": seconds}, **(facts or {})))])
    return position.get(path), said.getvalue()


def numbers(got):
    if got is None:
        return "refused"
    a, _b, st = got
    return "at %+.3f s, match %.3f, next place %.3f, %s points" % (
        a, st.get("quality", 0.0), st.get("next_best", 0.0), st.get("points"))


#------------------------------------------ 1. Along the whole reference

print("1. A short camera is looked for along the whole reference")
middle, _log = against_reference(MIDDLE, MIDDLE_LEN)
print("   from the middle: %s" % numbers(middle))
check("a short camera from the middle is placed where it was cut out",
      middle is not None and abs(middle[0] + MIDDLE_AT) < 0.04,
      "%s, wanted %+.3f s within 40 ms" % (numbers(middle), -MIDDLE_AT))
end, _log = against_reference(END, END_LEN)
print("   from the end:    %s" % numbers(end))
check("and one from the end of it as well",
      end is not None and abs(end[0] + END_AT) < 0.04,
      "%s, wanted %+.3f s within 40 ms" % (numbers(end), -END_AT))

#-------------------------------------------- 2. The other way round

print("\n2. The short curve first, the long one second")
env_ref = vpm.video_envelope(REF)
env_mid = vpm.video_envelope(MIDDLE)
a, _b, st = vpm.align_envelopes(env_mid, env_ref, sample_points=20,
                                distance_s=30.0, warn=False)
print("   at %+.3f s, match %.3f" % (a, st.get("quality", 0.0)))
check("a short first curve is found inside a longer second one",
      abs(a - MIDDLE_AT) < 0.04,
      "at %+.3f s, match %.3f, wanted %+.3f s within 40 ms"
      % (a, st.get("quality", 0.0), MIDDLE_AT))

#------------------------------------------------------ 3. Strangers

print("\n3. A camera from another room is not placed")
stranger, _log = against_reference(STRANGER, MIDDLE_LEN)
print("   a minute of it:  %s" % numbers(stranger))
check("a stranger as long as the short cameras is refused",
      stranger is None, numbers(stranger))
short_stranger, _log = against_reference(SHORT_STRANGER, SHORT_STRANGER_LEN)
q, nxt = vpm.best_and_next(env_ref, vpm.video_envelope(SHORT_STRANGER))[1:]
print("   twenty seconds:  %s (match %.3f, next place %.3f)"
      % (numbers(short_stranger), q, nxt))
check("a short one is refused although its match clears the floor",
      short_stranger is None and q >= vpm.CAMERA_MATCH_ENOUGH,
      "%s; its match %.3f against a floor of %.2f, the next place %.3f"
      % (numbers(short_stranger), q, vpm.CAMERA_MATCH_ENOUGH, nxt))

#-------------------------------------------------------- 4. The log

print("\n4. With a clock it stands there, and the log says why")
CLOCKS = {"tc": "10:00:00:00", "fps": 25.0}
by_clock, log = against_reference(SHORT_STRANGER, SHORT_STRANGER_LEN, CLOCKS)
st = by_clock[2] if by_clock else {}
# The two numbers of section 3: the same two curves, the same search.
wanted = vpm.T('  %s: its sound matches by %s, and by %s at another '
               'place as well -- placed by its clock alone') % (
    os.path.basename(SHORT_STRANGER), vpm.number_text(q, 3),
    vpm.number_text(nxt, 3))
print("   %s" % log.strip())
check("the log names the second place that fits as well",
      bool(st.get("by_clock_only")) and wanted in log,
      "by clock %r, wanted the line %r in %r"
      % (st.get("by_clock_only"), wanted.strip(), log.strip()))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
