# -*- coding: utf-8 -*-
"""The processing: the tracks go to auphonic.com and come back.

A piece of the program, read by beside(). It cannot import the file it
was cut out of, so the program is handed in and every name used out of
it is bound below. No key stands in here: it is asked for where it is
needed and goes into the call to curl, never into a log line, a file
or a message.
"""

# beside() puts the program here before this file is read.
PROGRAM = PROGRAM

# What this piece uses out of the program, bound once. One name is
# missing, and the block under the list says which and why.

T = PROGRAM.T
as_data_size = PROGRAM.as_data_size
as_good = PROGRAM.as_good
as_head = PROGRAM.as_head
as_hms = PROGRAM.as_hms
as_warn = PROGRAM.as_warn
ask_choice = PROGRAM.ask_choice
channel_count = PROGRAM.channel_count
channel_text = PROGRAM.channel_text
check_preset = PROGRAM.check_preset
gui_log = PROGRAM.gui_log
json = PROGRAM.json
kept_channels = PROGRAM.kept_channels
load_api_key = PROGRAM.load_api_key
number_text = PROGRAM.number_text
os = PROGRAM.os
re = PROGRAM.re
report_findings = PROGRAM.report_findings
safe_filename = PROGRAM.safe_filename
show_progress = PROGRAM.show_progress
similarity = PROGRAM.similarity
step_begin = PROGRAM.step_begin
subprocess = PROGRAM.subprocess
sys = PROGRAM.sys
tempfile = PROGRAM.tempfile
time = PROGRAM.time
widest_track = PROGRAM.widest_track

# OUTPUT_SINK is the one: the window sets it on the program object, a
# write the pieces are never told about, so a copy here would answer
# None and the progress line would reach nobody.


AUPHONIC = "https://auphonic.com"


def api_key_source(args=None):
    """Return (the API key, where it came from).

    Read in order: command line, environment, credential store. Which of
    the three answered travels with the key, or a complaint names the
    store for a key that came from elsewhere.
    """
    given = getattr(args, "auphonic_key", "") if args is not None else ""
    if given:
        return given, "argument"
    from_env = os.environ.get("AUPHONIC_TOKEN")
    if from_env:
        return from_env, "environment"
    kept = load_api_key() or ""
    return kept, ("store" if kept else "")


def key_refused_note(origin, error):
    """Say a key was refused, and name where that key came from."""
    if origin == "environment":
        return T('The key from AUPHONIC_TOKEN is not accepted: %s') % error
    if origin == "store":
        return T('The stored key is not accepted: %s') % error
    return T('auphonic.com does not accept the key: %s') % error


def api_key_from_anywhere(args):
    """Return the API key: command line, environment, credential store."""
    key = api_key_source(args)[0]
    if not key:
        raise RuntimeError(T('No API key. Pass --auphonic-api-key KEY, set '
                             'AUPHONIC_TOKEN or have it remembered once in '
                             'the interface. The key is in the Auphonic '
                             'account settings.'))
    return key.strip()


def _curl_call(key, arguments, output_binary=False, progress=False):
    """Run curl with the key in a config file rather than in argv.

    In argv it would stand in the process list for the length of the call.
    """
    fd, conf = tempfile.mkstemp(prefix="auph_", suffix=".conf")
    os.close(fd)
    leftovers = []
    closing, running = [], []
    try:
        # The one file that holds the key in plain text; the finally
        # below removes it whatever happened. Owner-readable only.
        os.chmod(conf, 0o600)
        # curl reads this file as configuration, so the key goes in as
        # a value: a quotation mark or a line break in it would start a
        # directive of its own. curl escapes with a backslash.
        safe = (str(key).replace("\\", "\\\\").replace('"', '\\"')
                .replace("\r", "").replace("\n", ""))
        with open(conf, "w", encoding="utf-8") as f:
            f.write('header = "Authorization: bearer %s"\n' % safe)
        if progress:
            # curl's own bar has no percentage and cannot be indented,
            # so its table is read and our bar drawn from it. The answer
            # goes to a file: an unread pipe fills up and stalls it.
            fd, body = tempfile.mkstemp(prefix="auph_", suffix=".out")
            os.close(fd)
            leftovers.append(body)
            answer_file = open(body, "wb")
            closing.append(answer_file)
            # Only the connection is limited, never the transfer: an
            # upload of gigabytes takes as long as it takes, but a
            # server that never answers must not hold the run.
            proc = subprocess.Popen(["curl", "-S", "-L",
                                     "--connect-timeout", "15",
                                     "--config", conf]
                                    + arguments,
                                    stdout=answer_file,
                                    stderr=subprocess.PIPE)
            running.append(proc)
            text = progress if isinstance(progress, str) else T('Transfer')
            rest, last_percent, last_time = "", -1, 0.0
            said = []            # everything that is not a progress line
            show_progress(text, 0.0)
            while True:
                piece = proc.stderr.read(64)
                if not piece:
                    break
                rest += piece.decode("utf-8", "replace")
                parts = re.split(r"[\r\n]", rest)
                rest = parts.pop()
                for line in parts:
                    m = re.match(r"\s*(\d{1,3})\s+\S+\s+\d", line)
                    if not m:
                        # curl -S says here why it gave up.
                        if line.strip():
                            said.append(line.strip())
                        continue
                    pct = min(100, int(m.group(1)))
                    now = time.time()
                    if pct != last_percent and now - last_time > 0.2:
                        show_progress(text, pct / 100.0)
                        last_percent, last_time = pct, now
            proc.wait()
            answer_file.close()
            with open(body, "rb") as fh:
                off = fh.read()
            try:
                os.unlink(body)
            except OSError:
                pass
            show_progress(text, 1.0)
            if PROGRAM.OUTPUT_SINK:
                PROGRAM.OUTPUT_SINK("\n")
            else:
                sys.stdout.write("\n")
            if rest.strip():
                said.append(rest.strip())
            p = subprocess.CompletedProcess(
                proc.args, proc.returncode, off,
                "\n".join(said[-20:]).encode("utf-8", "replace"))
        else:
            # Long enough for a call that fetches a list of presets,
            # short enough to look alive. Without it the button waits.
            p = subprocess.run(["curl", "-sS", "-L",
                                "--connect-timeout", "15",
                                "--max-time", "60",
                                "--config", conf] + arguments,
                               capture_output=True)
    finally:
        # A broken-off transfer leaves curl writing into a file nobody
        # reads: stopped here, or it downloads gigabytes for nothing.
        for child in running:
            if child.poll() is None:
                try:
                    child.kill()
                    child.wait(timeout=5)
                except Exception:
                    pass
        for handle in closing:
            try:
                handle.close()
            except Exception:
                pass
        # The config file holds the key, so it goes whatever happened,
        # and a failure to remove it must not replace the real error.
        # What cannot be removed is overwritten: no file keeps the key.
        for path in [conf] + leftovers:
            try:
                os.unlink(path)
            except FileNotFoundError:
                # Already gone is the goal, not a failure: the branch
                # below would make a fresh empty file at that path.
                continue
            except OSError:
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write("\n")
                except OSError:
                    pass
    if p.returncode:
        error = (p.stderr or b"").decode("utf-8", "replace")[-800:]
        # A return code is a name, not an amount: plain digits to look up.
        raise RuntimeError(error or T('curl ended with %d') % p.returncode)
    return p.stdout if output_binary else p.stdout.decode("utf-8", "replace")


