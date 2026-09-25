# -*- coding: utf-8 -*-
"""The project the run asks for is there, with the rate and size it named.

Against a DaVinci Resolve that is really running, not a stand-in: the
suite has never asked one. In order -- the project comes into being and
Resolve has it open, the rate and the size arrive and can be read back, a
rate Resolve does not know becomes the nearest one it does, drop frame
follows the handover both ways, and asking a second time for the same name
opens what is there instead of making a second one. The project is the
test's own and goes at the end.

Two limits of the method. Drop frame is asked after only at 29.97: at 25
Resolve refuses to switch it on, so a check there would be green whatever
the run did. And the playback rate is not asked after at all -- Resolve
refuses to set it, which is a finding about Resolve and not a claim about
the program.

A step that throws is a failed judgement and not a traceback, so the
closing count is reached whatever happens.
"""
import os
import sys
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


def number(x):
    """Resolve answers 25.0 where 25 was set, and '1280' where 1280 was."""
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


vpm = ground_of.program()
resolve = ground_of.a_resolve(vpm)
print("Resolve: %s %s" % (resolve.GetProductName(), resolve.GetVersionString()))

ground = ground_of.OwnProject(vpm, resolve, "settings")
pm = ground.pm
try:
    p = ground.open()
    print("\n1. The project comes into being")
    open_now = pm.GetCurrentProject()
    check("the project the run asked for is the one Resolve has open",
          open_now is not None and open_now.GetName() == ground.name,
          "open is %r, asked for %r"
          % (open_now.GetName() if open_now else None, ground.name))
    check("a name nobody used before is reported as created",
          ground.kind == "created",
          "reported %r, expected 'created'" % ground.kind)
    check("the saved project stands in the project manager's list",
          ground.listed(),
          "%r among %d projects"
          % (ground.name, len(pm.GetProjectListInCurrentFolder() or [])))

    print("\n2. Rate and size arrive")
    # 25 frames a second and 1280x720 -- the fixture material's own rate.
    # A fresh project on this machine carried 3840x2160 at 30, so neither
    # number below is one it would have had anyway.
    vpm.apply_project_settings(p, {"fps": 25.0, "width": 1280, "height": 720,
                                   "drop_frame": False})
    check("the frame rate the handover names is the project's",
          number(p.GetSetting("timelineFrameRate")) == 25.0,
          "project carries %r, handover said 25.0"
          % p.GetSetting("timelineFrameRate"))
    check("the timeline width the handover names is the project's",
          number(p.GetSetting("timelineResolutionWidth")) == 1280.0,
          "project carries %r, handover said 1280"
          % p.GetSetting("timelineResolutionWidth"))
    check("the timeline height the handover names is the project's",
          number(p.GetSetting("timelineResolutionHeight")) == 720.0,
          "project carries %r, handover said 720"
          % p.GetSetting("timelineResolutionHeight"))

    print("\n3. A rate Resolve does not know becomes one it does")
    # ffprobe measures 23.98 on such material; Resolve knows 23.976 and
    # rejects anything else, so the run decides it rather than letting
    # Resolve pick something.
    vpm.apply_project_settings(p, {"fps": 23.98, "width": 1920, "height": 1080,
                                   "drop_frame": False})
    check("a measured 23.98 reaches the project as 23.976",
          number(p.GetSetting("timelineFrameRate")) == 23.976,
          "project carries %r, expected 23.976"
          % p.GetSetting("timelineFrameRate"))
    # Not that a size arrives, but that a second one does: a size that is
    # never set stays whatever it was, and a check on one number alone is
    # green wherever the machine's own default happens to be that number.
    check("a second size arrives too, the first is not left standing",
          (number(p.GetSetting("timelineResolutionWidth")) == 1920.0
           and number(p.GetSetting("timelineResolutionHeight")) == 1080.0),
          "project carries %rx%r, handover said 1920x1080, before that 1280x720"
          % (p.GetSetting("timelineResolutionWidth"),
             p.GetSetting("timelineResolutionHeight")))

    print("\n4. Drop frame follows the handover, both ways")
    # Only at 29.97: at 25 Resolve refuses to switch drop frame on at all,
    # and a check made there would be green whatever the run did.
    vpm.apply_project_settings(p, {"fps": 29.97, "width": 1920, "height": 1080,
                                   "drop_frame": False})
    check("drop frame is off where the handover has it off",
          number(p.GetSetting("timelineDropFrameTimecode")) == 0.0,
          "project carries %r, handover said off"
          % p.GetSetting("timelineDropFrameTimecode"))
    vpm.apply_project_settings(p, {"fps": 29.97, "width": 1920, "height": 1080,
                                   "drop_frame": True})
    check("drop frame is on where the handover has it on",
          number(p.GetSetting("timelineDropFrameTimecode")) == 1.0,
          "project carries %r, handover said on"
          % p.GetSetting("timelineDropFrameTimecode"))
    check("and 29.97 stays 29.97 rather than becoming 30",
          number(p.GetSetting("timelineFrameRate")) == 29.97,
          "project carries %r, handover said 29.97"
          % p.GetSetting("timelineFrameRate"))

    print("\n5. Asking a second time does not make a second project")
    again, kind = vpm.open_or_create_project(pm, ground.name, "keep")
    # The second call handed back a project object of its own; the cleanup
    # closes that one.
    ground.project = again
    check("the same name a second time is opened, not created",
          kind == "keep", "reported %r, expected 'keep'" % kind)
    check("and it is the project the test made, not another",
          again is not None and again.GetName() == ground.name,
          "opened %r, expected %r"
          % (again.GetName() if again else None, ground.name))
    how_many = (pm.GetProjectListInCurrentFolder() or []).count(ground.name)
    check("there is still only one project of that name",
          how_many == 1, "%d projects called %r" % (how_many, ground.name))
except Exception as e:
    # Every path has to reach the closing lines, or a run that fell over
    # returns 0 and prints no verdict at all.
    import traceback
    traceback.print_exc()
    check("the run reached the end without an exception", False,
          "%s: %s" % (type(e).__name__, str(e).replace("\n", " ")[:120]))
finally:
    left_over = ground.close()

check("the project the test made is gone again", not left_over,
      left_over or "%r no longer in the project list" % ground.name)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
