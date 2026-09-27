# -*- coding: utf-8 -*-
"""Two recordings of one file name are told apart, as two cameras are.

Two recorders each wrote ZOOM0001.WAV, one in each folder. The rule
first, on paths alone: the second of one name is "(2)", a name of its
own stays whole. Then the preflight through collect_findings, the report
the window and the log both print: the facts line, the recording past
the first under Sync only, and the bleed between the two, measured by a
stand-in so only the naming is asked. Last the window: the file list's
row and the Assignment tab's row for each recording, and the speaker
name offered in grey there, the second guessed "(2)" as well.
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
from let_go import clean_up
SCRIPT = the_program.SCRIPT
import json, subprocess, tempfile, time, wave
import numpy as np
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


RATE = 48000
D = tempfile.mkdtemp(prefix="vpm_same_names_")
NAME = "ZOOM0001.WAV"


def recording(folder, hz):
    """Four seconds of a tone as *folder*/ZOOM0001.WAV."""
    os.makedirs(os.path.join(D, folder), exist_ok=True)
    path = os.path.join(D, folder, NAME)
    t = np.arange(4 * RATE) / float(RATE)
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes((0.4 * np.sin(2 * np.pi * hz * t) * 32767)
                      .astype("<i2").tobytes())
    return path


first = recording("RecorderA", 300.0)
second = recording("RecorderB", 700.0)
other = os.path.join(D, "RecorderB", "Guest.WAV")
vpm.shutil.copyfile(second, other)

print("1. The rule, on paths alone")
labels = vpm.recording_labels([first, second, other])
check("the first of two recordings of one name keeps its name",
      labels.get(first) == NAME, "named %r" % labels.get(first))
check("the second of one name is numbered (2)",
      labels.get(second) == NAME + " (2)", "named %r" % labels.get(second))
check("a recording whose name is its own stays whole",
      labels.get(other) == "Guest.WAV", "named %r" % labels.get(other))

print("\n2. The preflight report")
findings = vpm.collect_findings([first, second], [], fresh=True,
                                crosstalk=False, project_type="sync")
facts = dict((b.file, b.field) for b in findings
             if b.kind == "good" and b.file)
check("the facts lines of the two recordings differ",
      facts.get(first) == NAME and facts.get(second) == NAME + " (2)",
      "first %r, second %r" % (facts.get(first), facts.get(second)))
stops = [b for b in findings if b.kind == "abort"]
check("the recording past the first under Sync only is the (2)",
      len(stops) == 1 and stops[0].field == NAME + " (2)"
      and (NAME + " (2)") in stops[0].text,
      "%d reasons to stop: %s"
      % (len(stops), [(b.field, b.text) for b in stops]))
# The bleed is measured by a stand-in: the naming is the question here,
# not whether two tones share a room. Each heard in the other at 3 dB.
real_apart = vpm.check_crosstalk.__globals__["crosstalk_apart"]
vpm.check_crosstalk.__globals__["crosstalk_apart"] = \
    lambda *_a, **_k: ([(0, 1, 3.0), (1, 0, 3.0)], "")
try:
    bleed = [b.text for b in vpm.check_crosstalk(
        [first, second], labels=vpm.recording_labels([first, second]))
        if b.field == vpm.T('Bleed')]
finally:
    vpm.check_crosstalk.__globals__["crosstalk_apart"] = real_apart
check("the bleed between the two names them apart",
      len(bleed) == 2 and all("ZOOM0001 (2)" in x for x in bleed),
      "%d bleed lines: %s" % (len(bleed), bleed))

print("\n3. The window")
video = os.path.join(D, "WideCam.mov")
subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                "testsrc=size=160x90:rate=25:duration=4", "-c:v",
                "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                "-y", video], check=True)
project = os.path.join(D, "videopodcast-magic_Interview_2.json")
with open(project, "w", encoding="utf-8") as f:
    json.dump({"format": 3, "version": "test", "timeline": [],
               "files": [{"path": p, "kind": "audio"}
                         for p in (first, second)]
                        + [{"path": video, "kind": "video"}],
               "out_folder": os.path.join(D, "Ergebnis"),
               "production": "Names", "multitrack": False,
               "assignment": {}, "preset": ""}, f)
os.makedirs(os.path.join(D, "Ergebnis"), exist_ok=True)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (project, ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok


def drawn(text):
    """What ends up on the screen: & marks a key, && draws one &."""
    return str(text).replace("&&", "\x00").replace("&", "") \
                    .replace("\x00", "&")


def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def listed():
    """The captions under the AUDIO header of the file list, sorted."""
    top = win()
    if top is None:
        return []
    for t in top.findChildren(QtWidgets.QTreeWidget):
        root = t.invisibleRootItem()
        for i in range(root.childCount()):
            head = root.child(i)
            if head.text(0) == vpm.T('AUDIO'):
                return sorted(head.child(k).text(0).strip()
                              for k in range(head.childCount()))
    return []


def assigned():
    """The first column of the Assignment tab's recordings, sorted."""
    top = win()
    if top is None:
        return []
    want = drawn(vpm.T('Audio recording'))
    for view in top.findChildren(QtWidgets.QTreeView):
        model = view.model()
        if model is None or not model.columnCount() or isinstance(
                view, QtWidgets.QTreeWidget):
            continue
        if drawn(model.headerData(0, QtCore.Qt.Horizontal) or "") != want:
            continue
        return sorted(model.item(r, 0).text().split("\n")[0].strip()
                      for r in range(model.rowCount()))
    return []


