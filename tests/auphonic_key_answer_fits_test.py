# -*- coding: utf-8 -*-
"""What comes back is said about the key that went out, not another.

Two ways the window talked about a key other than the one it had used.
The answer from auphonic.com arrives in a signal, and what to do with
it was read off the field a second time -- so a key pasted while the
first check was running went into the store while a different one had
been checked, and the button went green over it. And the complaint
about a key that was refused named the store, although the environment
is read first and wins.

The sections: the origin of a key and the sentence that names it, both
without a window; then the window itself -- the refusal at start-up
names where its key came from, and a second key typed during a check
does not become the one that is kept.

Nothing here goes to auphonic.com: the fetch is replaced, and the key
store with it, so nothing real is ever read or written.
"""
import os
import sys
import time
import importlib.util
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
# The window is built with a key in the environment: that is the case
# the second section is about, and it decides what the window starts
# with, so it has to stand before the module is read.
FROM_ENV = "env-key-77777"
os.environ["AUPHONIC_TOKEN"] = FROM_ENV

from PySide6 import QtWidgets, QtCore
from PySide6.QtTest import QTest

app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.set_language("en")
# Before anything can reach the credential store: all three names of
# it go somewhere throwaway. On a Mac the two keychain names decide,
# and REG_PATH alone moved nothing there.
import key_store_apart
key_store_apart.apart(vpm)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def finish():
    """The one way out: the count, the verdict, the return code."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


REFUSED = "403: Token doesn't exist"
FIRST = "first-key-11111"
SECOND = "second-key-22222"
IN_STORE = "stored-key-33333"
# How long an answer may take to come back. Far above what a replaced
# fetch needs, short enough that a wiring that never fires does not
# hold the suite.
PATIENCE = 30.0
POLL = 0.02

# ---------------------------------------------------- the key store, replaced
# At least as strict as the real one: it takes only what it is given
# and hands back what it holds, and nothing outside this process is
# ever touched.
kept = [""]
stored = []


def store_stand_in(key):
    stored.append(key)
    kept[0] = key
    return True


vpm.load_api_key = lambda: kept[0]
vpm.store_api_key = store_stand_in
vpm.delete_api_key = lambda: kept.__setitem__(0, "")

# ------------------------------------------------------ the fetch, replaced
asked = []
hold = threading.Event()
hold.set()
answer = {"raise": True}


def fetch_stand_in(key):
    asked.append(key)
    hold.wait(PATIENCE)
    if answer["raise"]:
        raise RuntimeError(REFUSED)
    return [("Podcast_Multitrack", "u1", True)]


vpm.list_presets = fetch_stand_in
vpm.update_offer = lambda *a, **k: None

print("1. Where a key came from, and the sentence that names it")
key, origin = vpm.api_key_source()
check("a key in the environment is the one that goes out",
      (key, origin) == (FROM_ENV, "environment"),
      "%r from %r, wanted the environment" % (key, origin))
kept[0] = IN_STORE
key, origin = vpm.api_key_source()
check("and it beats one lying in the store",
      (key, origin) == (FROM_ENV, "environment"),
      "%r from %r while the store holds %r" % (key, origin, IN_STORE))
del os.environ["AUPHONIC_TOKEN"]
key, origin = vpm.api_key_source()
os.environ["AUPHONIC_TOKEN"] = FROM_ENV
check("without one in the environment the store answers",
      (key, origin) == (IN_STORE, "store"),
      "%r from %r, wanted the store" % (key, origin))
kept[0] = ""
check("the complaint about an environment key names the environment",
      vpm.key_refused_note("environment", REFUSED)
      == vpm.T('The key from AUPHONIC_TOKEN is not accepted: %s') % REFUSED,
      "%r" % vpm.key_refused_note("environment", REFUSED))
check("the complaint about a stored key names the store",
      vpm.key_refused_note("store", REFUSED)
      == vpm.T('The stored key is not accepted: %s') % REFUSED,
      "%r" % vpm.key_refused_note("store", REFUSED))
check("and the two complaints are not the same sentence",
      vpm.key_refused_note("environment", REFUSED)
      != vpm.key_refused_note("store", REFUSED),
      "%r" % vpm.key_refused_note("store", REFUSED))


# ------------------------------------------------------- reading the window
def drawn(text):
    """What ends up on the screen: & marks a key, && draws one &."""
    return str(text).replace("&&", "\x00").replace("&", "") \
                    .replace("\x00", "&")


def among(kind):
    """Every widget of that kind the program built.

    Not the children of the main window: the key and its tick live in
    a settings window of their own, and the preset list hangs on a
    page the tab bar only adopts once there are files.
    """
    return [w for w in app.allWidgets() if isinstance(w, kind)]


def key_field():
    """The field the key is typed into: the one that hides what it holds."""
    for w in among(QtWidgets.QLineEdit):
        if w.echoMode() == QtWidgets.QLineEdit.Password:
            return w
    return None


def button_named(text):
    for b in among(QtWidgets.QPushButton):
        if drawn(b.text()).strip() == text:
            return b
    return None


def keep_box():
    """The tick that says the key is to be kept, whatever it is called."""
    said = {vpm.T('Save in Keychain'), vpm.T('Save in Registry'),
            vpm.T('Keep it saved')}
    for b in among(QtWidgets.QCheckBox):
        if drawn(b.text()).strip() in said:
            return b
    return None


def preset_box():
    """The preset list: the one holding the no-Auphonic entry."""
    for b in among(QtWidgets.QComboBox):
        for i in range(b.count()):
            if b.itemData(i) == vpm.PRESET_NONE:
                return b
    return None


def note_shown():
    """The sentence the window is showing about the key, or ""."""
    heads = [vpm.T('The key from AUPHONIC_TOKEN is not accepted: %s'),
             vpm.T('The stored key is not accepted: %s'),
             vpm.T('auphonic.com does not accept the key: %s')]
    heads = [h.replace("%s", "").strip() for h in heads]
    for x in among(QtWidgets.QLabel):
        said = drawn(x.text()).strip()
        if any(said.startswith(h) for h in heads):
            return said
    return ""


def waited_for(condition, why):
    """Wait on a condition, never on the clock; returns how long it took."""
    began_here = time.time()
    while time.time() - began_here < PATIENCE:
        app.processEvents()
        if condition():
            return time.time() - began_here
        time.sleep(POLL)
    print("      gave up after %.1f s waiting for %s" % (PATIENCE, why))
    return None


def type_in(field, text):
    """Type into a field letter by letter, as somebody at the screen does."""
    field.setFocus()
    field.selectAll()
    QTest.keyClicks(field, text)
    QTest.keyClick(field, QtCore.Qt.Key_Return)
    app.processEvents()


def drive():
    box = preset_box()
    field = key_field()
    # Held on to now: the button says "checking ..." while a check is
    # running, and looking for it by its caption then finds nothing --
    # which ends the test in a traceback instead of a verdict.
    connect = button_named(vpm.T('Connect'))
    if box is None or field is None or connect is None:
        check("the window came up with its key field, list and button",
              False, "field %r, list %r, button %r" % (field, box, connect))
        app.quit()
        return
    check("the window came up with its key field, list and button",
          True, "the field holds %d characters" % len(field.text()))
    check("and it starts on the key out of the environment",
          field.text() == FROM_ENV,
          "%r against %r" % (field.text(), FROM_ENV))

    print("\n2. The refusal at start-up names where the key came from")
    # Opening the list is what asks auphonic.com -- the start-up try,
    # with a key nobody typed.
    box.showPopup()
    box.hidePopup()
    took = waited_for(lambda: note_shown() != "", "the refusal")
    said = note_shown()
    check("auphonic.com was asked with the key from the environment",
          asked[:1] == [FROM_ENV],
          "asked with %r after %s s" % (asked[:1], took))
    check("and the refusal names AUPHONIC_TOKEN, not the store",
          said == vpm.key_refused_note("environment", REFUSED),
          "%r against %r" % (said, vpm.key_refused_note("environment",
                                                        REFUSED)))

    print("\n3. A second key typed while the first is being checked")
    answer["raise"] = False
    hold.clear()
    tick = keep_box()
    if tick is None or not tick.isEnabled():
        check("ticking the box puts the key of the moment into the store",
              False, "no tick found on this platform")
        app.quit()
        return
    # Ticked while the key of the environment still stands there, so
    # what the tick stores and what the answer stores can be told
    # apart. With both storing the same key the last check below would
    # be green whether the answer ever stored anything or not.
    tick.setChecked(True)
    app.processEvents()
    check("ticking the box puts the key of the moment into the store",
          tick.isChecked() and stored[-1:] == [FROM_ENV],
          "the store holds %r after %d put(s)" % (stored[-1:], len(stored)))
    type_in(field, FIRST)
    was_asked, was_kept = len(asked), len(stored)
    connect.click()
    took = waited_for(lambda: len(asked) > was_asked, "the check to go out")
    check("the check really goes out", took is not None,
          "%d call(s) before, %d after, waited %s s"
          % (was_asked, len(asked), took))
    check("and it goes out with the key that stood in the field",
          asked[-1:] == [FIRST],
          "went out with %r, wanted %r" % (asked[-1:], FIRST))
    # And now the second paste, while the answer is still on its way.
    type_in(field, SECOND)
    check("a second key can be typed while the first is still running",
          field.text() == SECOND and len(stored) == was_kept,
          "the field says %r and the store has had %d put(s)"
          % (field.text(), len(stored) - was_kept))
    hold.set()
    took = waited_for(lambda: len(stored) > was_kept,
                      "the answer to reach the store")
    check("the answer really reaches the store", took is not None,
          "%d put(s) before, %d after, waited %s s"
          % (was_kept, len(stored), took))
    check("what is kept is the key that was checked, not the field",
          stored[-1:] == [FIRST],
          "kept %r while the field said %r" % (stored[-1:], field.text()))
    app.quit()


QtCore.QTimer.singleShot(2500, drive)
QtCore.QTimer.singleShot(90000, app.quit)
sys.argv = ["videopodcast-magic.py"]
vpm.gui()
os.environ.pop("AUPHONIC_TOKEN", None)
finish()
