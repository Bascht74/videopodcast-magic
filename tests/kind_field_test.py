# -*- coding: utf-8 -*-
"""The Kind field greys one entry, not the whole field.

A camera nobody is assigned to shows "Wide shot" although nobody said
so, and "Content" is barred while that holds: the file cannot be
content and have no speaker. The bar belongs on that one entry, with
the reason on it.

The field itself was greyed as well, so every camera serving as the
wide shot carried grey words in a shut box while a camera showing
"Content" stood in black. Sebastian, on the picture: "Here you wanted
to grey out only Content and make it unselectable. Currently
everything is grey (too much)."
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")

os.environ["QT_QPA_PLATFORM"] = "offscreen"

import importlib.util

from PySide6 import QtWidgets
from PySide6.QtCore import Qt

app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.set_language("en")

QUIET = vpm.COLOURS["quiet"]
error = []


def check(name, ok, extra=""):
    print("  %-56s %s%s" % (name, "ok" if ok else "FAIL",
                            "" if ok else "   " + extra))
    if not ok:
        error.append(name)


def entries(box):
    """Every entry of the list: its value, whether it is barred, its ink."""
    out = []
    for i in range(box.count()):
        ink = box.itemData(i, Qt.ForegroundRole)
        out.append((box.itemData(i),
                    not box.model().item(i).isEnabled(),
                    ink.color().name() if ink is not None else ""))
    return out


def barred(box):
    return [value for value, shut, _ink in entries(box) if shut]


def grey(box):
    return [value for value, _shut, ink in entries(box) if ink]


print("1. A wide shot the program worked out itself")
# What the file list and the camera table both show for a camera
# nobody is assigned to: "Wide shot", with the reason on the entry it
# bars.
value, why, derived = vpm.kind_on_show(vpm.TYPE_CONTENT, "Camera1.mov",
                                       ["Camera1.mov"], False)
check("it shows the wide shot", value == vpm.TYPE_WIDE, "shows %r" % value)
check("without anybody having said so", derived is True, str(derived))
check("and it says why", bool(why), repr(why))

_cell, box = vpm.clip_kind_cell("Camera1.mov", value, why, QUIET, derived)
check("only Content cannot be chosen", barred(box) == [vpm.TYPE_CONTENT],
      "barred: %s of %s" % (barred(box), list(vpm.CLIP_TYPES)))
check("and only Content is greyed in the list",
      grey(box) == [vpm.TYPE_CONTENT],
      "greyed: %s of %s" % (grey(box), list(vpm.CLIP_TYPES)))
check("the field itself carries no colour of its own",
      "color" not in box.styleSheet(),
      "the whole field is set to %r, so every word in it is grey, "
      "not only Content" % box.styleSheet())
check("the field can still be answered", box.isEnabled(),
      "the field is dead")
check("and the reason stands on the barred entry",
      box.itemData(list(vpm.CLIP_TYPES).index(vpm.TYPE_CONTENT),
                   Qt.ToolTipRole) == why,
      "the entry says %r, wanted %r"
      % (box.itemData(list(vpm.CLIP_TYPES).index(vpm.TYPE_CONTENT),
                      Qt.ToolTipRole), why))

print("\n2. A wide shot somebody marked")
# The other direction: a mark is an answer, nothing is derived, and
# nothing may be barred or grey.
value, why, derived = vpm.kind_on_show(vpm.TYPE_WIDE, "Camera1.mov",
                                       ["Camera1.mov"], True)
check("it stays a wide shot", value == vpm.TYPE_WIDE, "shows %r" % value)
check("and nothing is derived", derived is False, str(derived))
_cell, box = vpm.clip_kind_cell("Camera1.mov", value, why, QUIET, derived)
check("nothing is barred", barred(box) == [], str(barred(box)))
check("nothing is greyed", grey(box) == [], str(grey(box)))
check("and the field carries no colour of its own",
      "color" not in box.styleSheet(), repr(box.styleSheet()))

print("\n3. A camera like any other")
value, why, derived = vpm.kind_on_show(vpm.TYPE_CONTENT, "Camera2.mov",
                                       ["Camera1.mov"], True)
_cell, box = vpm.clip_kind_cell("Camera2.mov", value, why, QUIET, derived)
check("it shows Content", value == vpm.TYPE_CONTENT, "shows %r" % value)
check("nothing is barred", barred(box) == [], str(barred(box)))
check("and the field carries no colour of its own",
      "color" not in box.styleSheet(), repr(box.styleSheet()))

print("\n4. What the bar leaves alone")
# Intro, outro and "ignore this video" are answers about the file
# itself and have nothing to do with who is assigned where.
value, why, derived = vpm.kind_on_show(vpm.TYPE_CONTENT, "Camera1.mov",
                                       ["Camera1.mov"], False)
_cell, box = vpm.clip_kind_cell("Camera1.mov", value, why, QUIET, derived)
open_ones = [v for v, shut, _ink in entries(box) if not shut]
check("intro, outro and ignore stay open",
      set(open_ones) == {vpm.TYPE_WIDE, vpm.TYPE_INTRO, vpm.TYPE_OUTRO,
                         vpm.TYPE_IGNORED},
      "open: %s" % (open_ones,))

print("\n%s" % ("ALL OK" if not error else "FAIL: " + ", ".join(error)))
sys.exit(1 if error else 0)
