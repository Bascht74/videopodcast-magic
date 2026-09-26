# -*- coding: utf-8 -*-
"""The run: what is offered before it, the command line, the thread.

A piece of the program, read out of the folder beside the way in by
beside(). It cannot import the file it was cut out of, because that
file is still being read while this one is; the program is handed in
instead, and every name this piece uses out of it is bound below, by
name. What the window still calls out of it, it binds there in turn.
"""

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

# What this piece uses, bound once. Nothing of the window's own and
# nothing the window binds out of another piece: both stand on the
# program only once ui/ has been read, later than this file.

CAMERA_TYPES = PROGRAM.CAMERA_TYPES
T = PROGRAM.T
TN = PROGRAM.TN
as_data_size = PROGRAM.as_data_size
camera_shortfall_lines = PROGRAM.camera_shortfall_lines
json = PROGRAM.json
label_of = PROGRAM.label_of
number_text = PROGRAM.number_text
os = PROGRAM.os
path_key = PROGRAM.path_key
run_argv = PROGRAM.run_argv
size_in_mb = PROGRAM.size_in_mb
slider_argv = PROGRAM.slider_argv
space_summary_lines = PROGRAM.space_summary_lines
speakers_for_run = PROGRAM.speakers_for_run
sys = PROGRAM.sys
targets_to_ask = PROGRAM.targets_to_ask
tempfile = PROGRAM.tempfile
threading = PROGRAM.threading
time = PROGRAM.time
without_own_camera = PROGRAM.without_own_camera


#----------------------------------------------- What a finished run says
# Called by the window's run loop. A test holds that loop still by bending
# the program before the window is read, which a piece read out misses.


def run_done_text(dry):
    """What to say when a run has ended well.

    A dry run measures and writes nothing, so pointing at a result
    folder and offering to build a Resolve project out of it points at
    whatever an earlier run happened to leave there. Measured
    30.8.2026 on an interview: a dry run said "if all is
    right, Create Resolve project builds the project from it" while the
    newest handover in that folder was four days old, from another
    window and another measurement.
    """
    if dry:
        return T('\nMeasured. Nothing was written -- a dry run leaves the '
                 'result folder as it was.\n')
    return T('\nDone. Below, "Open result folder" shows the result.\nIf '
             'all is right, "Create Resolve project" builds the project '
             'from it.\n')


#--------------------------------------------------- Setting a run going
# The summary, the command line and the thread. The window's run loop,
# break-off button and prework key go via PROGRAM, absent at this head.


def user_asker(window, bridge, bridge_emit):
    """How the run asks somebody: the worker waits, the window asks.

    The dialog runs in the window's thread, reached through the bridge;
    the worker thread stands still until the answer is in.
    """
    bridge.question.connect(lambda f: PROGRAM.question_dialog(
        f, window, PROGRAM._qt_widgets(), PROGRAM.label))

    def ask_user(possible, title=T('Question')):
        """A question from the worker thread; the dialog is the window's."""
        f = PROGRAM.Question(possible, title)
        # A run waiting on a person is not stuck, however long it waits.
        with PROGRAM.RUN_VITALS.asking():
            bridge_emit(bridge.question, f)
            f.event.wait()
        return f.choice

    return ask_user


def wait_called_off(state, window):
    """Whether Stop called off a start waiting for camera audio.

    If so the buttons stand as before the press on Start, and the
    camera audio goes on being made: it is not the run's own work.
    """
    if not state.pop("wait_off", False):
        return False
    state["waiting"] = state["confirmed"] = False
    window.start_run.setText(T('Start'))
    window.start_run.setEnabled(True)
    window.preview_button.setEnabled(True)
    window.break_off.setVisible(False)
    return True


