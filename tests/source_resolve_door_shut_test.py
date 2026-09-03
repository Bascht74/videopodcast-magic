# -*- coding: utf-8 -*-
"""A test that calls at a door to Resolve has nailed it shut first.

Four sections: the doors, read out of the program and out of the test
that listed them already; that every file of the suite was read -- the
repository, not the folder; every call at a door held against the place
where connect_to_resolve was replaced; and the switches that make the
program connect in a process of its own, which no replacement reaches.

tests/resolve/ and the file that starts it are excepted, each by name:
those talk to a Resolve that is really running, on purpose, and are
started by hand. How many may be excepted is a ratchet.

The limit is that only the source is read. A replacement a test makes
while it runs is not seen, and one step is followed and not two: a
function that reaches a door through another -- write_handover through
the --resolve in its handover -- is not counted here.
"""
import ast
import io
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ME = os.path.basename(__file__)
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
# The test that asked the neighbouring question -- which files can reach a
# Resolve at all, and what shuts the way. Its answer is read out of it
# rather than written down a second time here.
SIBLING = "source_test_names_swept_test.py"
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


# The words run.sh judges a whole run by -- and it looks for FAIL
# anywhere in a line, not only at its start. Names and paths out of other
# files are printed here, so they go through this first.
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
    """Every file of the suite, by the path a red line would name.

    The repository is asked and not the folder. The builder moves the
    tests a machine cannot run out of `tests/` before the suite starts,
    and `tests/resolve/` never runs there at all -- but those files lie
    there, and they are the ones that talk to Resolve. A file that is
    there is read from there, so work not committed yet counts; only one
    that was moved aside is read out of the last commit. In a clone with
    no `.git` the folder is all there is and has to do.

    Returns (what was read, what could not be), the second one named so
    that a file quietly missing cannot pass for a file with nothing in it.
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
                # A file that will not open is not a file with nothing in
                # it, and it must not pass for one.
                lost.append("%s (%s)" % (path, type(e).__name__))
            continue
        text = git("show", "HEAD:./" + path)
        if text is None:
            lost.append(path)
        else:
            out[path] = text
    return out, lost


# A test that builds a child script writes it as a string with
# placeholders in it, and such a string has to parse before it can be
# read. Filled only so that it parses -- what the finished text says is
# not the question here.
FILLER = re.compile(r"%[-+ #0]*([0-9]+)?(\.[0-9]+)?([sdiruxXofge%])")


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


def last(node):
    """The last part of a name: vpm.a.b -> 'b'."""
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return None


def outermost(tree):
    """Which nodes of a tree stand at module level, as a set of ids.

    A replacement inside a function is made when that function runs, and
    the source does not say whether it ever does. Only what stands at
    module level has certainly happened by the time the file's own body
    reaches a door.
    """
    out, front = set(), [tree]
    while front:
        node = front.pop()
        for kid in ast.iter_child_nodes(node):
            if isinstance(kid, (ast.FunctionDef, ast.AsyncFunctionDef,
                                ast.ClassDef, ast.Lambda)):
                continue
            out.add(id(kid))
            front.append(kid)
    return out


def calls_in(text, wanted):
    """Which functions of a piece of source call one of `wanted`.

    The name of the innermost function the call stands in, or "<module>".
    Only the call itself -- one step, not two.
    """
    tree = parsed(text)
    if tree is None:
        return None
    up = {}
    for node in ast.walk(tree):
        for kid in ast.iter_child_nodes(node):
            up[id(kid)] = node
    out = {}
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and last(node.func) in wanted):
            continue
        holder, name = up.get(id(node)), "<module>"
        while holder is not None:
            if isinstance(holder, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = holder.name
                break
            holder = up.get(id(holder))
        out.setdefault(last(node.func), set()).add(name)
    return out


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


# ------------------------------------------------------------ the doors
# Two the neighbouring test has no reason to know: both open the
# connection, neither makes a project, so the question over there --
# is the project name one the sweep clears -- never had to ask about
# them. Here they count like any other door.
DOORS_HERE = ("check_resolve", "print_audio_track_mapping")
# The switches that make the program connect in a process of its own.
# --resolve-project only carries a name and reaches nothing by itself.
# Against a second process no replacement helps, so these are not
# allowed at all rather than allowed once something is nailed shut.
CONNECTING = ("--resolve", "--resolve-json", "--resolve-audio-tracks")

# ------------------------------------------------------- the exceptions
# The files that open the way on purpose, each named on its own -- not a
# pattern over the folder, which would let a fifth file in there out
# without anybody saying so. The count below is a ratchet like
# SKIPS_ALLOWED in run.sh: it may fall and never rise.
ALLOWED = {
    "resolve/project_clips_land_right_test.py":
        "talks to a Resolve that is really running, on purpose. Never in "
        "the suite: resolve.sh starts these by hand, and the project they "
        "make carries its own name and is deleted again afterwards.",
    "resolve/project_pool_takes_all_test.py":
        "talks to a Resolve that is really running, on purpose, and is "
        "started by hand through resolve.sh.",
    "resolve/project_run_puts_back_test.py":
        "talks to a Resolve that is really running, on purpose, and is "
        "started by hand through resolve.sh. Its child script does too.",
    "resolve/project_settings_arrive_test.py":
        "talks to a Resolve that is really running, on purpose, and is "
        "started by hand through resolve.sh.",
    "resolve/resolve_ground.py":
        "the ground those four stand on, and the one place among them "
        "that asks for the connection -- a_resolve leaves the test out "
        "saying why when no Resolve answers.",
    "resolve/sweep.py":
        "deletes the projects those four made. It has to reach the "
        "project manager to do it, and it is run by hand.",
    "resolve.sh":
        "starts those four and the sweep, and asks Resolve itself in a "
        "block of Python written into it, to see whether one is there.",
}
EXCEPTIONS_ALLOWED = 7


def scan(text, path, piece, offset, found, doors, nail, depth=0):
    """Gather every call at a door and every replacement out of one piece.

    A test that builds a child script as a string and starts it goes
    through the door in source no scan of the outer file sees, so a
    string that looks like code is read as code -- and as a piece of its
    own, because the outer file's replacement does not reach a second
    process.
    """
    tree = parsed(text)
    if tree is None:
        return False
    key = (path, piece)
    found["pieces"].add(key)
    top = outermost(tree)
    for node in ast.walk(tree):
        line = getattr(node, "lineno", 0) + offset
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if last(target) in doors:
                    found["nail"].setdefault(key, []).append(
                        (last(target), line, id(node) in top))
        if isinstance(node, ast.Call) and last(node.func) in doors:
            found["call"].append((key, line, last(node.func), id(node) in top))
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and node.value in CONNECTING):
            found["switch"].append((key, line, node.value))
        if (depth < 2 and isinstance(node, ast.Constant)
                and isinstance(node.value, str) and len(node.value) > 20
                and any(k + "(" in node.value for k in doors)):
            if not scan(node.value, path, "the script at line %d" % line,
                        line - 1, found, doors, nail, depth + 1):
                found["unread"].append("%s, the script at line %d"
                                       % (path, line))
    return True


# ------------------------------------------------------------------ 1.
print("1. The doors, out of the program and out of the test beside this")
files, lost = suite()
there = files.get(SIBLING, "")
tree = parsed(there) if there else None
words, DOORS_THERE, NAIL = {}, (), ""
for node in ast.walk(tree) if tree is not None else ():
    if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
        for target in node.targets:
            if isinstance(node.value.value, str) and last(target):
                words[last(target)] = node.value.value
for node in ast.walk(tree) if tree is not None else ():
    if not (isinstance(node, ast.Assign) and len(node.targets) == 1):
        continue
    if last(node.targets[0]) == "SHUT" and isinstance(node.value, ast.Constant):
        NAIL = node.value.value
    if last(node.targets[0]) == "DOORS" and isinstance(node.value,
                                                       (ast.Tuple, ast.List)):
        out = []
        for piece in node.value.elts:
            if isinstance(piece, ast.Constant) and isinstance(piece.value, str):
                out.append(piece.value)
            elif last(piece) in words:
                out.append(words[last(piece)])
        DOORS_THERE = tuple(out)
check("the doors and the nail come out of the test that listed them",
      bool(DOORS_THERE) and bool(NAIL),
      "%d doors and the nail %r out of %s"
      % (len(DOORS_THERE), quiet(NAIL or "none found"), SIBLING))

DOORS = tuple(sorted(set(DOORS_THERE) | set(DOORS_HERE)))
program = ""
try:
    program = io.open(SCRIPT, encoding="utf-8").read()
except (OSError, UnicodeDecodeError):
    program = ""
opens = calls_in(program, ("scriptapp",)) if program else None
holders = sorted((opens or {}).get("scriptapp", ()))
check("the program opens its connection in the one place a test nails",
      holders == [NAIL] and bool(NAIL),
      "scriptapp is called in %s, the nail is %r, %d characters of %s"
      % (quiet(", ".join(holders) or "nothing this could read"),
         quiet(NAIL or "none"), len(program), quiet(os.path.basename(SCRIPT))))

reached = calls_in(program, (NAIL,)) if (program and NAIL) else None
ground = calls_in(files.get(GROUND, ""), (NAIL,)) if NAIL else None
openers = set()
for one in ((reached or {}).get(NAIL, ()), (ground or {}).get(NAIL, ())):
    openers |= set(one)
openers.discard("<module>")
unknown = sorted(openers - set(DOORS))
check("every function that opens the connection is a door known here",
      bool(openers) and not unknown,
      "%d of %d openers are not among the %d doors: %s"
      % (len(unknown), len(openers), len(DOORS),
         quiet(", ".join(unknown)) or "none"))
for door in sorted(set(DOORS_HERE) - set(DOORS_THERE)):
    print("      %s is a door %s does not know: it opens the connection "
          "and makes no project" % (door, SIBLING))

# ------------------------------------------------------------------ 2.
print("\n2. Every file of the suite was read, the set-aside ones too")
found = {"call": [], "nail": {}, "switch": [], "pieces": set(),
         "unread": list(lost)}
for path in sorted(files):
    text = files[path]
    if path.endswith(".sh"):
        for at, body in blocks(text):
            if not any(k + "(" in body for k in DOORS):
                continue
            if not scan(body, path, "the block at line %d" % at, at - 1,
                        found, DOORS, NAIL):
                found["unread"].append("%s, the block at line %d" % (path, at))
        continue
    if not scan(text, path, "the file", 0, found, DOORS, NAIL):
        found["unread"].append(path)
check("every file the repository names under tests/ was read",
      not found["unread"], "%d of %d not read: %s"
      % (len(found["unread"]), len(files),
         quiet(", ".join(sorted(found["unread"])[:4])) or "none"))

# ------------------------------------------------------------------ 3.
print("\n3. Every call at a door, against the nail above it")
for path in sorted(ALLOWED):
    if path in files:
        print("      excepted by name: %s" % path)


def nailed(key, door, line, at_top):
    """The line the door was nailed shut on, or None.

    connect_to_resolve replaced shuts every door behind it; a door
    replaced by name shuts that one. At module level, and before the
    call where the call itself stands at module level -- a nail set
    afterwards was not there when the call was made.
    """
    for name, at, top in found["nail"].get(key, ()):
        if not top or name not in (NAIL, door):
            continue
        if at_top and at > line:
            continue
        return at
    return None


judged, open_doors = 0, []
for key, line, door, at_top in sorted(found["call"], key=lambda c: c[0][0]):
    if key[0] in ALLOWED:
        continue
    judged += 1
    if nailed(key, door, line, at_top) is None:
        open_doors.append("%s:%d %s" % (key[0], line, door))
check("there are calls at a door to judge at all", judged > 0,
      "%d calls in %d pieces of source, %d files excepted of %d read"
      % (judged, len(found["pieces"]),
         len([p for p in ALLOWED if p in files]), len(files)))
check("a test that calls at a door has nailed it shut first",
      not open_doors, "%d of %d calls stand open -- no %r replaced at module "
      "level above them: %s" % (len(open_doors), judged,
                                quiet(NAIL or "no nail"),
                                quiet("; ".join(open_doors[:4])) or "none"))
check("no more files are excepted than the ratchet allows",
      len(ALLOWED) <= EXCEPTIONS_ALLOWED, "%d excepted of at most %d%s: %s"
      % (len(ALLOWED), EXCEPTIONS_ALLOWED,
         " -- fewer here; the number comes down with them"
         if len(ALLOWED) < EXCEPTIONS_ALLOWED else "",
         quiet(", ".join(sorted(ALLOWED)))))

# ------------------------------------------------------------------ 4.
print("\n4. The switches that make the program connect on its own")
switches = set()
for node in ast.walk(parsed(program) or ast.parse("")):
    if (isinstance(node, ast.Call) and last(node.func) == "add_argument"
            and node.args and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)):
        switches.add(node.args[0].value)
gone = sorted(set(CONNECTING) - switches)
check("every switch named here is one the program still takes",
      not gone and bool(switches), "%d of %d not among the %d the program "
      "declares: %s" % (len(gone), len(CONNECTING), len(switches),
                        quiet(", ".join(gone)) or "none"))
carried = []
for key, line, switch in sorted(found["switch"], key=lambda s: s[0][0]):
    # This file has to write the switches down to look for them, and
    # cannot be judged by its own rule.
    if key[0] in ALLOWED or key[0] == ME:
        continue
    carried.append("%s:%d %s" % (key[0], line, switch))
check("no test hands the program a switch that makes it connect",
      not carried, "%d found, and a second process is past every "
      "replacement: %s" % (len(carried), quiet("; ".join(carried[:4]))
                           or "none"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
