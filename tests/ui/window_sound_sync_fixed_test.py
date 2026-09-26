# -*- coding: utf-8 -*-
"""The In the sound field keeps one answer, and Sync only fixes it mixed.

A recording's row in the file list carries what its sound holds. In
order: a fresh field on speech; an answer kept for its recording and the
time axis asked again; the field shut on mixed under Sync only; and the
way back, which shows what was chosen rather than what was forced. The
field is built on its own, not inside a window: which row carries it is
the file list's, and this asks only what the field does.
"""
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

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6 import QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")

QUIET = vpm.COLOURS["quiet"]
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# Two recordings by path; nothing is opened, the field works on names.
TALK = "/tmp/vpm_sound_field/Presenter_REC0001.wav"
BED = "/tmp/vpm_sound_field/CoPresenter_REC0002.wav"
asked = []
state = {"project_type": "cut", "sound_holds": vpm.ByFile(),
         "axis_sound_again": lambda: asked.append(time.time())}

print("1. A fresh field")
_cell, talk = vpm.sound_cell_for(TALK, state, QUIET)
_cell2, bed = vpm.sound_cell_for(BED, state, QUIET)
check("a recording's field starts on speech",
      talk.currentData() == vpm.SOUND_SPEECH and talk.isEnabled(),
      "shows %r, enabled %s -- wanted %r and True"
      % (talk.currentData(), talk.isEnabled(), vpm.SOUND_SPEECH))

print("\n2. An answer")
talk.setCurrentIndex(talk.findData(vpm.SOUND_MIXED))
check("picking mixed keeps it for that recording alone",
      state["sound_holds"].get(TALK) == vpm.SOUND_MIXED
      and state["sound_holds"].get(BED) is None,
      "kept %r for the one, %r for the other -- wanted mixed and none"
      % (state["sound_holds"].get(TALK), state["sound_holds"].get(BED)))
check("and the time axis is asked again", len(asked) == 1,
      "asked %d times, wanted once" % len(asked))

print("\n3. Sync only")
state["project_type"] = "sync"
vpm.sound_cells_follow(state)
check("under Sync only every field stands on mixed and is shut",
      [b.currentData() for b in (talk, bed)] == [vpm.SOUND_MIXED] * 2
      and not talk.isEnabled() and not bed.isEnabled(),
      "show %r, enabled %r -- wanted mixed twice and shut"
      % ([b.currentData() for b in (talk, bed)],
         [b.isEnabled() for b in (talk, bed)]))
check("and what it shows is not written into the answers",
      state["sound_holds"].get(BED) is None and len(asked) == 1,
      "the untouched recording holds %r, the axis asked %d times -- "
      "wanted none and once" % (state["sound_holds"].get(BED), len(asked)))

print("\n4. Back to the cut")
state["project_type"] = "cut"
vpm.sound_cells_follow(state)
check("back to the cut each field shows what was chosen",
      [b.currentData() for b in (talk, bed)]
      == [vpm.SOUND_MIXED, vpm.SOUND_SPEECH] and bed.isEnabled(),
      "show %r, enabled %s -- wanted mixed, speech and open"
      % ([b.currentData() for b in (talk, bed)], bed.isEnabled()))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
