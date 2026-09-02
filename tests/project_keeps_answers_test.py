# -*- coding: utf-8 -*-
"""The saved project holds what was answered, and nothing else.

Two ways something else got in. A recording taken out of the list left
the screen but not the store the project file is written from, so it
stood in the file with an empty name and came back at the next opening.
And where auphonic.com refused the key, the preset list fell back on
"work without Auphonic" -- a stand-in for a list that is missing, which
was written into the project as though somebody had chosen it.

The sections: what the store keeps about a file that has left; a
recording added, saved, removed and saved again; and a preset chosen,
then a key that stops being accepted. The window is driven from
outside, and the answer is read out of the file that was written,
never out of a variable.

Nothing here goes to auphonic.com or into a key store: both are
replaced by stand-ins, and all material lives under a folder of its own.
"""
import os
import sys
import time
import json
import wave
import shutil
import struct
import random
import tempfile
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
os.environ["VPM_NO_SPEAKER_SPLIT"] = "1"
os.environ.pop("AUPHONIC_TOKEN", None)

from PySide6 import QtWidgets, QtCore
from PySide6.QtTest import QTest

app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.set_language("en")
vpm.update_offer = lambda *a, **k: None

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


# A preset auphonic.com did not classify: it is offered whatever the
# Multitrack tick says, so the section is about the preset and not
# about the mode.
PRESET = "Podcast_Whole"
REFUSED = "403: Token doesn't exist"
PATIENCE = 40.0
POLL = 0.02

answer = {"raise": False}


def fetch_stand_in(key):
    if answer["raise"]:
        raise RuntimeError(REFUSED)
    return [(PRESET, "u1", None)]


vpm.list_presets = fetch_stand_in
vpm.load_api_key = lambda: "a-key-nobody-checks"
vpm.store_api_key = lambda key: True
vpm.delete_api_key = lambda: None

# ------------------------------------------------------------- the material
FOLDER = tempfile.mkdtemp(prefix="vpm_answers_")
OUT = os.path.join(FOLDER, "Result")
os.makedirs(OUT, exist_ok=True)


def a_recording(name, seed):
    """Eight seconds of noise, written the way a recorder writes."""
    path = os.path.join(FOLDER, name)
    rng = random.Random(seed)
    frames = 8 * 48000
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(48000)
        f.writeframes(b"".join(
            struct.pack("<h", rng.randint(-6000, 6000))
            for _ in range(frames)))
    return path


KEPT = a_recording("Presenter_REC0001.wav", 11)
GOING = a_recording("Guest_REC0002.wav", 22)

QtWidgets.QFileDialog.getOpenFileNames = staticmethod(
    lambda *a, **k: ([KEPT, GOING], ""))
QtWidgets.QFileDialog.getExistingDirectory = staticmethod(
    lambda *a, **k: OUT)
# Nothing may sit and wait for a click.
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok

_show = QtWidgets.QWidget.show


def offstage(self):
    self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
    _show(self)


QtWidgets.QWidget.show = offstage
QtWidgets.QDialog.show = offstage


# ------------------------------------------------------- reading the window
def drawn(text):
    """What ends up on the screen: & marks a key, && draws one &."""
    return str(text).replace("&&", "\x00").replace("&", "") \
                    .replace("\x00", "&")


def among(kind):
    return [w for w in app.allWidgets() if isinstance(w, kind)]


def button_named(text):
    for b in among(QtWidgets.QPushButton):
        if drawn(b.text()).strip() == text:
            return b
    return None


def action_named(text):
    for w in among(QtWidgets.QWidget):
        for a in w.actions():
            if drawn(a.text()).strip() == text:
                return a
    return None


def file_list():
    """The list of chosen files, found by what a screen reader says of it."""
    for t in among(QtWidgets.QTreeWidget):
        if t.accessibleName() == vpm.T('Chosen files'):
            return t
    return None


def rows_of(tree):
    """Every item of the tree, top level and below."""
    out = []
    stack = [tree.topLevelItem(i) for i in range(tree.topLevelItemCount())]
    while stack:
        node = stack.pop(0)
        out.append(node)
        stack += [node.child(i) for i in range(node.childCount())]
    return out


