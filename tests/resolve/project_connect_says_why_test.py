# -*- coding: utf-8 -*-
"""Each way the connection to Resolve fails is told apart, and a hit kept.

Against a scripting module of the stand-in's own, laid in a folder of
this test: connect_to_resolve is run whole, from the paths to the
import to scriptapp. In turn: that no real scripting module is within
reach before it is laid -- if one is, nothing below runs; an interface
that is not there, a module that will not load, a Resolve that does not
answer, and one that does, its Modules folder put on the path once. Then
check_resolve, the settings box's question, with the door nailed to the
stand-in: a Resolve that names itself, one that will not, one refused,
and an interface that is not there, which is not even tried.
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
import the_program
import importlib
import importlib.util
import tempfile
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


# The program's own connect, held before the door is nailed: it is what
# this test is about, and it only ever meets the module laid below.
the_connect = vpm.connect_to_resolve
CURRENT = {"answer": None, "calls": 0}


def nailed():
    """The door as check_resolve meets it: the stand-in, or a refusal."""
    CURRENT["calls"] += 1
    if isinstance(CURRENT["answer"], Exception):
        raise CURRENT["answer"]
    return CURRENT["answer"]


vpm.connect_to_resolve = nailed

WORK = tempfile.mkdtemp(prefix="connect_")
MODULE = "DaVinciResolveScript"


def short(text):
    """A path or message with this test's own folder cut to <work>."""
    return str(text).replace(WORK, "<work>")


def point_at(api, lib):
    """The interface and library the program is to look for."""
    os.environ["RESOLVE_SCRIPT_API"] = api
    os.environ["RESOLVE_SCRIPT_LIB"] = lib


def forget_module():
    """Let the next import look again, as a fresh process would."""
    sys.modules.pop(MODULE, None)
    importlib.invalidate_caches()


def ask_box():
    """(works, lines) of check_resolve, or ("raised", why) if it raised."""
    try:
        return vpm.check_resolve()
    except Exception as e:  # a raise is what the box must never do
        return "raised", [str(e)]


def connect():
    """(what came back, the error) of one connect against the stand-in."""
    forget_module()
    try:
        return the_connect(), None
    except Exception as e:  # what kind of error it is, is judged below
        return None, e


print("1. No real scripting module within reach")
forget_module()
reachable = importlib.util.find_spec(MODULE)
check("no real scripting module is reachable before the stand-in is laid",
      reachable is None,
      "found at %s -- nothing below calls it" % (
          getattr(reachable, "origin", None),))

if reachable is None:
    print("\n2. connect_to_resolve, whole")
    nowhere = os.path.join(WORK, "no-interface-here")
    point_at(nowhere, os.path.join(nowhere, "fusionscript.so"))
    got, error = connect()
    said = str(error or "")
    check("a missing interface is a stop naming both paths",
          isinstance(error, RuntimeError) and nowhere in said
          and "fusionscript.so" in said,
          "%s: %r" % (type(error).__name__, short(said)[:160]))

    empty = os.path.join(WORK, "interface-without-module")
    os.makedirs(os.path.join(empty, "Modules"))
    open(os.path.join(empty, "fusionscript.so"), "w").close()
    point_at(empty, os.path.join(empty, "fusionscript.so"))
    got, error = connect()
    said = str(error or "")
    check("a module that will not load is a stop naming the module",
          isinstance(error, RuntimeError) and MODULE in said
          and nowhere not in said,
          "%s: %r" % (type(error).__name__, short(said)[:160]))

    api, lib = stand.script_module(os.path.join(WORK, "interface"))
    point_at(api, lib)
    stand.ANSWER.clear()
    del stand.ASKED[:]
    got, error = connect()
    said = str(error or "")
    check("a Resolve that does not answer is a stop of its own",
          isinstance(error, RuntimeError) and stand.ASKED == ["Resolve"]
          and MODULE not in said and api not in said,
          "%s: %r after scriptapp was asked %r"
          % (type(error).__name__, short(said)[:120], stand.ASKED))

    answering = stand.Resolve()
    stand.ANSWER["Resolve"] = answering
    del stand.ASKED[:]
    got, error = connect()
    check("a Resolve that answers is handed back as it is",
          got is answering and error is None,
          "got %r, error %r" % (got, error))
    loaded = getattr(sys.modules.get(MODULE), "__file__", "") or ""
    check("the module that answered is the stand-in, not a real one",
          loaded.startswith(api), "module loaded from %r" % short(loaded))
    connect()
    modules = os.path.join(api, "Modules")
    check("the interface's Modules folder goes on the path once",
          sys.path.count(modules) == 1,
          "%s on the path %d times"
          % (short(modules), sys.path.count(modules)))

    print("\n3. check_resolve, the settings box's question")
    CURRENT["answer"] = stand.Resolve(product="Resolve Stand-in",
                                      version="21.0.4")
    works, lines = ask_box()
    check("a reached Resolve is named with its version, nothing else",
          works is True and lines == ["Resolve Stand-in 21.0.4"],
          "works %r, lines %r" % (works, lines))

    CURRENT["answer"] = stand.Resolve(product="Resolve Stand-in",
                                      throw=["GetVersionString"])
    works, lines = ask_box()
    check("a Resolve that will not give its version still counts as reached",
          works is True and lines == ["Resolve Stand-in"],
          "works %r, lines %r" % (works, lines))

    CURRENT["answer"] = RuntimeError("stand-in says no")
    works, lines = ask_box()
    check("a refused connection is not reached and carries its reason",
          works is False and "stand-in says no" in lines
          and len(lines) > 3,
          "works %r, %d lines: %r"
          % (works, len(lines), [short(x) for x in lines[2:4]]))

    point_at(nowhere, os.path.join(nowhere, "fusionscript.so"))
    CURRENT["calls"] = 0
    CURRENT["answer"] = stand.Resolve()
    works, lines = ask_box()
    check("without the interface the connection is not even tried",
          works is False and CURRENT["calls"] == 0
          and any(nowhere in line for line in lines),
          "works %r, connect asked %d times, lines %r"
          % (works, CURRENT["calls"], [short(x) for x in lines[:2]]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
