# -*- coding: utf-8 -*-
"""No function loses tested lines, and no new one goes untested.

A ratchet over what the whole suite runs of the program, measured by
coverage.py across every process (tests/tested_lines.py says how) and
held per function, never as one share: a share lets a new untested
function hide behind a test written elsewhere. In order: the measurement
saw the program run at all, no function has more untested lines than
its floor, and no function the state does not know is untested whole.
A floor falls by itself, except under `unsteady` in the state, and goes
with its function. Before the version JUDGED_FROM names, what would fall
is a NOTED line and the run stays green. Only `VPM_COVERAGE=1 bash
run.sh` runs this, after the rest.
"""
PLATFORM_BOUND = True
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import re
import time
import the_program
import ratchet
import tested_lines

began = time.time()
STATE = tested_lines.STATE
KEY = tested_lines.KEY
# Functions whose count differs between two runs of the same tree -- a
# cache one test fills before the other asks, a player that is quicker
# one time than the next -- or between this machine and the builder,
# which sets tests aside. Their allowance is the highest count seen, and
# a lucky run never lowers it, or the next ordinary one is red. Entered
# by hand with the count that was measured, or out of several runs by
# `python3 tested_lines.py --floors`.
UNSTEADY = tested_lines.UNSTEADY
# The data of the run that has just finished, and the program folder it
# was measured on; run.sh names both. The folder judged is the one
# VPM_SCRIPT names, which is the same one unless a copy is being held
# against the original's measurement.
DATA = os.environ.get("VPM_COVERAGE_DATA")
MEASURED = os.environ.get("VPM_COVERAGE_SOURCE") or the_program.FOLDER
# Where the builder wants the table it measured, whatever the verdict:
# its floor can differ from this machine's, and a red run must still
# say what it found.
TABLE = os.environ.get("VPM_COVERAGE_TABLE")
# The owner's decision for 3.0.0b29: that release measures and leaves its
# table, and what this test would fail on is said as a NOTED line; from
# this version on it fails, held against the program's VERSION as
# text_one_picture_each reads it. Ordered, not matched: a release that
# skipped this number -- b29 straight to 3.0.0 -- is judged all the
# same, and nobody has to remember the day. A version that cannot be
# read is judged.
JUDGED_FROM = "3.0.0b30"


def version_order(text):
    """3.0.0b29 as (3, 0, 0, 1, 29): a, b and rc come before the release."""
    found = re.match(r"(\d+)\.(\d+)\.(\d+)(?:(a|b|rc)(\d+))?$", text)
    if not found:
        return None
    return (tuple(int(n) for n in found.group(1, 2, 3))
            + (("a", "b", "rc", None).index(found.group(4)),
               int(found.group(5) or 0)))


said = re.search(r'^VERSION = "([^"]+)"', the_program.text(), re.M)
VERSION = said.group(1) if said else ""
JUDGING = (version_order(VERSION) is None
           or version_order(VERSION) >= version_order(JUDGED_FROM))

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    # Before JUDGED_FROM a judgement that falls is noted, not failed.
    noted = not ok and not JUDGING
    print("  %-58s %s %s" % (name, "ok" if ok else "noted" if noted
                             else "FAIL", extra))
    if noted:
        print("NOTED tested lines: %s [%s]" % (name, extra or "no numbers"))
    elif not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def first_few(rows):
    """The first three places, with their numbers, for the FAIL line."""
    return ", ".join(rows[:3]) + (" and %d more" % (len(rows) - 3)
                                  if len(rows) > 3 else "")


def finish():
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


if not DATA:
    print("SKIPPED: no measurement to judge -- VPM_COVERAGE=1"
          " VPM_ALL_LANGUAGES=1 bash run.sh measures the whole suite and"
          " runs this after it")
    finish()

data = tested_lines.combine(DATA)
ran = tested_lines.executed(data, MEASURED) if data is not None else {}
found, untested, lines = tested_lines.tally(the_program.FOLDER, ran)
print("  tested lines: %d of %d, %.1f %% -- %d functions, %d files measured"
      % (lines - untested, lines, 100.0 * (lines - untested) / (lines or 1),
         len(found), len(ran)))
print("  judged from %s on; the program says %s%s"
      % (JUDGED_FROM, VERSION or "no version",
         "" if JUDGING else " -- what falls is noted, not failed"))
table = dict((mark, [missed, first])
             for mark, (missed, _whole, first) in found.items())
if TABLE:
    with open(TABLE, "w") as out:
        out.write(ratchet.dumps({KEY: table}))

# ------------------------------------------------- The measurement itself
# Without it every function reads as untested, and the two judgements
# below would name four thousand places instead of the one cause.
check("the measurement saw the program's own lines run",
      lines > untested,
      "%d of %d lines run, %d program files in the data under %s/"
      % (lines - untested, lines, len(ran), os.path.basename(MEASURED)))
if lines <= untested:
    print("LEFT OUT the floors: with nothing measured, every function"
          " would read as untested")
    finish()

# -------------------------------------------------------------- The floors
state = ratchet.Ratchet(STATE)
state.announce()
old = state.old.get(KEY)
allowed = (dict((mark, entry[0]) for mark, entry in old.items())
           if isinstance(old, dict) else None)
unsteady = state.old.get(UNSTEADY)
unsteady = unsteady if isinstance(unsteady, dict) else {}
if allowed is not None:
    for mark, entry in unsteady.items():
        allowed[mark] = max(allowed.get(mark, 0), entry[0])
risen = []
fresh = []
if allowed is not None:
    for mark in sorted(found):
        missed, whole, first = found[mark]
        if mark in allowed and missed > allowed[mark]:
            risen.append((mark, missed, allowed[mark], first))
        elif mark not in allowed and missed == whole:
            fresh.append((mark, missed, first))

check("no function has more untested lines than its floor", not risen,
      "%d over: %s" % (len(risen), first_few(
          ["%s %d>%d" % (m, now, may) for m, now, may, _l in risen])))
for mark, now, may, line in risen:
    print("      line %-6s %s  %d untested, the state allows %d"
          % (line, mark, now, may))
if risen:
    print("      a function nobody touched that rose is unsteady: its"
          " highest count goes under %r in %s, by hand"
          % (UNSTEADY, os.path.basename(STATE)))
check("no function the state does not know is untested whole", not fresh,
      "%d untested: %s" % (len(fresh), first_few(
          ["%s %d lines" % (m, n) for m, n, _l in fresh])))
for mark, now, line in fresh:
    print("      line %-6s %s  %d lines, none of them run" % (line, mark, now))

# A floor moves only on a run with nothing over it, noted or failed:
# written while a function stands over its floor, the state would take
# the rise in.
if not risen and not fresh:
    kept = {}
    for mark, entry in table.items():
        was = old.get(mark) if isinstance(old, dict) else None
        # An unchanged count keeps its old line, so the diff of the state
        # shows what moved and not every line that shifted under it; an
        # unsteady function keeps its floor however low this run came.
        if was and (was[0] == entry[0] or mark in unsteady):
            kept[mark] = was
        else:
            kept[mark] = entry
    if kept != old:
        before = sum(e[0] for e in old.values()) if isinstance(old, dict) \
            else None
        after = sum(e[0] for e in kept.values())
        state.new[KEY] = kept
        state.new[UNSTEADY] = dict((m, e) for m, e in unsteady.items()
                                   if m in table)
        if state._save() and before is not None and after < before:
            print("      ratchet tightened: %d -> %d" % (before, after))

finish()
