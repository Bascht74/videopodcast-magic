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
    """The program, whose pieces answer to the same names.

    A piece binds the names it uses under its own, so a name bent from
    outside -- which is what a test does, and nothing else does --
    would reach this copy and leave the piece's standing. Bent here, it
    is bent in every piece of this program that carries it.
    """

    def __setattr__(self, name, value):
        types.ModuleType.__setattr__(self, name, value)
        for piece in PIECES.values():
            if "PROGRAM" in piece.__dict__ and name in piece.__dict__:
                piece.__dict__[name] = value


def pieces_answer_together():
    """Let a name bent on this program reach the pieces holding it.

    True where it took. This needs the module as an object, and a run
    that executes the file without registering it under its own name
    leaves none -- such a run bends nothing either, so nothing is lost.
    """
    me = sys.modules.get(__name__)
    if me is None or vars(me).get("__file__") != __file__:
        return False
    me.__class__ = OneName
    return True


def beside(name, program=None):
    """One piece of this program, out of the folder this file lies in.

    Read from its path, and not imported by name. The program is
    started three ways -- installed, as a plain file, and executed from
    an absolute path under a name a test picks -- and an import by name
    finds the piece in the first of them only. A piece given *program*
    gets it before it is read, and binds out of it what it uses.
    """
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
    """Bind what a piece brought of its own, under this program.

    A piece is a piece of this program and not a library beside it:
    what it brings answers here under the same name, so that nothing
    outside has to know which file a name ended up in. What it took
    out of the program stands here already and is left alone.
    """
    for name, what in list(piece.__dict__.items()):
        if not name.startswith("__") and name not in globals():
            globals()[name] = what


# ---------------------------------------------------------------------------
# Language
# ---------------------------------------------------------------------------
# Every message is written in English here. A translation lives in the
# folder "language" beside this one, keyed by the English text; T() looks
# it up, and a missing entry shows English rather than a gap.
#
# Adding a language takes three steps:
#   1. Copy language/de.po to the new two-letter code, and name that
#      code at the end of this file.
#   2. Translate every msgstr. Entries left out stay English.
#   3. Nothing else. --lang offers the new code and a system set to it
#      picks it automatically.

language = beside("language")
CATALOGUE = language.CATALOGUE
SOURCE_LANG = language.SOURCE_LANG
LANG = language.LANG
T = language.T
TN = language.TN
known_language = language.known_language
languages = language.languages
system_locale = language.system_locale
texts_of_language = language.texts_of_language


def set_language(name):
    """Switch every message to that language, English if it is unknown.

    The code is held twice: beside this file, where T() reads it, and
    here, which is where a reader of this program and every test look
    for it. One door sets both, so they cannot come apart.
    """
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
    kept = settings().get("language")
    return kept if isinstance(kept, str) and kept in languages() else ""


def group_text(number):
    """Group the thousands the way the chosen language does."""
    return format(int(number), ",d").replace(",", T(","))


def decimal_text(text):
    """Write the decimal point the way the chosen language writes it."""
    mark = T(".")
    return text.replace(".", mark) if mark != "." else text


def channel_text(count):
    """Say a channel count the way a person would.

    One and two have names; above that the number does the work. An
    unreadable file has no count at all, and then a guess would be worse
    than saying so.
    """
    try:
        count = int(count)
    except (TypeError, ValueError):
        return T('channel count unknown')
    return {1: "mono", 2: "stereo"}.get(
        count, TN(count, '%s channel', '%s channels') % group_text(count))


# Set to answer yes before the question is asked: a test run, a build
# machine, anything with nobody in front of it. It answers for both
# places that ask, the package manager and pip -- and nothing installs
# without it, or without somebody saying yes.
INSTALL_TOOLS = bool(os.environ.get("VPM_INSTALL_TOOLS"))


# What this program answers for. It rose to 9.0.1 the day all six
# builder jobs carried it and all three systems had a way of getting
# it offered to them. soxr is no part of it: without soxr the clock
# comes out a hundred times coarser, and coarser is not broken.
FFMPEG_FLOOR = (9, 0, 1)


# A piece of its own, in the folder "setup" beside this one. Read here
# at the top, because what stands under it wants tools and modules
# that may not be there yet. The floor above stays: it is what this
# program answers for, and the piece reads it out of here.

setup = beside("setup", program=PROGRAM)
take_from(setup)

# What this file itself calls out of the setting up. The rest of what
# it brings answers here too, through take_from above; these are
# written out because they are read in this file, and a name read here
# and bound nowhere here is a loose end.
_require_module = setup._require_module
certificate_file = setup.certificate_file
ffmpeg_can_be_had = setup.ffmpeg_can_be_had
find_required_tools = setup.find_required_tools
https_context = setup.https_context
load_api_key = setup.load_api_key
soxr_available = setup.soxr_available
soxr_note = setup.soxr_note
tools_repaired = setup.tools_repaired


# Set by main() before anything else happens, read by the window. It
# stays on this side of the seam because main() rebinds it with global
# as the run starts, and a copy over there would go on answering with
# what stood before that.
TOOL_TROUBLE = ("", "")


# The floor is what the interface needs: PySide6 does not build below
# 3.10. The command line alone could go lower, but one number is easier
# to state than two. The ceiling is what the suite runs on; between the
# two is untested.
NEEDS_PYTHON = (3, 10)
LIKES_PYTHON = "3.14.7"
if sys.version_info < NEEDS_PYTHON:
    sys.exit("videopodcast-magic needs Python %d.%d or newer -- this is "
             "%d.%d. Recommended version: %s."
             % (NEEDS_PYTHON + sys.version_info[:2] + (LIKES_PYTHON,)))

def only_reading(argv):
    """True where the command line only wants the switch list or the version.

    A question about the command line, asked where the command line is
    read. Reading it needs neither numpy nor ffmpeg.
    """
    return any(a in ("-h", "--help", "--version") for a in argv)


class Numpy:
    """Stands in for numpy until the first calculation asks for it.

    What this file holds must not depend on how the program was
    started, or its parts cannot import one another. Importing it
    fetches nothing; --version answers cheaply because it calculates
    nothing, not because argv was read while the file was being read.
    """

    def __getattr__(self, name):
        global np
        np = _require_module("numpy")
        return getattr(np, name)


np = Numpy()

def count_process_starts(where):
    """Write one line per process this program starts, into a file.

    Process starts are what the Windows builder charges for, so the
    suite counts them per test and prints the count beside the verdict.
    Off unless VPM_COUNT_STARTS names a file. Only Popen is wrapped --
    subprocess.run builds one itself, and wrapping both counted every
    run twice.
    """
    was_popen = subprocess.Popen

    def note(argv):
        first = argv if isinstance(argv, str) else (argv[0] if argv else "?")
        try:
            with open(where, "a", encoding="utf-8") as f:
                f.write("%s\n" % os.path.basename(str(first)))
        except OSError:
            return

    class Popen(was_popen):
        def __init__(self, *a, **k):
            note(a[0] if a else k.get("args") or [])
            was_popen.__init__(self, *a, **k)

    subprocess.Popen = Popen


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
VERSION = "3.0.0b5"
PROJECT_PREFIX = "videopodcast-magic_"  # project file: prefix + production
# The names inside the stored files. It counts up whenever a key or
# a stored value is renamed. An older file is refused with a clear
# message rather than read as if it still fitted.
FILE_FORMAT = 3
CEILING_DBTP = -1.0                     # true-peak ceiling of the result
LIMIT_MAX_DB = 6.0        # most the limiter may take off

# What the mixed track is called, one name for both paths. Not only a
# label: the handover file is written with it, Resolve names its audio
# track after it, and reading a handover back looks it up by this word.
MIX_TRACK_NAME = "Full-Mix"

# The switches that need several recordings. Everything else works on any
# run since the two paths became one.
ONLY_MULTITRACK = ("auphonic_resume", "assign", "multitrack")

# Values that are stored and shown at the same time. The value is fixed so
# a project file keeps its meaning in any language; what appears on screen
# comes from CHOICE_LABELS and goes through T().
MIX_ONLY = "mix-only"            # audio track without a camera of its own
IGNORE_AUDIO = "ignore-audio"    # audio track stays out entirely
# The answer "I do not know, go and measure" to the name field's
# question of who is to be heard: a typed name claims one person, this
# says there are several and the machine is to tell them apart.
SEVERAL_SPEAKERS = "several-speakers"
PRESET_NONE = "no-auphonic"      # list entry, not a preset name
TYPE_CONTENT, TYPE_INTRO, TYPE_OUTRO = "content", "intro", "outro"
# The camera nobody sits in front of. A value of the Kind field rather
# than something derived, so it is an answer somebody gives instead of
# a guess -- and it travels in the project file and on the switch.
TYPE_WIDE = "wide-shot"
TYPE_IGNORED = "ignore-video"    # video file stays out entirely
CLIP_TYPES = (TYPE_CONTENT, TYPE_WIDE, TYPE_INTRO, TYPE_OUTRO,
              TYPE_IGNORED)
# Which kinds are a camera in the run. The wide shot is one like any
# other -- aligned, rendered, cut to; the mark says only that no
# speaker belongs to it. Named once here rather than at every place
# that asks "is this a camera".
CAMERA_TYPES = (TYPE_CONTENT, TYPE_WIDE)
# Whether a video file's sound is material for the run. It cannot be
# measured: a radio microphone recorded into the video track looks like
# a room microphone, so only whoever was there knows. Synchronising is
# untouched by it; this decides only whether the sound counts as content.
AUDIO_UNUSED = "audio-unused"
AUDIO_MATERIAL = "audio-material"
AUDIO_USE = (AUDIO_UNUSED, AUDIO_MATERIAL)
# Two names that are easy to confuse: "do not use" leaves the audio out
# entirely, "no camera of its own" only keeps the person off camera.
# The fuller wording is twice as wide as the column allows, so the rest
# of it lives in the tooltip.
CHOICE_LABELS = {MIX_ONLY: "no camera of its own",
                 IGNORE_AUDIO: "do not use",
                 SEVERAL_SPEAKERS: "several speakers",
                 PRESET_NONE: "work without Auphonic",
                 TYPE_CONTENT: "Content", TYPE_INTRO: "Intro",
                 # The same words the cut band, the legend and the four
                 # cut rules use. A second name for one thing would
                 # read as a second thing.
                 TYPE_WIDE: 'Wide shot',
                 TYPE_OUTRO: "Outro", TYPE_IGNORED: "ignore this video",
                 AUDIO_UNUSED: "do not use the audio",
                 AUDIO_MATERIAL: "use the audio"}


def label_of(value):
    """Return what a stored value is called on screen."""
    return T(CHOICE_LABELS[value]) if value in CHOICE_LABELS else value


def fill_choices(box, values, chosen=None):
    """Fill a combo box: it stores the value and shows the label."""
    box.clear()
    for v in values:
        box.addItem(label_of(v), v)
    if chosen is not None:
        pick_choice(box, chosen)


def pick_choice(box, value):
    """Select the entry that stands for this value; first one if unknown."""
    i = box.findData(value)
    box.setCurrentIndex(i if i >= 0 else 0)


# Parallel runs keep per-thread output apart: progress feeds one shared
# bar, text goes to a private buffer and is flushed when the file is done.
THREAD_SHARE = {}    # thread id -> progress fraction of that file
THREAD_BUFFER = {}   # thread id -> list of text chunks

# How much room a file name gets on a button or in a chooser, in
# pixels: wide enough for a recorder's usual name, narrow enough that
# the player on the right stays in the window.
NAME_ROOM = 260
# What the row under the assignment table may take before the player on
# the right is pushed off the window: past this the sheet asks for more
# than a 13 inch screen has.
ROW_ROOM = 380
# How many rows of the speaker table are shown before it scrolls itself.
# Rows, not speakers: one row per speaker plus one for Silence, and the
# column header sits on top. Without a lid the table grew by a row per
# speaker until the Resolve sheet answered with a scroll bar of its own.
SPEAKER_ROWS_SHOWN = 4

# One palette for all three outputs -- GUI, log pane and terminal -- so a
# run looks the same wherever it is watched.
COLOURS = {
    "heading":   "#1f4e79",       # section heading
    "backdrop": "#e8eff7",      # the strip behind a heading
    "good":     "#2e7d4f",       # done
    # Dark enough to clear the 4.5 contrast floor on every surface it
    # stands on, our own and the three desktops'. A lighter orange
    # falls through on the foreign window colours.
    "warning": "#985508",       # warning, run continues
    "error":  "#b02020",       # aborted
    "value":    "#2f5d8a",       # numbers and results
    # Dark enough for the 4.5 contrast floor on the footer, which the
    # desktop paints lighter than our own surfaces.
    "quiet":   "#646e7b",       # secondary
    "text":    "#222222",
    # Surfaces -- GUI only
    "frame":  "#cfd8e3",
    "box":  "#fbfcfe",
    "head":    "#eef2f7",
    "sheet":   "#ffffff",
    "stripe":  "#dce6f2",
    # A switched-off button keeps its own colour, only muted: flat grey
    # reads as a different kind of thing, and the two buttons of a pair
    # then look as if only one were off. The pair still clears the
    # contrast floor, so the label stays readable.
    "off":     "#c6d6e6",       # disabled button: the fill, muted
    "off_text": "#3a5c80",      # disabled button: what stands on it
}

# Same roles for a dark desktop: same hues, lighter and less saturated.
# Saturated colour glares on dark, and a dark blue would be unreadable.
COLOURS_DARK = {
    "heading":   "#7fb4e6",
    "backdrop": "#233040",
    "good":     "#5cc98a",
    # Its own value, and it has to be: the light orange all but
    # disappears against a dark sheet.
    "warning": "#e2a355",
    "error":  "#f07070",
    "value":    "#9dc4e8",
    "quiet":   "#95a1b0",
    "text":    "#e4e8ee",
    "frame":  "#3c4653",
    "box":  "#232a33",
    "head":    "#2b333d",
    "sheet":   "#1d232a",
    "stripe":  "#33404f",
    "off":     "#2c3a48",
    "off_text": "#93a9c0",
}

# The light set kept aside. COLOURS is the one dictionary everything
# reads, so a desktop switched to dark and back has to find the light
# values again -- overwriting them in place would burn the way back.
COLOURS_LIGHT = dict(COLOURS)


def desktop_is_dark(QtWidgets, QtGui):
    """Report whether the desktop uses a dark colour scheme.

    Falls back to the window background lightness where Qt does not
    expose a scheme.
    """
    try:
        schema = QtWidgets.QApplication.styleHints().colorScheme()
        if "Dark" in str(schema):
            return True
        if "Light" in str(schema):
            return False
    except Exception:
        pass
    try:
        return QtWidgets.QApplication.palette().color(
            QtGui.QPalette.Window).lightness() < 128
    except Exception:
        return False
ANSI = {"heading": "\033[1;36m", "good": "\033[1;32m", "warning": "\033[33m",
        "error": "\033[1;31m", "value": "\033[36m", "quiet": "\033[90m",
        "text": ""}


MARK = "\x01"     # invisible prefix; it names the kind of a log line
MARK_KINDS = {"h": "heading", "g": "good", "w": "warning", "e": "error"}


def as_head(text):
    """Mark a line as a section heading."""
    return MARK + "h" + text


def as_good(text):
    """Mark a line as something that worked."""
    return MARK + "g" + text


def as_warn(text):
    """Mark a line as a warning; the run carries on."""
    return MARK + "w" + text


def as_bad(text):
    """Mark a line as an error."""
    return MARK + "e" + text


def split_kind(line):
    """Split a line into its kind and its plain text.

    The kind is stated where the line is written rather than read out of
    its wording, which would tie it to one language. Returns one of
    "heading", "good", "warning", "error", "text".
    """
    if line[:1] == MARK:
        return MARK_KINDS.get(line[1:2], "text"), line[2:]
    return "text", line


def strip_marks(text):
    """Take every kind marker back out of a text."""
    return re.sub(MARK + ".?", "", text) if MARK in text else text


class ColourWriter(object):
    """Colour terminal output without altering the text itself.

    Colour is chosen at the start of a line and held for the rest of it,
    so a progress bar rewriting its line stays intact. The invisible kind
    marker comes off here, so this is in place even without colour.
    """

    def __init__(self, raw, colour=True):
        self.raw = raw
        self.colour = colour
        self.begin = True
        self.pending = False
        self.carried = ""     # marker seen before its line had text

    def write(self, text):
        off = []
        for part in re.split(r"([\n\r])", text):
            if part in ("\n", "\r"):
                if self.pending:
                    off.append("\033[0m")
                    self.pending = False
                off.append(part)
                self.begin = True
            elif part:
                if self.begin:
                    kind, part = split_kind(part)
                    if kind == "text" and self.carried:
                        kind = self.carried
                    if not part:
                        # The marker was in front of a line break, so it
                        # belongs to the line that follows.
                        self.carried = kind
                        continue
                    self.carried = ""
                    code = ANSI.get(kind, "") if self.colour else ""
                    if code:
                        off.append(code)
                        self.pending = True
                    self.begin = False
                else:
                    part = strip_marks(part)
                off.append(part)
        self.raw.write("".join(off))
        self.raw.flush()

    def flush(self):
        self.raw.flush()

    def __getattr__(self, name):
        return getattr(self.raw, name)


