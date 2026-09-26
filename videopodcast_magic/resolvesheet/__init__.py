# -*- coding: utf-8 -*-
"""The third tab of the window: the camera cut, and the Resolve project.

A piece of the program, read in by beside() from the window and from
nowhere else, so Qt may stand at its head: the command line never
reads it. The program is handed in and bound below by name.
"""

from PySide6 import QtCore, QtGui, QtWidgets

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# Bound above the seam: all of them are read before the window is.
COLOURS = PROGRAM.COLOURS
T = PROGRAM.T
label = PROGRAM.label
speech_table_fill = PROGRAM.speech_table_fill

# scroll_sheet_build is the window's and stands below the line this file
# is read at, so it is asked as PROGRAM.scroll_sheet_build at the call.


class ResolveSheet(QtWidgets.QScrollArea):
    """Tab three: whether Resolve answers, the camera cut and its preview.

    Its two columns come out of make_resolve_check, which the window
    calls; this sheet holds the scrolling room they go into, and the
    speaker box it builds itself.
    """

    def __init__(self):
        """The scrolling sheet; what goes into it follows later."""
        QtWidgets.QScrollArea.__init__(self)
        _outside, self.room = PROGRAM.scroll_sheet_build(QtWidgets, self)

    def speakers_build(self, column, state):
        """The box with who speaks how much, at the foot of *column*.

        Without those numbers the cut beside it cannot be judged. The
        table is filled by speech_show.
        """
        self.state = state
        self.speaker_box = QtWidgets.QGroupBox(T('Speaker'))
        column.addWidget(self.speaker_box)
        speech_column = QtWidgets.QVBoxLayout(self.speaker_box)
        speech_column.setContentsMargins(10, 2, 10, 8)
        self.speech_title = label(T('Speakers, separated by voice'),
                                  COLOURS["heading"], True)
        speech_column.addWidget(self.speech_title)
        table = self.speech_table = QtWidgets.QTableWidget(0, 5)
        table.setHorizontalHeaderLabels([T('Speaker'), T('Speech time'),
                                         T('Share'), T('Blocks'),
                                         T('average')])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        speech_column.addWidget(table)
        table.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                            QtWidgets.QSizePolicy.Fixed)
        table.setMinimumWidth(240)
        table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

    def speech_show(self, d):
        """Write the speaker statistics into the table."""
        self.state["speech_time_total"] = speech_table_fill(
            QtCore.Qt, QtGui, QtWidgets, self.speech_table, d)
