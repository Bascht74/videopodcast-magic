# -*- coding: utf-8 -*-
"""Shot of the language box: the offer to start again, and what it brings.

Started by window_offers_restart_test.py. It runs the program's own
main(), so the loop that answers the code is the one measured; what it
finds goes into the file VPM_REBUILD_REPORT names, because main()
redirects the console into the log.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ["QT_QPA_PLATFORM"] = "offscreen"
import the_program
from PySide6 import QtWidgets, QtCore, QtGui

app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
REPORT = os.environ["VPM_REBUILD_REPORT"]
# German unless the window already speaks it. Picked here rather than
# handed in, so a machine whose system is German still measures a real
# change of language; the test reads back which one it was.
WANTED = "fr" if vpm.LANG == "de" else "de"


def say(line):
    """One line into the report file, which no redirect touches."""
    with open(REPORT, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def windows():
    return [w for w in app.topLevelWidgets()
            if "Video Podcast Magic" in w.windowTitle()]


def win():
    up = [w for w in windows() if w.isVisible()]
    return up[-1] if up else None


def button(text):
    for b in app.allWidgets():
        if isinstance(b, QtWidgets.QPushButton) and b.text().strip() == text:
            return b
    return None


def combo():
    name = vpm.T('Language of the window')
    for c in app.allWidgets():
        if isinstance(c, QtWidgets.QComboBox) and c.accessibleName() == name:
            return c
    return None


def offer():
    """The button that offers a new window, whether shown or not.

    Looked for inside the settings window and not among every widget
    in the process: a button nothing put on a sheet is still alive as
    long as a closure holds it, and would answer here for ever.
    """
    said = vpm.T('Restart the application')
    c = combo()
    if c is None:
        return None
    for b in c.window().findChildren(QtWidgets.QPushButton):
        if b.text().strip() == said:
            return b
    return None


def live_state():
    """The state dictionary of the window that is up just now.

    The window hangs its update sink on the program, and that sink
    closes over exactly that dictionary -- so the flag saying a run is
    going can be read and set from here without a run being started.
    """
    sink = getattr(vpm.PROGRAM, "UPDATE_SINK", None)
    if sink is None or sink.__closure__ is None:
        return {}
    return dict(zip(sink.__code__.co_freevars,
                    [c.cell_contents for c in sink.__closure__])).get(
                        "state") or {}


def question():
    """The box asking what becomes of the work, while one stands."""
    for d in app.topLevelWidgets():
        if isinstance(d, QtWidgets.QMessageBox) and d.isVisible():
            return d
    return None


def note_text():
    """The one wrapped grey line above the language field."""
    c = combo()
    if c is None:
        return ""
    for lab in c.window().findChildren(QtWidgets.QLabel):
        if lab.wordWrap() and lab.text():
            return lab.text()
    return ""


n = [0]
step_no = [0]


def step():
    i = step_no[0]
    step_no[0] += 1
    try:
        if i == 0:
            say("language at rest %s" % vpm.LANG)
            say("aiming at %s" % WANTED)
            b = button(vpm.T('Settings ...'))
            say("settings button %s" % (b is not None))
            if b is None:
                say("done")
                app.quit()
                return
            b.click()
        elif i == 1:
            c = combo()
            say("combo %s" % (c is not None))
            o = offer()
            say("offer built %s" % (o is not None))
            say("offer at rest visible %s" % (o is not None and o.isVisible()))
            say("note at rest %r" % note_text())
        elif i == 2:
            c = combo()
            n[0] = c.currentIndex()
            c.setCurrentIndex(c.findData(WANTED))
            app.processEvents()
            o = offer()
            say("offer after change visible %s"
                % (o is not None and o.isVisible()))
            say("note after change %r" % note_text())
        elif i == 3:
            c = combo()
            c.setCurrentIndex(n[0])
            app.processEvents()
            o = offer()
            say("offer after going back visible %s"
                % (o is not None and o.isVisible()))
        elif i == 4:
            c = combo()
            c.setCurrentIndex(c.findData(WANTED))
            app.processEvents()
            live_state()["running"] = True
            offer().click()
            app.processEvents()
            say("windows while running %d visible %d"
                % (len(windows()), len([w for w in windows()
                                        if w.isVisible()])))
            say("language while running %s" % vpm.LANG)
            say("note while running %r" % note_text())
        elif i == 5:
            live_state()["running"] = False
            say("windows before %d visible %d"
                % (len(windows()), len([w for w in windows()
                                        if w.isVisible()])))
            # Armed before the click: the click ends this event loop,
            # and a timer set afterwards would never be set at all.
            QtCore.QTimer.singleShot(4000, step)
            # Nothing has been added in this window, so nothing may be
            # asked. A box would hold the click here for ever, so it
            # is looked for from outside rather than waited on.
            QtCore.QTimer.singleShot(800, lambda: say(
                "question with nothing added %s" % (question() is not None)))
            offer().click()
            return
        elif i == 6:
            say("language now %s" % vpm.LANG)
            say("windows after %d visible %d"
                % (len(windows()), len([w for w in windows()
                                        if w.isVisible()])))
            w = win()
            say("title after %r" % (w.windowTitle() if w else None))
            say("done")
            app.quit()
            return
    except Exception:
        import traceback
        say("BROKE " + traceback.format_exc().replace("\n", " | "))
        app.quit()
        return
    QtCore.QTimer.singleShot(600, step)


QtCore.QTimer.singleShot(1200, step)
QtCore.QTimer.singleShot(120000, app.quit)
sys.argv = ["videopodcast_magic.py"]
code = vpm.main()
say("main came back with %s" % code)
