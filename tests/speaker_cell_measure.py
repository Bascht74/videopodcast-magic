# -*- coding: utf-8 -*-
"""The measurement behind window_speaker_cell_fits and window_speaker_langs*.

Started by those tests, each for its own languages: every language and
font costs a whole window with the project opened in it, and all of
them in one test ran near run.sh's limit. The judging stays in the
tests, so each one names its checks; this builds the windows and the
trees and hands back what each measured.

The real window is built by gui() once per language and font, in child
processes, the fixture project opened in it, on a small laptop's
screen; once its progress bar has gone it is dragged as small as it
goes, and what is seen of the assignment tree then is the width every
tree below is given. That window runs without a speaker separation, as
the suite does, so its own tree has no Speakers column; taken on trust
that a tree which scrolls sideways does not widen the window for one.

The tree the cells are measured in is built and filled by the same
functions the window uses, so what is measured here and what is drawn
there cannot drift apart. The height a text needs is worked out by the
font's own bounding box, a different road from the one the program
takes. What the cell is given has to be asked for and not left to the
label's own offer: the offer is right on this machine and was 14 px
short on the Windows builder, so a run here can confirm the asking but
never the offer.
"""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import json
import subprocess
import tempfile
import time
import the_program

SCRIPT = the_program.SCRIPT
# The screen the window is dragged small on: a small laptop's, the one
# window_sheets_fit opens on. The window never takes a least width
# past its screen, so on a wider desk the column only gets more room.
SCREEN = (1280, 1024)
NAME = "videopodcast-magic_Interview_2.json"
PATH = "/tmp/Presenter_2026-09-04.wav"
# Every language the window offers, read off the catalogues beside the
# program: written down here, the list stops at the languages there were
# that day, and the next one is offered unmeasured.
LANGUAGES = ("en",) + tuple(sorted(
    os.path.splitext(p)[0]
    for p in os.listdir(os.path.join(os.path.dirname(SCRIPT), "language"))
    if p.endswith(".po")))
# The languages every run measures, in window_speaker_cell_fits; the
# window_speaker_langs tests take the rest, for a release.
EVERY_RUN = ("en", "de")
# The same nominal font is drawn 1.89 times as wide on Windows as on
# this Mac -- measured on the builder over both languages, and written
# down beside WIDE_FONT in the program. A stretched font is that
# difference and nothing else: the glyphs get wider, the line height
# stays, which is exactly what makes a wrapping label need more lines
# than its own size hint admits.
WIDER = 189
# The fonts swept, from ours to the widest we build for.
FONTS = (100, 120, 136, 160, WIDER)


def languages_line(languages):
    """The one plain line saying which languages this test measures.

    The every-run pair is said in the_program's words, the same line
    every test measuring a language at a time prints; a release slice
    names its languages, as window_captions_langsN does.
    """
    if tuple(languages) == EVERY_RUN:
        return the_program.every_run_line(LANGUAGES)
    return "languages: %s" % ", ".join(languages)


