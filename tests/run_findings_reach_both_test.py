# -*- coding: utf-8 -*-
"""Every preflight finding reaches the log and the pane, not just a count.

The window hangs each finding on its file, so the report used to print
the heading and the count alone while a window was up. The log has no
file rows, and "11 checked, 5 hints" names none of the five. In order:
what the log and the pane hold while a window is up and that the count
still stands under them; that the advice is the one thing the short
form drops; and that the console lost neither a finding nor an advice.

Dropping the advice is a contract and not a description of today: in
the window it hangs on the mark already, and printing it a second time
in full is what would make the log long.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import shutil
import sys
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


# One finding of each kind, two of them with advice under it. The names
# are roles and the numbers are invented: what is read back is whether a
# line arrived, never what it says. Both advices stay under seventy
# characters, so the report does not wrap them and they can be looked up
# whole.
FOUND = [
    vpm.Finding("good", "WideCam.mov", "25 fps -- 1920x1080, 45000 frames"),
    vpm.Finding("hint", "Bleed", "Guest is audible on Presenter at -32 dB",
                "Move the microphones apart, or set --apart."),
    vpm.Finding("hint", "Presenter.wav", "starts 4 s after the first camera"),
    vpm.Finding("fixed", "CoPresenter.wav", "channel 2 was silent, dropped"),
    vpm.Finding("abort", "Guest.wav", "48 kHz against 44.1 kHz on the rest",
                "Record at one rate, or resample before the run."),
]
TEXTS = [b.text for b in FOUND]
ADVICE = [b.advice for b in FOUND if b.advice]


def report(window_up):
    """The report as its two readers get it: the log file, and the pane.

    The same pair the run itself builds -- Redirect writes the marks
    into the pane and the plain text into the file behind the console.
    """
    folder = tempfile.mkdtemp(prefix="vpm_findings_")
    try:
        where = os.path.join(folder, "run.log")
        pane = []
        file = open(where, "w", buffering=1, encoding="utf-8")
        was, old = vpm.GUI_RUNNING, sys.stdout
        vpm.GUI_RUNNING = window_up
        sys.stdout = vpm.Redirect(file, pane.append)
        try:
            vpm.report_findings(list(FOUND), "does the material fit together?",
                                anyway=True)
        finally:
            sys.stdout = old
            vpm.GUI_RUNNING = was
            file.close()
        with open(where, encoding="utf-8") as f:
            return f.read(), "".join(pane)
    finally:
        shutil.rmtree(folder, ignore_errors=True)


print("1. While a window is up, both readers get every finding")
log, pane = report(True)
absent = [t for t in TEXTS if t not in log]
check("every finding of the report stands in the log",
      absent == [], "%d of %d missing from %d characters: %s"
      % (len(absent), len(TEXTS), len(log), absent[:2]))
gone = [t for t in TEXTS if t not in pane]
check("and every one of them stands in the pane beside it",
      gone == [], "%d of %d missing from %d characters: %s"
      % (len(gone), len(TEXTS), len(pane), gone[:2]))
counted = vpm.T('%d checked') % len(FOUND)
check("the count still stands under the findings it counts",
      counted in log, "wanted %r in %d characters of log"
      % (counted, len(log)))

print("\n2. And the short form is short: the advice stays out")
still = [a for a in ADVICE if a in log]
check("the advice under a finding stays out of the window's log",
      still == [], "%d of %d advices still there: %s"
      % (len(still), len(ADVICE), still[:1]))

print("\n3. On the console nothing was taken away")
log, pane = report(False)
missing = [a for a in ADVICE if a not in log]
check("without a window the advice stands under its finding",
      missing == [], "%d of %d missing from %d characters: %s"
      % (len(missing), len(ADVICE), len(log), missing[:1]))
nowhere = [t for t in TEXTS if t not in log]
check("and every finding is named there as well",
      nowhere == [], "%d of %d missing from %d characters: %s"
      % (len(nowhere), len(TEXTS), len(log), nowhere[:2]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
