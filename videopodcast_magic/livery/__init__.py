# -*- coding: utf-8 -*-
"""How a run shows itself: its colours, its marks and the room it takes.

One palette for the window, the log pane and the terminal, the marks
that name the kind of a line, the writer that turns them into colour,
and what room a name or a table may take. The program is handed in.
"""

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# Bound above the seam, so each is a copy and none is read late.
os = PROGRAM.os
re = PROGRAM.re
sys = PROGRAM.sys

# __file__ is not among them: no line below reads it, so nothing here
# can quietly answer with this folder instead of the program's own.

# Parallel runs keep output apart; text is flushed when its file is done.
THREAD_SHARE = {}    # thread id -> progress fraction of that file
THREAD_BUFFER = {}   # thread id -> list of text chunks

# How much room a file name gets on a button or in a chooser: wide
# enough for a recorder's usual name, narrow enough for the player.
NAME_ROOM = 260
# What the row under the assignment table may take before the player
# is pushed off: past this the sheet needs more than a 13 inch screen.
ROW_ROOM = 380
# How many rows of the speaker table are shown before it scrolls.
# Rows, not speakers: one per speaker plus one for Silence, and the
# column header on top. Without a lid the table grows past the sheet.
SPEAKER_ROWS_SHOWN = 4

# One palette for GUI, log pane and terminal, so a run looks the same.
COLOURS = {
    "heading":   "#1f4e79",       # section heading
    "backdrop": "#e8eff7",      # the strip behind a heading
    "good":     "#2e7d4f",       # done
    # Dark enough for the 4.5 contrast floor on every surface, ours and
    # the three desktops'. A lighter orange falls through on theirs.
    "warning": "#985508",       # warning, run continues
    "error":  "#b02020",       # aborted
    "value":    "#2f5d8a",       # numbers and results
    # Dark enough for the 4.5 floor on the footer, lighter than ours.
    "quiet":   "#646e7b",       # secondary
    "text":    "#222222",
    # Surfaces -- GUI only
    "frame":  "#cfd8e3",
    "box":  "#fbfcfe",
    "head":    "#eef2f7",
    "sheet":   "#ffffff",
    "stripe":  "#dce6f2",
    # A switched-off button keeps its own colour, only muted: flat grey
    # reads as a different kind of thing, and a pair then looks as if
    # only one were off. It still clears the contrast floor.
    "off":     "#c6d6e6",       # disabled button: the fill, muted
    "off_text": "#3a5c80",      # disabled button: what stands on it
}

# Same roles for a dark desktop: same hues, lighter and less saturated.
# Saturated colour glares on dark, and a dark blue would be unreadable.
COLOURS_DARK = {
    "heading":   "#7fb4e6",
    "backdrop": "#233040",
    "good":     "#5cc98a",
    # Its own value: the light orange disappears against a dark sheet.
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

# The light set kept aside: COLOURS is the one dictionary everything
# reads, and overwriting it in place would burn the way back.
COLOURS_LIGHT = dict(COLOURS)


def desktop_is_dark(QtWidgets, QtGui):
    """Report whether the desktop uses a dark colour scheme.

    Falls back to window background lightness where Qt has no scheme.
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

    The kind is stated where the line is written, not read out of its
    wording, which would tie it to one language.
    """
    if line[:1] == MARK:
        return MARK_KINDS.get(line[1:2], "text"), line[2:]
    return "text", line


def strip_marks(text):
    """Take every kind marker back out of a text."""
    return re.sub(MARK + ".?", "", text) if MARK in text else text


class ColourWriter(object):
    """Colour terminal output without altering the text itself.

    Colour is set at the start of a line and held to its end, so a bar
    rewriting its line stays intact. The kind marker comes off here.
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
                        # The marker sat before a line break; it
                        # belongs to the next line.
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

    A Windows legacy code page aborts the run on one umlaut.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def enable_colour_output():
    """Put the output filter in place and colour it where that lands.

    The filter always runs -- it also strips the invisible kind markers.
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
