# -*- coding: utf-8 -*-
"""What the window is told is what the calculation gets.

handover_test.py hands `wide_marks_applied` and `cut_statistics` a
dictionary it built itself. That checks the arithmetic. It does not
check the piece in front of it: the window reading its own fields and
handing the answers over. Between the answer on the screen and the
call there is a wiring nobody watched, and that is where the faults of
this week sat -- the camera table not listening to the voices, the
preview reading a stale handover file, the numbers on the third tab
never reaching the run.

So the two functions are wrapped here and the window is driven from
the outside: an answer is given the way somebody at the screen would
give it -- a name typed key by key, an entry picked in a chooser, a
button pressed -- and then it is read off what arrived at the
calculation. Never a value written into a variable by hand: that would
check the variable, not the wiring.

Six wirings, each with a counter-check. A check that is green whatever
the answer is has not checked the wiring, so every one of them is run
twice with different answers and the two readings are held against
each other:

  the Kind of a file       content, wide shot, intro, ignore
  the wide shot mark       which camera, and whether anybody said so
  a speaker's camera       moved from one camera to another
  a name in a track        typed, then typed over
  the eight cut numbers    two sets, every number read back
  the In point             marked twice from two positions

The material is the shared interview fixture, linked to rather than
copied, with a separation stored in the project the way the program
stores one -- the same road cut_gate_test.py takes. Nothing is
measured and nothing is uploaded.

One of these does not hold, and it is left red rather than taken out.
A name typed into a track does reach the calculation -- but not by
itself: the preview computes again for a chooser, for a number and
for a mark, and not for a name. Measured on 29.8.2026: twelve seconds
after the last keystroke, neither the trimming nor the cut had run
once, and the new name arrived the moment anything else asked for the
cut. So the preview goes on showing the old speaker at the old camera
until something unrelated is touched.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
sys.path.insert(0, HERE)

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["VPM_SILENT"] = "1"
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
# The separation never runs here: what it would have found is in the
# project file already, and a run would fetch a model.
os.environ["VPM_NO_SPEAKER_SPLIT"] = "1"

import importlib.util
import json
import shutil
import tempfile

from PySide6 import QtCore, QtWidgets
from PySide6.QtTest import QTest

from fixture_root import fixture

app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.update_offer = lambda *a, **k: None
vpm.set_language("en")

# How long one answer may take to reach the calculation. The preview
# waits 400 ms after the last keystroke before it computes, so this is
# fifty times what the machine here needs -- and a wiring that never
# fires must not hold the suite either.
PATIENCE = 60
POLL = 200
WINDOW = (1400, 950)
# VPM_WIRING_DUMP=1 writes down every reading, not only the ones a
# check asks about.
DUMP = bool(os.environ.get("VPM_WIRING_DUMP"))

SPLIT = "Moderator_REC00009.wav"          # the recording with the voices
PLAIN = "Moderatorin_REC00008.wav"        # the recording with a name field
WIDE = "Totale_08141855_C003.mov"
HOSTS = "Moderatoren_08141855_C005.mov"
GUESTS = "Kandidat_08141858_C009.mov"
CAMERAS = (WIDE, HOSTS, GUESTS)
VOICES = (("V0", "Host"), ("V1", "Guest"))
# Two voices over the whole recording, so that a time window a few
# seconds in still leaves material behind.
SEGMENTS = [["V0", 0.5, 12.0], ["V1", 13.0, 24.0],
            ["V0", 25.0, 33.0], ["V1", 34.0, 39.0]]
# How far the player is dragged before the In point is marked a second
# time. Far enough that the two marks cannot be read as one, and far
# short of the material, which is under forty seconds long.
MOVED_TO = 6.0

error = []


def check(name, ok, extra=""):
    print("  %-54s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


def drawn(text):
    """What ends up on the screen: & marks a key, && draws one &."""
    return str(text).replace("&&", "\x00").replace("&", "") \
                    .replace("\x00", "&")


def stem_of(name):
    """The file name without folder and suffix, as the program reads it."""
    stem = os.path.splitext(os.path.basename(str(name or "")))[0]
    return stem[:-6] if stem.endswith("_audio") else stem


# ------------------------------------------------------------ the project
def own_project():
    """A project of its own, built out of the shared fixture.

    Opening a project moves the project file into its output folder and
    deletes copies lying elsewhere, so the fixture is only linked to and
    the project file is written afresh -- the same way cut_gate_test.py
    does it.
    """
    source = fixture("interview")
    own = tempfile.mkdtemp(prefix="vpm_wiring_")
    here = {}
    for name in (SPLIT, PLAIN) + CAMERAS:
        link = os.path.join(own, name)
        if not os.path.exists(link):
            os.symlink(os.path.join(source, name), link)
        here[name] = link
    # The voices carry a camera each from the start. The preselection
    # guesses from the file name, and a guess would make every reading
    # below depend on how well two names happen to match.
    assignment = {"voice:V0": HOSTS, "voice:V1": GUESTS}
    one = here[SPLIT]
    st = os.stat(one)
    d = {"format": vpm.FILE_FORMAT, "version": "test", "timeline": [],
         "call": [],
         "files": [{"path": here[n],
                    "kind": "video" if n.endswith(".mov") else "audio"}
                   for n in (SPLIT, PLAIN) + CAMERAS],
         "out_folder": os.path.join(own, "Result"),
         "production": "Wiring", "multitrack": True,
         "assignment": assignment, "preset": "",
         # Stored the way the program stores it: raw, in the time of the
         # recording, with the fingerprint of the file it was heard in.
         # A stored result whose source has changed is thrown away, and
         # this one has to survive that test.
         "speakers": {"source": os.path.abspath(one),
                      "mtime": int(st.st_mtime), "size": st.st_size,
                      "model": vpm.SPEAKER_MODEL_NAME, "model_mark": "",
                      "num_speakers": len(VOICES),
                      "names": dict(VOICES), "segments": SEGMENTS}}
    # The answer, and only the answer, brings the voices up.
    assignment["several:" + one] = True
    os.makedirs(d["out_folder"], exist_ok=True)
    path = os.path.join(own, "videopodcast-magic_Wiring.json")
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
# machine while the suite runs. The window still goes through the whole
# layout machinery, which is what makes what is read below worth
# reading.
_show = QtWidgets.QWidget.show


def offstage(self):
    self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
    _show(self)


QtWidgets.QWidget.show = offstage
QtWidgets.QDialog.show = offstage


# ------------------------------------------------------------- the spies
# The window looks both functions up in the module when it calls them,
# so replacing them here puts a reader between the window and the
# calculation. Everything is passed through unchanged: what is wanted
# is the real cut, only written down on the way.
seen = {"stat": [], "window": []}
last_wide = {}
last_window = {}

_real_wide = vpm.wide_marks_applied
_real_window = vpm.apply_time_window
_real_stat = vpm.cut_statistics


def picture_of(d):
    """What arrived, in the few values every check below asks about."""
    if not isinstance(d, dict):
        return {"cameras": [], "speakers": [], "length": None}
    return {"length": d.get("length_s"), "start": d.get("start_s"),
            "speakers": [s.get("name") for s in (d.get("speakers") or [])],
            "cameras": [{"stem": stem_of(c.get("source") or c.get("file")
                                         or c.get("camera")),
                         "who": sorted(c.get("speakers") or []),
                         "marked": bool(c.get("wide_marked")),
                         "wide": bool(c.get("wide"))}
                        for c in (d.get("cameras") or [])]}


def wide_spy(d, wide_names, speakers_on=None, marked=False):
    last_wide.clear()
    last_wide.update({"names": sorted(wide_names or []),
                      "on": dict(speakers_on or {}),
                      "marked": bool(marked)})
    return _real_wide(d, wide_names, speakers_on, marked)


def window_spy(d, in_point, out_point):
    out = _real_window(d, in_point, out_point)
    last_window.clear()
    last_window.update({"in": in_point, "out": out_point,
                        "left": picture_of(out[0]),
                        "complaint": out[1]})
    seen["window"].append(dict(last_window))
    return out


def stat_spy(d, *rest, **named):
    out = _real_stat(d, *rest, **named)
    rules = rest[6] if len(rest) > 6 else named.get("rules") or {}
    seen["stat"].append({
        "wide": dict(last_wide), "window": dict(last_window),
        "d": picture_of(d),
        # The five numbers that travel as arguments, and the three that
        # travel inside the rules. Named here the way the fields on the
        # screen are named, so a reading can be held against a field.
        "number": {"min-edit-duration": rest[0] if rest else None,
                   "edit-change-delay": rest[1] if len(rest) > 1 else None,
                   "wide-after": rest[2] if len(rest) > 2 else None,
                   "wide-length": rest[3] if len(rest) > 3 else None,
                   "wide-latest": rest[4] if len(rest) > 4 else None,
                   "min-speech-to-switch": (rules or {}).get("min_speech"),
                   "reaction-lead": (rules or {}).get("reaction_lead"),
                   "wide-most": (rules or {}).get("wide_most")},
        "edge": rest[5] if len(rest) > 5 else None,
        "out": None if not out else {
            "shots": out.get("shots"), "median": out.get("median"),
            # The cut itself, not only how many shots it has: two sets
            # of numbers can produce the same count of shots at other
            # seconds, and then a check on the count says nothing.
            "cut": [(round(a, 3), round(b, 3), who)
                    for a, b, who in (out.get("cut") or [])]}})
    if DUMP:
        print("  WIRING %s" % json.dumps(seen["stat"][-1], default=str))
    return out


vpm.wide_marks_applied = wide_spy
vpm.apply_time_window = window_spy
vpm.cut_statistics = stat_spy


# ------------------------------------------------------- reading the window
def window_of():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x
    return None


def by_columns(*wanted):
    """The view whose columns are called these, whatever class it is.

    Not "the first table with rows". The assignment was two tables and
    is now one tree over a model, and a test that names the class stops
    finding the sheet the day the class changes -- and finding nothing
    looks exactly like a project that has not opened yet. The column
    names are what a person reads off the sheet, and every view answers
    for them through QAbstractItemModel.
    """
    top = window_of()
    if top is None:
        return None, None
    for view in top.findChildren(QtWidgets.QAbstractItemView):
        # A header is a view too, hanging inside the view it belongs to
        # and answering out of the very same model.
        if isinstance(view, QtWidgets.QHeaderView):
            continue
        model = view.model()
        if model is None or not model.columnCount():
            continue
        titles = [drawn(model.headerData(c, QtCore.Qt.Horizontal) or "")
                  for c in range(model.columnCount())]
        if all(w in titles for w in wanted):
            return view, model
    return None, None


def tracks_view():
    """The assignment sheet: recordings, with their voices under them."""
    return by_columns(drawn(vpm.T('Audio recording')),
                      drawn(vpm.T('Speaker name')),
                      drawn(vpm.T('belongs to')))


def cameras_view():
    """The camera sheet, where the Kind of every video file stands."""
    return by_columns(drawn(vpm.T('Camera')), drawn(vpm.T('new file name')),
                      drawn(vpm.T('Kind')))


def field_at(view, model, row, column, parent=None):
    """The widget standing in one cell, whatever kind of view it is."""
    if view is None or model is None:
        return None
    index = (model.index(row, column, parent) if parent is not None
             else model.index(row, column))
    return view.indexWidget(index)


def chooser_in(cell):
    """The drop-down inside a cell, which may be wrapped in a box."""
    if cell is None:
        return None
    if isinstance(cell, QtWidgets.QComboBox):
        return cell
    return cell.findChild(QtWidgets.QComboBox)


def kind_box(name):
    """The Kind chooser of one video file, found by the file's name."""
    view, model = cameras_view()
    if view is None:
        return None
    head = [drawn(model.headerData(c, QtCore.Qt.Horizontal) or "")
            for c in range(model.columnCount())]
    where = head.index(drawn(vpm.T('Kind')))
    for r in range(model.rowCount()):
        if drawn(model.index(r, 0).data() or "") == name:
            return chooser_in(field_at(view, model, r, where))
    return None


