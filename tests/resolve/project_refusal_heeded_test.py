# -*- coding: utf-8 -*-
"""A track Resolve refuses is asked twice, then named, and the rest built.

Against a stand-in whose timelines refuse AddTrack on named calls. In
turn: a camera's picture, spare audio room, a camera's sound, the
intro's picture and sound, a track nothing needs, one granted when asked
again, picture and sound together, the intro's sound beside a kept
multicam timeline, and what the window then says. The code is 1 where
something lacks and 0 where not; the last lines list only what was laid.
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
import contextlib, io, re, sys, time, types
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
# it an endless loop and gives up. The program asks twice and breaks.
FOR_EVER = 20
# A refusal from this call on, never ended.
ALWAYS = 10 ** 6


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

    AddTrack(kind) refuses the calls numbered from `refuse[kind][0]` to
    `refuse[kind][1]`, as Resolve does once its limit is reached, and
    writes down where in the printed text each refusal fell.
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
        first, last = self.p.refuse.get(kind, (0, -1))
        if first <= self.calls[kind] <= last:
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
# Called only after the tracks: a build that stopped at one never
# reaches it.
QUEUED = []
vpm.queue_render_job = lambda *a, **k: QUEUED.append(a[1].GetName())
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


def build(handover, refuse, pm=None):
    """One build against a fresh stand-in, or again against *pm*.

    Returns (return code or the exception, everything printed, the
    refusals as [(kind, call, where in the text)], the timelines).
    """
    said = io.StringIO()
    if pm is not None:
        pm.said = said
        for p in pm.projects.values():
            p.refuse, p.refused, p.said = refuse, [], said
    pm = pm or PM(refuse, said)
    CURRENT["pm"] = pm
    del QUEUED[:]
    try:
        with contextlib.redirect_stdout(said):
            code = vpm.build_resolve_project(dict(handover, production="X"),
                                             "keep", log="")
    except Exception as e:
        code = e
    p = pm.projects.get("X")
    return (code, said.getvalue(), (p.refused if p else []),
            (p.tls if p else []))


def naming(text, words):
    """The lines of text that say "refused" and every one of the words."""
    return [clean(line) for line in text.splitlines()
            if "refused" in line and all(w in line for w in words)]


def clean(line):
    """A printed line without the program's colour marks, for a FAIL line."""
    line = re.sub(re.escape(vpm.MARK) + ".", "", line)
    return "".join(c for c in line if c >= " ").strip()


SYNC = {"project_type": "sync", "fps": 30.0, "start_tc": "19:04:27:00",
        "in_point": "19:04:27:00", "cut": [], "speakers": [],
        "cameras": CAMERAS}

def asked(code, refused):
    """Asked twice and not for ever, however the build ended."""
    return len(refused) == 2 and not isinstance(code, Endless)


def after(said, refused):
    """The lines printed after the last refusal."""
    rest = said[refused[-1][2]:] if refused else ""
    return [clean(line) for line in rest.splitlines() if clean(line)]


def last_two(said):
    """The last two lines printed."""
    return [clean(line) for line in said.splitlines() if clean(line)][-2:]


def sounds(tl):
    """The names of everything on any audio track of a stand-in timeline."""
    return sorted(set(x.GetName() for i in list(tl.a)
                      for x in tl.GetItemListInTrack("audio", i)))


def missing_called(said):
    """The lines that call the project incomplete or name what it lacks."""
    return [clean(line) for line in said.splitlines()
            if "not complete" in line or "lacks" in line]


def on_track(tl, kind, i):
    """The names of what lies on one track of a stand-in timeline."""
    return [x.GetName() for x in tl.GetItemListInTrack(kind, i)]


def ended(code):
    """How the build ended, for a FAIL line."""
    return "ended in %r" % (code,)


def lines(said):
    """Every line printed, cleaned, the empty ones left out."""
    return [clean(line) for line in said.splitlines() if clean(line)]


