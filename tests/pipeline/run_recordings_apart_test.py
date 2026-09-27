# -*- coding: utf-8 -*-
"""A run names two recordings of one file name apart, as the file list does.

One real run, started with the command line the window builds, on two
recordings of one file name on two cards, each a speaker of its own,
and a camera beside them. The plan the run prints names the first by
its file name and the second "(2)", in the order the window lists them
-- the file list's own rule, recording_labels, over the same order.
Then without typed names: the window's plan and a plain command line
guess two speakers, the second "(2)", each its own track, while a block
continuing card A's recording in its folder still joins it. Last, two
other file names guessing one speaker: two folders stay two speakers,
a gap in one folder still joins, a name typed alike on two folders
joins them, and the summary counts recordings, not blocks.
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
import json
import re
import shutil
import subprocess
import tempfile
import time
import the_program

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


def recording_in_plan(log, speaker):
    """The file the plan's line for *speaker* names, and the line itself."""
    for x in log.splitlines():
        m = re.match(r"  %s {2,}(\S.*?) +\d+:\d\d:\d\d"
                     % re.escape(speaker), x)
        if m:
            return m.group(1), x
    return None, ""


D = tempfile.mkdtemp(prefix="vpm_recs_")
# Forty seconds of pink noise, long enough for the alignment to find
# points. Two recorders, each with a card of its own, and both write the
# same file name; the camera heard the same room.
SRC = os.path.join(D, "room.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "anoisesrc=color=pink:duration=40:sample_rate=48000",
                "-af", "tremolo=f=3:d=0.8", "-ac", "1", "-c:a", "pcm_s16le",
                SRC], check=True)
RECS = []
for card, gain in (("CardA", "1"), ("CardB", "0.5")):
    os.makedirs(os.path.join(D, card))
    RECS.append(os.path.join(D, card, "ZOOM0001.WAV"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-af",
                    "volume=" + gain, "-c:a", "pcm_s16le", RECS[-1]],
                   check=True)
# Card A's recorder went on into a second block, a seamless continuation
# in the same folder: shorter than the first, as a last block is.
MORE = os.path.join(D, "CardA", "ZOOM0002.WAV")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-t", "10",
                "-c:a", "pcm_s16le", MORE], check=True)
CAM = os.path.join(D, "C0001.MP4")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "smptebars=size=160x90:rate=25:duration=40", "-i", SRC,
                "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                "-c:a", "pcm_s16le", "-shortest", CAM], check=True)
OUT = os.path.join(D, "out")
os.makedirs(OUT)
# The window writes the plan beside the line; so does this. The file
# list's order is the order of "files": card A first.
ASSIGN = os.path.join(D, "assign.json")
argv, plan, _m = vpm.run_argv({
    "files": [(RECS[0], "audio"), (RECS[1], "audio"), (CAM, "video")],
    "rows": [{"blocks": [RECS[0]], "speakers": "Guest",
              "camera_choice": ""},
             {"blocks": [RECS[1]], "speakers": "Presenter",
              "camera_choice": ""}],
    "cameras": [{"path": CAM, "name": "C0001"}],
    "clip_kinds": {}, "out_folder": OUT, "multitrack": False,
    "production": "Pilot", "cut": {}, "wide_at_edges": False,
    "key": ""}, ASSIGN)
with open(ASSIGN, "w", encoding="utf-8") as f:
    json.dump(plan or {}, f)
ENV = dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="en", VPM_SILENT="1",
           VPM_NO_SPEAKER_SPLIT="1", VPM_NO_UPDATE_CHECK="1",
           QT_QPA_PLATFORM="offscreen")
p = subprocess.run(
    [sys.executable, SCRIPT] + list(argv or ["-"])[1:]
    + ["--no-metrics", "--no-speech-recognition", "--no-transcript-file"],
    capture_output=True, text=True, env=ENV)
log = (p.stdout or "") + (p.stderr or "")

print("1. The run")
check("the run goes through on the window's command line",
      p.returncode == 0,
      "returned %d, last line: %s" % (p.returncode, (log.replace(
          D, "<tmp>").strip().splitlines() or [""])[-1][-120:]))

print("\n2. The two recordings, as the file list names them")
first, first_line = recording_in_plan(log, "Guest")
check("the plan names the first recording by its file name",
      first == "ZOOM0001.WAV",
      "Guest's recording named %r, wanted 'ZOOM0001.WAV'; the line: %r"
      % (first, first_line))
second, second_line = recording_in_plan(log, "Presenter")
check("and the second of that name (2), as the file list does",
      second == "ZOOM0001.WAV (2)",
      "Presenter's recording named %r, wanted 'ZOOM0001.WAV (2)'; the "
      "line: %r" % (second, second_line))

print("\n3. Without typed names, the guess")
_a, guessed, _m = vpm.run_argv({
    "files": [(RECS[0], "audio"), (RECS[1], "audio"), (CAM, "video")],
    "rows": [{"blocks": [RECS[0], MORE], "speakers": "",
              "camera_choice": ""},
             {"blocks": [RECS[1]], "speakers": "", "camera_choice": ""}],
    "cameras": [{"path": CAM, "name": "C0001"}],
    "clip_kinds": {}, "out_folder": OUT, "multitrack": False,
    "production": "Pilot", "cut": {}, "wide_at_edges": False,
    "key": ""}, ASSIGN)
