# -*- coding: utf-8 -*-
"""A second separation leaves the first its voices, names and cameras.

The steps: a recording set to several speakers, a name and a camera
given to each voice found in it, then the camera's sound made material
and set to several speakers too, and its voices named and seated as
well. The sections: the first separation, its voices seated, the
second beside it -- which takes none of the first's cameras and puts
none of its own voices on one -- what the run is handed, with every
voice on a camera of its own recording, the project file written, the
camera's sound switched off again, and -- in a second window -- that
file opened afresh.

Where a seating takes effect is not asked here: the window's part ends
at the handover, and cut_voice_on_its_camera measures what a run makes
of a voice and a camera.

The model does not run. A stand-in answers with two voices for the
recording and three for the camera, both calling their first voice
SPEAKER_00, and counts every call: so "nothing was separated again" is
counted rather than believed. The cache is stood in for as well, which
is what keeps the real one out of it.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import array, json, random, subprocess, sys, tempfile, time, wave

# One clock for both processes: the child runs this file from the top
# as well, and stops in look() before the parent's own part.
began = time.time()

RATE = 48000
SEC = 12
PRODUCTION = "Both"
ROOM = "Room.wav"
CAMERA = "A_camera.mov"
# The cameras to sit on. The first of them is the one whose own sound
# becomes the second recording; a voice may sit on it like on any
# other. Five, so that each of the five voices gets one of its own and
# a voice on the wrong recording's camera is visible as such.
VIDEOS = [CAMERA, "B_camera.mov", "C_camera.mov", "D_camera.mov",
          "E_camera.mov"]
# Two recordings, and both of them call their first voice SPEAKER_00 --
# which is the whole point: a voice is only a name together with the
# recording it was heard in. Different numbers, so a row that shows the
# wrong recording's separation cannot pass for the right one.
FOUND = {ROOM: [("SPEAKER_00", [(1.0, 4.0), (9.0, 11.5)]),
                ("SPEAKER_01", [(5.0, 8.0)])],
         CAMERA: [("SPEAKER_00", [(0.5, 2.0)]),
                  ("SPEAKER_01", [(3.0, 5.0)]),
                  ("SPEAKER_02", [(6.0, 9.0)])]}
# Typed into the two voices of the recording, and looked for again
# after the camera has been taken apart.
NAMES = ["Anna", "Bo"]
# Typed into the three voices of the camera's sound. None of them is
# one of the two above: since 31.8.2026 the program refuses the same
# speaker name in two recordings, and a test that handed out the same
# names would be measuring that refusal instead of the seating.
NAMES_CAMERA = ["Cid", "Del", "Eve"]
# Which camera each voice is set to, in the order the voices stand.
# The two recordings take cameras of their own, so a voice that landed
# on the other recording's camera is read off the list as such.
SEATS = {ROOM: ["B_camera.mov", "C_camera.mov"],
         CAMERA: [CAMERA, "D_camera.mov", "E_camera.mov"]}
# How many passes a row may stand unchanged before the wait gives up.
# Standstill and not a deadline: the builder is slower than this
# machine, and a slow machine still changes something.
STILL = 200
STEP_MS = 100          # between two passes of a wait
NEXT_MS = 300          # between two steps of the plan
# Over the whole run, and well over the waits inside it: a step that
# never comes has to be reported by the check that asks about it, not
# by the window being cut off in the middle of the plan.
WHOLE_MS = 420000


# The two windows, and what each of them is there for.
CASES = (("make", "two recordings separated one after the other"),
         ("again", "the project written by that window, opened afresh"))


# ---------------------------------------------------------- the child
def look(case, media, folder):
    """One window: the separations, or the project file opened again."""
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ.setdefault("VPM_SILENT", "1")
    os.environ.setdefault("VPM_NO_UPDATE_CHECK", "1")
    # The suite switches the separation off. This test is about what
    # two separations do to each other, so it is switched back on here
    # -- and every way into the real one is stood in for below.
    os.environ.pop("VPM_NO_SPEAKER_SPLIT", None)
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtTest import QTest

    app = QtWidgets.QApplication(sys.argv[:1])
    vpm = the_program.load()
    # Settled here too, or a standalone run on a German machine would
    # hold English keys against a German window.
    vpm.set_language("en")
    # Nothing may reach the network or the keychain: what is wanted is
    # the window, not a run.
    vpm.list_presets = lambda key: []
    vpm.load_api_key = lambda: ""
    vpm.update_offer = lambda *a, **k: None

    recording = os.path.join(media, ROOM)
    videos = [os.path.join(media, short) for short in VIDEOS]

    # Every call, in the order they came. The counter is what says
    # whether switching the camera's sound off or opening the project
    # again cost a separation.
    ran = []

    def split_stand_in(path, num_speakers=0, report=None, stopping=None):
        """Two voices for the recording, three for the camera."""
        short = os.path.basename(str(path))
        ran.append(short)
        if short not in FOUND:
            return [], "the test knows no recording called %s" % short
        return [(k, list(parts)) for k, parts in FOUND[short]], ""

    vpm.speaker_split_run = split_stand_in
    # The environment is never built and the model is never fetched:
    # both would take hundreds of megabytes off the network.
    vpm.speaker_split_available = lambda deep=False: True
    vpm.speaker_split_setup = lambda report=None: ""
    # A fixed mark, so the project file's separations still fit their
    # model whether or not this machine carries one.
    vpm.speaker_model_mark = lambda folder="": "testmark"
    # The real store stays untouched, in both directions: nothing is
    # read out of it and nothing is written into it.
    vpm.speaker_cache_read = lambda key: None
    vpm.speaker_cache_write = lambda key, segments: None
    # A separation is followed by writing down what is said in it, and
    # that reaches for a speech recogniser this test has no use for.
    vpm.words_at_hand = lambda audio_path, language="": []

    handed = []
    planned = []
    # The real builder of the command line, kept before it is stood in
    # for. It is the only thing that knows which camera a voice reaches
    # the run on; working that out in the test again would prove that
    # the test can copy the program, and nothing else.
    build_argv = vpm.run_argv

    def no_run(values, assignment_file_path=""):
        """What a run would be told -- and then no run."""
        handed.append(values)
        try:
            planned.append(build_argv(values, assignment_file_path))
        except Exception as e:
            # Kept as the answer rather than swallowed: a raise inside a
            # Qt slot is printed somewhere nobody reads, and the two
            # checks below would then say "no plan" without a reason.
            planned.append((None, {"voices_of": "no plan: %r" % e}, []))
        return None, None, []

    vpm.run_argv = no_run

    project = os.path.join(folder, "Result",
                           "%s%s.json" % (vpm.PROJECT_PREFIX, PRODUCTION))
    os.makedirs(os.path.dirname(project), exist_ok=True)
    # One recording and five cameras, nothing separated yet, and the
    # Multitrack tick off: one recording is spread over every camera
    # however many there are, and the cameras are carried by the voices
    # under it. "speakers_local": False is a no that was given once
    # and stored -- with it the program separates nothing by itself,
    # which is what makes the steps below the same on every machine:
    # unasked, a Mac starts a separation of its own accord and the
    # builder's two machines do not.
    if case == "make":
        d = {"format": vpm.FILE_FORMAT, "version": "test", "timeline": [],
             "call": [], "assignment": {}, "preset": "",
             "files": ([{"path": recording, "kind": "audio"}]
                       + [{"path": v, "kind": "video"} for v in videos]),
             "out_folder": os.path.dirname(project),
             "production": PRODUCTION, "multitrack": False,
             "speakers_local": False}
        with open(project, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)

    QtWidgets.QFileDialog.getOpenFileName = staticmethod(
        lambda *a, **k: (project, ""))
    # Nothing may sit and wait for a click: a modal window would hold
    # the test until somebody killed it.
    QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
    QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
    # Off the desktop on the way in, on any platform. The layout
    # machinery still runs: the rows are read out of the model, but a
    # window of Qt's untouched size builds them all the same.
    _show = QtWidgets.QWidget.show

    def offstage(self):
        self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
        _show(self)

    QtWidgets.QWidget.show = offstage
    QtWidgets.QDialog.show = offstage

    bad = []
    # A list, not a plain number: the checks are made in nested steps,
    # and "done" is taken by the flag that says the window got through
    # them.
    judged = [0]

    def check(name, ok, extra=""):
        judged[0] += 1
        print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
        if not ok:
            bad.append("%s [%s]" % (name, extra or "no numbers"))

    def tally():
        """How many separations ran, by recording.

        The count and not the list: a program separating over and over
        writes thousands of them, and a failure line nobody can read to
        the end says less than one that fits.
        """
        out = {}
        for x in ran:
            out[x] = out.get(x, 0) + 1
        return out

    def win():
        for x in app.topLevelWidgets():
            if "Video Podcast Magic" in x.windowTitle():
                return x

    def the_tree():
        """The assignment tree, found by the columns it promises.

        Not by its class: the file list is a tree as well, and a search
        by class would answer with whichever came first.
        """
        for v in win().findChildren(QtWidgets.QTreeView):
            m = v.model()
            if m is None:
                continue
            heads = [str(m.headerData(c, QtCore.Qt.Horizontal) or "")
                     for c in range(m.columnCount())]
            if vpm.T('Speaker name') in heads and vpm.T('Speakers') in heads:
                return v, heads
        return None, []

    def rows_now():
        """Every recording in the tree: its voices' names, and its mark.

        Asked of the model and of the fields in it, so that a change of
        widget class does not rewrite this. Keyed by the file name the
        row begins with -- a camera contributing its sound writes more
        than that into the same cell.
        """
        tree, heads = the_tree()
        if tree is None:
            return {}
        m = tree.model()
        name_col = heads.index(vpm.T('Speaker name'))
        mark_col = heads.index(vpm.T('Speakers'))
        out = {}
        for r in range(m.rowCount()):
            top = m.index(r, 0)
            names = []
            for k in range(m.rowCount(top)):
                w = tree.indexWidget(m.index(k, name_col, top))
                names.append(str(w.text()).strip()
                             if hasattr(w, "text") else "")
            mark = ""
            cell = tree.indexWidget(m.index(r, mark_col))
            for lab in (cell.findChildren(QtWidgets.QLabel)
                        if cell is not None else []):
                if lab.text():
                    mark = lab.text()
                    break
            out[str(top.data() or "")] = (names, mark)
        return out

    def row_for(short):
        """The row of that file: its names and its mark, or None."""
        for caption, value in rows_now().items():
            if caption.startswith(short):
                return value
        return None

    def separated(n):
        """What a row says when that many voices were found in it."""
        return vpm.TN(n, 'Separated: %d speaker',
                      'Separated: %d speakers') % n

    def name_field_of(short):
        """The field the name of that recording is answered in."""
        for w in win().findChildren(QtWidgets.QWidget):
            said = w.accessibleName()
            if said.startswith(vpm.T('Speaker name')) \
                    and " -- " in said \
                    and said.split(" -- ", 1)[1].strip().startswith(short):
                return w
        return None

    def pick_several(short):
        """Answer the name field with its one entry: several speakers.

        With the keyboard, which sends the same signal a click on the
        open list does and needs no popup on a machine with no screen.
        """
        w = name_field_of(short)
        if w is None:
            return False
        QTest.keyClick(w, QtCore.Qt.Key_Down)
        app.processEvents()
        return True

    def camera_audio_set(on):
        """Answer the Camera audio field of the video file.

        Found by what can be picked in it and by the row it names, never
        by a column; the same value stands in more than one place, and
        any of them is the answer.
        """
        want = vpm.AUDIO_MATERIAL if on else vpm.AUDIO_UNUSED
        for w in win().findChildren(QtWidgets.QComboBox):
            said = w.accessibleName()
            if not said.startswith(vpm.T('Camera audio')):
                continue
            if CAMERA not in said or not w.isEnabled():
                continue
            i = w.findData(want)
            if i < 0:
                continue
            w.setCurrentIndex(i)
            app.processEvents()
            return True
        return False

    def type_into(w, text):
        """Type a name in over what stands there, and be done with it.

        Letter by letter and not setText: what a person does is type,
        and Return ends it the way clicking elsewhere does.
        """
        w.setFocus()
        w.selectAll()
        QTest.keyClicks(w, text)
        QTest.keyClick(w, QtCore.Qt.Key_Return)
        app.processEvents()

    def voice_cells(short, column):
        """One column of the voice rows under that recording.

        By the column's heading rather than by its number: which column
        is where depends on whether the separation is switched off at
        all, and a number would quietly read the one next to it.
        """
        tree, heads = the_tree()
        if tree is None or column not in heads:
            return []
        m = tree.model()
        col = heads.index(column)
        for r in range(m.rowCount()):
            top = m.index(r, 0)
            if not str(top.data() or "").startswith(short):
                continue
            return [tree.indexWidget(m.index(k, col, top))
                    for k in range(m.rowCount(top))]
        return []

    def voice_fields(short):
        """The name fields of the voices under that recording."""
        return voice_cells(short, vpm.T('Speaker name'))

    def seats_now(short):
        """Which camera each voice of that recording is set to.

        The value behind the entry, not the words on it: the list shows
        a file name for a camera and a sentence for the two answers
        that are no camera, and only the value is the same in every
        language.
        """
        return [str(w.currentData() or "") if hasattr(w, "currentData")
                else "" for w in voice_cells(short, vpm.T('belongs to'))]

    # What could be answered when the voices were seated, per recording.
    offered = {}

    def seat(short):
        """Put the voices of that recording on the cameras meant for them.

        A camera that is not in the list is not picked and is written
        down as missing: the check that follows then says the camera
        was never on offer instead of blaming the seating.
        """
        boxes = voice_cells(short, vpm.T('belongs to'))
        got = []
        for w, want in zip(boxes, SEATS[short]):
            i = w.findData(want) if hasattr(w, "findData") else -1
            if i >= 0:
                w.setCurrentIndex(i)
            got.append(want if i >= 0 else "%s not on offer" % want)
        offered[short] = got
        app.processEvents()

    # ------------------------------------------------------- the wait
    AGAIN, STOP = "again", "stop"
    seen = {}

    def rows_wanted(want):
        """The rows *want* names, as (voices, mark) or None."""
        out = {}
        for short in want:
            row = row_for(short)
            out[short] = None if row is None else (len(row[0]), row[1])
        return out

    def seats_wanted(want):
        """The cameras the voices of those recordings are set to."""
        return {short: seats_now(short) for short in want}

    def waiter(name, want, read=None):
        """A step that waits for the sheet to say *want*.

        *read* is what is asked -- the voices under each recording, or
        the cameras they sit on. Never the clock: what is watched is
        the sheet itself, and the wait ends when it has stood unchanged
        through STILL passes. A slow machine keeps its patience, a
        standing one does not -- and patience run out is not an answer,
        it is what the next check reports.
        """
        read = read or rows_wanted
        mine = {"last": None, "still": 0, "passes": 0}

        def step():
            now = read(want)
            mine["passes"] += 1
            if now != mine["last"]:
                mine["last"] = now
                mine["still"] = 0
            else:
                mine["still"] += 1
            seen[name] = (now, mine["passes"], mine["still"])
            if now == want:
                return None
            return AGAIN if mine["still"] < STILL else None

        return step

    def said(name):
        """What that wait ended on, and how long it went on for."""
        now, passes, still = seen.get(name, (None, 0, 0))
        return "%s after %d passes, %d of them unchanged" % (
            now, passes, still)

    # ------------------------------------------------------ the steps
    # One thing at a time: answering rebuilds the whole sheet, and a
    # check reading it in the same breath reads the sheet about to go.
    done = [False]
    switched = [None, None]
    file_said = [None]
    saved = [None]
    started = [None]

    def open_project():
        win().show()
        win().resize(1400, 900)
        app.processEvents()
        for w in win().findChildren(QtWidgets.QPushButton):
            if w.text().strip().startswith(vpm.T('Open project ...')[:8]):
                w.click()
                return
        print("  no way into a project was found              FAIL")
        bad.append("no open button")

    def say_several_room():
        switched[0] = pick_several(ROOM)

    def look_room():
        row = row_for(ROOM) or ([], "")
        check("the recording comes apart into the voices it was heard to "
              "hold", len(row[0]) == len(FOUND[ROOM])
              and row[1] == separated(len(FOUND[ROOM])),
              "several speakers picked: %s; %s" % (switched[0],
                                                   said("room")))
        if len(row[0]) != len(FOUND[ROOM]):
            return STOP

    def type_names():
        for i, name in enumerate(NAMES):
            fields = voice_fields(ROOM)
            if i < len(fields) and fields[i] is not None:
                type_into(fields[i], name)

    def look_names():
        got = [str(w.text()).strip() for w in voice_fields(ROOM)
               if hasattr(w, "text")]
        check("each voice row took the name that was typed into it",
              got == NAMES, "%s, wanted %s" % (got, NAMES))

    def seat_room():
        seat(ROOM)

    def look_seated():
        got = seats_now(ROOM)
        check("each voice of the first recording sits on the camera it "
              "was given", got == SEATS[ROOM],
              "%s under %s, wanted %s -- answered: %s -- %s"
              % (got, ROOM, SEATS[ROOM], offered.get(ROOM),
                 said("seated")))

    def camera_on():
        switched[1] = camera_audio_set(True)

    def look_camera_row():
        check("the camera's sound becomes a recording of its own",
              row_for(CAMERA) is not None,
              "field answered: %s; %s" % (switched[1], said("camera row")))
        if row_for(CAMERA) is None:
            return STOP

    def say_several_camera():
        pick_several(CAMERA)

    def look_both():
        room = row_for(ROOM) or ([], "")
        camera = row_for(CAMERA) or ([], "")
        check("the camera comes apart into the voices heard on it",
              len(camera[0]) == len(FOUND[CAMERA]),
              "%d voices under %s, wanted %d -- %s"
              % (len(camera[0]), CAMERA, len(FOUND[CAMERA]),
                 said("both")))
        check("the first recording keeps its voices while a second is "
              "separated", len(room[0]) == len(FOUND[ROOM]),
              "%d voices under %s, wanted %d -- %s"
              % (len(room[0]), ROOM, len(FOUND[ROOM]), said("both")))
        check("and they still carry the names that were typed into them",
              room[0] == NAMES, "%s, wanted %s" % (room[0], NAMES))
        check("no voice of the second recording carries one of those "
              "names", not (set(NAMES) & set(camera[0])),
              "%s under %s against %s" % (camera[0], CAMERA, NAMES))
        check("every row says the number of voices found in its own "
              "recording",
              room[1] == separated(len(FOUND[ROOM]))
              and camera[1] == separated(len(FOUND[CAMERA])),
              "%s says %r, %s says %r" % (ROOM, room[1], CAMERA, camera[1]))

    def look_room_kept():
        got = seats_now(ROOM)
        check("separating a second recording leaves the first its "
              "cameras", got == SEATS[ROOM],
              "%s under %s, wanted %s -- %s"
              % (got, ROOM, SEATS[ROOM], said("both")))

    def look_camera_seats():
        got = seats_now(CAMERA)
        # What the program put there of its own accord, before anybody
        # has answered for these voices: the fault this is about read
        # the first recording's answers back onto them.
        strayed = sorted(set(got) & set(SEATS[ROOM]))
        check("no voice of the second recording is put on a camera of "
              "the first", not strayed,
              "%s under %s, %s belong to %s -- on both: %s"
              % (got, CAMERA, SEATS[ROOM], ROOM, strayed or "none"))

    def name_camera_voices():
        for i, name in enumerate(NAMES_CAMERA):
            fields = voice_fields(CAMERA)
            if i < len(fields) and fields[i] is not None:
                type_into(fields[i], name)

    def seat_camera():
        seat(CAMERA)

    def press_start():
        """Ask for a run. None starts: run_argv is stood in for above."""
        for w in win().findChildren(QtWidgets.QPushButton):
            if w.text().strip() == vpm.T('Start'):
                started[0] = "enabled" if w.isEnabled() else "greyed out"
                w.click()
                app.processEvents()
                return
        started[0] = "no Start button was found"

    def handed_seats():
        """Name -> the camera the run is told, by file name.

        Read out of the plan the window built, not out of the sheet: it
        is the plan that travels, and a voice that never reached it
        takes no picture whatever the sheet showed.
        """
        wishes = (planned[-1][1] if planned else None) or {}
        where = wishes.get("voices_of")
        if not isinstance(where, dict):
            return where
        return {k: os.path.basename(v) for k, v in where.items()}

    def look_handed_room():
        got = handed_seats()
        want = dict(zip(NAMES, SEATS[ROOM]))
        check("the run is handed the first recording's voices on their "
              "own cameras",
              isinstance(got, dict)
              and all(got.get(k) == v for k, v in want.items()),
              "%s, wanted %s in it -- Start: %s"
              % (got, want, started[0]))

    def look_handed_camera():
        got = handed_seats()
        want = dict(zip(NAMES_CAMERA, SEATS[CAMERA]))
        check("the run is handed the second recording's voices on their "
              "own cameras",
              isinstance(got, dict)
              and all(got.get(k) == v for k, v in want.items()),
              "%s, wanted %s in it -- Start: %s"
              % (got, want, started[0]))

    def save_project():
        for a in win().findChildren(QtGui.QAction):
            if a.text().replace("&", "").strip() == vpm.T('Save project'):
                a.trigger()
                saved[0] = True
                break
        app.processEvents()
        try:
            with open(project, encoding="utf-8") as f:
                d = json.load(f) or {}
        except (OSError, ValueError) as e:
            file_said[0] = "the project file could not be read: %s" % e
            return
        block = d.get("speakers") or {}
        file_said[0] = sorted(
            [os.path.basename(block.get("source") or "?")]
            + [os.path.basename(x.get("source") or "?")
               for x in (block.get("more") or [])]) if block else []

    def look_file():
        check("the project file carries both separations",
              file_said[0] == sorted([ROOM, CAMERA]),
              "%s, wanted %s -- asked to save: %s"
              % (file_said[0], sorted([ROOM, CAMERA]), saved[0]))

    def camera_off():
        camera_audio_set(False)

    def look_off():
        room = row_for(ROOM) or ([], "")
        check("switching the camera's sound off takes nothing from the "
              "first recording",
              len(room[0]) == len(FOUND[ROOM]) and room[0] == NAMES,
              "%d voices named %s under %s -- %s"
              % (len(room[0]), room[0], ROOM, said("off")))
        check("and nothing was separated a second time", len(ran) == 2,
              "%d separations: %s -- %s" % (len(ran), tally(),
                                            said("off")))

    def camera_on_again():
        camera_audio_set(True)

    def on_again_note():
        """Say so if the sound did not come back: the next window pays.

        Not a judgement -- what is claimed about switching off stands
        above. This is the state the window is left in, and the window
        writes it out as it closes.
        """
        if seen.get("on again", (None, 0, 0))[0] != both_there:
            print("  the camera's sound never came back on: %s"
                  % said("on again"))

    def look_reopened():
        room = row_for(ROOM) or ([], "")
        camera = row_for(CAMERA) or ([], "")
        check("opening the project again brings both recordings back "
              "with their voices",
              len(room[0]) == len(FOUND[ROOM])
              and len(camera[0]) == len(FOUND[CAMERA]),
              "%d under %s and %d under %s -- %s"
              % (len(room[0]), ROOM, len(camera[0]), CAMERA,
                 said("reopened")))
        check("and opening it again separated nothing", not ran,
              "%d separations: %s" % (len(ran), tally()))

    both_there = {ROOM: (len(FOUND[ROOM]), separated(len(FOUND[ROOM]))),
                  CAMERA: (len(FOUND[CAMERA]),
                           separated(len(FOUND[CAMERA])))}
    plan = ([open_project,
             waiter("sheet", {ROOM: (0, "")}),
             say_several_room,
             waiter("room", {ROOM: (len(FOUND[ROOM]),
                                    separated(len(FOUND[ROOM])))}),
             look_room,
             type_names,
             look_names,
             seat_room,
             waiter("seated", {ROOM: SEATS[ROOM]}, seats_wanted),
             look_seated,
             camera_on,
             waiter("camera row", {CAMERA: (0, "")}),
             look_camera_row,
             say_several_camera,
             waiter("both", both_there),
             look_both,
             look_room_kept,
             look_camera_seats,
             name_camera_voices,
             seat_camera,
             waiter("seated both", {ROOM: SEATS[ROOM],
                                    CAMERA: SEATS[CAMERA]}, seats_wanted),
             press_start,
             look_handed_room,
             look_handed_camera,
             save_project,
             look_file,
             camera_off,
             waiter("off", {ROOM: (len(FOUND[ROOM]),
                                   separated(len(FOUND[ROOM]))),
                            CAMERA: None}),
             look_off,
             # The window writes the project out as it closes, so it is
             # left the way the next one has to find it: with the
             # camera's sound in use, which is the state the second
             # case is about.
             camera_on_again,
             waiter("on again", both_there),
             on_again_note]
            if case == "make" else
            [open_project,
             waiter("reopened", both_there),
             look_reopened])

    def stop_now():
        """Nothing more to ask. The verdict stands at the end of look()."""
        done[0] = True
        app.quit()

    def step():
        if not plan:
            stop_now()
            return
        try:
            answer = plan[0]()
        except Exception:
            import traceback
            traceback.print_exc()
            bad.append("crash")
            stop_now()
            return
        if answer == STOP:
            stop_now()
            return
        if answer != AGAIN:
            plan.pop(0)
        QtCore.QTimer.singleShot(STEP_MS if answer == AGAIN else NEXT_MS,
                                 step)

    QtCore.QTimer.singleShot(300, step)
    # A window that never gets there must not hold the suite up, and
    # must not pass either: the plan stops here and the count below says
    # how far it got.
    QtCore.QTimer.singleShot(WHOLE_MS, app.quit)
    vpm.gui()
    if not done[0]:
        print("  the window never got as far as the checks   FAIL")
        bad.append("no answer")
    print("\n%d checks in %.2f s" % (judged[0], time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    return 1 if bad else 0


# --------------------------------------------------------- the parent
def material(folder):
    """One stereo recording and five cameras with sound, twelve seconds.

    Both channels of the recording carry the same signal, so the pair
    judgement calls them one stereo track and the recording stays one
    row -- what is measured here is two recordings, not two tracks out
    of one file.

    The cameras hear the same room, quieter. They have to: a camera
    whose sound matches nothing is put off the common time axis, and a
    recording that could not be placed is not offered to the separation
    at all. All five are made in one call to ffmpeg -- five processes
    would be five process starts, and that is what the Windows builder
    charges for.
    """
    rng = random.Random(11)
    sound = array.array("h", [0]) * (SEC * RATE)
    for a, b in ((1.0, 4.0), (5.0, 8.0), (9.0, 11.5)):
        for i in range(int(a * RATE), int(b * RATE)):
            sound[i] = int(max(-1.0, min(1.0, rng.gauss(0, 0.2))) * 32767)
    both = array.array("h", [0]) * (2 * SEC * RATE)
    both[0::2] = sound
    both[1::2] = sound
    recording = os.path.join(folder, ROOM)
    with wave.open(recording, "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes(both.tobytes())
    build = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
             "testsrc=size=160x90:rate=25:duration=%d" % SEC,
             "-i", recording]
    for short in VIDEOS:
        build += ["-map", "0:v", "-map", "1:a", "-af", "volume=0.6",
                  "-ac", "1", "-c:v", "libx264", "-preset", "ultrafast",
                  "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
                  os.path.join(folder, short)]
    subprocess.run(build, check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)


if os.environ.get("VPM_BOTH_CASE"):
    raise SystemExit(look(os.environ["VPM_BOTH_CASE"],
                          os.environ["VPM_BOTH_MEDIA"],
                          os.environ["VPM_BOTH_FOLDER"]))

# One window per case, one process per window: gui() does not come
# back, and a second one in this process would be a second interface
# standing on the first. The second window is a fresh program opening
# the file the first one wrote, which is what "opened again" means --
# in the same process a value made once for a file outlives the
# project it was made in.
media = tempfile.mkdtemp(prefix="vpm_both_")
material(media)
folder = tempfile.mkdtemp(prefix="vpm_both_")
# Every judgement in this test is made in a window, and every window is
# a process of its own. What they judged is carried up here, so the
# floor covers them: a window that stops judging brings the number down
# instead of passing.
done = 0
bad = []
for name, what in CASES:
    print("\n%s:" % what)
    child = subprocess.Popen(
        [sys.executable, os.path.abspath(__file__)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        env=dict(os.environ, VPM_BOTH_CASE=name, VPM_BOTH_MEDIA=media,
                 VPM_BOTH_FOLDER=folder, LANG="C", LC_ALL="C",
                 LANGUAGE="en", QT_QPA_PLATFORM="offscreen"), cwd=HERE)
    try:
        out, _ = child.communicate(timeout=600)
    except subprocess.TimeoutExpired:
        child.kill()
        out, _ = child.communicate()
        out = (out or "") + "\nthe window never came back"
    for line in (out or "").rstrip().split("\n"):
        # Long enough for a whole judgement to come through: a line cut
        # off here is a line the report cannot repeat, and on another
        # machine the line is all there is.
        print(line[:400])
        head = line.split(" checks in ")[0]
        if " checks in " in line and head.isdigit():
            done += int(head)
    if child.returncode != 0:
        bad.append(name)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
