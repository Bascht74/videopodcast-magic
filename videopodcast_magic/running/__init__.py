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

# What the program has and this piece uses, bound once so that the run
# reads as it did in the window. Nothing of the window's own is here,
# and nothing the window binds out of another piece: both stand on the
# program only once ui/ has been read whole, later than this file is.

CAMERA_TYPES = PROGRAM.CAMERA_TYPES
T = PROGRAM.T
TN = PROGRAM.TN
as_data_size = PROGRAM.as_data_size
camera_shortfall_lines = PROGRAM.camera_shortfall_lines
json = PROGRAM.json
label_of = PROGRAM.label_of
number_text = PROGRAM.number_text
os = PROGRAM.os
run_argv = PROGRAM.run_argv
size_in_mb = PROGRAM.size_in_mb
slider_argv = PROGRAM.slider_argv
space_summary_lines = PROGRAM.space_summary_lines
speakers_for_run = PROGRAM.speakers_for_run
sys = PROGRAM.sys
tempfile = PROGRAM.tempfile
threading = PROGRAM.threading
time = PROGRAM.time
without_own_camera = PROGRAM.without_own_camera


#----------------------------------------------- What a finished run says
# Called by the run loop, which stayed in the window: a test holds that
# loop still by bending it on the program before the window is read,
# and such a bend reaches the window but not a piece read out of it.


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
# The summary, the command line and the thread. What lives in the
# window itself -- the run loop, the break-off button, the prework's
# key -- goes through PROGRAM: at this file's head it is not there yet.


