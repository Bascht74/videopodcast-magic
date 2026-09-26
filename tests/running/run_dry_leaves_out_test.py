# -*- coding: utf-8 -*-
"""A dry run leaves the output folder exactly as it found it.

It says so when it ends, and this holds it to that over the interview
fixture, both ways a dry run starts. The window: the project opened out
of its output folder, the Dry run button pressed and the run waited
out. The command line: --dry-run into a folder already holding a file.
Each time the folder is read before and after, name, bytes and time of
each file: nothing came in, went, or was written again.
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
SCRIPT = the_program.SCRIPT
import glob, hashlib, subprocess, tempfile, time
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
from fixture_project import fixture_project

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


def folder_read(folder):
    """Every file under the folder, by its path there: digest and mtime.

    The time goes along because a file written again with the same
    bytes was still written, and the run said nothing was.
    """
    seen = {}
    for root, _dirs, names in os.walk(folder):
        for name in names:
            path = os.path.join(root, name)
            with open(path, "rb") as f:
                seen[os.path.relpath(path, folder)] = (hashlib.sha256(
                    f.read()).hexdigest(), os.stat(path).st_mtime_ns)
    return seen


def difference(before, after):
    """What a run did to the folder, in words: empty where nothing.

    Each file that came in, went, or was written: its bytes changed,
    or only its time -- written again with what it held.
    """
    said = ["came in: %s" % n for n in sorted(set(after) - set(before))]
    for name in sorted(before):
        if name not in after:
            said.append("gone: %s" % name)
        elif after[name][0] != before[name][0]:
            said.append("other bytes: %s" % name)
        elif after[name] != before[name]:
            said.append("written again, same bytes: %s" % name)
    return said


# Still for this long, and the window has stopped writing on its own:
# opening a project measures the axis and puts it into the file. The
# run itself is bound only by how long nothing is said.
STILL = 3.0
QUIET = 120.0
PROJECT, MEDIA = fixture_project("drywindow")
if PROJECT is None:
    print("SKIPPED: no test project -- point VPM_MEDIA at a folder "
          "holding videopodcast-magic_Interview_2.json (looked in %s)"
          % MEDIA)
    stop()
# Where a run leaves it: the project file lies in the output folder.
OWN = os.path.dirname(PROJECT)
OUT = os.path.join(OWN, "Ergebnis")
os.replace(PROJECT, os.path.join(OUT, os.path.basename(PROJECT)))
PROJECT = os.path.join(OUT, os.path.basename(PROJECT))
with open(os.path.join(OUT, "kept_from_before.txt"), "w") as f:
    f.write("a file the run has no business with\n")
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (PROJECT, ""))
vpm.say_dialog = lambda *a, **k: True
said = []
ended = []
real_loop = vpm.gui_run_loop


def loop_watched(argv, state, write, *rest):
    """The window's own run, with what it says kept and its end marked."""
    def write_kept(text):
        said.append(text)
        return write(text)
    try:
        real_loop(argv, state, write_kept, *rest)
    finally:
        ended.append(time.time())


vpm.gui_run_loop = loop_watched


def win():
    """The program's main window, or None before it stands."""
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def button(word):
    """The push button whose caption begins with this word."""
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(word):
            return w


window = {"before": None, "after": None, "why": ""}
step = [0]
mark = [time.time(), None, 0]


def carry_on():
    """One step of the window's side; every wait is on a condition."""
    now = time.time()
    if step[0] == 0:
        if win() is None or button(vpm.T('Open project')) is None:
            if now - mark[0] > QUIET:
                window["why"] = "no window after %.0f s" % QUIET
                return app.quit()
            return QtCore.QTimer.singleShot(50, carry_on)
        win().show()
        button(vpm.T('Open project')).click()
        step[0], mark[0] = 1, now
    elif step[0] == 1:
        dry = button(vpm.T('Dry run'))
        state = folder_read(OUT)
        if state != mark[1]:
            mark[1], mark[0] = state, now
        if dry is None or not dry.isEnabled() or now - mark[0] < STILL:
            if now - mark[0] > QUIET:
                window["why"] = "Dry run never came free in %.0f s" % QUIET
                return app.quit()
            return QtCore.QTimer.singleShot(100, carry_on)
        window["before"] = state
        dry.click()
        step[0], mark[0] = 2, now
    elif step[0] == 2:
        if len(said) != mark[2]:
            mark[2], mark[0] = len(said), now
        if not ended:
            if now - mark[0] > QUIET:
                window["why"] = "the run said nothing for %.0f s" % QUIET
                return app.quit()
            return QtCore.QTimer.singleShot(100, carry_on)
        step[0], mark[0], mark[1], mark[2] = 3, now, None, now
    elif step[0] == 3:
        # The window takes the end in after the run has gone: read once
        # it has been still as long as before the press, or judged as
        # it stands once it never comes to rest.
        state = folder_read(OUT)
        if state != mark[1]:
            mark[1], mark[0] = state, now
        if now - mark[0] < STILL and now - mark[2] < QUIET:
            return QtCore.QTimer.singleShot(100, carry_on)
        window["after"] = state
        return app.quit()
    QtCore.QTimer.singleShot(50, carry_on)


print("1. The window's Dry run button")
QtCore.QTimer.singleShot(0, carry_on)
sys.argv = ["videopodcast_magic.py"]
vpm.gui()
end_text = vpm.run_done_text(True).strip()
check("the window's dry run was started and came to its end",
      window["after"] is not None and end_text in "".join(said),
      "%s; %d pieces said, the last: %r"
      % (window["why"] or "ran", len(said), "".join(said)[-120:]))
if window["after"] is not None:
    check("a dry run in the window leaves the output folder as it was",
          not difference(window["before"], window["after"]),
          "%s (%d files before, %d after)"
          % ("; ".join(difference(window["before"], window["after"])),
             len(window["before"]), len(window["after"])))

print("\n2. --dry-run on the command line")
media = os.path.dirname(os.path.realpath(glob.glob(
    os.path.join(OWN, "*.mov"))[0]))
out = tempfile.mkdtemp(prefix="vpm_dryout_")
with open(os.path.join(out, "kept_from_before.txt"), "w") as f:
    f.write("a file the run has no business with\n")
before = folder_read(out)
answer = subprocess.run(
    [sys.executable, SCRIPT, "--dry-run", "--without-auphonic",
     "--out", out, "--no-metrics", "--no-speech-recognition",
     "--no-transcript-file"]
    + sorted(glob.glob(os.path.join(media, "*.wav")))
    + sorted(glob.glob(os.path.join(media, "*.mov"))),
    capture_output=True, text=True, errors="replace")
after = folder_read(out)
check("the command line's dry run came back with 0",
      answer.returncode == 0,
      "return code %d, the last it said: %r"
      % (answer.returncode, (answer.stdout + answer.stderr)[-160:]))
check("a dry run on the command line leaves its folder as it was",
      not difference(before, after),
      "%s (%d files before, %d after)"
      % ("; ".join(difference(before, after)), len(before), len(after)))
stop()
