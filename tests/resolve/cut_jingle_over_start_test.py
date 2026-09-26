# -*- coding: utf-8 -*-
"""Intro and outro: where they sit, and how far the content moves.

A jingle lies over the beginning rather than in front of it, on the
second picture track, its sound carrying under the first words. The
content moves back far enough for the jingle to finish speaking and no
further, or the timeline starts with a hole. Where the first word comes
late enough by itself, nothing moves and the jingle goes into the run-up.
The second tracks it lies on are asked for, as Resolve makes a timeline
with one of each and lays nothing on a track that is not there.
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
import math, sys, time
vpm = the_program.load()
FPS = 30.0
began = time.time()
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


class Item(object):
    """What Resolve hands back for a clip that lies on a track."""
    def __init__(self, entry):
        self.entry = entry

    def GetName(self):
        return self.entry["mediaPoolItem"].GetName()

    def GetDuration(self):
        return (self.entry.get("endFrame", 0)
                - self.entry.get("startFrame", 0))


class TL(object):
    """A timeline as Resolve makes one: one video and one audio track."""
    def __init__(self, mp=None):
        self.mp = mp
        self.tracks = {"video": 1, "audio": 1}

    def GetTrackCount(self, kind):
        return self.tracks[kind]

    def AddTrack(self, kind, *rest):
        self.tracks[kind] += 1
        return True

    def SetStartTimecode(self, tc):
        return True

    def SetTrackName(self, *a):
        return True

    def GetItemListInTrack(self, kind, index):
        want = 1 if kind == "video" else 2
        return [Item(x) for x in (self.mp.item if self.mp else [])
                if x.get("mediaType") == want
                and x.get("trackIndex") == index]


class MP(object):
    """Lays an item only on a track the timeline has, as Resolve does."""
    def __init__(self):
        self.item = []
        self.asked = []
        self.tl = None

    def AppendToTimeline(self, items):
        self.asked += items
        kinds = {1: "video", 2: "audio"}
        laid = [x for x in items if x["trackIndex"]
                <= self.tl.GetTrackCount(kinds[x["mediaType"]])]
        self.item += laid
        return laid


# How many video and audio tracks the last timeline built ended with,
# and every item it asked for, laid or not, in the shape of `where`.
TRACKS = []
ASKED = []


def run(intro_len, word0, outro_len=None, word1=100.0, audio=True,
        audio_until=None, audio_from=None):
    """Build one timeline and report where everything landed.

    Returns (lead-in in seconds, [(track, kind, name, start in seconds)]).
    """
    d = {"fps": FPS, "start_tc": "10:00:00:00", "length_s": 120.0,
         "speakers": [{"name": "A",
                       "sections": [[word0, word0 + 5], [word1 - 5, word1]]}]}
    if intro_len:
        d["intro"] = {"source": "/i.mov", "duration": intro_len,
                      "has_audio": audio, "audio_from": 0.0,
                      "audio_to": audio_until if audio else None}
    if outro_len:
        d["outro"] = {"source": "/o.mov", "duration": outro_len,
                      "has_audio": True,
                      "audio_from": (audio_from if audio_from is not None
                                     else 0.0),
                      "audio_to": outro_len}
    cameras = [{"camera": "C", "track": "C", "file": "C.mov",
                "source": "C.mov", "offset": 0.0, "duration": 200.0,
                "wide": False}]
    clips = {"C.mov": Clip("C.mov"), "/i.mov": Clip("i"),
             "/o.mov": Clip("o"), "mix.wav": Clip("mix")}
    mp = MP()
    tl = TL(mp)
    mp.tl = tl
    fps, origin = vpm.timeline_origin(d)
    lead_in = vpm.lead_in_offset(mp, tl, d, clips, fps, origin)
    vpm.build_cut_timeline(mp, tl,
                           [{"start": 0.0, "end": 120.0, "camera": "C"}],
                           cameras, clips, d, ("mix.wav", "Test"), lead_in)
    vpm.insert_intro_and_outro(mp, tl, d, clips, fps, origin, lead_in)
    TRACKS[:] = [tl.GetTrackCount("video"), tl.GetTrackCount("audio")]
    ASKED[:] = spots(mp.asked, origin)
    return lead_in / fps, spots(mp.item, origin)


def spots(items, origin):
    """Each item as (track, "video" or "audio", clip name, start in s)."""
    return [(x["trackIndex"], {1: "video", 2: "audio"}[x["mediaType"]],
             x["mediaPoolItem"].GetName(), (x["recordFrame"] - origin) / FPS)
            for x in items]


def at(where, track, kind, name):
    """Where the clip starts on that track, in seconds; NaN where it is not.

    Not None: a sum or a comparison with it would end the test in a
    traceback, where NaN turns every judgement on it red and goes on.
    """
    for t, k, n, start in where:
        if t == track and k == kind and n.startswith(name):
            return start
    return float("nan")


print()
print("1. A jingle whose sound runs to 8 s, first word at 3 s")
lead, where = run(10.0, 3.0, audio_until=8.0)
# First: without the tracks nothing below has anywhere to lie.
check("the jingle's second picture and sound tracks are asked for",
      TRACKS == [2, 2],
      "the timeline ends with %r video and audio tracks against [2, 2]"
      % (TRACKS,))
check("the content moves back by five seconds", abs(lead - 5.0) < 0.01,
      "%.2f s" % lead)
check("so the first word falls at 8 s, where the jingle stops",
      abs((lead + 3.0) - 8.0) < 0.01, "%.2f s" % (lead + 3.0))
check("the jingle starts the timeline", at(where, 2, "video", "i") == 0.0,
      str(where))
check("picture and sound of the content start together",
      at(where, 1, "video", "C") == at(where, 1, "audio", "mix") == lead,
      "picture at %s s, sound at %s s, lead-in %.2f s"
      % (at(where, 1, "video", "C"), at(where, 1, "audio", "mix"), lead))

print("\n2. The same jingle, but the first word only comes at 25 s")
lead, where = run(10.0, 25.0, audio_until=8.0)
check("nothing moves -- there is room already", abs(lead) < 0.01,
      "%.2f s" % lead)
check("the jingle sits inside the run-up instead",
      abs(at(where, 2, "video", "i") - 17.0) < 0.01,
      str(at(where, 2, "video", "i")))
# The jingle's sound has to end where the first word begins. Its picture
# may run on past that; the overlap is where the dissolve goes.
check("and its sound stops exactly at the first word",
      abs((at(where, 2, "audio", "i") + 8.0) - 25.0) < 0.01,
      "%.2f s" % (at(where, 2, "audio", "i") + 8.0))

print("\n3. An intro of 8 s and an outro of 12 s")
lead, where = run(8.0, 2.0, 12.0, word1=110.0, audio_until=8.0,
                  audio_from=1.5)
check("the content moves back by six seconds", abs(lead - 6.0) < 0.01,
      "%.2f s" % lead)
check("the intro is at the front", at(where, 2, "video", "i") == 0.0,
      "at %s s, wanted 0.00" % (at(where, 2, "video", "i"),))
check("the outro comes after the last word",
      at(where, 2, "video", "o") > lead + 110.0 - 5.0,
      str(at(where, 2, "video", "o")))
check("its sound and picture start together",
      at(where, 2, "video", "o") == at(where, 2, "audio", "o"),
      "picture at %s s, sound at %s s"
      % (at(where, 2, "video", "o"), at(where, 2, "audio", "o")))
check("and it is inside the timeline",
      at(where, 2, "video", "o") + 12.0 <= lead + 120.0 + 12.0,
      "the outro ends at %.2f s, the timeline at %.2f s"
      % (at(where, 2, "video", "o") + 12.0, lead + 120.0 + 12.0))

print("\n4. A jingle without sound")
lead, where = run(10.0, 3.0, audio=False)
check("the content still moves out of the way", lead > 0, "%.2f s" % lead)
# Asked, not laid: without its sound the jingle gets no second audio
# track, and nothing is laid on a track that is not there.
check("but only the picture is laid in",
      math.isnan(at(ASKED, 2, "audio", "i")), "asked for %s" % (ASKED,))
check("the jingle starts the timeline", at(where, 2, "video", "i") == 0.0,
      "at %s s, wanted 0.00" % (at(where, 2, "video", "i"),))

print("\n5. Neither of the two")
lead, where = run(None, 4.0)
check("nothing moves", abs(lead) < 0.01, "%.2f s" % lead)
check("and nothing lands on the second track",
      not [x for x in where if x[0] == 2], str(where))
check("content picture and sound are still together",
      at(where, 1, "video", "C") == at(where, 1, "audio", "mix") == 0.0,
      "picture at %s s, sound at %s s, wanted both 0.00"
      % (at(where, 1, "video", "C"), at(where, 1, "audio", "mix")))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
