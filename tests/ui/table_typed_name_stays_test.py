# -*- coding: utf-8 -*-
"""A name somebody typed stays as typed, even shaped like an offer.

A camera or voice name that reads like the program's own offer with a
number hung on is still the one somebody typed. Sections: a project
file opened, whose cameras carry such a name from an older file and one
marked as the table's own; then a name typed into the table and one
the file marks typed standing through a rebuild, the typed one saved
marked typed; last the voices, in memory, a typed stand-in kept from
renumbering and from a proposal once it comes back out of a file.
"""
PLATFORM_BOUND = True
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import wave
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import the_program

SCRIPT = the_program.SCRIPT

os.environ["QT_QPA_PLATFORM"] = "offscreen"
import numpy as np
from PySide6 import QtCore, QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.update_offer = lambda *a, **k: None

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


PATIENCE = 60.0
folder = tempfile.mkdtemp(prefix="vpm_typed_")
CAMS = []
for stem in ("C0001", "C0002", "C0003"):
    CAMS.append(os.path.join(folder, stem + ".MP4"))
    subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
         "testsrc=size=160x90:rate=25:duration=4", "-f", "lavfi",
         "-i", "sine=frequency=300:duration=4", "-c:a", "aac",
         "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
         "yuv420p", "-shortest", "-y", CAMS[-1]],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# One recording beside them: without it the sheet holds no camera table.
