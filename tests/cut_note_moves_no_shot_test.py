# -*- coding: utf-8 -*-
"""A name held on the picture moves nothing in the cut.

A voice that interjects for a moment would flash past unread, so a name
once shown stands for half a second. That is display and nothing else:
the preview has to show what Resolve will build. In order: that the
hold really holds, that the shots and the voices come back as they went
in, that the camera follows the cut at every moment, that no name is
invented, and that a jump shows the new place at once.
"""
import bisect
import copy
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("VPM_SILENT", "1")

import importlib.util

from PySide6 import QtCore, QtGui, QtWidgets, QtMultimedia
from PySide6 import QtMultimediaWidgets
from PySide6.QtCore import Qt

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.set_language("en")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def label(text, colour=None, bold=False):
    return QtWidgets.QLabel(text)


def hint(widget, text):
    widget.setToolTip(text)
    return widget


# No camera has a file: nothing is loaded, nothing is decoded, and the
# note is all that moves. Bo speaks for a fifth of a second, which is
# less than the hold and is the whole point of the material.
NEAR, FAR = "GuestCam_01011714_C003", "WideCam_01011812_C002"
CUT = [(0.0, 5.0, NEAR), (5.0, 10.0, FAR), (10.0, 15.0, NEAR)]
VOICES = [{"name": "Anna", "sections": [(0.0, 4.0), (11.0, 14.0)]},
          {"name": "Bo", "sections": [(4.6, 4.8), (6.0, 9.0)]},
          {"name": "Cem", "sections": [(11.2, 12.0)]}]
STEP_MS = 40
END_MS = 15000
# Written down here rather than read off the program: a test that takes
# its measure from the very number it judges agrees with it however far
# that number has moved.
HOLD_S = 0.5
CUT_BEFORE = copy.deepcopy(CUT)
VOICES_BEFORE = copy.deepcopy(VOICES)
NOBODY = vpm.T('No speaker')

CutPlayer = vpm.qt_cut_player(QtCore, QtGui, QtWidgets, Qt, QtMultimedia,
                              QtMultimediaWidgets, label, hint, vpm.COLOURS)
player = CutPlayer()
player.resize(640, 480)
player.show()
app.processEvents()
player.set(CUT, {}, {}, None, 0.0, 0.0, 15.0, None, [], {}, VOICES)
player.clock.stop()

print("0. What the player was handed")
check("the player took the three shots and the three voices",
      len(player.cut) == len(CUT_BEFORE)
      and len(player.speaking) == len(VOICES_BEFORE),
      "%d shots against %d, %d voices against %d"
      % (len(player.cut), len(CUT_BEFORE), len(player.speaking),
         len(VOICES_BEFORE)))

# The expectation, worked out the other way round: a set of moments per
# name and a bisection over the shot starts, where the program walks
# its lists. Two routes to the same answer, so a fault in one shows.
moments = [ms / 1000.0 for ms in range(0, END_MS + 1, STEP_MS)]
mine = {}
for voice in VOICES_BEFORE:
    for a, b in voice["sections"]:
        for i, t in enumerate(moments):
            if a <= t < b:
                mine.setdefault(i, []).append(voice["name"])
truth = [tuple(mine.get(i, ())) for i in range(len(moments))]
starts = [a for a, _b, _w in CUT_BEFORE]


def camera_at(t):
    """Which camera stands at t, or nothing past the end of the cut."""
    i = bisect.bisect_right(starts, t) - 1
    if i < 0 or t >= CUT_BEFORE[i][1]:
        return ""
    return CUT_BEFORE[i][2]


camera = [camera_at(t) for t in moments]

shown, cameras = [], []
for t in moments:
    player._follow_up(t)
    shown.append(player.note.speaking)
    cameras.append(player.note.camera)
player.clock.stop()

print("\n1. The hold holds")
# Every stand but the last, which the end of the sweep cuts short.
stands, since = [], 0
for i in range(1, len(shown)):
    if shown[i] != shown[since]:
        stands.append((moments[i] - moments[since], shown[since]))
        since = i
shortest = min(stands)[0] if stands else 0.0
check("the program holds a name for the half second measured against",
      vpm.NAME_HOLD_S == HOLD_S,
      "the program says %.3f s, this test measures against %.3f s"
      % (vpm.NAME_HOLD_S, HOLD_S))
check("a name once shown stands for at least half a second",
      bool(stands) and shortest >= HOLD_S,
      "%d stands, the shortest %.3f s against %.3f s; Bo is heard for "
      "0.200 s" % (len(stands), shortest, HOLD_S))

print("\n2. What the display leaves alone")
check("the shots the player goes by are the ones handed over",
      player.cut == [tuple(s) for s in CUT_BEFORE],
      "%r against %r" % (player.cut[:2], CUT_BEFORE[:2]))
check("the cut handed over comes back as it went in",
      CUT == CUT_BEFORE, "%d shots now against %d handed over: %r against "
      "%r" % (len(CUT), len(CUT_BEFORE), CUT[:2], CUT_BEFORE[:2]))
want_voices = [(v["name"], [tuple(x) for x in v["sections"]])
               for v in VOICES_BEFORE]
check("the speaker sections the note reads are the ones handed over",
      player.speaking == want_voices,
      "%r against %r" % (player.speaking, want_voices))
check("the voices handed over come back as they went in",
      VOICES == VOICES_BEFORE, "%r against %r" % (VOICES, VOICES_BEFORE))
wrong = [i for i, name in enumerate(cameras) if name != camera[i]]
check("the camera shown at every moment is the one the cut names there",
      not wrong,
      "%d of %d moments differ, the first at %.2f s: %r against %r"
      % (len(wrong), len(moments), moments[wrong[0]] if wrong else 0.0,
         cameras[wrong[0]] if wrong else "", camera[wrong[0]] if wrong
         else ""))

print("\n3. Nothing invented")
back = int(HOLD_S * 1000 / STEP_MS) + 1
made_up = []
for i, said in enumerate(shown):
    lately = set(truth[j] for j in range(max(0, i - back), i + 1))
    if said not in set("  ".join(x) or NOBODY for x in lately):
        made_up.append((moments[i], said))
check("no name is shown that nobody said within the hold before it",
      not made_up,
      "%d of %d moments invent one, the first at %.2f s: %r"
      % (len(made_up), len(moments), made_up[0][0] if made_up else 0.0,
         made_up[0][1] if made_up else ""))

print("\n4. A jump is a new place")
# Two tenths on, less than the hold: waiting there would keep the old
# name, and a jump is not waiting.
player.jump(11.0)
player.clock.stop()
before = player.note.speaking
player.jump(11.2)
player.clock.stop()
check("what stood before the jump is the name of the place left",
      before == "Anna", "%r against %r" % (before, "Anna"))
check("a jump to another place shows what is true there at once",
      player.note.speaking == "Anna  Cem",
      "%r against %r, two tenths on from %r"
      % (player.note.speaking, "Anna  Cem", before))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
