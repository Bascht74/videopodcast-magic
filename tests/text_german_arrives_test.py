# -*- coding: utf-8 -*-
"""The German texts are a file of their own, and every way in brings them.

The file beside the program holds the texts and the program holds none;
nothing was lost in the move. Then the three ways the program is
reached -- started by its path, read from an absolute path the way the
tests do, imported by name from a folder on the search path -- each has
to come up German, and the list pip installs by has to carry both
files. Last the order: the language is settled only once the texts
stand, so a machine set to German comes up German.
"""
import ast
import glob
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile
import time

began = time.time()
# the_program.py is deliberately not used here: what this test measures
# is how the program is reached, and a helper that does the reaching
# would be the thing under test rather than the thing testing.
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    ROOT, "videopodcast_magic.py")
# The program reads its texts from beside itself, so this test looks in
# the same place: against a snapshot that is the snapshot's own texts.
TEXTS_DE = os.path.join(os.path.dirname(SCRIPT),
                        "videopodcast_magic_texts_de.py")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# What the catalogue held on the day it moved out of the program. A
# floor, not a count: texts are added as the program grows, and only
# losing one is a fault.
ENTRIES = 1498
# The wording the three ways below are read by. Its German stands in
# the catalogue, so a retranslation moves the expectation with it.
COMPLAINT = "Not found: %s"

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def texts_of(path):
    """The dictionary a texts file holds, read without running it."""
    for node in ast.parse(io.open(path, encoding="utf-8").read()).body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
            return ast.literal_eval(node.value)
    return {}


# ---------------------------------------------------------- one file
print("1. The texts stand in a file of their own")
there = os.path.exists(TEXTS_DE)
check("the German texts are a file beside the program", there,
      "%s beside %s: %s" % (os.path.basename(TEXTS_DE),
                            os.path.basename(SCRIPT),
                            "there" if there else "not there"))
catalogue = texts_of(TEXTS_DE) if there else {}
source = io.open(SCRIPT, encoding="utf-8").read()
program = ast.parse(source)
# The shape that moved out: a dictionary written straight into
# CATALOGUE. One of those in the program means the texts are back.
back = [n.lineno for n in ast.walk(program)
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Dict)
        and isinstance(n.targets[0], ast.Subscript)
        and getattr(n.targets[0].value, "id", "") == "CATALOGUE"]
check("the program itself carries no catalogue of texts", not back,
      "%d dictionaries are written into CATALOGUE, on line(s) %s, wanted 0"
      % (len(back), back or "none"))
check("nothing was lost on the way out of the program",
      len(catalogue) >= ENTRIES,
      "%d entries in %s, wanted %d or more"
      % (len(catalogue), os.path.basename(TEXTS_DE), ENTRIES))
wanted = catalogue.get(COMPLAINT, "").split("%s")[0]
# The three ways below read the run for this German wording. Without
# it they would look for the empty string and find it every time.
check("the wording the three ways are read by is translated",
      len(wanted) > 4,
      "%r translates to %r, wanted a German wording" % (COMPLAINT, wanted))

# ------------------------------------------------------- the three ways
print("\n2. Every way into the program comes up German")
work = tempfile.mkdtemp()
absent = os.path.join(work, "no-such-recording.wav")
ARGS = ["--lang", "de", absent, "--dry-run", "--no-preflight", "--no-metrics"]
# Both channels: the complaint about a missing file goes to stderr.
ran = subprocess.run([sys.executable, SCRIPT] + ARGS,
                     capture_output=True, text=True, timeout=300,
                     env=dict(os.environ, LANG="C", LC_ALL="C"))
said = ran.stdout + ran.stderr
check("started by its path, the program speaks German",
      bool(wanted) and wanted in said,
      "%d characters back, %r among them: %s"
      % (len(said), wanted, "yes" if wanted and wanted in said else "no"))

# The way every test loads the program. Python puts the folder of a
# file loaded by its path on no search path, so this is the way that
# breaks first when the texts are looked for by an import.
check("the folder the program lies in is not on the search path",
      os.path.dirname(SCRIPT) not in sys.path,
      "sys.path holds %d entries, that folder among them: %s"
      % (len(sys.path),
         "yes" if os.path.dirname(SCRIPT) in sys.path else "no"))
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
try:
    spec.loader.exec_module(vpm)
    vpm.set_language("de")
    got = vpm.T(COMPLAINT, absent)
