# -*- coding: utf-8 -*-
"""The window's time axis is the run's measurement, drift rule included.

A recording made of blocks is joined and measured as the run measures
it, and every file lies where the run lays it: divided by its clock
where the run takes the drift out, unstretched where the drift stays in.
Sections: the interview fixture, whose two recordings of three blocks
the run places by sound and whose one drift stays in; a synthetic
camera with a recording in two blocks whose drift the run takes out;
and that recording once more, its join answering that it cannot be
placed. The run's side is read off the run's own functions.
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
import json
import shutil
import subprocess
import tempfile
import time
import wave
import numpy as np

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


# A tenth of a millisecond: the run's own numbers, not a frame apart.
SAME = 0.0001
WORK = tempfile.mkdtemp(prefix="vpm_axisrun_")


def name_of(p):
    return os.path.basename(p)


def clock(p):
    try:
        return vpm.file_timecode(p, 25.0)
    except Exception:
        return None


def run_side(cameras, rows):
    """Where the run lays every file, relative to its reference camera.

    The cameras by align_cameras, each recording joined by join_the_plan
    and placed by sound_places, and laid as speakers_for_the_cut reads
    it: recordings_on_axis, with the drift taken out where drift_clear
    says. {path: (start, clock, a, b, drift taken, placed by sound)}.
    """
    out = {}
    with contextlib.redirect_stdout(io.StringIO()):
        ref, position = vpm.align_cameras(
            [(p, vpm.video_facts(p)) for p in cameras])
        for p, (a, b, _st) in position.items():
            out[p] = (-a / b, None, a, b, None, True)
        made = vpm.join_the_plan([{"audio": row[0], "blocks": row}
                                  for row in rows], WORK)
        for row, m in zip(rows, made):
            got = vpm.sound_places(name_of(row[0]), m["source"], ref[0],
                                   ref[1]["duration"], False)
            if not got:
                out[row[0]] = (None, None, None, None, None, False)
                continue
            a, b, st = got
            track = {"name": name_of(row[0]), "source": m["source"],
                     "a": a, "b": b, "drift": vpm.drift_clear(b, st)}
            _n, _s, start, speed = vpm.recordings_on_axis([track],
                                                          (0.0, 1.0))[0]
            out[row[0]] = (start, speed, a, b, track["drift"],
                           not st.get("unplaceable"))
    return ref[0], out


def window_side(paths, rows):
    """Where the window's axis lays every file, relative to *ref*."""
    with contextlib.redirect_stdout(io.StringIO()):
        data, _text = vpm.axis_with_blocks(
            paths, clock, 5.0, dict((row[0], row) for row in rows),
            phase_of=lambda p: False)
    return data


def figure(value):
    return "none" if value is None else "%+.4f" % value


#------------------------------------------------ 1. The interview fixture

print("1. The interview fixture")
F = fixture("interview")
CAMERAS = [os.path.join(F, n) for n in (
    "WideCam_01011855_C001.mov", "PresentersCam_01011855_C002.mov",
    "GuestCam_01011858_C003.mov")]
ROWS = [[os.path.join(F, "Presenter_REC%05d.wav" % n) for n in (21, 22, 23)],
        [os.path.join(F, "CoPresenter_REC%05d.wav" % n)
         for n in (18, 19, 20)],
        [os.path.join(F, "Guest_Take0021A_Timecode.wav")]]
EVERY = CAMERAS + [p for row in ROWS for p in row]
ref, run = run_side(CAMERAS, ROWS)
data = window_side(EVERY, ROWS)
axis, speed = data.get("axis") or {}, data.get("clock") or {}
origin = axis.get(vpm.path_key(ref))


def at(p):
    """The window's place of *p* counted from the run's reference."""
    t = axis.get(vpm.path_key(p))
    return None if t is None or origin is None else t - origin


for p in sorted(run, key=name_of):
    print("   %-32s run %s, window %s" % (name_of(p), figure(run[p][0]),
                                          figure(at(p))))
