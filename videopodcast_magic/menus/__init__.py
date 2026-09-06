# -*- coding: utf-8 -*-
"""The menu bar of the window, and the transport on its keys.

A piece of the program, read in by beside(): it cannot import the file
it was cut out of, so the program is handed in and bound below by name.
"""

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# Bound above the seam. Every entry arrives as a name, a key and
# something to call, so what it does stays the window's business.
T = PROGRAM.T
open_page = PROGRAM.open_page

# Eight names of the window get no line here: this file is read while
# the window still is, so a copy would be an AttributeError. Each is
# read as PROGRAM.<name> where it is used.


def player_of_tab(tabs, players):
    """The player standing on the tab showing now, or None elsewhere.

    Which tab a player is on is nowhere written down: the sheet is
    asked whether the player is inside it. A folded-away player is none.
    """
    sheet = tabs.currentWidget()
    if sheet is None:
        return None
    for one in players:
        if (one is not None and sheet.isAncestorOf(one)
                and one.isVisibleTo(sheet)):
            return one
    return None


def player_loaded(one):
    """Whether a player has anything at all to play.

    The preview player holds one file, the cut player a list of shots.
    Both are empty until material arrives, and a transport command on
    an empty player does nothing -- which looks like a broken program.
    """
    return bool(getattr(one, "file_path", None) or getattr(one, "cut", None))


def transport(pick, what, *rest):
    """One transport command, to the player of the tab showing now.

    A player without that command is left alone rather than raising:
    the stand-in for a Qt without multimedia knows less than the others.
    """
    doing = getattr(pick(), what, None)
    if doing is not None:
        doing(*rest)


