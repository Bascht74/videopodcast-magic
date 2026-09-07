#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""What a candidate really costs to move, counted five ways instead of one.

    python3 price.py <program folder> <from piece> <to piece> <name> [<name> ...]

    python3 price.py /tmp/.../videopodcast_magic ui bearings make_time_axis

A screen that counts only "names that stand on the programme late" is
wrong in both directions, and by different amounts per candidate. The
six terms below are what it misses. Every one is read out of the tree
with `ast` and `symtable`; none is guessed.

  A  the receiving piece already has it -- its own name, or already at
     its head.                                                    0 each
  B  bound in the way in, or in a piece read ABOVE the receiving one:
     a new head line there.                                      +1 each
  C  forced `PROGRAM.` read at the use -- the name lives in the piece
     being left, in a piece read out of it, or in a piece read BELOW
     the receiving one (the fifth kind of head line).             +1 each
  E  something left behind still calls the moved name, so the piece it
     left has to fetch it back.                                 +1 if so
  F  head lines in the piece it left whose last reader was the moved
     code. They have to go: source_no_loose_ends is red on a head line
     nobody reads.                                                -1 each
  D  a PROGRAM. read the RECEIVING piece already had for the moved name
     -- it retires when the name lands there.                  -1 each

    paid = B + C + E      net = B + C + E - F - D

A screen counts only the part of C that lives in the piece being left,
so its error per candidate is  B + E - F  -- and it has no sign: on one
row here it was 3.5x optimistic, on the next it said free and the move
cost three.

