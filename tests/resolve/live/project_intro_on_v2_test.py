# -*- coding: utf-8 -*-
"""The intro lies alone on V2 and A2 at the frame it names, the cut behind it.

Against a DaVinci Resolve that is really running. First a cut timeline
with an intro: Resolve refused no track on the way, the intro's picture
lies alone on V2 and whole, its sound alone on A2, both where the timeline
starts, and the cut has moved back by as far as the intro speaks past the
first word. Then the same cut without an intro, as the counter-check:
nothing on V2 or A2, and the cut starting at the In point.

The material is the shared interview fixture, read and never written; the
intro is eight seconds cut out of its wide shot into a temporary folder of
the test's own. Where its sound stops is written into the handover by
hand rather than measured, so the placement below depends on nothing but
the program. The frame numbers are written out rather than computed, so
that a wrong sum in the program cannot be repeated by the test.

A step that throws is a failed judgement and not a traceback, so the
closing count is reached whatever happens.
"""
import os
import shutil
import subprocess
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


def on_track(tl, kind, i):
    """What lies on one track, as (name, first frame, length)."""
    return [(x.GetName(), x.GetStart(), x.GetDuration())
            for x in (tl.GetItemListInTrack(kind, i) or [])]


vpm = ground_of.program()
resolve = ground_of.a_resolve(vpm)
print("Resolve: %s %s" % (resolve.GetProductName(), resolve.GetVersionString()))

folder = ground_of.fixture("interview")
if not os.path.isdir(folder):
    ground_of.leave_out("no interview fixture at %s -- run 'cd tests && "
                        "bash fixtures.sh' to build it" % folder)
camera_file = ground_of.cameras_of(folder)
if len(camera_file) < 3:
    ground_of.leave_out("the interview fixture holds %d camera files, 3 are "
                        "needed -- run 'cd tests && bash fixtures.sh force'"
                        % len(camera_file))
ffmpeg = shutil.which("ffmpeg")
if not ffmpeg:
    ground_of.leave_out("ffmpeg is not on the search path, and the intro is "
                        "cut out of the fixture with it -- brew install ffmpeg")

# The intro: 200 frames of the wide shot, picture and sound, cut before
# anything is made in Resolve -- material that could not be made is a
# reason to stand aside, and standing aside must happen while there is
# still nothing to put back.
work = tempfile.mkdtemp(prefix="vpm_intro_")
intro = os.path.join(work, "Intro_Jingle.mov")
made = subprocess.run(
    [ffmpeg, "-v", "error", "-ss", "10", "-i", camera_file[-1],
     "-frames:v", "200", "-t", "8", "-r", "25",
     "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-y", intro], capture_output=True, text=True)
if made.returncode != 0 or not os.path.isfile(intro):
    shutil.rmtree(work, ignore_errors=True)
    ground_of.leave_out("ffmpeg could not cut the intro out of %s (ended "
                        "with %d: %s) -- run 'cd tests && bash fixtures.sh "
                        "force'" % (os.path.basename(camera_file[-1]),
                                    made.returncode,
                                    made.stderr.strip()[-80:]))
INTRO_NAME = os.path.basename(intro)

# 25 frames a second, and 01:00:10:00 is frame 90250 on the timecode
# clock -- the same ground project_clips_land_right stands on.
FPS = 25.0
START = "01:00:10:00"
ORIGIN = 90250
cameras = [
    {"camera": "Wide", "track": "Wide", "wide": True,
     "file": camera_file[0], "source": camera_file[0],
     "offset": -4.0, "duration": 120.0, "audio_tracks": ["Full-Mix"]},
    {"camera": "Guest", "track": "Guest",
     "file": camera_file[1], "source": camera_file[1],
     "offset": -2.0, "duration": 120.0, "audio_tracks": ["Guest"]},
    {"camera": "Hosts", "track": "Hosts",
     "file": camera_file[2], "source": camera_file[2],
     "offset": 0.0, "duration": 120.0, "audio_tracks": ["Hosts"]},
]
CUT = [{"camera": "Wide", "start": 0.0, "end": 4.0},
       {"camera": "Guest", "start": 4.0, "end": 8.0},
       {"camera": "Hosts", "start": 8.0, "end": 12.0}]
# The first word falls 2 s in, and the intro's sound stops 6 s into it.
# So the intro starts with the timeline, and the cut moves back by 6 - 2 =
# 4 s = 100 frames: its first shot at 90350 instead of 90250.
INTRO = {"source": intro, "duration": 8.0, "has_audio": True,
         "audio_from": 0.0, "audio_to": 6.0}
INTRO_AT = 90250
INTRO_LONG = 200
CUT_FIRST_WITH = 90350
CUT_FIRST_WITHOUT = 90250


