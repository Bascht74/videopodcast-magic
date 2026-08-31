# -*- coding: utf-8 -*-
"""What is typed into the window reaches the project file and comes back.

Every setting had a test where it is made and the project file had one
for its shape, but nothing took the whole window round the circle. In
order: the files, the production name, the new file name, the Kind and
the speaker name go in through the widgets a person would use; the
window closes and the file is read; a second window that knows nothing
opens it again; and closing the project empties the window while the
file itself stays. Where the first pass writes no file the second
cannot run, and says so rather than passing. The View menu is asked
here as well -- it needs a project open in a window, and this is the
only test that has one.
"""
import os
import time
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, json, shutil, subprocess, sys, tempfile, wave
import numpy as np
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtCore, QtWidgets

began = time.time()
app = QtWidgets.QApplication(sys.argv[:1])
# The window is closed further down, which is how the program writes the
# project file; the last window closing would otherwise take the
# application with it before anything is read back.
app.setQuitOnLastWindowClosed(False)
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
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


def menu_count():
    from PySide6 import QtGui
    return len(win().findChildren(QtGui.QAction))


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


def row_names(t):
    """Every new file name the camera table shows, whatever row it is on.

    The row that becomes the intro loses its name field -- an intro is
    not renamed -- so asking one fixed row for the name asks the wrong
    one as soon as the intro moves.
    """
    if t is None:
        return []
    return [t.cellWidget(r, 1).text() for r in range(t.rowCount())
            if t.cellWidget(r, 1) is not None]


def entry(label_text):
    """A named single-line field anywhere in the window."""
    for w in win().findChildren(QtWidgets.QLineEdit):
        if (w.accessibleName() or "").startswith(label_text):
            return w


def field_names():
    return [(w.accessibleName() or w.placeholderText() or "-")
            for w in win().findChildren(QtWidgets.QLineEdit)]


def project_files():
    return sorted(f for f in os.listdir(out_folder)
                  if f.startswith(vpm.PROJECT_PREFIX))


# What is set, and what has to come back, held by name so the failure can
# say which answer was lost and not that "something" was.
WANTED = {"production": "Rundlauf",
          "camera_name": "Rundlauf_Weit_eigener_Name",
          "kind": None,           # filled in once the box is known
          "speaker": "Die Befragte"}
found = {}

n = [0]
m = [0]
patience = [0]
over = set()


class NotYet(Exception):
    """The window has not caught up; wait and ask again."""


def needed(what, thing):
    """Give the thing back, or say it is not there yet.

    Fixed waits are what makes a window test flap: fast here, slow on
    the builder, and a step that simply failed there would be a red run
    that means nothing. So a step that does not find what it needs is
    run again, up to twenty times, before it is called red.
    """
    if thing is None or thing is False:
        raise NotYet(what)
    return thing


def deadline(which, at):
    """The whole pass has taken a minute: red, and it says where.

    A bare app.quit() here would end the run in the middle and leave
    every check after this point unreached -- and with nothing in `bad`
    the test would print a low count and go out green.
    """
    def fired():
        if which in over:
            return          # the pass is over; this timer is only late
        bad.append("%s never finished: 60 s gone, still at step %d"
                   % (which, at[0]))
        app.quit()
    return fired


