"""Does the preflight compare recordings instead of blocks?

A recording arrives in numbered blocks, and the length that counts is
those blocks added up. In order: the blocks are grouped into recordings
and each recording is as long as its own blocks together; the
comparison then reports none of them as short against the longest; and
the same comparison over the single blocks does report them, so the
answer before it is not green for want of anything to find.

The material is built once into the shared fixture folder and reused
from there, so a run measures the program and not ffmpeg.
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")

import importlib.util

sys.path.insert(0, HERE)
from fixture_root import fixture

began = time.time()
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
m = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = m
spec.loader.exec_module(m)

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


D = fixture("lengthtest")
os.makedirs(D, exist_ok=True)
# Two recordings in several blocks, plus a single-block one that is as
# long as the chains together.
plan = [("Host", [10, 10, 8], 300),
        ("Co-host", [10, 10, 10, 10], 440),
        ("Guest", [31], 620)]
every = []
for stem, lengths, audio in plan:
    for i, sec in enumerate(lengths):
        p = "%s/%s_REC%05d.wav" % (D, stem, 5 + i)
        if not os.path.exists(p):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                            "-i", "sine=frequency=%d:duration=%d"
                            % (audio, sec),
                            "-ar", "48000", "-ac", "1", p], check=True)
        every.append(p)
# A precondition of the material, not a judgement about the program:
# where ffmpeg wrote no file there is nothing to measure, and every
# length below would be nonsense rather than wrong.
missing = [p for p in every if not os.path.exists(p)]
assert len(every) == 8 and not missing, (
    "material: 8 blocks planned, %d built, missing %s"
    % (len(every) - len(missing), [os.path.basename(x) for x in missing]))

print("1. Eight blocks become three recordings")
chains = m.group_recording_parts(every)
data = []
for p in every:
    _b, d = m.measure_cached(p, "audio", m.check_audio_file, fresh=True)
    data.append(d)
recordings = m.by_recording(data, chains)
for a in recordings:
    print("   %-26s %6.1f s" % (a["name"], a["duration"]))
check("eight blocks are grouped into three recordings",
      len(recordings) == 3,
      "wanted 3 recordings out of %d blocks, %d chains grouped, found %d"
      % (len(every), len(chains), len(recordings)))

print("\n2. A recording is as long as its blocks together")
by_name = {a["name"].split("_")[0]: a["duration"] for a in recordings}
# 0.0 where the name is not there at all. The check above has then
# already fallen and names the first thing that was wrong.
check("a recording of three blocks is as long as the three together",
      abs(by_name.get("Host", 0.0) - 28.0) < 1.0,
      "Host: wanted 28.00 s from blocks 10+10+8, found %.2f s"
      % by_name.get("Host", 0.0))
check("a recording of four blocks is as long as the four together",
      abs(by_name.get("Co-host", 0.0) - 40.0) < 1.0,
      "Co-host: wanted 40.00 s from blocks 10+10+10+10, found %.2f s"
      % by_name.get("Co-host", 0.0))
check("a recording of one block is as long as that block",
      abs(by_name.get("Guest", 0.0) - 31.0) < 1.0,
      "Guest: wanted 31.00 s from one block of 31, found %.2f s"
      % by_name.get("Guest", 0.0))

print("\n3. What the comparison says about the recordings")
out = m.compare_audio_tracks(recordings)
for finding in out:
    print("   %-8s %-22s %s"
          % (finding.kind, finding.field, finding.text[:70]))
check("no recording is reported short against the longest",
      not out,
      "wanted 0 reports over %d recordings of 28.0, 40.0 and 31.0 s, "
      "found %d: %s"
      % (len(recordings), len(out), [f.field for f in out]))

print("\n4. The same comparison over the single blocks")
old = m.compare_audio_tracks(data)
for finding in old:
    print("   %-8s %-22s %s"
          % (finding.kind, finding.field, finding.text[:70]))
check("the same comparison over single blocks does report them short",
      len(old) > 0,
      "wanted at least 1 report over %d blocks, the shortest 8.0 s "
      "against a longest of 31.0 s, found %d" % (len(data), len(old)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
