# -*- coding: utf-8 -*-
"""What Mark In and Mark Out set is where the player stands.

An In point taken as given says nothing about the buttons that make
one. So the player is dragged to a spot, the mark is made, and what
came of it is read off the screen and off what reached the trimming.
In order: no material and no mark at either door; the ground, a file
with a timecode in the player; the button; the menu entry, with its key;
the project file; an Out point in front of the In point; and a step
whose answer never comes, red where it stands. From the project file on,
run_three_ways_agree has it, and this one stops there.
"""
import os
import sys
import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
sys.path.insert(0, HERE)

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["VPM_SILENT"] = "1"
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
# The separation never runs here: what it would have found is in the
# project file, and a run would fetch a model.
os.environ["VPM_NO_SPEAKER_SPLIT"] = "1"

import glob
import json
import shutil
import tempfile
import time

from PySide6 import QtCore, QtGui, QtWidgets

from fixture_root import fixture

app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.update_offer = lambda *a, **k: None
vpm.set_language("en")

# How long one step may stand completely still before it is given up on.
# Not a deadline: what is measured is how long nothing moved at all, so
# a slow machine is not punished and a step that hangs while there is
# time left is still caught.
POLL = 200
STILL = 100
WINDOW = (1400, 950)

SPLIT = "Presenter_REC00021.wav"          # the recording with the voices
PLAIN = "CoPresenter_REC00018.wav"        # the recording with a name field
WIDE = "WideCam_01011855_C001.mov"
HOSTS = "PresentersCam_01011855_C002.mov"
GUESTS = "GuestCam_01011858_C003.mov"
CAMERAS = (WIDE, HOSTS, GUESTS)
VOICES = (("V0", "Host"), ("V1", "Guest"))
SEGMENTS = [["V0", 0.5, 12.0], ["V1", 13.0, 24.0],
            ["V0", 25.0, 33.0], ["V1", 34.0, 39.0]]

# The spots the player is dragged to, in the order they are used. Far
# enough apart that two marks can never be read as one, and every pair
# leaves more than the five seconds the trimming asks for -- except the
# last, which is meant to fall short.
IN_AT = 6.0
OUT_AT = 20.0
MENU_OUT_AT = 30.0
MENU_IN_AT = 10.0
BACK_AT = 2.0
# How near the player has to land for the spot to count as reached. A
# mark is written to the frame, so half a frame at 25 pictures a second
# is the width in which the answer is still the same string.
NEAR = 0.02

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def drawn(text):
    """What ends up on the screen: & marks a key, && draws one &."""
    return str(text).replace("&&", "\x00").replace("&", "") \
                    .replace("\x00", "&")


def clock_seconds(mark, fps):
    """Read a clock time back as seconds -- by hand, not by the program.

    The program writes seconds as HH:MM:SS:FF; this goes the other way,
    so the reading and the writing cannot agree by sharing a fault.
    """
    try:
        h, m, s, f = (int(x) for x in str(mark).split(":"))
    except ValueError:
        return None
    return h * 3600 + m * 60 + s + f / max(1.0, float(fps))


