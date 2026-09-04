# -*- coding: utf-8 -*-
"""Whatever is written into the Speakers cell can be read there.

That cell is filled minutes after the sheet was built -- a separation
reports when it is done -- so a column measured from its own contents
was measured while every cell was still empty, and everything written
in afterwards was cut off at the top and at the right.

Sections: the column is wide enough for the two captions that must not
wrap; a row grows to a text that wraps and comes back down when the
cell is emptied; everything the cell can show, up to the longest report
a separation can hand it, is readable in both languages; at the
narrowest window the program allows, none of it has to be scrolled
sideways; and a recording whose voices hang under it stays open while
its cell is written.

Measured offscreen on a tree built and filled by the same functions the
window uses, so what is measured here and what is drawn there cannot
drift apart.
"""
import os
import re
import sys
import time
import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtWidgets

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


# The narrowest the window can be made, read out of the program rather
# than written down here: a number kept in two places drifts apart.
NARROWEST = int(re.search(r"window\.setMinimumSize\((\d+),",
                          the_program.text()).group(1))
PATH = "/tmp/Presenter_2026-09-04.wav"


def sheet(width):
    """The assignment tree with three Speakers cells in it.

    Built the way assignment_fresh builds it: the rows first with
    empty cells, the columns measured, and only then the text -- which
    is the order that made the cell unreadable.
    """
    columns = [vpm.T('Audio recording'), vpm.T('Speaker name'),
               vpm.T('belongs to'), "Timecode", vpm.T('Speakers')]
    tree = vpm.tree_build(columns)
    cells, nodes = [], []
    for _i in range(3):
        node = vpm.tree_row(tree, None, [os.path.basename(PATH)])
        vpm.tree_field(tree, node, 1, QtWidgets.QLineEdit())
        box, cell = vpm.split_cell_build(PATH, lambda *_: None, node[4])
        vpm.tree_field(tree, node, 4, box)
        cells.append(cell)
        nodes.append(node)
    holder = QtWidgets.QWidget()
    rows = QtWidgets.QVBoxLayout(holder)
    rows.setContentsMargins(0, 0, 0, 0)
    rows.addWidget(tree, 1)
    holder.resize(width, 700)
    for c in range(len(columns)):
        tree.resizeColumnToContents(c)
    tree.setColumnWidth(0, max(220, tree.columnWidth(0) + 30))
    tree.setColumnWidth(1, max(160, tree.columnWidth(1)))
    vpm.split_column_fit(tree, 4)
    holder.show()
    app.processEvents()
    return holder, tree, cells, nodes


def written(cells, text="", busy=False, found=0):
    """Fill the cells the way the window fills them, and no other way.

    Through split_cells_write itself, so the captions are the
    program's and not the test's: *text* arrives as the note hung on a
    recording, *busy* as a separation running on it, *found* as voices
    already stored for it. Nothing is laid out by hand afterwards --
    in the running program nobody does that either.
    """
    by_source = vpm.ByFile()
    if found:
        by_source[PATH] = {"segments": [("Speaker %d" % (i + 1), [])
                                        for i in range(found)]}
    note = (os.path.abspath(PATH), text, "#888888") if text else None
    vpm.split_cells_write(cells, busy, PATH if busy else "",
                          by_source, note)
    app.processEvents()


def unreadable(mark):
    """How many pixels of the text do not fit, in either direction.

    A wrapping label is cut at the top: it makes as many lines as it
    needs and the row shows the last of them. One that does not wrap
    is cut at the right instead. Both read the same way to somebody
    looking at it, so both come back as one number.
    """
    if mark.wordWrap():
        return mark.heightForWidth(max(1, mark.width())) - mark.height()
    return mark.sizeHint().width() - mark.width()


def missing_caption():
    return vpm.T('Speaker separation not available. The log says why.')


def reported_caption():
    """The longest the cell can be made to show.

    speaker_split_done hands it up to 200 characters of what the
    separation itself reported, so short captions are not the whole of
    what has to fit in there.
    """
    return vpm.T('The speaker separation reports: %s') % (
        "ImportError: Can't determine version for bottleneck, raised "
        "while the pipeline that tells voices apart was being built")


print("\n1. The column is measured for what it will hold")
vpm.set_language("en")
holder, tree, cells, nodes = sheet(NARROWEST)
room = tree.columnWidth(4)
mark_font = cells[0][2].fontMetrics()
button_wide = cells[0][1].sizeHint().width()
running = vpm.T('Separating speakers ...')
counted = vpm.TN(2, 'Separated: %d speaker', 'Separated: %d speakers') % 2
check("the column holds the running caption and its button",
      room >= mark_font.horizontalAdvance(running) + button_wide,
      "%d px of column against %d px of caption and %d px of button"
      % (room, mark_font.horizontalAdvance(running), button_wide))
