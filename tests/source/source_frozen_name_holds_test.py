# -*- coding: utf-8 -*-
"""Users' keys, logs and choices stay under the name they were filed under.

In order: the frozen values against today's, written out; the folders
the program answers with; every place that files something reads the
frozen name; the name is written out nowhere else; and the command pip
lays is the program's name. The limits: the folders are asked under the
VPM_ variables, so the leaf is held and not each system's base; and a
place reaching the program's name through an alias such as COMMAND is
not seen.
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
import io
import shutil
import tempfile
import time

import the_program

began = time.time()
vpm = the_program.load()
vpm.set_language("en")
desktop = vpm.beside("desktop", program=vpm.PROGRAM)
# The pyproject is the repository's: a snapshot under VPM_SCRIPT has none.
POM = os.path.join(the_program.ROOT, "pyproject.toml")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def tree_of(piece):
    """The parsed source of one piece, "" being the way in."""
    path = os.path.join(the_program.FOLDER, piece, "__init__.py")
    with io.open(path, encoding="utf-8") as f:
        return ast.parse(f.read())


def definition(tree, name):
    """The top-level def or assignment of that name, or None."""
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == name
                for t in node.targets):
            return node
    return None


print("1. The frozen values are today's")
check("the frozen name is the one users' things are filed under",
      vpm.FROZEN_NAME == "videopodcast-magic",
      "FROZEN_NAME is %r, wanted 'videopodcast-magic'" % (vpm.FROZEN_NAME,))
check("the keychain and the registry are asked under today's names",
      vpm.KEY_STORE_REAL == ("videopodcast-magic", "auphonic",
                             "Software\\videopodcast-magic"),
      "KEY_STORE_REAL is %r" % (vpm.KEY_STORE_REAL,))
check("a project file still begins with today's prefix",
      vpm.PROJECT_PREFIX == "videopodcast-magic_",
      "PROJECT_PREFIX is %r, wanted 'videopodcast-magic_'"
      % (vpm.PROJECT_PREFIX,))
check("the macOS bundle keeps today's identifier",
      desktop.IDENTIFIER == "com.github.bascht74.videopodcast-magic",
      "IDENTIFIER is %r" % (desktop.IDENTIFIER,))
check("a launcher of ours is still told by today's line",
      desktop.WRITTEN_BY == "# Written by videopodcast-magic.",
      "WRITTEN_BY is %r" % (desktop.WRITTEN_BY,))

print("\n2. The folders the program answers with")
base = tempfile.mkdtemp()
kept = dict((k, os.environ.get(k)) for k in
            ("VPM_LOGS", "VPM_SETTINGS", "VPM_CACHE", "VPM_TOOLS"))
try:
    for k in kept:
        os.environ[k] = base
    got = [vpm.log_folder(), vpm.settings_folder(), vpm.cache_folder(""),
           vpm.tools_folder(), os.path.basename(vpm.log_path() or "")]
finally:
    for k, v in kept.items():
        os.environ.pop(k, None) if v is None else os.environ.update({k: v})
    shutil.rmtree(base, ignore_errors=True)
wanted = [os.path.join(base, "videopodcast-magic"),
          os.path.join(base, "videopodcast-magic"),
          os.path.join(base, "videopodcast-magic", ""),
          os.path.join(base, "videopodcast-magic", "tools"),
          "videopodcast-magic.log"]
check("log, settings, cache and tools lie in today's folders",
      got == wanted,
      "log, settings, cache, tools, log file: %s, wanted %s"
      % ([str(g).replace(base, "<base>") for g in got],
         [w.replace(base, "<base>") for w in wanted]))

print("\n3. Every place that files a user's things reads the frozen name")
PLACES = (("logbook", "log_folder"), ("logbook", "log_path"),
          ("stowage", "cache_folder"), ("stowage", "settings_folder"),
          ("setup", "tools_folder"), ("setup", "KEY_STORE_REAL"),
          ("", "PROJECT_PREFIX"), ("desktop", "IDENTIFIER"),
          ("desktop", "WRITTEN_BY"), ("desktop", "_link"))
astray = []
for piece, name in PLACES:
    node = definition(tree_of(piece), name)
    reads = node is not None and any(
        isinstance(n, ast.Name) and n.id == "FROZEN_NAME"
        for n in ast.walk(node))
    spelled = node is not None and any(
        isinstance(n, ast.Constant) and isinstance(n.value, str)
        and "videopodcast" in n.value for n in ast.walk(node))
    # The program's name, read beside the frozen one, follows a rename.
    follows = node is not None and any(
        getattr(n, "id", getattr(n, "attr", "")) == "PROGRAM_NAME"
        for n in ast.walk(node))
    if not reads or spelled or follows:
        astray.append("%s/%s%s" % (
            piece or "__init__", name,
            " spells the name out" if spelled
            else " reads PROGRAM_NAME" if follows
            else " does not read FROZEN_NAME"))
check("every place that files a user's things reads the frozen name",
      not astray, "%d of %d places astray: %s"
      % (len(astray), len(PLACES), "; ".join(astray)))

print("\n4. The name is written out in one place only")
# Allowed beside the two definitions: a docstring, a text through T(),
# which the catalogue keys, and the repository's address.
loose = []
for folder, _dirs, files in os.walk(the_program.FOLDER):
    for leaf in files:
        if not leaf.endswith(".py"):
            continue
        path = os.path.join(folder, leaf)
        with io.open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read())
        spared = set()
        for n in ast.walk(tree):
            body = getattr(n, "body", None)
            if isinstance(body, list) and body \
                    and isinstance(body[0], ast.Expr) \
                    and isinstance(body[0].value, ast.Constant):
                spared.add(id(body[0].value))
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                    and n.func.id in ("T", "TN"):
                spared.update(id(a) for a in ast.walk(n))
            if isinstance(n, ast.Assign) and any(
                    isinstance(t, ast.Name)
                    and t.id in ("PROGRAM_NAME", "FROZEN_NAME")
                    for t in n.targets):
                spared.add(id(n.value))
        for n in ast.walk(tree):
            if isinstance(n, ast.Constant) and isinstance(n.value, str) \
                    and "videopodcast-magic" in n.value \
                    and "Bascht74/videopodcast-magic" not in n.value \
                    and id(n) not in spared:
                loose.append("%s:%d %r" % (
                    os.path.relpath(path, the_program.FOLDER), n.lineno,
                    n.value[:40]))
check("the name is spelled out only where the two names are set",
      not loose, "%d loose: %s" % (len(loose), "; ".join(loose[:6])))

print("\n5. The command pip lays")
laid = []
section = ""
for line in io.open(POM, encoding="utf-8"):
    line = line.split("#", 1)[0].strip()
    if line.startswith("["):
        section = line
    elif section in ("[project.scripts]", "[project.gui-scripts]") \
            and "=" in line:
        laid.append(line.split("=", 1)[0].strip().strip('"'))
check("the command pip lays is the program's name",
      laid == [vpm.PROGRAM_NAME],
      "pyproject.toml lays %s, the program calls itself %r"
      % (laid, vpm.PROGRAM_NAME))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
