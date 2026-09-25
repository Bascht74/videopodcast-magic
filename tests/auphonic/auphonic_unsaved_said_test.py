# -*- coding: utf-8 -*-
"""A key the store refuses takes its tick back and says so in the window.

The sections, as the test prints them: the window as it starts; the
refused checked key -- the tick back, the stored key kept, the sentence
under the field and on the sheet; the refusal over presets fitting only
the other mode -- the tick on again, refusal and note both, the refusal
in front; a key not kept there -- the note alone; the tick set by hand
over the refusing store -- the key handed on, no box, the sentence on the
key's line. Every box is answered at once and counted; the store is stood
in and never writes, and nothing goes to auphonic.com.
"""
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
import traceback
import the_program

SCRIPT = the_program.SCRIPT

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
# The key has to come out of the store, where the tick is decided.
os.environ.pop("AUPHONIC_TOKEN", None)

from PySide6 import QtWidgets, QtCore            # noqa: E402
from PySide6.QtTest import QTest                  # noqa: E402

app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
# All three names of the store go somewhere throwaway first, so even a
# stand-in that failed to take would not reach the real key.
import key_store_apart                            # noqa: E402
key_store_apart.apart(vpm)

began = time.time()
done = 0
bad = []
reached = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def finish():
    """The one way out: the count, the verdict, the return code."""
    if not reached:
        bad.append("the drive got to its end [it stopped before, "
                   "after %d checks]" % done)
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


IN_STORE = "stored-key-44444"
TYPED = "typed-key-55555"
RETYPED = "typed-key-66666"
UNKEPT = "typed-key-77777"
PATIENCE = 30.0
POLL = 0.02

# ------------------------------------------------ the key store, refusing
# At least as strict as the real one after a refused write: it keeps
# what it held, hands back only that, and answers every save with False.
held = [IN_STORE]
puts = []
deletes = []


def store_refuses(key):
    puts.append(key)
    return False


def delete_stand_in():
    deletes.append(held[0])
    gone, held[0] = bool(held[0]), ""
    return gone


vpm._ask_key_store = lambda: held[0]
vpm.load_api_key = lambda: held[0]
vpm.store_api_key = store_refuses
vpm.delete_api_key = delete_stand_in
# A locked keychain takes the tick away before anything is saved; that
# is another question, and the box has to be live for this one.
vpm.key_store_locked = lambda: False
# One preset of each kind, so that one fits whichever mode the window
# starts in: an account with none that fits says so on the same line.
vpm.list_presets = lambda key: [("Podcast_Multitrack", "u1", True),
                                ("Podcast_Single", "u2", False)]
vpm.update_offer = lambda *a, **k: None
# A box that would wait for a click is answered at once, so a fault that
# opens one ends in a red line instead of a run that hangs -- and counted
# by its title. A QMessageBox inherits this exec; its four ready-made
# boxes are C++ and do not, so they are answered here as well.
boxes = []


def box_answered(self, *_args):
    boxes.append(str(self.windowTitle()))
    return QtWidgets.QDialog.Rejected


def ready_box_answered(*args, **_kw):
    boxes.append(str(args[1]) if len(args) > 1 else "?")
    return QtWidgets.QMessageBox.Cancel


QtWidgets.QDialog.exec = box_answered
for _kind in ("information", "warning", "critical", "question"):
    setattr(QtWidgets.QMessageBox, _kind, staticmethod(ready_box_answered))


def drawn(text):
    """What ends up on the screen: & marks a key, && draws one &."""
    return str(text).replace("&&", "\x00").replace("&", "") \
                    .replace("\x00", "&")


def among(kind):
    return [w for w in app.allWidgets() if isinstance(w, kind)]


def key_field():
    for w in among(QtWidgets.QLineEdit):
        if w.echoMode() == QtWidgets.QLineEdit.Password:
            return w
    return None


def connect_button():
    for b in among(QtWidgets.QPushButton):
        if drawn(b.text()).strip() == vpm.T('Connect'):
            return b
    return None


def keep_box():
    said = {vpm.T('Save in Keychain'), vpm.T('Save in Registry'),
            vpm.T('Keep it saved')}
    for b in among(QtWidgets.QCheckBox):
        if drawn(b.text()).strip() in said:
            return b
    return None


