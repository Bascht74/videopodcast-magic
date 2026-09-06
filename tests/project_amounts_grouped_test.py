# -*- coding: utf-8 -*-
"""Resolve's report writes amounts as the language does, addresses not.

Three sections in the order they come: a count out of the audio
cleanup, which takes the thousands mark; the track number printed
beside it, which keeps its plain digits; and a measured frame rate,
which takes the decimal comma. All three are held as whole numbers, so
that a place gained is caught as well as a place lost.

The timeline and the project are stand-ins, so what is judged is what
the program prints, not what Resolve would make of it. No wording is
held against anything -- only the shape of the number, which is why
these checks stand whether a catalogue carries the sentence or not.
"""
import contextlib
import io
import re
import sys
import time

import the_program

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


class Item(object):
    def __init__(self, name):
        self.name = name

    def GetName(self):
        return self.name


class TL(object):
    """Audio tracks only, and Resolve's renumbering after a deletion."""

    def __init__(self, tracks):
        self.a = dict(tracks)
        self.names = {}

    def GetTrackCount(self, kind):
        return len(self.a) if kind == "audio" else 0

    def GetItemListInTrack(self, kind, i):
        return self.a.get(i, [])

    def GetTrackName(self, kind, i):
        return self.names.get(i, "")

    def SetTrackName(self, kind, i, name):
        self.names[i] = name
        return True

    def SetClipsLinked(self, items, state):
        return True

    def DeleteClips(self, items):
        for i in list(self.a):
            self.a[i] = [p for p in self.a[i] if p not in items]
        return True

    def DeleteTrack(self, kind, i):
        n = len(self.a)
        if i < 1 or i > n:
            return False
        for j in range(i, n):
            self.a[j] = self.a[j + 1]
            self.names[j] = self.names.get(j + 1, "")
        del self.a[n]
        self.names.pop(n, None)
        return True


class P(object):
    """A project that keeps every setting and hands it straight back."""

    def __init__(self):
        self.settings = {}

    def SetSetting(self, api_key, value):
        self.settings[api_key] = value
        return True

    def GetSetting(self, api_key):
        return self.settings.get(api_key, "")


def holding(text, *pieces):
    """The first line of text carrying one of pieces, for the FAIL line."""
    for line in text.splitlines():
        if any(p in line for p in pieces):
            return line.strip()
    return ""


def spoken(work):
    """Run work with the printing caught, and hand back what it said."""
    caught = io.StringIO()
    with contextlib.redirect_stdout(caught):
        work()
    said = caught.getvalue()
    for line in said.splitlines():
        print("      > %s" % line.rstrip())
    return said


# The whole run is German: that is the language whose thousands mark and
# whose decimal mark differ from the source's, so both directions show.
vpm.set_language("de")

# One camera, its audio on a track high enough that the track number and
# the count of tracks removed below it are both four digits long. The
# camera carries two audio clips, so one of them is the surplus that
# gets deleted and the track stays.
HOME = 1234
EMPTIED = HOME - 1
tracks = {i: [] for i in range(1, HOME + 1)}
tracks[HOME] = [Item("G.mov"), Item("G.mov")]
tl = TL(tracks)
cameras = [{"track": "Guest", "file": "G.mov", "source": "G.mov"}]

# Every one of the three wanted numbers is a piece of a longer one --
# "1.233" of "1.233,0", "A1234" of "A12340", "29,97" of "29,970" -- so
# asking whether it stands somewhere in the report catches a place that
# went away and not one that came. What is asked instead is what stands
# beside it: a digit, a comma or a dot on either side means the program
# printed a different number.
WHOLE_EMPTIED = re.compile(r"(?<![\d.,])1\.233(?![\d.,])")
WHOLE_HOME = re.compile(r"(?<![\d.,])A1234(?![\d.,])")

print("1. A count takes the thousands mark of the language")
report = spoken(lambda: vpm.trim_audio_tracks(
    tl, cameras, {"Guest": [Item("G.mov")]}))
said = holding(report, "%d" % EMPTIED, "1.233")
check("the emptied audio tracks are counted 1.233 whole, in the German form",
      bool(WHOLE_EMPTIED.search(report)) and "1233" not in report,
      "%r -- wanted %r with no digit or mark beside it, and %r nowhere"
      % (said, "1.233", "%d" % EMPTIED))

print("\n2. A track number keeps its plain digits")
said = holding(report, "A%d" % HOME, "A1.234")
check("the audio track the camera was kept on is A1234 whole, ungrouped",
      bool(WHOLE_HOME.search(report)) and "A1.234" not in report,
      "%r -- wanted %r with no digit or mark beside it, and %r nowhere"
      % (said, "A%d" % HOME, "A1.234"))

print("\n3. A measured frame rate takes the decimal comma")
# The wanted number is written out here rather than worked out the way
# the program works it out -- an expectation that takes the program's
# own road agrees with it whatever the road does. That holds for the
# two above as well.
WHOLE_RATE = re.compile(r"(?<![\d.,])29,97(?![\d.,])")
d = {"fps": 30.0, "fps_measured": 29.97002997, "width": 1920, "height": 1080}
rates = spoken(lambda: vpm.apply_project_settings(P(), d))
said = holding(rates, "29,97", "29.97")
check("the measured rate is 29,97 whole, in the German form",
      bool(WHOLE_RATE.search(rates)) and "29.97" not in rates,
      "%r -- wanted %r with no digit or mark beside it, and %r nowhere"
      % (said, "29,97", "29.97"))

vpm.set_language("en")

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
