# -*- coding: utf-8 -*-
"""The list of chosen files: the widget, and what changes what is in it.

A piece of the program, read in by beside(): it cannot import the file
it was cut out of, so the program is handed in and bound below by name.
"""

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# Bound above the seam. Two names are missing, and the two blocks
# under the list say which and why.

AUDIO_SUFFIXES = PROGRAM.AUDIO_SUFFIXES
COLOURS = PROGRAM.COLOURS
ON_DARK = PROGRAM.ON_DARK
T = PROGRAM.T
TN = PROGRAM.TN
VIDEO_SUFFIXES = PROGRAM.VIDEO_SUFFIXES
audio_summary = PROGRAM.audio_summary
beside = PROGRAM.beside
group_recording_parts = PROGRAM.group_recording_parts
guess_production_name = PROGRAM.guess_production_name
number_text = PROGRAM.number_text
os = PROGRAM.os
path_key = PROGRAM.path_key
probe_warm = PROGRAM.probe_warm
project_offer = PROGRAM.project_offer
recording_family = PROGRAM.recording_family
recordings_text = PROGRAM.recordings_text
remembered_forget = PROGRAM.remembered_forget
trouble_log = PROGRAM.trouble_log
video_facts = PROGRAM.video_facts
video_summary = PROGRAM.video_summary

# join_box_fill is the first one missing: it stands in the window
# below the line this file is read at, so a copy taken here is an
# AttributeError, and no earlier seam mends that.

# chain_fill_in is the second, and stands above that line. It goes the
# same way: both are asked as PROGRAM.something where they are called,
# by which time the window has been read whole.

# What the fittings bring. beside() lays its path against the folder
# the way in sits in, so this finds videopodcast_magic/fittings/ and
# not a folder under this one; the window is handed the same module.
fittings = beside("fittings", program=PROGRAM)
_list_accepts = fittings._list_accepts
label = fittings.label
speaks_as = fittings.speaks_as


#-------------------------------------------------- The list as a widget
# The tree on the first tab with its five columns. It holds no state of
# the window: a dropped file reaches take_paths through state.


