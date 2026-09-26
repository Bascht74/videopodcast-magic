# -*- coding: utf-8 -*-
"""Every test says whether its verdict can differ between systems.

A test with PLATFORM_BOUND = True runs on the six system jobs, one with
False once, on the neutral job; run.sh and tests.yml pick it by that
line alone, so a missing or misspelt line takes it out of both halves.
In order: every test carries the line exactly once, spelt as run.sh's
grep reads it; a test declared neutral starts no process, opens no
window and asks no platform; no test set aside on a system in tests.yml
is declared neutral.
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
import re
import time

began = time.time()
ROOT = os.path.dirname(HERE)
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "tests.yml")
# What makes a test's verdict hang on the machine: a process, a window,
# the platform asked by name, a lock, the network -- or a helper of the
# suite that does one of those. the_program, overview and ratchet only
# load the program or read the repository, and stay allowed.
BOUND_MODULES = {
    "subprocess", "multiprocessing", "asyncio", "signal", "PySide6",
    "ctypes", "msvcrt", "fcntl", "winreg", "platform", "socket",
    "urllib", "http", "captions_measure", "fixture_project",
    "interview_project", "fixture_root", "local_ground", "let_go",
    "key_store_apart", "audio_chain", "assignment_shot", "carry_shot",
    "language_shot", "preset_shot", "preview_shot", "reading_shot"}
BOUND_NAMES = {("sys", "platform"), ("os", "name"), ("os", "system"),
               ("os", "startfile")}

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def tests():
    """Every test run.sh would run: tests/ and one folder down, so not live/."""
    found = {}
    for place in [""] + sorted(os.listdir(HERE)):
        folder = os.path.join(HERE, place)
        if not os.path.isdir(folder):
            continue
        for name in sorted(os.listdir(folder)):
            if name.endswith("_test.py"):
                found[name[:-len("_test.py")]] = os.path.join(folder, name)
    return found


def reaches(source):
    """What in this source makes a verdict hang on the machine, by name."""
    seen = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            seen.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            seen.add(node.module.split(".")[0])
        elif isinstance(node, ast.Attribute) \
                and isinstance(node.value, ast.Name) \
                and (node.value.id, node.attr) in BOUND_NAMES:
            seen.add("%s.%s" % (node.value.id, node.attr))
    return sorted(seen & BOUND_MODULES
                  | {s for s in seen if "." in s})


ALL = tests()
print("1. Every test carries the line, once, as run.sh reads it")
said, wrong = {}, []
for name, path in sorted(ALL.items()):
    lines = io.open(path, encoding="utf-8").read().splitlines()
    marks = [l for l in lines if l.startswith("PLATFORM_BOUND")]
    if len(marks) == 1 and marks[0] in ("PLATFORM_BOUND = True",
                                         "PLATFORM_BOUND = False"):
        said[name] = marks[0].endswith("True")
    else:
        wrong.append("%s %s" % (name, marks or "none"))
check("the tests are found at all", len(ALL) > 100,
      "%d test files under tests/" % len(ALL))
check("every test says PLATFORM_BOUND = True or False, exactly once",
      not wrong, "%d of %d: %s" % (len(wrong), len(ALL), "; ".join(wrong[:6])))

print("\n2. A test declared neutral asks nothing of the machine")
neutral = sorted(n for n, b in said.items() if not b)
leaning = []
for name in neutral:
    hits = reaches(io.open(ALL[name], encoding="utf-8").read())
    if hits:
        leaning.append("%s: %s" % (name, ", ".join(hits)))
check("a neutral test starts no process, window or platform question",
      not leaning, "%d of %d neutral: %s"
      % (len(leaning), len(neutral), "; ".join(leaning[:6])))

print("\n3. What a system sets aside is bound")
workflow = io.open(WORKFLOW, encoding="utf-8").read()
aside = sorted(set(re.findall(r"^\s*aside ([a-z0-9_]+)", workflow, re.M)))
check("the set-aside names in tests.yml are read at all", len(aside) > 0,
      "%d names in .github/workflows/tests.yml" % len(aside))
loose = [n for n in aside if said.get(n) is False]
check("no test set aside on a system is declared neutral", not loose,
      "%d of %d set aside: %s" % (len(loose), len(aside), ", ".join(loose)))
print("\n%d bound, %d neutral" % (len(said) - len(neutral), len(neutral)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
