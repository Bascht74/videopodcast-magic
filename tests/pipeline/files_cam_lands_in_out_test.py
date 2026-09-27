# -*- coding: utf-8 -*-
"""A camera's file lands in the result folder, whatever its name holds.

One real run of one camera, its own sound the track, named through the
assignment file the window writes -- with a name that is a path into
another folder, as a field typed into can hold. The sections: nothing
is written where the name points, the camera file stands in the result
folder, the handover carries that file for the camera, and the log
says under which name it was written. The limit: one camera, and a
name the window would hand over; --new-name refuses such a name.
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
import json
import re
import shutil
import subprocess
import tempfile
import time

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


HOME = tempfile.mkdtemp(prefix="vpm_camname_")
CAMERA = os.path.join(HOME, "media", "WideCam_C001.mov")
OUT = os.path.join(HOME, "out")
# Where the name points: a folder of its own, there and empty, so a
# file written by the name would land and be seen.
ELSEWHERE = os.path.join(HOME, "elsewhere")
for folder in (os.path.dirname(CAMERA), OUT, ELSEWHERE):
    os.makedirs(folder)
NAME = os.path.join(ELSEWHERE, "Stray")
# Ninety seconds of bursts of noise: enough for the camera to be laid
# against its own sound, which a steady tone is not.
made = subprocess.run(
    ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
     "testsrc=size=160x90:rate=25:duration=90", "-f", "lavfi", "-i",
     "anoisesrc=color=pink:duration=90:seed=7,"
     "volume='if(lt(mod(t*t,2.3),0.9),1,0.03)':eval=frame",
     "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
     "-c:a", "pcm_s16le", "-shortest", CAMERA],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=240)
# A precondition of the material, not a judgement about the program.
assert made.returncode == 0 and os.path.exists(CAMERA), made.stdout
ASSIGN = os.path.join(HOME, "assign.json")
with open(ASSIGN, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "created_by": "test",
               "production": "Plain", "tracks_of": [],
               "cameras": [{"video": CAMERA, "name": NAME}]}, f)
env = dict(os.environ, QT_QPA_PLATFORM="offscreen")
try:
    kid = subprocess.run([sys.executable, SCRIPT, "--without-auphonic",
                          "--out", OUT, "--assign", ASSIGN, CAMERA],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         timeout=280, env=env)
    code = kid.returncode
    said = re.sub(r"\x1b\[[0-9;]*m", "", kid.stdout.decode("utf-8",
                                                          "replace"))
except subprocess.TimeoutExpired:
    code, said = None, "no end within 280 s"
lines = [line.strip() for line in said.replace("\r", "\n").splitlines()
         if line.strip()]
last = lines[-1] if lines else ""

print("1. Where the name points")
strays = sorted(os.listdir(ELSEWHERE))
check("nothing is written into the folder the name points at",
      not strays, "%d files there: %s; the run returned %r, last line %r"
      % (len(strays), strays, code, last))

print("\n2. The result folder")
written = sorted(n for n in os.listdir(OUT) if n.endswith(".mov"))
check("the camera file stands in the result folder",
      len(written) == 1, "%d camera files there: %s; the run returned "
      "%r, last line %r" % (len(written), written, code, last))
FILE = os.path.join(OUT, written[0]) if len(written) == 1 else ""

print("\n3. The handover")
handed = []
for name in os.listdir(OUT):
    if name.endswith("_resolve.json"):
        with open(os.path.join(OUT, name), encoding="utf-8") as f:
            handed = [c.get("file") or "" for c in json.load(f)["cameras"]]
check("the handover carries that file for the camera",
      FILE and [os.path.normcase(p) for p in handed]
      == [os.path.normcase(FILE)],
      "the handover names %s against %r" % (handed, FILE))

print("\n4. The log")
# The name it was written under is read off the file, not worked out.
STEM = written[0][:-len("_audio.mov")] if FILE else "?"
TOLD = vpm.T('  The camera name "%s" holds a folder or drive separator; '
             'it is written as "%s".').strip() % (NAME, STEM)
check("the log says the name was written as a plain one",
      TOLD in lines, "'%s' %s" % (TOLD, "said" if TOLD in lines
                                  else "not said"))

shutil.rmtree(HOME, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