def _parse_json(text):
    try:
        return json.loads(text)
    except ValueError:
        raise RuntimeError(T('Response was not JSON: %s') % text[:300])


def key_complaint(key):
    """What is wrong with this key before it is sent, or "".

    Only what can be told without asking anybody. No length and no
    character set -- a guessed format would turn away a key that works.
    """
    if not key:
        return T('There is no key.')
    if key != key.strip():
        return T('The key has a space or a line break at one end.')
    if any(c.isspace() for c in key):
        return T('The key is broken in the middle by a space or a line break.')
    if any(ord(c) < 32 or ord(c) == 127 for c in key):
        return T('The key has a character in it that cannot be typed.')
    return ""


def list_presets(key):
    """Fetch the stored presets: (name, uuid, Multitrack or None).

    ``minimal_data=1`` for two reasons: without it the answer is capped
    at ten presets whatever the limit says, and it is the form carrying
    ``is_multitrack``. An unclassified preset comes back as None --
    unknown, not ordinary.
    """
    d = _parse_json(_curl_call(key, [
        AUPHONIC + "/api/presets.json?minimal_data=1&limit=100"]))
    if d.get("status_code") not in (200, None):
        raise RuntimeError(T('Auphonic reports %s: %s')
                           % (d.get("status_code"), d.get("error_message")))
    items = []
    for p in (d.get("data") or []):
        mark = p.get("is_multitrack")
        items.append((p.get("preset_name") or p.get("name") or T('unnamed'),
                      p.get("uuid") or "",
                      None if mark is None else bool(mark)))
    return items


def preset_fits_mode(mark, multitrack):
    """Does a preset belong in the list for this mode?

    Only a preset we can place is thrown out: an unknown kind is shown
    rather than dropped, hiding one being worse than one entry too many.
    """
    return mark is None or bool(mark) == bool(multitrack)


def presets_for_mode(key, multitrack):
    """Return only the presets that match the mode.

    A multitrack preset in a plain production, or the other way round,
    makes a production Auphonic refuses to start.
    """
    return [(n, u, m) for n, u, m in list_presets(key)
            if preset_fits_mode(m, multitrack)]


def print_presets(key, multitrack=False):
    items = presets_for_mode(key, multitrack)
    if not items:
        print(T('No Multitrack preset found in the account.') if multitrack
              else T('No Singletrack preset found in the account.'))
        return 0
    print("Presets:")
    # The number in front is typed back below; %2d keeps a column.
    for i, (name, _, _) in enumerate(items, 1):
        print("  %2d  %s" % (i, name))
    return 0


def choose_preset(key, wanted, multitrack=False, lufs=None,
                   anyway=False):
    """Resolve a preset name to its UUID, asking if there is a choice.

    Both entry paths run through here, so this is where the preset is
    checked against the run. A mismatch raises before anything is uploaded.
    """
    items = presets_for_mode(key, multitrack)
    if not items:
        every = list_presets(key)
        if every:
            raise RuntimeError(
                (T('No Multitrack preset in the account. Only these: %s')
                 if multitrack else
                 T('No Singletrack preset in the account. Only these: %s'))
                % ", ".join(n for n, _, _ in every))
        raise RuntimeError(T('No presets stored in the account. One can be '
                             'created in the web interface.'))
    def done(uuid, name):
        # Checked whatever the loudness is set to: whether a Multitrack
        # preset carries a track template decides whether the tracks
        # come back processed at all.
        findings = check_preset(key, uuid or name, name, lufs, multitrack)
        if report_findings(findings, T('does the preset fit the run?'),
                          anyway):
            raise RuntimeError(T('preset does not fit the run'))
        return uuid or name, name

    if wanted:
        for name, uuid, _ in items:
            if wanted.lower() in (name.lower(), uuid.lower()):
                return done(uuid, name)
        for name, uuid, _m in list_presets(key):
            if wanted.lower() in (name.lower(), uuid.lower()):
                raise RuntimeError(
                    (T('%r is a Singletrack preset, and a Multitrack one '
                       'is needed.') if multitrack else
                     T('%r is a Multitrack preset, and a Singletrack one '
                       'is needed.')) % name)
        print(T('No preset is called %r.') % wanted)
    print(T('Which Auphonic preset should process this file?'))
    # Same list, same reason: this is the number to be typed back.
    for i, (name, uuid, _) in enumerate(items, 1):
        print("  %2d  %s" % (i, name))
    if not sys.stdin.isatty():
        raise RuntimeError(T('No preset given, no input possible. Choose '
                             'one of the above with --auphonic-preset NAME.'))
    while True:
        answer = input(T('  Number (empty = cancel): ')).strip()
        if not answer:
            raise RuntimeError(T('cancelled'))
        if answer.isdigit() and 1 <= int(answer) <= len(items):
            name, uuid, _ = items[int(answer) - 1]
            return done(uuid, name)
        # The bound on what may be typed, not a count of presets.
        print(T('  Please give a number between 1 and %d.') % len(items))


