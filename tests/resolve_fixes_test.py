# -*- coding: utf-8 -*-
"""Seven defects a review of the Resolve part turned up.

Each block says what went wrong before, because that is what the check
is guarding. What needs a running Resolve is not here: those three are
marked in the handover note and belong to a real run.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, io, sys, tempfile
import contextlib
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
WORK = tempfile.mkdtemp(prefix="resolvefix_")
bad = []


def check(what, ok, detail=""):
    print("  %-58s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


def spoken(call, *a, **k):
    """Run something and hand back what it printed."""
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        out = call(*a, **k)
    return out, said.getvalue()


print("1. The frame is one a camera really recorded")
# Width and height were each taken as their own maximum, so a landscape
# and a portrait camera together gave a square frame neither of them had.
check("landscape beside portrait",
      vpm.widest_frame({(1920, 1080), (1080, 1920)}) in
      ((1920, 1080), (1080, 1920)),
      str(vpm.widest_frame({(1920, 1080), (1080, 1920)})))
check("the larger of two landscape frames",
      vpm.widest_frame({(1920, 1080), (3840, 2160)}) == (3840, 2160))
check("nothing measured", vpm.widest_frame(set()) == (None, None))
check("one camera", vpm.widest_frame({(1280, 720)}) == (1280, 720))

print("\n2. A render never writes over the delivery before it")
# The target came from the production name alone, so a second run
# replaced the file of the first without asking.
folder = os.path.join(WORK, "out")
os.makedirs(folder)
check("free name stays as it is",
      vpm.free_render_name(folder, "Episode") == "Episode")
open(os.path.join(folder, "Episode.mp4"), "w").write("x")
check("taken name counts up",
      vpm.free_render_name(folder, "Episode") == "Episode_2")
open(os.path.join(folder, "Episode_2.mp4"), "w").write("x")
check("and counts on",
      vpm.free_render_name(folder, "Episode") == "Episode_3")
check("another extension is its own question",
      vpm.free_render_name(folder, "Episode", ".mov") == "Episode")

print("\n3. Two cameras of the same file name are not one camera")
# The map from file name to camera overwrote silently, so the clips of
# the first camera went to the second.


def cam(track, file_path):
    return {"track": track, "file": file_path, "source": file_path}


out, said = spoken(vpm.cameras_by_file_name,
                   [cam("Wide", "/a/C0001.MP4"), cam("Guest", "/b/G.MP4")])
check("two different names, nothing said", len(out) == 2 and not said,
      said.strip()[:50])
out, said = spoken(vpm.cameras_by_file_name,
                   [cam("Wide", "/a/C0001.MP4"),
                    cam("Guest", "/b/C0001.MP4")])
check("same name on both, and it is said", "C0001.MP4" in said
      and "Wide" in said and "Guest" in said, repr(said[:60]))


print("\n4. The clip is found again by its path, not by its name")
# Two cameras writing C0001.MP4 in two folders landed on one media pool
# item, and the second camera then showed the first one's picture.


class Clip(object):
    def __init__(self, name, where=None):
        self.name, self.where = name, where

    def GetName(self):
        return self.name

    def GetClipProperty(self, what):
        if what == "File Path":
            return self.where
        return ""


class Pool(object):
    def __init__(self, clips):
        self.clips = clips

    def ImportMedia(self, paths):
        return list(paths)

    def GetRootFolder(self):
        return self

    def GetClipList(self):
        return self.clips


here = os.path.join(WORK, "one")
there = os.path.join(WORK, "two")
os.makedirs(here); os.makedirs(there)
first = os.path.join(here, "C0001.MP4")
second = os.path.join(there, "C0001.MP4")
for f in (first, second):
    open(f, "w").write("x")
pool = Pool([Clip("C0001.MP4", first), Clip("C0001.MP4", second)])
out, said = spoken(vpm.import_media, pool, [first, second])
check("each path gets its own clip",
      out[first] is not out[second],
      "both on %s" % out[first].where)
check("and the right one", out[first].where == first
      and out[second].where == second)

# The same again from a Resolve that reports no path at all. Guessing
# would put one camera's picture on two tracks, so the run stops.
blind = Pool([Clip("C0001.MP4"), Clip("C0001.MP4")])
try:
    with contextlib.redirect_stdout(io.StringIO()):
        vpm.import_media(blind, [first, second])
    check("no path reported: the run stops", False, "it carried on")
except RuntimeError as e:
    check("no path reported: the run stops", "C0001.MP4" in str(e),
          str(e)[:60])

# One path twice in the list is not a collision.
single = Pool([Clip("C0001.MP4", first)])
try:
    with contextlib.redirect_stdout(io.StringIO()):
        out = vpm.import_media(single, [first, first])
    check("the same path twice is no collision", len(out) == 1)
except RuntimeError as e:
    check("the same path twice is no collision", False, str(e)[:60])

print("\n5. A camera without a render keeps its measured offset")
# The offsets are kept under the rendered file. A camera without one had
# no key, and 0.0 as a fallback put it at the start of the axis.


class Args(object):
    production = "Test"
    resolve = False
    lufs = -16.0
    intro = None
    outro = None


hand = os.path.join(WORK, "hand")
os.makedirs(hand)
wide = os.path.join(WORK, "W.mov")
guest = os.path.join(WORK, "G.mov")
for f in (wide, guest):
    open(f, "w").write("x")
rendered = os.path.join(WORK, "Wide.wav")
open(rendered, "w").write("x")

cameras = [{"name": "Wide", "video": wide}, {"name": "Guest", "video": guest}]
videos = [(wide, {"fps": 30.0, "width": 1920, "height": 1080,
                  "duration": 100.0, "tc": "10:00:00:00"}),
          (guest, {"fps": 30.0, "width": 1080, "height": 1920,
                   "duration": 100.0, "tc": "10:00:00:00"})]
# Wide has a render, Guest has none. Both were measured.
offsets = {rendered: -12.5, os.path.abspath(guest): -7.25}
out, said = spoken(vpm.write_handover, Args(), [], cameras, videos, hand,
                   0.0, (wide, videos[0][1]), [rendered], None, None,
                   0.0, None, None, offsets)
import json
written = json.load(io.open(os.path.join(hand, "Test_resolve.json"),
                            encoding="utf-8"))
by_camera = dict((c["camera"], c) for c in written["cameras"])
check("the camera with a render keeps its offset",
      by_camera["Wide"]["offset"] == -12.5,
      str(by_camera["Wide"]["offset"]))
check("the camera without one is found by its source",
      by_camera["Guest"]["offset"] == -7.25,
      str(by_camera["Guest"]["offset"]))
check("nothing to complain about", "offset" not in said.lower(),
      said.strip()[:60])

# And where nothing was measured for a camera, it is said out loud.
out, said = spoken(vpm.write_handover, Args(), [], cameras, videos, hand,
                   0.0, (wide, videos[0][1]), [rendered], None, None,
                   0.0, None, None, {rendered: -12.5})
check("an unmeasured camera is named", "Guest" in said, repr(said[:70]))

# A landscape and a portrait camera give a frame one of them has.
check("the handover frame is a real one",
      (written["width"], written["height"]) in ((1920, 1080), (1080, 1920)),
      "%sx%s" % (written["width"], written["height"]))

print("\n%s" % ("ALL OK" if not bad else "FAIL: " + ", ".join(bad)))
sys.exit(1 if bad else 0)
