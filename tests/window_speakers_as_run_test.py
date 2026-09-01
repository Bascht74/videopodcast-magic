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
for reaches neither.

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

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
