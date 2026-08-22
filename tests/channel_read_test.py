# -*- coding: utf-8 -*-
"""Reading the channels: one pass has to say what one pass per channel said.

Asking ffmpeg for channel k with a pan filter decodes the whole file
again for every channel -- a 32 channel recording was read 32 times
over, which on a mixer file is most of the waiting. Everything now comes
out of one pass and is taken apart afterwards. That is only allowed if
the numbers do not move, so this test reads the same file both ways and
holds them against each other.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, subprocess, sys, tempfile, time, wave
import numpy as np
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
WORK = tempfile.mkdtemp(prefix="chanread_")
bad = []


def check(what, ok, detail=""):
    print("  %-56s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


def build(name, channels, seconds=3, rate=48000, width=2):
    """A file whose channels are each a different tone, silence among them."""
    t = np.arange(int(rate * seconds)) / float(rate)
    rows = []
    for c in range(channels):
        if c % 5 == 3:
            rows.append(np.zeros_like(t))          # an unused input
        else:
            rows.append(0.4 * np.sin(2 * np.pi * (200 + 97 * c) * t))
    block = (np.stack(rows, axis=1) * 32767).astype("<i2")
    path = os.path.join(WORK, name)
    with wave.open(path, "wb") as f:
        f.setnchannels(channels); f.setsampwidth(width); f.setframerate(rate)
        f.writeframes(block.tobytes())
    return path


def one_by_one(path, rate, n):
    """The old way: one ffmpeg call per channel, with a pan filter."""
    out = []
    for k in range(n):
        p = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", path, "-filter_complex",
             "[0:a:0]pan=mono|c0=c%d[o]" % k, "-map", "[o]", "-ar",
             str(rate), "-f", "f32le", "-"], capture_output=True)
        out.append(np.frombuffer(p.stdout, dtype=np.float32))
    return out


print("1. Eight channels, read both ways")
path = build("eight.wav", 8)
rate = vpm.channel_rate(path, 8)
t0 = time.time()
mine = vpm.channel_levels(path, rate)
one_pass = time.time() - t0
t0 = time.time()
theirs = one_by_one(path, rate, 8)
per_channel = time.time() - t0
print("   one pass %.2f s, one call per channel %.2f s"
      % (one_pass, per_channel))
check("eight channels come back", len(mine) == 8, str(len(mine)))
check("each the same length as before",
      [len(x) for x in mine] == [len(x) for x in theirs],
      "%s vs %s" % ([len(x) for x in mine], [len(x) for x in theirs]))
worst = max(float(np.max(np.abs(a - b))) for a, b in zip(mine, theirs))
check("and the samples are the same", worst < 1e-6, "worst %.2e" % worst)

print("\n2. The channels do not get mixed up")
# The one that matters: channel k has to be channel k. A reshape with
# the wrong width would still give eight arrays of the right length.
for k in (0, 3, 7):
    peak = np.abs(np.fft.rfft(mine[k] * np.hanning(len(mine[k]))))
    hz = np.fft.rfftfreq(len(mine[k]), 1.0 / rate)[int(np.argmax(peak))]
    want = 0.0 if k % 5 == 3 else 200 + 97 * k
    check("channel %d carries its own tone" % (k + 1),
          (want == 0 and float(np.max(np.abs(mine[k]))) < 1e-6)
          or abs(hz - want) < 25, "%.0f Hz, wanted %.0f" % (hz, want))

print("\n3. A single channel file still works")
mono = build("mono.wav", 1)
rows = vpm.channel_levels(mono, vpm.channel_rate(mono, 1))
check("one row", len(rows) == 1, str(len(rows)))
check("and it holds something", float(np.max(np.abs(rows[0]))) > 0.1)

print("\n4. An unreadable file gives nothing, not a traceback")
broken = os.path.join(WORK, "broken.wav")
open(broken, "wb").write(b"not a wav")
try:
    rows = vpm.channel_levels(broken, 16000)
    check("no rows with anything in them",
          all(len(x) == 0 for x in rows), str([len(x) for x in rows]))
except Exception as e:
    check("no rows with anything in them", False, repr(e))

print("\n4b. An ffmpeg that dies is not taken for one that finished")
# Half a file read is worse than none: the judgement would be made on
# the part that arrived, and channel_facts_cached stores it under the
# file's size and time, so it would never be measured again. A stand-in
# ffmpeg that writes a little and then fails proves the return code is
# looked at.
fake = os.path.join(WORK, "bin")
os.makedirs(fake, exist_ok=True)
with open(os.path.join(fake, "ffmpeg"), "w") as f:
    f.write("#!/bin/sh\n"
            "head -c 40000 /dev/zero\n"
            "echo 'Error while decoding stream' >&2\n"
            "exit 1\n")
os.chmod(os.path.join(fake, "ffmpeg"), 0o755)
was = os.environ["PATH"]
os.environ["PATH"] = fake + os.pathsep + was
try:
    rows = vpm.channel_levels(path, rate)
    check("nothing comes back from a failed read",
          all(len(x) == 0 for x in rows), str([len(x) for x in rows]))
    facts = vpm.channel_facts(path)
    check("and the file counts as unreadable, not as judged",
          facts["readable"] is False, str(facts.get("readable")))
finally:
    os.environ["PATH"] = was
check("with the real ffmpeg back it reads again",
      len(vpm.channel_levels(path, rate)[0]) > 0)

print("\n5. The judgement over the whole file is unchanged")
facts = vpm.channel_facts(path)
check("eight channels judged", facts["channels"] == 8, str(facts["channels"]))
check("the empty one is found",
      [k for k, x in enumerate(facts["silent"]) if x] == [3],
      str(facts["silent"]))
check("and every neighbour has an answer",
      len(vpm.channel_joins(facts)) == 7,
      str(len(vpm.channel_joins(facts))))

print()
if bad:
    print("FAIL: %d of the checks" % len(bad))
    sys.exit(1)
print("all checks passed")
