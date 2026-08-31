# -*- coding: utf-8 -*-
"""When a camera cut is offered, and what the box over it is called.

The cut reads who speaks out of one list of speakers, and it makes no
difference to that list whether the people were told apart by a
microphone each or by the separation. The gate used to be the
Multitrack tick alone, so one recording with several voices told apart
in it got an empty Resolve sheet and a line saying a cut cannot be
done. It stands one step wider now:

  * One person with a name and a camera is a cut too, as long as a
    second camera exists, and the box is then called "Cut with the
    wide shot". With one camera there is nothing to cut to and the box
    stays away: that is the edge, checked from both sides.
  * A separation that is stored but that nobody answered for shows no
    voices at all: only an answer in the name field brings them up.

Six windows are built for real, one per case, offscreen, each with a
project of its own opened in it:

  several recordings, the tick set     cut there   "Camera cut"
  one recording, the voices separated  cut there   "Camera cut"
  one recording, one voice, 2 cameras  cut there   "Cut with the wide shot"
  one recording, one voice, 1 camera   cut away    the sentence instead
  a separation nobody answered for     cut away    the sentence instead
  one recording, nothing separated     cut away    the sentence instead

Neither sheet is looked for by the class of widget it happens to be: a
test that names the class goes green having checked nothing the day
the class changes, because the empty window it then sees is what half
these cases already expect. Both are found by their column names.

VPM_CUT_GATE_DUMP=1 prints what the children said.
"""
import os, sys, json, subprocess, tempfile, time

# All six at once. The repeat below is for a lock inside Qt that runs
# used to walk into; it costs nothing where it never fires, and it is
# the only thing that would say if that came back. A child that has
# said nothing for this long has stopped, not slowed.
AT_ONCE = 6
PATIENCE = 100

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
sys.path.insert(0, HERE)

# One recording and two cameras out of the shared fixture. The second
# recording is added only where the case is about having two.
ONE_TRACK = "Moderator_REC00009.wav"
TWO_TRACK = "Kandidat_0008A_Timecode.wav"
CAMERAS = ("Moderatoren_08141855_C005.mov", "Kandidat_08141858_C009.mov")
# What the separation would have found. Cut down to the first entry
# where a case wants a single voice.
VOICES = (("V0", "Host"), ("V1", "Guest"))
SEGMENTS = [["V0", 1.0, 4.0], ["V0", 9.0, 11.5], ["V1", 5.0, 8.0]]

# Every case in one place, so that what is built and what is expected
# cannot drift apart: the child builds from this, the parent checks
# against it.
#
#   tracks    the audio recordings in the project
#   cameras   how many of CAMERAS go in
#   tick      the Multitrack tick
#   stored    how many voices the stored separation holds
#   answered  whether somebody answered "several speakers" for it
#   voices    how many voice rows must then stand in the sheet
#   cut       whether the cut box and its preview are on the screen
#   title     what the cut box is called where it is on the screen
PLAN = {
    "multitrack": dict(
        say="several recordings, the tick set",
        tracks=(ONE_TRACK, TWO_TRACK), cameras=2, tick=True,
        stored=0, answered=False, voices=0,
        cut=True, title='Camera cut'),
    "separated": dict(
        say="one recording, two voices separated",
        tracks=(ONE_TRACK,), cameras=2, tick=False,
        stored=2, answered=True, voices=2,
        cut=True, title='Camera cut'),
    "one_voice": dict(
        say="one recording, one voice, two cameras",
        tracks=(ONE_TRACK,), cameras=2, tick=False,
        stored=1, answered=True, voices=1,
        cut=True, title='Cut with the wide shot'),
    "one_camera": dict(
        say="one recording, one voice, one camera",
        tracks=(ONE_TRACK,), cameras=1, tick=False,
        stored=1, answered=True, voices=1,
        cut=False, title=None),
    "unanswered": dict(
        say="a separation nobody answered for",
        tracks=(ONE_TRACK,), cameras=2, tick=False,
        stored=2, answered=False, voices=0,
        cut=False, title=None),
    "plain": dict(
        say="one recording, nothing separated",
        tracks=(ONE_TRACK,), cameras=2, tick=False,
        stored=0, answered=False, voices=0,
        cut=False, title=None),
}
CASES = ("multitrack", "separated", "one_voice", "one_camera",
         "unanswered", "plain")

