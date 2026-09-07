# -*- coding: utf-8 -*-
"""The fittings a window is put together out of.

A piece read out of the folder beside the way in by beside(). It
cannot import the file it was cut out of -- that file is still being
read -- so the program is handed in and every name is bound below.
What the window still calls out of it, it binds there in turn.
"""

# beside() puts the program here before this file is read.
PROGRAM = PROGRAM

# What this piece uses out of the program. LANG is left out -- the
# window sets it while it runs and a copy would part from it at the
# first assignment -- so it stays PROGRAM.LANG where it is read.
COLOURS = PROGRAM.COLOURS
CUT_CHOICES = PROGRAM.CUT_CHOICES
CUT_FIELDS = PROGRAM.CUT_FIELDS
IGNORE_AUDIO = PROGRAM.IGNORE_AUDIO
NAME_ROOM = PROGRAM.NAME_ROOM
ROW_ROOM = PROGRAM.ROW_ROOM
RUN_STOP = PROGRAM.RUN_STOP
SEVERAL_SPEAKERS = PROGRAM.SEVERAL_SPEAKERS
SHOT_NAMES = PROGRAM.SHOT_NAMES
T = PROGRAM.T
TN = PROGRAM.TN
Value = PROGRAM.Value
fill_choices = PROGRAM.fill_choices
label_of = PROGRAM.label_of
os = PROGRAM.os
run_stages = PROGRAM.run_stages
sys = PROGRAM.sys
time = PROGRAM.time

# Three widths come out of the player and not out of the way in.
# beside() lays its path against the folder the program starts in, so
# this is the piece the window read and not a second copy of it.
beside = PROGRAM.beside
player = beside("player", program=PROGRAM)
caption_room = player.caption_room
cut_caption_room = player.cut_caption_room
cut_choice_room = player.cut_choice_room

# fitted and widget_width stay in the window: this file is read while
# the window still is, so a copy of either would be an AttributeError.
# They are read as PROGRAM.<name> at the one place each is used.


# None of these reaches into gui(), so they stand out here where a test
# can call them directly rather than cutting them out of the source.

def zoom_button(QtWidgets, text, tip, does):
    """One of the small buttons that zoom the band."""
    b = QtWidgets.QToolButton()
    b.setText(text)
    b.setAutoRaise(True)
    b.setFixedWidth(caption_room(b, 24))
    hint(b, tip)
    b.clicked.connect(does)
    return b


def hint(widget, text):
    widget.setToolTip(text)
    return widget

def speaks_as(widget, what, row_name=""):
    """Give a field a name a screen reader can say.

    A field in a table cell is read out as its kind and nothing else --
    "combo box", "edit field". Which column and row it sits in is on
    the screen only, so it is said here too.
    """
    widget.setAccessibleName("%s -- %s" % (what, row_name)
                             if row_name else what)
    return widget

# How narrow the name field may get. It is typed into, so it is the one
# column that must not give way: Qt lets a stretching column fall to
# 16 px in silence, and on the Windows builder this one went to 79 px.
NAME_COLUMN_LEAST = 160


def split_column_room(widget):
    """How wide the Speakers column has to be for what it will hold.

    Not for what stands in it: it is filled minutes later, when a
    separation reports, and a column that measures its contents
    measured an empty one. Measured in the font that draws, over the
    two captions that must not wrap.
    """
    from PySide6 import QtWidgets as _qw
    mark = _qw.QLabel("")
    mark.setFont(widget.font())
    button = _qw.QPushButton(T('Stop'))
    button.setFont(widget.font())
    running = caption_room(mark, 0, [T('Separating ...'),
                                     T('Stopping ...')])
    done = caption_room(mark, 0, [TN(2, 'Separated: %s speaker',
                                     'Separated: %s speakers') % 2])
    return max(running + button.sizeHint().width() + 6, done) + 12


def split_column_fit(tree, column, stretch=1, least=NAME_COLUMN_LEAST):
    """Give the Speakers column its width, and the rest to the names.

    Out of the window, so it cannot drift from what is drawn. What is
    left over is handed out here rather than by a stretching column,
    and never below *least*: a stretching one falls as far as Qt likes,
    79 px on the Windows builder. Then the tree scrolls instead.
    """
    from PySide6 import QtCore as _qc
    from PySide6 import QtWidgets as _qw
    head = tree.header()
    head.setStretchLastSection(False)
    head.setSectionResizeMode(stretch, _qw.QHeaderView.Interactive)
    tree.setColumnWidth(column, split_column_room(tree))
    others = [c for c in range(head.count()) if c != stretch]
    # What the column was asked for before the room was shared out: the
    # leftover can be nothing, and nothing is a field with no name.
    asked = max(least, tree.columnWidth(stretch))

    def share_out():
        free = tree.viewport().width() - sum(tree.columnWidth(c)
                                             for c in others)
        tree.setColumnWidth(stretch, max(asked, free))

    tree._share_out = share_out

    class ShareWithWindow(_qc.QObject):
        """Hand the name column the room left over as the window moves."""

        def eventFilter(self, watched, what):
            if what.type() == _qc.QEvent.Resize:
                tree._share_out()
            return False

    if not hasattr(tree, "_share"):
        tree._share = ShareWithWindow(tree)
        tree.viewport().installEventFilter(tree._share)
    share_out()
    return tree.columnWidth(column)


