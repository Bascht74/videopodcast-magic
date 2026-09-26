# -*- coding: utf-8 -*-
"""A bext stamp's samples are counted at the WAV's own sample rate.

A recorder writes TimeReference as samples since midnight at the rate
it records at, so one hour is a different number at every rate. Three
files each stamped 01:00:00:00 as ffmpeg writes it -- 44.1, 48 and
96 kHz -- and file_timecode asked directly: all three read one hour.
48 kHz is the working rate and reads right under the fault too; it is
here so that a repair always dividing by 44100 cannot pass, and 96 so
that one aimed at 44.1 alone cannot. Then a 44.1 kHz recording in two
blocks, stamped 01:00:00:00 and 01:00:02:00, joined: the run's report
names the start the recorder wrote.
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
import contextlib, io, subprocess, tempfile, time
vpm = the_program.load()
vpm.set_language("en")
WORK = tempfile.mkdtemp(prefix="bextrate_")
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stamped(rate, samples, name="Room"):
    """A second of tone at *rate*, its bext stamp *samples* since midnight.

    Written by ffmpeg, as a recorder writes one: fmt chunk and bext.
    """
    out = os.path.join(WORK, "%s_%d.wav" % (name, rate))
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                    "sine=frequency=300:duration=1:sample_rate=%d" % rate,
                    "-ar", str(rate), "-c:a", "pcm_s16le",
                    "-write_bext", "1", "-metadata",
                    "time_reference=%d" % samples, "-y", out], check=True)
    return out


def said(path):
    """What was read, and what it was read from, for the failure line."""
    t = vpm.file_timecode(path)
    return t, "read %r s from %r samples at %r Hz, wanted 3600.0 s" % (
        t, vpm.bext_time_reference(path), vpm.wav_rate(path))


# One hour since midnight, written out per rate rather than computed:
# 3600 s x 44100, x 48000 and x 96000.
ONE_HOUR = 3600.0

print("One hour since midnight, at three sample rates")
# The note about 48 kHz goes on the failure line only: on a green line
# it would put the wrong start next to "ok".
t, extra = said(stamped(44100, 158760000))
ok = t is not None and abs(t - ONE_HOUR) < 1e-6
check("a 44.1 kHz file's stamp reads at 44.1 kHz, not at 48", ok,
      extra if ok else extra + " -- read at 48 kHz it is 3307.5 s, 00:55:07")
t, extra = said(stamped(48000, 172800000))
check("a 48 kHz file's stamp reads at 48 kHz",
      t is not None and abs(t - ONE_HOUR) < 1e-6, extra)
t, extra = said(stamped(96000, 345600000))
ok = t is not None and abs(t - ONE_HOUR) < 1e-6
check("a 96 kHz file's stamp reads at 96 kHz, not at 48", ok,
      extra if ok else extra + " -- read at 48 kHz it is 7200.0 s, 02:00:00")

print("\nA 44.1 kHz recording in two blocks, joined")
# 3600 s and 3602 s x 44100: one second of sound, then one of nothing.
first = stamped(44100, 158760000, "Rec_0001")
second = stamped(44100, 158848200, "Rec_0002")
heard = io.StringIO()
with contextlib.redirect_stdout(heard):
    vpm.join_with_report([first, second], os.path.join(WORK, "joined.wav"))
said_lines = [l.strip() for l in heard.getvalue().splitlines() if l.strip()]
wanted = (vpm.T('  %s blocks joined via timecode, start %s')
          % (vpm.number_text(2, 0), "01:00:00:00")).strip()
extra = "said %r, wanted %r" % (" / ".join(said_lines), wanted)
ok = wanted in said_lines
check("a joined 44.1 kHz recording reports its recorder's start", ok,
      extra if ok else extra + " -- read at 48 kHz it is 00:55:07:15")

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
