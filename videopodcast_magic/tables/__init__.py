# -*- coding: utf-8 -*-
"""The tables and the trees, and the rows and cells they are made of.

A piece of the program, read out of the folder beside the way in by
beside(). It cannot import the file it was cut out of, because that
file is still being read while this one is; the program is handed in
instead, and every name this piece uses out of it is bound below, by
name. What the window still calls out of it, it binds there in turn.
"""

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

# What the program has and this piece uses, bound once so that the
# tables read as they did in the window. Not one of them is a name the
# program binds again while it runs -- such a name is read through
# PROGRAM. where it is used, and there is none of that sort in here.
IGNORE_AUDIO = PROGRAM.IGNORE_AUDIO
MIX_ONLY = PROGRAM.MIX_ONLY
T = PROGRAM.T
TN = PROGRAM.TN
number_text = PROGRAM.number_text
parse_timecode = PROGRAM.parse_timecode
path_key = PROGRAM.path_key
video_facts = PROGRAM.video_facts


def from_the_front(entry):
    """Show a name from its beginning, and the whole of it on hovering.

    The column is narrower than the names are: they begin with the
    production and end with the camera, so a field showing its end
    reads "...11855_C002.mov" and one showing its beginning reads
    "PresentersCam_0...". The second is the one that says which row
    this is. Measured against the demo material: the name comes to
    about twice the width the column gives it.

    A field keeps its caret where it was left, so this is done once on
    building and never again -- typing must not jump back to the front.
    """
    entry.setCursorPosition(0)
    entry.setToolTip(entry.text())
    entry.textChanged.connect(entry.setToolTip)


def widget_width(w):
    """How wide a widget in a cell has to be to show what it holds.

    resizeColumnsToContents measures the text of items, and a cell with
    a widget in it has no item text. A column of input fields or drop
    downs was therefore measured as empty and came out at its minimum:
    the name column stood at 114 pixels with
    "Guest_Take0021A_Timecode.wav" in it, and the drop down beside it
    showed the last half of its word.

    The widget's own sizeHint does not help for a line edit -- it is the
    same whatever the text says -- so the text itself is measured. For a
    drop down every entry is measured, not only the one showing: the
    column must not jump about when somebody picks another one.
    """
    import PySide6.QtWidgets as _qw
    want = w.sizeHint().width()
    letters = w.fontMetrics()
    if isinstance(w, _qw.QLineEdit):
        # Room for the frame and the caret beside the text.
        want = max(want, letters.horizontalAdvance(w.text()) + 26)
    elif isinstance(w, _qw.QComboBox):
        widest = max([letters.horizontalAdvance(w.itemText(i))
                      for i in range(w.count())] or [0])
        # And for the arrow, which sits inside the box.
        want = max(want, widest + 44)
    return want


def fix_table_width(t, weights=None, most_rows=0):
    """Stretch the table over the full width, as tall as its content.

    Every column first gets what its content needs. What is left over is
    distributed, the name column taking the largest share and the number
    columns growing with it. Putting all of it into the first column would
    look lopsided, with the numbers stuck to the right edge.

    *most_rows* is a lid: beyond that many rows the table scrolls
    itself rather than growing on. Without one a table as tall as its
    content is a table that pushes the whole sheet taller, one row at a
    time, and the sheet answers with a scroll bar of its own -- so the
    reader scrolls the sheet to reach a table that would have fitted.
    Zero means no lid, which is what a table that cannot grow wants.
    """
    import PySide6.QtCore as _qc
    import PySide6.QtWidgets as _qw
    t.resizeColumnsToContents()
    # Whether the lid bites is settled before the columns are shared
    # out: a vertical scroll bar takes room from the viewport, and
    # columns measured against a viewport that then loses a scroll bar
    # come out too wide by exactly that bar.
    capped = bool(most_rows) and t.rowCount() > most_rows
    t.setVerticalScrollBarPolicy(_qc.Qt.ScrollBarAsNeeded if capped
                                 else _qc.Qt.ScrollBarAlwaysOff)
    head = t.horizontalHeader()
    head.setStretchLastSection(False)
    n = t.columnCount()
    for i in range(n):
        head.setSectionResizeMode(i, _qw.QHeaderView.Interactive)
        # The column header sits where its content sits.
        title = t.horizontalHeaderItem(i)
        if title is not None:
            title.setTextAlignment(
                (_qc.Qt.AlignLeft if i == 0 else _qc.Qt.AlignRight)
                | _qc.Qt.AlignVCenter)
    content = []
    for i in range(n):
        want = t.columnWidth(i)
        for r in range(t.rowCount()):
            cell = t.cellWidget(r, i)
            if cell is not None:
                want = max(want, widget_width(cell))
        content.append(want + 14)
    shares = list(weights) if weights else [3] + [1] * (n - 1)

    def distribute_width():
        free = t.viewport().width() - sum(content)
        total_sum = float(sum(shares)) or 1.0
        rest = free
        for i in range(n):
            assigned = int(free * shares[i] / total_sum) if free > 0 else 0
            if i == n - 1:
                assigned = rest
            rest -= assigned
            t.setColumnWidth(i, content[i] + max(0, assigned))

    t._distribute = distribute_width

    class GrowWithWindow(_qc.QObject):
        """Redistribute the table when the window grows wider."""

        def eventFilter(self, watched, what):
            if what.type() == _qc.QEvent.Resize:
                t._distribute()
            return False

    if not hasattr(t, "_grow"):
        t._grow = GrowWithWindow(t)
        t.viewport().installEventFilter(t._grow)
    distribute_width()
    t.setMinimumWidth(0)
    shown = most_rows if capped else t.rowCount()
    height = head.height() + 4
    for i in range(shown):
        height += t.rowHeight(i)
    t.setFixedHeight(height)


