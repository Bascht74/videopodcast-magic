# -*- coding: utf-8 -*-
"""The project type is chosen once, and the later tabs take its shape.

Cut by speaker or sync only. In order: the field on the production
strip offers the two and an empty entry; while it is empty Start is
grey and the footer says so; the first look at the assignment tab asks
once through the hook a test answers, a look that chose nothing is not
asked again, a new production asks afresh and the answer lands in the
field; sync only hides the speaker name column and the Multitrack line
and greys the cut tab under one sentence, its preview and wide shot
note standing empty -- and with the speakers go
"belongs to" and the camera's audio source, while the new file name
stays, since it names the file on every path, and a camera nobody is
on is offered its own stem there; back on cut it all returns, and the
Multitrack tick offers such a camera the full mix instead, a typed
name staying; the type goes round through the project file; a file from
before the question reads as cut and asks nothing, and the full-mix
name it saved for such a camera gives way to the stem while a name
typed into it stays; and the Resolve
button's tip names the cut only where there is one. The question's own
box is never opened here -- the hook stands in for it, so its wording and
buttons are not judged; and the suite runs without the separation, so
the Speakers column it would hide is not on any tree here.
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
import the_program
from let_go import clean_up
SCRIPT = the_program.SCRIPT
import json, shutil, subprocess, sys, tempfile, wave
import numpy as np
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtGui, QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
app.setQuitOnLastWindowClosed(False)
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.say_dialog = lambda *a, **k: True     # no dialog waits for anybody

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


RATE, SEC = 48000, 4
folder = tempfile.mkdtemp(prefix="vpm_type_")
out_folder = os.path.join(folder, "Ergebnis")
os.makedirs(out_folder, exist_ok=True)


def tone(name, hz=300.0):
    path = os.path.join(folder, name)
    t = np.arange(SEC * RATE) / float(RATE)
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes((0.4 * np.sin(2 * np.pi * hz * t) * 32767)
                      .astype("<i2").tobytes())
    return path


def clip(name):
    path = os.path.join(folder, name)
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                    "testsrc=size=160x90:rate=25:duration=%d" % SEC,
                    "-f", "lavfi", "-i",
                    "sine=frequency=300:duration=%d" % SEC,
                    "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
                    "yuv420p", "-c:a", "aac", "-shortest", "-y", path],
                   check=True)
    return path


audio = tone("A_speaker.wav")
one, two = clip("B_camera.mov"), clip("C_camera.mov")
# A file from before the question: no project_type key at all. Away
# from the material, or adding the files would offer it as theirs --
# the offer looks into the folders beside the files as well.
elsewhere = tempfile.mkdtemp(prefix="vpm_type_older_")
older = os.path.join(elsewhere, "videopodcast-magic_Older.json")
saved = os.path.join(elsewhere, "videopodcast-magic_Saved.json")
with open(older, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "version": "test",
               "timeline": [],
               "files": [{"path": audio, "kind": "audio"},
                         {"path": one, "kind": "video"},
                         {"path": two, "kind": "video"}],
               "out_folder": "", "production": "Older",
               "multitrack": False, "preset": "",
               # Saved before the stem: every field went into the file,
               # a suggestion nobody touched as well as a typed name.
               "assignment": {"video:" + one: "B_camera_Audio-Full-Mix",
                              "video:" + two: "Kept_name"}}, f)
# Which file the Open project dialog answers with: set per step.
opening = [older]
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (opening[0], ""))
QtWidgets.QFileDialog.getOpenFileNames = staticmethod(
    lambda *a, **k: ([audio, one, two], ""))
QtWidgets.QFileDialog.getExistingDirectory = staticmethod(
    lambda *a, **k: out_folder)
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok

# The question, answered here instead of in a box: how often it was
# asked, and what it is answered with. The window reaches the box
# through PROJECT_TYPE_ASK, which it fills itself while it is built, so
# what stands in is the box's own function, by name.
asked = []
answer = [""]
vpm.project_type_question = lambda window: (asked.append(1), answer[0])[1]


def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def button(word):
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(word):
            return w


def menu_action(text):
    """A menu entry by its wording, wherever in the bar it sits."""
    for a in win().findChildren(QtGui.QAction):
        if a.text().replace("&", "").strip().startswith(text):
            return a


def name_field():
    """The production name: the only field 340 wide."""
    for w in win().findChildren(QtWidgets.QLineEdit):
        if w.width() == 340 or w.maximumWidth() == 340:
            return w


def footer_note():
    """The state line under the sheets, above the start button."""
    for w in win().findChildren(QtWidgets.QLabel):
        if w.objectName() == "start_note":
            return w


def tab_bar():
    for tw in win().findChildren(QtWidgets.QTabWidget):
        if tw.count() and tw.tabText(0).startswith(
                vpm.T('Files && production')):
            return tw


def type_box():
    """The project type field: the drop-down carrying the two names."""
    for box in win().findChildren(QtWidgets.QComboBox):
        values = [box.itemData(i) for i in range(box.count())]
        if "cut" in values and "sync" in values:
            return box


def entries(box):
    return [(box.itemText(i), box.itemData(i)) for i in range(box.count())]


def pick(box, value):
    """Choose an entry the way somebody at the screen chooses it."""
    for i in range(box.count()):
        if box.itemData(i) == value:
            box.setCurrentIndex(i)
            app.processEvents()
            return True
    return False


def heads(t):
    """The column heads of a tree view, in order."""
    m = t.model()
    return [m.headerData(c, QtCore.Qt.Horizontal)
            for c in range(m.columnCount())]


def tree():
    """The recording tree on the assignment tab, by its first head.

    A view over a model, not a QTreeWidget: the file list is the one
    QTreeWidget, and this one is told apart by its first head.
    """
    for t in win().findChildren(QtWidgets.QTreeView):
        if t.model() is not None and (heads(t) or [""])[0] \
                == vpm.T('Audio recording'):
            return t


def head_hidden(t):
    """Which of the tree's column heads are hidden, by name."""
    return [name for c, name in enumerate(heads(t)) if t.isColumnHidden(c)]


