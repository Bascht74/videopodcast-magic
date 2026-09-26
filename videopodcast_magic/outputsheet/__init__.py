# -*- coding: utf-8 -*-
"""The fourth tab of the window: the log of a run, and what it made.

A piece of the program, read in by beside() from the window and from
nowhere else, so Qt may stand at its head: the command line never
reads it. The program is handed in and bound below by name.
"""

import queue

from PySide6 import QtCore, QtGui, QtWidgets

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# Bound above the seam: all of them are read before the window is.
T = PROGRAM.T
make_log_view = PROGRAM.make_log_view
open_in_file_manager = PROGRAM.open_in_file_manager

# reason_set and resolve_button_say are the window's and stand below the
# line this file is read at, so they are asked through PROGRAM at the call.


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

    It holds its own widgets, empties the run's lines into the log, and
    says for itself whether either button may be pressed. What the
    Resolve button starts is the run start's; what follows the end of
    a run is said through run_ended, in gui().
    """

    # The timer has emptied the last lines of a run that is over.
    run_ended = QtCore.Signal()

    def __init__(self, state):
        """The log pane, the row of buttons under it, and the log's timer."""
        QtWidgets.QWidget.__init__(self)
        self.state = state
        # The queue the run's lines wait in; gui() hands in its own.
        self.post = None
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(80)
        self.timer.timeout.connect(self.log_follow)
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

    def resolve_button_check(self):
        """Whether "Create Resolve project" can be pressed, and why not."""
        PROGRAM.resolve_button_say(self.state, self.only_resolve_env_curve,
                                   self.only_resolve)

    def log_drain(self):
        """Every line waiting in the queue, into the log pane."""
        while True:
            try:
                text = self.post.get_nowait()
            except queue.Empty:
                return
            self.log.append_text(text)

    def log_follow(self):
        """What the timer does: the waiting lines, and the end of the run."""
        self.log_drain()
        if not self.state["running"]:
            # The run sets the flag after its last line, so what was
            # written between the two is still waiting here.
            self.log_drain()
            self.timer.stop()
            self.run_ended.emit()
