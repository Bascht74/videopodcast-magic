# -*- coding: utf-8 -*-
"""The window, and everything it shows, asks or offers.

A piece of the program, read out by beside(). It cannot import the
file it was cut out of -- that file is still being read -- so the
program is handed in, and every name used out of it is bound below.
"""

# beside() puts the program here before this file is read.
PROGRAM = PROGRAM

# What this piece uses, bound once. What the program changes while it
# runs stays PROGRAM.something below: a copy would part from it.
AUDIO_MATERIAL = PROGRAM.AUDIO_MATERIAL
AUDIO_SUFFIXES = PROGRAM.AUDIO_SUFFIXES
AUDIO_UNUSED = PROGRAM.AUDIO_UNUSED
AUDIO_USE = PROGRAM.AUDIO_USE
ByFile = PROGRAM.ByFile
CAMERA_TYPES = PROGRAM.CAMERA_TYPES
CLIP_TYPES = PROGRAM.CLIP_TYPES
COLOURS = PROGRAM.COLOURS
FILE_FORMAT = PROGRAM.FILE_FORMAT
FileSet = PROGRAM.FileSet
Finding = PROGRAM.Finding
IGNORE_AUDIO = PROGRAM.IGNORE_AUDIO
MIX_ONLY = PROGRAM.MIX_ONLY
ON_DARK = PROGRAM.ON_DARK
PRESET_NONE = PROGRAM.PRESET_NONE
PROJECT_PREFIX = PROGRAM.PROJECT_PREFIX
ProgressPlan = PROGRAM.ProgressPlan
RUN_STOP = PROGRAM.RUN_STOP
SPEAKER_ROWS_SHOWN = PROGRAM.SPEAKER_ROWS_SHOWN
SPEAKER_SPLIT_OFF = PROGRAM.SPEAKER_SPLIT_OFF
SPEAKER_SPLIT_SPEED = PROGRAM.SPEAKER_SPLIT_SPEED
SPEAKER_STATE = PROGRAM.SPEAKER_STATE
SPEECH_CODES = PROGRAM.SPEECH_CODES
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
audio_clock_of = PROGRAM.audio_clock_of
audio_start_of = PROGRAM.audio_start_of
audio_summary = PROGRAM.audio_summary
axis_answer_kept = PROGRAM.axis_answer_kept
axis_still_valid = PROGRAM.axis_still_valid
axis_with_blocks = PROGRAM.axis_with_blocks
axis_worth_measuring = PROGRAM.axis_worth_measuring
back_pick = PROGRAM.back_pick
beside = PROGRAM.beside
blocks_facts = PROGRAM.blocks_facts
build_handover = PROGRAM.build_handover
camera_after_a_mark = PROGRAM.camera_after_a_mark
camera_gets_from = PROGRAM.camera_gets_from
camera_name_suggestion = PROGRAM.camera_name_suggestion
camera_row_cameras = PROGRAM.camera_row_cameras
camera_start_of = PROGRAM.camera_start_of
camera_to_remember = PROGRAM.camera_to_remember
cameras_in_track_order = PROGRAM.cameras_in_track_order
cameras_with_a_speaker = PROGRAM.cameras_with_a_speaker
cameras_with_own_audio = PROGRAM.cameras_with_own_audio
channel_count = PROGRAM.channel_count
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
guess_camera_name = PROGRAM.guess_camera_name
guess_production_name = PROGRAM.guess_production_name
guess_speaker_name = PROGRAM.guess_speaker_name
gui_log = PROGRAM.gui_log
has_sound = PROGRAM.has_sound
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
# Out of the language piece: the program binds neither of these two.
language_name = PROGRAM.language.language_name
reads_right_to_left = PROGRAM.language.reads_right_to_left
languages = PROGRAM.languages
list_presets = PROGRAM.list_presets
load_api_key = PROGRAM.load_api_key
log_aside = PROGRAM.log_aside
mark_time = PROGRAM.mark_time
log_path = PROGRAM.log_path
longest_stretch = PROGRAM.longest_stretch
loudness_field_build = PROGRAM.loudness_field_build
loudness_last = PROGRAM.loudness_last
main = PROGRAM.main
media_seconds = PROGRAM.media_seconds
metrics_sentence = PROGRAM.metrics_sentence
multitrack_state_note = PROGRAM.multitrack_state_note
names_used_twice = PROGRAM.names_used_twice
newer_release = PROGRAM.newer_release
no_place_message = PROGRAM.no_place_message
not_installed_note = PROGRAM.not_installed_note
number_text = PROGRAM.number_text
older_releases = PROGRAM.older_releases
open_in_file_manager = PROGRAM.open_in_file_manager
open_key_store_app = PROGRAM.open_key_store_app
open_page = PROGRAM.open_page
os = PROGRAM.os
parse_time_point = PROGRAM.parse_time_point
parse_timecode = PROGRAM.parse_timecode
path_key = PROGRAM.path_key
pick_choice = PROGRAM.pick_choice
platform = PROGRAM.platform
preset_fits_mode = PROGRAM.preset_fits_mode
preview_handover = PROGRAM.preview_handover
preview_out_of_date = PROGRAM.preview_out_of_date
probe_has = PROGRAM.probe_has
probe_warm = PROGRAM.probe_warm
project_files = PROGRAM.project_files
project_opened_note = PROGRAM.project_opened_note
question_note_build = PROGRAM.question_note_build
release_text_in = PROGRAM.release_text_in
resolve_installed = PROGRAM.resolve_installed
rules_from_cut_box = PROGRAM.rules_from_cut_box
run_stages = PROGRAM.run_stages
safe_filename = PROGRAM.safe_filename
sample_count = PROGRAM.sample_count
separation_sources = PROGRAM.separation_sources
set_update_skipped = PROGRAM.set_update_skipped
settings = PROGRAM.settings
sheet_speaker_names = PROGRAM.sheet_speaker_names
sign_of_life = PROGRAM.sign_of_life
size_in_mb = PROGRAM.size_in_mb
soxr_available = PROGRAM.soxr_available
soxr_note = PROGRAM.soxr_note
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
split_line_write = PROGRAM.split_line_write
start_again = PROGRAM.start_again
store_api_key = PROGRAM.store_api_key
strip_marks = PROGRAM.strip_marks
styles_follow_scheme = PROGRAM.styles_follow_scheme
subprocess = PROGRAM.subprocess
sys = PROGRAM.sys
system_locale = PROGRAM.system_locale
tc_column_write = PROGRAM.tc_column_write
threading = PROGRAM.threading
time = PROGRAM.time
timecode_seconds = PROGRAM.timecode_seconds
timecode_string = PROGRAM.timecode_string
timeline_entries = PROGRAM.timeline_entries
track_recordings_of = PROGRAM.track_recordings_of
tracks_awaiting_measure = PROGRAM.tracks_awaiting_measure
trouble_log = PROGRAM.trouble_log
update_fetched = PROGRAM.update_fetched
update_promise = PROGRAM.update_promise
video_facts = PROGRAM.video_facts
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
words_forgotten = PROGRAM.words_forgotten
words_from_handover = PROGRAM.words_from_handover
words_settings_grey = PROGRAM.words_settings_grey


def app_icon(QtGui):
    """The window's picture, or None where there is none to build.

    The piece that lays the entry in the program list owns the file;
    nothing here builds a path into another piece's folder. None
    rather than an empty icon: an empty icon looks to the caller
    exactly like a picture.
    """
    try:
        video = QtGui.QPixmap()
        video.loadFromData(beside("desktop", program=PROGRAM).icon_bytes())
        return None if video.isNull() else QtGui.QIcon(video)
    except Exception:
        return None


#-------------------------------------------------------------- Interface

# What the language field offers -- only languages with both codes,
# since an unknown recognition code would promise a transcript that
# cannot come. SPEECH_CODES, in the program, holds the second code.
SPOKEN_LANGUAGES = (
    ("ger", "German"), ("eng", "English"), ("fra", "French"),
    ("spa", "Spanish"), ("ita", "Italian"), ("nld", "Dutch"),
    ("por", "Portuguese"), ("pol", "Polish"), ("rus", "Russian"),
    ("swe", "Swedish"), ("dan", "Danish"), ("nor", "Norwegian"),
    ("fin", "Finnish"), ("ces", "Czech"), ("tur", "Turkish"),
    ("ell", "Greek"), ("hun", "Hungarian"), ("ron", "Romanian"),
    ("ukr", "Ukrainian"), ("cat", "Catalan"), ("ara", "Arabic"),
    ("heb", "Hebrew"), ("jpn", "Japanese"), ("zho", "Chinese"),
    ("kor", "Korean"),
)


def spoken_language_choices():
    """Return [(tag, name)] for the language field, by name."""
    return sorted(((tag, T(name)) for tag, name in SPOKEN_LANGUAGES),
                  key=lambda x: x[1].lower())


def language_of_system():
    """Return the track tag the system language suggests, or "".

    Only a suggestion for the empty field: the operating system does not
    know what language was spoken in a recording.
    """
    # The locale is read directly, not through known_language: that
    # one answers which language the *interface* speaks and falls back
    # to English. A Spanish system would then suggest English, and the
    # recording would be tagged wrongly.
    head = (system_locale() or "").replace("_", "-").split("-")[0]
    head = head.strip().lower()
    if len(head) != 2:
        return ""
    for tag, _name in SPOKEN_LANGUAGES:
        if SPEECH_CODES.get(tag) == head:
            return tag
    return ""


def audio_use_settled(video, chosen, forced, has_sound=True,
                      kind=TYPE_CONTENT):
    """What the audio field of one video file shows, and why.

    Returns (used, why). An empty *why* means there is a choice to
    make; otherwise the reason stands beside the greyed out field,
    because greyed out without a reason is a dead end.
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

    A drop-down and not a tick: closed it says its own state. A *why*
    settles the field; *alive* keeps it open for a reason that
    explains without deciding. Grey over the whole field would make
    every answer look barred, so choices_shut greys entry by entry.
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

    *shut* is the barred values, or {value: why} where two are barred
    differently; *noted* sets a sentence on an entry that stays open.
    Entries stay in the list, and every entry is set either way round:
    one that only shuts leaves a camera grey for the whole session.
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

    A guess counts only if it begins with a letter: the name becomes the
    track's label at auphonic.com, where "0008A" off a card number looks
    like a fault rather than a person. A typed name stands as typed.
    isalpha, not a-z: English has not every letter a name begins with.
    """
    return guess if str(guess or "")[:1].isalpha() else ""


class SpeakerName(Value):
    """A name field, answering the name the run works under.

    The field starts empty with the guess in grey, and a placeholder is
    not a value -- so get() gives the typed name and falls back to the
    guess, and the two places wanting the answer alone say typed(). The
    guess is filtered here, for the reason guess_worth_using gives.
    """

    def __init__(self, value="", suggested=""):
        Value.__init__(self, value)
        self.suggested = guess_worth_using(suggested)

    def get(self):
        return str(self._value or "").strip() or str(self.suggested or "")


def camera_tracks_of(camera_lines):
    """Every camera with the name it carries in the cut, in order.

    Guessing drops the take number, which is what tells the cameras of
    one rig apart, so where two guesses fall together the whole stem
    stands for both. Two files of one name stay one name: nothing in
    them tells the cameras apart.
    """
    files = [p for p, _v, _k, _n in camera_lines or ()]
    guessed = [guess_camera_name(p) for p in files]
    return [(p, os.path.splitext(os.path.basename(p))[0]
             if guessed.count(n) > 1 else n)
            for p, n in zip(files, guessed)]


def camera_tracks_clashing(camera_lines):
    """Names that more than one camera would carry in the cut.

    The cut keys a camera by that name: its colour, its legend line
    and which file plays. Two under one name are one camera, and only
    the last of them is ever seen.
    """
    names = [t for _p, t in camera_tracks_of(camera_lines)]
    return sorted(set(n for n in names if n and names.count(n) > 1))