def track_rows():
    """The recordings, and the voices hanging under each of them."""
    view, model = tracks_view()
    out = []
    if view is None:
        return out
    for r in range(model.rowCount()):
        top = model.index(r, 0)
        out.append({"says": drawn(top.data() or ""), "row": r,
                    "voices": [drawn(model.index(k, 0, top).data() or "")
                               for k in range(model.rowCount(top))]})
    return out


def name_field_of(row, voice=None):
    """The Speaker name field of a recording, or of a voice under it."""
    view, model = tracks_view()
    if view is None:
        return None
    top = model.index(row, 0)
    if voice is None:
        return field_at(view, model, row, 1)
    return field_at(view, model, voice, 1, top)


def camera_box_of(row, voice=None):
    """The "belongs to" chooser of a recording, or of a voice under it."""
    view, model = tracks_view()
    if view is None:
        return None
    top = model.index(row, 0)
    cell = (field_at(view, model, row, 2) if voice is None
            else field_at(view, model, voice, 2, top))
    return chooser_in(cell)


def number_fields():
    """The eight cut numbers, by the name of the switch they carry.

    Found by what a screen reader says of them, which is what the
    program itself writes on them -- not by their place in a grid.
    """
    top = window_of()
    out = {}
    if top is None:
        return out
    for key, caption, _d, unit, _s, _l in vpm.CUT_FIELDS:
        said = (vpm.T('%s, seconds') % vpm.T(caption) if unit == "s"
                else vpm.T(caption))
        for w in top.findChildren(QtWidgets.QLineEdit):
            if w.accessibleName() == said:
                out[key] = w
                break
    return out


