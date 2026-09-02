# -*- coding: utf-8 -*-
"""A steady tone no longer keeps a file off the time axis.

Where the plain loudness curve finds nothing, the same way runs again
on the bands that move: what stands still over a whole recording says
nothing about the time. In order -- what is left without it, the
phase, whose answer no sample point backs up; the second try placing
the file and handing the gate its numbers; the cheap way staying where
it reaches; and a recording that fits nowhere, placed by neither.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, subprocess, sys, tempfile, time, wave
import numpy as np

spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
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
# The recording runs a minute, the camera forty seconds of it from the
# fourth second on. So the answer both ways is +4.000 s, and it stands
# here as a number rather than being worked out from the material.
LENGTH, CAM_LEN, CAM_LATE = 60.0, 40.0, 4.0
# The tone: 100 Hz, the second harmonic of a 50 Hz mains, and 40 dB
# over the speech beside it. Measured on this material: the plain
# curve then reads 0.03 where it read 0.90 without it, and more tone
# does not push it lower -- 50 dB reads 0.026.
HUM_HZ, HUM_OVER_DB, HUM_AMP = 100.0, 40.0, 0.8
# What the run asks for on a reference of half an hour. Written out
# rather than left to the default: the gate below wants fifty sample
# points, and the default of one every two minutes never has them on
# material a test can afford to build.
ASKED = dict(sample_points=60, distance_s=30.0)


def bursts(seconds, seed):
    """Speech-like turns: noise in irregular pieces with pauses between.

    Irregular lengths and gaps make the cross correlation unambiguous;
    an even pattern fits itself at many places and the peak is then a
    coin toss.
    """
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


D = tempfile.mkdtemp(prefix="vpm_secondtry_")
# The speech is set so far down that the tone fits over it without
# clipping: clipped, the tone breaks into harmonics that follow the
# speech, and then it is no longer a band that stands still.
loud = HUM_AMP / np.sqrt(2.0) / 10 ** (HUM_OVER_DB / 20.0)
raw = bursts(LENGTH, 1) + np.random.default_rng(9).normal(
    0, 0.0004, int(LENGTH * RATE))
scale = loud / float(np.sqrt((raw ** 2).mean()))
whole = raw * scale
write(D + "/Guest.wav", whole)
# A second recording of the same shape and a different seed: nothing in
# it was ever in the same room as the camera.
write(D + "/Stray.wav",
      (bursts(LENGTH, 7) + np.random.default_rng(11).normal(
          0, 0.0004, int(LENGTH * RATE))) * scale)
cut_out = whole[int(CAM_LATE * RATE):int((CAM_LATE + CAM_LEN) * RATE)].copy()
seconds = np.arange(len(cut_out)) / float(RATE)
write(D + "/hum.wav",
      cut_out + HUM_AMP * np.sin(2 * np.pi * HUM_HZ * seconds))
write(D + "/clean.wav", cut_out)
PICTURE = ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
           "-c:a", "pcm_s16le"]
# One ffmpeg call for both cameras: a process start is what the Windows
# builder charges for. No frame is ever decoded, so colour bars do.
subprocess.run(
    ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
     "smptebars=size=320x180:rate=25:duration=%.1f" % CAM_LEN,
     "-i", D + "/hum.wav", "-i", D + "/clean.wav",
     "-map", "0:v", "-map", "1:a", "-t", "%.2f" % CAM_LEN] + PICTURE
    + [D + "/WideCam.mov",
       "-map", "0:v", "-map", "2:a", "-t", "%.2f" % CAM_LEN] + PICTURE
    + [D + "/Presenter.mov"], check=True)
GUEST, STRAY = D + "/Guest.wav", D + "/Stray.wav"
HUMMED, CLEAN = D + "/WideCam.mov", D + "/Presenter.mov"
second_way = vpm.align_on_moving_bands


def numbers(st):
    """The three numbers every line below carries, in one shape."""
    return "%.4f from %d points at %s ms" % (
        st.get("quality", 0.0), st.get("points", 0),
        "no" if st.get("spread_ms") is None else "%.2f" % st["spread_ms"])


#--------------------------------------- 1. What the plain curve does

print("1. The plain curve alone, with the second try taken out")
vpm.align_on_moving_bands = lambda *a, **k: None
plain_a, _b, plain = vpm.align_audio_to_video(GUEST, HUMMED, 0, **ASKED)
vpm.align_on_moving_bands = second_way
print("   hummed camera, plain only: %s, offset %+.3f s"
      % (numbers(plain), plain_a))
check("the still tone holds the plain curve under the floor",
      plain.get("quality", 0.0) < vpm.WEAK_MATCH,
      "%s, against a floor of %.2f" % (numbers(plain), vpm.WEAK_MATCH))
check("without the second try the phase is all that is left",
      plain.get("from_phase") is True,
      "the mark is %r, sharpness %s against %.1f"
      % (plain.get("from_phase"),
         "none" if plain.get("phase_sharp") is None
         else "%.1f" % plain["phase_sharp"], vpm.PHASE_SHARP_ENOUGH))
check("and it brings back nothing the gate can judge",
      vpm.fit_places_it(plain) is False,
      "%r from %s, and the gate wants %d points at %.1f ms"
      % (vpm.fit_places_it(plain), numbers(plain), vpm.FIT_POINTS_ENOUGH,
         vpm.FIT_SPREAD_MS))


#--------------------------------------------- 2. The second try

print("\n2. The second try places what the tone hid")
# Asked once on its own, so what it hands back can be looked at
# before the gate has taken or refused it -- through the chain those
# two are one answer, and a check on them would only say the gate
# agrees with itself.
alone = second_way(vpm.decode_audio(HUMMED, rate=4000),
                   vpm.decode_audio(GUEST, rate=4000, ss=0.0),
                   5.0, 4000, ASKED["sample_points"], 20.0,
                   ASKED["distance_s"])
found_a, found_b, found = vpm.align_audio_to_video(GUEST, HUMMED, 0, **ASKED)
print("   hummed camera: on its own %s | through the chain %s, offset "
      "%+.3f s" % ("-- none --" if alone is None else numbers(alone[2]),
                   numbers(found), found_a))
check("the second try hands back sample points, not a bare offset",
      alone is not None
      and alone[2].get("points", 0) >= vpm.FIT_POINTS_ENOUGH,
      "%s, the floor is %d points"
      % ("no answer at all" if alone is None
         else "%d points" % alone[2].get("points", 0),
         vpm.FIT_POINTS_ENOUGH))
check("and how far they scatter around the line",
      alone is not None and alone[2].get("spread_ms") is not None
      and alone[2]["spread_ms"] <= vpm.FIT_SPREAD_MS,
      "%s ms, the limit is %.1f"
      % ("no answer at all" if alone is None
         else "no" if alone[2].get("spread_ms") is None
         else "%.2f" % alone[2]["spread_ms"], vpm.FIT_SPREAD_MS))
check("so the gate can judge the second try, and lets it through",
      alone is not None and vpm.fit_places_it(alone[2]) is True,
      "%r from %s" % (alone is not None and vpm.fit_places_it(alone[2]),
                      "no answer at all" if alone is None
                      else numbers(alone[2])))
check("the second try is the one that placed it",
      found.get("from_bands") is True,
      "the mark is %r, %s" % (found.get("from_bands"), numbers(found)))
check("and it places the camera where the picture was cut out",
      abs(found_a - CAM_LATE) < 0.04,
      "%+.3f s, wanted %+.3f" % (found_a, CAM_LATE))
check("with no drift invented on the way", abs(found_b - 1.0) < 1e-4,
      "%.6f, wanted 1.000000 to within 0.0001" % found_b)
check("the phase way was never reached",
      found.get("phase_sharp") is None and not found.get("from_phase"),
      "sharpness %s and the phase mark %r, wanted none and None"
      % ("none" if found.get("phase_sharp") is None
         else "%.1f" % found["phase_sharp"], found.get("from_phase")))


#------------------------------------- 3. Where the cheap way reaches

print("\n3. The cheap way stays where it reaches")
tried = []


def counted(*a, **k):
    tried.append(1)
    return second_way(*a, **k)


vpm.align_on_moving_bands = counted
easy_a, _b, easy = vpm.align_audio_to_video(GUEST, CLEAN, 0, **ASKED)
after_easy = len(tried)
vpm.align_audio_to_video(GUEST, HUMMED, 0, **ASKED)
after_hard = len(tried)
vpm.align_on_moving_bands = second_way
print("   camera without the tone: %s, offset %+.3f s"
      % (numbers(easy), easy_a))
check("a camera the plain curve places never enters the second try",
      after_easy == 0,
      "entered %d times, wanted 0 -- the plain curve read %s"
      % (after_easy, numbers(easy)))
check("and the plain curve puts it where the picture was cut out",
      abs(easy_a - CAM_LATE) < 0.04,
      "%+.3f s, wanted %+.3f" % (easy_a, CAM_LATE))
check("a camera it cannot place does enter it",
      after_hard - after_easy == 1,
      "entered %d times for the hummed camera, wanted 1"
      % (after_hard - after_easy))


#------------------------------------------------------ 4. The guard

print("\n4. A recording that fits nowhere is not placed either")
lost_a, _b, lost = vpm.align_audio_to_video(STRAY, HUMMED, 0, **ASKED)
apart = second_way(vpm.decode_audio(HUMMED, rate=4000),
                   vpm.decode_audio(STRAY, rate=4000, ss=0.0),
                   5.0, 4000, ASKED["sample_points"], 20.0,
                   ASKED["distance_s"])
print("   foreign recording: plain %s | second try %s"
      % (numbers(lost), "-- none --" if apart is None else numbers(apart[2])))
check("the foreign recording stays under the floor on the plain curve",
      lost.get("quality", 0.0) < vpm.WEAK_MATCH,
      "%s, against a floor of %.2f" % (numbers(lost), vpm.WEAK_MATCH))
check("the second try ran on it and came back with an answer",
      apart is not None and len(apart) == 3,
      "%s came back, wanted an offset, a drift and the numbers"
      % ("nothing" if apart is None else "%d values" % len(apart)))
check("but its sample points do not reach the gate",
      apart is not None and vpm.fit_places_it(apart[2]) is False,
      "%r from %s, wanted False -- the floor is %d points at %.1f ms"
      % (apart is not None and vpm.fit_places_it(apart[2]),
         "no answer" if apart is None else numbers(apart[2]),
         vpm.FIT_POINTS_ENOUGH, vpm.FIT_SPREAD_MS))
check("so nothing was placed on the bands",
      not lost.get("from_bands"),
      "the mark is %r, and the offset it would hand back is %+.3f s"
      % (lost.get("from_bands"), lost_a))
check("and the file is refused rather than laid down at a guess",
      lost.get("unplaceable") is True,
      "the mark is %r, phase sharpness %s against %.1f"
      % (lost.get("unplaceable"),
         "none" if lost.get("phase_sharp") is None
         else "%.1f" % lost["phase_sharp"], vpm.PHASE_SHARP_ENOUGH))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
