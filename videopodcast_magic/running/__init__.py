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
camera_audio_pulled = PROGRAM.camera_audio_pulled
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


#-------------------------------------------------- The preview's own run
# The preview is the run, stopped before it writes: a dry run of what the
# window holds, in a thread of the window's and without a word.

# Where the preview's line names its plan before the file is written.
PLAN_PLACE = "<the plan>"
# The preview's runs going in this process, whichever window began them:
# output is one for the process, so no run may begin while one goes.
# "stopped": a run somebody started has pulled their stop (preview_stop).
PREVIEWS = {"alive": 0, "lock": threading.Lock(), "stopped": False}


class QuietHere(object):
    """An output that drops what one thread writes and passes the rest on.

    The preview's run prints as every run does; the window's log and
    file are for the runs somebody started. Only the thread named is
    quiet: the window's own lines go on through it. After off() it lets
    everything through, should anything still hold on to it.
    """

    def __init__(self, inner, ident):
        """Pass on to *inner*; drop what the thread *ident* writes."""
        self.inner, self.ident, self.on = inner, ident, True
        self.tail = ""

    def write(self, text):
        """Keep the quiet thread's last words, hand the rest on."""
        if self.on and threading.get_ident() == self.ident:
            self.tail = (self.tail + str(text))[-2000:]
            return len(text)
        return self.inner.write(text)

    def last_line(self):
        """The last line the quiet thread wrote: why a run stopped."""
        lines = [x.strip() for x in PROGRAM.re.sub(
            "\x1b\\[[0-9;]*m|[\x01-\x08]", "", self.tail).splitlines()]
        return ([x for x in lines if x] or [""])[-1]

    def flush(self):
        """Flush what is handed on."""
        try:
            self.inner.flush()
        except Exception:
            return

    def isatty(self):
        """Never a terminal: nothing is coloured for nobody."""
        return False

    def off(self):
        """Let everything through from now on."""
        self.on = False


def quiet_run(argv, key, over=None):
    """The preview's run in this thread, quiet: returns (code, why).

    A dry run of *argv* keeping its handover under *key*; with *over*, a
    handover of other cut numbers, the cut stage alone. What this thread
    writes goes nowhere and a question is refused; the limit: a thread
    the run starts itself writes on as usual.
    """
    old = sys.stdout, sys.stderr, PROGRAM.ASK_SINK
    quiet = [QuietHere(old[0], threading.get_ident()),
             QuietHere(old[1], threading.get_ident())]
    sys.stdout, sys.stderr = quiet
    PROGRAM.ASK_SINK = preview_asks_nothing
    code, why = 1, ""
    try:
        if over is not None:
            code = 0 if PROGRAM.handover_recut(over, argv, key) else 1
        else:
            ap = PROGRAM.build_argument_parser()
            args = ap.parse_args(PROGRAM.time_values_joined(list(argv[1:])))
            args._handover_key = key
            code = PROGRAM.run_from_command_line(args, ap)
    except SystemExit as e:
        code, why = (e.code, "") if isinstance(e.code, int) else (1, str(
            e.code or ""))
    except Exception as e:
        code, why = 1, str(e)
    finally:
        for q in quiet:
            q.off()
        sys.stdout, sys.stderr, PROGRAM.ASK_SINK = old
    return code or 0, (why or (quiet[0].last_line() or quiet[1].last_line()
                               if code else ""))


def preview_asks_nothing(possible, title=""):
    """Nobody is asked from the preview's run: it stops instead."""
    raise RuntimeError(title)


def preview_request(state, model, prework_busy, values_of):
    """The run the preview stands for: its line, plan and key.

    A dry run of *values_of*() without auphonic.com. None while a run,
    the camera audio or the time axis is busy (state["preview_waiting"]:
    the watchdog asks again); a line that cannot be built gives its why.
    """
    # A run going anywhere in this process holds the output: none begins.
    waiting = bool(state["running"] or state.get("waiting")
                   or PROGRAM.OUTPUT_SINK is not None
                   or state.get("starting") or state.get("axis_running")
                   or (state.get("own_cameras") and prework_busy()))
    state["preview_waiting"] = waiting and bool(model.files)
    if waiting or not model.files:
        return None
    # Nothing of auphonic.com: the cut is worked out on the raw sound.
    values = dict(values_of(), key="", preset="", done_folder="")
    argv, wishes, messages = run_argv(values, PLAN_PLACE)
    errors = [text for kind, _t, text, _b in messages if kind == "error"]
    if argv is None or errors:
        return {"why": errors[0] if errors else ""}
    plan = json.loads(json.dumps(wishes))
    words = PROGRAM.line_words(argv, plan)[0]
    return {"key": PROGRAM.handover_key(words, plan), "argv": list(argv),
            "words": words, "plan": plan, "wishes": wishes}


def preview_stop():
    """Stop the preview's runs going: a run somebody started comes first.

    Start, Dry run and Create Resolve project wait for them, and a
    preview's run can be for settings already changed again. Their stop
    is the run's own, pulled and taken back once the last of them ended,
    so what else measures in the window meanwhile meets it too, briefly.
    """
    # Under the lock: a run ending in between would take it back first.
    with PREVIEWS["lock"]:
        if PREVIEWS["alive"]:
            PREVIEWS["stopped"] = True
            PROGRAM.stop_asked_for()


