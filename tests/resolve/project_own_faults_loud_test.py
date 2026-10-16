# -*- coding: utf-8 -*-
"""A Resolve trap holds Resolve's calls, not a fault of our own.

Reads the Resolve piece, not runs it. A broad trap -- `except
Exception` that neither raises again nor writes the fault into the log
-- is there for a moody Resolve; a call of ours inside it turns our own
fault into a sentence that sounds like Resolve. In turn: that the piece
holds traps to judge at all; the reader held against two pieces of
source of its own, one with a call of ours in the trap and one whose
only call is a function of ours that does nothing but ask Resolve; and
the places, a ratchet that may fall and never rise. Its limit: a call
counts as Resolve's by its capital first letter, as the scripting
interface spells every one.
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
import ast
import io
import time
import ratchet

began = time.time()

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


PIECE = os.path.join(the_program.FOLDER, "resolve", "__init__.py")
STATE = os.path.join(HERE, "state", "resolve_traps_state.json")
# Builtins that only shape an answer already in hand; they cannot fault
# on their own in a way that would be ours rather than the answer's.
SHAPING = {"str", "bool", "int", "float", "len", "list", "dict", "tuple",
           "range", "enumerate"}


def is_resolve(call, thin):
    """Whether a call asks Resolve: a capitalised method, or a thin one."""
    f = call.func
    if isinstance(f, ast.Attribute):
        return f.attr[:1].isupper()
    return isinstance(f, ast.Name) and f.id in thin


def calls_in(nodes):
    """Every call under `nodes`, not counting a function defined there."""
    out, stack = [], list(nodes)
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.Lambda)):
            continue
        if isinstance(node, ast.Call):
            out.append(node)
        stack.extend(ast.iter_child_nodes(node))
    return out


def ours(call, thin):
    """The name of a call that is our own code, or None."""
    if is_resolve(call, thin):
        return None
    f = call.func
    if isinstance(f, ast.Name) and f.id in SHAPING:
        return None
    return ast.unparse(f)


def thin_ones(tree):
    """Functions of the piece whose every call asks Resolve or shapes."""
    thin = set()
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        made = calls_in(node.body)
        if made and all(ours(c, set()) is None for c in made):
            thin.add(node.name)
    return thin


def broad(handler):
    """A handler that catches anything and says nothing of what it was."""
    kind = handler.type
    if kind is not None and ast.unparse(kind) not in ("Exception",
                                                      "BaseException"):
        return False
    for node in ast.walk(handler):
        if isinstance(node, ast.Raise):
            return False
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "fault_into_log":
            return False
    return True


def judged(text):
    """(broad traps, {place: (how many, line)}) of one piece of source."""
    tree = ast.parse(text)
    thin = thin_ones(tree)
    seen = ratchet.owners(tree)
    traps, finds = 0, []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        if not any(broad(h) for h in node.handlers):
            continue
        traps += 1
        own = sorted(set(filter(None, (ours(c, thin)
                                       for c in calls_in(node.body)))))
        if own:
            finds.append(("%s: %s" % (seen.get(id(node), "<module>"),
                                      ", ".join(own)), node.lineno))
    return traps, ratchet.tally(finds)


print("1. The Resolve piece holds traps to judge")
traps, places = judged(io.open(PIECE, encoding="utf-8").read())
check("the Resolve piece holds broad traps for the reader to judge",
      traps > 0, "%d broad traps in %s" % (traps, PIECE))

print("\n2. The reader, against source of its own")
MIXED = '''
def colour(p, hdr):
    try:
        back = str(p.GetSetting("x"))
        if hdr_says(back) == hdr:
            return back
    except Exception:
        return ""
'''
_n, found = judged(MIXED)
check("a call of ours inside a Resolve trap is counted",
      list(found) == ["colour: hdr_says"], "found %r" % sorted(found))

THIN = '''
def add_track(tl, kind):
    return bool(tl.AddTrack(kind)) or bool(tl.AddTrack(kind))

def grow(tl):
    try:
        if tl.GetTrackCount("video") < 2 and add_track(tl, "video"):
            return True
    except Exception:
        return False
'''
_n, found = judged(THIN)
check("a function of ours that only asks Resolve counts as Resolve's",
      found == {}, "found %r" % sorted(found))

print("\n3. The places, held by the ratchet")
state = ratchet.Ratchet(STATE)
state.announce()
held = state.places("own_code_in_resolve_traps", places)
check("no place keeps more of our code in a Resolve trap than allowed",
      held.ok, "%d places now, the state allows %d: %s"
      % (sum(m for m, _l in places.values()), held.limit,
         ", ".join(sorted(places))[:300]))
held.report()

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
