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
COUNT_READ = re.compile(r"(?<![0-9])([0-9]+) tests(?![A-Za-z])")


def first_line(path):
    """The first line of a file's module docstring, or a stand-in.

    A test without one is a defect, not a reason to leave a row out:
    the row is written with the fault in it so it is seen in the README
    and in the red line of the test that guards it.
    """
    try:
        text = io.open(path, encoding="utf-8").read()
    except OSError as why:
        return "(unreadable: %s)" % why
    try:
        doc = ast.get_docstring(ast.parse(text), clean=False)
    except SyntaxError as why:
        return "(will not parse: %s)" % why
    if not doc or not doc.split("\n")[0].strip():
        return "(no docstring)"
    return doc.split("\n")[0].strip()


def statements(folder=HERE):
    """Every test in the folder: its name, and what green means.

    The name is the one run.sh prints and the one a red line carries,
    so `_test.py` comes off; that is what somebody grepping the README
    after a failure has in front of them.
    """
    out = {}
    for name in sorted(os.listdir(folder)):
        if name.endswith("_test.py"):
            out[name[:-len("_test.py")]] = first_line(
                os.path.join(folder, name))
    return out


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


def rendered(rows):
    """The whole block, markers included, ready to stand in the README."""
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
        row = ROW_READ.match(line)
        if row:
            out.append((under, row.group(1), unescape(row.group(2))))
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
    block = rendered(rows)
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