# --------------------------------------------------------------- the child
# The real window, built by gui() once per language and font, the way
# the program builds it again for a newly chosen language; the fixture
# project opened in it, and then dragged as small as it goes.
def narrow_child(cases):
    """Report, per case, how wide the window and its tree stay when small.

    Measured once the prework bar has come and gone, as a window at
    rest stands: while the bar shows, the window asks for more.
    """
    from fixture_root import fixture
    own = tempfile.mkdtemp(prefix="vpm_narrow_")
    with open(os.path.join(own, "screen.json"), "w") as f:
        json.dump({"screens": [{"name": "desk", "x": 0, "y": 0,
                                "width": SCREEN[0], "height": SCREEN[1],
                                "logicalDpi": 96, "dpr": 1}]}, f)
    # By its bare name from its own folder: Qt splits at every colon.
    os.environ["QT_QPA_PLATFORM"] = "offscreen:configfile=screen.json"
    # Pointed at a folder that is not there, so no Resolve is asked.
    os.environ["RESOLVE_SCRIPT_API"] = os.path.join(own, "no", "Scripting")
    os.environ["RESOLVE_SCRIPT_LIB"] = os.path.join(own, "no", "fusion")
    from PySide6 import QtCore, QtGui, QtWidgets
    was_in = os.getcwd()
    os.chdir(own)
    app = QtWidgets.QApplication(sys.argv[:1])
    os.chdir(was_in)
    plain = QtGui.QFont(QtWidgets.QApplication.font())
    vpm = the_program.load()
    vpm.list_presets = lambda key: []
    vpm.load_api_key = lambda: ""
    vpm.update_offer = lambda *a, **k: None
    QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
    QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
    _show = QtWidgets.QWidget.show

    def offstage(self):
        """Shown through the whole layout machinery, never on a screen."""
        self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
        _show(self)

    QtWidgets.QWidget.show = offstage
    QtWidgets.QDialog.show = offstage
    source = os.path.join(fixture("interview"), NAME)
    if not os.path.exists(source):
        print("NARROW " + json.dumps({"error": "no fixture project -- "
                                      "run tests/fixtures.sh"}))
        return

    def settle():
        """Process events until the visible widths stop moving."""
        was = None
        for _ in range(10):
            app.processEvents()
            now = sum(w.width() for w in app.allWidgets() if w.isVisible())
            if now == was:
                return
            was = now

    for n, case in enumerate(cases):
        language, stretch = case.split(":")
        # A private project per case: opening moves its file away.
        with open(source, encoding="utf-8") as f:
            project = json.load(f)
        for entry in project.get("files") or []:
            link = os.path.join(own, os.path.basename(entry["path"]))
            if not os.path.exists(link):
                os.symlink(entry["path"], link)
            entry["path"] = link
        path = os.path.join(own, str(n), NAME)
        os.makedirs(os.path.dirname(path))
        with open(path, "w", encoding="utf-8") as f:
            json.dump(project, f)
        QtWidgets.QFileDialog.getOpenFileName = staticmethod(
            lambda *a, **k: (path, ""))
        font = QtGui.QFont(plain)
        font.setStretch(int(stretch))
        QtWidgets.QApplication.setFont(font)
        vpm.set_language(language)
        got = {"case": case}
        seen = {"step": "window", "since": time.time()}

        def look():
            """One step further each time, and measure at the end."""
            window = [x for x in app.topLevelWidgets() if x.isVisible()
                      and "Video Podcast Magic" in x.windowTitle()]
            # The assignment tree, known by its first column's head.
            trees = [t for w in window
                     for t in w.findChildren(QtWidgets.QTreeView)
                     if t.model() is not None and t.model().headerData(
                         0, QtCore.Qt.Horizontal) == vpm.T('Audio recording')]
            bar = [b for w in window
                   for b in w.findChildren(QtWidgets.QProgressBar)
                   if b.isVisible()]
            step = seen["step"]
            if step == "window" and window:
                for b in window[0].findChildren(QtWidgets.QPushButton):
                    if b.text().replace("&", "").startswith(
                            vpm.T('Open project ...')[:8]):
                        b.click()
                        break
                step = "tree"
            elif step == "tree" and trees:
                step = "rest"
            elif step == "rest" and not bar:
                # The prework is queued in the call that builds the tree,
                # so its bar is up by now if there is work -- in the first
                # case of a child; later ones find the envelopes made.
                step = "measure"
            if step != seen["step"]:
                seen.update(step=step, since=time.time())
            if step == "measure":
                tabs = window[0].findChild(QtWidgets.QTabWidget)
                tabs.setCurrentIndex([k for k in range(tabs.count())
                                      if tabs.widget(k).isAncestorOf(
                                          trees[0])][0])
                settle()
                window[0].resize(1, 1)
                settle()
                # What is seen of the tree, not its own width: the sheet
                # scrolls, and lays the tree out wider than it shows.
                seen_of = QtCore.QRect(QtCore.QPoint(0, 0), trees[0].size())
                up = trees[0]
                while up.parentWidget() is not None:
                    seen_of.translate(up.pos())
                    up = up.parentWidget()
                    seen_of = seen_of.intersected(up.rect())
                got.update(window=window[0].width(), tree=trees[0].width(),
                           shown=seen_of.width())
            elif time.time() - seen["since"] > 60:
                got["error"] = "%s stood still for 60 s, waiting for %s" % (
                    case, step)
            else:
                QtCore.QTimer.singleShot(50, look)
                return
            for w in window:
                w.close()
            app.exit(vpm.LANGUAGE_AGAIN)

        QtCore.QTimer.singleShot(0, look)
        vpm.gui()
        print("NARROW " + json.dumps(got), flush=True)
        if "error" in got:
            return


# -------------------------------------------------------------- the parent
app = vpm = QtCore = QtGui = QtWidgets = None
# What narrowest_windows found, by (language, font); read by tree_room.
NARROW = {}


