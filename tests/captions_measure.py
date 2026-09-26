# -*- coding: utf-8 -*-
"""The measurement behind window_captions_fit and window_captions_langs*.

Started by those tests, each for its own languages: every language the
window offers costs a whole window with the project opened in it, and
all of them in one test ran near run.sh's limit on the builder. The
judging stays in the tests, so each one names its checks; this builds
the windows, one process per language, hands back what each reported,
and prints what stands beside the checks.

Why this is measured at all: a caption cut off in German only ever
stood in a screenshot, and nothing in the program misbehaved, so no
test that runs the program noticed. Four windows are built at a time,
each measured once the program has finished its work and the captions
stand still; a second round only confirms a finding
of the first. A caption this platform draws with a missing glyph is
not judged but named as left out: its width is the width of boxes, and
a machine without the script's fonts would otherwise call it cut off,
or not, for a reason that is not in the program.

First that the project came in -- a view in the window holds rows --
and that the program had finished its work by then. Every sheet is then
shown once, unmeasured, since a first look can set work going that
writes captions, and the wait is repeated: that no thread or timer of
the program was still at work when measured is judged too. Then every
widget carrying text in the window -- built for real, offscreen, empty
as it opens and again with the fixture project in it, since the
two show different sheets -- is asked how wide its text is and how
much room it has. The room is not guessed: a twin of the same class,
parent, font and style sheet is given a long text, and its size hint
minus the text width is what the frame costs. Word wrap, widgets with no
text or with an icon, and fields somebody types into are left out.
The window stands at the size the manual's pictures are taken at, and
grows only where its sheets need more even at their narrowest: there
the layout would squeeze a field below its text for want of window,
not of field -- whether the sheets fit is window_sheets_fit's claim.
Resolve is never asked: the sheet is measured as it stands where
Resolve does not answer, since where it does it is somebody's own.

The reading beside the zoom buttons is asked further things: that it
holds its place, that it says something before anybody clicks, that the
face it is really drawn in has a fixed width and one width for every
digit, and that the width it is pinned to holds the widest reading. The
last two hang together: the pin is measured for a reading of noughts, so
that is the widest reading there is only while every digit is as wide as
a nought.

The text pane of the Output tab -- the one a run writes into -- is asked
the same question about its face. It asks for a typewriter family by
name, and where that name is absent Qt falls to an alias that follows
the language, so a pane drawn fixed width here can be proportional on
another platform under another locale.

Windowless, Qt answers a request for the system's typewriter face with
the Linux alias "monospace" whatever the machine, so which face the
system itself would name cannot be judged there. That piece is left out
by name, with the numbers beside it, and what is drawn is judged all the
same. Where the platform knows no fixed-width family at all -- windowless
Windows is the reported case -- the font checks are left out, because a
red line would then name the platform and not the program.
"""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import json, shutil, subprocess, time
from concurrent.futures import ThreadPoolExecutor
import the_program

SCRIPT = the_program.SCRIPT
# Every language the window offers, read off the catalogues beside the
# program: written down here, the list stops at the languages there were
# that day, and the next one is offered unmeasured.
LANGUAGES = ("en",) + tuple(sorted(
    os.path.splitext(p)[0]
    for p in os.listdir(os.path.join(os.path.dirname(SCRIPT), "language"))
    if p.endswith(".po")))
# The languages every run measures, in window_captions_fit; the
# window_captions_langs tests take the rest, for a release.
EVERY_RUN = ("en", "de")
# Windows built at once: each is a whole program with Qt in it, and
# all of them side by side are memory the machine may not have.
AT_ONCE = 4
# Rounding, nothing else: a size hint is not the sum of the character
# widths, and both are whole pixels. Above what rounding costs in either
# language, well below the width a caption is really cut off by.
SLACK = 6
# The size the pictures for the manual are taken at. Fixed rather than
# taken from the desktop: there is no desktop offscreen, and a
# measurement that depends on somebody's screen is not a measurement.
WINDOW = (1400, 950)
# Widgets that draw their whole text and cut it off when there is no
# room. A line edit and a combo box scroll or elide on purpose, and
# their content is not a caption.
KINDS = ("QLabel", "QPushButton", "QCheckBox", "QRadioButton",
         "QToolButton", "QGroupBox", "QComboBox")