ROOM = os.path.join(folder, "Room.wav")
with wave.open(ROOM, "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(48000)
    f.writeframes((np.random.default_rng(3).normal(0, 0.1, 4 * 48000)
                   .clip(-1, 1) * 32767).astype("<i2").tobytes())
OUT = os.path.join(folder, "Result")
os.makedirs(OUT)
PROJECT = os.path.join(OUT, "videopodcast-magic_Typed.json")
with open(PROJECT, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "version": "test",
               "timeline": [], "preset": "", "production": "Typed",
               "multitrack": False, "project_type": "cut",
               "out_folder": OUT,
               "assignment": {"video:" + CAMS[0]: "C0001",
                              "videotyped:" + CAMS[0]: True,
                              "video:" + CAMS[1]: "C0002 2",
                              "video:" + CAMS[2]: "C0003 2",
                              "videotyped:" + CAMS[2]: False},
               "files": [{"path": ROOM, "kind": "audio"}]
               + [{"path": p, "kind": "video"} for p in CAMS]}, f)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (PROJECT, ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
_show = QtWidgets.QWidget.show


def offstage(self):
    """Shown for the layout, never on a screen."""
    self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
    _show(self)


QtWidgets.QWidget.show = offstage


def win():
    """The program's window."""
    for w in app.topLevelWidgets():
        if "Video Podcast Magic" in w.windowTitle():
            return w
    return None


def name_fields():
    """The camera table's name fields by the file each row names."""
    for t in win().findChildren(QtWidgets.QTableWidget):
        head = t.horizontalHeaderItem(1)
        if head is not None and head.text() == vpm.T('new file name'):
            return dict((t.item(r, 0).text(), t.cellWidget(r, 1))
                        for r in range(t.rowCount())
                        if t.item(r, 0) is not None and isinstance(
                            t.cellWidget(r, 1), QtWidgets.QLineEdit))
    return {}


def names():
    """What each camera's name field reads now."""
    return dict((k, w.text()) for k, w in name_fields().items())


def action_named(text):
    """A menu entry by its wording, & marks left out."""
    for w in app.allWidgets():
        for a in w.actions():
            if a.text().replace("&", "").strip() == text:
                return a
    return None


def multitrack_box():
    """The Multitrack tick itself, by its wording."""
    for w in win().findChildren(QtWidgets.QCheckBox):
        if w.text() == vpm.T('Multitrack (one track per speaker)'):
            return w
    return None


def waited_for(condition, why):
    """Turn the loop until *condition* holds; the seconds, or None."""
    began_here = time.time()
    while time.time() - began_here < PATIENCE:
        app.processEvents()
        if condition():
            return time.time() - began_here
        time.sleep(0.02)
    print("      gave up after %.1f s waiting for %s" % (PATIENCE, why))
    return None


def saved():
    """The project file as it lies on the disk now."""
    try:
        with open(PROJECT, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def seconds(took):
    """How long a wait took, or that it gave up."""
    return "gave up" if took is None else "%.2f s" % took


def voices():
    """The voice rules in memory: renumbering, and a proposal."""
    print("\n3. The voices")
    stand_in = vpm.T('Speaker %d') % 2
    kept = vpm.voice_name_free(stand_in, [stand_in], True)
    check("a typed stand-in beside the same name is not renumbered",
          kept == stand_in, "it became %r, wanted %r" % (kept, stand_in))
    source, label = os.path.join(folder, "Room.wav"), "SPEAKER_00"
    key = vpm.voice_key(source, label)
    marks = vpm.voice_marks_of({})
    typed = vpm.voice_typed_back({"voice_marks": marks},
                                 {"voicetyped:" + key: True}, key)
    lines = [(key, vpm.SpeakerName(stand_in), vpm.Value(""))]
    vpm.voice_proposal_apply(lines, {label: vpm.T('Guest')}, set(), marks,
                             source)
    check("a stand-in typed and kept in the file outlives a proposal",
          typed and lines[0][1].get() == stand_in,
          "marked typed %r; the field reads %r, wanted %r"
          % (typed, lines[0][1].get(), stand_in))


over = {"done": False}


def drive():
    win().show()
    win().resize(1400, 900)
    opening = action_named(vpm.T('Open project ...'))
    if opening is not None:
        opening.trigger()
    took = waited_for(lambda: len(names()) == 3, "the three name fields")
    now = names()
    print("1. A project file opened")
    check("the sheet came up with the three cameras' name fields",
          len(now) == 3, "%d name fields (%s): %r"
          % (len(now), seconds(took), now))
    check("a name from an older file the table never offered stays",
          now.get("C0002.MP4") == "C0002 2",
          "the field says %r, wanted 'C0002 2'; all %r"
          % (now.get("C0002.MP4"), now))
    check("a name marked as the table's own follows the table",
          now.get("C0003.MP4") == "C0003",
          "the field says %r, wanted 'C0003'; all %r"
          % (now.get("C0003.MP4"), now))

    print("\n2. A name typed into the table")
    field = name_fields().get("C0003.MP4")
    if field is not None:
        field.setText("C0003 7")
    box = multitrack_box()
    if box is not None:
        box.setChecked(True)
    took = waited_for(lambda: name_fields().get("C0003.MP4")
                      not in (None, field), "the table rebuilt")
    now = names()
    check("a name typed shaped like the offer stays through a rebuild",
          now.get("C0003.MP4") == "C0003 7",
          "the field says %r, wanted 'C0003 7'; all %r (%s)"
          % (now.get("C0003.MP4"), now, seconds(took)))
    check("one the file marks typed stays where the offer moved on",
          now.get("C0001.MP4") == "C0001",
          "the field says %r, wanted 'C0001'; all %r (%s)"
          % (now.get("C0001.MP4"), now, seconds(took)))
    saving = action_named(vpm.T('Save project'))
    if saving is not None:
        saving.trigger()
    took = waited_for(lambda: saved().get("version") == vpm.VERSION,
                      "the save")
    kept = saved().get("assignment") or {}
    check("the project file keeps it, marked as typed",
          kept.get("video:" + CAMS[2]) == "C0003 7"
          and kept.get("videotyped:" + CAMS[2]) is True,
          "the file holds %r marked %r, wanted 'C0003 7' marked True (%s)"
          % (kept.get("video:" + CAMS[2]),
             kept.get("videotyped:" + CAMS[2]), seconds(took)))
    voices()
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
    shutil.rmtree(folder, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