def begin():
    """Qt offscreen and the program loaded, in the test's own process."""
    global app, vpm, QtCore, QtGui, QtWidgets
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from PySide6 import QtCore, QtGui, QtWidgets
    app = QtWidgets.QApplication(sys.argv[:1])
    vpm = the_program.load()
    return vpm


def narrowest_windows(languages):
    """What the real window keeps dragged small, per language and font.

    Not a number read out of the source: the window takes its least size
    from its layout, which the language and the font move. The cases are
    shared out over a few children, each building the window again per
    case; a case that never came back is simply missing from the answer.
    """
    cases = ["%s:%d" % (l, s) for s in FONTS for l in languages]
    many = max(1, min(8, os.cpu_count() or 1, len(cases)))
    # Into a file each, not a pipe: a pipe nobody reads yet fills, and
    # the child writing into it waits for the ones before it to finish.
    logs = [tempfile.TemporaryFile("w+", encoding="utf-8")
            for _k in range(many)]
    started = [subprocess.Popen(
        [sys.executable, os.path.abspath(__file__)], cwd=HERE,
        stdout=logs[k], stderr=subprocess.STDOUT,
        env=dict(os.environ, VPM_NARROW_CASES=" ".join(cases[k::many])))
        for k in range(many)]
    trouble = []
    NARROW.clear()
    for child, log in zip(started, logs):
        child.wait()
        log.seek(0)
        out = log.read()
        log.close()
        for line in out.splitlines():
            if not line.startswith("NARROW "):
                continue
            got = json.loads(line[len("NARROW "):])
            if "error" in got:
                trouble.append(got["error"])
            else:
                language, stretch = got["case"].split(":")
                NARROW[(language, int(stretch))] = got
        if child.returncode:
            trouble.append("a child ended with %d: %s" % (
                child.returncode, " / ".join(out.splitlines()[-2:])[:200]))
    missing = [c for c in cases
               if (c.split(":")[0], int(c.split(":")[1])) not in NARROW]
    return cases, missing, trouble


def tree_room(language, stretch):
    """How much of the tree the narrowest window shows, or the screen.

    The screen stands in only for a case that was not measured; the
    first check says which those are, and is red for them.
    """
    got = NARROW.get((language, stretch))
    return got["shown"] if got else SCREEN[0]


def in_a_wider_font(times):
    """Draw everything from here on in a font that much wider."""
    was = QtWidgets.QApplication.font()
    wide = QtGui.QFont(was)
    wide.setStretch(times)
    QtWidgets.QApplication.setFont(wide)
    return was


def sheet(width):
    """The assignment tree with three Speakers cells in it.

    Built the way assignment_fresh builds it: the rows first with
    empty cells, the columns measured, and only then the text -- which
    is the order that made the cell unreadable.
    """
    columns = [vpm.T('Audio recording'), vpm.T('Speaker name'),
               vpm.T('belongs to'), "Timecode", vpm.T('Speakers')]
    tree = vpm.tree_build(columns)
    cells, nodes = [], []
    for _i in range(3):
        node = vpm.tree_row(tree, None, [os.path.basename(PATH)])
        vpm.tree_field(tree, node, 1, QtWidgets.QLineEdit())
        box, cell = vpm.split_cell_build(PATH, lambda *_: None, node[4])
        vpm.tree_field(tree, node, 4, box)
        cells.append(cell)
        nodes.append(node)
    holder = QtWidgets.QWidget()
    rows = QtWidgets.QVBoxLayout(holder)
    rows.setContentsMargins(0, 0, 0, 0)
    rows.addWidget(tree, 1)
    holder.resize(width, 700)
    for c in range(len(columns)):
        tree.resizeColumnToContents(c)
    tree.setColumnWidth(0, max(220, tree.columnWidth(0) + 30))
    vpm.split_column_fit(tree, 4)
    holder.show()
    app.processEvents()
    return holder, tree, cells, nodes


def written(cells, text="", busy=False, found=0):
    """Fill the cells the way the window fills them, and no other way.

    Through split_cells_write itself, so the captions are the
    program's and not the test's: *text* arrives as the note hung on a
    recording, *busy* as a separation running on it, *found* as voices
    already stored for it. Nothing is laid out by hand afterwards --
    in the running program nobody does that either.
    """
    by_source = vpm.ByFile()
    if found:
        by_source[PATH] = {"segments": [("Speaker %d" % (i + 1), [])
                                        for i in range(found)]}
    note = (os.path.abspath(PATH), text, "#888888") if text else None
    vpm.split_cells_write(cells, busy, PATH if busy else "",
                          by_source, note)
    app.processEvents()


