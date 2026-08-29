# -*- coding: utf-8 -*-
"""Which recording a camera is heard with in the preview.

A camera in the preview player does not play its own audio. It plays
the recording assigned to it, and preferably the prepared one: the
track that came back from auphonic.com, "final_<name>_<timecode>.wav",
at delivery level. The raw recording sits 16 to 36 dB below that, so
switching between the two players sounds like a fault -- which is why
the tick over the picture says which of the two is playing.

The rule has four steps, and all four are checked here through a real
window: the prepared track of the person on that camera, failing that
their raw recording, for a camera nobody is assigned to the prepared
overall mix, and where there is no prepared folder at all, nothing --
a wide shot then stays silent rather than playing a voice.

Until 25.8.2026 this test took audio_for_camera out of gui() with
inspect.getsource, exec'd it and handed it a dictionary of names
written out by hand. That list is a second interface, kept up to date
by nobody: the day the function was to call speaker_name_of, the test
died with NameError, and the change was taken back rather than the
test's private list extended. So there is no list any more. The window
is built for real, offscreen and off the desktop, a project is opened
in it, and the question is asked the way a person asks it -- click the
camera in the camera sheet, read what the player says it is playing.

What the player plays is read off the player itself: which file it has
under the picture, and what the tick over it says about that file. Not
which lines of gui() ran.

The fourth case is the new one and it is the reason for the rebuild.
Since 25.8.2026 a speaker name may be *guessed*: the field starts empty
with what the file name suggests standing in it in grey, and
speaker_name_of says that guess counts as the name where nothing was
typed. The prepared track is looked up by that name -- so a camera
whose speaker is only guessed must find its prepared track just like
one whose speaker was typed in. It does not yet: audio_for_camera
reads the field alone, finds nothing, and quietly hands out the raw
recording. The check for it is written here as it must come out, and
it is red until that is put right.

The cut on the Resolve sheet is asked the same question, because it
buys from the same shop: it takes the prepared overall mix and places
it by its timecode. It is asked through the handover file a run leaves
behind, which is the door the window already has.

The material is the shared interview fixture, copied into a folder of
its own and stamped with one clock -- see CLOCK below for why -- and
the prepared tracks are silent one-second WAVs written here: what is
checked is which file is chosen, not what is on it.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import wave

sys.path.insert(0, HERE)
from fixture_root import fixture

# No window on anybody's desktop, and no sound at somebody sitting
# next to it. The program reads VPM_SILENT with bool(), so every value
# silences the player, "0" as well.
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("VPM_SILENT", "1")
os.environ.setdefault("VPM_NO_UPDATE_CHECK", "1")
# Nothing is to be taken apart into voices here: a separation fetches
# 218 MB and runs for minutes, and the question is a different one.
os.environ["VPM_NO_SPEAKER_SPLIT"] = "1"

# Two recordings and three cameras out of the shared fixture. The
# first speaker is typed in, the second is left to the guess the file
# name gives -- that is the whole difference between the two, and the
# prepared track has to be found either way.
TYPED = "Moderator_REC00009.wav"
GUESSED = "Kandidat_0008A_Timecode.wav"
CAM_TYPED = "Moderatoren_08141855_C005.mov"
CAM_GUESSED = "Kandidat_08141858_C009.mov"
CAM_WIDE = "Totale_08141855_C003.mov"
TYPED_NAME = "Moderator"
# One clock for everything, cameras and recordings alike, and it is
# written in here rather than taken as it comes. Since 28.8.2026 the
# three shared cameras carry three different timecodes -- 18:55:00:00,
# 18:55:04:00 and 18:55:17:12, which is what a real shoot delivers --
# and the recordings beside them carry none at all. Neither suits this
# test. A recording without a clock has to be measured, and a player
# only keeps a track it can place beside the picture, so a test reading
# the player while the measurement is still running would see it drop
# the very track it had just chosen; and three cameras on three clocks
# would put the one prepared mix beside only one of them. So the
# cameras are stamped again on the way in, all three to the same value
# -- measured 28.8.2026: "-c copy -timecode" writes over the tag on the
# video stream and the timecode stream alike and leaves nothing of the
# old value -- and the recordings are given the BWF marker the prepared
# tracks carry anyway. What the distances between the fixture's own
# three timecodes are for is asked elsewhere.
CLOCK = 19 * 3600 + 4 * 60             # 19:04:00:00
TAIL = "19-04-00-00"                   # the timecode in the file name
WINDOW = (1400, 950)

from PySide6 import QtCore, QtWidgets     # noqa: E402  after the platform
from PySide6.QtTest import QTest          # noqa: E402

import importlib.util                     # noqa: E402

app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
# Every caption below is asked for through the catalogue, so the
# language does not decide the outcome -- but it is settled all the
# same, or a run on a German machine would compare English keys with a
# German window.
vpm.set_language("en")
# Nothing may reach the network or the keychain: what is wanted is the
# window, not a run.
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.update_offer = lambda *a, **k: None

error = []


def check(name, ok, extra=""):
    print("  %-56s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


# The name the program itself guesses out of the second file name, and
# the name its prepared track therefore carries. Worked out with the
# program's own two functions rather than written down: whoever changes
# how a name is guessed changes the material of this test with it, and
# the grey suggestion in the window is checked against the same value
# below.
GUESSED_NAME = vpm.guess_worth_using(vpm.guess_speaker_name(GUESSED))

material = fixture("interview")
missing = [n for n in (TYPED, GUESSED, CAM_TYPED, CAM_GUESSED, CAM_WIDE)
           if not os.path.exists(os.path.join(material, n))]
if missing or not GUESSED_NAME:
    print("SKIPPED: no material under %s -- missing %s"
          % (material, ", ".join(missing) or "a guessable name"))
    raise SystemExit(0)


# ------------------------------------------------------------- material
def timecode_in(path, seconds):
    """Put a BWF marker into a WAV that has none.

    The bext chunk goes in front of the ones already there and the RIFF
    length is corrected -- the same thing a recorder writes, and it is
    where the program looks for the start time of a recording.
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


