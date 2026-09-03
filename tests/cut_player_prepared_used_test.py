# -*- coding: utf-8 -*-
"""Which recording a camera is heard with in the preview.

A camera plays the recording assigned to it, preferably the prepared
one from auphonic.com, "final_<name>_<timecode>.wav"; the raw
recording sits 16 to 36 dB below that, so switching sounds like a
fault. Four steps are checked through a real window: the prepared
track of the person on that camera, failing that their raw recording,
for a camera nobody is assigned to the prepared overall mix, and with
no prepared folder at all nothing at all.

The question is asked the way a person asks it -- click the camera,
read what the player says it is playing -- and a guessed speaker name
must find its prepared track just like a typed one. The cut on the
Resolve sheet buys from the same shop, and it must build itself only
out of what the window measured: opening that sheet is what sets the
measurement going, and because it costs minutes on the graphics card,
opening it again -- while one runs, and once the answer is in -- must
set nothing going. Two things lie about the whole time and must have
no effect: a stranger's handover in the result folder, and an earlier
production's prepared tracks below the material.
"""
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
import time
import wave

sys.path.insert(0, HERE)
from fixture_root import fixture

# No window on anybody's desktop, and no sound next to it. The program
# reads VPM_SILENT with bool(), so every value silences the player,
# "0" as well.
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("VPM_SILENT", "1")
os.environ.setdefault("VPM_NO_UPDATE_CHECK", "1")
# Nothing is taken apart into voices here: a separation fetches
# hundreds of megabytes and runs for minutes.
os.environ["VPM_NO_SPEAKER_SPLIT"] = "1"

# The first speaker is typed in, the second is left to the guess the
# file name gives -- the prepared track has to be found either way.
TYPED = "Presenter_REC00021.wav"
GUESSED = "Guest_Take0021A_Timecode.wav"
CAM_TYPED = "PresentersCam_01011855_C002.mov"
CAM_GUESSED = "GuestCam_01011858_C003.mov"
CAM_WIDE = "WideCam_01011855_C001.mov"
TYPED_NAME = "Presenter"
# One clock for everything, written in here rather than taken as it
# comes: a recording without a clock has to be measured and the player
# drops a track it cannot yet place, and three cameras on three
# timecodes would put the one prepared mix beside only one of them.
CLOCK = 19 * 3600 + 4 * 60             # 19:04:00:00, the material
# The tracks from auphonic.com are trimmed to the window asked for, so
# they begin later than the material. Were the shift nought, the check
# would prove nothing: nought is also what a player shows that places
# nothing at all.
MIX_LEAD = 30.0
MIX_CLOCK = CLOCK + MIX_LEAD           # 19:04:30:00, the prepared tracks
TAIL = "19-04-30-00"                   # the timecode in the file name
WINDOW = (1400, 950)
# Who has the turn when, in the two recordings written below. The
# window measures this for itself; nothing hands it the answer.
LENGTH = 120
TURNS = {TYPED: [(0, 20), (40, 60), (80, 100)],
         GUESSED: [(20, 40), (60, 80), (100, 120)]}

from PySide6 import QtCore, QtWidgets     # noqa: E402  after the platform
from PySide6.QtTest import QTest          # noqa: E402

import importlib.util                     # noqa: E402

app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
# The language is settled, or a run on a German machine would compare
# English keys against a German window.
vpm.set_language("en")
# Nothing may reach the network or the keychain: what is wanted is the
# window, not a run.
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.update_offer = lambda *a, **k: None

# Every reading of the recordings the window sets going, counted where
# it is set going. It runs in a thread of its own and costs minutes on
# the graphics card, so how often it is started is the whole point of
# three of the judgements below. The real reading follows, unchanged,
# so what reaches the cut is the window's own answer; the gate only
# holds it still where a judgement needs it running, and it is let go
# again in the same step.
measurements = []
go_on = threading.Event()
_really_measure = vpm.speaker_measure_loop


def counted_measure(tracks, bridge, bridge_emit):
    measurements.append(len(tracks))
    go_on.wait(60)
    _really_measure(tracks, bridge, bridge_emit)


vpm.speaker_measure_loop = counted_measure

# The counter is called "counted" and not "done": "done" is the flag
# below that says the plan got to its end.
began = time.time()
counted = 0
error = []


def check(name, ok, extra=""):
    global counted
    counted += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append("%s [%s]" % (name, extra or "no numbers"))


# Worked out with the program's own functions rather than written
# down: whoever changes how a name is guessed changes the material of
# this test with it.
GUESSED_NAME = vpm.guess_worth_using(vpm.guess_speaker_name(GUESSED))

material = fixture("interview")
missing = [n for n in (CAM_TYPED, CAM_GUESSED, CAM_WIDE)
           if not os.path.exists(os.path.join(material, n))]
if missing or not GUESSED_NAME:
    print("SKIPPED: no material under %s -- missing %s"
          % (material, ", ".join(missing) or "a guessable name"))
    # Out through the same lines as every other way out: the run reads
    # the count off the last of them, and a way out that prints none
    # leaves the number unsaid rather than saying nought.
    print("\n%d checks in %.2f s" % (counted, time.time() - began))
    print("FAIL: " + " | ".join(error) if error else "ALL OK")
    sys.exit(1 if error else 0)


