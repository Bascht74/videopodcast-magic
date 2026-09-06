# -*- coding: utf-8 -*-
"""The window, and everything it shows, asks or offers.

A piece of the program, read out of the folder beside it by beside().
It cannot import the file it was cut out of, because that file is
still being read while this one is; the program is handed in instead,
and every name this piece uses out of it is bound below, by name, so
that nothing in here comes from nowhere.
"""

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

# What the program has and this piece uses, bound once so that the
# window reads as it did in the one file. Left out is what the program
# changes while it runs -- a copy would part from it at the first
# assignment -- so those few stay PROGRAM.something down below.
AUDIO_MATERIAL = PROGRAM.AUDIO_MATERIAL
AUDIO_SUFFIXES = PROGRAM.AUDIO_SUFFIXES
AUDIO_UNUSED = PROGRAM.AUDIO_UNUSED
AUDIO_USE = PROGRAM.AUDIO_USE
ByFile = PROGRAM.ByFile
CAMERA_TYPES = PROGRAM.CAMERA_TYPES
CLIP_TYPES = PROGRAM.CLIP_TYPES
COLOURS = PROGRAM.COLOURS
CUT_CHOICES = PROGRAM.CUT_CHOICES
CUT_FIELDS = PROGRAM.CUT_FIELDS
FILE_FORMAT = PROGRAM.FILE_FORMAT
FileSet = PROGRAM.FileSet
Finding = PROGRAM.Finding
IGNORE_AUDIO = PROGRAM.IGNORE_AUDIO
MIX_ONLY = PROGRAM.MIX_ONLY
NAME_ROOM = PROGRAM.NAME_ROOM
ON_DARK = PROGRAM.ON_DARK
PRESET_NONE = PROGRAM.PRESET_NONE
PROJECT_PREFIX = PROGRAM.PROJECT_PREFIX
ProgressPlan = PROGRAM.ProgressPlan
ROW_ROOM = PROGRAM.ROW_ROOM
RUN_STOP = PROGRAM.RUN_STOP
SEEK_AGAIN_MS = PROGRAM.SEEK_AGAIN_MS
SEEK_HIT_MS = PROGRAM.SEEK_HIT_MS
SEEK_PATIENCE_S = PROGRAM.SEEK_PATIENCE_S
SEEK_SETTLE_S = PROGRAM.SEEK_SETTLE_S
SEVERAL_SPEAKERS = PROGRAM.SEVERAL_SPEAKERS
SHOT_NAMES = PROGRAM.SHOT_NAMES
SPEAKER_ROWS_SHOWN = PROGRAM.SPEAKER_ROWS_SHOWN
SPEAKER_SPLIT_OFF = PROGRAM.SPEAKER_SPLIT_OFF
SPEAKER_SPLIT_SPEED = PROGRAM.SPEAKER_SPLIT_SPEED
SPEAKER_SPLIT_TOGETHER_CORES = PROGRAM.SPEAKER_SPLIT_TOGETHER_CORES
SPEAKER_STATE = PROGRAM.SPEAKER_STATE
SPOT_ARRIVED_MS = PROGRAM.SPOT_ARRIVED_MS
SR = PROGRAM.SR
Stopped = PROGRAM.Stopped
T = PROGRAM.T
TN = PROGRAM.TN
TYPE_CONTENT = PROGRAM.TYPE_CONTENT
TYPE_IGNORED = PROGRAM.TYPE_IGNORED
TYPE_INTRO = PROGRAM.TYPE_INTRO
TYPE_OUTRO = PROGRAM.TYPE_OUTRO
TYPE_WIDE = PROGRAM.TYPE_WIDE
UPDATE_OFF = PROGRAM.UPDATE_OFF
VERSION = PROGRAM.VERSION
VIDEO_SUFFIXES = PROGRAM.VIDEO_SUFFIXES
Value = PROGRAM.Value
_ENV = PROGRAM._ENV
_joins_seamlessly = PROGRAM._joins_seamlessly
_require_module = PROGRAM._require_module
api_key_source = PROGRAM.api_key_source
app_style_set = PROGRAM.app_style_set
apply_time_window = PROGRAM.apply_time_window
as_bad = PROGRAM.as_bad
as_data_size = PROGRAM.as_data_size
as_good = PROGRAM.as_good
as_head = PROGRAM.as_head
as_hms = PROGRAM.as_hms
as_minutes = PROGRAM.as_minutes
as_relative_time = PROGRAM.as_relative_time
assignment_pairs = PROGRAM.assignment_pairs
assignment_rows = PROGRAM.assignment_rows
atexit = PROGRAM.atexit
audio_clock_of = PROGRAM.audio_clock_of
audio_start_of = PROGRAM.audio_start_of
audio_summary = PROGRAM.audio_summary
axis_answer_kept = PROGRAM.axis_answer_kept
axis_still_valid = PROGRAM.axis_still_valid
axis_with_blocks = PROGRAM.axis_with_blocks
axis_worth_measuring = PROGRAM.axis_worth_measuring
back_pick = PROGRAM.back_pick
beside = PROGRAM.beside
block_at = PROGRAM.block_at
blocks_facts = PROGRAM.blocks_facts
build_handover = PROGRAM.build_handover
camera_after_a_mark = PROGRAM.camera_after_a_mark
camera_gets_from = PROGRAM.camera_gets_from
camera_name_suggestion = PROGRAM.camera_name_suggestion
camera_row_cameras = PROGRAM.camera_row_cameras
camera_shortfall_lines = PROGRAM.camera_shortfall_lines
camera_start_of = PROGRAM.camera_start_of
camera_to_remember = PROGRAM.camera_to_remember
cameras_in_track_order = PROGRAM.cameras_in_track_order
cameras_with_a_speaker = PROGRAM.cameras_with_a_speaker
cameras_with_own_audio = PROGRAM.cameras_with_own_audio
channel_count = PROGRAM.channel_count
channel_facts_cached = PROGRAM.channel_facts_cached
channel_facts_name = PROGRAM.channel_facts_name
channel_joins = PROGRAM.channel_joins
check_resolve = PROGRAM.check_resolve
collect_findings = PROGRAM.collect_findings
colours_pick = PROGRAM.colours_pick
cut_basis_line = PROGRAM.cut_basis_line
cut_box_title = PROGRAM.cut_box_title
cut_has_people = PROGRAM.cut_has_people
cut_statistics = PROGRAM.cut_statistics
cut_title_of = PROGRAM.cut_title_of
decimal_text = PROGRAM.decimal_text
delete_api_key = PROGRAM.delete_api_key
desktop_is_dark = PROGRAM.desktop_is_dark
every_audio_block = PROGRAM.every_audio_block
ffmpeg_can_be_had = PROGRAM.ffmpeg_can_be_had
file_timecode = PROGRAM.file_timecode
fill_choices = PROGRAM.fill_choices
find_handover_file = PROGRAM.find_handover_file
find_project_file = PROGRAM.find_project_file
find_required_tools = PROGRAM.find_required_tools
finished_tracks_deeper = PROGRAM.finished_tracks_deeper
finished_tracks_find = PROGRAM.finished_tracks_find
forget_soxr = PROGRAM.forget_soxr
format_complaint = PROGRAM.format_complaint
group_recording_parts = PROGRAM.group_recording_parts
group_text = PROGRAM.group_text
guess_camera_name = PROGRAM.guess_camera_name
guess_production_name = PROGRAM.guess_production_name
guess_speaker_name = PROGRAM.guess_speaker_name
gui_log = PROGRAM.gui_log
has_sound = PROGRAM.has_sound
how_many_processors = PROGRAM.how_many_processors
how_to_get_ffmpeg = PROGRAM.how_to_get_ffmpeg
https_context = PROGRAM.https_context
install_ffmpeg = PROGRAM.install_ffmpeg
installed_by_a_package_manager = PROGRAM.installed_by_a_package_manager
joined_channels = PROGRAM.joined_channels
json = PROGRAM.json
keep_setting = PROGRAM.keep_setting
kept_language = PROGRAM.kept_language
key_complaint = PROGRAM.key_complaint
key_refused_note = PROGRAM.key_refused_note
key_store_locked = PROGRAM.key_store_locked
key_store_trouble = PROGRAM.key_store_trouble
kind_on_show = PROGRAM.kind_on_show
known_language = PROGRAM.known_language
label_of = PROGRAM.label_of
label_say = PROGRAM.label_say
# Out of the language piece itself. The program binds what it uses of
# that piece one name at a time, and this is not one of them.
language_name = PROGRAM.language.language_name
reads_right_to_left = PROGRAM.language.reads_right_to_left
language_of_system = PROGRAM.language_of_system
languages = PROGRAM.languages
legend_markup = PROGRAM.legend_markup
list_presets = PROGRAM.list_presets
load_api_key = PROGRAM.load_api_key
log_aside = PROGRAM.log_aside
mark_time = PROGRAM.mark_time
log_path = PROGRAM.log_path
longest_stretch = PROGRAM.longest_stretch
loudness_field_build = PROGRAM.loudness_field_build
loudness_last = PROGRAM.loudness_last
main = PROGRAM.main
math = PROGRAM.math
media_seconds = PROGRAM.media_seconds
metrics_sentence = PROGRAM.metrics_sentence
multitrack_state_note = PROGRAM.multitrack_state_note
names_used_twice = PROGRAM.names_used_twice
newer_release = PROGRAM.newer_release
no_place_message = PROGRAM.no_place_message
not_installed_note = PROGRAM.not_installed_note
older_releases = PROGRAM.older_releases
open_in_file_manager = PROGRAM.open_in_file_manager
open_key_store_app = PROGRAM.open_key_store_app
open_page = PROGRAM.open_page
os = PROGRAM.os
parse_time_point = PROGRAM.parse_time_point
parse_timecode = PROGRAM.parse_timecode
path_key = PROGRAM.path_key
pending_prework = PROGRAM.pending_prework
pick_choice = PROGRAM.pick_choice
platform = PROGRAM.platform
preset_fits_mode = PROGRAM.preset_fits_mode
preview_handover = PROGRAM.preview_handover
preview_out_of_date = PROGRAM.preview_out_of_date
prework_standing = PROGRAM.prework_standing
prework_weight = PROGRAM.prework_weight
probe_has = PROGRAM.probe_has
probe_warm = PROGRAM.probe_warm
progress_from_line = PROGRAM.progress_from_line
project_files = PROGRAM.project_files
project_offer = PROGRAM.project_offer
project_opened_note = PROGRAM.project_opened_note
question_note_build = PROGRAM.question_note_build
re = PROGRAM.re
recording_family = PROGRAM.recording_family
recordings_text = PROGRAM.recordings_text
release_text_in = PROGRAM.release_text_in
remembered_forget = PROGRAM.remembered_forget
resolve_installed = PROGRAM.resolve_installed
rules_from_cut_box = PROGRAM.rules_from_cut_box
run_stages = PROGRAM.run_stages
safe_filename = PROGRAM.safe_filename
sample_count = PROGRAM.sample_count
separation_has_voices = PROGRAM.separation_has_voices
separation_sources = PROGRAM.separation_sources
set_update_skipped = PROGRAM.set_update_skipped
settings = PROGRAM.settings
sheet_speaker_names = PROGRAM.sheet_speaker_names
shutil = PROGRAM.shutil
sign_of_life = PROGRAM.sign_of_life
size_in_mb = PROGRAM.size_in_mb
soxr_available = PROGRAM.soxr_available
soxr_note = PROGRAM.soxr_note
space_summary_lines = PROGRAM.space_summary_lines
speaker_label_names = PROGRAM.speaker_label_names
speaker_measure_loop = PROGRAM.speaker_measure_loop
speaker_source_pick = PROGRAM.speaker_source_pick
speaker_split_begin = PROGRAM.speaker_split_begin
speaker_split_wanted = PROGRAM.speaker_split_wanted
speaker_statistics = PROGRAM.speaker_statistics
speakers_all_from_project = PROGRAM.speakers_all_from_project
speakers_all_on_window_axis = PROGRAM.speakers_all_on_window_axis
speakers_for_run = PROGRAM.speakers_for_run
speakers_from_project = PROGRAM.speakers_from_project
speakers_front_pick = PROGRAM.speakers_front_pick
speakers_keep = PROGRAM.speakers_keep
speakers_project_block = PROGRAM.speakers_project_block
speakers_still_wanted = PROGRAM.speakers_still_wanted
speakers_stored = PROGRAM.speakers_stored
speakers_window_all = PROGRAM.speakers_window_all
speech_heading = PROGRAM.speech_heading
speech_words_done = PROGRAM.speech_words_done
split_cells_write = PROGRAM.split_cells_write
split_channels = PROGRAM.split_channels
split_kind = PROGRAM.split_kind
split_line_write = PROGRAM.split_line_write
split_target = PROGRAM.split_target
spoken_language_choices = PROGRAM.spoken_language_choices
start_again = PROGRAM.start_again
store_api_key = PROGRAM.store_api_key
strip_marks = PROGRAM.strip_marks
styles_follow_scheme = PROGRAM.styles_follow_scheme
subprocess = PROGRAM.subprocess
sys = PROGRAM.sys
system_locale = PROGRAM.system_locale
tc_column_write = PROGRAM.tc_column_write
tempfile = PROGRAM.tempfile
threading = PROGRAM.threading
time = PROGRAM.time
timecode_seconds = PROGRAM.timecode_seconds
timecode_string = PROGRAM.timecode_string
timeline_entries = PROGRAM.timeline_entries
track_recordings_of = PROGRAM.track_recordings_of
tracks_awaiting_measure = PROGRAM.tracks_awaiting_measure
tracks_to_split = PROGRAM.tracks_to_split
trouble_log = PROGRAM.trouble_log
unpack_kind = PROGRAM.unpack_kind
update_fetched = PROGRAM.update_fetched
update_promise = PROGRAM.update_promise
updated_from = PROGRAM.updated_from
video_envelope = PROGRAM.video_envelope
video_facts = PROGRAM.video_facts
video_summary = PROGRAM.video_summary
voice_key = PROGRAM.voice_key
voice_key_parts = PROGRAM.voice_key_parts
voice_keys_carry_source = PROGRAM.voice_keys_carry_source
voice_lines_here_not = PROGRAM.voice_lines_here_not
voice_marks_of = PROGRAM.voice_marks_of
voice_name_free = PROGRAM.voice_name_free
voice_names_by_source = PROGRAM.voice_names_by_source
voice_names_clashing = PROGRAM.voice_names_clashing
voice_names_store = PROGRAM.voice_names_store
voice_row_marks = PROGRAM.voice_row_marks
voice_suggest_round = PROGRAM.voice_suggest_round
voices_answer_kept = PROGRAM.voices_answer_kept
voices_under = PROGRAM.voices_under
warn_box = PROGRAM.warn_box
weak_marks_show = PROGRAM.weak_marks_show
why_no_cut = PROGRAM.why_no_cut
wide_bar_of = PROGRAM.wide_bar_of
wide_cameras_of = PROGRAM.wide_cameras_of
wide_marks_applied = PROGRAM.wide_marks_applied
wide_note_build = PROGRAM.wide_note_build
wide_settings_grey = PROGRAM.wide_settings_grey
window_suggestion = PROGRAM.window_suggestion
without_own_camera = PROGRAM.without_own_camera
words_forgotten = PROGRAM.words_forgotten
words_from_handover = PROGRAM.words_from_handover
words_settings_grey = PROGRAM.words_settings_grey


def app_icon(QtGui):
    """The window's picture, or None where there is none to build.

    The picture is a file, and the piece that lays the entry in the
    program list owns it: nothing here builds a path into another
    piece's folder. It is asked at the place of use, as main() asks
    it. None rather than an empty icon where there is no picture --
    the caller only sets what it is given, and an empty icon would
    look to it exactly like a picture.
    """
    try:
        video = QtGui.QPixmap()
        video.loadFromData(beside("desktop", program=PROGRAM).icon_bytes())
        return None if video.isNull() else QtGui.QIcon(video)
    except Exception:
        return None


#-------------------------------------------------------------- Interface

def audio_use_settled(video, chosen, forced, has_sound=True,
                      kind=TYPE_CONTENT):
    """What the audio field of one video file shows, and why.

    Returns (used, why). An empty *why* means there is a choice to
    make. Where there is none the reason is said beside the greyed out
    field -- greyed out without a reason is the dead end this project
    took out of the preset list on 24.8.2026.

    Three things settle it without asking: a file with no audio track
    at all, a file that stays out entirely, and an intro or outro,
    which is placed as it lies and never processed. The fourth is the
    exception that was laid down: one video with sound and no audio
    recording beside it is the only sound there is.
    """
    a = path_key(video)
    if not has_sound:
        return False, T('no audio track in this file')
    if kind == TYPE_IGNORED:
        return False, T('this file stays out entirely')
    if kind in (TYPE_INTRO, TYPE_OUTRO):
        return False, T('a finished clip -- only placed, not processed')
    if a in set(path_key(p) for p in forced):
        return True, T('the only sound there is')
    return a in set(path_key(p) for p in chosen), ""


def choice_cell(values, chosen, why="", quiet="", alive=False):
    """One drop-down for a row of a list, with its reason beside it.

    A drop-down and not a tick: closed it reads "do not use the audio"
    and says its own state, where "as a track" needed a tooltip to say
    what it meant. It also leaves room for a third case later without
    rebuilding anything.

    A *why* stands next to the field, and by default settles it: there
    is nothing to answer, so the field is dead. *alive* keeps it open
    for an answer instead -- a reason that says which camera the cut
    uses explains something without taking the decision away, and a
    dead field would say the opposite.

    Nothing here colours the field itself. Grey is for the one entry a
    reason is about, which choices_shut sets entry by entry; over the
    whole field it makes every answer look barred.

    Returns (cell, box).
    """
    from PySide6 import QtWidgets as _qw
    cell = _qw.QWidget()
    row = _qw.QHBoxLayout(cell)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(6)
    box = _qw.QComboBox()
    fill_choices(box, values, chosen)
    row.addWidget(box)
    if why:
        if not alive:
            box.setEnabled(False)
        note = _qw.QLabel(why)
        note.setStyleSheet("color: %s" % quiet)
        note.setWordWrap(True)
        row.addWidget(note)
    row.addStretch(1)
    return cell, box


def choices_shut(box, shut, why, quiet, noted=None):
    """Grey out the entries of a drop-down that cannot be chosen.

    *shut* are the stored values that are barred, *why* says why. Where
    two entries are barred for different reasons, *shut* is a
    {value: why} instead and each carries its own; one sentence over
    both would explain neither. The entries stay in the list: taking
    them out would leave somebody wondering where the camera went, and
    the answer to "why can I not pick this" has to stand where the
    question is asked.

    *noted* is {value: sentence} for an entry that carries a sentence
    and stays open: which of two marked wide shots the cut takes
    explains something without taking the choice away.

    Every entry is set either way round, not only the barred ones. A
    function that can shut but not open again would leave a camera
    grey for the rest of the session because it was a wide shot for a
    moment.

    The list is Qt's own model, so an entry can be greyed one at a
    time. A box built on another model is left alone rather than
    half done.
    """
    from PySide6 import QtGui as _qg
    from PySide6.QtCore import Qt as _qt
    model = box.model()
    reasons = (dict(shut) if isinstance(shut, dict)
               else dict((value, why) for value in (shut or ())))
    notes = dict(noted or {})
    for i in range(box.count()):
        value = box.itemData(i)
        barred = value in reasons
        try:
            model.item(i).setEnabled(not barred)
        except AttributeError:
            return box
        box.setItemData(i, _qg.QBrush(_qg.QColor(quiet)) if barred else None,
                        _qt.ForegroundRole)
        box.setItemData(i, reasons[value] if barred else notes.get(value, ""),
                        _qt.ToolTipRole)
    return box


def guess_worth_using(guess):
    """A guessed speaker name, or nothing where the guess is no name.

    A guess counts only if it begins with a letter. With Multitrack the
    speaker name becomes the label of that track at auphonic.com, so it
    leaves the program and is read by people who never saw the file it
    was taken from -- "0008A", guessed off a card number, would look
    like a fault there rather than like a person. Thrown out, it leaves
    the field empty and grey-free, and the start button says what is
    missing instead of quietly running under a number.

    This is about what the program may take of its own accord. A name
    somebody typed stands as typed: whoever writes "2nd voice" has
    decided that, and it is not ours to refuse.

    The test is isalpha and not a-z: a name may begin with a letter
    that the English alphabet does not have, and a recording of Ute
    with an umlaut over the U is as much a person as one without.
    """
    return guess if str(guess or "")[:1].isalpha() else ""


class SpeakerName(Value):
    """A name field, answering the name the run works under.

    The field starts empty with what the file name suggests standing in
    it in grey, and a placeholder is not a value. So get() gives the
    typed name and falls back to the guess, and there is nothing a
    reader has to know: the plain reading is the right one everywhere,
    and the two places that want the answer alone -- the widget and the
    project file -- say typed() and pay one word for it.

    The other way round cost three faults in three places, each without
    a word: the file went out unnamed, the camera got no speaker, and
    an episode was cut on one camera because the preselection asked the
    field rather than the name.

    The guess is filtered here rather than by whoever passes it, for
    the same reason. "Guest_0008A.wav" gives a good guess, "0008A.wav"
    would name the track 0008A -- and with Multitrack that name is the
    track's label at auphonic.com, read by people who never saw the
    file, where a card number looks like a fault rather than a person.
    Thrown out, it leaves the field empty and grey-free and the start
    button says what is missing.
    """

    def __init__(self, value="", suggested=""):
        Value.__init__(self, value)
        self.suggested = guess_worth_using(suggested)

    def get(self):
        return str(self._value or "").strip() or str(self.suggested or "")


def camera_tracks_of(camera_lines):
    """Every camera with the name it carries in the cut, in order.

    Guessing reads one file and drops the take number, which is what
    tells the cameras of one rig apart. So where two guesses fall
    together the whole stem stands for both, and what differs is then
    at the end -- the end a long name is kept by. Two files of one
    name stay one name: nothing in them tells the cameras apart.
    """
    files = [p for p, _v, _k, _n in camera_lines or ()]
    guessed = [guess_camera_name(p) for p in files]
    return [(p, os.path.splitext(os.path.basename(p))[0]
             if guessed.count(n) > 1 else n)
            for p, n in zip(files, guessed)]


def camera_tracks_clashing(camera_lines):
    """Names that more than one camera would carry in the cut.

    The cut keys a camera by that name: its colour, its line in the
    legend and which file plays. Two under one name are one camera,
    and only the last of them is ever seen. What reaches here is two
    files of one name, which no guess off a file name can tell apart.
    """
    names = [t for _p, t in camera_tracks_of(camera_lines)]
    return sorted(set(n for n in names if n and names.count(n) > 1))


def missing_conditions(files, production, multitrack, assign_lines,
                       camera_lines, voice_lines=(), voiced=()):
    """Report what is still missing, and where it is missing.

    Returns {key: reason}. Empty means everything is there. The reasons
    are in plain words so they can be written under the start button: a
    greyed out button without a reason is a dead end.

    The keys say which sheet the reason belongs on -- 1 and 11 the file
    tab, 21 the production strip on it, 22 the assignment tab. 1 is the
    empty start and nothing else, so the footer can greet it quietly
    instead of warning about it.
    """
    pending = {}
    if not files:
        pending[1] = T('No files selected yet.')
    if not production.strip():
        pending[21] = T('The production has no name yet.')
    if multitrack:
        used = [r for r in assign_lines if r[2].get() != IGNORE_AUDIO]
        if len(used) < 2:
            pending[22] = (T('Multitrack needs two tracks in the table '
                             'above -- a camera counts as one once its '
                             'Camera audio is set to "use the audio".'))
        elif not all(v.get() for _r, v, _k in used):
            pending[22] = T('One audio recording has no speaker name yet.')
        else:
            names = [v.get() for _r, v, _k in used]
            if len(set(names)) < 2:
                pending[22] = (T('All recordings carry the same name '
                                 '-- that makes a single track.'))
    # A voice whose name is on somebody else. Held here and not asked
    # at the start: to the cut two voices of one name are one person,
    # and there is no answer that makes that right.
    clash = voice_names_clashing(assign_lines, voice_lines, voiced)
    if clash:
        pending[22] = (T('%s is on more than one speaker -- a name is a '
                         'person, and every person needs their own.')
                       % ", ".join(clash))
    # No sound at all: a video file whose Camera audio is not in use
    # contributes none, and a run with nothing to listen to has no first
    # step. Said here rather than in a dialog, like everything else that
    # is missing, and on the tab that carries the field.
    if files and not assign_lines:
        pending[11] = T('No sound to work with -- set a video file\'s '
                        'Camera audio to "use the audio", or add an '
                        'audio recording.')
    # Said before the file names below, so the one with a field to type
    # in wins where both are wrong at once.
    same_name = camera_tracks_clashing(camera_lines)
    if same_name:
        pending[22] = (T('Two cameras are one camera in the cut: %s. Their '
                         'files carry the same name, so rename one of '
                         'them.') % ", ".join(same_name))
    outputs = [v.get().strip() for _p, v, _k, _n in camera_lines]
    duplicate = sorted(set(n for n in outputs if n and outputs.count(n) > 1))
    if duplicate:
        pending[22] = (T('Two cameras would produce the same file: %s')
                     % ", ".join(duplicate))
    return pending


def chain_fill_in(group, row, discarded, selected,
                  item, lines_node, channel_rows_show):
    """Show a multi-part recording as one entry with its blocks below.

    Displayed like a single file -- format, length, timecode -- because
    that is what it is for everything downstream. The blocks sit below so
    its composition is visible.

    The last three are the window's: the function that makes a row, the
    map from a file to the row a finding about it belongs on, and the
    channel rows under a recording. Out here rather than inside the
    window because nothing in it needs anything else of gui().
    """
    lengths = [sample_count(p) for p in row]
    tcs = [file_timecode(p) for p in row]
    if all(t is not None for t in tcs):
        total = max(t + n / float(SR)
                     for t, n in zip(tcs, lengths)) - min(tcs)
    else:
        total = sum(lengths) / float(SR)
    node = item(group,
                    TN(len(row) - 1, '%s  + %s continuation',
                       '%s  + %s continuations')
                    % (os.path.basename(row[0]), group_text(len(row) - 1)),
                    os.path.dirname(row[0]), "audio", files_for_it=row)
    # The continuations point at this row too: a finding about block 3
    # belongs to the recording, not to nowhere.
    for part in row:
        lines_node[part] = node
    channel_rows_show(node, row[0])
    try:
        lines = audio_summary(row[0])
    except Exception as e:
        lines = [(T('Error'), str(e)[:120])]
    for k, value in lines:
        # Length and timecode apply to the whole recording, not to the
        # first block -- the format is the same for all of them.
        if k == T('Length'):
            value = (T('%s  (%s)  --  %s  --  %s blocks')
                 % (as_hms(total), as_data_size(sum(size_in_mb(x) for x in row)),
                    T('Timecode from %s')
                    % timecode_string(min(t for t in tcs if t is not None))
                    if any(t is not None for t in tcs)
                    else T('no timecode'), group_text(len(row))))
        item(node, "      " + k, value)
    for i, (p, n, t) in enumerate(zip(row, lengths, tcs), 1):
        source_text = (T('selected') if os.path.abspath(p) in selected
                 else T('found automatically'))
        # The row stands for this block alone, so Remove takes out
        # this block and not the whole recording.
        item(node, "      %d. %s" % (i, os.path.basename(p)),
               "%s, %s%s, %s"
               % (as_data_size(size_in_mb(p)), as_hms(n / float(SR)),
                  ", %s" % timecode_string(t) if t is not None else "",
                  source_text), "block", files_for_it=[p])
    for nm, reason in discarded:
        item(node, "      %s" % nm, T('does not belong: %s') % reason)
    node.setExpanded(False)
    return node


def wide_shot_barred(path, value, placeless):
    """Why this file cannot be the wide shot, or "" where it can be one.

    The wide shot is what the cut falls back on, so it has to lie on
    the time axis. *placeless* are the paths the measurement placed
    nowhere; empty or None bars nothing. A Kind somebody picked is
    barred as well: this states a fact about the material rather than
    suggesting one -- a file nothing places can only be a jingle.
    """
    if not placeless:
        return ""
    if path_key(path) not in set(path_key(p) for p in placeless):
        return ""
    return T('It fits nowhere in the material: no timecode, and its '
             'sound has nothing in common with the rest. The wide shot '
             'is what the cut falls back on, so it has to lie on the '
             'time axis.')


def edge_kind_barred(path, kinds):
    """Which of intro and outro this file cannot be, and why.

    An episode has one intro and one outro, and each travels to the run
    as a single switch. So while one file holds either mark, that entry
    is shut on every other file, rather than the second choice taking
    the mark off the first and leaving that file on a "Content" it may
    not be able to carry. *kinds* is {path: Value}, and a path missing
    from it counts as content.
    """
    here = path_key(path)
    barred = {}
    for kind in (TYPE_INTRO, TYPE_OUTRO):
        holder = next((p for p, value in (kinds or {}).items()
                       if path_key(p) != here and value.get() == kind), None)
        if holder:
            barred[kind] = T('%s is already set as %s, and an episode has '
                             'one of those. Answer differently here, or '
                             'take the mark off that file first.') \
                % (os.path.basename(holder), label_of(kind))
    return barred


def clip_kind_cell(short, kind, why="", quiet="", derived=False, no_wide="",
                   no_edge=None):
    """The Kind field of one video file: what this file is.

    It stands with the material and not in the assignment table:
    "ignore this video" is literally the question the file tab answers,
    and an intro is placed as it lies rather than assigned to anybody.

    Nothing stands beside the field: a reason goes on the entry it is
    about, never next to the answer. The rule that grey is never
    without a reason holds everywhere else.

    With *derived* the value on show is not the stored one -- it is
    what the program worked out. That is the wide shot nobody marked.
    Then *why* bars the one entry it is about and says itself there:
    a camera nobody sits in front of cannot be content while that is
    so. Only that entry is greyed and the field stands in black: grey
    over the whole box reads as "nothing to be done here", which is
    the opposite of what it is. *no_wide* bars the wide shot the same
    way, with its own sentence, and *no_edge* the marks somebody gave.

    Without *derived* a *why* explains rather than refuses -- which of
    several marked wide shots the cut takes -- and it stands on the
    wide shot entry without greying it.
    """
    cell, box = choice_cell(CLIP_TYPES, kind, "", quiet, alive=True)
    barred, noted = {}, {}
    if derived:
        barred[TYPE_CONTENT] = why
    elif why:
        noted[TYPE_WIDE] = why
    if no_wide:
        barred[TYPE_WIDE] = no_wide
        # Nor content: content is cut into the episode, and this file
        # has no place to be cut into -- as content it becomes the wide
        # shot by derivation. Intro, outro and "leave out" stay open.
        barred.setdefault(TYPE_CONTENT, T(
            'It fits nowhere in the material, so it cannot be cut into '
            'the episode. It can be set in front of it or after it.'))
    for value, sentence in (no_edge or {}).items():
        barred.setdefault(value, sentence)
    choices_shut(box, barred, why, quiet, noted)
    speaks_as(box, T('Kind'), short)
    hint(box, T('Content: a camera like any other.\nWide shot: a '
                'camera nobody sits in front of -- it takes no '
                'speaker, and the cut goes to it in a pause and in a '
                'long monologue.\nIntro and outro '
                'are finished clips -- not aligned, not processed, '
                'only placed in the Timeline.\nIgnore video: the file '
                'stays out entirely.'))
    return cell, box


def camera_audio_cell(short, used, why, quiet, beside_player=False):
    """The Camera audio field of one video file, built and named.

    Two places show it: the file list, where it is said which files
    play a part at all, and the camera table beside the player, where
    it can be heard whether that sound is usable. The wording differs,
    the field and the value behind it do not.

    Nothing stands behind the field, for the reason given at the Kind
    field above: this table is to show the answer and nothing else.
    Where the field is settled it is closed, and *why* says so from
    the field itself rather than from a sentence beside it.
    """
    cell, box = choice_cell(AUDIO_USE,
                            AUDIO_MATERIAL if used else AUDIO_UNUSED,
                            "", quiet)
    if why:
        box.setEnabled(False)
    speaks_as(box, T('Camera audio'), short)
    hint(box, T('Used, the sound of this file becomes a track like any '
                'other -- it appears in the table above.\nThe same field '
                'stands in the file list; both show the one answer.')
         if beside_player else
         T('Used, the channels measured under this file are cut into '
           'tracks, the way a recording is.\nMeasuring happens either '
           'way: that verdict is what this is decided on, and '
           'synchronising takes the sound regardless.'))
    return cell, box


def cameras_using_audio(files, kinds, uses, sound_of=None):
    """Which video files contribute their sound, and which by rule.

    Derived in one place for both tabs: two derivations of one answer
    drift apart, and then one tab offers a choice the other refuses.
    Only cameras are asked -- an intro is placed as it lies and never
    listened to. A wide shot is a camera: the room microphone often
    hangs on it, and that is the mix.

    *kinds* and *uses* are {path: Value}; a path missing from either
    counts as content and as not in use.
    """
    videos = [p for p, a in files if a == "video"]
    content = [p for p in videos
               if (kinds[p].get() if p in kinds else TYPE_CONTENT)
               in CAMERA_TYPES]
    return cameras_with_own_audio(
        content, [p for p, a in files if a == "audio"],
        [p for p in content if p in uses and uses[p].get()], sound_of)


def audio_use_bind(box, value, why=""):
    """Tie one drop-down to the audio decision of one video file.

    The same value stands in two places: in the file list, where it is
    said which files play a part, and beside the player on the
    assignment tab, where it can be *heard* whether that sound is
    usable at all -- and heard is the only way to tell. One value, two
    windows onto it; change either and the other follows at once.

    A settled field is inert: it is neither read back nor listened to,
    so the derivation cannot be turned into a stored answer by the act
    of showing it.
    """
    if why:
        return box
    box.currentIndexChanged.connect(
        lambda i: value.set(box.itemData(i) == AUDIO_MATERIAL))
    value.listen(lambda: pick_choice(
        box, AUDIO_MATERIAL if value.get() else AUDIO_UNUSED))
    return box


def kinds_said_again(state, rows):
    """Draw the Kind fields of both tables again.

    Only the assignment tab knows how to say its own; before it stands,
    the file list is all there is.
    """
    if state.get("kinds_refresh"):
        state["kinds_refresh"]()
    else:
        video_kinds_again(rows)


def kind_cell_for(path, value, wides, said, placeless, kinds, quiet,
                  after=None):
    """The Kind field of one video file, built and tied to its value.

    Three tables show a Kind, and all three ask here: what is derived,
    what is barred and what the field answers into are decided once.
    Two derivations of one answer drift apart, and then one table
    offers what another refuses. *kinds* says what every video file is,
    which tells whether intro and outro are free. Returns (cell, box).
    """
    short = os.path.basename(path)
    shown, why, derived = kind_on_show(value.get(), short, wides, said)
    cell, box = clip_kind_cell(short, shown, why, quiet, derived,
                               wide_shot_barred(path, value, placeless),
                               edge_kind_barred(path, kinds))
    clip_kind_bind(box, value, after=after)
    return cell, box


def clip_kind_bind(box, value, after=None):
    """Tie one Kind drop-down to what its video file is.

    The same pattern as audio_use_bind, and for the same reason: that a
    clip is in truth an outro is noticed while watching it, and the
    player stands on the assignment tab. So the field is offered there
    as well as in the file list. Not a doubling -- two values that can
    drift apart would be one; one value seen from two places is not.

    *after* is what has to happen once the answer has changed -- the
    tables that read the Kind have to be built again.
    """
    def chosen(i):
        picked = box.itemData(i)
        if picked == value.get():
            return
        value.set(picked)
        if after is not None:
            after()

    def by_hand(i):
        """The same, and it was a person who did it.

        activated fires for a person and never for the program, so the
        note lives here and nowhere else. It is kept on the value,
        which outlives every widget: the tables are thrown away and
        built again on each change, and a note that went with them
        would let a proposal write over an answer on the next redraw.
        """
        value.chosen_by_hand = True
        chosen(i)

    box.currentIndexChanged.connect(chosen)
    # And the same on activated, which is the signal for "somebody
    # picked this", changed or not. It is the only one that fires where
    # the box shows a derived wide shot: the entry is already the
    # current one, so no index changes, and choosing it is exactly how
    # a derivation is turned into an answer.
    box.activated.connect(by_hand)
    value.listen(lambda: pick_choice(box, value.get()))
    return box


def kind_proposal_apply(values, unplaceable, brief=()):
    """Propose a Kind for every file with no place.

    A proposal like the ones for the voices, and under the same rule:
    it fills only what still carries the program's own answer, and
    never touches a Kind somebody picked. Whether somebody picked is
    not read off the text -- setting a file back to content by hand is
    an answer too -- but off chosen_by_hand, which clip_kind_bind sets
    from the one Qt signal that fires for a person and not for the
    program.

    *unplaceable* are the files nothing could place; None means no
    measurement happened, and then nothing changes in either
    direction. A file that can be placed again gets its old Kind back,
    but only where the proposal is what stands there -- a measurement
    that did not run must not quietly put a file back into the run.

    *brief* are files that fit nothing and are far shorter than the
    rest, shortest first, and the shortest is proposed as the intro.

    Returns the paths whose Kind changed.
    """
    if unplaceable is None:
        return []
    lost = set(os.path.abspath(p) for p in unplaceable)
    short = [os.path.abspath(p) for p in (brief or ())]
    elsewhere = any(v.get() == TYPE_INTRO
                    and getattr(v, "kind_said", None) != TYPE_INTRO
                    for v in values.values())
    # A jingle has no place because it is not a camera, and it is meant
    # to be used rather than left out -- set at the front instead of
    # measured. One file only: an intro exists once, and none at all
    # where one already stands elsewhere.
    intro = short[0] if short and not elsewhere else None
    moved = []
    for path, value in list(values.items()):
        if getattr(value, "born_as", None) is None:
            value.born_as = value.get()
        if getattr(value, "chosen_by_hand", False):
            continue
        now, was = value.get(), value.born_as
        said = getattr(value, "kind_said", None)
        here = os.path.abspath(path)
        want = TYPE_INTRO if here == intro else TYPE_IGNORED
        if here in lost or here == intro:
            if now == want or now != (said or was):
                continue
            value.kind_said = want
            value.set(want)
            moved.append(path)
        elif said and now == said:
            value.kind_said = None
            value.set(was or TYPE_CONTENT)
            moved.append(path)
    return moved


def kinds_off_the_axis(values, no_place):
    """Move every file with no place off content and the wide shot.

    Not a proposal but a fact: a file with no timecode whose sound has
    nothing in common with the rest cannot be cut into the episode,
    however that answer got there. Intro is where it lands, and only
    while the intro is free -- an episode has one. Where it is taken
    the file is left out instead; outro stays one click away.
    """
    lost = set(path_key(p) for p in (no_place or ()))
    moved = []
    for path, value in list(values.items()):
        if path_key(path) not in lost or value.get() not in CAMERA_TYPES:
            continue
        taken = any(other.get() == TYPE_INTRO
                    for p, other in values.items()
                    if path_key(p) != path_key(path))
        value.set(TYPE_IGNORED if taken else TYPE_INTRO)
        moved.append(path)
    return moved


