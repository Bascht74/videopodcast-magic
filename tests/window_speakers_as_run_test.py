# -*- coding: utf-8 -*-
"""The window's preview counts the same speakers as the run will.

Both sides answer the owner's rule -- everybody is in unless somebody
said "do not use" -- and they answer it in two different places: the run
in speakers_for_the_cut over its tracks, the window in
track_recordings_of and speakers_window_all over the rows of the
assignment table. A preview built from other speakers than the run uses
is worse than none, and both sides have really been wrong: a track whose
row had been set to "do not use" was still measured, and a track with no
camera of its own fell out of preview and run alike the moment any
recording was taken apart.

One assignment, read both ways. In order: the run puts the separation's
voices and both free microphones into the cut, the preview comes to the
same list, the track with no camera of its own stands in both, a row set
to "do not use" reaches neither, and the recording a separation speaks
for reaches neither. Then the same question about the clock: the run
rewrites every track onto the axis before it reads the speakers off
it, so the window has to read on that clock too, or the two hear the
same hour at two different lengths. Last the line on the third tab
that says which of the two the cut in front of somebody is standing
on.

The run's reading of the microphones is stood in for, and it hands back
exactly what the window's stored measurement holds -- otherwise the two
sides are given different material and the comparison says nothing.
"""
import contextlib
import io
import os
import sys
import tempfile
import time
import wave

import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")

began = time.time()
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


#------------------------------------- One assignment, read two ways

D = tempfile.mkdtemp(prefix="vpmwinsame_")
MIC = os.path.join(D, "Mic_Anna.wav")
MIC2 = os.path.join(D, "Mic_Guest.wav")
ROOM = os.path.join(D, "room.wav")
REC = os.path.join(D, "Recorder.wav")
CAM = os.path.join(D, "CamOne.mov")
for path in (MIC, MIC2):
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(8000)
        f.writeframes(b"\0" * 16000)
for path in (ROOM, REC, CAM):
    with open(path, "wb") as f:
        f.write(b"\0" * 16)

# Four rows. Anna has a microphone and a camera; the guest has a
# microphone and no camera of his own; the room recording is in the mix
# and was taken apart by voice, so the people in it are on screen
# through their voices; the fourth recorder was set to "do not use"
# after it had been measured, which is the case that broke.
APART = [ROOM]
FREE = "Anna"
NO_CAMERA = "Guest"
IN_THE_MIX = "Room"
LEFT_OUT = "Recorder"
VOICES = [("Bea", [(11.5, 16.5)]), ("Cid", [(31.0, 36.5)])]
LENGTH = 36.5
# What "Measure speakers now" left behind in the window: every row that
# stood at the time, the one since set aside included.
MEASURED = {"segments": [(FREE, [(5.0, 10.0), (18.0, 23.0)]),
                         (NO_CAMERA, [(24.0, 29.0)]),
                         (IN_THE_MIX, [(2.0, 38.0)]),
                         (LEFT_OUT, [(1.0, 39.0)])],
            "length": 39.0}
WANTED = ["Bea", "Cid", FREE, NO_CAMERA]

#--- the window's side
assign_lines = [((MIC,), vpm.Value(FREE), vpm.Value(CAM)),
                ((MIC2,), vpm.Value(NO_CAMERA), vpm.Value(vpm.MIX_ONLY)),
                ((ROOM,), vpm.Value(IN_THE_MIX), vpm.Value(vpm.MIX_ONLY)),
                ((REC,), vpm.Value(LEFT_OUT), vpm.Value(vpm.IGNORE_AUDIO))]
rows = vpm.track_recordings_of(assign_lines)
preview, _far = vpm.speakers_window_all(VOICES, LENGTH, MEASURED, rows, APART)
preview_names = [n for n, _p in preview]

#--- the run's side
SAID = dict(MEASURED["segments"])


def reading_of(tracks, note=None, **rest):
    """Stand in for the run's reading, with the window's own numbers.

    It answers what the window measured and nothing besides -- one entry
    per track, as speakers_from_tracks does -- and it opens every file
    it is handed, so it refuses the paths the real reading refuses.
    """
    for _name, path, _offset in tracks:
        with open(path, "rb"):
            pass
    return [(name, list(SAID.get(name) or [])) for name, _p, _o in tracks]


class Args(object):
    pass


args = Args()
args._speakers = (VOICES, "the separation in this run")
args._separated = APART
# The rows above as the run sees them: the row set to "do not use" is no
# track of the run at all, and a mix-only row is a track with no camera.
tracks = [{"name": FREE, "axis": MIC, "camera": CAM, "blocks": [MIC]},
          {"name": NO_CAMERA, "axis": MIC2, "camera": "", "blocks": [MIC2]},
          {"name": IN_THE_MIX, "axis": ROOM, "camera": "", "blocks": [ROOM]}]
was = vpm.speakers_from_tracks
vpm.speakers_from_tracks = reading_of
try:
    with contextlib.redirect_stdout(io.StringIO()):
        run_names = [n for n, _p in vpm.speakers_for_the_cut(args, tracks)]