# ------------------------------------------------------------- material
def timecode_in(path, seconds):
    """Put a BWF marker into a WAV that has none.

    The bext chunk goes in front of the others and the RIFF length is
    corrected; that is where the program looks for the start time.
    """
    raw = open(path, "rb").read()
    if raw[:4] != b"RIFF" or raw[8:12] != b"WAVE":
        raise ValueError("%s is no RIFF/WAVE file" % path)
    body = bytearray(602)               # bext version 0, without history
    struct.pack_into("<Q", body, 338, int(round(seconds * 48000)))
    out = bytearray(raw[:12] + b"bext" + struct.pack("<I", len(body))
                    + bytes(body) + raw[12:])
    struct.pack_into("<I", out, 4, len(out) - 8)
    with open(path, "wb") as f:
        f.write(bytes(out))


def silent_wav(path, seconds=1.0, clock=None):
    """A short, real WAV on the clock: it is chosen, not listened to."""
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(48000)
        f.writeframes(b"\x00\x00" * int(48000 * seconds))
    timecode_in(path, CLOCK if clock is None else clock)


def one_second(amplitude, hz=500.0, rate=48000):
    """One second of a tone, as bytes, to be laid end to end."""
    return b"".join(struct.pack("<h", int(amplitude * 32767 * math.sin(
        2 * math.pi * hz * i / rate))) for i in range(rate))


LOUD = one_second(0.5)
# The room between the turns, seven blocks and never twice the same in
# a row; why is in voice_wav.
FLOOR = [one_second(0.002 * (1.35 ** k)) for k in range(7)]


def voice_wav(path, turns, seconds=LENGTH):
    """One person's recording: loud on their turn, the room between.

    The window measures who speaks when out of the recordings, and the
    shared fixture holds only unbroken sine tones. Two traps shape the
    room between the turns: blocks at exactly nought are left out of
    the noise floor, so the floor becomes the speech itself, and a
    quiet block that never varies makes the bleed between the
    microphones exact, which leaves nothing standing either. So the
    room breathes, seven levels in turn, 46 to 34 dB under the speech.
    """
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(48000)
        for second in range(int(seconds)):
            f.writeframes(LOUD if any(a <= second < b for a, b in turns)
                          else FLOOR[second % len(FLOOR)])
    timecode_in(path, CLOCK)


