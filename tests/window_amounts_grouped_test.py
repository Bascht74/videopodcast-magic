# -*- coding: utf-8 -*-
"""The window says its amounts the way the language does.

The sections in the order they come: the balance line under the file
list in German, where a thousand takes a dot; the same line in English,
where it takes a comma; the line about a wide shot that is too short,
where a length in seconds takes the decimal mark and a long one is
written out in digits instead of as a power of ten; and the speaker
table, whose share, block count and mean block length each take the
marks of the language.

The lines are asked of the functions that build them, and the table is
filled through the very call the window fills it with -- a check on the
helper alone stays green when somebody turns a caller back. Only the
statistics behind the table are a stand-in, so what is judged is what
the window writes and not what a recording would have measured. No
wording is held against anything, which is why these checks stand
whether a catalogue carries the sentence or not.
"""
import os
import sys
import time

import the_program

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("VPM_SILENT", "1")

from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import Qt

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def cell(table, row, column):
    """What stands in one box of the table, or "" where nothing does."""
    p = table.item(row, column)
    return p.text() if p is not None else ""


# Four digits, because that is where the languages part: under a
# thousand every one of them writes the same digits.
MANY = 1234
# A wide shot shorter than the shortest shot, so the line gets built at
# all -- the function answers with nothing where the two agree.
WIDE = {"wide-length": 2.5, "min-edit-duration": 4.0}
# The same pair, both of them large. Nothing caps either field: they
# are typed into the window and read back with float(), so a shortest
# shot of a million seconds is a setting the window accepts.
WIDE_LONG = {"wide-length": 1200.0, "min-edit-duration": 1500000.0}
# Two speakers, made up here so the table has something to write. The
# first speaks in 1234 blocks of two and a half seconds, which is where
# the block count wants a thousands mark; the second speaks once, for
# 1234.5 s, which is where the mean block length wants both marks.
# 4319.5 s of the 7000 are spoken, so 2680.5 s are silent.
TALKING = {"length_s": 7000.0, "speakers": [
    {"name": "role A", "sections": [(i * 4.0, i * 4.0 + 2.5)
                                     for i in range(1234)]},
    {"name": "role B", "sections": [(5000.0, 6234.5)]}]}

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

# The two halves of the same line, each with its own fault to fall
# into: "%g" leaves four digits ungrouped, and from a million on it
# goes over to exponential notation, where a decimal mark set into the
# result leaves "1,5e+06 s" standing in the German window.
said = vpm.wide_too_short(WIDE_LONG)
check("a four digit wide shot length carries the German thousands mark",
      "1.200,0" in said and "1200" not in said,
      "%r -- wanted %r in it and %r not" % (said, "1.200,0", "1200"))
check("a shortest shot of a million seconds is written out in digits",
      "1.500.000,0" in said and "e+" not in said,
      "%r -- wanted %r in it and no %r" % (said, "1.500.000,0", "e+"))

print("\n4. The speaker table says every one of its numbers in German")
table = QtWidgets.QTableWidget()
table.setColumnCount(5)
vpm.set_language("de")
vpm.speech_table_fill(Qt, QtGui, QtWidgets, table, TALKING)
# Before the boxes are read: an empty table would answer "" to every
# one of them below, and four checks would blame the language for it.
check("the table gets a row for each speaker and one for the silence",
      table.rowCount() == 3,
      "%d rows for 2 speakers and a silence row" % table.rowCount())

said = cell(table, 0, 2)
check("a speaker's share of the talking carries the German decimal mark",
      "71,4" in said and "71.4" not in said,
      "%r -- wanted %r in it and %r not" % (said, "71,4", "71.4"))

said = cell(table, 0, 3)
check("a speaker's count of speech blocks carries the thousands mark",
      "1.234" in said and "1234" not in said,
      "%r -- wanted %r in it and %r not" % (said, "1.234", "1234"))

said = cell(table, 1, 4)
check("a mean block length carries the thousands mark and the comma",
      "1.234,5" in said and "1234" not in said,
      "%r -- wanted %r in it and %r not" % (said, "1.234,5", "1234"))

said = cell(table, 2, 2)
check("the silence row's share carries the German decimal mark",
      "38,3" in said and "38.3" not in said,
      "%r -- wanted %r in it and %r not" % (said, "38,3", "38.3"))

# The suite runs in English, so the module goes back the way it was
# found: a language left standing reaches every test after this one.
vpm.set_language("en")

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