def preset_box_widget(QtWidgets, state, fetch):
    """The class for the preset list, which fetches itself when opened.

    Opening the list is the moment somebody wants to know what
    auphonic.com has; before that nothing is asked. Fetching takes a
    moment, so it says so rather than opening on the one entry it has --
    and whoever receives them opens it again. A factory, not a class.
    """

    class PresetBox(QtWidgets.QComboBox):

        def showPopup(self):
            if not state.get("presets") and not state.get("presets_busy"):
                state["presets_open_after"] = True
                fetch()
                if state.get("presets_busy"):
                    self.addItem(T('fetching from auphonic.com ...'), "")
                    self.model().item(self.count() - 1).setEnabled(False)
            QtWidgets.QComboBox.showPopup(self)

    return PresetBox


def preset_list_bring(state, fetch, apply_wish):
    """Bring the preset list up after a project was opened.

    The list is otherwise only fetched when somebody opens the box --
    so a project carrying a preset finds nothing to put it in, and the
    box says "without auphonic.com", which the project did not ask for.
    """
    if (state.get("preset_wanted") and not state.get("presets")
            and not state.get("presets_busy")):
        fetch()
    else:
        apply_wish()


def preset_box_fill(box, entries, state, none_value):
    """Put the rows into the preset list and pick what is wanted.

    Without auphonic.com stays selected until somebody picks: landing on
    the first entry of an arriving list would spend credit because a list
    came. Where the list cannot hold the wish -- key refused, no net --
    it stays in *state*, or the stand-in would be stored.
    """
    before_value = box.currentData() or ""
    box.blockSignals(True)
    box.clear()
    for value, text, pickable in entries:
        box.addItem(text, value)
        if not pickable:
            box.model().item(box.count() - 1).setEnabled(False)
    box.setCurrentIndex(0)
    box.setEnabled(True)
    wanted = state.get("preset_wanted") or before_value or ""
    if wanted:
        i = box.findData(wanted)
        if i >= 0:
            box.setCurrentIndex(i)
            state.pop("preset_wanted", None)
        elif wanted != none_value:
            state["preset_wanted"] = wanted
            # Not in the list yet -- being fetched, or refused. Its value
            # stays "without auphonic.com", so a run spends nothing.
            box.addItem(T('%s -- being checked') % wanted, none_value)
            box.model().item(box.count() - 1).setEnabled(False)
            box.setCurrentIndex(box.count() - 1)
    box.blockSignals(False)
    # What the box was asked for and what it settled on. A wish left
    # standing means the list could not hold it.
    gui_log("presets: %d in the list, wanted %r, before %r -> %r%s"
             % (box.count(), state.get("preset_wanted") or "", before_value,
                box.currentData(),
                "" if not state.get("preset_wanted") else " (not placed)"))


def preset_entries(presets, multitrack_on, none_label, none_value):
    """The rows of the preset list: (value, text, can be picked).

    The first row is not a preset but the decision to run without
    auphonic.com, always there. Three states, not the same: *presets*
    None means nobody has looked; an empty list is an account with no
    preset; a full list with nothing fitting is all the other mode.
    """
    kind = (T('Multitrack mode') if multitrack_on
            else T('Singletrack mode'))
    rows = [(none_value, none_label, True)]
    fitting = [(n, mt) for n, _u, mt in (presets or [])
               if preset_fits_mode(mt, multitrack_on)]
    for name, mark in fitting:
        # The bracket names the mode, so it may only stand where the mode
        # is known: an unclassified preset gets its own name and no more.
        rows.append((name, "%s  (%s)" % (name, kind) if mark is not None
                     else name, True))
    if presets is None or fitting:
        return rows
    if presets:
        none_yet, no_multi, no_single = preset_missing_rows()
        rows.append(("", no_multi if multitrack_on else no_single, False))
    else:
        rows.append(("", preset_missing_rows()[0], False))
    return rows


def preset_missing_rows():
    """The three sentences a list with nothing to pick can carry.

    In one place because two callers need them: the list puts one in, and
    the field has to be wide enough for the widest. Order: no preset at
    all, no Multitrack one, no Singletrack one. They say "of your own"
    and not "in the account" -- all we ever see is what somebody made.
    """
    return (T('No preset of your own -- create one on auphonic.com'),
            T('No Multitrack preset of your own -- create one'),
            T('No Singletrack preset of your own -- create one'))


def preset_mode_note(preset_list, multitrack_on):
    """What to say where the list came back and shows nothing.

    The presets are filtered by the mode, and an account without one of
    the kind in use leaves the list at its single entry -- which reads
    like a key that was refused, and is not. Returns (sentence or "",
    the presets that fit).
    """
    fitting = [n for n, _u, mt in (preset_list or [])
               if preset_fits_mode(mt, multitrack_on)]
    if not preset_list or fitting:
        return "", fitting
    return ((T('The key is good. Of the %s presets in the account none '
               'is a Multitrack one, so the list stays empty.')
             if multitrack_on else
             T('The key is good. Of the %s presets in the account none '
               'is a Singletrack one, so the list stays empty.'))
            % number_text(len(preset_list), 0), fitting)


# Output files with these endings are text about the audio, not audio.
TRANSCRIPT_SUFFIXES = (".json", ".srt", ".vtt", ".txt", ".html", ".xml")


# What may be sent back when a production is updated. A query answers
# with more -- size, checksum, download address -- and sending those
# back describes a file that does not exist yet.
OUTPUT_FILE_KEYS = ("format", "ending", "bitrate", "mono_mixdown",
                    "split_on_chapters", "suffix", "filename",
                    "outgoing_services")


def output_file_wish(f):
    """Reduce an output file entry to what may be asked for again."""
    return {k: f[k] for k in OUTPUT_FILE_KEYS if f.get(k) is not None}