own = tempfile.mkdtemp(prefix="vpm_prepared_")
aside = tempfile.mkdtemp(prefix="vpm_prepared_aside_")
# The recordings and the result lie beside each other, not one inside
# the other, and that is deliberate: a run writes where it is told to,
# which is usually not the folder the cameras were emptied into. Were
# the result a subfolder of the material, the window would reach the
# prepared tracks a second way -- one level below the material -- and a
# version that had stopped looking in the output folder altogether
# would still find them here.
media = os.path.join(own, "Recordings")
result = os.path.join(own, "Result")
done_folder = os.path.join(result, "auphonic-tracks")
os.makedirs(done_folder)
os.makedirs(media)
here = {}
for name in (TYPED, GUESSED, CAM_TYPED, CAM_GUESSED, CAM_WIDE):
    copy = os.path.join(media, name)
    here[name] = copy
    if name.endswith(".mov"):
        # Only stamped, not re-encoded: the clock is written beside
        # the pictures as they are copied through.
        subprocess.run(["ffmpeg", "-v", "error", "-i",
                        os.path.join(material, name), "-c", "copy",
                        "-timecode", "19:04:00:00", "-y", copy],
                       check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    else:
        # Written, not copied: somebody has to be audible in these.
        voice_wav(copy, TURNS[name])

FINAL = {n: os.path.join(done_folder, "final_%s_%s.wav" % (n, TAIL))
         for n in (TYPED_NAME, GUESSED_NAME, "Full-Mix")}
for path in FINAL.values():
    silent_wav(path, clock=MIX_CLOCK)
# What else comes back from a run and must never be played: the raw
# return, which is neither trimmed nor on the axis, the master and the
# statistics. They lie in the folder rather than in a comment -- a rule
# nothing tries to break is not checked.
for name in ("%s.wav" % TYPED_NAME, "Full-Mix.wav", "Interview_master.wav"):
    silent_wav(os.path.join(done_folder, name), clock=MIX_CLOCK)
with open(os.path.join(done_folder, "Interview_statistics.json"), "w",
          encoding="utf-8") as f:
    json.dump({}, f)

# The second bait, and it stays there to the end: an earlier
# production's prepared tracks, one level below the material, where the
# window looks last. The folder this run wrote comes first, so nothing
# may ever come out of here. Same three people, another day: the
# timecode in the names and the clock inside them are different, so a
# track taken from the wrong folder is named in the line that falls.
EARLIER_TAIL = "15-00-00-00"
EARLIER_CLOCK = 15 * 3600
EARLIER_FOLDER = os.path.join(media, "earlier-episode", "auphonic-tracks")
os.makedirs(EARLIER_FOLDER)
EARLIER = {n: os.path.join(EARLIER_FOLDER,
                           "final_%s_%s.wav" % (n, EARLIER_TAIL))
           for n in (TYPED_NAME, GUESSED_NAME, "Full-Mix")}
for path in EARLIER.values():
    silent_wav(path, clock=EARLIER_CLOCK)

# Multitrack, because only then does a recording belong to one camera.
# Who sits in front of which is picked in the sheet below: opening a
# multitrack project clears the stored assignment on purpose and works
# it out again from the speaker names.
project = os.path.join(media, "videopodcast-magic_Prepared.json")
with open(project, "w", encoding="utf-8") as f:
    json.dump({
        "format": vpm.FILE_FORMAT, "version": "test", "timeline": [],
        "call": [], "preset": "", "production": "Prepared",
        "multitrack": True, "out_folder": result, "assignment": {},
        "files": [{"path": here[n],
                   "kind": "video" if n.endswith(".mov") else "audio"}
                  for n in (TYPED, GUESSED, CAM_TYPED, CAM_GUESSED,
                            CAM_WIDE)],
    }, f, ensure_ascii=False, indent=1)

# The bait, and it stays there to the end: a stranger's handover in
# the right format under the right name. It has to be usable, or the
# window throws it out and it proves nothing -- so it covers the whole
# window. Only the material is wrong: other cameras, 600 s off. The
# zero point and the mix shift do not tell the two apart, because every
# handover is trimmed to the window's own In point.
FOREIGN_START = CLOCK - 120.0
FOREIGN_LENGTH = 600.0
FOREIGN_OFFSET = 600.0
FOREIGN_FOLDER = os.path.join(aside, "four-days-ago")
foreign_handover = os.path.join(result, "Prepared_resolve.json")


def foreign_camera(name, track, speakers, wide):
    where = os.path.join(FOREIGN_FOLDER, name)
    return {"file": where, "source": where, "camera": name,
            "track": track, "speakers": speakers,
            "audio_tracks": speakers or ["Full-Mix"],
            "offset": FOREIGN_OFFSET, "duration": FOREIGN_LENGTH,
            "wide": wide}


def foreign_turns(first):
    """Turns of half a minute over the whole ten minutes.

    Every window of two minutes then holds both people, whichever two
    minutes the window trims this file to -- so what comes out of it is
    a cut and not a single camera.
    """
    return [[float(a), float(a + 30)]
            for a in range(0 if first else 30, int(FOREIGN_LENGTH), 60)]


with open(foreign_handover, "w", encoding="utf-8") as f:
    json.dump({
        "format": vpm.FILE_FORMAT, "created_by": "another instance",
        "production": "Prepared", "fps": 25, "fps_measured": 25.0,
        "drop_frame": False, "width": 320, "height": 180,
        "start_tc": "19:02:00:00", "start_s": FOREIGN_START,
        "length_s": FOREIGN_LENGTH, "lufs": -16.0,
        "intro": None, "outro": None,
        "cameras": [
            foreign_camera("Old_C001.mov", TYPED_NAME, [TYPED_NAME],
                           False),
            foreign_camera("Old_C002.mov", GUESSED_NAME, [GUESSED_NAME],
                           False),
            foreign_camera("Old_C003.mov", "Wide", [], True)],
        "cut": [],
        "speakers": [
            {"name": TYPED_NAME, "sections": foreign_turns(True)},
            {"name": GUESSED_NAME, "sections": foreign_turns(False)}],
        "audio_files": {}, "words": [],
    }, f, ensure_ascii=False, indent=1)

# What the window has to arrive at by itself: programme time starts
# where the earliest recording starts, so the cameras sit at nought and
# the mix at the half minute it was trimmed to.
OWN_ZERO = CLOCK
OWN_MIX_SHIFT = MIX_LEAD
OWN_CAMERA_SHIFT = 0.0
OWN_CAMERAS = sorted(here[n] for n in (CAM_TYPED, CAM_GUESSED, CAM_WIDE))

QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (project, ""))
# Nothing may sit and wait for a click: a modal window would hold the
# suite until somebody kills it.
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
# Off the desktop on the way in: the offscreen platform keeps the
# window out of the window server, this keeps it off any screen.
_show = QtWidgets.QWidget.show


def offstage(self):
    self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
    _show(self)


QtWidgets.QWidget.show = offstage
QtWidgets.QDialog.show = offstage


# --------------------------------------------------- reading the window
def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def by_columns(*wanted):
    """The view whose columns are called these, whatever class it is.

    Not "the first table with rows": these views have changed class
    before and may again. Every view answers for its column names
    through QAbstractItemModel, and that is what a person reads.
    """
    for view in win().findChildren(QtWidgets.QAbstractItemView):
        # A header is a view too, and answers out of the same model.
        if isinstance(view, QtWidgets.QHeaderView):
            continue
        model = view.model()
        if model is None or not model.columnCount():
            continue
        titles = [str(model.headerData(c, QtCore.Qt.Horizontal) or "")
                  for c in range(model.columnCount())]
        if all(w in titles for w in wanted):
            return view
    return None


def cameras_view():
    return by_columns(vpm.T('Camera'), vpm.T('new file name'))


def assignment_view():
    return by_columns(vpm.T('Audio recording'), vpm.T('Speaker name'))