def unreadable(mark):
    """How many pixels of the text do not fit, in either direction.

    A wrapping label is cut at the top: it makes as many lines as it
    needs and the row shows the last of them. One that does not wrap
    is cut at the right instead. The height it needs is worked out
    here by the font's own bounding box for a wrapped paragraph --
    a different road from the heightForWidth the program asks, so the
    judgement is not the program's arithmetic handed back to it.
    """
    if not mark.wordWrap():
        return mark.sizeHint().width() - mark.width()
    from PySide6 import QtCore
    box = mark.fontMetrics().boundingRect(
        QtCore.QRect(0, 0, max(1, mark.width()), 0),
        QtCore.Qt.TextWordWrap, mark.text())
    return box.height() - mark.height()


def needs(mark):
    """The height the wrapped text needs at the width the label has."""
    from PySide6 import QtCore
    return mark.fontMetrics().boundingRect(
        QtCore.QRect(0, 0, max(1, mark.width()), 0),
        QtCore.Qt.TextWordWrap, mark.text()).height()


def one_line(mark):
    """The height of the label's text on one line, in the faces drawing it.

    Not the font's own line height: a script the font lacks is drawn in
    another face, and one line of Arabic stands 30 px tall where the
    interface font's line is 15 -- measured here, over every language.
    A line break written into the text is taken out: that is two lines.
    """
    from PySide6 import QtCore
    return mark.fontMetrics().boundingRect(
        QtCore.QRect(0, 0, 100000, 0), QtCore.Qt.TextWordWrap,
        mark.text().replace("\n", " ")).height()


def named(rows, form):
    """For the line: the languages over, or the one nearest its edge.

    A line naming every language would bury the one that fell, so the
    ones over are named -- and where none is, the closest, so a line
    that passes still says how near it came.
    """
    over = [r for r in rows if r[1] > 0]
    shown = over or sorted(rows, key=lambda r: -r[1])[:1]
    return "%d of %d over; %s" % (len(over), len(rows),
                                  ", ".join(form % r for r in shown))


def missing_caption():
    """The sentence the cell shows where no separation is set up."""
    return vpm.T('The speaker separation is not set up.')


def reported_caption():
    """The longest the cell can be made to show.

    split_cells_write takes the first line of what the separation
    reported and cuts that to 200 characters, so short captions are
    not the whole of what has to fit in there. Cut to the same 200
    here, so the longest case really is the one being measured.
    """
    return (vpm.T('The speaker separation reports: %s') % (
        "ImportError: Can't determine version for bottleneck, raised "
        "while the pipeline that tells voices apart was being built "
        "out of the models lying beside the program"))[:200]


# ------------------------------------------------------------ the sections
# Each hands back rows the test judges; the first field of a row is the
# language, the second how far it is out -- over nought is a fault.
def column_holds(languages):
    """Per language: the column against the running caption and button,
    and against the finished count, at the narrowest window at our font."""
    running_rows, counted_rows = [], []
    for language in languages:
        vpm.set_language(language)
        holder, tree, cells, nodes = sheet(tree_room(language, 100))
        room = tree.columnWidth(4)
        face = cells[0][2].fontMetrics()
        button_wide = cells[0][1].sizeHint().width()
        running = face.horizontalAdvance(vpm.T('Separating ...'))
        counted = face.horizontalAdvance(vpm.TN(
            2, 'Separated: %s speaker', 'Separated: %s speakers') % 2)
        running_rows.append((language, running + button_wide - room, room,
                             running, button_wide))
        counted_rows.append((language, counted - room, room, counted))
        holder.deleteLater()
    return running_rows, counted_rows


def rows_follow(languages):
    """Per language: the row grows to a wrapped text, and comes back down.

    Growing is asked only where the sentence really wraps at that width:
    in a script that draws it on one line there is nothing to grow for.
    """
    grows, back = [], []
    for language in languages:
        vpm.set_language(language)
        holder, tree, cells, nodes = sheet(tree_room(language, 100))
        seat = cells[0][3]
        written(cells)
        empty_row = tree.rowHeight(seat.index())
        written(cells, missing_caption())
        tall_row = tree.rowHeight(seat.index())
        wraps = needs(cells[0][2]) > one_line(cells[0][2])
        written(cells)
        back_row = tree.rowHeight(seat.index())
        if wraps:
            grows.append((language, empty_row - tall_row + 1, tall_row,
                          empty_row))
        back.append((language, back_row - empty_row, back_row, empty_row))
        holder.deleteLater()
    return grows, back


