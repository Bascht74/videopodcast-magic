# -*- coding: utf-8 -*-
"""The project file: a production written down, found again and read back.

A piece of the program, read in by beside(): it cannot import the file
it was cut out of, so the program is handed in and bound below by name.
"""

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# What this piece uses out of the program, bound once. Five names of
# the window stay below the seam and are read through PROGRAM where
# they are used: RESTART_ASK, _qt_widgets, language_of_system,
# measuring_stop and window_title.

ByFile = PROGRAM.ByFile
FILE_FORMAT = PROGRAM.FILE_FORMAT
PROJECT_PREFIX = PROGRAM.PROJECT_PREFIX
SPEAKER_STATE = PROGRAM.SPEAKER_STATE
T = PROGRAM.T
VERSION = PROGRAM.VERSION
VIDEO_SUFFIXES = PROGRAM.VIDEO_SUFFIXES
as_head = PROGRAM.as_head
find_handover_file = PROGRAM.find_handover_file
format_complaint = PROGRAM.format_complaint
json = PROGRAM.json
keep_setting = PROGRAM.keep_setting
loudness_last = PROGRAM.loudness_last
os = PROGRAM.os
preset_list_bring = PROGRAM.preset_list_bring
probe_warm = PROGRAM.probe_warm
settings = PROGRAM.settings
speakers_all_from_project = PROGRAM.speakers_all_from_project
speakers_from_project = PROGRAM.speakers_from_project
speakers_front_pick = PROGRAM.speakers_front_pick
time = PROGRAM.time
voice_keys_carry_source = PROGRAM.voice_keys_carry_source
words_forgotten = PROGRAM.words_forgotten


# =====================================================================
#  Finding one, and offering it
#  ----------------------------

def projects_beside(paths, deep=40):
    """The project files lying with this material, newest first.

    Looked for in the folders the material is in and one level below,
    since the project file goes into the output folder. Not deeper: a
    search over the whole disk would stand in the way of adding a file.
    Gives (path, when) pairs, each path once.
    """
    folders = []
    for one in paths:
        folder = os.path.dirname(os.path.abspath(one))
        if folder not in folders:
            folders.append(folder)
    look = list(folders)
    for folder in folders:
        # Counted by folders, not by names: a recording folder holds
        # hundreds of files, the output folder anywhere among them.
        count = 0
        try:
            names = sorted(os.listdir(folder))
        except OSError:
            continue
        for name in names:
            full = os.path.join(folder, name)
            if full in look or not os.path.isdir(full):
                continue
            look.append(full)
            count += 1
            if count >= deep:
                break
    found = {}
    for folder in look:
        # One attempt for the whole folder, not one per file: a folder
        # nobody can read holds no project file anybody can open.
        try:
            for name in os.listdir(folder):
                if (name.startswith(PROJECT_PREFIX)
                        and name.lower().endswith(".json")):
                    full = os.path.join(folder, name)
                    found[full] = os.path.getmtime(full)
        except OSError:
            continue
    return sorted(found.items(), key=lambda pair: -pair[1])


def when_written(when):
    """When a file was written, short enough to stand in a list."""
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(when))


def project_offer(QtWidgets, window, state, paths, ask, load):
    """Offer a project file lying with the material; never load it silently.

    Asked once per file found; the project is opened whole or not at
    all, and once one is open nothing more is offered. Returns whether
    one was opened -- the caller must not then rebuild the list.
    """
    if state.get("project_from"):
        return False
    seen = state.setdefault("projects_offered", set())
    found = [(one, when) for one, when in projects_beside(paths)
             if one not in seen]
    if not found:
        return False
    seen.update(one for one, _ in found)
    whole = T('Everything comes back from it: names, separation, assignment, '
              'types, the time window. The list of files is replaced by the '
              'one the project holds.')
    if len(found) == 1:
        one, when = found[0]
        if ask(T('Project found'),
               T('A project file lies with this material:\n\n  %s\n  '
                 'written %s\n\n%s')
               % (os.path.basename(one), when_written(when), whole),
               T('Open the project')):
            load(one)
            return True
        return False
    lines = ["%s   (%s)" % (os.path.basename(one), when_written(when))
             for one, when in found]
    picked, chosen = QtWidgets.QInputDialog.getItem(
        window, T('Project found'),
        T('Several project files lie with this material. Which one?\n\n%s')
        % whole, lines, 0, False)
    if chosen and picked in lines:
        load(found[lines.index(picked)][0])
        return True
    return False