def cells_laid_out(cells):
    """Give every cell the height its text needs, and lay the rows out.

    A wrapping label offers a height worked out at a width of its own
    choosing, and on the Windows builder that offer is 14 px short. So
    the width is read off the laid-out label and the height demanded
    from it, twice round: the first pass gives the label its width.
    """
    view = cells_are_shown_in(cells)
    if view is None:
        return False
    view.doItemsLayout()
    moved = False
    for _path, _button, mark, _item in list(cells or ()):
        # Let go of last time's height before asking again: a label
        # counts its own minimum into the answer, so an emptied cell
        # would still say it needs four lines.
        was = mark.minimumHeight()
        mark.setMinimumHeight(0)
        needs = max(0, mark.heightForWidth(max(1, mark.width())))
        if needs:
            mark.setMinimumHeight(needs)
        moved = moved or needs != was
    if moved:
        view.doItemsLayout()
    return True


def cells_are_shown_in(cells):
    """The view those cells stand in, or None where there is not one.

    tree_build makes the view the model's parent, so any one item knows
    where it is drawn.
    """
    for _path, _button, _mark, item in list(cells or ()):
        model = item.model()
        view = model.parent() if model is not None else None
        if hasattr(view, "doItemsLayout"):
            return view
    return None


def split_cell_build(path, on_stop, item):
    """The Speakers cell of one recording: its state, and a way out.

    Nothing here starts a separation -- that is answered in the name
    field of the same row -- so the cell only says what came of it and
    carries the button that breaks a running one off. Returns the cell,
    and the button, label and item to be reached again while it runs.
    """
    from PySide6 import QtWidgets as _qw
    box = _qw.QWidget()
    row = _qw.QHBoxLayout(box)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(6)
    button = _qw.QPushButton(T('Stop'))
    speaks_as(button, T('Stop'), os.path.basename(path))
    button.clicked.connect(lambda *_, x=path: on_stop(x))
    button.setVisible(False)
    mark = label("", COLOURS["quiet"])
    # Word wrap, because the cell is written to again after the column
    # was measured: a reason the separation could not run is hundreds
    # of pixels wide, and two lines beat a cut one.
    mark.setWordWrap(True)
    row.addWidget(mark, 1)
    row.addWidget(button)
    return box, (path, button, mark, item)


def typed_part(new, old):
    """What somebody typed, out of a caption they typed into.

    A combo box showing a picked entry does not replace its caption when
    the next letter arrives, it edits it: "A" typed into "several
    speakers" after "sev" leaves "sevAeral speakers". The caption comes
    back out by the head and tail the two strings still share.
    """
    head = 0
    while head < len(new) and head < len(old) and new[head] == old[head]:
        head += 1
    tail = 0
    while (tail < len(new) - head and tail < len(old) - head
           and new[-1 - tail] == old[-1 - tail]):
        tail += 1
    return new[head:len(new) - tail]