def button_named(text):
    top = window_of()
    if top is None:
        return None
    for b in top.findChildren(QtWidgets.QPushButton):
        if drawn(b.text()).strip() == text:
            return b
    return None


def in_point_shown():
    """What the player writes as the In point -- the answer on screen.

    Inside the preview player and nowhere else. Three places in this
    window say "In point": the player, the line under the cut strip,
    and the cut player on the Resolve tab -- and the last one converts
    the position into the timecode of the clip it holds. Only the
    player's own line shows the answer itself, and the answer is what
    travels on.
    """
    p = preview_player()
    head = drawn(vpm.T('In point %s')).replace("%s", "").strip()
    if p is None:
        return ""
    for x in p.findChildren(QtWidgets.QLabel):
        said = drawn(x.text()).strip()
        if said.startswith(head):
            return said[len(head):].strip()
    return ""


def preview_player():
    """The player the In point buttons sit in, found from the button.

    Not by class and not by name: it is the widget that owns the "Mark
    In" button, which is the only thing that makes it the right one of
    the two players in this window.
    """
    b = button_named(drawn(vpm.T('Mark In')))
    up = None if b is None else b.parentWidget()
    while up is not None and not hasattr(up, "spot_s"):
        up = up.parentWidget()
    return up


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


# ------------------------------------------------------ giving an answer
def pick(box, value):
    """Pick the entry that stands for this value, the way a click does.

    setCurrentIndex alone is not enough where the entry is already the
    current one: no index changes then, and a derived wide shot is
    turned into an answer by choosing exactly the entry that is
    already showing. "activated" is the signal a click raises whether
    the index moves or not, so both are given, and the program's own
    guard keeps the answer from being taken twice.
    """
    if box is None:
        return False
    i = box.findData(value)
    if i < 0:
        return False
    box.setCurrentIndex(i)
    box.activated.emit(i)
    app.processEvents()
    return True


