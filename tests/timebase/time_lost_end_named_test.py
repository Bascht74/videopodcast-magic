# -*- coding: utf-8 -*-
"""The log names only the end of a track that runs past the picture.

One measuring run, --dry-run and --without-auphonic, over one camera
and three tracks that hear the camera's pattern of tone bursts. The
first starts before the camera, the second runs on after it, the third
does both. After the run goes through: the first names only its front,
the second only its back, the third both -- a stretch of nought is
never named.
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
HOME = tempfile.mkdtemp(prefix="vpm_lostend_")
LENGTH = 2 * vpm.AXIS_MIN_WINDOW_S
# One uneven pattern over the whole stretch any file covers, so the
# sound can place every track against the camera.
BURSTS = [(0.6, 1.3), (1.9, 2.1), (2.9, 3.2), (3.7, 8.9), (9.6, 10.0),
          (10.8, 11.9), (12.3, 12.45), (13.4, 14.3), (15.1, 15.35),
          (16.2, 17.8), (18.5, 18.65), (19.3, 20.3), (21.0, 21.4),
          (21.9, 22.2), (23.0, 24.6), (25.3, 25.5), (26.1, 27.4),
          (28.0, 28.3)]


def made(argv, path):
    """A file made with ffmpeg; a precondition, not a judgement."""
    answer = subprocess.run(["ffmpeg", "-v", "error"] + argv + [path, "-y"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            timeout=LONGEST)
    assert answer.returncode == 0 and os.path.exists(path), answer.stdout
    return path


TONE = made(["-f", "lavfi", "-i", "aevalsrc='0.5*sin(2*PI*330*t)*(%s)'"
             ":s=48000:d=%g" % ("+".join("between(t,%g,%g)" % b
                                         for b in BURSTS), LENGTH + 10)],
            os.path.join(HOME, "bursts.wav"))
# The camera sees the pattern from 3 s on; each track takes its own
# stretch of the same pattern, so where it starts is how early it is.
CAMERA_FROM = 3.0
CAMERA = made(["-f", "lavfi", "-i", "testsrc=size=160x90:rate=25:"
               "duration=%g" % LENGTH, "-ss", "%g" % CAMERA_FROM,
               "-i", TONE, "-t", "%g" % LENGTH, "-c:v", "libx264",
               "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac",
               "-ar", "48000"], os.path.join(HOME, "WideCam_C001.mov"))


def track(name, early, late):
    """A track *early* s before the camera and *late* s past its end."""
    return made(["-ss", "%g" % (CAMERA_FROM - early), "-i", TONE, "-t",
                 "%g" % (early + LENGTH + late)], os.path.join(HOME, name))


FRONT = track("Guest_T01.wav", 2.0, 0.0)
BACK = track("Presenter_T02.wav", 0.0, 2.5)
BOTH = track("CoPresenter_T03.wav", 1.5, 3.0)


def finish():
    """The one way out: the count, the verdict, the return code."""
    shutil.rmtree(HOME, ignore_errors=True)
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


print("1. One camera and three tracks, measured and not written")
try:
    answer = subprocess.run(
        [sys.executable, SCRIPT, "--without-auphonic",
         "--no-speech-recognition", "--dry-run", "--out",
         os.path.join(HOME, "out"), FRONT, BACK, BOTH, CAMERA],
        capture_output=True, text=True, timeout=LONGEST,
        env=dict(os.environ, QT_QPA_PLATFORM="offscreen"))
    code, said = answer.returncode, answer.stdout + answer.stderr
except subprocess.TimeoutExpired:
    code, said = -1, ""
said = re.sub(re.escape(vpm.MARK) + "[a-z]", "", said)
lines = [x.rstrip() for x in re.sub(r"\x1b\[[0-9;]*m", "", said)
         .replace("\r", "\n").splitlines() if x.strip()]
window = vpm.T('  Common window:       %s to %s (%s)').split("%s")[0]
check("a measuring run over one camera and three tracks goes through",
      code == 0 and any(x.startswith(window) for x in lines),
      "returned %r after %.1f s, %d lines, the last %r"
      % (code, time.time() - began, len(lines), lines[-1] if lines else ""))

print("\n2. Which end each track loses")
# What each track says about itself; a name the log never gives
# stands as an empty list.
about = {name: [x for x in lines if x.startswith("    %s: " % name)]
         for name in ("Guest", "Presenter", "CoPresenter")}
want = vpm.T('    %s: %s at the front has no picture and is left out') \
    % ("Guest", vpm.as_hms(2.0))
check("a track starting before the picture names only its front",
      about["Guest"] == [want],
      "the log says %r, wanted [%r]" % (about["Guest"], want))
want = vpm.T('    %s: %s at the back has no picture and is left out') \
    % ("Presenter", vpm.as_hms(2.5))
check("a track running on past the picture names only its back",
      about["Presenter"] == [want],
      "the log says %r, wanted [%r]" % (about["Presenter"], want))
want = vpm.T('    %s: %s at the front and %s at the back have no '
             'picture and are left out') \
    % ("CoPresenter", vpm.as_hms(1.5), vpm.as_hms(3.0))
check("a track that loses both ends names both",
      about["CoPresenter"] == [want],
      "the log says %r, wanted [%r]" % (about["CoPresenter"], want))

finish()
