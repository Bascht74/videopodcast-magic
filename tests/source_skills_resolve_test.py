# -*- coding: utf-8 -*-
"""Every file, test and skill a skill names by name is really there.

The rules under .claude/skills/ are prose, and prose is where a rename
goes unnoticed: a test renamed in one commit left seven dead names
across the skills and shipped in a release, because nothing here read
them. Three sections: the paths a skill points at, the tests it names,
and the skills it sends the reader on to. What a skill says about the
program is not checked here -- only that what it names exists.
"""
import io
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKILLS = os.path.join(ROOT, ".claude", "skills")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def skills():
    """Every skill by name, with the text of its SKILL.md."""
    out = {}
    for name in sorted(os.listdir(SKILLS)):
        one = os.path.join(SKILLS, name, "SKILL.md")
        if os.path.isfile(one):
            out[name] = io.open(one, encoding="utf-8").read()
    return out


print("1. The skills are where they are looked for")
check("there is a skills folder", os.path.isdir(SKILLS), SKILLS)
if not os.path.isdir(SKILLS):
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad))
    sys.exit(1)

texts = skills()
check("every skill has a SKILL.md with a name and a description",
      all(re.search(r"^name:\s*\S", t, re.M)
          and re.search(r"^description:\s*\S", t, re.M)
          for t in texts.values()),
      "%d skills: %s" % (len(texts), ", ".join(sorted(texts))))

print("\n2. Every path a skill points at is there")
# Only what really looks like a path: a folder in front of it, or an
# ending this repository uses. `check(...)`, `abspath` and the like are
# backticked too and are not files.
LOOKS_LIKE = re.compile(
    r"`((?:tests|docs|development|\.github|\.claude)/[A-Za-z0-9_./-]+"
    r"|[A-Za-z][A-Za-z0-9_-]*\.(?:py|sh|md|json|yml))`")
missing = []
for name, text in sorted(texts.items()):
    for i, line in enumerate(text.splitlines(), 1):
        for hit in LOOKS_LIKE.findall(line):
            path = hit.rstrip(".")
            # A segment in capitals is a blank to fill in, not a file:
            # `docs/images/NAME.png` stands in a command as a pattern.
            if any(part.isupper() for part in re.split(r"[/.]", path)):
                continue
            if os.path.exists(os.path.join(ROOT, path)):
                continue
            # A bare file name may live in tests/ or beside the program.
            if "/" not in path and any(
                    os.path.exists(os.path.join(ROOT, d, path))
                    for d in ("", "tests", "docs", "development",
                              os.path.join("docs", "notes"))):
                continue
            missing.append("%s:%d %s" % (name, i, path))
check("every path a skill names resolves", not missing,
      "%d dead: %s" % (len(missing), "; ".join(missing[:4])))

print("\n3. Every test a skill names is there")
there = set(n[:-len("_test.py")] for n in os.listdir(HERE)
            if n.endswith("_test.py"))
NAMES_A_TEST = re.compile(r"`([a-z][a-z0-9_]*)_test\.py`|`([a-z][a-z0-9_]{4,})`")
gone = []
for name, text in sorted(texts.items()):
    for i, line in enumerate(text.splitlines(), 1):
        for full, bare in NAMES_A_TEST.findall(line):
            if full and full not in there:
                gone.append("%s:%d %s_test.py" % (name, i, full))
            elif bare and bare.endswith("_test") \
                    and bare[:-len("_test")] not in there:
                gone.append("%s:%d %s" % (name, i, bare))
check("every test a skill names is in the folder", not gone,
      "%d dead: %s" % (len(gone), "; ".join(gone[:4])))

print("\n4. Every skill a skill sends the reader on to is there")
# The bold markers count: the skills write **`gegenbeweis`** skill, and
# a pattern that wants a backtick right beside the word misses the shape
# they actually use.
SENDS_ON = re.compile(r"skill[s]?\s+\**`([a-z-]+)`"
                      r"|`([a-z-]+)`\**\s+skill")
astray = []
for name, text in sorted(texts.items()):
    for i, line in enumerate(text.splitlines(), 1):
        for a, b in SENDS_ON.findall(line):
            other = a or b
            if other and other not in texts:
                astray.append("%s:%d -> %s" % (name, i, other))
check("every skill named in a skill exists", not astray,
      "%d astray: %s" % (len(astray), "; ".join(astray[:4])))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
