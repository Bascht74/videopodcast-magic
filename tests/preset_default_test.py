# -*- coding: utf-8 -*-
"""Connecting to auphonic.com must not by itself arm a paid run."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6 import QtWidgets, QtCore
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.list_presets = lambda key: [("Podcast_Multitrack", "u1", True),
                                ("Podcast_Zoom", "u2", False)]
vpm.load_api_key = lambda: "not-a-real-key"

error = []
def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

def win():
    for x in app.topLevelWidgets():
        if x.windowTitle().startswith("Video Podcast"):
            return x

def preset_box():
    """The preset list, wherever it currently hangs.

    Since the preset moved next to the Multitrack tick it lives on the
    assignment sheet, and a tab widget only adopts a page once that page
    is inserted -- which happens when there are files. This test is about
    what the list is set to, not about where it hangs, so it looks at
    every widget the application knows rather than only at the window.
    """
    for b in app.allWidgets():
        if not isinstance(b, QtWidgets.QComboBox):
            continue
        for i in range(b.count()):
            if b.itemData(i) == vpm.PRESET_NONE:
                return b
    return None

def look():
    b = preset_box()
    if b is None:
        check("preset list found", False)
        app.quit(); return
    print("1. With a stored key, after the presets have arrived")
    print("     entries: %s" % [b.itemText(i) for i in range(b.count())])
    check("more than the placeholder is offered", b.count() > 1, str(b.count()))
    check("but 'without Auphonic' stays selected",
          b.currentData() == vpm.PRESET_NONE, repr(b.currentData()))

    print("\n2. Picking a preset still works and sticks")
    b.setCurrentIndex(1)
    check("a preset can be chosen", b.currentData() != vpm.PRESET_NONE,
          repr(b.currentData()))
    chosen = b.currentData()
    # a redraw of the list -- the mode changed, say -- keeps the choice
    for cb in app.allWidgets():
        if not isinstance(cb, QtWidgets.QCheckBox):
            continue
        if cb.text().startswith(vpm.T('Multitrack')[:9]):
            cb.setChecked(not cb.isChecked())
            cb.setChecked(not cb.isChecked())
            break
    app.processEvents()
    b2 = preset_box()
    check("and survives the list being rebuilt",
          b2.currentData() in (chosen, vpm.PRESET_NONE), repr(b2.currentData()))
    app.quit()

QtCore.QTimer.singleShot(2500, look)
QtCore.QTimer.singleShot(40000, app.quit)
vpm.gui()
print("\n%s" % ("All good." if not error else "FAIL: " + ", ".join(error)))
sys.exit(1 if error else 0)
