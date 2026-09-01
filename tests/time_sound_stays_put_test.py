# -*- coding: utf-8 -*-
"""Does a time window move the sound against the picture in Multitrack?

The simple path had exactly that fault: with an In and an Out point the
written sound slid against the picture by the distance between the start
of the recording and the start of the picture. Multitrack applies the
window on the common time axis instead, which reads as safe. Two runs,
one without a window and one with, hold the sound written into the
camera files against the original by cross correlation.

With a window the camera is no longer written whole: it carries the
window and a second at each end, cut back to the key frame before that.
So the delivered file's first frame is not the camera's, and every
judgement here is put back on the recording's axis first -- read off the
camera's own sound, the one track that is cut together with the picture.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import json, re, shutil, subprocess, sys, time, wave
import numpy as np
sys.path.insert(0, HERE)
from fixture_root import fixture

# The same environment the suite gives every test, so a run by hand
# measures the same thing. Speaker separation is off: it fetches a
# machine-learning environment and is not the question here.
os.environ.setdefault("VPM_NO_SPEAKER_SPLIT", "1")
ENV = dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="en",
           VPM_SILENT="1", VPM_NO_UPDATE_CHECK="1",
           QT_QPA_PLATFORM="offscreen")

began = time.time()
done = 0
error = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


def tail(text, n=2):
    rows = [x.strip() for x in text.splitlines() if x.strip()]
    return (" | ".join(rows[-n:]))[:100]


#------------------------------------------------------------- Material

RATE = 48000
# 39 s, and not less: the run stops below a common window of 30 s, and
# the window here is LENGTH minus the later of the two camera starts.
LENGTH = 39.0
# Where each camera's picture starts inside the recording: picture time
# t is recording time t + LATE. The two are deliberately different and
# neither is zero -- with both cameras starting together, every part of
# the offset the program computes would be zero and test nothing.
LATE = {"CamHost": 4.0, "CamGuest": 7.0}
CAM_LEN = dict((cam, LENGTH - late) for cam, late in LATE.items())
# Where the common window begins in recording time: with the later
# camera, because that is the first moment every camera saw.
COMMON = max(LATE.values())
# The window, given as a relative In and Out point counting from the
# start of the common window; each camera sees it at that time minus its
# own LATE. Both speakers have a turn inside it and turns outside it, so
# a window that did nothing is caught as surely as one that cut wrong.
WIN_IN, WIN_OUT = 8.0, 20.0
# The two ends of that window in recording time -- the axis the material
# was written on, and the only one both cameras share. Every judgement
# about the window is made on it, never on seconds counted from the
# start of a delivered file: with a window that start is not the
# camera's any more, and a check counting from there would hold the
# window against itself.
IN_AT, OUT_AT = COMMON + WIN_IN, COMMON + WIN_OUT
# Turns in recording time, with a pause of at least a second around
# each. Speech-like noise, because the alignment lives on the envelope
# of speech and a steady tone would align by luck. The quiet keeps the
# speech detection's noise floor out of the neighbour's bleed.
TURNS = {"Host": [(5, 10), (17, 22), (29, 34)],
         "Guest": [(11, 15.5), (23.5, 28)]}


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

    Both hold the same material, so the cross correlation has one clear
    peak.
    """
    n = 1 << int(np.ceil(np.log2(len(reference) + len(track))))
    c = np.fft.irfft(np.fft.rfft(reference, n)
                     * np.conj(np.fft.rfft(track, n)), n)
    k = int(np.argmax(np.abs(c)))
    return (k - n if k > n // 2 else k) / float(RATE)


def loud(x, step=1.0):
    """Which whole seconds of a track carry sound."""
    n = int(step * RATE)
    return [i for i in range(int(len(x) / n))
            if float(np.sqrt(np.mean(x[i * n:(i + 1) * n] ** 2))) > 50]


D = fixture("mtwindow")
shutil.rmtree(D, ignore_errors=True)
os.makedirs(D)
host, guest = voice(TURNS["Host"], 1), voice(TURNS["Guest"], 2)
bleed = 10 ** (-8.0 / 20)            # under the 3:1 rule on purpose
noise = np.random.default_rng(9).normal(0, 0.0004, len(host))
write(D + "/Host.wav", host + bleed * guest + noise)
write(D + "/Guest.wav", guest + bleed * host + noise)
write(D + "/room.wav", 0.6 * host + 0.6 * guest + noise)
# The written tracks are held against what the program was given, so
# the sources are read back rather than kept in memory.
src = {"Host": read(D + "/Host.wav"), "Guest": read(D + "/Guest.wav")}
# What both cameras record, and therefore the picture's own clock: the
# camera keeps this track and it is cut with the picture, so where it
# sits in the recording says where the delivered picture begins.
room = read(D + "/room.wav")

# One ffmpeg call for both cameras, because a process start is what the
# Windows builder charges for. The -ss in front of each output is an
# output option and cuts that file alone, so picture and sound of each
# camera begin its own LATE in -- what this fixture may not lose.
build = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
        "smptebars=size=320x180:rate=25:duration=%.1f" % LENGTH,
        "-i", D + "/room.wav"]
