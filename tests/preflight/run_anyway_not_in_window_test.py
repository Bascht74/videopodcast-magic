# -*- coding: utf-8 -*-
"""In the window a preflight stop offers no --anyway, which it cannot pass.

report_findings in this process, over one reason to stop, with the
program's window flag set as the window sets it for its own run: the
window builds the command line itself and never writes --anyway onto
it, so a stop there that names the switch points at nothing. Its limit:
the flag is set by hand here, not by a window that was opened; that the
command line still offers the switch is run_finished_mix_refused's.
"""
PLATFORM_BOUND = False
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
import contextlib
import io
import time

began = time.time()
vpm = the_program.load()
vpm.set_language("en")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


STOPPED = vpm.T('\nStopped before the first long step.').strip()
REASON = vpm.Finding("abort", "Presenter.wav", "a reason to stop")

print("1. A reason to stop, reported while the window runs")
was = vpm.GUI_RUNNING
said = io.StringIO()
try:
    vpm.GUI_RUNNING = True
    with contextlib.redirect_stdout(said):
        stops = vpm.report_findings([REASON], "does the material fit "
                                    "together?", False)
finally:
    vpm.GUI_RUNNING = was
lines = vpm.strip_marks(said.getvalue()).strip().splitlines()
last = lines[-1].strip() if lines else ""
check("a stop in the window offers no --anyway",
      stops is True and last == STOPPED,
      "returned %r, last line %r against %r" % (stops, last, STOPPED))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
