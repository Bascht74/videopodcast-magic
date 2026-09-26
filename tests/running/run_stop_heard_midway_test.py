# -*- coding: utf-8 -*-
"""Stop pressed in a real window run ends it, and leaves no false result.

Plain path stopped while camera files are written, Multitrack while a
track is levelled, the step read at half speed (-readrate) so Stop meets
it midway. Each: Stop there, a soon end, no ffmpeg left, the stage named
by its caption, Start back; plain also: no cut-short camera file, no
handover or EDL, and the check and time axis measure afterwards, no Start.
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


def stopped_run(project, at):
    """Open *project*, Start, press Stop once *at* is under way.

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

        def kept(text):
            """Keep a piece of the log, and hand it on to the window."""
            seen["log"].append(text)
            return write(text)

        try:
            return real_loop(argv, state, kept, *rest)
        finally:
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
                if k is None or not k.isEnabled():
                    if time.time() - since[0] > 90:
                        return give_up("Start was not ready after 90 s")
                    return QtCore.QTimer.singleShot(100, tick)
                k.click()
                step[0], since[0] = 2, time.time()
            elif step[0] == 2:
                seen["step"] = under_way()
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


try:
    plain_path()
    let_go()
    multitrack()
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("the test itself broke off")
finally:
    let_go()
shutil.rmtree(WORK, ignore_errors=True)
shutil.rmtree(STORE, ignore_errors=True)
stop()