def find_project_file(file_path):
    """Find the project file for whatever was pointed at.

    Pointing at the folder, or at the wrong file in it, should not
    produce an error, so the neighbourhood is searched too. A project
    file is a dict containing "files" -- the name alone is not enough,
    since plenty of files end in json. Returns (contents, path).
    """
    if not file_path:
        return None, ""
    folder = file_path if os.path.isdir(file_path) else os.path.dirname(file_path)
    attempts = [] if os.path.isdir(file_path) else [file_path]
    try:
        attempts += sorted(os.path.join(folder, n) for n in os.listdir(folder)
                           if n.startswith(PROJECT_PREFIX)
                           and n.lower().endswith(".json"))
    except OSError:
        pass
    for attempt in attempts:
        try:
            with open(attempt, encoding="utf-8") as f:
                loaded = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(loaded, dict) and "files" in loaded:
            return loaded, attempt
    return None, ""

# =====================================================================
#  What comes back out of one
#  --------------------------

def project_files(d):
    """Split the project's file list into what is still there and what is not.

    Returns ([(path, kind), ...], [missing names]). Vanished files are named
    rather than silently dropped.
    """
    present, missing = [], []
    for entry in ((d or {}).get("files") or []):
        file_path = entry.get("path")
        if not file_path:
            continue
        if os.path.exists(file_path):
            present.append((file_path, entry.get("kind") or "audio"))
        else:
            missing.append(os.path.basename(file_path))
    return present, missing


def project_state_read(file_path, elsewhere):
    """Read what is already there and clear leftovers elsewhere.

    Returns the contents of the file at the current location or, if
    there is none, of an earlier one, and beside it the places the
    caller is to clear so that only the one is left.
    """
    found, gone = {}, []
    places = [file_path]
    name = os.path.basename(file_path)
    for place in elsewhere:
        if not place:
            continue
        p = (place if place.lower().endswith(".json")
             else os.path.join(place, name))
        if p not in places:
            places.append(p)
    for p in places:
        try:
            if not os.path.isfile(p):
                continue
            with open(p, encoding="utf-8") as f:
                content = json.load(f) or {}
        except (OSError, ValueError):
            continue
        if not found:
            found = content
        elif isinstance(content, dict):
            # Only extend older state, never overwrite it.
            for s, value in content.items():
                found.setdefault(s, value)
        if os.path.abspath(p) != os.path.abspath(file_path):
            gone.append(p)
    return (found if isinstance(found, dict) else {}), gone


def project_opened_note(target):
    """The note in the log after a project was opened, and what to do next."""
    return T('PROJECT OPENED\n  All entries are back, nothing has been '
             'computed in this session.\n  The output folder holds the '
             'files of the last run:\n  %s\n\n  Three ways from here:\n   '
             ' • below "Open result folder" -- look at the files from '
             'that run,\n    • below "Create Resolve project" -- from '
             "that run's handover file,\n      without computing "
             'anything again,\n    • above "Start" -- compute '
             'everything again and overwrite the files.\n') % target

# =====================================================================
#  What becomes of the work before the application starts again
#  ------------------------------------------------------------

def restart_question(window, state, files, out_folder, report, folder_pick,
                     axis_file, axis_store):
    """Ask what becomes of the work before the application starts again.

    One question for the three ways out -- another language, a new
    version, a new ffmpeg -- so it says restart and not what is behind
    it. True to go on, False to leave everything standing. Nothing is
    asked where nothing has been added.
    """
    if not files:
        return True
    QtWidgets = PROGRAM._qt_widgets()
    box = QtWidgets.QMessageBox(window)
    box.setWindowTitle(T('Restart the application'))
    box.setText(T('The application is about to start again. Shall the '
                  'work be written to a project file first?'))
    box.setInformativeText(
        T('Written, the new window opens the project again and '
          'everything stands where it stood. Not written, it comes up '
          'empty and the files have to be added afresh.'))
    keep = box.addButton(T('Save and restart'),
                         QtWidgets.QMessageBox.AcceptRole)
    drop = box.addButton(T('Restart without saving'),
                         QtWidgets.QMessageBox.DestructiveRole)
    box.addButton(T('Cancel'), QtWidgets.QMessageBox.RejectRole)
    box.exec()
    pressed = box.clickedButton()
    # Nothing of an earlier restart may survive this one: a stale note
    # would open the wrong production in the next window.
    keep_setting("restart_project", "")
    if pressed is drop:
        state["restart_saving"] = False
        return True
    if pressed is not keep:
        return False
    if not out_folder.get():
        # The same handgrip as Save project: the sentence first, because
        # a folder dialog opening by itself does not say why it is there.
        report(T('Save project'),
               T('The project file goes into the output folder, and '
                 'none is chosen yet. Please choose one.'))
        folder_pick()
    # Written here and not left to the way out: one of the three callers
    # replaces the whole process, and nothing here runs after that.
    axis_store(state.get("axis") or {})
    keep_setting("restart_project", axis_file() or "")
    # Written now, so this window writes no more: its clean-up hangs on
    # the application and would write the production again at every quit.
    state["restart_saving"] = False
    return True

