# -*- coding: utf-8 -*-
"""The sheet's reasons stand in grey inside the field they are about.

A window over a project that locks something in every way the sheet
can: a camera nobody speaks on, one with no sound, an intro, a
recording set to "do not use". Each field is asked what it draws and
the grey ink is counted there; a shut field draws no value under it
and does not grow; a barred entry is asked with its list open and shut.
English and German. A third window marks the wide shot, over a speaker
and a voice on it and a voice set to "do not use". Offscreen, in Qt's
own style.
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
import json
import subprocess
import tempfile
import time
import wave
import the_program

SCRIPT = the_program.SCRIPT

os.environ["QT_QPA_PLATFORM"] = "offscreen"
import numpy as np
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtTest import QTest

began = time.time()
LANG = os.environ.get("VPM_LOCK_LANG", "")
MARKED = os.environ.get("VPM_LOCK_CASE") == "marked"
if MARKED:
    # The suite switches the separation off, and with it the voices;
    # every way into a separation is shut below instead.
    os.environ.pop("VPM_NO_SPEAKER_SPLIT", None)
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language(LANG or "en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.update_offer = lambda *a, **k: None
vpm.run_argv = lambda values, assignment_file_path="": (None, None, [])
vpm.fetch_model = lambda *a, **k: "not in a test"
vpm.speaker_split_available = lambda deep=False: True
vpm.speaker_split_run = lambda *a, **k: ([], "not in a test")
vpm.speaker_cache_read = lambda key: []

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def material(folder):
    """Two recordings and four video files, twelve seconds each."""
    made = {}
    for i, name in enumerate(("Room.wav", "Room2.wav")):
        sound = np.random.default_rng(i + 1).normal(0, 0.1, 12 * 48000)
        made[name] = os.path.join(folder, name)
        with wave.open(made[name], "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(48000)
            f.writeframes((np.clip(sound, -1, 1) * 32767)
                          .astype("<i2").tobytes())
    for name, sound in (("A_cam.mov", True), ("B_cam.mov", False),
                        ("W_cam.mov", True), ("Intro.mp4", True)):
        made[name] = os.path.join(folder, name)
        cmd = ["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
               "testsrc=size=160x90:rate=25:duration=12"]
        if sound:
            cmd += ["-f", "lavfi", "-i", "sine=frequency=300:duration=12",
                    "-c:a", "aac"]
        cmd += ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
                "yuv420p", "-shortest", "-y", made[name]]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    return made


if not LANG:
    # The parent: the material once, then one window per language.
    media = tempfile.mkdtemp(prefix="vpm_locks_")
    material(media)
    for lang, case, what in (("en", "", "In English"),
                             ("de", "", "In German"),
                             ("en", "marked", "A wide shot marked")):
        print("\n%s:" % what)
        try:
            child = subprocess.run(
                [sys.executable, os.path.abspath(__file__)], cwd=HERE,
                env=dict(os.environ, VPM_LOCK_LANG=lang,
                         VPM_LOCK_CASE=case, VPM_LOCK_MEDIA=media,
                         PYTHONUNBUFFERED="1"),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, timeout=140)
            out, code = child.stdout, child.returncode
        except subprocess.TimeoutExpired as gone:
            out, code = str(gone.stdout or ""), "none, stopped after 140 s"
        said = ""
        for line in out.splitlines():
            # Its judgements and a traceback; ffmpeg's chatter stays out.
            if line[61:63] == "ok" or line[61:65] == "FAIL" \
                    or line.startswith(("Traceback", "  File ")):
                print(line[:200])
            said = line[6:] if line.startswith("FAIL: ") else said
            head = line.split(" checks in ")[0]
            if " checks in " in line and head.isdigit():
                done += int(head)
        if code != 0:
            bad.append("the window %r ended with %s: %s"
                       % (what, code, said or "no FAIL line"))
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)
media = os.environ["VPM_LOCK_MEDIA"]
made = dict((n, os.path.join(media, n)) for n in (
    "Room.wav", "Room2.wav", "A_cam.mov", "B_cam.mov", "W_cam.mov",
    "Intro.mp4"))
project = os.path.join(tempfile.mkdtemp(prefix="vpm_locks_%s_" % LANG),
                       "videopodcast-magic_Locks.json")
sheet = {"format": vpm.FILE_FORMAT, "version": "test", "timeline": [],
         "preset": "", "production": "Locks", "multitrack": False,
         "out_folder": os.path.join(os.path.dirname(project), "Result"),
         "files": [{"path": made[n], "kind": "audio"}
                   for n in ("Room.wav", "Room2.wav")]
         + [{"path": made[n], "kind": "video"}
            for n in ("A_cam.mov", "B_cam.mov", "W_cam.mov", "Intro.mp4")]}
# Guest on A_cam, so W_cam has nobody and is the wide shot by derivation;
# Room2 is left out, and Intro.mp4 holds the intro.
sheet["assignment"] = {
    "audio:" + made["Room.wav"]: ["Guest", "A_cam.mov"],
    "audio:" + made["Room2.wav"]: ["", vpm.IGNORE_AUDIO],
    "kind:" + made["Intro.mp4"]: vpm.TYPE_INTRO}
if MARKED:
    # W_cam marked, with Guest and Cleo on it; in Room2 Bo is left out.
    room2 = os.path.abspath(made["Room2.wav"])
    held = os.stat(room2)
    sheet["assignment"] = {
        "audio:" + made["Room.wav"]: ["Guest", "W_cam.mov"],
        "kind:" + made["W_cam.mov"]: vpm.TYPE_WIDE,
        "several:" + room2: True,
        "voice:%s\nSPEAKER_00" % room2: "A_cam.mov",
        "voice:%s\nSPEAKER_01" % room2: vpm.IGNORE_AUDIO,
        "voice:%s\nSPEAKER_02" % room2: "W_cam.mov"}
    sheet["speakers"] = {
        "source": room2, "mtime": int(held.st_mtime), "size": held.st_size,
        "model": vpm.SPEAKER_MODEL_NAME, "model_mark": "",
        "num_speakers": 0,
        "names": {"SPEAKER_00": "Anna", "SPEAKER_01": "Bo",
                  "SPEAKER_02": "Cleo"},
        "segments": [["SPEAKER_00", 1.0, 4.0], ["SPEAKER_01", 5.0, 8.0],
                     ["SPEAKER_02", 9.0, 11.0]]}
with open(project, "w", encoding="utf-8") as f:
    json.dump(sheet, f)
os.makedirs(os.path.join(os.path.dirname(project), "Result"),
            exist_ok=True)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (project, ""))
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


def field(what, file_name):
    """The visible field of that column in that file's row, or None."""
    said = "%s -- %s" % (vpm.T(what), file_name)
    for w in win().findChildren(QtWidgets.QWidget):
        if w.accessibleName() == said and w.isVisible():
            return w
    return None


