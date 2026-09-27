# -*- coding: utf-8 -*-
"""Stop pressed in a real window run ends it, and leaves no false result.

Camera files (plain) and a levelled track (Multitrack), read at half
speed so Stop meets them midway: a soon end, no ffmpeg left; plain also
no cut-short file, handover or EDL, and check and axis measure after.
The time axis, its decoder held until Stop: nothing written. auphonic.com
stood in by a production that stays at work: a soon end. The run's own
separation by a stand-in worker: a soon end, the worker gone. Each: Stop
there, the stop said, Start back; all but the separation name the stage.
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
import glob
import json
import shutil
import subprocess
import tempfile
import time
import the_program
import way_ground as ground

SCRIPT = the_program.SCRIPT
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stop():
    """Nothing further can be asked, so count what there is and go."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


if ground.missing():
    print("SKIPPED: " + ground.missing())
    stop()

STORE = tempfile.mkdtemp(prefix="vpm_stop_store_")
os.environ["VPM_CACHE"] = STORE
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.words_at_hand = lambda *a, **k: []
vpm.recognise_speech = lambda *a, **k: ([], "")
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok

# The slowed step reads at half speed: a minute of camera takes two.
# Stop must end the run well inside that, on the slowest builder too.
PACE = "0.5"
SOON = 45.0
# Written this far, the step is under way and not merely begun.
UNDER_WAY = 64 * 1024
born = []
real_watch = vpm.RUN_VITALS.watch


def watched(proc):
    """Every child the run starts passes here; keep it for the end."""
    born.append(proc)
    return real_watch(proc)


vpm.RUN_VITALS.watch = watched
real_ffmpeg = vpm.run_ffmpeg_with_progress
slowed = {"at": None}
# A window of an earlier section outlives its gui(), and answers to the
# same title: its buttons would start that section's project again.
earlier = []


def paced(cmd, duration, text):
    """The program's own ffmpeg step, the chosen one read at half speed."""
    if slowed["at"] and slowed["at"] in os.path.basename(str(cmd[-1])):
        cmd = cmd[:1] + ["-readrate", PACE] + list(cmd[1:])
    return real_ffmpeg(cmd, duration, text)


vpm.run_ffmpeg_with_progress = paced


def running_ffmpeg():
    """The ffmpeg children of the run that have not ended, by output."""
    return [os.path.basename(str(p.args[-1])) for p in born
            if p.poll() is None and "ffmpeg" in os.path.basename(
                str(p.args[0] if isinstance(p.args, (list, tuple))
                    else p.args))]


