# -*- coding: utf-8 -*-
"""The Kind field greys one entry, not the whole field.

A camera nobody is assigned to shows "Wide shot" although nobody said
so, and "Content" is barred while that holds: the file cannot be
content and have no speaker. The bar belongs on that one entry, with
the reason on it.

Not every sentence is a refusal. Where two cameras are marked as the
wide shot, the second is told which of them the cut takes; that entry
carries the sentence and stays open, because it can still be chosen.

And the derivation does not ask who answered the field last. A camera
without a speaker is the wide shot in the cut whatever the field says,
so it is shown as one even where somebody set it to "Content" by hand
-- unlike the wide shot bar, which a hand-picked Kind does lift.

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


def note(box, value):
    """The sentence standing on one entry of the list."""
    return box.itemData(list(vpm.CLIP_TYPES).index(value), Qt.ToolTipRole)


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
      note(box, vpm.TYPE_CONTENT) == why,
      "the entry says %r, wanted %r" % (note(box, vpm.TYPE_CONTENT), why))

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

print("\n4. Two cameras marked, and only one of them is cut to")
# No rule picks between two marked wide shots: the cut takes the first
# in the list. The others are told so. That is an explanation and not a
# refusal, so the entry it sits on stays open and stays black.
BOTH = ["Camera1.mov", "Camera2.mov"]
value, why, derived = vpm.kind_on_show(vpm.TYPE_WIDE, "Camera2.mov",
                                       BOTH, True)
check("the second one still shows the wide shot", value == vpm.TYPE_WIDE,
      "shows %r" % value)
check("nothing is derived about it", derived is False, str(derived))
check("and it is told which camera the cut takes",
      why == "the cut uses Camera1.mov", repr(why))
_cell, box = vpm.clip_kind_cell("Camera2.mov", value, why, QUIET, derived)
check("the sentence stands on the wide shot entry",
      note(box, vpm.TYPE_WIDE) == why,
      "the entry says %r, wanted %r" % (note(box, vpm.TYPE_WIDE), why))
check("that entry can still be chosen", barred(box) == [], str(barred(box)))
check("and it is not greyed", grey(box) == [], str(grey(box)))
check("no other entry carries the sentence",
      [v for v in vpm.CLIP_TYPES if note(box, v)] == [vpm.TYPE_WIDE],
      str([v for v in vpm.CLIP_TYPES if note(box, v)]))
# The first of the two has nothing to be told: it is the one cut to.
value, why, derived = vpm.kind_on_show(vpm.TYPE_WIDE, "Camera1.mov",
                                       BOTH, True)
check("the first of the two is told nothing", why == "", repr(why))
_cell, box = vpm.clip_kind_cell("Camera1.mov", value, why, QUIET, derived)
check("and no entry of its list carries a sentence",
      not [v for v in vpm.CLIP_TYPES if note(box, v)],
      str([v for v in vpm.CLIP_TYPES if note(box, v)]))

print("\n5. A hand-picked Kind does not lift the derivation")
# Deliberate, and the two bars differ on purpose. That a file sits
# nowhere on the time axis is a measurement, and an answer overrules a
# measurement: wide_shot_barred lets a hand-picked Kind through. That no
# speaker is assigned is the assignment itself, and the run goes by it
# -- wide_shots_of makes such a camera the wide shot whatever the field
# says, so a field reading "Content" would disagree with the episode.


# The program's own Value, not a stand-in for it, with the note
# clip_kind_bind puts on it when a person picks an entry.
BY_HAND = vpm.Value(vpm.TYPE_CONTENT)
BY_HAND.chosen_by_hand = True
UNTOUCHED = vpm.Value(vpm.TYPE_CONTENT)
value, why, derived = vpm.kind_on_show(BY_HAND.get(), "Camera1.mov",
                                       ["Camera1.mov"], False)
check("it is still shown as the wide shot", value == vpm.TYPE_WIDE,
      "shows %r" % value)
check("and still as derived", derived is True, str(derived))
check("with the reason naming the missing speaker",
      why == "because no speaker is assigned to it", repr(why))
_cell, box = vpm.clip_kind_cell("Camera1.mov", value, why, QUIET, derived,
                                vpm.wide_shot_barred("/m/Camera1.mov",
                                                     BY_HAND, ()))
check("Content stays barred all the same",
      barred(box) == [vpm.TYPE_CONTENT], str(barred(box)))
check("and that is what the run really cuts to",
      vpm.wide_shots_of(["Camera1.mov", "Camera2.mov"], {"Camera2.mov"},
                        []) == ["Camera1.mov"],
      str(vpm.wide_shots_of(["Camera1.mov", "Camera2.mov"],
                            {"Camera2.mov"}, [])))
# The other bar, on the same value, and it does not step back for an
# answer: a file with no timecode whose sound has nothing in common with
# the rest cannot be cut into the episode however firmly anybody says
# otherwise. Sebastian, 31.8.2026 -- it can only be a jingle.
check("the wide shot bar holds against a hand-picked Kind as well",
      vpm.wide_shot_barred("/m/Camera1.mov", BY_HAND,
                           ["/m/Camera1.mov"]) != "",
      repr(vpm.wide_shot_barred("/m/Camera1.mov", BY_HAND,
                                ["/m/Camera1.mov"])[:60]))
check("and bars the same file where nobody answered",
      bool(vpm.wide_shot_barred("/m/Camera1.mov", UNTOUCHED,
                                ["/m/Camera1.mov"])),
      "a file that sits nowhere on the axis is offered as the wide shot")

print("\n6. What the bar leaves alone")
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
