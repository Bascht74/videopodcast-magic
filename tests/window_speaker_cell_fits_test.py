# -*- coding: utf-8 -*-
"""Whatever is written into the Speakers cell can be read there.

That cell is filled minutes after the sheet was built -- a separation
reports when it is done -- so a column measured from its own contents
was measured while every cell was still empty, and everything written
in afterwards was cut off at the top and at the right.

Sections: the column is wide enough for the two captions that must not
wrap; a row grows to a text that wraps and comes back down when the
cell is emptied; everything the cell can show, up to the longest report
a separation can hand it, is readable in both languages; the same again
in a font drawn as wide as the widest we build for; at the narrowest
window the program allows, in either language and across the fonts we
build for, the name field keeps a width somebody can type in and the
column carrying the button can be brought fully into view; and a
recording whose voices hang under it stays open while its cell is
written.

Measured offscreen on a tree built and filled by the same functions the
window uses, so what is measured here and what is drawn there cannot
drift apart. The height a text needs is worked out here by the font's
own bounding box, a different road from the one the program takes.

What the cell is given has to be asked for and not left to the label's
own offer, and that is a judgement of its own: the offer is right on
this machine and was 14 px short on the Windows builder, so a run here
can confirm the asking but never the offer.
"""
import os
import re
import sys
import time
import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtGui, QtWidgets

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
                          the_program.whole()).group(1))
PATH = "/tmp/Presenter_2026-09-04.wav"
# The same nominal font is drawn 1.89 times as wide on Windows as on
# this Mac -- measured on the builder over both languages, and written
# down beside WIDE_FONT in the program. A stretched font is that
# difference and nothing else: the glyphs get wider, the line height
# stays, which is exactly what makes a wrapping label need more lines
# than its own size hint admits.
WIDER = 189


