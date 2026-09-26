# -*- coding: utf-8 -*-
"""The second tab of the window: the assignment, and the time window.

A piece of the program, read in by beside() from the window and from
nowhere else, so Qt may stand at its head: the command line never
reads it. The program is handed in and bound below by name.
"""

from PySide6 import QtWidgets

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# Bound above the seam: all of them are read before the window is.
COLOURS = PROGRAM.COLOURS
T = PROGRAM.T
box_room = PROGRAM.box_room
hint = PROGRAM.hint
label = PROGRAM.label
stack_when_narrow = PROGRAM.stack_when_narrow

# scroll_sheet_build is the window's and stands below the line this file
# is read at, so it is asked as PROGRAM.scroll_sheet_build at the call.


class AssignmentSheet(QtWidgets.QScrollArea):
    """Tab two: the assignment on the left, the preview player on the right.

    Or the player under it, where the room ends (stack_when_narrow). It
    lays out the boxes; what fills them -- the tables, the tick, the
    player -- is still put in by the window.
    """

    def __init__(self):
        """The scrolling sheet, its two columns and the boxes in them."""
        QtWidgets.QScrollArea.__init__(self)
        _outside, room = PROGRAM.scroll_sheet_build(QtWidgets, self)
        two_columns = stack_when_narrow(self, QtWidgets.QHBoxLayout())
        room.addLayout(two_columns, 1)
        assign = QtWidgets.QGroupBox(T('Assignment: which audio track belongs '
                                       'to which camera'))
        two_columns.addWidget(assign, 1)
        self.assign_position = QtWidgets.QVBoxLayout(assign)
        self._assign_boxes_build()
        right_column = QtWidgets.QVBoxLayout()
        two_columns.addLayout(right_column)
        self.view_box = QtWidgets.QGroupBox(T('Preview player'))
        box_room(self.view_box, 580)
        right_column.addWidget(self.view_box)
        # Top aligned: the box is as tall as it needs to be and the rest
        # stays empty. Otherwise Qt pulls the rows inside it apart.
        right_column.addStretch(1)
        self.view_position = QtWidgets.QVBoxLayout(self.view_box)

    def _assign_boxes_build(self):
        """Under the tables: the Multitrack row, auphonic.com, the prework."""
        # The Multitrack tick lives here, under the tables: whether a
        # camera gives a track of its own is decided in this very table.
        self.multitrack_bar = QtWidgets.QWidget()
        self.multitrack_row = QtWidgets.QHBoxLayout(self.multitrack_bar)
        self.multitrack_row.setContentsMargins(0, 6, 0, 0)
        self.assign_position.addWidget(self.multitrack_bar)
        # And right under it what auphonic.com is to make of those tracks:
        # "what should this run do" in one place, filled by the window.
        run_box = QtWidgets.QGroupBox(
            T('Processing at auphonic.com (optional)'))
        self.run_layout = QtWidgets.QVBoxLayout(run_box)
        self.assign_position.addWidget(run_box)
        # One bar for all the prework, under the tables.
        self.prework_box = QtWidgets.QWidget()
        rows = QtWidgets.QVBoxLayout(self.prework_box)
        rows.setContentsMargins(0, 6, 0, 0)
        rows.setSpacing(2)
        self.prework_progress_bar = QtWidgets.QProgressBar()
        self.prework_progress_bar.setRange(0, 100)
        self.prework_progress_bar.setTextVisible(False)
        self.prework_progress_bar.setFixedHeight(8)
        rows.addWidget(self.prework_progress_bar)
        self.prework_label = label("", COLOURS["value"])
        rows.addWidget(self.prework_label)
        hint(self.prework_box, T('Envelopes and camera audio are prepared in '
                                 'the background.'))
        self.assign_position.addWidget(self.prework_box)
        self.prework_box.hide()

    def view_title(self, text=""):
        """Put the file name in the player's heading; that saves a line."""
        self.view_box.setTitle(T('Preview player%s')
                               % ("  --  " + text.replace("&", "&&")
                                  if text else ""))