def table_build(columns):
    """A table where the row is the file.

    Clicking the row brings it into view, so the whole row is selected
    rather than the single cell.
    """
    import PySide6.QtWidgets as _qw
    t = _qw.QTableWidget(0, len(columns))
    t.setHorizontalHeaderLabels(columns)
    t.verticalHeader().setVisible(False)
    t.setSelectionBehavior(_qw.QAbstractItemView.SelectRows)
    t.setSelectionMode(_qw.QAbstractItemView.SingleSelection)
    t.setEditTriggers(_qw.QAbstractItemView.NoEditTriggers)
    t.setShowGrid(False)
    t.setAlternatingRowColors(True)
    t.setSizePolicy(_qw.QSizePolicy.Expanding, _qw.QSizePolicy.Fixed)
    return t


def table_rows_fit(t, most=120):
    """Give a table rows as tall as their content, and no taller.

    The columns are measured before the rows, and that order is the
    whole point. A table wraps the text in a cell, so while the
    columns still stand at the width Qt hands out, a caption that does
    not fit is laid over two or three lines and the row is measured at
    that height. Widening the columns afterwards does not measure the
    row again -- it keeps the height it was given. Measured on
    24.8.2026 in the voices table: 45 px a row where the content needs
    28, three lines for a caption that fits on one.

    The rest shares the room between the tables: what fits in half of
    it needs no scroll bar, what does not scrolls itself.
    """
    import PySide6.QtCore as _qc
    import PySide6.QtWidgets as _qw
    t.resizeColumnsToContents()
    t.resizeRowsToContents()
    height = t.horizontalHeader().height() + 2 * t.frameWidth() + 2
    for i in range(t.rowCount()):
        height += t.rowHeight(i)
    t.setMinimumHeight(min(height, most))
    t.setVerticalScrollBarPolicy(_qc.Qt.ScrollBarAsNeeded)
    t.setSizePolicy(_qw.QSizePolicy.Expanding, _qw.QSizePolicy.Expanding)


def file_span(file_path, axis):
    """Return what this video file knows about its position in time.

    Three numbers travel together and are always wanted together: how
    long the file runs, what clock it was shot on, and where the
    measurement put it on the common axis.
    """
    try:
        info = video_facts(file_path)
    except Exception:
        return None
    fps = float(info.get("fps") or 30.0)
    tc = info.get("tc")
    try:
        tc0 = parse_timecode(tc, fps) if tc else None
    except Exception:
        tc0 = None
    return {"duration": float(info.get("duration") or 0.0), "fps": fps,
            "tc0": tc0,
            "axis": (axis or {}).get(path_key(file_path))}


def tree_build(columns):
    """The assignment as a tree: a recording, its voices under it.

    The same shape the file list on the first sheet already has, and
    the same thing said: what hangs under a file belongs to that file.
    A recording whose voices were told apart carries one row per voice;
    one where nobody was told apart carries none, and then the tree is
    a flat list with no special case anywhere.

    A view over a model rather than the QTreeWidget the file list uses,
    and for one reason: four places in the suite find the file list by
    asking the window for its first QTreeWidget. A second one of that
    class would answer instead, and the file list would be the one
    nobody could find any more. What is on the screen is the same tree
    either way.

    Not uniform row heights: the rows hold input fields and choosers,
    and a uniform tree gives every row the first row's height.
    """
    import PySide6.QtGui as _qg
    import PySide6.QtWidgets as _qw
    t = _qw.QTreeView()
    model = _qg.QStandardItemModel(0, len(columns))
    model.setHorizontalHeaderLabels(columns)
    # The view owns the model, so the rows go when the tree does and
    # anything still holding one is told rather than reading a corpse.
    model.setParent(t)
    t.setModel(model)
    t.setUniformRowHeights(False)
    t.setRootIsDecorated(True)
    t.setSelectionBehavior(_qw.QAbstractItemView.SelectRows)
    t.setSelectionMode(_qw.QAbstractItemView.SingleSelection)
    t.setEditTriggers(_qw.QAbstractItemView.NoEditTriggers)
    t.setAlternatingRowColors(True)
    t.setSizePolicy(_qw.QSizePolicy.Expanding, _qw.QSizePolicy.Expanding)
    return t


