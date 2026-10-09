# -*- coding: utf-8 -*-
"""Where an intro's sound starts and ends is found, and none is invented.

audible_range decides where the jingle's sound sits inside its file,
since a jingle can carry silence before and after. The files are
written here. In order: a tone between two silences is found at its
edges, a file of silence has no range, a sound shorter than a quarter
second has none either; then the intro entry: a file that is not a
video gives no entry, and a real one carries its length and the
sound's edges.
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
import shutil
import subprocess
import tempfile
import time
import the_program

SCRIPT = the_program.SCRIPT
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
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


folder = tempfile.mkdtemp(prefix="vpm_jingle_")


def tone(name, graph):
    out = os.path.join(folder, name)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    graph, "-c:a", "pcm_s16le", out],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out


# Silence 0.5 s, tone 1 s, silence 0.5 s.
framed = tone("framed.wav", "sine=frequency=500:duration=1,"
              "adelay=500:all=1,apad=pad_dur=0.5")
silent = tone("silent.wav", "anullsrc=r=48000:cl=mono,atrim=duration=2")
brief = tone("brief.wav", "sine=frequency=500:duration=0.2")
intro = os.path.join(folder, "intro.mov")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "testsrc=size=64x36:rate=25:duration=2", "-i", framed,
                "-c:v", "libx264", "-c:a", "pcm_s16le", "-shortest", intro],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
text = os.path.join(folder, "notes.mov")
open(text, "w").write("not a video\n")

start, end = vpm.audible_range(framed)
check("a tone between two silences is found at its edges",
      start is not None and abs(start - 0.5) <= 0.05
      and abs(end - 1.5) <= 0.05,
      "%r to %r, wanted 0.5 to 1.5 within 0.05 s" % (start, end))
got = vpm.audible_range(silent)
check("a file of silence has no audible range", got == (None, None),
      "%r" % (got,))
got = vpm.audible_range(brief)
check("a sound under a quarter second has no range", got == (None, None),
      "%r" % (got,))

try:
    got = vpm._intro_outro_entry(text)
except Exception as e:
    got = "raised %s" % type(e).__name__
check("a file that is not a video gives no intro entry", got is None,
      "%r" % (got,))
entry = vpm._intro_outro_entry(intro) or {}
check("the intro entry carries its length and the sound's edges",
      abs((entry.get("duration") or 0) - 2.0) <= 0.05
      and abs((entry.get("audio_from") or 0) - 0.5) <= 0.05
      and abs((entry.get("audio_to") or 0) - 1.5) <= 0.05,
      "length %r, sound %r to %r; wanted 2.0, 0.5 to 1.5"
      % (entry.get("duration"), entry.get("audio_from"),
         entry.get("audio_to")))

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