def angles(said):
    """The rows under "Angles:" in the closing hint, split into words."""
    rows = lines(said)
    at = rows.index("Angles:") + 1 if "Angles:" in rows else len(rows)
    out = []
    for row in rows[at:]:
        if not row.startswith("V"):
            break
        out.append(row.split())
    return out


print("1. A video track refused twice on the multicam timeline")
# The new timeline has one video track; the second camera needs a
# second, and every call for it is refused.
code, said, refused, tls = build(SYNC, {"video": (1, ALWAYS)})
check("a refused video track is asked twice, not for ever",
      asked(code, refused),
      "%d refusals against 2, the build %s" % (len(refused), ended(code)))
# Which track, which timeline, and the camera that lacks its place.
WORDS = ("V2", '"X Multicam"', "G_C003")
first = after(said, refused)[:1]
check("a video track refused twice names the camera it lacks",
      bool(naming("\n".join(first), WORDS)),
      "the line after the refusal, against one saying refused and %r: %r"
      % (WORDS, first))
tl = tls[-1] if tls else None
# Four audio tracks wanted and one there: three asked for. The empty
# ones are cleared away afterwards, so the asking is what is counted.
audio = tl.calls["audio"] if tl else 0
laid = on_track(tl, "video", 1) if tl else []
check("a video track refused twice leaves the rest built",
      not isinstance(code, Exception) and audio == 3
      and laid == ["W_C001.mov"],
      "%d audio tracks asked for against 3, V1 holds %r against "
      "['W_C001.mov'], the build %s" % (audio, laid, ended(code)))
check("a video track refused twice is named again at the end",
      bool(naming("\n".join(last_two(said)), WORDS)),
      "the last two lines, against one saying refused and %r: %r"
      % (WORDS, last_two(said)))
check("a video track refused twice ends the build in 1", code == 1,
      "the build %s against 1" % ended(code))
# What the closing lines say the timeline holds: V1 alone.
COUNTED = clean(vpm.T('  %s video tracks, named after the camera files:')
                % "1")
said_count = [x for x in lines(said) if "video tracks, named" in x]
check("a camera refused its track is not counted as a video track",
      said_count == [COUNTED],
      "%r against [%r]" % (said_count, COUNTED))
check("a camera refused its track is not listed among the angles",
      angles(said) == [["V1", "W_C001"]],
      "%r against [['V1', 'W_C001']]" % angles(said))
heard = sounds(tl) if tl else []
rows = [x for x in lines(said) if x.startswith("A") and "G_C003" in x]
check("a camera refused its track lays no sound without picture",
      heard == ["W_C001.mov"] and not rows,
      "the audio tracks hold %r against ['W_C001.mov'], rows %r against "
      "none" % (heard, rows))

print("\n2. An audio track refused where only the spare room ran short")
# Two cameras, four audio tracks asked for side by side; the timeline has
# one, the first call for a second is granted and every one after
# refused. Two tracks hold both cameras' sound: nothing is lost.
code, said, refused, tls = build(SYNC, {"audio": (2, ALWAYS)})
check("a refused audio track is asked twice, not for ever",
      asked(code, refused),
      "%d refusals against 2, the build %s" % (len(refused), ended(code)))
first = after(said, refused)[:1]
check("an audio track refused twice is named in a line",
      bool(naming("\n".join(first), ("A3",))),
      "the line after the refusal, against one saying refused and A3: %r"
      % first)
tl = tls[-1] if tls else None
laid = [on_track(tl, "video", i) for i in (1, 2)] if tl else []
heard = sounds(tl) if tl else []
check("an audio track refused twice leaves the rest built",
      not isinstance(code, Exception)
      and laid == [["W_C001.mov"], ["G_C003.mov"]]
      and heard == ["G_C003.mov", "W_C001.mov"],
      "V1 and V2 hold %r against [['W_C001.mov'], ['G_C003.mov']], the "
      "audio tracks %r against both, the build %s"
      % (laid, heard, ended(code)))
called = missing_called(said)
check("a spare audio track refused twice is not called missing",
      not called and code == 0,
      "%r against no such line, the build %s" % (called, ended(code)))

