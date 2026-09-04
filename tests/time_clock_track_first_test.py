# -*- coding: utf-8 -*-
"""A file's clock is read off its track before the file's own level.

A track's clock is what the camera wrote. The file's is what ffmpeg
made of the file, and the two can disagree: an unclaimed timecode
track is reported on the file level, a whole hour away from the
camera's own. Read in that order the camera wins, and a file that
keeps a clock nowhere but on its own level is still read.

The sections: the order asked of a probe built here, so that no
ffmpeg version can decide the answer; and the same order asked of two
files ffmpeg really wrote, which is where the shapes above come from.
"""
import os
import the_program
import shutil, subprocess, sys, tempfile, time
vpm = the_program.load()
WORK = tempfile.mkdtemp(prefix="trackfirst_")
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# 01:00:00:00 and 02:00:00:00, an hour apart -- the distance a camera
# travels on the common axis when the wrong one of the two is taken.
# Whole seconds carry no frames, so no frame rate can shift them.
TRACK, TRACK_S = "01:00:00:00", 3600.0
FILE, FILE_S = "02:00:00:00", 7200.0
LONE, LONE_S = "09:00:00:00", 32400.0


def probed(on_track, on_file):
    """An ffprobe answer carrying a clock on the track, the file, or both."""
    stream = {"codec_type": "video", "codec_name": "h264",
              "avg_frame_rate": "25/1", "r_frame_rate": "25/1",
              "width": 64, "height": 36, "duration": "1.0", "tags": {}}
    if on_track:
        stream["tags"]["timecode"] = on_track
    top = {"duration": "1.0", "tags": {}}
    if on_file:
        top["tags"]["timecode"] = on_file
    return {"streams": [stream], "format": top}


def asking(answer):
    """Put a made-up probe in front of the program and take it away after."""
    real = vpm.ffprobe_json
    vpm.ffprobe_json = lambda path: answer
    return real


print("The order, asked of a probe built here")
# A path that is not there: file_timecode looks for a bext stamp first
# and finds none, which is the case every camera file is in.
NOWHERE = os.path.join(WORK, "no_such_file.mov")
was = asking(probed(TRACK, FILE))
try:
    both = vpm.file_timecode(NOWHERE, 25.0)
    both_facts = (vpm.video_facts(NOWHERE) or {}).get("tc")
    vpm.ffprobe_json = lambda path: probed(TRACK, None)
    track_only = vpm.file_timecode(NOWHERE + "2", 25.0)
    vpm.ffprobe_json = lambda path: probed(None, FILE)
    file_only = vpm.file_timecode(NOWHERE + "3", 25.0)
    file_only_facts = (vpm.video_facts(NOWHERE + "3") or {}).get("tc")
finally:
    vpm.ffprobe_json = was

check("a clock kept only on a track is read",
      track_only is not None and abs(track_only - TRACK_S) < 1e-6,
      "read %r, wanted %.1f s for %s" % (track_only, TRACK_S, TRACK))
check("a clock kept only on the file level is read",
      file_only is not None and abs(file_only - FILE_S) < 1e-6,
      "read %r, wanted %.1f s for %s" % (file_only, FILE_S, FILE))
check("the track's clock is taken where the file's disagrees",
      both is not None and abs(both - TRACK_S) < 1e-6,
      "read %r, wanted %.1f s (%s off the track) and not %.1f s (%s off "
      "the file)" % (both, TRACK_S, TRACK, FILE_S, FILE))
check("video_facts takes the track's clock where the file's disagrees",
      both_facts == TRACK,
      "read %r, wanted %r off the track and not %r off the file"
      % (both_facts, TRACK, FILE))
check("video_facts reads a clock kept only on the file level",
      file_only_facts == FILE,
      "read %r, wanted %r" % (file_only_facts, FILE))


print("\nThe order, asked of files ffmpeg wrote")