def offered():
    """The grey speaker names in the Assignment tab's name column, sorted."""
    top = win()
    if top is None:
        return []
    want = drawn(vpm.T('Audio recording'))
    for view in top.findChildren(QtWidgets.QTreeView):
        model = view.model()
        if model is None or not model.columnCount() or isinstance(
                view, QtWidgets.QTreeWidget):
            continue
        if drawn(model.headerData(0, QtCore.Qt.Horizontal) or "") != want:
            continue
        out = []
        for r in range(model.rowCount()):
            cell = view.indexWidget(model.index(r, 1))
            fields = [] if cell is None else (
                [cell] if isinstance(cell, QtWidgets.QLineEdit) else
                cell.findChildren(QtWidgets.QLineEdit))
            out.append(fields[0].placeholderText() if fields else "")
        return sorted(out)
    return []


def tab_to(word):
    for bar in win().findChildren(QtWidgets.QTabWidget):
        for k in range(bar.count()):
            if word.lower() in drawn(bar.tabText(k)).lower():
                bar.setCurrentIndex(k)
                app.processEvents()
                return True
    return False


def button(text):
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(text):
            return w


WANT = [NAME, NAME + " (2)"]
n = [0]
waited = [0]
seen = {}


def step():
    """Open the project, then wait on each sheet for its two rows."""
    i = n[0]
    try:
        if i == 0:
            win().show(); win().resize(1300, 800); app.processEvents()
            button(drawn(vpm.T('Open project'))).click()
            n[0] += 1
        elif i == 1:
            # Waiting for the list to hold both, patient enough for a
            # slow builder; what it holds when patience ends is judged.
            if len(listed()) < 2 and waited[0] < 400:
                waited[0] += 1
            else:
                seen["list"] = listed()
                waited[0] = 0
                tab_to(drawn(vpm.T('Assignment')))
                n[0] += 1
        elif i == 2:
            if len(assigned()) < 2 and waited[0] < 400:
                waited[0] += 1
            else:
                seen["assigned"] = assigned()
                seen["offered"] = offered()
                app.quit()
                return
    except Exception:
        import traceback; traceback.print_exc(); app.quit(); return
    QtCore.QTimer.singleShot(25, step)


QtCore.QTimer.singleShot(0, step)
QtCore.QTimer.singleShot(120000, app.quit)
sys.argv = ["videopodcast_magic.py"]
vpm.gui()
check("the file list names the two recordings apart",
      seen.get("list") == WANT,
      "rows %r, wanted %r" % (seen.get("list"), WANT))
check("and the Assignment tab names them as the list does",
      seen.get("assigned") == WANT,
      "rows %r, wanted %r" % (seen.get("assigned"), WANT))
check("and offers two speakers there, the second guessed (2)",
      seen.get("offered") == ["ZOOM", "ZOOM (2)"],
      "grey names %r, wanted ['ZOOM', 'ZOOM (2)']" % (seen.get("offered"),))

clean_up(D)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