def speaker_name_cell(name_value, several_value, short):
    """The name field of one recording: a name, or "several speakers".

    One question -- who is to be heard here? -- with three answers
    rather than a field beside a button. Picking a name again costs
    nothing: the voices are hidden, not thrown away. What the file name
    suggests stands in the empty field in grey and is never written in,
    or "Zoom0004" would go into the mix as a speaker name.
    """
    from PySide6 import QtWidgets as _qw
    from PySide6.QtCore import Qt as _qt
    box = _qw.QComboBox()
    box.setEditable(True)
    box.setInsertPolicy(_qw.QComboBox.NoInsert)
    box.addItem(label_of(SEVERAL_SPEAKERS), SEVERAL_SPEAKERS)
    # On the entry itself, not only on the field: the field's own hint
    # is gone the moment the list is open, which is when it is decided.
    box.setItemData(0, T('Separates the recording by voice: every voice '
                         'gets a row of its own, and its camera in it. '
                         'About one minute for half an hour of audio, on '
                         'this machine and without an upload.'),
                    _qt.ToolTipRole)
    box.lineEdit().setPlaceholderText(
        str(getattr(name_value, "suggested", "")))
    speaks_as(box, T('Speaker name'), short)
    hint(box, T('Who is to be heard on this recording. A name means it '
                'is that one person.\n"several speakers" works out who '
                'speaks when, on this machine and without an upload -- '
                'about one minute for half an hour of audio. The names '
                'then go in the rows underneath.'))
    # True from the first letter until the typing is over. Answering
    # "one name, not several" rebuilds the whole sheet, and per
    # keystroke that destroys this very widget after the first letter.
    typing = [False]

    def show_now():
        # Not while somebody is typing. Every letter reaches name_value,
        # which calls this, which would write the value back over the
        # word being written.
        if typing[0]:
            return
        if several_value.get():
            box.setCurrentIndex(0)
        else:
            box.setCurrentIndex(-1)
            box.setEditText(str(name_value.typed()))

    def picked(_i=0):
        # Picked from the list, so the typing is over with the click:
        # the rows underneath should appear on the click itself.
        typing[0] = False
        several_value.set(box.currentData() == SEVERAL_SPEAKERS)

    def typed(text):
        # textEdited and not textChanged: the second fires when the
        # picked entry writes its caption in, and undoes the answer.
        if not typing[0] and several_value.get():
            # The first letter on a field that was showing "several
            # speakers". Qt edited that caption rather than replacing
            # it, so it comes back out and only the typing stays.
            typing[0] = True
            text = typed_part(text, label_of(SEVERAL_SPEAKERS))
            box.setEditText(text)
        typing[0] = True
        name_value.set(text)

    def settled():
        """The typing is over: only now is the answer given."""
        if not typing[0]:
            return
        typing[0] = False
        several_value.set(False)
        show_now()

    show_now()
    box.activated.connect(picked)
    box.lineEdit().textEdited.connect(typed)
    box.lineEdit().editingFinished.connect(settled)
    name_value.listen(show_now)
    several_value.listen(show_now)
    return box


def voice_row_cells(name_value, camera_value, targets, caption):
    """One voice's two fields: what it is called and where it goes.

    The row stands under the recording it was heard in, so it repeats
    neither the file name nor the two times -- neither belongs on
    screen. The longest passage is still worked out, because it is
    where a click on the row takes the player. Returns (name field,
    camera chooser).
    """
    from PySide6 import QtWidgets as _qw
    field = field_bind(_qw.QLineEdit(), name_value)
    speaks_as(field, T('Speaker name'), caption)
    box = _qw.QComboBox()
    speaks_as(box, T('belongs to'), caption)
    fill_choices(box, targets, camera_value.get())
    box.currentIndexChanged.connect(
        lambda *_: camera_value.set(box.currentData()))

    def name_useful():
        """Grey the name out where it cannot do anything.

        A voice set to "do not use" is out of the mix and out of the
        transcript, so a name for it has no effect. Greyed, not
        emptied: switching back must not cost the typing. Only "do not
        use" -- with "no camera of its own" the name still works. The
        row stays selectable, which is what plays the voice.
        """
        field.setEnabled(camera_value.get() != IGNORE_AUDIO)

    camera_value.listen(name_useful)
    name_useful()
    # So that nothing has to tell a voice from its recording by the
    # wording of a caption: the field itself says which level it is on.
    for w in (field, box):
        w.setObjectName("voice")
    return field, box


def more_speakers_row(audio_file_list, on_pick):
    """The row that asks for one speaker more than was found.

    Every recording can be listened to again: whoever hears a fourth
    person knows it before the program does. From three recordings on a
    button each pushed the player over the edge of the window, so with
    more than one the name moves into a chooser beside the button.
    """
    from PySide6 import QtWidgets as _qw
    if not audio_file_list:
        return None
    more = _qw.QWidget()
    more_row = _qw.QHBoxLayout(more)
    more_row.setContentsMargins(0, 0, 0, 0)
    if len(audio_file_list) == 1:
        only = audio_file_list[0]
        button = _qw.QPushButton()
        # The whole name first, at the ordinary size: only if that is
        # too wide does the type get smaller, and only then is the name
        # shortened, in the font the button really draws with.
        button.setText(T('One more speaker in %s') % os.path.basename(only))
        font_smaller_if_wide(button, 2, ROW_ROOM)
        if button.sizeHint().width() > ROW_ROOM:
            button.setText(T('One more speaker in %s')
                           % short_name(button, os.path.basename(only),
                                        NAME_ROOM))
        button.clicked.connect(lambda *_, x=only: on_pick(x))
        more_row.addWidget(button)
    else:
        which = _qw.QComboBox()
        for path in audio_file_list:
            which.addItem(os.path.basename(path), path)
        which.setSizeAdjustPolicy(_qw.QComboBox.AdjustToContents)
        button = _qw.QPushButton(T('One more speaker in'))
        # Button and chooser fit as a pair, and shrink as a pair or
        # not at all -- two sizes side by side look like a mistake.
        if (button.sizeHint().width()
                + min(which.sizeHint().width(), NAME_ROOM) > ROW_ROOM):
            font_smaller(button, 2)
            font_smaller(which, 2)
        # The width comes after the type is settled, in the font the box
        # really draws with, and from the names rather than a count of
        # characters: 27 letters want 288 px and the box can give 216.
        box_names_fit(which, NAME_ROOM)
        button.clicked.connect(lambda *_, b=which: on_pick(b.currentData()))
        more_row.addWidget(button)
        more_row.addWidget(which)
    hint(button, T('Listens to that recording again, looking for one '
                   'speaker more than was found.'))
    more_row.addStretch(1)
    return more