# ------------------------------------------------------------ the project
def own_project():
    """A project of its own, built out of the shared fixture.

    Opening a project moves the project file away and deletes copies
    lying elsewhere, so the fixture is only linked to.
    """
    source = fixture("interview")
    own = tempfile.mkdtemp(prefix="vpm_marks_")
    here = {}
    for name in (SPLIT, PLAIN) + CAMERAS:
        link = os.path.join(own, name)
        if not os.path.exists(link):
            os.symlink(os.path.join(source, name), link)
        here[name] = link
    assignment = {"voice:V0": HOSTS, "voice:V1": GUESTS}
    one = here[SPLIT]
    st = os.stat(one)
    d = {"format": vpm.FILE_FORMAT, "version": "test", "timeline": [],
         "call": [],
         "files": [{"path": here[n],
                    "kind": "video" if n.endswith(".mov") else "audio"}
                   for n in (SPLIT, PLAIN) + CAMERAS],
         "out_folder": os.path.join(own, "Result"),
         "production": "Marks", "multitrack": True,
         "assignment": assignment, "preset": "",
         # Stored the way the program stores it, with the fingerprint of
         # the file: a stored result whose source has changed is thrown
         # away, and this one has to survive that test.
         "speakers": {"source": os.path.abspath(one),
                      "mtime": int(st.st_mtime), "size": st.st_size,
                      "model": vpm.SPEAKER_MODEL_NAME, "model_mark": "",
                      "num_speakers": len(VOICES),
                      "names": dict(VOICES), "segments": SEGMENTS}}
    assignment["several:" + one] = True
    os.makedirs(d["out_folder"], exist_ok=True)
    path = os.path.join(own, "videopodcast-magic_Marks.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1)
    return own, path


FOLDER, PROJECT = own_project()
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (PROJECT, ""))
# Nothing may sit and wait for a click: a modal window would hold the
# test until the suite kills it.
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok

# Off the desktop on the way in: somebody may be sitting at this
# machine. The window still goes through the whole layout machinery.
_show = QtWidgets.QWidget.show


def offstage(self):
    self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
    _show(self)


QtWidgets.QWidget.show = offstage
QtWidgets.QDialog.show = offstage


# --------------------------------------------------------------- the spy
# The window looks the trimming up in the module when it calls it, so
# replacing it here reads what passes -- unchanged -- on the way.
seen = []
_real_window = vpm.apply_time_window


def window_spy(d, in_point, out_point):
    out = _real_window(d, in_point, out_point)
    seen.append({"in": in_point, "out": out_point, "complaint": out[1]})
    return out


vpm.apply_time_window = window_spy


# ------------------------------------------------------- reading the window
def window_of():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x
    return None


def anywhere_named(text):
    """The button with this caption, wherever it hangs.

    Before any material arrives the preview player is built but not yet
    put into the window, so looking only under the window would find
    nothing and a greyed button would be indistinguishable from none.
    """
    for b in app.allWidgets():
        if isinstance(b, QtWidgets.QPushButton) \
                and drawn(b.text()).strip() == text:
            return b
    return None


def button_named(text):
    top = window_of()
    if top is None:
        return None
    for b in top.findChildren(QtWidgets.QPushButton):
        if drawn(b.text()).strip() == text:
            return b
    return None


def action_named(text):
    top = window_of()
    if top is None:
        return None
    for a in top.findChildren(QtGui.QAction):
        if drawn(a.text()).strip() == text:
            return a
    return None


def label_saying(text):
    """Is that sentence standing anywhere in the program's widgets?"""
    for x in app.allWidgets():
        if isinstance(x, QtWidgets.QLabel) and text in drawn(x.text()):
            return x
    return None


def preview_player():
    """The player the mark buttons sit in, found from the button.

    Not by class and not by name: owning the "Mark In" button is the
    only thing that tells it from the other player in this window.
    Looked for among all the widgets and not only under the window,
    because before any material arrives the player is built but not yet
    put in, and the first step has to reach it there.
    """
    b = anywhere_named(drawn(vpm.T('Mark In')))
    up = None if b is None else b.parentWidget()
    while up is not None and not hasattr(up, "spot_s"):
        up = up.parentWidget()
    return up


def point_shown(caption):
    """What the player writes as In point or Out point.

    Three places in this window say "In point", and the cut player on
    the Resolve tab converts the position into the timecode of its own
    clip. Only the preview player's own line shows the answer itself,
    and the answer is what travels on.
    """
    p = preview_player()
    head = drawn(vpm.T(caption)).replace("%s", "").strip()
    if p is None:
        return ""
    for x in p.findChildren(QtWidgets.QLabel):
        said = drawn(x.text()).strip()
        if said.startswith(head):
            return said[len(head):].strip()
    return ""


