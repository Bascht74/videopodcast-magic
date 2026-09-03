# -*- coding: utf-8 -*-
"""A file nothing can place is refused, not laid down at a guess.

Without the refusal the numbers of a failed alignment are handed back
and used. The rule holds only where there is no usable timecode: a file
with a clock is placed by it, and refusing that for an uncorrelated
sound throws away a file known to the millisecond. In order: what the
alignment admits, the rule itself, the sample points that are its
second opinion, camera against camera, a whole run, what the window
offers, and last the same question on the recording side, where
another caller has to read the same verdict.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import glob, importlib.util, shutil, subprocess, sys, time, wave
import numpy as np
sys.path.insert(0, HERE)
from fixture_root import fixture

spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
# The sentences the run prints are held against the ones this process
# asks the program for, so both sides have to speak the same language.
vpm.set_language("en")
# The program's own text. Two sections below count places in it -- how
# many gates ask the sample points, and how many set the refusal mark --
# and the first of them stands before the run, so it is read here once.
source = open(SCRIPT, encoding="utf-8").read()

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


def name_of(path):
    """The file's own name: a full path in a failure line hides the point."""
    return os.path.basename(path)


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
# And a recording of its own that fits nowhere -- steady noise again,
# but not the sound any camera carries, so no run can place it by
# accident. It goes in twice: as it stands, and with a clock in it.
write(D + "/Stray.wav",
      np.random.default_rng(5).normal(0, 0.2, int(CAM_LEN * RATE)))
# The recording that does fit and has no clock at all: what the good
# camera heard, copied rather than converted, because wave writes no
# bext chunk and a copy costs no process.
shutil.copy(D + "/plain.wav", D + "/Fits.wav")

# Two ffmpeg calls for everything: a process start is what the Windows
# builder charges for. The first gives the two recordings that need one
# their timecode -- wave cannot write a bext chunk. The second writes
# all three cameras, colour bars at ultrafast, since no frame is ever
# decoded.
CLOCK_IN_IT = ["-write_bext", "1", "-metadata",
               "time_reference=%d"
               % int(vpm.parse_timecode(REC_TC, 25.0) * RATE),
               "-c:a", "pcm_s16le"]
subprocess.run(
    ["ffmpeg", "-v", "error", "-y", "-i", D + "/plain.wav",
     "-i", D + "/Stray.wav", "-map", "0:a"] + CLOCK_IN_IT
    + [D + "/Rec.wav", "-map", "1:a"] + CLOCK_IN_IT
    + [D + "/Timed.wav"], check=True)
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
# The guard on one run of the program. Well under the limit run.sh puts
# on the whole test, so a run that hangs says which one it was instead
# of only that the test ran out of time. The three of them together take
# four seconds here; the builder is up to three times slower.
RUN_LIMIT_S = 300
STRAY, TIMED, FITS = D + "/Stray.wav", D + "/Timed.wav", D + "/Fits.wav"
# What a run calls a recording: the stem of its file.
STRAY_NAME, TIMED_NAME, FITS_NAME = "Stray", "Timed", "Fits"
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
      not found[GOOD][1].get("unplaceable"),
      "the mark is %r, envelopes %.3f against a floor of %.2f"
      % (found[GOOD][1].get("unplaceable"),
         found[GOOD][1].get("quality", 0.0), vpm.WEAK_MATCH))
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
          bool(st.get("unplaceable")),
          "the mark is %r, and the offset it would hand back is %+.3f s"
          % (st.get("unplaceable"), found[v][0]))


#--------------------------------------------------------- 2. The rule

print("\n2. The rule: the timecode decides whether refusing is allowed")
clock_tc = vpm.timecode_seconds(facts[CLOCK])
for_lost = vpm.cannot_be_placed(found[LOST][1], None, [audio_start])
for_clock = vpm.cannot_be_placed(found[CLOCK][1], clock_tc, [audio_start])
for_good = vpm.cannot_be_placed(found[GOOD][1], None, [audio_start])
check("no timecode anywhere, no place", for_lost is True,
      "%r, wanted True -- the mark is %r, own clock None, others [%r]"
      % (for_lost, found[LOST][1].get("unplaceable"), audio_start))
check("a timecode on both sides, and it stays", for_clock is False,
      "%r, wanted False -- the mark is %r, own clock %r s, others [%r]"
      % (for_clock, found[CLOCK][1].get("unplaceable"), clock_tc,
         audio_start))