def camera_table():
    """The camera table on the assignment tab, by its first head."""
    for t in win().findChildren(QtWidgets.QTableWidget):
        item = t.horizontalHeaderItem(0)
        if item is not None and item.text() == vpm.T('Camera'):
            return t


def table_hidden(t):
    """Which of the table's column heads are hidden, by name."""
    return [t.horizontalHeaderItem(c).text() for c in range(t.columnCount())
            if t.isColumnHidden(c)]


def file_names():
    """The camera table's new file name fields, by the camera's file."""
    t = camera_table()
    return {t.item(r, 0).text(): getattr(t.cellWidget(r, 1), "text",
                                         lambda: None)()
            for r in range(t.rowCount())}


def multitrack_box():
    """The Multitrack tick itself, by its wording."""
    for w in win().findChildren(QtWidgets.QCheckBox):
        if w.text() == vpm.T('Multitrack (one track per speaker)'):
            return w


def multitrack_line():
    """The line holding the Multitrack tick: what sync only hides."""
    for w in win().findChildren(QtWidgets.QCheckBox):
        if w.text() == vpm.T('Multitrack (one track per speaker)'):
            return w.parentWidget()


def group(title):
    for g in win().findChildren(QtWidgets.QGroupBox):
        if g.title() == title:
            return g


def preview_group():
    ending = (vpm.T('%s -- preview') % "").strip()
    for g in win().findChildren(QtWidgets.QGroupBox):
        if g.title().endswith(ending):
            return g


SENTENCE = vpm.T('Sync only: no cut. The handover carries the multicam '
                 'timeline alone; the Resolve project is created from '
                 'the Output tab.')


def sync_sentence():
    for w in win().findChildren(QtWidgets.QLabel):
        if w.text() == SENTENCE:
            return w


def preview_words():
    """The preview's own sentence: the one rich-text label that wraps."""
    for w in preview_group().findChildren(QtWidgets.QLabel):
        if w.textFormat() == QtCore.Qt.RichText and w.wordWrap():
            return w.text()
    return "(no such label in the preview box)"


