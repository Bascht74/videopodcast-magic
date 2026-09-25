# -*- coding: utf-8 -*-
"""A run on mixed rates hands Resolve what its material says, and it builds.

A real run over the mixedcase fixture -- two rates, 10 bit beside 8,
one recorder in two blocks, no speaker on a camera -- with neither
auphonic.com nor Resolve. Its handover against the fixture's numbers:
shots, their sum, the Timeline's start and rate, each camera's rate.
Then build_camera_timeline over it, on a stand-in that keeps what it
is given: that it ran through, where it starts, every camera at its
own clock. The limit: the stand-in is not Resolve.
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
import glob
import json
import shutil
import subprocess
import tempfile
import threading
import time
import traceback
import the_program
from fixture_root import fixture

SCRIPT = the_program.SCRIPT
vpm = the_program.load()
vpm.set_language("en")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stop():
    """Nothing further can be asked, so count what there is and go."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


# ------------------------------------------------ the fixture's own numbers
# Out of the table in fixtures.sh, as values: the camera, its rate, and
# the clock it starts on. The 29.97 clock is non-drop, thirty labels a
# second, so 10:00:05:15 is 5.5 s after the wide shot's 10:00:00:00.
WIDE, PRES, GUEST = ("WideCam_01011000_C001", "PresentersCam_01011000_C002",
                     "GuestCam_01011000_C003")
RATE = {WIDE: 25.0, PRES: 25.0, GUEST: 29.97}
# Every camera ends on second 60 of the programme and the last one rolls
# at 5.5, so the stretch all three saw is 54.5 s long.
SEEN_BY_ALL = 60.0 - 5.5
# The turns inside that stretch (fixtures.sh): the guest's first is cut
# to its last 0.5 s, too short for a shot of its own; the eight after it
# are 4 s and longer. One shot per turn, since one camera serves all.
SHOTS = 8
# The Timeline begins where the last camera rolls, on its own clock.
START_TC, START_S = "10:00:05:15", 10 * 3600 + 5.5
# The camera Timeline begins at the first camera, and each camera sits
# at the frame its own clock names, counted at the Timeline's thirty
# labels a second: 10 h is 1080000, 3 s more 90, 5 s 15 frames 165.
CAMERA_START = "10:00:00:00"
FRAME_OF = {WIDE: 1080000, PRES: 1080090, GUEST: 1080165}

MEDIA = fixture("mixedcase")
SOUND = sorted(glob.glob(os.path.join(MEDIA, "*.wav")))
PICTURES = sorted(glob.glob(os.path.join(MEDIA, "*.mov")))
if len(SOUND) != 3 or len(PICTURES) != 3:
    print("SKIPPED: no mixedcase fixture under %s (%d recordings, %d "
          "cameras, 3 and 3 wanted) -- run tests/fixtures.sh"
          % (MEDIA, len(SOUND), len(PICTURES)))
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    sys.exit(0)

# ------------------------------------------------------------- the run
# Nothing printed for this long and the run is stuck rather than slow:
# it writes a progress bar while it works.
STILL = 120.0
OUT = tempfile.mkdtemp(prefix="vpm_mixedcase_")
NO_RESOLVE = os.path.join(OUT, "no-resolve-here")
ARGV = [sys.executable, SCRIPT, "--multitrack", "--without-auphonic",
        "--no-speech-recognition", "--out", OUT] + SOUND + PICTURES
# No --resolve, and the scripting interface pointed at a folder that is
# not there: the owner's Resolve may be open on the machine this runs on.
kid = subprocess.Popen(ARGV, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       env=dict(os.environ, RESOLVE_SCRIPT_API=NO_RESOLVE,
                                RESOLVE_SCRIPT_LIB=os.path.join(
                                    NO_RESOLVE, "fusionscript.so")))
pieces = []


def read():
    """Keep what the child prints, so it never blocks on a full pipe."""
    for piece in iter(lambda: kid.stdout.read1(65536), b""):
        pieces.append(piece)


reader = threading.Thread(target=read)
reader.daemon = True
reader.start()
last, seen, stuck = time.time(), 0, False
while kid.poll() is None:
    time.sleep(0.25)
    if len(pieces) != seen:
        seen, last = len(pieces), time.time()
    if time.time() - last > STILL:
        stuck = True
        kid.kill()
        break
