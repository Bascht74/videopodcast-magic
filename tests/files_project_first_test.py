# -*- coding: utf-8 -*-
"""The project is offered before the material is measured; closing stops it.

Two faults of the file list that no test watched, both reported from
the screen:

  Material dragged in was measured first and the project file beside it
  offered afterwards. Saying yes replaced the list with the project's
  own files, so everything measured until then had been measured for
  nothing.

  "Close project" emptied the list and left the measuring running. The
  bar went on naming files that were no longer in the window, and an
  answer arriving after the close put its work back on the bar.

Three parts, in this order: the question comes before the measuring,
yes throws no measurement away, closing breaks the measuring off. A
last judgement says whether all of them ran, so a crash or an exhausted
deadline cannot leave the file green with half its judgements missing.

The window is driven from the outside: the button is clicked, the menu
entry is triggered, and what is read back is what the window shows. The
offer itself is stood in for, so the order can be read without a modal
question; files_project_offered_test.py checks the offer's own behaviour.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
sys.path.insert(0, HERE)

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["VPM_SILENT"] = "1"
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
os.environ["VPM_NO_SPEAKER_SPLIT"] = "1"

import importlib.util
import json
import subprocess
import tempfile
import threading
import time

from PySide6 import QtCore, QtWidgets

app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.update_offer = lambda *a, **k: None
vpm.set_language("en")

# Nothing may sit and wait for a click: a modal window would hold the
# test until the suite kills it.
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok

# How long a condition may take to come true on a slow machine. Waited
# for, never slept past.
PATIENCE = 60.0

began = time.time()
done = 0
bad = []

# How many turns of carry_on() below there are. The last judgement holds
# the file to it, so a crash halfway through cannot pass for a full run.
STEPS = 8


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# ---------------------------------------------------------- the material
ROOT = tempfile.mkdtemp(prefix="vpm-first-")


def media(name):
    """One real but tiny file, so the window has something to measure."""
    path = os.path.join(ROOT, name)
    source = (["-f", "lavfi", "-i", "sine=frequency=440:duration=1"]
              if name.endswith(".wav") else
              ["-f", "lavfi", "-i", "testsrc=size=64x36:rate=30:duration=1",
               "-c:v", "libx264"])
    subprocess.run(["ffmpeg", "-v", "error"] + source + [path, "-y"],
                   check=True)
    return path


DROPPED = [media("Dropped_A.wav"), media("Dropped_B.mov")]
# The third part needs files of its own: the bar keeps one step per
# file, and a file measured once is finished there for good. More of
# them than the prework has threads, so that closing has a queue to
# empty and not only running threads to disown.
BUSY = [media("Busy_%d.%s" % (i, "wav" if i % 2 else "mov"))
        for i in range(8)]
# The project holds other files, so "was this measured before the
# question" has an answer that cannot be read two ways.
INSIDE = [media("Inside_A.wav"), media("Inside_B.mov")]
PROJECT = os.path.join(ROOT, vpm.PROJECT_PREFIX + "First.json")
with open(PROJECT, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "version": "test",
               "timeline": [], "call": [], "production": "First",
               "files": [{"path": p,
                          "kind": "audio" if p.endswith(".wav") else "video"}
                         for p in INSIDE]}, f)

DROPPED_SET = tuple(sorted(DROPPED))
to_add = list(DROPPED)
QtWidgets.QFileDialog.getOpenFileNames = staticmethod(
    lambda *a, **k: (list(to_add), ""))


# ------------------------------------------------------------- the spies
# Both functions are looked up in the module when the window calls them,
# so replacing them here reads the order they are called in.
events = []
answer = {"yes": False}


def offer_spy(widgets, window, state, paths, ask, load):
    events.append(("offer", tuple(sorted(paths))))
    if answer["yes"]:
        load(PROJECT)


_real_warm = vpm.probe_warm


def warm_spy(paths, workers=None):
    events.append(("measure", tuple(sorted(paths))))
    return _real_warm(paths, workers)


vpm.project_offer = offer_spy
vpm.probe_warm = warm_spy

# The envelopes can be held up on purpose, so that closing is caught
# with work still running and what that work reports afterwards arrives
# after the close. Open until the third part asks for it.
gate = threading.Event()
gate.set()
envelope = {"began": [], "ended": []}


def envelope_stub(path, hop_ms=5.0, rate=4000, report=None):
    a = os.path.abspath(path)
    envelope["began"].append(a)
    if report:
        report(0.25)
    # Held, not slept past: the test says when this work comes back.
    gate.wait(PATIENCE)
    if report:
        # The report that arrives after the close. It is the likeliest
        # way the fault returns: it puts the file back on the bar.
        report(0.75)
    envelope["ended"].append(a)
    return {}


vpm.video_envelope = envelope_stub

# The bar is drawn outside gui() from this one plan, so wrapping the
# drawing reads exactly what the bar shows -- the steps still open and
# the line beside it -- rather than guessing at it from a picture.
_real_paint = vpm.total_paint
drawn = {}


def paint_spy(Qt, plan, *rest):
    drawn["plan"] = plan
    return _real_paint(Qt, plan, *rest)


vpm.total_paint = paint_spy


def bar_line():
    """What stands beside the bar: the files still being worked on."""
    plan = drawn.get("plan")
    return plan.line() if plan is not None and plan.busy() else ""


# Every step the bar is given after the project was closed. Watching
# the widget does not see them: a step put back and finished between
# two glances leaves no trace on the screen, and the report that
# arrives after a close is followed at once by the one saying "done".
# So the plan is asked instead of the picture of it.
put_back = []


def short_step(name):
    """A step's name with the folder cut out, or the line is unreadable."""
    head, _colon, path = name.rpartition(":")
    return "%s:%s" % (head, os.path.basename(path)) if head else name