def one_second(clocks, name):
    """A file of one second per clock given, each clock on a track."""
    out = os.path.join(WORK, name)
    call = ["ffmpeg", "-v", "error"]
    for _ in clocks:
        call += ["-f", "lavfi", "-i", "testsrc=size=64x36:rate=25:duration=1"]
    for i in range(len(clocks)):
        call += ["-map", "%d:v" % i]
    call += ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p"]
    for i, c in enumerate(clocks):
        call += ["-metadata:s:v:%d" % i, "timecode=%s" % c]
    try:
        subprocess.run(call + [out, "-y"], check=True)
    except Exception:
        return None
    return out


def unclaimed(src, name):
    """Leave the last timecode track claimed by no picture track.

    ffmpeg writes one timecode track per picture track and a `tref` box
    pointing at it. Renaming the last of those boxes to `free` -- a box
    every reader steps over -- leaves that timecode track unclaimed,
    and ffprobe then reports its clock on the file level. That is the
    shape a real camera file takes on when ffmpeg reads only the first
    of several references out of one box.
    """
    out = os.path.join(WORK, name)
    raw = bytearray(open(src, "rb").read())
    spots, i = [], 0
    while True:
        j = raw.find(b"tref", i)
        if j < 0:
            break
        spots.append(j)
        i = j + 1
    if not spots:
        return None
    raw[spots[-1]:spots[-1] + 4] = b"free"
    with open(out, "wb") as f:
        f.write(bytes(raw))
    return out


def clocks_of(path):
    """(what the file level says, what the first track says)."""
    try:
        d = vpm.ffprobe_json(path)
    except Exception:
        return None, None
    top = ((d.get("format") or {}).get("tags") or {}).get("timecode")
    on_track = next((t for t in [(s.get("tags") or {}).get("timecode")
                                 for s in d.get("streams") or []] if t), None)
    return top, on_track


# One file whose two clocks disagree, and one that keeps a clock
# nowhere but on its own level. MXF is asked for the second because it
# is where broadcast material really keeps its clock, and ffmpeg puts
# none on a track there.
pair = one_second([TRACK, FILE], "two_clocks.mov")
split = unclaimed(pair, "unclaimed.mov") if pair else None
lone = os.path.join(WORK, "file_level_only.mxf")
try:
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi",
                    "-i", "testsrc=size=64x36:rate=25:duration=1",
                    "-c:v", "mpeg2video", "-pix_fmt", "yuv420p",
                    "-timecode", LONE, lone, "-y"], check=True)
except Exception:
    lone = None

top, on_track = clocks_of(split) if split else (None, None)
disagree = top == FILE and on_track == TRACK
lone_top, lone_track = clocks_of(lone) if lone else (None, None)
lone_ready = lone_top == LONE and lone_track is None

if disagree and lone_ready:
    real_pair = vpm.file_timecode(split, 25.0)
    real_facts = (vpm.video_facts(split) or {}).get("tc")
    real_lone = vpm.file_timecode(lone, 25.0)
    check("a written file's track clock beats the one on its file level",
          real_pair is not None and abs(real_pair - TRACK_S) < 1e-6,
          "read %r, wanted %.1f s (%s off the track) and not %.1f s (%s "
          "off the file)" % (real_pair, TRACK_S, TRACK, FILE_S, FILE))
    check("video_facts reads a written file's clock off its track",
          real_facts == TRACK,
          "read %r, wanted %r off the track and not %r off the file"
          % (real_facts, TRACK, FILE))
    check("a written file whose only clock is its file level is read",
          real_lone is not None and abs(real_lone - LONE_S) < 1e-6,
          "read %r, wanted %.1f s for %s" % (real_lone, LONE_S, LONE))
else:
    print("  LEFT OUT the three judgements on written files: this ffmpeg "
          "reports %r on the file level and %r on a track of the file "
          "built to disagree (wanted %r and %r), and %r on the file "
          "level of the MXF with %r on a track (wanted %r and nothing)"
          % (top, on_track, FILE, TRACK, lone_top, lone_track, LONE))

shutil.rmtree(WORK, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
