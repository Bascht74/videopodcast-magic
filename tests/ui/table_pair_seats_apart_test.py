# -*- coding: utf-8 -*-
"""Two cameras of one file name each take their own speakers.

Two cards give two files C0003.MP4; a cut with Multitrack on, Host.wav
and Guest.wav beside them. Sections: the chooser, the pair named apart,
the whole path on each; the sheet, the Camera column named alike, Host
on CardB and Guest on CardA; what the run and the preview are handed;
the wide shot once Guest is taken off; the project saved and opened
again; an older project whose answers name the file alone.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import wave
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import the_program

SCRIPT = the_program.SCRIPT

os.environ["QT_QPA_PLATFORM"] = "offscreen"
import numpy as np
from PySide6 import QtCore, QtGui, QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.update_offer = lambda *a, **k: None

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


folder = tempfile.mkdtemp(prefix="vpm_seats_")
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
CARD_A, CARD_B = PAIR
RECORDINGS = {}
for seed, who in enumerate(("Host", "Guest")):
    RECORDINGS[who] = os.path.join(folder, who + ".wav")
    with wave.open(RECORDINGS[who], "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(48000)
        f.writeframes((np.random.default_rng(seed).normal(0, 0.1, 6 * 48000)
                       .clip(-1, 1) * 32767).astype("<i2").tobytes())
OUT = os.path.join(folder, "Result")
os.makedirs(OUT)


def short(path):
    """A path as the FAIL line carries it: under the test's folder."""
    if not isinstance(path, str) or not path.startswith(folder):
        return repr(path)
    return os.path.relpath(path, folder).replace(os.sep, "/")


def project(stem, cameras):
    """A project file: the two names typed, each camera as given."""
    file_path = os.path.join(folder, "videopodcast-magic_%s.json" % stem)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({"format": vpm.FILE_FORMAT, "version": "test",
                   "timeline": [], "preset": "", "production": stem,
                   "multitrack": True, "project_type": "cut",
                   "speakers_local": False, "out_folder": OUT,
                   "assignment": {"audio:" + RECORDINGS[w]: [w, cameras[w]]
                                  for w in ("Host", "Guest")},
                   "files": [{"path": RECORDINGS[w], "kind": "audio"}
                             for w in ("Host", "Guest")]
                   + [{"path": p, "kind": "video"} for p in PAIR]}, f)
    return file_path


FRESH = project("Pair", {"Host": None, "Guest": None})
# As a project written before the camera was a path: the file name.
OLDER = project("Older", {"Host": "C0003.MP4", "Guest": "C0003.MP4"})
chosen = [FRESH]
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

# The real builder of the command line, kept before it is stood in
# for: it alone knows which camera a track reaches the run on.
build_argv = vpm.run_argv
handed = []


def no_run(values, assignment_file_path=""):
    """What a run would be told -- and then no run."""
    try:
        handed.append((values, build_argv(values, assignment_file_path)))
    except Exception as e:
        handed.append((values, (None, {"tracks_of": repr(e)}, [])))
    return None, None, []


vpm.run_argv = no_run


def win():
    """The program's window."""
    for w in app.topLevelWidgets():
        if "Video Podcast Magic" in w.windowTitle():
            return w
    return None


def chooser(who):
    """The "belongs to" field of one recording's row."""
    want = "%s -- %s" % (vpm.T('belongs to'), os.path.basename(
        RECORDINGS[who]))
    for box in win().findChildren(QtWidgets.QComboBox):
        if box.accessibleName() == want:
            return box
    return None


def camera_table():
    """The table under the tree: one row per camera, in the window's order."""
    for t in win().findChildren(QtWidgets.QTableWidget):
        head = t.horizontalHeaderItem(2)
        if head is not None and head.text() == vpm.T('gets audio from'):
            return t
    return None


def gets_from():
    """Column "gets audio from", row by row."""
    t = camera_table()
    if t is None:
        return []
    return [t.item(r, 2).text() if t.item(r, 2) else None
            for r in range(t.rowCount())]


def kinds():
    """What the Kind field of every camera row stands on, row by row."""
    t = camera_table()
    out = []
    for r in range(t.rowCount() if t is not None else 0):
        cell = t.cellWidget(r, 3)
        box = cell if isinstance(cell, QtWidgets.QComboBox) else (
            cell.findChild(QtWidgets.QComboBox) if cell else None)
        out.append(box.currentData() if box is not None else None)
    return out


