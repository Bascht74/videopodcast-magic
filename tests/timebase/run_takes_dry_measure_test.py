# -*- coding: utf-8 -*-
"""What a dry run measured, a later run takes until one of its inputs moves.

Command-line runs over the interview fixture, --without-auphonic, into a
store of their own: a dry run on an empty store, a second dry run, a
full run, a dry run with an Out point, and a dry run after one recording
was written again. Judged by the log: whether the axis and who speaks
when were measured or taken, and that a taken axis puts every file
where the measured one did. The limit: the log says it, so a run that
took the axis and said nothing would pass as one that measured.
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
import glob
import re
import shutil
import subprocess
import tempfile
import time
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


def stop():
    """Count what there is and go; every path ends here."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


MEDIA = os.environ.get("VPM_MEDIA") or ""
SOUND = sorted(glob.glob(os.path.join(MEDIA, "*.wav")))
PICTURES = sorted(glob.glob(os.path.join(MEDIA, "*.mov")))
if len(SOUND) < 2 or not PICTURES:
    print("SKIPPED: no interview material -- point VPM_MEDIA at the "
          "interview fixture (tests/fixtures.sh builds it; looked in %r)"
          % MEDIA)
    stop()

# The recording written again below is a copy of its own: the fixture
# is shared and only ever read. The others are read where they lie.
WORK = tempfile.mkdtemp(prefix="vpm_drymeasure_")
STORE = os.path.join(WORK, "store")
OUT = os.path.join(WORK, "out")
os.makedirs(OUT)
CHANGED = os.path.join(WORK, os.path.basename(SOUND[-1]))
shutil.copy(SOUND[-1], CHANGED)
files = SOUND[:-1] + [CHANGED] + PICTURES

AXIS_TAKEN = vpm.T('  Taken from the measurement kept on this machine: the '
                   'same files and settings, so nothing is measured again.')
# The headings as a terminal shows them: without the mark and the gap.
SPEAKERS_TAKEN = vpm.T('\nSPEAKERS -- MEASURED BEFORE').strip()
SPEAKERS_MEASURED = vpm.T('\nSPEAKERS -- MEASURED HERE').strip()


def run(*extra):
    """One run into this test's own store; its return code and log."""
    got = subprocess.run(
        [sys.executable, SCRIPT, "--without-auphonic", "--out", OUT,
         "--no-metrics", "--no-speech-recognition", "--no-transcript-file"]
        + list(extra) + files, capture_output=True, text=True,
        errors="replace", env=dict(os.environ, VPM_CACHE=STORE))
    return got.returncode, got.stdout + got.stderr


def offsets(log):
    """Every file's place as the axis section says it, in its order."""
    return re.findall(r"^  (\S.*?) +offset (-?[0-9:.]+)", log, re.M)


try:
    rc, first = run("--dry-run")
    check("a dry run on an empty store comes back with 0", rc == 0,
          "return code %d, the end of its log: %r" % (rc, first[-160:]))
    check("with nothing kept a dry run measures the axis itself",
          AXIS_TAKEN not in first and len(offsets(first)) >= 3,
          "taken line there: %s, %d places said"
          % (AXIS_TAKEN in first, len(offsets(first))))

    rc, second = run("--dry-run")
    check("a second dry run takes the axis the first one measured",
          AXIS_TAKEN in second, "return code %d, taken line there: %s"
          % (rc, AXIS_TAKEN in second))
    check("and who speaks when as well",
          SPEAKERS_TAKEN in second and SPEAKERS_MEASURED not in second,
          "measured before: %s, measured here: %s"
          % (SPEAKERS_TAKEN in second, SPEAKERS_MEASURED in second))

    rc, full = run()
    check("a full run after the dry runs takes the axis from the store",
          rc == 0 and AXIS_TAKEN in full,
          "return code %d, taken line there: %s" % (rc, AXIS_TAKEN in full))
    check("the taken axis puts every file where the dry run measured it",
          offsets(full) == offsets(first) and offsets(first),
          "measured %s, taken %s" % (offsets(first), offsets(full)))

    rc, narrower = run("--dry-run", "--out-point", "-0:00:20")
    check("another Out point keeps the axis",
          AXIS_TAKEN in narrower, "return code %d, taken line there: %s"
          % (rc, AXIS_TAKEN in narrower))
    check("and measures who speaks when again",
          SPEAKERS_MEASURED in narrower and SPEAKERS_TAKEN not in narrower,
          "measured here: %s, measured before: %s"
          % (SPEAKERS_MEASURED in narrower, SPEAKERS_TAKEN in narrower))

    os.utime(CHANGED, (2000000000, 2000000000))
    rc, after = run("--dry-run")
    check("a recording written since makes the axis measured again",
          rc == 0 and AXIS_TAKEN not in after and offsets(after),
          "return code %d, taken line there: %s, %d places said"
          % (rc, AXIS_TAKEN in after, len(offsets(after))))
except Exception as e:
    # A crash ends the runs, not the count: it goes out through stop().
    bad.append("the runs crashed [%r]" % e)
    print("  the runs crashed: %r" % e)
finally:
    shutil.rmtree(WORK, ignore_errors=True)
stop()
