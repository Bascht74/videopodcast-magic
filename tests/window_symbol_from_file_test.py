# -*- coding: utf-8 -*-
"""The window's symbol is the picture in the file, and nowhere else.

The symbol stood in the window's own source as a PNG written out in
text, and nothing asked after it: a picture that would not build, or a
call site quietly dropped, opened a window with nothing on it and no
run said so.

In order: the symbol is built at all, it is pixel for pixel the picture
in the file, no piece carries a picture in its source any more, the
symbol is put on both the application and the window -- both, or the
Mac shows the Python rocket in the dock -- and last that a picture
which cannot be read leaves the symbol unbuilt rather than empty, since
the window only asks whether it was given one.

The picture is read here down a path this test builds itself, not
through the program's reader: a check that asks its subject with the
subject's eyes says only that the two agree.
"""
import ast
import os
import sys
import time
import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
# Where the picture lies. Spelt out here rather than asked of the
# program, so that a program pointed somewhere else is caught.
PICTURE = os.path.join(the_program.FOLDER, "desktop", "icon.png")
# The first eleven characters of any PNG written out as base64 text.
# They are the file's own first six bytes, which never change, so this
# finds such a block whatever picture is in it.
AS_TEXT = "iVBORw0KGgo"

os.environ["QT_QPA_PLATFORM"] = "offscreen"


from PySide6 import QtGui, QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")

# Premultiplied on both sides. A pixmap comes back premultiplied, and
# converting it away and back again moves 13 of 65536 pixels on the
# soft edges -- measured -- so the comparison is made in the format the
# window really holds and both sides are brought to it once.
HELD = QtGui.QImage.Format_ARGB32_Premultiplied

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def as_said(icon):
    """What an answer from app_icon is, in words and a number."""
    if icon is None:
        return "nothing"
    if icon.isNull():
        return "an icon holding 0 pictures"
    return "an icon holding %d pictures" % len(icon.availableSizes())


# ---------------------------------------------------------------- built

symbol = vpm.ui.app_icon(QtGui)
offered = [] if symbol is None else [(s.width(), s.height())
                                     for s in symbol.availableSizes()]
check("the window's symbol is built at all",
      symbol is not None and not symbol.isNull(),
      "app_icon gave %s, sizes %s" % (as_said(symbol), offered or "none"))

# --------------------------------------------------------- from the file

wanted = QtGui.QImage(PICTURE).convertToFormat(HELD)
got = QtGui.QImage() if symbol is None else symbol.pixmap(
    wanted.size()).toImage().convertToFormat(HELD)
apart = 0
alike = not wanted.isNull() and wanted.size() == got.size()
if alike:
    for y in range(wanted.height()):
        for x in range(wanted.width()):
            if wanted.pixel(x, y) != got.pixel(x, y):
                apart += 1
if wanted.isNull():
    said = "no picture read at all out of %d bytes at %s" % (
        os.path.getsize(PICTURE) if os.path.exists(PICTURE) else 0, PICTURE)
elif not alike:
    said = "file %dx%d against a symbol %dx%d" % (
        wanted.width(), wanted.height(), got.width(), got.height())
else:
    said = "%d of %d pixels differ, both %dx%d" % (
        apart, wanted.width() * wanted.height(),
        wanted.width(), wanted.height())
check("the symbol is the picture that lies in the file",
      alike and apart == 0, said)

# ------------------------------------------------------- and nowhere else

PIECES = the_program.pieces()
carriers = [name for name, body in PIECES if AS_TEXT in body]
check("no piece of the program carries a picture in its source",
      not carriers, "%d of %d pieces carry one: %s"
      % (len(carriers), len(PIECES), carriers or "none"))

# ------------------------------------------------------------ put on both

tree = ast.parse(dict(PIECES)["ui/__init__.py"])
built = set()
for node in ast.walk(tree):
    if (isinstance(node, ast.Assign) and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "app_icon"):
        built |= set(one.id for one in node.targets
                     if isinstance(one, ast.Name))
worn = []
for node in ast.walk(tree):
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "setWindowIcon" and len(node.args) == 1
            and isinstance(node.args[0], ast.Name)
            and node.args[0].id in built
            and isinstance(node.func.value, ast.Name)):
        worn.append((node.func.value.id, node.lineno))
check("the symbol is put on the application and on the window",
      len(set(who for who, _line in worn)) == 2,
      "%d of them wear it: %s" % (len(set(who for who, _line in worn)),
                                  worn or "nobody"))

# ------------------------------------------------------ nothing to build

piece = vpm.beside("desktop", program=vpm)
reader = piece.icon_bytes
try:
    piece.icon_bytes = lambda folder=None: b""
    empty = vpm.ui.app_icon(QtGui)
finally:
    piece.icon_bytes = reader
check("a picture that cannot be read leaves the symbol unbuilt",
      empty is None, "app_icon gave %s where the file read as 0 bytes"
      % as_said(empty))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
