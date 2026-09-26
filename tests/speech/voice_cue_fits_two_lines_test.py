# -*- coding: utf-8 -*-
"""No subtitle in the srt runs to a third line, the speaker's name counted.

The words are made up here -- no recognition, no sound: two voices in
long passages, one of them slow enough that the clock cuts before the
lines do. The file is read as it is written, and in order: the lines a
subtitle holds, their length, how long it stands, and the name in
capitals in front wherever the voice changes, and nowhere else.
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
import time
import the_program
SCRIPT = the_program.SCRIPT
vpm = the_program.load()

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


FAST = ("About three years ago we started with a single microphone in a "
        "kitchen and the first year was the hardest one because nobody "
        "listened and we had to grow at our own pace without any help "
        "from anybody who knew how recording really worked back then. "
        "Listening to people who know recording well was how we learned")
SLOW = ("yes and so it is and we do it now and then as we go on and on "
        "for a long time to come")
SAID, t = [], 0.0
for who, text, step in (("Guest", FAST, 0.3), ("Presenter", SLOW, 1.0),
                        ("Guest", FAST, 0.3)):
    for word in text.split():
        SAID.append(dict(vpm.speech_word(t, t + step - 0.05, word),
                         speaker=who))
        t += step

cues = vpm.subtitle_cues(SAID)
srt = vpm.subtitle_file_text(cues)
blocks = [b.split("\n")[2:] for b in srt.strip().split("\n\n")]
print("%d words, %d subtitles" % (len(SAID), len(blocks)))

print("\n1. What a subtitle holds")
most = max(blocks, key=len)
check("no subtitle runs to a third line, the name counted in",
      len(most) <= vpm.SUBTITLE_LINES,
      "subtitle %d has %d lines against %d: %s"
      % (blocks.index(most) + 1, len(most), vpm.SUBTITLE_LINES,
         " / ".join(most)))
widest = max((line for b in blocks for line in b), key=len)
check("no subtitle line is longer than the line length",
      len(widest) <= vpm.SUBTITLE_LINE_CHARS,
      "%d characters against %d: %r"
      % (len(widest), vpm.SUBTITLE_LINE_CHARS, widest))
stands = max(b - a for a, b, _who, _text in cues)
check("no subtitle stands longer than the longest time",
      stands <= vpm.SUBTITLE_LONGEST_S + 1e-6,
      "%.2f s against %.2f s" % (stands, vpm.SUBTITLE_LONGEST_S))

print("\n2. The name where the voice changes")
named = [(i + 1, b[0].split(":")[0]) for i, b in enumerate(blocks)
         if b[0].split(":")[0] in ("GUEST", "PRESENTER")]
changes = [(i + 1, c[2].upper()) for i, c in enumerate(cues)
           if i == 0 or cues[i - 1][2] != c[2]]
check("the name stands in capitals where the voice changes",
      [n for _i, n in named] == ["GUEST", "PRESENTER", "GUEST"],
      "names %s, voice changes %s" % (named, changes))
check("and on no other subtitle", named == changes,
      "names on %s, voice changes on %s" % (named, changes))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
