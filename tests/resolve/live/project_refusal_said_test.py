# -*- coding: utf-8 -*-
"""A project the build cannot make is said so, and nothing half is built.

Against a DaVinci Resolve that is really running, through the program's
own build_resolve_project. In order -- a project name that is taken, with
the run told to stop: the build stops, says that nothing was created,
makes no second project beside it and leaves the one of that name as it
was; then the ground, that Resolve imports nothing of a file it cannot
read; and a camera file of that kind in the handover: the build stops,
names that file, and leaves no timeline behind.

The limit: a track Resolve refuses cannot be brought about in a real
Resolve on purpose, so that stays with project_refusal_heeded's stand-in.

The material is the shared interview fixture, read and never written;
the unreadable file is text under a camera's name, in a temporary folder
of the test's own. A step that throws is a failed judgement and not a
traceback, so the closing count is reached whatever happens.
"""
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import resolve_ground as ground_of

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def listed(pm):
    return pm.GetProjectListInCurrentFolder() or []


def open_now(pm):
    p = pm.GetCurrentProject()
    return p.GetName() if p else ""


def refusal(d, carry_on, name):
    """Run the build, and return what it raised -- "" where it raised nothing.

    A RuntimeError is how build_resolve_project stops; anything else is
    left to the outer handler, where it is a failed judgement of its own.
    """
    try:
        vpm.build_resolve_project(d, carry_on, name)
    except RuntimeError as e:
        return str(e)
    return ""


vpm = ground_of.program()
resolve = ground_of.a_resolve(vpm)
print("Resolve: %s %s" % (resolve.GetProductName(), resolve.GetVersionString()))

folder = ground_of.fixture("interview")
if not os.path.isdir(folder):
    ground_of.leave_out("no interview fixture at %s -- run 'cd tests && "
                        "bash fixtures.sh' to build it" % folder)
camera_file = ground_of.cameras_of(folder)
if len(camera_file) < 2:
    ground_of.leave_out("the interview fixture holds %d camera files, at "
                        "least 2 are needed -- run 'cd tests && bash "
                        "fixtures.sh force'" % len(camera_file))

work = tempfile.mkdtemp(prefix="vpm_refusal_")
# Text under a camera's name: a file that is there, so the program's own
# "these files do not exist" does not catch it first, and that no reader
# of pictures can make anything of.
unreadable = os.path.join(work, "PresentersCam_01011855_C009.mov")
with open(unreadable, "w") as f:
    f.write("this is not a film, only its name says so\n" * 200)
UNREADABLE_NAME = os.path.basename(unreadable)


def handover(files):
    """A handover the build takes, with these files as its cameras."""
    cams = []
    for i, path in enumerate(files):
        cams.append({"camera": "Cam%d" % (i + 1), "track": "Cam%d" % (i + 1),
                     "wide": i == 0, "file": path, "source": path,
                     "offset": 0.0, "duration": 120.0,
                     "audio_tracks": ["Full-Mix" if i == 0 else "Cam%d"
                                      % (i + 1)]})
    return {"fps": 25.0, "fps_measured": 25.0, "drop_frame": False,
            "width": 1280, "height": 720, "start_tc": "01:00:10:00",
            "in_point": "01:00:10:00", "speakers": [], "cameras": cams,
            "cut": [{"camera": "Cam1", "start": 0.0, "end": 4.0}],
            "length_s": 120.0}


ground = ground_of.OwnProject(vpm, resolve, "refusal")
# The project the second build makes for itself. Of the tests' shape, so
# the sweep takes it too if this test dies before its finally.
second = ground_of.a_test_name("unread")
pm = ground.pm
try:
    p = ground.open()
    mp = p.GetMediaPool()
    # Something in the project of the taken name, so that "left as it
    # was" has something to lose.
    vpm.create_timeline(mp, "kept")
    pm.SaveProject()
    held = p.GetTimelineCount()

    print("\n1. A name that is taken, and the run told to stop")
    among = len(listed(pm))
    said = refusal(handover(camera_file[:2]), "abort", ground.name)
    check("a taken name stops the build when the run says stop",
          bool(said), "build_resolve_project raised %r" % said[:80])
    check("and it says that nothing was created",
          said == vpm.T('Stopped. Nothing was created.'),
          "it said %r" % said[:80])
    check("no second project appears beside the taken name",
          len(listed(pm)) == among
          and "%s 2" % ground.name not in listed(pm),
          "%d projects in the list, %d before; %r among them: %s"
          % (len(listed(pm)), among, "%s 2" % ground.name,
             "%s 2" % ground.name in listed(pm)))
    check("the project of that name is left open and as it was",
          open_now(pm) == ground.name
          and pm.GetCurrentProject().GetTimelineCount() == held,
          "Resolve has %r open with %s timelines; %r held %d"
          % (open_now(pm), pm.GetCurrentProject().GetTimelineCount()
             if pm.GetCurrentProject() else "no", ground.name, held))

    print("\n2. A camera file Resolve cannot read")
    # The ground first, in the test's own project: what Resolve does with
    # such a file when asked directly. Red here says Resolve took it, and
    # then every line below is about that and not about the program.
    pool_before = len(mp.GetRootFolder().GetClipList() or [])
    took = mp.ImportMedia([unreadable]) or []
    pool_after = len(mp.GetRootFolder().GetClipList() or [])
    check("Resolve imports nothing of a file it cannot read",
          not took and pool_after == pool_before,
          "ImportMedia gave back %d clips; the pool holds %d, %d before"
          % (len(took), pool_after, pool_before))
    # Saved before the build creates its own project beside it: whatever
    # Resolve does with unsaved changes on the way out, there are none.
    pm.SaveProject()
    said = refusal(handover([camera_file[0], unreadable]), None, second)
    check("a camera file Resolve would not take stops the build",
          bool(said), "build_resolve_project raised %r" % said[:80])
    check("and the refusal names that file",
          said == vpm.T('Not found again after import: %s')
          % UNREADABLE_NAME,
          "it said %r" % said[:80])
    # Only the timelines. The project the build made, and the good clip
    # already in its pool, are the owner's question (see the report of
    # E-331), and a judgement on them would pin today's answer.
    now = pm.GetCurrentProject()
    check("a refused camera file leaves no timeline behind",
          open_now(pm) == second and now.GetTimelineCount() == 0,
          "Resolve has %r open, the build made %r; it holds %s timelines"
          % (open_now(pm), second,
             now.GetTimelineCount() if now else "no"))
except Exception as e:
    import traceback
    traceback.print_exc()
    check("the run reached the end without an exception", False,
          "%s: %s" % (type(e).__name__, str(e).replace("\n", " ")[:120]))
finally:
    left = []
    try:
        # Back to the test's own project first: close() saves and closes
        # the one that is open. Leaving the build's project this way
        # writes it out, so it stands in the list and can be deleted.
        if open_now(pm) != ground.name:
            pm.LoadProject(ground.name)
    except Exception as e:
        left.append("could not open %r again: %s" % (ground.name, e))
    left_over = ground.close()
    if left_over:
        left.append(left_over)
    try:
        if second in listed(pm):
            pm.DeleteProject(second)
        if second in listed(pm):
            left.append("%r is still in the project list" % second)
    except Exception as e:
        left.append("could not delete %r: %s" % (second, e))
    shutil.rmtree(work, ignore_errors=True)

check("the projects the test made are gone again", not left,
      "; ".join(left) or "%r and %r no longer in the project list"
      % (ground.name, second))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
