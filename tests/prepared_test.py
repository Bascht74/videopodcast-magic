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
it by its timecode. Until 30.8.2026 it was asked through the handover
file a run leaves behind, and this test put one in the result folder to
open that door. It is shut. A handover lying about may be days old --
another time window, another measurement -- and the cut built out of it
looks exactly like a fresh one; Sebastian was offered a Resolve project
out of a file four days old, with the sound under the wrong pictures.
Since then the window builds its cut only out of what it worked out
itself.

So the cut is waited for here rather than laid out: the speakers are
measured in the window, by its own button, and what the player then has
is read off it. And a handover of a stranger lies in the result folder
the whole time, naming three cameras that are not these and putting
them 600 s off. What happens to it is a check of its own -- without
that, the rule could quietly fall back tomorrow and every other line
here would stay green.

The cameras are the shared interview fixture, copied into a folder of
their own and stamped with one clock -- see CLOCK below for why. The
prepared tracks are silent one-second WAVs written here: what is
checked is which file is chosen, not what is on it. The two recordings
are written here as well, and they do have to hold something, since
30.8.2026: the window measures who speaks when out of them, and every
recording in the fixture is one unbroken sine tone with nobody in it.
See voice_wav.
"""
import math
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

# Three cameras out of the shared fixture, and two recordings written
# here under the names the fixture uses. The first speaker is typed in,
# the second is left to the guess the file name gives -- that is the
# whole difference between the two, and the prepared track has to be
# found either way.
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
CLOCK = 19 * 3600 + 4 * 60             # 19:04:00:00, the material
# The tracks that come back from auphonic.com are trimmed to the time
# window that was asked for, so they begin later than the material they
# were made from. Half a minute later here, and that half minute is the
# point of the check on the cut player: it has to place the mix by the
# mix's own timecode against programme time, and programme time begins
# where the earliest recording begins. Were everything on one clock the
# shift would be nought -- and nought is also what a player shows that
# places nothing at all, so the check would prove nothing.
MIX_LEAD = 30.0
MIX_CLOCK = CLOCK + MIX_LEAD           # 19:04:30:00, the prepared tracks
TAIL = "19-04-30-00"                   # the timecode in the file name
WINDOW = (1400, 950)
# Who has the turn when, in the two recordings written below. Two
# minutes, six turns of twenty seconds, the length of the cameras. The
# window measures this for itself, so it is the only place where it is
# written down -- nothing hands the answer to the program.
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
missing = [n for n in (CAM_TYPED, CAM_GUESSED, CAM_WIDE)
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
# The room between the turns, and it is seven blocks and not one. Why
# is in voice_wav: 46 to 34 dB under the speech, and never twice the
# same in a row.
FLOOR = [one_second(0.002 * (1.35 ** k)) for k in range(7)]


def voice_wav(path, turns, seconds=LENGTH):
    """One person's recording: loud on their turn, the room between.

    Since 30.8.2026 the window works out who speaks when by measuring
    the recordings, and there is nobody to find in the shared fixture:
    every recording in it is one unbroken sine tone, and a tone that
    never stops is its own noise floor. So the two recordings are
    written here, out of second-long blocks laid end to end.

    Two things about them are not decoration, and both were measured on
    30.8.2026 against the program's own speakers_from_tracks:

    A block of digital silence between the turns finds nobody. Blocks
    at exactly nought are left out of the noise floor, so the floor
    becomes the speech itself and nothing stands 10 dB over it.

    A quiet block that is always the same finds nobody either, and that
    one is less obvious. The bleed between two microphones is measured
    where one person speaks alone -- the level of the other track
    against theirs -- and where that ratio never varies it is exact:
    the subtraction leaves nought behind, and nought is the case
    above. So the room here breathes, seven levels in turn between 46
    and 34 dB under the speech. Then the ratio has a spread, the
    subtraction leaves a floor standing, and both people come out with
    their turns to the tenth of a second.
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
        # Written, not copied: somebody has to be audible in these.
        voice_wav(copy, TURNS[name])

FINAL = {n: os.path.join(done_folder, "final_%s_%s.wav" % (n, TAIL))
         for n in (TYPED_NAME, GUESSED_NAME, "Full-Mix")}
for path in FINAL.values():
    silent_wav(path, clock=MIX_CLOCK)
# What else comes back from a run and must never be played: the raw
# return, which is neither trimmed nor placed on the axis, the assembled
# master and the statistics beside it. They are in the folder rather
# than described in a comment -- a rule nothing tries to break is not
# checked.
for name in ("%s.wav" % TYPED_NAME, "Full-Mix.wav", "Interview_master.wav"):
    silent_wav(os.path.join(done_folder, name), clock=MIX_CLOCK)
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