def row_for(tree, path):
    """The item that stands for one file."""
    for node in rows_of(tree):
        held = node.data(0, QtCore.Qt.UserRole)
        if held and os.path.abspath(path) in [os.path.abspath(p)
                                              for p in held]:
            return node
    return None


def key_field():
    """The field the key is typed into: the one that hides what it holds."""
    for w in among(QtWidgets.QLineEdit):
        if w.echoMode() == QtWidgets.QLineEdit.Password:
            return w
    return None


def note_shown():
    """The sentence the window is showing about the key, or ""."""
    heads = [vpm.T('auphonic.com does not accept the key: %s'),
             vpm.T('The stored key is not accepted: %s'),
             vpm.T('The key from AUPHONIC_TOKEN is not accepted: %s')]
    heads = [h.replace("%s", "").strip() for h in heads]
    for x in among(QtWidgets.QLabel):
        said = drawn(x.text()).strip()
        if any(said.startswith(h) for h in heads):
            return said
    return ""


def preset_box():
    for b in among(QtWidgets.QComboBox):
        for i in range(b.count()):
            if b.itemData(i) == vpm.PRESET_NONE:
                return b
    return None


def waited_for(condition, why):
    began_here = time.time()
    while time.time() - began_here < PATIENCE:
        app.processEvents()
        if condition():
            return time.time() - began_here
        time.sleep(POLL)
    print("      gave up after %.1f s waiting for %s" % (PATIENCE, why))
    return None


def project_file():
    """The project file the program wrote, wherever it put it."""
    for base in (OUT, FOLDER):
        for name in sorted(os.listdir(base)):
            if name.startswith(vpm.PROJECT_PREFIX) and name.endswith(".json"):
                return os.path.join(base, name)
    return None


def saved():
    """Press "Save project" and read back what was written."""
    entry = action_named(vpm.T('Save project'))
    if entry is None:
        return None
    entry.trigger()
    app.processEvents()
    where = project_file()
    if not where:
        return None
    with open(where, encoding="utf-8") as f:
        return json.load(f)


def about(d, path):
    """Everything the saved assignment still says about one file."""
    keys = []
    for api_key in (d.get("assignment") or {}):
        head, _sep, rest = str(api_key).partition(":")
        if rest and os.path.abspath(rest) == os.path.abspath(path):
            keys.append(api_key)
    return sorted(keys)


print("1. What the store keeps about a file that has left")
STORE = {"audio:" + KEPT: ["Presenter", ""],
         "kind:" + KEPT: "content",
         "audio:" + GOING: ["Guest", ""],
         "kind:" + GOING: "intro",
         "own:" + GOING: True,
         "ownname:" + GOING: "GuestCam",
         "several:" + GOING: True,
         "video:" + GOING: "Interview_GuestCam",
         "voice:" + vpm.voice_key(GOING, "SPEAKER_00"): "x.mov",
         "voicename:" + vpm.voice_key(GOING, "SPEAKER_01"): "Guest",
         "player_file": KEPT}
store = dict(STORE)
struck = vpm.remembered_forget(store, [GOING])
about_going = [k for k in store
               if k.partition(":")[2].startswith(GOING)
               or GOING in k]
check("every key about a recording that left is struck",
      not about_going,
      "%d key(s) left of it, %d struck: %s"
      % (len(about_going), len(struck), sorted(about_going)[:3]))
check("a voice remembered under that recording goes with it",
      "voice:" + vpm.voice_key(GOING, "SPEAKER_00") in struck
      and "voicename:" + vpm.voice_key(GOING, "SPEAKER_01") in struck,
      "struck: %s" % sorted(k for k in struck if k.startswith("voice")))
check("and nothing about another recording is touched",
      store.get("audio:" + KEPT) == ["Presenter", ""]
      and store.get("kind:" + KEPT) == "content"
      and store.get("player_file") == KEPT,
      "%d of the %d keys are left, wanted the 3 that are not about it"
      % (len(store), len(STORE)))


