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
as_written = language.as_written
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
    kept = PROGRAM.settings().get("language")
    return kept if isinstance(kept, str) and kept in languages() else ""


def group_text(number):
    """Group the thousands the way the chosen language does."""
    return format(int(number), ",d").replace(",", T(","))


def decimal_text(text):
    """Write the decimal point the way the chosen language writes it."""
    mark = T(".")
    return text.replace(".", mark) if mark != "." else text


def number_text(number, places=1, plus=False):
    """Group the thousands and set the decimal mark, as the language does.

    The two above do one half each; a number with a decimal place needs
    both -- German printed "2000,0 ms" beside "1.234 points". Not in two
    passes over the finished text: one language's thousands mark is
    another's decimal mark, and measured on German the second pass reads
    what the first wrote, "1,234,5" one way round and "1.234.5" the
    other. So the halves are marked apart. *plus* signs a positive one.
    """
    # French and Russian group with a space, so nothing here may look
    # for a particular character: the cut is made at the point "%f"
    # wrote, while both halves are still plain digits.
    text = "%.*f" % (max(0, int(places)), float(number))
    ahead = "-" if text.startswith("-") else ("+" if plus else "")
    # "inf" and "nan" carry no digits to group, and int() stops the run
    # over them. A fit with no spread of its own reports its error as
    # inf, so this is reachable; decimal_text handed the word on.
    if not text.lstrip("-")[:1].isdigit():
        return ahead + text.lstrip("-")
    whole, _, rest = text.lstrip("-").partition(".")
    whole = format(int(whole), ",d").replace(",", T(","))
    return ahead + whole + (T(".") + rest if rest else "")


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

# A piece of its own, in the folder "choices" beside this one. Read
# where its lines stood: it takes T alone, bound at the head of this
# file, and ten pieces below bind seventeen of its names at their
# heads, material the first of them.
choices = beside("choices", program=PROGRAM)
take_from(choices)


# A piece of its own, in the folder "livery" beside this one. Read
# where its lines stood: it takes only os, re and sys, all three
# imports at the top of this file, and fourteen pieces below bind
# fifteen of its names at their heads, metadata the first of them.
livery = beside("livery", program=PROGRAM)
take_from(livery)

# What this file itself calls out of it. The rest of what it brings
# answers here too, through take_from above; these three are written
# out because they are read below, and a name read here and bound
# nowhere here is a loose end.
as_warn = livery.as_warn
enable_colour_output = livery.enable_colour_output
force_utf8_output = livery.force_utf8_output


# A piece of its own, in the folder "dials" beside this one. Read
# where its lines stood: it reads no name out of the program, and six
# pieces below bind twenty-six of its names at their heads.
dials = beside("dials", program=PROGRAM)
take_from(dials)

# What this file itself calls out of it. The rest of what it brings
# answers here too, through take_from above; these three are written
# out because they are read below, and a name read here and bound
# nowhere here is a loose end.
CUT_CHOICES = dials.CUT_CHOICES
MIN_EDIT_DURATION_S = dials.MIN_EDIT_DURATION_S
SILENCE_HOLD_S = dials.SILENCE_HOLD_S


def shell_quote(cmd):
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode("utf-8", "replace")[-2000:])
    return p


# A piece of its own, in the folder "filing" beside this one. Read
# where its lines stood: ten pieces below bind twenty of its names at
# their heads, and no line above it reads one.
filing = beside("filing", program=PROGRAM)
take_from(filing)

# What this file itself calls out of it: the two containers. path_key
# is not among them -- it is read inside the piece and nowhere here.
ByFile = filing.ByFile
FileSet = filing.FileSet


# A piece of its own, in the folder "stowage" beside this one. Read
# where its lines stood: kept_language far above reaches back for
# settings through PROGRAM, cache_folder is read 348 lines below, and
# logbook, the next piece read, binds cache_folder at its head.

stowage = beside("stowage", program=PROGRAM)
take_from(stowage)

# What this file itself calls out of it. The rest of what it brings
# answers here too, through take_from above; this one is written out
# because it is read below, and a name read here and bound nowhere
# here is a loose end.
cache_folder = stowage.cache_folder


