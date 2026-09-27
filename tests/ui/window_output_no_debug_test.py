# -*- coding: utf-8 -*-
"""The window's own [GUI] lines reach the log file, never the Output tab.

The player and the preset box write down what they did, in English and
for whoever reads the log -- "cut pause at 0.000 s, WideCam...". During
a run stdout is the Output tab, so a line printed there appeared in it,
in the German window too. The stdout a run sets up is set up here, the
way the window's run loop does it, and one such line is written:

  * the Output tab does not get it
  * the log file does, with its mark

In memory: the tab is a list and the log file a string buffer.
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
import io
import time
import the_program

vpm = the_program.load()

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


LINE = "cut pause at 0.000 s, WideCam_01011855_C001.mov"
tab = []
log_file = io.StringIO()
behind = io.StringIO()
kept_aside = list(vpm._LOG_ASIDE)
old_out, old_err = sys.stdout, sys.stderr
try:
    # What the log file is while the window runs: the one handle the
    # aside lines go through.
    vpm._LOG_ASIDE[:] = [log_file]
    # What gui_run_loop puts in place for the length of a run.
    sys.stdout = sys.stderr = vpm.Redirect(behind, tab.append)
    vpm.gui_log(LINE)
finally:
    sys.stdout, sys.stderr = old_out, old_err
    vpm._LOG_ASIDE[:] = kept_aside

shown = "".join(tab)
check("the Output tab does not get a window line during a run",
      vpm.GUI_MARK not in shown and LINE not in shown,
      "the tab got %r" % shown[-160:])
written = log_file.getvalue()
check("the log file gets it, with its mark",
      vpm.GUI_MARK in written and LINE in written,
      "the log file got %r" % written[-160:])

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
