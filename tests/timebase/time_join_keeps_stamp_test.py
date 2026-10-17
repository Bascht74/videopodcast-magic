# -*- coding: utf-8 -*-
"""A recording joined without a picture keeps the time its first block began.

A recorder stamps each block in the bext chunk, in samples at its own
rate, and whatever lays the joined file afterwards goes by that stamp.
join_the_plan and join_only in this process, over two stamped blocks
written here, the second straight after the first, one hour in. In
order: at 48 kHz, joined as it came, the file carries the hour; at
44.1 kHz it carries it at its own rate; and where the loudness is set
on the way and the file leaves at the working rate, the hour is counted
at that rate.
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
import contextlib
import io
import shutil
import subprocess
import tempfile
import time
import types
import the_program

began = time.time()
vpm = the_program.load()
vpm.set_language("en")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-62s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# One hour, in samples at the two rates.
HOUR_44 = 158760000
HOUR_48 = 172800000
ROOM = tempfile.mkdtemp(prefix="vpm_join_stamp_")
measured = vpm.normalise_loudness


def unmeasurable(*a, **k):
    raise ValueError("stand-in: the join is copied as it came")


def joined(name, rate, stamp, level):
    """Two blocks of *rate* stamped *stamp* on, joined and written out.

    *level* lets the loudness be measured and set, as on a run; without,
    the joined blocks are copied as they came. Returns (return code,
    the written file's stamp, its rate), None for what is not there.
    """
    folder = os.path.join(ROOM, name)
    out = os.path.join(folder, "out")
    os.makedirs(out)
    blocks = []
    for i, at in enumerate((stamp, stamp + 3 * rate)):
        path = os.path.join(folder, "Guest_%03d.wav" % (i + 1))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                        "sine=frequency=440:sample_rate=%d:duration=3" % rate,
                        "-af", "volume=-30dB", "-c:a", "pcm_s24le",
                        "-write_bext", "1", "-metadata",
                        "time_reference=%d" % at, path], check=True)
        blocks.append(path)
    vpm.normalise_loudness = measured if level else unmeasurable
    args = types.SimpleNamespace(
        out=out, lufs=-16.0, auphonic_key=None, auphonic_done=None,
        dry_run=False, in_point=None, out_point=None, without_auphonic=False)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            made = vpm.join_the_plan([{"name": "Guest", "audio": blocks[0],
                                       "blocks": blocks}], folder)
            code = vpm.join_only(args, made, folder)
    finally:
        vpm.normalise_loudness = measured
    target = os.path.join(out, "Guest_joined.wav")
    if not os.path.isfile(target):
        return code, None, None
    return code, vpm.bext_time_reference(target), vpm.wav_rate(target)


print("1. Joined as it came")
code, stamp, rate = joined("plain48", 48000, HOUR_48, level=False)
check("a 48 kHz recording joined from two blocks keeps the first stamp",
      code == 0 and stamp == HOUR_48,
      "returned %r, the joined file stamped %r at %r Hz, wanted %d"
      % (code, stamp, rate, HOUR_48))
code, stamp, rate = joined("plain44", 44100, HOUR_44, level=False)
check("a 44.1 kHz one keeps it at its own rate",
      code == 0 and stamp == HOUR_44 and rate == 44100,
      "returned %r, the joined file stamped %r at %r Hz, wanted %d at "
      "44100" % (code, stamp, rate, HOUR_44))

print("\n2. Its loudness set on the way")
code, stamp, rate = joined("level44", 44100, HOUR_44, level=True)
# The working rate is the program's; the hour is counted at it.
working = 3600 * vpm.SR
check("one levelled to the working rate carries the hour counted at it",
      code == 0 and stamp == working and rate == vpm.SR,
      "returned %r, the joined file stamped %r at %r Hz, wanted %d at %d"
      % (code, stamp, rate, working, vpm.SR))

shutil.rmtree(ROOM, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
