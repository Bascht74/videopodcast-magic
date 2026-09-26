# -*- coding: utf-8 -*-
"""requirements.txt and pyproject.toml name the same packages.

pip3 installs by pyproject.toml, and whoever prepares an environment by
hand installs by requirements.txt; a package on one list only is missing
on one of the two roads. In order: each list is found and names
something, then both directions. Names are compared as pip compares
them -- case, dots, dashes and underscores alike -- and versions,
extras and markers are left out: the limit is that only the names are
held.
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
# The lists are the repository's, whatever folder is being measured: a
# snapshot under VPM_SCRIPT carries neither of them.
NEEDS = os.path.join(the_program.ROOT, "requirements.txt")
POM = os.path.join(the_program.ROOT, "pyproject.toml")
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


print("1. Each list is found and names something")
needed = set()
for line in io.open(NEEDS, encoding="utf-8"):
    line = line.split("#", 1)[0].strip()
    # An option such as -r or --index-url names no package.
    if line and not line.startswith("-"):
        found = NAME.match(line)
        if found:
            needed.add(as_pip_reads(found.group(0)))
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
check("pyproject.toml's dependencies are found and name packages",
      len(listed) > 1,
      "%d name(s) under \"dependencies = [\" in %s, wanted more than one"
      % (len(listed), os.path.basename(POM)))
check("requirements.txt names packages", len(needed) > 1,
      "%d name(s) in %s, wanted more than one"
      % (len(needed), os.path.basename(NEEDS)))

print("\n2. Both directions")
only_needs = sorted(needed - listed)
only_pom = sorted(listed - needed)
check("every package requirements.txt names is in pyproject.toml",
      not only_needs,
      "only in requirements.txt: %s; pyproject.toml names %s"
      % (only_needs, sorted(listed)))
check("and every pyproject.toml package is in requirements.txt",
      not only_pom,
      "only in pyproject.toml: %s; requirements.txt names %s"
      % (only_pom, sorted(needed)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
