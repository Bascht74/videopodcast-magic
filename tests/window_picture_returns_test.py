# -*- coding: utf-8 -*-
"""A refused format does not outlive the attempt it was about.

Where Qt will not play a file the preview says so and offers a button
in the picture's place. That answer belonged to the player rather than
to the attempt: it stood on beside a picture running again, and a file
loaded afterwards had nowhere to appear at all -- the sound came and
nothing was to be seen.

Two grounds, one claim. A refusal handed to the player while a file
plays, and a file the app really cannot open followed by one it can.
What is asked is only that a picture is on show and that nothing says
"refused" any more -- never which page shows it, and never that a
refusal hides anything in the first place. A refusal counts whether Qt
signals it or only reports the InvalidMedia state.
"""
import os
import sys
import time
import shutil
import tempfile
import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("VPM_SILENT", "1")


from PySide6 import QtCore, QtGui, QtWidgets, QtMultimedia
from PySide6.QtCore import Qt

sys.path.insert(0, HERE)
from fixture_root import fixture

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


def label(text, colour=None, bold=False, large=0):
    return QtWidgets.QLabel(text)


def hint(widget, text):
    widget.setToolTip(text)
    return widget


POLL = 0.02      # the interval: what a wait costs when the thing comes
STILL = 20.0     # a sign of life unchanged this long: it never comes
PATIENCE = 60.0  # the bound a step that keeps moving reaches only broken
# What on_error writes over the file name today, without the name.
REFUSED_SAYS = (vpm.T('%s   --   the app does not know this format')
                % "").strip()


class Wait(object):
    """What a wait came back with, in the shape the FAIL line reads."""

    def __init__(self, took, why_not=""):
        self.took = took
        self.came = took is not None
        self.why_not = why_not

    def __str__(self):
        return "%.2f s" % self.took if self.came else self.why_not


def waited_for(condition, why, alive):
    """Wait on a condition, never on the clock; says what never came.

    What ends a wait that does not come is standstill: the sign of life
    unchanged for STILL seconds. One that keeps moving has PATIENCE. The
    judgement follows either way -- a wait that gave up must not take
    the check with it, only explain the numbers it then reads.
    """
    began_here = time.time()
    last, moved = alive(), began_here
    while True:
        app.processEvents()
        if condition():
            return Wait(time.time() - began_here)
        now = time.time()
        seen = alive()
        if seen != last:
            last, moved = seen, now
        if now - moved >= STILL:
            why_not = ("%.0f s with nothing changing, last %r"
                       % (now - moved, last))
            break
        if now - began_here >= PATIENCE:
            why_not = ("%.0f s still moving, last %r"
                       % (now - began_here, last))
            break
        time.sleep(POLL)
    print("      gave up waiting for %s: %s" % (why, why_not))
    return Wait(None, why_not)


# ------------------------------------------------------------- the material
# One file that plays and one that is no media file at all: twenty
# thousand bytes of noise under a video name. Both inside this test's
# own folder -- the playable one is copied out of the shared material
# rather than read where it lies, so nothing here can write into it.
FOLDER = tempfile.mkdtemp(prefix="vpm_picture_")
PLAYS = os.path.join(FOLDER, "WideCam_A001.mp4")
shutil.copy2(os.path.join(fixture("playertest"), "a.mp4"), PLAYS)
REFUSED = os.path.join(FOLDER, "Guest_B002.mp4")
with open(REFUSED, "wb") as f:
    f.write(os.urandom(20000))

state = {"in_point": None, "out_point": None, "axis": {}}
(WindowSlider, VideoSurface, Player, NoPlayer) = vpm.make_player_widgets(
    QtCore, QtGui, QtWidgets, Qt, label, hint,
    lambda *a, **k: None, lambda *a, **k: None, state)

player = Player()
player.resize(640, 480)
player.setAttribute(Qt.WA_DontShowOnScreen, True)
player.show()
app.processEvents()

pictures = []
player.player.videoSink().videoFrameChanged.connect(
    lambda frame: pictures.append(1))

READY = (QtMultimedia.QMediaPlayer.LoadedMedia,
         QtMultimedia.QMediaPlayer.BufferedMedia)
INVALID = QtMultimedia.QMediaPlayer.InvalidMedia


def status():
    """What moves while Qt opens or refuses a file: its state and error."""
    return (player.player.mediaStatus(), player.player.error())