def silent_wav(path, seconds=1.0):
    """A short, real WAV on the clock: it is chosen, not listened to."""
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(48000)
        f.writeframes(b"\x00\x00" * int(48000 * seconds))
    timecode_in(path, CLOCK)


own = tempfile.mkdtemp(prefix="vpm_prepared_")
aside = tempfile.mkdtemp(prefix="vpm_prepared_aside_")
result = os.path.join(own, "Result")
done_folder = os.path.join(result, "auphonic-tracks")
os.makedirs(done_folder)
here = {}
for name in (TYPED, GUESSED, CAM_TYPED, CAM_GUESSED, CAM_WIDE):
    copy = os.path.join(own, name)
    here[name] = copy
    if name.endswith(".mov"):
        # Only stamped, not re-encoded: the pictures are copied through
        # and the clock is written beside them.
        subprocess.run(["ffmpeg", "-v", "error", "-i",
                        os.path.join(material, name), "-c", "copy",
                        "-timecode", "19:04:00:00", "-y", copy],
                       check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    else:
        shutil.copyfile(os.path.join(material, name), copy)
        timecode_in(copy, CLOCK)

FINAL = {n: os.path.join(done_folder, "final_%s_%s.wav" % (n, TAIL))
         for n in (TYPED_NAME, GUESSED_NAME, "Full-Mix")}
for path in FINAL.values():
    silent_wav(path)
# What else comes back from a run and must never be played: the raw
# return, which is neither trimmed nor placed on the axis, the assembled
# master and the statistics beside it. They are in the folder rather
# than described in a comment -- a rule nothing tries to break is not
# checked.
for name in ("%s.wav" % TYPED_NAME, "Full-Mix.wav", "Interview_master.wav"):
    silent_wav(os.path.join(done_folder, name))
with open(os.path.join(done_folder, "Interview_statistics.json"), "w",
          encoding="utf-8") as f:
    json.dump({}, f)

# The project. Multitrack, because only then does a recording belong to
# one camera: without the tick every recording goes into every camera
# and no camera has a speaker of its own.
#
# Who sits in front of which camera is not written in here. It is
# picked in the sheet below, the way a person picks it -- opening a
# multitrack project clears the stored camera assignment on purpose
# ("without multitrack there was no choice") and works it out again
# from the speaker names, so a recording with no name typed in would
# arrive with no camera and the test would be measuring that instead.
project = os.path.join(own, "videopodcast-magic_Prepared.json")
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

# What a run leaves behind. The Resolve sheet measures nothing: it
# reads the handover file, "<production>_resolve.json", and the player
# under it takes its audio from the same prepared tracks -- the
# prepared overall mix, placed by its timecode. That is a second
# customer for the same folder, and it is asked through the door the
# window already has: a file of a written-down format, put where a run
# would have put it.
#
# Programme time starts half a minute after the clock the material
# carries, so the shift the player is given is a number and not a
# zero: the mix begins at 19:04:00:00 and the programme at
# 19:04:30:00, which puts the mix thirty seconds ahead of the start.
CUT_START = CLOCK + 30.0
CUT_LENGTH = 110.0
CUT_OFFSET = CLOCK - CUT_START
with open(os.path.join(result, "Prepared_resolve.json"), "w",
          encoding="utf-8") as f:
    json.dump({
        "format": vpm.FILE_FORMAT, "created_by": "test",
        "production": "Prepared", "fps": 25, "fps_measured": 25.0,
        "drop_frame": False, "width": 320, "height": 180,
        "start_tc": "19:04:30:00", "start_s": CUT_START,
        "length_s": CUT_LENGTH, "lufs": -16.0,
        "intro": None, "outro": None,
        "cameras": [
            {"file": here[CAM_TYPED], "source": here[CAM_TYPED],
             "camera": CAM_TYPED, "track": TYPED_NAME,
             "speakers": [TYPED_NAME], "audio_tracks": [TYPED_NAME],
             "offset": 0.0, "duration": CUT_LENGTH, "wide": False},
            {"file": here[CAM_GUESSED], "source": here[CAM_GUESSED],
             "camera": CAM_GUESSED, "track": GUESSED_NAME,
             "speakers": [GUESSED_NAME], "audio_tracks": [GUESSED_NAME],
             "offset": 0.0, "duration": CUT_LENGTH, "wide": False},
            {"file": here[CAM_WIDE], "source": here[CAM_WIDE],
             "camera": CAM_WIDE, "track": "Wide", "speakers": [],
             "audio_tracks": ["Full-Mix"], "offset": 0.0,
             "duration": CUT_LENGTH, "wide": True}],
        "cut": [],
        "speakers": [
            {"name": TYPED_NAME,
             "sections": [[0.0, 20.0], [40.0, 60.0], [80.0, 100.0]]},
            {"name": GUESSED_NAME,
             "sections": [[20.0, 40.0], [60.0, 80.0], [100.0, 110.0]]}],
        "audio_files": {}, "words": [],
    }, f, ensure_ascii=False, indent=1)

QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (project, ""))
# Nothing may sit and wait for a click: a modal window would hold the
# suite until somebody kills it.
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
# Off the desktop on the way in. The offscreen platform keeps the
# window out of the window server; this keeps it off the screen on any
# platform, and the layout machinery still runs.
_show = QtWidgets.QWidget.show


