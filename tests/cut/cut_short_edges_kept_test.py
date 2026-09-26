# -*- coding: utf-8 -*-
"""A too long wide edge is shortened, to a third or the latest setting.

Through camera_cut, the way preview and run both build the cut. Thirty
seconds whose announcements both run past a third: it begins and ends
on the wide shot, each edge stops at the third, no shot falls under the
minimum edit duration, and the log says so. The mixedcase voices over a
minute keep their edges and say nothing. Half an hour: each edge stops
at "Wide shot at the latest", and at a lower setting at that one.
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
import contextlib
import io
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


CAMERA_OF = {"Host": "HostCam", "Guest": "GuestCam"}
SHORTEST = 3.0
SHORTENED = vpm.T('  shortened to at most %s each -- the first '
                  'announcement ends at %s, the last begins at %s')


def cut_and_log(tracks, length, latest=120.0):
    """The cut with the wide shot at the edges, and what it printed."""
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        cut = vpm.camera_cut(tracks, length, CAMERA_OF, "Wide", SHORTEST,
                             0.3, after=0.0, holds=5.0, at_latest=latest,
                             edge=True, rules=None, faint=False)
    return [(round(a, 3), round(b, 3), who) for a, b, who in cut], \
        said.getvalue()


def shot(cut, i):
    """One shot written out for the failure line."""
    return "%s %.1f-%.1f" % (cut[i][2], cut[i][0], cut[i][1]) \
        if cut else "no cut"


print("1. Thirty seconds, both announcements longer than a third")
# The host talks most; the guest's one stretch runs from 11.5 to 21 s,
# so it is the first and the last announcement at once, and each edge
# would be longer than ten seconds. Cut at the third, the host is left
# 1.8 s before the guest, too short for a shot of its own.
short, short_log = cut_and_log([("Host", [(0.0, 11.5), (21.0, 30.0)]),
                                ("Guest", [(11.5, 21.0)])], 30.0)
check("a short recording still begins on the wide shot",
      bool(short) and short[0][2] == "Wide", "first %s" % shot(short, 0))
check("and still ends on it",
      bool(short) and short[-1][2] == "Wide", "last %s" % shot(short, -1))
check("the opening wide shot stops at a third of the length",
      bool(short) and short[0][2] == "Wide" and short[0][1] == 10.0,
      "first %s, wanted Wide 0.0-10.0" % shot(short, 0))
check("the closing wide shot begins a third before the end",
      bool(short) and short[-1][2] == "Wide" and short[-1][0] == 20.0,
      "last %s, wanted Wide 20.0-30.0" % shot(short, -1))
check("no shot of the shortened cut is under the minimum edit duration",
      bool(short) and min(b - a for a, b, _w in short) >= SHORTEST,
      "shots %s against a minimum of %.1f s"
      % ([shot(short, i) for i in range(len(short))], SHORTEST))
want = SHORTENED % (vpm.as_hms(10.0), vpm.as_hms(21.0), vpm.as_hms(11.5))
check("the log says the edges were shortened, and where the talk lies",
      short_log.count(want) == 1,
      "%r stands %d times in the log, wanted 1" % (want,
                                                   short_log.count(want)))

print("\n2. A minute, no edge too long")
# The two voices of the mixedcase fixture: the presenter's first turn
# ends at 12.5 s and the last begins at 49.5 s, both inside a third.
G = [(1.0, 6.0), (14.0, 20.0), (29.0, 34.5), (43.0, 48.0), (55.0, 59.5)]
P = [(7.5, 12.5), (21.5, 27.5), (36.0, 41.5), (49.5, 53.5)]
long_cut, long_log = cut_and_log([("Guest", G), ("Host", P)], 60.0)
check("a long enough recording holds the opening to its announcement",
      bool(long_cut) and long_cut[0][2] == "Wide"
      and long_cut[0][1] == 12.5,
      "first %s, wanted Wide 0.0-12.5" % shot(long_cut, 0))
lead = SHORTENED.split("%s")[0]
check("and says nothing about shortening",
      long_log.count(lead) == 0,
      "%r stands %d times in the log, wanted 0" % (lead,
                                                   long_log.count(lead)))

print("\n3. Half an hour, the other voice from 15:00 to 25:00")
# A third would be ten minutes of wide shot at each end; the setting
# the cut is handed, not the constant behind its starting value, caps it.
HALF = [("Host", [(0.0, 900.0), (1500.0, 1800.0)]),
        ("Guest", [(900.0, 1500.0)])]
half, _half_log = cut_and_log(HALF, 1800.0)
check("a long recording's opening wide shot stops at the latest setting",
      bool(half) and half[0] == (0.0, 120.0, "Wide"),
      "first %s, wanted Wide 0.0-120.0" % shot(half, 0))
check("and its closing one begins that long before the end",
      bool(half) and half[-1] == (1680.0, 1800.0, "Wide"),
      "last %s, wanted Wide 1680.0-1800.0" % shot(half, -1))
low, _low_log = cut_and_log(HALF, 1800.0, latest=60.0)
check("a lower latest setting holds both edges to it",
      bool(low) and low[0] == (0.0, 60.0, "Wide")
      and low[-1] == (1740.0, 1800.0, "Wide"),
      "first %s, last %s, wanted Wide 0.0-60.0 and Wide 1740.0-1800.0"
      % (shot(low, 0), shot(low, -1)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