def in_a_wider_font(times):
    """Draw everything from here on in a font that much wider."""
    was = QtWidgets.QApplication.font()
    wide = QtGui.QFont(was)
    wide.setStretch(times)
    QtWidgets.QApplication.setFont(wide)
    return was


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
    is cut at the right instead. The height it needs is worked out
    here by the font's own bounding box for a wrapped paragraph --
    a different road from the heightForWidth the program asks, so the
    judgement is not the program's arithmetic handed back to it.
    """
    if not mark.wordWrap():
        return mark.sizeHint().width() - mark.width()
    from PySide6 import QtCore
    box = mark.fontMetrics().boundingRect(
        QtCore.QRect(0, 0, max(1, mark.width()), 0),
        QtCore.Qt.TextWordWrap, mark.text())
    return box.height() - mark.height()


def needs(mark):
    """The height the wrapped text needs at the width the label has."""
    from PySide6 import QtCore
    return mark.fontMetrics().boundingRect(
        QtCore.QRect(0, 0, max(1, mark.width()), 0),
        QtCore.Qt.TextWordWrap, mark.text()).height()


def missing_caption():
    return vpm.T('Speaker separation not available. The log says why.')


def reported_caption():
    """The longest the cell can be made to show.

    speaker_split_show cuts what the separation reported to 200
    characters and hands the cell that, so short captions are not the
    whole of what has to fit in there. Cut to the same 200 here, so
    the longest case really is the one being measured.
    """
    return (vpm.T('The speaker separation reports: %s') % (
        "ImportError: Can't determine version for bottleneck, raised "
        "while the pipeline that tells voices apart was being built "
        "out of the models lying beside the program"))[:200]


print("\n1. The column is measured for what it will hold")
vpm.set_language("en")
holder, tree, cells, nodes = sheet(NARROWEST)
room = tree.columnWidth(4)
mark_font = cells[0][2].fontMetrics()
button_wide = cells[0][1].sizeHint().width()
running = vpm.T('Separating ...')
counted = vpm.TN(2, 'Separated: %s speaker', 'Separated: %s speakers') % 2
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
        "button": [], "asked": []}
for language in ("en", "de"):
    vpm.set_language(language)
    holder, tree, cells, nodes = sheet(NARROWEST)
    _path, button, mark, _item = cells[0]
    written(cells, missing_caption())
    over["missing"].append((language, unreadable(mark), mark.width(),
                            mark.height()))
    written(cells, busy=True)
    over["running"].append((language,
                            needs(mark) - mark.fontMetrics().height(),
                            mark.width(), needs(mark)))
    over["button"].append((language,
                           button.sizeHint().width() - button.width(),
                           button.width(), button.sizeHint().width()))
    written(cells, found=2)
    over["counted"].append((language,
                            needs(mark) - mark.fontMetrics().height(),
                            mark.width(), needs(mark)))
    written(cells, reported_caption())
    over["reported"].append((language, unreadable(mark), mark.width(),
                             mark.height()))
    over["asked"].append((language, needs(mark) - mark.minimumHeight(),
                          mark.minimumHeight(), needs(mark)))
    holder.deleteLater()
check("the sentence pointing at the log is readable in full",
      all(x[1] <= 0 for x in over["missing"]),
      "short by %s"
      % ["%s: %d px over in a label %dx%d" % x for x in over["missing"]])
check("the running caption stands on one line beside its button",
      all(x[1] <= 0 for x in over["running"]),
      "over one line by %s"
      % ["%s: %d px, %d px wide, %d px of text" % x
         for x in over["running"]])
check("a finished count of speakers stands on one line",
      all(x[1] <= 0 for x in over["counted"]),
      "over one line by %s"
      % ["%s: %d px, %d px wide, %d px of text" % x
         for x in over["counted"]])
check("a long reason from the separation is readable in full",
      all(x[1] <= 0 for x in over["reported"]),
      "short by %s"
      % ["%s: %d px over in a label %dx%d" % x for x in over["reported"]])
check("the height a cell asks for is measured, not left to a guess",
      all(x[1] <= 0 for x in over["asked"]),
      "short by %s"
      % ["%s: %d px, asked for %d of %d needed" % x
         for x in over["asked"]])
check("the button keeps its whole caption while a separation runs",
      all(x[1] <= 0 for x in over["button"]),
      "short by %s"
      % ["%s: %d px missing, %d px of %d" % x for x in over["button"]])

print("\n4. And in a font drawn as wide as the widest we build for")
was_font = in_a_wider_font(WIDER)
far = {"reported": [], "missing": [], "running": []}
try:
    for language in ("en", "de"):
        vpm.set_language(language)
        holder, tree, cells, nodes = sheet(NARROWEST)
        _path, button, mark, _item = cells[0]
        written(cells, reported_caption())
        far["reported"].append((language, unreadable(mark), mark.width(),
                                mark.height()))
        written(cells, missing_caption())
        far["missing"].append((language, unreadable(mark), mark.width(),
                               mark.height()))
        written(cells, busy=True)
        far["running"].append((language,
                               needs(mark) - mark.fontMetrics().height(),
                               mark.width(), needs(mark)))
        holder.deleteLater()
finally:
    QtWidgets.QApplication.setFont(was_font)
check("a long reason is readable in the widest font we build for",
      all(x[1] <= 0 for x in far["reported"]),
      "in a font %d%% as wide, short by %s" % (WIDER,
      ["%s: %d px over in a label %dx%d" % x for x in far["reported"]]))
check("so is the sentence pointing at the log, in that font",
      all(x[1] <= 0 for x in far["missing"]),
      "short by %s"
      % ["%s: %d px over in a label %dx%d" % x for x in far["missing"]])
check("and the running caption still on one line, in that font",
      all(x[1] <= 0 for x in far["running"]),
      "over one line by %s"
      % ["%s: %d px, %d px wide, %d px of text" % x
         for x in far["running"]])

print("\n5. Nothing is squeezed away or put out of reach")
# Both languages, because which of them asks the column for more room
# is not fixed: it is measured from two captions that must not wrap,
# and shortening one German caption made English the wider of the two.
#
# What is asked here changed once the name column stopped stretching.
# It used to be that nothing had to be scrolled sideways -- and that
# was only ever true because the name field gave way, down to 79 px on
# the Windows builder, in the one column somebody types into. Room for
# the name comes first now, and the tree scrolls instead; so what is
# asked is that the scrolling really reaches the far column, which is
# where the button to break a separation off sits.
narrow = []
was_font = QtWidgets.QApplication.font()
try:
    # Swept rather than measured at one width, because the squeeze does
    # not live at either end. Wide open there is room to spare, and in
    # the widest font we build for the tree scrolls so far that every
    # column keeps its own size. It is the middle that hurts -- the
    # window a little too narrow for what is in it -- and that is where
    # the Windows builder sits.
    for how_wide in (100, 120, 136, 160, WIDER):
        in_a_wider_font(how_wide)
        for language in ("de", "en"):
            vpm.set_language(language)
            holder, tree, cells, nodes = sheet(NARROWEST)
            written(cells, missing_caption())
            # Scrolled the whole way over, because what is asked is
            # not that the far column is narrow enough in principle
            # but that it really stands inside the viewport there.
            bar = tree.horizontalScrollBar()
            bar.setValue(bar.maximum())
            app.processEvents()
            head = tree.header()
            narrow.append(("%s at %d%%" % (language, how_wide),
                           head.sectionViewportPosition(4),
                           tree.columnWidth(4),
                           tree.viewport().width(),
                           tree.columnWidth(1)))
            holder.deleteLater()
finally:
    QtWidgets.QApplication.setFont(was_font)
check("the column carrying the button can be brought fully into view",
      all(0 <= left and left + wide <= room
          for _l, left, wide, room, _n in narrow),
      "scrolled the whole way over, at the narrowest window of %d px; %s"
      % (NARROWEST, ", ".join(
          "%s: the Speakers column %d px wide sits at %d in a viewport "
          "%d px wide" % (x[0], x[2], x[1], x[3]) for x in narrow)))
check("the field a name is typed into keeps its least width",
      all(name >= vpm.NAME_COLUMN_LEAST
          for _l, _w, _r, _b, name in narrow),
      "at least %d px wanted; %s"
      % (vpm.NAME_COLUMN_LEAST,
         ", ".join("%s: %d px" % (x[0], x[4]) for x in narrow)))

print("\n6. A recording that is open stays open while its cell is written")
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
