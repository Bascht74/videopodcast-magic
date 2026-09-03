# -*- coding: utf-8 -*-
"""Shots of the Resolve cut tab -- lists, speaker box, preview."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import re, sys, time, importlib.util
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("VPM_SILENT", "1")   # never beep at a person
from PySide6 import QtWidgets, QtCore, QtGui
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
# No network and no real key for a screenshot. list_presets returns
# (name, uuid, multitrack) triples; load_api_key returns the stored key.
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
# whatever Qt makes of it. The code is set once at the bottom instead.
bad = []
# Whether the last step was reached: the clock at the bottom stops the
# window whatever happens, which without this looks like a finished run.
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

    The pieces around the %s come out of the catalogue and are the same
    in both languages; only what is put in changes.
    """
    return re.compile("^" + "(.*)".join(
        re.escape(p) for p in template.split("%s")) + "$")


def preview_box():
    """The box holding the preview, found by the shape of its name.

    Not by a fixed title: the box says which of the three kinds of cut
    this is, and once the cut is computed the length is on the end. A
    fixed English title even goes on matching, because a phrase with no
    catalogue entry is handed back unchanged, so a stale lookup fails in
    German only.
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

    A lookup that finds nothing is a defect and says so: in silence the
    script photographs the wrong sheet and comes back with a 0.
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
    for QTableWidget finds nothing on a list built over a model. Header
    rows answer out of the same model and would say everything twice,
    and a drop-down's popup is not a list on the sheet, so both go.
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
    return lists()


def widget_text(w):
    """What a widget standing in a cell says, asked rather than recognised.

    Whatever can be asked for its text is asked, and a widget built out
    of others is asked of its parts, so a cell that grew a note beside
    its drop-down still reads.
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

    A list built over a model has no header items of its own, and asking
    one for its text goes bang on the day such a list turns up.
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

    A picture nobody wrote this run is worse than none: the file from
    the last run lies there looking current. So a grab with nothing on
    it takes the old file with it and says so.
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
before = [None]
holding = [None]
# What a wait has to show for itself when it gives up: how much
# standstill it has eaten, how often the window moved, how long it took.
watch = {"sign": None, "idle": 0, "moved": 0, "tries": 0,
         "began": 0.0, "since": 0.0}
NOTHING = object()              # no life sign read yet

# What each step may spend standing still: milliseconds between tries,
# and how many of them in a row may pass without the window moving.
# Time in which it moves is not counted, so a slow machine only takes
# longer while one that is stuck still gives up.
WAITS = {"the window": (100, 120),
         "the Open project button": (150, 200),
         "the Multitrack tick": (150, 200),
         "the Resolve cut sheet": (150, 200),
         "the speaker box and the preview box": (150, 250)}
# The backstop, and not the wait: it ends a run whose steps have stopped
# coming back at all. Every step starts it again, so it can never cut
# short a wait that is still working -- a wait says for itself when it
# gives up, and it always does.
IDLE = max(ms * tries for ms, tries in WAITS.values()) + 10000
clock = QtCore.QTimer()
clock.setSingleShot(True)
clock.timeout.connect(app.quit)


def alive():
    """The run is still going: the backstop begins again from here."""
    clock.start(IDLE)


def stirring():
    """A cheap reading of everything the window has written so far.

    The rows and the lines beside the bars come out of real reports and
    stand still when the work does. The bars themselves are left out:
    one of them creeps forward on a timer of its own and would call a
    window that hangs alive.
    """
    if win() is None:
        return None
    return (reading(),
            tuple(w.text() for w in win().findChildren(QtWidgets.QLabel)
                  if w.isVisible()))


def gave_up(what, ms, limit, life):
    """Why a wait ended, in numbers: only this line reaches another machine."""
    took = time.monotonic() - watch["began"]
    if life is None:
        return ("waited %.1f s for %s, and it never came -- %d tries in "
                "%.1f s, and nothing here that would say whether the "
                "window was still moving"
                % (limit * ms / 1000.0, what, watch["tries"], took))
    return ("gave up on %s: nothing moved for %.1f s, %d tries in a row "
            "-- %d changes before that, %.1f s altogether"
            % (what, time.monotonic() - watch["since"], limit,
               watch["moved"], took))


