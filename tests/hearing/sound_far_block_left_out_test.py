# -*- coding: utf-8 -*-
"""A block past the block limit per timecode is left out of the join, and said.

Three ten-second blocks with their start written the way a recorder
writes it: the second a minute inside the program's own limit after the
first, the third a minute past it after the second. Joined, the far one
is left out, the file holds the first two and the pause between them
and not the hours after, the far one is named with its distance, the
pause inside the limit is still filled -- and block detection, asked
from the first file, keeps exactly the blocks the join keeps. Last, a
pair of the first and the far one goes through the plan's join: the
track made of it lists the one block that was kept.
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
import contextlib, io, shutil, subprocess, tempfile, time

began = time.time()
vpm = the_program.load()
vpm.set_language("en")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# The limit is the program's, not written down here twice. Eight kHz
# keeps the pause of half an hour a file of some forty megabytes.
LIMIT = float(vpm.BLOCK_GAP_MAX_S)
RATE = 8000
NEAR = LIMIT - 60.0
FAR = LIMIT + 60.0
D = tempfile.mkdtemp(prefix="vpm_farblock_")
STARTS = {"REC0001": 0.0, "REC0002": 10.0 + NEAR,
          "REC0003": 10.0 + NEAR + 10.0 + FAR}
build = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
         "sine=frequency=440:duration=10:sample_rate=%d" % RATE]
for name, start in STARTS.items():
    build += ["-map", "0:a", "-c:a", "pcm_s16le", "-write_bext", "1",
              "-metadata", "time_reference=%d" % int(start * RATE),
              os.path.join(D, name + ".wav")]
subprocess.run(build, check=True)
paths = [os.path.join(D, n + ".wav") for n in sorted(STARTS)]

said = io.StringIO()
with contextlib.redirect_stdout(said):
    source, info = vpm.join_with_report(paths, os.path.join(D, "joined.wav"))
said = said.getvalue()
lines = [x.strip() for x in said.splitlines()]
length = float(subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
     "-of", "csv=p=0", source], capture_output=True, text=True)
    .stdout.strip() or 0)

print("Three blocks, the last one past the limit of %.0f s" % LIMIT)
dropped = [n for n, _far in info.get("dropped", [])]
check("a block past the limit per timecode is left out of the join",
      info["blocks"] == 2 and dropped == ["REC0003.wav"],
      "%d blocks joined, left out %s; wanted 2 and ['REC0003.wav']"
      % (info["blocks"], dropped))
wanted = 10.0 + NEAR + 10.0
check("the joined file ends with the near block, not hours later",
      abs(length - wanted) < 0.05,
      "%.3f s long against %.3f s" % (length, wanted))
told = (vpm.T('  %s left out -- %s per timecode away from the other '
              'blocks, too far apart for one recording')
        % ("REC0003.wav", vpm.as_hms(FAR))).strip()
check("the block left out is named with its distance", told in lines,
      "%r %s; the lines were %s"
      % (told, "said" if told in lines else "not said", lines[:4]))
gap = (vpm.T('  Gap of %s at %s -- filled with silence')
       % (vpm.as_hms(NEAR), vpm.as_hms(10.0))).strip()
check("a pause inside the limit is still joined and filled",
      gap in lines,
      "%r %s; the lines were %s"
      % (gap, "said" if gap in lines else "not said", lines[:4]))

print("\nBlock detection from the first file")
row, _discarded = vpm.find_continuation_files(paths[0])
row = [os.path.basename(p) for p in row]
joined = [n + ".wav" for n in sorted(STARTS) if n + ".wav" not in dropped]
check("block detection keeps the blocks the join keeps",
      row == joined == ["REC0001.wav", "REC0002.wav"],
      "detection kept %s, the join %s; wanted both REC0001 and REC0002"
      % (row, joined))

print("\nA far-apart pair in the plan")
pair = [paths[0], paths[2]]
with contextlib.redirect_stdout(io.StringIO()):
    made = vpm.join_the_plan([{"name": "Pair", "audio": pair[0],
                               "blocks": pair}], D)
listed = [os.path.basename(p) for p in made[0]["blocks"]]
check("the plan of a far-apart pair lists only the block it keeps",
      listed == ["REC0001.wav"],
      "the track lists %s; wanted ['REC0001.wav']" % listed)

shutil.rmtree(D, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
