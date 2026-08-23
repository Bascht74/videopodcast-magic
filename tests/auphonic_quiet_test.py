# -*- coding: utf-8 -*-
"""The program says nothing to auphonic.com unless somebody asks it to.

Two rules, both of them Sebastian's, both of them broken once:

  * A start-up must not speak to a third party about a key it was only
    asked to keep. The presets are fetched when the list is opened, and
    at no other time.
  * A key that is plainly not one never leaves the house. What "plainly"
    means is only what can be told without asking anybody -- how long a
    real key is has never been measured here, and a guessed format would
    turn away a key that works.
"""
import os
import re
import io
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

print("1. What is turned away before it is sent")
TURNED_AWAY = ["", "   ", "\n", "a b", "a\nb", " abc", "abc ", "abc\t",
               "abc\x01", "abc\x7f"]
for key in TURNED_AWAY:
    check("turned away: %r" % key, bool(vpm.key_complaint(key)))
# Nothing else. A key of any length and any character set gets through,
# because what a real one looks like is not written down anywhere.
# The last one carries a letter outside ASCII on purpose: what a real
# key may contain has never been measured here, so nothing is turned
# away for its character set alone. Written as an escape, because a
# test file that carries a German letter is what german_hunt_test.py
# looks for.
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
source = io.open(SCRIPT, encoding="utf-8").read()
# The timer that used to do it, in every shape it could come back in.
check("no timer calls presets_load",
      not re.search(r"singleShot\([^)]*presets_load", source))
# The definition carries asked=True as its default, so it is not a call
# site; only what stands without "def" in front of it is.
calls = sorted(re.findall(r"(?<!def )presets_load\(asked=(\w+)\)", source))
check("presets_load is called from the button and the list only",
      calls == ["False", "True"], str(calls))
check("the list fetches itself when it is opened",
      "def showPopup" in source and "presets_load(asked=False)" in source)

print("\n4. A start that finds a bad key says so quietly")
# asked=False is the fetch nobody asked for: it may write into the
# settings, never into a box.
quiet = re.search(r"if not state\.get\(\"key_asked\", True\):"
                  r"(.{0,400}?)return", source, re.S)
check("the unasked fetch has a quiet path", bool(quiet))
check("and that path opens no box",
      bool(quiet) and "report(" not in quiet.group(1))

print("\nAll good." if not error else "\nFAIL: %s" % ", ".join(error))
sys.exit(1 if error else 0)