for cam in ("CamHost", "CamGuest"):
    build += ["-ss", "%.2f" % LATE[cam],
             "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
             "-preset", "ultrafast", "-pix_fmt", "yuv420p",
             "-c:a", "pcm_s16le", "-shortest", D + "/" + cam + ".mov"]
subprocess.run(build, check=True)

# The file format number is read out of the program rather than the
# program imported for it: importing it to learn one integer costs a
# second and pulls a window toolkit in with it.
form = re.search(r"^FILE_FORMAT = (\d+)", open(SCRIPT, encoding="utf-8").read(),
                 re.M)
plan = {"format": int(form.group(1)) if form else 3, "created_by": "test",
        "production": "MW",
        "tracks_of": [
            {"audio": D + "/Host.wav", "blocks": [D + "/Host.wav"],
             "speakers": "Host", "camera": D + "/CamHost.mov",
             "camera_audio": False},
            {"audio": D + "/Guest.wav", "blocks": [D + "/Guest.wav"],
             "speakers": "Guest", "camera": D + "/CamGuest.mov",
             "camera_audio": False}],
        "cameras": [{"video": D + "/CamHost.mov", "name": "CamHost"},
                    {"video": D + "/CamGuest.mov", "name": "CamGuest"}]}
with open(D + "/assign.json", "w", encoding="utf-8") as f:
    json.dump(plan, f)


def run(out, *extra):
    """One Multitrack run on this material, and what it printed."""
    p = subprocess.run(
        [sys.executable, SCRIPT, "--multitrack", "--without-auphonic",
         "--no-speech-recognition", "--no-transcript-file",
         "--assign", D + "/assign.json", "--out", out, "--no-metrics",
         "--no-wide-edges"] + [str(x) for x in extra]
        + [D + "/Host.wav", D + "/Guest.wav",
           D + "/CamHost.mov", D + "/CamGuest.mov"],
        capture_output=True, text=True, timeout=1800, env=ENV)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


#-------------------------------------------------------------- The runs

# The run without a window is the reference point; the second asks for
# a window and nothing else, so any difference belongs to the window.
rc1, log1 = run(D + "/plain")
rc2, log2 = run(D + "/window", "--in-point", "+%d" % WIN_IN,
                "--out-point", "+%d" % WIN_OUT)

# One ffmpeg for everything the two runs wrote, because a process start
# is the expensive thing on the builder. A camera file carries a:0 the
# speaker assigned to it, a:1 the Full-Mix and a:2 the camera's own
# sound; the first and the last are what is measured here.
KINDS = (("spk", 0), ("cam", 2))
WANT = [(folder, cam) for folder in ("plain", "window")
        for cam in ("CamHost", "CamGuest")]
