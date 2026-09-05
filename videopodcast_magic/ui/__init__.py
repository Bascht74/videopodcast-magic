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
language_of_system = PROGRAM.language_of_system
languages = PROGRAM.languages
legend_markup = PROGRAM.legend_markup
list_presets = PROGRAM.list_presets
load_api_key = PROGRAM.load_api_key
log_aside = PROGRAM.log_aside
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
old_self_file = PROGRAM.old_self_file
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
restore_old_self = PROGRAM.restore_old_self
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
version_in_file = PROGRAM.version_in_file
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

# Window icon: a microphone in a film strip with a waveform below.
# Written out as PNG text, so there is no file beside it to lose.
ICON_PNG = (
    "iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAAfq0lEQVR4nO2deZBdR5XmfyfvvW+v"
    "VaXSvlq2kW1ZuL27zaI2ZhuGJRobdwTdTdMhgwMmDDEYAzOETTQzNO4mYLqH7hnTwBAsDQKzGWgb"
    "MLKxMbYRGCxhWatt7Uup9qq33Jt55o97Xy1SqVTLqyqB3hfxquq9dytv3syTJ0+e7+RJqKOOOuqo"
    "o4466qijjjrqqKOOOuqoo446/vghc10BAFU9K+oxFxARnes6zCpUVVTV26zqb9q0yTuXOx9AVc3m"
    "zZt9VfXuuusuM9v392frRps2qXfTTSAiFrAjv3u+S5u7u1+gv8+cE8JQsE5bV7XIkz/+cW/SHq76"
    "naoaYs3sZkM7zHiDJx0/9DDbtx9vsEF0pap7uTHmWhFp8X1vjbPuTEX90UCBIPCplCtHMOYwsNXD"
    "e6QUFn+1/oJlB4auU/VEcDBzgjBjApCodhERB/Dsix03esb8had6Y0NDfmmhkMYTMALOKXJ2mCOz"
    "Ak1+GiMoYB0Uy5bu7p7eyPGwjaL73ODxr19yySUViLVCtR1rjRlp9VhyxUK14+WOfDZzY1tLDnHg"
    "nHVGxCkqIKg6w7llCiUtLyqCiojGA8Z44gv9g44TXT3bwij6dPHH3/nyFe96VziyTWtejVqiWtFf"
    "//rFxbl5uU81NRZuaW3MoFHkjDHOOedVTd9zZ8yPj+G2UBURp6oYz/cGK9DR2fXkwED59pdeuOjJ"
    "WBOgtZwSamp1bt682RcR+9vt+17T0F7YsnxJ2y3NWc/hrEXEWFUfkVj2a3njP3AMt4WIKh6I56x1"
    "Wc9Gi9tbrm5qyD62dfeR98XCgdRy5VSzVYDqXb7IhujpZ3dtnD9/3r3NhQy+2sgZ42sir/VOnxSM"
    "gvGxdn5zzmttbfr01p37LhKRW3UTnqrWZJVQkz7RzZt92bAh2nJQNy5t4d7mFFajSBCZ9XXtHyVU"
    "1Xh+FPkEew67z126JH+ruqKB2H6YTtHT1gCqmzyRDdGJb//1RnPki/emjkTWLX25kbYLhTACqY/7"
    "6UHB88WVugLZ/d3owlR24/EfvgcRuVVVPQUnTN2Enlbv6KabPLn5m7b3y694a0ND6pvlvh4bVSpG"
    "CkvEvPpfobAEnJvubeogwj38ATjwCMbPhJl5zUFft/tM49sfen88AG+e8upgyipaVQ03bXK/UG0v"
    "L3vDv4TFAQ39ZpHCQqHUgfYdAmNAz7X1XS2hIB5UitC9B3Lt2FSrX+rqj1KL1r/v1wf0BpGbrap6"
    "U73DdOZoERHN7w//d37e0vlRqeQManARiA8mmEbRdYyCCHgpcBGCE+escQSaY+D/7tmzpwnQqa4M"
    "piQA1bX+1u3bX7mgNbhJo6JVMSOkUJnGtFTHWNCRfxqDK9tli/Pn9VbM+xMv4ZT6cqoaQAHUZO9q"
    "zaMGi2JATKyyAPTc8e3POFRBbdy2YhDxUHVeILhCvvCeLVueawPcVLTApAUgGf3u6V2HN8xrbX2l"
    "c6imWjyxRaj0Q6UHUEgV6kqgFlAHfgB+FsrdEA5A2AOpJlHQhe3z2lKNhfcky8FJ2wJTXgYatX/T"
    "Nq8BIufcmjcaBo9B53bAwcrXI21riZeBdVfA1CHxyA/ymOvuQp/5XPxZuhEuux0iJynfqOeZt2/a"
    "tu0TQDiFO0wcqioiolu27GkqzCtsX7V0/iJnbUxreSd1dFRz3uLchufFvaXEetsCNkLEuI7eIkeP"
    "d19/+UVLfzlZ0miyw9MA+IXU5S0tTYuccw4RQRXCcPTrLIZzYJ1ibfJyinNn+Yo1iuJ2jUKohOAi"
    "VAQR3LyWvPE9fW1y5aQG9WSngJjIEV5RyKUxOGdVh8N4hpz+Z5/jRxWcKp4Rcplq0M2oK6hEjjBS"
    "TNywZxeEkyTUJApBxYjied7L7tK7DCOiiyaCyQqAA/A872rPA7Uat5MqBMGwPrHEEnuWtKJzShAY"
    "As+jWLZs21nkhYMljnZEiEAhb1izPMPKZWlaGwOcOkplhzmbItTEh9SI95VYy6tTA2CMWXfjc+/N"
    "y1rpq07VEyl2sgKgm1V92Xt0ngGsahzSEvjovp9D1464rkteAW0XcDZwAU4hl/E40R3xvZ928Oiv"
    "etl3qEI5VJyN20gMBL6wYF7AlZcWePONLaxZkaFUcajO9SPEnCClbvTZ74KzkG5Gzn/LCI0gmgqC"
    "jA52twB9DFsLZ8SEBaAqVY9v29foFdLnqwOcE1IBuu8R9JE7kgsjdNf3mGsuoNo2ubTHDzZ38m/f"
    "OM7xzpBUypBOCamUGe5YBVWlozviOz/p5MFHu3nTja3c+rZ2MBBFipmzxYyAK+Me/ygceAT8HESD"
    "UDyGXHYbhKGoWtfQUCgMDBTPB/YxiQaf9DLQOlW0Os9oHNTXuSP+Ozs//p1wAdK4DKyd9SFU7fxM"
    "2vDpLx7mW/9xgmzW0Nzo4xTUKW4Miy/whXTKx1rla9/rYMfeIh9//zJyOUMYzoUQaKz6y31DXAAS"
    "gPGg49nRV6ridPLet9o8kp8mltSIs4ELUCCb9vj0Fw7z7/d30FDw8IxQCR3WOpwqOsbLOSUMHapK"
    "c6PHlmf6ufOeF6lUFN+TuVsljOACUJs4h9I1Kbo2AqBDP0Z8MDetZR3k0oYfPtzFd37SzaL2NL5v"
    "8H1DOuWRCsZ/Va8RY1gwP83vd5X5l68eIfBlbh2bJ9+8RpWpTUiYJh6/kV6/OeACVCHlCyd6Iv71"
    "q0e4YcNyli3NUy5PbRYSARs5vvWdnbz8ykauWl+gWHKzPxWcxAUgXtzmNcD0BUCBdDNExXh+wgIy"
    "J1yAc0qQ9rj/oQ5OdFt27erg+b2duCnWoxq96lT55n+c4Ip1hdlfEYzkAgYOxUZgpQdSTTWxracn"
    "AOJBaJE1b4SBuecCPF8oli0PP9lLJm04dmwAO02PtAhkAuGZ5wZ5/kCJ1csylCtulgTh9FyA/Mnt"
    "EE1/hVWjKcBD/uS20Z9Fs2v9OwfZjGH77kH2H6qQDgQxBr8GTygC3T0Rv312gDXLszineN4sPZuY"
    "eCXVdjFyw2dGcwFu+m1co7BwPdX/P8ssoCoIwt79ZcoVRzrlU67YaVvuIpBKGYwRdr9YTj6cfn0n"
    "jShi1JwqUpOK1HZ38JxyAfG9j54IY2IHmN+WI532pmUDOFU6O4uIicsGre5tmV2MwQXUAjWaAs4e"
    "LsD3BESw1nHxxfNZuDBPGE59FVAJLT/96V7URQT+HPqET8MFTBc1WAXoWcUFqMY/fN/jl08cHApM"
    "nlItJGERnUOMxF7tWcdEuICpY3oCoI6zlQsAiCI7YuPl1DFrBt+YOCMXMC17a5oa4OzkAqowxtTo"
    "1nPlA5w4FzBV1MYGGMkFVCt9FuwLqFQi3FQtwCEI2eyU913UBlUuIBpMNtvUjguokRE49GPEB3Po"
    "ORfBOeXCC9pobEzFzqCpGIGAtY6du06gauc2LqDOBUwOqkpzc4a2+dl4QTKFMkQgDC27dp+Y2xD3"
    "Ohcw2Topnufx1K8OotO2lIV02iBmjujgOhcwdQTBH/qehDoXUEedC5g6qtE900M8Bcw56lzAxFDd"
    "uGCt46orl9TECPzlE/tRN8ergDoXMDFYR+yKEKG7u4RzbtrLQE3Km9NkpnUuYGJoyBtE4u2KO3Z2"
    "1MwRpEBDLpHwWU1yWOcCJoSYolXOW5EhCAR1Sirl10T+RMBZZc3KDCCJXTFbElDnAiYEEahEyqql"
    "adrnBZzojvA9xbrpd5UxQjotXHJ+Fp3VeIA6FzBhiEAYKS2NAVetL/CdBztpbQliJ9o06GAR6B+w"
    "rF6e4aI1OcrhHEQF17mAiUGIt32/5dWt/PBnXVx15VIWLcpRqUw9IMRZx9e/tZO33NhCOmUYKFq8"
    "ueCG6lzAmWEMlCuO85Zl+PPXtfKjnx9mUXuaSji11vI9oacv4qVrs7zquiZKlbnq/DoXMHy7RKVX"
    "97+KjB7dIlCqWN51ywJ+v/N5tmztorXJI5xke/keFEuOQt7jjo3nEQSGcuVU9T9k445Rl5qgzgWM"
    "RuBLHPeXILJKZIclTZIwLgX+/o4VfPgf9/P0swO0NvkoSYedVjIFI7Em6RuwtLSkuOeDy1m6MMVg"
    "yZ2SBccYyKSGP3SqU9Y2p6tPnQtI4JySSXk8+Fg3P3iom8YGQ2+f5Q03tPCa65spVexQQgeReEt3"
    "Lmf4hw8t57NfOcL3f9qN8SCbNnGIl4IOCUKcEcQ5pVhWSmXH5ZfkufPWxSxdlGKwZPFGJItQhXQg"
    "7Hi+xP/52lEyaUOx5HjJmizvvqWdcqi1e/Q6F5DcQePl2P7DFX7x6z7aWn06OiMuXZuLj145aeAZ"
    "E68KgkD44MbFvPLqRjb9qJNnnhukuzfCiAypc9XYeEynDOctT/PmG1t51Z82kgrklM4fWZeu3ojH"
    "f9NPQ96jd8Diks8Vrb2X4FznAqqOnvNXpmlq9MhmPJqblL37yoAiY6RzMQLWKoORctWlBa5YV2Dv"
    "vhK/+f0gew+UONYRxilich5rVmS4+IIsF5+fJR14lCqWUkVP6fz4MWMjZPeLJdIpQ0PeEEbKS1Yn"
    "jiKnUOtA0joXEKd7Wb4oTSZtqISOwDc8t7fI0Y6Q1hafKDpV9VYNs8FSvJ9v9fI0a1ZkOdUOiAWs"
    "VHEMlCI8E9sDY8F4ccjZr7cNYrx4KlZVVi2vzdp8TJzrXIAxUIkcSxamWNye4oWDZXIZQ0dnxK+2"
    "9vOGDa1UKtFpQ7ir6r5cUZyLEg2aXKtxB0oyLYw16qtwDtIpw94DJbbvHiSbNrG9kTWsXZ3FqdY4"
    "uVSdCxiCjZR81uflVzWw4+tF8llDEAjffrCLG/+0GZNk8RhP5kTGiPOXoR9nRDXV3H0PdjJQdLQ0"
    "+vT0W65eX2DFkpnYOTyzXMA0J5KTuYA2yC1gps4LMEYIreONN7SwsD2gVHHksx479hb52v0dZFMe"
    "dtrs3+kRWaWQ9XnqmT4eeKSHhryHc4oReNt/ap2B4xGUk88LIN0CqYaacQF/UDmCRKBSccxrDvjP"
    "f9ZCX79N8vx5fOnbx7n/Z50Usj6R1ZoHcEZR3Pnb9wzy8c8exDOxp7C333L5ujxXXFKgWJ4hnqCe"
    "I2gYxgjl0PLnr2ll3YU5evssviekAsM9nzs8JAQk6/rxUE0XO56wOI2DTAq5uPM/+Ml99A04Uimh"
    "VI49he++ZQF2pumPGeICaiQAI7iAGT4vQCT2ixTyHh9612KamzwqocP3hWza8KnPH+aL9x3DiJDL"
    "eEkHjt3J+YxHPuvjeSeJr8amS+x8EvIZw0OP93DnPfvoH3RkMyZOjxwp73vHQi5YlR3TTVwzzCAX"
    "MP0qj+QCZum8AGOgWLKsWZHlo+9dQqnsCEOX5Pkz/Ns3jvHuj+7l8af7yaYN+YxPKogNxGpyaAF+"
    "+HA3X/n+cQYGHUKs5lVj1Z7LGHIZn+f3l/nQP+zj7n8+wGCp2vnK8c6Id751Pq99eQv9xegUN3HN"
    "MNZ5AecyF1CF58VeuisuKfCpj6zg4589SFevpang0dQYd9x/+9R+Ljk/y40va+LyS/K0zwsIvDhR"
    "9Fe+f5zPfPEIqrBtR5G/v2M5pEBxdHZbtu8p8sAj3WzZNsDAoKOQN3gmVvuVULnz1kW85dWtDJbs"
    "KG6itph5LmDC/11NFfvoMy+2zG/I7Fm1tL3F2SgJjxHw5+a8AOtiVb7rhSKfvPcQ23YWaWrwCHzB"
    "OmVg0OGc0tLks3xxmrXnZWlr8Xng0W72H6qQShl8D256XSuhVZ7bU2LvvhLHuyKcI15qJmX19Fna"
    "Wnze/85FbLi6iWJ5FiOFxzovwA21sesZjMzhI8f/7LK1yzZP5syAGgkAp875s7gvwFoll/UYGLT8"
    "+/0n+NYDnfQPWPI5L1b9QBgq5UqcDh5i9+9Q8giB/gGHdUrgC6lUbFSaJE/wYDF+tldd18g73trO"
    "8kVpBoqndzrNCPQkK3M0FzBlAfiD4QLGg+cJxZIjCISNb1vAhmubuO+BEzy2pY/O7gg/sQ2qnQ6x"
    "AVetrio0N3oxI5jYCcWSo1xx5HOGq9YXuPn1rVx1aQGrOvudD3Uu4EwwJrbcB0oRq5enufPWJfzV"
    "W8o8/GQfj/+mj+f3l+kdsESJBshnvVFWe3efxdo4J3Aua1i1NM0V6/LccF0jF6zKIgzzCXOSMeRc"
    "5wImAhHwJDbUUGX+vIC/eEMbN7++lcPHQvYdLrN3X5nefstPftFD/8BwDMEbNjSzqD3F0gUBK5am"
    "WbIgRTbtocSHR8QU8Kw9ygjUuYBJwyRETxgqZY25/0XtAUsXprjuskYAXjhY5omn+8mkhULecPs7"
    "FpJNe8TrAKVSUQZKUUwQzUSo14RR3xcwaThX5eyT96oUS/GcbzXOJn5yCtmevjigwyaHQwwRhapY"
    "ABmfJZwZ1PcFTBqqnOZQqNHwfRlls7Y0+aTHzSeglEM3N0ki6vsCJl6NVCA88dt+tu0cxB8jsWNs"
    "sgiHj1VIBZIQTMqXvn2cdMrg3KlBJVGkLF6Q4pVXN+J5sYaZ/azhZ3g/RfzR7AuwTslnfL52/3H+"
    "6UtHY//+WHKYRA1XYwlU4yCRL913HFeNJdDR18cZQ5XXvqyZu29fSmW2M0bW9wWcoQoKgW/o6Yu4"
    "78FOCnlDOmXGZ/lGEEQi0NQ4flMIyiO/6mXrjgHWr83P3sER9X0BE4NqHAFcyHkc64hIp4iDM09X"
    "dUar8XGvlXjjaeDH5Y81TcwM6vsCJgRJon+zaY+NN7fzyXsP0dNvMTL9pXJ1o4nvC29/UxtrVmQY"
    "LLvTBozWHPV9ARODMUKp4rj+igYuWL2avfvKNdvHZy3Mn+dz3rJMHPUzFz6Bc31fwERQDf9uafK5"
    "5qW1XYY61dkd+SejzgVMDFUGLxxzj54ObSyVSY4eEeau86HOBUwGY+3SjQePkApkKGj0DyON4dnJ"
    "BcR3nkMuQCdRatWIMwInuiMaCx7plFCu1MCaj/3OiYqYkZDgCXEBiet70hIxaQHwjAhoMsHOPhdQ"
    "fcJADJG6oR09p71eY/q2f8Byz72H2LqzSHtrwB0bF3H+ygyV6ZwJrIpkhm0NrZFaHnGDCXMBnueh"
    "6iZt+Ezq0VVV6KWoyv7YyE/OqJ+lfQFK3PEp43GiUgQg7fnjir1zSso3PPhoDw8+2oOzsHXnIF/+"
    "bseoWD4lNvR0ooNIQVI+0e+epfilr1PZ/NjMkZ7j7wtQEZHBYrGo1h0Yrt3EMGENICKqqua665YX"
    "n9l58IjCRVLlU2aMCxhW9ErM9fdGZf7uuUd5pvcI7ekC//3C67mwoY2Ks5hxemCw5MilDZ6BXNZQ"
    "rlRXLKAovsRxhM5B2UXjG4nOIemA8HfbGLjrf4B1aLlMduPfkLn5TWgpBGOSbCaxhpq2EhyPCxAj"
    "xcFiKUyHB09z9WkxWeUncen6rI0JkcQWqPW+gESATCKfqjh1pDzDj47u4kdHd2EVftdzlC+8+Dt8"
    "I8OPrLFX72T7yEvCvZR42q5a9KpK2vh0hUV+fnwfzw90kzHja5Vq2jH7++0QRUhbK5LPYbduG2qm"
    "qt2Ry8T2xrTstdNxAfH4UESxTp/3e88vVmM3J1r0lIxAce6hYjl6bz4gFoFUcw25gBEdX+yEdBP4"
    "PkQVAAaikJwf4ImQ9wPKLhq6j2p8fKznGZwqUUVHlnryXVCUtGd4fqCL27c+yKFSH2njc/faV3Bj"
    "+ypKkSU2edxQpw8JOMRLX4i9nk6H3qtCOi2c6IrY+UKJRe0BK6e6cfQMXIABh4ixzj52xRUSqqoP"
    "TJgpmqwAOIDeAX0q19Xbm1/Q3EglUjn/jcLgFLiAKq9ataKF+PpKD/rE/0SPPwP5dszVH4GW80Hj"
    "aSCeq+M5u6r2VSFIC4NdEZ0vlCi0B7QsyVAqnd4wcyi+8fjp8Rd4frCbxZlGOsoDfO/QTl7Tvprh"
    "ghMfhwLhiPJOHtZJvYJAeOFAmTvv2c/h4yGZlPDh2xaz4ZomSsn+wWF7Q/BOKxVn4AKsw6mY/v4K"
    "GvGTai1O3+CnYlICULUDROTQMzsP/MIEra91oTpV402aCxBGW9A2cSdnfHTnA+jzP4L8Ijj+O3Tb"
    "/4NXfALglFNAq+aHHwjdB8o8dM9++o+HeCnh+tsWs/zqRs7UJgIE4mHV4YngD9Vb49F3+Dfokaeg"
    "aRWy4lXjGnsuUf0PP9nHiwfKLFqQoqMr5Aebu7nh2qYhmyPn+0NCVRpvD8XpuIAIcJEaz5eOzmNH"
    "+yX9SLUK4z7sSZjKFGDim8hX+wbs63I+8WJgClxA6ZvfJ/rNbzHLlpC55a1IQy4ZZQMQ5GJ1G+Qh"
    "Ko+78FcHfsrw4pN9dB8o07AgxWBXyK7N3ay4ppHqnDweqtb/kPladXAd3oL+7L/EDhhbgis+gFz0"
    "V2d8NpFYE1gbHzRdDSdTIGt8nug8xFNdB1mdb+HG9lVnthHG4AKMMdaCH0bhD65fu7RvMvsBqpjK"
    "Ctiqqpw4WLnvyNGOHcb3jKBu2Ag0Z1T7kvIIH/slxXs/T7RjF+VvfZfy17+FBEHS0V5iRGr8e6LE"
    "koAXCGoV8WR65/xo4uM4+tt4+ZVrj/flH9kyyuA8UxEjfzuUrGd4susg7/3dj/jCi0/zgW0/4av7"
    "t5LxPNx4lRU5qX1FFcyxjt5yxco/TqxGp2LSApBYmGbDhlWlKIo+UQxVQCaudpKHdAcPIdks0lBA"
    "mptxh48kN+DUuXUSz6UT7JwJw0sx5ONQB97UY/EUxYjwVOchIpSFmQaa/TSPnzh45n8eVQ4YEavG"
    "mJ6evm9c8ZIlzyWjf9JLr6n6wJyqmoMy+PX9B48+7cTzjWAn0+bS0IAOFiEM0f5+yOXiL6bTcSdN"
    "ETVxQNrKiNHnxe+niGQNzep8M2Ub0RUW6QyLrMo3J7bBhMtRp8iho919kef+TlVPDmSbMKYkANV1"
    "5usvuKBsnf3boyd6rFNRmcgBPcagoSN45fWkNrwcjMG/6ELSb31zYjhyUrjOxHvRJQyg8WLHi51W"
    "1s6kRxqWDm99L3dBw5LhKo1n444hjAZD0VpevWA1d6y5jksb2/nr5eu5deVlVKyLl5wTq1lUdsbr"
    "7en78OXnL98NmKmMfpgGGygiLlE7Tz/97IsfmNfa9Om0IXSq4/uAkw14UiiQ+/B/Rbu6kYYGJPDQ"
    "cjlO0ouCDRNbwMavccsEq8qCtTmMLwx0hUQVZdHF+aQjxid9Tg6tEBLutxIhK18FxTvg0C+haSVy"
    "6UawUeybGAdVOtr3YhKqmkJWiaepd65azztXrAcDoVUidRMSdSOE+F6wb8+h+y67aPlnVdUXkSlH"
    "iE6LDhYRmwjBZ7buPnTRqhWLNvpqIz1TucLQ9nFpbgZr0UoUkxyRIss2oLvvjx0fXgbWvJHYIBzb"
    "pSoGwopjybo8r/7Icg5vG6BpSZpV1zYRlh2pzBk6Sx0K+GIwIlTcyLW+Qdb9JVzyl0m9GXJKjd0m"
    "Mf+wfm0O3xeOd4WUK8rlF+eT8kAFBsIoNncsGJlYdIJApJ4XvLj/xK9IRRtVtRocNmXUIiDEJb6B"
    "W7fuPsyq5Qs3BrjQxR6p0z9XtSergSPV99ZC00rMaz6Pdj6HFJZA03KIwiFPW7W5Ro5cAcKKsnhd"
    "gWXrGnAoYcWNOzMKsVPpsuaF+GI4Vh6g5CKubFk04iqFSiW5g45ekYyh5w1xyvor1+X51EeW8+tt"
    "A6xckmbDtU2URqSROb3zZ2wYIax2/rHeQ6952aWXdiXtPi1zd9oCkDiHSDTBrVt3H2b1yoUbJYps"
    "Urvx7YyxJssognQLsuza2K0RDWs4BUK1eGKwqkQjzA4RCEuOimpit43fyAZhIHJc07KEz65//ah1"
    "ecna4TlZThNcWBVeY6qhSPHlCKWKcuW6AleuawDiDKRTQWKJROqP2fnT3qBQk5CwRAiGNMG23UcO"
    "Njbm725rLmDURop6k7LJRWKyo5J4f0QwCpFTbpi/ku8f3sGhUh8Zz+dNiy/AjRjmYoY1xFjFjvxd"
    "/bvkIq5pXcw1bYvP7JkbUYBZuDC2W/oH0N5eZEF7/L3GuYsHS9V4BaaSPVSNYCOLX1YvOHr4xKau"
    "/iO31bLzoYZBoSM0gRGRj/1218EnSqXKPy1e2HqBh2LQSFWNghnHqTeyxFE9JRIniVyVa+ELl72R"
    "5/o7WJJpZHW+efRoPQ1UY8PM82QoUdTwnYTBKJqAbz6BMWjFErzsWrIn/naUN1OjYaoxVvcT6/gR"
    "xLcaMdap+s54/tGOnp7BUvmjl6xe8M/xt7Xr/InXbpKoWqZb9uxpavCb3x/45t1tbc0LUh6ojdSI"
    "sYpKYsQwGe3gVAmMITAGp1Cy0bid71y8X3DfoYScOVYhnTZ85N0xOVOsnJoOfmIPSdx6qRHTQ6ST"
    "jYBSUIwYB6iqGoxnHHD0eHelHLqvlgd7Prl+7eodSVvpdOf8kzFTMSxs2qTezTfHfuln9uxZEPiN"
    "twWef1M65V/U1lrASHwWX+z4c26inoz4OsVVAy3O8AhCTNBk08LxzpieXdwesGppmlLFIcg0fE8a"
    "F16t/FjRqOP8r4gxVJecAn39IT19/QfC0D5QttH/eumaRduAqn01I1m3ZkwAAFRVHn74YW/Dhg1R"
    "8t7b/kLnVah9NdiXiZj1vmdyjY2NOdWZTSShqvi+kEnFuf1jbr5W95vYpDayLp7n0dPTY51qr3O6"
    "GzG/sI7N/ZE8fM0Fbb3Jdd7dd6Mf+1jtVP7JmFEBqCJxVZqTpXjLnj1NaZdu9P30mlKpNLOV8GP/"
    "TVSKfThebbfETAoWaGpuprej40jr0pWHV7VI98jvVdUjVvdzeVpx7aGqsmnTJk9V/eH5vw5ANm9W"
    "X1W9ZLCcG1BVueuuu0zy4Ofiy5xTHV5HHXXUUUcdddRRRx111FFHHXXUUUcddcwR/j+kB10kFclR"
    "bAAAAABJRU5ErkJggg==")


