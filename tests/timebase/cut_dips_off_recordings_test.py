# -*- coding: utf-8 -*-
"""A dry run's sound dips, read off the recordings, are its axis tracks' own.

The interview fixture's recordings, a stereo file made of two of them
and two float files made louder. Each case is laid at places of its own
between an In and an Out point, and its loudness every ten milliseconds
is read twice: off the recordings at their place, as a dry run reads
it, and off the tracks written onto the axis and summed into one file,
as it was read before. In order: three recordings at three places, one
with its drift taken out; a mono and a stereo one; the stereo one
alone; a float recording past full scale; two under it whose sum is
past it. The limit: the written tracks are rounded to 24 bit, so a
value may lie one step apart where the sum stands on a step's edge.
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
import glob
import shutil
import subprocess
import tempfile
import time
import the_program
from fixture_root import fixture

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


WORK = tempfile.mkdtemp(prefix="vpm_dips_")


def stop():
    """Nothing further can be asked, so count what there is and go."""
    shutil.rmtree(WORK, ignore_errors=True)
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


MEDIA = fixture("interview")


def first(pattern):
    """The fixture's first file by a pattern, or ''."""
    found = sorted(glob.glob(os.path.join(MEDIA, pattern)))
    return found[0] if found else ""


GUEST, HOST, COHOST = (first("Guest_*.wav"), first("Presenter_*.wav"),
                       first("CoPresenter_*.wav"))
if not (GUEST and HOST and COHOST):
    print("SKIPPED: no interview fixture -- tests/fixtures.sh builds it "
          "under VPM_FIXTURES (looked in %s)" % MEDIA)
    stop()
STEREO = os.path.join(WORK, "stereo.wav")
# A precondition of the material, not a judgement: two recordings as
# the two channels of one file.
assert subprocess.run(
    ["ffmpeg", "-v", "error", "-y", "-i", HOST, "-i", COHOST,
     "-filter_complex", "[0:a][1:a]amerge=inputs=2[s]", "-map", "[s]",
     STEREO]).returncode == 0
# Float files, as a recorder writes them: the fixture peaks near -18 dB,
# so 20 dB more goes past full scale, and 14 dB more stays under it --
# and twice of that, summed, goes past again.
LOUD, HALF = os.path.join(WORK, "loud.wav"), os.path.join(WORK, "half.wav")
for made, gain in ((LOUD, "20dB"), (HALF, "14dB")):
    assert subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", GUEST, "-af", "volume=" + gain,
         "-c:a", "pcm_f32le", made]).returncode == 0

T0, T1 = 5.0, 65.0
# The values every case is held to: how many may differ, and by how much.
# A step apart is the 24 bit rounding; a sum twice as loud stands on a
# step's edge more often, 0.15 % of its values measured against 0.02 %.
SHARE_LEAST, STEP_MOST = 99.5, 1


def compare(tracks):
    """Off the recordings and off the summed files: (values, same, most)."""
    heard = vpm.levels_at_their_place(tracks, T0, T1, WORK)
    files = [vpm.place_track_on_axis(
        t["source"], os.path.join(WORK, "axis_%d.wav" % i), t["a"], t["b"],
        T0, T1, t["drift"]) for i, t in enumerate(tracks)]
    summed = vpm.mix_tracks(files, os.path.join(WORK, "sum_%d.wav"
                                                % len(tracks)),
                            label="sum")
    written = vpm.sound_levels(summed)
    for p in set(files + [summed]):
        os.remove(p)
    if not written or len(heard) != len(written):
        return len(heard), len(written), 0.0, None
    steps = [abs(x - y) for x, y in zip(heard, written)]
    same = 100.0 * sum(1 for d in steps if d == 0) / len(steps)
    return len(heard), len(written), same, max(steps)


def judged(tracks):
    """One case: the same values, give or take the 24 bit step.

    Returns (the verdict, its numbers); the check stands at the call,
    its wording written out, so the register can name it.
    """
    count, written, same, most = compare(tracks)
    return (most is not None and same >= SHARE_LEAST and most <= STEP_MOST,
            "%d values off the recordings, %d off the files, %.2f %% the "
            "same against %.1f %%, %s apart at most against %d"
            % (count, written, same, SHARE_LEAST, most, STEP_MOST))


print("1. Three recordings at three places, one drift taken out")
check("three recordings at their place sum as their files do", *judged(
    [dict(source=GUEST, a=0.0, b=1.0, drift=False),
     dict(source=HOST, a=-1.25, b=1.0, drift=False),
     dict(source=COHOST, a=2.5, b=1.0002, drift=True)]))
print("\n2. A mono and a stereo recording, the stereo drift taken out")
check("a stereo recording is summed as its file on the axis is", *judged(
    [dict(source=GUEST, a=0.3, b=1.0, drift=False),
     dict(source=STEREO, a=-0.7, b=0.9999, drift=True)]))
print("\n3. The stereo recording alone")
check("one recording alone is measured as its file on the axis is",
      *judged([dict(source=STEREO, a=0.0, b=1.0, drift=False)]))
print("\n4. A float recording past full scale")
check("a float recording past full scale stops there, as in its file",
      *judged([dict(source=LOUD, a=0.4, b=1.0, drift=False)]))
print("\n5. Two under full scale, their sum past it")
check("and a sum past full scale stops there, as the summed file did",
      *judged([dict(source=HALF, a=0.0, b=1.0, drift=False),
               dict(source=HALF, a=0.0, b=1.0, drift=False)]))
stop()