def make_file_list(Qt, QtGui, QtWidgets, sheet1_position, state):
    """Tab 1: the list of chosen files, with its stripes and its marks.

    Its own name because it is the widget and nothing else: the tree,
    what a file dropped on it does, the sentence the check writes into,
    the colour tables, and the maker of a single row.
    """
    items = QtWidgets.QTreeWidget()
    items.setColumnCount(5)
    # Column 0 carries the name and the tree structure, column 1 the
    # check mark -- indentation and the arrow sit in front of column 0.
    # Columns 3 and 4: what a video file is, and whether its sound counts.
    items.setHeaderLabels([T('File'), "", "", T('Kind'), T('Camera audio')])
    # Not uniform: those two hold drop-downs, taller than a line of
    # text, and uniform squashes them to the first row's height.
    items.setUniformRowHeights(False)
    items.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Interactive)
    items.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
    items.header().setStretchLastSection(False)
    for _c, _how in ((2, QtWidgets.QHeaderView.Stretch),
                     (3, QtWidgets.QHeaderView.ResizeToContents),
                     (4, QtWidgets.QHeaderView.ResizeToContents)):
        items.header().setSectionResizeMode(_c, _how)
    items.setColumnWidth(0, 420)
    items.setColumnWidth(1, 26)
    items.setAcceptDrops(True)
    items.setDragDropMode(QtWidgets.QAbstractItemView.DropOnly)
    speaks_as(items, T('Chosen files'))
    sheet1_position.addWidget(items, 1)

    def _list_takes(e):
        paths = [u.toLocalFile() for u in e.mimeData().urls()
                 if u.isLocalFile()]
        if paths:
            e.acceptProposedAction()
            state["take_paths"](paths)

    # Dropping onto the full list works too, not only onto the empty one.
    items.dragEnterEvent = _list_accepts
    items.dragMoveEvent = _list_accepts
    items.dropEvent = _list_takes

    # Below the list, one sentence on what the check found. The details
    # are marks in the first column; hovering or expanding says more.
    preflight_line = label("", COLOURS["quiet"])
    preflight_line.setWordWrap(True)
    preflight_line.setVisible(False)
    sheet1_position.addWidget(preflight_line)

    # The stripes: light on light, dark on dark, structure without glare.
    SHADES = {}

    def stripes_pick():
        """Fill the stripes of the file list for this desktop.

        Refilled in place and read off ON_DARK rather than asking the
        desktop again: two answers to one question drift apart.
        """
        SHADES.clear()
        SHADES.update({"group": QtGui.QColor("#2f3b49"),
             "audio": QtGui.QColor("#28313c"),
             "video": QtGui.QColor("#332f27"),
             "block": QtGui.QColor("#262b31")}
            if ON_DARK[0] else
            {"group": QtGui.QColor("#d9e2ec"),
             "audio": QtGui.QColor("#eef4fa"),
             "video": QtGui.QColor("#f3f0e8"),
             "block": QtGui.QColor("#f7f7f7")})

    stripes_pick()

    def line_colourise(item, kind, bold=False):
        brush = QtGui.QBrush(SHADES[kind])
        for column in range(items.columnCount()):
            item.setBackground(column, brush)
            if bold:
                s = item.font(column)
                s.setBold(True)
                item.setFont(column, s)
        return item

    # A mark says more than a line of text while there are only three.
    MARKS = {}

    def marks_pick():
        """Fill the marks of the first column with today's colours."""
        MARKS.clear()
        MARKS.update({"good": ("\u2713", COLOURS["good"]),
                      "hint": ("!", COLOURS["error"]),
                      "fixed": ("\u2713", COLOURS["good"]),
                      "abort": ("\u2715", COLOURS["error"])})

    marks_pick()
    # What a finding is called when it appears as its own row under the file.
    FINDING_WORD = {"hint": T('Note'), "fixed": T('fixed'),
                   "abort": T('Caution')}

    def set_mark(node, kind, text=""):
        """Give the file its check mark."""
        how = MARKS.get(kind)
        if not how:
            return
        if kind in ("hint", "abort"):
            trouble_log("%s -- %s" % (node.text(0) or "?", text or kind))
        node.setText(1, how[0])
        node.setForeground(1, QtGui.QBrush(QtGui.QColor(how[1])))
        node.setTextAlignment(1, Qt.AlignCenter)
        font = node.font(1)
        font.setBold(True)
        node.setFont(1, font)
        if text:
            for column in (0, 1, 2):
                node.setToolTip(column, text)

    def item(parent, text, value="", kind=None, bold=False, files_for_it=None,
               group_kind=None):
        p = QtWidgets.QTreeWidgetItem(parent, [text, "", value])
        if kind:
            line_colourise(p, kind, bold)
            # Kept, not only painted: Remove tells a block from its own
            # recording.
            p.setData(0, Qt.UserRole + 3, kind)
        if files_for_it is not None:
            p.setData(0, Qt.UserRole, list(files_for_it))
        if group_kind:
            p.setData(0, Qt.UserRole + 1, group_kind)
        return p

    return (items, preflight_line, stripes_pick, marks_pick, MARKS,
            FINDING_WORD, set_mark, item)

#------------------------------------------ Adding, removing, and again
# The five that change what the list holds and build every row again.
# They answer each other, which is why they are one call and not five.