QT_WORDS = []   # Qt's own translator, kept alive for as long as the window is


def mac_menu_name(name):
    """Put the program's name in the macOS menu bar; report whether it took.

    The first menu on a Mac carries CFBundleName out of the bundle
    around the executable, and a script started with python3 has no
    bundle of its own, so it borrows Python's and the entry reads
    "Python". setApplicationName does not reach it; only the bundle
    does, and it has to be written before the application is built.
    """
    if sys.platform != "darwin":
        return False
    try:
        import ctypes, ctypes.util
        objc = ctypes.cdll.LoadLibrary(ctypes.util.find_library("objc"))
        objc.objc_getClass.restype = ctypes.c_void_p
        objc.sel_registerName.restype = ctypes.c_void_p

        def send(obj, what, *args, types=()):
            call = ctypes.cast(objc.objc_msgSend, ctypes.CFUNCTYPE(
                ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, *types))
            return call(obj, objc.sel_registerName(what.encode()), *args)

        strings = ctypes.c_void_p(objc.objc_getClass(b"NSString"))

        def text_of(value):
            return ctypes.c_void_p(send(strings, "stringWithUTF8String:",
                                        value.encode(),
                                        types=(ctypes.c_char_p,)))

        bundle = ctypes.c_void_p(objc.objc_getClass(b"NSBundle"))
        info = ctypes.c_void_p(send(ctypes.c_void_p(
            send(bundle, "mainBundle")), "infoDictionary"))
        send(info, "setObject:forKey:", text_of(name),
             text_of("CFBundleName"),
             types=(ctypes.c_void_p, ctypes.c_void_p))
        return True
    except Exception:
        # An older macOS, a bundled build that carries its own name, or
        # a runtime that will not be talked to. The menu is unchanged.
        return False


def total_paint(Qt, plan, total_state, total_bar, total_line):
    """Draw the whole run's progress bar, or take it away when it is over.

    Outside gui() because it reaches into nothing of its own: plan and
    widgets come in as arguments.
    """
    if plan.busy():
        total_state["full_since"] = 0.0
        plan.creep(0.2)
        total_bar.setValue(int(round(1000 * plan.total())))
        PROGRAM.fitted(Qt, total_line, plan.line())
        total_bar.show()
        total_line.show()
        return
    if not plan.order:
        return
    # Finished: full for a moment, so the end is seen, then away.
    total_bar.setValue(1000)
    total_line.setText(T('done'))
    if not total_state["full_since"]:
        total_state["full_since"] = time.time()
    elif time.time() - total_state["full_since"] > 1.5:
        plan.clear()
        total_bar.hide()
        total_line.hide()


def total_hide(plan, total_state, total_bar, total_line):
    """Take the bar away: what it was counting is not being done.

    Clearing the plan is not enough: the widget goes on showing the
    figure it was last given until the timer draws again, and
    total_paint only hides it after a step has finished -- which is
    what does not happen when work is called off.
    """
    plan.clear()
    total_state["full_since"] = 0.0
    total_bar.setValue(0)
    total_line.setText("")
    total_bar.hide()
    total_line.hide()


def measuring_stop(state, paths, prework_clean_up, split_stop, split_run,
                   hide_bar):
    """Call off everything measuring a list that is about to go.

    Four strands go on reading the files otherwise, and their answers
    arrive in a window that has nothing to do with them. Each carries
    its own way of being called off; this is the one place that uses
    all of them. The prework goes first, and the bar is wiped after.
    """
    prework_clean_up(paths)
    for counted in ("preflight_run", "axis_run", "speakers_run"):
        state[counted] = state.get(counted, 0) + 1
    state["axis_running"] = False
    split_stop()
    split_run["busy"] = False
    # What split_stop wrote into the row goes with it: "Stopping ..."
    # must not be the last word on a production no longer open.
    state["split_note"] = None
    state["speakers_running"] = ""
    hide_bar()


