# -*- coding: utf-8 -*-
"""The chooser beside "One more speaker in" has to show which file.

That chooser is the only thing in the row saying which recording will
be listened to again. Qt cuts what does not fit off the end, and the
recordings of one session differ at the end, so several read alike. In
order: one recording, which keeps its name on the button and gets no
chooser at all; names the row has room for, shown whole and without a
tooltip; a name it has no room for, shortened in the middle, still told
apart from its neighbour and kept whole in a tooltip that follows the
choice; and last the button, which hands on the untouched path. Widths
are asked of the box itself, because the font decides.
"""
import os
import sys
import time
import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("VPM_SILENT", "1")
os.environ.setdefault("VPM_NO_UPDATE_CHECK", "1")
os.environ.setdefault("VPM_NO_SPEAKER_SPLIT", "1")
from PySide6 import QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")

done = 0
bad = []
# A window that goes out of scope takes its children with it, so the
# holders are kept for the whole run.
kept = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def verdict():
    """The one place the test ends -- every path leads through it."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


def row_of(names):
    """The button row for those recordings, laid out and measured."""
    paths = ["/tmp/nowhere/" + n for n in names]
    picked = []
    row = vpm.more_speakers_row(paths, picked.append)
    holder = QtWidgets.QWidget()
    box = QtWidgets.QVBoxLayout(holder)
    box.addWidget(row)
    kept.append(holder)
    holder.resize(1400, 200)
    holder.show()
    app.processEvents()
    return row, paths, picked


def text_room(which):
    """How much room the chooser leaves the name, in its own font."""
    option = QtWidgets.QStyleOptionComboBox()
    which.initStyleOption(option)
    field = which.style().subControlRect(
        QtWidgets.QStyle.CC_ComboBox, option,
        QtWidgets.QStyle.SC_ComboBoxEditField, which)
    return field.width()


def widest_of(which, names):
    """The widest of those names in the box's own font, in pixels."""
    return max([which.fontMetrics().horizontalAdvance(s) for s in names]
               or [0])


print("1. One recording keeps the name on the button")
row, paths, picked = row_of(["Room.wav"])
button = row.findChild(QtWidgets.QPushButton)
check("the name stands on the button",
      button is not None and "Room" in button.text(),
      "wanted 'Room' in the label, 1 button says %r"
      % (button.text() if button is not None else None))
check("and there is no chooser beside it",
      row.findChild(QtWidgets.QComboBox) is None,
      "1 recording, wanted 0 choosers in the row, found %d"
      % len(row.findChildren(QtWidgets.QComboBox)))

print("\n2. Names the row has room for are shown whole")
SHORT = ["Room.wav", "Host_REC00009.wav", "Guest_REC00010.wav"]
row, paths, picked = row_of(SHORT)
which = row.findChild(QtWidgets.QComboBox)
check("more than one recording brings a chooser", which is not None,
      "%d recordings, wanted 1 chooser in the row, found %d"
      % (len(SHORT), len(row.findChildren(QtWidgets.QComboBox))))
if which is None:
    # Nothing below can be measured without the chooser, and the count
    # has to be reached either way.
    verdict()
shown = [which.itemText(i) for i in range(which.count())]
check("every name stands in it unshortened", shown == SHORT,
      "wanted %d names %s, got %d names %s"
      % (len(SHORT), SHORT, len(shown), shown))
room = text_room(which)
widest = widest_of(which, shown)
check("and the chooser is wide enough to draw the widest of them",
      widest <= room, "widest %d px, room %d px" % (widest, room))
check("the chooser carries no tooltip it does not need",
      not which.toolTip(),
      "wanted 0 characters of tooltip, got %d: %r"
      % (len(which.toolTip()), which.toolTip()))

print("\n3. A name the row has no room for is shortened in the middle")
LONG = ["Guest_Take0021A_a_recording_name_far_too_long_for_the_row_"
        "take_17_channel_3.wav",
        "Guest_Take0021B_a_recording_name_far_too_long_for_the_row_"
        "take_18_channel_4.wav"]
row, paths, picked = row_of(LONG)
which = row.findChild(QtWidgets.QComboBox)
check("a long name brings a chooser too", which is not None,
      "%d recordings, wanted 1 chooser in the row, found %d"
      % (len(LONG), len(row.findChildren(QtWidgets.QComboBox))))
if which is None:
    verdict()
shown = [which.itemText(i) for i in range(which.count())]
check("the names are shortened", shown != LONG,
      "wanted fewer than %d characters, the first shows %d: %s"
      % (len(LONG[0]), len(shown[0]) if shown else 0, shown[:1]))
check("but not at the end -- both ends of the name survive",
      len(shown) == len(LONG)
      and all(s[:8] == whole[:8] and s[-8:] == whole[-8:]
              for s, whole in zip(shown, LONG)),
      "wanted the 8 first and 8 last characters of %s, got %s"
      % ([w[:8] + ".." + w[-8:] for w in LONG],
         [s[:8] + ".." + s[-8:] for s in shown]))
check("so the two of them are still told apart",
      len(shown) == 2 and shown[0] != shown[1],
      "wanted 2 different names, got %d: %s" % (len(set(shown)), shown))
room = text_room(which)
widest = widest_of(which, shown)
check("and what is left fits, so Qt takes nothing off besides",
      widest <= room, "widest %d px, room %d px" % (widest, room))
check("the chooser never grows past the room the row has",
      which.width() <= vpm.NAME_ROOM,
      "%d px against %d" % (which.width(), vpm.NAME_ROOM))
check("the whole name stands in the chooser's tooltip",
      which.toolTip() == LONG[0],
      "wanted %d characters %r, got %d characters %r"
      % (len(LONG[0]), LONG[0], len(which.toolTip()), which.toolTip()))
which.setCurrentIndex(1)
app.processEvents()
check("and it follows what is chosen",
      which.toolTip() == LONG[1],
      "chose entry 1, wanted %r, got %r" % (LONG[1], which.toolTip()))

print("\n4. What the button hands on is the path, whole")
button = row.findChild(QtWidgets.QPushButton)
button.click()
app.processEvents()
check("the button hands on the path of the chosen recording",
      picked == [paths[1]],
      "wanted 1 path %r, got %d: %s" % (paths[1], len(picked), picked))

verdict()
