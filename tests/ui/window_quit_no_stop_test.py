# -*- coding: utf-8 -*-
"""Quitting the window asks no media player to stop.

stop() at quit kept Python while it waited for a lock inside Qt's media
backend, whose thread holding that lock could be waiting for Python:
the window then never closed. In order: the window comes up empty;
every media player its widgets hold is swapped for a stand-in that says
it is playing and writes down what it is asked; the application quits
the way it does when the window is closed. The stand-ins cannot say
whether Qt blocks; they say whether the quit asks.
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
import time
import the_program
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
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


try:
    from PySide6 import QtMultimedia
except ImportError:
    QtMultimedia = None
if QtMultimedia is None:
    print("SKIPPED: this PySide6 has no QtMultimedia, so the window holds "
          "no media player -- install a PySide6 with it to bring it back")
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


class StandIn(object):
    """A media player that says it plays and writes down what it is asked."""

    def __init__(self, where):
        """Named after the widget and the attribute it stands in."""
        self.where, self.asked = where, []

    def playbackState(self):
        """Playing: a player that runs is the one a stop would reach."""
        self.asked.append("playbackState")
        return QtMultimedia.QMediaPlayer.PlayingState

    def __getattr__(self, name):
        """Anything else: noted, and answered with nothing."""
        def answer(*args, **kwargs):
            self.asked.append(name)
        return answer


stand_ins = []
# The attributes the player widgets hold their media players under.
HELD = ("player", "track", "audio", "videos")


def swap():
    """Put a stand-in where each media player of the window stood."""
    for top in app.topLevelWidgets():
        for widget in [top] + top.findChildren(QtWidgets.QWidget):
            for name in HELD:
                held = widget.__dict__.get(name)
                if isinstance(held, QtMultimedia.QMediaPlayer):
                    one = StandIn("%s.%s" % (type(widget).__name__, name))
                    setattr(widget, name, one)
                    stand_ins.append(one)
                elif isinstance(held, list):
                    for k, item in enumerate(held):
                        if isinstance(item, QtMultimedia.QMediaPlayer):
                            one = StandIn("%s.%s[%d]"
                                          % (type(widget).__name__, name, k))
                            held[k] = one
                            stand_ins.append(one)


def step():
    """Swap the players and quit, in one go: nothing plays in between."""
    try:
        swap()
    finally:
        app.quit()


# gui() builds the whole window before its loop starts, so the first
# turn of the loop finds every player there is.
QtCore.QTimer.singleShot(0, step)
# The guard: a quit that never comes back still reaches the lines below.
QtCore.QTimer.singleShot(60000, app.quit)
sys.argv = ["videopodcast_magic.py"]
vpm.gui()

where = sorted(one.where for one in stand_ins)
check("the window holds media players to stand in for",
      "Player.player" in where and "Player.track" in where,
      "%d stood in for: %s; the viewer's player and sound track wanted"
      % (len(where), where))
stopped = ["%s %s" % (one.where, one.asked) for one in stand_ins
           if "stop" in one.asked]
check("quitting the window stops no media player", not stopped,
      "%d of %d asked to stop: %s"
      % (len(stopped), len(stand_ins), "; ".join(stopped) or "none"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
