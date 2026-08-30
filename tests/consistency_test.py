# -*- coding: utf-8 -*-
"""Looks for half-finished renames and other loose ends.

A name that is read but never set; a getattr on an attribute that does
not exist; a dictionary key that is written but never read. The move to
English snagged on exactly those more than once, and no test noticed.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import ast
import builtins
import collections
import io
import re
import sys
import symtable

sys.path.insert(0, HERE)
import ratchet

STATE = os.path.join(HERE, "state", "consistency_state.json")
state = ratchet.Ratchet(STATE)
src = io.open(SCRIPT, encoding="utf-8").read()
tree = ast.parse(src)
lines = src.split("\n")

error = []


def check(name, ok, extra=""):
    print("  %-54s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


state.announce()


print("1. Every name that is read is also set")
# A name bound nowhere and not a piece of Python itself can only be a
# typo or a half-finished rename.
table = symtable.symtable(src, "vpm", "exec")
module_names = set(table.get_identifiers())
# The last two come from the compiler: __annotate__ for every scope
# that could carry annotations, __classdict__ for a class body. Both
# are read without ever being written in the source, which is what
# this check looks for, so they are named here rather than reported.
builtin_names = set(dir(builtins)) | {"__file__", "__name__",
                                      "__doc__", "__spec__",
                                      "__annotate__", "__classdict__"}
unresolved = []


def walk_block(block, chain):
    for s in block.get_symbols():
        if not s.is_referenced() or s.is_local() or s.is_parameter():
            continue
        name = s.get_name()
        if name in module_names or name in builtin_names:
            continue
        # free names from an enclosing function
        if any(name in c for c in chain):
            continue
        unresolved.append((block.get_name(), name))
    own = set(block.get_identifiers())
    for child in block.get_children():
        walk_block(child, chain + [own])


walk_block(table, [])
unresolved = sorted(set(unresolved))
check("no name without an origin", not unresolved,
      str(unresolved[:4]))

print("\n2. getattr/hasattr/setattr hit an attribute that exists")
# Every name the module ever sets or reads as an attribute.
attributes = set()
for node in ast.walk(tree):
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
for node in ast.walk(tree):
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
for node in ast.walk(tree):
    if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
        targets.add(node.attr)
# The test knows nothing about foreign objects; all the rest is checked.
FOREIGN = ("os", "sys", "np", "re", "QtCore", "QtGui", "QtWidgets",
           "QtMultimedia", "Qt", "locale", "ctypes", "shutil", "time")
wrong = []
for node in ast.walk(tree):
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
    allowed = targets if base == "args" else attributes
    if name not in allowed:
        wrong.append((node.lineno, base, name))
check("no access to an attribute without a counterpart", not wrong,
      str(wrong[:4]))

print("\n3. Dictionary keys are both written and read")
# After a rename, a key that is only written or only read is the most
# common leftover.
writes = collections.Counter()
reads = collections.Counter()
first = {}
for node in ast.walk(tree):
    if isinstance(node, ast.Dict):
        for x in node.keys:
            if isinstance(x, ast.Constant) and isinstance(x.value, str):
                writes[x.value] += 1
                first.setdefault(x.value, x.lineno)
    elif isinstance(node, ast.Subscript) \
            and isinstance(node.slice, ast.Constant) \
            and isinstance(node.slice.value, str):
        if isinstance(node.ctx, ast.Store):
            writes[node.slice.value] += 1
            first.setdefault(node.slice.value, node.lineno)
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

print("\n4. Qt signals and slots match up")
signals = set()
for node in ast.walk(tree):
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
for node in ast.walk(tree):
    if isinstance(node, ast.Attribute) \
            and node.attr in ("connect", "emit") \
            and isinstance(node.value, ast.Attribute):
        used.add(node.value.attr)
unused = sorted(signals - used)
check("every signal is also used", not unused, str(unused[:4]))

print("\n5. Calls match the signature")
functions = {}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        required = len(node.args.args) - len(node.args.defaults)
        functions.setdefault(node.name, []).append(
            (required, len(node.args.args), node.args.vararg is not None,
             set(a.arg for a in node.args.args + node.args.kwonlyargs)))
bad_calls = []
for node in ast.walk(tree):
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
        continue
    sig = functions.get(node.func.id)
    if not sig or len(sig) != 1:
        continue
    required, max_args, star, names = sig[0]
    n = len(node.args)
    kw = set(x.arg for x in node.keywords if x.arg)
    if any(x.arg is None for x in node.keywords) \
            or any(isinstance(a, ast.Starred) for a in node.args):
        continue
    if n > max_args and not star:
        bad_calls.append((node.lineno, node.func.id, "too many: %d of %d"
                          % (n, max_args)))
    elif n + len(kw) < required:
        bad_calls.append((node.lineno, node.func.id, "too few: %d of %d"
                          % (n + len(kw), required)))
    elif kw - names:
        bad_calls.append((node.lineno, node.func.id,
                          "unknown: %s" % sorted(kw - names)))
check("no call with the wrong number of values", not bad_calls,
      str(bad_calls[:4]))

print("\n6. What the catalogue promises does exist")
catalogue = {}
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict) \
            and isinstance(node.targets[0], ast.Subscript) \
            and len(node.value.keys) > 10:
        for key, value in zip(node.value.keys, node.value.values):
            if isinstance(key, ast.Constant) \
                    and isinstance(value, ast.Constant):
                catalogue[key.value] = value.value
P = re.compile(r"%[-+ #0-9.*]*[a-zA-Z%]")
mismatched = [k for k, v in catalogue.items()
              if P.findall(k) != P.findall(v)]
check("placeholders the same in both languages", not mismatched,
      str(mismatched[:3]))
duplicates = []   # a dict cannot carry the same key twice
check("no two meanings per key", not duplicates, str(duplicates[:3]))

print("\n7. Tests that check something")
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
      % (len(mute), held.limit), held.ok)
held.report()
for name in mute:
    print("      %s" % name)

print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
