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
ByFile = PROGRAM.ByFile
COLOURS = PROGRAM.COLOURS
T = PROGRAM.T
TN = PROGRAM.TN
channel_rows_build = PROGRAM.channel_rows_build
every_audio_block = PROGRAM.every_audio_block
field_bind = PROGRAM.field_bind
has_sound = PROGRAM.has_sound
hint = PROGRAM.hint
label = PROGRAM.label
loudness_field_build = PROGRAM.loudness_field_build
make_drop_area = PROGRAM.make_drop_area
number_text = PROGRAM.number_text
os = PROGRAM.os
path_label = PROGRAM.path_label
speaks_as = PROGRAM.speaks_as
wrap_row = PROGRAM.wrap_row

# The file list, its bar and the window's own cells stand below the line
# this file is read at, so each is asked as PROGRAM.<name> at the call.
Qt = QtCore.Qt


class FilesSheet(QtWidgets.QWidget):
    """Tab one: the drop area or the file list, and the production strip.

    Built empty with the window; list_build fills it at the point in the
    window's assembly where the list has always been made, so the order
    the widgets arrive in -- and with it the focus chain -- stays. The
    rows, the findings and the output folder are drawn here too, out of
    the ProjectModel; what the rest of the window does comes in as calls.
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
        self.channel_node = ByFile()     # file -> its row in the list

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
        # The list, its status line and its row maker, which the file
        # changes reach for here rather than being handed them.
        self.items, self.preflight_line, self.item = (
            parts[0], parts[1], parts[-1])
        self.marks, self.finding_word = parts[4], parts[5]
        return parts

    def rows_wire(self, model, state, bridge, late, again, use_value,
                  wides, kind_answered, prework_kick_off):
        """What the rows reach for in the window; the two signals they hear.

        *again* is the window's file -> draw its Kind cell again; the
        four callables stand in the window, most of them below this
        call, so they come in as late look-ups.
        """
        self.model, self.state, self.late, self.again = (
            model, state, late, again)
        self.use_value, self.wides = use_value, wides
        self.kind_answered = kind_answered
        self.prework_kick_off = prework_kick_off
        bridge.channels_done.connect(self.channels_arrived)
        self.items.currentItemChanged.connect(lambda *_: self.removable())

    def channel_rows_show(self, node, path):
        """The channel rows under one audio file, out of channel_rows_build."""
        m = self.model
        channel_rows_build(node, path, Qt, QtCore, QtWidgets,
                           m.blocks_of, m.channel_choice, self.channel_node,
                           self.channels_arrived, m.clip_kinds, self.items,
                           m.remembered, m.split_files)

    def channels_arrived(self, path):
        """The measurement for one file is in; redraw the rows it feeds.

        A recording of several blocks has one row and waits for every
        block. The row hangs on the first block, so a finished second
        block has to redraw the first one's node -- otherwise the last
        block to finish redraws nothing and the row waits for ever.
        """
        a = os.path.abspath(path)
        for api_key in dict.fromkeys([a, self.model.recording_of.get(a, a)]):
            entry = self.channel_node.get(api_key)
            if not entry:
                continue
            try:
                self.channel_rows_show(entry[0], entry[1])
            except RuntimeError:
                self.channel_node.pop(api_key, None)
        # The channels are known, so what has to be cut out is too. The
        # cameras belong in it, or a two-microphone camera is never cut.
        self.prework_kick_off(every_audio_block(
            self.model.files, self.model.blocks_of,
            self.state.get("own_cameras") or ()))

    def append_findings(self, node, its_findings):
        """List the hints for a file as lines below it.

        Otherwise the summary would count hints that can be read nowhere.
        """
        # Only the old finding lines: the same slot marks the channel rows
        # too, and clearing those would drop a setting.
        for i in range(node.childCount() - 1, -1, -1):
            if node.child(i).data(0, Qt.UserRole + 2) == "finding":
                node.removeChild(node.child(i))
        for b in its_findings:
            if b.kind == "good":
                continue
            line = self.item(node, "      " + self.finding_word[b.kind],
                             b.text)
            line.setData(0, Qt.UserRole + 2, "finding")
            line.setForeground(2, QtGui.QBrush(QtGui.QColor(
                self.marks[b.kind][1])))
            if b.advice:
                for column in (0, 1, 2):
                    line.setToolTip(column, b.advice)

    def show_overall(self, general):
        """Put what belongs to no single file into its own group."""
        items = self.items
        for i in range(items.topLevelItemCount() - 1, -1, -1):
            if items.topLevelItem(i).data(0, Qt.UserRole + 2):
                items.takeTopLevelItem(i)
        if not general:
            return
        group = self.item(items, T('GENERAL NOTES'),
                          TN(len(general), '%s point', '%s points')
                          % number_text(len(general), 0), "group", True)
        group.setData(0, Qt.UserRole + 2, True)
        group.setExpanded(True)
        for b in general:
            line = self.item(group, "      " + (b.field
                                                or self.finding_word[b.kind]),
                             b.text)
            line.setForeground(2, QtGui.QBrush(QtGui.QColor(
                self.marks[b.kind][1])))
            if b.advice:
                for column in (0, 1, 2):
                    line.setToolTip(column, b.advice)

    def video_choices_show(self, node, path, chosen, forced):
        """The two decisions a video file carries, in its own row.

        The Kind is shown twice in this window, and both show a derived
        wide shot -- which changes the moment a voice is given a camera.
        So the row leaves behind how to draw itself again; kinds_refresh
        calls it, or the list keeps calling every camera the wide shot.
        """
        short = os.path.basename(path)
        kinds = self.model.clip_kinds
        kind = kinds[path]
        self.again[path] = lambda: self.video_choices_show(
            node, path, chosen, forced)
        cell, box = PROGRAM.kind_cell_for(
            path, kind, *self.wides(), self.state.get("no_place"),
            kinds, COLOURS["quiet"],
            lambda p=path: self.kind_answered(p),
            self.state.get("camera_labels"))
        self.items.setItemWidget(node, 3, cell)
        used, why = PROGRAM.audio_use_settled(path, chosen, forced,
                                              has_sound(path), kind.get())
        sound, sound_box = PROGRAM.camera_audio_cell(short, used, why,
                                                     COLOURS["quiet"])
        PROGRAM.audio_use_bind(sound_box, self.use_value(path), why)
        self.items.setItemWidget(node, 4, sound)

    def removable(self):
        """Enable removal only when the selection actually offers something."""
        node = self.items.currentItem()
        while node is not None and node.data(0, Qt.UserRole) is None\
                and node.data(0, Qt.UserRole + 1) is None:
            node = node.parent()
        self.remove_button.setEnabled(node is not None)
        PROGRAM.menus_follow(self.late)  # so the entry's key dies with it

    def production_build(self, model, state, late, after_folder):
        """The Production box: the name, the output folder, the loudness.

        *after_folder* is what the window does once the folder moved.
        Returns the name's row and field, which the window hangs more
        on, and folder_show and folder_pick, which its menu and project
        file call.
        """
        self.model, self.state = model, state
        self.after_folder = after_folder
        # --- production: name and location belong together
        place_box = QtWidgets.QGroupBox(T('Production'))
        self.strip_rows.addWidget(place_box)
        place_position = QtWidgets.QVBoxLayout(place_box)
        # One row that breaks where the room ends: see wrap_row.
        name_bar = wrap_row(place_position)
        name_field = field_bind(QtWidgets.QLineEdit(), model.production, 340)
        # Duplicate names are marked red in their row; a missing production
        # name is the same fault and gets the same mark.
        late["name_field"] = name_field
        speaks_as(name_field, T('Production name'))
        name_bar.pair(label(T('Production name')), hint(
            name_field,
            T('Title at auphonic.com and start of the new file names.')))
        self.folder_row_build(place_position)
        # --- how loud the finished episode is. Why it stands here and what
        #     the entries mean is in loudness_field_build.
        loudness_field_build(place_position, model.lufs)
        return name_bar, name_field, self.folder_show, self.folder_pick

    def folder_row_build(self, place_position):
        """The output folder: the button, the path it shows, and reset."""
        folder_bar = QtWidgets.QHBoxLayout()
        place_position.addLayout(folder_bar)
        folder_button = QtWidgets.QPushButton(T('Output folder ...'))
        folder_button.clicked.connect(lambda: self.folder_pick())
        folder_bar.addWidget(hint(
            folder_button, T('If empty: next to each video file.')))
        speaks_as(folder_button, T('Choose the output folder'))
        self.folder_label = path_label(T('next to each video file'),
                                       COLOURS["quiet"])
        speaks_as(self.folder_label, T('Output folder'))
        folder_bar.addWidget(self.folder_label)
        self.reset = QtWidgets.QPushButton(T('reset'))
        self.reset.clicked.connect(lambda: self.folder_delete())
        speaks_as(self.reset, T('Output folder back beside each video file'))
        self.reset.hide()
        folder_bar.addWidget(hint(
            self.reset, T('Puts it back next to each video file.')))
        folder_bar.addStretch(1)

    def folder_show(self):
        """Say where the output goes, and offer reset once one is chosen."""
        d = self.model.out_folder.get()
        self.folder_label.say(d if d else T('next to each video file'))
        self.reset.setVisible(bool(d))

    def folder_pick(self):
        """Ask for an output folder; with one chosen, the handover follows."""
        d = QtWidgets.QFileDialog.getExistingDirectory(
            self.window(), T('Output folder'),
            self.model.out_folder.get() or self.model.commonest_folder()
            or "")
        if not d:
            return
        self.model.out_folder.set(d)
        self.folder_moved()

    def folder_delete(self):
        """The output folder back beside each video file."""
        self.model.out_folder.set("")
        self.folder_moved()

    def folder_moved(self):
        """What a new output folder changes: shown, handover, the window."""
        self.folder_show()
        self.state["resolve_json"] = None
        PROGRAM.handover_follows(
            self.state, [c[0] for c in self.model.camera_lines], True)
        self.after_folder()
