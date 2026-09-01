# -*- coding: utf-8 -*-
"""The picture keeps its shape, and the note under it keeps to two lines.

Black over and under a picture is what this is against, so the shape is
measured off the frames. In order: the handler hooked up only once all
it reads exists, what stands before a measurement, the shape read off a
picture far from sixteen to nine, that the picture gives height up and
takes none, that a narrower camera does not pull it back, and the air.
The height the box itself gets is the layout's, and is not measured.
"""
import ast
import io
import os
import shutil
import subprocess
import sys
import tempfile
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


# Written down here, not read off the program: a test that takes its
# expectation from the number it judges agrees with it however it moves.
SIXTEEN_TO_NINE = 16.0 / 9.0
AIR = 8                        # the air under the note, in pixels
WIDE, HIGH = 800, 200          # the picture built below: four to one
CAMERA = "WideCam_01011855_C001"
folder = tempfile.mkdtemp(prefix="vpm_shape_")
clip = os.path.join(folder, "two_to_one.mp4")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "testsrc=size=%dx%d:rate=25:duration=3" % (WIDE, HIGH),
                "-pix_fmt", "yuv420p", clip], check=False)

CutPlayer = vpm.qt_cut_player(QtCore, QtGui, QtWidgets, Qt, QtMultimedia,
                              QtMultimediaWidgets, label, hint, vpm.COLOURS)
player = CutPlayer()
player.resize(640, 480)
player.show()
app.processEvents()

print("0. The handler for the frames")
# A signal Qt may deliver at once, hooked up while the object is still
# being built, reaches an object that is not there yet. Read as a tree:
# the line the signal is connected on has to come after every line that
# binds something the handler touches.
source = io.open(SCRIPT, encoding="utf-8").read()
start, handler = None, []
for node in ast.walk(ast.parse(source)):
    if not (isinstance(node, ast.ClassDef) and node.name == "CutPlayer"):
        continue
    for inner in node.body:
        if not isinstance(inner, ast.FunctionDef):
            continue
        if inner.name == "__init__":
            start = inner
        if inner.name in ("_shape_seen", "_note_place"):
            handler.append(inner)
touches = set()
for one in handler:
    for node in ast.walk(one):
        if isinstance(node, ast.Attribute) \
                and isinstance(node.value, ast.Name) \
                and node.value.id == "self":
            touches.add(node.attr)
bound = {}
for node in ast.walk(start or ast.parse("pass")):
    if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store) \
            and isinstance(node.value, ast.Name) and node.value.id == "self":
        bound.setdefault(node.attr, node.lineno)
hooked = [node.lineno for node in ast.walk(start or ast.parse("pass"))
          if isinstance(node, ast.Attribute)
          and node.attr == "videoSizeChanged"]
after = sorted((bound[name], name) for name in touches if name in bound)
check("the handler is found in the player at all",
      bool(handler) and bool(hooked) and bool(after),
      "%d handler bodies, %d places it is hooked up, %d names it reads "
      "that the build binds" % (len(handler), len(hooked), len(after)))
check("the handler is hooked up only once all it reads exists",
      bool(hooked) and bool(after) and min(hooked) > after[-1][0],
      "hooked up on line %s, and %r is bound on line %s"
      % (min(hooked) if hooked else 0, after[-1][1] if after else "",
         after[-1][0] if after else 0))

print("\n1. Before a picture has arrived")
check("the material for the test was built", os.path.exists(clip),
      "%s is %d bytes"
      % (clip, os.path.getsize(clip) if os.path.exists(clip) else 0))
check("with nothing measured the box stands at sixteen to nine",
      abs(player.shape - SIXTEEN_TO_NINE) < 0.001,
      "%.4f against %.4f" % (player.shape, SIXTEEN_TO_NINE))
player.set([(0.0, 3.0, CAMERA)], {CAMERA: clip}, {}, None, 0.0, 0.0, 3.0,
           None, [], {CAMERA: vpm.clip_colour_rgb("Orange")},
           [{"name": "Anna", "sections": [(0.0, 3.0)]}])
