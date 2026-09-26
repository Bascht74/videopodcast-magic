# -*- coding: utf-8 -*-
"""Does every visible caption fit its field, second slice of languages?

The second of the slices the_program.language_part cuts every language
but English and German into -- window_captions_fit measures those two
on every run, the other window_captions_langs files the other slices,
and run.sh sets them aside unless VPM_ALL_LANGUAGES=1; run by hand,
this runs its slice. The
checks are window_captions_fit's word for word: the window measured,
the project in, the program finished, no thread or timer at work, the
zoom row, its reading and the output pane's face, every caption.
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
import captions_measure as m

import the_program
# This file's slice, by the rule every *_langsN family is cut by.
LANGUAGES = the_program.language_part(m.LANGUAGES, __file__)
# A precondition of the material, not a judgement: a slice with no
# language in it would come out green having looked at nothing.
assert LANGUAGES, "no languages in the slice this file's name asks for"
print("languages: %s" % ", ".join(LANGUAGES))

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


for language, out in m.windows(LANGUAGES):
    report = m.report_of(out)
    if report is None:
        check("%s: the window was measured" % language, False,
              "nothing came back")
        for x in out.rstrip().split("\n")[-20:]:
            print("    " + x[:150])
        continue
    if report.get("error") or not report.get("seen"):
        check("%s: the window was measured" % language, False,
              report.get("error", "no widget was looked at"))
        continue
    m.said_beside(language, report)
    if report.get("project"):
        cut = (" (a shortened wait: another language had run out of "
               "patience first)" if report.get("quick") else "")
        check("%s: the project came in" % language,
              report.get("filled") is True,
              "no table, tree or list in the window held a row %s s after "
              "'Open project' was pressed%s" % (report.get("waited"), cut))
        check("%s: the program had finished before it was measured"
              % language, report.get("settled") is True,
              "measured %s s after 'Open project', its plan %s, the "
              "captions unchanged for %s looks of 0.2 s (2 wanted)%s"
              % (report.get("waited"), "still busy" if report.get("busy")
                 else "done", report.get("still"), cut))
        check("%s: no thread or timer was still at work when measured"
              % language, report.get("in_hand") == [],
              "measured %s s after 'Open project' with %s still running, "
              "so a caption was measured that was about to change%s"
              % (report.get("waited"), ", ".join(report.get("in_hand")
                                                 or ["nothing reported"]),
                 cut))
    # The zoom row. A button that walks away as it is pressed cannot be
    # pressed twice, and the reading beside it is what pushed it.
    row = report.get("zoom_row") or {}
    if row.get("found") != 3 or not row.get("label"):
        print("  the zoom buttons were not on screen -- not measured.")
    else:
        check("%s: the zoom buttons hold their place" % language,
              not any(row["moved"]),
              "moved by %s pixels when the reading appeared" % row["moved"])
        check("%s: the reading stands there before anybody zooms" % language,
              bool((row.get("text") or "").strip()),
              "with no click at all it reads %r" % (row.get("text"),))
        low, high = row.get("digits") or [0.0, 0.0]
        evidence = m.evidence(row)
        if m.face_left_out(row, evidence):
            check("%s: the reading is drawn with a fixed width" % language,
                  bool(row.get("fixed_pitch")), evidence)
            # The pane a run writes into asks for a family by name and
            # falls to the alias where the name is absent -- the same
            # door as the reading, and it stood open unmeasured.
            pane = report.get("output_pane") or {}
            check("%s: the output pane is drawn with a fixed width" % language,
                  pane.get("found") == 1 and bool(pane.get("fixed_pitch")),
                  "the text pane of the Output tab asks for %r and draws "
                  "%r, fixed pitch %s"
                  % (pane.get("family"), pane.get("drawn"),
                     pane.get("fixed_pitch"))
                  if pane.get("found") == 1 else
                  "%d text panes of the class found where one was expected"
                  % pane.get("found", 0))
            check("%s: every digit in the reading is one width" % language,
                  high - low < m.SAME_WIDTH,
                  "drawn in %r, the digits measure %.2f to %.2f px; the "
                  "field is pinned to the width of %r, and that is the "
                  "widest reading there is only while every digit is as "
                  "wide as a nought"
                  % (row.get("drawn"), low, high, row.get("widest")))
        check("%s: the pinned width holds the widest reading" % language,
              row.get("width", 0) >= row.get("needs", 0),
              "pinned to %d px, but %r needs %d px in the font it is "
              "drawn in (%s)"
              % (row.get("width", 0), row.get("widest"), row.get("needs", 0),
                 row.get("drawn")))

    found = sorted(report["found"], key=lambda f: -f["short"])
    # The findings go on the line that fails, not only under it: a build
    # machine's log keeps the lines that say FAIL and drops the rest, and
    # the machine that could name a caption too narrow on Windows is the
    # one nobody here can run.
    check("%s: every caption fits its field" % language, not found,
          "%d cut off%s" % (len(found), "".join(
              "; %s short by %d px in %s: %r"
              % (f["kind"][:14], f["short"], f["box"][:30], f["text"][:60])
              for f in found)))
    for f in found:
        print("    %-14s short by %4d px  in %-30s  %r"
              % (f["kind"][:14], f["short"], f["box"][:30], f["text"][:60]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
