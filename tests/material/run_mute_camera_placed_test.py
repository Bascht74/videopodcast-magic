# -*- coding: utf-8 -*-
"""A camera with no sound but a timecode is placed by it and handed over.

One real run, Sync only and --without-auphonic, over two recordings, a
camera whose sound they share, a mute camera with a timecode 1.48 s
before that camera's, and a mute one with none. In order: the run goes
through; the mute camera with a clock is written, and the handover
places it by that clock where its timecode says, and the log says
nothing was found in its sound; the one with neither is still left out.
Then the cameras alone: the mute one is handed over by its clock too.
"""
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
import json
import re
import subprocess
import tempfile
import threading
import time

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


# No output for this long and the run is stuck rather than slow: it
# writes a progress bar while it works, so silence is the sign.
STILL = 120.0
STEP = 0.25
# A bound for one ffmpeg over seconds of material.
ASK = 120.0


def run(argv):
    """Start the program and watch it: (code, what it said, stuck, seconds)."""
    kid = subprocess.Popen(argv, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           env=dict(os.environ, QT_QPA_PLATFORM="offscreen"))
    pieces = []

    def read():
        """Collect what the program writes until it closes the pipe."""
        while True:
            try:
                piece = os.read(kid.stdout.fileno(), 65536)
            except OSError:
                break
            if not piece:
                break
            pieces.append(piece)

    reader = threading.Thread(target=read)
    reader.daemon = True
    reader.start()
    started, last, seen, stuck = time.time(), time.time(), 0, False
    while kid.poll() is None:
        time.sleep(STEP)
        if len(pieces) != seen:
            seen, last = len(pieces), time.time()
        if time.time() - last > STILL:
            stuck = True
            kid.kill()
            break
    took = time.time() - started
    reader.join(10)
    kid.wait()
    text = b"".join(pieces).decode("utf-8", "replace")
    # The mark in front of a warning is for the window, not for a line.
    text = re.sub(re.escape(vpm.MARK) + "[a-z]", "", text)
    text = re.sub(r"\x1b\[[0-9;]*m", "", text).replace("\r", "\n")
    return kid.returncode, text, stuck, took


def make(argv, path):
    """Material made with ffmpeg; a precondition, not a judgement."""
    made = subprocess.run(["ffmpeg", "-v", "error"] + argv + [path, "-y"],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          timeout=ASK)
    assert made.returncode == 0 and os.path.exists(path), made.stdout
    return path


def picture(timecode):
    """ffmpeg's arguments for a picture with no sound, clock or none."""
    return (["-f", "lavfi", "-i",
             "testsrc=size=160x90:rate=25:duration=%g" % LENGTH, "-c:v",
             "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-an"]
            + (["-timecode", timecode] if timecode else []))


#------------------------------------------------------------- Material

HOME = tempfile.mkdtemp(prefix="vpm_mutecam_")
LENGTH = 2 * vpm.AXIS_MIN_WINDOW_S
FRAME = 1.0 / 25
# The tone in bursts of one uneven pattern, so the sound places both
# recordings against the camera they were taken out of.
BURSTS = [(0.6, 1.3), (1.9, 2.1), (2.9, 3.2), (3.7, 8.9), (9.6, 10.0),
          (10.8, 11.9), (12.3, 12.45), (13.4, 14.3), (15.1, 15.35),
          (16.2, 17.8), (18.5, 18.65), (19.3, 20.3), (21.0, 21.4),
          (21.9, 22.2)]
gate = "+".join("between(t,%g,%g)" % burst for burst in BURSTS)
HEARD = make(["-f", "lavfi", "-i",
              "testsrc=size=160x90:rate=25:duration=%g" % LENGTH,
              "-f", "lavfi", "-i",
              "aevalsrc='0.5*sin(2*PI*330*t)*(%s)':s=48000:d=%g"
              % (gate, LENGTH), "-c:v", "libx264", "-preset", "ultrafast",
              "-pix_fmt", "yuv420p", "-c:a", "aac", "-timecode",
              "18:55:06:12", "-shortest"],
             os.path.join(HOME, "GuestCam_C003.mov"))
# 18:55:05:00 against 18:55:06:12 at 25 frames: 1.48 s earlier.
MUTE = make(picture("18:55:05:00"), os.path.join(HOME, "WideCam_C001.mov"))
CLOCK_SAYS = -1.48
NEITHER = make(picture(None), os.path.join(HOME, "Jingle_C009.mov"))
# Two recorders, or Multitrack has one track and stops before the axis.
TAKEN = [make(["-i", HEARD, "-vn", "-c:a", "pcm_s16le"],
              os.path.join(HOME, name))
         for name in ("TASCAM_0001.wav", "ZOOM0001.wav")]