def plan_watched():
    """Write down every step handed to the bar from now on."""
    plan = drawn.get("plan")
    if plan is None:
        put_back.append("no bar was ever drawn, so nothing could be read")
        return
    real_add, real_report = plan.add, plan.report

    def add_spy(name, *rest, **named):
        put_back.append(name)
        return real_add(name, *rest, **named)

    def report_spy(name, *rest, **named):
        put_back.append(name)
        return real_report(name, *rest, **named)

    plan.add = add_spy
    plan.report = report_spy


# ------------------------------------------------------------ the window
def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def button(text):
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(text):
            return w


def entry(text):
    """A menu entry, by the words it carries."""
    for a in win().findChildren(QtCore.QObject):
        if hasattr(a, "trigger") and hasattr(a, "text") \
                and a.text().replace("&", "").strip() == text:
            return a


def file_list():
    """The list of files: the one tree with the File and Kind columns."""
    for w in win().findChildren(QtWidgets.QTreeWidget):
        head = [w.headerItem().text(i) for i in range(w.columnCount())]
        if vpm.T('File') in head and vpm.T('Kind') in head:
            return w


def whole_bar():
    """The bar for the whole job: the one counting in thousandths."""
    for w in win().findChildren(QtWidgets.QProgressBar):
        if w.maximum() == 1000:
            return w


def bar_up():
    bar = whole_bar()
    return bar is not None and bar.isVisible()


def bar_says():
    """Where the bar stands, and whether it is on the screen at all.

    Both, because the two faults look alike in a number: a bar left
    standing at 0 and a bar taken away read the same otherwise.
    """
    bar = whole_bar()
    return ("%d of %d, %s" % (bar.value(), bar.maximum(),
                              "up" if bar.isVisible() else "away")
            if bar is not None else "no bar in the window")


def rows():
    """The file names the list shows, however deep they sit."""
    out = []

    def walk(node):
        for i in range(node.childCount()):
            kid = node.child(i)
            out.append(kid.text(0).strip())
            walk(kid)
    walk(file_list().invisibleRootItem())
    return out


def wait_for(condition, patience=PATIENCE):
    """Wait for a condition, never for a clock."""
    until = time.time() + patience
    while time.time() < until:
        app.processEvents()
        if condition():
            return True
        time.sleep(0.02)
    return False


def watch(seconds, note):
    """Let the window work, writing down every moment the bar stands."""
    until = time.time() + seconds
    while time.time() < until:
        app.processEvents()
        if bar_up() or bar_line():
            note.append("%s -- %s" % (bar_says(), bar_line()))
        time.sleep(0.02)


def add_files():
    """Click "Add files ...", the way somebody at the screen does."""
    button(vpm.T('Add files ...')).click()


def close_project():
    entry(vpm.T('Close project')).trigger()


step = [0]
tries = [0]
after_close = {"began": 0, "seen": []}


