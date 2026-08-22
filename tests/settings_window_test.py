# -*- coding: utf-8 -*-
"""What is set up once, and what is decided every time.

Two sorts of setting used to stand in one box on the first sheet: the
key for auphonic.com, which is entered once in a lifetime, and the
preset, which belongs to the production being made. Choosing a preset
therefore meant paging back from the table where the decision is
actually made. They are apart now -- the key and the Resolve check
behind "Settings ...", the preset under the assignment table -- and this
test holds them to it.
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
folder = tempfile.mkdtemp(prefix="vpm_settings_")


def tone(name, hz):
    path = os.path.join(folder, name)
    t = np.arange(SEC * RATE) / float(RATE)
    x = (0.4 * np.sin(2 * np.pi * hz * t) * 32767).astype("<i2")
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes(x.tobytes())
    return path


one, two = tone("A_speaker.wav", 300), tone("B_speaker.wav", 900)
project = os.path.join(folder, "videopodcast-magic_Interview_2.json")
with open(project, "w", encoding="utf-8") as f:
    json.dump({"format": 3, "version": "test", "timeline": [], "call": [],
               "files": [{"path": one, "kind": "audio"},
                         {"path": two, "kind": "audio"}],
               "out_folder": os.path.join(folder, "Ergebnis"),
               "production": "Settings", "multitrack": True,
               "assignment": {}, "preset": ""}, f)
os.makedirs(os.path.join(folder, "Ergebnis"), exist_ok=True)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (project, ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted


def win():
    for x in app.topLevelWidgets():
        if x.windowTitle().startswith("Video Podcast"):
            return x


def boxes(where):
    return [g.title() for g in where.findChildren(QtWidgets.QGroupBox)
            if g.isVisible()]


def button(word, where=None):
    for w in (where or win()).findChildren(QtWidgets.QPushButton):
        if word.lower() in w.text().lower():
            return w


def dialogs():
    return [d for d in app.topLevelWidgets()
            if isinstance(d, QtWidgets.QDialog) and d.isVisible()]


def tab(word):
    for tw in win().findChildren(QtWidgets.QTabWidget):
        for k in range(tw.count()):
            if word.lower() in tw.tabText(k).lower():
                tw.setCurrentIndex(k)
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
            if not tab("Assignment") and waited[0] < 40:
                waited[0] += 1; n[0] = 1
                QtCore.QTimer.singleShot(500, step); return
            print("\n1. The first sheet holds no access data any more")
            tab("Files")
            here = boxes(win())
            check("no key box on the first sheet",
                  not any("auphonic.com" in b and "Access" in b
                          for b in here), str(here))
            check("the production box is still there",
                  any("Produktion" in b or "Production" in b for b in here),
                  str(here))
            print("\n2. The preset stands where the tracks are decided")
            tab("Assignment")
            here = boxes(win())
            check("the auphonic box is on the assignment sheet",
                  any("auphonic.com" in b for b in here), str(here))
            found = None
            for c in win().findChildren(QtWidgets.QComboBox):
                if c.isVisible() and any(
                        c.itemData(k) == vpm.PRESET_NONE
                        for k in range(c.count())):
                    found = c
            check("and the preset list is one of its fields", found is not None)
            names = [w.text() for w in win().findChildren(QtWidgets.QCheckBox)
                     if w.isVisible()]
            check("the transcript tick came with it",
                  any("ranskri" in x or "ranscript" in x for x in names),
                  str(names))
            check("beside the multitrack tick",
                  any("ulti" in x for x in names), str(names))
            print("\n3. Settings: one window, opened on purpose")
            b = button("Settings")
            check("the button is there", b is not None)
            check("and no window is open yet", not dialogs())
            b.click(); app.processEvents()
            d = dialogs()
            check("it opens one", len(d) == 1, str(len(d)))
            if d:
                inside = [g.title() for g in
                          d[0].findChildren(QtWidgets.QGroupBox)]
                check("holding the key", any("Access" in x or "Zugang" in x
                                             for x in inside), str(inside))
                check("and the Resolve check",
                      any("Resolve" in x for x in inside), str(inside))
                check("with a field for the key",
                      len(d[0].findChildren(QtWidgets.QLineEdit)) >= 1)
                check("a Connect button", button("Connect", d[0]) is not None)
                check("and a way out", button("Close", d[0]) is not None)
                button("Close", d[0]).click(); app.processEvents()
                check("which closes it", not dialogs())
            print("\n%s" % ("ALL OK" if not error
                            else "FAIL: " + ", ".join(error)))
            app.quit(); return
    except Exception:
        import traceback; traceback.print_exc()
        error.append("crash"); app.quit(); return
    QtCore.QTimer.singleShot(1200, step)


QtCore.QTimer.singleShot(700, step)
QtCore.QTimer.singleShot(120000, app.quit)
sys.argv = ["videopodcast-magic.py"]
vpm.gui()
shutil.rmtree(folder, ignore_errors=True)
sys.exit(1 if error else 0)