# =====================================================================
#  Write it, close it, open it again
#  ---------------------------------

def make_project_file(QtWidgets, window, state, files, log, report, sheet2,
                      out_folder, production_var, start_var, end_var,
                      speech_language, lufs_value, edge_on, multitrack,
                      cut_var, channel_choice, clip_kind_values,
                      audio_use_values, no_join, join_to, remembered,
                      assign_lines, camera_lines, axis_file, axis_store,
                      project_collect, project_move, settings_extend,
                      commonest_folder, folder_show, folder_pick, items_fresh,
                      window_enable, tab_gone, output_show, mode_toggled,
                      player_follow_up, plan_wipe, prework_clean_up,
                      split_stop, split_run, preview_compute,
                      presets_wanted_now, presets_filter,
                      resolve_button_check, result_button_check, write):
    """The project file: write it, close it, open it again.

    One maker and not three functions, because the three are one theme
    and answer each other: project_new is the one list of what belongs
    to a production, and project_open runs it before laying the file's
    answers on top. The window makes them once its log writer and
    resolve_button_check stand, and hands both in.
    """

    def project_write(argv):
        """Store what this run did, so it can be reopened.

        Not the state of every button but what counts: the files, the
        output folder and the command line.
        """
        project_move()
        file_path = axis_file()
        if not file_path:
            return
        # The API key does not belong in a file.
        clean, skip = [], False
        for part in argv[1:]:
            if skip:
                skip = False
                continue
            if part == "--auphonic-api-key":
                skip = True
                continue
            clean.append(part)
        axis_old = (project_collect(file_path).get("timeline") or [])
        d = {"format": FILE_FORMAT,
             "version": VERSION,
             "files": [{"path": p, "kind": a} for p, a in files],
             "timeline": axis_old,
             "timeline_absolute": bool(state.get("axis_absolute")),
             "call": clean}
        settings_extend(d)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=1)
        except OSError as e:
            write(T('  Project file not writable (%s)\n') % e)
            return
        write(as_head(T('PROJECT SAVED\n  %s\n  This run can be opened again '
                        'later -- top left\n  "Open project ..."\n\n') % file_path))

    def project_new():
        """Empty the window, the way a new production starts.

        This is the list of what belongs to a project and what does not,
        and it is the only such list: opening a project runs it first and
        puts the file's answers on top, so the two cannot drift apart.
        Anything left standing here is carried into the next production.
        """
        PROGRAM.measuring_stop(state, [p for p, _a in files],
                               prework_clean_up, split_stop,
                               split_run, plan_wipe)
        state["closing"] = False
        tab_gone(sheet2)
        log.clear()
        state["results"] = []
        state["project_from"] = ""
        window.setWindowTitle(PROGRAM.window_title())
        files[:] = []
        out_folder.set("")
        production_var.set("")
        start_var.set("")
        end_var.set("")
        clip_kind_values.clear()
        audio_use_values.clear()
        no_join.clear()
        join_to.clear()
        channel_choice.clear()
        for name in ("wide_set_aside", "voiced", "projects_offered",
                     "speakers_source_chosen", "forced_own",
                     "result_folder", "resolve_json", "voice_marks",
                     "cut_basis", "run_auphonic") + SPEAKER_STATE:
            state.pop(name, None)
        words_forgotten(state)
        # Emptied, not taken away: the axis is read by name, and a missing
        # key there is a KeyError rather than an empty axis.
        state["axis"] = {}
        state["axis_clock"] = {}
        state["axis_absolute"] = False
        # The timecode belonged to the material that has just gone; left
        # standing, the menu went on offering marks on an empty window.
        state["tc_there"] = False
        state["speakers_local"] = {}
        state["speakers_source"] = ""
        state["speakers_by"] = ByFile()
        state["speakers_count"] = 0
        state["speakers_wanted"] = None
        state["preset_wanted"] = ""
        # Back to what they hold when the program has just started, so a
        # second production begins the way the first one did.
        speech_language.set(PROGRAM.language_of_system())
        lufs_value.set(loudness_last())
        edge_on.set(True)
        multitrack.set(False)
        items_fresh()
        folder_show()
        window_enable()
        resolve_button_check()
        result_button_check()
        preview_compute()

    def project_open(file_path=""):
        file_path = file_path or QtWidgets.QFileDialog.getOpenFileName(
            window, T('Open json project file'),
            out_folder.get() or commonest_folder() or "",
            T('Video Podcast Magic (%s*.json);;JSON files (*.json);;All '
              'files (*)') % PROJECT_PREFIX)[0]
        if not file_path:
            return
        d, file_path = find_project_file(file_path)
        if d is None:
            report('Project',
                   T('This is not a project file, and there is none in the '
                     'same folder.\n\nThe search is for %s*.json -- the '
                     'script writes it into the output folder at start.')
                   % PROJECT_PREFIX)
            return
        complaint = format_complaint(d)
        if complaint:
            report('Project', "%s\n\n%s" % (os.path.basename(file_path),
                                             complaint))
            return
        # Emptied first, by the one list of what belongs to a project,
        # and the file's answers put on top. Two lists would drift.
        project_new()
        state["project_from"] = file_path
        window.setWindowTitle(PROGRAM.window_title(file_path))
        present, missing = project_files(d)
        files[:] = present
        # Before anything is drawn: every file measured once, in
        # parallel. What follows then asks its questions of memory.
        probe_warm([x for x, _ in present])
        for s, value in (d.get("camera_cut") or {}).items():
            if s in cut_var:
                cut_var[s].set(value)
        out_folder.set(d.get("out_folder") or "")
        folder_show()
        production_var.set(d.get("production") or "")
        edge_on.set(bool(d.get("wide_at_edges", True)))
        # Set before the tables are built: the window prefill leaves standing
        # whatever is already there.
        start_var.set(d.get("in_point") or "")
        end_var.set(d.get("out_point") or "")
        # Restore the assignment before the tables are built, or the interface
        # suggests something and overwrites it.
        assign_lines[:] = []
        camera_lines[:] = []
        remembered.clear()
        # Intro, outro and "ignore this video" hang on the file, not
        # the table. Opening a project takes them with it, or two meet.
        if d.get("speech_language"):
            speech_language.set(d["speech_language"])
        # The saved project beats what was chosen last. null is an answer,
        # so the key decides and not the value.
        if "lufs" in d:
            lufs_value.set(d["lufs"])
        # The separations come back before the tables are built, or
        # the voices would be missing until they had run again.
        state["speakers_by"] = speakers_all_from_project(d)
        source, found, _called = speakers_from_project(d)
        state["speakers_local"] = found
        state["speakers_source"] = source or (d.get("speakers_source") or "")
        state["speakers_count"] = int(
            ((d.get("speakers") or {}).get("num_speakers")) or 0)
        speakers_front_pick(state)
        state["speakers_wanted"] = (bool(d["speakers_local"])
                                    if "speakers_local" in d else None)
        no_join.update(d.get("apart") or [])
        join_to.update(d.get("together") or {})
        for p, choice in (d.get("channels") or {}).items():
            channel_choice[p] = {int(k): bool(v) for k, v in choice.items()}
        state["preset_wanted"] = d.get("preset") or ""
        for api_key, value in (d.get("assignment") or {}).items():
            remembered[api_key] = (tuple(value) if isinstance(value, list)
                                   else value)
        voice_keys_carry_source(remembered,
                                state.get("speakers_source") or "")
        if d.get("multitrack"):
            multitrack.set(True)
        preset_list_bring(state, presets_wanted_now, presets_filter)
        items_fresh()
        if multitrack.get():
            # The tick fires nothing where it already stood, so the later
            # tabs are told by hand that the project is open.
            mode_toggled()
        state["results"] = []
        for name in SPEAKER_STATE:
            state.pop(name, None)
        target = out_folder.get()
        # The handover of that project's own run, and only where it names
        # the same cameras -- or the note promises what the button refuses.
        state["resolve_json"] = find_handover_file(
            target, os.path.dirname(os.path.abspath(file_path)),
            ours=[b for b, _n, _own, _own_name in camera_lines])
        if target and os.path.isdir(target) and any(
                n.lower().endswith(VIDEO_SUFFIXES) for n in os.listdir(target)):
            # Results from earlier: the sheet comes along with its buttons,
            # and says where things stand rather than looking like a failure.
            state["result_folder"] = target
            output_show(False)
            log.append_text(as_head(project_opened_note(target)))
        else:
            state["result_folder"] = None
        resolve_button_check()
        result_button_check()
        preview_compute()
        # The boundaries are back, so fetch the file containing them into
        # the player, or the two jump buttons go nowhere after opening.
        player_follow_up(spot_also=True)
        if missing:
            report('Project', T('These files no longer exist:\n  ')
                   + "\n  ".join(missing[:12]))

    def project_open_after_restart():
        """Open again what the window had open when it started again.

        Posted and not done here: this maker runs while the window is
        still being built, and project_open fills tables that do not
        stand yet. The note is forgotten before it is acted on.
        """
        from PySide6 import QtCore
        again = settings().get("restart_project") or ""
        if not again:
            return
        keep_setting("restart_project", "")
        if os.path.isfile(again):
            QtCore.QTimer.singleShot(0, lambda: project_open(again))

    PROGRAM.RESTART_ASK[0] = lambda: restart_question(
        window, state, files, out_folder, report, folder_pick,
        axis_file, axis_store)
    project_open_after_restart()
    return project_write, project_new, project_open