def player():
    """The preview player: the widget the tick over the picture sits in.

    Found through the tick and not by class: it is the same widget
    whether the player is the built-in one or a stand-in.
    """
    said = vpm.T('hear assigned audio')
    for box in win().findChildren(QtWidgets.QCheckBox):
        if box.text() != said:
            continue
        up = box.parentWidget()
        while up is not None and not hasattr(up, "track_path"):
            up = up.parentWidget()
        return up
    return None


def tick():
    """The tick that says whether the assigned audio is heard."""
    said = vpm.T('hear assigned audio')
    for box in win().findChildren(QtWidgets.QCheckBox):
        if box.text() == said:
            return box
    return None


def playing():
    """The file the player has under the picture, by its name alone."""
    p = player()
    path = None if p is None else getattr(p, "track_path", None)
    return os.path.basename(path) if path else None


def cut_player():
    """The player that runs the camera cut on the Resolve sheet.

    Found by what it must have to do that: an audio file of its own and
    a shift between programme time and that file. The preview player
    has no such shift, so the two cannot be confused.
    """
    for w in win().findChildren(QtWidgets.QWidget):
        if hasattr(w, "audio_offset") and hasattr(w, "audio"):
            return w
    return None


def cut_audio():
    """What the cut player was given: the file, and its shift.

    Nothing on the sheet writes the file name out, so it is read off
    the player. The whole path, not the name at the end of it: two
    folders here hold a file of that name, and a name cannot tell them
    apart -- nor tell either of them from a path to nothing at all.
    """
    p = cut_player()
    if p is None:
        return None, None
    where = p.audio.source().toLocalFile()
    return (where or None), p.audio_offset


def cut_places():
    """Where the cut player puts things: zero point and camera shifts.

    Both are what a wrong handover would move: it brings its own zero,
    and every camera hangs off it.
    """
    p = cut_player()
    if p is None:
        return None, {}
    return getattr(p, "tc0", None), dict(getattr(p, "offset", None) or {})


def cut_shots():
    """The shots the cut player holds: (from, to, camera) each."""
    p = cut_player()
    return list(getattr(p, "cut", None) or []) if p else []


def cut_cameras():
    """The cameras the cut player switches between, by their names."""
    return sorted({who for _a, _b, who in cut_shots()})


def cut_files():
    """The camera files the cut player was handed, whole paths."""
    p = cut_player()
    return sorted((getattr(p, "files", None) or {}).values()) if p else []


def tab_bar():
    """The bar of sheets, found by the one sheet that is always there."""
    for tw in win().findChildren(QtWidgets.QTabWidget):
        if tw.count() and tw.tabText(0).startswith(
                vpm.T('Files && production')):
            return tw
    return None


def cut_sheet():
    """The Resolve sheet, found by its name in the bar of sheets."""
    bar = tab_bar()
    if bar is None:
        return None
    for i in range(bar.count()):
        if bar.tabText(i).startswith(vpm.T('Resolve cut')):
            return bar.widget(i)
    return None


def sheets_offered():
    """The sheets the bar holds, for a failure line."""
    bar = tab_bar()
    return [] if bar is None else [bar.tabText(i) for i in range(bar.count())]


def sheet_says():
    """Everything the Resolve sheet has in words, as a person reads it.

    Read off the whole sheet rather than off one label picked out
    beforehand: what used to name that label -- the button it stood
    beside -- is gone, and its tooltip is wording like any other and
    moves when somebody rewrites it. The sentences looked for below
    all go through T() and are the program's own.
    """
    sheet = cut_sheet()
    if sheet is None:
        return []
    return [w.text().strip() for w in sheet.findChildren(QtWidgets.QLabel)
            if w.text().strip()]


def measure_note():
    """What the sheet says, short enough for a failure line.

    The sheet also carries the paragraph that explains the settings,
    which is longer than a whole failure line may be and carries line
    breaks a register row cannot hold. So: the short lines only, the
    last of them, which is where the one about the speakers sits.
    """
    said = [" ".join(x.split()) for x in sheet_says()]
    short = [x for x in said if len(x) < 70]
    return "%d lines on the sheet, the last short ones %s" % (len(said),
                                                              short[-6:])


def open_cut_sheet():
    """Click on the Resolve sheet, the way a person does."""
    bar, sheet = tab_bar(), cut_sheet()
    if bar is None or sheet is None:
        return False
    bar.setCurrentWidget(sheet)
    app.processEvents()
    return True


def look_away_and_back():
    """Off the Resolve sheet and onto it again, as a person would."""
    bar = tab_bar()
    if bar is None:
        return False
    bar.setCurrentIndex(0)
    app.processEvents()
    return open_cut_sheet()


def pick_camera(name):
    """Click that camera in the camera sheet, the way a person does.

    Selecting a row is what loads a file into the preview player. The
    row is looked up by the file name in it, not by its position.
    """
    view = cameras_view()
    if view is None:
        return False
    model = view.model()
    for r in range(model.rowCount()):
        if str(model.index(r, 0).data() or "") != name:
            continue
        view.clearSelection()
        view.setCurrentIndex(QtCore.QModelIndex())
        view.setCurrentIndex(model.index(r, 0))
        app.processEvents()
        return True
    return False