first = player.stack.geometry()
first_note = player.note.geometry()
box = player.box.rect()
check("the picture leaves the note its two lines and the air below",
      first.height() + player.note.line_room() + player.GAP
      <= box.height(),
      "the picture is %d high, the note wants %d and the air %d, in a "
      "box of %d" % (first.height(), player.note.line_room(), player.GAP,
                     box.height()))

print("\n2. The shape read off the picture")
player.play()
waited = QtCore.QElapsedTimer()
waited.start()
while abs(player.shape - SIXTEEN_TO_NINE) < 0.001 \
        and waited.elapsed() < 8000:
    app.processEvents()
    QtCore.QThread.msleep(5)
player.pause()
player.clock.stop()
check("a picture four to one is measured, not assumed",
      abs(player.shape - WIDE / float(HIGH)) < 0.01,
      "%.4f against %.4f after %d ms of at most 8000"
      % (player.shape, WIDE / float(HIGH), waited.elapsed()))
now = player.stack.geometry()
inside = (now.width() - 2 * player.FRAME) / float(
    max(1, now.height() - 2 * player.FRAME))
check("the picture is drawn at the shape that was measured",
      abs(inside - WIDE / float(HIGH)) < 0.02,
      "%d by %d inside the frame is %.4f, wanted %.4f"
      % (now.width() - 2 * player.FRAME, now.height() - 2 * player.FRAME,
         inside, WIDE / float(HIGH)))

print("\n3. It gives height up and takes none")
# What the picture gives up is only visible where its shape is what
# limits it. On a box wide enough for the shape, the height it is
# allowed limits it instead, and then it cannot shrink at all -- which
# is a fact about the box, not about the layout being wrong.
spare = player.box.height() - player.GAP - now.height()
check("the shape is what limits the picture here, not the room it has",
      spare > player.note.line_room(),
      "%d px left under the picture against the %d the note needs, in a "
      "box %d wide" % (spare, player.note.line_room(), player.box.width()))
check("a wider picture takes less height than a narrower one",
      now.height() < first.height(),
      "the picture went from %d to %d high at %.3f against %.3f"
      % (first.height(), now.height(), SIXTEEN_TO_NINE,
         WIDE / float(HIGH)))
check("what the picture gives up falls to the box, not to the note",
      player.note.height() == player.note.line_room()
      and player.note.height() == first_note.height(),
      "the note went from %d to %d high, wanting %d for its two lines, "
      "while the picture went from %d to %d"
      % (first_note.height(), player.note.height(),
         player.note.line_room(), first.height(), now.height()))
check("the picture never reaches past the box it sits in",
      player.box.rect().contains(now),
      "the picture is %d by %d at %d, the box %d by %d"
      % (now.width(), now.height(), now.x(), player.box.width(),
         player.box.height()))
player._shape_seen(QtCore.QSize(600, 800))
app.processEvents()
check("a narrower camera does not pull the shape back",
      abs(player.shape - WIDE / float(HIGH)) < 0.01,
      "%.4f after a picture of %.4f, wanted %.4f"
      % (player.shape, 600 / 800.0, WIDE / float(HIGH)))

print("\n4. The air at the foot")
# The note reaches as far down as it ever does only where the height
# limits the picture, not its shape. In a narrower box the air below
# the note is whatever the shape left over, and says nothing.
player.resize(1600, 480)
app.processEvents()
player._follow_up(1.0)
app.processEvents()
note = player.note.geometry()
check("air in the box's own colour stands under the note",
      player.box.height() - note.bottom() - 1 == AIR,
      "%d px of air under the note, wanted %d, the picture %d high in "
      "a box %d by %d"
      % (player.box.height() - note.bottom() - 1, AIR,
         player.stack.height(), player.box.width(),
         player.box.height()))

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
