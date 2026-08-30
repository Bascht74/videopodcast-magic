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
                       r"\*\*Version ([0-9][^.]*\.[^*]*)\.\*\*")):
    said = re.search(pattern, text_of(os.path.join(ROOT, name)))
    check("%s names this version" % name,
          bool(said) and said.group(1) == version,
          said.group(1) if said else "no version found")

print("\n2. The changelog keeps its shape")
# Keep a Changelog, plus the two groups this project added: Tests and
# Documentation, and Documentation last. Decided 23.8.2026.
ORDER = ["Added", "Changed", "Deprecated", "Removed", "Fixed",
         "Security", "Tests", "Documentation"]
# From 2.20.0-beta on a version says everything twice, in two blocks:
# the English one first, then a line reading **Deutsch**, then the same
# in German. Both belong on the release page, where a reader jumps to
# the language they want; the program shows only the one it runs in.
# The shape below is judged on the English half, and the German half is
# judged against it -- same number of points, and each in its own
# language.
MARK_DE = "**Deutsch**"


def two_halves(block):
    """The English and the German part of one version's section."""
    at = [i for i, x in enumerate(block.split("\n"))
          if x.strip() == MARK_DE]
    lines = block.split("\n")
    if not at:
        return block, ""
    return "\n".join(lines[:at[0]]), "\n".join(lines[at[0] + 1:])


blocks = re.split(r"^## \[", changelog, flags=re.M)[1:]
for block in blocks[:3]:                      # the newest three
    name = block.split("]")[0]
    block, german = two_halves(block)
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
print("\n3. Both languages, and each in its own")
# Sebastian, 31.8.2026: check the changelog in both languages and check
# yourself with it. A machine cannot say whether a sentence is good; it
# can say whether a sentence is in the language it claims to be.
# Function words give it away -- the same trick german_hunt_test uses
# on the manual.
GERMAN_WORDS = re.compile(
    r"(?<![A-Za-z\u00c0-\u024f])(und|oder|nicht|wird|wurde|werden|steht|"
    r"kann|eine|einen|einem|einer|dass|weil|damit|schon|noch|dann|"
    r"zwischen|jetzt)(?![A-Za-z\u00c0-\u024f])", re.I)
ENGLISH_WORDS = re.compile(
    r"(?<![A-Za-z])(the|and|with|from|into|which|would|there|their|"
    r"because|before|after|between|without|instead|about)(?![A-Za-z])",
    re.I)


def prose(text):
    """The words of a section, without headings, marks and addresses."""
    out = []
    for line in text.split("\n"):
        bare = line.strip()
        if not bare or bare.startswith(("#", "[", "---", "**")):
            continue
        out.append(re.sub(r"`[^`]*`|https?://\S+|\S+\.(md|py|json)", "",
                          bare))
    return " ".join(out)


newest, newest_german = two_halves(blocks[0])
check("the newest version says everything in both languages",
      bool(newest_german.strip()),
      "no %s line under %s" % (MARK_DE, blocks[0].split("]")[0]))
if newest_german.strip():
    same = (len(re.findall(r"^- ", newest, re.M)),
            len(re.findall(r"^- ", newest_german, re.M)))
    check("the same number of points on both sides", same[0] == same[1],
          "%d English, %d German" % same)
    over = sorted(set(m.group(0).lower()
                      for m in GERMAN_WORDS.finditer(prose(newest))))
    check("no German words on the English side", not over, str(over[:5]))
    over = sorted(set(m.group(0).lower()
                      for m in ENGLISH_WORDS.finditer(prose(newest_german))))
    check("no English words on the German side", not over, str(over[:5]))

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
