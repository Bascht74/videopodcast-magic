# -*- coding: utf-8 -*-
"""A track that begins after the picture is placed where the file says.

Raw samples carry no clock, so whatever ffmpeg hands back used to be
taken for the beginning of the file -- while a camera track can begin a
moment after the picture, and an AAC stream begins with samples the
file marks as not to be played. Material built here out of one
uncompressed signal: the same signal written with the picture and
written 2898 samples later, once uncompressed and once as AAC.
The blocks: what the file says the track begins at, where the decoded
samples land, and what the check "Full-Mix against the camera track"
reports over a written file whose two tracks begin at different times.
The limit: a file that does not declare its AAC lead-in cannot be put
right by anybody, because the number is not in it.
"""
import contextlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")

import importlib.util

spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
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


# The numbers this test is about, written out rather than computed: the
# ones measured on 2.9.2026 at a camera whose sound sat 1.4 frames in
# front of its picture.
RATE = 48000
LATE_SAMPLES = 2898
LATE_S = 0.060375           # 2898 / 48000
SECONDS = 20
FPS = 24.0                  # one frame is 41.7 ms, so 60 ms is more than one

folder = tempfile.mkdtemp(prefix="vpm_startslate_")
PLAIN = os.path.join(folder, "signal.wav")
LATE_PCM = os.path.join(folder, "WideCam_late.mov")
ON_TIME_PCM = os.path.join(folder, "WideCam_on_time.mov")
ON_TIME_AAC = os.path.join(folder, "Presenter_on_time.m4a")
LATE_AAC = os.path.join(folder, "Presenter_late.mov")
WRITTEN = os.path.join(folder, "Guest_written.mov")


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + list(args),
                   check=True, capture_output=True)


