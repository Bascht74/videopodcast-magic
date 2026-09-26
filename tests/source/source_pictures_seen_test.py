# -*- coding: utf-8 -*-
"""Every picture under docs/images was looked at in the bytes it has now.

docs/images/seen.tsv holds one row per picture: file, sha256, date, and
what it shows, written by whoever looked. In order: the record reads, a
row per file; every picture git holds or would take has a row with its
current sum; no row names a picture that is gone; and every row says
what it shows. The sum proves the bytes were the ones seen, never that
the line in the last field is true -- that stays a person's word.
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
import hashlib
import re
import subprocess
import time

ROOT = os.path.dirname(HERE)
IMAGES = os.path.join(ROOT, "docs", "images")
RECORD = os.path.join(IMAGES, "seen.tsv")
PICTURE = re.compile(r"\.(png|jpe?g|gif|svg|webp)$", re.I)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def git_names(*words):
    """The names git lists under docs/images, or None without git."""
    try:
        got = subprocess.run(["git", "-C", ROOT, "ls-files", "-z"]
                             + list(words) + ["--", "docs/images"],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL)
    except OSError:
        return None
    if got.returncode != 0:
        return None
    return [p for p in got.stdout.decode("utf-8").split("\0") if p]


# ---------------------------------------------------------------- 1.
print("1. What is read: the pictures git holds or would take, the record")
# git, not the folder: what it holds is what a push carries, and a
# picture copied in but not yet added is one `git add` from the same.
held = git_names()
loose = git_names("--others", "--exclude-standard")
if not held:
    print("SKIPPED: no git here -- this asks the repository which pictures "
          "it ships; run it in a checkout, or a clone with git add -A")
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("Good as far as it went -- nothing ran.")
    sys.exit(0)
pictures = {}
for rel in sorted(set(held) | set(loose or [])):
    path = os.path.join(ROOT, rel)
    if PICTURE.search(rel) and os.path.isfile(path):
        with open(path, "rb") as f:
            pictures[rel[len("docs/images/"):]] = hashlib.sha256(
                f.read()).hexdigest()
rows, torn = {}, []
twice = []
try:
    with open(RECORD, encoding="utf-8") as f:
        lines = f.read().splitlines()
except OSError as why:
    lines, torn = [], ["cannot read docs/images/seen.tsv: %s" % why]
for number, line in enumerate(lines, 1):
    if not line.strip() or line.startswith("#"):
        continue
    fields = line.split("\t")
    if len(fields) != 4:
        torn.append("line %d has %d fields, not 4" % (number, len(fields)))
        continue
    if fields[0] in rows:
        twice.append(fields[0])
    rows[fields[0]] = fields
check("seen.tsv reads, four tab fields on every row", not torn,
      "%d rows read; %s" % (len(rows), "; ".join(torn[:3]) or "none torn"))
check("seen.tsv names each picture on one row only", not twice,
      "named twice: %s" % (", ".join(twice) or "none"))

# ---------------------------------------------------------------- 2.
print("\n2. Every picture was seen in the bytes it has now")
unseen = []
for name in sorted(pictures):
    recorded = rows.get(name, [None, "no row"])[1]
    if recorded != pictures[name]:
        unseen.append("%s: now %s, seen.tsv %s" % (name, pictures[name],
                                                   recorded))
check("every picture has a seen row with its current sha256", not unseen,
      "%d of %d pictures unseen -- %s; look at each, then python3 "
      "development/seen_rows.py" % (len(unseen), len(pictures),
                                    "; ".join(unseen) or "none"))

# ---------------------------------------------------------------- 3.
print("\n3. No row stands for a picture that is gone")
gone = sorted(set(rows) - set(pictures))
check("no seen row names a picture that is no longer there", not gone,
      "rows without a picture: %s" % (", ".join(gone) or "none"))

# ---------------------------------------------------------------- 4.
print("\n4. Every row says what the picture shows")
blank = sorted(n for n, f in rows.items() if not f[3].strip())
check("every seen row says what the picture shows", not blank,
      "empty last field: %s -- a person writes it after looking"
      % (", ".join(blank) or "none"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
