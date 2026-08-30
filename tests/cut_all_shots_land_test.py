"""Checks the cut timeline: lengths fit, no gaps, nothing drops out."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys

spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

FPS = 30.0
class Clip(object):
    def __init__(self, name): self.name = name
    def GetName(self): return self.name
class Item(object):
    """What Resolve hands back for a clip that lies on a track."""
    def __init__(self, entry): self.entry = entry
    def GetName(self): return self.entry["mediaPoolItem"].GetName()
    def GetDuration(self):
        return (self.entry.get("endFrame", 0)
                - self.entry.get("startFrame", 0))
class TL(object):
    def __init__(self, mp=None): self.mp = mp
    def SetStartTimecode(self, tc): return True
    def SetTrackName(self, *a): return True
    def GetItemListInTrack(self, kind, index):
        want = 1 if kind == "video" else 2
        return [Item(x) for x in (self.mp.item if self.mp else [])
                if x.get("mediaType") == want
                and x.get("trackIndex") == index]
class MP(object):
    def __init__(self): self.item = []
    def AppendToTimeline(self, items): self.item += items; return items

cameras = [
    {"camera": "Wide", "track": "Wide", "file": "W.mov", "offset": -534.2,
     "duration": 4313.1, "source": "W.mov"},
    {"camera": "Guest", "track": "Guest", "file": "G.mov", "offset": -331.7,
     "duration": 4104.2, "source": "G.mov"},
    {"camera": "Hosts", "track": "Hosts", "file": "H.mov", "offset": -516.9,
     "duration": 4312.0, "source": "H.mov"},
]
clips = {"W.mov": Clip("W.mov"), "G.mov": Clip("G.mov"),
         "H.mov": Clip("H.mov"), "mix.wav": Clip("mix.wav")}

# A cut like the real run: 145 shots over 3759.7 s
cut, t = [], 0.0
i = 0
while t < 3759.7:
    length = min(3759.7 - t, [11.0, 1.8, 25.3, 7.4][i % 4])
    cut.append({"start": t, "end": t + length,
                    "camera": ["Guest", "Wide", "Hosts", "Guest"][i % 4]})
    t += length; i += 1
print("Cut: %d shots, %.1f s" % (len(cut), t))

d = {"fps": FPS, "start_tc": "19:04:27:00", "in_point": "19:04:27:00"}
mp = MP()
vpm.build_cut_timeline(mp, TL(mp), cut, cameras, clips, d,
                             ("mix.wav", "Result"))

video = [p for p in mp.item if p.get("mediaType") == 1]
print("\nInserted: %d of %d" % (len(video), len(cut)))
gaps, overlaps, wrong = 0, 0, 0
video.sort(key=lambda p: p["recordFrame"])
for i, p in enumerate(video):
    length = p["endFrame"] - p["startFrame"]
    want = (vpm.seconds_to_frames(cut[i]["end"], FPS)
            - vpm.seconds_to_frames(cut[i]["start"], FPS))
    if length != want:
        wrong += 1
        if wrong < 4:
            print("  wrong length at %d: %d instead of %d"
                  % (i, length, want))
    if i:
        v = video[i - 1]
        end = v["recordFrame"] + (v["endFrame"] - v["startFrame"])
        if p["recordFrame"] > end: gaps += 1
        if p["recordFrame"] < end: overlaps += 1
print("  wrong lengths: %d, gaps: %d, overlaps: %d"
      % (wrong, gaps, overlaps))
assert len(video) == len(cut) and not wrong and not gaps and not overlaps
print("\nOK: every shot present, right length, no gaps.")
