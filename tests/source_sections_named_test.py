# -*- coding: utf-8 -*-
"""The program divides into named sections, and the ground uses none above.

A table on every run: each section with its length, how many top-level
names it takes out of other sections, and how many of its own are read
outside. The table is printed, not judged. Two judgements: that it can
be formed at all -- the file reads, more than one section, every
dividing line with a heading -- and that the ground, everything before
the first dividing line, reads no name defined above it. Names are
resolved through the scopes, so a local `label` is not the top-level
one; a name bound at the top in two sections counts for both.
"""
import ast
import bisect
import os
import sys
import time
import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# ---- the sections --------------------------------------------------
# A dividing line begins at column one with #--- and carries its
# heading on the right. Everything before the first one is the ground,
# and it has no heading of its own to carry.
GROUND = "(the ground)"
RULE = "#---"

src = the_program.text()
lines = src.split("\n")

names = [GROUND]
starts = [1]
blank = 0
for number, line in enumerate(lines, 1):
    if not line.startswith(RULE):
        continue
    heading = line.lstrip("#-").strip()
    if not heading:
        blank += 1
    names.append(heading)
    starts.append(number)


def section_at(lineno):
    """Which section a line of the program lies in."""
    return bisect.bisect_right(starts, lineno) - 1


def length_of(index):
    end = starts[index + 1] - 1 if index + 1 < len(starts) else len(lines)
    return end - starts[index] + 1


# ---- the scopes ----------------------------------------------------
# `label`, `loud` and `hint` are top-level functions and also the usual
# name of a local variable. Counting every mention would say the
# sections lean on each other far more than they do -- 113 mentions of
# `label` against 45 that really mean the function. So each mention is
# resolved: a scope that binds the name covers the one above it, unless
# the innermost scope declares it global.
SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef,
          ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)


class Scope(object):
    def __init__(self, kind, binds, globs=(), nonlocs=()):
        self.kind = kind
        self.binds = set(binds)
        self.globs = set(globs)
        self.nonlocs = set(nonlocs)


def bound_in(nodes):
    """What a scope binds, without looking into the scopes inside it.

    Returns the pairs (name, line), the names declared global and the
    names declared nonlocal. The last two are taken out of the first,
    because such a name is not this scope's own.
    """
    pairs, globs, nonlocs = [], set(), set()
    stack = list(nodes)
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)):
            pairs.append((node.name, node.lineno))
            continue
        if isinstance(node, SCOPES):
            continue
        if isinstance(node, ast.Global):
            globs.update(node.names)
            continue
        if isinstance(node, ast.Nonlocal):
            nonlocs.update(node.names)
            continue
        if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load):
            pairs.append((node.id, node.lineno))
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                plain = alias.asname or alias.name.split(".")[0]
                if plain != "*":
                    pairs.append((plain, node.lineno))
            continue
        elif isinstance(node, ast.ExceptHandler) and node.name:
            pairs.append((node.name, node.lineno))
        elif node.__class__.__name__.startswith("Match"):
            held = getattr(node, "name", None)
            if isinstance(held, str):
                pairs.append((held, node.lineno))
        for child in ast.iter_child_nodes(node):
            stack.append(child)
    dropped = globs | nonlocs
    return ([p for p in pairs if p[0] not in dropped], globs, nonlocs)


def parameters(args):
    """Every name a signature binds, keyword-only and starred included."""
    out = [a.arg for a in (list(getattr(args, "posonlyargs", []))
                           + list(args.args) + list(args.kwonlyargs))]
    for starred in (args.vararg, args.kwarg):
        if starred is not None:
            out.append(starred.arg)
    return out


def means_the_top(name, stack):
    """Whether this mention of *name* means the top-level one.

    A class body is stepped over from inside a function, the way Python
    steps over it: what a class binds is not visible to the functions
    written in it.
    """
    inner = stack[1:]
    if not inner:
        return True
    if name in inner[-1].globs:
        return True
    if name in inner[-1].nonlocs:
        return False
    for depth in range(len(inner) - 1, -1, -1):
        scope = inner[depth]
        if scope.kind == "class" and depth != len(inner) - 1:
            continue
        if name in scope.binds:
            return False
    return True


uses = []      # (name, line) for every mention that means the top level