def force_utf8_output():
    """Force stdout/stderr to UTF-8.

    Windows consoles default to a legacy code page, where one umlaut in a
    message aborts the run. Replacement characters beat a crash.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def enable_colour_output():
    """Put the output filter in place and colour it where that lands.

    The filter always runs, because it also takes the invisible kind
    markers out again. Colour is added only on a terminal that shows it.
    """
    colour = not os.environ.get("NO_COLOR")
    try:
        colour = colour and bool(sys.stdout.isatty())
    except Exception:
        colour = False
    if colour and os.name == "nt":
        # Windows only shows control characters when asked to.
        try:
            import ctypes
            h = ctypes.windll.kernel32.GetStdHandle(-11)
            mode = ctypes.c_uint32()
            if not ctypes.windll.kernel32.GetConsoleMode(h,
                                                         ctypes.byref(mode)):
                colour = False
            else:
                ctypes.windll.kernel32.SetConsoleMode(h, mode.value | 0x0004)
        except Exception:
            colour = False
    if getattr(sys.stdout, "keeps_marks", False):
        # The window reads the markers itself and colours by them.
        return
    sys.stdout = ColourWriter(sys.stdout, colour)
    sys.stderr = ColourWriter(sys.stderr, colour)


class Value(object):
    """A value several observers can watch.

    Qt normally binds a value to its input widget. The assignment table is
    rebuilt on every change, so its widgets disappear while the entered
    values must survive. The value lives here and the widget follows it.
    """

    def __init__(self, value=""):
        self._value = value
        self._listeners = []

    def get(self):
        return self._value

    def typed(self):
        """Only the answer given here, with nothing standing in for it.

        The plain reading is get(). This one is for the two places that
        have to tell an answer from a guess: what a widget shows, and
        what is written into the project file. On every value but a
        name field the two are the same string.
        """
        return self._value

    def set(self, value):
        if value == self._value:
            return
        self._value = value
        for f in list(self._listeners):
            try:
                f()
            except Exception:
                pass

    def listen(self, f):
        self._listeners.append(f)
        return f


# What can be shown where "whoever speaks is on screen" gives no
# answer. The names are the values of the four choice fields below and
# of the switches behind them.
SHOT_WIDE = "wide"
SHOT_LISTENER = "listener"
SHOT_ALTERNATE = "alternate"
SHOT_HOLD = "hold"
SHOT_HOLD_BRIEF = "hold-brief"
SHOT_OFF = "off"
SHOT_ANSWER = "answer"

SHOT_NAMES = {
    SHOT_WIDE: 'Wide shot',
    SHOT_LISTENER: 'Listener',
    SHOT_ALTERNATE: 'Alternating',
    SHOT_HOLD: 'No camera change',
    # Holding without an end is a different answer from holding a
    # breath, so the two are two entries and the seconds stand in a
    # field of their own.
    SHOT_HOLD_BRIEF: 'Hold a short gap',
    # Named after what does not happen, not after a switch position:
    # in a row labelled "Question" the picture going early is the only
    # thing there is to leave alone.
    SHOT_OFF: 'do not go early',
    SHOT_ANSWER: 'Answering speaker',
}

# The shortest a shot may stand. A camera that changes faster than the
# viewer can settle on a face reads as nervous. One value for the
# interface, the switch and every default, or the two cut differently.
MIN_EDIT_DURATION_S = 3.0

# Up to here a gap with nobody in it counts as a breath rather than as
# an end, where the cut is told to hold one. Measured over 83 minutes
# on 2.9.2026: at one second no picture stands on a silent person for
# longer than 4.0 s, from two seconds on the first ones over five appear.
SILENCE_HOLD_S = 1.0

# The camera cut is derived from who speaks when; these numbers decide
# how fine it turns out. Per entry: switch, label, default, unit,
# short explanation beside it, longer one in the tooltip.
CUT_FIELDS = (
    ("min-edit-duration", 'Minimum Edit Duration',
     "%.1f" % MIN_EDIT_DURATION_S, "s",
     'shorter shots are merged in',
     'Shorter shots fall into the following one.'),
    ("min-speech-to-switch", 'Speaks at least', "1.5", "s",
     'below this the camera does not follow',
     ('A short "yes" does not move the picture. Without this a block of '
      'half a second draws the camera over, and the minimum edit '
      'duration then holds it there for seconds.')),
    ("silence-hold", 'Short gap up to', "%.1f" % SILENCE_HOLD_S, "s",
     'so long a silence leaves the picture alone',
     ('Only where "Nobody speaks" is set to hold a short gap. A gap up '
      'to this long changes nothing, a longer one goes to the wide '
      'shot. Above two seconds the picture begins to stand on someone '
      'silent for over five seconds.')),
    # Resolve's own name for it, in the German window as well, so it stays
    # English. The double quotes are the mark: this one is not translated.
    ("edit-change-delay", "Edit Change Delay", "0.3", "s",
     'the picture changes this much later than the sound',
     'A negative value makes the picture lead the sound.'),
    ("reaction-lead", 'Answer on screen earlier', "1.5", "s",
     'before the question ends',
     ('Zero is where the asker stops, not where the answer starts: the '
      'pause between them belongs to the question. Applies only where '
      '"After a question" asks for it, and the Edit Change Delay is '
      'not added again.')),
    ("wide-after", 'Wide shot after', "70", "s",
     'from here on a good moment for it is looked for',
     ('The soft limit of the pair: from here the program waits for a '
      'sentence boundary and puts the wide shot there, not on the '
      'clock. 0 turns it off. "Wide shot at the latest" is the hard '
      'limit, where it cuts without one.')),
    ("wide-latest", 'Wide shot at the latest', "120", "s",
     'and here it is cut, good moment or not',
     ('The hard limit of the pair: where no sentence boundary has '
      'turned up since "Wide shot after", the longest speech pause '
      'stands in for one, and at this point the cut happens whatever '
      'is being said.')),
    ("wide-length", 'Wide shot at least', "5", "s",
     'so long the inserted wide shot stands at least',
     ('It then runs to the end of the sentence. Below five seconds the '
      'look reads as a twitch.')),
    ("wide-most", 'Wide shot at most', "15", "s",
     'and at most this long',
     ('Where the end of the sentence lies beyond it, the last clause '
      'break before it ends the shot -- it is not cut off mid-sentence.')),
)

# The cases where the speech does not say whom to show, and what is
# shown instead. Per entry: switch, label, default, the values it
# takes, short explanation beside it, longer one in the tooltip.
CUT_CHOICES = (
    # First, and directly under "Answer on screen earlier": the two
    # belong to one question and used to stand at opposite ends of the
    # tab, in words that did not meet.
    ("on-question", 'After a question', SHOT_ANSWER,
     (SHOT_OFF, SHOT_ANSWER, SHOT_LISTENER),
     'the picture goes to the answer before it starts',
     ('Only after a question that is not the main speaker\'s, when '
      'somebody else takes over at once and keeps the floor.\n"do not '
      'go early" means no early camera change: the picture follows '
      'the sound here as it does everywhere else.')),
    ("on-monologue", 'Long monologue', SHOT_ALTERNATE,
     (SHOT_WIDE, SHOT_LISTENER, SHOT_ALTERNATE, SHOT_HOLD),
     'one person holds the floor past "Wide shot after"',
     ('"Alternating" remembers what the last break of this monologue '
      'showed. The listener only gets the picture when someone on that '
      'camera was heard in the last 20 seconds; otherwise the wide '
      'shot.')),
    ("on-together", 'Several speak at once', SHOT_WIDE,
     (SHOT_WIDE, SHOT_LISTENER, SHOT_ALTERNATE, SHOT_HOLD),
     'and no camera shows exactly them',
     'Cutting into a jumble looks frantic.'),
    # Directly above "Recognition uncertain", because the two were
    # taken for one another: nobody speaking is not the recognition
    # being unsure, and this is the case that decides a fifth of the
    # running time against that one's three thousandths.
    ("on-silence", 'Nobody speaks', SHOT_WIDE,
     (SHOT_WIDE, SHOT_HOLD_BRIEF, SHOT_HOLD),
     'no voice is heard at all here',
     ('A breath in the middle of a sentence and the end of a thought '
      'are both silence, and the program cannot tell them apart. Only '
      'the length can: "Short gap up to" says how long a silence may '
      'be and still count as a breath.')),
    ("on-uncertain", 'Recognition uncertain', SHOT_WIDE,
     (SHOT_WIDE, SHOT_LISTENER, SHOT_ALTERNATE, SHOT_HOLD),
     'the speaker recognition frays or leaves a heap behind',
     ('Guessing puts the wrong person on screen for seconds; the wide '
      'shot is right in every case. Somebody is speaking here -- where '
      'nobody is, "Nobody speaks" decides.')),
)


def shell_quote(cmd):
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode("utf-8", "replace")[-2000:])
    return p


# An ffprobe call costs a process start and, on an external volume, a
# seek out to the disc. Building the interface asks the same questions
# about the same file over and over, and one process each held the
# window thread until the disc answered.
_PROBE = {}


def path_key(path):
    """The one shape a path takes when two of them are compared.

    abspath settles the folder and nothing else: on Windows the same
    file reached two ways keeps the case and the separator it was typed
    with, and compares unequal. normcase settles both, and on a Mac it
    changes nothing. Every comparison and every path used as a key goes
    through here, so the fault where one side is put into shape and the
    other is not cannot be written.
    """
    return os.path.normcase(os.path.abspath(path))


class ByFile(dict):
    """A dictionary of files: one entry per file, whatever it is called.

    The same file arrives typed by hand, out of a file dialogue and out
    of a project file, and on Windows those differ in case while
    meaning one file. Finding therefore goes through path_key on every
    side. The key keeps the spelling it was first written under, so
    what is walked over, shown or saved is the name on the disc.
    """

    # A key that is not a string passes through untouched. A key made
    # of a path and something else is built where it is built, and
    # path_key belongs in that one place -- see prework_api_key.

    def __init__(self, *given, **named):
        dict.__init__(self)
        self._spelt = {}
        if given or named:
            self.update(*given, **named)

    def _index(self):
        """The spelling each file sits under, rebuilt if it is gone.

        A dictionary can come into being without __init__ -- fromkeys,
        a copy read back in -- and a lookup against an index that is
        not there would quietly miss.
        """
        try:
            return self._spelt
        except AttributeError:
            self._spelt = {path_key(k): k for k in self if isinstance(k, str)}
            return self._spelt

    def _as_stored(self, key):
        """The key this file already sits under, or the key itself."""
        if not isinstance(key, str):
            return key
        if dict.__contains__(self, key):
            return key
        return self._index().get(path_key(key), key)

    def __getitem__(self, key):
        return dict.__getitem__(self, self._as_stored(key))

    def __setitem__(self, key, value):
        here = self._as_stored(key)
        dict.__setitem__(self, here, value)
        if isinstance(key, str):
            self._index()[path_key(key)] = here

    def __delitem__(self, key):
        here = self._as_stored(key)
        dict.__delitem__(self, here)
        if isinstance(here, str):
            self._index().pop(path_key(here), None)

    def __contains__(self, key):
        return dict.__contains__(self, self._as_stored(key))

    def __ior__(self, other):
        self.update(other)
        return self

    def get(self, key, fallback=None):
        return dict.get(self, self._as_stored(key), fallback)

    def setdefault(self, key, fallback=None):
        here = self._as_stored(key)
        if dict.__contains__(self, here):
            return dict.__getitem__(self, here)
        self[key] = fallback
        return fallback

    def pop(self, key, *fallback):
        here = self._as_stored(key)
        got = dict.pop(self, here, *fallback)
        if isinstance(here, str):
            self._index().pop(path_key(here), None)
        return got

    def popitem(self):
        key, value = dict.popitem(self)
        if isinstance(key, str):
            self._index().pop(path_key(key), None)
        return key, value

    def clear(self):
        dict.clear(self)
        self._index().clear()

    def update(self, *given, **named):
        for other in given:
            pairs = other.items() if hasattr(other, "items") else other
            for key, value in pairs:
                self[key] = value
        for key, value in named.items():
            self[key] = value

    def copy(self):
        return ByFile(self)


class FileSet(set):
    """A set of files: one entry per file, whatever it is called.

    The companion to ByFile, and for the same reason. Only the members
    that are strings are put into shape; anything else passes through.
    """

    def __init__(self, given=()):
        set.__init__(self)
        self.update(given)

    @staticmethod
    def _shape(item):
        return path_key(item) if isinstance(item, str) else item

    def __contains__(self, item):
        return set.__contains__(self, self._shape(item))

    def add(self, item):
        set.add(self, self._shape(item))

    def discard(self, item):
        set.discard(self, self._shape(item))

    def remove(self, item):
        set.remove(self, self._shape(item))

    def update(self, *given):
        for other in given:
            for item in other or ():
                self.add(item)

    def difference_update(self, *given):
        for other in given:
            for item in other or ():
                self.discard(item)


def file_stamp(path):
    """Identify a file by what changes when it is written to.

    By the real path, not the one the caller typed: a symbolic link
    gives the same file two names and has it measured twice. Nothing
    reads the path back out of this -- it is a key and nothing else --
    so resolving the link costs microseconds and saves a process start.
    """
    try:
        s = os.stat(path)
    except OSError:
        return None
    return (os.path.realpath(path), int(s.st_mtime_ns), int(s.st_size))














def _ffprobe_text(path):
    return subprocess.run(["ffprobe", "-v", "error", "-print_format", "json",
                           "-show_format", "-show_streams", path],
                          capture_output=True).stdout


def cache_folder(sub=""):
    """Return the folder the program may keep its intermediate state in."""
    # VPM_CACHE points the whole thing somewhere else. The test suite
    # sets it: a test run has no business leaving envelopes, preflight
    # measurements and a compiled recogniser in the cache of whoever
    # happens to run it.
    base = os.environ.get("VPM_CACHE") or ""
    if not base:
        if sys.platform == "darwin":
            base = os.path.expanduser("~/Library/Caches")
        elif os.name == "nt":
            base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        else:
            base = (os.environ.get("XDG_CACHE_HOME")
                     or os.path.expanduser("~/.cache"))
    folder = os.path.join(base, "videopodcast-magic", sub)
    try:
        os.makedirs(folder, exist_ok=True)
    except OSError:
        return None
    return folder


def clean_old_files(folder, days=30):
    """Discard what has lain in this folder untouched for that long.

    One reader for both stores. A cache folder that only ever grows is
    a folder somebody finds one day and does not dare to delete.
    """
    if not folder:
        return
    limit = time.time() - days * 86400
    try:
        names = os.listdir(folder)
    except OSError:
        return
    for name in names:
        one = os.path.join(folder, name)
        try:
            if os.path.getmtime(one) < limit:
                os.unlink(one)
        except OSError:
            continue


def write_beside_then_move(file_path, data):
    """Write bytes so that no half-written file is ever read.

    Beside it and then moved into place: a run broken off halfway would
    otherwise leave half a file behind, and these files are read as
    measurements on every later start. Two runs writing the same one at
    the same moment is fine as well -- one of them wins whole.
    """
    if not file_path:
        return
    try:
        fd, beside = tempfile.mkstemp(dir=os.path.dirname(file_path),
                                      prefix=".vpm_", suffix=".part")
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(beside, file_path)
    except OSError:
        return


def settings_folder(make=False):
    """The folder somebody's own choices are kept in, or None.

    Not the cache: that is the one folder everybody is told may be
    deleted, and deleting it must not change the language the window
    speaks. So Application Support and not Caches, APPDATA and not
    LOCALAPPDATA -- a choice follows somebody onto the next machine,
    a measurement does not. VPM_SETTINGS points it somewhere else.
    """
    base = os.environ.get("VPM_SETTINGS") or ""
    if not base:
        # A test run marks itself with VPM_SILENT and has no business
        # in the settings of whoever started it -- the guard
        # key_store_off_limits() puts before the credential store, for
        # the same reason. A test with business here names its own.
        if os.environ.get("VPM_SILENT"):
            return None
        if sys.platform == "darwin":
            base = os.path.expanduser("~/Library/Application Support")
        elif os.name == "nt":
            base = os.environ.get("APPDATA") or os.path.expanduser("~")
        else:
            base = (os.environ.get("XDG_CONFIG_HOME")
                    or os.path.expanduser("~/.config"))
    folder = os.path.join(base, "videopodcast-magic")
    # Only a write asks for the folder to be built. Reading is what
    # every start does, and a run in which nobody chooses anything
    # must not leave an empty folder behind for having looked.
    if not make:
        return folder
    try:
        os.makedirs(folder, exist_ok=True)
    except OSError:
        return None
    return folder


def settings_file(make=False):
    """The file those choices stand in, or None where there is no place."""
    folder = settings_folder(make)
    return os.path.join(folder, "settings.json") if folder else None


# Read once and kept, under the file it was read from: that file is
# fixed within a run but not within a test, which points VPM_SETTINGS
# somewhere else and asks again. The same shape as _API_KEY.
_SETTINGS = {}


def forget_settings():
    """Read the settings file again the next time it is asked for."""
    _SETTINGS.clear()


def read_settings(path):
    """That file as a dictionary, empty wherever it cannot be had.

    Every way this can go wrong ends in the same answer, because that
    answer is what the program does with no file at all: ask the
    system. A remembered choice is a convenience, and a convenience
    that can stop a start is worse than no convenience.
    """
    if not path:
        return {}
    try:
        with open(path, "rb") as f:
            kept = json.loads(f.read().decode("utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return {}
    # A file holding a list or a number parses and is still not a
    # settings file; without this the first .get() on it raises.
    return kept if isinstance(kept, dict) else {}


def settings():
    """Everything kept from earlier runs, as a dictionary."""
    path = settings_file()
    if path not in _SETTINGS:
        _SETTINGS[path] = read_settings(path)
    return _SETTINGS[path]


def keep_setting(name, value):
    """Write one choice down for the next run. True if it went.

    Read, change the one entry, write the whole file back: an entry
    this version knows nothing about survives a version that does not
    know it, so an older copy started by accident does not throw away
    what a newer one wrote. That is what leaves room for the second
    setting and the third, and the language is only the first.
    """
    path = settings_file(make=True)
    if not path:
        return False
    kept = dict(settings())
    kept[name] = value
    try:
        data = json.dumps(kept, indent=1, sort_keys=True).encode("utf-8")
    except (TypeError, ValueError):
        return False
    write_beside_then_move(path, data)
    forget_settings()
    return read_settings(path).get(name) == value


EXT_MARK = "[EXT]"


ENV_MARK = "[ENV]"


BAD_MARK = "[BAD]"


TIME_MARK = "[TIME]"

# When this run began. The bundle a start from the Dock goes through
# puts its own second into VPM_STARTED before it hands over, because
# what happens before Python is running cannot be timed from inside it
# -- and that was exactly the ten seconds nobody could name on 5.9.2026.
_BEGAN = time.time()


def mark_time(what):
    """Write down how far into the start this is.

    Into the log and nowhere else. Five of these say where a slow start
    spends its time, which no amount of reading the source settles.
    """
    began, whence = _BEGAN, "this program"
    outside = (os.environ.get("VPM_STARTED") or "").strip()
    if outside.replace(".", "", 1).isdigit():
        began, whence = float(outside), "the click"
    log_aside("%s %s  %6.2f s since %s  %s"
              % (TIME_MARK, time.strftime("%H:%M:%S"),
                 time.time() - began, whence, what))


_LOG_ASIDE = []


def inside_folder(here, folder, paths=os.path):
    """Is that file inside this folder, however the two are spelled?

    One folder answers to more than one name: a link leads to it under
    another, and Python 3.10 on Windows spells the library folder lib
    where sysconfig spells it Lib. Held against each other as text they
    say no about one folder. The path module is an argument so that
    this machine can be asked what another one makes of two names.
    """
    here = paths.normcase(paths.realpath(here))
    folder = paths.normcase(paths.realpath(folder))
    return here.startswith(folder + paths.sep)


def installed_by_a_package_manager():
    """The folder a package manager owns this file in, or "".

    Two things hang on it. An installed copy is not written over by
    the self-update: something else keeps the record of which version
    is there, and writing the file would leave that record wrong. And
    an installed copy does not keep its log beside itself: that folder
    belongs to pip, not to the person running the program.
    """
    import sysconfig
    import site
    # site.USER_SITE, not getusersitepackages(): the call raises where
    # the user folder is switched off, the name is always there, and it
    # is None when there is no such folder.
    owned = [sysconfig.get_paths().get(k) for k in ("purelib", "platlib")]
    owned.append(site.USER_SITE)
    for folder in owned:
        if folder and inside_folder(__file__, folder):
            return folder
    return ""


def log_folder():
    """The folder a log belongs in on this system, or None.

    Neither the cache nor the settings: the cache is the one folder
    everybody is told they may delete, and a setting follows somebody
    to the next machine while a log says what happened on this one.
    Every platform keeps a third place for exactly that, named beside
    each branch below. VPM_LOGS points the whole thing somewhere else.
    """
    base = os.environ.get("VPM_LOGS") or ""
    if base:
        folder = os.path.join(base, "videopodcast-magic")
    elif os.environ.get("VPM_SILENT"):
        # A test run has no business in the log folder of whoever
        # started it, and the suite already points VPM_CACHE at a
        # throwaway. A test with business here names its own VPM_LOGS.
        return cache_folder("logs")
    elif sys.platform == "darwin":
        # What Console.app shows.
        folder = os.path.expanduser("~/Library/Logs/videopodcast-magic")
    elif os.name == "nt":
        # LOCALAPPDATA and not APPDATA: a log must not travel with a
        # roaming profile. Its own folder beside the cache, so that
        # emptying the cache does not take it along.
        folder = os.path.join(os.environ.get("LOCALAPPDATA")
                              or os.path.expanduser("~"),
                              "videopodcast-magic", "Logs")
    else:
        # XDG names this one for logs in so many words.
        folder = os.path.join(os.environ.get("XDG_STATE_HOME")
                              or os.path.expanduser("~/.local/state"),
                              "videopodcast-magic")
    try:
        os.makedirs(folder, exist_ok=True)
    except OSError:
        return None
    return folder


def log_path():
    """Where the log goes: beside the program, or in the user's place.

    Beside the program it is found without searching, and that is
    right for a copy somebody downloaded into a folder of their own.
    For an installed copy "beside the program" is site-packages, which
    pip owns: written over at the next install, sometimes read-only,
    and no place for anybody's data. So an installed run writes where
    this system keeps logs, and so does a copy that cannot write.
    """
    if not installed_by_a_package_manager():
        here = os.path.dirname(os.path.abspath(__file__))
        if os.path.isdir(here) and os.access(here, os.W_OK):
            return os.path.join(here, "videopodcast-magic.log")
    folder = log_folder()
    return os.path.join(folder, "videopodcast-magic.log") if folder else None


def log_aside(text):
    """Write one line into the log file only, never to the console.

    What a run prints is read by a person and by the window, and a
    diagnostic line landing between two progress bars tears them
    apart. This goes past both descriptors into the file itself.
    """
    if not _LOG_ASIDE:
        try:
            where = log_path()
            _LOG_ASIDE.append(open(where, "a", buffering=1,
                                   encoding="utf-8", errors="replace")
                              if where else None)
        except Exception:
            _LOG_ASIDE.append(None)
    if _LOG_ASIDE[0] is None:
        return
    try:
        _LOG_ASIDE[0].write(text + "\n")
    except Exception:
        # A write that failed once fails again -- a full disc, a file
        # taken away. Stop rather than throw once per line from here.
        _LOG_ASIDE[0] = None


# The same tool on the same file over and over -- the fine measurement
# asks for nine stretches out of two files -- is held back and written
# as one line with the count and the total.
_SAME_AGAIN = {"what": None, "times": 0, "seconds": 0.0}


def outside_say(tool, about, seconds=None, what=None):
    """One line about work that happens outside this program's own code.

    ffmpeg, ffprobe and the two models are where a run spends its
    minutes, and from outside a file read once and a file read four
    times look the same. A stored answer says so too, so every
    measurement in the log is either a call or the line saying why
    there was none.
    """
    same = (tool, about, what)
    if _SAME_AGAIN["what"] == same and seconds is not None:
        _SAME_AGAIN["times"] += 1
        _SAME_AGAIN["seconds"] += seconds
        return
    outside_flush()
    if seconds is None:
        log_aside("%s %s  %-13s %-22s %s"
                  % (EXT_MARK, time.strftime("%H:%M:%S"), tool,
                     what or "started", about))
        return
    _SAME_AGAIN.update({"what": same, "times": 1, "seconds": seconds})

def outside_flush():
    """Write out what was held back, as one line."""
    held = _SAME_AGAIN["what"]
    if not held:
        return
    tool, about, what = held
    times, seconds = _SAME_AGAIN["times"], _SAME_AGAIN["seconds"]
    log_aside("%s %s  %-13s %-22s %s"
              % (EXT_MARK, time.strftime("%H:%M:%S"), tool,
                 what or ("%.2f s" % seconds if times == 1
                          else "%d calls, %.2f s" % (times, seconds)),
                 about))
    _SAME_AGAIN.update({"what": None, "times": 0, "seconds": 0.0})



def probe_cache_path(api_key):
    """Where a measurement of a file is kept between runs, or None."""
    folder = cache_folder("probes")
    if not folder:
        return None
    mark = hashlib.sha1(repr(api_key).encode("utf-8")).hexdigest()[:32]
    return os.path.join(folder, mark + ".bin")


def probe_kept(api_key):
    """What was measured of this file before, or None to measure again."""
    file_path = probe_cache_path(api_key)
    if not file_path:
        return None
    try:
        with open(file_path, "rb") as f:
            got = f.read()
    except OSError:
        return None
    # An empty file is a write that was cut off, not a measurement.
    return got or None


def probe_keep(api_key, got):
    """Keep a measurement for the next run."""
    if got:
        write_beside_then_move(probe_cache_path(api_key), got)


def clean_probe_cache(days=30):
    """Discard stale probes; once per run is enough."""
    clean_old_files(cache_folder("probes"), days)


def probe_remember(name, path, work, keep=False, as_json=False):
    """Return a measured property of a file, asking only once.

    Keyed on size and modification time: a changed file is measured
    again, one that cannot be stat'ed every time. With *keep* the
    answer outlives the run, which is what a measurement costing half
    a minute needs; *as_json* is for one that is not text.

    A kept answer carries the recipe in its *name* -- see recipe_mark.
    """
    stamp = file_stamp(path)
    if stamp is None:
        return work()
    api_key = (name,) + stamp
    if api_key in _PROBE:
        # Not said. This one is asked thousands of times in a table
        # rebuild, and a line for each would drown the log it is
        # meant to make readable -- and cost more than the lookup.
        return _PROBE[api_key]
    got = probe_kept(api_key) if keep else None
    if got is not None and as_json:
        try:
            got = json.loads(got)
        except Exception:
            got = None          # half a write, or another version
    if got is not None:
        # This one is worth a line: it is the measurement that would
        # otherwise have cost seconds.
        outside_say(name.split("-")[0], os.path.basename(path),
                    what="read back from the store")
    if got is None:
        got = work()
        if keep:
            probe_keep(api_key, json.dumps(got).encode("utf-8")
                       if as_json else got)
    if len(_PROBE) > 4000:
        _PROBE.clear()
    _PROBE[api_key] = got
    return _PROBE[api_key]


def probe_has(name, path):
    """Report whether this measurement of this file is already there."""
    stamp = file_stamp(path)
    return stamp is not None and (name,) + stamp in _PROBE


def ffprobe_json(path):
    """Return what ffprobe says about a file.

    Parsed afresh from the remembered text each time, so a caller that
    changes the dictionary cannot affect the next one.
    """
    out = probe_remember("ffprobe", path, lambda: _ffprobe_text(path),
                         keep=True)
    return json.loads(out or b"{}")


def timecode_string(seconds, fps=30.0):
    if seconds < 0:
        seconds = 0.0
    f = int(round((seconds - int(seconds)) * fps))
    s = int(seconds)
    if f >= int(round(fps)):
        f, s = 0, s + 1
    return "%02d:%02d:%02d:%02d" % (s // 3600 % 24, s % 3600 // 60, s % 60, f)


def csv_line(values):
    """One row of a CSV file: comma separated, quoted where it matters.

    Comma and full stop, in every language. These files are read by other
    programs and compared across months; a separator that follows the
    language of the run would make two runs incomparable.
    """
    out = []
    for x in values:
        x = str(x)
        if any(c in x for c in ',";\r\n'):
            x = '"%s"' % x.replace('"', '""')
        out.append(x)
    return ",".join(out) + "\n"


def parse_timecode(s, fps=30.0):
    """Parse '6.4087', '0:06', '1:23:45' or '17:15:56:12' into seconds.

    Drop frame writes the last colon as a semicolon, '17:15:56;12'. That
    is the same value; how the frames are counted is a question for
    timecode_to_frames, not for a length in seconds.
    """
    t = str(s).strip().replace(";", ":")
    p = t.split(":")
    if len(p) == 4:
        return float(p[0]) * 3600 + float(p[1]) * 60 + float(p[2]) + float(p[3]) / fps
    if len(p) == 3:
        return float(p[0]) * 3600 + float(p[1]) * 60 + float(p[2])
    if len(p) == 2:
        return float(p[0]) * 60 + float(p[1])
    return float(t)


def frame_rate_fraction(fps):
    """Return a frame rate as a fraction: 29.97 -> 30000/1001.

    iXML requires a fraction rather than a decimal.
    """
    for whole, num, the_one in ((23.976, 24000, 1001), (29.97, 30000, 1001),
                           (47.952, 48000, 1001), (59.94, 60000, 1001),
                           (119.88, 120000, 1001)):
        if abs(fps - whole) < 0.02:
            return num, the_one
    return int(round(fps)), 1


def is_drop_frame(tc):
    """Report whether a timecode string is drop frame.

    The notation decides, not the frame rate: drop frame uses a semicolon
    before the frames. 29.97 exists in both flavours, so guessing from the
    rate is wrong half the time. No marker means non-drop.
    """
    return ";" in str(tc or "")


def timecode_moved(tc, by_s, fps=30.0):
    """A timecode string moved on by *by_s* seconds.

    Cutting a head off a camera moves the moment its first frame was
    taken, and whoever plays the file reads that moment off the
    timecode. The semicolon of drop frame is kept: losing it turns the
    same frame into a different time of day for whoever reads it.
    """
    moved = timecode_string(parse_timecode(tc, fps) + by_s, fps)
    if is_drop_frame(tc):
        head, _sep, frames = moved.rpartition(":")
        moved = head + ";" + frames
    return moved


def build_ixml(name, tr, fps, bits=24, channels=1, df=False):
    """Build the iXML block for one track.

    Resolve is happy with bext alone, but Premiere and Media Composer fall
    back to iXML. Writing both costs nothing.
    """
    num, the_one = frame_rate_fraction(fps)
    ndf = not df
    tracks = "".join(
        "    <TRACK>\n      <CHANNEL_INDEX>%d</CHANNEL_INDEX>\n"
        "      <INTERLEAVE_INDEX>%d</INTERLEAVE_INDEX>\n"
        "      <NAME>%s</NAME>\n    </TRACK>\n" % (k, k, _xml_escape(name))
        for k in range(1, max(1, channels) + 1))
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n<BWFXML>\n'
        '  <IXML_VERSION>1.5</IXML_VERSION>\n'
        '  <PROJECT>%s</PROJECT>\n'
        '  <TAPE>%s</TAPE>\n'
        '  <TAKE>1</TAKE>\n'
        '  <SPEED>\n'
        '    <NOTE>videopodcast-magic</NOTE>\n'
        '    <MASTER_SPEED>%d/%d</MASTER_SPEED>\n'
        '    <CURRENT_SPEED>%d/%d</CURRENT_SPEED>\n'
        '    <TIMECODE_RATE>%d/%d</TIMECODE_RATE>\n'
        '    <TIMECODE_FLAG>%s</TIMECODE_FLAG>\n'
        '    <FILE_SAMPLE_RATE>%d</FILE_SAMPLE_RATE>\n'
        '    <AUDIO_BIT_DEPTH>%d</AUDIO_BIT_DEPTH>\n'
        '    <TIMESTAMP_SAMPLES_SINCE_MIDNIGHT_HI>%d'
        '</TIMESTAMP_SAMPLES_SINCE_MIDNIGHT_HI>\n'
        '    <TIMESTAMP_SAMPLES_SINCE_MIDNIGHT_LO>%d'
        '</TIMESTAMP_SAMPLES_SINCE_MIDNIGHT_LO>\n'
        '  </SPEED>\n'
        '  <TRACK_LIST>\n    <TRACK_COUNT>%d</TRACK_COUNT>\n%s'
        '  </TRACK_LIST>\n</BWFXML>\n'
        % (_xml_escape(name), _xml_escape(name), num, the_one, num, the_one, num, the_one,
           "NDF" if ndf else "DF", SR, bits,
           tr >> 32, tr & 0xFFFFFFFF, max(1, channels), tracks))


def _xml_escape(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def append_ixml(file_path, xml):
    """Append the iXML block as a RIFF chunk and fix up the RIFF size."""
    payload = xml.encode("utf-8")
    if len(payload) % 2:
        payload += b"\x00"
    with open(file_path, "r+b") as f:
        f.seek(0, os.SEEK_END)
        end = f.tell()
        f.write(b"iXML" + struct.pack("<I", len(payload)) + payload)
        f.seek(4)
        f.write(struct.pack("<I", end + len(payload)))


def parse_time_point(s, fps=30.0):
    """Parse a --in-point/--out-point time.

    Returns (seconds, absolute). Absolute means wall clock since
    midnight, i.e. a timecode; everything else counts from the start of
    the window. A leading plus is optional, a bare number is seconds,
    and a negative value measures back from the window end -- that one
    only for --out-point.
    """
    t = str(s).strip()
    if not t:
        return None, False
    minus = t.startswith("-")
    absolute = t.count(":") >= 2 and not t.startswith(("+", "-"))
    value = parse_timecode(t.lstrip("+-"), fps)
    return (-value if minus else value), absolute


def as_relative_time(seconds):
    """Format a position the way --in-point expects it."""
    ms = int(round(max(0.0, seconds) * 1000))
    s = ms // 1000
    return "+%d:%02d:%02d.%03d" % (s // 3600, s % 3600 // 60, s % 60,
                                   ms % 1000)


def as_hms(sec, mark=None):
    """Write a duration as h:mm:ss with milliseconds.

    *mark* overrides the decimal point. A file that other programs read
    passes ".", so what is in it does not depend on the language.
    """
    # Round to milliseconds first, then split -- otherwise 119.9995 s
    # comes out as "0:01:59.1000".
    ms = int(round(abs(sec) * 1000))
    s = ms // 1000
    return "%s%d:%02d:%02d%s%03d" % ("-" if sec < 0 else "", s // 3600,
                                     s % 3600 // 60, s % 60,
                                     T(".") if mark is None else mark,
                                     ms % 1000)


def sample_count(path):
    """Return the length of a file in samples at the working rate."""
    return probe_remember("samples", path, lambda: _sample_count(path))


def _sample_count(path):
    # Out of the one description of the file rather than a second call
    # of its own: duration_ts counts samples exactly, where a duration
    # in seconds has already been rounded.
    d = ffprobe_json(path)
    a = next((x for x in d.get("streams", [])
              if x.get("codec_type") == "audio"), {})
    try:
        n, sr = int(a["duration_ts"]), int(a.get("sample_rate") or SR)
        return int(round(n * SR / sr)) if sr and sr != SR else n
    except (KeyError, TypeError, ValueError):
        pass
    duration = float(a.get("duration") or d.get("format", {}).get("duration") or 0)
    return int(round(duration * SR))


def bext_time_reference(path):
    """Return TimeReference from the bext chunk in samples, or None."""
    return probe_remember("bext", path, lambda: _bext_time_reference(path))


def _bext_time_reference(path):
    try:
        f = open(path, "rb")
    except OSError:
        return None
    with f:
        if f.read(4) not in (b"RIFF", b"RF64"):
            return None
        f.seek(12)
        while True:
            h = f.read(8)
            if len(h) < 8:
                return None
            cid, sz = h[:4], struct.unpack("<I", h[4:8])[0]
            if cid == b"bext":
                b = f.read(sz)
                return struct.unpack("<Q", b[338:346])[0] if len(b) >= 346 else None
            f.seek(sz + (sz & 1), os.SEEK_CUR)


DAY_S = 24 * 60 * 60


def unwrap_day(value, near):
    """Move *value* by whole days until it sits closest to *near*.

    A timecode starts over at midnight, so a recording running across it
    looks 23 hours away and every difference is out by a day. Nothing is
    added to either axis -- that would make one absolute and the other
    not -- so the two meet only where they are compared. Half a day is
    the fence: past it a night is indistinguishable from a day's gap.
    """
    if value is None or near is None:
        return value
    return value - DAY_S * round((value - near) / float(DAY_S))


def clocks_apart(spans):
    """Which of these time windows share their time with no other.

    *spans* is [(start, length, key), ...] read off the timecode.
    Material from one recording overlaps; a window overlapping with none
    came off a clock never set. All are first brought onto one axis
    around the middle, or a shoot across midnight would look the same.
    Fewer than three say nothing. Returns (apart, moved, placed).
    """
    spans = [(float(a), max(1.0, float(n or 0.0)), k) for a, n, k in spans]
    if len(spans) < 3:
        return set(), [], spans

    def alone(mine, start, wide, among):
        return not any(i != mine and start < b + m and b < start + wide
                       for i, (b, m, _k) in enumerate(among))

    middle = sorted(a for a, _n, _k in spans)[len(spans) // 2]
    moved, placed = [], []
    for i, (a, n, k) in enumerate(spans):
        shifted = unwrap_day(a, middle)
        # A file starting at 00:00:00 is not a recording that began in
        # the first second after midnight, it is a recorder whose clock
        # was never set -- and unwrapping it would drop it neatly among
        # the cameras and hide exactly the fault this is here for.
        if a < 1.0:
            shifted = a
        # Moving a file a whole day is a claim, and only worth making if
        # the file then lands among the others. A recorder left hours
        # out also moves under plain arithmetic and still overlaps
        # nothing, so the move is taken back.
        if shifted != a and not alone(i, shifted, n, spans):
            moved.append(k)
            placed.append((shifted, n, k))
        else:
            placed.append((a, n, k))
    return (set(k for i, (a, n, k) in enumerate(placed)
                if alone(i, a, n, placed)), moved, placed)




def picture_rate(probed):
    """The frame rate of the picture in an ffprobe answer, or nothing.

    ffprobe writes it as a fraction, '30000/1001' for 29.97. The mean
    over the file comes first, because it is frames over duration and
    therefore always a real number; the nominal rate is what the
    container claims and is a timebase in a few odd files.
    """
    v = next((s for s in probed.get("streams", ())
              if s.get("codec_type") == "video"), None)
    for key in ("avg_frame_rate", "r_frame_rate"):
        parts = str((v or {}).get(key) or "").split("/")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            if int(parts[0]) and int(parts[1]):
                return int(parts[0]) / float(int(parts[1]))
    return None


def file_timecode(path, fps=None):
    """Return the start time in seconds from bext or a timecode track.

    The frames of a timecode are frames, so the rate decides what they
    are worth: read at the wrong rate the start lands whole frames out.
    Where no rate is passed the file's own is taken. A sound file has
    none, so its frames belong to the reference picture and a caller who
    knows that rate passes it; without one 30 is the fallback.
    """
    tr = bext_time_reference(path)
    if tr is not None:
        return tr / float(SR)
    d = ffprobe_json(path)
    rate = float(fps) if fps else (picture_rate(d) or 30.0)
    # The tracks before the file: a track's clock is what the camera
    # wrote, the file level is what ffmpeg made of it, and the camera
    # wins where they disagree. A file that keeps a clock nowhere else
    # -- MXF and AVI do -- is still read, only afterwards.
    for source in [s.get("tags", {}) or {} for s in d.get("streams", [])] +\
                  [d.get("format", {}).get("tags", {})]:
        if source.get("timecode"):
            try:
                return parse_timecode(source["timecode"], rate)
            except Exception:
                pass
    return None


#----------------------------------------------------- The spoken language

# The audio track tag and the recognition language are two different
# code systems: ffmpeg wants three letters after ISO 639-2/B, both
# recognisers the two letter code. Only the plausible ones are listed;
# anything else is passed on as it stands and works itself out.
SPEECH_CODES = {
    "ger": "de", "deu": "de", "eng": "en", "fra": "fr", "fre": "fr",
    "spa": "es", "ita": "it", "nld": "nl", "dut": "nl", "por": "pt",
    "pol": "pl", "rus": "ru", "swe": "sv", "dan": "da", "nor": "no",
    "fin": "fi", "ces": "cs", "cze": "cs", "tur": "tr", "ell": "el",
    "gre": "el", "jpn": "ja", "zho": "zh", "chi": "zh", "kor": "ko",
    "ara": "ar", "heb": "he", "hun": "hu", "ron": "ro", "rum": "ro",
    "ukr": "uk", "cat": "ca",
}


def speech_locale(language):
    """The recogniser's code for the tag the interface carries.

    The Language field and --speech-language hold what ffmpeg wants on
    the audio track: three letters. Both recognisers want the two-letter
    code. "ger" matched no locale and was dropped without a word, so the
    machine's own language decided and the field did nothing -- asked
    for "eng" on a German Mac, the recognition ran in de_DE.
    """
    tag = (language or "").strip()
    return SPEECH_CODES.get(tag.lower(), tag)


# What the interface offers. The tag is what ffmpeg wants on the audio
# track, and the recogniser is told which language to expect.
# Only languages with both are listed -- offering one whose recognition
# code is unknown would promise a transcript that cannot come.
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


#-------------------------------------------------------- What a file says

def size_in_mb(file_path):
    try:
        return os.path.getsize(file_path) / 1e6
    except OSError:
        return 0.0


def as_data_size(mb_value):
    """Format a byte count for reading: 542 MB, 1,024 MB, 28.9 GB."""
    if mb_value >= 1000:
        return decimal_text("%.1f GB" % (mb_value / 1000.0))
    return "%s MB" % group_text(math.ceil(mb_value))


def audio_summary(file_path):
    """Return key facts about an audio file as (label, value) pairs."""
    d = ffprobe_json(file_path)
    a = next((x for x in d.get("streams", []) if x.get("codec_type") == "audio"), {})
    if str(a.get("sample_fmt", "")).startswith("flt"):
        depth = "32 bit float"
    else:
        depth = "%s bit" % (a.get("bits_per_raw_sample")
                            or a.get("bits_per_sample") or "?")
    channels = channel_text(a.get("channels"))
    tc = file_timecode(file_path)
    # Read at the file's own rate, so shown at it too: at 25 the frames
    # of the timecode are worth 1/25 s, and a line printed at 30 would
    # give the file back a timecode it never carried.
    rate = picture_rate(d) or 30.0
    return [("Format", "%s, %s, %s Hz, %s" % (a.get("codec_name", "?"), depth,
                                              a.get("sample_rate", "?"), channels)),
            (T('Length'), "%s  (%s)  --  %s"
             % (as_hms(sample_count(file_path) / float(SR)), as_data_size(size_in_mb(file_path)),
                "Timecode %s" % timecode_string(tc, rate) if tc is not None
                else T('no timecode')))]


MOV_CONTAINERS = (b"moov", b"trak", b"mdia", b"minf", b"stbl", b"wave")


def _mov_atoms(f, end):
    """Enumerate atoms between the current offset and end.

    Yields (kind, start of payload, end of atom) per atom.
    """
    while True:
        begin = f.tell()
        if begin + 8 > end:
            return
        head = f.read(8)
        if len(head) < 8:
            return
        size = struct.unpack(">I", head[:4])[0]
        kind = head[4:8]
        if size == 1:
            raw = f.read(8)
            if len(raw) < 8:
                return
            size = struct.unpack(">Q", raw)[0]
        elif size == 0:
            size = end - begin
        if size < 8:
            return
        stop = min(end, begin + size)
        yield kind, f.tell(), stop
        f.seek(stop)


def _read_colr_atom(f, end, depth=0):
    if depth > 8:
        return None
    for kind, content, stop in _mov_atoms(f, end):
        if kind == b"colr":
            f.seek(content)
            raw = f.read(min(19, stop - content))
            if len(raw) >= 10 and raw[:4] in (b"nclc", b"nclx"):
                prim, trc, mat = struct.unpack(">HHH", raw[4:10])
                full = (bool(raw[10] & 0x80)
                        if raw[:4] == b"nclx" and len(raw) >= 11 else None)
                return prim, trc, mat, full
            continue
        if kind in MOV_CONTAINERS:
            f.seek(content)
            hit = _read_colr_atom(f, stop, depth + 1)
            if hit:
                return hit
        elif kind == b"stsd":
            # Version, flags, count, then the entries.
            f.seek(content + 8)
            for _kind2, content2, end2 in _mov_atoms(f, stop):
                # Video entry: 78 bytes of fixed header, then sub-atoms.
                if end2 - content2 <= 78:
                    continue
                f.seek(content2 + 78)
                hit = _read_colr_atom(f, end2, depth + 1)
                if hit:
                    return hit
    return None


def colour_arguments(source, extend=False):
    """Pass the source colour tags through explicitly.

    With -c:v copy ffmpeg rewrites the colr box from its own values and
    replaces anything it does not know, so Resolve no longer recognises
    the input colour space. With fill_gaps=True one gap some cameras
    leave is closed: a BT.2020 matrix with unspecified primaries makes
    the primaries BT.2020 too. Nothing is invented.
    """
    values = mov_colour_tags(source)
    if not values:
        return []
    prim, trc, mat, full = values
    if extend and prim == 2 and mat == MATRIX_BT2020:
        prim = PRIMARIES_BT2020
    opts = ["-color_primaries", str(prim), "-color_trc", str(trc),
          "-colorspace", str(mat)]
    if full is not None:
        opts += ["-color_range", "pc" if full else "tv"]
    return opts


def camera_metadata(file_path):
    """Read the camera's QuickTime metadata keys.

    They name the device and app used. Resolve reads them; without them
    it cannot tell that a phone recorded in log, because the colr box of
    those files reports the transfer function as unspecified. Only the
    com. keys, because these have to reach the new file unchanged, and a
    plain key such as encoder is rewritten by whatever wrote it.
    """
    try:
        d = ffprobe_json(file_path)
    except Exception:
        return {}
    tags = ((d or {}).get("format") or {}).get("tags") or {}
    return {k: v for k, v in tags.items() if k.startswith("com.")}


# The one data track ffmpeg writes whole. mebx -- what an iPhone writes
# -- and camm, rtmd and fdsc arrive with an empty sample description.
# And never tmcd: ffmpeg then drops the timecode this program worked
# out, and the camera lands in the wrong place on the common axis.
DATA_TAGS_TO_KEEP = ("gpmd",)


def data_track_tags(file_path):
    """The tags of the file's data tracks, in the order ffprobe gives them."""
    try:
        d = ffprobe_json(file_path)
    except Exception:
        return []
    return [(s.get("codec_tag_string") or "?").strip()
            for s in (d or {}).get("streams", [])
            if s.get("codec_type") == "data"]