def offstage(self):
    self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
    _show(self)


QtWidgets.QWidget.show = offstage
QtWidgets.QDialog.show = offstage


# --------------------------------------------------- reading the window
def win():
    for x in app.topLevelWidgets():
        if x.windowTitle().startswith("Video Podcast"):
            return x


def by_columns(*wanted):
    """The view whose columns are called these, whatever class it is.

    Not "the first table with rows": the assignment was two
    QTableWidgets and is a QTreeView now, and the camera sheet may go
    the same way. Every view answers for its column names through
    QAbstractItemModel, and that is what a person reads off it.
    """
    for view in win().findChildren(QtWidgets.QAbstractItemView):
        # A header is a view too, hanging inside the view it belongs to
        # and answering out of the very same model.
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

    Found through the tick and not by class -- the tick is what a
    person sees and clicks, and it is the same widget whether the
    player is the built-in one or a stand-in.
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

    Found by what it must have to do that and by nothing else: an
    audio file of its own and a shift between programme time and that
    file. The preview player has no such shift -- it follows the
    picture -- so the two cannot be confused.
    """
    for w in win().findChildren(QtWidgets.QWidget):
        if hasattr(w, "audio_offset") and hasattr(w, "audio"):
            return w
    return None


def cut_audio():
    """What the cut player was given: the file, and its shift.

    Nothing on the sheet writes the file name out, so it is read off
    the player. It is the whole answer to "what runs under the cut":
    which file, and where in it programme time nought lies.
    """
    p = cut_player()
    if p is None:
        return None, None
    where = p.audio.source().toLocalFile()
    return (os.path.basename(where) if where else None), p.audio_offset


def pick_camera(name):
    """Click that camera in the camera sheet, the way a person does.

    Selecting a row is what loads a file into the preview player. The
    row is looked up by the file name standing in it, so the order the
    project happens to list the cameras in decides nothing.
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