names = [t.get("speakers") for t in (guessed or {}).get("tracks_of", [])]
check("the window's plan guesses two speakers, the second (2)",
      names == ["ZOOM", "ZOOM (2)"],
      "speakers %r, wanted ['ZOOM', 'ZOOM (2)']" % (names,))
p = subprocess.run(
    [sys.executable, SCRIPT, RECS[0], RECS[1], CAM, "--dry-run",
     "--out", OUT, "--without-auphonic", "--no-metrics",
     "--no-speech-recognition", "--no-transcript-file"],
    capture_output=True, text=True, env=ENV)
bare = (p.stdout or "") + (p.stderr or "")
second, second_line = recording_in_plan(bare, "ZOOM (2)")
check("the command line guesses card B a speaker of its own, (2)",
      second == "ZOOM0001.WAV (2)",
      "'ZOOM (2)' plays %r, wanted 'ZOOM0001.WAV (2)'; returned %d, last "
      "line: %s" % (second, p.returncode, (bare.replace(D, "<tmp>")
                                           .strip().splitlines()
                                           or [""])[-1][-120:]))
first, first_line = recording_in_plan(bare, "ZOOM")
check("and card A's continuation in its folder still joins card A",
      first == "ZOOM0001.WAV  (+1)",
      "'ZOOM' plays %r, wanted 'ZOOM0001.WAV  (+1)'; the line: %r"
      % (first, first_line))

print("\n4. A guess joins within one folder, never across")
# Two more cards. Card C's recorder stopped and started again: ZOOM0005
# after ZOOM0001 is no seamless continuation, only the same guess. Card
# D's recorder wrote another number, which guesses the same speaker.
C1, C5 = (os.path.join(D, "CardC", n) for n in ("ZOOM0001.WAV",
                                                  "ZOOM0005.WAV"))
D3 = os.path.join(D, "CardD", "ZOOM0003.WAV")
for path, cut in ((C1, "40"), (C5, "10"), (D3, "40")):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-t", cut,
                    "-c:a", "pcm_s16le", path], check=True)
_a, guessed, _m = vpm.run_argv({
    "files": [(C1, "audio"), (D3, "audio"), (CAM, "video")],
    "rows": [{"blocks": [C1], "speakers": "", "camera_choice": ""},
             {"blocks": [D3], "speakers": "", "camera_choice": ""}],
    "cameras": [{"path": CAM, "name": "C0001"}],
    "clip_kinds": {}, "out_folder": OUT, "multitrack": False,
    "production": "Pilot", "cut": {}, "wide_at_edges": False,
    "key": ""}, ASSIGN)
names = [t.get("speakers") for t in (guessed or {}).get("tracks_of", [])]
check("the window's plan guesses two file names in two folders apart",
      names == ["ZOOM", "ZOOM (2)"],
      "speakers %r, wanted ['ZOOM', 'ZOOM (2)']" % (names,))
p = subprocess.run(
    [sys.executable, SCRIPT, C1, C5, D3, CAM, "--dry-run",
     "--out", OUT, "--without-auphonic", "--no-metrics",
     "--no-speech-recognition", "--no-transcript-file"],
    capture_output=True, text=True, env=ENV)
bare = (p.stdout or "") + (p.stderr or "")
second, second_line = recording_in_plan(bare, "ZOOM (2)")
check("the command line guesses card D's other number a speaker apart",
      second == "ZOOM0003.WAV",
      "'ZOOM (2)' plays %r, wanted 'ZOOM0003.WAV'; returned %d, last "
      "line: %s" % (second, p.returncode, (bare.replace(D, "<tmp>")
                                           .strip().splitlines()
                                           or [""])[-1][-120:]))
first, first_line = recording_in_plan(bare, "ZOOM")
check("a stopped recording in one folder still joins across its gap",
      first == "ZOOM0001.WAV  (+1)",
      "'ZOOM' plays %r, wanted 'ZOOM0001.WAV  (+1)'; the line: %r"
      % (first, first_line))
# Typed alike on card A and card B, the owner says one person: that
# joins across folders, card A's continuation with it.
p = subprocess.run(
    [sys.executable, SCRIPT, RECS[0], MORE, RECS[1], CAM, "--dry-run",
     "--out", OUT, "--without-auphonic", "--no-metrics",
     "--no-speech-recognition", "--no-transcript-file",
     "--speaker-name", RECS[0], "Guest", "--speaker-name", RECS[1], "Guest"],
    capture_output=True, text=True, env=ENV)
typed = (p.stdout or "") + (p.stderr or "")
joined, joined_line = recording_in_plan(typed, "Guest")
check("one name typed on two folders joins them into one track",
      joined == "ZOOM0001.WAV  (+2)",
      "'Guest' plays %r, wanted 'ZOOM0001.WAV  (+2)'; returned %d, the "
      "line: %r" % (joined, p.returncode, joined_line))
summary = [x.strip() for x in typed.splitlines() if "In summary" in x]
check("and the summary counts the recordings joined, not their blocks",
      summary == ["In summary: Guest from 2 recordings"],
      "summary lines %r, wanted ['In summary: Guest from 2 recordings']"
      % (summary,))

shutil.rmtree(D, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