def kind_proposal_say(values, data):
    """Apply the proposal from a finished measurement and say what moved.

    Outside gui() because it decides nothing and touches no widget: the
    measurement carries the files with no place and the short ones
    among them, and each Kind that came out of it has its own sentence.
    """
    moved = kind_proposal_apply(values, (data or {}).get("unplaceable"),
                                (data or {}).get("brief"))
    # The proposal first, the fact after it: the proposal steps back
    # from an answer somebody gave, and what it leaves behind on content
    # or the wide shot is exactly what cannot be true.
    forced = kinds_off_the_axis(values, (data or {}).get("no_place"))
    for path in forced:
        print(T('%s fits nothing in the material, so it cannot be cut '
                'into the episode: set to Intro.') % os.path.basename(path)
              if values[path].get() == TYPE_INTRO else
              T('%s fits nothing in the material either, and the intro is '
                'taken: left out.') % os.path.basename(path))
    for path in moved:
        name, kind = os.path.basename(path), values[path].get()
        if kind == TYPE_INTRO:
            print(T('%s fits nothing in the material and is far shorter '
                    'than the rest: proposed as the intro, which is put '
                    'at the front and never measured.') % name)
        elif kind == TYPE_IGNORED:
            print(no_place_message(name))
        else:
            print(T('%s can be placed again and is back in the run.') % name)
    return moved + [p for p in forced if p not in moved]


# How many tabs the window can hold: files, assignment, cut, output.
# Three of them arrive with the material, so a menu or a key built at
# the start would name one. Too small a number here leaves the last
# tab's key dead until somebody has opened the menu once.
TABS_AT_MOST = 4


def window_ready(state):
    """Whether the time window can be set: the files share an axis.

    So as soon as any file carries a timecode, or as soon as the
    positions have been measured. Before that a boundary would not know
    what it refers to.
    """
    return bool(state["tc_there"] or state["axis"])


def menus_follow(late):
    """Grey each file entry with the button that does the same thing.

    Entry and button are left behind in *late* as a pair, and the
    button is the one source: it is greyed in places that ask nothing
    here -- a run, a selection -- and an entry with a state of its own
    drifts apart from it. Save and Close have no button anywhere in
    the window and follow whether a project stands at all.
    """
    for entry, button in late.get("menu_follows") or ():
        entry.setEnabled(button.isEnabled())
    here = late.get("project_here")
    for entry in late.get("menu_project") or ():
        entry.setEnabled(bool(here and here()))


#------------------------------------------------------------- The menus
# A piece of its own, in the folder "menus" beside the way in and not
# beside this file: beside() lays its path against the folder the
# program starts in, whoever calls it. Read where its block stood.

menus = beside("menus", program=PROGRAM)

# What the rest of the window calls out of it, bound by name: a name
# read here and bound nowhere here is a loose end. Three of the four
# are read on this side by no code and stand here all the same -- one
# test asks the program for player_loaded, and dir() keeps the rest.
build_menus = menus.build_menus
player_loaded = menus.player_loaded
player_of_tab = menus.player_of_tab
transport = menus.transport


#--------------------------------------------------------- The title bar
# What stands in the title bar of the window, and nothing else.
# It is read from three places in gui() and from no piece beside
# this one, so it stays here rather than travelling.


def window_title(project=""):
    """What stands in the title bar, with the open project named in it.

    A window with a project open and one without looked exactly alike,
    and after a few productions in a row there was no telling which one
    this was.

    The name goes in front, which is what a document window does
    everywhere else: Word writes "Report.docx - Word", and on a Mac the
    document names the window. It takes the place of the tag line,
    which nobody needs once the work has begun.
    """
    said = T('Video Podcast Magic %s -- raw material becomes an edited '
             'podcast') % VERSION
    if not project:
        return said
    return "%s -- %s" % (os.path.basename(project), said.split(" -- ")[0])


#------------------------------------------------------------ The tables
# A piece of its own, in the folder "tables" beside the way in and
# not beside this file: beside() lays its path against the folder
# the program starts in, whoever calls it. Read where its block stood.

tables = beside("tables", program=PROGRAM)

# What the window and the pieces beside it still call out of this
# one, bound by name: a name read here and bound nowhere here is a
# loose end. widget_width is read by no code on this side and stands
# here all the same -- the fittings ask the program for it.
file_span = tables.file_span
fix_table_width = tables.fix_table_width
folded_summary = tables.folded_summary
from_the_front = tables.from_the_front
row_picker_for = tables.row_picker_for
row_picker_watch = tables.row_picker_watch
table_build = tables.table_build
table_rows_fit = tables.table_rows_fit
tree_build = tables.tree_build
tree_cell = tables.tree_cell
tree_field = tables.tree_field
tree_row = tables.tree_row
tree_row_of = tables.tree_row_of
tree_rows_fit = tables.tree_rows_fit
widget_width = tables.widget_width


#------------------------------------------------------------ The player
# A piece of its own, in the folder "player" beside the way in and not
# beside this file: beside() lays its path against the folder the
# program starts in, whoever calls it. Read where its block stood.

player = beside("player", program=PROGRAM)

# What the rest of the window calls out of it, bound by name: a name
# read here and bound nowhere here is a loose end. NAME_HOLD_S is read
# by no code on this side and stands here all the same -- take_from()
# carries it to the program, and a test asks the program for it.
NAME_HOLD_S = player.NAME_HOLD_S
box_room = player.box_room
caption_room = player.caption_room
cut_caption_room = player.cut_caption_room
cut_choice_room = player.cut_choice_room
digits_font = player.digits_font
make_drop_area = player.make_drop_area
make_log_view = player.make_log_view
make_player_widgets = player.make_player_widgets
qt_cut_band = player.qt_cut_band
qt_cut_player = player.qt_cut_player


#------------------------------------------------------------ The orders
# A piece of its own, in the folder "orders" beside the way in and
# not beside this file: beside() lays its path against the folder
# the program starts in, whoever calls it. Read where its block stood.

orders = beside("orders", program=PROGRAM)

# What the rest of the window calls out of it, bound by name: a name
# read here and bound nowhere here is a loose end. voices_of_values
# is read by no code on this side and stands here all the same --
# take_from() carries it to the program, and dir() may lose nothing.
run_argv = orders.run_argv
slider_argv = orders.slider_argv
slider_numbers = orders.slider_numbers
speakers_to_cameras = orders.speakers_to_cameras
voices_of_values = orders.voices_of_values


#---------------------------------------- The settings sheet and the log
# The Settings window: the language box, the boxes for the key and
# for Resolve assembled into it, and the row the macOS keychain
# needs. The way to the log of a run stands at the end of it.


def language_box_build():
    """The box that says which language the window speaks.

    A box of its own, because it is the one setting here about the
    program itself while the two beside it are each about a service
    outside it. Made here rather than taken in: nothing on any sheet
    shows it, so there is nothing to borrow.
    """
    from PySide6 import QtWidgets as _qw
    box = _qw.QGroupBox(T('Language of the window'))
    rows = _qw.QVBoxLayout(box)
    # Above the field and not below it. Somebody who reads it after
    # choosing has already chosen, and is waiting for a window that
    # is not going to change.
    note = label(T('A language chosen here is spoken from the next '
                   'start.'), COLOURS["quiet"])
    # Wrapped, because the German sentence is the longer one and the
    # note beside this box is measured 89 px too wide for want of it.
    note.setWordWrap(True)
    rows.addWidget(note)
    chooser = _qw.QComboBox()
    speaks_as(chooser, T('Language of the window'))
    # The first entry names the language it will really bring, which
    # is what this program has texts for: an Italian system reads
    # English here rather than a promise nobody can keep.
    chooser.addItem(T('System language (%s)')
                    % language_name(known_language(system_locale())), "")
    for code, name in sorted(((c, language_name(c)) for c in languages()),
                             key=lambda pair: pair[1].lower()):
        chooser.addItem(name, code)
    # An empty setting is the first entry's own value, so a kept
    # language nobody has ever chosen lands there by itself.
    stands_at = chooser.findData(kept_language())
    chooser.setCurrentIndex(stands_at if stands_at >= 0 else 0)
    # Connected after the index is set: before it, opening the window
    # would write down a choice nobody made.
    chooser.currentIndexChanged.connect(
        lambda *_: keep_setting("language", chooser.currentData() or ""))
    field_row = _qw.QHBoxLayout()
    rows.addLayout(field_row)
    field_row.addWidget(chooser)
    field_row.addStretch(1)
    return box


def settings_dialog_build(parent, access_box, resolve_box, keep_where):
    """Assemble the Settings window out of the boxes that go in it.

    Out here for the reason cut_fields_build gives: this is widget
    assembly and nothing else, and the window is long enough. Two of
    the boxes are built where they are used on the page and move in
    here on the first click -- which is why this is a builder taking
    them in rather than a builder making them.
    """
    from PySide6 import QtWidgets as _qw
    d = _qw.QDialog(parent)
    d.setWindowTitle(T('Settings'))
    d.setMinimumWidth(620)
    rows = _qw.QVBoxLayout(d)
    # First, and the two that follow keep their note under them: it
    # says "Both", and a third box between them would take that word
    # away from the two it is about.
    rows.addWidget(language_box_build())
    rows.addWidget(access_box)
    rows.addWidget(resolve_box)
    rows.addWidget(label(
        T('Access and connection are asked once and then stay. The '
          'key goes into the %s, never into a file.') % keep_where, COLOURS["quiet"]))
    close_row = _qw.QHBoxLayout()
    rows.addLayout(close_row)
    close_row.addStretch(1)
    shut = _qw.QPushButton(T('Close'))
    shut.clicked.connect(d.accept)
    close_row.addWidget(shut)
    return d


def make_key_note(QtWidgets, label, hint, settings_open):
    """The line that says what is wrong with the key for auphonic.com.

    It is built twice, because the key is looked at from two places:
    the field and its button live in the settings window, the preset
    they unlock on the sheet. A note in only one of them is invisible
    from the other -- and the settings window stands over the sheet
    while somebody presses Connect.

    Returns the label for the settings window, the row for the sheet,
    and the two calls that show and hide the lot. Whatever is needed
    from gui() comes in as an argument, as with the player.
    """
    settings_note = label("", COLOURS["warning"])
    settings_note.setWordWrap(True)
    settings_note.setVisible(False)
    settings_note.setObjectName("key_note_settings")
    settings_note.setAccessibleName(T('What auphonic.com replied'))

    key_row = QtWidgets.QHBoxLayout()
    key_note = label("", COLOURS["quiet"])
    key_note.setWordWrap(True)
    key_note.setVisible(False)
    key_note.setObjectName("key_note")
    key_note.setAccessibleName(T('What auphonic.com replied'))
    key_row.addWidget(key_note, 1)
    # A button and not a link inside the line: measured on this
    # machine, a link in a label is announced as plain text and fires
    # on no key at all, while a button carries its own name and answers
    # the space bar. A pointer nobody can press is worse than none.
    settings_way = QtWidgets.QPushButton(T('Settings ...'))
    settings_way.setFlat(True)
    settings_way.setVisible(False)
    settings_way.setObjectName("key_note_way")
    settings_way.clicked.connect(lambda: settings_open())
    key_row.addWidget(hint(settings_way,
                           T('Open the settings, where the key is.')))

    def show(text):
        """Say what is wrong with the key, in both places it is read.

        Never in a box. A box has to be clicked away before the field
        it is about can be reached, and it says nothing the ungreen
        button and this line do not already say.
        """
        for note in (key_note, settings_note):
            note.setText(text)
            note.setStyleSheet("color: %s;" % COLOURS["warning"])
            note.setVisible(True)
        settings_way.setVisible(True)

    def hide():
        """Take the note back; nothing is wrong until something is."""
        key_note.setVisible(False)
        settings_note.setVisible(False)
        settings_way.setVisible(False)

    return settings_note, key_row, show, hide


def tick_off_quietly(box, value):
    """Take a tick back without the box answering its own toggle.

    The answer to that toggle throws the key away, so a save that did
    not work would take the key that was already there with it.
    """
    box.blockSignals(True)
    value.set(False)
    box.blockSignals(False)


def keychain_row_add(into, keep_button):
    """Put in the line that shows while the macOS keychain is locked.

    It greys the box that saves the key, says why, and offers the way
    to unlock. A timer asks again while the window stands, so the box
    wakes up by itself -- that waking is the only sign the unlock took.

    Returns the call that reads the state once.
    """
    from PySide6 import QtCore as _qc, QtWidgets as _qw
    row = _qw.QWidget()
    row.setObjectName("keychain_row")
    line = _qw.QHBoxLayout(row)
    line.setContentsMargins(0, 0, 0, 0)
    note = label(T('The keychain is locked. Unlock it and this button '
                   'wakes up.'), COLOURS["warning"])
    note.setWordWrap(True)
    note.setObjectName("keychain_locked")
    line.addWidget(note, 1)
    way = _qw.QPushButton(T('Open Keychain Access'))
    way.setObjectName("keychain_way")
    way.clicked.connect(lambda *_: open_key_store_app())
    line.addWidget(hint(way, T('Opens the app that unlocks the keychain.')))
    into.addWidget(row)

    def look():
        """Grey the save box while the store is shut, and wake it up."""
        shut = key_store_locked() is True
        row.setVisible(shut)
        keep_button.setEnabled(not shut)

    look()
    watch = _qc.QTimer(row)
    watch.timeout.connect(look)
    # Half a second: often enough that unlocking feels answered, and a
    # question that reads a bit out of a library is cheap enough to
    # repeat -- it starts no process and puts nothing on the screen.
    watch.start(500)
    return look


def log_open():
    """Hand the log of this run to whatever opens a text file here.

    The same way an address is opened, because it is the same
    mechanism: the Windows shell, open on a Mac, xdg-open elsewhere.
    Nothing is waited for -- the window carries on while the editor
    comes up, which on a cold start takes seconds.
    """
    where = log_path()
    if not where or not os.path.isfile(where):
        return False
    return open_page(where)


def log_entry(act, where, window):
    """Put the way to the log into the menu, alive while there is one.

    The console used to name the log file at every start and does not
    any more -- nothing is said in front of the window -- so this is
    where somebody finds it. Greyed and not hidden where there is
    nothing to open: an entry that is missing teaches nobody that
    there is a log at all, and the reason stands on the entry.
    """
    entry = act(where, T('Show the log of this run'), log_open)

    def alive():
        file_path = log_path()
        there = bool(file_path) and os.path.isfile(file_path)
        entry.setEnabled(there)
        entry.setToolTip(file_path if there
                         else T('Nothing has been written yet.'))

    alive()
    where.aboutToShow.connect(alive)
    return entry


#---------------------------------------------------------- The fittings
# A piece of its own, in the folder "fittings" beside the way in and
# not beside this file: beside() lays its path against the folder the
# program starts in, whoever calls it. Read where its block stood.

fittings = beside("fittings", program=PROGRAM)

# What the window and the pieces beside it still call out of this
# one, bound by name: a name read here and bound nowhere here is a
# loose end. cells_laid_out is read by no code on this side and
# stands here all the same -- the speakers piece asks the program.
NAME_COLUMN_LEAST = fittings.NAME_COLUMN_LEAST
_list_accepts = fittings._list_accepts
cells_laid_out = fittings.cells_laid_out
checkbox_bind = fittings.checkbox_bind
cut_fields_build = fittings.cut_fields_build
field_bind = fittings.field_bind
hint = fittings.hint
label = fittings.label
mac_menu_name = fittings.mac_menu_name
mark_red = fittings.mark_red
measuring_stop = fittings.measuring_stop
more_speakers_row = fittings.more_speakers_row
qt_own_words = fittings.qt_own_words
say_dialog = fittings.say_dialog
speaker_name_cell = fittings.speaker_name_cell
speaks_as = fittings.speaks_as
split_cell_build = fittings.split_cell_build
split_column_fit = fittings.split_column_fit
total_hide = fittings.total_hide
total_paint = fittings.total_paint
voice_row_cells = fittings.voice_row_cells
zoom_button = fittings.zoom_button


#-------------------------------------------- What the window works with
# Everything gui() calls that is not a fitting and not a piece of
# its own: the prework, the rows of the assignment sheet, the
# buttons that break a run off, and the run loop itself.


def prepared_tracks_in(folder):
    """The finished tracks lying in that folder: name -> file.

    They carry their timecode as a BWF marker and are at -16 LUFS, so
    for the preview they are the better source: a raw recording sits
    16 to 36 dB below. Only the fully assembled ones count --
    "final_<name>_<tc>.wav"; Auphonic's raw return is "<name>.wav",
    neither trimmed nor on the axis.
    """
    out = {}
    if not folder or not os.path.isdir(folder):
        return out
    try:
        names = sorted(os.listdir(folder))
    except OSError:
        return out
    for name in names:
        stem, suffix = os.path.splitext(name)
        if (suffix.lower() not in AUDIO_SUFFIXES
                or not stem.startswith("final_")):
            continue
        parts = stem[len("final_"):].rsplit("_", 1)
        if len(parts) == 2 and parts[0]:
            out[parts[0]] = os.path.join(folder, name)
    return out


def prework_api_key(file_path):
    s = os.stat(file_path)
    return (path_key(file_path), int(s.st_mtime), s.st_size)


def prework_share_key(file_path, task):
    """What one piece of prework on one file is counted under."""
    return (path_key(file_path), task)

def prework_fetch(file_path, target, report):
    """Extract one file while reporting progress.

    With -progress ffmpeg keeps writing how far it is. Without it the
    display would sit on the same text for minutes.
    """
    try:
        duration = video_facts(file_path)["duration"]
    except Exception:
        duration = 0.0
    # The depth of the source, like every other unpacking. This one
    # matters most of the three: it runs from the window while names
    # are still being typed, and what it leaves behind is handed to the
    # run as audio_done and used as it lies -- so a 16 bit copy made
    # here was what the whole run worked from, however deep the camera
    # recorded.
    cmd = ["ffmpeg", "-v", "error", "-nostats", "-progress", "pipe:1",
           "-i", file_path, "-map", "0:a:0", "-ac", "1", "-ar", str(SR),
           "-c:a", unpack_kind(file_path), "-y", target]
    # Errors into a file, not into a pipe: progress is read from stdout
    # until it ends, and an unread stderr pipe would fill up and stop
    # ffmpeg in the middle -- here in a thread that then never returns.
    fd, log = tempfile.mkstemp(prefix="vpm_pre_", suffix=".txt")
    os.close(fd)
    try:
        with open(log, "wb") as fh:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                    stderr=fh)
            for line in proc.stdout:
                share = progress_from_line(line, duration)
                if share is not None:
                    report(share)
            proc.wait()
        if proc.returncode:
            with open(log, "r", encoding="utf-8", errors="replace") as fh:
                raise RuntimeError(fh.read()[-300:])
    finally:
        try:
            os.unlink(log)
        except OSError:
            pass

def camera_offset(cameras, origin=None, fps=30.0):
    """Return how far each camera is shifted against programme time.

    Two data shapes lead here and they say it differently.

    The handover file of a run carries an ``offset`` per camera: the
    place the run found, in seconds, negative where the camera started
    before In point. The cut timeline in Resolve uses exactly that, and
    so does the player here -- position in the file is programme time
    minus offset. Which of the three ways found it was settled when the
    file was written; deciding it over again here is how the player and
    Resolve came apart.

    The preview built from the speaker statistics has no ``offset`` but a
    ``start_s`` per camera, the wall clock time of its start. The origin is
    then the wall clock time programme time begins at; without that, the
    earliest camera.
    """
    out = {}
    # The file that is actually played. It carries the camera's own
    # timecode and that camera's untouched picture, so "timecode minus
    # zero" says where it sits. A stored offset that disagrees is heard
    # as the sound running against the wrong picture -- and only away
    # from the reference camera, where nobody looks first.
    rate = max(1.0, float(fps or 30.0))
    if any(x.get("offset") is not None for x in cameras):
        for x in cameras:
            out[x["track"]] = float(x.get("offset") or 0.0)
        return out
    begin = (float(origin) if origin is not None else
              min((float(x.get("start_s") or 0.0) for x in cameras),
                  default=0.0))
    for x in cameras:
        out[x["track"]] = float(x.get("start_s") or 0.0) - begin
    return out

def reason_set(env_curve, button, on, reason, what_for):
    button.setEnabled(on)
    env_curve.setToolTip(what_for if on else reason)

class Question(object):
    def __init__(self, possible, title):
        self.possible, self.title = possible, title
        self.event = threading.Event()
        self.choice = "abort"



def channel_rows_fit(items, Qt, QtCore, QtWidgets):
    """Give every channel row the height its reason needs.

    The reason stands in the column that takes whatever the others
    leave, so how many lines it runs to is known only once the window
    has a width. Without this the wrapped line is drawn outside its
    row and the sentence is lost after all.
    """
    room = items.columnWidth(2)

    def fit(kid):
        beside = items.itemWidget(kid, 2)
        said = beside.findChild(QtWidgets.QLabel) if beside else None
        if said is None:
            return
        box = beside.findChild(QtWidgets.QCheckBox)
        # The width it has, and only before the first layout the width
        # it is about to get. Working from the column both times drifts
        # by a few pixels every round and the rows creep taller.
        left = said.width() or (
            room - (box.sizeHint().width() if box else 0) - 8)
        tall = said.fontMetrics().boundingRect(
            QtCore.QRect(0, 0, max(60, left), 0), Qt.TextWordWrap,
            said.text()).height()
        want = max(box.sizeHint().height() if box else 0, tall) + 4
        if kid.sizeHint(2).height() != want:
            kid.setSizeHint(2, QtCore.QSize(0, want))

    def walk(node):
        for i in range(node.childCount()):
            kid = node.child(i)
            if kid.data(0, Qt.UserRole + 2) == "channel":
                fit(kid)
            walk(kid)

    walk(items.invisibleRootItem())


def join_barred(path, targets, blocks=None):
    """Which recordings this one cannot be put into, and why.

    The window asks what the search asks, through the same
    _joins_seamlessly: timecodes that overlap, or that lie too far
    apart to be one recording, say these are two. By hand the
    difference goes into the joined file as silence, and no later step
    takes it out. Only where both sides carry a timecode -- without one
    there is nothing to check, and that is what this chooser is for.
    """
    blocks = blocks or {}
    mine = blocks.get(path) or [path]
    shut = {}
    for h in targets:
        yours = blocks.get(h) or [h]
        try:
            here, there = file_timecode(mine[0]), file_timecode(yours[0])
        except (OSError, ValueError, RuntimeError):
            continue
        if here is None or there is None:
            continue
        first, second = (mine, yours) if here <= there else (yours, mine)
        fits, why = _joins_seamlessly(first[-1], second[0], first)
        if not fits:
            shut[os.path.abspath(h)] = T(          # the box's own value
                '%s -- joined by hand that difference goes into the file '
                'as silence, and nothing later takes it out.') % why
    return shut


def join_box_fill(box, path, targets, blocks=None):
    """Fill the "belongs to" chooser: its entries, its bar, its hint.

    A target whose clock says the two cannot be one recording is greyed
    rather than left out of the list: the answer to "why can I not pick
    this" has to stand on the entry it is about. Returns the box.
    """
    box.addItem(T('a recording of its own'), "")
    for h in targets:
        box.addItem(os.path.basename(h), os.path.abspath(h))
    return hint(choices_shut(box, join_barred(path, targets, blocks), "",
                             COLOURS["quiet"]),
                T('Puts this recording into another one, with every '
                  'block it has.\nUse it where the file names give the '
                  'search nothing to go on.'))


def channel_rows_build(node, path, Qt, QtCore, QtWidgets, blocks_of,
                       channel_choice, channel_node, channels_arrived,
                       clip_kind_values, items, remembered, split_files):
    """Build the channel rows under one recording.

    Lifted out of gui() whole: it holds no state of its own, it
    only writes rows. What it needs from the window comes in as
    arguments, in the order the window has them.
    """
    api_key = os.path.abspath(path)
    channel_node[api_key] = (node, path)
    row = blocks_of.get(api_key) or [api_key]
    # Where the list stands, kept over the rebuild. Ticking a channel
    # halfway down a mixer file replaces every row below the file, and
    # the list would otherwise jump back to the top at every click.
    bar_was = items.verticalScrollBar().value()
    QtCore.QTimer.singleShot(
        0, lambda: items.verticalScrollBar().setValue(bar_was))
    for k in range(node.childCount() - 1, -1, -1):
        kid = node.child(k)
        if kid.data(0, Qt.UserRole + 2) == "channel":
            node.removeChild(kid)
    try:
        how_many = channel_count(path)
    except Exception:
        how_many = 1
    if how_many <= 1:
        return

    spot = [0]

    def channel_row(text, value):
        kid = QtWidgets.QTreeWidgetItem([text, "", value])
        kid.setData(0, Qt.UserRole + 2, "channel")
        node.insertChild(spot[0], kid)
        spot[0] += 1
        return kid

    if not all(probe_has(channel_facts_name(), x) for x in row):
        channel_row(T('      %s channels') % group_text(how_many),
                    T('measurement running ...'))
        return
    # Over the whole recording: the first block can be the soundcheck,
    # and then it says nothing about what the channels carry.
    facts = blocks_facts(row)
    silent = list(facts.get("silent") or [])
    picked = channel_choice.get(api_key) or {}
    # What the file is decides before the measurement does, and only
    # for a two channel intro or outro -- see kind_makes_stereo. The
    # run never gets here: an intro is used as it lies and is never
    # cut into tracks, so this is the one place that has to know.
    of_kind = clip_kind_values.get(api_key)
    kind = (of_kind.get() if of_kind is not None
            else remembered.get("kind:" + api_key))
    joined = joined_channels(facts, picked, kind)
    judged = {k: (stereo, sure, why)
              for k, stereo, sure, why in channel_joins(facts, kind)}
    # One row per channel, and the tick on it says "this one and the
    # next make one stereo track". Fixed pairs would be an assumption
    # of their own: on a mixer, channels 2 and 3 can be the pair.
    second = {k + 1 for k in joined}
    for k in range(how_many):
        kid = channel_row(T('      Channel %d') % (k + 1), "")
        if k in second:
            kid.setText(2, T('with Channel %d one stereo track') % k)
            continue
        if silent[k:k + 1] == [True]:
            kid.setText(2, T('unused input -- ignored'))
            continue
        if k >= how_many - 1 or silent[k + 1:k + 2] == [True]:
            kid.setText(2, T('a track of its own'))
            continue
        stereo, sure, why = judged.get(k, (False, False, ""))
        measured_stereo = stereo         # before any hand overrides it
        if picked.get(k) is not None:
            stereo = bool(picked[k])
            why = T('set by hand -- overrides the measurement')
            sure = True
        # The tick and its reason side by side in the wide column. In
        # the narrow one -- where the file marks live -- the word
        # beside the box is cut off after the first letter.
        beside = QtWidgets.QWidget()
        in_a_row = QtWidgets.QHBoxLayout(beside)
        in_a_row.setContentsMargins(0, 0, 0, 0)
        in_a_row.setSpacing(8)
        # An offer, not a statement: the row of a channel that is
        # already spoken for says "with Channel N one stereo track",
        # and a tick that used the same words beside a measurement
        # saying the opposite read as a contradiction.
        box = QtWidgets.QCheckBox(
            T('join with Channel %d') % (k + 2))
        box.setChecked(bool(joined.get(k)))
        said = label(why if sure else T('uncertain -- %s') % why,
                     COLOURS["quiet"])
        # What was measured is a sentence, and German writes it half as
        # long again as English. It wraps rather than being cut off:
        # what would run past the edge here is the finding itself.
        said.setWordWrap(True)
        in_a_row.addWidget(box)
        in_a_row.addWidget(said, 1)
        hint(box, T('On makes one stereo track out of this channel '
                    'and the next.\nThe next one then has no tick of '
                    'its own -- it is spoken for.\nWhat was measured '
                    'is in the line beside it.'))

        def chosen(on, file_path=api_key, number=k,
                   measured=measured_stereo):
            # Only a real override is remembered. Ticking a pair the
            # measurement already found, or unticking one it did not,
            # puts the row back to what was measured instead of
            # marking it "set by hand" -- which would otherwise
            # spread across every row somebody has ever touched.
            by_hand = channel_choice.setdefault(file_path, {})
            if bool(on) == bool(measured):
                by_hand.pop(number, None)
            else:
                by_hand[number] = bool(on)
            # The tracks that were cut follow the old answer, so they
            # are dropped and cut again -- every block of the
            # recording, not only the one the row sits on. Leaving the
            # others would put block one's channel 1 next to block
            # two's channels 1+2 on the same row.
            for block in blocks_of.get(file_path) or [file_path]:
                split_files.pop(block, None)
            QtCore.QTimer.singleShot(
                0, lambda: channels_arrived(file_path))

        box.toggled.connect(chosen)
        items.setItemWidget(kid, 2, beside)
    # A moment later, because the column still answers with its old
    # width while it is saying that the width has changed. The width
    # moves again whenever a column is dragged or the window grows.
    def when_settled(*_a):
        QtCore.QTimer.singleShot(
            0, lambda: channel_rows_fit(items, Qt, QtCore, QtWidgets))

    head = items.header()
    if not head.property("channel_rows_fit"):
        head.setProperty("channel_rows_fit", True)
        head.sectionResized.connect(when_settled)
    when_settled()


def video_kinds_again(rows):
    """Draw the Kind cells of the file list again.

    Which camera is the wide shot is derived from who is assigned
    where, and that answer is given on another tab long after this list
    was built. Every row left behind how to draw itself in *rows*; this
    calls them.
    """
    for again in list(rows.values()):
        try:
            again()
        except RuntimeError:
            # That row is gone. The list that replaced it drew itself
            # from the answer as it stands now.
            continue


def queue_once(QtCore, pending, key, work):
    """Let the event loop do this once, however often it is asked.

    One answer fires more than one listener, and every one of them
    asks for the same table to be drawn again. Asked three times, the
    second and the third land while the first is still exchanging the
    cells of that table -- and where a player is starting up at the
    same moment, Qt stands in QWidget::createWinId and does not come
    back.

    Measured 28.8.2026 on the gate test, which builds six windows at
    once: without this, two of four runs never ended; the same test
    against the previous version ended every time in about three
    seconds.
    """
    mark = "queued " + key
    if work is None or pending.get(mark):
        return
    pending[mark] = True

    def run():
        pending[mark] = False
        work()

    QtCore.QTimer.singleShot(0, run)


def hush_when_running(who, mark):
    """Stop the other player, but only if it is running.

    Two pictures at once are two moments at once, and neither can be
    judged, so one player stops the other when it starts. Told to stop
    while it is still starting up, though, the media player connects
    its own objects at that very moment and stands in a lock another
    thread already holds -- and the window never comes back.

    Measured 28.8.2026 on the gate test, which builds six windows at
    once: without this, one run in eight never ended, and the one that
    hung stood in QMediaPlayer::pause every time.

    *mark* names the player's own note of whether it is running. Asked
    on the Python side on purpose: asking Qt is the thing that blocks.
    """
    def quiet():
        hold = getattr(who, "pause", None)
        if hold and getattr(who, mark, False):
            hold()

    return quiet


def not_on_the_axis(path, kinds, remembered):
    """Why the file in the player carries no window boundary, or "".

    A boundary is a point on the axis of the episode. An intro is not
    on that axis: it is set in front, not cut in. A point marked inside
    one would put the window of the episode somewhere that has nothing
    to do with the interview -- seen on 26.8.2026 in a picture of
    an 18-second jingle in the player while the window above it said
    17:14 to 18:23.

    Content and the wide shot stay usable. Everything else -- intro,
    outro, and a file marked not to be used -- is not on the axis. What
    comes back is the reason, because greying the buttons out without
    one beside them reads as a fault in the program.
    """
    held = (kinds or {}).get(path)
    kind = (held.get() if held is not None
            else (remembered or {}).get("kind:" + (path or ""))
            or TYPE_CONTENT)
    if not path or kind in CAMERA_TYPES:
        return ""
    return T('%s is not on the axis of the episode: it is set in front of '
             'the material or after it, not cut into it. In point and Out '
             'point belong to what lies between.') % os.path.basename(path)


def fitted(Qt, label, text):
    """Put text into a label, shortened in the middle where it is too wide.

    The line beside the progress bar carries a file name, so how wide it
    turns out is decided by the material and not by the wording. Measured
    29.8.2026: with a camera file of 29 characters, while its envelope
    was being worked out, the German of this line stood 20 px past its
    field where the English of the same moment fitted -- and a shorter
    wording would only hold until the next longer file name.

    Shortened in the middle, because both ends carry meaning: the name
    at the front and how many are still running at the back. The whole
    line stays readable as a tooltip.
    """
    room = max(0, label.width() - 4)
    metrics = label.fontMetrics()
    if not room or metrics.horizontalAdvance(text) <= room:
        label.setToolTip("")
        label.setText(text)
        return
    label.setToolTip(text)
    label.setText(metrics.elidedText(text, Qt.ElideMiddle, room))








def stop_asked_for(where=""):
    """Ask the run to stop, and end what it has running at this moment."""
    RUN_STOP["wanted"] = True
    RUN_STOP["at"] = where
    for child in list(RUN_STOP["children"]):
        try:
            child.terminate()
        except Exception:
            # It ended by itself between the two lines. Nothing to do.
            pass


def stop_forget():
    """Forget a request, before the next run starts."""
    RUN_STOP["wanted"] = False
    RUN_STOP["at"] = ""
    RUN_STOP["children"].clear()




def stop_here(what=""):
    """Break off, where a run may be broken off -- and nowhere else.

    Called between steps, never in the middle of writing one file. A
    file half written is worse than a run that takes a few seconds
    longer to notice it should stop: the half file looks finished from
    the outside, and the next run finds it and believes it.
    """
    if RUN_STOP["wanted"]:
        # What the window said is the better answer: it knows which step
        # was on the screen, while this only knows where the run got to
        # before it looked.
        raise Stopped(RUN_STOP["at"] or what)


class Redirect(object):
    """Send the run output to the window and to the log file.

    The window is gone once it is closed; the file stays. Only that way
    can a run be read back afterwards.

    *show* is where the window wants it, *having* the open log file.
    Out here rather than inside gui(), because it needs one thing from
    the window and nothing else, and gui() has no room to spare.
    """

    # Says: leave the kind markers in, the window needs them.
    keeps_marks = True

    def __init__(self, having=None, show=None):
        self.having = having
        self.show = show

    def write(self, text):
        if self.show is not None:
            self.show(text)
        if self.having is not None:
            try:
                self.having.write(strip_marks(text))
                self.having.flush()
            except Exception:
                pass

    def flush(self):
        pass


def broken_off_report(where, results):
    """What to say after a run was broken off, in as many words.

    Not only that it ended. What was written before the break is
    whole -- a run is only ever broken off between steps, never in the
    middle of writing one file -- but the steps after it did not
    happen. So the folder holds a part of a run, and from the outside
    it looks like a result. Whoever reads this has to be able to tell
    the two apart tomorrow.
    """
    done = [os.path.basename(x) for x in (results or [])]
    return "\n".join([
        T('\nStopped during: %s') % (where or "?"),
        TN(len(done),
           '%s file was finished before that and is whole: %s',
           '%s files were finished before that and are whole: %s')
        % (group_text(len(done)), ", ".join(done) or "-"),
        T('Everything after that step is missing. The folder holds a '
          'part of a run, not a result.')])


def break_off_button(QtWidgets, state, say):
    """The button that stops a run, and what it says while it does.

    Away while nothing runs: a button that does nothing is a question
    nobody asked. It can be pressed at any moment, in the middle of
    writing a file as much as between two steps -- but the run stops
    only where stopping leaves nothing half written, so between the
    press and the end there is a wait. That wait is said out loud, or
    the button looks broken and gets pressed again and again.

    *state* is the window's own note of what is going on, and *say*
    writes a line where the run writes.
    """
    button = QtWidgets.QPushButton(T('Stop'))
    button.setVisible(False)

    def pressed():
        if not state.get("running"):
            return
        button.setEnabled(False)
        button.setText(T('Stopping ...'))
        say(T('\nStopping. The run ends as soon as it can do so '
              'without leaving a file half written -- one moment.\n'))
        stop_asked_for(state.get("run_step") or "")

    button.clicked.connect(pressed)
    return button


def button_in_a_frame(QtWidgets, button):
    """Wrap a button in a bare frame, and hand the frame back.

    Two reasons, and every footer button that can be switched off goes
    through here for both. A disabled button takes no mouse events in
    Qt and so shows no tooltip; the frame takes them and carries a copy
    of its text. And a button wants a fixed height where a plain widget
    wants a preferred one, so a wrapped button centres in its frame and
    a bare one in the row -- on an odd difference they round apart.
    """
    frame = QtWidgets.QWidget()
    row = QtWidgets.QHBoxLayout(frame)
    row.setContentsMargins(0, 0, 0, 0)
    row.addWidget(button)
    if button.toolTip():
        frame.setToolTip(button.toolTip())
    return frame


def row_same_height(buttons):
    """Give a row of buttons the height of the tallest among them.

    A flat button asks for less room than a framed one. Measured
    offscreen on 31.8.2026 at 1600x1000: Start and Dry run stood 29
    pixels high from 961 to 990, "Settings ..." 25 from 963 to 988 --
    centred between them, so it lined up with neither edge.

    No fixed number: how tall a button wants to be is the system font
    talking, and a number written down here would be wrong on the next
    machine. It is asked of the buttons themselves, and the wish is
    there whether the button is on screen or not, so one that is
    hidden while nothing runs comes out the same height as the rest.

    A button inside a wrapper is given the height itself, not the
    wrapper: the wrapper carries a tooltip for a disabled button and
    hugs whatever is in it.

    Returns the height that was set.
    """
    tallest = max([b.sizeHint().height() for b in buttons] or [0])
    for b in buttons:
        b.setMinimumHeight(tallest)
    return tallest


def break_off_arm(button):
    """Put the button back the way it was, for the run about to start."""
    stop_forget()
    button.setEnabled(True)
    button.setText(T('Stop'))
    button.setVisible(True)


def wide_too_short(number):
    """A line for where the wide shot lasts less than the shortest shot.

    Both are free fields and nothing stops them contradicting each
    other. Set that way, every wide shot put into a long monologue
    arrives under the number the shortest-shot field promises, and the
    cut merges it away again -- so nothing wrong reaches the timeline,
    but the wide shot somebody asked for is simply not there, and no
    line said why.

    Better said before than repaired after: the wide shot length may
    not be shorter than the shortest shot, and the line says so before
    the run rather than after it.

    Returns the line, or "" where the two agree.
    """
    holds = float(number.get("wide-length") or 0.0)
    least = float(number.get("min-edit-duration") or 0.0)
    if holds <= 0 or least <= 0 or holds >= least:
        return ""
    return T('The wide shot holds %s s, less than the shortest shot of '
             '%s s -- so it is merged away again and never appears.\n') % (
                 decimal_text("%g" % holds), decimal_text("%g" % least))


def run_done_text(dry):
    """What to say when a run has ended well.

    A dry run measures and writes nothing, so pointing at a result
    folder and offering to build a Resolve project out of it points at
    whatever an earlier run happened to leave there. Measured
    30.8.2026 on an interview: a dry run said "if all is
    right, Create Resolve project builds the project from it" while the
    newest handover in that folder was four days old, from another
    window and another measurement.
    """
    if dry:
        return T('\nMeasured. Nothing was written -- a dry run leaves the '
                 'result folder as it was.\n')
    return T('\nDone. Below, "Open result folder" shows the result.\nIf '
             'all is right, "Create Resolve project" builds the project '
             'from it.\n')


