# -*- coding: utf-8 -*-
"""The window fits its screen and its first three sheets fit the window.

The window is built offscreen on a stated screen, with the fixture
project opened the way window_captions_fit opens it -- the assignment
and Resolve sheets only exist once there are files. English, and the
three languages whose catalogues hold the most characters, counted off
the catalogues at every run; each in a window of its own.
First that the window came up on that screen with the project in it,
and that it opened no wider than that screen; then per sheet what it
needs against the room the window lets be seen of it on opening, and
for the two scrolling sheets whether a sideways scrollbar shows. Both
sides come out of one run on one platform, so a platform that draws
wider moves both; no pixel bound is written down.
The files sheet is measured with a long output folder chosen, the
kind a share gives. Left out: the Output sheet, which only appears once
a run has made something, and this test runs nothing; other languages;
Resolve, never asked, so its sheet stands as where it does not answer.
"""
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import os, re, sys, json, shutil, subprocess, tempfile, time
import the_program

SCRIPT = the_program.SCRIPT
sys.path.insert(0, HERE)


def longest_catalogues(many=3):
    """The languages whose catalogues hold the most characters, longest first.

    Counted off the catalogues beside the program at every run, never
    written down: a catalogue that grows past another moves into the
    measurement by itself, and a new language is counted like the rest.
    """
    folder = os.path.join(os.path.dirname(SCRIPT), "language")
    size = {}
    for name in os.listdir(folder):
        if name.endswith(".po"):
            size[name[:-3]] = sum(len(t) for t in the_program.po_texts(
                os.path.join(folder, name)).values())
    return sorted(size, key=lambda k: (-size[k], k))[:many]


LONGEST = longest_catalogues()
LANGUAGES = ("en",) + tuple(LONGEST)
NAME = "videopodcast-magic_Interview_2.json"
# The screen the window is opened on: a small laptop's. What a sheet
# needs does not depend on the screen, only its room does, so this is
# harder than any wider desk. Offscreen the platform's own screen is
# 800 px wide, under the window's minimum. The test reads the window's
# width off the window and does not say what the program's cap is.
SCREEN = (1280, 1024)
# An example, not a bound: one run offscreen on a Mac, 25.9.2026, gave
# the window 1280 px and a page of 1254 px; the sheets needed 906 en /
# 966 ta, the longest catalogue then (files), 1054 / 1186 (assignment),
# 968 / 1051 (Resolve).
# Windows draws wider and the builder's faces differ, so a fixed number
# measured here would be red there for no fault: what is held is the
# sheet against its own window, in the same run.


def own_project(own):
    """A private copy of the fixture project in *own*, or None.

    Opening a project moves the project file into its output folder and
    deletes copies lying elsewhere, which on the shared fixture would
    leave the next test with nothing to open.
    """
    from fixture_root import fixture
    source = os.path.join(fixture("interview"), NAME)
    if not os.path.exists(source):
        return None
    with open(source, encoding="utf-8") as f:
        d = json.load(f)
    for entry in d.get("files") or []:
        link = os.path.join(own, os.path.basename(entry["path"]))
        if not os.path.exists(link):
            os.symlink(entry["path"], link)
        entry["path"] = link
    # A long output folder, as a share gives one: the files sheet shows
    # the chosen folder, and a path is the longest thing it can show.
    # Made here, because opening the project moves its file into it.
    far = os.path.join(own, "Output_folder_with_a_long_name_as_a_share"
                       "_would_give_it", "Season_03_Episode_Recordings_2026",
                       "Cut_and_Sound_Versions_Final_Delivery")
    os.makedirs(far, exist_ok=True)
    d["out_folder"] = far
    path = os.path.join(own, NAME)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1)
    return path


def drawn(text):
    """What stands on the tab: no doubled ampersand, no tick."""
    return text.replace("&&", "\x00").replace("&", "") \
               .replace("\x00", "&").replace("✓", "").strip()