def hold(ok, what, life=None):
    """Wait for the window to get there, and give up at a standstill.

    The step comes back every few milliseconds until <ok> is true. What
    runs out is not time but standstill: <life> reads something cheap
    that changes while the window is still filling, and every change
    fills the budget up again. A wait with no such reading spends it on
    the clock, as it always did. Giving up is a defect and says so, or
    the shot is of whatever was on the screen.
    """
    ms, limit = WAITS[what]
    if ok:
        holding[0] = None
        return False
    if holding[0] != what:
        holding[0] = what
        watch.update(sign=NOTHING, idle=0, moved=0, tries=0,
                     began=time.monotonic(), since=time.monotonic())
    watch["tries"] += 1
    now = life() if life is not None else NOTHING
    if now is not NOTHING and now != watch["sign"]:
        if watch["sign"] is not NOTHING:
            watch["moved"] += 1
            watch["since"] = time.monotonic()
        watch["sign"] = now
        watch["idle"] = 0
    else:
        watch["idle"] += 1
    if watch["idle"] >= limit:
        fail(gave_up(what, ms, limit, life))
        holding[0] = None
        app.quit()
        return True
    n[0] -= 1
    QtCore.QTimer.singleShot(ms, step)
    return True


def showing(text):
    """Is a line beginning with that text on the screen?"""
    return any(w.isVisible() and w.text().startswith(text)
               for w in win().findChildren(QtWidgets.QLabel))


def built():
    """The project is in, so the sheet it fills is there.

    Asked of the window, which puts that sheet in once there are files.
    Asking the rows of a table would tie this script to the assignment
    being made of tables.
    """
    return sheet_of(vpm.T('Resolve cut'))[0] is not None


def fetching():
    """A still out of a video file is on its way.

    The player fetches it in a thread, and a shot taken before it lands
    photographs the picture from before.
    """
    return any(getattr(w, "_still_running", False)
               for w in win().findChildren(QtWidgets.QWidget))


def working():
    """A bar in the window says something is still running.

    The prework bar stands there while the envelopes are read, the
    footer bar while anything runs and for a moment after. Both are in
    the picture, so the shot waits for them.
    """
    return any(b.isVisible()
               for b in win().findChildren(QtWidgets.QProgressBar))


def ready():
    """Everything the pictures and the printout need is done.

    Both boxes stand on the screen, the time axis is measured -- it runs
    in a thread and moves the player when it lands -- no still is on its
    way, and boxes and lists read the same twice.
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
    alive()
    i = n[0]; n[0] += 1
    try:
        if i == 0:
            if hold(win() is not None, "the window"): return
            win().show(); app.processEvents()
        elif i == 1:
            k = button(vpm.T('Open project ...')[:8])
            if hold(k is not None, "the Open project button"): return
            print("Load button:", bool(k)); k.click()
        elif i == 2:
            # The tick only wakes up once the project is loaded.
            multitrack = vpm.T('Multitrack (one track per speaker)')
            ticks = [cb for cb in win().findChildren(QtWidgets.QCheckBox)
                     if cb.text().startswith(multitrack)]
            if hold(any(cb.isEnabled() for cb in ticks),
                    "the Multitrack tick", stirring): return
            for cb in ticks:
                print("Multitrack:", cb.isEnabled(), cb.isChecked())
                if cb.isEnabled() and not cb.isChecked():
                    cb.setChecked(True)
        elif i == 3:
            if hold(built(), "the Resolve cut sheet", stirring): return
            if not tab(vpm.T('Resolve cut')): return
        elif i == 4:
            if hold(ready(), "the speaker box and the preview box",
                    stirring): return
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
            # Every list this sheet holds, the hidden ones as well: the
            # speaker table is hidden while no speakers are known, and
            # that is the window saying so. Gone altogether is the
            # defect, and that is what fails.
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
alive()
sys.argv = ["videopodcast_magic.py"]
BEGAN = time.monotonic()
code = vpm.gui()
if not through[0] and not bad:
    # Naming the step and what it was waiting for: on another machine
    # only what stands in this line exists.
    doing = ("waiting for %s -- %d tries, %d of them with the window "
             "moving" % (holding[0], watch["tries"], watch["moved"])
             ) if holding[0] else "between two steps"
    fail("the steps stopped coming: nothing at all for %.0f s at step "
         "%d, %s (%.1f s altogether)"
         % (IDLE / 1000.0, n[0], doing, time.monotonic() - BEGAN))
if bad:
    print("\n%d thing(s) went wrong:" % len(bad))
    for line in bad:
        print("  -", line)
# What gui() gives back is Qt's event loop, not a statement about the
# pictures. The checks decide, and the number is said, not obeyed.
if code and through[0] and not bad:
    print("NOTE: the window returned %s although every step was reached "
          "and nothing was found wanting." % code)
# The last line, whatever happens. A run that comes back with a 1 and
# says nothing at all -- no traceback, no FAIL, no missing step -- leaves
# no report to improve. If this line is missing, the process did not get
# here; if it is there, the numbers on it say what went wrong.
print("END: through=%s bad=%d loop=%s" % (through[0], len(bad), code),
      flush=True)
raise SystemExit(1 if bad or not through[0] else 0)