def missing_conditions(files, production, multitrack, assign_lines,
                       camera_lines, voice_lines=(), voiced=()):
    """Report what is still missing, and where it is missing.

    Returns {key: reason}; empty means everything is there. Reasons go
    under the start button and are in plain words -- greyed out without
    one is a dead end. The key says which sheet: 1 and 11 the file tab,
    21 the production strip on it, 22 the assignment tab. 1 is empty.
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
    # A voice whose name is on somebody else: to the cut two voices of
    # one name are one person, and no answer makes that right.
    clash = voice_names_clashing(assign_lines, voice_lines, voiced)
    if clash:
        pending[22] = (T('%s is on more than one speaker -- a name is a '
                         'person, and every person needs their own.')
                       % ", ".join(clash))
    # No sound at all: a video file whose Camera audio is not in use
    # contributes none, and a run with nothing to hear has no first step.
    if files and not assign_lines:
        pending[11] = T('No sound to work with -- set a video file\'s '
                        'Camera audio to "use the audio", or add an '
                        'audio recording.')
    # Before the file names below, so the one with a field to type wins.
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
    that is what it is downstream. The last three arguments are the
    window's: the row maker, the map from a file to the row a finding
    belongs on, and the channel rows. Nothing in it needs gui().
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
                    % (os.path.basename(row[0]), number_text(len(row) - 1, 0)),
                    os.path.dirname(row[0]), "audio", files_for_it=row)
    # A finding about block 3 belongs to the recording, not to nowhere.
    for part in row:
        lines_node[part] = node
    channel_rows_show(node, row[0])
    try:
        lines = audio_summary(row[0])
    except Exception as e:
        lines = [(T('Error'), str(e)[:120])]
    for k, value in lines:
        # Length and timecode are the whole recording's, not block 1's.
        if k == T('Length'):
            value = (T('%s  (%s)  --  %s  --  %s blocks')
                 % (as_hms(total), as_data_size(sum(size_in_mb(x) for x in row)),
                    T('Timecode from %s')
                    % timecode_string(min(t for t in tcs if t is not None))
                    if any(t is not None for t in tcs)
                    else T('no timecode'), number_text(len(row), 0)))
        item(node, "      " + k, value)
    for i, (p, n, t) in enumerate(zip(row, lengths, tcs), 1):
        source_text = (T('selected') if os.path.abspath(p) in selected
                 else T('found automatically'))
        # The row stands for this block alone: Remove takes out only it.
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
    barred too: this is a fact about the material, not a suggestion.
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

    An episode has one intro and one outro, each a single switch to the
    run. So while one file holds a mark that entry is shut everywhere
    else, rather than a second choice taking the mark off the first.
    *kinds* is {path: Value}; a path missing from it counts as content.
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

    A reason goes on the entry it is about, never beside the field. With
    *derived* the value shown is what the program worked out, and *why*
    bars the entry it is about; *no_wide* bars the wide shot, *no_edge*
    the marks somebody gave. Without *derived* a *why* greys nothing.
    """
    cell, box = choice_cell(CLIP_TYPES, kind, "", quiet, alive=True)
    barred, noted = {}, {}
    if derived:
        barred[TYPE_CONTENT] = why
    elif why:
        noted[TYPE_WIDE] = why
    if no_wide:
        barred[TYPE_WIDE] = no_wide
        # Nor content: as content a placeless file becomes the wide shot
        # by derivation. Intro, outro and "leave out" stay open.
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

    Two places show it: the file list, where it is said which files play
    a part, and the camera table beside the player, where it can be heard
    whether that sound is usable. Where the field is settled it is shut,
    and *why* says so from the field rather than from beside it.
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
    drift apart, and then one tab offers what the other refuses. Only
    cameras are asked, and a wide shot is a camera. *kinds* and *uses*
    are {path: Value}; a path missing counts as content and unused.
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

    The same value stands in the file list and beside the player, where
    it can be *heard* whether that sound is usable -- and heard is the
    only way to tell. A settled field is inert, so the derivation cannot
    be turned into a stored answer by the act of showing it.
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

    Three tables show a Kind and all three ask here: two derivations of
    one answer drift apart, and then one table offers what another
    refuses. *kinds* says what every video file is, which tells whether
    intro and outro are free.
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

    The same pattern as audio_use_bind: that a clip is in truth an outro
    is noticed while watching it, and the player stands on the assignment
    tab. *after* is what has to happen once the answer changed -- the
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

        activated fires for a person and never for the program. The
        note is kept on the value, which outlives every widget: a note
        on a widget would go with the next redraw, and a proposal
        would then write over the answer.
        """
        value.chosen_by_hand = True
        chosen(i)

    box.currentIndexChanged.connect(chosen)
    # activated fires for "somebody picked this", changed or not: the
    # only signal that fires on a derived wide shot, already current.
    box.activated.connect(by_hand)
    value.listen(lambda: pick_choice(box, value.get()))
    return box


def kind_proposal_apply(values, unplaceable, brief=()):
    """Propose a Kind for every file with no place.

    Fills only what still carries the program's own answer, never a Kind
    somebody picked -- read off chosen_by_hand, not off the text, since
    setting a file back to content by hand is an answer too. Unplaceable
    None means no measurement ran. *brief*: the shortest becomes intro.
    """
    if unplaceable is None:
        return []
    lost = set(os.path.abspath(p) for p in unplaceable)
    short = [os.path.abspath(p) for p in (brief or ())]
    elsewhere = any(v.get() == TYPE_INTRO
                    and getattr(v, "kind_said", None) != TYPE_INTRO
                    for v in values.values())
    # A jingle has no place because it is not a camera, and is meant to
    # be used rather than left out. One intro only, and none if taken.
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
    however that answer got there. It lands on intro while that is
    free, and is left out where it is taken; outro stays a click away.
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

    Outside gui() because it decides nothing and touches no widget.
    """
    moved = kind_proposal_apply(values, (data or {}).get("unplaceable"),
                                (data or {}).get("brief"))
    # The proposal first, the fact after: what the proposal leaves on
    # content or the wide shot is exactly what cannot be true.
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
# Too small a number leaves the last tab's key dead until the menu opens.
TABS_AT_MOST = 4


def window_ready(state):
    """Whether the time window can be set: the files share an axis.

    Before that a boundary would not know what it refers to.
    """
    return bool(state["tc_there"] or state["axis"])


def menus_follow(late):
    """Grey each file entry with the button that does the same thing.

    The button is the one source: it is greyed in places that ask
    nothing here, and an entry with a state of its own drifts apart
    from it. Save and Close have no button and follow the project.
    """
    for entry, button in late.get("menu_follows") or ():
        entry.setEnabled(button.isEnabled())
    here = late.get("project_here")
    for entry in late.get("menu_project") or ():
        entry.setEnabled(bool(here and here()))


#------------------------------------------------------------- The menus
# A piece of its own, in the folder "menus" beside the way in: beside()
# lays its path against the folder the program starts in, not this file.

menus = beside("menus", program=PROGRAM)

# What the window calls out of it, bound by name: a name read here and
# bound nowhere is a loose end. Three are read by no code on this side.
build_menus = menus.build_menus
player_loaded = menus.player_loaded
player_of_tab = menus.player_of_tab
transport = menus.transport


#--------------------------------------------------------- The title bar
# What stands in the title bar of the window, and nothing else.


def window_title(project=""):
    """What stands in the title bar, with the open project named in it.

    The name goes in front, which is what a document window does
    everywhere else: Word writes "Report.docx - Word". It takes the place
    of the tag line, and without it a window with a project open and one
    without look exactly alike.
    """
    said = T('Video Podcast Magic %s -- raw material becomes an edited '
             'podcast') % VERSION
    if not project:
        return said
    return "%s -- %s" % (os.path.basename(project), said.split(" -- ")[0])


#------------------------------------------------------------ The tables
# A piece of its own, in the folder "tables". Read where its block stood.

tables = beside("tables", program=PROGRAM)

# What the window binds out of it by name. widget_width and file_span
# are read by no code here and stand all the same: the fittings ask
# the program for the one, a test for the other.
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
# A piece of its own, in the folder "player". Read where its block stood.

player = beside("player", program=PROGRAM)

# What the window binds out of it by name. Not every one is read here:
# take_from() carries them all to the program, and that is where the
# menus and the tests ask for them.
NAME_HOLD_S = player.NAME_HOLD_S
box_room = player.box_room
caption_room = player.caption_room
cut_caption_room = player.cut_caption_room
cut_choice_room = player.cut_choice_room
digits_font = player.digits_font
make_band_and_player = player.make_band_and_player
make_drop_area = player.make_drop_area
make_log_view = player.make_log_view
make_player_choice = player.make_player_choice
make_player_widgets = player.make_player_widgets
player_menu = player.player_menu
qt_cut_band = player.qt_cut_band
qt_cut_player = player.qt_cut_player


#------------------------------------------------------------ The orders
# A piece of its own, in the folder "orders". Read where its block stood.

orders = beside("orders", program=PROGRAM)

# What the window calls out of it, bound by name. voices_of_values is
# read by no code here: take_from() carries it to the program.
run_argv = orders.run_argv
slider_argv = orders.slider_argv
slider_numbers = orders.slider_numbers
speakers_to_cameras = orders.speakers_to_cameras
voices_of_values = orders.voices_of_values


#---------------------------------------- The settings sheet and the log
# The Settings window: the language box, the boxes for the key and for
# Resolve, and the row the macOS keychain needs. The log way at the end.


# What gui() answers with when the window is to be built again in
# another language. Neither 0 nor 1: those are a run finished and failed.
LANGUAGE_AGAIN = 7

# The window's own question before it is torn down: save the work, or
# not, or think better of it. The three ways out all ask the same one.
RESTART_ASK = [None]


def language_box_build(parent, state):
    """The box that says which language the window speaks.

    A box of its own: it is the one setting about the program itself,
    while the two beside it are each about a service outside it. The
    offer to fetch that language now stands in it too.
    """
    from PySide6 import QtWidgets as _qw
    box = _qw.QGroupBox(T('Language of the window'))
    rows = _qw.QVBoxLayout(box)
    # Above the field, not below: somebody who reads it after choosing
    # has already chosen, and waits for a window that will not change.
    note = label(T('A language chosen here is spoken from the next '
                   'start.'), COLOURS["quiet"])
    # Wrapped, because the German sentence is the longer one and the
    # note beside this box is measured 89 px too wide for want of it.
    note.setWordWrap(True)
    rows.addWidget(note)
    chooser = _qw.QComboBox()
    speaks_as(chooser, T('Language of the window'))
    # The first entry names the language it will really bring: an
    # Italian system reads English, not a promise nobody can keep.
    chooser.addItem(T('System language (%s)')
                    % language_name(known_language(system_locale())), "")
    for code, name in sorted(((c, language_name(c)) for c in languages()),
                             key=lambda pair: pair[1].lower()):
        chooser.addItem(name, code)
    # An empty setting is the first entry's value: an unchosen one lands there.
    stands_at = chooser.findData(kept_language())
    chooser.setCurrentIndex(stands_at if stands_at >= 0 else 0)
    fetch = _qw.QPushButton(T('Restart the application'))
    fetch.setVisible(False)
    hint(fetch, T('The work can be written to a project file first.'))

    def would_speak():
        """The language this box would bring, as a code.

        The system may name one this program has no texts for -- then
        it is English that arrives, and English that is compared.
        """
        return known_language(chooser.currentData() or system_locale())

    def offer_show():
        """Offer the new language only where there is a new one."""
        other = would_speak() != PROGRAM.LANG
        fetch.setVisible(other)
        note.setText(
            T('Starting the application again brings it at once, and '
              'asks first what is to happen to the work. Leaving it '
              'alone costs nothing -- it comes at the next start.')
            if other else
            T('A language chosen here is spoken from the next start.'))

    def restart_now():
        """Take this window down and ask for one in the new language."""
        # Not while a run is going: the run writes into this window,
        # and a new one would take its log and its buttons with it.
        if state.get("running"):
            note.setText(T('The run is still going. The window can be '
                           'started again once it is finished.'))
            return
        # One question for every way out of a window, answered by the
        # window itself. No is no: the sheet stays as it stands.
        ask = RESTART_ASK[0]
        if ask is not None and not ask():
            return
        box.window().close()
        # Closed and not deleted: the run loop, the colour watch and the
        # update sink outlive it and would reach a deleted window.
        parent.close()
        _qt_widgets().QApplication.instance().exit(LANGUAGE_AGAIN)

    def chosen(*_):
        """Write the choice down, and offer what it can bring now."""
        keep_setting("language", chooser.currentData() or "")
        offer_show()

    # Connected after the index is set: before it, opening the window
    # would write down a choice nobody made.
    chooser.currentIndexChanged.connect(chosen)
    field_row = _qw.QHBoxLayout()
    rows.addLayout(field_row)
    field_row.addWidget(chooser)
    fetch.clicked.connect(restart_now)
    field_row.addWidget(fetch)
    field_row.addStretch(1)
    offer_show()
    return box