# --------------------------------------------------------------- the child
# One process per language: parts of the program read the locale for
# themselves, so the language has to reach it through the environment
# too, and a second gui() would stand on the first.
def measure(language):
    """Build the window in that language and report the sheets' widths."""
    own = tempfile.mkdtemp(prefix="vpm_sheets_")
    with open(os.path.join(own, "screen.json"), "w") as f:
        json.dump({"screens": [{"name": "desk", "x": 0, "y": 0,
                                "width": SCREEN[0], "height": SCREEN[1],
                                "logicalDpi": 96, "dpr": 1}]}, f)
    # The screen file by its bare name, from its own folder: Qt splits
    # the platform string at every colon, so a Windows path ('C:\...')
    # would be read as a file called 'C' and Qt would abort. A path
    # relative to the test's folder would not do either: on a builder the
    # temporary folder and the checkout can lie on different drives.
    os.environ["QT_QPA_PLATFORM"] = "offscreen:configfile=screen.json"
    os.environ["VPM_SILENT"] = "1"
    # The Resolve sheet asks whether Resolve answers as soon as it is
    # shown; pointed at a folder that is not there, it answers "not"
    # without asking the Resolve somebody may have running here.
    os.environ["RESOLVE_SCRIPT_API"] = os.path.join(own, "no", "Scripting")
    os.environ["RESOLVE_SCRIPT_LIB"] = os.path.join(own, "no", "fusion")
    from PySide6 import QtCore, QtWidgets

    was_in = os.getcwd()
    os.chdir(own)
    app = QtWidgets.QApplication(sys.argv[:1])
    os.chdir(was_in)
    vpm = the_program.load()
    # Nothing may reach the network or the keychain: what is wanted is
    # the window, not a run.
    vpm.list_presets = lambda key: []
    vpm.load_api_key = lambda: ""
    vpm.update_offer = lambda *a, **k: None
    vpm.set_language(language)

    project = own_project(own)
    if project:
        QtWidgets.QFileDialog.getOpenFileName = staticmethod(
            lambda *a, **k: (project, ""))
    # Nothing may wait for a click: a modal window holds the test until
    # the suite kills it.
    QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
    QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok

    # Off the desktop, on the way in: the attribute has to be set before
    # the window is shown, and gui() shows it itself. It still goes
    # through the whole layout machinery.
    _show = QtWidgets.QWidget.show

    def offstage(self):
        self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
        _show(self)

    QtWidgets.QWidget.show = offstage
    QtWidgets.QDialog.show = offstage

    def settle():
        """Let the layout finish before anything is measured.

        Qt lays out over several passes; keep going until the widths
        stop moving, and give up rather than hang.
        """
        was = None
        for _ in range(10):
            app.processEvents()
            now = sum(w.width() for w in app.allWidgets() if w.isVisible())
            if now == was:
                return
            was = now

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

    def least(w):
        """The narrowest the widget can be drawn: its layout's minimum,
        or a minimum set on it outright where that is larger."""
        return max(w.minimumSizeHint().width(), w.minimumWidth())

    def widest_path(holder):
        """Down the widest visible child, level by level, for the FAIL line.

        A sheet that asks for too much does so through one branch of its
        layout; the line names that branch from the sheet down to the
        piece at its end, each with the width it asks for.
        """
        steps = []
        here = holder
        for _ in range(6):
            kids = [c for c in here.findChildren(
                        QtWidgets.QWidget,
                        options=QtCore.Qt.FindDirectChildrenOnly)
                    if c.isVisible()]
            if not kids:
                break
            here = max(kids, key=least)
            # The folder label holds this run's temporary folder, and
            # the root of it, under the home folder or not, is masked.
            name = drawn(caption(here)).replace(own, "<own>").replace(
                os.path.dirname(own), "<tmp>")[:30] or type(here).__name__
            steps.append("%r %d" % (name, least(here)))
        return " > ".join(steps) or "no visible piece"

    def shown(w):
        """How much of the widget's width the window lets be seen.

        Not its own width: a page can be laid out wider than the window
        around it, and what lies past the window's edge is cut off all
        the same.
        """
        top = w.window()
        seen = QtCore.QRect(w.mapTo(top, QtCore.QPoint(0, 0)), w.size())
        up = w.parentWidget()
        while up is not None:
            seen = seen.intersected(QtCore.QRect(
                up.mapTo(top, QtCore.QPoint(0, 0)), up.size()))
            up = up.parentWidget()
        return max(0, seen.width())

    def sheets_of(window):
        """The first three sheets: what each needs and what it is given."""
        bar = window.findChild(QtWidgets.QTabWidget)
        out = []
        for k in range(min(3, bar.count())):
            bar.setCurrentIndex(k)
            settle()
            sheet = bar.widget(k)
            one = {"place": k, "title": drawn(bar.tabText(k))}
            if isinstance(sheet, QtWidgets.QScrollArea):
                inside = sheet.widget()
                one["need"] = least(inside)
                one["room"] = shown(sheet.viewport())
                one["bar_shown"] = sheet.horizontalScrollBar().isVisible()
                one["scroll"] = sheet.horizontalScrollBar().maximum()
                one["widest"] = widest_path(inside)
            else:
                one["need"] = least(sheet)
                one["room"] = shown(sheet)
                one["bar_shown"] = None
                one["scroll"] = None
                one["widest"] = widest_path(sheet)
            out.append(one)
        return out

    result = {"project": bool(project), "tabs": [], "waited": 0,
              "screen": app.primaryScreen().availableGeometry().width()}
    step = [0]
    began = time.time()

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
            # As the program opened it: no resize by this test. The
            # frame counts, since it takes room on the screen too.
            frame = window.frameGeometry()
            result["window"] = [frame.width(), frame.height()]
            step[0] = 1
            if project:
                for b in window.findChildren(QtWidgets.QPushButton):
                    if drawn(b.text()).startswith(
                            vpm.T('Open project ...')[:8]):
                        b.click()
                        break
            QtCore.QTimer.singleShot(400, look)
            return
        # The tables are only built once the project is read. Waiting
        # for the rows rather than for the clock: a slow machine takes
        # longer, a window that never gets there gives up -- and says
        # so, rather than measuring a window with one sheet in it.
        filled = any(t.rowCount() for t in
                     window.findChildren(QtWidgets.QTableWidget))
        if project and not filled and time.time() - began < 120:
            QtCore.QTimer.singleShot(300, look)
            return
        result["filled"] = filled
        result["waited"] = round(time.time() - began, 1)
        result["sheets"] = sheets_of(window)
        bar = window.findChild(QtWidgets.QTabWidget)
        result["tabs"] = [drawn(bar.tabText(k)) for k in range(bar.count())]
        app.quit()

    QtCore.QTimer.singleShot(1200, look)
    # A window that never comes up must not hold the suite -- and must
    # not pass either: the report is empty then, and the parent says so.
    QtCore.QTimer.singleShot(150000, app.quit)
    vpm.gui()
    print("SHEETS " + json.dumps(result))
    shutil.rmtree(own, ignore_errors=True)