def ask_again():
    """Make the player work the question out afresh.

    Nothing watches the folder: which file belongs to the camera is
    decided when the tick is set. Taking it off and putting it back is
    the gesture that asks again, and it is one a person makes.
    """
    tick().setChecked(False)
    app.processEvents()
    tick().setChecked(True)
    app.processEvents()


def field_of(recording, column):
    """The field of that recording's row in that column.

    The row is found by the name its fields are given for a screen
    reader, "Speaker name -- Kandidat_0008A_Timecode.wav": the part
    behind the first dash names the row, in a table and in a tree
    alike.
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


def type_name(recording, text):
    """Type a speaker name in, letter by letter, and be done with it.

    Letter by letter and not setText: what is typed is the answer to
    the question the row asks, and Return is what ends it -- the same
    as clicking elsewhere.
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
# One thing at a time, each a moment of its own: loading a file into the
# player runs through ffprobe and the media layer, and a check made in
# the same breath reads the state that is about to go.
AGAIN, STOP = "again", "stop"
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
    """Wait for the sheets the project brings, not for a number of seconds.

    They are built out of a thread once every file has been looked at,
    and a fixed pause would be wrong on both sides. What has to be
    there is known before the window opens: two recordings and three
    cameras.
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
    check("the preview player is the one with the assigned-audio tick",
          player() is not None and tick() is not None)
    if player() is None or tick() is None:
        return STOP
    check("and the tick is set, so the assigned audio is what plays",
          tick().isChecked())


def put_them_on_cameras():
    """Say who sits in front of which camera, in the sheet."""
    check("the first recording can be put on a camera",
          put_on_camera(TYPED, CAM_TYPED))
    check("and the second one too", put_on_camera(GUESSED, CAM_GUESSED))


def type_one_name():
    """One name is typed in. The other is left to the guess."""
    check("a name can be typed in for the first",
          type_name(TYPED, TYPED_NAME))


def typed_name_look():
    """The speaker was typed in: his camera gets his prepared track."""
    check("the typed name stands in the field",
          name_in(TYPED) == TYPED_NAME, repr(name_in(TYPED)))
    check("and his recording is assigned to his camera",
          camera_of(TYPED) == CAM_TYPED, repr(camera_of(TYPED)))
    check("his camera can be clicked", pick_camera(CAM_TYPED))
    got = playing()
    check("and it plays the track prepared for him",
          got == os.path.basename(FINAL[TYPED_NAME]), str(got))
    # The raw return from auphonic.com is called "<name>.wav" and lies
    # in the same folder. It is neither trimmed nor on the axis, and
    # taking it would sound right and be wrong.
    check("not the raw return of the same name, nor the master",
          got not in ("%s.wav" % TYPED_NAME, "Interview_master.wav"),
          str(got))
    check("and the tick says a prepared track is playing",
          tick().toolTip() == says_prepared(got), repr(tick().toolTip()))


def guessed_name_look():
    """The speaker is only guessed: the same has to happen.

    Since 25.8.2026 the name field starts empty with the guess from the
    file name in grey, and that guess is the name the recording works
    under. The prepared track is looked up by the name -- so it has to
    be found here as well. This is the check that is red until
    audio_for_camera asks speaker_name_of instead of reading the field.
    """
    check("nothing is typed in this field", name_in(GUESSED) == "",
          repr(name_in(GUESSED)))
    check("but the guess stands in it in grey, and it is a name",
          hint_for(GUESSED) == GUESSED_NAME,
          "%r against %r" % (hint_for(GUESSED), GUESSED_NAME))
    check("and her recording is assigned to her camera",
          camera_of(GUESSED) == CAM_GUESSED, repr(camera_of(GUESSED)))
    check("her camera can be clicked", pick_camera(CAM_GUESSED))
    got = playing()
    check("and a guessed name finds its prepared track too",
          got == os.path.basename(FINAL[GUESSED_NAME]),
          "%s instead of %s"
          % (got, os.path.basename(FINAL[GUESSED_NAME])))


def wide_look():
    """A camera nobody is assigned to: the prepared overall mix."""
    check("the wide shot can be clicked", pick_camera(CAM_WIDE))
    got = playing()
    check("and it plays the prepared overall mix",
          got == os.path.basename(FINAL["Full-Mix"]), str(got))
    check("not the raw return of the mix", got != "Full-Mix.wav", str(got))


cut_waited = [0]


def cut_look():
    """The cut on the Resolve sheet runs on the prepared mix too.

    The sheet works the cut out by itself from what the run left
    behind, and hands the player the audio for it. That is not a click
    away -- it happens when the window notices the handover file -- so
    it is waited for rather than timed.
    """
    name, off = cut_audio()
    if name is None and cut_waited[0] < 60:
        cut_waited[0] += 1
        return AGAIN
    check("the cut player was given an audio file", name is not None,
          str(name))
    check("and it is the prepared overall mix",
          name == os.path.basename(FINAL["Full-Mix"]), str(name))
    check("placed by its own timecode against programme time",
          off is not None and abs(off - CUT_OFFSET) < 0.001,
          "%s, wanted %s" % (off, CUT_OFFSET))


def let_go_of(what):
    """Make every player let go of what it has open there.

    A player that has a file open holds it. Under macOS and Linux a held
    file can still be moved, under Windows it cannot -- which is why the
    two moves below were green on two systems and red on the third, with
    nothing to show for it but a permission error out of shutil.move.
    So nothing is moved here before the players have let go of it.

    Measured with lsof on 28.8.2026: at the second move the process has
    exactly one file of the folder open, the prepared overall mix, and
    it is the cut player on the Resolve sheet that holds it -- the
    preview player had gone over to the raw recording a step earlier and
    let the mix go with it. Asked of every player under every window all
    the same, and by what it has open rather than by which player it is,
    so that a second holder does not go unnoticed. Returns what was let
    go.

    A player that never started is not stopped. What lies behind stop()
    is built on first use, and building it waits for a lock another
    player holds while it is starting up -- the window then never comes
    back. playbackState only reads what is already noted.
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

    gui() comes back with the window still standing, so the folder used
    to go while players still held files in it. Let go, close, delete --
    in that order. And no ignore_errors: it would swallow the one thing
    that can go wrong here, a folder that stays because something still
    holds it.

    Letting go returns before the file is free. The media backend closes
    the handle in a thread of its own, so setSource() comes back while
    the system still has the file open. Under macOS and Linux that never
    shows, because a held file can be deleted there anyway. On Windows
    it does: measured on the build machine, five of these tests left
    four to seven files behind on the first attempt. So what is waited
    for is the handle, not a number of milliseconds -- delete, run the
    event loop, delete again, up to ten seconds. Ten because it is far
    above a thread closing a file, and still short enough that a folder
    which will never go does not hold the suite.

    What is left after that is a finding, not a failure: it is named,
    with how long it was waited on, and it does not turn the test red.
    A test that is red on one system on every run gets switched off
    rather than looked at, and then it says nothing at all.
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
    check("his camera can be clicked again", pick_camera(CAM_TYPED))
    ask_again()
    got = playing()
    check("without a prepared track it plays the raw recording",
          got == TYPED, str(got))
    check("and the tick says it is the raw one, and quieter",
          tick().toolTip() == says_raw(got), repr(tick().toolTip()))


