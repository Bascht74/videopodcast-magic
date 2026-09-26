# -*- coding: utf-8 -*-
"""A camera's own sound stands where its camera stands, however placed.

One measuring run, Sync only, --dry-run and --without-auphonic, over
four cameras alone. Three have a timecode that fits: two share one
pattern of tone bursts, the second 2.48 s later; the third hears a
steady tone, 1 s later. The fourth hears the bursts under noise, too
faint for a camera, and has no timecode. Sections: the sound places the
second, the clock the third, nothing the fourth; then each own sound at
its camera's offset, placed with it -- and the fourth's placed nowhere.
"""
PLATFORM_BOUND = True
import os
import re
import subprocess
import sys
import tempfile
import time
import shutil
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


def finish():
    """The one way out: the count, the verdict, the return code."""
    shutil.rmtree(HOME, ignore_errors=True)
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


# A bound for the run and for each ffmpeg, never reached when they work;
# it only turns a run that never comes back into a line saying so.
LONGEST = 600
HOME = tempfile.mkdtemp(prefix="vpm_ownsound_")
LENGTH = 2 * vpm.AXIS_MIN_WINDOW_S
# One uneven pattern, so the sound can measure one camera against the
# other; a steady tone gives it nothing, and the clock places that one.
BURSTS = [(0.6, 1.3), (1.9, 2.1), (2.9, 3.2), (3.7, 8.9), (9.6, 10.0),
          (10.8, 11.9), (12.3, 12.45), (13.4, 14.3), (15.1, 15.35),
          (16.2, 17.8), (18.5, 18.65), (19.3, 20.3), (21.0, 21.4),
          (21.9, 22.2), (23.0, 24.6)]


