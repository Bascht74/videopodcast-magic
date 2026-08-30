# -*- coding: utf-8 -*-
"""#60 in a whole run: build twice, update on the second pass."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
def check(name, ok, extra=""):
    print("  %-50s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


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
    def DuplicateTimeline(self, name):
        if any(t.GetName() == name for t in self.p.tls):
            return None
        k = TL(name, self.p)
        k.v = {i: list(x) for i, x in self.v.items()}
        self.p.tls.append(k)
        return k


class MP(object):
    def __init__(self, p): self.p = p; self.imported = []
    def CreateEmptyTimeline(self, name):
        if any(t.GetName() == name for t in self.p.tls):
            return None
        tl = TL(name, self.p); self.p.tls.append(tl); return tl
    def DeleteTimelines(self, items):
        for tl in items:
            if tl in self.p.tls: self.p.tls.remove(tl)
        return True


class Project(object):
    def __init__(self, name):
        self.name, self.tls, self.current = name, [], None
        self.mp = MP(self)
    def GetMediaPool(self): return self.mp
    def GetTimelineCount(self): return len(self.tls)
    def GetTimelineByIndex(self, i):
        return self.tls[i - 1] if 1 <= i <= len(self.tls) else None
    def SetCurrentTimeline(self, tl): self.current = tl; return True


class PM(object):
    def __init__(self): self.projects = {}
    def GetProjectListInCurrentFolder(self): return sorted(self.projects)
    def CreateProject(self, n):
        self.projects[n] = Project(n); return self.projects[n]
    def LoadProject(self, n): return self.projects.get(n)


class R(object):
    def __init__(self, pm): self.pm = pm
    def GetProductName(self): return "DaVinci Resolve Studio"
    def GetVersionString(self): return "21.0.4"
    def GetProjectManager(self): return self.pm


# Everything outside #60 is stubbed out -- the run itself is the subject.
pm = PM()
vpm.connect_to_resolve = lambda: R(pm)
vpm.apply_project_settings = lambda p, d: None
vpm.set_loudness_target = lambda p, x: None
vpm.set_remote_grades = lambda p, on=True: None
vpm.import_media = lambda mp, paths: {p: Item(os.path.basename(p))
                                        for p in paths}
vpm.queue_render_job = lambda *a, **k: None
vpm.lead_in_offset = lambda *a, **k: 0
vpm.insert_intro_and_outro = lambda *a, **k: None
vpm.colour_clips_by_camera = lambda *a, **k: None
vpm.create_colour_groups = lambda *a, **k: None
vpm.add_speaker_markers = lambda *a, **k: None
vpm.mix_file_from_handover = lambda d: (None, None)
def camera_tl(mp, tl, cameras, clips, d, every_tracks=False):
    for i, cam in enumerate(cameras, 1):
        tl.v[i] = [Item(os.path.basename(cam["file"]))]
vpm.build_camera_timeline = camera_tl
vpm.build_cut_timeline = lambda mp, tl, *a, **k: tl.v.setdefault(
    1, [Item("cut")])

D = {"production": "X", "fps": 30.0, "start_tc": "19:04:27:00",
     "cut": [{"start": 0.0, "end": 10.0, "camera": "Wide"},
                 {"start": 10.0, "end": 20.0, "camera": "Guest"}],
     "cameras": [{"camera": "Wide", "track": "Wide", "file": "/tmp/W.mov",
                  "source": "/tmp/W.mov", "wide": True, "offset": 0.0},
                 {"camera": "Guest", "track": "Guest",
                  "file": "/tmp/G.mov", "source": "/tmp/G.mov",
                  "offset": 0.0}]}

def names(p): return sorted(t.GetName() for t in p.tls)

print("1. First run -- the project comes into being")
vpm.build_resolve_project(dict(D), "keep", log="")
p = pm.projects["X"]
print("   ", names(p))
check("two timelines, no backup copy",
        names(p) == ["X Cut", "X Multicam"], str(names(p)))

print("\n2. Second run with 'keep' -- they pile up (as before)")
vpm.build_resolve_project(dict(D), "keep", log="")
print("   ", names(p))
check("cut 2 has been added", "X Cut 2" in names(p))

print("\n3. Third run with 'update'")
p.tls.append(TL("My own timeline", p))
before_value = names(p)
vpm.build_resolve_project(dict(D), "update", log="")
now = names(p)
print("   ", now)
check("cut back again without a suffix",
        "X Cut" in now and "X Cut 3" not in now)
check("multicam back again without a suffix",
        "X Multicam" in now and "X Multicam 2" not in now)
check("no backup copy any more",
        not [n for n in now if "Backup" in n], str(now))
check("foreign timeline still there", "My own timeline" in now)
check("nothing grew", len(now) == len(before_value),
        "%d/%d" % (len(now), len(before_value)))

print("\n4. A backup copy from an earlier run stays put")
p.tls.append(TL("X Multicam (Backup)", p))
vpm.build_resolve_project(dict(D), "update", log="")
check("old backup copy untouched",
        "X Multicam (Backup)" in names(p), str(names(p)))

print("\n5. Updating with other cameras")
D2 = dict(D)
D2["cameras"] = D["cameras"] + [{"camera": "Third", "track": "Third",
                                 "file": "/tmp/T.mov", "source": "/tmp/T.mov",
                                 "offset": 0.0}]
vpm.build_resolve_project(dict(D2), "update", log="")
now = names(p)
print("   ", now)
check("multicam there, without a suffix", "X Multicam" in now)
check("no second backup copy made",
        [n for n in now if "Backup" in n] == ["X Multicam (Backup)"],
        str([n for n in now if "Backup" in n]))

print("\n%s" % ("ALL OK" if not error else "FAIL: " + ", ".join(error)))
sys.exit(1 if error else 0)