def app_icon(QtGui):
    """Return the window icon, if it can be built."""
    try:
        import base64
        video = QtGui.QPixmap()
        video.loadFromData(base64.b64decode(ICON_PNG))
        return QtGui.QIcon(video)
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
                    TN(len(row) - 1, '%s  + %d continuation',
                       '%s  + %d continuations')
                    % (os.path.basename(row[0]), len(row) - 1),
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
            value = (T('%s  (%s)  --  %s  --  %d blocks')
                 % (as_hms(total), as_data_size(sum(size_in_mb(x) for x in row)),
                    T('Timecode from %s')
                    % timecode_string(min(t for t in tcs if t is not None))
                    if any(t is not None for t in tcs)
                    else T('no timecode'), len(row)))
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


def player_of_tab(tabs, players):
    """The player standing on the tab showing now, or None elsewhere.

    Which tab a player is on is nowhere written down: the sheet is
    asked whether the player is inside it. A player folded away is
    none: the Resolve preview goes when there is no cut to show, and
    the transport used to drive a picture nobody could see.
    """
    sheet = tabs.currentWidget()
    if sheet is None:
        return None
    for one in players:
        if (one is not None and sheet.isAncestorOf(one)
                and one.isVisibleTo(sheet)):
            return one
    return None


def player_loaded(one):
    """Whether a player has anything at all to play.

    The preview player holds one file, the cut player a list of shots.
    Both are empty until material arrives, and every transport command
    on an empty player returns without doing anything -- which from
    outside looks exactly like a program that is broken.
    """
    return bool(getattr(one, "file_path", None) or getattr(one, "cut", None))


def transport(pick, what, *rest):
    """One transport command, to the player of the tab showing now.

    A player that does not have that command is left alone rather than
    raising: which player is meant is decided at the press, and the
    stand-in for a Qt without multimedia knows less than the others.
    """
    doing = getattr(pick(), what, None)
    if doing is not None:
        doing(*rest)


def build_menus(QtGui, QtCore, QtWidgets, window, tabs, player, does,
                switched=None, cut_player=None, late=None, buttons=None,
                project_here=None):
    """The whole menu bar, from a table of what each entry does.

    Outside gui() because it decides nothing. Every entry is a name, a
    key and something to call, and all three come in; what is left here
    is the order they stand in, and where the lines between them go.
    *buttons* are the ones the switched entries follow, in their order.
    """

    def act(where, text, doing, keys="", inside=None):
        """One menu entry, with its key.

        *inside* scopes the key to a widget: the player keys are bare
        ones -- Space, I, O, the arrows -- and a bare key must not fire
        while somebody is typing a name into a field. Attached to the
        player, they work when the player has the focus and nowhere
        else, and the menu still shows them. Several widgets may be
        named, and then the key works at whichever of them has it.
        """
        action = QtGui.QAction(text, window)
        action.triggered.connect(lambda _=False: doing())
        if keys:
            action.setShortcut(QtGui.QKeySequence(keys))
            if inside is not None:
                action.setShortcutContext(
                    QtCore.Qt.WidgetWithChildrenShortcut)
                for widget in (inside if isinstance(inside, (list, tuple))
                               else [inside]):
                    widget.addAction(action)
        where.addAction(action)
        return action

    menu = QtWidgets.QMenuBar()

    # Three groups, in the order the work goes: the project first,
    # because a session begins by opening one or starting a new one;
    # then the material; then the run. Before this the project was not
    # in the menu at all -- the only way to a second production was to
    # quit the program and start it again.
    file_menu = menu.addMenu(T('&File'))
    act(file_menu, T('Open project ...'), does["open project"], "Ctrl+P")
    project_entries = [
        act(file_menu, T('Save project'), does["save project"], "Ctrl+S"),
        act(file_menu, T('Close project'), does["close project"], "Ctrl+W")]
    file_menu.addSeparator()
    act(file_menu, T('Add files ...'), does["add files"], "Ctrl+O")
    remove_entry = act(file_menu, T('Remove'), does["remove"],
                       "Ctrl+Backspace")
    act(file_menu, T('Output folder ...'), does["output folder"],
        "Ctrl+Shift+O")
    file_menu.addSeparator()
    run_entries = [act(file_menu, T('Start'), does["start"], "Ctrl+R"),
                   act(file_menu, T('Dry run'), does["dry run"],
                       "Ctrl+Shift+R")]
    followers = [remove_entry] + run_entries
    # The window decides what lives here, not the menu: these five are
    # handed over and switched with the buttons that do the same thing.
    # Born grey, because an empty window has nothing to remove, nothing
    # to save and nothing to start, and a fresh entry is born alive.
    for entry in project_entries + followers:
        entry.setEnabled(False)
    if late is not None:
        late["menu_project"] = project_entries
        late["menu_follows"] = list(zip(followers, buttons or ()))
        late["project_here"] = project_here
        # A menu built once carries the state of then, and the buttons
        # move while it stands: a run greys them, so does a selection.
        # Asked again on opening, as the View and Player menus are.
        file_menu.aboutToShow.connect(lambda: menus_follow(late))
    file_menu.addSeparator()
    # Qt moves anything it recognises as settings into the application
    # menu on a Mac, which is where people look for it.
    settings_action = act(file_menu, T('Settings ...'), does["settings"],
                          "Ctrl+,")
    settings_action.setMenuRole(QtGui.QAction.PreferencesRole)

    # The tabs by their own names, not "1. tab, 2. tab, 3. tab". The
    # name is read off the tab, so the menu says what the tab says; the
    # tick a finished tab carries is left out, since it comes and goes
    # and a menu entry that changes under the hand is worse than none.
    view_menu = menu.addMenu(T('&View'))
    def view_menu_fill():
        """Name the tabs that are there, each time the menu opens.

        The menu is built once, at the end of gui(), when only the
        first tab stands -- the other two arrive with the material. So
        a menu filled once names one tab for ever, and Ctrl+2 and
        Ctrl+3 name nothing at all. Qt has no signal for a tab
        arriving, and it has one for a menu opening.
        """
        view_menu.clear()
        for number in range(tabs.count()):
            named = tabs.tabText(number).replace("&&", "&")
            shown = act(view_menu, named.replace("\u2713", "").strip(),
                        lambda i=number: tabs.setCurrentIndex(i),
                        "Ctrl+%d" % (number + 1))
            # The entry shows the key and must not answer it: the same
            # key on the window would then be a second answer, Qt calls
            # that ambiguous and fires neither. Every key was dead the
            # moment somebody had opened this menu once.
            shown.setShortcutContext(QtCore.Qt.WidgetShortcut)

    view_menu_fill()
    view_menu.aboutToShow.connect(view_menu_fill)
    # The keys are not the menu's. A shortcut on a menu entry exists
    # only while that entry does, and refilling on opening would leave
    # Ctrl+2 dead until somebody had opened the menu once. These hang
    # on the window and wait for their tab.
    for number in range(TABS_AT_MOST):
        keyed = QtGui.QShortcut(
            QtGui.QKeySequence("Ctrl+%d" % (number + 1)), window)
        keyed.activated.connect(
            lambda i=number: (tabs.setCurrentIndex(i)
                              if i < tabs.count() else None))

    play_menu = player_menu(menu, player)
    # There are two players -- the preview on the assignment tab and the
    # cut player on the Resolve tab -- and which one is meant is decided
    # at the moment somebody presses, not when the entry is built: the
    # tab changes and the menu stands.
    both = [player] + ([cut_player] if cut_player is not None else [])
    played = []

    def playing():
        return player_of_tab(tabs, both)

    def play_enable():
        """Grey the transport out where there is no player to drive.

        On the file tab and on the output tab there is no player at
        all, and on the others none until material has arrived. And an
        entry the player of this tab cannot do stays grey as well.
        Asked again whenever the menu opens, for the same reason the
        View menu is refilled -- a menu built once carries the state
        of then.
        """
        one = playing()
        on = player_loaded(one)
        for entry, what in played:
            entry.setEnabled(on and hasattr(one, what))

    played.append((act(play_menu, T('Play and pause'),
                       lambda: transport(playing, "toggle"), "Space", both),
                   "toggle"))
    # L and K as in every editing program: L runs forward, K holds. J is
    # missing on purpose: backwards the ffmpeg backend under Qt reports
    # a rate of 0.00 and stands still, and a key that does nothing is
    # worse than none. K holds and never starts -- that is what it does
    # in an editing program, and the space bar is there for the other
    # half.
    played.append((act(play_menu, T('Play forward, faster on every press'),
                       lambda: transport(playing, "faster"), "L", both),
                   "faster"))
    played.append((act(play_menu, T('Pause'),
                       lambda: transport(playing, "pause"), "K", both),
                   "pause"))
    play_menu.addSeparator()
    for text, keys, seconds in (
            (T('One frame back'), "Left", -1.0 / 30.0),
            (T('One frame forward'), "Right", 1.0 / 30.0),
            (T('One second back'), "Shift+Left", -1.0),
            (T('One second forward'), "Shift+Right", 1.0),
            (T('Ten seconds back'), "Alt+Left", -10.0),
            (T('Ten seconds forward'), "Alt+Right", 10.0)):
        played.append((act(play_menu, text,
                           lambda s=seconds: transport(playing, "nudge", s),
                           keys, both), "nudge"))
    play_enable()
    play_menu.aboutToShow.connect(play_enable)
    tabs.currentChanged.connect(lambda *_: play_enable())
    play_menu.addSeparator()
    # The same four things the buttons under the player do, and they
    # are greyed with them: the buttons went dead without a time axis
    # while the menu wrote +0:00:00.000 into both fields.
    for text, doing, keys in (
            (T('Mark In'), does["mark in"], "I"),
            (T('Mark Out'), does["mark out"], "O"),
            (T('to In point'), does["to in"], "Shift+I"),
            (T('to Out point'), does["to out"], "Shift+O")):
        entry = act(play_menu, text, doing, keys, player)
        if switched is not None:
            switched.append(entry)

    help_menu = menu.addMenu(T('&Help'))
    act(help_menu, T('The manual'),
        lambda: open_page("https://github.com/Bascht74/"
                          "videopodcast-magic#readme"))
    act(help_menu, T('What changed in this version'),
        lambda: changes_shown(window))
    log_entry(act, help_menu, window)
    help_menu.addSeparator()
    act(help_menu, T('Look for a newer version now'),
        lambda: update_offer(window, asked=True))
    restore_entry(act, help_menu, window)
    about = act(help_menu, T('About Video Podcast Magic'),
                lambda: about_show(window))
    about.setMenuRole(QtGui.QAction.AboutRole)
    return menu


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


def from_the_front(entry):
    """Show a name from its beginning, and the whole of it on hovering.

    The column is narrower than the names are: they begin with the
    production and end with the camera, so a field showing its end
    reads "...11855_C002.mov" and one showing its beginning reads
    "PresentersCam_0...". The second is the one that says which row
    this is. Measured against the demo material: the name comes to
    about twice the width the column gives it.

    A field keeps its caret where it was left, so this is done once on
    building and never again -- typing must not jump back to the front.
    """
    entry.setCursorPosition(0)
    entry.setToolTip(entry.text())
    entry.textChanged.connect(entry.setToolTip)


def widget_width(w):
    """How wide a widget in a cell has to be to show what it holds.

    resizeColumnsToContents measures the text of items, and a cell with
    a widget in it has no item text. A column of input fields or drop
    downs was therefore measured as empty and came out at its minimum:
    the name column stood at 114 pixels with
    "Guest_Take0021A_Timecode.wav" in it, and the drop down beside it
    showed the last half of its word.

    The widget's own sizeHint does not help for a line edit -- it is the
    same whatever the text says -- so the text itself is measured. For a
    drop down every entry is measured, not only the one showing: the
    column must not jump about when somebody picks another one.
    """
    import PySide6.QtWidgets as _qw
    want = w.sizeHint().width()
    letters = w.fontMetrics()
    if isinstance(w, _qw.QLineEdit):
        # Room for the frame and the caret beside the text.
        want = max(want, letters.horizontalAdvance(w.text()) + 26)
    elif isinstance(w, _qw.QComboBox):
        widest = max([letters.horizontalAdvance(w.itemText(i))
                      for i in range(w.count())] or [0])
        # And for the arrow, which sits inside the box.
        want = max(want, widest + 44)
    return want


def fix_table_width(t, weights=None, most_rows=0):
    """Stretch the table over the full width, as tall as its content.

    Every column first gets what its content needs. What is left over is
    distributed, the name column taking the largest share and the number
    columns growing with it. Putting all of it into the first column would
    look lopsided, with the numbers stuck to the right edge.

    *most_rows* is a lid: beyond that many rows the table scrolls
    itself rather than growing on. Without one a table as tall as its
    content is a table that pushes the whole sheet taller, one row at a
    time, and the sheet answers with a scroll bar of its own -- so the
    reader scrolls the sheet to reach a table that would have fitted.
    Zero means no lid, which is what a table that cannot grow wants.
    """
    import PySide6.QtCore as _qc
    import PySide6.QtWidgets as _qw
    t.resizeColumnsToContents()
    # Whether the lid bites is settled before the columns are shared
    # out: a vertical scroll bar takes room from the viewport, and
    # columns measured against a viewport that then loses a scroll bar
    # come out too wide by exactly that bar.
    capped = bool(most_rows) and t.rowCount() > most_rows
    t.setVerticalScrollBarPolicy(_qc.Qt.ScrollBarAsNeeded if capped
                                 else _qc.Qt.ScrollBarAlwaysOff)
    head = t.horizontalHeader()
    head.setStretchLastSection(False)
    n = t.columnCount()
    for i in range(n):
        head.setSectionResizeMode(i, _qw.QHeaderView.Interactive)
        # The column header sits where its content sits.
        title = t.horizontalHeaderItem(i)
        if title is not None:
            title.setTextAlignment(
                (_qc.Qt.AlignLeft if i == 0 else _qc.Qt.AlignRight)
                | _qc.Qt.AlignVCenter)
    content = []
    for i in range(n):
        want = t.columnWidth(i)
        for r in range(t.rowCount()):
            cell = t.cellWidget(r, i)
            if cell is not None:
                want = max(want, widget_width(cell))
        content.append(want + 14)
    shares = list(weights) if weights else [3] + [1] * (n - 1)

    def distribute_width():
        free = t.viewport().width() - sum(content)
        total_sum = float(sum(shares)) or 1.0
        rest = free
        for i in range(n):
            assigned = int(free * shares[i] / total_sum) if free > 0 else 0
            if i == n - 1:
                assigned = rest
            rest -= assigned
            t.setColumnWidth(i, content[i] + max(0, assigned))

    t._distribute = distribute_width

    class GrowWithWindow(_qc.QObject):
        """Redistribute the table when the window grows wider."""

        def eventFilter(self, watched, what):
            if what.type() == _qc.QEvent.Resize:
                t._distribute()
            return False

    if not hasattr(t, "_grow"):
        t._grow = GrowWithWindow(t)
        t.viewport().installEventFilter(t._grow)
    distribute_width()
    t.setMinimumWidth(0)
    shown = most_rows if capped else t.rowCount()
    height = head.height() + 4
    for i in range(shown):
        height += t.rowHeight(i)
    t.setFixedHeight(height)


def table_build(columns):
    """A table where the row is the file.

    Clicking the row brings it into view, so the whole row is selected
    rather than the single cell.
    """
    import PySide6.QtWidgets as _qw
    t = _qw.QTableWidget(0, len(columns))
    t.setHorizontalHeaderLabels(columns)
    t.verticalHeader().setVisible(False)
    t.setSelectionBehavior(_qw.QAbstractItemView.SelectRows)
    t.setSelectionMode(_qw.QAbstractItemView.SingleSelection)
    t.setEditTriggers(_qw.QAbstractItemView.NoEditTriggers)
    t.setShowGrid(False)
    t.setAlternatingRowColors(True)
    t.setSizePolicy(_qw.QSizePolicy.Expanding, _qw.QSizePolicy.Fixed)
    return t


def table_rows_fit(t, most=120):
    """Give a table rows as tall as their content, and no taller.

    The columns are measured before the rows, and that order is the
    whole point. A table wraps the text in a cell, so while the
    columns still stand at the width Qt hands out, a caption that does
    not fit is laid over two or three lines and the row is measured at
    that height. Widening the columns afterwards does not measure the
    row again -- it keeps the height it was given. Measured on
    24.8.2026 in the voices table: 45 px a row where the content needs
    28, three lines for a caption that fits on one.

    The rest shares the room between the tables: what fits in half of
    it needs no scroll bar, what does not scrolls itself.
    """
    import PySide6.QtCore as _qc
    import PySide6.QtWidgets as _qw
    t.resizeColumnsToContents()
    t.resizeRowsToContents()
    height = t.horizontalHeader().height() + 2 * t.frameWidth() + 2
    for i in range(t.rowCount()):
        height += t.rowHeight(i)
    t.setMinimumHeight(min(height, most))
    t.setVerticalScrollBarPolicy(_qc.Qt.ScrollBarAsNeeded)
    t.setSizePolicy(_qw.QSizePolicy.Expanding, _qw.QSizePolicy.Expanding)


def file_span(file_path, axis):
    """Return what this video file knows about its position in time.

    Three numbers travel together and are always wanted together: how
    long the file runs, what clock it was shot on, and where the
    measurement put it on the common axis.
    """
    try:
        info = video_facts(file_path)
    except Exception:
        return None
    fps = float(info.get("fps") or 30.0)
    tc = info.get("tc")
    try:
        tc0 = parse_timecode(tc, fps) if tc else None
    except Exception:
        tc0 = None
    return {"duration": float(info.get("duration") or 0.0), "fps": fps,
            "tc0": tc0,
            "axis": (axis or {}).get(path_key(file_path))}


def tree_build(columns):
    """The assignment as a tree: a recording, its voices under it.

    The same shape the file list on the first sheet already has, and
    the same thing said: what hangs under a file belongs to that file.
    A recording whose voices were told apart carries one row per voice;
    one where nobody was told apart carries none, and then the tree is
    a flat list with no special case anywhere.

    A view over a model rather than the QTreeWidget the file list uses,
    and for one reason: four places in the suite find the file list by
    asking the window for its first QTreeWidget. A second one of that
    class would answer instead, and the file list would be the one
    nobody could find any more. What is on the screen is the same tree
    either way.

    Not uniform row heights: the rows hold input fields and choosers,
    and a uniform tree gives every row the first row's height.
    """
    import PySide6.QtGui as _qg
    import PySide6.QtWidgets as _qw
    t = _qw.QTreeView()
    model = _qg.QStandardItemModel(0, len(columns))
    model.setHorizontalHeaderLabels(columns)
    # The view owns the model, so the rows go when the tree does and
    # anything still holding one is told rather than reading a corpse.
    model.setParent(t)
    t.setModel(model)
    t.setUniformRowHeights(False)
    t.setRootIsDecorated(True)
    t.setSelectionBehavior(_qw.QAbstractItemView.SelectRows)
    t.setSelectionMode(_qw.QAbstractItemView.SingleSelection)
    t.setEditTriggers(_qw.QAbstractItemView.NoEditTriggers)
    t.setAlternatingRowColors(True)
    t.setSizePolicy(_qw.QSizePolicy.Expanding, _qw.QSizePolicy.Expanding)
    return t


def tree_row(t, under, texts):
    """One row of the tree, at the top or under another; its cells back.

    A row is the list of its cells, one per column. The first of them
    is the row itself as far as the tree is concerned: children hang on
    it, and what the row knows is stored on it.

    As many cells as the tree has columns, whatever it was handed: a
    row with one cell too many would give the tree a column nobody
    asked for, and one too few would leave a hole.
    """
    import PySide6.QtGui as _qg
    wide = t.model().columnCount()
    texts = list(texts)[:wide] + [""] * max(0, wide - len(texts))
    cells = [_qg.QStandardItem(x) for x in texts]
    for cell in cells:
        cell.setEditable(False)
    if under is None:
        t.model().appendRow(cells)
    else:
        under[0].appendRow(cells)
    return cells


def tree_cell(row, column, text, colour=None):
    """Write one cell of a tree row, in a colour where it matters."""
    import PySide6.QtGui as _qg
    row[column].setText(text)
    if colour:
        row[column].setForeground(_qg.QBrush(_qg.QColor(colour)))
    return row


def tree_field(t, row, column, widget):
    """Put an input field or a chooser into one cell of a row."""
    t.setIndexWidget(row[column].index(), widget)
    return widget


def tree_row_of(t, where):
    """The row an index points at, as the list of its cells."""
    model = t.model()
    if where is None or not where.isValid():
        return None
    return [model.itemFromIndex(where.sibling(where.row(), c))
            for c in range(model.columnCount())]


def folded_summary(tree, row):
    """What a folded recording says in place of its voices.

    The cameras, because the cameras are what folding takes off the
    screen. It said how many voices there were until 2.10.1-beta, and
    that number stood twice in the same line: the Speakers column of
    that very row already reads "Separated: 4 speakers".

    A voice with no camera yet is counted on its own. It is the one
    thing still to be decided, and added in with the rest it would hide
    behind them.
    """
    seen, without = [], 0
    parent = row[0]
    for r in range(parent.rowCount()):
        kid = parent.child(r, 2)
        box = tree.indexWidget(kid.index()) if kid is not None else None
        pick = box.currentData() if box is not None else None
        if not pick or pick in (IGNORE_AUDIO, MIX_ONLY):
            without += 1
        elif pick not in seen:
            seen.append(pick)
    if not seen:
        return T('no camera yet')
    return (TN(len(seen), 'on %d camera', 'on %d cameras') % len(seen)
            + ((T(', %d without') % without) if without else ""))


def row_picker_for(tree):
    """A filter that makes the row a clicked field sits in the current one.

    Whoever is deciding which camera "Speaker 2" belongs to has to be
    able to hear Speaker 2 first, and a row that is picked already
    plays. So opening the camera list, or clicking into the name field,
    does exactly what clicking the row does -- and nothing more than
    that: there is no second way of playing anything here, and there
    should not be one.

    A filter and not a signal, because QComboBox has none for "the list
    is opening", and a subclass for it would be a class per tree.
    """
    from PySide6 import QtCore as _qc

    class Picker(_qc.QObject):
        def eventFilter(self, who, event):
            # The press and not the focus: the focus also arrives while
            # the sheet is being built, and the player would open a file
            # nobody asked for.
            if event.type() == _qc.QEvent.MouseButtonPress:
                where = tree.indexAt(who.mapTo(tree.viewport(),
                                               who.rect().center()))
                if where.isValid():
                    tree.setCurrentIndex(where)
                    # And straight back: making a row current moves the
                    # focus into the tree, and a name field that loses
                    # the focus on the click that entered it cannot be
                    # typed in at all.
                    who.setFocus(_qc.Qt.MouseFocusReason)
            return False

    return Picker(tree)


def row_picker_watch(picker, *widgets):
    """Watch these fields, and the line edit inside any of them.

    An editable combo box hands its clicks to the line edit it holds,
    and a filter on the box alone never sees them -- the camera chooser
    reacted and the name field beside it did not.
    """
    for widget in widgets:
        widget.installEventFilter(picker)
        inner = getattr(widget, "lineEdit", None)
        inner = inner() if callable(inner) else None
        if inner is not None:
            inner.installEventFilter(picker)


