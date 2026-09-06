# -*- coding: utf-8 -*-
"""Every folder the program reads out of is on pip's list, and no other.

The program fetches each piece with beside("<name>"), and setuptools
ships packages and leaves a stray folder lying, so a folder pip was
never told about is simply missing from an installed copy. In order:
the list is read out of pyproject.toml at all; the program and every
folder any piece fetches stand on it; no name on it is without a
piece; and no folder of the program is fetched by nobody -- the last
is what falls the day this search is narrowed back to the way in. The
limit: a piece reached otherwise than by beside() shows as unfetched.
"""
import ast
import io
import os
import re
import sys
import time

import the_program

began = time.time()
FOLDER = the_program.FOLDER
# The list is the repository's, whatever folder is being measured: what
# pip would ship is a property of this checkout, and a snapshot under
# VPM_SCRIPT carries no pyproject.toml of its own.
POM = os.path.join(the_program.ROOT, "pyproject.toml")
# The name pip installs the program under. Every piece is a name below
# it, so the two are held together rather than one by one.
PACKAGE = "videopodcast_magic"
# What a name on the list has to have behind it to be a package at all.
# setuptools ships Python out of a package; a folder without this is
# not one, and naming it ships nothing.
PIECE = "__init__.py"

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# ------------------------------------------------------ what pip is told
print("1. The list pip installs by")
whole = io.open(POM, encoding="utf-8").read()
# From the key to the closing bracket, not the first line: the list is
# longer than one line, and reading only the first would call every
# name below it missing. "packages =" and not "packages", because the
# word itself stands in the reasoning written above the list.
row = ""
if "packages =" in whole:
    rest = whole.split("packages =", 1)[1]
    row = rest.split("]", 1)[0] if "]" in rest else rest
listed = sorted(set(re.findall(r'"([A-Za-z0-9_.]+)"', row)))
check("the list pip installs by is read out of pyproject.toml",
      len(listed) > 1,
      "%d name(s) between \"packages =\" and the closing bracket of %s, "
      "wanted more than one" % (len(listed), os.path.basename(POM)))

# ------------------------------------------------- what the program reads
print("\n2. Both directions between the list and the folders")
# Every beside() call in every piece, and not in the way in alone: five
# of the folders are fetched from inside ui/ and one from inside
# fittings/, so a search that reads the way in only sees none of them.
#
# A call and not an assignment: `beside = PROGRAM.beside` binds the
# name at the head of two pieces, and `beside = file_path + ".new"` is
# a local in a third. Both are Assign nodes and neither is a Call, so
# an ast walk tells them apart where a grep for "beside(" cannot.
# PROGRAM.beside("x") is taken too, though nothing writes it that way
# today: it is the same call under another spelling.
calls = []
for piece, body in the_program.pieces():
    for node in ast.walk(ast.parse(body)):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        named = (isinstance(node.func, ast.Name)
                 and node.func.id == "beside") \
            or (isinstance(node.func, ast.Attribute)
                and node.func.attr == "beside")
        if not named:
            continue
        first = node.args[0]
        told = first.value if isinstance(first, ast.Constant) \
            and isinstance(first.value, str) else None
        calls.append((piece, node.lineno, told))
# Where each folder is fetched, so a failing line can point at a place
# somebody can open. The first call in file order, sorted, so the same
# checkout always names the same one.
places = {}
for piece, line, told in sorted(calls):
    if told and os.path.isdir(os.path.join(FOLDER, told)):
        places.setdefault(told, "%s line %d" % (piece, line))

wanted = [(PACKAGE, "the folder every piece lies in")]
wanted += [("%s.%s" % (PACKAGE, name), places[name])
           for name in sorted(places)]
short = ["%s (%s)" % (name, where)
         for name, where in wanted if '"%s"' % name not in row]
# No floor under the number of folders here, although a search that
# found none would leave this green over a list of one. That case is
# the third check's, which names the folders nobody fetched; a floor
# here would say the same thing a line at a time and in numbers that
# read as though pip were at fault.
check("the program and each folder it fetches are on pip's list",
      not short,
      "%d beside() call(s) in %d piece(s) name %d folder(s), %d of those "
      "%d names not in packages: %s"
      % (len(calls), len(set(one for one, _l, _t in calls)), len(places),
         len(short), len(wanted), short or "none"))

# And the other way: a name on the list with nothing behind it ships
# nothing, and a renamed folder leaves exactly that.
stray = []
for name in listed:
    if name == PACKAGE:
        under = ""
    elif name.startswith(PACKAGE + "."):
        under = name[len(PACKAGE) + 1:].replace(".", os.sep)
    else:
        stray.append("%s (not a name under %s)" % (name, PACKAGE))
        continue
    if not os.path.isfile(os.path.join(FOLDER, under, PIECE)):
        stray.append("%s (no %s at %s)" % (name, PIECE, under or "."))
# A list that could not be read at all is the first check's, not this
# one's: asking for it again here says nothing new and makes this line
# report "0 of 0" where the line above already names the cause.
check("pip installs no name that has no piece behind it", not stray,
      "%d name(s) in packages, %d of them with nothing behind them: %s"
      % (len(listed), len(stray), stray or "none"))

# ------------------------------------------------- nothing fetched blind
print("\n3. Every piece on disk is fetched by a name that can be read")
# A folder holding a piece that no call above names is either dead
# weight or fetched by a name the search cannot read -- a variable, a
# joined string, a loop. The second is what makes the two checks above
# blind without anything going red, so it is asked outright.
on_disk = sorted(name for name in os.listdir(FOLDER)
                 if os.path.isfile(os.path.join(FOLDER, name, PIECE)))
unfetched = [name for name in on_disk if name not in places]
check("every folder of the program is fetched by its name",
      bool(on_disk) and not unfetched,
      "%d folder(s) hold a piece, %d of them named by no beside() call "
      "the search can read: %s"
      % (len(on_disk), len(unfetched), unfetched or "none"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
