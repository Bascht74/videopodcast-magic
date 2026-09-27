# -*- coding: utf-8 -*-
"""The assignment table: which recording, which speaker, which camera.

A piece of the program, read in by beside() from the second tab's
sheet and from nowhere else, so Qt may stand at its head: the command
line never reads it. The recordings above, the voices under them and
the cameras below, built again whenever what they show has changed.
"""

from PySide6 import QtCore, QtGui, QtWidgets

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# Bound above the seam: all of them are read before the window is.
AUDIO_SUFFIXES = PROGRAM.AUDIO_SUFFIXES
ByFile = PROGRAM.ByFile
CAMERA_TYPES = PROGRAM.CAMERA_TYPES
COLOURS = PROGRAM.COLOURS
IGNORE_AUDIO = PROGRAM.IGNORE_AUDIO
MIX_ONLY = PROGRAM.MIX_ONLY
SOUND_FINISHED = PROGRAM.SOUND_FINISHED
SPEAKER_SPLIT_OFF = PROGRAM.SPEAKER_SPLIT_OFF
SR = PROGRAM.SR
T = PROGRAM.T
TYPE_IGNORED = PROGRAM.TYPE_IGNORED
Value = PROGRAM.Value
assignment_marks_show = PROGRAM.assignment_marks_show
assignment_rows = PROGRAM.assignment_rows
camera_after_a_mark = PROGRAM.camera_after_a_mark
camera_gets_from = PROGRAM.camera_gets_from
camera_name_suggestion = PROGRAM.camera_name_suggestion
camera_names_offered = PROGRAM.camera_names_offered
camera_row_cameras = PROGRAM.camera_row_cameras
camera_to_remember = PROGRAM.camera_to_remember
field_bind = PROGRAM.field_bind
file_timecode = PROGRAM.file_timecode
fill_choices = PROGRAM.fill_choices
from_the_front = PROGRAM.from_the_front
guess_camera_name = PROGRAM.guess_camera_name
guess_production_name = PROGRAM.guess_production_name
guess_speaker_name = PROGRAM.guess_speaker_name
has_sound = PROGRAM.has_sound
label = PROGRAM.label
more_speakers_row = PROGRAM.more_speakers_row
name_apart = PROGRAM.name_apart
os = PROGRAM.os
parse_timecode = PROGRAM.parse_timecode
path_key = PROGRAM.path_key
row_picker_for = PROGRAM.row_picker_for
row_picker_watch = PROGRAM.row_picker_watch
sample_count = PROGRAM.sample_count
speaker_name_cell = PROGRAM.speaker_name_cell
speaks_as = PROGRAM.speaks_as
split_cell_build = PROGRAM.split_cell_build
split_column_fit = PROGRAM.split_column_fit
table_build = PROGRAM.table_build
table_rows_fit = PROGRAM.table_rows_fit
tree_build = PROGRAM.tree_build
tree_cell = PROGRAM.tree_cell
tree_field = PROGRAM.tree_field
tree_row = PROGRAM.tree_row
tree_rows_fit = PROGRAM.tree_rows_fit
video_facts = PROGRAM.video_facts
video_kinds_again = PROGRAM.video_kinds_again
wide_bar_of = PROGRAM.wide_bar_of
window_suggestion = PROGRAM.window_suggestion

# The cells the tables are made of -- SpeakerName, kind_cell_for and
# seven more -- are the window's and stand below the line this file is
# read at, so each is asked as PROGRAM.<name> at the call.


