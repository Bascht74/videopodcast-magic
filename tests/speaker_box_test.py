# -*- coding: utf-8 -*-
"""The chooser beside "One more speaker in" has to show which file.

That chooser is the only thing in the row saying which recording will
be listened to again. Qt cuts what does not fit off the end, and the
recordings of one session differ at the end, so several read alike. A
name that fits is shown whole; one that does not is shortened in the
middle and kept whole in a tooltip; the button hands on the untouched
path. Widths are asked of the box itself, because the font decides.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("VPM_SILENT", "1")
os.environ.setdefault("VPM_NO_UPDATE_CHECK", "1")
os.environ.setdefault("VPM_NO_SPEAKER_SPLIT", "1")
from PySide6 import QtWidgets

app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.set_language("en")

error = []
# A window that goes out of scope takes its children with it, so the
# holders are kept for the whole run.
kept = []


def check(name, ok, extra=""):
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append("%s -- %s" % (name, extra))


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


print("\n1. One recording keeps the name on the button")
row, paths, picked = row_of(["Room.wav"])
button = row.findChild(QtWidgets.QPushButton)
check("the name stands on the button",
      "Room" in button.text(), repr(button.text()))
check("and there is no chooser beside it",
      row.findChild(QtWidgets.QComboBox) is None)

print("\n2. Names the row has room for are shown whole")
SHORT = ["Room.wav", "Host_REC00009.wav", "Guest_REC00010.wav"]
row, paths, picked = row_of(SHORT)
which = row.findChild(QtWidgets.QComboBox)
check("more than one recording brings a chooser", which is not None)
shown = [which.itemText(i) for i in range(which.count())]
check("every name stands in it unshortened", shown == SHORT, str(shown))
room = text_room(which)
widest = max(which.fontMetrics().horizontalAdvance(s) for s in shown)
check("and the chooser is wide enough to draw the widest of them",
      widest <= room, "widest %d px, room %d px" % (widest, room))
check("the chooser carries no tooltip it does not need",
      not which.toolTip(), repr(which.toolTip()))

print("\n3. A name the row has no room for is shortened in the middle")
LONG = ["Kandidat_0008A_a_recording_name_far_too_long_for_the_row_"
        "take_17_channel_3.wav",
        "Kandidat_0008B_a_recording_name_far_too_long_for_the_row_"
        "take_18_channel_4.wav"]
row, paths, picked = row_of(LONG)
which = row.findChild(QtWidgets.QComboBox)
shown = [which.itemText(i) for i in range(which.count())]
check("the names are shortened", shown != LONG, str(shown[:1]))
check("but not at the end -- both ends of the name survive",
      all(s[:8] == whole[:8] and s[-8:] == whole[-8:]
          for s, whole in zip(shown, LONG)), str(shown))
check("so the two of them are still told apart",
      shown[0] != shown[1], str(shown))
room = text_room(which)
widest = max(which.fontMetrics().horizontalAdvance(s) for s in shown)
check("and what is left fits, so Qt takes nothing off besides",
      widest <= room, "widest %d px, room %d px" % (widest, room))
check("the chooser never grows past the room the row has",
      which.width() <= vpm.NAME_ROOM,
      "%d px against %d" % (which.width(), vpm.NAME_ROOM))
check("the whole name stands in the chooser's tooltip",
      which.toolTip() == LONG[0], repr(which.toolTip()))
which.setCurrentIndex(1)
app.processEvents()
check("and it follows what is chosen",
      which.toolTip() == LONG[1], repr(which.toolTip()))

print("\n4. What the button hands on is the path, whole")
button = row.findChild(QtWidgets.QPushButton)
button.click()
app.processEvents()
check("the button hands on the path of the chosen recording",
      picked == [paths[1]], str(picked))

print("")
assert not error, "%d wrong: %s" % (len(error), error)
print("all good")
