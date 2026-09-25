# -*- coding: utf-8 -*-
"""Two cameras of one file name are named apart as the command line does.

Two cards emptied into two folders give two files of one name. The
window offers the second '<name> 2', the name the run gives it, and
holds nothing back for it. Sections: the sheet with both name fields;
the names offered against a dry run's over the same files; what the
sheet holds back; then the first renamed by hand, against a dry run
given that name alone. One window over two Sync only projects.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import wave
import the_program

SCRIPT = the_program.SCRIPT

os.environ["QT_QPA_PLATFORM"] = "offscreen"
import numpy as np
from PySide6 import QtCore, QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.update_offer = lambda *a, **k: None
vpm.run_argv = lambda values, assignment_file_path="": (None, None, [])

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


folder = tempfile.mkdtemp(prefix="vpm_pair_")
PAIR = []
for card in ("CardA", "CardB"):
    os.makedirs(os.path.join(folder, card))
    PAIR.append(os.path.join(folder, card, "C0003.MP4"))
    subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
         "testsrc=size=160x90:rate=25:duration=6", "-f", "lavfi",
         "-i", "sine=frequency=300:duration=6", "-c:a", "aac",
         "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
         "yuv420p", "-shortest", "-y", PAIR[-1]],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# One recording beside them: without it the sheet holds no camera table.
ROOM = os.path.join(folder, "Room.wav")
with wave.open(ROOM, "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(48000)
    f.writeframes((np.random.default_rng(3).normal(0, 0.1, 6 * 48000)
                   .clip(-1, 1) * 32767).astype("<i2").tobytes())
OUT = os.path.join(folder, "Result")
os.makedirs(OUT)
PROJECTS = []
for stem, named in (("Pair", {}), ("Typed", {"video:" + PAIR[0]: "Wide"})):
    PROJECTS.append(os.path.join(folder, "videopodcast-magic_%s.json" % stem))
    with open(PROJECTS[-1], "w", encoding="utf-8") as f:
        json.dump({"format": vpm.FILE_FORMAT, "version": "test",
                   "timeline": [], "preset": "", "production": stem,
                   "multitrack": False, "project_type": "sync",
                   "out_folder": OUT, "assignment": named,
                   "files": [{"path": ROOM, "kind": "audio"}]
                   + [{"path": p, "kind": "video"} for p in PAIR]}, f)
chosen = [PROJECTS[0]]
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (chosen[0], ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
_show = QtWidgets.QWidget.show


def offstage(self):
    """Shown for the layout, never on a screen."""
    self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
    _show(self)


QtWidgets.QWidget.show = offstage


def win():
    """The program's window."""
    for w in app.topLevelWidgets():
        if "Video Podcast Magic" in w.windowTitle():
            return w
    return None


def offered():
    """The camera table's name fields, row by row, as they read now."""
    for t in win().findChildren(QtWidgets.QTableWidget):
        head = t.horizontalHeaderItem(1)
        if head is not None and head.text() == vpm.T('new file name'):
            fields = [t.cellWidget(r, 1) for r in range(t.rowCount())]
            return [w.text() for w in fields
                    if isinstance(w, QtWidgets.QLineEdit)]
    return []


def rows(names):
    """Camera lines the way the window keeps them: file, new name."""
    return [(p, vpm.Value(n), None, None) for p, n in zip(PAIR, names)]


def dry_run(names=()):
    """The names a Sync only dry run gives the pair; and what it said.

    Read off its plan lines, "C0003.MP4  ->  <name>_audio.mov", in the
    order the files were given.
    """
    argv = [sys.executable, SCRIPT, "--without-auphonic", "--dry-run",
            "--out", OUT, "--project-type", "sync"]
    for file, name in names:
        argv += ["--new-name", file, name]
    env = dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="en",
               VPM_SILENT="1", VPM_NO_SPEAKER_SPLIT="1",
               VPM_NO_UPDATE_CHECK="1", QT_QPA_PLATFORM="offscreen")
    try:
        said = subprocess.run(argv + [ROOM] + PAIR, env=env, timeout=280,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT).stdout.decode(
                                  "utf-8", "replace")
    except subprocess.TimeoutExpired:
        return [], "no end in 280 s"
    lead = "C0003.MP4  ->  "
    targets = [line.strip()[len(lead):] for line in said.splitlines()
               if line.strip().startswith(lead)]
    return ([t.rsplit("_", 1)[0] for t in targets],
            "%d plan lines" % len(targets) if len(targets) == 2
            else "no two plan lines; it ended %r" % said[-300:])