class AssignmentTable(object):
    """The tables of the second tab, and what they keep between builds.

    Made once by the sheet and never replaced. It reads the production
    out of the ProjectModel; what the rest of the window does when a
    table changes -- the prework, the separation, the file list's Kind
    -- is handed in once through wire(), before the first build.
    """

    def __init__(self, sheet, model, state, player):
        """Empty, with the lists a rebuild empties and fills again."""
        self.sheet, self.model, self.state = sheet, model, state
        self.player = player
        self.audio_fields, self.video_fields = [], []
        # The recordings of the assignment tree: (its row, the file, the
        # plain caption). The voices are not in here -- they have no file.
        self.file_rows = []
        # Which recordings somebody left open, over a rebuild of the tree.
        # Open is what a fresh one starts as: the assignment is underneath.
        self.tree_open = ByFile()
        # Two dictionaries of files the table builder fills and empties
        # again, and what the table last suggested itself.
        self.own_audio_names = ByFile()
        self.piece_label = ByFile()
        self.suggestions = ByFile()
        self.buttons_check = self.window = None

    def wire(self, buttons_check, video_kind_again, audio_use_now,
             audio_use_value, kind_answered, main_track_show,
             prework_kick_off, show_weak, tc_column_show, wide_cameras_now,
             voice_rows, split_parts):
        """Take what the rest of the window does; answer the two builds.

        *voice_rows* are the five of make_voice_rows a build reaches
        for, *split_parts* the four of make_speaker_split. What comes
        back is assignment_fresh and refresh_names.
        """
        self.buttons_check = buttons_check
        self.window = (video_kind_again, audio_use_now, audio_use_value,
                       kind_answered, main_track_show, prework_kick_off,
                       show_weak, tc_column_show, wide_cameras_now
                       ) + tuple(voice_rows) + tuple(split_parts)
        # The separation stands above this and redraws both tables when
        # a result comes back; the table builder is written before the
        # window, so the way over for both is state, as preview_soon's.
        self.state["assignment_fresh"] = self.assignment_fresh
        self.state["refresh_names"] = self.refresh_names
        return self.assignment_fresh, self.refresh_names

    def assignment_remember(self):
        """Write what the tables and the player show into the project."""
        m, state, player = self.model, self.state, self.player
        remembered = m.remembered
        for row, nv, cv in m.assign_lines:
            # The finished mix's row holds no answer of its own; set back,
            # the row finds the one it had.
            if (state.get("sound_holds") or {}).get(row[0]) \
                    == SOUND_FINISHED:
                continue
            # Where the voices stand underneath the row holds no selector,
            # and that fallback must not overwrite an older assignment.
            old = remembered.get("audio:" + row[0])
            quiet_row = os.path.abspath(row[0]) in (state.get("voiced") or ())
            # Only the answer: a guess written back is a guess nobody
            # checks, and a file renamed afterwards no longer moves it.
            remembered["audio:" + row[0]] = (nv.typed(), camera_to_remember(
                cv.get(), getattr(cv, "derived", None),
                old[1] if (quiet_row and old) else None))
        for file_path, nv, own_box, own_name_box in m.camera_lines:
            remembered.update(camera_name_kept(file_path, nv))
            # Only what somebody clicked is stored: a tick derived from
            # "one camera, no recording" is worked out afresh every time.
            if file_path not in (state.get("forced_own") or ()):
                remembered["own:" + file_path] = own_box.get()
            remembered["ownname:" + file_path] = own_name_box.get()
        for file_path, value in m.clip_kinds.items():
            remembered["kind:" + file_path] = value.get()
        # Where the player is belongs in the project: opening it again
        # should carry on there, not at the start of the file.
        try:
            if player.file_path:
                remembered["player_file"] = player.file_path
                remembered["player_spot"] = round(player.spot_s(), 3)
        except Exception:
            pass

    def cell(self, t, line, column, text, colour=None):
        """Put *text* into one cell of table *t*, in *colour* if given."""
        p = QtWidgets.QTableWidgetItem(text)
        if colour:
            p.setForeground(QtGui.QBrush(QtGui.QColor(colour)))
        t.setItem(line, column, p)
        return p

    def assignment_check(self):
        """Mark the trouble spots red, and let the preview hear the name."""
        m, state = self.model, self.state
        # A typed name is an answer like any other: without this the
        # preview keeps the old name at the old camera.
        if state.get("preview_soon"):
            state["preview_soon"]()
        assignment_marks_show(
            self.audio_fields, m.assign_lines, self.video_fields,
            m.camera_lines, bool(m.multitrack.get()), state, m.voice_lines)
        self.buttons_check()

    def assignment_fresh(self, forget=()):
        """Build both tables again, out of assignment_tables_build."""
        m, sheet = self.model, self.sheet
        (video_kind_again, audio_use_now, audio_use_value,
         kind_answered, main_track_show, prework_kick_off, show_weak,
         tc_column_show, wide_cameras_now, assignment_state_show,
         assignment_row_show, folded_show, voice_add, voices_build,
         speaker_split_kick_off, split_stop, voices_of,
         several_set) = self.window
        assignment_tables_build(
            forget, QtCore.Qt, QtCore, QtWidgets, m.assign_lines,
            sheet.assign_position, self.audio_fields, m.camera_lines,
            m.clip_kinds, self.file_rows, m.files, m.no_join,
            self.own_audio_names, self.piece_label, m.production,
            m.remembered, m.split_files, self.state, self.suggestions,
            self.tree_open, self.video_fields, video_kind_again,
            m.voice_lines, self.assignment_check, self.assignment_remember,
            assignment_row_show, assignment_state_show, audio_use_now,
            audio_use_value, self.cell, m.clip_kind_value, folded_show,
            kind_answered, self.line_show, main_track_show,
            prework_kick_off, several_set, show_weak,
            speaker_split_kick_off, split_stop, tc_column_show,
            m.together_now, voice_add, voices_build, voices_of,
            wide_cameras_now, sheet.window_enable,
            sheet.window_position_show, self.window_prefill)

    def refresh_names(self):
        """Suggest file names again; hand-edited ones stay."""
        untouched = [p for p, nv, _k, _n in self.model.camera_lines
                     if nv.get() == self.suggestions.get(p)
                     and not nv.by_hand]
        self.assignment_fresh(untouched)

    def line_show(self, table, file_list):
        """A clicked row of the camera table: that file in the player.

        One entry per row. The recordings are a tree and not a table,
        and a click in it is answered by assignment_row_show.
        """
        row = table.currentRow()
        if 0 <= row < len(file_list) and file_list[row]:
            self.sheet.player_load(file_list[row])

    def window_prefill(self, videos):
        """Take a camera's clock time as the axis; fill in no boundary.

        An In point and an Out point nobody set stay empty, and the run
        then takes the whole material, as the command line does. Filled
        in from the cameras they reached past the first frame, and the
        run warned about a window nobody chose. What stays is the axis:
        a camera with a timecode is enough to set a window by hand.
        """
        state = self.state
        entries, fps = [], 30.0
        for b in videos:
            try:
                if os.path.splitext(b)[1].lower() in AUDIO_SUFFIXES:
                    t0, duration = file_timecode(b), sample_count(b) / float(SR)
                else:
                    info = video_facts(b)
                    fps = max(1.0, info.get("fps") or 30.0)
                    t0 = parse_timecode(info["tc"], fps) if info.get("tc") else None
                    duration = info.get("duration") or 0.0
            except Exception:
                continue
            measured = state["axis"].get(path_key(b))
            if t0 is None or (measured is not None   # measured first
                               and state.get("axis_absolute")):
                t0 = measured
            entries.append((t0, duration))
        from_s, until, absolute = window_suggestion(entries, fps)
        if not (from_s and until and absolute):
            return
        # Nothing goes into the In or Out point: the run cannot tell a value
        # put there by the window from a chosen one, and one sent a clock time
        # before the first frame and made the run warn.
        if not state["axis"] or state.get("axis_absolute"):
            state["tc_there"] = True