def in_shown():
    return point_shown('In point %s')


def out_shown():
    return point_shown('Out point %s')


def player_clock():
    """The time the player says it stands at, read off its own line.

    That line and the mark are two readings of one position, taken by
    two different pieces of the program -- which is what makes them
    worth holding against each other.
    """
    p = preview_player()
    said = "" if p is None else drawn(p.middle.text())
    return said.split()[0] if said.split() else ""


def player_fps():
    p = preview_player()
    return getattr(p, "fps", 30.0) or 30.0


def player_ready():
    """Has the player a file with a length, so a spot can be marked?

    On a Qt without multimedia the player is a stand-in with no length,
    so this stays False and the step says what it saw instead.
    """
    p = preview_player()
    try:
        return bool(p is not None and p.player.duration() > 0)
    except AttributeError:
        return False


def tab_to(word):
    top = window_of()
    if top is None:
        return False
    for bar in top.findChildren(QtWidgets.QTabWidget):
        for k in range(bar.count()):
            if word.lower() in drawn(bar.tabText(k)).lower():
                bar.setCurrentIndex(k)
                app.processEvents()
                return True
    return False


def project_files():
    """Every project file lying in the production folder, with its age."""
    out = {}
    for p in glob.glob(os.path.join(FOLDER, "**", "*.json"), recursive=True):
        try:
            out[p] = os.stat(p).st_mtime_ns
        except OSError:
            pass
    return out


def newest_project():
    """The project file last written, read back."""
    known = project_files()
    if not known:
        return None, ""
    path = max(known, key=lambda p: known[p])
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f), path
    except (OSError, ValueError):
        return None, path


# ------------------------------------------------------------- the driver
plan = []
at = [0]
mark = [0]
polls = [0]
still = [0]
sign = [None]
kept = {}


def alive():
    """A sign of life that only moves because the program is working."""
    p = preview_player()
    try:
        where = round(p.spot_s(), 3)
    except AttributeError:
        where = None
    return (len(seen), where, in_shown(), out_shown(),
            "" if p is None else drawn(p.middle.text()))


def step(say, do, then, watch=False, until=None):
    """One answer given, and what must have arrived because of it.

    *watch* waits for a fresh call of the trimming; *until* for a state
    the step itself brings about.
    """
    plan.append({"say": say, "do": do, "then": then, "watch": watch,
                 "until": until or (lambda: True), "begun": False})


def drive():
    if at[0] >= len(plan):
        app.quit()
        return
    job = plan[at[0]]
    if not job["begun"]:
        job["begun"] = True
        polls[0] = still[0] = 0
        sign[0] = alive()
        mark[0] = len(seen)
        try:
            job["do"]()
        except Exception:
            import traceback
            traceback.print_exc()
            check("every step was answered", False,
                  "%s -- the answer could not be given" % job["say"])
            at[0] += 1
        QtCore.QTimer.singleShot(150, drive)
        return
    fresh = seen[mark[0]:]
    settled = (not job["watch"]) or bool(fresh)
    try:
        settled = settled and job["until"]()
    except Exception:
        settled = False
    if not settled:
        now = alive()
        still[0] = 0 if now != sign[0] else still[0] + 1
        sign[0] = now
        polls[0] += 1
        if still[0] < STILL:
            QtCore.QTimer.singleShot(POLL, drive)
            return
        print("\n%s" % job["say"])
        # The standstill first, because it is the first thing that was
        # wrong -- and the reading after it all the same, so that what
        # never arrived is named by the check it belonged to and not
        # only by the waiting.
        check("every step was answered", False,
              "%s -- nothing moved for %.1f s of %.1f s waited, "
              "%d trimmings since"
              % (job["say"], still[0] * POLL / 1000.0,
                 polls[0] * POLL / 1000.0, len(fresh)))
        read_off(job, fresh)
        at[0] += 1
        QtCore.QTimer.singleShot(50, drive)
        return
    print("\n%s" % job["say"])
    read_off(job, fresh)
    at[0] += 1
    QtCore.QTimer.singleShot(50, drive)


