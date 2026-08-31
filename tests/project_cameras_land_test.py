# -*- coding: utf-8 -*-
"""Every camera reaches the timeline on picture and sound tracks of its own.

What runs here is build_camera_timeline, which lays the cameras side by
side: one video track each, one audio track each, named after the speaker
and linked to its picture. No multicam clip is built -- that is something
only Resolve can make out of this timeline afterwards.

The media pool below answers the way Resolve does: without mediaType
picture and audio go to the same track number, and where the audio does
not fit the whole insert is refused without a word. So the second and the
third camera arrive only if the program notices the silent refusal and
inserts picture and audio separately.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys, time
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
# The files do not exist here, so the count cannot be read out of them.
vpm.audio_track_count = lambda cam: cam["audio"]

began = time.time()
done = 0
error = []
def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append("%s [%s]" % (name, extra or "no numbers"))


class Item(object):
    def __init__(self, name): self.name = name
    def GetName(self): return self.name


class TL(object):
    """A timeline that remembers what it was told, so it can be read back."""
    def __init__(self):
        self.v = {}; self.a = {}
        self.names = {"video": {}, "audio": {}}
        self.start = []
        self.linked = []
        self.audio_peak = 0
    def SetStartTimecode(self, tc): self.start.append(tc); return True
    def GetTrackCount(self, kind):
        return len(self.v) if kind == "video" else len(self.a)
    def AddTrack(self, kind):
        d = self.v if kind == "video" else self.a
        d.setdefault(len(d) + 1, [])
        self.audio_peak = max(self.audio_peak, len(self.a))
        return True
    def DeleteTrack(self, kind, i):
        # Resolve renumbers what lies above a deleted track.
        d = self.v if kind == "video" else self.a
        names = self.names[kind]
        n = len(d)
        if i < 1 or i > n:
            return False
        for j in range(i, n):
            d[j] = d[j + 1]
            names[j] = names.get(j + 1, "")
        del d[n]
        names.pop(n, None)
        return True
    def GetItemListInTrack(self, kind, i):
        return (self.v if kind == "video" else self.a).get(i, [])
    def SetTrackName(self, kind, i, name):
        self.names[kind][i] = name; return True
    def GetTrackName(self, kind, i): return self.names[kind].get(i, "")
    def SetClipsLinked(self, items, state):
        self.linked.append((tuple(p.GetName() for p in items), bool(state)))
        return True
    def DeleteClips(self, items):
        for d in (self.v, self.a):
            for i in list(d): d[i] = [p for p in d[i] if p not in items]
        return True


class MP(object):
    """Resolve as it behaves: without mediaType picture AND audio go to
    the same track number -- if audio sits there, it is refused. A track
    that was never made is refused too, and just as silently."""
    def __init__(self, tl):
        self.tl = tl; self.asked = []; self.refused = []
    def AppendToTimeline(self, items):
        out = []
        for e in items:
            kind = e.get("mediaType"); i = e["trackIndex"]
            name = e["mediaPoolItem"].name
            audio = e["mediaPoolItem"].audio
            self.asked.append((name, kind, i))
            room = [i + n for n in range(max(1, audio))]
            picture = 1 <= i <= self.tl.GetTrackCount("video")
            sound = (i >= 1 and room[-1] <= self.tl.GetTrackCount("audio")
                     and not any(self.tl.a.get(t) for t in room))
            if kind == 1:
                fits = picture
            elif kind == 2:
                fits = sound
            else:
                fits = picture and sound
            if not fits:
                self.refused.append((name, kind, i)); continue
            if kind != 2:
                self.tl.v[i].append(Item(name))
            if kind != 1:
                for t in room:
                    self.tl.a[t].append(Item(name))
            out.append(1)
        return out


class Clip(object):
    def __init__(self, name, audio): self.name, self.audio = name, audio
    def GetClipProperty(self):
        return {"FPS": "30.0", "Audio Ch": str(self.audio)}


FPS = 30.0
START = "19:04:27:00"
cameras = [{"camera": "Wide", "track": "Wide", "file": "W.mov",
            "source": "W.mov",
            "offset": -534.2, "duration": 4313.1, "audio": 2},
           {"camera": "Guest", "track": "Guest", "file": "G.mov",
            "source": "G.mov",
            "offset": -331.7, "duration": 4104.2, "audio": 3},
           {"camera": "Hosts", "track": "Hosts", "file": "H.mov",
            "source": "H.mov",
            "offset": -516.9, "duration": 4312.0, "audio": 5}]
clips = {cam["file"]: Clip(cam["file"], cam["audio"]) for cam in cameras}
tl = TL(); tl.AddTrack("video"); tl.AddTrack("audio")
mp = MP(tl)
d = {"fps": FPS, "start_tc": START, "in_point": START,
     "speakers": [], "cameras": cameras}
vpm.build_camera_timeline(mp, tl, cameras, clips, d)

video = {i: [p.GetName() for p in v] for i, v in sorted(tl.v.items())}
audio = {i: [p.GetName() for p in a] for i, a in sorted(tl.a.items())}
print("\nVideo tracks:", video)
print("Audio tracks:", audio)

print("\n1. Room was made before anything was inserted")
check("one video track per camera",
      tl.GetTrackCount("video") == len(cameras),
      "%d tracks for %d cameras" % (tl.GetTrackCount("video"), len(cameras)))
wanted = sum(cam["audio"] for cam in cameras) + len(cameras)
check("audio tracks for every camera side by side",
      tl.audio_peak >= wanted,
      "%d were made, %d needed (%s)"
      % (tl.audio_peak, wanted,
         " + ".join("%s %d" % (c["track"], c["audio"]) for c in cameras)))

print("\n2. The timeline begins at the earliest camera")
early = min(cam["offset"] for cam in cameras)
moved = int(round(-early * FPS))
check("the start was set at all", bool(tl.start), str(tl.start))
begin = tl.start[-1] if tl.start else ""
back = (vpm.timecode_to_frames(START, FPS)
        - vpm.timecode_to_frames(begin, FPS))
check("moved back by the earliest camera's head start",
      back == moved,
      "%s -> %s is %d frames, %.1f s needs %d"
      % (START, begin, back, -early, moved))

print("\n3. Every camera is on the timeline, on a track of its own")
for i, cam in enumerate(cameras, 1):
    check("%s on V%d" % (cam["track"], i),
          video.get(i) == [cam["file"]],
          "V%d holds %s, expected [%r]"
          % (i, video.get(i), cam["file"]))
check("no camera is missing from the picture",
      sorted(sum(video.values(), [])) == sorted(c["file"] for c in cameras),
      "on the timeline: %s" % sorted(sum(video.values(), [])))
check("the video tracks carry the speakers' names",
      tl.names["video"] == dict(enumerate((c["track"] for c in cameras), 1)),
      "%s, expected %s"
      % (tl.names["video"],
         dict(enumerate((c["track"] for c in cameras), 1))))

print("\n4. The camera whose picture and audio failed as one still got in")
combined = [(n, i) for n, kind, i in mp.refused if kind is None]
check("Resolve refused the joint insert for Guest",
      ("G.mov", 2) in combined, "refused jointly: %s" % combined)
after = [(n, kind) for n, kind, i in mp.asked if n == "G.mov"]
check("picture and audio were asked for separately",
      ("G.mov", 1) in after and ("G.mov", 2) in after,
      "asked for G.mov: %s" % after)
check("and Guest is on the timeline all the same",
      video.get(2) == ["G.mov"] and "G.mov" in sum(audio.values(), []),
      "V2 %s, audio %s" % (video.get(2), audio))
check("the same for the third camera",
      ("H.mov", 3) in combined and video.get(3) == ["H.mov"]
      and "H.mov" in sum(audio.values(), []),
      "refused jointly: %s, V3 %s" % (combined, video.get(3)))

print("\n5. One audio track per camera is left, and it is the right one")
check("as many audio tracks as cameras",
      tl.GetTrackCount("audio") == len(cameras),
      "%d tracks: %s" % (tl.GetTrackCount("audio"), audio))
check("no empty audio track was left standing",
      all(audio.get(i) for i in range(1, tl.GetTrackCount("audio") + 1)),
      str(audio))
for i, cam in enumerate(cameras, 1):
    check("%s audio on A%d, and only once" % (cam["track"], i),
          audio.get(i) == [cam["file"]],
          "A%d holds %s, expected [%r]" % (i, audio.get(i), cam["file"]))
check("the audio tracks carry the speakers' names",
      tl.names["audio"] == dict(enumerate((c["track"] for c in cameras), 1)),
      "%s, expected %s"
      % (tl.names["audio"],
         dict(enumerate((c["track"] for c in cameras), 1))))

print("\n6. Picture and audio hang together again")
again = [pair for pair, state in tl.linked if state]
for cam in cameras:
    check("%s linked to its picture again" % cam["track"],
          any(sorted(pair) == [cam["file"], cam["file"]] and len(pair) == 2
              for pair in again),
          "linked again: %s" % (again,))
loose = [pair for pair, state in tl.linked if not state]
check("unlinked first, or deleting takes the picture along",
      len(loose) >= len(cameras),
      "%d unlink calls for %d cameras" % (len(loose), len(cameras)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
