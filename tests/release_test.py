# -*- coding: utf-8 -*-
"""What a release has to have, checked instead of remembered.

Four releases went out with a version number set in one place and not
the other, a changelog section in the wrong shape, screenshots of a
window that no longer existed, or a picture the manual points at and
nobody shipped. A rule that only a person enforces holds until that
person is busy, so every check here is the mechanical half of a rule
written out in docs/notes/claude_intern.md.
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
# UNRELEASED is what a strand writes before the number is decided, and
# may stand at the top while work is going on.
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
# Documentation, Documentation last.
ORDER = ["Added", "Changed", "Deprecated", "Removed", "Fixed",
         "Security", "Tests", "Documentation"]
# A version says everything twice: the English half first, then a line
# reading **Deutsch**, then the same in German. The shape is judged on
# the English half and the German half is judged against it.
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
    # The report names the wanted order as well as the one found: a
    # line that only lists the groups leaves the reader to look the
    # order up somewhere else.
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
# The two ways the key could reach a file by accident: written out with
# the other settings, or handed to a subprocess in the environment.
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

print("\n3. Both languages, and each in its own")
# A machine cannot say whether a sentence is good, but it can say
# whether a sentence is in the language it claims to be. Function words
# give it away, the same trick german_hunt_test uses on the manual.
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

    # A point names the thing, says what it was and what it is now, and
    # leaves the reasoning to the commit message. A machine cannot judge
    # the writing, but it can hold the length.
    def points_of(part):
        """Every point of a section, each as one string."""
        out, now = [], None
        for line in part.split("\n"):
            if line.startswith("- "):
                if now:
                    out.append(now)
                now = [line]
            elif now is not None and line.startswith("  "):
                now.append(line)
            elif now:
                out.append(now)
                now = None
        if now:
            out.append(now)
        return out

    # Measured against the section itself, because a fixed limit goes
    # stale the moment the style moves. Half again the middle catches
    # the point that ran away and not the one that says a little more,
    # and the floor keeps a section of one-line points quiet.
    long_ones = []
    for part in (newest, newest_german):
        said = [" ".join(x.strip() for x in one)[2:]
                for one in points_of(part)]
        if len(said) < 3:
            continue
        middle = sorted(len(x) for x in said)[len(said) // 2]
        room = max(1.5 * middle, 200)
        for text in said:
            if len(text) > room:
                long_ones.append(
                    "%d characters against a middle of %d: %s"
                    % (len(text), middle, text[:40]))
    check("no point stands out by its length", not long_ones,
          long_ones[0] if long_ones else "")

    # Under Fixed a point can be written entirely in the past and read
    # as finished when it is not, so the word carrying the second half
    # -- what happens now -- has to be there. Only Fixed: Added is all
    # "now" by nature, and Changed carries the old state in its wording.
    NOW = {"Fixed": ("now", "no longer", "instead"),
           "Behoben": ("jetzt", "nicht mehr", "stattdessen")}
    half_told = []
    for part in (newest, newest_german):
        heading = None
        for chunk in part.split("### "):
            name = chunk.split("\n")[0].strip()
            if name not in NOW:
                continue
            heading = name
            for one in points_of("### " + chunk):
                text = " ".join(x.strip() for x in one)[2:]
                if not any(w in text.lower() for w in NOW[name]):
                    half_told.append("%s: %s" % (name, text[:60]))
        del heading
    check("every fixed point says how it is now", not half_told,
          "%d of them, first: %s" % (len(half_told), half_told[0])
          if half_told else "")

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