def wishes_then_start(key, uuid, stereo=False):
    """Set what the simple API cannot, then start the production.

    The simple API takes a file and a preset and nothing else, so keeping
    two channels is settled in one further call -- the one that starts
    the production, which without "action=start" waits for exactly this.
    """
    if not stereo:
        return
    d = _parse_json(_curl_call(
        key, [AUPHONIC + "/api/production/%s.json" % uuid]))
    already = ((d.get("data") or {}).get("output_files") or [])
    wish = [output_file_wish(f) for f in already]
    request = {}
    if stereo:
        # The preset folds the mixdown to one channel, and with a
        # stereo recording that cannot be undone afterwards.
        for f in wish:
            if f.get("mono_mixdown"):
                f["mono_mixdown"] = False
    request["output_files"] = wish
    request["action"] = "start"
    fd, js = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        with open(js, "w", encoding="utf-8") as f:
            json.dump(request, f, ensure_ascii=False)
        answer = _parse_json(_curl_call(
            key, ["-X", "POST", "-H", "Content-Type: application/json",
                  AUPHONIC + "/api/production/%s.json" % uuid, "-d", "@" + js]))
    finally:
        os.unlink(js)
    if answer.get("status_code") not in (200, 201, None):
        raise RuntimeError(T('Auphonic will not take the settings: '
                             '%s') % (answer.get("error_message")
                                      or answer.get("form_errors")))
    if stereo:
        print(T('  Two channels requested -- the recording is stereo'))


def run_single_production(audio, preset, presetname, key, target_folder,
                  wait_s=7200, dry_run=False, title=None):
    """Upload a file, start the production, wait, download the result."""
    title = title or os.path.splitext(os.path.basename(audio))[0]
    size = os.path.getsize(audio) / 1e6
    stereo = kept_channels(audio) == 2
    # What the file really has, not what the run keeps: kept_channels
    # answers one for anything above two, which would call a four
    # channel recording mono in the log. Only the wording changes.
    try:
        really = int(channel_count(audio))
    except (OSError, ValueError, RuntimeError):
        really = kept_channels(audio)
    print(as_head(T('PROCESSING AT AUPHONIC.COM:')))
    print(T('  Preset:  %s') % presetname)
    print(T('  File:    %s (%s, %s)') % (os.path.basename(audio),
                              as_data_size(size),
                              channel_text(really)))
    if really > 2:
        print(as_warn(T('  More than two channels go to auphonic.com as '
                        'one: the fold is only switched off for stereo.\n'
                        '  Where the channels are meant to stay apart, '
                        'cut the file into tracks first.')))
    if dry_run:
        print(T('  (measuring only: nothing uploaded)\n'))
        return None
    # With a stereo recording the production is created but not started:
    # switching the mono fold off is a second call.
    later = stereo
    make = ["-X", "POST", AUPHONIC + "/api/simple/productions.json",
            "-F", "preset=%s" % preset,
            "-F", "title=%s" % title,
            "-F", "input_file=@%s" % audio]
    if not later:
        make.insert(-2, "-F")
        make.insert(-2, "action=start")
    answer = _curl_call(key, make,
                   progress=T('Uploading %s') % os.path.basename(audio))
    d = _parse_json(answer)
    if d.get("status_code") not in (200, 201, None):
        raise RuntimeError(T('Auphonic reports %s: %s')
                           % (d.get("status_code"), d.get("error_message") or
                              d.get("form_errors") or answer[:300]))
    data = d.get("data") or d
    uuid = data.get("uuid")
    if not uuid:
        raise RuntimeError(T('no production id in the response: %s') % answer[:300])
    wishes_then_start(key, uuid, stereo)
    print(T('  Production running (%s)') % uuid)

    started = time.time()
    last, horizon = None, 150.0        # a guess: two and a half minutes,
                                       # doubling from there
    end = started + wait_s
    # The same waiting the multitrack production does, in one function.
    p = wait_for_production(key, uuid, wait_s)

    files = p.get("output_files") or []
    if not files:
        raise RuntimeError(T('production finished, but no output file'))
    def rank(f):
        # Lossless before lossy, in case the preset delivers several.
        nm = (f.get("filename") or "").lower()
        return {".wav": 1, ".flac": 2, ".aiff": 3}.get(os.path.splitext(nm)[1], 9)
    best = sorted(files, key=rank)[0]
    name = best.get("filename") or (title + ".wav")
    url = best.get("download_url")
    if not url:
        raise RuntimeError(T('no download address for %s') % name)
    os.makedirs(target_folder, exist_ok=True)
    target = os.path.join(target_folder, name)
    _curl_call(key, ["-o", target, url],
          progress=T('Downloading %s') % name)
    if os.path.getsize(target) < 1000:
        raise RuntimeError(T('downloaded file is only %s bytes')
                           % number_text(os.path.getsize(target), 0))
    print(T('  Result: %s (%s) -- stays next to the video file\n')
          % (os.path.basename(target), as_data_size(os.path.getsize(target) / 1e6)))
    fetch_text_outputs(key, files, target_folder, skip=best)
    return target


def fetch_text_outputs(key, files, target_folder, skip=None):
    """Fetch what a production wrote about the audio, not the audio.

    Transcript, subtitles, chapter marks: paid for either way.
    """
    fetched = set()
    for f in files or []:
        if f is skip:
            continue
        name = f.get("filename") or ""
        url = f.get("download_url")
        if not name or not url:
            continue
        if not name.lower().endswith(TRANSCRIPT_SUFFIXES):
            continue
        # Two outputs of one name land in the same file, and the second
        # download overwrites the first though both were paid for.
        if name in fetched:
            print(T('  %s is there already -- not fetched twice') % name)
            continue
        fetched.add(name)
        target = os.path.join(target_folder, name)
        try:
            _curl_call(key, ["-o", target, url],
                       progress=T('Downloading %s') % name)
            print(T('  Also fetched: %s') % name)
        except Exception as e:
            print(T('  %s could not be fetched: %s') % (name, e))


# What must not go from a preset into a production: identifiers, times,
# states. Everything else is adopted, fields added later included.
PRESET_READ_ONLY = (
    "uuid", "preset_name", "creation_time", "change_time", "status",
    "status_string", "error_status", "error_message", "warning_status",
    "warning_message", "image", "thumbnail", "length", "length_timestring",
    "waveform_image", "status_page", "edit_page", "start_allowed",
    "change_allowed", "in_review", "chapters", "preset", "is_multitrack")


def read_preset(key, uuid):
    """Fetch one preset in full."""
    d = _parse_json(_curl_call(key, [AUPHONIC + "/api/preset/%s.json" % uuid]))
    if d.get("status_code") not in (200, None):
        raise RuntimeError(T('Preset not readable: %s') % d.get("error_message"))
    return d.get("data") or d


