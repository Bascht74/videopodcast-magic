# -*- coding: utf-8 -*-
"""Nothing off a real production and nobody's name is in a shipped file.

The sections in the order they come: what was read -- everything git
names, which is exactly what becomes public; paths off somebody's
machine; a day in a file name that is not the demo day; the words these
productions were named with, where a file name is built; and the names
of people, which stand here hashed, because a check may not write down
what it forbids.

The limit of the method: a path is held against the machine the test
runs on, so a path off another disc is caught by whoever runs the suite
there. A hashed name cannot be read out of this file, but it can be
guessed and confirmed -- see the note at section 5. Nothing here reads
a picture, and nothing here knows a village from an invented word --
see the note at section 4.
"""
import hashlib
import io
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SELF = "tests/" + os.path.basename(__file__)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def spot(path, text, at):
    """Where a find sits, the way a person opens it: path:line."""
    return "%s:%d" % (path, text.count("\n", 0, at) + 1)


def line_at(text, at):
    """The whole line a find sits on, so section 5 can read it."""
    start = text.rfind("\n", 0, at) + 1
    end = text.find("\n", at)
    return text[start:] if end < 0 else text[start:end]


OWN = os.path.basename(__file__)[:-len("_test.py")]


def readable(path, text):
    """One file's text, minus this check's own rows in the register.

    The register ships like everything else, and a counter-proof's red
    line has to carry word for word the thing the check forbids -- or it
    proves nothing. Those rows and no others are blanked, the lines
    themselves left standing so that a find still names the line a
    person opens. Every other row is read and judged; the one that
    carried a real disc path was found in exactly this file.
    """
    if os.path.basename(path) != "counterproof":
        return text
    return "\n".join("" if line.startswith(OWN + "\t") else line
                     for line in text.split("\n"))


# ---------------------------------------------------------------- 1.
print("1. What is read: everything the repository ships")
# git, not the folder: what git names is what a clone gets and what
# stands on GitHub, and that is the whole question here. A file lying
# about untracked is nobody's business; docs/notes/ is untracked on
# purpose and holds material from real productions.
try:
    listed = subprocess.run(("git", "-C", ROOT, "ls-files", "-z"),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)
    named = [p for p in listed.stdout.decode("utf-8").split("\0") if p] \
        if listed.returncode == 0 else []
except OSError:
    named = []
if not named:
    print("SKIPPED: no git here -- this asks the repository what it ships, "
          "and a folder cannot answer it")
    sys.exit(0)
texts, binary = {}, 0
for path in named:
    try:
        texts[path] = readable(path, io.open(os.path.join(ROOT, path),
                                             encoding="utf-8").read())
    except (OSError, UnicodeDecodeError):
        binary += 1          # a picture, a font: nothing to read words in
check("the repository could be read", len(texts) > 100,
      "%d files read of %d git names, %d not text" % (len(texts),
                                                      len(named), binary))

# ---------------------------------------------------------------- 2.
print("\n2. Paths off somebody's machine")
# A pattern and not a list, and it does not go stale: these four roots
# are where a personal tree begins on the three systems the program
# runs on. /tmp is deliberately not among them -- it is where everything
# here is allowed to live, and it names nobody.
MACHINE = re.compile(r"(?:/Volumes/|/Users/|/home/|[A-Za-z]:\\Users\\)"
                     r"[A-Za-z0-9._%$~+-]+(?:[/\\][A-Za-z0-9._%$~+-]+)*")
# What tells a teaching example from a leak is not how the path looks --
# /Users/x/Desktop and /Users/someone/Desktop look alike -- but
# whether it names something that is really there. A path a test invents
# to explain a rule exists nowhere; a path that came off a disc exists
# on that disc. The repository's own place and the home folder are
# always refused, because no shipped file has any business knowing where
# this clone happens to lie.
ALWAYS = [p for p in (os.path.abspath(ROOT), os.path.expanduser("~"))
          if p and p not in ("/", os.sep)]
real = []
for path in sorted(texts):
    if path == SELF:
        continue             # this file carries the patterns themselves
    for m in MACHINE.finditer(texts[path]):
        found = m.group(0)
        if os.path.exists(found) or any(found.startswith(p) for p in ALWAYS):
            real.append("%s %s" % (spot(path, texts[path], m.start()), found))
check("no shipped file names a path that is really on this machine",
      not real, "%d of them: %s" % (len(real), "; ".join(real[:4]) or "none"))

# ---------------------------------------------------------------- 3.
print("\n3. A day in a file name that is not the demo day")
# A camera writes the day and the time of day into every clip, and that
# is the identifying half of the name -- the shoot happened, on that
# day. The demo material is stamped 1 January on purpose, so a pattern
# is enough here and no list is needed: eight digits that read as a
# month and a day and a time, and the month and day are not 01-01.
DAY = re.compile(r"(?<![0-9])(\d{2})(\d{2})([0-2]\d)([0-5]\d)(?![0-9])")
DEMO = "0101"
days = []
for path in sorted(texts):
    if path == SELF:
        continue
    for m in DAY.finditer(texts[path]):
        month, day = int(m.group(1)), int(m.group(2))
        if not (1 <= month <= 12 and 1 <= day <= 31):
            continue         # eight digits that are not a day at all
        if m.group(0)[:4] == DEMO:
            continue
        days.append("%s %s" % (spot(path, texts[path], m.start()),
                               m.group(0)))