def make_run_start(QtCore, state, files, log, report, ask, write, ask_user,
                   bridge, bridge_emit, out_folder, production_var,
                   start_var, end_var, speech_language, lufs_value,
                   done_folder, key_var, cut_var, edge_on, multitrack,
                   clip_kind_values, clip_kind_value, no_join, together_now,
                   assign_lines, camera_lines, voice_lines, prework_node,
                   prework_done, prework_queue, prework_run, prework_lock,
                   prework_busy, start_run, preview_button, only_resolve,
                   break_off, output_timer, files_for_run, window_length,
                   preset_plaintext, without_auphonic, output_show,
                   buttons_check, result_button_check, run_plan_build,
                   run_step_order, project_write):
    """Setting a run going: the summary, the command line, the thread.

    Outside gui() because the four are one theme and answer each other:
    what the summary offers is what start then builds, and both runs --
    the whole one and the Resolve-only one -- end in the same work_loop.
    What the window holds comes in as an argument and keeps its name
    inside. The call sits below the footer, the project file and the
    output timer, three of those arguments.
    """

    def work_loop(argv):
        # A separator, so several runs of one session can be told apart
        # in the log.
        try:
            sys.stdout.write(T('\n=== Run %s ===\n\n')
                             % time.strftime("%Y-%m-%d %H:%M:%S"))
            sys.stdout.flush()
        except Exception:
            pass
        PROGRAM.gui_run_loop(argv, state, write, ask_user, bridge,
                             bridge_emit, run_step_order)

    def summary_show(only_look):
        """Before the long run: what is about to happen, one line each.

        Everything in it is known or already measured; it has just not been
        shown anywhere. Aborting here costs nothing.
        """
        audio_files = [p for p, a in files if a == "audio"]
        videos_p = [p for p, a in files if a == "video"]
        kind_now = lambda p: clip_kind_value(p).get()
        content = [p for p in videos_p if kind_now(p) in CAMERA_TYPES]
        edge = [(kind_now(p), os.path.basename(p)) for p in videos_p
                if kind_now(p) not in CAMERA_TYPES]
        duration = window_length()
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
             for row, nv, cv in assign_lines],
            [(nv.get(), cv.get()) for _k, nv, cv in voice_lines],
            bool(multitrack.get()), state.get("voiced") or ())
        lines += camera_shortfall_lines(who, assign_lines, voice_lines)
        if without_auphonic() or not state.get("presets"):
            lines.append(T('Without processing at auphonic.com'))
        else:
            lines.append(T('Processing at auphonic.com with "%s"')
                          % (preset_plaintext() or "?"))
        lines += space_summary_lines(
            out_folder.get() or (os.path.dirname(videos_p[0])
                                  if videos_p else ""),
            audio_files, content, bool(multitrack.get()),
            start_var.get(), end_var.get())
        if only_look:
            lines.append("")
            lines.append(T('Dry run: only measuring, nothing written, '
                           'nothing uploaded.'))
        return ask(T('This is what happens next') if not only_look
                      else T('Dry run'),
                      "\n".join(lines),
                      T('Go ahead') if not only_look else T('Measure'))

    def start(only_look=False):
        if state["running"] or not files:
            return
        if not state.get("confirmed") and not summary_show(
                only_look):
            return
        # Where the camera audio is needed and not quite there yet, wait for it
        # -- but without freezing the window.
        if multitrack.get() and state.get("own_cameras") and prework_busy():
            if state["waiting"]:
                return          # a wait loop is already running
            state["waiting"] = True
            start_run.setEnabled(False)
            preview_button.setEnabled(False)

            def check_again():
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
        buttons_check()
        # The "Cameras only" question stood here until 25.8.2026: it
        # fired on the rule that made every camera a track by itself, and
        # that rule is gone. A selection with no sound in use never gets
        # this far now -- what_missing holds the button and says why.
        # The prework is done, and its display has no business in the file list
        # any more.
        for file_path, (node, original) in list(prework_node.items()):
            try:
                node.setText(2, original)
            except RuntimeError:
                prework_node.pop(file_path, None)
        # Collect what is in the interface once as plain values; run_argv
        # builds the command line from them. The whole decision about what a
        # run does sits there, and can be tested without opening a window.
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
            "files": files_for_run(),
            "clip_kinds": {p: value.get() for p, value in clip_kind_values.items()},
            "out_folder": out_folder.get(),
            "dry_run": bool(only_look),
            "multitrack": bool(multitrack.get()),
            "camera_audio_only": bool(state["camera_audio"]),
            "rows": [{"blocks": list(row),
                        "speakers": nv.get(),
                        "camera_choice": cv.get(),
                        "own_audio": row[0] in own_flag,
                        "from_camera": (own_flag.get(row[0])
                                        if isinstance(own_flag, dict) else ""),
                        "audio_done": audio_done_of(row)}
                       for row, nv, cv in assign_lines],
            "cameras": [{"path": p, "name": v.get()}
                        for p, v, _k, _n in camera_lines],
            "production": production_var.get(),
            "in_point": start_var.get(),
            "out_point": end_var.get(),
            "cut": {k: cut_var[k].get() for k in cut_var},
            "wide_at_edges": bool(edge_on.get()),
            # The voices this machine has already taken apart. They
            # travel with the run so it need not separate them again.
            "speakers_of": speakers_for_run(state, voice_lines),
            # A no given in the window has to reach the run: it would
            # otherwise pick a source itself and separate after all.
            "speakers_wanted": state.get("speakers_wanted"),
            # Which camera each voice belongs to. The run cannot work
            # that out: a voice has no file to be assigned by.
            "voices": [{"name": nv.get().strip(), "camera": cv.get()}
                       for _k, nv, cv in voice_lines],
            # Without auphonic.com: the key stays in the field but this run
            # does not see it.
            "key": "" if without_auphonic() else key_var.get(),
            "preset": preset_plaintext(),
            "done_folder": done_folder.get(),
            "speech_language": speech_language.get().strip(),
            "lufs": lufs_value.get(),
            "apart": sorted(no_join),
            "together": together_now(),
        }
        assign_file = ""
        if multitrack.get() or state.get("speakers_local"):
            fd, assign_file = tempfile.mkstemp(prefix="vpm_assign_",
                                           suffix=".json")
            os.close(fd)
        argv, wishes, messages = run_argv(values, assign_file)

        def discard():
            if assign_file:
                try:
                    os.remove(assign_file)
                except OSError:
                    pass

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
        # What is already there gets overwritten, so show what first.
        if not only_look:
            already_present = []
            for p, v, _k, _n in camera_lines:
                folder = out_folder.get() or os.path.dirname(p)
                target = os.path.join(folder, (v.get().strip()
                                             or os.path.splitext(
                                                 os.path.basename(p))[0])
                                    + ".mov")
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
        output_show()
        log.clear()
        state["results"] = []
        start_run.setEnabled(False)
        preview_button.setEnabled(False)
        only_resolve.setEnabled(False)
        start_run.setText(T('Preview running ...') if only_look else T('running ...'))
        state["running"], state["dry_run"] = True, bool(only_look)
        # Held now: the preset box can be turned while the run goes on.
        state["run_auphonic"] = not without_auphonic()
        PROGRAM.break_off_arm(break_off)
        run_plan_build()
        result_button_check()
        project_write(argv)      # the dry run too: same hand work
        threading.Thread(target=work_loop, args=(argv,), daemon=True).start()
        output_timer.start()

    def only_resolve_start_run():
        js = state.get("resolve_json")
        if not js or state["running"]:
            return
        output_show()
        log.clear()
        start_run.setEnabled(False)
        preview_button.setEnabled(False)
        only_resolve.setEnabled(False)
        only_resolve.setText(T('Resolve running ...'))
        state["running"] = True
        result_button_check()
        # Send the sliders from above along: the Resolve part recomputes the
        # cut list and should do so with what is in the fields now, not with
        # the values of the last run.
        argv = [sys.argv[0], "--resolve-json", js]
        # Where no number stands, the default applies -- nothing is aborted
        # here, the button should do something.
        values = {k: cut_var[k].get() for k in cut_var}
        part, bad = slider_argv(values)
        if bad:
            values[bad] = ""
            part, _s = slider_argv(values)
        argv += part
        if not edge_on.get():
            argv += ["--no-wide-edges"]
        threading.Thread(target=work_loop,
                         args=(argv,),
                         daemon=True).start()
        output_timer.start()

    return start, only_resolve_start_run