def inner(w):
    """The line a name is typed into, whichever field carries it."""
    edit = getattr(w, "lineEdit", None)
    return edit() if callable(edit) else w


def ink(w, beyond=False):
    """Pixels near the grey of the reason, where the reason stands.

    With *beyond*, those in the rest of that room, after the reason's own
    width: a value drawn under the reason runs on past it there.
    """
    said, room = vpm.why_shown(w)
    if room is None:
        return 0
    if beyond:
        room.setLeft(room.left() + w.fontMetrics().horizontalAdvance(said)
                     + 3)
    image = w.grab().toImage()
    grey = QtGui.QColor(vpm.COLOURS["quiet"])
    near = 0
    for x in range(max(0, room.left()), min(image.width(), room.right())):
        for y in range(max(0, room.top()),
                       min(image.height(), room.bottom())):
            c = image.pixelColor(x, y)
            if (abs(c.red() - grey.red()) + abs(c.green() - grey.green())
                    + abs(c.blue() - grey.blue())) < 60:
                near += 1
    return near


def judge(lang):
    """Every lock of the sheet, asked in the language now set."""
    kind_w = field('Kind', "W_cam.mov")
    sound_b = field('Camera audio', "B_cam.mov")
    sound_i = field('Camera audio', "Intro.mp4")
    sound_a = field('Camera audio', "A_cam.mov")
    name = field('Speaker name', "Room2.wav")
    kind_a = field('Kind', "A_cam.mov")
    fields = [kind_w, sound_b, sound_i, sound_a, name, kind_a]
    check("the sheet shows every field this project locks",
          None not in fields,
          "%s: %d of 6 found" % (lang, len([f for f in fields if f])))
    if None in fields:
        return
    said = vpm.why_shown(kind_w)[0]
    check("a camera nobody speaks on says so in its Kind field",
          said == vpm.T('no speaker'),
          "%s: draws %r, wanted %r, field %d px"
          % (lang, said, vpm.T('no speaker'), kind_w.width()))
    check("in grey, inside that field", ink(kind_w) >= 6,
          "%s: %d grey pixels where the reason stands"
          % (lang, ink(kind_w)))
    got = (vpm.why_shown(sound_b)[0], vpm.why_shown(sound_i)[0])
    wanted = (vpm.T('no audio track'), vpm.T('a finished clip'))
    under = (ink(sound_b, True), ink(sound_i, True))
    check("a shut Camera audio field says why in place of its value",
          got == wanted and not sound_b.isEnabled()
          and not sound_i.isEnabled() and under == (0, 0),
          "%s: %d and %d grey pixels past the reason, wanted 0 and 0;"
          " shut %s and %s; draws %r, wanted %r"
          % (lang, under[0], under[1], not sound_b.isEnabled(),
             not sound_i.isEnabled(), got, wanted))
    check("in grey, inside those fields",
          ink(sound_b) >= 6 and ink(sound_i) >= 6,
          "%s: %d and %d grey pixels" % (lang, ink(sound_b), ink(sound_i)))
    check("and no wider than an open Camera audio field",
          sound_b.width() == sound_a.width() == sound_i.width(),
          "%s: %d and %d px against %d px open"
          % (lang, sound_b.width(), sound_i.width(), sound_a.width()))
    line = inner(name)
    check("a name field whose track is not used says so in itself",
          vpm.why_shown(line)[0] == vpm.T('not used')
          and line.placeholderText() == "" and not name.isEnabled(),
          "%s: draws %r, wanted %r, guess still shown %r"
          % (lang, vpm.why_shown(line)[0], vpm.T('not used'),
             line.placeholderText()))
    check("in grey, inside that name field", ink(line) >= 6,
          "%s: %d grey pixels" % (lang, ink(line)))
    intro = kind_a.findData(vpm.TYPE_INTRO)
    label = vpm.label_of(vpm.TYPE_INTRO)
    reason = kind_a.itemData(intro, QtCore.Qt.ToolTipRole) or ""
    QTest.mouseClick(kind_a, QtCore.Qt.LeftButton)
    app.processEvents()
    opened = kind_a.itemText(intro)
    wide = kind_a.view().window().width()
    needs = kind_a.view().fontMetrics().horizontalAdvance(opened)
    check("a barred entry says why while its list is open",
          kind_a.view().isVisible() and bool(reason)
          and opened.startswith("%s: %s" % (label, reason[:20])),
          "%s: list open %r, the entry reads %r, its reason %r"
          % (lang, kind_a.view().isVisible(), opened, reason[:40]))
    check("and the open list is wide enough to show it", wide >= needs,
          "%s: list %d px, the entry needs %d px" % (lang, wide, needs))
    kind_a.hidePopup()
    app.processEvents()
    check("and the entry is its caption again once the list shuts",
          kind_a.itemText(intro) == label,
          "%s: reads %r, wanted %r" % (lang, kind_a.itemText(intro), label))