def find_output_format(key, find, avoid=()):
    """Find an Auphonic output format by its name.

    The identifiers are undocumented, so they are looked up rather than
    guessed: /api/info/output_files.json lists them all.
    """
    try:
        d = _parse_json(_curl_call(key, [AUPHONIC + "/api/info/output_files.json"]))
    except Exception:
        return None
    kinds = d.get("data")
    if isinstance(kinds, dict):
        kinds = [dict(v, format=k) for k, v in kinds.items()
                 if isinstance(v, dict)]
    if not isinstance(kinds, list):
        kinds = []
    for a in kinds:
        if not isinstance(a, dict):
            continue
        text = " ".join(str(a.get(f) or "")
                        for f in ("format", "string", "name")).lower()
        if all(word in text for word in find) and not any(word in text
                                                      for word in avoid):
            return {"format": a.get("format"),
                    "ending": a.get("ending") or ""}
    return None


def missing_outputs(existing, wanted):
    """Return the output formats still missing from a production.

    Auphonic appends rather than replaces on update: a format sent twice
    stands in the production twice, billed and computed twice.
    """
    def fingerprint(e):
        return (str((e or {}).get("format") or "").lower(),
                str((e or {}).get("suffix") or "").lower(),
                bool((e or {}).get("mono_mixdown")))
    present = set()
    for e in (existing or []):
        if not isinstance(e, dict):
            continue
        present.add(fingerprint(e))
        # The response carries the format but no suffix; the file name
        # has it. With no channel count stated both readings count as
        # present -- sending one twice is the worse mistake.
        name = str(e.get("filename") or "")
        stem = os.path.splitext(name)[0]
        kind = str(e.get("format") or "").lower()
        said = e.get("mono_mixdown")
        both = (bool(said),) if said is not None else (True, False)
        if "_" in stem:
            suffix = "_" + stem.rsplit("_", 1)[1].lower()
            for mono in both:
                present.add((kind, suffix, mono))
        elif e.get("suffix"):
            # Configured but not rendered: no file name, its own suffix.
            for mono in both:
                present.add((kind, str(e["suffix"]).lower(), mono))
    absent = []
    for e in wanted:
        if fingerprint(e) in present:
            continue
        present.add(fingerprint(e))
        absent.append(e)
    return absent


def master_output_format(key, stereo=False):
    """Request the finished mixdown as well -- 24 bit WAV.

    Not as audio but as a yardstick for how loud our own mix should end
    up, and it costs no extra credit. One channel would be half the
    download, but with a stereo track it would sit decibels off the mix.
    """
    kind = (find_output_format(key, ("wav-24bit",))
           or find_output_format(key, ("wav",), avoid=("zip", "tracks")))
    if not kind or not kind.get("format"):
        return None
    entry = {"format": kind["format"], "ending": kind.get("ending") or "wav",
               "mono_mixdown": not stereo, "suffix": "_master"}
    return entry


def build_multitrack_request(preset, title, names, base_name, key=None,
                             stereo=False):
    """Build the production request from the preset that was read.

    The preset cannot be sent along: Auphonic then merges its tracks
    with ours and the production stays incomplete. So it is read and
    adopted except what we set; its first track's settings apply to all.
    """
    request = {k: v for k, v in preset.items() if k not in PRESET_READ_ONLY}
    template = {}
    for track in (preset.get("multi_input_files") or []):
        template = dict(track.get("algorithms") or {})
        break
    request["is_multitrack"] = True
    request["multi_input_files"] = [
        {"type": "multitrack", "id": n, "algorithms": dict(template)}
        for n in names]
    # The single tracks only; the mixdown is built from them afterwards.
    request["output_files"] = [{"format": "tracks", "ending": "wav.zip"}]
    if key:
        # The finished mixdown comes along as a yardstick for the mix.
        mst = master_output_format(key, stereo)
        if mst:
            request["output_files"].append(mst)
            print(as_good(T('  Finished mixdown requested as the yardstick '
                            '(%s)')
                          % mst["format"]))
            if stereo:
                print(T('  Two channels, because one track is stereo'))
    request["metadata"] = dict(preset.get("metadata") or {})
    request["metadata"]["title"] = title
    request["output_basename"] = base_name
    return request


def find_production_by_title(key, title):
    """Return the Auphonic production with this title, or None."""
    d = _parse_json(_curl_call(key, [AUPHONIC + "/api/productions.json?limit=50"]))
    wanted_name = (title or "").strip().lower()
    for p in (d.get("data") or []):
        if ((p.get("metadata") or {}).get("title") or "").strip().lower()\
                == wanted_name:
            return p
    return None


def print_production(p):
    """Print what a production already contains."""
    tracks = p.get("multi_input_files") or []
    uploaded = [(x.get("id"), x.get("input_file")) for x in tracks]
    done = [f.get("filename") for f in (p.get("output_files") or [])
              if f.get("download_url")]
    print("  Status:      %s" % (p.get("status_string") or "?"))
    print(T('  Created:     %s') % (p.get("creation_time") or "?")[:19].replace(
        "T", " "))
    if uploaded:
        print(T('  Uploaded:'))
        for fingerprint, file in uploaded:
            print("    %-20s %s" % (fingerprint, file or T('-- nothing --')))
    if done:
        print(T('  Results:'))
        for n in done:
            small = (n or "").lower()
            if small.endswith(".zip"):
                what = T('the individual tracks, packed')
            elif small.endswith(".wav"):
                what = T('the finished mixdown')
            else:
                what = ""
            print("    %-46s %s" % (n, what))
    else:
        print(T('  Results:     none'))
    # Without the tracks nothing works and without the mixdown the
    # loudness has no yardstick; unsaid, "reuse" becomes a dead end.
    small = [(n or "").lower() for n in done]
    has_zip = any(n.endswith(".zip") for n in small)
    has_master = any(n.endswith(".wav") for n in small)
    missing = []
    if not has_zip:
        missing.append(T('the individual tracks'))
    if not has_master:
        missing.append(T('the mixdown as the yardstick'))
    if missing:
        # Always the production at auphonic.com, not the local disk.
        print(T('  Missing:     %s') % ", ".join(missing))
    return all(d for _, d in uploaded) and bool(uploaded), has_zip, missing


