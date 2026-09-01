# -*- coding: utf-8 -*-
"""A check that falls says what came out, not only that it fell.

In order: that the suite can be read, that every test judges through a
`check` it defines once itself, that the function records more than the
wording, and that every call fills the slot which carries it. Which
slot that is comes out of each file's own `check`, not out of a count
of arguments: a function that measures its own numbers asks nothing of
its callers. One limit: a call unpacked with a star is taken as filled,
since what the star holds is not on the page.
"""
import ast
import io
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stop():
    """Nothing further can be read, so say so and go."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad))
    sys.exit(1)


# The words run.sh judges the whole output by. A line carrying "FAIL"
# turns this test red however green it was, one beginning "LEFT OUT"
# says a piece was left out, and the error words decide which lines a
# red report shows. Wordings in the suite carry one of them, so what is
# quoted out of another test comes through here first.
LOUD = ("FAIL", "Traceback", "SKIPPED", "LEFT OUT", "Left out",
        "Error", "error", "Exception", "Interrupt")


def quiet(text):
    """A wording out of another test, safe to print in a line of ours."""
    text = " ".join(str(text).split())
    for word in LOUD:
        text = text.replace(word, word[:2] + "-" + word[2:])
    return text


def git(*args):
    """Ask git, and nothing if there is no git and no repository."""
    try:
        out = subprocess.run(("git", "-C", HERE) + args,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL)
    except OSError:
        return None
    return out.stdout.decode("utf-8") if out.returncode == 0 else None


def sources():
    """Every test of the repository, by the path a red line would name.

    The repository is asked, not the folder. The builder moves the tests
    a machine cannot run out of `tests/` before the suite starts, so
    what lies about here is 143 files there and more than 160 here, and
    a rule counted over the folder would leave the set-aside ones
    unjudged on exactly the machines that set them aside.

    A file that is there is read from there, so work that is not
    committed yet counts; only one that was moved aside is read out of
    the last commit. In a clone without a `.git` the folder is all there
    is and has to do.
    """
    paths = {}
    for root, folders, files in os.walk(HERE):
        folders[:] = [f for f in folders
                      if f not in ("state", "__pycache__")]
        for name in files:
            if not name.endswith("_test.py"):
                continue
            # Written the way git writes it. On Windows the walk says
            # resolve\x_test.py and git says resolve/x_test.py, and the
            # same file would come in twice and be counted twice.
            paths[os.path.relpath(os.path.join(root, name),
                                  HERE).replace(os.sep, "/")] = None
    listed = git("ls-files", "--", "*_test.py")
    for line in (listed or "").splitlines():
        line = line.strip()
        if line.endswith("_test.py"):
            paths.setdefault(line, None)
    out = {}
    for path in sorted(paths):
        here = os.path.join(HERE, path)
        if os.path.exists(here):
            out[path] = io.open(here, encoding="utf-8").read()
        else:
            text = git("show", "HEAD:./" + path)
            if text is not None:
                out[path] = text
    return out


# What a check function leaves behind when it falls: what it prints, and
# what it hands to the list the closing line reads back.
SINKS = ("append", "extend", "add", "insert")


def is_sink(node):
    return isinstance(node, ast.Call) and (
        (isinstance(node.func, ast.Name) and node.func.id == "print")
        or (isinstance(node.func, ast.Attribute)
            and node.func.attr in SINKS))


def read(node):
    """Every name this piece of code reads."""
    return set(k.id for k in ast.walk(node)
               if isinstance(k, ast.Name) and isinstance(k.ctx, ast.Load))


def bound(node):
    """Every name this statement gives a value to."""
    targets = []
    if isinstance(node, ast.Assign):
        targets = node.targets
    elif isinstance(node, (ast.AugAssign, ast.AnnAssign, ast.For,
                           ast.AsyncFor)):
        targets = [node.target]
    elif isinstance(node, ast.withitem) and node.optional_vars is not None:
        targets = [node.optional_vars]
    out = set()
    for target in targets:
        out |= set(k.id for k in ast.walk(target) if isinstance(k, ast.Name))
    return out


def shape(fn):
    """How one `check` function comes by the line it leaves behind.

    Three things are read out of it and nothing else. The record: every
    name that reaches a print or a collector, because those two are all
    a builder ever sees. The verdict: the name the failing branch turns
    on, and the one that picks the word "FA-IL" -- that name says
    whether the check fell, never what came out, so it is no evidence.
    And what the function works out for itself: a name it gives a value
    to and then puts into the record.

    Out of those: `own` is the evidence the function builds on its own,
    and `owed` the parameters that carry evidence and must therefore
    come from the caller. It is deliberately not "the third argument":
    a function that measures its own numbers asks nothing of its
    callers, however few arguments they pass.
    """
    params = [a.arg for a in fn.args.args] \
        + [a.arg for a in fn.args.kwonlyargs]
    record = set()
    verdict = set()
    mine = set()
    for node in ast.walk(fn):
        if is_sink(node):
            for piece in list(node.args) + [k.value for k in node.keywords]:
                record |= read(piece)
        if isinstance(node, ast.If) and any(
                is_sink(k) for s in node.body for k in ast.walk(s)):
            verdict |= read(node.test)
        if isinstance(node, ast.IfExp):
            for branch in (node.body, node.orelse):
                if isinstance(branch, ast.Constant) \
                        and isinstance(branch.value, str) \
                        and "FAIL" in branch.value:
                    verdict |= read(node.test)
        mine |= bound(node)
    own = (record & mine) - set(params)
    owed = (record & set(params[1:])) - verdict
    return tuple(params), frozenset(own), frozenset(owed)


def fills(call, params, owed):
    """Whether this call hands over a slot that carries evidence."""
    for name in owed:
        spot = params.index(name)
        if len(call.args) > spot:
            return call.args[spot]
        for word in call.keywords:
            if word.arg == name:
                return word.value
    return None


def empty(node):
    """A value that prints as nothing: the slot is filled with air."""
    return isinstance(node, ast.Constant) \
        and not str("" if node.value is None else node.value).strip()


print("1. The suite can be read")
found = sources()
check("the tests of this repository can be read at all", bool(found),
      "%d files found under %s" % (len(found), HERE))
if bad:
    stop()

trees = {}
broken = []
for path in sorted(found):
    try:
        trees[path] = ast.parse(found[path])
    except SyntaxError as why:
        broken.append("%s line %s" % (path, why.lineno))
check("every one of them parses", not broken,
      "%d of %d do not: %s" % (len(broken), len(found), broken[:3]))
if bad:
    stop()

print("\n2. Every test judges through a check it defines itself")
# Without a definition to read there is no telling which slot carries
# the evidence, and counting such a file as clean would be the silent
# pass this test exists to stop.
defined = {}
calls = {}
for path in sorted(trees):
    defined[path] = [n for n in ast.walk(trees[path])
                     if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                     and n.name == "check"]
    calls[path] = [n for n in ast.walk(trees[path])
                   if isinstance(n, ast.Call)
                   and isinstance(n.func, ast.Name) and n.func.id == "check"]
foreign = ["%s (%d calls)" % (p, len(calls[p])) for p in sorted(trees)
           if calls[p] and not defined[p]]
check("no test judges through a check it does not define", not foreign,
      "%d of %d tests: %s"
      % (len(foreign), len(trees), foreign[:3]))

# Where a file defines the same check twice the two are one shape and a
# call can be read against it. Where they differ, which one a call
# reaches is a question of scope this does not answer, and guessing it
# would count the file clean for the wrong reason.
shapes = dict((p, set(shape(d) for d in defined[p])) for p in sorted(trees))
split = ["%s (%d shapes)" % (p, len(shapes[p])) for p in sorted(trees)
         if len(shapes[p]) > 1]
check("a test that defines check twice defines it alike", not split,
      "%d of %d tests: %s" % (len(split), len(trees), split[:3]))
if bad:
    stop()

print("\n3. The check function records more than the wording")
# The first parameter is the wording, and the wording is in the source
# already. So the line is worth reading only if something else reaches
# it: a value the function measures itself, or one a caller hands over.
mute = []
silent = set()
for path in sorted(trees):
    if not defined[path]:
        continue
    for params, own, owed in shapes[path]:
        if not own and not owed:
            silent.add(path)
            mute.append("%s: check(%s) records only %s"
                        % (path, ", ".join(params),
                           params[0] if params else "nothing"))
check("every check function records a value beside the wording", not mute,
      "%d of %d tests: %s"
      % (len(mute), len(trees), quiet("; ".join(mute[:2]))))
for line in mute:
    print("      %s" % quiet(line))

print("\n4. Every call fills the slot that carries the value")
nude = []
counted = 0
starred = 0
for path in sorted(trees):
    # Where the function itself leaves nothing but the wording, no call
    # can mend that by handing something over. Section 3 has named the
    # fault where it sits; blaming the calls as well would report the
    # consequence and bury the cause under it.
    if not defined[path] or path in silent:
        continue
    lines = found[path].split("\n")
    for call in calls[path]:
        counted += 1
        # A star can hand over exactly what is missing here, and which
        # values it holds is not on the page. Taken as filled, and said
        # so in the head rather than counted as a find.
        if any(isinstance(a, ast.Starred) for a in call.args) \
                or any(k.arg is None for k in call.keywords):
            starred += 1
            continue
        given = None
        for params, own, owed in shapes[path]:
            if own:
                given = call            # the function measures its own
                break
            given = fills(call, params, owed)
        said = call.args[0] if call.args else None
        wording = said.value if isinstance(said, ast.Constant) \
            and isinstance(said.value, str) else "..."
        where = "%s:%d %r" % (path, call.lineno, wording[:44])
        # A slot holding "" prints what an unfilled one prints -- the
        # canonical check writes "no numbers" for both -- so the two
        # are the same find and are judged together.
        if given is None or empty(given):
            nude.append((where, lines[call.lineno - 1].strip()[:60]))

check("no call falls with nothing but its wording", not nude,
      "%d of %d calls in %d tests: %s"
      % (len(nude), counted, len(set(w.split(":")[0] for w, _l in nude)),
         quiet("; ".join(w for w, _l in nude[:3]))))
for where, line in nude:
    print("      %s -- %s" % (quiet(where), quiet(line)))

print("\n%d tests, %d calls, %d of them unpacked with a star"
      % (len(trees), counted, starred))
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
