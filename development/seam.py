#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""How wide the seam between the pieces really is, counted in keys.

    python3 seam.py <program folder> [<piece>]

    python3 seam.py /tmp/.../videopodcast_magic ui

`price.py` counts names crossing a piece boundary. This counts the other
seam, the one no tool here has ever looked at: **the untyped dictionary
`state`, which every piece reaches into by string key.**

A name that crosses shows up in a head line and can be seen. A key does
not: `state["speakers_local"]` written in one piece and read in five
others is an agreement between six files that nothing declares, nothing
checks and no ratchet holds. Parnas 1972 is about exactly this -- what
decides whether two people can work at once is the width of the seam,
not the number of files -- and a shared mutable record is his
modularization 1, the one he says forces a joint effort.

**Splitting a file does not narrow it.** Moving a name from `ui/` into
`speakers/` moves a *reader*: a key both of them touched may afterwards
be touched only by `speakers/`, and then the count falls. So this is
also the one number that says whether a campaign of moves bought
anything, measured the same way before and after.

**What it counts and what it cannot.** Only `state[...]`,
`state.get(...)`, `.setdefault(...)` and `.pop(...)` with a literal
string, on a carrier actually called `state`. A key reached under
another name, or built at run time, is invisible here. Measured
7.9.2026: taking `st` in as a second carrier adds 13 keys and not one
crossing, and taking `d` in adds 64 keys that belong to other
dictionaries entirely -- so the narrow reading is the honest one, and it
is a floor, never a ceiling.
"""
import ast
import collections
import io
import os
import sys

CARRIER = "state"
READERS = ("get", "setdefault", "pop")


def keys_of(path, carrier=CARRIER):
    """Every literal key this file reaches on *carrier*."""
    out = set()
    for n in ast.walk(ast.parse(io.open(path, encoding="utf-8").read())):
        if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name) \
                and n.value.id == carrier and isinstance(n.slice, ast.Constant) \
                and isinstance(n.slice.value, str):
            out.add(n.slice.value)
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and n.func.attr in READERS \
                and isinstance(n.func.value, ast.Name) \
                and n.func.value.id == carrier and n.args \
                and isinstance(n.args[0], ast.Constant) \
                and isinstance(n.args[0].value, str):
            out.add(n.args[0].value)
    return out


def pieces_of(folder):
    """The way in and every piece beside it, by name and path."""
    out = [("<the way in>", os.path.join(folder, "__init__.py"))]
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name, "__init__.py")
        if name != "language" and os.path.exists(path):
            out.append((name, path))
    return out


def main(argv):
    if not argv:
        print(__doc__.strip().split("\n\n")[1].strip())
        return 2
    folder = argv[0]
    asked = argv[1] if len(argv) > 1 else None

    where = collections.defaultdict(set)
    for name, path in pieces_of(folder):
        for key in keys_of(path):
            where[key].add(name)

    shared = sorted(k for k, v in where.items() if len(v) > 1)
    print("%d keys on `state`, over %d pieces"
          % (len(where), len({p for v in where.values() for p in v})))
    print("  touched by more than one piece   %3d" % len(shared))
    if asked:
        crossing = sorted(k for k in shared if asked in where[k])
        print("  crossing the %s/ boundary%s   %3d"
              % (asked, " " * max(0, 8 - len(asked)), len(crossing)))
        print()
        for k in crossing:
            print("  %-26s %s" % (k, " ".join(sorted(where[k]))))
    else:
        print()
        for k in shared:
            print("  %-26s %s" % (k, " ".join(sorted(where[k]))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
