# -*- coding: utf-8 -*-
"""Does every visible caption fit the field that carries it?

Both languages, because that is where this goes wrong: a caption cut off
in German only ever stood in a screenshot, and nothing in the program
misbehaved, so no test that runs the program noticed.

Every widget carrying text in the window -- built for real, offscreen,
with the fixture project in it -- is asked how wide its text is and how
much room it has. The room is not guessed: a twin of the same class,
parent, font and style sheet is given a long text, and its size hint
minus the text width is what the frame costs. Word wrap, widgets with no
text or with an icon, and fields somebody types into are left out.
"""
import os, sys, json, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
sys.path.insert(0, HERE)

LANGUAGES = ("en", "de")
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
         "QToolButton", "QGroupBox")
NAME = "videopodcast-magic_Interview_2.json"
# VPM_LAYOUT_DUMP=1 prints every caption with its numbers; nothing in
# the run depends on it.
DUMP = bool(os.environ.get("VPM_LAYOUT_DUMP"))


def own_project():
    """A private copy of the fixture project, or None.

    Opening a project moves the project file into its output folder and
    deletes copies lying elsewhere, which on the shared fixture would
    leave the next test with nothing to open.
    """
    import json as _json, tempfile
    from fixture_root import fixture
    source = os.path.join(fixture("interview"), NAME)
    if not os.path.exists(source):
        return None
    with open(source, encoding="utf-8") as f:
        d = _json.load(f)
    own = tempfile.mkdtemp(prefix="vpm_layout_")
    for entry in d.get("files") or []:
        link = os.path.join(own, os.path.basename(entry["path"]))
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
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ["VPM_SILENT"] = "1"
    import importlib.util
    from PySide6 import QtCore, QtGui, QtWidgets

    app = QtWidgets.QApplication(sys.argv[:1])
    spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
    vpm = importlib.util.module_from_spec(spec)
    sys.modules["vpm"] = vpm
    spec.loader.exec_module(vpm)
    # Nothing may reach the network or the keychain: what is wanted is
    # the window, not a run.
    vpm.list_presets = lambda key: []
    vpm.load_api_key = lambda: ""
    vpm.update_offer = lambda *a, **k: None
    vpm.set_language(language)

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
        """The text drawn in the widget, or "" if it carries none."""
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
                twin.setTitle(sample)
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
    round_now = [rounds[0]]
    seen = [0]

    def windows_size():
        """Give every window the program did not size itself its hint.

        The offscreen platform leaves a window it shows at its smallest
        allowed width instead of the width it asked for, and every
        caption in it would then look cut off.
        """
        for w in app.topLevelWidgets():
            if not w.isVisible() or w.windowTitle().startswith("Video Pod"):
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

    def window_of():
        for x in app.topLevelWidgets():
            if "Video Podcast Magic" in x.windowTitle():
                return x

    def look():
        """Open the project, wait for it to be in, then measure."""
        window = window_of()
        if window is None:
            result["error"] = "no window came up"
            app.quit()
            return
        if step[0] == 0:
            window.resize(*WINDOW)
            app.processEvents()
            sweep()                      # the empty window as it opens
            step[0] = 1
            if project:
                for b in window.findChildren(QtWidgets.QPushButton):
                    if drawn(b.text()).strip().startswith(
                            vpm.T('Open project ...')[:8]):
                        b.click()
                        break
            QtCore.QTimer.singleShot(400, look)
            return
        if step[0] == 1:
            # The tables are only built once the project is read.
            # Waiting for the rows rather than for the clock: a slow
            # machine takes longer, an interface that never gets there
            # gives up.
            filled = any(t.rowCount() for t in
                         window.findChildren(QtWidgets.QTableWidget))
            if project and not filled and waited[0] < 100:
                waited[0] += 1
                QtCore.QTimer.singleShot(300, look)
                return
            result["filled"] = filled
            step[0] = 2
        if step[0] == 2:
            round_now[0] = rounds[0]
            tabs_sweep(window)
            result["settings"] = settings_sweep(window)
            step[0] = 3
            QtCore.QTimer.singleShot(500, look)
            return
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
        result["found"] = [dict(text=t, kind=k, box=b, short=s)
                           for (t, k, b), s in rounds[1].items()
                           if (t, k, b) in rounds[0]]
        app.quit()

    QtCore.QTimer.singleShot(1200, look)
    # A window that never comes up must not hold the suite -- and must
    # not pass either: the report is empty then, and the parent says so.
    QtCore.QTimer.singleShot(180000, app.quit)
    vpm.gui()
    print("LAYOUT " + json.dumps(result))


if os.environ.get("VPM_LAYOUT_LANG"):
    measure(os.environ["VPM_LAYOUT_LANG"])
    raise SystemExit(0)


# -------------------------------------------------------------- the parent
error = []


def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


started = []
for language in LANGUAGES:
    locale = "%s_%s.UTF-8" % (language, language.upper())
    env = dict(os.environ, VPM_LAYOUT_LANG=language, LANG=locale,
               LC_ALL=locale, LANGUAGE=language,
               QT_QPA_PLATFORM="offscreen")
    started.append((language, subprocess.Popen(
        [sys.executable, os.path.abspath(__file__)], stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True, env=env, cwd=HERE)))

for language, process in started:
    try:
        out, _ = process.communicate(timeout=600)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        out = "the window never came back"
    # The measuring happens in the child, so its dump would otherwise go
    # into the pipe and no further.
    if DUMP:
        for x in out.split("\n"):
            if x and not x.startswith("LAYOUT "):
                print(x)
    line = [x for x in out.split("\n") if x.startswith("LAYOUT ")]
    if not line:
        check("%s: the window was measured" % language, False,
              "nothing came back")
        for x in out.rstrip().split("\n")[-20:]:
            print("    " + x[:150])
        continue
    report = json.loads(line[0][len("LAYOUT "):])
    if report.get("error") or not report.get("seen"):
        check("%s: the window was measured" % language, False,
              report.get("error", "no widget was looked at"))
        continue
    print("\n%s: %d captions, %s %s, window %s"
          % (language, report["seen"], report["style"], report["font"],
             report["size"]))
    if not report.get("project"):
        print("  the interview fixture is not there -- only the empty "
              "window was looked at. Run tests/fixtures.sh.")
    elif not report.get("filled"):
        print("  the project did not come in -- the tables stayed empty.")
    if not report.get("settings"):
        print("  the settings window was not reached -- not measured.")
    found = sorted(report["found"], key=lambda f: -f["short"])
    # The findings go on the line that fails, not only under it: a build
    # machine's log keeps the lines that say FAIL and drops the rest, and
    # the machine that could name a caption too narrow on Windows is the
    # one nobody here can run.
    check("%s: every caption fits its field" % language, not found,
          "%d cut off%s" % (len(found), "".join(
              "; %s short by %d px in %s: %r"
              % (f["kind"][:14], f["short"], f["box"][:30], f["text"][:60])
              for f in found)))
    for f in found:
        print("    %-14s short by %4d px  in %-30s  %r"
              % (f["kind"][:14], f["short"], f["box"][:30], f["text"][:60]))

print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