NAME = "videopodcast-magic_Interview_2.json"
# The longest the reading beside the zoom buttons can get: two hours or
# more on both sides. The field is pinned to this, so the pin and the
# check have to mean the same string.
WIDEST_READING = "00:00:00 -- 00:00:00"
# VPM_LAYOUT_DUMP=1 prints every caption with its numbers; nothing in
# the run depends on it.
DUMP = bool(os.environ.get("VPM_LAYOUT_DUMP"))
# Offscreen, because that is what the builder has and what runs here
# without a window. VPM_LAYOUT_PLATFORM=cocoa (or windows, or xcb) runs
# the same measurement on the platform a user actually sees -- which is
# the only way to judge the face the system itself calls its typewriter
# face. The window stays off the screen either way: every show() sets
# WA_DontShowOnScreen first.
PLATFORM = os.environ.get("VPM_LAYOUT_PLATFORM") or "offscreen"
# How far apart two digits may measure and still count as one width.
# Well under a tenth of a pixel: the faces that fail this are out by two
# pixels, and a face that is really fixed width is out by nothing at all.
SAME_WIDTH = 0.05
# The Resolve sheet asks whether Resolve answers as soon as it is shown,
# and on a machine where Resolve runs that is somebody's own. Pointed at
# a folder that is not there, it answers "not" without asking anybody --
# the answer every builder gives.
NO_RESOLVE = (os.path.join(HERE, "no_resolve_here", "Scripting"),
              os.path.join(HERE, "no_resolve_here", "fusionscript"))


def media_links(files):
    """One folder of links to the fixture's files, made once by the parent.

    Every window then reads the files under the same names, so what the
    first ones measured the rest find in the store, as a second opening
    does for a user -- instead of each language decoding every file
    again: ten processes fewer per window, measured, on a builder that
    pays for every process it starts.
    """
    import tempfile
    here = tempfile.mkdtemp(prefix="vpm_layout_media_")
    for path in files:
        os.symlink(path, os.path.join(here, os.path.basename(path)))
    return here


def own_project():
    """A private copy of the fixture project, or None.

    Opening a project moves the project file into its output folder and
    deletes copies lying elsewhere, which on the shared fixture would
    leave the next test with nothing to open. The files are reached
    through the parent's links where it made them, else through links
    of this window's own.
    """
    import json as _json, tempfile
    from fixture_root import fixture
    source = os.path.join(fixture("interview"), NAME)
    if not os.path.exists(source):
        return None
    with open(source, encoding="utf-8") as f:
        d = _json.load(f)
    own = tempfile.mkdtemp(prefix="vpm_layout_")
    media = os.environ.get("VPM_LAYOUT_MEDIA") or own
    for entry in d.get("files") or []:
        link = os.path.join(media, os.path.basename(entry["path"]))
        if not os.path.exists(link):
            os.symlink(entry["path"], link)
        entry["path"] = link
    d["out_folder"] = os.path.join(own, "Result")
    os.makedirs(d["out_folder"], exist_ok=True)
    path = os.path.join(own, NAME)
    with open(path, "w", encoding="utf-8") as f:
        _json.dump(d, f, indent=1)
    return path