def settings_dialog_build(parent, access_box, resolve_box, keep_where,
                          state):
    """Assemble the Settings window out of the boxes that go in it.

    Two of the boxes are built where they are used on the page and move
    in here on the first click -- which is why this takes them in
    rather than making them.
    """
    from PySide6 import QtWidgets as _qw
    d = _qw.QDialog(parent)
    d.setWindowTitle(T('Settings'))
    d.setMinimumWidth(620)
    rows = _qw.QVBoxLayout(d)
    # First, so the two that follow keep their note under them: it says
    # "Both", and a box between them would take that word away.
    rows.addWidget(language_box_build(parent, state))
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

    Built twice, because the key is looked at from two places: the field
    and its button in the settings window, the preset they unlock on the
    sheet -- and that window stands over the sheet. Returns the settings
    label, the row for the sheet, and the calls that show and hide it.
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
    # A button and not a link inside the line: a link in a label is
    # announced as plain text and fires on no key at all, while a
    # button carries its own name and answers the space bar.
    settings_way = QtWidgets.QPushButton(T('Settings ...'))
    settings_way.setFlat(True)
    settings_way.setVisible(False)
    settings_way.setObjectName("key_note_way")
    settings_way.clicked.connect(lambda: settings_open())
    key_row.addWidget(hint(settings_way,
                           T('Open the settings, where the key is.')))

    def show(text):
        """Say what is wrong with the key, in both places it is read.

        Never in a box: a box has to be clicked away before the field
        it is about can be reached.
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

    A timer asks again while the window stands, so the box wakes up by
    itself -- that waking is the only sign the unlock took. Returns the
    call that reads the state once.
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
    # Half a second: often enough that unlocking feels answered, and
    # cheap -- it starts no process and puts nothing on the screen.
    watch.start(500)
    return look


def log_open():
    """Hand the log of this run to whatever opens a text file here.

    Nothing is waited for -- the window carries on while the editor
    comes up, which on a cold start takes seconds.
    """
    where = log_path()
    if not where or not os.path.isfile(where):
        return False
    return open_page(where)


def log_entry(act, where, window):
    """Put the way to the log into the menu, alive while there is one.

    Greyed and not hidden where there is nothing to open: a missing
    entry teaches nobody that there is a log at all, and the reason
    stands on the entry.
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
# A piece of its own, in the folder "fittings". Read where its block stood.

fittings = beside("fittings", program=PROGRAM)

# What the window still calls out of it, bound by name. cells_laid_out
# is read by no code here: the speakers piece asks the program.
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


#--------------------------------------------------------- The file list
# A piece of its own, in "filelist". Its block stood in two places.

filelist = beside("filelist", program=PROGRAM)

# What the window calls out of it, bound by name. The two go the other
# way as well: that piece asks the program for chain_fill_in.
make_file_changes = filelist.make_file_changes
make_file_list = filelist.make_file_list


#----------------------------------------------------------- The prework
# A piece of its own, in "prework". Its block stood in two places.

prework = beside("prework", program=PROGRAM)

# What the window calls out of it, bound by name. prework_fetch is read
# by no code here, so that the program keeps every name it carried.
make_prework_bar = prework.make_prework_bar
make_prework_tasks = prework.make_prework_tasks
prework_api_key = prework.prework_api_key
prework_fetch = prework.prework_fetch
prework_share_key = prework.prework_share_key


#--------------------------------------------------------------- The run
# A piece of its own, in "running". Read where its blocks stood.

running = beside("running", program=PROGRAM)

# What the window calls out of it, bound by name.
make_run_start = running.make_run_start
run_done_text = running.run_done_text


#-------------------------------------------- What the window works with
# Everything gui() calls that is not a fitting and not a piece of its
# own: the assignment rows, the break-off buttons, and the run loop.


def prepared_tracks_in(folder):
    """The finished tracks lying in that folder: name -> file.

    At -16 LUFS with their timecode as a BWF marker, so the better
    preview source: a raw recording sits 16 to 36 dB below. Only
    "final_<name>_<tc>.wav" counts; Auphonic's raw return is
    "<name>.wav", neither trimmed nor on the axis.
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


def camera_offset(cameras, origin=None, fps=30.0):
    """Return how far each camera is shifted against programme time.

    A handover file carries an ``offset`` per camera, negative where the
    camera started before In point: position in the file is programme
    time minus offset, and deciding it again here is how the player and
    Resolve came apart. Failing that ``start_s`` against *origin*.
    """
    out = {}
    # A stored offset that disagrees with the camera's own timecode is
    # heard as sound against the wrong picture, away from the reference.
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

    The reason stands in the column that takes what the others leave,
    so its line count is known only once the window has a width.
    Without this the wrapped line is drawn outside its row.
    """
    room = items.columnWidth(2)

    def fit(kid):
        beside = items.itemWidget(kid, 2)
        said = beside.findChild(QtWidgets.QLabel) if beside else None
        if said is None:
            return
        box = beside.findChild(QtWidgets.QCheckBox)
        # The width it has; the column's only before the first layout.
        # From the column both times, the rows creep taller each round.
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
    _joins_seamlessly. By hand the difference goes into the joined file
    as silence, and no later step takes it out. Only where both sides
    carry a timecode -- without one there is nothing to check.
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
    rather than left out: "why can I not pick this" is answered on the
    entry it is about.
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

    Out of gui() because it holds no state: what it needs comes in as
    arguments, in the order the window has them.
    """
    api_key = os.path.abspath(path)
    channel_node[api_key] = (node, path)
    row = blocks_of.get(api_key) or [api_key]
    # Where the list stands, kept over the rebuild: ticking a channel
    # replaces every row below the file, and the list would jump to top.
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
        channel_row(T('      %s channels') % number_text(how_many, 0),
                    T('measurement running ...'))
        return
    # Over the whole recording: the first block can be the soundcheck,
    # and then it says nothing about what the channels carry.
    facts = blocks_facts(row)
    silent = list(facts.get("silent") or [])
    picked = channel_choice.get(api_key) or {}
    # What the file is decides before the measurement does, and only for
    # a two channel intro or outro -- see kind_makes_stereo.
    of_kind = clip_kind_values.get(api_key)
    kind = (of_kind.get() if of_kind is not None
            else remembered.get("kind:" + api_key))
    joined = joined_channels(facts, picked, kind)
    judged = {k: (stereo, sure, why)
              for k, stereo, sure, why in channel_joins(facts, kind)}
    # One row per channel; the tick says "this one and the next make one
    # stereo track". On a mixer, channels 2 and 3 can be the pair.
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
        # The tick and its reason side by side in the wide column: in the
        # narrow one the word beside the box is cut off after one letter.
        beside = QtWidgets.QWidget()
        in_a_row = QtWidgets.QHBoxLayout(beside)
        in_a_row.setContentsMargins(0, 0, 0, 0)
        in_a_row.setSpacing(8)
        # An offer, not a statement: a channel already spoken for says
        # "with Channel N one stereo track" instead.
        box = QtWidgets.QCheckBox(
            T('join with Channel %d') % (k + 2))
        box.setChecked(bool(joined.get(k)))
        said = label(why if sure else T('uncertain -- %s') % why,
                     COLOURS["quiet"])
        # German writes the finding half as long again as English, so it
        # wraps: what would run past the edge is the finding itself.
        said.setWordWrap(True)
        in_a_row.addWidget(box)
        in_a_row.addWidget(said, 1)
        hint(box, T('On makes one stereo track out of this channel '
                    'and the next.\nThe next one then has no tick of '
                    'its own -- it is spoken for.\nWhat was measured '
                    'is in the line beside it.'))

        def chosen(on, file_path=api_key, number=k,
                   measured=measured_stereo):
            # Only a real override is remembered: ticking a pair the
            # measurement already found puts the row back to measured.
            by_hand = channel_choice.setdefault(file_path, {})
            if bool(on) == bool(measured):
                by_hand.pop(number, None)
            else:
                by_hand[number] = bool(on)
            # The cut tracks follow the old answer, so every block goes:
            # block one's channel 1 beside block two's 1+2 otherwise.
            for block in blocks_of.get(file_path) or [file_path]:
                split_files.pop(block, None)
            QtCore.QTimer.singleShot(
                0, lambda: channels_arrived(file_path))

        box.toggled.connect(chosen)
        items.setItemWidget(kid, 2, beside)
    # A moment later: the column still answers with its old width while
    # it is saying that the width has changed.
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

    Which camera is the wide shot is derived from who is assigned where,
    an answer given on another tab long after this list was built. Every
    row left behind how to draw itself in *rows*.
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

    One answer fires more than one listener, and each asks for the same
    table again. Asked three times, the second and third land while the
    first is still exchanging cells -- and with a player starting at that
    moment Qt stands in QWidget::createWinId. Two runs in four hang.
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

    Two pictures at once are two moments at once, so one player stops the
    other. Told to stop while still starting up, the media player stands
    in a lock another thread holds -- one run in eight. *mark* is the
    player's own note of whether it runs: asking Qt is what blocks.
    """
    def quiet():
        hold = getattr(who, "pause", None)
        if hold and getattr(who, mark, False):
            hold()

    return quiet


def not_on_the_axis(path, kinds, remembered):
    """Why the file in the player carries no window boundary, or "".

    A boundary is a point on the axis of the episode, and an intro is not
    on that axis: it is set in front, not cut in. Content and the wide
    shot stay usable. The reason comes back with it, because greying the
    buttons without one reads as a fault.
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

    The line beside the progress bar carries a file name, so its width is
    decided by the material and not the wording: with a file name of 29
    characters the German stands 20 px past its field. Shortened in the
    middle, because both ends carry meaning; the whole line is a tooltip.
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

    Called between steps, never in the middle of writing one file: a
    half file looks finished from the outside, and the next run finds
    it and believes it.
    """
    if RUN_STOP["wanted"]:
        # What the window said is the better answer: it knows which step
        # was on the screen, this only where the run got to.
        raise Stopped(RUN_STOP["at"] or what)


class Redirect(object):
    """Send the run output to the window and to the log file.

    The window is gone once it is closed; the file stays, and only that
    way can a run be read back afterwards. *show* is where the window
    wants it, *having* the open log file.
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

    What was written before the break is whole -- a run breaks off
    between steps only -- but the steps after it did not happen. So the
    folder holds a part of a run and looks like a result from outside,
    and whoever reads this has to tell the two apart tomorrow.
    """
    done = [os.path.basename(x) for x in (results or [])]
    return "\n".join([
        T('\nStopped during: %s') % (where or "?"),
        TN(len(done),
           '%s file was finished before that and is whole: %s',
           '%s files were finished before that and are whole: %s')
        % (number_text(len(done), 0), ", ".join(done) or "-"),
        T('Everything after that step is missing. The folder holds a '
          'part of a run, not a result.')])


