# -*- coding: utf-8 -*-
"""Writes the table of every test into README.md, out of the tests.

A list of every test kept by hand is wrong within a week: somebody
renames one, rewords a heading, adds one, and nobody opens the README. So the tests are the source and this writes the list
down from them -- the name as run.sh prints it, and the first line of
the docstring, which says what holds when the test is green.

    python3 overview.py            # write it into README.md
    python3 overview.py --show     # print it, change nothing

text_tests_listed_test.py holds the README against the folder, so a
list that was not written back turns the suite red rather than going
quietly stale.
"""
import ast
import io
import os
import subprocess
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
README = os.path.join(HERE, "README.md")

# The twelve prefixes of the naming scheme, in the order the guidelines
# name them, and what part of the program each one stands for. The
# gloss is the only text here written by hand; the rows below it all
# come out of the files.
PREFIXES = [
    ("files_", "the material: what is read, what is written, what is left"),
    ("sound_", "channels, tracks and loudness"),
    ("time_", "the common time axis"),
    ("voice_", "who speaks, and where"),
    ("cut_", "the cut by speaker, and the player over it"),
    ("project_", "what DaVinci Resolve is handed"),
    ("auphonic_", "the way out to auphonic.com and back"),
    ("window_", "the interface"),
    ("table_", "the assignment table"),
    ("run_", "a whole run: command line, threads, progress, log"),
    ("text_", "the texts: catalogue, manual, changelog"),
    ("source_", "the source itself, held by ratchets"),
]

# The list lives between these two lines. Everything outside them is
# written by hand and never touched here.
BEGIN = "<!-- overview begins -- written by overview.py, not by hand -->"
END = "<!-- overview ends -->"

# What a row looks like, and what reads one back. Both here, so the two
# cannot drift apart.
ROW = "| `%s` | %s |"
ROW_READ = re.compile(r"^\| `([a-z0-9_]+)` \| (.*?) \|$")
HEAD_READ = re.compile(r"^### `([a-z]+_)`")
NO_PREFIX_HEAD = "### Under none of the twelve"
# The tests under resolve/live/ are not in the suite and not in its
# count; they stand in a table of their own, under this heading. Two
# folders down, so resolve/ itself stays a piece like any other.
APART = "resolve/live"
APART_HEAD = "### Under `resolve/live/`"
# Where each test lies: in tests/ or in the folder under it named after
# the piece of the program it checks. This index says which; the rows
# above it stay under their prefixes.
FOLDERS_HEAD = "### By folder"
FOLDER_ROW = "| %s | %s |"
FOLDER_READ = re.compile(r"^\| (`[a-z0-9_]+/`|tests/ itself) \| (.*) \|$")
ROOT_LABEL = "tests/ itself"
# The two folders that are no piece, each named where it holds a test.
ASIDE = (("source", "`source/` is no piece: it holds the tests that read"),
         ("source", "the source, the texts and the documents as a whole."),
         ("", "A test under `tests/ itself` has no piece folder yet."))
COUNT_READ = re.compile(r"(?<![0-9])([0-9]+) tests(?![A-Za-z])")


def first_line_of(text):
    """The first line of a source's module docstring, or a stand-in.

    A test without one is a defect, not a reason to leave a row out:
    the row is written with the fault in it so it is seen in the README
    and in the red line of the test that guards it.
    """
    try:
        doc = ast.get_docstring(ast.parse(text), clean=False)
    except SyntaxError as why:
        return "(will not parse: %s)" % why
    if not doc or not doc.split("\n")[0].strip():
        return "(no docstring)"
    return doc.split("\n")[0].strip()


def ours(path, below=""):
    """Whether a test at `path`, relative and with /, is the suite's.

    With `below` empty the suite is tests/ and every folder one below
    it, which leaves resolve/live/ out; with `below` named, that folder
    alone.
    """
    parent = path.rpartition("/")[0]
    if below:
        return parent == below
    return parent == "" or ("/" not in parent and parent != APART)


