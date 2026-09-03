# -*- coding: utf-8 -*-
"""Where the manual copies a list out of the program, it has to match.

A reading of the chapters found a dozen places where the manual claimed
something the program does not do, and none of the tests that read the
manual saw any of it: they check its form, and a wrong fact is a
question of truth. Only one shape can be judged by a machine, and it is
the only one this file touches -- the program keeps a list, the manual
writes the same list down. Sets get compared, never sentences.

  1. every switch of build_argument_parser stands in the table of
     docs/command-line.md, and every row of the table is a switch
  2. the defaults named in brackets at the end of a row, but only the
     ones a machine can compare
  3. the cut rules of CUT_CHOICES: their values, their defaults, and
     the default named again in docs/camera-cut.md
  4. the menus the window builds, against docs/interface.md
  5. links between the shipped .md files that lead nowhere

Both languages everywhere, and where the manual writes a label rather
than the raw value the way across is SHOT_NAMES and the catalogue, so a
renamed label moves both sides at once.

Left out on purpose, so a red line here always means a real defect:
defaults the manual writes in words because the program works the value
out at run time, where the parser holds None and the manual is the
better answer; the bold labels of a chapter, most of which are
subheadings rather than labels; and screenshots, which no test judges
without a reference image per system.
"""
import importlib.util
import io
import os
import re
import sys
import time

began = time.time()

# Menu names are German on one side and the suite runs under LC_ALL=C:
# without this a report of a finding would be a traceback instead.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "docs")
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    ROOT, "videopodcast_magic.py")

spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
source = io.open(SCRIPT, encoding="utf-8").read()
GERMAN = vpm.CATALOGUE["de"]

done = 0
bad = []


def check(what, ok, detail=""):
    global done
    done += 1
    print("  %-56s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


def found(what, cases):
    """One check, and under it one line per case that went wrong.

    A count is not enough to act on, so every line names what the
    program holds, what the manual says, and where it says it.
    """
    check(what, not cases, "%d, first: %s" % (len(cases), cases[0])
          if cases else "")
    for case in cases:
        print("      %s" % case)


def text_of(chapter):
    return io.open(os.path.join(DOCS, chapter), encoding="utf-8").read()


# A row of a switch table: | `--switch VALUE` | what it does (default) |
ROW = re.compile(r"\|\s*`(--[a-z0-9-]+)[^`]*`\s*\|\s*(.*?)\s*\|\s*$")
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

# --help is argparse's own and the chapter names it in the sentence
# above the tables, not in a row.
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
        # it; only a row that counts them can be compared.
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
    check("%s: every cut rule has a row" % chapter,
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
# Both chapters write the count as a word, and the neighbours of the
# real count are listed so a sentence keeps being read when a menu is
# added. text_no_german_left_test.py holds every test to English letters, so
# the German word with an umlaut is written as an escape.
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
    # "The menu bar carries four menus" -- the number in that sentence
    # is a fact about the window.
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
# Only links inside the repository: an outside address needs the
# network and is turned red by other people's servers. The text of a
# link may break over two lines, so the whole file is searched at once
# and the line worked out from where the hit sits.
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

print("\n%d checks in %.2f s" % (done, time.time() - began))
if bad:
    print("FAIL: %d of the checks" % len(bad))
    sys.exit(1)
print("All good.")
