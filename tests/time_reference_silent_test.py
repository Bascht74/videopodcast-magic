# -*- coding: utf-8 -*-
"""The camera everything else is measured against reports no measurement.

One camera is the reference: the others are laid against it, and it
sits at zero by definition. Its block of the log nevertheless carried
the same clock line as the rest -- "+0.00 ppm (+/- 0.00), residual
spread 0.0 ms, 0 of 0 points" -- which reads like a measurement that
came out at nothing and is in truth no measurement at all.

One run over material made here, without auphonic.com and without
speech recognition: two cameras sharing one pattern of tone bursts, the
second rolling later, and two recordings taken out of the first. The
log is read afterwards: which camera the run called the reference,
what its block says about the clock, and what the block of the camera
the sound measured says.

The limit of the method: nothing here is a claim about where the axis
landed -- only about which lines stand in whose block.
"""
import os
import sys
import time
import shutil
import tempfile
import subprocess
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


def finish():
    """The one way out: the count, the verdict, the return code."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


# How long the run may take. Far above what it needs here, and it only
# ever ends the test with a line saying the run never came back.
LONGEST = 900

HOME = tempfile.mkdtemp(prefix="vpm_reference_")
LENGTH = 2 * vpm.AXIS_MIN_WINDOW_S
# The tone in bursts of one uneven pattern, so the sound can measure one
# camera against the other; the second hears it from this far in. No
# timecode on either: a clock would place a camera the sound could not,
# and a camera its clock placed was measured against nothing.
BURSTS = [(0.6, 1.3), (1.9, 2.1), (2.9, 3.2), (3.7, 8.9), (9.6, 10.0),
          (10.8, 11.9), (12.3, 12.45), (13.4, 14.3), (15.1, 15.35),
          (16.2, 17.8), (18.5, 18.65), (19.3, 20.3), (21.0, 21.4),
          (21.9, 22.2)]


def make(argv, path):
    """Material made with ffmpeg; a precondition, not a judgement."""
    made = subprocess.run(["ffmpeg", "-v", "error"] + argv + [path, "-y"],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          timeout=LONGEST)
    assert made.returncode == 0 and os.path.exists(path), made.stdout
    return path


def camera(name, late):
    """A camera whose sound is the bursts, heard from *late* seconds on."""
    gate = "+".join("between(t+%g,%g,%g)" % (late, x, y) for x, y in BURSTS)
    return make(["-f", "lavfi", "-i",
                 "testsrc=size=160x90:rate=25:duration=%g" % LENGTH,
                 "-f", "lavfi", "-i",
                 "aevalsrc='0.5*sin(2*PI*330*t)*(%s)':s=48000:d=%g"
                 % (gate, LENGTH), "-c:v", "libx264", "-preset",
                 "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac",
                 "-shortest"], os.path.join(HOME, name))


CAMERAS = [camera("GuestCam_C003.mov", 0.0),
           camera("PresenterCam_C002.mov", 2.48)]
RECORDINGS = [make(["-i", CAMERAS[0], "-vn", "-c:a", "pcm_s16le"],
                   os.path.join(HOME, name))
              for name in ("TASCAM_0001.wav", "ZOOM0001.wav")]

OUT = os.path.join(HOME, "out")
print("1. One run over two recordings and two cameras")
try:
    answer = subprocess.run(
        [sys.executable, SCRIPT, "--without-auphonic", "--out", OUT,
         "--no-metrics", "--no-speech-recognition", "--no-transcript-file"]
        + RECORDINGS + CAMERAS,
        capture_output=True, text=True, timeout=LONGEST)
    code, said = answer.returncode, answer.stdout + answer.stderr
except subprocess.TimeoutExpired:
    # Through the same check as every other way out: a verdict only a
    # hanging run ever reaches is one nobody can show red.
    code, said = -1, ""
    print("    the run printed nothing back in %d s" % LONGEST)
print("    %d recordings, %d cameras, %.1f s"
      % (len(RECORDINGS), len(CAMERAS), time.time() - began))
check("the run came back and printed a log", code == 0 and len(said) > 200,
      "return code %d, %d characters of log" % (code, len(said)))

lines = said.splitlines()


# A camera's block runs from its heading to the next heading: another
# camera's, or the one the run prints once every camera is done. The
# blocks come out in the order the threads finish, so without that end
# whichever came last would run on to the end of the log, and what a
# block holds would change from run to run.
PROCESSING = vpm.T('\nPROCESSING: %s').strip()
AFTER = vpm.T('\nSAVING TRACKS').strip()


def block_of(name):
    """The lines of the log that belong to one camera's block."""
    out, inside = [], False
    for line in lines:
        if line.strip().startswith(PROCESSING % "") or line.strip() == AFTER:
            inside = line.strip() == PROCESSING % name
            continue
        if inside:
            out.append(line)
    return out


# Which camera the run itself called the reference, read out of its own
# line rather than guessed from the file sizes.
head = vpm.T('  Reference: %s (%s, longest running time)') \
    .split("%s")[0].rstrip()
named = [l.strip()[len(head.strip()):].strip().split(" (")[0]
         for l in lines if l.strip().startswith(head.strip())]
reference = named[0] if named else ""
others = [os.path.basename(v) for v in CAMERAS
          if os.path.basename(v) != reference]
check("the run names one of the cameras as the reference",
      reference in [os.path.basename(v) for v in CAMERAS] and len(others) == 1,
      "%r out of %r" % (reference, [os.path.basename(v) for v in CAMERAS]))
if not reference or not others:
    shutil.rmtree(HOME, ignore_errors=True)
    finish()

DRIFT = vpm.T('  Clock drift:     %+.2f ppm (+/- %.2f), residual spread '
              '%.1f ms, %d of %d points').split("%")[0].strip()
NOTHING = vpm.T('  Clock drift:     nothing measured -- this is the '
                'reference the others are held against').strip()

mine = block_of(reference)
measured = [l.strip() for l in mine if l.strip().startswith(DRIFT)
            and "ppm" in l]
check("the reference camera reports no clock measurement",
      not measured, "%d line(s) in the block of %s: %s"
      % (len(measured), reference, (measured or [""])[0][:70]))
check("and its block says instead that there was nothing to measure",
      any(l.strip() == NOTHING for l in mine),
      "no line %r in the block of %s" % (NOTHING[:50], reference))

theirs = block_of(others[0])
# Where the run says it placed that camera from: the camera comparison,
# or its timecode alone, which would mean nothing was measured.
OFFSET = vpm.T('  Offset:          %s   (from the camera comparison)') \
    .split("%s")[0].strip()
placed = [l.strip() for l in theirs if l.strip().startswith(OFFSET)]
drifts = [l for l in theirs if l.strip().startswith(DRIFT) and "ppm" in l]
check("a camera that was measured still reports its clock", bool(drifts),
      "%d line(s) in the block of %s, its offset line %r"
      % (len(drifts), others[0], (placed or [""])[0]))

shutil.rmtree(HOME, ignore_errors=True)
finish()
