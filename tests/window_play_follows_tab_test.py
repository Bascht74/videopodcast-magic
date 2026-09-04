# -*- coding: utf-8 -*-
"""The transport drives the player of the tab showing, or nothing.

All nine transport entries called the preview player of the second tab
-- on every tab, the Resolve tab included, where another player stands.
Five sections: that the tabs stand, that both players sit where they
should and hold material, and that the menu carries all nine; that the
entries live only on the two tabs that have a player, and that the fast
forward is alive on both because both players do it; that a command set
off from the menu lands in the player of the tab showing and nowhere
else; that the space bar typed at a player reaches that same one; and
that a player whose box is folded away counts as no player at all --
the Multitrack tick is taken off, which takes the Resolve preview off
the screen, and the transport has to go grey with it while the other
tab keeps its own.

Two traps. The transport is switched at currentChanged and aboutToShow
and nowhere else, so an isEnabled() read without a tab change before it
is the state of the build and green for nothing. And a typed key needs
the player on the screen: from a collapsed box the sequence cannot fire
at all, so the visibility is a check of its own before it.
"""
import os
import time
import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT

import json
import shutil
import subprocess
import sys
import tempfile
import wave

import numpy as np

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets
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


# The nine entries that drive a player, and the command each one is.
# Written out here rather than read off the program's own list: a test
# that takes its expectation from the very list it judges agrees with
# it however wrong both are.
TOGGLE = vpm.T('Play and pause')
FASTER = vpm.T('Play forward, faster on every press')
FRAME_ON = vpm.T('One frame forward')
TRANSPORT = [(TOGGLE, "toggle"),
             (FASTER, "faster"),
             (vpm.T('Pause'), "pause"),
             (vpm.T('One frame back'), "nudge"),
             (FRAME_ON, "nudge"),
             (vpm.T('One second back'), "nudge"),
             (vpm.T('One second forward'), "nudge"),
             (vpm.T('Ten seconds back'), "nudge"),
             (vpm.T('Ten seconds forward'), "nudge")]
# Files and production, Assignment and time window, Resolve cut, Output
# -- and the two in the middle are the ones with a player.
TABS_WANTED = 4
PREVIEW_TAB, CUT_TAB = 1, 2
FILES_TAB, OUT_TAB = 0, 3

RATE, SEC = 48000, 4
folder = tempfile.mkdtemp(prefix="vpm_play_")
out_folder = os.path.join(folder, "Ergebnis")
os.makedirs(out_folder, exist_ok=True)


