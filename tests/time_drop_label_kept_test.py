# -*- coding: utf-8 -*-
"""A timecode written back stays on the clock it was read from.

timecode_string is asked directly, so nothing here depends on what a
caller makes of the answer. The sections: the label -- with the flag
the semicolon stands before the frames, without it the colon, and the
digits are the same on both clocks; the count -- timecode_to_frames
reads the drop-frame label as the drop-frame frames since midnight and
the non-drop one as thirty a second; and a label moved on, which keeps
the separator it came with.
"""
import sys
import time
import the_program

vpm = the_program.load()

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


FPS = 29.97
# Ten hours since midnight, and ten hours and half a second: half a
# second at 29.97 is fifteen frames, so the frames digits are not zero.
TEN_HOURS = 36000.0
HALF_IN = 36000.5

print("1. THE LABEL")
drop = vpm.timecode_string(HALF_IN, FPS, drop_frame=True)
check("a drop-frame label written back carries the semicolon",
      drop == "10:00:00;15", "wrote %r, wanted '10:00:00;15'" % drop)
plain = vpm.timecode_string(HALF_IN, FPS)
check("a non-drop label keeps the colon and the same digits",
      plain == "10:00:00:15", "wrote %r, wanted '10:00:00:15'" % plain)

print("\n2. THE COUNT")
# Ten hours of labels are 1,080,000 numbers; the drop-frame clock skips
# two in each of the 540 minutes that are not a tenth, so the label
# 10:00:00;00 is frame 1,078,920. On a colon the same digits count
# 1,080,000 -- 1,080 frames or 36 s later on the drop-frame clock.
counted = vpm.timecode_to_frames(
    vpm.timecode_string(TEN_HOURS, FPS, drop_frame=True), FPS)
check("the drop-frame label counts the drop-frame frames since midnight",
      counted == 1078920, "counted %d frames, wanted 1078920" % counted)
counted = vpm.timecode_to_frames(vpm.timecode_string(TEN_HOURS, FPS), FPS)
check("the non-drop label still counts thirty a second",
      counted == 1080000, "counted %d frames, wanted 1080000" % counted)

print("\n3. A LABEL MOVED ON")
moved = vpm.timecode_moved("10:00:00;00", 3600.0, FPS)
check("a drop-frame label moved on keeps its semicolon",
      moved == "11:00:00;00", "moved to %r, wanted '11:00:00;00'" % moved)
moved = vpm.timecode_moved("10:00:00:00", 3600.0, FPS)
check("and a non-drop label moved on keeps its colon",
      moved == "11:00:00:00", "moved to %r, wanted '11:00:00:00'" % moved)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
