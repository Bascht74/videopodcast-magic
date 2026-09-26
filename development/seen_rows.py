# -*- coding: utf-8 -*-
"""Prints the rows docs/images/seen.tsv still owes, the last field empty.

Every picture under docs/images that git holds or would take, and whose
current sha256 has no row, gets one line: file, sum, today, and nothing
after the last tab. Whoever looked at the picture writes what it shows
there and puts the row in place of the old one. This never writes the
file and never fills that field: a row a machine wrote proves nobody
looked, and tests/source/source_pictures_seen_test.py refuses it.

    python3 development/seen_rows.py
"""
import datetime
import hashlib
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES = os.path.join(ROOT, "docs", "images")
PICTURE = re.compile(r"\.(png|jpe?g|gif|svg|webp)$", re.I)


def listed(*words):
    """What git names under docs/images, held and not yet added."""
    got = subprocess.run(["git", "-C", ROOT, "ls-files", "-z"] + list(words)
                         + ["--", "docs/images"],
                         stdout=subprocess.PIPE, check=True)
    return [p for p in got.stdout.decode("utf-8").split("\0") if p]


def seen():
    """The sums seen.tsv already holds, by file."""
    sums = {}
    try:
        with open(os.path.join(IMAGES, "seen.tsv"), encoding="utf-8") as f:
            for line in f.read().splitlines():
                fields = line.split("\t")
                if not line.startswith("#") and len(fields) >= 2:
                    sums[fields[0]] = fields[1]
    except OSError:
        pass
    return sums


def main():
    """Prints one row per picture whose bytes nobody has recorded yet."""
    today = datetime.date.today().isoformat()
    held = seen()
    owed = 0
    names = set(listed()) | set(listed("--others", "--exclude-standard"))
    for rel in sorted(names):
        path = os.path.join(ROOT, rel)
        if not (PICTURE.search(rel) and os.path.isfile(path)):
            continue
        name = rel[len("docs/images/"):]
        with open(path, "rb") as f:
            now = hashlib.sha256(f.read()).hexdigest()
        if held.get(name) != now:
            print("%s\t%s\t%s\t" % (name, now, today))
            owed += 1
    print("%d rows owed -- look at each picture, write what it shows after "
          "the last tab, replace its old row" % owed, file=sys.stderr)


if __name__ == "__main__":
    main()