def multitrack_box():
    """The tick that decides which presets fit, found by its caption."""
    for b in among(QtWidgets.QCheckBox):
        if drawn(b.text()).strip() == vpm.T('Multitrack (one track per '
                                            'speaker)'):
            return b
    return None


def notes():
    """The two lines about the key, by the names the program gives them."""
    return [w for w in among(QtWidgets.QLabel)
            if w.objectName() in ("key_note", "key_note_settings")]


def waited_for(condition, why):
    """Wait on a condition, never on the clock; None when it never came."""
    began_here = time.time()
    while time.time() - began_here < PATIENCE:
        app.processEvents()
        if condition():
            return time.time() - began_here
        time.sleep(POLL)
    print("      gave up after %.1f s waiting for %s" % (PATIENCE, why))
    return None


def drive():
    print("1. The window as it starts")
    took = waited_for(lambda: key_field() and connect_button()
                      and keep_box(), "the key field, button and tick")
    field, connect, tick = key_field(), connect_button(), keep_box()
    check("the window came up with its key field, button and tick",
          took is not None,
          "field %s, button %s, tick %s after %s s"
          % (field is not None, connect is not None, tick is not None,
             "%.2f" % took if took else took))
    if took is None:
        return
    check("the tick starts on, because the store holds a key",
          tick.isChecked() and tick.isEnabled(),
          "checked %s, enabled %s, the store holds %d chars"
          % (tick.isChecked(), tick.isEnabled(), len(held[0])))

    print("\n2. The store refuses the key that was checked")
    field.setFocus()
    field.selectAll()
    QTest.keyClicks(field, TYPED)
    app.processEvents()
    before = len(puts)
    connect.click()
    took = waited_for(lambda: len(puts) > before, "the save to be asked")
    check("the checked key is handed to the store",
          took is not None and puts[-1:] == [TYPED],
          "%d save(s) asked after %s s, the last with %d chars, wanted "
          "%d" % (len(puts) - before, "%.2f" % took if took else took,
                  len(puts[-1] if puts else ""), len(TYPED)))
    app.processEvents()
    check("a store that refuses takes the tick back",
          not tick.isChecked(),
          "the tick is %s after %d refused save(s)"
          % ("on" if tick.isChecked() else "off", len(puts) - before))
    check("and the key already in the store is not thrown away",
          not deletes and held[0] == IN_STORE,
          "%d delete(s) asked, the store holds %d chars, wanted 0 and %d"
          % (len(deletes), len(held[0]), len(IN_STORE)))
    want = vpm.T('The key was not saved: %s') % vpm.key_store_trouble()
    said = [(w.objectName(), drawn(w.text()), w.isHidden())
            for w in notes()]
    shown = [name for name, text, hidden in said
             if text == want and not hidden]
    check("the window says the key was not saved, in both places",
          sorted(shown) == ["key_note", "key_note_settings"],
          "shown in %s of %d lines, wanted key_note and "
          "key_note_settings; they say %s"
          % (shown, len(said), [t[:40] for _n, t, _h in said]))
    head = unfitting(field, connect, tick, want)
    if head is not None:
        nothing_refused(field, connect, tick, head)
    ticked_by_hand(field, tick, want)
    reached.append(True)


