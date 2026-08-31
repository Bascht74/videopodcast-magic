# -*- coding: utf-8 -*-
"""Does the sound in the cut player belong to the picture on screen?

Everything else about the cut is checked somewhere: that the moment
survives the nine roads onto one picture, that the player is handed the
prepared mix, that the offset is taken and not replaced by zero. What
nobody asked until now is the question a person asks while watching:
the picture shows a moment, the sound carries a moment, and are they
the same one? A cut whose sound sits a few seconds off the picture
looks right in every number and is unusable.

The player says it itself. With VPM_PLAYER_LOG set it prints, at every
change of picture, six numbers: programme time, which camera, where in
the picture file it is putting the playhead, that file's offset, where
in the sound file, and its offset. This test sets the variable, opens a
window on real material, moves the player about, and holds the numbers
against the clock the material carries.

The clock is what makes it a check rather than a restatement. Each
camera of the fixture carries its own timecode, so a position in the
picture file plus that file's timecode is a wall clock moment; the
position in the sound file plus the sound file's timecode is a second
one; and the start of the programme plus programme time is a third.
Three roads, measured with ffprobe here and not taken from the player,
and all three have to arrive at the same instant.

Where the cut comes from is the window's own arithmetic, because that
is where a person's comes from too. Until 30.8.2026 the window would
pick up any handover file lying in the result folder, and one of them
was four days old: another time window, another measurement, and the
sound sat off the picture. Since then it uses only what its own run
wrote, and where there is nothing it works the cut out of what it
knows -- the separation, who sits in front of which camera, and the
timecodes of the files. So this test hands the window a project and no
run: the separation travels in the project the way a saved one does,
the cameras carry their timecodes, and the cut is the window's answer.
A handover file from an older measurement lies in the result folder on
purpose, with a start an hour away, and one check is that programme
time did not land on it.

The cases, in two windows built offscreen:

  * every line the player prints, at a standstill and while running
  * after a jump into the middle of the cut, where it went wrong
  * at a camera change: the picture file changes, the sound runs on
  * with the offsets deliberately reversed, which has to turn red
  * a fresh cut handed over under a viewer, running and standing
  * with a time window set, where programme time starts later

The reversed run is the point of the whole file. Two numbers that come
out of one subtraction always agree with each other, so a check that
only holds them together holds nothing. Reversing the sign of every
offset is the fault that was suspected, and the same checks over the
same player have to see it.

What the player prints on is a condition and not a moment in time:
the jump prints inside itself, unless the cut it is holding does not
reach that far. While the window rebuilds its preview the player is
handed an empty cut, and a jump landing in that gap is answered with
silence. Every jump here therefore asks again until a line comes out,
and two steps make that gap on purpose and then wait it out -- without
them the waiting would be a story rather than a measurement.

A step is opened before the player is asked for anything and closed
again the moment it has answered, because the window prints too: every
rebuild of its preview hands the player a cut, and the player says so
at the start of the programme with the honest offsets in it. Charged
to whichever step happened to be left open, that line made the
reversed run read honest and would make the empty cut read noisy.
Between two steps it belongs to nobody, and the reversed run says how
many there were. And where the window did it in the middle of the one
step that has to run in real time, that step is begun again rather
than waited out: a player put back to the start will not reach a
moment it has already left, however long it is given.

A fresh cut arrives while somebody is watching, and that is the last
four steps. The window works its preview out again whenever a fact
about a file comes in and hands the player the answer; until 31.8.2026
that call took the viewer with it, stopping the player and winding it
back to the In point. It happened once in every run measured here, so
whoever pressed play soon after opening a project was put back where
they started. What the viewer keeps is the place and the playing. What
follows the fresh cut is the picture: where the new cut names another
camera on that second, that camera has to come up, and the short break
in the picture is the price of it. So a cut is handed over four times
-- to a player that is running, to one that stands, to one whose place
lies past the end of the fresh cut, and to one that finds another
camera on the second in view. The clock is read either side of the
handover in one breath, with no turn of the event loop between: the
player reads it at the first line of the handover and puts it back at
the last, so the two numbers are one call apart and nothing else.

And the numbers do not travel in the log. The window's media backend
writes to the error output while it opens a file, both go into one
pipe, and a fragment of it that ends without a newline takes the line
behind it along. The line is then printed, correct, and unreadable,
and whoever reads the log believes the player said nothing. That cost
three build machines a red run over a line that was there. So the
child reads its own lines as it prints them and leaves the numbers in
a file; the log is for people. One step writes such a fragment on
purpose, and the checks on it are what hold that arrangement in place.

Where this check stops: the timecode of a file is the ground it
stands on, so a timecode read wrongly in the first place would move
all three roads together and go unseen here. That question belongs to
time_all_ways_agree_test.py, which holds one moment against nine ways of
reaching a picture.
"""
import os
import sys
import json
import re
import shutil
import struct
import subprocess
import tempfile
import time
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
sys.path.insert(0, HERE)

# Three cameras out of the shared fixture, each with a timecode of its
# own -- 18:55:00:00, 18:55:04:00 and 18:55:17:12 -- which is the whole
# reason they are used here: three cameras on one clock would let a
# reversed sign pass on two of them.
WIDE = "Totale_08141855_C003.mov"
HOST = "Moderatoren_08141855_C005.mov"
GUEST = "Kandidat_08141858_C009.mov"
# What each one is called on the cut is not settled here: the window
# gives every camera a track name of its own, and the timecodes below
# are measured under those names, off the very files it opened.
CAMERAS = (WIDE, HOST, GUEST)

# Where programme time starts on the wall clock: half a minute after
# the earliest camera. Every offset is then a number and not a zero --
# a zero cannot be reversed, and a check that lands on one checks
# nothing -- and every position stays inside the 120 s the files run.
CUT_START = 18 * 3600 + 55 * 60 + 30.0
CUT_LENGTH = 60.0
# The prepared overall mix starts ten seconds before the programme.
MIX_START = CUT_START - 10.0
MIX_LENGTH = 90.0
TAIL = "18-55-20-00"                  # the timecode in its file name
# Who spoke when, in the time of the one recording all of them are on.
# This is what a separation leaves behind and what a saved project
# carries, and it is the whole of what the window needs to work a cut
# out: ten seconds each, turn and turn about, so the cut changes camera
# five times and every shot is long enough to jump into.
SEPARATION = (("SPEAKER_00", ((0.0, 10.0), (20.0, 30.0), (40.0, 50.0))),
              ("SPEAKER_01", ((10.0, 20.0), (30.0, 40.0), (50.0, 60.0))))
NAMED = {"SPEAKER_00": "Host", "SPEAKER_01": "Guest"}
# An older handover in the result folder, an hour away from the truth.
# It must not be read: that is the fault of 30.8.2026, kept here as a
# counter-check rather than as the source of the cut.
STALE_AWAY = 3600.0
# How far the window case pushes the start of the programme.
WINDOW_IN = 20.0
WINDOW = (1400, 950)
CASES = ("plain", "window")

# A child that has said nothing for this long has stopped, not slowed.
PATIENCE = 300
# How often one step may ask again before it gives up, at 200 ms each.
# Eight seconds for a window to finish one rebuild: it takes a single
# turn of the event loop on the machine this was written on, and a
# build machine three times as slow is nowhere near forty times.
TRIES = 40
# A player that says it is playing and whose clock has not moved for
# this many polls has stopped, not slowed. The clock is a stopwatch on
# the wall, so it goes on rising on the busiest machine as long as
# anything is playing at all -- which is why standstill is worth giving
# up on and a deadline is not.
STILL = 40
# How often the run into the camera change may be begun again. The
# window hands the player a fresh cut every time it recomputes its
# preview, and that pauses the player and puts it at the start of the
# programme. It happened once in every run measured here, beside eight
# neighbours and alone alike, and where it landed inside the second
# being played the old step waited sixteen seconds and reported a
# player that never ran.
BEGUN_AGAIN = 8
# How far the player's clock has to have risen before it counts as
# running. A poll is 200 ms apart, and the clock is a stopwatch on the
# wall, so a player that is running at all passes this on the first
# one; a tenth of a poll is far enough below that to survive a machine
# three times slower, and far enough above nought to mean something.
MOVED = 0.02
DUMP = bool(os.environ.get("VPM_SOUND_PICTURE_DUMP"))