def question_dialog(f, window, QtWidgets, label):
    """Ask the window's user what to do while a worker thread waits.

    Outside gui() because it reaches into nothing: the question, the
    window it belongs to and the two things it builds with come in as
    arguments. What it answers goes back on the question itself, which
    is what the waiting thread is holding.
    """
    dialog = QtWidgets.QDialog(window)
    dialog.setWindowTitle(f.title)
    dialog.setModal(True)
    position = QtWidgets.QVBoxLayout(dialog)
    position.addWidget(label(T('%s -- what should happen with it?\nThe '
                               'details are in the log.') % f.title))
    buttons = []
    for api_key, text in f.possible:
        # In the log the text is multi-line and indented; in the dialog it
        # becomes one line.
        r = QtWidgets.QRadioButton(" ".join(text.split()))
        position.addWidget(r)
        buttons.append((api_key, r))
    if buttons:
        buttons[0][1].setChecked(True)
    box = QtWidgets.QDialogButtonBox()
    carry_on = box.addButton(T('Continue'),
                             QtWidgets.QDialogButtonBox.AcceptRole)
    box.accepted.connect(dialog.accept)
    box.rejected.connect(dialog.reject)
    position.addWidget(box)
    carry_on.setDefault(True)
    if dialog.exec() == QtWidgets.QDialog.Accepted:
        for api_key, r in buttons:
            if r.isChecked():
                f.choice = api_key
                break
    else:
        f.choice = "abort"
    f.event.set()


def speech_table_fill(Qt, QtGui, QtWidgets, table, d):
    """Write the speaker statistics into the table.

    Outside gui() because it reaches into nothing: the table, the line
    under it and the three Qt names it builds cells with come in as
    arguments. Returns the total speech time as a sentence, empty
    where no speaker is known.
    """
    lines, total, silence, length = (speaker_statistics(d) if d
                                      else ([], 0.0, 0.0, 0.0))
    table.setRowCount(len(lines) + (1 if length > 0 else 0))
    for i, e in enumerate(lines):
        for column, text in ((0, e["name"]),
                             (1, as_minutes(e["seconds"])),
                             (2, "%.1f %%" % e["share"]),
                             (3, "%d" % e["blocks"]),
                             (4, "%.1f s" % e["mean"])):
            p = QtWidgets.QTableWidgetItem(text)
            if column:
                p.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(i, column, p)
    if length > 0:
        i = len(lines)
        for column, text in ((0, T('Silence')), (1, as_minutes(silence)),
                             (2, "%.1f %%" % (100.0 * silence / length)),
                             (3, ""), (4, "")):
            p = QtWidgets.QTableWidgetItem(text)
            p.setForeground(QtGui.QBrush(QtGui.QColor(COLOURS["quiet"])))
            if column:
                p.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(i, column, p)
    fix_table_width(table, most_rows=SPEAKER_ROWS_SHOWN)
    return (T('%s speech time') % as_minutes(total) if lines else "")


def preflight_sentence(findings, audio_file_list, recordings, videos_n):
    """The line under the file list: what is there, and what is wrong.

    Outside gui() because it reaches into nothing: the findings and the
    three counts come in as arguments. Returns the line and the colour
    it is written in.
    """
    recordings = recordings or audio_file_list
    parts = []
    if audio_file_list:
        parts.append("%s%s" % (
            TN(recordings, '%s audio recording', '%s audio recordings')
            % group_text(recordings),
            "" if recordings == audio_file_list
            else T(' from %s files') % group_text(audio_file_list)))
    if videos_n:
        parts.append(TN(videos_n, '%s video file', '%s video files')
                     % group_text(videos_n))
    sentence = ", ".join(parts) if parts else T('nothing selected')
    # What belongs to a file that does not take part is shown on its row,
    # not in the balance below.
    counts = [b for b in findings if not b.set_aside]
    serious = [b for b in counts if b.kind == "abort"]
    hints = [b for b in counts if b.kind == "hint"]
    if serious:
        return sentence + " -- %s" % serious[0].text, COLOURS["error"]
    if len(hints) == 1:
        return (sentence + T(' -- 1 note: %s') % hints[0].text[:110],
                COLOURS["warning"])
    if hints:
        return (sentence + T(' -- %s notes') % group_text(len(hints)),
                COLOURS["warning"])
    return sentence + T(' -- nothing to fault.'), COLOURS["quiet"]


def project_state_read(file_path, elsewhere):
    """Read what is already there and clear leftovers elsewhere.

    Outside gui() because it reaches into nothing: the place the file
    belongs and the places an earlier run may have put it come in as
    arguments. Returns the contents of the file at the current location
    or, if there is none yet, of an earlier one, and beside it the
    places the caller is to clear so that only the one is left.
    """
    found, gone = {}, []
    places = [file_path]
    name = os.path.basename(file_path)
    for place in elsewhere:
        if not place:
            continue
        p = (place if place.lower().endswith(".json")
             else os.path.join(place, name))
        if p not in places:
            places.append(p)
    for p in places:
        try:
            if not os.path.isfile(p):
                continue
            with open(p, encoding="utf-8") as f:
                content = json.load(f) or {}
        except (OSError, ValueError):
            continue
        if not found:
            found = content
        elif isinstance(content, dict):
            # Only extend older state, never overwrite it.
            for s, value in content.items():
                found.setdefault(s, value)
        if os.path.abspath(p) != os.path.abspath(file_path):
            gone.append(p)
    return (found if isinstance(found, dict) else {}), gone


def assignment_marks_show(audio_fields, assign_lines, video_fields,
                          camera_lines, multitrack_on, state,
                          voice_lines=()):
    """Mark the trouble spots red, and say beside the tables what they are.

    Outside gui() because it reaches into nothing: the fields, the rows
    behind them and the window's own store come in as arguments. Three
    things are caught here before they do damage: two recordings with
    the same speaker name, which would become a single track, a voice
    carrying a name that is on somebody else, and two cameras with the
    same output name, where the second would overwrite the first.
    """
    voiced = state.get("voiced") or set()
    audio_reason, video_reason = (state.get("audio_reason"),
                                  state.get("video_reason"))
    # Every name on the sheet at once, both levels of it: whichever way
    # somebody came in by, a name is a person and a person is there
    # once. A recording showing its voices is left out -- its field
    # says "several speakers" and not a name.
    twice = set(names_used_twice(assign_lines, voice_lines, voiced))
    used = [(f, v) for f, (r, v, cv) in zip(audio_fields, assign_lines)
               if cv.get() != IGNORE_AUDIO
               and os.path.abspath(r[0]) not in voiced] \
        if len(audio_fields) == len(assign_lines) else []
    names = [v.get() for _f, v in used]
    duplicate = set(n for n in names if n and names.count(n) > 1)
    for field, value in used:
        n = value.get()
        mark_red(field, bool(n) and n in twice,
                    T('This name occurs more than once. The recordings '
                      'would become one track -- for Multitrack '
                      'auphonic.com needs at least two different ones.'))
    fields = voice_marks_of(state).get("field") or {}
    for key, name_value, camera_value in voice_lines or ():
        n = name_value.get().strip()
        if fields.get(key) is not None:
            mark_red(fields[key],
                     bool(n) and n in twice
                     and camera_value.get() != IGNORE_AUDIO,
                     T('This name is on somebody else already. A name is '
                       'a person, and the cut puts a person on one '
                       'camera -- please give this voice its own.'))
    if audio_reason is not None:
        if duplicate and multitrack_on and len(set(names)) < 2:
            audio_reason.setText(
                T('✕  All recordings carry the same name. That makes '
                  'one track -- Multitrack needs at least two.'))
            audio_reason.setVisible(True)
        elif duplicate:
            audio_reason.setText(
                T('✕  %s occurs more than once. These recordings are '
                  'merged into one track and placed in sequence by '
                  'their timecode -- correct if recording was stopped '
                  'in between.') % ", ".join(sorted(duplicate)))
            audio_reason.setVisible(True)
        else:
            audio_reason.setVisible(False)

    if len(video_fields) == len(camera_lines):
        outputs = [v.get().strip() for _p, v, _k, _n in camera_lines]
        duplicate_video = set(n for n in outputs
                              if n and outputs.count(n) > 1)
        same_name = set(camera_tracks_clashing(camera_lines))
        track_of = dict(camera_tracks_of(camera_lines))
        for field, (p, value, _k, _n) in zip(video_fields, camera_lines):
            n = value.get().strip()
            # The file name first: of the two it is the one this field
            # can put right.
            same_file = bool(n) and n in duplicate_video
            mark_red(field,
                     same_file or track_of.get(p) in same_name,
                        T('Two cameras would produce the same file. '
                          'The second would overwrite the first.')
                        if same_file else
                        T('Two cameras are one camera in the cut. Their '
                          'files carry the same name, so rename one of '
                          'them.'))
        if video_reason is not None:
            if duplicate_video:
                video_reason.setText(
                    T('✕  Two cameras would produce the same file '
                      '(%s). The second would overwrite the first.')
                    % ", ".join(sorted(duplicate_video)))
                video_reason.setVisible(True)
            elif same_name:
                video_reason.setText(
                    T('✕  Two cameras are one camera in the cut (%s). '
                      'Their files carry the same name, so rename one '
                      'of them.')
                    % ", ".join(sorted(same_name)))
                video_reason.setVisible(True)
            else:
                video_reason.setVisible(False)


def make_log_writer(state, post):
    """The window's own way of taking a line of output.

    Outside gui() because it decides nothing: it hands the text to the
    queue the window drains. Every absolute path that really exists is
    kept as a result on the way through, so the button that opens the
    result folder has a target.
    """
    def write(text):
        for line in text.splitlines():
            path = line.strip()
            if os.path.isabs(path) and os.path.exists(path):
                if path not in state["results"]:
                    state["results"].append(path)
        post.put(text)

    return write


def make_update_sink(state, write, show, timer):
    """The window's way of running a long job with its output in view.

    The road a run takes, and for the same reason: the job works in a
    thread of its own while the window stays alive, its lines go into
    the Output tab, and the flag the window watches keeps a run from
    starting on top of it and brings the buttons back at the end.
    """
    def beside(job):
        show()
        state["running"] = True

        def loop():
            trouble = job(write)
            if trouble:
                write(as_bad("\n" + trouble + "\n"))
            state["running"] = False

        threading.Thread(target=loop, daemon=True).start()
        timer.start()

    return beside


def gui_run_loop(argv, state, write, ask_user, bridge, bridge_emit,
                 run_step_order):
    """Do the actual run in a worker thread and catch what it says.

    Outside gui() because it reaches into nothing: the command line,
    the two sinks the window offers and the bridge the progress goes
    over come in as arguments.
    """
    # The three sinks belong to the program: the run they carry
    # happens over there, and it reads them under its own names.
    old_out, old_err = sys.stdout, sys.stderr
    PROGRAM.OUTPUT_SINK = write
    PROGRAM.ASK_SINK = ask_user
    # -1 stands for "this stage is beginning": a Qt signal carries no
    # None, and a share of nothing is not a share.
    PROGRAM.PROGRESS_SINK = lambda name, share: bridge_emit(
        bridge.run_step, name,
        -1.0 if share is None else float(share))
    sys.stdout = sys.stderr = Redirect(old_out, write)
    code = 1
    try:
        sys.argv = argv
        code = main()
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
    except Stopped as e:
        code = 2
        print(as_bad(broken_off_report(e, state.get("results"))))
    except Exception as e:
        print(as_bad(T('\nStopped: %s') % e))
    finally:
        sys.stdout, sys.stderr = old_out, old_err
        PROGRAM.OUTPUT_SINK = None
        PROGRAM.ASK_SINK = PROGRAM.PROGRESS_SINK = None
    # However it ended, nothing of it is still running.
    for name in list(run_step_order):
        bridge_emit(bridge.run_step, name, 1.0)
    if code == 0:
        write(as_good(run_done_text(state.get("dry_run"))))
    else:
        write(as_bad(T('\nFinished with errors.\n')))
    for file_path in state["results"]:
        if file_path.lower().endswith("_resolve.json"):
            state["resolve_json"] = file_path
    if state["results"]:
        state["result_folder"] = os.path.dirname(
            state["results"][-1])
    state["running"] = False

def audio_under_camera(camera_path, kind_of, done,
                   assign_lines, blocks_of):
    """Return the audio recording belonging to this camera.

    For the preview: instead of the camera audio, the audio assigned to it
    plays. Preferably the processed track -- same content, at delivery
    level. Where that does not exist yet, the raw recording. With several
    speakers assigned to one camera the first one applies; a mix of both is
    only created during the run.

    With no speaker assigned -- that is the wide shot -- the overall mix
    plays, if it exists already. That is the same audio the cut timeline
    gets.
    """
    # An intro or an outro stands before or after the episode, not
    # inside it, so nothing off the episode's own axis belongs
    # under it -- neither a speaker's recording nor the mix.
    kind = kind_of.get(camera_path)
    if kind is not None and kind.get() in (TYPE_INTRO, TYPE_OUTRO):
        return []
    short = os.path.basename(camera_path)
    for row, nv, cv in assign_lines:
        if cv.get() != short:
            continue
        name = nv.get()
        if name and name in done:
            return [done[name]]
        if os.path.exists(row[0]):
            # The whole recording, not its head -- see block_at.
            return blocks_of.get(row[0]) or [row[0]]
    for name in ("Full-Mix", "Fullmix", "Mix"):
        if name in done:
            return [done[name]]
    return None


def make_player_choice(files, clip_kind_values, assign_lines, start_var,
                       end_var, player, remembered, state, window_enable):
    """Which file the player shows, and where it starts inside it.

    Outside gui() because it decides nothing about the window: it reads
    the two boundary fields, the file list and the Kinds, and answers
    with a video file and a time in it. `state`, `files` and
    `remembered` are the window's own objects and go on being written
    through.
    """
    def player_load(file_path, seconds=None):
        """Load a file into the player and remember which it was.

        The choice belongs in the project. And what was running goes on
        running: switching cameras while watching is comparing them.
        """
        remembered["player_file"] = file_path
        player.load(file_path, seconds, running=player.now_playing())
        if not state.get("closing"):
            window_enable()      # it decides whether a boundary can be set

    def player_spot_wanted(file_path):
        """Return where the player should start in this file.

        Preferably where it was left, which is stored in the project file.
        Otherwise at the In point: the start of the file usually shows only the
        setup.
        """
        spot = remembered.get("player_spot")
        if (remembered.get("player_file") == file_path
                and isinstance(spot, (int, float)) and spot > 0.0):
            return float(spot)
        span = picture_span(file_path)
        text = start_var.get()
        if not span or not (text or "").strip():
            return None
        try:
            value, absolute = parse_time_point(text, span["fps"])
        except Exception:
            return None
        if value is None:
            return None
        if absolute:
            if span["tc0"] is None:
                return None
            value -= span["tc0"]
        elif value >= 0:
            if span["axis"] is None:
                return None
            value -= span["axis"]
        else:
            value = span["duration"] + value
        if not (0.0 <= value <= span["duration"] + 0.05):
            return None
        return max(0.0, value)

    def picture_span(file_path):
        """What this file knows about its place in time, on this axis."""
        return file_span(file_path, state["axis"])

    def covers(file_path, text):
        """Report whether a time value lies inside this video file.

        None means undecidable -- the value is a timecode and the file has
        none, or it counts from the start of the material and the time axis
        has not been measured.
        """
        # A cheap early return, not a guard: four lines down the time
        # reader answers None for empty text just the same, so taking
        # this line out changes nothing anybody can see. It saves
        # reading the file's span for a field nobody has filled in.
        if not (text or "").strip():
            return None
        span = picture_span(file_path)
        if not span or not span["duration"]:
            return None
        try:
            value, absolute = parse_time_point(text, span["fps"])
        except Exception:
            return None
        if value is None:
            return None
        if absolute:
            if span["tc0"] is None:
                return None
            value -= span["tc0"]
        elif value >= 0:
            if span["axis"] is None:
                return None
            value -= span["axis"]
        else:
            value = span["duration"] + value
        return -0.05 <= value <= span["duration"] + 0.05

    def player_candidates():
        """Return the video files eligible for the player.

        Never one set to "ignore this video", which does not take part anyway.
        Intro and outro neither: they do not show the events the time window is
        about.
        """
        out = []
        for file_path, kind in files:
            if kind != "video":
                continue
            value = clip_kind_values.get(file_path)
            if value is not None and value.get() not in CAMERA_TYPES:
                continue
            out.append(file_path)
        return sorted(out, key=lambda x: os.path.basename(x).lower())

    def player_suggestion():
        """Return the file that belongs in the player.

        First choice is one containing In point *and* Out point, otherwise the
        two jump buttons go nowhere. Then one containing at least one boundary.
        Among equals the camera with no speaker assigned: that is the wide shot
        and shows the most. Among those the longest. A previous choice wins a
        tie.
        """
        videos = player_candidates()
        if not videos:
            return None
        taken = set(cv.get() for _r, _nv, cv in assign_lines)

        def hit(file_path):
            return sum(1 for t in (start_var.get(), end_var.get())
                       if covers(file_path, t) is True)

        def quality(file_path):
            free = 0 if os.path.basename(file_path) in taken else 1
            span = picture_span(file_path)
            return (hit(file_path), free, (span or {}).get("duration") or 0.0)

        # The remembered choice holds as long as it covers the boundaries just
        # as well. Letting it fail on "the wide shot is longer" would mean not
        # remembering it at all.
        last_time = remembered.get("player_file")
        if last_time in videos and hit(last_time) == max(hit(b)
                                                         for b in videos):
            return last_time
        return max(videos, key=quality)

    def main_track_show(force=False):
        """Load a picture into the player so the box is not empty.

        Without *force* whatever is playing stays. With *force* the file is
        chosen again -- after opening a project, say, when In point and Out
        point suddenly exist and the old file does not contain them.
        """
        suggestion = player_suggestion()
        if suggestion is None:
            return
        if player.file_path and not force:
            return
        if player.file_path == suggestion:
            return
        player_load(suggestion, player_spot_wanted(suggestion))

    def player_follow_up(spot_also=False):
        """Swap the player file if it no longer covers the boundaries.

        With *spot_also* it additionally jumps to the remembered position --
        when opening a project, where the player would otherwise sit at the
        start of the file.
        """
        swapped = False
        if ((start_var.get() or "").strip()
                or (end_var.get() or "").strip()):
            if not (player.file_path and all(
                    covers(player.file_path, t) is not False
                    for t in (start_var.get(), end_var.get()))):
                main_track_show(force=True)
                swapped = True
        if spot_also and not swapped and player.file_path:
            where_to = player_spot_wanted(player.file_path)
            if where_to is not None:
                player.jump(int(where_to * 1000))

    return (player_load, player_spot_wanted, picture_span, covers,
            player_candidates, player_suggestion, main_track_show,
            player_follow_up)


def make_voice_rows(Qt, QtCore, assign_lines, camera_lines, voice_lines,
                    files, remembered, state, tree_open, multitrack, player,
                    assignment_check, player_load, speaker_split_kick_off,
                    voices_of):
    """The rows of the assignment tree, and the voices under them.

    Outside gui() because none of it builds a widget. `state`, `files`,
    `remembered`, `tree_open` and the three row lists are the window's
    own objects and go on being written through. `player` is a
    parameter on purpose -- a module-level name player already holds
    the piece read by beside(), and a hoisted function reading it
    freely would have picked up the module instead of the widget.
    """
    def assignment_state_show():
        """What the material allows: the cut box, and the tick's line.

        The camera cut needs speakers told apart, and whether they came
        of separate tracks or of one recording taken apart is no part
        of it -- hanging the box off the Multitrack tick hid the cut
        from everybody with one recording and four voices in it. The
        line beside the tick says why Multitrack is not on offer, where
        the question is asked instead of at the start button.

        The widgets are looked up and not closed over: this runs while
        the window is still being built.
        """
        boxes = state.get("cut_boxes")
        if boxes:
            pairs = assignment_pairs(voice_lines, assign_lines)
            seen = len(camera_lines)
            on = bool(multitrack.get()) or cut_has_people(pairs, seen)
            boxes[0].setTitle(cut_box_title(pairs, multitrack.get(), seen))
            boxes[0].setVisible(on)
            boxes[1].setVisible(on)
            boxes[2].setVisible(not on)
        note = state.get("multitrack_note")
        if note is not None:
            used = [r for r in assign_lines if r[2].get() != IGNORE_AUDIO]
            note.setText(multitrack_state_note(
                len(used), sum(1 for _b, _nv, own, _n in camera_lines
                               if not own.get())))

    def voice_play(key):
        """Hand that voice to the player on the right.

        Without hearing it a name is a guess, and hearing it once is
        rarely enough. A player of its own played eight seconds and
        stopped, with no way back. The one on the right has the rail,
        the pause, the ten second jumps and the In and Out points, and
        it plays a recording as it lies: an audio file shows its name
        where the picture would be.

        It jumps into the middle of the longest stretch and not to its
        start, because the first moment of a passage is often the tail
        of somebody else's word. *key* carries the recording, so the
        row plays its own file and not whichever was separated last.
        """
        source, label = voice_key_parts(key)
        source = source or state.get("speakers_source") or ""
        stretch = longest_stretch(
            speakers_stored(state, source).get("segments"), label)
        if not source or not stretch:
            return
        length = min(8.0, stretch[1] - stretch[0])
        begin = stretch[0] + max(0.0, (stretch[1] - stretch[0] - length) / 2)
        player.load(source, seconds=begin, running=True)

    def assignment_row_show(tree):
        """A clicked row in the assignment tree, whichever level it is.

        The recording goes into the player like any other file. A voice
        has no file of its own, so the player opens the recording it
        was heard in and jumps to where that voice speaks longest. That
        is the whole of what a Listen button in the row would offer, so
        there is none.

        Which of the two a row is, the row itself says: the file hangs
        on a recording, the label of the voice on a voice.
        """
        row = tree_row_of(tree, tree.currentIndex())
        if row is None:
            return
        if row[0].data(Qt.UserRole + 2):
            voice_play(row[0].data(Qt.UserRole + 2))
        elif row[0].data(Qt.UserRole + 1):
            player_load(row[0].data(Qt.UserRole + 1))

    def folded_show(where):
        """Open, the voices carry the assignment; folded, the row sums up.

        The assignment has exactly one level. Where the voices are on
        the screen they carry it and the recording above them shows
        nothing beside its name -- two answers one above the other
        could contradict each other, which is what the two tables
        before this did. Folded away, the voices are not on the screen,
        and then the row says what went with them -- their cameras. Not
        how many they are: the Speakers column of the same row already
        says that, and the number stood there twice.

        Which way a recording was left is kept, so that reaching the
        sheet again finds it as it was, and the tree takes the height
        its open rows need.
        """
        tree = state.get("assignment_tree")
        row = tree_row_of(tree, where) if tree is not None else None
        if row is None:
            return
        p, many = row[0].data(Qt.UserRole + 1), row[0].rowCount()
        if not p or not many:
            return
        open_now = tree.isExpanded(where)
        tree_open[p] = open_now
        tree_cell(row, 2, "" if open_now else folded_summary(tree, row),
                  COLOURS["quiet"])
        tree_rows_fit(tree, 266)

    def voice_add(source):
        """Say there is one more voice on that recording than was found.

        A row without segments would say nothing, so this is the input
        to a fresh separation rather than an entry in a list: the
        number of speakers is set and the recording is listened to
        again.
        """
        found = len(speakers_stored(state, source).get("segments") or ())
        state["speakers_source_chosen"] = source
        state["speakers_count"] = found + 1
        speaker_split_kick_off(fresh=True)

    def voices_build(tree, under, path, videos, targets, wide=None):
        """The voices heard in one recording, hung under its row.

        Everything here counts per camera and not per speaker: two
        voices set to the same camera are one condition, and what one
        of them did counts for both. Which is why the camera sits on
        the voice and not on the file.

        *wide* is what wide_bar_of worked out, handed in rather than
        asked again. Returns how many voices there were, so the caller
        knows whether the recording is a parent at all.
        """
        wide = wide or wide_bar_of(targets, (), False, {})
        barred = wide["barred"]
        found = voices_of(path)
        # The names of this recording, not of the window.
        called = dict(speakers_stored(state, path).get("names") or {})
        for label, _parts in found:
            key = voice_key(path, label)
            name_value = SpeakerName(voice_name_free(
                remembered.get("voicename:" + key) or called.get(label),
                [nv.get() for _k, nv, _c in voice_lines]))
            picked, worked_out = camera_row_cameras(
                camera_after_a_mark("voice:" + key,
                                    remembered.get("voice:" + key), wide,
                                    name_value.get().strip() or label),
                wide["pickable"], name_value.get(), videos)
            camera_value = Value(MIX_ONLY if picked in barred else picked)
            camera_value.derived = worked_out
            # The first column says which of the two levels this row
            # is, indented under the recording, the way the file list
            # writes "belongs to" and "4 channels" under a file. Not
            # the file name and not the speaker's: the one stands in
            # the row above, the other in the field beside it.
            kid = tree_row(tree, under, [])
            tree_cell(kid, 0, T('Voice'), COLOURS["quiet"])
            kid[0].setData(key, Qt.UserRole + 2)
            field, box = voice_row_cells(name_value, camera_value,
                                         targets, name_value.get())
            choices_shut(box, barred, wide["why"], COLOURS["quiet"])
            tree_field(tree, kid, 1, field)
            tree_field(tree, kid, 2, box)
            row_picker_watch(state["row_picker"], field, box)
            voice_row_marks(state, key, name_value, camera_value,
                            field, box)
            def voice_answered(*_):
                """Store it, mark it, and say the Kind column again.

                Name and camera both count: the wide shot is derived
                from the cameras nobody is assigned to. The mark is the
                same way the rows above answer, on the same wait: a
                name already on somebody else is red while it is typed.
                """
                queue_once(QtCore, state, "voices", voices_remember)
                QtCore.QTimer.singleShot(0, assignment_check)
                queue_once(QtCore, state, "kinds",
                           state.get("kinds_refresh"))
                # The preview reads a handover older than this
                # answer, so it is told -- through the usual wait.
                soon = state.get("preview_soon")
                if soon:
                    soon()

            name_value.listen(voice_answered)
            camera_value.listen(voice_answered)
            voice_lines.append((key, name_value, camera_value))
        return len(found)

    def voices_remember():
        """Keep the names and cameras given to the voices."""
        if not voice_lines:
            # Switched back to a single name: the rows are hidden, and
            # what was measured and named must survive that -- three
            # minutes of computing are not undone by a mis-click.
            return
        # Each recording's names go back to that recording.
        named = voice_names_by_source(voice_lines,
                                      state.get("speakers_source") or "")
        voice_names_store(state, named)
        for k, nv, cv in voice_lines:
            # Only a real override, the same rule the recordings above
            # follow: a camera the program worked out itself goes back
            # as nothing, so renaming a voice moves its camera too.
            remembered["voice:" + k] = camera_to_remember(
                cv.get(), getattr(cv, "derived", None))
            # The name as well, not only the camera: state alone does
            # not reach the project file, and the name is what
            # auphonic.com puts on the track.
            said = nv.get().strip()
            if said:
                remembered["voicename:" + k] = said
            else:
                remembered.pop("voicename:" + k, None)
        voices_answer_kept(remembered, files, named)
        # A voice that has just been given a camera may be the second
        # one, and with it the camera cut becomes possible.
        assignment_state_show()
        # Bound below this block in gui(), so it is reached the way
        # voice_answered above reaches it: through state.
        soon = state.get("preview_soon")
        if soon:
            soon()

    return (assignment_state_show, voice_play, assignment_row_show,
            folded_show, voice_add, voices_build, voices_remember)


def make_prework_bar(QtCore, bridge, bridge_emit, plan, prework_box,
                     prework_label, prework_progress_bar, prework_node,
                     prework_discarded, prework_lock, prework_queue,
                     prework_run, prework_shares):
    """The prework bar, and what the working threads report into it.

    Outside gui() because it builds no widget: the box, the bar and the
    label are made there and handed in, and everything here runs in the
    window thread the signal arrives on. The containers are the
    window's own objects and go on being written through. QtCore is a
    parameter because PySide6 is imported inside gui(), and a hoisted
    function reading the name freely would find none.
    """
    def prework_busy():
        with prework_lock:
            return bool(prework_queue) or prework_run["threads"] > 0

    def prework_report(file_path, text, share=None, task=""):
        bridge_emit(bridge.progress, os.path.abspath(file_path), text,
                    -1.0 if share is None else float(share), task)

    def prework_display_text(file_path, text, share, task):
        """Runs in the window thread; Qt passes the signal through.

        Several threads work at once and each reports only its own file. What
        is displayed is therefore not the last message but the state of all
        files together: a percentage per file, with the bar showing the
        average. A file that left the list is not shown at all: its
        thread cannot be broken off mid-write and goes on reporting,
        and every such report would put it back on the bar.
        """
        if path_key(file_path) in prework_discarded:
            return
        if task:
            prework_shares[prework_share_key(file_path, task)] = max(
                0.0, min(1.0, share))
            plan.report("pre:%s:%s" % (task, file_path), share,
                        "%s   %s" % (os.path.basename(file_path), text)
                        if text else os.path.basename(file_path))
        elif share >= 1.0:
            for k in list(prework_shares):
                if k[0] == path_key(file_path):
                    prework_shares[k] = 1.0
            for name in [n for n in plan.order
                         if n.endswith(":" + file_path)]:
                plan.done(name)
        prework_status_show()
        # In the file list above as well; that is where one looks first.
        entry = prework_node.get(file_path)
        if entry:
            node, first_text = entry
            try:
                node.setText(2, "%s   --   %s" % (first_text, text)
                               if text else first_text)
            except RuntimeError:
                prework_node.pop(file_path, None)

    def prework_status_show():
        """Refresh the bar and the list."""
        if not prework_shares:
            prework_box.hide()
            return
        total, lines = prework_standing(prework_shares)
        # The bar only moves forward. Adding a file lowers the average
        # arithmetically, but a bar jumping back looks like a fault even though
        # nothing is lost.
        status = max(prework_run.get("bar", 0), int(round(100 * total)))
        prework_run["bar"] = status
        prework_progress_bar.setValue(status)
        prework_label.setText(T('Prework -- read audio and compute '
                                'envelopes:\n') + "\n".join(lines))
        prework_box.show()
        if total >= 0.999 and not prework_busy():
            prework_shares.clear()
            prework_run["bar"] = 0
            QtCore.QTimer.singleShot(1200, prework_box.hide)
        elif total >= 0.999 and not prework_ask_again.isActive():
            # This runs on a report, and no report follows a thread
            # counting itself out -- so the question is asked once more
            # rather than never. One look is on its way at a time.
            prework_ask_again.start(200)

    prework_ask_again = QtCore.QTimer(prework_box)
    prework_ask_again.setSingleShot(True)
    prework_ask_again.timeout.connect(prework_status_show)

    bridge.progress.connect(prework_display_text)

    return prework_busy, prework_report, prework_status_show


def make_prework_tasks(state, bridge, bridge_emit, plan, blocks_of,
                       recording_of, channel_choice, split_files, split_run,
                       prework_report, prework_status_show, prework_done,
                       prework_pending, prework_queue, prework_discarded,
                       prework_lock, prework_run, prework_shares):
    """What the background threads do to one file, and what starts them.

    The other side of the bar above: nothing here touches a widget, and
    all of it runs off the window thread. What it reports goes through
    prework_report, which crosses back over the signal. The three
    containers below are read nowhere else and are made here; the rest
    belong to the window and are handed in.
    """
    PREWORK_THREADS = max(1, min(4, how_many_processors()))
    prework_folder = {"path": None}
    prework_active = set()          # taken off the queue, being worked on

    def prework_where():
        """The folder the prepared files live in, made on first use."""
        with prework_lock:
            if not prework_folder["path"]:
                prework_folder["path"] = tempfile.mkdtemp(prefix="vpm_camaudio_")
                atexit.register(shutil.rmtree, prework_folder["path"], True)
            return prework_folder["path"]

    def prework_target(file_path, api_key):
        folder = prework_where()
        stem = os.path.splitext(os.path.basename(file_path))[0]
        return os.path.join(folder, "%s_%08x.wav"
                            % (safe_filename(stem)[:40],
                               abs(hash(api_key)) & 0xFFFFFFFF))

    def prework_audio_fetch(file_path, api_key):
        if api_key in prework_done:
            prework_report(file_path, "", 1.0, "audio")
            return True
        prework_report(file_path, T('Fetching audio ...'), 0.0, "audio")
        target = prework_target(file_path, api_key)
        try:
            prework_fetch(file_path, target,
                     lambda a, p=file_path: prework_report(
                         p, T('Fetching audio'), a, "audio"))
        except Exception as e:
            prework_report(file_path, T('no audio: %s') % str(e).strip()[:40], 1.0, "audio")
            return False
        # Where the file left the list meanwhile, the work was wasted; clear it
        # away right there rather than leaving it lying about.
        if path_key(file_path) in prework_discarded:
            try:
                os.unlink(target)
            except OSError:
                pass
            return False
        prework_done[api_key] = target
        return True

    def prework_env_curve_build(file_path):
        """Precompute the envelope so the run finds it ready."""
        if (path_key(file_path), 5.0, 4000) in _ENV:
            prework_report(file_path, "", 1.0, "envelope")
            return True
        prework_report(file_path, T('Envelope'), 0.0, "envelope")
        try:
            video_envelope(file_path, report=lambda a, p=file_path: prework_report(
                p, T('Envelope'), a, "envelope"))
        except Exception as e:
            prework_report(file_path, T('Envelope failed: %s')
                      % str(e).strip()[:40], 1.0, "envelope")
            return False
        return True

    def prework_channels_look(file_path):
        """Measure the channels of a multichannel file.

        Reading every channel of an hour of audio takes seconds. In the
        window thread that is a frozen list; here it is a line on the
        bar like everything else.
        """
        prework_report(file_path, T('Looking at the channels'), 0.0,
                       "channels")
        try:
            channel_facts_cached(file_path)
        except Exception as e:
            prework_report(file_path, T('channels not readable: %s')
                           % str(e).strip()[:40], 1.0, "channels")
            return False
        prework_report(file_path, "", 1.0, "channels")
        bridge_emit(bridge.channels_done, os.path.abspath(file_path))
        return True

    def prework_split_make(file_path):
        """Cut a multichannel file into the tracks it will contribute.

        Written as real files, because everything after this point --
        the assignment, the player, the run -- works with files. A
        track that stays whole is not written: the original is the
        track.
        """
        api_key = os.path.abspath(file_path)
        # The decision belongs to the recording, the cutting to the block:
        # every block is cut the same way, and the pieces are regrouped
        # afterwards.
        head = recording_of.get(api_key, api_key)
        try:
            facts = blocks_facts(blocks_of.get(head) or [api_key])
            want = tracks_to_split(file_path, facts,
                                   channel_choice.get(head))
        except Exception as e:
            prework_report(file_path, T('channels not readable: %s')
                           % str(e).strip()[:40], 1.0, "split")
            return False
        if not want:
            split_files[api_key] = []
            prework_report(file_path, "", 1.0, "split")
            bridge_emit(bridge.split_done, api_key)
            return True
        folder = prework_where()
        out = []
        for i, (chs, label) in enumerate(want):
            prework_report(file_path,
                           T('Cutting out track %d of %d')
                           % (i + 1, len(want)),
                           float(i) / len(want), "split")
            target = split_target(file_path, chs, folder)
            # A camera often records at 44.1 kHz while everything else in
            # the run is at 48. Two rates in one mix would not line up, so
            # a piece cut out of a video is brought to the run's rate.
            rate = (SR if os.path.splitext(file_path)[1].lower()
                    in VIDEO_SUFFIXES else None)
            try:
                if not os.path.exists(target) or not os.path.getsize(target):
                    split_channels(file_path, chs, target, rate=rate)
            except Exception as e:
                prework_report(file_path, T('cutting failed: %s')
                               % str(e).strip()[:40], 1.0, "split")
                return False
            out.append((target, label))
        split_files[api_key] = out
        prework_report(file_path, "", 1.0, "split")
        bridge_emit(bridge.split_done, api_key)
        return True

    def prework_drop(entry):
        """Take a task out of the count and off the bar.

        Counted as finished, because nobody else will finish it: a share
        stuck at zero holds the bar back for good. Reported through the
        signal, since the bar belongs to the window thread.
        """
        with prework_lock:
            prework_pending[entry[0]] = prework_pending.get(entry[0], 1) - 1
        prework_report(entry[0], "", 1.0, entry[1])

    def prework_work_loop():
        """One of several threads; takes whatever is still pending."""
        try:
            while True:
                with prework_lock:
                    if not prework_queue:
                        # Counted down inside the same lock. Between
                        # releasing it and a finally the count would be too
                        # high for a moment, and a kick_off landing there
                        # would start no thread at all.
                        prework_run["threads"] -= 1
                        return
                    entry = prework_queue.pop(0)
                    # It is off the queue but not done; without this a
                    # second thread would extract the same file into the
                    # same target while the first is still writing it.
                    prework_active.add(entry)
                file_path, task = entry
                try:
                    if path_key(file_path) in prework_discarded:
                        prework_drop(entry)
                        continue
                    try:
                        api_key = prework_api_key(file_path)
                    except OSError:
                        prework_drop(entry)
                        continue
                    if task == "audio":
                        good = prework_audio_fetch(file_path, api_key)
                    elif task == "channels":
                        good = prework_channels_look(file_path)
                    elif task == "split":
                        good = prework_split_make(file_path)
                    else:
                        good = prework_env_curve_build(file_path)
                    if not good:
                        prework_drop(entry)
                        continue
                    with prework_lock:
                        prework_pending[file_path] = prework_pending.get(
                            file_path, 1) - 1
                        done_with = prework_pending[file_path] <= 0
                    if done_with:
                        # Done means show nothing: a "ready" that stays
                        # only takes up space.
                        prework_report(file_path, "", 1.0)
                finally:
                    with prework_lock:
                        prework_active.discard(entry)
        except BaseException:
            with prework_lock:
                prework_run["threads"] -= 1
            raise

    def prework_kick_off(paths, having_audio=()):
        """Queue the prework: envelopes for all, audio for some."""
        for p in paths:
            prework_discarded.discard(path_key(p))

        def audio_present(a):
            """Report whether the processed audio is already there.

            None means the file cannot even be queried; the run reports that.
            """
            try:
                return prework_api_key(a) in prework_done
            except OSError:
                return None

        fresh = pending_prework(paths, having_audio, audio_present,
                              lambda a: (path_key(a), 5.0, 4000) in _ENV,
                              lambda a: probe_has(channel_facts_name(), a),
                              lambda a: os.path.abspath(a) in split_files)
        with prework_lock:
            for entry in fresh:
                if entry not in prework_queue and entry not in prework_active:
                    prework_queue.append(entry)
                    prework_pending[entry[0]] = prework_pending.get(entry[0], 0) + 1
            # Several threads at once: ffmpeg is barely held up while reading
            # and the files sit on the same disk -- four at a time saturate the
            # machine without getting in each other's way.
            # Measured: the different kinds of work do not slow each
            # other down, and the one real brake on the separation is a
            # full processor. On a small machine the prework therefore
            # goes single file while the separation runs; from four
            # processors up everything runs at once.
            room = (PREWORK_THREADS
                    if (how_many_processors() >= SPEAKER_SPLIT_TOGETHER_CORES
                        or not split_run["busy"]) else 1)
            needed = min(room - prework_run["threads"], len(prework_queue))
            prework_run["threads"] += max(0, needed)
        if not prework_shares:
            prework_run["bar"] = 0
        for p, task in fresh:
            prework_shares.setdefault(prework_share_key(p, task), 0.0)
            # Announced before the work starts: a bar that only learns of
            # a step when that step begins jumps backwards at every one.
            plan.add("pre:%s:%s" % (task, os.path.abspath(p)),
                     prework_weight(p, task), os.path.basename(p))
        prework_status_show()
        for _ in range(max(0, needed)):
            threading.Thread(target=prework_work_loop, daemon=True).start()
        # Bound in gui() below the call that built this, so it cannot be
        # a parameter. Reached the way the assignment tree reaches
        # preview_soon: through state.
        axis = state.get("axis_kick_off")
        if axis:
            axis(list(paths))

    return prework_kick_off