def cameras_listed():
    """The camera names the sheet shows, for a failure line.

    A click that finds no row leaves nothing behind to read: without the
    names that were there, red says only that the row was not found.
    """
    view = cameras_view()
    if view is None:
        return "no camera sheet in the window"
    model = view.model()
    return "%d rows in the camera sheet: %s" % (
        model.rowCount(),
        [str(model.index(r, 0).data() or "") for r in range(model.rowCount())])


def ask_again():
    """Make the player work the question out afresh.

    Nothing watches the folder: which file belongs to the camera is
    decided when the tick is set, so taking it off and putting it back
    is the gesture that asks again.
    """
    tick().setChecked(False)
    app.processEvents()
    tick().setChecked(True)
    app.processEvents()


def field_of(recording, column):
    """The field of that recording's row in that column.

    The row is found by the name its fields carry for a screen reader,
    "<column> -- <recording>": the part behind the first dash names the
    row, in a table and in a tree alike.
    """
    view = assignment_view()
    if view is None:
        return None
    for w in view.findChildren(QtWidgets.QWidget):
        said = w.accessibleName()
        if " -- " not in said:
            continue
        head, row = [x.strip() for x in said.split(" -- ", 1)]
        if head == column and row == recording:
            return w
    return None


def hint_for(recording):
    """The grey suggestion in the name field of that recording."""
    w = field_of(recording, vpm.T('Speaker name'))
    inner = getattr(w, "lineEdit", None)
    inner = inner() if callable(inner) else w
    if inner is not None and hasattr(inner, "placeholderText"):
        return str(inner.placeholderText())
    return None


def name_in(recording):
    """What is actually typed in that name field, as opposed to grey."""
    w = field_of(recording, vpm.T('Speaker name'))
    for way in ("currentText", "text"):
        if w is not None and hasattr(w, way):
            return str(getattr(w, way)()).strip()
    return None


def camera_of(recording):
    """Which camera that recording is assigned to, as the sheet has it."""
    w = field_of(recording, vpm.T('belongs to'))
    return None if w is None else w.currentData()


def put_on_camera(recording, camera):
    """Pick that camera for that recording, the way a person picks it."""
    w = field_of(recording, vpm.T('belongs to'))
    if w is None or w.findData(camera) < 0:
        return False
    w.setCurrentIndex(w.findData(camera))
    app.processEvents()
    return True


def cameras_offered(recording):
    """What the 'belongs to' box of that row offers, for a failure line."""
    w = field_of(recording, vpm.T('belongs to'))
    if w is None:
        return "the row has no 'belongs to' field"
    return "%d cameras offered: %s" % (
        w.count(), [w.itemData(i) for i in range(w.count())])


def type_name(recording, text):
    """Type a speaker name in, letter by letter, and be done with it.

    Letter by letter and not setText, and Return is what ends it --
    the same as clicking elsewhere.
    """
    w = field_of(recording, vpm.T('Speaker name'))
    if w is None:
        return False
    inner = getattr(w, "lineEdit", None)
    inner = inner() if callable(inner) else w
    QTest.keyClicks(inner, text)
    QTest.keyClick(inner, QtCore.Qt.Key_Return)
    app.processEvents()
    return True


def says_prepared(name):
    """What the tick says while a prepared track is playing."""
    return vpm.T('Playing %s -- the processed track from '
                 'auphonic.com,\nbrought to broadcast level. The same '
                 'audio as in the camera cut.') % name


def says_raw(name):
    """What the tick says while the raw recording is playing."""
    return vpm.T('Playing %s -- the raw recording.\nIt is much quieter '
                 'than the processed audio; once the tracks from '
                 'auphonic.com\nare there, the preview takes those.') % name


# ------------------------------------------------------------ the steps
# One thing at a time, each a moment of its own: loading a file runs
# through ffprobe and the media layer, and a check made in the same
# breath reads the state that is about to go.
AGAIN, STOP = "again", "stop"
# The two pauses between steps, in milliseconds: the short one for a
# step that asks to be asked again, the longer one between two steps.
# They stand here because a round is the unit every wait below counts
# in, and a wait that says how long it waited has to read the length of
# a round off the same place the timer does.
AGAIN_MS, STEP_MS = 250, 500
waited = [0]
done = [False]


def open_project():
    win().show()
    win().resize(*WINDOW)
    app.processEvents()
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(vpm.T('Open project ...')[:8]):
            w.click()
            break


def wait_for_sheets():
    """Wait for the sheets the project brings, not for a set time.

    They are built out of a thread once every file has been looked at,
    and a fixed pause would be wrong on both sides. What has to be
    there is known beforehand: two recordings and three cameras.
    """
    cams, rows = cameras_view(), assignment_view()
    there = (cams is not None and rows is not None
             and cams.model().rowCount() == 3
             and rows.model().rowCount() == 2)
    if not there and waited[0] < 160:
        waited[0] += 1
        return AGAIN
    check("the project brought its sheets up", there,
          "" if there else "cameras=%s recordings=%s"
          % (cams and cams.model().rowCount(),
             rows and rows.model().rowCount()))
    if not there:
        return STOP
    seat, box = player(), tick()
    check("the preview player is the one with the assigned-audio tick",
          seat is not None and box is not None,
          "ticks in the window saying %r: %d; the widget holding one %s"
          % (vpm.T('hear assigned audio'),
             sum(1 for b in win().findChildren(QtWidgets.QCheckBox)
                 if b.text() == vpm.T('hear assigned audio')),
             "was found" if seat is not None else "was not"))
    if seat is None or box is None:
        return STOP
    check("and the tick is set, so the assigned audio is what plays",
          box.isChecked(), "tick %s, and %s is under the picture"
          % (box.isChecked(), playing()))


