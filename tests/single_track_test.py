# -*- coding: utf-8 -*-
"""The simple path: one recording into the video files.

run_single_track_path is what runs when there are no separate speaker
tracks: one overall recording, aligned and written into the camera
files. It asks the question that costs the most when the answer is
wrong -- does the sound still sit against the picture it was recorded
with? The camera's sound is a known piece of the recording, so the
written track is held against the original and the offset comes out in
samples rather than impressions.

Beside that: a time window, a window outside the material, a camera
without sound, a recording without a camera, and a recorder that
stopped early. No key is given, so nothing is sent to auphonic.com.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import json, shutil, subprocess, sys, wave
import numpy as np
sys.path.insert(0, HERE)
from fixture_root import fixture

# The same environment the suite gives every test, so running this file
# by hand measures the same run. Speaker separation is off: with it on
# the run takes several times as long, wants a machine-learning
# environment, and separates something this test does not ask about.
os.environ.setdefault("VPM_NO_SPEAKER_SPLIT", "1")
ENV = dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="en",
           VPM_SILENT="1", VPM_NO_UPDATE_CHECK="1")

error = []


def check(name, ok, extra=""):
    print("  %-56s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


def tail(text, n=2):
    """The end of a run's output, for a check that missed a sentence."""
    rows = [x.strip() for x in text.splitlines() if x.strip()]
    return (" | ".join(rows[-n:]))[:80]


#------------------------------------------------------------- Material

RATE = 48000
# Long enough that the camera can start late and stop early and still
# leave a piece to align on: the alignment samples every two seconds and
# needs a handful of points with signal in both.
LENGTH = 34.0
# The whole point of the fixture: picture time t is recording time
# t + CAM_LATE, and every number below is checked against that.
CAM_LATE, CAM_LEN = 4.0, 26.0
# For the one question a single camera cannot ask: are two of them put
# down in the right places relative to each other? The second starts
# after the first and stops with it, so the first is the reference.
CAM2_LATE, CAM2_LEN = 9.0, 21.0
# A window inside the picture, in picture time.
WIN_IN, WIN_OUT = 8.0, 18.0
# The recorder that stopped early: a piece from the middle.
SHORT_FROM, SHORT_LEN = 6.0, 10.0
# Speech-like, because the alignment lives on speech pauses: a steady
# tone has no envelope to match and would align by luck. The pauses also
# make the window checks readable -- a silent second means it cut there.
TURNS = {"A": [(1, 6), (12, 17), (25, 30)], "B": [(7.5, 10.5), (19, 24)]}


def voice(turns, seed):
    rng = np.random.default_rng(seed)
    x = np.zeros(int(LENGTH * RATE))
    for a, b in turns:
        n = int((b - a) * RATE)
        env = 0.3 + 0.7 * np.abs(np.sin(np.linspace(0, 50, n)))
        x[int(a * RATE):int(a * RATE) + n] = rng.normal(0, 0.25, n) * env
    return x


def write(path, x):
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())


def read(path):
    with wave.open(path) as f:
        return np.frombuffer(f.readframes(f.getnframes()),
                             "<i2").astype(float)


