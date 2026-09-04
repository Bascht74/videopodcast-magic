# -*- coding: utf-8 -*-
"""What a release has to have, checked instead of remembered.

Four releases went out with a version number set in one place and not
the other, a changelog section in the wrong shape, screenshots of a
window that no longer existed, or a picture the manual points at and
nobody shipped. A rule that only a person enforces holds until that
person is busy, so every check here is the mechanical half of a rule
written out in docs/notes/claude_intern.md.
"""
import ast
import io
import json
import os
import re
import subprocess
import sys
import time
import zipfile
import the_program

began = time.time()

HERE = os.path.dirname(os.path.abspath(__file__))
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
source = text_of(SCRIPT)
found = re.search(r'^VERSION = "([^"]+)"', source, re.M)
check("the program says which version it is", bool(found),
      "VERSION = %r, wanted one line of it in the %d lines of %s"
      % (found.group(1) if found else None,
         source.count("\n") + 1, os.path.basename(SCRIPT)))
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


# The switch is dropped inside project_write, which sits in gui() and
# cannot be called from here. So its own filter is cut out of the source
# and run over a command line carrying a key: the lines themselves
# answer, instead of the word "strip" standing somewhere in the file.
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


# The filter is one assignment and the loop that follows it.
lifted = []
for one in (ast.parse(project_write_body() or "def project_write(argv): pass")
            .body[0].body):
    if isinstance(one, ast.Assign) and "clean" in ast.dump(one.targets[0]):
        lifted = [one]
    elif lifted and isinstance(one, ast.For):
        lifted.append(one)
        break


def key_dropped(argv):
    """What project_write's filter leaves of a command line."""
    if len(lifted) != 2:
        return None
    room = {"argv": argv}
    exec(compile(ast.Module(body=lifted, type_ignores=[]),
                 "project_write", "exec"), room)
    return room.get("clean")


KEY = "not-a-real-key-000"
left = key_dropped(["videopodcast_magic.py", "--out", "somewhere",
                    "--auphonic-api-key", KEY, "--auphonic-preset", "podcast"])
check("the project file drops the switch and its key",
      left is not None and "--auphonic-api-key" not in left
      and KEY not in left and "--auphonic-preset" in left
      and "podcast" in left,
      "the call it would write: %s" % (left,))

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

print("\n6. The program hangs on the releases that are out")
# Whoever has no copy yet gets one from the release page, and the
# program's own update reads that page too. A release without it
# offers a source archive of the whole repository instead, and nothing
# in the working tree can see that -- so this section asks github.com.
#
# A release keeps the shape it went out in, and there have been three.
# The file was renamed when the hyphen went out of it, so the older
# releases carry the old name for ever and the ones behind the rename
# the new one. And on 4.9.2026 the texts moved into files of their own
# beside the program: one of them alone dies on import, so from then on
# an archive of all of them goes up in place of the one file. All three
# names stand in the failure line -- held to one, this would be red on
# everything behind a change and never on the change itself.
ARCHIVE = "videopodcast_magic.zip"
ASSETS = (ARCHIVE, "videopodcast_magic.py", "videopodcast-magic.py")
ASSET_SAID = " or ".join(ASSETS)
left_out = []


