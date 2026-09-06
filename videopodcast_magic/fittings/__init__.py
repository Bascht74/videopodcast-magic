# -*- coding: utf-8 -*-
"""The fittings a window is put together out of.

A piece of the program, read out of the folder beside the way in by
beside(). It cannot import the file it was cut out of, because that
file is still being read while this one is; the program is handed in
instead, and every name this piece uses out of it is bound below, by
name. What the window still calls out of it, it binds there in turn.
"""

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

# What the program has and this piece uses, bound once so that the
# fittings read as they did in the window. LANG is left out -- the
# window sets it while it runs, and a copy would part from it at the
# first assignment -- so it stays PROGRAM.LANG where it is read.
COLOURS = PROGRAM.COLOURS
CUT_CHOICES = PROGRAM.CUT_CHOICES
CUT_FIELDS = PROGRAM.CUT_FIELDS
IGNORE_AUDIO = PROGRAM.IGNORE_AUDIO
NAME_ROOM = PROGRAM.NAME_ROOM
ROW_ROOM = PROGRAM.ROW_ROOM
SEVERAL_SPEAKERS = PROGRAM.SEVERAL_SPEAKERS
SHOT_NAMES = PROGRAM.SHOT_NAMES
T = PROGRAM.T
TN = PROGRAM.TN
Value = PROGRAM.Value
fill_choices = PROGRAM.fill_choices
label_of = PROGRAM.label_of
os = PROGRAM.os
sys = PROGRAM.sys
time = PROGRAM.time

# Three widths come out of the player and not out of the way in.
# beside() lays its path against the folder the program starts in,
# whoever calls it, so this is the piece the window read and not a
# second copy of it.
beside = PROGRAM.beside
player = beside("player", program=PROGRAM)
caption_room = player.caption_room
cut_caption_room = player.cut_caption_room
cut_choice_room = player.cut_choice_room

# fitted and widget_width stay in the window and get no line here:
# this file is read while the window is still being read, so a copy of
# either would be an AttributeError. They are read as PROGRAM.fitted
# and PROGRAM.widget_width at the one place each is used.


# Measured with co_freevars on 23.8.2026: not one of these reaches
# into gui(). They lived inside it out of habit, and 158 lines of
# the biggest function in the file were the price. Out here a test
# can call them directly instead of cutting them out of the source
# and exec-ing a copy, which is what two of them used to need. Out
# of the window since then, and a line at each end is the price.

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

    A field in a table cell is read out as its kind and nothing
    else -- "combo box", "edit field". Which column and which row
    it sits in is on the screen only, so it is said here as well.
    """
    widget.setAccessibleName("%s -- %s" % (what, row_name)
                             if row_name else what)
    return widget

# How narrow the name field may get. It is typed into, so it is the one
# column that must not give way: Qt lets a stretching column fall to
# 16 px and says nothing, and on the Windows builder this one went to
# 79 px at the narrowest window while everything still "fitted".
NAME_COLUMN_LEAST = 160


def split_column_room(widget):
    """How wide the Speakers column has to be for what it will hold.

    Not for what stands in it: it is filled minutes later, when a
    separation reports, and a column that measures its contents
    measured an empty one. Measured in the font that draws, over the
    two captions that must not wrap -- the running one, which shares
    the cell with the button, and the finished count.
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
    and never below *least*: a stretching one falls as far as Qt likes
    -- 79 px on the Windows builder, in the field a name is typed into.
    Where that will not fit, the tree scrolls, which is the lesser harm.
    """
    from PySide6 import QtCore as _qc
    from PySide6 import QtWidgets as _qw
    head = tree.header()
    head.setStretchLastSection(False)
    head.setSectionResizeMode(stretch, _qw.QHeaderView.Interactive)
    tree.setColumnWidth(column, split_column_room(tree))
    others = [c for c in range(head.count()) if c != stretch]
    # What the column was asked for before the room was shared out. It
    # never goes below that again: the leftover can be nothing at all,
    # and a column handed nothing is a field with no name in it.
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
    choosing. Here that offer comes out right; on the Windows builder
    it came out 14 px under what the text needed and a line went
    missing. So the height is not left to the offer: the width is read
    off the laid-out label and the height demanded from it. Twice
    round, because the first pass is what gives the label its width.
    """
    view = cells_are_shown_in(cells)
    if view is None:
        return False
    view.doItemsLayout()
    moved = False
    for _path, _button, mark, _item in list(cells or ()):
        # Let go of last time's height before asking again: a label
        # counts its own minimum into the answer, so an emptied cell
        # would still say it needs four lines. An empty one answers
        # -1, which is no height at all.
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

    The way out of a cell and back to the whole: tree_build makes the
    view the model's parent, so any one item knows where it is drawn.
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
    carries the button that breaks a running one off. Returns the cell
    and what has to be reached again while a run goes on: the button,
    the label, and the row's own item, which is the way from here back
    to the view that has to measure the row again.
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
    # of pixels wide, and two lines are better than a cut one. Making
    # room for the second line is cells_laid_out's business.
    mark.setWordWrap(True)
    row.addWidget(mark, 1)
    row.addWidget(button)
    return box, (path, button, mark, item)


