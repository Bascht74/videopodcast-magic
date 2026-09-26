# -*- coding: utf-8 -*-
"""A media player is stopped only when it runs, never when it never started.

stop() on a player that never started builds what lies behind it and
can wait for a lock inside Qt for good. In order: stop_if_running()
with stand-in players -- one never started, one playing, one paused,
all three handed in at once -- and then the source of player/ and ui/,
where no media player may be stopped except through it. The stand-ins
cannot say whether Qt blocks; they say who is asked to stop.
"""
PLATFORM_BOUND = False
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import ast
import io
import time
import the_program

began = time.time()
vpm = the_program.load()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


class QMediaPlayer(object):
    """The three states under the names Qt gives them, and nothing else."""
    StoppedState = "stopped"
    PlayingState = "playing"
    PausedState = "paused"


class QtMultimedia(object):
    """Stands in for the module the helper is handed."""
    QMediaPlayer = QMediaPlayer


class StandIn(object):
    """A player that answers its state and counts the stops it is given."""

    def __init__(self, state):
        """Stand in one state, with no stop given yet."""
        self.state, self.stops = state, 0

    def playbackState(self):
        """The state it was made in."""
        return self.state

    def stop(self):
        """Count the stop."""
        self.stops += 1


print("stop_if_running():")
never = StandIn(QMediaPlayer.StoppedState)
vpm.stop_if_running(QtMultimedia, never)
check("a player that never started is not stopped", never.stops == 0,
      "%d stop() on a player in the stopped state" % never.stops)
playing = StandIn(QMediaPlayer.PlayingState)
vpm.stop_if_running(QtMultimedia, playing)
check("a playing player is stopped", playing.stops == 1,
      "%d stop() on a player in the playing state" % playing.stops)
paused = StandIn(QMediaPlayer.PausedState)
vpm.stop_if_running(QtMultimedia, paused)
check("a paused player is stopped, since it still holds its file",
      paused.stops == 1,
      "%d stop() on a player in the paused state" % paused.stops)
three = [StandIn(QMediaPlayer.StoppedState),
         StandIn(QMediaPlayer.PlayingState),
         StandIn(QMediaPlayer.PausedState)]
vpm.stop_if_running(QtMultimedia, *three)
check("each of three handed in at once is asked on its own",
      [p.stops for p in three] == [0, 1, 1],
      "stops %s for stopped, playing, paused -- 0, 1, 1 wanted"
      % [p.stops for p in three])

# The receivers the player and the window hold their media players
# under. A timer's stop() is free and stays out: clock, watchdog.
MEDIA = ("player", "track", "audio", "videos")
print("the source:")
bare = []
for piece in ("player", "ui"):
    path = os.path.join(the_program.FOLDER, piece, "__init__.py")
    tree = ast.parse(io.open(path, encoding="utf-8").read())
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "stop"):
            continue
        held = node.func.value
        while isinstance(held, ast.Subscript):
            held = held.value
        name = getattr(held, "attr", getattr(held, "id", ""))
        if name in MEDIA:
            bare.append("%s/__init__.py:%d %s.stop()"
                        % (piece, node.lineno, name))
check("no media player is stopped except through stop_if_running",
      not bare, "; ".join(bare) or "none")

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
