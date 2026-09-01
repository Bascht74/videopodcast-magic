# -*- coding: utf-8 -*-
"""A project name a test gives Resolve is swept, or excepted by name.

resolve/sweep.py deletes what resolve_ground.TEST_PROJECT matches and
nothing else, so a test that names its project any other way leaves it
standing in somebody's project manager. Three sections: the shape the
sweep knows and the way a test builds a name, that every file of the
suite was read -- the repository, not the folder -- and the names, out
of every call that can carry one into a project manager.

A name may lie outside that shape where a test needs it to. Then it
stands in ALLOWED with its reason beside it, the run prints it by name,
and how many there may be is a ratchet: the number may fall, never rise.

Judged in a file that opens the way to a Resolve that is really running,
and there alone: a name given to a stand-in reaches nothing. Only what
stands in the source, so a name a test works out while it runs is
counted and not judged, and a placeholder is read as a lower-case word.
"""
import ast
import io
import os
import re
import subprocess
import sys
import textwrap
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GROUND = "resolve/resolve_ground.py"

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# The words run.sh judges a whole run by. Strings out of other files are
# printed here, and one carrying any of these would turn this test red
# however green it was, or make it look as though it had left a piece
# out. So they go through this first.
LOUD = ("FAIL", "Traceback", "SKIPPED", "LEFT OUT", "Left out",
        "Error", "error", "Exception", "Interrupt")


def quiet(text):
    """Text out of another file, safe to print in a line of ours."""
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


def suite():
    """Every file of the suite that can run, by the path a red line names.

    The repository is asked, not the folder. The builder moves the tests
    a machine cannot run out of `tests/` before the suite starts, and
    `tests/resolve/` is never run there at all -- but its files lie
    there, and they are the ones that talk to Resolve. A file that is
    there is read from there, so work not committed yet counts; only one
    that was moved aside is read out of the last commit. In a clone with
    no `.git` the folder is all there is and has to do.

    Returns (what was read, what could not be), the second one named so
    that a file quietly missing cannot pass for a file with no names in
    it.
    """
    paths = {}
    for root, folders, names in os.walk(HERE):
        folders[:] = [f for f in folders
                      if f not in ("state", "__pycache__", "shots")]
        for name in names:
            if not (name.endswith(".py") or name.endswith(".sh")):
                continue
            # Written the way git writes it. On Windows the walk says
            # resolve\sweep.py and git says resolve/sweep.py, and the
            # same file would come in twice.
            paths[os.path.relpath(os.path.join(root, name),
                                  HERE).replace(os.sep, "/")] = None
    for line in (git("ls-files", "--", "*.py", "*.sh") or "").splitlines():
        line = line.strip()
        if line.endswith(".py") or line.endswith(".sh"):
            paths.setdefault(line, None)
    out, lost = {}, []
    for path in sorted(paths):
        here = os.path.join(HERE, path)
        if os.path.exists(here):
            try:
                out[path] = io.open(here, encoding="utf-8").read()
            except (OSError, UnicodeDecodeError) as e:
                # A file that will not open is not a file with no names
                # in it, and it must not pass for one.
                lost.append("%s (%s)" % (path, type(e).__name__))
            continue
        text = git("show", "HEAD:./" + path)
        if text is None:
            lost.append(path)
        else:
            out[path] = text
    return out, lost


# ---------------------------------------------------------- placeholders
# A name is often written with a placeholder in it -- "vpm-test-%s-%d".
# Two fillings, because the two questions are different: as_name asks
# what the finished name looks like, as_code only has to make a piece of
# source parse.
FILLER = re.compile(r"%[-+ #0]*([0-9]+)?(\.[0-9]+)?([sdiruxXofge%])")


def as_name(text):
    """A name template with its placeholders filled in."""
    def one(m):
        if m.group(3) == "%":
            return "%"
        if m.group(3) in "sr":
            return "x"
        return "0" * max(1, int(m.group(1) or 1))
    return FILLER.sub(one, text)


def as_code(text):
    """The same text with its placeholders filled so that it can parse."""
    def one(m):
        if m.group(3) == "%":
            return "%"
        return "0" if m.group(3) in "diuxXofge" else "'x'"
    return FILLER.sub(one, text)


