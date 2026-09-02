# -*- coding: utf-8 -*-
"""A camera sits where its timecode says, not where the sound was measured.

The offset was once written from the alignment measurement instead of
the file's own timecode. On the reference camera the two agree, so it
read right while the others ran against the wrong picture. For every
camera: file_timecode(camera["file"]) - start_s == camera["offset"].
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, io, json, struct, subprocess, sys, tempfile, time
import contextlib
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
WORK = tempfile.mkdtemp(prefix="cameraplace_")
began = time.time()
done = 0
bad = []


def check(what, ok, detail=""):
    global done
    done += 1
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


class Args(object):
    production = "Test"
    resolve = False
    lufs = -16.0
    intro = None
    outro = None


print("Where a camera sits comes from its timecode, not from the sound")


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
# reference agrees, the other two carry the errors this guards against.
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
# Which cameras, not in which order: the cameras are named here and
# looked up by name, so re-ordering the handover leaves both of these
# judgements alone. Whether that order is part of the contract is a
# question of its own, and no judgement here answers it.
wrong = sorted(cam["camera"] for cam in written["cameras"]
               if abs(cam["offset"] - cam["sound_against_picture"]) > a_frame)
check("the reference alone would have shown nothing",
      wrong == ["Guest", "Hosts"], str(wrong))
kept = {cam["camera"]: cam["sound_against_picture"]
        for cam in written["cameras"]}
check("the measurement is kept, under its own name",
      kept == {"Wide": 0.0, "Hosts": -33.34, "Guest": -60.11}, str(kept))
# What says a camera was left unmeasured is the program's own warning,
# taken from the catalogue. Looking for the word "offset" anywhere in
# what was printed made any other line carrying it a failure, and it
# said nothing at all wherever the run is not in English.
warned = vpm.T('  No measured offset for %s -- placed at the '
               'start of the axis.').split("%s")[0].strip()
check("no camera was left unmeasured", warned not in said,
      "wanted no %r; printed: %s" % (warned, " ".join(said.split())[:70]))

# camera_place is the one place that answers this, so it is asked
# directly too, including the fallback a file without a timecode takes.
check("a stamped file: the timecode, not the measurement",
      vpm.camera_place(n_results[1], ZERO, -33.34, 30.0) == 4.0,
      str(vpm.camera_place(n_results[1], ZERO, -33.34, 30.0)))
plain = os.path.join(WORK, "no_timecode.wav")
open(plain, "w").write("x")
no_stamp = vpm.camera_place(plain, ZERO, -7.25, 30.0)
check("a file without a timecode keeps the measurement", no_stamp == -7.25,
      "got %r, wanted the measurement %r" % (no_stamp, -7.25))
no_zero = vpm.camera_place(n_results[1], None, -7.25, 30.0)
check("no zero point, so the measurement again", no_zero == -7.25,
      "got %r, wanted the measurement %r" % (no_zero, -7.25))
# An empty name reaches camera_place inside a row, never on its own:
# write_handover looks the rendered file up by camera name, puts "" there
# for a camera that has none, and hands over the pair ("", source).
# Asked with the empty name alone the answer is the same whether the
# guard on it stands or falls -- a name that is no file has no timecode
# either -- so the row is what is asked here, and what it has to show is
# that the empty name is stepped over rather than ending the row.
no_render = vpm.camera_place(("", n_results[1]), ZERO, -7.25, 30.0)
check("a camera with no render lands by its source's clock",
      no_render == 4.0,
      "got %r, wanted the source's 4.0 s and not the measurement %r"
      % (no_render, -7.25))
# A timecode of 00:00:00:00 is a timecode. Read as a truth value rather
# than as "there is one" it counts as none, and the camera drops back on
# the sound measurement instead of landing on the zero point.
midnight = stamped(os.path.join(WORK, "at_midnight.wav"), 0.0)
from_zero = vpm.camera_place((midnight, plain), 12.0, -7.25, 30.0)
check("a timecode of zero is a timecode, not a missing one",
      from_zero == -12.0,
      "got %r, wanted 0.0 minus the zero point 12.0, not the "
      "measurement -7.25" % (from_zero,))

# The frames of a timecode are frames, so the rate decides what they
# are worth. Through ffprobe, where a camera's timecode track comes
# from. The file asked about is one that is really there and carries no
# timecode of its own: what the program makes of a name that is no file
# is a question of its own, and hanging these two on it made every
# guard against a missing path a failure here.
real_probe = vpm.ffprobe_json
vpm.ffprobe_json = lambda path: {
    "format": {"tags": {"timecode": "18:55:00:12"}}, "streams": []}
try:
    at30 = vpm.camera_place(plain, ZERO, -99.0, 30.0)
    at25 = vpm.camera_place(plain, ZERO, -99.0, 25.0)
finally:
    vpm.ffprobe_json = real_probe
check("12 frames at 30 fps are 0.400 s", abs(at30 - 0.4) < 1e-6, str(at30))
check("the same 12 frames at 25 fps are 0.480 s", abs(at25 - 0.48) < 1e-6,
      str(at25))

# A camera's place was read off the rendered file alone, and not every
# ffmpeg carries a timecode track through a render. Where the read came
# back empty the place fell back to the measured shift without a word.
# Checked by handing camera_place a file that carries no timecode.
print("\nWhere the timecode is read")


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


with_tc = little_camera("with_timecode.mov", "18:55:04:00")
blank = little_camera("without_timecode.mov", None)
zero = vpm.file_timecode(with_tc, 25.0)
check("the built file carries a timecode", zero is not None, str(zero))
check("and the one built without one carries none",
      vpm.file_timecode(blank, 25.0) is None,
      str(vpm.file_timecode(blank, 25.0)))
# A number nobody could mistake for a timecode: where it turns up in an
# answer, the fall-back was taken.
WRONG = -99.5
check("a rendered file without one falls through to the source",
      abs(vpm.camera_place((blank, with_tc), 0.0, WRONG, 25.0) - zero)
      < 0.001, str(vpm.camera_place((blank, with_tc), 0.0, WRONG, 25.0)))
# Which end of the row is read first shows only where both files carry
# a timecode: with one of them blank, "the first one", "the last one",
# "the earliest" and "in name order" all answer the same. 18:55:04:00 at
# 25 fps is 68104.0 s, and the twelve frames below are 0.48 s on from it.
twelve = little_camera("twelve_frames.mov", "18:55:04:12")
rendered_first = vpm.camera_place((with_tc, twelve), 0.0, WRONG, 25.0)
check("the rendered file's timecode wins, not the source's",
      abs(rendered_first - 68104.0) < 0.001,
      "got %r, wanted the rendered file's 68104.0" % (rendered_first,))
rendered_later = vpm.camera_place((twelve, with_tc), 0.0, WRONG, 25.0)
check("and it wins when it is the later of the two as well",
      abs(rendered_later - 68104.48) < 0.001,
      "got %r, wanted the rendered file's 68104.48" % (rendered_later,))
check("and with no timecode anywhere the measurement is kept",
      abs(vpm.camera_place((blank, blank), 0.0, WRONG, 25.0) - WRONG)
      < 0.001, str(vpm.camera_place((blank, blank), 0.0, WRONG, 25.0)))
# One name on its own still works: a string is a row of characters, not
# a row of files, and taking it for one would ask after "W", "i", "t".
check("one file may still be passed on its own",
      abs(vpm.camera_place(with_tc, 0.0, WRONG, 25.0) - zero) < 0.001,
      str(vpm.camera_place(with_tc, 0.0, WRONG, 25.0)))
# The rate is the material's own here, and a wrong one would show only
# in the frames: twelve of them are 0.48 s at 25 and 0.40 s at 30.
check("the frames of a timecode are read at the file's rate",
      abs(vpm.file_timecode(twelve) - vpm.file_timecode(with_tc) - 0.48)
      < 0.001, str(vpm.file_timecode(twelve)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
