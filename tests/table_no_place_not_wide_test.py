# -*- coding: utf-8 -*-
"""A file that sits nowhere is not offered as the wide shot.

The wide shot is the camera that runs through and steps in wherever no
other one fits, so it has to lie on the time axis. A jingle does not:
no timecode, and no sound in common with the rest. In order: the barred
entry with its reason on it, the file that has a place and keeps the
choice, what a hand and a missing measurement leave alone, the
derivation, which stops picking such a file, and last that every table
builds the field in the one place where the bar is hung.
"""
import os
import sys
import time
import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT

os.environ["QT_QPA_PLATFORM"] = "offscreen"


from PySide6 import QtWidgets
from PySide6.QtCore import Qt

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


def entries(box):
    """Every entry of the list: its value, whether it is barred, its ink."""
    out = []
    for i in range(box.count()):
        ink = box.itemData(i, Qt.ForegroundRole)
        out.append((box.itemData(i),
                    not box.model().item(i).isEnabled(),
                    ink.color().name() if ink is not None else ""))
    return out


def barred(box):
    return [value for value, shut, _ink in entries(box) if shut]


def grey(box):
    return [value for value, _shut, ink in entries(box) if ink]


def says_at(box, kind):
    """What the list writes on one entry when it is pointed at."""
    return box.itemData(list(vpm.CLIP_TYPES).index(kind), Qt.ToolTipRole)


# Paths, not files: nothing here is opened. Which files sit nowhere is
# the measurement's answer, and it is handed in.
FOLDER = os.path.join(HERE, "state")
LOST = os.path.join(FOLDER, "Jingle.mov")
GOOD = os.path.join(FOLDER, "CamB.mov")
TAKEN = os.path.join(FOLDER, "CamA.mov")
NOWHERE = {os.path.abspath(LOST)}

print("1. The file the measurement could place nowhere")
kind = vpm.Value(vpm.TYPE_CONTENT)
why_wide = vpm.wide_shot_barred(LOST, kind, NOWHERE)
check("it is refused the wide shot, and a sentence says why",
      bool(why_wide), "the reason is %r" % why_wide)
check("the sentence names both halves of what it is missing",
      "timecode" in why_wide and "sound" in why_wide, repr(why_wide))
lost_cell, box = vpm.clip_kind_cell(os.path.basename(LOST),
                                    kind.get(), "", QUIET, False,
                                    why_wide)
check("neither the wide shot nor content can be chosen",
      sorted(barred(box)) == sorted([vpm.TYPE_WIDE, vpm.TYPE_CONTENT]),
      "barred: %s of %s" % (barred(box), list(vpm.CLIP_TYPES)))
check("and those two are the entries greyed in the list",
      sorted(grey(box)) == sorted([vpm.TYPE_WIDE, vpm.TYPE_CONTENT]),
      "greyed: %s of %s" % (grey(box), list(vpm.CLIP_TYPES)))
check("each of the two carries its own reason",
      says_at(box, vpm.TYPE_WIDE) == why_wide
      and "cut into the episode" in says_at(box, vpm.TYPE_CONTENT),
      "the wide shot says %r, Content says %r"
      % (says_at(box, vpm.TYPE_WIDE), says_at(box, vpm.TYPE_CONTENT)))
check("intro, outro and ignore stay open",
      set(v for v, shut, _i in entries(box) if not shut)
      == {vpm.TYPE_INTRO, vpm.TYPE_OUTRO, vpm.TYPE_IGNORED},
      "open: %s" % [v for v, shut, _i in entries(box) if not shut])
check("and the field itself can still be answered", box.isEnabled(),
      "the field is %s" % ("open" if box.isEnabled() else "dead"))

print("\n2. A file that has a place keeps every choice")
kind_good = vpm.Value(vpm.TYPE_CONTENT)
why_good = vpm.wide_shot_barred(GOOD, kind_good, NOWHERE)
check("nothing is refused it", why_good == "", repr(why_good))
good_cell, box_good = vpm.clip_kind_cell(
    os.path.basename(GOOD), kind_good.get(), "", QUIET, False, why_good)
check("so no entry of its Kind field is barred", barred(box_good) == [],
      "barred: %s" % (barred(box_good),))
# The bar has to come off again, and the same field is what comes back
# from a fresh measurement: a box that could shut but not open would
# keep the wide shot grey for the rest of the session.
vpm.choices_shut(box, {}, "", QUIET)
check("and a file that can be placed again gets the wide shot back",
      barred(box) == [] and grey(box) == []
      and says_at(box, vpm.TYPE_WIDE) == "",
      "barred %s, greyed %s, still says %r"
      % (barred(box), grey(box), says_at(box, vpm.TYPE_WIDE)))

print("\n3. What no measurement and what a hand leave alone")
check("without a measurement nothing is barred",
      vpm.wide_shot_barred(LOST, vpm.Value(vpm.TYPE_CONTENT), None) == ""
      and vpm.wide_shot_barred(LOST, vpm.Value(vpm.TYPE_CONTENT), set())
      == "",
      "None gave %r, the empty set gave %r"
      % (vpm.wide_shot_barred(LOST, vpm.Value(vpm.TYPE_CONTENT), None),
         vpm.wide_shot_barred(LOST, vpm.Value(vpm.TYPE_CONTENT), set())))
