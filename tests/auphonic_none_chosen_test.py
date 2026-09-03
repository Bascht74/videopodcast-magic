# -*- coding: utf-8 -*-
"""Connecting to auphonic.com must not by itself arm a paid run."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import importlib.util, sys, time
began = time.time()

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6 import QtWidgets, QtCore
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
# Before the window comes up: all three names of the credential store
# go somewhere throwaway. Measured on 2.9.2026 -- this file is the one
# that wrote "not-a-real-key" into the real keychain. The reading below
# is stood in for, the writing was not, and starting the window saves
# what it read; on a Mac the two keychain names stood in the program
# where they were used, so nothing here could redirect them.
import key_store_apart                                      # noqa: E402
key_store_apart.apart(vpm)
vpm.list_presets = lambda key: [("Podcast_Multitrack", "u1", True),
                                ("Podcast_Zoom", "u2", False)]
vpm.load_api_key = lambda: "not-a-real-key"

done = 0
error = []
def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x

def preset_box():
    """The preset list, wherever it currently hangs.

    A tab widget adopts a page only once that page is inserted, which
    happens when there are files. What matters here is what the list is
    set to, not where it hangs.
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
        boxes = [w for w in app.allWidgets()
                 if isinstance(w, QtWidgets.QComboBox)]
        check("preset list found", False,
              "no list held PRESET_NONE: %d lists on screen, "
              "with %s entries" % (len(boxes),
                                   [w.count() for w in boxes][:10]))
        app.quit(); return
    # Opening the list is what asks the service: a start must not speak
    # to a third party about a key it was only asked to keep. So the
    # list is opened here, the way somebody would.
    b.showPopup()
    b.hidePopup()
    # The fetch runs in a thread, so the list is not full the moment the
    # popup closes. Waited for, not slept through: on a busy machine a
    # fixed pause is either too short or wasted.
    import time
    until = time.time() + 20.0
    while b.count() < 2 and time.time() < until:
        app.processEvents()
        time.sleep(0.02)
    print("     waited %.1f s for the list" % (20.0 - (until - time.time())))

    print("1. With a stored key, after the list has been opened once")
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
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("\n%s" % ("All good." if not error else "FAIL: " + ", ".join(error)))
sys.exit(1 if error else 0)
