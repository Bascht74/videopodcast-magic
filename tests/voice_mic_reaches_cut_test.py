# -*- coding: utf-8 -*-
"""Every track is in the cut by its own microphone, or the log names it.

The owner's rule at the two places it is decided. First
separated_already, which lets a separation speak for a track only where
it was made of that track's own recording -- a track with no camera of
its own is measured like any other. Then speakers_for_the_cut, which
adds them up and names in the log whoever is not in the cut. The
reading is stood in for: what is asked is who is put into the cut, not
what a microphone sounds like, and the stand-in refuses what the real
reading refuses.
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
    os.path.dirname(HERE), "videopodcast_magic.py")

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


#------------------------------------------------------------- Material

D = tempfile.mkdtemp(prefix="vpmmiccut_")
ROOM = os.path.join(D, "room.wav")
MIC = os.path.join(D, "Mic_Anna.wav")
MIC2 = os.path.join(D, "Mic_Guest.wav")
CAM = os.path.join(D, "CamOne.mov")
# Real files, so the stand-in below can insist on opening them the way
# the real reading does. A second of silence is enough: nothing here
# listens to them.
for path in (ROOM, MIC, MIC2):
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(8000)
        f.writeframes(b"\0" * 16000)
with open(CAM, "wb") as f:
    f.write(b"\0" * 16)

# The room recording was taken apart by voice; Anna's microphone was not.
APART = [ROOM]


print("1. Who a separation speaks for")
sa = vpm.separated_already
# Anna: her own microphone, and a camera of her own in the assignment.
# The three fields below are the three ways a track can name a recording,
# and each of them has been the only one filled in a real project.
by_block = sa({"name": "Anna", "camera": CAM, "blocks": [ROOM]}, APART)
check("a separation speaks for the recording a track is made of",
      by_block is True, "answered %r, wanted True" % (by_block,))
by_source = sa({"name": "Anna", "camera": CAM, "source": ROOM}, APART)
check("and for the one a track names as its source",
      by_source is True, "answered %r, wanted True" % (by_source,))
by_camera = sa({"name": "Anna", "camera": CAM, "from_camera": CAM}, [CAM])
check("and for the camera a track was taken off",
      by_camera is True, "answered %r, wanted True" % (by_camera,))
free = sa({"name": "Anna", "camera": CAM, "blocks": [MIC]}, APART)
check("but not for a track it was not made of",
      free is False, "answered %r, wanted False" % (free,))
# The owner's decision of 31.8.2026, and the whole of what changed here:
# having no camera of its own is no longer an answer to this question.
# Otherwise the same person is in one run and out of the next, because
# somebody took an unrelated recording apart.
no_camera = sa({"name": "Guest", "camera": "", "blocks": [MIC2]}, APART)
check("and not for a track with no camera of its own",
      no_camera is False, "answered %r, wanted False" % (no_camera,))
alone_cam = sa({"name": "Anna", "camera": CAM, "blocks": [MIC]}, [])
alone_mix = sa({"name": "Guest", "camera": "", "blocks": [MIC2]}, [])
check("and without a separation for nothing at all",
      alone_cam is False and alone_mix is False,
      "with a camera %r, without one %r, wanted False and False"
      % (alone_cam, alone_mix))


print("\n2. What is put into the cut")
# What the separation of the room recording found. Anna is not in it --
# she was on her own microphone, and that is the whole case.
VOICES = [("Bea", [(11.5, 16.5)]), ("Cid", [(31.0, 36.5)])]
# What a reading of the three tracks says. One entry per track, which is
# what speakers_from_tracks answers whether or not anything was audible.
SAID = {"Anna": [(5.0, 10.0), (18.0, 23.0)], "Room": [(2.0, 38.0)],
        "Guest": [(24.0, 29.0)]}
WANTED = ["Bea", "Cid", "Anna", "Guest"]
handed = []


def reading_of(tracks, note=None, **rest):
    """Stand in for the reading, and refuse what the real one refuses.

    The real speakers_from_tracks decodes every file it is handed and
    answers one entry per track, a silent track included. Both are kept
    here: a stand-in that invents a track, or that takes a path nobody
    could open, makes the program look better than a run would.
    """
    for _name, path, _offset in tracks:
        with open(path, "rb"):
            pass
    handed.append([name for name, _p, _o in tracks])
    return [(name, list(SAID.get(name) or [])) for name, _p, _o in tracks]


class Args(object):
    pass


args = Args()
args._speakers = (VOICES, "the separation in this run")
args._separated = APART
TRACKS = [{"name": "Anna", "axis": MIC, "camera": CAM, "blocks": [MIC]},
          {"name": "Room", "axis": ROOM, "camera": "", "blocks": [ROOM]},
          {"name": "Guest", "axis": MIC2, "camera": "", "blocks": [MIC2]}]

was = vpm.speakers_from_tracks
vpm.speakers_from_tracks = reading_of
try:
    with contextlib.redirect_stdout(io.StringIO()) as log:
        out = vpm.speakers_for_the_cut(args, TRACKS)
finally:
    vpm.speakers_from_tracks = was
said = log.getvalue()
names = [n for n, _segs in out]
print("   ", [(n, len(s)) for n, s in out])

# The reading has to have happened at all, and over every track: a run
# in which nobody was measured would answer the checks below out of the
# separation alone and look right while measuring nothing.
check("the tracks were read, and every one of them",
      handed == [["Anna", "Room", "Guest"]], "handed %s, wanted %s"
      % (handed, [["Anna", "Room", "Guest"]]))
check("every voice of the separation stands in the cut",
      [n for n, _s in VOICES] == names[:len(VOICES)],
      "the cut holds %s, and the separation found %s"
      % (names, [n for n, _s in VOICES]))
mine = [segs for n, segs in out if n == "Anna"]
check("and the track no separation speaks for, by its own microphone",
      len(mine) == 1 and mine[0] == SAID["Anna"],
      "Anna stands %d times with %s, wanted once with %s"
      % (len(mine), mine[0] if mine else "nothing", SAID["Anna"]))
# The case the decision turned on: no camera of its own, and a
# separation of somebody else's recording standing beside it.
guest = [segs for n, segs in out if n == "Guest"]
check("and the track with no camera of its own, by its microphone too",
      len(guest) == 1 and guest[0] == SAID["Guest"],
      "Guest stands %d times with %s, wanted once with %s"
      % (len(guest), guest[0] if guest else "nothing", SAID["Guest"]))
check("the recording a separation was made of is not there beside them",
      names == WANTED, "the cut holds %d names %s, wanted %d %s"
      % (len(names), names, len(WANTED), WANTED))


print("\n3. And the log says who is not in the cut")
# A run that quietly holds fewer speakers than the sheet did is the
# fault this line exists for, so it is read out of the log itself.
front = vpm.T('  Not in the cut: %s -- a separation speaks for the '
              'recording, or it was not measured.').split("%s")[0]
line = ([ln for ln in said.split("\n") if ln.startswith(front)] or [""])[0]
print("    log line:", repr(line))
# First, or the two below are green over an empty string.
check("a run that leaves a track out prints a line saying so",
      bool(line), "found %r in %d lines of log, wanted a line under %r"
      % (line, len(said.split("\n")), front))
check("and the line names the track that is not in the cut",
      "Room" in line, "the line reads %r, wanted Room in it" % line)
also_in = [n for n in names if n in line]
check("and names nobody who stands in the cut",
      not also_in, "the line reads %r and holds %s, and the cut holds %s"
      % (line, also_in or "nobody", ", ".join(names)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