def tree_rows_fit(t, most=266):
    """Give the tree the height its open rows need, and no more.

    The counterpart of table_rows_fit, and the reason it cannot be
    that one: a tree has no rows to count, it has items, and how many
    of them are on the screen depends on what somebody expanded.
    viewportSizeHint answers exactly that -- Qt adds up the rows it
    would draw -- and it answers before the widget is ever shown,
    which is when this runs.

    The columns are left alone, unlike in a table: this runs again
    every time somebody opens or closes a row, and a column that
    re-measured itself on every click would make the tree jump about
    under the hand that is using it.
    """
    import PySide6.QtCore as _qc
    import PySide6.QtWidgets as _qw
    height = (t.viewportSizeHint().height() + t.header().height()
              + 2 * t.frameWidth() + 2)
    t.setMinimumHeight(min(height, most))
    t.setVerticalScrollBarPolicy(_qc.Qt.ScrollBarAsNeeded)
    t.setSizePolicy(_qw.QSizePolicy.Expanding, _qw.QSizePolicy.Expanding)


# The same nine point font runs about twice as wide on Windows as it
# does on macOS -- 1.89 times, measured on GitHub's runners over both
# languages on 24.8.2026, with 62 captions standing cut off in fields
# sized for the Mac, the worst of them by 136 px. Linux lies between
# the two and misses by 9 px in one spot. So the fields grow on
# Windows and nowhere else: the Mac layout is the one the manual's
# pictures show, and the one where four cut buttons and a checkbox
# were already weighed against a row 480 px wide.
WIDE_FONT = sys.platform == "win32"


def caption_room(widget, base, captions=()):
    """How wide a field has to be, and never narrower than designed.

    Measured in the font that is drawing rather than added as a
    constant: a surcharge in pixels fits one font and misses the next.
    A widget already carrying its text is asked for its own size hint,
    which counts the frame its style draws around it. Where several
    fields share one width every caption is handed in, because the
    widest of them decides; one average character is left as air.

    Measured on every system, not on Windows alone. It never returns
    less than the designed width, so where the design already fits
    nothing moves: measured on 25.8.2026, not one of the 150 captions
    on this machine wants more than its base. Windows was where it was
    needed first, at 1.89 times the width for the same nominal font,
    but the fixed numbers left "+10 s" 9 px short on Linux and the
    tests red at every push since the CI was set up. Sans Serif 9.0 is
    not the same font file on two systems.
    """
    metrics = widget.fontMetrics()
    want = widget.sizeHint().width()
    for caption in captions:
        want = max(want, metrics.horizontalAdvance(caption)
                   + metrics.averageCharWidth())
    return max(base, want)


def cut_caption_room(widget, base):
    """Width of the caption column beside the camera cut numbers.

    All the rows share it, so all the captions are measured: a column
    as wide as its own caption would leave the fields beside it
    ragged.
    """
    return caption_room(widget, base, [T(f[1]) for f in CUT_FIELDS]
                        + [T(c[1]) for c in CUT_CHOICES])


def cut_choice_room(widget, base):
    """Width of the drop-downs beside the camera cut captions.

    All the rows share it, so every entry any of them offers is
    measured: a box as wide as its own longest entry leaves the column
    ragged, and the widest entry anywhere decides.
    """
    return caption_room(widget, base,
                        [T(SHOT_NAMES.get(n, n))
                         for c in CUT_CHOICES for n in c[3]])


def box_room(box, base):
    """Fix a box at its designed width, and at what fits in it.

    Only the finished box knows how much room it wants, so it watches
    its own layout and is let out when what it carries has grown -- on
    every system, not on Windows alone. A missing font family is
    replaced by a wider one anywhere: measured on 2.9.2026, the
    player's line wants 519 px here, about 590 in a substitute 12 %
    wider, against a box fixed at 580.
    """
    box.setFixedWidth(base)
    from PySide6 import QtCore

    class BoxWatch(QtCore.QObject):
        def eventFilter(self, which, event):
            if event.type() == QtCore.QEvent.LayoutRequest:
                box_grown(which)
            return False

    box.installEventFilter(BoxWatch(box))
    return box


def box_grown(box):
    """Let a box out to the width the things inside it need."""
    layout = box.layout()
    if layout is None:
        return
    want = layout.totalMinimumSize().width()
    if want > box.width():
        box.setFixedWidth(want)


def make_drop_area(QtCore, QtGui, QtWidgets):
    """The area files are dragged onto while the list is empty.

    Once something is in the list it disappears -- the list is then the
    drop area itself.
    """

    class DropArea(QtWidgets.QFrame):

        def __init__(self, drop, pick, project, colours):
            QtWidgets.QFrame.__init__(self)
            self.drop = drop
            self.colours = colours
            self.setAcceptDrops(True)
            self.setFrameShape(QtWidgets.QFrame.StyledPanel)
            # With a name, so the dashed border runs around the area only and
            # not around every label inside it.
            self.setObjectName("droparea")
            position = QtWidgets.QVBoxLayout(self)
            position.setAlignment(QtCore.Qt.AlignCenter)
            position.setSpacing(10)
            large = QtWidgets.QLabel(T('Drag audio and video files here'))
            s = large.font()
            s.setPointSize(max(13, s.pointSize() + 4))
            s.setBold(True)
            large.setFont(s)
            large.setAlignment(QtCore.Qt.AlignCenter)
            position.addWidget(large)
            small = QtWidgets.QLabel(
                T('The audio recording of every speaker, plus the '
                  'cameras.\nThe order does not matter -- the program '
                  'recognises what is what.\nFor a multi-part recording the '
                  'first block is enough.'))
            small.setAlignment(QtCore.Qt.AlignCenter)
            small.setStyleSheet("color: %s;" % colours["quiet"])
            position.addWidget(small)
            button = QtWidgets.QPushButton(T('... or add files ...'))
            button.setFixedWidth(220)
            button.clicked.connect(lambda: pick())
            # Opening an earlier project only works here, at the start --
            # once files are in the list it would overwrite them.
            button2 = QtWidgets.QPushButton(T('Open project ...'))
            button2.setFixedWidth(220)
            button2.clicked.connect(lambda: project())
            row = QtWidgets.QHBoxLayout()
            row.addStretch(1)
            row.addWidget(button)
            row.addWidget(button2)
            row.addStretch(1)
            position.addLayout(row)
            self._paint(False)

        def _paint(self, active):
            """Draw a dashed border, solid while dragged over."""
            self.setStyleSheet(
                "QFrame#droparea { border: 2px dashed %s; "
                "border-radius: 10px; background: %s; }"
                % ((self.colours["heading"], self.colours["box"]) if active
                   else (self.colours["frame"], "transparent")))

        def dragEnterEvent(self, e):
            if e.mimeData().hasUrls():
                e.acceptProposedAction()
                self._paint(True)

        def dragLeaveEvent(self, e):
            self._paint(False)

        def dropEvent(self, e):
            self._paint(False)
            paths = [u.toLocalFile() for u in e.mimeData().urls()
                     if u.isLocalFile()]
            if paths:
                e.acceptProposedAction()
                self.drop(paths)

    return DropArea


def qt_cut_band(QtCore, QtGui, QtWidgets, Qt):
    """A band showing the computed camera cut.

    One bar per shot in the colour of its camera -- the same colour the
    clips will carry in Resolve. That shows the rhythm without rendering
    anything: where one camera holds for a long time, where it stutters,
    where the wide shot steps in.
    """

    class CutBand(QtWidgets.QWidget):

        selected = QtCore.Signal(float)
        zoomed = QtCore.Signal()

        # Below this the band would show less than a syllable.
        SHORTEST = 1.0

        def __init__(self, parent=None):
            QtWidgets.QWidget.__init__(self, parent)
            self.cut = []
            self.colours = {}
            self.length = 0.0
            self.spot = None
            # The stretch of time on show, or None for all of it.
            self.view = None
            self.setMinimumHeight(24)
            self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Fixed)
            self.setMouseTracking(True)
            self.setFocusPolicy(Qt.StrongFocus)

        def set(self, cut, colours, length):
            self.cut = list(cut or [])
            self.colours = dict(colours or {})
            self.length = float(length or 0.0) or (
                max((b for _a, b, _w in self.cut), default=0.0))
            self.view = None
            self.update()
            # The whole length is on show again, and it is a different
            # length from the one before. The reading beside the band
            # hangs on this signal, so it follows new material without
            # anybody having to zoom first.
            self.zoomed.emit()

        # -- What is on show -------------------------------------------
        def window(self):
            """The stretch of time the band is showing, as (from, to)."""
            if not self.view or self.length <= 0:
                return 0.0, self.length
            return max(0.0, self.view[0]), min(self.length, self.view[1])

        def zoom(self, factor, around=None):
            """Show half as much, or twice as much, around one point.

            Around the position by default: zooming in is done to look
            at where one is, and a magnifier that jumps somewhere else
            has to be dragged back every time.
            """
            if self.length <= 0:
                return
            a, b = self.window()
            span = min(self.length, max(self.SHORTEST, (b - a) * factor))
            middle = around
            if middle is None:
                middle = self.spot if self.spot is not None else (a + b) / 2.0
            middle = max(0.0, min(self.length, middle))
            a = max(0.0, min(self.length - span, middle - span / 2.0))
            self.view = None if span >= self.length else (a, a + span)
            self.update()
            self.zoomed.emit()

        def zoom_all(self):
            """Back to the whole length."""
            self.view = None
            self.update()
            self.zoomed.emit()

        def zoom_text(self):
            """What is on show, for a label beside the band.

            Without the milliseconds as_hms carries: this says which
            stretch is on screen, not where a cut sits. Unzoomed that
            is the whole material, and with no material yet it is zero
            to zero. It is never empty: a hole beside the zoom buttons
            says nothing about what the third one restores.
            """
            a, b = self.window()

            def clock(t):
                t = int(round(t))
                return "%d:%02d:%02d" % (t // 3600, t % 3600 // 60, t % 60)

            return "%s -- %s" % (clock(a), clock(b))

        def label_set(self, seconds):
            self.spot = seconds
            # The view follows the position rather than being left
            # behind: zoomed in, playing would otherwise run out of the
            # picture within seconds.
            if self.view is not None and seconds is not None:
                a, b = self.window()
                span = b - a
                if seconds < a or seconds > b:
                    a = max(0.0, min(self.length - span,
                                     seconds - span / 2.0))
                    self.view = (a, a + span)
            self.update()

        def _time(self, x):
            a, b = self.window()
            if b - a <= 0 or self.width() <= 0:
                return None
            return max(a, min(b, a + (b - a) * x / float(self.width())))

        def _x(self, t):
            a, b = self.window()
            if b - a <= 0:
                return 0
            return int(self.width() * (t - a) / (b - a))

        def wheelEvent(self, e):
            step = e.angleDelta().y()
            if not step:
                return
            self.zoom(0.5 if step > 0 else 2.0,
                      self._time(e.position().x()))
            e.accept()

        def keyPressEvent(self, e):
            if e.key() in (Qt.Key_Plus, Qt.Key_Equal):
                self.zoom(0.5)
            elif e.key() == Qt.Key_Minus:
                self.zoom(2.0)
            elif e.key() in (Qt.Key_0, Qt.Key_Home):
                self.zoom_all()
            else:
                QtWidgets.QWidget.keyPressEvent(self, e)

        def mousePressEvent(self, e):
            t = self._time(e.position().x())
            if t is not None:
                self.selected.emit(t)

        def mouseMoveEvent(self, e):
            t = self._time(e.position().x())
            if t is None:
                return
            for a, b, who in self.cut:
                if a <= t < b:
                    self.setToolTip(T('%s -- %d:%02d to %d:%02d (%.1f s)')
                                    % (who, int(a) // 60, int(a) % 60,
                                       int(b) // 60, int(b) % 60, b - a))
                    return
            self.setToolTip("")

        def paintEvent(self, _e):
            painter = QtGui.QPainter(self)
            width, height = self.width(), self.height()
            painter.fillRect(0, 0, width, height, QtGui.QColor("#20242a"))
            if self.length <= 0 or not self.cut:
                return
            begins, ends = self.window()
            for a, b, who in self.cut:
                if b <= begins or a >= ends:
                    continue
                x0 = self._x(max(a, begins))
                x1 = max(x0 + 1, self._x(min(b, ends)))
                painter.fillRect(x0, 0, x1 - x0, height,
                               QtGui.QColor(self.colours.get(who, "#888888")))
            # A scale, or the band is a coloured stripe without meaning.
            # The step follows what is on show: minutes over the whole
            # thing, seconds once zoomed in far enough.
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 90)))
            span = ends - begins
            step = 1.0
            for candidate in (1.0, 2.0, 5.0, 10.0, 15.0, 30.0, 60.0, 120.0,
                              300.0, 600.0, 1800.0, 3600.0):
                step = candidate
                if span / candidate <= 40:
                    break
            t = step * math.ceil(begins / step)
            while t < ends:
                x = self._x(t)
                painter.drawLine(x, 0, x, height)
                t += step
            if self.spot is not None and begins <= self.spot <= ends:
                painter.setPen(QtGui.QPen(QtGui.QColor("#ffffff"), 2))
                x = self._x(self.spot)
                painter.drawLine(x, 0, x, height)
            painter.end()

    return CutBand


SILENT_PLAYER = bool(os.environ.get("VPM_SILENT"))


def loud(value):
    """The volume to set: nothing at all where VPM_SILENT is set.

    The suite plays real files, and a machine that beeps its way through
    a run is no use to anybody working beside it. Volume and mute are
    all the switch touches, so where the playhead lands -- what the
    tests measure -- is untouched.
    """
    return 0.0 if SILENT_PLAYER else value


def hushed(on):
    """Whether to mute: always where VPM_SILENT is set."""
    return True if SILENT_PLAYER else on


def audio_sink(QtMultimedia, parent):
    """A player's audio output, silent from the start where asked.

    Full and not four fifths. Measured on 24.8.2026: Qt takes nothing
    above 1.0 -- setVolume(1.5) reads back as 1.0 and no change is
    signalled -- so 0.8 was giving away 1.94 dB against a ceiling that
    cannot be raised. On a recording that sits 18 dB below the
    delivery target, that is 1.94 dB nobody had to lose.
    """
    out = QtMultimedia.QAudioOutput(parent)
    out.setVolume(loud(1.0))
    out.setMuted(hushed(False))
    return out


def readable_on(colour):
    """Black or white, whichever can be read on *colour*.

    The threshold is where the two contrasts meet: sRGB luminance
    0.179 by WCAG 2.1, so a middling colour still takes black.
    """
    digits = str(colour or "").lstrip("#")
    if len(digits) != 6 or any(c not in "0123456789abcdefABCDEF"
                               for c in digits):
        return "#ffffff"
    parts = []
    for i in (0, 2, 4):
        v = int(digits[i:i + 2], 16) / 255.0
        parts.append(v / 12.92 if v <= 0.04045
                     else ((v + 0.055) / 1.055) ** 2.4)
    light = 0.2126 * parts[0] + 0.7152 * parts[1] + 0.0722 * parts[2]
    return "#000000" if light > 0.179 else "#ffffff"


def speakers_at(sections_per_name, t):
    """Who is speaking at programme time *t*, in the order handed in.

    Several at once are all of them: two people talking over each
    other are two names, and picking one would answer a question
    nobody asked. Nobody speaking is an empty list, which is an
    answer too.
    """
    return [name for name, spans in (sections_per_name or ())
            if any(a <= t < b for a, b in spans)]


# How long a name stands before another may take its place. A voice
# that interjects for a moment would flash past unread otherwise; the
# price is that the name lags the sound by up to this much.
NAME_HOLD_S = 0.5


class NameHold(object):
    """Keep a name up long enough to be read.

    Display only. What comes out of here never travels back into the
    cut: the picture switches where the cut says, whatever name is
    still standing. Time is programme time, so the same run of a
    programme gives the same names every time.
    """

    def __init__(self, at_least=NAME_HOLD_S):
        self.at_least = float(at_least)
        self.shown = None
        self.since = None

    def forget(self):
        """Drop what stands, so the next answer arrives at once."""
        self.shown, self.since = None, None

    def at(self, names, t):
        """What to show at programme time *t*, given *names* are true."""
        fresh = tuple(names or ())
        if self.shown is None:
            self.shown, self.since = fresh, float(t)
        elif fresh != self.shown:
            # A jump backwards is not waiting, it is a new place.
            waited = float(t) - self.since
            if waited < 0.0 or waited >= self.at_least:
                self.shown, self.since = fresh, float(t)
        return self.shown


