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

Five cases, in two windows built offscreen:

  * every line the player prints, at a standstill and while running
  * after a jump into the middle of the cut, where it went wrong
  * at a camera change: the picture file changes, the sound runs on
  * with the offsets deliberately reversed, which has to turn red
  * with a time window set, where programme time starts later

The reversed run is the point of the whole file. Two numbers that come
out of one subtraction always agree with each other, so a check that
only holds them together holds nothing. Reversing the sign of every
offset is the fault that was suspected, and the same checks over the
same player have to see it.

Where this check stops: the timecode of a file is the ground it
stands on, so a timecode read wrongly in the first place would move
all three roads together and go unseen here. That question belongs to
one_moment_test.py, which holds one moment against nine ways of
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
CAMERAS = ((WIDE, "Wide", []), (HOST, "Host", ["Host"]),
           (GUEST, "Guest", ["Guest"]))

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
# How far the window case pushes the start of the programme.
WINDOW_IN = 20.0
WINDOW = (1400, 950)
CASES = ("plain", "window")

# A child that has said nothing for this long has stopped, not slowed.
PATIENCE = 240
DUMP = bool(os.environ.get("VPM_SOUND_PICTURE_DUMP"))

# The line the player prints. Written by print() and not through the
# catalogue, so it reads the same in every language.
SAID = re.compile(
    r"^\s*player: programme\s+(-?[0-9.]+)\s+picture\s+(.*?)\s+at\s+"
    r"(-?[0-9.]+)\s+\(offset\s+(-?[0-9.]+)\)\s+sound\s+(-?[0-9.]+)\s+"
    r"\(offset\s+(-?[0-9.]+)\)\s*$")
MARK = "SOUNDPICTURE-STEP "
REPORT = "SOUNDPICTURE "