def git(folder, *args):
    """What git answers in `folder`, or None where there is no git."""
    try:
        out = subprocess.run(("git", "-C", folder) + args,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL)
    except OSError:
        return None
    return out.stdout.decode("utf-8") if out.returncode == 0 else None


def test_places(folder=HERE, below=""):
    """Every test of this repository: its name and where it lies, in pairs.

    The repository is asked, not the folder. The builder moves the tests
    a machine cannot run out of the way before the suite starts -- the
    Windows key store on a Mac, the speech model where there is none --
    so the folder there is never the whole suite. Without git, the
    folder has to do. Pairs and not a dictionary: a name lying in two
    folders comes back twice, where a dictionary would keep one of them.
    """
    here = {}
    for top in (os.listdir(folder) if os.path.isdir(folder) else ()):
        inside = os.path.join(folder, top)
        paths = [top]
        if os.path.isdir(inside) and not top.startswith((".", "__")):
            paths = [top + "/" + one for one in os.listdir(inside)]
        # A folder named deeper down, resolve/live/, is read as well.
        if below.startswith(top + "/"):
            deep = os.path.join(folder, *below.split("/"))
            if os.path.isdir(deep):
                paths += [below + "/" + one for one in os.listdir(deep)]
        for path in paths:
            if path.endswith("_test.py") and ours(path, below):
                here[path] = None
    listed = git(folder, "ls-files", "--", "*_test.py") or ""
    for line in (one.strip() for one in listed.splitlines()):
        if line.endswith("_test.py") and ours(line, below):
            here.setdefault(line, None)
    return [(path.rpartition("/")[2][:-len("_test.py")], path)
            for path in sorted(here)]


def test_sources(folder=HERE, below=""):
    """Every test of this repository, by name, with its text.

    Which tests those are, and where, is test_places's to say. A file
    that is there is read from there, so uncommitted work counts; only
    one that was moved aside is read out of the last commit. `below`
    names a folder, and a test there is that folder's and not the suite's.
    """
    out = {}
    for name, path in test_places(folder, below):
        whole = os.path.join(folder, *path.split("/"))
        if os.path.exists(whole):
            out[name] = io.open(whole, encoding="utf-8").read()
        else:
            text = git(folder, "show", "HEAD:./" + path)
            if text is not None:
                out[name] = text
    return out


def folders(folder=HERE):
    """Every test of the suite by name, and the folder it lies in.

    "" stands for tests/ itself. The folder carries the name of the
    piece of the program whose logic the test checks.
    """
    return dict((name, path.rpartition("/")[0])
                for name, path in test_places(folder))


def statements(folder=HERE, below=""):
    """Every test: its name, and what green means.

    The name is the one run.sh prints and the one a red line carries,
    so `_test.py` comes off; that is what somebody grepping the README
    after a failure has in front of them.
    """
    return dict((name, first_line_of(text))
                for name, text in test_sources(folder, below).items())


def grouped(rows):
    """The tests under their prefix, and the rest under none.

    A test whose name starts with no known prefix is not dropped. It
    gets a group of its own at the end, because a list that quietly
    leaves one out is worth less than none.
    """
    left = dict(rows)
    out = []
    for prefix, gloss in PREFIXES:
        mine = sorted(n for n in left if n.startswith(prefix))
        for name in mine:
            del left[name]
        out.append((prefix, gloss, mine))
    return out, sorted(left)


def escape(text):
    """A pipe in a statement would end the table cell it stands in."""
    return text.replace("|", "\\|")


def unescape(text):
    return text.replace("\\|", "|")


