# -*- coding: utf-8 -*-
"""Multitrack without a picture: the tracks are laid against each other.

Two microphones in one room, the second switched on later and off
earlier, and no camera. The axis is built out of the tracks themselves,
with the longest one as the reference; the files come out equally long
and with one start point, so the shorter recording is padded at both
ends, and the run says how far apart the two recorders were. Without
--multitrack the blocks are joined and nothing is aligned, and the log
says one thing about --lufs on this path, not two.

What the tracks carry is asked before where they sit: a file that came
out empty measures as perfectly placed, so the judgements about the
placement rest on that one being answered first.

The last section puts a track ten milliseconds out on purpose, because
the run itself never does -- it comes out to a fraction of a
millisecond, and the straightening then has nothing to straighten.

Nothing may reach auphonic.com here, and that is watched rather than
read off the log. A run of its own gets a made-up key, so that
--without-auphonic has something to hold back, and a stand-in curl on
the search path writes down every call. Where it cannot be put there --
Windows starts no #!/bin/sh file -- no key is given and those two
judgements are left out rather than claimed.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import shutil, subprocess, sys, time, wave
import numpy as np
sys.path.insert(0, HERE)
from fixture_root import fixture

vpm = the_program.load()
# The one message this file reads out of the program is translated here,
# in the parent, and the parent's language is the shell's: the program
# skips LANG=C on purpose and asks the system, which on a German Mac
# answers German. The runs below are forced to English; this says the
# same for the process doing the reading, so a test started by hand
# judges the program and not the shell it was started from.
vpm.set_language("en")

os.environ.setdefault("VPM_NO_SPEAKER_SPLIT", "1")
# A made-up key, and the environment carries it too so that no run of
# this test ever reaches for the one in the keychain -- not even a copy
# with the barrier broken.
NOT_A_KEY = "not-a-key-only-a-test"
ENV = dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="en",
           VPM_SILENT="1", VPM_NO_UPDATE_CHECK="1",
           AUPHONIC_TOKEN=NOT_A_KEY)

began = time.time()
done = 0
error = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append("%s [%s]" % (name, extra or "no numbers"))


#------------------------------------------------------------- Material

RATE = 48000
# Long enough for the drift measurement to have a lever arm. At 40
# seconds the two tracks came out 20 ms apart at the end, which is where
# the crossing voice starts to be audible; at 90 they agree to half a
# millisecond, and the whole run still costs about three seconds.
#
# What this material does not carry is a clock that really runs fast:
# both recordings come off one sample grid, so the ninety-odd ppm the
# run measures and takes out is the measurement's own noise. The drift
# correction is therefore exercised here, not proved.
#
# LATE is how much later the second recorder was switched on, STOP how
# much earlier it was switched off. The early stop is what makes the
# window longer than that recording, and it is the only reason the
# program has to pad anything: with the second file running to the end,
# both came out the same length whether the padding worked or not --
# measured 2.9.2026, the apad filter taken out and all 27 judgements
# still green.
LENGTH, LATE, STOP = 90.0, 3.0, 2.0
# What the two tracks may be out by. The first is the rule
# verify_alignment names: from about 20 ms the crossing voice is heard
# as a second one. The second is the placement against the material
# itself, where nothing is audible and only the cut would notice.
APART_MS, PLACE_MS = 20.0, 50.0
# How much of the recording's own level a track on the axis has to carry
# where both recordings were running. It is the same sound, only shifted
# and resampled, so the answer is about one; half of it means half the
# sound has gone missing. Measured 2.9.2026: 0.95 for both tracks in
# both stretches -- the material is written a little below full scale,
# so the file comes back a shade quieter than the array it was made
# from -- against 0.00 for a track the placement wrote out as silence.
LEVEL_LEAST = 0.5
# Put ten milliseconds out on purpose in the last section. Well above
# the millisecond verify_alignment straightens from, well below the
# 250 ms it refuses as impossible.
OUT_MS = 10.0


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
    """How far *x* sits behind *y*, in milliseconds.

    Says nothing about whether the two have anything in common: over a
    silent piece every shift is as good as every other, the peak lands
    on the first sample, and the answer is a confident zero. So the
    level is asked separately before this is believed.
    """
    n = 1 << int(np.ceil(np.log2(len(x) + len(y))))
    c = np.fft.irfft(np.fft.rfft(x, n) * np.conj(np.fft.rfft(y, n)), n)
    k = int(np.argmax(np.abs(c)))
    return (k - n if k > n // 2 else k) * 1000.0 / RATE


def level(x):
    """How loud a piece is, as a plain root mean square."""
    return float(np.sqrt(np.mean(np.square(x)))) if len(x) else 0.0


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
# The second recorder was switched on later and off earlier, so its file
# begins in the middle of the conversation and stops before the end.
write(D + "/Guest.wav",
      GUEST[int(LATE * RATE):int((LENGTH - STOP) * RATE)])
CALL = [sys.executable, SCRIPT, "--without-auphonic", "--no-metrics",
        "--no-speech-recognition", "--no-transcript-file"]
# The two stretches the placement is read at: an offset shows up at the
# front, a clock drift only at the back. The back one stops short of
# where the second recorder switched off, so both lie inside both
# recordings and the level there can be compared with the material.
LOOKED_AT = ((4.0, 12.0), (LENGTH - 14.0, LENGTH - 6.0))


#---------------------------------------------- Watching for an upload

# curl is the one program that could reach auphonic.com, and the program
# calls it by name. A stand-in first on the search path writes down every
# call and refuses, so an attempt leaves a trace here -- and while it
# stands there nothing can leave the machine, whatever is broken.
BIN = os.path.join(D, "bin")
CURL_CALLS = os.path.join(D, "curl_calls.txt")
os.makedirs(BIN)
STANDIN = os.path.join(BIN, "curl")
with open(STANDIN, "w") as f:
    f.write("#!/bin/sh\nprintf '%s\\n' \"$*\" >> '" + CURL_CALLS
            + "'\nexit 1\n")
os.chmod(STANDIN, 0o755)
ENV["PATH"] = BIN + os.pathsep + ENV.get("PATH", "")


def curl_calls():
    """What the stand-in curl was called with, oldest first."""
    try:
        with open(CURL_CALLS) as f:
            return [x.strip() for x in f if x.strip()]
    except OSError:
        return []


# Whether the stand-in is really the curl a subprocess finds. Asked, not
# assumed: on Windows a #!/bin/sh file is not started at all, the real
# curl.exe answers, and a judgement resting on the stand-in would then be
# green without anything having been watched.
try:
    subprocess.run(["curl", "--version"], capture_output=True, text=True,
                   env=ENV)
except OSError:
    pass
WATCHED = curl_calls() == ["--version"]
open(CURL_CALLS, "w").close()


#-------------------------------------- 1. With --multitrack: an axis

print("1. Two recordings, no picture: they are laid against each other")
p = subprocess.run(CALL + ["--multitrack", "--out", D + "/run",
                           D + "/Host.wav", D + "/Guest.wav"],
                   capture_output=True, text=True, env=ENV)
# Kept under a second name as well: section 2 writes over `log`, and the
# last judgement of section 4 has to ask this run and not that one.
axis_log = log = (p.stdout or "") + (p.stderr or "")
check("no traceback", "Traceback" not in log,
      log[log.find("Traceback"):][:90])
check("the run ends green", p.returncode == 0, str(p.returncode))
said = [line.strip() for line in log.splitlines()
        if "laid against each other" in line or "Reference:" in line]
print("   %s" % " | ".join(said[:2]))
check("it says there is no picture and the tracks carry the axis",
      any("laid against each other" in s for s in said),
      "%d lines of the log speak of the axis: %s" % (len(said), said[:2]))
check("the longest recording is the reference",
      any(s.startswith("Reference:") and "Host" in s for s in said),
      str(said[:2]))
# The run measures the two recorders against each other on the bleed
# after writing them, and says what it found. That the measurement then
# works is the last section's business; this is only about the run doing
# it at all, because taking the call away leaves everything else here
# looking right.
head = vpm.T('\n  Check against the bleed -- reference is %s:')
head = head.split("%s")[0].strip()
bleed = [x.strip() for x in log.splitlines() if head in x]
pair = [x.strip() for x in log.splitlines()
        if "<->" in x and "Host" in x and "Guest" in x]
check("the run measures the two recorders against each other",
      len(bleed) == 1 and len(pair) == 1,
      "%d lines announce the check, %d say what it found: %s"
      % (len(bleed), len(pair), pair[:1]))
made = sorted(f for f in os.listdir(D + "/run")) \
    if os.path.isdir(D + "/run") else []
print("   written: %s" % made)
# The measured trap: with --multitrack two people must never end up in
# one file, however alike their names look from outside.
check("one file per voice, and not the two glued into one",
      made == ["Guest_aligned.wav", "Host_aligned.wav"], str(made))
# The measurements below need those two files, and nothing after this
# section does. So a run that did not get them goes on rather than
# stopping here: it is red already, and the other three sections still
# say where the fault reaches.
if made == ["Guest_aligned.wav", "Host_aligned.wav"]:
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
    # The other end, where the second recorder had already stopped: the
    # window reaches further than that recording, and what stands there
    # is what the program padded it with. A track that stops with the
    # recording has nothing there at all, so an empty piece is a
    # failure and not a quiet one -- np.max would throw on it.
    tail = guest[int((LENGTH - STOP + 0.3) * RATE):]
    loudest = float(np.max(np.abs(tail))) if len(tail) else -1.0
    check("the track that stopped early is padded out with silence",
          0.0 <= loudest < 0.02,
          "%d samples past the recording, loudest %.4f"
          % (len(tail), loudest))

    # Before anything is said about where the tracks sit: that they
    # carry the recording at all. A track written out as silence lines
    # up with everything -- the correlation below has no peak to find
    # and answers zero -- so this precondition stands ahead of the two
    # judgements that rest on it, and carries its own numbers.
    print("   what the tracks carry, against the material:")
    thinnest, thin_name = None, ""
    for from_s, until_s in LOOKED_AT:
        for name, made_track, source in (("Host", host, HOST),
                                         ("Guest", guest, GUEST)):
            was = level(piece(source, from_s, until_s))
            got = level(piece(made_track, from_s, until_s))
            share = got / was if was else 0.0
            print("     %5.1f to %5.1f s   %-6s %.4f of %.4f = %.2f"
                  % (from_s, until_s, name, got, was, share))
            if thinnest is None or share < thinnest:
                thinnest, thin_name = share, name
    # The name says what the floor really rules out. Half the level is
    # a long way from "the sound the recording has there", and a check
    # promising that would be read as one nobody has to repeat.
    check("neither track is empty or far below its recording's level",
          thinnest is not None and thinnest >= LEVEL_LEAST,
          "the thinnest is %s at %.2f of the recording's level, wanted "
          "%.2f" % (thin_name, thinnest if thinnest is not None else -1.0,
                    LEVEL_LEAST))

    # Where every track really sits, measured at both ends: an offset
    # shows up at the front, a clock drift only at the back.
    print("   what was measured against the material:")
    worst_apart, worst_place = 0.0, 0.0
    for from_s, until_s in LOOKED_AT:
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
else:
    print("   the measurements of this section want those two files; "
          "the sections after it still run")


#--------------------------- 2. The barrier, with something to hold

# A run of its own, because a key changes what the run above is: with
# one, --lufs is in force on this path and section 5 would have nothing
# left to ask. And without one, --without-auphonic holds nothing back --
# there is nothing to send, so the barrier is never reached and taking
# it away changes nothing. Measured 2.9.2026: the guard replaced by
# `if args.auphonic_key:` and every judgement of this file still green.
print("\n2. Even with a key, --without-auphonic lets nothing out")
if WATCHED:
    p = subprocess.run(CALL + ["--auphonic-api-key", NOT_A_KEY,
                               "--multitrack", "--out", D + "/keyed",
                               D + "/Host.wav", D + "/Guest.wav"],
                       capture_output=True, text=True, env=ENV)
    keyed_log = (p.stdout or "") + (p.stderr or "")
    keyed = sorted(f for f in os.listdir(D + "/keyed")) \
        if os.path.isdir(D + "/keyed") else []
    # Asked before the barrier is: a run that died on its way there
    # sends nothing either, and would look like a barrier holding. The
    # two tracks written and no traceback is as close as the outside
    # gets -- the barrier stands right behind them. What the run
    # returns is deliberately not part of it: a broken barrier ends the
    # run on the made-up key, and that is the barrier's news, not this
    # judgement's.
    check("the run with a key got as far as the barrier",
          keyed == ["Guest_aligned.wav", "Host_aligned.wav"]
          and "Traceback" not in keyed_log,
          "wrote %s%s" % (keyed, ", and a traceback"
                          if "Traceback" in keyed_log else ""))
    sent = curl_calls()
    # Only the calls that went to auphonic.com are this judgement's
    # business. It used to compare against no call at all, so any other
    # use of curl on this path -- a tool list, a version question --
    # turned the one guard this project has into the one nobody
    # believes any more.
    reached = [c for c in sent if "auphonic.com" in c]
    # The address, not the whole command line: the rest of it is a
    # temporary file of this machine, and the failure line is read on
    # machines that have no such file.
    going = [w for call in reached for w in call.split() if "://" in w]
    print("   calls to curl in both runs so far: %d" % len(sent))
    check("nothing reached auphonic.com although a key was given",
          reached == [], "%d of %d calls to curl went there: %s"
          % (len(reached), len(sent), going[:1]))
else:
    print("LEFT OUT: the stand-in curl is a #!/bin/sh file and this "
          "machine starts none of those, so no key was given and nothing "
          "watched whether a run reached auphonic.com.")


#----------------------------------- 3. Without it: nothing has moved

print("\n3. Without --multitrack the blocks are joined, as before")
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
axis = [x.strip() for x in log.splitlines() if "MEASURING THE TIME AXIS" in x]
check("no axis was built", "MEASURING THE TIME AXIS" not in log,
      "%d of %d lines of the log announce the axis: %s"
      % (len(axis), len(log.splitlines()), axis[:2]))
if joined == ["Guest_joined.wav", "Host_joined.wav"]:
    length = dict((f, vpm.sample_count(D + "/join/" + f) / float(vpm.SR))
                  for f in joined)
    print("   lengths: %s" % {f: round(s, 2) for f, s in length.items()})
    # The whole difference between the two modes in one number: joined,
    # the files keep the length they were recorded at.
    check("and they keep the length they were recorded at",
          abs(length["Host_joined.wav"] - LENGTH) < 0.2
          and abs(length["Guest_joined.wav"]
                  - (LENGTH - LATE - STOP)) < 0.2,
          "%s against %.1f s and %.1f"
          % (length, LENGTH, LENGTH - LATE - STOP))


#---------------------------------------- 4. Which track the axis is

print("\n4. The reference is the longest track, not the first")
tracks = [{"name": "Guest", "source": D + "/Guest.wav", "blocks": []},
          {"name": "Host", "source": D + "/Host.wav", "blocks": []}]
placed = vpm.measure_tracks_against_each_other(tracks)
check("both tracks found a place", len(placed) == 2, str(len(placed)))
by_name = dict((t["name"], t) for t in placed)
# Both names or neither: reading a track that was never placed ends the
# file in a traceback, and the sections after it would go unasked.
if "Host" in by_name and "Guest" in by_name:
    check("the longest one is the reference and sits at zero",
          by_name["Host"]["a"] == 0.0 and by_name["Host"]["b"] == 1.0,
          "a=%s b=%s" % (by_name["Host"]["a"], by_name["Host"]["b"]))
    check("the later one is found where it was switched on",
          abs(-by_name["Guest"]["a"] - LATE) < 0.1,
          "%.3f s against %.1f" % (-by_name["Guest"]["a"], LATE))
else:
    print("   only %s came back, so where they sit goes unasked"
          % sorted(by_name))

#--------------------------- 5. One answer about --lufs, not two

# The preflight named a loudness target and eleven lines later the run
# said the target does nothing here, and both stood in one log. On this
# path the tracks leave as they were recorded -- a gain per track would
# put the voices out of balance, which is what the path exists to keep
# -- so the number only does something when it travels to auphonic.com.
print("\n5. With --lufs the log says one thing about it, not two")
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
# The other side of the rule, and it has to be asked of the same path:
# the run of section 1 is --multitrack without --lufs, and there neither
# line may stand. Asked of the joined run instead it was true twice over
# -- no --lufs and no --multitrack -- and could not have gone red.
loose = [x.strip() for x in axis_log.splitlines()
         if "--lufs does nothing here" in x or "nothing is adjusted here" in x]
check("without --lufs neither line is printed", not loose,
      "%d such lines in the run without --lufs: %s" % (len(loose), loose[:2]))
check("and the one predicate governs both messages",
      vpm.lufs_does_nothing(vpm.build_argument_parser().parse_args(
          ["--multitrack", "--lufs", "-16", "x.wav"]), ()) is True,
      "lufs_does_nothing said no on the very path that prints it")


#-------------------- 6. A track put out of place is straightened

# Nothing above ever asks what happens when a track really sits out of
# place: the run comes out to a fraction of a millisecond, so the
# straightening finds nothing to straighten and could be taken away
# without a judgement moving. Here one track is placed ten milliseconds
# late on purpose, and the same straightening is asked to take it out.
# The drift is left out of it -- this is about the offset alone.
print("\n6. A track ten milliseconds out is straightened, not left")
BENT = D + "/bent"
os.makedirs(BENT)
bent = [{"name": "Host", "source": D + "/Host.wav",
         "axis": BENT + "/Host_axis.wav", "a": 0.0, "b": 1.0},
        {"name": "Guest", "source": D + "/Guest.wav",
         "axis": BENT + "/Guest_axis.wav",
         "a": -LATE - OUT_MS / 1000.0, "b": 1.0}]
for track in bent:
    vpm.place_track_on_axis(track["source"], track["axis"], track["a"],
                            track["b"], 0.0, LENGTH, False)
askew = lag_ms(piece(vpm.decode_audio(bent[1]["axis"], rate=RATE), 20.0, 28.0),
               piece(GUEST, 20.0, 28.0))
print("   put there: %+.2f ms" % askew)
# The material for the judgement, not the judgement: if the track did
# not come out where it was put, the run below says nothing about
# straightening and the line that follows would blame the wrong thing.
check("the track really went in ten milliseconds out",
      abs(askew - OUT_MS) <= 1.0,
      "%+.2f ms against the %+.1f it was placed at" % (askew, OUT_MS))
vpm.verify_alignment(bent, 0.0, LENGTH, drift_allowed=False)
left = lag_ms(piece(vpm.decode_audio(bent[1]["axis"], rate=RATE), 20.0, 28.0),
              piece(GUEST, 20.0, 28.0))
print("   left over: %+.2f ms" % left)
check("an offset of ten milliseconds is taken out, not left standing",
      abs(left) <= 1.0,
      "%+.2f ms still there of the %+.1f put in, allowed 1.00"
      % (left, OUT_MS))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
