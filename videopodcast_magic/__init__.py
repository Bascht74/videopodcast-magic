#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Put processed audio back into video files.

    videopodcast-magic                       graphical interface
    videopodcast-magic --help                all switches

Design and rationale: see the manual under docs/ next to this file.
"""

import argparse
import atexit
import bisect
import contextlib
import ctypes
import datetime
import glob
import hashlib
import json
import math
import os
import platform
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import textwrap
from concurrent import futures
import threading
import time
import types


PIECES = {}    # the pieces of the program already read, by their path


class Program(object):
    """This program itself, for a piece of it that reaches back."""


PROGRAM = Program()
PROGRAM.__dict__ = globals()   # the names themselves, never a copy of them


class OneName(types.ModuleType):
    """The program, whose pieces answer to the same names."""

    def __setattr__(self, name, value):
        types.ModuleType.__setattr__(self, name, value)
        for piece in PIECES.values():
            if "PROGRAM" in piece.__dict__ and name in piece.__dict__:
                piece.__dict__[name] = value


def pieces_answer_together():
    """Let a name bent on this program reach the pieces holding it."""
    me = sys.modules.get(__name__)
    if me is None or vars(me).get("__file__") != __file__:
        return False
    me.__class__ = OneName
    return True


def beside(name, program=None):
    """One piece of this program, by path and never by name."""
    import importlib.util
    where = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         name, "__init__.py")
    if where not in PIECES:
        spec = importlib.util.spec_from_file_location(
            "videopodcast_magic." + name, where)
        piece = importlib.util.module_from_spec(spec)
        PIECES[where] = piece
        if program is not None:
            piece.PROGRAM = program
        spec.loader.exec_module(piece)
    return PIECES[where]


def take_from(piece):
    """Bind what a piece brought of its own, under this program."""
    for name, what in list(piece.__dict__.items()):
        if not name.startswith("__") and name not in globals():
            globals()[name] = what


# take_from places every name long before, so the `X = piece.X` lines
# below say nothing about the binding order: they are for a reader, and
# for source_no_loose_ends, which wants an origin for every name read.
# What each read binds, and why it stands there: development/internals.md.


#---------------------------------------------------------------- Language
# Every message is written in English here; language/ beside this one
# keys a translation to it, and a missing entry shows English. To add
# one: copy language/de.po to the new two-letter code, translate every
# msgstr, and name the code where the catalogue is filled at the end.

language = beside("language")
CATALOGUE = language.CATALOGUE
SOURCE_LANG = language.SOURCE_LANG
LANG = language.LANG
T = language.T
TN = language.TN
as_written = language.as_written
known_language = language.known_language
languages = language.languages
system_locale = language.system_locale
texts_of_language = language.texts_of_language


def set_language(name):
    """Switch every message to that language, English if it is unknown."""
    global LANG
    LANG = language.set_language(name)
    return LANG


def kept_language():
    """The language chosen in an earlier run, or "" if there was none.

    Only a code this program really has texts for counts as a choice.
    What stands under that name in the settings file can be anything
    -- a code from a newer version, one typed in by hand, something
    that is not text at all -- and none of that is anybody's choice:
    it falls through to the system, as if nothing had been written.
    """
    kept = PROGRAM.settings().get("language")
    return kept if isinstance(kept, str) and kept in languages() else ""


workbench = beside("workbench", program=PROGRAM)
take_from(workbench)

count_process_starts = workbench.count_process_starts
only_reading = workbench.only_reading


# What this program answers for. soxr is no part of it: without soxr
# the clock comes out a hundred times coarser, and coarser is not broken.
FFMPEG_FLOOR = (9, 0, 1)


setup = beside("setup", program=PROGRAM)
take_from(setup)

_require_module = setup._require_module
certificate_file = setup.certificate_file
ffmpeg_can_be_had = setup.ffmpeg_can_be_had
find_required_tools = setup.find_required_tools
https_context = setup.https_context
load_api_key = setup.load_api_key
soxr_available = setup.soxr_available
soxr_note = setup.soxr_note
tools_repaired = setup.tools_repaired


# main() rebinds this with global as the run starts, so it stays on
# this side of the seam: a copy in a piece would go on answering with
# what stood before.
TOOL_TROUBLE = ("", "")


# The floor is what PySide6 builds on. The command line alone could go
# lower, but one number is easier to state than two; the ceiling is
# what the suite runs on, and between the two is untested.
NEEDS_PYTHON = (3, 10)
LIKES_PYTHON = "3.14.7"
if sys.version_info < NEEDS_PYTHON:
    sys.exit("videopodcast-magic needs Python %d.%d or newer -- this is "
             "%d.%d. Recommended version: %s."
             % (NEEDS_PYTHON + sys.version_info[:2] + (LIKES_PYTHON,)))

class Numpy:
    """Stands in for numpy until the first calculation asks for it."""

    def __getattr__(self, name):
        global np
        np = _require_module("numpy")
        return getattr(np, name)


np = Numpy()

if os.environ.get("VPM_COUNT_STARTS"):
    count_process_starts(os.environ["VPM_COUNT_STARTS"])


SR = 48000
ASK_SINK = None      # set by the GUI: callable(options, title) -> key
OUTPUT_SINK = None   # set by the GUI: callable that receives raw log text
GUI_RUNNING = False  # the GUI already lists per-file details, so the log
                     # skips them when this is set
AUDIO_SUFFIXES = (".wav", ".bwf", ".flac", ".aif", ".aiff", ".mp3", ".m4a",
                ".aac", ".ogg", ".opus", ".wv", ".caf")
VIDEO_SUFFIXES = (".mov", ".mp4", ".m4v", ".mxf", ".mkv", ".avi", ".mts",
                 ".m2ts", ".mpg", ".mpeg", ".webm", ".r3d")
TRAILING_NUMBER = re.compile(r"^(.*?)(\d+)$")
VERSION = "3.0.0b9"
PROJECT_PREFIX = "videopodcast-magic_"  # project file: prefix + production
# It counts up whenever a stored key or value is renamed. An older
# file is refused with a clear message rather than half-read.
FILE_FORMAT = 3

# Not only a label: the handover is written with it, Resolve names its
# audio track after it, and a handover read back is looked up by it.
MIX_TRACK_NAME = "Full-Mix"

choices = beside("choices", program=PROGRAM)
take_from(choices)


livery = beside("livery", program=PROGRAM)
take_from(livery)

as_warn = livery.as_warn
enable_colour_output = livery.enable_colour_output
force_utf8_output = livery.force_utf8_output


dials = beside("dials", program=PROGRAM)
take_from(dials)

CUT_CHOICES = dials.CUT_CHOICES
MIN_EDIT_DURATION_S = dials.MIN_EDIT_DURATION_S
SILENCE_HOLD_S = dials.SILENCE_HOLD_S


filing = beside("filing", program=PROGRAM)
take_from(filing)

ByFile = filing.ByFile
FileSet = filing.FileSet


stowage = beside("stowage", program=PROGRAM)
take_from(stowage)

cache_folder = stowage.cache_folder


logbook = beside("logbook", program=PROGRAM)
take_from(logbook)

installed_by_a_package_manager = logbook.installed_by_a_package_manager
mark_time = logbook.mark_time


soundings = beside("soundings", program=PROGRAM)
take_from(soundings)

clean_probe_cache = soundings.clean_probe_cache
ffprobe_json = soundings.ffprobe_json


#---------------------------------------------------------- Time and timecode
timecode = beside("timecode", program=PROGRAM)
take_from(timecode)


#----------------------------------------------------- The spoken language

# ffmpeg wants three letters after ISO 639-2/B, both recognisers the
# two-letter code. Anything not listed is passed on as it stands.
SPEECH_CODES = {
    "ger": "de", "deu": "de", "eng": "en", "fra": "fr", "fre": "fr",
    "spa": "es", "ita": "it", "nld": "nl", "dut": "nl", "por": "pt",
    "pol": "pl", "rus": "ru", "swe": "sv", "dan": "da", "nor": "no",
    "fin": "fi", "ces": "cs", "cze": "cs", "tur": "tr", "ell": "el",
    "gre": "el", "jpn": "ja", "zho": "zh", "chi": "zh", "kor": "ko",
    "ara": "ar", "heb": "he", "hun": "hu", "ron": "ro", "rum": "ro",
    "ukr": "uk", "cat": "ca",
}


#-------------------------------------------------------- What a file says
metadata = beside("metadata", program=PROGRAM)
take_from(metadata)


#---------------------------------------------------------- The herald

# The window sets this on the program, a write that reaches no piece,
# so it stays on this side of the seam.
PROGRESS_SINK = None

herald = beside("herald", program=PROGRAM)
take_from(herald)

redirect_console = herald.redirect_console
running_from = herald.running_from
watch_outside_calls = herald.watch_outside_calls
write_through = herald.write_through


#--------------------------------------------------------- The hearing

hearing = beside("hearing", program=PROGRAM)
take_from(hearing)

clean_envelope_cache = hearing.clean_envelope_cache


#--------------------------------------------- Keeping itself up to date

# Set by the window on the program, a write that reaches no piece:
# callable(job), running job(say) in a thread into the Output tab.
UPDATE_SINK = None

upkeep = beside("upkeep", program=PROGRAM)
take_from(upkeep)

update_from_command_line = upkeep.update_from_command_line
update_note = upkeep.update_note


#---------------------------------------------------------- What is said

speech = beside("speech", program=PROGRAM)
take_from(speech)

CLOSING_MARKS = speech.CLOSING_MARKS
clause_break_times = speech.clause_break_times
recognise_speech = speech.recognise_speech
sentence_start_times = speech.sentence_start_times
sentences_of = speech.sentences_of
speech_word = speech.speech_word
speech_words_kick_off = speech.speech_words_kick_off
words_for_handover = speech.words_for_handover
words_from_handover = speech.words_from_handover
words_of_recording = speech.words_of_recording
write_transcript_files = speech.write_transcript_files


#--------------------------------------------------------------------- Run

def main():
    force_utf8_output()
    # Here rather than beside the last line of the file: a run started
    # through the installed command never passes that line.
    watch_outside_calls()
    mark_time("the program is read and running")
    if only_reading(sys.argv[1:]):
        # argparse prints and exits by itself; nothing here needs a tool.
        build_argument_parser().parse_args()
        return 0
    ap = build_argument_parser()
    args = ap.parse_args()
    # Before the first sentence is made, not before the first is
    # printed: the ffmpeg complaint below is written here and shown
    # much later. Only where one was typed, or the kept one is lost.
    if args.lang:
        set_language(args.lang)
    # --update wants no files and no tools, and a broken installation
    # is a reason to reach for it, so it is answered before either is
    # looked for.
    if args.update_now:
        return update_from_command_line()
    # Everything goes through ffmpeg, so below the floor there is
    # nothing to start. Behind only_reading() and --update on purpose:
    # --update must not fail on the thing it repairs.
    global TOOL_TROUBLE
    TOOL_TROUBLE = find_required_tools()
    mark_time("the tools are found")
    clean_envelope_cache()
    clean_probe_cache()
    clean_preflight_cache()
    # --lang alone is not a job: it only picks the language, so the window
    # still opens. Anything else on the command line means a run.
    rest = list(sys.argv[1:])
    while "--lang" in rest:
        i = rest.index("--lang")
        del rest[i:i + 2]
    rest = [a for a in rest if not a.startswith("--lang=")]
    to_the_window = not rest
    if to_the_window:
        # Qt before the console goes into the log file: a hundred
        # megabyte download, and behind the redirect the terminal would
        # stand silent for minutes and exit without a word.
        _require_module("PySide6.QtWidgets", "PySide6")
        # Nothing is said here: this path ends in a window. Where the
        # log is stands in the Help menu instead.
        redirect_console()
        mark_time("the log is open")
    # A place in the program list, laid once. Below the branch on
    # purpose: redirect_console() renames the running log, so a line
    # written above it lands in the log of the run before.
    beside("desktop", program=PROGRAM).lay_on_first_start()
    mark_time("the place in the program list is settled")
    if to_the_window:
        piece = window()
        while True:
            code = piece.gui()
            if code != piece.LANGUAGE_AGAIN:
                return code
            # The window took itself down for a chosen language; the
            # choice is read back so the next one speaks it.
            set_language(kept_language() or system_locale())
    force_utf8_output()
    enable_colour_output()
    # Whoever typed a command line has a console: said there, after the
    # language is settled and before the banner claims a run starts.
    if TOOL_TROUBLE[0] and not tools_repaired(*TOOL_TROUBLE):
        return 1
    print("videopodcast-magic %s   %s\n%s\n"
          % (VERSION, python_note(), running_from()))
    # Said, not asked: a run started from a script must not stop for a
    # question, and a coarser correction is not a fault.
    if not soxr_available() and ffmpeg_can_be_had():
        print(as_warn(soxr_note()))
    update_note()
    args.auphonic_done = getattr(args, "auphonic_done", None)
    args.auphonic_resume = getattr(args, "auphonic_resume", None)
    args.production = ""
    args.resolve_project = getattr(args, "resolve_project", None)
    if getattr(args, "hdr_check", None):
        try:
            return check_hdr(args.hdr_check)
        except Exception as e:
            print(T('Stopped: %s') % e)
            return 1
    if getattr(args, "resolve_audio_tracks", False):
        try:
            return print_audio_track_mapping()
        except Exception as e:
            print(T('Stopped: %s') % e)
            return 1
    if getattr(args, "resolve_json", None):
        try:
            return build_resolve_project(args.resolve_json, args.resolve_project,
                                 )
        except Exception as e:
            print(T('Resolve part stopped: %s') % e)
            return 1
    for long in ("no_camera_audio", "no_follow_ups", "no_drift",
                 "dry_run", "multitrack", "resolve"):
        setattr(args, long, getattr(args, long, False))
    args.name_camera = getattr(args, "name_camera", "Camera Original")

    if args.auphonic_key and not args.files:
        try:
            return print_presets(api_key_from_anywhere(args), args.multitrack)
        except Exception as e:
            print(T('Presets could not be loaded: %s') % e)
            return 1
    if not args.files:
        return ap.error(T('No files given.'))
    if args.auphonic_preset:
        e = os.path.splitext(args.auphonic_preset)[1].lower()
        if e in AUDIO_SUFFIXES + VIDEO_SUFFIXES or os.path.exists(args.auphonic_preset):
            args.files.insert(0, args.auphonic_preset)
            args.auphonic_preset = None

    audio_paths, video_paths, other = split_audio_and_video(args.files)
    for p in other:
        print(T('Unknown extension, skipped: %s') % os.path.basename(p))
    if not audio_paths and not video_paths:
        sys.exit(T('No audio file given.'))
    for p in audio_paths + video_paths:
        if not os.path.exists(p):
            sys.exit(T('Not found: %s') % p)

    # Preflight: once for both modes, before any fork.
    if run_preflight(args, audio_paths, video_paths):
        return 1
    if args.multitrack and not audio_paths:
        # Cameras only: their own audio becomes the track, and how many
        # tracks that is has to be measured -- one camera with two
        # microphones is two. So the plan is built before the decision.
        return multitrack_or_single(args, ap, audio_paths, video_paths)
    if not audio_paths:
        # Picture only, no multitrack: the camera audio becomes the track.
        if len(video_paths) > 1:
            print(T('Several cameras but no audio file. Each camera would '
                    'have its own audio --\nthat is what --multitrack is '
                    'for. Otherwise one camera after another.'))
            return 1
        args._camera_audio = tempfile.mkdtemp(prefix="vpm_camaudio_")
        atexit.register(shutil.rmtree, args._camera_audio, True)
        try:
            audio_paths = [extract_audio_from_video(video_paths[0], args._camera_audio)]
        except Exception as e:
            print(T('Camera audio not usable: %s') % e)
            return 1
        print()
    missing = check_mode_fits_input(audio_paths, args)
    if missing:
        print(missing)
        return 1
    # One way in, whatever --multitrack says: the switch decides how
    # the recordings are grouped and nothing else -- not the time axis,
    # not the arithmetic, not which code writes the files.
    return multitrack_or_single(args, ap, audio_paths, video_paths)


#------------------------------------------------ Beside the window
# What is running right now, so that breaking off can end it. A flag
# alone would not do: the run waits on ffmpeg for most of its minutes,
# and a child nobody tells goes on writing after the window has stopped.
RUN_STOP = {"wanted": False, "children": set(), "at": ""}


#---------------------------------------------------------- The material

material = beside("material", program=PROGRAM)
take_from(material)

channel_count = material.channel_count
channel_filter = material.channel_filter
expand_chains_to_tracks = material.expand_chains_to_tracks
find_continuation_files = material.find_continuation_files
format_complaint = material.format_complaint
kept_channels = material.kept_channels
parallel_map = material.parallel_map
place_track_on_axis = material.place_track_on_axis
python_note = material.python_note
remove_quietly = material.remove_quietly
shapes_match = material.shapes_match
wav_safe = material.wav_safe
widest_track = material.widest_track


#---------------------------------------------------------- The bearings

bearings = beside("bearings", program=PROGRAM)
take_from(bearings)

check_mode_fits_input = bearings.check_mode_fits_input
guess_speaker_name = bearings.guess_speaker_name
split_audio_and_video = bearings.split_audio_and_video
together_chains = bearings.together_chains


#--------------------------------------------------------- The preflight

preflight = beside("preflight", program=PROGRAM)
take_from(preflight)

PLATFORMS = preflight.PLATFORMS
check_preset = preflight.check_preset
clean_preflight_cache = preflight.clean_preflight_cache
lufs_does_nothing = preflight.lufs_does_nothing
report_findings = preflight.report_findings
run_ffmpeg_with_progress = preflight.run_ffmpeg_with_progress
run_preflight = preflight.run_preflight


#---------------------------------------------------------- The processing

auphonic = beside("auphonic", program=PROGRAM)
take_from(auphonic)

api_key_from_anywhere = auphonic.api_key_from_anywhere
print_presets = auphonic.print_presets
tracks_folder = auphonic.tracks_folder


#-------------------------------------------------------- The separation

# The two stay here, measured: the separation writes them back with
# PROGRAM.name = value, and source_names_stay_fresh goes red over a
# name written that way and bound at the top of a piece.
_SPEAKER_READY = None
_SPEAKER_WHY = ""

speakers = beside("speakers", program=PROGRAM)
take_from(speakers)



#---------------------------------------------------------- The project

resolve = beside("resolve", program=PROGRAM)
take_from(resolve)

CLIP_COLOURS = resolve.CLIP_COLOURS
CLIP_COLOURS_RGB = resolve.CLIP_COLOURS_RGB
CLIP_COLOURS_RGB_DARK = resolve.CLIP_COLOURS_RGB_DARK
CLIP_COLOURS_RGB_LIGHT = resolve.CLIP_COLOURS_RGB_LIGHT
MATRIX_BT2020 = resolve.MATRIX_BT2020
ON_DARK = resolve.ON_DARK
PRIMARIES_BT2020 = resolve.PRIMARIES_BT2020
build_resolve_project = resolve.build_resolve_project
camera_text = resolve.camera_text
check_hdr = resolve.check_hdr
colour_per_camera = resolve.colour_per_camera
colour_text = resolve.colour_text
file_frame_rate = resolve.file_frame_rate
frames_to_timecode = resolve.frames_to_timecode
hdr_from_sources = resolve.hdr_from_sources
known_frame_rate = resolve.known_frame_rate
own_frame_rate = resolve.own_frame_rate
print_audio_track_mapping = resolve.print_audio_track_mapping
resolve_timeline_rate = resolve.resolve_timeline_rate
seconds_to_frames = resolve.seconds_to_frames
timecode_to_frames = resolve.timecode_to_frames
timeline_frame_rate = resolve.timeline_frame_rate


#-------------------------------------------------------------- The cut

cut = beside("cut", program=PROGRAM)
take_from(cut)

MIN_SPEECH_TO_SWITCH_S = cut.MIN_SPEECH_TO_SWITCH_S
WIDE_AFTER_S = cut.WIDE_AFTER_S
finish_without_auphonic = cut.finish_without_auphonic
is_stand_in_name = cut.is_stand_in_name
roles_report = cut.roles_report
separation_for_run = cut.separation_for_run
speakers_for_the_cut = cut.speakers_for_the_cut
speakers_from_tracks = cut.speakers_from_tracks
voice_names_report = cut.voice_names_report
who_asks = cut.who_asks
write_cut_list = cut.write_cut_list
write_handover = cut.write_handover
write_metrics_csv = cut.write_metrics_csv


#------------------------------------------------------------ The chain

pipeline = beside("pipeline", program=PROGRAM)
take_from(pipeline)

extract_audio_from_video = pipeline.extract_audio_from_video
multitrack_or_single = pipeline.multitrack_or_single


#------------------------------------------------------------ The orders
orders = beside("orders", program=PROGRAM)
take_from(orders)

build_argument_parser = orders.build_argument_parser


#-------------------------------------------------------- The interface


def window():
    """The window, read out of the folder the first time it is wanted."""
    global ui
    ui = beside("ui", program=PROGRAM)
    take_from(ui)
    # A name bent on this program before the window was read: the
    # window binds its own under that name and would stand on it, so
    # the bend is carried in.
    for name, what in list(vars(ui).items()):
        if not name.startswith("__") and globals().get(name, what) is not what:
            setattr(ui, name, globals()[name])
    return ui


def __getattr__(name):
    """A name of the window, asked for before the window was read."""
    if name.startswith("__"):
        raise AttributeError(name)
    piece = window()
    return piece if name == "ui" else getattr(piece, name)


pieces_answer_together()


#--------------------------------------------------------------- Catalogue
# One file per language beside this one. How to add one: see the top.

CATALOGUE["de"] = texts_of_language("de")
# German is complete; the eleven after it are partial, and what they
# leave out appears in English. Arabic turns the window round.
CATALOGUE["es"] = texts_of_language("es")
CATALOGUE["pt"] = texts_of_language("pt")
CATALOGUE["fr"] = texts_of_language("fr")
CATALOGUE["it"] = texts_of_language("it")
CATALOGUE["tr"] = texts_of_language("tr")
CATALOGUE["ru"] = texts_of_language("ru")
CATALOGUE["uk"] = texts_of_language("uk")
CATALOGUE["zh"] = texts_of_language("zh")
CATALOGUE["ja"] = texts_of_language("ja")
CATALOGUE["hi"] = texts_of_language("hi")
CATALOGUE["ar"] = texts_of_language("ar")

# What somebody chose in an earlier run, else the system. --lang beats
# both, and main() applies it once the command line has been read.
LANG = set_language(kept_language() or system_locale())


if __name__ == "__main__":
    sys.exit(main())
