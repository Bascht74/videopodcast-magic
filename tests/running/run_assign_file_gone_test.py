# -*- coding: utf-8 -*-
"""A window run leaves no assignment file behind, however it ends.

The file names the recordings and the people in them. In order: a run
that finishes found its file while it ran and none is left afterwards;
a run stopped from the window leaves none; a window closed while its
run still goes leaves none (a child process, ended mid-run). The window
around the run start is stood in for and so is the run itself; the
start, its thread and the window's run loop are the program's own.
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
import glob, shutil, subprocess, tempfile, threading, time
os.environ["QT_QPA_PLATFORM"] = "offscreen"
CHILD = os.environ.get("VPM_ASSIGN_CHILD", "")
# Each part points the temporary folder at one of its own, under one
# place; the child is handed its parent's.
PLACE = (os.path.dirname(CHILD) if CHILD
         else tempfile.mkdtemp(prefix="vpm_gone_"))
from PySide6 import QtCore, QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


class Anything(object):
    """Takes every call and every name, and answers with itself."""

    def __getattr__(self, name):
        return self

    def __call__(self, *rest, **named):
        return self


class Value(object):
    """A window field as the run start reads it: get() and nothing else."""

    def __init__(self, value):
        self.value = value

    def get(self):
        """The value the field holds."""
        return self.value


def own_temp(tag):
    """A temporary folder of this part's own, made the program's too."""
    folder = tempfile.mkdtemp(prefix=tag + "_", dir=PLACE)
    os.environ["TMPDIR"] = folder
    tempfile.tempdir = None
    return folder


def model_in(folder):
    """Two recordings on two cameras, multitrack: the start writes a file."""
    paths = {}
    for name in ("Guest.wav", "Presenter.wav", "GuestCam.mov",
                 "PresentersCam.mov"):
        paths[name] = os.path.join(folder, name)
        open(paths[name], "wb").close()
    files = [(paths["Guest.wav"], "audio"), (paths["Presenter.wav"], "audio"),
             (paths["GuestCam.mov"], "video"),
             (paths["PresentersCam.mov"], "video")]
    model = Anything()
    model.__dict__.update(
        files=files, files_for_run=lambda: list(files),
        clip_kinds={}, out_folder=Value(os.path.join(folder, "out")),
        multitrack=Value(True), project_type=Value("cut"),
        assign_lines=[((paths["Guest.wav"],), Value("Guest"),
                       Value(paths["GuestCam.mov"])),
                      ((paths["Presenter.wav"],), Value("Presenter"),
                       Value(paths["PresentersCam.mov"]))],
        camera_lines=[(paths["GuestCam.mov"], Value(""), None, None),
                      (paths["PresentersCam.mov"], Value(""), None, None)],
        production=Value("Gone"), in_point=Value(""), out_point=Value(""),
        cut={}, edge_on=Value(False), voice_lines=[], key=Value(""),
        done_folder=Value(""), speech_language=Value(""), lufs=Value(None),
        no_join=set(), together_now=lambda: [])
    return model


def run_start(folder):
    """The run start over the stood-in window; hands back start and state."""
    state = {"running": False, "waiting": False, "confirmed": True,
             "camera_audio": False, "results": []}
    window = Anything()
    sheet = Anything()
    for name in ("start_run", "preview_button"):
        window.__dict__[name] = QtWidgets.QPushButton(name)
    sheet.__dict__["only_resolve"] = QtWidgets.QPushButton("resolve")
    window.__dict__["output_sheet"] = sheet
    window.__dict__["break_off"] = vpm.break_off_button(
        QtWidgets, state, lambda text: None)
    start, _only = vpm.make_run_start(
        QtCore, window, state, model_in(folder), Anything(),
        lambda *a: True, lambda text: None, Anything(), Anything(), {}, {},
        [], {"threads": 0}, threading.Lock(), lambda: False, Anything(),
        lambda: "", lambda: True, [])
    return start, state


# The run itself, stood in: it reads the file the line names, then
# ends the way the part asks for.
seen = {"file": "", "read": False}
ending = {"how": "finished"}
hold = threading.Event()


def stand_in_main():
    """The run: find --assign on the line, read it, end as told."""
    line = list(sys.argv)
    path = line[line.index("--assign") + 1] if "--assign" in line else ""
    seen["file"] = path
    try:
        with open(path, encoding="utf-8") as f:
            seen["read"] = bool(vpm.json.load(f).get("tracks_of"))
    except (OSError, ValueError):
        seen["read"] = False
    if ending["how"] == "stopped":
        raise vpm.Stopped("the stand-in run")
    if ending["how"] == "held":
        with open(os.path.join(PLACE, "seen"), "w") as f:
            f.write(path)
        hold.wait()
    return 0


vpm.gui_run_loop.__globals__["main"] = stand_in_main
threads = []
real_thread = threading.Thread


class KeptThread(real_thread):
    """A run thread like any other, kept so the test can wait on it."""

    def __init__(self, *rest, **named):
        real_thread.__init__(self, *rest, **named)
        threads.append(self)


def run_to_end(tag, how):
    """Start one run in a folder of its own; what is left there after."""
    folder = own_temp(tag)
    ending["how"] = how
    seen.update(file="", read=False)
    del threads[:]
    start, state = run_start(folder)
    start(False)
    until = time.time() + 30.0
    while (not threads or threads[0].is_alive()) and time.time() < until:
        app.processEvents()
        time.sleep(0.02)
    ended = bool(threads) and not threads[0].is_alive()
    return folder, ended, sorted(glob.glob(os.path.join(folder,
                                                        "vpm_assign_*")))


if CHILD:
    # The window closed mid-run: the run is held, the process ends.
    threading.Thread = KeptThread
    folder = own_temp("closed")
    ending["how"] = "held"
    start, _state = run_start(folder)
    start(False)
    until = time.time() + 30.0
    while not os.path.exists(os.path.join(PLACE, "seen")) \
            and time.time() < until:
        app.processEvents()
        time.sleep(0.02)
    with open(CHILD, "w") as f:
        f.write(folder)
    sys.exit(0)

threading.Thread = KeptThread
try:
    print("A run that finishes")
    folder, ended, left = run_to_end("finished", "finished")
    check("a finishing run found its assignment file while it ran",
          ended and seen["read"] and seen["file"].startswith(folder),
          "run ended %r, file %r, read %r"
          % (ended, os.path.basename(seen["file"]), seen["read"]))
    check("a finished run leaves no assignment file behind",
          ended and not left,
          "run ended %r, left %r"
          % (ended, [os.path.basename(p) for p in left]))

    print("\nA run stopped from the window")
    folder, ended, left = run_to_end("stopped", "stopped")
    check("a stopped run leaves no assignment file behind",
          ended and seen["file"] and not left,
          "run ended %r, file %r, left %r"
          % (ended, os.path.basename(seen["file"]),
             [os.path.basename(p) for p in left]))

    print("\nA window closed while its run goes")
    said = os.path.join(PLACE, "child_folder")
    env = dict(os.environ, VPM_ASSIGN_CHILD=said)
    child = subprocess.run([sys.executable, os.path.abspath(__file__)],
                           env=env, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, timeout=120)
    folder = ""
    if os.path.exists(said):
        with open(said) as f:
            folder = f.read()
    held = ""
    if os.path.exists(os.path.join(PLACE, "seen")):
        with open(os.path.join(PLACE, "seen")) as f:
            held = f.read()
    left = sorted(glob.glob(os.path.join(folder, "vpm_assign_*"))) \
        if folder else []
    check("a window closed mid-run leaves no assignment file behind",
          child.returncode == 0 and held.startswith(folder or "?")
          and not left,
          "child returned %r, held %r, left %r%s"
          % (child.returncode, os.path.basename(held),
             [os.path.basename(p) for p in left],
             ", said %r" % child.stdout.decode("utf-8", "replace")[-300:]
             if child.returncode else ""))
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("the test itself broke off")
finally:
    threading.Thread = real_thread
    shutil.rmtree(PLACE, True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