def type_in(field, text):
    """Type a text into a field, letter by letter.

    Not setText. The name field listens on textEdited and not on
    textChanged -- the entry it offers writes its own caption into the
    field, and an answer that came of that would undo itself in the
    same breath. Only a real keystroke tells the two apart.
    """
    if field is None:
        return False
    line = field.lineEdit() if hasattr(field, "lineEdit") else field
    if line is None:
        return False
    line.setFocus()
    line.selectAll()
    QTest.keyClicks(line, text)
    # Enter is what somebody presses when the word is finished, and it
    # is what tells the field the typing is over.
    QTest.keyClick(line, QtCore.Qt.Key_Return)
    app.processEvents()
    return True


# ------------------------------------------------------------- the driver
plan = []
at = [0]
waited = [0]
mark = {"stat": 0, "window": 0}


def step(say, do, then, watch="stat", until=None):
    """One answer given, and what must have arrived because of it.

    *watch* names the call that is waited for -- the calculation itself
    or the trimming in front of it. None means the answer changes
    nothing downstream and only *until* is waited for.
    """
    plan.append({"say": say, "do": do, "then": then, "watch": watch,
                 "until": until or (lambda: True), "begun": False})


def finish():
    print("\n%s" % ("ALL OK" if not error else "FAIL: " + ", ".join(error)))
    app.quit()


def drive():
    if at[0] >= len(plan):
        finish()
        return
    job = plan[at[0]]
    if not job["begun"]:
        job["begun"] = True
        waited[0] = 0
        mark["stat"] = len(seen["stat"])
        mark["window"] = len(seen["window"])
        try:
            job["do"]()
        except Exception:
            import traceback
            traceback.print_exc()
            check(job["say"], False, "the answer could not be given")
            at[0] += 1
        QtCore.QTimer.singleShot(150, drive)
        return
    watch = job["watch"]
    fresh = [] if watch is None else seen[watch][mark[watch]:]
    # Waiting for a fresh call and not for the clock: the preview
    # computes 400 ms after the last keystroke, and a machine under
    # load takes longer.
    settled = (watch is None or fresh)
    try:
        settled = settled and job["until"]()
    except Exception:
        settled = False
    if not settled and waited[0] < PATIENCE:
        waited[0] += 1
        QtCore.QTimer.singleShot(POLL, drive)
        return
    print("\n%s" % job["say"])
    if watch is not None and not fresh:
        check(job["say"], False,
              "nothing reached the calculation in %.1f s"
              % (waited[0] * POLL / 1000.0))
    else:
        try:
            job["then"](fresh[-1] if fresh else None, fresh)
        except Exception:
            import traceback
            traceback.print_exc()
            check(job["say"], False, "the reading could not be taken")
    at[0] += 1
    QtCore.QTimer.singleShot(50, drive)


