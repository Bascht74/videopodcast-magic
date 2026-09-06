# -*- coding: utf-8 -*-
"""The prework: audio, envelopes, channels and tracks fetched in advance.

A piece of the program, read out of the folder beside the way in by
beside(). It cannot import the file it was cut out of, because that
file is still being read while this one is; the program is handed in
instead, and every name this piece uses out of it is bound below, by
name. What the window still calls out of it, it binds there in turn.
"""

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

# What the program has and this piece uses, bound once so that the bar
# and the threads read as they did in the window. Nothing of the
# window's own is here: a name of ui/ is on the program only after ui/
# has been read whole, which is later than this file is read.

SPEAKER_SPLIT_TOGETHER_CORES = PROGRAM.SPEAKER_SPLIT_TOGETHER_CORES
SR = PROGRAM.SR
T = PROGRAM.T
VIDEO_SUFFIXES = PROGRAM.VIDEO_SUFFIXES
_ENV = PROGRAM._ENV
atexit = PROGRAM.atexit
blocks_facts = PROGRAM.blocks_facts
channel_facts_cached = PROGRAM.channel_facts_cached
channel_facts_name = PROGRAM.channel_facts_name
how_many_processors = PROGRAM.how_many_processors
os = PROGRAM.os
path_key = PROGRAM.path_key
pending_prework = PROGRAM.pending_prework
prework_standing = PROGRAM.prework_standing
prework_weight = PROGRAM.prework_weight
probe_has = PROGRAM.probe_has
progress_from_line = PROGRAM.progress_from_line
safe_filename = PROGRAM.safe_filename
shutil = PROGRAM.shutil
split_channels = PROGRAM.split_channels
split_target = PROGRAM.split_target
subprocess = PROGRAM.subprocess
tempfile = PROGRAM.tempfile
threading = PROGRAM.threading
tracks_to_split = PROGRAM.tracks_to_split
unpack_kind = PROGRAM.unpack_kind
video_envelope = PROGRAM.video_envelope
video_facts = PROGRAM.video_facts


#------------------------------------------------- What a piece of work is
# The three small ones the two makers below share: what a fetched file
# is counted under, what one task is counted under, and the unpacking
# itself. They came along because nothing else reads them.


def prework_api_key(file_path):
    s = os.stat(file_path)
    return (path_key(file_path), int(s.st_mtime), s.st_size)


def prework_share_key(file_path, task):
    """What one piece of prework on one file is counted under."""
    return (path_key(file_path), task)

def prework_fetch(file_path, target, report):
    """Extract one file while reporting progress.

    With -progress ffmpeg keeps writing how far it is. Without it the
    display would sit on the same text for minutes.
    """
    try:
        duration = video_facts(file_path)["duration"]
    except Exception:
        duration = 0.0
    # The depth of the source, like every other unpacking. This one
    # matters most of the three: it runs from the window while names
    # are still being typed, and what it leaves behind is handed to the
    # run as audio_done and used as it lies -- so a 16 bit copy made
    # here was what the whole run worked from, however deep the camera
    # recorded.
    cmd = ["ffmpeg", "-v", "error", "-nostats", "-progress", "pipe:1",
           "-i", file_path, "-map", "0:a:0", "-ac", "1", "-ar", str(SR),
           "-c:a", unpack_kind(file_path), "-y", target]
    # Errors into a file, not into a pipe: progress is read from stdout
    # until it ends, and an unread stderr pipe would fill up and stop
    # ffmpeg in the middle -- here in a thread that then never returns.
    fd, log = tempfile.mkstemp(prefix="vpm_pre_", suffix=".txt")
    os.close(fd)
    try:
        with open(log, "wb") as fh:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                    stderr=fh)
            for line in proc.stdout:
                share = progress_from_line(line, duration)
                if share is not None:
                    report(share)
            proc.wait()
        if proc.returncode:
            with open(log, "r", encoding="utf-8", errors="replace") as fh:
                raise RuntimeError(fh.read()[-300:])
    finally:
        try:
            os.unlink(log)
        except OSError:
            pass


#-------------------------------------------------------------- The bar
# What the window thread shows: the box, the bar and the line under it.
# The widgets are made in gui() and handed in.