# The bait, and it stays there to the end. A handover file of the right
# format under the right name -- "<production>_resolve.json" in the
# result folder -- written by somebody else, at some other time, off
# some other measurement. Until 30.8.2026 the window read whatever
# handover it found there, and that is exactly how Sebastian came to be
# shown a cut out of a four-day-old file. Since then it reads only what
# its own run wrote, so this file must have no effect at all.
#
# It is built to be *usable*, which took two goes and is the point of
# this comment. A file that the window would throw out anyway proves
# nothing: the first one here began ten minutes before the material,
# and the old program did not build a wrong cut out of it, it built
# none, because the In point of this window then fell past the end of
# that programme. So this one covers the window: it begins two minutes
# early and runs ten minutes, and the old program does make a cut of
# it.
#
# What it is wrong about is the material. It names three cameras that
# are not the three lying here -- files of a run whose folder is long
# gone -- and it puts them 600 s off programme time. That is what the
# counter-check reads, and it has to be that: the zero point and the
# shift of the mix do *not* tell the two apart, because the window
# trims every handover to its own In point and thereby pulls a strange
# one onto the same zero. Which cameras the cut runs on, and where they
# sit, nothing pulls straight.
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

# What the window has to arrive at by itself. Programme time starts
# where the earliest recording starts, and everything here carries the
# one clock, so that is CLOCK: the cameras then sit at nought, and the
# mix at the half minute it was trimmed to.
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


def cut_places():
    """Where the cut player puts things: zero point and camera shifts.

    The zero point is the clock time programme time nought lies at, and
    the shift of each camera is how far its file sits from that. Both
    are read off the player, because both are what a wrong handover
    would move: it brings its own zero, and every camera hangs off it.
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


def measure_note():
    """The sentence beside the measure button, for a FAIL line.

    Nothing is decided by it. It is the only place the window says why
    a measurement brought nothing, and a failure here is otherwise a
    cut that never appears and no reason anywhere.
    """
    said = (vpm.T('Measure speakers now'), vpm.T('measuring ...'))
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip() not in said or w.parentWidget() is None:
            continue
        return " / ".join(
            [x.text().strip() for x
             in w.parentWidget().findChildren(QtWidgets.QLabel)
             if x.text().strip()]) or "nothing said"
    return "no measure button"


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


def start_measuring():
    """Have the window work out who speaks when, here and now.

    This is the step that replaces the handover file. Nothing on disk
    tells the window where the speakers are any more, so it is asked
    the way a person asks: the button under the preview that measures
    the tracks. It runs in a thread of its own; what comes of it is
    waited for below.
    """
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip() == vpm.T('Measure speakers now'):
            w.click()
            app.processEvents()
            check("the speaker measurement can be started", True)
            return
    check("the speaker measurement can be started", False,
          "no button of that name")
    return STOP


def cut_look():
    """The cut on the Resolve sheet runs on the prepared mix too.

    It is not read from a file. The window measured the speakers a step
    ago, in a thread, and works the cut out of that together with the
    assignment after a timer of its own -- so what is waited for is the
    cut, never a number of seconds.

    A cut is there when the sound under it is a track of its own. With
    nothing to cut the player shows the one camera nobody is assigned
    to, from beginning to end, with that same camera's own sound under
    it -- and that state is what this check used to mistake for an
    answer.

    Not "more than one shot", and not "more than one camera" either.
    Both were tried on 30.8.2026 and both stop too early: a cut off the
    wrong material can be a single shot on a single camera, and this
    line then blames the waiting and gives up before the lines that say
    what is really wrong. Sound of its own is what tells a cut from no
    cut; whether it is the right cut is the next step's question.
    """
    shots, files = cut_shots(), cut_files()
    name, _off = cut_audio()
    there = bool(shots) and bool(name) and name not in [
        os.path.basename(x) for x in files]
    if not there and cut_waited[0] < 200:
        cut_waited[0] += 1
        return AGAIN
    check("the window worked a cut out on its own, from no file", there,
          "%d shots on %d cameras (%s), sound %s, after %d rounds -- %s"
          % (len(shots), len(cut_cameras()),
             ", ".join(cut_cameras()) or "none", name, cut_waited[0],
             measure_note()))
    if not there:
        return STOP
    name, off = cut_audio()
    check("the cut player was given an audio file", name is not None,
          str(name))
    check("and it is the prepared overall mix",
          name == os.path.basename(FINAL["Full-Mix"]), str(name))
    check("placed by its own timecode against programme time",
          off is not None and abs(off - OWN_MIX_SHIFT) < 0.001,
          "%s, wanted %s" % (off, OWN_MIX_SHIFT))


def bait_look():
    """The strange handover lies right there, and nothing reads it.

    Without this the rule could fall back tomorrow and every other line
    here would stay green: there would be a cut, the prepared mix would
    be under it, and only the material would be somebody else's -- the
    fault Sebastian was shown, exactly.

    So the cut is held against the material rather than against the
    clock: which camera files it runs on, and where they sit. The bait
    names three cameras of an older run, in a folder that is not here,
    600 s off programme time. Neither can be mistaken for what lies in
    this project.
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
        typed_name_look, guessed_name_look, wide_look, start_measuring,
        cut_look, bait_look, take_his_track_away, raw_look,
        take_the_folder_away, nothing_look]


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