def lines_of(text):
    """Every player line of one section, as numbers."""
    out = []
    for row in text.split("\n"):
        got = SAID.match(row)
        if got:
            out.append({"t": float(got.group(1)), "who": got.group(2),
                        "picture": float(got.group(3)),
                        "picture_offset": float(got.group(4)),
                        "sound": float(got.group(5)),
                        "sound_offset": float(got.group(6))})
    return out


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
    """Material, project and handover for one case.

    The cameras are only linked to: opening a project moves the project
    file into its output folder and would leave the next test with
    nothing to open. What a run leaves behind is written here by hand --
    the handover file with the cameras and who spoke when, and the
    prepared overall mix in the folder the run puts it in. Returns
    (project file, out folder, what was measured about the cameras).
    """
    source = fixture("interview")
    own = tempfile.mkdtemp(prefix="vpm_soundpicture_")
    result = os.path.join(own, "Result")
    done = os.path.join(result, "auphonic-tracks")
    os.makedirs(done)
    here = {}
    for name, _track, _who in CAMERAS:
        copy = os.path.join(own, name)
        # Copied and not linked to: three megabytes each, and a link is
        # a privilege on Windows rather than a file operation.
        shutil.copyfile(os.path.join(source, name), copy)
        here[name] = copy
    # The frame rate is measured, because the frames of a timecode are
    # frames: read at 30 what was shot at 25, 18:55:17:12 lands 80 ms
    # out, which is two frames and would swallow exactly the kind of
    # error this test is for.
    fps = float(vpm.video_facts(here[WIDE]).get("fps") or 30.0)
    tc = {track: float(vpm.file_timecode(here[name], fps))
          for name, track, _who in CAMERAS}
    mix = os.path.join(done, "final_Full-Mix_%s.wav" % TAIL)
    silent_wav(mix, MIX_LENGTH, MIX_START)

    project = os.path.join(own, "videopodcast-magic_Sound_picture.json")
    with open(project, "w", encoding="utf-8") as f:
        json.dump({
            "format": vpm.FILE_FORMAT, "version": "test", "timeline": [],
            "call": [], "preset": "", "production": "Sound picture",
            "multitrack": False, "out_folder": result, "assignment": {},
            # The In point travels in the project file. There is no
            # field to type it into -- the window takes it off the
            # picture -- so this is the door a test has.
            "in_point": vpm.as_relative_time(WINDOW_IN)
                        if case == "window" else "",
            "out_point": "",
            "files": [{"path": here[n], "kind": "video"}
                      for n, _t, _w in CAMERAS],
        }, f, ensure_ascii=False, indent=1)

    with open(os.path.join(result, "Sound_picture_resolve.json"), "w",
              encoding="utf-8") as f:
        json.dump({
            "format": vpm.FILE_FORMAT, "created_by": "test",
            "production": "Sound picture", "fps": int(round(fps)),
            "fps_measured": fps, "drop_frame": False,
            "width": 320, "height": 180,
            "start_tc": vpm.timecode_string(CUT_START, fps),
            "start_s": CUT_START, "length_s": CUT_LENGTH, "lufs": -16.0,
            "intro": None, "outro": None,
            "cameras": [
                {"file": here[name], "source": here[name],
                 "camera": name, "track": track, "speakers": list(who),
                 "audio_tracks": ["Full-Mix"] if not who else list(who),
                 # The measured offset beside the timecode, and the
                 # same value: where the two disagree the program takes
                 # the timecode and says so, which is a different
                 # question from this one.
                 "offset": round(tc[track] - CUT_START, 4),
                 "duration": CUT_LENGTH, "wide": not who}
                for name, track, who in CAMERAS],
            "cut": [],
            "speakers": [
                {"name": "Host",
                 "sections": [[0.0, 10.0], [20.0, 30.0], [40.0, 50.0]]},
                {"name": "Guest",
                 "sections": [[10.0, 20.0], [30.0, 40.0],
                              [50.0, 60.0]]}],
            "audio_files": {}, "words": [],
        }, f, ensure_ascii=False, indent=1)
    return project, result, {"fps": fps, "tc": tc,
                             "files": {t: here[n] for n, t, _w in CAMERAS},
                             "mix": mix, "mix_tc": MIX_START}


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
            if x.windowTitle().startswith("Video Podcast"):
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

    def step(name):
        """Say which step the lines below belong to."""
        print(MARK + name)
        sys.stdout.flush()

    result = {"case": case, "measured": measured, "start_s": CUT_START,
              "window_in": WINDOW_IN if case == "window" else 0.0}
    state = {"waited": 0, "played": 0}

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

        The window builds it out of the handover once every file has
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
        result["tc0"] = p.tc0
        result["begins"], result["until"] = p.begins, p.until
        result["audio"] = os.path.basename(
            p.audio.source().toLocalFile())
        result["offset"] = dict(p.offset)
        result["audio_offset"] = p.audio_offset
        result["spots"] = spots(p)
        result["edge"] = edge(p)

    def jumps():
        """Jump to each of the points, one line each."""
        p = cut_ready()
        if p is None:
            return
        for t in result["spots"]:
            step("jump %.3f" % t)
            p.jump(t)
            app.processEvents()

    def around_the_edge():
        """A quarter of a second either side of a camera change."""
        i = result.get("edge")
        if i is None:
            result["error"] = "the cut never changes camera"
            return
        p = cut_ready()
        if p is None:
            return
        b = result["cut"][i][1]
        for t in (round(b - 0.25, 3), round(b + 0.25, 3)):
            step("edge %.3f" % t)
            p.jump(t)
            app.processEvents()

    def play_over_the_edge():
        """Let it run into the camera change, the way a person does."""
        i = result.get("edge")
        p = cut_ready()
        if i is None or p is None:
            return
        b = result["cut"][i][1]
        step("playing over %.3f" % b)
        p.jump(max(p.begins, b - 1.2))
        app.processEvents()
        p.play()

    def wait_for_the_switch():
        """Wait for the shot to change, not for a number of seconds.

        Programme time in the player runs on a clock of its own, so the
        change comes whether or not the pictures decode. A seek that
        never takes is given up on after five seconds inside the
        player, which is the longest this can honestly wait for.
        """
        p = cut_ready()
        i = result.get("edge")
        if p is None or i is None:
            return
        if p.now != i + 1 and state["played"] < 80:
            state["played"] += 1
            return "again"
        result["switched"] = (p.now == i + 1)
        # How far it got, for the line that has to say so where it never
        # got there. The player's own clock, because that is the thing
        # that is meant to be running.
        result["ran_to"] = round(p._time(), 3)
        result["waited_ms"] = state["played"] * 200
        # It did start, so it may be stopped: a player that never ran
        # is a different matter, and pausing one of those is what left
        # a window standing.
        p.pause()

    def reversed_offsets():
        """The same points again, with every offset the wrong way round.

        Nothing else changes: the same window, the same player, the
        same cut and the same sound file. If the checks above cannot
        see this, they were reading the player's own arithmetic back to
        itself.
        """
        p = cut_ready()
        if p is None:
            return
        turned = {k: -v for k, v in p.offset.items()}
        result["reversed"] = turned
        # Said before the offsets are turned round: handing the player
        # a cut puts it back to the start, and that first line is
        # already a reversed one.
        step("reversed at the start")
        p.set([(a, b, w) for a, b, w in p.cut], dict(p.files), turned,
              p.audio.source().toLocalFile(), -p.audio_offset,
              p.begins, p.until, p.tc0)
        app.processEvents()
        for t in result["spots"]:
            step("reversed %.3f" % t)
            p.jump(t)
            app.processEvents()

    plan[:] = [open_project, wait_for_cut, jumps, around_the_edge]
    if case == "plain":
        plan += [play_over_the_edge, wait_for_the_switch, reversed_offsets]

    done = [False]

    def stop_now():
        done[0] = True
        print(REPORT + json.dumps(result))
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
        print(REPORT + json.dumps(dict(result, error="never got there")))