def build_menus(QtGui, QtCore, QtWidgets, window, tabs, player, does,
                switched=None, cut_player=None, late=None, buttons=None,
                project_here=None):
    """The whole menu bar, from a table of what each entry does.

    Outside gui() because it decides nothing. Every entry is a name, a
    key and something to call, and all three come in. *buttons* are the
    ones the switched entries follow, in their order.
    """
    def act(where, text, doing, keys="", inside=None):
        """One menu entry, with its key.

        *inside* scopes the key to a widget: bare keys -- Space, I, O,
        the arrows -- must not fire while somebody types into a field.
        Several may be named; the key works at whichever has the focus.
        """
        action = QtGui.QAction(text, window)
        action.triggered.connect(lambda _=False: doing())
        if keys:
            action.setShortcut(QtGui.QKeySequence(keys))
            if inside is not None:
                action.setShortcutContext(
                    QtCore.Qt.WidgetWithChildrenShortcut)
                for widget in (inside if isinstance(inside, (list, tuple))
                               else [inside]):
                    widget.addAction(action)
        where.addAction(action)
        return action

    menu = QtWidgets.QMenuBar()

    # Three groups, in the order the work goes: the project first,
    # because a session begins by opening one or starting a new one;
    # then the material, then the run.
    file_menu = menu.addMenu(T('&File'))
    act(file_menu, T('Open project ...'), does["open project"], "Ctrl+P")
    project_entries = [
        act(file_menu, T('Save project'), does["save project"], "Ctrl+S"),
        act(file_menu, T('Close project'), does["close project"], "Ctrl+W")]
    file_menu.addSeparator()
    act(file_menu, T('Add files ...'), does["add files"], "Ctrl+O")
    remove_entry = act(file_menu, T('Remove'), does["remove"],
                       "Ctrl+Backspace")
    act(file_menu, T('Output folder ...'), does["output folder"],
        "Ctrl+Shift+O")
    file_menu.addSeparator()
    run_entries = [act(file_menu, T('Start'), does["start"], "Ctrl+R"),
                   act(file_menu, T('Dry run'), does["dry run"],
                       "Ctrl+Shift+R")]
    followers = [remove_entry] + run_entries
    # The window decides what lives here: these five are switched with
    # the buttons that do the same thing. Born grey, because an empty
    # window has nothing to remove, save or start.
    for entry in project_entries + followers:
        entry.setEnabled(False)
    if late is not None:
        late["menu_project"] = project_entries
        late["menu_follows"] = list(zip(followers, buttons or ()))
        late["project_here"] = project_here
        # A menu built once carries the state of then, and the buttons
        # move while it stands. Asked again on opening, as View is.
        file_menu.aboutToShow.connect(lambda: PROGRAM.menus_follow(late))
    file_menu.addSeparator()
    # Qt moves anything it recognises as settings into the application
    # menu on a Mac, which is where people look for it.
    settings_action = act(file_menu, T('Settings ...'), does["settings"],
                          "Ctrl+,")
    settings_action.setMenuRole(QtGui.QAction.PreferencesRole)

    # The tabs by their own names, read off the tab, so the menu says
    # what the tab says. The tick a finished tab carries is left out:
    # an entry that changes under the hand is worse than none.
    view_menu = menu.addMenu(T('&View'))
    def view_menu_fill():
        """Name the tabs that are there, each time the menu opens.

        Built once, at the end of gui(), when only the first tab
        stands; the others arrive with the material. Qt has no signal
        for a tab arriving, and it has one for a menu opening.
        """
        view_menu.clear()
        for number in range(tabs.count()):
            named = tabs.tabText(number).replace("&&", "&")
            shown = act(view_menu, named.replace("\u2713", "").strip(),
                        lambda i=number: tabs.setCurrentIndex(i),
                        "Ctrl+%d" % (number + 1))
            # The entry shows the key and must not answer it: with the
            # window's own key that is two answers, and Qt fires neither.
            shown.setShortcutContext(QtCore.Qt.WidgetShortcut)

    view_menu_fill()
    view_menu.aboutToShow.connect(view_menu_fill)
    # The keys are not the menu's: a shortcut on a menu entry exists
    # only while that entry does, and the menu is refilled on opening.
    # These hang on the window and wait for their tab.
    for number in range(PROGRAM.TABS_AT_MOST):
        keyed = QtGui.QShortcut(
            QtGui.QKeySequence("Ctrl+%d" % (number + 1)), window)
        keyed.activated.connect(
            lambda i=number: (tabs.setCurrentIndex(i)
                              if i < tabs.count() else None))

    play_menu = PROGRAM.player_menu(menu, player)
    # Two players -- the preview on the assignment tab, the cut player
    # on the Resolve tab. Which is meant is decided at the press, not
    # when the entry is built: the tab changes and the menu stands.
    both = [player] + ([cut_player] if cut_player is not None else [])
    played = []

    def playing():
        return player_of_tab(tabs, both)

    def play_enable():
        """Grey the transport out where there is no player to drive.

        There is no player on the file and output tabs, and none on the
        others until material arrives; an entry this player cannot do
        stays grey too. Asked again on opening, like the View menu.
        """
        one = playing()
        on = player_loaded(one)
        for entry, what in played:
            entry.setEnabled(on and hasattr(one, what))

    played.append((act(play_menu, T('Play and pause'),
                       lambda: transport(playing, "toggle"), "Space", both),
                   "toggle"))
    # L and K as in every editing program: L runs forward, K holds and
    # never starts. J is missing on purpose -- backwards the ffmpeg
    # backend under Qt reports a rate of 0.00 and stands still.
    played.append((act(play_menu, T('Play forward, faster on every press'),
                       lambda: transport(playing, "faster"), "L", both),
                   "faster"))
    played.append((act(play_menu, T('Pause'),
                       lambda: transport(playing, "pause"), "K", both),
                   "pause"))
    play_menu.addSeparator()
    for text, keys, seconds in (
            (T('One frame back'), "Left", -1.0 / 30.0),
            (T('One frame forward'), "Right", 1.0 / 30.0),
            (T('One second back'), "Shift+Left", -1.0),
            (T('One second forward'), "Shift+Right", 1.0),
            (T('Ten seconds back'), "Alt+Left", -10.0),
            (T('Ten seconds forward'), "Alt+Right", 10.0)):
        played.append((act(play_menu, text,
                           lambda s=seconds: transport(playing, "nudge", s),
                           keys, both), "nudge"))
    play_enable()
    play_menu.aboutToShow.connect(play_enable)
    tabs.currentChanged.connect(lambda *_: play_enable())
    play_menu.addSeparator()
    # The same four things the buttons under the player do, and greyed
    # with them: without a time axis both must go dead together.
    for text, doing, keys in (
            (T('Mark In'), does["mark in"], "I"),
            (T('Mark Out'), does["mark out"], "O"),
            (T('to In point'), does["to in"], "Shift+I"),
            (T('to Out point'), does["to out"], "Shift+O")):
        entry = act(play_menu, text, doing, keys, player)
        if switched is not None:
            switched.append(entry)

    help_menu = menu.addMenu(T('&Help'))
    act(help_menu, T('The manual'),
        lambda: open_page("https://github.com/Bascht74/"
                          "videopodcast-magic#readme"))
    act(help_menu, T('What changed in this version'),
        lambda: PROGRAM.changes_shown(window))
    PROGRAM.log_entry(act, help_menu, window)
    help_menu.addSeparator()
    act(help_menu, T('Look for a newer version now'),
        lambda: PROGRAM.update_offer(window, asked=True))
    # Always there, never greyed and never hidden: behind it is a
    # question to github, and no menu being built can know the answer.
    act(help_menu, T('Back to an earlier version ...'),
        lambda: PROGRAM.restore_offer(window))
    about = act(help_menu, T('About Video Podcast Magic'),
                lambda: PROGRAM.about_show(window))
    about.setMenuRole(QtGui.QAction.AboutRole)
    return menu
