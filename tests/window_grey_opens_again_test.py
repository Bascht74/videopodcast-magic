# -*- coding: utf-8 -*-
"""Every setting greyed out opens again once its reason is gone.

A greying that jams looks exactly like one that works: a dead control
and a sentence beside it explaining why, for ever. So each of the two
greyings is read twice -- shut while the reason holds and reaching no
further, open again once it is gone -- and the note under it both
times, as a widget with a name rather than a hint on a control. In
order: the settings the cut box builder hands over, the wide shot's
greying, the words', and the two settings both of them reach, which
are open only where both say so. No window is opened.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")

os.environ["QT_QPA_PLATFORM"] = "offscreen"

import importlib.util

from PySide6 import QtWidgets
from PySide6.QtCore import Qt

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.set_language("en")

QUIET = vpm.COLOURS["quiet"]
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# The switch names are written out here rather than read from the
# program's own tuples: a test that takes its expectation from the very
# list the program greys by agrees with it however wrong both are.
# Sorted, so a list in a FAIL line reads the same on every machine.
EVERY_SETTING = ["edit-change-delay", "min-edit-duration",
                 "min-speech-to-switch", "on-monologue", "on-question",
                 "on-together", "on-uncertain", "reaction-lead",
                 "wide-after", "wide-latest", "wide-length", "wide-most"]
WIDE_NUMBERS = ["wide-after", "wide-latest", "wide-length", "wide-most"]
WIDE_BOXES = ["on-monologue", "on-together", "on-uncertain"]
# The two in both lists -- wide-after and wide-most -- are what makes
# the order matter; they stand in WIDE_NUMBERS and in WORDS_SETTINGS.
WORDS_SETTINGS = ["on-question", "reaction-lead", "wide-after", "wide-most"]
# Everything the words' greying has no business touching.
NOT_THE_WORDS = ["edit-change-delay", "min-edit-duration",
                 "min-speech-to-switch", "on-monologue", "on-together",
                 "on-uncertain", "wide-latest", "wide-length"]

alive = []  # the holders, so Qt does not collect the parts under them


def cut_box_build():
    """The cut box the window builds, without the window.

    The same three pieces in the same order: the settings and their
    parts, the tick for the edges, and the two notes hung underneath.
    """
    holder = QtWidgets.QWidget()
    into = QtWidgets.QVBoxLayout(holder)
    parts = {}
    vpm.cut_fields_build(into, parts)
    tick = QtWidgets.QCheckBox()
    into.addWidget(tick)
    wide_note = vpm.wide_note_build(vpm.label, QUIET)
    words_note = vpm.question_note_build(vpm.label, QUIET)
    into.addWidget(wide_note)
    into.addWidget(words_note)
    alive.append(holder)
    return parts, tick, wide_note, words_note


def dead(parts, keys):
    """Of these settings, the ones whose row and control are both dead."""
    return [k for k in keys
            if not parts[k][0].isEnabled() and not parts[k][1].isEnabled()]


def open_ones(parts, keys):
    """Of these settings, the ones whose row and control are both live."""
    return [k for k in keys
            if parts[k][0].isEnabled() and parts[k][1].isEnabled()]


def barred(box):
    """The stored values of the entries that cannot be chosen."""
    return [box.itemData(i) for i in range(box.count())
            if not box.model().item(i).isEnabled()]


def inked(box):
    """The stored values of the entries the list draws in the quiet colour."""
    return [box.itemData(i) for i in range(box.count())
            if box.itemData(i, Qt.ForegroundRole) is not None]


def wide_shut_in(parts, keys):
    """Of these drop-downs, the ones where the wide shot is barred."""
    return [k for k in keys if vpm.SHOT_WIDE in barred(parts[k][1])]


def wide_free_in(parts, keys):
    """Of these drop-downs, the ones where the wide shot is open and unmarked."""
    return [k for k in keys
            if barred(parts[k][1]) == [] and inked(parts[k][1]) == []]


def note_named(note):
    return (isinstance(note, QtWidgets.QLabel)
            and note.objectName() != "" and note.accessibleName() != "")


# Exactly, not at least: a setting added to the cut box and to neither
# greying would sit in no list below, and every judgement here would
# stay green while it went grey and never came back.
print("0. The ground: the settings the builder hands over")
parts, tick, wide_note, words_note = cut_box_build()
absent = [k for k in EVERY_SETTING if k not in parts]
unnamed = [k for k in sorted(parts) if k not in EVERY_SETTING]
check("the builder hands over exactly the settings named here",
      absent == [] and unnamed == [],
      "%d parts against %d names; missing %s, unnamed %s"
      % (len(parts), len(EVERY_SETTING), absent, unnamed))
if absent:
    # Without the parts every judgement below would be a KeyError, and a
    # traceback says less than the line above.
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)

print("\n1. Every camera carries a speaker, so there is no wide shot")
vpm.wide_settings_grey(parts, tick, wide_note, False, QUIET, True)
check("the four wide shot numbers are dead",
      dead(parts, WIDE_NUMBERS) == WIDE_NUMBERS,
      "%d of %d dead: %s"
      % (len(dead(parts, WIDE_NUMBERS)), len(WIDE_NUMBERS),
         dead(parts, WIDE_NUMBERS)))
check("the tick for the edges is dead with them", not tick.isEnabled(),
      "the tick is %s" % ("dead" if not tick.isEnabled() else "live"))
check("and the wide shot cannot be chosen in the three drop-downs",
      wide_shut_in(parts, WIDE_BOXES) == WIDE_BOXES,
      "%d of %d bar it: %s"
      % (len(wide_shut_in(parts, WIDE_BOXES)), len(WIDE_BOXES),
         wide_shut_in(parts, WIDE_BOXES)))
check("the wide shot's note carries a sentence and is shown",
      wide_note.text() != "" and not wide_note.isHidden(),
      "%d characters, %s"
      % (len(wide_note.text()),
         "hidden" if wide_note.isHidden() else "shown"))
check("the wide shot's note is a widget with a name, not a hint",
      note_named(wide_note),
      "%s, object name %r, name spoken %r"
      % (type(wide_note).__name__, wide_note.objectName(),
         wide_note.accessibleName()))

print("\n   ... and a camera comes free again")
vpm.wide_settings_grey(parts, tick, wide_note, True, QUIET, True)
check("the four wide shot numbers open again",
      open_ones(parts, WIDE_NUMBERS) == WIDE_NUMBERS,
      "%d of %d open: %s"
      % (len(open_ones(parts, WIDE_NUMBERS)), len(WIDE_NUMBERS),
         open_ones(parts, WIDE_NUMBERS)))
check("the tick for the edges opens with them", tick.isEnabled(),
      "the tick is %s" % ("live" if tick.isEnabled() else "dead"))
check("the wide shot can be chosen again in all three drop-downs",
      wide_free_in(parts, WIDE_BOXES) == WIDE_BOXES,
      "%d of %d free of a bar and of grey: %s"
      % (len(wide_free_in(parts, WIDE_BOXES)), len(WIDE_BOXES),
         wide_free_in(parts, WIDE_BOXES)))
check("and the wide shot's note is empty and out of sight again",
      wide_note.text() == "" and wide_note.isHidden(),
      "%d characters, %s"
      % (len(wide_note.text()),
         "hidden" if wide_note.isHidden() else "shown"))

print("\n2. No transcript is known yet")
parts, tick, wide_note, words_note = cut_box_build()
vpm.words_settings_grey(parts, words_note, False, True, QUIET)
check("the question's two settings and the wide shot's two are dead",
      dead(parts, WORDS_SETTINGS) == WORDS_SETTINGS,
      "%d of %d dead: %s, wanted %s"
      % (len(dead(parts, WORDS_SETTINGS)), len(WORDS_SETTINGS),
         dead(parts, WORDS_SETTINGS), WORDS_SETTINGS))
check("and the other eight settings are left alone",
      open_ones(parts, NOT_THE_WORDS) == NOT_THE_WORDS,
      "%d of %d still open: %s"
      % (len(open_ones(parts, NOT_THE_WORDS)), len(NOT_THE_WORDS),
         open_ones(parts, NOT_THE_WORDS)))
check("the words' note carries a sentence and is shown",
      words_note.text() != "" and not words_note.isHidden(),
      "%d characters, %s"
      % (len(words_note.text()),
         "hidden" if words_note.isHidden() else "shown"))
check("the words' note is a widget with a name, not a hint",
      note_named(words_note),
      "%s, object name %r, name spoken %r"
      % (type(words_note).__name__, words_note.objectName(),
         words_note.accessibleName()))

print("\n   ... and the transcript arrives")
vpm.words_settings_grey(parts, words_note, True, True, QUIET)
check("all four settings that need the words open again",
      open_ones(parts, WORDS_SETTINGS) == WORDS_SETTINGS,
      "%d of %d open: %s"
      % (len(open_ones(parts, WORDS_SETTINGS)), len(WORDS_SETTINGS),
         open_ones(parts, WORDS_SETTINGS)))
check("and the words' note is empty and out of sight again",
      words_note.text() == "" and words_note.isHidden(),
      "%d characters, %s"
      % (len(words_note.text()),
         "hidden" if words_note.isHidden() else "shown"))

# Two settings stand in both lists, and whichever greying runs last
# writes the widget. So each is asked whether it can prise open what
# the other shut, and that is asked in the order in which it could:
# with the one that shut them running first. A setting prised open is
# a live control that does nothing, under a note still saying why it
# is grey.
print("\n3. Where the two greyings meet on one setting")
parts, tick, wide_note, words_note = cut_box_build()
vpm.wide_settings_grey(parts, tick, wide_note, False, QUIET, True)
vpm.words_settings_grey(parts, words_note, True, False, QUIET)
check("words but no wide shot: the words cannot open what the wide "
      "shot's greying shut",
      dead(parts, EVERY_SETTING) == WIDE_NUMBERS,
      "%d of %d dead: %s, wanted %s"
      % (len(dead(parts, EVERY_SETTING)), len(WIDE_NUMBERS),
         dead(parts, EVERY_SETTING), WIDE_NUMBERS))
parts, tick, wide_note, words_note = cut_box_build()
vpm.words_settings_grey(parts, words_note, False, True, QUIET)
vpm.wide_settings_grey(parts, tick, wide_note, True, QUIET, False)
check("a wide shot but no words: the wide shot cannot open what the "
      "words' greying shut",
      dead(parts, EVERY_SETTING) == WORDS_SETTINGS,
      "%d of %d dead: %s, wanted %s"
      % (len(dead(parts, EVERY_SETTING)), len(WORDS_SETTINGS),
         dead(parts, EVERY_SETTING), WORDS_SETTINGS))
parts, tick, wide_note, words_note = cut_box_build()
vpm.wide_settings_grey(parts, tick, wide_note, True, QUIET, True)
vpm.words_settings_grey(parts, words_note, True, True, QUIET)
check("and where both say so every setting in the cut box is open",
      open_ones(parts, EVERY_SETTING) == EVERY_SETTING and tick.isEnabled(),
      "%d of %d open, the tick %s"
      % (len(open_ones(parts, EVERY_SETTING)), len(EVERY_SETTING),
         "live" if tick.isEnabled() else "dead"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