def stopped_run(project, at, ready=None, startable=None, in_run=None):
    """Open *project*, Start, press Stop once *at* is under way.

    *ready* says instead when to press: a name for the step, or None;
    *startable* is asked of the window before Start, and may pick in it;
    *in_run* are names of the program set only while the run runs.
    Hands back what was seen: Stop at the press, seconds from the press
    to the loop's end (None if it never came in SOON), the ffmpeg still
    running then, the log, Start and Stop afterwards, and why it gave up.
    """
    seen = {"why": "", "log": [], "ended": None, "pressed": None,
            "stop_there": None, "running": [], "start_back": None,
            "stop_gone": None, "step": None}
    QtWidgets.QFileDialog.getOpenFileName = staticmethod(
        lambda *a, **k: (project, ""))
    real_loop = vpm.gui_run_loop

    def loop(argv, state, write, *rest):
        """The window's own run loop, with its log and its end kept."""
        seen["state"] = state
        before = dict((n, getattr(vpm, n)) for n in in_run or {})
        for n, v in (in_run or {}).items():
            setattr(vpm, n, v)

        def kept(text):
            """Keep a piece of the log, and hand it on to the window."""
            seen["log"].append(text)
            return write(text)

        try:
            return real_loop(argv, state, kept, *rest)
        finally:
            for n, v in before.items():
                setattr(vpm, n, v)
            seen["ended"] = time.time()

    vpm.gui_run_loop = loop
    del born[:]
    slowed["at"] = at
    step, since = [0], [time.time(), 0]

    def win():
        """This section's window, once it stands; never an earlier one."""
        for x in app.topLevelWidgets():
            if vpm.DISPLAY_NAME in x.windowTitle() and x not in earlier:
                return x

    def button(text):
        """The window's button whose text begins with *text*."""
        for w in (win().findChildren(QtWidgets.QPushButton)
                  if win() else ()):
            if w.text().strip().startswith(text):
                return w

    def under_way():
        """The slowed step's child, running and some way into its file."""
        for p in born:
            out = str(p.args[-1])
            if at in os.path.basename(out) and p.poll() is None \
                    and os.path.exists(out) \
                    and os.path.getsize(out) >= UNDER_WAY:
                return os.path.basename(out)

    def give_up(why):
        """Stop waiting, and keep the reason for the red line."""
        seen["why"] = why
        app.quit()

    def tick():
        """One step: open, Start, wait for the step, Stop, wait, look."""
        try:
            if step[0] == 0:
                if button(vpm.T("Open project")) is None:
                    if time.time() - since[0] > 60:
                        return give_up("no Open project button in 60 s")
                    return QtCore.QTimer.singleShot(50, tick)
                win().show()
                button(vpm.T("Open project")).click()
                step[0], since[0] = 1, time.time()
            elif step[0] == 1:
                k = button(vpm.T("Start"))
                if startable is not None and not startable(win()):
                    k = None
                if k is None or not k.isEnabled():
                    if time.time() - since[0] > 90:
                        return give_up("Start was not ready after 90 s")
                    return QtCore.QTimer.singleShot(100, tick)
                k.click()
                step[0], since[0] = 2, time.time()
            elif step[0] == 2:
                seen["step"] = (ready or under_way)()
                if seen["step"]:
                    k = button(vpm.T("Stop"))
                    seen["stop_there"] = (k is not None and k.isVisible()
                                          and k.isEnabled())
                    seen["pressed"] = time.time()
                    if k is not None:
                        k.click()
                    step[0] = 3
                elif seen["ended"]:
                    return give_up("the run ended before %s was under way"
                                   % at)
                elif len(seen["log"]) != since[1]:
                    since[0], since[1] = time.time(), len(seen["log"])
                elif time.time() - since[0] > ground.STILL:
                    return give_up("the run stood still for %.0f s before "
                                   "%s" % (ground.STILL, at))
            elif step[0] == 3:
                # Waited on the loop's end, and judged either way at SOON.
                if seen["ended"] or time.time() - seen["pressed"] > SOON:
                    seen["running"] = running_ffmpeg()
                    step[0], since[0] = 4, time.time()
            else:
                k, s = button(vpm.T("Start")), button(vpm.T("Stop"))
                back = k is not None and k.isEnabled()
                gone = s is None or s.isHidden()
                if (back and gone) or time.time() - since[0] > 10 \
                        or not seen["ended"]:
                    seen["start_back"], seen["stop_gone"] = back, gone
                    return app.quit()
        except Exception as e:
            return give_up("%s: %s" % (type(e).__name__, e))
        QtCore.QTimer.singleShot(50, tick)

    QtCore.QTimer.singleShot(0, tick)
    sys.argv = ["videopodcast_magic.py"]
    vpm.gui()
    earlier.extend(x for x in app.topLevelWidgets()
                   if vpm.DISPLAY_NAME in x.windowTitle())
    vpm.gui_run_loop = real_loop
    slowed["at"] = None
    if seen["ended"] and seen["pressed"]:
        seen["took"] = seen["ended"] - seen["pressed"]
    else:
        seen["took"] = None
    seen["text"] = "".join(seen["log"])
    return seen


def let_go():
    """End whatever of a run is still running, so nothing outlives it."""
    for p in born:
        if p.poll() is None:
            p.kill()
            p.wait()


def length(path):
    """Seconds of a media file by ffprobe, or None when it cannot be read."""
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", path],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        return float(r.stdout.decode().strip())
    except ValueError:
        return None


