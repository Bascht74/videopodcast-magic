# -*- coding: utf-8 -*-
"""The fourth tab of the window: the log of a run, and what it made.

A piece of the program, read in by beside() from the window and from
nowhere else, so Qt may stand at its head: the command line never
reads it. The program is handed in and bound below by name.
"""

from PySide6 import QtGui, QtWidgets

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# Bound above the seam: all of them are read before the window is.
T = PROGRAM.T
make_log_view = PROGRAM.make_log_view
open_in_file_manager = PROGRAM.open_in_file_manager

# reason_set is the window's and stands below the line this file is
# read at, so it is asked as PROGRAM.reason_set at the call.


def having_reason(button):
    """The button in a wrapper that can carry the reason it is greyed.

    A disabled button shows no tooltip, so the wrapper holds it instead.
    """
    env_curve = QtWidgets.QWidget()
    position = QtWidgets.QHBoxLayout(env_curve)
    position.setContentsMargins(0, 0, 0, 0)
    position.addWidget(button)
    return env_curve


class OutputSheet(QtWidgets.QWidget):
    """Tab four: the log pane, and under it the two buttons for the result.

    It holds its own widgets and says for itself whether there is a
    result to open. The Resolve button is only laid out here; what it
    does and when it may be pressed are still the window's.
    """

    def __init__(self, state):
        """The log pane and the row of buttons under it."""
        QtWidgets.QWidget.__init__(self)
        self.state = state
        position = QtWidgets.QVBoxLayout(self)
        position.setContentsMargins(10, 10, 10, 10)
        self.log = make_log_view(QtGui, QtWidgets, QtGui.QTextCursor)()
        position.addWidget(self.log, 1)
        foot = QtWidgets.QHBoxLayout()
        position.addLayout(foot)
        # The result button belongs with the output, not in the footer.
        self.open_button = QtWidgets.QPushButton(T('Open result folder'))
        self.open_button.clicked.connect(self.result_open)
        self.open_button.setEnabled(False)
        self.open_env_curve = having_reason(self.open_button)
        self.open_env_curve.setToolTip(T('There is no result yet.'))
        foot.addWidget(self.open_env_curve)
        # The Resolve button belongs here: first one looks at the result,
        # then one creates the project.
        self.only_resolve = QtWidgets.QPushButton(T('Create Resolve project'))
        self.only_resolve.setEnabled(False)
        self.only_resolve_env_curve = having_reason(self.only_resolve)
        self.only_resolve_env_curve.setToolTip(T(
            'That needs the handover file from a run, and there is none.'))
        foot.addWidget(self.only_resolve_env_curve)
        foot.addStretch(1)

    def result_target(self):
        """The last result of a run, else the folder it wrote into."""
        state = self.state
        return (state["results"][-1] if state["results"]
                else state.get("result_folder"))

    def result_open(self):
        """Show the result in the file manager, if there is one."""
        target = self.result_target()
        if target:
            open_in_file_manager(target)

    def result_button_check(self):
        """The button opens only once there really is a result."""
        running = self.state["running"]
        PROGRAM.reason_set(self.open_env_curve, self.open_button,
                           bool(self.result_target()) and not running,
                           T('The run is still going.') if running
                           else T('There is no result yet.'),
                           T('Show in Finder.'))
