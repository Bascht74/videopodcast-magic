# -*- coding: utf-8 -*-
"""Speaker markers land on the frame of each turn, one per frame.

add_speaker_markers against a stand-in timeline that, like Resolve,
refuses a second marker on a frame already taken. Each turn is held to
its frame, on the cut timeline and on the multicam one that begins
earlier; two turns on one frame become one marker naming both; a taken
frame moves a marker on, and one with no free frame is counted and said;
each person keeps one colour.
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


class TL(object):
    """A timeline that keeps its markers and refuses a frame taken twice."""

    def __init__(self, refused=()):
        """No markers yet; *refused* are frames it will never take."""
        self.marks = {}
        self.refused = set(refused)

    def AddMarker(self, frame, colour, name, note, length):
        """Keep the marker, or answer False as Resolve does if taken."""
        if frame in self.marks or frame in self.refused:
            return False
        self.marks[frame] = (colour, name, length)
        return True


D = {"fps": 25.0, "start_tc": "00:00:00:00"}
TURNS = [{"name": "A", "sections": [(2.0, 5.0), (10.0, 12.0)]},
         {"name": "B", "sections": [(6.0, 8.0)]}]


def place(speaker, from_s=0.0, refused=()):
    """Markers on a fresh stand-in: (the timeline, what was printed)."""
    tl = TL(refused)
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        vpm.add_speaker_markers(tl, speaker, D, from_s)
    return tl, said.getvalue()


print("Where each marker lands")
tl, _said = place(TURNS)
check("every turn gets a marker on its frame",
      sorted(tl.marks) == [50, 150, 250],
      "markers at %s against [50, 150, 250]" % sorted(tl.marks))
tl, _said = place(TURNS, from_s=-4.0)
check("on the multicam timeline the marker moves by its start",
      sorted(tl.marks) == [150, 250, 350],
      "markers at %s against [150, 250, 350]" % sorted(tl.marks))
tl, _said = place([{"name": "A", "sections": [(20.0, 22.0)]},
                   {"name": "B", "sections": [(20.0, 21.0)]}])
names = [tl.marks[f][1] for f in sorted(tl.marks)]
check("two turns on one frame become one marker naming both",
      names == ["A + B"], "markers named %s against ['A + B']" % names)

print("\nA frame already taken")
tl, _said = place(TURNS, refused={50})
check("a taken frame moves the marker on by one",
      sorted(tl.marks) == [51, 150, 250],
      "markers at %s against [51, 150, 250]" % sorted(tl.marks))
tl, said = place(TURNS, refused=set(range(50, 60)))
lost = vpm.T(', %s not (no free picture)') % vpm.number_text(1, 0)
check("a marker with no free frame is counted as lost and said",
      lost in said and sorted(tl.marks) == [150, 250],
      "%r %s; markers at %s against [150, 250]"
      % (lost, "said" if lost in said else "not said", sorted(tl.marks)))

print("\nColours")
tl, _said = place(TURNS)
colours = [tl.marks[f][0] for f in sorted(tl.marks)]
want = [vpm.MARKER_COLOURS[0], vpm.MARKER_COLOURS[1], vpm.MARKER_COLOURS[0]]
check("each person keeps one colour", colours == want,
      "colours %s against %s" % (colours, want))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