def data_track_maps(file_path):
    """The -map arguments for the data tracks that may be carried over."""
    out = []
    for i, tag in enumerate(data_track_tags(file_path)):
        if tag in DATA_TAGS_TO_KEEP:
            out += ["-map", "0:d:%d" % i]
    return out


def check_data_tracks(source, target):
    """Report which of the camera's data tracks reached the new file.

    The timecode track is not counted: this program writes one of its
    own, so it is replaced rather than lost.
    """
    a = [t for t in data_track_tags(source) if t != "tmcd"]
    if not a:
        return
    b = data_track_tags(target)
    kept = [t for t in a if t in b]
    left = [t for t in a if t not in DATA_TAGS_TO_KEEP]
    if left:
        print(as_warn(T('  Data tracks:     %s left out -- ffmpeg cannot '
                        'write it') % ", ".join(left)))
    if kept:
        print(T('  Data tracks:     %s carried over') % ", ".join(kept))


# What the container says about itself and who wrote it. Every rewrite
# moves these, and none of them came off a camera, so counting them
# would claim camera data the camera never wrote.
CONTAINER_TAGS = ("major_brand", "minor_version", "compatible_brands",
                  "encoder")


def file_metadata(file_path):
    """Every metadata key of the file, minus what the container owns."""
    try:
        d = ffprobe_json(file_path)
    except Exception:
        return {}
    tags = ((d or {}).get("format") or {}).get("tags") or {}
    return {k: v for k, v in tags.items() if k.lower() not in CONTAINER_TAGS}


def check_camera_metadata(source, target):
    """Report whether the camera metadata keys survived the copy.

    Every key the source carries, not only the Apple ones: a camera
    writing none of those used to get no line at all. Presence is
    compared and not the value, because some values change on purpose
    -- the timecode is worked out afresh -- and a check reading those
    as a loss would cry wolf on every run.
    """
    a, b = file_metadata(source), file_metadata(target)
    if not a:
        print(T('  Camera data:     the source carries none'))
        return
    missing = [k for k in a if k not in b]
    if not missing:
        print(T('  Camera data:     %s keys carried over (%s)')
              % (group_text(len(a)), a.get("com.apple.quicktime.model")
                 or a.get("model")
                 or a.get("com.apple.quicktime.software") or "..."))
    else:
        print(as_warn(T('  Camera data:     Caution, %s of %s keys are '
                        'missing in the new file: %s')
                      % (group_text(len(missing)), group_text(len(a)),
                         ", ".join(missing[:4]))))
        print(T('                   Resolve may then not recognise the '
                'input colour space.'))


# Atoms in the sample description that ffmpeg drops when copying but
# Resolve reads. For iPhone recordings "logs" holds the recording
# curve, e.g. "com.apple.apple-wide-gamut.apple-log", which is how
# Resolve recognises Apple Log 2. The colr box says nothing about it.

# "gama" is the curve of older QuickTime recordings, "dvcC" and "dvvC"
# the Dolby Vision set. Not "st3d": ffmpeg writes a vexu box of its own
# beside it, and the two together make a file nothing will open, while
# every check in copy_mov_atoms passes.
ATOMS_TO_COPY = (b"logs", b"gama", b"dvcC", b"dvvC")


def _atom_boxes(data, start, end):
    """Return the boxes of one MOV level.

    Yields (start, size, kind, header length) per box.
    """
    i = start
    while i + 8 <= end:
        size = struct.unpack(">I", data[i:i + 4])[0]
        kind = data[i + 4:i + 8]
        head = 8
        if size == 1:
            if i + 16 > end:
                return
            size = struct.unpack(">Q", data[i + 8:i + 16])[0]
            head = 16
        elif size == 0:
            size = end - i
        if size < head or i + size > end:
            return
        yield i, size, kind, head
        i += size


def _find_atom(data, start, end, kind):
    for i, size, a, head in _atom_boxes(data, start, end):
        if a == kind:
            return i, size, head
    return None


def _video_track_chain(data, moov_i, moov_size, moov_head):
    """Return the video trak box and the chain down to its sample entry."""
    for t_i, t_size, t_kind, t_head in _atom_boxes(data, moov_i + moov_head,
                                           moov_i + moov_size):
        if t_kind != b"trak":
            continue
        mdia = _find_atom(data, t_i + t_head, t_i + t_size, b"mdia")
        if not mdia:
            continue
        hdlr = _find_atom(data, mdia[0] + mdia[2], mdia[0] + mdia[1],
                           b"hdlr")
        # hdlr: four bytes version and flags, four reserved, then the kind
        # of track.
        if not hdlr or data[hdlr[0] + hdlr[2] + 8:
                             hdlr[0] + hdlr[2] + 12] != b"vide":
            continue
        minf = _find_atom(data, mdia[0] + mdia[2], mdia[0] + mdia[1],
                           b"minf")
        if not minf:
            continue
        stbl = _find_atom(data, minf[0] + minf[2], minf[0] + minf[1],
                           b"stbl")
        if not stbl:
            continue
        stsd = _find_atom(data, stbl[0] + stbl[2], stbl[0] + stbl[1],
                           b"stsd")
        if not stsd:
            continue
        # In stsd: four bytes version/flags, four bytes count, then entries.
        entry = next(_atom_boxes(data, stsd[0] + stsd[2] + 8,
                              stsd[0] + stsd[1]), None)
        if not entry:
            continue
        return [(moov_i, moov_head), (t_i, t_head), (mdia[0], mdia[2]),
                (minf[0], minf[2]), (stbl[0], stbl[2]), (stsd[0], stsd[2]),
                (entry[0], entry[3])]
    return None


def _top_level_boxes(file_path):
    out = []
    total = os.path.getsize(file_path)
    with open(file_path, "rb") as f:
        pos = 0
        while pos < total - 8:
            f.seek(pos)
            head = f.read(8)
            if len(head) < 8:
                break
            size, kind = struct.unpack(">I4s", head)
            if size == 1:
                size = struct.unpack(">Q", f.read(8))[0]
            elif size == 0:
                size = total - pos
            if size < 8:
                break
            out.append((kind, pos, size))
            pos += size
    return out


# A sample description atom is an identifier, not a payload. Anything
# larger is left alone, because then the assumption no longer holds.
ATOM_LIMIT = 64 * 1024


def _verify_mov_after_edit(file_path, moov_pos, moov_old_size, above_before_value, for_it):
    """Verify the file survived the edit. An empty result means it did.

    Checked against the state before: same top level boxes at the same
    offsets, moov still last and reaching the end of file, the chain down to
    the video sample entry readable again, and the intended atoms present.
    """
    try:
        total = os.path.getsize(file_path)
        above = _top_level_boxes(file_path)
        if not above:
            return T('boxes no longer readable')
        if above[-1][0] != b"moov" or above[-1][1] != moov_pos:
            return T('moov is no longer in its place')
        if above[-1][1] + above[-1][2] != total:
            return T('moov no longer ends at the end of the file')
        if [(a, i, g) for a, i, g in above[:-1]] != \
                [(a, i, g) for a, i, g in above_before_value[:-1]]:
            return T('the media data is no longer where it was')
        if above[-1][2] <= moov_old_size:
            return T('moov has not grown')
        with open(file_path, "rb") as f:
            f.seek(above[-1][1])
            moov = f.read(above[-1][2])
        chain = _video_track_chain(moov, 0, len(moov), 8)
        if not chain:
            return T('the video track can no longer be found')
        e_i, e_head = chain[-1]
        e_size = struct.unpack(">I", moov[e_i:e_i + 4])[0]
        present = {bytes(a) for _i, _g, a, _k
                in _atom_boxes(moov, e_i + e_head + 78, e_i + e_size)}
        missing = [a.decode("latin1") for a in for_it if a not in present]
        if missing:
            return T('did not arrive: %s') % ", ".join(missing)
        # Every level has to fit exactly inside its parent, otherwise some
        # size field is wrong.
        for idx in range(len(chain) - 1):
            i, head = chain[idx]
            size = struct.unpack(">I", moov[i:i + 4])[0]
            kind_i, kind_head = chain[idx + 1]
            kind_size = struct.unpack(">I", moov[kind_i:kind_i + 4])[0]
            if not (i + head <= kind_i and kind_i + kind_size <= i + size):
                return T('a box no longer fits into its parent')
    except Exception as e:
        return T('cannot be read back (%s)') % str(e)[:60]
    return ""


def copy_mov_atoms(source, target, kinds=ATOMS_TO_COPY):
    """Copy sample description atoms from the source into the new file.

    Copied byte for byte, nothing synthesised, and only where moov sits
    at the end of the target: growing it then moves no media data and
    every offset stays valid. The result is verified and the old moov
    put back on any mismatch -- better without the atom than with a file
    nothing will open. Returns the atoms copied, [] where none were.
    """
    # Folders, missing paths and empty names occur here, and copying
    # atoms is a side step: they end it quietly rather than raise.
    for file_path in (source, target):
        if not file_path or not os.path.isfile(file_path):
            return []
    absent = []
    src_top = _top_level_boxes(source)
    src_moov = next(((p, g) for a, p, g in src_top if a == b"moov"), None)
    if not src_moov:
        return []
    with open(source, "rb") as f:
        f.seek(src_moov[0])
        src = f.read(src_moov[1])
    chain = _video_track_chain(src, 0, len(src), 8)
    if not chain:
        return []
    e_i, e_head = chain[-1]
    e_size = struct.unpack(">I", src[e_i:e_i + 4])[0]
    src_kind = bytes(src[e_i + 4:e_i + 8])       # hvc1, avc1, apcn ...
    existing = {}
    # The sub-atoms sit behind the box header and 78 bytes of fixed
    # fields of the video entry.
    for i, size, kind, head in _atom_boxes(src, e_i + e_head + 78,
                                   e_i + e_size):
        if kind not in kinds:
            continue
        if size > ATOM_LIMIT:
            print(T('  Atom %s skipped: %s bytes are too much for it.')
                  % (kind.decode("latin1"), group_text(size)))
            continue
        existing[kind] = src[i:i + size]
    if not existing:
        return []

    dst_top = _top_level_boxes(target)
    if not dst_top or dst_top[-1][0] != b"moov":
        print(T('  Cannot add atoms: moov is not at the end.'))
        return []
    dst_pos, dst_size = dst_top[-1][1], dst_top[-1][2]
    with open(target, "rb") as f:
        f.seek(dst_pos)
        dst = bytearray(f.read(dst_size))
    if len(dst) != dst_size:
        return []
    # The old moov stays in place: if the verification fails, it comes
    # back exactly as it was.
    old_moov = bytes(dst)
    chain = _video_track_chain(dst, 0, len(dst), 8)
    if not chain:
        return []
    e_i, e_head = chain[-1]
    e_size = struct.unpack(">I", dst[e_i:e_i + 4])[0]
    dst_kind = bytes(dst[e_i + 4:e_i + 8])
    if dst_kind != src_kind:
        # An atom from an HEVC description does not belong in an H.264 one.
        # The boxes fit, the contents do not.
        print(T('  Cannot add atoms: the source is %s, the target %s.') % (src_kind.decode("latin1", "replace"),
                       dst_kind.decode("latin1", "replace")))
        return []
    already = {bytes(kind) for _i, _g, kind, _k
             in _atom_boxes(dst, e_i + e_head + 78, e_i + e_size)}
    fresh = b"".join(v for k, v in existing.items() if k not in already)
    if not fresh:
        return []
    # Every box enclosing the entry grows.
    for i, _head in chain:
        size = struct.unpack(">I", dst[i:i + 4])[0]
        if size == 1:
            print(T('  Cannot add atoms: a 64 bit box is in the way.'))
            return []
        struct.pack_into(">I", dst, i, size + len(fresh))
    insert = e_i + e_size

    def moov_write(content):
        with open(target, "r+b") as f:
            f.seek(dst_pos)
            f.write(content)
            f.truncate(dst_pos + len(content))
            f.flush()
            os.fsync(f.fileno())

    for_it = [k for k in existing if k not in already]
    try:
        moov_write(bytes(dst[:insert]) + fresh + bytes(dst[insert:]))
        damage = _verify_mov_after_edit(target, dst_pos, dst_size, dst_top, for_it)
    except Exception as e:
        damage = T('while writing: %s') % str(e)[:60]
    if damage:
        try:
            moov_write(old_moov)
            back = T('the old moov is back in place')
        except Exception as e:
            back = T('ROLLBACK FAILED (%s)') % str(e)[:60]
        print(T('  Adding atoms taken back -- %s. %s')
              % (damage, back))
        return []
    return [k.decode("latin1") for k in for_it]