def read_off(job, fresh):
    try:
        job["then"](fresh[-1] if fresh else None)
    except Exception:
        import traceback
        traceback.print_exc()
        check("every step was answered", False,
              "%s -- the reading could not be taken" % job["say"])


# ----------------------------------------------------------- what is asked
# no material, no mark
def look_before(_fresh):
    b = anywhere_named(drawn(vpm.T('Mark In')))
    check("with nothing in the player the Mark In button is not available",
          b is not None and not b.isEnabled(),
          "%d such buttons, enabled %s against False"
          % (0 if b is None else 1, b is not None and b.isEnabled()))
    said = vpm.T('In point and Out point are available once the time axis '
                 'is set -- from the timecode or measured.')
    found = label_saying(said)
    check("and the window says why no mark can be made yet",
          found is not None, "%d labels carry %r against 1"
          % (0 if found is None else 1, said[:44]))
    # The second door. It was standing open while the first was locked:
    # the buttons went dead without a time axis, and the menu wrote
    # +0:00:00.000 into both fields all the same.
    live = [k for k in ('Mark In', 'Mark Out')
            if action_named(drawn(vpm.T(k))) is None
            or action_named(drawn(vpm.T(k))).isEnabled()]
    check("with nothing in the player the menu entries are dead too",
          not live, "%d of 2 still live: %s" % (len(live), live))
    for k in ('Mark In', 'Mark Out'):
        entry = action_named(drawn(vpm.T(k)))
        if entry is not None:
            entry.trigger()
    app.processEvents()
    check("and choosing one then writes nothing into the two fields",
          not in_shown() and not out_shown(),
          "In %r and Out %r, both wanted empty" % (in_shown(), out_shown()))


# the button
def open_project():
    """Open the project the way somebody would: with the button.

    Reading the project runs to its end inside the click, so the click
    stands in the step: what happened before it cannot be read.
    """
    top = window_of()
    for b in top.findChildren(QtWidgets.QPushButton):
        if drawn(b.text()).strip().startswith(
                vpm.T('Open project ...')[:8]):
            b.click()
            return
    check("every step was answered", False, "no Open project button")


def opened(_fresh):
    p = preview_player()
    where = os.path.basename(getattr(p, "file_path", "") or "") or "nothing"
    how_long = 0
    try:
        how_long = p.player.duration()
    except AttributeError:
        pass
    check("the project is open and a file stands in the player",
          player_ready(), "%s, %d ms" % (where, how_long))
    check("the material carries a timecode, so a mark is a clock time",
          getattr(p, "tc0", None) is not None,
          "start %r, %g pictures a second"
          % (getattr(p, "tc0", None), player_fps()))
    both = [k for k in ('Mark In', 'Mark Out')
            if (button_named(drawn(vpm.T(k))) is None
                or not button_named(drawn(vpm.T(k))).isEnabled())]
    check("with material there both mark buttons are available",
          not both, "not available: %s" % both)


def move_to(seconds):
    def do():
        p = preview_player()
        if p is None:
            return
        # Letting go of the position slider is what makes the player follow.
        p.slider.setValue(int(seconds * 1000))
        p.released()
        app.processEvents()
    return do


def stands_at(seconds):
    def ok():
        p = preview_player()
        try:
            return abs(p.spot_s() - seconds) <= NEAR
        except AttributeError:
            return False
    return ok


def moved(seconds):
    def then(_fresh):
        p = preview_player()
        check("the player stands where it was moved to", stands_at(seconds)(),
              "%.3f s against %.3f s, at most %.3f s apart"
              % (-1.0 if p is None else p.spot_s(), seconds, NEAR))
    return then


