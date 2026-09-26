# -*- coding: utf-8 -*-
"""A recording whose sample points scatter is not placed by them.

The plain loudness curve can find a place its own sample points do
not bear out: they scatter, or lie on a line no recorder runs at. In
order -- those points speak against the answer, a right pair's do
not, too few say nothing, and a clock speed alone speaks as well;
the run then does not keep that answer; the preview names the file
as not fitting. Synthetic material, one seed, cut out of one room.
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
import sys, tempfile, time, wave
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
# A camera of five minutes hearing two people taking turns, and one
# person's microphone of three. The microphone starts 260 s into the
# camera and runs past its end, its clock 40 ppm fast. The answer is
# +260.0 s; it stands here as a number.
LENGTH, REC_LEN, STARTS_AT, DRIFT = 300.0, 180.0, 260.0, 40e-6


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


def cut(x, t0, t1, drift=0.0):
    """Seconds t0 to t1 of x, read by a clock running *drift* fast."""
    at = t0 * RATE + np.arange(int((t1 - t0) * RATE)) * (1.0 + drift)
    return np.interp(at, np.arange(len(x)), x)


def pair(folder, name, starts_at, seed):
    """The camera and the microphone, the microphone *starts_at* in."""
    whole = LENGTH + 2 * REC_LEN + 10
    one = turns(whole, seed)
    other = turns(whole, seed + 1000) * (np.abs(one) < 1e-6)
    rng = np.random.default_rng(seed + 3)
    camera = 0.5 * one + 0.5 * other + rng.normal(0, 0.004, len(one))
    mic = other + 0.1 * one + rng.normal(0, 0.003, len(one))
    before = REC_LEN + 5
    ref, rec = folder + "/%s_cam.wav" % name, folder + "/%s_mic.wav" % name
    write(ref, cut(camera, before, before + LENGTH))
    write(rec, cut(mic, before + starts_at, before + starts_at + REC_LEN,
                   DRIFT))
    return ref, rec


def plain(ref, rec):
    """The plain curve's answer, asked the way the run asks it."""
    return vpm.align_envelopes(vpm.video_envelope(ref, 5.0, 4000),
                               vpm.video_envelope(rec, 5.0, 4000), 5.0,
                               sample_points=20, distance_s=30.0, warn=False)


def said(st):
    return "%s points, spread %.1f ms, %+.0f ppm, match %.3f" % (
        st.get("points"), st.get("spread_ms") or 0.0, st.get("ppm") or 0.0,
        st.get("quality", 0.0))


# Its own folder under the run's TMPDIR, which the run throws away.
D = tempfile.mkdtemp(prefix="vpm_scatter_")
# The microphone hanging off the back of the camera, only its first 40 s
# shared -- with more the curve finds it, since it searches the whole
# camera; and the same recording wholly inside, from the 60th second.
REF, REC = pair(D, "back", STARTS_AT, 38)
REF_IN, REC_IN = pair(D, "inside", 60.0, 32)

#------------------------------------------ 1. The points speak against it

print("1. The sample points against the plain curve's answer")
_a, _b, st = plain(REF, REC)
print("   hanging off the back: %s" % said(st))
check("the plain answer's points contradict it",
      bool(vpm.fit_speaks_against(st)),
      "%s -- wanted a spread over %s ms or a clock speed over %s ppm"
      % (said(st), vpm.FIT_SPREAD_MS, vpm.CLOCK_SPEED_BELIEVED_PPM))
_a, _b, st_in = plain(REF_IN, REC_IN)
print("   wholly inside:        %s" % said(st_in))
check("a right pair's points do not",
      not vpm.fit_speaks_against(st_in),
      "%s -- a right pair, wanted False" % said(st_in))
FEW = {"points": 2, "spread_ms": 400.0, "ppm": 5000.0}
check("fewer than three points say nothing",
      not vpm.fit_speaks_against(FEW),
      "2 points, 400 ms, 5000 ppm gave %s, wanted False"
      % vpm.fit_speaks_against(FEW))
STEADY = {"points": 12, "spread_ms": 5.0, "ppm": 5000.0}
check("a clock speed no recorder runs at speaks against it alone",
      bool(vpm.fit_speaks_against(STEADY)),
      "12 points, 5 ms, 5000 ppm gave %s, wanted True"
      % vpm.fit_speaks_against(STEADY))

#------------------------------------------------- 2. The run

print("\n2. The run does not keep the contradicted answer")
a, b, st = vpm.align_audio_to_video(REC, REF, sample_points=20,
                                    distance_s=30.0)
where = -a / b
print("   placed at %+.3f s, %s%s" % (
    where, "refused" if st.get("unplaceable") else "placed",
    ", by phase" if st.get("from_phase") else ""))
check("the run does not keep the contradicted answer",
      st.get("unplaceable") or abs(where - STARTS_AT) < 0.05,
      "at %+.3f s, wanted %+.1f s or refused; the plain curve said %s"
      % (where, STARTS_AT, said(plain(REF, REC)[2])))

#------------------------------------------------- 3. The preview

print("\n3. The preview names it as not fitting")
data, text = vpm.measure_time_axis([REF, REC])
print("   %s" % text)
KEY = vpm.path_key(REC)
weak = [vpm.path_key(p) for p in data.get("weak") or ()]
under = [vpm.path_key(p) for p in data.get("unplaceable") or ()]
check("the preview names it as not fitting",
      KEY in weak and KEY not in under,
      "weak %s, under the floor %s -- wanted it weak and not under"
      % (KEY in weak, KEY in under))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