def put_them_on_cameras():
    """Say who sits in front of which camera, in the sheet."""
    check("the first recording can be put on a camera",
          put_on_camera(TYPED, CAM_TYPED),
          "%s wanted; %s" % (CAM_TYPED, cameras_offered(TYPED)))
    check("and the second one too", put_on_camera(GUESSED, CAM_GUESSED),
          "%s wanted; %s" % (CAM_GUESSED, cameras_offered(GUESSED)))


def type_one_name():
    """One name is typed in. The other is left to the guess."""
    check("a name can be typed in for the first",
          type_name(TYPED, TYPED_NAME),
          "%r typed, the field now holds %r"
          % (TYPED_NAME, name_in(TYPED)))


def typed_name_look():
    """The speaker was typed in: his camera gets his prepared track."""
    check("the typed name stands in the field",
          name_in(TYPED) == TYPED_NAME, repr(name_in(TYPED)))
    check("and his recording is assigned to his camera",
          camera_of(TYPED) == CAM_TYPED, repr(camera_of(TYPED)))
    check("his camera can be clicked", pick_camera(CAM_TYPED),
          "%s wanted; %s" % (CAM_TYPED, cameras_listed()))
    got = playing()
    check("and it plays the track prepared for him",
          got == os.path.basename(FINAL[TYPED_NAME]), str(got))
    # The raw return from auphonic.com is called "<name>.wav" and lies
    # in the same folder: taking it would sound right and be wrong.
    check("not the raw return of the same name, nor the master",
          got not in ("%s.wav" % TYPED_NAME, "Interview_master.wav"),
          str(got))
    check("and the tick says a prepared track is playing",
          tick().toolTip() == says_prepared(got), repr(tick().toolTip()))


def guessed_name_look():
    """The speaker is only guessed: the same has to happen.

    The name field starts empty with the guess from the file name in
    grey, and that guess is the name the recording works under. The
    prepared track is looked up by the name, so it has to be found
    here as well.
    """
    check("nothing is typed in this field", name_in(GUESSED) == "",
          repr(name_in(GUESSED)))
    check("but the guess stands in it in grey, and it is a name",
          hint_for(GUESSED) == GUESSED_NAME,
          "%r against %r" % (hint_for(GUESSED), GUESSED_NAME))
    check("and her recording is assigned to her camera",
          camera_of(GUESSED) == CAM_GUESSED, repr(camera_of(GUESSED)))
    check("her camera can be clicked", pick_camera(CAM_GUESSED),
          "%s wanted; %s" % (CAM_GUESSED, cameras_listed()))
    got = playing()
    check("and a guessed name finds its prepared track too",
          got == os.path.basename(FINAL[GUESSED_NAME]),
          "%s instead of %s"
          % (got, os.path.basename(FINAL[GUESSED_NAME])))


def wide_look():
    """A camera nobody is assigned to: the prepared overall mix."""
    check("the wide shot can be clicked", pick_camera(CAM_WIDE),
          "%s wanted; %s" % (CAM_WIDE, cameras_listed()))
    got = playing()
    check("and it plays the prepared overall mix",
          got == os.path.basename(FINAL["Full-Mix"]), str(got))
    check("not the raw return of the mix", got != "Full-Mix.wav", str(got))


cut_waited = [0]
sound_waited = [0]
# How far the sound may lag behind the cut, counted in rounds of the
# step below. The cut is drawn from what the window measured; the mix
# comes out of a search through folders, and a program that draws the
# one at once and hands the other in when the search comes back is
# right rather than broken. Where the mix is there in the same breath,
# as it is today, not one of these rounds is used, so the bound is only
# ever paid in a run that is going red anyway -- which is why it is set
# well above the lag measured here rather than at the edge of it: the
# builder is about nine times slower than this machine.
SOUND_ROUNDS = 20


def open_the_cut_sheet():
    """Have the window work out who speaks when, here and now.

    Nothing on disk tells the window where the speakers are, and there
    is no button to ask with any more: opening the Resolve sheet is
    what sets the reading going. It runs in a thread of its own, and
    what comes of it is waited for below.

    The second look is taken while that reading is still running, and
    it is held here rather than raced against: a reading that had
    already come back would answer the question of the step after this
    one instead of this one's.
    """
    opened = open_cut_sheet()
    check("the Resolve sheet is there to be opened", opened,
          "%r wanted; the window offers %s"
          % (vpm.T('Resolve cut'), sheets_offered()))
    if not opened:
        return STOP
    check("opening the Resolve sheet sets the speaker measurement going",
          len(measurements) == 1,
          "%d measurements set going, wanted 1; %s"
          % (len(measurements), measure_note()))
    working = vpm.T('working out who speaks when ...')
    check("and the sheet says while it runs that it is working it out",
          working in sheet_says(),
          "%r not among the %s" % (working, measure_note()))
    came_back = look_away_and_back()
    check("a second look while it runs sets no second measurement going",
          came_back and len(measurements) == 1,
          "%d measurements after looking away and back, wanted 1; the "
          "sheet %s and there are %s"
          % (len(measurements),
             "was opened again" if came_back else "never came back",
             measure_note()))
    # Let go, or the reading never reaches the cut the steps below read.
    go_on.set()


