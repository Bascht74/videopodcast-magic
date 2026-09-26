# -*- coding: utf-8 -*-
"""What comes back is said about the key that went out, not another.

Two ways the window talked about a key other than the one it had used.
The answer from auphonic.com arrives in a signal, and what to do with
it was read off the field a second time -- so a key pasted while the
first check was running went into the store while a different one had
been checked, and the button went green over it. And the complaint
about a refused key has to name the place that key came from.

The sections: the origin of a key, a run's too -- the window's
hand-over or the store, none with --without-auphonic, and AUPHONIC_TOKEN
no longer read at all -- and the sentence that names it, both without
a window; then the window itself -- the refusal at start-up names the
store its key came from, and a second key typed during a check does
not become the one kept.

Nothing here goes to auphonic.com: the fetch is replaced, and the key
store with it, so nothing real is ever read or written.
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
import time
import types
import threading
import the_program

SCRIPT = the_program.SCRIPT

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
# A made-up key in the variable the program once read, set before the
# module is read: nothing may take it up any more, at start or later.
FROM_ENV = "FAKEKEY-0000"
os.environ["AUPHONIC_TOKEN"] = FROM_ENV

from PySide6 import QtWidgets, QtCore
from PySide6.QtTest import QTest

app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
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
check("AUPHONIC_TOKEN alone gives no key at all",
      (key, origin) == ("", ""),
      "%d characters from %r, wanted none" % (len(key), origin))
bare = types.SimpleNamespace(without_auphonic=False)
vpm.key_for_run(bare)
check("and a run finds none in it either",
      bare.auphonic_key is None,
      "%r from %r, wanted None" % (bare.auphonic_key, bare.auphonic_key_from))
kept[0] = IN_STORE
key, origin = vpm.api_key_source()
check("the stored key is the one that goes out",
      (key, origin) == (IN_STORE, "store"),
      "%d characters from %r, wanted the store's %d"
      % (len(key), origin, len(IN_STORE)))
key, origin = vpm.api_key_source(handed=FIRST)
check("the window's hand-over beats the store",
      (key, origin) == (FIRST, "window"),
      "%r from %r, wanted %r from the window" % (key, origin, FIRST))
# A run handed the stored key by main(): a refusal in the middle of it
# has to name the store, not the window that never held a key.
run = types.SimpleNamespace(without_auphonic=False)
vpm.key_for_run(run)
run_key, run_origin = vpm.api_key_source(run)
check("a run's key out of the store is named so",
      (run_key, run_origin) == (IN_STORE, "store"),
      "%r from %r, wanted the store" % (run_key, run_origin))
check("the complaint about a stored key names the store",
      vpm.key_refused_note("store", REFUSED)
      == vpm.T('The stored key is not accepted: %s') % REFUSED,
      "%r" % vpm.key_refused_note("store", REFUSED))
check("the complaint about a typed key names auphonic.com alone",
      vpm.key_refused_note("window", REFUSED)
      == vpm.T('auphonic.com does not accept the key: %s') % REFUSED,
      "%r" % vpm.key_refused_note("window", REFUSED))
held_back = types.SimpleNamespace(without_auphonic=True)
vpm.key_for_run(held_back)
check("--without-auphonic takes no key although one is stored",
      held_back.auphonic_key is None,
      "the run holds %s" % ("no key" if held_back.auphonic_key is None
                            else "a key from %r" % held_back.auphonic_key_from))


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
    heads = [vpm.T('The stored key is not accepted: %s'),
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
    check("and it starts on the stored key",
          field.text() == IN_STORE,
          "%d characters against the store's %d"
          % (len(field.text()), len(IN_STORE)))

    print("\n2. The refusal at start-up names where the key came from")
    # Opening the list is what asks auphonic.com -- the start-up try,
    # with a key nobody typed.
    box.showPopup()
    box.hidePopup()
    took = waited_for(lambda: note_shown() != "", "the refusal")
    said = note_shown()
    check("auphonic.com was asked with the stored key",
          asked[:1] == [IN_STORE],
          "asked with %r after %s s" % (asked[:1], took))
    check("and the refusal names the store",
          said == vpm.key_refused_note("store", REFUSED),
          "%r against %r" % (said, vpm.key_refused_note("store", REFUSED)))

    print("\n3. A second key typed while the first is being checked")
    answer["raise"] = False
    hold.clear()
    tick = keep_box()
    if tick is None or not tick.isEnabled():
        check("ticking the box puts the key of the moment into the store",
              False, "no tick found on this platform")
        app.quit()
        return
    # Ticked while the stored key still stands there, so what the tick
    # stores and what the answer stores can be told apart. It starts
    # ticked, for a key is stored: off first, and on again.
    tick.setChecked(False)
    app.processEvents()
    tick.setChecked(True)
    app.processEvents()
    check("ticking the box puts the key of the moment into the store",
          tick.isChecked() and stored[-1:] == [IN_STORE],
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
sys.argv = ["videopodcast_magic.py"]
vpm.gui()
os.environ.pop("AUPHONIC_TOKEN", None)
finish()