def made(argv, path):
    """A file made with ffmpeg; a precondition, not a judgement."""
    answer = subprocess.run(["ffmpeg", "-v", "error"] + argv + [path, "-y"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            timeout=LONGEST)
    assert answer.returncode == 0 and os.path.exists(path), answer.stdout
    return path


# The bursts are worked out once, sample by sample, and every camera
# takes its stretch of them.
TONE = made(["-f", "lavfi", "-i", "aevalsrc='0.5*sin(2*PI*330*t)*(%s)'"
             ":s=16000:d=%g" % ("+".join("between(t,%g,%g)" % b
                                         for b in BURSTS), LENGTH + 5)],
            os.path.join(HOME, "bursts.wav"))


def camera(name, late, timecode, length):
    """A camera hearing the bursts from *late* s on, or a steady tone."""
    sound = (["-ss", "%g" % late, "-i", TONE] if late is not None
             else ["-f", "lavfi", "-i", "sine=frequency=220:sample_rate="
                   "48000:duration=%g" % length])
    return made(["-f", "lavfi", "-i", "testsrc=size=160x90:rate=25:"
                 "duration=%g" % length] + sound
                + ["-t", "%g" % length, "-c:v", "libx264", "-preset",
                   "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar",
                   "48000", "-timecode", timecode],
                os.path.join(HOME, name))


REFERENCE = camera("GuestCam_C003.mov", 0.0, "18:55:04:00", LENGTH + 2)
BY_SOUND = camera("PresenterCam_C002.mov", 2.48, "18:55:06:12", LENGTH)
BY_CLOCK = camera("WideCam_C001.mov", None, "18:55:05:00", LENGTH)
# The bursts from 1.2 s on at a fifth, under noise: 0.19 against the
# reference, under the floor for a camera and above it for a sound.
NOWHERE = made(["-f", "lavfi", "-i", "testsrc=size=160x90:rate=25:"
                "duration=%g" % LENGTH, "-ss", "1.2", "-i", TONE,
                "-f", "lavfi", "-i", "anoisesrc=color=white:seed=4:"
                "amplitude=0.5:sample_rate=16000:duration=%g" % LENGTH,
                "-filter_complex", "[1:a]volume=0.2[t];[t][2:a]amix="
                "inputs=2:normalize=0", "-t", "%g" % LENGTH, "-c:v",
                "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-ar", "48000"],
               os.path.join(HOME, "SideCam_C004.mov"))


def pattern(text):
    """A T() text as a regular expression, each %s a group of its own."""
    parts = re.split(r"%-?\d*s", text.strip())
    return re.compile("^" + "(.*?)".join(re.escape(p) for p in parts)
                      + "$")


#--------------------------------------------------------------- 1. Run

print("1. Four cameras alone, Sync only, measured and not written")
try:
    answer = subprocess.run(
        [sys.executable, SCRIPT, "--project-type", "sync",
         "--without-auphonic", "--multitrack", "--dry-run", "--out",
         os.path.join(HOME, "out"), REFERENCE, BY_SOUND, BY_CLOCK, NOWHERE],
        capture_output=True, text=True, timeout=LONGEST,
        env=dict(os.environ, QT_QPA_PLATFORM="offscreen"))
    code, said = answer.returncode, answer.stdout + answer.stderr
except subprocess.TimeoutExpired:
    code, said = -1, ""
said = re.sub(re.escape(vpm.MARK) + "[a-z]", "", said)
lines = [x.strip() for x in re.sub(r"\x1b\[[0-9;]*m", "", said)
         .replace("\r", "\n").splitlines() if x.strip()]
check("a measuring run over four cameras goes through",
      code == 0 and len(lines) > 20,
      "returned %r after %.1f s, %d lines, the last %r"
      % (code, time.time() - began, len(lines), lines[-1] if lines else ""))
by_clock = pattern(vpm.T('  %s: its sound matches by %s, under the floor '
                         'of %s -- placed by its clock alone'))
clocked = [m.group(1) for m in map(by_clock.match, lines) if m]
check("the sound places the second camera and the clock the third",
      clocked == [os.path.basename(BY_CLOCK)],
      "placed by the clock: %s, wanted [%r]"
      % (clocked, os.path.basename(BY_CLOCK)))

#------------------------------------------------------ 2. The time axis

print("\n2. Where each camera's own sound stands")
# Every placing line of the block, the camera's and its sound's alike:
# {name: (offset, the note in brackets or "")}.
# The last group is the note, empty on a camera's own line.
WAYS = [pattern(vpm.T('  %-20s offset %s, clock drift not measured%s')),
        pattern(vpm.T('  %-20s offset %s, clock drift %s ppm (+/- %s), '
                      'residual spread %s ms, %s of %s points%s'))]
placed = {}
for m in (way.match(line) for line in lines for way in WAYS):
    if m:
        placed[m.group(1).strip()] = (m.group(2),
                                      m.group(m.re.groups).strip()[1:-1])
WITH = vpm.T("placed with its camera")
WITH_CLOCK = vpm.T("placed with its camera, by that camera's clock")


def stem(path):
    """The name the run gives a camera's own sound: the file's stem."""
    return os.path.splitext(os.path.basename(path))[0]


own = placed.get(stem(BY_SOUND))
cam = placed.get(os.path.basename(BY_SOUND))
check("a camera's own sound stands where the sound placed its camera",
      own is not None and cam is not None and own[0] == cam[0]
      and own[1] == WITH,
      "its sound %r, the camera %r, wanted the same offset and %r"
      % (own, cam, WITH))
own = placed.get(stem(REFERENCE))
check("the reference's own sound stands with the reference, at nought",
      own == (vpm.as_hms(0.0), WITH),
      "its sound %r, wanted %r" % (own, (vpm.as_hms(0.0), WITH)))
own = placed.get(stem(BY_CLOCK))
cam = placed.get(os.path.basename(BY_CLOCK))
check("and a camera its clock placed keeps its own sound with it",
      own is not None and cam is not None and own[0] == cam[0]
      and own[1] == WITH_CLOCK,
      "its sound %r, the camera %r, wanted the same offset and %r"
      % (own, cam, WITH_CLOCK))
refused = vpm.no_place_message(stem(NOWHERE)).strip()
check("and a camera nothing placed leaves its own sound nowhere",
      stem(NOWHERE) not in placed and refused in lines
      and os.path.basename(NOWHERE) not in placed,
      "its sound %r, the camera %r, wanted neither placed and %r said"
      % (placed.get(stem(NOWHERE)), placed.get(os.path.basename(NOWHERE)),
         refused[:40]))

finish()