def cut_look():
    """The cut on the Resolve sheet runs on the prepared mix too.

    The window works the cut out of its own measurement after a timer
    of its own, so what is waited for is the cut, never a set time. A
    cut is there when the player holds more than one camera file: with
    no cut it is handed the single file the preview shows, and that is
    the only state a cut can be confused with -- not "more than one
    shot", because that one file is a shot too.

    The sound then gets a second wait of its own, a short one, and
    after it it is judged either way -- because waiting and judging are
    two things, and putting them in one guard loses one fault or the
    other. With the sound inside the one long wait, a version that put
    no mix under the cut ran that wait out, said the cut had never
    come, and stopped, while the three lines that name the real fault
    never spoke. With no wait for the sound at all, a version that
    draws the cut at once and hands the mix in when the folder search
    comes back -- the obvious step once the output folder may sit on a
    network share -- comes to rest right and is called red three times
    over. So: first the sound is there or the patience is out, then the
    judgement, and every line that falls says which of the two it was.
    """
    shots, files = cut_shots(), cut_files()
    there = bool(shots) and len(files) > 1
    if not there and cut_waited[0] < 200:
        cut_waited[0] += 1
        return AGAIN
    # A path is not a file: handed the name alone, or the same name in
    # the folder above, the player has nothing to play and says nothing
    # about it. And a camera file is not an answer here but the state
    # before one -- it is what the program falls back to while no
    # prepared mix is there, and what it is left holding when none ever
    # comes. So both make the sound "not yet there" and are waited on,
    # and both are a red line once the patience is out.
    where, off = cut_audio()
    on_disk = bool(where) and os.path.isfile(where)
    a_camera = bool(where) and os.path.realpath(where) in [
        os.path.realpath(x) for x in files]
    sound_there = on_disk and not a_camera
    if there and not sound_there and sound_waited[0] < SOUND_ROUNDS:
        sound_waited[0] += 1
        return AGAIN
    # What ended that second wait, in every line resting on it.
    heard = ("the sound was there after %d of %d rounds"
             % (sound_waited[0], SOUND_ROUNDS) if sound_there else
             "no sound of its own came in %d rounds, %.1f s of waiting"
             % (sound_waited[0], sound_waited[0] * AGAIN_MS / 1000.0))
    check("the window worked a cut out on its own, from no file", there,
          "%d shots on %d cameras (%s), %d camera files, sound %s, after "
          "%d rounds -- %s"
          % (len(shots), len(cut_cameras()),
             ", ".join(cut_cameras()) or "none", len(files),
             os.path.basename(where) if where else None, cut_waited[0],
             measure_note()))
    if not there:
        return STOP
    check("the cut player was given an audio file", sound_there,
          "%s -- %s, and it is %s of the %d camera files under the cut; %s"
          % (where, "a file that is there" if on_disk else "nothing on disk",
             "one" if a_camera else "none", len(files), heard))
    name = os.path.basename(where) if where else None
    check("and it is the prepared overall mix",
          name == os.path.basename(FINAL["Full-Mix"]),
          "%s -- %s" % (name, heard))
    check("placed by its own timecode against programme time",
          off is not None and abs(off - OWN_MIX_SHIFT) < 0.001,
          "%s, wanted %s -- %s" % (off, OWN_MIX_SHIFT, heard))


def sheet_again_look():
    """The answer is in, and a fresh look must not pay for it twice.

    The cut above is only there because the reading came back, so by
    here the window knows who speaks when. Opening the sheet again is
    the commonest thing a person does on it, and each time it costs
    minutes of the graphics card if the window forgets what it has.
    """
    came_back = look_away_and_back()
    check("no measurement is set going once the speakers are known",
          came_back and len(measurements) == 1,
          "%d measurements after the answer was in, wanted 1; the sheet "
          "%s and there are %s"
          % (len(measurements),
             "was opened again" if came_back else "never came back",
             measure_note()))


def bait_look():
    """The strange handover lies right there, and nothing reads it.

    Without this the rule could fall back and every other line here
    would stay green: there would be a cut, the prepared mix would be
    under it, and only the material would be somebody else's. So the
    cut is held against the material rather than against the clock:
    which camera files it runs on, and where they sit.
    """
    zero, places = cut_places()
    files = cut_files()
    check("the cut runs on the cameras of this project",
          bool(files) and not set(files) - set(OWN_CAMERAS),
          "%s -- not this project's: %s; the strange file names its "
          "cameras in %s"
          % (sorted(os.path.basename(x) for x in files),
             sorted(os.path.basename(x) for x in set(files)
                    - set(OWN_CAMERAS)) or "none",
             FOREIGN_FOLDER))
    check("and every one of them where its own timecode puts it",
          bool(places) and all(abs(v - OWN_CAMERA_SHIFT) < 0.001
                               for v in places.values()),
          "%s, wanted %s each -- the file carries %s"
          % (sorted(places.values()), OWN_CAMERA_SHIFT, FOREIGN_OFFSET))
    check("programme time starts where the material starts",
          zero is not None and abs(zero - OWN_ZERO) < 0.001,
          "%s, wanted %s" % (zero, OWN_ZERO))
    check("and the file is still lying there, ignored rather than eaten",
          os.path.exists(foreign_handover), foreign_handover)


