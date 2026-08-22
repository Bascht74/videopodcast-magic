"""The new preflight checks: timecode comparison and chains."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys, subprocess
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
m = importlib.util.module_from_spec(spec); sys.modules["vpm"] = m
spec.loader.exec_module(m)

def line(finding):
    return "%-8s %-22s %s" % (finding.kind, finding.field, finding.text[:70])

print("== tc comparison: recorder at 00:00:48, cameras at 17:14 ==")
data = [{"name": "Full-Mix-016_Zoom.wav", "path": "/x/zoom.wav",
          "tc": 48.0, "duration": 5216.0},
         {"name": "Guest_0007A.wav", "path": "/x/guest.wav",
          "tc": 61676.0, "duration": 4100.0},
         {"name": "Hosts_C002.mov", "path": "/x/c002.mov",
          "tc": 62065.0, "duration": 4128.0},
         {"name": "Wide_C007.mov", "path": "/x/c007.mov",
          "tc": 62053.0, "duration": 4132.0}]
out = m.timecode_comparison(data)
for finding in out:
    print("  ", line(finding), "| file:", finding.file)
assert len(out) == 1 and out[0].file == "/x/zoom.wav", out
print("   -> exactly the Zoom file, nothing else")

print("\n== tc comparison: all clean ==")
clean = [dict(d) for d in data]
clean[0]["tc"] = 61600.0
assert m.timecode_comparison(clean) == [], "must report nothing"
print("   -> no report")

print("\n== tc comparison: too few with timecode ==")
assert m.timecode_comparison(data[:2]) == [], "with two nothing is decidable"
print("   -> no report")

print("\n== Chains instead of files for the bleed ==")
D = "/tmp/chaintest"
os.makedirs(D, exist_ok=True)
names = []
for stem, blocks, audio in (("Host", 3, 300), ("Co-host", 4, 440),
                            ("Guest", 1, 620)):
    for i in range(blocks):
        p = "%s/%s_REC%05d.wav" % (D, stem, 5 + i)
        if not os.path.exists(p):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                            "-i", "sine=frequency=%d:duration=4" % audio,
                            "-ar", "48000", "-ac", "1", p], check=True)
        names.append(p)
print("   Files:", len(names))
chains = m.group_recording_parts(names)
print("   Recordings:", len(chains),
      [os.path.basename(r[0]) for r, _ in chains])
assert len(chains) == 3, chains
pairs_file = len(names) * (len(names) - 1)
pairs_chain = len(chains) * (len(chains) - 1)
print("   Pairs before %d, after %d" % (pairs_file, pairs_chain))
assert pairs_chain < pairs_file

print("\n== The finding carries the file ==")
findings, d = m.measure_cached(names[0], "audio", m.check_audio_file,
                               fresh=True)
assert all(x.file == os.path.abspath(names[0]) for x in findings), findings
print("   ->", os.path.basename(findings[0].file), "on all",
      len(findings), "findings")
print("   data:", {k: d[k] for k in ("name", "rate", "channel_count")})
print("\nall good")