def make_prework_bar(QtCore, bridge, bridge_emit, plan, prework_box,
                     prework_label, prework_progress_bar, prework_node,
                     prework_discarded, prework_lock, prework_queue,
                     prework_run, prework_shares):
    """The prework bar, and what the working threads report into it.

    Outside gui() because it builds no widget: the box, the bar and the
    label are made there and handed in, and everything here runs in the
    window thread the signal arrives on. The containers are the
    window's own objects and go on being written through. QtCore is a
    parameter because PySide6 is imported inside gui(), and a hoisted
    function reading the name freely would find none.
    """
    def prework_busy():
        with prework_lock:
            return bool(prework_queue) or prework_run["threads"] > 0

    def prework_report(file_path, text, share=None, task=""):
        bridge_emit(bridge.progress, os.path.abspath(file_path), text,
                    -1.0 if share is None else float(share), task)

    def prework_display_text(file_path, text, share, task):
        """Runs in the window thread; Qt passes the signal through.

        Several threads work at once and each reports only its own file. What
        is displayed is therefore not the last message but the state of all
        files together: a percentage per file, with the bar showing the
        average. A file that left the list is not shown at all: its
        thread cannot be broken off mid-write and goes on reporting,
        and every such report would put it back on the bar.
        """
        if path_key(file_path) in prework_discarded:
            return
        if task:
            prework_shares[prework_share_key(file_path, task)] = max(
                0.0, min(1.0, share))
            plan.report("pre:%s:%s" % (task, file_path), share,
                        "%s   %s" % (os.path.basename(file_path), text)
                        if text else os.path.basename(file_path))
        elif share >= 1.0:
            for k in list(prework_shares):
                if k[0] == path_key(file_path):
                    prework_shares[k] = 1.0
            for name in [n for n in plan.order
                         if n.endswith(":" + file_path)]:
                plan.done(name)
        prework_status_show()
        # In the file list above as well; that is where one looks first.
        entry = prework_node.get(file_path)
        if entry:
            node, first_text = entry
            try:
                node.setText(2, "%s   --   %s" % (first_text, text)
                               if text else first_text)
            except RuntimeError:
                prework_node.pop(file_path, None)

    def prework_status_show():
        """Refresh the bar and the list."""
        if not prework_shares:
            prework_box.hide()
            return
        total, lines = prework_standing(prework_shares)
        # The bar only moves forward. Adding a file lowers the average
        # arithmetically, but a bar jumping back looks like a fault even though
        # nothing is lost.
        status = max(prework_run.get("bar", 0), int(round(100 * total)))
        prework_run["bar"] = status
        prework_progress_bar.setValue(status)
        prework_label.setText(T('Prework -- read audio and compute '
                                'envelopes:\n') + "\n".join(lines))
        prework_box.show()
        if total >= 0.999 and not prework_busy():
            prework_shares.clear()
            prework_run["bar"] = 0
            QtCore.QTimer.singleShot(1200, prework_box.hide)
        elif total >= 0.999 and not prework_ask_again.isActive():
            # This runs on a report, and no report follows a thread
            # counting itself out -- so the question is asked once more
            # rather than never. One look is on its way at a time.
            prework_ask_again.start(200)

    prework_ask_again = QtCore.QTimer(prework_box)
    prework_ask_again.setSingleShot(True)
    prework_ask_again.timeout.connect(prework_status_show)

    bridge.progress.connect(prework_display_text)

    return prework_busy, prework_report, prework_status_show


#------------------------------------------------- What the threads do
# The other side of the bar: nothing here touches a widget, and all of
# it runs off the window thread.


