# -*- coding: utf-8 -*-
"""Clip colours Resolve refuses are counted and said, the rest still set.

usable_clip_colours and colour_clips_by_camera against stand-in
timeline items that take only Resolve's sixteen clip colours. In turn:
the probe puts back the colour a clip had; a clip that will not say its
colour, and one that takes none, leave the whole list on offer; a clip
that refuses its colour, by answer or by raising, counted in a line
while the others are coloured; and a timeline where no clip takes a
colour, which says so.
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
            "source": "/tmp/%s.mov" % WIDE, "wide": True},
           {"camera": GUEST, "track": GUEST, "file": "/tmp/%s.mov" % GUEST,
            "source": "/tmp/%s.mov" % GUEST, "speakers": ["Guest"]}]
# Two names Resolve offers and one it does not.
WANTED = ["Blue", "Cyan", "Teal"]

print("1. The probe")
item = stand.Item(WIDE + ".mov")
item.colour = "Orange"
got = vpm.usable_clip_colours(item, WANTED)
check("the probe puts back the colour the clip had",
      item.colour == "Orange" and got == ["Blue", "Teal"],
      "clip now %r, on offer %r" % (item.colour, got))
item = stand.Item(WIDE + ".mov", throw=["GetClipColor"])
got = vpm.usable_clip_colours(item, WANTED)
check("a clip that will not say its colour is not probed at all",
      got == WANTED and item.count("SetClipColor") == 0,
      "on offer %r, SetClipColor asked %d times"
      % (got, item.count("SetClipColor")))
item = stand.Item(WIDE + ".mov", throw=["SetClipColor"])
got = vpm.usable_clip_colours(item, WANTED)
check("a clip that takes no colour leaves the whole list on offer",
      got == WANTED, "on offer %r" % (got,))


def timeline():
    """Two wide cuts on V1, three guest cuts on V2."""
    tl = stand.Timeline("Episode Cut")
    tl.AddTrack("video")
    for track, name, n in ((1, WIDE, 2), (2, GUEST, 3)):
        for _ in range(n):
            tl.lay("video", track, stand.Item(name + ".mov"))
    return tl


def colour(tl):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        vpm.colour_clips_by_camera(tl, CAMERAS)
    return out.getvalue()


def colours(tl, track):
    return [x.colour for x in tl.GetItemListInTrack("video", track)]


print("\n2. Colouring the cut")
tl = timeline()
guest = tl.GetItemListInTrack("video", 2)
guest[1].refuse.add("SetClipColor")
guest[2].throw.add("SetClipColor")
said = colour(tl)
# The one line that names no angle and counts two.
left = [l.strip() for l in said.splitlines()
        if " 2 " in " %s " % l.strip() and WIDE not in l and GUEST not in l]
check("clips that refuse their colour are counted in a line",
      len(left) == 1 and colours(tl, 2)[1:] == ["", ""],
      "said %r, V2 coloured %r" % (left, colours(tl, 2)))
check("the clips that take their colour are coloured all the same",
      "" not in colours(tl, 1) and colours(tl, 2)[0] != ""
      and colours(tl, 2)[0] != colours(tl, 1)[0],
      "V1 %r, V2 %r" % (colours(tl, 1), colours(tl, 2)))

tl = timeline()
for track in (1, 2):
    for x in tl.GetItemListInTrack("video", track):
        x.refuse.add("SetClipColor")
said = colour(tl)
angles = [l for l in said.splitlines() if WIDE in l or GUEST in l]
check("a timeline where no clip takes a colour says so",
      said.strip() != "" and not angles
      and colours(tl, 1) + colours(tl, 2) == [""] * 5,
      "said %r" % said.strip())

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