kid.wait()
reader.join(10)
said = b"".join(pieces).decode("utf-8", "replace")
# The output folder named as <out>, so a red line carries no machine's path.
tail = [line.strip() for line in said.replace(OUT, "<out>").splitlines()
        if line.strip()][-3:]
HANDOVER = os.path.join(OUT, "mixedcase_resolve.json")

print("1. The run over the owner's kind of material")
check("the run came back with 0 and wrote its handover",
      not stuck and kid.returncode == 0 and os.path.exists(HANDOVER),
      "return code %s%s, handover %s -- the log ends: %s"
      % (kid.returncode, " after standing still %.0f s" % STILL
         if stuck else "", "there" if os.path.exists(HANDOVER)
         else "missing", " / ".join(tail)[-240:]))
if not os.path.exists(HANDOVER):
    stop()
d = json.load(open(HANDOVER, encoding="utf-8"))
print("    %d shots, %d cameras, speakers on them: %s"
      % (len(d.get("cut") or []), len(d.get("cameras") or []),
         [c.get("speakers") for c in d.get("cameras") or []]))

print("\n2. The handover against the fixture's numbers")
cut = d.get("cut") or []
check("the handover holds one shot per turn the cameras all saw",
      len(cut) == SHOTS, "%d shots, %d wanted: %s"
      % (len(cut), SHOTS, [(e.get("start"), e.get("end")) for e in cut]))
total = sum(float(e["end"]) - float(e["start"]) for e in cut)
check("the shots add up to the stretch all three cameras saw",
      abs(total - SEEN_BY_ALL) < 0.5 / 29.97,
      "%.4f s against %.4f s" % (total, SEEN_BY_ALL))
check("the Timeline starts on the clock of the last camera to roll",
      d.get("start_tc") == START_TC
      and abs(float(d.get("start_s") or 0) - START_S) < 1e-6,
      "start_tc %r, start_s %r; wanted %r and %r"
      % (d.get("start_tc"), d.get("start_s"), START_TC, START_S))
check("the Timeline runs at the higher of the two rates",
      abs(float(d.get("fps") or 0) - 29.97) < 1e-3,
      "%r, wanted 29.97" % d.get("fps"))
rates = dict((c.get("camera"), c.get("fps")) for c in d.get("cameras") or [])
check("each camera keeps its own rate in the handover",
      sorted(rates) == sorted(RATE)
      and all(abs(float(rates[k] or 0) - RATE[k]) < 1e-3 for k in RATE),
      "%s, wanted %s" % (rates, RATE))


# ------------------------------------------- the camera Timeline, no Resolve
class Item(object):
    """One thing lying on a track, with the frame it was laid at."""

    def __init__(self, name, frame):
        self.name, self.frame = name, frame

    def GetName(self):
        return self.name


class Clip(object):
    """A media pool clip: its file name, and the audio it brings along."""

    def __init__(self, path):
        self.name = os.path.basename(path)
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type",
             "-of", "csv=p=0", path], stdout=subprocess.PIPE)
        self.channels = probe.stdout.decode().split().count("audio")

    def GetClipProperty(self):
        return {"Audio Ch": str(self.channels)}


class Timeline(object):
    """Keeps what it is told, and refuses a track that was never made."""

    def __init__(self):
        # A new Resolve Timeline brings one video and one audio track.
        self.tracks = {"video": [[]], "audio": [[]]}
        self.names = {"video": {}, "audio": {}}
        self.starts = []

    def GetName(self):
        return "mixedcase Multicam"

    def GetTrackCount(self, kind):
        return len(self.tracks[kind])

    def AddTrack(self, kind):
        self.tracks[kind].append([])
        return True

    def DeleteTrack(self, kind, i):
        # Resolve renumbers what lies above a deleted track.
        if not 1 <= i <= len(self.tracks[kind]):
            return False
        del self.tracks[kind][i - 1]
        names = self.names[kind]
        self.names[kind] = dict((j - (j > i), n) for j, n in names.items()
                                if j != i)
        return True

    def GetItemListInTrack(self, kind, i):
        if not 1 <= i <= len(self.tracks[kind]):
            return []
        return list(self.tracks[kind][i - 1])

    def SetTrackName(self, kind, i, name):
        if not 1 <= i <= len(self.tracks[kind]):
            return False
        self.names[kind][i] = name
        return True

    def GetTrackName(self, kind, i):
        return self.names[kind].get(i, "")

    def SetStartTimecode(self, tc):
        self.starts.append(tc)
        return True

    def GetStartTimecode(self):
        return self.starts[-1] if self.starts else "01:00:00:00"

    def SetClipsLinked(self, items, state):
        return True

    def DeleteClips(self, items):
        for kind in self.tracks:
            self.tracks[kind] = [[p for p in t if p not in items]
                                 for t in self.tracks[kind]]
        return True


