# -*- coding: utf-8 -*-
"""Every shot in the cut band stands at its time in its camera colour.

The band has no margins: a time is at width * t / length. The ruler and
the playhead are drawn over the colours, so a sample that lands on one
steps aside, never further than the shot's own pixels reach.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import sys, time, importlib.util
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtWidgets, QtCore, QtGui
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
m = importlib.util.module_from_spec(spec); sys.modules["vpm"] = m
spec.loader.exec_module(m)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# A conversation of three voices, taking turns, over ten minutes.
import random
random.seed(7)
names = ["Host", "Co-host", "Guest"]
segs = {n: [] for n in names}
t = 0.0
while t < 600:
    who = names[random.randrange(3)]
    d = random.uniform(1.5, 14.0)
    segs[who].append((round(t, 2), round(min(600.0, t + d), 2)))
    t += d + random.uniform(0.1, 0.8)
d = {"speakers": [{"name": n, "sections": segs[n]} for n in names],
     "cameras": [{"track": "Hosts", "speakers": ["Host", "Co-host"]},
                 {"track": "Guest", "speakers": ["Guest"]},
                 {"track": "Wide", "speakers": []}],
     "length_s": 600.0}
LENGTH = 600.0
numbers = m.cut_statistics(d, 1.2, 0.3, 45.0, 2.5, 120.0, True)
cut = list(numbers["cut"] or [])
colours = numbers["colours"]
print("Shots:", numbers["shots"])
print("Colours:", colours)

check("a cut list came back", bool(cut), "%d shots" % len(cut))
check("one entry per shot", len(cut) == numbers["shots"],
      "%d entries, %d shots" % (len(cut), numbers["shots"]))
check("a colour for every camera",
      set(colours) == {"Hosts", "Guest", "Wide"},
      ", ".join(sorted(colours)))
check("no colour handed out twice",
      len(set(colours.values())) == len(colours),
      "%d distinct of %d" % (len(set(colours.values())), len(colours)))
check("the wide shot keeps the tan of the palette",
      colours.get("Wide") == m.CLIP_COLOURS_RGB["Tan"],
      "%s, expected %s" % (colours.get("Wide"),
                           m.CLIP_COLOURS_RGB["Tan"]))

WIDE, HIGH = 1200, 46
CutBand = m.qt_cut_band(QtCore, QtGui, QtWidgets, QtCore.Qt)
# What the widget looks like with nothing in it, so the check below
# reads its own idea of empty out of the program rather than a colour
# written down here.
blank = CutBand()
blank.resize(WIDE, HIGH)
BACK = blank.grab().toImage().pixelColor(0, 0).name()
band = CutBand()
band.resize(WIDE, HIGH)
band.set(cut, colours, LENGTH)
band.label_set(210.0)
# A by-product for looking at, not part of the check. Same place as the
# window scripts write to, so the pictures of one run sit together.
shots = os.environ.get("VPM_SHOTS") or os.path.join(HERE, "shots")
os.makedirs(shots, exist_ok=True)
band.grab().save(os.path.join(shots, "5_cut_band.png"))

video = band.grab().toImage()
MIDDLE = HIGH // 2
painted = set(QtGui.QColor(c).name() for c in colours.values())
row = [x for x in range(WIDE)
       if video.pixelColor(x, MIDDLE).name() != BACK]
column = [y for y in range(HIGH)
          if video.pixelColor(7, y).name() != BACK]
check("the band fills the widget", len(row) == WIDE and len(column) == HIGH,
      "x %d of %d, y %d of %d, empty is %s"
      % (len(row), WIDE, len(column), HIGH, BACK))

# The band may claim three colours and still paint only two, so look
# for each of them in the picture itself.
seen = set()
for x in range(0, WIDE, 3):
    name = video.pixelColor(x, MIDDLE).name()
    if name in painted:
        seen.add(name)
check("all three colours stand in the picture", seen == painted,
      "%d of %d: %s" % (len(seen), len(painted), ", ".join(sorted(seen))))


def sample(x, x0, x1):
    """The camera colour at x, past a ruler line or the playhead."""
    for step in (0, 1, -1, 2, -2):
        near = x + step
        if x0 <= near < x1:
            got = video.pixelColor(near, MIDDLE).name()
            if got in painted:
                return got
    return video.pixelColor(x, MIDDLE).name()


# One check over all of them: a line per shot would bury the FAIL line
# the build machine greps out, and the first mismatch says as much.
right, first = 0, ""
for a, b, who in cut:
    x0 = int(WIDE * a / LENGTH)
    x1 = min(WIDE, max(x0 + 1, int(WIDE * b / LENGTH)))
    middle = (a + b) / 2.0
    x = min(WIDE - 1, int(WIDE * middle / LENGTH))
    got = sample(x, x0, x1)
    want = QtGui.QColor(colours[who]).name()
    if got == want:
        right += 1
    elif not first:
        first = "; first miss %s at %.1f s, x=%d is %s not %s" % (
            who, middle, x, got, want)
check("every shot at its own time in its own colour", right == len(cut),
      "%d of %d%s" % (right, len(cut), first))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
