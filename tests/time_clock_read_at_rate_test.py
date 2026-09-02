# -*- coding: utf-8 -*-
"""What a file's clock says is read at that file's own rate.

Reading a clock and placing a camera are two questions, and this is
the first of them: file_timecode is asked directly, so nothing here
depends on what a caller makes of the answer.

The sections: the two places a clock is kept -- a bext stamp and a
timecode track; the frames of a timecode read at two rates and at the
file's own; and the two answers that look alike and are not, a clock
standing at zero and no clock at all.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, struct, subprocess, sys, tempfile, time
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
WORK = tempfile.mkdtemp(prefix="clockread_")
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stamped(path, seconds):
    """Write a file that carries *seconds* in a bext chunk.

    That is where file_timecode looks first, and it costs no ffprobe.
    """
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


# 18:55:00:00 and 18:55:04:00 in seconds since midnight. Whole seconds
# on purpose: a timecode carrying no frames names the same instant at
# every rate, so the two files below differ in their frames alone.
BASE = 68100.0
FOUR = 68104.0

print("The two places a clock is kept")
at_four = stamped(os.path.join(WORK, "four_seconds_in.wav"), FOUR)
midnight = stamped(os.path.join(WORK, "at_midnight.wav"), 0.0)
plain = os.path.join(WORK, "no_clock.wav")
open(plain, "w").write("x")
with_tc = little_camera("with_timecode.mov", "18:55:04:00")
blank = little_camera("without_timecode.mov", None)
twelve = little_camera("twelve_frames.mov", "18:55:04:12")
from_zero = little_camera("twelve_frames_from_zero.mov", "18:55:00:12")

bext = vpm.file_timecode(at_four, 25.0)
check("a bext stamp is read where one is there",
      bext is not None and abs(bext - FOUR) < 1e-6,
      "read %r, wanted %.1f s" % (bext, FOUR))
built = vpm.file_timecode(with_tc, 25.0)
check("the built file carries a timecode",
      built is not None and abs(built - FOUR) < 0.001,
      "read %r, wanted %.1f s" % (built, FOUR))
none_at_all = vpm.file_timecode(blank, 25.0)
check("and the one built without one carries none", none_at_all is None,
      "read %r, wanted nothing at all" % (none_at_all,))

print("\nThe frames of a timecode are frames")
# The same twelve frames, read at two rates. 12/30 is 0.400 s and 12/25
# is 0.480 s, and eighty milliseconds is two frames of picture.
at30 = vpm.file_timecode(from_zero, 30.0)
at25 = vpm.file_timecode(from_zero, 25.0)
check("12 frames at 30 fps are 0.400 s",
      at30 is not None and abs((at30 - BASE) - 0.4) < 1e-6,
      "read %r, which is %s past %.1f s, wanted 0.400 s"
      % (at30, "nothing" if at30 is None else "%.4f s" % (at30 - BASE),
         BASE))
check("the same 12 frames at 25 fps are 0.480 s",
      at25 is not None and abs((at25 - BASE) - 0.48) < 1e-6,
      "read %r, which is %s past %.1f s, wanted 0.480 s"
      % (at25, "nothing" if at25 is None else "%.4f s" % (at25 - BASE),
         BASE))
# And with no rate passed at all the file's own is taken. Both files
# below are 25 fps material, so twelve frames must come out at 0.48 s
# -- read at 30 the gap would be 0.40 s.
own_far = vpm.file_timecode(twelve)
own_near = vpm.file_timecode(with_tc)
check("the frames of a timecode are read at the file's rate",
      own_far is not None and own_near is not None
      and abs((own_far - own_near) - 0.48) < 0.001,
      "%r less %r is %s, wanted 0.480 s -- at 30 fps it would be 0.400"
      % (own_far, own_near,
         "nothing" if own_far is None or own_near is None
         else "%.4f s" % (own_far - own_near)))

print("\nA clock at zero, and no clock at all")
# Read as a truth value rather than as "there is one", a stamp of zero
# counts as no stamp, and every caller then falls back on something
# else. The two answers have to be told apart here, where they are
# read, and not by each caller for itself.
at_zero = vpm.file_timecode(midnight, 25.0)
check("a timecode of zero reads as zero, not as nothing",
      at_zero is not None and abs(at_zero) < 1e-9,
      "read %r, wanted 0.0 and not None" % (at_zero,))
nothing = vpm.file_timecode(plain, 25.0)
check("a file carrying no clock in either place answers nothing",
      nothing is None, "read %r, wanted nothing at all" % (nothing,))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