def qt_own_words(QtCore, app):
    """Give Qt its own texts in the chosen language.

    "Preferences", "Quit", "Services" and the file dialog's buttons are
    Qt's words, not ours, and stay English otherwise. Kept in a list
    afterwards: Qt holds no reference, so a translator that goes out of
    scope changes nothing.
    """
    words = QtCore.QTranslator()
    if words.load("qtbase_" + PROGRAM.LANG, QtCore.QLibraryInfo.path(
            QtCore.QLibraryInfo.LibraryPath.TranslationsPath)):
        app.installTranslator(words)
        QT_WORDS.append(words)
        return True
    return False


def say_dialog(QtWidgets, window, title, text, do_text="", no_text=""):
    """One message box, with one button or with two.

    With do_text it is a question and gives back whether the action was
    chosen; without it, a message. The buttons carry the action rather
    than yes and no, so nobody has to read the question backwards.
    """
    d = QtWidgets.QDialog(window)
    d.setWindowTitle(title)
    d.setMinimumWidth(720 if do_text else 620)
    position = QtWidgets.QVBoxLayout(d)
    position.setContentsMargins(18, 16, 18, 14)
    position.setSpacing(14)
    position.addWidget(label(title, COLOURS["heading"], True, 15))
    m = label(text)
    m.setWordWrap(True)
    m.setMinimumWidth(660 if do_text else 560)
    position.addWidget(m)
    bar = QtWidgets.QHBoxLayout()
    position.addLayout(bar)
    # Both buttons right, the action outermost and preselected.
    bar.addStretch(1)
    if do_text:
        no_button = QtWidgets.QPushButton(no_text)
        no_button.clicked.connect(d.reject)
        bar.addWidget(no_button)
    yes_button = QtWidgets.QPushButton(do_text or T('Close'))
    yes_button.clicked.connect(d.accept)
    yes_button.setDefault(True)
    yes_button.setAutoDefault(True)
    bar.addWidget(yes_button)
    return d.exec() == QtWidgets.QDialog.Accepted


def label(text, colour=None, bold=False, large=0):
    """A piece of text on the screen, in the colour it belongs in."""
    from PySide6 import QtWidgets as _qw
    widget = _qw.QLabel(text)
    style = []
    if colour:
        style.append("color: %s" % colour)
    if bold:
        style.append("font-weight: bold")
    if large:
        style.append("font-size: %dpx" % large)
    if style:
        widget.setStyleSheet(";".join(style))
    return widget

def font_smaller(widget, less=1):
    """Set a widget's font that many points below the application's.

    Through the font and not through a style sheet: a fixed size there
    ignores whatever the system font is set to.
    """
    from PySide6 import QtWidgets as _qw
    f = _qw.QApplication.font()
    if f.pointSizeF() > 0:
        f.setPointSizeF(max(6.0, f.pointSizeF() - less))
    else:
        f.setPixelSize(max(8, f.pixelSize() - less))
    widget.setFont(f)
    return widget

def font_smaller_if_wide(widget, less, room):
    """Shrink the type only where the widget is wider than *room*.

    Smaller type is a cost, not a free win: on a machine whose system
    font was turned up it undoes what somebody set it for. So it is
    taken where the row would otherwise push the sheet wider than the
    player leaves it, and nowhere else.
    """
    if widget.sizeHint().width() <= room:
        return widget
    return font_smaller(widget, less)

def short_name(widget, text, room):
    """Shorten a file name to the room there is, from the middle.

    Both ends of a file name carry what tells two of them apart -- the
    take at the front, the channel at the back -- so what goes is the
    middle. Measured in the font the widget actually draws with.
    """
    from PySide6 import QtCore as _qc
    return widget.fontMetrics().elidedText(text, _qc.Qt.ElideMiddle, room)

def box_names_fit(box, room):
    """Give a chooser of file names the width it needs, up to *room*.

    A chooser asks for as much as its widest entry needs and no more
    than *room*; what it cannot get, it takes off the name. Qt takes it
    off the end, and the recordings of one session differ at the end --
    cut there, three of them read alike. So every entry is shortened in
    the middle instead, and the whole name stays a tooltip.
    """
    from PySide6 import QtCore as _qc
    want = PROGRAM.widget_width(box)
    box.setMinimumWidth(min(want, room))
    box.setMaximumWidth(room)
    if want <= room:
        return box
    whole = [box.itemText(i) for i in range(box.count())]
    for i, name in enumerate(whole):
        # The arrow sits inside the box and takes room off the text;
        # the same allowance widget_width measures with.
        box.setItemText(i, short_name(box, name, room - 44))
        box.setItemData(i, name, _qc.Qt.ToolTipRole)

    def whole_name(*_):
        """Put the chosen name, unshortened, on the box."""
        i = box.currentIndex()
        box.setToolTip(whole[i] if 0 <= i < len(whole) else "")

    box.currentIndexChanged.connect(whole_name)
    whole_name()
    return box

