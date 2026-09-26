# -*- coding: utf-8 -*-
"""The sheet's reasons stand whole, in grey, in or under their field.

A window over a project that locks something in every way the sheet
can: a camera nobody speaks on, one with no sound, an intro, a recording
set to "do not use". Each field is asked what it draws, the Kind field's
line under it what it reads, and the grey ink is counted there; a shut
field draws no value under it and does not grow; a barred entry is asked
with its list open and shut; at the window's smallest that line is whole.
English and German, and a third window marks the wide shot. Offscreen.
In the builder's release run an open list too narrow for its entry is
noted rather than failed: cut_off_rule.py.
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
import json
import subprocess
import tempfile
import time
import wave
import cut_off_rule
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


def check(name, ok, extra="", cut_off=False):
    global done
    done += 1
    # A text cut off is noted, not failed, in the builder's release run
    # alone; cut_off_rule.py says whose rule it is and when.
    noted = not ok and cut_off and cut_off_rule.noted(name, extra)
    print("  %-58s %s %s" % (name, "ok" if ok else "noted" if noted
                             else "FAIL", extra))
    if not ok and not noted:
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
            # Its judgements, a traceback and a NOTED line run.sh collects;
            # ffmpeg's chatter stays out.
            if line[61:63] == "ok" or line[61:65] == "FAIL" \
                    or line[61:66] == "noted" or line.startswith(
                        ("Traceback", "  File ", "NOTED cut off: ")):
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


def line_under(w):
    """The reason line in the table cell that holds *w*, or None."""
    here = w.parentWidget()
    for _ in range(3):
        if here is None:
            return None
        line = here.findChild(QtWidgets.QLabel, "reason_line")
        if line is not None:
            return line
        here = here.parentWidget()
    return None


def reads(line):
    """What the line says, without the places it may wrap at."""
    return line.text().replace("\u200b", "") if line else ""


def grey(line):
    """Pixels near the grey of the reasons anywhere on the line."""
    if line is None:
        return 0
    image = line.grab().toImage()
    want = QtGui.QColor(vpm.COLOURS["quiet"])
    near = 0
    for x in range(image.width()):
        for y in range(image.height()):
            c = image.pixelColor(x, y)
            if (abs(c.red() - want.red()) + abs(c.green() - want.green())
                    + abs(c.blue() - want.blue())) < 60:
                near += 1
    return near


def judge_smallest(lang):
    """At the window's smallest, the line under the Kind field is whole.

    The table and the sheet are scrolled to that field first, as a hand
    would: what lies past an edge is a scroll away, not cut.
    """
    kind_w = field('Kind', "W_cam.mov")
    line = line_under(kind_w) if kind_w else None
    if line is None:
        check("at the smallest window the reason under Kind is whole",
              False, "%s: no line under the Kind field, window %dx%d"
              % (lang, win().width(), win().height()))
        return
    table = line.parentWidget()
    while table is not None and not isinstance(table,
                                               QtWidgets.QTableWidget):
        table = table.parentWidget()
    holder = kind_w.parentWidget().parentWidget()
    for row in range(table.rowCount()):
        if table.cellWidget(row, 3) is holder:
            table.scrollTo(table.model().index(row, 3))
    app.processEvents()
    sheet = table.parentWidget()
    while sheet is not None and not isinstance(sheet, QtWidgets.QScrollArea):
        sheet = sheet.parentWidget()
    if sheet is not None:
        sheet.ensureWidgetVisible(line)
    app.processEvents()
    text = reads(line)
    tall = line.heightForWidth(line.width())
    wide = line.fontMetrics().horizontalAdvance(text)
    seen = line.visibleRegion().boundingRect()
    check("at the smallest window the reason under Kind is whole",
          tall <= seen.height() and min(wide, line.width()) <= seen.width(),
          "%s: window %dx%d, %r needs %dx%d px on a line of %d px, "
          "%dx%d of it can be seen"
          % (lang, win().width(), win().height(), text, min(
              wide, line.width()), tall, line.width(), seen.width(),
             seen.height()))


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
    said, inside = reads(line_under(kind_w)), vpm.why_shown(kind_w)[0]
    check("a camera nobody speaks on says so under its Kind field",
          said == vpm.T('no speaker') and inside == "",
          "%s: the line under it reads %r, the field draws %r; wanted %r "
          "under it and nothing in it"
          % (lang, said, inside, vpm.T('no speaker')))
    check("in grey, under that field", grey(line_under(kind_w)) >= 6,
          "%s: %d grey pixels on the line under it"
          % (lang, grey(line_under(kind_w))))
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
          "%s: list %d px, the entry needs %d px" % (lang, wide, needs),
          cut_off=True)
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
    said = reads(line_under(kind_w))
    check("a marked wide shot camera says so under its Kind field",
          said == vpm.T('no speaker')
          and kind_w.currentData() == vpm.TYPE_WIDE,
          "the line under it reads %r on %r, wanted %r on %r" % (
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
    seen = (grey(line_under(kind_w)), ink(moved), ink(line))
    check("in grey, under the one field and inside the other two",
          min(seen) >= 6, "%d, %d and %d grey pixels" % seen)
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
        app.quit()
        return
    judge(LANG)
    state["still"], state["size"] = 0, None
    win().resize(1, 1)
    QtCore.QTimer.singleShot(200, smallest)


def smallest():
    """Wait for the window dragged small to hold its size, then judge.

    Given up into the judgement after 60 turns rather than instead of it.
    """
    state["round"] += 1
    now = (win().width(), win().height())
    state["still"] = state["still"] + 1 if now == state["size"] else 0
    state["size"] = now
    if state["still"] < 3 and state["round"] < 300:
        QtCore.QTimer.singleShot(100, smallest)
        return
    judge_smallest(LANG)
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