if os.environ.get("VPM_SHEETS_LANG"):
    measure(os.environ["VPM_SHEETS_LANG"])
    raise SystemExit(0)


# -------------------------------------------------------------- the parent
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def home_off(text):
    """A line from the child, the home folder as ~ and scratch as <scratch>.

    A counter-proof's program copy lies in a scratch folder whose name
    carries the account's (/tmp/claude-<uid>/-Users-<name>-...).
    """
    return re.sub(r"(/private)?/tmp/claude-\d+/[^/\s'\"]+", "<scratch>",
                  text.replace(os.path.expanduser("~"), "~"))


started = []
for language in LANGUAGES:
    locale = "%s_%s.UTF-8" % (language, language.upper())
    env = dict(os.environ, VPM_SHEETS_LANG=language, LANG=locale,
               LC_ALL=locale, LANGUAGE=language)
    started.append((language, subprocess.Popen(
        [sys.executable, os.path.abspath(__file__)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        env=env, cwd=HERE)))

reports = {}
for language, process in started:
    try:
        out, _ = process.communicate(timeout=240)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        out = "the window never came back within 240 s"
    line = [x for x in out.split("\n") if x.startswith("SHEETS ")]
    try:
        report = json.loads(line[0][len("SHEETS "):]) if line else {}
    except ValueError as e:
        report = {"error": "the child's report did not read: %s" % e}
    report["came_back"] = bool(line)
    report["language"] = language
    report["last_lines"] = home_off(" / ".join(
        x for x in out.rstrip().split("\n")[-4:] if x))[:300]
    reports[language] = report


def came_up(report):
    """The first thing that can be wrong, before any sheet is judged.

    A window with one sheet in it, or on a screen narrower than the one
    laid out, would make every line below about the harness.
    """
    screen = report.get("screen") or 0
    window = (report.get("window") or [0, 0])[0]
    if not report["came_back"]:
        why = "nothing came back -- last lines: " + report["last_lines"]
    elif report.get("error"):
        why = report["error"]
    elif not report.get("project"):
        why = "no fixture project -- run tests/fixtures.sh"
    elif not report.get("filled"):
        why = "the tables stayed empty after %s s" % report.get("waited")
    elif screen != SCREEN[0]:
        why = ("the screen came up %d px wide, not the %d px laid out -- "
               "the platform did not take the screen file"
               % (screen, SCREEN[0]))
    else:
        why = "window %d px wide on a %d px screen, tabs %s, %.1f s" % (
            window, screen, report.get("tabs"), report.get("waited") or 0)
    return (report["came_back"] and report.get("filled") is True
            and screen == SCREEN[0]), why


def on_screen(report):
    """The window opens no wider than the screen, measured in one run.

    The program keeps a sheet that asks for too much from widening the
    window by a minimum size set on it outright; without that, the room
    the sheets are judged against below would grow with them, and every
    sheet would fit a window that runs off the screen.
    """
    screen = report.get("screen") or 0
    window = (report.get("window") or [0, 0])[0]
    return 0 < window <= screen, "window %d px wide on a %d px screen" % (
        window, screen)


def sheet(report, place):
    """The sheet at that place in the tab bar, or None."""
    for s in report.get("sheets") or []:
        if s["place"] == place:
            return s
    return None


def missing(report, place):
    return False, "no sheet at place %d -- the tab bar holds %s" % (
        place, report.get("tabs"))


def fits(report, place, room_name):
    """What the sheet needs against the room it is given, in one run.

    The files sheet is a plain page and cannot scroll: what does not fit
    is cut off. The two others scroll, so what they need is the widget
    inside the scroll area and their room is the viewport.
    """
    s = sheet(report, place)
    if s is None:
        return missing(report, place)
    window = (report.get("window") or [0, 0])[0]
    # The widest piece can be the folder's path, and should <own> not
    # stand in for it, a temporary folder under the home folder would
    # bring the account's name into the line.
    return s["need"] <= s["room"], home_off(
        "%r needs %d px in a %s %d px wide, the window %d px; widest: %s"
        % (s["title"], s["need"], room_name, s["room"], window,
           s["widest"]))


def no_bar(report, place):
    """No sideways scrollbar is shown on the scrolling sheet.

    A claim of its own beside fits(): it also falls when a bar stands
    there with nothing to scroll.
    """
    s = sheet(report, place)
    if s is None:
        return missing(report, place)
    window = (report.get("window") or [0, 0])[0]
    return s["bar_shown"] is False, (
        "%r sideways bar shown: %s, scrolls %s px; needs %d px in a "
        "viewport %d px wide, the window %d px"
        % (s["title"], s["bar_shown"], s["scroll"], s["need"], s["room"],
           window))


def of(report, verdict):
    """The verdict, its line naming the language it was measured in."""
    ok, why = verdict
    return ok, "%s: %s" % (report.get("language"), why)


# Written out once per window: a computed name would leave one wording
# for four checks, and the register could not say which was seen red.
# The three by their place among the catalogues, since which language
# holds that place is counted at the run.
en = reports["en"]
first, second, third = (reports[x] for x in LONGEST)
check("en: the window came up with the project in it", *of(en, came_up(en)))
check("en: the window opens no wider than its screen",
      *of(en, on_screen(en)))
check("en: the files sheet fits the page on opening",
      *of(en, fits(en, 0, "page")))
check("en: the assignment sheet fits its viewport on opening",
      *of(en, fits(en, 1, "viewport")))
check("en: the assignment sheet shows no sideways scrollbar",
      *of(en, no_bar(en, 1)))
check("en: the Resolve sheet fits its viewport on opening",
      *of(en, fits(en, 2, "viewport")))
check("en: the Resolve sheet shows no sideways scrollbar",
      *of(en, no_bar(en, 2)))

check("longest catalogue: the window came up with the project in it",
      *of(first, came_up(first)))
check("longest catalogue: the window opens no wider than its screen",
      *of(first, on_screen(first)))
check("longest catalogue: the files sheet fits the page on opening",
      *of(first, fits(first, 0, "page")))
check("longest catalogue: the assignment sheet fits its viewport",
      *of(first, fits(first, 1, "viewport")))
check("longest catalogue: the assignment sheet shows no sideways bar",
      *of(first, no_bar(first, 1)))
check("longest catalogue: the Resolve sheet fits its viewport",
      *of(first, fits(first, 2, "viewport")))
check("longest catalogue: the Resolve sheet shows no sideways bar",
      *of(first, no_bar(first, 2)))

check("second longest: the window came up with the project in it",
      *of(second, came_up(second)))
check("second longest: the window opens no wider than its screen",
      *of(second, on_screen(second)))
check("second longest: the files sheet fits the page on opening",
      *of(second, fits(second, 0, "page")))
check("second longest: the assignment sheet fits its viewport",
      *of(second, fits(second, 1, "viewport")))
check("second longest: the assignment sheet shows no sideways bar",
      *of(second, no_bar(second, 1)))
check("second longest: the Resolve sheet fits its viewport",
      *of(second, fits(second, 2, "viewport")))
check("second longest: the Resolve sheet shows no sideways bar",
      *of(second, no_bar(second, 2)))

check("third longest: the window came up with the project in it",
      *of(third, came_up(third)))
check("third longest: the window opens no wider than its screen",
      *of(third, on_screen(third)))
check("third longest: the files sheet fits the page on opening",
      *of(third, fits(third, 0, "page")))
check("third longest: the assignment sheet fits its viewport",
      *of(third, fits(third, 1, "viewport")))
check("third longest: the assignment sheet shows no sideways bar",
      *of(third, no_bar(third, 1)))
check("third longest: the Resolve sheet fits its viewport",
      *of(third, fits(third, 2, "viewport")))
check("third longest: the Resolve sheet shows no sideways bar",
      *of(third, no_bar(third, 2)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
