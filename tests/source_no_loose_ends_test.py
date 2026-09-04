# -*- coding: utf-8 -*-
"""Looks for half-finished renames and other loose ends.

A name that is read but never set; a getattr on an attribute that does
not exist; a dictionary key that is written but never read. The move to
English snagged on exactly those more than once, and no test noticed.

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
bad_calls = []
judged = 0
passed_over = 0
for where, node in everywhere():
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
        continue
    sig = functions.get(node.func.id)
    if not sig:
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
# The two counts are the reach: a section that judges nothing is green
# and says so, instead of reporting no fault over an empty search.
check("no call with the wrong number of values", not bad_calls,
      "%d wrong of %d calls judged in %d piece(s), %d passed over for a "
      "name defined more than once: %s"
      % (len(bad_calls), judged, len(PIECES), passed_over, bad_calls[:4]))

print("\n7. What the catalogue promises does exist")
# The translations do not stand in the program any more; each language
# is a file `<code>.py` in the folder "language" beside the way in,
# holding one name. `texts_of_language` reads them from there whatever
# the copy that is running is called, so this looks in the same place --
# and it takes every file it finds there rather than one by name,
# because a language added tomorrow would otherwise be the next thing
# nobody measures. Only `__init__.py` is left out: it carries no texts
# and is there so that pip ships the folder at all.
BESIDE = os.path.join(os.path.dirname(os.path.abspath(SCRIPT)), "language")
languages = sorted(p for p in glob.glob(os.path.join(BESIDE, "*.py"))
                   if os.path.basename(p) != "__init__.py")
# The pairs as they stand in the source. `ast.literal_eval` would make a
# dict of them, and a dict keeps one value per key -- a key written twice
# with two translations loses one of them without a sound. So they are
# gathered while the tree is walked, before any dict exists.
pairs = []
for path in languages:
    where = os.path.basename(path)
    for node in ast.walk(ast.parse(io.open(path, encoding="utf-8").read())):
        if not (isinstance(node, ast.Assign)
                and isinstance(node.value, ast.Dict)
                and any(isinstance(t, ast.Name) and t.id == "TEXTS"
                        for t in node.targets)):
            continue
        for key, value in zip(node.value.keys, node.value.values):
            if isinstance(key, ast.Constant) and isinstance(key.value, str) \
                    and isinstance(value, ast.Constant) \
                    and isinstance(value.value, str):
                pairs.append((key.value, value.value, where, key.lineno))
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

print("\n%d checks in %.2f s" % (done, time.time() - began))
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