def break_off_button(QtWidgets, state, say):
    """The button that stops a run, and what it says while it does.

    Away while nothing runs: a button that does nothing is a question
    nobody asked. It can be pressed at any moment, but the run stops only
    where nothing is left half written, so between the press and the end
    there is a wait -- said out loud, or the button looks broken.
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

    A disabled button takes no mouse events in Qt and so shows no
    tooltip; the frame takes them and carries a copy of its text. And a
    button wants a fixed height where a plain widget wants a preferred
    one, so on an odd difference a bare button rounds apart.
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

    A flat button asks for less room than a framed one: Start stands 29
    pixels high where "Settings ..." stands 25, so it lines up with
    neither edge. No fixed number -- that is the system font talking, and
    the wish stands whether the button is on screen or not.
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

    Both are free fields and nothing stops them contradicting: set that
    way, every wide shot is merged away again and no line says why. The
    numbers go through the number helper and not "%g", which turns
    exponential from a million on and leaves "1,5e+06 s" in German.
    """
    holds = float(number.get("wide-length") or 0.0)
    least = float(number.get("min-edit-duration") or 0.0)
    if holds <= 0 or least <= 0 or holds >= least:
        return ""
    return T('The wide shot holds %s s, less than the shortest shot of '
             '%s s -- so it is merged away again and never appears.\n') % (
                 number_text(holds, 1), number_text(least, 1))


def question_dialog(f, window, QtWidgets, label):
    """Ask the window's user what to do while a worker thread waits.

    Outside gui() because it reaches into nothing. What it answers goes
    back on the question itself, which the waiting thread is holding.
    """
    dialog = QtWidgets.QDialog(window)
    dialog.setWindowTitle(f.title)
    dialog.setModal(True)
    position = QtWidgets.QVBoxLayout(dialog)
    position.addWidget(label(T('%s -- what should happen with it?\nThe '
                               'details are in the log.') % f.title))
    buttons = []
    for api_key, text in f.possible:
        # Multi-line and indented in the log; one line in the dialog.
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

    Outside gui() because it reaches into nothing. Returns the total
    speech time as a sentence, empty where no speaker is known.
    """
    lines, total, silence, length = (speaker_statistics(d) if d
                                      else ([], 0.0, 0.0, 0.0))
    table.setRowCount(len(lines) + (1 if length > 0 else 0))
    # The block count reaches four digits after nine minutes: a block
    # lasts at least 0.2 s and takes 0.35 s of silence to end it, so it
    # goes through the number helper like the columns beside it.
    for i, e in enumerate(lines):
        for column, text in ((0, e["name"]),
                             (1, as_minutes(e["seconds"])),
                             (2, "%s %%" % number_text(e["share"], 1)),
                             (3, number_text(e["blocks"], 0)),
                             (4, "%s s" % number_text(e["mean"], 1))):
            p = QtWidgets.QTableWidgetItem(text)
            if column:
                p.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(i, column, p)
    if length > 0:
        i = len(lines)
        quiet_share = number_text(100.0 * silence / length, 1)
        for column, text in ((0, T('Silence')), (1, as_minutes(silence)),
                             (2, "%s %%" % quiet_share),
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

    Outside gui() because it reaches into nothing. Returns the line and
    the colour it is written in.
    """
    recordings = recordings or audio_file_list
    parts = []
    if audio_file_list:
        parts.append("%s%s" % (
            TN(recordings, '%s audio recording', '%s audio recordings')
            % number_text(recordings, 0),
            "" if recordings == audio_file_list
            else T(' from %s files') % number_text(audio_file_list, 0)))
    if videos_n:
        parts.append(TN(videos_n, '%s video file', '%s video files')
                     % number_text(videos_n, 0))
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
        return (sentence + T(' -- %s notes') % number_text(len(hints), 0),
                COLOURS["warning"])
    return sentence + T(' -- nothing to fault.'), COLOURS["quiet"]


def project_state_read(file_path, elsewhere):
    """Read what is already there and clear leftovers elsewhere.

    Returns the contents of the file at the current location or, if
    there is none, of an earlier one, and beside it the places the
    caller is to clear so that only the one is left.
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

    Three things are caught before they do damage: two recordings under
    one speaker name, which become a single track, a voice carrying a
    name that is on somebody else, and two cameras with the same output
    name, where the second overwrites the first.
    """
    voiced = state.get("voiced") or set()
    audio_reason, video_reason = (state.get("audio_reason"),
                                  state.get("video_reason"))
    # Every name on the sheet at once, both levels. A recording showing
    # its voices is left out: its field says "several speakers".
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

    Every absolute path that really exists is kept as a result on the
    way through, so the button that opens the result folder has a target.
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

    The road a run takes: the job works in a thread of its own, its
    lines go into the Output tab, and the flag the window watches keeps
    a run from starting on top of it.
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

    Outside gui() because it reaches into nothing.
    """
    # The three sinks belong to the program: the run happens over there.
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

    For the preview the audio assigned to the camera plays instead of the
    camera audio: preferably the processed track, at delivery level, else
    the raw recording. With several speakers the first applies. With no
    speaker -- the wide shot -- the overall mix plays if it exists.
    """
    # An intro or outro stands before or after the episode, so nothing
    # off the episode's own axis belongs under it.
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


