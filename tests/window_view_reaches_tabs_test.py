# -*- coding: utf-8 -*-
"""The View menu reaches every tab that stands, by name and by key.

The keys Ctrl+1 to Ctrl+n do not hang on the menu entries, which are
built anew every time the menu opens; they hang on the window and wait
for their tab, so the two can drift apart and the menu can offer a key
the window cannot answer. Three states are asked: a window with nothing
open, where only the first tab stands; the same window with a project
in it, before the menu has been opened again; and after it has. Each
key is then both set off on the window and typed at it, since between
the two lies a shortcut map that answers twice or not at all.
"""
import os
import time
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import json, shutil, subprocess, sys, tempfile, wave
import numpy as np
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtTest import QTest

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


# Files and production stands from the start; Assignment and time
# window, Resolve cut and Output arrive with the material. So four, and
# four keys.
TABS_WANTED = 4
KEYS_WANTED = ["Ctrl+1", "Ctrl+2", "Ctrl+3", "Ctrl+4"]
# The same four as keys to type, since a key sequence cannot be typed.
NUMBER_KEYS = [QtCore.Qt.Key_1, QtCore.Qt.Key_2,
               QtCore.Qt.Key_3, QtCore.Qt.Key_4]
# Where each key is fired from, so that a key landing on the tab that
# was already current proves nothing.
FROM_TAB = [1, 2, 3, 0]
TICK = "✓"

RATE, SEC = 48000, 4
folder = tempfile.mkdtemp(prefix="vpm_view_")
out_folder = os.path.join(folder, "Ergebnis")
os.makedirs(out_folder, exist_ok=True)


def tone(name, hz=300.0):
    path = os.path.join(folder, name)
    t = np.arange(SEC * RATE) / float(RATE)
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes((0.4 * np.sin(2 * np.pi * hz * t) * 32767)
                      .astype("<i2").tobytes())
    return path


def clip(name):
    path = os.path.join(folder, name)
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                    "testsrc=size=160x90:rate=25:duration=%d" % SEC,
                    "-f", "lavfi", "-i",
                    "sine=frequency=300:duration=%d" % SEC,
                    "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
                    "yuv420p", "-c:a", "aac", "-shortest", "-y", path],
                   check=True)
    return path