def qt_cut_player(QtCore, QtGui, QtWidgets, Qt, QtMultimedia,
                      QtMultimediaWidgets, label, hint, COLOURS):
    """Play the computed cut without rendering anything.

    Two video surfaces sit on top of each other: one shows, the other is
    already loading the next shot and starts shortly before. At the cut it
    only switches over, which costs no frame. The audio comes from one file
    throughout so nothing jumps at the cuts.

    Seeking is a request in Qt, not a command: before loading, before the
    first frame and in mid-playback, setPosition is silently discarded.
    Every seek therefore goes through a Seeker that checks whether it
    actually took and retries if not.
    """

    # The box the pictures sit in. It is also what a stretch with no
    # shot of its own is drawn in: no shot, no colour to show.
    BACKDROP = "#101418"

    # How close the player has to be for a position to count as reached.
    HIT_MS = 350
    # How long to keep retrying before giving up on a position.
    PATIENCE_MS = 5000
    # How much time lies between two attempts.
    SPACING_MS = 120

    VERBOSE = bool(os.environ.get("VPM_PLAYER_DEBUG"))

    MEDIA_STATES = {}
    for _n in ("NoMedia", "LoadingMedia", "LoadedMedia", "StalledMedia",
               "BufferingMedia", "BufferedMedia", "EndOfMedia",
               "InvalidMedia"):
        _w = getattr(QtMultimedia.QMediaPlayer, _n, None)
        if _w is not None:
            MEDIA_STATES[_w] = _n
    PLAY_STATES = {}
    for _n in ("StoppedState", "PlayingState", "PausedState"):
        _w = getattr(QtMultimedia.QMediaPlayer, _n, None)
        if _w is not None:
            PLAY_STATES[_w] = _n[:-5]

    def _sec(ms):
        """Format milliseconds readably, always with the true sign."""
        try:
            return "%.2f s" % (ms / 1000.0)
        except Exception:
            return str(ms)

    def _position(p):
        """Report how one player is doing."""
        return "%s/%s%s" % (PLAY_STATES.get(p.playbackState(), "?"),
                            MEDIA_STATES.get(p.mediaStatus(), "?"),
                            "" if p.isSeekable() else T('/not seekable'))

    class Seeker(object):
        """Seek to a position and keep checking until it actually holds."""

        def __init__(self, player, name):
            self.p, self.name = player, name
            self.want = None
            self.attempts = 0
            self.total = QtCore.QElapsedTimer()
            self.last_percent = QtCore.QElapsedTimer()

        def pending(self):
            return self.want is not None

        def forget(self):
            self.want = None

        def seek_to(self, ms, reason=""):
            ms = max(0, int(ms))
            self.want = ms
            self.attempts = 0
            self.total.restart()
            self.last_percent.restart()
            _say(T('%s: should go to %s%s -- %s')
                   % (self.name, _sec(ms), (" (%s)" % reason) if reason else "",
                      _position(self.p)))
            self._set()

        def _set(self):
            if not self.p.isSeekable():
                if self.attempts == 0:
                    _say(T('%s: not seekable yet, will follow (%s)')
                           % (self.name, _position(self.p)))
                return
            self.attempts += 1
            self.p.setPosition(self.want)
            _say(T('%s: setPosition(%s), attempt %d, then at %s')
                   % (self.name, _sec(self.want), self.attempts,
                      _sec(self.p.position())))

        def check(self):
            """Report True once the position holds, or has been given up on."""
            if self.want is None:
                return True
            have = self.p.position()
            if abs(have - self.want) <= HIT_MS:
                _say(TN(self.attempts,
                         '%s: sits at %s (target %s) after %d ms, %d attempt',
                         '%s: sits at %s (target %s) after %d ms, %d attempts')
                       % (self.name, _sec(have), _sec(self.want),
                          self.total.elapsed(), self.attempts))
                self.want = None
                return True
            if self.total.elapsed() > PATIENCE_MS:
                print(T('  Player: %s stays at %s instead of %s -- given '
                        'up after %d attempts (%s)')
                      % (self.name, _sec(have), _sec(self.want),
                         self.attempts, _position(self.p)))
                self.want = None
                return True
            if self.last_percent.elapsed() >= SPACING_MS:
                self.last_percent.restart()
                self._set()
            return False

    def _say(text):
        if VERBOSE:
            print(T('  Player: %s') % text)

    class ShotNote(QtWidgets.QWidget):
        """Who speaks and which camera runs, in the shot's colour.

        One display for both cases, and only its height differs: under
        a picture it is a strip as high as its two lines, without one
        it covers the whole area. The colour is opaque either way -- a
        video surface cannot be written on through, and text on an
        unknown picture cannot be read.
        """

        def __init__(self, parent=None):
            QtWidgets.QWidget.__init__(self, parent)
            self.setAttribute(Qt.WA_TransparentForMouseEvents)
            self.colour = BACKDROP
            self.camera = ""
            self.speaking = ""
            self.strong = QtGui.QFont(self.font())
            self.strong.setBold(True)

        def line_room(self):
            """How high the two lines and the air round them are."""
            return 2 * QtGui.QFontMetrics(self.strong).height() + 8

        def show_shot(self, colour, camera, speaking):
            """Take what to show, and repaint only where it changed."""
            fresh = (colour, camera, speaking)
            if fresh == (self.colour, self.camera, self.speaking):
                return
            self.colour, self.camera, self.speaking = fresh
            self.update()

        def _fits(self, text, width, metrics):
            """The camera name, cut at the front where it is too wide.

            What tells two cameras apart sits at the end of these names,
            in the take and the camera number, so the front is what
            goes. Qt's own single ellipsis marks where.
            """
            return metrics.elidedText(text, Qt.ElideLeft, width)

        def paintEvent(self, _event):
            painter = QtGui.QPainter(self)
            painter.fillRect(self.rect(), QtGui.QColor(self.colour))
            painter.setPen(QtGui.QColor(readable_on(self.colour)))
            room = self.rect().adjusted(6, 0, -6, 0)
            bold = QtGui.QFontMetrics(self.strong)
            high = bold.height()
            # The two lines stand in the middle of whatever they are
            # given, across and down. Both cases then read the same,
            # and a strip cut to their height needs no second rule.
            top = room.top() + max(0, (room.height() - 2 * high) // 2)
            # The camera on top, who is speaking underneath. The
            # colour field then reads like the band below it, which is
            # a band of camera shots -- and one camera can carry
            # several speakers, which is what the second line is for.
            painter.setFont(self.strong)
            painter.drawText(
                QtCore.QRect(room.left(), top, room.width(), high),
                Qt.AlignHCenter | Qt.AlignVCenter,
                self._fits(self.camera, room.width(), bold))
            painter.setFont(self.font())
            painter.drawText(
                QtCore.QRect(room.left(), top + high, room.width(), high),
                Qt.AlignHCenter | Qt.AlignVCenter,
                QtGui.QFontMetrics(self.font()).elidedText(
                    self.speaking, Qt.ElideRight, room.width()))
            painter.end()

    class CutPlayer(QtWidgets.QWidget):

        position_changed = QtCore.Signal(float)

        # How long before the cut the next surface starts running.
        LEAD_IN = 1.0

        # How thick the shot's colour lies round the picture. A hairline
        # round a moving picture is not caught out of the corner of the
        # eye, which is the only place this is ever looked at.
        FRAME = 6

        # Air under the note, in the box's own colour. Two coloured
        # areas touching are read as one, and the cut band is next.
        GAP = 8

        # The shape of the picture before one has been measured. Every
        # camera here has been 16:9 so far, and it is what the box was.
        SHAPE = 16.0 / 9.0

        def __init__(self, parent=None):
            QtWidgets.QWidget.__init__(self, parent)
            position = QtWidgets.QVBoxLayout(self)
            position.setContentsMargins(0, 0, 0, 0)
            position.setSpacing(6)
            # The box the picture and the note share. It keeps the size
            # the picture alone used to have: what the picture gives up
            # by taking its own shape stays inside the box and does not
            # move the window.
            self.box = QtWidgets.QWidget()
            self.box.setMinimumHeight(302)
            self.box.setMinimumWidth(320)
            self.box.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                    QtWidgets.QSizePolicy.Expanding)
            self.box.setStyleSheet("background: %s;" % BACKDROP)
            self.shape = self.SHAPE
            self.stack = QtWidgets.QStackedWidget(self.box)
            self.stack.setMinimumSize(1, 1)
            self._frame = None
            self._blank = True
            self._frame_show(BACKDROP)
            self.surfaces, self.videos = [], []
            for _ in (0, 1):
                f = QtMultimediaWidgets.QVideoWidget()
                # Without this the width follows the picture currently loaded,
                # and the whole window jumps on switching.
                f.setSizePolicy(QtWidgets.QSizePolicy.Ignored,
                                QtWidgets.QSizePolicy.Ignored)
                f.setMinimumSize(1, 1)
                p = QtMultimedia.QMediaPlayer(self)
                p.setVideoOutput(f)
                self.stack.addWidget(f)
                # Make the window for the picture now, while no player
                # has a file yet. Made later -- the first time somebody
                # opens this tab -- it is made while the players are
                # starting up, and then two threads reach for the same
                # lock inside Qt. Measured 28.8.2026 on the gate test,
                # which builds six windows at once: without this, half
                # the runs stood in QWidget::createWinId and never came
                # back.
                f.winId()
                self.surfaces.append(f)
                self.videos.append(p)
            # The note last, so Qt puts it over the picture.
            self.note = ShotNote(self.box)
            self.note.hide()
            self.box.installEventFilter(self)
            self.hold = NameHold()
            # Only now: what answers this signal lays the note out, and
            # a signal is connected when everything it touches exists,
            # never earlier. Qt decides on its own when it delivers.
            for f in self.surfaces:
                f.videoSink().videoSizeChanged.connect(
                    lambda _s=None, w=f: self._shape_seen(
                        w.videoSink().videoSize()))
            position.addWidget(self.box, 1)
            self.seekers = [Seeker(self.videos[0], T('Video 1')),
                          Seeker(self.videos[1], T('Video 2'))]
            self.videos[0].mediaStatusChanged.connect(
                lambda st: self._reported(T('Video 1'), st))
            self.videos[1].mediaStatusChanged.connect(
                lambda st: self._reported(T('Video 2'), st))
            self.audio_out = audio_sink(QtMultimedia, self)
            self.audio = QtMultimedia.QMediaPlayer(self)
            self.audio.setAudioOutput(self.audio_out)
            self.audio_seek = Seeker(self.audio, T('Audio'))
            self.audio.mediaStatusChanged.connect(
                lambda st: self._reported(T('Audio'), st))
            # What goes wrong belongs on the console, debug mode or not.
            for name, player in ((T('Audio'), self.audio), (T('Video 1'), self.videos[0]),
                                  (T('Video 2'), self.videos[1])):
                player.errorOccurred.connect(
                    lambda _f, txt, n=name:
                    print(T('  Player: %s reports an error -- %s')
                          % (n, txt)))
            # When the output device changes -- headphones in, headphones out
            # -- the old QAudioOutput keeps playing into nothing: the display
            # runs, nothing is heard. So follow the new device.
            try:
                self.devices = QtMultimedia.QMediaDevices(self)
                self.devices.audioOutputsChanged.connect(self._follow_device)
            except Exception:
                self.devices = None
            # The rail runs from In point to Out point: there is nothing to see
            # beyond, so it cannot be dragged beyond either.
            self.rail = QtWidgets.QSlider(Qt.Horizontal)
            self.rail.setRange(0, 1000)
            self.rail.sliderMoved.connect(self._dragged)
            position.addWidget(hint(self.rail, T('Drag to move the position.')))
            self.position = position
            digits = digits_font(QtGui, self)
            # One line: In point on the left, Out point on the right,
            # where we are in the middle. The length is already in the
            # heading, and the camera stands in the picture itself.
            line = QtWidgets.QHBoxLayout()
            position.addLayout(line)
            self.left_label = label("", COLOURS["value"], True)
            self.right_label = label("", COLOURS["value"], True)
            self.spot_label = label("", COLOURS["heading"], True)
            for m in (self.left_label, self.right_label, self.spot_label):
                m.setFont(QtGui.QFont(digits))
            line.addWidget(self.left_label)
            line.addStretch(1)
            line.addWidget(self.spot_label)
            line.addStretch(1)
            line.addWidget(self.right_label)
            status = QtWidgets.QHBoxLayout()
            position.addLayout(status)
            status.addStretch(1)
            # For fault finding: what the three players report by themselves.
            small = QtGui.QFont(digits)
            small.setPointSize(max(6, digits.pointSize() - 4))
            self.readouts = label("", COLOURS["quiet"])
            self.readouts.setFont(small)
            # Only while something runs. With the player stopped the line is
            # just one line less picture.
            self.readouts.setVisible(False)
            status.addWidget(self.readouts)
            bar = QtWidgets.QHBoxLayout()
            position.addLayout(bar)

            # All the same height: buttons with an icon and buttons with text
            # compute different heights otherwise. And all icons the same size:
            # the system icons come in different sizes and look lopsided side
            # by side.
            HEIGHT = 30
            SYMBOL = QtCore.QSize(18, 18)

            def wide(widget):
                widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                QtWidgets.QSizePolicy.Fixed)
                widget.setFixedHeight(HEIGHT)
                return widget

            def icon(name):
                return self.style().standardIcon(
                    getattr(QtWidgets.QStyle, name))

            def button(name, text, on_click):
                button = QtWidgets.QToolButton()
                button.setIcon(icon(name))
                button.setIconSize(SYMBOL)
                button.setAutoRaise(True)
                button.clicked.connect(on_click)
                bar.addWidget(hint(wide(button), text), 1)
                return button

            def step(text, tooltip_text, seconds):
                button = QtWidgets.QToolButton()
                button.setText(text)
                button.setAutoRaise(True)
                button.setMinimumWidth(caption_room(button, 42))
                button.clicked.connect(lambda _=False, x=seconds: self.nudge(x))
                bar.addWidget(hint(wide(button), tooltip_text), 1)
                return button

            button("SP_MediaSkipBackward", T('To the In point.'),
                  lambda: self.jump(self.begins))
            step("-10 s", T('Ten seconds back.'), -10.0)
            step("-1 s", T('One second back.'), -1.0)
            step("-1 F", T('One frame back.'), -1.0 / 30.0)
            self.button = button("SP_MediaPlay", T('Play and pause.'),
                               self.toggle)
            step("+1 F", T('One frame forward.'), 1.0 / 30.0)
            step("+1 s", T('One second forward.'), 1.0)
            step("+10 s", T('Ten seconds forward.'), 10.0)
            # At the end of the transport, where the steps forward end
            # -- the same place and the same button as on the preview.
            self.fast_button = button("SP_MediaSeekForward",
                                      T('Play forward, twice as fast on '
                                        'every press -- the L key.'),
                                      self.faster)
            self.mute_button = button("SP_MediaVolume", T('Mute.'),
                                     self.toggle_mute)
            self.loud = QtWidgets.QSlider(Qt.Horizontal)
            self.loud.setRange(0, 100)
            self.loud.setValue(100)
            self.loud.setMinimumWidth(72)
            self.loud.valueChanged.connect(
                lambda v: self.audio_out.setVolume(loud(v / 100.0)))
            bar.addWidget(hint(wide(self.loud),
                               T('Volume. 100 is as loud as it goes -- '
                                 'Qt takes nothing above that.')), 2)
            self.audio_out.setVolume(loud(1.0))
            self._muted = False
            # Fast forward doubles from here. Only forwards, for the
            # reason the preview player gives at its own rate.
            self._speed = 1.0
            self.clock = QtCore.QTimer(self)
            self.clock.setInterval(40)
            self.clock.timeout.connect(self._tick)
            # Programme time runs on a clock of its own. Hanging it off the
            # audio position would mean stopping as soon as the player dislikes
            # a file.
            self.stopwatch = QtCore.QElapsedTimer()
            self.base = 0.0
            self._t = 0.0
            self._playing = False      # what the button says
            self._seeking = False       # a seek is in progress
            self.cut, self.files, self.offset = [], {}, {}
            self.begins, self.until = 0.0, 0.0
            self.audio_offset = 0.0
            self.tc0 = None                   # wall clock when it started
            self.now = None                 # which shot is running
            self.loaded = [None, None]       # which one in which pane
            self.colours, self.wides = {}, set()
            self.speaking = []            # who speaks when, for the note

        def eventFilter(self, who, event):
            """Lay the box out again whenever the box changes size."""
            if who is self.box and event.type() == QtCore.QEvent.Resize:
                self._note_place()
            return QtWidgets.QWidget.eventFilter(self, who, event)

        def _shape_seen(self, size):
            """Take a picture's shape, if it is wider than what is set.

            Only wider, and never back: cutting between two cameras of
            different format would move the whole player every few
            seconds, which is worse than a strip beside the narrower
            one. So the box ends up as wide as the widest camera, and
            no picture ever gets a band over and under it.
            """
            if size.height() <= 0 or size.width() <= 0:
                return
            shape = size.width() / float(size.height())
            if shape <= self.shape + 0.001:
                return
            self.shape = shape
            self._note_place()

        def _frame_show(self, colour):
            """Lay the shot's colour round the picture."""
            if colour == self._frame:
                return
            self._frame = colour
            self.stack.setStyleSheet(
                "background: %s; border: %dpx solid %s;"
                % (BACKDROP, self.FRAME, colour))

        def _note_place(self):
            """Fit the picture to its shape and put the note under it.

            The picture keeps the size it had at most, never more, and
            the note under it is as high as its two lines. Whatever
            stays free below falls to the box's own colour, so the
            strip reads as a caption to the picture. A strip of that
            colour stays free at the foot in any case, or the note and
            the cut band under it read as one thing.
            """
            wide, high = self.box.width(), self.box.height() - self.GAP
            lines = self.note.line_room()
            room = max(1, high - lines - 2 * self.FRAME)
            seen = max(1, min(room, int((wide - 2 * self.FRAME)
                                        / self.shape)))
            across = min(wide, int(seen * self.shape) + 2 * self.FRAME)
            self.stack.setGeometry((wide - across) // 2, 0, across,
                                   seen + 2 * self.FRAME)
            # As wide as the framed picture, so frame and note read as
            # one block rather than as a band laid under a picture.
            # Without a picture there is nothing to caption and nothing
            # to sit under, so there the colour keeps the whole box.
            over = 0 if self._blank else self.stack.height()
            deep = high if self._blank else min(lines, high - over)
            self.note.setGeometry(self.stack.x(), over,
                                  self.stack.width(), max(1, deep))
            self.note.raise_()

        def _note_show(self, t, j):
            """Say who speaks and which camera runs at programme time *t*.

            Reading only: the hold below moves nothing but this note,
            and *j* comes from the cut as it was handed over.
            """
            who = self.cut[j][2] if j is not None else None
            colour = self.colours.get(who) or BACKDROP
            # Never an empty line: a blank reads as a fault, a sentence
            # says that nobody is speaking. The mark for the wide shot
            # stands beside the name, never in its place -- the wide
            # shot is a choice of camera, not a silence.
            said = "  ".join(self.hold.at(speakers_at(self.speaking, t), t))
            said = said or T('No speaker')
            if who in self.wides:
                said = "%s %s" % (said, T('(wide shot)'))
            self._frame_show(colour)
            self.note.show_shot(colour, who or "", said)
            blank = who is None or who not in self.files
            self.note.setVisible(bool(self.cut))
            if blank != self._blank:
                self._blank = blank
                self._note_place()

        def _reported(self, name, status):
            _say(T('%s reports %s')
                   % (name, MEDIA_STATES.get(status, str(status))))

        def _follow_device(self):
            """Follow the audio output device after it has changed."""
            try:
                fresh = QtMultimedia.QMediaDevices.defaultAudioOutput()
            except Exception:
                return
            if fresh is None or fresh == self.audio_out.device():
                return
            print(T('  Player: audio output switches to %s')
                  % (fresh.description() or T('the default device')))
            spot, was_running = self.audio.position(), self.is_running()
            self.audio_out.setDevice(fresh)
            self.audio_seek.seek_to(spot, T('after the device change'))
            if was_running:
                try:
                    self.audio.play()
                except Exception:
                    pass

        def replace_rail(self, widget):
            """Replace the rail with something better.

            The cut band shows more in the same place than a grey line.
            """
            i = self.position.indexOf(self.rail)
            self.rail.setParent(None)
            self.rail = None
            self.position.insertWidget(max(0, i), widget)

        # -- Controls ---------------------------------------------------
        def nudge(self, seconds):
            self.jump(self._time() + seconds)

        def toggle_mute(self):
            self._muted = not self._muted
            self.audio_out.setMuted(hushed(self._muted))
            self.mute_button.setIcon(self.style().standardIcon(
                QtWidgets.QStyle.SP_MediaVolumeMuted if self._muted
                else QtWidgets.QStyle.SP_MediaVolume))

        def _dragged(self, value):
            if self.until > self.begins:
                self.jump(self.begins
                              + (self.until - self.begins) * value / 1000.0)

        def _timer(self, t):
            if self.tc0 is None:
                return as_hms(t)
            return timecode_string(self.tc0 + t)

        def _times_show(self):
            self.left_label.setText(
                T('In point %s') % self._timer(self.begins))
            self.right_label.setText(
                T('Out point %s') % self._timer(self.until))

        # -- Setup ----------------------------------------------------
        def set(self, cut, files, offset, audio_file, audio_offset,
                   begins=0.0, until=None, tc0=None,
                   wides=None, colours=None, speaking=None):
            # Where the viewer was, and whether they were watching. A
            # fresh cut arrives whenever the window recomputes its
            # preview, and the picture has to follow it -- but the place
            # and the playing belong to whoever is sitting there.
            ran, where = self._playing, self._time()
            self.pause()
            # Every shot, a camera without a file included: the sound
            # runs on there, and the note says whose shot it is.
            self.cut = [(a, b, who) for a, b, who in (cut or [])]
            self.files = dict(files or {})
            self.wides = set(wides or ())
            self.colours = dict(colours or {})
            # Who speaks when. Read for the note and for nothing else.
            self.speaking = [(str(s.get("name") or ""),
                              [(float(a), float(b))
                               for a, b in (s.get("sections") or [])])
                             for s in (speaking or [])]
            self.hold.forget()
            self.offset = dict(offset or {})
            self.audio_offset = float(audio_offset or 0.0)
            self.begins = float(begins or 0.0)
            self.until = float(until if until is not None else
                             max((b for _a, b, _w in self.cut),
                                 default=0.0))
            self.now = None
            self.loaded = [None, None]
            self.tc0 = tc0
            for seeker in self.seekers:
                seeker.forget()
            self.audio_seek.forget()
            if audio_file:
                _say(T('Audio file %s') % os.path.basename(audio_file))
                self.audio.setSource(QtCore.QUrl.fromLocalFile(audio_file))
            self._times_show()
            self._note_place()
            self.jump(where if where > self.begins else self.begins)
            if ran:
                self.play()

        # -- Seeking --------------------------------------------------
        def jump(self, t):
            """Seek to a point in programme time.

            Always done at a standstill: a running player often refuses the new
            position, and the programme clock would run away during the seek.
            Playback resumes only once picture and audio are both there, which
            the tick handles.
            """
            t = max(self.begins, min(self.until or t, t))
            # A jump is a new place, and the speed it was reached at
            # says nothing about it: back to normal, playing or not.
            self.speed_set(1.0)
            self._t = t
            self.base = t
            self._seeking = True
            self.hold.forget()
            _say(T('--- jump to %s programme time%s ---')
                   % (as_hms(t), T(' (playing)') if self._playing else T(' (paused)')))
            pause_if_running(QtMultimedia, self.audio, *self.videos)
            self.audio_seek.seek_to(
                (t - self.audio_offset) * 1000, T('Audio at programme time'))
            self.now = None
            # Seek on the *visible* surface. Switching to the other would mean
            # showing one that is still loading -- during playback that shows
            # nothing, or the previous shot.
            self._follow_up(t, at_once=True,
                             slot=self.stack.currentIndex())
            if not self.clock.isActive():
                self.clock.start()
            self._tick()

        # -- Playback ----------------------------------------------------
        def is_running(self):
            return self._playing

        def toggle(self):
            self.pause() if self._playing else self.play()

        def faster(self):
            """Play forward, and double the rate on every further press.

            1x, 2x, 4x, 8x, and there it stays -- the same rates and the
            same button as the preview player, so one key does one
            thing on both tabs.
            """
            if not self.cut:
                return
            if self._playing:
                self.speed_set(min(8.0, self._speed * 2.0))
            else:
                self.speed_set(1.0)
                self.play()

        def speed_set(self, rate):
            """Ask for a playback rate and keep the one that arrived.

            The programme clock runs on the rate as well: at twice speed
            the cut arrives twice as soon, and a clock left at 1x would
            switch the picture where the sound has long gone.
            """
            if self._playing and not self._seeking \
                    and self.stopwatch.isValid():
                self.base = self._time()
                self.stopwatch.restart()
            self.audio.setPlaybackRate(rate)
            for one in self.videos:
                one.setPlaybackRate(rate)
            arrived = self.audio.playbackRate()
            self._speed = arrived if arrived > 0 else 1.0
            self.speed_show()

        def speed_show(self):
            """Put the rate on the fast forward button; nothing at 1x."""
            fast = self._speed > 1.01
            self.fast_button.setToolButtonStyle(
                Qt.ToolButtonTextBesideIcon if fast
                else Qt.ToolButtonIconOnly)
            self.fast_button.setText(
                "%g\u00d7" % self._speed if fast else "")
            self.fast_button.setAccessibleName(
                T('Fast forward, %g times speed') % self._speed if fast
                else T('Fast forward'))

        def play(self):
            if not self.cut:
                return
            # The other player first: two pictures running at once are
            # two moments at once, and neither can be judged. What it
            # is set to is in gui(), where both players are known.
            quiet = getattr(self, "hush", None)
            if quiet:
                quiet()
            self._playing = True
            self._icon()
            gui_log("cut play at %.3f s, %s" % (self._time(), self._on_now()))
            if not self.clock.isActive():
                self.clock.start()
            if not self._seeking:
                self._start_playing()

        def _on_now(self):
            """Name the file the cut is showing, for the log."""
            if self.now is None or not (0 <= self.now < len(self.cut)):
                return "nothing loaded"
            who = self.cut[self.now][2]
            return "%s (%s)" % (os.path.basename(self.files.get(who) or "-"),
                                 who)

        def _start_playing(self):
            """Resume playing; the clock starts at the position found."""
            self.base = self._t
            self.stopwatch.restart()
            try:
                self.audio.play()
            except Exception:
                pass
            self._play_when_ready(self.stack.currentIndex())
            # A "play" that does not arrive otherwise shows up only as silence.
            # Check after a moment and try again.
            QtCore.QTimer.singleShot(400, self._recheck_audio)

        def _recheck_audio(self):
            if not self._playing or self._seeking:
                return
            if self.audio.playbackState() == \
                    QtMultimedia.QMediaPlayer.PlayingState:
                return
            print(T('  Player: the audio is not running (%s) -- one more '
                    'attempt.')
                  % _position(self.audio))
            try:
                self.audio.play()
            except Exception:
                pass

        def _play_when_ready(self, slot):
            """Start a surface only when its position holds.

            Otherwise the next attempt pulls it back again.
            """
            if self.seekers[slot].pending():
                return False
            try:
                self.videos[slot].play()
            except Exception:
                return False
            return True

        def pause(self):
            if self._playing and not self._seeking:
                self._t = self._time()
            self._playing = False
            gui_log("cut pause at %.3f s, %s" % (self._t, self._on_now()))
            pause_if_running(QtMultimedia, self.audio, *self.videos)
            # Whatever leaves the running picture goes back to 1x: a
            # rate that survives out of sight explains nothing later.
            self.speed_set(1.0)
            self._icon()
            if not self._seeking and not VERBOSE:
                self.clock.stop()

        def _icon(self):
            self._show_metrics()
            self.button.setIcon(self.style().standardIcon(
                QtWidgets.QStyle.SP_MediaPause if self._playing
                else QtWidgets.QStyle.SP_MediaPlay))

        def _time(self):
            if self._playing and not self._seeking and self.stopwatch.isValid():
                return (self.base
                        + self._speed * self.stopwatch.elapsed() / 1000.0)
            return self._t

        def _which(self, t):
            for j, (a, b, _w) in enumerate(self.cut):
                if a <= t < b:
                    return j
            return None

        def _tick(self):
            if self._seeking and self._search_check():
                return
            t = self._time()
            if self.until and t >= self.until:
                self.pause()
                return
            self._follow_up(t)
            self._show_metrics()
            self._display_text(t)
            if (self.rail is not None and self.until > self.begins
                    and not self.rail.isSliderDown()):
                self.rail.setValue(int(1000 * (t - self.begins)
                                          / (self.until - self.begins)))
            self.position_changed.emit(t)
            if not self._playing and not self._seeking and not VERBOSE:
                self.clock.stop()

        def _search_check(self):
            """Report True while a seek is still in progress."""
            slot = self.stack.currentIndex()
            done = self.audio_seek.check()
            done = self.seekers[slot].check() and done
            self._show_metrics()
            self._display_text(self._t)
            if not done:
                return True
            self._seeking = False
            _say(T('--- point set, programme time runs from %s ---')
                   % as_hms(self._t))
            if self._playing:
                self._start_playing()
            return False

        def _show_metrics(self):
            """Show the debug line only while something is running."""
            if self.readouts.isVisible() != bool(
                    VERBOSE and (self._playing or self._seeking)):
                self.readouts.setVisible(
                    bool(VERBOSE and (self._playing or self._seeking)))

        def _offset_of(self, slot):
            """Return this surface's file offset against the clock."""
            j = self.loaded[slot]
            if j is None or not (0 <= j < len(self.cut)):
                return 0.0
            return self.offset.get(self.cut[j][2], 0.0)

        def _display_text(self, t):
            if not VERBOSE or not self.readouts.isVisible():
                return

            def status(p, unit, offset):
                """Report everything converted back to programme time.

                The raw positions in the files stand on their own and tell
                nobody whether they are right -- three different numbers can
                all be correct and three identical ones all wrong. Converted,
                every one has to read the same as the clock, and the bracket
                behind shows how far off it is.
                """
                spot = p.position() / 1000.0 + offset
                return "%s %7.2f (%+.2f)%s" % (
                    PLAY_STATES.get(p.playbackState(), "?")[:5].ljust(5), spot,
                    spot - t,
                    T(' target %.2f') % (unit.want / 1000.0 + offset)
                    if unit.pending() else "")

            # For the audio the output too: where it runs according to the
            # display and nothing is heard, the answer is here.
            self.readouts.setText(
                T('Clock %7.2f%s | B1[%s] %s | B2[%s] %s | Audio %s %s')
                % (t, T(' SEEKING') if self._seeking else "",
                   self.loaded[0], status(self.videos[0], self.seekers[0],
                                          self._offset_of(0)),
                   self.loaded[1], status(self.videos[1], self.seekers[1],
                                          self._offset_of(1)),
                   status(self.audio, self.audio_seek, self.audio_offset),
                   T('MUTED') if self.audio_out.isMuted()
                   else T('volume %.2f') % self.audio_out.volume()))

        def _follow_up(self, t, at_once=False, slot=None):
            # One search, and both the picture and the note go by it.
            j = self._which(t)
            self.spot_label.setText("%d:%02d" % (int(t) // 60, int(t) % 60))
            self._note_show(t, j)
            if j is None or self.cut[j][2] not in self.files:
                return
            if j != self.now or slot is not None:
                self._switch_to(j, t, slot)
            elif not at_once:
                self._prepare(j + 1, t)

        def _switch_to(self, j, t, slot=None):
            if slot is None:
                slot = next((k for k in (0, 1) if self.loaded[k] == j), None)
            if slot is None:
                slot = 1 - self.stack.currentIndex()
            _a, _b, who = self.cut[j]
            want = max(0.0, t - self.offset.get(who, 0.0))
            fresh = self.loaded[slot] != j
            # Where picture and sound are being put, read word for word
            # by a test. Two numbers that should mean the same moment;
            # where they do not, the sound runs against the wrong
            # picture -- heard long before it can be pointed at.
            if os.environ.get("VPM_PLAYER_LOG"):
                print("  player: programme %8.3f  picture %-32s "
                      "at %8.3f (offset %8.3f)  sound %8.3f (offset %8.3f)"
                      % (t, who, want, self.offset.get(who, 0.0),
                         max(0.0, t - self.audio_offset), self.audio_offset))
            if fresh:
                self._load(slot, j)
            self.stack.setCurrentIndex(slot)
            # Showing a surface puts it on top of its brothers, and the
            # note is one of them.
            self.note.raise_()
            self.now = j
            # Set the position again: a prepared surface otherwise sits where
            # it was loaded, in doubt right at the front.
            p = self.videos[slot]
            if abs(p.position() - want * 1000) > HIT_MS or fresh:
                self.seekers[slot].seek_to(
                    want * 1000, T('Pane %d on %s') % (slot + 1, who))
            else:
                self.seekers[slot].forget()
            if self._playing and not self._seeking:
                self._play_when_ready(slot)
            pause_if_running(QtMultimedia, self.videos[1 - slot])

        def _load(self, slot, j):
            """Load a shot's file into a surface."""
            _a, _b, who = self.cut[j]
            file_path = self.files.get(who)
            if not file_path:
                return
            self.loaded[slot] = j
            p = self.videos[slot]
            if p.source() != QtCore.QUrl.fromLocalFile(file_path):
                _say(T('Pane %d loads %s (%s)')
                       % (slot + 1, os.path.basename(file_path), who))
                p.setSource(QtCore.QUrl.fromLocalFile(file_path))

        def _prepare(self, j, t):
            """Load the next shot and start it running."""
            if j >= len(self.cut) or self.cut[j][2] not in self.files:
                return
            slot = 1 - self.stack.currentIndex()
            a, _b, who = self.cut[j]
            # The lead is a lead in real time: at twice speed the cut
            # arrives twice as soon, so the pane has to start earlier.
            lead = self.LEAD_IN * max(1.0, self._speed)
            if self.loaded[slot] == j:
                self.seekers[slot].check()
                if (a - t <= lead and self._playing
                        and self.videos[slot].playbackState()
                        != QtMultimedia.QMediaPlayer.PlayingState):
                    self._play_when_ready(slot)
                return
            if a - t > 2 * lead:
                return
            self._load(slot, j)
            self.seekers[slot].seek_to(
                max(0.0, a - lead - self.offset.get(who, 0.0)) * 1000,
                T('Prepare pane %d for %s') % (slot + 1, who))

    return CutPlayer


def make_player_widgets(QtCore, QtGui, QtWidgets, Qt, label, hint,
                     ffplay_preview, real_tc, state):
    """The building blocks of the preview: rail, video surface, player.

    They sit outside gui() because they have nothing to do with the rest of
    the layout -- a video player is a video player. They are still built
    only once Qt is loaded: without Qt the script keeps working on the
    command line, and a class inheriting from a Qt widget could not even be
    defined then.

    Whatever is needed from gui() comes in as an argument and keeps its
    name inside.
    """
    from PySide6 import QtMultimedia, QtMultimediaWidgets
    class WindowSlider(QtWidgets.QSlider):
        """A slider showing what is left of the material.

        The chosen time window lies as a light band over the rail, the
        discarded parts grey before and after it. Dragging then shows whether
        the position is still inside.
        """

        def __init__(self, parent=None):
            QtWidgets.QSlider.__init__(self, Qt.Horizontal, parent)
            self.begins = None
            self.until = None
            self.colours_apply()

        def colours_apply(self):
            """Paint the rail in the colours of this desktop.

            The rail is drawn grey throughout -- only what lies between
            the In point and the Out point is blue. Otherwise the
            system would colour everything left of the handle and two
            unrelated things would look alike.

            The three values come from COLOURS, so the rail follows a
            dark desktop; a fixed light grey stood there before at
            10.7 against a dark box, a white band in a dark window.
            Measured 23.8.2026: the outline against the handle is now
            5.2 light and 6.0 dark, where the fixed pair gave 2.9 --
            under the 3 that WCAG 1.4.11 asks of a control.
            """
            self.setStyleSheet("""
                QSlider::groove:horizontal {
                    height: 6px; background: %(frame)s; border-radius: 3px;
                }
                QSlider::sub-page:horizontal,
                QSlider::add-page:horizontal {
                    background: %(frame)s; border-radius: 3px;
                }
                QSlider::handle:horizontal {
                    width: 13px; margin: -5px 0; border-radius: 7px;
                    background: %(sheet)s; border: 1px solid %(quiet)s;
                }
            """ % {k: COLOURS[k] for k in ("frame", "sheet", "quiet")})

        def set_range(self, begins, until):
            self.begins, self.until = begins, until
            self.update()

        def paintEvent(self, e):
            QtWidgets.QSlider.paintEvent(self, e)
            if self.begins is None and self.until is None:
                return
            span = self.maximum() - self.minimum()
            if span <= 0:
                return
            groove = self.style().subControlRect(
                QtWidgets.QStyle.CC_Slider,
                self._options(), QtWidgets.QStyle.SC_SliderGroove, self)
            handle = self.style().pixelMetric(
                QtWidgets.QStyle.PM_SliderLength, None, self)
            width = max(1, groove.width() - handle)

            def x(ms):
                share = (min(max(ms, self.minimum()), self.maximum())
                          - self.minimum()) / float(span)
                return groove.left() + handle / 2.0 + share * width

            a = x(self.begins if self.begins is not None else self.minimum())
            b = x(self.until if self.until is not None else self.maximum())
            if b <= a:
                return
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            # Leave the handle clear, or the band draws a line right through
            # it.
            handle_rect = self.style().subControlRect(
                QtWidgets.QStyle.CC_Slider, self._options(),
                QtWidgets.QStyle.SC_SliderHandle, self)
            painter.setClipRegion(QtGui.QRegion(self.rect())
                                - QtGui.QRegion(handle_rect))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QtGui.QColor(COLOURS["value"]))
            height = 6
            painter.drawRoundedRect(
                QtCore.QRectF(a, groove.center().y() - height / 2.0,
                              b - a, height), 3, 3)
            painter.setPen(QtGui.QPen(QtGui.QColor(COLOURS["heading"]), 2))
            for edge in (a, b):
                painter.drawLine(QtCore.QPointF(edge, groove.center().y() - 8),
                               QtCore.QPointF(edge, groove.center().y() + 8))
            painter.end()

        def _options(self):
            opt = QtWidgets.QStyleOptionSlider()
            self.initStyleOption(opt)
            return opt

    # Qt's own surface. Nothing is caught on it: the picture fills the
    # box it has been given and there is no full screen to leave.
    VideoSurface = QtMultimediaWidgets.QVideoWidget

    class Player(QtWidgets.QWidget):

        plays = True
        # Signal for the still fetched in the background.
        still_ready = QtCore.Signal(bytes, str, int)

        T('The viewer: a window inside the window that stays put.\n\n        '
          'Qt plays audio and video itself -- that is enough for the\n      '
          '  usual formats. What the machine does not know (MXF, R3D,\n     '
          '   some ProRes variants) the player hands on to ffplay instead\n '
          '       of throwing an error.\n\n        In point and Out point are '
          'set from here as well: the point you\n        see is the point '
          'you mean.\n        ')

        def __init__(self, parent=None):
            QtWidgets.QWidget.__init__(self, parent)
            self.file_path = None
            self.tc0 = None            # wall clock time at file start
            self.fps = 30.0
            self.failed = None
            # What the line above the picture says when nothing is wrong,
            # so a refusal written over it can be taken back again.
            self._title_plain = None
            position = QtWidgets.QVBoxLayout(self)
            position.setContentsMargins(0, 0, 0, 0)
            position.setSpacing(6)
            self.title = label(T('nothing loaded yet'), COLOURS["quiet"])
            self.title.setWordWrap(True)
            position.addWidget(self.title)
            # Whoever embeds the player can take the file name into their own
            # heading and save the line here.
            self.heading = None
            self.video = VideoSurface(self)
            # Fixed height: otherwise the picture claims half the interface as
            # soon as Qt knows the resolution of the file.
            self.video.setFixedHeight(302)
            self.video.setMinimumWidth(320)
            self.video.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                    QtWidgets.QSizePolicy.Fixed)
            self.video.setStyleSheet("background: #101418;")
            # A paused player draws nothing on some machines, so the frame is
            # fetched with ffmpeg and laid over the top -- that works for
            # formats Qt will not play too.
            self.still = QtWidgets.QLabel()
            self.still.setAlignment(Qt.AlignCenter)
            self.still.setStyleSheet("background: #101418;")
            self.stack = QtWidgets.QStackedWidget()
            self.stack.addWidget(self.video)
            self.stack.addWidget(self.still)
            self.stack.setFixedHeight(302)
            self.stack.setCurrentWidget(self.still)
            position.addWidget(self.stack)
            self.still_ready.connect(self.still_show)
            self._still_index = 0
            self._still_job = None
            self._still_running = False
            self._still_lock = threading.Lock()
            # Where Qt cannot handle the format, a button takes the same place.
            self.extern = QtWidgets.QPushButton(
                T('External preview -- the app does not know this format'))
            self.extern.setMinimumHeight(60)
            self.extern.clicked.connect(self.outside_show)
            self.extern.hide()
            position.addWidget(self.extern)
            # First the rail across the full width, the buttons below -- the
            # way every player is laid out.
            self.slider = WindowSlider()
            self.slider.setRange(0, 1000)
            self.slider.sliderMoved.connect(self.scrub)
            self.slider.sliderPressed.connect(
                lambda: setattr(self, "_held", True))
            self.slider.sliderReleased.connect(self.released)
            self._held = False
            self._should_play = False
            # Fast forward doubles from here. Only forwards: a negative
            # rate is accepted by Qt but the ffmpeg backend underneath
            # reports 0.00 back and stands still, so backwards is not
            # offered at all rather than offered and dead.
            self._speed = 1.0
            self._muted = False
            # The picture should follow while dragging but not be decoded on
            # every pixel: four times a second is enough.
            self._scrub_target = None
            position.addWidget(hint(self.slider, T('Drag to move the position.')))
            # Fixed character width, or the line shifts back and forth with
            # every changing digit.
            digits = digits_font(QtGui, self)
            # Under the rail first the configured window and its buttons --
            # that is the handle. Only then where we are, and the transport at
            # the bottom.
            cut_row = QtWidgets.QHBoxLayout()
            position.addLayout(cut_row)
            self.cut_left = label("", COLOURS["value"], True)
            cut_row.addWidget(self.cut_left)
            cut_row.addStretch(1)
            self.cut_right = label("", COLOURS["value"], True)
            cut_row.addWidget(self.cut_right)
            # The window length on a line of its own, under the two
            # boundaries it spans. In the row above, In point and Out
            # point and the gaps take 300 of the 560 px; the German
            # sentence about a file that starts later wants 288 of the
            # 260 left over, the one about a file outside the window
            # 300. The line costs 16 px of height in a box that has 260
            # px of them unused underneath it.
            window_row = QtWidgets.QHBoxLayout()
            position.addLayout(window_row)
            window_row.addStretch(1)
            self.cut_middle = label("", COLOURS["quiet"])
            window_row.addWidget(self.cut_middle)
            window_row.addStretch(1)
            for m in (self.cut_left, self.cut_middle, self.cut_right):
                m.setFont(QtGui.QFont(digits))
            # Stays empty if nobody fills it: the interface puts its cut
            # buttons in here.
            self.cut_bar = QtWidgets.QHBoxLayout()
            position.addLayout(self.cut_bar)
            # A line of its own for the checkbox. It used to stand in the
            # row above, between the four cut buttons: in English the
            # five fit, in German they do not, and the label came out
            # cut off after two thirds. Measured: the four German
            # buttons and the checkbox want 548 px in a row about 480 px
            # wide. Made
            # unshrinkable it stopped being cut off and started sitting
            # on top of the next button instead -- which is why it now
            # has a line to itself in both languages rather than one
            # language having a layout of its own.
            self.under_cut = QtWidgets.QHBoxLayout()
            position.addLayout(self.under_cut)
            # Left where the file starts, right where it ends, in the middle
            # where we are.
            time_row = QtWidgets.QHBoxLayout()
            position.addLayout(time_row)
            self.left_label = label("", COLOURS["quiet"])
            time_row.addWidget(self.left_label)
            time_row.addStretch(1)
            self.middle = label("", COLOURS["heading"], True)
            time_row.addWidget(self.middle)
            time_row.addStretch(1)
            self.right_label = label("", COLOURS["quiet"])
            time_row.addWidget(self.right_label)
            for m in (self.left_label, self.right_label):
                m.setFont(QtGui.QFont(digits))
            digits.setBold(True)
            self.middle.setFont(QtGui.QFont(digits))
            digits.setBold(False)
            bar = QtWidgets.QHBoxLayout()
            position.addLayout(bar)

            def icon(name):
                return self.style().standardIcon(
                    getattr(QtWidgets.QStyle, name))

            # All buttons equally wide across the line, so the transport is
            # where the eye looks for it and not at the left edge. Same height
            # and same icon size too: the system icons come in different
            # sizes.
            HEIGHT = 30
            SYMBOL = QtCore.QSize(18, 18)

            def wide(widget):
                widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                QtWidgets.QSizePolicy.Fixed)
                widget.setFixedHeight(HEIGHT)
                return widget

            def button(name, text, on_click):
                k = QtWidgets.QToolButton()
                k.setIcon(icon(name))
                k.setIconSize(SYMBOL)
                k.setAutoRaise(True)
                k.clicked.connect(on_click)
                bar.addWidget(hint(wide(k), text), 1)
                return k

            def step(text, tooltip_text, seconds=None, videos=None):
                button = QtWidgets.QToolButton()
                button.setText(text)
                button.setAutoRaise(True)
                button.setMinimumWidth(caption_room(button, 42))
                button.clicked.connect(
                    lambda _=False, s=seconds, b=videos: self.nudge(s, b))
                bar.addWidget(hint(wide(button), tooltip_text), 1)
                return button

            button("SP_MediaSkipBackward", T('To the start.'),
                  lambda: self.jump(0))
            step("-10 s", T('Ten seconds back.'), seconds=-10.0)
            step("-1 s", T('One second back.'), seconds=-1.0)
            step("-1 F", T('One frame back.'), videos=-1)
            self.button = button("SP_MediaPlay", T('Play and pause -- the '
                                                   'space bar works too.'),
                               self.toggle)
            self.button.setAccessibleName(T('Play and pause'))
            step("+1 F", T('One frame forward.'), videos=1)
            step("+1 s", T('One second forward.'), seconds=1.0)
            step("+10 s", T('Ten seconds forward.'), seconds=10.0)
            # Fast forward has a button of its own, at the end of the
            # transport where the steps forward end. The L key did the
            # same thing before and did it invisibly: a key nobody is
            # told about is a key nobody presses.
            self.fast_button = button("SP_MediaSeekForward",
                                      T('Play forward, twice as fast on '
                                        'every press -- the L key.'),
                                      self.faster)
            self.mute_button = button("SP_MediaVolume", T('Mute.'),
                                     self.toggle_mute)
            self.loud = QtWidgets.QSlider(Qt.Horizontal)
            self.loud.setRange(0, 100)
            self.loud.setValue(100)
            self.loud.setMinimumWidth(72)
            self.loud.valueChanged.connect(lambda *_: self.audio_adjust())
            bar.addWidget(hint(wide(self.loud),
                               T('Volume. 100 is as loud as it goes -- '
                                 'Qt takes nothing above that.')), 2)
            # The checkbox sits a line lower with the cut buttons: there is
            # room there, and it belongs to the same handle.
            self.track_checkbox = QtWidgets.QCheckBox(T('hear assigned audio'))
            self.under_cut.addWidget(self.track_checkbox)
            self.under_cut.addStretch(1)
            self.track_checkbox.setChecked(True)
            self.track_checkbox.toggled.connect(lambda *_: self.track_adjust())
            self.track_checkbox.setToolTip(T('The recording assigned to this '
                                         'camera instead of the camera '
                                         'audio.'))
            # Second player: the picture comes from the camera, the audio from
            # the assigned recording. Both are set to the same position and
            # started together -- enough for a preview; measuring and aligning
            # happen in the run.
            self._muted = False
            self.track_audio = audio_sink(QtMultimedia, self)
            self.track = QtMultimedia.QMediaPlayer(self)
            self.track.setAudioOutput(self.track_audio)
            self._moment = None    # kept where a file cannot show it
            self._wanted_ms = None  # where a jump is headed, until it lands
            self.track_path = None          # the block playing now
            self.track_blocks = []          # the whole recording, in order
            self.find_track = None          # set by the GUI
            self._track_target = None
            self.track.mediaStatusChanged.connect(self.track_loaded)
            self.audio = audio_sink(QtMultimedia, self)
            self.player = QtMultimedia.QMediaPlayer(self)
            self.player.setAudioOutput(self.audio)
            self.player.setVideoOutput(self.video)
            self.player.positionChanged.connect(self.spot)
            self.player.durationChanged.connect(self.length)
            self.player.mediaStatusChanged.connect(self.loaded)
            self._target_at = 0.0   # when that jump was asked for
            self._moaned = None     # the refusal already reported
            self._target_ms = None
            # At a standstill a still fetched by ffmpeg is shown, during
            # playback the video surface. Reason: some camera formats -- 10 bit
            # 4:2:2 for instance -- Qt cannot get onto the GPU ("failed to get
            # textures for frame"), and the surface would stay black.
            self.player.videoSink().videoFrameChanged.connect(
                self.frame_arrived)
            self.audio_adjust()
            # Once here, so the fast forward button carries its name for
            # a screen reader before anything has been loaded.
            self.speed_show()
            self.player.errorOccurred.connect(self.on_error)

        # --- load and play
        def load(self, file_path, seconds=None, running=False):
            """Show a different file at the same point.

            Playback stops on the switch, otherwise comparing two cameras would
            start the audio every time. If old and new file both carry a
            measured place the seek goes to the same moment in the
            events, not the same offset from the file start: cameras
            begin at different times. The clocks are the fallback.
            """
            old_one_position = self.position()
            old_one_spot = self.spot_s()
            pause_if_running(QtMultimedia, self.player)
            self.speed_set(1.0)
            self.file_path = os.path.abspath(file_path)
            self.failed = (file_path, seconds)
            audio_file = os.path.splitext(file_path)[1].lower() in AUDIO_SUFFIXES
            self.tc0, self.fps = None, 30.0
            try:
                if audio_file:
                    self.tc0 = file_timecode(file_path)
                else:
                    info = video_facts(file_path)
                    self.fps = max(1.0, info.get("fps") or 30.0)
                    if info.get("tc"):
                        self.tc0 = parse_timecode(info["tc"], self.fps)
            except Exception:
                pass
            if seconds is None:
                old_timer, old_axis = old_one_position
                # The measurement first, for both ends at once: two
                # clocks each carry their own idea of the time, and the
                # difference stays in the result. See track_follow_up.
                if old_axis is not None and self.axis_s() is not None:
                    seconds = old_axis - self.axis_s()
                elif old_timer is not None and self.tc0 is not None:
                    seconds = old_timer - self.tc0
                else:
                    seconds = old_one_spot
                if seconds < 0.0:
                    # This camera had not started at that moment. Its
                    # front is what can be shown, but the moment is
                    # kept: read back out of a file that cannot hold
                    # it, it would be lost for the next switch too.
                    self._moment = old_one_position
                    seconds = 0.0
                else:
                    self._moment = None
            self._title_plain = "%s%s" % (os.path.basename(file_path),
                                          T('   --   audio only')
                                          if audio_file else "")
            self._title_show(self._title_plain)
            self.extern.hide()
            # And the picture back: a refused format takes the surface
            # away, and that state belonged to the player rather than to
            # the file -- one such file cost every later one its picture,
            # sound running and nothing to be seen.
            self.picture_show()
            self.stack.setVisible(not audio_file)
            # Remember first, then set: setSource can fire "loaded"
            # immediately, and that clears the target position.
            target = int(max(0.0, seconds) * 1000)
            self._target_ms = target
            self._target_at = time.monotonic()
            self.player.setSource(QtCore.QUrl.fromLocalFile(self.file_path))
            self.player.setPosition(target)
            self.track_adjust()
            self._should_play = bool(running)
            # Not started here even where it is wanted: setPosition on
            # a source that has not loaded does nothing, so a player
            # started now runs the file's front until the jump lands.
            # loaded() starts it once the position sits.
            if not running:
                # Fetch a frame right on loading. The previous one stays up
                # until it arrives -- better than a black surface.
                QtCore.QTimer.singleShot(0, self.expect_frame)
            self.set_mark()
            self.spot(int(max(0.0, seconds) * 1000))
            self._wanted_ms = target   # after spot(), or it drops it
            self.window_draw()
            gui_log("load %s at %.3f s%s"
                     % (os.path.basename(file_path), max(0.0, seconds),
                        ", playing" if running else ""))

        def window_draw(self):
            """Draw the In point and the Out point onto the rail."""
            self.slider.set_range(self._limit(state["in_point"]),
                                         self._limit(state["out_point"]))
            self.spot(self.player.position())

        def _window_length(self):
            """Return the length of the configured window.

            Computed from the two settings, not from their positions in this
            file: with In point before this file's first frame, the length of
            the file would appear instead of the length of the window.
            """
            try:
                a, abs_a = parse_time_point(state["in_point"], self.fps)
                b, abs_b = parse_time_point(state["out_point"], self.fps)
            except Exception:
                return ""
            if a is None or b is None or abs_a != abs_b or b <= a:
                return ""
            missing = ""
            if abs_a and self.tc0 is not None:
                duration = self.player.duration() / 1000.0
                if self.tc0 + duration <= a or self.tc0 >= b:
                    missing = T('  --  this file is outside')
                elif self.tc0 > a:
                    missing = T('  (this file starts later)')
                elif self.tc0 + duration < b:
                    missing = T('  (this file ends earlier)')
            return T('Window %s%s') % (as_hms(b - a), missing)

        def _limit(self, text):
            """Convert a time value into a position in this file."""
            try:
                value, absolute = parse_time_point(text, self.fps)
            except Exception:
                return None
            if value is None:
                return None
            if absolute:
                if self.tc0 is None:
                    return None
                value -= self.tc0
            elif value >= 0 and self.axis_s() is not None:
                # Relative values count from the start of the material, not
                # from the start of this file.
                value -= self.axis_s()
            elif value < 0:
                value = self.player.duration() / 1000.0 + value
            return int(max(0.0, value) * 1000)

        def jump_to(self, text):
            ms = self._limit(text)
            if ms is None:
                return False
            self.jump(ms)
            return True

        def set_mark(self):
            is_running = (self.player.playbackState()
                      == QtMultimedia.QMediaPlayer.PlayingState)
            self.button.setIcon(self.style().standardIcon(
                QtWidgets.QStyle.SP_MediaPause if is_running
                else QtWidgets.QStyle.SP_MediaPlay))

        def seek_settle(self):
            """Ask for the jump again until the new file is really there.

            A freshly opened file falls back to its front after it has
            reported itself loaded -- measured 18 to 88 ms, never twice
            the same -- and the single shot fired on that report went
            with it. A clock of its own, since a still picture reports
            no position and nothing would ask again.
            """
            if self._target_ms is None:
                return
            here = self.player.position()
            waited = time.monotonic() - self._target_at
            if here >= self._target_ms - SEEK_HIT_MS:
                # At the mark or past it. Playing on moves forward, a
                # file that fell back is behind -- so "past it" is never
                # the fault, and no state has to be waited for.
                if waited >= SEEK_SETTLE_S:
                    self._target_ms = None
                    if not self._should_play:
                        self.expect_frame()
                    return
            elif self.player.mediaStatus() in (
                    QtMultimedia.QMediaPlayer.LoadedMedia,
                    QtMultimedia.QMediaPlayer.BufferedMedia,
                    QtMultimedia.QMediaPlayer.BufferingMedia):
                self.player.setPosition(self._target_ms)
            if waited > SEEK_PATIENCE_S:
                gui_log("%s stays at %.3f s instead of %.3f s -- given up"
                         % (os.path.basename(self.file_path or "-"),
                            self.player.position() / 1000.0,
                            self._target_ms / 1000.0))
                self._target_ms = None
                if self._should_play:
                    self.play_when_ready()
                return
            QtCore.QTimer.singleShot(SEEK_AGAIN_MS, self.seek_settle)

        def play_when_ready(self):
            """Start only once the jump has landed.

            Started earlier, the next attempt pulls the picture back --
            the cut player says the same thing in _play_when_ready.
            """
            if self._target_ms is not None:
                return
            playing = QtMultimedia.QMediaPlayer.PlayingState
            self.stack.setCurrentWidget(self.video)
            if self.player.playbackState() != playing:
                self.player.play()
            if self.track_path and self.track.playbackState() != playing:
                self.track.play()

        def loaded(self, status):
            """Enable seeking once the file is open.

            setSource works in the background; a setPosition before that goes
            nowhere, and without a nudge the surface stays black.
            """
            pending = (QtMultimedia.QMediaPlayer.LoadedMedia,
                     QtMultimedia.QMediaPlayer.BufferedMedia)
            if status not in pending:
                return
            self.seek_settle()
            if self._should_play:
                self.stack.setCurrentWidget(self.video)
                self.player.play()
                if self.track_path:
                    self.track.play()
            else:
                self.expect_frame()
            self.set_mark()

        def track_loaded(self, status):
            """The same for the assigned audio track."""
            pending = (QtMultimedia.QMediaPlayer.LoadedMedia,
                     QtMultimedia.QMediaPlayer.BufferedMedia)
            if status not in pending:
                return
            target, self._track_target = self._track_target, None
            if target is not None:
                self.track.setPosition(target)
            if (self.player.playbackState()
                    == QtMultimedia.QMediaPlayer.PlayingState):
                self.track.play()

        def start(self):
            """Play on from here, at the speed currently set."""
            if self.file_path is None:
                return
            # The cut player first, for the reason given at its own
            # play: two pictures running at once cannot be judged.
            quiet = getattr(self, "hush", None)
            if quiet:
                quiet()
            self._should_play = True
            self.stack.setCurrentWidget(self.video)
            self.player.play()
            if self.track_path:
                self.track.play()
            self.set_mark()
            gui_log("play %s at %.3f s%s"
                     % (os.path.basename(self.file_path), self.spot_s(),
                        " with %s" % os.path.basename(self.track_path)
                        if self.track_path else ""))

        def pause(self):
            """Hold the picture, and put the speed back to normal.

            Everything that leaves the running picture -- pausing, a
            jump, another file -- goes back to 1x. A rate that survives
            out of sight is one nobody can explain the odd sound by
            afterwards, and the way on from a standstill is the play
            button, which says nothing about eight times speed.

            There is no stop beside this. Stopping would mean going
            back to the beginning, and nothing here wants that: what
            the transport is for is holding a passage still.
            """
            if self.file_path is None:
                return
            self._should_play = False
            pause_if_running(QtMultimedia, self.player, self.track)
            self.speed_set(1.0)
            QtCore.QTimer.singleShot(60, self.expect_frame)
            self.set_mark()
            gui_log("pause %s at %.3f s"
                     % (os.path.basename(self.file_path), self.spot_s()))

        def now_playing(self):
            """Whether playback is meant to go on -- across a file switch."""
            return bool(self._should_play)

        def toggle(self):
            if self.file_path is None:
                return
            if (self.player.playbackState()
                    == QtMultimedia.QMediaPlayer.PlayingState):
                self.pause()
            else:
                self.start()

        def faster(self):
            """Play forward, and double the rate on every further press.

            1x, 2x, 4x, 8x, and there it stays: beyond that the sound
            carries nothing to find a passage by, which is what fast
            forward is for. Backward is not offered -- see _speed.
            """
            if self.file_path is None:
                return
            if (self.player.playbackState()
                    == QtMultimedia.QMediaPlayer.PlayingState):
                self.speed_set(min(8.0, self._speed * 2.0))
            else:
                self.speed_set(1.0)
                self.start()

        def speed_set(self, rate):
            """Ask for a playback rate and keep the one that arrived.

            Qt takes a rate without promising it, and the backend below
            may hand back another. What is shown is therefore what the
            player reports, not what was asked for.
            """
            self.player.setPlaybackRate(rate)
            self.track.setPlaybackRate(rate)
            arrived = self.player.playbackRate()
            self._speed = arrived if arrived > 0 else 1.0
            self.speed_show()

        def speed_show(self):
            """Put the rate on the fast forward button; nothing at 1x.

            On the button that made it: the rate is what that button
            does, and the play button keeps one meaning. It also keeps
            the row stiller -- measured at the narrowest the transport
            goes, a number beside the play icon pushes five of the ten
            buttons 26 pixels along, beside this one it pushes one.
            """
            fast = self._speed > 1.01
            self.fast_button.setToolButtonStyle(
                Qt.ToolButtonTextBesideIcon if fast
                else Qt.ToolButtonIconOnly)
            self.fast_button.setText("%g\u00d7" % self._speed if fast else "")
            self.fast_button.setAccessibleName(
                T('Fast forward, %g times speed') % self._speed if fast
                else T('Fast forward'))

        def picture_show(self):
            """Put up the page the stack calls the current one.

            Which of the two carries the picture is the stack's answer;
            this only undoes a page hidden behind its back.
            """
            here = self.stack.currentWidget()
            if here is not None:
                here.show()

        def trouble_gone(self):
            """Take the refusal back once pictures arrive again.

            It is an answer about one attempt, not about the player, so
            a picture running again settles it -- without this only
            loading another file did, and the button stood on beside it.
            """
            if not self.extern.isVisible():
                return
            # Pictures again, so the refusal may be reported again: what
            # was silenced was the storm, not the fault.
            self._moaned = None
            self.extern.hide()
            self.picture_show()
            if self._title_plain is not None:
                self._title_show(self._title_plain)

        def frame_arrived(self, frames):
            """Qt delivered a frame; show it during playback."""
            if frames is None or not frames.isValid():
                return
            self.trouble_gone()
            if (self._should_play
                    and self.stack.currentWidget() is not self.video):
                self.stack.setCurrentWidget(self.video)

        def expect_frame(self):
            """Request a new still; the old one stays until it arrives.

            Not by switching to the video surface: that is black right after a
            seek, and with these formats often permanently.
            """
            self.still_fetch()

        def still_fetch(self):
            """Fetch a single frame from this position, in the background.

            Only ever one at a time. Dragging would otherwise fire a new ffmpeg
            call at the same 30 GB file every tenth of a second and the machine
            would fall behind. A request arriving meanwhile simply replaces the
            pending one -- only the last position chosen is of interest anyway.
            """
            if not self.file_path or os.path.splitext(self.file_path)[1].lower() \
                    in AUDIO_SUFFIXES:
                return
            self._still_index += 1
            with self._still_lock:
                self._still_job = (self.file_path,
                                           max(0.0, self.spot_s()),
                                           max(320, self.stack.width()),
                                           self._still_index)
                if self._still_running:
                    return
                self._still_running = True
            threading.Thread(target=self._still_loop,
                             daemon=True).start()

        def _still_loop(self):
            while True:
                with self._still_lock:
                    job = self._still_job
                    self._still_job = None
                    if job is None:
                        self._still_running = False
                        return
                file_path, spot, width, idx = job
                try:
                    p = subprocess.run(
                        ["ffmpeg", "-v", "error", "-ss", "%.3f" % spot,
                         "-i", file_path, "-frames:v", "1", "-vf",
                         "scale=%d:-2" % width, "-q:v", "4",
                         "-f", "image2pipe", "-vcodec", "mjpeg", "-"],
                        capture_output=True, timeout=30)
                    if p.returncode == 0 and p.stdout:
                        self.still_ready.emit(p.stdout, file_path, idx)
                except Exception:
                    pass

        def still_show(self, raw, file_path, idx):
            """Insert the fetched frame, if it is still the right one."""
            if idx != self._still_index or file_path != self.file_path:
                return
            if (self.player.playbackState()
                    == QtMultimedia.QMediaPlayer.PlayingState):
                return
            video = QtGui.QPixmap()
            if not video.loadFromData(raw):
                return
            self.still.setPixmap(video.scaled(
                self.stack.size(), Qt.KeepAspectRatio,
                Qt.SmoothTransformation))
            self.stack.setCurrentWidget(self.still)


        # --- the assigned audio track
        def track_adjust(self):
            """Pick the audio for the picture: own or assigned."""
            wanted_value = None
            if (self.track_checkbox.isChecked() and self.find_track
                    and self.file_path and os.path.splitext(self.file_path)[1].lower()
                    not in AUDIO_SUFFIXES):
                wanted_value = self.find_track(self.file_path)
            if not wanted_value:
                self.track_path, self.track_blocks = None, []
                self.track.stop()
                self.track.setSource(QtCore.QUrl())
                self.track_checkbox.setEnabled(bool(self.find_track))
                self.audio_adjust()
                return
            # A recording arrives as all its blocks; which one plays
            # depends on where the picture stands, so track_follow_up
            # picks it.
            if list(wanted_value) != self.track_blocks:
                self.track_blocks = list(wanted_value)
                self.track_path = None
            self._label_track()
            self.audio_adjust()
            self.track_follow_up()

        def _label_track(self):
            """Label the checkbox with what is playing and how loud it is.

            Depending on the recording level, a raw recording sits 16 to 36 dB
            below the processed audio. Switching between the two players, that
            is easily mistaken for a fault.
            """
            playing = self.track_path or (self.track_blocks
                                           or [None])[0]
            if not playing:
                self.track_checkbox.setToolTip(
                    T('The recording assigned to this camera instead of '
                      'the camera audio.'))
                return
            name = os.path.basename(playing)
            if name.startswith("final_"):
                self.track_checkbox.setToolTip(
                    T('Playing %s -- the processed track from '
                      'auphonic.com,\nbrought to broadcast level. The same '
                      'audio as in the camera cut.') % name)
            else:
                self.track_checkbox.setToolTip(
                    T('Playing %s -- the raw recording.\nIt is much quieter '
                      'than the processed audio; once the tracks from '
                      'auphonic.com\nare there, the preview takes those.') % name)

        def track_where(self):
            """Which block belongs under the picture now, and where in it.

            Both ends of this out of the same reckoning: two clocks are
            seconds apart -- 2.35 s where that was found -- and taking
            one from the other leaves exactly that between sound and
            picture. The clocks are the fallback, and then for both at
            once. Returns (path, seconds into it, which reckoning).
            """
            here = self.axis_spot()
            if here is not None:
                path, into = block_at(
                    self.track_blocks, here,
                    lambda p: state["axis"].get(path_key(p)))
                if path is not None:
                    return path, into, "measured"
            here = self.timer_s()
            if here is not None:
                path, into = block_at(self.track_blocks, here, real_tc)
                if path is not None:
                    return path, into, "by clock"
            return None, None, ""

        def track_follow_up(self):
            """Move the audio track to the same point in the events."""
            if not self.track_blocks:
                return
            path, into, whose = self.track_where()
            if path is None:
                # Not this recording's moment. Its first block is loaded
                # and stays ready, but silent -- sounding here would put
                # it against a picture it does not belong to.
                path = self.track_blocks[0]
            if path != self.track_path:
                self.track_path = path
                self.track.setSource(QtCore.QUrl.fromLocalFile(path))
                self._label_track()
            if into is None:
                pause_if_running(QtMultimedia, self.track)
                gui_log("%s is not due where %s stands -- silent"
                         % (os.path.basename(path),
                            os.path.basename(self.file_path or "-")))
                return
            ms = int(max(0.0, into) * 1000)
            gui_log("%s %s: %.3f s into it, block %d of %d"
                     % (os.path.basename(path), whose, ms / 1000.0,
                        self.track_blocks.index(path) + 1,
                        len(self.track_blocks)))
            self._track_target = ms
            self.track.setPosition(ms)
            # Only where playback is really wanted -- the short nudge for the
            # still is silent and must not start anything here.
            if self._should_play:
                self.track.play()
            else:
                pause_if_running(QtMultimedia, self.track)

        def toggle_mute(self):
            self._muted = not self._muted
            self.audio_adjust()

        def audio_adjust(self):
            """Apply volume and mute to both players.

            While the assigned recording plays, the camera audio is switched
            off and the slider still has to work, otherwise it does nothing.
            """
            value = self.loud.value() / 100.0
            self.audio.setVolume(loud(value))
            self.track_audio.setVolume(loud(value))
            self.track_audio.setMuted(hushed(self._muted))
            self.audio.setMuted(hushed(self._muted
                                        or bool(self.track_blocks)))
            self.mute_button.setIcon(self.style().standardIcon(
                QtWidgets.QStyle.SP_MediaVolumeMuted if self._muted
                else QtWidgets.QStyle.SP_MediaVolume))

        def nudge(self, seconds=None, videos=None):
            """Step forwards or backwards without starting playback."""
            ms = self.player.position()
            if seconds:
                ms += int(seconds * 1000)
            if videos:
                ms += int(round(videos * 1000.0 / max(1.0, self.fps)))
            self.jump(max(0, min(ms, self.player.duration() or ms)))

        def scrub(self, ms):
            """Only the numbers follow while dragging.

            Decoding a frame at every step would mean one ffmpeg call per
            tenth of a second. The new frame arrives once the mouse stops.
            """
            self._scrub_target = ms
            self.spot(ms)

        def jump(self, ms):
            # A jump is a new place, and the speed it was reached at
            # says nothing about it: back to normal, playing or not.
            self.speed_set(1.0)
            self.player.setPosition(ms)
            self.track_follow_up()
            self.spot(ms)
            if not self._should_play:
                self.expect_frame()

        def released(self):
            self._held = False
            self._scrub_target = None
            self.player.setPosition(self.slider.value())
            self.track_follow_up()
            if not self._should_play:
                self.expect_frame()

        def length(self, ms):
            self.slider.setRange(0, max(1, ms))
            self.show_edges()

        def time_mark(self, seconds_from_begin):
            """Return a position in this file as wall clock time.

            Out of the measurement wherever it carries a wall clock:
            it has held every file against the others, while a single
            clock carries only its own idea of the time. The file's own
            timecode answers where nothing was measured, and a measured
            axis with no clock behind it says so.
            """
            a = self.axis_s()
            if a is not None and state.get("axis_absolute"):
                return timecode_string(a + seconds_from_begin, self.fps)
            if self.tc0 is not None:
                return timecode_string(self.tc0 + seconds_from_begin, self.fps)
            if a is not None:
                return T('%s virtual') % timecode_string(a + seconds_from_begin,
                                                 self.fps)
            return as_hms(seconds_from_begin)

        def show_edges(self):
            duration = self.player.duration() / 1000.0
            self.left_label.setText(T('Start %s') % self.time_mark(0.0))
            self.right_label.setText(T('End %s') % self.time_mark(duration))
            begins, until = state["in_point"], state["out_point"]
            self.cut_left.setText(T('In point %s') % (begins or "--"))
            self.cut_right.setText(T('Out point %s') % (until or "--"))
            self.cut_middle.setText(self._window_length())

        def track_watch(self):
            """Take over where the picture has run past a boundary.

            The audio runs free once it is put in place, so nothing
            would notice a block ending: it just falls silent. And a
            recording beginning later than the picture stands has to
            come in when its moment arrives. A lookup on every tick,
            acting only on a change.
            """
            if not self.track_blocks:
                return
            path, into, _whose = self.track_where()
            due = into is not None
            playing = (self.track.playbackState()
                        == QtMultimedia.QMediaPlayer.PlayingState)
            # Three reasons to put it right: another block holds this
            # moment; the sound is due and silent; it sounds and is not.
            if ((path or self.track_blocks[0]) != self.track_path
                    or (due and self._should_play and not playing)
                    or (not due and playing)):
                self.track_follow_up()

        def spot(self, ms):
            # Arrived: from here the player's own position is the truth
            # again, and playing on has to move it away from the mark.
            if (self._wanted_ms is not None
                    and abs(ms - self._wanted_ms) <= SPOT_ARRIVED_MS):
                self._wanted_ms = None
            if not self._held:
                self.slider.setValue(ms)
            self.track_watch()
            # Timecode on the left, playback position on the right. With a cut
            # in set it counts from there, negative before it, as in an editor.
            begins = self._limit(state["in_point"])
            rel = (ms - (begins or 0)) / 1000.0
            self.middle.setText("%s   %s%s"
                               % (self.time_mark(ms / 1000.0),
                                  "-" if rel < 0 else "", as_hms(abs(rel))))
            self.show_edges()

        def spot_s(self):
            """Where the player stands, in seconds.

            Where it was sent, until it arrives: a file plays from its
            front while the jump is on its way, and a camera switch
            reading that front loses the moment -- for this switch and
            every one after it, since each counts from the last.
            """
            ms = self.player.position()
            want = self._wanted_ms
            if want is not None and abs(ms - want) > SPOT_ARRIVED_MS:
                return want / 1000.0
            return ms / 1000.0

        def timer_s(self):
            """Return the wall clock time here, or nothing without timecode."""
            if self.tc0 is None:
                return None
            return self.tc0 + self.spot_s()

        def axis_s(self):
            """Return where this file starts on the measured axis."""
            p = self.file_path   # nothing loaded is nowhere on the axis
            return state["axis"].get(path_key(p)) if p else None

        def axis_spot(self):
            """Return the position in the events, from the axis."""
            a = self.axis_s()
            return None if a is None else a + self.spot_s()

        def position(self):
            """Return where we are, by clock and by measured axis.

            Where a file cannot hold the moment -- it begins later --
            the moment kept at the switch answers instead of the front
            of that file, so the next switch lands right again.
            """
            if self._moment is not None and not self.spot_s():
                return self._moment
            return self.timer_s(), self.axis_spot()

        def _title_show(self, text):
            """Show the file name.

            In the heading where there is one, otherwise in the line above the
            picture.
            """
            if self.heading is not None:
                self.heading(text)
            else:
                self.title.setText(text)

        def outside_show(self):
            if self.file_path:
                ffplay_preview(self.file_path, self.spot_s())

        def on_error(self, error, *_):
            """Offer ffplay when Qt cannot handle the format.

            Not automatically: a window opening unasked startles more than it
            helps. A button takes the place of the picture and says why it
            cannot be shown here.
            """
            if error == QtMultimedia.QMediaPlayer.NoError:
                return
            # Once per file and error. Measured 3.9.2026: Qt raised one
            # of these 2590 times in two seconds, because the stop()
            # below fed the play() in loaded(), which raised it again.
            if self._moaned == (self.file_path, str(error)):
                return
            self._moaned = (self.file_path, str(error))
            # What Qt really complains about, in the log: on screen
            # every refusal reads alike, and a file whose picture is
            # fine while only its sound breaks looks exactly like an
            # unknown format. Here the difference survives.
            gui_log("%s refused: %s (code %s)"
                     % (os.path.basename(self.file_path or "-"),
                        self.player.errorString() or "no reason given",
                        error))
            self.player.stop()
            self.video.hide()
            self.extern.show()
            self._title_show(T('%s   --   the app does not know this format')
                               % os.path.basename(self.file_path or ""))

    class NoPlayer(QtWidgets.QWidget):
        """Fallback for a Qt built without multimedia."""

        def __init__(self, parent=None):
            QtWidgets.QWidget.__init__(self, parent)
            position = QtWidgets.QVBoxLayout(self)
            m = label(T('No player is built in here -- playback runs in '
                        'ffplay in its own window.'),
                      COLOURS["quiet"])
            m.setWordWrap(True)
            position.addWidget(m)
            self.cut_bar = QtWidgets.QHBoxLayout()
            position.addLayout(self.cut_bar)
            self.under_cut = QtWidgets.QHBoxLayout()
            position.addLayout(self.under_cut)
            self.heading = None
            self.title = m
            self.file_path = None
            self.tc0 = None
            self.fps = 30.0

        def load(self, file_path, seconds=None, running=False):
            self.file_path = os.path.abspath(file_path)
            ffplay_preview(file_path, seconds or 0.0)

        def now_playing(self):
            return False

        def spot_s(self):
            return 0.0

        def timer_s(self):
            return None

        find_track = None

        def axis_s(self):
            return None

        def axis_spot(self):
            return None

        def spot(self, ms):
            pass

        def jump(self, ms):
            pass

        def window_draw(self):
            pass

        def jump_to(self, text):
            return False

        # The menu binds these directly. Without them the window never
        # gets built on a Qt without multimedia -- the menu is switched
        # off there instead, see *plays*.
        plays = False

        def toggle(self):
            pass

        def faster(self):
            pass

        def pause(self):
            pass

        def nudge(self, seconds):
            pass

    return WindowSlider, VideoSurface, Player, NoPlayer