def update_production(key, uuid, request):
    """Bring an existing production's settings up to the preset.

    Uploaded files stay in place -- Auphonic matches tracks by
    identifier -- so another preset costs no upload and no credit.
    """
    fd, js = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    without_output = dict(request)
    try:
        with open(js, "w", encoding="utf-8") as f:
            json.dump(without_output, f, ensure_ascii=False)
        answer = _parse_json(_curl_call(key, ["-X", "POST", "-H",
                                    "Content-Type: application/json",
                                    AUPHONIC + "/api/production/%s.json" % uuid,
                                    "-d", "@" + js]))
    finally:
        os.unlink(js)
    if answer.get("status_code") not in (200, 201, None):
        raise RuntimeError(T('Change rejected: %s')
                           % (answer.get("error_message")
                              or answer.get("form_errors")))
    return answer.get("data") or {}


def read_production(key, uuid):
    """Fetch the current state of a production."""
    return (_parse_json(_curl_call(key, [AUPHONIC + "/api/production/%s.json" % uuid]))
            .get("data") or {})


def update_track(key, uuid, track_id, algorithms):
    """Change the settings of a single track.

    Auphonic matches a track only through its own URL: the track list
    sent to the production appends instead -- three tracks become six.
    """
    fd, js = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        with open(js, "w", encoding="utf-8") as f:
            json.dump({"id": track_id, "type": "multitrack",
                       "algorithms": algorithms}, f, ensure_ascii=False)
        answer = _parse_json(_curl_call(key, [
            "-X", "POST", "-H", "Content-Type: application/json",
            AUPHONIC + "/api/production/%s/multi_input_files/%s.json"
            % (uuid, track_id), "-d", "@" + js]))
    finally:
        os.unlink(js)
    if answer.get("status_code") not in (200, 201, None):
        return str(answer.get("error_message")
                   or answer.get("form_errors") or T('rejected'))
    return None


def update_all_tracks(key, uuid, wanted, existing):
    """Bring the tracks of an existing production up to the preset.

    *wanted* is the track list from our request, one identifier and the
    preset settings per track. Returns (changed, unchanged, errors).
    """
    present = dict((str(t.get("id")), t) for t in
              (existing.get("multi_input_files") or []))
    error, changed, same = [], [], []
    for entry in wanted:
        fingerprint = str(entry.get("id"))
        want = entry.get("algorithms") or {}
        old = present.get(fingerprint)
        if old is None:
            error.append(T('%s: not there') % fingerprint)
            continue
        if dict(old.get("algorithms") or {}) == dict(want):
            same.append(fingerprint)
            continue
        bad = update_track(key, uuid, fingerprint, want)
        if bad:
            error.append("%s: %s" % (fingerprint, bad))
        else:
            changed.append(fingerprint)
    return changed, same, error


def run_multitrack_production(key, preset_uuid, title, tracks, target_folder,
                        wait_s=7200, dry_run=False, carry_on=None):
    """Create a multitrack production, upload, wait, fetch the tracks.

    Returns {speaker name: path of the processed file}.
    """
    step_begin("auphonic")
    names = [track["name"] for track in tracks]
    base = safe_filename(title)
    print(as_head(T('PROCESSING AT AUPHONIC.COM (MULTITRACK):')))
    print(T('  Production:  %s') % title)
    print(T('  Tracks:      %s') % ", ".join(names))
    total = sum(os.path.getsize(track["axis"]) for track in tracks) / 1e6
    print(T('  To upload:   %s') % as_data_size(total))
    if dry_run:
        print(T('  (measuring only: nothing uploaded)\n'))
        return {}

    preset = read_preset(key, preset_uuid)
    if not preset.get("is_multitrack"):
        raise RuntimeError(T('%r is not a Multitrack preset')
                           % preset.get("preset_name"))
    stereo = widest_track([track["axis"] for track in tracks]) == 2
    request = build_multitrack_request(preset, title, names, base, key,
                                       stereo)

    # --- does this production already exist?
    existing = find_production_by_title(key, title)
    if existing:
        return reuse_production(key, existing, request, preset,
                                          tracks, names, target_folder, base,
                                          wait_s, carry_on)
    fd, js = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        with open(js, "w", encoding="utf-8") as f:
            json.dump(request, f, ensure_ascii=False)
        answer = _parse_json(_curl_call(key, ["-X", "POST", "-H",
                                    "Content-Type: application/json",
                                    AUPHONIC + "/api/productions.json",
                                    "-d", "@" + js]))
    finally:
        os.unlink(js)
    if answer.get("status_code") not in (200, 201, None):
        raise RuntimeError(T('Auphonic reports %s: %s')
                           % (answer.get("status_code"),
                              answer.get("error_message")
                              or answer.get("form_errors")))
    p = answer.get("data") or {}
    uuid = p.get("uuid")
    if not uuid:
        raise RuntimeError(T('no production id in the response'))
    created = [x.get("id") for x in (p.get("multi_input_files") or [])]
    if sorted(created) != sorted(names):
        raise RuntimeError(T('Auphonic created different tracks than '
                             'requested: %s instead of %s') % (created, names))
    print(T('  Production running (%s)') % uuid)

    upload_args = ["-X", "POST", AUPHONIC + "/api/production/%s/upload.json" % uuid]
    for track in tracks:
        upload_args += ["-F", "%s=@%s" % (track["name"], track["axis"])]
    d = _parse_json(_curl_call(
        key, upload_args,
        progress=T('Uploading %s tracks')
        % number_text(len(tracks), 0)))
    absent = [x.get("id") for x in ((d.get("data") or {}).get(
        "multi_input_files") or []) if not x.get("input_file")]
    if absent:
        raise RuntimeError(T('These tracks got no file: %s')
                           % ", ".join(absent))

    _curl_call(key, ["-X", "POST",
                AUPHONIC + "/api/production/%s/start.json" % uuid])
    p = wait_for_production(key, uuid, wait_s)

    return download_results(key, p, names, target_folder, base)


