# -*- coding: utf-8 -*-
"""A whole multitrack run that finishes on this machine alone.

Measure the time axis, take the bleed out of the speech detection, mix,
cut by speaker, write the files and the handover for Resolve -- all of
it here, with nothing leaving the house. The run is started with
--without-auphonic, and the test holds the program to that: the log has
to say what is missing, and nothing may be uploaded.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, json, shutil, subprocess, sys, time, wave
import numpy as np
sys.path.insert(0, os.path.dirname(
    os.path.abspath(__file__)))
from fixture_root import fixture

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


D = fixture("localrun")
shutil.rmtree(D, ignore_errors=True)
os.makedirs(D)
# The program refuses a common range of sound and picture under 30
# seconds, and the second camera starts CAM_LATE late, so the window is
# LENGTH - CAM_LATE: at 34 that is 2.5 s over the barrier.
RATE, LENGTH, CAM_LATE = 48000, 34.0, 1.5
# Five turns of 5 s with at least 1 s of quiet around each, so a quarter
# of the material is quiet. Under a fifth quiet, each track's noise floor
# lands inside the neighbour's bleed and the threshold throws the bleed
# out by itself -- a build with the separation taken out then passes.
# 5 s also stays clear of MIN_EDIT_DURATION_S, under which a shot is
# merged away; nothing starts before CAM_LATE, where the window begins.
TURNS = {"Host": [(2, 7), (15, 20), (28, 33)],
         "Guest": [(8.5, 13.5), (21.5, 26.5)]}


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


host, guest = voice(TURNS["Host"], 1), voice(TURNS["Guest"], 2)
bleed = 10 ** (-8.0 / 20)            # under the 3:1 rule on purpose
noise = np.random.default_rng(9).normal(0, 0.0004, len(host))
write(D + "/Host.wav", host + bleed * guest + noise)
write(D + "/Guest.wav", guest + bleed * host + noise)
write(D + "/room.wav", 0.6 * host + 0.6 * guest + noise)
# Colour bars at the fastest preset: the run never decodes a video
# frame, it reads packet times and copies the picture through, so the
# picture only has to exist. One call writes both cameras -- the second
# is the first from CAM_LATE on, and the -ss in front of it is an output
# option that cuts that file alone.
subprocess.run(
    ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
     "smptebars=size=320x180:rate=25:duration=%.1f" % LENGTH,
     "-i", D + "/room.wav",
     "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
     "-preset", "ultrafast",
     "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "-shortest",
     D + "/CamHost.mov",
     "-ss", "%.2f" % CAM_LATE,
     "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
     "-preset", "ultrafast",
     "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "-shortest",
     D + "/CamGuest.mov"], check=True)

plan = {"format": vpm.FILE_FORMAT, "created_by": "test", "production": "WA",
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

OUT = D + "/out"
print("1. The run goes through without a key")
p = subprocess.run(
    [sys.executable, SCRIPT, "--multitrack", "--without-auphonic",
     "--assign", D + "/assign.json", "--out", OUT, "--no-metrics",
     "--no-speech-recognition", "--no-transcript-file",
     "--no-wide-edges", D + "/Host.wav", D + "/Guest.wav",
     D + "/CamHost.mov", D + "/CamGuest.mov"],
    capture_output=True, text=True, timeout=900,
    env=dict(os.environ, LANG="C", LC_ALL="C"))
out = (p.stdout or "") + (p.stderr or "")
check("return code 0", p.returncode == 0, str(p.returncode))
check("no traceback", "Traceback" not in out,
        out[out.find("Traceback"):][:90])
said = out.count("WITHOUT AUPHONIC.COM")
check("it says what is missing", said > 0,
        "%d mentions of WITHOUT AUPHONIC.COM in %d characters of log, "
        "wanted at least 1" % (said, len(out)))
api = out.count("auphonic.com/api")
sent = out.count("Uploading")
check("nothing was uploaded", api == 0 and sent == 0,
        "%d mentions of auphonic.com/api and %d of Uploading, wanted 0 and 0"
        % (api, sent))
measured = out.count("Bleed measured")
apart = out.count("Bleed not separable")
check("the bleed was measured", measured > 0,
        "%d mentions of Bleed measured and %d of Bleed not separable in %d "
        "characters of log, wanted at least 1" % (measured, apart, len(out)))

print("\n2. The files are there")
made = sorted(os.listdir(OUT)) if os.path.isdir(OUT) else []
for tail in ("_speakers.csv", "_cameracut.csv", "_resolve.json"):
    check("WA%s written" % tail, os.path.exists(OUT + "/WA" + tail),
          "wanted WA%s; the %d files in out are %s" % (tail, len(made), made))
for name in ("CamHost.mov", "CamGuest.mov"):
    check("%s written" % name, os.path.exists(OUT + "/" + name),
          "wanted %s; the %d files in out are %s" % (name, len(made), made))
tracks = (sorted(os.listdir(OUT + "/auphonic-tracks"))
          if os.path.isdir(OUT + "/auphonic-tracks") else [])
check("the mix is there",
        os.path.exists(OUT + "/auphonic-tracks/final_Full-Mix.wav"),
        "wanted final_Full-Mix.wav; the %d files in auphonic-tracks are %s"
        % (len(tracks), tracks))

print("\n3. The speakers were told apart")
rows = open(OUT + "/WA_speakers.csv", encoding="utf-8").read().splitlines()[1:]
found = {}
for line in rows:
    part = line.split(",")
    found[part[0]] = found.get(part[0], 0.0) + float(part[4])
print("   ", {k: round(v) for k, v in found.items()})
check("both speakers appear", set(found) == {"Host", "Guest"}, str(set(found)))
# 15 s of Host and 10 s of Guest are in the material.
check("Host about 15 s", 12 <= found.get("Host", 0) <= 18,
        str(round(found.get("Host", 0))))
check("Guest about 10 s", 7 <= found.get("Guest", 0) <= 13,
        str(round(found.get("Guest", 0))))
# Durations alone let a lot through. What the separation is for is that
# no microphone reports its neighbour, so how much of each speaker's
# reported speech falls in the other one's turns is measured. The csv
# counts from the common start, CAM_LATE into the material.
NEXT_TO = {"Host": "Guest", "Guest": "Host"}
foreign = {"Host": 0.0, "Guest": 0.0}
for line in rows:
    part = line.split(",")
    hour, minute, second = part[3].split(":")
    a = int(hour) * 3600 + int(minute) * 60 + float(second)
    b = a + float(part[4])
    for c, d in TURNS.get(NEXT_TO.get(part[0], ""), []):
        foreign[part[0]] = foreign.get(part[0], 0.0) + max(
            0.0, min(b, d - CAM_LATE) - max(a, c - CAM_LATE))
print("   ", {k: round(v, 1) for k, v in foreign.items()}, "of the other's turns")
check("neither track claims the other's turns",
        max(foreign.values()) <= 1.5,
        str({k: round(v, 1) for k, v in foreign.items()}))

print("\n4. And the cut alternates")
cut = open(OUT + "/WA_cameracut.csv", encoding="utf-8").read().splitlines()[1:]
cameras = [line.split(",")[1] for line in cut]
print("   ", len(cut), "shots:", cameras)
check("more than two shots", len(cut) > 2, str(len(cut)))
check("both cameras are used", set(cameras) == {"CamHost", "CamGuest"},
        str(set(cameras)))

print("\n5. The handover holds the same cut")
d = json.load(open(OUT + "/WA_resolve.json", encoding="utf-8"))
check("format stamped", d.get("format") == vpm.FILE_FORMAT,
        "%r in the file, wanted %r" % (d.get("format"), vpm.FILE_FORMAT))
check("cut in the file", len(d.get("cut") or []) == len(cut),
        "%d/%d" % (len(d.get("cut") or []), len(cut)))
# The track name is the speaker; the camera name stands beside it.
check("both cameras in the file",
        {cam.get("camera") for cam in (d.get("cameras") or [])}
        == {"CamHost", "CamGuest"},
        str([cam.get("camera") for cam in (d.get("cameras") or [])]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
