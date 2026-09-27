# -*- coding: utf-8 -*-
"""The window refuses an In and Out point where the run does, in its words.

The run judges a hand-set window in clip_to_time_window, the window's
trimming in apply_time_window; each pair below goes to both, and both
have to come back with the same refusal, word for word. "Before" is an
Out point in front of the In point, "on" one on it, "short" one under
five seconds after it, "past" both behind the material in the wrong
order, and "pulled back" an Out point that leaves under five seconds
once it is pulled back into the material. "Five seconds" is the
control: both take it. Relative points only; timecodes are
time_point_pulled_back's.
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
SCRIPT = the_program.SCRIPT
import contextlib, io, time
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


# Ten minutes of material: 0 to 600 s for the run, length_s for the window.
LENGTH = 600.0
HANDOVER = {"start_s": 1000.0, "length_s": LENGTH, "fps": 30.0,
            "speakers": []}
BEFORE = vpm.T('    Out point lies before In point -- that does not '
               'work.').strip()
SHORT = (vpm.T('    The window would be only %s long -- that cannot be '
               'intended.') % vpm.as_hms(3.0)).strip()


class Call(object):
    """What a call says about the window: an In point and an Out point."""

    def __init__(self, first="", last=""):
        self.in_point = first
        self.out_point = last


def both(first, last):
    """What the run and the window say to one pair.

    The run's answer is the last line it prints, the window's the
    complaint apply_time_window hands back; the run's window comes too,
    so a refusal is also seen to stop it.
    """
    told = io.StringIO()
    with contextlib.redirect_stdout(told):
        got = vpm.clip_to_time_window(Call(first, last), 0.0, LENGTH, None)
    lines = [x.strip() for x in told.getvalue().splitlines() if x.strip()]
    _d, complaint = vpm.apply_time_window(dict(HANDOVER), first, last)
    return got, (lines[-1] if lines else ""), complaint


def said(got, run, window, wanted):
    return ("run %s saying %r, window saying %r, wanted %r"
            % (got, run, window, wanted))


print("1. Out point in front of the In point, and on it")
got, run, window = both("+2:00", "+1:00")
check("before: the window refuses it in the run's words",
      got == (None, None) and run == BEFORE and window == BEFORE,
      said(got, run, window, BEFORE))
got, run, window = both("+1:00", "+1:00")
check("on: the window refuses it in the run's words",
      got == (None, None) and run == BEFORE and window == BEFORE,
      said(got, run, window, BEFORE))
got, run, window = both("+15:00", "+12:00")
check("past: behind the material the order is judged first",
      got == (None, None) and run == BEFORE and window == BEFORE,
      said(got, run, window, BEFORE))

print("\n2. Out point just after the In point")
got, run, window = both("+1:00", "+1:03")
check("short: three seconds are refused in the run's words",
      got == (None, None) and run == SHORT and window == SHORT,
      said(got, run, window, SHORT))
got, run, window = both("+9:57", "+10:30")
check("pulled back: three seconds left inside are refused alike",
      got == (None, None) and run == SHORT and window == SHORT,
      said(got, run, window, SHORT))
got, run, window = both("+1:00", "+1:05")
check("five seconds: both take the window",
      got == (60.0, 65.0) and window == "",
      "run %s, wanted (60.0, 65.0); window saying %r, wanted ''"
      % (got, window))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
