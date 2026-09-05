# -*- coding: utf-8 -*-
"""The program says nothing to auphonic.com unless somebody asks it to.

Two rules, both broken once: a start-up must not speak to a third party
about a key it was only asked to keep, so the presets are fetched when
the list is opened and at no other time; and a key that is plainly not
one never leaves the house, where plainly covers only what can be told
without asking, because a guessed format turns away a key that works.
"""
import os
import re
import sys
import time
import the_program

began = time.time()

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
vpm = the_program.load()

done = 0
error = []
def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

print("1. What is turned away before it is sent")
TURNED_AWAY = ["", "   ", "\n", "a b", "a\nb", " abc", "abc ", "abc\t",
               "abc\x01", "abc\x7f"]
for key in TURNED_AWAY:
    said = vpm.key_complaint(key)
    check("turned away: %r" % key, bool(said),
          "complaint %r, wanted one" % (said,))
# Any length and any character set gets through: what a real key looks
# like is written down nowhere. The last one carries a letter outside
# ASCII, written as an escape because text_no_german_left_test.py hunts for
# German letters in the test files.
LET_THROUGH = ["a", "abcdef", "x" * 200, "AbC-123_xyz", "0123456789",
               "schl\u00fcssel-1234"]
for key in LET_THROUGH:
    check("let through: %r" % key, not vpm.key_complaint(key),
          vpm.key_complaint(key))

print("\n2. Every complaint is a sentence somebody can read")
for key in TURNED_AWAY[1:]:
    said = vpm.key_complaint(key)
    check("%r says something whole" % key,
          said.endswith(".") or said.endswith("?"), repr(said))

print("\n3. Nothing is fetched at the start")
source = the_program.whole()
# A timer, in every shape it could come back in.
timers = re.findall(r"singleShot\([^)]*presets_load", source)
check("no timer calls presets_load", not timers,
      "%d timers call it, wanted 0: %s" % (len(timers), timers))
# The definition carries a default too, so it is not a call site.
calls = sorted(re.findall(r"(?<!def )presets_load\(asked=(\w+)\)", source))
check("presets_load is called from the button and the list only",
      calls == ["False", "True"], str(calls))
popups = source.count("def showPopup")
unasked = source.count("presets_load(asked=False)")
check("the list fetches itself when it is opened",
      popups >= 1 and unasked >= 1,
      "def showPopup %d times and presets_load(asked=False) %d times, "
      "wanted at least 1 of each" % (popups, unasked))

print("\n4. A start that finds a bad key says so quietly")
# asked=False is the fetch nobody asked for: settings yes, a box no.
quiet = re.search(r"if not state\.get\(\"key_asked\", True\):"
                  r"(.{0,400}?)return", source, re.S)
check("the unasked fetch has a quiet path", bool(quiet),
      "%d key_asked guards in %d characters of source, wanted 1"
      % (0 if quiet is None else 1, len(source)))
boxes = quiet.group(1).count("report(") if quiet else -1
check("and that path opens no box", boxes == 0,
      "%d report( calls in the %d characters after the guard, wanted 0"
      % (boxes, len(quiet.group(1)) if quiet else 0))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("\nAll good." if not error else "\nFAIL: %s" % ", ".join(error))
sys.exit(1 if error else 0)