check("an alignment that worked is never refused", for_good is False,
      "%r, wanted False -- the mark is %r, envelopes %.3f"
      % (for_good, found[GOOD][1].get("unplaceable"),
         found[GOOD][1].get("quality", 0.0)))
# A clock reading only says something next to a second one.
lone_tc = vpm.timecode_places_it(36000.0, [None, None])
paired_tc = vpm.timecode_places_it(36000.0, [None, 36004.0])
check("a lone timecode among files that have none places nothing",
      lone_tc is False,
      "36000.0 among [None, None] -> %r, wanted False" % lone_tc)
check("but one with a partner does", paired_tc is True,
      "36000.0 among [None, 36004.0] -> %r, wanted True" % paired_tc)


#------------------------------------ 2b. The sample points beside it

print("\n2b. The sample points are the second opinion at the camera gate")
st = {"quality": 0.44, "points": 234, "spread_ms": 10.91}
check("many sample points, close on the line, place the file",
      vpm.fit_places_it(st) is True,
      "%r from %d points at %.2f ms, against %d and %.1f"
      % (vpm.fit_places_it(st), st["points"], st["spread_ms"],
         vpm.FIT_POINTS_ENOUGH, vpm.FIT_SPREAD_MS))
few = {"quality": 0.44, "points": 49, "spread_ms": 1.0}
check("too few of them place nothing, however close they lie",
      vpm.fit_places_it(few) is False,
      "%r from %d points at %.2f ms, the floor is %d points"
      % (vpm.fit_places_it(few), few["points"], few["spread_ms"],
         vpm.FIT_POINTS_ENOUGH))
wide = {"quality": 0.44, "points": 234, "spread_ms": 15.1}
check("and enough of them place nothing when they scatter",
      vpm.fit_places_it(wide) is False,
      "%r from %d points at %.2f ms, the limit is %.1f ms"
      % (vpm.fit_places_it(wide), wide["points"], wide["spread_ms"],
         vpm.FIT_SPREAD_MS))
none = {"quality": 0.0, "points": 0, "spread_ms": 0.0}
check("no sample point places nothing, however tight the spread reads",
      vpm.fit_places_it(none) is False,
      "%r from %d points at %.2f ms"
      % (vpm.fit_places_it(none), none["points"], none["spread_ms"]))
nospread = {"quality": 0.44, "points": 234}
check("nor does one that never measured a spread",
      vpm.fit_places_it(nospread) is False,
      "%r from %d points and no spread at all"
      % (vpm.fit_places_it(nospread), nospread["points"]))
gates = source.count("and not fit_places_it(st)")
check("both gates ask it, the window's and the run's",
      gates == 2 and source.count("def fit_places_it") == 1,
      "%d gates ask it (wanted 2), %d definitions of the rule (wanted 1)"
      % (gates, source.count("def fit_places_it")))


#------------------------------------------------- 3. Two cameras alone

print("\n3. Camera against camera: the refused one leaves the axis")
ref, position = vpm.align_cameras([(v, facts[v]) for v in
                                   (GOOD, LOST, CLOCK)])
check("the camera that fits is the reference", ref[0] == GOOD,
      os.path.basename(ref[0]))
check("the one nothing can place is not on the axis",
      LOST not in position, str(sorted(map(os.path.basename, position))))
check("the one with a timecode still is", CLOCK in position,
      "Clock.mov on the axis %r, its timecode %r s, on the axis: %s"
      % (CLOCK in position, vpm.timecode_seconds(facts[CLOCK]),
         sorted(map(name_of, position))))


#------------------------------------------------------ 4. A whole run

print("\n4. A whole run: recording plus three cameras")
p = subprocess.run(
    [sys.executable, SCRIPT, "--without-auphonic", "--no-metrics",
     "--no-speech-recognition", "--no-transcript-file",
     "--out", D + "/run", REC, GOOD, LOST, CLOCK],
    capture_output=True, text=True, timeout=RUN_LIMIT_S, env=ENV)
log = (p.stdout or "") + (p.stderr or "")
check("no traceback", "Traceback" not in log,
      log[log.find("Traceback"):][:90] if "Traceback" in log else "")
went_out = [line.strip()[:70] for line in log.splitlines()
            if "auphonic.com/api" in line or "Uploading" in line]
check("nothing was sent to auphonic.com", not went_out,
      "%d lines name the service or an upload, wanted 0: %s"
      % (len(went_out), went_out[:2]))
