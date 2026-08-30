# -*- coding: utf-8 -*-
"""Does a time window move the sound against the picture in Multitrack?

The simple path had exactly that fault: with an In and an Out point the
written sound slid against the picture by the distance between the start
of the recording and the start of the picture. In the material that
found it, four seconds; in a real recording that distance is never zero,
so the fault was never invisible -- it was only never looked for.

Multitrack is the path Sebastian actually runs, so the same question has
to be answered there, and answered by measurement rather than by reading
the code. It is built differently: the window is applied in seconds on
the common time axis, where every file already knows where it sits,
instead of each track being trimmed by a head count of its own. That
reads as safe. This test says whether it is.

The material is built so the question has an exact answer. The cameras
carry the room mix from CAM_LATE seconds into the recording onwards, so
picture time t is recording time t + CAM_LATE, and every speaker track
begins CAM_LATE before its own picture does. That distance is the whole
point of the fixture: were the picture to begin with the recording, the
fault being looked for would be zero by construction and a green run
would prove nothing.

Two runs are made on it, one without a window and one with an In and an
Out point, and the sound written into the camera files is held against
the original by cross correlation. The answer comes out in samples.

Nothing leaves the house: no key is given, --without-auphonic says so
out loud, and the test holds the run to it.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import json, re, shutil, subprocess, sys, wave
import numpy as np
sys.path.insert(0, HERE)
from fixture_root import fixture

# The same environment the suite gives every test, so a run by hand
# measures the same thing. The speaker separation is switched off: it
# fetches a machine-learning environment and is not what is asked here.
os.environ.setdefault("VPM_NO_SPEAKER_SPLIT", "1")
ENV = dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="en",
           VPM_SILENT="1", VPM_NO_UPDATE_CHECK="1",
           QT_QPA_PLATFORM="offscreen")

error = []


def check(name, ok, extra=""):
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


def tail(text, n=2):
    rows = [x.strip() for x in text.splitlines() if x.strip()]
    return (" | ".join(rows[-n:]))[:100]


#------------------------------------------------------------- Material

RATE = 48000
# 36 s, and not less. The run stops below a common window of 30 s, and
# the cameras start CAM_LATE late, so the window is LENGTH - CAM_LATE.
# At 36 that is 32 s: two over the barrier.
LENGTH = 36.0
# Where the picture starts inside the recording. This is the number the
# whole test hangs on: picture time t is recording time t + CAM_LATE.
CAM_LATE = 4.0
CAM_LEN = LENGTH - CAM_LATE
# The window, in picture time, given as a relative In and Out point --
# the common window begins at picture time 0, so +8 and +20 are picture
# seconds 8 and 20. Both speakers have a turn inside it and both have
# turns outside it, so a window that did nothing would be caught as
# surely as one that cut in the wrong place.
WIN_IN, WIN_OUT = 8.0, 20.0
# Turns in recording time, with a pause of at least a second around
# each. Speech-like noise, because the alignment lives on the envelope
# of speech; a steady tone would align by luck. Twelve of the 36 s are
# quiet, which is what keeps the speech detection's noise floor out of
# the neighbour's bleed.
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
    peak and the answer is exact to the sample.
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
# What the program was given is what the written tracks are held
# against, so the sources are read back rather than kept in memory.
src = {"Host": read(D + "/Host.wav"), "Guest": read(D + "/Guest.wav")}

# One ffmpeg call for both cameras, because a process start is what the
# Windows builder charges for. Colour bars at ultrafast: the run never
# decodes a video frame, it reads the packet times and copies the
# picture through, so the picture only has to exist.
#
# The -ss in front of each output is an output option and cuts that file
# alone: picture and sound of both cameras begin CAM_LATE into the
# recording. That is what makes picture time t equal recording time
# t + CAM_LATE, and it is the one thing this fixture may not lose.
subprocess.run(
    ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
     "smptebars=size=320x180:rate=25:duration=%.1f" % LENGTH,
     "-i", D + "/room.wav",
     "-ss", "%.2f" % CAM_LATE,
     "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "ultrafast",
     "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "-shortest",
     D + "/CamHost.mov",
     "-ss", "%.2f" % CAM_LATE,
     "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "ultrafast",
     "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "-shortest",
     D + "/CamGuest.mov"], check=True)

# The file format number is read out of the program rather than the
# program imported for it: importing 36000 lines to learn one integer
# costs a second and pulls a window toolkit in with it.
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
    p = subprocess.run(
        [sys.executable, SCRIPT, "--multitrack", "--without-auphonic",
         "--assign", D + "/assign.json", "--out", out, "--no-metrics",
         "--no-wide-edges"] + [str(x) for x in extra]
        + [D + "/Host.wav", D + "/Guest.wav",
           D + "/CamHost.mov", D + "/CamGuest.mov"],
        capture_output=True, text=True, timeout=1800, env=ENV)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


#-------------------------------------------------------------- The runs

# The run without a window is the reference point: it says where the
# sound sits when nothing was asked of it. The second run asks for a
# window and nothing else, so any difference between the two belongs to
# the window.
rc1, log1 = run(D + "/plain")
rc2, log2 = run(D + "/window", "--in-point", "+%d" % WIN_IN,
                "--out-point", "+%d" % WIN_OUT)

# One ffmpeg for everything the two runs wrote, because a process start
# is the expensive thing on the builder. Stream a:0 of each camera file
# is the speaker who was assigned to it.
WANT = [(folder, cam) for folder in ("plain", "window")
        for cam in ("CamHost", "CamGuest")]
here = [(f, c) for f, c in WANT if os.path.exists(D + "/" + f + "/" + c + ".mov")]
tracks = {}
call = ["ffmpeg", "-v", "error", "-y"]
for i, (folder, cam) in enumerate(here):
    tracks[(folder, cam)] = D + "/t_%s_%s.wav" % (folder, cam)
    call += ["-i", D + "/" + folder + "/" + cam + ".mov"]
for i, (folder, cam) in enumerate(here):
    # -ac 1: the written speaker tracks are stereo, and read back as
    # mono samples a stereo file is twice as long and correlates
    # against nothing.
    call += ["-map", "%d:a:0" % i, "-c:a", "pcm_s16le", "-ar", str(RATE),
             "-ac", "1", tracks[(folder, cam)]]
if here and subprocess.run(call, capture_output=True).returncode:
    # A file with fewer audio tracks than it should have would take the
    # one call down as a whole and every check with it. Then each track
    # pays for its own call and each check fails on its own account.
    for folder, cam in here:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i",
                        D + "/" + folder + "/" + cam + ".mov", "-map", "0:a:0",
                        "-c:a", "pcm_s16le", "-ar", str(RATE), "-ac", "1",
                        tracks[(folder, cam)]], capture_output=True)


def track(folder, cam):
    path = tracks.get((folder, cam))
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
          "auphonic.com/api" not in log and "Uploading" not in log)
check("the second run says it took the window",
      "Time window by hand" in log2,
      "" if "Time window by hand" in log2 else tail(log2))

print("\n2. Without a window the sound sits on its picture")
plain_at = {}
for cam in ("CamHost", "CamGuest"):
    check("%s was written" % cam,
          os.path.exists(D + "/plain/" + cam + ".mov"))
    x = track("plain", cam)
    check("%s keeps the whole picture" % cam,
          abs(len(x) / float(RATE) - CAM_LEN) < 0.05,
          "%.3f s of %.1f" % (len(x) / float(RATE), CAM_LEN))
    plain_at[cam] = begins_at(src[SPEAKER[cam]], x)
    check("%s: the sound starts where the picture starts" % cam,
          abs(plain_at[cam] - CAM_LATE) < FRAME,
          "begins at %.3f s of the recording, wanted %.3f"
          % (plain_at[cam], CAM_LATE))

print("\n3. With a window it still sits on its picture")
# This is the question the whole file exists for. The window moves the
# sound to another place in the picture; the piece that lands at picture
# time WIN_IN has to be the piece that was recorded then. Measured
# against the run without a window, so the answer is a difference
# between two measurements of the same material and no constant of the
# processing can hide inside it.
for cam in ("CamHost", "CamGuest"):
    check("%s was written" % cam,
          os.path.exists(D + "/window/" + cam + ".mov"))
    x = track("window", cam)
    check("%s keeps the whole picture" % cam,
          abs(len(x) / float(RATE) - CAM_LEN) < 0.05,
          "%.3f s of %.1f" % (len(x) / float(RATE), CAM_LEN))
    at = begins_at(src[SPEAKER[cam]], x)
    check("%s: the sound still belongs to the picture" % cam,
          abs(at - CAM_LATE) < FRAME,
          "the written track begins at %.3f s of the recording, wanted "
          "%.3f -- %+.0f ms out" % (at, CAM_LATE, (at - CAM_LATE) * 1000))
    check("%s: the window moved nothing against the run without one" % cam,
          abs(at - plain_at[cam]) < FRAME,
          "%+.0f ms against the run without a window"
          % ((at - plain_at[cam]) * 1000))

print("\n4. And the window really is a window")
# Without this a run that ignored the In and Out point altogether would
# pass part 3 with the best numbers in the file.
for cam in ("CamHost", "CamGuest"):
    heard = loud(track("window", cam))
    check("%s: nothing sounds before the In point" % cam,
          all(i >= WIN_IN - 1 for i in heard), str(heard[:4]))
    check("%s: nothing sounds after the Out point" % cam,
          all(i < WIN_OUT for i in heard), str(heard[-4:]))
    check("%s: there is sound inside the window" % cam,
          len(heard) >= 3, str(len(heard)))
    outside = loud(track("plain", cam))
    check("%s: and outside it there was sound before" % cam,
          any(i < WIN_IN - 1 for i in outside)
          or any(i >= WIN_OUT for i in outside), str(outside[:6]))

print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
