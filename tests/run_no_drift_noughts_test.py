# -*- coding: utf-8 -*-
"""A drift nobody measured says it was not measured, never noughts.

One real run, Sync only and --without-auphonic, over four cameras alone,
each with a timecode that fits. Three share one pattern of tone bursts:
the reference, a long one rolling 2.48 s later, whose drift the sound
can measure, and a short one rolling with it, too short for a single
point. The fourth hears a steady tone, and its clock places it. The
sections: the run goes through and places them so; the time axis block
and the short camera's own block say "not measured" where nothing was,
and the long one's its number.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
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
HOME = tempfile.mkdtemp(prefix="vpm_noughts_")
# One uneven pattern, so the sound can measure the cameras against each
# other; a steady tone gives it nothing, and the clock places that one.
BURSTS = [(0.6, 1.3), (1.9, 2.1), (2.9, 3.2), (3.7, 8.9), (9.6, 10.0),
          (10.8, 11.9), (12.3, 12.45), (13.4, 14.3), (15.1, 15.35),
          (16.2, 17.8), (18.5, 18.65), (19.3, 20.3), (21.0, 21.4),
          (21.9, 22.2), (23.0, 24.6), (25.2, 25.4), (26.1, 27.9),
          (28.5, 28.7), (29.4, 30.9), (31.6, 31.8), (32.5, 34.0),
          (34.7, 35.0), (35.8, 37.9), (38.6, 38.8), (39.5, 40.4),
          (41.2, 41.5), (42.1, 43.6), (44.2, 44.5)]


def made(argv, path):
    """A file made with ffmpeg; a precondition, not a judgement."""
    answer = subprocess.run(["ffmpeg", "-v", "error"] + argv + [path, "-y"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            timeout=LONGEST)
    assert answer.returncode == 0 and os.path.exists(path), answer.stdout
    return path


# The bursts are worked out once, sample by sample, and every camera
# takes its stretch of them: three times over it took seconds.
TONE = made(["-f", "lavfi", "-i", "aevalsrc='0.5*sin(2*PI*330*t)*(%s)'"
             ":s=16000:d=36" % "+".join("between(t,%g,%g)" % b
                                        for b in BURSTS)],
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


# A short camera matches a long reference by less: measured 25.9.2026, 12
# s against 42 s by 0.43, 20 s against 30 s by 0.86, the floor is 0.5;
# and against 30 s a long one got 8 points where the short one got none.
REFERENCE = camera("GuestCam_C003.mov", 0.0, "18:55:04:00", 32)
MEASURED = camera("PresenterCam_C002.mov", 2.48, "18:55:06:12", 30)
SHORT = camera("CoPresenterCam_C004.mov", 2.48, "18:55:06:12", 20)
BY_CLOCK = camera("WideCam_C001.mov", None, "18:55:05:00", 30)


def pattern(text):
    """A T() text as a regular expression, each %s a group of its own."""
    parts = re.split(r"%-?\d*s", text.strip())
    return re.compile("^" + "(.*?)".join(re.escape(p) for p in parts)
                      + "$")


def stem(path):
    """The name the run gives a camera's own sound: the file's stem."""
    return os.path.splitext(os.path.basename(path))[0]


#--------------------------------------------------------------- 1. Run

print("1. Four cameras alone, Sync only")
try:
    answer = subprocess.run(
        [sys.executable, SCRIPT, "--project-type", "sync",
         "--without-auphonic", "--multitrack", "--no-metrics", "--out",
         os.path.join(HOME, "out"), REFERENCE, MEASURED, SHORT, BY_CLOCK],
        capture_output=True, text=True, timeout=LONGEST,
        env=dict(os.environ, QT_QPA_PLATFORM="offscreen"))
    code, said = answer.returncode, answer.stdout + answer.stderr
except subprocess.TimeoutExpired:
    code, said = -1, ""
said = re.sub(re.escape(vpm.MARK) + "[a-z]", "", said)
lines = [x.strip() for x in re.sub(r"\x1b\[[0-9;]*m", "", said)
         .replace("\r", "\n").splitlines() if x.strip()]
check("a run over four cameras goes through",
      code == 0 and len(lines) > 20,
      "returned %r after %.1f s, %d lines, the last %r"
      % (code, time.time() - began, len(lines), lines[-1] if lines else ""))
by_clock = pattern(vpm.T('  %s: its sound matches by %s, under the floor '
                         'of %s -- placed by its clock alone'))
clocked = [m.group(1) for m in map(by_clock.match, lines) if m]
check("the sound places three cameras and the clock the fourth",
      clocked == [os.path.basename(BY_CLOCK)],
      "placed by the clock: %s, wanted [%r]"
      % (clocked, os.path.basename(BY_CLOCK)))

#------------------------------------------------------ 2. The time axis

print("\n2. The time axis block")
UNMEASURED = pattern(vpm.T('  %-20s offset %s, clock drift not measured%s'))
MEASURING = pattern(vpm.T('  %-20s offset %s, clock drift %s ppm (+/- %s), '
                          'residual spread %s ms, %s of %s points%s'))
# {name: the line}, one for each way it can be said.
unmeasured = {m.group(1).strip(): m.group(0)
              for m in map(UNMEASURED.match, lines) if m}
measured = {m.group(1).strip(): m.group(0)
            for m in map(MEASURING.match, lines) if m}


def said_of(name):
    """What the block says of one name, for a FAIL line."""
    return "not measured: %r, with a number: %r" % (
        unmeasured.get(name), measured.get(name))


name = os.path.basename(SHORT)
check("a camera placed on too few points says its drift is not measured",
      name in unmeasured and name not in measured,
      "%s -- %s" % (name, said_of(name)))
name = os.path.basename(BY_CLOCK)
check("and so does a camera its clock placed, with no noughts",
      name in unmeasured and name not in measured,
      "%s -- %s" % (name, said_of(name)))
name = stem(REFERENCE)
check("and so does the reference's own sound",
      name in unmeasured and name not in measured,
      "%s -- %s" % (name, said_of(name)))
name = os.path.basename(MEASURED)
check("a camera whose drift the sound measured still says its number",
      name in measured and name not in unmeasured,
      "%s -- %s" % (name, said_of(name)))

#-------------------------------------------------- 3. The camera's block

print("\n3. The short camera's own block")
# A camera's block runs from its heading to the next heading, whichever
# camera's that is, or to the first line the run prints once all are done.
PROCESSING = vpm.T('\nPROCESSING: %s').strip()
ENDS = [vpm.T('\nRESULT').strip(), vpm.T('\nSAVING TRACKS').strip()]


def block_of(path):
    """The lines of the log that belong to one camera's block."""
    out, inside = [], False
    for line in lines:
        if line.startswith(PROCESSING % "") or line in ENDS:
            inside = line == PROCESSING % os.path.basename(path)
            continue
        if inside:
            out.append(line)
    return out


NOT_MEASURED = vpm.T('  Clock drift:     not measured -- too few points '
                     'of its sound held for one').strip()
DRIFT = pattern(vpm.T('  Clock drift:     %s ppm (+/- %s), residual '
                      'spread %s ms, %s of %s points'))
RUNNING = pattern(vpm.T('  Drift over the running time: %s s = %s frames  '
                        '-->  %s'))
mine = block_of(SHORT)
noughts = [x for x in mine if DRIFT.match(x) or RUNNING.match(x)]
check("and the short camera's own block says so, with no noughts",
      NOT_MEASURED in mine and not noughts,
      "%d lines in its block, %r %s, lines with a number: %s"
      % (len(mine), NOT_MEASURED[:40], "among them" if NOT_MEASURED in mine
         else "not among them", noughts))
theirs = block_of(MEASURED)
check("while the camera whose drift was measured prints its number",
      any(DRIFT.match(x) for x in theirs) and NOT_MEASURED not in theirs,
      "%d lines in its block: %s" % (len(theirs), theirs[:6]))

finish()
