# -*- coding: utf-8 -*-
"""A file with no place is told what became of it, not only what is wrong.

The program moves a file whose sound is not recognised and which
carries no timecode off content and the wide shot at the moment it
finds it -- to Intro, or out of the run where the intro is taken. The
note beside the file said none of that: it complained, the row beside
it said Intro, and the two read as contradicting each other.

Sections: what the note says for each of the two decisions and for a
file nobody has decided about; and that the note is written out of the
Kind field the window really holds, rather than out of a value passed
in beside it.

The words in it are the program's own, asked for by their value, so
this measures the sentence and not one language's spelling of it.
"""
import os
import sys
import time
import the_program

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
from PySide6 import QtWidgets

app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


PATH = "/tmp/vpm no place/GuestCam_C003.mov"
INTRO = vpm.label_of(vpm.TYPE_INTRO)
OUTRO = vpm.label_of(vpm.TYPE_OUTRO)

print("1. What the note says for each decision")

to_intro = vpm.weak_note(PATH, True, vpm.TYPE_INTRO)
check("a file set to Intro is told so, beside the complaint",
      INTRO in to_intro and OUTRO in to_intro,
      "it says %r, wanted %r and %r in it"
      % (to_intro.splitlines()[-1], INTRO, OUTRO))

left_out = vpm.weak_note(PATH, True, vpm.TYPE_IGNORED)
check("one left out because the intro was taken is told that instead",
      left_out != to_intro and INTRO in left_out and OUTRO in left_out,
      "it says %r, wanted a different sentence naming %r and %r"
      % (left_out.splitlines()[-1], INTRO, OUTRO))

undecided = vpm.weak_note(PATH, True)
check("a file nobody has decided about keeps the plain refusal",
      INTRO not in undecided and OUTRO not in undecided
      and undecided.splitlines()[-1].strip(),
      "it says %r, wanted a sentence naming no kind at all"
      % (undecided.splitlines()[-1],))


print("\n2. The note is written out of the Kind field the window holds")


class Kind(object):
    """One Kind field of the window, as much of it as this road uses."""

    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


tree = vpm.tree_build(["Recording", "Name", "belongs to", "Timecode",
                       "Speakers"])
row = vpm.tree_row(tree, None, [os.path.basename(PATH)])
kinds = vpm.ByFile()
kinds[PATH] = Kind(vpm.TYPE_INTRO)
state = {"weak": (), "no_place": (vpm.path_key(PATH),),
         "file_rows": [(row, PATH, os.path.basename(PATH))],
         "clip_kinds": kinds}
vpm.weak_marks_show(state, {})
written = row[0].text()
check("the note is written out of the Kind field the window really holds",
      INTRO in written and OUTRO in written,
      "the row says %r, wanted %r and %r in it -- the field says %r"
      % (written.splitlines()[-1], INTRO, OUTRO, kinds[PATH].get()))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
