# -*- coding: utf-8 -*-
"""A reading that fails costs its tracks the cut, and the log says so.

Reading the microphones can go wrong -- a file the decoder will not
take, a machine out of memory -- and until 31.8.2026 the run died of it.
Now it carries on, and that is better, but it is a swallowed failure:
the people on those tracks are in the mix and on no camera, and the only
place that can say so is the log.

So: the call comes back instead of throwing, the log names every track
that fell out of the cut and repeats what the reading said went wrong,
the voices a separation found are still there, and the tracks that were
not measured really are missing -- the price of going on, counted.

The failure is staged: a reading that refuses is what is being asked
about, and no real file refuses to order.
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

D = tempfile.mkdtemp(prefix="vpmfailread_")
MIC = os.path.join(D, "Mic_Anna.wav")
ROOM = os.path.join(D, "room.wav")
CAM = os.path.join(D, "CamOne.mov")
with wave.open(MIC, "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(8000)
    f.writeframes(b"\0" * 16000)
with open(ROOM, "wb") as f:
    f.write(b"\0" * 16)
with open(CAM, "wb") as f:
    f.write(b"\0" * 16)

# The room recording was taken apart and holds two voices; Anna's
# microphone was not, so she is the one the reading was for.
VOICES = [("Bea", [(11.5, 16.5)]), ("Cid", [(31.0, 36.5)])]
MINE = "Anna"
# What the reading complains about. Made of words no other line of the
# log carries, so finding it in there means the reason travelled and not
# that something else happens to say the same.
REASON = "the decoder would not take Xylophon_08"
WANTED_NAMES = ["Bea", "Cid"]


def reading_that_fails(tracks, note=None, **rest):
    """A reading that refuses, the way a broken file makes it refuse.

    It throws where the real one throws -- out of the call, with a
    message -- and it throws before answering anything, so nothing can
    reach the cut through a half-filled result.
    """
    raise ValueError(REASON)


class Args(object):
    pass


args = Args()
args._speakers = (VOICES, "the separation in this run")
args._separated = [ROOM]
TRACKS = [{"name": MINE, "axis": MIC, "camera": CAM, "blocks": [MIC]},
          {"name": "Room", "axis": ROOM, "camera": "", "blocks": [ROOM]}]

was = vpm.speakers_from_tracks
vpm.speakers_from_tracks = reading_that_fails
fell = None
out = None
try:
    with contextlib.redirect_stdout(io.StringIO()) as log:
        out = vpm.speakers_for_the_cut(args, TRACKS)
except Exception as e:                        # noqa: BLE001 -- the subject
    fell = "%s: %s" % (type(e).__name__, str(e)[:80])
finally:
    vpm.speakers_from_tracks = was
text = log.getvalue()

print("1. The run goes on")
check("a reading that fails comes back instead of throwing",
      fell is None, "it threw %s, wanted no fault" % (fell or "-",))

print("\n2. And the log says what it cost")
# The name and the reason on one line, because that is the only place a
# person can learn it: the cut list afterwards shows a person missing
# and never says why. Two checks, so a red line names which half is
# gone rather than "the log is wrong somewhere".
carries = [line for line in text.splitlines() if REASON in line]
check("the reason the reading gave reaches the log",
      len(carries) == 1, "%d lines of %d carry it, wanted 1"
      % (len(carries), len(text.splitlines())))
check("and it names the track that fell out of the cut",
      bool(carries) and MINE in carries[0],
      "the line is %r, and it should hold %r"
      % ((carries[0].strip()[:90] if carries else "not there"), MINE))

print("\n3. And what is left of the cut")
names = [n for n, _segs in (out or ())]
check("the voices a separation found are still in the cut",
      names == WANTED_NAMES, "the cut holds %d names %s, wanted %d %s"
      % (len(names), names, len(WANTED_NAMES), WANTED_NAMES))
check("and the track that was not read is not in it",
      MINE not in names, "the cut holds %s, and %s should not be among them"
      % (names, MINE))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
