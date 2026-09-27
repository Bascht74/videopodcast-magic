# -*- coding: utf-8 -*-
"""A recording of several blocks is marked by its first block's Kind.

Only the first block of a recording has a Kind field, and what it says
holds for every block behind the row. A first block set to Intro and a
later block with no place: the file list's row is not red and its note
says what became of the intro, the Assignment tab's row is not red
either, and the line under the list does not count it as refused. The
other way round: a Kind standing on a later block does not speak for
the recording, whose first block is content, so its row stays red.
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
CAPTION = "ZOOM0004_Tr1.WAV  (+1)"
RED = QtGui.QColor(vpm.COLOURS["error"]).name()
PLAIN = QtGui.QColor(vpm.COLOURS["text"]).name()


def both_after(kinds):
    """Both sheets and the line, the later block with no place.

    The file list's row is the one every block points at, the tree's row
    its cells and plain caption under the first block, as the two sheets
    keep them; *kinds* is the Kind fields, {file: its value}.
    """
    node = QtWidgets.QTreeWidgetItem([CAPTION, "", FOLDER])
    cells = [QtGui.QStandardItem(CAPTION) for _ in range(4)]
    state = {"weak": set(), "no_place": {vpm.path_key(SECOND)},
             "clip_kinds": vpm.ByFile(kinds),
             "file_rows": [(cells, FIRST, CAPTION)]}
    nodes = vpm.ByFile({FIRST: node, SECOND: node})
    vpm.weak_marks_show(state, nodes)
    refused, _by_clock = vpm.rows_off_the_axis(nodes, state)
    return (node.foreground(2).color().name(), node.text(2),
            cells[0].foreground().color().name(), refused)


print("1. The first block set to Intro, a later block with no place")
listed, note, assigned, refused = both_after(
    {FIRST: vpm.Value(vpm.TYPE_INTRO)})
check("a later misfit block of an intro is not red in the file list",
      listed != RED,
      "the row is written in %s, wanted anything but %s (error)"
      % (listed, RED))
decided = vpm.weak_decision(vpm.TYPE_INTRO, True)
check("and the row's note says what became of the intro",
      note.endswith(decided),
      "column 2 says %r, wanted it to end on %r" % (note, decided))
check("a later misfit block of an intro is not red on the tab",
      assigned != RED,
      "the tree's row is written in %s, wanted anything but %s (error)"
      % (assigned, RED))
check("and the line under the list does not count it as refused",
      refused == [],
      "refused %r, wanted none" % (refused,))

print("\n2. A Kind on a later block, the first block content")
listed, _note, assigned, refused = both_after(
    {FIRST: vpm.Value(vpm.TYPE_CONTENT), SECOND: vpm.Value(vpm.TYPE_INTRO)})
check("a Kind on a later block leaves the recording red on both",
      listed == RED and assigned == RED,
      "file list %s, tab %s, wanted %s (error) on both"
      % (listed, assigned, RED))
check("and the line counts that recording as refused",
      refused == [os.path.basename(SECOND)],
      "refused %r, wanted [%r]" % (refused, os.path.basename(SECOND)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
