# -*- coding: utf-8 -*-
"""Everything that can be set is set, saved, opened again, and asked after.

Sebastian, 30.8.2026, looking at a project he had just opened: *"But the
speakers are not there and everything says wide shot, although the
project file was loaded? Is there no test that saves as many options as
possible and then opens it again and checks whether everything is
there?"*

There was not. Every setting had its own test at the place where it is
made, and the project file had a test for its shape -- but nothing ever
took the whole window round the circle: set it, write it, open it,
compare. A setting that never reaches the file looks exactly like a
setting that was never made, and from inside the window neither is
visible.

So this walks the circle. Each answer is set through the widget a
person would use, the file is written the way the program writes it,
a second reading takes it back, and every single answer is asked after
by name. What cannot come back is named in the failure, not counted.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, json, shutil, subprocess, sys, tempfile, wave
import numpy as np
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
# The window is closed on purpose further down -- that is how the
# program writes the project file -- and the last window closing would
# otherwise take the application with it before anything was read back.
app.setQuitOnLastWindowClosed(False)
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
vpm.say_dialog = lambda *a, **k: True     # no dialog waits for anybody

bad = []


def check(what, ok, detail=""):
    print("  %-56s %s%s" % (what, "ok" if ok else "FAIL",
                            "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


RATE = 48000
folder = tempfile.mkdtemp(prefix="vpm_round_")
out_folder = os.path.join(folder, "Ergebnis")
os.makedirs(out_folder, exist_ok=True)


def tone(name, hz=300.0, seconds=6.0):
    path = os.path.join(folder, name)
    t = np.arange(int(seconds * RATE)) / float(RATE)
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes((0.4 * np.sin(2 * np.pi * hz * t) * 32767)
                      .astype("<i2").tobytes())
    return path


def camera(name, seconds=6):
    path = os.path.join(folder, name)
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                    "smptebars=size=160x90:rate=25:duration=%d" % seconds,
                    "-f", "lavfi", "-i",
                    "sine=frequency=300:duration=%d" % seconds,
                    "-c:v", "libx264", "-preset", "ultrafast",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
                    "-y", path], check=True)
    return path


voice = tone("Gesamtton.wav")
one, two = camera("Weit.mov"), camera("Nah.mov")
ALL = [voice, one, two]

adding = list(ALL)
QtWidgets.QFileDialog.getOpenFileNames = staticmethod(
    lambda *a, **k: (list(adding), ""))
QtWidgets.QFileDialog.getExistingDirectory = staticmethod(
    lambda *a, **k: out_folder)
project_path = [""]
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (project_path[0], ""))


def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def button(text):
    for w in (win().findChildren(QtWidgets.QPushButton)
              + win().findChildren(QtWidgets.QCheckBox)):
        if w.text().strip().startswith(text):
            return w


def menu_action(text):
    """A menu entry by its wording, wherever in the bar it sits."""
    from PySide6 import QtGui
    for a in win().findChildren(QtGui.QAction):
        if a.text().replace("&", "").strip().startswith(text):
            return a


def tables():
    return win().findChildren(QtWidgets.QTableWidget)


def camera_table():
    """The table whose columns are Camera, new file name, ... Kind."""
    for t in tables():
        head = [t.horizontalHeaderItem(i).text()
                if t.horizontalHeaderItem(i) else ""
                for i in range(t.columnCount())]
        if any(h.startswith("Kind") for h in head) and t.rowCount():
            return t


def entry(label_text):
    """A named single-line field anywhere in the window."""
    for w in win().findChildren(QtWidgets.QLineEdit):
        if (w.accessibleName() or "").startswith(label_text):
            return w


# What is set, and what has to come back. Each one is a (name, set, read)
# so the failure can say which answer was lost, not that "something" was.
WANTED = {"production": "Rundlauf",
          "camera_name": "Rundlauf_Weit_eigener_Name",
          "kind": None,           # filled in once the box is known
          "transcript": False,
          "speaker": "Die Befragte"}
found = {}

n = [0]
patience = [0]


class NotYet(Exception):
    """The window has not caught up; wait and ask again."""


def needed(what, thing):
    """Give the thing back, or say it is not there yet.

    Fixed waits are what makes a window test flap. This machine is fast
    and every step was ready inside a second; the builder is not, and a
    step that simply failed there would be a red run that means nothing.
    So a step that does not find what it needs is run again, up to
    twenty times, and only then called red.
    """
    if thing is None or thing is False:
        raise NotYet(what)
    return thing


def step():
    i = n[0]
    print("   step %d" % i, flush=True)
    try:
        if i == 0:
            win().show(); win().resize(1400, 900); app.processEvents()
            needed("the Add files button", button("Add files")).click()
        elif i == 1:
            # The output folder is not guessed any more, and without one
            # there is nowhere for the project file to go. Chosen here
            # the way a person chooses it.
            needed("the output folder button",
                   button("Output folder")).click()
        elif i == 2:
            shown = vpm_files()
            check("the files are in",
                  all(os.path.basename(p) in shown for p in ALL), str(shown))
            box = production_field()
            check("there is a production field", box is not None)
            if box is not None:
                box.setText(WANTED["production"])
                box.editingFinished.emit()
                app.processEvents()
                # Asked back at once. A test that cannot set a field must
                # say so, or it reports the program for its own mistake.
                check("the production name went in",
                      box.text() == WANTED["production"], repr(box.text()))
                found["production_widget"] = box
        elif i == 3:
            t = needed("the camera table", camera_table())
            check("the camera table stands", t is not None and t.rowCount() == 2,
                  "" if t is None else str(t.rowCount()))
            if t is not None:
                # The name on one row, the intro on the other. A clip
                # that becomes the intro leaves the camera table, and
                # with it the name that had been typed into it -- which
                # is right, and which cost this test a run to see.
                name = t.cellWidget(1, 1)
                check("the new file name is a field", name is not None)
                if name is not None:
                    name.setText(WANTED["camera_name"])
                    name.editingFinished.emit()
                    app.processEvents()
                    check("the new file name went in",
                          name.text() == WANTED["camera_name"],
                          repr(name.text()))
                kind = t.cellWidget(0, 3)
                boxes = (kind.findChildren(QtWidgets.QComboBox)
                         if kind is not None else [])
                check("the Kind column is a drop down", bool(boxes))
                if boxes:
                    b = boxes[0]
                    print("   Typen:", [b.itemText(k)
                                        for k in range(b.count())])
                    # Not "Content": that is what an unanswered file
                    # holds anyway, so choosing it proves nothing. And
                    # not the wide shot, which the program derives for a
                    # camera nobody sits in front of. What is wanted is
                    # the answer only a person can give -- this clip is
                    # the intro -- which is the one Sebastian's jingle
                    # needs and the one that was not coming back.
                    for k in range(b.count()):
                        word = b.itemText(k)
                        if ("ntro" in word or "orspann" in word):
                            WANTED["kind"] = word
                            b.setCurrentIndex(k)
                            break
                    check("there is an Intro to choose",
                          WANTED["kind"] is not None,
                          str([b.itemText(k) for k in range(b.count())]))
            # The name of the voice on the recording. This is the one
            # Sebastian missed: his file carried "Sprecher 1" to "4", the
            # names nobody had given, and there was no test that a name
            # given by hand ever reaches the file at all.
            said = entry("Speaker name")
            check("there is a speaker name field", said is not None)
            if said is not None:
                said.setText(WANTED["speaker"])
                said.editingFinished.emit()
                app.processEvents()
                check("the speaker name went in",
                      said.text() == WANTED["speaker"], repr(said.text()))
            tick = button("Fetch transcript")
            if tick is not None and tick.isChecked() != WANTED["transcript"]:
                tick.setChecked(WANTED["transcript"])
        elif i == 4:
            # Is there one already? The axis is measured as soon as the
            # files are in, and that writes the file -- long before
            # anybody has typed anything. If closing does not write it
            # again, everything typed since is lost, and the file looks
            # like a saved project while holding none of the answers.
            early = [f for f in os.listdir(out_folder)
                     if f.startswith(vpm.PROJECT_PREFIX)]
            found["early"] = early
            if early:
                found["early_text"] = open(
                    os.path.join(out_folder, early[0])).read()
            # Written the way the program writes it. The window's close
            # is not the route: the program hangs its writing on the
            # application quitting, and this test has to stay alive to
            # read the file back, so it says the same thing the program
            # says rather than the thing that looks like it.
            win().close()
            app.aboutToQuit.emit()
            app.processEvents()
        elif i == 5:
            box = found.get("production_widget")
            if box is not None:
                check("and the production name still stands there",
                      box.text() == WANTED["production"], repr(box.text()))
            t = camera_table()
            if t is not None and t.cellWidget(0, 1) is not None:
                check("and so does the new file name",
                      t.cellWidget(0, 1).text() == WANTED["camera_name"],
                      repr(t.cellWidget(0, 1).text()))
            print("   Felder im Fenster:")
            for w in win().findChildren(QtWidgets.QLineEdit):
                print("     %-34s %r" % (w.accessibleName() or "-", w.text()))
            names = [f for f in os.listdir(out_folder)
                     if f.startswith(vpm.PROJECT_PREFIX)]
            if found.get("early"):
                now = open(os.path.join(out_folder, found["early"][0])).read()
                check("closing the window writes the file again",
                      now != found.get("early_text"),
                      "byte for byte the one written before anything was "
                      "typed")
            check("a project file was written", bool(names), str(
                os.listdir(out_folder)))
            if not names:
                raise SystemExit
            project_path[0] = os.path.join(out_folder, names[0])
            d = json.load(open(project_path[0]))
            found["file"] = d
            check("it names the production",
                  d.get("production") == WANTED["production"],
                  repr(d.get("production")))
            check("it names the new file",
                  WANTED["camera_name"] in json.dumps(d),
                  "not anywhere in the file")
            check("it keeps the Kind that was chosen",
                  any(str(k).startswith("kind:") for k in
                      (d.get("assignment") or {})),
                  str(sorted(d.get("assignment") or {})[:6]))
            check("it keeps the transcript answer", "transcript" in d,
                  str(sorted(d)))
            check("it keeps the speaker name",
                  WANTED["speaker"] in json.dumps(d, ensure_ascii=False),
                  "not anywhere in the file")
        else:
            app.quit()
            return
        n[0] += 1
        patience[0] = 0
        QtCore.QTimer.singleShot(700, step)
    except NotYet as why:
        patience[0] += 1
        if patience[0] > 20:
            bad.append("step %d waited for %s and it never came" % (i, why))
            app.quit()
            return
        QtCore.QTimer.singleShot(500, step)
    except SystemExit:
        app.quit()
    except Exception:
        import traceback; traceback.print_exc()
        bad.append("step %d fell over" % i)
        app.quit()


def vpm_files():
    for t in win().findChildren(QtWidgets.QTreeWidget):
        if t.topLevelItemCount():
            names = []
            for r in range(t.topLevelItemCount()):
                it = t.topLevelItem(r)
                names.append(it.text(0))
                for j in range(it.childCount()):
                    names.append(it.child(j).text(0))
            if len(names) >= 3:
                return names
    return []


def production_field():
    for w in win().findChildren(QtWidgets.QLineEdit):
        name = (w.accessibleName() or "") + " " + (w.placeholderText() or "")
        if "roduction" in name or "roduktion" in name:
            return w


print("1. Set it and write it")
QtCore.QTimer.singleShot(500, step)
QtCore.QTimer.singleShot(60000, app.quit)
vpm.gui()

print("\n2. Open it again, in a window that knows nothing")
# A second window, built from nothing. Reading the file back is not the
# same question as getting the answers back into the window: a value can
# stand in the file and never reach the field that shows it.
m = [0]


def again():
    i = m[0]
    print("   step %d" % i, flush=True)
    try:
        if i == 0:
            win().show(); win().resize(1400, 900); app.processEvents()
            needed("the Open project button",
                   button("Open project")).click()
        elif i == 1:
            box = needed("the production field", production_field())
            check("the production name is back",
                  box is not None and box.text() == WANTED["production"],
                  repr(box.text()) if box is not None else "no field")
            # The View menu used to say "1. tab, 2. tab, 3. tab", which
            # tells nobody anything. It says what the tabs say now.
            check("the View menu names the tabs, not their numbers",
                  menu_action("Files") is not None
                  and menu_action("1. tab") is None,
                  "no entry starting with the first tab's name")
            check("the title bar names the project",
                  os.path.basename(project_path[0]) in win().windowTitle(),
                  win().windowTitle())
        elif i == 2:
            t = needed("the camera table again", camera_table())
            check("the camera table is back",
                  t is not None and t.rowCount() == 2,
                  "" if t is None else str(t.rowCount()))
            if t is not None:
                names = [t.cellWidget(r, 1).text() for r in range(t.rowCount())
                         if t.cellWidget(r, 1) is not None]
                check("the new file name is back",
                      WANTED["camera_name"] in names, str(names))
                kinds = []
                for r in range(t.rowCount()):
                    cell = t.cellWidget(r, 3)
                    for b in (cell.findChildren(QtWidgets.QComboBox)
                              if cell is not None else []):
                        kinds.append(b.currentText())
                check("the Kind that was chosen is back",
                      WANTED["kind"] in kinds,
                      "wanted %r, found %s" % (WANTED["kind"], kinds))
            said = entry("Speaker name")
            check("the speaker name is back",
                  said is not None and said.text() == WANTED["speaker"],
                  repr(said.text()) if said is not None else "no field")
            tick = button("Fetch transcript")
            check("the transcript answer is back",
                  tick is not None and tick.isChecked() == WANTED["transcript"],
                  "" if tick is None else str(tick.isChecked()))
        elif i == 3:
            # Closing the project must leave nothing of it behind. Until
            # this existed the only way to a second production was to
            # quit the program, and anything left standing here would be
            # carried into the next one.
            needed("the Close project entry",
                   menu_action("Close project")).trigger()
        elif i == 4:
            check("closing empties the file list", not vpm_files(),
                  str(vpm_files()))
            box = production_field()
            check("closing empties the production name",
                  box is None or box.text() == "",
                  repr(box.text()) if box is not None else "")
            check("closing takes the project out of the title bar",
                  os.path.basename(project_path[0]) not in win().windowTitle(),
                  win().windowTitle())
            t = camera_table()
            check("the camera table is gone or empty",
                  t is None or t.rowCount() == 0,
                  "" if t is None else str(t.rowCount()))
            check("the project file itself is untouched",
                  os.path.exists(project_path[0]))
        else:
            app.quit()
            return
        m[0] += 1
        patience[0] = 0
        QtCore.QTimer.singleShot(700, again)
    except NotYet as why:
        patience[0] += 1
        if patience[0] > 20:
            bad.append("second pass, step %d waited for %s" % (i, why))
            app.quit()
            return
        QtCore.QTimer.singleShot(500, again)
    except Exception:
        import traceback; traceback.print_exc()
        bad.append("second pass, step %d fell over" % i)
        app.quit()


if project_path[0]:
    adding[:] = []
    QtCore.QTimer.singleShot(500, again)
    QtCore.QTimer.singleShot(60000, app.quit)
    vpm.gui()
else:
    check("there was a project file to open again", False)

shutil.rmtree(folder, ignore_errors=True)
print("\n----")
if bad:
    print("FAIL %d of them: %s" % (len(bad), "; ".join(bad)))
    sys.exit(1)
print("All good.")
