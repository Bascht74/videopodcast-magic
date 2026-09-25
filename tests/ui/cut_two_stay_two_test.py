# -*- coding: utf-8 -*-
"""Two cameras never become one camera in the cut.

The cut keys a camera by its name, so two of one name would be one: one
colour, one line in the legend, and only the last file plays. In
order: the names handed out; two files of one name told apart by a
number, as the run tells them; and where two cameras are given one new
file name, the start held back, red on the row and the line under the
table -- and none of it for two files of one name named apart.
"""
import os
import sys
import time
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import the_program

SCRIPT = the_program.SCRIPT

os.environ["QT_QPA_PLATFORM"] = "offscreen"


from PySide6 import QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
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
# One name for the files, and one new file name typed for both.
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

print("\n2. Two files of one name")
paired = [t for _p, t in vpm.camera_tracks_of(SAME)]
check("two files of one name in two folders are told apart by a number",
      paired == ["C0001", "C0001 2"],
      "the cut names them %r off %s, wanted ['C0001', 'C0001 2']"
      % (paired, [p for p, _v, _k, _n in SAME]))


def held_back(camera_lines):
    """What the window says is missing on the assignment sheet."""
    return vpm.missing_conditions(
        ["/m/a.wav"], "Ep12", False,
        [(["/m/a.wav"], vpm.Value("Anna"), vpm.Value(""))],
        camera_lines).get(22)


print("\n3. Two cameras given one new file name")
check("two cameras given one new file name hold the start back",
      held_back(BOTH) == vpm.T('Two cameras would produce the same file: %s')
      % "Ep12_C0001",
      "the sheet says %r" % (held_back(BOTH),))
check("and it lets go once the two carry two names",
      held_back(RIG) is None,
      "the sheet says %r" % (held_back(RIG),))

print("\n4. The camera's own row says which one")
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


fields, line, shown = marked(BOTH)
check("both fields of one new file name are marked red with why",
      all("border" in (f.styleSheet() or "") for f in fields)
      and [f.toolTip() for f in fields] == [ONE_FILE, ONE_FILE],
      "the style sheets are %s, the hints %s"
      % ([f.styleSheet() for f in fields],
         [f.toolTip()[:40] for f in fields]))
check("the line under the table stands and names the file",
      shown and line.text() == vpm.T(
          '✕  Two cameras would produce the same file (%s). The second '
          'would overwrite the first.') % "Ep12_C0001",
      "visible %r, saying %r" % (shown, line.text()))
fields, line, shown = marked(SAME)
check("two files of one name with two new names are not marked",
      not any("border" in (f.styleSheet() or "") for f in fields)
      and not shown,
      "the style sheets are %s, the line visible %r saying %r"
      % ([f.styleSheet() for f in fields], shown, line.text()))
fields, line, shown = marked(RIG)
check("a camera whose name is its own is not marked",
      not any("border" in (f.styleSheet() or "") for f in fields),
      "the style sheets are %s" % [f.styleSheet() for f in fields])

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