def field_bind(field, value, width=None):
    """Bind an input field and a value so each follows the other.

    The field shows the answer and not the name behind it: a value that
    carries a suggestion offers it in grey, where it can be overruled.
    """
    field.setText(str(value.typed()))
    if getattr(value, "suggested", ""):
        field.setPlaceholderText(str(value.suggested))
    if width:
        field.setFixedWidth(width)
    field.textChanged.connect(lambda t: value.set(t))

    def follow_up():
        if field.text() != str(value.typed()):
            field.setText(str(value.typed()))

    value.listen(follow_up)
    return field

def choice_bind(box, value, allowed):
    """Bind a drop-down and a value; *allowed* are the stored names.

    The list shows the translated names, the value keeps the name the
    switch carries -- a German project has to read alike in English.
    """
    for name in allowed:
        box.addItem(T(SHOT_NAMES.get(name, name)), name)
    box.setCurrentIndex(max(0, list(allowed).index(value.get())
                            if value.get() in allowed else 0))
    box.currentIndexChanged.connect(
        lambda i: value.set(box.itemData(i)))

    def follow_up():
        if box.currentData() != value.get() and value.get() in allowed:
            box.setCurrentIndex(list(allowed).index(value.get()))

    value.listen(follow_up)
    return box

def cut_fields_build(into, parts=None):
    """Build the numbers and the choices of the cut box.

    Out here rather than inside the window, which is long enough
    without sixty lines of grid. Returns {command line name: Value}, in
    the order CUT_FIELDS and CUT_CHOICES stand in. *parts* is filled
    with {command line name: (row, field or box)} for whoever has to
    grey a setting out later, handed over rather than returned.
    """
    parts = {} if parts is None else parts
    from PySide6 import QtWidgets as _qw
    from PySide6.QtCore import Qt as _qt
    cut_var = {}
    field_grid = _qw.QGridLayout()
    into.addLayout(field_grid)
    # The rhythm first, the wide shot after it, the question last --
    # its seconds stand directly above "After a question". At half the
    # width the sliders no longer fit side by side.
    apart_ = ("wide", "reaction")
    ordered = ([f for f in CUT_FIELDS
                if not f[0].startswith(apart_)]
               + [f for f in CUT_FIELDS if f[0].startswith("wide")]
               + [f for f in CUT_FIELDS if f[0].startswith("reaction")])
    for idx, (api_key, caption, default_value, unit, short,
              long) in enumerate(ordered):
        line = _qw.QWidget()
        row_layout = _qw.QHBoxLayout(line)
        row_layout.setContentsMargins(0, 0, 18, 0)
        m = label(T(caption))
        m.setFixedWidth(cut_caption_room(m, 140))
        row_layout.addWidget(m)
        value = Value(default_value)
        cut_var[api_key] = value
        field = field_bind(_qw.QLineEdit(), value, 56)
        field.setAlignment(_qt.AlignRight)
        # The caption stands left of the field and the unit right of
        # it; neither is read out with the field, so both are said here.
        speaks_as(field, T('%s, seconds') % T(caption)
                  if unit == "s" else T(caption))
        row_layout.addWidget(field)
        t = label("%s  %s" % (unit, T(short)), COLOURS["quiet"])
        row_layout.addWidget(t)
        row_layout.addStretch(1)
        for _w in (line, m, field, t):
            hint(_w, T(long))
        field_grid.addWidget(line, idx, 0)
        parts[api_key] = (line, field)
    # Below the numbers: the cases where the speech does not say who
    # belongs on screen. Here and not in the settings window because
    # they change the cut, and the cut is what this tab is about.
    choice_grid = _qw.QGridLayout()
    into.addLayout(choice_grid)
    for idx, (api_key, caption, default_value, allowed, short,
              long) in enumerate(CUT_CHOICES):
        line = _qw.QWidget()
        row_layout = _qw.QHBoxLayout(line)
        row_layout.setContentsMargins(0, 0, 18, 0)
        m = label(T(caption))
        m.setFixedWidth(cut_caption_room(m, 140))
        row_layout.addWidget(m)
        value = Value(default_value)
        cut_var[api_key] = value
        box = choice_bind(_qw.QComboBox(), value, allowed)
        box.setFixedWidth(cut_choice_room(box, 150))
        speaks_as(box, T(caption))
        row_layout.addWidget(box)
        t = label(T(short), COLOURS["quiet"])
        row_layout.addWidget(t)
        row_layout.addStretch(1)
        for _w in (line, m, box, t):
            hint(_w, T(long))
        choice_grid.addWidget(line, idx, 0)
        parts[api_key] = (line, box)
    return cut_var


def checkbox_bind(checkbox, value):
    checkbox.setChecked(bool(value.get()))
    checkbox.toggled.connect(lambda b: value.set(bool(b)))
    value.listen(lambda: checkbox.setChecked(bool(value.get()))
                 if checkbox.isChecked() != bool(value.get()) else None)
    return checkbox

