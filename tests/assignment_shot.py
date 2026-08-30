# -*- coding: utf-8 -*-
"""Shot of the assignment sheet: the tree of voices and the cameras."""
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtWidgets, QtCore, QtGui
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
sys.path.insert(0, HERE)
from fixture_project import fixture_project
PROJECT, SRC = fixture_project("assignshot")
OUT = os.environ.get("VPM_SHOTS") or os.path.join(HERE, "shots"); os.makedirs(OUT, exist_ok=True)
if PROJECT is None:
    print("SKIPPED: no test media -- point VPM_MEDIA at a folder "
          "holding videopodcast-magic_Interview_2.json")
    raise SystemExit(0)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (PROJECT, ""))

# What went wrong, collected rather than raised: an exception inside a
# timer callback leaves the event loop half way and the return code is
# whatever Qt makes of it. The code is set once at the bottom.
bad = []
# Whether the last step was reached. The clock at the bottom stops the
# window in the end, which otherwise reads as a finished run.
through = [False]


def fail(why):
    """Say what is missing, and remember that the run is red."""
    print("FAIL:", why)
    bad.append(why)


def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x
def button(t):
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(t): return w


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
    """Switch to the sheet whose title contains *s*, or stop.

    Silence would mean photographing the wrong sheet and returning 0.
    """
    tw, k = sheet_of(s)
    if tw is None:
        fail("no sheet is called %r. There are: %s" % (s, sheet_names()))
        app.quit()
        return False
    tw.setCurrentIndex(k); app.processEvents(); return True


# ------------------------------------------------- reading what is shown
def views():
    """Every list on the screen, whatever furniture it is made of.

    Asked of the view and its model, not of one widget class: a lookup
    for QTableWidget found the camera table and said nothing at all
    about the tree this script is named after. Header rows answer out
    of the same model, and a drop-down's popup is not a list on the
    sheet, so both are left out.
    """
    return [v for v in win().findChildren(QtWidgets.QAbstractItemView)
            if v.isVisible() and not isinstance(v, QtWidgets.QHeaderView)
            and v.window() is win()]


