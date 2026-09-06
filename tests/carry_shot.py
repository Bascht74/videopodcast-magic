# -*- coding: utf-8 -*-
"""Shot of a restart with work in the window, answered all three ways.

Started by window_restart_carries_test.py. It runs the program's own
main(), opens the fixture project, marks In and Out, and then presses
Restart the application three times -- cancelling, saving, and not
saving -- reading the window and the project file after each. What it
finds goes into the file VPM_REBUILD_REPORT names, because main()
redirects the console into the log.
"""
import hashlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ["QT_QPA_PLATFORM"] = "offscreen"
import the_program
from PySide6 import QtWidgets, QtCore, QtGui

app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
from fixture_project import fixture_project

REPORT = os.environ["VPM_REBUILD_REPORT"]
PROJECT, SRC = fixture_project("carry")
if PROJECT is None:
    raise SystemExit("no material under %s" % SRC)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (PROJECT, ""))
# Three languages, so no two readings can be mistaken for each other.
LADDER = ["de", "fr", "it"]

LOOK = 60           # milliseconds between two looks
STILL = 400         # looks in a row without the window moving


def say(line):
    with open(REPORT, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def windows():
    return [w for w in app.topLevelWidgets()
            if "Video Podcast Magic" in w.windowTitle()]


def win():
    up = [w for w in windows() if w.isVisible()]
    return up[-1] if up else None


def live_state():
    sink = getattr(vpm.PROGRAM, "UPDATE_SINK", None)
    if sink is None or sink.__closure__ is None:
        return {}
    return dict(zip(sink.__code__.co_freevars,
                    [c.cell_contents for c in sink.__closure__])).get(
                        "state") or {}


def button(text, where=None):
    for b in (where or win() or app).findChildren(QtWidgets.QPushButton):
        if b.text().strip() == text:
            return b
    return None


def question():
    """The box asking what becomes of the work, while it stands."""
    for d in app.topLevelWidgets():
        if isinstance(d, QtWidgets.QMessageBox) and d.isVisible():
            return d
    return None


def combo():
    """The language field of the settings sheet that is up.

    The sheet of a window that has been restarted is closed but still
    alive, and its field answers just as well -- so only a field on a
    sheet somebody can see counts.
    """
    name = vpm.T('Language of the window')
    for c in app.allWidgets():
        if (isinstance(c, QtWidgets.QComboBox)
                and c.accessibleName() == name and c.window().isVisible()):
            return c
    return None


def offer():
    c = combo()
    return button(vpm.T('Restart the application'), c.window()) if c else None


def rows():
    w = win()
    if w is None:
        return -1
    for t in w.findChildren(QtWidgets.QTreeWidget):
        def under(node):
            return 1 + sum(under(node.child(i))
                           for i in range(node.childCount()))
        return sum(under(t.topLevelItem(i))
                   for i in range(t.topLevelItemCount()))
    return -1


def tabs():
    w = win()
    for tw in (w.findChildren(QtWidgets.QTabWidget) if w else []):
        return [tw.tabText(k) for k in range(tw.count())]
    return []


watched = [""]


def project_on_disc():
    """Name, size and a mark of the contents of the project file.

    The contents and not the clock: the file is moved along when the
    output folder changes, and a move alone shifts the time without a
    word of it being rewritten. The path is held from the first
    reading on, because a restart told not to save leaves no project
    in the window and the file still has to be looked at.
    """
    s = live_state()
    watched[0] = s.get("project_from") or s.get("project_last") or watched[0]
    p = watched[0]
    if not p or not os.path.isfile(p):
        return [os.path.basename(p), None, None, None]
    with open(p, "rb") as f:
        raw = f.read()
    try:
        named = json.loads(raw.decode("utf-8")).get("production")
    except (ValueError, UnicodeDecodeError):
        named = None
    return [os.path.basename(p), len(raw),
            hashlib.sha1(raw).hexdigest()[:12], named]


def reading(tag):
    s = live_state()
    w = win()
    c = combo()
    go = offer()
    say("%s %s" % (tag, json.dumps(
        {"rows": rows(), "tabs": tabs(), "file": project_on_disc(),
         "project": os.path.basename(s.get("project_from") or ""),
         "in": s.get("in_point"), "out": s.get("out_point"),
         "language": vpm.LANG, "windows": len(windows()),
         "visible": len([x for x in windows() if x.isVisible()]),
         "box": [c.currentData() if c else None,
                 go is not None and go.isVisible()],
         "title": w.windowTitle() if w else None},
        ensure_ascii=False, sort_keys=True)))


def menu_open_project():
    w = win()
    for a in (w.findChildren(QtGui.QAction) if w else []):
        if "open project" in a.text().lower().replace("&", ""):
            a.trigger()
            return True
    return False


def settings_open():
    button(vpm.T('Settings ...')).click()
    return True


def language_pick(code):
    combo().setCurrentIndex(combo().findData(code))
    return True


def marks_set():
    for word in (vpm.T('Mark In'), vpm.T('Mark Out')):
        b = button(word)
        if b is not None:
            b.click()
    return True


def offer_press():
    offer().click()
    return True


PROBE = "not saved probe"


def probe_lay():
    """Put a mark in the project file that any write would rub out.

    Without one a restart told not to save could write the file again
    with the very same bytes, and nothing would show it. The mark goes
    in the production name, because that is a field the program sets
    on every write; it is laid in the file from outside, so the window
    itself is left exactly as it stands.
    """
    p = watched[0]
    if not p or not os.path.isfile(p):
        say("NO PROJECT FILE TO MARK")
        return True
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    d["production"] = PROBE
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    return True


# Each step: what it is waiting for, the wait itself, and what it does
# once that is true. The waits are conditions, never a length of time.
def steps():
    yield ("the window", lambda: win() is not None, menu_open_project)
    yield ("the files", lambda: rows() > 0, marks_set)
    # Read after the marks and not before them, so that what the
    # restart has to bring back is one settled state and not one the
    # window was still filling in.
    yield ("the marks", lambda: live_state().get("in_point"),
           lambda: reading("BEFORE") or True)
    yield ("nothing", lambda: True, settings_open)
    yield ("the language field", lambda: combo() is not None,
           lambda: language_pick(LADDER[0]))
    yield ("the offer", lambda: offer() is not None and offer().isVisible(),
           offer_press)
    yield ("the question", lambda: question() is not None,
           lambda: press(vpm.T('Cancel')))
    yield ("the question gone", lambda: question() is None,
           lambda: reading("CANCELLED") or True)
    yield ("nothing", lambda: True, offer_press)
    yield ("the question again", lambda: question() is not None,
           lambda: press(vpm.T('Save and restart')))
    yield ("the window in %s" % LADDER[0],
           lambda: vpm.LANG == LADDER[0] and rows() > 0,
           lambda: reading("SAVED") or True)
    yield ("nothing", lambda: True, settings_open)
    yield ("the field of the new sheet", lambda: combo() is not None,
           lambda: language_pick(LADDER[1]))
    yield ("nothing", lambda: True, probe_lay)
    # Read again right before the press: between the two restarts the
    # new window opened the project and wrote it, so a file compared
    # against the reading before that would look written by the drop.
    yield ("the offer again",
           lambda: offer() is not None and offer().isVisible(),
           lambda: (reading("READY"), offer_press())[1])
    yield ("the third question", lambda: question() is not None,
           lambda: press(vpm.T('Restart without saving')))
    yield ("the window in %s" % LADDER[1], lambda: vpm.LANG == LADDER[1],
           lambda: reading("DROPPED") or True)


def press(word):
    d = question()
    b = button(word, d)
    say("question up with %s"
        % [x.text() for x in d.findChildren(QtWidgets.QPushButton)])
    if b is None:
        say("NO BUTTON %r IN THE QUESTION" % word)
        d.reject()
        return True
    b.click()
    return True


LEFT = list(steps())
idle = [0]
sign = [None]


def tick():
    if not LEFT:
        say("done")
        app.quit()
        return
    name, ready, do = LEFT[0]
    now = (rows(), vpm.LANG, len(windows()), question() is not None,
           bool(combo()), len(LEFT))
    idle[0] = idle[0] + 1 if now == sign[0] else 0
    sign[0] = now
    if idle[0] > STILL:
        say("STOOD STILL waiting for %s -- %s" % (name, now))
        app.quit()
        return
    # The next look is arranged before the step runs, not after it: a
    # step that presses the restart ends up inside the question's own
    # event loop and never comes back here, and the chain would die
    # exactly where the question waits to be answered.
    QtCore.QTimer.singleShot(LOOK, tick)
    try:
        if ready():
            LEFT.pop(0)
            do()
    except Exception:
        import traceback
        say("BROKE " + traceback.format_exc().replace("\n", " | "))
        app.quit()


QtCore.QTimer.singleShot(LOOK, tick)
sys.argv = ["videopodcast_magic.py"]
say("main came back with %s" % vpm.main())