def _logs_atom_text(file_path):
    """Return the text of the video track logs atom, or ""."""
    try:
        above = _top_level_boxes(file_path)
        spot = next(((p, g) for a, p, g in above if a == b"moov"), None)
        if not spot:
            return ""
        with open(file_path, "rb") as f:
            f.seek(spot[0])
            moov = f.read(spot[1])
        chain = _video_track_chain(moov, 0, len(moov), 8)
        if not chain:
            return ""
        e_i, e_head = chain[-1]
        e_size = struct.unpack(">I", moov[e_i:e_i + 4])[0]
        for i, size, kind, head in _atom_boxes(moov, e_i + e_head + 78, e_i + e_size):
            if kind == b"logs":
                return moov[i + head:i + size].decode("latin1", "replace")
    except Exception:
        pass
    return ""


# The atom holds a reverse domain name whose middle piece is the colour
# space; no digit anywhere says which of the two curves it is.
LOG_ATOM_NAMES = {"com.apple.rec2020.apple-log": "Apple Log (Rec.2020)",
                  "com.apple.apple-wide-gamut.apple-log":
                      "Apple Log 2 (Apple Wide Gamut)"}


def log_curve_from_atom(text):
    """Return the recording curve named by the logs atom.

    The name carries the colour space too: the same curve is recorded in
    two of them, and a table built for one lays the wrong space on the
    other. Known identifiers get a plain name, anything else is shown
    verbatim -- an unknown identifier is information, an invented name
    would not be.
    """
    raw = (text or "").replace("\x00", " ").strip()
    if not raw:
        return ""
    return LOG_ATOM_NAMES.get(raw.lower(), raw)


def check_colour_survived(source, target, extend=False):
    """Report whether the written file carries the intended colour tags.

    Compared against the intended values, not against the source: missing
    primaries are filled in from the matrix, so the box is meant to differ.
    """
    a, b = mov_colour_tags(source), mov_colour_tags(target)
    if a is None and b is None:
        return
    want = a
    if a and extend and a[0] == 2 and a[2] == MATRIX_BT2020:
        want = (PRIMARIES_BT2020,) + tuple(a[1:])
    if b == want and want != a:
        print(T('  Colour:          %d/%d/%d -- primaries filled in from '
                'the matrix (source: %d)') % (want[0], want[1], want[2], a[0]))
        return
    if a == b:
        print(T('  Colour:          %d/%d/%d carried over') % a[:3])
        return
    print(as_warn(T('  Colour:          Caution, %s in the source, %s in '
                    'the new file') % (a[:3] if a else T('nothing'), b[:3] if b else T('nothing'))))
    print(T('                   Resolve may then not recognise the input '
            'colour space.'))


def mov_colour_tags(file_path):
    """Read the colr box of a MOV file.

    Returns (primaries, transfer, matrix, full range) or None. ffprobe
    is not used: it reports names rather than numbers and names a wrong
    one for values it does not know, Apple Log among them. Only the atom
    tree is walked, so a huge recording is skipped over rather than read.
    """
    try:
        size = os.path.getsize(file_path)
        with open(file_path, "rb") as f:
            return _read_colr_atom(f, size)
    except (OSError, struct.error):
        return None


def video_summary(file_path, info):
    v = info["video"]
    tags = info.get("tags") or {}
    # The nominal rate comes first: editors use it. The measured one
    # beside it where it differs -- frame count over track duration, so a
    # property of the container.
    label_text, measured = info.get("nominal") or info["fps"], info["fps"]
    lines = [("Video", "%s, %sx%s, %s fps%s%s"
               % (v.get("codec_name", "?"), v.get("width"), v.get("height"),
                  decimal_text("%.3f" % label_text),
                  "" if abs(measured - label_text) < 0.0005
                  else T('  (container; measured %s)')
                  % decimal_text("%.4f" % measured),
                  "" if known_frame_rate(file_frame_rate(info))
                  else T('  --  no Resolve Timeline runs at this rate; '
                         'it is converted'))),
              (T('Length'), "%s  (%s)  --  %s"
               % (as_hms(info["duration"]), as_data_size(size_in_mb(file_path)),
                  "Timecode %s" % info["tc"] if info["tc"]
                  else T('no timecode'))),
              (T('Colour'), colour_text(file_path, v, tags)),
              (T('Camera'), camera_text(tags))]
    if info["audio"]:
        a = info["audio"][0]
        channels = channel_text(a.get("channels"))
        count = len(info["audio"])
        lines.append((T('Camera audio'),
                      TN(count, '%s track, %s, %s Hz, %s',
                         '%s tracks, %s, %s Hz, %s')
                      % (group_text(count), a.get("codec_name", "?"),
                         a.get("sample_rate", "?"), channels)))
    else:
        lines.append((T('Camera audio'), T('no audio track present')))
    return lines


def print_key_values(lines, indent="  "):
    # The column follows the longest label, so it holds in every language.
    width = max([len(k) for k, _ in lines] or [9]) + 1
    for k, value in lines:
        print("%s%-*s %s" % (indent, width, k + ":", value))


def print_audio_details(file_path, indent="  "):
    print_key_values(audio_summary(file_path), indent)


def print_video_details(file_path, info, indent="  "):
    print_key_values(video_summary(file_path, info), indent)


def open_in_file_manager(file_path):
    """Show a folder in Finder, Explorer or the desktop file manager."""
    folder = file_path if os.path.isdir(file_path) else os.path.dirname(file_path)
    try:
        if sys.platform == "darwin":
            if os.path.isdir(file_path):
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["open", "-R", file_path])
        elif os.name == "nt":
            if os.path.isdir(file_path):
                os.startfile(folder)
            else:
                # The switch and the path have to be one single argument,
                # otherwise Explorer opens the documents folder.
                subprocess.Popen('explorer /select,"%s"'
                                 % os.path.normpath(file_path))
        else:
            subprocess.Popen(["xdg-open", folder])
        return True
    except Exception:
        return False


def report_timecode_check(audio_start, info, measured, indent="  "):
    """Compare what the timecode says with what can be heard."""
    if audio_start is None or not info["tc"]:
        return
    fps = max(1.0, info["fps"])
    loud_tc = unwrap_day(parse_timecode(info["tc"], fps),
                         audio_start) - audio_start
    deviation = measured - loud_tc
    print(T('%sTimecode check of the audio file') % indent)
    if not GUI_RUNNING:
        print(T('%s  Audio starts per timecode at    %s')
              % (indent, timecode_string(audio_start, fps)))
        print(T('%s  Picture starts per timecode at  %s')
              % (indent, timecode_string(parse_timecode(info["tc"], fps), fps)))
    print(T('%s  Offset per timecode:            %s') % (indent, as_hms(loud_tc)))
    print(T('%s  Offset measured:                %s') % (indent, as_hms(measured)))
    if abs(deviation) > 60:
        print(T('%s  Deviation:                      %s') % (indent, as_hms(deviation)))
        print(T('%s  The audio timecode does not fit the picture at all -- '
                'probably a clock never set. The measurement is used.')
              % indent)
    elif abs(deviation) > 0.5 / fps:
        print(T('%s  Deviation:                      %s  (%s frames)')
              % (indent, as_hms(deviation),
                 decimal_text("%.1f" % (abs(deviation) * fps))))
        print(T('%s  The timecode does not fit what is heard. The '
                'measurement is used.') % indent)
    else:
        print(T('%s  Deviation:                      %s  (%s frames) -- fits')
              % (indent, as_hms(deviation),
                 decimal_text("%.1f" % (abs(deviation) * fps))))


#---------------------------------------------------------- Collecting files

# What a run works out from the files it was given -- the time axis,
# the offsets, the names, the picture levels, the colours and the
# sliders -- stands in a piece of its own, in the folder "bearings"
# beside this one, and is read far below, where the pieces are read.

# Three functions stay here with the constants they use, each for one
# measured reason: a piece read before the bearings binds it at its
# head, and a head binding reaches into this file only. The material
# binds safe_filename and gcc_phat_offset, what is said the third.


def safe_filename(name):
    return re.sub(r"[^A-Za-z0-9_.+-]", "_", name) or "track"


PHAT_BAND = (300.0, 3500.0)


def gcc_phat_offset(x, y, rate, max_ms=120.0):
    """Return by how many milliseconds y arrives later than x.

    GCC-PHAT: the cross spectrum is normalised to magnitude one across the
    speech band so only the phase counts. Against reverberation and against
    different microphones that is far more robust than a plain cross
    correlation, and it measures to a fraction of a sample rather than to an
    envelope grid. Returns (milliseconds, sharpness of the peak).
    """
    n = 1 << int(np.ceil(np.log2(len(x) + len(y))))
    X, Y = np.fft.rfft(x, n), np.fft.rfft(y, n)
    R = np.conj(X) * Y
    f = np.fft.rfftfreq(n, 1.0 / rate)
    band = (f >= PHAT_BAND[0]) & (f <= PHAT_BAND[1])
    W = np.zeros_like(R)
    W[band] = R[band] / np.maximum(np.abs(R[band]), 1e-12)
    r = np.fft.irfft(W, n)
    size = int(max_ms / 1000.0 * rate)
    corr_window = np.concatenate([r[-size:], r[:size + 1]])
    k = int(np.argmax(corr_window))
    peak = float(corr_window[k])
    if 0 < k < len(corr_window) - 1:
        a, b, c = corr_window[k - 1], corr_window[k], corr_window[k + 1]
        denominator = a - 2 * b + c
        fine = 0.5 * (a - c) / denominator if abs(denominator) > 1e-12 else 0.0
    else:
        fine = 0.0
    return ((k - size + fine) / rate * 1000.0,
            peak / (float(np.std(corr_window)) + 1e-12))


# How much is read at a time when marking a file by its content. A
# larger block buys nothing: the hashing sets the pace, not the disk.
CONTENT_BLOCK = 1 << 20


def file_content_mark(file_path):
    """Return what a file holds, as one string over size and content.

    For a file whose name says nothing: a mix is written into a fresh
    folder on every run, so path and time can never meet themselves,
    and a modification time cannot tell two writes inside one second
    apart either. Costs about a third of a second per gigabyte, read
    or cached. "" where the file cannot be read.
    """
    mark = hashlib.sha1()
    try:
        with open(file_path, "rb") as f:
            mark.update(b"%d\n" % os.fstat(f.fileno()).st_size)
            for block in iter(lambda: f.read(CONTENT_BLOCK), b""):
                mark.update(block)
    except OSError:
        return ""
    return mark.hexdigest()


#---------------------------------------------------------------- Video data

def video_facts(path, fps_default=None, tc_default_value=None):
    d = ffprobe_json(path)
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), None)
    if v is None:
        raise RuntimeError(T('no video track in %s') % os.path.basename(path))
    a = [s for s in d.get("streams", []) if s.get("codec_type") == "audio"]
    fps = fps_default
    if not fps:
        r = v.get("avg_frame_rate") or v.get("r_frame_rate") or "30/1"
        try:
            num, the_one = (int(x) for x in r.split("/"))
            fps = num / the_one if the_one else 30.0
        except Exception:
            fps = 30.0
    tc = tc_default_value
    if tc is None:
        # The tracks before the file, for the reason in file_timecode:
        # the track is the camera's clock, the file level is ffmpeg's
        # reading of it, and the camera wins where they disagree.
        for source in [s.get("tags", {}) or {} for s in d.get("streams", [])] +\
                      [d.get("format", {}).get("tags", {})]:
            if source.get("timecode"):
                tc = source["timecode"]
                break
    dur = float(d.get("format", {}).get("duration") or v.get("duration") or 0.0)
    label_text = 0.0
    try:
        num, the_one = (float(x) for x in str(v.get("r_frame_rate")
                                          or "0/0").split("/"))
        label_text = num / the_one if the_one else 0.0
    except Exception:
        label_text = 0.0
    return {"fps": fps, "tc": tc, "duration": dur, "audio": a, "video": v,
            "width": v.get("width"), "height": v.get("height"),
            "nominal": label_text or fps,
            "tags": (d.get("format") or {}).get("tags") or {}}


#---------------------------------------------------------- Audio analysis

def audio_track_starts_at(path, stream=None):
    """When the first sample of this audio track is to be heard, in seconds.

    A camera track can begin after the picture, and an AAC stream
    begins with samples the file marks as not to be played; both go
    into this number, and both were being thrown away. Measured
    2.9.2026 over three cameras of one shoot: 60,375 ms at one of them
    and none at the other two -- so it is read, never assumed.
    """
    # And what no file declares cannot be put right from here: a stream
    # whose lead-in is nowhere written down comes back that much too
    # late, and nothing in it says by how much.
    try:
        rows = [s for s in (ffprobe_json(path).get("streams") or [])
                if s.get("codec_type") == "audio"]
        row = rows[stream or 0] if rows else {}
        return float(row.get("start_time") or 0.0)
    except (IndexError, TypeError, ValueError):
        return 0.0


def audio_on_the_picture(x, path, rate, stream=None):
    """Put decoded samples where the file says they are to be heard.

    Silence in front where the track starts after the picture, and the
    head cut away where it starts before it. Only for a decode from the
    front: with -ss ffmpeg counts from the presentation time itself and
    the samples already lie right.
    """
    head = int(round(audio_track_starts_at(path, stream) * rate))
    if head > 0:
        return np.concatenate([np.zeros(head, dtype=x.dtype), x])
    if head < 0:
        return x[-head:]
    return x


def decode_audio(path, rate=SR, ss=None, duration=None, stream=None,
                 dtype=None):
    """Decode one channel of a file into samples.

    ffmpeg writes float32 and the default widens it to float64.
    Whoever hands the samples on in float32 asks for float32 here and
    saves a copy at twice the size, which over a whole episode is the
    largest block the program holds. None is that default: numpy is
    fetched at the end of this file and cannot stand in a signature.
    """
    cmd = ["ffmpeg", "-v", "error"]
    if ss is not None:
        cmd += ["-ss", "%.6f" % ss]
    if duration is not None:
        cmd += ["-t", "%.6f" % duration]
    cmd += ["-i", path]
    if stream is not None:
        cmd += ["-map", "0:a:%d" % stream]
    cmd += ["-ac", "1", "-ar", str(rate), "-f", "f32le", "-"]
    p = subprocess.run(cmd, capture_output=True)
    x = np.frombuffer(p.stdout, dtype=np.float32).astype(
        dtype or np.float64)
    # What comes back begins where the file says the track begins, not
    # where ffmpeg's first sample happens to fall. With -ss it already
    # does: there ffmpeg counts from the presentation time itself.
    return x if ss is not None else audio_on_the_picture(x, path, rate,
                                                         stream)


_ENV = {}


def show_progress(text, share=None):
    # Where this thread runs inside a parallel batch, its progress goes into
    # the shared bar rather than onto a line of its own -- three bars above
    # each other would be unreadable.
    own_flag = THREAD_SHARE.get(threading.get_ident())
    if own_flag is not None:
        own_flag.report(0.0 if share is None else share, text)
        return
    step_report(share)
    draw_progress_bar(text, share)


def progress_from_line(line, duration):
    """Extract the progress fraction from a line of "ffmpeg -progress".

    Returns a number between 0 and 0.999, or None if the line says nothing
    about progress. Four places read this output and should read it the same
    way.
    """
    if isinstance(line, bytes):
        line = line.decode("utf-8", "replace")
    line = line.strip()
    if not line.startswith("out_time_ms=") or not duration or duration <= 0:
        return None
    try:
        return min(0.999, int(line.split("=")[1]) / 1e6 / float(duration))
    except ValueError:
        return None


def draw_progress_bar(text, share=None):
    """Write one progress line, directly."""
    if share is None:
        line = "\r  %s" % text
    else:
        line = "\r  %s [%-30s] %3.0f %%" % (text, "#" * int(share * 30),
                                             share * 100)
    if OUTPUT_SINK:
        OUTPUT_SINK(line)
    else:
        sys.stdout.write(line + " " * 6)
        sys.stdout.flush()


class SharedProgressBar(object):
    """One progress bar for everything running at once.

    Every file reports its own share and the average is displayed. Because
    each share can only rise, the bar never jumps back.
    """

    def __init__(self, text, how_many):
        self.text, self.how_many = text, max(1, how_many)
        self.status, self.lock = {}, threading.Lock()
        self.last_time = -1.0
        self.stream = None      # the real output, past the buffer

    def show(self, share):
        line = "\r  %s [%-30s] %3.0f %%" % (
            T('%s (%s files)') % (self.text, group_text(self.how_many)),
            "#" * int(share * 30), share * 100)
        if OUTPUT_SINK:
            OUTPUT_SINK(line)
            return
        # Past the buffer: the bar belongs on the real output, otherwise it
        # only appears once the file is finished.
        stream = self.stream or sys.stdout
        try:
            stream.write(line + " " * 6)
            stream.flush()
        except Exception:
            pass

    def report(self, who, share):
        with self.lock:
            self.status[who] = share
            total = sum(self.status.values()) / float(self.how_many)
            # At most 99 % while the run is not through. The last file reports
            # itself done before its report leaves the buffer, and a bar at 100
            # % with something still arriving below looks like a hang.
            total = min(0.99, total)
            if abs(total - self.last_time) < 0.005:
                return          # nothing new, so no second line
            self.last_time = total
        # The bar in the footer wants the joint figure, not each file's:
        # several threads reporting one at a time would make it jump to
        # whichever file happens to be furthest along.
        step_report(total)
        self.show(total)

    def stop(self):
        self.show(1.0)
        write_through("\n")


class Share(object):
    """The progress of one file, assembled from sections.

    The sections are roughly weighted: measure, write, verify. Within a
    section the ffmpeg progress is passed through. It never goes back.
    """

    def __init__(self, progress_bar, who):
        self.progress_bar, self.who = progress_bar, who
        self.begins, self.until, self.highest = 0.0, 1.0, 0.0
        self.done = set()

    def segment(self, begins, until):
        self.begins, self.until = begins, until
        self.report(0.0)

    def report(self, share, text=None):
        # The bar itself runs jointly; every step still enters this file's
        # report as soon as it is through. Otherwise the lines one knows from a
        # sequential run would be missing there.
        if text and share >= 0.999 and text not in self.done:
            self.done.add(text)
            write_through("  %s [%s] 100 %%\n" % (text, "#" * 30))
        value = self.begins + (self.until - self.begins) * max(0.0, min(1.0, share))
        if value > self.highest:
            self.highest = value
        self.progress_bar.report(self.who, self.highest)


# The run says which stage it is in, and how far that stage is. The
# interface draws one bar out of it; on the command line nothing is
# connected and the calls cost a comparison.
PROGRESS_SINK = None
_STEP = {"name": ""}


def step_begin(name):
    """Say that the run has reached a stage. Ends the one before it."""
    _STEP["name"] = name
    if PROGRESS_SINK:
        try:
            PROGRESS_SINK(name, None)
        except Exception:
            pass


def step_report(share):
    """Say how far the current stage is, 0 to 1."""
    if PROGRESS_SINK and _STEP["name"] and share is not None:
        try:
            PROGRESS_SINK(_STEP["name"], float(share))
        except Exception:
            pass


def run_stages(multitrack, cameras, auphonic, speakers=None):
    """The stages of a run and what share of the bar each is worth.

    The weights are proportions measured on real jobs, not guesses at a
    clock: writing the camera files reads and re-encodes every camera in
    full and takes longer than everything before it together, so it gets
    most of the bar. Pulling the audio out of the cameras is the other
    long one. A stage that will not happen is not in the list.
    """
    cameras = max(0, int(cameras))
    out = [("plan", 1.0, T('Reading the plan'))]
    # Only the multitrack path pulls the audio out of the cameras; the
    # simple path aligns against them and leaves them alone. Listed for
    # both, the bar held a fifth of itself for a stage that never
    # reported, and then jumped that fifth in one go when the next one
    # began.
    if cameras and multitrack:
        out.append(("camera audio", 5.0 * cameras,
                    T('Audio out of the cameras')))
    out.append(("time base", 4.0, T('Common time axis')))
    if auphonic:
        out.append(("auphonic", 8.0, T('Processing at auphonic.com')))
    else:
        out.append(("loudness", 4.0, T('Loudness and levels')))
    if multitrack if speakers is None else speakers:
        out.append(("speakers", 3.0, T('Who speaks when')))
    if cameras:
        out.append(("cameras", 12.0 * cameras,
                    T('Writing the camera files')))
    out.append(("result", 1.0, T('Handover and result')))
    return out


class ProgressPlan(object):
    """One bar for a job whose steps take very different lengths.

    Each step carries a weight, and the bar is the weighted sum of what
    the steps report. Three things make it readable rather than merely
    correct:

    It never goes back. A step added while the job runs lowers the
    arithmetic, and a bar jumping backwards reads as a fault even though
    nothing was lost.

    A step that cannot say how far it is creeps towards its own end
    instead of standing still. The creep slows as it approaches and
    never reaches the boundary, so the bar keeps moving without ever
    claiming a step is further along than it is.

    Long steps get room in proportion to how long they take. Pulling the
    audio out of an hour of 4K and reading a wav file are one step each,
    and giving them the same share of the bar would make it useless.
    """

    def __init__(self):
        self.order = []
        self.weight = {}
        self.share = {}
        self.real = {}
        self.caption = {}
        self.began = set()
        self.highest = 0.0

    def clear(self):
        self.__init__()

    def add(self, name, weight=1.0, caption=""):
        """Announce a step. Announcing it twice changes nothing."""
        if name not in self.weight:
            self.order.append(name)
            self.weight[name] = max(0.01, float(weight))
            self.share[name] = 0.0
        if caption:
            self.caption[name] = caption

    def begin(self, name, caption="", weight=1.0):
        """Mark a step as under way without claiming a figure for it.

        For work that reports nothing at all until it is finished. Such
        a step may creep the whole way to its ceiling; one that does
        report stays close to what it reported.
        """
        self.add(name, weight, caption)
        self.began.add(name)

    def report(self, name, share, caption=""):
        """Say how far one step is. Unknown steps count as weight 1."""
        self.begin(name, caption)
        value = max(0.0, min(1.0, float(share)))
        self.real[name] = max(self.real.get(name, 0.0), value)
        self.share[name] = max(self.share[name], value)

    def done(self, name):
        self.report(name, 1.0)

    def drop(self, names):
        """Forget steps whose work was called off.

        A step left standing half way is neither finished nor being
        worked on, and it holds the bar up for ever. Marking it done
        instead would put the bar at the end of work nobody did.
        """
        for name in list(names):
            if name not in self.weight:
                continue
            self.order.remove(name)
            del self.weight[name]
            del self.share[name]
            self.real.pop(name, None)
            self.caption.pop(name, None)
            self.began.discard(name)
        if not self.order:
            self.highest = 0.0

    def creep(self, seconds, reach=0.93, half_life=30.0, lead=0.12,
              beyond=0.99, slower=10.0):
        """Let the running steps drift on, but not into a lie.

        Asymptotic: half the remaining distance every half_life. A step
        that has reported a figure may only creep a little past it --
        otherwise the bar would sit near the end of a step that is a
        tenth of the way through. A step that reports nothing at all has
        nothing to be held to and may creep the whole way.

        Past the ceiling it goes on at a tenth of the speed, up to
        *beyond*. Something that runs far longer than expected should
        still show life; at a tenth of the pace that reads as "nearly
        there, still working" rather than as a promise.
        """
        if seconds <= 0 or half_life <= 0:
            return
        part = 1.0 - 0.5 ** (float(seconds) / float(half_life))
        crawl = 1.0 - 0.5 ** (float(seconds) / (float(half_life) * slower))
        for name in self.began:
            here = self.share[name]
            top = (reach if name not in self.real
                   else min(reach, self.real[name] + lead))
            # A hair short of the ceiling counts as at it. The approach
            # is asymptotic and would otherwise never cross, so the slow
            # stretch past it could never be reached at all.
            if here < top - 0.001:
                self.share[name] = here + (top - here) * part
            elif top >= reach and here < beyond:
                here = max(here, top)
                self.share[name] = here + (beyond - here) * crawl

    def total(self):
        """The whole job as one number, 0 to 1, and never falling."""
        weight = sum(self.weight.values())
        if not weight:
            return self.highest
        now = sum(self.weight[n] * self.share[n] for n in self.order) / weight
        self.highest = max(self.highest, now)
        return self.highest

    def busy(self):
        """Report whether anything is still outstanding."""
        return any(self.share[n] < 0.999 for n in self.order)

    def running(self):
        """The steps under way, in the order they were announced."""
        return [n for n in self.order
                if n in self.began and self.share[n] < 0.999]

    def line(self):
        """One line for beside the bar: what is being worked on."""
        busy = self.running()
        if not busy:
            return ""
        first = self.caption.get(busy[0]) or busy[0]
        if len(busy) == 1:
            return first
        return T('%s and %s more') % (first, group_text(len(busy) - 1))


