# -*- coding: utf-8 -*-
"""A channel cut out of a recorder file keeps the time it was recorded at.

A recorder writes the start of its take into the bext chunk, counted in
samples at its own rate. split_channels writes one channel into a file
of its own, and that stamp has to go with it, or the piece lands at
zero and a real pause is swallowed. The source is four channels at
44.1 kHz starting at one hour, written here. In order: the source
carries its stamp, a piece at the same rate carries the same number,
and a piece written at 48 kHz carries the same hour counted at 48 kHz.
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


# One hour, in samples at the two rates.
HOUR_44 = 158760000
HOUR_48 = 172800000

folder = tempfile.mkdtemp(prefix="vpm_splitstamp_")
source = os.path.join(folder, "TAKE_0001.WAV")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "sine=frequency=300:duration=0.5:sample_rate=44100",
                "-af", "pan=4c|c0=c0|c1=0.5*c0|c2=0.25*c0|c3=0.1*c0",
                "-c:a", "pcm_s24le", "-write_bext", "1",
                "-metadata", "time_reference=%d" % HOUR_44, source],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

stamp = vpm.bext_time_reference(source) if os.path.exists(source) else None
check("the recorder file carries its stamp", stamp == HOUR_44,
      "%r samples, wanted %d" % (stamp, HOUR_44))

same = vpm.split_channels(source, (2,), os.path.join(folder, "same.wav"))
got = vpm.bext_time_reference(same) if os.path.exists(same) else None
check("a piece at the recorder's rate keeps the stamp", got == HOUR_44,
      "%r samples, wanted %d" % (got, HOUR_44))

other = vpm.split_channels(source, (2,), os.path.join(folder, "other.wav"),
                           rate=48000)
got = vpm.bext_time_reference(other) if os.path.exists(other) else None
check("a piece at 48 kHz carries the same hour counted at 48 kHz",
      got == HOUR_48, "%r samples, wanted %d" % (got, HOUR_48))

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
