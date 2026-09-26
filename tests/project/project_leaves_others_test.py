# -*- coding: utf-8 -*-
"""Opening, starting or renaming a project leaves each project file its own.

The window remembered where it last wrote a project file, and a new
production or another project opened in the same window did not forget
it. The next output folder or name then moved the old project's file
onto the new one's: the first project's file left its folder, and the
second one's was overwritten with the first one's production.

The sections in the order they run: two projects in two folders, the
first opened and then the second, and afterwards each file lies where
it lay and names its own production; then a new production with its own
material, saved into its own folder, and the project open before it is
still where it was; then an unnamed production's file laid beside the
second project's, that project opened, and both files still lie there,
each naming its own production; then a Finder copy of the second
project's file opened and saved, and the original is byte for byte what
it was, the copy carries the save, and the title bar names the copy;
last a rename typed onto the name of another project's file beside it:
that file stays as it was, the renamed one is saved into its own, the
window says once which project lies there, and a free name moves it
again; a name typed through another project's name on its way to a
free one moves nothing and says nothing until Enter, and then moves once,
and Save project settles a name still being typed the same way;
last a new production never saved, named like another project beside
its material: that file stays byte for byte, the new one is saved under
the next free name, and the window says so once; and once its file is
deleted, named like a third project: that file stays byte for byte too.
The window is driven from outside and the answer is read out of the
files on the disk and the title bar, never out of a variable.
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
import json
import wave
import shutil
import struct
import random
import tempfile
import the_program

SCRIPT = the_program.SCRIPT

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
os.environ["VPM_NO_SPEAKER_SPLIT"] = "1"
os.environ.pop("AUPHONIC_TOKEN", None)

from PySide6 import QtWidgets, QtCore, QtTest

app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
# Before anything can reach the credential store: all three names of
# it go somewhere throwaway.
import key_store_apart
key_store_apart.apart(vpm)
vpm.update_offer = lambda *a, **k: None
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


PATIENCE = 40.0
POLL = 0.02

# ------------------------------------------------------------- the material
ROOT = tempfile.mkdtemp(prefix="vpm_others_")


def a_recording(folder, name, seed):
    """Four seconds of noise, written the way a recorder writes."""
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, name)
    rng = random.Random(seed)
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(48000)
        f.writeframes(b"".join(struct.pack("<h", rng.randint(-6000, 6000))
                               for _ in range(4 * 48000)))
    return path


TAKEN = a_recording(os.path.join(ROOT, "Takes"), "Presenter_REC0001.wav", 11)
FA = os.path.join(ROOT, "A")
FB = os.path.join(ROOT, "B")
FC = os.path.join(ROOT, "C")
FRESH = a_recording(FC, "Guest_REC0002.wav", 22)
PA = os.path.join(FA, vpm.PROJECT_PREFIX + "Alpha.json")
PB = os.path.join(FB, vpm.PROJECT_PREFIX + "Beta.json")
# The file a production without a name is written to, beside Beta's;
# laid down only in the section that asks about it.
PU = os.path.join(FB, vpm.PROJECT_PREFIX + "Project.json")
# What the Finder names a copy of Beta's file laid beside it.
PBC = os.path.join(FB, vpm.PROJECT_PREFIX + "Beta copy.json")
# Another production's file in Beta's folder, and the name Beta takes
# after it is refused: laid down only in the section that asks.
PG = os.path.join(FB, vpm.PROJECT_PREFIX + "Gamma.json")
PD = os.path.join(FB, vpm.PROJECT_PREFIX + "Delta.json")
PR = os.path.join(FB, vpm.PROJECT_PREFIX + "Gammaray.json")
PS = os.path.join(FB, vpm.PROJECT_PREFIX + "Gammarays.json")
# Another production's file beside the new material, and where a
# production never saved under that name goes instead.
PE = os.path.join(FC, vpm.PROJECT_PREFIX + "Eta.json")
PE2 = os.path.join(FC, vpm.PROJECT_PREFIX + "Eta (2).json")
PT = os.path.join(FC, vpm.PROJECT_PREFIX + "Theta.json")
for path, out, production in ((PA, FA, "Alpha"), (PB, FB, "Beta")):
    os.makedirs(out, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"format": vpm.FILE_FORMAT, "version": "test",
                   "timeline": [], "preset": "", "production": production,
                   "multitrack": False, "project_type": "cut",
                   "out_folder": out, "assignment": {},
                   "files": [{"path": TAKEN, "kind": "audio"}]}, f)

chosen = [PA]
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (chosen[0], ""))
QtWidgets.QFileDialog.getOpenFileNames = staticmethod(
    lambda *a, **k: ([FRESH], ""))
QtWidgets.QFileDialog.getExistingDirectory = staticmethod(
    lambda *a, **k: FC)
# Every message the window puts, written down on its way through.
said = []
_say = vpm.say_dialog


def say_dialog(*a, **k):
    """The window's one dialog: noted as (title, text), then put."""
    said.append((a[2], a[3]) if len(a) > 3 else a)
    return _say(*a, **k)


