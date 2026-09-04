# -*- coding: utf-8 -*-
"""A note too long for its place breaks into lines, and its box gives.

Three texts stood cut off in a user's window and in none of ours: the
note in the file column, the colour tag of the cameras, and the line
under the player. The first two are too long for the column they stand
in; the third fits here and not there, because a font family the style
sheet names is missing on that machine and the substitute builds wider
-- against a box pinned at its designed width.

The sections: a box pinned by box_room lets itself out when what
stands in it wants more, on this system and not on Windows alone; and
the two notes carry line breaks, so the widest line of each is
narrower than the sentence was. Measured in the face that is drawing,
both languages.

What this cannot show is what a particular substitute font measures on
somebody else's machine; it shows that neither text has to be drawn on
one line any more.
"""
import os
import sys
import time
import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["VPM_NO_UPDATE_CHECK"] = "1"

from PySide6 import QtWidgets, QtGui, QtCore

app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


metrics = QtGui.QFontMetrics(app.font())


def widest(text):
    """How wide the text is drawn: the widest of its lines."""
    return max(metrics.horizontalAdvance(line)
               for line in str(text).splitlines() or [""])


def on_one_line(text):
    """How wide the same text would be with the breaks taken out."""
    return metrics.horizontalAdvance(" ".join(str(text).split()))


# The shape a camera really writes, and the length of it: a shorter
# name would hide the place where a column cuts one off.
CAMERAS = [{"name": "GuestCam_01011858_C003.mov", "colour": (2, 2, 9),
            "logs": "AppleLog", "nominal": 25.0},
           {"name": "PresentersCam_01011855_C002.mov", "colour": (1, 1, 1),
            "logs": "Rec709", "nominal": 25.0},
           {"name": "WideCam_01011855_C001.mov", "colour": (9, 16, 9),
            "logs": "", "nominal": 25.0}]

print("1. A box pinned at its designed width lets itself out")
box = QtWidgets.QGroupBox("Room")
vpm.box_room(box, 120)
designed = box.width()
inside = QtWidgets.QVBoxLayout(box)
long_one = QtWidgets.QLabel("Start 10:15:23:00 virtual        "
                            "End 11:42:07:03 virtual")
inside.addWidget(long_one)
box.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
box.show()
app.processEvents()
wanted = inside.totalMinimumSize().width()
check("a box pinned to a width gives when its content wants more",
      box.width() >= wanted,
      "%d px designed, %d px wanted, %d px after -- on %s"
      % (designed, wanted, box.width(), sys.platform))
check("and the design is what it keeps where nothing wants more",
      designed == 120, "%d px against the 120 px it was given" % designed)

print("\n2. The note in the file column")
# Written out once per language rather than looped: the register of
# counter-proofs knows wordings, and one computed name would stand
# for two judgements of which only one was ever seen red.
vpm.set_language("en")
english = vpm.weak_note("GuestCam_01011858_C003.mov", True)
check("the English note about a file that fits nowhere breaks up",
      len(english.splitlines()) > 1
      and widest(english) < on_one_line(english),
      "%d line(s), widest %d px against %d px on one line"
      % (len(english.splitlines()), widest(english), on_one_line(english)))
vpm.set_language("de")
german = vpm.weak_note("GuestCam_01011858_C003.mov", True)
check("and so does the German one",
      len(german.splitlines()) > 1 and widest(german) < on_one_line(german),
      "%d line(s), widest %d px against %d px on one line"
      % (len(german.splitlines()), widest(german), on_one_line(german)))

print("\n3. The colour tag and the recording curve of the cameras")
vpm.set_language("en")
found = {b.field: b.text for b in vpm.compare_cameras(CAMERAS)}
tag = found.get(vpm.T('Colour tag'), "")
check("every camera's colour tag stands on a line of its own",
      len(tag.splitlines()) == len(CAMERAS)
      and widest(tag) < on_one_line(tag),
      "%d line(s) for %d cameras, widest %d px against %d px on one line"
      % (len(tag.splitlines()), len(CAMERAS), widest(tag),
         on_one_line(tag)))
curve = found.get(vpm.T('Capture curve'), "")
check("and so does every recording curve",
      len(curve.splitlines()) == 2 and widest(curve) < on_one_line(curve),
      "%d line(s) for 2 curves, widest %d px against %d px on one line"
      % (len(curve.splitlines()), widest(curve), on_one_line(curve)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
