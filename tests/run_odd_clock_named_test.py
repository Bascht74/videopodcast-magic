# -*- coding: utf-8 -*-
"""A clock that was never set is found, and blocks group as recordings."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, shutil, subprocess, sys, tempfile, time
began = time.time()
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
m = importlib.util.module_from_spec(spec); sys.modules["vpm"] = m
spec.loader.exec_module(m)

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def line(finding):
    return "%-8s %-22s %s" % (finding.kind, finding.field, finding.text[:70])


print("1. tc comparison: recorder at 00:00:48, cameras at 17:14")
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
one = len(out) == 1
check("one file of the four is reported", one,
      "%d reported: %s" % (len(out), [f.field for f in out]))
check("and it is the recorder standing apart", one
      and out[0].file == "/x/zoom.wav",
      out[0].file if out else "nothing reported")
check("said as a hint, not as a fault", one and out[0].kind == "hint",
      out[0].kind if out else "nothing reported")
check("the field names the file it is about", one
      and out[0].field == "Full-Mix-016_Zoom",
      repr(out[0].field) if out else "nothing reported")
check("the text carries both clocks", one
      and "00:00:48:00" in out[0].text and "17:14:13:00" in out[0].text,
      out[0].text[:46] if out else "nothing reported")

print("\n2. tc comparison: all clean")
clean = [dict(d) for d in data]
clean[0]["tc"] = 61600.0
quiet = m.timecode_comparison(clean)
check("clocks within minutes of each other: no report", quiet == [],
      "%d reported: %s" % (len(quiet), [f.field for f in quiet]))

print("\n3. tc comparison: too few with timecode")
two = m.timecode_comparison(data[:2])
check("with two files nothing is decidable", two == [],
      "%d reported: %s" % (len(two), [f.field for f in two]))

print("\n4. Chains instead of files for the bleed")
D = tempfile.mkdtemp(prefix="vpm_preflight_")
names = []
for stem, blocks, audio in (("Host", 3, 300), ("Co-host", 4, 440),
                            ("Guest", 1, 620)):
    for i in range(blocks):
        p = "%s/%s_REC%05d.wav" % (D, stem, 5 + i)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                        "-i", "sine=frequency=%d:duration=4" % audio,
                        "-ar", "48000", "-ac", "1", p], check=True)
        names.append(p)
chains = m.group_recording_parts(names)
print("   Recordings:", [os.path.basename(r[0]) for r, _ in chains])
blocks_of = sorted(len(r) for r, _ in chains)
check("eight blocks make three recordings", len(chains) == 3,
      "%d recordings from %d files" % (len(chains), len(names)))
check("every block lands in one, and none is lost",
      blocks_of == [1, 3, 4], "blocks per recording: %s" % blocks_of)
check("each recording begins at its first block",
      all(os.path.basename(r[0]).endswith("REC00005.wav")
          for r, _ in chains),
      str([os.path.basename(r[0]) for r, _ in chains])[:44])
pairs_file = len(names) * (len(names) - 1)
pairs_chain = len(chains) * (len(chains) - 1)
check("and far fewer pairs are compared", pairs_chain < pairs_file,
      "%d pairs before, %d after" % (pairs_file, pairs_chain))

print("\n5. The finding carries the file")
findings, d = m.measure_cached(names[0], "audio", m.check_audio_file,
                               fresh=True)
check("every finding names the file it came off",
      bool(findings) and all(x.file == os.path.abspath(names[0])
                             for x in findings),
      "%d findings, %s" % (len(findings), os.path.basename(
          findings[0].file) if findings else "none"))
check("a readable file is described, not faulted",
      bool(findings) and all(x.kind == "good" for x in findings),
      str(sorted({x.kind for x in findings})))
check("the data carry the file's own name",
      d.get("name") == os.path.basename(names[0]), repr(d.get("name")))
check("the rate is the 48000 Hz it was built at",
      d.get("rate") == 48000, "%s Hz" % d.get("rate"))
check("one channel, as it was recorded",
      d.get("channel_count") == 1, "%s channels" % d.get("channel_count"))
check("the length is the four seconds it holds",
      abs((d.get("duration") or 0.0) - 4.0) < 0.1,
      "%.2f s" % (d.get("duration") or 0.0))

shutil.rmtree(D, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