def make_preview(Qt, QtWidgets, state, bridge, bridge_emit, assign_lines,
                 camera_lines, voice_lines, cut_var, cut_parts, edge_on,
                 start_var, end_var, multitrack, out_folder, clip_kind_value,
                 wide_cameras_now, commonest_folder, band_show, speech_show,
                 window_info_show, question_note, cut_column, forecast_box,
                 preview_label, speech_title, speech_table):
    """The preview: who speaks when, and what the cut would look like.

    Outside gui() because it is one question answered end to end -- the
    handover built from the assignment, the measurement that fills what
    the assignment leaves open, and the numbers written under the
    picture. The widgets it writes into are made in gui() and handed
    in; the one row it builds itself belongs to the measurement alone.
    Qt comes in as a parameter: PySide6 is imported inside gui().
    """

    def off_speakers():
        """Build a handover from who speaks when and the assignment.

        Turning the cut values then needs no Resolve run to see the
        effect. Where nothing is found, the reason is stated.
        """
        # The separations first: worked out on this machine, and there
        # before anything has been uploaded. They separate people
        # rather than levels, so they go in front of the measurement.
        apart = separation_sources(speakers_for_run(state, voice_lines))
        rows = track_recordings_of(assign_lines)
        segment_list, length = speakers_all_on_window_axis(
            state, voice_lines, assign_lines, audio_start)
        state["stat_measured"] = not bool(segment_list)
        # And every track no separation speaks for, measured from its
        # own microphone. The run takes those too, and a preview that
        # leaves people out is a preview of a different cut.
        segment_list, length = speakers_window_all(
            segment_list, length, state.get("speakers_measured"),
            rows, apart)
        state["tracks_left"] = tracks_awaiting_measure(
            rows, state.get("speakers_measured"), apart)
        where_to = speakers_to_cameras(assign_lines, voice_lines,
                                       state.get("voiced") or set())
        axis = state.get("axis") or {}

        d, reason = build_handover(segment_list, length, where_to,
            [{"track": t, "file": b,
              "start_s": camera_start(b),      # the mark, or the preview
              "wide_marked": clip_kind_value(b).get() == TYPE_WIDE}
             for b, t in camera_tracks_of(camera_lines)],
            audio_origin=[audio_start_of(row[0], axis)
                      for row, _nv, cv in assign_lines
                      if cv.get() != IGNORE_AUDIO and os.path.exists(row[0])],
            camera_origin=[camera_start_of(b)
                           for b, _n, _own, _own_flag in camera_lines],
            places=(out_folder.get(), commonest_folder()))
        if d is None:
            state["reason"] = reason
        return d

    def audio_start(file_path):
        """Return where this recording starts on the common time axis.

        The same road as audio_start_of, because it is the same
        question: two places answering it apart is how a clock that was
        never set got believed here while the first tab said out loud
        that it could not be right.
        """
        t = audio_start_of(file_path, state.get("axis") or {})
        return 0.0 if t is None else float(t)

    def camera_start(file_path):
        """Return where this file starts on the common time axis.

        The measurement first, then the timecode. Without either the
        beginning -- then all files lie on top of each other and the
        preview still shows the rhythm.
        """
        a = (state.get("axis") or {}).get(path_key(file_path))
        if a is None:
            try:
                a = timecode_seconds(video_facts(file_path))
            except (OSError, ValueError, RuntimeError):
                a = None
        return float(a) if a is not None else 0.0

    def forecast_empty(empty):
        """While nothing is computed the box holds only the hint."""
        for widget in (speech_title, speech_table):
            widget.setVisible(not empty)

    def speaker_measure_done(result):
        segment_list, length, error = result
        state["speakers_measuring"] = False
        if error:
            state["measure_failed"] = True
            label_say(measure_label, error[:160], COLOURS["error"])
            return
        state["speakers_measured"] = {"segments": segment_list,
                                        "length": length}
        state["cut_basis"] = "measured"
        label_say(measure_label,
                  *cut_basis_line("measured", len(segment_list), length))
        # preview_soon: through state. The kick-off hangs on the
        # debounce timer and is made after this function has run.
        state["preview_soon"]()

    def speaker_measure():
        """Derive the speech segments from the tracks themselves."""
        tracks = []
        for row, name_value, camera_value in assign_lines:
            if camera_value.get() == IGNORE_AUDIO:
                continue
            name = name_value.get() or os.path.basename(row[0])
            tracks.append((name, row[0], audio_start(row[0]),
                           audio_clock_of(row[0], state.get("axis_clock"))))
        if not tracks:
            label_say(measure_label, T('No audio tracks are assigned.'),
                      COLOURS["error"])
            return
        begin = min(v for _n, _p, v, _b in tracks)
        tracks = [(n, p, v - begin, b) for n, p, v, b in tracks]
        state["measure_failed"] = False
        state["speakers_measuring"] = True
        measure_line.setVisible(True)
        label_say(measure_label, T('working out who speaks when ...'),
                  COLOURS["quiet"])
        threading.Thread(target=speaker_measure_loop,
                         args=(tracks, bridge, bridge_emit),
                         daemon=True).start()

    measure_line = QtWidgets.QWidget()
    _measure_row = QtWidgets.QHBoxLayout(measure_line)
    _measure_row.setContentsMargins(0, 0, 0, 0)
    measure_label = label("", COLOURS["quiet"])
    measure_label.setWordWrap(True)
    hint(measure_label, T('Works out who speaks when from the tracks '
              'themselves -- one microphone per person, level against its '
              'own noise floor. Where everybody is on one recording, '
              '"several speakers" in the Speaker name field is the way.'))
    _measure_row.addWidget(measure_label, 1)
    cut_column.addWidget(measure_line)
    bridge.speakers_measured.connect(speaker_measure_done)
    bridge.speaker_note.connect(measure_label.setText)
    measure_line.setVisible(False)

    forecast_empty(True)

    def preview_set(text, colour=None):
        preview_label.setTextFormat(Qt.RichText)
        preview_label.setText(text)
        preview_label.setStyleSheet("color: %s" % (colour or COLOURS["value"]))

    def preview_compute():
        # Kept in state at the end of this def: an answer on the
        # assignment sheet has to reach the preview without a run.
        # Preferably the handover file, which holds everything. Failing
        # that the speakers worked out here together with the assignment
        # set above; those are there before the first Resolve run.
        d = None
        state["reason"] = ""
        # The handover of a run, and what it stands on is said out loud
        # further down. Only where there is none does the window work
        # the speakers out for itself.
        d = preview_handover(state)
        if d is None:
            d = off_speakers()
        # A change on the assignment sheet reaches the preview without
        # a run: the file may be older than the answer.
        now = state.get("wide_cameras_now")
        if d is not None and now:
            try:
                on = {}
                for _row, nv, cv in assign_lines:
                    nm = nv.get()
                    if nm and cv.get() not in (MIX_ONLY, IGNORE_AUDIO):
                        on[nm] = cv.get()
                for _label, nv, cv in voice_lines:
                    nm = nv.get().strip()
                    if nm and cv.get() not in (MIX_ONLY, IGNORE_AUDIO):
                        on[nm] = cv.get()
                wides, said = now()
                d = wide_marks_applied(d, wides, on, said)
                # The window is not applied here. It is applied below by
                # apply_time_window, out of start_s -- which is the zero
                # the sections count from. Doing it here as well would
                # move them a second time.
            except RuntimeError:
                # A widget went while we asked it. The rebuild that
                # took it away brings its own answer, so this one goes.
                d = None
        if d is None:
            state["statistics"] = False
            speech_show(None)
            # Without numbers the box stays empty but for the one sentence.
            # Empty table headers promise content that does not exist.
            forecast_empty(True)
            forecast_box.setTitle(T('%s -- preview') % cut_title_of(
                voice_lines, multitrack.get(), assign_lines,
                len(camera_lines)))
            state["cut_numbers"] = None
            band_show(None)
            preview_set(T('No speakers are known yet -- they are worked '
                          'out of the tracks as soon as this tab is opened. '
                          'Where everybody is on one recording, "several '
                          'speakers" in the Speaker name field is the way.'),
                        COLOURS["quiet"])
            preview_label.setToolTip(state.get("reason") or "")
            measure_line.setVisible(bool(state.get("tracks_left")))
            return
        state["statistics"] = True
        # The line stays and says what the cut stands on. Only the
        # button comes and goes: somebody whose track has not been
        # measured is in the cut and not in this picture.
        measure_line.setVisible(True)
        if state.get("tracks_left"):
            measure_label.setText(T('%s not measured yet -- in the cut, '
                                    'not yet in this preview.')
                                  % ", ".join(state["tracks_left"]))
        loaded, bad = slider_numbers(
            {numbers: cut_var[numbers].get() for numbers in cut_var})
        if bad:
            preview_set(T('%r is not a number.')
                            % cut_var[bad].get().strip(),
                            COLOURS["warning"])
            return
        number = {numbers: v[1] for numbers, v in loaded.items()}
        # A manually set time window shifts everything, or the preview would
        # show a cut that will not exist that way.
        d, complaint = apply_time_window(d, start_var.get(), end_var.get())
        if complaint:
            preview_set(complaint, COLOURS["warning"])
            return
        speech_show(d)
        if not (state.get("tracks_left") or state.get("measure_failed")):
            label_say(measure_label, *cut_basis_line(
                state.get("cut_basis"), len(d.get("speakers") or []),
                float(d.get("length_s") or 0.0)))
        window_info_show()
        # The words come with the handover and nowhere else, and the
        # greying belongs here: with the wide shot's it would run
        # before the handover is read and answer from the round before.
        state["words_there"] = bool(words_from_handover(d))
        if state.get("cut_box_there"):
            words_settings_grey(cut_parts, question_note,
                                state["words_there"],
                                bool(wide_cameras_now()[0]), COLOURS["quiet"])
        try:
            numbers = cut_statistics(d, number["min-edit-duration"],
                number["edit-change-delay"], number["wide-after"],
                number["wide-length"], number["wide-latest"],
                bool(edge_on.get()), rules_from_cut_box(
                    number, {k: cut_var[k].get() for k in cut_var}))
        except Exception as e:
            preview_set(T('Preview not possible: %s') % e,
                            COLOURS["warning"])
            return
        if not numbers:
            preview_set(why_no_cut(d), COLOURS["warning"])
            return
        preview_label.setStyleSheet("")
        preview_label.setToolTip("")
        forecast_empty(False)
        try:
            forecast_box.setTitle(T('%s -- preview  (length %s)') % (
                cut_title_of(voice_lines, multitrack.get(),
                             assign_lines, len(camera_lines)),
                as_hms(max(b for _a, b, _w in numbers["cut"]))))
        except Exception:
            pass
        # Where the segments come from belongs with them: self-measured is
        # coarser than what auphonic.com delivers.
        speech_title.setText(speech_heading(
            state.get("stat_measured"), state.get("speech_time_total") or ""))
        state["cut_numbers"] = numbers
        state["cut_data"] = d
        band_show(numbers)
        preview_label.setText(wide_too_short(number)
                              + metrics_sentence(numbers, COLOURS, as_minutes))

    return preview_compute, speaker_measure


def make_speaker_split(QtCore, state, bridge, bridge_emit, plan, files,
                       assign_lines, voice_lines, remembered, split_run,
                       split_line, split_label, split_never, axis_store):
    """Separate the speakers, locally, and say where that stands.

    A third source for the same thing: who speaks when. auphonic.com
    says it from its statistics, speakers_from_tracks measures it where
    every person has a microphone, and this works it out from one
    recording, on this machine, before anything is uploaded. Three
    names built further down in gui() come through *state* rather than
    through a parameter, as state["preview_soon"] already does here.
    """
    # It gets a thread of its own and an entry of its own on the bar,
    # and deliberately no place in the prework count: axis_work_loop
    # waits in "while prework_busy()", and three minutes there would
    # hold up the time axis and the playhead with it.
    def speaker_split_source(alone=False):
        """Which file the separation listens to, and why that one."""
        audio_files = [p for p, a in files if a == "audio"]
        videos = [p for p, a in files if a == "video"]
        # The one derived answer, not the stored one: a camera whose
        # sound is the only sound there is was never clicked, so nothing
        # about it stands in the store.
        return speaker_source_pick(
            audio_files, videos, state.get("own_cameras") or (),
            chosen=state.get("speakers_source_chosen") or "",
            placeless=state.get("no_place") or (), alone=alone)

    def speaker_split_show(text="", colour=None, where=""):
        """Say where the separation stands: in the row of its file.

        What is happening to a recording belongs in the line that shows
        that recording, so the state goes into the Speakers cell of the
        row. Below the table only the one question about the project is
        left, and split_line_write says how rarely it speaks at all.
        *where* names the recording a message belongs to.
        """
        state["split_note"] = ((os.path.abspath(where) if where else "",
                                text, colour or COLOURS["quiet"])
                               if text else None)
        split_line_write(split_line, split_label, split_never,
                         speaker_split_wanted(state.get("speakers_wanted")),
                         split_run["busy"], bool(files))
        split_cells_show()

    def split_cells_show():
        """Write the state of the separation into every file's row."""
        if SPEAKER_SPLIT_OFF:
            return
        if not split_cells_write(state.get("split_cells") or (),
                                 split_run["busy"],
                                 state.get("speakers_running") or "",
                                 state.get("speakers_by") or ByFile(),
                                 state.get("split_note")):
            state["split_cells"] = []

    def speaker_split_note(text, share):
        """Runs in the window thread: the row and the bar together."""
        source = state.get("speakers_running") or ""
        speaker_split_show(text, where=source)
        if source:
            plan.report("speakers:" + source, share)

    bridge.speakers_split_note.connect(speaker_split_note)

    def speaker_split_done(result):
        """The separation came back: keep it, store it, show it."""
        source, count, segments, trouble = result
        split_run["busy"] = False
        plan.done("speakers:" + source)
        state["speakers_running"] = ""
        if trouble:
            speaker_split_show(trouble[:200], COLOURS["error"], where=source)
            return
        if not segments:
            speaker_split_show("", COLOURS["quiet"])
            return
        # The names are an assignment, not a measurement: a voice that
        # already had one keeps it -- its own recording's names. The
        # stand-in counts past every name on the sheet, so a second
        # recording's first voice is not a second "Speaker 1".
        called = dict(speakers_stored(state, source).get("names") or {})
        speakers_keep(state, source, segments, count, dict(
            speaker_label_names(segments, called, sheet_speaker_names(
                assign_lines, voice_lines_here_not(voice_lines, source),
                state.get("voiced") or ()))))
        axis_store(state.get("axis") or {})
        state["assignment_fresh"]()
        speaker_split_show()
        state["preview_soon"]()

    bridge.speakers_split.connect(speaker_split_done)
    bridge.speakers_heard.connect(
        lambda r: speech_words_done(state, r, state["preview_soon"]))

    def speaker_split_kick_off(fresh=False):
        """Start the separation where there is something to separate.

        Nothing is computed again for a moved time window, a new In
        point or a renamed speaker: those are arithmetic on what is
        stored. A different source file, a changed source file or a
        number of speakers set by hand are inputs to the measurement,
        and only they start it over.

        Without *fresh* nobody asked, so the source has to be the only
        one it can be; speaker_source_pick says what that means.
        """
        if split_run["busy"] or not files:
            return
        source, _why = speaker_split_source(alone=not fresh)
        if not source:
            speaker_split_show()
            return
        count = int(state.get("speakers_count") or 0)
        if not fresh:
            if speakers_stored(state, source).get("segments"):
                speaker_split_show()
                return
            if not speaker_split_wanted(state.get("speakers_wanted")):
                speaker_split_show()
                return
        state["speakers_wanted"] = True
        split_run["busy"] = True
        split_run["stop"] = False
        label_run = state.get("speakers_run", 0) + 1
        state["speakers_run"] = label_run
        state["speakers_running"] = source
        # Measured at 28 times real time on the graphics unit, so the
        # share of the bar is known rather than guessed.
        plan.add("speakers:" + source,
                 max(2.0, media_seconds(source) / SPEAKER_SPLIT_SPEED),
                 T('Separating speakers'))
        plan.begin("speakers:" + source, T('Separating speakers'))
        speaker_split_show()
        speaker_split_begin(state, split_run, bridge, bridge_emit,
                            source, count, label_run,
                            state["speech_language"].get())

    def split_stop(_source=""):
        """The one button left in a row: stop listening to it."""
        if not split_run["busy"]:
            return
        split_run["stop"] = True
        speaker_split_show(T('Stopping ...'),
                           where=state.get("speakers_running") or "")

    def voices_stored_for(path):
        """How many voices of this very recording are already here.

        Zero where there are none, so whether and how many are the same
        question. It does not depend on what the row is showing: a row
        that says one person still carries what was measured on it.
        """
        return len(voices_under(path, True, state.get("speakers_by")))

    def voices_of(path):
        """The voices to show under this recording, if any."""
        return voices_under(path, remembered.get("several:" + path),
                            state.get("speakers_by"))

    def several_set(path, on):
        """The name field was answered: several speakers, or one again.

        Switching back hides the rows underneath; it throws nothing
        away. What was measured stays in the project and in the cache,
        so switching forward again is instant and the names and cameras
        given to the voices are still there.
        """
        remembered["several:" + path] = bool(on)
        if on and not voices_stored_for(path) and not SPEAKER_SPLIT_OFF:
            if state.get("speakers_source_chosen") != path:
                # A number of speakers set by hand belongs to the
                # recording it was set for, not to the next one.
                state["speakers_count"] = 0
            state["speakers_source_chosen"] = path
            QtCore.QTimer.singleShot(
                0, lambda: speaker_split_kick_off(fresh=True))
        QtCore.QTimer.singleShot(0, lambda: state["assignment_fresh"]())

    def speaker_split_never():
        """The other button: not on this machine, and remember it."""
        state["speakers_wanted"] = False
        axis_store(state.get("axis") or {})
        speaker_split_show()

    split_never.clicked.connect(speaker_split_never)

    return speaker_split_kick_off, split_stop, voices_of, several_set


def make_band_and_player(Qt, QtCore, QtGui, QtWidgets, QtMultimedia,
                         QtMultimediaWidgets, NoPlayer, state, files,
                         assign_lines, clip_kind_values,
                         forecast_outer, view_player):
    """The cut band, the player below it, and what those two show.

    Both draw the same computed cut and follow one position, so they
    are built together. What the player is fed with is decided in
    gui(), where the cut data stands, and reached back through
    state["player_load_cut"] -- the way state["preview_soon"] is
    already reached from here.
    """
    # The cut band: the computed cut over the full length, one bar per shot in
    # the colour of its camera. The clips in Resolve get the same colours
    # later.
    CutBand = qt_cut_band(QtCore, QtGui, QtWidgets, Qt)
    cut_band = CutBand()
    hint(cut_band, T('Each shot in the colour of its camera. Hover for '
                     'camera and duration, click to jump.'))
    # One label that wraps, not a row of widgets: legend_markup says
    # why, and does the work.
    band_legend = label("", COLOURS["quiet"])
    band_legend.setTextFormat(Qt.RichText)
    band_legend.setWordWrap(True)
    band_legend.setContentsMargins(0, 2, 0, 0)

    def legend_show(numbers):
        """Which colour belongs to which camera."""
        band_legend.setText(legend_markup(numbers))

    def band_show(numbers):
        present = bool(numbers and numbers.get("cut"))
        band_legend.setVisible(present)
        if present:
            end = max(b for _a, b, _w in numbers["cut"])
            cut_band.set(numbers["cut"], numbers.get("colours") or {}, end)
            legend_show(numbers)
        # Built in gui() after this function has handed back the
        # player it feeds, so it cannot be a parameter. The way over
        # is the one preview_soon takes.
        state["player_load_cut"](numbers)

    # The player below. It always shows something: with a cut it plays it and
    # switches camera at every cut; otherwise the file belonging to no speaker,
    # usually the wide shot.
    if QtMultimedia is not None:
        CutPlayer = qt_cut_player(QtCore, QtGui, QtWidgets, Qt,
                                           QtMultimedia, QtMultimediaWidgets,
                                           label, hint, COLOURS)
        cut_player = CutPlayer()
    else:
        cut_player = NoPlayer()
    # Each player silences the other when it starts: two at once are
    # two moments at once, and neither can be judged.
    cut_player.hush = hush_when_running(view_player, "_should_play")
    view_player.hush = hush_when_running(cut_player, "_playing")
    forecast_outer.addWidget(cut_player, 1)
    # Zoom on the band. Over an hour of material a single shot is two
    # pixels wide, and whether a cut sits in a pause or in the middle of
    # a word cannot be seen there at all. In and out by a factor of two
    # around the current position.
    band_row = QtWidgets.QWidget()
    band_line = QtWidgets.QHBoxLayout(band_row)
    band_line.setContentsMargins(0, 0, 0, 0)
    band_line.setSpacing(6)
    band_line.addWidget(cut_band, 1)
    zoom_span = label("", COLOURS["quiet"])
    # The same typewriter digits the player uses for its times below.
    zoom_span.setFont(digits_font(QtGui, zoom_span))

    # Pinned, and measured after the font is set. The reading sits
    # after the buttons and the band takes what is left, so a text that
    # grows pushes the row along -- 104 px at the first zoom, and the
    # button walks out from under the pointer.
    zoom_span.setFixedWidth(caption_room(zoom_span, 0,
                                         ["00:00:00 -- 00:00:00"]))

    def zoom_show():
        zoom_span.setText(cut_band.zoom_text())

    band_line.addWidget(zoom_button(
        QtWidgets, "\u2212", T('Show twice as much (minus key, or the wheel over '
                    'the band)'), lambda: cut_band.zoom(2.0)))
    band_line.addWidget(zoom_button(
        QtWidgets, "+", T('Show half as much, around the current position (plus '
               'key, or the wheel over the band)'),
        lambda: cut_band.zoom(0.5)))
    band_line.addWidget(zoom_button(
        QtWidgets, "\u25ad", T('The whole length again (0 key)'),
        lambda: cut_band.zoom_all()))
    band_line.addWidget(zoom_span)
    cut_band.zoomed.connect(zoom_show)
    # Once here, or it stands empty until somebody zooms: the signal
    # above fires on a change, and nothing has changed yet.
    zoom_show()

    # The band takes the place of the position rail: it shows the same time
    # plus which camera runs when. The legend stays below.
    if hasattr(cut_player, "replace_rail"):
        cut_player.replace_rail(band_row)
    else:
        forecast_outer.addWidget(band_row)
    forecast_outer.addWidget(band_legend)

    def band_spot_chosen(t):
        state["band_spot"] = t
        cut_band.label_set(t)
        try:
            cut_player.jump(t)
        except Exception:
            pass

    cut_band.selected.connect(band_spot_chosen)
    if hasattr(cut_player, "position_changed"):
        cut_player.position_changed.connect(cut_band.label_set)
        cut_player.position_changed.connect(lambda *_: zoom_show())

    def preview_file():
        """What is shown while there is no cut.

        The file assigned to no speaker, which is the wide shot. Failing that,
        the first one that is neither intro nor outro.
        """
        videos = [p for p, a in files
                  if a == "video"
                  and (p not in clip_kind_values
                       or clip_kind_values[p].get() in CAMERA_TYPES)]
        if not videos:
            return None
        taken = set()
        for _chain, _nv, cv in assign_lines:
            if cv.get() not in (MIX_ONLY, IGNORE_AUDIO):
                taken.add(cv.get())
        free = [b for b in videos if os.path.basename(b) not in taken]
        return (free or videos)[0]

    return cut_band, cut_player, band_show, preview_file


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

    Whatever is needed from gui() comes in as an argument and keeps its
    name inside. The widgets are made here and hung into the layout
    handed in; the lists and dictionaries belong to the window and are
    emptied at the start of every rebuild. Two names bound further down
    in gui() come through *state*, as state["preview_soon"] already does.
    """
    assignment_remember()
    for p in forget:
        remembered.pop("video:" + p, None)
    # Between the old table going and the new one arriving is a
    # moment with nothing in it, and Qt paints it: a flash, as if a
    # window had opened. Painting waits for the next turn of the
    # loop, when the new table stands.
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
    # Cleared with the rest: the voices belong to the tree that
    # has just gone, and a row that no longer exists must not
    # still be able to say which camera it is on.
    voice_lines[:] = []
    file_rows[:] = []
    state["split_cells"] = []
    state["voiced"] = set()
    audio_fields[:] = []
    video_fields[:] = []
    # The two lines carrying a reason are widgets of that table
    # too. Left pointing at the old ones, the next check writes
    # into something Qt has deleted -- a crash, not a mark.
    state["audio_reason"] = None
    state["video_reason"] = None
    audio_files = [p for p, a in files if a == "audio"]
    videos = sorted([p for p, a in files if a == "video"],
                    key=lambda x: os.path.basename(x).lower())
    # A camera contributing its audio is an input track like any other, so
    # it is in the same table above. The dictionary is the window's and
    # is emptied here: a rebuild starts over.
    own_audio_names.clear()
    # What a cut-out piece is called: the label the cutting gave it,
    # "Camera 1" and "Camera 2" for two clip-on microphones on one
    # camera. Without it the piece would be named after its file, which
    # carries the channel number and not the person.
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
              'a video file\'s Camera audio to "use the audio" in the '
              'file list.'), COLOURS["quiet"]))
        # Before the exit, not after the table: the time axis is
        # measured over the envelope of every file and is needed
        # whether or not any sound is in use. Leaving here first
        # would take a project its time axis.
        if videos:
            prework_kick_off(list(videos))
        # And the button, for the same reason: the way in here is
        # also taking the last sound away, and then it stood
        # enabled with an empty reason beside it.
        assignment_check()
        return
    # The cameras first, then the two special cases. MIX_ONLY means the
    # track is processed and in the mix but is not the first track on any
    # camera. IGNORE_AUDIO leaves it out entirely -- useful where the
    # matching video is still missing.
    targets = ([os.path.basename(b) for b in videos]
             + [MIX_ONLY, IGNORE_AUDIO])
    wide = wide_bar_of(targets, *wide_cameras_now(),
                       aside=state.setdefault("wide_set_aside", {}))
    barred = wide["barred"]
    head = T('Audio recording')
    belongs_head = T('belongs to')
    # The column for the separation is only there where there is a
    # separation to have: with it switched off it would be a column
    # of empty cells offering something the program cannot do.
    # It no longer holds a button -- asking for the voices to be
    # told apart is an answer in the name field of the same row --
    # only what came of it, and a way to break off while it runs.
    columns = [head, T('Speaker name'), belongs_head, "Timecode"]
    if not SPEAKER_SPLIT_OFF:
        columns.append(T('Speakers'))
    tree_audio = tree_build(columns)
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
    state["without_tc"] = without_tc
    if not without_tc:
        state["tc_there"] = True
    for (row, _) in chains:
        first = row[0]
        camera_track = os.path.abspath(first) in state["own_audio_rows"]
        from_camera = state["own_audio_rows"].get(first) \
            if isinstance(state["own_audio_rows"], dict) else None
        stem = (guess_camera_name(from_camera or first)
                 if camera_track else guess_speaker_name(first))
        # So the two rows of one camera can be told apart.
        if piece_label.get(first):
            stem = piece_label[first]
        if camera_track:
            stem = remembered.get("ownname:" + first) or stem
        caption = os.path.basename(first)
        if camera_track:
            caption += T('   (camera audio)')
        elif len(row) > 1:
            caption += "  (+%d)" % (len(row) - 1)
        node = tree_row(tree_audio, None, [caption])
        node[0].setData(first, Qt.UserRole + 1)
        audio_file_list.append(first)
        file_rows.append((node, first, caption))
        old_name, old_camera = remembered.get("audio:" + first, (None, None))
        # Empty until somebody answers, with the guess offered in
        # grey and never written in. The field itself knows both,
        # so no reader of it has to.
        name_value = SpeakerName(old_name or "", stem)
        # The voices this recording is showing. Where there are any,
        # the assignment belongs to them and not here: two answers
        # one above the other could contradict each other, and the
        # rule is that the assignment has exactly one level.
        kids = voices_of(first)
        if kids:
            state["voiced"].add(os.path.abspath(first))
        if SPEAKER_SPLIT_OFF:
            # Nothing can be told apart on this machine, so there is
            # only one answer to give and a plain field to give it in.
            name_field = field_bind(QtWidgets.QLineEdit(), name_value)
            speaks_as(name_field, T('Speaker name'), caption)
        else:
            # Only an answer picks the answer. What was found used
            # to do it, so a separation that came back with four
            # voices set the field to "several speakers" without
            # anybody saying so.
            said = remembered.get("several:" + first)
            several_value = Value(bool(said))
            several_value.listen(
                lambda *_, p=first, v=several_value: several_set(
                    p, v.get()))
            name_field = speaker_name_cell(name_value, several_value,
                                           caption)
        tree_field(tree_audio, node, 1, name_field)
        row_picker_watch(state["row_picker"], name_field)
        # Before the branch below, so that a row without a selector
        # says how its separation stands too: whether a recording is
        # spread over every camera has nothing to do with who is
        # heard on it.
        if not SPEAKER_SPLIT_OFF:
            box_, cell_ = split_cell_build(first, split_stop, node[4])
            tree_field(tree_audio, node, 4, box_)
            state["split_cells"].append(cell_)
        # The voices go under the row before the row is filled in:
        # whether this recording has any is what decides what it
        # carries itself.
        if voices_build(tree_audio, node, first, videos, targets, wide):
            tree_audio.setExpanded(node[0].index(),
                                   tree_open.get(first, True))
            folded_show(node[0].index())
        # Where the voices hang underneath, the rows below carry the
        # cameras and this row carries none -- the assignment has
        # exactly one level. The cell says so instead of standing
        # empty, which left the reader to work it out. The Multitrack
        # tick does not come into it: which camera a recording belongs
        # to is the same question with the tick and without it.
        if kids:
            tree_cell(node, 2, T('the voices below carry the cameras'),
                      COLOURS["quiet"])
            # MIX_ONLY is the truth here: no track belongs to one camera
            # alone.
            assign_lines.append((row, name_value, Value(MIX_ONLY)))
            continue
        # Camera rows get the full selector too. A clip-on microphone
        # plugged into one camera does not mean the person is filmed by
        # that camera -- two microphones on one camera are usually two
        # people sitting in front of two others. The camera the audio
        # came from is only the preselection.
        own_camera = (os.path.basename(from_camera or first)
                      if camera_track else "")
        was = camera_after_a_mark("audio:" + first, old_camera, wide,
            name_value.get() or os.path.basename(first))
        picked, worked_out = camera_row_cameras(
            was, wide["pickable"], name_value.get(), videos,
            own_camera="" if own_camera in barred else own_camera)
        camera_value = Value(MIX_ONLY if picked in barred else picked)
        camera_value.derived = worked_out
        box = QtWidgets.QComboBox()
        speaks_as(box, belongs_head, caption)
        fill_choices(box, targets, camera_value.get())
        choices_shut(box, barred, wide["why"], COLOURS["quiet"])

        def chosen(_i=0, b=box, value=camera_value, f=name_field):
            """Hand the value on; an ignored track needs no name."""
            v = b.currentData()
            value.set(v)
            f.setEnabled(v != IGNORE_AUDIO)

        box.currentIndexChanged.connect(chosen)
        chosen()
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
    # A voice the separation missed is still asked for below the
    # tree: it is not a row of the tree but the input to another
    # separation, and it belongs to no one recording in particular.
    more = more_speakers_row(audio_file_list, voice_add)
    if more is not None:
        column_layout.addWidget(more)
    audio_reason = label("", COLOURS["error"])
    audio_reason.setWordWrap(True)
    audio_reason.setVisible(False)
    column_layout.addWidget(audio_reason)
    state["audio_reason"] = audio_reason
    # The rows that carry a file, which is not every row: the
    # timecode and the "does not fit" mark belong to a recording,
    # and a voice has neither.
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
    # What comes out, and the two decisions that can only be made
    # after watching: what the clip is, and whether its sound is
    # material. Both stand in the file list as well, on the same
    # value -- that a clip is in truth an outro is noticed in the
    # player, and the player is here.
    table_video = table_build([T('Camera'), T('new file name'),
                               T('gets audio from'), T('Kind'),
                               T('Camera audio')])
    column_layout.addWidget(table_video, 1)
    video_reason = label("", COLOURS["error"])
    video_reason.setWordWrap(True)
    video_reason.setVisible(False)
    column_layout.addWidget(video_reason)
    state["video_reason"] = video_reason
    taken = {}
    for _, nv, cv in assign_lines:
        taken.setdefault(cv.get(), []).append(nv)
    wides, said = wide_cameras_now()

    def kinds_refresh():
        """Say the Kind column again, with the wide shot as it is now.

        A voice given a name and a camera makes that camera one
        somebody sits in front of, so it is no longer the derived
        wide shot. The table is built before that answer exists.

        Both tables that show a Kind, not only this one: the file
        list on the first tab shows the same derivation, and left
        out it goes on saying "Wide shot" for every camera while
        this one says something else.
        """
        if state.get("closing"):
            return
        video_kinds_again(video_kind_again)
        try:
            fresh, marked = wide_cameras_now()
            for i, path in enumerate(videos):
                if i >= table_video.rowCount():
                    break
                box_cell, _box = kind_cell_for(
                    path, clip_kind_value(path), fresh, marked,
                    state.get("no_place"), clip_kind_values,
                    COLOURS["quiet"], lambda q=path: kind_answered(q))
                table_video.setCellWidget(i, 3, box_cell)
        except RuntimeError:
            # The table was rebuilt under us; the new one is right.
            return

    state["kinds_refresh"] = kinds_refresh
    for row, b in enumerate(videos):
        short = os.path.basename(b)
        table_video.insertRow(row)
        cell(table_video, row, 0, short)
        clip_kind = clip_kind_value(b)
        kind_cell, _kind_box = kind_cell_for(
            b, clip_kind, wides, said, state.get("no_place"),
            clip_kind_values, COLOURS["quiet"],
            lambda p=b: kind_answered(p))
        table_video.setCellWidget(row, 3, kind_cell)
        own_audio = audio_use_value(b)
        used, why = audio_use_settled(b, own_now, forced,
                                      has_sound(b), clip_kind.get())
        if clip_kind.get() not in CAMERA_TYPES:
            # A finished clip has nothing to assign and gets no new name --
            # it is used directly. Rather than offering empty fields that
            # do nothing, a sentence is there instead. Its Camera audio
            # is built all the same, greyed out with the reason beside
            # it: "a finished clip -- only placed, not processed" is
            # the answer to the question the field raises, and a blank
            # cell answers nothing.
            cell(table_video, row, 1,
                  T('stays out') if clip_kind.get() == TYPE_IGNORED
                  else T('used directly'),
                  COLOURS["quiet"])
            cell(table_video, row, 2, "")
            sound_off, sound_off_box = camera_audio_cell(
                short, used, why, COLOURS["quiet"], True)
            audio_use_bind(sound_off_box, own_audio, why)
            table_video.setCellWidget(row, 4, sound_off)
            continue
        # A camera can contribute its own audio too -- the wide shot with
        # the room microphone, say, or where somebody has no recording of
        # their own. It is then a track like any other: with a speaker
        # name, it goes up, gets processed and is in the mix.
        # One camera can give more than one track: two clip-on
        # microphones on two channels are two speakers, and both names
        # belong in the file name of that camera.
        mine = own_audio_names.get(b) or []
        own_audio_name = mine[0] if mine else Value(
            remembered.get("ownname:" + b) or guess_camera_name(b))
        own = list(taken.get(short) or [])
        if used:
            own += mine or [own_audio_name]
        suggestion = camera_name_suggestion(production_var.get(),
                                            short, own)
        suggestions[b] = suggestion
        name_value = Value(remembered.get("video:" + b) or suggestion)
        name_entry = field_bind(QtWidgets.QLineEdit(), name_value)
        speaks_as(name_entry, T('new file name'), short)
        from_the_front(name_entry)
        table_video.setCellWidget(row, 1, name_entry)
        cell(table_video, row, 2, camera_gets_from(short, wide, own),
             COLOURS["quiet"])
        # The file list's field again, on the same value: it stands
        # here because the player does, and usable sound is heard.
        sound, sound_box = camera_audio_cell(short, used, why,
                                             COLOURS["quiet"], True)
        audio_use_bind(sound_box, own_audio, why)
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
    # content. The first column of the tree carries the triangles and the
    # indentation as well, so it is measured with room for both.
    tree_audio.setColumnWidth(0, max(220, tree_audio.columnWidth(0) + 30))
    # The new file name is long, so it gets whatever is left.
    table_video.horizontalHeader().setStretchLastSection(False)
    table_video.horizontalHeader().setSectionResizeMode(
        1, QtWidgets.QHeaderView.Stretch)
    tree_audio.header().setStretchLastSection(True)
    if not SPEAKER_SPLIT_OFF:
        # A width for what the column will hold, not for what is in
        # it: it is written to minutes later, and a column that
        # measures its contents measured an empty one. The room
        # left over goes to the name field, which scrolls its own.
        split_column_fit(tree_audio, 4)
    # The camera list now stands, so queue what can be prepared: the
    # envelope for every camera, plus the camera audio for those
    # contributing it.
    window_prefill(videos)
    window_enable()
    show_weak()
    main_track_show()
    every_cameras = [p for p, _n, _k, _own_name in camera_lines]
    # Every camera goes in either way -- the time axis lives on those
    # envelopes. Only the second task, fetching the sound itself, is
    # for the ones whose audio was set to "use".
    having_audio = [p for p in every_cameras if p in own_now]
    # The audio recordings belong in it: the time axis needs their
    # envelopes just as much, and the bar should show that they are being
    # worked on.
    # Every block, not only the row's first: a recording made of three
    # blocks has to be measured and the In point all three.
    every = list(every_cameras)
    for r, _nv, _cv in assign_lines:
        for x in r:
            if x not in every:
                every.append(x)
    if every:
        prework_kick_off(every, having_audio)
    # Beside the prework, not behind it: the two do not slow each
    # other down, and the separation is the long one of the two.
    speaker_split_kick_off()
    assignment_check()
    assignment_state_show()
    # The last camera to be given a speaker takes the wide shot away.
    state["wide_state_show"]()
    # And the file list says so too. It is built when the files come
    # in, which is before anybody is assigned, and the Kind it shows
    # is derived from exactly that -- so without this the first tab
    # goes on calling every camera the wide shot while the table
    # above says something else.
    video_kinds_again(video_kind_again)

def make_footer(Qt, QtCore, QtWidgets, window, vertical, state, files,
                plan, bridge, late, multitrack, without_auphonic,
                settings_open):
    """The bottom row of the window: the one bar, and the four buttons.

    Outside gui() because it is one strip answered end to end -- the bar
    for the whole run, the plan behind it that says what each stage is
    worth, and the buttons that start, try, stop and set up. What goes
    into the log while the run lasts belongs to the run, so the break-off
    reaches back through state["write"]: the writer is made further down
    in gui(). Qt comes in as a parameter, imported inside gui().
    """
    # Above the buttons, not under them: a line below the bottom row
    # reads like a footnote to the window rather than the answer to
    # "why can I not press this". Decided 30.8.2026.
    start_note = label("", COLOURS["quiet"])
    vertical.addWidget(start_note)
    foot = QtWidgets.QHBoxLayout()
    vertical.addLayout(foot)
    total_bar = QtWidgets.QProgressBar()
    total_bar.setRange(0, 1000)
    total_bar.setTextVisible(False)
    total_bar.setFixedHeight(12)
    # Wide enough to read a share off it. The bar grows with the window
    # instead of standing at a fixed 170 px: measured, the stretch behind
    # it took every spare pixel, so the bar stayed at its minimum however
    # wide the window was. The stretch factor below lets it take the
    # larger part of the free space, the maximum keeps it from running
    # across a very wide screen and pushing the reason for a grey Start
    # button out of sight.
    total_bar.setMinimumWidth(220)
    total_bar.setMaximumWidth(620)
    hint(total_bar, T('Everything still outstanding, measured against '
                      'what is done. Long pieces of work take up more of '
                      'the bar than short ones.'))
    total_line = label("", COLOURS["quiet"])
    foot.addWidget(total_bar, 3)
    foot.addWidget(total_line, 1)
    total_bar.hide()
    total_line.hide()
    total_state = {"full_since": 0.0}

    run_step_order = []

    def plan_wipe():
        total_hide(plan, total_state, total_bar, total_line)

    def run_plan_build():
        """Announce the stages of the run before it starts.

        The whole job at once, not stage by stage: a bar that only learns
        of the next stage when the last one ends jumps backwards at every
        boundary and tells nobody anything.

        The plan before it is thrown away, finished or still going.
        Pressing start while the measuring after a project still ran
        added the run to what was there; the bar then stood still for
        two stages at 0.500, because it never falls and the truth had
        to climb back to it. Standing still says the wrong thing as
        surely as falling back. Safe, because report() puts an unknown
        step back -- see tests/progress_plan_test.py.
        """
        plan_wipe()
        cameras = len([1 for p, a in files if a == "video"])
        stages = run_stages(bool(multitrack.get()), cameras,
                            not without_auphonic(),
                            speakers=bool(multitrack.get()
                                          or state.get("speakers_local")))
        run_step_order[:] = [name for name, _w, _c in stages]
        for name, weight, caption in stages:
            plan.add("run:" + name, weight, caption)

    def run_step_take(name, share):
        """One stage of the run reports. Runs in the window thread.

        A stage beginning means every earlier one is over, whether it ran
        or was skipped -- with auphonic.com the speaker detection never
        happens, and a step left at nothing would hold the bar back for
        the rest of the job.
        """
        if name not in run_step_order:
            plan.add("run:" + name, 1.0, name)
            run_step_order.append(name)
        if share < 0:
            for earlier in run_step_order[:run_step_order.index(name)]:
                plan.done("run:" + earlier)
            plan.begin("run:" + name)
            return
        plan.report("run:" + name, share)

    bridge.run_step.connect(run_step_take)

    def total_show():
        """Refresh the one bar. A timer calls this, not the work.

        The work reports from several threads and at very different
        rates; letting each report redraw would mean either a bar that
        stutters or one that stands still for a minute at a time.
        """
        try:
            total_paint(Qt, plan, total_state, total_bar, total_line)
        except RuntimeError:
            # The window is closing and the widgets are already gone.
            # A timer still firing into them must not turn into a
            # traceback on the way out.
            total_clock.stop()

    total_clock = QtCore.QTimer(window)
    total_clock.timeout.connect(total_show)
    total_clock.start(200)
    foot.addStretch(1)
    # Only the Resolve part: after a run, or where a handover file from earlier
    # is already in the output folder. Then nothing has to be recomputed -- one
    # looks at the result and creates the project after.
    start_run = QtWidgets.QPushButton(T('Start'))
    start_run.setEnabled(False)
    hint(start_run, T('Measure, align, process, write files.'))
    # Both run buttons sit in a frame of their own: it is what makes the
    # tooltip of a switched-off button reachable at all, and it is what
    # keeps the two standing on one line. button_in_a_frame says why.
    start_run_env_curve = button_in_a_frame(QtWidgets, start_run)
    foot.addWidget(start_run_env_curve)
    preview_button = QtWidgets.QPushButton(T('Dry run'))
    preview_button.setEnabled(False)
    hint(preview_button,
            T('Measure only -- nothing is written or uploaded.'))
    foot.addWidget(button_in_a_frame(QtWidgets, preview_button))
    break_off = break_off_button(QtWidgets, state, lambda t: state["write"](t))
    foot.addWidget(break_off)
    # The two run buttons are one pair and switch off the same way: both
    # keep their shape and fade into the same muted blue. The rank stays
    # readable -- the main action is filled, the dry run only outlined --
    # but neither of them looks pressable while it is off.
    start_run.setStyleSheet(
        "QPushButton { background: %s; color: %s; font-weight: bold; "
        "border: 1px solid %s; border-radius: 5px; padding: 6px 21px; }"
        "QPushButton:disabled { background: %s; color: %s; "
        "border-color: %s; }"
        "QPushButton:hover:!disabled { background: %s; border-color: %s; }"
        % (COLOURS["heading"], COLOURS["sheet"], COLOURS["heading"],
           COLOURS["off"], COLOURS["off_text"], COLOURS["off"],
           COLOURS["value"], COLOURS["value"]))
    preview_button.setStyleSheet(
        "QPushButton { background: %s; color: %s; "
        "border: 1px solid %s; border-radius: 5px; padding: 6px 17px; }"
        "QPushButton:disabled { background: transparent; color: %s; "
        "border-color: %s; }"
        "QPushButton:hover:!disabled { background: %s; }"
        % (COLOURS["box"], COLOURS["heading"], COLOURS["heading"],
           COLOURS["off_text"], COLOURS["off"], COLOURS["backdrop"]))
    # Settings belongs with the buttons, not beside the tabs: it is not
    # a step of the work, so it stays flat and keeps its distance, but
    # the footer is where a button is looked for.
    settings_button = QtWidgets.QPushButton(T('Settings ...'))
    settings_button.setFlat(True)
    hint(settings_button, T('Key for auphonic.com, and whether Resolve '
                            'answers.'))
    settings_button.clicked.connect(lambda: settings_open())
    foot.addSpacing(18)
    foot.addWidget(settings_button)
    row_same_height([start_run, preview_button, break_off, settings_button])

    # In full and in view: a tooltip is out of reach for the keyboard.
    start_note.setWordWrap(True)
    start_note.setVisible(False)
    # Named so it can be found: the test looks for this line, and a
    # reading program announces it by name rather than as "label".
    start_note.setObjectName("start_note")
    start_note.setAccessibleName(T('Why the run cannot start'))
    late["start_note"] = start_note
    return (start_run, start_run_env_curve, preview_button, break_off,
            plan_wipe, run_plan_build, run_step_order, total_clock)


def make_file_list(Qt, QtGui, QtWidgets, sheet1_position, state):
    """Tab 1: the list of chosen files, with its stripes and its marks.

    Outside gui() because it is the widget and nothing else: the tree
    with its five columns, what a file dropped on it does, the sentence
    under it that the check writes into, the two colour tables refilled
    when the desktop changes, and the maker of a single row. A dropped
    file reaches take_paths through state, which gui() fills in further
    down -- what goes into the list is decided there, not here.
    """
    items = QtWidgets.QTreeWidget()
    items.setColumnCount(5)
    # Column 0 carries the file name and the tree structure, column 1 the check
    # mark, column 2 the value. The mark cannot go in column 0: indentation and
    # the expand arrow sit in front of it there.
    # Columns 3 and 4 are the two decisions a video file carries: what it
    # is, and whether its sound is material. Both are about the material
    # itself, so they stand where the material is listed.
    items.setHeaderLabels([T('File'), "", "", T('Kind'), T('Camera audio')])
    # Not uniform: those two hold drop-downs, and a drop-down is taller
    # than a line of text. Uniform gives every row the first row's height
    # and the fields come out squashed.
    items.setUniformRowHeights(False)
    items.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Interactive)
    items.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
    items.header().setStretchLastSection(False)
    for _c, _how in ((2, QtWidgets.QHeaderView.Stretch),
                     (3, QtWidgets.QHeaderView.ResizeToContents),
                     (4, QtWidgets.QHeaderView.ResizeToContents)):
        items.header().setSectionResizeMode(_c, _how)
    items.setColumnWidth(0, 420)
    items.setColumnWidth(1, 26)
    items.setAcceptDrops(True)
    items.setDragDropMode(QtWidgets.QAbstractItemView.DropOnly)
    speaks_as(items, T('Chosen files'))
    sheet1_position.addWidget(items, 1)

    def _list_takes(e):
        paths = [u.toLocalFile() for u in e.mimeData().urls()
                 if u.isLocalFile()]
        if paths:
            e.acceptProposedAction()
            state["take_paths"](paths)

    # Dropping onto the full list works too -- somebody who already has files
    # and adds one is not looking for a button.
    items.dragEnterEvent = _list_accepts
    items.dragMoveEvent = _list_accepts
    items.dropEvent = _list_takes

    # Below the list, one sentence on what the check found. The details are
    # marks in the first column; whoever wants more hovers over them or expands
    # the file.
    preflight_line = label("", COLOURS["quiet"])
    preflight_line.setWordWrap(True)
    preflight_line.setVisible(False)
    sheet1_position.addWidget(preflight_line)

    # The stripes of the file list: light on light, dark on dark. They should
    # structure the rows, not outshine them.
    SHADES = {}

    def stripes_pick():
        """Fill the stripes of the file list for this desktop.

        Refilled in place, and read off ON_DARK rather than asking the
        desktop a second time: two independent answers to the same
        question drift apart the moment one of them is refreshed.
        """
        SHADES.clear()
        SHADES.update({"group": QtGui.QColor("#2f3b49"),
             "audio": QtGui.QColor("#28313c"),
             "video": QtGui.QColor("#332f27"),
             "block": QtGui.QColor("#262b31")}
            if ON_DARK[0] else
            {"group": QtGui.QColor("#d9e2ec"),
             "audio": QtGui.QColor("#eef4fa"),
             "video": QtGui.QColor("#f3f0e8"),
             "block": QtGui.QColor("#f7f7f7")})

    stripes_pick()

    def line_colourise(item, kind, bold=False):
        brush = QtGui.QBrush(SHADES[kind])
        for column in range(items.columnCount()):
            item.setBackground(column, brush)
            if bold:
                s = item.font(column)
                s.setBold(True)
                item.setFont(column, s)
        return item

    # What goes in the first, narrow column. A mark says more than a line of
    # text as long as there are only three of them.
    MARKS = {}

    def marks_pick():
        """Fill the marks of the first column with today's colours."""
        MARKS.clear()
        MARKS.update({"good": ("\u2713", COLOURS["good"]),
                      "hint": ("!", COLOURS["error"]),
                      "fixed": ("\u2713", COLOURS["good"]),
                      "abort": ("\u2715", COLOURS["error"])})

    marks_pick()
    # What a finding is called when it appears as its own row under the file.
    FINDING_WORD = {"hint": T('Note'), "fixed": T('fixed'),
                   "abort": T('Caution')}

    def set_mark(node, kind, text=""):
        """Give the file its check mark."""
        how = MARKS.get(kind)
        if not how:
            return
        if kind in ("hint", "abort"):
            trouble_log("%s -- %s" % (node.text(0) or "?", text or kind))
        node.setText(1, how[0])
        node.setForeground(1, QtGui.QBrush(QtGui.QColor(how[1])))
        node.setTextAlignment(1, Qt.AlignCenter)
        font = node.font(1)
        font.setBold(True)
        node.setFont(1, font)
        if text:
            for column in (0, 1, 2):
                node.setToolTip(column, text)

    def item(parent, text, value="", kind=None, bold=False, files_for_it=None,
               group_kind=None):
        p = QtWidgets.QTreeWidgetItem(parent, [text, "", value])
        if kind:
            line_colourise(p, kind, bold)
            # Kept, not only painted: Remove has to tell a single block
            # of a recording from the recording itself.
            p.setData(0, Qt.UserRole + 3, kind)
        if files_for_it is not None:
            p.setData(0, Qt.UserRole, list(files_for_it))
        if group_kind:
            p.setData(0, Qt.UserRole + 1, group_kind)
        return p

    return (items, preflight_line, stripes_pick, marks_pick, MARKS,
            FINDING_WORD, set_mark, item)