def _list_accepts(e):
    if e.mimeData().hasUrls():
        e.acceptProposedAction()

def mark_red(widget, on, reason=""):
    """Mark an entry as faulty in place.

    A dialog at startup comes too late: by then the row is out of sight.
    Red in the row shows which one is meant, the hint says why.
    """
    if widget is None:
        return
    try:
        widget.setStyleSheet(
            "border: 1px solid %s; border-radius: 3px;" % COLOURS["error"]
            if on else "")
        widget.setToolTip(reason if on else "")
    except RuntimeError:
        pass


def stop_asked_for(where=""):
    """Ask the run to stop, and end what it has running at this moment."""
    RUN_STOP["wanted"] = True
    RUN_STOP["at"] = where
    for child in list(RUN_STOP["children"]):
        try:
            child.terminate()
        except Exception:
            # It ended by itself between the two lines. Nothing to do.
            pass

def break_off_button(QtWidgets, state, say):
    """The button that stops a run, and what it says while it does.

    Away while nothing runs: a button that does nothing is a question
    nobody asked. It can be pressed at any moment, but the run stops only
    where nothing is left half written, so between the press and the end
    there is a wait -- said out loud, or the button looks broken.
    """
    button = QtWidgets.QPushButton(T('Stop'))
    button.setVisible(False)

    def pressed():
        if not state.get("running"):
            return
        button.setEnabled(False)
        button.setText(T('Stopping ...'))
        say(T('\nStopping. The run ends as soon as it can do so '
              'without leaving a file half written -- one moment.\n'))
        stop_asked_for(state.get("run_step") or "")

    button.clicked.connect(pressed)
    return button

def button_in_a_frame(QtWidgets, button):
    """Wrap a button in a bare frame, and hand the frame back.

    A disabled button takes no mouse events in Qt and so shows no
    tooltip; the frame takes them and carries a copy of its text. And a
    button wants a fixed height where a plain widget wants a preferred
    one, so on an odd difference a bare button rounds apart.
    """
    frame = QtWidgets.QWidget()
    row = QtWidgets.QHBoxLayout(frame)
    row.setContentsMargins(0, 0, 0, 0)
    row.addWidget(button)
    if button.toolTip():
        frame.setToolTip(button.toolTip())
    return frame

def row_same_height(buttons):
    """Give a row of buttons the height of the tallest among them.

    A flat button asks for less room than a framed one: Start stands 29
    pixels high where "Settings ..." stands 25, so it lines up with
    neither edge. No fixed number -- that is the system font talking, and
    the wish stands whether the button is on screen or not.
    """
    tallest = max([b.sizeHint().height() for b in buttons] or [0])
    for b in buttons:
        b.setMinimumHeight(tallest)
    return tallest