# ----------------------------------------------------------- what is asked
def camera_named(rec, stem):
    for c in rec["d"]["cameras"]:
        if c["stem"] == stem:
            return c
    return None


kept = {}


def open_project():
    """Open the project the way somebody would: with the button.

    Reading the project runs to its end inside the click, the first
    computation of the preview with it. So the click stands in the
    step and not in front of the driver -- what happened before the
    step began cannot be read afterwards.
    """
    top = window_of()
    for b in top.findChildren(QtWidgets.QPushButton):
        if drawn(b.text()).strip().startswith(
                vpm.T('Open project ...')[:8]):
            b.click()
            return
    check("the project can be opened", False, "no Open project button")


def ready(rec, _all):
    rows = track_rows()
    kept["rows"] = rows
    check("the sheet holds both recordings",
          len(rows) == 2,
          "%d rows: %s" % (len(rows), [r["says"] for r in rows]))
    voiced = [r for r in rows if r["voices"]]
    check("the stored separation shows its two voices",
          len(voiced) == 1 and len(voiced[0]["voices"]) == 2,
          str([(r["says"], len(r["voices"])) for r in rows]))
    check("three cameras stand in the camera sheet",
          len(rec["d"]["cameras"]) == 3,
          str([c["stem"] for c in rec["d"]["cameras"]]))
    check("the two voices reach the calculation with their cameras",
          (camera_named(rec, stem_of(HOSTS)) or {}).get("who") == ["Host"]
          and (camera_named(rec, stem_of(GUESTS)) or {}).get("who")
          == ["Guest"],
          str([(c["stem"], c["who"]) for c in rec["d"]["cameras"]]))
    check("nobody marked a wide shot yet, and the calculation is told so",
          rec["wide"].get("marked") is False, str(rec["wide"]))
    check("the camera without a speaker is the derived wide shot",
          rec["wide"].get("names") == [WIDE], str(rec["wide"].get("names")))


def voiced_row():
    """Which row of the sheet carries the voices, read off the sheet."""
    for r in track_rows():
        if r["voices"]:
            return r["row"]
    return 0


def plain_row():
    for r in track_rows():
        if not r["voices"]:
            return r["row"]
    return 1


# 1. the Kind of a file, in all four of its answers
def mark_wide():
    pick(kind_box(WIDE), vpm.TYPE_WIDE)


def wide_arrived(rec, _all):
    check("the mark reaches the calculation as an answer, not a guess",
          rec["wide"].get("marked") is True, str(rec["wide"].get("marked")))
    check("and it names the camera that was marked",
          rec["wide"].get("names") == [WIDE], str(rec["wide"].get("names")))
    got = camera_named(rec, stem_of(WIDE))
    check("the camera itself arrives marked",
          bool(got) and got["marked"] is True,
          str([(c["stem"], c["marked"]) for c in rec["d"]["cameras"]]))


def mark_other_wide():
    pick(kind_box(WIDE), vpm.TYPE_CONTENT)
    pick(kind_box(HOSTS), vpm.TYPE_WIDE)


def other_wide_arrived(rec, _all):
    check("the mark moved to the other camera",
          rec["wide"].get("names") == [HOSTS], str(rec["wide"].get("names")))
    here = camera_named(rec, stem_of(HOSTS))
    there = camera_named(rec, stem_of(WIDE))
    check("and it moved in the calculation too",
          bool(here) and here["marked"] is True
          and bool(there) and there["marked"] is False,
          str([(c["stem"], c["marked"]) for c in rec["d"]["cameras"]]))


def make_intro():
    pick(kind_box(HOSTS), vpm.TYPE_CONTENT)
    pick(kind_box(WIDE), vpm.TYPE_INTRO)


def intro_arrived(rec, _all):
    check("a file called Intro is no camera any more",
          camera_named(rec, stem_of(WIDE)) is None,
          str([c["stem"] for c in rec["d"]["cameras"]]))


def make_ignored():
    pick(kind_box(WIDE), vpm.TYPE_IGNORED)


def ignored_arrived(rec, _all):
    check("a file left out stays out",
          camera_named(rec, stem_of(WIDE)) is None,
          str([c["stem"] for c in rec["d"]["cameras"]]))


