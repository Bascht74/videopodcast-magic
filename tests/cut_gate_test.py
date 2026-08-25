# -*- coding: utf-8 -*-
"""What the camera cut hangs on: the material, not the Multitrack tick.

The cut reads who speaks when out of one list of speakers. It makes no
difference to that list whether the people were told apart by having a
microphone each or by the separation taking a single recording apart:
the voices found in one recording carry a camera of their own, and the
cut reads them along with the tracks.

The window used to ask a different question. The cut box, its preview
and the sentence standing in their place were switched by the
Multitrack tick alone, so whoever had one recording with four voices
told apart in it got an empty Resolve sheet and a line saying it
cannot be done.

Three windows are built for real, one per case, offscreen and kept off
the desktop, each with a project of its own opened in it. In every one
the same three widgets are asked whether they are on the screen:

  several recordings, the tick set     cut there, sentence away
  one recording, the voices separated  cut there, sentence away
  one recording, nothing separated     cut away, sentence there

The middle case is what this test was written for, and it is the one
that can be red. A red there says the camera cut still hangs on the
tick, not that this test is broken -- whoever finds it red has the
fault in front of them, not a broken test. The other two are the ends
it must not break on the way.

Measured on 25 August 2026 against two copies of the program: with the
box switched by the tick alone the middle case is red in all three of
its lines and the other two cases are green, and with the box switched
by whether two people have a name and a camera all three are green.
So the red the middle case can show is the fault and nothing else.

Nothing is measured here. The separation does not run: its result
travels in the project file the way it always does, and the material
is the shared interview fixture, linked to rather than copied.

VPM_CUT_GATE_DUMP=1 prints what the three children said.
"""
import os, sys, json, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
sys.path.insert(0, HERE)

CASES = ("multitrack", "separated", "plain")
NAMES = {"multitrack": "several recordings, the tick set",
         "separated": "one recording, the voices separated",
         "plain": "one recording, nothing separated"}
# What each case must show: (the camera cut, the sentence).
WANTED = {"multitrack": (True, False),
          "separated": (True, False),
          "plain": (False, True)}
# One recording and two cameras out of the shared fixture. The second
# recording is added only where the case is about having two.
ONE_TRACK = "Moderator_REC00009.wav"
TWO_TRACK = "Kandidat_0008A_Timecode.wav"
CAMERAS = ("Moderatoren_08141855_C005.mov", "Kandidat_08141858_C009.mov")
# The size the pictures for the manual are taken at. Fixed rather than
# taken from the desktop: there is no desktop offscreen, and a window
# left at its smallest could hide a box for the wrong reason.
WINDOW = (1400, 950)
DUMP = bool(os.environ.get("VPM_CUT_GATE_DUMP"))


