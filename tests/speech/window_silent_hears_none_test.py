# -*- coding: utf-8 -*-
"""Silent mode opens a project and sets no recogniser going by itself.

On way_ground's production -- three recordings, three cameras, a stored
separation -- opened offscreen: first silent, as the suite runs, and
nothing is heard, neither the separated recording nor the window's own
transcript, while the time axis stands; then closed, silent mode taken
off, opened again, and both are heard. The limit: silent mode is taken
off by bending the one question the window asks, not VPM_SILENT.
"""
PLATFORM_BOUND = True
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import shutil
import tempfile
import time
import the_program
import way_ground as ground

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stop():
    """Nothing further can be asked, so count what there is and go."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


if ground.missing():
    print("SKIPPED: " + ground.missing())
    stop()

# Silent, as the suite runs, whoever starts this. A store of its own, so
# no words another test left behind answer in place of the recogniser.
os.environ["VPM_SILENT"] = "1"
STORE = tempfile.mkdtemp(prefix="vpm_silent_store_")
os.environ["VPM_CACHE"] = STORE
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtGui, QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
app.setQuitOnLastWindowClosed(False)
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
# The window's transcript waits on this switch as well; the model is
# stood in, and the stored separation means it is never asked anyway.
vpm.SPEAKER_SPLIT_OFF = False
vpm.speaker_split_run = lambda path, count=0, **kw: ([], "")
vpm.speaker_split_available = lambda deep=False: True

heard = []     # the file name each call of the recogniser was handed


def recogniser(path, language="", install=True):
    """Stand in for both recognisers, and note what was handed over."""
    heard.append(os.path.basename(path))
    return []


vpm.macos_words = recogniser
vpm.whisper_words = recogniser

# Every round of the window's transcript, as (the axis stood, it said
# news). The rounds come every three seconds, so they are the sign of
# life the waiting below counts.
rounds = []
real_round = vpm.window_words_round


def counted_round(state, assign_lines, report=None):
    """The real round, with what it saw and answered kept."""
    answer = real_round(state, assign_lines, report)
    rounds.append((bool(state.get("axis"))
                   and not state.get("axis_running"), bool(answer)))
    return answer


vpm.window_words_round = counted_round

PATIENCE = 150.0       # the builder is nine times slower than this machine
WORK = ground.own_folder("silent")
os.makedirs(os.path.join(WORK, "project"))
os.makedirs(os.path.join(WORK, "out"))
SOURCE = ground.media(ground.HEARD_IN)
PROJECT = ground.project_plain(
    vpm, os.path.join(WORK, "project"), os.path.join(WORK, "out"),
    multitrack=False,
    extra={"assignment": {"several:" + SOURCE: True},
           "speakers": ground.separation(vpm), "speakers_source": SOURCE,
           "speakers_local": True})
SEPARATED = os.path.basename(SOURCE)


def win():
    """The program's window, once it stands."""
    for x in app.topLevelWidgets():
        if vpm.DISPLAY_NAME in x.windowTitle():
            return x


def button(text):
    """The window's button whose text begins with *text*."""
    for w in win().findChildren(QtWidgets.QPushButton) if win() else ():
        if w.text().replace("&", "").strip().startswith(text):
            return w


def menu_action(text):
    """The window's menu entry whose text begins with *text*."""
    for a in win().findChildren(QtGui.QAction) if win() else ():
        if a.text().replace("&", "").strip().startswith(text):
            return a


def standing():
    """How many rounds so far saw the time axis standing."""
    return len([1 for stood, _news in rounds if stood])


def waited_for(condition):
    """Let the window work until *condition* holds; the seconds, or None."""
    here = time.time()
    while time.time() - here < PATIENCE:
        app.processEvents()
        if condition():
            return round(time.time() - here, 1)
        time.sleep(0.02)
    return None


def drive():
    """Open silently, judge; close, take silent mode off, open, judge."""
    try:
        win().show()
        QtWidgets.QFileDialog.getOpenFileName = staticmethod(
            lambda *a, **k: (PROJECT, ""))
        print("1. Opened in silent mode")
        button(vpm.T("Open project")).click()
        # Two rounds on a standing axis: by then the preview has asked
        # for the separated recording's words, and the round has had its
        # chance to begin the window's transcript.
        took = waited_for(lambda: standing() >= 2)
        check("silent: the time axis stood while the project lay open",
              took is not None,
              "%d of %d rounds saw a standing axis, waited up to %.0f s"
              % (standing(), len(rounds), PATIENCE))
        check("silent: opening a stored separation sets no recogniser going",
              heard == [],
              "the recogniser was handed %s, wanted nothing" % heard)
        check("silent: the window's transcript round begins nothing",
              not [1 for _stood, news in rounds if news],
              "%d of %d rounds said a transcript was begun, wanted none"
              % (len([1 for _s, news in rounds if news]), len(rounds)))

        print("\n2. Closed, silent mode taken off, opened again")
        menu_action(vpm.T("Close project")).trigger()
        del rounds[:]
        took = waited_for(lambda: rounds and not rounds[-1][0])
        if took is None:
            check("unsilenced: the separated recording is written down",
                  False, "the project never closed: the axis still stood "
                  "after %.0f s" % PATIENCE)
            return
        # A store of its own again: whatever the first half left in its
        # store must not answer for the recogniser in the second.
        vpm.listening_unasked = lambda: True
        os.environ["VPM_CACHE"] = tempfile.mkdtemp(dir=STORE)
        del rounds[:], heard[:]
        button(vpm.T("Open project")).click()
        # Ten rounds on a standing axis is half a minute of a window
        # that could have listened; both arrive long before.
        waited_for(lambda: (SEPARATED in heard and "mix.wav" in heard)
                   or standing() >= 10)
        check("unsilenced: the separated recording is written down",
              SEPARATED in heard,
              "the recogniser was handed %s after %d rounds on a standing "
              "axis, wanted %s among them" % (heard, standing(), SEPARATED))
        check("unsilenced: the window hears its transcript from a mix",
              "mix.wav" in heard,
              "the recogniser was handed %s after %d rounds on a standing "
              "axis, wanted mix.wav among them" % (heard, standing()))
    except Exception:
        import traceback
        traceback.print_exc()
        bad.append("crash")
    finally:
        app.quit()


QtCore.QTimer.singleShot(700, drive)
sys.argv = ["videopodcast_magic.py"]
vpm.gui()
shutil.rmtree(WORK, ignore_errors=True)
shutil.rmtree(STORE, ignore_errors=True)
stop()