def make_content():
    pick(kind_box(WIDE), vpm.TYPE_CONTENT)


def content_arrived(rec, _all):
    check("and set back to Content it is a camera again",
          camera_named(rec, stem_of(WIDE)) is not None,
          str([c["stem"] for c in rec["d"]["cameras"]]))


# 2. a speaker's camera
def move_host():
    pick(camera_box_of(voiced_row(), 0), WIDE)


def host_moved(rec, _all):
    check("the camera picked for a speaker reaches the calculation",
          rec["wide"]["on"].get("Host") == WIDE, str(rec["wide"]["on"]))
    got = camera_named(rec, stem_of(WIDE))
    check("and the speaker sits at that camera in the handover",
          bool(got) and got["who"] == ["Host"],
          str([(c["stem"], c["who"]) for c in rec["d"]["cameras"]]))
    was = camera_named(rec, stem_of(HOSTS))
    check("the camera left behind no longer carries him",
          bool(was) and was["who"] == [],
          str([(c["stem"], c["who"]) for c in rec["d"]["cameras"]]))


def move_host_back():
    pick(camera_box_of(voiced_row(), 0), HOSTS)


def host_back(rec, _all):
    check("moved back, the calculation follows again",
          rec["wide"]["on"].get("Host") == HOSTS
          and (camera_named(rec, stem_of(HOSTS)) or {}).get("who") == ["Host"],
          str(rec["wide"]["on"]))


# 3. a name typed into a track
def name_the_plain_track():
    pick(camera_box_of(plain_row()), GUESTS)
    type_in(name_field_of(plain_row()), "Sidekick")


def name_arrived(rec, _all):
    check("the typed name reaches the calculation",
          rec["wide"]["on"].get("Sidekick") == GUESTS, str(rec["wide"]["on"]))
    got = camera_named(rec, stem_of(GUESTS))
    check("and stands at its camera beside the voice already there",
          bool(got) and got["who"] == ["Guest", "Sidekick"],
          str([(c["stem"], c["who"]) for c in rec["d"]["cameras"]]))


def rename_the_plain_track():
    type_in(name_field_of(plain_row()), "Helper")


def rename_alone(_rec, _all):
    """Does a name on its own make the preview compute again?

    Read apart from whether the name arrives, because the two are not
    the same question and the answers differ. The step before changed
    a chooser as well, and a chooser rebuilds the sheet; a name is
    typed into a field that nothing else follows.
    """
    fresh = seen["stat"][mark["stat"]:]
    early = seen["window"][mark["window"]:]
    kept["rename_alone"] = bool(fresh)
    # Both counters, so the answer says which of the two happened: the
    # preview never ran, or it ran and stopped before the cut. The
    # trimming sits in front of the cut in the same function.
    check("a typed name alone makes the preview compute again",
          bool(fresh),
          "%.1f s, %d cut calls, %d window calls"
          % (waited[0] * POLL / 1000.0, len(fresh), len(early)))


def nudge():
    """Ask for the cut again without touching the assignment."""
    tab_to(drawn(vpm.T('Resolve cut')).split()[0])
    type_in(number_fields().get("wide-after"), "37")


def rename_arrived(rec, _all):
    check("typed over, the new name arrives and the old one is gone",
          rec["wide"]["on"].get("Helper") == GUESTS
          and "Sidekick" not in rec["wide"]["on"], str(rec["wide"]["on"]))
    got = camera_named(rec, stem_of(GUESTS))
    check("and the calculation shows the new name at the camera",
          bool(got) and got["who"] == ["Guest", "Helper"],
          str([(c["stem"], c["who"]) for c in rec["d"]["cameras"]]))


# 4. the eight numbers
FIRST = {"min-edit-duration": "2.5", "min-speech-to-switch": "1.1",
         "edit-change-delay": "0.7", "reaction-lead": "2.2",
         "wide-after": "31", "wide-length": "6.5",
         "wide-most": "17", "wide-latest": "95"}
# The second minimum edit duration is longer than any block in the
# material, so the shots have to fall into one another: two sets of
# numbers that leave the same cut behind would prove nothing.
SECOND = {"min-edit-duration": "15", "min-speech-to-switch": "0.4",
          "edit-change-delay": "0.2", "reaction-lead": "3.3",
          "wide-after": "9", "wide-length": "5.5",
          "wide-most": "12", "wide-latest": "60"}


