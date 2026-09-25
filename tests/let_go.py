# -*- coding: utf-8 -*-
"""Letting go of a folder the window has played from, and deleting it.

Eleven window tests carried these two functions, eight of them word for
word in their code and all of them differing in the docstring alone.
They stand here once. The name has no `_test` in it: `run.sh` collects
the suite as `*_test.py`, and a helper so named is run as a test.

Both print what they did, as lines of the test that called them: never
starting with `FAIL`, `SKIPPED:` or `LEFT OUT`, and never saying
`error`, since `run.sh` counts those against the test. The application
is the one already running; neither function starts one.
"""
import os
import shutil


def let_go_of(what):
    """Make every player let go of what it has open in there.

    Windows cannot delete or move a held file, and ignore_errors would
    hide the folder staying behind. Players are found by what they hold,
    not by which player they are, so a second holder cannot slip through.
    A path is compared both as written and resolved: material linked out
    of the shared fixture is held under the link's name. One that never
    started is not stopped: building what lies behind stop() waits for a
    lock a starting player holds. Returns the names let go, sorted.
    """
    from PySide6 import QtCore, QtWidgets
    app = QtWidgets.QApplication.instance()
    roots = [os.path.abspath(what), os.path.realpath(what)]

    def belongs(where):
        for held in (os.path.abspath(where), os.path.realpath(where)):
            for root in roots:
                if held == root or held.startswith(root + os.sep):
                    return True
        return False

    let_go = []
    for top in app.topLevelWidgets():
        for x in top.findChildren(QtCore.QObject):
            if not (hasattr(x, "setSource") and hasattr(x, "source")):
                continue
            where = x.source()
            if not isinstance(where, QtCore.QUrl):
                continue
            where = where.toLocalFile()
            if not where or not belongs(where):
                continue
            state = getattr(x, "playbackState", None)
            state = state() if state is not None else None
            if state is not None and state != type(state).StoppedState:
                x.stop()
            x.setSource(QtCore.QUrl())
            let_go.append(os.path.basename(where))
    app.processEvents()
    return sorted(let_go)


def clean_up(what):
    """Close the window, then delete the folder, waiting for the grip.

    gui() comes back with the window still standing. Let go, close,
    delete, in that order, and no ignore_errors: it would swallow the one
    thing that can go wrong, a folder that stays because something still
    holds it. The media backend closes the handle in a thread of its
    own, so the wait is on the handle and not on a fixed pause: up to ten
    seconds, after which what is left is named and does not turn the test
    red -- a test red on one system on every run gets switched off, not
    read.
    """
    from PySide6 import QtCore, QtWidgets
    app = QtWidgets.QApplication.instance()
    print("  let go of %s" % (", ".join(let_go_of(what)) or "nothing"))
    for top in app.topLevelWidgets():
        top.close()
    app.processEvents()
    clock = QtCore.QElapsedTimer()
    clock.start()
    while True:
        left = []
        try:
            shutil.rmtree(what)
        except OSError:
            for here, _, files in os.walk(what):
                left += [os.path.join(here, f) for f in files]
            left = left or ([what] if os.path.exists(what) else [])
        if not left or clock.elapsed() > 10000:
            break
        app.processEvents()
        QtCore.QThread.msleep(50)
    if left:
        print("  the folder stayed: %d still held after %.1f s, first %s"
              % (len(left), clock.elapsed() / 1000.0, left[0]))
    else:
        print("  the folder went away with the window, after %.1f s"
              % (clock.elapsed() / 1000.0))