def typed_part(new, old):
    """What somebody typed, out of a caption they typed into.

    A combo box showing a picked entry does not replace its caption
    when the next letter arrives, it edits it: typing "A" into "several
    speakers" with the cursor after "sev" leaves "sevAeral speakers".
    The letter is what was meant, so the caption is taken back out --
    by the head and the tail the two strings still share, which finds
    it wherever the cursor happened to be.
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

    One question -- who is to be heard on this recording? -- with three
    answers rather than a field beside a button. A name typed in says
    the recording is that one person. The one entry that can be picked
    instead says there are several, and the machine goes and tells them
    apart; the names then belong in the rows underneath.

    Picking a name again is allowed and costs nothing: the voices are
    hidden, not thrown away. A separation of 87 minutes takes three of
    them, and a mis-click must not be that expensive.

    What the file name suggests the person is called comes off the
    value itself and stands in the empty field in grey. It is never
    written in: a guess that is written in is a guess nobody checks,
    and "Zoom0004" would go into the mix as a speaker name. The field
    starts empty and stays empty until somebody answers.
    """
    from PySide6 import QtWidgets as _qw
    from PySide6.QtCore import Qt as _qt
    box = _qw.QComboBox()
    box.setEditable(True)
    box.setInsertPolicy(_qw.QComboBox.NoInsert)
    box.addItem(label_of(SEVERAL_SPEAKERS), SEVERAL_SPEAKERS)
    # On the entry itself, not only on the field: the field's own hint
    # is gone the moment the list is open, which is exactly when
    # somebody is deciding whether to pick this.
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
    # "one name, not several" rebuilds the whole sheet, and the field
    # being typed in is part of the sheet: given per keystroke, the
    # answer destroyed this very widget after the first letter, nothing
    # took the focus back, and the speaker was left called "A".
    typing = [False]

    def show_now():
        # Not while somebody is typing. Every letter reaches name_value,
        # which calls this, which would write the value back over the
        # word being written -- or, while the answer still reads
        # "several speakers", write that caption over it.
        if typing[0]:
            return
        if several_value.get():
            box.setCurrentIndex(0)
        else:
            box.setCurrentIndex(-1)
            box.setEditText(str(name_value.typed()))

    def picked(_i=0):
        # Picked from the list, so the typing is over with the click.
        # This way stays immediate: the rows underneath should appear
        # on the click and not after a detour through the field.
        typing[0] = False
        several_value.set(box.currentData() == SEVERAL_SPEAKERS)

    def typed(text):
        # textEdited and not textChanged: the second one fires when the
        # picked entry writes its own caption into the field, and the
        # answer would undo itself in the same breath.
        if not typing[0] and several_value.get():
            # The first letter on a field that was showing "several
            # speakers". Qt has just edited that caption rather than
            # replaced it, so the caption comes back out and only what
            # was typed stays.
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
    neither the file name nor the two times. Those times were pulled
    apart on 25.8.2026 -- how long the voice speaks and where its
    longest passage lies had been one number that read like a
    timestamp -- and that was the right answer to the wrong question:
    neither belongs on screen. The longest passage is still worked out,
    because it is where a click on the row takes the player. It is
    simply not written down, and the column stays narrow.

    Returns (name field, camera chooser).
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
        transcript, so a name for it is an entry without effect. It is
        greyed, not emptied: switching back must not cost the typing.

        Only "do not use" does this. "No camera of its own" means the
        person is in the mix and in the transcript, and there the name
        works -- greying it there would take away a setting that has
        an effect.

        The row stays selectable, which is what plays the voice: a
        disabled field lets the click through to the view under it,
        and that is the very tool somebody decides with. And the
        greying needs no reason written beside it, because the reason
        stands two fields along in the same row.
        """
        field.setEnabled(camera_value.get() != IGNORE_AUDIO)

    camera_value.listen(name_useful)
    name_useful()
    # So that nothing has to tell a voice from its recording by the
    # wording of a caption: whoever reads these rows can ask the field
    # itself which of the two levels it belongs to.
    for w in (field, box):
        w.setObjectName("voice")
    return field, box


def more_speakers_row(audio_file_list, on_pick):
    """The row that asks for one speaker more than was found.

    Every recording can be listened to again, whether anything was
    found in it or not: whoever hears a fourth person knows it before
    the program does. One button per recording put the player on the
    right over the edge of the window from three recordings on, and
    there can be seven -- so with more than one recording the name
    moves off the button and into a chooser beside it, and the row
    stays the same width whatever the material.
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
        # The whole name first, at the ordinary size. Only if that is
        # too wide does the type get smaller, and only then is the
        # name shortened -- the elision has to be measured in the font
        # the button really draws with.
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
        # Button and chooser together have to fit; measured as a pair,
        # and shrunk as a pair or not at all -- two different sizes
        # side by side look like a mistake.
        if (button.sizeHint().width()
                + min(which.sizeHint().width(), NAME_ROOM) > ROW_ROOM):
            font_smaller(button, 2)
            font_smaller(which, 2)
        # The width comes after the type is settled, in the font the
        # box really draws with, and it comes from the names rather
        # than from a count of characters. Measured offscreen at this
        # Mac's system font, 31.8.2026: a name of 27 letters wants 288
        # px and the box can give its text 216, so that one is
        # shortened and shorter names beside it are not.
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

    The first menu on a Mac carries the name of the running program, and
    that name does not come from Qt. It comes from CFBundleName in the
    bundle around the executable -- and a script started with python3
    has no bundle of its own, so it borrows the one Python lives in.
    Measured on this Mac, 30.8.2026: the entry read "Python", and every
    menu said so.

    setApplicationName does not reach it; only the bundle does. So the
    entry is written, through the Objective-C runtime, before the
    application is built -- afterwards the menu is already drawn.
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
        # An older macOS, a bundled build that already carries its name,
        # or a runtime that will not be talked to. The menu then says
        # what it said before, and nothing else is worse for it.
        return False


