"""Does the preflight compare recordings instead of blocks?"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys, subprocess
sys.path.insert(0, os.path.dirname(
    os.path.abspath(__file__)))
from fixture_root import fixture
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
m = importlib.util.module_from_spec(spec); sys.modules["vpm"] = m
spec.loader.exec_module(m)

D = fixture("lengthtest")
os.makedirs(D, exist_ok=True)
# Rebuild: two recordings in several blocks, plus a single-block one that
# is as long as the chains together.
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

chains = m.group_recording_parts(every)
print("Files %d, recordings %d" % (len(every), len(chains)))
data = []
for p in every:
    _b, d = m.measure_cached(p, "audio", m.check_audio_file, fresh=True)
    data.append(d)
recordings = m.by_recording(data, chains)
for a in recordings:
    print("   %-26s %6.1f s" % (a["name"], a["duration"]))
assert len(recordings) == 3
by_name = {a["name"].split("_")[0]: a["duration"] for a in recordings}
assert abs(by_name["Host"] - 28) < 1.0, by_name
assert abs(by_name["Co-host"] - 40) < 1.0, by_name
assert abs(by_name["Guest"] - 31) < 1.0, by_name
print("   -> the lengths are those of the recordings")

print("\nFindings from the comparison:")
out = m.compare_audio_tracks(recordings)
for finding in out:
    print("   %-8s %-22s %s"
          % (finding.kind, finding.field, finding.text[:70]))
assert not out, "no recording is shorter than half the longest"
print("   -> no false report")

print("\nCross-check with blocks (the old way):")
old = m.compare_audio_tracks(data)
for finding in old:
    print("   %-8s %-22s %s"
          % (finding.kind, finding.field, finding.text[:70]))
assert old, "the old way would have complained here"
print("   -> would have wrongly reported %d blocks" % len(old))
print("\nall good")
