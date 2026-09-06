# -*- coding: utf-8 -*-
"""How a run shows itself: its colours, its marks and the room it takes.

One palette for the window, the log pane and the terminal, the marks
that say what kind a line is, the writer that turns them into colour
on a console, and what room a name or a table may take.

A piece of the program, read out of the folder beside it by beside().
The program is handed in, and every name used out of it bound below.
"""

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

# What the program has and this piece uses. All three are imports and
# stand far above the seam, so each is a copy of what was there and
# none is read late.

os = PROGRAM.os
re = PROGRAM.re
sys = PROGRAM.sys

# __file__ is not among them, and it is counted rather than looked
# for: no line below reads it, so there is nothing here that would
# quietly answer with this folder instead of the program's own.


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
