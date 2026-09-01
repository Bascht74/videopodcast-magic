# -*- coding: utf-8 -*-
"""Every shot of the cut counts its frames in the rate of its own camera.

Resolve reads startFrame and endFrame as frames of the file, so a shot
from a 24 camera on a 30 Timeline has to be counted at 24. First
frames_of_the_file on its own, which may fall short of a slot but never
run past it; then a cut list through build_cut_timeline over cameras of
three rates, each shot looked up in its own file and beginning where the
one before it really stopped; last a camera the handover gives no rate.
The stand-in media pool takes whatever it is handed, so this says what
the program built, not what Resolve would accept.
"""
import importlib.util
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
began = time.time()
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.set_language("en")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


class Clip(object):
    def __init__(self, name):
        self.name = name

    def GetName(self):
        return self.name


class TL(object):
    """What Resolve hands back for a timeline. Takes whatever it is given."""

    def __init__(self, mp):
        self.mp = mp

    def SetStartTimecode(self, tc):
        return True

    def SetTrackName(self, *a):
        return True

    def GetItemListInTrack(self, kind, index):
        want = 1 if kind == "video" else 2
        return [Item(x) for x in self.mp.item
                if x.get("mediaType") == want and x.get("trackIndex") == index]


class Item(object):
    def __init__(self, entry):
        self.entry = entry

    def GetName(self):
        return self.entry["mediaPoolItem"].GetName()

    def GetDuration(self):
        return self.entry.get("endFrame", 0) - self.entry.get("startFrame", 0)


class MP(object):
    def __init__(self):
        self.item = []

    def AppendToTimeline(self, items):
        self.item += items
        return items


print("\n1. How many frames of a file fill a piece of the Timeline")
# Written out, not computed: 219 frames of a 30 Timeline are 7.3 s, and
# 7.3 s of a 24 file are 175.2 frames, of which 175 whole ones fit.
check("a 30 Timeline slot is filled from a 24 file to the whole frame",
      vpm.frames_of_the_file(219, 30.0, 24.0) == 175,
      "%d against 175 for 219 frames of a 30 Timeline"
      % vpm.frames_of_the_file(219, 30.0, 24.0))
check("and from a 25 file to its own whole frame",
      vpm.frames_of_the_file(195, 30.0, 25.0) == 163,
      "%d against 163 for 195 frames of a 30 Timeline"
      % vpm.frames_of_the_file(195, 30.0, 25.0))
check("a file at the Timeline's own rate gives the slot back unchanged",
      vpm.frames_of_the_file(195, 30.0, 30.0) == 195,
      "%d against 195 for 195 frames of a 30 Timeline"
      % vpm.frames_of_the_file(195, 30.0, 30.0))
check("a file faster than the Timeline is counted in its own frames too",
      vpm.frames_of_the_file(100, 24.0, 30.0) == 126,
      "%d against 126 for 100 frames of a 24 Timeline"
      % vpm.frames_of_the_file(100, 24.0, 30.0))
# The piece may fall short of its slot, never run past it: a shot that
# overruns pushes the next one, and the pushes add up over an hour.
# Measured on Resolve 21: n frames of a file become the whole number
# below n times the two rates, so that is how the slot is worked out here.
RATES = (24.0, 25.0, 29.97, 30.0, 50.0, 60.0)
SLOTS = 6 * 899


def on_the_timeline(slot, own):
    return int(vpm.frames_of_the_file(slot, 30.0, own) * 30.0 / own)


over = [(slot, own) for own in RATES for slot in range(1, 900)
        if on_the_timeline(slot, own) > slot]
check("no piece ever asks for more of its file than its slot holds",
      not over, "%d of %d slots run past their own: %s"
      % (len(over), SLOTS, over[:3] or "none"))
short = [(slot, own) for own in RATES for slot in range(1, 900)
         if slot - on_the_timeline(slot, own) >= 30.0 / own]
check("and none falls short of it by a whole frame of its own file",
      not short, "%d of %d slots short by a frame of their file or more: %s"
      % (len(short), SLOTS, short[:3] or "none"))

print("\n2. The same cut list over cameras of three rates")
FPS = 30.0
cameras = [
    {"camera": "Hosts", "track": "Hosts", "file": "H.mov", "source": "H.mov",
     "offset": -12.0, "duration": 600.0, "fps": 24.0},
    {"camera": "Guest", "track": "Guest", "file": "G.mov", "source": "G.mov",
     "offset": -8.0, "duration": 600.0, "fps": 25.0},
    {"camera": "Wide", "track": "Wide", "file": "W.mov", "source": "W.mov",
     "offset": -4.0, "duration": 600.0, "fps": 30.0},
]
clips = {"H.mov": Clip("H.mov"), "G.mov": Clip("G.mov"),
         "W.mov": Clip("W.mov")}