def make_footer(Qt, QtCore, QtWidgets, window, vertical, state, files,
                plan, bridge, late, multitrack, without_auphonic,
                settings_open):
    """The bottom row of the window: the one bar, and the four buttons.

    One strip answered end to end -- the bar, the plan behind it that
    says what each stage is worth, and the four buttons. The break-off
    reaches back through state["write"]: the writer is made in the
    window. Qt comes in as a parameter.
    """
    # Above the buttons, not under them: a line below the bottom row
    # reads like a footnote, not the answer to "why can I not press it".
    start_note = label("", COLOURS["quiet"])
    vertical.addWidget(start_note)
    foot = QtWidgets.QHBoxLayout()
    vertical.addLayout(foot)
    total_bar = QtWidgets.QProgressBar()
    total_bar.setRange(0, 1000)
    total_bar.setTextVisible(False)
    total_bar.setFixedHeight(12)
    # Wide enough to read a share off it, and growing with the window
    # rather than fixed: the stretch behind it takes every spare pixel.
    # The maximum keeps it from pushing the grey-Start reason off screen.
    total_bar.setMinimumWidth(220)
    total_bar.setMaximumWidth(620)
    hint(total_bar, T('Everything still outstanding, measured against '
                      'what is done. Long pieces of work take up more of '
                      'the bar than short ones.'))
    total_line = label("", COLOURS["quiet"])
    foot.addWidget(total_bar, 3)
    foot.addWidget(total_line, 1)
    total_bar.hide()
    total_line.hide()
    total_state = {"full_since": 0.0}

    run_step_order = []

    def plan_wipe():
        total_hide(plan, total_state, total_bar, total_line)

    def run_plan_build():
        """Announce the stages of the run before it starts.

        The whole job at once, not stage by stage: a bar that learns of
        the next stage only when the last ends jumps backwards at every
        boundary. The plan before it is thrown away, finished or not --
        added to, the bar stands still, because it never falls back.
        """
        plan_wipe()
        cameras = len([1 for p, a in files if a == "video"])
        stages = run_stages(bool(multitrack.get()), cameras,
                            not without_auphonic(),
                            speakers=bool(multitrack.get()
                                          or state.get("speakers_local")))
        run_step_order[:] = [name for name, _w, _c in stages]
        for name, weight, caption in stages:
            plan.add("run:" + name, weight, caption)

    def run_step_take(name, share):
        """One stage of the run reports. Runs in the window thread.

        A stage beginning means every earlier one is over, whether it ran
        or was skipped -- a step left at nothing holds the bar back.
        """
        if name not in run_step_order:
            # No caption: the key is an internal English word, and a
            # step with none says nothing rather than showing it.
            plan.add("run:" + name, 1.0)
            run_step_order.append(name)
        if share < 0:
            for earlier in run_step_order[:run_step_order.index(name)]:
                plan.done("run:" + earlier)
            plan.begin("run:" + name)
            return
        plan.report("run:" + name, share)

    bridge.run_step.connect(run_step_take)

    def total_show():
        """Refresh the one bar. A timer calls this, not the work.

        The work reports from several threads at very different rates;
        redrawing on each report stutters or stands still for a minute.
        """
        try:
            total_paint(Qt, plan, total_state, total_bar, total_line)
        except RuntimeError:
            # The window is closing and the widgets are gone. A timer
            # firing into them must not become a traceback on the way out.
            total_clock.stop()

    total_clock = QtCore.QTimer(window)
    total_clock.timeout.connect(total_show)
    total_clock.start(200)
    foot.addStretch(1)
    # Only the Resolve part: after a run, or where a handover file is
    # already in the output folder. Then nothing has to be recomputed.
    start_run = QtWidgets.QPushButton(T('Start'))
    start_run.setEnabled(False)
    hint(start_run, T('Measure, align, process, write files.'))
    # Both run buttons sit in a frame of their own: it makes the tooltip
    # of a switched-off button reachable. button_in_a_frame says why.
    start_run_env_curve = button_in_a_frame(QtWidgets, start_run)
    foot.addWidget(start_run_env_curve)
    preview_button = QtWidgets.QPushButton(T('Dry run'))
    preview_button.setEnabled(False)
    hint(preview_button,
            T('Measure only -- nothing is written or uploaded.'))
    foot.addWidget(button_in_a_frame(QtWidgets, preview_button))
    break_off = break_off_button(QtWidgets, state, lambda t: state["write"](t))
    foot.addWidget(break_off)
    # The two run buttons are one pair and switch off the same way. The
    # rank stays readable: the main action filled, the dry run outlined.
    start_run.setStyleSheet(
        "QPushButton { background: %s; color: %s; font-weight: bold; "
        "border: 1px solid %s; border-radius: 5px; padding: 6px 21px; }"
        "QPushButton:disabled { background: %s; color: %s; "
        "border-color: %s; }"
        "QPushButton:hover:!disabled { background: %s; border-color: %s; }"
        % (COLOURS["heading"], COLOURS["sheet"], COLOURS["heading"],
           COLOURS["off"], COLOURS["off_text"], COLOURS["off"],
           COLOURS["value"], COLOURS["value"]))
    preview_button.setStyleSheet(
        "QPushButton { background: %s; color: %s; "
        "border: 1px solid %s; border-radius: 5px; padding: 6px 17px; }"
        "QPushButton:disabled { background: transparent; color: %s; "
        "border-color: %s; }"
        "QPushButton:hover:!disabled { background: %s; }"
        % (COLOURS["box"], COLOURS["heading"], COLOURS["heading"],
           COLOURS["off_text"], COLOURS["off"], COLOURS["backdrop"]))
    # Settings belongs with the buttons, not beside the tabs: not a step
    # of the work, so flat and at a distance, but where a button is sought.
    settings_button = QtWidgets.QPushButton(T('Settings ...'))
    settings_button.setFlat(True)
    hint(settings_button, T('Key for auphonic.com, and whether Resolve '
                            'answers.'))
    settings_button.clicked.connect(lambda: settings_open())
    foot.addSpacing(18)
    foot.addWidget(settings_button)
    row_same_height([start_run, preview_button, break_off, settings_button])

    # In full and in view: a tooltip is out of reach for the keyboard.
    start_note.setWordWrap(True)
    start_note.setVisible(False)
    # Named so it can be found: the test looks for this line, and a
    # reading program announces it by name rather than as "label".
    start_note.setObjectName("start_note")
    start_note.setAccessibleName(T('Why the run cannot start'))
    late["start_note"] = start_note
    return (start_run, start_run_env_curve, preview_button, break_off,
            plan_wipe, run_plan_build, run_step_order, total_clock)
