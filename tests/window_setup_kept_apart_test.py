# -*- coding: utf-8 -*-
"""What is set up once, and what is decided every time.

The key for auphonic.com and the preset used to stand in one box on the
first sheet, so choosing a preset meant paging away from the table where
that choice belongs. They are apart now -- key and Resolve check behind
"Settings ...", preset and the Multitrack tick under the assignment
table. In order: the window with a project opened in it, the first sheet
without the key box, preset and tick beside the table, the settings
window opening on the button and closing again, and last whether the run
got through its steps at all rather than breaking off.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import importlib.util, json, shutil, sys, tempfile, time, traceback, wave
import numpy as np
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets
began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# Every caption is asked of the program, not written out here: a literal
# would tie the test to one language and one wording. The one exception
# is the product name in the title bar, which is the same in every
# language and is not translated.
NAME = "Video Podcast Magic"
KEY_BOX = vpm.T('Access to auphonic.com')
RESOLVE_BOX = vpm.T('Connection to Resolve')
RUN_BOX = vpm.T('Processing at auphonic.com (optional)')
PLACE_BOX = vpm.T('Production')
MULTI = vpm.T('Multitrack (one track per speaker)')
SETTINGS = vpm.T('Settings ...')
CONNECT = vpm.T('Connect')
CLOSE = vpm.T('Close')
OPEN_PROJECT = vpm.T('Open project ...')
SHEET_FILES = vpm.T('Files && production')
SHEET_ASSIGN = vpm.T('Assignment && time window')

RATE, SEC = 48000, 4
folder = tempfile.mkdtemp(prefix="vpm_settings_")


def tone(name, hz):
    path = os.path.join(folder, name)
    t = np.arange(SEC * RATE) / float(RATE)
    x = (0.4 * np.sin(2 * np.pi * hz * t) * 32767).astype("<i2")
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes(x.tobytes())
    return path


one, two = tone("A_speaker.wav", 300), tone("B_speaker.wav", 900)
project = os.path.join(folder, "videopodcast-magic_Interview_2.json")
with open(project, "w", encoding="utf-8") as f:
    json.dump({"format": 3, "version": "test", "timeline": [], "call": [],
               "files": [{"path": one, "kind": "audio"},
                         {"path": two, "kind": "audio"}],
               "out_folder": os.path.join(folder, "Ergebnis"),
               "production": "Settings", "multitrack": True,
               "assignment": {}, "preset": ""}, f)
os.makedirs(os.path.join(folder, "Ergebnis"), exist_ok=True)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (project, ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted


def tops(shown=True):
    """The titles of the windows: those one can see, or every one there is.

    A window that was built and never shown counts for "did it come up
    at all" and for nothing else, so the two are asked apart.
    """
    return [x.windowTitle() for x in app.topLevelWidgets()
            if x.windowTitle() and (x.isVisible() or not shown)]


def win():
    for x in app.topLevelWidgets():
        if NAME in x.windowTitle():
            return x


def parts(where, kind):
    """Every widget of that kind one can see in that window, and no other.

    findChildren reaches into the settings window as well, because that
    one is built as a child of the main window. Without the second
    condition the key box would count as standing on the sheet behind
    it the moment somebody opened the settings.
    """
    return [w for w in where.findChildren(kind)
            if w.isVisible() and w.window() is where.window()]


def boxes(where):
    return [g.title() for g in parts(where, QtWidgets.QGroupBox)]


def buttons(where=None):
    """The captions of every button one can see in there."""
    return [w.text() for w in parts(where or win(), QtWidgets.QPushButton)]


def button(word, where=None):
    for w in parts(where or win(), QtWidgets.QPushButton):
        if word.lower() in w.text().lower():
            return w


def dialogs():
    return [d for d in app.topLevelWidgets()
            if isinstance(d, QtWidgets.QDialog) and d.isVisible()]


def sheets():
    """Every sheet the window offers, in the order they stand."""
    out = []
    for tw in win().findChildren(QtWidgets.QTabWidget):
        out += [tw.tabText(k) for k in range(tw.count())]
    return out


def same(written, title):
    """Whether that sheet is the one, tick and all.

    A finished sheet carries a tick behind its name and Qt writes an
    ampersand doubled, so neither side can be compared as it stands.
    """
    return title.replace("&&", "&") in written.replace("&&", "&")


def tab(title):
    """Page to that sheet; report whether the window has one."""
    for tw in win().findChildren(QtWidgets.QTabWidget):
        for k in range(tw.count()):
            if same(tw.tabText(k), title):
                tw.setCurrentIndex(k)
                app.processEvents()
                return True
    return False


# How long the window is given to come up and to open the project. Both
# stay well under the whole run's patience below, so a slow machine
# learns which step never came and not only that the time is up.
UP = 30.0
LOADED = 30.0
PATIENCE = 120.0
at = [0]
watch = QtCore.QElapsedTimer()
how = ["through"]
# Once the window is down, no timer speaks any more. A step still in
# the queue would otherwise be run by the event loop inside the
# clearing-up and reach a judgement after the count had been printed --
# which is how a check gets lost without anybody seeing it go.
gone = [False]


def stop():
    """The one place the run ends on purpose. Everything after it counts."""
    how[0] = "through"
    app.quit()


def first_sheet():
    print("\n2. The first sheet holds no access data any more")
    got = tab(SHEET_FILES)
    check("the first sheet is there to page back to", got,
          "%d sheets: %s" % (len(sheets()), sheets()))
    if not got:
        return False
    here = boxes(win())
    check("the key box has left the first sheet", KEY_BOX not in here,
          "%d boxes on the first sheet: %s" % (len(here), here))
    check("the production box is still on the first sheet",
          PLACE_BOX in here,
          "%d boxes on the first sheet: %s" % (len(here), here))
    return True


def assignment_sheet():
    print("\n3. The preset stands where the tracks are decided")
    tab(SHEET_ASSIGN)
    here = boxes(win())
    check("the auphonic box stands on the assignment sheet",
          RUN_BOX in here,
          "%d boxes on the assignment sheet: %s" % (len(here), here))
    lists = parts(win(), QtWidgets.QComboBox)
    carry = [c for c in lists
             if any(c.itemData(k) == vpm.PRESET_NONE
                    for k in range(c.count()))]
    check("the preset list stands on the assignment sheet too",
          len(carry) >= 1,
          "%d visible lists there, %d of them offering %r"
          % (len(lists), len(carry), vpm.PRESET_NONE))
    ticks = [w.text() for w in parts(win(), QtWidgets.QCheckBox)]
    check("the multitrack tick stands on the assignment sheet",
          MULTI in ticks, "%d ticks there: %s" % (len(ticks), ticks))


def settings_window():
    print("\n4. Settings: one window, opened on purpose")
    names = buttons()
    b = button(SETTINGS)
    check("a Settings button stands in the window", b is not None,
          "%d visible buttons, %d of them saying %r"
          % (len(names), sum(1 for x in names if SETTINGS in x), SETTINGS))
    check("no settings window stands open before it is asked for",
          not dialogs(), "%d windows open, 0 wanted: %s"
          % (len(dialogs()), tops()))
    if b is None:
        return
    b.click()
    app.processEvents()
    d = dialogs()
    check("the button opens exactly one settings window", len(d) == 1,
          "%d windows open, 1 wanted: %s" % (len(d), tops()))
    if len(d) != 1:
        return
    inside = boxes(d[0])
    check("the settings window holds the key box", KEY_BOX in inside,
          "%d boxes in it: %s" % (len(inside), inside))
    check("the settings window holds the Resolve check",
          RESOLVE_BOX in inside, "%d boxes in it: %s" % (len(inside), inside))
    fields = parts(d[0], QtWidgets.QLineEdit)
    check("the settings window has a field to type the key into",
          len(fields) >= 1, "%d fields in it, at least 1 wanted" % len(fields))
    said = buttons(d[0])
    check("the settings window has a Connect button for the key",
          button(CONNECT, d[0]) is not None,
          "%d buttons in it, %d saying %r: %s"
          % (len(said), sum(1 for x in said if CONNECT in x), CONNECT, said))
    out = button(CLOSE, d[0])
    check("the settings window has a button that closes it", out is not None,
          "%d buttons in it, %d saying %r: %s"
          % (len(said), sum(1 for x in said if CLOSE in x), CLOSE, said))
    if out is None:
        return
    out.click()
    app.processEvents()
    check("pressing that button closes the settings window", not dialogs(),
          "%d windows still open, 0 wanted: %s" % (len(dialogs()), tops()))


def step():
    """One step of the window's life; the next is queued at the end.

    Nothing here waits on the clock: each step asks for the thing it
    needs and comes back in a fifth of a second until it is there.
    Patience running out is a red check with the seconds in it, never a
    silent carry-on -- and a step that cannot go on stops the run, so
    the count below reports what was reached and not what crashed.
    """
    if gone[0]:
        return
    try:
        if at[0] == 0:
            if win() is None and watch.elapsed() < UP * 1000:
                QtCore.QTimer.singleShot(200, step); return
            print("\n1. The window comes up with a project in it")
            w = win()
            check("the window comes up", w is not None,
                  "%.1f s of %.1f s allowed, %d windows: %s"
                  % (watch.elapsed() / 1000.0, UP,
                     len(tops(False)), tops(False)))
            if w is None:
                return stop()
            w.show(); w.resize(1400, 900); app.processEvents()
            names = buttons()
            b = button(OPEN_PROJECT)
            check("a button offers to open an earlier project",
                  b is not None, "%d visible buttons, %d saying %r"
                  % (len(names), sum(1 for x in names if OPEN_PROJECT in x),
                     OPEN_PROJECT))
            if b is None:
                return stop()
            b.click()
            watch.restart()
        elif at[0] == 1:
            got = tab(SHEET_ASSIGN)
            if not got and watch.elapsed() < LOADED * 1000:
                QtCore.QTimer.singleShot(200, step); return
            check("the project opens and the assignment sheet appears", got,
                  "%.1f s of %.1f s allowed, %d sheets: %s"
                  % (watch.elapsed() / 1000.0, LOADED,
                     len(sheets()), sheets()))
            if not got:
                return stop()
        elif at[0] == 2:
            if first_sheet():
                assignment_sheet()
                settings_window()
            return stop()
    except Exception:
        traceback.print_exc()
        how[0] = ("it broke off at step %d of 3: %s"
                  % (at[0] + 1,
                     traceback.format_exc().strip().splitlines()[-1]))
        app.quit()
        return
    at[0] += 1
    QtCore.QTimer.singleShot(0, step)


def out_of_patience():
    """The run is cut off. It says so, and the count still gets printed."""
    if gone[0]:
        return
    how[0] = ("it stood still at step %d of 3 after %.0f s"
              % (at[0] + 1, PATIENCE))
    app.quit()


watch.start()
QtCore.QTimer.singleShot(0, step)
QtCore.QTimer.singleShot(int(PATIENCE * 1000), out_of_patience)


def let_go_of(what):
    """Make every player let go of what it has open in there.

    Under Windows a folder holding an open file cannot be deleted, and
    ignore_errors would hide that it stays behind. Players are found by
    what they hold, so a second holder cannot slip through. One that
    never started is not stopped: what lies behind stop() is built on
    first use and waits for a lock another player holds.
    """
    what = os.path.realpath(what)
    let_go = []
    for top in app.topLevelWidgets():
        for x in top.findChildren(QtCore.QObject):
            if not (hasattr(x, "setSource") and hasattr(x, "source")):
                continue
            where = x.source()
            if not isinstance(where, QtCore.QUrl):
                continue
            where = where.toLocalFile()
            if not where:
                continue
            held = os.path.realpath(where)
            if held != what and not held.startswith(what + os.sep):
                continue
            state = getattr(x, "playbackState", None)
            state = state() if state is not None else None
            if state is not None and state != type(state).StoppedState:
                x.stop()
            x.setSource(QtCore.QUrl())
            let_go.append(os.path.basename(where))
    app.processEvents()
    return sorted(let_go)


def clean_up(what):
    """Close the window, then delete the folder, waiting for the grip.

    gui() comes back with the window still standing. Let go, close,
    delete -- in that order, and without ignore_errors, which would
    swallow the one thing that can go wrong: a folder that stays.
    Letting go returns before the system has closed the handle, so the
    delete is retried against the event loop for up to ten seconds.
    What is left after that is named, but does not turn the test red.
    """
    print("  let go of %s" % (", ".join(let_go_of(what)) or "nothing"))
    for top in app.topLevelWidgets():
        top.close()
    app.processEvents()
    clock = QtCore.QElapsedTimer()
    clock.start()
    while True:
        left = []
        try:
            shutil.rmtree(what)
        except OSError:
            for here, _, files in os.walk(what):
                left += [os.path.join(here, f) for f in files]
            left = left or ([what] if os.path.exists(what) else [])
        if not left or clock.elapsed() > 10000:
            break
        app.processEvents()
        QtCore.QThread.msleep(50)
    if left:
        print("  the folder stayed: %d still held after %.1f s, first %s"
              % (len(left), clock.elapsed() / 1000.0, left[0]))
    else:
        print("  the folder went away with the window, after %.1f s"
              % (clock.elapsed() / 1000.0))


sys.argv = ["videopodcast_magic.py"]
# The window itself is the last thing that can throw, and a throw here
# would take the closing lines with it. So it is caught like the steps
# inside it, and the last check below reports it.
try:
    vpm.gui()
except Exception:
    traceback.print_exc()
    how[0] = ("the window itself broke off: %s"
              % traceback.format_exc().strip().splitlines()[-1])
gone[0] = True
print("")
check("the window came through every step and stopped by itself",
      how[0] == "through",
      "%d of 3 steps in %.2f s" % (at[0] + 1, time.time() - began)
      if how[0] == "through" else how[0])
try:
    clean_up(folder)
except Exception:
    traceback.print_exc()

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