def readable(languages):
    """Per language, everything the cell can show, at our font."""
    over = {"missing": [], "running": [], "counted": [], "reported": [],
            "button": [], "asked": []}
    for language in languages:
        vpm.set_language(language)
        holder, tree, cells, nodes = sheet(tree_room(language, 100))
        _path, button, mark, _item = cells[0]
        written(cells, missing_caption())
        over["missing"].append((language, unreadable(mark), mark.width(),
                                mark.height()))
        written(cells, busy=True)
        over["running"].append((language,
                                needs(mark) - one_line(mark),
                                mark.width(), needs(mark)))
        over["button"].append((language,
                               button.sizeHint().width() - button.width(),
                               button.width(), button.sizeHint().width()))
        written(cells, found=2)
        over["counted"].append((language,
                                needs(mark) - one_line(mark),
                                mark.width(), needs(mark)))
        written(cells, reported_caption())
        over["reported"].append((language, unreadable(mark), mark.width(),
                                 mark.height()))
        over["asked"].append((language, needs(mark) - mark.minimumHeight(),
                              mark.minimumHeight(), needs(mark)))
        holder.deleteLater()
    return over


def readable_wide(languages):
    """The same again in the widest font we build for."""
    was_font = in_a_wider_font(WIDER)
    far = {"reported": [], "missing": [], "running": []}
    try:
        for language in languages:
            vpm.set_language(language)
            holder, tree, cells, nodes = sheet(tree_room(language, WIDER))
            _path, button, mark, _item = cells[0]
            written(cells, reported_caption())
            far["reported"].append((language, unreadable(mark),
                                    mark.width(), mark.height()))
            written(cells, missing_caption())
            far["missing"].append((language, unreadable(mark), mark.width(),
                                   mark.height()))
            written(cells, busy=True)
            far["running"].append((language,
                                   needs(mark) - one_line(mark),
                                   mark.width(), needs(mark)))
            holder.deleteLater()
    finally:
        QtWidgets.QApplication.setFont(was_font)
    return far


def squeezed(languages):
    """Per language and font: the far column scrolled to, and the name.

    What is asked changed once the name column stopped stretching. It
    used to be that nothing had to be scrolled sideways -- only true
    because the name field gave way, down to 79 px on the Windows
    builder. Room for the name comes first now, and the tree scrolls, so
    what is asked is that the scrolling reaches the far column, where the
    button to break a separation off sits. Swept over the fonts, because
    it is the middle that hurts: the window a little too narrow for what
    is in it, which is where the Windows builder sits.
    """
    narrow = []
    was_font = QtWidgets.QApplication.font()
    try:
        for how_wide in FONTS:
            in_a_wider_font(how_wide)
            for language in languages:
                vpm.set_language(language)
                holder, tree, cells, nodes = sheet(
                    tree_room(language, how_wide))
                written(cells, missing_caption())
                # Scrolled the whole way over: what is asked is that the
                # far column really stands inside the viewport there.
                bar = tree.horizontalScrollBar()
                bar.setValue(bar.maximum())
                app.processEvents()
                head = tree.header()
                narrow.append(("%s at %d%%" % (language, how_wide),
                               head.sectionViewportPosition(4),
                               tree.columnWidth(4),
                               tree.viewport().width(),
                               tree.columnWidth(1)))
                holder.deleteLater()
    finally:
        QtWidgets.QApplication.setFont(was_font)
    return narrow


def stays_open(languages):
    """Per language: a recording with voices under it, open before and after.

    The height of a row is put right by laying the items out again, which
    must not fold the tree up under the hand that opened it.
    """
    rows = []
    for language in languages:
        vpm.set_language(language)
        holder, tree, cells, nodes = sheet(tree_room(language, 100))
        vpm.tree_row(tree, nodes[0], ["Speaker 1"])
        tree.setExpanded(nodes[0][0].index(), True)
        was_open = tree.isExpanded(nodes[0][0].index())
        written(cells, missing_caption())
        now_open = tree.isExpanded(nodes[0][0].index())
        rows.append((language, 0 if was_open and now_open else 1,
                     was_open, now_open))
        holder.deleteLater()
    return rows


if __name__ == "__main__" and os.environ.get("VPM_NARROW_CASES"):
    narrow_child(os.environ["VPM_NARROW_CASES"].split())