if os.environ.get("VPM_SOUND_PICTURE_CASE"):
    look(os.environ["VPM_SOUND_PICTURE_CASE"])
    raise SystemExit(0)


# ------------------------------------------------------------ the parent
error = []


def check(name, ok, extra=""):
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


from fixture_root import fixture              # noqa: E402  after the child

material = fixture("interview")
missing = [n for n, _t, _w in CAMERAS
           if not os.path.exists(os.path.join(material, n))]
if missing:
    print("SKIPPED: no material under %s -- missing %s"
          % (material, ", ".join(missing)))
    raise SystemExit(0)


def build(case):
    """Start one child on one case."""
    env = dict(os.environ, VPM_SOUND_PICTURE_CASE=case,
               QT_QPA_PLATFORM="offscreen", VPM_SILENT="1",
               VPM_NO_SPEAKER_SPLIT="1", VPM_NO_UPDATE_CHECK="1",
               VPM_PLAYER_LOG="1", LANG="C", LC_ALL="C", LANGUAGE="en")
    return subprocess.Popen(
        [sys.executable, os.path.abspath(__file__)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        env=env, cwd=HERE)


def listen(case, process):
    """Wait for one child, and take the report and the steps apart."""
    try:
        out, _ = process.communicate(timeout=PATIENCE)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        out = ""
    said = [x for x in out.split("\n") if x.startswith(REPORT)]
    if DUMP or not said:
        for x in out.split("\n"):
            if x and not x.startswith(REPORT):
                print("  | %s" % x)
    if not said:
        return {"error": "the window never came back"}, {}
    report = json.loads(said[-1][len(REPORT):])
    steps, name = {}, None
    for row in out.split("\n"):
        if row.startswith(MARK):
            name = row[len(MARK):].strip()
            steps[name] = []
            continue
        got = SAID.match(row)
        if got and name:
            steps[name] = steps[name] + lines_of(row)
    return report, steps


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
    print("%s:" % ("the cut as the run left it" if case == "plain"
                   else "the same cut with a time window set"))
    measured = d.get("measured") or {}
    frame = 1.0 / max(1.0, float(measured.get("fps") or 30.0))
    check("  the window brought a cut over two cameras up",
          bool(d.get("cut")) and len(set(w for _a, _b, w in d["cut"])) > 1,
          json.dumps(d.get("error") or "")[:160])
    if not d.get("cut"):
        continue
    check("  and it runs on the prepared overall mix",
          d.get("audio") == os.path.basename(measured.get("mix") or ""),
          str(d.get("audio")))
    tc0 = d.get("tc0")
    check("  programme time starts where the handover says",
          tc0 is not None and abs(
              tc0 - (d["start_s"] + d["window_in"])) < 0.001,
          "%s, wanted %s" % (tc0, d["start_s"] + d["window_in"]))
    if tc0 is None:
        continue

    # ---- the core: every line the player printed, at every step
    honest = [k for k in steps if not k.startswith("reversed")]
    check("  the player printed a line at every step",
          len(honest) >= 4 and all(steps[k] for k in honest),
          json.dumps({k: len(steps[k]) for k in sorted(steps)}))
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
    check("  running into the cut, the camera changed by itself",
          bool(d.get("switched"))
          and len(set(x["who"] for x in ran)) > 1,
          "reached programme %s after %s ms, over %s"
          % (d.get("ran_to"), d.get("waited_ms"),
             json.dumps([x["who"] for x in ran])))

    # ---- the counter-check: the same checks over reversed offsets
    turned = sorted(k for k in steps if k.startswith("reversed"))
    seen = [line for k in turned for line in steps[k]]
    real = [line for line in seen
            if abs((d.get("reversed") or {}).get(line["who"], 0.0)) > frame]
    check("  the reversed run printed lines with a real offset in them",
          len(real) >= 1 and len(real) == len(seen),
          "%d of %d lines, offsets %s"
          % (len(real), len(seen), json.dumps(d.get("reversed"))))
    off = []
    for line in real:
        m = moments(line, measured, tc0)
        off.append(max(abs(m["picture"] - m["clock"]),
                       abs(m["sound"] - m["clock"])))
    check("  and every one of them is caught by the same check",
          bool(off) and min(off) > frame,
          "smallest gap %.3f s, a frame is %.3f s"
          % (min(off) if off else 0.0, frame))

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

print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
