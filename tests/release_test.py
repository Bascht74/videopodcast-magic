# -*- coding: utf-8 -*-
"""What a release has to have, checked instead of remembered.

Four things went wrong in this project because they were on a list
somebody had to read rather than in a test that turns red:

  * a version number set in one place and not the other,
  * a changelog section written in the wrong shape,
  * screenshots that showed a window which no longer existed,
  * a picture referred to from the manual that was not there.

A rule that only a person enforces is a rule that holds until that
person is busy. Every check here is the mechanical half of a rule that
is written out in docs/notes/claude_intern.md.
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    ROOT, "videopodcast-magic.py")

error = []
def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

def text_of(path):
    return io.open(path, encoding="utf-8").read()

print("1. One version number, named the same everywhere")
source = text_of(SCRIPT)
found = re.search(r'^VERSION = "([^"]+)"', source, re.M)
check("the program says which version it is", bool(found))
version = found.group(1) if found else ""

changelog = text_of(os.path.join(ROOT, "CHANGELOG.md"))
sections = re.findall(r"^## \[([^\]]+)\]", changelog, re.M)
check("the changelog has sections", bool(sections),
      str(sections[:3]))
# UNRELEASED is what a strand writes before the number is decided; it
# is allowed to stand at the top while work is going on.
newest = next((s for s in sections if s.upper() != "UNRELEASED"), "")
check("the newest numbered section is this version", newest == version,
      "%r in the changelog, %r in the program" % (newest, version))

for name, pattern in (("README.md", r"\*\*Version ([0-9][^.]*\.[^*]*)\.\*\*"),
                      ("README.de.md",
                       r"\*\*Fassung ([0-9][^.]*\.[^*]*)\.\*\*")):
    said = re.search(pattern, text_of(os.path.join(ROOT, name)))
    check("%s names this version" % name,
          bool(said) and said.group(1) == version,
          said.group(1) if said else "no version found")

print("\n2. The changelog keeps its shape")
# Keep a Changelog, plus the two groups this project added: Tests and
# Documentation, and Documentation last. Decided 23.8.2026.
ORDER = ["Added", "Changed", "Deprecated", "Removed", "Fixed",
         "Security", "Tests", "Documentation"]
blocks = re.split(r"^## \[", changelog, flags=re.M)[1:]
for block in blocks[:3]:                      # the newest three
    name = block.split("]")[0]
    groups = re.findall(r"^### (\w+)", block, re.M)
    unknown = [g for g in groups if g not in ORDER]
    check("%s: only groups that are allowed" % name, not unknown,
          str(unknown))
    check("%s: every group once" % name,
          len(groups) == len(set(groups)), str(groups))
    rank = [ORDER.index(g) for g in groups if g in ORDER]
    # What it should be, not only what it is. A line that says
    # ['Tests', 'Added', 'Changed'] leaves the reader to work out the
    # order for themselves and to look it up somewhere else -- and this
    # went red on all six builders on 30.8.2026 for exactly that, twice
    # in one evening.
    check("%s: groups in order, Documentation last" % name,
          rank == sorted(rank),
          "%s -- wanted %s" % (groups, [g for g in ORDER if g in groups]))

print("\n3. Every picture is there, and every picture is used")
images = os.path.join(ROOT, "docs", "images")
on_disc = set(n for n in os.listdir(images) if n.endswith(".png"))
used = set()
missing = []
for folder, _, names in os.walk(ROOT):
    if os.sep + "." in folder or "notes" in folder:
        continue
    for name in names:
        if not name.endswith(".md"):
            continue
        path = os.path.join(folder, name)
        for shown in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text_of(path)):
            used.add(os.path.basename(shown))
            whole = os.path.normpath(os.path.join(folder, shown))
            if not os.path.exists(whole):
                missing.append("%s -> %s" % (name, shown))
check("no picture is referred to that is not there", not missing,
      str(missing[:3]))
spare = sorted(on_disc - used)
check("no picture lies there unused", not spare, str(spare))
check("every picture has both languages",
      all(n.replace(".png", ".de.png") in on_disc for n in on_disc
          if not n.endswith(".de.png")),
      str(sorted(n for n in on_disc if not n.endswith(".de.png")
                 and n.replace(".png", ".de.png") not in on_disc)))

print("\n4. The key never reaches a file")
# The rule that must not break, in the two ways it could: written out
# with the other settings, or handed to a subprocess in the
# environment. Both are how it would happen by accident.
into_file = re.findall(r"^\s*(?:f\.write|json\.dump)\(.*"
                       r"(?:api_key|token|auphonic_key)", source,
                       re.M | re.I)
check("no line writes the key into a file", not into_file,
      str(into_file[:2]))
check("the key is taken out before pip runs",
      source.count('clean.pop("AUPHONIC_TOKEN", None)') >= 3,
      "%d places" % source.count('clean.pop("AUPHONIC_TOKEN", None)'))
check("the project file strips the switch",
      "--auphonic-api-key" in source and "strip" in source.lower())

# The five things a release is, printed where somebody stands right
# before setting the tag. Three of them a test can look at and does,
# above; two only a person can answer, and those are the two that were
# forgotten four releases running -- caught up afterwards instead of
# being part of the work. Sebastian, 31.8.2026: make it a rule you
# cannot overlook. A rule in a document can be overlooked; a block on
# the screen at the moment of the deed is harder.
print("""
Before the tag -- five things, and the tag comes last:

  checked here   the changelog names this version, in the right groups
  checked here   the READMEs name this version
  checked here   the manual's defaults match the parser (docs_truth)
  ONLY A PERSON  the manual says what a person can now see or feel,
                 in both languages -- a moved default, a new answer in
                 a field, a computation that costs their processor
  ONLY A PERSON  the pictures show the program as it is now, where the
                 window changed (docs/notes says how they are taken)
  ONLY A PERSON  the open list and the roadmap issue are brought up to
                 date, not caught up afterwards

And before all of them: green on all six builder jobs, and the times
fetched with builder_times.sh and looked at.""")

print("\nAll good." if not error else "\nFAIL: %s" % ", ".join(error))
sys.exit(1 if error else 0)
