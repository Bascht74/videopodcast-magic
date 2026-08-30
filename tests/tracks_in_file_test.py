# -*- coding: utf-8 -*-
"""Which audio tracks stand in a written camera file, counted and named.

A camera file carries the mix and the camera's own sound, and where
nobody was assigned it carries every recording on a line of its own as
well, so the edit can reach for one voice without importing anything
beside the video. Losing those single tracks changes no sentence the run
prints, so the question is put to the written file itself: how many
audio tracks are in it, and what is each one called.
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
# the common window is LENGTH minus the latest camera start.
LENGTH = 36.0
# Where each camera's picture starts inside the recording. None of them
# is zero, so no arithmetic in the run is tested against nothing.
LATE = {"CamHost": 3.0, "CamGuest": 5.0, "CamWide": 4.0}
# Turns with a pause of at least a second around each. Speech-like
# noise, because the alignment lives on the envelope of speech; a steady
# tone would align by luck.
TURNS = {"Host": [(4, 9), (16, 21), (27, 32)],
         "Guest": [(10, 14.5), (22.5, 26)]}


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


D = fixture("tracksinfile")
shutil.rmtree(D, ignore_errors=True)
os.makedirs(D)
host, guest = voice(TURNS["Host"], 1), voice(TURNS["Guest"], 2)
bleed = 10 ** (-8.0 / 20)            # under the 3:1 rule on purpose
noise = np.random.default_rng(9).normal(0, 0.0004, len(host))
write(D + "/Host.wav", host + bleed * guest + noise)
write(D + "/Guest.wav", guest + bleed * host + noise)
write(D + "/room.wav", 0.6 * host + 0.6 * guest + noise)

# One ffmpeg call for all three cameras, because a process start is what
# the Windows builder charges for. Colour bars at ultrafast: the run
# never decodes a video frame, it reads the packet times and copies the
# picture through, so the picture only has to exist.
build = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
         "smptebars=size=320x180:rate=25:duration=%.1f" % LENGTH,
         "-i", D + "/room.wav"]
for cam in sorted(LATE):
    build += ["-ss", "%.2f" % LATE[cam],
              "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
              "-preset", "ultrafast", "-pix_fmt", "yuv420p",
              "-c:a", "pcm_s16le", "-shortest", D + "/" + cam + ".mov"]
subprocess.run(build, check=True)

# The file format number is read out of the program rather than the
# program imported for it: importing 30000 lines to learn one integer
# costs a second and pulls a window toolkit in with it.
form = re.search(r"^FILE_FORMAT = (\d+)",
                 open(SCRIPT, encoding="utf-8").read(), re.M)
# CamWide is in the assignment as a camera and in nobody's track: that
# is the wide shot, and it is the case the counting exists for. It must
# come out with the mix and nothing else, or "more tracks is better"
# would pass for an answer.
plan = {"format": int(form.group(1)) if form else 3, "created_by": "test",
        "production": "TC",
        "tracks_of": [
            {"audio": D + "/Host.wav", "blocks": [D + "/Host.wav"],
             "speakers": "Host", "camera": D + "/CamHost.mov",
             "camera_audio": False},
            {"audio": D + "/Guest.wav", "blocks": [D + "/Guest.wav"],
             "speakers": "Guest", "camera": D + "/CamGuest.mov",
             "camera_audio": False}],
        "cameras": [{"video": D + "/" + cam + ".mov", "name": cam}
                    for cam in sorted(LATE)]}
with open(D + "/assign.json", "w", encoding="utf-8") as f:
    json.dump(plan, f)


def run(out, *extra):
    """One run on this material, and what it printed."""
    p = subprocess.run(
        [sys.executable, SCRIPT, "--without-auphonic", "--no-metrics",
         "--no-wide-edges", "--out", D + "/" + out]
        + [str(x) for x in extra],
        capture_output=True, text=True, timeout=1800, env=ENV)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


#-------------------------------------------------------------- The runs

rc = {}
log = {}
rc["one"], log["one"] = run("one", D + "/Host.wav", D + "/CamHost.mov")
rc["two"], log["two"] = run("two", D + "/Host.wav", D + "/Guest.wav",
                            D + "/CamHost.mov")
rc["nosingle"], log["nosingle"] = run(
    "nosingle", "--no-single-tracks", D + "/Host.wav", D + "/Guest.wav",
    D + "/CamHost.mov")
rc["assign"], log["assign"] = run(
    "assign", "--assign", D + "/assign.json", D + "/Host.wav",
    D + "/Guest.wav", *[D + "/" + cam + ".mov" for cam in sorted(LATE)])

MIX, CAM = "Full-Mix", "Camera Original"
# What each written file has to hold. Order is not part of it, but
# multiplicity is: four tracks of which two are the same one would be
# just as wrong as three.
WANTED = (
    ("one", "CamHost_audio.mov", [MIX, CAM]),
    ("two", "CamHost_audio.mov", [MIX, "Host", "Guest", CAM]),
    ("nosingle", "CamHost_audio.mov", [MIX, CAM]),
    ("assign", "CamHost.mov", ["Host", MIX, CAM]),
    ("assign", "CamGuest.mov", ["Guest", MIX, CAM]),
    ("assign", "CamWide.mov", [MIX, CAM]),
)


def names_in(path):
    """The names of the audio tracks in a file, in the order written.

    A track name in a MOV file lives in handler_name; the title tag
    ffprobe would rather show is not written into this container.
    """
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a",
                        "-show_entries", "stream_tags=handler_name",
                        "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return [x.strip() for x in p.stdout.splitlines() if x.strip()]


#----------------------------------------------------------- The answers

print("1. Every run goes through with nothing leaving the house")
for name in ("one", "two", "nosingle", "assign"):
    check("the %s run returns 0" % name, rc[name] == 0,
          "%d, ends: %s" % (rc[name], tail(log[name])))
    fell = log[name].find("Traceback")
    check("no traceback in the %s run" % name, fell < 0,
          log[name][fell:][:90] if fell >= 0 else "")
    check("nothing was uploaded in the %s run" % name,
          "auphonic.com/api" not in log[name]
          and "Uploading" not in log[name])

print("\n2. What the written files carry")
for folder, made, want in WANTED:
    path = D + "/" + folder + "/" + made
    there = os.path.exists(path)
    check("%s: %s was written" % (folder, made), there,
          "" if there else str(sorted(os.listdir(D + "/" + folder))
                               if os.path.isdir(D + "/" + folder)
                               else "no folder"))
    found = names_in(path) if there else []
    check("%s: %s holds %d audio tracks" % (folder, made, len(want)),
          len(found) == len(want),
          "%d: %s" % (len(found), ", ".join(found) or "none"))
    check("%s: %s holds the right ones" % (folder, made),
          sorted(found) == sorted(want),
          "has %s -- wanted %s" % (", ".join(found) or "none",
                                   ", ".join(want)))

print("\n3. A run nobody asked for multitrack does not call itself that")
# Two recordings and a camera go through the same machinery multitrack
# uses, and for a while said so in its headings. The word belongs to the
# switch: a reader who never typed it must not be told they are in a
# mode they did not choose.
heads = [line for line in log["two"].splitlines()
         if line.strip() and line[:1] not in " \t"]
named = [line.strip() for line in heads if "multitrack" in line.lower()]
check("no heading of the ordinary run says multitrack", not named,
      " | ".join(named)[:100])

print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