def make_log_view(QtGui, QtWidgets, Cursor):
    """The log pane of the output tab, once Qt is there.

    Outside gui() for the same reason as the player widgets: a log pane
    is a log pane and has nothing to do with the rest of the layout, and
    a class inheriting from a Qt widget cannot even be defined while the
    script is running on the command line without Qt.
    """
    class LogView(QtWidgets.QTextEdit):
        """The log pane, coloured so the structure is visible.

        Headings get a coloured band, warnings and errors their own
        colour. Otherwise it is a wall of text to search through.

        The colours are the ones of the scheme in force, as everywhere
        else in the window. What is particular here is where they sit:
        in the formats new lines are written in, and in the format
        already sitting on every line written earlier. Neither is a
        style sheet, so ``styles_follow_scheme`` does not reach them,
        and a log is the one thing in the window that cannot simply be
        built again -- it is what a run said. Hence ``colours_apply``,
        which paints what is there rather than making it anew.
        """

        # The kind of a line is kept on the line itself, in the one slot
        # Qt gives a text block for a caller's own use. Reading the kind
        # back out of the wording would tie it to one language, the same
        # reason ``split_kind`` is told the kind rather than guessing it.
        KINDS = ("text", "heading", "good", "warning", "error",
                 "value", "quiet")

        def __init__(self):
            QtWidgets.QTextEdit.__init__(self)
            self.setReadOnly(True)
            self.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
            s = QtGui.QFont("Menlo" if sys.platform == "darwin"
                            else "Consolas", 11 if sys.platform == "darwin"
                            else 9)
            s.setStyleHint(QtGui.QFont.Monospace)
            self.setFont(s)
            self._kind = "text"
            self._formats = {}
            self._formats_build()

        def _formats_build(self):
            """Take the formats from the palette as it stands now."""
            self._formats = {}
            for kind, colour in COLOURS.items():
                f = QtGui.QTextCharFormat()
                f.setForeground(QtGui.QColor(colour))
                if kind in ("heading", "good", "error"):
                    f.setFontWeight(QtGui.QFont.Bold)
                self._formats[kind] = f

        def colours_apply(self):
            """Paint the log in the colours now in force.

            Called when the desktop switches between light and dark.
            The ground under the pane changes with the scheme, so what
            stands on it has to change with it. Measured on 26.8.2026:
            a run written while the desktop was light and then read on
            the dark sheet stood at a contrast of 1.00 -- #222222 on
            #1d232a -- and a heading written after the switch at 1.55,
            #1f4e79 on #233040. That is the dark blue on dark grey in
            the photograph.
            """
            self._formats_build()
            doc = self.document()
            c = QtGui.QTextCursor(doc)
            c.beginEditBlock()
            block = doc.begin()
            while block.isValid():
                self._paint(block, self._kind_of(block))
                block = block.next()
            c.endEditBlock()

        def _kind_of(self, block):
            """What kind of line this is, as it was written down."""
            state = block.userState()
            if 0 <= state < len(self.KINDS):
                return self.KINDS[state]
            return "text"

        def append_text(self, text):
            progress_bar = self.verticalScrollBar()
            below = progress_bar.value() >= progress_bar.maximum() - 4
            c = self.textCursor()
            c.movePosition(Cursor.End)
            for part in re.split(r"(\r|\n)", text):
                if part == "\r":
                    # Progress rewrites the same line over and over.
                    c.movePosition(Cursor.StartOfBlock, Cursor.KeepAnchor)
                    c.removeSelectedText()
                    self._kind = "text"
                elif part == "\n":
                    if c.block().text().strip():
                        self._colourise(c.block())
                        self._kind = "text"
                    c.insertBlock(QtGui.QTextBlockFormat(),
                                  QtGui.QTextCharFormat())
                elif part:
                    if c.block().text():
                        part = strip_marks(part)
                    else:
                        kind, part = split_kind(part)
                        if kind != "text":
                            self._kind = kind
                    if part:
                        c.insertText(part)
            self._colourise(c.block())
            self.setTextCursor(c)
            if below:
                progress_bar.setValue(progress_bar.maximum())

        def _colourise(self, block):
            """Colour a line, and note on it what kind it is."""
            if not block.text().strip():
                return
            kind = self._kind
            block.setUserState(self.KINDS.index(kind)
                               if kind in self.KINDS else 0)
            self._paint(block, kind)

        def _paint(self, block, kind):
            """Put the colours of one kind on one line."""
            if not block.text().strip():
                return
            c = QtGui.QTextCursor(block)
            c.movePosition(Cursor.StartOfBlock)
            c.movePosition(Cursor.EndOfBlock, Cursor.KeepAnchor)
            c.setCharFormat(self._formats.get(kind, self._formats["text"]))
            bf = QtGui.QTextBlockFormat()
            if kind == "heading":
                bf.setBackground(QtGui.QColor(COLOURS["backdrop"]))
            c.setBlockFormat(bf)

    return LogView