def app_language_set(QtCore, Qt, app):
    """Give Qt its own words, and turn the window the way they read.

    One door, because both answer the same question -- what language
    this is. On the application, where Qt puts the direction itself
    when it finds its own Arabic, so a machine whose Qt brings none
    gets the same window as one whose Qt does. Set either way round,
    or a second window in one process finds the first one's still up.
    """
    qt_own_words(QtCore, app)
    app.setLayoutDirection(Qt.RightToLeft if reads_right_to_left(PROGRAM.LANG)
                           else Qt.LeftToRight)


#----------------------------------------------------- The window itself
# One function, and the largest in the program. What could be
# lifted out of it stands above and below; what is left holds the
# widgets it builds and reaches for them by closure.


def gui():
    """Build the Qt interface.

    Three tabs in the order they are needed: choose files, configure, watch.
    Tabs two and three appear only once they have something to show -- an empty
    form helps nobody.

    The actual work is done by the same main() as on the command line; the
    interface only assembles the arguments and captures the output.
    """
    import queue
    _require_module("PySide6.QtWidgets", "PySide6")
    from PySide6 import QtCore, QtGui, QtWidgets

    Qt = QtCore.Qt
    Cursor = QtGui.QTextCursor

    PROGRAM.GUI_RUNNING = True

    # The ffmpeg backend of Qt would otherwise print the whole format block to
    # the console for every file loaded.
    os.environ.setdefault("QT_LOGGING_RULES",
                          "qt.multimedia.ffmpeg*=false;qt.multimedia*=false")
    mac_menu_name("Video Podcast Magic")   # before the menu bar is built
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv[:1])
    app.setApplicationName("Video Podcast Magic")
    app.setApplicationDisplayName("Video Podcast Magic")
    app_language_set(QtCore, Qt, app)

    # With the system in dark mode the same roles get dark shades. Otherwise a
    # white box would stand in a dark window, and the lists Qt draws itself
    # would be black.
    colours_pick(desktop_is_dark(QtWidgets, QtGui))

    # Only a few places get an appearance of their own: boxes, the tab bar and
    # the start button. Everything else stays as the system draws it, which
    # looks right on every machine.

    app_style_set(app)

    window = QtWidgets.QWidget()
    window.setWindowTitle(window_title())
    symbol = app_icon(QtGui)
    if symbol is not None:
        # On the Mac the dock icon belongs to the application, not to the
        # window, or the Python rocket appears there.
        app.setWindowIcon(symbol)
        window.setWindowIcon(symbol)

    files = []                      # [(path, "audio"|"video")]
    state = {"running": False, "results": [], "presets": None,
               "resolve_json": None, "result_folder": None,
               "camera_audio": False, "waiting": False, "without_tc": False,
               "assignment_content": None, "statistics": False,
               "in_point": "", "out_point": "", "axis": {}, "tc_there": False,
               "weak": set(), "tables": [], "axis_absolute": False,
               "axis_clock": {}}
    post = queue.Queue()

    # ------------------------------------------------------------------
    # Bridge: what arises in a worker thread must not reach the window from
    # there. Qt passes signals into the right thread by itself, so everything
    # from the threads goes through here.
    # ------------------------------------------------------------------
    class Bridge(QtCore.QObject):
        progress = QtCore.Signal(str, str, float, str)
        question = QtCore.Signal(object)
        # The key the answer is about travels with it: read off the
        # field again when the answer lands, it may be a second one
        # somebody pasted while the first was still on its way.
        presets = QtCore.Signal(object, str, str)
        axis = QtCore.Signal(object, str)
        preflight = QtCore.Signal(object)
        resolve_check = QtCore.Signal(object)
        speakers_measured = QtCore.Signal(object)
        run_step = QtCore.Signal(str, float)
        channels_done = QtCore.Signal(str)
        split_done = QtCore.Signal(str)
        speaker_note = QtCore.Signal(str)
        speakers_split = QtCore.Signal(object)
        speakers_split_note = QtCore.Signal(str, float)
        speakers_heard = QtCore.Signal(object)

    bridge = Bridge()

    def bridge_emit(signal, *values):
        """Send a signal from a working thread, if there is still a window.

        A thread that finishes while the window is closing would be
        emitting into an object Qt has already deleted. That raises, and
        the traceback reads like a crash although nothing was lost.
        """
        if state.get("closing"):
            return
        try:
            signal.emit(*values)
        except RuntimeError:
            pass

    def report(title, text):
        """Show a message with a button that says what it does."""
        say_dialog(QtWidgets, window, title, text)

    def ask(title, text, do_text, no_text=T('Cancel')):
        """Ask a question and report whether the action was chosen."""
        return say_dialog(QtWidgets, window, title, text, do_text, no_text)

    # ------------------------------------------------------------------
    # Play it -- Qt brings a player along
    # ------------------------------------------------------------------
    try:
        from PySide6 import QtMultimedia, QtMultimediaWidgets
    except ImportError:
        QtMultimedia = QtMultimediaWidgets = None

    def ffplay_preview(file_path, seconds, only_audio=False):
        """Fallback: Qt cannot play some camera formats."""
        command = ["ffplay", "-autoexit", "-alwaysontop", "-loglevel", "error",
                  "-ss", "%.2f" % max(0.0, seconds), "-t", "10",
                  "-window_title", os.path.basename(file_path)]
        if os.environ.get("VPM_SILENT"):
            command += ["-volume", "0"]
        if only_audio or os.path.splitext(file_path)[1].lower() in AUDIO_SUFFIXES:
            command += ["-showmode", "1", "-x", "640", "-y", "240"]
        command.append(file_path)
        try:
            subprocess.Popen(command, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        except OSError:
            report(T('Playback not possible'),
                   T('This file cannot be played here, and ffplay is '
                     'missing as a fallback.'))

    # The preview building blocks live outside; real_tc only exists further
    # down, hence a late-binding wrapper.
    (WindowSlider, VideoSurface, Player, NoPlayer) = make_player_widgets(
        QtCore, QtGui, QtWidgets, Qt, label, hint, ffplay_preview,
        lambda *a, **k: real_tc(*a, **k), state)

    # ------------------------------------------------------------------
    # The one bar
    #
    # Measuring runs in the background and across every tab, and a bar
    # that lives on one page is invisible exactly when it matters. This
    # plan collects every outstanding piece of work; its bar sits in the
    # footer, beside Start. Declared here because the pieces that feed it
    # are built long before the footer is.
    # ------------------------------------------------------------------
    plan = ProgressPlan()

    # ------------------------------------------------------------------
    # Layout: header, tabs, footer
    # ------------------------------------------------------------------
    vertical = QtWidgets.QVBoxLayout(window)
    vertical.setContentsMargins(12, 10, 12, 10)
    vertical.setSpacing(8)

    # No header line: name, version and purpose are in the window title. A few
    # pixels of air remain so the top edge of the tabs is visible.
    vertical.addSpacing(4)

    tabs = QtWidgets.QTabWidget()
    vertical.addWidget(tabs, 1)

    def scroll_sheet():
        """Return a scrolling tab; the settings outgrow the window."""
        outside = QtWidgets.QScrollArea()
        outside.setWidgetResizable(True)
        outside.setFrameShape(QtWidgets.QFrame.NoFrame)
        inside = QtWidgets.QWidget()
        outside.setWidget(inside)
        position = QtWidgets.QVBoxLayout(inside)
        position.setContentsMargins(10, 12, 10, 10)
        position.setSpacing(16)
        return outside, position

    sheet1 = QtWidgets.QWidget()
    sheet1_position = QtWidgets.QVBoxLayout(sheet1)
    sheet1_position.setContentsMargins(10, 10, 10, 10)
    tabs.addTab(sheet1, T('Files && production'))

    # Production name, output folder and auphonic.com sit as a narrow strip
    # under the file list rather than on a sheet of their own: there are four
    # values, and a sheet for them would be four fifths empty. The strip is
    # attached further down, behind the list and the button bar.
    tab1 = QtWidgets.QWidget()
    in_layout = QtWidgets.QVBoxLayout(tab1)
    in_layout.setContentsMargins(0, 6, 0, 0)
    in_layout.setSpacing(14)
    tab2, assign_position_outside = scroll_sheet()
    tab3, resolve_position = scroll_sheet()

    sheet2 = QtWidgets.QWidget()
    sheet2_position = QtWidgets.QVBoxLayout(sheet2)
    sheet2_position.setContentsMargins(10, 10, 10, 10)

    def table_show(sheet, title, index, pick=False):
        if tabs.indexOf(sheet) < 0:
            tabs.insertTab(min(index, tabs.count()), sheet, title)
        if pick:
            tabs.setCurrentWidget(sheet)

    def tab_gone(sheet):
        i = tabs.indexOf(sheet)
        if i >= 0:
            tabs.removeTab(i)

    def settings_show():
        """Show the later tabs only once there are files."""
        if files:
            table_show(tab2, T('Assignment && time window'), 1)
            table_show(tab3, T('Resolve cut'), 2)
        else:
            tab_gone(tab2)
            tab_gone(tab3)

    def output_show(select=True):
        table_show(sheet2, T('Output'), 3, select)

    # ----------------------------------------------------- Tab 1: the files
    # While nothing is chosen the drop area is here and explains the
    # workflow; afterwards the list. Both in the same place, so it is clear
    # that one replaces the other.
    DropArea = make_drop_area(QtCore, QtGui, QtWidgets)
    drop_area = DropArea(lambda paths: take_paths(paths),
                           lambda: add_files(),
                           lambda: project_open(), COLOURS)
    sheet1_position.addWidget(drop_area, 1)

    # ------------------------------------------------------------------
    # The file list itself, and the two colour tables it draws with.
    # What comes back is what the rest of the window reaches for.
    # ------------------------------------------------------------------
    (items, preflight_line, stripes_pick, marks_pick, MARKS, FINDING_WORD,
     set_mark, item) = make_file_list(Qt, QtGui, QtWidgets,
                                      sheet1_position, state)

    # What a file with several channels becomes. The decision belongs
    # here, on the file page: the assignment tab works with the result,
    # and putting the question there as well would fill it up.
    # Blocks taken out of a recording by hand. They stand on their own
    # from then on; putting one back later makes it a file in its own
    # right. Only removing the whole recording clears its marks.
    no_join = FileSet()
    # Which blocks make up which recording. The channels are judged over
    # the whole recording, not over its first block -- see blocks_facts.
    blocks_of = ByFile()
    recording_of = ByFile()
    # Files put into a recording by hand: {file: the recording it joins}.
    # The counterpart to no_join, and stored in the project the same way.
    join_to = ByFile()

    def together_now():
        """The by-hand groupings, as group_recording_parts wants them."""
        return [[target, source] for source, target in sorted(join_to.items())
                if target and target != source]
    channel_choice = ByFile()    # file -> {pair number: stereo yes/no}
    channel_node = ByFile()      # file -> its row in the list
    video_kind_again = ByFile()  # file -> draw its Kind cell again
    # file -> [(track file, label)]. An empty list means the file was
    # looked at and stays whole; a missing entry means not looked at
    # yet.
    split_files = ByFile()

    def channel_rows_show(node, path):
        channel_rows_build(node, path, Qt, QtCore, QtWidgets,
                           blocks_of, channel_choice, channel_node,
                           channels_arrived, clip_kind_values, items,
                           remembered, split_files)

    def files_for_run():
        """The file list a run is given, with tracks in place of sources.

        Only here, not in the list the project stores: that one keeps
        the files as they lie on disc, so opening the project again
        finds them. The tracks are cut afresh each time and live in a
        temporary folder.
        """
        out = []
        for p, kind in files:
            pieces = (split_files.get(p) or []
                      if kind == "audio" else [])
            if pieces:
                out += [(x, "audio") for x, _label in pieces]
            else:
                out.append((p, kind))
        return out

    def split_arrived(path):
        """One file has been cut into its tracks: rebuild the tables."""
        assignment_fresh()
        buttons_check()

    bridge.split_done.connect(split_arrived)

    def channels_arrived(path):
        """The measurement for one file is in; redraw the rows it feeds.

        A recording of several blocks has one row, and that row waits for
        every block: the judgement is made over all of them. The row hangs
        on the first block, so a finished second block has to redraw the
        first one's node -- otherwise the last block to finish redraws
        nothing and the row says "being looked at" for ever.
        """
        a = os.path.abspath(path)
        for api_key in dict.fromkeys([a, recording_of.get(a, a)]):
            entry = channel_node.get(api_key)
            if not entry:
                continue
            try:
                channel_rows_show(entry[0], entry[1])
            except RuntimeError:
                channel_node.pop(api_key, None)
        # Now that the channels are known, what has to be cut out of
        # the file is known too.
        # The cameras belong in it too, or a camera carrying two clip-on
        # microphones would be measured and never cut.
        prework_kick_off(every_audio_block(files, blocks_of,
                                          state.get("own_cameras") or ()))

    bridge.channels_done.connect(channels_arrived)


    # Widgets that are built further down but are marked from up here.
    # Empty while the window is still being put together, so the checks
    # below run from the first moment without asking whether they may.
    late = {}

    def what_missing():
        """What is still missing, in plain words, keyed by tab."""
        return missing_conditions(files, production_var.get(),
                                  multitrack.get(), assign_lines,
                                  camera_lines, voice_lines,
                                  state.get("voiced") or set())

    def tab_named(sheet):
        """What the tab holding this sheet is called at the moment.

        Read off the tab rather than kept in a list beside it, and without
        the doubled ampersand Qt needs and the tick it may already carry.
        """
        i = tabs.indexOf(sheet) if sheet is not None else -1
        if i < 0:
            return T('this window')
        return tabs.tabText(i).replace("&&", "&").replace("\u2713", "").strip()

    def tab_checkbox():
        """Put a tick behind each tab once nothing on it is outstanding."""
        pending = what_missing()
        # The first tab now carries both, files and production, so what is
        # missing on it can come from either.
        first = bool({1, 11, 21} & set(pending))
        # Only the two tabs that can hold something outstanding. Nothing on
        # the Resolve tab keeps a run from starting, so a tick there would
        # always be on, and a mark that is always on says nothing.
        for sheet, pending_here, base_title in (
                (sheet1, first, T('Files && production')),
                (tab2, 22 in pending, T('Assignment && time window'))):
            i = tabs.indexOf(sheet)
            if i < 0:
                continue
            tabs.setTabText(i, base_title if pending_here
                            else base_title + "  \u2713")
        return pending

    def buttons_check():
        """Enable start and dry run only once nothing is missing.

        And if something is, what it is appears beside the button.
        """
        pending = tab_checkbox()
        ready = not pending and not state["running"]
        start_run.setEnabled(ready)
        preview_button.setEnabled(ready)
        menus_follow(late)
        mark_red(late.get("name_field"), 21 in pending,
                 pending.get(21, ""))
        note = late.get("start_note")
        if pending and not state["running"]:
            # The names come from the tabs themselves. A second list of
            # names kept beside them drifts apart from them with every
            # rename, and then points at pages nobody can find.
            on_tab = {1: sheet1, 11: sheet1, 21: sheet1,
                      22: tab2}
            lines = [T('Not ready yet:')]
            for index_number in sorted(pending):
                lines.append("  %s -- %s" % (tab_named(on_tab.get(index_number)),
                                              pending[index_number]))
            lines.append("")
            lines.append(T('Rows marked red show where the problem is; a '
                           'tick on the tab means everything is there.'))
            start_run_env_curve.setToolTip("\n".join(lines))
            # And the same in the window itself, in full. A tooltip
            # cannot be reached with the keyboard and is not read out
            # reliably, so the state line carries the reason rather
            # than a pointer at where the reason is kept.
            if note is not None:
                # Nothing opened yet is where everybody starts, not a
                # fault: quiet type. The warning colour is kept for the
                # case where something really is missing.
                if 1 in pending:
                    note.setText(T('No files or project opened yet.'))
                    note.setStyleSheet("color: %s;" % COLOURS["quiet"])
                else:
                    note.setText(T('Cannot start yet: %s') % "   ".join(
                        "%s -- %s" % (tab_named(on_tab.get(k)), pending[k])
                        for k in sorted(pending)))
                    note.setStyleSheet("color: %s;"
                                       % COLOURS["warning"])
                note.setVisible(True)
        else:
            start_run_env_curve.setToolTip(T('Measure, align, process, '
                                             'write files.'))
            if note is not None:
                note.setText("")
                note.setVisible(False)

    settings_window = {}

    def settings_open():
        """Open the window with everything that is set up once.

        Built on the first click rather than with the rest: the Resolve
        box it borrows is created a good deal later than this, and a
        window assembled up here would be assembled around nothing.
        """
        d = settings_window.get("dialog")
        if d is None:
            d = settings_window["dialog"] = settings_dialog_build(
                window, access_box, resolve_box, keep_where)
        # Whether Resolve answers is worth knowing at the moment somebody
        # looks, not as it was at some point earlier: Resolve gets started
        # and stopped, and a verdict from ten minutes ago is worth
        # nothing. So it is asked again on every opening.
        state["resolve_checked"] = True
        resolve_check_run_kick_off()
        d.show()
        d.raise_()
        d.activateWindow()

    def append_findings(node, its_findings):
        """List the hints for a file as lines below it.

        Otherwise the summary would count hints that can be read nowhere.
        """
        # Only the old finding lines. The same slot marks the channel rows
        # and the "belongs to" row, and clearing those here would take away
        # a setting the moment the check came back.
        for i in range(node.childCount() - 1, -1, -1):
            if node.child(i).data(0, Qt.UserRole + 2) == "finding":
                node.removeChild(node.child(i))
        for b in its_findings:
            if b.kind == "good":
                continue
            line = item(node, "      " + FINDING_WORD[b.kind], b.text)
            line.setData(0, Qt.UserRole + 2, "finding")
            line.setForeground(2, QtGui.QBrush(QtGui.QColor(
                MARKS[b.kind][1])))
            if b.advice:
                for column in (0, 1, 2):
                    line.setToolTip(column, b.advice)

    def show_overall(general):
        """Put what belongs to no single file into its own group."""
        for i in range(items.topLevelItemCount() - 1, -1, -1):
            if items.topLevelItem(i).data(0, Qt.UserRole + 2):
                items.takeTopLevelItem(i)
        if not general:
            return
        group = item(items, T('GENERAL NOTES'),
                        TN(len(general), '%s point', '%s points')
                        % group_text(len(general)), "group", True)
        group.setData(0, Qt.UserRole + 2, True)
        group.setExpanded(True)
        for b in general:
            line = item(group, "      " + (b.field or FINDING_WORD[b.kind]),
                           b.text)
            line.setForeground(2, QtGui.QBrush(QtGui.QColor(
                MARKS[b.kind][1])))
            if b.advice:
                for column in (0, 1, 2):
                    line.setToolTip(column, b.advice)

    def preflight_fill_in(findings):
        """Write the preflight findings into the list."""
        plan.done("check")
        if not files:
            return
        # Remember them: the list is rebuilt on every change and the marks
        # would be lost.
        state["preflight_findings"] = findings
        # The worst mark per file -- one hint weighs more than nine lines of
        # "fine". Which file is meant the finding says itself; a name
        # comparison would miss too often.
        rank = {"good": 0, "fixed": 1, "hint": 2, "abort": 3}
        # Collected per *row*, not per file: a multi-part recording has three
        # files but only one row. Otherwise the last block would overwrite the
        # mark and the hints of the first.
        per_node, general = {}, []
        for b in findings:
            node = lines_node.get(b.file) if b.file else None
            if node is not None:
                per_node.setdefault(id(node), (node, []))[1].append(b)
            elif b.kind != "good":
                # No row for it, so into the general group rather than counting
                # the finding and showing it nowhere.
                general.append(b)
        for node, its_findings in per_node.values():
            worst = max(its_findings, key=lambda x: rank[x.kind])
            set_mark(node, worst.kind, worst.text)
            append_findings(node, its_findings)
        show_overall(general)
        # The sentence below: what is there, and whether anything speaks
        # against it.
        sentence, colour_line = preflight_sentence(
            findings, len([1 for _p, a in files if a == "audio"]),
            state.get("audio_recordings"),
            len([1 for _p, a in files if a == "video"]))
        preflight_line.setText(sentence)
        preflight_line.setStyleSheet("color: %s;" % colour_line)

    def preflight_work_loop(audio_files, videos_p, label_run, crosstalk,
                         set_aside=(), apart=(), together=()):
        """Measure in the background so the interface does not freeze."""
        try:
            findings = collect_findings(audio_files, videos_p, False,
                                        crosstalk, set_aside, apart,
                                        together)
        except Exception as e:
            # An empty list would read as "nothing to fault", and the run
            # would start on material nobody looked at.
            findings = [Finding("abort", T('Check'),
                                T('the check itself stopped: %s') % e)]
        if state.get("preflight_run") == label_run:
            bridge_emit(bridge.preflight, findings)

    def preflight_kick_off():
        """Re-check after every change to the file list.

        Measured and cached per file, so adding a camera waits only for that
        one.
        """
        if not files:
            # Counted on, so the answer of a check still running
            # against the old list is dropped when it arrives.
            state["preflight_run"] = state.get("preflight_run", 0) + 1
            plan.drop(["check"])
            preflight_line.setText("")
            return
        # What is explicitly left out or discarded as video is still checked,
        # or its row would be the only one without a mark. It does not enter
        # the comparisons though, and its finding does not count towards the
        # balance.
        gone = set()
        for row, _nv, cv in assign_lines:
            if cv.get() == IGNORE_AUDIO:
                gone.update(path_key(x) for x in row)
        for file_path, value in clip_kind_values.items():
            if value.get() == TYPE_IGNORED:
                gone.add(path_key(file_path))
        audio_files = [p for p, a in files if a == "audio"]
        videos_p = [p for p, a in files if a == "video"]
        label_run = state.get("preflight_run", 0) + 1
        state["preflight_run"] = label_run
        plan.begin("check", T('Checking files'), 2.0)
        preflight_line.setText(T('checking ...'))
        preflight_line.setStyleSheet("color: %s;" % COLOURS["quiet"])
        # Crosstalk is a question about per-speaker tracks. Without multitrack
        # there are none, and while nothing is assigned it is not even settled
        # which file is a microphone and which a mix.
        threading.Thread(target=preflight_work_loop,
                         args=(audio_files, videos_p, label_run,
                               bool(multitrack.get()), gone,
                               frozenset(no_join),
                               tuple(tuple(g) for g in together_now())),
                         daemon=True).start()

    def join_row_show(node, path, heads):
        """Offer to put this recording into another one.

        The counterpart to "stands on its own" on a block: there a file
        that was found is taken out, here one that was not found is put
        in. Needed where the file names say nothing -- a recorder that
        numbers by neither a counter nor a clock -- and where two
        recorders were started one after the other on purpose.

        Only offered while there is another recording to join, and never
        on the recording somebody is already joining into: a chain of
        joins would be a puzzle, not a setting. What the clocks rule
        out is greyed rather than offered -- join_barred says which.
        """
        others = [h for h in heads if path_key(h) != path_key(path)
                  and h not in join_to]
        if not others:
            return
        kid = QtWidgets.QTreeWidgetItem(["      " + T('belongs to'), "", ""])
        kid.setData(0, Qt.UserRole + 2, "join")
        node.insertChild(0, kid)
        box = join_box_fill(QtWidgets.QComboBox(), path, others, blocks_of)
        i = box.findData(join_to.get(path) or "")
        box.setCurrentIndex(i if i >= 0 else 0)

        def chosen(_i=0, file_path=os.path.abspath(path), b=box):
            target = b.currentData() or ""
            if target:
                join_to[file_path] = target
            else:
                join_to.pop(file_path, None)
            QtCore.QTimer.singleShot(0, items_fresh)
            QtCore.QTimer.singleShot(0, assignment_fresh)
            QtCore.QTimer.singleShot(0, preflight_kick_off)

        box.currentIndexChanged.connect(chosen)
        # In the wide column, not beside it: this box holds file names,
        # and column one is only as wide as a checkbox.
        items.setItemWidget(kid, 2, box)

    def audio_use_value(path):
        """Whether this video file's sound is material -- one per file.

        One value for both places that show it, its listener added once
        here: a rebuilt table would pile up more of them otherwise.
        """
        v = audio_use_values.get(path)
        if v is None:
            v = audio_use_values[path] = Value(
                bool(remembered.get("own:" + path)))
            v.listen(lambda: QtCore.QTimer.singleShot(0, refresh_names))
        return v

    def audio_use_now():
        """The one derivation both tabs read; the values made on the way."""
        for p, a in files:
            if a == "video":
                clip_kind_value(p)
                audio_use_value(p)
        return cameras_using_audio(files, clip_kind_values,
                                   audio_use_values, has_sound)

    def video_choices_show(node, path, chosen, forced):
        """The two decisions a video file carries, in its own row.

        The Kind is shown twice in this window, here and in the camera
        table of the assignment sheet, and both show a derived wide shot
        -- which changes the moment a voice is given a camera. So the
        row leaves behind how to draw itself again; kinds_refresh calls
        it. Without it the list keeps what it said when the files came
        in, which is before anybody is assigned: every camera the wide
        shot.
        """
        short = os.path.basename(path)
        kind = clip_kind_values[path]
        video_kind_again[path] = lambda: video_choices_show(
            node, path, chosen, forced)
        cell, box = kind_cell_for(path, kind, *wide_cameras_now(),
                                  state.get("no_place"), clip_kind_values,
                                  COLOURS["quiet"],
                                  lambda p=path: kind_answered(p))
        items.setItemWidget(node, 3, cell)
        used, why = audio_use_settled(path, chosen, forced,
                                      has_sound(path), kind.get())
        sound, sound_box = camera_audio_cell(short, used, why,
                                             COLOURS["quiet"])
        audio_use_bind(sound_box, audio_use_value(path), why)
        items.setItemWidget(node, 4, sound)

    def items_fresh():
        probe_warm([p for p, _ in files])
        items.clear()
        # The rows are gone with it, so what could draw them again goes
        # too; the loop below hands back what the new list holds.
        video_kind_again.clear()
        prework_node.clear()
        lines_node.clear()
        # Which blocks belong to which recording is worked out below, for
        # the audio files that are in the list now. Emptied here rather
        # than there: with the last audio file gone, the loop below never
        # reaches the audio branch, and what stayed behind kept the
        # removed files in every_audio_block -- so the work for a file
        # nobody selected any more was queued again and again.
        blocks_of.clear()
        recording_of.clear()
        remove_button.setEnabled(False)
        # Once for the whole list: the rule looks at every file at once.
        own_now, forced_now = audio_use_now()
        state["own_cameras"] = list(own_now)
        state["forced_own"] = list(forced_now)
        for kind, title in (("audio", T('AUDIO')), ("video", "VIDEO")):
            own = [p for p, a in files if a == kind]
            if not own:
                continue
            if kind == "audio":
                chains = group_recording_parts(own, apart=no_join,
                                               together=together_now())
                file_count = sum(len(r) for r, _ in chains)
                header_value = recordings_text(len(chains), file_count)
                state["audio_recordings"] = len(chains)
            else:
                chains, header_value = None, TN(
                    len(own), '%s file', '%s files') % group_text(len(own))
            group = item(items, title, header_value, "group", True,
                            group_kind=kind)
            group.setExpanded(True)
            if kind == "audio":
                selected = set(os.path.abspath(p) for p in own)
                heads = [r[0] for r, _d in chains]
                for r, _d in chains:
                    head = os.path.abspath(r[0])
                    blocks_of[head] = [os.path.abspath(x) for x in r]
                    for x in r:
                        recording_of[x] = head
                for row, discarded in chains:
                    if len(row) > 1:
                        node = chain_fill_in(
                            group, row, discarded, selected, item,
                            lines_node, channel_rows_show)
                        join_row_show(node, row[0], heads)
                        continue
                    p = row[0]
                    node = item(group, os.path.basename(p),
                                    os.path.dirname(p), "audio",
                                    files_for_it=[p])
                    lines_node[p] = node
                    join_row_show(node, p, heads)
                    channel_rows_show(node, p)
                    try:
                        lines = audio_summary(p)
                    except Exception as e:
                        lines = [(T('Error'), str(e)[:120])]
                    for k, value in lines:
                        item(node, "      " + k, value)
                    # Collapsed: the format details are reference material, not
                    # news. Whoever needs them expands the file.
                    node.setExpanded(False)
                continue
            for p in sorted(own,
                            key=lambda x: os.path.basename(x).lower()):
                node = item(group, os.path.basename(p),
                                os.path.dirname(p), "video", files_for_it=[p])
                prework_node[p] = (node, os.path.dirname(p))
                lines_node[p] = node
                video_choices_show(node, p, own_now, forced_now)
                channel_rows_show(node, p)
                try:
                    lines = video_summary(p, video_facts(p))
                except Exception as e:
                    lines = [(T('Error'), str(e)[:120])]
                for k, value in lines:
                    item(node, "      " + k, value)
                node.setExpanded(False)
        # The drop area gives way to the list as soon as something is in it.
        drop_area.setVisible(not files)
        items.setVisible(bool(files))
        preflight_line.setVisible(bool(files))
        # Re-enter what has already been measured at once, so the list does not
        # stand there briefly without marks.
        if state.get("preflight_findings"):
            preflight_fill_in(state["preflight_findings"])
        preflight_kick_off()
        bar_env_curve.setVisible(bool(files))
        # The name comes from the material. The output folder comes from
        # nobody: a handover file in a subfolder belongs to the run that
        # wrote it, may be days old and from another measurement, and a
        # setting taken out of it looks exactly like an answer somebody
        # gave here. Settled on 30.8.2026: the project file has to be
        # enough, everything else is made again. So the folder stays
        # empty until it is chosen.
        if files and not production_var.get().strip():
            production_var.set(guess_production_name(files[0][0]))
        show_weak()
        finished_tracks_check()
        buttons_check()
        settings_show()
        assignment_fresh()

    def take_paths(new_one, quiet=False):
        """Take paths into the list, from the file dialog or dragged in.

        Folders are expanded: dragging in the recording folder means the files
        in it, not the folder.
        """
        paths = []
        for p in new_one:
            if os.path.isdir(p):
                for name in sorted(os.listdir(p)):
                    paths.append(os.path.join(p, name))
            else:
                paths.append(p)
        unknown = []
        for p in paths:
            e = os.path.splitext(p)[1].lower()
            kind = ("audio" if e in AUDIO_SUFFIXES
                   else "video" if e in VIDEO_SUFFIXES else None)
            if kind is None:
                if not os.path.basename(p).startswith("."):
                    unknown.append(os.path.basename(p))
                continue
            if p not in [x for x, _ in files]:
                files.append((p, kind))
        if unknown and not quiet:
            report(T('Not recognised'),
                   T('These files are neither audio nor video and stay '
                     'out:\n\n  %s') % "\n  ".join(unknown[:12]))
        # Asked before the files are measured. Opening the project
        # replaces the list with its own files, so everything measured
        # first was measured for nothing -- and it builds that list
        # itself, which is why nothing more happens here then.
        if project_offer(QtWidgets, window, state, [x for x, _ in files],
                         ask, project_open):
            return
        items_fresh()

    # A file dropped straight onto the list lands here, and the list is
    # built before this function exists.
    state["take_paths"] = take_paths

    def add_files():
        pattern = (T('Audio and video (%s);;All files (*)')
                  % " ".join("*" + e for e in AUDIO_SUFFIXES + VIDEO_SUFFIXES))
        new_one, _ = QtWidgets.QFileDialog.getOpenFileNames(
            window, T('Select audio and video files'),
            commonest_folder() or "", pattern)
        take_paths(new_one)

    def remove():
        choice = items.currentItem()
        if choice is None:
            return
        # On a group header it means all of it. That is a bigger thing than one
        # file, so it asks.
        kind = choice.data(0, Qt.UserRole + 1)
        single_block = False
        if kind:
            affected = [p for p, a in files if a == kind]
            if not affected:
                return
            how = T('audio file') if kind == "audio" else T('video file')
            if not ask(T('Remove all'),
                    T('Remove all %s %ss from the list?\n\n%s')
                    % (group_text(len(affected)), how,
                       "\n".join("  " + os.path.basename(p)
                                  for p in affected[:12])
                       + ("\n  ..." if len(affected) > 12 else "")),
                    T('Remove from list')):
                return
            gone = set(os.path.abspath(p) for p in affected)
        else:
            # Upwards from the clicked node until one stands for files. With a
            # multi-part recording the whole recording always goes -- a single
            # block could not be deselected anyway, it would be found again on
            # the next rebuild.
            node = choice
            while node is not None and node.data(0, Qt.UserRole) is None:
                node = node.parent()
            if node is None:
                return
            gone = set(os.path.abspath(p) for p in node.data(0, Qt.UserRole))
            single_block = node.data(0, Qt.UserRole + 3) == "block"
            if single_block:
                # One block out of a recording: it must stay out. The
                # search for continuations looks in the folder, not in
                # the list.
                no_join.update(gone)
        files[:] = [(p, a) for p, a in files
                      if os.path.abspath(p) not in gone]
        # A whole recording leaving takes the marks of its blocks with
        # it: adding the files again then joins them up as before.
        if not single_block:
            for p in list(gone):
                no_join.difference_update(recording_family(p))
        prework_clean_up(gone)
        items_fresh()
        # After the tables are built again, not before: building them
        # writes back every row they hold, and the row that has just
        # gone is among them until then. The project file is written
        # out of this store, so a row leaving the screen leaves it too.
        remembered_forget(remembered, gone)

    def removable():
        """Enable removal only when the selection actually offers something."""
        node = items.currentItem()
        while node is not None and node.data(0, Qt.UserRole) is None\
                and node.data(0, Qt.UserRole + 1) is None:
            node = node.parent()
        remove_button.setEnabled(node is not None)
        menus_follow(late)     # so the entry's key dies with the button

    items.currentItemChanged.connect(lambda *_: removable())

    # This bar only exists once something is in the list; before that the drop
    # area leads, and two offers side by side would be one too many.
    bar_env_curve = QtWidgets.QWidget()
    bar = QtWidgets.QHBoxLayout(bar_env_curve)
    bar.setContentsMargins(0, 0, 0, 0)
    sheet1_position.addWidget(bar_env_curve)
    bar_env_curve.setVisible(False)

    # Order of the sheet: the files first, then the name that follows from
    # their folder, then the optional parts.
    sheet1_position.addWidget(tab1)
    # At the start there are exactly two ways: start fresh or open an earlier
    # project, so the two stand side by side. Once files are in the list the
    # way is decided -- a project would overwrite them. The other direction
    # works: files can be added to an opened project.
    add_button = QtWidgets.QPushButton(T('Add files ...'))
    add_button.clicked.connect(add_files)
    bar.addWidget(hint(add_button,
                       T('Order does not matter. For a multi-part '
                         'recording the first block is enough.')))
    remove_button = QtWidgets.QPushButton(T('Remove'))
    remove_button.clicked.connect(remove)
    remove_button.setEnabled(False)
    # "Remove" on its own leaves open what goes; on screen the list
    # beside it says so, read out it does not.
    speaks_as(remove_button, T('Remove the chosen file from the list'))
    bar.addWidget(hint(remove_button,
                             T('Dropping AUDIO or VIDEO takes all of it.')))
    bar.addStretch(1)

    # ------------------------------------------------------------------
    # Tab 2: settings
    # ------------------------------------------------------------------
    out_folder = Value("")
    production_var = Value("")
    start_var = Value("")
    end_var = Value("")
    multitrack = Value(False)

    def commonest_folder():
        """Return the folder most of the chosen files come from."""
        counter = {}
        for p, _ in files:
            folder = os.path.dirname(os.path.abspath(p))
            counter[folder] = counter.get(folder, 0) + 1
        return max(counter, key=counter.get) if counter else None

    # --- production: name and location belong together
    place_box = QtWidgets.QGroupBox(T('Production'))
    in_layout.addWidget(place_box)
    place_position = QtWidgets.QVBoxLayout(place_box)
    name_bar = QtWidgets.QHBoxLayout()
    place_position.addLayout(name_bar)
    name_bar.addWidget(label(T('Production name')))
    _name_field = field_bind(QtWidgets.QLineEdit(), production_var, 340)
    # Duplicate names and duplicate output names are marked red in their row;
    # a missing production name is the same kind of fault and gets the same
    # mark instead of only greying the start button out.
    late["name_field"] = _name_field
    speaks_as(_name_field, T('Production name'))
    name_bar.addWidget(hint(
        _name_field, T('Title at auphonic.com and start of the new file names.')))
    _name_field.editingFinished.connect(lambda: refresh_names())
    production_var.listen(buttons_check)
    name_bar.addStretch(1)

    folder_bar = QtWidgets.QHBoxLayout()
    place_position.addLayout(folder_bar)
    folder_button = QtWidgets.QPushButton(T('Output folder ...'))
    folder_button.clicked.connect(lambda: folder_pick())
    folder_bar.addWidget(hint(
        folder_button, T('If empty: next to each video file.')))
    speaks_as(folder_button, T('Choose the output folder'))
    folder_label = label(T('next to each video file'), COLOURS["quiet"])
    speaks_as(folder_label, T('Output folder'))
    folder_bar.addWidget(folder_label)
    reset = QtWidgets.QPushButton(T('reset'))
    reset.clicked.connect(lambda: folder_delete())
    speaks_as(reset, T('Output folder back beside each video file'))
    reset.hide()
    folder_bar.addWidget(hint(reset,
                                    T('Puts it back next to each video file.')))
    folder_bar.addStretch(1)

    def folder_show():
        d = out_folder.get()
        folder_label.setText(d if d else T('next to each video file'))
        reset.setVisible(bool(d))

    def folder_pick():
        d = QtWidgets.QFileDialog.getExistingDirectory(
            window, T('Output folder'),
            out_folder.get() or commonest_folder() or "")
        if not d:
            return
        out_folder.set(d)
        folder_show()
        state["resolve_json"] = None
        resolve_button_check()
        preview_compute()
        finished_tracks_check()

    def folder_delete():
        out_folder.set("")
        folder_show()

    # --- how loud the finished episode is. Why it stands here and what
    #     the entries mean is in loudness_field_build.
    lufs_value = Value(loudness_last())
    loudness_field_build(place_position, lufs_value)

    # --- sheet 2 of the settings: the assignment on the left, the viewer
    #     with the time window below it on the right. What is configured
    #     and what is seen while doing it belong side by side.
    two_columns = QtWidgets.QHBoxLayout()
    assign_position_outside.addLayout(two_columns, 1)

    assign = QtWidgets.QGroupBox(T('Assignment: which audio track belongs '
                                   'to which camera'))
    two_columns.addWidget(assign, 1)
    assign_position = QtWidgets.QVBoxLayout(assign)
    # The Multitrack tick lives here, under the tables. Whether a camera
    # contributes a track of its own is decided in this very table, and
    # that is what decides whether Multitrack is possible at all -- a tick
    # on an earlier sheet would ask before the answer exists. It is filled
    # in further down, once the value it binds to exists.
    multitrack_bar = QtWidgets.QWidget()
    multitrack_row = QtWidgets.QHBoxLayout(multitrack_bar)
    multitrack_row.setContentsMargins(0, 6, 0, 0)
    assign_position.addWidget(multitrack_bar)
    # And right under it what auphonic.com is to make of those tracks:
    # the whole "what should this run do" in one place. Put here, filled
    # further down where the preset list is built.
    run_box = QtWidgets.QGroupBox(T('Processing at auphonic.com (optional)'))
    run_layout = QtWidgets.QVBoxLayout(run_box)
    assign_position.addWidget(run_box)
    # One bar for all the prework, under the tables.
    prework_box = QtWidgets.QWidget()
    _prework_rows = QtWidgets.QVBoxLayout(prework_box)
    _prework_rows.setContentsMargins(0, 6, 0, 0)
    _prework_rows.setSpacing(2)
    prework_progress_bar = QtWidgets.QProgressBar()
    prework_progress_bar.setRange(0, 100)
    prework_progress_bar.setTextVisible(False)
    prework_progress_bar.setFixedHeight(8)
    _prework_rows.addWidget(prework_progress_bar)
    prework_label = label("", COLOURS["value"])
    _prework_rows.addWidget(prework_label)
    hint(prework_box, T('Envelopes and camera audio are prepared in the '
                        'background.'))
    assign_position.addWidget(prework_box)
    prework_box.hide()

    right_column = QtWidgets.QVBoxLayout()
    two_columns.addLayout(right_column)

    view_box = QtWidgets.QGroupBox(T('Preview player'))
    box_room(view_box, 580)
    right_column.addWidget(view_box)
    # Top aligned: the box is as tall as it needs to be and the rest stays
    # empty. Otherwise Qt pulls the rows inside it apart.
    right_column.addStretch(1)
    view_position = QtWidgets.QVBoxLayout(view_box)
    player = (Player() if QtMultimedia is not None else NoPlayer())
    player.find_track = lambda p: audio_for_camera(p)

    def view_title(text=""):
        """Put the file name in the heading; that saves a line."""
        view_box.setTitle(T('Preview player%s')
                              % ("  --  " + text.replace("&", "&&")
                                 if text else ""))

    player.heading = view_title
    player.title.hide()
    view_position.addWidget(player)
    axis_label = label("", COLOURS["quiet"])
    axis_label.setWordWrap(True)
    hint(axis_label, T('Without timecode the position of the files is '
                       'measured.'))

    # The In point and Out point are taken from the picture, not typed. The
    # buttons sit in the player, right under the times they refer to.
    set_line = player.cut_bar

    def limit_set(target):
        """Adopt the position currently on screen as a boundary.

        In the same reckoning as the readout right above these buttons:
        two of them one widget apart put it where nobody set it.
        """
        a = player.axis_spot()
        exact = a if (a is not None and state.get("axis_absolute")) \
            else player.timer_s()
        if exact is not None:
            target.set(timecode_string(exact, player.fps))
            return
        target.set(as_relative_time(a if a is not None else player.spot_s()))

    def window_remember():
        """Put the boundaries where the player will find them."""
        state["in_point"] = start_var.get()
        state["out_point"] = end_var.get()
        player.window_draw()

    start_var.listen(window_remember)
    end_var.listen(window_remember)

    _in_point_button = QtWidgets.QPushButton(T('Mark In'))
    _in_point_button.clicked.connect(lambda: limit_set(start_var))
    set_line.addWidget(hint(_in_point_button, T('Takes the position from the picture.')))
    def to_limit(text, how):
        """Jump to the window boundary, fetching the right file if needed.

        Only when no file contains the position does a message say why
        nothing moved.
        """
        if player.jump_to(text):
            window_label.setVisible(False)
            return
        matching = next((b for b in player_candidates()
                        if covers(b, text) is True), None)
        if matching and matching != player.file_path:
            player_load(matching)
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

    _to_in_point = QtWidgets.QPushButton(T('to In point'))
    _to_in_point.clicked.connect(lambda: to_limit(start_var.get(), "In point"))
    set_line.addWidget(hint(_to_in_point, T('Jumps to the start of the window.')))
    set_line.addStretch(1)
    _to_out_point = QtWidgets.QPushButton(T('to Out point'))
    _to_out_point.clicked.connect(lambda: to_limit(end_var.get(), "Out point"))
    set_line.addWidget(hint(_to_out_point, T('Jumps to the end of the window.')))
    _out_point_button = QtWidgets.QPushButton(T('Mark Out'))
    _out_point_button.clicked.connect(lambda: limit_set(end_var))
    set_line.addWidget(hint(_out_point_button, T('Takes the position from the picture.')))
    window_switch = [_in_point_button, _to_in_point, _to_out_point, _out_point_button]

    window_label = label("", COLOURS["warning"])
    window_label.setWordWrap(True)
    view_position.addWidget(window_label)
    window_hint = label("", COLOURS["quiet"])
    window_hint.setWordWrap(True)
    view_position.addWidget(window_hint)
    view_position.addWidget(axis_label)

    # Under the assignment table: separating the speakers is an action
    # on one named recording, and every recording carries the button
    # for it in its own row. What stands here is the one question that
    # is about the project and not about a file -- whether this machine
    # works it out at all -- said once, beside the rows it applies to.
    split_line = QtWidgets.QWidget()
    _split_row = QtWidgets.QHBoxLayout(split_line)
    _split_row.setContentsMargins(0, 0, 0, 0)
    split_label = label("", COLOURS["quiet"])
    split_label.setWordWrap(True)
    _split_row.addWidget(split_label, 1)
    split_never = QtWidgets.QPushButton(T('Not on this machine'))
    hint(split_never, T('Leaves the separation switched off for this '
                        'project. The cut then comes from the tracks or '
                        'from auphonic.com, as before.'))
    _split_row.addWidget(split_never)
    assign_position.insertWidget(1, split_line)
    split_line.setVisible(False)

    def window_position_show():
        """Say what the In point and the Out point refer to."""
        if not state["without_tc"] or not state["axis"]:
            window_label.hide()
            return
        window_label.setText(
            T('No audio file carries a timecode. In point and Out point count '
              'from the start of the material -- the position of the files '
              'to each other is measured.'))
        window_label.show()

    def window_enable():
        away = not_on_the_axis(getattr(player, "file_path", None),
                               clip_kind_values, remembered)
        on = window_ready(state) and not away
        for widget in window_switch:
            widget.setEnabled(on)
        window_hint.setText(away or ("" if on else T(
            'In point and Out point are available once the time axis is '
            'set -- from the timecode or measured.')))
        window_hint.setVisible(not on)

    def window_length():
        """Return the length of the window, empty if none is set."""
        try:
            a, _ = parse_time_point(start_var.get(), 30.0)
            b, _ = parse_time_point(end_var.get(), 30.0)
        except Exception:
            return ""
        if a is None or b is None or b <= a:
            return ""
        return as_hms(b - a)

    def window_prefill(videos):
        """Prefill the In point and the Out point from what the cameras offer.

        As far as the cameras reach -- from the earliest start to the latest
        end. That is what happens without an entry anyway; here it is visible
        and can be adjusted.
        """
        if start_var.get().strip() or end_var.get().strip():
            return
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
        if not from_s:
            return
        if not absolute and not window_ready(state):
            return          # without an axis the value has no reference
        if absolute and (not state["axis"] or state.get("axis_absolute")):
            state["tc_there"] = True
        start_var.set(from_s)
        end_var.set(until)



    assign_lines = []            # [(chain, name_value, camera_value)]
    camera_lines = []           # [(path, name_value, own, own_name)]
    # One row per voice a separation heard, hanging under the recording
    # it was heard in. Two tables one above the other said the same
    # thing twice -- both carried a speaker name and a camera, and only
    # their heading said which level was meant. A tree says it by where
    # the row hangs, the way the file list already does. Up here with
    # the other two: what is missing is asked of all three.
    voice_lines = []             # [(key, name_value, camera_value)]
    remembered = {}              # survives a redraw of the table
    suggestions = ByFile()       # what the table last suggested itself

    # ------------------------------------------------------------------
    # Extract the camera audio in the background
    #
    # Where the camera audio becomes a track it has to come out of the video
    # files. With two hours of 4K that takes minutes. Rather than leaving the
    # interface standing, a thread starts as soon as the table is built -- by
    # the time Start is pressed it is usually done and the run simply takes
    # what is there.
    #
    # The work itself stands above in make_prework_bar and
    # make_prework_tasks. What stays here are the containers: the rest
    # of the window writes through them.
    # ------------------------------------------------------------------
    prework_done = {}               # (path, mtime, size) -> WAV
    prework_queue = []                # still to fetch
    prework_discarded = set()    # left the list while being fetched
    prework_pending = ByFile()          # path -> how many tasks are still open
    prework_node = ByFile()      # path -> (row in the file list, text)
    lines_node = ByFile()        # path -> row in the file list
    prework_lock = threading.Lock()
    prework_run = {"threads": 0}
    prework_shares = {}              # (path, task) -> 0..1
    # Declared here rather than beside its own block: the prework asks
    # whether the separation is running before that block is reached.
    split_run = {"busy": False, "stop": False}

    prework_busy, prework_report, prework_status_show = make_prework_bar(
        QtCore, bridge, bridge_emit, plan, prework_box, prework_label,
        prework_progress_bar, prework_node, prework_discarded,
        prework_lock, prework_queue, prework_run, prework_shares)

    prework_kick_off = make_prework_tasks(
        state, bridge, bridge_emit, plan, blocks_of, recording_of,
        channel_choice, split_files, split_run, prework_report,
        prework_status_show, prework_done, prework_pending, prework_queue,
        prework_discarded, prework_lock, prework_run, prework_shares)

    # ------------------------------------------------------------------
    # Measure the time axis where there is no timecode
    #
    # Without timecode nobody knows which position in one file matches which
    # position in another -- on a switch the player could only jump bluntly to
    # the same second from the start of the file, which shows something else
    # entirely on a camera that started later.
    #
    # The same measurement the run makes works here too: after the prework the
    # envelopes are in memory already, and their cross correlation says how far
    # the files lie apart. After that the player jumps to the same point in the
    # events, and the In point and the Out point apply to every file alike.
    # ------------------------------------------------------------------
    HOP = 5.0
    tc_cache = {}

    def real_tc(p):
        """Return the timecode the file itself carries, or nothing."""
        a = os.path.abspath(p)
        if a not in tc_cache:
            try:
                if os.path.splitext(a)[1].lower() in AUDIO_SUFFIXES:
                    tc_cache[a] = file_timecode(a)
                else:
                    info = video_facts(a) or {}
                    tc_cache[a] = (parse_timecode(info["tc"],
                                               max(1.0, info.get("fps") or 30.0))
                                      if info.get("tc") else None)
            except Exception:
                tc_cache[a] = None
        return tc_cache[a]

    def axis_measure(paths):
        """Determine how all files sit relative to each other."""
        return axis_with_blocks(paths, real_tc, HOP, blocks_of)

    def axis_file():
        """Return the project file, even before a name is settled.

        There is exactly one. It comes into being while the time axis is
        measured, at that point still next to the material, and moves along
        once an output folder is chosen. Two copies of the same production
        would be a trap: the wrong one gets opened.
        """
        target = out_folder.get() or commonest_folder()
        if not target or not os.path.isdir(target):
            return None
        name = safe_filename(production_var.get().strip() or 'Project')
        return os.path.join(target, "%s%s.json" % (PROJECT_PREFIX, name))

    def project_move():
        """Move the project file after a rename or a new output folder.

        The file is named after the production and lives in the output folder,
        and both can change after it has been written. It is then moved rather
        than created a second time.
        """
        fresh = axis_file()
        old = state.get("project_last")
        if not fresh or not old or os.path.abspath(old) == os.path.abspath(fresh):
            if fresh:
                state["project_last"] = fresh
            return
        try:
            if os.path.isfile(old):
                os.replace(old, fresh)
        except OSError:
            return
        state["project_last"] = fresh

    def project_collect(file_path):
        """Read the project file, earlier locations included."""
        found, gone = project_state_read(file_path, (
            out_folder.get(), commonest_folder(),
            state.get("project_last")))
        for p in gone:
            try:
                os.unlink(p)
            except OSError:
                pass
        state["project_last"] = file_path
        return found

    # Renaming the production or changing the output folder moves the file
    # along at once, or a second one would appear beside it on the next write.
    production_var.listen(project_move)
    out_folder.listen(project_move)

    def settings_extend(d):
        """Put the settings into the project file as well.

        The file exists as soon as the time axis is measured, long before
        anything has run. Opening it then should give everything back, not
        just the file list.
        """
        try:
            d["production"] = production_var.get().strip()
            d["out_folder"] = out_folder.get()
            d["multitrack"] = bool(multitrack.get())
            d["wide_at_edges"] = bool(edge_on.get())
            d["camera_cut"] = {s: cut_var[s].get() for s in cut_var}
            d["in_point"] = start_var.get()
            d["out_point"] = end_var.get()
            # Who belongs to which camera is set by hand and cannot be guessed
            # again -- the suggestion rule distributes in order and is bound to
            # be wrong with three speakers on two cameras.
            assignment_remember()
            d["assignment"] = {s: (list(value) if isinstance(value, tuple) else value)
                              for s, value in remembered.items()}
            # The no-Auphonic entry is not a preset but very much a
            # decision, and it should be there again on opening. A
            # fallback is not that decision: where a preset was chosen
            # and only the list is missing, the choice is what is kept.
            d["preset"] = (state.get("preset_wanted")
                           or (PRESET_NONE if without_auphonic()
                               else preset_plaintext().strip()))
            d["speech_language"] = speech_language.get().strip()
            # null where nothing is adjusted, and written even then: the
            # key being there is what tells this file apart from one
            # written before there was a choice.
            d["lufs"] = lufs_value.get()
            # The separations travel with the project: three minutes of
            # computing should not be paid a second time because the
            # folder moved to another machine. Raw, in the time of the
            # source file -- a changed offset is then arithmetic.
            block = speakers_project_block(state)
            if block:
                d["speakers"] = block
            d["speakers_source"] = state.get("speakers_source") or ""
            # Missing means nobody has been asked yet, which is not the
            # same as a no.
            if state.get("speakers_wanted") is not None:
                d["speakers_local"] = bool(state["speakers_wanted"])
            d["apart"] = sorted(no_join)
            d["together"] = {k: v for k, v in sorted(join_to.items())}
            # Which pair of channels is one track and which is two: set
            # by hand, and not guessable a second time.
            d["channels"] = {p: {str(k): bool(v) for k, v in choice.items()}
                             for p, choice in channel_choice.items() if choice}
        except NameError:
            pass            # GUI still being built, so without them
        return d

    def axis_store(axis):
        """Put the measurement into the project file.

        Over two hours of material it takes minutes, so it should be there next
        time. The file size and mtime are stored with it: if those no longer
        match, it is measured again rather than carried on wrongly.
        """
        project_move()
        file_path = axis_file()
        if not file_path:
            return
        d = project_collect(file_path)
        d["format"] = FILE_FORMAT
        d["version"] = VERSION
        # Without a measurement the stored one stays: this is also the
        # way the settings reach the file where every file carries a
        # timecode and no axis was ever measured.
        if axis:
            d["timeline"] = timeline_entries(axis, state.get("axis_clock"))
            d["timeline_absolute"] = bool(state.get("axis_absolute"))
        d["files"] = [{"path": p, "kind": a} for p, a in files]
        settings_extend(d)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=1)
        except OSError as e:
            # A measurement of several minutes is in here. If it is lost,
            # somebody has to hear about it, or the next start silently
            # measures again.
            print(T('  Project file could not be written: %s') % e)

    def axis_read(paths):
        """Reuse a previously measured axis if it still fits."""
        file_path = axis_file()
        if not file_path or not os.path.exists(file_path):
            return None
        try:
            with open(file_path, encoding="utf-8") as f:
                d = json.load(f) or {}
        except (OSError, ValueError):
            return None
        return axis_still_valid(d, paths)

    def axis_work_loop(paths, label_run):
        """Wait for the envelopes, then measure.

        Broken off where the list it was started for has gone: this is
        the longest reading of the material there is.
        """
        while prework_busy():
            if state.get("axis_run") != label_run:
                return
            time.sleep(0.4)
        if state.get("axis_run") != label_run:
            return
        try:
            data, text = axis_measure(paths)
        except Exception as e:
            data, text = {}, T('time axis not measurable: %s') % str(e)[:60]
        # Counted like the check above: putting an answer about files
        # that have left in would carry one axis into the next.
        if state.get("axis_run") == label_run:
            bridge_emit(bridge.axis, data or {}, text)

    def axis_kick_off(paths):
        """Measure wherever there are two files, timecode or not.

        A clock is set by hand and is set wrong; the run measures anyway.
        """
        every = list(paths)
        for row, _nv, _cv in assign_lines:
            if row[0] not in every:
                every.append(row[0])
        if len(every) < 2:
            return
        if not axis_worth_measuring(files, every, state):
            return
        remembered = axis_read(every)
        if remembered:
            axis_present(remembered, "", remember=False)
            return
        if state.get("axis_running"):
            # A file added while the measurement runs: the answer on its
            # way is about the list without it. The request is kept and
            # asked again once that answer is in, or the new file never
            # gets measured at all.
            state["axis_again"] = list(paths)
            return
        state["axis_running"] = True
        label_run = state.get("axis_run", 0) + 1
        state["axis_run"] = label_run
        plan.begin("axis", T('Measuring time axis'), 3.0)
        axis_label.setText(T('Measuring time axis ...'))
        axis_label.setStyleSheet("color: %s" % COLOURS["quiet"])
        threading.Thread(target=axis_work_loop, args=(every, label_run),
                         daemon=True).start()

    # The prework hands its files on to the time axis, and stands above
    # this line: the way over is the same one voice_answered takes.
    state["axis_kick_off"] = axis_kick_off

    def axis_present(data, text, remember=True):
        state["axis_running"] = False
        axis_answer_kept(state)
        plan.done("axis")
        axis = (data or {}).get("axis") or {}
        state["axis"] = axis
        state["axis_clock"] = (data or {}).get("clock") or {}
        state["axis_absolute"] = bool((data or {}).get("absolute"))
        state["weak"] = set(path_key(p) for p in ((data or {}).get("weak") or []))
        state["no_place"] = set(path_key(p)
                                for p in ((data or {}).get("no_place") or []))
        if axis and remember:
            axis_store(axis)
        show_weak()
        # A file nothing could place is proposed for "ignore this
        # video", or for "Intro" where it is far shorter than the rest.
        # A proposal, so it stops at anything answered.
        for p in kind_proposal_say(state.get("clip_kinds") or {}, data):
            kind_answered(p)
        # And the Kind fields are said again even where no proposal
        # moved one: which files sit nowhere is known only now.
        kinds_said_again(state, video_kind_again)
        axis_label.setText(text)
        axis_label.setStyleSheet("color: %s" % (COLOURS["good"] if axis
                                                 else COLOURS["warning"]))
        player.spot(int(player.spot_s() * 1000))
        player.window_draw()
        window_enable()
        window_position_show()
        tc_column_show()
        # Only now can it be said which file contains In point and Out point:
        # relative values count from the start of the material, and that is
        # known only after the measurement.
        player_follow_up()
        # Taken out before it is asked again, or a stored axis coming
        # back through here would ask a third time.
        if state.get("axis_again") is not None:
            axis_kick_off(state.pop("axis_again"))

    bridge.axis.connect(axis_present)

    # Separate the speakers, locally: what the window does when a
    # separation is started, followed and its result written down.
    (speaker_split_kick_off, split_stop, voices_of,
     several_set) = make_speaker_split(
        QtCore, state, bridge, bridge_emit, plan, files, assign_lines,
        voice_lines, remembered, split_run, split_line, split_label,
        split_never, axis_store)

    def tc_column_show():
        """Fill the timecode column, real or computed."""
        rows = state.get("file_rows")
        if rows and not tc_column_write(
                rows, real_tc, state["axis"],
                state.get("axis_absolute")):
            state["file_rows"] = None

    def show_weak():
        """Mark the files that do not fit the common axis.

        On the first sheet, where the files are chosen, and on the
        recordings of the assignment tree. Not on the cameras there:
        that note has been read by then, see weak_rows_mark.
        """
        for p in weak_marks_show(state, lines_node):
            lines_node.pop(p, None)

    def prework_clean_up(gone):
        """What left the list needs no audio either."""
        gone = FileSet(gone)
        keys = set(path_key(p) for p in gone)      # what the cache is keyed by
        with prework_lock:
            dropped = [(p, a) for p, a in prework_queue if p in gone]
            prework_queue[:] = [(p, a) for p, a in prework_queue
                                if p not in gone]
            # What is being extracted cannot be aborted mid-write -- the thread
            # clears it away itself once it is finished.
            prework_discarded.update(keys)
        for api_key in [k for k in prework_done if k[0] in gone]:
            file = prework_done.pop(api_key, None)
            if file and os.path.exists(file):
                try:
                    os.unlink(file)
                except OSError:
                    pass
        # Runs in the window thread, so the bar may be touched directly.
        for p, task in dropped:
            # Their share would stay at zero and hold the bar back.
            prework_shares.pop(prework_share_key(p, task), None)
        # The same on the bar for the whole job: a step announced for
        # a file that has left keeps that bar creeping.
        plan.drop([n for n in plan.order
                   if n.startswith("pre:") and n.split(":", 2)[-1] in gone])
        if dropped:
            prework_status_show()
        for p in gone:
            prework_node.pop(p, None)
            prework_pending.pop(p, None)
        for api_key in [k for k in _ENV if k[0] in keys]:  # 5.8 MB an hour
            _ENV.pop(api_key, None)

    def prepared_tracks():
        """Return the finished tracks from auphonic.com: name -> file."""
        return prepared_tracks_in(
            done_folder.get()
            or finished_tracks_find(out_folder.get())
            or finished_tracks_find(commonest_folder())
            or finished_tracks_deeper(commonest_folder()))

    def audio_for_camera(camera_path):
        """The recording that belongs under this camera in the preview."""
        return audio_under_camera(camera_path, clip_kind_values,
                                  prepared_tracks(), assign_lines,
                                  blocks_of)

    def line_show(table, file_list):
        """A clicked row of the camera table: that file in the player.

        One entry per row. The recordings are a tree and not a table,
        and a click in it is answered by assignment_row_show.
        """
        row = table.currentRow()
        if 0 <= row < len(file_list) and file_list[row]:
            player_load(file_list[row])

    clip_kind_values = ByFile()
    # One value per video file, shown twice -- file list and player. Not
    # a second store: the same object both times.
    audio_use_values = ByFile()

    # The time axis is measured elsewhere and proposes a Kind from there.
    state["clip_kinds"] = clip_kind_values

    # Below clip_kind_values, which player_candidates reads: the eight
    # are only called out of other closures, so binding them here is
    # early enough.
    (player_load, player_spot_wanted, picture_span, covers,
     player_candidates, player_suggestion, main_track_show,
     player_follow_up) = make_player_choice(
         files, clip_kind_values, assign_lines, start_var, end_var,
         player, remembered, state, window_enable)

    def clip_kind_value(path):
        """One video file's Kind -- one value, and two places show it."""
        return clip_kind_values.setdefault(
            path, Value(remembered.get("kind:" + path) or TYPE_CONTENT))
    def wide_cameras_now():
        """Which cameras here are the wide shot, and who said so.

        Kept in state as well: the preview needs the same answer, and it
        lives in another part of the window.
        """
        return wide_cameras_of(files, clip_kind_values, remembered,
                               cameras_with_a_speaker(
                                   assign_lines, voice_lines,
                                   state.get("voiced") or ()),
                               state.get("no_place") or ())

    state["wide_cameras_now"] = wide_cameras_now

    def kind_answered(path):
        """A Kind changed: both tables show it, and the assignment too.

        Drawing them again is also what shuts "Intro" on the other
        files, and opens it again when the mark is taken off.
        """
        QtCore.QTimer.singleShot(0, items_fresh)
        QtCore.QTimer.singleShot(0, assignment_fresh)

    def assignment_remember():
        for row, nv, cv in assign_lines:
            # Where the voices stand underneath, the row holds no selector:
            # the recording has no camera of its own then, and that fallback
            # value must not overwrite an assignment that was once made --
            # switching back to one name has to find the old one again.
            old = remembered.get("audio:" + row[0])
            quiet_row = os.path.abspath(row[0]) in (state.get("voiced") or ())
            # Only the answer, the same rule the camera beside it
            # follows: a guess written back is a guess nobody checks,
            # and a file renamed afterwards would no longer move it.
            remembered["audio:" + row[0]] = (nv.typed(), camera_to_remember(
                cv.get(), getattr(cv, "derived", None),
                old[1] if (quiet_row and old) else None))
        for file_path, nv, own_box, own_name_box in camera_lines:
            remembered["video:" + file_path] = nv.get()
            # Only what somebody clicked themselves is stored. A tick that
            # follows from "one camera, no audio recording" is derived
            # afresh every time, so it disappears by itself as soon as an
            # audio recording joins and leaves nothing behind.
            if file_path not in (state.get("forced_own") or ()):
                remembered["own:" + file_path] = own_box.get()
            remembered["ownname:" + file_path] = own_name_box.get()
        for file_path, value in clip_kind_values.items():
            remembered["kind:" + file_path] = value.get()
        # Where the player is belongs in the project: opening it again
        # should carry on there, not at the start of the file.
        try:
            if player.file_path:
                remembered["player_file"] = player.file_path
                remembered["player_spot"] = round(player.spot_s(), 3)
        except Exception:
            pass

    def cell(t, line, column, text, colour=None):
        p = QtWidgets.QTableWidgetItem(text)
        if colour:
            p.setForeground(QtGui.QBrush(QtGui.QColor(colour)))
        t.setItem(line, column, p)
        return p

    audio_fields, video_fields = [], []

    def assignment_check():
        """Mark the trouble spots red, and let the preview hear the name."""
        # A typed name is an answer like any other; without this the
        # preview went on showing the old name at the old camera until
        # something unrelated was touched. Found 30.8.2026.
        if state.get("preview_soon"):
            state["preview_soon"]()
        assignment_marks_show(
            audio_fields, assign_lines, video_fields, camera_lines,
            bool(multitrack.get()), state, voice_lines)
        buttons_check()

    # The recordings of the assignment tree: (its row, the file, the
    # plain caption). The voices are not in here -- they have no file.
    file_rows = []
    # Which recordings somebody left open, over a rebuild of the tree.
    # Open is what a fresh one starts as: the assignment lives in the
    # rows underneath, and a sheet that hides its own subject is no use.
    tree_open = ByFile()

    # Bound here, above assignment_fresh, which reaches for all seven,
    # and above the assignment_state_show() further down in this body.
    (assignment_state_show, voice_play, assignment_row_show, folded_show,
     voice_add, voices_build, voices_remember) = make_voice_rows(
         Qt, QtCore, assign_lines, camera_lines, voice_lines, files,
         remembered, state, tree_open, multitrack, player,
         assignment_check, player_load, speaker_split_kick_off,
         voices_of)

    # Two dictionaries of files the table builder fills and empties
    # again. They are made here because the window owns them.
    own_audio_names = ByFile()
    piece_label = ByFile()

    def assignment_fresh(forget=()):
        """Build both tables again, out of the piece above gui()."""
        assignment_tables_build(
            forget, Qt, QtCore, QtWidgets, assign_lines, assign_position,
            audio_fields, camera_lines, clip_kind_values, file_rows, files,
            no_join, own_audio_names, piece_label, production_var,
            remembered, split_files, state, suggestions, tree_open,
            video_fields, video_kind_again, voice_lines, assignment_check,
            assignment_remember, assignment_row_show, assignment_state_show,
            audio_use_now, audio_use_value, cell, clip_kind_value,
            folded_show, kind_answered, line_show, main_track_show,
            prework_kick_off, several_set, show_weak, speaker_split_kick_off,
            split_stop, tc_column_show, together_now, voice_add,
            voices_build, voices_of, wide_cameras_now, window_enable,
            window_position_show, window_prefill)

    # The separation stands above this line and redraws both tables when
    # a result comes back; the way over is the one preview_soon takes.
    state["assignment_fresh"] = assignment_fresh

    def refresh_names():
        """Suggest file names again; hand-edited ones stay."""
        untouched = [p for p, nv, _k, _n in camera_lines
                      if nv.get() == suggestions.get(p)]
        assignment_fresh(untouched)

    # The table builder stands above gui() and is written before this,
    # so the way over is state -- as state["preview_soon"] already is.
    state["refresh_names"] = refresh_names

    def mode_toggled():
        """The checkbox changed: what the later tabs show changes with it.

        The tabs themselves stay, and so does the assignment: which
        camera a recording belongs to is asked with the tick and
        without it, and the same answer comes out of the run either
        way. So nothing here throws a camera away. It used to, on the
        reasoning that without Multitrack there had been no choice to
        make -- and once the choice can be made without the tick, that
        reasoning would have deleted real handiwork on every click.
        """
        assignment_fresh()
        if files:
            table_show(tab2, T('Assignment && time window'), 1)
            table_show(tab3, T('Resolve cut'), 2)
        # What gets checked hangs on this decision.
        preflight_kick_off()
        presets_filter()
        # Camera cut and forecast live off the speakers being told
        # apart. Whether that came of separate tracks or of one
        # recording taken apart is not this question.
        assignment_state_show()
        try:
            resolve_button_check()
        except NameError:
            pass            # the button does not exist during setup

    # --- Multitrack
    #
    # Under the assignment table, not beside the production name: what
    # Multitrack needs is decided in that table. Two input tracks, and a
    # camera counts as one as soon as its Camera audio is used.
    # A tick on the sheet before would ask the question before the answer
    # can exist.
    multitrack_value = multitrack
    multi_button = QtWidgets.QCheckBox(T('Multitrack (one track per speaker)'))
    checkbox_bind(multi_button, multitrack_value)
    multi_button.toggled.connect(lambda *_: mode_toggled())
    multitrack_row.addWidget(hint(
        multi_button, T('One audio track per person, kept apart all the '
                        'way to auphonic.com.\nWorks without it as well -- '
                        'then without de-bleed and leveler.\nIt needs two '
                        'input tracks: a recording of its own, a channel '
                        'of a\nmultichannel recorder, or the audio of a '
                        'video file set to "use\nthe audio". The camera '
                        'cut does not need this tick.')))
    # Why it is not on offer. The tick stays clickable either way.
    multitrack_note = label("", COLOURS["quiet"])
    multitrack_row.addSpacing(10)
    multitrack_row.addWidget(multitrack_note)
    multitrack_row.addStretch(1)
    state["multitrack_note"] = multitrack_note
    assignment_state_show()

    # --- Spoken language
    #
    # Two jobs at once: it becomes the language tag of the written
    # audio track, and it tells the recognition here what to expect.
    # Empty is a fair answer to both -- the tag stays off and the
    # recognition works the language out for itself.
    speech_language = Value(language_of_system())
    # The separation, which stands above this line, reads the tag when
    # it starts a run.
    state["speech_language"] = speech_language
    language_box = QtWidgets.QComboBox()
    language_box.addItem(T('not set'), "")
    for tag, name in spoken_language_choices():
        language_box.addItem(name, tag)

    def language_show():
        """Put the stored tag onto the list."""
        i = language_box.findData(speech_language.get() or "")
        language_box.setCurrentIndex(i if i >= 0 else 0)

    language_box.currentIndexChanged.connect(
        lambda *_: speech_language.set(language_box.currentData() or ""))
    speech_language.listen(lambda *_: language_show())
    language_show()
    name_bar.insertSpacing(name_bar.count() - 1, 18)
    name_bar.insertWidget(name_bar.count() - 1,
                          label(T('Language'), COLOURS["quiet"]))
    name_bar.insertSpacing(name_bar.count() - 1, 6)
    name_bar.insertWidget(name_bar.count() - 1, hint(language_box,
        T('The language spoken in the recording. It becomes the tag of '
          'the\nwritten audio track, and the recognition here is told to '
          'expect it.\nPreset from the system language. "%s" leaves the '
          'track untagged\nand lets the recognition work the language '
          'out itself.') % T('not set')))

    # --- Auphonic, in two halves
    #
    # The key belongs to the person and is entered once in a lifetime; the
    # preset belongs to this production and is chosen every time. They
    # used to sit in one box on the first sheet, so choosing a preset meant
    # paging back from the table where the decision is actually made. The
    # key now lives behind "Settings ...", the preset under the assignment.
    access_box = QtWidgets.QGroupBox(T('Access to auphonic.com'))
    access_layout = QtWidgets.QVBoxLayout(access_box)
    first_line = QtWidgets.QHBoxLayout()
    access_layout.addLayout(first_line)
    first_line.addWidget(label("API Key:"))
    _key_first, state["key_from"] = api_key_source()
    key_var = Value(_key_first)
    key_entry = field_bind(QtWidgets.QLineEdit(), key_var, 280)
    key_entry.setEchoMode(QtWidgets.QLineEdit.Password)
    first_line.addWidget(key_entry)
    remember = Value(bool(load_api_key()))
    # Name where it goes; "remember" does not say where.
    if platform.system() == "Darwin":
        keep_text, keep_where = T('Save in Keychain'), T('Keychain')
    elif platform.system() == "Windows":
        keep_text, keep_where = T('Save in Registry'), "Registry"
    else:
        keep_text, keep_where = T('Keep it saved'), T('system store')
    keep_button = checkbox_bind(QtWidgets.QCheckBox(keep_text), remember)
    first_line.addWidget(hint(
        keep_button, T('The key is then in the %s, never in a file.')
        % keep_where))
    check_button = QtWidgets.QPushButton(T('Connect'))
    check_button.setFixedWidth(caption_room(check_button, 110))
    first_line.addWidget(hint(check_button,
                                  T('Check the key and fetch Presets.')))
    keychain_row_add(access_layout, keep_button)

    # The note about the key, under the field and on the sheet both.
    (settings_note, key_row, key_note_show,
     key_note_hide) = make_key_note(QtWidgets, label, hint,
                                    lambda: settings_open())
    access_layout.addWidget(settings_note)
    run_layout.addLayout(key_row)

    def button_green(on):
        """Checked and good: the button turns green and goes to sleep."""
        check_button.setEnabled(not on)
        check_button.setStyleSheet(
            "QPushButton:disabled { background: %s; color: white; "
            "font-weight: bold; border: 0px; border-radius: 4px; }"
            % COLOURS["good"] if on else "")

    second_line = QtWidgets.QHBoxLayout()
    run_layout.addLayout(second_line)
    second_line.addWidget(label(T('Preset:')))
    presets_wanted_now = lambda: presets_load(asked=False)
    preset_box = preset_box_widget(QtWidgets, state, presets_wanted_now)()
    preset_box.setMinimumWidth(caption_room(preset_box, 320,
                                            preset_missing_rows()))
    # While no key is checked there is only the one entry, and it describes
    # exactly what happens then.
    preset_box.addItem(label_of(PRESET_NONE), PRESET_NONE)
    second_line.addWidget(hint(preset_box,
        T('Determines how auphonic.com processes the audio.\n\n"%s" leaves '
          'the key in place and still does not go there.\nThe audio is then '
          'only merged and normalised, not unmixed --\nand without separate '
          'tracks there is no camera cut.') % label_of(PRESET_NONE)))
    second_line.addSpacing(16)
    # Where the processed tracks are already there, nothing is uploaded. The
    # script finds that out itself; this only says so.
    done_folder = Value("")
    done_label = label("", COLOURS["good"])
    second_line.addWidget(done_label)
    second_line.addStretch(1)

    def without_auphonic():
        """Report whether the entry stands in the preset list."""
        return preset_box.currentData() == PRESET_NONE

    def without_auphonic_toggled(*_):
        """Multitrack no longer hangs off auphonic.com.

        Without a preset the run stays local: aligned, mixed, cut -- only
        de-bleed, leveler and noise removal are missing. So the tick stays
        available; only the preset behind it changes what happens.
        """
        multi_button.setEnabled(True)
        buttons_check()

    preset_box.currentIndexChanged.connect(without_auphonic_toggled)

    def preset_picked(*_):
        """A pick by hand is the wish from here on, whatever it was.

        Only a click raises this; rebuilding the list is done with the
        signals blocked. So what is kept here is a decision and never
        the entry the box fell onto when the list went away.
        """
        state["preset_wanted"] = preset_box.currentData() or ""

    preset_box.activated.connect(preset_picked)
    def finished_tracks_check():
        """Check whether processed tracks are already in the output folder."""
        found = (finished_tracks_find(out_folder.get())
                    or finished_tracks_find(commonest_folder())
                    or finished_tracks_deeper(commonest_folder()))
        done_folder.set(found or "")
        done_label.setText(T('processed tracks found -- nothing is uploaded') if found else "")

    def remember_toggled(on):
        if on:
            if not store_api_key(key_var.get().strip()):
                tick_off_quietly(keep_button, remember)
                report(T('The key was not saved'), key_store_trouble())
        else:
            delete_api_key()

    keep_button.toggled.connect(remember_toggled)

    # The box only appears with multitrack, since only there is the
    # speaker-to-camera assignment it lives off. All numbers on this sheet
    # apply to the configured window, so that stands here again and nobody
    # has to page back. Whether Resolve is reachable would otherwise only
    # show at the end of a long run, so it is checked on the first look at
    # this sheet, in the background -- the connection takes a moment.
    resolve_box = QtWidgets.QGroupBox(T('Connection to Resolve'))
    # Two areas side by side as in the assignment: what is configured on the
    # left, what comes of it on the right.
    resolve_columns = QtWidgets.QHBoxLayout()
    resolve_position.addLayout(resolve_columns, 1)
    resolve_left = QtWidgets.QVBoxLayout()
    resolve_right = QtWidgets.QVBoxLayout()
    resolve_columns.addLayout(resolve_left, 1)
    resolve_columns.addLayout(resolve_right, 1)
    # One line saying whether Resolve is there, and the way to the box
    # that can ask again. Hidden until something has been asked.
    _echo_row = QtWidgets.QHBoxLayout()
    resolve_left.addLayout(_echo_row)
    resolve_echo = label("", COLOURS["quiet"], True)
    resolve_echo.setVisible(False)
    _echo_row.addWidget(resolve_echo)
    _echo_button = QtWidgets.QPushButton(T('Settings ...'))
    _echo_button.setFlat(True)
    _echo_button.clicked.connect(lambda: settings_open())
    _echo_button.setVisible(False)
    _echo_row.addWidget(_echo_button)
    _echo_row.addStretch(1)
    _resolve_rows = QtWidgets.QVBoxLayout(resolve_box)
    _resolve_head_row = QtWidgets.QHBoxLayout()
    _resolve_rows.addLayout(_resolve_head_row)
    resolve_head = label(T('not checked yet'), COLOURS["quiet"], True)
    resolve_head.setWordWrap(True)
    _resolve_head_row.addWidget(resolve_head, 1)
    verify_button = QtWidgets.QPushButton(T('Check again'))
    speaks_as(verify_button, T('Check the connection to Resolve again'))
    hint(verify_button, T('Connects to Resolve again.'))
    _resolve_head_row.addWidget(verify_button)
    resolve_text = label("", COLOURS["quiet"])
    resolve_text.setWordWrap(True)
    resolve_text.setVisible(False)
    _resolve_rows.addWidget(resolve_text)

    def resolve_check_run_fill_in(result):
        works, lines = result
        # The box itself lives in the settings window. Its answer belongs
        # here as well, on the sheet that builds the Resolve project: a
        # verdict written only into a window nobody has opened is no
        # verdict at all.
        resolve_echo.setText(T('Resolve answers') if works
                             else T('Resolve does not answer -- see '
                                    'Settings'))
        resolve_echo.setStyleSheet("color: %s;" % (COLOURS["good"] if works
                                                   else COLOURS["error"]))
        # Only where it does not answer. Resolve has nothing to set, so
        # a line saying it is there costs a row and tells nobody
        # anything -- and the way to the box is only worth showing to
        # somebody who has something to fix.
        resolve_echo.setVisible(not works)
        _echo_button.setVisible(not works)
        resolve_head.setText(T('Resolve answers%s')
                             % (("  (%s)" % lines[0]) if works and lines
                                else "" if works else T(' not.')))
        resolve_head.setStyleSheet("color: %s; font-weight: bold;"
                                   % (COLOURS["good"] if works
                                      else COLOURS["error"]))
        resolve_text.setText("" if works else "\n".join(lines))
        resolve_text.setVisible(not works)
        verify_button.setEnabled(True)
        verify_button.setText(T('Check again'))

    def resolve_check_run_work_loop():
        try:
            result = check_resolve()
        except Exception as e:
            result = (False, [T('Check itself failed: %s') % e])
        bridge_emit(bridge.resolve_check, result)

    def resolve_check_run_kick_off():
        verify_button.setEnabled(False)
        verify_button.setText(T('checking ...'))
        resolve_head.setText(T('checking ...'))
        resolve_head.setStyleSheet("color: %s;" % COLOURS["quiet"])
        resolve_text.setText("")
        resolve_text.setVisible(False)
        threading.Thread(target=resolve_check_run_work_loop,
                         daemon=True).start()

    verify_button.clicked.connect(resolve_check_run_kick_off)
    bridge.resolve_check.connect(resolve_check_run_fill_in)

    def resolve_sheet_chosen(*_):
        """Resolve and the speakers, on the first look at this tab.

        Not twice -- a second speaker run costs minutes for nothing.
        """
        if tabs.currentWidget() is not tab3:
            return
        if not state.get("resolve_checked"):
            state["resolve_checked"] = True
            resolve_check_run_kick_off()
        if speakers_still_wanted(state):
            gui_log("cut tab opened with no speakers known -- measuring")
            speaker_measure()

    tabs.currentChanged.connect(resolve_sheet_chosen)

    # The In point and Out point are in the player on the right; a box of their
    # own would be the same information twice.
    window_info = QtWidgets.QWidget()
    window_info.setVisible(False)
    _info_row = QtWidgets.QHBoxLayout(window_info)
    window_info_label = label("", COLOURS["value"], True)
    _info_row.addWidget(window_info_label)

    def window_info_show():
        a, b = start_var.get().strip(), end_var.get().strip()
        duration = window_length()
        window_info_label.setText(
            T('In point: %s     Out point: %s     Duration: %s')
            % (a or T('Beginning'), b or T('End'),
               duration or T('the whole material')))

    start_var.listen(window_info_show)
    end_var.listen(window_info_show)

    # What stands in place of the camera cut: one line saying why, which
    # beats an empty area. Until 2.7.0-beta it sent people to
    # auphonic.com for an assignment the machine has made since 2.0.0.
    without_cut_label = label(
        T('There is no camera cut yet: it needs two people, each with a '
          'name and a camera.\nSeparate recordings give that with the '
          'Multitrack tick, and so does "several speakers" in the '
          'Speaker name field of one recording --\nthe voices found there '
          'get their camera in the table under the recordings.\nA Resolve '
          'project is created anyway -- all cameras at their measured '
          'places, ready for Multicam.'),
        COLOURS["quiet"])
    without_cut_label.setWordWrap(True)
    resolve_left.addWidget(without_cut_label)
    without_cut_label.setVisible(False)

    cut_box = QtWidgets.QGroupBox(T('Camera cut'))
    resolve_left.addWidget(cut_box)
    cut_position = QtWidgets.QVBoxLayout(cut_box)
    cut_parts = {}
    cut_var = cut_fields_build(cut_position, cut_parts)
    edge_on = Value(True)
    _edge_box = checkbox_bind(QtWidgets.QCheckBox(
        T('Wide shot for greeting at the start and farewell at the end')), edge_on)
    cut_position.addWidget(hint(
        _edge_box, T('During greeting and farewell the picture stays wide.')))
    wide_note = wide_note_build(label, COLOURS["quiet"])
    question_note = question_note_build(label, COLOURS["quiet"])
    for _n in (wide_note, question_note):
        cut_position.addWidget(_n)
    def wide_state_show():
        """Grey the wide shot settings where there is no wide shot.

        Silent while the cut box is still being assembled -- it is
        built after the tables that ask for this, and the startup call
        below is the first one that counts.
        """
        if state.get("cut_box_there"):
            wide_settings_grey(cut_parts, _edge_box, wide_note,
                               bool(wide_cameras_now()[0]), COLOURS["quiet"],
                               bool(state.get("words_there")))
            preview_kick_off()

    # The same way over as refresh_names above, and for the same reason.
    state["wide_state_show"] = wide_state_show
    # Preview: as soon as a handover file from earlier is there, the cut can be
    # recomputed on every change without writing anything. Then the effect of a
    # number is visible rather than guessed.
    forecast_box = QtWidgets.QGroupBox(
        T('%s -- preview') % cut_title_of(voice_lines, multitrack.get(),
                                          assign_lines, len(camera_lines)))
    # The three that stand or fall together, where the assignment can
    # reach them: it is rebuilt before this tab exists.
    state["cut_boxes"] = (cut_box, forecast_box, without_cut_label)
    # Weighted: whatever stays free below goes into this picture.
    resolve_right.addWidget(forecast_box, 1)
    forecast_outer = QtWidgets.QVBoxLayout(forecast_box)
    forecast_position = QtWidgets.QHBoxLayout()
    forecast_outer.addLayout(forecast_position)
    forecast_outer.setStretch(0, 0)
    cut_column = QtWidgets.QVBoxLayout()
    forecast_position.addLayout(cut_column)
    # The per-camera numbers are in the legend under the cut band; the space
    # here belongs to the picture.
    preview_label = label("", COLOURS["value"])
    preview_label.setTextFormat(Qt.RichText)
    preview_label.setWordWrap(True)
    preview_label.setAlignment(Qt.AlignTop)
    cut_column.addWidget(preview_label)
    cut_column.addStretch(1)

    # Beside it: who speaks how much. Without those numbers the cut next to it
    # cannot be judged.
    speaker_box = QtWidgets.QGroupBox(T('Speaker'))
    resolve_left.addWidget(speaker_box)
    speech_column = QtWidgets.QVBoxLayout(speaker_box)
    speech_column.setContentsMargins(10, 2, 10, 8)
    speech_title = label(T('Speakers, separated by voice'),
                        COLOURS["heading"], True)
    speech_column.addWidget(speech_title)
    speech_position = speech_column
    speech_table = QtWidgets.QTableWidget(0, 5)
    speech_table.setHorizontalHeaderLabels([T('Speaker'), T('Speech time'),
                                            T('Share'), T('Blocks'),
                                            T('average')])
    speech_table.verticalHeader().setVisible(False)
    speech_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    speech_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
    speech_table.setShowGrid(False)
    speech_table.setAlternatingRowColors(True)
    speech_position.addWidget(speech_table)


    def speech_show(d):
        """Write the speaker statistics into the table."""
        state["speech_time_total"] = speech_table_fill(
            Qt, QtGui, QtWidgets, speech_table, d)

    speech_table.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                QtWidgets.QSizePolicy.Fixed)
    speech_table.setMinimumWidth(240)
    speech_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    # The cut band and the player under it, with what they show.
    (cut_band, cut_player, band_show,
     preview_file) = make_band_and_player(
        Qt, QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets,
        NoPlayer, state, files, assign_lines, clip_kind_values,
        forecast_outer, player)

    def audio_for_cut(d, cameras, offset):
        """Return the audio to run under the camera cut: (file, offset).

        Preferably the finished overall mix from auphonic.com: it is at
        delivery level, carries its timecode and is exactly what the cut
        timeline in Resolve gets.

        Where it does not exist yet -- because the speakers were only measured
        locally, say -- the camera file carrying the mix as its first audio
        track is used; the same choice as for angle 1 of the multicam clip. The
        audio is then as loud as the camera recorded it, so noticeably quieter.
        A speaker camera would be worse: it brings only one voice.
        """
        done = prepared_tracks()
        mix = next((done[n] for n in ("Full-Mix", "Fullmix", "Mix")
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

    def player_load_cut(numbers):
        """Feed the player with the cut, or with a single file."""
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
                audio_file, audio_offset = audio_for_cut(d, cameras, offset)
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
    # band_show reaches for this through state: it is built above the
    # line that made it, so it cannot be handed over as a parameter.
    state["player_load_cut"] = player_load_cut
    band_show(None)
    resolve_left.addStretch(1)
    # No stretch on the right: the room below belongs to the preview picture,
    # not to empty space.
    resolve_right.addStretch(0)

    preview_compute, speaker_measure = make_preview(
        Qt, QtWidgets, state, bridge, bridge_emit, assign_lines,
        camera_lines, voice_lines, cut_var, cut_parts, edge_on, start_var,
        end_var, multitrack, out_folder, clip_kind_value, wide_cameras_now,
        commonest_folder, band_show, speech_show, window_info_show,
        question_note, cut_column, forecast_box, preview_label,
        speech_title, speech_table)

    state["preview_compute"] = preview_compute

    # Do not compute on every keystroke; wait a moment.
    preview_timer = QtCore.QTimer(window)
    preview_timer.setSingleShot(True)
    preview_timer.setInterval(400)
    preview_timer.timeout.connect(lambda: voice_suggest_round(
        state, voice_lines, assign_lines, camera_lines,
        start_var.get(), end_var.get(), speech_language.get(),
        lambda r: bridge_emit(bridge.speakers_heard, r)))
    preview_timer.timeout.connect(preview_compute)

    def preview_kick_off():
        preview_timer.start()
    state["preview_soon"] = preview_kick_off

    for _v in cut_var.values():
        _v.listen(preview_kick_off)
    edge_on.listen(preview_kick_off)
    start_var.listen(preview_kick_off)
    end_var.listen(preview_kick_off)

    # As soon as a run has left a handover file behind, the preview
    # should appear by itself rather than on the next click.
    watchdog = QtCore.QTimer(window)
    watchdog.setInterval(3000)

    def check_for_a_cut():
        if preview_out_of_date(state, multitrack.get()):
            preview_compute()

    watchdog.timeout.connect(check_for_a_cut)
    watchdog.start()

    def presets_filter():
        """Offer only the presets that match the mode."""
        preset_box_fill(preset_box,
                        preset_entries(state["presets"], multitrack.get(),
                                       label_of(PRESET_NONE), PRESET_NONE),
                        state, PRESET_NONE)
        without_auphonic_toggled()

    def preset_plaintext():
        """Return the chosen preset name, empty where none was chosen.

        The first entry is not a preset but the decision to work without
        auphonic.com, so it yields nothing to pass on.
        """
        choice = preset_box.currentData()
        return "" if not choice or choice == PRESET_NONE else choice

    def presets_load(asked=True):
        """Check the API key and fetch the presets in one go.

        The call is the test: a preset list coming back means the key is good.
        Only then are preset and multitrack available. Fetched in its own
        thread so the window does not freeze.

        *asked* is false for the try at start-up with a remembered key.
        It decides the wording and nothing else: a key out of the store
        is named as the stored one, a key just typed is not. Neither of
        them opens a box -- a rejected key belongs at the button that
        stays ungreen and in the line under it, not over the window.
        """
        state["key_asked"] = asked
        key_note_hide()
        key = key_var.get()
        wrong = key_complaint(key)
        if wrong:
            # Nothing leaves the house over a key that is plainly not
            # one. Which of the cases it is stands in the sentence
            # itself, so one place to say it is enough.
            key_note_show(wrong)
            return
        key = key.strip()
        state["presets_busy"] = True
        check_button.setEnabled(False)
        check_button.setText(T('checking ...'))

        def fetch():
            try:
                bridge_emit(bridge.presets, list_presets(key), "", key)
            except Exception as e:
                bridge_emit(bridge.presets, None, str(e)[:90], key)

        threading.Thread(target=fetch, daemon=True).start()

    def presets_arrived(preset_list, error, checked=""):
        state["presets_busy"] = False
        check_button.setText(T('Connect'))
        # Opened while it was still fetching: show it again, now with
        # what came back. Only where the list is still the front thing
        # somebody is looking at, so a fetch from Connect does not make
        # a list jump open under their hands.
        open_after = state.pop("presets_open_after", False) and preset_list
        if preset_list is None:
            state["presets"] = None
            button_green(False)
            presets_filter()
            # Whole and unshortened: what auphonic.com said is the only
            # account of the reason anybody gets. Only the wording
            # differs -- at start-up the key came out of the store or
            # out of AUPHONIC_TOKEN, and is named as such.
            if not state.get("key_asked", True):
                key_note_show(key_refused_note(state.get("key_from"), error))
                return
            key_note_show(key_refused_note("", error))
            return
        state["presets"] = preset_list
        # A store that refuses must show, or the button goes green over
        # a key that is gone at the next start. What goes in is the key
        # that was checked, never the field read a second time: a paste
        # during the check otherwise stored one nobody had checked.
        if remember.get() and not store_api_key(
                (checked or key_var.get()).strip()):
            tick_off_quietly(keep_button, remember)
            key_note_show(T('The key was not saved: %s')
                          % key_store_trouble())
        button_green(True)
        presets_filter()
        note, fitting = preset_mode_note(preset_list, multitrack.get())
        if note:
            key_note_show(note)
        if open_after and fitting:
            preset_box.showPopup()

    bridge.preflight.connect(preflight_fill_in)
    bridge.presets.connect(presets_arrived)
    check_button.clicked.connect(lambda: presets_load(asked=True))

    def api_key_changed():
        """A new key means unchecked until OK is pressed again.

        Multitrack is not touched: it works without auphonic.com too, so a
        key being retyped is no reason to switch it off.
        """
        state["presets"] = None
        button_green(False)
        # The complaint was about the key that stood there before, and
        # it must not be read as being about the one now being typed.
        key_note_hide()
        presets_filter()

    key_var.listen(api_key_changed)

    # ------------------------------------------------------------------
    # Tab 3: log
    # ------------------------------------------------------------------
    log = make_log_view(QtGui, QtWidgets, Cursor)()
    sheet2_position.addWidget(log, 1)

    output_foot = QtWidgets.QHBoxLayout()
    sheet2_position.addLayout(output_foot)

    def result_open():
        target = (state["results"][-1] if state["results"]
                else state.get("result_folder"))
        if target:
            open_in_file_manager(target)

    # The result button belongs with the output, not in the footer. A disabled
    # button takes no mouse events in Qt and therefore shows no tooltip, so a
    # wrapper holds it and carries the reason.
    def having_reason(button):
        env_curve = QtWidgets.QWidget()
        position = QtWidgets.QHBoxLayout(env_curve)
        position.setContentsMargins(0, 0, 0, 0)
        position.addWidget(button)
        return env_curve

    open_button = QtWidgets.QPushButton(T('Open result folder'))
    open_button.clicked.connect(result_open)
    open_button.setEnabled(False)
    open_env_curve = having_reason(open_button)
    open_env_curve.setToolTip(T('There is no result yet.'))
    output_foot.addWidget(open_env_curve)
    # The Resolve button belongs here: first one looks at the result, then one
    # creates the project.
    only_resolve = QtWidgets.QPushButton(T('Create Resolve project'))
    only_resolve.setEnabled(False)
    only_resolve_env_curve = having_reason(only_resolve)
    only_resolve_env_curve.setToolTip(T('That needs the handover file from '
                                        'a run, and there is none.'))
    output_foot.addWidget(only_resolve_env_curve)
    output_foot.addStretch(1)

    def result_button_check():
        """The button appears only once there really is a result."""
        target = (state["results"][-1] if state["results"]
                else state.get("result_folder"))
        reason_set(open_env_curve, open_button,
                     bool(target) and not state["running"],
                     T('The run is still going.') if state["running"]
                     else T('There is no result yet.'),
                     T('Show in Finder.'))

    # ------------------------------------------------------------------
    # Footer
    # ------------------------------------------------------------------
    # What comes back is what the rest of the window reaches for: the
    # two run buttons and the frame that carries the reason a grey Start
    # gives, the break-off, the plan behind the bar and the order of its
    # stages, and the timer that has to be stopped when the window goes.
    (start_run, start_run_env_curve, preview_button, break_off,
     plan_wipe, run_plan_build, run_step_order, total_clock) = make_footer(
        Qt, QtCore, QtWidgets, window, vertical, state, files,
        plan, bridge, late, multitrack, without_auphonic, settings_open)

    # ------------------------------------------------------------------
    # Project file
    # ------------------------------------------------------------------
    def project_write(argv):
        """Store what this run did, so it can be reopened.

        Not the state of every button but what counts: the files, the output
        folder and the command line. That is enough to repeat the same run, or
        just the Resolve part of it.
        """
        project_move()
        file_path = axis_file()
        if not file_path:
            return
        # The API key does not belong in a file.
        clean, skip = [], False
        for part in argv[1:]:
            if skip:
                skip = False
                continue
            if part == "--auphonic-api-key":
                skip = True
                continue
            clean.append(part)
        axis_old = (project_collect(file_path).get("timeline") or [])
        d = {"format": FILE_FORMAT,
             "version": VERSION,
             "files": [{"path": p, "kind": a} for p, a in files],
             "timeline": axis_old,
             "timeline_absolute": bool(state.get("axis_absolute")),
             "call": clean}
        settings_extend(d)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=1)
        except OSError as e:
            write(T('  Project file not writable (%s)\n') % e)
            return
        write(as_head(T('PROJECT SAVED\n  %s\n  This run can be opened again '
                        'later -- top left\n  "Open project ..."\n\n') % file_path))

    def project_new():
        """Empty the window, the way a new production starts.

        Until now the only way to a second production was to quit the
        program and start it again. Asked for on 30.8.2026: a close
        project and a new one in the menu, so that a second production
        does not need a restart.

        This is also the list of what belongs to a project and what does
        not, and it is the only such list: opening a project runs it
        first and then puts the file's answers on top, so the two cannot
        drift apart. Anything left standing here would be carried from
        one production into the next, which is the fault that took the
        output folder out of an old handover file.
        """
        measuring_stop(state, [p for p, _a in files], prework_clean_up,
                       split_stop, split_run, plan_wipe)
        state["closing"] = False
        tab_gone(sheet2)
        log.clear()
        state["results"] = []
        state["project_from"] = ""
        window.setWindowTitle(window_title())
        files[:] = []
        out_folder.set("")
        production_var.set("")
        start_var.set("")
        end_var.set("")
        clip_kind_values.clear()
        audio_use_values.clear()
        no_join.clear()
        join_to.clear()
        channel_choice.clear()
        for name in ("wide_set_aside", "voiced", "projects_offered",
                     "speakers_source_chosen", "forced_own",
                     "result_folder", "resolve_json", "voice_marks",
                     "cut_basis", "run_auphonic") + SPEAKER_STATE:
            state.pop(name, None)
        words_forgotten(state)
        # Emptied, not taken away: the time axis is read by name in
        # several places, and a missing key there is a KeyError rather
        # than an empty axis.
        state["axis"] = {}
        state["axis_clock"] = {}
        state["axis_absolute"] = False
        # The timecode belonged to the material that has just gone; left
        # standing, the menu went on offering marks on an empty window.
        state["tc_there"] = False
        state["speakers_local"] = {}
        state["speakers_source"] = ""
        state["speakers_by"] = ByFile()
        state["speakers_count"] = 0
        state["speakers_wanted"] = None
        state["preset_wanted"] = ""
        # Back to what they hold when the program has just started, so a
        # second production begins the way the first one did.
        speech_language.set(language_of_system())
        lufs_value.set(loudness_last())
        edge_on.set(True)
        multitrack.set(False)
        items_fresh()
        folder_show()
        window_enable()
        resolve_button_check()
        result_button_check()
        preview_compute()

    def project_save():
        """Write the project file now, without running anything.

        It was written at the start of a run and when the program was
        quitted, and nowhere else -- so a session that set up a
        production and then went away for the night had it, and a
        session that wanted it on paper first had no way to ask.
        """
        if not out_folder.get():
            # The sentence first, the chooser after it. A folder dialog
            # opening by itself does not say why it is there, and the
            # explanation used to come only for whoever cancelled.
            report(T('Save project'),
                   T('The project file goes into the output folder, and '
                     'none is chosen yet. Please choose one.'))
            folder_pick()
            if not out_folder.get():
                return
        axis_store(state.get("axis") or {})
        where = axis_file()
        report(T('Save project'),
               T('Written:\n\n  %s') % where if where
               else T('Nothing was written -- there is no material yet.'))

    def project_open(file_path=""):
        file_path = file_path or QtWidgets.QFileDialog.getOpenFileName(
            window, T('Open json project file'),
            out_folder.get() or commonest_folder() or "",
            T('Video Podcast Magic (%s*.json);;JSON files (*.json);;All '
              'files (*)') % PROJECT_PREFIX)[0]
        if not file_path:
            return
        d, file_path = find_project_file(file_path)
        if d is None:
            report('Project',
                   T('This is not a project file, and there is none in the '
                     'same folder.\n\nThe search is for %s*.json -- the '
                     'script writes it into the output folder at start.')
                   % PROJECT_PREFIX)
            return
        complaint = format_complaint(d)
        if complaint:
            report('Project', "%s\n\n%s" % (os.path.basename(file_path),
                                             complaint))
            return
        # Emptied first, by the one list of what belongs to a project,
        # and the file's answers put on top. Two clearing lists would
        # drift, and what one of them forgot would travel from the last
        # production into this one.
        project_new()
        state["project_from"] = file_path
        window.setWindowTitle(window_title(file_path))
        present, missing = project_files(d)
        files[:] = present
        # Before anything is drawn: every file measured once, in
        # parallel. What follows then asks its questions of memory.
        probe_warm([x for x, _ in present])
        for s, value in (d.get("camera_cut") or {}).items():
            if s in cut_var:
                cut_var[s].set(value)
        out_folder.set(d.get("out_folder") or "")
        folder_show()
        production_var.set(d.get("production") or "")
        edge_on.set(bool(d.get("wide_at_edges", True)))
        # Set before the tables are built: the window prefill leaves standing
        # whatever is already there.
        start_var.set(d.get("in_point") or "")
        end_var.set(d.get("out_point") or "")
        # Restore the assignment before the tables are built, or the interface
        # suggests something and overwrites it.
        assign_lines[:] = []
        camera_lines[:] = []
        remembered.clear()
        # Intro, outro and "ignore this video" hang on the file, not on the
        # table, so they outlive the table being rebuilt. Opening another
        # project has to take them with it: a file that was the intro there
        # would otherwise still be the intro here, and two of them stop the
        # run.
        if d.get("speech_language"):
            speech_language.set(d["speech_language"])
        # The saved project beats what was chosen last. null is an answer
        # here, so the key decides and not the value; a file from before
        # there was a choice carries none and changes nothing.
        if "lufs" in d:
            lufs_value.set(d["lufs"])
        # The separations come back before the tables are built, or
        # the voices would be missing until they had run again.
        state["speakers_by"] = speakers_all_from_project(d)
        source, found, _called = speakers_from_project(d)
        state["speakers_local"] = found
        state["speakers_source"] = source or (d.get("speakers_source") or "")
        state["speakers_count"] = int(
            ((d.get("speakers") or {}).get("num_speakers")) or 0)
        speakers_front_pick(state)
        state["speakers_wanted"] = (bool(d["speakers_local"])
                                    if "speakers_local" in d else None)
        no_join.update(d.get("apart") or [])
        join_to.update(d.get("together") or {})
        for p, choice in (d.get("channels") or {}).items():
            channel_choice[p] = {int(k): bool(v) for k, v in choice.items()}
        state["preset_wanted"] = d.get("preset") or ""
        for api_key, value in (d.get("assignment") or {}).items():
            remembered[api_key] = (tuple(value) if isinstance(value, list)
                                   else value)
        voice_keys_carry_source(remembered,
                                state.get("speakers_source") or "")
        if d.get("multitrack"):
            multitrack.set(True)
        preset_list_bring(state, presets_wanted_now, presets_filter)
        items_fresh()
        if multitrack.get():
            # The tick fires nothing where it already stood, so the later
            # tabs are told by hand that the project is open.
            mode_toggled()
        state["results"] = []
        for name in SPEAKER_STATE:
            state.pop(name, None)
        target = out_folder.get()
        # The handover of that project's own run, looked for where the
        # note below sends the reader, and only where it names the same
        # cameras. Without it the note promised "Create Resolve
        # project" while the button stayed grey.
        state["resolve_json"] = find_handover_file(
            target, os.path.dirname(os.path.abspath(file_path)),
            ours=[b for b, _n, _own, _own_name in camera_lines])
        if target and os.path.isdir(target) and any(
                n.lower().endswith(VIDEO_SUFFIXES) for n in os.listdir(target)):
            # Results from earlier: the sheet comes along, since its buttons
            # are there. So it does not look like a failed run, it says where
            # things stand.
            state["result_folder"] = target
            output_show(False)
            log.append_text(as_head(project_opened_note(target)))
        else:
            state["result_folder"] = None
        resolve_button_check()
        result_button_check()
        preview_compute()
        # The In point and Out point are back, so fetch the file containing
        # them into the player. Otherwise "to In point" and "to Out point" go
        # nowhere right after opening.
        player_follow_up(spot_also=True)
        if missing:
            report('Project', T('These files no longer exist:\n  ')
                   + "\n  ".join(missing[:12]))

    def resolve_button_check():
        # The simple path creates a handover too -- there the multicam timeline
        # arises instead of the camera cut. So the file decides whether there
        # is anything to build, not the checkbox.
        if state["running"]:
            reason_set(only_resolve_env_curve, only_resolve, False,
                         T('The run is still going.'), "")
            return
        js = state.get("resolve_json")
        what_for = T('Cut, EDL, CSV and the handover are worked out '
                     'again from the numbers above. Who speaks when '
                     'stays as the run measured it. Resolve must be '
                     'running.')
        if js and resolve_installed():
            state["resolve_json"] = js
            reason_set(only_resolve_env_curve, only_resolve, True, "",
                       what_for)
            only_resolve.setText(T('Create Resolve project'))
        else:
            reason_set(only_resolve_env_curve, only_resolve, False,
                         T('That needs the handover file from a run, and '
                           'there is none.')
                         if resolve_installed() else
                         T('The Resolve interface is not where it should be.'), what_for)

    def only_resolve_start_run():
        js = state.get("resolve_json")
        if not js or state["running"]:
            return
        output_show()
        log.clear()
        start_run.setEnabled(False)
        preview_button.setEnabled(False)
        only_resolve.setEnabled(False)
        only_resolve.setText(T('Resolve running ...'))
        state["running"] = True
        result_button_check()
        # Send the sliders from above along: the Resolve part recomputes the
        # cut list and should do so with what is in the fields now, not with
        # the values of the last run.
        argv = [sys.argv[0], "--resolve-json", js]
        # Where no number stands, the default applies -- nothing is aborted
        # here, the button should do something.
        values = {k: cut_var[k].get() for k in cut_var}
        part, bad = slider_argv(values)
        if bad:
            values[bad] = ""
            part, _s = slider_argv(values)
        argv += part
        if not edge_on.get():
            argv += ["--no-wide-edges"]
        threading.Thread(target=work_loop,
                         args=(argv,),
                         daemon=True).start()
        output_timer.start()

    only_resolve.clicked.connect(only_resolve_start_run)

    # ------------------------------------------------------------- The run
    write = make_log_writer(state, post)
    # The footer stands before this line and its break-off button says
    # into the log why it stopped. Reached back the way the other
    # forward references in here are reached.
    state["write"] = write

    output_timer = QtCore.QTimer(window)
    output_timer.setInterval(80)

    def clear():
        def drain():
            while True:
                try:
                    text = post.get_nowait()
                except queue.Empty:
                    return
                log.append_text(text)

        drain()
        if not state["running"]:
            # The run sets the flag after its last line, so what was
            # written between the two is still waiting here.
            drain()
            output_timer.stop()
            break_off.setVisible(False)
            start_run.setText(T('Start'))
            buttons_check()
            result_button_check()
            resolve_button_check()
            preview_compute()

    output_timer.timeout.connect(clear)
    PROGRAM.UPDATE_SINK = make_update_sink(state, write, output_show,
                                           output_timer)

    # Runs in the window thread while the worker thread waits.
    bridge.question.connect(
        lambda f: question_dialog(f, window, QtWidgets, label))

    def ask_user(possible, title=T('Question')):
        """A question from the worker thread; the dialog is the window's."""
        f = Question(possible, title)
        bridge_emit(bridge.question, f)
        f.event.wait()
        return f.choice

    def work_loop(argv):
        # A separator, so several runs of one session can be told apart
        # in the log.
        try:
            sys.stdout.write(T('\n=== Run %s ===\n\n')
                             % time.strftime("%Y-%m-%d %H:%M:%S"))
            sys.stdout.flush()
        except Exception:
            pass
        gui_run_loop(argv, state, write, ask_user, bridge, bridge_emit,
                     run_step_order)

    def summary_show(only_look):
        """Before the long run: what is about to happen, one line each.

        Everything in it is known or already measured; it has just not been
        shown anywhere. Aborting here costs nothing.
        """
        audio_files = [p for p, a in files if a == "audio"]
        videos_p = [p for p, a in files if a == "video"]
        kind_now = lambda p: clip_kind_value(p).get()
        content = [p for p in videos_p if kind_now(p) in CAMERA_TYPES]
        edge = [(kind_now(p), os.path.basename(p)) for p in videos_p
                if kind_now(p) not in CAMERA_TYPES]
        duration = window_length()
        lines = ["%s, %s%s"
                  % (TN(len(content), '%s camera', '%s cameras')
                     % group_text(len(content)),
                     TN(len(audio_files), '%s audio recording',
                        '%s audio recordings') % group_text(len(audio_files)),
                     ", " + duration if duration else "")]
        for kind, name in edge:
            lines.append("%s: %s" % (label_of(kind), name))
        who = without_own_camera(
            [(row, nv.get(), cv.get())
             for row, nv, cv in assign_lines],
            [(nv.get(), cv.get()) for _k, nv, cv in voice_lines],
            bool(multitrack.get()), state.get("voiced") or ())
        lines += camera_shortfall_lines(who, assign_lines, voice_lines)
        if without_auphonic() or not state.get("presets"):
            lines.append(T('Without processing at auphonic.com'))
        else:
            lines.append(T('Processing at auphonic.com with "%s"')
                          % (preset_plaintext() or "?"))
        lines += space_summary_lines(
            out_folder.get() or (os.path.dirname(videos_p[0])
                                  if videos_p else ""),
            audio_files, content, bool(multitrack.get()),
            start_var.get(), end_var.get())
        if only_look:
            lines.append("")
            lines.append(T('Dry run: only measuring, nothing written, '
                           'nothing uploaded.'))
        return ask(T('This is what happens next') if not only_look
                      else T('Dry run'),
                      "\n".join(lines),
                      T('Go ahead') if not only_look else T('Measure'))

    def start(only_look=False):
        if state["running"] or not files:
            return
        if not state.get("confirmed") and not summary_show(
                only_look):
            return
        # Where the camera audio is needed and not quite there yet, wait for it
        # -- but without freezing the window.
        if multitrack.get() and state.get("own_cameras") and prework_busy():
            if state["waiting"]:
                return          # a wait loop is already running
            state["waiting"] = True
            start_run.setEnabled(False)
            preview_button.setEnabled(False)

            def check_again():
                if not prework_busy():
                    state["waiting"] = False
                    state["confirmed"] = True
                    start(only_look)
                    return
                with prework_lock:
                    pending = len(prework_queue) + prework_run["threads"]
                start_run.setText(T('Camera audio, %s to go ...')
                                  % group_text(pending))
                QtCore.QTimer.singleShot(300, check_again)

            check_again()
            return
        state["waiting"] = False
        state["confirmed"] = False
        start_run.setText(T('Start'))
        buttons_check()
        # The "Cameras only" question stood here until 25.8.2026: it
        # fired on the rule that made every camera a track by itself, and
        # that rule is gone. A selection with no sound in use never gets
        # this far now -- what_missing holds the button and says why.
        # The prework is done, and its display has no business in the file list
        # any more.
        for file_path, (node, original) in list(prework_node.items()):
            try:
                node.setText(2, original)
            except RuntimeError:
                prework_node.pop(file_path, None)
        # Collect what is in the interface once as plain values; run_argv
        # builds the command line from them. The whole decision about what a
        # run does sits there, and can be tested without opening a window.
        def audio_done_of(row):
            try:
                return prework_done.get(prework_api_key(row[0]))
            except OSError:
                return None

        own_flag = state.get("own_audio_rows", set())
        values = {
            # The tracks, not the files they came out of: a recorder
            # file holding four channels goes into the run as four.
            "files": files_for_run(),
            "clip_kinds": {p: value.get() for p, value in clip_kind_values.items()},
            "out_folder": out_folder.get(),
            "dry_run": bool(only_look),
            "multitrack": bool(multitrack.get()),
            "camera_audio_only": bool(state["camera_audio"]),
            "rows": [{"blocks": list(row),
                        "speakers": nv.get(),
                        "camera_choice": cv.get(),
                        "own_audio": row[0] in own_flag,
                        "from_camera": (own_flag.get(row[0])
                                        if isinstance(own_flag, dict) else ""),
                        "audio_done": audio_done_of(row)}
                       for row, nv, cv in assign_lines],
            "cameras": [{"path": p, "name": v.get()}
                        for p, v, _k, _n in camera_lines],
            "production": production_var.get(),
            "in_point": start_var.get(),
            "out_point": end_var.get(),
            "cut": {k: cut_var[k].get() for k in cut_var},
            "wide_at_edges": bool(edge_on.get()),
            # The voices this machine has already taken apart. They
            # travel with the run so it need not separate them again.
            "speakers_of": speakers_for_run(state, voice_lines),
            # A no given in the window has to reach the run: it would
            # otherwise pick a source itself and separate after all.
            "speakers_wanted": state.get("speakers_wanted"),
            # Which camera each voice belongs to. The run cannot work
            # that out: a voice has no file to be assigned by.
            "voices": [{"name": nv.get().strip(), "camera": cv.get()}
                       for _k, nv, cv in voice_lines],
            # Without auphonic.com: the key stays in the field but this run
            # does not see it.
            "key": "" if without_auphonic() else key_var.get(),
            "preset": preset_plaintext(),
            "done_folder": done_folder.get(),
            "speech_language": speech_language.get().strip(),
            "lufs": lufs_value.get(),
            "apart": sorted(no_join),
            "together": together_now(),
        }
        assign_file = ""
        if multitrack.get() or state.get("speakers_local"):
            fd, assign_file = tempfile.mkstemp(prefix="vpm_assign_",
                                           suffix=".json")
            os.close(fd)
        argv, wishes, messages = run_argv(values, assign_file)

        def discard():
            if assign_file:
                try:
                    os.remove(assign_file)
                except OSError:
                    pass

        for kind, title, text, button in messages:
            if kind == "question":
                if not ask(title, text, button):
                    discard()
                    return
            else:
                report(title, text)
                discard()
                return
        if argv is None:
            discard()
            return
        if wishes is not None:
            with open(assign_file, "w", encoding="utf-8") as f:
                json.dump(wishes, f, ensure_ascii=False, indent=1)
        # What is already there gets overwritten, so show what first.
        if not only_look:
            already_present = []
            for p, v, _k, _n in camera_lines:
                folder = out_folder.get() or os.path.dirname(p)
                target = os.path.join(folder, (v.get().strip()
                                             or os.path.splitext(
                                                 os.path.basename(p))[0])
                                    + ".mov")
                if os.path.exists(target):
                    already_present.append("%s   (%s)"
                                    % (os.path.basename(target),
                                       as_data_size(size_in_mb(target))))
            if already_present and not ask(
                    T('Overwrite files'),
                    T('These files exist already and will be written '
                      'again:\n\n  %s\n\nIs that intended?')
                    % "\n  ".join(already_present[:12]), T('Overwrite')):
                discard()
                return
        output_show()
        log.clear()
        state["results"] = []
        start_run.setEnabled(False)
        preview_button.setEnabled(False)
        only_resolve.setEnabled(False)
        start_run.setText(T('Preview running ...') if only_look else T('running ...'))
        state["running"], state["dry_run"] = True, bool(only_look)
        # Held now: the preset box can be turned while the run goes on.
        state["run_auphonic"] = not without_auphonic()
        break_off_arm(break_off)
        run_plan_build()
        result_button_check()
        project_write(argv)      # the dry run too: same hand work
        threading.Thread(target=work_loop, args=(argv,), daemon=True).start()
        output_timer.start()

    start_run.clicked.connect(lambda: start(False))
    preview_button.clicked.connect(lambda: start(True))

    # As large as the screen, but an ordinary window.
    screen = app.primaryScreen().availableGeometry()
    window.resize(min(1600, screen.width()), min(1000, screen.height()))
    window.setMinimumSize(1000, 520)
    window.move(screen.left(), screen.top())

    def clean_up():
        """Write first -- closing used to save nothing. Then stop."""
        state["closing"] = True
        try:
            axis_store(state.get("axis") or {})
            watchdog.stop()
            total_clock.stop()
            output_timer.stop()
            if getattr(player, "player", None) is not None:
                player.player.stop()
                player.track.stop()
        except Exception:
            pass

    app.aboutToQuit.connect(clean_up)

    items_fresh()
    folder_show()
    state["cut_box_there"] = True    # the cut box stands, so it can be read
    wide_state_show()
    preview_compute()
    # No fetch at start-up, not even with a key that is remembered.
    # Laid down 23.8.2026: it may not happen by itself. A start that
    # speaks to auphonic.com unasked is a start that speaks to a third
    # party about a key it was only asked to keep. The presets are
    # fetched when somebody opens the list -- that is the moment they
    # are wanted, and the only moment they are needed.
    # The later sheets exist from the start. Time window, player and Resolve
    # are needed on the simple path too.
    # ------------------------------------------------------- The menu
    # A Mac program without a menu bar is not a Mac program: About,
    # Settings and Help are expected in places the window itself has no
    # say over. QLayout.setMenuBar hands it to the system menu bar on a
    # Mac and puts it at the top of the window everywhere else.
    menu = build_menus(QtGui, QtCore, QtWidgets, window, tabs, player, {
        "add files": add_files, "remove": remove,
        "output folder": folder_pick,
        "start": lambda: start_run.click(),
        "dry run": lambda: preview_button.click(),
        "settings": lambda: settings_open(),
        "open project": lambda: project_open(),
        "save project": project_save, "close project": project_new,
        "mark in": lambda: limit_set(start_var),
        "mark out": lambda: limit_set(end_var),
        "to in": lambda: to_limit(start_var.get(), "In point"),
        "to out": lambda: to_limit(end_var.get(), "Out point")},
        window_switch, cut_player, late,
        (remove_button, start_run, preview_button),
        lambda: bool(files) or bool(state.get("project_from")))
    vertical.setMenuBar(menu)
    window_enable()    # after the menu: its four player entries join the list
    buttons_check()    # and its five file entries follow the buttons

    def scheme_changed(*_):
        """Follow a desktop switched between light and dark while running.

        What is held centrally is rebuilt: the palette, the style
        sheet of the whole program, the stripes and marks of the file
        list, the rails of the players, and the clip colours, which
        the preview works out again. What a single widget baked into
        its own style sheet when it was built is swapped over role by
        role, so those rows follow as well.

        The log pane is neither: its colours sit in text formats, which
        no style sheet swap reaches, and its content cannot be built
        again. It repaints itself from the kind noted on every line.
        """
        dark = desktop_is_dark(QtWidgets, QtGui)
        if dark == ON_DARK[0]:
            return
        colours_pick(dark)
        app_style_set(app)
        styles_follow_scheme(app, dark)
        log.colours_apply()
        stripes_pick()
        marks_pick()
        for rail in window.findChildren(WindowSlider):
            rail.colours_apply()
        items_fresh()
        buttons_check()
        # The clip colours follow ON_DARK, but only where they are
        # worked out afresh -- the cut already drawn carries the ones
        # it was built with.
        preview_kick_off()

    try:
        app.styleHints().colorSchemeChanged.connect(scheme_changed)
    except AttributeError:
        # Qt without that signal leaves the palette as it was found at
        # the start, which is how it behaved before.
        pass

    mode_toggled()
    window.show()
    mark_time("the window is up")
    # A moment after the window is up, not before: the first thing
    # somebody sees should be their files, not a question about updates
    # -- unless ffmpeg is too old, which comes at once.
    QtCore.QTimer.singleShot(0, lambda: after_window(window, app, QtCore))
    return app.exec()




#------------------------------------------------ Once the window stands
# What the window opens after it is up: the player menu, the
# offers for a missing tool, the boxes about this version and the
# next one, and the preset list it fetches when it is opened.


def player_menu(menu, player):
    """The player menu, greyed out where there is no player.

    A Qt without multimedia hands out the stand-in, which plays nothing
    here -- it opens ffplay in a window of its own. Every entry in this
    menu would then do nothing, and an entry that does nothing is worse
    than one that is visibly not available.
    """
    out = menu.addMenu(T('&Player'))
    out.menuAction().setEnabled(getattr(player, "plays", True))
    return out


def after_window(window, app, QtCore):
    """What the window does once it stands there, in the order it does it.

    Below the ffmpeg floor there is nothing behind the box, so it comes
    at once and the run ends behind it. Otherwise the update question,
    a moment later.
    """
    if PROGRAM.TOOL_TROUBLE[0]:
        return tools_offer(window, app)
    if soxr_offer(window):
        return None
    QtCore.QTimer.singleShot(1500, lambda: update_offer(window))


def tools_offer(window, app):
    """The one thing the window offers below the ffmpeg floor.

    A box on the window rather than a line anywhere: nothing is ever
    said in front of the window, and there is no console to say it in.
    Answered with Quit, the run ends. Answered with the button it does
    not: the install writes into the Output tab, and somebody has to
    be able to read what it said there.
    """
    QtWidgets = _qt_widgets()
    kind, says = PROGRAM.TOOL_TROUBLE
    box = QtWidgets.QMessageBox(window)
    box.setWindowTitle("ffmpeg")
    box.setText(says)
    printed = how_to_get_ffmpeg(kind != "missing")
    # What the button lets somebody in for, before they press it: a
    # package manager may build from source and a built one is over a
    # hundred megabytes, so either way it is minutes rather than
    # seconds. Only where there is a button to press.
    box.setInformativeText(
        T('Nothing runs until that is put right.') + ("\n\n" + T(
            'Getting it takes a few minutes, and what it says appears '
            'under Output.') if ffmpeg_can_be_had() else ""))
    do = None
    if ffmpeg_can_be_had() or sys.platform == "win32":
        do = box.addButton(T('Get it: %s') % printed,
                           QtWidgets.QMessageBox.AcceptRole)
    box.addButton(T('Quit'), QtWidgets.QMessageBox.RejectRole)
    trouble_log("ffmpeg -- %s" % says)
    box.exec()
    if do is not None and box.clickedButton() is do:
        if install_watched(window, app, kind != "missing"):
            return True
        # No window to show it in -- the way it went before, and then
        # the run ends as it always did.
        install_ffmpeg(update=kind != "missing", asked=True)
    app.quit()
    return False


def soxr_offer(window):
    """Offer a finer ffmpeg where this one has no soxr. True if it was taken.

    Not a gate: the run goes on either way, and that is the whole
    difference from the box above. Asked once per version and then
    written down -- a box that comes back at every start over
    something that is not broken is a box people learn to click away.
    """
    if os.environ.get("VPM_SILENT") or not ffmpeg_can_be_had():
        # A test run is offered nothing, and neither is a machine with
        # no way of getting a better build.
        return False
    if soxr_available() or settings().get("soxr-asked") == VERSION:
        return False
    QtWidgets = _qt_widgets()
    box = QtWidgets.QMessageBox(window)
    box.setWindowTitle("ffmpeg")
    box.setText(soxr_note())
    box.setInformativeText(
        T('Everything works without it. Getting a build that has it '
          'takes a few minutes, and what it says appears under Output.'))
    do = box.addButton(T('Get it: %s') % how_to_get_ffmpeg(True),
                       QtWidgets.QMessageBox.AcceptRole)
    box.addButton(T('Carry on'), QtWidgets.QMessageBox.RejectRole)
    keep_setting("soxr-asked", VERSION)
    box.exec()
    if box.clickedButton() is not do:
        return False
    return bool(install_watched(window, None, True))


def install_watched(window, app, update):
    """Get ffmpeg with what it says under Output, not behind the window.

    Before this the command ran in the window's own thread with its
    output going nowhere anybody could see. This is the road the
    update already takes: a thread of its own while the window stays
    alive, and every line into the Output tab. Nothing is ended here
    -- a window that stays open is one somebody can read the failure
    in. False where there is no window to show it in.
    """
    if PROGRAM.UPDATE_SINK is None:
        return False
    ended = []

    def job(say):
        trouble = install_job(update, say)
        ended.append(trouble)
        return trouble

    PROGRAM.UPDATE_SINK(job)
    restart_when_done(window, ended, ffmpeg_in_place())
    return True


def install_job(update, say):
    """The install itself, every line to *say*. Trouble, or "" when done.

    What somebody let themselves in for stands first, before the
    manager's own first line: this may build from source, and that is
    minutes rather than seconds. Every line goes into the log beside
    the pane as well -- what the pane holds is gone when the window
    goes, and the file is where somebody is sent afterwards.
    """
    def line(text):
        said = text if text.endswith("\n") else text + "\n"
        log_aside(said.rstrip("\n"))
        say(said)

    line("")
    line(as_head(T('Installing ffmpeg')))
    line(T('This takes a few minutes -- a package manager may build '
           'from source. What it says appears here.'))
    watched, stop = sign_of_life(line, say)
    try:
        good = install_ffmpeg(update=update, asked=True, say=watched)
    finally:
        stop()
    # Asked again, not taken on trust: a package manager can report
    # success having just laid down an ffmpeg still too old for this.
    forget_soxr()
    if good and not find_required_tools()[0]:
        line(as_good(T('That worked.')))
        # What really arrived, asked rather than announced: nothing
        # here promises soxr, so nothing here may claim it either.
        line("  " + soxr_note())
        line(T('Start the program again to pick it up.'))
        return ""
    return T('Nothing runs until that is put right. This way: %s') \
        % how_to_get_ffmpeg(update)


def restart_when_done(window, ended, said):
    """Wait for the job in the other thread, then offer the restart.

    A timer rather than a call out of that thread: a box belongs to
    the window's own thread and to no other. It stops itself either
    way, and it offers nothing where the job came back with trouble
    -- there is nothing to pick up then. *said* is the words.
    """
    from PySide6 import QtCore
    watch = QtCore.QTimer(window)
    watch.setInterval(300)

    def look():
        if not ended:
            return
        watch.stop()
        if ended[0] == "":
            restart_offer(window, said)

    watch.timeout.connect(look)
    watch.start()
    return watch


def ffmpeg_in_place():
    """What the restart box says once ffmpeg arrived: title, head, rest."""
    return ("ffmpeg", T('ffmpeg is in place.'),
            T('The program reads it when it starts. It can start again '
              'now, or you can do that yourself later.'))


def version_in_place(tag):
    """What the restart box says once that version arrived.

    Three things somebody needs and cannot see: which version is now
    on the disc, that the window in front of them is still the old
    one, and that they may take the restart or leave it.
    """
    return ("Video Podcast Magic", T('%s is in place.') % tag,
            T('This window is still the version it started as. It can '
              'start again now and come up as the new one, or you can '
              'do that yourself later.'))


def restart_offer(window, said):
    """Say in a box what arrived, and offer the restart. *said* is the words.

    A box rather than a line: in the Output tab that sentence is the
    last of two hundred the package manager wrote, and it goes under
    there. The box holds nothing up -- the window's timers go on
    turning inside it, so a pane still filling keeps filling, which is
    measured. True where somebody asked for the restart.
    """
    if os.environ.get("VPM_SILENT"):
        return False
    title, arrived, rest = said
    QtWidgets = _qt_widgets()
    box = QtWidgets.QMessageBox(window)
    box.setWindowTitle(title)
    box.setText(arrived)
    box.setInformativeText(rest)
    do = box.addButton(T('Start again now'),
                       QtWidgets.QMessageBox.AcceptRole)
    box.addButton(T('Later'), QtWidgets.QMessageBox.RejectRole)
    box.exec()
    if box.clickedButton() is not do:
        return False
    start_again()
    # Only reached where the start failed: one that works never comes
    # back. So it is said where the offer stood, and not on a console
    # this program does not have.
    warn_box(QtWidgets, window, title,
             T('Starting again did not work. Close the window and '
               'start the program the way you did before.'))
    return True


def about_show(window):
    """Show what this program is, which version, and under what terms."""
    QtWidgets = _qt_widgets()
    box = QtWidgets.QMessageBox(window)
    box.setWindowTitle(T('About Video Podcast Magic'))
    box.setText("Video Podcast Magic %s" % VERSION)
    box.setInformativeText(
        T('Raw material from a video podcast becomes an edited '
          'episode: the good audio out of the video files, the '
          'cameras on one time axis, a first cut by speaker, and a '
          'DaVinci Resolve project.')
        + "\n\n"
        + T('Python %s on %s') % (platform.python_version(),
                                  platform.system())
        + "\n\n"
        + T('MIT licence, Copyright (c) 2026 Sebastian Lotz. Handed '
            'over as it is, without warranty of any kind.'))
    box.exec()


RELEASE_BY_TAG = ("https://api.github.com/repos/Bascht74/videopodcast-magic"
                  "/releases/tags/%s")


def release_text_of(tag):
    """What the release with that tag says about itself, or "".

    Asked for by name, because "what changed in this version" is about
    the one running here and not about the newest one there. One
    question for a text, nothing sent.
    """
    if UPDATE_OFF or not tag:
        return ""
    try:
        import urllib.request
        with urllib.request.urlopen(RELEASE_BY_TAG % tag,
                                    context=https_context(),
                                    timeout=20) as answer:
            return str(json.load(answer).get("body") or "").strip()
    except Exception:
        return ""






def story_window(window, title, said, changed, page=""):
    """One window with a heading, a text that scrolls, and a way out.

    Two places show a release text and they used to build the same
    dialog twice. *page* is left out where there is nothing to look up
    -- a link under a text somebody is already reading is an offer to
    read it somewhere else.
    """
    QtWidgets = _qt_widgets()
    from PySide6 import QtCore
    box = QtWidgets.QDialog(window)
    box.setWindowTitle(title)
    box.resize(680, 520)
    rows = QtWidgets.QVBoxLayout(box)
    if said:
        head = QtWidgets.QLabel(said)
        font = head.font()
        font.setBold(True)
        head.setFont(font)
        head.setWordWrap(True)
        rows.addWidget(head)
    story = QtWidgets.QPlainTextEdit(release_text_in(changed))
    story.setReadOnly(True)
    # The bar stands there whether it is needed or not, as in the
    # update dialog: a text that scrolls without one looks like a text
    # that ends where the frame does.
    story.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
    story.setLineWrapMode(QtWidgets.QPlainTextEdit.WidgetWidth)
    story.setAccessibleName(title)
    rows.addWidget(story, 1)
    if page:
        where = QtWidgets.QLabel(page)
        where.setStyleSheet("color: %s;" % COLOURS["quiet"])
        where.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        rows.addWidget(where)
    feet = QtWidgets.QHBoxLayout()
    rows.addLayout(feet)
    feet.addStretch(1)
    # Qt translates its own standard buttons, so this one does not go
    # through the catalogue: an entry that reads the same in both
    # languages looks like English somebody forgot.
    fine = QtWidgets.QDialogButtonBox(
        QtWidgets.QDialogButtonBox.Ok, parent=box)
    fine.accepted.connect(box.accept)
    feet.addWidget(fine)
    box.exec()


def changes_shown(window):
    """Show what changed in the version running here.

    It used to open a browser at the changelog of the whole project,
    where somebody then looked for their own version among all the
    others. Settled 31.8.2026: show the text here, the way the
    update window does -- without its buttons, and about this version
    rather than the new one.
    """
    QtWidgets = _qt_widgets()
    changed = release_text_of("v" + VERSION) or release_text_of(VERSION)
    if not changed:
        QtWidgets.QMessageBox.information(
            window, T('What changed in this version'),
            T('The text for %s could not be fetched.') % VERSION)
        return
    story_window(window, T('What changed in this version'), "", changed)


def newest_shown(window, page, changed):
    """Say that this is the newest, and show what is in it.

    Asked for on 24.8.2026, at the box that only said "no newer
    version found": show the last changelog here as well. The release
    text comes down with the same answer that was asked for the
    version number, so it costs nothing, and whoever just asked has
    earned more than a full stop.

    Without the text this stays what it was: one line and a button.
    """
    QtWidgets = _qt_widgets()
    said = T('No newer version found. This one is %s.') % VERSION
    if not changed:
        QtWidgets.QMessageBox.information(
            window, T('Look for a newer version now'), said)
        return
    story_window(window, T('Look for a newer version now'), said, changed,
                 page)


def preset_box_widget(QtWidgets, state, fetch):
    """The class for the preset list, which fetches itself when opened.

    Opening the list is the moment somebody wants to know what
    auphonic.com has. Before that the program does not ask it anything
    -- not at start-up, not in the background.

    Fetching takes a moment, and the list used to open on the one entry
    it already had while the answer was still on its way. Whoever
    opened it saw nothing and closed it, and the presets arrived into a
    list nobody was looking at any more. They were there on the second
    opening, and nobody opens twice. So it says it is fetching, and
    whoever receives them opens it again.

    A factory rather than a class inside gui(): it needs three names
    from there and nothing else, and coding_guidelines section 12 keeps
    out of gui() what does not have to be in it.
    """

    class PresetBox(QtWidgets.QComboBox):

        def showPopup(self):
            if not state.get("presets") and not state.get("presets_busy"):
                state["presets_open_after"] = True
                fetch()
                if state.get("presets_busy"):
                    self.addItem(T('fetching from auphonic.com ...'), "")
                    self.model().item(self.count() - 1).setEnabled(False)
            QtWidgets.QComboBox.showPopup(self)

    return PresetBox


def preset_list_bring(state, fetch, apply_wish):
    """Bring the preset list up after a project was opened.

    The list is otherwise only fetched when somebody opens the box --
    so a project carrying a preset finds nothing to put it in, and the
    box says "without auphonic.com", which the project did not ask for.
    """
    if (state.get("preset_wanted") and not state.get("presets")
            and not state.get("presets_busy")):
        fetch()
    else:
        apply_wish()


def preset_box_fill(box, entries, state, none_value):
    """Put the rows into the preset list and pick what is wanted.

    Without auphonic.com stays selected until somebody picks: landing
    on the first entry of an arriving list would spend credit because
    a list came. The wish is what stood there before, or what a
    project brought; where the list cannot hold it -- key refused, no
    net -- it stays in *state*, or the stand-in would be stored.
    """
    before_value = box.currentData() or ""
    box.blockSignals(True)
    box.clear()
    for value, text, pickable in entries:
        box.addItem(text, value)
        if not pickable:
            box.model().item(box.count() - 1).setEnabled(False)
    box.setCurrentIndex(0)
    box.setEnabled(True)
    wanted = state.get("preset_wanted") or before_value or ""
    if wanted:
        i = box.findData(wanted)
        if i >= 0:
            box.setCurrentIndex(i)
            state.pop("preset_wanted", None)
        elif wanted != none_value:
            state["preset_wanted"] = wanted
            # Not in the list yet -- being fetched, or refused. A row
            # says so; its value stays "without auphonic.com", so a run
            # before the answer spends nothing.
            box.addItem(T('%s -- being checked') % wanted, none_value)
            box.model().item(box.count() - 1).setEnabled(False)
            box.setCurrentIndex(box.count() - 1)
    box.blockSignals(False)
    # What the box was asked for and what it settled on. A wish left
    # standing is the sign that the list could not hold it -- which is
    # how a preset can be in the project file and not on the screen.
    gui_log("presets: %d in the list, wanted %r, before %r -> %r%s"
             % (box.count(), state.get("preset_wanted") or "", before_value,
                box.currentData(),
                "" if not state.get("preset_wanted") else " (not placed)"))


def preset_entries(presets, multitrack_on, none_label, none_value):
    """The rows of the preset list: (value, text, can be picked).

    The first row is not a preset but the decision to run without
    auphonic.com. It is always there, including without a checked key,
    because then it applies anyway.

    Where the list came back and holds nothing to pick, a grey row says
    so where the question is asked. Asked for on 24.8.2026: the list
    used to come back with its single row and nothing to explain it,
    which reads like a key that was refused.

    Three states, and they are not the same thing. *presets* is None
    while nobody has looked yet -- then nothing is said, because
    nothing is known. An empty list is an account that carries no
    preset of its own. A full list with nothing fitting is an account
    that carries presets, none of them for this mode.

    "Of your own" and not "in the account": auphonic.com has presets of
    its own, and the interface does not hand them out. We only ever
    see what somebody made there, and that is all we may claim.
    """
    kind = (T('Multitrack mode') if multitrack_on
            else T('Singletrack mode'))
    rows = [(none_value, none_label, True)]
    fitting = [(n, mt) for n, _u, mt in (presets or [])
               if preset_fits_mode(mt, multitrack_on)]
    for name, mark in fitting:
        # The bracket names the mode, so it may only stand where the
        # mode is known. A preset auphonic.com did not classify is
        # offered under its own name and nothing more.
        rows.append((name, "%s  (%s)" % (name, kind) if mark is not None
                     else name, True))
    if presets is None or fitting:
        return rows
    if presets:
        none_yet, no_multi, no_single = preset_missing_rows()
        rows.append(("", no_multi if multitrack_on else no_single, False))
    else:
        rows.append(("", preset_missing_rows()[0], False))
    return rows


def preset_missing_rows():
    """The three sentences a list with nothing to pick can carry.

    In one place because two callers need them: the list puts one of
    them in, and the field they stand in has to be wide enough for the
    widest. Order: no preset at all, no Multitrack one, no Singletrack
    one.

    They say "of your own" and not "in the account". auphonic.com has
    presets of its own and the interface does not hand them out, so
    all we ever see is what somebody made there -- and that is all we
    may claim.
    """
    return (T('No preset of your own -- create one on auphonic.com'),
            T('No Multitrack preset of your own -- create one'),
            T('No Singletrack preset of your own -- create one'))


def preset_mode_note(preset_list, multitrack_on):
    """What to say where the list came back and shows nothing.

    The presets are filtered by the mode, and an account without one of
    the kind in use leaves the list at its single entry. Coming back
    full and then showing empty reads like a key that was refused. It
    is not: it is an account without a preset of this kind, and saying
    so costs one sentence.

    Returns (sentence or "", the presets that fit).
    """
    fitting = [n for n, _u, mt in (preset_list or [])
               if preset_fits_mode(mt, multitrack_on)]
    if not preset_list or fitting:
        return "", fitting
    return ((T('The key is good. Of the %s presets in the account none '
               'is a Multitrack one, so the list stays empty.')
             if multitrack_on else
             T('The key is good. Of the %s presets in the account none '
               'is a Singletrack one, so the list stays empty.'))
            % group_text(len(preset_list)), fitting)


def update_offer(window, asked=False):
    """Ask about looking for updates, look, and offer the new one.

    Everything here happens in the window: the command line is left
    alone on purpose, because a run started from a script must not
    stop to ask anything.

    *asked* is somebody choosing to look from the menu. Then there is
    an answer either way -- silence after a click reads like a program
    that did nothing.
    """
    QtWidgets = _qt_widgets()
    tag, page, changed, trouble = newer_release(asked)
    if not tag:
        if asked:
            # Switched off, or unable to look at all: both mean nothing
            # was seen, and calling this the newest version would then
            # be a guess.
            if UPDATE_OFF or trouble:
                QtWidgets.QMessageBox.information(
                    window, T('Look for a newer version now'),
                    trouble or T('The check for new versions is '
                                 'switched off here.'))
            else:
                newest_shown(window, page, changed)
        return
    # A dialog of its own rather than a QMessageBox: the box hides what
    # changed behind a "Show Details" button of its own making, which
    # it does not translate, and gives it four lines to be read in.
    # What somebody is about to install is not a detail.
    from PySide6 import QtCore
    owner = installed_by_a_package_manager()
    box = QtWidgets.QDialog(window)
    box.setWindowTitle(T('A newer version is out'))
    box.resize(680, 560)
    rows = QtWidgets.QVBoxLayout(box)

    head = QtWidgets.QLabel(T('%s is out. This is %s.') % (tag, VERSION))
    font = head.font()
    font.setBold(True)
    head.setFont(font)
    rows.addWidget(head)

    said = QtWidgets.QLabel(update_promise(owner))
    said.setWordWrap(True)
    rows.addWidget(said)

    if changed:
        rows.addWidget(QtWidgets.QLabel(T('What changed since %s:') % VERSION))
        story = QtWidgets.QPlainTextEdit(changed)
        story.setReadOnly(True)
        # The bar stands there whether it is needed or not: a text that
        # scrolls without one looks like a text that ends where the
        # frame does.
        story.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOn)
        story.setLineWrapMode(QtWidgets.QPlainTextEdit.WidgetWidth)
        story.setAccessibleName(T('What changed since %s:') % VERSION)
        rows.addWidget(story, 1)
    if page:
        where = QtWidgets.QLabel(page)
        where.setStyleSheet("color: %s;" % COLOURS["quiet"])
        where.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        rows.addWidget(where)

    quiet = QtWidgets.QCheckBox(T('Skip this version'))
    quiet.setToolTip(T('Only this one. The next release asks again, and '
                       'Help > Look for a newer version now asks at any '
                       'time.'))
    rows.addWidget(quiet)

    feet = QtWidgets.QHBoxLayout()
    rows.addLayout(feet)
    feet.addStretch(1)
    later = QtWidgets.QPushButton(T('Later'))
    later.clicked.connect(box.reject)
    feet.addWidget(later)
    now = QtWidgets.QPushButton(T('Update'))
    now.setDefault(True)
    now.clicked.connect(box.accept)
    feet.addWidget(now)

    answered = box.exec()
    if quiet.isChecked():
        # Only this one version, and remembered whichever button was
        # pressed: somebody who ticks it and then updates anyway still
        # meant it about this one.
        set_update_skipped(tag)
    if answered != QtWidgets.QDialog.Accepted:
        return
    trouble = update_watched(window, tag, owner)
    if trouble:
        warn_box(QtWidgets, window, T('A newer version is out'), trouble)


