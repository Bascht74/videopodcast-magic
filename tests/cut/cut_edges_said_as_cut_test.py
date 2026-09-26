# -*- coding: utf-8 -*-
"""The log names the wide edges the finished cut has, not the ones laid.

Through camera_cut, the way preview and run both build the cut, at a
shortest shot of five seconds. Both edges long enough: the line names
where they stand. The opening edge shorter than the shortest shot: it
goes in the merging, and the line says only the closing one stands;
the closing edge too short, only the opening one. Both too short: the
line says none stands.
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
BOTH = vpm.T('  Wide shot at the edges: until %s and from %s')
ONLY_FROM = vpm.T('  Wide shot at the edges: only from %s -- the opening '
                  'one was shorter than the shortest shot and went into '
                  'the next')
ONLY_UNTIL = vpm.T('  Wide shot at the edges: only until %s -- the '
                   'closing one was shorter than the shortest shot and '
                   'went into the one before')
NONE = vpm.T('  Wide shot at the edges: none -- both were shorter than '
             'the shortest shot and went into their neighbours')
# What the four lines begin with alike.
LEAD = os.path.commonprefix([BOTH, ONLY_FROM, ONLY_UNTIL, NONE])


def cut_and_log(tracks, length):
    """The cut with the wide shot at the edges, and what it printed."""
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        cut = vpm.camera_cut(tracks, length, CAMERA_OF, "Wide", SHORTEST,
                             0.0, after=0.0, holds=5.0, at_latest=120.0,
                             edge=True, rules=None, faint=False)
    return [(round(a, 3), round(b, 3), who) for a, b, who in cut], \
        said.getvalue()


def edge_lines(log):
    """The lines of the log that speak of the edges."""
    return [line for line in log.splitlines() if line.startswith(LEAD)]


print("1. A minute, both edges longer than the shortest shot")
# The guest greets for eight seconds and says goodbye in the last ten;
# the host talks in between. Both edges outlast five seconds.
whole, whole_log = cut_and_log([("Guest", [(0.0, 8.0), (50.0, 60.0)]),
                                ("Host", [(8.0, 50.0)])], 60.0)
want = BOTH % (vpm.as_hms(8.0), vpm.as_hms(50.0))
check("where both edges stand, the line names where they end and begin",
      edge_lines(whole_log) == [want],
      "the log says %r, wanted [%r] -- cut %s"
      % (edge_lines(whole_log), want, whole))

print("\n2. The opening edge shorter than the shortest shot")
# The greeting lasts 4.5 s, under the five-second shortest shot: the
# merging hands it to the host's camera, and the cut opens on that.
lost, lost_log = cut_and_log([("Guest", [(0.0, 4.5), (50.0, 60.0)]),
                              ("Host", [(4.5, 50.0)])], 60.0)
check("the cut opens on the host, so the opening edge is gone",
      bool(lost) and lost[0] == (0.0, 50.0, "HostCam"),
      "first shot %s, wanted (0.0, 50.0, 'HostCam')"
      % (lost[0] if lost else "none",))
want = ONLY_FROM % vpm.as_hms(50.0)
check("a merged-away opening edge is not named in the log",
      edge_lines(lost_log) == [want],
      "the log says %r, wanted [%r]" % (edge_lines(lost_log), want))

print("\n3. The closing edge shorter than the shortest shot")
# The greeting stands; the goodbye lasts 4.5 s and goes into the host.
end_lost, end_log = cut_and_log([("Guest", [(0.0, 8.0), (55.5, 60.0)]),
                                 ("Host", [(8.0, 55.5)])], 60.0)
check("the cut closes on the host, so the closing edge is gone",
      bool(end_lost) and end_lost[-1] == (8.0, 60.0, "HostCam"),
      "last shot %s, wanted (8.0, 60.0, 'HostCam')"
      % (end_lost[-1] if end_lost else "none",))
want = ONLY_UNTIL % vpm.as_hms(8.0)
check("a merged-away closing edge is not named in the log",
      edge_lines(end_log) == [want],
      "the log says %r, wanted [%r]" % (edge_lines(end_log), want))

print("\n4. Both edges shorter than the shortest shot")
# 4.5 s at each end: both go, and the whole minute is the host's.
gone, gone_log = cut_and_log([("Guest", [(0.0, 4.5), (55.5, 60.0)]),
                              ("Host", [(4.5, 55.5)])], 60.0)
check("the cut holds no wide shot at all",
      gone == [(0.0, 60.0, "HostCam")],
      "cut %s, wanted [(0.0, 60.0, 'HostCam')]" % (gone,))
check("where both edges went, the log says none stands",
      edge_lines(gone_log) == [NONE],
      "the log says %r, wanted [%r]" % (edge_lines(gone_log), NONE))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