check("every day stamped into a name is the demo day", not days,
      "%d against %s: %s" % (len(days), DEMO, "; ".join(days[:4]) or "none"))

# ---------------------------------------------------------------- 4.
print("\n4. The words these productions were named with")
# Here a list cannot be avoided, and it is worth saying why rather than
# pretending otherwise: no pattern tells a village from an invented
# word, and the only thing that marks these names is that they are
# German -- the productions are. So the list holds the German role
# words, which name a part and not a person or a place, and it is the
# memory of what has already gone out. What catches the next case is
# sections 2 and 3, which need no list at all.
#
# And the list stays small for a second reason: a check that names the
# real names publishes them. A village, a person, a production number
# would have to be written down here to be forbidden here, in the file
# that ships. So those are kept out of the source and handed to a person
# instead.
LEAKED = ("Kandidat", "Moderatorin", "Moderatoren", "Moderator", "Totale",
          "Gast")
# Only where a file name is built. The same words are honest German in a
# German chapter -- "Totale" is what a wide shot is called, "Moderatoren"
# is what two presenters are -- and a check that reddened at those would
# be switched off within the week. A word followed by an underscore or
# by a media suffix is a file name and nothing else.
NAMED = re.compile(r"(?<![A-Za-z])(?:%s)"
                   r"(?:_[A-Za-z0-9]|\.(?:mov|mp4|m4a|mkv|mxf|wav|aac))"
                   % "|".join(LEAKED))
words = []
for path in sorted(texts):
    if path == SELF:
        continue
    for m in NAMED.finditer(texts[path]):
        words.append("%s %s" % (spot(path, texts[path], m.start()),
                                m.group(0)))
check("no file name is built out of one of them", not words,
      "%d of %d words, %s: %s" % (len(words), len(LEAKED),
                                  "|".join(LEAKED),
                                  "; ".join(words[:4]) or "none"))

# ---------------------------------------------------------------- 5.
print("\n5. The names of people")
# A check that forbids a name may not write the name down. This file
# ships like every other, so a list of forbidden names would put them
# in the repository -- in the one file that forbids them. So the list
# holds sha256 over the word in lower case, and the repository's own
# words are hashed to meet it. Nothing here can be read back.
#
# What that is worth, so that nobody takes it for more: a hash cannot
# be read, but it can be guessed. Whoever suspects a name hashes it and
# compares. The purpose is that the name is not legible here, not that
# it is secret -- for a secret, a public repository is the wrong place.
#
# To add a name, and nothing else about this has to be understood:
#
#   python3 -c "from hashlib import*;print(sha256(b'name').hexdigest())"
#
# Measure the word first, because a short one is a syllable and not a
# name: in this repository "ann" stands in 3230 places and "mark" in
# 1566 (measured 1.9.2026), and either would report a heap of places
# that name nobody. SHORTEST is a floor and not a promise -- it holds
# the number of pieces down, it does not make four letters a name.
NAMES = (
    "4dd68e2ab3a30973318ea903e088b3d3480655ef4236109fe47272c1c1582880",
    "0456e50086d924490738f5b2e58218eeb54b36b0bc47511a1d52835f408d7a8c",
)
SHORTEST = 4
# Not whole words: a first name and a surname are written as one in an
# account name, a German ending is stuck on the back of a first name,
# and in an address the name stands in front of the @. So every run of
# letters is cut into every piece of SHORTEST letters and more, and each
# piece is hashed -- 147000 of them here, a tenth of a second (1.9.2026).
WORD = re.compile(r"[^\W\d_]+")
words = set()
for path in sorted(texts):
    words.update(WORD.findall(texts[path].lower()))
cand = set()
for word in words:
    for size in range(SHORTEST, len(word) + 1):
        for at in range(len(word) - size + 1):
            cand.add(word[at:at + size])
check("there is a name to look for and there are words to look in",
      bool(NAMES) and bool(cand),
      "%d names against %d pieces of %d letters or more out of %d words"
      % (len(NAMES), len(cand), SHORTEST, len(words)))
hits = set(piece for piece in cand
           if hashlib.sha256(piece.encode("utf-8")).hexdigest() in NAMES)
# This file is not exempt from its own section, unlike sections 2 to 4:
# those carry the patterns they forbid, this one carries no name. A
# copyright notice is the one place a name belongs -- the licence names
# the holder, in LICENSE and in the box the program shows -- and it is
# taken as read there, on that line and nowhere else.
#
# The find is never printed, only where it stands. A counter-proof's red
# line goes into tests/state/counterproof word for word, and the
# register ships too; a line naming the name would leak it there.
places = []
for path in sorted(texts):
    low = texts[path].lower()
    at_all = []
    for piece in hits:
        at = low.find(piece)
        while at >= 0:
            at_all.append(at)
            at = low.find(piece, at + 1)
    for at in sorted(at_all):
        if "opyright" not in line_at(texts[path], at):
            places.append(spot(path, texts[path], at))
check("no shipped file spells out one of the names", not places,
      "%d of them against %d names: %s" % (len(places), len(NAMES),
                                           "; ".join(places[:4]) or "none"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
