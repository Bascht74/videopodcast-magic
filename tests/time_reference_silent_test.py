# -*- coding: utf-8 -*-
"""The camera everything else is measured against reports no measurement.

One camera is the reference: the others are laid against it, and it
sits at zero by definition. Its block of the log nevertheless carried
the same clock line as the rest -- "+0.00 ppm (+/- 0.00), residual
spread 0.0 ms, 0 of 0 points" -- which reads like a measurement that
came out at nothing and is in truth no measurement at all.

One run over the shared fixture, without auphonic.com and without
speech recognition, and the log is read afterwards: which camera the
run called the reference, what its block says about the clock, and
what another camera's block says.

The limit of the method: the cameras of that folder share no signal,
so nothing here is a claim about where the axis landed -- only about
which lines stand in whose block.
"""
import os
import sys
import time
import glob
import shutil
import tempfile
import subprocess
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
sys.path.insert(0, HERE)
from fixture_root import fixture

spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
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


def finish(skipped=""):
    """The one way out: the count, the verdict, the return code."""
    if skipped:
        print("SKIPPED: " + skipped)
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    if bad:
        print("FAIL: " + " | ".join(bad))
    elif not skipped:
        print("ALL OK")
    sys.exit(1 if bad else 0)


# How long the run may take. Far above what it needs here, and it only
# ever ends the test with a line saying the run never came back.
LONGEST = 900

MEDIA = fixture("interview")
RECORDINGS = sorted(glob.glob(os.path.join(MEDIA, "*.wav")))[:2]
CAMERAS = sorted(glob.glob(os.path.join(MEDIA, "*.mov")))[:2]
if len(RECORDINGS) < 2 or len(CAMERAS) < 2:
    finish("no fixture material -- 'cd tests && bash fixtures.sh' builds "
           "the interview folder this reads (%s)" % MEDIA)

OUT = tempfile.mkdtemp(prefix="vpm_reference_")
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


def block_of(name):
    """The lines of the log that belong to one camera's block."""
    head = vpm.T('\nPROCESSING: %s').strip() % name
    out, inside = [], False
    for line in lines:
        if line.strip().startswith(vpm.T('\nPROCESSING: %s').strip() % ""):
            inside = line.strip() == head.strip()
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
    shutil.rmtree(OUT, ignore_errors=True)
    finish()

DRIFT = vpm.T('  Clock drift:     %+.2f ppm (+/- %.2f), residual spread '
              '%.1f ms, %d of %d points').split("%")[0].strip()
NOTHING = vpm.T('  Clock drift:     nothing measured -- this is the '
                'reference the others are held against').strip()

mine = block_of(reference)
measured = [l.strip() for l in mine if l.strip().startswith(DRIFT)
            and "ppm" in l]
check("the reference camera reports no clock measurement",
      not measured, "%d line(s) in its %d line block: %s"
      % (len(measured), len(mine), (measured or [""])[0][:70]))
check("and its block says instead that there was nothing to measure",
      any(l.strip() == NOTHING for l in mine),
      "%d line(s) in its block, none of them %r" % (len(mine), NOTHING[:50]))

theirs = block_of(others[0])
check("a camera that was measured still reports its clock",
      any(l.strip().startswith(DRIFT) and "ppm" in l for l in theirs),
      "%d line(s) in the %d line block of %s"
      % (len([l for l in theirs if "ppm" in l]), len(theirs), others[0]))

shutil.rmtree(OUT, ignore_errors=True)
finish()