here = [(f, c) for f, c in WANT if os.path.exists(D + "/" + f + "/" + c + ".mov")]
tracks = {}
call = ["ffmpeg", "-v", "error", "-y"]
for folder, cam in here:
    call += ["-i", D + "/" + folder + "/" + cam + ".mov"]
for i, (folder, cam) in enumerate(here):
    for kind, stream in KINDS:
        tracks[(folder, cam, kind)] = D + "/t_%s_%s_%s.wav" % (folder, cam, kind)
        # -ac 1: the written speaker tracks are stereo, and read as mono
        # samples a stereo file is twice as long and correlates against
        # nothing.
        call += ["-map", "%d:a:%d" % (i, stream), "-c:a", "pcm_s16le",
                 "-ar", str(RATE), "-ac", "1", tracks[(folder, cam, kind)]]
if here and subprocess.run(call, capture_output=True).returncode:
    # A file with fewer audio tracks than it should have would take the
    # one call down and every check with it, so each track then pays
    # for its own call and each check fails on its own account.
    for folder, cam in here:
        for kind, stream in KINDS:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i",
                            D + "/" + folder + "/" + cam + ".mov",
                            "-map", "0:a:%d" % stream, "-c:a", "pcm_s16le",
                            "-ar", str(RATE), "-ac", "1",
                            tracks[(folder, cam, kind)]], capture_output=True)


def track(folder, cam, kind="spk"):
    path = tracks.get((folder, cam, kind))
    return read(path) if path and os.path.exists(path) else np.zeros(RATE)


SPEAKER = {"CamHost": "Host", "CamGuest": "Guest"}
# One frame at 25 fps is 40 ms. Anything past that is visible on lips.
FRAME = 0.04

#----------------------------------------------------------- The answers

print("1. Both runs go through with nothing leaving the house")
check("the run without a window returns 0", rc1 == 0, str(rc1))
check("the run with a window returns 0", rc2 == 0, str(rc2))
for name, log in (("without", log1), ("with", log2)):
    check("no traceback in the run %s a window" % name,
          "Traceback" not in log, log[log.find("Traceback"):][:90])
    check("nothing was uploaded in the run %s a window" % name,
          "auphonic.com/api" not in log and "Uploading" not in log,
          "%d mentions of auphonic.com/api and %d of Uploading in %d "
          "characters of log, wanted none"
          % (log.count("auphonic.com/api"), log.count("Uploading"), len(log)))
check("the second run says it took the window",
      "Time window by hand" in log2,
      "" if "Time window by hand" in log2 else tail(log2))

print("\n2. Without a window the sound sits on its picture")
plain_at, picture_at = {}, {}
for cam in ("CamHost", "CamGuest"):
    made = D + "/plain/" + cam + ".mov"
    check("%s was written" % cam, os.path.exists(made),
          "%d bytes, -1 for not there; the folder holds %s"
          % (os.path.getsize(made) if os.path.exists(made) else -1,
             sorted(os.listdir(D + "/plain"))
             if os.path.isdir(D + "/plain") else "no folder"))
    x = track("plain", cam)
    check("%s keeps the whole picture" % cam,
          abs(len(x) / float(RATE) - CAM_LEN[cam]) < 0.05,
          "%.3f s of %.1f" % (len(x) / float(RATE), CAM_LEN[cam]))
    plain_at[cam] = begins_at(src[SPEAKER[cam]], x)
    check("%s: the sound starts where the picture starts" % cam,
          abs(plain_at[cam] - LATE[cam]) < FRAME,
          "begins at %.3f s of the recording, wanted %.3f"
          % (plain_at[cam], LATE[cam]))
    # Part 3 reads the delivered picture's start off the camera's own
    # sound, because with a window the file no longer starts where the
    # camera did. Here, where the answer is known, that reading is held
    # against it -- otherwise part 3 rests on an unproved method.
    own = track("plain", cam, "cam")
    picture_at[("plain", cam)] = begins_at(room, own)
    check("%s: the camera's own sound says where the picture starts" % cam,
          abs(picture_at[("plain", cam)] - LATE[cam]) < FRAME,
          "%.1f s of camera sound beginning at %.3f s of the recording, "
          "wanted %.3f"
          % (len(own) / float(RATE), picture_at[("plain", cam)], LATE[cam]))

