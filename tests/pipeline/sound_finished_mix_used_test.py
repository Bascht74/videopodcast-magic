# -*- coding: utf-8 -*-
"""A finished mix given to a run is the Full-Mix, placed and as it came.

One run with two recordings, two cameras and a stereo mix made
elsewhere, which starts later than the recordings and carries a bed on
its right channel that no recording has. Asked of what was written: the
camera file's Full-Mix carries that bed at its own level and sits on the
camera's sound, the written file's own check says so without a caution,
the stored Full-Mix is the same, the handover names the finished mix and
it is nobody's voice. Alignment is measured here by a route of its own.
"""
PLATFORM_BOUND = True
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import the_program
SCRIPT = the_program.SCRIPT
import glob, json, math, subprocess, tempfile, time, wave
import numpy as np

os.environ.setdefault("VPM_NO_SPEAKER_SPLIT", "1")
ENV = dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="en",
           VPM_SILENT="1", VPM_NO_UPDATE_CHECK="1",
           QT_QPA_PLATFORM="offscreen")

began = time.time()
vpm = the_program.load()
vpm.set_language("en")
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


#------------------------------------------------------------- Material

RATE = 48000
LENGTH = 36.0
LATE = {"CamHost": 3.0, "CamGuest": 5.0}
TURNS = {"Host": [(4, 9), (16, 21), (27, 32)],
         "Guest": [(10, 14.5), (22.5, 26)]}
# The finished mix starts this far into the recordings, so it has to be
# placed, and carries a bed this loud on its right channel only.
MIX_LATE = 1.5
BED = 0.03


def voice(turns, seed):
    rng = np.random.default_rng(seed)
    x = np.zeros(int(LENGTH * RATE))
    for a, b in turns:
        n = int((b - a) * RATE)
        env = 0.3 + 0.7 * np.abs(np.sin(np.linspace(0, 50, n)))
        x[int(a * RATE):int(a * RATE) + n] = rng.normal(0, 0.25, n) * env
    return x


def write(path, x, channels=1):
    with wave.open(path, "wb") as f:
        f.setnchannels(channels); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())


D = os.path.join(tempfile.mkdtemp(prefix="vpm_run_"), "finishedmix")
os.makedirs(D)
host, guest = voice(TURNS["Host"], 1), voice(TURNS["Guest"], 2)
noise = np.random.default_rng(9).normal(0, 0.0004, len(host))
bleed = 10 ** (-8.0 / 20)
write(D + "/Host.wav", host + bleed * guest + noise)
write(D + "/Guest.wav", guest + bleed * host + noise)
write(D + "/room.wav", 0.6 * host + 0.6 * guest + noise)
k = int(MIX_LATE * RATE)
left = 0.5 * host[k:] + 0.5 * guest[k:]
right = left + BED * np.sin(2 * np.pi * 997 * np.arange(len(left)) / RATE)
both = np.empty(2 * len(left))
both[0::2], both[1::2] = left, right
MIX = D + "/ZOOM0004_LR.wav"
write(MIX, both, 2)
build = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
         "smptebars=size=320x180:rate=25:duration=%.1f" % LENGTH,
         "-i", D + "/room.wav"]
for cam in sorted(LATE):
    build += ["-ss", "%.2f" % LATE[cam], "-map", "0:v", "-map", "1:a",
              "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
              "yuv420p", "-c:a", "pcm_s16le", "-shortest",
              D + "/" + cam + ".mov"]
subprocess.run(build, check=True)

p = subprocess.run(
    [sys.executable, SCRIPT, "--without-auphonic", "--no-metrics",
     "--no-speech-recognition", "--no-transcript-file", "--out",
     D + "/out", D + "/Host.wav", D + "/Guest.wav", D + "/CamHost.mov",
     D + "/CamGuest.mov", "--finished-mix", MIX],
    capture_output=True, text=True, timeout=1800, env=ENV)
log = (p.stdout or "") + (p.stderr or "")


def track(path, index, pan=None):
    """One audio track of a file at 8 kHz: one channel, or all summed."""
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-map", "0:a:%d" % index]
    cmd += ["-af", pan] if pan else ["-ac", "1"]
    cmd += ["-ar", "8000", "-f", "f32le", "-"]
    got = subprocess.run(cmd, capture_output=True)
    return np.frombuffer(got.stdout, dtype="<f4").astype(float)


def bed_level(path, index=0):
    """How loud what differs between right and left is, in dB."""
    diff = track(path, index, "pan=mono|c0=c1-c0")
    rms = math.sqrt(float((diff ** 2).mean())) if len(diff) else 0.0
    return 20 * math.log10(max(rms, 1e-9))


def lag_ms(a, b):
    """Where b sits against a, by 10 ms loudness boxes, in ms."""
    def boxes(x):
        n = len(x) // 80
        return np.sqrt((x[:n * 80].reshape(n, 80) ** 2).mean(1))
    a, b = boxes(a), boxes(b)
    n = min(len(a), len(b))
    a, b = a[:n] - a[:n].mean(), b[:n] - b[:n].mean()
    return (int(np.argmax(np.correlate(a, b, "full"))) - (n - 1)) * 10


# The bed as it went in, measured the same way it is measured below.
WANT = 20 * math.log10(BED / math.sqrt(2))

print("1. The run")
check("the run with a finished mix returns 0", p.returncode == 0,
      "%d, ends: %s" % (p.returncode, " | ".join(log.splitlines()[-2:])))

print("\n2. The camera file")
CAMFILE = D + "/out/CamHost_audio.mov"
there = os.path.exists(CAMFILE)
have = bed_level(CAMFILE) if there else -180.0
check("the camera's Full-Mix carries the finished mix's bed",
      have > WANT - 6.0,
      "bed at %.1f dB, went in at %.1f dB" % (have, WANT))
check("at the level it came with: no gain and no limiter on it",
      abs(have - WANT) < 1.0,
      "bed at %.1f dB against %.1f dB going in" % (have, WANT))
shift = (lag_ms(track(CAMFILE, 3), track(CAMFILE, 0)) if there else 9999)
check("the Full-Mix sits on the camera's own sound",
      abs(shift) <= 20, "%+d ms against the camera's sound" % shift)
caution = vpm.T('   Caution: more than one frame')
said = vpm.T('  Check:           %s against the camera track %s ms '
             '(match %s)%s').split("%s")
lines = [x for x in log.splitlines() if said[0] in x and said[1] in x]
check("the written file's own check finds it in place",
      len(lines) == 2 and not any(caution in x for x in lines),
      " | ".join(x.strip() for x in lines)[:150] or "no check line")

print("\n3. The stored mix and the handover")
stored = sorted(glob.glob(D + "/out/*/final_Full-Mix*.wav"))
kept = bed_level(stored[0]) if stored else -180.0
check("the stored Full-Mix is the finished mix",
      abs(kept - WANT) < 1.0,
      "%d stored, bed at %.1f dB against %.1f dB" % (len(stored), kept, WANT))
handovers = sorted(glob.glob(D + "/out/*_resolve.json"))
d = json.load(open(handovers[0], encoding="utf-8")) if handovers else {}
check("the handover names the finished mix",
      [os.path.basename(x) for x in d.get("finished_mix") or ()]
      == [os.path.basename(MIX)],
      "names %r" % (d.get("finished_mix"),))
voices = sorted(s.get("name") for s in d.get("speakers") or ())
check("the finished mix is nobody's voice", voices == ["Guest", "Host"],
      "speakers %r -- wanted Guest and Host" % voices)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