# The line the player prints. Written by print() and not through the
# catalogue, so it reads the same in every language.
SAID = re.compile(
    r"^\s*player: programme\s+(-?[0-9.]+)\s+picture\s+(.*?)\s+at\s+"
    r"(-?[0-9.]+)\s+\(offset\s+(-?[0-9.]+)\)\s+sound\s+(-?[0-9.]+)\s+"
    r"\(offset\s+(-?[0-9.]+)\)\s*$")
MARK = "SOUNDPICTURE-STEP "
REPORT = "SOUNDPICTURE "
OUT = "VPM_SOUND_PICTURE_OUT"
# What a media backend says when it opens a file, and the thing that
# matters about it: no newline at the end. It goes to the error output,
# which shares one pipe with the log, so it takes the line printed next
# along with it. One step below writes this on purpose.
NOISE = b"[mov,mp4 @ 0x7f] Could not open media. FFmpeg error: "


def numbers_of(got):
    """The six numbers of one player line."""
    return {"t": float(got.group(1)), "who": got.group(2),
            "picture": float(got.group(3)),
            "picture_offset": float(got.group(4)),
            "sound": float(got.group(5)),
            "sound_offset": float(got.group(6))}


# --------------------------------------------------------------- material
def timecode_in(path, seconds):
    """Put a BWF marker into a WAV that has none.

    The bext chunk goes in front of the ones already there and the RIFF
    length is corrected -- what a recorder writes, and where the
    program looks for the start time of a recording.
    """
    raw = open(path, "rb").read()
    if raw[:4] != b"RIFF" or raw[8:12] != b"WAVE":
        raise ValueError("%s is no RIFF/WAVE file" % path)
    body = bytearray(602)              # bext version 0, without history
    struct.pack_into("<Q", body, 338, int(round(seconds * 48000)))
    out = bytearray(raw[:12] + b"bext" + struct.pack("<I", len(body))
                    + bytes(body) + raw[12:])
    struct.pack_into("<I", out, 4, len(out) - 8)
    with open(path, "wb") as f:
        f.write(bytes(out))


def silent_wav(path, seconds, start):
    """A real WAV on the clock: it is placed, not listened to."""
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(48000)
        f.writeframes(b"\x00\x00" * int(48000 * seconds))
    timecode_in(path, start)


def own_project(case, vpm, fixture):
    """Material and project for one case, and no run.

    The cameras are copied: opening a project moves the project file
    into its output folder and would leave the next test with nothing
    to open. Nothing here pretends a run has happened. What the window
    is given is what a person has before the first run: three cameras
    with their timecodes, one recording everybody is on with a
    separation stored beside it, who sits in front of which camera, and
    the prepared overall mix in the folder a run puts it in. The cut is
    then the window's own arithmetic.

    The one file that does claim a run is the handover in the result
    folder, and it is wrong on purpose -- an hour away, one camera, one
    speaker. Since 30.8.2026 the window does not touch a handover its
    own run did not write, and that file is how this test says so.

    Returns (project file, out folder, what was measured about the
    material).
    """
    source = fixture("interview")
    own = tempfile.mkdtemp(prefix="vpm_soundpicture_")
    result = os.path.join(own, "Result")
    done = os.path.join(result, "auphonic-tracks")
    os.makedirs(done)
    here = {}
    for name in CAMERAS:
        copy = os.path.join(own, name)
        # Copied and not linked to: three megabytes each, and a link is
        # a privilege on Windows rather than a file operation.
        shutil.copyfile(os.path.join(source, name), copy)
        here[name] = copy
    # The frame rate is measured, and every timecode here is read at
    # it, because the frames of a timecode are frames: read at 30 what
    # was shot at 25, 18:55:17:12 lands 80 ms out. That is two frames,
    # and it is exactly the size of error this test is for. It also
    # sets how close the three roads have to come: one frame.
    fps = float(vpm.video_facts(here[WIDE]).get("fps") or 30.0)
    mix = os.path.join(done, "final_Full-Mix_%s.wav" % TAIL)
    silent_wav(mix, MIX_LENGTH, MIX_START)
    # The one recording everybody is on. Its timecode is what tells the
    # window where programme time starts: the speech was measured on
    # this file, so the zero point of the segments is its beginning.
    voices = os.path.join(own, "Everyone_0001.wav")
    silent_wav(voices, CUT_LENGTH, CUT_START)

    project = os.path.join(own, "videopodcast-magic_Sound_picture.json")
    with open(project, "w", encoding="utf-8") as f:
        json.dump({
            "format": vpm.FILE_FORMAT, "version": "test", "timeline": [],
            "call": [], "preset": "", "production": "Sound picture",
            # Several cameras, or there is no camera cut to look at.
            "multitrack": True, "out_folder": result,
            "assignment": {
                # "several speakers" on that recording, which is what
                # puts the separated voices under it as rows of their
                # own. Without that answer the window shows none, and
                # then nobody is in front of a camera.
                "several:" + voices: True,
                "voice:SPEAKER_00": HOST,
                "voice:SPEAKER_01": GUEST,
                # Said out loud rather than derived, so the wide shot
                # is the one meant and not whichever camera happens to
                # have nobody in front of it.
                "kind:" + here[WIDE]: vpm.TYPE_WIDE,
            },
            # The separation as a saved project carries it: raw, in the
            # time of its own file, with the fingerprint that says it
            # still belongs to it.
            "speakers": vpm.speakers_for_project(
                voices, [(label, [tuple(x) for x in parts])
                         for label, parts in SEPARATION],
                len(SEPARATION), dict(NAMED)),
            "speakers_source": voices,
            "speakers_local": True,
            # The In point travels in the project file. There is no
            # field to type it into -- the window takes it off the
            # picture -- so this is the door a test has.
            "in_point": vpm.as_relative_time(WINDOW_IN)
                        if case == "window" else "",
            "out_point": "",
            "files": [{"path": here[n], "kind": "video"}
                      for n in CAMERAS]
                     + [{"path": voices, "kind": "audio"}],
        }, f, ensure_ascii=False, indent=1)

    # The handover of an older run, left lying in the result folder. An
    # hour off, one camera, one speaker -- so that a window reading it
    # cannot be mistaken for a window that did the arithmetic itself.
    stale = os.path.join(result, "Sound_picture_resolve.json")
    with open(stale, "w", encoding="utf-8") as f:
        json.dump({
            "format": vpm.FILE_FORMAT, "created_by": "an earlier run",
            "production": "Sound picture", "fps": int(round(fps)),
            "fps_measured": fps, "drop_frame": False,
            "width": 320, "height": 180,
            "start_tc": vpm.timecode_string(CUT_START - STALE_AWAY, fps),
            "start_s": CUT_START - STALE_AWAY, "length_s": CUT_LENGTH,
            "lufs": -16.0, "intro": None, "outro": None,
            "cameras": [
                {"file": here[WIDE], "source": here[WIDE],
                 "camera": WIDE, "track": "Wide", "speakers": ["Nobody"],
                 "audio_tracks": ["Full-Mix"], "offset": 0.0,
                 "duration": CUT_LENGTH, "wide": False}],
            "cut": [],
            "speakers": [{"name": "Nobody",
                          "sections": [[0.0, CUT_LENGTH]]}],
            "audio_files": {}, "words": [],
        }, f, ensure_ascii=False, indent=1)
    # "tc" and "files" stay empty until the player says which files it
    # opened and what it calls them; they are filled in wait_for_cut.
    return project, result, {"fps": fps, "tc": {}, "files": {},
                             "mix": mix, "mix_tc": MIX_START,
                             "voices": voices, "stale": stale,
                             "stale_start": CUT_START - STALE_AWAY}