def slider_numbers(values):
    """Read the cut sliders as numbers.

    An empty field means the default and a comma means a decimal point --
    typing "1,2" means 1.2 and should not produce an error.

    Returns ({field: (text, number)}, the first field that is not a number, or
    None). The text comes back too because the command line passes it on
    unchanged and the message quotes it.
    """
    out = {}
    for api_key, _b, default_value, _e, _k, _l in CUT_FIELDS:
        raw = str((values or {}).get(api_key, "")).strip()
        raw = raw.replace(",", ".") or default_value
        try:
            out[api_key] = (raw, float(raw))
        except ValueError:
            return out, api_key
    return out, None


def voices_of_values(values):
    """Name -> camera file, out of what the interface holds.

    The window knows a camera by the name of its file; the run wants
    the file. A voice set to "no camera of its own" or left out is not
    in the answer -- it keeps its name in the markers and takes no
    picture.
    """
    where = {}
    for cam in (values.get("cameras") or ()):
        if not cam.get("path"):
            continue
        where[os.path.basename(cam["path"])] = cam["path"]
        if (cam.get("name") or "").strip():
            where[cam["name"].strip()] = cam["path"]
    out = {}
    for row in (values.get("voices") or ()):
        name = (row.get("name") or "").strip()
        pick = row.get("camera") or ""
        if name and pick in where:
            out[name] = where[pick]
    return out


def slider_argv(values):
    """Return the cut sliders as command line switches.

    Returns (switch list, the first field that is not a number, or None). The
    switches for the fields before the bad one are already in the list.
    """
    numbers, bad = slider_numbers(values)
    out = []
    for api_key, _b, _v, _e, _k, _l in CUT_FIELDS:
        if api_key not in numbers:
            break
        out += ["--" + api_key, numbers[api_key][0]]
    for api_key, _b, default_value, allowed, _k, _l in CUT_CHOICES:
        picked = str((values or {}).get(api_key, "")).strip()
        out += ["--" + api_key,
                picked if picked in allowed else default_value]
    return out, bad


