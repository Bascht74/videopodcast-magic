# -*- coding: utf-8 -*-
"""Why the start button is grey, and where that is said.

A greyed button with no reason is the commonest dead end in an
interface. Three things are checked here: the reason stands in the
footer where it can be read without hovering, the missing production
name is marked red in its own field like every other faulty entry, and
the reason names the tabs by the names they actually carry, read off the
tabs rather than from a second list beside them.

The fourth is the intro: two files set to intro would both be written
into the same switch, so the second choice frees the first.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, json, shutil, subprocess, sys, tempfile, wave
import numpy as np
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""

error = []


def check(name, ok, extra=""):
    print("  %-54s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


RATE, SEC = 48000, 4
folder = tempfile.mkdtemp(prefix="vpm_reason_")


def tone(name, hz):
    path = os.path.join(folder, name)
    t = np.arange(SEC * RATE) / float(RATE)
    x = (0.4 * np.sin(2 * np.pi * hz * t) * 32767).astype("<i2")
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes(x.tobytes())
    return path


def clip(name):
    path = os.path.join(folder, name)
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                    "testsrc=size=160x90:rate=25:duration=%d" % SEC,
                    "-f", "lavfi", "-i",
                    "sine=frequency=300:duration=%d" % SEC,
                    "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
                    "yuv420p", "-c:a", "aac", "-shortest", "-y", path],
                   check=True)
    return path


audio = tone("A_speaker.wav", 300)
one, two = clip("B_camera.mov"), clip("C_camera.mov")
project = os.path.join(folder, "videopodcast-magic_Interview_2.json")
with open(project, "w", encoding="utf-8") as f:
    json.dump({"format": 3, "version": "test", "timeline": [], "call": [],
               "files": [{"path": audio, "kind": "audio"},
                         {"path": one, "kind": "video"},
                         {"path": two, "kind": "video"}],
               "out_folder": os.path.join(folder, "Ergebnis"),
               "production": "Reason", "multitrack": False,
               "assignment": {}, "preset": ""}, f)
os.makedirs(os.path.join(folder, "Ergebnis"), exist_ok=True)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (project, ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted


def win():
    for x in app.topLevelWidgets():
        if x.windowTitle().startswith("Video Podcast"):
            return x


def button(word):
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(word):
            return w


def name_field():
    """The production name: the only field 340 wide."""
    for w in win().findChildren(QtWidgets.QLineEdit):
        if w.width() == 340 or w.maximumWidth() == 340:
            return w


def footer_note():
    """The word-wrapped label left of the start button."""
    for w in win().findChildren(QtWidgets.QLabel):
        if w.wordWrap() and w.maximumWidth() == 430:
            return w


def tab_bar():
    for tw in win().findChildren(QtWidgets.QTabWidget):
        if tw.count() >= 2:
            return tw


def tab_titles():
    tw = tab_bar()
    return [tw.tabText(k) for k in range(tw.count())]


def kind_boxes():
    """The type selectors in the camera table -- one per video file."""
    out = []
    for box in win().findChildren(QtWidgets.QComboBox):
        values = [box.itemData(i) for i in range(box.count())]
        if vpm.TYPE_INTRO in values:
            out.append(box)
    return out


def pick(box, value):
    for i in range(box.count()):
        if box.itemData(i) == value:
            box.setCurrentIndex(i)
            app.processEvents()
            return True
    return False


n = [0]
waited = [0]


def step():
    i = n[0]; n[0] += 1
    try:
        if i == 0:
            win().show(); win().resize(1400, 900); app.processEvents()
            button("Open project").click()
        elif i == 1:
            if name_field() is None and waited[0] < 60:
                waited[0] += 1; n[0] = 1
                QtCore.QTimer.singleShot(500, step); return
            field = name_field()
            check("the production name field is there", field is not None)
            print("\n1. A name is there: nothing outstanding")
            check("no reason in the footer",
                  not footer_note().isVisible(),
                  repr(footer_note().text()))
            check("and the field is not marked",
                  "border" not in (field.styleSheet() or ""),
                  repr(field.styleSheet()))
            print("\n2. The name taken away")
            field.setText("")
            app.processEvents()
            note = footer_note()
            check("the reason stands in the footer, not only in a hint",
                  note.isVisible() and bool(note.text().strip()),
                  repr(note.text()))
            # The footer no longer names the reason once something is
            # chosen: it points at the tooltip, which carries the whole
            # list. What names this reason is the red field below.
            check("and it points at the tooltip",
                  "tooltip" in note.text().lower(), repr(note.text()))
            check("the field itself is marked red",
                  "border" in (field.styleSheet() or ""),
                  repr(field.styleSheet()))
            check("the field says why when hovered",
                  bool(field.toolTip().strip()), repr(field.toolTip()))
            check("start is grey", not button("Start").isEnabled())
            print("\n3. The reason names the tabs that exist")
            hint = ""
            for w in win().findChildren(QtWidgets.QWidget):
                if button("Start") in w.findChildren(QtWidgets.QPushButton) \
                        and w.toolTip().startswith("Not ready"):
                    hint = w.toolTip()
            check("the hint lists what is missing", bool(hint), repr(hint))
            titles = [t.replace("&&", "&").replace("✓", "").strip()
                      for t in tab_titles()]
            named = [line.split(" -- ")[0].strip()
                     for line in hint.splitlines() if " -- " in line]
            check("every name in it is a tab that exists",
                  bool(named) and all(x in titles for x in named),
                  "%s vs %s" % (named, titles))
            check("no page number from an older layout",
                  not any(x.startswith("2.") for x in named), str(named))
            print("\n4. The tick sits on the tabs that can be complete")
            check("no tick while the name is missing",
                  "✓" not in tab_titles()[0], str(tab_titles()))
            field.setText("Reason")
            app.processEvents()
            check("and it comes back with the name",
                  "✓" in tab_titles()[0], str(tab_titles()))
            check("start is live again", button("Start").isEnabled())
            check("the footer is quiet again",
                  not footer_note().isVisible(), repr(footer_note().text()))
            resolve = [t for t in tab_titles() if "Resolve" in t]
            check("the Resolve tab carries no tick it cannot lose",
                  resolve and "✓" not in resolve[0], str(resolve))
            print("\n5. Only one file can be the intro")
            boxes = kind_boxes()
            check("two video files, two selectors", len(boxes) == 2,
                  str(len(boxes)))
            pick(boxes[0], vpm.TYPE_INTRO)
            n[0] = 2
            QtCore.QTimer.singleShot(1500, step)
            return
        elif i == 2:
            boxes = kind_boxes()
            kinds = [b.currentData() for b in boxes]
            check("the first one is the intro",
                  kinds.count(vpm.TYPE_INTRO) == 1, str(kinds))
            pick(boxes[1], vpm.TYPE_INTRO)
            n[0] = 3
            QtCore.QTimer.singleShot(1500, step)
            return
        elif i == 3:
            kinds = [b.currentData() for b in kind_boxes()]
            check("the second choice frees the first",
                  kinds.count(vpm.TYPE_INTRO) == 1, str(kinds))
            check("and the first one is content again",
                  kinds[0] == vpm.TYPE_CONTENT, str(kinds))
            print("\n%s" % ("ALL OK" if not error
                            else "FAIL: " + ", ".join(error)))
            app.quit(); return
    except Exception:
        import traceback; traceback.print_exc()
        error.append("crash"); app.quit(); return
    QtCore.QTimer.singleShot(1200, step)


QtCore.QTimer.singleShot(700, step)
QtCore.QTimer.singleShot(180000, app.quit)
sys.argv = ["videopodcast-magic.py"]
vpm.gui()
shutil.rmtree(folder, ignore_errors=True)
sys.exit(1 if error else 0)