def make_voice_rows(Qt, QtCore, assign_lines, camera_lines, voice_lines,
                    files, remembered, state, tree_open, multitrack, player,
                    assignment_check, player_load, speaker_split_kick_off,
                    voices_of):
    """The rows of the assignment tree, and the voices under them.

    Outside gui() because none of it builds a widget; the window's own
    objects go on being written through. `player` is a parameter on
    purpose -- the module-level name player holds the piece read by
    beside(), and a free read here picks up the module, not the widget.
    """
    def assignment_state_show():
        """What the material allows: the cut box, and the tick's line.

        The camera cut needs speakers told apart, and whether they came
        of separate tracks or of one recording taken apart is no part of
        it. The widgets are looked up and not closed over: this runs
        while the window is still being built.
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

        Without hearing it a name is a guess. The player on the right has
        the rail, the pause, the jumps and the boundaries. It jumps into
        the middle of the longest stretch: the first moment of a passage
        is often the tail of somebody else's word.
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
        has no file of its own, so the player opens the recording it was
        heard in and jumps to where that voice speaks longest -- which is
        the whole of what a Listen button would offer, so there is none.
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

        The assignment has exactly one level: where the voices are on the
        screen the recording above shows nothing beside its name, because
        two answers one above the other can contradict each other.
        Folded, the row says their cameras -- not how many.
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
        to a fresh separation rather than an entry in a list.
        """
        found = len(speakers_stored(state, source).get("segments") or ())
        state["speakers_source_chosen"] = source
        state["speakers_count"] = found + 1
        speaker_split_kick_off(fresh=True)

    def voices_build(tree, under, path, videos, targets, wide=None):
        """The voices heard in one recording, hung under its row.

        Everything counts per camera and not per speaker: two voices set
        to the same camera are one condition, which is why the camera
        sits on the voice and not on the file. *wide* is what
        wide_bar_of worked out. Returns how many voices there were.
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
            # The first column says which of the two levels this row is,
            # the way the file list writes "4 channels" under a file.
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
                from the cameras nobody is assigned to.
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
            # what was measured and named must survive a mis-click.
            return
        # Each recording's names go back to that recording.
        named = voice_names_by_source(voice_lines,
                                      state.get("speakers_source") or "")
        voice_names_store(state, named)
        for k, nv, cv in voice_lines:
            # Only a real override: a camera the program worked out goes
            # back as nothing, so renaming a voice moves its camera too.
            remembered["voice:" + k] = camera_to_remember(
                cv.get(), getattr(cv, "derived", None))
            # The name as well: state alone does not reach the project
            # file, and the name is what auphonic.com puts on the track.
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


def make_preview(Qt, QtWidgets, state, bridge, bridge_emit, assign_lines,
                 camera_lines, voice_lines, cut_var, cut_parts, edge_on,
                 start_var, end_var, multitrack, out_folder, clip_kind_value,
                 wide_cameras_now, commonest_folder, band_show, speech_show,
                 window_info_show, question_note, cut_column, forecast_box,
                 preview_label, speech_title, speech_table):
    """The preview: who speaks when, and what the cut would look like.

    Outside gui() because it is one question answered end to end: the
    handover built from the assignment, the measurement that fills what
    it leaves open, and the numbers under the picture. Qt comes in as a
    parameter -- PySide6 is imported inside gui().
    """

    def off_speakers():
        """Build a handover from who speaks when and the assignment.

        Turning the cut values then needs no Resolve run to see the
        effect. Where nothing is found, the reason is stated.
        """
        # The separations first: they separate people rather than levels,
        # and are there before anything has been uploaded.
        apart = separation_sources(speakers_for_run(state, voice_lines))
        rows = track_recordings_of(assign_lines)
        segment_list, length = speakers_all_on_window_axis(
            state, voice_lines, assign_lines, audio_start)
        state["stat_measured"] = not bool(segment_list)
        # And every track no separation speaks for: the run takes those
        # too, and a preview that leaves people out is a different cut.
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

        The same road as audio_start_of: two places answering it apart
        is how a clock that was never set gets believed here while the
        first tab says out loud that it cannot be right.
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
        d = None
        state["reason"] = ""
        # The handover of a run. Only where there is none does the
        # window work the speakers out for itself.
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
                # The window is applied below by apply_time_window, out
                # of start_s. Here as well would move it a second time.
            except RuntimeError:
                # A widget went while we asked it. The rebuild that
                # took it away brings its own answer, so this one goes.
                d = None
        if d is None:
            state["statistics"] = False
            speech_show(None)
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
        # The line stays and says what the cut stands on: somebody whose
        # track is unmeasured is in the cut and not in this picture.
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
        # The words come with the handover; the greying belongs here, or
        # it runs before the handover is read and answers from last round.
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


def speakers_step_said(source):
    """What the line under the overall bar says while one is separated.

    The name and not the path: the bar stands in the window, not in the
    folder, and the line has one line's room.
    """
    return T('Separating speakers: %s') % os.path.basename(source)


def make_speaker_split(QtCore, state, bridge, bridge_emit, plan, files,
                       assign_lines, voice_lines, remembered, split_run,
                       split_line, split_label, split_never, axis_store):
    """Separate the speakers, locally, and say where that stands.

    A third source for the same thing: who speaks when. auphonic.com says
    it from its statistics, speakers_from_tracks measures it where every
    person has a microphone, and this works it out from one recording.
    Three names built further down in gui() come through *state*.
    """
    # A thread of its own and an entry of its own on the bar, and no
    # place in the prework count: axis_work_loop waits in "while
    # prework_busy()", and three minutes there hold up the time axis.
    def speaker_split_source(alone=False):
        """Which file the separation listens to, and why that one."""
        audio_files = [p for p, a in files if a == "audio"]
        videos = [p for p, a in files if a == "video"]
        # The derived answer, not the stored one: a camera whose sound is
        # the only sound there is was never clicked.
        return speaker_source_pick(
            audio_files, videos, state.get("own_cameras") or (),
            chosen=state.get("speakers_source_chosen") or "",
            placeless=state.get("no_place") or (), alone=alone)

    def speaker_split_show(text="", colour=None, where=""):
        """Say where the separation stands: in the row of its file.

        What is happening to a recording belongs in the line that shows
        it, so the state goes into the Speakers cell of the row. *where*
        names the recording a message belongs to.
        """
        state["split_note"] = ((os.path.abspath(where) if where else "",
                                text, colour or COLOURS["quiet"])
                               if text else None)
        split_line_write(split_line, split_label, split_never,
                         speaker_split_wanted(state.get("speakers_wanted")),
                         split_run["busy"], bool(files),
                         state.get("split_note"))
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
            # The caption travels with every report: pressing Start clears
            # the plan under a running separation, leaving the step bare.
            plan.report("speakers:" + source, share,
                        speakers_step_said(source))

    bridge.speakers_split_note.connect(speaker_split_note)

    def speaker_split_done(result):
        """The separation came back: keep it, store it, show it."""
        source, count, segments, trouble = result
        split_run["busy"] = False
        plan.done("speakers:" + source)
        state["speakers_running"] = ""
        if trouble:
            speaker_split_show(trouble, COLOURS["error"], where=source)
            return
        if not segments:
            speaker_split_show("", COLOURS["quiet"])
            return
        # The names are an assignment, not a measurement: a voice that
        # had one keeps it, and the stand-in counts past the sheet.
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

        Nothing is computed again for a moved time window, a new In point
        or a renamed speaker: those are arithmetic on what is stored. Only
        a changed source file or a hand-set number of speakers start it
        over. Without *fresh* nobody asked, so the source must be alone.
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
                 speakers_step_said(source))
        plan.begin("speakers:" + source, speakers_step_said(source))
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

        It does not depend on what the row is showing: a row that says
        one person still carries what was measured on it.
        """
        return len(voices_under(path, True, state.get("speakers_by")))

    def voices_of(path):
        """The voices to show under this recording, if any."""
        return voices_under(path, remembered.get("several:" + path),
                            state.get("speakers_by"))

    def several_set(path, on):
        """The name field was answered: several speakers, or one again.

        Switching back hides the rows underneath and throws nothing
        away: what was measured stays in the project and in the cache.
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
    name inside. The lists and dictionaries belong to the window and are
    emptied at the start of every rebuild. Two names bound further down
    in gui() come through *state*.
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
              'a video file\'s Camera audio to "use the audio" in the '
              'file list.'), COLOURS["quiet"]))
        # Before the exit, not after the table: the time axis is needed
        # whether or not any sound is in use.
        if videos:
            prework_kick_off(list(videos))
        # And the button, for the same reason: the way in here is also
        # taking the last sound away.
        assignment_check()
        return
    # The cameras first, then the two special cases. MIX_ONLY: processed
    # and in the mix, but not the first track on any camera.
    # IGNORE_AUDIO: left out entirely.
    targets = ([os.path.basename(b) for b in videos]
             + [MIX_ONLY, IGNORE_AUDIO])
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
        # Empty until somebody answers, with the guess offered in grey
        # and never written in. The field itself knows both.
        name_value = SpeakerName(old_name or "", stem)
        # The voices this recording is showing. Where there are any, the
        # assignment belongs to them: it has exactly one level.
        kids = voices_of(first)
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
    # A voice the separation missed is asked for below the tree: it is
    # the input to another separation, not a row of this one.
    more = more_speakers_row(audio_file_list, voice_add)
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
            # A finished clip has nothing to assign and gets no new
            # name, so a sentence stands where the empty fields would.
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
        # A camera can contribute its own audio and is then a track
        # like any other. One camera can give more than one.
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
    # content; the first also carries triangles and the indentation.
    tree_audio.setColumnWidth(0, max(220, tree_audio.columnWidth(0) + 30))
    # The new file name is long, so it gets whatever is left.
    table_video.horizontalHeader().setStretchLastSection(False)
    table_video.horizontalHeader().setSectionResizeMode(
        1, QtWidgets.QHeaderView.Stretch)
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
    speaker_split_kick_off()
    assignment_check()
    assignment_state_show()
    # The last camera to be given a speaker takes the wide shot away.
    state["wide_state_show"]()
    # And the file list says so too: built before anybody is assigned,
    # it would go on calling every camera the wide shot.
    video_kinds_again(video_kind_again)

def make_footer(Qt, QtCore, QtWidgets, window, vertical, state, files,
                plan, bridge, late, multitrack, without_auphonic,
                settings_open):
    """The bottom row of the window: the one bar, and the four buttons.

    Outside gui() because it is one strip answered end to end -- the bar,
    the plan behind it that says what each stage is worth, and the four
    buttons. The break-off reaches back through state["write"]: the
    writer is made further down. Qt comes in as a parameter.
    """
    # Above the buttons, not under them: a line below the bottom row
    # reads like a footnote, not the answer to "why can I not press it".
    start_note = label("", COLOURS["quiet"])
    vertical.addWidget(start_note)
    foot = QtWidgets.QHBoxLayout()
    vertical.addLayout(foot)
    total_bar = QtWidgets.QProgressBar()
    total_bar.setRange(0, 1000)
    total_bar.setTextVisible(False)
    total_bar.setFixedHeight(12)
    # Wide enough to read a share off it, and growing with the window
    # rather than fixed: the stretch behind it takes every spare pixel.
    # The maximum keeps it from pushing the grey-Start reason off screen.
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

        The whole job at once, not stage by stage: a bar that learns of
        the next stage only when the last ends jumps backwards at every
        boundary. The plan before it is thrown away, finished or not --
        added to, the bar stands still, because it never falls back.
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
        or was skipped -- a step left at nothing holds the bar back.
        """
        if name not in run_step_order:
            # No caption: the key is an internal English word, and a
            # step with none says nothing rather than showing it.
            plan.add("run:" + name, 1.0)
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

        The work reports from several threads at very different rates;
        redrawing on each report stutters or stands still for a minute.
        """
        try:
            total_paint(Qt, plan, total_state, total_bar, total_line)
        except RuntimeError:
            # The window is closing and the widgets are gone. A timer
            # firing into them must not become a traceback on the way out.
            total_clock.stop()

    total_clock = QtCore.QTimer(window)
    total_clock.timeout.connect(total_show)
    total_clock.start(200)
    foot.addStretch(1)
    # Only the Resolve part: after a run, or where a handover file is
    # already in the output folder. Then nothing has to be recomputed.
    start_run = QtWidgets.QPushButton(T('Start'))
    start_run.setEnabled(False)
    hint(start_run, T('Measure, align, process, write files.'))
    # Both run buttons sit in a frame of their own: it makes the tooltip
    # of a switched-off button reachable. button_in_a_frame says why.
    start_run_env_curve = button_in_a_frame(QtWidgets, start_run)
    foot.addWidget(start_run_env_curve)
    preview_button = QtWidgets.QPushButton(T('Dry run'))
    preview_button.setEnabled(False)
    hint(preview_button,
            T('Measure only -- nothing is written or uploaded.'))
    foot.addWidget(button_in_a_frame(QtWidgets, preview_button))
    break_off = break_off_button(QtWidgets, state, lambda t: state["write"](t))
    foot.addWidget(break_off)
    # The two run buttons are one pair and switch off the same way. The
    # rank stays readable: the main action filled, the dry run outlined.
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
    # Settings belongs with the buttons, not beside the tabs: not a step
    # of the work, so flat and at a distance, but where a button is sought.
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


def app_language_set(QtCore, Qt, app):
    """Give Qt its own words, and turn the window the way they read.

    One door, because both answer the same question. On the application,
    where Qt puts the direction itself when it finds its own Arabic. Set
    either way round, or a second window in one process finds the
    first one's still up.
    """
    qt_own_words(QtCore, app)
    app.setLayoutDirection(Qt.RightToLeft if reads_right_to_left(PROGRAM.LANG)
                           else Qt.LeftToRight)


def restart_question(window, state, files, out_folder, report, folder_pick,
                     axis_file, axis_store):
    """Ask what becomes of the work before the application starts again.

    One question for the three ways out -- another language, a new
    version, a new ffmpeg -- so it says restart and not what is behind
    it. True to go on, False to leave everything standing. Nothing is
    asked where nothing has been added.
    """
    if not files:
        return True
    QtWidgets = _qt_widgets()
    box = QtWidgets.QMessageBox(window)
    box.setWindowTitle(T('Restart the application'))
    box.setText(T('The application is about to start again. Shall the '
                  'work be written to a project file first?'))
    box.setInformativeText(
        T('Written, the new window opens the project again and '
          'everything stands where it stood. Not written, it comes up '
          'empty and the files have to be added afresh.'))
    keep = box.addButton(T('Save and restart'),
                         QtWidgets.QMessageBox.AcceptRole)
    drop = box.addButton(T('Restart without saving'),
                         QtWidgets.QMessageBox.DestructiveRole)
    box.addButton(T('Cancel'), QtWidgets.QMessageBox.RejectRole)
    box.exec()
    pressed = box.clickedButton()
    # Nothing of an earlier restart may survive this one: a stale note
    # would open the wrong production in the next window.
    keep_setting("restart_project", "")
    if pressed is drop:
        state["restart_saving"] = False
        return True
    if pressed is not keep:
        return False
    if not out_folder.get():
        # The same handgrip as Save project: the sentence first, because
        # a folder dialog opening by itself does not say why it is there.
        report(T('Save project'),
               T('The project file goes into the output folder, and '
                 'none is chosen yet. Please choose one.'))
        folder_pick()
    # Written here and not left to the way out: one of the three callers
    # replaces the whole process, and nothing here runs after that.
    axis_store(state.get("axis") or {})
    keep_setting("restart_project", axis_file() or "")
    # Written now, so this window writes no more: its clean-up hangs on
    # the application and would write the production again at every quit.
    state["restart_saving"] = False
    return True


def make_project_file(QtWidgets, window, state, files, log, report, sheet2,
                      out_folder, production_var, start_var, end_var,
                      speech_language, lufs_value, edge_on, multitrack,
                      cut_var, channel_choice, clip_kind_values,
                      audio_use_values, no_join, join_to, remembered,
                      assign_lines, camera_lines, axis_file, axis_store,
                      project_collect, project_move, settings_extend,
                      commonest_folder, folder_show, folder_pick, items_fresh,
                      window_enable, tab_gone, output_show, mode_toggled,
                      player_follow_up, plan_wipe, prework_clean_up,
                      split_stop, split_run, preview_compute,
                      presets_wanted_now, presets_filter,
                      resolve_button_check, result_button_check, write):
    """The project file: write it, close it, open it again.

    Outside gui() because the three are one theme and answer each other:
    project_new is the one list of what belongs to a production, and
    project_open runs it before laying the file's answers on top. The
    call sits below the log writer and resolve_button_check.
    """

    def project_write(argv):
        """Store what this run did, so it can be reopened.

        Not the state of every button but what counts: the files, the
        output folder and the command line.
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

        This is the list of what belongs to a project and what does not,
        and it is the only such list: opening a project runs it first and
        puts the file's answers on top, so the two cannot drift apart.
        Anything left standing here is carried into the next production.
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
        # Emptied, not taken away: the axis is read by name, and a missing
        # key there is a KeyError rather than an empty axis.
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
        # and the file's answers put on top. Two lists would drift.
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
        # Intro, outro and "ignore this video" hang on the file, not
        # the table. Opening a project takes them with it, or two meet.
        if d.get("speech_language"):
            speech_language.set(d["speech_language"])
        # The saved project beats what was chosen last. null is an answer,
        # so the key decides and not the value.
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
        # The handover of that project's own run, and only where it names
        # the same cameras -- or the note promises what the button refuses.
        state["resolve_json"] = find_handover_file(
            target, os.path.dirname(os.path.abspath(file_path)),
            ours=[b for b, _n, _own, _own_name in camera_lines])
        if target and os.path.isdir(target) and any(
                n.lower().endswith(VIDEO_SUFFIXES) for n in os.listdir(target)):
            # Results from earlier: the sheet comes along with its buttons,
            # and says where things stand rather than looking like a failure.
            state["result_folder"] = target
            output_show(False)
            log.append_text(as_head(project_opened_note(target)))
        else:
            state["result_folder"] = None
        resolve_button_check()
        result_button_check()
        preview_compute()
        # The boundaries are back, so fetch the file containing them into
        # the player, or the two jump buttons go nowhere after opening.
        player_follow_up(spot_also=True)
        if missing:
            report('Project', T('These files no longer exist:\n  ')
                   + "\n  ".join(missing[:12]))

    def project_open_after_restart():
        """Open again what the window had open when it started again.

        Posted and not done here: this maker runs while the window is
        still being built, and project_open fills tables that do not
        stand yet. The note is forgotten before it is acted on.
        """
        from PySide6 import QtCore
        again = settings().get("restart_project") or ""
        if not again:
            return
        keep_setting("restart_project", "")
        if os.path.isfile(again):
            QtCore.QTimer.singleShot(0, lambda: project_open(again))

    RESTART_ASK[0] = lambda: restart_question(
        window, state, files, out_folder, report, folder_pick,
        axis_file, axis_store)
    project_open_after_restart()
    return project_write, project_new, project_open