except Exception as why:
    # A program that cannot find its texts does not load at all. That
    # is the answer to this check, not a reason to end in a traceback
    # and leave the six judgements below unasked.
    got = "%s: %s" % (type(why).__name__, why)
check("read from an absolute path, the program speaks German",
      bool(wanted) and got.startswith(wanted),
      "T(%r) begins %r, wanted %r"
      % (COMPLAINT, got[:len(wanted) or 16], wanted))

# The shape an installation has: every file of the program in one
# folder, and the folder on the search path. A copy, so nothing is
# imported twice here. What travels is named by its shape and never one
# by one: a list would be right today and wrong the day a language is
# added, and pip installs by shape too.
installed = os.path.join(work, "site")
os.makedirs(installed)
shutil.copy(SCRIPT, os.path.join(installed, "videopodcast_magic.py"))
for near in sorted(glob.glob(os.path.join(os.path.dirname(SCRIPT),
                                          "videopodcast_magic*.py"))):
    if not os.path.samefile(near, SCRIPT):
        shutil.copy(near, installed)
BY_NAME = ("import videopodcast_magic as v\n"
           "v.set_language('de')\n"
           "print(len(v.CATALOGUE['de']))\n"
           "print(v.T(%r, 'x'))\n" % COMPLAINT)
byname = subprocess.run([sys.executable, "-c", BY_NAME], cwd=work,
                        capture_output=True, text=True, timeout=300,
                        env=dict(os.environ, PYTHONPATH=installed,
                                 LANG="C", LC_ALL="C"))
# Only what the run printed itself: a traceback would carry the whole
# path of this machine into a line that gets written down.
check("imported by name, the program speaks German",
      bool(wanted) and wanted in byname.stdout,
      "the run said %r and went out with %d"
      % (byname.stdout.strip()[:40] or "nothing", byname.returncode))

# What makes that third way true of a real installation. setuptools
# takes a list of names and no pattern, so the list is held against the
# program instead of against a name written down here: every language
# the program takes in has to be on it, or an installed copy asks for a
# file pip never brought and does not start.
needed = ["videopodcast_magic"]
for node in ast.walk(program):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
            and node.func.id == "texts_of_language" and node.args \
            and isinstance(node.args[0], ast.Constant):
        needed.append("videopodcast_magic_texts_" + node.args[0].value)
POM = os.path.join(ROOT, "pyproject.toml")
# From the key to the closing bracket, not the first line: the list grew
# past what fits on one, and reading only the first would have called
# every name below it missing.
whole = io.open(POM, encoding="utf-8").read()
row = ""
if "py-modules" in whole:
    rest = whole.split("py-modules", 1)[1]
    row = rest.split("]", 1)[0] if "]" in rest else rest
short = [name for name in needed if '"%s"' % name not in row]
check("pip is told to install every file the program loads", not short,
      "%d of the %d files the program loads are not in py-modules: %s"
      % (len(short), len(needed), short or "none"))

# -------------------------------------------------------------- the order
print("\n3. The language is settled after the texts stand")
last = {}
for node in program.body:
    if not isinstance(node, ast.Assign):
        continue
    aim = node.targets[0]
    if isinstance(aim, ast.Subscript) \
            and getattr(aim.value, "id", "") == "CATALOGUE":
        last["texts"] = node.lineno
    if isinstance(aim, ast.Name) and aim.id == "LANG":
        last["lang"] = node.lineno
check("the texts are taken in before the language is settled",
      last.get("texts", 0) and last.get("texts", 0) < last.get("lang", 0),
      "the last CATALOGUE line is %s, the last LANG line %s"
      % (last.get("texts"), last.get("lang")))
# And what that order is for: LANG is settled out of languages(), which
# reads the catalogue. Settled too early it can only ever say English.
READ_BACK = ("import importlib.util, sys\n"
             "s = importlib.util.spec_from_file_location('vpm', %r)\n"
             "m = importlib.util.module_from_spec(s)\n"
             "s.loader.exec_module(m)\n"
             "print(m.LANG)\n" % SCRIPT)
german_machine = subprocess.run(
    [sys.executable, "-c", READ_BACK], cwd=work, capture_output=True,
    text=True, timeout=300,
    env=dict(os.environ, LANGUAGE="de", LANG="de_DE.UTF-8",
             LC_ALL="de_DE.UTF-8"))
check("a machine set to German comes up German",
      german_machine.stdout.strip() == "de",
      "the program came up in %r and went out with %d, wanted 'de'"
      % (german_machine.stdout.strip() or "nothing",
         german_machine.returncode))

shutil.rmtree(work, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