# --------------------------------------------------------------- the child
# One process per language: parts of the program read the locale for
# themselves, so the language has to reach it through the environment
# too, and a second gui() would stand on the first.
def measure(language):
    """Build the window in that language and report every caption."""
    os.environ["QT_QPA_PLATFORM"] = PLATFORM
    os.environ["VPM_SILENT"] = "1"
    os.environ["RESOLVE_SCRIPT_API"], os.environ["RESOLVE_SCRIPT_LIB"] = \
        NO_RESOLVE
    from PySide6 import QtCore, QtGui, QtWidgets

    app = QtWidgets.QApplication(sys.argv[:1])
    vpm = the_program.load()
    # Nothing may reach the network or the keychain: what is wanted is
    # the window, not a run.
    vpm.list_presets = lambda key: []
    vpm.load_api_key = lambda: ""
    vpm.update_offer = lambda *a, **k: None
    vpm.set_language(language)
    # The bar is drawn outside gui() from one plan; wrapping the drawing
    # hands over the program's own word on whether it is still at work.
    _paint = vpm.total_paint
    work = {}

    def paint_spy(Qt, plan, *rest):
        work["plan"] = plan
        return _paint(Qt, plan, *rest)

    vpm.total_paint = paint_spy

    def working():
        """Whether the program still has work open, by its own plan."""
        plan = work.get("plan")
        return plan is None or plan.busy()

    def in_hand():
        """What the program has started outside its plan and not finished.

        Its threads, and the timers it has set to go off once: the cut
        sheet works out the speakers in a thread and waits on a timer
        before it draws the preview, and neither goes through the plan.
        """
        import threading
        threads = [t.name for t in threading.enumerate()
                   if t is not threading.main_thread() and t.is_alive()]
        return threads + ["a %d ms timer" % t.interval()
                          for w in app.topLevelWidgets()
                          for t in w.findChildren(QtCore.QTimer)
                          if t.isActive() and t.isSingleShot()]

    project = own_project()
    if project:
        QtWidgets.QFileDialog.getOpenFileName = staticmethod(
            lambda *a, **k: (project, ""))
    # Nothing may wait for a click: a modal window holds the test until
    # the suite kills it.
    QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
    QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok

    # Off the desktop, on the way in: the attribute has to be set before
    # the window is shown, and gui() shows it itself. It still goes
    # through the whole layout machinery -- without that every width
    # would be Qt's untouched 100.
    _show = QtWidgets.QWidget.show

    def offstage(self):
        self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
        _show(self)

    QtWidgets.QWidget.show = offstage
    QtWidgets.QDialog.show = offstage

    def caption(w):
        """The text drawn in the widget, or "" if it carries none.

        A drop-down is asked for the longest entry it offers, not for
        the one showing: every one of them can be picked, and a box
        that fits only what it opens on is cut off as soon as somebody
        chooses.
        """
        count = getattr(w, "count", None)
        item = getattr(w, "itemText", None)
        if count is not None and item is not None:
            try:
                entries = [item(i) for i in range(count())]
            except Exception:
                entries = []
            if entries:
                return max(entries, key=len)
        for name in ("text", "title"):
            reader = getattr(w, name, None)
            if reader is None:
                continue
            try:
                value = reader()
            except Exception:
                continue
            if isinstance(value, str):
                return value
        return ""

    def drawn(text):
        """What ends up on the screen: & marks a key, && draws one &."""
        return text.replace("&&", "\x00").replace("&", "") \
                   .replace("\x00", "&")

    def missing_glyphs(font, text):
        """How many characters of the text this platform draws as a box."""
        layout = QtGui.QTextLayout(drawn(text).replace("\n", " "), font)
        layout.beginLayout()
        layout.createLine()
        layout.endLayout()
        return sum(1 for run in layout.glyphRuns()
                   for glyph in run.glyphIndexes() if glyph == 0)

    def widest(metrics, text):
        """The widest line, since a caption may hold a line break."""
        return max(metrics.horizontalAdvance(line)
                   for line in drawn(text).split("\n"))

    surcharges = {}

    def surcharge(w):
        """How much of the widget is not text -- built and measured.

        The twin gets a long text on purpose: a button has a smallest
        width of its own, and a short text would measure that instead of
        the frame. The smallest hint, because a group box without content
        has no wanted width at all. A group box still comes out short,
        since the style sheet pushes its heading right and Qt's hint does
        not count that in -- the safe direction.
        """
        key = (type(w).__name__, w.objectName(), w.styleSheet(),
               w.isEnabled(), id(w.parentWidget()))
        if key in surcharges:
            return surcharges[key]
        sample = "M" * 40
        got = None
        try:
            twin = type(w)(w.parentWidget())
            twin.setObjectName(w.objectName())
            twin.setStyleSheet(w.styleSheet())
            twin.setFont(w.font())
            # The state as well: a rule for QPushButton:disabled takes
            # the border off, and a twin that is switched on would count
            # a border that is not drawn.
            twin.setEnabled(w.isEnabled())
            for reader, writer in (("isFlat", "setFlat"),
                                   ("autoRaise", "setAutoRaise"),
                                   ("isCheckable", "setCheckable"),
                                   ("isChecked", "setChecked")):
                get, put = getattr(w, reader, None), getattr(twin, writer,
                                                             None)
                if get is not None and put is not None:
                    try:
                        put(get())
                    except Exception:
                        pass
            try:
                twin.setText(sample)
            except Exception:
                try:
                    twin.setTitle(sample)
                except Exception:
                    # A drop-down carries no text of its own: what it
                    # draws is the entry standing in it.
                    twin.addItem(sample)
            got = twin.minimumSizeHint().width() \
                - twin.fontMetrics().horizontalAdvance(sample)
            twin.setParent(None)
            twin.deleteLater()
        except Exception:
            got = None
        surcharges[key] = got
        return got

    def where(w):
        """Which box the widget sits in, so a finding can be found again."""
        parent = w.parentWidget()
        while parent is not None:
            title = getattr(parent, "title", None)
            if title is not None:
                try:
                    if title():
                        return drawn(title())
                except Exception:
                    pass
            if parent.isWindow():
                return parent.windowTitle() or type(parent).__name__
            parent = parent.parentWidget()
        return ""

    # Two rounds, and only what is short in both counts: a caption just
    # rewritten stands in its old field for one turn of the event loop,
    # which alone would make the report differ from run to run.
    rounds = [{}, {}]
    empty = [{}, {}]                     # the same, before the project
    round_now = [empty[0]]
    seen = [0]
    undrawable = set()

    def windows_size():
        """Every window at a width its sheets can be laid out in.

        The offscreen platform leaves a window it shows at its smallest
        allowed width, not the one it asked for: those get their hint.
        The program's own window keeps the size the pictures are taken
        at, and grows only to the least its sheets need -- narrower, the
        layout squeezes fields below their text, which is the sheet not
        fitting the window: window_sheets_fit's question, not this one's.
        """
        main = window_of()
        for w in app.topLevelWidgets():
            if not w.isVisible():
                continue
            if w is main:
                least = w.minimumSizeHint().width()
                if w.width() < least:
                    result["widened"] = max(result.get("widened", 0), least)
                    w.resize(least, w.height())
                continue
            hint = w.sizeHint()
            if hint.isValid() and w.width() < hint.width():
                w.resize(hint)
        settle()


    def settle():
        """Let the layout finish before anything is measured.

        Qt lays out over several passes, and a caption measured between
        two of them looks too narrow, so one round of processEvents is
        enough on an idle machine and not on a busy one. Keep going until
        the widths stop moving, and give up rather than hang.
        """
        was = None
        for _ in range(10):
            app.processEvents()
            now = sum(w.width() for w in app.allWidgets() if w.isVisible())
            if now == was:
                return
            was = now

    def sweep():
        """Every widget on the screen right now, measured once."""
        windows_size()
        for w in app.allWidgets():
            if type(w).__name__ not in KINDS or not w.isVisible():
                continue
            text = caption(w)
            if not text.strip():
                continue
            wrap = getattr(w, "wordWrap", None)
            if wrap is not None and wrap():
                continue
            icon = getattr(w, "icon", None)
            if icon is not None:
                try:
                    if not icon().isNull():
                        continue   # the icon takes room the twin has not
                except Exception:
                    pass
            if missing_glyphs(w.font(), text):
                undrawable.add(text)
                continue
            room = surcharge(w)
            if room is None:
                continue
            seen[0] += 1
            short = widest(w.fontMetrics(), text) - (w.width() - room)
            if DUMP:
                print("  %-12s room %4d width %4d short %4d  %r"
                      % (type(w).__name__, room, w.width(), short,
                         text[:50]))
            if short > SLACK:
                kind = type(w).__name__
                if w.objectName():
                    kind += " " + w.objectName()
                round_now[0][(text, kind, where(w))] = short

    def zoom_row_holds(window):
        """The reading beside the zoom buttons: does it hold its place?

        Three things about it, and the last two were added after it was
        found empty on a screenshot. It sits after the buttons and the
        band before them takes what is left, so a text that grows pushes
        the whole row along -- pressing + once moved the buttons out from
        under the pointer. It says times, so it is written in typewriter
        digits like the times under it. And it is pinned to the width of
        the widest reading, which has to be measured in the font that
        draws it: measured in one font and drawn in another, the reading
        is cut off instead.

        The text is read before anything is clicked, because that is
        where it was empty.
        """
        buttons = [b for b in window.findChildren(QtWidgets.QToolButton)
                   if b.text() in ("\u2212", "+", "\u25ad")]
        if len(buttons) != 3:
            return {"found": len(buttons)}
        beside = buttons[-1].parent().findChildren(QtWidgets.QLabel)
        span = beside[-1] if beside else None
        if span is None:
            return {"found": 3, "label": False}

        def spots():
            app.processEvents()
            return [b.mapTo(window, QtCore.QPoint(0, 0)).x() for b in buttons]

        was = span.text()
        empty = spots()
        span.setText("0:00:00 -- 1:49:36")
        full = spots()
        span.setText(was)
        # The face that is drawn, not the name that was asked for. The
        # name is the program's own wish and comparing it with itself is
        # true however the text comes out: windowless, Qt answers the
        # request with the Linux alias "monospace" on every platform,
        # and both sides of that comparison then read "monospace" while
        # the interface face is what appears. QFontInfo answers for the
        # face Qt really found, so it is the one that can be wrong.
        # Both are reported, because the difference between them is the
        # finding.
        wanted = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        drawn_in = QtGui.QFontInfo(span.font())
        # Fractions, not whole pixels: rounded, two digits three
        # quarters of a pixel apart look alike.
        fine = QtGui.QFontMetricsF(span.font())
        digits = [fine.horizontalAdvance(d) for d in "0123456789"]
        # What this platform could do at all. A face that is not fixed
        # width has two possible doors, and they are not the same: the
        # program asked for the wrong thing, or the platform has nothing
        # of the kind to give. Counted rather than assumed -- windowless
        # Windows is reported to see no system fonts whatever.
        families = QtGui.QFontDatabase.families()
        fixed_here = [f for f in families
                      if QtGui.QFontDatabase.isFixedPitch(f)]
        return {"found": 3, "label": True, "empty": empty, "full": full,
                "moved": [a - b for a, b in zip(full, empty)],
                "text": was, "family": span.font().family(),
                "fixed_family": wanted.family(),
                "drawn": drawn_in.family(),
                "fixed_pitch": bool(drawn_in.fixedPitch()),
                # Whether the platform's answer names a family that is
                # really here. Windowless it does not, and then nothing
                # can be said about the face the system itself would use.
                "known": wanted.family() in families,
                "families": len(families), "any_fixed": len(fixed_here),
                "some_fixed": fixed_here[:3],
                "digits": [min(digits), max(digits)],
                "width": span.minimumWidth(),
                "widest": WIDEST_READING,
                "needs": span.fontMetrics().horizontalAdvance(
                    WIDEST_READING)}

    def output_pane_face():
        """The text pane of the Output tab: which face is it drawn in?

        Found by its class rather than through the tab bar: the sheet
        it sits on only goes into the bar once a run writes into it, so
        while the window is measured the pane has no window above it.
        It is the program's one text pane of that class; a second one
        would make the answer ambiguous, so the count is reported too.
        """
        panes = [w for w in app.allWidgets()
                 if isinstance(w, QtWidgets.QTextEdit)]
        if len(panes) != 1:
            return {"found": len(panes)}
        pane = panes[0]
        drawn_in = QtGui.QFontInfo(pane.font())
        return {"found": 1, "family": pane.font().family(),
                "drawn": drawn_in.family(),
                "fixed_pitch": bool(drawn_in.fixedPitch())}

    def tabs_sweep(window):
        """Sheet by sheet: only what lies on top is on the screen."""
        for bar in window.findChildren(QtWidgets.QTabBar):
            for k in range(bar.count()):
                bar.setCurrentIndex(k)
                app.processEvents()
                sweep()
                # The sheet's own tab: its room is the tab Qt drew, its
                # surcharge the difference between what the bar asked
                # for and the text in it.
                text = bar.tabText(k)
                if not text.strip():
                    continue
                metrics = bar.fontMetrics()
                room = bar.tabSizeHint(k).width() \
                    - metrics.horizontalAdvance(drawn(text))
                seen[0] += 1
                short = widest(metrics, text) \
                    - (bar.tabRect(k).width() - room)
                if short > SLACK:
                    round_now[0][(drawn(text), "tab",
                                  bar.window().windowTitle())] = short

    def show_every_sheet(window):
        """Every sheet on top once, unmeasured, and back to where it was.

        The first look at a sheet can start work -- the cut sheet works
        out the speakers, then redraws its preview -- and what that work
        writes stood in no round that judges: shown sheet by sheet, the
        sheet was measured before the work was done.
        """
        for bar in window.findChildren(QtWidgets.QTabBar):
            was = bar.currentIndex()
            for k in range(bar.count()):
                bar.setCurrentIndex(k)
                app.processEvents()
            bar.setCurrentIndex(was)
        app.processEvents()
        return True

    def settings_sweep(window):
        """The window behind "Settings ...", which is built on the click."""
        wanted = vpm.T('Settings ...')[:8]
        for b in window.findChildren(QtWidgets.QPushButton):
            if drawn(b.text()).strip().startswith(wanted) and b.isVisible():
                b.click()
                app.processEvents()
                sweep()
                for d in app.topLevelWidgets():
                    if isinstance(d, QtWidgets.QDialog) and d.isVisible():
                        d.close()
                app.processEvents()
                return True
        return False

    result = {"project": bool(project)}
    step = [0]
    waited = [0]
    quiet = [0]
    clicked = [0.0]

    def views_filled(window):
        """Whether a table, tree or list in the window holds rows.

        The list inside a drop-down is a view as well and holds its
        entries from the start, so it does not count.
        """
        for v in window.findChildren(QtWidgets.QAbstractItemView):
            up = v.parentWidget()
            while up is not None and not isinstance(up, QtWidgets.QComboBox):
                up = up.parentWidget()
            if up is None and v.model() is not None \
                    and v.model().rowCount() > 0:
                return True
        return False

    def window_of():
        for x in app.topLevelWidgets():
            if "Video Podcast Magic" in x.windowTitle():
                return x

    def look():
        """Open the project, wait for it to be in, then measure."""
        window = window_of()
        if window is None and step[0] == 0 and waited[0] < 600:
            waited[0] += 1
            QtCore.QTimer.singleShot(50, look)
            return
        if window is None:
            result["error"] = "no window came up"
            app.quit()
            return
        if step[0] == 0:
            window.resize(*WINDOW)
            app.processEvents()
            sweep()                      # the empty window as it opens,
            # and again half a second on, but only to confirm a finding:
            # with none, the second look could not change the verdict.
            if round_now[0] is empty[0] and empty[0]:
                round_now[0] = empty[1]
                QtCore.QTimer.singleShot(500, look)
                return
            step[0] = 1
            clicked[0] = time.time()
            if project:
                for b in window.findChildren(QtWidgets.QPushButton):
                    if drawn(b.text()).strip().startswith(
                            vpm.T('Open project ...')[:8]):
                        b.click()
                        break
            QtCore.QTimer.singleShot(50, look)
            return
        if step[0] == 1:
            # Rows in, the plan done, nothing else in hand, the captions as
            # they were two looks ago. 150 looks of standstill end the wait,
            # and 60 s in all (10 and 10 s once another window has run
            # out of patience); the parent judges which it was.
            filled = views_filled(window)
            face = tuple(sorted((type(w).__name__, caption(w))
                                for w in app.allWidgets()
                                if type(w).__name__ in KINDS
                                and w.isVisible()))
            still = face == work.get("face")
            work["face"] = face
            quiet[0] = quiet[0] + 1 if still else 0
            quick = bool(os.environ.get("VPM_LAYOUT_QUICK"))
            if project and (not filled or working() or in_hand()
                            or quiet[0] < 2) \
                    and quiet[0] < (10 if quick else 150) \
                    and time.time() - clicked[0] < (10 if quick else 60):
                QtCore.QTimer.singleShot(200, look)
                return
            # Then every sheet once, and the same wait again: what showing
            # a sheet starts is measured with the rest, once it is done.
            if not work.get("shown"):
                work["shown"] = show_every_sheet(window)
                QtCore.QTimer.singleShot(200, look)
                return
            result["filled"] = filled
            result["busy"] = working()
            result["in_hand"] = in_hand()
            result["settled"] = not working() and quiet[0] >= 2
            result["waited"] = round(time.time() - clicked[0], 1)
            result["still"] = quiet[0]
            result["quick"] = quick
            step[0] = 2
        if step[0] == 2:
            round_now[0] = rounds[0]
            seen[0] = 0
            tabs_sweep(window)
            result["settings"] = settings_sweep(window)
            step[0] = 3
            # A finding has to stand twice; with none in the first round
            # the second could not change the verdict, so it is not run.
            if rounds[0]:
                QtCore.QTimer.singleShot(500, look)
                return
        if rounds[0]:
            round_now[0] = rounds[1]
            seen[0] = 0
            tabs_sweep(window)
            settings_sweep(window)
        result["font"] = "%s %.1f" % (app.font().family(),
                                      app.font().pointSizeF())
        # The platform, not the style: a style sheet is laid over the
        # style, and what is in app.style() then carries no name. The
        # platform decides the font, and the font is what this rests on.
        result["style"] = app.platformName()
        result["size"] = "%dx%d" % (window.width(), window.height())
        result["seen"] = seen[0]
        result["zoom_row"] = zoom_row_holds(window)
        result["output_pane"] = output_pane_face()
        result["undrawable"] = sorted(undrawable)
        both = {k: s for k, s in rounds[1].items() if k in rounds[0]}
        both.update((k, s) for k, s in empty[1].items() if k in empty[0])
        result["found"] = [dict(text=t, kind=k, box=b, short=s)
                           for (t, k, b), s in both.items()]
        app.quit()

    QtCore.QTimer.singleShot(0, look)
    # A window that never comes up must not hold the suite -- and must
    # not pass either: the report is empty then, and the parent says so.
    # Above the 30 s for the window and the 60 s for the project.
    QtCore.QTimer.singleShot(100000, app.quit)
    vpm.gui()
    print("LAYOUT " + json.dumps(result))


