# -*- coding: utf-8 -*-
"""Why the start button is grey, and where that is said.

A greyed button with no reason is the commonest dead end in an
interface. The reason has to stand in the footer, not in a tooltip; the
faulty field has to be marked red; the tabs have to be named as they
are labelled; and of two files set to intro the second frees the first.
A camera nobody is assigned to shows a wide shot it never stored, so
this test asks the value behind a field, not its label.
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
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""

# What a Kind field stores, as against what it shows: currentData()
# answers the second question, and the two can differ. clip_kind_bind
# is the one place where the field and the value behind it meet, so
# the value is taken there. Not a copy: the object the window reads.
stored_kind = {}
_clip_kind_bind = vpm.clip_kind_bind


def clip_kind_bind(box, value, after=None):
    stored_kind[box.accessibleName()] = value
    return _clip_kind_bind(box, value, after=after)


vpm.clip_kind_bind = clip_kind_bind

error = []


def check(name, ok, extra=""):
    print("  %-54s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


RATE, SEC = 48000, 4
folder = tempfile.mkdtemp(prefix="vpm_reason_")


def tone(name, hz):
    path = os.path.join(folder, name)
    t = np.arange(SEC * RATE) / float(RATE)
    x = (0.4 * np.sin(2 * np.pi * hz * t) * 32767).astype("<i2")
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes(x.tobytes())
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


audio = tone("A_speaker.wav", 300)
one, two = clip("B_camera.mov"), clip("C_camera.mov")
project = os.path.join(folder, "videopodcast-magic_Interview_2.json")
with open(project, "w", encoding="utf-8") as f:
    json.dump({"format": 3, "version": "test", "timeline": [], "call": [],
               "files": [{"path": audio, "kind": "audio"},
                         {"path": one, "kind": "video"},
                         {"path": two, "kind": "video"}],
               "out_folder": os.path.join(folder, "Ergebnis"),
               "production": "Reason", "multitrack": False,
               "assignment": {}, "preset": ""}, f)
os.makedirs(os.path.join(folder, "Ergebnis"), exist_ok=True)
QtWidgets.QFileDialog.getOpenFileName = staticmethod(
    lambda *a, **k: (project, ""))
QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted


def win():
    for x in app.topLevelWidgets():
        if "Video Podcast Magic" in x.windowTitle():
            return x


def button(word):
    for w in win().findChildren(QtWidgets.QPushButton):
        if w.text().strip().startswith(word):
            return w


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
        if tw.count() >= 2:
            return tw


def tab_titles():
    tw = tab_bar()
    return [tw.tabText(k) for k in range(tw.count())]


def kind_boxes():
    """The type selectors, one per video file.

    The same value has a field on both tabs, so counting widgets would
    say four where there are two files. They are told apart by the
    accessible name: one entry per file, whichever field is met first.
    """
    out, seen = [], set()
    for box in win().findChildren(QtWidgets.QComboBox):
        values = [box.itemData(i) for i in range(box.count())]
        if vpm.TYPE_INTRO not in values:
            continue
        who = box.accessibleName() or str(id(box))
        if who in seen:
            continue
        seen.add(who)
        out.append(box)
    return out


def stored_kinds():
    """What the Kind fields store, in the order the fields stand in.

    Not always what the field shows: the wide shot the program works
    out for itself is shown and not stored.
    """
    return [stored_kind[b.accessibleName()].get() for b in kind_boxes()]


def kind_reason(box):
    """The grey line beside a Kind field, empty where there is none."""
    cell = box.parentWidget()
    return " ".join(w.text().strip() for w in
                    cell.findChildren(QtWidgets.QLabel) if w.text().strip())


def pick(box, value):
    """Choose an entry the way somebody at the screen chooses it.

    Both signals, because currentIndexChanged stays quiet when the
    entry is already the current one, and that is the case here: a
    field showing a derived wide shot has that entry selected already,
    so choosing it is what turns the derivation into a stored answer.
    """
    for i in range(box.count()):
        if box.itemData(i) == value:
            box.setCurrentIndex(i)
            box.activated.emit(i)
            app.processEvents()
            return True
    return False


n = [0]
waited = [0]


def step():
    i = n[0]; n[0] += 1
    try:
        if i == 0:
            win().show(); win().resize(1400, 900); app.processEvents()
            button("Open project").click()
        elif i == 1:
            if name_field() is None and waited[0] < 60:
                waited[0] += 1; n[0] = 1
                QtCore.QTimer.singleShot(500, step); return
            field = name_field()
            check("the production name field is there", field is not None)
            print("\n1. A name is there: nothing outstanding")
            check("no reason in the footer",
                  not footer_note().isVisible(),
                  repr(footer_note().text()))
            check("and the field is not marked",
                  "border" not in (field.styleSheet() or ""),
                  repr(field.styleSheet()))
            print("\n2. The name taken away")
            field.setText("")
            app.processEvents()
            note = footer_note()
            check("the reason stands in the footer, not only in a hint",
                  note.isVisible() and bool(note.text().strip()),
                  repr(note.text()))
            # The state line has to name the reason itself: a tooltip
            # cannot be reached with the keyboard and is not read out
            # reliably.
            check("and it names the reason rather than pointing at one",
                  "tooltip" not in note.text().lower()
                  and len(note.text()) > 20, repr(note.text()))
            check("the field itself is marked red",
                  "border" in (field.styleSheet() or ""),
                  repr(field.styleSheet()))
            check("the field says why when hovered",
                  bool(field.toolTip().strip()), repr(field.toolTip()))
            check("start is grey", not button("Start").isEnabled())
            print("\n3. The reason names the tabs that exist")
            hint = ""
            for w in win().findChildren(QtWidgets.QWidget):
                if button("Start") in w.findChildren(QtWidgets.QPushButton) \
                        and w.toolTip().startswith("Not ready"):
                    hint = w.toolTip()
            check("the hint lists what is missing", bool(hint), repr(hint))
            titles = [t.replace("&&", "&").replace("✓", "").strip()
                      for t in tab_titles()]
            named = [line.split(" -- ")[0].strip()
                     for line in hint.splitlines() if " -- " in line]
            check("every name in it is a tab that exists",
                  bool(named) and all(x in titles for x in named),
                  "%s vs %s" % (named, titles))
            check("no page number from an older layout",
                  not any(x.startswith("2.") for x in named), str(named))
            print("\n4. The tick sits on the tabs that can be complete")
            check("no tick while the name is missing",
                  "✓" not in tab_titles()[0], str(tab_titles()))
            field.setText("Reason")
            app.processEvents()
            check("and it comes back with the name",
                  "✓" in tab_titles()[0], str(tab_titles()))
            check("start is live again", button("Start").isEnabled())
            check("the footer is quiet again",
                  not footer_note().isVisible(), repr(footer_note().text()))
            resolve = [t for t in tab_titles() if "Resolve" in t]
            check("the Resolve tab carries no tick it cannot lose",
                  resolve and "✓" not in resolve[0], str(resolve))
            print("\n5. Only one file can be the intro")
            boxes = kind_boxes()
            check("two video files, two selectors", len(boxes) == 2,
                  str(len(boxes)))
            pick(boxes[0], vpm.TYPE_INTRO)
            n[0] = 2
            QtCore.QTimer.singleShot(1500, step)
            return
        elif i == 2:
            boxes = kind_boxes()
            kinds = stored_kinds()
            check("the first one is the intro",
                  kinds[0] == vpm.TYPE_INTRO
                  and kinds.count(vpm.TYPE_INTRO) == 1, str(kinds))
            pick(boxes[1], vpm.TYPE_INTRO)
            n[0] = 3
            QtCore.QTimer.singleShot(1500, step)
            return
        elif i == 3:
            kinds = stored_kinds()
            check("the second choice frees the first",
                  kinds[1] == vpm.TYPE_INTRO
                  and kinds.count(vpm.TYPE_INTRO) == 1, str(kinds))
            check("and the first one is content again",
                  kinds[0] == vpm.TYPE_CONTENT, str(kinds))
            print("\n6. The wide shot nobody marked: shown, not stored")
            # Nobody is assigned to a camera here, so the first file is
            # the wide shot the program works out for itself.
            free = kind_boxes()[0]
            check("the value stored stays content",
                  stored_kinds()[0] == vpm.TYPE_CONTENT,
                  str(stored_kinds()))
            check("the field shows the wide shot instead",
                  free.currentData() == vpm.TYPE_WIDE,
                  repr(free.currentText()))
            check("greyed, so a derivation cannot pass for an answer",
                  "color" in (free.styleSheet() or ""),
                  repr(free.styleSheet()))
            # The reason sits on the entry it is about, not beside the
            # field: only Content is barred, and the row stays short
            # enough to read.
            check("nothing stands beside it any more",
                  not kind_reason(free), repr(kind_reason(free)))
            check("and Content is the one entry barred",
                  not free.model().item(
                      free.findData(vpm.TYPE_CONTENT)).isEnabled())
            check("with the reason on that entry",
                  bool(free.itemData(free.findData(vpm.TYPE_CONTENT),
                                     QtCore.Qt.ToolTipRole)),
                  repr(free.itemData(free.findData(vpm.TYPE_CONTENT),
                                     QtCore.Qt.ToolTipRole)))
            check("and an intro is still free to choose",
                  free.model().item(
                      free.findData(vpm.TYPE_INTRO)).isEnabled())
            check("the field stays operable all the same",
                  free.isEnabled())
            print("\n7. Choosing what is shown makes it an answer")
            pick(free, vpm.TYPE_WIDE)
            n[0] = 4
            QtCore.QTimer.singleShot(1500, step)
            return
        elif i == 4:
            free = kind_boxes()[0]
            check("now the wide shot is stored, not worked out",
                  stored_kinds()[0] == vpm.TYPE_WIDE, str(stored_kinds()))
            check("so the field is no longer grey",
                  "color" not in (free.styleSheet() or ""),
                  repr(free.styleSheet()))
            check("and needs no reason beside it any more",
                  not kind_reason(free), repr(kind_reason(free)))
            print("\n%s" % ("ALL OK" if not error
                            else "FAIL: " + ", ".join(error)))
            app.quit(); return
    except Exception:
        import traceback; traceback.print_exc()
        error.append("crash"); app.quit(); return
    QtCore.QTimer.singleShot(1200, step)


QtCore.QTimer.singleShot(700, step)
QtCore.QTimer.singleShot(180000, app.quit)
def let_go_of(what):
    """Make every player let go of what it has open in there.

    Under Windows a folder cannot be deleted while a player holds a
    file in it, so every player under every window is asked, by what it
    has open rather than by which player it is. One that never started
    is not stopped: what lies behind stop() is built on first use, and
    that build waits for a lock another player holds while starting up.
    Returns the names that were let go.
    """
    what = os.path.realpath(what)
    let_go = []
    for top in app.topLevelWidgets():
        for x in top.findChildren(QtCore.QObject):
            if not (hasattr(x, "setSource") and hasattr(x, "source")):
                continue
            where = x.source()
            if not isinstance(where, QtCore.QUrl):
                continue
            where = where.toLocalFile()
            if not where:
                continue
            held = os.path.realpath(where)
            if held != what and not held.startswith(what + os.sep):
                continue
            state = getattr(x, "playbackState", None)
            state = state() if state is not None else None
            if state is not None and state != type(state).StoppedState:
                x.stop()
            x.setSource(QtCore.QUrl())
            let_go.append(os.path.basename(where))
    app.processEvents()
    return sorted(let_go)


def clean_up(what):
    """Close the window, then delete the folder, waiting for the grip.

    gui() comes back with the window still standing: let go, close,
    delete, in that order, and no ignore_errors, which would swallow a
    folder that stays because something still holds it. Letting go
    returns before the file is free -- the media backend closes the
    handle in a thread of its own -- so what is waited for is the
    handle and not a number of milliseconds. What is left after ten
    seconds is named as a finding, not a failure: a test red on one
    system on every run gets switched off rather than looked at.
    """
    print("  let go of %s" % (", ".join(let_go_of(what)) or "nothing"))
    for top in app.topLevelWidgets():
        top.close()
    app.processEvents()
    clock = QtCore.QElapsedTimer()
    clock.start()
    while True:
        left = []
        try:
            shutil.rmtree(what)
        except OSError:
            for here, _, files in os.walk(what):
                left += [os.path.join(here, f) for f in files]
            left = left or ([what] if os.path.exists(what) else [])
        if not left or clock.elapsed() > 10000:
            break
        app.processEvents()
        QtCore.QThread.msleep(50)
    if left:
        print("  the folder stayed: %d still held after %.1f s, first %s"
              % (len(left), clock.elapsed() / 1000.0, left[0]))
    else:
        print("  the folder went away with the window, after %.1f s"
              % (clock.elapsed() / 1000.0))


sys.argv = ["videopodcast-magic.py"]
vpm.gui()
clean_up(folder)
sys.exit(1 if error else 0)
