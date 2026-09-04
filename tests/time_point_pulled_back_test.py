# -*- coding: utf-8 -*-
"""A hand-set In or Out point never reaches past what every camera saw.

The window handed on is the stretch every camera saw; a point typed in
is pulled back into it, and one that would leave less than five seconds
is refused outright. Both together are what keeps a camera from being
delivered as a sliver of picture, which is what the floor under the kept
length would otherwise make of it. "Inside" is the control, "pulled
back" the two ends, and "refused" the two ways out.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import contextlib, io, sys, time
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


# The window every camera saw, as the measurement hands it over.
SHARED_FROM, SHARED_TO = 0.0, 38.0
# The reference camera, for the points written as a timecode. Only its
# frame rate and its own timecode are ever read.
REFERENCE = ("WideCam.mov", {"fps": 25.0, "tc": "10:00:00:00"})


class Call(object):
    """What a call says about the window: an In point and an Out point."""

    def __init__(self, first="", last=""):
        self.in_point = first
        self.out_point = last


def window(first, last, reference=None):
    """The window that call comes to, and the last of what it said.

    The whole report would carry the two points back into the failure
    line, where they already stand; the end of it is the sentence that
    says what became of them.
    """
    told = io.StringIO()
    with contextlib.redirect_stdout(told):
        got = vpm.clip_to_time_window(Call(first, last), SHARED_FROM,
                                      SHARED_TO, reference)
    spoken = [x.strip() for x in told.getvalue().splitlines() if x.strip()]
    return got, " | ".join(spoken[-2:])


print("1. A window inside the shared one is taken as it is")
inside, told = window("+5", "+30")
check("a point that asks for less than there is stands",
      inside == (5.0, 30.0), "%s, wanted (5.0, 30.0) -- %s" % (inside, told))

print("\n2. A point past the end is pulled back")
late, told = window("+5", "+44")
check("an Out point after the last shared frame is pulled back to it",
      late == (5.0, SHARED_TO),
      "%s, wanted (5.0, %.1f) -- %s" % (late, SHARED_TO, told))
early, told = window("09:59:00:00", "+30", REFERENCE)
check("an In point before the first shared frame is pulled forward to it",
      early == (SHARED_FROM, 30.0),
      "%s, wanted (%.1f, 30.0) -- %s" % (early, SHARED_FROM, told))

print("\n3. And where nothing is left, the run does not start")
nothing, told = window("+40", "+44")
check("a window with no picture left in it is refused",
      nothing == (None, None), "%s, wanted (None, None) -- %s"
      % (nothing, told))
narrow, told = window("+10", "+14")
check("and one under five seconds is refused too",
      narrow == (None, None), "%s, wanted (None, None) -- %s"
      % (narrow, told))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