def drive():
    add = button_named(vpm.T('Add files ...'))
    if add is None:
        # Through the same wording the section below uses: a check
        # only a broken window ever reaches is one nobody can show red.
        check("both recordings are in the list", False,
              "no Add button on screen, so nothing was ever added")
        app.quit()
        return
    add.click()
    tree = file_list()
    took = waited_for(
        lambda: tree is not None and row_for(tree, GOING) is not None,
        "the two recordings to appear in the list")
    check("both recordings are in the list", took is not None,
          "%d row(s) after %s s"
          % (0 if tree is None else len(rows_of(tree)), took))
    if took is None:
        app.quit()
        return

    print("\n2. A recording that is taken out of the list")
    first = saved()
    check("the saved project holds both recordings", first is not None
          and len(first.get("files") or []) == 2
          and about(first, GOING),
          "%d file(s), %d entry(s) about the one that goes"
          % (len(((first or {}).get("files")) or []),
             len(about(first or {}, GOING))))
    node = row_for(tree, GOING)
    tree.setCurrentItem(node)
    app.processEvents()
    button_named(vpm.T('Remove')).click()
    app.processEvents()
    check("the row really left the window",
          row_for(tree, GOING) is None and row_for(tree, KEPT) is not None,
          "the removed one is %s, the other %s"
          % ("gone" if row_for(tree, GOING) is None else "still there",
             "there" if row_for(tree, KEPT) is not None else "gone"))
    second = saved()
    left = [f.get("path") for f in ((second or {}).get("files") or [])]
    check("the saved file list holds only the recording that stayed",
          [os.path.abspath(p) for p in left] == [os.path.abspath(KEPT)],
          "%r against %r" % (left, [KEPT]))
    check("and the assignment says nothing about the one that left",
          not about(second or {}, GOING),
          "%r still in the saved assignment" % (about(second or {}, GOING),))
    print("\n3. A preset, and a key that stops being accepted")
    box = preset_box()
    if box is None:
        check("the preset list offers what auphonic.com sent", False,
              "no preset list on screen")
        app.quit()
        return
    box.showPopup()
    box.hidePopup()
    took = waited_for(lambda: box.findData(PRESET) >= 0, "the preset list")
    check("the preset list offers what auphonic.com sent",
          box.findData(PRESET) >= 0,
          "%d entry(s) after %s s: %s"
          % (box.count(), took,
             [box.itemData(i) for i in range(box.count())]))
    box.setCurrentIndex(box.findData(PRESET))
    box.activated.emit(box.currentIndex())
    app.processEvents()
    third = saved()
    check("the preset somebody picked is what the project keeps",
          (third or {}).get("preset") == PRESET,
          "%r against %r" % ((third or {}).get("preset"), PRESET))
    # And now auphonic.com refuses the key. A key retyped is what makes
    # the button askable again -- after a good answer it is green and
    # asleep, which is what somebody in front of a refused key does too.
    answer["raise"] = True
    field = key_field()
    if field is None:
        check("the box stands on 'without Auphonic' when it is saved",
              False, "no key field on screen")
        app.quit()
        return
    field.setFocus()
    field.selectAll()
    QTest.keyClicks(field, "another-key-44444")
    QTest.keyClick(field, QtCore.Qt.Key_Return)
    app.processEvents()
    button_named(vpm.T('Connect')).click()
    took = waited_for(lambda: note_shown() != "", "the key to be refused")
    check("the refused key is said as a note", note_shown() != "",
          "the window says %r after %s s" % (note_shown()[:60], took))
    check("the box stands on 'without Auphonic' when it is saved",
          box.currentData() == vpm.PRESET_NONE,
          "the box stands on %r, wanted %r"
          % (box.currentData(), vpm.PRESET_NONE))
    fourth = saved()
    check("the fallback is not written into the project as a decision",
          (fourth or {}).get("preset") == PRESET,
          "%r against %r" % ((fourth or {}).get("preset"), PRESET))
    app.quit()


QtCore.QTimer.singleShot(2500, drive)
QtCore.QTimer.singleShot(180000, app.quit)
sys.argv = ["videopodcast-magic.py"]
try:
    vpm.gui()
finally:
    shutil.rmtree(FOLDER, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
