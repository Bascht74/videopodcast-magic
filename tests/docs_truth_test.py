# -*- coding: utf-8 -*-
"""Where the manual copies a list out of the program, it has to match.

A reading of the twelve chapters on 24.8.2026 found thirteen places
where the manual claimed something the program does not do: the menu
bar carries four menus and the chapter said three, the default of
--speakers-local was given wrongly, --no-transcript-file was missing
from the list that calls itself complete. None of the three tests that
read the manual saw any of it. They check its form -- both languages
there, no German word on the English side, every index entry pointing
at a heading that exists -- and a wrong fact is a question of truth,
not of form.

Eight of the thirteen were whole sentences of prose. A test that
judges those is a test that turns red at every rewording, and a test
like that gets switched off rather than fixed. The five that remain
are all the same shape, and that shape is the only one this file
touches: the program keeps a list, and the manual writes the same list
down. Sets get compared, never sentences.

  1. every switch of build_argument_parser stands in the table of
     docs/command-line.md, and every row of the table is a switch
  2. the defaults named in brackets at the end of a row, but only the
     ones a machine can compare
  3. the four cut rules of CUT_CHOICES: their values, their defaults,
     and the default named again in docs/camera-cut.md
  4. the menus the window builds, against docs/interface.md
  5. links between the shipped .md files that lead nowhere

Both languages everywhere, and where the manual writes a label rather
than the raw value -- "Alternating" for alternate -- the way across is
SHOT_NAMES and the catalogue, so a renamed label moves both sides at
once.

What is deliberately left out, so that a red line here always means a
real defect:

  * Defaults the manual writes in words because the program works the
    value out at run time: --head and --tail say "measured", --tc and
    --fps say "from the video file", --speakers-local names the
    recording the run picks itself, --auphonic-preset and
    --auphonic-resume say the program asks. The parser holds None for
    all of them. What the manual writes there is the better answer,
    not a wrong one, and comparing it against None would only teach
    the manual to say less. Measured on 24.8.2026: 21 of 68 rows,
    every one of them a false alarm.
  * Every bold label of a chapter looked up in the program. Measured:
    8 of 38 in interface.md are not labels at all but bold
    subheadings. The narrower case, the menu bar, is check 4.
  * Screenshots. Whether a picture still shows today's window is a
    question no test answers without a reference image per system;
    shoot_screenshots.py makes them all again before a release.

Where a chapter no longer names a number of menus at all, check 4 says
so in its own line instead of turning red: the names are the check
that bites, the count is the one that reads well.
"""
import importlib.util
import io
import os
import re
import sys

# Menu names and labels are German on one side, and the suite runs
# under LC_ALL=C. A report that cannot print its own finding would be
# a traceback instead of a message.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "docs")
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    ROOT, "videopodcast-magic.py")

spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
source = io.open(SCRIPT, encoding="utf-8").read()
GERMAN = vpm.CATALOGUE["de"]

bad = []


