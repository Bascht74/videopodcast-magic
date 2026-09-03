# -*- coding: utf-8 -*-
"""Shot of the Auphonic box: the list entry instead of the checkbox."""
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtWidgets, QtCore
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
# No account is asked for here: the preset list and the key come from
# these two stubs, under the names the program uses today.
vpm.list_presets = lambda key: [
    ("Podcast_Zoom", "u1", False),
    ("Podcast_Multitrack", "u2", True)]
vpm.load_api_key = lambda: "secret"
OUT = os.environ.get("VPM_SHOTS") or os.path.join(HERE, "shots")
os.makedirs(OUT, exist_ok=True)

def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x

def group(title):
    """The box of this name, over every widget rather than one window.

    A box on the assignment sheet hangs off no window until files are
    loaded. Searching the window alone finds nothing, and a shot that
    finds nothing leaves quietly and counts as passed.
    """
    for w in win().findChildren(QtWidgets.QGroupBox):
        if w.title().startswith(title):
            return w
    for w in app.allWidgets():
        if isinstance(w, QtWidgets.QGroupBox) and w.title().startswith(title):
            return w

def button(text):
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(text):
            return w
    for w in app.allWidgets():
        if (isinstance(w, QtWidgets.QPushButton)
                and w.text().strip().startswith(text)):
            return w

def preset_box():
    """The preset list, wherever it hangs -- see group()."""
    seen = list(win().findChildren(QtWidgets.QComboBox))
    seen += [w for w in app.allWidgets()
             if isinstance(w, QtWidgets.QComboBox) and w not in seen]
    for w in seen:
        for i in range(w.count()):
            if w.itemText(i) == vpm.label_of(vpm.PRESET_NONE):
                return w
    return None

error = []
n = [0]
def step():
    i = n[0]; n[0] += 1
    try:
        if i == 0:
            win().show(); app.processEvents()
        elif i == 1:
            g = group(vpm.T('Processing at auphonic.com (optional)'))
            if g is None:
                # Loudly, and with a code of its own: leaving quietly
                # here would report a shot that never happened as good.
                print("FAIL: the auphonic.com box was not found")
                for w in app.allWidgets():
                    if isinstance(w, QtWidgets.QGroupBox):
                        print("  Group:", w.title())
                error.append("box"); app.quit(); return
            n.append(g)
            b = preset_box()
            print("1. Unchecked:", [b.itemText(j) for j in range(b.count())],
                  "| chosen:", repr(b.currentText()),
                  "| enabled:", b.isEnabled())
            g.grab().save(OUT + "/1_unchecked.png")
        elif i == 2:
            button(vpm.T('Connect')).click()
        elif i == 4:
            g = n[-1]; b = preset_box()
            print("2. Checked:", [b.itemText(j) for j in range(b.count())],
                  "| chosen:", repr(b.currentText()))
            g.grab().save(OUT + "/2_checked.png")
            b.setCurrentText(vpm.label_of(vpm.PRESET_NONE))
            app.processEvents()
            multitrack = vpm.T('Multitrack (one track per speaker)')
            # Without files the assignment sheet is in no window yet, so
            # the tick is found over every widget rather than over one.
            multi = [w for w in app.allWidgets()
                     if isinstance(w, QtWidgets.QCheckBox)
                     and w.text().startswith(multitrack)][0]
            print("3. Entry chosen:", repr(b.currentText()),
                  "| Multitrack on:", multi.isChecked(),
                  "| enabled:", multi.isEnabled())
            g.grab().save(OUT + "/3_without_auphonic.png")
            print("\ndone"); app.quit(); return
    except Exception as e:
        import traceback; traceback.print_exc(); app.quit(); return
    QtCore.QTimer.singleShot(1200, step)

QtCore.QTimer.singleShot(1000, step)
QtCore.QTimer.singleShot(45000, app.quit)
sys.argv = ["videopodcast_magic.py"]
vpm.gui()
sys.exit(1 if error else 0)
