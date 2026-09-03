# -*- coding: utf-8 -*-
"""The picture says who speaks and which camera runs, in the shot's colour.

One note serves both cases and only its height differs: under a picture
it is a strip of two lines, without one it covers the whole area. In
order: what the two lines carry, the four ways speech and the wide shot
can meet, the colour round the picture and on the note, the two
heights, and that the camera is named there and in no line under it.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("VPM_SILENT", "1")

import importlib.util

from PySide6 import QtCore, QtGui, QtWidgets, QtMultimedia
from PySide6 import QtMultimediaWidgets
from PySide6.QtCore import Qt

sys.path.insert(0, HERE)
from fixture_root import fixture

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


# Two cameras with a file, one without: the camera without a picture is
# where the note has to take the whole area instead of a strip.
MATERIAL = fixture("playertest")
NEAR = "GuestCam_01011714_C003"
WIDE = "WideCam_01011855_C001"
FAR = "PresentersCam_01011812_C002"
BLUE, ORANGE, GREEN = "#3465a4", "#cc7722", "#4e9a06"
CUT = [(0.0, 6.0, NEAR), (6.0, 12.0, WIDE), (12.0, 18.0, FAR)]
FILES = {NEAR: os.path.join(MATERIAL, "a.mp4"),
         FAR: os.path.join(MATERIAL, "b.mp4")}
COLOURS = {NEAR: BLUE, WIDE: ORANGE, FAR: GREEN}
VOICES = [{"name": "Anna", "sections": [(0.5, 3.0), (13.0, 17.0)]},
          {"name": "Bo", "sections": [(2.0, 5.0), (7.0, 9.0)]}]
NOBODY = vpm.T('No speaker')
MARK = vpm.T('(wide shot)')

print("0. The material and the cut")
there = [f for f in FILES.values() if os.path.exists(f)]
check("the two camera files the cut needs are there",
      len(there) == len(FILES),
      "%d of %d under %s" % (len(there), len(FILES), MATERIAL))

CutPlayer = vpm.qt_cut_player(QtCore, QtGui, QtWidgets, Qt, QtMultimedia,
                              QtMultimediaWidgets, label, hint, vpm.COLOURS)
player = CutPlayer()
player.resize(640, 480)
player.show()
app.processEvents()
player.set(CUT, FILES, {}, None, 0.0, 0.0, 18.0, None,
           [WIDE], COLOURS, VOICES)
check("the player took the three shots it was handed",
      len(player.cut) == len(CUT),
      "%d shots against %d" % (len(player.cut), len(CUT)))

# Handed a cut the player seeks, and its own timer runs until that
# lands. A tick between a move and a reading would put the note back to
# the start, so the seek is waited out and the timer stopped.
waited = QtCore.QElapsedTimer()
waited.start()
while player._seeking and waited.elapsed() < 8000:
    app.processEvents()
    QtCore.QThread.msleep(5)
player.clock.stop()
check("the player settled after it was handed the cut",
      not player._seeking, "seeking done after %d ms of at most 8000"
      % waited.elapsed())


def at(t):
    """Move the note to programme time t and give back what it shows.

    Through the player's own follow-up, not past it, so what is read
    here is what a running player would put on the screen. The moments
    are more than the hold apart, so no name is held over.
    """
    player._follow_up(t)
    app.processEvents()
    return player.note


print("\n1. The two lines")
note = at(1.0)
check("the note names the camera the cut names there",
      note.camera == NEAR, "%r against %r" % (note.camera, NEAR))
check("and who speaks at that moment",
      note.speaking == "Anna", "%r against %r" % (note.speaking, "Anna"))
note = at(2.5)
check("two speaking at once are both named",
      note.speaking == "Anna  Bo",
      "%r against %r" % (note.speaking, "Anna  Bo"))

print("\n2. Speech and the wide shot, all four ways")
note = at(4.0)
check("on an ordinary camera the name stands there without a mark",
      note.speaking == "Bo", "%r against %r" % (note.speaking, "Bo"))
note = at(5.5)
check("nobody on an ordinary camera says so, and says nothing else",
      note.speaking == NOBODY, "%r against %r" % (note.speaking, NOBODY))
note = at(8.0)
check("somebody on the wide shot keeps his name and gets the mark "
      "beside it", note.speaking == "Bo %s" % MARK,
      "%r against %r" % (note.speaking, "Bo %s" % MARK))
check("the wide shot is still named by its own file",
      note.camera == WIDE, "%r against %r" % (note.camera, WIDE))
note = at(10.0)
check("nobody on the wide shot says both: no speaker, and the mark",
      note.speaking == "%s %s" % (NOBODY, MARK),
      "%r against %r" % (note.speaking, "%s %s" % (NOBODY, MARK)))

print("\n3. The colour")
note = at(14.0)
check("the note carries the colour this shot has in the band",
      note.colour == GREEN, "%r against %r" % (note.colour, GREEN))
check("the same colour lies round the picture, and thicker than a hair",
      GREEN in player.stack.styleSheet()
      and "border: %dpx" % player.FRAME in player.stack.styleSheet(),
      "the box says %r, wanted %s at %d px"
      % (player.stack.styleSheet(), GREEN, player.FRAME))

print("\n4. One note, two heights")
box = player.box.rect()
strip = at(14.0).geometry()
picture = player.stack.geometry()
check("the note sits under the picture, not on it",
      strip.top() == picture.bottom() + 1
      and strip.height() >= player.note.line_room(),
      "the note starts at %d, the picture ends at %d, and it is %d high "
      "against at least %d"
      % (strip.top(), picture.bottom(), strip.height(),
         player.note.line_room()))
without = at(8.0).geometry()
check("without a picture the same note takes the whole box",
      without.top() == 0
      and without.height() == box.height() - player.GAP,
      "%d high from %d, against %d from 0"
      % (without.height(), without.top(), box.height() - player.GAP))
notes = player.box.findChildren(type(player.note))
check("one note serves both cases, not two displays",
      len(notes) == 1 and notes[0] is player.note,
      "%d notes under the picture" % len(notes))

print("\n5. Named there and nowhere else")
at(14.0)
also = [m.text() for m in player.findChildren(QtWidgets.QLabel)
        if m.text() == FAR]
check("the camera is named in the picture and in no line under it",
      not also, "%d labels under the video carry %r" % (len(also), FAR))

print("\n6. Which of the two lines is on top")
# Measured on the painted surface, not on the two values: reading the
# values back tells nothing about where they land, and that is how the
# camera and the speaker came to be the wrong way round through three
# versions with this test green the whole time.
#
# Written on one line at a time and the ink counted in each half. That
# holds whatever the font is, whatever it measures and wherever the
# text is centred -- unlike matching pixels against an expected shape.


def ink_halves(camera, speaking):
    """Paint the note with these two lines, and count the ink."""
    note.resize(320, note.line_room())
    note.show_shot("#ffffff", camera, speaking)
    picture = note.grab().toImage().convertToFormat(
        QtGui.QImage.Format_RGB32)
    high = picture.height()
    above = below = 0
    for y in range(high):
        for x in range(0, picture.width(), 2):
            if QtGui.qGray(picture.pixel(x, y)) < 200:
                if y < high // 2:
                    above += 1
                else:
                    below += 1
    return above, below


above, below = ink_halves("WideCam_A001", "")
check("the camera stands in the upper half of the note",
      above > 20 and below == 0, "%d dots above, %d below" % (above, below))
above, below = ink_halves("", "Guest")
check("and who speaks in the lower half",
      below > 20 and above == 0, "%d dots above, %d below" % (above, below))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
