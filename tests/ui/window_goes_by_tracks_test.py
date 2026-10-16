# -*- coding: utf-8 -*-
"""The window waits for a file's tracks, then goes by them, not the file.

The mixer fixture's eight channels, its measuring and then its cutting
held by stand-ins until the window has been looked at: both times Start
and Dry run grey and the footer naming the file, and no press handing a
run the file whole. Let go: a press hands the four tracks, and the
preset list, asked before the file came, offers Multitrack alone. Last a
file whose channels a stand-in cannot read holds Start only while it is
measured, as the run takes such a file whole. The run is stood in.
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
from fixture_root import fixture
from let_go import clean_up
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
app.setQuitOnLastWindowClosed(False)
vpm = the_program.load()
vpm.set_language("en")
vpm.load_api_key = lambda: ""
vpm.store_api_key = lambda key: True         # nothing into the keychain
vpm.account_credit = lambda key: None        # nothing to auphonic.com
vpm.update_offer = lambda *a, **k: None
# No dialog waits for anybody, and each says yes but one: once the time
# axis is in, a project file lies with the material, and a file added
# later would open that project in its place.
vpm.say_dialog = lambda *a, **k: a[2:3] != (vpm.T('Project found'),)
vpm.project_type_question = lambda window: "cut"
# A plain list, not the Presets auphonic.com answers with: only that one
# lets the window ask the account next.
vpm.list_presets = lambda key: [("Multitrack preset", "m", True),
                                ("Singletrack preset", "s", False)]

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


folder = tempfile.mkdtemp(prefix="vpm_tracks_")
out_folder = os.path.join(folder, "Result")
os.makedirs(out_folder)
mixer = os.path.join(folder, "Mixer.wav")
shutil.copy(os.path.join(fixture("mixer"), "Mixer.wav"), mixer)
other = tempfile.mkdtemp(prefix="vpm_tracks_other_")
unreadable = os.path.join(other, "Recorder.wav")
shutil.copy(mixer, unreadable)
adding = [mixer]
QtWidgets.QFileDialog.getOpenFileNames = staticmethod(
    lambda *a, **k: (list(adding), ""))
QtWidgets.QFileDialog.getExistingDirectory = staticmethod(
    lambda *a, **k: out_folder)
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok

# What a press hands the run, by file name; the preview's own run is told
# apart by the plan it is given.
handed = []
vpm.run_argv = lambda values, plan="": (
    handed.append([os.path.basename(p) for p, _k in values["files"]])
    if plan != vpm.running.PLAN_PLACE else None, (None, None, []))[1]

# The measuring and the cutting, each held in the prework's thread until
# the window has been looked at: without the hold the tracks can be in
# before the first look on a fast machine. The file whose channels cannot
# be read is held the same way before it is refused.
held = {"measuring": threading.Event(), "cutting": threading.Event(),
        "refusing": threading.Event()}
free = {name: threading.Event() for name in held}


def hold(name):
    """Say that *name* has begun, then wait for the test to let it go."""
    if threading.current_thread() is not threading.main_thread():
        held[name].set()
        free[name].wait(300)


real_split = vpm.split_channels
real_facts = vpm.channel_facts_cached


def split_held(*a, **k):
    hold("cutting")
    return real_split(*a, **k)


def facts_held(path):
    if os.path.basename(path) == os.path.basename(unreadable):
        hold("refusing")
        raise RuntimeError("stand-in: these channels cannot be read")
    if not free["measuring"].is_set():
        hold("measuring")
    return real_facts(path)


vpm.split_channels = split_held
vpm.channel_facts_cached = facts_held
TRACKS = ["Channel1.wav", "Channel2.wav", "Channel3+4.wav", "Channel8.wav"]
WAITING = vpm.T('The channels of %s are not cut into tracks yet.') \
    % os.path.basename(mixer)


def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def button(word):
    """A button by its wording, in the window or the settings."""
    for w in QtWidgets.QApplication.allWidgets():
        if isinstance(w, QtWidgets.QPushButton) and w.text().strip() == word:
            return w


def footer_note():
    for w in win().findChildren(QtWidgets.QLabel):
        if w.objectName() == "start_note":
            return w.text()
    return "(no footer note)"


def preset_values():
    """What the preset list offers, by value: the first is the no-preset."""
    for w in QtWidgets.QApplication.allWidgets():
        if isinstance(w, QtWidgets.QComboBox):
            values = [w.itemData(i) for i in range(w.count())]
            if values[:1] == [vpm.PRESET_NONE]:
                return values
    return []


def ground():
    """Key, name and type set, the key checked: all but the file."""
    win().show()
    for w in QtWidgets.QApplication.allWidgets():
        if isinstance(w, QtWidgets.QLineEdit) \
                and w.echoMode() == QtWidgets.QLineEdit.Password:
            w.setText("stand-in-key-never-sent")
        elif isinstance(w, QtWidgets.QLineEdit) and (
                w.width() == 340 or w.maximumWidth() == 340):
            w.setText("Tracks")
    for box in win().findChildren(QtWidgets.QComboBox):
        values = [box.itemData(i) for i in range(box.count())]
        if "cut" in values and "sync" in values:
            box.setCurrentIndex(values.index("cut"))
    button(vpm.T('Connect')).click()


phase = ["presets"]
waited = [time.time()]
LIMIT = 120.0       # seconds per phase: the builder is nine times slower
SINGLE_ONLY = [vpm.PRESET_NONE, "Singletrack preset"]
MULTI_ONLY = [vpm.PRESET_NONE, "Multitrack preset"]
seen = {}


def looked(start, dry):
    """Start, Dry run and the footer as they stand, a press if it can."""
    live, dry_live, said = start.isEnabled(), dry.isEnabled(), footer_note()
    if live:
        start.click()
    return live, dry_live, said


def step():
    try:
        now = time.time() - waited[0]
        start, dry = button(vpm.T('Start')), button(vpm.T('Dry run'))
        if phase[0] == "presets":
            if preset_values() != SINGLE_ONLY and now < LIMIT:
                return QtCore.QTimer.singleShot(50, step)
            print("\n1. Before the file: the presets, of no track's kind")
            check("the preset list is in before the file is added",
                  preset_values() == SINGLE_ONLY,
                  "offers %r after %.1f s" % (preset_values(), now))
            phase[0], waited[0] = "measuring", time.time()
            button(vpm.T('Add files ...')).click()
        elif phase[0] in ("measuring", "cutting"):
            if not held[phase[0]].is_set() and now < LIMIT:
                return QtCore.QTimer.singleShot(20, step)
            live, dry_live, said = looked(start, dry)
            if phase[0] == "measuring":
                print("\n2. The file's channels being measured, held")
                check("while its channels are measured, Start is grey too",
                      held["measuring"].is_set() and not live
                      and WAITING in said,
                      "measuring begun %r, Start enabled %r, footer %r"
                      % (held["measuring"].is_set(), live, said))
                seen["dry measuring"] = dry_live
                phase[0], waited[0] = "cutting", time.time()
                free["measuring"].set()
            else:
                print("\n3. The file being cut into tracks, held")
                check("while the file is being cut, Start is grey and says "
                      "why",
                      held["cutting"].is_set() and not live
                      and WAITING in said,
                      "cutting begun %r, Start enabled %r, footer %r"
                      % (held["cutting"].is_set(), live, said))
                check("and Dry run waits with it, both times",
                      not seen["dry measuring"] and not dry_live,
                      "Dry run enabled %r while measured, %r while cut"
                      % (seen["dry measuring"], dry_live))
                phase[0], waited[0] = "cut", time.time()
                free["cutting"].set()
        elif phase[0] == "cut":
            if start.isEnabled():
                start.click()
            if (not handed or "Mixer.wav" in handed[-1]) and now < LIMIT:
                return QtCore.QTimer.singleShot(20, step)
            print("\n4. Cut: what a press hands, and what the presets offer")
            print("   handed: %r" % handed)
            check("no press of Start hands the run the file whole",
                  not any("Mixer.wav" in h for h in handed),
                  "%d presses handed it whole, of %d"
                  % (sum("Mixer.wav" in h for h in handed), len(handed)))
            last = handed[-1] if handed else []
            check("once cut, a press of Start hands the run its four tracks",
                  sorted(n.split("_")[-1] for n in last) == TRACKS,
                  "handed %r after %.1f s, Start enabled %r, footer %r"
                  % (last, now, start.isEnabled(), footer_note()))
            phase[0], waited[0] = "kind", time.time()
        elif phase[0] == "kind":
            # The tracks are written before the window hears they are in,
            # so a press can hand them a moment before the list follows.
            if preset_values() != MULTI_ONLY and now < LIMIT:
                return QtCore.QTimer.singleShot(20, step)
            check("and the preset list then offers the Multitrack one alone",
                  preset_values() == MULTI_ONLY,
                  "offers %r %.1f s after the tracks were handed"
                  % (preset_values(), now))
            phase[0], waited[0] = "refusing", time.time()
            adding[:] = [unreadable]
            button(vpm.T('Add files ...')).click()
        elif phase[0] == "refusing":
            if not held["refusing"].is_set() and now < LIMIT:
                return QtCore.QTimer.singleShot(20, step)
            seen["grey while measured"] = not start.isEnabled()
            phase[0], waited[0] = "refused", time.time()
            free["refusing"].set()
        elif phase[0] == "refused":
            if not start.isEnabled() and now < LIMIT:
                return QtCore.QTimer.singleShot(50, step)
            print("\n5. A file whose channels cannot be read")
            check("a file whose channels cannot be read holds Start no "
                  "longer",
                  seen["grey while measured"] and start.isEnabled(),
                  "Start grey while measured %r, enabled %r %.1f s after "
                  "the refusal, footer %r"
                  % (seen["grey while measured"], start.isEnabled(), now,
                     footer_note()))
            app.quit()
            return
        QtCore.QTimer.singleShot(20, step)
    except Exception:
        import traceback
        traceback.print_exc()
        bad.append("crash")
        app.quit()


def begin():
    try:
        ground()
    except Exception:
        import traceback
        traceback.print_exc()
        bad.append("crash")
        app.quit()
        return
    QtCore.QTimer.singleShot(50, step)


QtCore.QTimer.singleShot(700, begin)
QtCore.QTimer.singleShot(600000, app.quit)
sys.argv = ["videopodcast_magic.py"]
vpm.gui()
for event in free.values():
    event.set()
clean_up(folder)
clean_up(other)
# Here and nowhere else: a window that never got as far as the checks
# quits on the timer above, and this line is what says how few it made.
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
