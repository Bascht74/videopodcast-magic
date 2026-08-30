# -*- coding: utf-8 -*-
"""Shots of the Resolve cut tab -- lists, speaker box, preview."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import re, sys, importlib.util
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("VPM_SILENT", "1")   # never beep at a person
from PySide6 import QtWidgets, QtCore, QtGui
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
# No network and no real key for a screenshot: the two functions the
# interface would call for that are stubbed out. (list_presets returns
# (name, uuid, multitrack) triples; load_api_key returns the stored key.)
vpm.list_presets = lambda key: [("Podcast_Multitrack", "u1", True),
                                ("Podcast_Zoom", "u2", False)]
vpm.load_api_key = lambda: "not-a-real-key"
sys.path.insert(0, HERE)
from fixture_project import fixture_project
PROJECT, SRC = fixture_project("previewshot")
OUT = os.environ.get("VPM_SHOTS") or os.path.join(HERE, "shots")
os.makedirs(OUT, exist_ok=True)
if PROJECT is None:
    print("SKIPPED: no test media -- point VPM_MEDIA at a folder "
          "holding videopodcast-magic_Interview_2.json")
    raise SystemExit(0)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (PROJECT, ""))

# What went wrong, collected rather than raised: an exception inside a
# timer callback leaves the event loop half way and the return code is
# whatever Qt makes of it. Every complaint lands here, the loop is
# stopped, and the code is set once at the bottom. This script ran for
# 39 seconds and came back green while writing one of its two pictures.
bad = []
# Whether the last step was reached. The clock at the bottom stops the
# window after a minute whatever happens, and without this that looked
# like a run that had finished.
through = [False]


def fail(why):
    """Say what is missing, and remember that the run is red."""
    print("FAIL:", why)
    bad.append(why)


def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x

def button(text):
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(text):
            return w

def boxes():
    return win().findChildren(QtWidgets.QGroupBox)

def box_titles():
    return [w.title() for w in boxes() if w.isVisible()]

def group(title):
    for w in boxes():
        if w.title().startswith(title):
            return w


def like(template):
    """A test for a title the program builds out of a template.

    The pieces around the %s are the same in every case and in both
    languages, because the template comes out of the catalogue; only
    what is put in changes.
    """
    return re.compile("^" + "(.*)".join(
        re.escape(p) for p in template.split("%s")) + "$")


def preview_box():
    """The box holding the preview, found by the shape of its name.

    It was looked for under "Camera cut -- preview" until now. No box
    has carried that name since 2.7.0-beta: the box says what kind of
    cut this is, and that is one of three -- camera cut, cut with the
    wide shot, first cut by speaker -- and once the cut is computed the
    length is on the end as well.

    It went on working in English all the same, and that is why nobody
    saw it: there is no catalogue entry for "Camera cut -- preview", so
    in English the lookup handed the phrase back and it happens to be
    the beginning of "Camera cut -- preview  (length ...)". Measured on
    25.8.2026: the English run took 3.1 seconds and wrote the picture,
    the German run took 38.8 seconds, wrote no picture and came back
    with 0. Whoever ran it in German kept the English picture from
    somebody else's run, looking new. And the two cases the English
    title does not begin that way -- the wide shot and the first cut by
    speaker -- were blind in both languages.

    Not one of the three names then, and not a guess: the two
    templates the window itself builds the title from, with the part
    that changes left open.
    """
    shapes = [like(vpm.T('%s -- preview  (length %s)')),
              like(vpm.T('%s -- preview'))]
    for w in boxes():
        if any(s.match(w.title()) for s in shapes):
            return w


def speaker_box():
    return group(vpm.T('Speaker'))


def sheet_of(s):
    """The tab holding the sheet whose title contains *s*, and its place."""
    for tw in win().findChildren(QtWidgets.QTabWidget):
        for k in range(tw.count()):
            if s.lower() in tw.tabText(k).lower():
                return tw, k
    return None, None


def sheet_names():
    return [tw.tabText(k) for tw in win().findChildren(QtWidgets.QTabWidget)
            for k in range(tw.count())]


def tab(s):
    """Switch to the sheet whose title contains *s*.

    It used to return in silence where nothing matched, and the script
    then carried on photographing the wrong sheet -- with a return code
    of 0, so nothing anywhere went red. When the tab names lost their
    numbers on 23.8.2026 that is exactly what happened. A lookup that
    finds nothing is a defect, and says so.
    """
    tw, k = sheet_of(s)
    if tw is None:
        fail("no sheet is called %r. There are: %s" % (s, sheet_names()))
        app.quit()
        return False
    tw.setCurrentIndex(k); app.processEvents(); return True


# ------------------------------------------------- reading what is shown
def lists(under=None, shown=True):
    """The lists of the window, or of one sheet, whatever they are made of.

    Asked of the view and its model, not of one widget class: a lookup
    for QTableWidget found nothing on this sheet and printed nothing at
    all, and it asked the header for an item of its own, which is not
    there in a list built over a model.

    Two kinds are left out. Header rows are views in their own right
    and answer out of the same model, so they would say everything a
    second time. And every drop-down keeps a list of its own in a
    popup: that is not a list on the sheet, and which window a view
    belongs to says which of the two it is.
    """
    root = under if under is not None else win()
    out = []
    for v in root.findChildren(QtWidgets.QAbstractItemView):
        if isinstance(v, QtWidgets.QHeaderView) or v.window() is not win():
            continue
        if shown and not v.isVisible():
            continue
        out.append(v)
    return out


def views():
    """The lists on the screen."""
    return lists()


def widget_text(w):
    """What a widget standing in a cell says, asked rather than recognised.

    Nothing is recognised here: whatever can be asked for its text is
    asked, and a widget built out of others is asked of the parts it is
    built from -- a cell that used to be a bare drop-down and is a
    drop-down with a note beside it now reads either way.
    """
    for ask in ("currentText", "text", "toPlainText"):
        answer = getattr(w, ask, None)
        if callable(answer):
            try:
                said = answer()
            except Exception:
                said = None
            if isinstance(said, str):
                return said.strip()
    parts = [widget_text(k) for k in w.children()
             if isinstance(k, QtWidgets.QWidget) and not k.isHidden()]
    return "  ".join(p for p in parts if p)


def head_of(view):
    """The column names of a view, out of its model.

    Out of the model and not out of a header item: a list built over a
    model has no items of its own, and asking one for its text is the
    kind of thing that goes bang on the day it turns up.
    """
    model = view.model()
    if model is None:
        return []
    return [str(model.headerData(c, QtCore.Qt.Horizontal) or "")
            for c in range(model.columnCount(QtCore.QModelIndex()))]


def rows_of(view, under=None, depth=0):
    """Every row of a view and everything hanging under it, cell by cell.

    A flat list is a tree with nothing under its rows, so one reading
    serves both.
    """
    model = view.model()
    if model is None:
        return []
    root = under if under is not None else QtCore.QModelIndex()
    out = []
    wide = model.columnCount(root)
    for r in range(model.rowCount(root)):
        cells = []
        for c in range(wide):
            where = model.index(r, c, root)
            inside = view.indexWidget(where)
            cells.append(widget_text(inside) if inside is not None
                         else str(model.data(where) or ""))
        out.append((depth, cells))
        out += rows_of(view, model.index(r, 0, root), depth + 1)
    return out


def reading():
    """Every visible list with its columns and its rows."""
    return [(head_of(v), rows_of(v)) for v in views()]


def blank(picture):
    """One colour from edge to edge: nothing was drawn on it."""
    if picture.isNull() or picture.width() < 2 or picture.height() < 2:
        return True
    image = picture.toImage().convertToFormat(QtGui.QImage.Format_RGB32)
    raw = bytes(image.constBits())
    return raw == raw[:4] * (len(raw) // 4)


def shot(name, w=None):
    """Take one picture -- and where there is nothing on it, do not keep it.

    A picture nobody wrote this run is worse than no picture: the file
    from the last run lies there looking current, and that is what
    B_Camera.png did for as long as the box could not be found. So a
    grab with nothing on it takes the old file with it and says so.
    """
    path = os.path.join(OUT, name + ".png")
    f = win(); f.resize(1600, 1150); app.processEvents()
    picture = (w or f).grab()
    if blank(picture):
        if os.path.exists(path):
            os.remove(path)
        fail("nothing is on the picture for %s -- the file is gone, "
             "not left standing from an earlier run" % name)
        return False
    picture.save(path)
    print("  -> %s  %dx%d" % (name, picture.width(), picture.height()))
    return True


n = [0]
waited = [0]
before = [None]


def hold(ok, what, ms=150, limit=200):
    """Wait for a condition instead of waiting for the clock.

    The step comes back every <ms> milliseconds until <ok> is true, at
    most <limit> times -- more than ten times the pause that stood here
    before, so a slow machine only takes longer and is not called red,
    while an interface that never gets there still gives up.

    Giving up is a defect and says so. It used to let the step carry on
    as though the wait had worked: the run then sat out 37.5 seconds,
    photographed the sheet anyway and came back green.
    """
    if ok:
        waited[0] = 0
        return False
    if waited[0] >= limit:
        waited[0] = 0
        fail("waited %.1f s for %s, and it never came"
             % (limit * ms / 1000.0, what))
        app.quit()
        return True
    waited[0] += 1
    n[0] -= 1
    QtCore.QTimer.singleShot(ms, step)
    return True


def showing(text):
    """Is a line beginning with that text on the screen?"""
    return any(w.isVisible() and w.text().startswith(text)
               for w in win().findChildren(QtWidgets.QLabel))


def built():
    """The project is in, so the sheet it fills is there.

    Asked of the window, which puts that sheet in once there are files
    and takes it out again when there are none. It used to be asked of
    the rows of a table, which tied this script to the assignment being
    made of tables -- and it stopped being made of tables.
    """
    return sheet_of(vpm.T('Resolve cut'))[0] is not None


def fetching():
    """A still out of a video file is on its way.

    The player fetches the picture it shows in a thread. Taking the
    shot before it arrives would photograph the picture from before.
    """
    return any(getattr(w, "_still_running", False)
               for w in win().findChildren(QtWidgets.QWidget))


def working():
    """A bar in the window says something is still running.

    The prework bar stands there while the envelopes are read, the
    footer bar while anything runs -- and after that it stays full for
    another second and a half so that the end is seen, before it goes
    away by itself. Both are in the picture, so the shot waits until
    they have gone.
    """
    return any(b.isVisible()
               for b in win().findChildren(QtWidgets.QProgressBar))


def ready():
    """Everything the pictures and the printout need is done.

    Both boxes stand on the screen, the time axis is measured -- it
    runs in a thread and moves the player when it lands -- no still is
    on its way, and boxes and lists read the same twice in a row, so
    the layout has come to rest.
    """
    two = [speaker_box(), preview_box()]
    now = ([(b.isVisible(), b.height(), b.width()) if b else None
            for b in two], reading())
    was, before[0] = before[0], now
    return (all(b is not None and b.isVisible() for b in two)
            and now == was and not fetching()
            and not showing(vpm.T('Measuring time axis ...'))
            and not working())


def step():
    i = n[0]; n[0] += 1
    try:
        if i == 0:
            if hold(win() is not None, "the window", 100, 120): return
            win().show(); app.processEvents()
        elif i == 1:
            k = button(vpm.T('Open project ...')[:8])
            if hold(k is not None, "the Open project button"): return
            print("Load button:", bool(k)); k.click()
        elif i == 2:
            # The tick only wakes up once the project is loaded: that is
            # what the pause here used to sit out.
            multitrack = vpm.T('Multitrack (one track per speaker)')
            ticks = [cb for cb in win().findChildren(QtWidgets.QCheckBox)
                     if cb.text().startswith(multitrack)]
            if hold(any(cb.isEnabled() for cb in ticks),
                    "the Multitrack tick"): return
            for cb in ticks:
                print("Multitrack:", cb.isEnabled(), cb.isChecked())
                if cb.isEnabled() and not cb.isChecked():
                    cb.setChecked(True)
        elif i == 3:
            if hold(built(), "the Resolve cut sheet"): return
            if not tab(vpm.T('Resolve cut')): return
        elif i == 4:
            if hold(ready(), "the speaker box and the preview box",
                    150, 250): return
            shot("A_tab")
            # The name of the picture stays English, the lookup does
            # not: the window carries the translated title, and the
            # preview carries the name of whichever cut this is.
            for name, gb in (("Speaker", speaker_box()),
                             ("Camera", preview_box())):
                if gb is None:
                    fail("there is no %s box on this sheet. The boxes "
                         "here are: %s" % (name, box_titles()))
                    continue
                print("%s box %r" % (name, gb.title()))
                shot("B_" + name, gb)
                print(name, "height", gb.height(), "width", gb.width())
            # Every list this sheet holds, the hidden ones as well. The
            # speaker table is hidden while no speakers are known --
            # that is the window saying so, and printing nothing at all
            # cannot be told apart from a script that stopped finding
            # it. Gone altogether is the defect, and that is what fails.
            tw, k = sheet_of(vpm.T('Resolve cut'))
            page = tw.widget(k) if tw is not None else None
            here = lists(page, shown=False)
            if not here:
                fail("this sheet holds no list at all -- the speaker "
                     "table is not there")
            for view in here:
                head, rows = head_of(view), rows_of(view)
                wide = getattr(view, "columnWidth", None)
                print("List:", " | ".join(head),
                      "--", "on the screen" if view.isVisible()
                      else "hidden", "rows", len(rows),
                      "widths", [wide(c) for c in range(len(head))]
                      if callable(wide) else "-",
                      "Viewport", view.viewport().width())
                for _depth, cells in rows:
                    print("   " + " | ".join(cells))
            through[0] = True
            print("\ndone"); app.quit(); return
    except Exception:
        import traceback; traceback.print_exc()
        fail("the run threw"); app.quit(); return
    QtCore.QTimer.singleShot(50, step)

QtCore.QTimer.singleShot(50, step)
QtCore.QTimer.singleShot(60000, app.quit)
sys.argv = ["videopodcast-magic.py"]
code = vpm.gui()
if not through[0] and not bad:
    fail("the window closed before the last step -- the minute ran out")
if bad:
    print("\n%d thing(s) went wrong:" % len(bad))
    for line in bad:
        print("  -", line)
raise SystemExit(1 if bad else (code or 0))
