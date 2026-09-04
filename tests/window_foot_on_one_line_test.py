# -*- coding: utf-8 -*-
"""The buttons in the footer stand on one line, and say why they are off.

Two things about the same row, and one built them: a button that is
switched off takes no mouse events in Qt, so its tooltip is out of
reach, and a button packed into a frame to carry that text is centred
in the frame while an unpacked neighbour is centred in the row. On an
odd difference the two round apart.

What is judged is where the buttons sit and what a pointer over them
would really show -- never how they were built, so another way of
solving it stays green. The place is compared button against button,
with no pixel written down: a number here would be this machine's.

The limit of the method: offscreen, which is what the suite and the
builder have, Qt draws in the Fusion style and the row was exact there
even while it stood crooked in the native macOS style, which is where
it was seen. So this reads as a guard offscreen and as a measurement under
VPM_LAYOUT_PLATFORM=cocoa, which is where it was made to fall.
"""
import os
import sys
import time
import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
sys.path.insert(0, HERE)

# The platform the suite has. cocoa, windows or xcb runs the same
# measurement in the style a person really sees; the window stays off
# the screen either way, because every show() sets WA_DontShowOnScreen.
PLATFORM = os.environ.get("VPM_LAYOUT_PLATFORM") or "offscreen"
os.environ["QT_QPA_PLATFORM"] = PLATFORM
os.environ["VPM_SILENT"] = "1"
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
# The size the pictures for the manual are taken at. Fixed rather than
# read off a desktop: there is no desktop offscreen.
WINDOW = (1600, 1000)
# How long the window may take to build, and how often it is asked.
# Never reached in the ordinary case, so it costs nothing; running out
# is red, with a line saying what never came.
PATIENCE = 60.0
POLL = 50

from PySide6 import QtCore, QtWidgets

import key_store_apart

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
# The credential store gets a name of its own before the window comes
# up: starting it saves the key it read, and the real one is not this
# test's to touch.
key_store_apart.apart(vpm)
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.update_offer = lambda *a, **k: None
vpm.set_language("en")

_show = QtWidgets.QWidget.show


def offstage(self):
    """Every window is built and laid out, and none reaches a screen."""
    self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
    _show(self)


QtWidgets.QWidget.show = offstage
QtWidgets.QDialog.show = offstage


def drawn(text):
    """What ends up on the screen: & marks a key, && draws one &."""
    return str(text).replace("&&", "\x00").replace("&", "") \
                    .replace("\x00", "&")


def window_of():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x
    return None


def reachable_text(button):
    """What a pointer resting on this button would really show.

    Qt sends the event to the widget under the pointer; one that is
    switched off does not take it and it travels on to the parent. So
    the answer is the first widget from here upward that is switched on
    and carries a text. This asks the behaviour and not the build: it
    is the same answer however somebody arranges for it.
    """
    at = button
    while at is not None:
        if at.isEnabled() and at.toolTip():
            return at.toolTip()
        at = at.parentWidget()
    return ""


WANTED = ("Start", "Dry run", "Settings ...")
found = {}
# The best sight of the row so far. Kept because a button left out of
# the footer never becomes visible, and a failure line saying "0 of 3"
# would send the reader looking for three faults instead of one.
seen = {}
waited = [0.0]


def footer_buttons(window):
    """Whichever of the three footer buttons are up at this moment."""
    out = {}
    for b in app.allWidgets():
        if not isinstance(b, QtWidgets.QPushButton) or not b.isVisible():
            continue
        text = drawn(b.text())
        for want in WANTED:
            if text == drawn(vpm.T(want)):
                out[want] = b
    return out


def look():
    """Measure once the row stands, and give up on standstill."""
    window = window_of()
    if window is not None:
        window.resize(*WINDOW)
    app.processEvents()
    ready = footer_buttons(window) if window is not None else {}
    if len(ready) > len(seen):
        seen.clear()
        seen.update(ready)
    # The sign of life is the row itself: three buttons, up, and laid
    # out to a real width. A widget Qt has not reached yet is 100 wide
    # and would be measured as though it were finished.
    if len(ready) == len(WANTED) and all(b.width() > 0 and b.height() > 0
                                         for b in ready.values()):
        found.update(ready)
        found["window"] = window
        app.quit()
        return
    waited[0] += POLL / 1000.0
    if waited[0] >= PATIENCE:
        app.quit()
        return
    QtCore.QTimer.singleShot(POLL, look)


QtCore.QTimer.singleShot(POLL, look)
vpm.gui()

print("1. The row is there to be measured")
check("all three footer buttons come up and are laid out",
      len(found) == len(WANTED) + 1,
      "%d of %d found after %.1f s of at most %.1f -- %s came up, %s "
      "never did"
      % (len(seen), len(WANTED), waited[0], PATIENCE,
         sorted(seen) or "none", [n for n in WANTED if n not in seen]
         or "none"))
if len(found) != len(WANTED) + 1:
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)

window = found["window"]
place = {}
for name in WANTED:
    button = found[name]
    top = button.mapTo(window, QtCore.QPoint(0, 0)).y()
    place[name] = (top, top + button.height())
print("   %s in the %s style"
      % (", ".join("%s %d..%d" % (n, place[n][0], place[n][1])
                   for n in WANTED), PLATFORM))

print("\n2. They stand on one line")
tops = sorted(set(place[n][0] for n in WANTED))
check("every footer button begins at the same height",
      len(tops) == 1,
      "%s -- the tops are %d apart, wanted none"
      % ({n: place[n][0] for n in WANTED}, tops[-1] - tops[0]))
bottoms = sorted(set(place[n][1] for n in WANTED))
check("and every one of them ends at the same height",
      len(bottoms) == 1,
      "%s -- the bottoms are %d apart, wanted none"
      % ({n: place[n][1] for n in WANTED}, bottoms[-1] - bottoms[0]))

print("\n3. A button that is off still says why")
# The two run buttons are switched off over an empty window, which is
# the state this is about: asked of a button that is on, the question
# would answer itself.
off = [n for n in ("Start", "Dry run") if not found[n].isEnabled()]
check("both run buttons are switched off here, so the question means "
      "something",
      off == ["Start", "Dry run"],
      "switched off: %s, wanted both" % (off or "neither",))
# Which text shows is not fixed here: Start's frame carries the reason
# the run cannot begin, which is better than the button's own line and
# changes as the reason does. What is fixed is that something shows.
#
# Written out one by one rather than looped: a name put together at run
# time leaves the register one wording for four judgements, and then no
# row can say which of the four was ever seen red.
start, dry = found["Start"], found["Dry run"]
check("Start carries a text of its own saying what it does",
      bool(start.toolTip()),
      "it says %r, wanted a sentence" % (start.toolTip()[:70],))
check("and a pointer on Start while it is off reaches a text at all",
      bool(reachable_text(start)),
      "the button says %r and a pointer would show %r -- wanted "
      "something rather than nothing"
      % (start.toolTip()[:50], reachable_text(start)[:60]))
check("Dry run carries a text of its own saying what it does",
      bool(dry.toolTip()),
      "it says %r, wanted a sentence" % (dry.toolTip()[:70],))
check("and a pointer on Dry run while it is off reaches a text at all",
      bool(reachable_text(dry)),
      "the button says %r and a pointer would show %r -- wanted "
      "something rather than nothing"
      % (dry.toolTip()[:50], reachable_text(dry)[:60]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