def type_numbers(which):
    def do():
        tab_to(drawn(vpm.T('Resolve cut')).split()[0])
        fields = number_fields()
        missing = [k for k in which if k not in fields]
        if missing:
            check("every cut number has a field", False, str(missing))
        for key, text in which.items():
            type_in(fields.get(key), text)
    return do


def numbers_arrived(which, say):
    def then(rec, _all):
        wrong = {k: (which[k], rec["number"].get(k)) for k in which
                 if rec["number"].get(k) is None
                 or abs(float(rec["number"][k]) - float(which[k])) > 1e-6}
        check("%s: every number arrives as it was typed" % say,
              not wrong, str(wrong) if wrong else str(rec["number"]))
        kept.setdefault("numbers", []).append(rec)
    return then


def numbers_moved(_rec, _all):
    both = kept.get("numbers") or []
    if len(both) < 2:
        check("the second set can be held against the first", False,
              "%d readings" % len(both))
        return
    before, rec = both[0], both[1]
    same = [k for k in FIRST if before["number"].get(k)
            == rec["number"].get(k)]
    check("no number stayed where it was",
          not same, "unchanged: %s" % same)
    if before["out"] and rec["out"]:
        check("and the cut that comes out is a different one",
              before["out"]["cut"] != rec["out"]["cut"],
              "%d shots %s -> %d shots %s"
              % (before["out"]["shots"], before["out"]["cut"][:1],
                 rec["out"]["shots"], rec["out"]["cut"][:1]))
    else:
        check("the cut was computed for both sets of numbers",
              False, "%s -> %s" % (before["out"], rec["out"]))


# 5. the In point
def player_ready():
    """Has the player a file with a length, so a spot can be marked?

    On a Qt without multimedia the player is a stand-in that plays
    nothing; it has no length either, so this stays False and the step
    says what it saw instead of marking a spot that is not there.
    """
    p = preview_player()
    try:
        return bool(p is not None and p.player.duration() > 0)
    except AttributeError:
        return False


def wait_for_a_file():
    """Go where the player stands and let it get its file."""
    tab_to(drawn(vpm.T('Assignment')))
    app.processEvents()


def file_stands(_rec, _all):
    p = preview_player()
    where = os.path.basename(getattr(p, "file_path", "") or "") or "nothing"
    how_long = 0
    try:
        how_long = p.player.duration()
    except AttributeError:
        pass
    check("a file stands in the player, so a spot can be marked",
          player_ready(), "%s, %d ms" % (where, how_long))


def player_moved():
    """Is the player where it was dragged to?"""
    p = preview_player()
    try:
        return abs(p.spot_s() - MOVED_TO) < 1.5
    except AttributeError:
        return False


def mark_in_first():
    b = button_named(drawn(vpm.T('Mark In')))
    if b is None:
        check("the In point can be marked", False, "no Mark In button")
        return
    b.click()


def in_point_arrived(rec, _all):
    shown = in_point_shown()
    kept["in_first"] = rec
    kept["shown_first"] = shown
    check("the player shows an In point after the click",
          bool(shown) and shown != "--", repr(shown))
    check("and exactly that text reaches the calculation",
          rec["in"] == shown, "%r vs %r" % (rec["in"], shown))


def mark_in_later():
    p = preview_player()
    if p is None:
        check("the player can be moved", False, "no player")
        return
    # Dragging the position slider is what somebody at the screen does;
    # letting go is what makes the player follow.
    p.slider.setValue(int(MOVED_TO * 1000))
    p.released()
    app.processEvents()


def moved(_rec, _all):
    p = preview_player()
    check("the player really moved", player_moved(),
          "" if p is None else "%.2f s" % p.spot_s())


def mark_in_second():
    b = button_named(drawn(vpm.T('Mark In')))
    if b is not None:
        b.click()


def second_in_point(rec, _all):
    shown = in_point_shown()
    before = kept.get("in_first")
    check("the second mark is a different one",
          bool(shown) and shown != kept.get("shown_first"),
          "%r -> %r" % (kept.get("shown_first"), shown))
    check("and it too arrives unchanged",
          rec["in"] == shown, "%r vs %r" % (rec["in"], shown))
    if before is None or before["left"]["length"] is None \
            or rec["left"]["length"] is None:
        check("the trimmed material can be compared", False,
              "%s -> %s" % (before and before["left"]["length"],
                            rec["left"]["length"]))
        return
    lost = before["left"]["length"] - rec["left"]["length"]
    check("the material the calculation gets is that much shorter",
          abs(lost - MOVED_TO) < 1.0,
          "%.3f s -> %.3f s" % (before["left"]["length"],
                                rec["left"]["length"]))