# -------------------------------------------------------------- the parent
# A backstop for a child that does not even quit itself, as it does
# after 100 s. A hung one holds one of four places this long while the
# rest go on in three; on the slowest builder that comes to about 220 s
# of run.sh's 300 -- estimated from its logs, not measured there.
CHILD_LIMIT = 120
# Once one window has run out of patience, the rest wait a shorter
# while: every language waiting its full patience would run past
# run.sh's 300 s, and the test would then name nothing at all.
not_in = []


def one(language, media):
    """One language's window in a process of its own; its whole output."""
    locale = "%s_%s.UTF-8" % (language, language.upper())
    env = dict(os.environ, VPM_LAYOUT_LANG=language, LANG=locale,
               LC_ALL=locale, LANGUAGE=language, QT_QPA_PLATFORM=PLATFORM,
               VPM_LAYOUT_QUICK="1" if not_in else "",
               VPM_LAYOUT_MEDIA=media)
    process = subprocess.Popen(
        [sys.executable, os.path.abspath(__file__)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        env=env, cwd=HERE)
    try:
        out, _ = process.communicate(timeout=CHILD_LIMIT)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        out = "the window never came back within %d s" % CHILD_LIMIT
    if '"filled": false' in out or '"settled": false' in out \
            or '"in_hand": ["' in out:
        not_in.append(language)
    return language, out


def windows(languages):
    """Every language's window, four at a time: (language, output) pairs.

    The fixture's files are linked once for every window; with no
    fixture each window says so itself. A pool rather than waves: a wave
    waits for its slowest window.
    """
    from fixture_root import fixture
    media = ""
    if os.path.exists(os.path.join(fixture("interview"), NAME)):
        with open(os.path.join(fixture("interview"), NAME),
                  encoding="utf-8") as f:
            media = media_links([e["path"] for e in json.load(f).get("files")
                                 or []])
    with ThreadPoolExecutor(AT_ONCE) as pool:
        outputs = list(pool.map(lambda l: one(l, media), languages))
    if media:
        shutil.rmtree(media, ignore_errors=True)
    return outputs


def report_of(out):
    """The report one window's output carries, or None if it carries none.

    The measuring happens in the child, so its dump would otherwise go
    into the pipe and no further.
    """
    if DUMP:
        for x in out.split("\n"):
            if x and not x.startswith("LAYOUT "):
                print(x)
    line = [x for x in out.split("\n") if x.startswith("LAYOUT ")]
    if not line:
        return None
    return json.loads(line[0][len("LAYOUT "):])


def said_beside(language, report):
    """What one language's window says beside its checks: size, left out."""
    print("\n%s: %d captions, %s %s, window %s"
          % (language, report["seen"], report["style"], report["font"],
             report["size"]))
    if report.get("widened"):
        print("  the window was widened to %d px, the least its sheets "
              "need in this platform's fonts: at %d px the layout would "
              "squeeze fields below their text, and whether the sheets "
              "fit the window is window_sheets_fit's question"
              % (report["widened"], WINDOW[0]))
    if report.get("undrawable"):
        # A piece of this language was not judged, and run.sh reports
        # the test green with that piece named rather than green whole.
        print("  LEFT OUT (%s, the script's glyphs): this platform draws "
              "%d caption(s) with a missing glyph, so their width is the "
              "width of boxes and was not judged -- first %r. A platform "
              "with the script's fonts judges them."
              % (language, len(report["undrawable"]),
                 report["undrawable"][0][:40]))
    if not report.get("project"):
        print("  the interview fixture is not there -- only the empty "
              "window was looked at. Run tests/fixtures.sh.")
    if not report.get("settings"):
        print("  the settings window was not reached -- not measured.")


# Pieces this machine could not judge, said once rather than once per
# language: they are about the platform, not about the words in it.
said = []


def evidence(row):
    """The evidence for the two font checks, printed whether they pass.

    Which face was asked for, which one is drawn, whether that one has a
    fixed width, and what this platform had to offer. Windowless Linux
    and Windows cannot be measured here at all, so the builder's own log
    is the only place the answer can come from.
    """
    low, high = row.get("digits") or [0.0, 0.0]
    return ("it asks for %r and draws %r, fixed pitch %s; its "
            "digits measure %.2f to %.2f px. This platform "
            "knows %d font families, %d of them fixed width%s"
            % (row.get("family"), row.get("drawn"),
               row.get("fixed_pitch"), low, high,
               row.get("families", 0), row.get("any_fixed", 0),
               (" (%s)" % ", ".join(row.get("some_fixed") or []))
               if row.get("some_fixed") else ""))


def face_left_out(row, evidence):
    """Say, once, what this platform cannot judge about the faces.

    True where the font checks can say something about the program:
    where the platform knows at least one fixed-width family.
    """
    if not row.get("known") and "system face" not in said:
        # Said once, not once per language: it is one piece, and it
        # is about the platform rather than about the words in the
        # window. run.sh reads a line beginning LEFT OUT and reports
        # the test as green with a piece missing, which is what this
        # is -- the face drawn is still judged below.
        said.append("system face")
        print("  LEFT OUT (the system's own typewriter face): this "
              "platform answers %r, which is not a family it knows, "
              "so whether the program picks up the face the system "
              "itself would use cannot be judged here -- only that "
              "what is drawn has a fixed width. %s. A run on the "
              "platform a user sees judges it: "
              "VPM_LAYOUT_PLATFORM=cocoa (or windows, or xcb)."
              % (row.get("fixed_family"), evidence))
    if not row.get("any_fixed"):
        # No family of fixed width anywhere on this platform, so
        # nothing the program could ask for would be drawn with one.
        # Red here would name the platform and not the program, and
        # silence would hide that the piece was never checked.
        if "any face" not in said:
            said.append("any face")
            print("  LEFT OUT (the width of the face): this "
                  "platform's Qt knows no fixed-width font family "
                  "at all, so nothing the program asks for can be "
                  "drawn with one and none of the font checks says "
                  "anything about the program. %s. Windowless "
                  "Windows is the known case, QTBUG-142818; "
                  "QT_QPA_FONTDIR pointing at the system's font "
                  "folder is what would bring the fonts back."
                  % evidence)
        return False
    return True


if __name__ == "__main__":
    measure(os.environ["VPM_LAYOUT_LANG"])