def make_preflight(state, files, plan, bridge, bridge_emit, preflight_line,
                   set_mark, append_findings, show_overall, lines_node,
                   no_join, together_now, multitrack, assign_lines,
                   clip_kind_values):
    """Checking the files in the background, and showing what came back.

    Outside gui() because the three are one theme: the list changed, so
    it is measured again, and the marks come back into the same rows. The
    call sits below clip_kind_values, which preflight_kick_off reads.
    """

    def preflight_fill_in(findings):
        """Write the preflight findings into the list."""
        plan.done("check")
        if not files:
            return
        # Remember them: the list is rebuilt on every change and the marks
        # would be lost.
        state["preflight_findings"] = findings
        # The worst mark per file -- one hint weighs more than nine lines
        # of "fine". Which file is meant the finding says itself.
        rank = {"good": 0, "fixed": 1, "hint": 2, "abort": 3}
        # Collected per *row*, not per file: a multi-part recording has
        # three files and one row, and the last block would overwrite it.
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
        # What is left out is still checked, or its row would be the only
        # one without a mark. It enters no comparison and no balance.
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
        # Crosstalk is a question about per-speaker tracks. Without
        # multitrack there are none, and nothing is assigned yet.
        threading.Thread(target=preflight_work_loop,
                         args=(audio_files, videos_p, label_run,
                               bool(multitrack.get()), gone,
                               frozenset(no_join),
                               tuple(tuple(g) for g in together_now())),
                         daemon=True).start()

    return preflight_fill_in, preflight_kick_off


def make_time_axis(state, files, plan, bridge, bridge_emit, assign_lines,
                   blocks_of, real_tc, HOP, prework_busy, out_folder,
                   production_var, commonest_folder, project_move,
                   project_collect, settings_extend, axis_label, player,
                   video_kind_again, kind_answered, show_weak,
                   tc_column_show, player_follow_up, window_enable,
                   window_position_show):
    """The one time axis: measured, kept, and shown.

    Outside gui() because the seven are one theme -- where the files lie
    relative to each other, read out of the material, written into the
    project file and read back. The call sits below kind_answered, the
    last name axis_present reaches for.
    """

    def axis_measure(paths):
        """Determine how all files sit relative to each other."""
        return axis_with_blocks(paths, real_tc, HOP, blocks_of)

    def axis_file():
        """Return the project file, even before a name is settled.

        There is exactly one. It comes into being while the time axis is
        measured, still next to the material, and moves once an output
        folder is chosen. Two copies would be a trap: the wrong one opens.
        """
        target = out_folder.get() or commonest_folder()
        if not target or not os.path.isdir(target):
            return None
        name = safe_filename(production_var.get().strip() or 'Project')
        return os.path.join(target, "%s%s.json" % (PROJECT_PREFIX, name))

    def axis_store(axis):
        """Put the measurement into the project file.

        Over two hours of material it takes minutes, so it should be
        there next time. Size and mtime are stored with it.
        """
        # A restart told not to save writes nothing: the clean-up calls
        # this on every way out, and would put down what was declined.
        if state.get("restart_saving") is False:
            return
        project_move()
        file_path = axis_file()
        if not file_path:
            return
        d = project_collect(file_path)
        d["format"] = FILE_FORMAT
        d["version"] = VERSION
        # Without a measurement the stored one stays: this is also how the
        # settings reach the file where no axis was ever measured.
        if axis:
            d["timeline"] = timeline_entries(axis, state.get("axis_clock"))
            d["timeline_absolute"] = bool(state.get("axis_absolute"))
        d["files"] = [{"path": p, "kind": a} for p, a in files]
        settings_extend(d)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=1)
        except OSError as e:
            # Several minutes of measurement are in here. Lost silently,
            # the next start measures it all again.
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
            # way is about the list without it, so the request is kept.
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
        # A file nothing could place is proposed for "ignore this video",
        # or "Intro" where it is far shorter. A proposal stops at answers.
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
        # Only now can it be said which file holds the boundaries: relative
        # values count from the start of the material.
        player_follow_up()
        # Taken out before it is asked again, or a stored axis coming
        # back through here would ask a third time.
        if state.get("axis_again") is not None:
            axis_kick_off(state.pop("axis_again"))

    bridge.axis.connect(axis_present)

    return axis_file, axis_kick_off, axis_store