# ------------------------------------------------------------- the child
def look(case):
    """Build one window, move the player, and say what it printed."""
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ["VPM_SILENT"] = "1"
    os.environ["VPM_NO_UPDATE_CHECK"] = "1"
    os.environ["VPM_NO_SPEAKER_SPLIT"] = "1"
    os.environ["VPM_PLAYER_LOG"] = "1"
    import importlib.util
    from PySide6 import QtCore, QtWidgets
    from fixture_root import fixture

    app = QtWidgets.QApplication(sys.argv[:1])
    spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
    vpm = importlib.util.module_from_spec(spec)
    sys.modules["vpm"] = vpm
    spec.loader.exec_module(vpm)
    vpm.set_language("en")
    # Nothing may reach the network or the keychain: what is wanted is
    # the window, not a run.
    vpm.list_presets = lambda key: []
    vpm.load_api_key = lambda: ""
    vpm.update_offer = lambda *a, **k: None

    project, _result, measured = own_project(case, vpm, fixture)
    QtWidgets.QFileDialog.getOpenFileName = staticmethod(
        lambda *a, **k: (project, ""))
    # Nothing may sit and wait for a click.
    QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
    QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
    _show = QtWidgets.QWidget.show

    def offstage(self):
        self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
        _show(self)

    QtWidgets.QWidget.show = offstage
    QtWidgets.QDialog.show = offstage

    def window_of():
        for x in app.topLevelWidgets():
            if "Video Podcast Magic" in x.windowTitle():
                return x

    def cut_player():
        """The player that runs the camera cut.

        Found by what it must have to do that: an audio file of its own
        and a shift between programme time and that file. The preview
        player has no such shift -- it follows the picture -- so the
        two cannot be confused.
        """
        window = window_of()
        if window is None:
            return None
        for w in window.findChildren(QtWidgets.QWidget):
            if hasattr(w, "audio_offset") and hasattr(w, "audio"):
                return w
        return None

    seen = {"now": None, "lines": {}, "total": 0, "loose": 0}

    class Tee(object):
        """Pass everything on, and keep the player's lines going past.

        The player prints inside the jump, so this process can read its
        own answer the moment it asked for one -- both whether a line
        came at all, which is what the waiting hangs on, and the six
        numbers in it, which are the measurement.

        Kept here rather than read back out of the log because the log
        is not a channel a measurement can travel through: the media
        backend writes to the error output at the same time, the two
        arrive in one pipe, and a fragment of its chatter that ends
        without a newline takes the next line with it. Reproduced with
        four lines of Python. The line is then printed, correct, and
        unreadable -- and the reader is left thinking the player said
        nothing.
        """

        def __init__(self, stream):
            self.stream, self.rest = stream, ""

        def write(self, text):
            self.stream.write(text)
            self.rest += text
            while "\n" in self.rest:
                row, self.rest = self.rest.split("\n", 1)
                got = SAID.match(row)
                if not got:
                    continue
                # Counted whether or not a step is running, so that the
                # log can be held against it afterwards.
                seen["total"] += 1
                if seen["now"]:
                    seen["lines"][seen["now"]].append(numbers_of(got))
                else:
                    # Nobody asked for this one. Counted rather than
                    # dropped, so a run that goes wrong can say how busy
                    # the window was laying its own cut over the
                    # player's while nothing was being measured.
                    seen["loose"] += 1
            return len(text)

        def flush(self):
            self.stream.flush()

        def isatty(self):
            return False

        def __getattr__(self, name):
            return getattr(self.stream, name)

    sys.stdout = Tee(sys.stdout)

    def step(name):
        """Begin a step: the lines from here on belong to it.

        The mark goes into the log as well, so a person reading the log
        can still see where they are. Nothing reads it back.
        """
        seen["now"] = name
        seen["lines"][name] = []
        print(MARK + name)
        sys.stdout.flush()

    def close():
        """End the step: a line that comes now belongs to no step.

        The window hands the player a cut every time it rebuilds its
        preview, and the player answers that at the start of the
        programme with the honest offsets in it. Nobody asked for that
        line, so no step may be charged with it. Left open, the last
        reversed jump collected one and the counter-check then read the
        honest numbers and called itself toothless -- red beside eight
        neighbours on this Mac, twice out of two, and green alone.
        """
        seen["now"] = None

    def said_in(name):
        """The player lines of that step, as this process saw them."""
        return seen["lines"].get(name) or []

    result = {"case": case, "measured": measured, "start_s": CUT_START,
              "window_in": WINDOW_IN if case == "window" else 0.0}
    state = {"waited": 0, "played": 0, "ready": 0, "from": 0.0,
             "turned": 0, "seen_at": 0.0, "still": 0, "again": 0,
             "went": None, "quiet": 0, "afresh": 0}
    keep = {}
    # What each of the four handovers below left behind. Handed up as
    # one piece so that a run which never got that far says so with an
    # empty box rather than with numbers nobody measured.
    handover = {}
    result["handover"] = handover

    def cut_ready():
        p = cut_player()
        if p is None or not getattr(p, "cut", None):
            return None
        if len(set(w for _a, _b, w in p.cut)) < 2:
            return None
        if not p.audio.source().toLocalFile():
            return None
        return p

    def spots(p):
        """One point in a shot of each camera, three at the most.

        Read off the cut the window worked out rather than written down
        here: what the cut looks like is the cut's business, and a test
        that assumed it would be checking its own arithmetic.
        """
        out, seen = [], set()
        for a, b, who in p.cut:
            if who in seen or b - a < 1.0:
                continue
            seen.add(who)
            out.append(round((a + b) / 2.0, 3))
        return out[:3]

    def edge(p):
        """The first cut where the camera really changes."""
        for i in range(len(p.cut) - 1):
            if p.cut[i][2] != p.cut[i + 1][2]:
                return i
        return None

    def covers(p, t):
        """Report whether the player's cut holds that moment right now.

        This is the whole condition for a line: the jump asks the
        player which shot the moment belongs to, and prints inside the
        answer. Where no shot holds it, the jump returns without a
        word. That is not a rare state -- while the window rebuilds its
        preview the player is handed an empty cut, and a test that read
        its points off one cut and jumped into another asks for a line
        that cannot come. Seen on slower machines: of four jumps in one
        window, one came back silent while the same run was green on a
        quick one. The last two steps make that state on purpose.
        """
        return p is not None and any(a <= t < b for a, b, _w in p.cut)

    def go_to(tag, t, noise=False, on_retry=None):
        """One step: jump to that moment and see a line come out of it.

        Waits for the state that makes a line rather than for a length
        of time, and asks again where the player is between cuts. Where
        it never gets one it says what the player was holding instead,
        which is the difference between "the program went quiet" and
        "the window was in the middle of something".
        """
        tries = [0]
        # Every shape the player's cut took while this step waited. One
        # of them means it stood still; several mean the window was
        # working and only needed longer. That is the difference
        # between "wait longer" and "it is never coming", and it has to
        # be in the line that reports the failure.
        shapes = []

        def once():
            p = cut_ready()
            shape = [[a, b, w] for a, b, w in (p.cut if p else [])]
            if not shapes or shapes[-1] != shape:
                shapes.append(shape)
            if covers(p, t):
                step(tag)
                if noise:
                    os.write(2, NOISE)
                p.jump(t)
                sys.stdout.flush()
                # The jump printed inside itself or not at all, so the
                # step is over here: what the window prints next is not
                # this step's answer.
                close()
                if said_in(tag):
                    result.setdefault("tries", {})[tag] = tries[0]
                    return
            if tries[0] < TRIES:
                tries[0] += 1
                if on_retry is not None and tries[0] == 1:
                    on_retry()
                return "again"
            result.setdefault("silent", []).append(
                {"step": tag, "covered": covers(p, t),
                 "waited_ms": tries[0] * 200, "cuts_seen": len(shapes),
                 "moved": len(shapes) > 1, "last_cut": shapes[-1][:6]})
        return once

    plan = []

    def open_project():
        window = window_of()
        window.show()
        window.resize(*WINDOW)
        app.processEvents()
        for b in window.findChildren(QtWidgets.QPushButton):
            if b.text().strip().startswith(vpm.T('Open project ...')[:8]):
                b.click()
                break

    def wait_for_cut():
        """Wait for the cut, not for the clock.

        The window works it out itself, out of the separation in the
        project and the timecodes of the files, once every file has
        been looked at. What must be there is known before the window
        opens: a cut over at least two cameras, with a sound file under
        it.
        """
        p = cut_ready()
        if p is None and state["waited"] < 200:
            state["waited"] += 1
            return "again"
        if p is None:
            result["error"] = "no cut came up"
            return "stop"
        result["cut"] = [[a, b, w] for a, b, w in p.cut]
        # The timecodes, measured now and off the very files the player
        # opened, under the names it calls them by. Written down here
        # rather than beside the material because what a camera is
        # called on the cut is the window's answer and not this test's:
        # a timecode filed under a name nobody uses checks nothing.
        measured["files"] = {t: os.path.basename(x)
                             for t, x in p.files.items()}
        measured["tc"] = {}
        for track, path in p.files.items():
            stamp = vpm.file_timecode(path, measured["fps"])
            if stamp is not None:
                measured["tc"][track] = float(stamp)
        # What the player was holding, kept as it is: the last two steps
        # take it away and put it back to show that the waiting works.
        keep.update(cut=[(a, b, w) for a, b, w in p.cut],
                    files=dict(p.files), offset=dict(p.offset),
                    audio=p.audio.source().toLocalFile(),
                    audio_offset=p.audio_offset, begins=p.begins,
                    until=p.until, tc0=p.tc0)
        result["tc0"] = p.tc0
        result["begins"], result["until"] = p.begins, p.until
        result["audio"] = os.path.basename(
            p.audio.source().toLocalFile())
        result["offset"] = dict(p.offset)
        result["audio_offset"] = p.audio_offset
        result["spots"] = spots(p)
        result["edge"] = edge(p)
        # One step per jump, built now that the cut is known. Each is a
        # step of its own so that the event loop turns between them:
        # two jumps in one breath give the window no chance to finish
        # whatever it was doing, and the second lands in the gap.
        for t in result["spots"]:
            plan.append(go_to("jump %.3f" % t, t))
        if result["edge"] is None:
            result["error"] = "the cut never changes camera"
            return
        b = result["cut"][result["edge"]][1]
        for t in (round(b - 0.25, 3), round(b + 0.25, 3)):
            plan.append(go_to("edge %.3f" % t, t))
        if case == "plain":
            # The same jump again, with the backend chattering into the
            # log at the moment the player prints. This is the state
            # that called a green run red on three build machines, and
            # it has to pass now: the numbers no longer travel that way.
            plan.append(go_to("chatter %.3f" % result["spots"][0],
                              result["spots"][0], noise=True))
        plan.extend(after_the_edge)

    def run_at_the_edge(p):
        """Put the player just before the change and set it going.

        Called again where the window took the cut back: handing the
        player a cut pauses it and puts it at the start of the
        programme, and what was being measured is then gone. Beginning
        again costs the 1.2 s of programme it plays; waiting for a
        clock that was put back to zero costs the whole run.

        The step is opened again with it, so the lines of the attempt
        that was interrupted go rather than being read as this one's.
        """
        b = result["cut"][result["edge"]][1]
        step("playing over %.3f" % b)
        p.jump(max(p.begins, b - 1.2))
        # Where the clock stood before it was asked to run, so that
        # "it never started" can be told from "it never got there".
        state["from"] = state["seen_at"] = p._time()
        state["still"] = 0
        p.play()

    def play_over_the_edge():
        """Let it run into the camera change, the way a person does."""
        i = result.get("edge")
        p = cut_ready()
        b = result["cut"][i][1] if i is not None else 0.0
        start = max(p.begins, b - 1.2) if p is not None else 0.0
        if not covers(p, start):
            if state["ready"] < TRIES:
                state["ready"] += 1
                return "again"
            result.setdefault("silent", []).append(
                {"step": "playing over", "covered": False,
                 "waited_ms": state["ready"] * 200})
            return
        run_at_the_edge(p)

    def wait_for_the_switch():
        """Wait for the shot to change, and give up on standstill.

        Three things can happen while it runs and they are not the
        same. The shot changes: done. The clock moves: the player is
        working, and a machine that needs longer must not be called
        broken for it. The clock stands still, or has gone back to the
        start of the programme -- and that last one is a state, not a
        delay: the window recomputes its preview whenever a fact about
        a file arrives, hands the player the fresh cut, and the player
        pauses and goes back to the beginning. Then the run is begun
        again rather than waited out.

        The clock is a stopwatch on the wall, so it rises while
        anything is playing however loaded the machine is. Standstill
        therefore means stopped, and it is the only thing worth giving
        up on.

        And play is not pressed at a player that is already playing:
        play starts the clock over at the position it finds. A poll
        that pressed it every time held the clock at a fifth of a
        second for sixteen seconds and then reported a player that
        never ran -- which was this test's own doing and not the
        program's.
        """
        p = cut_ready()
        i = result.get("edge")
        if p is None or i is None:
            close()
            return
        state["played"] += 1
        now = p._time()
        if p.now != i + 1:
            if not p._playing or now < state["from"] - 0.5:
                # The window laid its own cut over ours and the player
                # is back at the start. Begin again.
                if state["again"] < BEGUN_AGAIN:
                    state["again"] += 1
                    run_at_the_edge(p)
                    return "again"
            elif now > state["seen_at"] + 0.01:
                # It is running. Nothing to ask for, and nothing to
                # press: pressing play here is what froze the clock.
                state["seen_at"] = now
                state["still"] = 0
                return "again"
            elif state["still"] < STILL:
                state["still"] += 1
                # A play that lands before the file is loaded is
                # dropped, and then the cause is worth asking for once
                # more -- every couple of seconds, not every poll.
                if state["still"] % 10 == 0:
                    p.play()
                return "again"
        result["switched"] = (p.now == i + 1)
        # How far it got, for the line that has to say so where it never
        # got there. The player's own clock, because that is the thing
        # that is meant to be running.
        result["ran_to"] = round(max(state["seen_at"], now), 3)
        result["waited_ms"] = state["played"] * 200
        result["still_for_ms"] = state["still"] * 200
        # How often the window took the cut back from under it. A run
        # that was begun three times and one that was never disturbed
        # look alike in every other number.
        result["begun_again"] = state["again"]
        # Whether it left the mark at all. A player that never started
        # and one that started and stopped short of the change fail the
        # same way from outside, and they are not the same fault.
        result["started"] = state["seen_at"] > state["from"]
        result["from_at"] = round(state["from"], 3)
        # It did start, so it may be stopped: a player that never ran
        # is a different matter, and pausing one of those is what left
        # a window standing.
        p.pause()
        # The one step that goes on printing after its own body has
        # returned: it ends where the player stops, not where the jump
        # did.
        close()

    def reversed_offsets():
        """The same points again, with every offset the wrong way round.

        Nothing else changes: the same window, the same player, the
        same cut and the same sound file. If the checks above cannot
        see this, they were reading the player's own arithmetic back to
        itself.

        What gets turned round is what the window handed the player at
        the start and this test kept, not whatever the player is
        holding now. On a second go it is already holding the reversed
        numbers, and reversing those would put the honest ones back and
        leave the counter-check checking nothing while staying green.
        """
        p = cut_ready()
        if p is None or not keep:
            return
        turned = {k: -v for k, v in keep["offset"].items()}
        result["reversed"] = turned
        # Said before the offsets are turned round: handing the player
        # a cut puts it back to the start, and that first line is
        # already a reversed one.
        step("reversed at the start")
        p.set(keep["cut"], keep["files"], turned, keep["audio"],
              -keep["audio_offset"], keep["begins"], keep["until"],
              keep["tc0"])
        # No turn of the event loop in here, and no waiting either. The
        # jump prints before it returns, and letting the window run in
        # between would let it lay its own cut over this one -- the
        # counter-check would then be reading the honest offsets and
        # calling the checks toothless.
        for t in result["spots"]:
            step("reversed %.3f" % t)
            p.jump(t)
        close()
        # And where the window did get in between, the step is done
        # again rather than reported. It shows in what was printed, and
        # in two shapes: one shot answering twice while another never
        # does, and a line carrying the honest offset because the
        # rebuild landed between two jumps. On a loaded machine both are
        # the machine talking, not the program.
        said = [x for t in result["spots"]
                for x in said_in("reversed %.3f" % t)]
        astray = [x for x in said
                  if abs(x["picture_offset"] - turned.get(x["who"], 0.0))
                  > 0.001]
        if ((len(set(x["who"] for x in said)) < len(result["spots"])
             or astray) and state["turned"] < TRIES):
            state["turned"] += 1
            return "again"
        result["reversed_seen"] = dict(p.offset)
        result["reversed_sound"] = p.audio_offset
        result["reversed_tries"] = state["turned"]

    def empty_cut():
        """The state the slower machine was caught in, on purpose.

        A jump prints unless the player's cut holds that moment, and
        between two loads it holds nothing at all. Reproduced here so
        that the waiting above rests on a measurement rather than on a
        story: the same jump, the same player, an empty cut, and not a
        word out of it.
        """
        p = cut_player()
        if p is None:
            return
        step("an empty cut")
        p.set([], {}, {}, None, 0.0)
        p.jump(result["spots"][0])
        # Closed at once, or the rebuild that comes while the next step
        # waits would print into it and this step would read noisy.
        close()

    def hand_it_back():
        """Give the player its cut again, a moment later.

        Says so first: handing over a cut puts the player back to the
        start and that prints a line of its own, which belongs to this
        and not to the step waiting beside it.
        """
        p = cut_player()
        if p is not None and keep:
            step("the cut comes back")
            p.set(keep["cut"], keep["files"], keep["offset"],
                  keep["audio"], keep["audio_offset"], keep["begins"],
                  keep["until"], keep["tc0"])
            close()

    def late_cut():
        """Ask for a moment the player does not hold yet.

        The counter-check to the waiting itself: the step before left
        the player with an empty cut, the cut comes back, and the jump
        has to arrive at a line all the same.

        The cut comes back on the step's own first retry, not after a
        length of time. A clock racing the plan decides differently on
        a loaded machine than on an idle one: the cut was back before
        the step ever asked, and the line it prints landed on whatever
        step was current.
        """
        plan.append(go_to("late %.3f" % result["spots"][0],
                          result["spots"][0], on_retry=hand_it_back))

    # ------------------------------- a fresh cut arrives under a viewer
    def shot_at(cut, t):
        """Which camera that cut shows at that moment."""
        for a, b, who in cut:
            if a <= t < b:
                return who
        return None

    def other_than(who):
        """Another camera of the same cut."""
        for _a, _b, w in keep["cut"]:
            if w != who:
                return w
        return None

    def on_screen(p):
        """The picture file the visible surface is holding.

        What a viewer would see, and not what the cut says or what the
        player printed: a cut can name a camera whose file was never
        loaded, and then the line reads right while the screen shows
        the shot before. Only the surface says which of the two it is.

        Nothing is caught here on purpose. A surface holding no file
        answers with an empty name by itself, which is a measurement; a
        player that has no surfaces at all is a different matter, and a
        traceback says so where an empty name would read as the first.
        """
        return os.path.basename(
            p.videos[p.stack.currentIndex()].source().toLocalFile())

    def hand_a_cut(p, cut, until):
        """Hand the player a cut and read the clock either side of it.

        Both readings in one breath, with no turn of the event loop
        between them: the player reads its own clock at the first line
        of the handover and puts it back at the last, so what lies
        between the two numbers is that one call and nothing else.
        """
        before, was = p._time(), p._playing
        p.set(cut, keep["files"], keep["offset"], keep["audio"],
              keep["audio_offset"], keep["begins"], until, keep["tc0"])
        return {"ran_before": was, "before": round(before, 3),
                "after": round(p._time(), 3), "runs_after": p._playing}

    def a_cut_while_it_plays():
        """Hand a running player a fresh cut, while it is running.

        The condition and the handover are one poll on purpose. Waiting
        for the clock in one step and handing the cut over in the next
        leaves a turn of the event loop in between, and the window can
        stop the player in it -- the step would then report a player
        that was not running rather than a place that was lost.

        The clock is a stopwatch on the wall, so it rises on the
        busiest machine as long as anything plays at all. Standstill is
        therefore worth giving up on, and a deadline is not. Where the
        window took the cut back the run is begun again rather than
        waited out, the same way as at the camera change.
        """
        p = cut_player()
        if p is None or not keep or not result.get("spots"):
            return
        at = result["spots"][0]
        if state["went"] is None:
            p.jump(at)
            p.play()
            state["went"] = p._time()
            state["quiet"] = 0
            return "again"
        now = p._time()
        moved = now - state["went"]
        if not (p._playing and moved >= MOVED):
            if not p._playing and state["afresh"] < BEGUN_AGAIN:
                # The window laid its own cut over ours and stopped it.
                state["afresh"] += 1
                state["went"] = None
                return "again"
            if state["quiet"] < STILL:
                state["quiet"] += 1
                # A play that lands before the file is loaded is
                # dropped, so the cause is worth asking for once more
                # now and then.
                if state["quiet"] % 10 == 0:
                    p.play()
                return "again"
            # Patience gone, and the cut is handed over all the same.
            # Left out, this step would be missing from the report and
            # the run would judge one thing less than the run before --
            # which is a second failure, about the count, on top of the
            # one that matters. Handed over, the first check below is
            # the one about the clock, and it says what never happened.
        step("a cut while it plays")
        handover["playing"] = hand_a_cut(p, keep["cut"], keep["until"])
        close()
        handover["playing"].update(
            at=at, began_at=round(state["went"], 3), moved=round(moved, 3),
            needed=MOVED, polls=state["quiet"], begun_again=state["afresh"],
            waited_ms=state["quiet"] * 200)
        p.pause()

    def a_cut_while_it_stands():
        """Hand a standing player a fresh cut.

        The other half of it: whoever had paused stays paused. A repair
        that put the playing back for everybody would start a picture
        running in front of somebody who had stopped it.
        """
        p = cut_player()
        if p is None or not keep or not result.get("spots"):
            return
        at = result["spots"][-1]
        p.pause()
        p.jump(at)
        step("a cut while it stands")
        handover["standing"] = hand_a_cut(p, keep["cut"], keep["until"])
        close()
        handover["standing"]["at"] = at

    def a_shorter_cut_arrives():
        """The fresh cut ends before the place the viewer was at.

        Then the place cannot be kept as it is, and the question is
        what becomes of it: pulled in to the end of the new cut, or
        thrown away. The first is a viewer who has to wind back a
        little, the second is a viewer who lost their place.
        """
        p = cut_player()
        if p is None or not keep or not result.get("spots"):
            return
        at = result["spots"][-1]
        ends_at = round((keep["begins"] + at) / 2.0, 3)
        shorter = [(a, min(b, ends_at), who) for a, b, who in keep["cut"]
                   if a < ends_at]
        p.pause()
        p.jump(at)
        step("a shorter cut")
        handover["shorter"] = hand_a_cut(p, shorter, ends_at)
        close()
        handover["shorter"].update(at=at, ends_at=ends_at,
                                   begins=keep["begins"])

    def another_camera_arrives():
        """The fresh cut puts another camera on the second in view.

        This is the half of the repair that the kept place must not
        cost. The picture belongs to the cut, so where the fresh cut
        names another camera on that second, that camera is what has to
        be on screen -- a short break in the picture is the price, and
        the owner asked for it to be paid.
        """
        p = cut_player()
        if p is None or not keep or not result.get("spots"):
            return
        at = result["spots"][0]
        # The honest cut first: the step before left a shorter one
        # behind, and this one is about the camera and nothing else.
        p.set(keep["cut"], keep["files"], keep["offset"], keep["audio"],
              keep["audio_offset"], keep["begins"], keep["until"],
              keep["tc0"])
        p.pause()
        p.jump(at)
        was = shot_at(keep["cut"], at)
        other = other_than(was)
        swapped = [(a, b, other if a <= at < b else who)
                   for a, b, who in keep["cut"]]
        step("another camera on the same second")
        showed = on_screen(p)
        p.set(swapped, keep["files"], keep["offset"], keep["audio"],
              keep["audio_offset"], keep["begins"], keep["until"],
              keep["tc0"])
        shows = on_screen(p)
        close()
        handover["camera"] = {
            "at": at, "was": was, "now_says": other, "showed": showed,
            "shows": shows,
            "was_file": os.path.basename(keep["files"].get(was) or ""),
            "wanted": os.path.basename(keep["files"].get(other) or "")}
        p.pause()

    def and_then_a_fresh_cut():
        """Queue the four handovers, after everything else is done.

        Appended from inside a step rather than listed with the others,
        because the step before this one appends the last of its own
        jumps to the end of the plan. Listed, these four would come
        between that step and its jump, and the jump would find a
        player holding a cut again -- which is the one thing that step
        is about not finding.
        """
        plan.extend([a_cut_while_it_plays, a_cut_while_it_stands,
                     a_shorter_cut_arrives, another_camera_arrives])

    after_the_edge = []
    if case == "plain":
        after_the_edge[:] = [play_over_the_edge, wait_for_the_switch,
                             reversed_offsets, empty_cut, late_cut,
                             and_then_a_fresh_cut]
    plan[:] = [open_project, wait_for_cut]

    done = [False]

    def hand_over(why=""):
        """Write the report where the parent will read it.

        Into a file, and not down the log. The log is shared with
        whatever the media backend has to say, and a measurement does
        not travel through a channel somebody else is writing in.
        Written whole and then moved into place, so a half-written file
        is never read as a report.
        """
        where = os.environ.get(OUT)
        if not where:
            return
        result["steps"] = seen["lines"]
        result["printed"] = seen["total"]
        result["loose"] = seen["loose"]
        if why:
            result["error"] = why
        with open(where + ".part", "w", encoding="utf-8") as f:
            json.dump(result, f)
        os.replace(where + ".part", where)

    def stop_now():
        done[0] = True
        hand_over()
        print(REPORT + "report written")
        sys.stdout.flush()
        app.quit()

    def next_step():
        if not plan:
            stop_now()
            return
        try:
            answer = plan[0]()
        except Exception:
            import traceback
            traceback.print_exc()
            result["error"] = "crash"
            stop_now()
            return
        if answer == "stop":
            stop_now()
            return
        if answer != "again":
            plan.pop(0)
        QtCore.QTimer.singleShot(200 if answer == "again" else 300,
                                 next_step)

    QtCore.QTimer.singleShot(300, next_step)
    # A window that never gets there must not hold the suite, and must
    # not pass either: the report is missing then and the parent says so.
    QtCore.QTimer.singleShot(200000, app.quit)
    vpm.gui()
    if not done[0]:
        hand_over("the window never got as far as the steps")


