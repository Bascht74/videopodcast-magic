# -*- coding: utf-8 -*-
"""A switch that is taken and does nothing is worse than no switch.

Three of them once stood in the help: accepted, never read, the user
believing they had an effect. Every other test asks whether what was
wanted happens; none asks whether what is offered still does anything.
The second question is the same one a step further out -- the mark
"[multitrack only]" was set once and printed to nobody, because --help
builds a parser of its own and never reached the place it was set in.
"""
import ast
import os
import re
import subprocess
import sys
import time
import the_program

began = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT = the_program.SCRIPT

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

print("\n2. The mark stands in the printed help")
MARK = "[multitrack only]"
# Printed, not formatted here. --help takes a way of its own through
# main(), and the whole point of the check is that the mark survives it.
help_run = subprocess.run([sys.executable, SCRIPT, "--help"],
                          capture_output=True, text=True)
help_text = (help_run.stdout or "") + (help_run.stderr or "")
check("--help answers at all", help_run.returncode == 0 and len(help_text) > 500,
      "rc=%d, %d characters" % (help_run.returncode, len(help_text)))

# One block per switch: a line beginning at column three with a dash
# opens it, everything indented further belongs to it. Folded into one
# line, because argparse wraps and the mark may sit across a break.
HEAD = re.compile(r"^ {2}(-\S+)")
blocks = {}
current = None
for line in help_text.splitlines():
    opening = HEAD.match(line)
    if opening:
        current = opening.group(1).rstrip(",")
        blocks[current] = line
    elif current and line.startswith("    "):
        blocks[current] += " " + line.strip()
    elif not line.strip():
        current = None
check("--help lists the switches one by one", len(blocks) > 20,
      "%d blocks" % len(blocks))

printed = {}
for entry in switches:
    said = [blocks[name] for name in entry.option_strings if name in blocks]
    if said:
        printed[entry.dest] = MARK in " ".join(said[0].split())
should = list(vpm.ONLY_MULTITRACK)
check("the program knows which switches need several recordings",
      len(should) > 0, "%d" % len(should))
found("every one of them carries %s in --help" % MARK,
      [dest for dest in should if not printed.get(dest)])
found("and no switch that does not need it carries %s" % MARK,
      [dest for dest, has in sorted(printed.items())
       if has and dest not in should])

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