def read(node, stack):
    """Walk one node, carrying the scopes it stands in."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        for mark in node.decorator_list:
            read(mark, stack)
        args = node.args
        for value in list(args.defaults) + [v for v in args.kw_defaults if v]:
            read(value, stack)
        for arg in (list(getattr(args, "posonlyargs", [])) + list(args.args)
                    + list(args.kwonlyargs) + [args.vararg, args.kwarg]):
            if arg is not None and arg.annotation is not None:
                read(arg.annotation, stack)
        if node.returns is not None:
            read(node.returns, stack)
        pairs, globs, nonlocs = bound_in(node.body)
        held = set(n for n, _line in pairs) | set(parameters(args))
        inner = stack + [Scope("function", held - globs - nonlocs,
                               globs, nonlocs)]
        for statement in node.body:
            read(statement, inner)
        return
    if isinstance(node, ast.Lambda):
        args = node.args
        for value in list(args.defaults) + [v for v in args.kw_defaults if v]:
            read(value, stack)
        pairs, globs, nonlocs = bound_in([node.body])
        held = set(n for n, _line in pairs) | set(parameters(args))
        read(node.body, stack + [Scope("function", held, globs, nonlocs)])
        return
    if isinstance(node, ast.ClassDef):
        for mark in node.decorator_list:
            read(mark, stack)
        for base in list(node.bases) + [k.value for k in node.keywords]:
            read(base, stack)
        pairs, globs, nonlocs = bound_in(node.body)
        inner = stack + [Scope("class", set(n for n, _l in pairs),
                               globs, nonlocs)]
        for statement in node.body:
            read(statement, inner)
        return
    if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp,
                         ast.GeneratorExp)):
        # The first thing walked over is read where the comprehension
        # stands; everything else inside it.
        read(node.generators[0].iter, stack)
        held = set()
        for gen in node.generators:
            pairs, _g, _n = bound_in([gen.target])
            held |= set(n for n, _line in pairs)
        inner = stack + [Scope("comprehension", held)]
        for number, gen in enumerate(node.generators):
            if number:
                read(gen.iter, inner)
            for condition in gen.ifs:
                read(condition, inner)
        for field in ("elt", "key", "value"):
            part = getattr(node, field, None)
            if part is not None:
                read(part, inner)
        return
    if isinstance(node, ast.Name):
        if isinstance(node.ctx, ast.Load) and means_the_top(node.id, stack):
            uses.append((node.id, node.lineno))
        return
    for child in ast.iter_child_nodes(node):
        read(child, stack)


# ---- the table -----------------------------------------------------
unreadable = ""
tree = None
try:
    tree = ast.parse(src)
except SyntaxError as why:
    unreadable = ", and it does not read past line %s" % why.lineno

home = {}      # top-level name -> the sections that bind it
if tree is not None:
    pairs, _globs, _nonlocs = bound_in(tree.body)
    for name, line in pairs:
        home.setdefault(name, set()).add(section_at(line))
    for statement in tree.body:
        read(statement, [Scope("module", set(home))])

inward = dict((i, set()) for i in range(len(starts)))
outward = dict((i, set()) for i in range(len(starts)))
for name, line in uses:
    where = home.get(name)
    if not where:
        continue
    here = section_at(line)
    if here in where:
        continue
    inward[here].add(name)
    for born in where:
        outward[born].add(name)

print("The sections of the program, and what crosses between them")
print("  %-34s %7s %6s %6s" % ("section", "lines", "in", "out"))
for index, heading in enumerate(names):
    print("  %-34s %7d %6d %6d"
          % ((heading or "(no heading)")[:34], length_of(index),
             len(inward[index]), len(outward[index])))
print("  %-34s %7d %6d %6d"
      % ("all of them", len(lines),
         sum(len(v) for v in inward.values()),
         sum(len(v) for v in outward.values())))

print("\nWhat the table is held to")
check("the program divides into sections that carry headings",
      tree is not None and len(starts) > 1 and blank == 0,
      "%d sections over %d lines, %d dividing line(s) with no heading; "
      "wanted 2 sections or more and none unheaded%s"
      % (len(starts), len(lines), blank, unreadable))

above = sorted(inward[0])
check("the ground section uses no name defined above it",
      tree is not None and not above,
      "%d name(s) reached up out of the ground, wanted 0%s%s"
      % (len(above), ": " + ", ".join(above[:8]) if above else "",
         unreadable))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