by_hand = vpm.Value(vpm.TYPE_WIDE)
by_hand.chosen_by_hand = True
check("a Kind somebody picked is barred too where nothing places the file",
      vpm.wide_shot_barred(LOST, by_hand, NOWHERE) != "",
      "the answer %r came back with %r, wanted a reason"
      % (by_hand.get(), vpm.wide_shot_barred(LOST, by_hand, NOWHERE)))

print("\n4. The derivation stops at the same file")
FILES = [(TAKEN, "video"), (GOOD, "video"), (LOST, "video")]
KINDS = dict((p, vpm.Value(vpm.TYPE_CONTENT)) for p, _a in FILES)
SPEAKER = {os.path.basename(TAKEN)}
wides, said = vpm.wide_cameras_of(FILES, KINDS, {}, SPEAKER)
check("a camera nobody sits in front of is the derived wide shot",
      wides == [os.path.basename(GOOD), os.path.basename(LOST)]
      and said is False, "%s, marked %s" % (wides, said))
wides, said = vpm.wide_cameras_of(FILES, KINDS, {}, SPEAKER, NOWHERE)
check("but not one that sits nowhere",
      wides == [os.path.basename(GOOD)] and said is False,
      "%s, marked %s" % (wides, said))
check("so its Kind field does not show a wide shot it may not be",
      vpm.kind_on_show(vpm.TYPE_CONTENT, os.path.basename(LOST),
                       wides, said)[0] == vpm.TYPE_CONTENT,
      "shows %r" % vpm.kind_on_show(vpm.TYPE_CONTENT,
                                    os.path.basename(LOST), wides, said)[0])
MARKED = dict(KINDS)
MARKED[LOST] = vpm.Value(vpm.TYPE_WIDE)
wides, said = vpm.wide_cameras_of(FILES, MARKED, {}, SPEAKER, NOWHERE)
check("a mark stands even there, because a mark is an answer",
      wides == [os.path.basename(LOST)] and said is True,
      "%s, marked %s" % (wides, said))
# Both bars at once: a file with no place that the derivation still
# shows as the wide shot would carry two reasons, and one sentence over
# both would explain neither.
two_cell, two = vpm.clip_kind_cell(
    os.path.basename(LOST), vpm.TYPE_WIDE,
    "because no speaker is assigned to it", QUIET, True, why_wide)
check("two barred entries each keep their own reason",
      sorted(barred(two)) == sorted([vpm.TYPE_CONTENT, vpm.TYPE_WIDE])
      and says_at(two, vpm.TYPE_WIDE) == why_wide
      and says_at(two, vpm.TYPE_CONTENT) == "because no speaker is "
                                            "assigned to it",
      "barred %s; the wide shot says %r, Content says %r"
      % (sorted(barred(two)), says_at(two, vpm.TYPE_WIDE),
         says_at(two, vpm.TYPE_CONTENT)))

# The three tables that show a Kind ask one function for the cell, and
# that is where the bar is hung. A table building its own would offer
# the wide shot again while everything here stayed green.
source = the_program.whole()
built, one_place = (source.count("clip_kind_cell("),
                    source.count("kind_cell_for("))
check("every table asks the one place for its Kind field",
      built == 2 and one_place >= 4,
      "clip_kind_cell stands %d times (its own def and one call), "
      "kind_cell_for %d (its own def and %d tables)"
      % (built, one_place, one_place - 1))

print("\nA Kind out of a project file is corrected too")
# The greyed entry stops a hand in the window. A project file does not
# go through the window, and neither does a switch, so the same rule
# stands once more where the measurement meets the answers.
by_file = dict((p, vpm.Value(vpm.TYPE_CONTENT)) for p in (LOST, GOOD))
by_file[LOST].chosen_by_hand = True
moved = vpm.kinds_off_the_axis(by_file, NOWHERE)
check("a file with no place is taken off content whoever set it",
      moved == [LOST] and by_file[LOST].get() == vpm.TYPE_INTRO,
      "moved %s, the file now says %r"
      % ([os.path.basename(p) for p in moved], by_file[LOST].get()))
check("a file the measurement placed is left where it was",
      by_file[GOOD].get() == vpm.TYPE_CONTENT, by_file[GOOD].get())
wide_by_file = {LOST: vpm.Value(vpm.TYPE_WIDE)}
vpm.kinds_off_the_axis(wide_by_file, NOWHERE)
check("and off the wide shot in the same way",
      wide_by_file[LOST].get() == vpm.TYPE_INTRO, wide_by_file[LOST].get())
outro = {LOST: vpm.Value(vpm.TYPE_OUTRO)}
check("an outro it already carries is not turned into an intro",
      vpm.kinds_off_the_axis(outro, NOWHERE) == []
      and outro[LOST].get() == vpm.TYPE_OUTRO, outro[LOST].get())
check("without a measurement nothing is moved",
      vpm.kinds_off_the_axis({LOST: vpm.Value(vpm.TYPE_CONTENT)}, ()) == [],
      "with no list of placeless files, something moved")

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