def step():
    i = n[0]
    print("   step %d" % i, flush=True)
    try:
        if i == 0:
            win().show(); win().resize(1400, 900); app.processEvents()
            needed("the Add files button", button("Add files")).click()
        elif i == 1:
            # Without an output folder there is nowhere for the project
            # file to go, so it is chosen the way a person chooses it.
            needed("the output folder button",
                   button("Output folder")).click()
        elif i == 2:
            shown = vpm_files()
            here = [os.path.basename(p) for p in ALL
                    if os.path.basename(p) in shown]
            check("all three files that were added stand in the window",
                  len(here) == 3,
                  "%d of 3 there, the window shows %s" % (len(here), shown))
            box = production_field()
            check("the window has a field for the production name",
                  box is not None,
                  "%d single-line fields, named %s"
                  % (len(field_names()), field_names()))
            if box is not None:
                box.setText(WANTED["production"])
                box.editingFinished.emit()
                app.processEvents()
                found["production_widget"] = box
            # A test that cannot set a field must say so, or it reports
            # the program for its own mistake.
            check("the production name typed in stands in the field",
                  box is not None and box.text() == WANTED["production"],
                  "wanted %r, the field holds %r"
                  % (WANTED["production"],
                     None if box is None else box.text()))
        elif i == 3:
            t = needed("the camera table", camera_table())
            check("the camera table holds a row for each of the cameras",
                  t.rowCount() == 2, "%d rows against 2" % t.rowCount())
            # The name on one row, the intro on the other: a clip that
            # becomes the intro loses its name field, taking any name
            # typed into it with it.
            found["name_file"] = (t.item(1, 0).text()
                                  if t.rowCount() > 1 and t.item(1, 0)
                                  else "")
            name = t.cellWidget(1, 1) if t.rowCount() > 1 else None
            check("the camera row carries a field for the new file name",
                  isinstance(name, QtWidgets.QLineEdit),
                  "row 1 (%s) column 1 holds %r"
                  % (found["name_file"] or "no row", name))
            if isinstance(name, QtWidgets.QLineEdit):
                name.setText(WANTED["camera_name"])
                name.editingFinished.emit()
                app.processEvents()
            check("the new file name typed in stands in the field",
                  isinstance(name, QtWidgets.QLineEdit)
                  and name.text() == WANTED["camera_name"],
                  "wanted %r, the field holds %r"
                  % (WANTED["camera_name"],
                     name.text()
                     if isinstance(name, QtWidgets.QLineEdit) else None))
            # Which file the Intro is given to, so the project file can
            # be asked what that one file holds instead of whether some
            # entry begins with "kind:".
            found["kind_file"] = (t.item(0, 0).text()
                                  if t.item(0, 0) else "")
            kind = t.cellWidget(0, 3)
            boxes = (kind.findChildren(QtWidgets.QComboBox)
                     if kind is not None else [])
            check("the Kind column offers a list to choose from",
                  bool(boxes),
                  "row 0 (%s) column 3 holds %r, holding %d drop downs"
                  % (found["kind_file"] or "no row", kind, len(boxes)))
            words = ([boxes[0].itemText(k) for k in range(boxes[0].count())]
                     if boxes else [])
            # Not "Content", which an unanswered file holds anyway, and
            # not the wide shot, which the program derives on its own.
            # Wanted is the answer only a person can give: this clip is
            # the intro.
            for k, word in enumerate(words):
                if "ntro" in word or "orspann" in word:
                    WANTED["kind"] = word
                    # The box shows the label and stores the value; the
                    # project file holds the value.
                    found["kind_value"] = boxes[0].itemData(k)
                    boxes[0].setCurrentIndex(k)
                    break
            check("Intro is one of the kinds on offer",
                  WANTED["kind"] is not None,
                  "%d kinds on offer: %s" % (len(words), words))
            # Nothing tested that a speaker name given by hand ever
            # reaches the file; the made-up names stood there instead.
            said = entry("Speaker name")
            check("the recording carries a field for the speaker name",
                  said is not None,
                  "%d single-line fields, named %s"
                  % (len(field_names()), field_names()))
            if said is not None:
                said.setText(WANTED["speaker"])
                said.editingFinished.emit()
                app.processEvents()
            check("the speaker name typed in stands in the field",
                  said is not None and said.text() == WANTED["speaker"],
                  "wanted %r, the field holds %r"
                  % (WANTED["speaker"],
                     None if said is None else said.text()))
        elif i == 4:
            # The file is written once as soon as the axis is measured,
            # before anybody has typed anything. If closing does not
            # write it again, everything typed since is lost -- so what
            # stands there now is read first, and it is the one file the
            # program promises rather than one of several.
            early = project_files()
            check("one project file stands there before the window closes",
                  len(early) == 1,
                  "%d project files against 1; the folder holds %s"
                  % (len(early), sorted(os.listdir(out_folder))))
            if early:
                found["early"] = early
                found["early_text"] = open(
                    os.path.join(out_folder, early[0])).read()
            # The program hangs its writing on the application quitting,
            # and this test has to stay alive to read the file back, so
            # it emits that signal instead of really quitting.
            win().close()
            app.aboutToQuit.emit()
            app.processEvents()
        elif i == 5:
            box = found.get("production_widget")
            check("the production name stands in the field after closing",
                  box is not None and box.text() == WANTED["production"],
                  "wanted %r, the field holds %r"
                  % (WANTED["production"],
                     None if box is None else box.text()))
            shown = row_names(camera_table())
            check("the new file name stands in the table after closing",
                  WANTED["camera_name"] in shown,
                  "wanted %r, the table shows %s"
                  % (WANTED["camera_name"], shown))
            print("   the fields in the window:")
            for w in win().findChildren(QtWidgets.QLineEdit):
                print("     %-34s %r" % (w.accessibleName() or "-", w.text()))
            names = project_files()
            check("one project file stands in the output folder",
                  len(names) == 1,
                  "%d project files against 1; the folder holds %s"
                  % (len(names), sorted(os.listdir(out_folder))))
            if not names:
                raise SystemExit
            project_path[0] = os.path.join(out_folder, names[0])
            now = open(project_path[0]).read()
            check("closing the window writes the project file again",
                  found.get("early_text") is not None
                  and now != found["early_text"],
                  "%d characters before anything was typed, %d now, and "
                  "they are %s"
                  % (len(found.get("early_text") or ""), len(now),
                     "the same" if now == found.get("early_text")
                     else "different"))
            d = json.loads(now)
            check("the project file names the production",
                  d.get("production") == WANTED["production"],
                  "wanted %r, the file says %r"
                  % (WANTED["production"], d.get("production")))
            check("the project file holds the new file name",
                  WANTED["camera_name"] in now,
                  "%r stands %d times in the %d characters of the file"
                  % (WANTED["camera_name"],
                     now.count(WANTED["camera_name"]), len(now)))
            kinds = dict(
                (os.path.basename(str(k).split(":", 1)[1]), v)
                for k, v in (d.get("assignment") or {}).items()
                if str(k).startswith("kind:"))
            check("the project file keeps the Kind that was chosen",
                  kinds.get(found.get("kind_file")) == found.get("kind_value"),
                  "%s holds %r, chosen was %r; all %d of them: %s"
                  % (found.get("kind_file"),
                     kinds.get(found.get("kind_file")),
                     found.get("kind_value"), len(kinds), kinds))
            check("the project file keeps the speaker name",
                  WANTED["speaker"] in now,
                  "%r stands %d times in the %d characters of the file"
                  % (WANTED["speaker"], now.count(WANTED["speaker"]),
                     len(now)))
        else:
            over.add("the first pass")
            app.quit()
            return
        n[0] += 1
        patience[0] = 0
        QtCore.QTimer.singleShot(700, step)
    except NotYet as why:
        patience[0] += 1
        if patience[0] > 20:
            bad.append("step %d waited for %s: 21 goes over about 10 s, "
                       "and it never came" % (i, why))
            over.add("the first pass")
            app.quit()
            return
        QtCore.QTimer.singleShot(500, step)
    except SystemExit:
        over.add("the first pass")
        app.quit()
    except Exception:
        import traceback; traceback.print_exc()
        bad.append("step %d fell over" % i)
        over.add("the first pass")
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
QtCore.QTimer.singleShot(60000, deadline("the first pass", n))
vpm.gui()

