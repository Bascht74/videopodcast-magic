# -*- coding: utf-8 -*-
"""The second tab of the window: the assignment, and the time window.

A piece of the program, read in by beside() from the window and from
nowhere else, so Qt may stand at its head: the command line never
reads it. The program is handed in and bound below by name. The
assignment table is a piece of its own, assignmenttable/, read here.
"""

from PySide6 import QtWidgets

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# Bound above the seam: all of them are read before the window is.
COLOURS = PROGRAM.COLOURS
T = PROGRAM.T
as_relative_time = PROGRAM.as_relative_time
beside = PROGRAM.beside
box_room = PROGRAM.box_room
hint = PROGRAM.hint
label = PROGRAM.label
not_on_the_axis = PROGRAM.not_on_the_axis
os = PROGRAM.os
stack_when_narrow = PROGRAM.stack_when_narrow
timecode_string = PROGRAM.timecode_string

# The recordings, voices and cameras: read by this sheet and no other.
assignmenttable = beside("assignmenttable", program=PROGRAM)
AssignmentTable = assignmenttable.AssignmentTable

# scroll_sheet_build, window_ready and audio_under_camera are the
# window's and stand below the line this file is read at, so each is
# asked as PROGRAM.<name> at the call.


class AssignmentSheet(QtWidgets.QScrollArea):
    """Tab two: the assignment on the left, the preview player on the right.

    Or the player under it, where the room ends (stack_when_narrow). It
    lays out the boxes, and window_build puts the player the window made
    into them, with the In point and Out point under it and the tables
    beside it. The tick and the auphonic.com box are the window's still.
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

    def window_build(self, model, state, player, prepared_tracks,
                     player_load, player_candidates, covers):
        """The player on the right, the time window under it, the tables.

        The player's class comes out of make_player_widgets, so the
        window makes it; the four that choose what it plays stand further
        down there and come in as callables. What comes back is what the
        rest of the window reaches for, in the order it is unpacked.
        """
        self.model, self.state, self.player = model, state, player
        self.prepared_tracks, self.player_load = prepared_tracks, player_load
        self.player_candidates, self.covers = player_candidates, covers
        player.find_track = self.audio_for_camera
        player.heading = self.view_title
        player.title.hide()
        # The Resolve tab writes the marks as this player's line does.
        state["mark_shown"] = getattr(player, "mark_shown", None)
        state["mark_on_clock"] = getattr(player, "mark_on_clock", None)
        self.view_position.addWidget(player)
        self.axis_label = label("", COLOURS["quiet"])
        self.axis_label.setWordWrap(True)
        hint(self.axis_label, T('Without timecode the position of the '
                                'files is measured.'))
        model.in_point.listen(self.window_remember)
        model.out_point.listen(self.window_remember)
        self._window_buttons_build(player.cut_bar)
        self._split_line_build()
        self.table = AssignmentTable(self, model, state, player)
        return (self.axis_label, self.window_switch, self.split_line,
                self.split_label, self.split_never, self.limit_set,
                self.to_limit, self.window_enable, self.window_position_show)

    def _window_buttons_build(self, set_line):
        """The four buttons of the time window, and the lines under them.

        The In point and Out point are taken from the picture, not typed:
        the buttons sit in the player, right under the times they mean.
        """
        start_var, end_var = self.model.in_point, self.model.out_point
        in_button = QtWidgets.QPushButton(T('Mark In'))
        in_button.clicked.connect(lambda: self.limit_set(start_var))
        set_line.addWidget(hint(
            in_button, T('Takes the position from the picture.')))
        to_in = QtWidgets.QPushButton(T('to In point'))
        to_in.clicked.connect(lambda: self.to_limit(start_var))
        set_line.addWidget(hint(to_in, T('Jumps to the start of the window.')))
        set_line.addStretch(1)
        to_out = QtWidgets.QPushButton(T('to Out point'))
        to_out.clicked.connect(lambda: self.to_limit(end_var))
        set_line.addWidget(hint(to_out, T('Jumps to the end of the window.')))
        out_button = QtWidgets.QPushButton(T('Mark Out'))
        out_button.clicked.connect(lambda: self.limit_set(end_var))
        set_line.addWidget(hint(
            out_button, T('Takes the position from the picture.')))
        self.window_switch = [in_button, to_in, to_out, out_button]
        self.window_label = label("", COLOURS["warning"])
        self.window_label.setWordWrap(True)
        self.view_position.addWidget(self.window_label)
        self.window_hint = label("", COLOURS["quiet"])
        self.window_hint.setWordWrap(True)
        self.view_position.addWidget(self.window_hint)
        self.view_position.addWidget(self.axis_label)

    def _split_line_build(self):
        """The one project-wide question of the separation, under the table.

        Separating itself is an action on one named recording, in its row.
        """
        self.split_line = QtWidgets.QWidget()
        row = QtWidgets.QHBoxLayout(self.split_line)
        row.setContentsMargins(0, 0, 0, 0)
        self.split_label = label("", COLOURS["quiet"])
        self.split_label.setWordWrap(True)
        row.addWidget(self.split_label, 1)
        self.split_never = QtWidgets.QPushButton(T('Not on this machine'))
        hint(self.split_never, T(
            'Leaves the separation switched off for this project. The cut '
            'then comes from the tracks or from auphonic.com, as before.'))
        row.addWidget(self.split_never)
        self.assign_position.insertWidget(1, self.split_line)
        self.split_line.setVisible(False)

    def limit_set(self, target):
        """Adopt the position currently on screen as a boundary.

        Kept counted from where every camera runs, as the run counts it
        (a timecode is read at the reference camera's rate); the line
        shows it as a timecode. Before that moment it stays a timecode.
        """
        player = self.player
        # Measured, else by its timecode, as the player's place_s.
        here = player.axis_s()
        here = getattr(player, "tc0", None) if here is None else here
        if here is None:
            target.set(as_relative_time(player.spot_s()))
            return
        at, zero = here + player.spot_s(), player.marks_zero()
        if at < zero - 0.0005 and getattr(player, "marks_on_clock", bool)():
            target.set(timecode_string(at, player.fps))
            return
        target.set(as_relative_time(at - zero))

    def window_remember(self):
        """Put the boundaries where the player will find them."""
        self.state["in_point"] = self.model.in_point.get()
        self.state["out_point"] = self.model.out_point.get()
        self.player.window_draw()
        # A mark moved since the run greys "Create Resolve project".
        (self.state.get("resolve_button_check") or (lambda: None))()

    def to_limit(self, var):
        """Go to *var*'s point, loading the file that holds it, or say why."""
        player, window_label = self.player, self.window_label
        text = var.get()
        how = T('In point') if var is self.model.in_point else T('Out point')
        # The run's refusal, not a jump to somewhere near the end.
        refused = PROGRAM.in_point_refused(text) \
            if var is self.model.in_point else ""
        if refused:
            window_label.setText(refused)
            window_label.setVisible(True)
            return
        if player.jump_to(text):
            window_label.setVisible(False)
            return
        matching = next((b for b in self.player_candidates()
                        if self.covers(b, text) is True), None)
        if matching and matching != player.file_path:
            self.player_load(matching)
            if player.jump_to(text):
                window_label.setText(
                    T('%s is in %s -- the file is now in the player.')
                    % (how, os.path.basename(matching)))
                window_label.setVisible(True)
                return
        window_label.setText(
            T('%s is in none of the video files. Is there a timecode that '
              'fits the material?') % how)
        window_label.setVisible(True)

    def window_position_show(self):
        """Say what the In point and the Out point refer to."""
        if not self.state["without_tc"] or not self.state["axis"]:
            self.window_label.hide()
            return
        self.window_label.setText(
            T('No audio file carries a timecode. In point and Out point count '
              'from the moment every camera runs -- the position of the files '
              'to each other is measured.'))
        self.window_label.show()

    def window_enable(self):
        """Offer the time window's buttons only where they mean something."""
        away = not_on_the_axis(getattr(self.player, "file_path", None),
            self.model.clip_kinds, self.model.remembered,
            self.state.get("camera_labels"))
        on = PROGRAM.window_ready(self.state) and not away
        for widget in self.window_switch:
            widget.setEnabled(on)
        self.window_hint.setText(away or ("" if on else T(
            'In point and Out point are available once the time axis is '
            'set -- from the timecode or measured.')))
        self.window_hint.setVisible(not on)

    def audio_for_camera(self, camera_path):
        """The recording that belongs under this camera in the preview."""
        m = self.model
        return PROGRAM.audio_under_camera(
            camera_path, m.clip_kinds, self.prepared_tracks(),
            m.assign_lines, m.voice_lines, m.blocks_of)
