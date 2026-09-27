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
camera_offset = PROGRAM.camera_offset
cameras_in_track_order = PROGRAM.cameras_in_track_order
checkbox_bind = PROGRAM.checkbox_bind
cut_fields_build = PROGRAM.cut_fields_build
cut_title_of = PROGRAM.cut_title_of
file_timecode = PROGRAM.file_timecode
gui_log = PROGRAM.gui_log
hint = PROGRAM.hint
label = PROGRAM.label
make_band_and_player = PROGRAM.make_band_and_player
make_preview = PROGRAM.make_preview
make_resolve_check = PROGRAM.make_resolve_check
os = PROGRAM.os
parse_timecode = PROGRAM.parse_timecode
preview_out_of_date = PROGRAM.preview_out_of_date
question_note_build = PROGRAM.question_note_build
speakers_still_wanted = PROGRAM.speakers_still_wanted
speech_table_fill = PROGRAM.speech_table_fill
stack_when_narrow = PROGRAM.stack_when_narrow
video_facts = PROGRAM.video_facts
voice_suggest_round = PROGRAM.voice_suggest_round
wide_note_build = PROGRAM.wide_note_build
wide_settings_grey = PROGRAM.wide_settings_grey

# The window's own stand below the line this file is read at, so each is
# asked as PROGRAM.<name> at the call: scroll_sheet_build, sync_note_build,
# choice_boxes_even, unless_sync and MIX_TRACK_ALIASES.


def audio_for_cut(d, cameras, offset, done):
    """Return the audio to run under the camera cut: (file, offset).

    Preferably the finished overall mix from auphonic.com (*done*, name
    -> file): at delivery level, with its timecode, and what the cut
    timeline gets. Failing that the camera file carrying the mix as its
    first audio track -- quieter. A speaker camera would bring one voice.
    """
    mix = next((done[n] for n in PROGRAM.MIX_TRACK_ALIASES
                if n in done), None)
    origin = d.get("start_s")
    if mix and origin is not None:
        try:
            # With the measured frame rate, for the same reason as
            # in camera_place: the frames of a timecode are frames.
            tc = file_timecode(mix, max(1.0, float(
                d.get("fps_measured") or d.get("fps") or 30.0)))
        except Exception:
            tc = None
        if tc is not None:
            # The same computation as for the cameras: position in the file
            # = programme time minus offset.
            return mix, float(tc) - float(origin)
    first = (cameras_in_track_order(cameras) or [{}])[0]
    return first.get("file"), offset.get(first.get("track"), 0.0)


def player_load_cut(cut_player, cut_band, state, numbers, prepared_tracks,
                    preview_file):
    """Feed the player with the cut, or with a single file.

    *prepared_tracks* and *preview_file* are asked only when needed:
    the finished tracks for the sound under a cut, the file for none.
    """
    if not hasattr(cut_player, "set"):
        return
    d = state.get("cut_data")
    if numbers and numbers.get("cut") and d:
        cameras = [x for x in (d.get("cameras") or []) if x.get("file")]
        offset = camera_offset(cameras, d.get("start_s"),
            max(1.0, float(d.get("fps_measured") or d.get("fps") or 30.0)))
        files_per_track = {x["track"]: x["file"] for x in cameras}
        if files_per_track:
            end = max(b for _a, b, _w in numbers["cut"])
            audio_file, audio_offset = audio_for_cut(d, cameras, offset,
                                                     prepared_tracks())
            cut_player.set(
                numbers["cut"], files_per_track, offset,
                audio_file, audio_offset,
                0.0, end, d.get("start_s"),
                numbers.get("wide_shots"), numbers.get("colours"),
                d.get("speakers"))
            return
    file_path = preview_file()
    if not file_path:
        cut_player.set([], {}, {}, None, 0.0)
        return
    try:
        duration = float(video_facts(file_path).get("duration") or 0.0)
    except Exception:
        duration = 0.0
    name = os.path.basename(file_path)
    try:
        tc = video_facts(file_path).get("tc")
        tc0 = parse_timecode(tc, 30.0) if tc else None
    except Exception:
        tc0 = None
    cut_player.set([(0.0, duration or 1e6, name)], {name: file_path},
                   {name: 0.0}, file_path, 0.0, 0.0, duration or None,
                   tc0, [], {name: COLOURS["head"]})
    # Without a cut the band stays as a position display, in one colour.
    cut_band.set([(0.0, duration or 1.0, name)],
                 {name: COLOURS["head"]}, duration or 1.0)