def took(seen):
    """Seconds from Stop to the run's end, as the red line says it."""
    if seen["took"] is None:
        return "no end within %.0f s of Stop" % SOON
    return "%.2f s from Stop to the end" % seen["took"]


BROKEN_OFF = vpm.T('Everything after that step is missing. The folder '
                   'holds a part of a run, not a result.')
AT_STEP = vpm.T('\nStopped during: %s').strip().split("%s")[0].strip()
WORK = ground.own_folder("stop")


def finished_named(text):
    """The names the stop report lists as finished, or None if no list.

    The list is the line after "Stopped during:", after its last colon;
    "-" stands for none.
    """
    lines = [x.strip() for x in text.splitlines()]
    at = [i for i, x in enumerate(lines) if AT_STEP in x]
    if not at or at[-1] + 1 >= len(lines):
        return None
    listed = lines[at[-1] + 1].rsplit(": ", 1)[-1]
    return [] if listed == "-" else listed.split(", ")


def stopped_at(text):
    """What the last "Stopped during:" line names, or None without one."""
    at = [x for x in text.splitlines() if AT_STEP in x]
    return at[-1].split(AT_STEP, 1)[1].strip() if at else None


def afterwards(call):
    """What *call* gave: ('returned', value) or ('raised', its text)."""
    try:
        return "returned", call()
    except BaseException as e:      # noqa: BLE001 -- the answer judged
        return "raised", "%s: %s" % (type(e).__name__, str(e)[:80])


def plain_path():
    """Stop while the camera files are written, and what is left."""
    print("Plain path, Stop while the camera files are written")
    OUT = os.path.join(WORK, "plain")
    os.makedirs(OUT)
    # The project file inside the out folder, where it is kept in use;
    # the stop report must still not count it as finished.
    seen = stopped_run(ground.project_file(vpm, OUT, OUT), "_audio.mov")
    check("Stop stands and can be pressed while a camera file is written",
          bool(seen["stop_there"]),
          "%s; Stop there and enabled: %r"
          % (seen["why"] or "pressed at %s" % seen["step"],
             seen["stop_there"]))
    check("the run ends soon after Stop pressed during the camera files",
          seen["took"] is not None and seen["took"] < SOON,
          "%s; %s" % (took(seen),
                      seen["why"] or "the step read at %sx" % PACE))
    check("no ffmpeg of a run stopped at the cameras runs on",
          seen["pressed"] is not None and not seen["running"],
          "%d still running when the loop was back or given up: %s"
          % (len(seen["running"]), seen["running"]))
    short = []
    for film in sorted(glob.glob(os.path.join(OUT, "*_audio.mov"))):
        name = os.path.basename(film)[:-len("_audio.mov")]
        source = ground.media(name)
        have = length(film)
        want = length(source) if os.path.exists(source) else None
        if have is None or want is None or have < want - 0.5:
            short.append("%s %s s of %s s" % (os.path.basename(film), have,
                                              want))
    check("no camera file cut short by Stop is left under its name",
          seen["pressed"] is not None and not short,
          "%d cut short: %s" % (len(short), "; ".join(short)))
    left = [os.path.basename(p) for p in
            glob.glob(os.path.join(OUT, "*_resolve.json"))
            + glob.glob(os.path.join(OUT, "*.edl"))]
    check("a run stopped at the camera files writes no handover or EDL",
          seen["pressed"] is not None and not left,
          "left in the folder: %s" % (sorted(left),))
    check("the window names the step a camera-file run was stopped in",
          AT_STEP in seen["text"] and BROKEN_OFF in seen["text"],
          "'%s' %s, the break-off sentence %s; the log ends: %s"
          % (AT_STEP, "said" if AT_STEP in seen["text"] else "missing",
             "said" if BROKEN_OFF in seen["text"] else "missing",
             " / ".join(x.strip() for x in seen["text"]
                     .replace(OUT, "<out>").splitlines()
                     if x.strip())[-300:]))
    named = finished_named(seen["text"])
    foreign = [n for n in named or () if n not in os.listdir(OUT)
               or n.startswith(vpm.PROJECT_PREFIX)]
    check("the stop report names as finished only results in the out folder",
          seen["pressed"] is not None and named is not None and not foreign,
          "named %s, not a result of the out folder: %s"
          % (named, foreign))
    check("Start is back and Stop gone after a run stopped at the cameras",
          bool(seen["start_back"]) and bool(seen["stop_gone"]),
          "Start enabled %r, Stop gone %r" % (seen["start_back"],
                                              seen["stop_gone"]))
    said, wanted = stopped_at(seen["text"]), vpm.T('Writing the camera files')
    check("the stop report names the camera stage by its caption",
          said == wanted, "said %r, wanted %r" % (said, wanted))
    # What the window measures on its own, after the run and with no
    # new Start: the check of the files and the time axis.
    sound, pictures = ground.material()
    how, got = afterwards(lambda: vpm.collect_findings(sound, pictures))
    check("the file check measures after a stopped run, with no Start",
          how == "returned" and bool(got),
          "the check %s %s" % (how, "%d findings" % len(got)
                               if how == "returned" else got))
    how, got = afterwards(lambda: vpm.measure_time_axis(sound + pictures))
    placed = len(got[0].get("axis") or {}) if how == "returned" else 0
    check("the time axis measures after a stopped run, with no Start",
          placed == len(sound + pictures),
          "%d of %d files placed; %s %s" % (
              placed, len(sound + pictures), how,
              got[1] if how == "returned" else got))