Read positions come from the order of beside() calls in the way in, so
this needs no table kept by hand.
"""
import ast
import builtins
import os
import symtable
import sys


def read_order(folder):
    """The pieces in the order the way in reads them, by beside() call."""
    src = open(os.path.join(folder, "__init__.py"), encoding="utf-8").read()
    order, seen = [], set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "beside" and node.args \
                and isinstance(node.args[0], ast.Constant):
            name = node.args[0].value
            if name not in seen:
                seen.add(name)
                order.append((node.lineno, name))
    order.sort()
    return [n for _l, n in order]


def owners(folder):
    """Which file each name is really defined in -- head lines are not that."""
    own = {}
    for d, _s, fs in os.walk(folder):
        for f in fs:
            if not f.endswith(".py"):
                continue
            rel = os.path.relpath(os.path.join(d, f), folder)
            piece = "" if rel == "__init__.py" else rel.split(os.sep)[0]
            tree = ast.parse(open(os.path.join(d, f), encoding="utf-8").read())
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                     ast.ClassDef)):
                    own.setdefault(node.name, set()).add(piece)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if piece == "":
                        for a in node.names:
                            own.setdefault(a.asname or a.name.split(".")[0],
                                           set()).add(piece)
                elif isinstance(node, ast.Assign):
                    for t in node.targets:
                        # `A, B, C = ...` binds three names, and the
                        # TYPE_* constants of choices/ are written that
                        # way: a reader that only knows ast.Name calls
                        # them defined nowhere and prices them as a
                        # forced read. Measured here on TYPE_CONTENT
                        # and TYPE_INTRO before this line stood.
                        for one in (t.elts if isinstance(t, (ast.Tuple, ast.List))
                                    else [t]):
                            if not isinstance(one, ast.Name):
                                continue
                            v = node.value
                            head = (isinstance(v, ast.Attribute)
                                    and isinstance(v.value, ast.Name)
                                    and v.value.id == "PROGRAM"
                                    and v.attr == one.id)
                            if not head:
                                own.setdefault(one.id, set()).add(piece)
    return own


def piece_file(folder, piece):
    return os.path.join(folder, piece, "__init__.py")


def head_of(path):
    head = {}
    for node in ast.parse(open(path, encoding="utf-8").read()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            v = node.value
            if isinstance(v, ast.Attribute) and isinstance(v.value, ast.Name) \
                    and v.value.id == "PROGRAM":
                head[node.targets[0].id] = node.lineno
    return head


def own_of(path):
    out = set()
    for node in ast.parse(open(path, encoding="utf-8").read()).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(node.name)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    v = node.value
                    if not (isinstance(v, ast.Attribute)
                            and isinstance(v.value, ast.Name)
                            and v.value.id == "PROGRAM" and v.attr == t.id):
                        out.add(t.id)
    return out


def reads_of(path, names):
    """The global names each of those functions reads, and their line spans."""
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    table = symtable.symtable(src, path, "exec")
    spans = {n.name: (n.lineno, n.end_lineno) for n in tree.body
             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
             and n.name in names}
    missing = [n for n in names if n not in spans]
    if missing:
        raise SystemExit("not at the top level of %s: %s" % (path, missing))

    def block(name):
        def find(tb):
            for ch in tb.get_children():
                if ch.get_name() == name and ch.get_lineno() == spans[name][0]:
                    return ch
                got = find(ch)
                if got:
                    return got
        return find(table)

    out = {}
    for name in names:
        got, tb = set(), block(name)

        def walk(t):
            for s in t.get_symbols():
                if s.is_global():
                    got.add(s.get_name())
            for ch in t.get_children():
                walk(ch)
        walk(tb)
        out[name] = got - set(dir(builtins))
    return spans, out


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 2
    folder, frm, to, names = argv[0], argv[1], argv[2], list(argv[3:])
    order = read_order(folder)
    own = owners(folder)
    where = {p: i for i, p in enumerate(order)}
    from_path, to_path = piece_file(folder, frm), piece_file(folder, to)
    to_head, to_own = head_of(to_path), own_of(to_path)
    spans, reads = reads_of(from_path, names)

    # Everything the whole group reads, minus the group itself.
    need = set()
    for n in names:
        need |= reads[n]
    need -= set(names)

    A, B, C = [], [], []
    for n in sorted(need):
        if n in to_own or n in to_head:
            A.append(n)
            continue
        lives = own.get(n, {"(nowhere)"})
        below = all(w != "" and where.get(w, 99) > where.get(to, -1)
                    for w in lives)
        if frm in lives or below:
            C.append((n, sorted(lives)))
        else:
            B.append((n, sorted(lives)))

    # E: a reader of a moved name left behind, anywhere outside the group.
    src_from = open(from_path, encoding="utf-8").read()
    tree_from = ast.parse(src_from)
    inside = lambda at: any(a <= at <= b for a, b in
                            (spans[n] for n in names))
    E = []
    for n in names:
        left = [x.lineno for x in ast.walk(tree_from)
                if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load)
                and x.id == n and not inside(x.lineno)]
        if left:
            E.append((n, left))

    # F: head lines of the piece it leaves whose last reader was the group.
    from_head = head_of(from_path)
    uses = {}
    for x in ast.walk(tree_from):
        if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load):
            uses.setdefault(x.id, []).append(x.lineno)
    F = []
    for n, line in from_head.items():
        rest = [x for x in uses.get(n, []) if x != line and not inside(x)]
        got = [x for x in uses.get(n, []) if x != line and inside(x)]
        if got and not rest:
            F.append(n)

    # D: the receiving piece already reaches a moved name through
    # PROGRAM. -- that read retires the moment the name lands there.
    # Found 7.9.2026 by a strand holding this tool against a ledger it
    # had counted by hand: `wide_too_short` came out free here and the
    # ledger fell by one, because `cut/` was already reaching for it.
    src_to = open(to_path, encoding="utf-8").read()
    tree_to = ast.parse(src_to)
    to_head = head_of(to_path)
    D = sorted({a.attr for a in ast.walk(tree_to)
                if isinstance(a, ast.Attribute)
                and getattr(a.value, "id", "") == "PROGRAM"
                and a.attr in names and a.attr not in to_head})

    lines = sum(b - a + 1 for a, b in (spans[n] for n in names))
    paid = len(B) + len(C) + len(E)
    net = paid - len(F) - len(D)
    sieve = len([1 for n, lives in C if frm in lives])

    print("moving %s from %s/ to %s/ -- %d lines"
          % (", ".join(names), frm, to, lines))
    print("  A  already in %s/            %2d  %s" % (to, len(A), A))
    print("  B  new head line in %s/      %2d  %s"
          % (to, len(B), [n for n, _w in B]))
    print("  C  forced PROGRAM. read       %2d  %s"
          % (len(C), ["%s (%s)" % (n, ",".join(w) or "the way in")
                      for n, w in C]))
    print("  E  fetched back into %s/     %2d  %s"
          % (frm, len(E), [n for n, _l in E]))
    print("  F  dead head line in %s/     %2d  %s" % (frm, len(F), sorted(F)))
    print("  D  read %s/ already had    %2d  %s" % (to, len(D), D))
    print("  ----")
    print("  paid = B+C+E = %d      net = paid - F - D = %+d" % (paid, net))
    print("  a screen counting late names alone sees %d, and is out by %+d"
          % (sieve, paid - sieve))
    if net > 0:
        print("  %.0f lines a crossing (net)" % (lines / net))
    elif net == 0:
        print("  net zero: the move is free on crossings")
    else:
        print("  net below zero: the move pays for itself")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