def assignment_file(wanted):
    """A new, empty assignment file for one run, and what removes it.

    Hands back (path, discard), ("", discard) when *wanted* is false.
    The file names recordings and people, so it never outlives the run:
    the run's thread removes it at the end, and a window closed while
    the run still goes removes it on the way out.
    """
    path = ""
    if wanted:
        fd, path = tempfile.mkstemp(prefix="vpm_assign_", suffix=".json")
        os.close(fd)

    def discard():
        """Remove the file; whether this call removed it, gone is gone."""
        try:
            os.remove(path)
        except OSError:
            return False
        return True

    if path:
        PROGRAM.atexit.register(discard)
    return path, discard


def make_run_start(QtCore, window, state, model, report, ask, write,
                   bridge, bridge_emit, prework_node, prework_done,
                   prework_queue, prework_run, prework_lock, prework_busy,
                   output_timer, preset_plaintext, without_auphonic,
                   run_step_order):
    """Setting a run going: the summary, the command line, the thread.

    One name for four because they are one theme and answer each other:
    what the summary offers is what start then builds, and both runs --
    the whole one and the Resolve-only one -- end in the same work_loop.
    What the production holds is read off *model*, the footer's buttons
    off *window*, and what follows a start goes out as its signals.
    """
    log = window.output_sheet.log
    only_resolve = window.output_sheet.only_resolve
    result_button_check = window.output_sheet.result_button_check
    start_run, preview_button = window.start_run, window.preview_button
    ask_user = user_asker(window, bridge, bridge_emit)

    def work_loop(argv, discard=None):
        # A separator, so several runs of one session can be told apart
        # in the log.
        try:
            sys.stdout.write(T('\n=== Run %s ===\n\n')
                             % time.strftime("%Y-%m-%d %H:%M:%S"))
            sys.stdout.flush()
        except Exception:
            pass
        # However the run ends, its assignment file goes with it.
        try:
            PROGRAM.gui_run_loop(argv, state, write, ask_user, bridge,
                                 bridge_emit, run_step_order)
        finally:
            if discard:
                discard()
                PROGRAM.atexit.unregister(discard)

    def summary_show(only_look):
        """Before the long run: what is about to happen, one line each.

        Everything in it is known or already measured; it has just not been
        shown anywhere. Aborting here costs nothing.
        """
        audio_files = [p for p, a in model.files if a == "audio"]
        videos_p = [p for p, a in model.files if a == "video"]
        kind_now = lambda p: model.clip_kind_value(p).get()
        content = [p for p in videos_p if kind_now(p) in CAMERA_TYPES]
        edge = [(kind_now(p), os.path.basename(p)) for p in videos_p
                if kind_now(p) not in CAMERA_TYPES]
        duration = model.window_length()
        lines = ["%s, %s%s"
                  % (TN(len(content), '%s camera', '%s cameras')
                     % number_text(len(content), 0),
                     TN(len(audio_files), '%s audio recording',
                        '%s audio recordings')
                     % number_text(len(audio_files), 0),
                     ", " + duration if duration else "")]
        for kind, name in edge:
            lines.append("%s: %s" % (label_of(kind), name))
        who = without_own_camera(
            [(row, nv.get(), cv.get())
             for row, nv, cv in model.assign_lines],
            [(nv.get(), cv.get()) for _k, nv, cv in model.voice_lines],
            state.get("voiced") or ())
        lines += camera_shortfall_lines(who, model.assign_lines,
                                        model.voice_lines)
        if without_auphonic() or not state.get("presets"):
            lines.append(T('Without processing at auphonic.com'))
        else:
            lines.append(T('Processing at auphonic.com with "%s"')
                          % (preset_plaintext() or "?"))
        lines += space_summary_lines(
            model.out_folder.get() or (os.path.dirname(videos_p[0])
                                        if videos_p else ""),
            audio_files, content, bool(model.multitrack.get()),
            model.in_point.get(), model.out_point.get())
        if only_look:
            lines.append("")
            lines.append(T('Dry run: only measuring, nothing written, '
                           'nothing uploaded.'))
        return ask(T('This is what happens next') if not only_look
                      else T('Dry run'),
                      "\n".join(lines),
                      T('Go ahead') if not only_look else T('Measure'))

    def start(only_look=False):
        """Turn what the window holds into a command line and set it going.

        Nothing starts twice or unconfirmed: the summary comes first, and
        while camera audio is being extracted the button counts down and
        calls back here. run_argv builds argv, wishes and questions from the
        interface read once into plain values (testable without a window);
        questions all precede any write. A timer drains the worker thread.
        """

        if state["running"] or not model.files:
            return
        # A name still being typed is settled, as leaving the field would.
        if state.get("name_settle"):
            state["name_settle"]()
        if not state.get("confirmed") and not summary_show(
                only_look):
            return
        # Where the camera audio is needed and not quite there yet, wait for it
        # -- but without freezing the window. Ticked or not: the plan is one.
        if state.get("own_cameras") and prework_busy():
            if state["waiting"]:
                return          # a wait loop is already running
            state["waiting"] = True
            start_run.setEnabled(False)
            preview_button.setEnabled(False)
            # Stop calls the waiting start off; the prework goes on.
            PROGRAM.break_off_arm(window.break_off, run=False)

            def check_again():
                if wait_called_off(state, window):
                    return
                if not prework_busy():
                    state["waiting"] = False
                    state["confirmed"] = True
                    start(only_look)
                    return
                with prework_lock:
                    pending = len(prework_queue) + prework_run["threads"]
                start_run.setText(T('Camera audio, %s to go ...')
                                  % number_text(pending, 0))
                QtCore.QTimer.singleShot(300, check_again)

            check_again()
            return
        state["waiting"] = False
        state["confirmed"] = False
        start_run.setText(T('Start'))
        window.run_starting.emit()
        # A selection with no sound in use never gets this far --
        # what_missing holds the button and says why. The prework is
        # done, and its display has no business in the file list.
        for file_path, (node, original) in list(prework_node.items()):
            try:
                node.setText(2, original)
            except RuntimeError:
                prework_node.pop(file_path, None)
        # The interface read once as plain values; run_argv builds the
        # command line from them, so what a run does can be tested
        # without a window.
        def audio_done_of(row):
            try:
                return prework_done.get(
                    PROGRAM.prework_api_key(row[0]))
            except OSError:
                return None

        own_flag = state.get("own_audio_rows", set())
        values = {
            # The tracks, not the files they came out of: a recorder
            # file holding four channels goes into the run as four.
            "files": model.files_for_run(),
            "clip_kinds": {p: value.get()
                           for p, value in model.clip_kinds.items()},
            "out_folder": model.out_folder.get(),
            "dry_run": bool(only_look),
            "multitrack": bool(model.multitrack.get()),
            # "cut" or "sync"; the window does not start without one.
            "project_type": model.project_type.get(),
            "camera_audio_only": bool(state["camera_audio"]),
            "rows": [{"blocks": list(row),
                        "speakers": nv.get(),
                        "camera_choice": cv.get(),
                        "own_audio": row[0] in own_flag,
                        "from_camera": (own_flag.get(row[0])
                                        if isinstance(own_flag, dict) else ""),
                        "audio_done": audio_done_of(row)}
                       for row, nv, cv in model.assign_lines],
            "cameras": [{"path": p, "name": v.get()}
                        for p, v, _k, _n in model.camera_lines],
            "production": model.production.get(),
            "in_point": model.in_point.get(),
            "out_point": model.out_point.get(),
            "cut": {k: model.cut[k].get() for k in model.cut},
            "wide_at_edges": bool(model.edge_on.get()),
            # The voices this machine has already taken apart. They
            # travel with the run so it need not separate them again.
            "speakers_of": speakers_for_run(state, model.voice_lines),
            # A no given in the window has to reach the run: it would
            # otherwise pick a source itself and separate after all.
            "speakers_wanted": state.get("speakers_wanted"),
            # Which camera each voice belongs to. The run cannot work
            # that out: a voice has no file to be assigned by.
            "voices": [{"name": nv.get().strip(), "camera": cv.get()}
                       for _k, nv, cv in model.voice_lines],
            # Without auphonic.com: the key stays in the field but this run
            # does not see it.
            "key": "" if without_auphonic() else model.key.get(),
            "preset": preset_plaintext(),
            "done_folder": model.done_folder.get(),
            "speech_language": model.speech_language.get().strip(),
            # What each recording's sound holds, by its first block.
            "sound": dict(state.get("sound_holds") or {}),
            "lufs": model.lufs.get(),
            "apart": sorted(model.no_join),
            "together": model.together_now(),
        }
        # Every run carries the plan, ticked or not: one way to the run.
        assign_file, discard = assignment_file(True)
        argv, wishes, messages = run_argv(values, assign_file)
        for kind, title, text, button in messages:
            if kind == "question":
                if not ask(title, text, button):
                    discard()
                    return
            else:
                report(title, text)
                discard()
                return
        if argv is None:
            discard()
            return
        if wishes is not None:
            with open(assign_file, "w", encoding="utf-8") as f:
                json.dump(wishes, f, ensure_ascii=False, indent=1)
        # What is already there and not our own earlier delivery gets
        # asked about first, by the rule the run itself goes by.
        if not only_look:
            already_present = []
            for target in targets_to_ask(
                    [p for p, _v, _k, _n in model.camera_lines],
                    {path_key(p): v.get().strip()
                     for p, v, _k, _n in model.camera_lines},
                    model.out_folder.get(), values["production"].strip()):
                if os.path.exists(target):
                    already_present.append("%s   (%s)"
                                    % (os.path.basename(target),
                                       as_data_size(size_in_mb(target))))
            if already_present and not ask(
                    T('Overwrite files'),
                    T('These files exist already and will be written '
                      'again:\n\n  %s\n\nIs that intended?')
                    % "\n  ".join(already_present[:12]), T('Overwrite')):
                discard()
                return
        window.output_show()
        log.clear()
        state["results"] = []
        start_run.setEnabled(False)
        preview_button.setEnabled(False)
        only_resolve.setEnabled(False)
        start_run.setText(T('Preview running ...') if only_look else T('running ...'))
        state["running"], state["dry_run"] = True, bool(only_look)
        # Held now: the preset box can be turned while the run goes on.
        state["run_auphonic"] = not without_auphonic()
        PROGRAM.break_off_arm(window.break_off)
        # The plan is built, the result buttons follow, and the project
        # file is written -- but not by a dry run, which says it left
        # the output folder as it was: the close writes the hand work.
        window.run_begun.emit(bool(only_look))
        threading.Thread(target=work_loop, args=(argv, discard),
                         daemon=True).start()
        output_timer.start()

    def only_resolve_start_run():
        js = state.get("resolve_json")
        if not js or state["running"]:
            return
        window.output_show()
        log.clear()
        start_run.setEnabled(False)
        preview_button.setEnabled(False)
        only_resolve.setEnabled(False)
        only_resolve.setText(T('Resolve running ...'))
        state["running"] = True
        PROGRAM.break_off_arm(window.break_off)
        result_button_check()
        # The sliders go along: the Resolve part recomputes the cut list
        # and must do it with what stands in the fields now.
        argv = [sys.argv[0], "--resolve-json", js]
        # Where no number stands, the default applies -- nothing is aborted
        # here, the button should do something.
        values = {k: model.cut[k].get() for k in model.cut}
        part, bad = slider_argv(values)
        if bad:
            values[bad] = ""
            part, _s = slider_argv(values)
        argv += part
        if not model.edge_on.get():
            argv += ["--no-wide-edges"]
        threading.Thread(target=work_loop,
                         args=(argv,),
                         daemon=True).start()
        output_timer.start()

    return start, only_resolve_start_run