class CutGroup(QtWidgets.QWidget):
    """One group of the camera cut's settings, which opens and shuts.

    A header button with the group's name; beside it, while the group is
    shut, its values on a line of their own, wrapped rather than cut, so
    a shut group still says what it holds. *toggled* is told (group, on)
    when the button is pressed; *summary* gives the line.
    """

    # The rhythm, the wide shot, and where the speech does not decide:
    # the question's seconds stand over "After a question", as before.
    PLAN = (("timing", ("min-edit-duration", "min-speech-to-switch",
                        "silence-hold", "edit-change-delay")),
            ("wide", ("wide-after", "wide-latest", "wide-length",
                      "wide-most")),
            ("special", ("reaction-lead", "on-question", "on-monologue",
                         "on-together", "on-silence", "on-uncertain")))

    def __init__(self, key, title, summary, toggled):
        """The header, the line beside it, and the rows' empty body."""
        QtWidgets.QWidget.__init__(self)
        self.key = self.name = key
        self.summary = summary
        column = QtWidgets.QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(2)
        head = QtWidgets.QHBoxLayout()
        column.addLayout(head)
        self.button = QtWidgets.QToolButton()
        self.button.setText(title)
        self.button.setAutoRaise(True)
        bold = self.button.font()
        bold.setBold(True)
        self.button.setFont(bold)
        self.button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.button.clicked.connect(
            lambda *_: toggled(self, not self.is_open()))
        head.addWidget(self.button, 0,
                       QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.said = label("", COLOURS["quiet"])
        self.said.setWordWrap(True)
        head.addWidget(self.said, 1)
        head.addStretch(0)
        self.body = QtWidgets.QWidget()
        self.rows = QtWidgets.QVBoxLayout(self.body)
        self.rows.setContentsMargins(18, 0, 0, 0)
        column.addWidget(self.body)

    def is_open(self):
        """Whether the rows of this group are shown."""
        return not self.body.isHidden()

    def open_show(self, on):
        """Show the rows or only the header, and the arrow that says which."""
        self.body.setVisible(on)
        self.button.setArrowType(QtCore.Qt.DownArrow if on
                                 else QtCore.Qt.RightArrow)
        self.said_again()

    def said_again(self):
        """The values beside the header, while shut; read out either way."""
        text = self.summary()
        self.said.setText("" if self.is_open() else text)
        self.said.setVisible(not self.is_open())
        self.button.setAccessibleDescription(text)


class CutGroups(object):
    """The camera cut's groups on one sheet, and which of them are open.

    *opened* holds the open groups' keys, the one opened longest ago
    first. What was open is asked of the settings file, not the project:
    it is how somebody likes the tab, not a fact about one production.
    """

    def __init__(self, sheet, into, loose, parts, values):
        """Each row out of the grid it was built in (*loose*) into a group.

        Nothing kept means all open until the first look settles it.
        """
        self.sheet, self.values, self.arranged = sheet, values, False
        self.parts = parts
        titles = {"timing": T('Timing'), "wide": T('Wide shot'),
                  "special": T('Special cases')}
        self.groups, self.group_of = [], {}
        for key, keys in CutGroup.PLAN:
            group = CutGroup(key, titles[key],
                             lambda k=keys: self.said(k), self.toggled)
            for api_key in keys:
                line = parts[api_key][0]
                for i in range(loose.count()):
                    loose.itemAt(i).layout().removeWidget(line)
                group.rows.addWidget(line)
                values[api_key].listen(group.said_again)
            into.addWidget(group)
            self.groups.append(group)
            self.group_of[key] = group
        kept = PROGRAM.settings().get("cut_groups_open")
        self.kept = kept if isinstance(kept, list) else None
        self.opened = [g.key for g in self.groups
                       if self.kept is None or g.key in kept]
        if self.kept is not None:
            self.opened.sort(key=kept.index)
        for group in self.groups:
            group.open_show(group.key in self.opened)

    def said(self, keys):
        """The values of one group on one line, for its header when shut."""
        said = []
        for api_key, caption, _d, unit, _s, _l in PROGRAM.CUT_FIELDS:
            if api_key in keys:
                said.append("%s %s\u00a0%s" % (
                    T(caption), self.values[api_key].get(), unit))
        # A choice as its drop-down names it, in the language shown.
        for api_key, caption, _d, _a, _s, _l in PROGRAM.CUT_CHOICES:
            if api_key in keys:
                said.append("%s: %s" % (T(caption),
                                        self.parts[api_key][1].currentText()))
        return "  ·  ".join(said)

    def toggled(self, group, on):
        """A header was pressed: open or shut that group, then make room.

        The group just opened is the newest, so it is never the one the
        room it needs is taken from.
        """
        if group.key in self.opened:
            self.opened.remove(group.key)
        if on:
            self.opened.append(group.key)
        group.open_show(on)
        if on:
            self.fit()
        self.keep()

    def first(self):
        """On a look at the tab: make room, and first time decide who leads.

        Without a kept choice a group holding a value off its default is
        put last, so it is the one left open when room runs short.
        """
        if self.kept is None and not self.arranged:
            self.arranged = True
            plain = dict((f[0], str(f[2])) for f in
                         PROGRAM.CUT_FIELDS + PROGRAM.CUT_CHOICES)
            plan = dict(CutGroup.PLAN)
            self.opened.sort(key=lambda key: any(
                str(self.values[k].get()) != plain[k] for k in plan[key]))
        self.fit()

    def fit(self):
        """Shut the group opened longest ago while the tab would scroll.

        Never the last open one, and none whose shutting would not lower
        the tab: where the preview beside it is what is too tall, taking
        the settings away gains nothing.
        """
        room = self.sheet.maximumViewportSize().height()
        while len(self.opened) > 1:
            before = self.room_needed()
            if before <= room:
                break
            oldest = self.group_of[self.opened.pop(0)]
            oldest.open_show(False)
            if self.room_needed() >= before:
                self.opened.insert(0, oldest.key)
                oldest.open_show(True)
                break

    def room_needed(self):
        """The height the tab asks for now, in the width it is shown in.

        Every layout from the groups up is told to measure again first:
        a hidden row only reaches the tab's size once they have.
        """
        inside = self.sheet.widget()
        here = self.groups[0]
        while here is not None and here is not self.sheet:
            if here.layout() is not None:
                here.layout().invalidate()
            here = here.parentWidget()
        for group in self.groups:
            group.layout().invalidate()
        inside.layout().activate()
        need = inside.minimumSizeHint().height()
        if inside.hasHeightForWidth():
            need = max(need, inside.heightForWidth(
                self.sheet.maximumViewportSize().width()))
        return need

    def keep(self):
        """Write down which groups are open, oldest first, where it moved.

        Only after a press: shutting for room alone writes nothing, so a
        window that is only looked at leaves the settings as they were.
        """
        if self.opened != self.kept:
            self.kept = list(self.opened)
            PROGRAM.keep_setting("cut_groups_open", list(self.opened))


class ResolveSheet(QtWidgets.QScrollArea):
    """Tab three: whether Resolve answers, the camera cut and its preview.

    Built empty with the window; cut_build fills it at the point in the
    window's assembly where it has always been filled, so the order the
    widgets arrive in -- and with it the focus chain -- stays. It reads
    the production off the ProjectModel it is handed.
    """

    def __init__(self):
        """The scrolling sheet; what goes into it follows later."""
        QtWidgets.QScrollArea.__init__(self)
        _outside, self.room = PROGRAM.scroll_sheet_build(QtWidgets, self)

    def cut_build(self, window, model, state, bridge, bridge_emit, parts):
        """Everything on this tab, and what the window reaches for of it.

        *parts* holds what the window made elsewhere and this tab uses:
        settings_open, wide_cameras_now, prepared_tracks, player,
        NoPlayer, split_line and the two multimedia modules. Returns the
        Resolve box and its check, and the preview's pieces.
        """
        self.window, self.model, self.state = window, model, state
        self.parts = parts
        # Whether Resolve answers, and the box that says so, stand in
        # make_resolve_check(). Below settings_open, which its line reaches.
        (self.resolve_box, left, right,
         self.resolve_check_run_kick_off) = make_resolve_check(
             QtWidgets, bridge, bridge_emit, self.room,
             parts["settings_open"])
        # The row holding its two columns is the left one's parent layout.
        stack_when_narrow(self, left.parent())
        window.tabs.currentChanged.connect(self.chosen)
        self.info_build()
        self.settings_build(left)
        self.forecast_build(left, right)
        self.preview_build(bridge, bridge_emit)
        return (self.resolve_box, self.resolve_check_run_kick_off,
                self.cut_var, self.edge_on, self.cut_player,
                self.preview_compute, self.preview_kick_off, self.watchdog,
                self.wide_state_show)

    def chosen(self, *_):
        """Resolve and the speakers, on the first look at this tab.

        Not twice -- a second speaker run costs minutes for nothing.
        """
        if self.window.tabs.currentWidget() is not self:
            return
        # After the tab is laid out, which is after this signal.
        QtCore.QTimer.singleShot(0, self.cut_groups.first)
        if not self.state.get("resolve_checked"):
            self.state["resolve_checked"] = True
            self.resolve_check_run_kick_off()
        if PROGRAM.sync_only(self.state):
            return          # no cut, so no speakers to measure
        if speakers_still_wanted(self.state, self.model.assign_lines,
                                 self.model.voice_lines):
            gui_log("cut tab opened with no speakers known -- measuring")
            self.speaker_measure()

    def info_build(self):
        """The line with In point, Out point and duration, kept up to date.

        The In point and Out point are in the player on the tab before;
        a box of their own would be the same information twice.
        """
        self.window_info = QtWidgets.QWidget()
        self.window_info.setVisible(False)
        info_row = QtWidgets.QHBoxLayout(self.window_info)
        self.window_info_label = label("", COLOURS["value"], True)
        info_row.addWidget(self.window_info_label)
        self.model.in_point.listen(self.window_info_show)
        self.model.out_point.listen(self.window_info_show)

    def window_info_show(self):
        """Write In point, Out point and duration into their line."""
        shown = self.state.get("mark_shown") or (lambda text: text)
        a = shown(self.model.in_point.get()).strip()
        b = shown(self.model.out_point.get()).strip()
        duration = self.model.window_length(self.state.get("mark_on_clock"))
        self.window_info_label.setText(
            T('In point: %s     Out point: %s     Duration: %s')
            % (a or T('Beginning'), b or T('End'),
               duration or T('the whole material')))

    def settings_build(self, left):
        """The left column: the notes, and the camera cut's settings grid.

        The grid -- the cut fields, the wide shot tick and its two notes
        -- is one unit in one box, so it can be regrouped in one place.
        """
        # Sync only: nothing on this tab is set, and one sentence says so.
        self.sync_note = PROGRAM.sync_note_build(left)
        # What stands in place of the camera cut: one line saying why.
        self.without_cut_label = label(
            T('There is no camera cut yet: it needs two people, each with a '
              'name and a camera.\nSeparate recordings give that with the '
              'Multitrack tick, and so does "several speakers" in the '
              'Speaker name field of one recording --\nthe voices found there '
              'get their camera in the table under the recordings.\nA Resolve '
              'project is created anyway -- all cameras at their measured '
              'places, ready for Multicam.'),
            COLOURS["quiet"])
        self.without_cut_label.setWordWrap(True)
        left.addWidget(self.without_cut_label)
        self.without_cut_label.setVisible(False)
        self.cut_box = QtWidgets.QGroupBox(T('Camera cut'))
        left.addWidget(self.cut_box)
        cut_position = QtWidgets.QVBoxLayout(self.cut_box)
        self.cut_parts = {}
        # Built into a layout of no window's, then handed to the groups.
        loose = QtWidgets.QVBoxLayout()
        self.cut_var = self.model.cut = cut_fields_build(loose,
                                                         self.cut_parts)
        PROGRAM.choice_boxes_even(
            [box for _line, box in self.cut_parts.values()])
        self.edge_on = self.model.edge_on
        self.edge_box = checkbox_bind(QtWidgets.QCheckBox(
            T('Wide shot for greeting at the start and farewell at the end')),
            self.edge_on)
        self.cut_groups = CutGroups(self, cut_position, loose,
                                    self.cut_parts, self.cut_var)
        self.groups = self.cut_groups.groups
        self.cut_groups.group_of["wide"].rows.addWidget(hint(
            self.edge_box,
            T('During greeting and farewell the picture stays wide.')))
        self.wide_note = wide_note_build(label, COLOURS["quiet"])
        self.question_note = question_note_build(label, COLOURS["quiet"])
        for note in (self.wide_note, self.question_note):
            cut_position.addWidget(note)
        # The same way over as refresh_names in the window, and for the
        # same reason: the tables ask for it before this tab is built.
        self.state["wide_state_show"] = self.wide_state_show

    def wide_state_show(self):
        """Grey the wide shot settings where there is no wide shot.

        Silent while the cut box is still being assembled: it is built
        after the tables that ask for this.
        """
        if self.state.get("cut_box_there"):
            PROGRAM.unless_sync(self.state, wide_settings_grey,
                                self.wide_note)(
                self.cut_parts, self.edge_box, self.wide_note,
                bool(self.parts["wide_cameras_now"]()[0]),
                COLOURS["quiet"], bool(self.state.get("words_there")))
            self.preview_kick_off()

    def forecast_build(self, left, right):
        """The right column: the preview box, the cut band and its player.

        With a handover file from earlier the cut is recomputed on every
        change, so the effect of a number is seen rather than guessed.
        The speaker box goes under the settings on the left.
        """
        model, state, parts = self.model, self.state, self.parts
        self.forecast_box = QtWidgets.QGroupBox(
            T('%s -- preview') % cut_title_of(
                model.voice_lines, model.multitrack.get(),
                model.assign_lines, len(model.camera_lines)))
        # The three that stand or fall together, where the assignment can
        # reach them: it is rebuilt before this tab exists.
        state["cut_boxes"] = (self.cut_box, self.forecast_box,
                              self.without_cut_label)
        # Weighted: whatever stays free below goes into this picture.
        right.addWidget(self.forecast_box, 1)
        forecast_outer = QtWidgets.QVBoxLayout(self.forecast_box)
        forecast_position = QtWidgets.QHBoxLayout()
        forecast_outer.addLayout(forecast_position)
        forecast_outer.setStretch(0, 0)
        self.cut_column = QtWidgets.QVBoxLayout()
        forecast_position.addLayout(self.cut_column)
        # The per-camera numbers are in the legend under the cut band; the
        # space here belongs to the picture.
        self.preview_label = label("", COLOURS["value"])
        self.preview_label.setTextFormat(QtCore.Qt.RichText)
        self.preview_label.setWordWrap(True)
        self.preview_label.setAlignment(QtCore.Qt.AlignTop)
        self.cut_column.addWidget(self.preview_label)
        self.cut_column.addStretch(1)
        # Beside it: who speaks how much, in a box of this sheet's own.
        self.speakers_build(left, state)
        # What the project type greys or hides: the same way over as
        # cut_boxes.
        state["sync_parts"] = (self.sync_note, self.speaker_box,
                               self.window.assignment_sheet.multitrack_bar,
                               parts["split_line"])
        (self.cut_band, self.cut_player, band_show,
         self.preview_file) = make_band_and_player(
            QtCore.Qt, QtCore, QtGui, QtWidgets, parts["QtMultimedia"],
            parts["QtMultimediaWidgets"], parts["NoPlayer"], state,
            model.files, model.assign_lines, model.clip_kinds,
            forecast_outer, parts["player"])
        # band_show reaches for this through state: it is built above the
        # line that made it, so it cannot be handed over as a parameter.
        state["player_load_cut"] = lambda numbers: player_load_cut(
            self.cut_player, self.cut_band, state, numbers,
            parts["prepared_tracks"], self.preview_file)
        band_show(None)
        left.addStretch(1)
        # No stretch on the right: the room below belongs to the preview
        # picture, not to empty space.
        right.addStretch(0)
        self.band_show = band_show

    def preview_build(self, bridge, bridge_emit):
        """The preview's computation, and the two timers that start it.

        One waits a moment after a change instead of computing on every
        keystroke; the other looks every three seconds whether a run has
        left a handover file behind, so the preview appears by itself.
        """
        model, state = self.model, self.state
        start_var, end_var = model.in_point, model.out_point
        preview_compute, self.speaker_measure = make_preview(
            QtCore.Qt, QtWidgets, state, bridge, bridge_emit,
            model.assign_lines, model.camera_lines, model.voice_lines,
            self.cut_var, self.cut_parts, self.edge_on, start_var, end_var,
            model.multitrack, model.out_folder, model.clip_kind_value,
            self.parts["wide_cameras_now"], model.commonest_folder,
            self.band_show, self.speech_show, self.window_info_show,
            self.question_note, self.cut_column, self.forecast_box,
            self.preview_label, self.speech_title, self.speech_table)
        # A project that only synchronises has no cut to preview.
        self.preview_compute = PROGRAM.unless_sync(state, preview_compute,
                                                   self.preview_label)
        state["preview_compute"] = self.preview_compute
        self.preview_timer = QtCore.QTimer(self.window)
        self.preview_timer.setSingleShot(True)
        self.preview_timer.setInterval(400)
        self.preview_timer.timeout.connect(lambda: voice_suggest_round(
            state, model.voice_lines, model.assign_lines, model.camera_lines,
            start_var.get(), end_var.get(), model.speech_language.get(),
            lambda r: bridge_emit(bridge.speakers_heard, r)))
        self.preview_timer.timeout.connect(self.preview_compute)
        state["preview_soon"] = self.preview_kick_off
        for v in self.cut_var.values():
            v.listen(self.preview_kick_off)
        self.edge_on.listen(self.preview_kick_off)
        start_var.listen(self.preview_kick_off)
        end_var.listen(self.preview_kick_off)
        # The window's own transcript reports on the prework bar, as a
        # line of its own beside the files.
        self.words_report = lambda text, share: bridge_emit(
            bridge.progress, T('Transcript'), text, share, "words")
        self.watchdog = QtCore.QTimer(self.window)
        self.watchdog.setInterval(3000)
        self.watchdog.timeout.connect(self.check_for_a_cut)
        self.watchdog.start()

    def preview_kick_off(self):
        """Compute the preview a moment from now, not on every keystroke."""
        self.preview_timer.start()

    def check_for_a_cut(self):
        """Compute the preview when a run has left a newer handover file.

        Or when the window's own transcript was begun or has arrived:
        this is also the look that starts it, once the time axis stands.
        """
        heard = PROGRAM.window_words_round(
            self.state, self.model.assign_lines, self.words_report)
        if preview_out_of_date(self.state) or heard:
            self.preview_compute()

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
