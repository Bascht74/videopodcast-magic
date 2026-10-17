# -*- coding: utf-8 -*-
"""A return that cannot hold the sound that went up is refused, and said.

Built speech-like sound, one take of 44 s, held by the return check
against what is said to have come back. In order: right returns are
accepted -- processed, short by a lossy frame, and longer by a jingle
in front and a tail behind; returns that are not the take are refused
-- last week's take forward against this week's reversed and 12 s
shorter, the take reversed at full length, another voice, and the take
with its last seconds gone; the refusal is said on the track's line and
under the lines, apart from a return of noise left unsure; and a return
of the whole range trimmed to the window is judged on the file as it
came, whole or short at its end. Not asked: other sound longer than
what went up, placed inside it -- that passes.
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
import struct
import subprocess
import tempfile
import time
import types
import numpy as np

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


vpm = the_program.load()
vpm.set_language("en")
SR = vpm.SR
T = tempfile.mkdtemp(prefix="foreign_")
TAKE_S = 44.0


def speech_like(duration, seed):
    rng = np.random.default_rng(seed)
    n = int(duration * SR)
    x = np.zeros(n)
    t = 0
    while t < n - SR:
        length = int(rng.uniform(0.3, 1.2) * SR)
        f0 = rng.uniform(90, 190)
        k = np.arange(length)
        piece = sum(np.sin(2 * np.pi * f0 * h * k / SR) / h for h in range(1, 12))
        x[t:t + length] += 0.3 * piece * np.hanning(length)
        t += length + int(rng.uniform(0.05, 0.5) * SR)
    return x + 0.001 * rng.normal(size=n)


def write(name, x):
    file_path = os.path.join(T, name)
    b = (np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()
    with open(file_path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 36 + len(b)) + b"WAVE")
        f.write(b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, SR, SR * 2, 2, 16))
        f.write(b"data" + struct.pack("<I", len(b)) + b)
    return file_path


def processed(name, x):
    """What auphonic.com might make of it: the ends of the band and the
    level changed, the timing not."""
    raw = write("raw_" + name, x)
    out = os.path.join(T, name)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af",
                    "highpass=f=80,lowpass=f=8000,volume=-4dB",
                    "-c:a", "pcm_s16le", out], check=True)
    return out


def returned(name, sent, back):
    """The return check over one track; (its answer, the track, its log)."""
    folder = os.path.join(T, name)
    os.makedirs(folder)
    track = {"name": name, "axis": sent, "done": back}
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        answer = vpm.verify_returned_tracks([track], TAKE_S, folder)
    return answer, track, said.getvalue()


def numbers(answer, track):
    return ("the answer was %r: offset %s ms, the return %.2f s against "
            "%.2f s sent, spread %s ms"
            % (answer, "--" if track.get("offset_ms") is None
               else "%.1f" % track["offset_ms"],
               vpm.sample_count(track["done"]) / float(SR),
               vpm.sample_count(track["axis"]) / float(SR),
               "--" if track.get("residual_ms") is None
               else "%.1f" % track["residual_ms"]))


take = speech_like(TAKE_S, seed=3)
sent = write("sent.wav", take)
this_week = write("this_week.wav", take[::-1])
n = len(take)

print("Right returns")
answer, track, _said = returned("Processed", sent, processed("p.wav", take))
check("a processed return of the take is accepted", answer is True,
      numbers(answer, track))
frame = processed("frame.wav", take[:n - int(0.1 * SR)])
answer, track, _said = returned("Frame", sent, frame)
check("a return short by a lossy frame is still accepted", answer is True,
      numbers(answer, track) + ", 0.10 s taken off its end")
jingle = 0.2 * np.sin(2 * np.pi * 440 * np.arange(int(6.4 * SR)) / SR)
tail = 0.2 * np.sin(2 * np.pi * 330 * np.arange(int(6.0 * SR)) / SR)
around = processed("around.wav", np.concatenate([jingle, take, tail]))
answer, track, _said = returned("Around", sent, around)
check("a return with a jingle in front and a tail is accepted",
      answer is True, numbers(answer, track) + ", 6.4 s in front, 6.0 behind")

print("\nReturns that are not the take")
last_week = processed("last_week.wav", take[:int(32.0 * SR)])
answer, track, said_last_week = returned("LastWeek", this_week, last_week)
check("last week's take, 12 s shorter, is refused", answer is False,
      numbers(answer, track) + ", forward against reversed")
answer, track, _said = returned("Reversed", sent,
                                processed("reversed.wav", take[::-1]))
check("the take reversed at full length is refused", answer is False,
      numbers(answer, track))
answer, track, _said = returned(
    "OtherVoice", sent, processed("other.wav", speech_like(TAKE_S, seed=11)))
check("another voice of the same length is refused", answer is False,
      numbers(answer, track))
answer, track, _said = returned(
    "Trimmed", sent, processed("trimmed.wav", take[:n - int(3.0 * SR)]))
check("the take with its last 3 s gone is refused", answer is False,
      numbers(answer, track) + ", 3.00 s taken off its end")

print("\nHow a refusal is said")
said = vpm.T('   Caution: %s s of what went up is not in it').split("%s")[1]
line = next((x for x in said_last_week.splitlines() if "LastWeek" in x
             and "offset" in x), "")
check("the refused track's line says what went up is not in it",
      said in line, "the line: %r" % line.strip()[:160])
REFUSED = vpm.T('  -->  refused')
ALIGNED = vpm.T('  -->  aligned')
check("and that it is refused, not that it was aligned",
      REFUSED in line and ALIGNED not in line,
      "the line: %r" % line.strip()[:160])
UNDER_REFUSED = vpm.T('\n  Refused: %s -- what came back does not match '
                      'what went up. Better to\n  stop than to write '
                      'something wrong.')
UNDER_UNSURE = vpm.T('\n  For %s it could not be established whether the '
                     'return matches the\n  upload. Better to stop than to '
                     'write something wrong.')
check("under the lines it is named refused, not left unsure",
      UNDER_REFUSED % "LastWeek" in said_last_week
      and UNDER_UNSURE % "LastWeek" not in said_last_week,
      "the log's last lines: %r" % said_last_week.strip()[-160:])
noise = np.random.default_rng(1).normal(size=n) * 0.1
answer, track, said_noise = returned("Noise", sent,
                                     write("noise.wav", noise))
check("a return of noise is left unsure, not named refused",
      answer is False and UNDER_UNSURE % "Noise" in said_noise
      and UNDER_REFUSED % "Noise" not in said_noise,
      numbers(answer, track) + ", the log's last lines: %r"
      % said_noise.strip()[-160:])

print("\nA return of the whole range, trimmed to the window")
# The window is the take, 76 s into a range of 120 s that went up
# before an In point was set; past a minute in, the trim is the way.
RANGE_S, SHIFT_S = 120.0, 76.0
recording = speech_like(RANGE_S, seed=7)
recording[int(SHIFT_S * SR):int(SHIFT_S * SR) + n] = take


def trimmed(name, seconds):
    """The range as long as *seconds* handed in by --auphonic-done, then
    checked: (taken, the return check's answer, the track)."""
    folder = os.path.join(T, name)
    os.makedirs(folder)
    write(os.path.join(name, "Guest.wav"), recording[:int(seconds * SR)])
    track = {"name": "Guest", "axis": sent}
    args = types.SimpleNamespace(auphonic_done=folder,
                                 without_auphonic=False)
    with contextlib.redirect_stdout(io.StringIO()):
        taken = vpm.processed_tracks_taken(args, [track], folder,
                                           {"Guest": TAKE_S}, RANGE_S,
                                           SHIFT_S)
        answer = vpm.verify_returned_tracks([track], TAKE_S, folder)
    return taken, answer, track


taken, answer, track = trimmed("Whole", RANGE_S)
check("a trimmed return of the whole range is accepted",
      taken is True and answer is True and track.get("edge"),
      "taken %r, edge %r, %s" % (taken, track.get("edge"),
                                 numbers(answer, track)))
taken, answer, track = trimmed("Short", RANGE_S - 14.0)
check("one whose file lacks the take's last 14 s is refused",
      taken is True and answer is False and track.get("edge"),
      "taken %r, edge %r, %s, the file as it came %.2f s"
      % (taken, track.get("edge"), numbers(answer, track),
         RANGE_S - 14.0))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
