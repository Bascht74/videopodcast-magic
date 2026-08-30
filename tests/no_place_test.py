# -*- coding: utf-8 -*-
"""A video nothing can place is refused, not laid down at a guess.

Without the refusal the numbers of a failed alignment are handed back
and used. The rule holds only where there is no usable timecode: a
camera with a clock is placed by it, and refusing that for an
uncorrelated sound throws away a known file. Three cases: no timecode
and a foreign sound, a timecode and the same sound, one that fits.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, shutil, subprocess, sys, wave
import numpy as np
sys.path.insert(0, HERE)
from fixture_root import fixture

spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

os.environ.setdefault("VPM_NO_SPEAKER_SPLIT", "1")
ENV = dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="en",
           VPM_SILENT="1", VPM_NO_UPDATE_CHECK="1")

error = []


def check(name, ok, extra=""):
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


#------------------------------------------------------------- Material

RATE = 48000
# The envelope needs length: against too short a camera the same steady
# noise lands just over the floor, and the refusal would then depend on
# the seed rather than on the material.
LENGTH, CAM_LEN, CAM_LATE = 60.0, 40.0, 4.0
# Both cameras that have a clock carry the same one; the third has none.
REC_TC = "10:00:00:00"
CAM_TC = "10:00:04:00"


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


def read(path):
    with wave.open(path) as f:
        return np.frombuffer(f.readframes(f.getnframes()),
                             "<i2").astype(float)


def begins_at(reference, track):
    """Where in *reference* the first sample of *track* was taken from."""
    n = 1 << int(np.ceil(np.log2(len(reference) + len(track))))
    c = np.fft.irfft(np.fft.rfft(reference, n)
                     * np.conj(np.fft.rfft(track, n)), n)
    k = int(np.argmax(np.abs(c)))
    return (k - n if k > n // 2 else k) / float(RATE)


D = fixture("noplace")
shutil.rmtree(D, ignore_errors=True)
os.makedirs(D)
whole = (bursts(LENGTH, 1)
         + np.random.default_rng(9).normal(0, 0.0004, int(LENGTH * RATE)))
write(D + "/plain.wav", whole)
# The foreign sound: steady noise, the case the program names itself --
# no edges, nothing to align on. One file for both cameras that carry
# it, so the two differ in their timecode and in nothing else.
write(D + "/foreign.wav",
      np.random.default_rng(2).normal(0, 0.2, int(CAM_LEN * RATE)))

# Two ffmpeg calls for everything: a process start is what the Windows
# builder charges for. The first gives the recording its timecode --
# wave cannot write a bext chunk. The second writes all three cameras,
# colour bars at ultrafast, since no frame is ever decoded.
subprocess.run(
    ["ffmpeg", "-v", "error", "-y", "-i", D + "/plain.wav",
     "-write_bext", "1", "-metadata",
     "time_reference=%d" % int(vpm.parse_timecode(REC_TC, 25.0) * RATE),
     "-c:a", "pcm_s16le", D + "/Rec.wav"], check=True)
PICTURE = ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
           "-c:a", "pcm_s16le"]
subprocess.run(
    ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
     "smptebars=size=320x180:rate=25:duration=%.1f" % CAM_LEN,
     "-i", D + "/plain.wav", "-i", D + "/foreign.wav",
     # The camera that fits: its sound is the recording from CAM_LATE
     # on, so picture time t is recording time t + CAM_LATE.
     "-map", "0:v", "-map", "1:a", "-ss", "%.2f" % CAM_LATE,
     "-t", "%.2f" % CAM_LEN, "-timecode", CAM_TC] + PICTURE
    + [D + "/Good.mov",
       # The one nothing can place: foreign sound, and no clock.
       "-map", "0:v", "-map", "2:a", "-t", "%.2f" % CAM_LEN] + PICTURE
    + [D + "/Lost.mov",
       # The same foreign sound, but this one knows what time it is.
       "-map", "0:v", "-map", "2:a", "-t", "%.2f" % CAM_LEN,
       "-timecode", CAM_TC] + PICTURE + [D + "/Clock.mov"], check=True)

REC = D + "/Rec.wav"
GOOD, LOST, CLOCK = D + "/Good.mov", D + "/Lost.mov", D + "/Clock.mov"
rec = read(D + "/plain.wav")
facts = dict((v, vpm.video_facts(v)) for v in (GOOD, LOST, CLOCK))
audio_start = vpm.file_timecode(REC)


#--------------------------------------------------- 1. The measurement

print("1. What the alignment finds, and what it admits")
found = {}
for v in (GOOD, LOST, CLOCK):
    a, b, st = vpm.align_audio_to_video(REC, v, 0)
    found[v] = (a, st)
    print("   %-10s offset %+7.3f s, envelopes %+.3f, phase %s"
          % (os.path.basename(v), a, st.get("quality", 0.0),
             "-" if st.get("phase_sharp") is None
             else "%.1f" % st["phase_sharp"]))
check("the camera that fits is found where it was cut out",
      abs(found[GOOD][0] - CAM_LATE) < 0.04,
      "%+.3f s, wanted %+.3f" % (found[GOOD][0], CAM_LATE))
check("and its match is far above the floor",
      found[GOOD][1].get("quality", 0.0) > 0.5,
      "%.3f against %.2f" % (found[GOOD][1].get("quality", 0.0),
                             vpm.WEAK_MATCH))
check("it is not marked unplaceable",
      not found[GOOD][1].get("unplaceable"))
for v in (LOST, CLOCK):
    short = os.path.basename(v)
    st = found[v][1]
    check("%s: the envelopes stay under the floor" % short,
          st.get("quality", 0.0) < vpm.WEAK_MATCH,
          "%.3f against %.2f" % (st.get("quality", 0.0), vpm.WEAK_MATCH))
    check("%s: the phase way was tried and failed too" % short,
          st.get("phase_sharp") is not None
          and st["phase_sharp"] < vpm.PHASE_SHARP_ENOUGH,
          "%.1f against %.1f" % (st.get("phase_sharp") or 0.0,
                                 vpm.PHASE_SHARP_ENOUGH))
    check("%s: and it says so, instead of handing back a guess" % short,
          bool(st.get("unplaceable")))


#--------------------------------------------------------- 2. The rule

print("\n2. The rule: the timecode decides whether refusing is allowed")
check("no timecode anywhere, no place",
      vpm.cannot_be_placed(found[LOST][1], None, [audio_start]) is True)
check("a timecode on both sides, and it stays",
      vpm.cannot_be_placed(found[CLOCK][1],
                           vpm.timecode_seconds(facts[CLOCK]),
                           [audio_start]) is False)
check("an alignment that worked is never refused",
      vpm.cannot_be_placed(found[GOOD][1], None, [audio_start]) is False)
# A clock reading only says something next to a second one.
check("a lone timecode among files that have none places nothing",
      vpm.timecode_places_it(36000.0, [None, None]) is False)
check("but one with a partner does",
      vpm.timecode_places_it(36000.0, [None, 36004.0]) is True)


#------------------------------------------------- 3. Two cameras alone

print("\n3. Camera against camera: the refused one leaves the axis")
ref, position = vpm.align_cameras([(v, facts[v]) for v in
                                   (GOOD, LOST, CLOCK)])
check("the camera that fits is the reference", ref[0] == GOOD,
      os.path.basename(ref[0]))
check("the one nothing can place is not on the axis",
      LOST not in position, str(sorted(map(os.path.basename, position))))
check("the one with a timecode still is", CLOCK in position)


#------------------------------------------------------ 4. A whole run

print("\n4. A whole run: recording plus three cameras")
p = subprocess.run(
    [sys.executable, SCRIPT, "--without-auphonic", "--no-metrics",
     "--out", D + "/run", REC, GOOD, LOST, CLOCK],
    capture_output=True, text=True, timeout=900, env=ENV)
log = (p.stdout or "") + (p.stderr or "")
check("no traceback", "Traceback" not in log,
      log[log.find("Traceback"):][:90])
check("nothing was sent to auphonic.com",
      "auphonic.com/api" not in log and "Uploading" not in log)
check("the run ends non-zero, because one camera was left out",
      p.returncode == 1, str(p.returncode))
said = [line.strip() for line in log.splitlines()
        if "cannot be placed" in line]
print("   %s" % (said[0][:150] if said else "-- nothing said --"))
check("the run says one file cannot be placed", len(said) == 1,
      "%d lines" % len(said))
check("and names the one that cannot", bool(said) and "Lost.mov" in said[0])
# Without a way out, and without saying whose job it is, the message is
# a dead end.
check("the message asks for a timecode",
      bool(said) and "timecode" in said[0].lower())
check("and says it has to be set elsewhere",
      bool(said) and "another program" in said[0])
check("the camera with the clock is not among the refused",
      not any("Clock.mov" in line for line in said))
made = dict((n, os.path.exists("%s/run/%s_audio.mov" % (D, n)))
            for n in ("Good", "Lost", "Clock"))
print("   written: %s" % made)
check("nothing was written for the refused camera", made["Lost"] is False)
check("the one with the clock was written all the same",
      made["Clock"] is True)
check("and so was the one that fits", made["Good"] is True)
if made["Good"]:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i",
                    D + "/run/Good_audio.mov", "-map", "0:a:0",
                    "-c:a", "pcm_s16le", "-ar", str(RATE),
                    D + "/good_track.wav"], check=True)
    at = begins_at(rec, read(D + "/good_track.wav"))
    check("its new track still starts where the picture starts",
          abs(at - CAM_LATE) < 0.04,
          "begins at %.3f s of the recording, wanted %.3f" % (at, CAM_LATE))


#-------------------------------------------- 5. What the window offers

print("\n5. In the window: the file is proposed for 'ignore this video'")
data, text = vpm.measure_time_axis([REC, GOOD, LOST, CLOCK],
                                   lambda p: vpm.file_timecode(p))
lost = [os.path.basename(x) for x in (data.get("unplaceable") or [])]
print("   unplaceable: %s   weak: %s"
      % (lost, [os.path.basename(x) for x in (data.get("weak") or [])]))
check("the measurement names the file with no place", lost == ["Lost.mov"],
      str(lost))
check("and not the one with a timecode", "Clock.mov" not in lost)

kinds = dict((v, vpm.Value(vpm.TYPE_CONTENT)) for v in (GOOD, LOST, CLOCK))
moved = vpm.kind_proposal_apply(kinds, data.get("unplaceable"))
check("the proposal moves exactly that one", moved == [LOST], str(moved))
check("and sets it to 'ignore this video'",
      kinds[LOST].get() == vpm.TYPE_IGNORED, kinds[LOST].get())
check("the others keep what they were",
      kinds[GOOD].get() == vpm.TYPE_CONTENT
      and kinds[CLOCK].get() == vpm.TYPE_CONTENT)
check("a second round changes nothing again",
      vpm.kind_proposal_apply(kinds, data.get("unplaceable")) == [])
# The whole point of a proposal: it stops at an answer.
by_hand = vpm.Value(vpm.TYPE_CONTENT)
by_hand.chosen_by_hand = True
check("a Kind somebody picked is never written over",
      vpm.kind_proposal_apply({LOST: by_hand}, data.get("unplaceable")) == []
      and by_hand.get() == vpm.TYPE_CONTENT)
check("without a measurement nothing moves in either direction",
      vpm.kind_proposal_apply(kinds, None) == []
      and kinds[LOST].get() == vpm.TYPE_IGNORED)
check("but a measurement that can place it takes the proposal back",
      vpm.kind_proposal_apply(kinds, []) == [LOST]
      and kinds[LOST].get() == vpm.TYPE_CONTENT)
# The window has to go this way, not through a second copy of the rule.
source = open(SCRIPT, encoding="utf-8").read()
check("the window calls the proposal", "kind_proposal_apply(" in source
      and source.count("def kind_proposal_apply") == 1)
check("the refusal is written down once", source.count("unplaceable\"] = True")
      == 2 and source.count("def cannot_be_placed") == 1)

print("\n%s" % ("All good." if not error
                else "FAIL: %s" % ", ".join(error)))
sys.exit(1 if error else 0)
