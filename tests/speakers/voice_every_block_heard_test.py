# -*- coding: utf-8 -*-
"""The window's speaker measurement hears every block, laid as the run lays them.

A guest recorded in three blocks of 40 s speaks only in the second and
third, beside a presenter on one file. Sections: blocks with a timecode,
blocks without one, a hole before the last block held against the
run's own join, a block past the fence, and the window's own button --
what it hands the measurement and what that measurement hears. The
speech is modulated noise: what is judged is where loudness lies.
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
import shutil
import subprocess
import tempfile
import threading
import time
import wave

os.environ["QT_QPA_PLATFORM"] = "offscreen"
SCRIPT = the_program.SCRIPT
import numpy as np
from PySide6 import QtCore, QtWidgets     # noqa: E402  after the platform

app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
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


SR = 48000
EDGE = 0.3             # how far an edge may sit from where it was put
BLOCK = 40             # seconds per block, as a recorder splits them
FAR = 2 * 3600         # past the half-hour fence between two blocks
D = tempfile.mkdtemp(prefix="vpm_blocks_")
rng = np.random.default_rng(5)


def voice(total, parts):
    """A quiet floor with louder, modulated noise where somebody speaks."""
    x = rng.normal(0, 0.002, int(total * SR))
    for a, b in parts:
        n = int((b - a) * SR)
        x[int(a * SR):int(a * SR) + n] += rng.normal(0, 0.12, n) * (
            0.6 + 0.4 * np.sin(np.linspace(0, 40, n)))
    return x


def write(path, x, stamp=None):
    """A 16-bit WAV, with a bext time reference where *stamp* is given."""
    raw = path + ".raw.wav"
    with wave.open(raw, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
    cmd = ["ffmpeg", "-v", "error", "-i", raw, "-c:a", "pcm_s16le"]
    if stamp is not None:
        cmd += ["-write_bext", "1", "-metadata", "time_reference=%d" % stamp]
    subprocess.run(cmd + ["-y", path], check=True)
    os.unlink(raw)
    return path


def blocks(kind, starts):
    """The guest's three blocks, each stamped at *starts* (None: none)."""
    return [write("%s/Guest_%s-%04d.WAV" % (D, kind, i),
                  GUEST[i * BLOCK * SR:(i + 1) * BLOCK * SR],
                  None if at is None else at * SR)
            for i, at in enumerate(starts)]


def guest_heard(path):
    """The guest's passages, rounded, with the presenter measured beside."""
    out = dict(vpm.speakers_from_tracks([("Presenter", HOST, 0.0),
                                         ("Guest", path, 0.0)]))
    return [(round(a, 2), round(b, 2)) for a, b in out.get("Guest", [])]


def worst(got, want):
    """How far the furthest edge sits from where it was put; inf if the
    number of passages differs, since then no edge has a partner."""
    if len(got) != len(want):
        return float("inf")
    return max([abs(g - w) for gs, ws in zip(got, want)
                for g, w in zip(gs, ws)] or [0.0])


HOST = write(D + "/Presenter.WAV",
             voice(3 * BLOCK, [(5, 10), (30, 35), (70, 75), (100, 105)]), 0)
# Speech only in the second and third block: the first holds the floor.
GUEST = voice(3 * BLOCK, [(50, 55), (60, 65), (90, 95)])
WANT = [(50.0, 55.0), (60.0, 65.0), (90.0, 95.0)]

try:
    print("1. Three blocks, each with its timecode")
    got = guest_heard(blocks("tc", [0, BLOCK, 2 * BLOCK]))
    check("speech in a later block is found where the timecode puts it",
          worst(got, WANT) <= EDGE,
          "the guest was heard at %s, wanted %s within %.1f s"
          % (got, WANT, EDGE))

    print("\n2. Three blocks without a timecode")
    got = guest_heard(blocks("plain", [None, None, None]))
    check("without a timecode the blocks follow each other in order",
          worst(got, WANT) <= EDGE,
          "the guest was heard at %s, wanted %s within %.1f s"
          % (got, WANT, EDGE))

    print("\n3. A hole of 10 s before the third block")
    holed = blocks("hole", [0, BLOCK, 2 * BLOCK + 10])
    got = guest_heard(holed)
    want = [(50.0, 55.0), (60.0, 65.0), (100.0, 105.0)]
    check("a hole between two blocks stays silent in the measurement",
          worst(got, want) <= EDGE,
          "the guest was heard at %s, wanted %s within %.1f s"
          % (got, want, EDGE))
    joined, info = vpm.join_audio_parts(holed, D + "/joined.wav")
    by_run = guest_heard(joined)
    check("the blocks handed in give what the run's joined file gives",
          info.get("tc") and worst(got, by_run) <= EDGE,
          "from the blocks %s, from the run's join %s (timecode used: %s)"
          % (got, by_run, info.get("tc")))

    print("\n4. The third block two hours away")
    got = guest_heard(blocks("far", [0, BLOCK, FAR]))
    want = [(50.0, 55.0), (60.0, 65.0)]
    check("a block past the fence is left out, as the run leaves it out",
          worst(got, want) <= EDGE,
          "the guest was heard at %s, wanted %s within %.1f s"
          % (got, want, EDGE))

    print("\n5. The window's button")
    handed, arrived = [], threading.Event()

    def caught(tracks, bridge, bridge_emit):
        """Take what the button hands the measurement, and stop there."""
        handed.extend(tracks)
        arrived.set()

    vpm.cut.speaker_measure_loop = caught
    row = blocks("win", [0, BLOCK, 2 * BLOCK])
    lines = [([HOST], vpm.Value("Presenter"), vpm.Value("")),
             (row, vpm.Value("Guest"), vpm.Value(""))]
    signal = type("Signal", (), {"connect": lambda s, f: None,
                                 "emit": lambda s, *a: None})
    bridge = type("Bridge", (), {"speakers_measured": signal(),
                                 "speaker_note": signal()})()
    column = QtWidgets.QVBoxLayout()
    _compute, measure = vpm.make_preview(
        QtCore.Qt, QtWidgets, {"axis": {}}, bridge, lambda *a: None,
        lines, [], [], {}, [], None, None, None, None, None, None, None,
        None, None, None, None, None, column, None, QtWidgets.QLabel(),
        QtWidgets.QLabel(), QtWidgets.QTableWidget())
    measure()
    arrived.wait(30)
    guest = [t for t in handed if t[0] == "Guest"]
    given = list(guest[0][1]) if guest and not isinstance(
        guest[0][1], str) else [guest[0][1]] if guest else []
    check("the window hands the measurement every block of a recording",
          [os.path.basename(p) for p in given]
          == [os.path.basename(p) for p in row],
          "handed %s, wanted %s" % ([os.path.basename(p) for p in given],
                                    [os.path.basename(p) for p in row]))
    out = dict(vpm.speakers_from_tracks(handed)) if handed else {}
    got = [(round(a, 2), round(b, 2)) for a, b in out.get("Guest", [])]
    check("what the window hands in hears the later blocks' speech",
          worst(got, WANT) <= EDGE,
          "the guest was heard at %s, wanted %s within %.1f s"
          % (got, WANT, EDGE))
finally:
    shutil.rmtree(D, True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