def multitrack():
    """Stop while a Multitrack track is levelled."""
    print("\nMultitrack, Stop while a track is levelled")
    OUT = os.path.join(WORK, "multi")
    os.makedirs(OUT)
    os.makedirs(os.path.join(WORK, "multi_project"))
    seen = stopped_run(ground.project_plain(
        vpm, os.path.join(WORK, "multi_project"), OUT, multitrack=True),
        "level_")
    check("Stop stands and can be pressed while a Multitrack track levels",
          bool(seen["stop_there"]),
          "%s; Stop there and enabled: %r"
          % (seen["why"] or "pressed at %s" % seen["step"],
             seen["stop_there"]))
    check("a Multitrack run ends soon after Stop pressed while levelling",
          seen["took"] is not None and seen["took"] < SOON,
          "%s; %s" % (took(seen),
                      seen["why"] or "the step read at %sx" % PACE))
    check("no ffmpeg of a stopped Multitrack run runs on",
          seen["pressed"] is not None and not seen["running"],
          "%d still running when the loop was back or given up: %s"
          % (len(seen["running"]), seen["running"]))
    check("the window says where a Multitrack run was stopped",
          AT_STEP in seen["text"] and BROKEN_OFF in seen["text"],
          "'%s' %s, the break-off sentence %s; the log ends: %s"
          % (AT_STEP, "said" if AT_STEP in seen["text"] else "missing",
             "said" if BROKEN_OFF in seen["text"] else "missing",
             " / ".join(x.strip() for x in seen["text"]
                     .replace(OUT, "<out>").splitlines()
                     if x.strip())[-300:]))
    # Any stage caption: the levelling runs inside the speaker stage
    # today, and a better stage for it must not turn this red.
    said = stopped_at(seen["text"])
    wanted = [c for _n, _w, c in vpm.run_stages(True, 3, False)]
    check("the stop report names a Multitrack stage by its caption",
          said in wanted, "said %r, wanted one of %r" % (said, wanted))
    check("Start is back and Stop gone after a stopped Multitrack run",
          bool(seen["start_back"]) and bool(seen["stop_gone"]),
          "Start enabled %r, Stop gone %r" % (seen["start_back"],
                                              seen["stop_gone"]))


def results(out):
    """The camera files, handover and EDLs lying in *out*, by name."""
    return sorted(os.path.basename(p) for p in
                  glob.glob(os.path.join(out, "*_audio.mov"))
                  + glob.glob(os.path.join(out, "*_resolve.json"))
                  + glob.glob(os.path.join(out, "*.edl")))