audio = tone("A_speaker.wav")
one, two = clip("B_camera.mov"), clip("C_camera.mov")
# A finished video in the output folder is what brings the Output tab
# with the project: the program takes it for results from an earlier
# run and shows the sheet that belongs to them.
shutil.copy(one, os.path.join(out_folder, "Fertig.mov"))
project = os.path.join(folder, "videopodcast-magic_Tabs.json")
with open(project, "w", encoding="utf-8") as f:
    json.dump({"format": 3, "version": "test", "timeline": [], "call": [],
               "files": [{"path": audio, "kind": "audio"},
                         {"path": one, "kind": "video"},
                         {"path": two, "kind": "video"}],
               "out_folder": out_folder, "production": "Tabs",
               "multitrack": False, "assignment": {}, "preset": ""}, f)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (project, ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted


def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def button(word):
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(word):
            return w


def tab_bar():
    """The bar of sheets, found by the one tab that is always there."""
    for tw in win().findChildren(QtWidgets.QTabWidget):
        if tw.count() and tw.tabText(0).startswith(
                vpm.T('Files && production')):
            return tw


def view_menu():
    for m in win().findChildren(QtWidgets.QMenu):
        if m.title() == vpm.T('&View'):
            return m


def open_view():
    """Open the View menu the way somebody at the screen opens it.

    Opening is what refills it, and nothing else does: Qt has no signal
    for a tab arriving. The popup is put away again afterwards, or it
    keeps the keyboard and every key fired later goes to it.
    """
    m = view_menu()
    if m is None:
        return False
    m.popup(QtCore.QPoint(0, 0))
    app.processEvents()
    m.close()
    app.processEvents()
    for _ in range(20):
        away = QtWidgets.QApplication.activePopupWidget()
        if away is None:
            break
        away.hide()
        app.processEvents()
    win().activateWindow()
    app.processEvents()
    return QtWidgets.QApplication.activePopupWidget() is None


def words(text):
    """The words on a head or an entry, without tick or ampersands.

    A tab head writes an ampersand doubled and the menu writes it
    single, and a finished tab carries a tick the menu leaves off. Both
    are dropped here rather than translated into each other, so that
    this does not repeat the program's own step.
    """
    return tuple(text.replace("&", " ").replace(TICK, " ").split())


def entries():
    return [a.text() for a in view_menu().actions()]


def offered():
    """Every key the View menu shows beside an entry."""
    return [a.shortcut().toString() for a in view_menu().actions()]


def answered():
    """Every key the window itself can answer, whatever menu is open."""
    return sorted(s.key().toString()
                  for s in win().findChildren(QtGui.QShortcut)
                  if s.isEnabled()
                  and s.context() == QtCore.Qt.WindowShortcut)


def fire(key):
    """Set off the window's own shortcut for one key."""
    for s in win().findChildren(QtGui.QShortcut):
        if s.key().toString() == key and s.isEnabled():
            s.activated.emit()
            app.processEvents()
            return True
    return False


def numbered(entry):
    """A wording that puts a number where the tab's name should be."""
    first = (words(entry) or ("",))[0].rstrip(".")
    return first.isdigit()


found = {}
n = [0]
seen = [-1]
patience = [0]
over = set()


class NotYet(Exception):
    """The window has not caught up; wait and ask again."""


def needed(what, thing):
    if thing is None or thing is False:
        raise NotYet(what)
    return thing


def deadline():
    """The whole pass has taken 90 s: red, and it says where.

    A bare app.quit() here would end the run in the middle and leave
    every check after this point unreached -- and with nothing in `bad`
    the test would print a low count and go out green.
    """
    def fired():
        if "the pass" in over:
            return          # the pass is over; this timer is only late
        bad.append("the pass never finished: 90 s gone, still at step %d"
                   % n[0])
        app.quit()
    return fired


def step():
    i = n[0]
    print("   step %d" % i, flush=True)
    try:
        if i == 0:
            needed("the window", win()).show()
            win().resize(1400, 900)
            app.processEvents()
            print("1. A window with nothing open")
            tw = needed("the tab bar", tab_bar())
            check("only the first tab stands before a project is open",
                  tw.count() == 1,
                  "%d tabs against 1: %s"
                  % (tw.count(),
                     [tw.tabText(k) for k in range(tw.count())]))
            needed("the View menu to open", open_view())
            found["alone"] = entries()
            found["window"] = id(win())
            check("the View menu names no tab that is not there yet",
                  [words(t) for t in found["alone"]]
                  == [words(tw.tabText(0))],
                  "with %d tabs (%s) the menu names %d: %s"
                  % (tw.count(),
                     [tw.tabText(k) for k in range(tw.count())],
                     len(found["alone"]), found["alone"]))
            needed("the Open project button", button("Open project")).click()
        elif i == 1:
            tw = needed("the tab bar", tab_bar())
            # Waited for is the project, which the title bar reports, and
            # then a count that has stopped moving -- never the number
            # this step judges, or a missing tab would end the run here
            # instead of being reported below.
            if tw.count() != seen[0]:
                seen[0] = tw.count()
                found["still"] = 0
                patience[0] = 0
            else:
                found["still"] = found.get("still", 0) + 1
            if os.path.basename(project) not in win().windowTitle():
                raise NotYet("the project in the title bar, which reads %r"
                             % win().windowTitle())
            if found.get("still", 0) < 5:
                raise NotYet("the tabs to stop arriving, %d of them for "
                             "%d rounds" % (tw.count(), found.get("still", 0)))
            print("\n2. The project is open, the menu not opened since")
            check("the tabs arrive with the material",
                  tw.count() == TABS_WANTED,
                  "%d tabs against %d: %s"
                  % (tw.count(), TABS_WANTED,
                     [tw.tabText(k) for k in range(tw.count())]))
            keys = answered()
            missing = [k for k in KEYS_WANTED if k not in keys]
            check("every tab has its key without the View menu being opened",
                  not missing,
                  "%d tabs stand, the window answers %s, and %s is missing"
                  % (tw.count(), keys, missing or "nothing"))
        elif i == 2:
            tw = needed("the tab bar", tab_bar())
            needed("the View menu to open", open_view())
            print("\n3. The menu has been opened again")
            shown = entries()
            heads = [tw.tabText(k) for k in range(tw.count())]
            check("the View menu names the tabs and does not number them",
                  [words(t) for t in shown] == [words(h) for h in heads]
                  and not any(numbered(t) for t in shown),
                  "%d tabs %s against %d entries %s, of them numbered: %s"
                  % (len(heads), heads, len(shown), shown,
                     [t for t in shown if numbered(t)] or "none"))
            check("a tab that arrives later is named in the same window",
                  len(shown) > len(found["alone"])
                  and id(win()) == found["window"],
                  "the menu named %d before the project and %d now, "
                  "the window is %s"
                  % (len(found["alone"]), len(shown),
                     "the same one" if id(win()) == found["window"]
                     else "another one"))
            keyless = [t for t, k in zip(shown, offered()) if not k]
            check("every tab the View menu names offers a key",
                  bool(shown) and not keyless,
                  "%d entries %s, their keys %s, without one: %s"
                  % (len(shown), shown, offered(), keyless or "none"))
            keys = answered()
            nowhere = [k for k in offered() if k and k not in keys]
            check("the window answers every key the View menu offers",
                  not nowhere,
                  "the menu offers %s, the window answers %s, without an "
                  "answer: %s" % (offered(), keys, nowhere or "none"))
        elif i == 3:
            tw = needed("the tab bar", tab_bar())
            print("\n4. Every key on its tab")
            landed = []
            for k, key in enumerate(KEYS_WANTED):
                tw.setCurrentIndex(FROM_TAB[k])
                app.processEvents()
                fire(key)
                landed.append(tw.currentIndex())
            check("every key on the window brings its own tab up",
                  landed == [0, 1, 2, 3],
                  "%s landed on %s, wanted [0, 1, 2, 3], each fired from "
                  "%s" % (KEYS_WANTED, landed, FROM_TAB))
            # Typed, not set off: between the key and the shortcut lies
            # Qt's shortcut map, and a second answer to the same key --
            # the menu entry that shows it -- makes it fire neither.
            # Which window has the keyboard stands in the line, because
            # a key typed at the wrong one reaches nothing either.
            win().activateWindow()
            app.processEvents()
            typed = []
            for k, key in enumerate(NUMBER_KEYS):
                tw.setCurrentIndex(FROM_TAB[k])
                app.processEvents()
                QTest.keyClick(win(), key, QtCore.Qt.ControlModifier)
                app.processEvents()
                typed.append(tw.currentIndex())
            check("a typed key reaches the window and brings its tab up",
                  typed == [0, 1, 2, 3],
                  "%s typed landed on %s, wanted [0, 1, 2, 3], each from "
                  "%s, and the keyboard is at %s"
                  % (KEYS_WANTED, typed, FROM_TAB,
                     "the program's window"
                     if id(app.activeWindow()) == id(win())
                     else repr(app.activeWindow())))
        else:
            over.add("the pass")
            app.quit()
            return
        n[0] += 1
        patience[0] = 0
        QtCore.QTimer.singleShot(400, step)
    except NotYet as why:
        patience[0] += 1
        if patience[0] > 40:
            bad.append("step %d waited for %s: 41 goes over about 16 s "
                       "with nothing changing, and it never came"
                       % (i, why))
            over.add("the pass")
            app.quit()
            return
        QtCore.QTimer.singleShot(400, step)
    except Exception:
        import traceback; traceback.print_exc()
        bad.append("step %d fell over" % i)
        over.add("the pass")
        app.quit()


QtCore.QTimer.singleShot(500, step)
QtCore.QTimer.singleShot(90000, deadline())
# A window that falls over while it is being built takes the event loop
# with it, and the closing lines below are the only place that counts.
try:
    vpm.gui()
except Exception:
    import traceback; traceback.print_exc()
    bad.append("the window never came up: gui() fell over")

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
