# -*- coding: utf-8 -*-
"""Every order of the same cameras gives run and window one time axis.

Four cameras of one room: two exactly as long, a third sharing sound
with only the second of them, a fourth with only the third. Sections:
every order of the four, through the run's door (align_cameras) --
one reference, one place per camera, the places where the cameras were
cut, the fourth placed through the third; the same orders through the
window's door (measure_time_axis), which agrees with the run; and a tie
nothing else settles, where a timecode and then the path decide.
Synthetic material, fixed seeds, the axis compared to a frame.
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
import contextlib
import io
import itertools
import subprocess
import tempfile
import time
import wave
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


#------------------------------------------------------------- Material

RATE = 8000
FRAME = 1.0 / 25
SCENE = 500.0
# Where each camera starts and stops in the room's time. The first two
# run exactly as long; the third shares sixty seconds with the second
# and none with the first; the fourth fifty with the third alone.
SPANS = {"WideCam_C001": (0.0, 240.0), "GuestCam_C002": (120.0, 360.0),
         "PresenterCam_C003": (300.0, 420.0),
         "CoPresenterCam_C004": (370.0, 470.0)}
# The second shares sound with both others it can reach, so it is the
# one the most others place against; the answer stands here as a name.
WANTED_REF = "GuestCam_C002"


def turns(seconds, seed):
    """Speech-like turns: noise in irregular pieces with pauses between."""
    rng = np.random.default_rng(seed)
    n = int(seconds * RATE)
    x = np.zeros(n)
    t = 0.2
    while t < seconds - 1.0:
        long_s = float(rng.uniform(0.3, 3.0))
        k, i0 = int(long_s * RATE), int(t * RATE)
        k = min(k, n - i0)
        if k > 2:
            x[i0:i0 + k] = rng.normal(0, 0.25, k) * np.hanning(k)
        t += long_s + float(rng.uniform(0.2, 2.5))
    return x


def write(path, x):
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())


def cameras(folder, spans, clocks=None):
    """One .mov per span, each hearing the room its own way: {name: path}."""
    one, other = turns(SCENE, 5), turns(SCENE, 6)
    other = other * (np.abs(one) < 1e-6)
    made = {}
    for i, (name, (t0, t1)) in enumerate(sorted(spans.items())):
        rng = np.random.default_rng(40 + i)
        near = 0.3 + 0.15 * i
        room = near * one + (1.0 - near) * other + rng.normal(
            0, 0.004, len(one))
        wav = os.path.join(folder, name + ".wav")
        write(wav, room[int(t0 * RATE):int(t1 * RATE)])
        path = os.path.join(folder, name + ".mov")
        clock = (clocks or {}).get(name)
        # A tiny picture at five frames: no frame is ever decoded.
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
             "color=size=64x36:rate=5", "-i", wav, "-map", "0:v", "-map",
             "1:a", "-shortest", "-c:v", "libx264", "-preset", "ultrafast",
             "-c:a", "pcm_s16le"]
            + (["-timecode", clock] if clock else []) + [path], check=True)
        made[name] = path
    return made


def the_run(paths):
    """align_cameras in this order: (reference name, {name: start}, via)."""
    with contextlib.redirect_stdout(io.StringIO()):
        ref, position = vpm.align_cameras(
            [(p, vpm.video_facts(p)) for p in paths])
    starts = dict((name_of(p), -a / b) for p, (a, b, _st) in position.items())
    first = min(starts.values())
    via = dict((name_of(p), name_of(st["via"])) for p, (_a, _b, st)
               in position.items() if st.get("via"))
    return (name_of(ref[0]), dict((n, s - first) for n, s in starts.items()),
            via)


def the_window(paths):
    """measure_time_axis in this order: {name: place on the axis}."""
    with contextlib.redirect_stdout(io.StringIO()):
        data, _text = vpm.measure_time_axis(list(paths))
    axis = data.get("axis") or {}
    return dict((name_of(p), axis[vpm.path_key(p)]) for p in paths
                if vpm.path_key(p) in axis)


def name_of(path):
    return os.path.splitext(os.path.basename(path))[0]


def widest(many):
    """How far the answers for one camera lie apart, over all orders."""
    names = set().union(*[set(m) for m in many])
    return max(max(m.get(n, 1e9) for m in many)
               - min(m.get(n, -1e9) for m in many) for n in names)


def said(starts):
    return ", ".join("%s %+.3f" % (n, starts[n]) for n in sorted(starts))


# Its own folder under the run's TMPDIR, which the run throws away.
D = tempfile.mkdtemp(prefix="vpm_orders_")
CAMS = cameras(D, SPANS)
ORDERS = list(itertools.permutations(sorted(CAMS.values())))
TRUTH = dict((n, t0) for n, (t0, _t1) in SPANS.items())

#------------------------------------------------------ 1. The run's door

print("1. Every order of the four cameras through the run")
runs = [the_run(order) for order in ORDERS]
refs = sorted(set(r[0] for r in runs))
print("   %d orders, references %s; the first: %s"
      % (len(runs), refs, said(runs[0][1])))
check("every order gives the run the one reference that places most",
      refs == [WANTED_REF], "references %s over %d orders, wanted only %s"
      % (refs, len(runs), WANTED_REF))
check("and every camera one place, whatever the order",
      all(len(r[1]) == len(SPANS) for r in runs)
      and widest([r[1] for r in runs]) <= 0.001,
      "cameras placed per order %s, the widest spread %.3f s"
      % (sorted(set(len(r[1]) for r in runs)),
         widest([r[1] for r in runs])))
off = max(abs(runs[0][1].get(n, 1e9) - TRUTH[n]) for n in TRUTH)
check("the places are where the cameras were cut out of the room",
      off <= FRAME, "%s against %s, %.3f s off at worst"
      % (said(runs[0][1]), said(TRUTH), off))
vias = sorted(set(tuple(sorted(r[2].items())) for r in runs))
check("the camera only a placed camera hears is placed through that one",
      vias == [(("CoPresenterCam_C004", "PresenterCam_C003"),)],
      "placed through %s, wanted CoPresenterCam_C004 through "
      "PresenterCam_C003 in every order" % vias)

#--------------------------------------------------- 2. The window's door

print("\n2. The same orders through the window")
windows = [the_window(order) for order in ORDERS]
print("   the first: %s" % said(windows[0]))
check("every order gives the window one axis",
      all(len(w) == len(SPANS) for w in windows)
      and widest(windows) <= 0.001,
      "cameras on it per order %s, the widest spread %.3f s"
      % (sorted(set(len(w) for w in windows)), widest(windows)))
apart = max(abs(windows[0].get(n, 1e9) - runs[0][1].get(n, -1e9))
            for n in TRUTH)
check("and the window's axis is the run's",
      apart <= FRAME, "window %s, run %s, %.3f s apart at worst"
      % (said(windows[0]), said(runs[0][1]), apart))

#--------------------------------------------------------- 3. A plain tie

print("\n3. Two cameras as long, each placing only the other")
TIE = {"WideCam_C011": (0.0, 200.0), "GuestCam_C012": (60.0, 260.0)}
bare = cameras(tempfile.mkdtemp(prefix="vpm_tie_", dir=D), TIE)
pair = sorted(bare.values())
got = sorted(set(the_run(order)[0] for order in (pair, pair[::-1])))
print("   references %s" % got)
check("a tie nothing else settles goes by the path, not the order",
      got == ["GuestCam_C012"], "references %s over both orders, wanted "
      "GuestCam_C012, the first path" % got)
clocked = cameras(tempfile.mkdtemp(prefix="vpm_tieclock_", dir=D), TIE,
                  {"WideCam_C011": "10:00:00:00"})
pair = sorted(clocked.values())
got = sorted(set(the_run(order)[0] for order in (pair, pair[::-1])))
print("   with a clock on the second path: references %s" % got)
check("and a camera with a clock goes before one without",
      got == ["WideCam_C011"], "references %s over both orders, wanted "
      "WideCam_C011, the one with a timecode" % got)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