def wide_note_words():
    """The line under the wide shot settings saying why they are grey."""
    for w in win().findChildren(QtWidgets.QLabel):
        if w.objectName() == "wide_note":
            return w.text()
    return "(no wide shot note)"


def preview_ran(limit=30.0):
    """Let the preview's timer run out; what was waited, for the line.

    The preview is written 400 ms after a change, by a timer of its
    own -- the one single shot of that interval. Judged either way.
    """
    timers = [t for t in win().findChildren(QtCore.QTimer)
              if t.isSingleShot() and t.interval() == 400]
    clock = time.time()
    while any(t.isActive() for t in timers) \
            and time.time() - clock < limit:
        app.processEvents()
        QtCore.QThread.msleep(20)
    return "%d preview timer(s), one still running: %r, after %.1f s" % (
        len(timers), any(t.isActive() for t in timers), time.time() - clock)


def project_files():
    return sorted(n for n in os.listdir(out_folder)
                  if n.startswith(vpm.PROJECT_PREFIX) and n.endswith(".json"))


def tab_to(index):
    tab_bar().setCurrentIndex(index)
    app.processEvents()


n = [0]
waited = [0]
LIMIT = 120     # rounds of 500 ms: the builder is nine times slower


def wait_for(ready, then, what):
    """Poll for *ready* every half second, red once patience is out."""
    if ready():
        waited[0] = 0
        then()
        return
    waited[0] += 1
    if waited[0] > LIMIT:
        check("what a step waited for came", False,
              "%s never came in %d rounds of 500 ms" % (what, waited[0]))
        app.quit()
        return
    QtCore.QTimer.singleShot(500, lambda: wait_for(ready, then, what))