def carry_on():
    i = step[0]
    step[0] += 1
    try:
        if i == 0:
            if (win() is None or button(vpm.T('Add files ...')) is None) \
                    and tries[0] < 500:
                tries[0] += 1
                step[0] = 0
                QtCore.QTimer.singleShot(20, carry_on)
                return
            win().show()
            app.processEvents()

        elif i == 1:
            print("1. The question comes before the measuring")
            answer["yes"] = False
            del events[:]
            add_files()
            seen = list(events)
            offers = [e for e in seen if e[0] == "offer"]
            measured = [e for e in seen if e[0] == "measure"]
            check("the question is asked before anything is measured",
                  bool(seen) and seen[0][0] == "offer",
                  "the window did this: %s" % (short(seen),))
            check("and it is asked about the files just added",
                  len(offers) == 1 and offers[0][1] == DROPPED_SET,
                  "asked about %s, wanted %s"
                  % (short(offers), short([("", DROPPED_SET)])))
            check("no means the files are measured exactly once",
                  measured == [("measure", DROPPED_SET)],
                  "measured %s, wanted one round over %s"
                  % (short(measured), short([("", DROPPED_SET)])))

        elif i == 2:
            close_project()
            QtCore.QTimer.singleShot(50, carry_on)
            return

        elif i == 3:
            print("\n2. Yes throws no measurement away")
            answer["yes"] = True
            del events[:]
            add_files()
            seen = list(events)
            offers = [e for e in seen if e[0] == "offer"]
            before = [e for e in seen if e[0] == "measure"][:1] \
                if seen and seen[0][0] == "measure" else []
            # First, or the two below report the list and the order
            # while in truth no question was ever put.
            check("the second set of files is asked about as well",
                  len(offers) == 1,
                  "%d questions asked, wanted 1; the window did this: %s"
                  % (len(offers), short(seen)))
            check("the files the project replaces are not measured first",
                  before == [],
                  "measured before the question: %s (whole run %s)"
                  % (short(before), short(seen)))
            check("the project's own files are in the list instead",
                  all(any(os.path.basename(p) == r for r in rows())
                      for p in INSIDE),
                  "the list shows %d rows %s, wanted %s in them"
                  % (len(rows()), rows(),
                     [os.path.basename(p) for p in INSIDE]))

        elif i == 4:
            print("\n3. Closing the project breaks the measuring off")
            answer["yes"] = False
            close_project()
            app.processEvents()
            del events[:]
            del envelope["began"][:]
            del envelope["ended"][:]
            gate.clear()
            to_add[:] = BUSY
            add_files()
            # Caught in the act: work has to be running before closing
            # it means anything.
            waited = time.time()
            going = wait_for(lambda: bar_up() and bool(envelope["began"]))
            check("the bar stands while the files are being measured",
                  going,
                  "after %.1f s of at most %.0f: bar %s, line %r, "
                  "envelopes begun %d"
                  % (time.time() - waited, PATIENCE, bar_says(), bar_line(),
                     len(envelope["began"])))

        elif i == 5:
            after_close["began"] = len(envelope["began"])
            close_project()
            app.processEvents()
            check("closing takes the bar away at once",
                  not bar_up() and not bar_line(),
                  "the bar stands at %s and says %r"
                  % (bar_says(), bar_line()))
            check("and the list is empty", rows() == [],
                  "the list still shows %d rows, wanted 0: %s"
                  % (len(rows()), rows()))
            # From here on the bar counts nothing: whatever it is
            # handed belongs to a production that is no longer open.
            plan_watched()

        elif i == 6:
            # Now the work that was held comes back. Its report is about
            # files nobody has any more.
            waiting = len(envelope["began"]) - len(envelope["ended"])
            gate.set()
            came_back = wait_for(
                lambda: len(envelope["ended"]) >= after_close["began"])
            watch(1.5, after_close["seen"])
            check("the work that was running comes back", came_back,
                  "%d were waiting, %d came back"
                  % (waiting, len(envelope["ended"])))
            check("nothing new is measured after the close",
                  len(envelope["began"]) == after_close["began"],
                  "%d files had begun at the close, %d have begun now"
                  % (after_close["began"], len(envelope["began"])))
            check("an answer arriving after the close leaves the bar away",
                  not put_back and not after_close["seen"] and not bar_up()
                  and not bar_line(),
                  "%d steps put back on the bar %s, bar seen %d times %s, "
                  "and it now stands at %s saying %r"
                  % (len(put_back),
                     sorted(set(short_step(n) for n in put_back))[:3],
                     len(after_close["seen"]), after_close["seen"][:2],
                     bar_says(), bar_line()))
            check("and it does not fill the emptied list", rows() == [],
                  "the list shows %d rows again, wanted 0: %s"
                  % (len(rows()), rows()))

        elif i == 7:
            # The window goes; the count and the verdict are printed
            # below, where every way out of this test comes past --
            # the crash above, and the deadline that quits the run.
            app.quit()
            return
    except Exception:
        import traceback
        traceback.print_exc()
        bad.append("the test got through its steps without crashing "
                   "[crashed in step %d of %d -- the traceback is above]"
                   % (i + 1, STEPS))
        app.quit()
        return
    QtCore.QTimer.singleShot(50, carry_on)


def short(seen):
    """The events with the folder cut off, or the line is unreadable."""
    return [(what, tuple(os.path.basename(p) for p in paths))
            for what, paths in seen]


QtCore.QTimer.singleShot(0, carry_on)
# The one way out that is not carry_on's. It only closes the window --
# the judgement about it is the last one below, which every way out
# comes past, so an exhausted deadline is red and not a green 0.
QtCore.QTimer.singleShot(240000, app.quit)
sys.argv = ["videopodcast-magic.py"]
vpm.gui()
gate.set()

print("")
check("the test got through all of its steps", step[0] >= STEPS,
      "stopped after step %d of %d, %.0f s gone, %d judgements made"
      % (step[0], STEPS, time.time() - began, done))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
