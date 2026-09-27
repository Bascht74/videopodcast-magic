# -*- coding: utf-8 -*-
"""The cut tab's preview measures and builds nothing of its own.

The preview is the run itself, stopped before anything is written: it
may not reach a measurement or a handover builder only the window has.
Read out of the source, every piece of the program: from make_preview,
by name, every function it names -- called, or handed on as a
callback, by a bare name, through PROGRAM. or through self. -- and
every one those name, to the end. Then one line per window-only
function that may not be among them. The limit: a name is followed by
its spelling, so a function reached only through another object's
attribute is not followed.
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
import time
import the_program

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def definitions():
    """Every function in the program by its name: [(piece, node)].

    Nested and method definitions too: the preview's own helpers stand
    inside make_preview, and one of them is what this test looks for.
    """
    found = {}
    for piece, body in the_program.pieces():
        for node in ast.walk(ast.parse(body)):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                found.setdefault(node.name, []).append((piece, node))
    return found


def named_in(node):
    """The names a function reaches: bare, PROGRAM.x and self.x."""
    names = set()
    for x in ast.walk(node):
        if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load):
            names.add(x.id)
        elif (isinstance(x, ast.Attribute) and isinstance(x.value, ast.Name)
              and x.value.id in ("PROGRAM", "self")):
            names.add(x.attr)
    return names


def reached(start, defs):
    """{name: the name it was reached from} for all *start* reaches."""
    came_from = {start: None}
    todo = [start]
    while todo:
        name = todo.pop()
        for _piece, node in defs.get(name, ()):
            for other in named_in(node):
                if other in defs and other not in came_from:
                    came_from[other] = name
                    todo.append(other)
    return came_from


def road(name, came_from):
    """The chain from make_preview to *name*, as one line."""
    chain = [name]
    while came_from.get(chain[-1]):
        chain.append(came_from[chain[-1]])
    return " -> ".join(reversed(chain))


def verdict(name, came_from):
    """(not reached, evidence) for one window-only function.

    With no preview found nothing was followed, and that is no answer.
    """
    if not came_from:
        return False, "%s not asked: no make_preview to follow" % name
    if name not in came_from:
        return True, "%s not reached from make_preview (%d functions " \
                     "reached)" % (name, len(came_from))
    return False, "reached: %s" % road(name, came_from)


DEFS = definitions()
print("The preview in the source")
where = ["%s:%d" % (piece, node.lineno)
         for piece, node in DEFS.get("make_preview", ())]
check("the cut tab's preview is found in the program's source",
      len(where) == 1,
      "make_preview defined %d times (%s), wanted once"
      % (len(where), ", ".join(where) or "nowhere"))
CAME_FROM = reached("make_preview", DEFS) if where else {}

print("\nWhat it may not reach")
ok, why = verdict("off_speakers", CAME_FROM)
check("the preview builds no speakers of its own (off_speakers)", ok, why)
ok, why = verdict("run_window_take", CAME_FROM)
check("the preview cuts no window of its own (run_window_take)", ok, why)
ok, why = verdict("speakers_all_on_window_axis", CAME_FROM)
check("the preview places no speakers on an axis of its own", ok, why)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