def make_auphonic_box(QtWidgets, state, bridge, bridge_emit, run_layout,
                      settings_open, buttons_check, multi_button,
                      multitrack, out_folder, commonest_folder, report):
    """The key for auphonic.com, and the preset a run is given.

    Outside gui() because the two are one theme: the key is checked by
    fetching the presets, and what comes back is what the preset box
    offers. The call sits below multi_button, which the preset switches
    on when it says no processing is wanted.
    """
    # --- In two places in the window: the key behind "Settings ...", set
    #     once; the preset under the assignment, chosen every time.
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
        de-bleed, leveler and noise removal are missing.
        """
        multi_button.setEnabled(True)
        buttons_check()

    preset_box.currentIndexChanged.connect(without_auphonic_toggled)

    def preset_picked(*_):
        """A pick by hand is the wish from here on, whatever it was.

        Only a click raises this; rebuilding the list is done with the
        signals blocked, so what is kept here is never a fallback.
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

        The call is the test: a preset list coming back means the key is
        good. Fetched in its own thread so the window does not freeze.
        *asked* decides the wording only. Neither opens a box: a rejected
        key belongs at the ungreen button and the line under it.
        """
        state["key_asked"] = asked
        key_note_hide()
        key = key_var.get()
        wrong = key_complaint(key)
        if wrong:
            # Nothing leaves the house over a key that is plainly not one.
            # Which case it is stands in the sentence itself.
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
        # Opened while it was still fetching: show it again with what came
        # back -- but never let a fetch from Connect open a list itself.
        open_after = state.pop("presets_open_after", False) and preset_list
        if preset_list is None:
            state["presets"] = None
            button_green(False)
            presets_filter()
            # Whole and unshortened: what auphonic.com said is the only
            # account anybody gets. Only the wording differs.
            if not state.get("key_asked", True):
                key_note_show(key_refused_note(state.get("key_from"), error))
                return
            key_note_show(key_refused_note("", error))
            return
        state["presets"] = preset_list
        # A store that refuses must show, or the button goes green over a
        # key that is gone at the next start. The key that goes in is the
        # one that was checked, never the field read a second time.
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

    return (access_box, keep_where, key_var, done_folder,
            without_auphonic, preset_plaintext, presets_filter,
            presets_wanted_now, finished_tracks_check)


def make_resolve_check(QtWidgets, bridge, bridge_emit, resolve_position,
                       settings_open):
    """The box saying whether Resolve answers, and the run behind it.

    Outside gui() because the box, the check and the line above the cut
    tab are one theme. The call sits below settings_open, which the way
    into the settings window reaches for.
    """
    # The box only appears with multitrack, which is where the
    # speaker-to-camera assignment is. Resolve is checked on opening.
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
        # The box lives in the settings window; its answer belongs here as
        # well, or it is written into a window nobody has opened.
        resolve_echo.setText(T('Resolve answers') if works
                             else T('Resolve does not answer -- see '
                                    'Settings'))
        resolve_echo.setStyleSheet("color: %s;" % (COLOURS["good"] if works
                                                   else COLOURS["error"]))
        # Only where it does not answer: a line saying Resolve is there
        # costs a row, and the way to the box is for somebody with a fix.
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

    return (resolve_box, resolve_left, resolve_right,
            resolve_check_run_kick_off)


#----------------------------------------------------- The window itself
# One function, and the largest in the program. What could be lifted out
# stands above and below; what is left holds the widgets and closes over.


def gui():
    """Build the Qt interface.

    Three tabs in the order they are needed: choose files, configure,
    watch. Tabs two and three appear only once they have something to
    show. The work is done by the same main() as on the command line;
    this only assembles the arguments and captures the output.
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

    # With the system in dark mode the same roles get dark shades, or a
    # white box stands in a dark window with black lists inside it.
    colours_pick(desktop_is_dark(QtWidgets, QtGui))

    # Only boxes, the tab bar and the start button get an appearance of
    # their own. The rest stays as the system draws it.

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
    # Bridge: what arises in a worker thread must not reach the window
    # from there. Qt passes signals into the right thread by itself.
    # ------------------------------------------------------------------
    class Bridge(QtCore.QObject):
        progress = QtCore.Signal(str, str, float, str)
        question = QtCore.Signal(object)
        # The key the answer is about travels with it: read off the field
        # again, it may be a second one pasted while the first was away.
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

        A thread finishing while the window closes would emit into an
        object Qt has deleted -- a traceback that reads like a crash.
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
    # The one bar: measuring runs in the background and across every tab,
    # and a bar that lives on one page is invisible when it matters.
    # Declared here because the pieces that feed it come before the footer.
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

    # Production name, output folder and auphonic.com sit as a narrow
    # strip: four values, and a sheet for them would be four fifths empty.
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
    # workflow; afterwards the list, in the same place.
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

    # Blocks taken out of a recording by hand stand on their own from
    # then on. Only removing the whole recording clears its marks.
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
    # file -> [(track file, label)]. An empty list means looked at and
    # whole; a missing entry means not looked at yet.
    split_files = ByFile()

    def channel_rows_show(node, path):
        channel_rows_build(node, path, Qt, QtCore, QtWidgets,
                           blocks_of, channel_choice, channel_node,
                           channels_arrived, clip_kind_values, items,
                           remembered, split_files)

    def files_for_run():
        """The file list a run is given, with tracks in place of sources.

        Only here, not in the list the project stores: that one keeps the
        files as they lie on disc. The tracks are cut afresh each time.
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

        A recording of several blocks has one row and waits for every
        block. The row hangs on the first block, so a finished second
        block has to redraw the first one's node -- otherwise the last
        block to finish redraws nothing and the row waits for ever.
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
        # The channels are known, so what has to be cut out is too. The
        # cameras belong in it, or a two-microphone camera is never cut.
        prework_kick_off(every_audio_block(files, blocks_of,
                                          state.get("own_cameras") or ()))

    bridge.channels_done.connect(channels_arrived)


    # Widgets built further down but marked from up here. Empty while the
    # window is assembled, so the checks below run without asking.
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
        # Only the two tabs that can hold something outstanding: a tick
        # that is always on says nothing.
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
            # The names come from the tabs themselves: a second list
            # drifts apart at every rename and points at nothing.
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
            # And the same in the window itself, in full: a tooltip cannot
            # be reached with the keyboard and is not read out reliably.
            if note is not None:
                # Nothing opened yet is where everybody starts, not a
                # fault: quiet type, and the warning colour kept back.
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
        box it borrows is created a good deal later than this.
        """
        d = settings_window.get("dialog")
        if d is None:
            d = settings_window["dialog"] = settings_dialog_build(
                window, access_box, resolve_box, keep_where, state)
        # Whether Resolve answers is asked again on every opening: it
        # gets started and stopped, and an old verdict is worth nothing.
        state["resolve_checked"] = True
        resolve_check_run_kick_off()
        d.show()
        d.raise_()
        d.activateWindow()

    def append_findings(node, its_findings):
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
                        % number_text(len(general), 0), "group", True)
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

        The Kind is shown twice in this window, and both show a derived
        wide shot -- which changes the moment a voice is given a camera.
        So the row leaves behind how to draw itself again; kinds_refresh
        calls it, or the list keeps calling every camera the wide shot.
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
    # At the start there are two ways: start fresh or open a project. Once
    # files are in the list a project would overwrite them; the reverse works.
    add_button = QtWidgets.QPushButton(T('Add files ...'))
    bar.addWidget(hint(add_button,
                       T('Order does not matter. For a multi-part '
                         'recording the first block is enough.')))
    remove_button = QtWidgets.QPushButton(T('Remove'))
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
    # Duplicate names are marked red in their row; a missing production
    # name is the same fault and gets the same mark.
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
    #     on the right. Configuring and seeing belong side by side.
    two_columns = QtWidgets.QHBoxLayout()
    assign_position_outside.addLayout(two_columns, 1)

    assign = QtWidgets.QGroupBox(T('Assignment: which audio track belongs '
                                   'to which camera'))
    two_columns.addWidget(assign, 1)
    assign_position = QtWidgets.QVBoxLayout(assign)
    # The Multitrack tick lives here, under the tables: whether a
    # camera gives a track of its own is decided in this very table.
    multitrack_bar = QtWidgets.QWidget()
    multitrack_row = QtWidgets.QHBoxLayout(multitrack_bar)
    multitrack_row.setContentsMargins(0, 6, 0, 0)
    assign_position.addWidget(multitrack_bar)
    # And right under it what auphonic.com is to make of those tracks:
    # "what should this run do" in one place, filled further down.
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

    # Under the assignment table: separating is an action on one named
    # recording. Here stands the one project-wide question.
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
    # it was heard in: a tree says the level by where the row hangs.
    voice_lines = []             # [(key, name_value, camera_value)]
    remembered = {}              # survives a redraw of the table
    suggestions = ByFile()       # what the table last suggested itself

    # ------------------------------------------------------------------
    # Extract the camera audio in the background: with two hours of 4K it
    # takes minutes, so a thread starts as soon as the table is built.
    # The work stands above in make_prework_bar and make_prework_tasks;
    # what stays here are the containers the rest of the window writes to.
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
    # Measure the time axis where there is no timecode: without one, a
    # switch could only jump to the same second from the start of the
    # file. The same measurement the run makes works here -- the envelopes
    # are in memory after the prework, and cross correlation says the rest.
    # ------------------------------------------------------------------
    HOP = 5.0
    tc_cache = {}

    # The measuring itself stands above in make_time_axis. What stays here
    # is the timecode a file carries: the axis and the column read it.
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

    def project_move():
        """Move the project file after a rename or a new output folder.

        It is named after the production and lives in the output folder,
        and both can change. Moved rather than created a second time.
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
        anything has run, and opening it should give everything back.
        """
        try:
            d["production"] = production_var.get().strip()
            d["out_folder"] = out_folder.get()
            d["multitrack"] = bool(multitrack.get())
            d["wide_at_edges"] = bool(edge_on.get())
            d["camera_cut"] = {s: cut_var[s].get() for s in cut_var}
            d["in_point"] = start_var.get()
            d["out_point"] = end_var.get()
            # Who belongs to which camera is set by hand and cannot be
            # guessed again: three speakers on two cameras come out wrong.
            assignment_remember()
            d["assignment"] = {s: (list(value) if isinstance(value, tuple) else value)
                              for s, value in remembered.items()}
            # The no-Auphonic entry is a decision, not a preset, and comes
            # back on opening. A fallback is not that decision.
            d["preset"] = (state.get("preset_wanted")
                           or (PRESET_NONE if without_auphonic()
                               else preset_plaintext().strip()))
            d["speech_language"] = speech_language.get().strip()
            # null where nothing is adjusted, and written even then: the
            # key tells this file apart from one written before the choice.
            d["lufs"] = lufs_value.get()
            # The separations travel with the project, raw and in the time
            # of the source file -- a changed offset is then arithmetic.
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

    def tc_column_show():
        """Fill the timecode column, real or computed."""
        rows = state.get("file_rows")
        if rows and not tc_column_write(
                rows, real_tc, state["axis"],
                state.get("axis_absolute")):
            state["file_rows"] = None

    def show_weak():
        """Mark the files that do not fit the common axis.

        On the first sheet and on the recordings of the assignment tree.
        Not on the cameras there: that note has been read by then.
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

    # ------------------------------------------------------------------
    # The check in the background -- the three lifted out of here. Below
    # clip_kind_values, which preflight_kick_off reads.
    # ------------------------------------------------------------------
    preflight_fill_in, preflight_kick_off = make_preflight(
        state, files, plan, bridge, bridge_emit, preflight_line,
        set_mark, append_findings, show_overall, lines_node,
        no_join, together_now, multitrack, assign_lines,
        clip_kind_values)

    # Below clip_kind_values, which player_candidates reads: the eight are
    # only called out of other closures, so here is early enough.
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

    # Below kind_answered, the last of the four names axis_present reaches
    # for. The prework is built above this line and reaches over by state.
    axis_file, axis_kick_off, axis_store = make_time_axis(
        state, files, plan, bridge, bridge_emit, assign_lines,
        blocks_of, real_tc, HOP, prework_busy, out_folder,
        production_var, commonest_folder, project_move,
        project_collect, settings_extend, axis_label, player,
        video_kind_again, kind_answered, show_weak,
        tc_column_show, player_follow_up, window_enable,
        window_position_show)
    state["axis_kick_off"] = axis_kick_off

    # Separate the speakers, locally: what the window does when a
    # separation is started, followed and its result written down.
    (speaker_split_kick_off, split_stop, voices_of,
     several_set) = make_speaker_split(
        QtCore, state, bridge, bridge_emit, plan, files, assign_lines,
        voice_lines, remembered, split_run, split_line, split_label,
        split_never, axis_store)

    def assignment_remember():
        for row, nv, cv in assign_lines:
            # Where the voices stand underneath the row holds no selector,
            # and that fallback must not overwrite an older assignment.
            old = remembered.get("audio:" + row[0])
            quiet_row = os.path.abspath(row[0]) in (state.get("voiced") or ())
            # Only the answer: a guess written back is a guess nobody
            # checks, and a file renamed afterwards no longer moves it.
            remembered["audio:" + row[0]] = (nv.typed(), camera_to_remember(
                cv.get(), getattr(cv, "derived", None),
                old[1] if (quiet_row and old) else None))
        for file_path, nv, own_box, own_name_box in camera_lines:
            remembered["video:" + file_path] = nv.get()
            # Only what somebody clicked is stored: a tick derived from
            # "one camera, no recording" is worked out afresh every time.
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
        # A typed name is an answer like any other: without this the
        # preview keeps the old name at the old camera.
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
    # Open is what a fresh one starts as: the assignment is underneath.
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

        The tabs themselves stay, and so does the assignment: which camera
        a recording belongs to is asked with the tick and without it, and
        the same answer comes out of the run either way. So nothing here
        throws a camera away -- that would delete real handiwork.
        """
        assignment_fresh()
        if files:
            table_show(tab2, T('Assignment && time window'), 1)
            table_show(tab3, T('Resolve cut'), 2)
        # What gets checked hangs on this decision.
        preflight_kick_off()
        presets_filter()
        # Camera cut and forecast live off the speakers being told apart,
        # however that happened.
        assignment_state_show()
        try:
            resolve_button_check()
        except NameError:
            pass            # the button does not exist during setup

    # --- Multitrack, under the assignment table: what it needs is
    #     decided in that table, so no earlier sheet can ask it.
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

    # --- Spoken language: the tag of the written audio track, and
    #     what the recognition expects. Empty answers both.
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

    # The key for auphonic.com and the preset a run is given stand in
    # make_auphonic_box(). Below multi_button, which its handler switches.
    (access_box, keep_where, key_var, done_folder,
     without_auphonic, preset_plaintext, presets_filter,
     presets_wanted_now, finished_tracks_check) = make_auphonic_box(
         QtWidgets, state, bridge, bridge_emit, run_layout,
         settings_open, buttons_check, multi_button, multitrack,
         out_folder, commonest_folder, report)

    # Whether Resolve answers, and the box that says so, stand in
    # make_resolve_check(). Below settings_open, which its line reaches.
    (resolve_box, resolve_left, resolve_right,
     resolve_check_run_kick_off) = make_resolve_check(
         QtWidgets, bridge, bridge_emit, resolve_position, settings_open)

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

    # What stands in place of the camera cut: one line saying why.
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

        Silent while the cut box is still being assembled: it is built
        after the tables that ask for this.
        """
        if state.get("cut_box_there"):
            wide_settings_grey(cut_parts, _edge_box, wide_note,
                               bool(wide_cameras_now()[0]), COLOURS["quiet"],
                               bool(state.get("words_there")))
            preview_kick_off()

    # The same way over as refresh_names above, and for the same reason.
    state["wide_state_show"] = wide_state_show
    # Preview: with a handover file from earlier the cut is recomputed on
    # every change, so the effect of a number is seen rather than guessed.
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

        Preferably the finished overall mix from auphonic.com: at delivery
        level, with its timecode, and what the cut timeline gets. Failing
        that the camera file carrying the mix as its first audio track --
        quieter. A speaker camera would be worse: it brings one voice.
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

    bridge.preflight.connect(preflight_fill_in)

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

    # The result button belongs with the output, not in the footer. A
    # disabled button shows no tooltip, so a wrapper carries the reason.
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
    # What comes back is what the rest of the window reaches for, down to
    # the timer that has to be stopped when the window goes.
    (start_run, start_run_env_curve, preview_button, break_off,
     plan_wipe, run_plan_build, run_step_order, total_clock) = make_footer(
        Qt, QtCore, QtWidgets, window, vertical, state, files,
        plan, bridge, late, multitrack, without_auphonic, settings_open)

    # ------------------------------------------------------------------
    # Project file -- writing, closing and opening it stand in
    # make_project_file(); this one asks for a folder first.
    # ------------------------------------------------------------------
    def project_save():
        """Write the project file now, without running anything.

        Otherwise it is written only at the start of a run and at the
        quit, so setting up a production is not enough to keep it.
        """
        if not out_folder.get():
            # The sentence first, the chooser after: a folder dialog
            # opening by itself does not say why it is there.
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

    def resolve_button_check():
        # The simple path creates a handover too, for a multicam timeline.
        # So the file decides whether there is anything to build.
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

    # ------------------------------------------------------------- The run
    write = make_log_writer(state, post)
    # The footer stands before this line and its break-off button says
    # into the log why it stopped. Reached back through state.
    state["write"] = write

    # ------------------------------------------------------------------
    # The file list changing -- the five lifted out of here. Above the
    # project file, which takes items_fresh; take_paths goes back.
    # ------------------------------------------------------------------
    items_fresh, take_paths, add_files, remove = make_file_changes(
        Qt, QtCore, QtWidgets, window, state, files, ask,
        report, items, item, drop_area, preflight_line,
        preflight_fill_in, preflight_kick_off, blocks_of,
        recording_of, join_to, no_join, lines_node,
        prework_node, video_kind_again, channel_rows_show,
        audio_use_now, video_choices_show, settings_show,
        buttons_check, show_weak, assignment_fresh,
        finished_tracks_check, prework_clean_up, remembered,
        together_now, production_var, commonest_folder,
        remove_button, bar_env_curve)

    # A file dropped straight onto the list lands here; the buttons above
    # stand long before the five exist and are hung on them here.
    state["take_paths"] = take_paths
    add_button.clicked.connect(add_files)
    remove_button.clicked.connect(remove)

    # ------------------------------------------------------------------
    # Project file -- the three lifted out of here. Below the writer,
    # because it and resolve_button_check go in as arguments.
    # ------------------------------------------------------------------
    (project_write, project_new, project_open) = make_project_file(
        QtWidgets, window, state, files, log, report, sheet2,
        out_folder, production_var, start_var, end_var,
        speech_language, lufs_value, edge_on, multitrack,
        cut_var, channel_choice, clip_kind_values,
        audio_use_values, no_join, join_to, remembered,
        assign_lines, camera_lines, axis_file, axis_store,
        project_collect, project_move, settings_extend,
        commonest_folder, folder_show, folder_pick, items_fresh,
        window_enable, tab_gone, output_show, mode_toggled,
        player_follow_up, plan_wipe, prework_clean_up,
        split_stop, split_run, preview_compute,
        presets_wanted_now, presets_filter,
        resolve_button_check, result_button_check, write)
    # take_paths asks whether the files just dropped in carry a
    # project of their own, and it is made here, below it.
    state["project_open"] = project_open

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

    # ------------------------------------------------------------------
    # Setting a run going -- the four lifted out of here. Below the
    # footer, the project file and the timer, which go in as arguments.
    # ------------------------------------------------------------------
    start, only_resolve_start_run = make_run_start(
        QtCore, state, files, log, report, ask, write, ask_user,
        bridge, bridge_emit, out_folder, production_var, start_var,
        end_var, speech_language, lufs_value, done_folder, key_var,
        cut_var, edge_on, multitrack, clip_kind_values, clip_kind_value,
        no_join, together_now, assign_lines, camera_lines, voice_lines,
        prework_node, prework_done, prework_queue, prework_run,
        prework_lock, prework_busy, start_run, preview_button,
        only_resolve, break_off, output_timer, files_for_run,
        window_length, preset_plaintext, without_auphonic, output_show,
        buttons_check, result_button_check, run_plan_build,
        run_step_order, project_write)

    only_resolve.clicked.connect(only_resolve_start_run)
    start_run.clicked.connect(lambda: start(False))
    preview_button.clicked.connect(lambda: start(True))

    # As large as the screen, but an ordinary window.
    screen = app.primaryScreen().availableGeometry()
    window.resize(min(1600, screen.width()), min(1000, screen.height()))
    window.setMinimumSize(1000, 520)
    window.move(screen.left(), screen.top())

    def clean_up():
        """Write the work down first, then stop the timers and the player."""
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
    # No fetch at start-up, not even with a remembered key: a start that
    # speaks to auphonic.com unasked speaks to a third party about a key
    # it was only asked to keep. The list is fetched when it is opened.

    # ------------------------------------------------------- The menu
    # A Mac program without a menu bar is not a Mac program: About,
    # Settings and Help are expected where the window has no say.
    # QLayout.setMenuBar puts it in the system bar on a Mac.
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

        What is held centrally is rebuilt: the palette, the style sheet,
        the stripes and marks, the rails and the clip colours. What a
        widget baked into its own sheet is swapped role by role. The log
        pane repaints from the kind noted on every line instead.
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
        # The clip colours follow ON_DARK only where they are worked out
        # afresh -- the cut already drawn carries what it was built with.
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
    # A moment after the window is up: the first thing somebody sees
    # should be their files, not a question about updates.
    QtCore.QTimer.singleShot(0, lambda: after_window(window, app, QtCore))
    return app.exec()


#------------------------------------------------ Once the window stands
# What the window opens after it is up: the offers for a missing
# tool, the version boxes, and the preset list.


def after_window(window, app, QtCore):
    """What the window does once it stands there, in the order it does it.

    Below the ffmpeg floor there is nothing behind the box, so it comes
    at once. Otherwise the update question, a moment later.
    """
    if PROGRAM.TOOL_TROUBLE[0]:
        return tools_offer(window, app)
    if soxr_offer(window):
        return None
    QtCore.QTimer.singleShot(1500, lambda: update_offer(window))


def tools_offer(window, app):
    """The one thing the window offers below the ffmpeg floor.

    A box on the window rather than a line anywhere: there is no console
    to say it in. Answered with Quit, the run ends; answered with the
    button it does not, because the install writes into the Output tab.
    """
    QtWidgets = _qt_widgets()
    kind, says = PROGRAM.TOOL_TROUBLE
    box = QtWidgets.QMessageBox(window)
    box.setWindowTitle("ffmpeg")
    box.setText(says)
    printed = how_to_get_ffmpeg(kind != "missing")
    # What the button lets somebody in for: a package manager may build
    # from source, so either way it is minutes rather than seconds.
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

    Not a gate: the run goes on either way. Asked once per version and
    written down -- a box that comes back at every start over something
    that is not broken is a box people learn to click away.
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

    The road the update already takes: a thread of its own while the
    window stays alive, and every line into the Output tab. Nothing is
    ended here -- an open window is one somebody can read the failure in.
    False where there is no window to show it in.
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

    What somebody let themselves in for stands first: this may build from
    source, and that is minutes rather than seconds. Every line goes into
    the log file too -- the pane is gone when the window goes.
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

    A timer rather than a call out of that thread: a box belongs to the
    window's own thread. It offers nothing where the job came back with
    trouble -- there is nothing to pick up then. *said* is the words.
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

    Three things somebody needs and cannot see: which version is on the
    disc, that this window is still the old one, and that it can wait.
    """
    return ("Video Podcast Magic", T('%s is in place.') % tag,
            T('This window is still the version it started as. It can '
              'start again now and come up as the new one, or you can '
              'do that yourself later.'))


