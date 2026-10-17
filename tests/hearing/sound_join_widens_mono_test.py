# -*- coding: utf-8 -*-
"""Blocks of different width join at the widest, mono on both sides.

A recorder that was switched from one input to two between takes leaves
a mono block and a stereo block with no timecode. The concat demuxer
refuses those, so join_audio_parts widens them in a graph first. The
blocks are written here: half a second of mono, then half a second of
stereo. In order: the join is stereo and as long as both blocks, the
mono block stands on both sides at its own level -- not 3 dB down as
ffmpeg's own upmix would put it -- and a single block is handed back
as it is, with nothing written.
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
np = vpm.np

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


RATE = 48000
folder = tempfile.mkdtemp(prefix="vpm_joinwide_")
mono = os.path.join(folder, "TAKE_01.WAV")
stereo = os.path.join(folder, "TAKE_02.WAV")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "sine=frequency=440:duration=0.5:sample_rate=%d" % RATE,
                "-af", "volume=0.5", "-ac", "1", "-c:a", "pcm_s24le", mono],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "sine=frequency=660:duration=0.5:sample_rate=%d" % RATE,
                "-af", "pan=stereo|c0=0.2*c0|c1=0.4*c0",
                "-c:a", "pcm_s24le", stereo],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def samples(path, channels):
    """The file as float rows of *channels*, read by ffmpeg."""
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le",
                        "-"], capture_output=True)
    return np.frombuffer(p.stdout, dtype=np.float32).reshape(-1, channels)


def rms(x):
    return float(np.sqrt(np.mean(np.asarray(x, dtype=np.float64) ** 2)))


target = os.path.join(folder, "joined.wav")
out, info = vpm.join_audio_parts([mono, stereo], target)
facts = vpm.audio_stream_facts(target) if os.path.exists(target) else {}
width = int(facts.get("channels") or 0)
x = samples(target, 2) if width == 2 else np.zeros((0, 2))
check("a mono and a stereo block join as stereo, both lengths long",
      width == 2 and abs(len(x) - RATE) <= 2 and info.get("blocks") == 2,
      "%d channels, %d samples, %r blocks; wanted 2, %d, 2"
      % (width, len(x), info.get("blocks"), RATE))
first = x[RATE // 10:RATE * 4 // 10] if len(x) else np.zeros((0, 2))
source = samples(mono, 1)[RATE // 10:RATE * 4 // 10]
left, right, alone = (rms(first[:, 0]) if len(first) else 0.0,
                      rms(first[:, 1]) if len(first) else 0.0, rms(source))
check("the mono block stands on both sides at its own level",
      alone > 0 and abs(left - alone) < 0.01 * alone
      and abs(right - alone) < 0.01 * alone,
      "left %.4f, right %.4f, the block alone %.4f" % (left, right, alone))

single = os.path.join(folder, "single.wav")
out, info = vpm.join_audio_parts([mono], single)
check("a single block is handed back as it is, nothing written",
      out == mono and info.get("blocks") == 1 and not os.path.exists(single),
      "handed back %s, %r blocks, a file written: %s"
      % (os.path.basename(out), info.get("blocks"), os.path.exists(single)))

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