print("\n3. With a window it still sits on its picture")
# This is the question the whole file exists for: the piece that lands
# at the In point has to be the piece that was recorded then. The camera
# is cut down to the window now, so how much of it survives says nothing
# about the sound; what has to hold is that sound and picture were cut
# together. It is measured twice over, against the camera's own sound
# and against the run without a window, so no constant can hide in it.
for cam in ("CamHost", "CamGuest"):
    made = D + "/window/" + cam + ".mov"
    check("%s was written" % cam, os.path.exists(made),
          "%d bytes, -1 for not there; the folder holds %s"
          % (os.path.getsize(made) if os.path.exists(made) else -1,
             sorted(os.listdir(D + "/window"))
             if os.path.isdir(D + "/window") else "no folder"))
    x = track("window", cam)
    own = track("window", cam, "cam")
    at_pic = begins_at(room, own)
    picture_at[("window", cam)] = at_pic
    held = len(x) / float(RATE)
    check("%s: the delivered picture holds the whole window" % cam,
          at_pic <= IN_AT + FRAME and at_pic + held >= OUT_AT - FRAME,
          "the picture runs from %.3f to %.3f s of the recording and the "
          "window from %.1f to %.1f, read off %.1f s of camera sound"
          % (at_pic, at_pic + held, IN_AT, OUT_AT, len(own) / float(RATE)))
    at = begins_at(src[SPEAKER[cam]], x)
    check("%s: the sound sits on the delivered picture" % cam,
          abs(at - at_pic) < FRAME,
          "the sound begins at %.3f s of the recording and the picture at "
          "%.3f -- %+.0f ms out" % (at, at_pic, (at - at_pic) * 1000))
    moved = begins_at(track("plain", cam), x)
    cut = at_pic - picture_at[("plain", cam)]
    check("%s: the sound is the same the run without a window wrote" % cam,
          abs(moved - cut) < FRAME,
          "it was taken %.3f s into that run's track, and the window cut "
          "%.3f s off the front -- %+.0f ms out"
          % (moved, cut, (moved - cut) * 1000))

print("\n4. And the window really is a window")
# Without this a run that ignored the In and Out point altogether would
# pass part 3 with the best numbers in the file. The seconds come out of
# the delivered file, and that file no longer starts where the camera
# did -- so each one is put back on the recording's axis before it is
# judged. Counted from the file instead, the Out point check could not
# fall at all: the file begins at the In point and ends a second after
# the Out point. One second of slack on the In side, because a whole
# second is called loud as soon as part of it carries sound.
for cam in ("CamHost", "CamGuest"):
    at_pic = picture_at[("window", cam)]
    heard = [at_pic + i for i in loud(track("window", cam))]
    check("%s: nothing sounds before the In point" % cam,
          all(t >= IN_AT - 1 for t in heard),
          "the first loud seconds sit at %s of the recording, the In point "
          "at %.1f" % (["%.1f" % t for t in heard[:4]], IN_AT))
    check("%s: nothing sounds after the Out point" % cam,
          all(t < OUT_AT for t in heard),
          "the last loud seconds sit at %s of the recording, the Out point "
          "at %.1f" % (["%.1f" % t for t in heard[-4:]], OUT_AT))
    check("%s: there is sound inside the window" % cam,
          len(heard) >= 3, str(len(heard)))
    outside = [LATE[cam] + i for i in loud(track("plain", cam))]
    check("%s: and outside it there was sound before" % cam,
          any(t < IN_AT - 1 for t in outside) or any(t >= OUT_AT for t in outside),
          "the run without a window sounds at %s of the recording"
          % ["%.1f" % t for t in outside[:6]])

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
