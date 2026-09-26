# -*- coding: utf-8 -*-
"""A ratchet writes no floor from a tree that is behind origin/main.

Four small trees are built in a folder of their own: one checked out
behind its origin/main, one holding origin/main plus a commit of its
own, one with no origin/main at all, and a folder that is no
repository. In order: what git says about each tree, and that it says
nothing where it cannot tell; that every counter kind -- number,
rising, places -- keeps its floor in the tree behind main and is still
red there when the measure is worse; that the run says so once and
claims no tightening; and that the current tree and the tree without
an origin/main write as they always did. What origin/main holds is as
fresh as the last fetch, and nothing here fetches.
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
import contextlib
import io
import json
import shutil
import subprocess
import tempfile
import time

sys.path.insert(0, HERE)
# This measures the ratchet, not the program. A snapshot's name in
# VPM_SCRIPT would make the ratchet decline to write for that reason,
# and the trees below could then not be told apart.
os.environ.pop("VPM_SCRIPT", None)
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


def git(folder, *words):
    """git's return code in `folder`, None where there is no git."""
    try:
        return subprocess.run(("git", "-C", folder, "-c", "user.name=t",
                               "-c", "user.email=t@t") + words,
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL).returncode
    except OSError:
        return None


def commit(folder, name):
    """One file, one commit; the return code of the commit.

    A folder a clone never made answers None rather than a traceback,
    so the precondition below is the line that goes red.
    """
    try:
        io.open(os.path.join(folder, name), "w").write(name + "\n")
    except OSError:
        return None
    git(folder, "add", name)
    return git(folder, "commit", "-q", "-m", name)


def floor_of(path):
    """What the state file says, as a dict."""
    return json.loads(io.open(path, encoding="utf-8").read())


def finish():
    """The one way out: the trees gone, the count, the verdict, the code."""
    shutil.rmtree(ROOM, ignore_errors=True)
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


def counted(path, key, value):
    """A number counter measured once, with its output kept."""
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        limit = ratchet.Ratchet(path).number(key, value)
    return limit, said.getvalue()


ROOM = tempfile.mkdtemp(prefix="floor-")
if git(ROOM, "--version") is None:
    print("SKIPPED: no git here -- the floor is a claim about origin/main, "
          "and only git can say whether a tree holds it")
    shutil.rmtree(ROOM, ignore_errors=True)
    sys.exit(0)

# ---------------------------------------------------------------- 1.
print("1. Four trees, and what git says about each")
UP = os.path.join(ROOM, "up")
BEHIND = os.path.join(ROOM, "behind")
CURRENT = os.path.join(ROOM, "current")
LONE = os.path.join(ROOM, "lone")
NOWHERE = os.path.join(ROOM, "nowhere")
os.makedirs(UP)
os.makedirs(LONE)
os.makedirs(NOWHERE)
built = [git(UP, "init", "-q", "-b", "main"),
         commit(UP, "first"), commit(UP, "second"),
         git(ROOM, "clone", "-q", UP, BEHIND),
         git(BEHIND, "checkout", "-q", "-b", "old", "HEAD~1"),
         git(ROOM, "clone", "-q", UP, CURRENT),
         git(CURRENT, "checkout", "-q", "-b", "fresh"),
         commit(CURRENT, "third"),
         git(LONE, "init", "-q", "-b", "main"), commit(LONE, "alone")]
check("the four trees could be built", all(rc == 0 for rc in built),
      "git return codes %s" % built)
if bad:
    finish()        # nothing below can be asked of trees that are not there
contained = git(BEHIND, "merge-base", "--is-ancestor", "origin/main",
                "HEAD")
check("git calls the tree behind origin/main not current",
      ratchet.tree_is_current(BEHIND) is False,
      "tree_is_current answered %r, git merge-base --is-ancestor rc %s"
      % (ratchet.tree_is_current(BEHIND), contained))
check("a tree holding origin/main plus its own commit is current",
      ratchet.tree_is_current(CURRENT) is True,
      "tree_is_current answered %r" % ratchet.tree_is_current(CURRENT))
check("a tree with no origin/main is taken as current",
      ratchet.tree_is_current(LONE) is True,
      "tree_is_current answered %r, rev-parse origin/main rc %s"
      % (ratchet.tree_is_current(LONE),
         git(LONE, "rev-parse", "--verify", "-q", "origin/main")))
check("a folder that is no repository is taken as current",
      ratchet.tree_is_current(NOWHERE) is True,
      "tree_is_current answered %r" % ratchet.tree_is_current(NOWHERE))