check("the run ends non-zero, because one camera was left out",
      p.returncode == 1, str(p.returncode))
said = [line.strip() for line in log.splitlines()
        if "cannot be placed" in line]
print("   %s" % (said[0][:150] if said else "-- nothing said --"))
check("the run says one file cannot be placed", len(said) == 1,
      "%d lines" % len(said))
# The name stands at the front of that sentence and the way out at its
# end, so each is quoted from the end it lives at: cut from the wrong
# one and the failure line hides the very words being looked for.
head = said[0][:60] if said else "-- no line said it --"
tail = said[0][-95:] if said else "-- no line said it --"
check("and names the one that cannot", bool(said) and "Lost.mov" in said[0],
      "looked for 'Lost.mov' in %r" % head)
# Without a way out, and without saying whose job it is, the message is
# a dead end.
check("the message asks for a timecode",
      bool(said) and "timecode" in said[0].lower(),
      "looked for 'timecode' in %r" % tail)
check("and says it has to be set elsewhere",
      bool(said) and "another program" in said[0],
      "looked for 'another program' in %r" % tail)
named_clock = [line[:60] for line in said if "Clock.mov" in line]
check("the camera with the clock is not among the refused",
      not named_clock,
      "%d of %d refused lines name Clock.mov: %s"
      % (len(named_clock), len(said), named_clock[:1]))
made = dict((n, os.path.exists("%s/run/%s_audio.mov" % (D, n)))
            for n in ("Good", "Lost", "Clock"))
print("   written: %s" % made)
check("nothing was written for the refused camera", made["Lost"] is False,
      "Lost_audio.mov there %r, wanted False -- written: %s"
      % (made["Lost"], made))
check("the one with the clock was written all the same",
      made["Clock"] is True,
      "Clock_audio.mov there %r, wanted True -- written: %s"
      % (made["Clock"], made))
check("and so was the one that fits", made["Good"] is True,
      "Good_audio.mov there %r, wanted True -- written: %s"
      % (made["Good"], made))
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
check("and not the one with a timecode", "Clock.mov" not in lost,
      "with no place: %s, wanted Clock.mov not among them" % lost)

kinds = dict((v, vpm.Value(vpm.TYPE_CONTENT)) for v in (GOOD, LOST, CLOCK))
moved = vpm.kind_proposal_apply(kinds, data.get("unplaceable"))
check("the proposal moves exactly that one", moved == [LOST], str(moved))
check("and sets it to 'ignore this video'",
      kinds[LOST].get() == vpm.TYPE_IGNORED, kinds[LOST].get())
check("the others keep what they were",
      kinds[GOOD].get() == vpm.TYPE_CONTENT
      and kinds[CLOCK].get() == vpm.TYPE_CONTENT,
      "Good.mov %r and Clock.mov %r, wanted %r for both"
      % (kinds[GOOD].get(), kinds[CLOCK].get(), vpm.TYPE_CONTENT))
again = vpm.kind_proposal_apply(kinds, data.get("unplaceable"))
check("a second round changes nothing again", again == [],
      "moved %s, wanted []" % [name_of(x) for x in again])
# The whole point of a proposal: it stops at an answer.
by_hand = vpm.Value(vpm.TYPE_CONTENT)
by_hand.chosen_by_hand = True
kept = vpm.kind_proposal_apply({LOST: by_hand}, data.get("unplaceable"))
check("a Kind somebody picked is never written over",
      kept == [] and by_hand.get() == vpm.TYPE_CONTENT,
      "moved %s and the Kind is %r, wanted [] and %r"
      % ([name_of(x) for x in kept], by_hand.get(), vpm.TYPE_CONTENT))
unasked = vpm.kind_proposal_apply(kinds, None)
check("without a measurement nothing moves in either direction",
      unasked == [] and kinds[LOST].get() == vpm.TYPE_IGNORED,
      "moved %s and Lost.mov is %r, wanted [] and %r"
      % ([name_of(x) for x in unasked], kinds[LOST].get(), vpm.TYPE_IGNORED))
taken_back = vpm.kind_proposal_apply(kinds, [])
check("but a measurement that can place it takes the proposal back",
      taken_back == [LOST] and kinds[LOST].get() == vpm.TYPE_CONTENT,
      "moved %s and Lost.mov is %r, wanted ['Lost.mov'] and %r"
      % ([name_of(x) for x in taken_back], kinds[LOST].get(),
         vpm.TYPE_CONTENT))