def let_go_of(what):
    """Make every player let go of what it has open there.

    A held file can still be moved under macOS and Linux, under Windows
    it cannot, so nothing is moved before the players have let go.
    Asked of every player by what it has open rather than by which one
    it is, so a second holder does not go unnoticed. A player that
    never started is not stopped: what lies behind stop() is built on
    first use, and that building waits for a lock another player holds
    while starting up, so the window never comes back.
    """
    what = os.path.realpath(what)
    let_go = []
    for top in app.topLevelWidgets():
        for x in top.findChildren(QtCore.QObject):
            if not (hasattr(x, "setSource") and hasattr(x, "source")):
                continue
            where = x.source()
            if not isinstance(where, QtCore.QUrl):
                continue
            where = where.toLocalFile()
            if not where:
                continue
            held = os.path.realpath(where)
            if held != what and not held.startswith(what + os.sep):
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

    gui() comes back with the window still standing: let go, close,
    delete, in that order, and no ignore_errors -- it would swallow the
    one thing that can go wrong here. Letting go returns before the file
    is free, the backend closes the handle in a thread of its own, and
    on Windows a held file cannot be deleted, so the handle is waited
    for up to ten seconds. What is left after that is named rather than
    turned red.
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


def take_his_track_away():
    """Only his prepared track goes; the folder and the rest stay."""
    print("  let go of %s"
          % (", ".join(let_go_of(FINAL[TYPED_NAME])) or "nothing"))
    shutil.move(FINAL[TYPED_NAME], os.path.join(aside, "his.wav"))


def raw_look():
    """Nothing prepared for him: his raw recording, and the tick says so."""
    check("his camera can be clicked again", pick_camera(CAM_TYPED),
          "%s wanted; %s" % (CAM_TYPED, cameras_listed()))
    ask_again()
    got = playing()
    check("without a prepared track it plays the raw recording",
          got == TYPED, str(got))
    check("and the tick says it is the raw one, and quieter",
          tick().toolTip() == says_raw(got), repr(tick().toolTip()))


def take_the_folder_away():
    """Both folders of prepared tracks, out of every reach.

    The program looks in the output folder, in the folder the material
    comes from and one level below, so moving one aside within any of
    them would still find it -- and leaving the earlier production's
    folder standing would keep the window supplied out of the very
    place the step is meant to empty.
    """
    print("  let go of %s"
          % (", ".join(let_go_of(done_folder) + let_go_of(EARLIER_FOLDER))
             or "nothing"))
    shutil.move(done_folder, os.path.join(aside, "auphonic-tracks"))
    shutil.move(EARLIER_FOLDER, os.path.join(aside, "earlier-auphonic-tracks"))


def nothing_look():
    """No prepared folder at all: silence for the wide shot."""
    check("the wide shot can be clicked once more", pick_camera(CAM_WIDE),
          "%s wanted; %s" % (CAM_WIDE, cameras_listed()))
    ask_again()
    check("with nothing prepared the wide shot gets no audio",
          playing() is None, str(playing()))
    check("his camera can be clicked once more", pick_camera(CAM_TYPED),
          "%s wanted; %s" % (CAM_TYPED, cameras_listed()))
    ask_again()
    check("but he still gets his raw recording", playing() == TYPED,
          str(playing()))


plan = [open_project, wait_for_sheets, put_them_on_cameras, type_one_name,
        typed_name_look, guessed_name_look, wide_look, open_the_cut_sheet,
        cut_look, sheet_again_look, bait_look, take_his_track_away, raw_look,
        take_the_folder_away, nothing_look]


def stop_now():
    # The verdict is said in one place, at the foot of the file: the
    # window can also go out through the timer below, and a count
    # printed only here would leave that way out reporting nothing.
    done[0] = True
    # Let a held reading go on whichever way out is taken, so it is
    # never the thing that keeps a file open while the folder goes.
    go_on.set()
    app.quit()


def step():
    if not plan:
        stop_now()
        return
    try:
        answer = plan[0]()
    except Exception:
        import traceback
        traceback.print_exc()
        error.append("crash")
        stop_now()
        return
    if answer == STOP:
        stop_now()
        return
    if answer != AGAIN:
        plan.pop(0)
    QtCore.QTimer.singleShot(AGAIN_MS if answer == AGAIN else STEP_MS, step)


QtCore.QTimer.singleShot(300, step)
# A window that never gets there must not hold the suite -- there is no
# timeout(1) on this machine -- and must not pass either.
QtCore.QTimer.singleShot(240000, app.quit)
vpm.gui()
if not done[0]:
    print("  the window never got as far as the checks   FAIL")
    error.append("no answer")
clean_up(aside)
print("\n%d checks in %.2f s" % (counted, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