def log_end(text, out):
    """The last of the window's log on one line, the out folder named."""
    return " / ".join(x.strip() for x in text.replace(out, "<out>")
                      .splitlines() if x.strip())[-300:]


def said_stopped(text):
    """Where the window's report stands: step line and break-off sentence."""
    return "'%s' %s, the break-off sentence %s" % (
        AT_STEP, "said" if AT_STEP in text else "missing",
        "said" if BROKEN_OFF in text else "missing")


def time_axis():
    """Stop while the time axis is measured, the decoder held there."""
    print("\nPlain path, Stop while the time axis is measured")
    OUT = os.path.join(WORK, "axis")
    os.makedirs(OUT)
    os.makedirs(os.path.join(WORK, "axis_project"))
    AXIS = vpm.T('Common time axis')
    measuring = {"now": False, "stage": ""}
    real, real_begin = vpm.decode_audio, vpm.step_begin

    def noted(name):
        """The run begins a stage: noted here, in the run's own thread."""
        measuring["stage"] = name
        return real_begin(name)

    def held(*a, **k):
        """The decoder, held inside the axis stage until Stop is pressed."""
        if measuring["stage"] == "time base":
            measuring["now"], since = True, time.time()
            while not vpm.RUN_STOP["wanted"] and time.time() - since < SOON:
                time.sleep(0.05)
            measuring["now"] = False
        return real(*a, **k)

    vpm.decode_audio, vpm.step_begin = held, noted
    try:
        seen = stopped_run(
            ground.project_file(vpm, os.path.join(WORK, "axis_project"),
                                OUT), "the time axis",
            ready=lambda: measuring["now"] and "the time axis")
    finally:
        vpm.decode_audio, vpm.step_begin = real, real_begin
    check("Stop stands and can be pressed while the time axis is measured",
          bool(seen["stop_there"]),
          "%s; Stop there and enabled: %r"
          % (seen["why"] or "pressed at %s" % seen["step"],
             seen["stop_there"]))
    left = results(OUT)
    # Judged on a run that came back: one still going writes on.
    check("a run stopped at the time axis writes no camera file or EDL",
          seen["pressed"] is not None and bool(seen["ended"]) and not left,
          "the run %s; left in the folder: %s; the log ends: %s"
          % ("came back" if seen["ended"] else "never came back", left,
             log_end(seen["text"], OUT)[-160:]))
    check("the window says where a run stopped at the time axis stopped",
          AT_STEP in seen["text"] and BROKEN_OFF in seen["text"],
          "%s; the log ends: %s" % (said_stopped(seen["text"]),
                                    log_end(seen["text"], OUT)))
    said = stopped_at(seen["text"])
    check("the stop report names the time axis stage by its caption",
          said == AXIS, "said %r, wanted %r" % (said, AXIS))
    check("Start is back and Stop gone after a run stopped at the axis",
          bool(seen["start_back"]) and bool(seen["stop_gone"]),
          "Start enabled %r, Stop gone %r" % (seen["start_back"],
                                              seen["stop_gone"]))


PRESET = "Stand-in preset"


class Service(object):
    """Stands in for auphonic.com: a production that stays at work.

    Every production it is asked about is still processing, until the
    section is over and it says the production failed, so a run that
    never heard Stop ends all the same.
    """

    def __init__(self):
        self.polls = []
        self.over = False

    def __call__(self, key, arguments, output_binary=False, progress=False):
        arguments = [str(a) for a in arguments]
        url = next((a for a in arguments
                    if a.startswith(vpm.auphonic.AUPHONIC)), "")
        path = url[len(vpm.auphonic.AUPHONIC):]
        post = "-X" in arguments
        if "-o" in arguments:
            open(arguments[arguments.index("-o") + 1], "wb").close()
            return b"" if output_binary else ""
        production = {"uuid": "PRODUCTION", "status": 2 if self.over else 1,
                      "status_string": "Audio Processing",
                      "error_message": "the test is over",
                      "output_files": []}
        if path.startswith("/api/preset/"):
            answer = {"status_code": 200, "data": {
                "uuid": "PRESET", "preset_name": PRESET,
                "is_multitrack": False, "algorithms": {},
                "output_files": [{"format": "wav-24bit", "ending": "wav"}]}}
        elif path.startswith("/api/info/output_files"):
            answer = {"data": {"wav-24bit": {"string": "WAV",
                                             "ending": "wav"}}}
        elif "?" in path:
            answer = {"status_code": 200, "data": []}
        else:
            if path.startswith("/api/production/") and not post:
                self.polls.append(time.time())
            answer = {"status_code": 201 if post else 200,
                      "data": production}
        return json.dumps(answer)


