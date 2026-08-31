# -*- coding: utf-8 -*-
"""A file left out of a recording is named, with the reason.

Two ways of being left out: a file named by hand that cannot be
used, and a second name for the same moment that nothing joins.
Both went by without a word.

Each half first asks whether the recording came back at all and
whether it holds the file it was asked about, so a red line names
the first thing that was wrong and not a consequence of it.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, struct, sys, tempfile, time, wave
import numpy as np
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
WORK = tempfile.mkdtemp(prefix="whynotjoined_")
began = time.time()
done = 0
bad = []
RATE = 48000


def check(what, ok, detail=""):
    global done
    done += 1
    print("  %-58s %s %s" % (what, "ok" if ok else "FAIL", detail))
    if not ok:
        bad.append("%s [%s]" % (what, detail or "no numbers"))


def tone(name, hz, seconds=1.0):
    path = os.path.join(WORK, name)
    t = np.arange(int(seconds * RATE)) / float(RATE)
    x = (0.5 * np.sin(2 * np.pi * hz * t) * 32767).astype("<i2")
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes(x.tobytes())
    return path


def long_silence(name, seconds):
    """A file of this length without the bytes -- only the length is read."""
    path = os.path.join(WORK, name)
    n = int(seconds * vpm.SR)
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 36 + n * 2) + b"WAVE"
                + b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, vpm.SR,
                                        vpm.SR * 2, 2, 16)
                + b"data" + struct.pack("<I", n * 2))
        f.seek(n * 2 - 1, 1)
        f.write(b"\x00")
    return path


print("A file named by hand that cannot be used is said out loud")
GONE = "nope.wav"
solo = tone("r_260809_000030.wav", 300.0)
other = tone("x_260809_010000.wav", 300.0)
gone = os.path.join(WORK, GONE)
rows = vpm.group_recording_parts(
    [solo, other], together=[[solo, gone]])
# Two files were handed in and both exist, so two recordings come back.
# Asked first: with none of them the two checks under it would report a
# missing name where in truth nothing at all came back.
check("the two files that exist come back as two recordings",
      len(rows) == 2, "2 wanted, %d came back" % (len(rows),))
left_out = [(name, why) for _row, discarded in rows
            for name, why in discarded]
named = [name for name, _why in left_out]
check("the file named by hand that is not there is left out",
      named.count(GONE) == 1,
      "%s wanted 1 time, found %d among %d left out: %s"
      % (GONE, named.count(GONE), len(left_out), named))
reasons = [why for _name, why in left_out]
check("and the one reason given says the file was not found",
      reasons == [vpm.T('not found')],
      "1 reason wanted, saying %r -- %d given: %s"
      % (vpm.T('not found'), len(reasons), reasons))

print("\nTwo file names for the same moment say why nothing was joined")
# Five minutes apart, so the trailing number cannot pass for a counter
# and only the clock rule could join the two.
LATER = "v_260808_140500.wav"
DOUBLED = ("v_20260808_140000.wav", "v_260808_140000.wav")
long_silence(DOUBLED[1], 300.0)
long_silence(DOUBLED[0], 300.0)
after = long_silence(LATER, 300.0)
row, discarded = vpm.find_continuation_files(after)
in_row = [os.path.basename(x) for x in row]
# The same order as above: does the recording hold the file that was
# asked about at all? Without this a recording made of quite other
# files would still be one block long and pass the check below.
check("the file asked about is in the recording that comes back",
      in_row.count(LATER) == 1,
      "%s wanted 1 time, found %d among %d blocks: %s"
      % (LATER, in_row.count(LATER), len(in_row), in_row))
check("neither name for the doubled moment joins the recording",
      len(row) == 1, "1 block wanted, %d found: %s" % (len(row), in_row))
told = sorted(name for name, _why in discarded)
check("both names for that moment are named as left out",
      told == sorted(DOUBLED),
      "2 wanted, %s -- %d found, %s" % (sorted(DOUBLED), len(told), told))
said = vpm.T('two file names for the same moment -- '
             'neither of them is taken')
why_told = [why for _name, why in discarded]
check("each reason says the same moment was named twice",
      why_told == [said, said],
      "2 reasons wanted, saying %r -- %d of %d say it: %s"
      % (said, why_told.count(said), len(why_told), why_told))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
