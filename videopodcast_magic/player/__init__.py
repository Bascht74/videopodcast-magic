# -*- coding: utf-8 -*-
"""The moving picture: the player, the cut band and the log view.

A piece of the program, read out of the folder beside the way in by
beside(). It cannot import the file it was cut out of, because that
file is still being read while this one is; the program is handed in
instead, and every name this piece uses out of it is bound below, by
name. Nothing here reads back into the window: what the window still
calls out of this piece it binds there, by name, in its turn.
"""

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

# What the program has and this piece uses, bound once so that the
# player reads as it did in the window. Not one of them is a name the
# program binds again while it runs -- such a name is read through
# PROGRAM. where it is used, and there is none of that sort in here.
AUDIO_SUFFIXES = PROGRAM.AUDIO_SUFFIXES
COLOURS = PROGRAM.COLOURS
CUT_CHOICES = PROGRAM.CUT_CHOICES
CUT_FIELDS = PROGRAM.CUT_FIELDS
SEEK_AGAIN_MS = PROGRAM.SEEK_AGAIN_MS
SEEK_HIT_MS = PROGRAM.SEEK_HIT_MS
SEEK_PATIENCE_S = PROGRAM.SEEK_PATIENCE_S
SEEK_SETTLE_S = PROGRAM.SEEK_SETTLE_S
SHOT_NAMES = PROGRAM.SHOT_NAMES
SPOT_ARRIVED_MS = PROGRAM.SPOT_ARRIVED_MS
T = PROGRAM.T
TN = PROGRAM.TN
as_hms = PROGRAM.as_hms
block_at = PROGRAM.block_at
decimal_text = PROGRAM.decimal_text
file_timecode = PROGRAM.file_timecode
group_text = PROGRAM.group_text
gui_log = PROGRAM.gui_log
math = PROGRAM.math
os = PROGRAM.os
parse_time_point = PROGRAM.parse_time_point
parse_timecode = PROGRAM.parse_timecode
path_key = PROGRAM.path_key
re = PROGRAM.re
split_kind = PROGRAM.split_kind
strip_marks = PROGRAM.strip_marks
subprocess = PROGRAM.subprocess
sys = PROGRAM.sys
threading = PROGRAM.threading
time = PROGRAM.time
timecode_string = PROGRAM.timecode_string
video_facts = PROGRAM.video_facts


# Two names came out of the window with the block, so that this piece
# reads nothing back out of it. pause_if_running is called here and
# nowhere else; digits_font the window still uses once, and binds back
# by name like the rest.
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
                    self.setToolTip(T('%s -- %d:%02d to %d:%02d (%s s)')
                                    % (who, int(a) // 60, int(a) % 60,
                                       int(b) // 60, int(b) % 60,
                                       decimal_text("%.1f" % (b - a))))
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
                        'up after %s attempts (%s)')
                      % (self.name, _sec(have), _sec(self.want),
                         group_text(self.attempts), _position(self.p)))
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
                T('Fast forward, %s times speed')
                % decimal_text("%g" % self._speed) if fast
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
                T('Fast forward, %s times speed')
                % decimal_text("%g" % self._speed) if fast
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