def begins_at(reference, track):
    """Where in *reference* the first sample of *track* was taken from.

    Both are the same material, so the cross correlation has one clear
    peak and the answer is exact to the sample. A negative number means
    the track starts before the reference does, which is the case where
    a recorder stopped early and silence was written in front of it.
    """
    n = 1 << int(np.ceil(np.log2(len(reference) + len(track))))
    c = np.fft.irfft(np.fft.rfft(reference, n)
                     * np.conj(np.fft.rfft(track, n)), n)
    k = int(np.argmax(np.abs(c)))
    return (k - n if k > n // 2 else k) / float(RATE)


def loud(x, step=1.0):
    """Which seconds of a track carry sound, as a list of whole seconds."""
    n = int(step * RATE)
    return [i for i in range(int(len(x) / n))
            if float(np.sqrt(np.mean(x[i * n:(i + 1) * n] ** 2))) > 50]


D = fixture("singletrack")
shutil.rmtree(D, ignore_errors=True)
os.makedirs(D)
a, b = voice(TURNS["A"], 1), voice(TURNS["B"], 2)
noise = np.random.default_rng(9).normal(0, 0.0004, len(a))
whole = 0.7 * a + 0.7 * b + noise
write(D + "/Rec.wav", whole)
write(D + "/Short.wav", whole[int(SHORT_FROM * RATE):
                              int((SHORT_FROM + SHORT_LEN) * RATE)])
# Read back rather than kept: what the program was given is what the
# written tracks are held against.
rec = read(D + "/Rec.wav")

# One ffmpeg call for all the video files, because a process start is
# what the Windows builder charges for. The run never decodes a frame,
# so the picture only has to exist.
#
# The -ss and -t in front of an output cut that file alone, which is what
# makes the first camera begin CAM_LATE into the recording. The second
# takes the picture only -- a camera with no audio track at all.
subprocess.run(
    ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
     "smptebars=size=320x180:rate=25:duration=%.1f" % LENGTH,
     "-i", D + "/Rec.wav",
     "-ss", "%.2f" % CAM_LATE, "-t", "%.2f" % CAM_LEN,
     "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset",
     "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le",
     D + "/Cam.mov",
     "-t", "3", "-map", "0:v", "-c:v", "libx264", "-preset", "ultrafast",
     "-pix_fmt", "yuv420p", D + "/Mute.mov",
     # The third output is the second camera, later into both.
     "-ss", "%.2f" % CAM2_LATE, "-t", "%.2f" % CAM2_LEN,
     "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset",
     "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le",
     D + "/Cam2.mov"], check=True)


def run(*extra):
    """One run of the program on the simple path, and what it printed."""
    p = subprocess.run(
        [sys.executable, SCRIPT, "--without-auphonic", "--no-metrics"]
        + [str(x) for x in extra],
        capture_output=True, text=True, timeout=900, env=ENV)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


#-------------------------------------------------------------- The runs

# All six runs first, then one ffmpeg to decode everything they wrote:
# decoding after each run costs more process starts.
rc1, log1 = run("--out", D + "/plain", D + "/Rec.wav", D + "/Cam.mov")
rc2, log2 = run("--out", D + "/window", "--in-point", "+%d" % WIN_IN,
                "--out-point", "+%d" % WIN_OUT, D + "/Rec.wav",
                D + "/Cam.mov")
rc3, _ = run("--out", D + "/beyond", "--in-point", "+%d" % (LENGTH + 6),
             "--out-point", "+%d" % (LENGTH + 16), D + "/Rec.wav",
             D + "/Cam.mov")
rc4, log4 = run("--out", D + "/mute", D + "/Rec.wav", D + "/Mute.mov")
rc5, log5 = run("--out", D + "/alone", D + "/Rec.wav")
rc6, _ = run("--out", D + "/short", D + "/Short.wav", D + "/Cam.mov")
rc7, log7 = run("--out", D + "/two", D + "/Rec.wav", D + "/Cam.mov",
                D + "/Cam2.mov")

MADE = "/Cam_audio.mov"
WANTED = [("plain", 0), ("plain", 1), ("window", 0), ("beyond", 0),
          ("short", 0)]
# Files that are not there are left out rather than taking the call
# down: parts 4 and 5 have cases where no file is the right answer.
here = [f for f in ("plain", "window", "beyond", "short")
        if os.path.exists(D + "/" + f + MADE)]
want = [(f, s) for f, s in WANTED if f in here]
tracks = {}
call = ["ffmpeg", "-v", "error", "-y"]
for folder in here:
    call += ["-i", D + "/" + folder + MADE]
for i, (folder, stream) in enumerate(want):
    tracks[(folder, stream)] = D + "/t%d.wav" % i
    call += ["-map", "%d:a:%d" % (here.index(folder), stream),
             "-c:a", "pcm_s16le", "-ar", str(RATE), tracks[(folder, stream)]]
if want and subprocess.run(call, capture_output=True).returncode:
    # A file with fewer audio tracks than it should have takes the whole
    # call down, and every check with it, saying nothing about which file
    # was wrong. So that run pays for one call per track.
    for folder, stream in want:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i",
                        D + "/" + folder + MADE, "-map", "0:a:%d" % stream,
                        "-c:a", "pcm_s16le", "-ar", str(RATE),
                        tracks[(folder, stream)]], capture_output=True)


def track(folder, stream=0):
    """One audio track of a written file, or silence where none is."""
    path = tracks.get((folder, stream))
    return read(path) if path and os.path.exists(path) else np.zeros(RATE)


#----------------------------------------------------------- The answers

