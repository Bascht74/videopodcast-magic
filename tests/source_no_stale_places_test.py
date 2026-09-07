# -*- coding: utf-8 -*-
"""No docstring sends a reader to a place its own piece does not hold.

A function that moves house keeps its docstring, and a docstring that
said "Outside gui() because ..." then names a thing the new file does
not contain. The sentence still reads as an explanation, so nobody
stumbles over it -- and whoever follows it looks for `gui()` in a file
that has none.

Measured 7.9.2026, after eight moves out of the window in one night:
eight such sentences stood in six pieces, and nothing was watching.
The judgement is narrow on purpose -- only `gui()`, which is the one
name the pieces were cut away from -- and the table beside it prints
every position phrase there is, so the next one that starts to
accumulate can be seen before it needs a sweep.

The limit of the method: a docstring that says "this file" is right or
wrong depending on what it means, and no reading tells them apart.
Those are printed, never judged.
"""
import ast
import os
import re
import sys
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


GUI = re.compile(r"[Oo]utside `?gui\(\)|\bin gui\(\)|\bgui\(\) *\bbelow|"
                 r"\bgui\(\) *\babove")
ANY_PLACE = re.compile(r"[Oo]utside `?gui\(\)|further down|further up|"
                       r"in this file|this file|at the top of this file|"
                       r"beside gui")

print("1. Where a docstring names a place")
found, wrong = [], []
for where, body in the_program.pieces():
    piece = os.path.basename(os.path.dirname(where)) or "the way in"
    tree = ast.parse(body)
    has_gui = any(isinstance(n, ast.FunctionDef) and n.name == "gui"
                  for n in tree.body)
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.FunctionDef,
                                 ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        said = ast.get_docstring(node) or ""
        hit = ANY_PLACE.search(said)
        if not hit:
            continue
        name = getattr(node, "name", "(the module)")
        found.append((piece, name, hit.group(0)))
        if GUI.search(said) and not has_gui:
            wrong.append("%s/%s" % (piece, name))

print("  %-12s %-30s %s" % ("piece", "name", "the phrase"))
for piece, name, phrase in found:
    print("  %-12s %-30s %r" % (piece, name, phrase))
print("  %d phrase(s) over %d pieces" % (len(found), len(the_program.pieces())))

check("no docstring names gui() in a piece that does not hold it",
      not wrong,
      "%d of %d place phrases wrong: %s"
      % (len(wrong), len(found), wrong[:3] or "none"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
