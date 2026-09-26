# -*- coding: utf-8 -*-
"""A recording of several blocks keeps its misfit mark whatever block ran last.

The file list shows such a recording as one row, and every block of it
points at that row. Each block used to paint the row on its own, so a
later block that fits painted the first one's warning back to the
plain colour. Sections: a first block with no place and a later one
that fits, then a first block that is only weak; the note beside the
row as well as its colour; and a recording whose blocks all fit, which
stays plain.
"""
PLATFORM_BOUND = True
import os
import sys
import time
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import the_program

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
SCRIPT = the_program.SCRIPT
from PySide6 import QtGui, QtWidgets

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


FOLDER = "/tmp/vpm blocks"
FIRST = FOLDER + "/ZOOM0004_Tr1.WAV"
SECOND = FOLDER + "/ZOOM0004_Tr1-0001.WAV"
PLAIN = QtGui.QColor(vpm.COLOURS["text"]).name()
RED = QtGui.QColor(vpm.COLOURS["error"]).name()
AMBER = QtGui.QColor(vpm.COLOURS["warning"]).name()


def row_after(weak, no_place):
    """The one row both blocks point at, as the file list builds it."""
    node = QtWidgets.QTreeWidgetItem(["ZOOM0004_Tr1.WAV  + 1 continuation",
                                      "", FOLDER])
    # Block order as the list inserts them: the first block, then the next.
    vpm.weak_nodes_mark({FIRST: node, SECOND: node}, weak, no_place)
    return node.foreground(2).color().name(), node.text(2)


print("1. A first block with no place, a later block that fits")
ink, note = row_after((), (vpm.path_key(FIRST),))
check("a recording whose first block has no place stands in red",
      ink == RED,
      "the row is written in %s, wanted %s (error) and not %s (text)"
      % (ink, RED, PLAIN))
check("and its note still says the block does not fit",
      note != FOLDER and "\n" in note,
      "column 2 says %r, wanted the note and not the folder %r"
      % (note, FOLDER))

print("\n2. A first block that is only weak, a later block that fits")
ink, note = row_after((vpm.path_key(FIRST),), ())
check("a recording whose first block is weak stands in the warning colour",
      ink == AMBER,
      "the row is written in %s, wanted %s (warning) and not %s (text)"
      % (ink, AMBER, PLAIN))

print("\n3. Every block fits")
ink, note = row_after((), ())
check("a recording whose blocks all fit stays in the plain colour",
      ink == PLAIN and note == FOLDER,
      "the row is written in %s with %r, wanted %s (text) and %r"
      % (ink, note, PLAIN, FOLDER))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