print("0. The material is still there")
# First, because every check below reads these files: one of them gone
# shows up as a traceback in a later part rather than as a finding here.
# The run writes beside the material and must never write over it or take
# it away -- measuring the loudness makes a sum file and deletes it again,
# and a short cut that lets "the sum" mean the recording deletes that.
for name, want in (("Rec.wav", LENGTH), ("Short.wav", SHORT_LEN),
                   ("Cam.mov", None), ("Cam2.mov", None),
                   ("Mute.mov", None)):
    there = os.path.exists(D + "/" + name)
    check("%s is still there" % name, there)
    if there and want is not None:
        held = len(read(D + "/" + name)) / float(RATE)
        check("and %s is as long as it was" % name, abs(held - want) < 0.02,
              "%.3f s, was %.3f" % (held, want))
if error:
    # No point measuring sound against material that is not there.
    print("\nFAIL: " + ", ".join(error))
    sys.exit(1)

print("\n1. The ordinary run: recording plus camera")
check("it goes through", rc1 == 0, str(rc1))
check("no traceback", "Traceback" not in log1,
      log1[log1.find("Traceback"):][:90])
check("nothing was sent to auphonic.com",
      "auphonic.com/api" not in log1 and "Uploading" not in log1)
check("the camera file was written under its own name",
      os.path.exists(D + "/plain" + MADE))
mix, cam = track("plain", 0), track("plain", 1)
check("the picture was not shortened",
      abs(len(mix) / float(RATE) - CAM_LEN) < 0.05,
      "%.3f s of %.1f" % (len(mix) / float(RATE), CAM_LEN))
check("the camera keeps its own sound beside the new track",
      len(loud(cam)) > 5 and "Camera Original" in log1,
      "%d loud seconds" % len(loud(cam)))
# The number this whole test exists for. The camera's sound is the
# recording from CAM_LATE on, so the track written beside it has to
# start at exactly that place in the recording. One frame at 25 fps is
# 40 ms; anything beyond that is visible on lips.
at = begins_at(rec, mix)
check("the new sound starts where the picture starts",
      abs(at - CAM_LATE) < 0.04,
      "begins at %.3f s of the recording, wanted %.3f" % (at, CAM_LATE))
check("and it sits on the camera's own sound",
      abs(begins_at(cam, mix)) < 0.04,
      "%+.0f ms against the camera track" % (begins_at(cam, mix) * 1000))
# What is thrown away has to be said, or a run that quietly dropped
# seconds of material looks like one that did the right thing -- and the
# amount, not only the fact.
left_out = [line for line in log1.splitlines() if "left out" in line]
check("the run says what it leaves out", bool(left_out),
      "" if left_out else "not in the log, which ends: " + tail(log1))
if left_out:
    said = left_out[0]
    want_front = "0:00:%02d" % CAM_LATE
    want_back = "0:00:%02d" % (LENGTH - CAM_LATE - CAM_LEN)
    check("and how much, at both ends",
          want_front in said and want_back in said,
          "%s -- wanted %s and %s" % (said.strip(), want_front, want_back))
check("the offset it measured is in the log", "Offset:" in log1,
      "" if "Offset:" in log1 else tail(log1))

print("\n2. The handover names what was written")
book = D + "/plain/singletrack_resolve.json"
check("a handover for Resolve is there", os.path.exists(book),
      str(sorted(os.listdir(D + "/plain"))
          if os.path.isdir(D + "/plain") else "no folder"))
if os.path.exists(book):
    d = json.load(open(book, encoding="utf-8"))
    cams = d.get("cameras") or []
    check("it names the written file, not the source",
          bool(cams) and os.path.abspath(cams[0].get("file") or "")
          == os.path.abspath(D + "/plain" + MADE),
          str(cams[0].get("file") if cams else None))
    check("it knows how long the picture is",
          abs(float(d.get("length_s") or 0) - CAM_LEN) < 0.05,
          str(d.get("length_s")))

print("\n3. A time window inside the picture")
win = track("window")
check("the window run goes through", rc2 == 0, str(rc2))
check("the picture stays whole", abs(len(win) / float(RATE) - CAM_LEN) < 0.05,
      "%.3f s" % (len(win) / float(RATE)))
heard = loud(win)
check("nothing sounds before the In point",
      all(i >= WIN_IN for i in heard), str(heard[:4]))
