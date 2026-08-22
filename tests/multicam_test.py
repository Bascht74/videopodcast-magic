"""Checks: the second camera gets in, even when picture+audio fail as one.

A smoke test on purpose. A multicam clip is something only Resolve can
build and only Resolve can judge; what runs here is the call that asks
for it. So this catches a crash, not a clip that came out wrong.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.audio_track_count = lambda cam: cam["audio"]

class Item(object):
    def __init__(self, name): self.name = name
    def GetName(self): return self.name
class TL(object):
    def __init__(self): self.v = {}; self.a = {}
    def SetStartTimecode(self, tc): return True
    def GetTrackCount(self, kind):
        return len(self.v) if kind == "video" else len(self.a)
    def AddTrack(self, kind):
        (self.v if kind == "video" else self.a).setdefault(
            len(self.v if kind == "video" else self.a) + 1, []); return True
    def GetItemListInTrack(self, kind, i):
        return (self.v if kind == "video" else self.a).get(i, [])
    def SetTrackName(self, *a): return True
    def GetTrackName(self, kind, i): return ""
    def SetClipsLinked(self, *a): return True
    def DeleteClips(self, items):
        for d in (self.v, self.a):
            for i in list(d): d[i] = [p for p in d[i] if p not in items]
        return True
class MP(object):
    """Resolve as it behaves: without mediaType picture AND audio go to
    the same track number -- if audio sits there, it is refused."""
    def __init__(self, tl): self.tl = tl
    def AppendToTimeline(self, items):
        out = []
        for e in items:
            kind = e.get("mediaType"); i = e["trackIndex"]
            name = e["mediaPoolItem"].name
            audio = e["mediaPoolItem"].audio
            if kind == 1:
                self.tl.v.setdefault(i, []).append(Item(name)); out.append(1)
            elif kind == 2:
                if any(self.tl.a.get(i + n) for n in range(audio)): continue
                for n in range(audio):
                    self.tl.a.setdefault(i + n, []).append(Item(name))
                out.append(1)
            else:
                if any(self.tl.a.get(i + n) for n in range(audio)): continue
                self.tl.v.setdefault(i, []).append(Item(name))
                for n in range(audio):
                    self.tl.a.setdefault(i + n, []).append(Item(name))
                out.append(1)
        return out
class Clip(object):
    def __init__(self, name, audio): self.name, self.audio = name, audio
    def GetClipProperty(self):
        return {"FPS": "30.0", "Audio Ch": str(audio_count)}

cameras = [{"camera": "Wide", "track": "Wide", "file": "W.mov",
            "source": "W.mov",
            "offset": -534.2, "duration": 4313.1, "audio": 2},
           {"camera": "Guest", "track": "Guest", "file": "G.mov",
            "source": "G.mov",
            "offset": -331.7, "duration": 4104.2, "audio": 3},
           {"camera": "Hosts", "track": "Hosts", "file": "H.mov",
            "source": "H.mov",
            "offset": -516.9, "duration": 4312.0, "audio": 5}]
audio_count = 3
clips = {cam["file"]: Clip(cam["file"], cam["audio"]) for cam in cameras}
tl = TL(); tl.AddTrack("video"); tl.AddTrack("audio")
d = {"fps": 30.0, "start_tc": "19:04:27:00", "in_point": "19:04:27:00",
     "speakers": [], "cameras": cameras}
vpm.build_camera_timeline(MP(tl), tl, cameras, clips, d)
print("\nVideo tracks:",
      {i: [p.GetName() for p in v] for i, v in tl.v.items() if v})