finally:
    vpm.speakers_from_tracks = was

print("1. What the run makes of it")
print("   ", "run:", run_names, " preview:", preview_names)
# First, or the comparison below is green over two empty lists and the
# three that follow are green over nothing having reached either side.
check("the run puts the voices and every free microphone in the cut",
      run_names == WANTED, "the run holds %d names %s, wanted %d %s"
      % (len(run_names), run_names, len(WANTED), WANTED))

print("\n2. And the preview beside it")
check("the preview comes to the same speakers as the run",
      preview_names == run_names, "the preview holds %d names %s, the run %d %s"
      % (len(preview_names), preview_names, len(run_names), run_names))
check("a track with no camera of its own stands in both",
      NO_CAMERA in preview_names and NO_CAMERA in run_names,
      "%s stands in the preview %s and in the run %s, wanted in both"
      % (NO_CAMERA, NO_CAMERA in preview_names, NO_CAMERA in run_names))
check("a row set to \"do not use\" reaches neither of them",
      LEFT_OUT not in preview_names and LEFT_OUT not in run_names,
      "%s stands in the preview %s and in the run %s, wanted in neither"
      % (LEFT_OUT, LEFT_OUT in preview_names, LEFT_OUT in run_names))
check("and the recording a separation speaks for reaches neither",
      IN_THE_MIX not in preview_names and IN_THE_MIX not in run_names,
      "%s stands in the preview %s and in the run %s, wanted in neither"
      % (IN_THE_MIX, IN_THE_MIX in preview_names, IN_THE_MIX in run_names))

print("\n3. And it reads them on the clock the run uses")
import numpy as np
CLOCKED = os.path.join(D, "Clocked.wav")
SPEED, LONG, HZ = 1.02, 20.0, 8000
with wave.open(CLOCKED, "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(HZ)
    n = int(LONG * HZ)
    x = np.random.default_rng(3).normal(0.0, 0.002, n)
    for begin in (1.0, 8.0, 17.0):
        i0, i1 = int(begin * HZ), int((begin + 1.5) * HZ)
        x[i0:i1] += np.random.default_rng(4).normal(0.0, 0.3, i1 - i0)
    f.writeframes((np.clip(x, -0.99, 0.99) * 32000).astype("<i2").tobytes())
# Two per cent, not the thirty parts per million of a real recorder:
# the reading works in blocks of a tenth of a second, and a real drift
# would hide inside one block over twenty seconds. What is checked is
# that the number is applied and in which direction.
flat = dict(vpm.speakers_from_tracks([("One", CLOCKED, 0.0)])).get("One") or []
sped = dict(vpm.speakers_from_tracks(
    [("One", CLOCKED, 0.0, SPEED)])).get("One") or []
print("   ", "flat:", flat, " on the clock:", sped)
check("both readings find the three passages",
        len(flat) == 3 and len(sped) == 3,
        "%d passages flat, %d on the clock, wanted 3 each"
        % (len(flat), len(sped)))
if len(flat) == 3 and len(sped) == 3:
    check("a recorder running fast has its last passage pulled forward",
            abs(sped[2][0] - flat[2][0] / SPEED) < 0.15,
            "the last passage starts at %.2f s, wanted %.2f s, flat %.2f s"
            % (sped[2][0], flat[2][0] / SPEED, flat[2][0]))
    check("and its first one barely moves",
            abs(sped[0][0] - flat[0][0]) < 0.15,
            "%.2f s against %.2f s" % (sped[0][0], flat[0][0]))
check("a file the axis does not know runs at 1",
        vpm.audio_clock_of("/nowhere.wav", {}) == 1.0,
        "%r" % (vpm.audio_clock_of("/nowhere.wav", {}),))
check("and one it does keeps its own speed",
        vpm.audio_clock_of(CLOCKED, {vpm.path_key(CLOCKED): SPEED}) == SPEED,
        "%r" % (vpm.audio_clock_of(CLOCKED, {vpm.path_key(CLOCKED): SPEED}),))

print("\n4. And the third tab says what the cut stands on")
vpm.set_language("en")
said = dict((b, vpm.cut_basis_line(b, 3, 4163.0))
            for b in ("measured", "run", "auphonic"))
for b in ("measured", "run", "auphonic"):
    print("   %-9s %s" % (b, said[b][0]))
check("three bases, three different sentences",
        len(set(t for t, _c in said.values())) == 3,
        "%s" % [t for t, _c in said.values()])
check("the raw recordings are the provisional answer",
        said["measured"][1] == vpm.COLOURS["warning"]
        and "recordings" in said["measured"][0],
        "%s in %s" % (said["measured"][0], said["measured"][1]))
check("a finished run is the good one, with or without auphonic.com",
        said["run"][1] == vpm.COLOURS["good"]
        and said["auphonic"][1] == vpm.COLOURS["good"],
        "run %s, auphonic %s" % (said["run"][1], said["auphonic"][1]))
check("and auphonic.com is named where it did the work",
        "Auphonic" in said["auphonic"][0], said["auphonic"][0])

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