def preset_picked(window):
    """Pick the stand-in preset, as a hand would; True once it holds."""
    for box in window.findChildren(QtWidgets.QComboBox):
        at = box.findData(PRESET)
        if at >= 0:
            if box.currentData() != PRESET:
                box.setCurrentIndex(at)
            return box.currentData() == PRESET
    return False


def auphonic_wait():
    """Stop while the production at auphonic.com is waited for."""
    print("\nPlain path, Stop while auphonic.com works on the production")
    OUT = os.path.join(WORK, "service")
    os.makedirs(OUT)
    os.makedirs(os.path.join(WORK, "service_project"))
    service = Service()
    kept = (vpm._curl_call, vpm.load_api_key, vpm.list_presets)
    vpm._curl_call = service
    vpm.load_api_key = lambda: "stand-in-key"
    vpm.list_presets = lambda key: [(PRESET, "PRESET", False)]
    path = ground.project_file(vpm, os.path.join(WORK, "service_project"),
                               OUT)
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    d["preset"] = PRESET
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f)
    seen = None
    try:
        seen = stopped_run(path, "the wait for auphonic.com",
                           ready=lambda: bool(service.polls)
                           and "the wait for auphonic.com",
                           startable=preset_picked)
    finally:
        service.over = True
        since = time.time()
        while not seen_ended(seen) and time.time() - since < 30:
            time.sleep(0.1)
        vpm._curl_call, vpm.load_api_key, vpm.list_presets = kept
    check("Stop stands and can be pressed while auphonic.com is waited for",
          bool(seen["stop_there"]),
          "%s; Stop there and enabled: %r"
          % (seen["why"] or "pressed at %s" % seen["step"],
             seen["stop_there"]))
    check("the run ends soon after Stop pressed while auphonic.com works",
          seen["took"] is not None and seen["took"] < SOON,
          "%s; asked for the production %d times"
          % (took(seen), len(service.polls)))
    check("the window says where a run stopped at auphonic.com stopped",
          AT_STEP in seen["text"] and BROKEN_OFF in seen["text"],
          "%s; the log ends: %s" % (said_stopped(seen["text"]),
                                    log_end(seen["text"], OUT)))
    said, wanted = stopped_at(seen["text"]), vpm.T('Processing at '
                                                   'auphonic.com')
    check("the stop report names the auphonic.com stage by its caption",
          said == wanted, "said %r, wanted %r" % (said, wanted))
    check("Start is back and Stop gone after a run stopped at auphonic.com",
          bool(seen["start_back"]) and bool(seen["stop_gone"]),
          "Start enabled %r, Stop gone %r" % (seen["start_back"],
                                              seen["stop_gone"]))


def seen_ended(seen):
    """Whether the run loop of a section has come back."""
    return seen is not None and bool(seen.get("ended"))


# The stand-in separation works this long unless it is ended: well past
# SOON, so a Stop that waits for it shows.
LASTS = 3 * SOON
WORKER = '''import json, os, sys, time
sys.stdin.buffer.read()
began = time.time()
while time.time() - began < %(lasts)r and not os.path.exists(%(end)r):
    with open(%(beat)r, "a") as f:
        f.write(".")
    sys.stderr.write("P\\tstand-in\\t%%d\\t%%d\\n"
                     %% (time.time() - began, %(lasts)r))
    sys.stderr.flush()
    time.sleep(0.1)
print(json.dumps({"segments": [["SPEAKER_00", 1.0, 5.0]]}))
'''


