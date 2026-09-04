# -*- coding: utf-8 -*-
"""The box that shows the prework goes away once the prework is over.

It is put up by a report and taken down by one, and the last report can
reach the window while the thread that sent it is still counted as
working -- then nothing follows and the box stands for good. The lock
below makes that order instead of waiting for a busy machine to fall
into it. The sections: the box comes up, its bar reaches the end, and
the box goes again.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import sys, tempfile, threading, time
os.environ["QT_QPA_PLATFORM"] = "offscreen"
# An empty cache of its own: with what was measured kept from an earlier
# run there is no prework to do and no box to watch.
os.environ["VPM_CACHE"] = tempfile.mkdtemp(prefix="vpm_prework_cache_")
from PySide6 import QtWidgets, QtCore
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: [("Podcast_Multitrack", "u1", True)]
vpm.load_api_key = lambda: ""
sys.path.insert(0, HERE)
from fixture_project import fixture_project

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def finish():
    """The one way out, whatever happened above."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


PROJECT, MEDIA = fixture_project("preworkbox")
if PROJECT is None:
    print("SKIPPED: no test project -- point VPM_MEDIA at a folder "
          "holding videopodcast-magic_Interview_2.json (looked in %s)" % MEDIA)
    finish()
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (PROJECT, ""))

# ------------------------------------------------- the order, made not waited
MAIN = threading.current_thread()
# What a working thread pays for every lock it takes. It has to outlast
# the window's answer to a report, which is immediate, and nothing else.
HOLD = 0.05


class SlowLock(object):
    """A real lock that costs a working thread a moment to take.

    The thread that finishes the last piece reports it and counts itself
    out afterwards. Whether the window hears the report before or after
    that is a race, and this settles it the way a loaded machine does:
    the two locks on the thread's way out are taken slowly, so the
    window always answers the last report while the thread is still in.
    """

    def __init__(self):
        self.real = threading.Lock()

    def __enter__(self):
        if threading.current_thread() is not MAIN:
            time.sleep(HOLD)
        return self.real.__enter__()

    def __exit__(self, *why):
        return self.real.__exit__(*why)

    def acquire(self, *a, **k):
        if threading.current_thread() is not MAIN:
            time.sleep(HOLD)
        return self.real.acquire(*a, **k)

    def release(self):
        return self.real.release()

    def locked(self):
        return self.real.locked()


class SlowThreading(object):
    """The threading module the program imported, with its locks slowed."""

    Lock = staticmethod(SlowLock)

    def __getattr__(self, name):
        return getattr(threading, name)


vpm.threading = SlowThreading()


# ------------------------------------------------------------- reading it
def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def bars(range_of):
    """Every bar in the window counting in that range.

    The footer bar counts in thousandths and the prework bar in per
    cent, and a range outlives every change of looks.
    """
    if win() is None:
        return []
    return [w for w in win().findChildren(QtWidgets.QProgressBar)
            if w.maximum() == range_of]


def box():
    """The prework bar, and the box it sits in."""
    found = bars(100)
    return found[0] if len(found) == 1 else None


def up():
    """Is the prework box put up?

    Asked of the box and not of the bar, and with isHidden rather than
    isVisible: the box sits on the assignment sheet, so a run reading
    visibility would only ever see it while that sheet is in front,
    and what the program itself puts up and takes down is the box.
    """
    b = box()
    return b is not None and not b.parent().isHidden()


def life():
    """A reading that moves only because the prework is getting on.

    The bar's own value and the lines under it, which name the files
    still being read. Both stand still the moment the work does.
    """
    b = box()
    return (b.value() if b is not None else None,
            b.parent().isHidden() if b is not None else None,
            tuple(w.text() for w in win().findChildren(QtWidgets.QLabel)))


def button(text):
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(text):
            return w


# How many tries in a row without the window moving a step may spend.
# Time in which it moves is not counted, so a slow machine takes longer
# and only a window that is stuck gives up. The box is taken down after
# a wait of its own, so a standstill here is measured in seconds.
STEP = 100
STILL = {"the box to come up": 100, "the box to go again": 100}
seen = {"shown": 0, "high": 0, "gone": False, "left": {}}
watch = {"sign": None, "idle": 0, "moved": 0, "tries": 0, "since": 0.0}
n = [0]
NOTHING = object()