def download_results(key, p, names, target_folder, base):
    """Download a finished production: the single tracks."""
    zip_file = None
    for f in (p.get("output_files") or []):
        if (f.get("filename") or "").lower().endswith(".zip"):
            zip_file = f
            break
    if not zip_file:
        raise RuntimeError(T('Production finished, but no ZIP with the '
                             'individual tracks'))
    cache = tracks_folder(target_folder)
    target = os.path.join(cache, zip_file.get("filename"))
    _curl_call(key, ["-o", target, zip_file.get("download_url")],
          progress=T('Downloading %s') % zip_file.get("filename"))
    # Whatever else the preset produces belongs here: it is paid for.
    already = set()
    for f in (p.get("output_files") or []):
        name = f.get("filename") or ""
        if not name or not f.get("download_url") or f is zip_file:
            continue
        if name.lower() in already:
            # Two output kinds of one file name: the second overwrites.
            print(T('  %s is in the production twice -- fetched once.')
                  % name)
            continue
        already.add(name.lower())
        extra_file = os.path.join(cache, name)
        try:
            _curl_call(key, ["-o", extra_file, f["download_url"]],
                  progress=T('Downloading %s') % name)
        except Exception as e:
            print(T('  %s could not be fetched: %s') % (name, e))
    return match_zip_entries_to_tracks(target, names, target_folder)


def ask_reuse_production(complete, has_result, default_value=None, missing=()):
    """Ask what should happen to the existing production."""
    possible = []
    # Reuse only where all of it is there: no statistics, no camera cut.
    if has_result and not missing:
        possible.append(("result", T('take the existing result (nothing '
                                     'computed, nothing paid)')))
    if complete:
        possible.append(("rerun", T('recompute with the chosen preset -- '
                                    'the files stay\n       where they are, '
                                    'costs no credit')))
    possible.append(("upload", T('upload everything again and recompute -- '
                                 'this costs credit')))
    possible.append(("abort", T('cancel')))
    return ask_choice(possible, T('What should happen with it?'),
                      T('This production already exists'), default_value)


def rename_tracks(tracks, names, request, new_one):
    """Rename the speakers to the track names used by the production.

    By position, and everywhere at once: the tracks drive file names,
    statistics and camera assignment, and the request goes to Auphonic.
    """
    for track, old, fresh in zip(tracks, list(names), new_one):
        print("    %-22s -> %s" % (old, fresh))
        track["name"] = fresh
    names[:] = list(new_one)
    for entry, fresh in zip(request.get("multi_input_files") or [], new_one):
        entry["id"] = fresh


def ask_track_names(old, fresh, default_value=None):
    """Ask what to do when the production uses different track names."""
    print(T('\n  The tracks are named differently there:'))
    # The track number names the track; the counts below are quantities.
    for i, name in enumerate(fresh, 1):
        print(T('    Track %d  %-22s (here: %s)')
              % (i, name, old[i - 1] if i <= len(old) else "--"))
    if len(old) != len(fresh):
        print(T('  There are %s tracks there and %s here -- that does not '
                'match.') % (number_text(len(fresh), 0),
                             number_text(len(old), 0)))
        possible = [("upload", T('upload everything again and recompute -- '
                                 'this costs credit')),
                    ("abort", T('cancel'))]
    else:
        possible = [("adopt", T('take the names from there and carry on '
                                'with them --\n       no upload, costs '
                                'nothing')),
                    ("upload", T('keep our names and upload everything '
                                 'again -- this costs\n       credit')),
                    ("abort", T('cancel'))]
    return ask_choice(possible, T('What should happen with it?'),
                      T('Different track names'), default_value)


def reuse_production(key, existing, request, preset, tracks,
                               names, target_folder, base, wait_s, carry_on):
    """Reuse a production that already exists.

    Only the upload costs credit, so another preset means recomputing.
    """
    print(T('\n  THERE IS ALREADY A PRODUCTION WITH THIS NAME'))
    complete, has_result, missing = print_production(existing)
    # "reuse" here means: recompute, upload nothing.
    choice = ask_reuse_production(complete, has_result,
                            "rerun" if carry_on == "adopt" else carry_on,
                            missing)
    uuid = existing.get("uuid")
    if choice == "abort":
        raise RuntimeError(
            T('Stopped. Choose another production name -- then a new '
              'production\n  is created -- or pick one of the other options.'))

    if choice == "rerun" and not complete:
        raise RuntimeError(
            T('Files are missing there -- without a new upload nothing can '
              'be computed.\n  With --auphonic-resume upload the script '
              'uploads again; this costs credit.'))
    upload_again = (choice == "upload")
    if not upload_again:
        # There the tracks keep their upload names, the ZIP is named
        # after them, and Auphonic matches through it. Where they differ
        # we adopt theirs or upload again, never unasked.
        there = [x.get("id") for x in
                (existing.get("multi_input_files") or [])]
        if sorted(there) != sorted(names):
            second = ask_track_names(list(names), there, carry_on)
            if second == "abort":
                raise RuntimeError(
                    T('Stopped. Nothing was uploaded and nothing computed.'))
            if second == "adopt":
                print(T('  The names from there are adopted:'))
                rename_tracks(tracks, names, request, there)
            else:
                upload_again = True
                choice = "upload"

    if choice == "result":
        if not has_result:
            raise RuntimeError(T('This production has no result yet.'))
        if missing:
            raise RuntimeError(
                T('The existing result is unusable: %s is missing there. '
                  'With --auphonic-resume rerun it can be recomputed '
                  'without uploading anything.') % T(' and ').join(missing))
        print(T('  Existing result adopted -- nothing computed, nothing paid.'))
        p = (_parse_json(_curl_call(key, [AUPHONIC + "/api/production/%s.json" % uuid]))
             .get("data") or {})
        return download_results(key, p, names, target_folder, base)

    if not upload_again:
        print(T('  Note: this computes with the files uploaded at the '
                'time. They carry\n  the time window and the alignment of '
                'that day. Where the In point, the Out point\n  or the '
                'measured '
                'position differ now, the return check measures the\n  '
                'difference and moves the tracks into place.'))
    print(T('  Settings brought to preset %r')
          % (preset.get("preset_name") or "?"))
    change = dict(request)
    if not upload_again:
        # The track list stays out: Auphonic appends it on update rather
        # than matching -- three tracks become six. They follow one by
        # one below, each through its own URL.
        change.pop("multi_input_files", None)
        change.pop("is_multitrack", None)
        # The same for the output files, or Auphonic computes them twice.
        absent_ones = missing_outputs(existing.get("output_files"),
                                     request.get("output_files") or [])
        if absent_ones:
            change["output_files"] = absent_ones
            print(T('  Added: %s')
                  % ", ".join(str(e.get("format")) for e in absent_ones))
        else:
            change.pop("output_files", None)
            print(T('  All needed output files already exist.'))
        left_over = [t.get("id") for t in (existing.get("multi_input_files")
                                        or []) if t.get("id") not in names]
        if left_over:
            print(as_warn(T('  Caution: the production holds further '
                            'tracks (%s). They go into the\n  mix -- please '
                            'delete them at auphonic.com.') % ", ".join(str(u) for u in left_over)))
    update_production(key, uuid, change)
    if not upload_again:
        # The track list could not go above; its own URL per track does.
        changed, same, bad = update_all_tracks(
            key, uuid, request.get("multi_input_files") or [], existing)
        parts = []
        if changed:
            parts.append(T('%s brought to the preset')
                         % number_text(len(changed), 0))
        if same:
            parts.append(T('%s were already right')
                         % number_text(len(same), 0))
        print(T('  Tracks: %s') % (", ".join(parts) or T('nothing to do')))
        for line in bad:
            print(as_warn(T('  Caution: track %s -- it keeps its settings.') % line))
        after = read_production(key, uuid)
        now = after.get("multi_input_files") or []
        if len(now) > len(existing.get("multi_input_files") or []):
            raise RuntimeError(
                T('Tracks were added while changing (now %s). That makes '
                  'the mix\n  wrong. Please delete the tracks without a '
                  'file at auphonic.com.') % number_text(len(now), 0))
    if upload_again:
        print(T('  The files are uploaded again -- this costs credit.'))
        upload_args = ["-X", "POST",
                AUPHONIC + "/api/production/%s/upload.json" % uuid]
        for track in tracks:
            upload_args += ["-F", "%s=@%s" % (track["name"], track["axis"])]
        d = _parse_json(_curl_call(key, upload_args,
                        progress=T('Uploading %s tracks')
                        % number_text(len(tracks), 0)))
        absent = [x.get("id") for x in ((d.get("data") or {}).get(
            "multi_input_files") or []) if not x.get("input_file")]
        if absent:
            raise RuntimeError(T('These tracks got no file: %s')
                               % ", ".join(absent))
    else:
        print(T('  The existing files are reused -- recomputing costs nothing.'))
    _curl_call(key, ["-X", "POST",
                AUPHONIC + "/api/production/%s/start.json" % uuid])
    p = wait_for_production(key, uuid, wait_s)
    return download_results(key, p, names, target_folder, base)


