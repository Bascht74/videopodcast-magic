# -*- coding: utf-8 -*-
"""With no clock on the reference, every camera is stamped by its place.

Three cameras hearing one pattern of tone bursts; the longest, the
reference, carries no timecode, one carries a clock three seconds off
what the sound says, one none. One whole run, --without-auphonic, and
then the written camera files are asked: each carries the timecode of
its measured place, counted from 00:00:00 at the first frame any camera
shows -- the one with the wrong clock too, never its own reading.
"""
PLATFORM_BOUND = True
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import the_program
SCRIPT = the_program.SCRIPT
vpm = the_program.load()
vpm.set_language("en")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# A bound for the run and for each ffmpeg, never reached when they work;
# it only turns a run that never comes back into a line saying so.
LONGEST = 600
HOME = tempfile.mkdtemp(prefix="vpm_stampplace_")
BURSTS = [(0.6, 1.3), (1.9, 2.1), (2.9, 3.2), (3.7, 8.9), (9.6, 10.0),
          (10.8, 11.9), (12.3, 12.45), (13.4, 14.3), (15.1, 15.35),
          (16.2, 17.8), (18.5, 18.65), (19.3, 20.3), (21.0, 21.4),
          (21.9, 22.2), (23.0, 24.6), (25.3, 25.5), (26.1, 27.4),
          (28.0, 28.3), (29.1, 30.6), (31.2, 31.5), (32.4, 34.0)]
# Where each camera's first frame sits in the reference's time, and so
# the stamp it is owed at 25 frames a second.
WANTED = {"WideCam_C001": "00:00:00:00", "GuestCam_C002": "00:00:02:00",
          "PresenterCam_C003": "00:00:06:00"}


def made(argv, path):
    """A file made with ffmpeg; a precondition, not a judgement."""
    answer = subprocess.run(["ffmpeg", "-v", "error"] + argv + [path, "-y"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            timeout=LONGEST)
    assert answer.returncode == 0 and os.path.exists(path), answer.stdout
    return path


TONE = made(["-f", "lavfi", "-i", "aevalsrc='0.5*sin(2*PI*330*t)*(%s)'"
             ":s=48000:d=36" % "+".join("between(t,%g,%g)" % b
                                         for b in BURSTS)],
            os.path.join(HOME, "bursts.wav"))


def camera(name, late, length, clock):
    """A camera hearing the pattern from *late* s on, with or without a clock."""
    return made(["-f", "lavfi", "-i", "testsrc=size=160x90:rate=25:"
                 "duration=%g" % length, "-ss", "%g" % late, "-i", TONE,
                 "-t", "%g" % length, "-c:v", "libx264", "-preset",
                 "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac",
                 "-ar", "48000"] + (["-timecode", clock] if clock else []),
                os.path.join(HOME, name + ".mov"))


CAMERAS = [camera("WideCam_C001", 0.0, 34.0, None),
           camera("GuestCam_C002", 2.0, 26.0, "10:00:05:00"),
           camera("PresenterCam_C003", 6.0, 24.0, None)]
TRACK = made(["-i", TONE, "-t", "34"], os.path.join(HOME, "Room_T01.wav"))


def stamp_of(path):
    """The timecode a written file carries, or '' where it has none."""
    answer = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format_tags=timecode:stream_tags=timecode", "-of",
         "default=nw=1:nk=1", path], capture_output=True, text=True)
    found = [x.strip() for x in answer.stdout.splitlines() if x.strip()]
    return found[0] if found else ""


print("1. One whole run, the reference without a clock")
OUT = os.path.join(HOME, "out")
try:
    answer = subprocess.run(
        [sys.executable, SCRIPT, "--without-auphonic",
         "--no-speech-recognition", "--no-transcript-file", "--no-metrics",
         "--out", OUT, TRACK] + CAMERAS,
        capture_output=True, text=True, timeout=LONGEST,
        env=dict(os.environ, QT_QPA_PLATFORM="offscreen"))
    code, said = answer.returncode, answer.stdout + answer.stderr
except subprocess.TimeoutExpired:
    code, said = -1, ""
lines = [x for x in re.sub(r"\x1b\[[0-9;]*m", "", said).splitlines()
         if x.strip()]
written = dict((name, os.path.join(OUT, name + "_audio.mov"))
               for name in WANTED)
there = sorted(n for n, p in written.items() if os.path.exists(p))
check("the run goes through and writes every camera",
      code == 0 and there == sorted(WANTED),
      "returned %r, written %s, the last line %r"
      % (code, there, lines[-1] if lines else ""))

print("\n2. The stamps the written files carry")
got = dict((n, stamp_of(p)) for n, p in written.items()
           if os.path.exists(p))
print("   %s" % ", ".join("%s %s" % (n, got.get(n)) for n in sorted(WANTED)))
check("the reference is stamped 00:00:00:00, though it has no clock",
      got.get("WideCam_C001") == WANTED["WideCam_C001"],
      "stamped %r, wanted %r" % (got.get("WideCam_C001"),
                                 WANTED["WideCam_C001"]))
check("a camera with a wrong clock is stamped by its measured place",
      got.get("GuestCam_C002") == WANTED["GuestCam_C002"],
      "stamped %r, wanted %r, its own clock reading 10:00:05:00"
      % (got.get("GuestCam_C002"), WANTED["GuestCam_C002"]))
check("and one without a clock by its measured place too",
      got.get("PresenterCam_C003") == WANTED["PresenterCam_C003"],
      "stamped %r, wanted %r" % (got.get("PresenterCam_C003"),
                                 WANTED["PresenterCam_C003"]))

shutil.rmtree(HOME, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
