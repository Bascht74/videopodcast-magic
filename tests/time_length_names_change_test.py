# -*- coding: utf-8 -*-
"""The length line names the measured window only where it differs.

The bracket after the length says "yours instead of the measured one".
An Out point past the last frame is pulled back to that frame, and then
the bracket repeats the number standing in front of it -- under a line
that has just said the measured window is being kept. In order: a
window really cut, one pulled back to the whole of it, and the German
run, which needs a wording of its own for the short line.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import contextlib
import io
import sys
import time

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


# The window every camera saw, as the measurement hands it over: an
# hour and a half, so a point two hours in lies well past the last
# frame and a shorter one is plainly shorter.
MEASURED_FROM, MEASURED_TO = 0.0, 5191.601


class Call(object):
    """What a call says about the window: an In point and an Out point."""

    def __init__(self, first="", last=""):
        self.in_point = first
        self.out_point = last


def last_line(first, last, language="en"):
    """The window, and the line the block about it ends on."""
    vpm.set_language(language)
    told = io.StringIO()
    with contextlib.redirect_stdout(told):
        window = vpm.clip_to_time_window(Call(first, last), MEASURED_FROM,
                                         MEASURED_TO, None)
    spoken = [x for x in told.getvalue().splitlines() if x.strip()]
    return window, spoken[-1] if spoken else ""


def whole():
    """The measured length, written the way the run writes it."""
    return vpm.as_hms(MEASURED_TO - MEASURED_FROM)


print("1. A window that really was cut names the measured one beside it")
window, said = last_line("+5", "+1:00:00")
check("a shorter window names a second length beside its own",
      said.count("(") == 1, "%r for the window %s" % (said, window))
# A refused window comes back as (None, None). Read straight, that
# would end the file in a traceback and take the three checks below
# with it, so it turns into a length nothing can hold instead.
mine = vpm.as_hms(window[1] - window[0]) if None not in window else "no window"
check("and that line holds the kept length and the measured one",
      mine in said and whole() in said,
      "%r, wanted %s and %s in it" % (said, mine, whole()))

print("\n2. A point pulled back to the last frame drops the bracket")
window, said = last_line("", "+2:00:00")
check("a window pulled back to the whole of it names no second length",
      "(" not in said, "%r for the window %s" % (said, window))
check("and that line still says how long the window is",
      whole() in said, "%r, wanted %s in it" % (said, whole()))

print("\n3. The German run has a wording for the short line too")
english = vpm.T('    Length  %s').split("%s")[0].strip()
_window, german_said = last_line("", "+2:00:00", "de")
german = vpm.T('    Length  %s').split("%s")[0].strip()
vpm.set_language("en")
check("the German run says the short line in its own words",
      german != english and german_said.strip().startswith(german),
      "%r begins %r, and the English is %r"
      % (german_said, german, english))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