def judge_marked():
    """The marked wide shot, what it moved, a voice left out."""
    kind_w = field('Kind', "W_cam.mov")
    moved = field('belongs to', "Room.wav")
    voice = field('Speaker name', "Bo")
    fields = [kind_w, moved, voice]
    check("the sheet shows the marked camera, a speaker and a voice",
          None not in fields,
          "%d of 3 found" % len([f for f in fields if f]))
    if None in fields:
        return
    said = vpm.why_shown(kind_w)[0]
    check("a camera marked as the wide shot says so in its Kind field",
          said == vpm.T('no speaker')
          and kind_w.currentData() == vpm.TYPE_WIDE,
          "draws %r on %r, wanted %r on %r" % (
              said, kind_w.currentData(), vpm.T('no speaker'),
              vpm.TYPE_WIDE))
    said = vpm.why_shown(moved)[0]
    check("a speaker the mark moved says so in its own field",
          said == vpm.T('moved off the wide shot')
          and moved.currentData() == vpm.MIX_ONLY,
          "draws %r on %r, wanted %r on %r" % (
              said, moved.currentData(), vpm.T('moved off the wide shot'),
              vpm.MIX_ONLY))
    line = inner(voice)
    said = vpm.why_shown(line)[0]
    check("a voice set to do not use says so in its name field",
          said == vpm.T('not used') and not voice.isEnabled(),
          "draws %r, wanted %r, field shut %s"
          % (said, vpm.T('not used'), not voice.isEnabled()))
    grey = (ink(kind_w), ink(moved), ink(line))
    check("in grey, inside those three fields", min(grey) >= 6,
          "%d, %d and %d grey pixels" % grey)
    cleo = field('belongs to', "Cleo")
    said = vpm.why_shown(cleo)[0] if cleo else "no such field"
    check("a voice the mark moved says so, in grey, in its own field",
          cleo is not None and said == vpm.T('moved off the wide shot')
          and cleo.currentData() == vpm.MIX_ONLY and ink(cleo) >= 6,
          "draws %r on %r with %d grey pixels, wanted %r on %r and 6 or "
          "more" % (said, cleo and cleo.currentData(),
                    ink(cleo) if cleo else 0,
                    vpm.T('moved off the wide shot'), vpm.MIX_ONLY))


