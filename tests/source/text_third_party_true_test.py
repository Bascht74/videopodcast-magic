# -*- coding: utf-8 -*-
"""THIRD-PARTY.md names exactly the packages pip installs with the program.

pip3 installs what pyproject.toml's dependencies name, and
THIRD-PARTY.md says what that is and under which licence; a package
added there and not here is installed on every machine without a word
about its terms. In order: both lists are found and name something,
then both directions. Only the rows under "## Installed with it" are
held -- what is pulled in, started or used by the tests stands under
headings of its own and is not compared. Names are compared as pip
compares them; the licences beside them are not judged.
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
import io
import re
import time

import the_program

began = time.time()
# Both are the repository's, whatever folder is being measured: a
# snapshot under VPM_SCRIPT carries neither. VPM_THIRD_PARTY and
# VPM_PYPROJECT point at other copies, for the counter-proof.
PAPER = os.environ.get("VPM_THIRD_PARTY") \
    or os.path.join(the_program.ROOT, "THIRD-PARTY.md")
POM = os.environ.get("VPM_PYPROJECT") \
    or os.path.join(the_program.ROOT, "pyproject.toml")
HEADING = "## Installed with it"
# The front of a requirement: what stands before a version, an extra or
# a marker.
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def as_pip_reads(name):
    """A package name the way pip compares it (PEP 503)."""
    return re.sub(r"[-_.]+", "-", name).lower()


print("1. Both lists are found and name something")
# A row is two spaces and a name; the lines that carry a description
# on stand further in and name nothing.
named = set()
inside = False
for line in io.open(PAPER, encoding="utf-8"):
    line = line.rstrip("\n")
    if line.startswith("## "):
        inside = line.strip() == HEADING
        continue
    found = NAME.match(line[2:]) if inside and line.startswith("  ") \
        and not line.startswith("   ") else None
    if found:
        named.add(as_pip_reads(found.group(0)))
# The comments come off each line before the quotes are read: a
# comment inside the list quotes a command of its own. The list ends at
# the first bracket outside the quotes; one inside names an extra.
listed = set()
whole = io.open(POM, encoding="utf-8").read()
start = re.search(r"^dependencies\s*=\s*\[", whole, re.M)
ended = False
for line in whole[start.end():].splitlines() if start else ():
    for spec, close in re.findall(r'"([^"]*)"|(\])', line.split("#", 1)[0]):
        ended = ended or bool(close)
        found = None if ended else NAME.match(spec.strip())
        if found:
            listed.add(as_pip_reads(found.group(0)))
    if ended:
        break
check("THIRD-PARTY.md lists packages under its install heading",
      len(named) > 1,
      "%d name(s) under \"%s\" in %s, wanted more than one"
      % (len(named), HEADING, os.path.basename(PAPER)))
check("pyproject.toml's dependencies are found and name packages",
      len(listed) > 1,
      "%d name(s) under \"dependencies = [\" in %s, wanted more than one"
      % (len(listed), os.path.basename(POM)))

print("\n2. Both directions")
unnamed = sorted(listed - named)
stale = sorted(named - listed)
check("every dependency pip installs is named in THIRD-PARTY.md",
      not unnamed,
      "missing from THIRD-PARTY.md: %s; it names %s"
      % (unnamed, sorted(named)))
check("and THIRD-PARTY.md names no package pip no longer installs",
      not stale,
      "in THIRD-PARTY.md but not in pyproject.toml: %s; pyproject names %s"
      % (stale, sorted(listed)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
