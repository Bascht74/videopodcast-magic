# -*- coding: utf-8 -*-
"""A track Resolve refuses is asked for once, and a refused video one named.

Against a stand-in for Resolve whose timeline refuses AddTrack from a
named call on, as Resolve does at its limit; build_resolve_project runs
for real down to the tracks. The sections: a refused video track and a
refused audio track on the multicam timeline, a refused second video
track for an intro. In each, asked once and not for ever; for the two
video tracks, named in a line after the refusal (the kind and "refuse",
"could not" or "cannot").

Not judged: whether a refused audio track is named, or whether a refusal
stops the build. Today the audio one is passed over without a word and
the build returns 0 after each of the three -- a finding for the owner,
not a contract, and a check stating either way would pin it.

The limit: the stand-in answers one call at a time; where Resolve's own
track limit lies is not measured here.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import contextlib, io, re, sys, time
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


# How often a refused kind may be asked again before the stand-in calls
# it an endless loop and gives up. The program asks once and breaks.
FOR_EVER = 20
# What makes a line a refusal, whatever else it says.
REFUSAL = ("refuse", "could not", "cannot")


class Item(object):
    def __init__(self, name): self.name = name
    def GetName(self): return self.name


class Clip(object):
    def __init__(self, name, audio=1): self.name, self.audio = name, audio
    def GetName(self): return self.name
    def GetClipProperty(self):
        return {"FPS": "30.0", "Audio Ch": str(self.audio)}


class Endless(Exception):
    """The program kept asking for a track that was refused."""


class TL(object):
    """A timeline as Resolve makes one: one video and one audio track.

    AddTrack(kind) refuses from the call numbered in `refuse` on, as
    Resolve does once its limit is reached, and writes down where in the
    printed text each refusal fell.
    """
    def __init__(self, name, project):
        self.name, self.p = name, project
        self.v = {1: []}; self.a = {1: []}
        self.names = {"video": {}, "audio": {}}
        self.calls = {"video": 0, "audio": 0}
    def GetName(self): return self.name
    def SetStartTimecode(self, tc): return True
    def GetStartFrame(self): return 0
    def GetTrackCount(self, kind):
        return len(self.v) if kind == "video" else len(self.a)
    def AddTrack(self, kind, *rest):
        self.calls[kind] += 1
        first = self.p.refuse.get(kind)
        if first is not None and self.calls[kind] >= first:
            self.p.refused.append((kind, self.calls[kind],
                                   self.p.said.tell()))
            if len(self.p.refused) > FOR_EVER:
                raise Endless("%s asked %d times after the refusal"
                              % (kind, len(self.p.refused)))
            return False
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
    def SetClipsLinked(self, items, state): return True
    def DeleteClips(self, items):
        for d in (self.v, self.a):
            for i in list(d): d[i] = [x for x in d[i] if x not in items]
        return True


class MP(object):
    """Picture and audio of one insert land on the same track number, and
    a track that was never made is refused, as Resolve does."""
    def __init__(self, p): self.p = p
    def CreateEmptyTimeline(self, name):
        tl = TL(name, self.p); self.p.tls.append(tl); return tl
    def AppendToTimeline(self, items):
        tl, out = self.p.tls[-1], []
        for e in items:
            kind, i = e.get("mediaType"), e.get("trackIndex", 1)
            clip = e["mediaPoolItem"]
            picture = 1 <= i <= tl.GetTrackCount("video")
            sound = 1 <= i <= tl.GetTrackCount("audio")
            fits = (picture if kind == 1 else sound if kind == 2
                    else picture and sound)
            if not fits:
                continue
            if kind != 2:
                tl.v[i].append(Item(clip.name))
            if kind != 1:
                tl.a[i].append(Item(clip.name))
            out.append(Item(clip.name))
        return out


class Project(object):
    def __init__(self, name, refuse, said):
        self.name, self.tls, self.mp = name, [], MP(self)
        self.refuse, self.refused, self.said = refuse, [], said
    def GetName(self): return self.name
    def GetMediaPool(self): return self.mp
    def GetTimelineCount(self): return len(self.tls)
    def GetTimelineByIndex(self, i):
        return self.tls[i - 1] if 1 <= i <= len(self.tls) else None
    def SetCurrentTimeline(self, tl): return True


class PM(object):
    def __init__(self, refuse, said):
        self.projects, self.refuse, self.said = {}, refuse, said
    def GetProjectListInCurrentFolder(self): return sorted(self.projects)
    def CreateProject(self, n):
        p = Project(n, self.refuse, self.said); self.projects[n] = p
        return p
    def LoadProject(self, n): return self.projects.get(n)


class R(object):
    def __init__(self, pm): self.pm = pm
    def GetProductName(self): return "DaVinci Resolve Studio"
    def GetVersionString(self): return "21.0.4"
    def GetProjectManager(self): return self.pm


# Everything around the tracks is stubbed out; the layer that asks for
# them -- build_camera_timeline, insert_intro_and_outro -- is real.
vpm.apply_project_settings = lambda p, d: None
vpm.set_loudness_target = lambda p, x: None
vpm.set_remote_grades = lambda p, on=True: None
vpm.import_media = lambda mp, paths: {p: Clip(os.path.basename(p))
                                        for p in paths}
vpm.queue_render_job = lambda *a, **k: None
vpm.lead_in_offset = lambda *a, **k: 0
vpm.colour_clips_by_camera = lambda *a, **k: None
vpm.create_colour_groups = lambda *a, **k: None
vpm.add_speaker_markers = lambda *a, **k: None
vpm.mix_file_from_handover = lambda d: (None, None)
vpm.build_cut_timeline = lambda *a, **k: None
# The files do not exist here, so the count cannot be read out of them.
vpm.audio_track_count = lambda cam: 1

# The door to Resolve is nailed shut here, at module level and before
# any build: the stand-in of the current build is what answers.
CURRENT = {}
vpm.connect_to_resolve = lambda: R(CURRENT["pm"])

CAMERAS = [{"camera": "W_C001", "track": "W_C001", "file": "/tmp/W_C001.mov",
            "source": "/tmp/W_C001.mov", "wide": True, "speakers": [],
            "offset": 0.0},
           {"camera": "G_C003", "track": "G_C003", "file": "/tmp/G_C003.mov",
            "source": "/tmp/G_C003.mov", "wide": True, "speakers": [],
            "offset": 0.0}]


def build(handover, refuse):
    """One build against a fresh stand-in.

    Returns (return code or the exception, everything printed, the
    refusals as [(kind, call, where in the text)]).
    """
    said = io.StringIO()
    pm = PM(refuse, said)
    CURRENT["pm"] = pm
    try:
        with contextlib.redirect_stdout(said):
            code = vpm.build_resolve_project(dict(handover, production="X"),
                                             "keep", log="")
    except Exception as e:
        code = e
    p = pm.projects.get("X")
    return code, said.getvalue(), (p.refused if p else [])


def naming(text, kind):
    """The lines of text that name a refused track of this kind."""
    return [clean(line) for line in text.splitlines()
            if kind in line.lower()
            and any(w in line.lower() for w in REFUSAL)]


def clean(line):
    """A printed line without the program's colour marks, for a FAIL line."""
    line = re.sub(re.escape(vpm.MARK) + ".", "", line)
    return "".join(c for c in line if c >= " ").strip()