def tone(name, hz=300.0):
    path = os.path.join(folder, name)
    t = np.arange(SEC * RATE) / float(RATE)
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
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
# with the project: the program takes it for results of an earlier run.
shutil.copy(one, os.path.join(out_folder, "Fertig.mov"))
project = os.path.join(folder, "videopodcast-magic_Play.json")
with open(project, "w", encoding="utf-8") as f:
    json.dump({"format": 3, "version": "test", "timeline": [], "call": [],
               "files": [{"path": audio, "kind": "audio"},
                         {"path": one, "kind": "video"},
                         {"path": two, "kind": "video"}],
               "out_folder": out_folder, "production": "Play",
               # Multitrack, because that is what puts the preview box on
               # the Resolve tab: without it the box stays away, the cut
               # player is on no screen, and a key typed at it cannot fire.
               "multitrack": True, "assignment": {}, "preset": ""}, f)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (project, ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted

# The probe. Both player classes are made by a builder called from
# gui(), so they are marked on the way out, before a single player
# exists -- which is the only way to hear the call where it lands
# rather than where the menu meant to send it. Every command is passed
# on to the real method: a probe that swallowed the call would leave
# the player in a state the program never gets it into.
watch = [False]
calls = []
klass = {}


def marked(cls, tag):
    klass[tag] = cls
    # The commands, not the entries: six of the nine are the same nudge,
    # and marking a method once per entry wraps it six deep -- one press
    # then arrives as six.
    for what in sorted(set(w for _text, w in TRANSPORT)):
        real = cls.__dict__.get(what)
        # Never added where it is missing: the cut player has no fast
        # forward, and the menu greys that entry by exactly that
        # absence. A probe that supplied it would grey nothing.
        if real is None:
            continue

        def made(real=real, what=what, tag=tag):
            def called(self, *a, **k):
                if watch[0]:
                    calls.append((tag, what))
                return real(self, *a, **k)
            return called

        setattr(cls, what, made())


_player_widgets = vpm.make_player_widgets
_cut_player = vpm.qt_cut_player


def player_widgets_watched(*a, **k):
    out = _player_widgets(*a, **k)
    marked(out[2], "preview")       # rail, surface, Player, NoPlayer
    return out


def cut_player_watched(*a, **k):
    cls = _cut_player(*a, **k)
    marked(cls, "cut")
    return cls


vpm.make_player_widgets = player_widgets_watched
vpm.qt_cut_player = cut_player_watched


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


def tick(text):
    """The checkbox with this caption."""
    for w in win().findChildren(QtWidgets.QCheckBox):
        if w.text().strip() == text:
            return w


def tab_names():
    """The captions of the tabs, which move while the window rebuilds."""
    tw = tab_bar()
    return tuple(tw.tabText(k) for k in range(tw.count())) if tw else ()


def play_menu():
    for m in win().findChildren(QtWidgets.QMenu):
        if m.title() == vpm.T('&Player'):
            return m


def entry(text):
    for a in play_menu().actions():
        if a.text() == text:
            return a


def player(tag):
    cls = klass.get(tag)
    if cls is None:
        return None
    for w in win().findChildren(cls):
        return w


def sits_on(w):
    """Which tab holds this player, asked of the sheets themselves."""
    tw = tab_bar()
    for k in range(tw.count()):
        if tw.widget(k).isAncestorOf(w):
            return k
    return -1


def show_tab(k):
    """Bring a tab up the way somebody at the screen does.

    This is what switches the transport: play_enable hangs on
    currentChanged. Read without it, isEnabled() answers with the state
    of the moment the menu was built.
    """
    tab_bar().setCurrentIndex(k)
    app.processEvents()


def alive_now():
    """The transport entries that are alive on the tab showing."""
    return [text for text, _what in TRANSPORT if entry(text).isEnabled()]


def grey_now():
    return [text for text, _what in TRANSPORT if not entry(text).isEnabled()]


def quiet():
    """Both players at a standstill, and nothing written down.

    A running player is stopped by the other one starting, and that
    stop would land in the record as a command nobody gave.
    """
    watch[0] = False
    for tag in ("preview", "cut"):
        w = player(tag)
        if w is not None:
            w.pause()
    app.processEvents()


def set_off(text):
    """Trigger one entry and report what the players heard."""
    quiet()
    calls[:] = []
    watch[0] = True
    entry(text).trigger()
    app.processEvents()
    watch[0] = False
    return list(calls)


def typed(w, key):
    """Type one key at a player and report what the players heard."""
    quiet()
    win().activateWindow()
    w.setFocus()
    app.processEvents()
    calls[:] = []
    watch[0] = True
    QTest.keyClick(w, key)
    app.processEvents()
    watch[0] = False
    return list(calls)


n = [0]
seen = [-1]
still = [0]
patience = [0]
sign = [None]
over = set()
found = {}
# The captions after the Multitrack tick came off, and how many rounds
# they have stood: the rebuild is what has to finish, and no judgement
# below reads them.
named = [None]
named_still = [0]


def life():
    """A sign that moves only because the window is working.

    Patience is spent on standstill, not on a deadline: the builder is
    up to three times slower than this machine, and a count of rounds
    would punish it for being slow rather than for being stuck.
    """
    where = win()
    tw = tab_bar() if where is not None else None
    return (where.windowTitle() if where is not None else None,
            tw.count() if tw is not None else -1)


class NotYet(Exception):
    """The window has not caught up; wait and ask again."""


def needed(what, thing):
    if thing is None or thing is False:
        raise NotYet(what)
    return thing


def deadline():
    """The whole pass has taken 150 s: red, and it says where.

    A bare app.quit() here would end the run in the middle and leave
    every check after this point unreached -- and with nothing in `bad`
    the test would print a low count and go out green.
    """
    def fired():
        if "the pass" in over:
            return          # the pass is over; this timer is only late
        bad.append("the pass never finished: 150 s gone, still at step %d"
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
            needed("the Open project button",
                   button(vpm.T('Open project ...'))).click()
        elif i == 1:
            # Waited for is the project in the title bar and a tab count
            # that has stopped moving -- never the number a check reads.
            if os.path.basename(project) not in win().windowTitle():
                raise NotYet("the project in the title bar, which reads %r"
                             % win().windowTitle())
            tw = needed("the tab bar", tab_bar())
            if tw.count() != seen[0]:
                seen[0], still[0] = tw.count(), 0
            else:
                still[0] += 1
            if still[0] < 5:
                raise NotYet("the tabs to stop arriving, %d of them for %d "
                             "rounds" % (tw.count(), still[0]))
            print("1. Both players are there and hold material")
            check("the four tabs stand before the transport is read",
                  tw.count() == TABS_WANTED,
                  "%d tabs against %d: %s"
                  % (tw.count(), TABS_WANTED,
                     [tw.tabText(k) for k in range(tw.count())]))
            found["preview"], found["cut"] = player("preview"), player("cut")
            check("the preview player is the built-in one and sits on the "
                  "assignment tab",
                  found["preview"] is not None
                  and sits_on(found["preview"]) == PREVIEW_TAB,
                  "the preview player is %s and sits on tab %s, wanted %d"
                  % (type(found["preview"]).__name__,
                     sits_on(found["preview"]) if found["preview"] is not None
                     else "nowhere", PREVIEW_TAB))
            check("the cut player is the built-in one and sits on the "
                  "Resolve tab",
                  found["cut"] is not None
                  and sits_on(found["cut"]) == CUT_TAB,
                  "the cut player is %s and sits on tab %s, wanted %d"
                  % (type(found["cut"]).__name__,
                     sits_on(found["cut"]) if found["cut"] is not None
                     else "nowhere", CUT_TAB))
            empty = [tag for tag in ("preview", "cut")
                     if not vpm.player_loaded(found[tag])]
            check("both players hold material before the transport is read",
                  not empty,
                  "the preview player holds %r, the cut player %d shots; "
                  "empty: %s"
                  % (getattr(found["preview"], "file_path", None),
                     len(getattr(found["cut"], "cut", None) or []),
                     empty or "neither"))
            offered = [text for text, _what in TRANSPORT
                       if entry(text) is not None]
            check("the Player menu carries all nine transport entries",
                  len(offered) == len(TRANSPORT),
                  "%d of %d there, missing: %s"
                  % (len(offered), len(TRANSPORT),
                     [t for t, _w in TRANSPORT if t not in offered] or "none"))
        elif i == 2:
            print("\n2. Where the transport lives")
            show_tab(PREVIEW_TAB)
            check("on the assignment tab all nine transport entries are "
                  "alive", len(alive_now()) == len(TRANSPORT),
                  "%d of %d alive, grey: %s"
                  % (len(alive_now()), len(TRANSPORT), grey_now() or "none"))
            show_tab(CUT_TAB)
            check("on the Resolve tab all nine transport entries are alive",
                  len(alive_now()) == len(TRANSPORT),
                  "%d of %d alive, grey: %s"
                  % (len(alive_now()), len(TRANSPORT), grey_now() or "none"))
            check("the fast forward is alive there because the cut player "
                  "can do it", entry(FASTER).isEnabled()
                  and hasattr(found["cut"], "faster"),
                  "the entry is %s and the cut player %s the command"
                  % ("alive" if entry(FASTER).isEnabled() else "grey",
                     "has" if hasattr(found["cut"], "faster") else "has not"))
            show_tab(OUT_TAB)
            check("on the output tab, where no player stands, all nine "
                  "transport entries are grey", not alive_now(),
                  "%d of %d alive: %s"
                  % (len(alive_now()), len(TRANSPORT), alive_now() or "none"))
            show_tab(FILES_TAB)
            check("on the files tab, where no player stands, all nine "
                  "transport entries are grey", not alive_now(),
                  "%d of %d alive: %s"
                  % (len(alive_now()), len(TRANSPORT), alive_now() or "none"))
        elif i == 3:
            print("\n3. Where a command set off from the menu lands")
            heard = set_off(TOGGLE)
            check("on the files tab Play and pause reaches no player at all",
                  heard == [],
                  "the tab showing is %d and the players heard %s"
                  % (tab_bar().currentIndex(), heard or "nothing"))
            show_tab(PREVIEW_TAB)
            heard = set_off(TOGGLE)
            check("Play and pause on the assignment tab reaches the preview "
                  "player", heard == [("preview", "toggle")],
                  "the tab showing is %d and the players heard %s"
                  % (tab_bar().currentIndex(), heard or "nothing"))
            heard = set_off(FRAME_ON)
            check("a frame forward on the assignment tab reaches the "
                  "preview player", heard == [("preview", "nudge")],
                  "the tab showing is %d and the players heard %s"
                  % (tab_bar().currentIndex(), heard or "nothing"))
            show_tab(CUT_TAB)
            heard = set_off(TOGGLE)
            check("Play and pause on the Resolve tab reaches the cut player",
                  heard == [("cut", "toggle")],
                  "the tab showing is %d and the players heard %s"
                  % (tab_bar().currentIndex(), heard or "nothing"))
            heard = set_off(FRAME_ON)
            check("a frame forward on the Resolve tab reaches the cut "
                  "player", heard == [("cut", "nudge")],
                  "the tab showing is %d and the players heard %s"
                  % (tab_bar().currentIndex(), heard or "nothing"))
        elif i == 4:
            print("\n4. Where a typed key lands")
            show_tab(PREVIEW_TAB)
            quiet()
            check("the preview player is on the screen before a key is "
                  "typed at it", found["preview"].isVisible(),
                  "the tab showing is %d and the preview player is %s"
                  % (tab_bar().currentIndex(),
                     "on the screen" if found["preview"].isVisible()
                     else "not on the screen"))
            heard = typed(found["preview"], QtCore.Qt.Key_Space)
            check("the space bar typed at the preview player reaches it",
                  heard == [("preview", "toggle")],
                  "the tab showing is %d, the keyboard is at %s and the "
                  "players heard %s"
                  % (tab_bar().currentIndex(),
                     "the program's window"
                     if app.activeWindow() is win() else repr(
                         app.activeWindow()),
                     heard or "nothing"))
            show_tab(CUT_TAB)
            quiet()
            check("the cut player is on the screen before a key is typed "
                  "at it", found["cut"].isVisible(),
                  "the tab showing is %d and the cut player is %s"
                  % (tab_bar().currentIndex(),
                     "on the screen" if found["cut"].isVisible()
                     else "not on the screen"))
            heard = typed(found["cut"], QtCore.Qt.Key_Space)
            check("the space bar typed at the cut player reaches it",
                  heard == [("cut", "toggle")],
                  "the tab showing is %d, the keyboard is at %s and the "
                  "players heard %s"
                  % (tab_bar().currentIndex(),
                     "the program's window"
                     if app.activeWindow() is win() else repr(
                         app.activeWindow()),
                     heard or "nothing"))
            quiet()
        elif i == 5:
            print("\n5. A player folded away is no player")
            show_tab(FILES_TAB)
            quiet()
            # The Multitrack tick off takes the Resolve preview box off
            # the screen, and the cut player sits inside it.
            needed("the Multitrack tick",
                   tick(vpm.T('Multitrack (one track per speaker)'))).click()
            app.processEvents()
        elif i == 6:
            # Waited for is the rebuild the tick sets off, seen on the tab
            # captions -- never on the visibility a check below reads.
            marks = tab_names()
            if marks != named[0]:
                named[0], named_still[0] = marks, 0
            else:
                named_still[0] += 1
            if named_still[0] < 5:
                raise NotYet("the tabs to stop being renamed, %r for %d "
                             "rounds" % (marks, named_still[0]))
            show_tab(CUT_TAB)
            check("the Multitrack tick is off and the cut player off the "
                  "screen before the transport is read",
                  not tick(vpm.T('Multitrack (one track per speaker)')
                           ).isChecked() and not found["cut"].isVisible(),
                  "the tick is %s and the cut player is %s, on tab %d"
                  % ("on" if tick(vpm.T('Multitrack (one track per '
                                        'speaker)')).isChecked() else "off",
                     "on the screen" if found["cut"].isVisible()
                     else "not on the screen", tab_bar().currentIndex()))
            check("on the Resolve tab with the cut player folded away all "
                  "nine transport entries are grey", not alive_now(),
                  "%d of %d alive: %s"
                  % (len(alive_now()), len(TRANSPORT), alive_now() or "none"))
            heard = set_off(TOGGLE)
            check("with the cut player folded away Play and pause reaches "
                  "no player at all", heard == [],
                  "the tab showing is %d and the players heard %s"
                  % (tab_bar().currentIndex(), heard or "nothing"))
            show_tab(PREVIEW_TAB)
            check("the preview player is still on the screen, so the three "
                  "readings above are not a transport greyed everywhere",
                  found["preview"].isVisible() and len(alive_now())
                  == len(TRANSPORT),
                  "the preview player is %s and %d of %d entries are alive, "
                  "grey: %s"
                  % ("on the screen" if found["preview"].isVisible()
                     else "not on the screen", len(alive_now()),
                     len(TRANSPORT), grey_now() or "none"))
            quiet()
        else:
            over.add("the pass")
            app.quit()
            return
        n[0] += 1
        patience[0] = 0
        QtCore.QTimer.singleShot(400, step)
    except NotYet as why:
        moved = life()
        if moved != sign[0]:
            sign[0], patience[0] = moved, 0
        patience[0] += 1
        if patience[0] > 60:
            bad.append("step %d waited for %s: 60 rounds of 400 ms with "
                       "the window at %r not moving at all, and it never "
                       "came" % (i, why, sign[0]))
            over.add("the pass")
            app.quit()
            return
        QtCore.QTimer.singleShot(400, step)
    except Exception:
        import traceback
        traceback.print_exc()
        bad.append("step %d fell over" % i)
        over.add("the pass")
        app.quit()


QtCore.QTimer.singleShot(500, step)
QtCore.QTimer.singleShot(150000, deadline())
# A window that falls over while it is being built takes the event loop
# with it, and the closing lines below are the only place that counts.
try:
    vpm.gui()
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("the window never came up: gui() fell over")

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