print("\n3. An audio track refused that costs a camera its sound")
# Every call for a second audio track refused: the second camera's
# picture finds V2, its sound no track.
code, said, refused, tls = build(SYNC, {"audio": (1, ALWAYS)})
WORDS = ("A2", '"X Multicam"', "G_C003")
check("an audio track refused twice names the camera left silent",
      bool(naming("\n".join(after(said, refused)), WORDS)),
      "the lines after the refusal saying refused, against one with %r: "
      "%r" % (WORDS, [x for x in after(said, refused) if "refused" in x]))
check("an audio track refused twice is named again at the end",
      bool(naming("\n".join(last_two(said)), WORDS)),
      "the last two lines, against one saying refused and %r: %r"
      % (WORDS, last_two(said)))
check("an audio track refused twice ends the build in 1", code == 1,
      "the build %s against 1" % ended(code))

print("\n4. A second video track for the intro refused twice")
# One camera and an intro with sound: the cut timeline needs a second
# video track for its picture and a second audio track for its sound,
# and every call for the video one is refused.
ONE = dict(SYNC, project_type="cut", cameras=CAMERAS[:1], length_s=60.0,
           intro={"source": "/tmp/Intro.mov", "duration": 5.0,
                  "has_audio": True})
code, said, refused, tls = build(ONE, {"video": (1, ALWAYS)})
check("a refused intro track is asked twice, not for ever",
      asked(code, refused),
      "%d refusals against 2, the build %s" % (len(refused), ended(code)))
WORDS = ("V2", '"X Cut"', "picture of Intro")
first = after(said, refused)[:1]
check("an intro track refused twice names the picture it lacks",
      bool(naming("\n".join(first), WORDS)),
      "the line after the refusal, against one saying refused and %r: %r"
      % (WORDS, first))
tl = tls[-1] if tls else None
sound = on_track(tl, "audio", 2) if tl else []
check("an intro track refused twice leaves the rest built",
      not isinstance(code, Exception) and sound == ["Intro.mov"]
      and len(QUEUED) == 1,
      "A2 holds %r against ['Intro.mov'], %d render jobs against 1, the "
      "build %s" % (sound, len(QUEUED), ended(code)))
check("an intro track refused twice is named again at the end",
      bool(naming("\n".join(last_two(said)), WORDS)),
      "the last two lines, against one saying refused and %r: %r"
      % (WORDS, last_two(said)))
check("an intro track refused twice ends the build in 1", code == 1,
      "the build %s against 1" % ended(code))

print("\n5. A second audio track for the intro refused twice")
# The same timeline; this time every call for an audio track is refused,
# and the only one asked for is the intro's.
code, said, refused, tls = build(ONE, {"audio": (1, ALWAYS)})
WORDS = ("A2", '"X Cut"', "sound of Intro")
first = after(said, refused)[:1]
check("an intro sound track refused twice names what it lacks",
      bool(naming("\n".join(first), WORDS)),
      "the line after the refusal, against one saying refused and %r: %r"
      % (WORDS, first))
tl = tls[-1] if tls else None
picture = on_track(tl, "video", 2) if tl else []
check("an intro sound track refused twice leaves the picture",
      not isinstance(code, Exception) and picture == ["Intro.mov"]
      and len(QUEUED) == 1,
      "V2 holds %r against ['Intro.mov'], %d render jobs against 1, the "
      "build %s" % (picture, len(QUEUED), ended(code)))
check("an intro sound refused twice is named again at the end",
      bool(naming("\n".join(last_two(said)), WORDS)),
      "the last two lines, against one saying refused and %r: %r"
      % (WORDS, last_two(said)))
check("an intro sound track refused twice ends the build in 1", code == 1,
      "the build %s against 1" % ended(code))
ON_A2 = clean(vpm.T(', audio on A2'))
claimed = [x for x in lines(said) if ON_A2 in x]
check("an intro sound track refused twice is not said to be on A2",
      not claimed, "%r against no line saying %r" % (claimed, ON_A2))