def handover(with_intro):
    """The handover as the run writes it, with or without the intro."""
    d = {"fps": FPS, "fps_measured": FPS, "drop_frame": False,
         "width": 1280, "height": 720, "start_tc": START, "in_point": START,
         "speakers": [{"name": "Guest", "sections": [[2.0, 11.0]]}],
         "cameras": cameras, "cut": CUT, "length_s": 120.0,
         "_refused": []}
    if with_intro:
        d["intro"] = dict(INTRO)
    return d


def cut_timeline(mp, name, d, clips):
    """Build the cut timeline the way build_resolve_project does."""
    tl = vpm.create_timeline(mp, name)
    fps, origin = vpm.timeline_origin(d)
    lead_in = vpm.lead_in_offset(mp, tl, d, clips, fps, origin)
    vpm.build_cut_timeline(mp, tl, CUT, cameras, clips, d, None, lead_in)
    vpm.insert_intro_and_outro(mp, tl, d, clips, fps, origin, lead_in)
    return tl


ground = ground_of.OwnProject(vpm, resolve, "intro")
try:
    p = ground.open()
    d = handover(True)
    vpm.apply_project_settings(p, d)
    mp = p.GetMediaPool()
    clips = vpm.import_media(mp, [cam["file"] for cam in cameras] + [intro])

    print("\n1. With an intro: it lies on V2 and A2, the cut behind it")
    tl = cut_timeline(mp, "%s Intro" % ground.name, d, clips)
    # First, or every line below would say the intro is missing while
    # Resolve simply had no track to put it on.
    check("Resolve refused no track the intro needs",
          not d["_refused"] and tl.GetTrackCount("video") >= 2,
          "%d video tracks, %d audio tracks, refused: %s"
          % (tl.GetTrackCount("video"), tl.GetTrackCount("audio"),
             d["_refused"] or "nothing"))
    lies = on_track(tl, "video", 2)
    check("the intro lies alone on V2",
          len(lies) == 1 and lies[0][0] == INTRO_NAME,
          "V2 holds %s, expected one %r" % ([x[0] for x in lies], INTRO_NAME))
    check("the intro starts where the timeline starts",
          len(lies) == 1 and lies[0][1] == INTRO_AT,
          "V2 starts at %s, the first word 2 s in less 6 s of intro sound "
          "puts it at %d" % (lies[0][1] if lies else None, INTRO_AT))
    check("the intro goes on whole, not as a piece",
          len(lies) == 1 and lies[0][2] == INTRO_LONG,
          "V2 is %s frames long, the intro is %d"
          % (lies[0][2] if lies else None, INTRO_LONG))
    sound = on_track(tl, "audio", 2)
    check("the intro's sound lies alone on A2",
          len(sound) == 1 and sound[0][0] == INTRO_NAME,
          "A2 holds %s, expected one %r"
          % ([x[0] for x in sound], INTRO_NAME))
    check("and it starts with the intro's picture",
          len(sound) == 1 and sound[0][1] == INTRO_AT,
          "A2 starts at %s, V2 at %d" % (sound[0][1] if sound else None,
                                         INTRO_AT))
    shots = on_track(tl, "video", 1)
    check("the cut moves back by as far as the intro speaks",
          bool(shots) and shots[0][1] == CUT_FIRST_WITH,
          "the first shot starts at %s, 4 s after %d is %d"
          % (shots[0][1] if shots else None, ORIGIN, CUT_FIRST_WITH))

    print("\n2. Without an intro: nothing on V2 or A2, the cut at the In point")
    plain = handover(False)
    tl0 = cut_timeline(mp, "%s Plain" % ground.name, plain, clips)
    check("without an intro nothing lies on V2",
          not on_track(tl0, "video", 2),
          "V2 holds %s, of %d video tracks"
          % ([x[0] for x in on_track(tl0, "video", 2)],
             tl0.GetTrackCount("video")))
    check("nor on A2",
          not on_track(tl0, "audio", 2),
          "A2 holds %s, of %d audio tracks"
          % ([x[0] for x in on_track(tl0, "audio", 2)],
             tl0.GetTrackCount("audio")))
    shots = on_track(tl0, "video", 1)
    check("without an intro the cut starts at the In point",
          bool(shots) and shots[0][1] == CUT_FIRST_WITHOUT,
          "the first shot starts at %s, the In point is %d"
          % (shots[0][1] if shots else None, CUT_FIRST_WITHOUT))
except Exception as e:
    import traceback
    traceback.print_exc()
    check("the run reached the end without an exception", False,
          "%s: %s" % (type(e).__name__, str(e).replace("\n", " ")[:120]))
finally:
    left_over = ground.close()
    shutil.rmtree(work, ignore_errors=True)

check("the project the test made is gone again", not left_over,
      left_over or "%r no longer in the project list" % ground.name)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
