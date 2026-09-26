# -*- coding: utf-8 -*-
"""Timecoded blocks in a row are joined whole at 44.1 and 96 kHz too.

A recorder stamps a block in samples at its own rate, and the join lays
the blocks by those stamps. In order: a 96 kHz recording in two blocks
of ten seconds, one straight after the other -- as long as both, no hole
said, the second where its stamp puts it; the same at 44.1 kHz -- as
long as both, not taken for microphones side by side; and two 96 kHz
blocks with ten seconds between them, the hole named with its length.
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
import contextlib, io, json, shutil, subprocess, tempfile, time
import numpy as np

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


D = tempfile.mkdtemp(prefix="vpm_joinrate_")


def block(name, freq, rate, stamp):
    """Ten seconds of one tone at *rate*, stamped *stamp* samples in."""
    path = os.path.join(D, name + ".wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "sine=frequency=%d:sample_rate=%d:duration=10"
                    % (freq, rate), "-c:a", "pcm_s24le", "-write_bext", "1",
                    "-metadata", "time_reference=%d" % stamp, path],
                   check=True)
    return path


def join(name, *blocks):
    """Join the blocks; what was said, the info, and the file's length."""
    target = os.path.join(D, name + "_joined.wav")
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        _src, info = vpm.join_with_report(list(blocks), target)
    probe = json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-show_format", "-of", "json", target],
        stdout=subprocess.PIPE).stdout or b"{}")
    length = float((probe.get("format") or {}).get("duration") or 0.0)
    return said.getvalue(), info, length, target


def second_tone_from(path):
    """Where 880 Hz first outweighs 440 Hz, in steps of 50 ms; None if never."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1",
                          "-ar", "8000", "-f", "f32le", "-"],
                         stdout=subprocess.PIPE).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    for k in range(len(x) // 400):
        # 400 samples at 8 kHz: 20 Hz a bin, 440 in bin 22, 880 in 44.
        bins = np.abs(np.fft.rfft(x[k * 400:(k + 1) * 400]))
        if bins[44] > bins[22]:
            return k * 0.05
    return None


# The program's sentences, cut where their numbers begin.
GAP = vpm.T('  Gap of %s at %s -- filled with silence').split("%s")[0].strip()
OVER = vpm.T('  Overlap of %s at %s -- both sound there').split(
    "%s")[0].strip()


def holes(said):
    """The lines that name a hole or an overlap."""
    return [x.strip() for x in said.splitlines()
            if x.strip().startswith((GAP, OVER))]


print("1. A 96 kHz recording in two blocks, one after the other")
# Stamps written out: 10 s x 96000 is where the second block starts.
said, info, length, joined = join(
    "hi", block("Presenter_REC00021", 440, 96000, 0),
    block("Presenter_REC00022", 880, 96000, 960000))
check("a 96 kHz recording in two blocks is joined as long as both",
      abs(length - 20.0) < 0.001, "%.3f s joined, wanted 20.000 s" % length)
check("and no hole is said between its blocks", not holes(said),
      "said %s, wanted nothing" % holes(said))
at = second_tone_from(joined)
check("the second block starts where its stamp puts it",
      at is not None and abs(at - 10.0) < 0.051,
      "the second block's tone begins at %s, wanted 10.00 s"
      % ("no point" if at is None else "%.2f s" % at))

print("\n2. A 44.1 kHz recording in two blocks, one after the other")
said, info, length, _joined = join(
    "cd", block("Guest_REC00031", 440, 44100, 0),
    block("Guest_REC00032", 880, 44100, 441000))
check("a 44.1 kHz recording in two blocks is joined as long as both",
      abs(length - 20.0) < 0.001, "%.3f s joined, wanted 20.000 s" % length)
check("and its blocks are not taken for microphones side by side",
      not info.get("side_by_side") and not holes(said),
      "side by side: %s, said %s, wanted neither"
      % (info.get("side_by_side"), holes(said)))

print("\n3. Two 96 kHz blocks with ten seconds between them")
said, info, length, _joined = join(
    "gap", block("CoPresenter_REC00041", 440, 96000, 0),
    block("CoPresenter_REC00042", 880, 96000, 1920000))
named = vpm.T('  Gap of %s at %s -- filled with silence').strip() % (
    "0:00:10.000", "0:00:10.000")
check("a hole between 96 kHz blocks is named with its own length",
      holes(said) == [named], "said %s, wanted [%r]" % (holes(said), named))

shutil.rmtree(D, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