def seat(who, value):
    """Pick an entry by what it stores, the way a click would."""
    box = chooser(who)
    box.setCurrentIndex(box.findData(value))


def picked(who):
    """What one recording's "belongs to" field stores now."""
    box = chooser(who)
    return box.currentData() if box is not None else None


def to_sheet():
    """Bring the assignment sheet to the front, where the table stands."""
    for tw in win().findChildren(QtWidgets.QTabWidget):
        for k in range(tw.count()):
            if vpm.T('Assignment && time window')[:8].lower() \
                    in tw.tabText(k).lower():
                tw.setCurrentIndex(k)


def press(text):
    """A push button by its wording."""
    for b in win().findChildren(QtWidgets.QPushButton):
        if b.text().strip().startswith(text):
            b.click()
            return True
    return False


def menu_action(text):
    """A menu entry by its wording, wherever in the bar it sits."""
    for a in win().findChildren(QtGui.QAction):
        if a.text().replace("&", "").strip().startswith(text):
            return a
    return None


def saved():
    """The project file Save project wrote into the output folder."""
    for name in sorted(os.listdir(OUT)):
        if name.startswith(vpm.PROJECT_PREFIX) and name.endswith(".json"):
            with open(os.path.join(OUT, name), encoding="utf-8") as f:
                return os.path.join(OUT, name), json.load(f)
    return None, {}


def judge_chooser():
    box = chooser("Host")
    entries = [(box.itemText(i), box.itemData(i),
                box.itemData(i, QtCore.Qt.ToolTipRole))
               for i in range(box.count())] if box else []
    pair = [e for e in entries if e[1] not in (vpm.MIX_ONLY,
                                               vpm.IGNORE_AUDIO)]
    print("1. The chooser")
    check("the pair stands in the chooser as two entries apart",
          len(pair) == 2 and len(set(e[0] for e in pair)) == 2
          and sorted(short(e[1]) for e in pair)
          == ["CardA/C0003.MP4", "CardB/C0003.MP4"],
          "entries %s, wanted two labels apart holding CardA/C0003.MP4 "
          "and CardB/C0003.MP4" % [(e[0], short(e[1])) for e in pair])
    check("the chooser numbers the second of the pair, in the window's order",
          [(e[0], short(e[1])) for e in pair]
          == [("C0003.MP4", "CardA/C0003.MP4"),
              ("C0003.MP4 (2)", "CardB/C0003.MP4")],
          "entries %s, wanted C0003.MP4 for CardA and C0003.MP4 (2) for "
          "CardB" % [(e[0], short(e[1])) for e in pair])
    check("each of the pair shows its whole path on hover",
          len(pair) == 2 and all(e[2] == e[1] for e in pair),
          "tooltips %s against %s" % ([short(e[2]) for e in pair],
                                      [short(e[1]) for e in pair]))


def judge_sheet():
    said = gets_from()
    t = camera_table()
    named = [(t.item(r, 0).text(), short(t.item(r, 0).toolTip()))
             if t is not None and t.item(r, 0) else None
             for r in range(t.rowCount() if t is not None else 0)]
    print("\n2. The sheet: Host on CardB, Guest on CardA")
    check("the Camera column names the pair alike, the path on hover",
          named == [("C0003.MP4", "CardA/C0003.MP4"),
                    ("C0003.MP4 (2)", "CardB/C0003.MP4")],
          "rows %s, wanted C0003.MP4 over CardA/C0003.MP4 and "
          "C0003.MP4 (2) over CardB/C0003.MP4" % (named,))
    check("each of the pair gets audio only from its own speaker",
          said == ["Guest", "Host"],
          "CardA, CardB say %r, wanted ['Guest', 'Host']" % (said,))