vpm.say_dialog = say_dialog
# Nothing may sit and wait for a click.
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
# Several project files beside the material: none is picked.
QtWidgets.QInputDialog.getItem = staticmethod(lambda *a, **k: ("", False))

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


def action_named(text):
    for w in among(QtWidgets.QWidget):
        for a in w.actions():
            if drawn(a.text()).strip() == text:
                return a
    return None


def name_field():
    """The production's name field, found by the name it speaks as."""
    for w in among(QtWidgets.QLineEdit):
        if w.accessibleName() == vpm.T('Production name'):
            return w
    return None


def typed_in(text, fresh=True, enter=True):
    """Type a name into the field key by key, as a person does.

    *fresh* types over what stands there; *enter* settles it at the end.
    """
    f = name_field()
    if fresh:
        f.selectAll()
    QtTest.QTest.keyClicks(f, text)
    app.processEvents()
    if enter:
        QtTest.QTest.keyClick(f, QtCore.Qt.Key_Return)
        app.processEvents()


def field_says():
    f = name_field()
    return f.text() if f is not None else None


def file_list():
    """The list of chosen files, found by what a screen reader says of it."""
    for t in among(QtWidgets.QTreeWidget):
        if t.accessibleName() == vpm.T('Chosen files'):
            return t
    return None


def listed(path):
    """Whether one file stands in the list, top level or below."""
    tree = file_list()
    if tree is None:
        return False
    stack = [tree.topLevelItem(i) for i in range(tree.topLevelItemCount())]
    while stack:
        node = stack.pop(0)
        held = node.data(0, QtCore.Qt.UserRole)
        if held and os.path.abspath(path) in [os.path.abspath(p)
                                              for p in held]:
            return True
        stack += [node.child(i) for i in range(node.childCount())]
    return False


def waited_for(condition, why):
    began_here = time.time()
    while time.time() - began_here < PATIENCE:
        app.processEvents()
        if condition():
            return time.time() - began_here
        time.sleep(POLL)
    print("      gave up after %.1f s waiting for %s" % (PATIENCE, why))
    return None


def seconds(took):
    """How long a wait took, or that it gave up."""
    return "gave up" if took is None else "%.2f s" % took


def projects_in(folder):
    """The project files lying in one folder, by their bare names."""
    return sorted(n for n in os.listdir(folder)
                  if n.startswith(vpm.PROJECT_PREFIX) and n.endswith(".json"))


def production_of(path):
    """The production a project file names, or what stops it being read."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f).get("production")
    except (OSError, ValueError) as e:
        return "unreadable: %s" % type(e).__name__


def title():
    """What the window's title bar says, or empty while there is none."""
    for w in app.topLevelWidgets():
        if "Video Podcast Magic" in w.windowTitle():
            return w.windowTitle()
    return ""