def widget_text(w):
    """What a widget standing in a cell says, asked rather than recognised.

    A cell may hold more than the bare drop-down a test recognised, and
    the reading then came away with an empty string. So whatever can be
    asked for its text is asked, and a widget built out of others is
    asked of the parts it is built from.
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
    """The column names of a view, out of its model."""
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


def with_column(lists, name):
    """The list carrying a column of that name, or None."""
    for head, rows in lists:
        if name in head:
            return head, rows
    return None


def blank(picture):
    """One colour from edge to edge: nothing was drawn on it."""
    if picture.isNull() or picture.width() < 2 or picture.height() < 2:
        return True
    image = picture.toImage().convertToFormat(QtGui.QImage.Format_RGB32)
    raw = bytes(image.constBits())
    return raw == raw[:4] * (len(raw) // 4)


def keep(picture, name):
    """Write a picture out -- and where there is nothing on it, do not.

    A picture nobody wrote this run is worse than none: the file from
    the last run lies there looking current.
    """
    path = os.path.join(OUT, name + ".png")
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
holding = [None]

# What each step may spend waiting: milliseconds between tries, and how
# many tries. The clock at the bottom is their sum, so it can no longer
# end the run before the step it is guarding has said which condition
# never came true -- which is the whole point of these waits.
WAITS = {"the window": (100, 100),
         "the Open project button": (150, 120),
         "the Multitrack tick": (150, 120),
         "the assignment sheet": (150, 120),
         "the two lists of the assignment sheet": (150, 240)}
# Ten seconds on top of the waits: between them the steps hop 50 ms
# apart and do their own work -- loading, drawing, grabbing a picture.
DEADLINE = sum(ms * tries for ms, tries in WAITS.values()) + 10000


def hold(ok, what):
    """Wait for a condition instead of waiting for the clock.

    The step comes back every few milliseconds until <ok> is true, as
    often as WAITS allows, so a slow machine only takes longer while an
    interface that never gets there still gives up. Giving up is a
    defect and says so, or the shot is of whatever was on the screen.
    """
    ms, limit = WAITS[what]
    if ok:
        waited[0] = 0
        holding[0] = None
        return False
    if waited[0] >= limit:
        waited[0] = 0
        holding[0] = None
        fail("waited %.1f s for %s, and it never came"
             % (limit * ms / 1000.0, what))
        app.quit()
        return True
    waited[0] += 1
    holding[0] = what
    n[0] -= 1
    QtCore.QTimer.singleShot(ms, step)
    return True


def showing(text):
    """Is a line beginning with that text on the screen?"""
    return any(w.isVisible() and w.text().startswith(text)
               for w in win().findChildren(QtWidgets.QLabel))


def built():
    """The project is in, so the sheet it fills is there.

    Asked of the window, which puts that sheet in once there are files:
    the file list on the sheet in front has rows too, so asking a table
    for rows was already true while page one was still on top.
    """
    return sheet_of(vpm.T('Assignment && time window')[:9])[0] is not None


def working():
    """A bar in the window says something is still running.

    The prework bar stands while the envelopes are read, the footer bar
    while anything runs and for a moment after, so that the end is
    seen. Both are in the picture, so the shot waits until they go.
    """
    return any(b.isVisible()
               for b in win().findChildren(QtWidgets.QProgressBar))


TREE = lambda: vpm.T('Audio recording')
CAMERAS = lambda: vpm.T('Camera')


def ready():
    """Everything the picture and the printout need is done.

    Both lists this sheet is about hold rows, nothing runs in the
    background any more -- the time axis is measured in a thread and
    only its end writes the Timecode column -- and everything reads the
    same twice in a row, so nothing arrives late.
    """
    now = reading()
    was, before[0] = before[0], now
    wanted = [with_column(now, TREE()), with_column(now, CAMERAS())]
    return (all(w is not None and w[1] for w in wanted)
            and now == was
            and not showing(vpm.T('Measuring time axis ...'))
            and not working())


def show(head, rows, name):
    """Print one list, with what hangs under a row indented under it."""
    print("%s: %s" % (name, " | ".join(head)))
    for depth, cells in rows:
        print("   " + "    " * depth + " | ".join(cells))
    return rows


def step():
    i = n[0]; n[0] += 1
    try:
        if i == 0:
            if hold(win() is not None, "the window"): return
            win().show(); win().resize(1500, 1050); app.processEvents()
        elif i == 1:
            if hold(button(vpm.T('Open project ...')[:8]) is not None,
                    "the Open project button"): return
            button(vpm.T('Open project ...')[:8]).click()
        elif i == 2:
            # The tick only wakes up once the project is loaded.
            multitrack = vpm.T('Multitrack (one track per speaker)')
            boxes = [cb for cb in win().findChildren(QtWidgets.QCheckBox)
                     if cb.text().startswith(multitrack)]
            if hold(any(cb.isEnabled() for cb in boxes),
                    "the Multitrack tick"): return
            for cb in boxes:
                if cb.isEnabled():
                    cb.setChecked(True)
        elif i == 3:
            if hold(built(), "the assignment sheet"): return
            if not tab(vpm.T('Assignment && time window')[:9]): return
        elif i == 4:
            if hold(ready(), "the two lists of the assignment sheet"): return
            app.processEvents()
            keep(win().grab(), "assignment")
            lists = reading()
            tree = with_column(lists, TREE())
            cameras = with_column(lists, CAMERAS())
            if tree is None:
                fail("no list on this sheet has a %r column -- the "
                     "assignment tree is not in the picture. Columns "
                     "found: %s" % (TREE(), [h for h, _r in lists]))
            else:
                rows = show(tree[0], tree[1], "Tree")
                under = sum(1 for d, _c in rows if d)
                print("Tree rows: %d, of them %d under a recording"
                      % (len(rows), under))
            if cameras is None:
                fail("no list on this sheet has a %r column -- the "
                     "camera table is not in the picture. Columns "
                     "found: %s" % (CAMERAS(), [h for h, _r in lists]))
            else:
                head, rows = cameras
                show(head, rows, "Cameras")
                # The two columns that came out empty once the cell held
                # more than a bare drop-down. An empty column is the
                # whole defect, so it is counted, not eyeballed.
                for column in (vpm.T('Kind'), vpm.T('Camera audio')):
                    if column not in head:
                        fail("the camera table has no %r column" % column)
                        continue
                    c = head.index(column)
                    full = sum(1 for _d, cells in rows if cells[c].strip())
                    print("Camera table %r: %d of %d rows filled"
                          % (column, full, len(rows)))
                    if rows and not full:
                        fail("the %r column is empty in every row" % column)
            through[0] = True
            print("\ndone"); app.quit(); return
    except Exception:
        import traceback; traceback.print_exc()
        fail("the run threw"); app.quit(); return
    QtCore.QTimer.singleShot(50, step)

QtCore.QTimer.singleShot(50, step)
QtCore.QTimer.singleShot(DEADLINE, app.quit)
sys.argv = ["videopodcast-magic.py"]
code = vpm.gui()
if not through[0] and not bad:
    # Naming the step and what it was waiting for: on another machine
    # only what stands in this line exists.
    doing = ("waiting for %s" % holding[0]) if holding[0] else "at work"
    fail("the run was stopped after %.0f s at step %d, %s"
         % (DEADLINE / 1000.0, n[0], doing))
if bad:
    print("\n%d thing(s) went wrong:" % len(bad))
    for line in bad:
        print("  -", line)
# What gui() gives back is what Qt's event loop gave back, and that is
# not a statement about the pictures: it has come back as 1 with every
# step reached and no check failed. So the checks decide, and the
# number is said out loud rather than obeyed.
if code and through[0] and not bad:
    print("NOTE: the window returned %s although every step was reached "
          "and nothing was found wanting." % code)
# The last line, whatever happens. This script has come back with a 1
# and no traceback, no FAIL of its own and no line about a step it
# missed. If this line is missing, the process did not get here: it was
# killed or left through a door nobody knows about.
print("END: through=%s bad=%d loop=%s" % (through[0], len(bad), code),
      flush=True)
raise SystemExit(1 if bad or not through[0] else 0)
