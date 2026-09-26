# -*- coding: utf-8 -*-
"""The reaction cut lands where the picture changes, and is counted there.

The talk is built here, so where the picture changes is known. In order:
an answer beside the change to its camera is brought forward, one beside
a change to another camera is not, two questions into one answer count
once, and a question too short for a shot of its own is not shown while
one that is shown keeps the shortest shot -- counted only where the
picture still changes. Every count is read out of the line the run
prints, not out of the numbers behind it.
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

began = time.time()
vpm = the_program.load()
vpm.set_language("en")
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def asked(start, end, count=8):
    """One question as words: *count* words from *start* to *end*."""
    step = (end - start) / count
    return [vpm.speech_word(start + i * step, start + i * step + step * 0.9,
                            "word" + ("?" if i == count - 1 else ""))
            for i in range(count)]


CAMERAS = {"Host": "CamA", "Guest": "CamB", "Third": "CamC"}


def cut_of(tracks, words, length=60.0, min_len=0.5):
    """The cut of this talk, and the lines the run prints about questions."""
    rules = vpm.cut_rules(words=words, on_question=vpm.SHOT_ANSWER,
                          reaction_lead=1.5)
    cut = vpm.build_camera_cut(tracks, length, CAMERAS, "Wide",
                               min_len=min_len, lead_in=-0.3, rules=rules)
    return cut, vpm.question_report(rules)


def counted(questions, cuts):
    """The first line of the report, as it reads for these two numbers."""
    return vpm.T('  Question: %s in the transcript, %s became a reaction '
                 'cut.') % (questions, cuts)


def starts(cut, camera):
    """Where each shot of *camera* begins, to the millisecond."""
    return [round(a, 3) for a, _b, who in cut if who == camera]


# The Host asks until 9.875 s; the Guest answers from 10.5 s, but the
# Third speaks with him until 12.0 s, so the picture goes to the wide
# shot at 10.5 and to the Guest's camera only at 12.0 -- 1.5 s off.
QUESTION = asked(0.0, 10.0)

print("1. An answer beside the change to its camera")
beside, said = cut_of([("Host", [(0.0, 10.0)]), ("Guest", [(10.5, 60.0)]),
                       ("Third", [(10.5, 12.0)])], QUESTION)
check("an answer 1.5 s off the change to its camera comes early",
      starts(beside, "CamB") == [8.375],
      "CamB starts at %s, wanted [8.375] -- the question ends at 9.875, "
      "the lead is 1.5, the change sits at 12.0" % starts(beside, "CamB"))
check("and the log counts it as one reaction cut",
      said.splitlines()[:1] == [counted("1", "1")], repr(said))

print("\n2. A change to another camera beside the answer")
# The same, but the Third holds on until 14.0: the change at 10.5 is to
# the wide shot, and the one to the Guest lies 3.5 s off, past the gap.
other, said = cut_of([("Host", [(0.0, 10.0)]), ("Guest", [(10.5, 60.0)]),
                      ("Third", [(10.5, 14.0)])], QUESTION)
check("a change to another camera is not brought forward",
      starts(other, "Wide") == [10.3] and starts(other, "CamB") == [14.3],
      "wide shot at %s, CamB at %s, wanted [10.3] and [14.3] -- both "
      "only 0.3 s late" % (starts(other, "Wide"), starts(other, "CamB")))
check("an answer not brought forward is no reaction cut in the log",
      said.splitlines()[:1] == [counted("1", "0")], repr(said))

print("\n3. Two questions into one answer")
# Both questions end within 3.0 s of the Guest's first word at 10.5.
twice, said = cut_of([("Host", [(0.0, 10.0)]), ("Guest", [(10.5, 60.0)])],
                     asked(5.0, 8.0) + asked(8.0, 10.0))
check("two questions into one answer count as one reaction cut",
      said.splitlines()[:1] == [counted("2", "1")], repr(said))
check("and the other question is named as sharing that answer",
      vpm.T('the answer was counted with the question before') in said,
      repr(said))

print("\n4. A question shorter than the shortest shot")
# Shortest shot 3.0 s. The Host asks from 20.0 s; the shot starts 0.3 s
# late at 20.3 and the Guest is brought in 1.5 s before the question
# ends: a question to 26.0 keeps 4.125 s, one to 24.5 only 2.644 s.
shown, _said = cut_of([("Third", [(0.0, 20.0)]), ("Host", [(20.0, 26.0)]),
                       ("Guest", [(26.5, 80.0)])], asked(20.0, 26.0),
                      80.0, 3.0)
gone, said = cut_of([("Third", [(0.0, 20.0)]), ("Host", [(20.0, 24.5)]),
                     ("Guest", [(25.0, 80.0)])], asked(20.0, 24.5),
                    80.0, 3.0)
check("a question shorter than the shortest shot is not shown",
      starts(gone, "CamA") == [] and starts(gone, "CamB") == [20.3],
      "CamA at %s, CamB at %s, wanted [] and [20.3]"
      % (starts(gone, "CamA"), starts(gone, "CamB")))
asker = [round(b - a, 3) for a, b, who in shown + gone if who == "CamA"]
check("a question that is shown keeps the shortest shot",
      asker == [4.125],
      "the asker's shots last %s s, wanted [4.125] -- one, over 3.0" % asker)
check("a question gone that way still counts as a reaction cut",
      said.splitlines()[:1] == [counted("1", "1")], repr(said))
# The Guest speaks before the question as well as after it: with the
# question gone the picture stays on the Guest from 10.3 s, and nothing
# was cut. The Third before him keeps a change in front of it.
still, said = cut_of([("Third", [(0.0, 10.0)]),
                      ("Guest", [(10.0, 20.0), (23.5, 60.0)]),
                      ("Host", [(20.0, 23.0)])], asked(20.0, 23.0),
                     60.0, 3.0)
check("a question gone between two answers is no reaction cut",
      starts(still, "CamB") == [10.3]
      and said.splitlines()[:1] == [counted("1", "0")],
      "CamB at %s, wanted [10.3]; %r" % (starts(still, "CamB"), said))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
