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
source = io.open(SCRIPT, encoding="utf-8").read()
# A timer, in every shape it could come back in.
check("no timer calls presets_load",
      not re.search(r"singleShot\([^)]*presets_load", source))
# The definition carries a default too, so it is not a call site.
calls = sorted(re.findall(r"(?<!def )presets_load\(asked=(\w+)\)", source))
check("presets_load is called from the button and the list only",
      calls == ["False", "True"], str(calls))
check("the list fetches itself when it is opened",
      "def showPopup" in source and "presets_load(asked=False)" in source)

print("\n4. A start that finds a bad key says so quietly")
# asked=False is the fetch nobody asked for: settings yes, a box no.
quiet = re.search(r"if not state\.get\(\"key_asked\", True\):"
                  r"(.{0,400}?)return", source, re.S)
check("the unasked fetch has a quiet path", bool(quiet))
check("and that path opens no box",
      bool(quiet) and "report(" not in quiet.group(1))

print("\nAll good." if not error else "\nFAIL: %s" % ", ".join(error))
sys.exit(1 if error else 0)