def run_argv(values, assignment_file_path=""):
    """Build the command line from what the interface holds.

    This part has nothing to do with Qt: a dict of plain values goes in, a
    list of strings comes out. It decides what a run does, and can be
    tested without opening a window.

    Returns (argv, plan, messages)

      argv      the command line, or None if something is missing
      plan      what goes into the assignment file, or None
      messages  list of (kind, title, text, button) in the order the
                interface should present them. "error" means show and
                abort, "question" means ask and abort on no.

    The order matters: first the query about camera audio, then the checks on
    the assignment, then the key. Answering the first query with no means the
    later messages are never seen.
    """
    messages = []

    def error(title, text):
        messages.append(("error", title, text, ""))
        return None, None, messages

    files = list(values.get("files") or [])
    clip_kind = dict(values.get("clip_kinds") or {})
    # Intro and outro are not cameras: they do not go into the file list but
    # along as their own switch.
    edge = {}
    # One intro and one outro. Two files of the same kind would go into
    # the same switch and the last one would silently win, so the run
    # stops and names the two that are meant.
    doubled = []
    for file_path, kind in sorted(clip_kind.items()):
        switch = ("--intro" if kind == TYPE_INTRO
                  else "--outro" if kind == TYPE_OUTRO else None)
        if switch is None:
            continue
        if switch in edge:
            doubled.append((kind, edge[switch], file_path))
        edge[switch] = file_path
    if doubled:
        kind, first, second = doubled[0]
        return error(
            T('Two files as %s') % label_of(kind),
            T('%s and %s are both set to %s. Only one file can be that '
              '-- please set the other one back to content.')
            % (os.path.basename(first), os.path.basename(second),
               label_of(kind)))
    # Anything set to "ignore this video" does not come along at all.
    off = set(p for p, a in clip_kind.items() if a == TYPE_IGNORED)
    argv = ["videopodcast_magic.py"] + [p for p, _a in files
                                        if p not in edge.values()
                                        and p not in off]
    for switch, file_path in sorted(edge.items()):
        argv += [switch, file_path]
    # The wide shots stay in the file list -- they are cameras, and the
    # run films, aligns and renders them like any other. The switch
    # only says that no speaker belongs to them.
    for file_path in sorted(p for p, a in clip_kind.items()
                            if a == TYPE_WIDE and p not in off):
        argv += ["--wide-shot", file_path]
    if values.get("out_folder"):
        argv += ["--out", values["out_folder"]]
    # No switch means "take it from the source files", the same as on the
    # command line. So the entry that adjusts nothing adds nothing here.
    if values.get("lufs") is not None:
        argv += ["--lufs", "%g" % values["lufs"]]
    if (values.get("speech_language") or "").strip():
        argv += ["--speech-language", values["speech_language"].strip()]
    # Blocks taken out of a recording by hand. Without this the run
    # searches the folder and joins them up again.
    for p in sorted(values.get("apart") or ()):
        argv += ["--apart", p]
    # Files put into a recording by hand. The search would not find them
    # together, so the run has to be told.
    for group in (values.get("together") or ()):
        if len(group) > 1:
            argv += ["--together"] + list(group)
    if values.get("dry_run"):
        argv += ["--dry-run"]

    # The last net under the window's own mark: a voice whose name is
    # on somebody else already. Refused and not asked -- to the cut two
    # voices of one name are one person, and there is nothing sensible
    # to do with the answer "yes, merge them".
    voices = [(r.get("name") or "").strip()
              for r in (values.get("voices") or ())
              if r.get("camera") != IGNORE_AUDIO
              and (r.get("name") or "").strip()]
    twice = sorted(set(n for n in voices if voices.count(n) > 1))
    if twice:
        return error(
            T('One name for two voices'),
            T('%s stands on more than one voice. A name is a person, and '
              'the cut puts a person on one camera -- two voices of one '
              'name would be one person in two places.')
            % ", ".join(twice))

    plan = None
    if values.get("multitrack"):
        only_video = bool(values.get("camera_audio_only"))
        lines = [r for r in (values.get("rows") or [])
                  if r.get("camera_choice") != IGNORE_AUDIO]
        if only_video:
            messages.append((
                "question", T('Cameras only'),
                T('There are no separate audio recordings. Then the audio '
                  'of the %d cameras is used -- each becomes a track, and '
                  'Auphonic removes the bleed.')
                % len(values.get("rows") or []), T('Take the camera audio')))
        if len(lines) < 2:
            return error(
                T('Multitrack needs several tracks'),
                T('Multitrack needs at least two input tracks. A track is '
                  'a recording of its own, a channel of a multichannel '
                  'recorder, or the audio of a video file set to "use the '
                  'audio". Several blocks of the same recording count as '
                  'one, tracks set aside not at all.'))
        names = [(r.get("speakers") or "").strip() for r in lines]
        if not all(names):
            return error(
                T('Speaker names'),
                T('Every row needs a name -- at Auphonic it becomes the '
                  'track ID.'))
        duplicate = sorted(set(n for n in names if names.count(n) > 1))
        if duplicate and len(set(names)) < 2:
            return error(
                T('Only one speaker'),
                T('All rows carry the same name -- that makes a single '
                  'track, and Multitrack needs at least two.'))
        if duplicate:
            messages.append((
                "question", T('Names used more than once'),
                T('These names occur more than once:\n\n  %s\n\nThe recordings '
                  'are merged into one track and laid end to end by their '
                  'timecode. That is right if recording was stopped in '
                  'between.')
                % "\n  ".join(duplicate), T('Merge them')))
        tracks = []
        for r in lines:
            blocks = list(r.get("blocks") or [])
            target = r.get("camera_choice") or ""
            full = ""
            for p, a in files:
                if a == "video" and os.path.basename(p) == target:
                    full = p
                    break
            camera_track = bool(r.get("own_audio"))
            # Two different things, kept apart: where the audio comes from,
            # and which camera the speaker is on. For a clip-on microphone
            # plugged into one camera they need not be the same -- the
            # person may well be filmed by another one.
            source = r.get("from_camera") or ""
            straight = bool(blocks) and os.path.splitext(
                blocks[0])[1].lower() in VIDEO_SUFFIXES
            entry = {"audio": blocks[0] if blocks else "",
                       "blocks": blocks,
                       "speakers": (r.get("speakers") or "").strip(),
                       "camera": full,
                       "camera_audio": bool(only_video or
                                            (camera_track and straight))}
            if camera_track or only_video:
                if not full:
                    # No camera picked: the track belongs to the one it
                    # came out of.
                    entry["camera"] = os.path.abspath(source or (
                        blocks[0] if blocks else ""))
                entry["from_camera"] = os.path.abspath(
                    source or (blocks[0] if blocks else ""))
                # What the background thread has already fetched the run
                # need not fetch again.
                if r.get("audio_done"):
                    entry["audio_done"] = r["audio_done"]
            tracks.append(entry)
        cameras = [{"video": cam.get("path"),
                    "name": (cam.get("name") or "").strip()
                    or os.path.splitext(os.path.basename(
                        cam.get("path") or ""))[0]}
                   for cam in (values.get("cameras") or [])]
        if len(set(cam["name"] for cam in cameras)) != len(cameras):
            return error(
                T('File names'),
                T('Two cameras would produce the same new file. Please '
                  'give different names.'))
        plan = {"format": FILE_FORMAT,
                "created_by": "videopodcast-magic %s" % VERSION,
                "production": (values.get("production") or "").strip()
                or 'Production', "tracks_of": tracks, "cameras": cameras}
        # What the separation heard travels with the assignment. Raw and
        # in the time of its own file -- the run puts it on the axis.
        if separation_has_voices(values.get("speakers_of")):
            plan["speakers_of"] = values["speakers_of"]
            # And which camera each voice belongs to. The simple path
            # has sent this along since it learned to cut; multitrack
            # never did, so the run knew the voices and not where they
            # sit.
            plan["voices_of"] = voices_of_values(values)
        argv += ["--multitrack", "--assign", assignment_file_path]
        if values.get("speakers_wanted") is False:
            argv += ["--no-speakers-local"]
    elif separation_has_voices(values.get("speakers_of")) \
            and assignment_file_path:
        # One track, and the voices in it already told apart. It
        # travels the way the multitrack path sends it, so the run does
        # not spend the minutes twice -- and with it which camera each
        # voice belongs to, which only the window knows. The sliders go
        # too: since 24.8.2026 this path cuts as well, and numbers that
        # do not reach the run are numbers that do nothing.
        plan = {"format": FILE_FORMAT,
                "created_by": "videopodcast-magic %s" % VERSION,
                "speakers_of": values["speakers_of"],
                "voices_of": voices_of_values(values)}
        argv += ["--speakers-from", assignment_file_path]
    if values.get("speakers_wanted") is False \
            and not values.get("multitrack"):
        argv += ["--no-speakers-local"]

    # The time window and the cut numbers belong to every run, not only
    # to the two that carry an assignment file. They hang on no
    # speaker: In point and Out point are a window over the material,
    # and docs/simple-path.md promises them to the simple way in so
    # many words. The cut numbers are what the preview beside them is
    # computed from, and a preview that is computed from other numbers
    # than the run uses is worse than none.
    #
    # Until 2.10.1-beta these sat inside the two branches above. On the
    # third way -- no Multitrack, no separation in the window -- In
    # point, Out point, the numbers, the choices and the wide shot tick
    # all stayed in the window, the run cut with the built-in defaults,
    # and nothing said so.
    if (values.get("in_point") or "").strip():
        argv += ["--in-point", values["in_point"].strip()]
    if (values.get("out_point") or "").strip():
        argv += ["--out-point", values["out_point"].strip()]
    part, bad = slider_argv(values.get("cut"))
    if bad:
        return error(
            T('Camera cut'),
            T('%r is not a number.') % (values.get("cut") or {})[bad])
    argv += part
    if not values.get("wide_at_edges"):
        argv += ["--no-wide-edges"]

    # Finished tracks lie in a folder, and nothing is sent anywhere to
    # use them. This used to hang inside "if key:", so a run without a
    # key never saw the folder -- the same lock as on the command line,
    # found on 23.8.2026 while opening that one.
    if values.get("done_folder"):
        argv += ["--auphonic-done", values["done_folder"]]

    key = (values.get("key") or "").strip()
    if key:
        selected = (values.get("preset") or "").strip()
        if not selected:
            return error(
                T('Preset missing'),
                T('Load Presets and pick one, or leave the API Key empty.'))
        argv += ["--auphonic-api-key", key, "--auphonic-preset", selected]
        # Only with a key: without auphonic.com there is nobody to
        # transcribe, and the switch would promise something that
        # cannot happen.
    elif values.get("multitrack"):
        # No key, no preset: it runs locally. Everything that only
        # auphonic.com can do is missing, and the run says so.
        argv += ["--without-auphonic"]
    return argv, plan, messages


def speakers_to_cameras(assign_lines, voice_lines, voiced=()):
    """Who is on which camera, out of the two tables that say so.

    *assign_lines* are the recording rows, *voice_lines* the voices a
    separation found under one of them, *voiced* the recordings whose
    voices stand underneath.

    The assignment has exactly one level. Where the voices of a
    recording stand under it, they carry the camera and the recording
    does not -- two answers one above the other could say different
    things about the same camera. Two voices on one camera are one
    condition and not two; segments_per_camera folds them together.
    """
    where_to = {}
    for chain, name_value, camera_value in assign_lines:
        if os.path.abspath(chain[0]) in (voiced or ()):
            continue
        n = name_value.get()
        if n and camera_value.get() != IGNORE_AUDIO:
            where_to[n] = camera_value.get()
    for _label, name_value, camera_value in voice_lines:
        n = name_value.get().strip()
        if n and camera_value.get() != IGNORE_AUDIO:
            where_to[n] = camera_value.get()
    return where_to


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
    chooser.addItem(T('The language of the system (%s)')
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
        T('Both are asked once and then stay. The key goes into the %s, '
          'never into a file.') % keep_where, COLOURS["quiet"]))
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


def restore_entry(act, where, window):
    """Put the way back into the menu, where there is one to go back to.

    Nothing at all where no update has left an .old beside the program:
    greyed out would be a promise that cannot be kept. Read once, when
    the menu is built -- going back starts the program over, so this
    entry never outlives the file it names.
    """
    kept = old_self_file()
    if not kept:
        return
    back = version_in_file(kept)
    act(where, (T('Back to %s') % back) if back
        else T('Back to the kept version'), lambda: restore_offer(window))


# --- Helpers that hold nothing from gui() -----------------
# Measured with co_freevars on 23.8.2026: not one of these
# reaches into gui(). They lived inside it out of habit, and
# 158 lines of the biggest function in the file were the
# price. Out here a test can call them directly instead of
# cutting them out of the source and exec-ing a copy, which
# is what two of them used to need.

def zoom_button(QtWidgets, text, tip, does):
    """One of the small buttons that zoom the band."""
    b = QtWidgets.QToolButton()
    b.setText(text)
    b.setAutoRaise(True)
    b.setFixedWidth(caption_room(b, 24))
    hint(b, tip)
    b.clicked.connect(does)
    return b


def hint(widget, text):
    widget.setToolTip(text)
    return widget

def speaks_as(widget, what, row_name=""):
    """Give a field a name a screen reader can say.

    A field in a table cell is read out as its kind and nothing
    else -- "combo box", "edit field". Which column and which row
    it sits in is on the screen only, so it is said here as well.
    """
    widget.setAccessibleName("%s -- %s" % (what, row_name)
                             if row_name else what)
    return widget

# How narrow the name field may get. It is typed into, so it is the one
# column that must not give way: Qt lets a stretching column fall to
# 16 px and says nothing, and on the Windows builder this one went to
# 79 px at the narrowest window while everything still "fitted".
NAME_COLUMN_LEAST = 160


def split_column_room(widget):
    """How wide the Speakers column has to be for what it will hold.

    Not for what stands in it: it is filled minutes later, when a
    separation reports, and a column that measures its contents
    measured an empty one. Measured in the font that draws, over the
    two captions that must not wrap -- the running one, which shares
    the cell with the button, and the finished count.
    """
    from PySide6 import QtWidgets as _qw
    mark = _qw.QLabel("")
    mark.setFont(widget.font())
    button = _qw.QPushButton(T('Stop'))
    button.setFont(widget.font())
    running = caption_room(mark, 0, [T('Separating ...'),
                                     T('Stopping ...')])
    done = caption_room(mark, 0, [TN(2, 'Separated: %d speaker',
                                     'Separated: %d speakers') % 2])
    return max(running + button.sizeHint().width() + 6, done) + 12


def split_column_fit(tree, column, stretch=1, least=NAME_COLUMN_LEAST):
    """Give the Speakers column its width, and the rest to the names.

    Out of the window, so it cannot drift from what is drawn. What is
    left over is handed out here rather than by a stretching column,
    and never below *least*: a stretching one falls as far as Qt likes
    -- 79 px on the Windows builder, in the field a name is typed into.
    Where that will not fit, the tree scrolls, which is the lesser harm.
    """
    from PySide6 import QtCore as _qc
    from PySide6 import QtWidgets as _qw
    head = tree.header()
    head.setStretchLastSection(False)
    head.setSectionResizeMode(stretch, _qw.QHeaderView.Interactive)
    tree.setColumnWidth(column, split_column_room(tree))
    others = [c for c in range(head.count()) if c != stretch]
    # What the column was asked for before the room was shared out. It
    # never goes below that again: the leftover can be nothing at all,
    # and a column handed nothing is a field with no name in it.
    asked = max(least, tree.columnWidth(stretch))

    def share_out():
        free = tree.viewport().width() - sum(tree.columnWidth(c)
                                             for c in others)
        tree.setColumnWidth(stretch, max(asked, free))

    tree._share_out = share_out

    class ShareWithWindow(_qc.QObject):
        """Hand the name column the room left over as the window moves."""

        def eventFilter(self, watched, what):
            if what.type() == _qc.QEvent.Resize:
                tree._share_out()
            return False

    if not hasattr(tree, "_share"):
        tree._share = ShareWithWindow(tree)
        tree.viewport().installEventFilter(tree._share)
    share_out()
    return tree.columnWidth(column)


def cells_laid_out(cells):
    """Give every cell the height its text needs, and lay the rows out.

    A wrapping label offers a height worked out at a width of its own
    choosing. Here that offer comes out right; on the Windows builder
    it came out 14 px under what the text needed and a line went
    missing. So the height is not left to the offer: the width is read
    off the laid-out label and the height demanded from it. Twice
    round, because the first pass is what gives the label its width.
    """
    view = cells_are_shown_in(cells)
    if view is None:
        return False
    view.doItemsLayout()
    moved = False
    for _path, _button, mark, _item in list(cells or ()):
        # Let go of last time's height before asking again: a label
        # counts its own minimum into the answer, so an emptied cell
        # would still say it needs four lines. An empty one answers
        # -1, which is no height at all.
        was = mark.minimumHeight()
        mark.setMinimumHeight(0)
        needs = max(0, mark.heightForWidth(max(1, mark.width())))
        if needs:
            mark.setMinimumHeight(needs)
        moved = moved or needs != was
    if moved:
        view.doItemsLayout()
    return True


def cells_are_shown_in(cells):
    """The view those cells stand in, or None where there is not one.

    The way out of a cell and back to the whole: tree_build makes the
    view the model's parent, so any one item knows where it is drawn.
    """
    for _path, _button, _mark, item in list(cells or ()):
        model = item.model()
        view = model.parent() if model is not None else None
        if hasattr(view, "doItemsLayout"):
            return view
    return None


def split_cell_build(path, on_stop, item):
    """The Speakers cell of one recording: its state, and a way out.

    Nothing here starts a separation -- that is answered in the name
    field of the same row -- so the cell only says what came of it and
    carries the button that breaks a running one off. Returns the cell
    and what has to be reached again while a run goes on: the button,
    the label, and the row's own item, which is the way from here back
    to the view that has to measure the row again.
    """
    from PySide6 import QtWidgets as _qw
    box = _qw.QWidget()
    row = _qw.QHBoxLayout(box)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(6)
    button = _qw.QPushButton(T('Stop'))
    speaks_as(button, T('Stop'), os.path.basename(path))
    button.clicked.connect(lambda *_, x=path: on_stop(x))
    button.setVisible(False)
    mark = label("", COLOURS["quiet"])
    # Word wrap, because the cell is written to again after the column
    # was measured: a reason the separation could not run is hundreds
    # of pixels wide, and two lines are better than a cut one. Making
    # room for the second line is cells_laid_out's business.
    mark.setWordWrap(True)
    row.addWidget(mark, 1)
    row.addWidget(button)
    return box, (path, button, mark, item)


def typed_part(new, old):
    """What somebody typed, out of a caption they typed into.

    A combo box showing a picked entry does not replace its caption
    when the next letter arrives, it edits it: typing "A" into "several
    speakers" with the cursor after "sev" leaves "sevAeral speakers".
    The letter is what was meant, so the caption is taken back out --
    by the head and the tail the two strings still share, which finds
    it wherever the cursor happened to be.
    """
    head = 0
    while head < len(new) and head < len(old) and new[head] == old[head]:
        head += 1
    tail = 0
    while (tail < len(new) - head and tail < len(old) - head
           and new[-1 - tail] == old[-1 - tail]):
        tail += 1
    return new[head:len(new) - tail]


def speaker_name_cell(name_value, several_value, short):
    """The name field of one recording: a name, or "several speakers".

    One question -- who is to be heard on this recording? -- with three
    answers rather than a field beside a button. A name typed in says
    the recording is that one person. The one entry that can be picked
    instead says there are several, and the machine goes and tells them
    apart; the names then belong in the rows underneath.

    Picking a name again is allowed and costs nothing: the voices are
    hidden, not thrown away. A separation of 87 minutes takes three of
    them, and a mis-click must not be that expensive.

    What the file name suggests the person is called comes off the
    value itself and stands in the empty field in grey. It is never
    written in: a guess that is written in is a guess nobody checks,
    and "Zoom0004" would go into the mix as a speaker name. The field
    starts empty and stays empty until somebody answers.
    """
    from PySide6 import QtWidgets as _qw
    from PySide6.QtCore import Qt as _qt
    box = _qw.QComboBox()
    box.setEditable(True)
    box.setInsertPolicy(_qw.QComboBox.NoInsert)
    box.addItem(label_of(SEVERAL_SPEAKERS), SEVERAL_SPEAKERS)
    # On the entry itself, not only on the field: the field's own hint
    # is gone the moment the list is open, which is exactly when
    # somebody is deciding whether to pick this.
    box.setItemData(0, T('Separates the recording by voice: every voice '
                         'gets a row of its own, and its camera in it. '
                         'About one minute for half an hour of audio, on '
                         'this machine and without an upload.'),
                    _qt.ToolTipRole)
    box.lineEdit().setPlaceholderText(
        str(getattr(name_value, "suggested", "")))
    speaks_as(box, T('Speaker name'), short)
    hint(box, T('Who is to be heard on this recording. A name means it '
                'is that one person.\n"several speakers" works out who '
                'speaks when, on this machine and without an upload -- '
                'about one minute for half an hour of audio. The names '
                'then go in the rows underneath.'))
    # True from the first letter until the typing is over. Answering
    # "one name, not several" rebuilds the whole sheet, and the field
    # being typed in is part of the sheet: given per keystroke, the
    # answer destroyed this very widget after the first letter, nothing
    # took the focus back, and the speaker was left called "A".
    typing = [False]

    def show_now():
        # Not while somebody is typing. Every letter reaches name_value,
        # which calls this, which would write the value back over the
        # word being written -- or, while the answer still reads
        # "several speakers", write that caption over it.
        if typing[0]:
            return
        if several_value.get():
            box.setCurrentIndex(0)
        else:
            box.setCurrentIndex(-1)
            box.setEditText(str(name_value.typed()))

    def picked(_i=0):
        # Picked from the list, so the typing is over with the click.
        # This way stays immediate: the rows underneath should appear
        # on the click and not after a detour through the field.
        typing[0] = False
        several_value.set(box.currentData() == SEVERAL_SPEAKERS)

    def typed(text):
        # textEdited and not textChanged: the second one fires when the
        # picked entry writes its own caption into the field, and the
        # answer would undo itself in the same breath.
        if not typing[0] and several_value.get():
            # The first letter on a field that was showing "several
            # speakers". Qt has just edited that caption rather than
            # replaced it, so the caption comes back out and only what
            # was typed stays.
            typing[0] = True
            text = typed_part(text, label_of(SEVERAL_SPEAKERS))
            box.setEditText(text)
        typing[0] = True
        name_value.set(text)

    def settled():
        """The typing is over: only now is the answer given."""
        if not typing[0]:
            return
        typing[0] = False
        several_value.set(False)
        show_now()

    show_now()
    box.activated.connect(picked)
    box.lineEdit().textEdited.connect(typed)
    box.lineEdit().editingFinished.connect(settled)
    name_value.listen(show_now)
    several_value.listen(show_now)
    return box


def voice_row_cells(name_value, camera_value, targets, caption):
    """One voice's two fields: what it is called and where it goes.

    The row stands under the recording it was heard in, so it repeats
    neither the file name nor the two times. Those times were pulled
    apart on 25.8.2026 -- how long the voice speaks and where its
    longest passage lies had been one number that read like a
    timestamp -- and that was the right answer to the wrong question:
    neither belongs on screen. The longest passage is still worked out,
    because it is where a click on the row takes the player. It is
    simply not written down, and the column stays narrow.

    Returns (name field, camera chooser).
    """
    from PySide6 import QtWidgets as _qw
    field = field_bind(_qw.QLineEdit(), name_value)
    speaks_as(field, T('Speaker name'), caption)
    box = _qw.QComboBox()
    speaks_as(box, T('belongs to'), caption)
    fill_choices(box, targets, camera_value.get())
    box.currentIndexChanged.connect(
        lambda *_: camera_value.set(box.currentData()))

    def name_useful():
        """Grey the name out where it cannot do anything.

        A voice set to "do not use" is out of the mix and out of the
        transcript, so a name for it is an entry without effect. It is
        greyed, not emptied: switching back must not cost the typing.

        Only "do not use" does this. "No camera of its own" means the
        person is in the mix and in the transcript, and there the name
        works -- greying it there would take away a setting that has
        an effect.

        The row stays selectable, which is what plays the voice: a
        disabled field lets the click through to the view under it,
        and that is the very tool somebody decides with. And the
        greying needs no reason written beside it, because the reason
        stands two fields along in the same row.
        """
        field.setEnabled(camera_value.get() != IGNORE_AUDIO)

    camera_value.listen(name_useful)
    name_useful()
    # So that nothing has to tell a voice from its recording by the
    # wording of a caption: whoever reads these rows can ask the field
    # itself which of the two levels it belongs to.
    for w in (field, box):
        w.setObjectName("voice")
    return field, box


def more_speakers_row(audio_file_list, on_pick):
    """The row that asks for one speaker more than was found.

    Every recording can be listened to again, whether anything was
    found in it or not: whoever hears a fourth person knows it before
    the program does. One button per recording put the player on the
    right over the edge of the window from three recordings on, and
    there can be seven -- so with more than one recording the name
    moves off the button and into a chooser beside it, and the row
    stays the same width whatever the material.
    """
    from PySide6 import QtWidgets as _qw
    if not audio_file_list:
        return None
    more = _qw.QWidget()
    more_row = _qw.QHBoxLayout(more)
    more_row.setContentsMargins(0, 0, 0, 0)
    if len(audio_file_list) == 1:
        only = audio_file_list[0]
        button = _qw.QPushButton()
        # The whole name first, at the ordinary size. Only if that is
        # too wide does the type get smaller, and only then is the
        # name shortened -- the elision has to be measured in the font
        # the button really draws with.
        button.setText(T('One more speaker in %s') % os.path.basename(only))
        font_smaller_if_wide(button, 2, ROW_ROOM)
        if button.sizeHint().width() > ROW_ROOM:
            button.setText(T('One more speaker in %s')
                           % short_name(button, os.path.basename(only),
                                        NAME_ROOM))
        button.clicked.connect(lambda *_, x=only: on_pick(x))
        more_row.addWidget(button)
    else:
        which = _qw.QComboBox()
        for path in audio_file_list:
            which.addItem(os.path.basename(path), path)
        which.setSizeAdjustPolicy(_qw.QComboBox.AdjustToContents)
        button = _qw.QPushButton(T('One more speaker in'))
        # Button and chooser together have to fit; measured as a pair,
        # and shrunk as a pair or not at all -- two different sizes
        # side by side look like a mistake.
        if (button.sizeHint().width()
                + min(which.sizeHint().width(), NAME_ROOM) > ROW_ROOM):
            font_smaller(button, 2)
            font_smaller(which, 2)
        # The width comes after the type is settled, in the font the
        # box really draws with, and it comes from the names rather
        # than from a count of characters. Measured offscreen at this
        # Mac's system font, 31.8.2026: a name of 27 letters wants 288
        # px and the box can give its text 216, so that one is
        # shortened and shorter names beside it are not.
        box_names_fit(which, NAME_ROOM)
        button.clicked.connect(lambda *_, b=which: on_pick(b.currentData()))
        more_row.addWidget(button)
        more_row.addWidget(which)
    hint(button, T('Listens to that recording again, looking for one '
                   'speaker more than was found.'))
    more_row.addStretch(1)
    return more