def running():
    """What moves while a file plays, whether or not a picture comes."""
    return (player.player.playbackState(), player.player.position(),
            len(pictures))


def on_show():
    """The page the stack calls current, and whether it is really up.

    Not "is the video surface visible": which of the two pages carries
    the picture is the preview's own business, and a version that
    answers a refusal by showing the still is just as right.
    """
    page = player.stack.currentWidget()
    name = "video" if page is player.video else "still"
    return name, bool(player.stack.isVisible() and page is not None
                      and page.isVisible())


def said_now():
    """The line above the picture, wherever the preview writes it."""
    return player.title.text()


try:
    print("1. A refusal while a file plays, then the same file on")
    player.load(PLAYS)
    waited_for(lambda: player.player.mediaStatus() in READY,
               "the file to open", status)
    was = len(pictures)
    player.start()
    took = waited_for(lambda: len(pictures) > was,
                      "the picture to run before the refusal", running)
    name, up = on_show()
    check("the picture is up before anything is refused", up,
          "page %r up %s, stack up %s, %d pictures after %s"
          % (name, up, player.stack.isVisible(), len(pictures) - was, took))

    # Refused while it plays, so the refusal meets the page on show.
    # Refused before it had ever played it hid a page nobody saw: the
    # still was on show, the start switched to the picture and put it
    # up, and the refusal was never taken back for this check to see
    # (measured 23.9.2026: three repairs, each of them green alone).
    # What the refusal met is printed with the judgement below.
    # Not a FormatError: on an open file with a picture the preview
    # reads that as the sound track and keeps the picture, and then
    # nothing here ever stood in for it.
    player.on_error(QtMultimedia.QMediaPlayer.ResourceError, "in the test")
    met, met_up = on_show()
    app.processEvents()
    was = len(pictures)
    player.start()
    took = waited_for(lambda: len(pictures) > was,
                      "the picture to run on after the refusal", running)
    name, up = on_show()
    check("the picture is up again once it runs on after a refusal", up,
          "page %r up %s, %d pictures more after %s; the refusal left "
          "page %r up %s"
          % (name, up, len(pictures) - was, took, met, met_up))
    check("and the line above it no longer says the format was refused",
          REFUSED_SAYS not in said_now(),
          "the line says %r, %d pictures more" % (said_now()[:60],
                                                  len(pictures) - was))
    check("and the button that stood in for the picture is gone",
          not player.extern.isVisible(),
          "button up %s, %d pictures more"
          % (player.extern.isVisible(), len(pictures) - was))

    print("\n2. A file the app cannot open, then one it can")
    # Each refusal as Qt gives it: the error signal, or only the state.
    # Both as they arrive, never the state read back -- the file before
    # leaves its state behind, and a read would take that for an answer.
    trouble = []
    player.player.errorOccurred.connect(lambda *a: trouble.append("error"))

    def state_says(status):
        if status == INVALID:
            trouble.append("InvalidMedia")

    player.player.mediaStatusChanged.connect(state_says)
    player.load(REFUSED)
    took = waited_for(lambda: bool(trouble), "the app to refuse the file",
                      status)
    check("the app really cannot play the file put in front of it",
          bool(trouble),
          "%d refusals (%s) after %s, player error %r, status %r, "
          "button up %s"
          % (len(trouble), ", ".join(trouble) or "none", took,
             player.player.error(), player.player.mediaStatus(),
             player.extern.isVisible()))

    player.load(PLAYS)
    took = waited_for(lambda: player.player.mediaStatus() in READY,
                      "the file that plays to open again", status)
    name, up = on_show()
    check("the picture is back once a file that plays is loaded", up,
          "page %r up %s, stack up %s, after %s"
          % (name, up, player.stack.isVisible(), took))

    was = len(pictures)
    player.start()
    ran = waited_for(lambda: player.player.position() > 0,
                     "the file to run on", running)
    check("the file really plays on after the one that was refused",
          ran.came,
          "position %d ms after %s, %d pictures more"
          % (player.player.position(), ran, len(pictures) - was))
    name, up = on_show()
    check("and the picture is still there while that file plays", up,
          "page %r up %s, position %d ms, %d pictures more"
          % (name, up, player.player.position(), len(pictures) - was))
finally:
    try:
        player.player.stop()
    except Exception:
        pass
    shutil.rmtree(FOLDER, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