def own_project(case, vpm):
    """A project of its own for one case, built out of the fixture.

    Opening a project moves the project file into its output folder
    and deletes copies lying elsewhere. On the shared fixture that
    would leave the next test with nothing to open, so the material is
    only linked to and the project file is written afresh -- the same
    way layout_test.py does it.

    The three cases differ in one thing each: "plain" and "separated"
    in whether a separation travels with the project, "plain" and
    "multitrack" in the second recording and the tick.
    """
    from fixture_root import fixture
    source = fixture("interview")
    wanted = [ONE_TRACK] + list(CAMERAS)
    if case == "multitrack":
        wanted.insert(1, TWO_TRACK)
    own = tempfile.mkdtemp(prefix="vpm_cutgate_")
    here = {}
    for name in wanted:
        link = os.path.join(own, name)
        if not os.path.exists(link):
            os.symlink(os.path.join(source, name), link)
        here[name] = link
    d = {"format": vpm.FILE_FORMAT, "version": "test", "timeline": [],
         "call": [],
         "files": [{"path": here[n],
                    "kind": "video" if n.endswith(".mov") else "audio"}
                   for n in wanted],
         "out_folder": os.path.join(own, "Result"),
         "production": "Cut gate",
         "multitrack": case == "multitrack",
         "assignment": {}, "preset": ""}
    if case == "separated":
        # What the separation would have found, stored the way the
        # program stores it: raw, in the time of the recording, with
        # the fingerprint of the file it was heard in -- a stored
        # result whose source has changed is thrown away, and this one
        # must survive that test. The cameras are given by hand: the
        # preselection guesses from the name, and a guess would make
        # the case depend on how well two names happen to match.
        one = here[ONE_TRACK]
        st = os.stat(one)
        d["speakers"] = {
            "source": os.path.abspath(one), "mtime": int(st.st_mtime),
            "size": st.st_size, "model": vpm.SPEAKER_MODEL_NAME,
            "model_mark": "", "num_speakers": 2,
            "names": {"V0": "Host", "V1": "Guest"},
            "segments": [["V0", 1.0, 4.0], ["V0", 9.0, 11.5],
                         ["V1", 5.0, 8.0]]}
        d["assignment"] = {"voice:V0": CAMERAS[0],
                           "voice:V1": CAMERAS[1]}
    os.makedirs(d["out_folder"], exist_ok=True)
    path = os.path.join(own, "videopodcast-magic_Cut_gate.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1)
    return path


# --------------------------------------------------------------- the child
# One process per case. A second gui() in one process would be a second
# interface standing on the first, and the state of the first one with it.
def look(case):
    """Build the window for one case and say what its Resolve sheet shows."""
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ["VPM_SILENT"] = "1"
    os.environ["VPM_NO_UPDATE_CHECK"] = "1"
    # The separation never starts here: what it would have found is in
    # the project file already, and a run would fetch a model.
    os.environ["VPM_NO_SPEAKER_SPLIT"] = "1"
    import importlib.util
    from PySide6 import QtCore, QtWidgets
    app = QtWidgets.QApplication(sys.argv[:1])
    spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
    vpm = importlib.util.module_from_spec(spec)
    sys.modules["vpm"] = vpm
    spec.loader.exec_module(vpm)
    # Nothing here may reach the network or the keychain: what is
    # wanted is the window, not a run.
    vpm.list_presets = lambda key: []
    vpm.load_api_key = lambda: ""
    vpm.update_offer = lambda *a, **k: None
    vpm.set_language("en")

    project = own_project(case, vpm)
    QtWidgets.QFileDialog.getOpenFileName = staticmethod(
        lambda *a, **k: (project, ""))
    # Nothing may sit and wait for a click: a modal window would hold
    # the test until the suite kills it.
    QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
    QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok

    # Off the desktop, on the way in: the attribute has to be set
    # before the window is shown, and gui() shows it itself. Somebody
    # is sitting at this machine while the suite runs. The window still
    # goes through the whole layout machinery, which is what makes
    # isVisible worth reading at all.
    _show = QtWidgets.QWidget.show

    def offstage(self):
        self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
        _show(self)

    QtWidgets.QWidget.show = offstage
    QtWidgets.QDialog.show = offstage

    def drawn(text):
        """What ends up on the screen: & marks a key, && draws one &."""
        return text.replace("&&", "\x00").replace("&", "") \
                   .replace("\x00", "&")

    def window_of():
        for x in app.topLevelWidgets():
            if x.windowTitle().startswith("Video Podcast"):
                return x

    def three(window):
        """The cut box, its preview, and the sentence in their place.

        The two boxes are found by their heading, the way a person
        finds them on the sheet. The preview grows a length in its
        heading as soon as there are numbers, so only the front of it
        is compared.

        The sentence is found by where it stands and not by what it
        says: it is the widget directly above the cut box in the same
        column. Its wording is going to be rewritten, and a test that
        looked for the words would go green by losing sight of it. The
        wording is the fallback, not the way in.
        """
        head = drawn(vpm.T('Camera cut'))
        ahead = drawn(vpm.T('Camera cut -- preview'))
        boxes = window.findChildren(QtWidgets.QGroupBox)
        cut = [g for g in boxes if drawn(g.title()) == head]
        fore = [g for g in boxes if drawn(g.title()).startswith(ahead)]
        if not cut or not fore:
            return None, None, None
        note, column = None, cut[0].parentWidget()
        layout = None if column is None else column.layout()
        at = -1 if layout is None else layout.indexOf(cut[0])
        item = layout.itemAt(at - 1) if at > 0 else None
        if item is not None and isinstance(item.widget(),
                                           QtWidgets.QLabel):
            note = item.widget()
        if note is None:
            start = drawn(vpm.T('There is no camera cut yet'))[:24]
            for x in window.findChildren(QtWidgets.QLabel):
                if drawn(x.text()).startswith(start):
                    note = x
                    break
        return cut[0], fore[0], note

    def reading(window):
        """Is each of the three on the screen right now?"""
        cut, fore, note = three(window)
        if cut is None or fore is None or note is None:
            return None
        return {"cut": bool(cut.isVisible()),
                "forecast": bool(fore.isVisible()),
                "note": bool(note.isVisible()),
                "says": drawn(note.text()).split("\n")[0][:40]}

    def sheet(window, word):
        """Bring one sheet to the front: only what lies on top is seen."""
        for bar in window.findChildren(QtWidgets.QTabWidget):
            for k in range(bar.count()):
                if word.lower() in drawn(bar.tabText(k)).lower():
                    bar.setCurrentIndex(k)
                    app.processEvents()
                    return True
        return False

    def tick(window):
        """The Multitrack checkbox, so the case can say what it is."""
        head = drawn(vpm.T('Multitrack (one track per speaker)'))
        for b in window.findChildren(QtWidgets.QCheckBox):
            if drawn(b.text()) == head:
                return b
        return None

    def voice_rows(window):
        """How many voice rows there are, whatever holds them.

        This used to look for a second table headed "Voice". On
        25.8.2026 the two tables became one, the voices moved under
        their recording, and the heading went with them -- so the old
        way found nothing and read it as "no voices". Furniture again.
        A voice row is now what its own fields say it is: the program
        marks them with objectName "voice".
        """
        seen = set()
        for w in window.findChildren(QtWidgets.QWidget):
            if w.objectName() != "voice":
                continue
            name = w.accessibleName() or ""
            seen.add(name.split(" -- ", 1)[-1] if " -- " in name else id(w))
        return seen

    resolve = drawn(vpm.T('Resolve cut')).split()[0]
    result = {"case": case}
    step = [0]
    waited = [0]

    def go():
        window = window_of()
        if window is None:
            result["error"] = "no window came up"
            app.quit()
            return
        if step[0] == 0:
            window.resize(*WINDOW)
            app.processEvents()
            step[0] = 1
            for b in window.findChildren(QtWidgets.QPushButton):
                if drawn(b.text()).strip().startswith(
                        vpm.T('Open project ...')[:8]):
                    b.click()
                    break
            QtCore.QTimer.singleShot(400, go)
            return
        if step[0] == 1:
            # Waiting for the tables rather than for the clock: they
            # are built once the project has been read and every file
            # looked at. A slow machine takes longer, and an interface
            # that never gets there gives up rather than hangs.
            rows = any(t.rowCount() for t in
                       window.findChildren(QtWidgets.QTableWidget))
            heard = voice_rows(window)
            if not (rows and (case != "separated" or heard)) \
                    and waited[0] < 160:
                waited[0] += 1
                QtCore.QTimer.singleShot(250, go)
                return
            result["filled"] = bool(rows)
            result["voices"] = len(heard)
            box = tick(window)
            result["tick"] = None if box is None else bool(box.isChecked())
            result["sheet"] = sheet(window, resolve)
            result["first"] = reading(window)
            step[0] = 2
            QtCore.QTimer.singleShot(700, go)
            return
        # Read a second time, a moment later. A box that has just been
        # shown or hidden stands the other way for one turn of the
        # event loop, and a test that is red every third run gets
        # switched off rather than looked at.
        sheet(window, resolve)
        result["shown"] = reading(window)
        result["settled"] = result["shown"] == result.get("first")
        app.quit()

    QtCore.QTimer.singleShot(1200, go)
    # A window that never comes up must not hold the suite -- and must
    # not pass either: the report is empty then, and the parent says so.
    QtCore.QTimer.singleShot(240000, app.quit)
    vpm.gui()
    print("CUTGATE " + json.dumps(result))


if os.environ.get("VPM_CUT_GATE_CASE"):
    look(os.environ["VPM_CUT_GATE_CASE"])
    raise SystemExit(0)


# -------------------------------------------------------------- the parent
error = []


def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


from fixture_root import fixture

material = fixture("interview")
missing = [n for n in (ONE_TRACK, TWO_TRACK) + CAMERAS
           if not os.path.exists(os.path.join(material, n))]
if missing:
    print("SKIPPED: no material under %s -- missing %s"
          % (material, ", ".join(missing)))
    raise SystemExit(0)

started = []
for case in CASES:
    env = dict(os.environ, VPM_CUT_GATE_CASE=case,
               QT_QPA_PLATFORM="offscreen", VPM_SILENT="1",
               VPM_NO_SPEAKER_SPLIT="1", VPM_NO_UPDATE_CHECK="1",
               LANG="C", LC_ALL="C", LANGUAGE="en")
    started.append((case, subprocess.Popen(
        [sys.executable, os.path.abspath(__file__)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        env=env, cwd=HERE)))

report = {}
for case, process in started:
    try:
        out, _ = process.communicate(timeout=900)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        out = "the window never came back"
    said = [x for x in out.split("\n") if x.startswith("CUTGATE ")]
    report[case] = json.loads(said[-1][8:]) if said else {}
    # The child does the building, so the child does the talking. Its
    # output is kept out of the way while it says nothing new -- but a
    # child that never reported is shown whole, or its traceback would
    # go into the pipe and no further.
    if DUMP or not said:
        for x in out.split("\n"):
            if x and not x.startswith("CUTGATE "):
                print("  | %s" % x)

for case in CASES:
    d = report.get(case) or {}
    name = NAMES[case]
    print("%s:" % name)
    check("  the project is open", bool(d.get("filled")),
          json.dumps(d.get("error") or ""))
    check("  the Multitrack tick is %s"
          % ("set" if case == "multitrack" else "not set"),
          d.get("tick") is (case == "multitrack"), str(d.get("tick")))
    if case == "separated":
        check("  two voices came out of the project file",
              d.get("voices") == 2, str(d.get("voices")))
    shown = d.get("shown")
    if not shown:
        check("  the cut box, its preview and the sentence were found",
              False, json.dumps(d)[:160])
        continue
    cut_on, note_on = WANTED[case]
    check("  the camera cut box is %s" % ("there" if cut_on else "away"),
          shown["cut"] is cut_on, json.dumps(shown))
    check("  the preview box is %s" % ("there" if cut_on else "away"),
          shown["forecast"] is cut_on, json.dumps(shown))
    check("  the sentence is %s" % ("there" if note_on else "away"),
          shown["note"] is note_on, json.dumps(shown))
    if not d.get("settled"):
        print("      read twice and not the same both times: %s"
              % json.dumps(d.get("first")))

print()
if error:
    print("FAIL: " + ", ".join(error))
    sys.exit(1)
print("All good.")