def restart_offer(window, said):
    """Say in a box what arrived, and offer the restart. *said* is the words.

    A box rather than a line: in the Output tab that sentence is the last
    of two hundred the package manager wrote. The box holds nothing up --
    the window's timers go on turning inside it. True where somebody
    asked for the restart.
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
    # The same question the language button asks: the process is replaced
    # and what the window held is gone with it. No means Later.
    ask = RESTART_ASK[0]
    if ask is not None and not ask():
        return False
    start_again()
    # Only reached where the start failed: one that works never comes
    # back. Said where the offer stood -- there is no console.
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

    Asked by name: "what changed in this version" is about the one
    running here, not the newest one there. Nothing is sent.
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

    Two places show a release text. *page* is left out where there is
    nothing to look up -- a link under a text somebody is already
    reading is an offer to read it somewhere else.
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
    # The bar stands there whether it is needed or not: a text that
    # scrolls without one looks like one that ends at the frame.
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
    # through the catalogue.
    fine = QtWidgets.QDialogButtonBox(
        QtWidgets.QDialogButtonBox.Ok, parent=box)
    fine.accepted.connect(box.accept)
    feet.addWidget(fine)
    box.exec()


def changes_shown(window):
    """Show what changed in the version running here.

    The text here, the way the update window shows it -- without its
    buttons, and about this version rather than the new one. A browser
    at the whole changelog leaves somebody hunting for their own.
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

    The release text comes down with the same answer that was asked for
    the version number, so it costs nothing, and whoever just asked has
    earned more than a full stop. Without the text this stays one line
    and a button.
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
    auphonic.com has; before that nothing is asked. Fetching takes a
    moment, so it says so rather than opening on the one entry it has --
    and whoever receives them opens it again. A factory, not a class.
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

    Without auphonic.com stays selected until somebody picks: landing on
    the first entry of an arriving list would spend credit because a list
    came. Where the list cannot hold the wish -- key refused, no net --
    it stays in *state*, or the stand-in would be stored.
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
            # Not in the list yet -- being fetched, or refused. Its value
            # stays "without auphonic.com", so a run spends nothing.
            box.addItem(T('%s -- being checked') % wanted, none_value)
            box.model().item(box.count() - 1).setEnabled(False)
            box.setCurrentIndex(box.count() - 1)
    box.blockSignals(False)
    # What the box was asked for and what it settled on. A wish left
    # standing means the list could not hold it.
    gui_log("presets: %d in the list, wanted %r, before %r -> %r%s"
             % (box.count(), state.get("preset_wanted") or "", before_value,
                box.currentData(),
                "" if not state.get("preset_wanted") else " (not placed)"))


def preset_entries(presets, multitrack_on, none_label, none_value):
    """The rows of the preset list: (value, text, can be picked).

    The first row is not a preset but the decision to run without
    auphonic.com, always there. Three states, not the same: *presets*
    None means nobody has looked; an empty list is an account with no
    preset; a full list with nothing fitting is all the other mode.
    """
    kind = (T('Multitrack mode') if multitrack_on
            else T('Singletrack mode'))
    rows = [(none_value, none_label, True)]
    fitting = [(n, mt) for n, _u, mt in (presets or [])
               if preset_fits_mode(mt, multitrack_on)]
    for name, mark in fitting:
        # The bracket names the mode, so it may only stand where the mode
        # is known: an unclassified preset gets its own name and no more.
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

    In one place because two callers need them: the list puts one in, and
    the field has to be wide enough for the widest. Order: no preset at
    all, no Multitrack one, no Singletrack one. They say "of your own"
    and not "in the account" -- all we ever see is what somebody made.
    """
    return (T('No preset of your own -- create one on auphonic.com'),
            T('No Multitrack preset of your own -- create one'),
            T('No Singletrack preset of your own -- create one'))


def preset_mode_note(preset_list, multitrack_on):
    """What to say where the list came back and shows nothing.

    The presets are filtered by the mode, and an account without one of
    the kind in use leaves the list at its single entry -- which reads
    like a key that was refused, and is not. Returns (sentence or "",
    the presets that fit).
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
            % number_text(len(preset_list), 0), fitting)


def update_offer(window, asked=False):
    """Ask about looking for updates, look, and offer the new one.

    Everything happens in the window: the command line is left alone,
    because a run started from a script must not stop to ask. *asked* is
    somebody choosing to look from the menu -- then there is an answer
    either way, since silence after a click reads like nothing happened.
    """
    QtWidgets = _qt_widgets()
    tag, page, changed, trouble = newer_release(asked)
    if not tag:
        if asked:
            # Switched off, or unable to look: both mean nothing was seen,
            # and calling this the newest version would be a guess.
            if UPDATE_OFF or trouble:
                QtWidgets.QMessageBox.information(
                    window, T('Look for a newer version now'),
                    trouble or T('The check for new versions is '
                                 'switched off here.'))
            else:
                newest_shown(window, page, changed)
        return
    # A dialog of its own rather than a QMessageBox: the box hides what
    # changed behind an untranslated "Show Details" button with four
    # lines of room. What somebody is about to install is not a detail.
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
        # scrolls without one looks like one that ends at the frame.
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
        # pressed: ticking it and updating anyway still meant this one.
        set_update_skipped(tag)
    if answered != QtWidgets.QDialog.Accepted:
        return
    trouble = update_watched(window, tag, owner)
    if trouble:
        warn_box(QtWidgets, window, T('A newer version is out'), trouble)


def update_watched(window, tag, owner):
    """Put that version in place and offer the restart once it is in.

    update_fetched hands pip to the window and comes back while pip is
    still fetching, so a box said there would be said too early. The sink
    is wrapped for that one call: what the job ended with lands in a
    list, and the ffmpeg install's timer turns it into the box.
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

    Asked with the weight of the update itself: it decides which program
    runs from the next start. A list and not one name, because the
    version that broke something is not always the one before this.
    """
    QtWidgets = _qt_widgets()
    title = T('Back to an earlier version')
    owner = installed_by_a_package_manager()
    if not owner:
        # Nothing pip keeps a record of, so nothing for pip to put back.
        # Said before a list is fetched that could not be acted on.
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
    # What a step back does not do stands here: it is the one thing about
    # it that surprises people, and afterwards is too late.
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