def parsed(text):
    """The syntax tree of a piece of source, or None.

    Tried as it stands first: filling the placeholders in of a text that
    already parses can only break it.
    """
    for attempt in (text, as_code(text)):
        try:
            return ast.parse(attempt)
        except (SyntaxError, ValueError):
            continue
    return None


# ------------------------------------------------------------- the calls
# Every way a name written in a test can reach a project manager, and
# where in the call it sits. OwnProject and a_test_name do not take the
# name but the word it is built from, so they are held apart below.
NAME_AT = {"CreateProject": 0, "LoadProject": 0, "DeleteProject": 0,
           "open_or_create_project": 1}
BUILT_AT = {"OwnProject": 2, "a_test_name": 0}
# build_resolve_project is the one that carries no name at all in most
# calls: it takes the whole handover, and the project is named after its
# "production" where no name was passed. That is how a name reaches
# Resolve without any of the calls above standing in the test.
HANDOVER = "build_resolve_project"
SWITCH = "--resolve-project"
# What opens the way to a Resolve that is really running. A file that
# calls none of these cannot give a name to anything but its own
# stand-in, whatever it writes.
DOORS = ("connect_to_resolve", "a_resolve", "scriptapp",
         "GetProjectManager", "OwnProject", "a_test_name", HANDOVER)
SHUT = "connect_to_resolve"

# -------------------------------------------------------- the exceptions
# Names that lie outside the sweep's shape on purpose, each with the
# reason it does. A key is one file and the name as it stands written in
# it -- this one name in this one file, not everything that carries the
# word "decoy" or the word "KEEP"; the line number is left out because
# lines move and the reason must not go stale with them.
#
# The count below is a ratchet, like SKIPS_ALLOWED in run.sh: one
# exception more turns the run red although every check in it was green,
# because the run then swept less than the run that set the number. The
# number may fall, and never rise. Whoever needs another one writes the
# reason here first, and raising the number is a line in the diff.
ALLOWED = {
    ("resolve/project_run_puts_back_test.py", "vpm-test-decoy-KEEP-%d"):
        "a decoy has to lie outside the shape the sweep clears, or it no "
        "longer shows what that test is for: that the sweep takes its own "
        "whole shape and not everything beginning with vpm-test. Give it "
        "a name the sweep can clear and it proves nothing. The test "
        "deletes it itself in its finally; a run that is killed leaves it "
        "standing, and that is known.",
}
EXCEPTIONS_ALLOWED = 1


def last(node):
    """The last part of a called name: vpm.a.b() -> 'b'."""
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return None


def where(call, which, key):
    """One argument of a call, by position or by keyword."""
    for word in call.keywords:
        if word.arg == key:
            return word.value
    return call.args[which] if len(call.args) > which else None


def literal(node, seen, depth=0):
    """The text a piece of source stands for, or None if it is worked out.

    A name is followed one step, and only where the file assigns it once:
    `decoy = "vpm-test-..."` two lines above the call is the same thing
    written down, while a name the file sets three times is a value that
    depends on the run.
    """
    if node is None or depth > 3:
        return None
    if isinstance(node, ast.Constant):
        return node.value if isinstance(node.value, str) else None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        return literal(node.left, seen, depth + 1)
    if isinstance(node, ast.JoinedStr):
        out = []
        for piece in node.values:
            if isinstance(piece, ast.Constant) and isinstance(piece.value,
                                                              str):
                out.append(piece.value)
            else:
                out.append("%s")
        return "".join(out)
    if isinstance(node, ast.Name) and len(seen.get(node.id, [])) == 1:
        return literal(seen[node.id][0], seen, depth + 1)
    return None


def handed_over(node, seen, depth=0):
    """The handover dictionary a call was given, or None.

    Only what is written down: `{"production": "X"}` at the call, or a
    name the file sets once, or `dict(D)` around one.
    """
    if node is None or depth > 3:
        return None
    if isinstance(node, ast.Dict):
        out = {}
        for key, value in zip(node.keys, node.values):
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                out[key.value] = literal(value, seen, depth + 1)
        return out
    if isinstance(node, ast.Call) and last(node.func) == "dict":
        out = {}
        if node.args:
            out.update(handed_over(node.args[0], seen, depth + 1) or {})
        for word in node.keywords:
            if word.arg:
                out[word.arg] = literal(word.value, seen, depth + 1)
        return out
    if isinstance(node, ast.Name) and len(seen.get(node.id, [])) == 1:
        return handed_over(seen[node.id][0], seen, depth + 1)
    return None


