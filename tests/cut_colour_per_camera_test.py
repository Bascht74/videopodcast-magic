# -*- coding: utf-8 -*-
"""Clip colours: one per angle, and the same one every time.

The colour tells the cutter at a glance which camera a clip comes
from, so every clip of one camera carries the same colour and two
cameras never share one while colours are left. Resolve accepts only
its own sixteen names and refuses anything else silently, so the run
finds out which ones an installation takes rather than trusting a list.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys, time
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# Resolve takes only these names. The set is swapped below to see what
# happens on an installation that knows fewer of them.
REAL_COLOURS = {"Orange", "Apricot", "Yellow", "Lime", "Olive", "Green",
                "Teal", "Navy", "Blue", "Purple", "Violet", "Pink", "Tan",
                "Beige", "Brown", "Chocolate"}


class Item(object):
    """One clip in the timeline, as much of it as the colouring needs."""

    def __init__(self, name):
        self.name = name
        self.colour = None

    def GetName(self):
        return self.name

    def GetClipColor(self):
        return self.colour

    def ClearClipColor(self):
        self.colour = None
        return True

    def SetClipColor(self, wanted):
        if wanted in REAL_COLOURS:
            self.colour = wanted
            return True
        return False


class TL(object):
    def __init__(self, item):
        self.item = item

    def GetTrackCount(self, kind):
        return 1

    def GetItemListInTrack(self, kind, track):
        return self.item


PER_CAMERA = 3


def run(speaker_count):
    """Colour a timeline of one wide shot and this many speakers."""
    cameras = [{"camera": "Wide", "track": "Wide", "file": "W.mov",
                "source": "W.mov", "wide": True}]
    for i in range(speaker_count):
        cameras.append({"camera": "C%d" % i, "track": "Speaker %d" % i,
                        "file": "C%d.mov" % i, "source": "C%d.mov" % i,
                        "wide": False})
    item = []
    for cam in cameras:
        for _n in range(PER_CAMERA):
            item.append(Item(cam["file"]))
    vpm.colour_clips_by_camera(TL(item), cameras)
    return cameras, item


def per_camera(item):
    """Return {file name: the colours its clips carry}."""
    out = {}
    for clip in item:
        out.setdefault(clip.GetName(), set()).add(clip.colour)
    return out


print("1. Every clip gets a colour, one per camera")
for n in (1, 2, 3, 5, 8, 15):
    cameras, item = run(n)
    angles = n + 1
    groups = per_camera(item)
    check("%2d angles: every clip is coloured" % angles,
          all(c.colour for c in item),
          "%d of %d clips coloured"
          % (len([c for c in item if c.colour]), len(item)))
    check("%2d angles: each camera keeps one colour" % angles,
          all(len(v) == 1 for v in groups.values()),
          str({k: v for k, v in groups.items() if len(v) > 1}))
    check("%2d angles: no two cameras share a colour" % angles,
          len(set(c.colour for c in item)) == angles,
          "%d colours for %d angles"
          % (len(set(c.colour for c in item)), angles))
    refused = [c.colour for c in item if c.colour not in REAL_COLOURS]
    check("%2d angles: only names Resolve knows" % angles,
          all(c.colour in REAL_COLOURS for c in item),
          "%d of %d clips carry a name Resolve refuses: %s"
          % (len(refused), len(item), sorted(set(map(str, refused)))))

print("\n2. More angles than colours")
cameras, item = run(20)
groups = per_camera(item)
check("every clip is still coloured", all(c.colour for c in item),
      "%d of %d clips coloured"
      % (len([c for c in item if c.colour]), len(item)))
check("each camera still keeps one colour",
      all(len(v) == 1 for v in groups.values()),
      "%d of %d cameras carry more than one colour: %s"
      % (len([v for v in groups.values() if len(v) > 1]), len(groups),
         {k: v for k, v in groups.items() if len(v) > 1}))
check("all sixteen colours are used",
      len(set(c.colour for c in item)) == len(REAL_COLOURS),
      str(len(set(c.colour for c in item))))

print("\n3. An installation that knows only three names")
REAL_COLOURS = {"Blue", "Green", "Orange"}
cameras, item = run(4)
groups = per_camera(item)
check("every clip is coloured with what is left",
      all(c.colour for c in item),
      "%d of %d clips coloured"
      % (len([c for c in item if c.colour]), len(item)))
refused = [c.colour for c in item if c.colour not in REAL_COLOURS]
check("and only with names it accepts",
      all(c.colour in REAL_COLOURS for c in item),
      "%d of %d clips carry a name Resolve refuses: %s"
      % (len(refused), len(item), sorted(set(map(str, refused)))))
check("each camera still keeps one colour",
      all(len(v) == 1 for v in groups.values()),
      str({k: v for k, v in groups.items() if len(v) > 1}))
check("three colours for five angles, so two repeat",
      len(set(c.colour for c in item)) == 3,
      str(sorted(set(c.colour for c in item))))

print("\n4. Nothing to colour")
REAL_COLOURS = {"Blue"}
raised = ""
try:
    vpm.colour_clips_by_camera(TL([]), [{"camera": "A", "track": "A",
                                         "file": "A.mov", "source": "A.mov",
                                         "wide": False}])
except Exception as e:
    raised = "%s: %s" % (type(e).__name__, e)
check("an empty timeline does not raise", not raised, raised)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