def judge_run():
    print("\n3. What the run and the preview are handed")
    values, (argv, plan, _m) = handed[-1] if handed else ({}, (None, {}, []))
    on = {t.get("speakers"): t.get("camera")
          for t in ((plan or {}).get("tracks_of") or [])
          if isinstance(t, dict)}
    check("the run puts each speaker on the camera picked for it",
          on == {"Host": CARD_B, "Guest": CARD_A},
          "Host on %s, Guest on %s, wanted CardB/C0003.MP4 and "
          "CardA/C0003.MP4; %d start(s) asked for, plan %r"
          % (short(on.get("Host")), short(on.get("Guest")), len(handed),
             sorted(plan or {}) if isinstance(plan, dict) else plan))
    where = {r.get("speakers"): r.get("camera_choice")
             for r in values.get("rows") or ()}
    d, why = vpm.build_handover(
        [("Host", [(0.0, 2.0)]), ("Guest", [(2.0, 4.0)])], 6.0, where,
        [{"track": "Card %d" % (i + 1), "file": p, "start_s": 0.0}
         for i, p in enumerate(PAIR)])
    seats = [(short(c.get("file")), c.get("speakers"))
             for c in (d or {}).get("cameras") or ()]
    check("the preview seats each speaker on its own camera",
          seats == [("CardA/C0003.MP4", ["Guest"]),
                    ("CardB/C0003.MP4", ["Host"])],
          "%s, wanted CardA ['Guest'] and CardB ['Host']; %s"
          % (seats, why or "built"))


def judge_wide():
    now = kinds()
    print("\n4. Guest taken off: the one of the pair nobody sits at")
    check("the one of the pair nobody sits at is the wide shot",
          now == [vpm.TYPE_WIDE, vpm.TYPE_CONTENT],
          "Kind of CardA, CardB %r, wanted [%r, %r]"
          % (now, vpm.TYPE_WIDE, vpm.TYPE_CONTENT))


def judge_reopened(where):
    print("\n5. The project saved and opened again")
    check("a reopened project stands on the same one of the pair",
          picked("Host") == CARD_B,
          "Host on %s, wanted CardB/C0003.MP4; saved as %s"
          % (short(picked("Host")), short(where)))


def judge_older():
    print("\n6. An older project, the camera named by its file alone")
    both = [picked("Host"), picked("Guest")]
    check("an older project's file name reads as the first of the pair",
          both == [CARD_A, CARD_A],
          "Host on %s, Guest on %s, wanted both on CardA/C0003.MP4"
          % tuple(short(p) for p in both))


state = {"round": 0, "seen": None, "still": 0, "step": "open"}


def settled(now):
    """True once *now* has stood unchanged for five turns."""
    state["still"] = state["still"] + 1 if (
        now is not None and now == state["seen"]) else 0
    state["seen"] = now
    return state["still"] >= 5


def next_step(name):
    """Go on to the step *name*, its waiting started afresh."""
    state.update(step=name, round=0, still=0, seen=None)


def step():
    """One turn: wait for the sheet to stand still, then act and judge."""
    state["round"] += 1
    if state["round"] > 300:
        bad.append("the window never settled at step %r" % state["step"])
        app.quit()
        return
    s = state["step"]
    if s == "open":
        win().show()
        win().resize(1400, 900)
        press(vpm.T('Open project ...')[:8])
        next_step("chooser")
    elif s in ("chooser", "reopened", "older"):
        to_sheet()
        box = chooser("Host")
        now = ((box.count(), picked("Host"), picked("Guest"),
                tuple(gets_from())) if box is not None else None)
        if settled(now) and len(now[3]) == 2:
            if s == "chooser":
                judge_chooser()
                seat("Host", CARD_B)
                seat("Guest", CARD_A)
                next_step("sheet")
            elif s == "reopened":
                judge_reopened(state.get("saved"))
                chosen[0] = OLDER
                press(vpm.T('Open project ...')[:8])
                next_step("older")
            else:
                judge_older()
                app.quit()
                return
    elif s == "sheet":
        if settled(tuple(gets_from())):
            judge_sheet()
            press(vpm.T('Start'))
            next_step("run")
    elif s == "run":
        if handed or state["round"] > 50:
            judge_run()
            menu_action(vpm.T('Save project')).trigger()
            next_step("saved")
    elif s == "saved":
        where, d = saved()
        if d or state["round"] > 50:
            state["saved"] = where
            seat("Guest", vpm.MIX_ONLY)
            next_step("wide")
    elif s == "wide":
        if settled(tuple(kinds())):
            judge_wide()
            chosen[0] = state.get("saved") or FRESH
            press(vpm.T('Open project ...')[:8])
            next_step("reopened")
    QtCore.QTimer.singleShot(200, step)


def deadline():
    """An outer brake only: the waiting inside is on the sheet."""
    bad.append("the window never finished: 280 s gone, at step %r"
               % state["step"])
    app.quit()


QtCore.QTimer.singleShot(300, step)
brake = QtCore.QTimer()
brake.setSingleShot(True)
brake.timeout.connect(deadline)
brake.start(280000)
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
