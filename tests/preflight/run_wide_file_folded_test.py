# -*- coding: utf-8 -*-
"""The command line says a four-channel file is folded, not cut by rows.

The window cuts such a file by its channel rows; the command line has
none and cuts nothing. One file of four channels goes through the
command line's preflight and through the window's check. In order:
what the command line says and what it no longer says; that the
window keeps its line; and that what the command line says is what
the run does -- it folds the file to one channel, and a run sending it
to auphonic.com stops before the upload, as the advice says.
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
import contextlib, io, shutil, tempfile, time, wave
import numpy as np
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


# Its own folder under the run's TMPDIR, which the run throws away, and
# its own cache, so no answer another test stored stands in for this one.
WORK = tempfile.mkdtemp(prefix="vpm_wide_folded_")
os.environ["VPM_CACHE"] = os.path.join(WORK, "cache")
SR = 16000
# Four microphones on one recorder, each with a tone of its own.
t = np.arange(3 * SR) / float(SR)
FOUR = np.stack([np.sin(2 * np.pi * hz * t) * 0.3
                 for hz in (130, 190, 250, 310)], axis=1)
WIDE = os.path.join(WORK, "ZOOM0001_Tr1234.wav")
with wave.open(WIDE, "w") as f:
    f.setnchannels(4)
    f.setsampwidth(2)
    f.setframerate(SR)
    f.writeframes((FOUR * 20000).astype("<i2").tobytes())


class Call(object):
    """As much of a parsed command line as the preflight reads."""

    def __init__(self):
        self.out = WORK
        self.dry_run = True
        self.anyway = False
        self.lufs = None


seen = []
keep = (vpm.check_disk_space, vpm.report_findings)
vpm.check_disk_space = lambda *a, **k: []
vpm.report_findings = lambda found, *a, **k: (seen.extend(found), 0)[1]
try:
    vpm.run_preflight(Call(), [WIDE], [])
finally:
    vpm.check_disk_space, vpm.report_findings = keep
said = [b.text for b in seen]
window = [b.text for b in vpm.collect_findings([WIDE], [], True)]
ROWS = vpm.T('%s channels -- cut into tracks, see the rows above.') % "4"
FOLDED = vpm.T('%s channels -- the command line cuts none into tracks '
               'and folds the file to one channel, two people into one '
               'voice.') % "4"

print("1. What the command line says")
check("the command line points to no channel rows",
      ROWS not in said, "%d findings: %s" % (len(said), said[:4]))
check("it says the file is folded to one channel",
      FOLDED in said, "%d findings: %s" % (len(said), said[:4]))

print("\n2. The window keeps its line")
check("the window's check still points to the channel rows",
      ROWS in window, "%d findings: %s" % (len(window), window[:4]))

print("\n3. What it says is what the run does")
check("the run takes the file as one channel",
      vpm.kept_channels(WIDE) == 1,
      "%s channels kept of %s" % (vpm.kept_channels(WIDE),
                                  vpm.channel_count(WIDE)))
with contextlib.redirect_stdout(io.StringIO()) as printed:
    stops = vpm.too_wide_for_one_file([{"audio": WIDE}])
check("a run sending it to auphonic.com stops before the upload",
      stops is True, "answered %r, printed %r"
      % (stops, " ".join(printed.getvalue().split())[:120]))

shutil.rmtree(WORK, True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
