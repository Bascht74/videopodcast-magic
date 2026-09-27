# -*- coding: utf-8 -*-
"""The decision book's template carries nothing of its owner's work.

development/decision_book/ holds a copy of the owner's board -- the page
and a README -- for other developers to publish as their own. The
sections in the order they come: the two files are there; the owner is
named by one constant; no forbidden name, no link but the font
stylesheet, no card number and no calendar day stands in either file;
the change log holds one entry and the page is version v1.

The limit of the method: the names are the hashed ones
source_no_real_names keeps, read out of that file, so a name it does
not know is not found here either. A count, an estimate or a release
number of the owner's is not recognised by its shape and is not looked
for.
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
import hashlib
import io
import json
import re
import time

ROOT = os.path.dirname(HERE)
BOOK = os.path.join(ROOT, "development", "decision_book")
NAMES_FROM = os.path.join(HERE, "source", "source_no_real_names_test.py")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def read(path):
    try:
        return io.open(path, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError):
        return ""


def spot(label, text, at):
    return "%s:%d" % (label, text.count("\n", 0, at) + 1)


# ---------------------------------------------------------------- 1.
print("1. The two files")
page = read(os.path.join(BOOK, "index.html"))
readme = read(os.path.join(BOOK, "README.md"))
both = (("index.html", page), ("README.md", readme))
check("the decision book's page and README are there",
      len(page) > 10000 and len(readme) > 500,
      "index.html %d characters, README.md %d, wanted over 10000 and 500"
      % (len(page), len(readme)))

# ---------------------------------------------------------------- 2.
print("\n2. The owner is a role, named once")
# The page calls the owner by a role word, and it stands in one
# constant: a second literal is where the next copy puts a name back.
DEFINED = 'const OWNER_NAME="Eigner";'
literals = page.count('"Eigner"')
check("the owner is named by the one constant OWNER_NAME",
      DEFINED in page and literals == 1,
      "definition %s, \"Eigner\" written %d times, wanted once"
      % ("found" if DEFINED in page else "missing", literals))

# ---------------------------------------------------------------- 3.
print("\n3. Names, links, card numbers, days")
# The names are not written here: source_no_real_names keeps them as
# sha256, and they are read out of that file so they stand in one place.
names, shortest = (), 4
try:
    for node in ast.parse(read(NAMES_FROM)).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id == "NAMES":
                names = tuple(ast.literal_eval(node.value))
            elif node.targets[0].id == "SHORTEST":
                shortest = ast.literal_eval(node.value)
except (SyntaxError, ValueError):
    names = ()
WORD = re.compile(r"[^\W\d_]+")
named = []
for label, text in both:
    low = text.lower()
    for m in WORD.finditer(low):
        word = m.group(0)
        for size in range(shortest, len(word) + 1):
            for at in range(len(word) - size + 1):
                digest = hashlib.sha256(
                    word[at:at + size].encode("utf-8")).hexdigest()
                if digest in names:
                    named.append(spot(label, text, m.start() + at))
check("the book spells out none of the forbidden names",
      bool(names) and not named,
      "%d names read from source_no_real_names, %d places: %s"
      % (len(names), len(named), "; ".join(named[:4]) or "none"))

# A link to the owner's session, artifact, repository or runs is theirs;
# where the page shows one it takes it from the data. The stylesheet it
# loads is the one link that is the page's own.
LINK = re.compile(r"https?://([^\s\"'<>()/]+)[^\s\"'<>()]*")
OWN_HOSTS = ("fonts.googleapis.com",)
links = []
for label, text in both:
    for m in LINK.finditer(text):
        if m.group(1) not in OWN_HOSTS:
            links.append("%s %s" % (spot(label, text, m.start()), m.group(0)))
check("the book writes no link but the font stylesheet", not links,
      "%d links besides %s: %s" % (len(links), "|".join(OWN_HOSTS),
                                   "; ".join(links[:4]) or "none"))

CARD = re.compile(r"(?<![A-Za-z0-9])E-\d+")
cards = []
for label, text in both:
    for m in CARD.finditer(text):
        cards.append("%s %s" % (spot(label, text, m.start()), m.group(0)))
check("the book names no card number", not cards,
      "%d of them: %s" % (len(cards), "; ".join(cards[:4]) or "none"))

# A day in either spelling the page and its data use: 27.9.2026 and
# 2026-09-27. A day stands for a moment of somebody's work.
DAY = re.compile(r"(?<![\d.])\d{1,2}\.\d{1,2}\.(?:19|20)\d\d(?!\d)"
                 r"|(?<!\d)(?:19|20)\d\d-\d\d-\d\d(?!\d)")
days = []
for label, text in both:
    for m in DAY.finditer(text):
        days.append("%s %s" % (spot(label, text, m.start()), m.group(0)))
check("the book carries no calendar day", not days,
      "%d of them: %s" % (len(days), "; ".join(days[:4]) or "none"))

# ---------------------------------------------------------------- 4.
print("\n4. No history")
log = re.search(r"const BUCH_LOG=(\[.*?\]);\n", page, re.S)
try:
    entries = json.loads(log.group(1)) if log else None
except ValueError:
    entries = None
count = len(entries) if isinstance(entries, list) else -1
first = entries[0].get("v") if count == 1 and isinstance(entries[0], dict) \
    else None
check("the book's change log holds one entry, v1",
      count == 1 and first == "v1",
      "%d entries (-1: not read as JSON), the first %r, wanted 1 and 'v1'"
      % (count, first))
version = re.search(r'const PAGE_VERSION="([^"]*)";', page)
check("the book's page is version v1",
      bool(version) and version.group(1) == "v1",
      "PAGE_VERSION %r, wanted 'v1'" % (version.group(1) if version else None))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