def hold(ok, what):
    """Wait for the window to get there, and give up at a standstill.

    Giving up is not the end of the run: what is missing is written
    down and the steps go on to the judgements, so the red line comes
    from the check and not from a wait that swallowed it.
    """
    if ok:
        watch.update(sign=NOTHING, idle=0, moved=0, tries=0,
                     since=time.time())
        return False
    watch["tries"] += 1
    now = life()
    if now != watch["sign"]:
        if watch["sign"] is not NOTHING:
            watch["moved"] += 1
        watch["sign"] = now
        watch["idle"] = 0
        watch["since"] = time.time()
    else:
        watch["idle"] += 1
    if watch["idle"] >= STILL[what]:
        # The clock, not the number of tries times their interval: on a
        # machine with something else to do a try takes longer than it
        # was asked to, and the second number would understate it.
        seen["left"][what] = ("nothing moved for %.1f s, %d tries in a row, "
                              "%d changes before that"
                              % (time.time() - watch["since"], watch["idle"],
                                 watch["moved"]))
        watch.update(sign=NOTHING, idle=0, moved=0, tries=0,
                     since=time.time())
        return False
    n[0] -= 1
    QtCore.QTimer.singleShot(STEP, step)
    return True


def look():
    """What the box is doing, read on every turn."""
    if up():
        seen["shown"] += 1
        b = box()
        seen["high"] = max(seen["high"], b.value())
    elif seen["shown"]:
        seen["gone"] = True


def judge():
    """The three judgements, and every path through the test reaches them."""
    if done:
        return
    check("the prework box comes up while the prework runs",
          seen["shown"] > 0,
          "seen up on %d turns of %d ms; %d bar(s) count in per cent and "
          "%d in thousandths; %s"
          % (seen["shown"], STEP, len(bars(100)), len(bars(1000)),
             seen["left"].get("the box to come up", "it came")))
    check("the prework bar reaches the end", seen["high"] >= 100,
          "got to %d of 100" % seen["high"])
    check("the prework box goes away when the work is done",
          seen["shown"] > 0 and seen["gone"],
          "up on %d turns, gone afterwards %s; %s"
          % (seen["shown"], seen["gone"],
             seen["left"].get("the box to go again", "it went")))
    app.quit()


def step():
    look()
    i = n[0]; n[0] += 1
    try:
        if i == 0:
            if win() is None:
                n[0] -= 1
                QtCore.QTimer.singleShot(STEP, step)
                return
            win().show(); win().resize(1400, 900); app.processEvents()
        elif i == 1:
            if hold(button(vpm.T('Open project ...')[:8]) is not None,
                    "the box to come up"):
                return
            opener = button(vpm.T('Open project ...')[:8])
            if opener is None:
                seen["left"]["the box to come up"] = "no Open project button"
                judge(); return
            opener.click()
        elif i == 2:
            if hold(up(), "the box to come up"):
                return
        elif i == 3:
            if hold(seen["shown"] and not up(), "the box to go again"):
                return
            judge(); return
    except Exception:
        import traceback; traceback.print_exc()
        bad.append("the run threw")
        app.quit(); return
    QtCore.QTimer.singleShot(STEP, step)


# The backstop, and not the wait: it catches a window whose steps have
# stopped coming back at all. Both waits above give up on their own and
# say so, so this can never cut one of them short -- and it gives up
# into the judgements rather than instead of them.
GUARD = 2 * sum(STILL.values()) * STEP + 60000
QtCore.QTimer.singleShot(GUARD, judge)
QtCore.QTimer.singleShot(STEP, step)
sys.argv = ["videopodcast_magic.py"]
vpm.gui()
if not done:
    # A run that proved nothing must not read like one that proved
    # everything. Not a judgement about the program -- it says only
    # that this run has nothing to say about it.
    bad.append("the steps never reached the judgements [stopped at step %d "
               "after %.0f s, the box seen up on %d turns]"
               % (n[0], time.time() - began, seen["shown"]))
    print("FAIL: " + bad[-1])
finish()
