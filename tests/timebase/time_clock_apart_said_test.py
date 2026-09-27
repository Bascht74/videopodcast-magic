# -*- coding: utf-8 -*-
"""A clock the sound contradicts is named, by the run and the window alike.

Three cameras hearing one pattern of tone bursts, the longest the
reference with a clock: one whose clock is three seconds off what the
sound says, one whose clock agrees. Sections: one measuring run,
--dry-run and --without-auphonic, names the one that is off with both
places and the gap, and not the one that agrees; the window's
measurement of the same files prints the same line, word for word.
"""
PLATFORM_BOUND = True
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import contextlib
import io
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
HOME = tempfile.mkdtemp(prefix="vpm_clockapart_")
# One uneven pattern over the whole stretch any file covers, so the
# sound can place every camera against the reference.
BURSTS = [(0.6, 1.3), (1.9, 2.1), (2.9, 3.2), (3.7, 8.9), (9.6, 10.0),
          (10.8, 11.9), (12.3, 12.45), (13.4, 14.3), (15.1, 15.35),
          (16.2, 17.8), (18.5, 18.65), (19.3, 20.3), (21.0, 21.4),
          (21.9, 22.2), (23.0, 24.6), (25.3, 25.5), (26.1, 27.4),
          (28.0, 28.3), (29.1, 30.6), (31.2, 31.5), (32.4, 34.0)]
# The guest's camera rolls 2 s after the reference, its clock says 5;
# the presenter's rolls 6 s after it, and its clock says so.
GUEST_LATE, GUEST_CLOCK = 2.0, "10:00:05:00"
PRESENTER_LATE, PRESENTER_CLOCK = 6.0, "10:00:06:00"


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
    """A camera hearing the pattern from *late* s on, with its clock."""
    return made(["-f", "lavfi", "-i", "testsrc=size=160x90:rate=25:"
                 "duration=%g" % length, "-ss", "%g" % late, "-i", TONE,
                 "-t", "%g" % length, "-c:v", "libx264", "-preset",
                 "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac",
                 "-ar", "48000", "-timecode", clock],
                os.path.join(HOME, name))


WIDE = camera("WideCam_C001.mov", 0.0, 34.0, "10:00:00:00")
GUEST = camera("GuestCam_C002.mov", GUEST_LATE, 26.0, GUEST_CLOCK)
PRESENTER = camera("PresenterCam_C003.mov", PRESENTER_LATE, 24.0,
                   PRESENTER_CLOCK)
TRACK = made(["-i", TONE, "-t", "34"], os.path.join(HOME, "Room_T01.wav"))
ENDING = vpm.T('  %s: its clock says %s, the sound measured %s -- %s s '
               'apart; the measurement is used').split("%s")[-1]


def about(lines, name):
    """The lines naming *name* and ending as a clock line does."""
    return [x for x in lines if x.startswith("  %s: " % name)
            and x.endswith(ENDING)]


def gap_in(line):
    """The gap a clock line gives, in seconds, or None."""
    found = re.findall(r"([+-][0-9]+\.[0-9]+) s", line or "")
    return float(found[-1]) if found else None


print("1. One measuring run over the three cameras and a track")
try:
    answer = subprocess.run(
        [sys.executable, SCRIPT, "--without-auphonic",
         "--no-speech-recognition", "--dry-run", "--out",
         os.path.join(HOME, "out"), TRACK, WIDE, GUEST, PRESENTER],
        capture_output=True, text=True, timeout=LONGEST,
        env=dict(os.environ, QT_QPA_PLATFORM="offscreen"))
    code, said = answer.returncode, answer.stdout + answer.stderr
except subprocess.TimeoutExpired:
    code, said = -1, ""
said = re.sub(re.escape(vpm.MARK) + "[a-z]", "", said)
lines = [x.rstrip() for x in re.sub(r"\x1b\[[0-9;]*m", "", said)
         .replace("\r", "\n").splitlines() if x.strip()]
check("a measuring run over three cameras and a track goes through",
      code == 0, "returned %r, %d lines, the last %r"
      % (code, len(lines), lines[-1] if lines else ""))
run_guest = about(lines, os.path.basename(GUEST))
gap = gap_in(run_guest[0] if run_guest else None)
check("the run names the camera whose clock is 3 s off, with the gap",
      len(run_guest) == 1 and gap is not None and abs(gap + 3.0) <= 0.04,
      "lines %r, gap %s s, wanted one line and -3.000 s"
      % (run_guest, gap))
run_presenter = about(lines, os.path.basename(PRESENTER))
check("and not the camera whose clock agrees",
      run_presenter == [], "lines %r" % run_presenter)

print("\n2. The window's measurement of the same files")
shown = io.StringIO()
try:
    with contextlib.redirect_stdout(shown):
        vpm.measure_time_axis([TRACK, WIDE, GUEST, PRESENTER],
                              tc_of=lambda p: vpm.file_timecode(p))
except Exception as e:
    shown.write("the measurement broke off: %s" % e)
window = [x.rstrip() for x in shown.getvalue().splitlines() if x.strip()]
check("the window prints the run's line for it, word for word",
      about(window, os.path.basename(GUEST)) == run_guest
      and run_guest != [], "window %r, run %r"
      % (about(window, os.path.basename(GUEST)), run_guest))
check("and it too leaves the camera that agrees unnamed",
      about(window, os.path.basename(PRESENTER)) == [],
      "window %r" % about(window, os.path.basename(PRESENTER)))

shutil.rmtree(HOME, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
