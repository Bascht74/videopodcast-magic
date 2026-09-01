# -*- coding: utf-8 -*-
"""Two cameras never become one camera in the cut.

The cut keys a camera by its name, so two of one name are one: one
colour, one line in the legend, and only the last file plays. In
order: the names handed out, what still falls together, and what the
window shows then -- the start held back, red on the row, the line
under the table, and the file name keeping precedence over both.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")

os.environ["QT_QPA_PLATFORM"] = "offscreen"

import importlib.util

from PySide6 import QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.set_language("en")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def rows(*cameras):
    """Camera lines the way the window keeps them: file, new name."""
    return [(path, vpm.Value(new), None, None) for path, new in cameras]


# One rig, one folder: the take number is what tells the two apart, and
# it is what the guess throws away. The new file names differ, so
# nothing here trips the check about two cameras writing one file.
RIG = rows(("/m/Studio_Camera_A001.mp4", "Ep12_Studio_Anna_Camera_A001"),
           ("/m/Studio_Camera_A002.mp4", "Ep12_Studio_Bernd_Camera_A002"))
# Two cards emptied into two folders. The files carry one name, and
# there is nothing in either of them that says which camera it was.
SAME = rows(("/a/C0001.MP4", "Ep12_C0001_Anna"),
            ("/b/C0001.MP4", "Ep12_C0001_Bernd"))
# Both wrong at once: one name for the files and one for the new file.
BOTH = rows(("/a/C0001.MP4", "Ep12_C0001"),
            ("/b/C0001.MP4", "Ep12_C0001"))
APART = rows(("/m/Podcast_Wide.mp4", "Ep12_Podcast_Wide"),
             ("/m/Podcast_Close.mp4", "Ep12_Podcast_Anna_Close"))

print("1. The names handed out")
named = vpm.camera_tracks_of(RIG)
check("two cameras of one rig carry two names",
      len(set(t for _p, t in named)) == 2,
      "%s off %s" % ([t for _p, t in named],
                     [os.path.basename(p) for p, _t in named]))
check("what tells them apart stands at the end of the name",
      [t[-4:] for _p, t in named] == ["A001", "A002"],
      "the names end on %s" % [t[-4:] for _p, t in named])
short = vpm.camera_tracks_of(APART)
check("a camera whose guess is its own keeps the short name",
      [t for _p, t in short] == ["Wide", "Close"],
      "%s instead of ['Wide', 'Close']" % [t for _p, t in short])
three = vpm.camera_tracks_of(RIG + rows(
    ("/m/Podcast_Wide.mp4", "Ep12_Podcast_Wide")))
check("of three cameras only the two that fell together are lengthened",
      [t for _p, t in three] == ["Studio_Camera_A001", "Studio_Camera_A002",
                                 "Wide"],
      "the three names are %s" % [t for _p, t in three])

print("\n2. What no name off a file name can tell apart")
check("two files of one name in two folders still fall together",
      vpm.camera_tracks_clashing(SAME) == ["C0001"],
      "reported %s off %s" % (vpm.camera_tracks_clashing(SAME),
                              [p for p, _v, _k, _n in SAME]))
check("and one rig in one folder is not reported as falling together",
      vpm.camera_tracks_clashing(RIG) == [],
      "reported %s off %s" % (vpm.camera_tracks_clashing(RIG),
                              [os.path.basename(p)
                               for p, _v, _k, _n in RIG]))


def held_back(camera_lines):
    """What the window says is missing on the assignment sheet."""
    return vpm.missing_conditions(
        ["/m/a.wav"], "Ep12", False,
        [(["/m/a.wav"], vpm.Value("Anna"), vpm.Value(""))],
        camera_lines).get(22)


print("\n3. The window holds the run back")
WANTED = vpm.T('Two cameras are one camera in the cut: %s. Their files '
               'carry the same name, so rename one of them.') % "C0001"
check("the start is held back, and the reason names the camera",
      held_back(SAME) == WANTED,
      "the sheet says %r" % (held_back(SAME),))
check("and it lets go once the two files carry two names",
      held_back(RIG) is None,
      "the sheet says %r" % (held_back(RIG),))
check("the file name has the last word where both are wrong",
      held_back(BOTH) == vpm.T('Two cameras would produce the same file: %s')
      % "Ep12_C0001",
      "the sheet says %r" % (held_back(BOTH),))

print("\n4. The camera's own row says which one")
IN_THE_CUT = vpm.T('Two cameras are one camera in the cut. Their files '
                   'carry the same name, so rename one of them.')
ONE_FILE = vpm.T('Two cameras would produce the same file. The second '
                 'would overwrite the first.')
# Qt deletes a widget with its parent, so the parents outlive the call
# that made them. Without this the fields were gone before they could be
# asked, and the test ended in a traceback instead of a verdict.
sheets = []


def marked(camera_lines):
    """The fields and the line under the table, after one round of marking.

    The real functions on real widgets: mark_red writes a border into
    the style sheet and the reason into the tooltip, and nothing else
    of the window is needed for either.
    """
    sheet = QtWidgets.QWidget()
    sheets.append(sheet)
    fields = [QtWidgets.QLineEdit(sheet) for _x in camera_lines]
    line = QtWidgets.QLabel("", sheet)
    line.setVisible(False)
    vpm.assignment_marks_show(
        [], [], fields, camera_lines, True,
        {"audio_reason": None, "video_reason": line, "voiced": set()})
    # The sheet is never shown, so the answer has to be asked of it and
    # not of the screen.
    return fields, line, line.isVisibleTo(sheet)


fields, line, shown = marked(SAME)
check("the field of a camera that cannot be told apart is marked red",
      all("border" in (f.styleSheet() or "") for f in fields),
      "the style sheets are %s" % [f.styleSheet() for f in fields])
check("and the reason on it is the one about the cut",
      [f.toolTip() for f in fields] == [IN_THE_CUT, IN_THE_CUT],
      "the hints are %s" % [f.toolTip()[:40] for f in fields])
check("the line under the table stands and names the camera",
      shown and line.text() == vpm.T(
          '✕  Two cameras are one camera in the cut (%s). Their files '
          'carry the same name, so rename one of them.') % "C0001",
      "visible %r, saying %r" % (shown, line.text()))
fields, line, shown = marked(RIG)
check("a camera whose name is its own is not marked",
      not any("border" in (f.styleSheet() or "") for f in fields),
      "the style sheets are %s" % [f.styleSheet() for f in fields])
check("and the line goes once the two files carry two names",
      not shown and not line.text(),
      "visible %r, saying %r" % (shown, line.text()))
fields, line, shown = marked(BOTH)
check("where both are wrong the row says the one that can be typed away",
      [f.toolTip() for f in fields] == [ONE_FILE, ONE_FILE],
      "the hints are %s" % [f.toolTip()[:40] for f in fields])

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
