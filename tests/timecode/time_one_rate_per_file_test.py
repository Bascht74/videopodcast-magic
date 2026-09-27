# -*- coding: utf-8 -*-
"""Every place counts a file at one rate: the nominal one, where standard.

A phone recording with a variable frame rate names 30 in its container
and averages less. Read by one place at 30 and by another at the
average, the cut, the Timeline and a timecode land frames apart.

The sections: a variable-rate file ffmpeg writes here, asked of the cut
side, the Resolve side and the timecode side; then the rule itself on
two readings no file here has -- a standard nominal rate beside a
slightly different average, and a nominal figure that is a timebase.
"""
PLATFORM_BOUND = True
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
import shutil, subprocess, tempfile, time
from fractions import Fraction
vpm = the_program.load()
WORK = tempfile.mkdtemp(prefix="onerate_")
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


print("A variable-rate file, asked of every side")

# Two seconds at 30, then every frame held half as long again: the
# container still says 30, the average comes out at 3600/149 = 24.16.
# The clock's frame digit is 29 so that a wrong rate shows in it.
PHONE = os.path.join(WORK, "phone_vfr.mov")
CLOCK = "00:00:10:29"
try:
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi",
                    "-i", "testsrc=size=64x36:rate=30:duration=4",
                    "-vf", "setpts='if(gte(N,60),(60+(N-60)*1.5)/30/TB,"
                           "N/30/TB)'",
                    "-fps_mode", "vfr", "-c:v", "libx264",
                    "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                    "-video_track_timescale", "600", "-timecode", CLOCK,
                    PHONE, "-y"], check=True)
    stream = next(s for s in vpm.ffprobe_json(PHONE)["streams"]
                  if s.get("codec_type") == "video")
except Exception as e:
    stream = {"error": str(e)}
nominal, mean = stream.get("r_frame_rate"), stream.get("avg_frame_rate")
check("the material names 30 and averages under 25",
      nominal == "30/1" and mean not in (None, "0/0", "30/1")
      and float(Fraction(mean)) < 25.0,
      "ffprobe says r_frame_rate %s, avg_frame_rate %s; wanted 30/1 and "
      "an average under 25" % (nominal, mean))

if os.path.isfile(PHONE):
    facts = vpm.video_facts(PHONE)
    cut_side, resolve_side = facts["fps"], vpm.file_frame_rate(facts)
    check("the cut and the Resolve side both count the phone file at 30",
          abs(cut_side - 30.0) < 1e-9 and abs(resolve_side - 30.0) < 1e-9,
          "cut side %.4f, Resolve side %.4f, wanted 30 for both"
          % (cut_side, resolve_side))
    read = vpm.file_timecode(PHONE)
    check("a timecode's frame digit 29 on the phone file is 29/30 s on",
          read is not None and abs(read - 10.9667) < 0.001,
          "read %r s, wanted 10.9667 (10 s and 29 frames at 30; at the "
          "average 24.16 it is 11.2003, 7 frames late)" % read)


print("\nThe rule, on readings no file here has")

ntsc = vpm.stream_frame_rate({"r_frame_rate": "30000/1001",
                               "avg_frame_rate": "2990/100"})
check("a standard nominal rate wins over a slightly different average",
      ntsc is not None and abs(ntsc - 29.97003) < 0.0001,
      "answered %r, wanted 29.97003 (30000/1001) and not 29.90" % ntsc)
timebase = vpm.stream_frame_rate({"r_frame_rate": "90000/1",
                                  "avg_frame_rate": "2997/100"})
check("a nominal figure that is no camera's gives way to the average",
      timebase is not None and abs(timebase - 29.97) < 0.0001,
      "answered %r, wanted 29.97 from the average and not 90000" % timebase)

shutil.rmtree(WORK, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