def judge_plain():
    """The names offered where nobody typed one, against the dry run's."""
    names = offered()
    print("1. The camera table")
    check("the sheet came up with both cameras' name fields",
          len(names) == 2, "%d name fields, wanted 2" % len(names))
    print("\n2. The names offered")
    check("the second camera of one file name is offered '<name> 2'",
          names == ["C0003", "C0003 2"],
          "offers %r, wanted ['C0003', 'C0003 2']" % names)
    said, tail = dry_run()
    check("the command line gives the pair the same two names",
          said == names and len(set(said)) == 2,
          "the dry run %r, the window %r; %s" % (said, names, tail))
    print("\n3. What the pair holds back")
    held = vpm.missing_conditions(PAIR, "Pair", False, [], rows(names),
                                  project_type="sync").get(22)
    check("the pair holds nothing back on the assignment sheet",
          held is None, "the sheet says %r" % (held,))


def judge_typed():
    """The first camera named by hand: the second keeps the plain stem."""
    names = offered()
    print("\n4. The first camera renamed by hand")
    said, tail = dry_run([(PAIR[0], "Wide")])
    check("beside a typed name the second is offered the stem, as run",
          names == ["Wide", "C0003"] and said == names,
          "the window %r, the dry run given 'Wide' %r, wanted both "
          "['Wide', 'C0003']; %s" % (names, said, tail))


def to_sheet():
    """Bring the assignment sheet to the front, where the table stands."""
    for tw in win().findChildren(QtWidgets.QTabWidget):
        for k in range(tw.count()):
            if vpm.T('Assignment && time window')[:8].lower() \
                    in tw.tabText(k).lower():
                tw.setCurrentIndex(k)


state = {"round": 0, "seen": None, "still": 0, "phase": 0}


def open_project():
    """Press "Open project ..."; the dialog answers with chosen[0]."""
    for b in win().findChildren(QtWidgets.QPushButton):
        if b.text().strip().startswith(vpm.T('Open project ...')[:8]):
            b.click()
            return


def step():
    """Open a project, wait for the names to stand still, judge; twice."""
    state["round"] += 1
    if state["round"] == 1 and not state["phase"]:
        win().show()
        win().resize(1400, 900)
        open_project()
    to_sheet()
    now = offered() or None
    # Settled: both fields there, the first as this project names it,
    # and unchanged for five turns.
    first = "Wide" if state["phase"] else "C0003"
    state["still"] = state["still"] + 1 if (
        now and len(now) == 2 and now[0] == first
        and now == state["seen"]) else 0
    state["seen"] = now
    if state["still"] < 5 and state["round"] < 240:
        QtCore.QTimer.singleShot(200, step)
        return
    if state["phase"]:
        judge_typed()
        app.quit()
        return
    judge_plain()
    state.update(phase=1, round=0, still=0, seen=None)
    chosen[0] = PROJECTS[1]
    open_project()
    QtCore.QTimer.singleShot(200, step)


def deadline():
    """An outer brake only: the waiting inside is on the names."""
    bad.append("the window never finished: 240 s gone, at turn %d"
               % state["round"])
    app.quit()


QtCore.QTimer.singleShot(300, step)
brake = QtCore.QTimer()
brake.setSingleShot(True)
brake.timeout.connect(deadline)
brake.start(240000)
try:
    vpm.gui()
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("the window never came up: gui() fell over")
brake.stop()

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