SYNC = {"project_type": "sync", "fps": 30.0, "start_tc": "19:04:27:00",
        "in_point": "19:04:27:00", "cut": [], "speakers": [],
        "cameras": CAMERAS}

def asked(code, refused):
    """Asked once and not for ever, however the build ended."""
    return len(refused) == 1 and not isinstance(code, Endless)


def heard(code, said, refused, kind):
    """The lines naming the refusal: printed after it, or raised with it."""
    after = said[refused[0][2]:] if refused else ""
    if isinstance(code, Exception) and not isinstance(code, Endless):
        after += "\n" + str(code)
    return naming(after, kind)


print("1. A refused video track on the multicam timeline")
# The new timeline has one video track; the second camera needs a
# second, and the first call for it is refused.
code, said, refused = build(SYNC, {"video": 1})
check("a refused video track is asked once, not for ever",
      asked(code, refused),
      "%d refusals against 1, the build ended in %r"
      % (len(refused), code))
lines = heard(code, said, refused, "video")
check("a refused video track is named in a line",
      bool(lines), "%d lines after the refusal name it against at least 1:"
      " %r" % (len(lines), lines[:1]))

print("\n2. A refused audio track on the multicam timeline")
# Two cameras want four audio tracks side by side; the timeline has one,
# the second call is refused.
code, said, refused = build(SYNC, {"audio": 2})
check("a refused audio track is asked once, not for ever",
      asked(code, refused),
      "%d refusals against 1, the build ended in %r"
      % (len(refused), code))

print("\n3. A refused second video track for the intro")
# One camera and an intro: the cut timeline needs a second video track
# for the intro to lie on, and the first call for it is refused.
ONE = dict(SYNC, project_type="cut", cameras=CAMERAS[:1], length_s=60.0,
           intro={"source": "/tmp/Intro.mov", "duration": 5.0,
                  "has_audio": False})
code, said, refused = build(ONE, {"video": 1})
check("a refused intro track is asked once, not for ever",
      asked(code, refused),
      "%d refusals against 1, the build ended in %r"
      % (len(refused), code))
lines = heard(code, said, refused, "video")
check("a refused intro track is named in a line",
      bool(lines), "%d lines after the refusal name it against at least 1:"
      " %r" % (len(lines), lines[:1]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
