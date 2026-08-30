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
import overview
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

# The repository, not the folder: the builder moves the tests a machine
# cannot run out of tests/ before the suite starts, so a test a skill
# names would read as a dead file on the jobs that set it aside. Both
# sections below ask this set instead of what happens to lie in tests/.
SUITE = set(overview.test_sources(HERE))

print("\n2. Every path a skill points at is there")
# Only what really looks like a path: a folder in front of it, or an
# ending this repository uses. `check(...)`, `abspath` and the like are
# backticked too and are not files.
LOOKS_LIKE = re.compile(
    r"`((?:tests|docs|development|\.github|\.claude)/[A-Za-z0-9_./-]+"
    r"|[A-Za-z][A-Za-z0-9_-]*\.(?:py|sh|md|json|yml))`")
# Named one by one, so a new name under docs/notes has to be thought
# about rather than slipping in: these are files of the notes folder
# that the skills mention without their folder in front of them.
NOT_SHIPPED = {"shoot_terminal.py", "shoot_screenshots.py", "bilder.md",
               "aufgaben.md", "claude_intern.md"}
missing = []
for name, text in sorted(texts.items()):
    for i, line in enumerate(text.splitlines(), 1):
        for hit in LOOKS_LIKE.findall(line):
            path = hit.rstrip(".")
            # A segment in capitals is a blank to fill in, not a file:
            # `docs/images/NAME.png` stands in a command as a pattern.
            if any(part.isupper() for part in re.split(r"[/.]", path)):
                continue
            # The working notes are deliberately not shipped, so on a
            # clone they are absent by design and not by mistake. A
            # skill may point at them; it may not depend on them.
            if path.startswith("docs/notes") or path in NOT_SHIPPED:
                continue
            # A test is asked of the suite, and it makes no difference
            # whether the skill writes tests/ in front of the name: the
            # one set aside is still one of ours, and a skill naming it
            # is not naming a dead file.
            base = os.path.basename(path)
            if base.endswith("_test.py") and path in (base, "tests/" + base):
                if base[:-len("_test.py")] in SUITE:
                    continue
            # Everything else goes over the folder, not over git: nothing
            # moves these, and the folder answers for uncommitted work as
            # readily as for the rest. A bare name may also live in
            # tests/ or beside the program.
            elif os.path.exists(os.path.join(ROOT, path)):
                continue
            elif "/" not in path and any(
                    os.path.exists(os.path.join(ROOT, d, path))
                    for d in ("", "tests", "docs", "development")):
                continue
            missing.append("%s:%d %s" % (name, i, path))
check("every path a skill names resolves", not missing,
      "%d dead: %s" % (len(missing), "; ".join(missing[:4])))

print("\n3. Every test a skill names is there")
NAMES_A_TEST = re.compile(r"`([a-z][a-z0-9_]*)_test\.py`|`([a-z][a-z0-9_]{4,})`")
gone = []
for name, text in sorted(texts.items()):
    for i, line in enumerate(text.splitlines(), 1):
        for full, bare in NAMES_A_TEST.findall(line):
            if full and full not in SUITE:
                gone.append("%s:%d %s_test.py" % (name, i, full))
            elif bare and bare.endswith("_test") \
                    and bare[:-len("_test")] not in SUITE:
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
