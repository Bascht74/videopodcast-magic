# -*- coding: utf-8 -*-
"""A Qt without multimedia still builds the window, and ffplay plays.

Qt's multimedia modules are barred before anything imports them, as on
a Qt built without them, and the window is brought up offscreen. In
order: the window stands and its Player menu is greyed; once two
cameras and a recording are added, both players are the stand-in,
which says that ffplay plays, and once the camera table stands --
where the window fills an empty preview -- no ffplay was opened by
itself; a file the stand-in is handed goes to ffplay at the second
asked for. ffplay itself is stood in for: what is judged is the
line the window would start it with.
"""
PLATFORM_BOUND = True
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import shutil
import subprocess
import tempfile
import time
import the_program
from fixture_root import fixture

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("VPM_SILENT", "1")
# What a Qt without multimedia answers: the import itself fails. Set
# before PySide6 is touched, so nothing has the modules already.
sys.modules["PySide6.QtMultimedia"] = None
sys.modules["PySide6.QtMultimediaWidgets"] = None
from PySide6 import QtCore, QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.say_dialog = lambda *a, **k: True     # no dialog waits for anybody

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# ffplay stood in for, after the program is loaded: one of its pieces
# builds a class on the real Popen. Everything else goes through.
started = []
real_popen = subprocess.Popen


class NoFfplay(object):
    """What the window gets back instead of a running ffplay."""

    def __init__(self, command):
        started.append(list(command))

    def poll(self):
        return 0

    def wait(self, *_a, **_k):
        return 0


def popen(command, *a, **k):
    if command and os.path.basename(str(command[0])) == "ffplay":
        return NoFfplay(command)
    return real_popen(command, *a, **k)


subprocess.Popen = popen
_show = QtWidgets.QWidget.show


def offstage(self):
    """Shown for the layout, never on a screen."""
    self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
    _show(self)


QtWidgets.QWidget.show = offstage

FOLDER = tempfile.mkdtemp(prefix="vpm_noplayer_")
CAMERA = os.path.join(FOLDER, "WideCam_C001.mp4")
SECOND = os.path.join(FOLDER, "GuestCam_C002.mp4")
SOUND = os.path.join(FOLDER, "Presenter_REC0001.m4a")
for name, path in (("a.mp4", CAMERA), ("b.mp4", SECOND),
                   ("audio.m4a", SOUND)):
    shutil.copy2(os.path.join(fixture("playertest"), name), path)


def win():
    """The program's window, or None while it is not up."""
    for w in app.topLevelWidgets():
        if vpm.DISPLAY_NAME in w.windowTitle():
            return w
    return None


def of_kind(name):
    """Every widget in the window whose class is called *name*."""
    return [w for w in win().findChildren(QtWidgets.QWidget)
            if type(w).__name__ == name]


def cameras_tabled():
    """How many rows the camera table of the second tab holds.

    The window fills the empty preview right after it builds this
    table, so a table with both cameras means that moment has passed.
    """
    for table in win().findChildren(QtWidgets.QTableWidget):
        names = [str(table.item(r, 0).text()) if table.item(r, 0) else ""
                 for r in range(table.rowCount())]
        if os.path.basename(CAMERA) in names:
            return table.rowCount()
    return 0


state = {"step": 0, "rounds": 0, "over": False}


def step():
    """One step of the pass, on a timer, waiting on rounds of 200 ms."""
    s = state["step"]
    state["rounds"] += 1
    if s == 0:
        if win() is None and state["rounds"] < 150:
            return QtCore.QTimer.singleShot(200, step)
        print("1. The window, built on a Qt without multimedia")
        check("the window stands without Qt's multimedia", win() is not None,
              "%r after %d rounds of 200 ms"
              % (win().windowTitle()[:40] if win() else None,
                 state["rounds"]))
        if win() is None:
            return finish()
        menus = [m for m in win().findChildren(QtWidgets.QMenu)
                 if m.title() == vpm.T('&Player')]
        check("the Player menu is greyed where nothing can play",
              len(menus) == 1 and not menus[0].menuAction().isEnabled(),
              "%d menus titled %r, enabled %s"
              % (len(menus), vpm.T('&Player'),
                 [m.menuAction().isEnabled() for m in menus]))
        # The two players are built with the tabs the first files bring.
        of_kind("DropArea")[0].drop([CAMERA, SECOND, SOUND])
    elif s == 1:
        if (cameras_tabled() < 2 or len(of_kind("NoPlayer")) < 2) \
                and state["rounds"] < 150:
            return QtCore.QTimer.singleShot(200, step)
        print("\n2. Two cameras and a recording added")
        players = of_kind("NoPlayer")
        check("both players are the stand-in that hands on to ffplay",
              len(players) == 2,
              "%d stand-ins, wanted 2 (preview and cut)" % len(players))
        wanted = vpm.T('No player is built in here -- playback runs in '
                       'ffplay in its own window.')
        said = [p.title.text() for p in players]
        check("the stand-in says that ffplay plays instead",
              bool(said) and all(t == wanted for t in said),
              "%r against %r" % (said, wanted))
        check("the camera table is built with both cameras",
              cameras_tabled() == 2,
              "%d rows after %d rounds of 200 ms, wanted 2"
              % (cameras_tabled(), state["rounds"]))
        check("files added open no ffplay by themselves",
              started == [],
              "ffplay started %d times: %r" % (len(started), started[:1]))
        print("\n3. A file handed to the stand-in")
        del started[:]
        if players:
            players[0].load(CAMERA, 12.5)
        line = started[0] if len(started) == 1 else []
        check("a file handed to the stand-in plays in ffplay from the "
              "second asked for",
              line[:1] == ["ffplay"] and line[-1:] == [CAMERA]
              and "-ss" in line
              and line[line.index("-ss") + 1:][:1] == ["12.50"],
              "%d ffplay lines, the first %r" % (len(started), line))
        return finish()
    state["step"], state["rounds"] = s + 1, 0
    QtCore.QTimer.singleShot(200, step)


def finish():
    state["over"] = True
    app.quit()


def deadline():
    """An outer brake only: the waiting inside is on rounds of 200 ms."""
    if not state["over"]:
        bad.append("the pass never finished: 120 s gone, at step %d"
                   % state["step"])
        app.quit()


QtCore.QTimer.singleShot(300, step)
QtCore.QTimer.singleShot(120000, deadline)
try:
    vpm.gui()
except Exception:
    import traceback
    traceback.print_exc()
    check("the window stands without Qt's multimedia", False,
          "gui() fell over: %s" % (sys.exc_info()[1],))

subprocess.Popen = real_popen
shutil.rmtree(FOLDER, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
