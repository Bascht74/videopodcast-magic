# -*- coding: utf-8 -*-
"""A name the program writes on itself is held nowhere as a stale copy.

Read out of the source: every name written as `PROGRAM.<name> = ...`
over all the pieces, against every name a piece binds at its top --
the seam's own line, because a bend on the program reaches a piece
exactly where the piece's namespace already carries the name. Measured
on the running program: `PROGRAM` carries the way in's names themselves
and not a copy, a bent name reaches the piece that holds it, and the
same name written on `PROGRAM` does not.

That last one pins the seam as it stands, and on purpose: the guard
above it is only worth having while a write on `PROGRAM` stays behind,
so a red there says the guard may go with it. `PROGRAM.__dict__ =
globals()` is the seam itself and no case of it. Two things the source
does not show: a write made through `setattr`, and a name a piece puts
at its top only while it runs, out of a `global` inside a function.
"""
import ast
import os
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


def under_the_folder(path):
    """One piece's path as it is printed: below the program's folder."""
    return os.path.relpath(os.path.abspath(path),
                           the_program.FOLDER).replace(os.sep, "/")


def briefly(value):
    """One value as a failure line carries it, cut short.

    A piece holds whole sentences and web addresses, and the line that
    reaches the builder is read there and nowhere else.
    """
    said = repr(value)
    return said if len(said) < 48 else said[:45] + "..."


def bound_at_top(body):
    """Every name a piece binds at its top, as (name, line).

    Exactly what lands in the piece's own namespace, and so exactly
    what a name bent on the program reaches: `OneName.__setattr__`
    writes into a piece where `name in piece.__dict__`, and nowhere
    else. A function, a class and a comprehension are stepped over --
    what they bind is theirs and not the piece's -- while an `if` or a
    `try` at the top is walked into, because what stands in it binds at
    the top all the same.
    """
    out = []
    stack = list(body)
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)):
            out.append((node.name, node.lineno))
            continue
        if isinstance(node, (ast.Lambda, ast.ListComp, ast.SetComp,
                             ast.DictComp, ast.GeneratorExp)):
            continue
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                plain = alias.asname or alias.name.split(".")[0]
                if plain != "*":
                    out.append((plain, node.lineno))
            continue
        if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load):
            out.append((node.id, node.lineno))
        elif isinstance(node, ast.ExceptHandler) and node.name:
            out.append((node.name, node.lineno))
        for child in ast.iter_child_nodes(node):
            stack.append(child)
    return out


print("1. What the source says")
# The way in is not a piece here: `PROGRAM.__dict__` is its namespace,
# so a name written on PROGRAM is the way in's own name and can never
# be a stale copy of itself. Everything else is a piece.
PIECES = the_program.pieces()
ENTRY = under_the_folder(the_program.SCRIPT)

written = {}       # name -> (piece, line) where it is first written
top = {}           # name -> (piece, line) where a piece first binds it
for where, body in PIECES:
    tree = ast.parse(body)
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Attribute)
                and isinstance(node.ctx, ast.Store)
                and isinstance(node.value, ast.Name)
                and node.value.id == "PROGRAM"):
            continue
        # The line that makes the whole mechanism, not a case of it.
        if node.attr == "__dict__":
            continue
        written.setdefault(node.attr, (where, node.lineno))
    if where == ENTRY:
        continue
    for name, line in bound_at_top(tree.body):
        top.setdefault(name, (where, line))

print("   %d name(s) written on the program: %s"
      % (len(written), ", ".join(sorted(written)) or "none"))
print("   %d name(s) bound at the top of a piece, over %d piece(s)"
      % (len(top), len(PIECES) - 1))

both = sorted(set(written) & set(top))
say = ["%s bound at %s line %d, written at %s line %d"
       % (name, top[name][0], top[name][1],
          written[name][0], written[name][1]) for name in both]
check("no name the program writes on itself is bound at the top of a piece",
      bool(written) and bool(top) and not both,
      "%d name(s) written on the program, %d bound at the top of a piece "
      "over %d piece(s), %d in both, wanted at least one of the first two "
      "and 0 in both: %s"
      % (len(written), len(top), len(PIECES) - 1, len(both),
         "; ".join(say[:4]) or "none"))

print("\n2. What the running program says")
# Why the guard above is needed at all. The program is run, not read:
# the difference between a bend and a write on PROGRAM is a difference
# in what happens, and no reading of the source shows it.
BENT = "the test bent this name on the program"
WRITTEN = "the program wrote this name on its own object"

vpm = None
trouble = ""
try:
    vpm = the_program.load()
except Exception as why:
    trouble = "%s: %s" % (type(why).__name__, why)

same = vpm is not None and vpm.PROGRAM.__dict__ is vars(vpm)
check("the program's own object carries the way in's names, not a copy",
      same,
      "PROGRAM's names are %s the way in's, %d name(s) on "
      "PROGRAM against %d in the way in%s"
      % ("the same dictionary as" if same else "another dictionary than",
         len(vpm.PROGRAM.__dict__) if vpm is not None else 0,
         len(vars(vpm)) if vpm is not None else 0,
         "; the program did not run: " + trouble if vpm is None else ""))

# A name to bend: one a piece really took out of the program, plain
# text so that bending it can disturb nothing, and none of the names
# the program writes on itself. It is put back afterwards.
probe = None       # (the piece's name, the piece, the name in it)
if vpm is not None:
    for path, piece in vpm.PIECES.items():
        if "PROGRAM" not in piece.__dict__:
            continue
        for name in sorted(piece.__dict__):
            if name.startswith("_") or name in written:
                continue
            value = piece.__dict__[name]
            if isinstance(value, str) and vars(vpm).get(name) is value:
                probe = (under_the_folder(path), piece, name)
                break
        if probe is not None:
            break

reached = stayed = False
took = "nothing"
after_bend = after_write = "nothing was bent"
if probe is not None:
    where, piece, name = probe
    before = piece.__dict__[name]
    setattr(vpm, name, BENT)
    after_bend = piece.__dict__.get(name)
    reached = after_bend == BENT
    setattr(vpm.PROGRAM, name, WRITTEN)
    after_write = piece.__dict__.get(name)
    stayed = after_write != WRITTEN
    took = vars(vpm).get(name)
    setattr(vpm, name, before)

named = "%s in %s" % (probe[2], probe[0]) if probe is not None \
    else "no piece held a name it took out of the program"

check("a name bent on the program reaches the piece that holds it",
      probe is not None and reached,
      "%s: after the bend the piece holds %s, wanted %s"
      % (named, briefly(after_bend), briefly(BENT)))

check("a name written on the program's own object stays out of the piece",
      probe is not None and stayed,
      "%s: after the write the piece holds %s and the way in %s, wanted "
      "anything but %s in the piece"
      % (named, briefly(after_write), briefly(took), briefly(WRITTEN)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