def press(caption):
    def do():
        b = button_named(drawn(vpm.T(caption)))
        if b is not None:
            b.click()
    return do


def trigger(caption):
    def do():
        a = action_named(drawn(vpm.T(caption)))
        if a is not None:
            a.trigger()
    return do


def in_marked(fresh):
    said, clock = in_shown(), player_clock()
    kept["in"] = said
    check("Mark In writes the clock time the player shows",
          bool(clock) and said == clock, "%r against %r" % (said, clock))
    check("the In point reaches the trimming exactly as it stands on screen",
          fresh is not None and fresh["in"] == said,
          "%r against %r" % (None if fresh is None else fresh["in"], said))


def out_marked(fresh):
    said, clock = out_shown(), player_clock()
    kept["out"] = said
    check("Mark Out writes the clock time the player shows",
          bool(clock) and said == clock, "%r against %r" % (said, clock))
    check("the Out point reaches the trimming exactly as it stands on screen",
          fresh is not None and fresh["out"] == said,
          "%r against %r" % (None if fresh is None else fresh["out"], said))
    fps = player_fps()
    a = clock_seconds(kept.get("in"), fps)
    b = clock_seconds(said, fps)
    check("the two marks lie as far apart as the player was dragged",
          a is not None and b is not None
          and abs((b - a) - (OUT_AT - IN_AT)) <= 1.0 / fps,
          "%s to %s is %s s, dragged %.3f s"
          % (kept.get("in"), said, "?" if a is None or b is None
             else "%.3f" % (b - a), OUT_AT - IN_AT))


# the menu entry, the second door
def keys_of_the_menu():
    """The two keys, read off the entries that carry them."""
    a = action_named(drawn(vpm.T('Mark In')))
    said = "" if a is None else a.shortcut().toString()
    check("the Mark In entry carries the key I", said == "I",
          "entry %s, key %r against 'I'" % (a is not None, said))
    b = action_named(drawn(vpm.T('Mark Out')))
    said = "" if b is None else b.shortcut().toString()
    check("the Mark Out entry carries the key O", said == "O",
          "entry %s, key %r against 'O'" % (b is not None, said))


def menu_out_marked(fresh):
    said, clock = out_shown(), player_clock()
    before = kept.get("out")
    check("the menu entry marks the Out point where the player stands",
          bool(clock) and said == clock, "%r against %r" % (said, clock))
    check("and it moved the mark away from where the button had put it",
          bool(said) and said != before, "%r -> %r" % (before, said))
    kept["out"] = said
    kept["out_arrived"] = None if fresh is None else fresh["out"]


def menu_in_marked(fresh):
    said, clock = in_shown(), player_clock()
    before = kept.get("in")
    check("the menu entry marks the In point where the player stands",
          bool(clock) and said == clock, "%r against %r" % (said, clock))
    check("and it moved that mark too, away from the button's",
          bool(said) and said != before, "%r -> %r" % (before, said))
    kept["in"] = said


# the project file
def save_project():
    kept["files"] = project_files()
    a = action_named(drawn(vpm.T('Save project')))
    if a is not None:
        a.trigger()


def written_out(_fresh):
    d, path = newest_project()
    where = os.path.basename(path or "") or "nothing"
    check("the project file carries the In point as it stands on screen",
          bool(d) and d.get("in_point") == kept.get("in"),
          "%s: %r against %r"
          % (where, None if not d else d.get("in_point"), kept.get("in")))
    check("and the Out point as it stands on screen",
          bool(d) and d.get("out_point") == kept.get("out"),
          "%s: %r against %r"
          % (where, None if not d else d.get("out_point"), kept.get("out")))


# an Out point in front of the In point
COMPLAINT = vpm.T('Out point lies less than 5 seconds after In point.')


def complaint_up():
    return label_saying(COMPLAINT) is not None