print("\n6. A second video track nothing would lie on, refused twice")
# One camera and no intro: the second track is asked for all the same.
BARE = dict(ONE)
del BARE["intro"]
code, said, refused, tls = build(BARE, {"video": (1, ALWAYS)})
called = missing_called(said)
check("a second track nothing would lie on is not called missing",
      len(refused) == 2 and not called and code == 0,
      "%d refusals against 2, %r against no such line, the build %s"
      % (len(refused), called, ended(code)))

print("\n7. A video track refused once and granted the second time")
code, said, refused, tls = build(SYNC, {"video": (1, 1)})
tl = tls[-1] if tls else None
second = on_track(tl, "video", 2) if tl else []
check("a track refused once and granted the second time is added",
      len(refused) == 1 and second == ["G_C003.mov"],
      "%d refusals against 1, V2 holds %r against ['G_C003.mov'], the "
      "build %s"
      % (len(refused), second, ended(code)))

print("\n8. A video and an audio track refused together")
# G_C003 finds neither V2 nor A2: its picture is the loss, and its
# sound is not a second one.
code, said, refused, tls = build(SYNC, {"video": (1, ALWAYS),
                                        "audio": (1, ALWAYS)})
twice = [x for x in naming(said, ("G_C003",)) if "sound of" in x]
check("a camera refused its picture is not named as lacking sound",
      len(refused) == 4 and not twice,
      "%d refusals against 4, %r against no such line"
      % (len(refused), twice))

print("\n9. The intro's sound refused beside a multicam timeline kept")
# Built once in full, then again into the same project, where the
# multicam timeline stays as it is and the cut one is built anew.
CUT = dict(SYNC, project_type="cut", length_s=60.0,
           cut=[{"start": 0.0, "end": 60.0, "camera": "W_C001"}],
           intro=ONE["intro"])
code, said, refused, tls = build(CUT, {})
pm = CURRENT["pm"]
code, said, refused, tls = build(CUT, {"audio": (1, ALWAYS)}, pm)
multicams = [t.GetName() for t in tls if "Multicam" in t.GetName()]
check("a kept multicam timeline is not built again beside it",
      multicams == ["X Multicam"],
      "%r against ['X Multicam']" % multicams)
WORDS = ("A2", '"X Cut"', "sound of Intro")
check("a refusal beside a kept multicam is named at the end",
      bool(naming("\n".join(last_two(said)), WORDS)),
      "the last two lines, against one saying refused and %r: %r"
      % (WORDS, last_two(said)))
check("a refusal beside a kept multicam ends the build in 1", code == 1,
      "the build %s against 1" % ended(code))

print("\n10. What the window says after a refusal")
# The window's own run loop, with main standing in for the command
# line's switch, which returns the build's code as it is: that switch
# may not stand in a test (source_resolve_door_shut).
ERRORS = clean(vpm.T('\nFinished with errors.\n'))
DONE = clean(vpm.run_done_text(False).strip().splitlines()[0])


def window_says(handover, refuse):
    """What the window writes after one build, and the build's code."""
    got = {}

    def main():
        got["code"], said, _r, _t = build(handover, refuse)
        sys.stdout.write(said)
        return got["code"]
    vpm.main = main
    written = []
    state = {"dry_run": False, "results": [], "running": True}
    with contextlib.redirect_stdout(io.StringIO()):
        vpm.window().gui_run_loop(
            ["vpm"], state, written.append, lambda *a: None,
            types.SimpleNamespace(run_step=None), lambda *a: None, [])
    return got.get("code"), lines("".join(written))[-3:]


code, last = window_says(SYNC, {"video": (1, ALWAYS)})
check("a camera refused its track leaves the window saying errors",
      ERRORS in last and DONE not in last,
      "the last lines %r against %r, the build %s"
      % (last, ERRORS, ended(code)))
code, last = window_says(SYNC, {"audio": (2, ALWAYS)})
check("spare room refused leaves the window saying done",
      DONE in last and ERRORS not in last,
      "the last lines %r against %r, the build %s"
      % (last, DONE, ended(code)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
