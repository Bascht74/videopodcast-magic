# -*- coding: utf-8 -*-
"""No language answers fewer of the program's texts than it did before.

What the catalogues were held to was that they carry the same
placeholders and no key twice, never how much of the program they
cover -- and for months nothing said that most of them covered a
quarter of it.

A counted thing is one text here, not two: TN() carries a singular and
a plural of the same sentence, and one block keyed by the singular
answers both.

What the program says is every text handed to T() or TN(), bound as
Python binds the call, so a keyword counts like a position. A literal
is said as it stands. Anything else is traced back -- through the
function it stands in, the callers of that function, and every loop,
lookup and unpacking on the way -- to where its value comes from, and
has to end in a text field of a table named here, or the call is red
with what it drew on. A text put together is red too, even out of two
table texts: what T() is handed is then neither of them. T() handed on
as a value or taken in under another name is red the same way, because
its calls cannot be read. A named table has to be one literal that
nothing writes into afterwards, its texts written out; and a lookup
that falls back to its own key has to be handed only keys that stand in
the table, so the fallback is never what is said. The limit: a table
changed under another name it was given, a table reached through
getattr(), and T() reached through getattr() by a name not written
out, are not seen. Nor are three shapes read for what they are: a text
handed on through a @staticmethod, whose arguments are counted as if it
took self, so another argument is traced; an attribute of any object
that carries a table's name, which is taken for the table itself; and a
name T() reads in a class body, which is looked up in the module around
it.

The sections: what the program says as literals; what reaches T()
through a table, and that those tables stand, written out and never
written into; that no fallback hands on a key its table lacks; that no
shipped catalogue carries an empty translation, which would blank a
label rather than leave it English; that what each language answers
may only grow, never shrink; that every catalogue on disk answers all
of it; and that the languages the window offers and the catalogues on
disk are the same set, so neither can appear without the other.
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
import ast
import inspect
import re
import the_program
SCRIPT = the_program.SCRIPT
import sys, time
import ratchet
vpm = the_program.load()
began = time.time()
STATE = os.path.join(HERE, "state", "coverage_state.json")
state = ratchet.Ratchet(STATE)
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


state.announce()
HOME = os.path.dirname(SCRIPT)
CATALOGUES = sorted(
    (os.path.splitext(os.path.basename(p))[0], os.path.join(HOME, "language", p))
    for p in os.listdir(os.path.join(HOME, "language")) if p.endswith(".po"))

trees = dict((name, ast.parse(body)) for name, body in the_program.pieces())
# Which parameters of the two sayers are texts is this test's knowledge:
# T's first, TN's second and third (the first is the count). What they
# are called is asked of the loaded program, so that a keyword call is
# bound by the names the program really gives them -- and asked there,
# not of the pieces, so that a reading of the pieces that comes back
# empty still reaches the first check below instead of stopping here.
SAYERS = dict((name, [p.name for p in inspect.signature(
    getattr(vpm, name)).parameters.values()
    if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)])
    for name in ("T", "TN"))
TEXT_PARAMS = {"T": SAYERS["T"][:1], "TN": SAYERS["TN"][1:3]}


def sayer(call):
    """'T' or 'TN' where *call* calls one of them, plain or as x.T()."""
    f = call.func
    name = (f.id if isinstance(f, ast.Name)
            else f.attr if isinstance(f, ast.Attribute) else None)
    return name if name in TEXT_PARAMS else None


def text_args(call):
    """What *call* hands over as texts, one per text parameter.

    Bound the way Python binds it: by position, else by keyword. None
    where it cannot be told -- a starred argument in front of it, or a
    ** mapping it would have to come out of.
    """
    names = SAYERS[sayer(call)]
    out = []
    for name in TEXT_PARAMS[sayer(call)]:
        at = names.index(name)
        by_word = [k.value for k in call.keywords if k.arg == name]
        if any(isinstance(a, ast.Starred) for a in call.args[:at + 1]):
            out.append(None)
        elif at < len(call.args):
            out.append(call.args[at])
        elif by_word:
            out.append(by_word[0])
        else:
            out.append(None)
    return out


def literal(node):
    return isinstance(node, ast.Constant) and isinstance(node.value, str)


print("\n1. What the program says")
# Every text handed to T() or TN() as a literal, over every piece --
# reading one file measures a program with holes in it the moment a
# piece moves out, and it moves out silently.
# A counted thing is one text, not two. TN() carries the singular and
# the plural of the same sentence, and a catalogue answers both with one
# block keyed by the singular -- po_pairs hands it back that way. Asking
# for the plural wording as an entry of its own demands a duplicate that
# nothing ever reads: measured, none of the 40 is said through T()
# anywhere in the program, and the forty standing in de.po are dead.
said = set()
second = set()
for _piece, tree in trees.items():
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and sayer(node)):
            continue
        words = [a.value if a is not None and literal(a) else None
                 for a in text_args(node)]
        if sayer(node) == "TN" and words[1] is not None:
            second.add(words[1])
        said.update(w for w in words if w is not None)
said -= second
check("the program was read, not an empty tree",
      len(said) > 1000,
      "%d texts out of %d pieces, %d plural wordings left aside"
      % (len(said), len(trees), len(second)))

print("\n1b. What reaches T() through a table")
# The literals above are not all of it. A label shown for a stored
# value, a caption of the cut box, a spoken language, a colour name: all
# of them reach T() as a variable, and before 24.9.2026 none of them
# stood in `said` -- 93 texts, and 27 catalogues had never been asked
# for them. So every text T() is handed that is not a literal is traced
# back to where its value comes from, and has to end in a text field of
# a table named here. The trace follows the value, not the spelling:
# `T(what_for)` is the same words whichever table the loop above it
# walks, and a list keyed by the words stayed green when the loop was
# pointed at a table nobody translated.
#
# Where each table stands. Which part of it is text is not written
# here: the trace says which field a call reads, and that field is read
# out of the source by `ast`, not out of the loaded program -- a value
# computed at run time is exactly what a reading cannot vouch for, so a
# text that is not written out is reported, not guessed at.
TABLES = {
    "CHOICE_LABELS": "choices/__init__.py",
    "SHOT_NAMES": "dials/__init__.py",
    "CUT_FIELDS": "dials/__init__.py",
    "CUT_CHOICES": "dials/__init__.py",
    "PLATFORMS": "preflight/__init__.py",
    "SPOKEN_LANGUAGES": "ui/__init__.py",
    "PRIMARIES_NAMES": "colour/__init__.py",
    "TRC_NAMES": "colour/__init__.py",
    "MATRIX_NAMES": "colour/__init__.py",
    "RESOLVE_REASONS": "resolve/__init__.py",
    "HINT_MULTICAM": "resolve/__init__.py",
}
# Standing in a text field and passed through T(), and English on
# purpose in every language: Resolve's own name for a setting, which the
# user looks for in Resolve as written there, and the names of colour
# standards and curves. Measured 24.9.2026: no catalogue translates any
# of them. Whether "linear" and "Film" belong here is not measured,
# only found so: they are the names H.273 gives, and nobody has said
# they should read otherwise.
KEPT_ENGLISH = {
    "Edit Change Delay",
    "BT.709", "BT.470 M", "BT.470 B/G", "BT.601 (SMPTE 170M)", "SMPTE 240M",
    "Film", "BT.2020", "XYZ", "DCI-P3", "Display P3", "EBU 3213-E",
    "Gamma 2.2", "Gamma 2.8", "linear", "xvYCC", "sRGB", "BT.2020 10 bit",
    "BT.2020 12 bit", "PQ (HDR10)", "SMPTE ST 428-1", "HLG", "Apple Log",
    "GBR", "FCC", "YCgCo", "SMPTE ST 2085", "ICtCp",
}

# The ground the trace walks: who stands in whom, which piece a module
# is, every call by the name it calls, and every name that is read as a
# value instead of being called.
parents = {}
piece_of = {}
calls_by_name = {}
handed = {}
for piece, tree in trees.items():
    piece_of[tree] = piece
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
for piece, tree in trees.items():
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            name = (f.id if isinstance(f, ast.Name)
                    else f.attr if isinstance(f, ast.Attribute) else None)
            calls_by_name.setdefault(name, []).append(node)
        # T taken in under another name, or fetched by getattr(): the
        # calls then go by a name no reading here knows.
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name in TEXT_PARAMS \
                        and alias.asname not in (None, alias.name):
                    handed.setdefault(alias.name, []).append((
                        piece, node, "taken in as %s" % alias.asname))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "getattr" and len(node.args) > 1 \
                and isinstance(node.args[1], ast.Constant) \
                and node.args[1].value in TEXT_PARAMS:
            handed.setdefault(node.args[1].value, []).append((
                piece, node, "fetched, " + ast.unparse(node)[:40]))
        name = (node.id if isinstance(node, ast.Name)
                else node.attr if isinstance(node, ast.Attribute) else None)
        up = parents.get(node)
        if name is None or not isinstance(node.ctx, ast.Load) \
                or isinstance(up, ast.Call) and up.func is node:
            continue
        # `T = PROGRAM.T` at the top of a piece is how every piece
        # reaches the program's own; that is taking it, not handing it.
        if isinstance(up, ast.Assign) and parents.get(up) is tree \
                and [getattr(t, "id", None) for t in up.targets] == [name]:
            continue
        handed.setdefault(name, []).append((
            piece, node, "handed on as a value, " + ast.unparse(up)[:40]))


def scopes_of(node):
    """The functions *node* stands in, innermost first, the module last."""
    chain = []
    while node in parents:
        node = parents[node]
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.Lambda, ast.Module)):
            chain.append(node)
    return chain


bound_in = {}
bound_raw = {}


def bindings(scope):
    """{name: [(how, what, where)]} for every name *scope* binds."""
    if scope in bound_in:
        return bound_in[scope]
    found = {}

    def put(target, how, what, at=()):
        if isinstance(target, ast.Name):
            found.setdefault(target.id, []).append((how, what, at))
        elif isinstance(target, (ast.Tuple, ast.List)):
            for i, one in enumerate(target.elts):
                if isinstance(one, ast.Starred):
                    put(one.value, "?", "a starred unpacking")
                else:
                    put(one, how, what, at + (i,))

    if not isinstance(scope, ast.Module):
        a = scope.args
        for p in a.posonlyargs + a.args + a.kwonlyargs:
            found.setdefault(p.arg, []).append(("param", scope, p.arg))
        for p in (a.vararg, a.kwarg):
            if p is not None:
                put(ast.Name(id=p.arg), "?", "a * parameter")
    outside = set()
    todo = list(ast.iter_child_nodes(scope))
    while todo:
        node = todo.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)):
            put(ast.Name(id=node.name), "?", "a function or a class")
            continue
        if isinstance(node, ast.Lambda):
            continue
        todo.extend(ast.iter_child_nodes(node))
        if isinstance(node, (ast.Global, ast.Nonlocal)):
            outside.update(node.names)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                put(t, "value", node.value)
        elif isinstance(node, ast.AugAssign):
            put(node.target, "aug", node)
        elif isinstance(node, (ast.AnnAssign, ast.NamedExpr)) \
                and node.value is not None:
            put(node.target, "value", node.value)
        elif isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)):
            put(node.target, "iter", node.iter)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                put(ast.Name(id=(alias.asname or alias.name).split(".")[0]),
                    "?", "an import")
        elif isinstance(node, ast.withitem) and node.optional_vars:
            put(node.optional_vars, "?", "a with statement")
        elif isinstance(node, ast.ExceptHandler) and node.name:
            put(ast.Name(id=node.name), "?", "an exception")
    bound_raw[scope] = dict(found)
    for name in outside:
        found.pop(name, None)
    # A function inside this one, or inside this piece, can bind one of
    # its names again through `nonlocal` or `global`. What it puts there
    # is not followed, only named, so a value that may come from it
    # cannot pass as traced.
    for node in ast.walk(scope):
        if not isinstance(node, (ast.Global, ast.Nonlocal)):
            continue
        inner = scopes_of(node)[0]
        if inner is scope or isinstance(node, ast.Global) != isinstance(
                scope, ast.Module):
            continue
        bindings(inner)
        for name in node.names:
            if name in bound_raw[inner]:
                found.setdefault(name, []).append((
                    "?", "%s bound again in %s() through %s" % (
                        name, getattr(inner, "name", "a lambda"),
                        type(node).__name__.lower()), ()))
    bound_in[scope] = found
    return found


# A path says where a value comes from: a root and the steps taken from
# it. `CUT_CHOICES[*][3][*]` is every element of field 3 of every row;
# `=text` is a literal, `?what` a place the trace cannot follow, and
# `!NAME` a table that is not one of those named here. The steps in
# brackets and `.key` can be read out of a table; the rest are on the
# way -- a collection not yet taken apart.
PAIRS = {"values()": "[*]", "keys()": ".key", "items()": ".item",
         "enumerate()": ".enum"}


def step(path, op):
    """*path* taken one step on: "iter", "*" (a lookup) or an index."""
    if path[0][0] == "?":
        return path
    last = path[-1]
    if last == "(+)":
        # Taken apart again, the two put together were collections, and
        # what comes out is an element of either -- at no index known.
        return step(path[:-1], op if op == "iter" else "*")
    if op == "iter" and last in PAIRS:
        return path[:-1] + (PAIRS[last],)
    if last == "[...]":
        return path[:-1]
    if last == ".item" and op in (0, 1):
        return path[:-1] + ((".key", "[*]")[op],)
    if last == ".enum" and op in (0, 1):
        return path[:-1] + (".count",) if op == 0 \
            else step(path[:-1], "iter")
    if path[0][0] == "=" or last in PAIRS or last in (".item", ".enum"):
        return ("?%s taken apart" % render(path),)
    if op == "iter":
        dict_table = len(path) == 1 and isinstance(
            table_literal.get(path[0]), ast.Dict)
        return path + ((".key" if dict_table else "[*]"),)
    return path + (("[*]" if op == "*" else "[%d]" % op),)


def render(path):
    if path[-1] == "(+)":
        return "%s, put together with another" % render(path[:-1])
    if path[0][0] == "=":
        return repr(path[0][1:])
    if path[0][0] == "!":
        return "%s%s, a table not named here" % (path[0][1:],
                                                 "".join(path[1:]))
    return path[0].lstrip("?") + "".join(path[1:])


def more(paths, mark):
    return set(p if p[0][0] == "?" else p + (mark,) for p in paths)


tracing = set()
fallbacks = {}


def trace(node):
    """Every path the value of *node* can come from."""
    if isinstance(node, ast.Constant):
        return {("=" + node.value,)} if literal(node) and node.value else set()
    if isinstance(node, ast.Name):
        return named(node)
    if isinstance(node, ast.Attribute) and node.attr in TABLES:
        return {(node.attr,)}
    if isinstance(node, ast.Subscript):
        if isinstance(node.slice, ast.Slice):
            return {("?a slice, %s" % ast.unparse(node)[:30],)}
        try:
            op = ast.literal_eval(node.slice)
        except (ValueError, TypeError, SyntaxError):
            op = "*"
        if not isinstance(op, int) or isinstance(op, bool):
            op = "*"
        return set(step(p, op) for p in trace(node.value))
    if isinstance(node, ast.Call):
        f = node.func
        if isinstance(f, ast.Attribute) and f.attr == "get" and node.args:
            out = set(step(p, "*") for p in trace(f.value))
            if len(node.args) > 1:
                if isinstance(node.args[1], ast.Constant):
                    out |= trace(node.args[1])
                else:
                    # Taken only when the key is not in the table: then
                    # it is the key's own business, and 1c asks it.
                    fallbacks[node] = True
            return out
        if isinstance(f, ast.Attribute) and not node.args \
                and f.attr in ("values", "keys", "items"):
            return more(trace(f.value), f.attr + "()")
        if isinstance(f, ast.Name) and node.args and f.id in (
                "sorted", "list", "tuple", "reversed", "set", "frozenset"):
            return trace(node.args[0])
        if isinstance(f, ast.Name) and f.id == "enumerate" and node.args:
            return more(trace(node.args[0]), "enumerate()")
        return {("?a call of %s()" % ast.unparse(f)[:30],)}
    if isinstance(node, (ast.ListComp, ast.GeneratorExp, ast.SetComp)):
        return more(trace(node.elt), "[...]")
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        out = set()
        for one in node.elts:
            out |= more(trace(one), "[...]")
        return out
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        # Two texts put together are a third, which no catalogue holds,
        # wherever the two came from; two lists put together are one
        # list. So both sides carry a mark that falls away only when the
        # value is taken apart again.
        return more(trace(node.left) | trace(node.right), "(+)")
    if isinstance(node, ast.IfExp):
        return trace(node.body) | trace(node.orelse)
    if isinstance(node, ast.BoolOp):
        out = set()
        for one in node.values:
            out |= trace(one)
        return out
    return {("?%s" % ast.unparse(node)[:30],)}


def named(node):
    """Where the name *node* reads comes from, in the scopes it stands in."""
    for scope in scopes_of(node):
        found = bindings(scope).get(node.id)
        if not found:
            continue
        if isinstance(scope, ast.Module):
            return named_at_top(node.id, piece_of[scope], found)
        out = set()
        for one in found:
            out |= bound(*one)
        return out
    return {("?%s, bound nowhere in its piece" % node.id,)}


def named_at_top(name, piece, found):
    """A name a piece binds at its top: a table, or traced on."""
    if name in TABLES and TABLES[name] == piece:
        return {(name,)}
    if name in TABLES and all(
            how == "value" and isinstance(what, ast.Attribute)
            and what.attr == name for how, what, _at in found):
        return {(name,)}
    if any(how == "value" and not at and (
            literal(what) or isinstance(what, (ast.Dict, ast.Tuple, ast.List)))
           for how, what, at in found):
        return {("!%s in %s" % (name, piece),)}
    out = set()
    for one in found:
        out |= bound(*one)
    return out


def bound(how, what, at):
    """Where a value bound one way comes from, taken apart as *at* says."""
    if how == "?":
        return {("?" + what,)}
    if how == "param":
        return handed_in(what, at)
    key = (what, at)
    if key in tracing:
        return set()
    tracing.add(key)
    try:
        if how == "aug" and isinstance(what.op, ast.Add):
            paths = more(trace(what.value), "(+)")
        elif how == "aug":
            paths = {("?%s" % ast.unparse(what)[:30],)}
        else:
            paths = trace(what)
        if how == "iter":
            paths = set(step(p, "iter") for p in paths)
        for i in at:
            paths = set(step(p, i) for p in paths)
        return paths
    finally:
        tracing.discard(key)


def handed_in(function, name):
    """Where parameter *name* of *function* comes from: its callers."""
    key = (function, name)
    if key in tracing:
        return set()
    if isinstance(function, ast.Lambda):
        return {("?parameter %s of a lambda" % name,)}
    if handed.get(function.name):
        return {("?parameter %s of %s(), which is handed on as a value"
                 % (name, function.name),)}
    calls = calls_by_name.get(function.name, [])
    if not calls:
        return {("?parameter %s of %s(), called nowhere"
                 % (name, function.name),)}
    tracing.add(key)
    a = function.args
    plain = [p.arg for p in a.posonlyargs + a.args]
    defaults = dict(zip(plain[len(plain) - len(a.defaults):], a.defaults))
    defaults.update((p.arg, d) for p, d in zip(a.kwonlyargs, a.kw_defaults)
                    if d is not None)
    out = set()
    try:
        for call in calls:
            at = plain.index(name) if name in plain else None
            if at is not None and isinstance(call.func, ast.Attribute) \
                    and isinstance(parents.get(function), ast.ClassDef):
                at -= 1
            by_word = [k.value for k in call.keywords if k.arg == name]
            if at is not None and any(isinstance(x, ast.Starred)
                                      for x in call.args[:at + 1]):
                out.add(("?a starred argument to %s()" % function.name,))
            elif at is not None and 0 <= at < len(call.args):
                out |= trace(call.args[at])
            elif by_word:
                out |= trace(by_word[0])
            elif any(k.arg is None for k in call.keywords):
                out.add(("?a ** argument to %s()" % function.name,))
            elif name in defaults:
                out |= trace(defaults[name])
            else:
                out.add(("?parameter %s of %s(), not passed"
                         % (name, function.name),))
        return out
    finally:
        tracing.discard(key)


def text_path(path):
    """A path that ends in text read out of a named table."""
    return path[0] in TABLES and all(
        s in ("[*]", ".key") or re.match(r"\[-?\d+\]$", s) for s in path[1:])


def calls_in(piece, tree):
    """Every T()/TN() call as (function it stands in, call)."""
    found = []

    def walk(node, where):
        for child in ast.iter_child_nodes(node):
            inside = where
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef,
                                  ast.ClassDef)):
                inside = where + [child.name]
            if isinstance(child, ast.Call) and sayer(child):
                found.append((".".join(where) or "<module>", child))
            walk(child, inside)
    walk(tree, [])
    return found


# Where each named table stands: the one literal its piece binds it to.
table_literal = {}
for table in sorted(TABLES):
    for node in (trees[TABLES[table]].body if TABLES[table] in trees else []):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == table
                for t in node.targets):
            table_literal.setdefault(table, node.value)

untraced = []
texts_fed = 0
calls_fed = 0
reached = set()
for piece in sorted(trees):
    for function, node in calls_in(piece, trees[piece]):
        fed_here = False
        for arg in text_args(node):
            if arg is not None and literal(arg):
                continue
            fed_here = True
            texts_fed += 1
            paths = (trace(arg) if arg is not None
                     else {("?an argument that cannot be told",)})
            for path in sorted(paths):
                if path[0][0] == "=" and len(path) == 1:
                    # A fallback written into the argument is said as
                    # well: T(TRC_NAMES.get(trc, 'unknown')) says it.
                    # The plural wordings TN() hands its own T() stay
                    # left aside, as in section 1.
                    if path[0][1:] not in second:
                        said.add(path[0][1:])
                elif text_path(path):
                    reached.add(path)
                else:
                    untraced.append("%s %s() line %d: %s(%s) <- %s"
                                    % (piece, function, node.lineno,
                                       sayer(node),
                                       ast.unparse(arg)[:40]
                                       if arg is not None else "?",
                                       render(path)))
        calls_fed += fed_here
for name in ("T", "TN"):
    for piece, node, how in handed.get(name, []):
        untraced.append("%s line %d: %s %s" % (piece, node.lineno, name, how))
check("every variable handed T() traces to a text of a named table",
      not untraced,
      "%d texts in %d calls reach T() as no literal, %d not traced: %s"
      % (texts_fed, calls_fed, len(untraced), untraced[:3] or "none"))

# Anything that changes a named table after its literal: a text put in
# at run time is exactly what a reading of the literal cannot see.
CHANGES = {"update", "setdefault", "append", "extend", "insert", "add",
           "pop", "popitem", "clear", "remove", "discard", "__setitem__",
           "__delitem__", "__ior__", "__iadd__"}
# The same changes called unbound, with the table as the first argument:
# dict.update(TABLE, ...), operator.setitem(TABLE, ...).
UNBOUND = {"dict", "list", "set", "operator"}
FREE = {"setitem", "delitem", "iadd", "ior", "iconcat"}


def table_under(node):
    """The named table *node* reaches, through any lookups, and whether
    it had to look anything up to get there."""
    looked = False
    while isinstance(node, ast.Subscript):
        node, looked = node.value, True
    name = (node.id if isinstance(node, ast.Name)
            else node.attr if isinstance(node, ast.Attribute) else None)
    return (name if name in TABLES else None), looked


written_into = []
for piece in sorted(trees):
    for node in ast.walk(trees[piece]):
        # A copy: taking the tree's own list apart would empty it.
        targets = (list(node.targets)
                   if isinstance(node, (ast.Assign, ast.Delete))
                   else [node.target] if isinstance(
                       node, (ast.AugAssign, ast.AnnAssign)) else [])
        flat = []
        while targets:
            t = targets.pop()
            if isinstance(t, (ast.Tuple, ast.List)):
                targets.extend(t.elts)
            else:
                flat.append(t.value if isinstance(t, ast.Starred) else t)
        for t in flat:
            table, looked = table_under(t)
            if table is None:
                continue
            value = getattr(node, "value", None)
            if not looked and isinstance(node, ast.Assign) and isinstance(
                    t, ast.Name) and (value is table_literal.get(table) or (
                        isinstance(value, ast.Attribute)
                        and value.attr == table)):
                continue
            written_into.append("%s line %d: %s" % (
                piece, node.lineno, ast.unparse(node)[:50]))
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        bound_form = isinstance(f, ast.Attribute) and f.attr in CHANGES \
            and table_under(f.value)[0]
        unbound = node.args and table_under(node.args[0])[0] and (
            isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name)
            and f.value.id in UNBOUND and f.attr in CHANGES | FREE
            or isinstance(f, ast.Name) and f.id in FREE)
        if bound_form or unbound:
            written_into.append("%s line %d: %s" % (
                piece, node.lineno, ast.unparse(node)[:50]))


def cells(node, steps):
    """The nodes a path's steps lead to inside a table's literal."""
    out = [node]
    for s in steps:
        nxt = []
        for n in out:
            if s == "[*]" and isinstance(n, ast.Dict):
                nxt += n.values
            elif s == "[*]" and isinstance(n, (ast.Tuple, ast.List, ast.Set)):
                nxt += n.elts
            elif s == ".key" and isinstance(n, ast.Dict):
                nxt += [k if k is not None else v
                        for k, v in zip(n.keys, n.values)]
            elif s[0] == "[" and s != "[*]" \
                    and isinstance(n, (ast.Tuple, ast.List)) \
                    and -len(n.elts) <= int(s[1:-1]) < len(n.elts):
                nxt.append(n.elts[int(s[1:-1])])
            elif s[0] == "[" and s != "[*]" and isinstance(n, ast.Dict) \
                    and [k for k in n.keys if isinstance(k, ast.Constant)
                         and k.value == int(s[1:-1])]:
                nxt += [v for k, v in zip(n.keys, n.values)
                        if isinstance(k, ast.Constant)
                        and k.value == int(s[1:-1])]
            else:
                nxt.append(n)
        out = nxt
    return out


missing = sorted("%s in %s" % (t, TABLES[t]) for t in TABLES
                 if t not in table_literal)
unwritten = []
from_paths = {}
for path in sorted(reached):
    if path[0] not in table_literal:
        continue
    for cell in cells(table_literal[path[0]], path[1:]):
        if literal(cell):
            from_paths.setdefault(path, set()).add(cell.value)
        else:
            unwritten.append("%s line %d: %s"
                             % ("".join(path), cell.lineno,
                                ast.unparse(cell)[:30]))
check("every named table is one literal, its texts written out",
      not missing and not unwritten and not written_into,
      "%d tables, %d texts read; not found: %s; not a literal: %s;"
      " written into: %s"
      % (len(TABLES), sum(len(v) for v in from_paths.values()),
         missing[:3] or "none", unwritten[:2] or "none",
         written_into[:2] or "none"))
# Only what a call still reads: a table nothing hands to T() any more is
# not said, and holding a catalogue to it would ask for dead weight.
through = set()
for texts in from_paths.values():
    through |= texts
before = len(said)
said |= through - KEPT_ENGLISH
print("      %d texts reach T() through a table and not as a literal,"
      " %d kept English" % (len(said) - before,
                            len(through & KEPT_ENGLISH)))

print("\n1c. A fallback stays inside its table")
# `SHOT_NAMES.get(name, name)` hands T() the stored name itself when the
# table has no entry for it -- a word like "hold-brief", in no catalogue
# and in no language. The trace above cannot hold that word to anything,
# so this asks the other way round: every key such a lookup can be
# handed stands in its table, and the fallback is never taken. Asked of
# the loaded program, because the keys are names like SHOT_WIDE whose
# value only the program knows.


def loaded(piece):
    """The loaded module a piece became."""
    want = os.path.realpath(os.path.join(HOME, piece))
    for m in [vpm] + [v for v in vars(vpm).values()
                      if isinstance(v, type(sys))]:
        if os.path.realpath(getattr(m, "__file__", None) or "") == want:
            return m
    return None


def values_at(path):
    """What stands at *path* in the loaded program, or None."""
    if path[0][0] == "=" and len(path) == 1:
        return [path[0][1:]]
    if path[0] not in TABLES or loaded(TABLES[path[0]]) is None:
        return None
    out = [getattr(loaded(TABLES[path[0]]), path[0], None)]
    try:
        for s in path[1:]:
            if s == "[*]":
                out = [v for o in out for v in (
                    o.values() if isinstance(o, dict) else o)]
            elif s == ".key":
                out = [v for o in out for v in o.keys()]
            elif re.match(r"\[-?\d+\]$", s):
                out = [o[int(s[1:-1])] for o in out]
            else:
                return None
    except (AttributeError, TypeError, IndexError, KeyError):
        return None
    return out


outside = []
looked_up = 0
for call in fallbacks:
    at = scopes_of(call)
    where = "%s line %d: %s" % (piece_of[at[-1]], call.lineno,
                                ast.unparse(call)[:40])
    found = [values_at(p) for p in sorted(trace(call.func.value))]
    tables = [t for f in found if f is not None for t in f]
    for key in sorted(trace(call.args[0])):
        keys = values_at(key)
        if keys is None or None in found or not tables \
                or not all(isinstance(t, dict) for t in tables):
            outside.append("%s, keys from %s cannot be looked up"
                           % (where, render(key)))
            continue
        for k in keys:
            looked_up += 1
            if not all(k in t for t in tables):
                outside.append("%s, %s holds %r, not in the table"
                               % (where, render(key), k))
check("a fallback never hands T() a value from outside its table",
      not outside,
      "%d fallbacks, %d keys looked up; outside: %s"
      % (len(fallbacks), looked_up, outside[:2] or "none"))

print("\n2. No catalogue carries an empty translation")
# An empty msgstr used to be kept, and T() handed back the empty string
# -- the label vanished instead of staying English. read_po leaves it
# out now, so an empty entry is dead weight rather than damage; it is
# still a fault, because somebody wrote a key and no answer.
blank = []
for code, path in CATALOGUES:
    for key, value, at in the_program.po_pairs(path):
        if key and not value:
            blank.append("%s:%d" % (code, at))
check("no shipped catalogue carries an empty translation",
      not blank,
      "%d empty of %d catalogues: %s"
      % (len(blank), len(CATALOGUES), blank[:4] or "none"))

print("\n3. What a language answers may only grow")
# Counted as what it answers, not as what it lacks. The gap grows when
# the program does, through no fault of the language: measured, one
# sentence added to the program reddened eleven of twelve at once, and
# a check that reddens eleven languages because somebody wrote a
# sentence gets worked around instead of followed.
answered = {}
for code, path in CATALOGUES:
    has = set(the_program.po_texts(path))
    answered[code] = len([w for w in said if w in has])
# One check over all of them, not one per language: a check whose name
# is computed carries one wording for every language, and the
# register cannot then say which of them was ever seen red.
worse = []
for code in sorted(answered):
    floor = state.rising("answers_" + code, answered[code])
    if answered[code] > floor:
        print("      ratchet raised: %d -> %d" % (floor, answered[code]))
    if answered[code] < floor:
        worse.append("%s %d against %d" % (code, answered[code], floor))
check("no language answers fewer of the program's texts than before",
      not worse,
      "%d of %d languages fell back: %s"
      % (len(worse), len(answered), worse[:4] or "none"))

print("\n3b. Every catalogue answers all of it")
# The floor above cannot see this: a language keeps answering just as
# many while the program says one more, and nothing moves. So every
# catalogue on disk is held to everything. A half-finished .po then
# turns the suite red instead of merely raising its floor, and that is
# wanted: every language answers every text today, and one that falls
# behind is a fault, not a language on its way.
short = []
for code, path in CATALOGUES:
    has = set(the_program.po_texts(path))
    missing = [w for w in said if w not in has]
    if missing:
        short.append("%s misses %d, first %r"
                     % (code, len(missing), missing[0][:40]))
check("every catalogue answers all of the program's texts",
      not short,
      "%d of %d catalogues fell short: %s"
      % (len(short), len(CATALOGUES), short[:2] or "none"))

print("\n4. The list of languages and the catalogues on disk agree")
# Not "is every catalogue held to a number": the ratchet adopts a new
# key the first time it sees it, so that judgement is true by
# construction and can never fall. This one can: a language offered
# without a catalogue answers English under its own name, and a
# catalogue nobody offers is never read.
offered = set(vpm.language.LANGUAGE_NAMES) - {"en"}
on_disk = set(code for code, _p in CATALOGUES)
check("every language the window offers has a catalogue on disk",
      not (offered - on_disk),
      "%d offered, %d on disk, without a catalogue: %s"
      % (len(offered), len(on_disk), sorted(offered - on_disk) or "none"))
check("and no catalogue lies there that the window never offers",
      not (on_disk - offered),
      "%d on disk, %d offered, never offered: %s"
      % (len(on_disk), len(offered), sorted(on_disk - offered) or "none"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