# The size the pictures for the manual are taken at. Fixed rather than
# taken from the desktop: a window at its smallest could hide a box.
WINDOW = (1400, 950)
DUMP = bool(os.environ.get("VPM_CUT_GATE_DUMP"))


def own_project(case, vpm):
    """A project of its own for one case, built out of the fixture.

    Opening a project moves the project file away and deletes copies
    lying elsewhere, which on the shared fixture would leave the next
    test with nothing to open, so the material is only linked to.
    Everything the six cases differ in stands in PLAN.
    """
    from fixture_root import fixture
    plan = PLAN[case]
    source = fixture("interview")
    cameras = list(CAMERAS[:plan["cameras"]])
    wanted = list(plan["tracks"]) + cameras
    own = tempfile.mkdtemp(prefix="vpm_cutgate_")
    here = {}
    for name in wanted:
        link = os.path.join(own, name)
        if not os.path.exists(link):
            os.symlink(os.path.join(source, name), link)
        here[name] = link
    assignment = {}
    d = {"format": vpm.FILE_FORMAT, "version": "test", "timeline": [],
         "call": [],
         "files": [{"path": here[n],
                    "kind": "video" if n.endswith(".mov") else "audio"}
                   for n in wanted],
         "out_folder": os.path.join(own, "Result"),
         "production": "Cut gate",
         "multitrack": bool(plan["tick"]),
         "assignment": assignment, "preset": ""}
    if plan["stored"]:
        # Stored the way the program stores it, with the fingerprint of
        # the file: a stored result whose source has changed is thrown
        # away, and this one must survive that test. The cameras are
        # given by hand, so no case hangs on a guess from a name.
        one = here[ONE_TRACK]
        st = os.stat(one)
        voices = list(VOICES[:plan["stored"]])
        labels = [k for k, _n in voices]
        d["speakers"] = {
            "source": os.path.abspath(one), "mtime": int(st.st_mtime),
            "size": st.st_size, "model": vpm.SPEAKER_MODEL_NAME,
            "model_mark": "", "num_speakers": len(voices),
            "names": dict(voices),
            "segments": [s for s in SEGMENTS if s[0] in labels]}
        for i, label in enumerate(labels):
            assignment["voice:" + label] = cameras[min(i, len(cameras) - 1)]
        if plan["answered"]:
            # The answer, and only the answer, brings the voices up.
            assignment["several:" + one] = True
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
    # the project file, and a run would fetch a model.
    os.environ["VPM_NO_SPEAKER_SPLIT"] = "1"
    import importlib.util
    from PySide6 import QtCore, QtWidgets
    app = QtWidgets.QApplication(sys.argv[:1])
    spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
    vpm = importlib.util.module_from_spec(spec)
    sys.modules["vpm"] = vpm
    spec.loader.exec_module(vpm)
    # Nothing here may reach the network or the keychain.
    vpm.list_presets = lambda key: []
    vpm.load_api_key = lambda: ""
    vpm.update_offer = lambda *a, **k: None
    vpm.set_language("en")

    plan = PLAN[case]
    project = own_project(case, vpm)
    QtWidgets.QFileDialog.getOpenFileName = staticmethod(
        lambda *a, **k: (project, ""))
    # Nothing may sit and wait for a click: a modal window would hold
    # the test until the suite kills it.
    QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
    QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok

    # Off the desktop, on the way in: the attribute has to be set
    # before the window is shown, and gui() shows it itself. The window
    # still goes through the whole layout machinery, which is what
    # makes isVisible worth reading at all.
    _show = QtWidgets.QWidget.show

    def offstage(self):
        self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
        _show(self)

    QtWidgets.QWidget.show = offstage
    QtWidgets.QDialog.show = offstage

    def drawn(text):
        """What ends up on the screen: & marks a key, && draws one &."""
        return str(text).replace("&&", "\x00").replace("&", "") \
                        .replace("\x00", "&")

    def window_of():
        for x in app.topLevelWidgets():
            if "Video Podcast Magic" in x.windowTitle():
                return x

    # ----------------------------------------------- reading the sheets
    def by_columns(window, *wanted):
        """The view whose columns are called these, whatever class it is.

        Not "the first QTableWidget with rows": a test that names the
        class stops finding the sheet the day the class changes, and
        finding nothing looks exactly like a project that has not
        opened yet -- a state half these cases expect, so it would
        pass without checking. Returns (view, model, column names).
        """
        for view in window.findChildren(QtWidgets.QAbstractItemView):
            # A header is a view too, over the very same model, and it
            # holds none of the fields.
            if isinstance(view, QtWidgets.QHeaderView):
                continue
            model = view.model()
            if model is None or not model.columnCount():
                continue
            titles = [drawn(model.headerData(c, QtCore.Qt.Horizontal) or "")
                      for c in range(model.columnCount())]
            if all(w in titles for w in wanted):
                return view, model, titles
        return None, None, []

    def in_cell(view, index):
        """What one cell says, whether it is text or a field.

        The rows carry fields and choosers, so the cell's own text is
        empty, and a chooser is asked for the value it stores, not the
        label it draws: the value is the camera.
        """
        widget = view.indexWidget(index)
        if isinstance(widget, QtWidgets.QComboBox):
            got = widget.currentData()
            return drawn(got if got is not None else widget.currentText())
        if isinstance(widget, QtWidgets.QLineEdit):
            return drawn(widget.text())
        return drawn(index.data() or "")

    def hint_in_cell(view, index):
        """The grey suggestion in an empty field, if it has one."""
        widget = view.indexWidget(index)
        if isinstance(widget, QtWidgets.QComboBox) and widget.lineEdit():
            return drawn(widget.lineEdit().placeholderText())
        if isinstance(widget, QtWidgets.QLineEdit):
            return drawn(widget.placeholderText())
        return ""

    def assignment_of(window):
        """The assignment sheet read off its model: rows, and rows under them.

        A recording is a top row, a voice a row hanging under it, and
        it is read off the model alone.
        """
        view, model, titles = by_columns(
            window, drawn(vpm.T('Audio recording')),
            drawn(vpm.T('Speaker name')), drawn(vpm.T('belongs to')))
        if view is None:
            return None
        out = {"head": titles, "kind": type(view).__name__, "rows": []}
        for r in range(model.rowCount()):
            top = model.index(r, 0)
            voices = []
            for k in range(model.rowCount(top)):
                voices.append({
                    "says": drawn(model.index(k, 0, top).data() or ""),
                    "name": in_cell(view, model.index(k, 1, top)),
                    "camera": in_cell(view, model.index(k, 2, top))})
            out["rows"].append({
                "says": drawn(top.data() or ""),
                "name": in_cell(view, model.index(r, 1)),
                "hint": hint_in_cell(view, model.index(r, 1)),
                "voices": voices})
        return out

    def cameras_of(window):
        """The camera sheet, found the same way and counted."""
        view, model, titles = by_columns(
            window, drawn(vpm.T('Camera')), drawn(vpm.T('new file name')))
        if view is None:
            return None
        return {"head": titles, "kind": type(view).__name__,
                "rows": [drawn(model.index(r, 0).data() or "")
                         for r in range(model.rowCount())]}

    # ------------------------------------------- the three on the sheet
    def marked_voices(window):
        """The voice fields, counted the second way: their own mark.

        The program marks a voice row's fields with objectName "voice";
        two counts that disagree mean one is looking at furniture.
        """
        return len([w for w in window.findChildren(QtWidgets.QLineEdit)
                    if w.objectName() == "voice"])

    def three(window):
        """The cut box, its preview, and the sentence in their place.

        The cut box is found by what is inside it and not by its
        heading: the heading is the very thing that changes, and the
        wide-shot tick lives in that box alone. The preview is the
        group whose heading carries the "-- preview" tail. The sentence
        is the widget above the cut box, its wording only a fallback.
        """
        edge = drawn(vpm.T('Wide shot for greeting at the start and '
                           'farewell at the end'))
        cut = None
        for b in window.findChildren(QtWidgets.QCheckBox):
            if drawn(b.text()) != edge:
                continue
            up = b.parentWidget()
            while up is not None and not isinstance(up, QtWidgets.QGroupBox):
                up = up.parentWidget()
            cut = up
            break
        tail = drawn(vpm.T('%s -- preview')).replace("%s", "").strip()
        fore = None
        for g in window.findChildren(QtWidgets.QGroupBox):
            if g is not cut and tail and tail in drawn(g.title()):
                fore = g
                break
        if cut is None or fore is None:
            return None, None, None
        note, column = None, cut.parentWidget()
        layout = None if column is None else column.layout()
        at = -1 if layout is None else layout.indexOf(cut)
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
        return cut, fore, note

    def reading(window):
        """Each of the three: on the screen now, and what it says."""
        cut, fore, note = three(window)
        if cut is None or fore is None or note is None:
            return None
        return {"cut": bool(cut.isVisible()),
                "forecast": bool(fore.isVisible()),
                "note": bool(note.isVisible()),
                "title": drawn(cut.title()),
                "ahead": drawn(fore.title()),
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

    resolve = drawn(vpm.T('Resolve cut')).split()[0]
    result = {"case": case}
    step = [0]
    waited = [0]

    def ready(window):
        """Everything this case's project brings must stand in the sheets.

        Not "some rows somewhere": the recordings, the voices and the
        cameras are known before the window opens, so they are waited
        for. Silence is the one answer a gate test must not accept.
        """
        got = assignment_of(window)
        cams = cameras_of(window)
        if got is None or cams is None:
            return False
        if len(got["rows"]) != len(plan["tracks"]):
            return False
        if sum(len(r["voices"]) for r in got["rows"]) != plan["voices"]:
            return False
        return len(cams["rows"]) == plan["cameras"]

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
            # Waiting for the sheets rather than for the clock: they
            # are built once the project has been read and every file
            # looked at, and a slow machine takes longer.
            if not ready(window) and waited[0] < 160:
                waited[0] += 1
                QtCore.QTimer.singleShot(250, go)
                return
            result["assignment"] = assignment_of(window)
            result["cameras"] = cameras_of(window)
            result["marked"] = marked_voices(window)
            box = tick(window)
            result["tick"] = None if box is None else bool(box.isChecked())
            result["sheet"] = sheet(window, resolve)
            result["first"] = reading(window)
            step[0] = 2
            QtCore.QTimer.singleShot(700, go)
            return
        # Read a second time, a moment later: a box just shown or
        # hidden stands the other way for one turn of the event loop.
        sheet(window, resolve)
        result["shown"] = reading(window)
        result["settled"] = result["shown"] == result.get("first")
        app.quit()

    QtCore.QTimer.singleShot(1200, go)
    # A window that never comes up must not hold the suite -- and must
    # not pass either: the report is empty then, and the parent says so.
    QtCore.QTimer.singleShot(240000, app.quit)

    # No watchdog in here. Where this stops it stops inside Qt, and Qt
    # holds the interpreter's lock while it waits, so no thread of this
    # process runs any more. Whoever watches this is the parent below.
    vpm.gui()
    print("CUTGATE " + json.dumps(result))


if os.environ.get("VPM_CUT_GATE_CASE"):
    look(os.environ["VPM_CUT_GATE_CASE"])
    raise SystemExit(0)


# -------------------------------------------------------------- the parent
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


from fixture_root import fixture

material = fixture("interview")
missing = [n for n in (ONE_TRACK, TWO_TRACK) + CAMERAS
           if not os.path.exists(os.path.join(material, n))]
if missing:
    print("SKIPPED: no material under %s -- missing %s"
          % (material, ", ".join(missing)))
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)

