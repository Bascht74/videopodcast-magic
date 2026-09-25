"""Checks the cut timeline: lengths fit, no gaps, nothing drops out.

A cut of a few hundred shots over three cameras goes to
build_cut_timeline against a stand-in media pool, and what came back is
read off the video track. In order: how many shots landed of how many
were asked for, then each shot's length against the cut, then the two
sides of every join -- no gap, and no overlap either. The stand-in takes
whatever it is handed, so this says what the program built, not what
Resolve would accept. Then a camera that stopped early: another takes
its shot at its length, the window counts such shots, and a shot no
camera covers is named.
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
import contextlib, io, sys, time

began = time.time()
vpm = the_program.load()

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


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

# A cut like the real run: shots of 11.0, 1.8, 25.3 and 7.4 s in turn,
# over 3759.7 s, the last one cut short where the material ends.
cut, t = [], 0.0
i = 0
while t < 3759.7:
    length = min(3759.7 - t, [11.0, 1.8, 25.3, 7.4][i % 4])
    cut.append({"start": t, "end": t + length,
                    "camera": ["Guest", "Wide", "Hosts", "Guest"][i % 4]})
    t += length; i += 1
print("Cut: %d shots, %.1f s" % (len(cut), t))
# A precondition of the material, not a judgement on the program: with
# an empty or a tiny cut list every check below would pass on an almost
# empty timeline and say nothing.
assert len(cut) > 100, "the cut list came out at %d shots" % len(cut)

d = {"fps": FPS, "start_tc": "19:04:27:00", "in_point": "19:04:27:00"}
mp = MP()
vpm.build_cut_timeline(mp, TL(mp), cut, cameras, clips, d,
                             ("mix.wav", "Result"))

video = [p for p in mp.item if p.get("mediaType") == 1]
print("\nInserted: %d of %d" % (len(video), len(cut)))
gaps, overlaps, wrong = 0, 0, 0
first_wrong = first_gap = first_overlap = ""
video.sort(key=lambda p: p["recordFrame"])
for i, p in enumerate(video):
    length = p["endFrame"] - p["startFrame"]
    if i < len(cut):
        # The expectation by its own route. Asking the program for the
        # frame count would compute it as wrongly as the timeline did,
        # and the comparison would hold whatever the rounding does.
        want = (int(round(cut[i]["end"] * FPS))
                - int(round(cut[i]["start"] * FPS)))
        if length != want:
            wrong += 1
            if not first_wrong:
                first_wrong = ("first at shot %d: %d frames instead of %d"
                               % (i, length, want))
    if i:
        v = video[i - 1]
        end = v["recordFrame"] + (v["endFrame"] - v["startFrame"])
        if p["recordFrame"] > end:
            gaps += 1
            if not first_gap:
                first_gap = ("first before shot %d: %d frames"
                             % (i, p["recordFrame"] - end))
        if p["recordFrame"] < end:
            overlaps += 1
            if not first_overlap:
                first_overlap = ("first before shot %d: %d frames"
                                 % (i, end - p["recordFrame"]))

joins = max(0, len(video) - 1)
paired = min(len(video), len(cut))
check("every shot of the cut lands on the timeline",
      len(video) == len(cut),
      "%d shots on the track against %d in the cut"
      % (len(video), len(cut)))
check("every shot lands at the length the cut asks for",
      wrong == 0,
      "%d of %d shots off; %s" % (wrong, paired, first_wrong or "none"))
check("no gap opens between two shots",
      gaps == 0,
      "%d gaps in %d joins; %s" % (gaps, joins, first_gap or "none"))
check("no shot overlaps the one before it",
      overlaps == 0,
      "%d overlaps in %d joins; %s"
      % (overlaps, joins, first_overlap or "none"))

print("\nA camera that stopped early")
# Wide runs 100 s, Guest only 50: the Guest shot at 60 s has to go to
# Wide, and the one at 100 s lies behind every camera.
short = [{"camera": "Wide", "track": "Wide", "file": "W.mov", "offset": 0.0,
          "duration": 100.0, "source": "W.mov"},
         {"camera": "Guest", "track": "Guest", "file": "G.mov",
          "offset": 0.0, "duration": 50.0, "source": "G.mov"}]
asked = [{"start": 0.0, "end": 20.0, "camera": "Guest"},
         {"start": 20.0, "end": 40.0, "camera": "Wide"},
         {"start": 40.0, "end": 49.0, "camera": "Guest"},
         {"start": 60.0, "end": 80.0, "camera": "Guest"},
         {"start": 100.0, "end": 110.0, "camera": "Guest"}]
mp = MP()
said = io.StringIO()
with contextlib.redirect_stdout(said):
    vpm.build_cut_timeline(mp, TL(mp), asked, short, clips,
                           {"fps": FPS, "start_tc": "00:00:00:00"})
said = said.getvalue()
at = {p["recordFrame"]: p for p in mp.item if p.get("mediaType") == 1}
taken = at.get(1800)
check("a shot whose camera is not running is taken by another",
      taken is not None and taken["mediaPoolItem"].GetName() == "W.mov"
      and taken["startFrame"] == 1800,
      "at frame 1800: %s from frame %s, wanted W.mov from 1800"
      % (taken["mediaPoolItem"].GetName() if taken else "nothing",
         taken["startFrame"] if taken else "-"))
check("the replacement keeps the length the cut asks for",
      taken is not None and taken["endFrame"] - taken["startFrame"] == 600,
      "%s frames against 600" % (taken["endFrame"] - taken["startFrame"]
                                 if taken else "no shot"))
once = (vpm.T('    %sx the intended camera was not running -- a '
              'different one is there.') % vpm.number_text(1, 0)).strip()
check("and the window says so, with the count", once in said,
      "%r %s among %d lines" % (once, "said" if once in said else "not said",
                                len(said.splitlines())))
left = (vpm.T('    Left without picture: %s')
        % (vpm.T('%s (%s to %s)') % ("Guest", "0:01:40.000",
                                      "0:01:50.000"))).strip()
check("a shot no camera covers is named, not dropped silently",
      left in said and 3000 not in at,
      "%r %s; %d shots placed at frames %s"
      % (left, "said" if left in said else "not said", len(at), sorted(at)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