def still_beating(path):
    """Whether *path* still grows: False once it stood a second still."""
    size, since, limit = -1, time.time(), time.time() + 10
    while time.time() < limit:
        now = os.path.getsize(path) if os.path.exists(path) else 0
        if now != size:
            size, since = now, time.time()
        elif time.time() - since >= 1.0:
            return False
        time.sleep(0.1)
    return True


def separation():
    """Stop while the run separates the speakers of its one recording."""
    print("\nPlain path, Stop while the run separates the speakers")
    OUT = os.path.join(WORK, "separation")
    PARTS = os.path.join(WORK, "separation_worker")
    for folder in (OUT, PARTS, os.path.join(WORK, "separation_project")):
        os.makedirs(folder)
    beat, end = os.path.join(PARTS, "beat"), os.path.join(PARTS, "end")
    worker = os.path.join(PARTS, "worker.py")
    with open(worker, "w", encoding="utf-8") as f:
        f.write(WORKER % {"lasts": LASTS, "beat": beat, "end": end})
    names = ("speaker_split_available", "speaker_model_folder",
             "speaker_model_checked", "speaker_model_mark",
             "speaker_python", "speaker_worker_file")
    kept = [getattr(vpm, n) for n in names]
    stand_ins = (lambda deep=False: True, lambda: PARTS,
                 lambda folder="": "", lambda folder="": "stand-in",
                 lambda: sys.executable, lambda: worker)
    for n, v in zip(names, stand_ins):
        setattr(vpm, n, v)
    sound, pictures = ground.material()
    seen = None
    try:
        # One recording and no separation handed over: the run takes it
        # apart itself. Allowed only while the run runs, or the window
        # starts one of its own on opening.
        seen = stopped_run(
            ground.project_plain(
                vpm, os.path.join(WORK, "separation_project"), OUT,
                multitrack=False,
                extra={"files": [{"path": p, "kind": "audio"}
                                 for p in sound]
                       + [{"path": p, "kind": "video"}
                          for p in pictures]}),
            "the separation",
            ready=lambda: os.path.exists(beat)
            and os.path.getsize(beat) > 0 and "the separation",
            in_run={"SPEAKER_SPLIT_OFF": False})
        running = still_beating(beat)
    finally:
        open(end, "w").close()
        since = time.time()
        while not seen_ended(seen) and time.time() - since < 60:
            time.sleep(0.1)
        for n, v in zip(names, kept):
            setattr(vpm, n, v)
    check("Stop stands and can be pressed while the run separates speakers",
          bool(seen["stop_there"]),
          "%s; Stop there and enabled: %r"
          % (seen["why"] or "pressed at %s" % seen["step"],
             seen["stop_there"]))
    check("the run ends soon after Stop pressed during the separation",
          seen["took"] is not None and seen["took"] < SOON,
          "%s; the separation works %.0f s unless it is ended"
          % (took(seen), LASTS))
    check("the separation of a stopped run does not work on",
          seen["pressed"] is not None and not running,
          "the worker %s after the run was back or given up"
          % ("still worked" if running else "had ended"))
    check("the window says where a run stopped in the separation stopped",
          AT_STEP in seen["text"] and BROKEN_OFF in seen["text"],
          "%s; the log ends: %s" % (said_stopped(seen["text"]),
                                    log_end(seen["text"], OUT)))
    check("Start is back and Stop gone after a run stopped in separation",
          bool(seen["start_back"]) and bool(seen["stop_gone"]),
          "Start enabled %r, Stop gone %r" % (seen["start_back"],
                                              seen["stop_gone"]))


try:
    plain_path()
    let_go()
    multitrack()
    let_go()
    time_axis()
    let_go()
    auphonic_wait()
    let_go()
    separation()
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("the test itself broke off")
finally:
    let_go()
shutil.rmtree(WORK, ignore_errors=True)
shutil.rmtree(STORE, ignore_errors=True)
stop()
