# -*- coding: utf-8 -*-
"""A bare start, as the installed command makes it, opens the window and ends.

In a child, offscreen: the folder loaded under its own name and main()
called with nothing on the line, as pip's starter does; once the window
stands the child closes it. Judged: the window stood, nothing was said
in front of it, closing it ended the start with 0. The limit: pip's own
starter is not built, and the event loop is wrapped to look and close.
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
import json
import shutil
import subprocess
import tempfile
import time
import the_program

SCRIPT = the_program.SCRIPT
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    """One judgement: a line in the report, and a name in bad if it fell."""
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# What pip's starter does -- import the package by its name, call main()
# -- with the event loop wrapped: once the program's window stands, what
# it shows is written down and the window is closed as a user closes it.
CHILD = r"""
import importlib.util, json, os, sys, time
SCRIPT, SEEN = sys.argv[1:3]
sys.argv = ["videopodcast-magic"]
from PySide6 import QtCore, QtWidgets
real = QtWidgets.QApplication.exec
began = time.time()


def look():
    app = QtWidgets.QApplication.instance()
    name = sys.modules["videopodcast_magic"].DISPLAY_NAME
    for w in app.topLevelWidgets():
        if w.isVisible() and name in w.windowTitle():
            with open(SEEN, "w", encoding="utf-8") as f:
                json.dump({"title": w.windowTitle(),
                           "waited": time.time() - began}, f)
            return w.close()
    if time.time() - began > 60:
        return app.quit()
    QtCore.QTimer.singleShot(100, look)


def exec_(*a):
    QtCore.QTimer.singleShot(0, look)
    return real(*a)


QtWidgets.QApplication.exec = staticmethod(exec_)
spec = importlib.util.spec_from_file_location(
    "videopodcast_magic", SCRIPT,
    submodule_search_locations=[os.path.dirname(os.path.abspath(SCRIPT))])
m = importlib.util.module_from_spec(spec)
sys.modules["videopodcast_magic"] = m
spec.loader.exec_module(m)
sys.exit(m.main())
"""

work = tempfile.mkdtemp(prefix="vpm_barestart_")
child = os.path.join(work, "starter.py")
seen_file = os.path.join(work, "seen.json")
with open(child, "w", encoding="utf-8") as f:
    f.write(CHILD)
env = dict(os.environ, QT_QPA_PLATFORM="offscreen")
try:
    ran = subprocess.run([sys.executable, child, SCRIPT, seen_file], env=env,
                         capture_output=True, text=True, errors="replace",
                         timeout=240)
    code, said = ran.returncode, (ran.stdout + ran.stderr).strip()
except subprocess.TimeoutExpired as e:
    code, said = None, "still running after %d s" % e.timeout
seen = {}
if os.path.exists(seen_file):
    with open(seen_file, encoding="utf-8") as f:
        seen = json.load(f)

print("1. The start, as the installed command makes it")
check("a bare start opens the program's window", bool(seen.get("title")),
      "no window stood; code %s, said %r"
      % (code, said[-200:]) if not seen.get("title")
      else "%r after %.2f s" % (seen["title"], seen["waited"]))
check("and says nothing in front of it", said == "",
      "%d characters: %r" % (len(said), said[-200:]))
check("closing the window ends the start with 0",
      bool(seen.get("title")) and code == 0,
      "code %s after %s" % (code, "the window closed" if seen.get("title")
                            else "no window"))

shutil.rmtree(work, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
