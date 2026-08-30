# -*- coding: utf-8 -*-
"""The index has to point at sections that are really there.

A single style round can rename most of the headings of a chapter, in
both languages, and leave an index that names chapter and section
wrong in most of its entries with nothing turning red. So every entry
is looked up here: the chapter has to exist and the title has to stand
in it as a heading. The cheap questions live here too, because nothing
else reads the index. The index itself is a section of the manual's
README, not a file of its own, and it ships with every checkout: so
its absence is a defect here and not a machine that cannot check it.
"""
import collections
import io
import os
import re
import sys

# The titles reported are German on one side, and the suite runs under
# LC_ALL=C, where a finding that cannot be printed is a traceback.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "docs")
LINE_MAX = 79
MOST_PLACES = 3

bad = []


def check(what, ok, detail=""):
    print("  %-56s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


# Two places the index may stand: beside the chapter list in the
# manual's README, or in a file of its own. The first with entries wins.
PLACES = {"en": ["README.md", "register.md", "index.md"],
          "de": ["README.de.md", "register.de.md", "index.de.md"]}
# How a chapter name inside an entry becomes a file name.
SUFFIX = {"en": ".md", "de": ".de.md"}
# An entry: the keyword in bold, a colon, then where it points. The
# dashes are read as well, so an index that falls back to one turns red
# below instead of parsing as nothing and skipping the whole file.
ENTRY = re.compile(r"^\*\s+\*\*(.+?)\*\*\s*(:|\u2014|\u2013|--)\s+(\S.*)$")
# One place: the chapter in code font, a comma, the heading in quotes.
TARGET = [("\u201e",
           re.compile(r"^`([^`]+)`\s*,\s*\u201e(.+)\u201c$")),
          ("\"", re.compile(r"^`([^`]+)`\s*,\s*\"(.+)\"$"))]
# An entry that carries no place of its own and hands on to another.
SEE = re.compile(r"^(?:see|siehe)\s+(\S.*)$", re.I)
# Umlauts fold onto their base letter, the way German orders an index.
FOLD = {"\u00e4": "a", "\u00f6": "o", "\u00fc": "u", "\u00df": "ss",
        "\u00c4": "a", "\u00d6": "o", "\u00dc": "u"}


def normal(text):
    """A heading or a title, down to what a rename would change."""
    text = text.replace("\u2026", "...")
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[`*_]", "", text)
    text = text.strip().strip("#").strip()
    return " ".join(text.split()).lower()


def sort_key(word):
    """How an index is ordered: no case, no markup, umlauts folded."""
    word = re.sub(r"[`*_]", "", word).lower()
    word = "".join(FOLD.get(c, c) for c in word)
    return re.sub(r"^[^0-9a-z]+", "", word)


def places_of(tail):
    """The chapter and title pairs of one entry, None if it is none."""
    out = []
    for piece in tail.split(";"):
        piece = piece.strip()
        for quote, pattern in TARGET:
            hit = pattern.match(piece)
            if hit:
                out.append((hit.group(1), hit.group(2), quote))
                break
        else:
            return None
    return out or None


def entry_of(line):
    """The match of one list item, if it reads as an index entry."""
    hit = ENTRY.match(line)
    if hit and (places_of(hit.group(3)) or SEE.match(hit.group(3))):
        return hit
    return None


def list_items(text):
    """The list items of a document, each folded onto one line."""
    out, live = [], False
    for number, raw in enumerate(text.splitlines(), 1):
        if raw.startswith("* "):
            out.append([number, raw.strip()])
            live = True
        elif live and raw.startswith("  ") and raw.strip():
            out[-1][1] += " " + raw.strip()
        else:
            live = False
    return out


def read_index(lang):
    """The index of one language: its file, its lines, its entries."""
    for name in PLACES[lang]:
        path = os.path.join(DOCS, name)
        if not os.path.exists(path):
            continue
        text = io.open(path, encoding="utf-8").read()
        items = list_items(text)
        entries = []
        for number, line in items:
            hit = entry_of(line)
            if hit:
                entries.append((number, hit))
        # Five tells an index from a stray list item and still catches
        # one that is only half written.
        if len(entries) >= 5:
            return path, text.splitlines(), items, entries
    return None, [], [], []


HEADINGS = {}


def headings_of(path):
    """Every heading of one chapter, normalised."""
    if path not in HEADINGS:
        found = set()
        for line in io.open(path, encoding="utf-8"):
            if line.startswith("#"):
                found.add(normal(line))
        HEADINGS[path] = found
    return HEADINGS[path]


print("1. Where the index stands")
books = {}
for lang in ("en", "de"):
    books[lang] = read_index(lang)
    path, lines, items, entries = books[lang]
    print("  %-4s %s" % (lang, "%s, %d entries" % (
        os.path.relpath(path, ROOT), len(entries)) if path else "none yet"))

# Red, not a skip. A skip says "this machine could not"; the index is
# a shipped part of the manual, so gone it is a defect, and a skip
# would also spend the one the suite allows.
check("an index was found at all",
      bool(books["en"][0]) or bool(books["de"][0]),
      "none of %s holds five entries" % ", ".join(
          PLACES["en"] + PLACES["de"]))

check("the index stands in both languages",
      bool(books["en"][0]) and bool(books["de"][0]),
      "missing: %s" % [lang for lang in ("en", "de") if not books[lang][0]])

counted, pointers, into = {}, {}, {}
for lang in ("en", "de"):
    path, lines, items, entries = books[lang]
    if not path:
        continue
    print("\n2%s. The %s index, %s" % (
        "ab"[lang == "de"], lang, os.path.relpath(path, ROOT)))
    first, last = entries[0][0], entries[-1][0]
    keys = [hit.group(1) for _, hit in entries]

    # A list item between the first and the last entry that does not
    # read as one is broken. Nothing outside that span is looked at, so
    # the chapter list in the same file stays out.
    broken = [(n, line[:52]) for n, line in items
              if first <= n <= last and not entry_of(line)]
    check("%s: every line of the index reads as an entry" % lang,
          not broken, "%d, first at line %s" % (
              len(broken), broken[0][0] if broken else "-"))
    for number, line in broken[:6]:
        print("      line %d: %s" % (number, line))

    wanted = []
    for number, hit in entries:
        for chapter, title, quote in places_of(hit.group(3)) or []:
            wanted.append((number, hit.group(1), chapter, title, quote))

    pointers[lang] = sum(1 for _, hit in entries
                         if SEE.match(hit.group(3)))
    counted[lang] = len(keys) - pointers[lang]
    into[lang] = collections.Counter(c for _, _, c, _, _ in wanted)

    absent = [(n, key, chapter) for n, key, chapter, _, _ in wanted
              if not os.path.exists(
                  os.path.join(DOCS, chapter + SUFFIX[lang]))]
    check("%s: every entry names a chapter that is there" % lang,
          not absent, "%d, first: %s -> %s" % (
              len(absent), absent[0][1] if absent else "-",
              absent[0][2] if absent else "-"))
    for number, key, chapter in absent[:6]:
        print("      line %d: %s -> no chapter %s%s"
              % (number, key, chapter, SUFFIX[lang]))

    misses = []
    for number, key, chapter, title, _ in wanted:
        chapter_file = os.path.join(DOCS, chapter + SUFFIX[lang])
        if not os.path.exists(chapter_file):
            continue
        if normal(title) not in headings_of(chapter_file):
            misses.append((number, key, chapter, title))
    check("%s: every entry names a heading that is there" % lang,
          not misses, "%d of %d places, first: %s -> %s, \"%s\"" % (
              len(misses), len(wanted),
              misses[0][1] if misses else "-",
              misses[0][2] if misses else "-",
              misses[0][3] if misses else "-"))
    for number, key, chapter, title in misses[:10]:
        print("      line %d: %s -> %s%s has no heading \"%s\""
              % (number, key, chapter, SUFFIX[lang], title))

    seen, twice = set(), []
    for key in keys:
        if sort_key(key) in seen:
            twice.append(key)
        seen.add(sort_key(key))
    check("%s: no keyword stands twice" % lang, not twice, str(twice[:3]))

    # Two orderings, one with the spaces and one without: a pair is
    # only out of order when it is out of order under both.
    tumbles = [(a, b) for a, b in zip(keys, keys[1:])
               if sort_key(a) > sort_key(b)
               and sort_key(a).replace(" ", "") > sort_key(b).replace(" ", "")]
    check("%s: the keywords are in order" % lang, not tumbles,
          "%d, first: %s before %s" % (
              len(tumbles), tumbles[0][0] if tumbles else "-",
              tumbles[0][1] if tumbles else "-"))

    known = [sort_key(k) for k in keys]
    lost = []
    for number, hit in entries:
        pointer = SEE.match(hit.group(3))
        if pointer and not any(
                k.startswith(sort_key(pointer.group(1))) for k in known):
            lost.append((number, hit.group(1), pointer.group(1)))
    check("%s: every cross reference leads to a keyword" % lang,
          not lost, str(lost[:2]))

    crowded = [hit.group(1) for _, hit in entries
               if len(places_of(hit.group(3)) or []) > MOST_PLACES]
    check("%s: no entry names more than %d places" % (lang, MOST_PLACES),
          not crowded, str(crowded[:3]))

    marks = sorted(set(hit.group(2) for _, hit in entries))
    check("%s: a colon separates keyword and place" % lang,
          marks == [":"], str(marks))
    # Exactly one, not "at most one": an index whose entries all hand on
    # to another keyword has no place in it at all, and no quote form.
    quotes = sorted(set(quote for _, _, _, _, quote in wanted))
    check("%s: one quote form throughout" % lang, len(quotes) == 1,
          "%d forms %s over %d places" % (len(quotes), quotes, len(wanted)))

    over = [n for n in range(first, last + 1)
            if len(lines[n - 1]) > LINE_MAX]
    check("%s: no line of the index over %d characters" % (lang, LINE_MAX),
          not over, "%d, first at line %s" % (
              len(over), over[0] if over else "-"))

    # A chapter nobody can reach through the index is a hole in it, and
    # what the index itself may stand in is no chapter.
    chapters = set(name[:-len(SUFFIX[lang])] for name in os.listdir(DOCS)
                   if name.endswith(SUFFIX[lang])
                   and name not in PLACES[lang]
                   and (lang == "de" or not name.endswith(".de.md")))
    reached = set(chapter for _, _, chapter, _, _ in wanted)
    check("%s: every chapter is reachable through the index" % lang,
          not chapters - reached, str(sorted(chapters - reached)))

print("\n3. The two indexes beside each other")
print("  keywords %s, cross references %s"
      % (sorted(counted.items()), sorted(pointers.items())))
check("both languages hold the same number of keywords",
      len(counted) == 2 and len(set(counted.values())) == 1,
      str(sorted(counted.items())))

# The titles differ by language, the chapters do not. A keyword that
# fell out of one side shows up as a chapter that side points at less
# often, even where a cross reference makes the counts above come out
# even. That is why the sides are not compared line for line.
apart = []
if len(into) == 2:
    for chapter in sorted(set(into["en"]) | set(into["de"])):
        if into["en"][chapter] != into["de"][chapter]:
            apart.append("%s: en %d, de %d" % (
                chapter, into["en"][chapter], into["de"][chapter]))
check("both point into each chapter equally often",
      len(into) == 2 and not apart, str(apart[:3]))

print()
if bad:
    print("FAIL: %d of the checks" % len(bad))
    sys.exit(1)
# What was read, not only that it went well: an index that shrank to
# four entries would otherwise report the same "All good." as a whole one.
print("All good -- %s entries read."
      % ", ".join("%s %d" % (lang, len(books[lang][3]))
                  for lang in ("en", "de")))