def version_of(path):
    """The version a project file was last written by."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f).get("version")
    except (OSError, ValueError) as e:
        return "unreadable: %s" % type(e).__name__


def everywhere():
    """What lies in the three folders, so a failing line shows it all."""
    return "; ".join("%s holds %s" % (os.path.basename(d), projects_in(d))
                     for d in (FA, FB, FC))


over = {"done": False}


def drive():
    print("1. One project opened, then another")
    opening = action_named(vpm.T('Open project ...'))
    if opening is not None:
        opening.trigger()
    took = waited_for(lambda: field_says() == "Alpha",
                      "the first project's name")
    check("the first project opens with its production in the field",
          field_says() == "Alpha",
          "the field says %r (%s), wanted 'Alpha'"
          % (field_says(), seconds(took)))
    chosen[0] = PB
    if opening is not None:
        opening.trigger()
    took = waited_for(lambda: field_says() == "Beta",
                      "the second project's name")
    check("the second project opens with its production in the field",
          field_says() == "Beta",
          "the field says %r (%s), wanted 'Beta'"
          % (field_says(), seconds(took)))
    check("the first project's file stays in its folder, as its own",
          os.path.isfile(PA) and production_of(PA) == "Alpha",
          "%s names %r, wanted 'Alpha'; %s"
          % (os.path.basename(PA), production_of(PA), everywhere()))
    check("the second project's file keeps its own production",
          os.path.isfile(PB) and production_of(PB) == "Beta",
          "%s names %r, wanted 'Beta'; %s"
          % (os.path.basename(PB), production_of(PB), everywhere()))

    print("\n2. A new production after it, with material of its own")
    closing = action_named(vpm.T('Close project'))
    if closing is not None:
        closing.trigger()
    app.processEvents()
    adding = action_named(vpm.T('Add files ...'))
    if adding is not None:
        adding.trigger()
    took = waited_for(lambda: listed(FRESH), "the new material in the list")
    check("the new production's material is in the list", listed(FRESH),
          "%s listed: %s (%s)"
          % (os.path.basename(FRESH), listed(FRESH), seconds(took)))
    saving = action_named(vpm.T('Save project'))
    if saving is not None:
        saving.trigger()
    took = waited_for(lambda: projects_in(FC), "the new production's file")
    check("the new production's file is written into its own folder",
          len(projects_in(FC)) == 1,
          "%d project file(s) in C (%s), wanted 1; %s"
          % (len(projects_in(FC)), seconds(took), everywhere()))
    check("the project open before it stays in its folder, as its own",
          os.path.isfile(PB) and production_of(PB) == "Beta",
          "%s names %r, wanted 'Beta'; %s"
          % (os.path.basename(PB), production_of(PB), everywhere()))

    print("\n3. A project opened beside an unnamed production's file")
    with open(PU, "w", encoding="utf-8") as f:
        json.dump({"format": vpm.FILE_FORMAT, "version": "test",
                   "timeline": [], "preset": "", "production": "",
                   "multitrack": False, "project_type": "cut",
                   "out_folder": FB, "assignment": {},
                   "files": [{"path": TAKEN, "kind": "audio"}]}, f)
    chosen[0] = PB
    if opening is not None:
        opening.trigger()
    took = waited_for(lambda: field_says() == "Beta",
                      "the project's name beside the unnamed file")
    check("the project beside an unnamed file opens with its production",
          field_says() == "Beta",
          "the field says %r (%s), wanted 'Beta'"
          % (field_says(), seconds(took)))
    check("the opened project's file keeps its own production",
          os.path.isfile(PB) and production_of(PB) == "Beta",
          "%s names %r, wanted 'Beta'; %s"
          % (os.path.basename(PB), production_of(PB), everywhere()))
    check("the unnamed production's file beside it stays, as its own",
          os.path.isfile(PU) and production_of(PU) == "",
          "%s there: %s, names %r, wanted ''; %s"
          % (os.path.basename(PU), os.path.isfile(PU),
             production_of(PU) if os.path.isfile(PU) else None,
             everywhere()))

    print("\n4. A Finder copy of a project opened and saved")
    shutil.copyfile(PB, PBC)
    with open(PB, "rb") as f:
        before = f.read()
    chosen[0] = PBC
    if opening is not None:
        opening.trigger()
    waited_for(lambda: title().startswith(os.path.basename(PBC)),
               "the copy's name in the title bar")
    if saving is not None:
        saving.trigger()
    took = waited_for(lambda: version_of(PBC) == vpm.VERSION
                      or version_of(PB) == vpm.VERSION,
                      "the save to reach a file")
    after = b""
    if os.path.isfile(PB):
        with open(PB, "rb") as f:
            after = f.read()
    check("saving the opened copy leaves the original byte for byte",
          after == before,
          "%s: %d bytes before, %d after, written by version %r (%s); %s"
          % (os.path.basename(PB), len(before), len(after),
             version_of(PB), seconds(took), everywhere()))
    check("the save goes into the copy that was opened",
          version_of(PBC) == vpm.VERSION and production_of(PBC) == "Beta",
          "%s written by version %r naming %r, wanted %r naming 'Beta' "
          "(%s); %s" % (os.path.basename(PBC), version_of(PBC),
                        production_of(PBC), vpm.VERSION, seconds(took),
                        everywhere()))
    check("the title bar names the copy the save went into",
          title().startswith(os.path.basename(PBC)),
          "the title reads %r, wanted it to begin with %r"
          % (title(), os.path.basename(PBC)))

    print("\n5. A rename onto the name of another project beside it")
    with open(PG, "w", encoding="utf-8") as f:
        json.dump({"format": vpm.FILE_FORMAT, "version": "test",
                   "timeline": [], "preset": "", "production": "Gamma",
                   "multitrack": False, "project_type": "cut",
                   "out_folder": FB, "assignment": {},
                   "files": [{"path": TAKEN, "kind": "audio"}]}, f)
    with open(PG, "rb") as f:
        before = f.read()
    chosen[0] = PB
    if opening is not None:
        opening.trigger()
    waited_for(lambda: field_says() == "Beta" and title().startswith(
        os.path.basename(PB)), "the project's name after the copy")
    k = len(said)
    typed_in("Gamma")
    if saving is not None:
        saving.trigger()
    took = waited_for(lambda: production_of(PB) == "Gamma"
                      or production_of(PG) != "Gamma", "the save")
    with open(PG, "rb") as f:
        after = f.read()
    check("a rename onto another project's name leaves its file as it was",
          after == before,
          "%s: %d bytes before, %d after, naming %r (%s); %s"
          % (os.path.basename(PG), len(before), len(after),
             production_of(PG), seconds(took), everywhere()))
    check("the renamed project is saved into its own file, as renamed",
          production_of(PB) == "Gamma" and version_of(PB) == vpm.VERSION,
          "%s names %r, written by version %r (%s); %s"
          % (os.path.basename(PB), production_of(PB), version_of(PB),
             seconds(took), everywhere()))
    named = [text for put, text in said[k:]
             if put == vpm.T('Project') and os.path.basename(PG) in text]
    check("and the window says once which project lies there",
          len(named) == 1, "%d of the messages since the rename, titled %s, "
          "name %s under %r" % (len(named), [put for put, _t in said[k:]],
                                os.path.basename(PG), vpm.T('Project')))
    typed_in("Delta")
    took = waited_for(lambda: os.path.isfile(PD), "the file under Delta")
    check("a name no other project has takes the file along again",
          os.path.isfile(PD) and not os.path.isfile(PB)
          and production_of(PG) == "Gamma",
          "%s there %s, %s there %s (%s); %s"
          % (os.path.basename(PD), os.path.isfile(PD),
             os.path.basename(PB), os.path.isfile(PB), seconds(took),
             everywhere()))
    k = len(said)
    typed_in("Gamma", enter=False)
    check("typing through another project's name moves nothing yet",
          os.path.isfile(PD) and production_of(PG) == "Gamma"
          and len(said) == k,
          "the field says %r; %s there %s, %d message(s) since the typing "
          "began: %r; %s" % (field_says(), os.path.basename(PD),
                             os.path.isfile(PD), len(said) - k, said[k:],
                             everywhere()))
    typed_in("ray", fresh=False)
    took = waited_for(lambda: os.path.isfile(PR), "the file under Gammaray")
    with open(PG, "rb") as f:
        after = f.read()
    check("the name settled by Enter moves the file once, saying nothing",
          os.path.isfile(PR) and not os.path.isfile(PD) and after == before
          and len(said) == k,
          "%s there %s, %s there %s, %s %d bytes before and %d after, "
          "%d message(s): %r (%s); %s"
          % (os.path.basename(PR), os.path.isfile(PR),
             os.path.basename(PD), os.path.isfile(PD),
             os.path.basename(PG), len(before), len(after), len(said) - k,
             said[k:], seconds(took), everywhere()))
    k = len(said)
    typed_in("Gammarays", enter=False)
    if saving is not None:
        saving.trigger()
    took = waited_for(lambda: os.path.isfile(PS), "the file under Gammarays")
    check("Save project settles a name still typed: one file, nothing said",
          os.path.isfile(PS) and not os.path.isfile(PR)
          and production_of(PS) == "Gammarays"
          and [p for p, _t in said[k:]] == [vpm.T('Save project')],
          "%s there %s naming %r, %s there %s, messages since titled %r, "
          "wanted only %r (%s); %s"
          % (os.path.basename(PS), os.path.isfile(PS), production_of(PS),
             os.path.basename(PR), os.path.isfile(PR),
             [put for put, _t in said[k:]], vpm.T('Save project'),
             seconds(took), everywhere()))

    print("\n6. A production never saved, named like another project")
    with open(PE, "w", encoding="utf-8") as f:
        json.dump({"format": vpm.FILE_FORMAT, "version": "test",
                   "timeline": [], "preset": "", "production": "Eta",
                   "multitrack": False, "project_type": "cut",
                   "out_folder": FC, "assignment": {},
                   "files": [{"path": TAKEN, "kind": "audio"}]}, f)
    with open(PE, "rb") as f:
        before = f.read()
    if closing is not None:
        closing.trigger()
    app.processEvents()
    k = len(said)
    typed_in("Eta")
    if adding is not None:
        adding.trigger()
    waited_for(lambda: listed(FRESH), "the material of the new production")
    if saving is not None:
        saving.trigger()
    took = waited_for(lambda: os.path.isfile(PE2)
                      or production_of(PE) != "Eta", "the save")
    with open(PE, "rb") as f:
        after = f.read()
    check("a production never saved leaves the other's file as it was",
          after == before,
          "%s: %d bytes before, %d after, naming %r (%s); %s"
          % (os.path.basename(PE), len(before), len(after),
             production_of(PE), seconds(took), everywhere()))
    check("it is saved under the next free name instead",
          production_of(PE2) == "Eta" and version_of(PE2) == vpm.VERSION,
          "%s names %r, written by version %r (%s); %s"
          % (os.path.basename(PE2), production_of(PE2), version_of(PE2),
             seconds(took), everywhere()))
    named = [text for put, text in said[k:]
             if put == vpm.T('Project') and os.path.basename(PE) in text]
    check("and the window says once which project lies there, and where",
          len(named) == 1 and os.path.basename(PE2) in named[0],
          "%d of the messages since the name, titled %s, name %s under "
          "%r: %r" % (len(named), [put for put, _t in said[k:]],
                      os.path.basename(PE), vpm.T('Project'), named))
    # Its own file gone from the disk, then named like another project.
    with open(PT, "w", encoding="utf-8") as f:
        json.dump({"format": vpm.FILE_FORMAT, "version": "test",
                   "timeline": [], "preset": "", "production": "Theta",
                   "multitrack": False, "project_type": "cut",
                   "out_folder": FC, "assignment": {},
                   "files": [{"path": TAKEN, "kind": "audio"}]}, f)
    with open(PT, "rb") as f:
        before = f.read()
    if os.path.isfile(PE2):
        os.remove(PE2)
    typed_in("Theta")
    if saving is not None:
        saving.trigger()
    took = waited_for(lambda: production_of(PT) != "Theta"
                      or len(projects_in(FC)) > 3, "the save")
    with open(PT, "rb") as f:
        after = f.read()
    check("one whose file was deleted leaves the other's file as it was",
          after == before,
          "%s: %d bytes before, %d after, naming %r (%s); %s"
          % (os.path.basename(PT), len(before), len(after),
             production_of(PT), seconds(took), everywhere()))
    over["done"] = True
    app.quit()


def brake():
    """An outer brake only: every wait inside has its own patience."""
    if not over["done"]:
        bad.append("the pass never finished: 240 s gone")
        app.quit()


QtCore.QTimer.singleShot(0, drive)
QtCore.QTimer.singleShot(240000, brake)
sys.argv = ["videopodcast_magic.py"]
try:
    vpm.gui()
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("the window never came up: gui() fell over")
finally:
    shutil.rmtree(ROOT, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