def check(what, ok, detail=""):
    print("  %-56s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


def found(what, cases):
    """One check, and under it one line per case that went wrong.

    A count is not enough to act on. Every line names what the program
    holds, what the manual says and which file and line it says it in.
    """
    check(what, not cases, "%d, first: %s" % (len(cases), cases[0])
          if cases else "")
    for case in cases:
        print("      %s" % case)


def text_of(chapter):
    return io.open(os.path.join(DOCS, chapter), encoding="utf-8").read()


# A row of a switch table: | `--switch VALUE` | what it does |
ROW = re.compile(r"\|\s*`(--[a-z0-9-]+)[^`]*`\s*\|\s*(.*?)\s*\|\s*$")
# What the row names as the default, in brackets at the very end.
TAIL = re.compile(r"\(([^()]{1,60})\)\s*$")
NUMBER = re.compile(r"^-?\d+(?:[.,]\d+)?$")


def rows_of(chapter):
    """Switch, what the row says, and the line it stands on."""
    out = []
    for number, line in enumerate(text_of(chapter).splitlines(), 1):
        hit = ROW.match(line.strip())
        if hit:
            out.append((hit.group(1), hit.group(2).strip(), number))
    return out


CHAPTERS = (("command-line.md", False), ("command-line.de.md", True))

# --help is argparse's own, and the chapter names it in the sentence
# above the tables rather than in a row of its own.
SILENT = {"--help"}

print("1. Every switch in the table, every row a switch")
parser = vpm.build_argument_parser()
switches = {}
for action in parser._actions:
    for name in action.option_strings:
        if name.startswith("--"):
            switches[name] = action
check("build_argument_parser hands out its switches",
      len(switches) > 20, "%d" % len(switches))

for chapter, german in CHAPTERS:
    rows = rows_of(chapter)
    check("%s still holds a table of switches" % chapter,
          len(rows) > 20, "%d rows" % len(rows))
    listed = [switch for switch, _, _ in rows]
    where = {}
    for switch, _, number in rows:
        where.setdefault(switch, number)
    missing = sorted(set(switches) - set(listed) - SILENT)
    found("%s: no switch of the program is missing" % chapter,
          ["%s: build_argument_parser has it, %s has no row for it"
           % (switch, chapter) for switch in missing])
    gone = sorted(set(listed) - set(switches))
    found("%s: no row for a switch that is gone" % chapter,
          ["%s:%d says %s, build_argument_parser does not know it"
           % (chapter, where[switch], switch) for switch in gone])
    twice = sorted(s for s in set(listed) if listed.count(s) > 1)
    found("%s: no switch stands in two rows" % chapter,
          ["%s: %s stands %d times" % (chapter, switch, listed.count(switch))
           for switch in twice])

print("\n2. The defaults a machine can compare")
for chapter, german in CHAPTERS:
    wrong = []
    counted = 0
    for switch, says, number in rows_of(chapter):
        action = switches.get(switch)
        tail = TAIL.search(says)
        if action is None or tail is None:
            continue
        said = tail.group(1).strip()
        real = action.default
        real_number = isinstance(real, (int, float)) \
            and not isinstance(real, bool)
        if NUMBER.match(said):
            counted += 1
            # German writes 1,5 where English writes 1.5.
            plain = said.replace(",", ".") if german else said
            if not real_number or float(plain) != float(real):
                wrong.append("%s:%d %s says (%s), the parser has %r"
                             % (chapter, number, switch, said, real))
        elif said in ("off", "aus"):
            counted += 1
            if real is not False:
                wrong.append("%s:%d %s says (%s), the parser has %r"
                             % (chapter, number, switch, said, real))
        elif said.startswith("`") and said.endswith("`") \
                and not said.strip("`").startswith("--"):
            counted += 1
            if said.strip("`") != real:
                wrong.append("%s:%d %s says (%s), the parser has %r"
                             % (chapter, number, switch, said, real))
    found("%s: %d comparable defaults, all right" % (chapter, counted),
          wrong)

print("\n3. The cut rules against CUT_CHOICES")
RULES = dict(("--" + rule[0], rule) for rule in vpm.CUT_CHOICES)
check("CUT_CHOICES holds the rules", len(RULES) > 1, "%d" % len(RULES))
for chapter, german in CHAPTERS:
    wrong = []
    seen = 0
    for switch, says, number in rows_of(chapter):
        rule = RULES.get(switch)
        if rule is None:
            continue
        seen += 1
        values = list(rule[3])
        # A row either counts the values up or points at the row above
        # it ("the same four values"); only the counted ones compare.
        named = [word for word in re.findall(r"`([^`]+)`", says)
                 if not word.startswith("--")]
        if named and sorted(named) != sorted(values):
            wrong.append("%s:%d %s takes %s, the row lists %s"
                         % (chapter, number, switch,
                            ", ".join(values), ", ".join(named)))
        tail = TAIL.search(says)
        said = tail.group(1).strip() if tail else "nothing"
        if said != rule[2]:
            wrong.append("%s:%d %s falls back to %s, the row says (%s)"
                         % (chapter, number, switch, rule[2], said))
    found("%s: %d cut rules with their values and defaults"
          % (chapter, seen), wrong)
    check("%s: all four cut rules have a row" % chapter,
          seen == len(RULES), "%d of %d" % (seen, len(RULES)))


def bullets(chapter):
    """The items of the bullet lists, each folded back into one line."""
    out = []
    open_item = False
    for number, line in enumerate(text_of(chapter).splitlines(), 1):
        if line.startswith("* "):
            out.append([line[2:].strip(), number])
            open_item = True
        elif open_item and line.startswith("  ") and line.strip():
            out[-1][0] += " " + line.strip()
        else:
            open_item = False
    return out


for chapter, german in (("camera-cut.md", False),
                        ("camera-cut.de.md", True)):
    items = bullets(chapter)
    wrong = []
    for switch in sorted(RULES):
        rule = RULES[switch]
        label = vpm.SHOT_NAMES.get(rule[2], rule[2])
        if german:
            label = GERMAN.get(label, label)
        mine = [item for item in items if "`%s`" % switch in item[0]]
        if not mine:
            wrong.append("%s: %s falls back to %s, no bullet names it"
                         % (chapter, switch, label))
            continue
        if any("**%s**" % label in item[0] for item in mine):
            continue
        text, number = mine[0]
        bold = re.findall(r"\*\*([^*]+)\*\*", text)
        wrong.append("%s:%d %s falls back to %s, the bullet says %s"
                     % (chapter, number, switch, label,
                        " and ".join(bold[1:]) or "nothing"))
    found("%s: every cut rule shows its default" % chapter, wrong)

print("\n4. The menu bar against the menus the window builds")
MENUS = re.compile(r"addMenu\(T\((['\"])(&?[^'\"]+)\1\)\)")
menus = [hit.group(2) for hit in MENUS.finditer(source)]
check("the program builds a menu bar", len(menus) > 1,
      "%d menus" % len(menus))
# Both chapters write the count as a word. Four and five are the ones
# that matter; the rest are there so a sentence about a window with
# fewer or more menus still gets read instead of passed over.
# german_hunt_test.py holds every test to English letters, so the one
# German word with an umlaut in it is written as an escape.
NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                "six": 6, "seven": 7, "ein": 1, "zwei": 2, "drei": 3,
                "vier": 4, "f\u00fcnf": 5, "sechs": 6, "sieben": 7}
