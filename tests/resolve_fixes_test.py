# -*- coding: utf-8 -*-
"""Defects of the Resolve part, each with the check that would have caught it.

Blocks 1 to 5 come from a review; blocks 6 to 8 from the night of
26 August 2026, when eight faults went in at once and rode through the
whole suite. Two of them were one sentence: the offset of a camera is
its timecode minus the zero point, and it holds for every camera, not
only for the reference -- there the wrong number and the right one are
the same number.

Each block says what went wrong before, because that is what the check
is guarding. What needs a running Resolve is not here: those three are
marked in the handover note and belong to a real run.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, io, sys, tempfile, subprocess
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


print("\n6. Where a camera sits comes from its timecode, not from the sound")
# The night of 26 August: the offset was written from the alignment
# measurement instead of from the file's own timecode. On the reference
# camera the two agree to the millisecond, so it read right -- the other
# two were 37.34 s and 77.51 s out, and the sound ran against the wrong
# picture. What the handover file promises is one sentence:
#
#     "Position in the file is programme time minus offset."
#
# So for every camera, and not for the reference alone:
#
#     file_timecode(camera["file"]) - d["start_s"] == camera["offset"]
import struct


def stamped(path, seconds):
    """Write a file that carries *seconds* as its own start time.

    A bext chunk, which is where file_timecode looks first -- so this
    costs no ffprobe and no camera.
    """
    body = (b"\0" * 338 + struct.pack("<Q", int(round(seconds * vpm.SR)))
            + b"\0" * 8)
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 4 + 8 + len(body)) + b"WAVE")
        f.write(b"bext" + struct.pack("<I", len(body)) + body)
    return path


ZERO = 68100.0                                   # 18:55:00:00, the wide shot
# Per camera: its timecode, and what the alignment measured. The
# reference agrees to the millisecond; the other two carry exactly the
# two errors of that night.
NIGHT = [("Wide", 68100.0, 0.0),
         ("Hosts", 68104.0, 4.0 - 37.34),
         ("Guest", 68117.4, 17.4 - 77.51)]

night = os.path.join(WORK, "night")
os.makedirs(night)
n_cameras, n_videos, n_results, n_offsets = [], [], [], {}
for name, tc, measured in NIGHT:
    src = os.path.join(WORK, name + "_source.mov")
    open(src, "w").write("x")
    rendered = stamped(os.path.join(WORK, name + ".wav"), tc)
    n_cameras.append({"name": name, "video": src})
    n_videos.append((src, {"fps": 30.0, "width": 1920, "height": 1080,
                           "duration": 300.0,
                           "tc": vpm.timecode_string(tc, 30.0)}))
    n_results.append(rendered)
    n_offsets[os.path.abspath(rendered)] = measured

_out, said = spoken(vpm.write_handover, Args(), [], n_cameras, n_videos,
                    night, ZERO, (n_cameras[0]["video"], n_videos[0][1]),
                    n_results, None, None, 300.0, None, None, n_offsets)
written = json.load(io.open(os.path.join(night, "Test_resolve.json"),
                            encoding="utf-8"))
check("the zero point is written down as it was passed",
      written["start_s"] == ZERO, str(written["start_s"]))
a_frame = 1.0 / max(1.0, float(written["fps_measured"]))
for cam in written["cameras"]:
    stamp = vpm.file_timecode(cam["file"])
    check("%s: timecode minus zero point is the offset" % cam["camera"],
          stamp is not None
          and abs((stamp - written["start_s"]) - cam["offset"]) <= a_frame,
          "%s - %s != %s" % (stamp, written["start_s"], cam["offset"]))
# Why one camera is not enough: on the reference the wrong number and
# the right one are the same number.
wrong = [cam["camera"] for cam in written["cameras"]
         if abs(cam["offset"] - cam["sound_against_picture"]) > a_frame]
check("the reference alone would have shown nothing",
      wrong == ["Hosts", "Guest"], str(wrong))
check("the measurement is kept, under its own name",
      [cam["sound_against_picture"] for cam in written["cameras"]]
      == [0.0, -33.34, -60.11],
      str([cam["sound_against_picture"] for cam in written["cameras"]]))
check("no camera was left unmeasured", "offset" not in said.lower(),
      said.strip()[:60])

# camera_place is the one place that answers this, so it is asked
# directly too -- including the fallback, which is what a file without a
# timecode is allowed to do.
check("a stamped file: the timecode, not the measurement",
      vpm.camera_place(n_results[1], ZERO, -33.34, 30.0) == 4.0,
      str(vpm.camera_place(n_results[1], ZERO, -33.34, 30.0)))
plain = os.path.join(WORK, "no_timecode.wav")
open(plain, "w").write("x")
check("a file without a timecode keeps the measurement",
      vpm.camera_place(plain, ZERO, -7.25, 30.0) == -7.25)
check("no zero point, so the measurement again",
      vpm.camera_place(n_results[1], None, -7.25, 30.0) == -7.25)
check("no file at all, likewise",
      vpm.camera_place("", ZERO, -7.25, 30.0) == -7.25)

# The frames of a timecode are frames, so the rate decides what they are
# worth. Read through ffprobe, because that is where a camera's timecode
# track comes from.
real_probe = vpm.ffprobe_json
vpm.ffprobe_json = lambda path: {
    "format": {"tags": {"timecode": "18:55:00:12"}}, "streams": []}
try:
    at30 = vpm.camera_place("/nowhere/Cam.mov", ZERO, -99.0, 30.0)
    at25 = vpm.camera_place("/nowhere/Cam.mov", ZERO, -99.0, 25.0)
finally:
    vpm.ffprobe_json = real_probe
check("12 frames at 30 fps are 0.400 s", abs(at30 - 0.4) < 1e-6, str(at30))
check("the same 12 frames at 25 fps are 0.480 s", abs(at25 - 0.48) < 1e-6,
      str(at25))


print("\n7. The preview and the Resolve build read the same number")
# Both take the offset out of this one file: the player through
# camera_offset, the Resolve build by putting cam["offset"] straight into
# recordFrame. In the night they came apart by those same 37.34 s -- and
# only away from the reference camera, where nobody looks first.
for_player, said = spoken(vpm.camera_offset, written["cameras"],
                          written["start_s"], written["fps_measured"])
for_resolve = dict((cam["track"], cam["offset"])
                   for cam in written["cameras"])
check("both know the same tracks",
      sorted(for_player) == sorted(for_resolve),
      "%s / %s" % (sorted(for_player), sorted(for_resolve)))
for track in sorted(for_resolve):
    check("%s: player and Resolve agree" % track,
          abs(for_player[track] - for_resolve[track]) <= a_frame,
          "%.4f against %.4f" % (for_player[track], for_resolve[track]))
check("and there was nothing to put right", not said.strip(),
      said.strip()[:70])

# A file that does carry the night's numbers -- an old handover, or one
# edited by hand. The timecode keeps the precedence, and both numbers go
# into the log rather than one of them being dropped in silence.
poisoned = [dict(cam, offset=cam["sound_against_picture"])
            for cam in written["cameras"]]
after, said = spoken(vpm.camera_offset, poisoned, written["start_s"],
                     written["fps_measured"])
check("the timecode wins over a stored measurement",
      all(abs(after[t] - for_resolve[t]) <= a_frame for t in for_resolve),
      str(after))
check("and both numbers are said out loud",
      "+4.000" in said and "-33.340" in said, repr(said[:90]))


print("\n8. A handover without a window builds the cut list again")
# In the night the button returned at once and left the cut of the last
# run standing: 81 shots where the turned setting gives 47. What tripped
# it was a test that held the In point against start_s -- but start_s is
# the zero of the axis, the earliest camera, and it is earlier than any
# In point anybody sets, so every window was refused. A handover without
# a window is the normal case: every run without --in-point writes one.
speaker_a, speaker_b, at = [], [], 0.0
while at < 300.0:
    speaker_a.append([round(at, 3), round(at + 5.0, 3)])
    speaker_b.append([round(at + 5.0, 3), round(at + 10.0, 3)])
    at += 10.0
STALE = [{"start": 0.0, "end": 300.0, "camera": "Wide"}]
cut_folder = os.path.join(WORK, "cut")
os.makedirs(cut_folder)
for who in ("Wide", "A", "B"):
    open(os.path.join(cut_folder, who + ".mov"), "w").write("x")


def a_handover(window=None):
    """A handover file as a run writes it -- by default without a window."""
    cams = []
    for who, speaks in (("Wide", []), ("A", ["A"]), ("B", ["B"])):
        path = os.path.join(cut_folder, who + ".mov")
        cams.append({"camera": who, "source": path, "file": path,
                     "track": who, "speakers": speaks, "offset": 0.0})
    return {"production": "Test", "start_s": ZERO, "fps": 30,
            "fps_measured": 30.0, "start_tc": "18:55:00:00",
            "length_s": 300.0,
            "in_point": (window or (None, None))[0],
            "out_point": (window or (None, None))[1],
            "speakers": [{"name": "A", "sections": speaker_a},
                         {"name": "B", "sections": speaker_b}],
            "cameras": cams, "cut": list(STALE)}


def refreshed(call, window=None):
    """Put the settings in the project file and press the button."""
    with open(os.path.join(cut_folder, "videopodcast-magic_Test.json"),
              "w", encoding="utf-8") as f:
        json.dump({"production": "Test", "call": call}, f)
    d = a_handover(window)
    path = os.path.join(cut_folder, "Test_resolve.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f)
    kept, sys.argv[1:] = sys.argv[1:], []
    try:
        reason, _said = spoken(vpm.refresh_cut_list, d, path)
    finally:
        sys.argv[1:] = kept
    return reason, d.get("cut") or []


short, short_cut = refreshed(["--min-edit-duration", "3"])
check("without a window it does not refuse", short is None, str(short))
check("and the cut of the last run is gone", short_cut != STALE,
      str(short_cut[:2]))
long_r, long_cut = refreshed(["--min-edit-duration", "12"])
check("the turned setting does not refuse either", long_r is None,
      str(long_r))
check("and it really builds again: another number of shots",
      len(long_cut) != len(short_cut),
      "%d and %d" % (len(long_cut), len(short_cut)))
# The In point of the interface against a handover that has none: this
# is the pair that was refused.
with_in, in_cut = refreshed(["--in-point", "18:55:30:00",
                             "--min-edit-duration", "12"])
check("an In point beside a handover without one does not refuse",
      with_in is None, str(with_in))
check("and gives the same cut as without it", in_cut == long_cut,
      "%d against %d" % (len(in_cut), len(long_cut)))
# And what may still be refused, so that the repair did not take the
# guard with it: the window really did move since the files were made.
moved, _c = refreshed(["--in-point", "19:00:00:00",
                       "--min-edit-duration", "12"],
                      window=("18:55:30:00", "18:59:00:00"))
check("a window that really moved is still refused", bool(moved),
      str(moved))

# ----------------------------------------------------------------------
# Where the timecode is read, when the rendered file has none
#
# A camera's place in the handover is its own timecode minus the zero of
# the axis, and it was read off the rendered file alone. Not every
# ffmpeg carries a timecode track through a render: Windows with
# ffmpeg 9 does not, macOS with the same 9 and Ubuntu with 6 do. So on
# one system in three the read came back empty and the place fell back
# to the measured shift -- without a word, and the cameras stood where
# the measurement saw them instead of where their own clocks say they
# are. That is the fault the first section of this file is about,
# returning through a back door on a system nobody here can run.
#
# Checked without Windows by handing camera_place a file that carries no
# timecode, which is exactly what Windows hands it.
print("\n8. Where the timecode is read")


def little_camera(name, stamp):
    """A second of picture, with a timecode or without one."""
    out = os.path.join(WORK, name)
    call = ["ffmpeg", "-v", "error", "-f", "lavfi",
            "-i", "testsrc=size=64x36:rate=25:duration=1",
            "-c:v", "libx264", "-preset", "ultrafast",
            "-pix_fmt", "yuv420p"]
    if stamp:
        call += ["-timecode", stamp]
    subprocess.run(call + [out, "-y"], check=True)
    return out


stamped = little_camera("with_timecode.mov", "18:55:04:00")
blank = little_camera("without_timecode.mov", None)
zero = vpm.file_timecode(stamped, 25.0)
check("the built file carries a timecode", zero is not None, str(zero))
check("and the one built without one carries none",
      vpm.file_timecode(blank, 25.0) is None,
      str(vpm.file_timecode(blank, 25.0)))
# A number nobody could mistake for a timecode: where it turns up in an
# answer, the fall-back was taken.
WRONG = -99.5
check("a rendered file without one falls through to the source",
      abs(vpm.camera_place((blank, stamped), 0.0, WRONG, 25.0) - zero)
      < 0.001, str(vpm.camera_place((blank, stamped), 0.0, WRONG, 25.0)))
check("the rendered file still wins where it has one",
      abs(vpm.camera_place((stamped, blank), 0.0, WRONG, 25.0) - zero)
      < 0.001, str(vpm.camera_place((stamped, blank), 0.0, WRONG, 25.0)))
check("and with no timecode anywhere the measurement is kept",
      abs(vpm.camera_place((blank, blank), 0.0, WRONG, 25.0) - WRONG)
      < 0.001, str(vpm.camera_place((blank, blank), 0.0, WRONG, 25.0)))
# One name on its own still works: a string is a row of characters, not
# a row of files, and taking it for one would ask after "W", "i", "t".
check("one file may still be passed on its own",
      abs(vpm.camera_place(stamped, 0.0, WRONG, 25.0) - zero) < 0.001,
      str(vpm.camera_place(stamped, 0.0, WRONG, 25.0)))
# The rate is the material's own here, and a wrong one would show: at
# 30 the four seconds of 18:55:04:00 stay four, so the frames have to
# carry it -- 18:55:04:12 at 25 is 0.48 s, at 30 it is 0.40 s.
twelve = little_camera("twelve_frames.mov", "18:55:04:12")
check("the frames of a timecode are read at the file's rate",
      abs(vpm.file_timecode(twelve) - vpm.file_timecode(stamped) - 0.48)
      < 0.001, str(vpm.file_timecode(twelve)))


print("\n%s" % ("ALL OK" if not bad else "FAIL: " + ", ".join(bad)))
sys.exit(1 if bad else 0)