def preview_run(request, done):
    """The preview's run: the dry run, or the cut stage over *over*.

    In a thread of its own and quiet; *done* gets (key, code, why), and
    (None, 0, "") where preview_stop ended it: nothing ran, nothing is
    kept. The plan goes into a file of its own for the run, as Start's
    does, and never outlives it.
    """
    path, discard = assignment_file(True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(request["wishes"], f, ensure_ascii=False, indent=1)
    argv = [path if w == PLAN_PLACE else w for w in request["argv"]]
    # Counted from here, not from the thread: a Start pressed in between
    # has to find it.
    with PREVIEWS["lock"]:
        PREVIEWS["alive"] += 1

    def work():
        """The run itself, then the file gone and *done* told."""
        code, why = 1, ""
        try:
            if not PREVIEWS["stopped"]:
                code, why = quiet_run(argv, request["key"],
                                      request.get("over"))
        finally:
            discard()
            PROGRAM.atexit.unregister(discard)
            with PREVIEWS["lock"]:
                PREVIEWS["alive"] -= 1
                stopped = PREVIEWS["stopped"]
                if stopped and not PREVIEWS["alive"]:
                    PREVIEWS["stopped"] = False
                    PROGRAM.RUN_STOP["wanted"] = False
                    PROGRAM.RUN_STOP["at"] = ""
        done((None, 0, "") if stopped else (request["key"], code, why))

    threading.Thread(target=work, daemon=True).start()


def window_values(state, model, prework_done, without_auphonic,
                  preset_plaintext, only_look):
    """What the window holds, read once as plain values for run_argv.

    One reading for the three that start a run -- Start, Dry run and
    the preview's own -- so what a run does can be tested without a
    window. *model* holds the production, *state* the window's own.
    """
    def audio_done_of(row):
        """The camera audio made for *row* ahead of time, or None."""
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
        # Key and print too: one voice heard again may share a name.
        "voices": [{"name": nv.get().strip(), "camera": cv.get(),
                    "key": k, "heard": getattr(nv, "heard", None)}
                   for k, nv, cv in model.voice_lines],
        # Without auphonic.com: the key stays in the field but this run
        # does not see it.
        "key": "" if without_auphonic() else model.key.get(),
        "preset": preset_plaintext(),
        "done_folder": model.done_folder.get(),
        "speech_language": model.speech_language.get().strip(),
        # Where the window's own transcript is kept, once it is there:
        # the dry run and the run cut by it rather than by none (E-554).
        "words_of": PROGRAM.window_words_reference(state,
                                                   model.assign_lines),
        # What each recording's sound holds, by its first block.
        "sound": dict(state.get("sound_holds") or {}),
        "lufs": model.lufs.get(),
        "apart": sorted(model.no_join),
        "together": model.together_now(),
    }
    return values


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
        duration = model.window_length(state.get("axis"),
                                       state.get("mark_on_clock"))
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
            audio_files, content,
            model.in_point.get(), model.out_point.get())
        if only_look:
            lines.append("")
            lines.append(T('Dry run: only measuring, nothing written, '
                           'nothing uploaded.'))
        return ask(T('This is what happens next') if not only_look
                      else T('Dry run'),
                      "\n".join(lines),
                      T('Go ahead') if not only_look else T('Measure'))

    def held():
        """Whether a run waits: for camera audio, or the preview's run."""
        return bool((state.get("own_cameras") and prework_busy())
                    or state.get("preview_running") or PREVIEWS["alive"])

    state["preview_request"] = lambda: preview_request(
        state, model, prework_busy, lambda: window_values(
            state, model, prework_done, without_auphonic, preset_plaintext,
            True))
    state["preview_run"] = preview_run

    def start(only_look=False):
        """start_now, with no preview's run let in while it goes.

        Its questions wait in the window's own loop, where the preview's
        timer runs too; a run the preview began then would write into
        this one's log.
        """
        state["starting"] = True
        try:
            return start_now(only_look)
        finally:
            state["starting"] = False

    def start_now(only_look=False):
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
        # The preview's run is waited for too: it is a run of its own.
        if held():
            # The preview's run is stopped, not waited out.
            preview_stop()
            if state["waiting"]:
                return          # a wait loop is already running
            state["waiting"] = True
            start_run.setEnabled(False)
            preview_button.setEnabled(False)
            # Stop calls the waiting start off; the prework goes on.
            PROGRAM.break_off_arm(window.break_off, run=False)

            def check_again():
                """Start once nothing is waited for; else say what is."""
                if wait_called_off(state, window):
                    return
                if not held():
                    state["waiting"] = False
                    state["confirmed"] = True
                    start(only_look)
                    return
                with prework_lock:
                    pending = len(prework_queue) + prework_run["threads"]
                start_run.setText(T('Preview running ...')
                                  if state.get("preview_running")
                                  or PREVIEWS["alive"] else
                                  T('Camera audio, %s to go ...')
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
        values = window_values(state, model, prework_done, without_auphonic,
                               preset_plaintext, only_look)
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
        # What the bar plans for: the run pulls a camera's audio wherever
        # the plan makes it a track, tick or no tick.
        state["run_camera_audio"] = camera_audio_pulled(wishes)
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
        # One run at a time in this window, the preview's included.
        if state.get("preview_running") or PREVIEWS["alive"]:
            preview_stop()
            QtCore.QTimer.singleShot(300, only_resolve_start_run)
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
