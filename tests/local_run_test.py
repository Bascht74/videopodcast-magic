# -*- coding: utf-8 -*-
"""#80: a whole multitrack run that finishes on this machine alone.

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
import importlib.util, json, shutil, subprocess, sys, wave
import numpy as np
sys.path.insert(0, os.path.dirname(
    os.path.abspath(__file__)))
from fixture_root import fixture

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []


def check(name, ok, extra=""):
    print("  %-54s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


D = fixture("localrun")
shutil.rmtree(D, ignore_errors=True)
os.makedirs(D)
# How long the material is, and why it is not shorter. The program stops
# with "the common range of sound and picture is only ... long" below 30
# seconds, and the second camera starts CAM_LATE late, so the window is
# LENGTH - CAM_LATE. At 34 the window is 32.5 s: 2.5 s over the barrier.
# It used to be 40 s, which cost the run a sixth more of everything it
# decodes without proving anything the 34 do not.
RATE, LENGTH, CAM_LATE = 48000, 34.0, 1.5
# Five turns, each at least 5 s. The camera cut merges anything under
# MIN_EDIT_DURATION_S = 3 s into the shot that follows, so a turn near
# that length would cost the "more than two shots" check its meaning.
# Measured with this material: shortest shot 5.8 s, so the margin is
# nearly a factor of two.
TURNS = {"Host": [(1, 7), (14, 20), (27, 33)],
         "Guest": [(8, 13), (21, 26)]}


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
# Colour bars and the fastest encoder setting, on purpose. The run never
# decodes a single video frame -- it reads the packet times to check the
# frame rate and copies the picture through with -c:v copy. Measured by
# logging every ffmpeg call of one run: not one of the 62 decodes video.
# So the picture only has to exist, and building it was the most
# expensive thing in this test: testsrc at the default preset cost 0.90 s
# of processor time per file, colour bars at ultrafast cost 0.22 s.
# Resolution and frame rate stay as they were -- a camera file with an
# odd frame rate would be a different test.
#
# One call, two files. The second camera is the first from CAM_LATE on,
# so one ffmpeg reads the room sound once and writes both outputs: the
# -ss in front of the second file is an output option and cuts that
# file alone. This is why it may be done in one call at all -- the two
# files differ in nothing but where they begin. Both come out byte for
# byte as the two calls made them in the sound, to the second in
# length, and one frame shorter in the picture, which nothing here
# reads. Measured: 0.135 s for the two calls, 0.077 s for the one, and
# one process start fewer -- and a process start is what the builder
# charges for. The count the suite prints went 87 -> 85 with it, which
# is two because that counter sees a subprocess.run once as a run and
# once again as the Popen inside it.
#
# That is all the building is worth, and it is worth writing down: of
# the 50 processes this test really starts, the material is one. The
# other 49 belong to the run, and no flag can take them away without
# taking a stage of the run with them.
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
     "--no-wide-edges", D + "/Host.wav", D + "/Guest.wav",
     D + "/CamHost.mov", D + "/CamGuest.mov"],
    capture_output=True, text=True, timeout=900,
    env=dict(os.environ, LANG="C", LC_ALL="C"))
out = (p.stdout or "") + (p.stderr or "")
check("return code 0", p.returncode == 0, str(p.returncode))
check("no traceback", "Traceback" not in out,
        out[out.find("Traceback"):][:90])
check("it says what is missing", "WITHOUT AUPHONIC.COM" in out)
check("nothing was uploaded", "auphonic.com/api" not in out
        and "Uploading" not in out)
check("the bleed was measured", "Bleed measured" in out, "")

print("\n2. The files are there")
for tail in ("_speakers.csv", "_cameracut.csv", "_resolve.json"):
    check("WA%s written" % tail, os.path.exists(OUT + "/WA" + tail))
for name in ("CamHost.mov", "CamGuest.mov"):
    check("%s written" % name, os.path.exists(OUT + "/" + name))
check("the mix is there",
        os.path.exists(OUT + "/auphonic-tracks/final_Full-Mix.wav"))

print("\n3. The speakers were told apart")
rows = open(OUT + "/WA_speakers.csv", encoding="utf-8").read().splitlines()[1:]
found = {}
for line in rows:
    part = line.split(",")
    found[part[0]] = found.get(part[0], 0.0) + float(part[4])
print("   ", {k: round(v) for k, v in found.items()})
check("both speakers appear", set(found) == {"Host", "Guest"}, str(set(found)))
# 18 s of Host and 10 s of Guest are in the material; the bands are as
# wide, relative to that, as they were for the 40 s version.
check("Host about 18 s", 14 <= found.get("Host", 0) <= 22,
        str(round(found.get("Host", 0))))
check("Guest about 10 s", 7 <= found.get("Guest", 0) <= 13,
        str(round(found.get("Guest", 0))))

print("\n4. And the cut alternates")
cut = open(OUT + "/WA_cameracut.csv", encoding="utf-8").read().splitlines()[1:]
cameras = [line.split(",")[1] for line in cut]
print("   ", len(cut), "shots:", cameras)
check("more than two shots", len(cut) > 2, str(len(cut)))
check("both cameras are used", set(cameras) == {"CamHost", "CamGuest"},
        str(set(cameras)))

print("\n5. The handover holds the same cut")
d = json.load(open(OUT + "/WA_resolve.json", encoding="utf-8"))
check("format stamped", d.get("format") == vpm.FILE_FORMAT)
check("cut in the file", len(d.get("cut") or []) == len(cut),
        "%d/%d" % (len(d.get("cut") or []), len(cut)))
# The track name is the speaker where one is assigned; the camera name
# stands beside it.
check("both cameras in the file",
        {cam.get("camera") for cam in (d.get("cameras") or [])}
        == {"CamHost", "CamGuest"},
        str([cam.get("camera") for cam in (d.get("cameras") or [])]))

print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
