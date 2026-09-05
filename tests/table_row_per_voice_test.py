# -*- coding: utf-8 -*-
"""A separation stored in the project becomes rows -- once somebody says so.

The model does not run here: the project file carries what the
separation found, and the way from there to the screen is what is
checked. Only an answer given by somebody shows the voices, and the
silence must throw nothing away -- bringing them back may not separate
anything again, so every door into a separation is counted.

A voice row is found by what it does: its fields carry a name a screen
reader can say, "belongs to -- Room.wav", and of the rows so named the
ones that put somebody on a camera and are not named after a file came
from the separation. The view itself is asked through
QAbstractItemModel, so a change of widget class does not rewrite it.

Two windows: a project carrying three voices and one carrying none,
both arranged so that no separation can start.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import json, re, subprocess, sys, tempfile, time, wave

# One clock for both processes: the child runs this file from the top
# as well, and stops in look() before the parent's own part.
began = time.time()

RATE = 48000
SEC = 12
# What the separation found, as the project file carries it. Three
# voices and not two, so the number of rows cannot pass for the number
# of files; told apart by how much each speaks, so the order of the
# rows is a statement, and their longest passages do not overlap.
FOUND = [("SPEAKER_00", [(1.0, 4.0), (9.0, 11.5)]),
         ("SPEAKER_01", [(5.0, 8.0)]),
         ("SPEAKER_02", [(8.2, 8.8)])]
LONGEST = [max(parts, key=lambda p: p[1] - p[0]) for _k, parts in FOUND]
CASES = (("found", "a project carrying a separation of three voices"),
         ("none", "a project carrying no separation"))
# Given once, before the voices are hidden, and looked for again after
# they have been brought back: what was typed has to outlive the rows.
NAMES = ["Anna", "Bo", "Cem"]
# The one name given to the recording itself, which hides the voices.
ALONE = "Ida"


# ---------------------------------------------------------- the child
def look(case, media):
    """One window, one project: report what the voice rows do."""
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ.setdefault("VPM_SILENT", "1")
    os.environ.setdefault("VPM_NO_UPDATE_CHECK", "1")
    # The suite switches the separation off; this test needs the way from
    # a stored result to the screen, so it is switched back on here and
    # every way into it is counted rather than assumed shut.
    os.environ.pop("VPM_NO_SPEAKER_SPLIT", None)
    from PySide6 import QtCore, QtWidgets
    from PySide6.QtTest import QTest

    app = QtWidgets.QApplication(sys.argv[:1])
    vpm = the_program.load()
    # The language is settled here too, or a standalone run on a German
    # machine would compare English keys with a German window.
    vpm.set_language("en")
    # Nothing may reach the network or the keychain: what is wanted is
    # the window, not a run.
    vpm.list_presets = lambda key: []
    vpm.load_api_key = lambda: ""
    vpm.update_offer = lambda *a, **k: None

    # Every door into taking a recording apart: fetching the model,
    # reading the cache, and the separation itself. Showing stored voices
    # has to cost none of them, so they are counted, not taken on trust.
    separations = []

    def no_setup(*a, **k):
        separations.append("fetching the model")
        return "not in a test"

    def no_split(source="", count=0, *a, **k):
        separations.append("separating %s" % os.path.basename(str(source)))
        return [], "not in a test"

    def no_cache(key):
        separations.append("reading the cache")
        return []

    vpm.fetch_model = no_setup
    vpm.speaker_split_available = lambda deep=False: True
    vpm.speaker_split_run = no_split
    vpm.speaker_cache_read = no_cache

    played = []
    real_players = vpm.make_player_widgets

    def player_widgets(*a):
        """The real player, with every load written down.

        Where and from which second it is asked to play is the only sign
        from outside that a click plays this voice; the ffplay fallback
        in the seventh argument would open a real window, so it goes.
        """
        a = list(a)
        a[6] = lambda *x, **k: None
        made = real_players(*a)
        for kind in made[2:]:
            real_load = kind.load

            def load(self, file_path, seconds=None, running=False,
                     _f=real_load):
                played.append((file_path, seconds, running))
                return _f(self, file_path, seconds, running)

            kind.load = load
        return made

    vpm.make_player_widgets = player_widgets

    handed = []

    def no_run(values, assignment_file_path=""):
        """What the run would be told -- and then no run.

        Everything the window has to say is turned into a command line
        here, so this is where "it arrives at the run" can be read. No
        command line makes start() give the file back and return.
        """
        handed.append(values)
        return None, None, []

    vpm.run_argv = no_run

    folder = tempfile.mkdtemp(prefix="vpm_voices_")
    recording = os.path.join(media, "Room.wav")
    video = os.path.join(media, "A_camera.mov")
    room = os.path.basename(recording)
    # One recording and one camera, and the Multitrack tick off: with
    # one track there is nothing to distribute, and the program refuses
    # to start while the tick says otherwise.
    d = {"format": vpm.FILE_FORMAT, "version": "test", "timeline": [],
         "call": [], "assignment": {}, "preset": "",
         "files": [{"path": recording, "kind": "audio"},
                   {"path": video, "kind": "video"}],
         "out_folder": os.path.join(folder, "Result"),
         "production": "Voices", "multitrack": False}
    if case == "found":
        stat = os.stat(recording)
        d["speakers"] = {"source": os.path.abspath(recording),
                         "mtime": int(stat.st_mtime),
                         "size": stat.st_size,
                         "model": vpm.SPEAKER_MODEL_NAME,
                         "model_mark": "", "num_speakers": 0,
                         "names": {},
                         "segments": [[k, a, b] for k, parts in FOUND
                                      for a, b in parts]}
    else:
        # A no that was given once and is stored: with it the program
        # separates nothing by itself, which makes this case safe to
        # open at all.
        d["speakers_local"] = False
    project = os.path.join(folder, "videopodcast-magic_Voices.json")
    with open(project, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.makedirs(d["out_folder"], exist_ok=True)

    QtWidgets.QFileDialog.getOpenFileName = staticmethod(
        lambda *a, **k: (project, ""))
    # Nothing may sit and wait for a click: a modal window would hold
    # the test until somebody kills it.
    QtWidgets.QDialog.exec = lambda self: QtWidgets.QDialog.Accepted
    QtWidgets.QMessageBox.exec = lambda self: QtWidgets.QMessageBox.Ok
    # Off the desktop on the way in, on any platform. The layout
    # machinery still has to run: without it every widget sits at Qt's
    # untouched 100 by 30 and selecting a row by where it is measures air.
    _show = QtWidgets.QWidget.show

    def offstage(self):
        self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
        _show(self)

    QtWidgets.QWidget.show = offstage
    QtWidgets.QDialog.show = offstage

    bad = []
    # A list, not a plain number: the checks are made in nested steps,
    # and "done" is taken here by the flag that says the window got
    # through them.
    judged = [0]

    def check(name, ok, extra=""):
        judged[0] += 1
        print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
        if not ok:
            bad.append("%s [%s]" % (name, extra or "no numbers"))

    def win():
        for x in app.topLevelWidgets():
            if "Video Podcast Magic" in x.windowTitle():
                return x

    def sheet_of(word):
        """The sheet whose tab carries that word, brought to the front."""
        for tw in win().findChildren(QtWidgets.QTabWidget):
            for k in range(tw.count()):
                if word.lower() in tw.tabText(k).lower():
                    tw.setCurrentIndex(k)
                    app.processEvents()
                    return tw.widget(k)
        return None

    def buttons(word):
        return [w for w in win().findChildren(QtWidgets.QPushButton)
                if word.lower() in w.text().lower()]

    def labels(word):
        return [w for w in win().findChildren(QtWidgets.QLabel)
                if word.lower() in w.text().lower()]

    def rows_named(sheet):
        """Every row on that sheet, by the name its fields are given.

        A field in a table cell is read out as its kind alone, so the
        program puts the column and the row into the accessible name,
        "belongs to -- Room.wav". That holds in a table and in a tree
        alike, which is why rows are counted from it, not rowCount().
        """
        rows = {}
        for w in sheet.findChildren(QtWidgets.QWidget):
            said = w.accessibleName()
            if " -- " not in said:
                continue
            rows.setdefault(said.split(" -- ", 1)[1].strip(),
                            []).append(w)
        return rows

    def camera_chooser(widgets):
        """The chooser that puts somebody on a camera, or None.

        Recognised by what can be picked in it, not by its column.
        """
        for w in widgets:
            if not isinstance(w, QtWidgets.QComboBox):
                continue
            picks = [w.itemData(i) for i in range(w.count())]
            if vpm.MIX_ONLY in picks and vpm.IGNORE_AUDIO in picks:
                return w
        return None

    def voice_rows(sheet, file_names):
        """The rows the separation produced, top to bottom.

        A row that puts somebody on a camera and is not named after one
        of the files is one of them, in a table of their own or under
        their recording in a tree alike. Ordered by where they sit, so
        that "the first row" is the first one somebody sees.
        """
        out = []
        for said, widgets in rows_named(sheet).items():
            plain = re.sub(r"\s*\(.*\)\s*$", "", said).strip()
            if plain in file_names:
                continue
            box = camera_chooser(widgets)
            if box is None:
                continue
            top = min(w.mapTo(sheet, w.rect().topLeft()).y()
                      for w in widgets)
            out.append((top, said, widgets, box))
        out.sort(key=lambda x: (x[0], x[1]))
        return out

    def name_field_of(sheet, said):
        """The field the name of that row is answered in.

        Which kind of widget it is depends on whether this machine can
        tell voices apart at all, so it is found by what it is for.
        """
        for w in rows_named(sheet).get(said, []):
            if w.accessibleName().startswith(vpm.T('Speaker name')):
                return w
        return None

    def text_of(w):
        """What an input field shows, chooser or plain field alike."""
        if w is None:
            return None
        for way in ("currentText", "text"):
            if hasattr(w, way):
                return str(getattr(w, way)()).strip()
        return None

    def type_into(w, text):
        """Type a name in, letter by letter, and be done with it.

        Letter by letter and not setText: the program tells typing from
        picking, and only the end of the typing counts as the answer.
        Return ends it, the same as clicking elsewhere.
        """
        inner = getattr(w, "lineEdit", None)
        inner = inner() if callable(inner) else w
        QTest.keyClicks(inner, text)
        QTest.keyClick(inner, QtCore.Qt.Key_Return)
        app.processEvents()

    def pick_several(w):
        """Pick the one entry the name field offers: several speakers.

        With the keyboard: it sends the same signal a click on the open
        list does and needs no popup on a machine that has no screen.
        """
        QTest.keyClick(w, QtCore.Qt.Key_Down)
        app.processEvents()

    def view_of(w):
        """The item view a field sits in, whatever class that is."""
        v = w
        while v is not None and not isinstance(
                v, QtWidgets.QAbstractItemView):
            v = v.parentWidget()
        return v

    def headings_of(view):
        """What the columns of that view are called."""
        m = view.model()
        return [str(m.headerData(c, QtCore.Qt.Horizontal) or "")
                for c in range(m.columnCount())]

    def row_of(view, begins):
        """The top-level row whose first cell begins with that."""
        m = view.model()
        for r in range(m.rowCount()):
            if str(m.index(r, 0).data() or "").startswith(begins):
                return m.index(r, 0)
        return None

    def under(view, where):
        """What hangs under that row: the first cell of every child."""
        m = view.model()
        if where is None:
            return None
        return [str(m.index(r, 0, where).data() or "")
                for r in range(m.rowCount(where))]

    def row_pick(box):
        """Select the row that chooser sits in, the way a click does.

        Which view carries it and which row of the view it is are both
        asked rather than known: a table answers that and so does a tree.
        """
        view = view_of(box)
        if view is None:
            return False
        spot = box.mapTo(view.viewport(), box.rect().center())
        where = view.indexAt(spot)
        if not where.isValid():
            return False
        view.clearSelection()
        view.setCurrentIndex(QtCore.QModelIndex())
        view.setCurrentIndex(where)
        app.processEvents()
        return True

    file_names = {os.path.basename(recording), os.path.basename(video)}
    # "Separated: " in whatever language the window is speaking.
    separated = vpm.TN(1, 'Separated: %s speaker',
                       'Separated: %s speakers').split("%s")[0]
    several = vpm.label_of(vpm.SEVERAL_SPEAKERS)
    picks = [os.path.basename(video), vpm.MIX_ONLY,
             os.path.basename(video)]

    def speakers_cell():
        """The Speakers cell of the recording's row, whatever sits in it.

        The column is found by its heading and not by its number: which
        columns there are depends on what this machine can do.
        """
        view = tree()
        where = row_of(view, room)
        if where is None:
            return None
        which = headings_of(view).index(vpm.T('Speakers'))
        return view.indexWidget(where.sibling(where.row(), which))

    def buttons_in_cell():
        """The buttons standing open in that cell, in their own words."""
        cell = speakers_cell()
        return [b.text() for b in
                (cell.findChildren(QtWidgets.QPushButton) if cell else [])
                if b.isVisible()]

    def labels_in_cell():
        """What that cell says, in its own words."""
        cell = speakers_cell()
        return [x.text() for x in
                (cell.findChildren(QtWidgets.QLabel) if cell else [])]

    # ------------------------------------------------------ the steps
    # One thing at a time: answering rebuilds the whole sheet, and a
    # check that reads it in the same breath reads the sheet that is
    # about to go.
    AGAIN, STOP = "again", "stop"
    waited = [0]
    sheet_now = [None]
    done = [False]

    def open_project():
        win().show()
        win().resize(1400, 900)
        app.processEvents()
        for w in win().findChildren(QtWidgets.QPushButton):
            if w.text().strip().startswith(vpm.T('Open project ...')[:8]):
                w.click()
                break

    def wait_for_sheet():
        """Wait for the recording's own row, not for a number of seconds.

        The sheet is built out of a thread, so a fixed pause is wrong on
        both sides. The voices come in the same breath as the recordings:
        once that row is there the voice rows are there too, or not.
        """
        sheet = sheet_of(vpm.T('Assignment && time window')[:8])
        named = rows_named(sheet) if sheet is not None else {}
        there = sheet is not None and room in named
        if not there and waited[0] < 120:
            waited[0] += 1
            return AGAIN
        check("the project brought its assignment sheet up", there,
              "%d such sheets after %d rounds of waiting, %s wanted among "
              "its %d rows: %s"
              % (0 if sheet is None else 1, waited[0], room, len(named),
                 sorted(named)[:5]))
        sheet_now[0] = sheet
        return None if there else STOP

    def sheet():
        return sheet_now[0]

    def tree():
        return view_of(name_field_of(sheet(), room))

    # --- the project carrying three voices, in three states

    def unanswered_look():
        """Nobody answered: nothing chosen for them, nothing thrown away."""
        rows = voice_rows(sheet(), file_names)
        check("nobody answered, so there are no voice rows", not rows,
              str([r[1] for r in rows]))
        check("and the name field of the recording is empty",
              text_of(name_field_of(sheet(), room)) == "",
              repr(text_of(name_field_of(sheet(), room))))
        # Asked of the model rather than of the widgets: on the screen
        # and in the tree are two questions.
        check("and the tree hangs nothing under the recording",
              under(tree(), row_of(tree(), room)) == [],
              str(under(tree(), row_of(tree(), room))))
        check("and the columns are the ones the sheet promises",
              vpm.T('Speaker name') in headings_of(tree())
              and vpm.T('Speakers') in headings_of(tree()),
              str(headings_of(tree())))
        # What was measured is kept and shown: the silence is about the
        # answer.
        mark = vpm.TN(len(FOUND), 'Separated: %s speaker',
                      'Separated: %s speakers') % len(FOUND)
        check("the row says all the same what was separated",
              bool(labels(mark)),
              str([x.text() for x in labels(separated)]))
        check("and nothing has been separated", not separations,
              str(separations))

    def say_several():
        pick_several(name_field_of(sheet(), room))

    def voices_look():
        """Three voices asked for: three rows, and what each one can do."""
        rows = voice_rows(sheet(), file_names)
        check("a row for every voice the separation found",
              len(rows) == len(FOUND), "%d rows" % len(rows))
        # The core of it: what was measured once is shown again for
        # nothing, and that is counted rather than assumed.
        check("and showing them separated nothing again",
              not separations, str(separations))
        check("and the field now says several speakers",
              text_of(name_field_of(sheet(), room)) == several,
              repr(text_of(name_field_of(sheet(), room))))
        check("and the tree hangs all three under the recording",
              under(tree(), row_of(tree(), room))
              == [vpm.T('Voice')] * len(FOUND),
              str(under(tree(), row_of(tree(), room))))
        if len(rows) != len(FOUND):
            for _t, said, _w, _b in rows:
                print("      %r" % said[:90])
            return STOP
        no_field = [said for _t, said, widgets, _b in rows
                    if not any(isinstance(w, QtWidgets.QLineEdit)
                               for w in widgets)]
        check("every row has a field to put a name in", not no_field,
              "%d of %d rows carry no name field: %s"
              % (len(no_field), len(rows), no_field))
        no_cam = [said for _t, said, _w, box in rows
                  if box.findData(os.path.basename(video)) < 0]
        check("and a chooser offering the camera itself", not no_cam,
              "%d of %d choosers do not offer %s: %s"
              % (len(no_cam), len(rows), os.path.basename(video), no_cam))
        # Every voice is asked for in turn and has to answer with its
        # own longest passage. The three do not overlap, so a position
        # says which voice was meant, and the first row says the order.
        aimed = []
        for _t, _s, _w, box in rows:
            before = len(played)
            row_pick(box)
            aimed.append(played[-1] if len(played) > before else None)
        check("a row picked plays that voice at its longest passage",
              all(got is not None and got[1] is not None and got[2]
                  and os.path.basename(got[0])
                  == os.path.basename(recording)
                  and a - 0.05 <= got[1] <= b
                  for got, (a, b) in zip(aimed, LONGEST)),
              str([None if got is None else round(got[1] or -1.0, 2)
                   for got in aimed]))
        for (_t, _s, widgets, box), name, pick in zip(rows, NAMES, picks):
            for w in widgets:
                if isinstance(w, QtWidgets.QLineEdit):
                    w.setText(name)
            box.setCurrentIndex(max(0, box.findData(pick)))
        app.processEvents()
        check("a voice that was missed can still be asked for",
              len(buttons(vpm.T('One more speaker in'))) == 1,
              str([b.text() for b in
                   buttons(vpm.T('One more speaker in'))]))
        check("and the window says what was found",
              bool(labels(vpm.TN(len(FOUND), 'Separated: %s speaker',
                                 'Separated: %s speakers') % len(FOUND))),
              str([x.text() for x in labels(separated)]))
        running = [b.text() for b in buttons(vpm.T('Stop'))
                   if b.isVisible()]
        check("and nothing is being computed", not running,
              "%d Stop buttons on show, wanted 0: %s"
              % (len(running), running))

    def say_one_name():
        type_into(name_field_of(sheet(), room), ALONE)

    def alone_look():
        """One name given instead: the rows go, the answer stays."""
        rows = voice_rows(sheet(), file_names)
        check("one name given, and the voice rows are gone", not rows,
              str([r[1] for r in rows]))
        # Answering rebuilds the whole sheet, the field being typed in
        # included: the name lived in the widget that was thrown away.
        check("the name survives the rebuild the answer causes",
              text_of(name_field_of(sheet(), room)) == ALONE,
              repr(text_of(name_field_of(sheet(), room))))
        check("and the tree hangs nothing under the recording again",
              under(tree(), row_of(tree(), room)) == [],
              str(under(tree(), row_of(tree(), room))))
        check("and saying one name separated nothing", not separations,
              str(separations))
        # The cell that says how the separation stands says only that.
        # The way back to several speakers is the name field, and the
        # one button that belongs here breaks a running separation off.
        check("the Speakers cell puts no button on show",
              not buttons_in_cell(), "%d on show: %s"
              % (len(buttons_in_cell()), buttons_in_cell()))
        stands = [vpm.TN(len(FOUND), 'Separated: %s speaker',
                         'Separated: %s speakers') % len(FOUND)]
        check("and the cell still says how the separation stands",
              labels_in_cell() == stands,
              "%s, wanted %s" % (labels_in_cell(), stands))
        pick_several(name_field_of(sheet(), room))

    def again_look():
        """The way back taken: the same three voices, as they were left."""
        rows = voice_rows(sheet(), file_names)
        check("asking for several speakers again brings the voices back",
              len(rows) == len(FOUND),
              "%d rows, wanted %d" % (len(rows), len(FOUND)))
        check("and brought them back without separating anything",
              not separations, str(separations))
        check("and the field says several speakers again",
              text_of(name_field_of(sheet(), room)) == several,
              repr(text_of(name_field_of(sheet(), room))))
        if len(rows) != len(FOUND):
            return STOP
        # What was typed into a row that has since been thrown away and
        # built again: the names live on the voice, not on the widget.
        got_names = [text_of(w) for _t, _s, widgets, _b in rows
                     for w in widgets
                     if isinstance(w, QtWidgets.QLineEdit)]
        check("the names given to the voices came back with them",
              got_names == NAMES, str(got_names))
        got_picks = [box.currentData() for _t, _s, _w, box in rows]
        check("and so did the cameras they were put on",
              got_picks == picks, str(got_picks))

    def dry_run():
        """The name and the camera of a row reach the run itself."""
        offered = ""
        for b in buttons(vpm.T('Dry run')):
            offered = "%r enabled=%s" % (b.text(), b.isEnabled())
            b.click()
            break
        app.processEvents()
        pairs = []
        for values in handed:
            for v in values.get("voices") or []:
                pairs.append((str(v.get("name") or "").strip(),
                              str(v.get("camera") or "")))
            # Both lists on purpose: which one carries a voice depends
            # on how the sheet is built.
            for r in values.get("rows") or []:
                pairs.append((str(r.get("speakers") or "").strip(),
                              str(r.get("camera_choice") or "")))
        check("what was typed and picked reaches the run",
              bool(handed) and all(pair in pairs
                                   for pair in zip(NAMES, picks)),
              str(pairs) if handed else "Dry run: " + (offered or "none"))

    # --- the project carrying no separation at all

    def empty_look():
        """Nothing separated: no voice rows, and the recording alone."""
        rows = voice_rows(sheet(), file_names)
        check("no separation, no voice rows", not rows,
              str([r[1] for r in rows]))
        named = rows_named(sheet())
        check("the recording is a row all the same", room in named,
              "%s wanted among the %d rows: %s"
              % (room, len(named), sorted(named)[:5]))
        check("and its name field is empty",
              text_of(name_field_of(sheet(), room)) == "",
              repr(text_of(name_field_of(sheet(), room))))
        check("and the tree hangs nothing under it",
              under(tree(), row_of(tree(), room)) == [],
              str(under(tree(), row_of(tree(), room))))
        check("and nothing says a separation was found",
              not labels(separated), str([x.text() for x
                                          in labels(separated)]))
        running = [b.text() for b in buttons(vpm.T('Stop'))
                   if b.isVisible()]
        check("and nothing is being computed", not running,
              "%d Stop buttons on show, wanted 0: %s"
              % (len(running), running))
        check("and nothing has been separated", not separations,
              str(separations))

    def name_it():
        type_into(name_field_of(sheet(), room), ALONE)

    def asked_look():
        """A name given where nothing was ever listened to.

        One person named is an answer, not a question: nothing is
        listened to because of it and nothing is put in the row's way
        asking whether there were several -- that is the name field's
        business, and it is where it was.
        """
        check("the name given is what the field says",
              text_of(name_field_of(sheet(), room)) == ALONE,
              repr(text_of(name_field_of(sheet(), room))))
        check("the Speakers cell puts no button on show",
              not buttons_in_cell(), "%d on show: %s"
              % (len(buttons_in_cell()), buttons_in_cell()))
        came = voice_rows(sheet(), file_names)
        check("and no voice rows came of a name", not came,
              "%d voice rows, wanted 0: %s"
              % (len(came), [said for _t, said, _w, _b in came]))
        check("and naming one person separated nothing", not separations,
              str(separations))

    plan = ([open_project, wait_for_sheet, unanswered_look, say_several,
             voices_look, say_one_name, alone_look, again_look, dry_run]
            if case == "found" else
            [open_project, wait_for_sheet, empty_look, name_it,
             asked_look])

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
        QtCore.QTimer.singleShot(250 if answer == AGAIN else 400, step)

    QtCore.QTimer.singleShot(300, step)
    # A window that never gets there must not hold the suite -- there is
    # no timeout(1) on this machine -- and must not pass either.
    QtCore.QTimer.singleShot(150000, app.quit)
    vpm.gui()
    if not done[0]:
        print("  the window never got as far as the checks   FAIL")
        bad.append("no answer")
    print("\n%d checks in %.2f s" % (judged[0], time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    return 1 if bad else 0


# --------------------------------------------------------- the parent
def material(folder):
    """One recording and one camera, twelve seconds of each."""
    import numpy as np
    rng = np.random.default_rng(11)
    sound = np.zeros(SEC * RATE)
    for a, b in ((1.0, 4.0), (5.0, 8.0), (9.0, 11.5)):
        n = int((b - a) * RATE)
        sound[int(a * RATE):int(a * RATE) + n] = rng.normal(0, 0.2, n)
    recording = os.path.join(folder, "Room.wav")
    with wave.open(recording, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes((np.clip(sound, -1, 1) * 32767)
                      .astype("<i2").tobytes())
    video = os.path.join(folder, "A_camera.mov")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
         "testsrc=size=160x90:rate=25:duration=%d" % SEC,
         "-f", "lavfi", "-i", "sine=frequency=300:duration=%d" % SEC,
         "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
         "yuv420p", "-c:a", "aac", "-shortest", "-y", video],
        check=True, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)


if os.environ.get("VPM_VOICES_CASE"):
    raise SystemExit(look(os.environ["VPM_VOICES_CASE"],
                          os.environ["VPM_VOICES_MEDIA"]))

# One window per case, one process per window: a second gui() in one
# process would be a second interface standing on the first.
media = tempfile.mkdtemp(prefix="vpm_voices_")
material(media)
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
        env=dict(os.environ, VPM_VOICES_CASE=name,
                 VPM_VOICES_MEDIA=media, LANG="C", LC_ALL="C",
                 LANGUAGE="en", QT_QPA_PLATFORM="offscreen"), cwd=HERE)
    try:
        out, _ = child.communicate(timeout=420)
    except subprocess.TimeoutExpired:
        child.kill()
        out, _ = child.communicate()
        out = (out or "") + "\nthe window never came back"
    for line in (out or "").rstrip().split("\n"):
        print(line[:160])
        head = line.split(" checks in ")[0]
        if " checks in " in line and head.isdigit():
            done += int(head)
    if child.returncode != 0:
        bad.append(name)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
