# -*- coding: utf-8 -*-
"""A build that stops takes back the project it made, and nothing else.

Against a stand-in project manager that keeps what Resolve was measured
to do: a created project stands in no list until it is saved or gets a
Timeline, LoadProject writes it out, DeleteProject refuses the open one.
In order: a camera file Resolve will not take -- the made project is
deleted, the one open before is open again, no other project is asked
for, the reason still reaches the caller, and the run says so; a project
the run only opened stays; with nothing open that could be opened again
the made one stays open and the run says so; where Resolve keeps it the
run says that too; and a build that finishes keeps what it made.
"""
PLATFORM_BOUND = True
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import contextlib
import io
import shutil
import tempfile
import time
import the_program

SCRIPT = the_program.SCRIPT

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


class Clip(object):
    def __init__(self, path): self.path = path
    def GetName(self): return os.path.basename(self.path)
    def GetClipProperty(self, key=None):
        return self.path if key == "File Path" else {"File Path": self.path}


class Folder(object):
    def __init__(self, p): self.p = p
    def GetClipList(self): return list(self.p.pool)


class TL(object):
    def __init__(self, name): self.name = name
    def GetName(self): return self.name


class MP(object):
    """A file whose name says it cannot be read is imported as nothing,
    as Resolve does with text under a camera's name. The first Timeline
    puts an unsaved project into the list -- measured on Resolve
    21.0.4.5, see resolve/live/project_run_puts_back_test.py."""
    def __init__(self, p): self.p = p
    def ImportMedia(self, paths):
        fresh = [Clip(x) for x in paths if "unreadable" not in x]
        self.p.pool.extend(fresh)
        return fresh
    def GetRootFolder(self): return Folder(self.p)
    def CreateEmptyTimeline(self, name):
        if any(t.name == name for t in self.p.tls):
            return None
        tl = TL(name)
        self.p.tls.append(tl)
        self.p.pm.saved[self.p.name] = self.p
        return tl


class Project(object):
    def __init__(self, name, pm):
        self.name, self.pm, self.pool, self.tls = name, pm, [], []
        self.mp = MP(self)
    def GetName(self): return self.name
    def GetMediaPool(self): return self.mp
    def GetTimelineCount(self): return len(self.tls)
    def GetTimelineByIndex(self, i):
        return self.tls[i - 1] if 1 <= i <= len(self.tls) else None
    def SetCurrentTimeline(self, tl): return True


class PM(object):
    """What Resolve's project manager was measured to do with these calls
    (resolve/live/resolve_ground.py): only a saved project stands in the
    list and can be loaded or deleted; creating drops an unsaved open
    project for good; loading writes it out under its own name; the open
    project cannot be deleted. `keep` makes DeleteProject refuse all."""
    def __init__(self, listed, open_name, saved_open=True, keep=False):
        self.saved = dict((n, Project(n, self)) for n in listed)
        self.current = (self.saved[open_name] if saved_open
                        else Project(open_name, self))
        self.keep = keep
        self.asked_to_delete, self.closed = [], []
    def GetProjectListInCurrentFolder(self): return sorted(self.saved)
    def GetCurrentProject(self): return self.current
    def CreateProject(self, n):
        if n in self.saved:
            return None
        self.current = Project(n, self)
        return self.current
    def LoadProject(self, n):
        if n not in self.saved:
            return None
        if self.current is not None:
            self.saved[self.current.name] = self.current
        self.current = self.saved[n]
        return self.current
    def SaveProject(self):
        self.saved[self.current.name] = self.current
        return True
    def DeleteProject(self, n):
        self.asked_to_delete.append(n)
        if self.keep or n not in self.saved or self.saved[n] is self.current:
            return False
        del self.saved[n]
        return True
    def CloseProject(self, p):
        self.closed.append(p.GetName())
        self.current = None
        return True


class R(object):
    def __init__(self, pm): self.pm = pm
    def GetProductName(self): return "DaVinci Resolve Studio"
    def GetVersionString(self): return "21.0.4"
    def GetProjectManager(self): return self.pm


# The stand-in refuses what Resolve refuses. Preconditions of the
# material, not judgements on the program.
_probe = PM(["Mine"], "Mine")
assert _probe.DeleteProject("Mine") is False       # the open one
assert _probe.DeleteProject("Nowhere") is False    # one never saved
assert _probe.CreateProject("Mine") is None        # a taken name
_probe.CreateProject("Fresh")
assert "Fresh" not in _probe.GetProjectListInCurrentFolder()
assert _probe.LoadProject("Fresh") is None         # in no list

# Everything around import and the project is stubbed out; the build,
# the import and the taking back are real.
vpm.apply_project_settings = lambda p, d: None
vpm.set_loudness_target = lambda p, x: None
vpm.set_remote_grades = lambda p, on=False: None
vpm.lead_in_offset = lambda *a, **k: 0
vpm.build_cut_timeline = lambda *a, **k: None
vpm.colour_clips_by_camera = lambda *a, **k: None
vpm.insert_intro_and_outro = lambda *a, **k: None
vpm.create_colour_groups = lambda *a, **k: None
vpm.queue_render_job = lambda *a, **k: None
vpm.add_speaker_markers = lambda *a, **k: None
vpm.mix_file_from_handover = lambda d: (None, None)
CURRENT = {}
vpm.connect_to_resolve = lambda: R(CURRENT["pm"])

