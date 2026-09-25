# -*- coding: utf-8 -*-
"""The line under the file list counts the rows the time axis marked.

A row the axis refused is red and says it does not fit; the line under
the list may not say "nothing to fault" beside it. In order: refused
rows counted as a fault in red, three blocks as one, a file placed by
its timecode alone as a note, also beside a note of the check, one set
to the intro as neither, nothing off the axis as nothing to fault, the
line following the rows when they are painted again after the check,
and "checking" kept while the check runs. Real widgets, rows marked by
the program's own painter; the axis verdict is set by hand, and nothing
reads a file.
"""
import os
import shutil
import sys
import tempfile
import threading
import time
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import the_program

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import Qt

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


class Plan(object):
    """The progress plan of the window, which this test does not show."""

    def begin(self, *a):
        pass

    def done(self, *a):
        pass

    def drop(self, *a):
        pass


class Bridge(object):
    """The signal the check answers through, by name only."""
    preflight = "preflight"


class Value(object):
    """A field of the window: a Kind, or the multitrack tick."""

    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


# Names only: nothing here opens a file, so nothing is built.
D = tempfile.mkdtemp(prefix="vpm_line_")
GUEST = os.path.join(D, "Guest_Take0021A_Timecode.wav")
BLOCKS = [os.path.join(D, "Presenter_REC0002%d.wav" % i) for i in (1, 2, 3)]
COPRES = os.path.join(D, "CoPresenter_REC00018.wav")
WIDE = os.path.join(D, "WideCam_01011855_C001.mov")
GUESTCAM = os.path.join(D, "GuestCam_01011858_C003.mov")
FILES = ([(p, "audio") for p in [GUEST] + BLOCKS + [COPRES]]
         + [(WIDE, "video"), (GUESTCAM, "video")])

state = {"audio_recordings": 3}
kinds = vpm.ByFile()
kinds[WIDE] = Value(vpm.TYPE_CONTENT)
kinds[GUESTCAM] = Value(vpm.TYPE_CONTENT)
state["clip_kinds"] = kinds
sheet = QtWidgets.QVBoxLayout()
(items, line, _stripes, _marks, _MARKS, _word, set_mark,
 item) = vpm.make_file_list(Qt, QtGui, QtWidgets, sheet, state)
rows = vpm.ByFile()
for p in (GUEST, COPRES, WIDE, GUESTCAM):
    rows[p] = item(items, os.path.basename(p), D, "audio", files_for_it=[p])
# Three blocks, one row: the way the list hangs a recording of blocks.
chain = item(items, os.path.basename(BLOCKS[0]), D, "audio",
             files_for_it=BLOCKS)
for p in BLOCKS:
    rows[p] = chain
fill_in, kick_off = vpm.make_preflight(
    state, FILES, Plan(), Bridge(), lambda *a: None, line, set_mark,
    lambda *a: None, lambda *a: None, rows, set(), lambda: [],
    Value(False), [], kinds)


def axis_says(weak=(), nowhere=()):
    """Leave a measurement's verdict in the state, and paint the rows."""
    state["weak"] = set(vpm.path_key(p) for p in weak)
    state["no_place"] = set(vpm.path_key(p) for p in nowhere)
    vpm.weak_marks_show(state, rows)


def ink(p):
    return rows[p].foreground(2).color().name()


def colour_of_line():
    return line.styleSheet()


def ends(text):
    return "%r, wanted it to end in %r" % (line.text()[-80:], text)


print("\n1. Rows the axis refused")
axis_says(weak=[GUEST, BLOCKS[0], WIDE], nowhere=[GUEST, BLOCKS[0]])
fill_in([])
two = vpm.TN(2, ' -- %s file does not fit the others',
             ' -- %s files do not fit the others') % vpm.number_text(2, 0)
check("the line counts the rows that do not fit",
      line.text().endswith(two), ends(two))
