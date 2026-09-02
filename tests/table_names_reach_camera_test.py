# -*- coding: utf-8 -*-
"""A speaker's name reaches the camera row, typed or only suggested.

The name field starts empty with the guess from the file name standing
in it in grey, and a placeholder is not a value. Everything that read
the field alone therefore saw nothing: the camera column said "?"
where the name was plainly on the screen, and the camera's new file
name -- which travels to Resolve -- was built without it.

The sections: the cell that says where a camera gets its audio from,
and the file name the camera is offered. What this cannot show is that
the window really hands these fields in; that is one call at each of
the two places.
"""
import os
import sys
import time
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
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


def field(typed="", offered=""):
    """A speaker name field as the assignment table builds one.

    The guess is never written into the field: it is hung on the value
    as the placeholder, which is exactly what made it invisible.
    """
    value = vpm.Value(typed)
    value.suggested = offered
    return value


NOWHERE = {"barred": set(), "pushed": {}, "aside": {}}
CAMERA = "GuestCam_01011858_C003.mov"

print("1. What the camera row says it gets its audio from")
typed = vpm.camera_gets_from(CAMERA, NOWHERE, [field("Guest")])
check("a typed name stands in the camera's audio cell",
      typed == "Guest", "%r against 'Guest'" % typed)
offered = vpm.camera_gets_from(CAMERA, NOWHERE, [field("", "Guest")])
check("and so does a name that is only offered in grey",
      offered == "Guest", "%r against 'Guest'" % offered)
three = vpm.camera_gets_from(
    CAMERA, NOWHERE,
    [field("", "Guest"), field("Presenter"), field("", "CoPresenter")])
check("three of them come out in the order the rows stand in",
      three == "Guest, Presenter, CoPresenter",
      "%r against 'Guest, Presenter, CoPresenter'" % three)
nameless = vpm.camera_gets_from(CAMERA, NOWHERE, [field("", "")])
check("a row with no name at all is still the one that says ?",
      nameless == "?", "%r against '?'" % nameless)

print("\n2. The file name the camera is offered")
# A speaker who is not in the camera's own name: "Guest" on GuestCam
# stands in the file name whether it was read off the field or not,
# and a check that cannot tell the two apart is no check.
was = vpm.camera_name_suggestion("Interview", CAMERA, [field("Presenter")])
check("a typed name is in the camera's new file name",
      "Presenter" in was, "%r -- wanted 'Presenter' in it" % was)
grey = vpm.camera_name_suggestion("Interview", CAMERA,
                                  [field("", "CoPresenter")])
check("and a name only offered in grey is in it too",
      "CoPresenter" in grey, "%r -- wanted 'CoPresenter' in it" % grey)
check("and it is the name the run would build out of that name",
      grey == vpm.camera_output_name("Interview", CAMERA, ["CoPresenter"]),
      "%r against %r"
      % (grey, vpm.camera_output_name("Interview", CAMERA, ["CoPresenter"])))
empty = vpm.camera_name_suggestion("Interview", CAMERA, [field("", "")])
check("a camera nobody is on falls back on the overall mix",
      empty == vpm.camera_output_name("Interview", CAMERA,
                                      ["Audio-Full-Mix"]),
      "%r against %r" % (empty, vpm.camera_output_name(
          "Interview", CAMERA, ["Audio-Full-Mix"])))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
