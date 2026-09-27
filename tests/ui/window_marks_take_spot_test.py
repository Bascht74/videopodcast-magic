# -*- coding: utf-8 -*-
"""What Mark In and Mark Out set is where the player stands.

An In point taken as given says nothing about the buttons that make
one. So the player is dragged to a spot, the mark is made, and what
came of it is read off the screen and off what reached the trimming --
held as moments, since the field shows a clock time and the mark
travels counted from where every camera runs. In order: no material
and no mark at either door; the ground, a file with a timecode in the
player and the time axis measured; the button; the menu entry, with its
key; the project file; an Out point in front of the In point; Mark In
on a recording, and on a camera at 29.97 beside 25 ones, where the run
reads it and where 'to In point' goes back to; and a step whose answer never comes, red where it stands.
From the project file on, run_three_ways_agree has it, and this one
stops there.
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
import the_program
from let_go import clean_up

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
import subprocess
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
# The blocks after each head: the preview is the run, and the run places
# a recording by all of its sound, never by its first 40 s alone.
BLOCKS = ("Presenter_REC00022.wav", "Presenter_REC00023.wav",
          "CoPresenter_REC00019.wav", "CoPresenter_REC00020.wav")
WIDE = "WideCam_01011855_C001.mov"
HOSTS = "PresentersCam_01011855_C002.mov"
GUESTS = "GuestCam_01011858_C003.mov"
CAMERAS = (WIDE, HOSTS, GUESTS)
# A camera at 29.97, made here: no sound, so its clock places it and the
# run never takes it for its reference -- though it runs longest of all,
# which by the files alone would make it one.
NTSC = "CoPresenterCam_01011855_C004.mov"
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
# A recording in front of where every camera runs (17.48 s), so its mark
# is a timecode. Six tenths into a second: 15 frames at 25 and 18 at 30,
# which a reading at 25 would take for 0.72 s -- three frames late.
SOUND_AT = 10.6
# The run reads a timecode at its reference camera's rate; every camera
# here runs at 25, and the wide shot's clock reads 18:55:00:00.
RUN_FPS = 25.0
WIDE_CLOCK = 18 * 3600 + 55 * 60.0
# On the 29.97 camera, in front of where every camera runs as well: six
# tenths into a second are 18 frames at 29.97, read at 25 as 0.72 s.
NTSC_CLOCK = WIDE_CLOCK + 12.6
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
    for name in (SPLIT, PLAIN) + BLOCKS + CAMERAS:
        link = os.path.join(own, name)
        if not os.path.exists(link):
            os.symlink(os.path.join(source, name), link)
        here[name] = link
    here[NTSC] = os.path.join(own, NTSC)
    # Its own clock at its own rate, as a recorder writes it.
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "testsrc=size=320x180:rate=30000/1001", "-t", "125",
                    "-c:v", "libx264", "-preset", "ultrafast",
                    "-timecode", "18:55:04:00", here[NTSC]], check=True)
    assignment = {"voice:V0": HOSTS, "voice:V1": GUESTS}
    one = here[SPLIT]
    st = os.stat(one)
    d = {"format": vpm.FILE_FORMAT, "version": "test", "timeline": [],
         "files": [{"path": here[n],
                    "kind": "video" if n.endswith(".mov") else "audio"}
                   for n in (SPLIT, PLAIN) + BLOCKS + CAMERAS + (NTSC,)],
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
    # Where the trimming cut, on the clock: start_s is the time of day
    # programme time begins at, and after trimming that is the In point.
    cut = out[0] if not out[1] and isinstance(out[0], dict) else {}
    seen.append({"in": in_point, "out": out_point, "complaint": out[1],
                 "start": cut.get("start_s"), "length": cut.get("length_s")})
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
    and the moment it names is what travels on.
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


def cut_at(fresh, end=False):
    """Where the trimming cut, in seconds of the clock, or None."""
    if fresh is None or fresh.get("start") is None:
        return None
    if not end:
        return float(fresh["start"])
    if fresh.get("length") is None:
        return None
    return float(fresh["start"]) + float(fresh["length"])


def in_marked(fresh):
    said, clock = in_shown(), player_clock()
    kept["in"] = said
    check("Mark In writes the clock time the player shows",
          bool(clock) and said == clock, "%r against %r" % (said, clock))
    fps = player_fps()
    at, meant = cut_at(fresh), clock_seconds(said, fps)
    check("the trimming begins at the In point the screen shows",
          at is not None and meant is not None
          and abs(at - meant) <= 0.5 / fps + 0.001,
          "cut at %s s, screen %r = %s s, sent %r, at most %.3f s apart"
          % (at, said, meant, None if fresh is None else fresh["in"],
             0.5 / fps + 0.001))


def out_marked(fresh):
    said, clock = out_shown(), player_clock()
    kept["out"] = said
    check("Mark Out writes the clock time the player shows",
          bool(clock) and said == clock, "%r against %r" % (said, clock))
    fps = player_fps()
    at, meant = cut_at(fresh, end=True), clock_seconds(said, fps)
    check("the trimming ends at the Out point the screen shows",
          at is not None and meant is not None
          and abs(at - meant) <= 0.5 / fps + 0.001,
          "cut until %s s, screen %r = %s s, sent %r, at most %.3f s apart"
          % (at, said, meant, None if fresh is None else fresh["out"],
             0.5 / fps + 0.001))
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
    kept["in_arrived"] = None if fresh is None else fresh["in"]


# the project file
def save_project():
    kept["files"] = project_files()
    a = action_named(drawn(vpm.T('Save project')))
    if a is not None:
        a.trigger()


def written_out(_fresh):
    d, path = newest_project()
    where = os.path.basename(path or "") or "nothing"
    check("the project file keeps the In point the trimming got",
          bool(d) and d.get("in_point") == kept.get("in_arrived")
          and bool(kept.get("in_arrived")),
          "%s: %r against %r, the screen showing %r"
          % (where, None if not d else d.get("in_point"),
             kept.get("in_arrived"), kept.get("in")))
    check("and the Out point the trimming got",
          bool(d) and d.get("out_point") == kept.get("out_arrived")
          and bool(kept.get("out_arrived")),
          "%s: %r against %r, the screen showing %r"
          % (where, None if not d else d.get("out_point"),
             kept.get("out_arrived"), kept.get("out")))


# an Out point in front of the In point: the preview is the run, stopped
# before it writes, so what it says is the run's own refusal.
COMPLAINT = vpm.T('    Out point lies before In point -- that does not '
                  'work.').strip()


def axis_measured():
    """Has the time axis been measured and written into the project file?

    Written by the program once the measurement lands, so it moves only
    because the program worked. Every mark below is read against where
    the material starts, and that is only settled once the axis is.
    """
    d, _path = newest_project()
    return bool(d and d.get("timeline"))


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


# a mark on a recording
def to_recording():
    p = preview_player()
    if p is not None:
        p.load(os.path.join(FOLDER, PLAIN), SOUND_AT)
        app.processEvents()


def on_recording():
    p = preview_player()
    return (p is not None and os.path.basename(p.file_path or "") == PLAIN
            and stands_at(SOUND_AT)())


def sound_marked(_fresh):
    """The field's In point, read the way the run reads it, by hand.

    The run's own reader, handed the wide camera the way the run hands
    it its reference, and no window to pull the point back into.
    """
    import contextlib
    import io
    import types
    p = preview_player()
    said = in_shown()
    meant = read = None
    try:
        meant = p.axis_s() + p.spot_s()
        wide = os.path.join(FOLDER, WIDE)
        with contextlib.redirect_stdout(io.StringIO()):
            got = vpm.clip_to_time_window(
                types.SimpleNamespace(in_point=said, out_point=None),
                -1e6, 1e6, (wide, vpm.video_facts(wide)))
        read = None if got[0] is None else WIDE_CLOCK + got[0]
    except (AttributeError, TypeError):
        pass
    check("Mark In on a recording is the moment the run reads",
          meant is not None and read is not None
          and abs(read - meant) <= 1.0 / RUN_FPS,
          "field %r on %s, player at %s s, run reads %s s, at most %.3f s "
          "apart, player at %g fps"
          % (said, os.path.basename(getattr(p, "file_path", "") or "-"),
             None if meant is None else "%.3f" % meant,
             None if read is None else "%.3f" % read, 1.0 / RUN_FPS,
             player_fps()))


# a mark on a camera at another rate
def to_ntsc():
    p = preview_player()
    if p is not None:
        p.load(os.path.join(FOLDER, NTSC), 1.0)
        app.processEvents()


def on_ntsc():
    p = preview_player()
    return (p is not None and os.path.basename(p.file_path or "") == NTSC
            and getattr(p, "axis_s", lambda: None)() is not None)


def ntsc_spot():
    """Where in the 29.97 file the clock reads NTSC_CLOCK."""
    p = preview_player()
    return NTSC_CLOCK - p.axis_s()


def to_ntsc_spot():
    move_to(ntsc_spot())()


def ntsc_marked(_fresh):
    """As sound_marked, on a camera whose own rate is not the run's."""
    import contextlib
    import io
    import types
    p = preview_player()
    said = in_shown()
    meant = read = None
    try:
        meant = p.axis_s() + p.spot_s()
        wide = os.path.join(FOLDER, WIDE)
        with contextlib.redirect_stdout(io.StringIO()):
            got = vpm.clip_to_time_window(
                types.SimpleNamespace(in_point=said, out_point=None),
                -1e6, 1e6, (wide, vpm.video_facts(wide)))
        read = None if got[0] is None else WIDE_CLOCK + got[0]
    except (AttributeError, TypeError):
        pass
    check("Mark In on a 29.97 camera is the moment the run reads at 25",
          meant is not None and read is not None
          and abs(read - meant) <= 1.0 / RUN_FPS,
          "field %r on %s, player at %s s, run reads %s s, at most %.3f s "
          "apart, player at %g fps"
          % (said, os.path.basename(getattr(p, "file_path", "") or "-"),
             None if meant is None else "%.3f" % meant,
             None if read is None else "%.3f" % read, 1.0 / RUN_FPS,
             player_fps()))
    kept["ntsc_at"] = None if p is None else p.spot_s()