state = {"round": 0, "widths": None, "still": 0}


def to_sheet():
    """Bring the assignment sheet to the front."""
    for tw in win().findChildren(QtWidgets.QTabWidget):
        for k in range(tw.count()):
            if vpm.T('Assignment && time window')[:8].lower() \
                    in tw.tabText(k).lower():
                tw.setCurrentIndex(k)


def step():
    """Open the project, wait for the sheet to stand still, judge."""
    state["round"] += 1
    if state["round"] == 1:
        win().show()
        win().resize(1400, 900)
        for b in win().findChildren(QtWidgets.QPushButton):
            if b.text().strip().startswith(vpm.T('Open project ...')[:8]):
                b.click()
                break
    to_sheet()
    kind_w = field('Kind', "W_cam.mov")
    now = None if kind_w is None else [
        w.width() for w in win().findChildren(QtWidgets.QComboBox)
        if w.isVisible()]
    # Settled: the fields are there and their widths held for five turns.
    state["still"] = state["still"] + 1 if (
        now and now == state["widths"]) else 0
    state["widths"] = now
    if state["still"] < 5 and state["round"] < 240:
        QtCore.QTimer.singleShot(200, step)
        return
    if MARKED:
        judge_marked()
    else:
        judge(LANG)
    app.quit()


def deadline():
    """An outer brake only: the waiting inside is on the widths."""
    bad.append("the window never finished: 120 s gone, in %s at turn %d"
               % (LANG, state["round"]))
    app.quit()


QtCore.QTimer.singleShot(300, step)
brake = QtCore.QTimer()
brake.setSingleShot(True)
brake.timeout.connect(deadline)
brake.start(120000)
try:
    vpm.gui()
except Exception:
    import traceback
    traceback.print_exc()
    bad.append("the window never came up: gui() fell over")
brake.stop()

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
