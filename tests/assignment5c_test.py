# -*- coding: utf-8 -*-
"""#38 Stage 5c: what decides that a camera's sound is material.

Two things the version before this one wrote down have gone. It demanded
that no audio recording and three cameras give camera audio by itself --
the rule Sebastian retired on 25.8.2026, whose replacement is "no tick,
no audio" -- and its last section opened this file and searched the
source for the literal text "suggestion = camera_output_name(". The
second is the worse of the two: reformatting a call turned it red while
the program did exactly what it did before, and a test that answers a
question about layout when it was asked about behaviour teaches people
to stop reading it.

So the rows are asked of the function that builds them, and the interface
is asked of a real window instead of of the file it is written in. The
audio decision is found by what can be picked in it -- the two answers
the program knows -- and by the file its accessible name mentions, never
by a column number, a heading or a row count. It stands in two places at
once, on the file sheet and beside the player, and the checks below walk
it from one to the other and back.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, json, shutil, subprocess, sys, tempfile

PRODUCTION = "Two cameras"
CAMERAS = ("Wide_C003.mov", "Guest_C009.mov")


def load():
    """The program, freshly imported into this process."""
    spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["vpm"] = module
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------- the child
def look(media):
    """One window, two cameras, no recording: what the field does."""
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ.setdefault("VPM_SILENT", "1")
    os.environ.setdefault("VPM_NO_UPDATE_CHECK", "1")
    os.environ.setdefault("VPM_NO_SPEAKER_SPLIT", "1")
    from PySide6 import QtCore, QtWidgets

    app = QtWidgets.QApplication(sys.argv[:1])
    vpm = load()
    # Every caption below is asked for through the catalogue, so the
    # language does not decide the outcome -- but it is settled all the
    # same, or a standalone run on a German machine would compare
    # English keys with a German window.
    vpm.set_language("en")
    # Nothing may reach the network or the keychain: what is wanted is
    # the window, not a run.
    vpm.list_presets = lambda key: []
    vpm.load_api_key = lambda: ""
    vpm.update_offer = lambda *a, **k: None
    vpm.speaker_split_setup = lambda *a, **k: "not in a test"
    vpm.speaker_split_run = lambda *a, **k: ([], "not in a test")

    error = []

    def check(name, ok, extra=""):
        print("  %-56s %s %s" % (name, "ok" if ok else "FAIL", extra))
        if not ok:
            error.append(name)

    videos = [os.path.join(media, n) for n in CAMERAS]
    folder = tempfile.mkdtemp(prefix="vpm_a5c_")
    project = os.path.join(folder, "videopodcast-magic_Cameras.json")
    d = {"format": vpm.FILE_FORMAT, "version": "test", "timeline": [],
         "call": [], "assignment": {}, "preset": "",
         "files": [{"path": p, "kind": "video"} for p in videos],
         "out_folder": os.path.join(folder, "Result"),
         "production": PRODUCTION, "multitrack": False,
         # A no that was given once and is stored, so nothing separates
         # anything by itself.
         "speakers_local": False}
    with open(project, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.makedirs(d["out_folder"], exist_ok=True)

    #------------------------------------ the field on its own, no window
    # Cheap and exact, and it says what the window afterwards can only
    # show in the large: one value, two fields, and a settled field that
    # is inert.
    print("\n5. The audio decision as a field")
    quiet = vpm.COLOURS["quiet"]
    value = vpm.Value(False)
    _cell, box = vpm.camera_audio_cell("Wide_C003.mov", False, "", quiet)
    vpm.audio_use_bind(box, value)
    picks = [box.itemData(i) for i in range(box.count())]
    check("the field offers two answers and no more",
          picks == [vpm.AUDIO_UNUSED, vpm.AUDIO_MATERIAL], str(picks))
    check("and stands on 'do not use the audio'",
          box.currentData() == vpm.AUDIO_UNUSED, str(box.currentData()))
    box.setCurrentIndex(box.findData(vpm.AUDIO_MATERIAL))
    check("choosing writes the decision down", value.get() is True)
    _cell2, box2 = vpm.camera_audio_cell("Wide_C003.mov", value.get(), "",
                                         quiet, True)
    vpm.audio_use_bind(box2, value)
    check("a second field on the same value opens on it",
          box2.currentData() == vpm.AUDIO_MATERIAL)
    box2.setCurrentIndex(box2.findData(vpm.AUDIO_UNUSED))
    check("and changing either one moves the other",
          box.currentData() == vpm.AUDIO_UNUSED and value.get() is False,
          str(box.currentData()))
    # The exception: one video with sound and no recording beside it.
    # The reason comes out of the program, not out of a string here.
    used, why = vpm.audio_use_settled("Only.mov", ["Only.mov"],
                                      ["Only.mov"])
    settled = vpm.Value(False)
    cell3, box3 = vpm.camera_audio_cell("Only.mov", used, why, quiet)
    vpm.audio_use_bind(box3, settled, why)
    check("the settled field shows the audio in use",
          box3.currentData() == vpm.AUDIO_MATERIAL)
    check("and cannot be changed", not box3.isEnabled())
    check("and the reason stands beside it, not in a tooltip",
          any(w.text() == why
              for w in cell3.findChildren(QtWidgets.QLabel)), why)
    box3.setCurrentIndex(box3.findData(vpm.AUDIO_UNUSED))
    check("and showing it stores nothing", settled.get() is False)

    #-------------------------------------------------------- the window
    QtWidgets.QFileDialog.getOpenFileName = staticmethod(
        lambda *a, **k: (project, ""))
    # Nothing may sit and wait for a click: a modal window would hold
    # the test until somebody kills it.
    QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
    QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
    # Off the desktop on the way in. The offscreen platform keeps the
    # window out of the window server; this keeps it off the screen on
    # any platform, and the layout machinery still runs.
    _show = QtWidgets.QWidget.show

    def offstage(self):
        self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
        _show(self)

    QtWidgets.QWidget.show = offstage
    QtWidgets.QDialog.show = offstage

    def win():
        for x in app.topLevelWidgets():
            if x.windowTitle().startswith("Video Podcast"):
                return x

    def sheet_of(word):
        """The sheet whose tab carries that word."""
        for tw in win().findChildren(QtWidgets.QTabWidget):
            for k in range(tw.count()):
                if word.lower() in tw.tabText(k).lower():
                    return tw.widget(k)
        return None

    def rows_named(sheet):
        """Every row on that sheet, by the name its fields are given.

        A field in a table cell is read out as its kind and nothing
        else -- "combo box", "edit field" -- so the program says the
        column and the row in the accessible name, "Camera audio --
        Wide_C003.mov". The part behind the first dash is the row.
        """
        rows = {}
        if sheet is None:
            return rows
        for w in sheet.findChildren(QtWidgets.QWidget):
            said = w.accessibleName()
            if " -- " not in said:
                continue
            rows.setdefault(said.split(" -- ", 1)[1].strip(),
                            []).append(w)
        return rows

    def chooser(widgets, wanted):
        """The chooser offering exactly those answers, or None."""
        for w in widgets:
            if not isinstance(w, QtWidgets.QComboBox):
                continue
            picks = [w.itemData(i) for i in range(w.count())]
            if all(x in picks for x in wanted):
                return w
        return None

    def audio_box(sheet, short):
        """The audio decision of that file on that sheet.

        Recognised by what can be picked in it -- the two answers the
        program knows -- and not by which column it stands in.
        """
        for said, widgets in rows_named(sheet).items():
            if not said.startswith(short):
                continue
            box = chooser(widgets, vpm.AUDIO_USE)
            if box is not None:
                return box
        return None

    def track_rows(sheet):
        """The rows of the recordings table, by the name they carry.

        A row that puts somebody on a camera is an input track. Which
        field says so is read off what can be picked in it: a camera,
        and the two answers that are not a camera.
        """
        out = {}
        for said, widgets in rows_named(sheet).items():
            box = chooser(widgets, (vpm.MIX_ONLY, vpm.IGNORE_AUDIO))
            if box is not None:
                out[said] = box
        return out

    def written(sheet, short):
        """What stands in the new-file-name field of that video row."""
        for said, widgets in rows_named(sheet).items():
            if not said.startswith(short):
                continue
            for w in widgets:
                if isinstance(w, QtWidgets.QLineEdit):
                    return w.text()
        return None

    def start_button():
        for w in win().findChildren(QtWidgets.QPushButton):
            if w.text().strip() == vpm.T('Start'):
                return w

    def start_reason():
        said = vpm.T('Why the run cannot start')
        for w in win().findChildren(QtWidgets.QLabel):
            if w.accessibleName() == said:
                return w.text()
        return None

    files_word = vpm.T('Files && production')[:8]
    assign_word = vpm.T('Assignment && time window')[:8]
    shorts = [os.path.basename(p) for p in videos]
    # What the reason has to name if it is to be of any use: the answer
    # that would fix it. Asked of the catalogue, so a reworded label
    # moves both sides at once.
    fixes_it = vpm.label_of(vpm.AUDIO_MATERIAL)
    n = [0]
    waited = [0]
    done = [False]

    def step():
        i = n[0]
        n[0] += 1
        try:
            if i == 0:
                win().show()
                win().resize(1400, 900)
                app.processEvents()
                for w in win().findChildren(QtWidgets.QPushButton):
                    if w.text().strip().startswith(
                            vpm.T('Open project ...')[:8]):
                        w.click()
            elif i == 1:
                # Waiting for the fields rather than for a number of
                # seconds: the list is built out of a thread and a fixed
                # pause would be wrong on both sides.
                sheet = sheet_of(files_word)
                there = all(audio_box(sheet, s) is not None
                            for s in shorts)
                if not there and waited[0] < 120:
                    waited[0] += 1
                    n[0] = 1
                    QtCore.QTimer.singleShot(250, step)
                    return
                check("the project brought both cameras into the list",
                      there)
                if not there:
                    app.quit()
                    return
                nothing_look(sheet)
                QtCore.QTimer.singleShot(400, step)
                return
            elif i == 2:
                box_now = audio_box(sheet_of(files_word), shorts[0])
                box_now.setCurrentIndex(
                    box_now.findData(vpm.AUDIO_MATERIAL))
                app.processEvents()
                waited[0] = 0
                QtCore.QTimer.singleShot(400, step)
                return
            elif i == 3:
                sheet = sheet_of(assign_word)
                there = audio_box(sheet, shorts[0]) is not None
                if not there and waited[0] < 120:
                    waited[0] += 1
                    n[0] = 3
                    QtCore.QTimer.singleShot(250, step)
                    return
                chosen_look(sheet, there)
                QtCore.QTimer.singleShot(400, step)
                return
            elif i == 4:
                box_now = audio_box(sheet_of(assign_word), shorts[0])
                if box_now is None:
                    check("the field is still there to take back", False)
                else:
                    box_now.setCurrentIndex(
                        box_now.findData(vpm.AUDIO_UNUSED))
                app.processEvents()
                QtCore.QTimer.singleShot(600, step)
                return
            elif i == 5:
                taken_back_look()
                print("\n%s" % ("ALL OK" if not error
                                else "FAIL: " + ", ".join(error)))
                done[0] = True
                app.quit()
                return
        except Exception:
            import traceback
            traceback.print_exc()
            error.append("crash")
            done[0] = True
            app.quit()
            return
        QtCore.QTimer.singleShot(400, step)

    def nothing_look(sheet):
        """Nothing chosen: no sound, and the run cannot start."""
        boxes = [audio_box(sheet, s) for s in shorts]
        check("every video file carries the decision itself",
              all(b is not None for b in boxes))
        check("and every one of them starts on 'do not use'",
              all(b.currentData() == vpm.AUDIO_UNUSED for b in boxes),
              str([b.currentData() for b in boxes]))
        check("two cameras leave a real choice, not a settled field",
              all(b.isEnabled() for b in boxes))
        check("so no track stands in the recordings table",
              not track_rows(sheet_of(assign_word)),
              str(list(track_rows(sheet_of(assign_word)))))
        check("and the run cannot start",
              start_button() is not None
              and not start_button().isEnabled())
        said = start_reason() or ""
        check("with the reason under the button, saying what to do",
              fixes_it in said, repr(said[:90]))

    def chosen_look(sheet, there):
        """One camera chosen on the file sheet: what tab 2 shows."""
        check("the choice reaches the sheet beside the player", there)
        if not there:
            return
        box_here = audio_box(sheet, shorts[0])
        check("and the field there shows the same answer",
              box_here.currentData() == vpm.AUDIO_MATERIAL,
              str(box_here.currentData()))
        other = audio_box(sheet, shorts[1])
        check("while the camera nobody chose stays on 'do not use'",
              other is not None
              and other.currentData() == vpm.AUDIO_UNUSED)
        rows = track_rows(sheet)
        mine = [said for said in rows if said.startswith(shorts[0])]
        check("the camera has become a row in the recordings table",
              len(mine) == 1, str(list(rows)))
        if mine:
            check("and that row starts on the camera it came out of",
                  rows[mine[0]].currentData() == shorts[0],
                  str(rows[mine[0]].currentData()))
        check("nothing else moved into the table",
              len(rows) == len(mine), str(list(rows)))
        # The name the run would write. Asked of the same function the
        # program uses, so a changed rule changes both sides -- and a
        # reformatted call changes neither.
        check("the untouched camera is named as the full mix",
              written(sheet, shorts[1])
              == vpm.camera_output_name(PRODUCTION, shorts[1],
                                        ["Audio-Full-Mix"]),
              str(written(sheet, shorts[1])))
        check("and now there is sound, so the run can start",
              start_button().isEnabled(), repr((start_reason() or "")[:90]))

    def taken_back_look():
        """Taken back beside the player: the file sheet follows."""
        box_here = audio_box(sheet_of(files_word), shorts[0])
        check("taking it back on one sheet shows on the other",
              box_here is not None
              and box_here.currentData() == vpm.AUDIO_UNUSED,
              str(None if box_here is None else box_here.currentData()))
        sheet = sheet_of(assign_word)
        check("and the track is out of the recordings table again",
              not track_rows(sheet), str(list(track_rows(sheet))))
        check("with a line in its place saying what would fill it",
              any(fixes_it in w.text()
                  for w in sheet.findChildren(QtWidgets.QLabel)))
        # These two were found by being missing. Measured on 25.8.2026:
        # taking the last sound away left the Start button live and the
        # reason line empty, while a window that *opened* without sound
        # refused correctly -- the button had simply never been enabled
        # there. assignment_fresh() left early when there was nothing to
        # show, and assignment_check(), which ends in buttons_check(),
        # sits at the far end of it. The way in matters, so both ways
        # are asked.
        check("no sound left, so the run cannot start again",
              not start_button().isEnabled())
        check("and the reason is under the button once more",
              fixes_it in (start_reason() or ""))

    QtCore.QTimer.singleShot(300, step)
    # A window that never gets there must not hold the suite -- there is
    # no timeout(1) on this machine -- and must not pass either.
    QtCore.QTimer.singleShot(150000, app.quit)
    vpm.gui()
    if not done[0]:
        print("  the window never got as far as the checks   FAIL")
        error.append("no answer")
    shutil.rmtree(folder, ignore_errors=True)
    return 1 if error else 0


if os.environ.get("VPM_A5C_MEDIA"):
    raise SystemExit(look(os.environ["VPM_A5C_MEDIA"]))


# -------------------------------------------------------- the parent
vpm = load()

error = []


def check(name, ok, extra=""):
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)


D = tempfile.mkdtemp(prefix="assignment5c_")


def file(n):
    p = os.path.join(D, n)
    open(p, "wb").write(b"\0" * 16)
    return p


print("1. Which rows the upper table gets")
t1, t2 = file("Guest_REC001.wav"), file("Co-host_REC002.wav")
b1, b2, b3 = (file("Wide_C003.mov"), file("Guest_C009.mov"),
              file("Host_C005.mov"))
rows, cam_audio, own = vpm.assignment_rows([t1, t2], [b1, b2, b3])
check("two audio recordings -> two rows", len(rows) == 2, str(len(rows)))
check("no camera contributes unasked", own == {})

rows, cam_audio, own = vpm.assignment_rows([t1, t2], [b1, b2, b3],
                                           own_flag_cameras=[b1])
check("with one camera chosen -> three rows", len(rows) == 3,
        str(len(rows)))
check("it sits at the back", rows[-1][0] == [b1])
check("and is noted as coming out of that camera",
        own == {os.path.abspath(b1): os.path.abspath(b1)})

# Until 25.8.2026 this case gave one row per camera by itself. Sebastian
# retired it: nothing can tell a radio microphone in the video track from
# a room microphone, so the program stopped guessing.
rows, cam_audio, own = vpm.assignment_rows([], [b1, b2, b3])
check("no recording and nothing chosen -> no rows at all",
        rows == [] and own == {}, str(rows))
check("and the old automatic stays off", cam_audio is False)

rows, cam_audio, own = vpm.assignment_rows([], [b1], own_flag_cameras=[b1])
check("one camera chosen -> one row", len(rows) == 1 and own)
rows, cam_audio, own = vpm.assignment_rows([], [])
check("nothing at all -> nothing at all", rows == [] and cam_audio is False)

print("\n2. Which camera a track is preselected to")
TARGETS = ["Wide_C003.mov", "Guest_C009.mov", "Host_C005.mov",
           vpm.MIX_ONLY, vpm.IGNORE_AUDIO]
VIDEOS = [b1, b2, b3]
check("set by hand still applies",
        vpm.preselected_camera("Host_C005.mov", TARGETS, "Guest", VIDEOS)
        == "Host_C005.mov")
check("ignore stays as well",
        vpm.preselected_camera(vpm.IGNORE_AUDIO, TARGETS, "Guest", VIDEOS)
        == vpm.IGNORE_AUDIO)
check("camera gone -> guessed anew",
        vpm.preselected_camera("Gone_C099.mov", TARGETS, "Guest", VIDEOS)
        == "Guest_C009.mov")
check("without an old choice, by the name",
        vpm.preselected_camera(None, TARGETS, "Guest", VIDEOS)
        == "Guest_C009.mov")
# No camera carries this speaker's name, not even a similar one.
check("no match -> mix only",
        vpm.preselected_camera(None, TARGETS, "Visitor", VIDEOS)
        == vpm.MIX_ONLY)
check("empty name -> mix only",
        vpm.preselected_camera(None, TARGETS, "", VIDEOS) == vpm.MIX_ONLY)
# The camera the audio came out of is where a row starts, but only until
# somebody says otherwise: a clip-on microphone in one camera may belong
# to a person another camera is filming.
check("own camera is the preselection",
        vpm.preselected_camera(None, TARGETS, "Guest", VIDEOS,
                           own_camera="Wide_C003.mov")
        == "Wide_C003.mov")
check("but a setting made by hand beats it",
        vpm.preselected_camera("Host_C005.mov", TARGETS, "Guest", VIDEOS,
                           own_camera="Wide_C003.mov")
        == "Host_C005.mov")

print("\n3. What the new video file is called")
f = vpm.camera_output_name
check("speakers into the middle",
        f("Interview 1", "Hosts_08141714_C002.mov", ["Host", "Co-host"])
        == "Interview 1_Hosts_Host+Co-host_08141714_C002",
        f("Interview 1", "Hosts_08141714_C002.mov", ["Host", "Co-host"]))
check("camera already named like the speaker -> not twice",
        f("Interview 2", "Guest_08141858_C009.mov", ["Guest"])
        == "Interview 2_Guest_08141858_C009",
        f("Interview 2", "Guest_08141858_C009.mov", ["Guest"]))
# The typo is "Gueest", not "Guset": a swapped pair only scores 0.80 and
# stays under the 0.85 mark, so the check would test nothing.
check("not twice with a typo either",
        "Gueest_Guest" not in f("I", "Gueest_C009.mov", ["Guest"]),
        f("I", "Gueest_C009.mov", ["Guest"]))
check("without speakers the full mix",
        f("Interview 2", "Wide_08141855_C003.mov", ["Audio-Full-Mix"])
        == "Interview 2_Wide_Audio-Full-Mix_08141855_C003",
        f("Interview 2", "Wide_08141855_C003.mov", ["Audio-Full-Mix"]))
check("camera name without a separator -> appended at the back",
        f("I", "C009.mov", ["Guest"]) == "I_C009_Guest",
        f("I", "C009.mov", ["Guest"]))
check("empty production becomes 'Production'",
        f("", "Camera_C001.mov", []).startswith("Production_"),
        f("", "Camera_C001.mov", []))
check("only spaces counts as empty",
        f("   ", "Camera_C001.mov", []).startswith("Production_"))
check("empty speaker names drop out",
        f("I", "Camera_C001.mov", ["", "  ", "Anna"])
        == "I_Camera_Anna_C001",
        f("I", "Camera_C001.mov", ["", " ", "Anna"]))
check("a whole path works too",
        f("I", "/deep/in/folder/Camera_C001.mov", ["Anna"])
        == "I_Camera_Anna_C001")
check("dots in the camera name separate too",
        f("I", "Camera.C001.mov", ["Anna"]) == "I_Camera_Anna_C001",
        f("I", "Camera.C001.mov", ["Anna"]))
check("no crash without a speaker list",
        isinstance(f("I", "Camera_C001.mov"), str))

print("\n4. What comes out in the same order as before")
# The three cameras of a real two-part interview, in the shape they
# were delivered in: a production name with spaces and a number.
REAL = [("Wide_08141855_C003.mov", ["Audio-Full-Mix"],
         "Interview Example Town 2_Wide_Audio-Full-Mix_08141855_C003"),
        ("Guest_08141858_C009.mov", ["Guest"],
         "Interview Example Town 2_Guest_08141858_C009"),
        ("Hosts_08141855_C005.mov", ["Host", "Co-host"],
         "Interview Example Town 2_Hosts_Host+Co-host_"
         "08141855_C005")]
for cam, spk, want in REAL:
    have = f("Interview Example Town 2", cam, spk)
    check("as delivered: %s" % cam.split("_")[0], have == want, have)

shutil.rmtree(D, ignore_errors=True)


def material(folder):
    """Two cameras, six seconds each, one channel of sound apiece.

    One channel on purpose: two uncorrelated channels would be cut into
    two tracks, and how many tracks a camera gives is the subject of
    camera_channels_test.py, not of this one.
    """
    for name, hz in zip(CAMERAS, (300, 700)):
        subprocess.run(
            ["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
             "testsrc=size=160x90:rate=25:duration=6",
             "-f", "lavfi", "-i",
             "sine=frequency=%d:duration=6" % hz,
             "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
             "yuv420p", "-c:a", "aac", "-ac", "1", "-shortest", "-y",
             os.path.join(folder, name)],
            check=True, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)


# One window in a process of its own: a second gui() standing on the
# first is not what a whole window makes of a whole project, and a
# window that hangs must not take the checks above down with it.
print("\n5./6. The window itself")
media = tempfile.mkdtemp(prefix="vpm_a5c_media_")
material(media)
child = subprocess.Popen(
    [sys.executable, os.path.abspath(__file__)],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    env=dict(os.environ, VPM_A5C_MEDIA=media, LANG="C", LC_ALL="C",
             LANGUAGE="en", QT_QPA_PLATFORM="offscreen"), cwd=HERE)
try:
    out, _ = child.communicate(timeout=420)
except subprocess.TimeoutExpired:
    child.kill()
    out, _ = child.communicate()
    out = (out or "") + "\nFAIL: the window never came back"
for line in (out or "").rstrip().split("\n"):
    print(line[:160])
if child.returncode != 0:
    error.append("the window")
shutil.rmtree(media, ignore_errors=True)

print("\n%s" % ("All good." if not error
                else "FAIL: %s" % ", ".join(error)))
sys.exit(1 if error else 0)