cut = [{"start": 0.0, "end": 7.3, "camera": "Hosts"},
       {"start": 7.3, "end": 13.8, "camera": "Guest"},
       {"start": 13.8, "end": 20.3, "camera": "Wide"},
       {"start": 20.3, "end": 26.8, "camera": "Hosts"}]
d = {"fps": FPS, "fps_measured": FPS, "start_tc": "10:00:00:00",
     "in_point": "10:00:00:00", "cameras": cameras}
mp = MP()
vpm.build_cut_timeline(mp, TL(mp), cut, cameras, clips, d, None, 0)
video = sorted((p for p in mp.item if p.get("mediaType") == 1),
               key=lambda p: p["recordFrame"])
check("every shot of the cut list reaches the Timeline",
      len(video) == 4, "%d shots against the 4 the cut list names"
      % len(video))
# Written out. The Hosts camera started 12 s before the In point, so its
# first shot begins at 12 s of the file -- 288 frames at 24, not 360 at 30.
check("the first shot starts at frame 288 of its own 24 file",
      video and video[0]["startFrame"] == 288,
      "%s against 288, 12 s into a 24 file"
      % (video[0]["startFrame"] if video else None))
check("the 25 shot starts at frame 382 of its own file",
      len(video) > 1 and video[1]["startFrame"] == 382,
      "%s against 382, 15.3 s into a 25 file"
      % (video[1]["startFrame"] if len(video) > 1 else None))
check("the 30 shot starts at frame 534 of its own file",
      len(video) > 2 and video[2]["startFrame"] == 534,
      "%s against 534, 17.8 s into a 30 file"
      % (video[2]["startFrame"] if len(video) > 2 else None))
check("a 7.3 s shot asks for 175 frames of the 24 file, not 219",
      video and video[0]["endFrame"] - video[0]["startFrame"] == 175,
      "%s frames against 175"
      % (video[0]["endFrame"] - video[0]["startFrame"] if video else None))
# 195 frames of the Timeline, and the one the 24 shot before it could
# not fill: 196 frames of 30 are 163.33 of a 25 file, of which 164 cover
# the place.
check("a 6.5 s shot asks for 164 frames of the 25 file, not 195",
      len(video) > 1
      and video[1]["endFrame"] - video[1]["startFrame"] == 164,
      "%s frames against 164"
      % (video[1]["endFrame"] - video[1]["startFrame"]
         if len(video) > 1 else None))
check("the shot from the 30 camera keeps the Timeline's own 195",
      len(video) > 2
      and video[2]["endFrame"] - video[2]["startFrame"] == 195,
      "%s frames against 195"
      % (video[2]["endFrame"] - video[2]["startFrame"]
         if len(video) > 2 else None))
# The place on the timeline is the cut list's own and owes nothing to the
# camera: 7.3 s at 30 is frame 219, counted from the In point.
place = [p["recordFrame"] - vpm.timeline_origin(d)[1] for p in video]
check("a shot begins where the one before it really stopped",
      place == [0, 218, 414, 609],
      "%s against [0, 218, 414, 609]" % place)
OWN = {"Hosts": 24.0, "Guest": 25.0, "Wide": 30.0}
fills = [vpm.timeline_frames_of(p["endFrame"] - p["startFrame"], FPS,
                                OWN[cut[i]["camera"]])
         for i, p in enumerate(video)]
holes = [place[i + 1] - (place[i] + fills[i]) for i in range(len(video) - 1)]
check("no Timeline frame is left without a picture between two shots",
      holes == [0, 0, 0],
      "%s frames open at the three joins, none of them allowed" % holes)
check("and no shot runs into the one that follows it",
      not [x for x in holes if x < 0],
      "%s frames of overlap at the three joins" % holes)

print("\n3. A camera the handover gives no rate")
older = [dict(cam) for cam in cameras]
for cam in older:
    cam.pop("fps")
d_old = dict(d, cameras=older)
mp = MP()
vpm.build_cut_timeline(mp, TL(mp), cut, older, clips, d_old, None, 0)
video = sorted((p for p in mp.item if p.get("mediaType") == 1),
               key=lambda p: p["recordFrame"])
check("a handover from an older version falls back to the Timeline's rate",
      video and video[0]["startFrame"] == 360,
      "%s against 360, 12 s read at the Timeline's 30"
      % (video[0]["startFrame"] if video else None))
check("and the shot is then as long as the slot, in Timeline frames",
      video and video[0]["endFrame"] - video[0]["startFrame"] == 219,
      "%s frames against 219"
      % (video[0]["endFrame"] - video[0]["startFrame"] if video else None))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
