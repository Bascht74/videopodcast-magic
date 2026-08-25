# -*- coding: utf-8 -*-
"""A separation stored in the project becomes rows -- once somebody says so.

The model does not run here: the project file already carries what the
separation found. What is checked is the way from there to the screen,
and it is checked as behaviour rather than as furniture.

Until 25.8.2026 that way was automatic: a stored separation of three
voices put three rows on the screen by itself and wrote "several
speakers" into the field above them, so as not to contradict them --
the program answering its own question. Only an answer given by
somebody shows them now, and a project nobody answered for shows an
empty field and no rows.

Which makes the promise that goes with it the thing to check: the
silence throws nothing away. Saying "several speakers" later has to
bring the voices back *without separating anything again* -- three
minutes of computing must not be the price of a mis-click. So every
door into a separation is counted here rather than assumed shut, and
the count stays at nought while the voices appear, go and come back.

One window follows all three states: nobody answered; "several
speakers" picked in the field; a name typed instead, which hides the
voices and survives the rebuild that answer causes, and then the offer
in the Speakers cell, which brings them back as they were left.

A voice row is looked for by what it does, not by where it sits. Every
field the program puts into a row carries a name a screen reader can
say, "belongs to -- Room.wav", and the part behind the first dash names
the row; fields sharing it are one row, in a table or under a parent in
a tree alike. Of those rows, the ones that put somebody on a camera and
are not named after a file are the ones the separation produced. Where
the view itself is asked something -- what its columns are called, what
hangs under the recording -- it is asked through QAbstractItemModel,
headerData and index(row, column, parent): the assignment was a
QTableWidget until 25.8.2026 and is a QTreeView now, and a test naming
either would have to be rewritten the next time somebody is right about
that question.

Two windows, one after the other, because the number of rows is the
point: three voices carried are three rows once they are asked for, and
a project carrying none has none however it is asked. Both are arranged
so that no separation can start -- setting one up fetches 218 MB and a
run takes minutes.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import json, re, subprocess, sys, tempfile, wave

RATE = 48000
SEC = 12
# What the separation found, as the project file carries it: raw, in
# the time of the recording itself. Three voices and not two, so that
# the number of rows cannot be mistaken for the number of files or for
# a constant somebody wrote down. They are told apart by how much they
# speak -- 5.5 s, 3.0 s, 0.6 s -- so the order of the rows is a
# statement and not an accident, and their longest passages do not
# overlap, so a position handed to the player names one voice and no
# other.
FOUND = [("SPEAKER_00", [(1.0, 4.0), (9.0, 11.5)]),
         ("SPEAKER_01", [(5.0, 8.0)]),
         ("SPEAKER_02", [(8.2, 8.8)])]
LONGEST = [max(parts, key=lambda p: p[1] - p[0]) for _k, parts in FOUND]
CASES = (("found", "a project carrying a separation of three voices"),
         ("none", "a project carrying no separation"))
# The names and cameras given to the three voices. They are given
# once, before the voices are hidden, and looked for again after they
# have been brought back: what was typed has to outlive the rows it
# was typed into.
NAMES = ["Anna", "Bo", "Cem"]
# The one name given to the recording itself, which is the answer
# "one person" -- the answer that hides the voices again.
ALONE = "Ida"


# ---------------------------------------------------------- the child
def look(case, media):
    """One window, one project: report what the voice rows do."""
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    os.environ.setdefault("VPM_SILENT", "1")
    os.environ.setdefault("VPM_NO_UPDATE_CHECK", "1")
    # The suite switches the separation off so that no test fetches the
    # model or computes for minutes. This test needs the way from a
    # stored result to the screen, and nothing is measured again for a
    # result that is stored -- so it is switched back on here, the two
    # projects below leave it nothing to do, and every way to it is
    # counted rather than assumed shut.
    os.environ.pop("VPM_NO_SPEAKER_SPLIT", None)
    import importlib.util
    from PySide6 import QtCore, QtWidgets
    from PySide6.QtTest import QTest

    app = QtWidgets.QApplication(sys.argv[:1])
    spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
    vpm = importlib.util.module_from_spec(spec)
    sys.modules["vpm"] = vpm
    spec.loader.exec_module(vpm)
    # Every caption below is asked for through the catalogue, so the
    # language does not decide the outcome -- but it is settled all the
    # same, or a standalone run on a German machine would compare
    # English keys with a German window. The suite sets the same thing
    # in the environment; this says it once more where it is read.
    vpm.set_language("en")
    # Nothing may reach the network or the keychain: what is wanted is
    # the window, not a run.
    vpm.list_presets = lambda key: []
    vpm.load_api_key = lambda: ""
    vpm.update_offer = lambda *a, **k: None

    # Every attempt to take a recording apart, whichever of the three
    # doors it goes through: fetching the model, reading what an
    # earlier run left in the cache, and the separation itself. The
    # whole promise of this change is that showing stored voices costs
    # none of them, and a promise is worth what it is counted at -- so
    # they are counted here rather than switched off and taken on
    # trust. That the list stays empty is a check of its own below.
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

    vpm.speaker_split_setup = no_setup
    vpm.speaker_split_run = no_split
    vpm.speaker_cache_read = no_cache

    played = []
    real_players = vpm.make_player_widgets

    def player_widgets(*a):
        """The real player, with every load written down.

        Where the player is asked to play, and from which second, is
        the only thing "a click plays this voice" can be read off from
        the outside -- the playhead itself needs a file to be decoded
        first and would answer late.

        The seventh argument is the ffplay fallback, which opens a
        window of its own. Nothing here may put a window on the screen
        somebody is sitting in front of, so it is taken out on the way
        in.
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

        Everything the window has to say is collected in one dict and
        turned into a command line here, so this is where "it arrives
        at the run" can be read. Handing back no command line is the
        program's own way of saying "not this time": start() gives the
        temporary file back and returns.
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
    # to start while the tick says otherwise. That refusal would stop
    # the last check below before it began -- and one recording taken
    # apart into voices is the case the voice rows exist for anyway.
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
        # separates nothing by itself, which is what makes this case
        # safe to open at all.
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
    # Off the desktop on the way in. The offscreen platform keeps the
    # window out of the window server; this keeps it off the screen on
    # any platform, and the layout machinery still runs -- without that
    # every widget would sit at Qt's untouched 100 by 30 and selecting
    # a row by where it is would measure air.
    _show = QtWidgets.QWidget.show

    def offstage(self):
        self.setAttribute(QtCore.Qt.WA_DontShowOnScreen, True)
        _show(self)

    QtWidgets.QWidget.show = offstage
    QtWidgets.QDialog.show = offstage

    error = []

    def check(name, ok, extra=""):
        print("  %-56s %s %s" % (name, "ok" if ok else "FAIL", extra))
        if not ok:
            error.append(name)

    def win():
        for x in app.topLevelWidgets():
            if x.windowTitle().startswith("Video Podcast"):
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

        A field in a table cell is read out as its kind and nothing
        else -- "combo box", "edit field" -- so the program says the
        column and the row in the accessible name, "belongs to --
        Room.wav". The part behind the first dash is the row. That is
        true of a cell in a table and of a cell under a parent in a
        tree alike, which is why the rows are counted here and not out
        of rowCount().
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

        Recognised by what can be picked in it and not by which column
        it stands in: a camera, and the two answers that are not a
        camera.
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
        of the files is one of them. With the recordings that is the
        whole difference, and it holds whether the voices stand in a
        table of their own, as they once did, or under their recording
        in a tree. Ordered by where they are on the sheet, so that "the
        first row" means the first one somebody sees.
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
        tell voices apart at all -- a chooser with one entry to pick
        where it can, a plain field where it cannot -- so it is found
        by what it is for and read through text_of below.
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

        Letter by letter and not setText: the program tells typing
        from picking, and only the end of the typing counts as the
        answer "this recording is one person". Return is what ends it,
        the same as clicking elsewhere.
        """
        inner = getattr(w, "lineEdit", None)
        inner = inner() if callable(inner) else w
        QTest.keyClicks(inner, text)
        QTest.keyClick(inner, QtCore.Qt.Key_Return)
        app.processEvents()

    def pick_several(w):
        """Pick the one entry the name field offers: several speakers.

        With the keyboard, because that is a pick like any other -- it
        goes through the same signal a click on the open list sends,
        and it needs no popup window on a machine that has no screen.
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

        Which view carries it is asked of the widget rather than known
        in advance, and which row it is of the view is asked of the
        view -- a table answers that and so does a tree.
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
    # "Separated: " in whatever language the window is speaking, so a
    # run outside the suite reads the same as one inside it.
    separated = vpm.TN(1, 'Separated: %d speaker',
                       'Separated: %d speakers').split("%d")[0]
    # The words every offer in the Speakers cell begins with, in
    # whatever language: "Only one speaker -- ...". What follows the
    # dash depends on what that recording already carries, and is
    # written down where it is checked.
    one_speaker = vpm.T(
        'Only one speaker -- separate the track?').split(" -- ")[0]
    several = vpm.label_of(vpm.SEVERAL_SPEAKERS)
    picks = [os.path.basename(video), vpm.MIX_ONLY,
             os.path.basename(video)]

    def offers():
        """The offers standing open in the window, in their own words."""
        return [b for b in win().findChildren(QtWidgets.QPushButton)
                if b.isVisible() and b.text().startswith(one_speaker)]

    def said_by(offer_list):
        return str([b.text() for b in offer_list])

    # ------------------------------------------------------ the steps
    # One thing at a time, each a moment of its own: answering rebuilds
    # the whole sheet, and a check that reads the sheet in the same
    # breath as the answer reads the sheet that is about to go.
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

        The sheet is built out of a thread and a fixed pause would be
        wrong on both sides. The voices are built in the same breath as
        the recordings, so once that row is there the voice rows are
        there too -- or they are not, and that is the answer.
        """
        sheet = sheet_of(vpm.T('Assignment && time window')[:8])
        there = sheet is not None and room in rows_named(sheet)
        if not there and waited[0] < 120:
            waited[0] += 1
            return AGAIN
        check("the project brought its assignment sheet up", there)
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
        # Asked of the model rather than of the widgets: whether the
        # voices are on the screen is one question, and whether the
        # tree carries them under their recording is another.
        check("and the tree hangs nothing under the recording",
              under(tree(), row_of(tree(), room)) == [],
              str(under(tree(), row_of(tree(), room))))
        check("and the columns are the ones the sheet promises",
              vpm.T('Speaker name') in headings_of(tree())
              and vpm.T('Speakers') in headings_of(tree()),
              str(headings_of(tree())))
        # What was measured is kept and shown: the silence is about
        # the answer, not about the measurement.
        mark = vpm.TN(len(FOUND), 'Separated: %d speaker',
                      'Separated: %d speakers') % len(FOUND)
        check("the row says all the same what was separated",
              bool(labels(mark)),
              str([x.text() for x in labels(separated)]))
        check("and nothing offers to correct an answer nobody gave",
              not offers(), said_by(offers()))
        check("and nothing has been separated", not separations,
              str(separations))

    def say_several():
        pick_several(name_field_of(sheet(), room))

    def voices_look():
        """Three voices asked for: three rows, and what each one can do."""
        rows = voice_rows(sheet(), file_names)
        check("a row for every voice the separation found",
              len(rows) == len(FOUND), "%d rows" % len(rows))
        # The core of the change: what was measured once is shown
        # again for nothing. Counted, not assumed -- every way into a
        # separation is stubbed and writes itself down.
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
        check("every row has a field to put a name in",
              all(any(isinstance(w, QtWidgets.QLineEdit)
                      for w in widgets)
                  for _t, _s, widgets, _b in rows))
        check("and a chooser offering the camera itself",
              all(box.findData(os.path.basename(video)) >= 0
                  for _t, _s, _w, box in rows))
        # Every voice is asked for in turn, and the answer has to be
        # that voice's longest passage. The three do not overlap, so a
        # position says which voice was meant -- and the first row
        # having to answer with the longest-speaking voice is what says
        # the rows stand in the order of how much each is heard.
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
              bool(labels(vpm.TN(len(FOUND), 'Separated: %d speaker',
                                 'Separated: %d speakers') % len(FOUND))),
              str([x.text() for x in labels(separated)]))
        check("and nothing is being computed",
              not any(b.isVisible()
                      for b in buttons(vpm.T('Break off'))))

    def say_one_name():
        type_into(name_field_of(sheet(), room), ALONE)

    def alone_look():
        """One name given instead: the rows go, the answer stays."""
        rows = voice_rows(sheet(), file_names)
        check("one name given, and the voice rows are gone", not rows,
              str([r[1] for r in rows]))
        # Answering rebuilds the whole sheet, the field being typed in
        # included. That the name is still there afterwards is not a
        # given: it lived in the widget that was thrown away.
        check("the name survives the rebuild the answer causes",
              text_of(name_field_of(sheet(), room)) == ALONE,
              repr(text_of(name_field_of(sheet(), room))))
        check("and the tree hangs nothing under the recording again",
              under(tree(), row_of(tree(), room)) == [],
              str(under(tree(), row_of(tree(), room))))
        check("and saying one name separated nothing", not separations,
              str(separations))
        # The way back, in the cell that already says how the
        # separation stands. Its exact words are printed beside the
        # check: what they may say depends on what the recording
        # carries, and both forms begin here.
        check("the row offers the way back to several speakers",
              len(offers()) == 1, said_by(offers()))
        if offers():
            offers()[0].click()
            app.processEvents()

    def again_look():
        """The offer taken: the same three voices, as they were left."""
        rows = voice_rows(sheet(), file_names)
        check("the offer brings the three voices back",
              len(rows) == len(FOUND), "%d rows" % len(rows))
        check("and brought them back without separating anything",
              not separations, str(separations))
        check("and the field says several speakers again",
              text_of(name_field_of(sheet(), room)) == several,
              repr(text_of(name_field_of(sheet(), room))))
        if len(rows) != len(FOUND):
            return STOP
        # What was typed into a row that has since been thrown away
        # and built again. The names live on the voice, not on the
        # widget, or three minutes of naming would go with one
        # mis-click.
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
            # Read from both lists on purpose: which of them carries a
            # voice is a question of how the sheet is built, and the
            # run is told the same thing either way.
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
        check("the recording is a row all the same",
              room in rows_named(sheet()))
        check("and its name field is empty",
              text_of(name_field_of(sheet(), room)) == "",
              repr(text_of(name_field_of(sheet(), room))))
        check("and the tree hangs nothing under it",
              under(tree(), row_of(tree(), room)) == [],
              str(under(tree(), row_of(tree(), room))))
        check("and nothing says a separation was found",
              not labels(separated), str([x.text() for x
                                          in labels(separated)]))
        check("and nothing offers to correct an answer nobody gave",
              not offers(), said_by(offers()))
        check("and nothing is being computed",
              not any(b.isVisible()
                      for b in buttons(vpm.T('Break off'))))
        check("and nothing has been separated", not separations,
              str(separations))

    def name_it():
        type_into(name_field_of(sheet(), room), ALONE)

    def asked_look():
        """A name given where nothing was ever listened to.

        The offer here is the other one: there is nothing stored to
        show, so it offers to go and look. It is not clicked -- that
        would fetch 218 MB and compute for minutes -- so what is
        checked is that it stands there, says so, and has started
        nothing by standing there.
        """
        check("the name given is what the field says",
              text_of(name_field_of(sheet(), room)) == ALONE,
              repr(text_of(name_field_of(sheet(), room))))
        check("and now the row offers to go and look",
              len(offers()) == 1
              and offers()[0].text() == vpm.T(
                  'Only one speaker -- separate the track?'),
              said_by(offers()))
        check("and no voice rows came of a name",
              not voice_rows(sheet(), file_names))
        check("and the offer alone separated nothing", not separations,
              str(separations))

    plan = ([open_project, wait_for_sheet, unanswered_look, say_several,
             voices_look, say_one_name, alone_look, again_look, dry_run]
            if case == "found" else
            [open_project, wait_for_sheet, empty_look, name_it,
             asked_look])

    def stop_now():
        print("\n%s" % ("ALL OK" if not error
                        else "FAIL: " + ", ".join(error)))
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
            error.append("crash")
            stop_now()
            return
        if answer == STOP:
            stop_now()
            return
        if answer != AGAIN:
            plan.pop(0)
        QtCore.QTimer.singleShot(250 if answer == AGAIN else 400, step)

    QtCore.QTimer.singleShot(300, step)
    # A window that never gets there must not hold the suite -- there
    # is no timeout(1) on this machine -- and must not pass either.
    QtCore.QTimer.singleShot(150000, app.quit)
    vpm.gui()
    if not done[0]:
        print("  the window never got as far as the checks   FAIL")
        error.append("no answer")
    return 1 if error else 0


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
# process would be a second interface standing on the first, and the
# question here is what a whole window makes of a whole project.
media = tempfile.mkdtemp(prefix="vpm_voices_")
material(media)
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
    if child.returncode != 0:
        bad.append(name)

print()
if bad:
    print("FAIL: " + ", ".join(bad))
    sys.exit(1)
print("All good.")