def total_paint(Qt, plan, total_state, total_bar, total_line):
    """Draw the whole run's progress bar, or take it away when it is over.

    Outside gui() because it reaches into nothing of its own: the plan it
    reads and the two widgets it writes to come in as arguments.
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

    Clearing the plan is not enough. The widget goes on showing the
    figure it was last given until the timer draws again, and
    total_paint only hides it after a step has finished -- which is
    what does not happen when work is called off. Outside gui() beside
    total_paint, and for the same reason: it touches nothing of its own.
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
    its own way of being called off already -- a queue to empty, a
    number saying which list it belongs to -- and this is the one place
    that uses all of them. The prework goes first: it takes the files
    off the bar, which is wiped after.
    """
    prework_clean_up(paths)
    for counted in ("preflight_run", "axis_run", "speakers_run"):
        state[counted] = state.get(counted, 0) + 1
    state["axis_running"] = False
    split_stop()
    split_run["busy"] = False
    # What split_stop wrote into the row goes with it: "Stopping ..."
    # must not be the last thing said about a production that is no
    # longer open.
    state["split_note"] = None
    state["speakers_running"] = ""
    hide_bar()


def qt_own_words(QtCore, app):
    """Give Qt its own texts in the chosen language.

    "Preferences", "Quit", "Services" and the buttons in the file dialog
    are Qt's words, not ours, so they stay English however much of our
    own text is translated -- on a Mac the whole first menu was English
    in a German window. Qt brings them translated and only has to be
    told to use them. Kept in a list afterwards: Qt holds no reference,
    so a translator that goes out of scope changes nothing.
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
    chosen; without it, a message with nothing to decide. The buttons
    carry the action rather than yes and no, so nobody has to read the
    question backwards to know what will happen.
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
    # Both buttons to the right, the action outermost and preselected --
    # the way the system does it.
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

    Through the font and not through a style sheet: a fixed size in
    a style sheet ignores whatever the system font is set to, and
    then reads as tiny on one machine and as normal on the next.
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

    Smaller type is a cost, not a free win: it is harder to read,
    and on a machine whose system font was turned up it undoes
    exactly what somebody set it for. So it is taken where the row
    would otherwise push the sheet wider than the player leaves
    it, and nowhere else.
    """
    if widget.sizeHint().width() <= room:
        return widget
    return font_smaller(widget, less)