def read(text, path, offset, found, depth=0):
    """Gather every name and every open door out of one piece of source.

    Returns whether it could be read at all. A test that builds a child
    script as a string and starts it gives names to Resolve through
    source no scan of the outer file sees, so a string that looks like
    code is read as code.
    """
    tree = parsed(text)
    if tree is None:
        return False
    seen = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if last(target) == SHUT:
                    found["shut"].add(path)
                if isinstance(target, ast.Name):
                    seen.setdefault(target.id, []).append(node.value)
    for node in ast.walk(tree):
        line = getattr(node, "lineno", 0) + offset
        if isinstance(node, ast.Call):
            name = last(node.func)
            if name in DOORS:
                found["open"].setdefault(path, "%s at line %d" % (name, line))
            if name in NAME_AT:
                found["name"].append(
                    (path, line, name,
                     literal(where(node, NAME_AT[name], "name"), seen)))
            elif name in BUILT_AT:
                word = literal(where(node, BUILT_AT[name], "what"), seen)
                found["built"].append((path, line, name, word))
            elif name == HANDOVER:
                given = literal(where(node, 2, "project_name"), seen)
                if given is None:
                    carried = handed_over(where(node, 0, "source"), seen)
                    given = (carried.get("production") or "Production"
                             ) if carried is not None else None
                found["name"].append(
                    (path, line, "%s, the handover's production" % name,
                     given))
        # A switch on a command line the test builds: the program takes
        # the name from there and hands it to the project manager itself.
        if isinstance(node, (ast.List, ast.Tuple)):
            parts = node.elts
            for i, piece in enumerate(parts[:-1]):
                if (isinstance(piece, ast.Constant) and piece.value == SWITCH):
                    found["open"].setdefault(
                        path, "%s at line %d" % (SWITCH, line))
                    found["name"].append((path, line, SWITCH,
                                          literal(parts[i + 1], seen)))
        if (depth < 2 and isinstance(node, ast.Constant)
                and isinstance(node.value, str) and len(node.value) > 20
                and any(k + "(" in node.value
                        for k in tuple(NAME_AT) + tuple(BUILT_AT) + DOORS)):
            read(node.value, path, line - 1, found, depth + 1)
    return True


def blocks(text):
    """The pieces a shell file feeds to something on standard input.

    resolve.sh talks to Resolve through a Python block written straight
    into it, so a shell file is not simply skipped.
    """
    out = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        opens = re.search(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1\s*$",
                          lines[i])
        if opens:
            tag, body, i = opens.group(2), [], i + 1
            at = i + 1
            while i < len(lines) and lines[i].strip() != tag:
                body.append(lines[i])
                i += 1
            out.append((at, "\n".join(body)))
        i += 1
    return out


# ------------------------------------------------------------------ 1.
print("1. The shape the sweep knows, and the way a test builds a name")
files, lost = suite()
ground = files.get(GROUND, "")
pattern = None
template = None
tree = parsed(ground) if ground else None
for node in ast.walk(tree) if tree is not None else ():
    if (isinstance(node, ast.Assign) and len(node.targets) == 1
            and last(node.targets[0]) == "TEST_PROJECT"
            and isinstance(node.value, ast.Call)
            and last(node.value.func) == "compile"
            and node.value.args
            and isinstance(node.value.args[0], ast.Constant)):
        pattern = node.value.args[0].value
    if isinstance(node, ast.FunctionDef) and node.name == "a_test_name":
        for step in ast.walk(node):
            if (isinstance(step, ast.Return)
                    and isinstance(step.value, ast.BinOp)
                    and isinstance(step.value.left, ast.Constant)):
                template = step.value.left.value

