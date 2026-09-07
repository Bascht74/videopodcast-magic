# -*- coding: utf-8 -*-
"""Looks for half-finished renames and other loose ends.

A name that is read but never set, and one that is set and never read
by anybody; a getattr on an attribute that does not exist; a dictionary
key that is written but never read. The move to English snagged on
those more than once, and no test noticed.

The program is a folder of pieces and every one of them is read, or a
piece cut out of the way in would take its loose ends out of sight with
it. The translations are read too, and they are not program: they are
data, and are held to the two things a translation owes.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import ast
import builtins
import collections
import glob
import io
import re
import sys
import subprocess
import symtable
import time

sys.path.insert(0, HERE)
import ratchet

began = time.time()

STATE = os.path.join(HERE, "state", "consistency_state.json")
state = ratchet.Ratchet(STATE)
PIECES = the_program.pieces()
TREES = [(where, ast.parse(body)) for where, body in PIECES]


def everywhere():
    """Every node of every piece, with the piece it stands in.

    The piece travels with the node because a line number on its own
    points into whichever file the reader happens to think of, and
    there is more than one now.
    """
    for where, tree in TREES:
        for node in ast.walk(tree):
            yield where, node


done = 0
error = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-54s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


state.announce()


print("1. Every piece the program loads was read")
# The program fetches its own pieces, and beside("language") is the
# one door: an import by name does not find them the way a test starts
# the program. So what it asks for and what was read here have to be
# the same list, or a piece nobody looked at may hold anything.
asked_for = set()
for where, node in everywhere():
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
            and node.func.id == "beside" and node.args \
            and isinstance(node.args[0], ast.Constant) \
            and isinstance(node.args[0].value, str):
        asked_for.add(node.args[0].value + "/__init__.py")
were_read = set(name for name, _body in PIECES)
never_read = sorted(asked_for - were_read)
check("every piece the program loads was read", not never_read,
      "%d piece(s) asked for, %d read (%s), never read: %s"
      % (len(asked_for), len(were_read), ", ".join(sorted(were_read)),
         never_read or "none"))

print("\n2. Every name that is read is also set")
# A name bound nowhere and not a piece of Python itself can only be a
# typo or a half-finished rename.
#
# The last two come from the compiler: __annotate__ for every scope
# that could carry annotations, __classdict__ for a class body. Both
# are read without ever being written in the source, which is what
# this check looks for, so they are named here rather than reported.
builtin_names = set(dir(builtins)) | {"__file__", "__name__",
                                      "__doc__", "__spec__",
                                      "__annotate__", "__classdict__"}
unresolved = []
looked_at = 0


def walk_block(where, block, module_names, chain):
    global looked_at
    for s in block.get_symbols():
        looked_at += 1
        if not s.is_referenced() or s.is_local() or s.is_parameter():
            continue
        name = s.get_name()
        if name in module_names or name in builtin_names:
            continue
        # free names from an enclosing function
        if any(name in c for c in chain):
            continue
        unresolved.append((where, block.get_name(), name))
    own = set(block.get_identifiers())
    for child in block.get_children():
        walk_block(where, child, module_names, chain + [own])


# Each piece is its own module: a name is at home where its own file
# binds it, and what one piece hands another it binds by name there.
for where, body in PIECES:
    table = symtable.symtable(body, where, "exec")
    walk_block(where, table, set(table.get_identifiers()), [])
unresolved = sorted(set(unresolved))
check("no name without an origin", not unresolved,
      "%d name(s) without one, out of %d looked at in %d piece(s): %s"
      % (len(unresolved), looked_at, len(PIECES), unresolved[:4]))

# And the other way round. The head lines `X = PROGRAM.X` at the top of
# a piece are written out for a reader and for the check above, not for
# the machine: take_from() has already put those names in place, so a
# line for a name nobody reads changes nothing and says something
# false. It is what a lift leaves behind. Measured 6.9.2026, after
# fourteen functions had moved out of gui(): seventeen such lines stood
# in ui/__init__.py, math and re among them.
#
# The entry is left out. It binds names for the pieces to fetch, so a
# name it never reads itself is the ordinary case there, not a loose
# end.
head_lines = 0
never_read = []
for where, body in PIECES:
    if where == "__init__.py":
        continue
    tree = ast.parse(body, where)
    heads = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target, value = node.targets[0], node.value
        if isinstance(target, ast.Name) \
                and isinstance(value, ast.Attribute) \
                and isinstance(value.value, ast.Name) \
                and value.value.id == "PROGRAM":
            heads.setdefault(target.id, node.lineno)
    head_lines += len(heads)
    read = set(node.id for node in ast.walk(tree)
               if isinstance(node, ast.Name)
               and isinstance(node.ctx, ast.Load))
    for name in sorted(heads):
        if name not in read:
            never_read.append("%s:%d %s" % (where, heads[name], name))
check("no name fetched from the way in that its piece never reads",
      not never_read, "%d of %d head lines dead, first: %s"
      % (len(never_read), head_lines, never_read[:4] or "none"))

print("\n3. getattr/hasattr/setattr hit an attribute that exists")
# Every name the module ever sets or reads as an attribute.
attributes = set()
for where, node in everywhere():
    if isinstance(node, ast.Attribute):
        attributes.add(node.attr)
    if isinstance(node, ast.FunctionDef):
        attributes.add(node.name)
    # A name bound in a class body is an attribute too, even though it
    # never appears as one.
    if isinstance(node, ast.ClassDef):
        for inner in node.body:
            if isinstance(inner, ast.Assign):
                for target in inner.targets:
                    if isinstance(target, ast.Name):
                        attributes.add(target.id)
            elif isinstance(inner, ast.AnnAssign) \
                    and isinstance(inner.target, ast.Name):
                attributes.add(inner.target.id)
# args is the argparse namespace: there the targets of the switches
# count, because some of them are set on one path only.
targets = set()
for where, node in everywhere():
    if isinstance(node, ast.Call) \
            and isinstance(node.func, ast.Attribute) \
            and node.func.attr == "add_argument":
        dest = None
        for kw in node.keywords:
            if kw.arg == "dest" and isinstance(kw.value, ast.Constant):
                dest = kw.value.value
        if dest is None:
            for a in node.args:
                if isinstance(a, ast.Constant) \
                        and str(a.value).startswith("--"):
                    dest = str(a.value)[2:].replace("-", "_")
        if dest:
            targets.add(dest)
# What the run itself writes into the namespace counts as well.
for where, node in everywhere():
    if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
        targets.add(node.attr)
# The test knows nothing about foreign objects; all the rest is checked.
FOREIGN = ("os", "sys", "np", "re", "QtCore", "QtGui", "QtWidgets",
           "QtMultimedia", "Qt", "locale", "ctypes", "shutil", "time")
wrong = []
reached = 0
for where, node in everywhere():
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in ("getattr", "hasattr", "setattr")):
        continue
    if len(node.args) < 2 or not isinstance(node.args[1], ast.Constant):
        continue
    name = node.args[1].value
    if not isinstance(name, str):
        continue
    base = node.args[0].id if isinstance(node.args[0], ast.Name) else ""
    if base in FOREIGN:
        continue
    reached += 1
    allowed = targets if base == "args" else attributes
    if name not in allowed:
        wrong.append(("%s line %d" % (where, node.lineno), base, name))
check("no access to an attribute without a counterpart", not wrong,
      "%d without one, out of %d asked for by name over %d attribute(s): %s"
      % (len(wrong), reached, len(attributes), wrong[:4]))

print("\n4. Dictionary keys are both written and read")
# After a rename, a key that is only written or only read is the most
# common leftover.
writes = collections.Counter()
reads = collections.Counter()
first = {}
for where, node in everywhere():
    if isinstance(node, ast.Dict):
        for x in node.keys:
            if isinstance(x, ast.Constant) and isinstance(x.value, str):
                writes[x.value] += 1
                first.setdefault(x.value, "%s line %d" % (where, x.lineno))
    elif isinstance(node, ast.Subscript) \
            and isinstance(node.slice, ast.Constant) \
            and isinstance(node.slice.value, str):
        if isinstance(node.ctx, ast.Store):
            writes[node.slice.value] += 1
            first.setdefault(node.slice.value,
                             "%s line %d" % (where, node.lineno))
        else:
            reads[node.slice.value] += 1
    elif isinstance(node, ast.Call) \
            and isinstance(node.func, ast.Attribute) \
            and node.func.attr in ("get", "pop", "setdefault") \
            and node.args \
            and isinstance(node.args[0], ast.Constant) \
            and isinstance(node.args[0].value, str):
        reads[node.args[0].value] += 1
# Only our own keys: the ones from foreign answers (ffprobe, Auphonic,
# Resolve) are read only, by their very nature.
FOREIGN = re.compile(r"^[a-z_]+$")
write_only = sorted(k for k in writes
                    if k not in reads and FOREIGN.match(k)
                    and writes[k] > 1)
# The key is the fingerprint: it is written in a dozen places, so it
# has no one line, and the name is what has to stop turning up.
held = state.places("write_only",
                    dict((k, (1, first.get(k, 0))) for k in write_only))
check("keys nobody reads: %d (ratchet %d)"
      % (len(write_only), held.limit), held.ok,
      str(write_only[:5]))
held.report()

print("\n5. Qt signals and slots match up")
signals = set()
for where, node in everywhere():
    # Both spellings: Signal(...) and QtCore.Signal(...). Looking only
    # for the first finds nothing at all.
    if not (isinstance(node, ast.Assign) and isinstance(node.value, ast.Call)):
        continue
    f = node.value.func
    name = (f.id if isinstance(f, ast.Name)
            else f.attr if isinstance(f, ast.Attribute) else "")
    if name != "Signal":
        continue
    for target in node.targets:
        if isinstance(target, ast.Name):
            signals.add(target.id)
check("signals found at all", bool(signals), "%d" % len(signals))
used = set()
for where, node in everywhere():
    if isinstance(node, ast.Attribute) \
            and node.attr in ("connect", "emit") \
            and isinstance(node.value, ast.Attribute):
        used.add(node.value.attr)
unused = sorted(signals - used)
check("every signal is also used", not unused, str(unused[:4]))

print("\n6. Calls match the signature")
# The signatures come from every piece, and a call by bare name is
# looked up in all of them: T() is written here and defined next door,
# and a signature that cannot be found is a call nobody judges.
functions = {}
for where, node in everywhere():
    if isinstance(node, ast.FunctionDef):
        required = len(node.args.args) - len(node.args.defaults)
        functions.setdefault(node.name, []).append(
            (required, len(node.args.args), node.args.vararg is not None,
             set(a.arg for a in node.args.args + node.args.kwonlyargs)))


def own_names(fn):
    """The names a function binds itself, nested definitions left out.

    A name bound in a nested definition is that definition's own; it
    says nothing about the text around it.
    """
    args = fn.args
    names = set(a.arg for a in args.args + args.kwonlyargs
                + getattr(args, "posonlyargs", []))
    if args.vararg:
        names.add(args.vararg.arg)
    if args.kwarg:
        names.add(args.kwarg.arg)

    def look(node):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef,
                                  ast.ClassDef)):
                names.add(child.name)
                continue
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
                names.add(child.id)
            elif isinstance(child, (ast.Import, ast.ImportFrom)):
                for one in child.names:
                    names.add((one.asname or one.name).split(".")[0])
            elif isinstance(child, ast.ExceptHandler) and child.name:
                names.add(child.name)
            look(child)

    # A lambda's body is one expression, a function's is a list.
    for step in fn.body if isinstance(fn.body, list) else [fn.body]:
        look(step)
    return names


def calls_with_scope():
    """Every call by bare name, with the names bound around it.

    A call whose name is a parameter, a local assignment or a loop
    variable is not a call of the program's function of that name, and
    holding it against that signature is a false alarm. Only function
    scopes count: at module level a bare name really is the global one.
    """
    found = []
    here = [""]

    def walk(node, bound):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                found.append((here[0], child, bound))
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                inner = bound | own_names(child)
                for step in child.body:
                    walk(step, inner)
                # Decorators and default values are read where the
                # definition stands, not inside it.
                for step in child.decorator_list + child.args.defaults:
                    walk(step, bound)
                continue
            if isinstance(child, ast.Lambda):
                walk(child.body, bound | own_names(child))
                continue
            if isinstance(child, (ast.ListComp, ast.SetComp, ast.DictComp,
                                  ast.GeneratorExp)):
                inner = set(bound)
                for gen in child.generators:
                    for name in ast.walk(gen.target):
                        if isinstance(name, ast.Name):
                            inner.add(name.id)
                walk(child, inner)
                continue
            walk(child, bound)

    for where, tree in TREES:
        here[0] = where
        walk(tree, set())
    return found


bad_calls = []
judged = 0
passed_over = 0
shadowed = 0
for where, node, bound in calls_with_scope():
    sig = functions.get(node.func.id)
    if not sig:
        continue
    if node.func.id in bound:
        # The name is bound where the call stands, so this is not the
        # program's function of that name.
        shadowed += 1
        continue
    if len(sig) != 1:
        passed_over += 1
        continue
    required, max_args, star, names = sig[0]
    n = len(node.args)
    kw = set(x.arg for x in node.keywords if x.arg)
    if any(x.arg is None for x in node.keywords) \
            or any(isinstance(a, ast.Starred) for a in node.args):
        continue
    judged += 1
    at = "%s line %d" % (where, node.lineno)
    if n > max_args and not star:
        bad_calls.append((at, node.func.id, "too many: %d of %d"
                          % (n, max_args)))
    elif n + len(kw) < required:
        bad_calls.append((at, node.func.id, "too few: %d of %d"
                          % (n + len(kw), required)))
    elif kw - names:
        bad_calls.append((at, node.func.id,
                          "unknown: %s" % sorted(kw - names)))
# The three counts are the reach: a section that judges nothing is
# green and says so, instead of reporting no fault over an empty
# search. The third one is new -- a call whose name is bound where it
# stands is not this function's call, and counting them apart shows
# whether the new rule is quietly eating the section.
check("no call with the wrong number of values", not bad_calls,
      "%d wrong of %d calls judged in %d piece(s), %d passed over for a "
      "name defined more than once, %d for a name bound where the call "
      "stands: %s"
      % (len(bad_calls), judged, len(PIECES), passed_over, shadowed,
         bad_calls[:4]))

print("\n7. What the catalogue promises does exist")
# The translations do not stand in the program any more; each language
# is a file `<code>.po` in the folder "language" beside the way in.
# `texts_of_language` reads them from there whatever the copy that is
# running is called, so this looks in the same place -- and it takes
# every file it finds there rather than one by name, because a language
# added tomorrow would otherwise be the next thing nobody measures.
BESIDE = os.path.join(os.path.dirname(os.path.abspath(SCRIPT)), "language")
languages = sorted(glob.glob(os.path.join(BESIDE, "*.po")))
# The pairs as they stand in the file. A dictionary keeps one value per
# key -- a key written twice with two translations loses one of them
# without a sound -- so they are gathered as a list, before any
# dictionary exists.
pairs = []
for path in languages:
    where = os.path.basename(path)
    for key, value, at in the_program.po_pairs(path):
        pairs.append((key, value, where, at))
# Without this the two judgements below stand over an empty list and are
# green for nothing -- which is what they were the day the texts moved
# out of the program and this section went on reading the program.
silent = sorted(set(os.path.basename(p) for p in languages)
                - set(w for _, _, w, _ in pairs))
check("the languages beside the program were read",
      bool(languages) and not silent,
      "%d files in %s, %d entries in them, read nothing: %s"
      % (len(languages),
         os.path.join(os.path.basename(os.path.dirname(BESIDE)),
                      os.path.basename(BESIDE)),
         len(pairs), silent[:3] or "none"))
P = re.compile(r"%[-+ #0-9.*]*[a-zA-Z%]")
mismatched = ["%s line %d: %r wants %s, the translation has %s"
              % (where, at, key[:40], P.findall(key), P.findall(value))
              for key, value, where, at in pairs
              if P.findall(key) != P.findall(value)]
check("placeholders the same in both languages", not mismatched,
      "%d of %d entries differ, first: %s"
      % (len(mismatched), len(pairs), mismatched[:3]))
meanings = collections.defaultdict(dict)
for key, value, where, at in pairs:
    meanings[(where, key)].setdefault(value, at)
duplicates = ["%s line %d: %r means %r and %r"
              % (where, sorted(said.values())[1], key[:40],
                 sorted(said)[0][:40], sorted(said)[1][:40])
              for (where, key), said in meanings.items() if len(said) > 1]
check("no two meanings per key", not duplicates,
      "%d of %d entries said twice, first: %s"
      % (len(duplicates), len(pairs), duplicates[:3]))

print("\n8. Tests that check something")
# A test that only prints catches a crash and nothing else. A ratchet,
# so the ones still like that can be mended one at a time and no new
# one joins them.
mute = []
for name in sorted(os.listdir(HERE)):
    if not name.endswith("_test.py"):
        continue
    try:
        t = ast.parse(open(os.path.join(HERE, name), encoding="utf-8").read())
    except SyntaxError:
        continue
    speaks = any(
        isinstance(k, ast.Assert)
        or (isinstance(k, ast.Call) and isinstance(k.func, ast.Name)
            and k.func.id == "check")
        for k in ast.walk(t))
    if not speaks:
        mute.append(name)
# Here the file name is the fingerprint; the finds are spread over many
# files rather than sitting in the program.
held = state.places("mute_tests", dict((n, (1, 0)) for n in mute))
check("tests without a single check: %d (ratchet %d)"
      % (len(mute), held.limit), held.ok,
      "%d tests against a ratchet of %d, first: %s"
      % (len(mute), held.limit, mute[:5]))
held.report()
for name in mute:
    print("      %s" % name)

print("\n9. Every name a piece defines is read somewhere")
# The mirror of section 2. That one finds a name read and never set;
# this one finds a name set and never read -- by anybody, in any piece
# or any test. Section 3 of source_no_loose_ends cannot see it: it
# judges `X = PROGRAM.X` head lines, not definitions.
#
# "No reader in its own piece" is the ordinary case here and not a
# fault: a piece exists to hold names other pieces call. What is a
# fault is a name nobody anywhere reads, and two of those were found
# by hand on 7.9.2026 -- queue_once, left behind in the window when
# its callers moved out, and voices_on_cameras, whose two callers went
# in a clean-up eight days earlier while it stayed.
defined, first_at = {}, {}
for name, body in PIECES:
    piece = name.split("/")[0]
    for node in ast.parse(body).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.setdefault(node.name, piece)
            first_at.setdefault(node.name, "%s line %d" % (name, node.lineno))
        elif isinstance(node, ast.Assign):
            # A handle on another piece -- `filelist = beside("filelist")`
            # -- is not a definition of anything. It is read only in the
            # `X = filelist.X` lines under it, which this section skips
            # as bindings, so counting it would report it every time.
            if isinstance(node.value, ast.Call) \
                    and isinstance(node.value.func, ast.Name) \
                    and node.value.func.id == "beside":
                continue
            for target in node.targets:
                if isinstance(target, ast.Name):
                    defined.setdefault(target.id, piece)
                    first_at.setdefault(target.id,
                                        "%s line %d" % (name, node.lineno))


def is_binding(node):
    """A line that only fetches a name: `X = PROGRAM.X` or `X = piece.X`."""
    if not (isinstance(node, ast.Assign) and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and isinstance(node.value, ast.Attribute)):
        return False
    return node.value.attr == node.targets[0].id


read_somewhere = set()
for name, body in PIECES:
    for node in ast.parse(body).body:
        if is_binding(node):
            continue
        own = getattr(node, "name", None)
        for inner in ast.walk(node):
            if isinstance(inner, ast.Name) and isinstance(inner.ctx, ast.Load):
                if inner.id != own:
                    read_somewhere.add(inner.id)
            elif isinstance(inner, ast.Attribute):
                read_somewhere.add(inner.attr)
# A name a test reaches for is read, even when no piece calls it.
# **The repository, not the folder.** The builder moves the tests a
# machine cannot run out of tests/ before the suite starts, and their
# names would then look unread: measured 7.9.2026, this section said 7
# here and 10 on both macOS jobs, the extra ones reached only by a test
# that had been set aside. So the list comes from git, and a file that
# is listed but not on disk is read out of the last commit.
ROOT = os.path.dirname(HERE)
shipped = []
try:
    listed = subprocess.run(("git", "-C", ROOT, "ls-files", "-z", "tests"),
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if listed.returncode == 0:
        shipped = [x for x in listed.stdout.decode("utf-8", "ignore").split("\0")
                   if x.endswith(".py")]
except OSError:
    shipped = []
from_git = 0
if not shipped:
    shipped = ["tests/" + n for n in sorted(os.listdir(HERE))
               if n.endswith(".py")]
for rel in shipped:
    full = os.path.join(ROOT, rel)
    if os.path.exists(full):
        text = io.open(full, encoding="utf-8", errors="ignore").read()
    else:
        got = subprocess.run(("git", "-C", ROOT, "show", "HEAD:" + rel),
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        if got.returncode != 0:
            continue
        text = got.stdout.decode("utf-8", "ignore")
        from_git += 1
    read_somewhere |= set(re.findall(r"[A-Za-z_][A-Za-z_0-9]*", text))
unread = sorted(n for n in defined if n not in read_somewhere)
held = state.places("unread_names",
                    dict((n, (1, first_at.get(n, 0))) for n in unread))
check("names nobody reads: %d (ratchet %d)" % (len(unread), held.limit),
      held.ok, "%d against a ratchet of %d over %d test files (%d out of "
      "the last commit), first: %s"
      % (len(unread), held.limit, len(shipped), from_git, unread[:5]))
held.report()
for n in unread:
    print("      %-32s %s" % (n, first_at.get(n, "")))

print("\n%d checks in %.2f s" % (done, time.time() - began))
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
