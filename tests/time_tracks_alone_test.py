# -*- coding: utf-8 -*-
"""Multitrack without a picture: the tracks are laid against each other.

Two microphones in one room, one switched on later, and no camera. The
run used to refuse this for want of an axis. It now builds the axis out
of the tracks themselves, with the longest one as the reference, and
writes equally long files with the same start point -- what a multitrack
production needs. Without --multitrack nothing changes: the blocks of
one recording are joined and nothing is aligned.

And the log says one thing about --lufs on this path, not two: the
preflight used to name a target that the run then said does nothing.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, shutil, subprocess, sys, time, wave
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

began = time.time()
done = 0
error = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


#------------------------------------------------------------- Material

RATE = 48000
# Long enough for the drift measurement to have a lever arm. At 40
# seconds the two tracks came out 20 ms apart at the end, which is where
# the crossing voice starts to be audible; at 90 they agree to a
# millisecond, and the whole run still costs about a second.
LENGTH, LATE = 90.0, 3.0
# What the two tracks may be out by. The first is the rule
# verify_alignment names: from about 20 ms the crossing voice is heard
# as a second one. The second is the placement against the material
# itself, where nothing is audible and only the cut would notice.
APART_MS, PLACE_MS = 20.0, 50.0


def turns(seconds, seed):
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


def lag_ms(x, y):
    """How far *x* sits behind *y*, in milliseconds."""
    n = 1 << int(np.ceil(np.log2(len(x) + len(y))))
    c = np.fft.irfft(np.fft.rfft(x, n) * np.conj(np.fft.rfft(y, n)), n)
    k = int(np.argmax(np.abs(c)))
    return (k - n if k > n // 2 else k) * 1000.0 / RATE


def piece(x, from_s, until_s):
    return x[int(from_s * RATE):int(until_s * RATE)]


D = fixture("tracksalone")
shutil.rmtree(D, ignore_errors=True)
os.makedirs(D)
one = turns(LENGTH, 1)
two = turns(LENGTH, 2)
hiss = np.random.default_rng(9).normal(0, 0.0004, int(LENGTH * RATE))
# Each microphone hears its own voice loud and the other one quietly.
# Without that bleed there is nothing the two tracks share, and nothing
# to lay one against the other by.
HOST = one + 0.12 * two + hiss
GUEST = two + 0.12 * one + hiss
write(D + "/Host.wav", HOST)
# The second recorder was switched on later, so its file is shorter and
# begins in the middle of the conversation.
write(D + "/Guest.wav", GUEST[int(LATE * RATE):])
CALL = [sys.executable, SCRIPT, "--without-auphonic", "--no-metrics",
        "--no-speech-recognition", "--no-transcript-file"]


#-------------------------------------- 1. With --multitrack: an axis

print("1. Two recordings, no picture: they are laid against each other")
p = subprocess.run(CALL + ["--multitrack", "--out", D + "/run",
                           D + "/Host.wav", D + "/Guest.wav"],
                   capture_output=True, text=True, env=ENV)
log = (p.stdout or "") + (p.stderr or "")
check("no traceback", "Traceback" not in log,
      log[log.find("Traceback"):][:90])
check("nothing was sent to auphonic.com",
      "auphonic.com/api" not in log and "Uploading" not in log)
check("the run ends green", p.returncode == 0, str(p.returncode))
check("it no longer refuses for want of a picture",
      "needs pictures" not in log)
said = [line.strip() for line in log.splitlines()
        if "laid against each other" in line or "Reference:" in line]
print("   %s" % " | ".join(said[:2]))
check("it says there is no picture and the tracks carry the axis",
      any("laid against each other" in s for s in said))
check("the longest recording is the reference",
      any(s.startswith("Reference:") and "Host" in s for s in said),
      str(said[:2]))
made = sorted(f for f in os.listdir(D + "/run")) \
    if os.path.isdir(D + "/run") else []
print("   written: %s" % made)
# The measured trap: with --multitrack two people must never end up in
# one file, however alike their names look from outside.
check("one file per voice, and not the two glued into one",
      made == ["Guest_aligned.wav", "Host_aligned.wav"], str(made))
if len(made) != 2:
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(error or ["nothing was written"]))
    sys.exit(1)

host = vpm.decode_audio(D + "/run/Host_aligned.wav", rate=RATE)
guest = vpm.decode_audio(D + "/run/Guest_aligned.wav", rate=RATE)
print("   lengths: %.3f s and %.3f s" % (len(host) / float(RATE),
                                         len(guest) / float(RATE)))
check("both tracks are the same length to the sample",
      len(host) == len(guest),
      "%d against %d samples" % (len(host), len(guest)))
check("and they are as long as the two recordings cover together",
      abs(len(host) / float(RATE) - LENGTH) < 0.5,
      "%.3f s against %.1f" % (len(host) / float(RATE), LENGTH))
check("the later track has silence where it was not recording yet",
      float(np.max(np.abs(guest[:int((LATE - 0.3) * RATE)]))) < 0.02,
      "%.4f" % float(np.max(np.abs(guest[:int((LATE - 0.3) * RATE)]))))

# Where every track really sits, measured at both ends: an offset shows
# up at the front, a clock drift only at the back.
print("   what was measured against the material:")
worst_apart, worst_place = 0.0, 0.0
for from_s, until_s in ((4.0, 12.0), (LENGTH - 10.0, LENGTH - 2.0)):
    off_host = lag_ms(piece(host, from_s, until_s),
                      piece(HOST, from_s, until_s))
    off_guest = lag_ms(piece(guest, from_s, until_s),
                       piece(GUEST, from_s, until_s))
    print("     %5.1f to %5.1f s   Host %+7.2f ms   Guest %+7.2f ms"
          % (from_s, until_s, off_host, off_guest))
    worst_apart = max(worst_apart, abs(off_host - off_guest))
    worst_place = max(worst_place, abs(off_host), abs(off_guest))
check("the two tracks agree with each other at both ends",
      worst_apart <= APART_MS,
      "%.2f ms apart, allowed %.0f" % (worst_apart, APART_MS))
check("and both sit where the recording says they do",
      worst_place <= PLACE_MS,
      "%.2f ms off, allowed %.0f" % (worst_place, PLACE_MS))


#----------------------------------- 2. Without it: nothing has moved

print("\n2. Without --multitrack the blocks are joined, as before")
p = subprocess.run(CALL + ["--out", D + "/join",
                           D + "/Host.wav", D + "/Guest.wav"],
                   capture_output=True, text=True, env=ENV)
log = (p.stdout or "") + (p.stderr or "")
check("no traceback", "Traceback" not in log,
      log[log.find("Traceback"):][:90])
check("the run ends green", p.returncode == 0, str(p.returncode))
joined = sorted(f for f in os.listdir(D + "/join")) \
    if os.path.isdir(D + "/join") else []
print("   written: %s" % joined)
check("the joined files come out under their own names",
      joined == ["Guest_joined.wav", "Host_joined.wav"], str(joined))
check("no axis was built", "MEASURING THE TIME AXIS" not in log)
if joined == ["Guest_joined.wav", "Host_joined.wav"]:
    length = dict((f, vpm.sample_count(D + "/join/" + f) / float(vpm.SR))
                  for f in joined)
    print("   lengths: %s" % {f: round(s, 2) for f, s in length.items()})
    # The whole difference between the two modes in one number: joined,
    # the files keep the length they were recorded at.
    check("and they keep the length they were recorded at",
          abs(length["Host_joined.wav"] - LENGTH) < 0.2
          and abs(length["Guest_joined.wav"] - (LENGTH - LATE)) < 0.2,
          str(length))


#---------------------------------------- 3. Which track the axis is

print("\n3. The reference is the longest track, not the first")
tracks = [{"name": "Guest", "source": D + "/Guest.wav", "blocks": []},
          {"name": "Host", "source": D + "/Host.wav", "blocks": []}]
placed = vpm.measure_tracks_against_each_other(tracks)
check("both tracks found a place", len(placed) == 2, str(len(placed)))
by_name = dict((t["name"], t) for t in placed)
check("the longest one is the reference and sits at zero",
      by_name["Host"]["a"] == 0.0 and by_name["Host"]["b"] == 1.0,
      "a=%s b=%s" % (by_name["Host"]["a"], by_name["Host"]["b"]))
check("the later one is found where it was switched on",
      abs(-by_name["Guest"]["a"] - LATE) < 0.1,
      "%.3f s against %.1f" % (-by_name["Guest"]["a"], LATE))

#--------------------------- 4. One answer about --lufs, not two

# The preflight named a loudness target and eleven lines later the run
# said the target does nothing here, and both stood in one log. On this
# path the tracks leave as they were recorded -- a gain per track would
# put the voices out of balance, which is what the path exists to keep
# -- so the number only does something when it travels to auphonic.com.
print("\n4. With --lufs the log says one thing about it, not two")
p = subprocess.run(CALL + ["--multitrack", "--lufs", "-16",
                           "--out", D + "/loud",
                           D + "/Host.wav", D + "/Guest.wav"],
                   capture_output=True, text=True, env=ENV)
loud = (p.stdout or "") + (p.stderr or "")
check("the run ends green", p.returncode == 0, str(p.returncode))
target = [line.strip() for line in loud.splitlines()
          if line.strip().startswith("Loudness")]
does_nothing = [line.strip() for line in loud.splitlines()
                if "--lufs does nothing here" in line]
print("   preflight: %s" % (target[0][:100] if target else "-- nothing --"))
check("the preflight says what the target is", len(target) == 1,
      "%d lines beginning Loudness" % len(target))
check("the run says the number does nothing here",
      len(does_nothing) == 1, str(does_nothing[:2]))
check("and the preflight says so too rather than the opposite",
      bool(target) and "nothing is adjusted here" in target[0],
      "the run says the number does nothing, the preflight says %r"
      % (target[0][:70] if target else None))
check("the number itself still stands in the line",
      bool(target) and "-16 LUFS" in target[0],
      repr(target[0][:70]) if target else "no Loudness line at all")
# The other side of the rule: with a key the number reaches
# auphonic.com and is in force, so neither line may appear.
check("without --lufs neither line is printed",
      "--lufs does nothing here" not in log
      and not [x for x in log.splitlines()
               if "nothing is adjusted here" in x],
      "the run says the number does nothing while none was given")
check("and the one predicate governs both messages",
      vpm.lufs_does_nothing(vpm.build_argument_parser().parse_args(
          ["--multitrack", "--lufs", "-16", "x.wav"]), ()) is True,
      "lufs_does_nothing said no on the very path that prints it")

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