QT_WORDS = []   # Qt's own translator, kept alive for as long as the window is


def mac_menu_name(name):
    """Put the program's name in the macOS menu bar; report whether it took.

    The first menu on a Mac carries the name of the running program, and
    that name does not come from Qt. It comes from CFBundleName in the
    bundle around the executable -- and a script started with python3
    has no bundle of its own, so it borrows the one Python lives in.
    Measured on this Mac, 30.8.2026: the entry read "Python", and every
    menu said so.

    setApplicationName does not reach it; only the bundle does. So the
    entry is written, through the Objective-C runtime, before the
    application is built -- afterwards the menu is already drawn.
    """
    if sys.platform != "darwin":
        return False
    try:
        import ctypes, ctypes.util
        objc = ctypes.cdll.LoadLibrary(ctypes.util.find_library("objc"))
        objc.objc_getClass.restype = ctypes.c_void_p
        objc.sel_registerName.restype = ctypes.c_void_p

        def send(obj, what, *args, types=()):
            call = ctypes.cast(objc.objc_msgSend, ctypes.CFUNCTYPE(
                ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, *types))
            return call(obj, objc.sel_registerName(what.encode()), *args)

        strings = ctypes.c_void_p(objc.objc_getClass(b"NSString"))

        def text_of(value):
            return ctypes.c_void_p(send(strings, "stringWithUTF8String:",
                                        value.encode(),
                                        types=(ctypes.c_char_p,)))

        bundle = ctypes.c_void_p(objc.objc_getClass(b"NSBundle"))
        info = ctypes.c_void_p(send(ctypes.c_void_p(
            send(bundle, "mainBundle")), "infoDictionary"))
        send(info, "setObject:forKey:", text_of(name),
             text_of("CFBundleName"),
             types=(ctypes.c_void_p, ctypes.c_void_p))
        return True
    except Exception:
        # An older macOS, a bundled build that already carries its name,
        # or a runtime that will not be talked to. The menu then says
        # what it said before, and nothing else is worse for it.
        return False


def total_paint(Qt, plan, total_state, total_bar, total_line):
    """Draw the whole run's progress bar, or take it away when it is over.

    Outside gui() because it reaches into nothing of its own: the plan it
    reads and the two widgets it writes to come in as arguments.
    """
    if plan.busy():
        total_state["full_since"] = 0.0
        plan.creep(0.2)
        total_bar.setValue(int(round(1000 * plan.total())))
        fitted(Qt, total_line, plan.line())
        total_bar.show()
        total_line.show()
        return
    if not plan.order:
        return
    # Finished: full for a moment, so the end is seen, then away.
    total_bar.setValue(1000)
    total_line.setText(T('done'))
    if not total_state["full_since"]:
        total_state["full_since"] = time.time()
    elif time.time() - total_state["full_since"] > 1.5:
        plan.clear()
        total_bar.hide()
        total_line.hide()


def digits_font(QtGui, widget):
    """The system's typewriter face, at the size the widget is drawn in.

    For readings made of digits. In a proportional face the columns
    shift about as the digits change, and a time that moves while it
    counts is read as the layout moving, not the clock.
    """
    font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
    font.setPointSize(max(9, widget.font().pointSize()))
    # The hint, because the name is not always one this machine knows:
    # a windowless Qt answers the Linux alias "monospace" everywhere,
    # and without the hint the text falls back to the interface face --
    # which is not fixed width, and measures 12 per cent narrower.
    font.setStyleHint(QtGui.QFont.Monospace)
    return font


def total_hide(plan, total_state, total_bar, total_line):
    """Take the bar away: what it was counting is not being done.

    Clearing the plan is not enough. The widget goes on showing the
    figure it was last given until the timer draws again, and
    total_paint only hides it after a step has finished -- which is
    what does not happen when work is called off. Outside gui() beside
    total_paint, and for the same reason: it touches nothing of its own.
    """
    plan.clear()
    total_state["full_since"] = 0.0
    total_bar.setValue(0)
    total_line.setText("")
    total_bar.hide()
    total_line.hide()


def measuring_stop(state, paths, prework_clean_up, split_stop, split_run,
                   hide_bar):
    """Call off everything measuring a list that is about to go.

    Four strands go on reading the files otherwise, and their answers
    arrive in a window that has nothing to do with them. Each carries
    its own way of being called off already -- a queue to empty, a
    number saying which list it belongs to -- and this is the one place
    that uses all of them. The prework goes first: it takes the files
    off the bar, which is wiped after.
    """
    prework_clean_up(paths)
    for counted in ("preflight_run", "axis_run", "speakers_run"):
        state[counted] = state.get(counted, 0) + 1
    state["axis_running"] = False
    split_stop()
    split_run["busy"] = False
    # What split_stop wrote into the row goes with it: "Stopping ..."
    # must not be the last thing said about a production that is no
    # longer open.
    state["split_note"] = None
    state["speakers_running"] = ""
    hide_bar()


def qt_own_words(QtCore, app):
    """Give Qt its own texts in the chosen language.

    "Preferences", "Quit", "Services" and the buttons in the file dialog
    are Qt's words, not ours, so they stay English however much of our
    own text is translated -- on a Mac the whole first menu was English
    in a German window. Qt brings them translated and only has to be
    told to use them. Kept in a list afterwards: Qt holds no reference,
    so a translator that goes out of scope changes nothing.
    """
    words = QtCore.QTranslator()
    if words.load("qtbase_" + PROGRAM.LANG, QtCore.QLibraryInfo.path(
            QtCore.QLibraryInfo.LibraryPath.TranslationsPath)):
        app.installTranslator(words)
        QT_WORDS.append(words)
        return True
    return False


def say_dialog(QtWidgets, window, title, text, do_text="", no_text=""):
    """One message box, with one button or with two.

    With do_text it is a question and gives back whether the action was
    chosen; without it, a message with nothing to decide. The buttons
    carry the action rather than yes and no, so nobody has to read the
    question backwards to know what will happen.
    """
    d = QtWidgets.QDialog(window)
    d.setWindowTitle(title)
    d.setMinimumWidth(720 if do_text else 620)
    position = QtWidgets.QVBoxLayout(d)
    position.setContentsMargins(18, 16, 18, 14)
    position.setSpacing(14)
    position.addWidget(label(title, COLOURS["heading"], True, 15))
    m = label(text)
    m.setWordWrap(True)
    m.setMinimumWidth(660 if do_text else 560)
    position.addWidget(m)
    bar = QtWidgets.QHBoxLayout()
    position.addLayout(bar)
    # Both buttons to the right, the action outermost and preselected --
    # the way the system does it.
    bar.addStretch(1)
    if do_text:
        no_button = QtWidgets.QPushButton(no_text)
        no_button.clicked.connect(d.reject)
        bar.addWidget(no_button)
    yes_button = QtWidgets.QPushButton(do_text or T('Close'))
    yes_button.clicked.connect(d.accept)
    yes_button.setDefault(True)
    yes_button.setAutoDefault(True)
    bar.addWidget(yes_button)
    return d.exec() == QtWidgets.QDialog.Accepted


def label(text, colour=None, bold=False, large=0):
    """A piece of text on the screen, in the colour it belongs in."""
    from PySide6 import QtWidgets as _qw
    widget = _qw.QLabel(text)
    style = []
    if colour:
        style.append("color: %s" % colour)
    if bold:
        style.append("font-weight: bold")
    if large:
        style.append("font-size: %dpx" % large)
    if style:
        widget.setStyleSheet(";".join(style))
    return widget

def font_smaller(widget, less=1):
    """Set a widget's font that many points below the application's.

    Through the font and not through a style sheet: a fixed size in
    a style sheet ignores whatever the system font is set to, and
    then reads as tiny on one machine and as normal on the next.
    """
    from PySide6 import QtWidgets as _qw
    f = _qw.QApplication.font()
    if f.pointSizeF() > 0:
        f.setPointSizeF(max(6.0, f.pointSizeF() - less))
    else:
        f.setPixelSize(max(8, f.pixelSize() - less))
    widget.setFont(f)
    return widget

def font_smaller_if_wide(widget, less, room):
    """Shrink the type only where the widget is wider than *room*.

    Smaller type is a cost, not a free win: it is harder to read,
    and on a machine whose system font was turned up it undoes
    exactly what somebody set it for. So it is taken where the row
    would otherwise push the sheet wider than the player leaves
    it, and nowhere else.
    """
    if widget.sizeHint().width() <= room:
        return widget
    return font_smaller(widget, less)

def short_name(widget, text, room):
    """Shorten a file name to the room there is, from the middle.

    Both ends of a file name carry what tells two of them apart --
    the take at the front, the channel at the back -- so what goes
    is the middle. The width is measured in the font the widget
    actually draws with.
    """
    from PySide6 import QtCore as _qc
    return widget.fontMetrics().elidedText(text, _qc.Qt.ElideMiddle, room)

def box_names_fit(box, room):
    """Give a chooser of file names the width it needs, up to *room*.

    A chooser asks for as much as its widest entry needs and no more
    than *room*; what it cannot get, it takes off the name. Qt takes it
    off the end, and the recordings of one session differ at the end --
    cut there, three of them read alike. So where the room is not
    enough, every entry is shortened in the middle instead, and the
    whole name stays reachable as a tooltip: on the entry in the open
    list, and on the box itself for the one that is chosen.

    Nothing is shortened while the room is enough. An unshortened name
    is worth more than a uniform look.
    """
    from PySide6 import QtCore as _qc
    want = widget_width(box)
    box.setMinimumWidth(min(want, room))
    box.setMaximumWidth(room)
    if want <= room:
        return box
    whole = [box.itemText(i) for i in range(box.count())]
    for i, name in enumerate(whole):
        # The arrow sits inside the box and takes room off the text;
        # the same allowance widget_width measures with.
        box.setItemText(i, short_name(box, name, room - 44))
        box.setItemData(i, name, _qc.Qt.ToolTipRole)

    def whole_name(*_):
        """Put the chosen name, unshortened, on the box."""
        i = box.currentIndex()
        box.setToolTip(whole[i] if 0 <= i < len(whole) else "")

    box.currentIndexChanged.connect(whole_name)
    whole_name()
    return box

def field_bind(field, value, width=None):
    """Bind an input field and a value so each follows the other.

    The field shows the answer and not the name behind it: a value
    that carries a suggestion offers it in grey, which is where a
    guess belongs and where it can be overruled by typing over it.
    """
    field.setText(str(value.typed()))
    if getattr(value, "suggested", ""):
        field.setPlaceholderText(str(value.suggested))
    if width:
        field.setFixedWidth(width)
    field.textChanged.connect(lambda t: value.set(t))

    def follow_up():
        if field.text() != str(value.typed()):
            field.setText(str(value.typed()))

    value.listen(follow_up)
    return field

def choice_bind(box, value, allowed):
    """Bind a drop-down and a value; *allowed* are the stored names.

    The list shows the translated names, the value keeps the name
    the switch carries -- a project written on a German machine has
    to read the same on an English one.
    """
    for name in allowed:
        box.addItem(T(SHOT_NAMES.get(name, name)), name)
    box.setCurrentIndex(max(0, list(allowed).index(value.get())
                            if value.get() in allowed else 0))
    box.currentIndexChanged.connect(
        lambda i: value.set(box.itemData(i)))

    def follow_up():
        if box.currentData() != value.get() and value.get() in allowed:
            box.setCurrentIndex(list(allowed).index(value.get()))

    value.listen(follow_up)
    return box

def cut_fields_build(into, parts=None):
    """Build the numbers and the choices of the cut box.

    Out here rather than inside the window, which is long enough
    without sixty lines of grid. It is a builder and nothing else: the
    values it makes are handed back, and what listens to them is the
    window's business.

    Returns {command line name: Value}, in the order CUT_FIELDS and
    CUT_CHOICES stand in, which is the order they are read in.

    *parts* is filled with {command line name: (row, field or box)} for
    whoever has to grey a setting out later. Handed over rather than
    returned, so the one thing this builds stays the one thing it
    returns and the callers that want none of it change nothing.
    """
    parts = {} if parts is None else parts
    from PySide6 import QtWidgets as _qw
    from PySide6.QtCore import Qt as _qt
    cut_var = {}
    field_grid = _qw.QGridLayout()
    into.addLayout(field_grid)
    # The rhythm first, the wide shot after it, and the question last --
    # its seconds stand directly above "After a question", which is the
    # first of the choices below. At half the width the sliders no
    # longer fit side by side.
    apart_ = ("wide", "reaction")
    ordered = ([f for f in CUT_FIELDS
                if not f[0].startswith(apart_)]
               + [f for f in CUT_FIELDS if f[0].startswith("wide")]
               + [f for f in CUT_FIELDS if f[0].startswith("reaction")])
    for idx, (api_key, caption, default_value, unit, short,
              long) in enumerate(ordered):
        line = _qw.QWidget()
        row_layout = _qw.QHBoxLayout(line)
        row_layout.setContentsMargins(0, 0, 18, 0)
        m = label(T(caption))
        m.setFixedWidth(cut_caption_room(m, 140))
        row_layout.addWidget(m)
        value = Value(default_value)
        cut_var[api_key] = value
        field = field_bind(_qw.QLineEdit(), value, 56)
        field.setAlignment(_qt.AlignRight)
        # The caption stands to the left of the field and the unit
        # to the right of it; neither is read out with the field, so
        # both are said here.
        speaks_as(field, T('%s, seconds') % T(caption)
                  if unit == "s" else T(caption))
        row_layout.addWidget(field)
        t = label("%s  %s" % (unit, T(short)), COLOURS["quiet"])
        row_layout.addWidget(t)
        row_layout.addStretch(1)
        for _w in (line, m, field, t):
            hint(_w, T(long))
        field_grid.addWidget(line, idx, 0)
        parts[api_key] = (line, field)
    # Below the numbers: the cases where the speech does not say who
    # belongs on screen, and what is shown instead. They sit here and
    # not in the settings window because they change the cut, and the
    # cut is what this tab is about.
    choice_grid = _qw.QGridLayout()
    into.addLayout(choice_grid)
    for idx, (api_key, caption, default_value, allowed, short,
              long) in enumerate(CUT_CHOICES):
        line = _qw.QWidget()
        row_layout = _qw.QHBoxLayout(line)
        row_layout.setContentsMargins(0, 0, 18, 0)
        m = label(T(caption))
        m.setFixedWidth(cut_caption_room(m, 140))
        row_layout.addWidget(m)
        value = Value(default_value)
        cut_var[api_key] = value
        box = choice_bind(_qw.QComboBox(), value, allowed)
        box.setFixedWidth(cut_choice_room(box, 150))
        speaks_as(box, T(caption))
        row_layout.addWidget(box)
        t = label(T(short), COLOURS["quiet"])
        row_layout.addWidget(t)
        row_layout.addStretch(1)
        for _w in (line, m, box, t):
            hint(_w, T(long))
        choice_grid.addWidget(line, idx, 0)
        parts[api_key] = (line, box)
    return cut_var


def checkbox_bind(checkbox, value):
    checkbox.setChecked(bool(value.get()))
    checkbox.toggled.connect(lambda b: value.set(bool(b)))
    value.listen(lambda: checkbox.setChecked(bool(value.get()))
                 if checkbox.isChecked() != bool(value.get()) else None)
    return checkbox

def _list_accepts(e):
    if e.mimeData().hasUrls():
        e.acceptProposedAction()

def mark_red(widget, on, reason=""):
    """Mark an entry as faulty in place.

    A dialog at startup comes too late: by then the row is out of sight.
    Red in the row shows which one is meant, and the hint on it says why.
    """
    if widget is None:
        return
    try:
        widget.setStyleSheet(
            "border: 1px solid %s; border-radius: 3px;" % COLOURS["error"]
            if on else "")
        widget.setToolTip(reason if on else "")
    except RuntimeError:
        pass



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
        channel_row(T('      %d channels') % how_many,
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


def pause_if_running(QtMultimedia, *players):
    """Stop the players that are running, and leave the others alone.

    QMediaPlayer.pause() is not free on a player that never started.
    What lies behind it is built when it is first needed, and building
    it connects objects -- which waits for a lock that another player's
    decoding threads hold while they are starting up. The window then
    does not come back at all.

    Measured 28.8.2026 on two tests of this project, both stopped for
    good in QMediaPlayer::pause, and one of them with a single window
    open -- so this is not a thing only a test can reach.

    A player that is not playing has nothing to pause, so the question
    is asked first: playbackState only reads what is already noted and
    builds nothing.
    """
    for one in players:
        try:
            if (one.playbackState()
                    == QtMultimedia.QMediaPlayer.PlayingState):
                one.pause()
        except Exception:
            # A player already taken down answers nothing, and the
            # window is going anyway.
            pass




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
           '%d file was finished before that and is whole: %s',
           '%d files were finished before that and are whole: %s')
        % (len(done), ", ".join(done) or "-"),
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
    return T('The wide shot holds %g s, less than the shortest shot of '
             '%g s -- so it is merged away again and never appears.\n') % (
                 holds, least)


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
            TN(recordings, '%d audio recording', '%d audio recordings')
            % recordings,
            "" if recordings == audio_file_list
            else T(' from %d files') % audio_file_list))
    if videos_n:
        parts.append(TN(videos_n, '%d video file', '%d video files')
                     % videos_n)
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
        return (sentence + T(' -- %d notes') % len(hints),
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
    qt_own_words(QtCore, app)

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
            take_paths(paths)

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
                        TN(len(general), '%d point', '%d points')
                        % len(general),
                        "group", True)
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
                chains, header_value = (
                    None, TN(len(own), '%d file', '%d files') % len(own))
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
                    T('Remove all %d %ss from the list?\n\n%s')
                    % (len(affected), how,
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
    # ------------------------------------------------------------------
    PREWORK_THREADS = max(1, min(4, how_many_processors()))
    prework_folder = {"path": None}
    prework_done = {}               # (path, mtime, size) -> WAV
    prework_queue = []                # still to fetch
    prework_active = set()          # taken off the queue, being worked on
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
        axis_kick_off(list(paths))

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

    # ------------------------------------------------------------------
    # Separate the speakers, locally
    #
    # A third source for the same thing: who speaks when. auphonic.com
    # says it from its statistics, speakers_from_tracks measures it
    # where every person has a microphone, and this works it out from
    # one recording, on this machine, before anything is uploaded.
    # ------------------------------------------------------------------
    #
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
        assignment_fresh()
        speaker_split_show()
        preview_kick_off()

    bridge.speakers_split.connect(speaker_split_done)
    bridge.speakers_heard.connect(
        lambda r: speech_words_done(state, r, preview_kick_off))

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
                            speech_language.get())

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
        QtCore.QTimer.singleShot(0, assignment_fresh)

    def speaker_split_never():
        """The other button: not on this machine, and remember it."""
        state["speakers_wanted"] = False
        axis_store(state.get("axis") or {})
        speaker_split_show()

    split_never.clicked.connect(speaker_split_never)

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

    clip_kind_values = ByFile()
    # One value per video file, shown twice -- file list and player. Not
    # a second store: the same object both times.
    audio_use_values = ByFile()

    # The time axis is measured elsewhere and proposes a Kind from there.
    state["clip_kinds"] = clip_kind_values

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
        preview_kick_off()

    def assignment_fresh(forget=()):
        """Two tables: audio recordings above, video files below."""
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
        # it is in the same table above.
        own_audio_names = ByFile()
        # What a cut-out piece is called: the label the cutting gave it,
        # "Camera 1" and "Camera 2" for two clip-on microphones on one
        # camera. Without it the piece would be named after its file, which
        # carries the channel number and not the person.
        piece_label = ByFile()
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
                lambda *_: QtCore.QTimer.singleShot(0, refresh_names))
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
        wide_state_show()
        # And the file list says so too. It is built when the files come
        # in, which is before anybody is assigned, and the Kind it shows
        # is derived from exactly that -- so without this the first tab
        # goes on calling every camera the wide shot while the table
        # above says something else.
        video_kinds_again(video_kind_again)

    def refresh_names():
        """Suggest file names again; hand-edited ones stay."""
        untouched = [p for p, nv, _k, _n in camera_lines
                      if nv.get() == suggestions.get(p)]
        assignment_fresh(untouched)

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
        player_load_cut(numbers)

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
    cut_player.hush = hush_when_running(player, "_should_play")
    player.hush = hush_when_running(cut_player, "_playing")
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
    band_show(None)
    resolve_left.addStretch(1)
    # No stretch on the right: the room below belongs to the preview picture,
    # not to empty space.
    resolve_right.addStretch(0)

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
        preview_kick_off()

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
    break_off = break_off_button(QtWidgets, state, lambda t: write(t))
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
                  % (TN(len(content), '%d camera', '%d cameras')
                     % len(content),
                     TN(len(audio_files), '%d audio recording',
                        '%d audio recordings') % len(audio_files),
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
                start_run.setText(T('Camera audio, %d to go ...') % pending)
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
    # A moment after the window is up, not before: the first thing
    # somebody sees should be their files, not a question about
    # updates. Unless ffmpeg is too old -- that is then the one thing
    # the window has to offer, and it comes at once.
    QtCore.QTimer.singleShot(0, lambda: after_window(window, app, QtCore))
    return app.exec()




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
    restart_when_done(window, ended)
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


def restart_when_done(window, ended):
    """Wait for the install in the other thread, then offer the restart.

    A timer rather than a call out of that thread: a box belongs to
    the window's own thread and to no other. It stops itself either
    way, and it offers nothing where the install came back with
    trouble -- there is nothing to pick up then.
    """
    from PySide6 import QtCore
    watch = QtCore.QTimer(window)
    watch.setInterval(300)

    def look():
        if not ended:
            return
        watch.stop()
        if ended[0] == "":
            restart_offer(window)

    watch.timeout.connect(look)
    watch.start()
    return watch


def restart_offer(window):
    """Say in a box that ffmpeg is there, and offer the restart.

    A box rather than a line: in the Output tab that sentence is the
    last of two hundred the package manager wrote, and it goes under
    there. The box holds nothing up -- the window's timers go on
    turning inside it, so a pane still filling keeps filling, which is
    measured. True where somebody asked for the restart.
    """
    if os.environ.get("VPM_SILENT"):
        return False
    QtWidgets = _qt_widgets()
    box = QtWidgets.QMessageBox(window)
    box.setWindowTitle("ffmpeg")
    box.setText(T('ffmpeg is in place.'))
    box.setInformativeText(
        T('The program reads it when it starts. It can start again '
          'now, or you can do that yourself later.'))
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
    warn_box(QtWidgets, window, "ffmpeg",
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
    return ((T('The key is good. Of the %d presets in the account none '
               'is a Multitrack one, so the list stays empty.')
             if multitrack_on else
             T('The key is good. Of the %d presets in the account none '
               'is a Singletrack one, so the list stays empty.'))
            % len(preset_list), fitting)


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
    trouble = update_fetched(tag, owner)
    if trouble:
        warn_box(QtWidgets, window, T('A newer version is out'), trouble)


def restore_offer(window):
    """Ask, then put the kept version back and start again.

    Asked with the same weight as the update itself: it changes which
    program runs from the next second on, and this way is the one
    somebody takes when the newer one has just gone wrong on them.
    """
    QtWidgets = _qt_widgets()
    beside = old_self_file()
    if not beside:
        return
    back = version_in_file(beside)
    title = (T('Back to %s') % back) if back \
        else T('Back to the kept version')
    box = QtWidgets.QDialog(window)
    box.setWindowTitle(title)
    box.setMinimumWidth(620)
    rows = QtWidgets.QVBoxLayout(box)
    rows.setContentsMargins(18, 16, 18, 14)
    rows.setSpacing(14)
    head = QtWidgets.QLabel(title)
    font = head.font()
    font.setBold(True)
    head.setFont(font)
    rows.addWidget(head)
    # The buttons of the update window are named through T() rather
    # than written out here: a name copied into a sentence points into
    # thin air the day the button is renamed.
    said = QtWidgets.QLabel(
        T('%s takes the place of %s, and the file kept beside this one '
          'is used up. Forward again means fetching %s over the '
          'network. The program starts again straight '
          'away.\n\nThe next start offers %s once more: "%s" puts that '
          'off, "%s" passes over that one version.')
        % (back or T('The kept version'), VERSION, VERSION, VERSION,
           T('Later'), T('Skip this version')))
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
    trouble = restore_old_self()
    if trouble:
        warn_box(QtWidgets, window, title, trouble)
        return
    start_again()


def _qt_widgets():
    """QtWidgets, without carrying it down from the caller."""
    from PySide6 import QtWidgets
    return QtWidgets