unplaced = [name_of(p) for p, r in run.items() if not r[5]]
check("the run places every recording of the fixture by its sound",
      not unplaced, "not placed: %s" % unplaced)
weak = sorted(name_of(p) for p in data.get("weak") or ())
check("the window names no file as not fitting where the run places all",
      not weak, "named as not fitting: %s" % weak)
apart = [(name_of(p), at(p), r[0]) for p, r in sorted(run.items())
         if r[0] is not None and (at(p) is None or abs(at(p) - r[0]) > SAME)]
check("every file lies where the run lays it, to a tenth of a ms",
      not apart, "; ".join("%s window %s run %+.4f" % (n, figure(w), r)
                           for n, w, r in apart))
left_in = [p for p, r in run.items() if r[4] is False and r[3] != 1.0]
check("the fixture holds a recording whose drift the run leaves in",
      bool(left_in), "b of each recording: %s" % ", ".join(
          "%s %.7f drift %s" % (name_of(p), r[3], r[4])
          for p, r in run.items() if r[4] is not None))
check("where the run leaves the drift in, the window's clock is 1.0",
      bool(left_in) and all(speed.get(vpm.path_key(p)) == 1.0
                            for p in left_in),
      ", ".join("%s clock %.7f, the run's b %.7f"
                % (name_of(p), speed.get(vpm.path_key(p)) or 0.0, run[p][3])
                for p in left_in))
behind = [(name_of(row[i]), at(row[i]), at(row[0]) + 40.0 * i)
          for row in ROWS[:2] for i in (1, 2)
          if at(row[0]) is not None]
check("the blocks after a head follow it by their length",
      len(behind) == 4 and all(t is not None and abs(t - w) <= SAME
                               for _n, t, w in behind),
      "; ".join("%s at %s, wanted %+.4f" % (n, figure(t), w)
                for n, t, w in behind) or "no head on the axis")

#-------------------------------------- 2. A drift the run takes out

print("\n2. A recording whose drift the run takes out")
RATE = 16000
LENGTH = 300.0
# The recorder starts this far into the camera: far enough that -a and
# -a / b lie milliseconds apart, so the drift rule shows in the place.
LATE = 20.0
BLOCK = 140.0
PPM = 150.0


def bursts(seconds, seed):
    """Speech-like turns: noise in irregular pieces with pauses between."""
    rng = np.random.default_rng(seed)
    n = int(seconds * RATE)
    x = np.zeros(n)
    t = 0.2
    while t < seconds - 1.0:
        long_s = float(rng.uniform(0.25, 0.9))
        k, i0 = int(long_s * RATE), int(t * RATE)
        x[i0:i0 + k] = (rng.normal(0, float(rng.uniform(0.08, 0.3)), k)
                        * np.hanning(k))
        t += long_s + float(rng.uniform(0.2, 1.1))
    return x + rng.normal(0, 0.0004, n)


def write(path, x):
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())


room = bursts(LENGTH, 7)
write(os.path.join(WORK, "room.wav"), room)
CAM = os.path.join(WORK, "WideCam_C001.mov")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "color=size=64x36:rate=5", "-i",
                os.path.join(WORK, "room.wav"), "-map", "0:v", "-map", "1:a",
                "-shortest", "-c:v", "libx264", "-preset", "ultrafast",
                "-c:a", "pcm_s16le", CAM], check=True)
