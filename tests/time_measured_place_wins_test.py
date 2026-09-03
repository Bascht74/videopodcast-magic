# -*- coding: utf-8 -*-
"""A camera stands where it was measured; its clock is the last resort.

Not every camera shares a timecode, and a shared one is still a frame
or two out, so a clock is where a measurement starts and not what it
is replaced by. Only where nothing was measured does the clock answer,
and where that happens the run has to say so: a camera placed without
a measurement is one nobody checked.

The sections: the three steps camera_place goes through and the word
it hands back for each; which file of a row its clock is read from;
the same three steps once more through the handover, one camera
placed each way; the lines the run owes wherever a measurement was
missing; and a camera whose sound gives nothing, which the axis
places by its clock rather than stopping on.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import importlib.util, io, json, struct, subprocess, sys, tempfile, time
import contextlib
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
WORK = tempfile.mkdtemp(prefix="measuredplace_")
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


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


def stamped(path, seconds):
    """Write a file that carries *seconds* in a bext chunk."""
    body = (b"\0" * 338 + struct.pack("<Q", int(round(seconds * vpm.SR)))
            + b"\0" * 8)
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 4 + 8 + len(body)) + b"WAVE")
        f.write(b"bext" + struct.pack("<I", len(body)) + body)
    return path


def little_camera(name, stamp):
    """A second of picture at 25 fps, with a timecode track or without."""
    out = os.path.join(WORK, name)
    call = ["ffmpeg", "-v", "error", "-f", "lavfi",
            "-i", "testsrc=size=64x36:rate=25:duration=1",
            "-c:v", "libx264", "-preset", "ultrafast",
            "-pix_fmt", "yuv420p"]
    if stamp:
        call += ["-timecode", stamp]
    subprocess.run(call + [out, "-y"], check=True)
    return out


ZERO = 68100.0                                # 18:55:00:00, the wide shot
FOUR = 68104.0                                # four seconds later
# The alignment found this camera thirty-three seconds from the axis.
# Nowhere near its clock, and that is the point: where the two disagree
# only one of them can be the place, and the rule says which.
MEASURED = -33.34

print("The three steps, and the word each one hands back")
at_four = stamped(os.path.join(WORK, "four_seconds_in.wav"), FOUR)
plain = os.path.join(WORK, "no_clock.wav")
open(plain, "w").write("x")
midnight = stamped(os.path.join(WORK, "at_midnight.wav"), 0.0)

where, how = vpm.camera_place(at_four, ZERO, MEASURED, 30.0)
check("a measured camera stands where it was measured, not where its "
      "clock says", abs(where - MEASURED) < 1e-9,
      "placed at %r, wanted the measured %.2f and not the clock's %.1f"
      % (where, MEASURED, FOUR - ZERO))
check("and camera_place says the measurement is what placed it",
      how == "measured", "it says %r" % (how,))
# A measurement of 0.0 is a camera the alignment found exactly on the
# axis. Read as a truth value it counts as nothing measured, and the
# camera then jumps to wherever its clock happens to stand.
at_axis, how_axis = vpm.camera_place(at_four, ZERO, 0.0, 30.0)
check("a measurement of zero is a measurement, not a missing one",
      abs(at_axis) < 1e-9 and how_axis == "measured",
      "placed at %r by %r, wanted 0.0 by the measurement and not the "
      "clock's %.1f" % (at_axis, how_axis, FOUR - ZERO))
by_clock, how_clock = vpm.camera_place(at_four, ZERO, None, 30.0)
check("with nothing measured the clock answers",
      abs(by_clock - (FOUR - ZERO)) < 1e-9,
      "placed at %r, wanted the clock's %.1f" % (by_clock, FOUR - ZERO))
check("and camera_place says the clock is what was left",
      how_clock == "clock", "it says %r" % (how_clock,))
lost, how_lost = vpm.camera_place((plain, plain), ZERO, None, 30.0)
check("with no measurement and no clock the camera lands on the start "
      "of the axis", abs(lost) < 1e-9, "placed at %r, wanted 0.0" % (lost,))
check("and camera_place says nothing placed it", how_lost == "nowhere",
      "it says %r" % (how_lost,))
# No zero point means no axis to measure a clock against, so the clock
# is no answer here either -- and the word has to say that, or a camera
# at the start of the axis and a camera nobody could place read alike.
no_zero, how_no_zero = vpm.camera_place(at_four, None, None, 30.0)
check("no zero point, so the clock cannot answer either",
      abs(no_zero) < 1e-9 and how_no_zero == "nowhere",
      "placed at %r by %r, wanted 0.0 and nothing having placed it"
      % (no_zero, how_no_zero))

print("\nWhich file of a row the clock is read from")
# Every one of these is asked with nothing measured, because that is
# the only case in which a clock is read at all.
with_tc = little_camera("with_timecode.mov", "18:55:04:00")
blank = little_camera("without_timecode.mov", None)
twelve = little_camera("twelve_frames.mov", "18:55:04:12")
# An empty name reaches camera_place inside a row, never on its own:
# write_handover looks the rendered file up by camera name and puts ""
# there for a camera that has none. What this has to show is that the
# empty name is stepped over rather than ending the row.
no_render = vpm.camera_place(("", at_four), ZERO, None, 30.0)[0]
check("a camera with no render lands by its source's clock",
      abs(no_render - (FOUR - ZERO)) < 1e-9,
      "placed at %r, wanted the source's %.1f" % (no_render, FOUR - ZERO))
# Not every ffmpeg carries a timecode track through a render -- Windows
# with ffmpeg 9 does not -- so a row whose rendered file lost it has to
# fall through to the source rather than counting as having no clock.
fell_through = vpm.camera_place((blank, with_tc), 0.0, None, 25.0)[0]
check("a rendered file without one falls through to the source",
      abs(fell_through - FOUR) < 0.001,
      "read %r, wanted the source's %.1f" % (fell_through, FOUR))
# Which end of the row is read first shows only where both files carry
# a clock: with one of them blank, "the first", "the last", "the
# earliest" and "in name order" all answer the same. 18:55:04:00 at 25
# fps is 68104.0 s, and the twelve frames are 0.48 s on from it.
rendered_first = vpm.camera_place((with_tc, twelve), 0.0, None, 25.0)[0]
check("the rendered file's timecode wins, not the source's",
      abs(rendered_first - FOUR) < 0.001,
      "read %r, wanted the rendered file's %.1f" % (rendered_first, FOUR))
rendered_later = vpm.camera_place((twelve, with_tc), 0.0, None, 25.0)[0]
check("and it wins when it is the later of the two as well",
      abs(rendered_later - (FOUR + 0.48)) < 0.001,
      "read %r, wanted the rendered file's %.2f"
      % (rendered_later, FOUR + 0.48))
# One name on its own still works: a string is a row of characters, not
# a row of files, and taking it for one would ask after "w", "i", "t".
alone = vpm.camera_place(with_tc, 0.0, None, 25.0)[0]
check("one file may still be passed on its own",
      abs(alone - FOUR) < 0.001,
      "read %r, wanted the file's %.1f" % (alone, FOUR))
# A clock standing at 00:00:00:00 is a clock. Read as a truth value it
# counts as none, and the row goes on to the next file instead.
from_zero = vpm.camera_place((midnight, at_four), 12.0, None, 30.0)[0]
check("a timecode of zero is a timecode, not a missing one",
      abs(from_zero + 12.0) < 1e-9,
      "placed at %r, wanted 0.0 less the zero point 12.0 and not the "
      "next file in the row" % (from_zero,))

print("\nThe handover: one camera placed each way")
# Three cameras of one evening, one for each of the three steps.
# WideCam was measured and its clock disagrees, Presenter carries a
# clock and nothing was measured for it, Guest has neither.
NIGHT = [("WideCam", FOUR, MEASURED), ("Presenter", 68117.4, None),
         ("Guest", None, None)]
night = os.path.join(WORK, "night")
os.makedirs(night)
n_cameras, n_videos, n_results, n_offsets = [], [], [], {}
for name, tc, measured in NIGHT:
    src = os.path.join(WORK, name + "_source.mov")
    open(src, "w").write("x")
    rendered = os.path.join(WORK, name + ".wav")
    if tc is None:
        open(rendered, "w").write("x")
    else:
        stamped(rendered, tc)
    n_cameras.append({"name": name, "video": src})
    n_videos.append((src, {"fps": 30.0, "width": 1920, "height": 1080,
                           "duration": 300.0,
                           "tc": vpm.timecode_string(ZERO, 30.0)}))
    n_results.append(rendered)
    if measured is not None:
        n_offsets[os.path.abspath(rendered)] = measured

_out, said = spoken(vpm.write_handover, Args(), [], n_cameras, n_videos,
                    night, ZERO, (n_cameras[0]["video"], n_videos[0][1]),
                    n_results, None, None, 300.0, None, None, n_offsets)
written = json.load(io.open(os.path.join(night, "Test_resolve.json"),
                            encoding="utf-8"))
check("the zero point is written down as it was passed",
      written["start_s"] == ZERO,
      "%r against the %.1f it was handed" % (written["start_s"], ZERO))
placed = {cam["camera"]: cam["offset"] for cam in written["cameras"]}
by = {cam["camera"]: cam["placed_by"] for cam in written["cameras"]}
kept = {cam["camera"]: cam["sound_against_picture"]
        for cam in written["cameras"]}
check("the wide shot stands where the run measured it",
      abs(placed.get("WideCam", 1e9) - MEASURED) < 1e-4,
      "offset %r, wanted the measured %.2f and not its clock's %.1f"
      % (placed.get("WideCam"), MEASURED, FOUR - ZERO))
check("and the handover says the measurement placed it",
      by.get("WideCam") == "measured", "it says %r" % (by.get("WideCam"),))
check("the presenters' camera stands where its own clock says",
      abs(placed.get("Presenter", 1e9) - 17.4) < 1e-4,
      "offset %r, wanted its clock's 17.4" % (placed.get("Presenter"),))
check("and the handover says the clock placed it",
      by.get("Presenter") == "clock", "it says %r" % (by.get("Presenter"),))
check("the guest's camera lands on the start of the axis",
      placed.get("Guest") == 0.0,
      "offset %r, wanted 0.0" % (placed.get("Guest"),))
check("and the handover says nothing placed it",
      by.get("Guest") == "nowhere", "it says %r" % (by.get("Guest"),))
# A 0.0 here would be a lie nothing can read back out of the file: it
# looks exactly like a camera the alignment found on the axis.
check("where nothing was measured, nothing is claimed about the sound "
      "against the picture",
      kept.get("Presenter") is None and kept.get("Guest") is None,
      "the two unmeasured cameras carry %r and %r, wanted nothing"
      % (kept.get("Presenter"), kept.get("Guest")))

print("\nWhat the run says where a measurement was missing")
# The program's own lines, out of the catalogue: written out here they
# would tie the test to one language and one wording.
disagreed = vpm.T('  %s: the measurement puts it at %+.3f s, the '
                  'timecode at %+.3f s -- the measurement is used.') \
    % ("WideCam", MEASURED, FOUR - ZERO)
check("a measurement that disagrees with the clock is said out loud, "
      "with both numbers", disagreed in said,
      "wanted %r; printed: %s" % (disagreed, " ".join(said.split())[:70]))
clock_line = vpm.T('  Nothing was found in the sound for %s -- placed '
                   'by the timecode alone.') % "Presenter"
check("the camera placed by its clock alone is named", clock_line in said,
      "wanted %r; printed: %s" % (clock_line, " ".join(said.split())[:70]))
lost_line = vpm.T('  No measured offset for %s -- placed at the '
                  'start of the axis.') % "Guest"
check("the camera placed nowhere is named", lost_line in said,
      "wanted %r; printed: %s" % (lost_line, " ".join(said.split())[:70]))

print("\nAnd a run in which every camera was measured")
# Three measurements, none of them zero and none of them agreeing with
# a clock: with zeroes here a measurement that never arrived and one
# that did would write the same number.
ALL = {"WideCam": MEASURED, "Presenter": -60.11, "Guest": -7.25}
whole = os.path.join(WORK, "whole")
os.makedirs(whole)
w_offsets = {os.path.abspath(p): ALL[os.path.splitext(
    os.path.basename(p))[0]] for p in n_results}
_out, all_said = spoken(vpm.write_handover, Args(), [], n_cameras, n_videos,
                        whole, ZERO,
                        (n_cameras[0]["video"], n_videos[0][1]), n_results,
                        None, None, 300.0, None, None, w_offsets)
all_written = json.load(io.open(os.path.join(whole, "Test_resolve.json"),
                                encoding="utf-8"))
all_kept = {cam["camera"]: cam["sound_against_picture"]
            for cam in all_written["cameras"]}
check("the measurement is kept, under its own name", all_kept == ALL,
      "%s against the %s that was handed in" % (all_kept, ALL))
warned = vpm.T('  No measured offset for %s -- placed at the '
               'start of the axis.').split("%s")[0].strip()
check("no camera was left unmeasured", warned not in all_said,
      "wanted no %r; printed: %s"
      % (warned, " ".join(all_said.split())[:70]))
alone_line = vpm.T('  Nothing was found in the sound for %s -- placed '
                   'by the timecode alone.').split("%s")[0].strip()
check("and no camera is reported as placed by its clock",
      alone_line not in all_said,
      "wanted no %r; printed: %s"
      % (alone_line, " ".join(all_said.split())[:70]))


#------------- 5. A camera whose sound gives nothing does not stop the axis
print("\n5. A camera with nothing to measure is placed by its clock")

# video_envelope raises where a file gives nothing back, on purpose:
# caching a curve of silence would treat the file as unalignable until
# it next changes, saying nothing. Standing in for it here keeps this
# section off ffmpeg.
#
# The stand-in is not the softer one: it raises for the file the real
# one raises for, and hands back a real curve for the other. Nothing
# is measured against the broken camera either way -- there is no
# curve to measure.
BROKEN = os.path.join(WORK, "BrokenCam_01011856_C004.mov")
SOUND = os.path.join(WORK, "WideCam_01011855_C001.mov")
real_envelope = vpm.video_envelope


def envelope_of_the_one_that_speaks(path, *rest, **named):
    if os.path.basename(path).startswith("Broken"):
        raise ValueError("no audio data from %s" % os.path.basename(path))
    return vpm.np.zeros(24000)


vpm.video_envelope = envelope_of_the_one_that_speaks
try:
    try:
        answered, raised = vpm.envelope_heard(BROKEN), None
    except Exception as trouble:
        answered, raised = "never got there", trouble
    check("a file that gives nothing back answers instead of raising",
          raised is None and answered is None,
          "raised %r, answered %r" % (raised, answered))
    curve = vpm.envelope_heard(SOUND)
    check("and one that does give something hands its curve back",
          curve is not None and len(curve) == 24000,
          "%d points" % (0 if curve is None else len(curve)))

    # The broken one is the longer of the two, so the old reference
    # would have been the one there is nothing to measure against.
    facts_broken = {"duration": 120.0, "tc": "18:55:10:00", "fps": 25.0}
    facts_sound = {"duration": 60.0, "tc": "18:55:00:00", "fps": 25.0}
    videos = [(BROKEN, facts_broken), (SOUND, facts_sound)]
    ref_clip, position = vpm.align_cameras(videos)
    check("the reference is a camera there is something to measure "
          "against, not the longest",
          ref_clip[0] == SOUND, os.path.basename(ref_clip[0]))
    check("the camera with no sound is placed rather than left out",
          BROKEN in position, sorted(os.path.basename(p) for p in position))
    a, b, st = position.get(BROKEN, (None, None, {}))
    # 18:55:00:00 less 18:55:10:00: the reference clock less its own.
    check("and it stands where its clock says, ten seconds behind the "
          "reference", a == -10.0, "a = %r" % (a,))
    check("its verdict says the clock alone placed it",
          bool(st.get("by_clock_only")), repr(sorted(st)))

    # The same camera without a clock: nothing left to place it with.
    facts_no_clock = {"duration": 120.0, "fps": 25.0}
    _ref, place_no_clock = vpm.align_cameras(
        [(BROKEN, facts_no_clock), (SOUND, facts_sound)])
    check("with no sound and no clock it is refused, not laid down "
          "somewhere", BROKEN not in place_no_clock,
          sorted(os.path.basename(p) for p in place_no_clock))
finally:
    vpm.video_envelope = real_envelope

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