check("and the finished count without wrapping it",
      room >= mark_font.horizontalAdvance(counted),
      "%d px of column against %d px of caption"
      % (room, mark_font.horizontalAdvance(counted)))

print("\n2. The row grows to the text and comes back down")
seat = cells[0][3]
written(cells)
empty_row = tree.rowHeight(seat.index())
written(cells, missing_caption())
tall_row = tree.rowHeight(seat.index())
written(cells)
back_row = tree.rowHeight(seat.index())
check("a cell whose text has to wrap gets a taller row",
      tall_row > empty_row,
      "%d px of row for the wrapped text against %d px for an empty "
      "cell" % (tall_row, empty_row))
check("and the row comes back down when the cell is emptied",
      back_row <= empty_row,
      "%d px of row after emptying against %d px when it was empty"
      % (back_row, empty_row))
holder.deleteLater()

print("\n3. Everything the cell can show is readable, both languages")
over = {"missing": [], "running": [], "counted": [], "reported": [],
        "button": []}
for language in ("en", "de"):
    vpm.set_language(language)
    holder, tree, cells, nodes = sheet(NARROWEST)
    _path, button, mark, _item = cells[0]
    written(cells, missing_caption())
    over["missing"].append((language, unreadable(mark), mark.width(),
                            mark.height()))
    written(cells, busy=True)
    over["running"].append((language, unreadable(mark), mark.width(),
                            mark.height()))
    over["button"].append((language,
                           button.sizeHint().width() - button.width(),
                           button.width(), button.sizeHint().width()))
    written(cells, found=2)
    over["counted"].append((language, unreadable(mark), mark.width(),
                            mark.height()))
    written(cells, reported_caption())
    over["reported"].append((language, unreadable(mark), mark.width(),
                             mark.height()))
    holder.deleteLater()
check("the sentence pointing at the log is readable in full",
      all(x[1] <= 0 for x in over["missing"]),
      "short by %s"
      % ["%s: %d px over in a label %dx%d" % x for x in over["missing"]])
check("the running caption is readable beside its button",
      all(x[1] <= 0 for x in over["running"]),
      "short by %s"
      % ["%s: %d px over in a label %dx%d" % x for x in over["running"]])
check("a finished count of speakers is readable in full",
      all(x[1] <= 0 for x in over["counted"]),
      "short by %s"
      % ["%s: %d px over in a label %dx%d" % x for x in over["counted"]])
check("a long reason from the separation is readable in full",
      all(x[1] <= 0 for x in over["reported"]),
      "short by %s"
      % ["%s: %d px over in a label %dx%d" % x for x in over["reported"]])
check("the button keeps its whole caption while a separation runs",
      all(x[1] <= 0 for x in over["button"]),
      "short by %s"
      % ["%s: %d px missing, %d px of %d" % x for x in over["button"]])

print("\n4. Nothing has to be scrolled sideways")
vpm.set_language("de")
holder, tree, cells, nodes = sheet(NARROWEST)
written(cells, missing_caption())
wanted = sum(tree.columnWidth(c) for c in range(5))
check("at the narrowest window the columns fit the width there is",
      wanted <= tree.viewport().width()
      and tree.horizontalScrollBar().maximum() == 0,
      "%d px of columns in a viewport %d px wide, scroll range 0..%d, "
      "window at least %d px"
      % (wanted, tree.viewport().width(),
         tree.horizontalScrollBar().maximum(), NARROWEST))
holder.deleteLater()

print("\n5. A recording that is open stays open while its cell is written")
# The voices hang under their recording, and the height of a row is put
# right by laying the items out again -- which must not fold the tree
# up under the hand that opened it.
holder, tree, cells, nodes = sheet(NARROWEST)
vpm.tree_row(tree, nodes[0], ["Speaker 1"])
tree.setExpanded(nodes[0][0].index(), True)
was_open = tree.isExpanded(nodes[0][0].index())
written(cells, missing_caption())
check("a recording with voices under it stays open when its cell is "
      "written", was_open and tree.isExpanded(nodes[0][0].index()),
      "open before %r, open after %r"
      % (was_open, tree.isExpanded(nodes[0][0].index())))
holder.deleteLater()

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
