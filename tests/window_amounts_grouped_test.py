# -*- coding: utf-8 -*-
"""The window says its amounts the way the language does.

Three sections in the order they come: the balance line under the file
list in German, where a thousand takes a dot; the same line in English,
where it takes a comma; and the line about a wide shot that is too
short, where a length in seconds takes the decimal mark.

The lines are asked of the functions that build them rather than of a
window: what is judged is the shape of the number, and a window would
only put Qt under it. No wording is held against anything, which is why
these checks stand whether a catalogue carries the sentence or not.
"""
import sys
import time

import the_program

began = time.time()
vpm = the_program.load()

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# Four digits, because that is where the languages part: under a
# thousand every one of them writes the same digits.
MANY = 1234
# A wide shot shorter than the shortest shot, so the line gets built at
# all -- the function answers with nothing where the two agree.
WIDE = {"wide-length": 2.5, "min-edit-duration": 4.0}

print("1. A count in the balance line takes the thousands mark of German")
vpm.set_language("de")
line, _colour = vpm.preflight_sentence([], 0, 0, MANY)
check("the video files under the file list are counted in the German form",
      "1.234" in line and "1234" not in line,
      "%r -- wanted %r in it and %r not" % (line, "1.234", "1234"))

print("\n2. And in English the comma")
vpm.set_language("en")
line, _colour = vpm.preflight_sentence([], 0, 0, MANY)
check("the same count in the English window carries the comma",
      "1,234" in line and "1234" not in line,
      "%r -- wanted %r in it and %r not" % (line, "1,234", "1234"))

print("\n3. A length in seconds takes the decimal mark of the language")
vpm.set_language("de")
said = vpm.wide_too_short(WIDE)
check("the wide shot length carries the German decimal mark",
      "2,5" in said and "2.5" not in said,
      "%r -- wanted %r in it and %r not" % (said, "2,5", "2.5"))

# The suite runs in English, so the module goes back the way it was
# found: a language left standing reaches every test after this one.
vpm.set_language("en")

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