def unfitting(field, connect, tick, want):
    """The refusal over presets of the other kind only: both sentences.

    Gives back what the note begins with, or None without the tick.
    """
    print("\n3. The store refuses it over presets that fit only the other "
          "mode")
    multi = multitrack_box()
    if multi is None:
        bad.append("the Multitrack tick was found [no check box says %r]"
                   % vpm.T('Multitrack (one track per speaker)'))
        return None
    multi_on = multi.isChecked()
    vpm.list_presets = lambda key: [("Podcast_Other", "u3", not multi_on)]
    # The tick goes on again through a save that is taken and written
    # nowhere; the refusing store then answers the Connect below.
    vpm.store_api_key = lambda key: True
    tick.click()
    vpm.store_api_key = store_refuses
    app.processEvents()
    check("the tick is on again before the second Connect",
          tick.isChecked(),
          "the tick is %s after one click with a store that takes the key"
          % ("on" if tick.isChecked() else "off"))
    field.setFocus()
    field.selectAll()
    QTest.keyClicks(field, RETYPED)
    app.processEvents()
    before = len(puts)
    connect.click()
    took = waited_for(lambda: len(puts) > before, "the second save")
    kind = (vpm.T('The key is good. Of the %s presets in the account none '
                  'is a Multitrack one, so the list stays empty.')
            if multi_on else
            vpm.T('The key is good. Of the %s presets in the account none '
                  'is a Singletrack one, so the list stays empty.'))
    head, tail = kind.split("%s")
    said = [(w.objectName(), drawn(w.text()), w.isHidden())
            for w in notes()]
    refused = sorted(n for n, t, h in said if want in t and not h)
    check("a refusal over presets that fit only the other mode says so",
          took is not None and refused == ["key_note", "key_note_settings"],
          "save asked %s, the sentence in %s of %d lines, wanted key_note "
          "and key_note_settings; they say %s"
          % (took is not None, refused, len(said),
             [t[:60] for _n, t, _h in said]))
    noted = sorted(n for n, t, h in said
                   if head in t and tail in t and not h)
    check("and the note that no preset fits the mode stands beside it",
          noted == ["key_note", "key_note_settings"],
          "Multitrack %s, the note in %s of %d lines; they say %s"
          % ("on" if multi_on else "off", noted, len(said),
             [t[-60:] for _n, t, _h in said]))
    order = [(t.find(want), t.find(head)) for _n, t, h in said if not h]
    check("and the refusal stands in front of the note",
          len(order) == 2 and all(0 <= r < n for r, n in order),
          "the refusal and the note begin at %s in %d shown lines, wanted "
          "the refusal first in 2" % (order, len(order)))
    return head


def nothing_refused(field, connect, tick, head):
    """A key not kept over the same presets: the note alone on the line."""
    print("\n4. A key not kept, over presets that fit only the other mode")
    field.setFocus()
    field.selectAll()
    QTest.keyClicks(field, UNKEPT)
    app.processEvents()
    before = len(puts)
    connect.click()
    took = waited_for(lambda: sorted(
        w.objectName() for w in notes()
        if head in drawn(w.text()) and not w.isHidden())
        == ["key_note", "key_note_settings"], "the note in both lines")
    said = [drawn(w.text()) for w in notes() if not w.isHidden()]
    check("with nothing refused the note stands alone, no line above it",
          took is not None and len(said) == 2
          and all(t.startswith(head) for t in said),
          "tick %s, %d save(s) asked, note after %s s; the %d shown "
          "lines begin %s" % ("on" if tick.isChecked() else "off",
                              len(puts) - before,
                              "%.2f" % took if took else took, len(said),
                              [t[:30] for t in said]))


def ticked_by_hand(field, tick, want):
    """The tick set by hand, the store refusing: no box, the key's line."""
    print("\n5. The tick set by hand, the store refusing")
    typed = field.text()
    was_on = tick.isChecked()
    before, boxes_before = len(puts), len(boxes)
    tick.click()
    app.processEvents()
    check("the tick set by hand hands the typed key to the store",
          not was_on and puts[before:] == [typed],
          "tick %s before the click, %d save(s) asked, the last with %d "
          "chars, wanted 1 with %d" % ("on" if was_on else "off",
                                        len(puts) - before,
                                        len(puts[-1] if puts else ""),
                                        len(typed)))
    opened = boxes[boxes_before:]
    check("a tick the store refuses opens no box",
          opened == [],
          "%d box(es) opened, titled %s" % (len(opened), opened))
    said = [(w.objectName(), drawn(w.text()), w.isHidden())
            for w in notes()]
    shown = sorted(n for n, t, h in said if t == want and not h)
    check("and the key's line says the key was not saved",
          shown == ["key_note", "key_note_settings"],
          "shown in %s of %d lines, wanted key_note and "
          "key_note_settings; they say %s"
          % (shown, len(said), [t[:40] for _n, t, _h in said]))


def drive_and_quit():
    """Every way out of the drive ends the window and reaches finish()."""
    try:
        drive()
    except Exception as exc:                      # noqa: BLE001
        traceback.print_exc()
        bad.append("the drive ran without an error [%s: %s]"
                   % (type(exc).__name__, exc))
    finally:
        app.quit()


QtCore.QTimer.singleShot(0, drive_and_quit)
sys.argv = ["videopodcast_magic.py"]
try:
    vpm.gui()
except Exception as exc:                          # noqa: BLE001
    traceback.print_exc()
    bad.append("the window was built [%s: %s]" % (type(exc).__name__, exc))
finish()