def make_prework_tasks(state, bridge, bridge_emit, plan, blocks_of,
                       recording_of, channel_choice, split_files, split_run,
                       prework_report, prework_status_show, prework_done,
                       prework_pending, prework_queue, prework_discarded,
                       prework_lock, prework_run, prework_shares):
    """What the background threads do to one file, and what starts them.

    The other side of the bar above: nothing here touches a widget, and
    all of it runs off the window thread. What it reports goes through
    prework_report, which crosses back over the signal. The three
    containers below are read nowhere else and are made here; the rest
    belong to the window and are handed in.
    """
    PREWORK_THREADS = max(1, min(4, how_many_processors()))
    prework_folder = {"path": None}
    prework_active = set()          # taken off the queue, being worked on

    def prework_where():
        """The folder the prepared files live in, made on first use."""
        with prework_lock:
            if not prework_folder["path"]:
                prework_folder["path"] = tempfile.mkdtemp(prefix="vpm_camaudio_")
                atexit.register(shutil.rmtree, prework_folder["path"], True)
            return prework_folder["path"]

    def prework_target(file_path, api_key):
        folder = prework_where()
        stem = os.path.splitext(os.path.basename(file_path))[0]
        return os.path.join(folder, "%s_%08x.wav"
                            % (safe_filename(stem)[:40],
                               abs(hash(api_key)) & 0xFFFFFFFF))

    def prework_audio_fetch(file_path, api_key):
        if api_key in prework_done:
            prework_report(file_path, "", 1.0, "audio")
            return True
        prework_report(file_path, T('Fetching audio ...'), 0.0, "audio")
        target = prework_target(file_path, api_key)
        try:
            prework_fetch(file_path, target,
                     lambda a, p=file_path: prework_report(
                         p, T('Fetching audio'), a, "audio"))
        except Exception as e:
            prework_report(file_path, T('no audio: %s') % str(e).strip()[:40], 1.0, "audio")
            return False
        # Where the file left the list meanwhile, the work was wasted; clear it
        # away right there rather than leaving it lying about.
        if path_key(file_path) in prework_discarded:
            try:
                os.unlink(target)
            except OSError:
                pass
            return False
        prework_done[api_key] = target
        return True

    def prework_env_curve_build(file_path):
        """Precompute the envelope so the run finds it ready."""
        if (path_key(file_path), 5.0, 4000) in _ENV:
            prework_report(file_path, "", 1.0, "envelope")
            return True
        prework_report(file_path, T('Envelope'), 0.0, "envelope")
        try:
            video_envelope(file_path, report=lambda a, p=file_path: prework_report(
                p, T('Envelope'), a, "envelope"))
        except Exception as e:
            prework_report(file_path, T('Envelope failed: %s')
                      % str(e).strip()[:40], 1.0, "envelope")
            return False
        return True

    def prework_channels_look(file_path):
        """Measure the channels of a multichannel file.

        Reading every channel of an hour of audio takes seconds. In the
        window thread that is a frozen list; here it is a line on the
        bar like everything else.
        """
        prework_report(file_path, T('Looking at the channels'), 0.0,
                       "channels")
        try:
            channel_facts_cached(file_path)
        except Exception as e:
            prework_report(file_path, T('channels not readable: %s')
                           % str(e).strip()[:40], 1.0, "channels")
            return False
        prework_report(file_path, "", 1.0, "channels")
        bridge_emit(bridge.channels_done, os.path.abspath(file_path))
        return True

    def prework_split_make(file_path):
        """Cut a multichannel file into the tracks it will contribute.

        Written as real files, because everything after this point --
        the assignment, the player, the run -- works with files. A
        track that stays whole is not written: the original is the
        track.
        """
        api_key = os.path.abspath(file_path)
        # The decision belongs to the recording, the cutting to the block:
        # every block is cut the same way, and the pieces are regrouped
        # afterwards.
        head = recording_of.get(api_key, api_key)
        try:
            facts = blocks_facts(blocks_of.get(head) or [api_key])
            want = tracks_to_split(file_path, facts,
                                   channel_choice.get(head))
        except Exception as e:
            prework_report(file_path, T('channels not readable: %s')
                           % str(e).strip()[:40], 1.0, "split")
            return False
        if not want:
            split_files[api_key] = []
            prework_report(file_path, "", 1.0, "split")
            bridge_emit(bridge.split_done, api_key)
            return True
        folder = prework_where()
        out = []
        for i, (chs, label) in enumerate(want):
            prework_report(file_path,
                           T('Cutting out track %d of %d')
                           % (i + 1, len(want)),
                           float(i) / len(want), "split")
            target = split_target(file_path, chs, folder)
            # A camera often records at 44.1 kHz while everything else in
            # the run is at 48. Two rates in one mix would not line up, so
            # a piece cut out of a video is brought to the run's rate.
            rate = (SR if os.path.splitext(file_path)[1].lower()
                    in VIDEO_SUFFIXES else None)
            try:
                if not os.path.exists(target) or not os.path.getsize(target):
                    split_channels(file_path, chs, target, rate=rate)
            except Exception as e:
                prework_report(file_path, T('cutting failed: %s')
                               % str(e).strip()[:40], 1.0, "split")
                return False
            out.append((target, label))
        split_files[api_key] = out
        prework_report(file_path, "", 1.0, "split")
        bridge_emit(bridge.split_done, api_key)
        return True

    def prework_drop(entry):
        """Take a task out of the count and off the bar.

        Counted as finished, because nobody else will finish it: a share
        stuck at zero holds the bar back for good. Reported through the
        signal, since the bar belongs to the window thread.
        """
        with prework_lock:
            prework_pending[entry[0]] = prework_pending.get(entry[0], 1) - 1
        prework_report(entry[0], "", 1.0, entry[1])

    def prework_work_loop():
        """One of several threads; takes whatever is still pending."""
        try:
            while True:
                with prework_lock:
                    if not prework_queue:
                        # Counted down inside the same lock. Between
                        # releasing it and a finally the count would be too
                        # high for a moment, and a kick_off landing there
                        # would start no thread at all.
                        prework_run["threads"] -= 1
                        return
                    entry = prework_queue.pop(0)
                    # It is off the queue but not done; without this a
                    # second thread would extract the same file into the
                    # same target while the first is still writing it.
                    prework_active.add(entry)
                file_path, task = entry
                try:
                    if path_key(file_path) in prework_discarded:
                        prework_drop(entry)
                        continue
                    try:
                        api_key = prework_api_key(file_path)
                    except OSError:
                        prework_drop(entry)
                        continue
                    if task == "audio":
                        good = prework_audio_fetch(file_path, api_key)
                    elif task == "channels":
                        good = prework_channels_look(file_path)
                    elif task == "split":
                        good = prework_split_make(file_path)
                    else:
                        good = prework_env_curve_build(file_path)
                    if not good:
                        prework_drop(entry)
                        continue
                    with prework_lock:
                        prework_pending[file_path] = prework_pending.get(
                            file_path, 1) - 1
                        done_with = prework_pending[file_path] <= 0
                    if done_with:
                        # Done means show nothing: a "ready" that stays
                        # only takes up space.
                        prework_report(file_path, "", 1.0)
                finally:
                    with prework_lock:
                        prework_active.discard(entry)
        except BaseException:
            with prework_lock:
                prework_run["threads"] -= 1
            raise

    def prework_kick_off(paths, having_audio=()):
        """Queue the prework: envelopes for all, audio for some."""
        for p in paths:
            prework_discarded.discard(path_key(p))

        def audio_present(a):
            """Report whether the processed audio is already there.

            None means the file cannot even be queried; the run reports that.
            """
            try:
                return prework_api_key(a) in prework_done
            except OSError:
                return None

        fresh = pending_prework(paths, having_audio, audio_present,
                              lambda a: (path_key(a), 5.0, 4000) in _ENV,
                              lambda a: probe_has(channel_facts_name(), a),
                              lambda a: os.path.abspath(a) in split_files)
        with prework_lock:
            for entry in fresh:
                if entry not in prework_queue and entry not in prework_active:
                    prework_queue.append(entry)
                    prework_pending[entry[0]] = prework_pending.get(entry[0], 0) + 1
            # Several threads at once: ffmpeg is barely held up while reading
            # and the files sit on the same disk -- four at a time saturate the
            # machine without getting in each other's way.
            # Measured: the different kinds of work do not slow each
            # other down, and the one real brake on the separation is a
            # full processor. On a small machine the prework therefore
            # goes single file while the separation runs; from four
            # processors up everything runs at once.
            room = (PREWORK_THREADS
                    if (how_many_processors() >= SPEAKER_SPLIT_TOGETHER_CORES
                        or not split_run["busy"]) else 1)
            needed = min(room - prework_run["threads"], len(prework_queue))
            prework_run["threads"] += max(0, needed)
        if not prework_shares:
            prework_run["bar"] = 0
        for p, task in fresh:
            prework_shares.setdefault(prework_share_key(p, task), 0.0)
            # Announced before the work starts: a bar that only learns of
            # a step when that step begins jumps backwards at every one.
            plan.add("pre:%s:%s" % (task, os.path.abspath(p)),
                     prework_weight(p, task), os.path.basename(p))
        prework_status_show()
        for _ in range(max(0, needed)):
            threading.Thread(target=prework_work_loop, daemon=True).start()
        # Bound in gui() below the call that built this, so it cannot be
        # a parameter. Reached the way the assignment tree reaches
        # preview_soon: through state.
        axis = state.get("axis_kick_off")
        if axis:
            axis(list(paths))

    return prework_kick_off
