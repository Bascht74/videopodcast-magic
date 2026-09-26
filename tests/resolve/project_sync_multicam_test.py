# -*- coding: utf-8 -*-
"""A sync-only handover builds the multicam timeline alone, and says so.

Against a stand-in for Resolve: what build_resolve_project makes out of
a handover is read back as timeline names, render jobs and log lines.
The sections: a sync handover with several cameras gets the multicam
timeline, no cut timeline, no render job and no speaker markers, and
the log names the reason; a cut list inside a sync handover changes
nothing, because the flag decides and not the list; a cut handover
without a cut keeps today's way -- multicam alone, the older reason in
the log; a cut handover with a cut still gets both timelines and its
render job; one camera in sync gets the straight timeline, as one
camera always did; the multicam timeline's own log line names the
camera files rather than the speakers when the run only synchronised;
and a track carries the label the window's legend gives the camera --
the speaker, or the wide shot -- while the key the camera is filed
under stays the file's, so two cameras nobody is on stay two tracks.

The limit of the method: nothing here is laid on a real timeline; the
stand-in records the calls, and the real insert is another test's.
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
import contextlib, io, sys, time
began = time.time()
vpm = the_program.load()
vpm.set_language("en")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


class Item(object):
    def __init__(self, name): self.name = name
    def GetName(self): return self.name


class TL(object):
    def __init__(self, name, project):
        self.name, self.p = name, project
        self.v = {}
    def GetName(self): return self.name
    def GetTrackCount(self, kind): return len(self.v) if kind == "video" else 0
    def GetItemListInTrack(self, kind, i): return self.v.get(i, [])


class MP(object):
    def __init__(self, p): self.p = p
    def CreateEmptyTimeline(self, name):
        tl = TL(name, self.p); self.p.tls.append(tl); return tl
    def DeleteTimelines(self, items):
        self.p.tls = [t for t in self.p.tls if t not in items]; return True


class Project(object):
    def __init__(self, name):
        self.name, self.tls, self.mp = name, [], MP(self)
        self.current = None
    def GetName(self): return self.name
    def GetMediaPool(self): return self.mp
    def GetTimelineCount(self): return len(self.tls)
    def GetTimelineByIndex(self, i):
        return self.tls[i - 1] if 1 <= i <= len(self.tls) else None
    def SetCurrentTimeline(self, tl): self.current = tl; return True


class PM(object):
    def __init__(self): self.projects = {}
    def GetProjectListInCurrentFolder(self): return sorted(self.projects)
    def CreateProject(self, n):
        p = Project(n); self.projects[n] = p; return p
    def LoadProject(self, n): return self.projects.get(n)


class R(object):
    def __init__(self, pm): self.pm = pm
    def GetProductName(self): return "DaVinci Resolve Studio"
    def GetVersionString(self): return "21.0.4"
    def GetProjectManager(self): return self.pm


# Everything around the decision is stubbed out; what the stubs are
# asked for is written down, and the decision is read off that.
asked = {"render": [], "markers": []}
vpm.apply_project_settings = lambda p, d: None
vpm.set_loudness_target = lambda p, x: None
vpm.set_remote_grades = lambda p, on=True: None
vpm.import_media = lambda mp, paths: {p: Item(os.path.basename(p))
                                        for p in paths}
vpm.queue_render_job = lambda p, tl, *a, **k: asked["render"].append(
    tl.GetName())
vpm.lead_in_offset = lambda *a, **k: 0
vpm.insert_intro_and_outro = lambda *a, **k: None
vpm.colour_clips_by_camera = lambda *a, **k: None
vpm.create_colour_groups = lambda *a, **k: None
vpm.add_speaker_markers = lambda tl, *a, **k: asked["markers"].append(
    tl.GetName())
vpm.mix_file_from_handover = lambda d: (None, None)


def camera_tl(mp, tl, cameras, clips, d, every_tracks=False):
    for i, cam in enumerate(cameras, 1):
        tl.v[i] = [Item(os.path.basename(cam["file"]))]


# Section 6 runs the real one, so it is kept before the stub goes in.
lay_cameras = vpm.build_camera_timeline
vpm.build_camera_timeline = camera_tl
vpm.build_cut_timeline = lambda mp, tl, *a, **k: tl.v.setdefault(
    1, [Item("cut")])

CAMERAS = [{"camera": "W_C001", "track": "W_C001", "file": "/tmp/W_C001.mov",
            "source": "/tmp/W_C001.mov", "wide": True, "speakers": [],
            "offset": 0.0},
           {"camera": "G_C003", "track": "G_C003", "file": "/tmp/G_C003.mov",
            "source": "/tmp/G_C003.mov", "wide": True, "speakers": [],
            "offset": 0.0}]
CUT = [{"start": 0.0, "end": 10.0, "camera": "W_C001"},
       {"start": 10.0, "end": 20.0, "camera": "G_C003"}]
SPEAKERS = [{"name": "Guest", "sections": [[0.0, 10.0]]}]
SYNC_LINE = vpm.T('\n  Sync only: no cut by speaker was asked for.\n  Only '
                  'the Timeline for the multicam clip is built.').strip()
NO_CUT_LINE = vpm.T('\n  No camera cut in the handover -- without speaker '
                    'statistics there is none.\n  Only the Timeline for the '
                    'multicam clip is built.').strip()
ONE_LINE = vpm.T('\n  Timeline: the camera in one piece, the mix below'
                 ).strip()


# The door to Resolve is nailed shut here, at module level and before
# any build: the stand-in of the current build is what answers.
CURRENT = {}
vpm.connect_to_resolve = lambda: R(CURRENT["pm"])


def build(handover, what):
    """One build against a fresh stand-in: (timeline names, log)."""
    pm = PM()
    CURRENT["pm"] = pm
    asked["render"], asked["markers"] = [], []
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        vpm.build_resolve_project(dict(handover, production=what), "keep",
                                  log="")
    p = pm.projects.get(what)
    return (sorted(t.GetName() for t in (p.tls if p else [])),
            said.getvalue())


print("1. Sync only, several cameras: the multicam timeline and nothing else")
names, said = build({"project_type": "sync", "fps": 30.0,
                     "start_tc": "19:04:27:00", "cut": [],
                     "speakers": [], "cameras": CAMERAS}, "S")
check("a sync handover gets the multicam timeline and no cut timeline",
      names == ["S Multicam"], "timelines %s against ['S Multicam']" % names)
check("and no render job is queued for it", asked["render"] == [],
      "%d render job(s): %s" % (len(asked["render"]), asked["render"]))
check("and the log says why there is no cut", SYNC_LINE in said,
      "the sentence stands at character %d of %d"
      % (said.find(SYNC_LINE), len(said)))

print("\n2. A cut list inside a sync handover changes nothing")
names, said = build({"project_type": "sync", "fps": 30.0,
                     "start_tc": "19:04:27:00", "cut": CUT,
                     "speakers": SPEAKERS, "cameras": CAMERAS}, "T")
check("the flag decides, not the list: still the multicam timeline alone",
      names == ["T Multicam"], "timelines %s against ['T Multicam']" % names)
check("and the speakers of such a handover put no markers on it",
      asked["markers"] == [],
      "%d timeline(s) got markers: %s" % (len(asked["markers"]),
                                          asked["markers"]))

print("\n3. A cut handover without a cut keeps today's way")
names, said = build({"project_type": "cut", "fps": 30.0,
                     "start_tc": "19:04:27:00", "cut": [],
                     "speakers": [], "cameras": CAMERAS}, "C")
check("no cut in a cut handover: the multicam timeline alone",
      names == ["C Multicam"], "timelines %s against ['C Multicam']" % names)
check("and the log gives the older reason, not the sync one",
      NO_CUT_LINE in said and SYNC_LINE not in said,
      "older reason at character %d, sync reason at %d"
      % (said.find(NO_CUT_LINE), said.find(SYNC_LINE)))

print("\n4. A cut handover with a cut still gets both")
names, said = build({"project_type": "cut", "fps": 30.0,
                     "start_tc": "19:04:27:00", "cut": CUT,
                     "speakers": SPEAKERS, "cameras": CAMERAS}, "D")
check("a cut handover with a cut gets the cut timeline and the multicam",
      names == ["D Cut", "D Multicam"],
      "timelines %s against ['D Cut', 'D Multicam']" % names)
check("and its render job", asked["render"] == ["D Cut"],
      "render jobs %s against ['D Cut']" % asked["render"])
# A handover from before the project type has no key at all.
names, said = build({"fps": 30.0, "start_tc": "19:04:27:00", "cut": CUT,
                     "speakers": SPEAKERS, "cameras": CAMERAS}, "E")
check("a handover without the key is read as a cut",
      names == ["E Cut", "E Multicam"],
      "timelines %s against ['E Cut', 'E Multicam']" % names)

print("\n5. One camera in sync: the straight timeline, as one camera "
      "always got")
names, said = build({"project_type": "sync", "fps": 30.0,
                     "start_tc": "19:04:27:00", "cut": [],
                     "speakers": [], "cameras": CAMERAS[:1]}, "F")
check("one camera in sync gets the camera in one piece",
      names == ["F Cut"] and ONE_LINE in said,
      "timelines %s against ['F Cut'], the line at character %d"
      % (names, said.find(ONE_LINE)))

print("\n6. The multicam timeline's log line names the files, not the "
      "speakers")
# The real build_camera_timeline this time, over a timeline that
# answers every call the way Resolve does (the stand-in of
# project_cameras_land, copied: a test cannot be imported without
# running it); only the line at the end is read.


class LaidTL(object):
    """A timeline that remembers what it was told, so it can be read back."""
    def __init__(self):
        self.v = {}; self.a = {}
        self.names = {"video": {}, "audio": {}}
        self.start = []
        self.linked = []
    def SetStartTimecode(self, tc): self.start.append(tc); return True
    def GetTrackCount(self, kind):
        return len(self.v) if kind == "video" else len(self.a)
    def AddTrack(self, kind):
        d = self.v if kind == "video" else self.a
        d.setdefault(len(d) + 1, [])
        return True
    def DeleteTrack(self, kind, i):
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


class LaidMP(object):
    """Without mediaType picture AND audio go to the same track number;
    where audio sits there, or the track was never made, it is refused."""
    def __init__(self, tl):
        self.tl = tl
    def AppendToTimeline(self, items):
        out = []
        for e in items:
            kind = e.get("mediaType"); i = e["trackIndex"]
            name = e["mediaPoolItem"].name
            audio = e["mediaPoolItem"].audio
            room = [i + n for n in range(max(1, audio))]
            picture = 1 <= i <= self.tl.GetTrackCount("video")
            sound = (i >= 1 and room[-1] <= self.tl.GetTrackCount("audio")
                     and not any(self.tl.a.get(t) for t in room))
            fits = (picture if kind == 1 else sound if kind == 2
                    else picture and sound)
            if not fits:
                continue
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


# The files do not exist here, so the count cannot be read out of them.
vpm.audio_track_count = lambda cam: cam["audio"]
FILES = vpm.T('  %s video tracks, named after the camera files:'
              ).split("%s")[1].strip()
PEOPLE = vpm.T('  %s video tracks, named after the speakers:'
               ).split("%s")[1].strip()
for kind, wants, wants_not in (("sync", FILES, PEOPLE),
                               ("cut", PEOPLE, FILES)):
    tl = LaidTL(); tl.AddTrack("video"); tl.AddTrack("audio")
    mp = LaidMP(tl)
    cams = [dict(c, audio=1) for c in CAMERAS]
    clips = {c["file"]: Clip(c["file"], 1) for c in cams}
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        lay_cameras(
            mp, tl, cams, clips,
            {"project_type": kind, "fps": 30.0, "start_tc": "19:04:27:00",
             "in_point": "19:04:27:00", "speakers": [], "cameras": cams})
    said = said.getvalue()
    if kind == "sync":
        check("in sync the tracks are said to be named after the camera "
              "files",
              wants in said and wants_not not in said,
              "files at character %d, speakers at %d"
              % (said.find(wants), said.find(wants_not)))
    else:
        check("in a cut they are said to be named after the speakers",
              wants in said and wants_not not in said,
              "speakers at character %d, files at %d"
              % (said.find(wants), said.find(wants_not)))

print("\n7. The track carries the window's label, the key stays the file's")
# The real layer again, over a cut handover somebody speaks in. What a
# camera is filed under stays the file's stem -- two cameras nobody is on
# would otherwise fall on one key -- and only the name on the track is
# the legend's, read back off the timeline and not off the log.
WIDE = vpm.T('Wide shot')
LONE = dict(CAMERAS[0], audio=1)
OTHER = dict(CAMERAS[1], audio=1)
GUEST = {"camera": "Guest", "track": "Guest", "file": "/tmp/G_C002.mov",
         "source": "/tmp/G_C002.mov", "wide": False, "speakers": ["Guest"],
         "offset": 0.0, "audio": 1}
FILE_NAMES = {1: "W_C001", 2: "G_C003"}


def laid(kind, cams, speakers):
    """The real layer over a fresh timeline: (video names, audio names, tl)."""
    tl = LaidTL(); tl.AddTrack("video"); tl.AddTrack("audio")
    # Resolve reports a clip by its file name, never its path.
    clips = {c["file"]: Clip(os.path.basename(c["file"]), 1) for c in cams}
    with contextlib.redirect_stdout(io.StringIO()):
        lay_cameras(LaidMP(tl), tl, cams, clips,
                    {"project_type": kind, "fps": 30.0,
                     "start_tc": "19:04:27:00", "in_point": "19:04:27:00",
                     "speakers": speakers, "cameras": cams})
    return tl.names["video"], tl.names["audio"], tl


video, audio, tl = laid("cut", [LONE, GUEST], SPEAKERS)
check("a camera nobody is on is labelled the wide shot on its track",
      video.get(1) == WIDE, "V1 is %r against %r" % (video.get(1), WIDE))
check("a camera with a speaker keeps the speaker's name",
      video.get(2) == "Guest", "V2 is %r against 'Guest'" % video.get(2))
check("the audio track under each says the same as its picture",
      audio == {1: WIDE, 2: "Guest"},
      "audio %s against %s" % (audio, {1: WIDE, 2: "Guest"}))
video, audio, tl = laid("cut", [LONE, GUEST, OTHER], SPEAKERS)
TWO = {1: vpm.T('Wide shot %d') % 1, 2: "Guest", 3: vpm.T('Wide shot %d') % 2}
check("two cameras nobody is on stay two tracks, numbered apart",
      tl.GetTrackCount("video") == 3 and video == TWO,
      "%d video tracks named %s against %s"
      % (tl.GetTrackCount("video"), video, TWO))
video, audio, tl = laid("sync", [LONE, OTHER], SPEAKERS)
check("in sync the tracks keep the camera files' names, speakers or not",
      video == FILE_NAMES, "video %s against %s" % (video, FILE_NAMES))
video, audio, tl = laid("cut", [LONE, OTHER], [])
check("a cut nobody was heard in keeps the files' names, like the window",
      video == FILE_NAMES, "video %s against %s" % (video, FILE_NAMES))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
