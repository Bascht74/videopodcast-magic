# -*- coding: utf-8 -*-
"""Six files added in the window are read as the line reads the same six.

way_ground's six files, in a mixed order. First the window as it
opens: the first sheet alone. Then Add files with the six: its table
holds two recordings, the presenter's two blocks as one, and the three
cameras; the output folder and the type are given and Dry run pressed.
Then the line's --dry-run over the same six: two recordings, the
blocks as one -- and the window's dry run reads the recordings and the
cameras the line reads; which camera a recording is on is the window's
own choice. The limit: the plan as printed, measuring only.
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
import re
import shutil
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


if ground.missing() or not all(os.path.exists(p)
                               for p in ground.recordings()):
    print("SKIPPED: " + (ground.missing() or "the presenter's two blocks "
                         "are missing under %s -- run tests/fixtures.sh"
                         % ground.MEDIA))
    stop()

STORE = tempfile.mkdtemp(prefix="vpm_way_store_")
os.environ["VPM_CACHE"] = STORE
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.words_at_hand = lambda *a, **k: []
vpm.recognise_speech = lambda *a, **k: ([], "")
# The question the assignment sheet asks once, answered without a box.
vpm.project_type_question = lambda window: "cut"

# Mixed: a camera first, the second block before the first.
ADDED = [ground.media(n) for n in (
    ground.WIDE, "Presenter_REC00032", ground.GUEST, "Guest_Take0031A",
    ground.PRES, "Presenter_REC00031")]
# What both doors should make of them, as values: each recording by
# the row it is shown under, the joined one with its second block.
RECORDINGS = ["Guest_Take0031A.wav", "Presenter_REC00031.wav (+1)"]
CAMERAS = sorted(n + ".mov" for n in (ground.WIDE, ground.PRES,
                                      ground.GUEST))
WORK = ground.own_folder("added")
OUT_WINDOW = os.path.join(WORK, "window")
os.makedirs(OUT_WINDOW)
QtWidgets.QFileDialog.getOpenFileNames = staticmethod(
    lambda *a, **k: (list(ADDED), ""))
QtWidgets.QFileDialog.getExistingDirectory = staticmethod(
    lambda *a, **k: OUT_WINDOW)


def read_alike(lines):
    """The plan's lines without what only the window chooses.

    A recording's camera is picked in the window's table, and the line
    given no assignment picks none; the order of the cameras is the
    table's. So a recording's line is cut at its arrow, and all sorted.
    """
    return sorted(x.split(" -> ")[0] if re.search(r"\d:\d\d:\d\d\.\d{3}", x)
                  else x for x in lines)


def plan(text):
    """The RECOGNISED PLAN a run prints: its rows, recordings and cameras.

    From its heading to the next heading in capitals; the two times of
    a camera's line below its file are left out, only the names count.
    """
    out, inside = [], False
    for line in text.splitlines():
        if line.strip() == vpm.T("RECOGNISED PLAN").strip() or \
                line.endswith(vpm.T("RECOGNISED PLAN").strip()):
            inside = True
            continue
        if inside and re.match(r"^[A-Z][A-Z .,:-]+$", line.strip()) \
                and not line.startswith(" "):
            break
        if inside and ("->" in line or "  (+" in line):
            out.append(" ".join(line.split()))
    return out


def recordings_in(lines):
    """The recordings a plan names, each as its row: file, (+n) blocks."""
    return [re.search(r"(\S+\.wav(?: \(\+\d+\))?)", x).group(1)
            for x in lines if ".wav" in x.split("->")[0]]


def tabs(window):
    """The window's sheets that stand, by the words on their tabs."""
    out = []
    for t in window.findChildren(QtWidgets.QTabWidget) if window else ():
        out += [t.tabText(i).replace("&&", "&").replace("✓", "")
                .strip() for i in range(t.count()) if t.isTabVisible(i)]
    return out


def button(window, text):
    """The window's button whose words begin with *text*."""
    for b in window.findChildren(QtWidgets.QPushButton):
        if b.text().replace("&", "").strip().startswith(text):
            return b


seen = {}
step = [0]


def answer(window):
    """Add the six, read the tables, give folder and type; "" when done."""
    if step[0] == 0:
        seen["fresh"] = tabs(window)
        button(window, vpm.T("Add files ...")[:9]).click()
        step[0] = 1
        return "the six added"
    if step[0] == 1:
        rows = ground.fields(window, vpm.T("Speaker name"))
        cams = [t for t in window.findChildren(QtWidgets.QTableWidget)
                if t.rowCount()]
        if len(rows) < 2 or not cams:
            return "the tables, %d recording rows so far" % len(rows)
        seen["rows"] = sorted(" ".join(r.split()) for r in rows)
        seen["cameras"] = sorted(
            t.item(r, 0).text() for t in cams for r in range(t.rowCount())
            if t.item(r, 0) is not None)
        button(window, vpm.T("Output folder ...")[:13]).click()
        for t in window.findChildren(QtWidgets.QTabWidget):
            t.setCurrentIndex(1)
        step[0] = 2
    return ""


print("1. The window as it opens, then the six files added")
kept = ground.window_answered_run(vpm, app, None, {}, answer,
                                  press="Dry run")
check("a fresh window shows the first sheet alone",
      len(seen.get("fresh") or []) == 1,
      "sheets standing before any file: %s, wanted only %r"
      % (seen.get("fresh"), vpm.T("Files && production").replace("&&", "&")))
check("the window's table holds two recordings, the blocks as one",
      seen.get("rows") == RECORDINGS,
      "rows %s, wanted %s" % (seen.get("rows"), RECORDINGS))
check("the window's camera table holds the three cameras",
      seen.get("cameras") == CAMERAS,
      "rows %s, wanted %s" % (seen.get("cameras"), CAMERAS))
said_window = "".join(kept["log"])
check("the window's dry run ran to its end, with a plan",
      kept["ended"] and not kept["why"] and "--dry-run" in (kept["argv"]
                                                           or [])
      and bool(plan(said_window)),
      "loop %s, %s, dry run %s, %d plan lines"
      % ("came back" if kept["ended"] else "never came back",
         kept["why"] or "nothing given up",
         "--dry-run" in (kept["argv"] or []), len(plan(said_window))))

print("\n2. The command line, a dry run over the same six")
code, said, stuck = ground.line_run(
    [sys.executable, SCRIPT, "--dry-run", "--without-auphonic",
     "--no-speech-recognition", "--out", os.path.join(WORK, "line")]
    + ADDED, STORE)
by_line = plan(said)
wrote = ground.written_names(os.path.join(WORK, "line"))
check("the line's dry run came back with 0, a plan, nothing written",
      not stuck and code == 0 and bool(by_line) and not wrote,
      "return code %s%s, %d plan lines, %d files written %s -- the log "
      "ends: %s"
      % (code, " after standing still" if stuck else "", len(by_line),
         len(wrote), wrote[:4], " / ".join(
             x.strip() for x in said.replace(WORK, "<work>").splitlines()
             if x.strip())[-200:]))
check("at the line, two recordings, the blocks as one",
      recordings_in(by_line) == RECORDINGS,
      "recordings %s, wanted %s -- the plan: %s"
      % (recordings_in(by_line), RECORDINGS, by_line))

print("\n3. The two doors against each other")
check("the window's dry run reads the recordings and cameras the line does",
      bool(by_line) and read_alike(plan(said_window)) == read_alike(by_line),
      "line %s -- window %s" % (by_line, plan(said_window)))

shutil.rmtree(WORK, ignore_errors=True)
shutil.rmtree(STORE, ignore_errors=True)
stop()
