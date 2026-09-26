# -*- coding: utf-8 -*-
"""What a release has to have, checked instead of remembered.

Four releases went out with a version number set in one place and not
the other, a changelog section in the wrong shape, screenshots of a
window that no longer existed, or a picture the manual points at and
nobody shipped. A rule that only a person enforces holds until that
person is busy, so every check here is the mechanical half of a rule
written out in docs/notes/claude_intern.md. Only the working tree is
read here; what hangs on github.com is text_release_has_program's.
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
import the_program

began = time.time()

ROOT = os.path.dirname(HERE)
SCRIPT = the_program.SCRIPT

done = 0
error = []
def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

def text_of(path):
    return io.open(path, encoding="utf-8").read()

print("1. One version number, named the same everywhere")
# Every piece of the program joined: the key filter this test lifts out
# sits inside the window, which is a piece of its own, and a version
# read out of the file the program starts in would have been all that
# was ever read here.
source = the_program.whole()
found = re.search(r'^VERSION = "([^"]+)"', source, re.M)
check("the program says which version it is", bool(found),
      "VERSION = %r, wanted one line of it in the %d lines of the program"
      % (found.group(1) if found else None, source.count("\n") + 1))
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

# The roadmap's "Where the program stands today" is in here because it
# drifted two versions behind without anything noticing: it says the
# number in the same shape as the READMEs and was never held to it.
#
# The four are written out rather than looped over, because a check
# whose name is computed carries no wording the register can key on --
# the two READMEs had stood here for versions with no counter-proof
# possible, and nothing said so.
SAYS_VERSION = r"\*\*Version ([0-9][^.]*\.[^*]*)\.\*\*"
said_by = {}
for name in ("README.md", "README.de.md", "ROADMAP.md", "ROADMAP.de.md"):
    found = re.search(SAYS_VERSION, text_of(os.path.join(ROOT, name)))
    said_by[name] = found.group(1) if found else "no version found"

check("README.md names this version", said_by["README.md"] == version,
      said_by["README.md"])
check("README.de.md names this version", said_by["README.de.md"] == version,
      said_by["README.de.md"])
check("ROADMAP.md names this version", said_by["ROADMAP.md"] == version,
      said_by["ROADMAP.md"])
check("ROADMAP.de.md names this version",
      said_by["ROADMAP.de.md"] == version, said_by["ROADMAP.de.md"])

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
    # Only the part below ROOT is asked: a checkout that itself lies
    # under a dot-folder would otherwise skip every folder, and every
    # picture would count as unused. ROOT itself is "." to relpath, and
    # a dot-folder to the line under it, so it stands as nothing.
    below = os.path.relpath(folder, ROOT)
    below = "" if below == os.curdir else os.sep + below
    if os.sep + "." in below or "notes" in below:
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


# project_write stores no command line: the source of the function is
# read here and asked both halves of that, because a filter can be got
# round and an absent argument cannot.
def project_write_body():
    """The source of project_write, dedented to the left margin."""
    lines = source.split("\n")
    at = [i for i, x in enumerate(lines)
          if x.strip().startswith("def project_write(")]
    if not at:
        return ""
    room = len(lines[at[0]]) - len(lines[at[0]].lstrip())
    out = [lines[at[0]][room:]]
    for x in lines[at[0] + 1:]:
        if x.strip() and len(x) - len(x.lstrip()) <= room:
            break
        out.append(x[room:])
    return "\n".join(out)


body = project_write_body()
first = (body or "").split("\n")[0]
check("project_write is handed no command line",
      first.startswith("def project_write():"),
      "its first line: %r" % (first.strip() or "no project_write found",))
check("and fetches none of its own", body and "argv" not in body,
      "argv named in %s"
      % ([x.strip() for x in (body or "").split("\n") if "argv" in x]
         or ("no line" if body else "no project_write found")))

print("\n5. Both languages, and each in its own")
# A machine cannot say whether a sentence is good, but it can say
# whether a sentence is in the language it claims to be. Function words
# give it away, the same trick text_no_german_left_test uses on the manual.
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
      "" if newest_german.strip() else
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
                # The room, not only the two numbers: without it
                # whoever shortens guesses, and guesses more than once.
                long_ones.append(
                    "%d characters, %d too many (room %d, middle %d): %s"
                    % (len(text), len(text) - int(room), int(room),
                       middle, text[:40]))
    check("no point stands out by its length", not long_ones,
          long_ones[0] if long_ones else "")

    # A point says what the program does differently; why the old state
    # was wrong belongs in the commit message. Three points of one
    # version had to be rewritten because they explained the mechanism
    # instead, and the checks above caught none of them.
    #
    # No machine can judge that, so what is held here are two marks such
    # a sentence leaves behind. Both were measured over all 984 points
    # the file held when they were written: the first matches nothing at
    # all, the second twice, and both times the same point -- the one
    # whose two similarity scores were struck out for saying nothing.
    #
    # WHAT THIS DOES NOT CATCH, and it is most of it: mechanism
    # explained in ordinary words. "Qt answers neither of two claims on
    # one key" passes every rule below, and the word cannot go on a
    # list -- four good points name Qt, for a Qt built without
    # multimedia, which is a state the reader is in. Nor can a list of
    # tool names: ffprobe stands ten times in the manual. Whole numbers
    # without a unit pass too, and so does a two-sentence justification
    # short enough to stay under the length above.
    #
    # What stands in backticks is a quotation -- a switch, a file name,
    # an environment variable -- and is not read as prose. Every one of
    # the 24 underscores in the file stands inside them.
    QUOTED = re.compile(r"`[^`]*`")
    # kept_channels, project_write, QShortcut: shapes that only ever
    # come from the source. A switch is spelled --no-single-tracks and
    # keeps its hyphens, so it is not one of them.
    OUT_OF_SOURCE = re.compile(
        r"(?<![\w-])[a-z][a-z0-9]*(?:_[a-z0-9]+)+(?!\w)"
        r"|(?<![A-Za-z])Q[A-Z][A-Za-z]{2,}(?![A-Za-z])")
    # A number is understood without context where it carries what it
    # measures: "0.040 s", "2.88 MB", "18 seconds". A fraction below one
    # followed by a function word or by the end of the sentence carries
    # nothing: it is a score off a scale that lives inside the program,
    # and the reader cannot read it. Only below one -- above it the same
    # rule would fall over a contrast ratio and over "Python 3.10".
    FUNCTION_WORD = ("against|to|and|or|of|on|in|at|for|from|with|than|"
                     "as|the|a|was|is|were|are|be|not|but|so|then|now|"
                     "it|its|his|her|their|zu|zum|zur|und|oder|auf|im|"
                     "an|am|bei|der|die|das|den|dem|des|ein|eine|einen|"
                     "einem|einer|war|ist|sind|nicht|aber|gegen|nach|"
                     "vor|mit|von|aus|als|wie|noch|schon|dann|jetzt")
    WITHOUT_UNIT = re.compile(
        r"(?<![\d.,:v-])0[.,](\d\d+)(?![\d.,])(\s+(?:%s)\b|\s*[.,;)]|$)"
        % FUNCTION_WORD, re.I)

    from_source, no_unit, weighed = [], [], 0
    for part in (newest, newest_german):
        for one in points_of(part):
            said = " ".join(x.strip() for x in one)[2:]
            weighed += 1
            prose_only = QUOTED.sub(" ", said)
            for spotted in OUT_OF_SOURCE.finditer(prose_only):
                from_source.append("%r in: %s" % (spotted.group(0),
                                                  said[:50]))
            for spotted in WITHOUT_UNIT.finditer(prose_only):
                no_unit.append("%r in: %s" % (spotted.group(0).strip(),
                                              said[:50]))
    check("no point carries a name out of the source", not from_source,
          "%d in %d points, first: %s" % (len(from_source), weighed,
                                          from_source[0])
          if from_source else "none in %d points" % weighed)
    check("every number in a point says what it counts", not no_unit,
          "%d in %d points, first: %s" % (len(no_unit), weighed,
                                          no_unit[0])
          if no_unit else "none in %d points" % weighed)

    # Under Fixed a point can be written entirely in the past and read
    # as finished when it is not, so the word carrying the second half
    # -- what happens now -- has to be there. Only Fixed: Added is all
    # "now" by nature, and Changed carries the old state in its wording.
    NOW = {"Fixed": ("now", "no longer", "instead"),
           "Behoben": ("jetzt", "nicht mehr", "stattdessen")}
    half_told = []
    for part in (newest, newest_german):
        for chunk in part.split("### "):
            name = chunk.split("\n")[0].strip()
            if name not in NOW:
                continue
            for one in points_of("### " + chunk):
                text = " ".join(x.strip() for x in one)[2:]
                if not any(w in text.lower() for w in NOW[name]):
                    half_told.append("%s: %s" % (name, text[:60]))
    check("every fixed point says how it is now", not half_told,
          "%d of them, first: %s" % (len(half_told), half_told[0])
          if half_told else "")

print("""
Before the tag -- five things, and the tag comes last:

  checked here   the changelog names this version, in the right groups
  checked here   the READMEs and the roadmap name this version
  checked here   the manual's defaults match the parser (docs_truth)
  checked beside the file hangs on every release github.com lists,
                 where github.com answers at all (text_release_has_program)
  ONLY A PERSON  the manual says what a person can now see or feel,
                 in both languages -- a moved default, a new answer in
                 a field, a computation that costs their processor
  ONLY A PERSON  the pictures show the program as it is now, where the
                 window changed (docs/notes says how they are taken)
  ONLY A PERSON  the open list and the roadmap issue are brought up to
                 date, not caught up afterwards

And before all of them: green on all six builder jobs, and the times
fetched with builder_times.sh and looked at.""")

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("\nFAIL: %s" % ", ".join(error) if error else "\nAll good.")
sys.exit(1 if error else 0)
