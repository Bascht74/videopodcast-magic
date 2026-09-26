# -*- coding: utf-8 -*-
"""The first tab of the window: the files, and the production strip.

A piece of the program, read in by beside() from the window and from
nowhere else, so Qt may stand at its head: the command line never
reads it. The program is handed in and bound below by name.
"""

from PySide6 import QtCore, QtGui, QtWidgets

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# Bound above the seam: all of them are read before the window is.
COLOURS = PROGRAM.COLOURS
make_drop_area = PROGRAM.make_drop_area

# The file list and its bar are the window's and stand below the line
# this file is read at, so each is asked as PROGRAM.<name> at the call.


class FilesSheet(QtWidgets.QWidget):
    """Tab one: the drop area or the file list, and the production strip.

    Built empty with the window; list_build fills it at the point in the
    window's assembly where the list has always been made, so the order
    the widgets arrive in -- and with it the focus chain -- stays.
    """

    def __init__(self):
        """The sheet with its margins, and the strip under the list."""
        QtWidgets.QWidget.__init__(self)
        self.position = QtWidgets.QVBoxLayout(self)
        self.position.setContentsMargins(10, 10, 10, 10)
        # Production name, output folder and auphonic.com sit as a narrow
        # strip: four values, and a sheet for them would be four fifths empty.
        self.strip = QtWidgets.QWidget()
        self.strip_rows = QtWidgets.QVBoxLayout(self.strip)
        self.strip_rows.setContentsMargins(0, 6, 0, 0)
        self.strip_rows.setSpacing(14)

    def list_build(self, state, take, add, open_project):
        """The drop area, the file list and the bar above it; the list's parts.

        While nothing is chosen the drop area is here and explains the
        workflow; afterwards the list, in the same place. The three
        callables are what a drop, a click on "add" and one on "open"
        do. Returns what make_file_list hands back.
        """
        drop_area_class = make_drop_area(QtCore, QtGui, QtWidgets)
        self.drop_area = drop_area_class(take, add, open_project, COLOURS)
        self.position.addWidget(self.drop_area, 1)
        parts = PROGRAM.make_file_list(QtCore.Qt, QtGui, QtWidgets,
                                       self.position, state)
        (self.bar, self.add_button,
         self.remove_button) = PROGRAM.file_bar_build(
             QtWidgets, self.position, self.strip)
        return parts