def update_watched(window, tag, owner):
    """Put that version in place and offer the restart once it is in.

    update_fetched hands pip to the window and comes back while pip is
    still fetching, so a box said there would be said too early. The
    sink is wrapped for that one call instead: what the job ended with
    lands in a list, and the timer the ffmpeg install uses turns it
    into the box. Trouble, or "".
    """
    ended = []
    sink = PROGRAM.UPDATE_SINK

    def watched(job):
        def watch(say):
            trouble = job(say)
            ended.append(trouble)
            return trouble

        sink(watch)

    if sink is not None:
        PROGRAM.UPDATE_SINK = watched
    try:
        trouble = update_fetched(tag, owner)
    finally:
        PROGRAM.UPDATE_SINK = sink
    # Only the road pip takes: the other one writes over a loose file
    # and starts again by itself, so there is nothing left to offer.
    if not trouble and owner:
        restart_when_done(window, ended, version_in_place(tag))
    return trouble


def restore_offer(window):
    """Ask which earlier version, then hand that one to pip.

    The way somebody takes when the newer version has just gone wrong
    on them, and it is asked with the weight of the update itself: it
    decides which program runs from the next start. A list and not one
    name, because the version that broke something is not always the
    one before this, and the one before this is only the first guess.
    """
    QtWidgets = _qt_widgets()
    title = T('Back to an earlier version')
    owner = installed_by_a_package_manager()
    if not owner:
        # Nothing pip keeps a record of, so there is nothing for pip to
        # put back. Said before a list is fetched that could not be
        # acted on anyway.
        warn_box(QtWidgets, window, title, not_installed_note())
        return
    older, trouble = older_releases(VERSION)
    if trouble or not older:
        # Two different answers, and they must not read alike: one says
        # nothing older is out, the other says nobody could look.
        QtWidgets.QMessageBox.information(
            window, title,
            trouble or T('No version earlier than %s is out that pip can '
                         'install.') % VERSION)
        return
    box = QtWidgets.QDialog(window)
    box.setWindowTitle(title)
    box.setMinimumWidth(620)
    rows = QtWidgets.QVBoxLayout(box)
    rows.setContentsMargins(18, 16, 18, 14)
    rows.setSpacing(14)
    head = QtWidgets.QLabel(
        T('This is %s. Which version shall pip put in its place?')
        % VERSION)
    font = head.font()
    font.setBold(True)
    head.setFont(font)
    rows.addWidget(head)
    picked = QtWidgets.QComboBox()
    picked.addItems(older)
    picked.setCurrentIndex(older.index(back_pick(older)))
    speaks_as(picked, title)
    rows.addWidget(picked)
    # What a step back does not do stands here rather than nowhere: it
    # is the one thing about it that surprises people, and afterwards
    # is too late.
    said = QtWidgets.QLabel(
        T('pip fetches it into %s, and what pip says appears under '
          'Output. The version chosen here runs from the next '
          'start.\n\nIt brings the program back and nothing else. What '
          'a newer version wrote into the settings stays written, and '
          'projects and their files are left as they are.') % owner)
    said.setWordWrap(True)
    rows.addWidget(said)
    feet = QtWidgets.QHBoxLayout()
    rows.addLayout(feet)
    feet.addStretch(1)
    later = QtWidgets.QPushButton(T('Later'))
    later.clicked.connect(box.reject)
    feet.addWidget(later)
    now = QtWidgets.QPushButton(T('Go back'))
    now.setDefault(True)
    now.clicked.connect(box.accept)
    feet.addWidget(now)
    if box.exec() != QtWidgets.QDialog.Accepted:
        return
    # The same road as the update, down to the command: pip is handed
    # the tag that was chosen, and its lines go into the Output tab.
    trouble = update_fetched(picked.currentText(), owner)
    if trouble:
        warn_box(QtWidgets, window, title, trouble)


def _qt_widgets():
    """QtWidgets, without carrying it down from the caller."""
    from PySide6 import QtWidgets
    return QtWidgets