def ntsc_back(_fresh):
    """The player reads the mark as it wrote it: at the run's rate."""
    p = preview_player()
    was, now = kept.get("ntsc_at"), None if p is None else p.spot_s()
    check("and 'to In point' goes back there, on the 29.97 camera",
          was is not None and now is not None
          and abs(now - was) <= 1.0 / RUN_FPS,
          "field %r, player at %s s against %s s marked, at most %.3f s "
          "apart, on %s" % (in_shown(), None if now is None else "%.3f" % now,
                            None if was is None else "%.3f" % was,
                            1.0 / RUN_FPS, os.path.basename(
                                getattr(p, "file_path", "") or "-")))


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
# The preview's run begins on the first look at its tab.
step("1a. the Resolve cut tab is looked at once",
     lambda: tab_to(drawn(vpm.T('Resolve cut'))), lambda _f: None)
step("1b. the player goes where the marks are made",
     lambda: tab_to(drawn(vpm.T('Assignment'))), lambda _f: None,
     until=player_ready)
step("1c. the time axis is measured", lambda: None, lambda _f: None,
     until=axis_measured)
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
step("7. a recording goes into the player, before every camera runs",
     to_recording, lambda _f: None, until=on_recording)
step("7b. Mark In is pressed there", press('Mark In'), sound_marked,
     until=lambda: in_shown() != kept.get("in"))
step("8. a camera at 29.97 goes into the player", to_ntsc,
     lambda _f: kept.update(sound_in=in_shown()), until=on_ntsc)
step("8a. it is dragged in front of where every camera runs", to_ntsc_spot,
     lambda _f: None, until=lambda: stands_at(ntsc_spot())())
step("8b. Mark In is pressed there", press('Mark In'), ntsc_marked,
     until=lambda: in_shown() != kept.get("sound_in"))
step("8c. the player is dragged away from it", move_to(MENU_OUT_AT),
     moved(MENU_OUT_AT), until=stands_at(MENU_OUT_AT))
step("8d. 'to In point' is pressed", press('to In point'), ntsc_back,
     until=lambda: not stands_at(MENU_OUT_AT)())


QtCore.QTimer.singleShot(1200, start)
# A window that never comes up must not hold the suite -- and must not
# pass either: nothing has been checked then, and the count says so.
QtCore.QTimer.singleShot(420000, app.quit)


sys.argv = ["videopodcast_magic.py"]
vpm.gui()
if not plan or not plan[-1]["begun"]:
    check("every step was run", False,
          "%d of %d" % (sum(1 for j in plan if j["begun"]), len(plan)))
clean_up(FOLDER)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
