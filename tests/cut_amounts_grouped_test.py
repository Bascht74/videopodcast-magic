# -*- coding: utf-8 -*-
"""The cut's report writes amounts as the language does, names not.

The sections in the order they come: a count of sentences, read in
German and then in English so both thousands marks show; the padded
seconds beside a grouped minute; the name a voice is proposed under,
which keeps its plain digits; and a measured distance between two
microphones, which takes the decimal mark.

The material is made up here -- a ranking, and two levels forty
decibels apart -- so what is judged is the shape of the number the
program prints, and no wording is held against a catalogue.
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


def holding(text, *pieces):
    """The first line of text carrying one of pieces, for the FAIL line."""
    for line in text.splitlines():
        if any(p in line for p in pieces):
            return line.strip()
    return ""


# Who asks, as the ranking hands it on: name, sentences, questions,
# speaking time. The first voice carries a four-digit count of
# sentences, which is where a thousands mark shows at all.
SENTENCES = 1240
ASKED = 312
ORDER = [("SPEAKER_00", SENTENCES, ASKED, 900.0),
         ("SPEAKER_01", 800, 40, 1800.0)]

print("1. A count of sentences takes the thousands mark of the language")
vpm.set_language("de")
german = "\n".join(vpm.roles_report(ORDER))
said = holding(german, "1.240", "1240")
check("the sentences behind the questions carry the German thousands mark",
      "1.240" in german and "1240" not in german,
      "%r -- wanted %r in it and %r not" % (said, "1.240", "1240"))

vpm.set_language("en")
english = "\n".join(vpm.roles_report(ORDER))
said = holding(english, "1,240", "1240")
check("the same count carries the English thousands comma",
      "1,240" in english and "1.240" not in english,
      "%r -- wanted %r in it and %r not" % (said, "1,240", "1.240"))

print("\n2. The seconds beside a grouped minute keep their nought")
# Four seconds past the 1234th minute. The minutes are an amount and
# take the mark; the seconds are a padded sub-field under sixty, and
# grouping them would turn "3:04 min" into "3:4 min".
LONG_S = 1234 * 60 + 4
vpm.set_language("de")
minutes = vpm.as_minutes(LONG_S)
check("the seconds beside the minutes keep their leading nought",
      ":04" in minutes,
      "as_minutes(%d) is %r, wanted %r in it" % (LONG_S, minutes, ":04"))

print("\n3. The name a voice is proposed under keeps its plain digits")
# The last row of the ranking is the guest and the rest are hosts in
# the order they ask, so the last host carries the highest number.
ASKING = 1234
RANKING = [("v%d" % i, 10, 3, 5.0) for i in range(ASKING + 1)]
vpm.set_language("de")
called = vpm.voice_role_names(RANKING)["v%d" % (ASKING - 1)]
check("the number in a proposed voice name is not grouped",
      called.endswith("1234") and "1.234" not in called,
      "%r -- wanted it to end in %r and not to hold %r"
      % (called, "1234", "1.234"))

print("\n4. A measured distance takes the decimal mark of the language")
# Two microphones, one voice loud in each and quiet in the other. A
# level of 1.0 against 0.01 is forty decibels, so forty decibels is
# what the line has to say.
LOUD = [1.0] * 10
SOFT = [0.01] * 10
VOICES = [("SPEAKER_00", [(0.0, 1.0)]), ("SPEAKER_01", [(1.0, 2.0)])]
BOX = [{"names": ["MicA", "MicB"], "block": 0.1, "begin": 0.0,
        "level": [LOUD + SOFT, SOFT + LOUD]}]
vpm.set_language("de")
_named, lines = vpm.name_voices_by_microphone(VOICES, BOX)
line = lines[0] if lines else ""
check("the distance to the next microphone carries the German decimal mark",
      "40,0" in line and "40.0" not in line,
      "%d line(s) back, first %r -- wanted %r in it and %r not"
      % (len(lines), line, "40,0", "40.0"))

vpm.set_language("en")

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
