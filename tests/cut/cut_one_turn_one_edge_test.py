# -*- coding: utf-8 -*-
"""A voice that speaks once gets the wide edge nearer to it, not both.

Through camera_cut, the way preview and run both build the cut, over a
minute at a shortest shot of five seconds. The guest's one turn near
the start: the cut opens on the wide shot and closes on the host, and
the log says there is no closing edge because the voice spoke once.
Near the end, the other way round. Last, the one edge shorter than the
shortest shot: it goes in the merging, and the log says so.
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
SHORTEST = 5.0
ONLY_UNTIL = vpm.T('  Wide shot at the edges: only until %s -- the other '
                   'voice speaks only once, near the start, so there is '
                   'no closing one')
ONLY_FROM = vpm.T('  Wide shot at the edges: only from %s -- the other '
                  'voice speaks only once, near the end, so there is no '
                  'opening one')
NONE = vpm.T('  Wide shot at the edges: none -- the other voice speaks '
             'only once, and that one edge was shorter than the shortest '
             'shot')
LEAD = os.path.commonprefix([ONLY_UNTIL, ONLY_FROM, NONE])


def cut_and_log(tracks, length):
    """The cut with the wide shot at the edges, and its edge lines."""
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        cut = vpm.camera_cut(tracks, length, CAMERA_OF, "Wide", SHORTEST,
                             0.0, after=0.0, holds=5.0, at_latest=120.0,
                             edge=True, rules=None, faint=False)
    lines = [x for x in said.getvalue().splitlines() if x.startswith(LEAD)]
    return [(round(a, 3), round(b, 3), who) for a, b, who in cut], lines


def shot(cut, i):
    """One shot written out for the failure line."""
    return "%s %.1f-%.1f" % (cut[i][2], cut[i][0], cut[i][1]) \
        if cut else "no cut"


print("1. The guest speaks once, near the start")
# Nine seconds from 0:03: three seconds from the start, 48 from the end.
early, early_log = cut_and_log([("Guest", [(3.0, 12.0)]),
                                ("Host", [(0.0, 3.0), (12.0, 60.0)])], 60.0)
check("one turn near the start opens the cut on the wide shot",
      bool(early) and early[0] == (0.0, 12.0, "Wide"),
      "first %s, wanted Wide 0.0-12.0" % shot(early, 0))
check("and no closing wide edge runs from it to the end",
      bool(early) and early[-1][2] != "Wide",
      "last %s, wanted a camera and not the wide shot" % shot(early, -1))
want = ONLY_UNTIL % vpm.as_hms(12.0)
check("the log says the one turn made only the opening edge",
      early_log == [want], "the log says %r, wanted [%r]" % (early_log, want))

print("\n2. The guest speaks once, near the end")
# Nine seconds from 0:48: 48 seconds from the start, three from the end.
late, late_log = cut_and_log([("Guest", [(48.0, 57.0)]),
                              ("Host", [(0.0, 48.0), (57.0, 60.0)])], 60.0)
check("one turn near the end closes the cut on the wide shot",
      bool(late) and late[-1] == (48.0, 60.0, "Wide"),
      "last %s, wanted Wide 48.0-60.0" % shot(late, -1))
check("and no opening wide edge runs to it from the start",
      bool(late) and late[0][2] != "Wide",
      "first %s, wanted a camera and not the wide shot" % shot(late, 0))
want = ONLY_FROM % vpm.as_hms(48.0)
check("the log says the one turn made only the closing edge",
      late_log == [want], "the log says %r, wanted [%r]" % (late_log, want))

print("\n3. The one edge shorter than the shortest shot")
# The guest's turn ends 4.5 s in: the opening edge would be shorter than
# five seconds and goes into the host's shot after it.
brief, brief_log = cut_and_log([("Guest", [(0.0, 4.5)]),
                                ("Host", [(4.5, 60.0)])], 60.0)
check("the log says the one edge went and names no other",
      brief_log == [NONE] and brief == [(0.0, 60.0, "HostCam")],
      "cut %s, the log says %r, wanted [(0.0, 60.0, 'HostCam')] and [%r]"
      % (brief, brief_log, NONE))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
