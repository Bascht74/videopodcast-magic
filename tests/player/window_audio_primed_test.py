# -*- coding: utf-8 -*-
"""Every sound output the program makes is primed against PySide's lock.

In PySide6 6.12 the first disconnectNotify() of a QAudioOutput asks
Python, and asked from Qt's media thread under Qt's lock it can wait for
good. audio_sink() asks once on the thread that holds Python. In order:
audio_sink() with a stand-in output that notes what is done to it, then
the source of the whole program, where no output may be made but there.
The stand-in cannot say whether PySide keeps the answer; it says whether
the question is asked.
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


class Signal(object):
    """A signal that notes every connect and disconnect, with the receiver."""

    def __init__(self, notes):
        """Writes into the output's own notes."""
        self.notes = notes

    def connect(self, receiver):
        """Noted."""
        self.notes.append(("connect", receiver))

    def disconnect(self, receiver):
        """Noted."""
        self.notes.append(("disconnect", receiver))


class QAudioOutput(object):
    """Stands in for Qt's sound output and notes what is done to it."""
    made = []

    def __init__(self, parent=None):
        """Made under a parent, with no notes yet."""
        self.notes = []
        self.volumeChanged = Signal(self.notes)
        QAudioOutput.made.append(self)

    def setVolume(self, value):
        """Noted."""
        self.notes.append(("setVolume", value))

    def setMuted(self, value):
        """Noted."""
        self.notes.append(("setMuted", value))


class QtMultimedia(object):
    """Stands in for the module audio_sink is handed."""
    QAudioOutput = QAudioOutput


print("audio_sink():")
out = vpm.audio_sink(QtMultimedia, None)
notes = out.notes if isinstance(out, QAudioOutput) else []
pairs = [(what, who) for what, who in notes
         if what in ("connect", "disconnect")]
check("a sound output is connected and let go as it is made",
      len(pairs) == 2 and pairs[0][0] == "connect"
      and pairs[1][0] == "disconnect" and pairs[0][1] is pairs[1][1],
      "%d outputs made, what was done to it: %s"
      % (len(QAudioOutput.made), [n[0] for n in notes]))

print("the source:")
made_elsewhere = []
for here, _dirs, files in os.walk(the_program.FOLDER):
    for name in files:
        if not name.endswith(".py"):
            continue
        path = os.path.join(here, name)
        tree = ast.parse(io.open(path, encoding="utf-8").read())
        inside = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "audio_sink":
                inside.update(id(n) for n in ast.walk(node))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or id(node) in inside:
                continue
            called = getattr(node.func, "attr", getattr(node.func, "id", ""))
            if called == "QAudioOutput":
                made_elsewhere.append("%s:%d" % (
                    os.path.relpath(path, the_program.FOLDER), node.lineno))
check("no sound output is made except through audio_sink",
      not made_elsewhere,
      "%d made elsewhere: %s" % (len(made_elsewhere),
                                 "; ".join(made_elsewhere) or "none"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