def from_github(url, first_bytes=0):
    """What an address answers, or None where nothing answered.

    Over curl rather than urllib: a Python from python.org verifies
    against a certificate store it does not have, and a machine that
    lacks only that must not turn this red. Every reason there is no
    answer -- no network, no name, no permission, a spent rate limit
    -- is written down and leaves the section unasked.
    """
    # -L, because an attachment is handed on to the storage it lies in.
    call = ["curl", "-fsSL", "--max-time", "20",
            "-H", "Accept: application/vnd.github+json"]
    if first_bytes:
        call += ["-r", "0-%d" % (first_bytes - 1)]
    try:
        got = subprocess.run(call + [url], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    except OSError as why:
        left_out.append("curl did not run: %s" % why)
        return None
    if got.returncode:
        left_out.append(
            "%s answered nothing (curl %d: %s)"
            % (url.split("/")[2], got.returncode,
               got.stderr.decode("utf-8", "replace").strip()[:60]))
        return None
    return got.stdout


# The address is the program's own, so a repository that moves takes
# this with it. RELEASE_LIST is written as two pieces of one string.
named = re.search(r'^RELEASE_LIST = \(([^)]+)\)', source, re.M)
listing = "".join(re.findall(r'"([^"]*)"', named.group(1))) if named else ""
check("the program says where its releases are listed", bool(listing),
      listing or "no RELEASE_LIST in the program")

answered = from_github(listing) if listing else None
try:
    releases = json.loads(answered.decode("utf-8")) if answered else None
except ValueError as why:
    left_out.append("what came back is not the list: %s" % why)
    releases = None

if not isinstance(releases, list):
    print("  (%s -- this section asked nothing)"
          % (left_out[0] if left_out else "no address to ask"))
else:
    # Every one of them, with no earliest. The oldest eight were fitted
    # with the file afterwards, out of their own tags, so a boundary
    # here would only say from when somebody had last looked.
    want = [r for r in releases if not r.get("draft")]
    without = []
    for one in want:
        names = [a.get("name") for a in one.get("assets", [])]
        if not [n for n in ASSETS if n in names]:
            without.append("%s carries %s"
                           % (one.get("tag_name"), ", ".join(names)
                              or "nothing but the source archive"))
    check("every release carries the program",
          not without,
          "%d of %d carry %s; %s" % (len(want) - len(without), len(want),
                                     ASSET_SAID, "; ".join(without[:3])
                                     or "none is missing it"))

    # A wrong or half-written attachment is short, and the size comes
    # with the list, so nothing has to be fetched to see it.
    #
    # Two floors, because the two shapes are not the same size. The
    # file only ever grew, so half of the one in the working tree is
    # under every release that was ever made. The archive holds the
    # same program compressed: measured 4.9.2026, 1 950 864 bytes of
    # source came to 588 141, about a third of what the program alone
    # weighs -- so a sixth of that is half again of the smallest it has
    # been, and far above anything half-written.
    floor = os.path.getsize(SCRIPT) // 2
    floor_zip = os.path.getsize(SCRIPT) // 6
    stubs = ["%s: %s at %d bytes" % (one.get("tag_name"), a.get("name"),
                                     a.get("size") or 0)
             for one in want for a in one.get("assets", [])
             if a.get("name") in ASSETS
             and (a.get("size") or 0) < (floor_zip
                                         if a.get("name") == ARCHIVE
                                         else floor)]
    check("none of them is a stub", not stubs,
          "under %d bytes, an archive under %d: %s"
          % (floor, floor_zip, "; ".join(stubs[:3]) or "none of them"))

    newest = want[0] if want else {}
    address = [(a.get("name"), a.get("browser_download_url"))
               for a in newest.get("assets", [])
               if a.get("name") in ASSETS]
    # The version stands near the top, so the first pages of the file
    # answer for the file's version without fetching a megabyte and a
    # half. The window follows the line as the program grows.
    #
    # An archive is not readable that way: what is in it is compressed,
    # and reading it back wants the whole of it to seek in. So that one
    # is fetched entire -- 588 141 bytes when it was measured -- and
    # opening it is at the same time the answer to whether it is an
    # archive at all.
    window = max(32768, source.find('VERSION = "') + 8192)
    got = None
    if address:
        name, url = address[0]
        got = from_github(url, 0 if name == ARCHIVE else window)
    if got is not None:
        if name == ARCHIVE:
            try:
                box = zipfile.ZipFile(io.BytesIO(got))
                parts = [n for n in box.namelist() if not n.endswith("/")]
                text = "\n".join(box.read(n).decode("utf-8", "replace")
                                 for n in parts)
            except (zipfile.BadZipFile, OSError, RuntimeError, ValueError):
                parts, text = [], ""
            # Only the program itself carries such a line, and none of
            # the text files beside it does -- counted 4.9.2026, none
            # of the nine.
            looks = bool(parts) and 'VERSION = "' in text
            shown = "%d bytes, %d files in it" % (len(got), len(parts))
        else:
            text = got.decode("utf-8", "replace")
            looks = text.startswith("#!") and 'VERSION = "' in text
            shown = "%d bytes, %r" % (len(got), text[:20])
        said = re.search(r'^VERSION = "([^"]+)"', text, re.M)
        tag = newest.get("tag_name") or ""
        check("what hangs on %s is the program" % tag, looks, shown)
        check("and it carries the version of its tag",
              bool(said) and "v" + said.group(1) == tag,
              "%s says %s, the tag says %s"
              % (name, said.group(1) if said else "nothing", tag))

print("""
Before the tag -- five things, and the tag comes last:

  checked here   the changelog names this version, in the right groups
  checked here   the READMEs and the roadmap name this version
  checked here   the manual's defaults match the parser (docs_truth)
  checked here   the file hangs on every release github.com lists,
                 where github.com answers at all
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

# Said, not passed over. Not the SKIPPED marker: that one counts the
# whole test as skipped, and run.sh allows one skip in the suite, which
# a machine without a registry already takes. A machine without a
# network would then be red for the weather.
if left_out:
    print("\nLeft out: %s" % left_out[0])
print("\nFAIL: %s" % ", ".join(error) if error else
      "\nAll good." if not left_out else
      "\nGood as far as it went -- github.com was not asked.")
sys.exit(1 if error else 0)