check("the line is red while a row is red",
      ink(GUEST) == vpm.COLOURS["error"]
      and vpm.COLOURS["error"] in colour_of_line(),
      "row %s, line %r, wanted %s in both"
      % (ink(GUEST), colour_of_line(), vpm.COLOURS["error"]))
axis_says(weak=[GUEST] + BLOCKS, nowhere=[GUEST] + BLOCKS)
fill_in([])
check("a recording in three blocks is one file that does not fit",
      line.text().endswith(two), ends(two))

print("\n2. A file placed by its timecode alone")
axis_says(weak=[WIDE])
fill_in([])
# In the row's own words: what its note says under the folder.
one = vpm.T(' -- 1 note: %s') % "%s: %s" % (
    os.path.basename(WIDE), rows[WIDE].text(2).split("\n", 1)[-1].strip())
check("a file placed by its timecode alone is one note in the line",
      line.text().endswith(one)
      and vpm.COLOURS["warning"] in colour_of_line(),
      ends(one) + ", colour %r" % colour_of_line())
hint = vpm.Finding("hint", "Level", "quiet", file=COPRES)
fill_in([hint])
notes = vpm.T(' -- %s notes') % vpm.number_text(2, 0)
check("a note of the check and one of the axis are counted together",
      line.text().endswith(notes), ends(notes))

print("\n3. A file set to the intro")
kinds[GUESTCAM] = Value(vpm.TYPE_INTRO)
axis_says(weak=[GUESTCAM], nowhere=[GUESTCAM])
fill_in([])
quiet = vpm.T(' -- nothing to fault.')
check("a file set to the intro is no fault in the line",
      line.text().endswith(quiet), ends(quiet) + ", row ink %s"
      % ink(GUESTCAM))
kinds[GUESTCAM] = Value(vpm.TYPE_CONTENT)

print("\n4. The rows painted again after the check")
axis_says()
fill_in([])
app.processEvents()
check("with nothing off the axis the line says nothing to fault",
      line.text().endswith(quiet), ends(quiet))
# Nothing calls the line here: the axis lands, then a Kind changes,
# and each time only the rows are painted, as the window does.
axis_says(weak=[GUEST, BLOCKS[0], GUESTCAM],
          nowhere=[GUEST, BLOCKS[0], GUESTCAM])
app.processEvents()
landed = line.text()
kinds[GUESTCAM] = Value(vpm.TYPE_INTRO)
vpm.weak_marks_show(state, rows)
app.processEvents()
three = vpm.TN(3, ' -- %s file does not fit the others',
               ' -- %s files do not fit the others') % vpm.number_text(3, 0)
check("the line follows the rows when they are painted again",
      landed.endswith(three) and line.text().endswith(two),
      "%r when the axis landed, wanted %r; %r after the intro, wanted %r"
      % (landed[-60:], three, line.text()[-60:], two))
kinds[GUESTCAM] = Value(vpm.TYPE_CONTENT)

print("\n5. While the check runs")
# The check is held until it is let go, so "still running" is a state
# and not a moment; the stand-in answers nothing of its own.
held = threading.Event()
answered = []
vpm.preflight.collect_findings = lambda *a, **k: (held.wait(60), [])[1]
fill_in2, kick_off2 = vpm.make_preflight(
    state, FILES, Plan(), Bridge(), lambda _s, f: answered.append(f), line,
    set_mark, lambda *a: None, lambda *a: None, rows, set(), lambda: [],
    Value(False), [], kinds)
kick_off2()
running = line.text()
axis_says(weak=[WIDE])
app.processEvents()
check("the line keeps saying the check runs until it answers",
      line.text() == running == vpm.T('checking ...'),
      "%r before the axis landed, %r after, wanted %r both times"
      % (running, line.text(), vpm.T('checking ...')))
held.set()
waited = 0.0
while not answered and waited < 60.0:
    time.sleep(0.05)
    waited += 0.05
shutil.rmtree(D, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