def camera_name_typed(kept, typed, offered):
    """Whether a camera's kept name is one somebody typed.

    The project file says so under "videotyped:"; what was typed stands
    as typed, whatever it looks like. An older file does not say, and
    there a name the table could have offered itself -- *offered*, the
    one told apart with " 2" included -- counts as never typed.
    """
    if not kept:
        return False
    if typed is not None:
        return bool(typed)
    return kept not in offered


def name_typed_watch(field, name_value):
    """Mark *name_value* typed the moment its field says something else.

    Watched before field_bind binds the two: a name the program sets
    reaches the value first and the field after, so only a name that
    came in through the field differs from the value here.
    """
    def seen(text):
        """Typed where the field runs ahead of the value."""
        if text != str(name_value.get()):
            name_value.by_hand = True

    field.textChanged.connect(seen)
    return field


def camera_name_kept(file_path, name_value):
    """What the project file keeps of one camera's name: it, and who."""
    return {"video:" + file_path: name_value.get(),
            "videotyped:" + file_path: bool(name_value.by_hand)}


def reason_own_line(cell, box):
    """Move the reason written after a Kind field onto a line under it.

    In the field it made the field, its column and the table so wide
    that a narrow window cut it off at the table's edge. Under it, it
    wraps to the field's width instead. Returns the cell to put in the
    table: *cell* itself where the field carries no reason.
    """
    why = getattr(getattr(box, "_why", None), "why", "")
    if not why or not box.isEnabled():
        return cell
    PROGRAM.why_in_field(box, "", COLOURS["quiet"])
    holder = QtWidgets.QWidget()
    column = QtWidgets.QVBoxLayout(holder)
    column.setContentsMargins(0, 0, 0, 2)
    column.setSpacing(0)
    column.addWidget(cell)
    # A file name has no space to wrap at: these give it places to.
    line = label("".join(c + "​" if c in "_.-" else c for c in why),
                 COLOURS["quiet"])
    line.setWordWrap(True)
    line.setObjectName("reason_line")
    # No width of its own: the column is as wide as the field.
    line.setSizePolicy(QtWidgets.QSizePolicy.Ignored,
                       QtWidgets.QSizePolicy.Preferred)
    column.addWidget(line)
    box.setAccessibleDescription(why)
    return holder


