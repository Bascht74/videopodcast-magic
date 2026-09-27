# -*- coding: utf-8 -*-
"""A camera's audio tracks are counted in its file, timecode not among them.

Three camera files with one, two and three sound streams, each carrying
a timecode stream as cameras write it, are counted by audio_track_count.
Then a file with no sound, and a file with sound that ffprobe cannot
be started for: both fall back to the handover, which lists the
processed tracks and not the camera's own microphone, so that one is
added to them.
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
SCRIPT = the_program.SCRIPT
import shutil, subprocess, tempfile, time

began = time.time()
vpm = the_program.load()

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


D = tempfile.mkdtemp(prefix="vpm_audiocount_")
# One ffmpeg call writes all four files: a process start is what the
# Windows builder charges for.
build = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
         "testsrc=size=160x90:rate=25:duration=1"]
for seed in (1, 2, 3):
    build += ["-f", "lavfi", "-i", "anoisesrc=d=1:seed=%d" % seed]
for n in (1, 2, 3, 0):
    build += ["-map", "0:v"]
    for k in range(1, n + 1):
        build += ["-map", "%d:a" % k]
    build += ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
              "yuv420p", "-c:a", "pcm_s16le", "-timecode", "01:00:00:00",
              os.path.join(D, "Cam%d.mov" % n)]
subprocess.run(build, check=True)


def kinds(path):
    """The stream kinds in a file, as ffprobe names them."""
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "stream=codec_type", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return [x.strip() for x in p.stdout.splitlines() if x.strip()]


# A precondition of the material, not a judgement about the program:
# without the timecode stream, counting it by mistake could not show.
for n in (1, 2, 3, 0):
    have = kinds(os.path.join(D, "Cam%d.mov" % n))
    assert have.count("audio") == n and "data" in have, (n, have)

print("Counted in the file")
got = [vpm.audio_track_count({"file": os.path.join(D, "Cam%d.mov" % n)})
       for n in (1, 2, 3)]
check("one, two and three sound streams are counted as such",
      got == [1, 2, 3], "counted %s against [1, 2, 3]" % got)

print("\nNothing to count in the file")
HANDED = ["Host.wav", "Guest.wav"]
mute = vpm.audio_track_count({"file": os.path.join(D, "Cam0.mov"),
                              "audio_tracks": HANDED})
check("a file without sound falls back to the handover", mute == 3,
      "%d tracks against 3: the two handed over and the camera's own"
      % mute)
# A copy never probed before, so no kept answer stands in for ffprobe;
# and a PATH where ffprobe is not, so starting it raises.
UNREAD = os.path.join(D, "Unread.mov")
shutil.copy(os.path.join(D, "Cam1.mov"), UNREAD)
path_was = os.environ.get("PATH", "")
os.environ["PATH"] = tempfile.mkdtemp(prefix="vpm_noprobe_")
try:
    lost = vpm.audio_track_count({"file": UNREAD, "audio_tracks": HANDED})
finally:
    os.environ["PATH"] = path_was
check("a file ffprobe cannot be started for falls back the same way",
      lost == 3,
      "%d tracks against 3: the two handed over and the camera's own"
      % lost)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
