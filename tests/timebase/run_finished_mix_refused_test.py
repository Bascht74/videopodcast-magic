# -*- coding: utf-8 -*-
"""A finished mix that cannot stand in for the mix is said, or stops the run.

Dry runs on two recordings and two cameras. In order: a file that is no
audio file is refused; without a picture the preflight stops the run,
and with --anyway the time axis does; a mix shorter than every camera is
a note before the axis and a silent stretch named on it; one whose sound
shares nothing with the cameras stops the run, and so does one that lies
wholly outside the In and Out point. Each is read off the run's own
words, taken from the catalogue.
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
import subprocess, tempfile, time, wave
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


def stereo(x):
    both = np.empty(2 * len(x))
    both[0::2], both[1::2] = x, x
    return both


D = os.path.join(tempfile.mkdtemp(prefix="vpm_run_"), "misfit")
os.makedirs(D)
host, guest = voice(TURNS["Host"], 1), voice(TURNS["Guest"], 2)
noise = np.random.default_rng(9).normal(0, 0.0004, len(host))
write(D + "/Host.wav", host + 0.4 * guest + noise)
write(D + "/Guest.wav", guest + 0.4 * host + noise)
write(D + "/room.wav", 0.6 * host + 0.6 * guest + noise)
together = 0.5 * host + 0.5 * guest
# Ten seconds of the mix, from 1.5 s into the recordings: it fits where
# it is, and ends long before any camera does.
SHORT = D + "/ZOOM0005_LR.wav"
write(SHORT, stereo(together[int(1.5 * RATE):int(11.5 * RATE)]), 2)
# Thirty seconds of noise nothing else heard.
ALIEN = D + "/ZOOM0006_LR.wav"
write(ALIEN, stereo(np.random.default_rng(77).normal(0, 0.2,
                                                     int(30 * RATE))), 2)
build = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
         "smptebars=size=320x180:rate=25:duration=%.1f" % LENGTH,
         "-i", D + "/room.wav"]
for cam in sorted(LATE):
    build += ["-ss", "%.2f" % LATE[cam], "-map", "0:v", "-map", "1:a",
              "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
              "yuv420p", "-c:a", "pcm_s16le", "-shortest",
              D + "/" + cam + ".mov"]
subprocess.run(build, check=True)
FILES = [D + "/Host.wav", D + "/Guest.wav", D + "/CamHost.mov",
         D + "/CamGuest.mov"]


def run(out, *words):
    """A dry run on this material and the words given; code and log."""
    p = subprocess.run(
        [sys.executable, SCRIPT, "--without-auphonic", "--dry-run",
         "--no-speech-recognition", "--out", D + "/" + out]
        + [str(w) for w in words],
        capture_output=True, text=True, timeout=1800, env=ENV)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def ends(text):
    return " | ".join(x.strip() for x in text.splitlines()[-2:])[:120]


def head(text):
    """The words of a line before its first number goes in."""
    return text.split("%s")[0]


HOMELESS = vpm.T('the finished mix takes the place of the mix in the '
                 'camera files, and without a video file there are none.')
SHORTER = vpm.T('the finished mix runs %s, shorter than every camera (the '
                'shortest %s): where it ends, the Full-Mix is silent.')
SILENT = vpm.T('  The finished mix leaves %s at the front and %s at the '
               'back of the window silent.')
NOWHERE = vpm.T('  The finished mix found no place on the time axis: it '
                'shares no sound with the cameras. The run stops rather '
                'than lay it anywhere.')
OUTSIDE = vpm.T('  The finished mix has nothing in the window from %s to '
                '%s: it lies from %s to %s. The run stops.')

print("1. Not an audio file")
rc, log = run("video", *(FILES + ["--finished-mix", D + "/CamHost.mov"]))
said = vpm.T('The finished mix has to be an audio file: %s') \
    % os.path.abspath(D + "/CamHost.mov")
check("a video file as the finished mix is refused",
      rc != 0 and said in log, "%d, ends: %s" % (rc, ends(log)))

print("\n2. No picture")
rc, log = run("alone", D + "/Host.wav", "--finished-mix", SHORT)
# Its own stop, not the axis's net under it, which says the same.
stopped = vpm.T('\nStopped before the first long step. With --anyway it '
                'runs regardless.').strip()
check("without a video file the preflight stops the run",
      rc == 1 and HOMELESS in log and stopped in log,
      "%d, the preflight's stop %s, ends: %s"
      % (rc, "said" if stopped in log else "not said", ends(log)))
rc, log = run("anyway", "--anyway", D + "/Host.wav", "--finished-mix",
              SHORT)
check("and past --anyway the time axis stops it",
      rc == 1 and log.count(HOMELESS) >= 2,
      "%d, said %d times, ends: %s" % (rc, log.count(HOMELESS), ends(log)))

print("\n3. Too short")
rc, log = run("short", *(FILES + ["--finished-mix", SHORT]))
check("a mix shorter than every camera is a note before the axis",
      rc == 0 and head(SHORTER) in log, "%d, ends: %s" % (rc, ends(log)))
check("and the axis names the stretch it leaves silent",
      head(SILENT) in log, "ends: %s" % ends(log))

print("\n4. Nothing in common")
rc, log = run("alien", *(FILES + ["--finished-mix", ALIEN]))
check("a mix whose sound shares nothing with the cameras stops the run",
      rc == 1 and NOWHERE in log, "%d, ends: %s" % (rc, ends(log)))

print("\n5. Outside the window")
rc, log = run("outside", *(FILES + ["--finished-mix", SHORT,
                                   "--in-point", "+20"]))
check("a mix wholly outside In and Out point stops the run",
      rc == 1 and head(OUTSIDE) in log, "%d, ends: %s" % (rc, ends(log)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
