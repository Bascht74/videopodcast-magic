# -*- coding: utf-8 -*-
"""A desktop switched to dark leaves no light ground standing in the window.

The window is built offscreen with the desktop light, switched to dark
and back. Sections: the window comes up and stands still, the ground
behind the sheets is a colour of the palette in force, the switch
arrives, the ground changes with the desktop, no colour at all is left
standing over a part of the picture, and the ground comes back. The
limit: offscreen Qt reports no colour scheme, so the desktop is stood
in for at the one place the window asks it.
"""
import os
import sys
import time

import the_program

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtGui, QtWidgets

app = QtWidgets.QApplication(sys.argv[:1])
m = the_program.load()

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# The window asks the desktop once, here. Offscreen Qt answers
# ColorScheme.Unknown whatever the machine does, so this one answer is
# stood in for and everything under it runs as on a real desktop.
UI = m.window()
DARK = [False]
UI.desktop_is_dark = lambda *a, **k: DARK[0]

# Milliseconds between looks, looks without a change that count as
# settled, and looks without a change that count as never getting
# there. Standstill, not elapsed time: a slow machine only takes longer.
PAUSE = 120
SETTLED = 3
STILL = 150
# How much of the picture one colour may keep across the switch. The
# ground kept 18.1 % of it before this was mended, and 0 after.
SHARE = 0.01


def top():
    """The window, once Qt has one with that title."""
    for w in app.topLevelWidgets():
        if "Video Podcast Magic" in w.windowTitle():
            return w
    return None


def picture():
    """The window as an image, and the image is the caller's to hold.

    Whoever reads points out of it keeps it in a name of its own: a
    picture nobody holds is freed while it is still being read.
    """
    return top().grab().toImage().convertToFormat(QtGui.QImage.Format_RGB32)


def sign_of_life():
    """Something the window itself changes while it is still building.

    Read without grabbing: a grab every tenth of a second is the
    dearest thing in the run, and what a wait needs is a value that
    moves while work is being done.
    """
    window = top()
    if window is None:
        return (len(app.topLevelWidgets()), len(app.allWidgets()))
    return (window.width(), window.height(), len(app.allWidgets()),
            tuple(k.text() for k in window.findChildren(QtWidgets.QLabel)
                  if k.isVisible()))


def ground_of(image):
    """What the window paints where nothing of its own stands.

    Two points in from the corner: the outermost row is the window's
    own edge, which the style draws.
    """
    return image.pixelColor(2, 2).name()


def in_force():
    """Every colour the palette in force holds, as Qt spells them."""
    return set(QtGui.QColor(v).name() for v in m.COLOURS.values())


def settle(seconds):
    """Let the window work for a while without blocking on the clock."""
    end = time.time() + seconds
    while time.time() < end:
        app.processEvents(QtCore.QEventLoop.AllEvents, 50)
        time.sleep(0.01)


def switch(dark):
    """Do to the window what a desktop switched over does to it."""
    DARK[0] = dark
    app.styleHints().colorSchemeChanged.emit(
        QtCore.Qt.ColorScheme.Dark if dark else QtCore.Qt.ColorScheme.Light)
    settle(2.0)


def standing_still(image_a, image_b):
    """How often each colour is the same point in both pictures.

    Every other point in each direction: the ground is a surface, and a
    quarter of the points says as much about it as all of them.
    """
    seen = {}
    read = 0
    for y in range(0, image_a.height(), 2):
        for x in range(0, image_a.width(), 2):
            read += 1
            here = image_a.pixel(x, y)
            if here == image_b.pixel(x, y):
                seen[here] = seen.get(here, 0) + 1
    return read, seen


watch = {"sign": None, "idle": 0, "looks": 0}
read_through = [False]
trouble = [""]


def measure():
    """The four readings, once the window stands there."""
    light = picture()
    ground_light = ground_of(light)
    palette_light = in_force()
    check("the ground the window paints is a colour of the palette",
          ground_light in palette_light,
          "%s, and the palette holds %s"
          % (ground_light, ", ".join(sorted(palette_light))))
    switch(True)
    dark = picture()
    ground_dark = ground_of(dark)
    palette_dark = in_force()
    check("the ground goes with the desktop into dark",
          ground_dark != ground_light and ground_dark in palette_dark,
          "%s in light, %s in dark, ON_DARK %r, and the dark palette "
          "holds %s" % (ground_light, ground_dark, m.ON_DARK[0],
                        ", ".join(sorted(palette_dark))))
    read, seen = standing_still(light, dark)
    worst = max(seen.values()) if seen else 0
    colour = ""
    for value, count in seen.items():
        if count == worst:
            colour = QtGui.QColor.fromRgb(value).name()
            break
    check("no colour is left standing over a part of the window",
          worst <= read * SHARE,
          "%s stood still at %d of %d points, %.1f %%, and %.1f %% is the "
          "most allowed" % (colour or "nothing", worst, read,
                            100.0 * worst / read, 100.0 * SHARE))
    switch(False)
    again = picture()
    ground_back = ground_of(again)
    check("and the ground comes back when the desktop does",
          ground_back == ground_light,
          "%s before, %s in dark, %s after" % (ground_light, ground_dark,
                                               ground_back))
    read_through[0] = True


def step():
    """Wait for the window to stand still, then read it.

    What runs out is standstill, not elapsed time: every look that
    finds anything moved starts the count again, so a machine that is
    slow only takes longer and one that is stuck is still caught.
    """
    try:
        sign = sign_of_life()
        watch["looks"] += 1
        if sign == watch["sign"]:
            watch["idle"] += 1
        else:
            watch["sign"] = sign
            watch["idle"] = 0
        if watch["idle"] >= SETTLED and top() is not None:
            measure()
            app.quit()
            return
        if watch["idle"] >= STILL:
            trouble[0] = ("nothing moved for %d looks, and the window was %s"
                          % (watch["idle"],
                             "there" if top() is not None else "never there"))
            app.quit()
            return
    except Exception:
        import traceback
        traceback.print_exc()
        trouble[0] = "the reading threw, and the trace is above"
        app.quit()
        return
    QtCore.QTimer.singleShot(PAUSE, step)


QtCore.QTimer.singleShot(PAUSE, step)
sys.argv = ["videopodcast_magic.py"]
code = m.gui()
check("the window comes up and stands still to be read",
      read_through[0] and not trouble[0],
      "%s -- %d looks %d ms apart, %d of them without a change, the loop "
      "came back with %r, %.1f s in all"
      % (trouble[0] or "read", watch["looks"], PAUSE, watch["idle"], code,
         time.time() - began))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