STEM = os.path.splitext(os.path.basename(MUTE))[0]
LOST = os.path.splitext(os.path.basename(NEITHER))[0]
OUT = os.path.join(HOME, "out")

#----------------------------------------------------------------- 1. Run

print("1. A mute camera with a clock and one without, beside recordings")
code, said, stuck, took = run([sys.executable, SCRIPT, "--project-type",
                               "sync", "--without-auphonic", "--multitrack",
                               "--out", OUT] + TAKEN + [HEARD, MUTE, NEITHER])
lines = [line.strip() for line in said.splitlines() if line.strip()]
check("a run with two mute cameras goes through",
      code == 0 and not stuck,
      "returned %r after %.1f s, stood still %s, last line %r"
      % (code, took, stuck, lines[-1] if lines else ""))

#------------------------------------------------ 2. The one with a clock

print("\n2. The mute camera with a timecode")
WRITTEN = os.path.join(OUT, STEM + "_audio.mov")
check("the mute camera with a timecode is written",
      os.path.exists(WRITTEN),
      "%s %s; in the folder: %s"
      % (os.path.basename(WRITTEN),
         "there" if os.path.exists(WRITTEN) else "missing",
         sorted(os.listdir(OUT)) if os.path.isdir(OUT) else "no folder"))
found = [os.path.join(OUT, f) for f in sorted(os.listdir(OUT))
         if f.endswith("_resolve.json")] if os.path.isdir(OUT) else []
cameras = {}
if len(found) == 1:
    with open(found[0], encoding="utf-8") as f:
        cameras = {c.get("camera"): c for c in
                   json.load(f).get("cameras") or []}
mine = cameras.get(STEM) or {}
check("and the handover places it by its clock, where its timecode says",
      mine.get("placed_by") == "clock"
      and abs(float(mine.get("offset") or 0.0) - CLOCK_SAYS) <= FRAME,
      "placed_by %r at %r, wanted clock at %.2f within %.2f; cameras %s; "
      "handover files %s" % (mine.get("placed_by"), mine.get("offset"),
                             CLOCK_SAYS, FRAME, sorted(cameras),
                             [os.path.basename(f) for f in found]))
nothing = re.escape(vpm.T('  Nothing was found in the sound for %s -- placed '
                          'by the timecode alone.').strip()
                    ).replace(re.escape("%s"), "(.*?)")
named = [n for m in (re.match(nothing, x) for x in lines) if m
         for n in m.group(1).split(", ")]
check("and the log says nothing was found in its sound",
      STEM in named, "the line names %s, wanted %r among them"
      % (named, STEM))

#--------------------------------------------------- 3. The one with none

print("\n3. The mute camera with no timecode")
skipped = vpm.T('  %s has no camera sound -- without it nothing can be '
                'aligned').strip() % os.path.basename(NEITHER)
check("a camera with neither sound nor timecode is still left out",
      LOST not in cameras and skipped in lines,
      "in the handover: %s; %r %s among the %d lines the run wrote"
      % (LOST in cameras, skipped, "found" if skipped in lines
         else "not found", len(lines)))

#------------------------------------------------- 4. The cameras alone

print("\n4. The same mute camera beside two cameras, no recordings")
SECOND = make(["-i", HEARD, "-c", "copy"],
              os.path.join(HOME, "PresenterCam_C002.mov"))
ALONE = os.path.join(HOME, "alone")
code, said, stuck, took = run([sys.executable, SCRIPT, "--project-type",
                               "sync", "--without-auphonic", "--multitrack",
                               "--out", ALONE, HEARD, SECOND, MUTE])
found = [os.path.join(ALONE, f) for f in sorted(os.listdir(ALONE))
         if f.endswith("_resolve.json")] if os.path.isdir(ALONE) else []
cameras = {}
if len(found) == 1:
    with open(found[0], encoding="utf-8") as f:
        cameras = {c.get("camera"): c for c in
                   json.load(f).get("cameras") or []}
mine = cameras.get(STEM) or {}
check("the cameras alone hand it over too, placed by its clock",
      code == 0 and mine.get("placed_by") == "clock"
      and abs(float(mine.get("offset") or 0.0) - CLOCK_SAYS) <= FRAME
      and bool(mine.get("file")),
      "returned %r; placed_by %r at %r, file %r, wanted clock at %.2f "
      "within %.2f; cameras %s; handover files %s"
      % (code, mine.get("placed_by"), mine.get("offset"),
         os.path.basename(mine.get("file") or ""), CLOCK_SAYS, FRAME,
         sorted(cameras), [os.path.basename(f) for f in found]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