def make_file_changes(Qt, QtCore, QtWidgets, window, state, files, ask,
                      report, items, item, drop_area, preflight_line,
                      preflight_fill_in, preflight_kick_off, blocks_of,
                      recording_of, join_to, no_join, lines_node,
                      prework_node, video_kind_again, channel_rows_show,
                      audio_use_now, video_choices_show, settings_show,
                      buttons_check, show_weak, assignment_fresh,
                      finished_tracks_check, prework_clean_up, remembered,
                      together_now, production_var, commonest_folder,
                      remove_button, bar_env_curve):
    """The file list changing: adding, removing, and reading it again.

    One name for five because they are one theme and answer each other:
    take_paths and remove change what `files` holds, and both end in
    items_fresh, which builds every row again and asks for a check.
    """

    def join_row_show(node, path, heads):
        """Offer to put this recording into another one.

        The counterpart to "stands on its own" on a block: there a file
        that was found is taken out, here one that was not is put in --
        for a recorder that numbers by neither counter nor clock. Only
        offered while there is another recording to join, and never on
        the one being joined into; join_barred says what is greyed.
        """
        others = [h for h in heads if path_key(h) != path_key(path)
                  and h not in join_to]
        if not others:
            return
        kid = QtWidgets.QTreeWidgetItem(["      " + T('belongs to'), "", ""])
        kid.setData(0, Qt.UserRole + 2, "join")
        node.insertChild(0, kid)
        box = PROGRAM.join_box_fill(QtWidgets.QComboBox(), path, others,
                                    blocks_of)
        i = box.findData(join_to.get(path) or "")
        box.setCurrentIndex(i if i >= 0 else 0)

        def chosen(_i=0, file_path=os.path.abspath(path), b=box):
            target = b.currentData() or ""
            if target:
                join_to[file_path] = target
            else:
                join_to.pop(file_path, None)
            QtCore.QTimer.singleShot(0, items_fresh)
            QtCore.QTimer.singleShot(0, assignment_fresh)
            QtCore.QTimer.singleShot(0, preflight_kick_off)

        box.currentIndexChanged.connect(chosen)
        # In the wide column: column one is only as wide as a checkbox.
        items.setItemWidget(kid, 2, box)

    def items_fresh():
        probe_warm([p for p, _ in files])
        items.clear()
        # The rows are gone with it, so what could draw them again goes too.
        video_kind_again.clear()
        prework_node.clear()
        lines_node.clear()
        # Which blocks belong to which recording is worked out below, for
        # the audio files in the list now. Emptied here rather than
        # there: with the last one gone the loop never reaches that branch.
        blocks_of.clear()
        recording_of.clear()
        remove_button.setEnabled(False)
        # Once for the whole list: the rule looks at every file at once.
        own_now, forced_now = audio_use_now()
        state["own_cameras"] = list(own_now)
        state["forced_own"] = list(forced_now)
        for kind, title in (("audio", T('AUDIO')), ("video", "VIDEO")):
            own = [p for p, a in files if a == kind]
            if not own:
                continue
            if kind == "audio":
                chains = group_recording_parts(own, apart=no_join,
                                               together=together_now())
                file_count = sum(len(r) for r, _ in chains)
                header_value = recordings_text(len(chains), file_count)
                state["audio_recordings"] = len(chains)
            else:
                chains, header_value = None, TN(
                    len(own), '%s file', '%s files') % number_text(len(own), 0)
            group = item(items, title, header_value, "group", True,
                            group_kind=kind)
            group.setExpanded(True)
            if kind == "audio":
                selected = set(os.path.abspath(p) for p in own)
                heads = [r[0] for r, _d in chains]
                for r, _d in chains:
                    head = os.path.abspath(r[0])
                    blocks_of[head] = [os.path.abspath(x) for x in r]
                    for x in r:
                        recording_of[x] = head
                for row, discarded in chains:
                    if len(row) > 1:
                        node = PROGRAM.chain_fill_in(
                            group, row, discarded, selected, item,
                            lines_node, channel_rows_show)
                        join_row_show(node, row[0], heads)
                        continue
                    p = row[0]
                    node = item(group, os.path.basename(p),
                                    os.path.dirname(p), "audio",
                                    files_for_it=[p])
                    lines_node[p] = node
                    join_row_show(node, p, heads)
                    channel_rows_show(node, p)
                    try:
                        lines = audio_summary(p)
                    except Exception as e:
                        lines = [(T('Error'), str(e)[:120])]
                    for k, value in lines:
                        item(node, "      " + k, value)
                    # Collapsed: format details are reference, not news.
                    node.setExpanded(False)
                continue
            for p in sorted(own,
                            key=lambda x: os.path.basename(x).lower()):
                node = item(group, os.path.basename(p),
                                os.path.dirname(p), "video", files_for_it=[p])
                prework_node[p] = (node, os.path.dirname(p))
                lines_node[p] = node
                video_choices_show(node, p, own_now, forced_now)
                channel_rows_show(node, p)
                try:
                    lines = video_summary(p, video_facts(p))
                except Exception as e:
                    lines = [(T('Error'), str(e)[:120])]
                for k, value in lines:
                    item(node, "      " + k, value)
                node.setExpanded(False)
        # The drop area gives way to the list as soon as something is in it.
        drop_area.setVisible(not files)
        items.setVisible(bool(files))
        preflight_line.setVisible(bool(files))
        # Re-enter what is measured, so the list is never briefly markless.
        if state.get("preflight_findings"):
            preflight_fill_in(state["preflight_findings"])
        preflight_kick_off()
        bar_env_curve.setVisible(bool(files))
        # The name comes from the material, the output folder from
        # nobody: a handover file in a subfolder belongs to the run that
        # wrote it, so the folder stays empty until it is chosen.
        if files and not production_var.get().strip():
            production_var.set(guess_production_name(files[0][0]))
        show_weak()
        finished_tracks_check()
        buttons_check()
        settings_show()
        assignment_fresh()

    def take_paths(new_one, quiet=False):
        """Take paths into the list, from the file dialog or dragged in.

        Folders are expanded: dragging in the recording folder means the files
        in it, not the folder.
        """
        paths = []
        for p in new_one:
            if os.path.isdir(p):
                for name in sorted(os.listdir(p)):
                    paths.append(os.path.join(p, name))
            else:
                paths.append(p)
        unknown = []
        for p in paths:
            e = os.path.splitext(p)[1].lower()
            kind = ("audio" if e in AUDIO_SUFFIXES
                   else "video" if e in VIDEO_SUFFIXES else None)
            if kind is None:
                if not os.path.basename(p).startswith("."):
                    unknown.append(os.path.basename(p))
                continue
            if p not in [x for x, _ in files]:
                files.append((p, kind))
        if unknown and not quiet:
            report(T('Not recognised'),
                   T('These files are neither audio nor video and stay '
                     'out:\n\n  %s') % "\n  ".join(unknown[:12]))
        # Asked before the files are measured: opening the project
        # replaces the list with its own files and builds that list
        # itself, so anything measured first was measured for nothing.
        if project_offer(QtWidgets, window, state, [x for x, _ in files],
                         ask, state["project_open"]):
            return
        items_fresh()

    def add_files():
        pattern = (T('Audio and video (%s);;All files (*)')
                  % " ".join("*" + e for e in AUDIO_SUFFIXES + VIDEO_SUFFIXES))
        new_one, _ = QtWidgets.QFileDialog.getOpenFileNames(
            window, T('Select audio and video files'),
            commonest_folder() or "", pattern)
        take_paths(new_one)

    def remove():
        choice = items.currentItem()
        if choice is None:
            return
        # On a group header it means all of it, so it asks.
        kind = choice.data(0, Qt.UserRole + 1)
        single_block = False
        if kind:
            affected = [p for p, a in files if a == kind]
            if not affected:
                return
            how = T('audio file') if kind == "audio" else T('video file')
            if not ask(T('Remove all'),
                    T('Remove all %s %ss from the list?\n\n%s')
                    % (number_text(len(affected), 0), how,
                       "\n".join("  " + os.path.basename(p)
                                  for p in affected[:12])
                       + ("\n  ..." if len(affected) > 12 else "")),
                    T('Remove from list')):
                return
            gone = set(os.path.abspath(p) for p in affected)
        else:
            # Upwards from the clicked node until one stands for files.
            # With a multi-part recording the whole recording always goes:
            # a single block would be found again on the next rebuild.
            node = choice
            while node is not None and node.data(0, Qt.UserRole) is None:
                node = node.parent()
            if node is None:
                return
            gone = set(os.path.abspath(p) for p in node.data(0, Qt.UserRole))
            single_block = node.data(0, Qt.UserRole + 3) == "block"
            if single_block:
                # One block out of a recording: it must stay out. The
                # search for continuations looks in the folder, not here.
                no_join.update(gone)
        files[:] = [(p, a) for p, a in files
                      if os.path.abspath(p) not in gone]
        # A whole recording leaving takes the marks of its blocks with
        # it: adding the files again then joins them up as before.
        if not single_block:
            for p in list(gone):
                no_join.difference_update(recording_family(p))
        prework_clean_up(gone)
        items_fresh()
        # After the tables are built again, not before: building them
        # writes back every row they hold, and the row that has just gone
        # is among them until then. This store feeds the project file.
        remembered_forget(remembered, gone)

    return items_fresh, take_paths, add_files, remove