check("nothing sounds after the Out point",
      all(i < WIN_OUT for i in heard), str(heard[-4:]))
check("there is sound inside the window", len(heard) >= 5, str(len(heard)))
# The window moves the sound, and that is where it can lose the picture:
# what lands at picture time WIN_IN has to be what was recorded then.
at = begins_at(rec, win)
check("the sound in the window still belongs to the picture",
      abs(at - CAM_LATE) < 0.04,
      "the written track begins at %.3f s of the recording, wanted %.3f "
      "-- %.1f s out" % (at, CAM_LATE, at - CAM_LATE))
said = "time window" in log2.lower()
check("the run says it trimmed to the window", said,
      "" if said else "not in the log, which ends: " + tail(log2))

print("\n4. A time window that lies outside the material")
beyond = track("beyond")
# Refuse, clamp the window, write nothing: what this path does is its
# own business. Only one outcome is no answer at all -- a run that
# returns 0 and names a video file with no sound in it.
made = os.path.exists(D + "/beyond" + MADE)
check("a video it calls a result has sound in it",
      rc3 != 0 or not made or len(loud(beyond)) > 0,
      "return %d, file written %s, %d loud seconds"
      % (rc3, "yes" if made else "no", len(loud(beyond))))

print("\n5. What the path does when something is missing")
check("a camera without sound is refused, not written",
      rc4 != 0 and not os.path.exists(D + "/mute" + MADE), str(rc4))
said = "no camera sound" in log4
check("and it says why", said,
      "" if said else "not in the log, which ends: " + tail(log4))
check("a recording without a camera ends without work",
      rc5 == 0 and "nothing to do" in log5,
      "return %d, ends: %s" % (rc5, tail(log5, 1)))
check("and it writes no video for it",
      not os.path.isdir(D + "/alone")
      or not [x for x in os.listdir(D + "/alone") if x.endswith(".mov")])

print("\n6. A recorder that stopped before the camera did")
short = track("short")
check("the run goes through", rc6 == 0, str(rc6))
check("the picture stays whole",
      abs(len(short) / float(RATE) - CAM_LEN) < 0.05,
      "%.3f s" % (len(short) / float(RATE)))
# The short recording is SHORT_FROM into the material, so it belongs at
# picture time SHORT_FROM - CAM_LATE, with silence before and after it.
piece = read(D + "/Short.wav")
at = -begins_at(piece, short)
check("the short recording sits at its place in the picture",
      abs(at - (SHORT_FROM - CAM_LATE)) < 0.04,
      "at picture time %.3f s, wanted %.3f" % (at, SHORT_FROM - CAM_LATE))
heard = loud(short)
check("the rest of the picture is silent, not padded with noise",
      bool(heard) and max(heard) < SHORT_FROM - CAM_LATE + SHORT_LEN + 1,
      str(heard))

print("\n7. Two cameras, and where the handover puts them")
# With one camera an unmeasured 0.0 looks right, since the only camera
# is the zero of the axis. A handover that writes the offset left over
# after the cut to the camera's start -- zero by construction -- shows
# only here, with the two on top of each other.
check("the two-camera run goes through", rc7 == 0,
      str(rc7) + " " + tail(log7))
book2 = D + "/two/singletrack_resolve.json"
check("a handover is there", os.path.exists(book2),
      str(sorted(os.listdir(D + "/two")) if os.path.isdir(D + "/two")
          else "no folder"))
if os.path.exists(book2):
    cams = json.load(open(book2, encoding="utf-8")).get("cameras") or []
    where = dict((c.get("camera") or "", c.get("offset")) for c in cams)
    check("both cameras are in it", len(cams) == 2, str(sorted(where)))
    # What the handover promises: position in the file is programme time
    # minus this. So the camera that starts later in the recording stands
    # later on the axis, by exactly the difference of the two starts.
    two = sorted(where.values(), key=lambda x: (x is None, x))
    apart = (two[1] - two[0]) if len(two) == 2 and None not in two else None
    check("they stand apart by what separates their starts",
          apart is not None and abs(apart - (CAM2_LATE - CAM_LATE)) < 0.05,
          "%s apart, wanted %.1f s -- %s"
          % (("%.3f s" % apart) if apart is not None else "nothing",
             CAM2_LATE - CAM_LATE, where))
    check("neither of them was written as an unmeasured zero",
          len([x for x in two if x == 0.0]) <= 1, str(where))

print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
