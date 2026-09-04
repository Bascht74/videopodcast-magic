# -*- coding: utf-8 -*-
"""A camera is cut to the window even where its key frames cannot be read.

The copy starts on the key frame before the window so the picture is not
taken from between two of them. Where that query fails there is no key
frame to start on and the front stays whole -- but the end is cut all
the same, and the line the run prints has to say so. "Both ends" is the
control with the query working, "no key frames" the same call with it
failing, and "what it says" the line itself.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import contextlib, io, subprocess, sys, tempfile, time
vpm = the_program.load()
vpm.set_language("en")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


#------------------------------------------------------------- Material

D = tempfile.mkdtemp(prefix="withoutkeys_")
CAMERA = os.path.join(D, "Camera.mov")
FPS, LENGTH = 25, 20.0
# A key frame on every whole second, so what the copy may start on is a
# value here and not a second calculation.
subprocess.run(
    ["ffmpeg", "-v", "error", "-f", "lavfi",
     "-i", "testsrc2=size=160x90:rate=%d:duration=%.1f" % (FPS, LENGTH),
     "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
     "-force_key_frames", "expr:eq(mod(n,%d),0)" % FPS, "-y", CAMERA],
    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# The material has to carry the key frames the expectations rest on.
# That says nothing about the program, so it is an assert, not a check.
marks = [round(float(x.strip().rstrip(",")), 3) for x in subprocess.run(
    ["ffprobe", "-v", "error", "-select_streams", "v:0", "-skip_frame",
     "nokey", "-show_entries", "frame=pts_time", "-of", "csv=p=0",
     "-read_intervals", "%+9", CAMERA],
    capture_output=True, text=True).stdout.splitlines() if x.strip()]
assert marks[:5] == [0.0, 1.0, 2.0, 3.0, 4.0], marks[:5]

# The camera rolled 8.4 s before the window begins and the window runs
# 5 s. So in camera time the window is 8.4 to 13.4, and with the second
# the program keeps at each end the copy wants 7.4 to 14.4. The tenths
# are the point: 7.4 falls between two key frames and the copy has to go
# back to 7.0.
OFFSET, WINDOW_S = -8.4, 5.0
CUT_AT, KEEP_S = 7.0, 7.4
# Without a key frame to go back to, the copy starts at 0 and keeps
# everything up to the end of the window and its margin.
BLIND_CUT_AT, BLIND_KEEP_S = 0.0, 14.4

real_run = vpm.subprocess.run


def blind_run(cmd, *a, **k):
    """ffprobe refuses the key-frame query, and nothing else."""
    if isinstance(cmd, (list, tuple)) and "-skip_frame" in cmd:
        raise OSError("stand-in: the key-frame query fails")
    return real_run(cmd, *a, **k)


said = io.StringIO()
seeing = vpm.camera_window_cut(CAMERA, LENGTH, OFFSET, WINDOW_S)
vpm.subprocess.run = blind_run
try:
    with contextlib.redirect_stdout(said):
        blind = vpm.camera_window_cut(CAMERA, LENGTH, OFFSET, WINDOW_S)
finally:
    vpm.subprocess.run = real_run
spoken = said.getvalue()

#------------------------------------------------------------ The answers

print("1. Both ends, with the key frames read")
check("the copy starts on the key frame before the window",
      abs(seeing[0] - CUT_AT) < 0.001,
      "starts at %.3f s, wanted %.3f" % (seeing[0], CUT_AT))
check("and it is as long as the window and a second at each end",
      seeing[1] is not None and abs(seeing[1] - KEEP_S) < 0.001,
      "%s s written, wanted %.3f" % (seeing[1], KEEP_S))

print("\n2. The same call with no key frames to be had")
check("the end is still cut to the window",
      blind[1] is not None and abs(blind[1] - BLIND_KEEP_S) < 0.001,
      "%s s of %.1f written, wanted %.3f"
      % (blind[1], LENGTH, BLIND_KEEP_S))
check("and the front is left where it is, there being no key frame",
      abs(blind[0] - BLIND_CUT_AT) < 0.001,
      "starts at %.3f s, wanted %.3f" % (blind[0], BLIND_CUT_AT))

print("\n3. And it says so")
check("the run names the camera whose key frames it could not read",
      os.path.basename(CAMERA) in spoken,
      "looked for %r in the %d characters printed: %r"
      % (os.path.basename(CAMERA), len(spoken), spoken[:120]))

vpm.shutil.rmtree(D, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
