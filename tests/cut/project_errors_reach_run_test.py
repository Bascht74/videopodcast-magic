# -*- coding: utf-8 -*-
"""A --resolve run whose Resolve build refused a track ends in 1, not 0.

Two whole Sync only runs of the interview fixture's cameras and one
recording, started through main as the command line starts one, with
the Resolve build asked for: once with a video track Resolve refuses
every time -- first that the build reached it, then the run's code --
and once with nothing refused. Resolve is a stand-in whose timelines
refuse AddTrack as project_refusal_heeded's do; the run and the build
are the real ones. The limit: --resolve itself is not typed, because a
test may not carry a switch that connects (source_resolve_door_shut);
the parser's default for it is set instead, which is all the switch does.
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
import contextlib, glob, io, re, shutil, tempfile, time
from fixture_root import fixture
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


def stop():
    """Nothing further can be asked, so count what there is and go."""
    shutil.rmtree(WORK, ignore_errors=True)
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


# How often a refused track may be asked for before the stand-in calls
# it an endless loop and gives up. The program asks twice and breaks.
FOR_EVER = 20
ALWAYS = 10 ** 6


class Endless(Exception):
    """The program kept asking for a track that was refused."""


class Item(object):
    def __init__(self, name): self.name = name
    def GetName(self): return self.name


class Clip(object):
    def __init__(self, name): self.name = name
    def GetName(self): return self.name
    def GetClipProperty(self):
        return {"FPS": "30.0", "Audio Ch": "1"}


class TL(object):
    """A timeline as Resolve makes one: one video and one audio track.

    AddTrack(kind) refuses the calls numbered from `refuse[kind][0]` to
    `refuse[kind][1]`, as Resolve does once its limit is reached.
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
            self.p.refused += 1
            if self.p.refused > FOR_EVER:
                raise Endless("%s asked %d times after the refusal"
                              % (kind, self.p.refused))
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
    """Picture and sound of one insert land on the same track number, and
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
            if not (picture if kind == 1 else sound if kind == 2
                    else picture and sound):
                continue
            if kind != 2:
                tl.v[i].append(Item(clip.name))
            if kind != 1:
                tl.a[i].append(Item(clip.name))
            out.append(Item(clip.name))
        return out


class Project(object):
    def __init__(self, name, refuse):
        self.name, self.tls, self.mp = name, [], MP(self)
        self.refuse, self.refused = refuse, 0
    def GetName(self): return self.name
    def GetMediaPool(self): return self.mp
    def GetTimelineCount(self): return len(self.tls)
    def GetTimelineByIndex(self, i):
        return self.tls[i - 1] if 1 <= i <= len(self.tls) else None
    def SetCurrentTimeline(self, tl): return True


class PM(object):
    def __init__(self, refuse): self.projects, self.refuse = {}, refuse
    def GetProjectListInCurrentFolder(self): return sorted(self.projects)
    def CreateProject(self, n):
        p = Project(n, self.refuse); self.projects[n] = p
        return p
    def LoadProject(self, n): return self.projects.get(n)


class R(object):
    def __init__(self, pm): self.pm = pm
    def GetProductName(self): return "DaVinci Resolve Studio"
    def GetVersionString(self): return "21.0.4"
    def GetProjectManager(self): return self.pm


# Everything around the tracks is stubbed out; the run, the build and
# the layer that asks for the tracks are real.
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
# The stand-in's clips say one channel; the count follows them.
vpm.audio_track_count = lambda cam: 1

# The door to Resolve is nailed shut here, at module level and before
# any build: the stand-in of the current build is what answers.
CURRENT = {}
vpm.connect_to_resolve = lambda: R(CURRENT["pm"])

# What --resolve does and nothing more: the parsed run asks for the build.
_parser = vpm.build_argument_parser


def asking_for_the_build():
    ap = _parser()
    ap.set_defaults(resolve=True)
    return ap


vpm.build_argument_parser = asking_for_the_build

# The material is copied, not read in place: a run leaves its project
# memory beside what it was given, and the fixture is shared.
MEDIA = fixture("interview")
WORK = tempfile.mkdtemp(prefix="vpm_handedon_")
RECORDING = sorted(glob.glob(os.path.join(MEDIA, "Guest_*.wav")))[:1]
CAMERAS = sorted(glob.glob(os.path.join(MEDIA, "*.mov")))
check("the fixture holds one recording and the cameras of a whole job",
      len(RECORDING) == 1 and len(CAMERAS) >= 2,
      "%d recording and %d cameras under %s -- 'cd tests && bash "
      "fixtures.sh' builds them" % (len(RECORDING), len(CAMERAS), MEDIA))
if len(RECORDING) != 1 or len(CAMERAS) < 2:
    stop()
# A folder of a fixed name: the run names the project after it, and a
# FAIL line then reads the same on every machine.
GIVEN = []
os.makedirs(os.path.join(WORK, "Interview"))
for f in RECORDING + CAMERAS:
    GIVEN.append(os.path.join(WORK, "Interview", os.path.basename(f)))
    shutil.copy(f, GIVEN[-1])


def run(refuse, n):
    """One whole run: its code, what the build refused, what it printed."""
    CURRENT["pm"] = PM(refuse)
    out = os.path.join(WORK, "out%d" % n)
    said = io.StringIO()
    kept = sys.argv
    sys.argv = [SCRIPT, "--project-type", "sync", "--without-auphonic",
                "--out", out] + GIVEN
    try:
        with contextlib.redirect_stdout(said):
            code = vpm.main()
    except BaseException as e:
        code = e
    finally:
        sys.argv = kept
    # The run names the project itself; one run makes one.
    made = list(CURRENT["pm"].projects.values())
    return code, sum(p.refused for p in made), said.getvalue()


# The build names its transcript last, and a path says nothing about
# how it ended: the line before it is the one that does.
WRITTEN = vpm.T('  Transcript: %s').split("%s")[0].strip()


def last_line(said):
    """The run's last word, without the colour marks, for a FAIL line.

    The folder of this run is written as <work>: a path that changes
    with every run says nothing a reader could compare.
    """
    rows = [re.sub(re.escape(vpm.MARK) + ".", "", x).strip()
            .replace(WORK, "<work>")
            for x in said.splitlines() if x.strip()]
    rows = [x for x in rows if not x.startswith(WRITTEN)]
    return rows[-1][:160] if rows else ""


print("1. A video track Resolve refuses every time")
code, refused, said = run({"video": (1, ALWAYS)}, 1)
# The precondition: the build really ran and was refused, or the code
# below says nothing about a refusal.
check("the build reached Resolve and was refused a track twice",
      refused == 2,
      "%d refusals against 2, the run ended in %r, last line %r"
      % (refused, code, last_line(said)))
check("a run whose build was refused a track twice ends in 1",
      code == 1,
      "the run ended in %r against 1, last line %r"
      % (code, last_line(said)))

print("\n2. Nothing refused")
code, refused, said = run({}, 2)
check("a run whose build refused nothing ends in 0",
      code == 0 and refused == 0,
      "the run ended in %r against 0, %d refusals against none, last "
      "line %r" % (code, refused, last_line(said)))

stop()