class Pool(object):
    """Resolve's insert: picture and sound on one track number unless told.

    Where a track is missing or its sound would land on taken tracks,
    the whole entry is refused without a word, as Resolve does.
    """

    def __init__(self, tl):
        self.tl, self.given = tl, []

    def AppendToTimeline(self, entries):
        out = []
        for e in entries:
            self.given.append(dict(e))
            clip, i, kind = e["mediaPoolItem"], e["trackIndex"], \
                e.get("mediaType")
            room = range(i, i + max(1, clip.channels))
            picture = 1 <= i <= self.tl.GetTrackCount("video")
            sound = (i >= 1 and room[-1] <= self.tl.GetTrackCount("audio")
                     and not any(self.tl.GetItemListInTrack("audio", t)
                                 for t in room))
            if not {1: picture, 2: sound}.get(kind, picture and sound):
                continue
            if kind != 2:
                self.tl.tracks["video"][i - 1].append(
                    Item(clip.name, e["recordFrame"]))
            if kind != 1:
                for t in room:
                    self.tl.tracks["audio"][t - 1].append(
                        Item(clip.name, e["recordFrame"]))
            out.append(Item(clip.name, e["recordFrame"]))
        return out


print("\n3. The camera Timeline out of this handover")
cameras = vpm.cameras_in_track_order(d.get("cameras") or [])
clips = dict((c["file"], Clip(c["file"])) for c in cameras if c.get("file"))
tl = Timeline()
pool = Pool(tl)
d["_refused"] = []
try:
    vpm.build_camera_timeline(pool, tl, cameras, clips, d)
    crashed = ""
except Exception as e:
    where = traceback.extract_tb(sys.exc_info()[2])[-1]
    crashed = "%s: %s, in %s line %d" % (type(e).__name__, e, where.name,
                                         where.lineno)
check("the camera Timeline was built from the run's handover",
      not crashed, crashed or "")
print("    refused: %s" % (d.get("_refused") or "nothing"))
check("the camera Timeline starts on the clock of the first camera",
      bool(tl.starts) and tl.starts[-1] == CAMERA_START,
      "start set to %s, wanted %s last" % (tl.starts, CAMERA_START))
lying = {}
for track in tl.tracks["video"]:
    for item in track:
        lying.setdefault(item.name, []).append(item.frame)


def frame_of(camera):
    """The frames the camera's picture was laid at, found by its file."""
    for cam in cameras:
        if cam.get("camera") == camera:
            return lying.get(os.path.basename(cam.get("file") or ""))
    return None


check("the wide camera sits on the camera Timeline at its own clock",
      frame_of(WIDE) == [FRAME_OF[WIDE]],
      "%s, wanted [%d] -- all: %s" % (frame_of(WIDE), FRAME_OF[WIDE], lying))
check("and so does the presenters' camera, in 10 bit",
      frame_of(PRES) == [FRAME_OF[PRES]],
      "%s, wanted [%d] -- all: %s" % (frame_of(PRES), FRAME_OF[PRES], lying))
check("and so does the guest's camera, at 29.97",
      frame_of(GUEST) == [FRAME_OF[GUEST]],
      "%s, wanted [%d] -- all: %s"
      % (frame_of(GUEST), FRAME_OF[GUEST], lying))

shutil.rmtree(OUT, ignore_errors=True)
stop()
