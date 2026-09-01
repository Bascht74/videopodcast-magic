# -*- coding: utf-8 -*-
"""Every camera and every shot lands on the track and frame the cut names.

Against a DaVinci Resolve that is really running. First the ground: a clip
asked onto a track that was never made is not on it, which is why
everything below is read back off the timeline instead of taken from what
the interface answered. Then the camera timeline -- one video track per
camera, none left empty, each camera at the frame its offset says, the
tracks named after the speakers. Then the cut timeline -- one track, every
shot of the cut list on it, at the frame and the length the list names.

The material is the shared interview fixture, read and never written. The
frame numbers below are written out rather than computed, so that a wrong
sum in the program cannot be repeated by the test.

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

# 25 frames a second is what the fixture material carries, and
# 01:00:10:00 is 3610 s -- frame 90250 on the timecode clock. Every frame
# number further down is measured from there.
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
NAME_OF = [os.path.basename(cam["file"]) for cam in cameras]
# The earliest camera started 4 s before the In point, so the timeline
# begins 100 frames earlier than 90250. Each camera then sits at its own
# offset: -4 s, -2 s, 0 s.
CAMERA_START = 90150
CAMERA_AT = [90150, 90200, 90250]
# The whole 120 s file goes on, at 25 frames a second.
WHOLE = 3000
CUT = [{"camera": "Wide", "start": 0.0, "end": 4.0},
       {"camera": "Guest", "start": 4.0, "end": 8.0},
       {"camera": "Hosts", "start": 8.0, "end": 12.0}]
# The cut starts at the In point, so at 90250, and each shot is 4 s = 100
# frames long.
CUT_AT = [90250, 90350, 90450]
CUT_LONG = [100, 100, 100]
d = {"fps": FPS, "fps_measured": FPS, "drop_frame": False,
     "width": 1280, "height": 720, "start_tc": START, "in_point": START,
     "speakers": [], "cameras": cameras, "cut": CUT}

ground = ground_of.OwnProject(vpm, resolve, "clips")
try:
    p = ground.open()
    vpm.apply_project_settings(p, d)
    mp = p.GetMediaPool()
    clips = vpm.import_media(mp, [cam["file"] for cam in cameras])

    print("\n1. The ground: a track that was never made holds nothing")
    empty = vpm.create_timeline(mp, "asked for too much")
    had = empty.GetTrackCount("video")
    said = mp.AppendToTimeline([{"mediaPoolItem": clips[cameras[0]["file"]],
                                 "trackIndex": 7, "recordFrame": ORIGIN,
                                 "startFrame": 0, "endFrame": 25,
                                 "mediaType": 1}])
    check("a clip asked onto a track that was never made is not on it",
          not (empty.GetItemListInTrack("video", 7) or []),
          "V7 of a %d-track timeline holds %s"
          % (had, empty.GetItemListInTrack("video", 7)))
    check("and no such track appeared because it was asked for",
          empty.GetTrackCount("video") == had,
          "%d video tracks, %d before the ask"
          % (empty.GetTrackCount("video"), had))
    check("so what the interface answers is no evidence on its own",
          bool(said),
          "Resolve answered %r to an insert onto a track that is not there"
          % bool(said))

    print("\n2. The camera timeline: one track per camera")
    tl = vpm.create_timeline(mp, "%s Cameras" % ground.name)
    vpm.build_camera_timeline(mp, tl, cameras, clips, d)
    check("one video track per camera, and no more",
          tl.GetTrackCount("video") == 3,
          "%d video tracks for 3 cameras" % tl.GetTrackCount("video"))
    check("one audio track per camera is left when it is tidied",
          tl.GetTrackCount("audio") == 3,
          "%d audio tracks for 3 cameras" % tl.GetTrackCount("audio"))
    bare = [i for i in range(1, tl.GetTrackCount("video") + 1)
            if not on_track(tl, "video", i)]
    check("no video track is left empty",
          not bare, "empty video tracks: %s of %d"
          % (bare, tl.GetTrackCount("video")))
    bare = [i for i in range(1, tl.GetTrackCount("audio") + 1)
            if not on_track(tl, "audio", i)]
    check("no audio track is left empty",
          not bare, "empty audio tracks: %s of %d"
          % (bare, tl.GetTrackCount("audio")))
    check("the timeline begins where the earliest camera does",
          tl.GetStartFrame() == CAMERA_START,
          "begins at frame %d, the earliest camera at %d"
          % (tl.GetStartFrame(), CAMERA_START))
    for i, cam in enumerate(cameras, 1):
        # The speaker's name out of the dictionary first: a subscript
        # inside a check's own wording puts its key into the register
        # alongside the sentence.
        who, moved = cam["track"], cam["offset"]
        lies = on_track(tl, "video", i)
        check("%s alone on V%d, and it is its own file" % (who, i),
              len(lies) == 1 and lies[0][0] == NAME_OF[i - 1],
              "V%d holds %s, expected one %r"
              % (i, [x[0] for x in lies], NAME_OF[i - 1]))
        check("%s starts at the frame its offset says" % who,
              len(lies) == 1 and lies[0][1] == CAMERA_AT[i - 1],
              "V%d starts at %s, %+.1f s from the In point is frame %d"
              % (i, lies[0][1] if lies else None, moved, CAMERA_AT[i - 1]))
        check("%s goes on whole, not as a piece" % who,
              len(lies) == 1 and lies[0][2] == WHOLE,
              "V%d is %s frames long, the file is %d"
              % (i, lies[0][2] if lies else None, WHOLE))
    named = [tl.GetTrackName("video", i) for i in range(1, 4)]
    check("the video tracks carry the speakers' names",
          named == ["Wide", "Guest", "Hosts"],
          "%s, expected %s" % (named, ["Wide", "Guest", "Hosts"]))
    named = [tl.GetTrackName("audio", i)
             for i in range(1, tl.GetTrackCount("audio") + 1)]
    check("the audio tracks carry them too",
          named == ["Wide", "Guest", "Hosts"],
          "%s, expected %s" % (named, ["Wide", "Guest", "Hosts"]))

    print("\n3. The cut timeline: every shot at the frame the list says")
    cut_tl = vpm.create_timeline(mp, "%s Cut" % ground.name)
    vpm.build_cut_timeline(mp, cut_tl, CUT, cameras, clips, d, None, 0)
    check("the cut stays on one video track",
          cut_tl.GetTrackCount("video") == 1,
          "%d video tracks for a cut of one" % cut_tl.GetTrackCount("video"))
    lies = on_track(cut_tl, "video", 1)
    check("every shot of the cut list is on the timeline",
          len(lies) == len(CUT),
          "%d shots on V1, the cut list names %d" % (len(lies), len(CUT)))
    check("the timeline begins at the In point",
          cut_tl.GetStartFrame() == ORIGIN,
          "begins at frame %d, the In point is %d"
          % (cut_tl.GetStartFrame(), ORIGIN))
    check("each shot starts at the frame the cut list names",
          [x[1] for x in lies] == CUT_AT,
          "shots start at %s, the cut list says %s"
          % ([x[1] for x in lies], CUT_AT))
    check("each shot is as long as the cut list says",
          [x[2] for x in lies] == CUT_LONG,
          "shots are %s frames, the cut list says %s"
          % ([x[2] for x in lies], CUT_LONG))
    check("each shot comes from the camera the cut list names",
          [x[0] for x in lies] == NAME_OF,
          "shots come from %s, the cut list names %s"
          % ([x[0] for x in lies], NAME_OF))
    check("no gap is left between one shot and the next",
          all(a[1] + a[2] == b[1] for a, b in zip(lies, lies[1:])),
          "shots run %s" % [(x[1], x[1] + x[2]) for x in lies])
    check("the cut's video track says what is on it",
          cut_tl.GetTrackName("video", 1) == "Camera cut",
          "V1 is called %r, expected 'Camera cut'"
          % cut_tl.GetTrackName("video", 1))
except Exception as e:
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
