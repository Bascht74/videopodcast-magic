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
     For the six pieces the window reads out of itself there is no
     take_from(), so EVERY moved name needs a line there.
  F  head lines in the piece it left whose last reader was the moved
     code. They have to go: source_no_loose_ends is red on a head line
     nobody reads.                                                -1 each
  D  a PROGRAM. read the RECEIVING piece already had for the moved name
     -- it retires when the name lands there.                  -1 each

    paid = B + C + E      net = B + C + E - F - D

Under those, one line that is not a cost: **how many of the names are
read by no piece but the one they are leaving.** Every term above says
what a move costs, and none of them says whether it is right -- there is
no measure that does. This one says the single thing about the names
themselves that can be counted without a judgement: a name nobody else
reads is private to its piece, so moving it carries the whole of it
across and leaves nothing scattered behind.

**A constant at the top level counts too**, since 7.9.2026: what it
reads is read off its value rather than out of a symtable block, which
it does not have. What its span does *not* cover is the comment above
it, and that travels with it -- so the "lines a crossing" figure is a
little low for a group of constants.

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
    out = [n for _l, n in order]
    # The six pieces the window reads out of itself stand nowhere in
    # the way in's list, and without a position they were priced as
    # unreachable from everywhere -- found 7.9.2026, when a head line
    # for `run_stages` in `fittings/` was called impossible and then
    # run green. They are read while `ui/` is read, so they sit at
    # `ui/`'s place: everything the way in took before `ui/` is theirs
    # to bind, and nothing after it is.
    if "ui" in out:
        ui_src = open(os.path.join(folder, "ui", "__init__.py"),
                      encoding="utf-8").read()
        under, seen2 = [], set()
        for node in ast.walk(ast.parse(ui_src)):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                    and node.func.id == "beside" and node.args \
                    and isinstance(node.args[0], ast.Constant):
                nm = node.args[0].value
                if nm not in seen2 and nm not in out:
                    seen2.add(nm)
                    under.append((node.lineno, nm))
        under.sort()
        at = out.index("ui")
        out = out[:at + 1] + [n for _l, n in under] + out[at + 1:]
    return out


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
    # A constant at the top level travels the same way a function does,
    # and until 7.9.2026 naming one made this refuse the whole run. Six
    # of them had to be left out of a move of thirty-five names, and
    # four then showed up under C as forced reads although they were
    # moving too: the net came out four too high. A constant has no
    # symtable block, so what it reads is read off its value here.
    values = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 \
                and isinstance(n.targets[0], ast.Name) \
                and n.targets[0].id in names and n.targets[0].id not in spans:
            spans[n.targets[0].id] = (n.lineno, n.end_lineno)
            values[n.targets[0].id] = n.value
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
        if name in values:
            out[name] = {x.id for x in ast.walk(values[name])
                         if isinstance(x, ast.Name)} - set(dir(builtins))
            continue
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


