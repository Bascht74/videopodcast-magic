# -*- coding: utf-8 -*-
"""A project of the same name is never taken over unasked, nor made twice.

open_or_create_project against a stand-in project manager that refuses
a taken name, as Resolve does. In turn: a project that cannot be made
is a stop; cancel stops before anything is made; one that will not open
is a stop; "new" takes the first free number after the name; a refused
new name is a stop; and with every number taken, nothing is made.
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
import the_program
import contextlib
import io
import time
import resolve_stand_in as stand

began = time.time()
vpm = the_program.load()
vpm.set_language("en")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


NAME = "Episode"


def open_or_make(pm, answer=None):
    """(project, kind, the error) for one call, the answer preselected."""
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            p, kind = vpm.open_or_create_project(pm, NAME, answer)
            return p, kind, None
        except RuntimeError as e:
            return None, None, e


print("1. Nothing of that name yet")
pm = stand.ProjectManager(refuse_names=[NAME])
p, kind, error = open_or_make(pm)
check("a project Resolve will not make is a stop, not a None",
      p is None and error is not None and NAME in str(error),
      "project %r, error %r" % (p, error))

print("\n2. The name is taken")
pm = stand.ProjectManager(names=[NAME])
p, kind, error = open_or_make(pm, "abort")
check("cancel stops before anything is made or opened",
      error is not None and not pm.made and pm.count("LoadProject") == 0,
      "error %r, made %r, opened %d times"
      % (error, pm.made, pm.count("LoadProject")))
pm = stand.ProjectManager(names=[NAME], refuse=["LoadProject"])
p, kind, error = open_or_make(pm, "update")
check("a project that will not open is a stop",
      p is None and error is not None and pm.count("LoadProject") == 1,
      "project %r, error %r" % (p, error))
pm = stand.ProjectManager(names=[NAME, NAME + " 2"])
p, kind, error = open_or_make(pm, "new")
check("new beside it takes the first free number",
      kind == "created" and pm.made == [NAME + " 3"]
      and p is pm.projects.get(NAME + " 3"),
      "kind %r, made %r, error %r" % (kind, pm.made, error))
pm = stand.ProjectManager(names=[NAME], refuse_names=[NAME + " 2"])
p, kind, error = open_or_make(pm, "new")
check("a new name Resolve will not make is a stop",
      p is None and error is not None and NAME + " 2" in str(error)
      and not pm.made,
      "project %r, error %r, made %r" % (p, error, pm.made))
pm = stand.ProjectManager(names=[NAME] + ["%s %d" % (NAME, k)
                                          for k in range(2, 100)])
p, kind, error = open_or_make(pm, "new")
check("with every number taken nothing is made",
      p is None and error is not None and not pm.made
      and pm.count("CreateProject") == 0,
      "project %r, error %r, CreateProject asked %d times"
      % (p, error, pm.count("CreateProject")))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
