# -*- coding: utf-8 -*-
"""A switch that is taken and does nothing is worse than no switch.

Three of them once stood in the help: accepted, never read, the user
believing they had an effect. Every other test asks whether what was
wanted happens; none asks whether what is offered still does anything.
Last, a switch retired is gone and not kept on without effect:
--multitrack is refused as any word the parser does not know.
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
import ast
import contextlib
import io
import time
import the_program

began = time.time()

vpm = the_program.load()

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def found(what, complaints):
    """Green when the list is empty, and the names go into the FAIL line.

    Not underneath it: on another machine only the line carrying the
    word FAIL is kept, and a list on the lines below is thrown away.
    """
    check(what, not complaints, ", ".join(complaints))


parser = vpm.build_argument_parser()
# -h and --version carry a dest argparse invented for them; nothing in
# the program reads either, because argparse answers both itself and
# leaves before the run begins.
ANSWERED_BY_ARGPARSE = ("help", "version")
switches = [entry for entry in parser._actions
            if entry.dest not in ANSWERED_BY_ARGPARSE]
dests = set(entry.dest for entry in switches)

print("1. Every switch is read somewhere")
check("build_argument_parser hands out its switches",
      len(switches) > 20, "%d" % len(switches))

# Every piece of the program: a switch whose only reader sits in the
# window would otherwise be reported as taken and never read.
TREES = [ast.parse(body) for _piece, body in the_program.pieces()]
defined_in = [node for tree in TREES for node in ast.walk(tree)
              if isinstance(node, ast.FunctionDef)
              and node.name == "build_argument_parser"]
check("build_argument_parser found in the source", len(defined_in) == 1,
      "%d of that name" % len(defined_in))
# The parser is the definition, not a reader: every dest stands in it
# once by construction, so everything inside it is left out.
parser_nodes = set(map(id, ast.walk(defined_in[0]))) if defined_in else set()

# The two ways the program reads a setting by name. "args" is what the
# namespace is called everywhere; a parse_args() asked straight out is
# the one other holder, and getattr covers the loops that build the
# field name rather than writing it down.
NAMESPACE = ("args", "a", "ns", "opts", "options", "parsed")
read_by_name = set()
keys = set()
compared = set()
for tree in TREES:
    for node in ast.walk(tree):
        if id(node) in parser_nodes:
            continue
        if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load):
            holder = node.value
            if (isinstance(holder, ast.Name) and holder.id in NAMESPACE) or (
                    isinstance(holder, ast.Call)
                    and isinstance(holder.func, ast.Attribute)
                    and holder.func.attr.startswith("parse_")):
                read_by_name.add(node.attr)
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in ("getattr", "hasattr")
                and len(node.args) >= 2
                and isinstance(node.args[1], ast.Constant)):
            read_by_name.add(node.args[1].value)
        if isinstance(node, ast.Dict):
            keys.update(k.value for k in node.keys
                        if isinstance(k, ast.Constant) and isinstance(k.value, str))
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
            keys.add(node.slice.value)
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("get", "setdefault", "pop")
                and node.args and isinstance(node.args[0], ast.Constant)):
            keys.add(node.args[0].value)
        if isinstance(node, ast.Compare):
            for side in [node.left] + list(node.comparators):
                if isinstance(side, ast.Constant) and isinstance(side.value, str):
                    compared.add(side.value)

# The rest of the ways in, and they are real ones: the cut rules travel
# as dictionary keys, and --update-check is answered off sys.argv before
# a namespace exists. A name in a message does not count -- a key and a
# comparison do, and nothing else.
by_key = {}
for entry in switches:
    if entry.dest in read_by_name:
        continue
    spelt = [name for name in entry.option_strings if name in compared]
    if spelt:
        by_key[entry.dest] = "as %s" % spelt[0]
    elif entry.dest in keys:
        by_key[entry.dest] = "as a key"

found("all %d switches are read, none merely taken" % len(switches),
      ["/".join(entry.option_strings) or entry.dest for entry in switches
       if entry.dest not in read_by_name and entry.dest not in by_key])
print("     %d read off the namespace, %d by name: %s"
      % (len(dests & read_by_name), len(by_key),
         ", ".join("%s %s" % (k, v) for k, v in sorted(by_key.items()))))

print("\n2. A switch retired is refused, not kept on without effect")
# Whether the tracks go up as one Multitrack production follows from the
# material, so the switch that once said it is gone: the parser answers
# it as it answers any word it does not know, with its own complaint and
# a return of 2, before a run begins.
heard = io.StringIO()
try:
    with contextlib.redirect_stderr(heard):
        parser.parse_args(["--multitrack"])
    returned = None
except SystemExit as stop:
    returned = stop.code
complaint = (heard.getvalue().strip().splitlines() or [""])[-1]
check("--multitrack is refused as a word the parser does not know",
      returned == 2 and "--multitrack" in complaint,
      "parse_args returned %r against 2 and said %r"
      % (returned, complaint))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