check("the shape the sweep deletes stands in the tests' own ground",
      bool(pattern), "TEST_PROJECT in %s: %s"
      % (GROUND, quiet(pattern) if pattern else "not found in %d characters"
         % len(ground)))
check("and the way a test builds a name stands there too",
      bool(template), "a_test_name in %s returns %s"
      % (GROUND, quiet(template) if template else "no template this can read"))
made = as_name(template) if template else ""
try:
    shape = re.compile(pattern) if pattern else None
except re.error as e:
    shape, pattern = None, "%s -- %s" % (pattern, e)
check("a name built that way is one the sweep deletes",
      bool(shape) and bool(made) and bool(shape.match(made)),
      "%r against %s" % (quiet(made), quiet(pattern or "no shape to hold it "
                                            "against")))

# ------------------------------------------------------------------ 2.
print("\n2. Every file of the suite was read, the set-aside ones too")
found = {"name": [], "built": [], "open": {}, "shut": set()}
unread = list(lost)
for path in sorted(files):
    text = files[path]
    if path.endswith(".sh"):
        for at, body in blocks(text):
            if not any(k + "(" in body
                       for k in tuple(NAME_AT) + tuple(BUILT_AT) + DOORS):
                continue
            if not read(body, path, at - 1, found):
                unread.append("%s, the block at line %d" % (path, at))
        continue
    if not read(text, path, 0, found):
        unread.append(path)
check("every file the repository names under tests/ was read",
      not unread, "%d of %d not read: %s"
      % (len(unread), len(files), quiet(", ".join(sorted(unread)[:4]))
         or "none"))

# ------------------------------------------------------------------ 3.
print("\n3. The names the tests can give Resolve")
reaches = dict((p, why) for p, why in found["open"].items()
               if p not in found["shut"])
for path in sorted(reaches):
    print("      %s can reach a Resolve that is running -- %s"
          % (path, reaches[path]))

# Two texts per name: the one that stands in the file, so that a red
# line can be grepped for, and the one with the placeholders filled in,
# which is what the sweep would have to match.
judged = []
runtime = 0
for path, line, route, word in found["built"]:
    if path not in reaches:
        continue
    if word is None or template is None:
        runtime += 1
        continue
    judged.append((path, line, "%s(%r)" % (route, word), word,
                   as_name(template.replace("%s", word, 1))))
for path, line, route, name in found["name"]:
    if path not in reaches:
        continue
    if name is None:
        runtime += 1
    else:
        judged.append((path, line, route, name, as_name(name)))

check("there are names to judge at all", bool(judged),
      "%d names read out of the source, %d worked out while a test runs, "
      "in %d files that can reach Resolve"
      % (len(judged), runtime, len(reaches)))
outside = []
excused = {}
for path, line, route, written, name in sorted(judged):
    if shape and shape.match(name):
        continue
    if (path, written) in ALLOWED:
        excused.setdefault((path, written), []).append("%d (%s)"
                                                       % (line, route))
        continue
    outside.append("%s:%d %r%s (%s)"
                   % (path, line, quiet(written),
                      "" if name == written else " -> %r" % quiet(name),
                      route))
# By name, so that whoever reads a green run sees that something was
# taken out of the judgement rather than taking the run for clean.
for spot in sorted(excused):
    print("      excepted by name: %s %r at line%s %s"
          % (spot[0], quiet(spot[1]), "" if len(excused[spot]) == 1 else "s",
             ", ".join(excused[spot])))
    for piece in textwrap.wrap(quiet(ALLOWED[spot]), 66):
        print("          %s" % piece)
check("a project name a test can give Resolve is swept, or excepted by name",
      bool(shape) and not outside, "%d of %d are not, against %s: %s"
      % (len(outside), len(judged), quiet(pattern or "no shape at all"),
         quiet("; ".join(outside)) or "none"))
check("no more names are excepted than the ratchet allows",
      len(excused) <= EXCEPTIONS_ALLOWED, "%d excepted of at most %d%s: %s"
      % (len(excused), EXCEPTIONS_ALLOWED,
         " -- fewer here; the number comes down with them"
         if len(excused) < EXCEPTIONS_ALLOWED else "",
         "; ".join("%s %r" % (p, quiet(w)) for p, w in sorted(excused))
         or "none"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