def step():
    i = n[0]; n[0] += 1
    try:
        if i == 0:
            win().show(); win().resize(1400, 900); app.processEvents()
            print("\n1. The field on the production strip")
            box = type_box()
            check("the project type field stands on the first tab",
                  box is not None,
                  "%d drop-downs, none with both cut and sync"
                  % len(win().findChildren(QtWidgets.QComboBox)))
            check("it offers the two types and an empty entry",
                  [d for _t, d in entries(box)] == ["", "cut", "sync"],
                  "%s" % entries(box))
            check("the two are named as the manual names them",
                  [t for t, _d in entries(box)][1:]
                  == [vpm.T('Cut by speaker'), vpm.T('Sync only')],
                  "%s" % entries(box))
            check("and it starts on the empty entry",
                  box.currentData() == "", repr(box.currentText()))
            button("Add files").click()
            wait_for(lambda: tree() is not None, step, "the tables")
            return
        elif i == 1:
            name_field().setText("Type"); app.processEvents()
            print("\n2. Start is grey while nothing is chosen")
            note = footer_note()
            check("Start is grey with files and a name but no type",
                  not button("Start").isEnabled(),
                  "Start enabled %r, type %r, name %r"
                  % (button("Start").isEnabled(), type_box().currentData(),
                     name_field().text()))
            check("and the footer says the type is missing",
                  note.isVisible()
                  and vpm.T('No project type chosen yet.') in note.text(),
                  repr(note.text()))
            print("\n3. The first look at the assignment tab asks once")
            tab_to(1)
            check("switching to the assignment tab asks through the hook",
                  len(asked) == 1, "asked %d times" % len(asked))
            check("choosing nothing leaves the field empty",
                  type_box().currentData() == "",
                  "the field holds %r after answering %r"
                  % (type_box().currentData(), answer[0]))
            tab_to(0); tab_to(1)
            check("a look that chose nothing is not asked again",
                  len(asked) == 1, "asked %d times" % len(asked))
            # Closed and added again: a new production is a new question.
            menu_action("Close project").trigger(); app.processEvents()
            answer[0] = "sync"
            button("Add files").click()
            wait_for(lambda: tree() is not None, step, "the tables again")
            return
        elif i == 2:
            name_field().setText("Type"); app.processEvents()
            tab_to(1)
            check("a new production asks afresh",
                  len(asked) == 2, "asked %d times" % len(asked))
            check("and the answer lands in the field",
                  type_box().currentData() == "sync",
                  "the field holds %r after answering %r"
                  % (type_box().currentData(), answer[0]))
            check("so Start is live", button("Start").isEnabled(),
                  "Start enabled %r, footer %r"
                  % (button("Start").isEnabled(), footer_note().text()))
            print("\n4. Sync only: no speakers, no cut")
            t = tree()
            check("the Speaker name column is hidden",
                  vpm.T('Speaker name') in head_hidden(t),
                  "hidden heads %s of %d columns"
                  % (head_hidden(t), len(heads(t))))
            check("and the belongs-to column with it",
                  vpm.T('belongs to') in head_hidden(t),
                  "hidden heads %s of %d columns"
                  % (head_hidden(t), len(heads(t))))
            cams = camera_table()
            check("under sync only the camera table shows the new file name",
                  vpm.T('new file name') not in table_hidden(cams),
                  "hidden heads %s of %d columns"
                  % (table_hidden(cams), cams.columnCount()))
            check("but hides where the camera gets its audio from",
                  vpm.T('gets audio from') in table_hidden(cams),
                  "hidden heads %s of %d columns"
                  % (table_hidden(cams), cams.columnCount()))
            names = file_names()
            check("under sync only a camera nobody is on keeps its own stem",
                  names.get("C_camera.mov") == "C_camera",
                  "the field says %r, wanted 'C_camera'; all fields %s"
                  % (names.get("C_camera.mov"), names))
            check("the Multitrack line is hidden",
                  multitrack_line().isHidden(),
                  "hidden %r" % multitrack_line().isHidden())
            check("the Auphonic box stays",
                  not group(vpm.T('Processing at auphonic.com '
                                  '(optional)')).isHidden(),
                  "hidden %r"
                  % group(vpm.T('Processing at auphonic.com '
                                '(optional)')).isHidden())
            tab_to(2)
            check("the cut tab carries the one sentence",
                  sync_sentence() is not None
                  and not sync_sentence().isHidden(),
                  "found %r" % (sync_sentence() is not None))
            check("the Speaker box is greyed",
                  not group(vpm.T('Speaker')).isEnabled(),
                  "enabled %r" % group(vpm.T('Speaker')).isEnabled())
            check("the preview box is greyed",
                  preview_group() is not None
                  and not preview_group().isEnabled(),
                  "enabled %r" % (preview_group() is not None
                                  and preview_group().isEnabled()))
            waited_for = preview_ran()
            check("under sync only the preview promises no speakers",
                  preview_words() == "",
                  "the preview says %r; %s"
                  % (preview_words()[:90], waited_for))
            check("nor does the wide shot note ask for a wide shot",
                  wide_note_words() == "",
                  "the note says %r" % wide_note_words()[:90])
            print("\n5. Back on cut everything returns")
            tab_to(0)
            pick(type_box(), "cut")
            tab_to(1)
            t = tree()
            check("the Speaker name column is back",
                  vpm.T('Speaker name') not in head_hidden(t),
                  "hidden heads %s of %d columns"
                  % (head_hidden(t), len(heads(t))))
            check("belongs to and the audio source column are back",
                  vpm.T('belongs to') not in head_hidden(t)
                  and table_hidden(camera_table()) == [],
                  "hidden heads %s in the tree, %s in the camera table"
                  % (head_hidden(t), table_hidden(camera_table())))
            check("the Multitrack line is back",
                  not multitrack_line().isHidden(),
                  "hidden %r" % multitrack_line().isHidden())
            waited_for = preview_ran()
            check("and the preview speaks again",
                  preview_words() != "",
                  "the preview says %r; %s"
                  % (preview_words()[:90], waited_for))
            t = camera_table()
            [t.cellWidget(r, 1) for r in range(t.rowCount())
             if t.item(r, 0).text() == "C_camera.mov"][0].setText(
                 "Typed_name")
            multitrack_box().setChecked(True); app.processEvents()
            names = file_names()
            check("with Multitrack it is offered the full mix instead",
                  names.get("B_camera.mov") == "B_camera_Audio-Full-Mix",
                  "the field says %r, wanted 'B_camera_Audio-Full-Mix'; all "
                  "fields %s" % (names.get("B_camera.mov"), names))
            check("while a name typed before the tick stays",
                  names.get("C_camera.mov") == "Typed_name",
                  "the field says %r, wanted 'Typed_name'; all fields %s"
                  % (names.get("C_camera.mov"), names))
            multitrack_box().setChecked(False); app.processEvents()
            tab_to(2)
            check("the sentence is gone from the cut tab",
                  sync_sentence() is None or sync_sentence().isHidden(),
                  "hidden %r" % (sync_sentence() is None
                                 or sync_sentence().isHidden()))
            check("and the Speaker box is live again",
                  group(vpm.T('Speaker')).isEnabled(),
                  "enabled %r" % group(vpm.T('Speaker')).isEnabled())
            print("\n6. The type goes round through the project file")
            tab_to(0)
            pick(type_box(), "sync")
            button("Output folder").click(); app.processEvents()
            menu_action("Save project").trigger(); app.processEvents()
            wait_for(lambda: project_files(), step, "the project file")
            return
        elif i == 3:
            names = project_files()
            written = json.load(open(os.path.join(out_folder, names[0]),
                                     encoding="utf-8"))
            check("the project file carries the type",
                  written.get("project_type") == "sync",
                  "project_type %r in %s" % (written.get("project_type"),
                                             names[0]))
            # Kept aside: opening another project moves this file along
            # with the production name, and it is opened again below.
            shutil.copy(os.path.join(out_folder, names[0]), saved)
            opening[0] = older
            button("Open project").click()
            wait_for(lambda: name_field().text() == "Older", step,
                     "the older project")
            return
        elif i == 4:
            print("\n7. A file from before the question reads as cut")
            check("an older file without the key opens as cut by speaker",
                  type_box().currentData() == "cut",
                  "the field holds %r" % type_box().currentData())
            tab_to(1)
            check("and the assignment tab asks nothing",
                  len(asked) == 2, "asked %d times in all" % len(asked))
            names = file_names()
            check("its saved full-mix name gives way to the stem",
                  names.get("B_camera.mov") == "B_camera",
                  "the field says %r, wanted 'B_camera'; all fields %s"
                  % (names.get("B_camera.mov"), names))
            check("while a name typed into the file stays",
                  names.get("C_camera.mov") == "Kept_name",
                  "the field says %r, wanted 'Kept_name'; all fields %s"
                  % (names.get("C_camera.mov"), names))
            check("Start is live on the older project",
                  button("Start").isEnabled(),
                  "Start enabled %r, footer %r"
                  % (button("Start").isEnabled(), footer_note().text()))
            opening[0] = saved
            button("Open project").click()
            wait_for(lambda: name_field().text() == "Type", step,
                     "the saved project")
            return
        elif i == 5:
            check("the saved file brings sync only back",
                  type_box().currentData() == "sync",
                  "the field holds %r" % type_box().currentData())
            tab_to(1)
            t = tree()
            check("and its tables come up without the speaker column",
                  t is not None and vpm.T('Speaker name') in head_hidden(t),
                  "hidden heads %s" % (head_hidden(t) if t else "no tree"))
            print("\n8. What the Resolve button says it does")
            # The tip stands on the button only with a handover file
            # from a run, which no window here has; so the sentence is
            # asked of the piece that chooses it.
            check("under sync only the Resolve tip says there is no cut",
                  vpm.T('Sync only') in vpm.resolve_what_for(True)
                  and vpm.T('Cut, EDL') not in vpm.resolve_what_for(True),
                  repr(vpm.resolve_what_for(True)))
            check("and under cut it speaks of the cut",
                  vpm.resolve_what_for(False).startswith(vpm.T('Cut, EDL')),
                  repr(vpm.resolve_what_for(False)))
            app.quit(); return
    except Exception:
        import traceback; traceback.print_exc()
        bad.append("crash"); app.quit(); return
    QtCore.QTimer.singleShot(600, step)


QtCore.QTimer.singleShot(700, step)
QtCore.QTimer.singleShot(240000, app.quit)


sys.argv = ["videopodcast_magic.py"]
vpm.gui()
clean_up(folder)
shutil.rmtree(elsewhere)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