def build(case):
    """Start one child on one case."""
    env = dict(os.environ, VPM_CUT_GATE_CASE=case,
               QT_QPA_PLATFORM="offscreen", VPM_SILENT="1",
               VPM_NO_SPEAKER_SPLIT="1", VPM_NO_UPDATE_CHECK="1",
               LANG="C", LC_ALL="C", LANGUAGE="en")
    return subprocess.Popen(
        [sys.executable, os.path.abspath(__file__)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        env=env, cwd=HERE)


def listen(case, process):
    """Wait for one child and read its last word."""
    stopped = False
    try:
        out, _ = process.communicate(timeout=PATIENCE)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        out, stopped = "the window never came back", True
    said = [x for x in out.split("\n") if x.startswith("CUTGATE ")]
    # Its output is kept out of the way while it says nothing new, but
    # a child that never reported is shown whole, or its traceback
    # would go into the pipe and no further.
    if DUMP or not said:
        for x in out.split("\n"):
            if x and not x.startswith("CUTGATE "):
                print("  | %s" % x)
    if said:
        return json.loads(said[-1][8:])
    return {"error": "stopped inside Qt"} if stopped else {}


report = {}
for first in range(0, len(CASES), AT_ONCE):
    wave = [(c, build(c)) for c in CASES[first:first + AT_ONCE]]
    for case, process in wave:
        report[case] = listen(case, process)

# Where Qt stopped rather than the program being wrong, once more on a
# quiet machine -- and said out loud, because a repeat nobody sees is
# a green that was bought.
for case in CASES:
    if "stopped inside Qt" in str((report.get(case) or {}).get("error")):
        print("  | %s stopped inside Qt; once more, on its own" % case)
        report[case] = listen(case, build(case))

for case in CASES:
    d = report.get(case) or {}
    plan = PLAN[case]
    print("%s:" % plan["say"])
    got = d.get("assignment")
    cams = d.get("cameras")
    # Everything below hangs on there being a sheet at all, so a miss
    # here says so instead of quietly agreeing with a case that expects
    # nothing to be shown.
    check("  the assignment sheet answers for its columns", bool(got),
          "" if got else json.dumps(d.get("error") or d)[:160])
    if not got or not cams:
        check("  the camera sheet answers for its columns", bool(cams),
              json.dumps(d)[:160])
        continue
    check("  its columns are %s" % ", ".join(got["head"][:3]),
          got["head"][:3] == ["Audio recording", "Speaker name",
                              "belongs to"],
          "%s in a %s" % (json.dumps(got["head"]), got["kind"]))
    check("  it holds %d recording(s)" % len(plan["tracks"]),
          len(got["rows"]) == len(plan["tracks"]),
          json.dumps([r["says"] for r in got["rows"]]))
    check("  they are the recordings of the project",
          all(any(r["says"].startswith(os.path.splitext(t)[0])
                  for r in got["rows"]) for t in plan["tracks"]),
          json.dumps([r["says"] for r in got["rows"]]))
    check("  the camera sheet holds %d camera(s)" % plan["cameras"],
          len(cams["rows"]) == plan["cameras"],
          "%s in a %s" % (json.dumps(cams["rows"]), cams["kind"]))
    check("  the Multitrack tick is %s"
          % ("set" if plan["tick"] else "not set"),
          d.get("tick") is bool(plan["tick"]), str(d.get("tick")))

    voices = [v for r in got["rows"] for v in r["voices"]]
    check("  %d voice row(s) under the recording" % plan["voices"],
          len(voices) == plan["voices"],
          json.dumps([(v["name"], v["camera"]) for v in voices]))
    # The same number counted the other way. They can only disagree if
    # one of the two is looking at something that is not a voice row.
    check("  the marked voice fields agree",
          d.get("marked") == plan["voices"], str(d.get("marked")))
    if plan["voices"]:
        want = [(name, CAMERAS[min(i, plan["cameras"] - 1)])
                for i, (_k, name) in enumerate(VOICES[:plan["voices"]])]
        check("  each voice is named and on its camera",
              [(v["name"], v["camera"]) for v in voices] == want,
              json.dumps([(v["name"], v["camera"]) for v in voices]))
    # The recording's own name field is never filled in by the program:
    # what the file name suggests stands beside it in grey, and a
    # stored separation writes nothing into it either -- only an answer.
    check("  the recording's name field is empty",
          all(r["name"] == "" for r in got["rows"]),
          json.dumps([r["name"] for r in got["rows"]]))
    check("  the suggestion stands beside it in grey",
          all(r["hint"] for r in got["rows"]),
          json.dumps([r["hint"] for r in got["rows"]]))

    shown = d.get("shown")
    if not shown:
        check("  the cut box, its preview and the sentence were found",
              False, json.dumps(d)[:200])
        continue
    cut_on = bool(plan["cut"])
    check("  the camera cut box is %s" % ("there" if cut_on else "away"),
          shown["cut"] is cut_on, json.dumps(shown)[:200])
    check("  the preview box is %s" % ("there" if cut_on else "away"),
          shown["forecast"] is cut_on, json.dumps(shown)[:200])
    check("  the sentence is %s" % ("away" if cut_on else "there"),
          shown["note"] is (not cut_on), json.dumps(shown)[:200])
    if plan["title"]:
        check("  the box is called %r" % plan["title"],
              shown["title"] == plan["title"], repr(shown["title"]))
        # The two names are worked out in two places, so the preview
        # beside the box has to be held against it.
        check("  the preview says the same name",
              shown["ahead"].startswith(shown["title"] + " -- "),
              repr(shown["ahead"]))
    if not d.get("settled"):
        print("      read twice and not the same both times: %s"
              % json.dumps(d.get("first")))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