def build():
    """One signal, and the five files made out of it."""
    t = np.arange(SECONDS * RATE) / float(RATE)
    x = np.zeros(len(t), dtype=np.float64)
    rs = np.random.RandomState(11)
    # Bursts of noise with silence between them: an onset a threshold
    # can find to the sample, and a shape a correlation can bite on.
    for k in range(0, SECONDS, 2):
        a = int((k + 0.5) * RATE)
        x[a:a + int(0.2 * RATE)] = rs.normal(0, 0.3, int(0.2 * RATE))
    raw = (np.clip(x, -1, 1) * 32000).astype("<i2")
    with wave.open(PLAIN, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(raw.tobytes())
    # Uncompressed, copied into a container that says the track begins
    # LATE_S after the picture. Nothing is re-encoded, so the samples
    # are the same ones and only their time changes.
    ffmpeg("-itsoffset", "%.6f" % LATE_S, "-i", PLAIN, "-c:a", "copy",
           LATE_PCM)
    ffmpeg("-i", PLAIN, "-c:a", "copy", ON_TIME_PCM)
    # The same signal as AAC, which brings a lead-in of its own that the
    # file declares, and the same stream moved by LATE_S.
    ffmpeg("-i", PLAIN, "-c:a", "aac", "-b:a", "128k", ON_TIME_AAC)
    ffmpeg("-itsoffset", "%.6f" % LATE_S, "-i", ON_TIME_AAC, "-c:a", "copy",
           LATE_AAC)
    # What a run writes: the overall mix on track one, the camera track
    # on track two. The camera track begins LATE_S in and has lost
    # exactly that much at its head, so on the axis the two are level --
    # which is what the check is there to find out.
    cut = os.path.join(folder, "camera_track.wav")
    with wave.open(cut, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(raw[LATE_SAMPLES:].tobytes())
    ffmpeg("-i", PLAIN, "-itsoffset", "%.6f" % LATE_S, "-i", cut,
           "-map", "0:a", "-map", "1:a", "-c:a", "copy", WRITTEN)


def onset(x, level=0.05):
    """Where the first burst begins, in samples.

    Not the program's road: the program lines two curves up against
    each other, this one asks the samples themselves where the silence
    stops.
    """
    loud = np.nonzero(np.abs(x) > level)[0]
    return int(loud[0]) if len(loud) else -1


build()
QUIET = int(0.5 * RATE)        # where the first burst sits in the signal

print("1. What the file says")
# What ffmpeg writes is rounded to its own grid, and the grid is not
# the same on every build -- 2898 samples here, 2880 on the builder. So
# the file is asked what it says, and everything below is held against
# that answer. The claim is that the program follows the file, not that
# ffmpeg hits a number.
says_late = vpm.audio_track_starts_at(LATE_PCM)
SAYS = int(round(says_late * RATE))
check("the file says a late uncompressed track begins after the picture",
      abs(says_late - LATE_S) < 0.002,
      "the file says %.6f s, asked for %.6f s (%d samples)"
      % (says_late, LATE_S, SAYS))
says_zero = vpm.audio_track_starts_at(ON_TIME_AAC)
check("the file says an AAC track written with the picture begins at "
      "zero", abs(says_zero) < 1e-6,
      "the file says %.6f s, wanted 0.000000 s" % says_zero)

print("\n2. Where the decoded samples land")
plain = vpm.decode_audio(PLAIN, rate=RATE)
late_pcm = vpm.decode_audio(LATE_PCM, rate=RATE)
on_time_pcm = vpm.decode_audio(ON_TIME_PCM, rate=RATE)
late_aac = vpm.decode_audio(LATE_AAC, rate=RATE)
on_time_aac = vpm.decode_audio(ON_TIME_AAC, rate=RATE)
moved = onset(late_pcm) - onset(plain)
check("a late uncompressed track lands where the file says",
      moved == SAYS,
      "the burst sits %d samples further in, the file says %d (%d "
      "against %d)" % (moved, SAYS, onset(late_pcm), onset(plain)))
moved_aac = onset(late_aac) - onset(on_time_aac)
# AAC lands on its own frame grid, so it may miss the mark by a
# handful of samples where the uncompressed one hits it exactly.
# Measured: 2 samples here, 16 on the builder -- a third of a
# millisecond, far under one picture.
AAC_SLACK = 48        # one millisecond at this rate
check("a late AAC track lands as far in as the file says",
      abs(moved_aac - SAYS) <= AAC_SLACK,
      "the burst sits %d samples further in, the file says %d, allowed "
      "%d (%d against %d)" % (moved_aac, SAYS, AAC_SLACK,
                              onset(late_aac), onset(on_time_aac)))
check("a track written with the picture is not moved",
      onset(on_time_pcm) == QUIET,
      "its burst sits at %d, wanted %d" % (onset(on_time_pcm), QUIET))
check("and it comes back with every sample it had",
      len(on_time_pcm) == SECONDS * RATE,
      "%d samples came back, wanted %d" % (len(on_time_pcm),
                                           SECONDS * RATE))

print("\n3. The check over a written file")


class Settings(object):
    """What check_written_file asks its arguments for, and no more."""
    no_camera_audio = False


heard = io.StringIO()
with contextlib.redirect_stdout(heard):
    vpm.check_written_file(WRITTEN, [(vpm.MIX_TRACK_NAME, "")], 1,
                           Settings(), FPS)
told = heard.getvalue()
# The progress bar rewrites its own line, so only what stands after the
# last carriage return of a line was ever meant to be read.
lines = [x.split("\r")[-1] for x in told.split("\n")]
line = next((x for x in lines if " ms " in x and "%" not in x),
            told.replace("\n", " ")[-160:])
found = re.search(r"([+-]\d+) ms", line)
apart = abs(int(found.group(1))) if found else None
check("the check over a written file whose camera track begins late "
      "stays under one frame", apart is not None and apart < 1000.0 / FPS,
      "it reports %s ms against a frame of %.1f ms -- %r"
      % (apart, 1000.0 / FPS, line))
check("and it no longer cautions that the two are more than one frame "
      "apart", vpm.T('   Caution: more than one frame').strip() not in told,
      "the check said %r" % line)

shutil.rmtree(folder, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
