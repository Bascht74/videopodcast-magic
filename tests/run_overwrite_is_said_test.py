# -*- coding: utf-8 -*-
"""A run that replaces a file says so, and marks one it did not make.

Writing over the delivery of an earlier run is the everyday case and
gets a quiet line. Writing over anything else -- an original, a proxy, a
hand-made export, another production's result under the same name -- is
marked: nothing here says this program made it, and until now the run
walked over it without a word.

The sections: what the record of earlier runs holds, what is said about
a target something is already lying at, and one real run to show the
line reaches the log. What this cannot show is that a person reads it.
"""
import os
import subprocess
import sys
import tempfile
import time
import json
import shutil
import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
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


D = tempfile.mkdtemp(prefix="vpm_overwrite_")
OUT = os.path.join(D, "out")
os.makedirs(OUT)
KNOWN = os.path.join(OUT, "CamOne_audio.mov")
STRANGE = os.path.join(OUT, "CamTwo_audio.mov")
GONE = os.path.join(OUT, "CamThree_audio.mov")
for path in (KNOWN, STRANGE):
    with open(path, "w", encoding="utf-8") as f:
        f.write("a file standing where a target would go")
with open(os.path.join(OUT, "Show_resolve.json"), "w", encoding="utf-8") as f:
    json.dump({"cameras": [{"camera": "CamOne", "file": KNOWN}]}, f)
# In a folder of its own, and that is not tidiness: beside the good one
# it sorts first, and a reader that took any record it found would come
# back empty off this one and look right.
TORN = os.path.join(D, "torn")
os.makedirs(TORN)
with open(os.path.join(TORN, "Broken_resolve.json"), "w",
          encoding="utf-8") as f:
    f.write("this is not a handover")

print("1. What the record of earlier runs here holds")
ours = vpm.written_before_here(OUT, "Show")
check("the record names the file an earlier run wrote here",
      vpm.path_key(KNOWN) in ours,
      "%d entries, wanted %r among them" % (len(ours), vpm.path_key(KNOWN)))
check("and it names nothing else",
      vpm.path_key(STRANGE) not in ours,
      "%d entries, did not want %r" % (len(ours), vpm.path_key(STRANGE)))
other = vpm.written_before_here(OUT, "Other")
check("a production with no record of its own reads nothing",
      other == set(), "%d entries, wanted 0" % len(other))
broken = vpm.written_before_here(TORN, "Broken")
check("an unreadable record reads nothing instead of stopping the run",
      broken == set(), "%d entries, wanted 0" % len(broken))

print("\n2. What is said about a target something lies at")
check("nothing is said about a target that is not there",
      vpm.replacement_lines([GONE], ours) == [],
      str(vpm.replacement_lines([GONE], ours)))
quiet = vpm.replacement_lines([KNOWN], ours)
check("a delivery of an earlier run gets one line",
      len(quiet) == 1, "%d lines: %s" % (len(quiet), quiet))
check("and that line is not marked",
      bool(quiet) and vpm.split_kind(quiet[0])[0] == "text",
      "kind %r, wanted 'text'"
      % (vpm.split_kind(quiet[0])[0] if quiet else "no line"))
loud = vpm.replacement_lines([STRANGE], ours)
check("a file this production has no record of is marked",
      bool(loud) and vpm.split_kind(loud[0])[0] == "error",
      "kind %r, wanted 'error'"
      % (vpm.split_kind(loud[0])[0] if loud else "no line"))
check("the marked line names the whole path",
      bool(loud) and STRANGE in loud[0],
      "%r -- wanted %r in it" % (loud[0] if loud else "no line", STRANGE))
check("the quiet line names the file and not the path",
      bool(quiet) and os.path.basename(KNOWN) in quiet[0]
      and OUT not in quiet[0],
      "%r -- wanted %r in it and %r out of it"
      % (quiet[0] if quiet else "no line", os.path.basename(KNOWN), OUT))

print("\n3. A real run says it")
# Forty seconds of pink noise under a small picture: long enough for the
# alignment to find points, small enough to build and write in seconds.
M = os.path.join(D, "mat")
os.makedirs(M)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "anoisesrc=color=pink:duration=40:sample_rate=48000",
                "-af", "tremolo=f=3:d=0.8", "-ac", "1", "-c:a", "pcm_s16le",
                os.path.join(M, "Rec.wav")], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "smptebars=size=160x90:rate=25:duration=40",
                "-i", os.path.join(M, "Rec.wav"), "-map", "0:v", "-map", "1:a",
                "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
                "yuv420p", "-c:a", "pcm_s16le", "-shortest",
                os.path.join(M, "Cam.mov")], check=True)
RUN_OUT = os.path.join(D, "run")
os.makedirs(RUN_OUT)
# A file nobody here made, standing exactly where the run will write.
WALKED_ON = os.path.join(RUN_OUT, "Cam_audio.mov")
with open(WALKED_ON, "w", encoding="utf-8") as f:
    f.write("a hand-made export")
ENV = dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="en", VPM_SILENT="1",
           VPM_NO_SPEAKER_SPLIT="1", VPM_NO_UPDATE_CHECK="1",
           QT_QPA_PLATFORM="offscreen")
p = subprocess.run(
    [sys.executable, SCRIPT, "--without-auphonic", "--no-metrics",
     "--no-speech-recognition", "--no-transcript-file", "--no-wide-edges",
     "--out", RUN_OUT, os.path.join(M, "Rec.wav"), os.path.join(M, "Cam.mov")],
    capture_output=True, text=True, env=ENV)
log = (p.stdout or "") + (p.stderr or "")
check("the run goes through", p.returncode == 0,
      "returned %d, ends: %s" % (p.returncode, log.strip()[-90:]))
wanted = vpm.T('  %s is already there and is written over -- this '
               'production has no record of making it.') % WALKED_ON
check("a real run says it about a file nobody here made", wanted in log,
      "%r against %d characters of log" % (wanted, len(log)))
# Otherwise the line could be a false alarm about a file nothing touches,
# and the check above would be just as green.
after = os.path.getsize(WALKED_ON) if os.path.exists(WALKED_ON) else -1
check("and the file it warned about really is written over",
      after > len("a hand-made export"),
      "%d bytes afterwards, -1 for not there, %d before"
      % (after, len("a hand-made export")))

shutil.rmtree(D, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