def take_the_folder_away():
    """The whole folder of prepared tracks, out of every reach.

    Out of the temporary folder altogether: the program looks in the
    output folder, in the folder the material comes from, and one level
    below that, so moving it aside within any of them would still find
    it.
    """
    print("  let go of %s"
          % (", ".join(let_go_of(done_folder)) or "nothing"))
    shutil.move(done_folder, os.path.join(aside, "auphonic-tracks"))


def nothing_look():
    """No prepared folder at all: silence for the wide shot."""
    check("the wide shot can be clicked once more", pick_camera(CAM_WIDE))
    ask_again()
    check("with nothing prepared the wide shot gets no audio",
          playing() is None, str(playing()))
    check("his camera can be clicked once more", pick_camera(CAM_TYPED))
    ask_again()
    check("but he still gets his raw recording", playing() == TYPED,
          str(playing()))


plan = [open_project, wait_for_sheets, put_them_on_cameras, type_one_name,
        typed_name_look, guessed_name_look, wide_look, cut_look,
        take_his_track_away, raw_look, take_the_folder_away, nothing_look]


def stop_now():
    print("\n%s" % ("ALL OK" if not error else "FAIL: " + ", ".join(error)))
    done[0] = True
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
    QtCore.QTimer.singleShot(250 if answer == AGAIN else 500, step)


QtCore.QTimer.singleShot(300, step)
# A window that never gets there must not hold the suite -- there is no
# timeout(1) on this machine -- and must not pass either.
QtCore.QTimer.singleShot(240000, app.quit)
vpm.gui()
if not done[0]:
    print("  the window never got as far as the checks   FAIL")
    error.append("no answer")
clean_up(aside)
sys.exit(1 if error else 0)
