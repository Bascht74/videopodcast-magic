# -*- coding: utf-8 -*-
"""The preflight asks about bleed whether Multitrack is ticked or not.

Two recordings come out as two tracks in every camera with the tick and
without it, so how much each microphone hears of the other is a question
about the material, not about the switch. Two microphones with bleed
built in go through the command line's preflight twice, the tick off and
on: the bleed is asked both times, and the two reports agree. What is
free on disk and the loudness line are replaced, so the report holds
what the material says and nothing about this machine.
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
import shutil, tempfile, time, wave
import numpy as np
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


# Its own folder under the run's TMPDIR, which the run throws away, and
# its own cache, so no answer another test stored stands in for this one.
WORK = tempfile.mkdtemp(prefix="vpm_bleed_tick_")
os.environ["VPM_CACHE"] = os.path.join(WORK, "cache")
SR = 16000
# Two speakers taking turns, each heard 12 dB down in the other's
# microphone: enough windows for the reading, and a bleed it names.
SECONDS, TURN, DOWN_DB = 16, 2, 12.0


def write(path, x):
    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(
            np.clip(x * 20000, -32000, 32000).astype("<i2").tobytes())
    return path


t = np.arange(TURN * SR) / float(SR)
turns = [np.sin(2 * np.pi * hz * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 3 * t))
         for hz in (130, 190)]
own, other = np.zeros(SECONDS * SR), np.zeros(SECONDS * SR)
for k in range(SECONDS // TURN):
    at = slice(k * TURN * SR, (k + 1) * TURN * SR)
    loud, soft = (own, other) if k % 2 == 0 else (other, own)
    loud[at] = turns[k % 2]
    soft[at] = turns[k % 2] * 10 ** (-DOWN_DB / 20.0)
rng = np.random.default_rng(3)
SOUNDS = [write(os.path.join(WORK, "Presenter.wav"),
                own + rng.uniform(-1, 1, len(own)) * 0.0005),
          write(os.path.join(WORK, "Guest.wav"),
                other + rng.uniform(-1, 1, len(other)) * 0.0005)]


class Call(object):
    """As much of a parsed command line as the preflight reads."""

    def __init__(self, multitrack):
        self.multitrack = multitrack
        self.out = WORK
        self.dry_run = True
        self.anyway = False
        self.lufs = None


def report(multitrack):
    """The findings the command line's preflight reports for SOUNDS."""
    seen = []
    keep = (vpm.check_disk_space, vpm.report_findings)
    vpm.check_disk_space = lambda *a, **k: []
    vpm.report_findings = lambda found, *a, **k: (seen.extend(found), 0)[1]
    try:
        vpm.run_preflight(Call(multitrack), SOUNDS, [])
    finally:
        vpm.check_disk_space, vpm.report_findings = keep
    return [(f.field, f.text) for f in seen]


BLEED = vpm.T('Bleed')
print("1. The tick off, and on")
off, on = report(False), report(True)
asked = [text[:60] for field, text in off if field == BLEED]
check("with the tick off the bleed is asked all the same", bool(asked),
      "%d findings, %d of them about bleed: %s"
      % (len(off), len(asked), asked[:1]))
differ = sorted(set(off) ^ set(on))
check("and the tick on gives the same report, finding for finding",
      off == on,
      "%d findings off, %d on, %d stand in only one: %s"
      % (len(off), len(on), len(differ), [t[:50] for _f, t in differ[:2]]))

shutil.rmtree(WORK, True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