# A second clone behind main, asked with no git on the path: the answer
# is memoised per folder, so the first clone would answer from memory.
UNASKED = os.path.join(ROOM, "unasked")
git(ROOM, "clone", "-q", UP, UNASKED)
git(UNASKED, "checkout", "-q", "-b", "old", "HEAD~1")
path_was = os.environ.get("PATH", "")
try:
    os.environ["PATH"] = NOWHERE
    blind = ratchet.tree_is_current(UNASKED)
finally:
    os.environ["PATH"] = path_was
check("without git the tree behind main is taken as current",
      blind is True, "tree_is_current answered %r with PATH=%s"
      % (blind, NOWHERE))

# ---------------------------------------------------------------- 2.
print("\n2. In the tree behind main the floor stays where it is")
STATE = os.path.join(BEHIND, "style_state.json")
io.open(STATE, "w").write(json.dumps({"n": 10, "r": 10,
                                      "p": {"a": [2, 5]}}))
limit, said = counted(STATE, "n", 7)
check("a number counter in the tree behind main keeps its floor",
      floor_of(STATE)["n"] == 10 and limit == 10,
      "file says %s, limit %d after measuring 7" % (floor_of(STATE)["n"],
                                                    limit))
worse, _s = counted(STATE, "n", 12)
check("a worse count in the tree behind main is held to the old floor",
      worse == 10, "limit %d after measuring 12" % worse)
with contextlib.redirect_stdout(io.StringIO()):
    up = ratchet.Ratchet(STATE).rising("r", 12)
check("a rising counter in the tree behind main keeps its floor",
      floor_of(STATE)["r"] == 10 and up == 10,
      "file says %s, floor %d after measuring 12" % (floor_of(STATE)["r"],
                                                     up))
with contextlib.redirect_stdout(io.StringIO()):
    fewer = ratchet.Ratchet(STATE).places("p", {"a": (1, 5)})
check("a place counter in the tree behind main keeps its places",
      floor_of(STATE)["p"] == {"a": [2, 5]} and fewer.ok
      and not fewer.tightened,
      "file says %s, ok %r, tightened %r after measuring 1 of 2"
      % (floor_of(STATE)["p"], fewer.ok, fewer.tightened))
with contextlib.redirect_stdout(io.StringIO()):
    more = ratchet.Ratchet(STATE).places("p", {"a": (3, 5)})
check("a new place in the tree behind main is still red",
      not more.ok and len(more.worse) == 1,
      "ok %r, %d places over after measuring 3 of 2" % (more.ok,
                                                        len(more.worse)))

# ---------------------------------------------------------------- 3.
print("\n3. The run says so once, and claims no tightening")
told = io.StringIO()
with contextlib.redirect_stdout(told):
    one = ratchet.Ratchet(STATE)
    one.number("n", 7)
    one.rising("r", 12)
    one.places("p", {"a": (1, 5)})
lines = [line for line in told.getvalue().splitlines()
         if "behind origin/main" in line]
check("the run says once that the tree is behind origin/main",
      len(lines) == 1, "%d such lines over 3 counters: %s"
      % (len(lines), told.getvalue().strip()[:120]))
check("the line names the state file that was not written",
      len(lines) == 1 and "style_state.json" in lines[0],
      "the line: %s" % (lines[0].strip() if lines else "none"))
quiet = io.StringIO()
with contextlib.redirect_stdout(quiet):
    one.note(10, 7)
check("no tightened line is said in the tree behind main",
      "tightened" not in quiet.getvalue(),
      "note(10, 7) printed %r" % quiet.getvalue().strip())

# ---------------------------------------------------------------- 4.
print("\n4. Elsewhere the ratchet writes as it always did")
FRESH = os.path.join(CURRENT, "style_state.json")
io.open(FRESH, "w").write(json.dumps({"n": 10}))
limit, said = counted(FRESH, "n", 7)
check("the same number counter on the current tree tightens",
      floor_of(FRESH)["n"] == 7 and limit == 10,
      "file says %s, limit %d after measuring 7" % (floor_of(FRESH)["n"],
                                                    limit))
told = io.StringIO()
with contextlib.redirect_stdout(told):
    ratchet.Ratchet(FRESH).note(10, 7)
check("the current tree says it tightened",
      "ratchet tightened: 10 -> 7" in told.getvalue(),
      "note(10, 7) printed %r" % told.getvalue().strip())
ALONE = os.path.join(LONE, "style_state.json")
io.open(ALONE, "w").write(json.dumps({"n": 10}))
limit, said = counted(ALONE, "n", 7)
check("the same counter in the tree without origin/main tightens",
      floor_of(ALONE)["n"] == 7 and limit == 10,
      "file says %s, limit %d after measuring 7" % (floor_of(ALONE)["n"],
                                                    limit))

finish()
