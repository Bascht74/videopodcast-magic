# -*- coding: utf-8 -*-
"""Who speaks, read off the originals, is what the tracks on the axis say.

Two recordings of one programme: the host's begins before the window and
off the block grid, the guest's later and on a clock of its own. In
order: the originals read at their place against the same tracks
written onto the axis, each speaker against where the turns were put,
nothing outside the window heard, and the run's own step -- after the
separation, who speaks when over the cut's window reads the originals,
with the tracks on the axis silenced. The guest's clock is five in a thousand, far past a real one,
so a clock left out shows at a tenth of a second.
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
import argparse, contextlib, io, tempfile, time, wave
import numpy as np

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
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
D = tempfile.mkdtemp(prefix="vpm_originals_")
T0, T1 = 2.0, 55.0       # the cut's window on the programme's axis
EDGE = 0.15              # how far an edge may sit from where it was put
SAME = 0.02              # two readings of one block grid: rounding only
# Programme seconds. The host also speaks before and after the window.
TURNS = {"Host": [(0.5, 1.5), (4.0, 12.0), (24.0, 31.0), (46.0, 53.0),
                  (56.5, 59.0)],
         "Guest": [(13.0, 22.0), (33.0, 44.0)]}
# recorder = a + b * programme: the host began 3.33 s before programme
# nought, the guest 1.23 s after it with a fast clock.
PLACE = {"Host": (3.33, 1.0, False), "Guest": (-1.23, 1.005, True)}
rng = np.random.default_rng(7)


def recording(who):
    """Speech-like noise where *who* speaks, in the recorder's own time."""
    a, b, _drift = PLACE[who]
    length = a + b * 62.0
    x = rng.normal(0, 0.002, int(length * SR))
    for p, q in TURNS[who]:
        lo, hi = int((a + b * p) * SR), int((a + b * q) * SR)
        lo = max(lo, 0)
        if hi > lo:
            x[lo:hi] += rng.normal(0, 0.12, hi - lo) * (
                0.6 + 0.4 * np.sin(np.linspace(0, 40, hi - lo)))
    path = "%s/%s_REC0001.wav" % (D, who)
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
    return path


def in_window(who):
    """Where the turns were put, counted from the window's start."""
    return [(max(p, T0) - T0, min(q, T1) - T0) for p, q in TURNS[who]
            if q > T0 and p < T1]


def worst(got, want):
    """The furthest edge from its partner; inf if the counts differ."""
    if len(got) != len(want):
        return float("inf")
    return max([abs(g - w) for gs, ws in zip(got, want)
                for g, w in zip(gs, ws)] or [0.0])


tracks = []
for who in sorted(PLACE):
    a, b, drift = PLACE[who]
    source = recording(who)
    axis = "%s/axis_%s.wav" % (D, who)
    vpm.place_track_on_axis(source, axis, a, b, T0, T1, drift)
    tracks.append({"name": who, "source": source, "blocks": [source],
                   "a": a, "b": b, "drift": drift, "axis": axis})

on_axis = dict(vpm.speakers_from_tracks(
    [(t["name"], t["axis"], 0.0) for t in tracks]))
originals = dict(vpm.speakers_from_tracks(
    vpm.recordings_on_axis(tracks, (T0, T1)), span=T1 - T0))
print("   on the axis:", on_axis)
print("   originals:  ", originals)

print("1. The originals against the tracks written onto the axis")
far = worst(originals.get("Host", []), on_axis.get("Host", []))
check("a recording off the block grid gives the axis track's edges",
      far <= SAME, "host %s against %s, %.3f s apart, allowed %.2f"
      % (originals.get("Host"), on_axis.get("Host"), far, SAME))
far = worst(originals.get("Guest", []), on_axis.get("Guest", []))
check("a recording on its own clock gives the axis track's edges",
      far <= EDGE, "guest %s against %s, %.3f s apart, allowed %.2f"
      % (originals.get("Guest"), on_axis.get("Guest"), far, EDGE))

print("\n2. Each speaker where the turns were put")
far = worst(originals.get("Host", []), in_window("Host"))
check("a recording that began before the window is heard in place",
      far <= EDGE, "host %s, wanted %s within %.2f s"
      % (originals.get("Host"), in_window("Host"), EDGE))
far = worst(originals.get("Guest", []), in_window("Guest"))
check("a recording with a clock of its own is heard in place",
      far <= EDGE, "guest %s, wanted %s within %.2f s"
      % (originals.get("Guest"), in_window("Guest"), EDGE))

print("\n3. Nothing outside the window")
edges = [e for segs in originals.values() for s in segs for e in s]
check("no speech is heard before or after the cut's window",
      edges and min(edges) >= 0.0 and max(edges) <= T1 - T0 + 1e-6,
      "edges from %s to %s s, the window is 0 to %.1f s"
      % (min(edges or [None]), max(edges or [None]), T1 - T0))

print("\n4. The run's step reads the originals")
# The tracks on the axis are silenced: whatever is heard now came off
# the originals. Who speaks when is asked with the window, as the run
# asks it.
for t in tracks:
    vpm.place_track_on_axis(t["source"], t["axis"], 0.0, 1.0, 1e6,
                            1e6 + T1 - T0, False)
args = argparse.Namespace(no_speakers_local=True)
with contextlib.redirect_stdout(io.StringIO()):
    vpm.separation_for_run(args, tracks, {}, T0, T1)
    got = dict(vpm.speakers_of_the_run(args, tracks, (T0, T1)))
far = worst(got.get("Host", []), in_window("Host"))
check("after the separation step the run reads each recording itself",
      far <= EDGE and worst(got.get("Guest", []), in_window("Guest"))
      <= EDGE, "host %s, guest %s; wanted %s and %s"
      % (got.get("Host"), got.get("Guest"), in_window("Host"),
         in_window("Guest")))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