# ------------------------------------------------------------- the running
def start():
    top = window_of()
    if top is None:
        check("the window came up", False, "no window")
        finish()
        return
    top.resize(*WINDOW)
    app.processEvents()
    drive()


def sheets_filled():
    """Everything the project brings has to stand in the sheets.

    Not "some rows somewhere": two recordings, two voices under one of
    them and three cameras are all known before the window opens, so
    they are what is waited for. A sheet that never turns up leaves
    this False and the step says what it saw instead.
    """
    rows = track_rows()
    _view, model = cameras_view()
    return (len(rows) == 2
            and sum(len(r["voices"]) for r in rows) == 2
            and model is not None and model.rowCount() == 3)


step("0. the project is open and the sheets are filled", open_project,
     ready, until=sheets_filled)
step("1. a camera is marked as the wide shot", mark_wide, wide_arrived)
step("1b. counter-check: the mark moves to another camera",
     mark_other_wide, other_wide_arrived)
step("1c. counter-check: the file becomes an intro", make_intro,
     intro_arrived)
step("1d. counter-check: the file is left out", make_ignored,
     ignored_arrived)
step("1e. counter-check: and is a camera again", make_content,
     content_arrived)
step("2. a speaker is given another camera", move_host, host_moved)
step("2b. counter-check: and moved back", move_host_back, host_back)
step("3. a name is typed into a track", name_the_plain_track, name_arrived)
step("3b. the name is typed over", rename_the_plain_track, rename_alone,
     watch=None, until=lambda: len(seen["stat"]) > mark["stat"])
step("3c. counter-check: the new name reaches the calculation", nudge,
     rename_arrived)
step("4. the eight cut numbers are filled in", type_numbers(FIRST),
     numbers_arrived(FIRST, "first set"))
step("4b. counter-check: eight other numbers", type_numbers(SECOND),
     numbers_arrived(SECOND, "second set"))
step("4c. counter-check: nothing stayed behind", lambda: None,
     numbers_moved, watch=None)
step("5. a file stands in the player", wait_for_a_file, file_stands,
     watch=None, until=player_ready)
step("5b. the In point is marked from the picture", mark_in_first,
     in_point_arrived, watch="window")
step("5c. the player is moved to another spot", mark_in_later, moved,
     watch=None, until=player_moved)
step("5d. counter-check: marked again from there", mark_in_second,
     second_in_point, watch="window")


QtCore.QTimer.singleShot(1200, start)
# A window that never comes up must not hold the suite -- and must not
# pass either: nothing has been checked then, and the count says so.
QtCore.QTimer.singleShot(420000, app.quit)


def let_go_of(what):
    """Make every player let go of what it has open in there.

    A player holds the file it has open. Under macOS and Linux the
    folder can be deleted anyway, under Windows it cannot -- and with
    ignore_errors nobody hears of it: the folder simply stays behind on
    every run. Every player under every window is asked, and by what it
    has open rather than by which player it is, so that a second holder
    cannot slip through. Returns the names that were let go.

    A player that never started is not stopped. What lies behind stop()
    is built on first use, and building it waits for a lock another
    player holds while it is starting up -- the window then never comes
    back. playbackState only reads what is already noted.

    The material here is linked to and not copied, so a file is asked
    for under both its names: the path the player was given, and where
    that path really leads. Following the link alone lands in the
    shared fixture, which is not the folder that is about to go, and
    every player would look like somebody else's.
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

    gui() comes back with the window still standing, so the folder used
    to go while players still held files in it. Let go, close, delete --
    in that order. And no ignore_errors: it would swallow the one thing
    that can go wrong here, a folder that stays because something still
    holds it.

    Letting go returns before the file is free. The media backend closes
    the handle in a thread of its own, so setSource() comes back while
    the system still has the file open. Under macOS and Linux that never
    shows, because a held file can be deleted there anyway. On Windows
    it does, so what is waited for is the handle, not a number of
    milliseconds -- delete, run the event loop, delete again, up to ten
    seconds. Ten because it is far above a thread closing a file, and
    still short enough that a folder which will never go does not hold
    the suite.

    What is left after that is a finding, not a failure: it is named,
    with how long it was waited on, and it does not turn the test red.
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


sys.argv = ["videopodcast-magic.py"]
vpm.gui()
if not plan or not plan[-1]["begun"]:
    check("every step was run", False,
          "%d of %d" % (sum(1 for j in plan if j["begun"]), len(plan)))
clean_up(FOLDER)
sys.exit(1 if error else 0)