for chapter, german in (("interface.md", False),
                        ("interface.de.md", True)):
    text = text_of(chapter)
    names = []
    for menu in menus:
        name = GERMAN.get(menu, menu) if german else menu
        names.append(name.replace("&", ""))
    wrong = ["%s: the window builds the menu %s, the chapter never "
             "puts it in bold" % (chapter, name)
             for name in names if ("**%s**" % name) not in text]
    found("%s: every menu of the window stands in the chapter" % chapter,
          wrong)
    # "The menu bar carries four menus", "Die Menueleiste traegt vier
    # Menues" -- the same sentence, and the number in it is a fact.
    bar = re.compile(r"Men\w+leiste") if german else re.compile("menu bar")
    counter = re.compile(r"(\w+)\s+Men\w{0,2}s\b") if german \
        else re.compile(r"(\w+)\s+menus\b")
    said = []
    for number, line in enumerate(text.splitlines(), 1):
        if not bar.search(line):
            continue
        for hit in counter.finditer(line):
            word = hit.group(1).lower()
            if word in NUMBER_WORDS:
                said.append((number, hit.group(0), NUMBER_WORDS[word]))
    found("%s: %d sentence(s) count the menus, all right"
          % (chapter, len(said)),
          ["%s:%d the window builds %d menus, the sentence says %r"
           % (chapter, number, len(menus), text_said)
           for number, text_said, how_many in said
           if how_many != len(menus)])

print("\n5. Links between the chapters")
# Only the files that are shipped, and only links inside the repository.
# An outside address needs the network and is made red by other
# people's servers -- the wrong kind of test for a suite.
# The text of a link may be broken over two lines, so the whole file
# is searched at once and the line worked out from where the hit sits.
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)", re.S)
pages = []
for folder in (ROOT, DOCS, os.path.join(ROOT, "development")):
    if not os.path.isdir(folder):
        continue
    for name in sorted(os.listdir(folder)):
        if name.endswith(".md"):
            pages.append(os.path.join(folder, name))


def headings(path):
    """The anchors a Markdown file offers, the way GitHub builds them."""
    out = set()
    for line in io.open(path, encoding="utf-8"):
        if line.startswith("#"):
            title = line.lstrip("#").strip().lower()
            title = re.sub(r"[^\w\s-]", "", title, flags=re.U)
            out.add(re.sub(r"\s+", "-", title))
    return out


dead = []
links = anchors = 0
for page in pages:
    short = os.path.relpath(page, ROOT)
    text = io.open(page, encoding="utf-8").read()
    for hit in LINK.finditer(text):
        href = hit.group(1).strip()
        if href.startswith(("http://", "https://", "mailto:", "#")):
            continue
        links += 1
        number = text.count("\n", 0, hit.start()) + 1
        path, _, mark = href.partition("#")
        target = os.path.normpath(
            os.path.join(os.path.dirname(page), path))
        if not os.path.exists(target):
            dead.append("%s:%d points at %s, there is no such file"
                        % (short, number, href))
            continue
        if not mark:
            continue
        anchors += 1
        if target.endswith(".md") and mark.lower() not in headings(target):
            dead.append("%s:%d points at %s, that heading is not in %s"
                        % (short, number, href, os.path.basename(target)))
check("the chapters link to each other at all", links > 20,
      "%d links" % links)
found("%d links and %d anchors, all of them lead somewhere"
      % (links, anchors), dead)

print()
if bad:
    print("FAIL: %d of the checks" % len(bad))
    sys.exit(1)
print("All good.")
