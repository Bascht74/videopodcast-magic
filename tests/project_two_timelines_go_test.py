# -*- coding: utf-8 -*-
"""#60: update a project -- the two timelines go, nothing else."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys, time
began = time.time()
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

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
    def __init__(self, name, tracks=None):
        self.name = name
        self.v = dict(tracks or {})
    def GetName(self): return self.name
    def GetTrackCount(self, kind): return len(self.v) if kind == "video" else 0
    def GetItemListInTrack(self, kind, i): return self.v.get(i, [])


class MP(object):
    def __init__(self, project): self.p = project; self.deleted = []
    def DeleteTimelines(self, items):
        for tl in items:
            if tl in self.p.tls:
                self.p.tls.remove(tl)
                self.deleted.append(tl.GetName())
        return True


class Project(object):
    def __init__(self, tls): self.tls = list(tls); self.current = None
    def GetTimelineCount(self): return len(self.tls)
    def GetTimelineByIndex(self, i):
        return self.tls[i - 1] if 1 <= i <= len(self.tls) else None
    def SetCurrentTimeline(self, tl): self.current = tl; return True
    def GetMediaPool(self): return self.mp


def build_project(names):
    p = Project([TL(n) for n in names])
    p.mp = MP(p)
    return p


print("1. Both timelines go, everything else stays")
p = build_project(["X Cut", "X Multicam", "X Multicam (Backup)",
           "My own timeline", "X Cut 2"])
gone, stayed = vpm.refresh_resolve_timelines(
    p, p.mp, ["X Cut", "X Multicam"])
left_over = [t.GetName() for t in p.tls]
check("deleted: cut and multicam",
        sorted(gone) == ["X Cut", "X Multicam"], str(gone))
check("nothing stayed behind", stayed == [], str(stayed))
check("backup copy still there", "X Multicam (Backup)" in left_over)
check("foreign timeline still there", "My own timeline" in left_over)
check("numbered leftovers untouched", "X Cut 2" in left_over)
check("switched over before deleting", p.current is not None,
        p.current.GetName() if p.current else "-")

print("\n2. They do not exist at all -- nothing happens")
p = build_project(["Something else"])
gone, stayed = vpm.refresh_resolve_timelines(
    p, p.mp, ["X Cut", "X Multicam"])
check("nothing deleted", gone == [] and stayed == [])
check("stock unchanged", [t.GetName() for t in p.tls] == ["Something else"])

print("\n3. Deleting fails -> reported, not hushed up")
p = build_project(["X Cut", "X Multicam"])
p.mp.DeleteTimelines = lambda items: True        # pretends it worked
gone, stayed = vpm.refresh_resolve_timelines(
    p, p.mp, ["X Cut", "X Multicam"])
check("recognised as stayed",
        sorted(stayed) == ["X Cut", "X Multicam"], str(stayed))
check("nothing wrongly reported as gone", gone == [], str(gone))

print("\n4. DeleteTimelines throws -> follow up one at a time")
p = build_project(["X Cut", "X Multicam"])
real = p.mp.DeleteTimelines
def fussy(items):
    if len(items) > 1:
        raise RuntimeError("one at a time only")
    return real(items)
p.mp.DeleteTimelines = fussy
gone, stayed = vpm.refresh_resolve_timelines(
    p, p.mp, ["X Cut", "X Multicam"])
check("both gone all the same",
        sorted(gone) == ["X Cut", "X Multicam"], str(gone))

print("\n5. The question now knows four possibilities")
asked = {}
class PM(object):
    def GetProjectListInCurrentFolder(self): return ["X"]
    def LoadProject(self, n): return "PROJECT"
    def CreateProject(self, n): return "NEW"
real_ask = vpm.ask_choice
def remember(possible, heading, title=None, default_value=None, switch=None):
    asked["keys"] = [k for k, _ in possible]
    asked["switch"] = switch
    return "update"
vpm.ask_choice = remember
pr, kind = vpm.open_or_create_project(PM(), "X")
vpm.ask_choice = real_ask
check("four possibilities, update first",
        asked["keys"] == ["update", "keep", "new", "abort"],
        str(asked["keys"]))
check("names the right switch",
        asked["switch"] == "--resolve-project", str(asked["switch"]))
check("kind is returned", (pr, kind) == ("PROJECT", "update"),
        str((pr, kind)))

print("\n6. New project -> kind 'created', no question")
class PM2(PM):
    def GetProjectListInCurrentFolder(self): return []
pr, kind = vpm.open_or_create_project(PM2(), "Y")
check("created", (pr, kind) == ("NEW", "created"), str((pr, kind)))

print("\n7. Given by switch -> no question asked")
pr, kind = vpm.open_or_create_project(PM(), "X", "keep")
check("keep passed through", kind == "keep", kind)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