def other_readers(folder, names, frm):
    """Which pieces besides *frm* read each of these names.

    The one number this tool has that is not a cost. A name no other
    piece reads is private to the one it sits in, so moving it carries
    the whole of it across and leaves nothing scattered behind; a name
    half the program reads sits on the programme either way, and where
    it lives says much less.

    The way in is not counted as a reader. Its `X = <piece>.X` lines
    bind nothing -- they stand there for a reader and for
    source_no_loose_ends -- and counting them would make every name look
    as though the way in used it.
    """
    out = dict((n, []) for n in names)
    for piece in sorted(os.listdir(folder)):
        if piece in (frm, "__pycache__", "language"):
            continue
        path = os.path.join(folder, piece, "__init__.py")
        if not os.path.exists(path):
            continue
        tree = ast.parse(open(path, encoding="utf-8").read())
        seen = set()
        for x in ast.walk(tree):
            if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load):
                seen.add(x.id)
            elif isinstance(x, ast.Attribute):
                seen.add(x.attr)
        head = head_of(path)
        for n in names:
            # A head line alone is not a reading: it is the binding, and
            # it goes out with the name.
            if n in seen and n not in head:
                out[n].append(piece)
    return out


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

    # E again, for the six pieces the window reads out of itself: there
    # is no take_from() for them, so a name of theirs reaches the
    # programme only through an explicit `X = <piece>.X` line in the
    # window. Every moved name needs one, whether a reader is left
    # behind or not. Measured 7.9.2026: with one bind line instead of
    # five, dir(vpm) after the window fell 1292 -> 1288 and lost
    # exactly the four names that had none.
    ui_src = open(os.path.join(folder, "ui", "__init__.py"),
                  encoding="utf-8").read()
    under = {n.args[0].value
             for n in ast.walk(ast.parse(ui_src))
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
             and n.func.id == "beside" and n.args
             and isinstance(n.args[0], ast.Constant)}
    bind_only = to in under
    if bind_only:
        had = {n for n, _l in E}
        E = E + [(n, ["a bind line in ui/"]) for n in names if n not in had]

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
    # A fetch-back into a piece the way in reads is `X = PROGRAM.X`, and
    # the ledger counts that. Into one of the six the window reads
    # itself it is `X = <piece>.X`, which the ledger does not count --
    # it is work and a place that can go wrong, but not a crossing.
    # Held against all three measured moves: the channel rows +0, the
    # short-shot line -1, the footer +1. No other reading gives all
    # three.
    paid = len(B) + len(C) + len(E)
    crossing_E = 0 if bind_only else len(E)
    net = len(B) + len(C) + crossing_E - len(F) - len(D)
    sieve = len([1 for n, lives in C if frm in lives])

    print("moving %s from %s/ to %s/ -- %d lines"
          % (", ".join(names), frm, to, lines))
    print("  A  already in %s/            %2d  %s" % (to, len(A), A))
    print("  B  new head line in %s/      %2d  %s"
          % (to, len(B), [n for n, _w in B]))
    print("  C  forced PROGRAM. read       %2d  %s"
          % (len(C), ["%s (%s)" % (n, ",".join(w) or "the way in")
                      for n, w in C]))
    # The sixth fault this tool has been caught in, and the only one it
    # can warn about itself: a move priced in parts is priced wrong.
    # Measured 7.9.2026 on the same move -- the first block of twelve
    # names alone came out at +2, and all forty-one together at -13,
    # because a name that is moving too looks from here like a name
    # staying behind. Every such name shows up under C with the piece
    # being left in its brackets, so the count is free.
    left_behind = [n for n, lives in C if frm in lives]
    if left_behind:
        print("     of those, %d live in %s/, which you are leaving: if any "
              "of them is\n     moving as well, price them in one run or "
              "this comes out too high" % (len(left_behind), frm))
        print("     %s" % sorted(left_behind))
    print("  E  fetched back into %s/     %2d  %s"
          % (frm, len(E), [n for n, _l in E]))
    print("  F  dead head line in %s/     %2d  %s" % (frm, len(F), sorted(F)))
    print("  D  read %s/ already had    %2d  %s" % (to, len(D), D))
    print("  ----")
    print("  paid = B+C+E = %d      net = %+d%s"
          % (paid, net, "   (the %d line(s) back are not crossings: no "
                        "take_from for %s/)" % (len(E), to) if bind_only else ""))
    print("  a screen counting late names alone sees %d, and is out by %+d"
          % (sieve, paid - sieve))
    # The one line here that is not a cost. Every other number says what
    # the move costs; none of them says whether it is right, and the
    # literature has no measure that does -- so this says the one thing
    # about the name itself that can be counted without a judgement.
    others = other_readers(folder, names, frm)
    alone = sorted(n for n in names if not others[n])
    print("  ----")
    print("  read by no piece but %s/    %2d of %d  %s"
          % (frm, len(alone), len(names), alone))
    for n in names:
        if others[n]:
            print("      %-28s also read in %s"
                  % (n, ", ".join(p + "/" for p in others[n])))
    if net > 0:
        print("  %.0f lines a crossing (net)" % (lines / net))
    elif net == 0:
        print("  net zero: the move is free on crossings")
    else:
        print("  net below zero: the move pays for itself")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