def wait_for_production(key, uuid, wait_s):
    """Wait for the production to finish, with a progress bar and a timeout."""
    started = time.time()
    end = started + wait_s
    horizon = 150.0
    print(T('  Time limit: %s') % as_hms(wait_s))
    while time.time() < end:
        d = _parse_json(_curl_call(key, [AUPHONIC + "/api/production/%s.json" % uuid]))
        p = d.get("data") or {}
        status, text = p.get("status"), p.get("status_string") or "?"
        if status == 3:
            sys.stdout.write(T('\r  [%-30s] 100 %%  %s  done%s\n')
                             % ("#" * 30, as_hms(time.time() - started), " " * 20))
            return p
        if status == 2:
            raise RuntimeError(T('Auphonic reports an error: %s')
                               % (p.get("error_message") or text))
        for _ in range(5):
            elapsed = time.time() - started
            while elapsed >= horizon:
                horizon *= 2
            share = min(0.99, elapsed / horizon)
            # The bar is redrawn over itself, so every field keeps its
            # width: %3.0f is what holds the %% in place. 0 to 99 with
            # no decimal place, so no mark a language could set.
            sys.stdout.write("\r  [%-30s] %3.0f %%  %s  %s        "
                             % ("#" * int(share * 30), share * 100,
                                as_hms(elapsed), text))
            sys.stdout.flush()
            if time.time() >= end:
                break
            time.sleep(2)
    raise RuntimeError(T('Time limit of %s reached, production still '
                         'running: %s/engine/status/%s') % (as_hms(wait_s), AUPHONIC, uuid))


def tracks_folder(folder, create=True):
    """Return the folder with the tracks and everything else from Auphonic."""
    target = os.path.join(folder, "auphonic-tracks")
    if create:
        os.makedirs(target, exist_ok=True)
    return target


def match_zip_entries_to_tracks(zip_file_path, names, target_folder):
    """Unpack the ZIP and match its files to the track names.

    Auphonic does not say how it names them; the closest match is used.
    """
    import zipfile
    folder = tracks_folder(target_folder)
    with zipfile.ZipFile(zip_file_path) as zf:
        files = [n for n in zf.namelist()
                   if not n.endswith("/") and not os.path.basename(n).startswith(".")]
        zf.extractall(folder)
    assignment, pending = {}, list(files)
    print(T('  In the archive: %s') % ", ".join(os.path.basename(d) for d in files))
    try:
        # Once unpacked the ZIP is no longer needed.
        os.unlink(zip_file_path)
    except OSError:
        pass
    # What the entries do not have in common: where each carries the
    # episode title and the title the speakers' names, the whole name
    # tells them apart worse than nothing -- 0.286 against 0.278.
    stems = [os.path.splitext(os.path.basename(d))[0] for d in files]
    head = os.path.commonprefix(stems) if len(stems) > 1 else ""
    tail = (os.path.commonprefix([x[::-1] for x in stems])[::-1]
            if len(stems) > 1 else "")
    telling = {d: (x[len(head):len(x) - len(tail)] or x)
               for d, x in zip(files, stems)}

    for name in names:
        if not pending:
            break
        best = max(pending, key=lambda d: similarity(name, telling[d]))
        quality = similarity(name, telling[best])
        if name.lower() in telling[best].lower() or quality > 0.4:
            assignment[name] = os.path.join(folder, best)
            pending.remove(best)
            print("    %-20s <- %s" % (name, os.path.basename(best)))
        else:
            print(T('    %-20s <- nothing suitable found') % name)
    return assignment
