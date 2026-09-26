# -*- coding: utf-8 -*-
"""A file ffprobe cannot read is named so, and the run goes on without it.

One dry run on the command line over two recordings of one noise and two
files ffprobe cannot open: a WAV whose header names no channels, which
leaves ffprobe half an answer, and one holding no media at all. The
sections: the run ends in its own words and returns 0; the preflight
names each of the two as not readable, with ffprobe's reason and never
a JSON parser's; a readable recording beside them is described as ever.
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
import re
import struct
import subprocess
import tempfile
import time

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


# A dry run over eight seconds of sound ends within seconds here; the
# bound only names a run that never ends, well before run.sh would.
ASK = 240.0
D = tempfile.mkdtemp(prefix="vpm_unreadable_")
OUT = tempfile.mkdtemp(prefix="vpm_unreadable_out_")
host = os.path.join(D, "Host_0001.wav")
guest = os.path.join(D, "Guest_0001.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "anoisesrc=d=8:c=pink:r=48000:a=0.3:s=7", "-ac", "1", host],
               check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", host,
                "-af", "volume=0.5", guest], check=True)
# A RIFF header like any other, but naming no channels: ffprobe opens
# the JSON answer, fails on the decoder and leaves it half written.
no_channels = os.path.join(D, "Mixer_0001.wav")
body = b"\0" * 9600
with open(no_channels, "wb") as f:
    f.write(b"RIFF" + struct.pack("<I", 36 + len(body)) + b"WAVE"
            + b"fmt " + struct.pack("<IHHIIHH", 16, 1, 0, 48000, 96000, 2, 16)
            + b"data" + struct.pack("<I", len(body)) + body)
no_media = os.path.join(D, "Room_0001.wav")
with open(no_media, "w") as f:
    f.write("these bytes are no recording\n")

env = dict(os.environ, QT_QPA_PLATFORM="offscreen",
           VPM_CACHE=tempfile.mkdtemp(prefix="vpm_unreadable_cache_"))
try:
    kid = subprocess.run(
        [sys.executable, SCRIPT, "--multitrack", "--dry-run",
         "--without-auphonic", "--out", OUT, "--no-metrics",
         "--no-speech-recognition", "--no-transcript-file",
         guest, host, no_channels, no_media],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=ASK,
        env=env)
    code, said = kid.returncode, kid.stdout.decode("utf-8", "replace")
except subprocess.TimeoutExpired:
    code, said = None, "no end within %.0f s" % ASK
said = re.sub(r"\x1b\[[0-9;]*m", "", said).replace("\r", "\n")
lines = [x.strip() for x in said.splitlines() if x.strip()]


def preflight_line(name):
    """The preflight's first line about that file, or ""."""
    return next((x for x in lines if x.startswith(name + " ")), "")


NOT_READABLE = vpm.T('not readable')
PARSER = ("Expecting", "column", "char ", "JSONDecodeError")

print("1. The run over two unreadable files")
check("the run over an unreadable file ends without a traceback",
      "Traceback" not in said,
      "last line %r" % (lines[-1][:70] if lines else "nothing said"))
check("and returns 0, the unreadable files left out", code == 0,
      "returned %s, last line %r"
      % (code, lines[-1][:60] if lines else "nothing said"))

print("\n2. The preflight names both, in ffprobe's words")
for_mixer = preflight_line("Mixer_0001.wav")
check("the preflight calls a WAV with no channels not readable",
      NOT_READABLE in for_mixer, "its line %r" % for_mixer[:90])
reason = for_mixer.split(NOT_READABLE, 1)[-1].lstrip(": ")
check("its line gives ffprobe's reason, not a parser's",
      bool(reason) and not any(p in for_mixer for p in PARSER),
      "reason %r in %r" % (reason[:40], for_mixer[:90]))
for_room = preflight_line("Room_0001.wav")
check("a file holding no media is named not readable too",
      NOT_READABLE in for_room, "its line %r" % for_room[:90])

print("\n3. A readable recording beside them")
for_host = preflight_line("Host_0001.wav")
# As it was built: 48 kHz, 16 bit, one channel, eight seconds.
DESCRIBED = vpm.T('%s kHz, %s bit, %s, %s') % (
    "48", "16", vpm.channel_text(1), vpm.as_hms(8.0))
check("a readable recording is described, not called unreadable",
      for_host.endswith(DESCRIBED) and NOT_READABLE not in for_host,
      "its line %r" % for_host[:90])

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