def tree_row(t, under, texts):
    """One row of the tree, at the top or under another; its cells back.

    A row is the list of its cells, one per column. The first of them
    is the row itself as far as the tree is concerned: children hang on
    it, and what the row knows is stored on it.

    As many cells as the tree has columns, whatever it was handed: a
    row with one cell too many would give the tree a column nobody
    asked for, and one too few would leave a hole.
    """
    import PySide6.QtGui as _qg
    wide = t.model().columnCount()
    texts = list(texts)[:wide] + [""] * max(0, wide - len(texts))
    cells = [_qg.QStandardItem(x) for x in texts]
    for cell in cells:
        cell.setEditable(False)
    if under is None:
        t.model().appendRow(cells)
    else:
        under[0].appendRow(cells)
    return cells


def tree_cell(row, column, text, colour=None):
    """Write one cell of a tree row, in a colour where it matters."""
    import PySide6.QtGui as _qg
    row[column].setText(text)
    if colour:
        row[column].setForeground(_qg.QBrush(_qg.QColor(colour)))
    return row


def tree_field(t, row, column, widget):
    """Put an input field or a chooser into one cell of a row."""
    t.setIndexWidget(row[column].index(), widget)
    return widget


def tree_row_of(t, where):
    """The row an index points at, as the list of its cells."""
    model = t.model()
    if where is None or not where.isValid():
        return None
    return [model.itemFromIndex(where.sibling(where.row(), c))
            for c in range(model.columnCount())]


def folded_summary(tree, row):
    """What a folded recording says in place of its voices.

    The cameras, because the cameras are what folding takes off the
    screen. It said how many voices there were until 2.10.1-beta, and
    that number stood twice in the same line: the Speakers column of
    that very row already reads "Separated: 4 speakers".

    A voice with no camera yet is counted on its own. It is the one
    thing still to be decided, and added in with the rest it would hide
    behind them.
    """
    seen, without = [], 0
    parent = row[0]
    for r in range(parent.rowCount()):
        kid = parent.child(r, 2)
        box = tree.indexWidget(kid.index()) if kid is not None else None
        pick = box.currentData() if box is not None else None
        if not pick or pick in (IGNORE_AUDIO, MIX_ONLY):
            without += 1
        elif pick not in seen:
            seen.append(pick)
    if not seen:
        return T('no camera yet')
    return (TN(len(seen), 'on %s camera', 'on %s cameras')
            % number_text(len(seen), 0)
            + ((T(', %s without') % number_text(without, 0))
               if without else ""))


def row_picker_for(tree):
    """A filter that makes the row a clicked field sits in the current one.

    Whoever is deciding which camera "Speaker 2" belongs to has to be
    able to hear Speaker 2 first, and a row that is picked already
    plays. So opening the camera list, or clicking into the name field,
    does exactly what clicking the row does -- and nothing more than
    that: there is no second way of playing anything here, and there
    should not be one.

    A filter and not a signal, because QComboBox has none for "the list
    is opening", and a subclass for it would be a class per tree.
    """
    from PySide6 import QtCore as _qc

    class Picker(_qc.QObject):
        def eventFilter(self, who, event):
            # The press and not the focus: the focus also arrives while
            # the sheet is being built, and the player would open a file
            # nobody asked for.
            if event.type() == _qc.QEvent.MouseButtonPress:
                where = tree.indexAt(who.mapTo(tree.viewport(),
                                               who.rect().center()))
                if where.isValid():
                    tree.setCurrentIndex(where)
                    # And straight back: making a row current moves the
                    # focus into the tree, and a name field that loses
                    # the focus on the click that entered it cannot be
                    # typed in at all.
                    who.setFocus(_qc.Qt.MouseFocusReason)
            return False

    return Picker(tree)


def row_picker_watch(picker, *widgets):
    """Watch these fields, and the line edit inside any of them.

    An editable combo box hands its clicks to the line edit it holds,
    and a filter on the box alone never sees them -- the camera chooser
    reacted and the name field beside it did not.
    """
    for widget in widgets:
        widget.installEventFilter(picker)
        inner = getattr(widget, "lineEdit", None)
        inner = inner() if callable(inner) else None
        if inner is not None:
            inner.installEventFilter(picker)


def tree_rows_fit(t, most=266):
    """Give the tree the height its open rows need, and no more.

    The counterpart of table_rows_fit, and the reason it cannot be
    that one: a tree has no rows to count, it has items, and how many
    of them are on the screen depends on what somebody expanded.
    viewportSizeHint answers exactly that -- Qt adds up the rows it
    would draw -- and it answers before the widget is ever shown,
    which is when this runs.

    The columns are left alone, unlike in a table: this runs again
    every time somebody opens or closes a row, and a column that
    re-measured itself on every click would make the tree jump about
    under the hand that is using it.
    """
    import PySide6.QtCore as _qc
    import PySide6.QtWidgets as _qw
    height = (t.viewportSizeHint().height() + t.header().height()
              + 2 * t.frameWidth() + 2)
    t.setMinimumHeight(min(height, most))
    t.setVerticalScrollBarPolicy(_qc.Qt.ScrollBarAsNeeded)
    t.setSizePolicy(_qw.QSizePolicy.Expanding, _qw.QSizePolicy.Expanding)