print("\n2. Open it again, in a window that knows nothing")
# A second window, built from nothing: a value can stand in the file and
# never reach the field that shows it.


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
            check("the production name is back in the second window",
                  box.text() == WANTED["production"],
                  "wanted %r, the field holds %r"
                  % (WANTED["production"], box.text()))
            # The View menu names the tabs; a numbered entry tells
            # nobody which tab it is.
            check("the View menu names the tabs and does not number them",
                  menu_action("Files") is not None
                  and menu_action("1. tab") is None,
                  "of %d menu entries, one starting 'Files': %s, one "
                  "starting '1. tab': %s"
                  % (menu_count(), menu_action("Files") is not None,
                     menu_action("1. tab") is not None))
            check("the title bar names the project that is open",
                  os.path.basename(project_path[0]) in win().windowTitle(),
                  "wanted %r in the title, which reads %r"
                  % (os.path.basename(project_path[0]), win().windowTitle()))
        elif i == 2:
            t = needed("the camera table again", camera_table())
            check("the camera table is back with a row for each camera",
                  t.rowCount() == 2, "%d rows against 2" % t.rowCount())
            shown = row_names(t)
            check("the new file name is back in the camera table",
                  WANTED["camera_name"] in shown,
                  "wanted %r, the table shows %s"
                  % (WANTED["camera_name"], shown))
            kinds = []
            for r in range(t.rowCount()):
                cell = t.cellWidget(r, 3)
                for b in (cell.findChildren(QtWidgets.QComboBox)
                          if cell is not None else []):
                    kinds.append(b.currentText())
            check("the Kind that was chosen is back in the drop down",
                  WANTED["kind"] in kinds,
                  "wanted %r among the %d shown: %s"
                  % (WANTED["kind"], len(kinds), kinds))
            said = entry("Speaker name")
            check("the speaker name is back in its field",
                  said is not None and said.text() == WANTED["speaker"],
                  "wanted %r, the field holds %r"
                  % (WANTED["speaker"],
                     None if said is None else said.text()))
        elif i == 3:
            # Closing must leave nothing of the project behind: what
            # stands here is carried into the next production.
            needed("the Close project entry",
                   menu_action("Close project")).trigger()
        elif i == 4:
            check("closing the project empties the file list",
                  not vpm_files(),
                  "%d entries left: %s" % (len(vpm_files()), vpm_files()))
            box = production_field()
            check("closing the project empties the production name",
                  box is None or box.text() == "",
                  "the field holds %r"
                  % ("no field at all" if box is None else box.text()))
            check("closing the project takes it out of the title bar",
                  os.path.basename(project_path[0]) not in win().windowTitle(),
                  "%r should not be in the title, which reads %r"
                  % (os.path.basename(project_path[0]), win().windowTitle()))
            t = camera_table()
            check("closing the project empties the camera table",
                  t is None or t.rowCount() == 0,
                  "%d rows against 0" % (0 if t is None else t.rowCount()))
            there = os.path.exists(project_path[0])
            check("closing the project leaves the file itself in place",
                  there, "%s, %d bytes"
                  % (os.path.basename(project_path[0]),
                     os.path.getsize(project_path[0]) if there else -1))
        else:
            over.add("the second pass")
            app.quit()
            return
        m[0] += 1
        patience[0] = 0
        QtCore.QTimer.singleShot(700, again)
    except NotYet as why:
        patience[0] += 1
        if patience[0] > 20:
            bad.append("second pass, step %d waited for %s: 21 goes over "
                       "about 10 s, and it never came" % (i, why))
            over.add("the second pass")
            app.quit()
            return
        QtCore.QTimer.singleShot(500, again)
    except Exception:
        import traceback; traceback.print_exc()
        bad.append("second pass, step %d fell over" % i)
        over.add("the second pass")
        app.quit()


if project_path[0]:
    adding[:] = []
    QtCore.QTimer.singleShot(500, again)
    QtCore.QTimer.singleShot(60000, deadline("the second pass", m))
    vpm.gui()
else:
    check("the first pass left a project file to open again", False,
          "nothing beginning %r in %s"
          % (vpm.PROJECT_PREFIX, sorted(os.listdir(out_folder))))

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
