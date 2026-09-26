# -*- coding: utf-8 -*-
"""A speaker's name reaches the camera row, typed or only suggested.

The name field starts empty with the guess standing in it in grey, and
a placeholder is not a value: what reads the field has to read the
guess too. The sections: the cell that says where a camera gets its
audio from, its names sorted as the file name sorts them, lower case
and umlauts too, and the mix where nobody is on it; and the file name
the camera is offered. What this cannot show is that the window really
hands these fields in; that is one call at each of the two places.
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
import time
import the_program

SCRIPT = the_program.SCRIPT
vpm = the_program.load()
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

    The guess is never written into the field: it is offered in grey,
    and the field itself is what knows that.
    """
    return vpm.SpeakerName(typed, offered)


CAMERA = "GuestCam_01011858_C003.mov"

print("1. What the camera row says it gets its audio from")
typed = vpm.camera_gets_from([field("Guest")])
check("a typed name stands in the camera's audio cell",
      typed == "Guest", "%r against 'Guest'" % typed)
offered = vpm.camera_gets_from([field("", "Guest")])
check("and so does a name that is only offered in grey",
      offered == "Guest", "%r against 'Guest'" % offered)
three = vpm.camera_gets_from(
    [field("", "Guest"), field("Presenter"), field("", "CoPresenter")])
# In the rows Guest, Presenter, CoPresenter: sorted is another order,
# so a cell that keeps the rows' order cannot pass by chance.
check("three of them come out sorted, as in the camera's file name",
      three == "CoPresenter, Guest, Presenter",
      "%r against 'CoPresenter, Guest, Presenter'" % three)
# Plain sorting puts Bob before anna, and the O with an umlaut after
# Paul, where a reader does not look for it.
UMLAUT = "\u00d6zlem"
READ = "anna, Bob, %s, Paul" % UMLAUT
mixed = vpm.camera_gets_from(
    [field("Paul"), field("", UMLAUT), field("anna"), field("", "Bob")])
check("and lower case and an umlaut stand where a reader expects them",
      mixed == READ, "%r against %r" % (mixed, READ))
nameless = vpm.camera_gets_from([field("", "")])
check("a row with no name at all is still the one that says ?",
      nameless == "?", "%r against '?'" % nameless)
# A marked wide shot is one of these: why nobody speaks on it stands
# grey in its own fields, and this cell says what it gets.
wide = vpm.camera_gets_from([])
check("a camera nobody speaks on says it gets the mix of all tracks",
      wide == vpm.T("the mix of all tracks"),
      "%r against %r" % (wide, vpm.T("the mix of all tracks")))

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
