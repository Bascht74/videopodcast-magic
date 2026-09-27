# -*- coding: utf-8 -*-
"""While the window writes its transcript, the four grey ones say so.

way_ground's production, Multitrack, opened offscreen and its Resolve
cut tab looked at, with a stand-in recogniser that holds the mix until
released. In order: the window sets its own transcript going; while it
is held, the four settings that need words are grey and the note under
them says it is being written; released, the four open and the note
goes. The limit: the recogniser is stood in, and silent mode is taken
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
import threading
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

# A store of its own, so no words another test left behind answer in
# place of the recogniser; and a Resolve that is not there to answer.
STORE = tempfile.mkdtemp(prefix="vpm_writing_store_")
NOWHERE = os.path.join(STORE, "no-resolve-here")
os.environ.pop("VPM_NO_SPEAKER_SPLIT", None)
os.environ.update(VPM_CACHE=STORE, QT_QPA_PLATFORM="offscreen",
                  RESOLVE_SCRIPT_API=NOWHERE,
                  RESOLVE_SCRIPT_LIB=os.path.join(NOWHERE, "fusionscript.so"))
from PySide6 import QtCore, QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
app.setQuitOnLastWindowClosed(False)
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
vpm.SPEAKER_SPLIT_OFF = False
vpm.speaker_split_run = lambda path, count=0, **kw: ([], "")
vpm.speaker_split_available = lambda deep=False: True
# The suite runs silent, and silent mode lets the window start no
# recogniser by itself; here the recogniser is stood in and asked.
vpm.listening_unasked = lambda: True

PATIENCE = 150.0       # the builder is nine times slower than this machine
FOUR = ["on-question", "reaction-lead", "wide-after", "wide-most"]
LISTENING = vpm.T('It is being written down in the background; '
                  'they open by themselves when it is done.')
gate = threading.Event()   # set: the recogniser hands its words back
heard = []                 # the file name each call was handed


def recogniser(path, language="", install=True):
    """Stand in for both; the window's mix is held until the gate opens."""
    heard.append(os.path.basename(path))
    if os.path.basename(path) != "mix.wav":
        return []
    gate.wait(PATIENCE)
    return [{"start": 2.0, "end": 2.4, "word": "Why?"},
            {"start": 8.0, "end": 8.4, "word": "Because."}]


vpm.macos_words = recogniser
vpm.whisper_words = recogniser

WORK = ground.own_folder("writing")
os.makedirs(os.path.join(WORK, "project"))
os.makedirs(os.path.join(WORK, "out"))
PROJECT = ground.project_plain(
    vpm, os.path.join(WORK, "project"), os.path.join(WORK, "out"),
    multitrack=True)


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


def sheet():
    """The Resolve cut tab, once the project has brought it."""
    return getattr(win(), "resolve_sheet", None) if win() else None


def seen():
    """(the note's text where shown, the four that are grey)."""
    note = win().findChild(QtWidgets.QLabel, "question_note")
    parts = sheet().cut_parts
    return ("" if note is None or note.isHidden() else note.text(),
            [k for k in FOUR if not parts[k][1].isEnabled()])


def waited_for(condition):
    """Let the window work until *condition* holds; the seconds, or None."""
    here = time.time()
    while time.time() - here < PATIENCE:
        app.processEvents()
        if condition():
            return round(time.time() - here, 1)
        time.sleep(0.02)
    return None


def tail(text):
    """The end of a note, where its reason stands, for a failure line."""
    return repr(text[-60:]) if text else "no note shown"


def drive():
    """Open, look at the cut tab, hold the transcript, then let it come."""
    try:
        win().show()
        QtWidgets.QFileDialog.getOpenFileName = staticmethod(
            lambda *a, **k: (PROJECT, ""))
        button(vpm.T("Open project")).click()
        if waited_for(lambda: sheet() is not None) is None:
            check("the window sets its transcript going in the background",
                  False, "no Resolve cut tab after %.0f s" % PATIENCE)
            return
        win().tabs.setCurrentWidget(sheet())
        took = waited_for(lambda: "mix.wav" in heard)
        check("the window sets its transcript going in the background",
              took is not None, "the recogniser was handed %s within "
              "%.0f s, wanted mix.wav among them" % (heard, PATIENCE))
        # Given up into the judgement: whatever the note says by then.
        waited_for(lambda: seen()[0].endswith(LISTENING))
        said, grey = seen()
        check("while it is written the four are grey and the note says so",
              said.endswith(LISTENING) and grey == FOUR,
              "note %s, grey %s" % (tail(said), grey))
        gate.set()
        took = waited_for(lambda: seen() == ("", []))
        said, grey = seen()
        check("once the words are there the four open and the note goes",
              took is not None, "after %.0f s note %s, grey %s"
              % (PATIENCE, tail(said), grey))
    except Exception:
        import traceback
        traceback.print_exc()
        bad.append("crash")
    finally:
        gate.set()
        app.quit()


QtCore.QTimer.singleShot(700, drive)
sys.argv = ["videopodcast_magic.py"]
vpm.gui()
shutil.rmtree(WORK, ignore_errors=True)
shutil.rmtree(STORE, ignore_errors=True)
stop()
