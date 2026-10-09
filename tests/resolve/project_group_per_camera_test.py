# -*- coding: utf-8 -*-
"""Every camera gets one colour group, and every clip of it lands there.

create_colour_groups against a stand-in project and timeline: two
cameras, the wide shot with three cuts and the guest with two. In turn:
a group per camera under the camera's name and each clip in its own;
a group already in the project taken again rather than made twice; a
group Resolve will not make, by answer or by raising, named and the
other camera grouped all the same; clips a group would not take, by
answer or by raising, counted in the line; groups made where the
project will not list those it has; and a timeline with no camera on
it, which makes no group and says so.
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
import the_program
import contextlib
import io
import time
import resolve_stand_in as stand

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


WIDE, GUEST = "WideCam_C001", "GuestCam_C003"
CAMERAS = [{"camera": WIDE, "track": WIDE, "file": "/tmp/%s.mov" % WIDE,
            "source": "/tmp/%s.mov" % WIDE},
           {"camera": GUEST, "track": GUEST, "file": "/tmp/%s.mov" % GUEST,
            "source": "/tmp/%s.mov" % GUEST}]


def ground(**switches):
    """A project and a timeline: three wide cuts on V1, two guest on V2."""
    p = stand.Project(**switches)
    tl = p.pool.CreateEmptyTimeline("Episode Multicam")
    tl.AddTrack("video")
    for track, name, n in ((1, WIDE, 3), (2, GUEST, 2)):
        for _ in range(n):
            tl.lay("video", track, stand.Item(name + ".mov", 100))
    return p, tl


def group(p, tl):
    """What create_colour_groups printed."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        vpm.create_colour_groups(p, tl, CAMERAS)
    return out.getvalue()


def items(tl, track):
    return tl.GetItemListInTrack("video", track)


def where(tl, track):
    """The group name each clip of a track sits in, None for none."""
    return [x.group.GetName() if x.group else None for x in items(tl, track)]


print("1. A group per camera")
p, tl = ground()
said = group(p, tl)
check("every camera gets a colour group under its own name",
      sorted(g.GetName() for g in p.groups) == sorted([WIDE, GUEST]),
      "groups %r" % [g.GetName() for g in p.groups])
check("every clip lands in the group of its own camera",
      where(tl, 1) == [WIDE] * 3 and where(tl, 2) == [GUEST] * 2,
      "V1 in %r, V2 in %r" % (where(tl, 1), where(tl, 2)))

print("\n2. A group the project already has")
p, tl = ground()
before = p.AddColorGroup(WIDE)
said = group(p, tl)
check("a group already in the project is taken again, not made twice",
      [g.GetName() for g in p.groups].count(WIDE) == 1
      and all(x.group is before for x in items(tl, 1)),
      "%d groups named %s, V1 in the old one: %r"
      % ([g.GetName() for g in p.groups].count(WIDE), WIDE,
         [x.group is before for x in items(tl, 1)]))

print("\n3. A group Resolve will not make")
p, tl = ground(refuse_groups=[GUEST])
said = group(p, tl)
named = [l.strip() for l in said.splitlines() if GUEST in l]
check("a group Resolve answers no to is named in a line",
      len(named) == 1 and where(tl, 2) == [None, None],
      "lines naming it %r, V2 in %r" % (named, where(tl, 2)))
check("the other camera is grouped all the same",
      where(tl, 1) == [WIDE] * 3, "V1 in %r" % (where(tl, 1),))

p, tl = ground(throw=["AddColorGroup"])
said = group(p, tl)
named = [l.strip() for l in said.splitlines()
         if "stand-in AddColorGroup refused" in l]
check("a group Resolve raises on is named with what it said",
      len(named) == 2 and where(tl, 1) == [None] * 3,
      "%d lines with the reason, V1 in %r" % (len(named), where(tl, 1)))

print("\n4. Clips a group will not take")
p, tl = ground()
items(tl, 2)[1].refuse.add("AssignToColorGroup")
said = group(p, tl)
short = [l.strip() for l in said.splitlines() if GUEST in l]
check("clips a group would not take are counted, one of two",
      len(short) == 1 and " 1 " in short[0] and " 2 " in short[0],
      "said %r" % (short,))

p, tl = ground()
items(tl, 1)[0].throw.add("AssignToColorGroup")
said = group(p, tl)
short = [l.strip() for l in said.splitlines() if WIDE in l]
check("a clip a group raises on is counted too, two of three",
      len(short) == 1 and " 2 " in short[0] and " 3 " in short[0],
      "said %r" % (short,))

print("\n5. Groups that cannot be listed")
p, tl = ground(throw=["GetColorGroupsList"])
said = group(p, tl)
check("a project that will not list its groups still gets them made",
      sorted(g.GetName() for g in p.groups) == sorted([WIDE, GUEST])
      and where(tl, 2) == [GUEST] * 2,
      "groups %r, V2 in %r" % ([g.GetName() for g in p.groups],
                               where(tl, 2)))

print("\n6. No camera on the timeline")
p = stand.Project()
tl = p.pool.CreateEmptyTimeline("Empty")
tl.lay("video", 1, stand.Item("Somebody_else.mov", 100))
said = group(p, tl)
check("a timeline without a camera's clip says it has none",
      p.count("AddColorGroup") == 0 and said.strip() != "",
      "AddColorGroup asked %d times, said %r"
      % (p.count("AddColorGroup"), said.strip()[:80]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