def out_before_in(_fresh):
    said, clock = out_shown(), player_clock()
    fps = player_fps()
    a = clock_seconds(kept.get("in"), fps)
    b = clock_seconds(said, fps)
    check("an Out point in front of the In point is taken as it stands",
          bool(clock) and said == clock and a is not None and b is not None
          and b < a,
          "In %s, Out %r against the player's %r" % (kept.get("in"), said,
                                                    clock))
    check("and the trimming says on screen why it will not cut that",
          complaint_up(), "%d labels carry %r against 1, after %d trimmings"
          % (0 if not complaint_up() else 1, COMPLAINT[:40], len(seen)))


# ------------------------------------------------------------- the running
def start():
    top = window_of()
    if top is None:
        check("every step was answered", False, "no window came up")
        app.quit()
        return
    top.resize(*WINDOW)
    app.processEvents()
    drive()


step("0. nothing is loaded yet", lambda: None, look_before)
step("1. the project is opened", open_project, opened, until=player_ready)
step("1b. the player goes where the marks are made",
     lambda: tab_to(drawn(vpm.T('Assignment'))), lambda _f: None,
     until=player_ready)
step("2. the player is dragged to the In point", move_to(IN_AT),
     moved(IN_AT), until=stands_at(IN_AT))
step("2b. Mark In is pressed", press('Mark In'), in_marked, watch=True)
step("3. the player is dragged to the Out point", move_to(OUT_AT),
     moved(OUT_AT), until=stands_at(OUT_AT))
step("3b. Mark Out is pressed", press('Mark Out'), out_marked, watch=True)
step("4. the keys on the two menu entries", lambda: None,
     lambda _f: keys_of_the_menu())
step("4b. the player is dragged further on", move_to(MENU_OUT_AT),
     moved(MENU_OUT_AT), until=stands_at(MENU_OUT_AT))
step("4c. Mark Out is chosen from the menu", trigger('Mark Out'),
     menu_out_marked, watch=True)
step("4d. the player is dragged back", move_to(MENU_IN_AT),
     moved(MENU_IN_AT), until=stands_at(MENU_IN_AT))
step("4e. Mark In is chosen from the menu", trigger('Mark In'),
     menu_in_marked, watch=True)
step("5. the project is saved", save_project, written_out,
     until=lambda: project_files() != kept.get("files"))
step("6. the player is dragged in front of the In point", move_to(BACK_AT),
     moved(BACK_AT), until=stands_at(BACK_AT))
step("6b. Mark Out is pressed there", press('Mark Out'), out_before_in,
     until=complaint_up)


QtCore.QTimer.singleShot(1200, start)
# A window that never comes up must not hold the suite -- and must not
# pass either: nothing has been checked then, and the count says so.
QtCore.QTimer.singleShot(420000, app.quit)


def let_go_of(what):
    """Make every player let go of what it has open in there.

    Under Windows a folder with an open file cannot be deleted, so
    every player is asked, by what it has open and under both its
    names: the material is linked to, and the link alone lands in the
    shared fixture. A player that never started is not stopped -- what
    lies behind stop() waits for a lock another player holds.
    """
    roots = [os.path.abspath(what), os.path.realpath(what)]
    let_go = []

    def belongs(where):
        for held in (os.path.abspath(where), os.path.realpath(where)):
            for root in roots:
                if held == root or held.startswith(root + os.sep):
                    return True
        return False

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

    Let go, close, delete, in that order, and no ignore_errors: it
    would swallow the one thing that can go wrong here, a folder that
    stays because something still holds it. Letting go returns before
    the file is free, so what is waited for is the handle and not a
    number of milliseconds. What stays is named and does not fail.
    """
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


sys.argv = ["videopodcast_magic.py"]
vpm.gui()
if not plan or not plan[-1]["begun"]:
    check("every step was run", False,
          "%d of %d" % (sum(1 for j in plan if j["begun"]), len(plan)))
clean_up(FOLDER)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