work = tempfile.mkdtemp()
good = os.path.join(work, "WideCam_C001.mov")
unreadable = os.path.join(work, "Guest_C002_unreadable.mov")
for path in (good, unreadable):
    with open(path, "w") as f:
        f.write("stands in for a film\n")


def handover(files):
    cams = [{"camera": "Cam%d" % i, "track": "Cam%d" % i, "wide": i == 1,
             "file": x, "source": x, "offset": 0.0, "duration": 60.0,
             "audio_tracks": ["Full-Mix"]}
            for i, x in enumerate(files, 1)]
    return {"production": "X", "fps": 25.0, "start_tc": "01:00:00:00",
            "speakers": [], "cameras": cams, "length_s": 60.0}


def build(pm, files, carry_on=None):
    """One build against *pm*: (what it raised or returned, what it said)."""
    CURRENT["pm"] = pm
    said = io.StringIO()
    try:
        with contextlib.redirect_stdout(said):
            outcome = vpm.build_resolve_project(handover(files), carry_on,
                                                log="")
    except Exception as e:
        outcome = e
    return outcome, said.getvalue()


def open_name(pm):
    return pm.current.GetName() if pm.current is not None else ""


STOPPED = vpm.T('Not found again after import: %s') % os.path.basename(
    unreadable)
TAKEN_BACK = vpm.T('  The half-built project %r is deleted again, %r is '
                   'open again.') % ("X", "Mine")

try:
    print("\n1. A camera file Resolve will not take")
    pm = PM(["Mine", "Other"], "Mine")
    outcome, said = build(pm, [good, unreadable])
    check("a stopped build deletes the project it made",
          "X" not in pm.saved and open_name(pm) != "X",
          "the list holds %s, Resolve has %r open"
          % (sorted(pm.saved), open_name(pm)))
    check("and opens again the project that was open before",
          open_name(pm) == "Mine",
          "Resolve has %r open, 'Mine' was open before" % open_name(pm))
    check("no other project is asked to be deleted",
          pm.asked_to_delete == ["X"]
          and sorted(pm.saved) == ["Mine", "Other"],
          "asked to delete %s, the list holds %s against ['Mine', 'Other']"
          % (pm.asked_to_delete, sorted(pm.saved)))
    check("the reason the build stopped still reaches the caller",
          isinstance(outcome, RuntimeError) and str(outcome) == STOPPED,
          "the build ended in %r against RuntimeError(%r)"
          % (outcome, STOPPED))
    check("the run says it deleted the project and what it opened",
          TAKEN_BACK in said,
          "%r in what the build said: %s" % (TAKEN_BACK, TAKEN_BACK in said))

    print("\n2. A project the run only opened")
    pm = PM(["Mine", "X"], "Mine")
    outcome, said = build(pm, [good, unreadable], "keep")
    check("a stopped build leaves a project it only opened standing",
          "X" in pm.saved and pm.asked_to_delete == [],
          "the list holds %s, asked to delete %s, the build ended in %r"
          % (sorted(pm.saved), pm.asked_to_delete, outcome))

    print("\n3. Nothing open that could be opened again")
    # A fresh Resolve opens on an unsaved project; creating took it away.
    pm = PM(["Other"], "Untitled Project", saved_open=False)
    outcome, said = build(pm, [good, unreadable])
    stays = vpm.T('  The project %r this run made stays open -- nothing was '
                  'open before\n  that could be opened again. Delete it in '
                  'Resolve\'s project manager.') % "X"
    check("with nothing to open again the made project stays open",
          open_name(pm) == "X" and pm.closed == []
          and pm.asked_to_delete == [],
          "Resolve has %r open, closed %s, asked to delete %s"
          % (open_name(pm), pm.closed, pm.asked_to_delete))
    check("and the run says it stays and is to be deleted by hand",
          stays.strip() in said,
          "%r in what the build said: %s" % (stays.strip()[:50],
                                             stays.strip() in said))

    print("\n4. Resolve keeps the made project")
    pm = PM(["Mine"], "Mine", keep=True)
    outcome, said = build(pm, [good, unreadable])
    caution = vpm.T('  Caution: the half-built project %r could not be '
                    'deleted, or %r not\n  opened again. Please do it in '
                    'Resolve\'s project manager.') % ("X", "Mine")
    check("where Resolve keeps the made project the run says so",
          caution.strip() in said and TAKEN_BACK not in said,
          "the caution in what the build said: %s, the all-clear: %s"
          % (caution.strip() in said, TAKEN_BACK in said))

    print("\n5. A build that finishes")
    pm = PM(["Mine"], "Mine")
    outcome, said = build(pm, [good])
    check("a build that finishes keeps the project it made, open",
          outcome == 0 and "X" in pm.saved and open_name(pm) == "X"
          and pm.asked_to_delete == [],
          "the build ended in %r, the list holds %s, %r is open, asked to "
          "delete %s" % (outcome, sorted(pm.saved), open_name(pm),
                         pm.asked_to_delete))
except Exception as e:
    import traceback
    traceback.print_exc()
    check("the run reached the end without an exception", False,
          "%s: %s" % (type(e).__name__, str(e)[:120]))
finally:
    shutil.rmtree(work, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