# The recorder runs PPM fast: its second s holds the room's s * (1 + PPM).
late = room[int(LATE * RATE):]
n = len(late)
fast = np.interp(np.arange(n) * (1.0 + PPM * 1e-6), np.arange(n), late)
cut = int(BLOCK * RATE)
HEAD = os.path.join(WORK, "Presenter_REC00001.wav")
TAIL = os.path.join(WORK, "Presenter_REC00002.wav")
write(HEAD, fast[:cut])
write(TAIL, fast[cut:])
ref2, run2 = run_side([CAM], [[HEAD, TAIL]])
data2 = window_side([CAM, HEAD, TAIL], [[HEAD, TAIL]])
axis, speed = data2.get("axis") or {}, data2.get("clock") or {}
origin = axis.get(vpm.path_key(ref2))
start, _speed, a, b, taken, placed = run2[HEAD]
print("   run: a %s, b %.7f, drift taken %s; window head %s, clock %.7f"
      % (figure(a), b or 0.0, taken, figure(at(HEAD)),
         speed.get(vpm.path_key(HEAD)) or 0.0))
check("the run takes the drift of the recording out",
      placed and taken is True,
      "placed by sound %s, b %.7f, drift taken %s" % (placed, b or 0.0,
                                                      taken))
check("where the run takes the drift out, the window runs at its clock",
      b is not None and abs((speed.get(vpm.path_key(HEAD)) or 0.0) - b)
      <= 1e-9, "window %.9f against the run's %.9f"
      % (speed.get(vpm.path_key(HEAD)) or 0.0, b or 0.0))
check("and lays the recording where the run lays it",
      start is not None and at(HEAD) is not None
      and abs(at(HEAD) - start) <= SAME,
      "window %s against the run's %s" % (figure(at(HEAD)), figure(start)))
# The joined file's second block begins at sample BLOCK of it, and the
# run lays recording time s at (s - a) / b on the axis.
wanted = (BLOCK - a) / b if b else None
check("its second block follows at the head's length on the run's clock",
      wanted is not None and at(TAIL) is not None
      and abs(at(TAIL) - wanted) <= SAME,
      "window %s against %s; by the length alone %s"
      % (figure(at(TAIL)), figure(wanted),
         figure(at(HEAD) + BLOCK if at(HEAD) is not None else None)))

#------------------------------ 3. A join the run cannot place (E-535)

print("\n3. A recording whose joined sound the run cannot place")
# The join's measurement as the run keeps it, by head: None where it
# found nothing, a place marked unplaceable where the sound gave none.
# The run refuses such a head (tracks_placed): it lies nowhere, and the
# window's axis says so too instead of keeping what the head alone got.
HEAD_KEY = vpm.path_key(HEAD)


def joined_as(got, weak=()):
    """The window's axis of section 2, the join answering *got*."""
    data = json.loads(json.dumps(data2))
    data["weak"] = list(weak)
    vpm.head_by_the_whole(data, [CAM, HEAD, TAIL], {HEAD: [HEAD, TAIL]},
                          raw={"joined": {HEAD_KEY: got}})
    return data


def nowhere_line(data):
    """Where the head stands in *data*, and whether it is said to."""
    return "head at %s, among those with no place: %s" % (
        figure((data.get("axis") or {}).get(HEAD_KEY)),
        HEAD_KEY in set(vpm.path_key(p) for p in data.get("no_place") or ()))


found_nothing = joined_as(None)
check("a head whose join finds nothing stands nowhere, as in the run",
      HEAD_KEY not in (found_nothing.get("axis") or {})
      and HEAD in (found_nothing.get("no_place") or ()),
      nowhere_line(found_nothing))
check("and its later block with it",
      vpm.path_key(TAIL) not in (found_nothing.get("axis") or {}),
      "tail at %s" % figure((found_nothing.get("axis") or {}).get(
          vpm.path_key(TAIL))))
unplaced = joined_as([0.0, 1.0, {"unplaceable": True}])
check("a head its join cannot place stands nowhere, though it alone did",
      HEAD_KEY not in (unplaced.get("axis") or {})
      and HEAD in (unplaced.get("no_place") or ()), nowhere_line(unplaced))
by_clock = joined_as([0.0, 1.0, {"unplaceable": True}], weak=[HEAD])
check("a head its clock placed keeps that place",
      HEAD_KEY in (by_clock.get("axis") or {}), nowhere_line(by_clock))

shutil.rmtree(WORK, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