# A piece of its own, in the folder "logbook" beside this one. Read
# where its lines stood: cache_folder, the last of the four names it
# takes, stands eight lines above, and soundings sixteen below binds
# outside_say at its head, as do desktop, hearing, herald and ui.

logbook = beside("logbook", program=PROGRAM)
take_from(logbook)

# What this file itself calls out of it. The rest of what it brings
# answers here too, through take_from above; these two are written out
# because they are read below, and a name read here and bound nowhere
# here is a loose end.
installed_by_a_package_manager = logbook.installed_by_a_package_manager
mark_time = logbook.mark_time


# A piece of its own, in the folder "soundings" beside this one. Read
# where its lines stood: outside_say, the last of the eight it takes,
# stands right above, and timecode, six lines below, binds ffprobe_json
# at its head -- eleven pieces bind three of these names at theirs.

soundings = beside("soundings", program=PROGRAM)
take_from(soundings)

# What this file itself calls out of it. The rest of what it brings
# answers here too, through take_from above; these two are written out
# because they are read below, and a name read here and bound nowhere
# here is a loose end.
clean_probe_cache = soundings.clean_probe_cache
ffprobe_json = soundings.ffprobe_json


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


#---------------------------------------------------------- Time and timecode
# A piece of its own, in the folder "timecode" beside this one. Read
# above every piece below it: twelve of them bind sixteen of its names
# at their heads, and metadata, the next one read, binds seven.

timecode = beside("timecode", program=PROGRAM)
take_from(timecode)


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
# A piece of its own, in the folder "metadata" beside this one. Read
# where its lines stood: fifteen of its names are bound at the head of
# six pieces read below, and every one of those six finds them here.

metadata = beside("metadata", program=PROGRAM)
take_from(metadata)


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


#---------------------------------------------------------- The herald
# A piece of its own, in the folder "herald" beside this one. Read
# where its lines stood, before the material: that binds the progress
# line and the progress reading at its own head, further down.

# The run says which stage it is in, and how far that stage is. The
# interface draws one bar out of it; on the command line nothing is
# connected and the calls cost a comparison. It stays in this file
# because the window sets it on the program, which reaches no piece.
PROGRESS_SINK = None

herald = beside("herald", program=PROGRAM)
take_from(herald)

# What this file itself calls out of the herald. The rest of what it
# brings answers here too, through take_from above; these are written
# out because they are read in this file, and a name read here and
# bound nowhere here is a loose end.
redirect_console = herald.redirect_console
running_from = herald.running_from
watch_outside_calls = herald.watch_outside_calls
write_through = herald.write_through


#--------------------------------------------------------- The hearing
# A piece of its own, in the folder "hearing" beside this one. Read
# after the herald, whose progress line it binds at its own head, and
# before the material, which binds twelve of its names at that one.

hearing = beside("hearing", program=PROGRAM)
take_from(hearing)

# What this file itself calls out of the hearing. The rest of what it
# brings answers here too, through take_from above; this one is
# written out because it is read in this file, and a name read here
# and bound nowhere here is a loose end.
clean_envelope_cache = hearing.clean_envelope_cache


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
# German is complete; the nine after it are partial, and every text
# they leave out appears in English. Arabic reads from right to left,
# and the window turns itself round for it.
CATALOGUE["es"] = texts_of_language("es")
CATALOGUE["pt"] = texts_of_language("pt")
CATALOGUE["fr"] = texts_of_language("fr")
CATALOGUE["ru"] = texts_of_language("ru")
CATALOGUE["uk"] = texts_of_language("uk")
CATALOGUE["zh"] = texts_of_language("zh")
CATALOGUE["ja"] = texts_of_language("ja")
CATALOGUE["hi"] = texts_of_language("hi")
CATALOGUE["ar"] = texts_of_language("ar")

# Where the window's language comes from: what somebody chose in an
# earlier run, and the system where nobody has chosen yet. --lang beats
# both, and main() applies it once the command line has been read.
LANG = set_language(kept_language() or system_locale())


if __name__ == "__main__":
    sys.exit(main())