# The window has to go this way, not through a second copy of the rule.
# The def line carries the name too, so it is taken off the count. Left
# in, it answered the question by itself and the check could not fall:
# every call site could go and the mention in the def line kept it green.
proposal_calls = (source.count("kind_proposal_apply(")
                  - source.count("def kind_proposal_apply("))
check("the window calls the proposal", proposal_calls >= 1
      and source.count("def kind_proposal_apply") == 1,
      "%d calls beside %d definitions, wanted at least 1 beside exactly 1"
      % (proposal_calls, source.count("def kind_proposal_apply")))
# Three gates give up and mark a file: the run's camera floor, the
# preview's camera floor, and a recording against a camera. One rule
# reads the mark, and there must stay only one.
check("the refusal is written down once", source.count("unplaceable\"] = True")
      == 3 and source.count("def cannot_be_placed") == 1,
      "%d places set the mark (wanted 3), %d definitions of the rule "
      "(wanted 1)"
      % (source.count("unplaceable\"] = True"),
         source.count("def cannot_be_placed")))


#------------------------------ 6. The recording side of the same rule

print("\n6. A recording: the same verdict, read by another caller")
_a, _b, stray_st = vpm.align_audio_to_video(STRAY, GOOD, 0)
check("a recording foreign to the camera is marked unplaceable",
      bool(stray_st.get("unplaceable")),
      "envelopes %.3f against %.2f, phase %.1f against %.1f"
      % (stray_st.get("quality", 0.0), vpm.WEAK_MATCH,
         stray_st.get("phase_sharp") or 0.0, vpm.PHASE_SHARP_ENOUGH))


def run_with(folder, *material):
    """One run over these files, against the camera that has a clock."""
    p = subprocess.run(
        [sys.executable, SCRIPT, "--without-auphonic", "--no-metrics",
         "--no-speech-recognition", "--no-transcript-file",
         "--out", D + "/" + folder] + list(material) + [GOOD],
        capture_output=True, text=True, timeout=RUN_LIMIT_S, env=ENV)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


# The whole sentence with the name taken out of it. Searched for rather
# than typed, so no English wording lives in the test.
SAYS_NO = vpm.no_place_message("").strip()
NOTHING_LEFT = vpm.T('\nNo audio track could be aligned -- there is nothing '
                     'to put on the axis.').strip()
alone_rc, alone_log = run_with("refused", STRAY)
both_rc, both_log = run_with("placed", TIMED, FITS)
whole = alone_log + both_log
check("neither run threw", "Traceback" not in whole,
      whole[whole.find("Traceback"):][:90] if "Traceback" in whole else "")
turned_away = [line.strip() for line in alone_log.splitlines()
               if SAYS_NO in line]
print("   %s" % (turned_away[0][:150] if turned_away
                 else "-- nothing said --"))
check("the recording nothing can place is refused", len(turned_away) == 1,
      "%d such lines" % len(turned_away))
check("and the refusal is the sentence the program keeps for it",
      bool(turned_away)
      and turned_away[0] == vpm.no_place_message(STRAY_NAME),
      (turned_away[0][:70] if turned_away else "--"))
check("with its only recording gone the run stops and says so",
      NOTHING_LEFT in alone_log, "looked for '%s'" % NOTHING_LEFT[:40])
check("and it ends non-zero instead of carrying on", alone_rc == 1,
      str(alone_rc))
# The second run: the same foreign sound, but with a clock in it, and
# beside it one that measures and has no clock at all. The clock is the
# first way and the sound the second, and either one is enough.
sent_away = [line.strip().split()[0] for line in both_log.splitlines()
             if SAYS_NO in line]
check("with a clock or a match, nothing is turned away", sent_away == [],
      str(sent_away))
laid_down = sorted(os.path.basename(f) for f in
                   glob.glob(D + "/placed/auphonic-tracks/final_*.wav"))
print("   written: %s" % laid_down)
check("the same sound with a clock is laid on the axis",
      any(TIMED_NAME in n for n in laid_down), str(laid_down))
check("and so is a recording that measures and has no clock",
      any(FITS_NAME in n for n in laid_down), str(laid_down))
check("that run carries both through to the end",
      both_rc == 0 and os.path.exists(D + "/placed/Good_audio.mov"),
      "returned %d, Good_audio.mov %s"
      % (both_rc, os.path.exists(D + "/placed/Good_audio.mov")))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