def write_through(text):
    """Print text; buffer it first when running in a parallel thread."""
    p = THREAD_BUFFER.get(threading.get_ident())
    if p is not None:
        p.append(text)
        return
    if OUTPUT_SINK:
        OUTPUT_SINK(text)
    else:
        sys.stdout.write(text)
        sys.stdout.flush()


class ThreadOutput(object):
    """Stand-in for sys.stdout while several threads are writing."""

    def __init__(self, real):
        self.real = real

    def write(self, text):
        p = THREAD_BUFFER.get(threading.get_ident())
        if p is not None:
            p.append(text)
            return len(text)
        return self.real.write(text)

    def flush(self):
        try:
            self.real.flush()
        except Exception:
            pass


def decode_audio_long(path, rate, duration, text, stream=None, report=None):
    """Decode audio with progress reporting.

    Reading a 30 GB file once takes minutes, and a blinking cursor is not
    enough feedback for that.
    """
    return decode_audio_tracks(path, rate, duration, text, [stream],
                               report)[0]


def decode_audio_tracks(path, rate, duration, text, streams, report=None):
    """Decode several tracks of one file in one pass over the container.

    Asking track by track reads a 36 GB camera file once per track, and
    off a drive that pass is the whole of the waiting; one ffmpeg with a
    -map per track reads it once. One process has one progress stream,
    so the text has to name every track that pass is fetching.
    """
    cmd = ["ffmpeg", "-v", "error", "-nostats", "-progress", "pipe:1",
           "-i", path]
    raws = []
    for stream in streams:
        fd, raw = tempfile.mkstemp(suffix=".raw")
        os.close(fd)
        raws.append(raw)
        if stream is not None:
            cmd += ["-map", "0:a:%d" % stream]
        cmd += ["-ac", "1", "-ar", str(rate), "-f", "f32le", "-y", raw]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL)
        points = 0
        for line in proc.stdout:
            share = progress_from_line(line, duration)
            if share is not None:
                if report:
                    report(share)
                else:
                    show_progress(text, share)
                continue
            note = line.decode("utf-8", "replace").strip()
            if note.startswith("out_time_ms=") or note.startswith("frame="):
                points = (points + 1) % 20
                if not report:
                    show_progress(note + " " + "." * (points // 4 + 1))
        proc.wait()
        if report:
            report(1.0)
        else:
            show_progress(text, 1.0)
            if THREAD_SHARE.get(threading.get_ident()) is None:
                if OUTPUT_SINK:
                    OUTPUT_SINK("\n")
                else:
                    sys.stdout.write("\n")
        # Each track on the time of its own start, the same as the
        # short way above: a big file must not be placed differently
        # from a small one only because it came through here.
        return [audio_on_the_picture(
                    np.fromfile(raw, dtype=np.float32).astype(np.float64),
                    path, rate, stream)
                for raw, stream in zip(raws, streams)]
    finally:
        for raw in raws:
            remove_quietly(raw)




def running_from():
    """Which copy of the script this is.

    Not sys.argv[0]: the restart after an update and the call out of
    DaVinci Resolve both set it to something else. __file__ is the file
    that was really loaded.
    """
    try:
        return os.path.abspath(__file__)
    except Exception:
        return "?"





# The mark the window's own lines carry, so they can be picked out of a
# log that also holds what ffmpeg and Qt write: grep for it.
GUI_MARK = "[GUI]"


# What a speaker reading leaves behind in the state. Cleared together,
# or a reading of one project is read back in the next.
SPEAKER_STATE = ("measure_failed", "speakers_measured", "speakers_measuring")


def speakers_still_wanted(state):
    """Whether the speakers still have to be worked out.

    Not while one run is under way and not after one failed -- it would
    fail the same way and cost the same minutes. And not where a
    finished run already knows them: measuring again would relabel its
    preview as measured from the raw recordings.
    """
    return not (state.get("speakers_measured")
                or state.get("speakers_measuring")
                or state.get("measure_failed")
                or state.get("cut_basis") in ("run", "auphonic"))


# How close a player has to be to a jump before it counts as arrived.
# One second: a seek lands on the key frame before the mark, and with
# long GOPs on 4K material that is most of a second away.
SPOT_ARRIVED_MS = 1000

# Waiting for a jump to land, as the cut player's Seeker does -- which
# is why that one switches cameras cleanly. Measured on 18 and 27 GB
# files: a file falls back to its front 18 to 88 ms after reporting
# itself loaded. A seek is a request, not a command.
SEEK_HIT_MS = 350
SEEK_AGAIN_MS = 120
SEEK_PATIENCE_S = 5.0
SEEK_SETTLE_S = 0.5


def gui_log(text):
    """Write down what the window just did.

    A window tells nobody afterwards what it was showing, where it
    stood, or which of the two reckonings a position came out of. The
    log is what somebody can send along with a complaint. It lands in
    the file: redirect_console has the descriptors by then.
    """
    print("%s %s  %s" % (GUI_MARK, time.strftime("%H:%M:%S"), text))




def outside_what(cmd):
    """The tool and the file one call to another program is about."""
    parts = [str(x) for x in ([cmd] if isinstance(cmd, str) else (cmd or []))]
    if not parts:
        return "", ""
    tool = os.path.basename(parts[0])
    # A python of its own runs the speaker separation, and "python3"
    # says nothing about what is taking the minutes. The script it is
    # given is the name worth printing.
    if tool.startswith("python") and len(parts) > 1:
        tool = os.path.basename(parts[1]).replace(".py", "") or tool
    for i, one in enumerate(parts):
        if one == "-i" and i + 1 < len(parts):
            return tool, os.path.basename(parts[i + 1])
    # ffprobe takes its file last and without a switch in front of it.
    tail = parts[-1]
    return tool, os.path.basename(tail) if not tail.startswith("-") else ""












# Otherwise the last run of identical calls is never written: nothing
# different comes after it to push it out.
atexit.register(outside_flush)


def outside_log(cmd, seconds=None):
    """Write down one call to a program outside this one.

    Every call is here because subprocess is wrapped once below, so a
    new call site cannot forget to say so.
    """
    tool, about = outside_what(cmd)
    if tool:
        outside_say(tool, about, seconds)


@contextlib.contextmanager
def outside_work(tool, about):
    """Time work that runs in this process but costs like an outside call.

    The models are not subprocesses, so the wrapper below does not see
    them -- and they are the longest thing a run does. Said even where
    it fails: work that broke off after four minutes still took them.
    """
    began = time.monotonic()
    try:
        yield
    finally:
        outside_say(tool, about, time.monotonic() - began)


_subprocess_run, _subprocess_popen = subprocess.run, subprocess.Popen


# run() opens a Popen of its own, so without this every call it makes
# would be said twice. Per thread: the window runs its prework in
# several at once, and one counter for all of them would silence the
# wrong lines.
_in_run = threading.local()


def run_outside(cmd, *rest, **named):
    """subprocess.run, with the call and how long it took written down."""
    began = time.monotonic()
    _in_run.here = getattr(_in_run, "here", 0) + 1
    try:
        return _subprocess_run(cmd, *rest, **named)
    finally:
        _in_run.here -= 1
        outside_log(cmd, time.monotonic() - began)


class SaysWhenDone(_subprocess_popen):
    """A Popen that says how long it ran when somebody waits for it.

    Started and finished are two lines because a long call is
    interesting while it runs -- and without the second one a process
    that took four minutes cannot be told from one that took four
    seconds.
    """

    def __init__(self, cmd, *rest, **named):
        self._began = time.monotonic()
        self._said = False
        self._cmd = cmd
        _subprocess_popen.__init__(self, cmd, *rest, **named)

    def _say_done(self):
        if not self._said:
            self._said = True
            outside_log(self._cmd, time.monotonic() - self._began)

    def wait(self, *rest, **named):
        try:
            return _subprocess_popen.wait(self, *rest, **named)
        finally:
            self._say_done()

    def communicate(self, *rest, **named):
        try:
            return _subprocess_popen.communicate(self, *rest, **named)
        finally:
            self._say_done()


def popen_outside(cmd, *rest, **named):
    """subprocess.Popen, saying both when it started and when it ended."""
    if getattr(_in_run, "here", 0):
        return _subprocess_popen(cmd, *rest, **named)
    outside_log(cmd)
    return SaysWhenDone(cmd, *rest, **named)


def watch_outside_calls():
    """Route every call to another program past the log.

    Wrapped here rather than at the 46 call sites: what is asked of a
    call site is forgotten by the next one somebody writes. Called from
    main(), where somebody has asked for a run -- done while the file
    is read, the replacement would reach into whoever imported it, and
    their processes have nothing to do with a run.
    """
    subprocess.run = run_outside
    subprocess.Popen = popen_outside


def trouble_log(text):
    """Write down what the window is showing in red.

    A red mark in the window is gone the moment the row is drawn
    again, and the complaint about it arrives hours later. In the log
    it keeps, with the time beside it.
    """
    said = " ".join(str(text or "").split())
    if said:
        log_aside("%s %s  %s"
                  % (BAD_MARK, time.strftime("%H:%M:%S"), said[:200]))


def redirect_console():
    """Redirect everything that would go to the terminal into a file.

    Not only our own messages: the file descriptors themselves are
    redirected so that what Qt and ffmpeg write underneath Python comes
    along. One backup of the previous run is kept.
    """
    file_path = log_path()
    if not file_path:
        return None
    # The aside handle may already stand open on the file about to be
    # renamed -- the tool check runs a process before this, and every
    # outside call is written down. Left alone, the whole run's aside
    # lines would land in the previous run's log. Measured 4.9.2026.
    while _LOG_ASIDE:
        kept = _LOG_ASIDE.pop()
        try:
            if kept is not None:
                kept.close()
        except Exception:
            kept = None
    # The backup is called ..._1.log rather than ....log.1 --
    # otherwise Finder does not know the extension and will not open it.
    before_value = os.path.splitext(file_path)[0] + "_1.log"
    try:
        old = file_path + ".1"
        if os.path.exists(old):
            os.unlink(old)          # from older versions
    except OSError:
        pass
    try:
        if os.path.exists(file_path):
            os.replace(file_path, before_value)
        file = open(file_path, "w", buffering=1, encoding="utf-8",
                     errors="replace")
        # Header: version, time, machine -- and which copy of the
        # script this was. Several runnable copies of the same version
        # are the normal case here: the snapshot the test suite runs
        # against, the one pip installed, a checkout somebody started
        # by its path. They share one log file, and without the path
        # nobody can tell later why one run came out different from
        # another.
        file.write("Video Podcast Magic %s   %s   %s %s   %s\n%s\n\n"
                    % (VERSION,
                       time.strftime("%Y-%m-%d %H:%M:%S"),
                       platform.system(), platform.release(),
                       python_note(), running_from()))
        os.dup2(file.fileno(), 1)
        os.dup2(file.fileno(), 2)
        # The aside lines go through this same handle from now on: two
        # handles on one file keep two write positions, and whichever
        # is behind writes over what the other put there. Measured
        # 5.9.2026 -- a line came out as "rogram list is settled".
        _LOG_ASIDE.append(file)
    except Exception:
        return None
    return file_path


def envelope_cache_folder():
    """Return the folder the computed envelopes may live in."""
    return cache_folder("envelopes")
















def clean_envelope_cache(days=30):
    """Discard stale envelopes; once per run is enough."""
    clean_old_files(envelope_cache_folder(), days)




_RECIPE_MARKS = {}


def recipe_mark(name, *work):
    """A short mark of the way something is worked out.

    A number counted by hand would have to be remembered, and the day
    somebody forgets it the store hands back a measurement another
    recipe wrote. So the source of the functions that decide the
    numbers is read and hashed: it cannot change without changing
    this.
    """
    if name not in _RECIPE_MARKS:
        try:
            import inspect
            text = "".join(inspect.getsource(f) for f in work)
        except Exception:
            # Nothing to read the source from. The version is coarse --
            # every release throws the store away -- but it never hands
            # back what some other recipe wrote.
            text = VERSION
        _RECIPE_MARKS[name] = hashlib.sha1(
            text.encode("utf-8")).hexdigest()[:12]
    return _RECIPE_MARKS[name]


def envelope_recipe_mark():
    """The mark for a curve: what ffmpeg is asked for, and the rest."""
    return recipe_mark("envelope", decode_audio, decode_audio_tracks,
                       envelope, audio_track_starts_at,
                       audio_on_the_picture)


def envelope_cache_path(path, hop_ms, rate):
    """Return a cache name that changes as soon as the file changes.

    Or as soon as the way the curve is worked out changes: without that
    mark a changed recipe reads the old curves back and the run
    compares two of them that were never measured the same way.
    """
    folder = envelope_cache_folder()
    if not folder:
        return None
    try:
        st = os.stat(path)
    except OSError:
        return None
    import hashlib
    fingerprint = "%s|%d|%d|%.3f|%d|%s" % (path_key(path), int(st.st_mtime),
                                    st.st_size, hop_ms, rate,
                                    envelope_recipe_mark())
    return os.path.join(folder,
                        hashlib.sha1(fingerprint.encode("utf-8")).hexdigest()
                        + ".npy")


def envelope_log(path, hop_ms, rate, what):
    """Say whether a curve came out of the store or off the disc.

    A curve costs minutes on a large file and nothing when it is
    found. Which of the two happened is invisible from outside, and
    the numbers are in the line because a curve is kept under them:
    the same file at another hop or rate is another curve.
    """
    log_aside("%s %s  %-30s %g/%d  %s"
              % (ENV_MARK, time.strftime("%H:%M:%S"),
                 os.path.basename(path)[:30], hop_ms, rate, what))


def video_envelope(path, hop_ms=5.0, rate=4000, report=None):
    """Return the envelope of the video audio track, computed once per file.

    The cache survives the whole run. The interface warms it while the user
    is still typing, so by the time the run starts the curve is there.
    Kept under path_key: the prework warms it under the absolute path
    and the time axis asks under the name the file dialog gave, and
    where those differ the file was read twice. It is opened by the
    path as it came in."""
    api_key = (path_key(path), hop_ms, rate)
    if api_key not in _ENV:
        # Reading an hour of 4K takes minutes; twice is unnecessary.
        cache = envelope_cache_path(path, hop_ms, rate)
        if cache and os.path.exists(cache):
            try:
                _ENV[api_key] = np.load(cache)
                envelope_log(path, hop_ms, rate, "read back from the store")
                return _ENV[api_key]
            except Exception as trouble:
                envelope_log(path, hop_ms, rate,
                             "the stored curve would not read: %s" % trouble)
        else:
            envelope_log(path, hop_ms, rate,
                         "nothing in the store, reading the file"
                         if cache else "no store to look in")
        duration = 0.0
        try:
            duration = float(ffprobe_json(path).get("format", {}).get("duration") or 0)
        except Exception:
            pass
        large = os.path.getsize(path) > 200e6 if os.path.exists(path) else False
        if large or report:
            x = decode_audio_long(path, rate, duration,
                                T('Reading audio track from %s') % os.path.basename(path),
                                report=report)
        else:
            x = decode_audio(path, rate=rate)
        _ENV[api_key] = envelope(x, hop_ms, rate)
        if len(_ENV[api_key]) < 10:
            # ffmpeg delivered nothing. Caching that would mean treating the
            # file as unalignable until it next changes, without ever saying
            # why.
            _ENV.pop(api_key, None)
            raise ValueError(T('no audio data from %s')
                             % os.path.basename(path))
        if cache:
            # Beside it and then moved: two files being measured at
            # once, or a run broken off, must not leave half a curve
            # behind for the next start to read as a measurement.
            try:
                # The suffix has to be .npy: np.save appends one
                # otherwise, and the move would then miss the file.
                fd, beside = tempfile.mkstemp(dir=os.path.dirname(cache),
                                              prefix=".vpm_", suffix=".npy")
                os.close(fd)
                np.save(beside, _ENV[api_key].astype("float32"))
                os.replace(beside, cache)
            except Exception:
                pass
    return _ENV[api_key]


def envelope(x, hop_ms=5.0, rate=SR):
    h = max(1, int(hop_ms * rate / 1000.0))
    m = len(x) // h
    if m < 2:
        return np.zeros(0)
    e = np.sqrt((x[:m * h].reshape(-1, h) ** 2).mean(1))
    e = np.log(e + 1e-9)
    return e - e.mean()


# Narrow where mains hum sits, wider above it. Everything over the last
# edge is counted into the last band: at 4000 Hz that is a single bin.
BAND_EDGES = (0, 50, 75, 100, 125, 150, 200, 250, 300, 400, 500, 650,
              800, 1000, 1200, 1400, 1600, 1800, 2000)
# How long a stretch one band level is read over. 64 ms is long enough
# to tell 50 Hz from 100 Hz; the 5 ms box the plain curve uses is not,
# and there a hum and the voice over it land in the same value.
BAND_WINDOW_S = 0.064
# A band counts if its own loudness moves at least half as much as the
# liveliest band of that recording. Measured 1.9.2026 over 38 tracks
# from four productions: the mains hum drops out of every one of them,
# and none of the 85 pairs that belong together got worse.
BAND_MOVES_ENOUGH = 0.5


def band_powers(x, hop_ms=5.0, rate=SR):
    """How much power each band holds at every step of the curve.

    One short spectrum every hop, its bins summed inside the band
    edges. Worked through in blocks: a whole episode at once is a
    matrix of some gigabytes, and the answer is the same either way.
    """
    hop = max(1, int(hop_ms * rate / 1000.0))
    win = max(16, 1 << int(round(np.log2(BAND_WINDOW_S * rate))))
    steps = (len(x) - win) // hop
    bands = len(BAND_EDGES) - 1
    if steps < 10:
        return np.zeros((bands, 0), dtype=np.float32)
    which = np.clip(np.searchsorted(np.asarray(BAND_EDGES, float),
                                    np.fft.rfftfreq(win, 1.0 / rate),
                                    side="right") - 1, 0, bands - 1)
    shape = np.hanning(win)
    out = np.empty((bands, steps), dtype=np.float32)
    block = 40000
    for s in range(0, steps, block):
        k = min(block, steps - s)
        at = np.arange(win)[None, :] + hop * np.arange(s, s + k)[:, None]
        power = np.abs(np.fft.rfft(x[at] * shape, axis=1)) ** 2
        for b in range(bands):
            here = which == b
            out[b, s:s + k] = power[:, here].sum(1) if here.any() else 0.0
    return out


def moving_bands(power):
    """Which bands say something about the time, and which stand still.

    A band whose level never changes cannot place anything, however
    loud it is: mains hum sits there at full strength and says the
    same thing from the first second to the last. Asked of the
    recording itself, so no frequency has to be set from outside.
    """
    if not power.size:
        return np.zeros(len(power), dtype=bool)
    move = np.array([float(np.log(np.sqrt(np.asarray(p, float)) + 1e-9).std())
                     for p in power])
    return move >= BAND_MOVES_ENOUGH * (float(move.max()) or 1.0)


def band_envelope(x, hop_ms=5.0, rate=SR):
    """The loudness curve without the bands that carry no movement.

    What envelope() reads in one piece, read band by band with the
    still ones left out. Where every band moves alike nothing is left
    out, and this is the same curve through a longer window.
    """
    power = band_powers(x, hop_ms, rate)
    keep = moving_bands(power)
    kept = power[keep] if keep.any() else power
    if not kept.size:
        return np.zeros(0)
    e = np.log(np.sqrt(kept.astype(np.float64).sum(0)) + 1e-9)
    return e - e.mean()


def phase_align(a, b, rate, most_s=None):
    """Where b sits against a, by phase alone. (seconds, sharpness).

    The envelope way asks where two recordings are loud together, and
    that needs something to be loud and quiet about. Music has almost
    nothing: a mixed, limited song holds the same loudness for minutes.
    Measured on 23.8.2026 -- an iPhone recording of monitor speakers
    against the finished mix of the same music -- the envelope way
    answered 74.775 s at a quality of -0.183, and the right answer was
    569.2 s.

    This one throws the loudness away and keeps only the phase, which
    is what a re-recording through a room survives. It found that 569.2
    s to within twelve milliseconds, first try, with nothing to go on.

    The sharpness is the peak against the noise around it. It says how
    much the answer is worth, and it is the only thing that does: a
    peak that is barely above its neighbours is a guess.
    """
    if len(a) < rate or len(b) < rate:
        return 0.0, 0.0
    n = 1 << int(np.ceil(np.log2(len(a) + len(b))))
    fa = np.fft.rfft(np.asarray(a, float) - np.mean(a), n)
    fb = np.fft.rfft(np.asarray(b, float) - np.mean(b), n)
    both = fb * np.conj(fa)
    # The whitening is the whole point: every frequency counts the
    # same, so a loud bass drum does not drown out the rest.
    line = np.fft.irfft(both / (np.abs(both) + 1e-12), n)
    k = int(np.argmax(line))
    if k > n // 2:
        k -= n
    if most_s is not None and abs(k) / float(rate) > most_s:
        return 0.0, 0.0
    sharp = float(line.max() / (line.std() or 1.0))
    return k / float(rate), sharp


def looks_like_music(env):
    """A guess at whether this is music, for the log and nothing else.

    Speech swings in syllables, two to eight times a second. Music
    swings with the beat and the phrase, slower. Measured on 23.8.2026
    the two do not separate cleanly -- a finished mix landed at 26 per
    cent of its movement in the syllable band, speech at 31 to 32 --
    so this decides nothing. It only explains, afterwards, why the
    plain way had so little to work with.
    """
    e = np.asarray(env, float)
    e = e[np.isfinite(e)]
    if len(e) < 4000:
        return False
    e = e - e.mean()
    power = np.abs(np.fft.rfft(e * np.hanning(len(e)))) ** 2
    hz = np.fft.rfftfreq(len(e), 0.005)
    whole = float(power[(hz >= 0.2) & (hz < 20.0)].sum()) or 1.0
    syllables = float(power[(hz >= 2.0) & (hz < 8.0)].sum()) / whole
    return syllables < 0.20


def cross_correlate(a, b):
    """Where b sits against a, and how well it fits there.

    The peak is the largest positive one, not the largest by size.
    An envelope here is log loudness with its mean taken out, so it
    swings either side of zero -- but two that belong together still
    rise and fall together, and that pushes the correlation up. A
    strong negative peak is the opposite: loud where the other is
    quiet. That is never where they belong, however large it is.

    Taking the absolute value used to hand exactly that back. Measured
    on 23.8.2026, an iPhone recording of monitor speakers against the
    finished mix of the same music: it answered +74.775 s at -0.183,
    while the best real agreement was +0.131 somewhere else again.
    Neither is a match -- but only one of the two is even a possible
    one. The right answer, +569.2 s, needed another method entirely.
    """
    m = min(len(a), len(b))
    if m < 10:
        return 0, 0.0
    a, b = a[:m], b[:m]
    nf = 1 << int(np.ceil(np.log2(2 * m)))
    cc = np.fft.irfft(np.fft.rfft(b, nf) * np.conj(np.fft.rfft(a, nf)), nf)
    k = int(np.argmax(cc))
    if k > nf // 2:
        k -= nf
    label_text = np.sqrt((a ** 2).sum() * (b ** 2).sum())
    return k, float(cc[k % nf] / label_text) if label_text else 0.0


def join_with_report(paths, target, keep_parts=False):
    """Join the blocks of one recording and say what was found.

    The joining was shared; the reporting was not. The ordinary path
    said how many blocks went together, where the gaps were and whether
    two of them overlapped instead of following each other. The
    multitrack path did the same work in silence, so a recording with a
    ten-second hole in it went through without a word.
    """
    source, join_info = join_audio_parts(paths, target, keep_parts=keep_parts)
    if join_info.get("tc"):
        print(T('  %s blocks joined via timecode, start %s')
              % (group_text(join_info["blocks"]),
                 timecode_string(join_info["start"] / float(SR))))
        for at_s, g in join_info.get("gaps_found", []):
            if g > 0:
                print(T('  Gap of %s at %s -- filled with silence')
                      % (as_hms(g / float(SR)), as_hms(at_s / float(SR))))
            else:
                # A negative gap is an overlap. Nothing is filled there;
                # the two sound at the same time.
                print(T('  Overlap of %s at %s -- both sound there')
                      % (as_hms(-g / float(SR)), as_hms(at_s / float(SR))))
        if join_info.get("side_by_side"):
            print(T('  They overlap -- several microphones at once, not '
                    'blocks in a row.'))
            if join_info.get("parts"):
                print(T('  Each one also goes into the video as a track of '
                        'its own: %s')
                      % ", ".join(n for n, _p in join_info["parts"]))
            else:
                print(T('  Only the mix goes into the video '
                        '(--no-single-tracks).'))
    else:
        print(T('  %s blocks joined in name order (no timecode -- gaps '
                'would not be recognisable)')
              % group_text(join_info["blocks"]))
    return source, join_info


def join_audio_parts(paths, target, keep_parts=False):
    """Join several audio files into one.

    With timecodes they are placed on a common time axis and gaps are filled
    with silence. Without, they are laid end to end in the order they came
    in -- the caller has already put them in it.

    The result has as many channels as the widest of them. One stereo
    recording among mono ones therefore keeps its sides, and the mono ones
    are copied to both -- written out rather than left to ffmpeg, which
    would take 3 dB off them on the way.

    With *keep_parts* each recording is also written on its own, on the same
    axis and the same length as the sum, so it can go into the video beside
    the mix. Only where the recordings overlap: blocks laid end to end are
    one recording, and a track per block would be silence with one block in
    it. It costs no second decode -- the same pass writes both.
    """
    paths = list(paths)
    if len(paths) == 1:
        return paths[0], {"blocks": 1, "parts": []}
    channels = widest_track(paths)
    same = [channel_filter(kept_channels(p), channels) for p in paths]
    lengths = [sample_count(p) for p in paths]
    trs = [bext_time_reference(p) for p in paths]
    # Every file has to carry a time, and no two may claim the same one:
    # sorting by it would otherwise depend on the order the files came in.
    # Two recorders started together write exactly the same number, and
    # those recordings run at the same time -- so they are placed on the
    # axis together rather than end to end.
    having_tc = all(t is not None for t in trs)
    if having_tc and len(set(trs)) != len(trs):
        order = sorted(range(len(paths)),
                       key=lambda i: (trs[i], os.path.basename(paths[i]).lower()))
        paths = [paths[i] for i in order]
        lengths = [lengths[i] for i in order]
        trs = [trs[i] for i in order]
        same = [same[i] for i in order]

    if having_tc:
        entries = list(zip(trs, paths, lengths)) if len(set(trs)) != len(trs) \
            else sorted(zip(trs, paths, lengths))
        t0 = entries[0][0]
        total = max(t + n for t, _, n in entries) - t0
        gaps = []
        for (ta, _, na), (tb, _, _) in zip(entries, entries[1:]):
            g = tb - (ta + na)
            if abs(g) > SR // 100:
                gaps.append((ta + na - t0, g))
        # Do the recordings run at the same time or one after another? The
        # timecodes say so, and nothing else has to be guessed: overlapping
        # means several microphones were running at once, and then each one
        # is worth a track of its own.
        side_by_side = any(tb < ta + na for (ta, _, na), (tb, _, _)
                           in zip(entries, entries[1:]))
        alone = []
        if side_by_side and keep_parts:
            folder = os.path.dirname(os.path.abspath(target)) or "."
            for i, (_t, p, _n) in enumerate(entries):
                alone.append((guess_speaker_name(p),
                              os.path.join(folder, "part%d_%s.wav"
                                           % (i, safe_filename(
                                               guess_speaker_name(p))))))
        parts, chains, markers, writes = [], [], [], []
        for i, (t, p, n) in enumerate(entries):
            parts += ["-i", p]
            d = t - t0
            f = [channel_filter(kept_channels(p), channels)]
            f += ["adelay=delays=%dS:all=1" % d] if d else []
            f += ["apad=whole_len=%d" % total, "atrim=end_sample=%d" % total,
                  "asetpts=N/SR/TB"]
            # One decode, two uses: the sum, and the single track beside it.
            # A filter output can only be read once, hence the split.
            tail = ",asplit=2[t%d][s%d]" % (i, i) if alone else "[t%d]" % i
            chains.append("[%d:a]%s%s" % (i, ",".join(f), tail))
            markers.append("[t%d]" % i)
            if alone:
                writes += (["-map", "[s%d]" % i, "-c:a", "pcm_s24le",
                            "-write_bext", "1", "-metadata",
                            "time_reference=%d" % t0]
                           + wav_safe(alone[i][1])
                           + ["-y", alone[i][1]])
        fc = ";".join(chains) + ";" + "".join(markers) +\
             "amix=inputs=%d:normalize=0[out]" % len(markers)
        shell_quote(["ffmpeg", "-v", "error"] + parts + ["-filter_complex", fc,
            "-map", "[out]", "-c:a", "pcm_s24le", "-write_bext", "1",
            "-metadata", "time_reference=%d" % t0]
            + wav_safe(target) + ["-y", target] + writes)
        return target, {"blocks": len(paths), "tc": True, "gaps_found": gaps,
                      "start": t0, "side_by_side": side_by_side,
                      "parts": alone}

    # In the order they came in. Without a timecode that order is the
    # only one there is: it comes from the counter, from the clock in the
    # name, or from a hand that said these belong together in this order.
    # Sorting by name again would throw the last of the three away.
    row = list(zip(paths, lengths))
    if len(set(same)) == 1 and same[0] == "anull":
        # All alike: the concat demuxer is the cheapest way and needs no
        # filter graph at all.
        lst = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
        for p, _ in row:
            lst.write("file '%s'\n" % os.path.abspath(p).replace("'", "'\\''"))
        lst.close()
        try:
            shell_quote(["ffmpeg", "-v", "error", "-f", "concat", "-safe", "0",
                "-i", lst.name, "-c:a", "pcm_s24le", "-y", target])
        finally:
            os.unlink(lst.name)
        return target, {"blocks": len(paths), "tc": False, "parts": []}
    # Different channel counts: the concat demuxer refuses those, so the
    # blocks are brought to the same width first and strung together in the
    # filter graph.
    parts, chains, markers = [], [], []
    for i, (p, _n) in enumerate(row):
        parts += ["-i", p]
        chains.append("[%d:a]%s[t%d]"
                      % (i, channel_filter(kept_channels(p), channels), i))
        markers.append("[t%d]" % i)
    fc = ";".join(chains) + ";" + "".join(markers) +\
        "concat=n=%d:v=0:a=1[out]" % len(markers)
    shell_quote(["ffmpeg", "-v", "error"] + parts + ["-filter_complex", fc,
        "-map", "[out]", "-c:a", "pcm_s24le", "-y", target])
    return target, {"blocks": len(paths), "tc": False, "parts": []}


def audio_range_covered_by_video(audio, video, edge_s=60.0):
    """Return which part of the audio file has a counterpart in the picture.

    Only the first and last *edge_s* seconds are searched. Two passes:
    coarse with 4 s windows in half second steps, then fine with 1 s windows
    in 50 ms steps around the edge found. The coarse window finds the edge
    reliably but sits systematically late -- a window half inside the intro
    only half matches. The second pass recovers that.
    """
    HOP, rate = 5.0, 4000
    env_video = video_envelope(video, HOP, rate)
    env_audio = envelope(decode_audio(audio, rate=rate), HOP, rate)
    n_audio = sample_count(audio)
    if len(env_video) < 200 or len(env_audio) < 200:
        return 0, n_audio, {"reason": T('too short')}

    # The anchor is the middle of the picture, not of the audio: the audio can
    # be a multiple longer, and then its middle may lie entirely outside what
    # the camera recorded.
    m0, m1 = int(len(env_video) * 0.25), int(len(env_video) * 0.75)
    middle = env_video[m0:m1]
    nf = 1 << int(np.ceil(np.log2(len(env_audio) + len(middle))))
    cc = np.fft.irfft(np.fft.rfft(env_audio, nf)
                      * np.conj(np.fft.rfft(middle, nf)), nf)
    # Where the picture sits when the audio is at zero.
    shift = m0 - int(np.argmax(cc[:max(1, len(env_audio))]))

    def quality(i, W):
        j = i + shift
        if i < 0 or i + W > len(env_audio) or j < 0 or j + W > len(env_video):
            return 0.0
        a, b = env_audio[i:i + W], env_video[j:j + W]
        na, nb = np.sqrt((a ** 2).sum()), np.sqrt((b ** 2).sum())
        return float((a * b).sum() / (na * nb)) if na > 0 and nb > 0 else 0.0

    win_coarse = int(4.0 * 1000 / HOP)
    # Measure the reference level only where audio and picture both run.
    t0 = max(0, -shift)
    t1 = min(len(env_audio), len(env_video) - shift)
    means = [quality(i, win_coarse) for i in
                   range(t0 + int((t1 - t0) * 0.3),
                         max(t0 + int((t1 - t0) * 0.3) + 1,
                             t0 + int((t1 - t0) * 0.7)), win_coarse)]
    level = float(np.median(means)) if means else 0.0
    if level < 0.15:
        return 0, n_audio, {"reason":
                            T('no match in the middle either (%s)')
                            % decimal_text("%.2f" % level)}
    threshold = max(0.12, 0.5 * level)
    R = int(edge_s * 1000 / HOP)
    step_coarse = int(0.5 * 1000 / HOP)
    win_fine = int(1.0 * 1000 / HOP)
    step_fine = max(1, int(0.05 * 1000 / HOP))

    def edge(front):
        """Return where the part matching the picture begins or ends.

        Searched around the place it should sit after coarse alignment, not
        around the start and end of the file. Where the audio is a multiple of
        the picture in length, the edges lie far inside.
        """
        anchor = t0 if front else t1 - win_coarse
        coarse, run = None, 0
        steps = range(0, R, step_coarse)
        for d in steps:
            i = anchor + d if front else anchor - d
            if i < 0 or i + win_coarse > len(env_audio):
                continue
            if quality(i, win_coarse) > threshold:
                run += 1
                if run >= 2:
                    coarse = i if front else i + win_coarse
                    break
            else:
                run = 0
        if coarse is None:
            return max(0, t0) if front else min(len(env_audio), t1)
        best = coarse
        for k in range(1, int(6.0 * 1000 / HOP / step_fine)):
            i = coarse - k * step_fine if front else coarse + k * step_fine
            if quality(i if front else i - win_fine, win_fine) > threshold:
                best = i
            else:
                break
        return max(0, best) if front else min(len(env_audio), best)

    i0, i1 = edge(True), edge(False)
    if i1 <= i0:
        return 0, n_audio, {"reason": T('edges implausible')}
    return (max(0, int(i0 * HOP / 1000.0 * SR)),
            int(min(n_audio, i1 * HOP / 1000.0 * SR)),
            {"threshold": threshold, "level": level})


# What the phase way has to beat before it is believed instead of the
# plain one. Measured on 23.8.2026: on the music that sent us looking
# it came out at 28.7 against a nearest rival of 26.5, and the answer
# was right to twelve milliseconds. Not measured on enough material to
# call it a threshold -- it is a floor, and the log prints the number
# so anybody can see how close it was.
PHASE_SHARP_ENOUGH = 8.0


def align_on_moving_bands(x_video, x_audio, HOP, rate, sample_points,
                          window_s, distance_s):
    """The same way again, on the bands that carry movement.

    Returns what align_envelopes returns, or None where a curve came
    out too short to compare. The numbers in it are the ordinary ones
    -- sample points and their spread -- so the gate that judges the
    first answer judges this one by the same rule.
    """
    curve_video = band_envelope(x_video, HOP, rate)
    curve_audio = band_envelope(x_audio, HOP, rate)
    if len(curve_video) < 10 or len(curve_audio) < 10:
        return None
    return align_envelopes(curve_video, curve_audio, HOP, sample_points,
                           window_s, distance_s, warn=False)


def align_audio_to_video(audio, video, head_s, sample_points=None, window_s=20.0,
               distance_s=120.0):
    """Return a, b with audio time = a + b * video time."""
    HOP, rate = 5.0, 4000
    env_video = video_envelope(video, HOP, rate)
    x_audio = decode_audio(audio, rate=rate, ss=head_s / float(SR))
    env_audio = envelope(x_audio, HOP, rate)
    a, b, st = align_envelopes(env_video, env_audio, HOP, sample_points,
                               window_s, distance_s,
                               warn=os.path.basename(audio))
    if st.get("quality", 0.0) >= WEAK_MATCH:
        return a, b, st
    # The plain way found nothing worth having. Both files are read
    # here, once, for the second try and for the phase way under it --
    # the phase way read them itself before, so this costs no decode.
    x_video = decode_audio(video, rate=rate)
    second = align_on_moving_bands(x_video, x_audio, HOP, rate,
                                   sample_points, window_s, distance_s)
    if second is not None and fit_places_it(second[2]):
        # Sample points enough, and close enough to one line. Measured
        # over 293 pairs out of different productions not one gets that
        # far, and all 85 that belong together do.
        second[2]["from_bands"] = True
        return second
    # Both curves came up empty. The phase way -- it only ever runs
    # here, where the answer was going to be wrong anyway, and it is
    # the one way no sample point backs up.
    st["music_like"] = looks_like_music(env_audio)
    where, sharp = phase_align(x_video, x_audio, rate)
    st["phase_s"], st["phase_sharp"] = where, sharp
    if sharp >= PHASE_SHARP_ENOUGH:
        st["from_phase"] = True
        # No drift from this one: it answers where, not how fast. The
        # factor stays 1.0 and the report says the drift is unknown
        # rather than pretending it is zero.
        return where, 1.0, st
    # Both ways came up empty. The numbers still travel back, because
    # the log prints them, but they are marked for what they are: not
    # an alignment, a guess. Whoever asked has to decide what to do
    # with a file that has no place -- see cannot_be_placed.
    st["unplaceable"] = True
    return a, b, st


# How far a point may sit from the middle before it is thrown away.
# 3 is the ordinary choice for a robust fit; the floor keeps a very
# tight set of points from throwing away its own scatter. 20 ms is the
# floor because it is four times HOP -- what the envelope can resolve
# at all. It is a floor, not a measured threshold, and says so.
# Below this the global agreement between two envelopes is not worth
# calling a match. Not measured on real material yet -- it is the old
# 0.05 floor, kept, and now applied to the signed value instead of the
# size. What a good alignment looks like is measured: 0.5 to 0.9 on
# material that belongs together, 0.13 on a camera track against a
# finished mix of the same room.
WEAK_MATCH = 0.05

# The shortest stretch of shared sound and picture that a run will work
# with when the alignment could not place a single sample point in it.
# Where it did place points, the length does not matter -- what was
# measured was measured. Ten seconds because the alignment's own spacing
# is a couple of seconds and a handful of them is the least that says
# anything; the thirty that stood here before was a round number nobody
# had measured, and it refused 26 seconds of picture that come out exact.
AXIS_MIN_WINDOW_S = 10.0

# What one camera has to match another by before it is laid on the axis.
# Far above WEAK_MATCH: between two cameras there is no phase way to fall
# back on, so the envelopes are the whole measurement, and the floor for
# "nothing at all" is not the number for "these two heard the same room".
#
#   camera against camera, 21 s against 26 s      0.837   right
#   camera against camera, 68 min against 68 min  0.811   right
#   an 18-second jingle against 68 min of camera  0.210   nonsense
#
# Measured 30.8.2026; two recordings of different conversations came to
# 0.21 to 0.27 the same day. A real match sits above 0.8, unrelated
# material with structure near 0.25, and half is the middle of the gap.
CAMERA_MATCH_ENOUGH = 0.5
# Measured 1.9.2026, four productions, 85 pairs that belong together
# against 293 that do not: the correlation overlaps (worst real 0.203,
# best foreign 0.124), the fit does not (62 against 43 sample points,
# 11.3 against 22.4 ms).
FIT_POINTS_ENOUGH = 50
FIT_SPREAD_MS = 15.0


def fit_places_it(st):
    """Report whether the sample points alone place this file.

    The correlation above compares two loudness curves over the whole
    runtime, and a steady tone in one of them -- mains hum -- pushes it
    down without moving where the file belongs. The fit does move with
    the answer: many points spread over the runtime, all on one line.
    A file that fits nowhere gets neither.
    """
    spread = st.get("spread_ms")
    return (st.get("points", 0) >= FIT_POINTS_ENOUGH
            and spread is not None and spread <= FIT_SPREAD_MS)


# Against a sound recording a real match reads far lower, so this floor
# only tells a measurement from noise. It stood as a bare 0.15 in the
# middle of the axis measurement until 31.8.2026.
SOUND_MATCH_ENOUGH = 0.15
# Not the count of sample points: they are set 30 seconds apart, so
# shorter material has none at all -- the 21-second camera above had
# none and was placed exactly right.


def timecode_places_it(own, others):
    """Report whether a timecode can put this file among the others.

    A timecode alone places nothing. It is a reading of a clock, and a
    reading only says something next to a second one: the file has to
    carry one and so has something else in the material. Where a
    single file has a timecode and no other does, it is as unplaced as
    if it had none.
    """
    return own is not None and any(t is not None for t in others)


def files_with_no_place(weak, clocks):
    """Which of the badly fitting files no clock places either.

    The one reading of "it fits nowhere": the intro proposal and the
    bar on the wide shot both ask here. Weak alone is not it -- a
    camera whose sound says nothing is still placed by its timecode --
    and below the floor is not it either, because that is measured
    against nothing at all and a jingle lands above it.
    """
    return [p for p in weak
            if not timecode_places_it(
                clocks.get(p), [t for q, t in clocks.items() if q != p])]


def cannot_be_placed(st, own_tc, other_tcs):
    """Report whether an alignment left a file with no place at all.

    Two ways lead to a place, and either one is enough. The timecode
    is the first, and where it answers the sound is not asked at all:
    a camera whose microphone heard nothing of the room is still
    placed to the frame by its clock, and refusing it because of its
    sound would throw away a file that is in fact known to the
    millisecond. The measurement is the second way, and *st* carries
    its verdict: "unplaceable" stands there when every way of
    measuring came up empty.

    Only where neither answers is there nothing left. Then the file is
    refused rather than laid down somewhere, because laid down
    somewhere it looks exactly like a file that fits.

    Not by the count of sample points, though that was tried on
    30.8.2026 and reverted the same hour: on the ordinary path a
    measurement with no sample points is still a measurement -- the
    offset comes from the cross correlation and only the clock drift is
    missing, which is what "too few sample points for a drift
    measurement" says. Reading that as "no place" refused material the
    tests prove is placed to the sample.
    """
    if not (st or {}).get("unplaceable"):
        return False
    return not timecode_places_it(own_tc, other_tcs)


def which_way_placed(st, hint=""):
    """Add to a track's note which way put it on the axis.

    The plain loudness curve says nothing, being the ordinary answer;
    the two later ways do, and both report lines use this one function
    so they say the same thing. The phase carries its sharpness against
    PHASE_SHARP_ENOUGH, and says the drift is unknown: it answers where
    a track sits, not how fast it ran, and the line beside it prints
    +0.00 ppm, which would otherwise read as a drift measured at zero.
    """
    if (st or {}).get("from_bands"):
        hint = (hint + ", " if hint else "") + T('placed on the bands '
                                                 'that move')
    if (st or {}).get("from_phase"):
        hint = (hint + ", " if hint else "") + (
            T('placed by phase, sharpness %s against a floor of %s, '
              'drift unknown')
            % (decimal_text("%.1f" % float(st.get("phase_sharp") or 0.0)),
               decimal_text("%.1f" % PHASE_SHARP_ENOUGH)))
    return hint


def no_place_message(name):
    """Say that a file cannot be placed, and what would fix it."""
    return T('%s cannot be placed: its sound has nothing in common '
             'with the rest of the material, and the file carries no '
             'timecode. It needs one that fits the other recordings, '
             'and that has to be set with another program.') % name


def timecode_seconds(info):
    """The timecode in a video's facts, in seconds, or nothing."""
    if not (info or {}).get("tc"):
        return None
    try:
        return parse_timecode(info["tc"], max(1.0, info.get("fps") or 30.0))
    except (ValueError, TypeError):
        return None


OUTLIER_SIGMA = 3.0
OUTLIER_FLOOR_S = 0.020
OUTLIER_ROUNDS = 6


def _spans_share(tv, duration_v):
    """How much of the runtime the surviving points still cover.

    A set that has been cleaned down to one corner of the recording
    looks tidy and says nothing about the rest of it.
    """
    if len(tv) < 2 or duration_v <= 0:
        return 0.0
    return float((max(tv) - min(tv)) / duration_v)


def without_outliers(tv, dt):
    """Throw away points that lie far from the others. (tv, dt, dropped).

    The anchor is the median, not the line: a single outlier tips the
    line, and then the wrong points look like the odd ones out. The
    scatter is measured as the median absolute deviation, scaled by
    1.4826 so it means the same as a standard deviation on ordinary
    data.

    Six rounds at most, and never below three points -- two points
    always fit a line perfectly, which would turn a broken measurement
    into a confident one. Every point thrown away is named in the log:
    a run that cleans up in silence cannot be checked afterwards.
    """
    kept_t, kept_d = np.asarray(tv, float), np.asarray(dt, float)
    dropped = []
    for _ in range(OUTLIER_ROUNDS):
        if len(kept_t) < 4:
            break
        b, a = np.polyfit(kept_t, kept_d, 1)
        rest = kept_d - (a + b * kept_t)
        middle = float(np.median(rest))
        mad = float(np.median(np.abs(rest - middle))) * 1.4826
        limit = max(OUTLIER_SIGMA * mad, OUTLIER_FLOOR_S)
        keep = np.abs(rest - middle) <= limit
        if keep.all() or int(keep.sum()) < 3:
            break
        for i in np.flatnonzero(~keep):
            dropped.append((float(kept_t[i]), float(rest[i]) * 1000))
        kept_t, kept_d = kept_t[keep], kept_d[keep]
    return kept_t, kept_d, dropped


def align_envelopes(env_video, env_audio, HOP=5.0, sample_points=None, window_s=20.0,
                       distance_s=120.0, points_off="video", warn=True):
    """The same on ready-made envelopes.

    Which way round: the second curve's time = a + b * the first
    curve's time. Said without the word "reference" on purpose --
    align_cameras calls the *first* of its two the reference, and
    reading this line with that meaning turns the pair round.

    *points_off* decides which of the two curves the sample points are
    picked on; the first by default. For a de-bled speaker track it has to
    be the second: only one speaker is left there, and only where they speak
    is there anything to compare. Picking the spots on the camera track
    would land mostly in passages where somebody else talks.

    The number of sample points grows with the runtime -- about one every
    two minutes, at least nine. More points make the slope more certain, and
    the slope is the clock drift. The envelopes are in memory anyway, so an
    extra point costs almost nothing. Kept separate from align_audio_to_video
    so two cameras can be compared without reading the large files twice.
    """
    if len(env_video) < 10 or len(env_audio) < 10:
        raise RuntimeError(T('too little audio to align'))
    if points_off == "audio":
        a, b, st = align_envelopes(env_audio, env_video, HOP, sample_points, window_s,
                                      distance_s, warn=warn)
        return -a / b, 1.0 / b, st
    k, g = cross_correlate(env_video, env_audio)
    coarse = k * HOP / 1000.0
    # Signed, not by size: see cross_correlate. Said out loud even
    # where it passes, because "found something" and "found it barely"
    # look the same from outside. A second try on the same two files
    # has heard it once and asks for silence.
    if warn and g < WEAK_MATCH:
        # warn carries the name where the caller has one. Without it
        # a run with several recordings prints a heap of warnings
        # nobody can put back against a file.
        print(as_warn(T('      WARNING: weak match for %s (%s, %s is '
                        'the floor). The two may not belong together.')
                      % (warn if isinstance(warn, str)
                         else T('this pair of files'),
                         decimal_text("%.3f" % g),
                         decimal_text("%.2f" % WEAK_MATCH))))

    duration_v = len(env_video) * HOP / 1000.0
    W = int(window_s * 1000 / HOP)
    # Create twice as many candidates as needed -- the uninteresting ones drop
    # out immediately, and too many beats too few.
    if sample_points is None:
        sample_points = max(9, min(80, int(duration_v / distance_s) + 1))
    candidates = max(sample_points * 2, 12)
    spread_total = float(np.std(env_video)) or 1.0

    points, with_signal = [], 0
    for i in range(candidates):
        t = duration_v * (i + 0.5) / candidates
        i0 = int(t * 1000 / HOP) - W // 2
        if i0 < 0 or i0 + W > len(env_video):
            continue
        seg = env_video[i0:i0 + W]
        # Silence or steady noise is no use for comparison: there are no edges
        # to align on.
        if float(np.std(seg)) < 0.35 * spread_total:
            continue
        with_signal += 1
        j0 = i0 + int(round(coarse * 1000 / HOP))
        pad = int(2000 / HOP)
        if j0 - pad < 0 or j0 + W + pad > len(env_audio):
            continue
        around = env_audio[j0 - pad:j0 + W + pad]
        nf = 1 << int(np.ceil(np.log2(len(around) + len(seg))))
        cc = np.fft.irfft(np.fft.rfft(around, nf) * np.conj(np.fft.rfft(seg, nf)), nf)
        kk = int(np.argmax(cc[:2 * pad + 1])) - pad
        label_text = np.sqrt((seg ** 2).sum() * (around[pad + kk:pad + kk + W] ** 2).sum())
        if label_text <= 0:
            continue
        if float(cc[kk + pad] / label_text) > 0.2:
            points.append((t, coarse + kk * HOP / 1000.0))
    count_n = {"candidates": candidates, "with_signal": with_signal,
                "points": len(points)}

    if len(points) >= 3:
        tv = np.array([p[0] for p in points])
        dt = np.array([p[1] for p in points])
        # What the raw points say, before anything is thrown away. It
        # stays in the report: a run that quietly cleans itself up and
        # then calls the result good has traded a loud fault for a
        # quiet one.
        b0, a0 = np.polyfit(tv, dt, 1)
        raw_spread = float(np.std(dt - (a0 + b0 * tv)) * 1000)
        tv, dt, dropped = without_outliers(tv, dt)
        b, a = np.polyfit(tv, dt, 1)
        rest = dt - (a + b * tv)
        n = len(tv)
        sxx = float(((tv - tv.mean()) ** 2).sum())
        s2 = float((rest ** 2).sum()) / max(1, n - 2)
        se_b = (s2 / sxx) ** 0.5 if sxx > 0 else float("inf")
        count_n.update({"ppm": b * 1e6, "ppm_error": se_b * 1e6,
                         "spread_ms": float(np.std(rest) * 1000), "quality": g,
                         "raw_spread_ms": raw_spread,
                         "dropped": dropped,
                         "spans_share": _spans_share(tv, duration_v),
                         "offsets": [float(x) for x in dt],
                         "times": [float(x) for x in tv]})
        return a, 1.0 + b, count_n
    count_n["quality"] = g
    return coarse, 1.0, count_n


#--------------------------------------------- Keeping itself up to date

# =====================================================================
#  Keeping itself up to date
# =====================================================================
# The program can look whether a newer release is out and, if somebody
# says so, let pip fetch it. Three rules hold it in place:
#
#   * Looking is free and needs no permission: one question for a
#     version number, nothing sent. It always looks; only
#     VPM_NO_UPDATE_CHECK stops it, and that belongs to the machine.
#   * Fetching is asked every single time: the window in a box, the
#     command line with a line and --update. Never unasked, and never
#     while a run is going on.
#   * pip fetches it, and there is no second way: this is a folder,
#     and writing over the way in leaves the rest of it behind.

RELEASES = ("https://api.github.com/repos/Bascht74/videopodcast-magic"
            "/releases/latest")
# The whole list, for the versions in between. Whoever skipped two
# releases wants to read all three, not only the newest.
RELEASE_LIST = ("https://api.github.com/repos/Bascht74/videopodcast-magic"
                "/releases?per_page=30")
# Off for a test run: a suite must not reach for the network, and it
# must certainly not swap the file it is testing.
UPDATE_OFF = bool(os.environ.get("VPM_NO_UPDATE_CHECK"))
# What pip is pointed at where the program was installed rather than
# downloaded. No PyPI in it: pip reads the repository itself, and
# pip_update hangs the release on the end, because the address alone
# is the head of the default branch.
PIP_SOURCE = "git+https://github.com/Bascht74/videopodcast-magic"
UPDATE_SINK = None   # set by the GUI: callable(job) that runs job(say)
                     # in a thread, its lines going into the Output tab

# How far back the way back reaches. Below v3.0.0b0 the repository is
# no package at all -- v2.32.0-beta carries neither pyproject.toml nor
# setup.py -- so pip sent there fetches what it cannot install. Twenty,
# because a list longer than its window is no longer a choice.
OLDEST_TO_GO_BACK_TO = "v3.0.0b0"
MOST_TO_GO_BACK_TO = 20


def update_skip_file():
    """Where the version somebody chose to pass over is kept."""
    folder = cache_folder()
    return os.path.join(folder, "update_skip") if folder else ""


def update_skipped():
    """The version somebody chose to pass over, or "" for none."""
    where = update_skip_file()
    if not where or not os.path.exists(where):
        return ""
    try:
        with open(where, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def set_update_skipped(tag):
    """Pass over this one version. The next one asks again.

    In place of "do not ask again", which stopped the looking for
    good: a no that cannot be taken back is a trap, and this program
    has walked the owner into it twice. One version passed over is not
    an answer about all of them, and nothing else here says no.
    """
    where = update_skip_file()
    if not where:
        return
    try:
        with open(where, "w", encoding="utf-8") as f:
            f.write(str(tag or ""))
    except OSError:
        return


def updated_from_file():
    """Where the version the last install left behind is kept."""
    folder = cache_folder()
    return os.path.join(folder, "updated_from") if folder else ""


def updated_from():
    """The version that was running before the last install, or "".

    Whoever goes looking for the way back has, nearly every time, just
    been moved off exactly that version, so it is what the list of
    earlier versions opens on. A guess and no more: it is the entry
    that is picked out, never the only one on offer.
    """
    where = updated_from_file()
    if not where or not os.path.exists(where):
        return ""
    try:
        with open(where, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def set_updated_from(tag):
    """Note the version an install that went through left behind."""
    where = updated_from_file()
    if not where:
        return
    try:
        with open(where, "w", encoding="utf-8") as f:
            f.write(str(tag or ""))
    except OSError:
        return


# PEP 440 hangs the pre-release straight on the numbers, with no dash:
# a1 is an alpha, b0 a beta, rc1 a release candidate. Without a number
# it means the zeroth of them, so 3.0.0b reads as 3.0.0b0.
PIP_PRE_RELEASE = re.compile(r"^(\d+(?:\.\d+)*)(a|b|rc)(\d*)$")


def pre_release_key(pre):
    """The name of a pre-release, cut so that ten comes after nine.

    Runs of digits and runs of everything else, each run of digits as
    the number it is. The 0 and the 1 in front keep the two kinds
    apart, so a number is never held against a word: b9 falls under
    b10 and beta.2 under beta.10, where either read as text would sort
    the other way round.
    """
    return tuple((0, int(run)) if run.isdigit() else (1, run)
                 for run in re.findall(r"\d+|\D+", pre))


def version_key(text):
    """A version as something that can be compared.

    Two spellings and one order: 2.0.0-beta the way the tags read, and
    3.0.0b0 the way pip writes it. Both are older than the same
    numbers with nothing hung on them, which is what Semantic
    Versioning and PEP 440 both say. Anything unreadable sorts oldest,
    so a name nobody understands never counts as newer.
    """
    text = str(text or "").strip().lstrip("vV")
    core, _, pre = text.partition("-")
    hung_on = None if pre else PIP_PRE_RELEASE.match(core)
    if hung_on:
        core = hung_on.group(1)
        pre = hung_on.group(2) + (hung_on.group(3) or "0")
    numbers = []
    for piece in core.split(".")[:3]:
        numbers.append(int(piece) if piece.isdigit() else 0)
    while len(numbers) < 3:
        numbers.append(0)
    # 1 for a finished release, 0 for a pre-release: that way 2.0.0
    # comes after 2.0.0-beta, which is what the standard says.
    return (tuple(numbers), 1 if not pre else 0, pre_release_key(pre))


def releases_in_between(newest, running):
    """The release texts from *running* up to *newest*, newest first.

    Somebody who skipped two versions was shown the newest text alone
    and had to guess at the rest. GitHub answers with the whole list,
    so the versions in between cost one more request and no thought.

    Returns "" where the list cannot be had. The caller then keeps the
    single text it already has, which is what was shown before -- a
    failure here must never be worse than not asking.
    """
    try:
        import urllib.request
        with urllib.request.urlopen(RELEASE_LIST, context=https_context(),
                                    timeout=20) as answer:
            found = json.load(answer)
    except Exception:
        return ""
    if not isinstance(found, list):
        return ""
    want = []
    for one in found:
        if not isinstance(one, dict) or one.get("draft"):
            continue
        tag = str(one.get("tag_name") or "")
        if not tag:
            continue
        # Strictly between: the newest is already in hand, and the
        # running one is what somebody has.
        if version_key(running) < version_key(tag) <= version_key(newest):
            want.append((version_key(tag), tag,
                         str(one.get("body") or "").strip()))
    want.sort(reverse=True)
    # Each one cut to the language this is running in, here rather than
    # where it is shown: two windows show this text, and only one of
    # them was cutting. The other handed a German reader the English
    # half, which is the half that comes first.
    return "\n\n".join("## %s\n\n%s" % (tag, release_text_in(body))
                        for _k, tag, body in want if body)


def older_releases(running):
    """The versions to go back to, newest first, and why not: (list, "").

    Older than *running* and never *running* itself, none below
    OLDEST_TO_GO_BACK_TO, at most MOST_TO_GO_BACK_TO of them.

    An empty list with nothing beside it means there is nothing older
    to go back to. An empty list with a sentence means nobody knows,
    and the two must not read alike: saying something reassuring where
    nothing was seen is worse than saying it could not be seen.

    The address answers with the newest thirty releases, so somebody
    thirty releases behind gets nothing here. That is the right
    answer for them: what they want is the way forward.
    """
    try:
        import urllib.request
        with urllib.request.urlopen(RELEASE_LIST, context=https_context(),
                                    timeout=20) as answer:
            found = json.load(answer)
    except Exception as e:
        return [], T('Could not look for earlier versions: %s') % e
    if not isinstance(found, list):
        return [], T('The list of earlier versions could not be read.')
    floor, here = version_key(OLDEST_TO_GO_BACK_TO), version_key(running)
    want = []
    for one in found:
        if not isinstance(one, dict) or one.get("draft"):
            continue
        tag = str(one.get("tag_name") or "")
        if not tag:
            continue
        if floor <= version_key(tag) < here:
            want.append((version_key(tag), tag))
    want.sort(reverse=True)
    return [tag for _key, tag in want[:MOST_TO_GO_BACK_TO]], ""


def back_pick(older):
    """Which of *older* the way back is opened on, or "" for none.

    The version the last install left behind where it is still on
    offer, otherwise the newest -- a note gone stale must not take
    the choice with it. Held by version_key and not as text: what is
    noted is this program's own VERSION, 3.0.0b4, while the release
    carrying it is tagged v3.0.0b4, and as text those never meet.
    """
    was = updated_from()
    if was:
        for tag in older:
            if version_key(tag) == version_key(was):
                return tag
    return older[0] if older else ""


def newer_release(asked=False):
    """(tag, page, what changed, trouble) of a newer release.

    All four are "" where a newer release was looked for and none was
    there. *trouble* carries a sentence where the looking itself could
    not happen -- no network, or a certificate store this Python cannot
    read. That is not the same answer as "nothing newer", and it must
    not read as one: a program that says something reassuring where it
    knows nothing is worse than one that says it does not know.

    A pre-release is never the answer: GitHub only calls one release
    the latest, and it is never one put out for trying.

    The third piece is the release text itself. An address alone asks
    somebody to open a browser to find out what they are about to
    install, and most will not: they will click yes without knowing.
    It comes down with the same answer, so it costs nothing.

    *asked* is a direct question -- from the menu or from --update. A
    version passed over does not stand against that;
    VPM_NO_UPDATE_CHECK does, because that one is set by whoever runs
    the machine rather than by whoever clicks.
    """
    if UPDATE_OFF:
        return "", "", "", ""
    passed_over = "" if asked else update_skipped()
    try:
        import urllib.request
        with urllib.request.urlopen(RELEASES, context=https_context(),
                                    timeout=20) as answer:
            found = json.load(answer)
    except Exception as e:
        # Said, not swallowed. Whoever did not ask is not told -- a
        # start without a network would otherwise complain every time.
        return "", "", "", (T('Could not look for a newer version: %s')
                            % e if asked else "")
    tag = str(found.get("tag_name") or "")
    if passed_over and tag == passed_over:
        # Passed over once, so it is not offered again by itself. The
        # next release has another name and asks, and the menu asks
        # whenever somebody wants it to.
        return "", "", "", ""
    if not tag or version_key(tag) <= version_key(VERSION):
        # Nothing newer. The answer already carries the text of the
        # release that is running, and throwing it away means asking
        # somebody to open a browser to read what they already have.
        # It comes back with an empty tag, so callers that only want a
        # newer version are unaffected.
        same = version_key(tag) == version_key(VERSION) if tag else False
        return ("", str(found.get("html_url") or "") if same else "",
                str(found.get("body") or "").strip() if same else "", "")
    text = str(found.get("body") or "").strip()
    # Two versions may lie between what runs here and what is out.
    # Showing only the newest hides what somebody is also getting.
    whole = releases_in_between(tag, VERSION)
    return (tag, str(found.get("html_url") or ""), whole or text, "")


def not_installed_note():
    """The one sentence for "pip has nothing here to update".

    One place, so the window and the console cannot say two different
    things about the same case. pip is the only way in and therefore
    the only way on; a copy running out of a folder of its own is not
    a version pip keeps a record of, so the way on is the command that
    installs it properly.
    """
    return T('This copy runs out of a folder of its own, so pip has '
             'nothing here to update. This installs it: %s') % (
                 "pip3 install -U " + PIP_SOURCE)


def pip_update(tag, say):
    """Let pip put that release in place. "" when it worked, or why not.

    The one road, forwards and backwards alike: *tag* is a release
    somebody chose, and a direct git address tells pip to install what
    the address names rather than only to climb. The Python this is
    running in, so what changes is the installation that would run,
    and pip's lines go on as they arrive: the first install fetches a
    gigabyte, and silence looks broken.
    """
    order = [sys.executable, "-m", "pip", "install", "-U",
             PIP_SOURCE + "@" + tag]
    say("  %s\n" % " ".join(order))
    try:
        started = subprocess.Popen(order, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
    except OSError as e:
        return T('pip could not be started: %s') % e
    for line in started.stdout:
        say(line.decode("utf-8", "replace"))
    code = started.wait()
    if code:
        return T('pip stopped with %s. What it managed stands in the '
                 'lines above.') % code
    # Written only where pip went through, and it is what was running
    # until this moment: the way back opens on it, because whoever
    # wants the way back has just been moved off that one version.
    set_updated_from(VERSION)
    say(T('%s is installed. It runs from the next start.') % tag + "\n")
    return ""


def update_promise(owner):
    """What the window says it will do before it asks.

    Two different things happen, so two different sentences are owed.
    *owner* is the folder a package manager installed this into, and
    where there is one pip fetches the new version into it. Where
    there is none there is nothing pip keeps a record of, and the
    sentence says so before the button is pressed rather than after.
    """
    if owner:
        return T('Update? pip fetches it into %s. What pip says appears '
                 'under Output, and the new version runs from the next '
                 'start.') % owner
    return not_installed_note()


def update_fetched(tag, owner):
    """Hand that release to pip. "" where it is under way, or why not.

    pip is the only way in and therefore the only way on: it keeps the
    record of which version is installed, and this program is a folder
    whose way in is one file of nine. pip takes minutes, so the window
    runs it beside itself rather than in its own thread.
    """
    if not owner:
        return not_installed_note()
    if UPDATE_SINK is None:
        return T('There is no window to show what pip says.')
    UPDATE_SINK(lambda say: pip_update(tag, say))
    return ""


def update_note():
    """Say on the command line that a newer version is out.

    A line and nothing else. A run started out of a script must not
    stop to ask anything, so there is no box and no question here, and
    nothing at all is fetched. What the second line names is the way
    that works here: --update where pip owns this copy, and the
    command that installs it where nothing owns it.
    """
    tag, page, _changed, _trouble = newer_release()
    if not tag:
        return
    print(T('%s is out. This is %s.') % (tag, VERSION))
    if installed_by_a_package_manager():
        print(T('--update fetches it and puts it in place.'))
    else:
        print(not_installed_note())
    if page:
        print("  %s" % page)


def update_from_command_line():
    """Let pip fetch the newer version. 0, or 1 with a word.

    Asked for outright, so a version passed over in the window does
    not stand against it. The same machinery as the window's button,
    down to the command: what differs is where pip's lines go.
    Nothing is started again afterwards: a command line hands the next
    run back to whoever is at the keyboard.
    """
    if UPDATE_OFF:
        print(T('The check for new versions is switched off here.'))
        return 1
    tag, _page, _changed, trouble = newer_release(asked=True)
    if trouble:
        print(trouble)
        return 1
    if not tag:
        print(T('No newer version found. This one is %s.') % VERSION)
        return 0
    if not installed_by_a_package_manager():
        print(not_installed_note())
        return 1
    # Whoever typed --update has a console, so pip writes into it as it
    # goes -- write_through is to this what UPDATE_SINK is to the
    # window, and pip's first install fetches a gigabyte: a console
    # standing silent for minutes looks like a program that has hung.
    trouble = pip_update(tag, write_through)
    if trouble:
        print(trouble)
        return 1
    return 0


def start_again():
    """Start this program once more, in place of this run."""
    here = os.path.abspath(__file__)
    try:
        sys.stdout.flush()
        os.execv(sys.executable, [sys.executable, here] + sys.argv[1:])
    except OSError as e:
        print(T('Starting again did not work: %s') % e)
        print(T('Start it by hand: %s %s') % (sys.executable, here))


#---------------------------------------------------------- Certificates

def use_certificates():
    """Point the libraries that fetch on their own at the bundle.

    They read these two variables and nothing else; without them the
    model download fails on a Python that has no certificates.
    """
    bundle = certificate_file()
    if not bundle:
        print(T('  No certificate bundle found -- an HTTPS download '
                'may fail.'))
        return None
    os.environ.setdefault("SSL_CERT_FILE", bundle)
    os.environ.setdefault("REQUESTS_CA_BUNDLE", bundle)
    return bundle


#---------------------------------------------------------- What is said
# A piece of its own, in the folder "speech" beside this one. Read
# here and not where it is first used, because it binds what it takes
# out of this file: use_certificates above is the last of that.

speech = beside("speech", program=PROGRAM)
take_from(speech)

# What this file itself calls out of the recognition. The rest of what
# it brings answers here too, through take_from above; these are
# written out because they are read in this file, and a name read here
# and bound nowhere here is a loose end.
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

def collect_with_continuations(paths, no_followups, apart=(), together=()):
    """The given files plus their continuations, without duplicates.

    *apart* names blocks that stand on their own, *together* files that
    belong to one recording although their names do not say so -- see
    group_recording_parts.
    """
    apart = FileSet(apart or ())
    joined = ByFile()
    for row in together_chains(together):
        for x in row:
            if x not in apart:
                joined[x] = [y for y in row if y not in apart]
    out, seen, hints = [], set(), []
    for p in paths:
        if os.path.abspath(p) in seen:
            continue
        if p in joined:
            row, discarded = list(joined[p]), []
        elif no_followups or p in apart:
            row, discarded = [p], []
        else:
            row, discarded = find_continuation_files(os.path.abspath(p))
            row = [x for x in row if x not in apart
                   and x not in joined]
        for path in row:
            if os.path.abspath(path) not in seen:
                seen.add(os.path.abspath(path))
                out.append(path)
        hints += discarded
    # Sort by name so the order of selection does not matter: giving only the
    # first block or all three in any order yields the same list. A row
    # forced together by hand is the one thing that keeps its order.
    # --together promises "these files are one recording, in this
    # order", and sorting the row by name would break that promise on
    # every name that is not already alphabetical.
    #
    # The row travels as one block, and the block sorts under the
    # alphabetically smallest name in it. Not under the name given
    # first: the whole point of sorting here is that the order of
    # selection makes no difference, and a block that moved with the
    # order it was typed in would put that difference straight back.
    rank = ByFile()
    for row in together_chains(together):
        row = [x for x in row if x not in apart]
        if not row:
            continue
        smallest = min(os.path.basename(x).lower() for x in row)
        for k, x in enumerate(row):
            rank[x] = (smallest, k)
    out.sort(key=lambda x: rank.get(
        x, (os.path.basename(x).lower(), 0)))
    return out, hints


def build_argument_parser():
    """Define all command line switches."""
    ap = argparse.ArgumentParser(
        prog="videopodcast-magic",
        description="videopodcast-magic %s -- put processed audio into "
                    "video files as the first audio track" % VERSION)
    ap.add_argument("--version", action="version",
                    version="videopodcast-magic %s   %s"
                            % (VERSION, python_note()))
    ap.add_argument("--lang", choices=languages(), default=None,
                    help="language of the messages (default: the system's)")
    ap.add_argument("files", nargs="*",
                    help="audio and video files, told apart by extension. "
                         "Audio only = join and write.")
    ap.add_argument("--out", default=None,
                    help="output folder (default: next to each video)")
    ap.add_argument("--auphonic-api-key", dest="auphonic_key",
                    default=None, metavar="KEY",
                    help="API key from the Auphonic account settings. Turns "
                         "processing on. Without files it only lists the "
                         "presets.")
    ap.add_argument("--auphonic-preset", default=None, metavar="NAME",
                    help="preset name or id (default: asked for)")
    ap.add_argument("--auphonic-wait", dest="auphonic_wait", type=int,
                    default=7200, metavar="SECONDS",
                    help="how long to wait for Auphonic (default: 7200)")
    ap.add_argument("--suffix", default="_audio",
                    help="added to the file name (default: _audio)")
    ap.add_argument("--name-camera", dest="name_camera",
                    default="Camera Original",
                    help="name of the camera track (default: Camera Original)")
    ap.add_argument("--no-camera-audio", dest="no_camera_audio",
                    action="store_true",
                    help="drop the camera's own audio instead of keeping it")
    ap.add_argument("--no-follow-ups", dest="no_follow_ups",
                    action="store_true",
                    help="do not look for numbered continuation files "
                         "(default: they are looked for)")
    ap.add_argument("--apart", action="append", default=[], metavar="FILE",
                    help="this block stands on its own and is not joined "
                         "to a recording, even where its name says it is a "
                         "continuation. May be given several times. The "
                         "interface sets it when a single block is taken "
                         "out of a recording by hand.")
    ap.add_argument("--no-drift", dest="no_drift", action="store_true",
                    help="measure and report clock drift, but do not take "
                         "it out")
    ap.add_argument("--tc", default=None, metavar="HH:MM:SS:FF",
                    help="start timecode of the picture. Used to compare "
                         "against the audio and written into the result. "
                         "Needed where the camera wrote none or a wrong one. "
                         "(default: from the video file)")
    ap.add_argument("--fps", type=float, default=None, metavar="NUMBER",
                    help="frame rate to assume. Decides what a frame is -- "
                         "the frame counts and the threshold above which "
                         "clock drift is taken out. Needed only where "
                         "ffprobe reports a wrong rate. "
                         "(default: from the video file)")
    ap.add_argument("--speech-language", dest="speech_language",
                    default="", metavar="CODE",
                    help="language tag of the audio tracks, three letters "
                         "per ISO 639-2/B -- ger, eng, fra. Careful: ffmpeg "
                         "drops 'deu' silently. Empty means no tag. "
                         "(default: none)")
    ap.add_argument("--speakers-local", dest="speakers_local", default=None,
                    metavar="FILE",
                    help="take exactly that recording apart by voice, "
                         "instead of the one the run would pick itself. A "
                         "run picks a single audio recording, or the "
                         "longest camera track where there is none, and "
                         "takes it apart on its own. What it needs came "
                         "with the program; the run takes minutes. "
                         "(default: whatever the run picks)")
    ap.add_argument("--update", dest="update_now",
                    action="store_true", default=False,
                    help="let pip fetch the newer version, in the Python "
                         "this is running in, and write what pip says "
                         "here. A run only ever says that one is out; "
                         "nothing is fetched without this. (default: off)")
    ap.add_argument("--speakers-from", dest="speakers_from", default=None,
                    metavar="FILE",
                    help="take a finished separation out of a project or "
                         "assignment file instead of computing one. "
                         "(default: none)")
    ap.add_argument("--speakers-count", dest="speakers_count", type=int,
                    default=0, metavar="NUMBER",
                    help="how many people --speakers-local should find. A "
                         "given number improves the recognition and "
                         "quadruples the picture time on the wrong person, "
                         "so it is set only where it is known. "
                         "(default: work it out)")
    ap.add_argument("--no-speakers-local", dest="no_speakers_local",
                    action="store_true",
                    help="never take a recording apart by voice in this "
                         "run, whatever else says so. (default: off)")
    ap.add_argument("--no-speech-recognition", dest="no_speech_recognition",
                    action="store_true",
                    help="do not write down what is said. The cut then has "
                         "no sentence boundaries and the wide shot goes to "
                         "the longest pause nearby. (default: off)")
    ap.add_argument("--no-transcript-file", dest="no_transcript_file",
                    action="store_true",
                    help="write no transcript beside the result. Normally "
                         "the words that were heard go into the output "
                         "folder as json, srt and txt. (default: off)")
    ap.add_argument("--auphonic-resume", dest="auphonic_resume", default=None,
                    choices=("result", "rerun", "adopt", "upload", "abort"),
                    help="what to do when the production is already there: "
                         "result = take the existing one, rerun = compute "
                         "again with the chosen preset without a new upload "
                         "(costs nothing), adopt = the same, but take the "
                         "track names there as speaker names, upload = "
                         "everything again, abort = stop. Without this it "
                         "asks. (default: ask)")
    ap.add_argument("--auphonic-done", dest="auphonic_done", default=None,
                    metavar="FOLDER",
                    help="folder holding tracks Auphonic has already "
                         "processed (files named after the speakers). Then "
                         "nothing is uploaded and no credit is spent -- for "
                         "a second run on the same audio. (default: none)")
    ap.add_argument("--min-edit-duration", dest="min_edit_duration", type=float,
                    default=MIN_EDIT_DURATION_S, metavar="SECONDS",
                    help="shortest a shot may stand. Anything shorter is "
                         "merged into the one that follows; 0 turns it "
                         "off. Three "
                         "seconds is what interview cutting practice asks "
                         "for -- a camera that changes faster than the "
                         "viewer can settle on a face reads as nervous. "
                         "SmartSwitch calls the same thing 1.00, which is "
                         "why this used to be 1.2. (default: 3)")
    ap.add_argument("--min-speech-to-switch", dest="min_speech_to_switch",
                    type=float, default=MIN_SPEECH_TO_SWITCH_S,
                    metavar="SECONDS",
                    help="how long somebody has to hold the floor before "
                         "the camera follows them. Below it the picture "
                         "stays where it is: a short \"yes\" is not a "
                         "change of speaker, and without this the minimum "
                         "edit duration then holds the wrong person on "
                         "screen for seconds. 0 turns it off. (default: "
                         "1.5)")
    ap.add_argument("--silence-hold", dest="silence_hold", type=float,
                    default=SILENCE_HOLD_S, metavar="SECONDS",
                    help="how long a silence may be and still count as a "
                         "breath rather than an end. Only where "
                         "--on-silence hold-brief asks for it: up to here "
                         "the picture stays, beyond it the wide shot "
                         "comes. (default: 1.0)")
    ap.add_argument("--edit-change-delay", dest="delay", type=float,
                    default=0.3, metavar="SECONDS",
                    help="how much later than the audio the picture cuts. "
                         "Negative lets the picture lead. (default: 0.3)")
    ap.add_argument("--reaction-lead", dest="reaction_lead", type=float,
                    default=1.5, metavar="SECONDS",
                    help="how much earlier the picture goes to the answer "
                         "after a question. Only where --on-question asks "
                         "for it. (default: 1.5)")
    ap.add_argument("--reaction-gap", dest="reaction_gap", type=float,
                    default=3.0, metavar="SECONDS",
                    help="how soon the answer has to follow the question "
                         "for the reaction cut to fire. (default: 3)")
    ap.add_argument("--reaction-hold", dest="reaction_hold", type=float,
                    default=0.7, metavar="SHARE",
                    help="how much of the ten seconds after the question "
                         "the answering speaker has to hold, as a share "
                         "between 0 and 1. (default: 0.7)")
    for switch, _caption, default_value, values, _short, _long in CUT_CHOICES:
        ap.add_argument("--" + switch, dest=switch.replace("-", "_"),
                        choices=list(values), default=default_value,
                        help="what is shown where the speech does not say "
                             "it: %s. (default: %s)"
                             % (", ".join(values), default_value))
    ap.add_argument("--wide-after", dest="wide_after", type=float,
                    default=WIDE_AFTER_S, metavar="SECONDS",
                    help="from this hold time on, a shot is broken up by "
                         "leaving the speaker for a while -- placed on a "
                         "sentence boundary nearby, not by the clock. "
                         "0 turns it off. (default: 70)")
    ap.add_argument("--wide-length", dest="wide_length", type=float,
                    default=5.0, metavar="SECONDS",
                    help="how long such an interposed shot stands at "
                         "least; it then runs to the end of the sentence. "
                         "(default: 5)")
    ap.add_argument("--wide-most", dest="wide_most", type=float,
                    default=15.0, metavar="SECONDS",
                    help="how long it stands at most. Where the end of the "
                         "sentence lies beyond it, the last clause break "
                         "before it ends the shot. (default: 15)")
    ap.add_argument("--wide-latest", dest="wide_latest", type=float,
                    default=120.0, metavar="SECONDS",
                    help="upper limit: longest one camera may stand without "
                         "a cut. Where no good pause turns up, it cuts "
                         "anyway. (default: 120)")
    ap.add_argument("--no-wide-edges", dest="no_wide_edges",
                    action="store_true",
                    help="do NOT hold the wide shot at the beginning and the "
                         "end. By default the picture stays wide while the "
                         "greeting and the goodbye are spoken.")
    ap.add_argument("--parallel", type=int, default=0, metavar="COUNT",
                    help="process this many video files at once. 0 = decide "
                         "for me, 1 = one after another. (default: 0)")
    ap.add_argument("--no-metrics", dest="no_metrics", action="store_true",
                    help="measure no metrics at the end and compare no "
                         "camera colours. Saves a few minutes on long "
                         "recordings.")
    ap.add_argument("--intro", default=None, metavar="FILE",
                    help="video file laid over the beginning. It sits on the "
                         "second picture and audio track, so its sound "
                         "carries on under the first words. It is neither "
                         "aligned nor processed. (default: none)")
    ap.add_argument("--outro", default=None, metavar="FILE",
                    help="the same for the end: it starts where the last "
                         "word ends. (default: none)")
    ap.add_argument("--wide-shot", dest="wide_shot", action="append",
                    default=None, metavar="FILE",
                    help="this video file is a wide shot: a camera nobody "
                         "sits in front of. It is filmed, aligned and cut "
                         "to like any other, it just takes no speaker. May "
                         "be given several times. Without it the cameras "
                         "no speaker is assigned to are the wide shots. "
                         "(default: none, so derived)")
    ap.add_argument("--no-single-tracks", dest="no_single_tracks",
                    action="store_true",
                    help="put only the mix into the video, not the single "
                         "recordings beside it. Without Multitrack several "
                         "recordings running at the same time are mixed "
                         "into one track; by default each also goes in on "
                         "its own, unprocessed, so the edit can reach for "
                         "one voice. That costs about 520 MB per track and "
                         "hour.")
    ap.add_argument("--together", action="append", nargs="+",
                    default=[], metavar="FILE",
                    help="these files are one recording, in this order. The "
                         "counterpart to --apart, for blocks the search "
                         "cannot recognise as belonging together -- a "
                         "recorder whose file names carry neither a counter "
                         "nor a clock. Repeatable for several recordings.")
    ap.add_argument("--no-preflight", dest="no_preflight",
                    action="store_true",
                    help="skip the preflight report. By default the material "
                         "is checked before the first long step starts.")
    ap.add_argument("--preflight-again", dest="preflight_again",
                    action="store_true",
                    help="measure the preflight again instead of taking the "
                         "stored measurement. Not needed: a changed file is "
                         "measured again anyway.")
    ap.add_argument("--anyway", action="store_true",
                    help="run even where the preflight found a reason to "
                         "stop.")
    ap.add_argument("--lufs", type=float, default=None,
                    help="loudness the sum of all speaker tracks is brought "
                         "to. The same gain goes on every track, so their "
                         "balance is kept. Usual values: %s. Without it "
                         "nothing is adjusted: the sound is taken from the "
                         "source files as it is, and auphonic.com goes on "
                         "doing what its preset says. (default: none)"
                    % ", ".join("%.0f = %s" % (lufs, what)
                                for lufs, what in PLATFORMS.values()))
    ap.add_argument("--assign", default=None, metavar="FILE",
                    help="JSON file holding which audio track belongs to "
                         "which camera. The interface writes it; this is how "
                         "the assignment reaches a run without it. "
                         "(default: none)")
    ap.add_argument("--without-auphonic", dest="without_auphonic",
                    action="store_true",
                    help="run without auphonic.com: align, mix and write "
                         "locally. The camera cut then comes from a speech "
                         "detection of our own. No de-bleed, no leveler, no "
                         "noise removal.")
    ap.add_argument("--multitrack", action="store_true",
                    help="send every audio file to Auphonic as its own "
                         "track, so the bleed between the microphones can be "
                         "removed. Needs two input tracks -- a recording "
                         "of its own, a channel of a multichannel "
                         "recorder, or the audio of a camera -- and a "
                         "multitrack preset. Which audio belongs to which "
                         "camera comes from --assign; the interface writes "
                         "that file.")
    ap.add_argument("--speech-language-camera", dest="speech_language_camera",
                    default="", metavar="CODE",
                    help="the same for the camera track. Empty means no tag "
                         "-- that is what makes the QuickTime player tell "
                         "the two entries in its audio menu apart at all "
                         "(default: empty)")
    ap.add_argument("--in-point", dest="in_point", default=None, metavar="TIME",
                    help="start of the time window. A timecode like 17:20:14 "
                         "or 17:20:14:00 is absolute, +12:30 or 90 counts "
                         "from the start of the measured window. "
                         "(default: from the video files)")
    ap.add_argument("--out-point", dest="out_point", default=None, metavar="TIME",
                    help="end of the time window, same notation. A negative "
                         "value like -30 counts back from the end. "
                         "(default: from the video files)")
    ap.add_argument("--resolve", action="store_true",
                    help="afterwards create the project in DaVinci Resolve, "
                         "import the finished files and build the timelines. "
                         "Resolve has to be running. (default: off)")
    ap.add_argument("--hdr-check", dest="hdr_check", default=None,
                    metavar="FILE",
                    help="only look: does this finished file carry "
                         "everything that marks it as HDR? Checks primaries, "
                         "curve, matrix, bit depth, codec profile and the "
                         "static metadata. Changes nothing.")
    ap.add_argument("--resolve-json", dest="resolve_json", default=None,
                    metavar="FILE",
                    help="run only the Resolve part, from a "
                         "Production_resolve.json that is already there. "
                         "Then nothing is measured and nothing written.")
    ap.add_argument("--resolve-audio-tracks", dest="resolve_audio_tracks",
                    action="store_true",
                    help="only look: for the project open in Resolve, print "
                         "the audio channel mapping of every clip and the "
                         "tracks of every timeline. Changes nothing.")
    ap.add_argument("--resolve-project", dest="resolve_project", default=None,
                    choices=("update", "keep", "new", "abort"),
                    help="what to do when the Resolve project is already "
                         "there: update = delete both timelines and build "
                         "them again, keep = put the new ones beside them, "
                         "new = a second project alongside, abort = stop. "
                         "Without this it asks.")
    ap.add_argument("--dry-run", action="store_true",
                    help="only measure and report, write nothing")
    # A switch that needs several recordings says so, or it would be
    # taken and do nothing. Marked here rather than at the call site:
    # --help builds its own parser and never reached the old place, so
    # the mark was set and shown to nobody.
    for entry in ap._actions:
        if entry.dest in ONLY_MULTITRACK:
            entry.help = (entry.help or "") + "  [multitrack only]"
    return ap

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
    # The language before the first sentence is made, not before the
    # first one is printed: the complaint about ffmpeg below is written
    # down here and shown much later. Only where one was typed, or the
    # system's language and the one kept from an earlier run are lost.
    if args.lang:
        set_language(args.lang)
    # --update wants no files and no tools, so it is answered before
    # either is looked for -- a broken installation is one of the
    # reasons to reach for it. It is the only way the command line
    # fetches anything.
    if args.update_now:
        return update_from_command_line()
    # Everything this program does goes through ffmpeg, so below the
    # floor there is nothing to start. Behind only_reading() and
    # --update on purpose: --update is the way out of a broken
    # installation and must not fail on the thing it repairs.
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
        # Qt before the console goes into the log file. It is a hundred
        # megabyte download on a machine that has none, and behind the
        # redirect the terminal would stand silent for minutes and then
        # exit without a word.
        _require_module("PySide6.QtWidgets", "PySide6")
        # Nothing is said here: this path ends in a window, and the
        # program is not started from a console. Where the log is
        # stands in the Help menu instead.
        redirect_console()
        mark_time("the log is open")
    # A place in the program list, laid once and never again. Below the
    # branch on purpose: redirect_console() renames the running log to
    # the backup, so a line written before it lands in the log of the
    # run before, where the Help menu never looks.
    beside("desktop", program=PROGRAM).lay_on_first_start()
    mark_time("the place in the program list is settled")
    if to_the_window:
        return window().gui()
    force_utf8_output()
    enable_colour_output()
    # Whoever typed a command line has a console, so it is said there --
    # after the language is settled, and before the banner claims a run
    # is starting.
    if TOOL_TROUBLE[0] and not tools_repaired(*TOOL_TROUBLE):
        return 1
    print("videopodcast-magic %s   %s\n%s\n"
          % (VERSION, python_note(), running_from()))
    # Said, not asked. A run started from a script must not stop for a
    # question, and this is not a fault -- only a coarser correction.
    # Where nothing could be done about it, nothing is said either.
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
        # Cameras only: their own audio becomes the track. How many
        # tracks that is has to be measured, not counted -- one camera
        # with two clip-on microphones is two of them. So the plan is
        # built first and the decision falls behind it; a camera with
        # one microphone drops into the ordinary path there.
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
    # One way in, whatever --multitrack says. The switch decides how the
    # recordings are grouped, and nothing else -- not which time axis is
    # built, not which arithmetic places the window, not which code
    # writes the files. One axis for one job.
    return multitrack_or_single(args, ap, audio_paths, video_paths)


#------------------------------------------------ Beside the window
# Named here rather than inside the interface section: none of them
# touches a widget, and other sections reach in for them.


def stand_in_camera(names):
    """What stands in front of a silence where no camera is a wide shot.

    Not a wide shot, and it must not act as one: everything the wide
    shot settings ask for is switched off wherever this is used.

    All that matters here is that the preview and the run reach for the
    same camera -- and they did not. The preview took the first of its
    own list, the run took the reference clip, and in a real shoot both
    are real cameras, so it showed as two different cuts rather than as
    a fault. Found 25.8.2026, and only reachable at all since a camera
    with a speaker stopped counting as a wide shot.

    By name, not by position: the two lists are built in different
    places and nothing says they are sorted alike, so a rule that hangs
    on the order would let them drift again on the day one of them is
    built differently.
    """
    return sorted(n for n in names if n)[:1] or ["Wide"]


def common_window(camera_areas):
    """The stretch every camera saw, and the two that decide it.

    *camera_areas* is (from, to, name) per camera, in reference camera
    time. Returns (t0, begins_with, t1, ends_with).

    Every camera, not any camera. A window wider than a camera reaches
    has a stretch where a cut to that camera finds no picture, and the
    episode then comes out shorter than the window said it would.
    Measured on 26.8.2026 over the test interview: the beginning lay
    12.567 s before one of three cameras began, and on the fixture the
    window even began at -0.180 s -- before its own zero. Whoever wants
    that stretch anyway sets an In point of their own; what is derived
    is a window every camera can fill. Decided on 29.8.2026.

    Sitting out here rather than inside the run because it is
    arithmetic and nothing else, and arithmetic can be held against
    numbers without building a window and an hour of sound first.
    """
    t0, begins_with = max((x, name) for x, _y, name in camera_areas)
    t1, ends_with = min((y, name) for _x, y, name in camera_areas)
    return t0, begins_with, t1, ends_with


def finished_tracks_find(base):
    """Report whether processed tracks from Auphonic are already there.

    After a run the output folder holds a subfolder with the single tracks.
    Choosing the same folder again usually means reassembling rather than
    uploading again, so it is offered.
    """
    if not base or not os.path.isdir(base):
        return None
    for name in ("auphonic-tracks",):
        p = os.path.join(base, name)
        if os.path.isdir(p) and any(
                os.path.splitext(f)[1].lower() in AUDIO_SUFFIXES
                for f in os.listdir(p)):
            return p
    return None


MARK_DE = "**Deutsch**"


# What separates the two halves of a release text. Each version says
# everything twice: the English part first, the German part under this
# line. Two strings in one place -- the changelog writes them, the
# window looks for them, and the release test insists on them.
MARK_EN = "**English**"


def release_text_in(text, language=None):
    """Keep the half of a release text that is in this language.

    From 2.20.0-beta on a release says everything twice, in two blocks
    one under the other: English first, German under a line of its own.
    Both belong on the release page, where anybody may read and jump to
    the language they want. In the window only one is wanted -- two
    languages in a box are twice as long and half as readable.

    Given away only where the mark is really there. A text from before
    this, or one where the mark was forgotten, comes back whole: half a
    text is worse than one in the wrong language.
    """
    lines = str(text or "").split("\n")
    at = [i for i, x in enumerate(lines) if x.strip() == MARK_DE]
    if not at:
        return text
    if (language or LANG) == "de":
        kept = lines[at[0] + 1:]
    else:
        kept = lines[:at[0]]
        # The rule that draws the line between them goes with it.
        while kept and kept[-1].strip() in ("", "---", "***", "___"):
            kept.pop()
    return "\n".join(x for x in kept
                      if x.strip() not in (MARK_EN, MARK_DE)).strip()


class Stopped(Exception):
    """The run was broken off from the window."""


# What is running right now, so that breaking off can end it. A flag on
# its own would not do: the run spends most of its minutes waiting for
# ffmpeg, and a child nobody tells goes on writing long after the window
# says it has stopped.
RUN_STOP = {"wanted": False, "children": set(), "at": ""}


def stop_wanted():
    """Whether somebody has asked for the run to stop."""
    return bool(RUN_STOP["wanted"])


#---------------------------------------------------------- The material
# A piece of its own, in the folder "material" beside this one. Read
# after stop_wanted, which it binds, and before the checking, which
# binds the camera margin, the clipping and parallel_map out of it.

material = beside("material", program=PROGRAM)
take_from(material)

# What this file itself calls out of the material. The rest of what it
# brings answers here too, through take_from above; these are written
# out because they are read in this file, and a name read here and
# bound nowhere here is a loose end.
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
# A piece of its own, in the folder "bearings" beside this one. Read
# after the material, whose names it binds, and before the checking;
# the window's colours and the writing of the cut list it reads late.

bearings = beside("bearings", program=PROGRAM)
take_from(bearings)

# What this file itself calls out of the bearings. The rest of what
# it brings answers here too, through take_from above; these are
# written out because they are read in this file, and a name read
# here and bound nowhere here is a loose end.
check_mode_fits_input = bearings.check_mode_fits_input
guess_speaker_name = bearings.guess_speaker_name
split_audio_and_video = bearings.split_audio_and_video
together_chains = bearings.together_chains


#--------------------------------------------------------- The preflight
# A piece of its own, in the folder "preflight" beside this one. Read
# after Stopped, RUN_STOP and stop_wanted, which it binds, and before
# the separation, which binds run_ffmpeg_with_progress out of it.

preflight = beside("preflight", program=PROGRAM)
take_from(preflight)

# What this file itself calls out of the checking. The rest of what it
# brings answers here too, through take_from above; these are written
# out because they are read in this file, and a name read here and
# bound nowhere here is a loose end.
PLATFORMS = preflight.PLATFORMS
check_preset = preflight.check_preset
clean_preflight_cache = preflight.clean_preflight_cache
lufs_does_nothing = preflight.lufs_does_nothing
report_findings = preflight.report_findings
run_ffmpeg_with_progress = preflight.run_ffmpeg_with_progress
run_preflight = preflight.run_preflight


#---------------------------------------------------------- The processing
# A piece of its own, in the folder "auphonic" beside this one. Read
# after the checking, because choose_preset asks it whether the preset
# fits; the checking reaches back for read_preset, through PROGRAM.

auphonic = beside("auphonic", program=PROGRAM)
take_from(auphonic)

# What this file itself calls out of the processing. The rest of what it
# brings answers here too, through take_from above; these are written
# out because they are read in this file, and a name read here and
# bound nowhere here is a loose end.
api_key_from_anywhere = auphonic.api_key_from_anywhere
print_presets = auphonic.print_presets
tracks_folder = auphonic.tracks_folder


#-------------------------------------------------------- The separation
# A piece of its own, in the folder "speakers" beside this one. Read
# here and not where it is first used, because the cut and the window
# bind names out of it: this line stands before the two that read them.

# Measured once and kept: importing pyannote takes seconds, and the
# question is asked wherever a separation might be wanted. forget_
# speaker_split() throws it away, because after an install the answer
# from before it is about an installation that is gone.

# The two stay here because the separation rebinds them as it runs.
# A copy in the piece would go stale under a name bent from outside,
# so it reads and writes them through the program.
_SPEAKER_READY = None
_SPEAKER_WHY = ""

speakers = beside("speakers", program=PROGRAM)
take_from(speakers)

# Nothing in this file calls into the separation, so nothing is
# written out here: what the piece brings answers under this program
# through take_from above, and that is what the cut and the window
# bind out of it.


#---------------------------------------------------------- The project
# A piece of its own, in the folder "resolve" beside this one. Read
# here and not where it is first used, because it binds what it takes
# out of this file: Finding, which the preflight above brings in.

resolve = beside("resolve", program=PROGRAM)
take_from(resolve)

# What this file itself calls out of the project building. The rest of
# what it brings answers here too, through take_from above; these are
# written out because they are read in this file, and a name read here
# and bound nowhere here is a loose end.
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
# A piece of its own, in the folder "cut" beside this one. Read here
# and not where it is first used, because the window binds names out
# of it: this line has to stand before the one that reads the window.

cut = beside("cut", program=PROGRAM)
take_from(cut)

# What this file itself calls out of the cutting. The rest of what it
# brings answers here too, through take_from above; these are written
# out because they are read in this file, and a name read here and
# bound nowhere here is a loose end.
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
# A piece of its own, in the folder "pipeline" beside this one. Read
# after the cut, whose names it uses, and before the window, which
# binds unpack_kind out of it.

pipeline = beside("pipeline", program=PROGRAM)
take_from(pipeline)

# What this file itself calls out of the chain. The rest of what it
# brings answers here too, through take_from above; these are written
# out because they are read in this file, and a name read here and
# bound nowhere here is a loose end.
extract_audio_from_video = pipeline.extract_audio_from_video
multitrack_or_single = pipeline.multitrack_or_single


#-------------------------------------------------------- The interface
# A piece of its own, in the folder "ui" beside this one. It is read on
# the way to the window and not here: a run on the command line opens
# none and then never reads it.


def window():
    """The window, read out of the folder the first time it is wanted."""
    global ui
    ui = beside("ui", program=PROGRAM)
    take_from(ui)
    # A name bent on this program before the window was read. The
    # window binds its own under the same name and would stand on that
    # one, so the bend is carried in -- which a piece read on the way
    # through gets from pieces_answer_together() for nothing.
    for name, what in list(vars(ui).items()):
        if not name.startswith("__") and globals().get(name, what) is not what:
            setattr(ui, name, globals()[name])
    return ui


def __getattr__(name):
    """A name of the window, asked for before the window was read.

    What the window brings stands here once it has been read, and
    until then this answers by reading it. So this file hands out the
    same names as it did when it read the window on its way through.
    """
    if name.startswith("__"):
        raise AttributeError(name)
    piece = window()
    return piece if name == "ui" else getattr(piece, name)


pieces_answer_together()


# ---------------------------------------------------------------------------
# Catalogue
# ---------------------------------------------------------------------------
# Every message of this program in the other languages stands in a file
# of its own beside this one. How to add a language: see the top.

CATALOGUE["de"] = texts_of_language("de")
# German is complete; the seven after it are partial, and every text
# they leave out appears in English. Arabic is translated and stands
# beside them, but is not offered: the window never sets a reading
# direction, so it would come out left to right.
CATALOGUE["es"] = texts_of_language("es")
CATALOGUE["pt"] = texts_of_language("pt")
CATALOGUE["fr"] = texts_of_language("fr")
CATALOGUE["ru"] = texts_of_language("ru")
CATALOGUE["zh"] = texts_of_language("zh")
CATALOGUE["ja"] = texts_of_language("ja")
CATALOGUE["hi"] = texts_of_language("hi")

# Where the window's language comes from: what somebody chose in an
# earlier run, and the system where nobody has chosen yet. --lang beats
# both, and main() applies it once the command line has been read.
LANG = set_language(kept_language() or system_locale())


if __name__ == "__main__":
    sys.exit(main())