def rendered(rows, apart=None, where=None):
    """The whole block, markers included, ready to stand in the README.

    `apart` are the tests under resolve/live/, by name as resolve.sh takes
    them. Their table carries no count: the one above is the suite's.
    `where` is each suite test's folder, for the index by folder.
    """
    groups, loose = grouped(rows)
    out = [BEGIN, ""]
    out.append("%d tests. The name is the one a red line carries, and beside"
               " it the" % len(rows))
    out.append("first line of that test's docstring: what holds about the"
               " program when")
    out.append("it is green.")
    for prefix, gloss, mine in groups:
        out += ["", "### `%s` -- %s" % (prefix, gloss), "",
                "| Test | Green means |", "|---|---|"]
        for name in mine:
            out.append(ROW % (name, escape(rows[name])))
    if loose:
        out += ["", NO_PREFIX_HEAD, "",
                "These are about the suite itself rather than about a part",
                "of the program, so no prefix fits them.", "",
                "| Test | Green means |", "|---|---|"]
        for name in loose:
            out.append(ROW % (name, escape(rows[name])))
    if where:
        out += ["", FOLDERS_HEAD + " -- the piece each test checks", "",
                "A test lies in the folder named after the piece of the",
                "program under `videopodcast_magic/` whose logic it checks;",
                "`bash run.sh <name>` finds it there by its name alone."]
        out += [line for one, line in ASIDE if one in where.values()]
        out += ["", "| Folder | Tests |", "|---|---|"]
        for one in sorted(set(where.values()), key=lambda f: (not f, f)):
            label = "`%s/`" % one if one else ROOT_LABEL
            out.append(FOLDER_ROW % (label, ", ".join(
                "`%s`" % name for name in sorted(where)
                if where[name] == one)))
    if apart:
        out += ["", APART_HEAD + " -- beside a running DaVinci Resolve", "",
                "Not in the suite and not in the count above: `resolve.sh`",
                "starts these by hand, one after another.", "",
                "| Test | Green means |", "|---|---|"]
        for name in sorted(apart):
            out.append(ROW % (name, escape(apart[name])))
    out += ["", END]
    return "\n".join(out) + "\n"


def rows_in(text):
    """Read the block back: the rows, and the heading each one sits under.

    Used by the test that guards the list, so the reading and the
    writing sit in one file and cannot come apart.
    """
    inside = False
    under = ""
    out = []
    for line in text.splitlines():
        if line.strip() == BEGIN:
            inside = True
            continue
        if line.strip() == END:
            inside = False
            continue
        if not inside:
            continue
        head = HEAD_READ.match(line)
        if head:
            under = head.group(1)
        elif line.startswith(NO_PREFIX_HEAD):
            under = ""
        elif line.startswith(APART_HEAD):
            under = APART + "/"
        row = ROW_READ.match(line)
        if row:
            out.append((under, row.group(1), unescape(row.group(2))))
    return out


def folders_in(text):
    """Read the index back: every test named in it, and its folder.

    Pairs and not a dictionary, so a name standing in two rows of the
    index is seen twice rather than once.
    """
    out = []
    inside = False
    for line in text.splitlines():
        if line.strip() == BEGIN:
            inside = True
        elif line.strip() == END:
            inside = False
        row = FOLDER_READ.match(line) if inside else None
        if row:
            one = "" if row.group(1) == ROOT_LABEL else row.group(1)[1:-2]
            out += [(name, one) for name in
                    re.findall(r"`([a-z0-9_]+)`", row.group(2))]
    return out


def counts_in(text):
    """Every "N tests" the README claims, as numbers."""
    return [int(n) for n in COUNT_READ.findall(text)]


def spliced(text, block):
    """The README with the block put in place of the old one."""
    start = text.find(BEGIN)
    stop = text.find(END)
    if start < 0 or stop < 0:
        raise SystemExit("no %s / %s markers in %s" % (BEGIN, END, README))
    return text[:start] + block + text[stop + len(END) + 1:]


def main(argv):
    rows = statements()
    block = rendered(rows, statements(HERE, APART), folders())
    if "--show" in argv:
        sys.stdout.write(block)
        return 0
    text = io.open(README, encoding="utf-8").read()
    fresh = spliced(text, block)
    # The count outside the block as well, or the README says one thing
    # at the top and another in the middle.
    fresh = COUNT_READ.sub("%d tests" % len(rows), fresh)
    if fresh == text:
        print("%s is up to date: %d tests" % (README, len(rows)))
        return 0
    io.open(README, "w", encoding="utf-8").write(fresh)
    print("%s written: %d tests" % (README, len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
