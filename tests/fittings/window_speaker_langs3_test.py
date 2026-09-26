# -*- coding: utf-8 -*-
"""Whatever is written into the Speakers cell can be read, third slice.

The third of the slices the_program.language_part cuts every language
but English and German into -- window_speaker_cell_fits measures those
two on every run, the other window_speaker_langs files the other
slices, and run.sh sets them aside unless VPM_ALL_LANGUAGES=1; run by
hand, this runs its slice. The checks are window_speaker_cell_fits's word for word.
Sections, as they print: the real window, with a project open, is
dragged as small as it goes in every language and font, and every tree
after that is given what the narrowest window shows of it; the column
holds the two captions that must not wrap; a row grows to a text that
wraps and comes back down; everything the cell can show, up to the
longest report a separation can hand it, is readable; the same in the
widest font we build for; at the narrowest window, across the fonts,
the name field keeps its least width and the column carrying the button
can be brought fully into view; a recording whose voices hang under it
stays open while its cell is written. speaker_cell_measure.py builds
the windows and says how they are measured.
"""
PLATFORM_BOUND = True
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
import speaker_cell_measure as m

import the_program
# This file's slice, by the rule every *_langsN family is cut by.
LANGUAGES = the_program.language_part(m.LANGUAGES, __file__)
# A precondition of the material, not a judgement: a slice with no
# language in it would come out green having looked at nothing.
assert LANGUAGES, "no languages in the slice this file's name asks for"
print(m.languages_line(LANGUAGES))
vpm = m.begin()

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


print("\n1. The window is dragged as small as it goes")
cases, missing, trouble = m.narrowest_windows(LANGUAGES)
check("the window is dragged small in every language and font",
      not missing and not trouble,
      "%d of %d cases measured on a %dx%d screen; missing %s; %s"
      % (len(cases) - len(missing), len(cases), m.SCREEN[0], m.SCREEN[1],
         " ".join(missing[:6]) or "none", " | ".join(trouble[:3])
         or "nothing went wrong"))
least = min(m.NARROW.values(), key=lambda g: g["window"], default=None)
print("  narrowest window %s" % (
    "%d px, %d px of its tree seen, %s" % (
        least["window"], least["shown"], least["case"]) if least else "none"))

print("\n2. The column is measured for what it will hold")
running, counted = m.column_holds(LANGUAGES)
check("the column holds the running caption and its button",
      all(x[1] <= 0 for x in running),
      m.named(running, "%s: %d px short, %d px of column against %d px of "
                       "caption and %d px of button"))
check("and the finished count without wrapping it",
      all(x[1] <= 0 for x in counted),
      m.named(counted, "%s: %d px short, %d px of column against %d px of "
                       "caption"))

print("\n3. The row grows to the text and comes back down")
grows, back = m.rows_follow(LANGUAGES)
# Where no sentence wrapped, nothing was asked: red, not green.
check("a cell whose text has to wrap gets a taller row",
      grows and all(x[1] <= 0 for x in grows),
      m.named(grows, "%s: %d px short of growing, %d px of row for the "
                     "wrapped text against %d px for an empty cell")
      if grows else "in none of %s did the sentence wrap, so no row was "
      "asked to grow" % ", ".join(LANGUAGES))
check("and the row comes back down when the cell is emptied",
      all(x[1] <= 0 for x in back),
      m.named(back, "%s: %d px over, %d px of row after emptying against "
                    "%d px when it was empty"))

print("\n4. Everything the cell can show is readable, every language")
over = m.readable(LANGUAGES)
check("the sentence saying it is not set up is readable in full",
      all(x[1] <= 0 for x in over["missing"]),
      m.named(over["missing"], "%s: %d px over in a label %dx%d"))
check("the running caption stands on one line beside its button",
      all(x[1] <= 0 for x in over["running"]),
      m.named(over["running"], "%s: %d px over one line, %d px wide, "
                               "%d px of text"))
check("a finished count of speakers stands on one line",
      all(x[1] <= 0 for x in over["counted"]),
      m.named(over["counted"], "%s: %d px over one line, %d px wide, "
                               "%d px of text"))
check("a long reason from the separation is readable in full",
      all(x[1] <= 0 for x in over["reported"]),
      m.named(over["reported"], "%s: %d px over in a label %dx%d"))
check("the height a cell asks for is measured, not left to a guess",
      all(x[1] <= 0 for x in over["asked"]),
      m.named(over["asked"], "%s: %d px short, asked for %d of %d needed"))
check("the button keeps its whole caption while a separation runs",
      all(x[1] <= 0 for x in over["button"]),
      m.named(over["button"], "%s: %d px missing, %d px of %d"))

print("\n5. And in a font drawn as wide as the widest we build for")
far = m.readable_wide(LANGUAGES)
check("a long reason is readable in the widest font we build for",
      all(x[1] <= 0 for x in far["reported"]),
      "in a font %d%% as wide, %s" % (m.WIDER, m.named(
          far["reported"], "%s: %d px over in a label %dx%d")))
check("so is the sentence saying it is not set up, in that font",
      all(x[1] <= 0 for x in far["missing"]),
      m.named(far["missing"], "%s: %d px over in a label %dx%d"))
check("and the running caption still on one line, in that font",
      all(x[1] <= 0 for x in far["running"]),
      m.named(far["running"], "%s: %d px over one line, %d px wide, "
                              "%d px of text"))

print("\n6. Nothing is squeezed away or put out of reach")
narrow = m.squeezed(LANGUAGES)
# For the lines only: how far each window is out, in the order named().
out_of_view = [(x[0], max(-x[1], x[1] + x[2] - x[3]), x[2], x[1], x[3])
               for x in narrow]
name_short = [(x[0], vpm.NAME_COLUMN_LEAST - x[4], x[4]) for x in narrow]
check("the column carrying the button can be brought fully into view",
      all(0 <= left and left + wide <= seen
          for _l, left, wide, seen, _n in narrow),
      "scrolled the whole way over, in the tree the narrowest window "
      "leaves; %s" % m.named(out_of_view, "%s: %d px out of view, the "
                             "Speakers column %d px wide at %d in a "
                             "viewport %d px wide"))
check("the field a name is typed into keeps its least width",
      all(name >= vpm.NAME_COLUMN_LEAST
          for _l, _w, _r, _b, name in narrow),
      "at least %d px wanted; %s"
      % (vpm.NAME_COLUMN_LEAST,
         m.named(name_short, "%s: %d px under, %d px wide")))

print("\n7. A recording that is open stays open while its cell is written")
kept = m.stays_open(LANGUAGES)
check("a recording with voices under it stays open when its cell is "
      "written", all(x[1] == 0 for x in kept),
      m.named(kept, "%s: %d folded, open before %r, open after %r"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
