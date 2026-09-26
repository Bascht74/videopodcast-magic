# -*- coding: utf-8 -*-
"""The repository and the name a person reads are each written out once.

In order: the repository's account is spelled only where REPOSITORY is
set; the display name only where DISPLAY_NAME is set, texts through T()
included; no catalogue spells the display name out; and every language
keeps the placeholder where the English carries it. The limits: a
docstring is spared, the account is matched with its capitals, so the
frozen bundle identifier is not seen, and the needles are today's.
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
import glob
import io
import time

import the_program

began = time.time()
vpm = the_program.load()
vpm.set_language("en")
# The account, not the whole address: two literals side by side were
# how the address stood, and one of them alone holds only the account.
ACCOUNT = vpm.REPOSITORY.split("/")[0]
NAME = vpm.DISPLAY_NAME
PLACEHOLDER = "%(name)s"

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def spelled(needle, setter):
    """Every string in the program holding *needle*, bar the one setting it.

    A docstring is spared: it is read by nobody who runs the program.
    """
    loose = []
    for folder, _dirs, files in os.walk(the_program.FOLDER):
        for leaf in sorted(files):
            if not leaf.endswith(".py"):
                continue
            path = os.path.join(folder, leaf)
            with io.open(path, encoding="utf-8") as f:
                tree = ast.parse(f.read())
            spared = set()
            for n in ast.walk(tree):
                body = getattr(n, "body", None)
                if isinstance(body, list) and body \
                        and isinstance(body[0], ast.Expr) \
                        and isinstance(body[0].value, ast.Constant):
                    spared.add(id(body[0].value))
                if isinstance(n, ast.Assign) and any(
                        isinstance(t, ast.Name) and t.id == setter
                        for t in n.targets):
                    spared.add(id(n.value))
            for n in ast.walk(tree):
                if isinstance(n, ast.Constant) and isinstance(n.value, str) \
                        and needle in n.value and id(n) not in spared:
                    loose.append("%s:%d %r" % (
                        os.path.relpath(path, the_program.FOLDER), n.lineno,
                        n.value[:40]))
    return loose


print("1. The repository")
loose = spelled(ACCOUNT, "REPOSITORY")
check("the repository is spelled out only where REPOSITORY is set",
      not loose, "%d loose: %s" % (len(loose), "; ".join(loose[:6])))

print("\n2. The name a person reads")
loose = spelled(NAME, "DISPLAY_NAME")
check("the display name is spelled out only where DISPLAY_NAME is set",
      not loose, "%d loose: %s" % (len(loose), "; ".join(loose[:6])))

print("\n3. The catalogues")
catalogues = sorted(glob.glob(os.path.join(the_program.FOLDER, "language",
                                           "*.po")))
written = []
dropped = []
named = 0
for path in catalogues:
    leaf = os.path.basename(path)
    for key, value, at in the_program.po_pairs(path):
        if NAME in key or NAME in value:
            written.append("%s:%d %r" % (leaf, at, (value or key)[:40]))
        if PLACEHOLDER in key:
            named += 1
            if value and PLACEHOLDER not in value:
                dropped.append("%s:%d %r" % (leaf, at, value[:40]))
check("no catalogue spells the display name out",
      catalogues and not written,
      "%d catalogues, %d entries spell it: %s"
      % (len(catalogues), len(written), "; ".join(written[:4])))
check("every language keeps the name's placeholder",
      named > 0 and not dropped,
      "%d entries carry %s in English, %d translations drop it: %s"
      % (named, PLACEHOLDER, len(dropped), "; ".join(dropped[:4])))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