if os.environ.get("VPM_SOUND_PICTURE_CASE"):
    look(os.environ["VPM_SOUND_PICTURE_CASE"])
    raise SystemExit(0)


# ------------------------------------------------------------ the parent
# The counter is not called "done" here: the child above uses that name
# for two things of its own, and one name for three things is how a
# closing line ends in a traceback instead of a verdict.
began = time.time()
judged = 0
bad = []


def check(name, ok, extra=""):
    global judged
    judged += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


from fixture_root import fixture              # noqa: E402  after the child

material = fixture("interview")
missing = [n for n in CAMERAS
           if not os.path.exists(os.path.join(material, n))]
if missing:
    print("SKIPPED: no material under %s -- missing %s"
          % (material, ", ".join(missing)))
    print("\n%d checks in %.2f s" % (judged, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


posted = tempfile.mkdtemp(prefix="vpm_soundpicture_said_")


def build(case):
    """Start one child on one case, and say where to put its report."""
    env = dict(os.environ, VPM_SOUND_PICTURE_CASE=case,
               QT_QPA_PLATFORM="offscreen", VPM_SILENT="1",
               VPM_NO_SPEAKER_SPLIT="1", VPM_NO_UPDATE_CHECK="1",
               VPM_PLAYER_LOG="1", LANG="C", LC_ALL="C", LANGUAGE="en")
    env[OUT] = os.path.join(posted, "%s.json" % case)
    return subprocess.Popen(
        [sys.executable, os.path.abspath(__file__)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        env=env, cwd=HERE)


def listen(case, process):
    """Wait for one child and read the report it left behind.

    Off the disc and not out of the log. The child's log carries the
    media backend's chatter as well -- the two share one pipe -- and a
    fragment of it that ends without a newline takes the line behind it
    with it. That line is then printed and correct and unreadable, and
    the reader is left believing the player said nothing. Which is what
    happened: three build machines called a green run red over a line
    that was there.
    """
    try:
        out, _ = process.communicate(timeout=PATIENCE)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        out = ""
    where = os.path.join(posted, "%s.json" % case)
    left = os.path.exists(where)
    # The log is for reading, and it is shown whole where there is
    # nothing else to go on.
    if DUMP or not left:
        for x in out.split("\n"):
            if x:
                print("  | %s" % x)
    if not left:
        return {"error": "the child left no report"}, {}
    with open(where, encoding="utf-8") as f:
        d = json.load(f)
    # How many of the player's lines are still readable in the log,
    # against how many the child printed. The difference is what the
    # error output ate, and it is what this test used to be reading.
    d["in_the_log"] = sum(1 for r in out.split("\n") if SAID.match(r))
    return d, d.get("steps") or {}


report = {}
children = [(c, build(c)) for c in CASES]
for case, process in children:
    report[case] = listen(case, process)


def moments(line, measured, tc0):
    """The one instant, worked out three ways.

    From the picture: where the playhead sits in that camera's file,
    plus the timecode that file carries. From the sound: the same with
    the sound file. From the clock: programme time on top of where the
    programme starts. All three are wall clock seconds since midnight.
    """
    tc = measured["tc"].get(line["who"])
    if tc is None:
        return None
    return {"picture": line["picture"] + tc,
            "sound": line["sound"] + measured["mix_tc"],
            "clock": line["t"] + tc0}


def agree(step_lines, measured, tc0, frame):
    """How far the three roads are apart, worst first.

    Returns (the worst gap, a sentence about the line it was on). No
    line at all is not agreement: a step whose lines went missing would
    otherwise pass with nothing in it.
    """
    if not step_lines:
        return None, "the player printed nothing here"
    worst, said = 0.0, ""
    for line in step_lines:
        m = moments(line, measured, tc0)
        if m is None:
            return None, "%s is not a camera of this cut" % line["who"]
        gap = max(abs(m["picture"] - m["clock"]),
                  abs(m["sound"] - m["clock"]))
        if gap >= worst:
            worst = gap
            said = ("%s at programme %.3f: picture %+.3f s, sound "
                    "%+.3f s against the clock (a frame is %.3f s)"
                    % (line["who"], line["t"], m["picture"] - m["clock"],
                       m["sound"] - m["clock"], frame))
    return worst, said


for case in CASES:
    d, steps = report[case]
    print("%s:" % ("the cut the window worked out" if case == "plain"
                   else "the same cut with a time window set"))
    measured = d.get("measured") or {}
    frame = 1.0 / max(1.0, float(measured.get("fps") or 30.0))
    check("  the window worked a cut over two cameras out by itself",
          bool(d.get("cut")) and len(set(w for _a, _b, w in d["cut"])) > 1,
          json.dumps(d.get("error") or "")[:160])
    if not d.get("cut"):
        continue
    check("  and it runs on the prepared overall mix",
          d.get("audio") == os.path.basename(measured.get("mix") or ""),
          str(d.get("audio")))
    tc0 = d.get("tc0")
    want_tc0 = d["start_s"] + d["window_in"]
    check("  programme time starts where the recording's clock says",
          tc0 is not None and abs(tc0 - want_tc0) < 0.001,
          "%s, wanted %s" % (tc0, want_tc0))
    # The counter-check to that one, and the reason this test was
    # rewritten: a handover of an older run lies in the result folder,
    # an hour away and on one camera. A window reading it would land on
    # its start and show one shot; both are visible from here.
    stale = measured.get("stale_start")
    check("  and not where the older handover in the folder says",
          tc0 is not None and stale is not None
          and abs(tc0 - (stale + d["window_in"])) > 1.0
          and len(set(w for _a, _b, w in d["cut"])) > 1,
          "programme starts at %s, that file says %s, %d camera(s) in "
          "the cut" % (tc0, stale, len(set(w for _a, _b, w in d["cut"]))))
    if tc0 is None:
        continue

    # ---- the core: every line the player printed, at every step
    # Two steps are quiet on purpose and stand outside this. The empty
    # cut is the state a slower machine caught this test in,
    # reproduced. The shorter cut ends where it draws the viewer to, and
    # a shot runs up to its end and not into it, so no shot holds that
    # moment and the player has nothing to say about it -- that step is
    # about the clock, and its own checks are further down.
    QUIET = ("an empty cut", "a shorter cut")
    honest = [k for k in steps
              if not k.startswith("reversed") and k not in QUIET]
    check("  the player printed a line at every step",
          len(honest) >= 4 and all(steps[k] for k in honest),
          "%s %s" % (json.dumps({k: len(steps[k]) for k in sorted(steps)}),
                     json.dumps(d.get("silent") or [])[:220]))
    for name in sorted(honest):
        worst, said = agree(steps[name], measured, tc0, frame)
        check("  %s: sound and picture mean one moment" % name,
              worst is not None and worst <= frame, said)

    # ---- the jump: the line has to be about the point asked for
    for name in sorted(k for k in honest if k.startswith("jump")):
        want = float(name.split()[1])
        got = steps[name][0]["t"] if steps[name] else None
        check("  %s: the line is about that very moment" % name,
              got is not None and abs(got - want) <= frame, str(got))

    # ---- the camera change: the picture moves, the sound runs on
    at_edge = sorted(k for k in steps if k.startswith("edge"))
    if len(at_edge) == 2:
        before = steps[at_edge[0]][0]
        after = steps[at_edge[1]][0]
        check("  at the cut the picture file changes",
              before["who"] != after["who"],
              "%s then %s" % (before["who"], after["who"]))
        # The counter-check to the one below: this pair is only worth
        # anything if the two cameras really lie apart in their files.
        check("  and the two cameras lie apart in their files",
              abs(before["picture_offset"] - after["picture_offset"])
              > frame,
              "%.3f against %.3f" % (before["picture_offset"],
                                     after["picture_offset"]))
        check("  the sound keeps its offset over the cut",
              abs(before["sound_offset"] - after["sound_offset"]) < 0.001,
              "%.3f then %.3f" % (before["sound_offset"],
                                  after["sound_offset"]))
        moved = after["sound"] - before["sound"]
        ran = after["t"] - before["t"]
        check("  and it runs on with the clock instead of jumping",
              abs(moved - ran) <= frame,
              "sound moved %.3f s while the programme moved %.3f s"
              % (moved, ran))
        # The counter-check to that one: the picture is where the jump
        # happens. Both numbers come off the same two lines, so if the
        # sound looked continuous because nothing moved at all, this
        # says so.
        stepped = after["picture"] - before["picture"]
        check("  while the picture does jump, into the other file",
              abs(stepped - ran) > frame,
              "picture moved %.3f s while the programme moved %.3f s"
              % (stepped, ran))

    if case != "plain":
        continue

    # ---- running into the cut, rather than jumping over it
    playing = sorted(k for k in steps if k.startswith("playing"))
    ran = steps[playing[0]] if playing else []
    check("  running into the cut, the player ran at all",
          bool(d.get("started")),
          "clock %s -> %s after %s ms, still for %s ms, begun again %s "
          "time(s)" % (d.get("from_at"), d.get("ran_to"),
                       d.get("waited_ms"), d.get("still_for_ms"),
                       d.get("begun_again")))
    check("  running into the cut, the camera changed by itself",
          bool(d.get("switched"))
          and len(set(x["who"] for x in ran)) > 1,
          "ran %s to %s in %s ms, begun again %s time(s), over %s"
          % (d.get("from_at"), d.get("ran_to"), d.get("waited_ms"),
             d.get("begun_again"), json.dumps([x["who"] for x in ran])))

    # ---- the counter-check: the same checks over reversed offsets
    turned = sorted(k for k in steps if k.startswith("reversed"))
    seen = [line for k in turned for line in steps[k]]
    # That the reversal reached the player at all, and was still there
    # when it printed. A rebuild passing through would put the honest
    # cut back, and the checks below would then be reading the right
    # numbers and calling themselves toothless.
    want = d.get("reversed") or {}
    check("  the player was still holding the reversed offsets",
          bool(want) and d.get("reversed_seen") == want
          and all(abs(x["picture_offset"] - want.get(x["who"], 0.0))
                  < 0.001 for x in seen),
          "%s, printed %s, asked again %s time(s), %s line(s) of the "
          "window's own belonged to no step"
          % (json.dumps(d.get("reversed_seen")),
             json.dumps(sorted(set((x["who"], x["picture_offset"])
                                   for x in seen))),
             d.get("reversed_tries"), d.get("loose")))
    real = [line for line in seen
            if abs((d.get("reversed") or {}).get(line["who"], 0.0)) > frame]
    check("  the reversed run printed lines with a real offset in them",
          len(real) >= 1 and len(real) == len(seen),
          "%d of %d lines, offsets %s"
          % (len(real), len(seen), json.dumps(d.get("reversed"))))
    off, nameless = [], []
    for line in real:
        m = moments(line, measured, tc0)
        # A camera nobody measured a timecode for is not a small gap,
        # it is no measurement at all, and it must not be counted as
        # one -- least of all here, where a large gap is the pass.
        if m is None:
            nameless.append(line["who"])
            continue
        off.append(max(abs(m["picture"] - m["clock"]),
                       abs(m["sound"] - m["clock"])))
    check("  and every one of them is caught by the same check",
          bool(off) and not nameless and min(off) > frame,
          "smallest gap %.3f s, a frame is %.3f s%s"
          % (min(off) if off else 0.0, frame,
             (", no timecode measured for %s"
              % json.dumps(sorted(set(nameless)))) if nameless else ""))

    # ---- why the waiting above is written the way it is
    # A jump prints unless the player's cut holds that moment. The
    # state where it holds none is a real one -- the window hands the
    # player an empty cut while it rebuilds -- and it is what a slower
    # machine caught this test in. Here it is made on purpose, so that
    # the retry is answering something measured.
    check("  a jump into an empty cut prints nothing, which is the gap",
          "an empty cut" in steps and not steps["an empty cut"],
          "%d line(s)" % len(steps.get("an empty cut") or []))

    # ---- and the reason the numbers do not travel in the log any more
    # One step wrote what a media backend writes while it opens a file:
    # a fragment on the error output with no newline at the end. Both
    # go into one pipe, so it swallows the line the player prints next.
    # The step still has to arrive with its numbers, and the log has to
    # be short of at least that one line -- which is the proof that the
    # hazard is real and that this test no longer walks into it.
    noisy = sorted(k for k in steps if k.startswith("chatter"))
    asked = float(noisy[0].split()[1]) if noisy else None
    check("  a line printed while the backend chatters still arrives",
          bool(noisy) and any(abs(x["t"] - asked) <= frame
                              for x in steps[noisy[0]]),
          "lines at %s" % (json.dumps([x["t"] for x in steps[noisy[0]]])
                           if noisy else "-"))
    lost = (d.get("printed") or 0) - (d.get("in_the_log") or 0)
    check("  and the log is short of it, which is why it is not read",
          lost >= 1,
          "the child printed %s, the log still carries %s"
          % (d.get("printed"), d.get("in_the_log")))
    # And the other half: asked for a moment the player does not hold
    # yet, the step waits for the cut to come back and gets its line.
    # A step written against a length of time fails this one.
    late = sorted(k for k in steps if k.startswith("late"))
    want = float(late[0].split()[1]) if late else None
    tries = (d.get("tries") or {}).get(late[0] if late else "", 0)
    check("  and one that has to wait for the cut still gets its line",
          bool(late) and tries >= 1
          and any(abs(x["t"] - want) <= frame for x in steps[late[0]]),
          "asked again %s time(s), lines at %s"
          % (tries, json.dumps([x["t"] for x in steps[late[0]]])
             if late else "-"))

    # ---- a fresh cut arrives under a viewer
    # The window works its preview out again whenever a fact about a
    # file comes in and hands the player the answer. Until 31.8.2026
    # that call stopped whoever was watching and wound them back to the
    # In point -- once in every run measured here, beside neighbours
    # and alone alike, so pressing play soon after opening a project
    # put the viewer back where they started. What the viewer keeps is
    # the place and the playing; what follows the fresh cut is the
    # picture.
    over = d.get("handover") or {}
    on_air = over.get("playing") or {}
    check("  the fresh cut reached a player that was really running",
          (on_air.get("moved") or 0.0) >= (on_air.get("needed") or 1e9),
          "the clock rose %s s from %s, wanted %s s, after %s poll(s) and "
          "%s ms, begun again %s time(s)"
          % (on_air.get("moved"), on_air.get("began_at"),
             on_air.get("needed"), on_air.get("polls"),
             on_air.get("waited_ms"), on_air.get("begun_again")))
    check("  and that player is playing after the handover too",
          on_air.get("runs_after") is True,
          "playing %s before the fresh cut, %s after"
          % (on_air.get("ran_before"), on_air.get("runs_after")))
    # Where the limit comes from: the handover reads the player's clock
    # at its first line and puts it back at its last, so the two
    # numbers are one call apart and nothing else -- measured at 0.000 s
    # here, at 25 frames a second. A frame is the smallest step the
    # picture has, so a place that moved less than one was not lost;
    # and it leaves a machine three times slower all the room it needs.
    apart = (abs(on_air["after"] - on_air["before"])
             if "after" in on_air and "before" in on_air else None)
    check("  and it is still at the second it was watching",
          apart is not None and apart <= frame,
          "programme %s before the fresh cut, %s after, %s s apart, a "
          "frame is %.3f s"
          % (on_air.get("before"), on_air.get("after"),
             "-" if apart is None else round(apart, 4), frame))
    at_rest = over.get("standing") or {}
    check("  a player at a standstill is not set going by a fresh cut",
          at_rest.get("ran_before") is False
          and at_rest.get("runs_after") is False,
          "playing %s before the fresh cut, %s after"
          % (at_rest.get("ran_before"), at_rest.get("runs_after")))
    rested = (abs(at_rest["after"] - at_rest["before"])
              if "after" in at_rest and "before" in at_rest else None)
    check("  and it too keeps the second it was standing on",
          rested is not None and rested <= frame,
          "programme %s before the fresh cut, %s after, %s s apart, a "
          "frame is %.3f s"
          % (at_rest.get("before"), at_rest.get("after"),
             "-" if rested is None else round(rested, 4), frame))
    cropped = over.get("shorter") or {}
    check("  the place really lay past the end of the shorter cut",
          cropped.get("before") is not None
          and cropped.get("ends_at") is not None
          and cropped["before"] > cropped["ends_at"] + frame,
          "the viewer was at %s, the shorter cut ends at %s"
          % (cropped.get("before"), cropped.get("ends_at")))
    check("  and a shorter cut draws it in to that end, not to the start",
          cropped.get("after") is not None
          and cropped.get("ends_at") is not None
          and abs(cropped["after"] - cropped["ends_at"]) <= frame,
          "at %s afterwards, the cut ends at %s and begins at %s, a "
          "frame is %.3f s" % (cropped.get("after"), cropped.get("ends_at"),
                               cropped.get("begins"), frame))
    swapped = over.get("camera") or {}
    check("  the fresh cut names another camera on the second in view",
          bool(swapped.get("was_file"))
          and swapped.get("showed") == swapped.get("was_file")
          and bool(swapped.get("wanted"))
          and swapped.get("wanted") != swapped.get("was_file"),
          "at programme %s the screen held %s, the fresh cut says %s"
          % (swapped.get("at"), json.dumps(swapped.get("showed")),
             json.dumps(swapped.get("wanted"))))
    check("  and that camera's file is the one on screen afterwards",
          bool(swapped.get("wanted"))
          and swapped.get("shows") == swapped.get("wanted"),
          "%s on screen, wanted %s"
          % (json.dumps(swapped.get("shows")),
             json.dumps(swapped.get("wanted"))))

# ---- what the time window did to the picture, seen from outside
plain, _s = report["plain"]
shifted, _s2 = report["window"]
if plain.get("offset") and shifted.get("offset"):
    print("the time window, seen on both runs:")
    both = sorted(set(plain["offset"]) & set(shifted["offset"]))
    moved = [(t, plain["offset"][t] - shifted["offset"][t]) for t in both]
    check("  every camera moved by the In point, and by no more",
          bool(moved) and all(abs(v - WINDOW_IN) < 0.05 for _t, v in moved),
          json.dumps([[t, round(v, 3)] for t, v in moved]))
    check("  and the sound moved with them",
          abs((plain.get("audio_offset") or 0.0)
              - (shifted.get("audio_offset") or 0.0) - WINDOW_IN) < 0.05,
          "%s against %s" % (plain.get("audio_offset"),
                             shifted.get("audio_offset")))

print("\n%d checks in %.2f s" % (judged, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