def reason_rows_fit(table, column):
    """Make each row whose *column* carries a reason line tall enough."""
    for row in range(table.rowCount()):
        holder = table.cellWidget(row, column)
        if holder is None or holder.findChild(
                QtWidgets.QLabel, "reason_line") is None:
            continue
        table.setRowHeight(row, max(table.rowHeight(row),
                                    holder.heightForWidth(
                                        table.columnWidth(column))))


def finished_row_shown(node, row, stem, caption, state, assign_lines,
                       file_rows):
    """Show a recording set to the finished mix as what it is, if it is.

    No speaker and no camera: the run leaves its row out of the plan,
    and so does the table -- "do not use" in the lines, which every
    reader of them already leaves out, and the reason in the cell. It
    stays a row with a file, so its timecode and its fit are shown.
    """
    if (state.get("sound_holds") or {}).get(row[0]) != SOUND_FINISHED:
        return False
    file_rows.append((node, row[0], caption))
    tree_cell(node, 2, T('the finished mix -- no speaker, no camera'),
              COLOURS["quiet"])
    assign_lines.append((row, PROGRAM.SpeakerName("", stem),
                         Value(IGNORE_AUDIO)))
    return True


def assignment_tables_build(forget, Qt, QtCore, QtWidgets, assign_lines,
                            assign_position, audio_fields, camera_lines,
                            clip_kind_values, file_rows, files, no_join,
                            own_audio_names, piece_label, production_var,
                            remembered, split_files, state, suggestions,
                            tree_open, video_fields, video_kind_again,
                            voice_lines, assignment_check,
                            assignment_remember, assignment_row_show,
                            assignment_state_show, audio_use_now,
                            audio_use_value, cell, clip_kind_value,
                            folded_show, kind_answered, line_show,
                            main_track_show, prework_kick_off, several_set,
                            show_weak, speaker_split_kick_off, split_stop,
                            tc_column_show, together_now, voice_add,
                            voices_build, voices_of, wide_cameras_now,
                            window_enable, window_position_show,
                            window_prefill):
    """Two tables: audio recordings above, video files below.

    Whatever is needed from the window comes in as an argument and keeps
    its name inside. The lists and dictionaries belong to AssignmentTable
    and are emptied at the start of every rebuild. Two names the window
    binds after the table is wired come through *state*.
    """
    assignment_remember()
    for p in forget:
        remembered.pop("video:" + p, None)
    # Between the old table going and the new one arriving Qt paints a
    # flash. Painting waits for the next turn of the loop.
    holder = assign_position.parentWidget()
    if holder is not None and holder.updatesEnabled():
        holder.setUpdatesEnabled(False)
        QtCore.QTimer.singleShot(
            0, lambda h=holder: h.setUpdatesEnabled(True))
    old = state.get("assignment_content")
    if old is not None:
        old.setParent(None)
        old.deleteLater()
    # The marks of the old table went with its widgets.
    content = QtWidgets.QWidget()
    column_layout = QtWidgets.QVBoxLayout(content)
    column_layout.setContentsMargins(0, 0, 0, 0)
    column_layout.setSpacing(10)
    # In front of the Multitrack tick and the prework bar.
    assign_position.insertWidget(0, content)
    state["assignment_content"] = content
    assign_lines[:] = []
    # Cleared with the rest: a row that no longer exists must not still
    # be able to say which camera it is on.
    voice_lines[:] = []
    file_rows[:] = []
    state["split_cells"] = []
    state["voiced"] = set()
    audio_fields[:] = []
    video_fields[:] = []
    # The two lines carrying a reason are widgets of that table too:
    # left pointing at the old ones, the next check hits deleted Qt.
    state["audio_reason"] = None
    state["video_reason"] = None
    audio_files = [p for p, a in files if a == "audio"]
    videos = sorted([p for p, a in files if a == "video"],
                    key=lambda x: os.path.basename(x).lower())
    # A camera contributing its audio is an input track like any other,
    # so it is in the table above. Emptied here: a rebuild starts over.
    own_audio_names.clear()
    # What a cut-out piece is called: the label the cutting gave it.
    # Without it the piece is named after its file's channel number.
    piece_label.clear()
    for _src, _pieces in split_files.items():
        for _path, _label in _pieces or []:
            piece_label[_path] = _label
    # The file list's own derivation, called and not copied: both
    # tabs show one value and must not disagree about it.
    own_now, forced = audio_use_now()
    chains, camera_audio, own = assignment_rows(
        audio_files, videos, own_now,
        split_of=lambda x: [t[0] for t in
                            split_files.get(x) or []],
        apart=no_join, together=together_now())
    state["camera_audio"] = camera_audio
    state["own_audio_rows"] = own
    state["own_cameras"] = list(own_now)
    state["forced_own"] = list(forced)
    if not chains:
        column_layout.addWidget(label(
            T('No sound in use yet -- add an audio recording, or set '
              'a video file\'s Camera audio to "use internal audio" in the '
              'file list.'), COLOURS["quiet"]))
        # Before the exit, not after the table: the time axis is needed
        # whether or not any sound is in use.
        if videos:
            prework_kick_off(list(videos))
        # And the button, for the same reason: the way in here is also
        # taking the last sound away.
        assignment_check()
        return
    # Cameras, then MIX_ONLY (in the mix, first track on no camera) and
    # IGNORE_AUDIO (left out). A camera is its path: two files of one
    # name are two cameras, and the chooser shows them apart.
    targets = list(videos) + [MIX_ONLY, IGNORE_AUDIO]
    wide = wide_bar_of(targets, *wide_cameras_now(),
                       aside=state.setdefault("wide_set_aside", {}))
    barred = wide["barred"]
    head = T('Audio recording')
    belongs_head = T('belongs to')
    # The separation column is only there where there is a separation
    # to have. No button -- only what came of it, and a way to stop.
    columns = [head, T('Speaker name'), belongs_head, "Timecode"]
    if not SPEAKER_SPLIT_OFF:
        columns.append(T('Speakers'))
    tree_audio = tree_build(columns)
    # Sync only: the columns about speakers stay in the tree, hidden,
    # so the cells keep their numbers and the project file its keys.
    sync_only = PROGRAM.sync_only(state)
    tree_audio.setColumnHidden(1, sync_only)
    # And "belongs to" with them: without a plan the run reads no
    # camera off a recording, so the column would promise an answer.
    tree_audio.setColumnHidden(2, sync_only)
    if not SPEAKER_SPLIT_OFF:
        tree_audio.setColumnHidden(4, sync_only)
    state["assignment_tree"] = tree_audio
    state["row_picker"] = row_picker_for(tree_audio)
    column_layout.addWidget(tree_audio, 1)
    audio_file_list = []
    # Without timecode a position cannot be converted onto the common axis.
    # Where not one file carries one, the values are relative to the first.
    tc_of_row = []
    for row, _ in chains:
        try:
            tc_of_row.append(file_timecode(row[0]))
        except Exception:
            tc_of_row.append(None)
    without_tc = not any(t is not None for t in tc_of_row)
    # Two recordings of one file name are told apart as in the file list.
    heard = PROGRAM.recording_labels(audio_files)
    state["without_tc"] = without_tc
    if not without_tc:
        state["tc_there"] = True
    for (row, _) in chains:
        first = row[0]
        camera_track = os.path.abspath(first) in state["own_audio_rows"]
        from_camera = state["own_audio_rows"].get(first) \
            if isinstance(state["own_audio_rows"], dict) else None
        stem = (guess_camera_name(from_camera or first)
                 if camera_track else guess_speaker_name(first,
                                                         heard.get(first)))
        # So the two rows of one camera can be told apart.
        if piece_label.get(first):
            stem = piece_label[first]
        if camera_track:
            stem = remembered.get("ownname:" + first) or stem
        caption = heard.get(first) or os.path.basename(first)
        if camera_track:
            caption += T('   (camera audio)')
        elif len(row) > 1:
            caption += "  (+%d)" % (len(row) - 1)
        node = tree_row(tree_audio, None, [caption])
        node[0].setData(first, Qt.UserRole + 1)
        if finished_row_shown(node, row, stem, caption, state,
                              assign_lines, file_rows):
            continue
        audio_file_list.append(first)
        file_rows.append((node, first, caption))
        old_name, old_camera = remembered.get("audio:" + first, (None, None))
        # Empty until somebody answers, with the guess offered in grey
        # and never written in. The field itself knows both.
        name_value = PROGRAM.SpeakerName(old_name or "", stem)
        # The voices this recording is showing. Where there are any, the
        # assignment belongs to them: it has exactly one level.
        kids = [] if sync_only else voices_of(first)
        if kids:
            state["voiced"].add(os.path.abspath(first))
        if SPEAKER_SPLIT_OFF:
            # Nothing can be told apart on this machine, so there is
            # only one answer to give and a plain field to give it in.
            name_field = field_bind(QtWidgets.QLineEdit(), name_value)
            speaks_as(name_field, T('Speaker name'), caption)
        else:
            # Only an answer picks the answer: a separation that comes
            # back with four voices does not set the field itself.
            said = remembered.get("several:" + first)
            several_value = Value(bool(said))
            several_value.listen(
                lambda *_, p=first, v=several_value: several_set(
                    p, v.get()))
            name_field = speaker_name_cell(name_value, several_value,
                                           caption)
        tree_field(tree_audio, node, 1, name_field)
        row_picker_watch(state["row_picker"], name_field)
        # Before the branch below, so a row without a selector says how
        # its separation stands too.
        if not SPEAKER_SPLIT_OFF:
            box_, cell_ = split_cell_build(first, split_stop, node[4])
            tree_field(tree_audio, node, 4, box_)
            state["split_cells"].append(cell_)
        # The voices go under the row before the row is filled in:
        # whether it has any decides what the row carries itself.
        if voices_build(tree_audio, node, first, videos, targets, wide):
            tree_audio.setExpanded(node[0].index(),
                                   tree_open.get(first, True))
            folded_show(node[0].index())
        # Where the voices hang underneath they carry the cameras and
        # this row none. The cell says so rather than standing empty.
        if kids:
            tree_cell(node, 2, T('the voices below carry the cameras'),
                      COLOURS["quiet"])
            # MIX_ONLY is the truth here: no track belongs to one camera
            # alone.
            assign_lines.append((row, name_value, Value(MIX_ONLY)))
            continue
        # Camera rows get the full selector too: a clip-on microphone
        # in one camera does not mean the person is filmed by it.
        own_camera = (next((b for b in videos if path_key(b) == path_key(
            from_camera or first)), "") if camera_track else "")
        was = camera_after_a_mark("audio:" + first, old_camera, wide)
        picked, worked_out = camera_row_cameras(
            was, wide["pickable"], name_value.get(), videos,
            own_camera="" if own_camera in barred else own_camera)
        camera_value = Value(MIX_ONLY if picked in barred else picked)
        camera_value.derived = worked_out
        box = QtWidgets.QComboBox()
        speaks_as(box, belongs_head, caption)
        fill_choices(box, targets, camera_value.get())
        PROGRAM.choices_shut(box, barred, wide["why"], COLOURS["quiet"])

        def chosen(_i=0, b=box, value=camera_value, f=name_field,
                   guess=name_value.suggested):
            """Hand the value on; an ignored track needs no name."""
            v = b.currentData()
            value.set(v)
            PROGRAM.name_shut(f, v == IGNORE_AUDIO, guess, COLOURS["quiet"])

        box.currentIndexChanged.connect(chosen)
        chosen()
        PROGRAM.moved_says_why(box, "audio:" + first, wide, COLOURS["quiet"])
        # When the camera changes, the summary below no longer fits.
        box.currentIndexChanged.connect(
            lambda *_: QtCore.QTimer.singleShot(0, state["refresh_names"]))
        tree_field(tree_audio, node, 2, box)
        row_picker_watch(state["row_picker"], box)
        if camera_track:
            own_audio_names.setdefault(from_camera or first,
                                       []).append(name_value)
        assign_lines.append((row, name_value, camera_value))
        audio_fields.append(name_field)
        name_value.listen(lambda *_: QtCore.QTimer.singleShot(
            0, assignment_check))
    # A voice the separation missed is asked for below the tree: it is
    # the input to another separation, not a row of this one.
    more = (None if sync_only
            else more_speakers_row(audio_file_list, voice_add))
    if more is not None:
        column_layout.addWidget(more)
    audio_reason = label("", COLOURS["error"])
    audio_reason.setWordWrap(True)
    audio_reason.setVisible(False)
    column_layout.addWidget(audio_reason)
    state["audio_reason"] = audio_reason
    # The rows that carry a file, which is not every row: the timecode
    # and the "does not fit" mark belong to a recording, not a voice.
    state["file_rows"] = list(file_rows)
    tc_column_show()
    # One tree where there were two tables, so it may be as tall as
    # both were: 120 each, and the heading the second one had.
    tree_rows_fit(tree_audio, 266)
    for _signal in (tree_audio.expanded, tree_audio.collapsed):
        _signal.connect(folded_show)
    tree_audio.selectionModel().selectionChanged.connect(
        lambda *_, t=tree_audio: assignment_row_show(t))

    window_position_show()

    # --- second table: what the new video files should be called
    if not production_var.get():
        production_var.set(guess_production_name(chains[0][0][0]))
    camera_lines[:] = []
    # What comes out, and the two decisions only watching can settle:
    # what the clip is, and whether its sound is material.
    table_video = table_build([T('Camera'), T('new file name'),
                               T('gets audio from'), T('Kind'),
                               T('Camera audio')])
    # Sync only: the new file name stays, since the run names each file
    # and its track after it on every path; where the audio comes from
    # is read off the speakers, and there are none -- so that one hides.
    table_video.setColumnHidden(2, sync_only)
    column_layout.addWidget(table_video, 1)
    video_reason = label("", COLOURS["error"])
    video_reason.setWordWrap(True)
    video_reason.setVisible(False)
    column_layout.addWidget(video_reason)
    state["video_reason"] = video_reason
    taken = {}
    for _, nv, cv in assign_lines:
        if PROGRAM.is_a_path(cv.get()):
            taken.setdefault(path_key(cv.get()), []).append(nv)
    wides, said = wide_cameras_now()
    shown = PROGRAM.camera_labels(videos)
    state["camera_labels"] = shown

    def kinds_refresh():
        """Say the Kind column again, with the wide shot as it is now.

        A voice given a name and a camera makes that camera one somebody
        sits in front of, so it is no longer the derived wide shot, and
        the table is built before that answer exists. Both tables that
        show a Kind: left out, the file list keeps saying "Wide shot".
        """
        if state.get("closing"):
            return
        video_kinds_again(video_kind_again)
        try:
            fresh, marked = wide_cameras_now()
            for i, path in enumerate(videos):
                if i >= table_video.rowCount():
                    break
                box_cell, _box = PROGRAM.kind_cell_for(
                    path, clip_kind_value(path), fresh, marked,
                    state.get("no_place"), clip_kind_values,
                    COLOURS["quiet"], lambda q=path: kind_answered(q), shown)
                table_video.setCellWidget(i, 3, reason_own_line(box_cell,
                                                                _box))
            reason_rows_fit(table_video, 3)
        except RuntimeError:
            # The table was rebuilt under us; the new one is right.
            return

    state["kinds_refresh"] = kinds_refresh
    offered_now = set()
    for row, b in enumerate(videos):
        short = os.path.basename(b)
        table_video.insertRow(row)
        # Named as the choosers name it, the whole path on the tooltip.
        cell(table_video, row, 0, shown[b]).setToolTip(b)
        clip_kind = clip_kind_value(b)
        kind_cell, _kind_box = PROGRAM.kind_cell_for(
            b, clip_kind, wides, said, state.get("no_place"),
            clip_kind_values, COLOURS["quiet"],
            lambda p=b: kind_answered(p), shown)
        table_video.setCellWidget(row, 3, reason_own_line(kind_cell,
                                                          _kind_box))
        own_audio = audio_use_value(b)
        used, why = PROGRAM.audio_use_settled(b, own_now, forced,
                                              has_sound(b), clip_kind.get())
        if clip_kind.get() not in CAMERA_TYPES:
            # A finished clip has nothing to assign and gets no new
            # name, so a sentence stands where the empty fields would.
            cell(table_video, row, 1,
                  T('stays out') if clip_kind.get() == TYPE_IGNORED
                  else T('used directly'),
                  COLOURS["quiet"])
            cell(table_video, row, 2, "")
            sound_off, sound_off_box = PROGRAM.camera_audio_cell(
                short, used, why, COLOURS["quiet"], True)
            PROGRAM.audio_use_bind(sound_off_box, own_audio, why)
            table_video.setCellWidget(row, 4, sound_off)
            continue
        # A camera can contribute its own audio and is then a track
        # like any other. One camera can give more than one.
        mine = own_audio_names.get(b) or []
        own_audio_name = mine[0] if mine else Value(
            remembered.get("ownname:" + b) or guess_camera_name(b))
        own = list(taken.get(path_key(b)) or [])
        if used:
            own += mine or [own_audio_name]
        multitrack_now = bool(state["multitrack"].get()) and not sync_only
        # A kept name nobody typed was the table's own -- a project
        # file saves every field -- so it follows the table.
        kept = remembered.get("video:" + b) or ""
        offer = camera_name_suggestion(production_var.get(), short, own,
                                       multitrack_now, sync_only)
        by_hand = camera_name_typed(
            kept, remembered.get("videotyped:" + b),
            camera_names_offered(production_var.get(), short, own)
            | {name_apart(offer, set(offered_now))})
        kept = kept if by_hand else ""
        # Told apart from the names the rows above carry, as the run does.
        suggestion = name_apart(offer, set(offered_now) if kept
                                else offered_now)
        if kept:
            offered_now.add(kept.lower())
        suggestions[b] = suggestion
        name_value = Value(kept or suggestion)
        name_value.by_hand = by_hand
        name_entry = field_bind(name_typed_watch(QtWidgets.QLineEdit(),
                                                 name_value), name_value)
        speaks_as(name_entry, T('new file name'), short)
        from_the_front(name_entry)
        table_video.setCellWidget(row, 1, name_entry)
        cell(table_video, row, 2, camera_gets_from(own),
             COLOURS["quiet"])
        # The file list's field again, on the same value: it stands
        # here because the player does, and usable sound is heard.
        sound, sound_box = PROGRAM.camera_audio_cell(
            short, used, why, COLOURS["quiet"], True)
        PROGRAM.audio_use_bind(sound_box, own_audio, why)
        table_video.setCellWidget(row, 4, sound)
        camera_lines.append((b, name_value, own_audio, own_audio_name))
        video_fields.append(name_entry)
        name_value.listen(lambda *_: QtCore.QTimer.singleShot(
            0, assignment_check))
    table_rows_fit(table_video)
    table_video.itemSelectionChanged.connect(
        lambda t=table_video, d=list(videos): line_show(t, d))
    table_video.resizeColumnsToContents()
    for c in range(len(columns)):
        tree_audio.resizeColumnToContents(c)
    # The name columns carry input fields, which must not shrink to their
    # content; the first also carries triangles and the indentation.
    tree_audio.setColumnWidth(0, max(220, tree_audio.columnWidth(0) + 30))
    # The new file name is long, so it gets whatever is left.
    table_video.horizontalHeader().setStretchLastSection(False)
    table_video.horizontalHeader().setSectionResizeMode(
        1, QtWidgets.QHeaderView.Stretch)
    reason_rows_fit(table_video, 3)
    tree_audio.header().setStretchLastSection(True)
    if not SPEAKER_SPLIT_OFF:
        # A width for what the column will hold, not for what is in it:
        # a column measuring its contents measures an empty one.
        split_column_fit(tree_audio, 4)
    # The camera list now stands, so queue what can be prepared: the
    # envelope for every camera, plus the audio of those contributing it.
    window_prefill(videos)
    window_enable()
    show_weak()
    main_track_show()
    every_cameras = [p for p, _n, _k, _own_name in camera_lines]
    # A camera more or fewer can make another run's handover the right one.
    PROGRAM.handover_follows(state, every_cameras)
    # Every camera goes in either way -- the time axis lives on those
    # envelopes. Only fetching the sound is for those set to "use".
    having_audio = [p for p in every_cameras if p in own_now]
    # The audio recordings belong in it too, and every block of them:
    # a recording of three blocks is measured and In-pointed thrice.
    every = list(every_cameras)
    for r, _nv, _cv in assign_lines:
        for x in r:
            if x not in every:
                every.append(x)
    if every:
        prework_kick_off(every, having_audio)
    # Beside the prework, not behind it: the two do not slow each
    # other down, and the separation is the long one of the two.
    if not sync_only:
        speaker_split_kick_off()
    assignment_check()
    assignment_state_show()
    # The last camera to be given a speaker takes the wide shot away.
    state["wide_state_show"]()
    # And the file list says so too: built before anybody is assigned,
    # it would go on calling every camera the wide shot.
    video_kinds_again(video_kind_again)
