# -*- coding: utf-8 -*-
"""A window set by In and Out is cut as though it were the whole recording.

A recording, and the same one with talk before and after it, the window
set around it by timecode and taken. With the wide shot at the edges
both begin and end on it and agree shot for shot; without, the window
begins and ends on a speaker's camera and still agrees. Then a window
too short for a greeting against a recording just that long. Through
apply_time_window and cut_statistics; the run trims its material in the
pipeline, which this does not reach.
"""
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


CAMERAS = [{"track": "HostCam", "speakers": ["Host"]},
           {"track": "GuestCam", "speakers": ["Guest"]},
           {"track": "Wide", "speakers": []}]
# Four minutes: the host greets, the guest talks most, the host asks
# three times and says goodbye. Seconds of the recording.
HOST = [(2.0, 18.0), (40.0, 50.0), (90.0, 100.0), (150.0, 160.0),
        (222.0, 240.0)]
GUEST = [(20.0, 38.0), (52.0, 88.0), (102.0, 148.0), (162.0, 220.0)]
# The same four minutes a minute into a take of six, with talk before
# the greeting and after the goodbye.
AHEAD = 60.0
HOST_TAKE = [(30.0, 55.0)] + [(a + AHEAD, b + AHEAD) for a, b in HOST] \
    + [(305.0, 320.0)]
GUEST_TAKE = [(5.0, 25.0)] + [(a + AHEAD, b + AHEAD) for a, b in GUEST] \
    + [(325.0, 355.0)]


def handover(host, guest, length, start_s):
    """A handover file the way the run writes it, at 25 frames."""
    return {"speakers": [{"name": "Host", "sections": [list(x) for x in host]},
                         {"name": "Guest",
                          "sections": [list(x) for x in guest]}],
            "cameras": [dict(c) for c in CAMERAS], "length_s": length,
            "start_s": start_s, "fps": 25.0,
            "start_tc": vpm.timecode_string(start_s, 25.0)}


def cut_of(d, edge):
    """The cut the preview shows, rounded to the millisecond."""
    numbers = vpm.cut_statistics(d, edge=edge)
    return [(round(a, 3), round(b, 3), who)
            for a, b, who in (numbers or {}).get("cut") or []]


def shot(cut, i):
    """One shot written out for the failure line."""
    return "%s %.1f-%.1f" % (cut[i][2], cut[i][0], cut[i][1]) \
        if cut else "no cut"


whole = handover(HOST, GUEST, 240.0, 36000.0 + AHEAD)
take = handover(HOST_TAKE, GUEST_TAKE, 360.0, 36000.0)
window, said = vpm.apply_time_window(take, "10:01:00:00", "10:05:00:00")
check("In and Out around the recording are taken", not said and
      abs(window.get("length_s", 0) - 240.0) < 0.001,
      "complaint %r, length %s s against 240" % (said,
                                                window.get("length_s")))

print("1. With the wide shot at the edges")
on_whole, on_window = cut_of(whole, True), cut_of(window, True)
check("the whole recording begins and ends on the wide shot",
      bool(on_whole) and on_whole[0][2] == "Wide"
      and on_whole[-1][2] == "Wide",
      "first %s, last %s" % (shot(on_whole, 0), shot(on_whole, -1)))
check("the window begins on the wide shot at In",
      bool(on_window) and on_window[0][2] == "Wide"
      and on_window[0][0] == 0.0, "first %s" % shot(on_window, 0))
check("the window ends on the wide shot at Out",
      bool(on_window) and on_window[-1][2] == "Wide"
      and on_window[-1][1] == 240.0, "last %s" % shot(on_window, -1))
differ = [i for i, (x, y) in enumerate(zip(on_whole, on_window)) if x != y]
check("the window's cut is the whole recording's, shot for shot",
      bool(on_whole) and on_whole == on_window,
      "%d shots against %d, first difference at %s: %s against %s"
      % (len(on_window), len(on_whole), differ[:1],
         shot(on_window, differ[0]) if differ else "-",
         shot(on_whole, differ[0]) if differ else "-"))

print("\n2. Without it")
off_whole, off_window = cut_of(whole, False), cut_of(window, False)
check("with the tick off the window begins on a speaker's camera",
      bool(off_window) and off_window[0][2] != "Wide",
      "first %s" % shot(off_window, 0))
check("with the tick off the window ends on a speaker's camera",
      bool(off_window) and off_window[-1][2] != "Wide",
      "last %s" % shot(off_window, -1))
check("with the tick off too the window's cut is the whole one's",
      bool(off_whole) and off_whole == off_window,
      "%d shots against %d, first %s against %s"
      % (len(off_window), len(off_whole), shot(off_window, 0),
         shot(off_whole, 0)))

print("\n3. A window too short for a greeting")
# The two voices of the mixedcase fixture, and the window the concept
# run set on them: thirty seconds, the first handover twelve and a half
# in. Cut short there, a recording of just those thirty seconds is cut
# alike -- whatever the rule for a greeting says about them.
G = [(1.0, 6.0), (14.0, 20.0), (29.0, 34.5), (43.0, 48.0), (55.0, 59.5)]
P = [(7.5, 12.5), (21.5, 27.5), (36.0, 41.5), (49.5, 53.5)]


def inside(segs, a, b):
    """The turns inside [a, b], counted from a."""
    return [(max(x, a) - a, min(y, b) - a) for x, y in segs
            if y > a and x < b]


short, said = vpm.apply_time_window(handover(P, G, 60.0, 36000.0),
                                    "10:00:15:00", "10:00:45:00")
alone = handover(inside(P, 15.0, 45.0), inside(G, 15.0, 45.0), 30.0,
                 36015.0)
short_cut, alone_cut = cut_of(short, True), cut_of(alone, True)
check("a short window is cut as a recording of its length is",
      not said and bool(alone_cut) and short_cut == alone_cut,
      "complaint %r; window first %s last %s, recording first %s last %s"
      % (said, shot(short_cut, 0), shot(short_cut, -1),
         shot(alone_cut, 0), shot(alone_cut, -1)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
