# -*- coding: utf-8 -*-
"""A weak file's note names the way that placed it, not another one.

A recording the sound hardly places goes as the run lays it -- its
measurement, or its clock -- a camera at its timecode, and the note
beside each says which of the two rules it went by. Both are
read out of one weak_marks_show call, the way the window hands over the
measurement: the recording on both sheets, the tree and the file list,
the camera on the file list, where its note stands. The limit: the
measurement is laid here in the shape measure_time_axis gives.
"""
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import time
import the_program

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6 import QtWidgets

app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


RECORDING = "/tmp/vpm weak note/Host_REC0001.wav"
CAMERA = "/tmp/vpm weak note/SideCam_C002.mov"
# The finding under the name, asked for by its value.
BY_RUN = vpm.T('%s\n   sound not recognised; placed as the run '
               'places it').split("\n")[1].strip()
BY_CLOCK = vpm.T('%s\n   sound not recognised; placed by its '
                 'timecode').split("\n")[1].strip()

# Both weak and neither refused: each has its place.
tree = vpm.tree_build(["Recording", "Name", "belongs to", "Timecode",
                       "Speakers"])
row = vpm.tree_row(tree, None, [os.path.basename(RECORDING)])
nodes = dict((p, QtWidgets.QTreeWidgetItem([os.path.basename(p), "", ""]))
             for p in (RECORDING, CAMERA))
state = {"weak": [vpm.path_key(RECORDING), vpm.path_key(CAMERA)],
         "no_place": [], "clock_alone": [],
         "file_rows": [(row, RECORDING, os.path.basename(RECORDING))]}
vpm.weak_marks_show(state, nodes)


def said(text):
    """The finding in a note: its second line, or "" where it has none."""
    lines = text.splitlines()
    return lines[1].strip() if len(lines) > 1 else ""


print("1. The recording")
got = said(row[0].text())
check("a weak recording's row in the tree says the run places it",
      got == BY_RUN, "the tree says %r, wanted %r" % (got, BY_RUN))
got = said(nodes[RECORDING].text(2))
check("and so does its line in the file list",
      got == BY_RUN, "the list says %r, wanted %r" % (got, BY_RUN))

print("\n2. The camera")
got = said(nodes[CAMERA].text(2))
check("a weak camera's line in the file list names its timecode",
      got == BY_CLOCK, "the list says %r, wanted %r" % (got, BY_CLOCK))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