def short_name(widget, text, room):
    """Shorten a file name to the room there is, from the middle.

    Both ends of a file name carry what tells two of them apart --
    the take at the front, the channel at the back -- so what goes
    is the middle. The width is measured in the font the widget
    actually draws with.
    """
    from PySide6 import QtCore as _qc
    return widget.fontMetrics().elidedText(text, _qc.Qt.ElideMiddle, room)

def box_names_fit(box, room):
    """Give a chooser of file names the width it needs, up to *room*.

    A chooser asks for as much as its widest entry needs and no more
    than *room*; what it cannot get, it takes off the name. Qt takes it
    off the end, and the recordings of one session differ at the end --
    cut there, three of them read alike. So where the room is not
    enough, every entry is shortened in the middle instead, and the
    whole name stays reachable as a tooltip: on the entry in the open
    list, and on the box itself for the one that is chosen.

    Nothing is shortened while the room is enough. An unshortened name
    is worth more than a uniform look.
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

    The field shows the answer and not the name behind it: a value
    that carries a suggestion offers it in grey, which is where a
    guess belongs and where it can be overruled by typing over it.
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

    The list shows the translated names, the value keeps the name
    the switch carries -- a project written on a German machine has
    to read the same on an English one.
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
    without sixty lines of grid. It is a builder and nothing else: the
    values it makes are handed back, and what listens to them is the
    window's business.

    Returns {command line name: Value}, in the order CUT_FIELDS and
    CUT_CHOICES stand in, which is the order they are read in.

    *parts* is filled with {command line name: (row, field or box)} for
    whoever has to grey a setting out later. Handed over rather than
    returned, so the one thing this builds stays the one thing it
    returns and the callers that want none of it change nothing.
    """
    parts = {} if parts is None else parts
    from PySide6 import QtWidgets as _qw
    from PySide6.QtCore import Qt as _qt
    cut_var = {}
    field_grid = _qw.QGridLayout()
    into.addLayout(field_grid)
    # The rhythm first, the wide shot after it, and the question last --
    # its seconds stand directly above "After a question", which is the
    # first of the choices below. At half the width the sliders no
    # longer fit side by side.
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
        # The caption stands to the left of the field and the unit
        # to the right of it; neither is read out with the field, so
        # both are said here.
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
    # belongs on screen, and what is shown instead. They sit here and
    # not in the settings window because they change the cut, and the
    # cut is what this tab is about.
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
    Red in the row shows which one is meant, and the hint on it says why.
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
