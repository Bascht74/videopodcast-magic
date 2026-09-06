# -*- coding: utf-8 -*-
"""The hearing: what a file sounds like, and where that puts it.

A piece of the program, read out of the folder beside it by beside().
It cannot import the file it was cut out of, because that file is
still being read while this one is; the program is handed in instead,
and every name this piece uses out of it is bound below, by name.
"""

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

# What the program has and this piece uses, bound once so that the
# measuring reads as it did in the one file. Eight names are missing,
# and the two blocks under the list say which and why.

ENV_MARK = PROGRAM.ENV_MARK
SR = PROGRAM.SR
T = PROGRAM.T
THREAD_SHARE = PROGRAM.THREAD_SHARE
VERSION = PROGRAM.VERSION
as_hms = PROGRAM.as_hms
as_warn = PROGRAM.as_warn
bext_time_reference = PROGRAM.bext_time_reference
cache_folder = PROGRAM.cache_folder
clean_old_files = PROGRAM.clean_old_files
decimal_text = PROGRAM.decimal_text
ffprobe_json = PROGRAM.ffprobe_json
group_text = PROGRAM.group_text
hashlib = PROGRAM.hashlib
log_aside = PROGRAM.log_aside
os = PROGRAM.os
parse_timecode = PROGRAM.parse_timecode
path_key = PROGRAM.path_key
progress_from_line = PROGRAM.progress_from_line
safe_filename = PROGRAM.safe_filename
sample_count = PROGRAM.sample_count
shell_quote = PROGRAM.shell_quote
show_progress = PROGRAM.show_progress
subprocess = PROGRAM.subprocess
sys = PROGRAM.sys
tempfile = PROGRAM.tempfile
threading = PROGRAM.threading
time = PROGRAM.time
timecode_string = PROGRAM.timecode_string


# Six of the eight come out of the material, which is read further down
# than this piece, so a copy taken here would find nothing: the channel
# filter, the channel count kept, the note about the Python in use, the
# quiet remove, the safe wav name and the widest track.

# OUTPUT_SINK is the seventh. The window sets it on the program object,
# and that is a write the pieces are never told about, so a copy here
# would answer with the value of the run before. It stays over there
# and is read as PROGRAM.OUTPUT_SINK where a line is written.

# numpy is the eighth, and the one name here that the program has still
# to fetch: it holds a stand-in until the first sum asks, and binds the
# real module under its own name then -- which a copy taken up there
# would never see. So this asks the program once, the same way.
class LateNumpy:
    """Stands in for the program's numpy until a sum wants it."""

    def __getattr__(self, name):
        global np
        got = getattr(PROGRAM.np, name)
        np = PROGRAM.np
        return got


np = LateNumpy()


def audio_track_starts_at(path, stream=None):
    """When the first sample of this audio track is to be heard, in seconds.

    A camera track can begin after the picture, and an AAC stream
    begins with samples the file marks as not to be played; both go
    into this number, and both were being thrown away. Measured
    2.9.2026 over three cameras of one shoot: 60,375 ms at one of them
    and none at the other two -- so it is read, never assumed.
    """
    # And what no file declares cannot be put right from here: a stream
    # whose lead-in is nowhere written down comes back that much too
    # late, and nothing in it says by how much.
    try:
        rows = [s for s in (ffprobe_json(path).get("streams") or [])
                if s.get("codec_type") == "audio"]
        row = rows[stream or 0] if rows else {}
        return float(row.get("start_time") or 0.0)
    except (IndexError, TypeError, ValueError):
        return 0.0


def audio_on_the_picture(x, path, rate, stream=None):
    """Put decoded samples where the file says they are to be heard.

    Silence in front where the track starts after the picture, and the
    head cut away where it starts before it. Only for a decode from the
    front: with -ss ffmpeg counts from the presentation time itself and
    the samples already lie right.
    """
    head = int(round(audio_track_starts_at(path, stream) * rate))
    if head > 0:
        return np.concatenate([np.zeros(head, dtype=x.dtype), x])
    if head < 0:
        return x[-head:]
    return x


def decode_audio(path, rate=SR, ss=None, duration=None, stream=None,
                 dtype=None):
    """Decode one channel of a file into samples.

    ffmpeg writes float32 and the default widens it to float64.
    Whoever hands the samples on in float32 asks for float32 here and
    saves a copy at twice the size, which over a whole episode is the
    largest block the program holds. None is that default: numpy is
    fetched at the end of this file and cannot stand in a signature.
    """
    cmd = ["ffmpeg", "-v", "error"]
    if ss is not None:
        cmd += ["-ss", "%.6f" % ss]
    if duration is not None:
        cmd += ["-t", "%.6f" % duration]
    cmd += ["-i", path]
    if stream is not None:
        cmd += ["-map", "0:a:%d" % stream]
    cmd += ["-ac", "1", "-ar", str(rate), "-f", "f32le", "-"]
    p = subprocess.run(cmd, capture_output=True)
    x = np.frombuffer(p.stdout, dtype=np.float32).astype(
        dtype or np.float64)
    # What comes back begins where the file says the track begins, not
    # where ffmpeg's first sample happens to fall. With -ss it already
    # does: there ffmpeg counts from the presentation time itself.
    return x if ss is not None else audio_on_the_picture(x, path, rate,
                                                         stream)


_ENV = {}


def decode_audio_long(path, rate, duration, text, stream=None, report=None):
    """Decode audio with progress reporting.

    Reading a 30 GB file once takes minutes, and a blinking cursor is not
    enough feedback for that.
    """
    return decode_audio_tracks(path, rate, duration, text, [stream],
                               report)[0]


def decode_audio_tracks(path, rate, duration, text, streams, report=None):
    """Decode several tracks of one file in one pass over the container.

    Asking track by track reads a 36 GB camera file once per track, and
    off a drive that pass is the whole of the waiting; one ffmpeg with a
    -map per track reads it once. One process has one progress stream,
    so the text has to name every track that pass is fetching.
    """
    cmd = ["ffmpeg", "-v", "error", "-nostats", "-progress", "pipe:1",
           "-i", path]
    raws = []
    for stream in streams:
        fd, raw = tempfile.mkstemp(suffix=".raw")
        os.close(fd)
        raws.append(raw)
        if stream is not None:
            cmd += ["-map", "0:a:%d" % stream]
        cmd += ["-ac", "1", "-ar", str(rate), "-f", "f32le", "-y", raw]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL)
        points = 0
        for line in proc.stdout:
            share = progress_from_line(line, duration)
            if share is not None:
                if report:
                    report(share)
                else:
                    show_progress(text, share)
                continue
            note = line.decode("utf-8", "replace").strip()
            if note.startswith("out_time_ms=") or note.startswith("frame="):
                points = (points + 1) % 20
                if not report:
                    show_progress(note + " " + "." * (points // 4 + 1))
        proc.wait()
        if report:
            report(1.0)
        else:
            show_progress(text, 1.0)
            if THREAD_SHARE.get(threading.get_ident()) is None:
                if PROGRAM.OUTPUT_SINK:
                    PROGRAM.OUTPUT_SINK("\n")
                else:
                    sys.stdout.write("\n")
        # Each track on the time of its own start, the same as the
        # short way above: a big file must not be placed differently
        # from a small one only because it came through here.
        return [audio_on_the_picture(
                    np.fromfile(raw, dtype=np.float32).astype(np.float64),
                    path, rate, stream)
                for raw, stream in zip(raws, streams)]
    finally:
        for raw in raws:
            PROGRAM.remove_quietly(raw)


def envelope_cache_folder():
    """Return the folder the computed envelopes may live in."""
    return cache_folder("envelopes")


def clean_envelope_cache(days=30):
    """Discard stale envelopes; once per run is enough."""
    clean_old_files(envelope_cache_folder(), days)


_RECIPE_MARKS = {}


def recipe_mark(name, *work):
    """A short mark of the way something is worked out.

    A number counted by hand would have to be remembered, and the day
    somebody forgets it the store hands back a measurement another
    recipe wrote. So the source of the functions that decide the
    numbers is read and hashed: it cannot change without changing
    this.
    """
    if name not in _RECIPE_MARKS:
        try:
            import inspect
            text = "".join(inspect.getsource(f) for f in work)
        except Exception:
            # Nothing to read the source from. The version is coarse --
            # every release throws the store away -- but it never hands
            # back what some other recipe wrote.
            text = VERSION
        _RECIPE_MARKS[name] = hashlib.sha1(
            text.encode("utf-8")).hexdigest()[:12]
    return _RECIPE_MARKS[name]


def envelope_recipe_mark():
    """The mark for a curve: what ffmpeg is asked for, and the rest."""
    return recipe_mark("envelope", decode_audio, decode_audio_tracks,
                       envelope, audio_track_starts_at,
                       audio_on_the_picture)


def envelope_cache_path(path, hop_ms, rate):
    """Return a cache name that changes as soon as the file changes.

    Or as soon as the way the curve is worked out changes: without that
    mark a changed recipe reads the old curves back and the run
    compares two of them that were never measured the same way.
    """
    folder = envelope_cache_folder()
    if not folder:
        return None
    try:
        st = os.stat(path)
    except OSError:
        return None
    import hashlib
    fingerprint = "%s|%d|%d|%.3f|%d|%s" % (path_key(path), int(st.st_mtime),
                                    st.st_size, hop_ms, rate,
                                    envelope_recipe_mark())
    return os.path.join(folder,
                        hashlib.sha1(fingerprint.encode("utf-8")).hexdigest()
                        + ".npy")


def envelope_log(path, hop_ms, rate, what):
    """Say whether a curve came out of the store or off the disc.

    A curve costs minutes on a large file and nothing when it is
    found. Which of the two happened is invisible from outside, and
    the numbers are in the line because a curve is kept under them:
    the same file at another hop or rate is another curve.
    """
    log_aside("%s %s  %-30s %g/%d  %s"
              % (ENV_MARK, time.strftime("%H:%M:%S"),
                 os.path.basename(path)[:30], hop_ms, rate, what))


def video_envelope(path, hop_ms=5.0, rate=4000, report=None):
    """Return the envelope of the video audio track, computed once per file.

    The cache survives the whole run. The interface warms it while the user
    is still typing, so by the time the run starts the curve is there.
    Kept under path_key: the prework warms it under the absolute path
    and the time axis asks under the name the file dialog gave, and
    where those differ the file was read twice. It is opened by the
    path as it came in."""
    api_key = (path_key(path), hop_ms, rate)
    if api_key not in _ENV:
        # Reading an hour of 4K takes minutes; twice is unnecessary.
        cache = envelope_cache_path(path, hop_ms, rate)
        if cache and os.path.exists(cache):
            try:
                _ENV[api_key] = np.load(cache)
                envelope_log(path, hop_ms, rate, "read back from the store")
                return _ENV[api_key]
            except Exception as trouble:
                envelope_log(path, hop_ms, rate,
                             "the stored curve would not read: %s" % trouble)
        else:
            envelope_log(path, hop_ms, rate,
                         "nothing in the store, reading the file"
                         if cache else "no store to look in")
        duration = 0.0
        try:
            duration = float(ffprobe_json(path).get("format", {}).get("duration") or 0)
        except Exception:
            pass
        large = os.path.getsize(path) > 200e6 if os.path.exists(path) else False
        if large or report:
            x = decode_audio_long(path, rate, duration,
                                T('Reading audio track from %s') % os.path.basename(path),
                                report=report)
        else:
            x = decode_audio(path, rate=rate)
        _ENV[api_key] = envelope(x, hop_ms, rate)
        if len(_ENV[api_key]) < 10:
            # ffmpeg delivered nothing. Caching that would mean treating the
            # file as unalignable until it next changes, without ever saying
            # why.
            _ENV.pop(api_key, None)
            raise ValueError(T('no audio data from %s')
                             % os.path.basename(path))
        if cache:
            # Beside it and then moved: two files being measured at
            # once, or a run broken off, must not leave half a curve
            # behind for the next start to read as a measurement.
            try:
                # The suffix has to be .npy: np.save appends one
                # otherwise, and the move would then miss the file.
                fd, beside = tempfile.mkstemp(dir=os.path.dirname(cache),
                                              prefix=".vpm_", suffix=".npy")
                os.close(fd)
                np.save(beside, _ENV[api_key].astype("float32"))
                os.replace(beside, cache)
            except Exception:
                pass
    return _ENV[api_key]


def envelope(x, hop_ms=5.0, rate=SR):
    h = max(1, int(hop_ms * rate / 1000.0))
    m = len(x) // h
    if m < 2:
        return np.zeros(0)
    e = np.sqrt((x[:m * h].reshape(-1, h) ** 2).mean(1))
    e = np.log(e + 1e-9)
    return e - e.mean()


# Narrow where mains hum sits, wider above it. Everything over the last
# edge is counted into the last band: at 4000 Hz that is a single bin.
BAND_EDGES = (0, 50, 75, 100, 125, 150, 200, 250, 300, 400, 500, 650,
              800, 1000, 1200, 1400, 1600, 1800, 2000)
# How long a stretch one band level is read over. 64 ms is long enough
# to tell 50 Hz from 100 Hz; the 5 ms box the plain curve uses is not,
# and there a hum and the voice over it land in the same value.
BAND_WINDOW_S = 0.064
# A band counts if its own loudness moves at least half as much as the
# liveliest band of that recording. Measured 1.9.2026 over 38 tracks
# from four productions: the mains hum drops out of every one of them,
# and none of the 85 pairs that belong together got worse.
BAND_MOVES_ENOUGH = 0.5


def band_powers(x, hop_ms=5.0, rate=SR):
    """How much power each band holds at every step of the curve.

    One short spectrum every hop, its bins summed inside the band
    edges. Worked through in blocks: a whole episode at once is a
    matrix of some gigabytes, and the answer is the same either way.
    """
    hop = max(1, int(hop_ms * rate / 1000.0))
    win = max(16, 1 << int(round(np.log2(BAND_WINDOW_S * rate))))
    steps = (len(x) - win) // hop
    bands = len(BAND_EDGES) - 1
    if steps < 10:
        return np.zeros((bands, 0), dtype=np.float32)
    which = np.clip(np.searchsorted(np.asarray(BAND_EDGES, float),
                                    np.fft.rfftfreq(win, 1.0 / rate),
                                    side="right") - 1, 0, bands - 1)
    shape = np.hanning(win)
    out = np.empty((bands, steps), dtype=np.float32)
    block = 40000
    for s in range(0, steps, block):
        k = min(block, steps - s)
        at = np.arange(win)[None, :] + hop * np.arange(s, s + k)[:, None]
        power = np.abs(np.fft.rfft(x[at] * shape, axis=1)) ** 2
        for b in range(bands):
            here = which == b
            out[b, s:s + k] = power[:, here].sum(1) if here.any() else 0.0
    return out


def moving_bands(power):
    """Which bands say something about the time, and which stand still.

    A band whose level never changes cannot place anything, however
    loud it is: mains hum sits there at full strength and says the
    same thing from the first second to the last. Asked of the
    recording itself, so no frequency has to be set from outside.
    """
    if not power.size:
        return np.zeros(len(power), dtype=bool)
    move = np.array([float(np.log(np.sqrt(np.asarray(p, float)) + 1e-9).std())
                     for p in power])
    return move >= BAND_MOVES_ENOUGH * (float(move.max()) or 1.0)


def band_envelope(x, hop_ms=5.0, rate=SR):
    """The loudness curve without the bands that carry no movement.

    What envelope() reads in one piece, read band by band with the
    still ones left out. Where every band moves alike nothing is left
    out, and this is the same curve through a longer window.
    """
    power = band_powers(x, hop_ms, rate)
    keep = moving_bands(power)
    kept = power[keep] if keep.any() else power
    if not kept.size:
        return np.zeros(0)
    e = np.log(np.sqrt(kept.astype(np.float64).sum(0)) + 1e-9)
    return e - e.mean()


def phase_align(a, b, rate, most_s=None):
    """Where b sits against a, by phase alone. (seconds, sharpness).

    The envelope way asks where two recordings are loud together, and
    that needs something to be loud and quiet about. Music has almost
    nothing: a mixed, limited song holds the same loudness for minutes.
    Measured on 23.8.2026 -- an iPhone recording of monitor speakers
    against the finished mix of the same music -- the envelope way
    answered 74.775 s at a quality of -0.183, and the right answer was
    569.2 s.

    This one throws the loudness away and keeps only the phase, which
    is what a re-recording through a room survives. It found that 569.2
    s to within twelve milliseconds, first try, with nothing to go on.

    The sharpness is the peak against the noise around it. It says how
    much the answer is worth, and it is the only thing that does: a
    peak that is barely above its neighbours is a guess.
    """
    if len(a) < rate or len(b) < rate:
        return 0.0, 0.0
    n = 1 << int(np.ceil(np.log2(len(a) + len(b))))
    fa = np.fft.rfft(np.asarray(a, float) - np.mean(a), n)
    fb = np.fft.rfft(np.asarray(b, float) - np.mean(b), n)
    both = fb * np.conj(fa)
    # The whitening is the whole point: every frequency counts the
    # same, so a loud bass drum does not drown out the rest.
    line = np.fft.irfft(both / (np.abs(both) + 1e-12), n)
    k = int(np.argmax(line))
    if k > n // 2:
        k -= n
    if most_s is not None and abs(k) / float(rate) > most_s:
        return 0.0, 0.0
    sharp = float(line.max() / (line.std() or 1.0))
    return k / float(rate), sharp


def looks_like_music(env):
    """A guess at whether this is music, for the log and nothing else.

    Speech swings in syllables, two to eight times a second. Music
    swings with the beat and the phrase, slower. Measured on 23.8.2026
    the two do not separate cleanly -- a finished mix landed at 26 per
    cent of its movement in the syllable band, speech at 31 to 32 --
    so this decides nothing. It only explains, afterwards, why the
    plain way had so little to work with.
    """
    e = np.asarray(env, float)
    e = e[np.isfinite(e)]
    if len(e) < 4000:
        return False
    e = e - e.mean()
    power = np.abs(np.fft.rfft(e * np.hanning(len(e)))) ** 2
    hz = np.fft.rfftfreq(len(e), 0.005)
    whole = float(power[(hz >= 0.2) & (hz < 20.0)].sum()) or 1.0
    syllables = float(power[(hz >= 2.0) & (hz < 8.0)].sum()) / whole
    return syllables < 0.20


def cross_correlate(a, b):
    """Where b sits against a, and how well it fits there.

    The peak is the largest positive one, not the largest by size.
    An envelope here is log loudness with its mean taken out, so it
    swings either side of zero -- but two that belong together still
    rise and fall together, and that pushes the correlation up. A
    strong negative peak is the opposite: loud where the other is
    quiet. That is never where they belong, however large it is.

    Taking the absolute value used to hand exactly that back. Measured
    on 23.8.2026, an iPhone recording of monitor speakers against the
    finished mix of the same music: it answered +74.775 s at -0.183,
    while the best real agreement was +0.131 somewhere else again.
    Neither is a match -- but only one of the two is even a possible
    one. The right answer, +569.2 s, needed another method entirely.
    """
    m = min(len(a), len(b))
    if m < 10:
        return 0, 0.0
    a, b = a[:m], b[:m]
    nf = 1 << int(np.ceil(np.log2(2 * m)))
    cc = np.fft.irfft(np.fft.rfft(b, nf) * np.conj(np.fft.rfft(a, nf)), nf)
    k = int(np.argmax(cc))
    if k > nf // 2:
        k -= nf
    label_text = np.sqrt((a ** 2).sum() * (b ** 2).sum())
    return k, float(cc[k % nf] / label_text) if label_text else 0.0


def join_with_report(paths, target, keep_parts=False):
    """Join the blocks of one recording and say what was found.

    The joining was shared; the reporting was not. The ordinary path
    said how many blocks went together, where the gaps were and whether
    two of them overlapped instead of following each other. The
    multitrack path did the same work in silence, so a recording with a
    ten-second hole in it went through without a word.
    """
    source, join_info = join_audio_parts(paths, target, keep_parts=keep_parts)
    if join_info.get("tc"):
        print(T('  %s blocks joined via timecode, start %s')
              % (group_text(join_info["blocks"]),
                 timecode_string(join_info["start"] / float(SR))))
        for at_s, g in join_info.get("gaps_found", []):
            if g > 0:
                print(T('  Gap of %s at %s -- filled with silence')
                      % (as_hms(g / float(SR)), as_hms(at_s / float(SR))))
            else:
                # A negative gap is an overlap. Nothing is filled there;
                # the two sound at the same time.
                print(T('  Overlap of %s at %s -- both sound there')
                      % (as_hms(-g / float(SR)), as_hms(at_s / float(SR))))
        if join_info.get("side_by_side"):
            print(T('  They overlap -- several microphones at once, not '
                    'blocks in a row.'))
            if join_info.get("parts"):
                print(T('  Each one also goes into the video as a track of '
                        'its own: %s')
                      % ", ".join(n for n, _p in join_info["parts"]))
            else:
                print(T('  Only the mix goes into the video '
                        '(--no-single-tracks).'))
    else:
        print(T('  %s blocks joined in name order (no timecode -- gaps '
                'would not be recognisable)')
              % group_text(join_info["blocks"]))
    return source, join_info


def join_audio_parts(paths, target, keep_parts=False):
    """Join several audio files into one.

    With timecodes they are placed on a common time axis and gaps are filled
    with silence. Without, they are laid end to end in the order they came
    in -- the caller has already put them in it.

    The result has as many channels as the widest of them. One stereo
    recording among mono ones therefore keeps its sides, and the mono ones
    are copied to both -- written out rather than left to ffmpeg, which
    would take 3 dB off them on the way.

    With *keep_parts* each recording is also written on its own, on the same
    axis and the same length as the sum, so it can go into the video beside
    the mix. Only where the recordings overlap: blocks laid end to end are
    one recording, and a track per block would be silence with one block in
    it. It costs no second decode -- the same pass writes both.
    """
    paths = list(paths)
    if len(paths) == 1:
        return paths[0], {"blocks": 1, "parts": []}
    channels = PROGRAM.widest_track(paths)
    same = [PROGRAM.channel_filter(PROGRAM.kept_channels(p), channels)
            for p in paths]
    lengths = [sample_count(p) for p in paths]
    trs = [bext_time_reference(p) for p in paths]
    # Every file has to carry a time, and no two may claim the same one:
    # sorting by it would otherwise depend on the order the files came in.
    # Two recorders started together write exactly the same number, and
    # those recordings run at the same time -- so they are placed on the
    # axis together rather than end to end.
    having_tc = all(t is not None for t in trs)
    if having_tc and len(set(trs)) != len(trs):
        order = sorted(range(len(paths)),
                       key=lambda i: (trs[i], os.path.basename(paths[i]).lower()))
        paths = [paths[i] for i in order]
        lengths = [lengths[i] for i in order]
        trs = [trs[i] for i in order]
        same = [same[i] for i in order]

    if having_tc:
        entries = list(zip(trs, paths, lengths)) if len(set(trs)) != len(trs) \
            else sorted(zip(trs, paths, lengths))
        t0 = entries[0][0]
        total = max(t + n for t, _, n in entries) - t0
        gaps = []
        for (ta, _, na), (tb, _, _) in zip(entries, entries[1:]):
            g = tb - (ta + na)
            if abs(g) > SR // 100:
                gaps.append((ta + na - t0, g))
        # Do the recordings run at the same time or one after another? The
        # timecodes say so, and nothing else has to be guessed: overlapping
        # means several microphones were running at once, and then each one
        # is worth a track of its own.
        side_by_side = any(tb < ta + na for (ta, _, na), (tb, _, _)
                           in zip(entries, entries[1:]))
        alone = []
        if side_by_side and keep_parts:
            folder = os.path.dirname(os.path.abspath(target)) or "."
            for i, (_t, p, _n) in enumerate(entries):
                name = PROGRAM.guess_speaker_name(p)
                alone.append((name,
                              os.path.join(folder, "part%d_%s.wav"
                                           % (i, safe_filename(name)))))
        parts, chains, markers, writes = [], [], [], []
        for i, (t, p, n) in enumerate(entries):
            parts += ["-i", p]
            d = t - t0
            f = [PROGRAM.channel_filter(PROGRAM.kept_channels(p), channels)]
            f += ["adelay=delays=%dS:all=1" % d] if d else []
            f += ["apad=whole_len=%d" % total, "atrim=end_sample=%d" % total,
                  "asetpts=N/SR/TB"]
            # One decode, two uses: the sum, and the single track beside it.
            # A filter output can only be read once, hence the split.
            tail = ",asplit=2[t%d][s%d]" % (i, i) if alone else "[t%d]" % i
            chains.append("[%d:a]%s%s" % (i, ",".join(f), tail))
            markers.append("[t%d]" % i)
            if alone:
                writes += (["-map", "[s%d]" % i, "-c:a", "pcm_s24le",
                            "-write_bext", "1", "-metadata",
                            "time_reference=%d" % t0]
                           + PROGRAM.wav_safe(alone[i][1])
                           + ["-y", alone[i][1]])
        fc = ";".join(chains) + ";" + "".join(markers) +\
             "amix=inputs=%d:normalize=0[out]" % len(markers)
        shell_quote(["ffmpeg", "-v", "error"] + parts + ["-filter_complex", fc,
            "-map", "[out]", "-c:a", "pcm_s24le", "-write_bext", "1",
            "-metadata", "time_reference=%d" % t0]
            + PROGRAM.wav_safe(target) + ["-y", target] + writes)
        return target, {"blocks": len(paths), "tc": True, "gaps_found": gaps,
                      "start": t0, "side_by_side": side_by_side,
                      "parts": alone}

    # In the order they came in. Without a timecode that order is the
    # only one there is: it comes from the counter, from the clock in the
    # name, or from a hand that said these belong together in this order.
    # Sorting by name again would throw the last of the three away.
    row = list(zip(paths, lengths))
    if len(set(same)) == 1 and same[0] == "anull":
        # All alike: the concat demuxer is the cheapest way and needs no
        # filter graph at all.
        lst = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
        for p, _ in row:
            lst.write("file '%s'\n" % os.path.abspath(p).replace("'", "'\\''"))
        lst.close()
        try:
            shell_quote(["ffmpeg", "-v", "error", "-f", "concat", "-safe", "0",
                "-i", lst.name, "-c:a", "pcm_s24le", "-y", target])
        finally:
            os.unlink(lst.name)
        return target, {"blocks": len(paths), "tc": False, "parts": []}
    # Different channel counts: the concat demuxer refuses those, so the
    # blocks are brought to the same width first and strung together in the
    # filter graph.
    parts, chains, markers = [], [], []
    for i, (p, _n) in enumerate(row):
        parts += ["-i", p]
        chains.append("[%d:a]%s[t%d]"
                      % (i, PROGRAM.channel_filter(
                          PROGRAM.kept_channels(p), channels), i))
        markers.append("[t%d]" % i)
    fc = ";".join(chains) + ";" + "".join(markers) +\
        "concat=n=%d:v=0:a=1[out]" % len(markers)
    shell_quote(["ffmpeg", "-v", "error"] + parts + ["-filter_complex", fc,
        "-map", "[out]", "-c:a", "pcm_s24le", "-y", target])
    return target, {"blocks": len(paths), "tc": False, "parts": []}


def audio_range_covered_by_video(audio, video, edge_s=60.0):
    """Return which part of the audio file has a counterpart in the picture.

    Only the first and last *edge_s* seconds are searched. Two passes:
    coarse with 4 s windows in half second steps, then fine with 1 s windows
    in 50 ms steps around the edge found. The coarse window finds the edge
    reliably but sits systematically late -- a window half inside the intro
    only half matches. The second pass recovers that.
    """
    HOP, rate = 5.0, 4000
    env_video = video_envelope(video, HOP, rate)
    env_audio = envelope(decode_audio(audio, rate=rate), HOP, rate)
    n_audio = sample_count(audio)
    if len(env_video) < 200 or len(env_audio) < 200:
        return 0, n_audio, {"reason": T('too short')}

    # The anchor is the middle of the picture, not of the audio: the audio can
    # be a multiple longer, and then its middle may lie entirely outside what
    # the camera recorded.
    m0, m1 = int(len(env_video) * 0.25), int(len(env_video) * 0.75)
    middle = env_video[m0:m1]
    nf = 1 << int(np.ceil(np.log2(len(env_audio) + len(middle))))
    cc = np.fft.irfft(np.fft.rfft(env_audio, nf)
                      * np.conj(np.fft.rfft(middle, nf)), nf)
    # Where the picture sits when the audio is at zero.
    shift = m0 - int(np.argmax(cc[:max(1, len(env_audio))]))

    def quality(i, W):
        j = i + shift
        if i < 0 or i + W > len(env_audio) or j < 0 or j + W > len(env_video):
            return 0.0
        a, b = env_audio[i:i + W], env_video[j:j + W]
        na, nb = np.sqrt((a ** 2).sum()), np.sqrt((b ** 2).sum())
        return float((a * b).sum() / (na * nb)) if na > 0 and nb > 0 else 0.0

    win_coarse = int(4.0 * 1000 / HOP)
    # Measure the reference level only where audio and picture both run.
    t0 = max(0, -shift)
    t1 = min(len(env_audio), len(env_video) - shift)
    means = [quality(i, win_coarse) for i in
                   range(t0 + int((t1 - t0) * 0.3),
                         max(t0 + int((t1 - t0) * 0.3) + 1,
                             t0 + int((t1 - t0) * 0.7)), win_coarse)]
    level = float(np.median(means)) if means else 0.0
    if level < 0.15:
        return 0, n_audio, {"reason":
                            T('no match in the middle either (%s)')
                            % decimal_text("%.2f" % level)}
    threshold = max(0.12, 0.5 * level)
    R = int(edge_s * 1000 / HOP)
    step_coarse = int(0.5 * 1000 / HOP)
    win_fine = int(1.0 * 1000 / HOP)
    step_fine = max(1, int(0.05 * 1000 / HOP))

    def edge(front):
        """Return where the part matching the picture begins or ends.

        Searched around the place it should sit after coarse alignment, not
        around the start and end of the file. Where the audio is a multiple of
        the picture in length, the edges lie far inside.
        """
        anchor = t0 if front else t1 - win_coarse
        coarse, run = None, 0
        steps = range(0, R, step_coarse)
        for d in steps:
            i = anchor + d if front else anchor - d
            if i < 0 or i + win_coarse > len(env_audio):
                continue
            if quality(i, win_coarse) > threshold:
                run += 1
                if run >= 2:
                    coarse = i if front else i + win_coarse
                    break
            else:
                run = 0
        if coarse is None:
            return max(0, t0) if front else min(len(env_audio), t1)
        best = coarse
        for k in range(1, int(6.0 * 1000 / HOP / step_fine)):
            i = coarse - k * step_fine if front else coarse + k * step_fine
            if quality(i if front else i - win_fine, win_fine) > threshold:
                best = i
            else:
                break
        return max(0, best) if front else min(len(env_audio), best)

    i0, i1 = edge(True), edge(False)
    if i1 <= i0:
        return 0, n_audio, {"reason": T('edges implausible')}
    return (max(0, int(i0 * HOP / 1000.0 * SR)),
            int(min(n_audio, i1 * HOP / 1000.0 * SR)),
            {"threshold": threshold, "level": level})


# What the phase way has to beat before it is believed instead of the
# plain one. Measured on 23.8.2026: on the music that sent us looking
# it came out at 28.7 against a nearest rival of 26.5, and the answer
# was right to twelve milliseconds. Not measured on enough material to
# call it a threshold -- it is a floor, and the log prints the number
# so anybody can see how close it was.
PHASE_SHARP_ENOUGH = 8.0


def align_on_moving_bands(x_video, x_audio, HOP, rate, sample_points,
                          window_s, distance_s):
    """The same way again, on the bands that carry movement.

    Returns what align_envelopes returns, or None where a curve came
    out too short to compare. The numbers in it are the ordinary ones
    -- sample points and their spread -- so the gate that judges the
    first answer judges this one by the same rule.
    """
    curve_video = band_envelope(x_video, HOP, rate)
    curve_audio = band_envelope(x_audio, HOP, rate)
    if len(curve_video) < 10 or len(curve_audio) < 10:
        return None
    return align_envelopes(curve_video, curve_audio, HOP, sample_points,
                           window_s, distance_s, warn=False)


def align_audio_to_video(audio, video, head_s, sample_points=None, window_s=20.0,
               distance_s=120.0):
    """Return a, b with audio time = a + b * video time."""
    HOP, rate = 5.0, 4000
    env_video = video_envelope(video, HOP, rate)
    x_audio = decode_audio(audio, rate=rate, ss=head_s / float(SR))
    env_audio = envelope(x_audio, HOP, rate)
    a, b, st = align_envelopes(env_video, env_audio, HOP, sample_points,
                               window_s, distance_s,
                               warn=os.path.basename(audio))
    if st.get("quality", 0.0) >= WEAK_MATCH:
        return a, b, st
    # The plain way found nothing worth having. Both files are read
    # here, once, for the second try and for the phase way under it --
    # the phase way read them itself before, so this costs no decode.
    x_video = decode_audio(video, rate=rate)
    second = align_on_moving_bands(x_video, x_audio, HOP, rate,
                                   sample_points, window_s, distance_s)
    if second is not None and fit_places_it(second[2]):
        # Sample points enough, and close enough to one line. Measured
        # over 293 pairs out of different productions not one gets that
        # far, and all 85 that belong together do.
        second[2]["from_bands"] = True
        return second
    # Both curves came up empty. The phase way -- it only ever runs
    # here, where the answer was going to be wrong anyway, and it is
    # the one way no sample point backs up.
    st["music_like"] = looks_like_music(env_audio)
    where, sharp = phase_align(x_video, x_audio, rate)
    st["phase_s"], st["phase_sharp"] = where, sharp
    if sharp >= PHASE_SHARP_ENOUGH:
        st["from_phase"] = True
        # No drift from this one: it answers where, not how fast. The
        # factor stays 1.0 and the report says the drift is unknown
        # rather than pretending it is zero.
        return where, 1.0, st
    # Both ways came up empty. The numbers still travel back, because
    # the log prints them, but they are marked for what they are: not
    # an alignment, a guess. Whoever asked has to decide what to do
    # with a file that has no place -- see cannot_be_placed.
    st["unplaceable"] = True
    return a, b, st


# How far a point may sit from the middle before it is thrown away.
# 3 is the ordinary choice for a robust fit; the floor keeps a very
# tight set of points from throwing away its own scatter. 20 ms is the
# floor because it is four times HOP -- what the envelope can resolve
# at all. It is a floor, not a measured threshold, and says so.
# Below this the global agreement between two envelopes is not worth
# calling a match. Not measured on real material yet -- it is the old
# 0.05 floor, kept, and now applied to the signed value instead of the
# size. What a good alignment looks like is measured: 0.5 to 0.9 on
# material that belongs together, 0.13 on a camera track against a
# finished mix of the same room.
WEAK_MATCH = 0.05

# The shortest stretch of shared sound and picture that a run will work
# with when the alignment could not place a single sample point in it.
# Where it did place points, the length does not matter -- what was
# measured was measured. Ten seconds because the alignment's own spacing
# is a couple of seconds and a handful of them is the least that says
# anything; the thirty that stood here before was a round number nobody
# had measured, and it refused 26 seconds of picture that come out exact.
AXIS_MIN_WINDOW_S = 10.0

# What one camera has to match another by before it is laid on the axis.
# Far above WEAK_MATCH: between two cameras there is no phase way to fall
# back on, so the envelopes are the whole measurement, and the floor for
# "nothing at all" is not the number for "these two heard the same room".
#
#   camera against camera, 21 s against 26 s      0.837   right
#   camera against camera, 68 min against 68 min  0.811   right
#   an 18-second jingle against 68 min of camera  0.210   nonsense
#
# Measured 30.8.2026; two recordings of different conversations came to
# 0.21 to 0.27 the same day. A real match sits above 0.8, unrelated
# material with structure near 0.25, and half is the middle of the gap.
CAMERA_MATCH_ENOUGH = 0.5
# Measured 1.9.2026, four productions, 85 pairs that belong together
# against 293 that do not: the correlation overlaps (worst real 0.203,
# best foreign 0.124), the fit does not (62 against 43 sample points,
# 11.3 against 22.4 ms).
FIT_POINTS_ENOUGH = 50
FIT_SPREAD_MS = 15.0


def fit_places_it(st):
    """Report whether the sample points alone place this file.

    The correlation above compares two loudness curves over the whole
    runtime, and a steady tone in one of them -- mains hum -- pushes it
    down without moving where the file belongs. The fit does move with
    the answer: many points spread over the runtime, all on one line.
    A file that fits nowhere gets neither.
    """
    spread = st.get("spread_ms")
    return (st.get("points", 0) >= FIT_POINTS_ENOUGH
            and spread is not None and spread <= FIT_SPREAD_MS)


# Against a sound recording a real match reads far lower, so this floor
# only tells a measurement from noise. It stood as a bare 0.15 in the
# middle of the axis measurement until 31.8.2026.
SOUND_MATCH_ENOUGH = 0.15
# Not the count of sample points: they are set 30 seconds apart, so
# shorter material has none at all -- the 21-second camera above had
# none and was placed exactly right.


def timecode_places_it(own, others):
    """Report whether a timecode can put this file among the others.

    A timecode alone places nothing. It is a reading of a clock, and a
    reading only says something next to a second one: the file has to
    carry one and so has something else in the material. Where a
    single file has a timecode and no other does, it is as unplaced as
    if it had none.
    """
    return own is not None and any(t is not None for t in others)


def files_with_no_place(weak, clocks):
    """Which of the badly fitting files no clock places either.

    The one reading of "it fits nowhere": the intro proposal and the
    bar on the wide shot both ask here. Weak alone is not it -- a
    camera whose sound says nothing is still placed by its timecode --
    and below the floor is not it either, because that is measured
    against nothing at all and a jingle lands above it.
    """
    return [p for p in weak
            if not timecode_places_it(
                clocks.get(p), [t for q, t in clocks.items() if q != p])]


def cannot_be_placed(st, own_tc, other_tcs):
    """Report whether an alignment left a file with no place at all.

    Two ways lead to a place, and either one is enough. The timecode
    is the first, and where it answers the sound is not asked at all:
    a camera whose microphone heard nothing of the room is still
    placed to the frame by its clock, and refusing it because of its
    sound would throw away a file that is in fact known to the
    millisecond. The measurement is the second way, and *st* carries
    its verdict: "unplaceable" stands there when every way of
    measuring came up empty.

    Only where neither answers is there nothing left. Then the file is
    refused rather than laid down somewhere, because laid down
    somewhere it looks exactly like a file that fits.

    Not by the count of sample points, though that was tried on
    30.8.2026 and reverted the same hour: on the ordinary path a
    measurement with no sample points is still a measurement -- the
    offset comes from the cross correlation and only the clock drift is
    missing, which is what "too few sample points for a drift
    measurement" says. Reading that as "no place" refused material the
    tests prove is placed to the sample.
    """
    if not (st or {}).get("unplaceable"):
        return False
    return not timecode_places_it(own_tc, other_tcs)


def which_way_placed(st, hint=""):
    """Add to a track's note which way put it on the axis.

    The plain loudness curve says nothing, being the ordinary answer;
    the two later ways do, and both report lines use this one function
    so they say the same thing. The phase carries its sharpness against
    PHASE_SHARP_ENOUGH, and says the drift is unknown: it answers where
    a track sits, not how fast it ran, and the line beside it prints
    +0.00 ppm, which would otherwise read as a drift measured at zero.
    """
    if (st or {}).get("from_bands"):
        hint = (hint + ", " if hint else "") + T('placed on the bands '
                                                 'that move')
    if (st or {}).get("from_phase"):
        hint = (hint + ", " if hint else "") + (
            T('placed by phase, sharpness %s against a floor of %s, '
              'drift unknown')
            % (decimal_text("%.1f" % float(st.get("phase_sharp") or 0.0)),
               decimal_text("%.1f" % PHASE_SHARP_ENOUGH)))
    return hint


def no_place_message(name):
    """Say that a file cannot be placed, and what would fix it."""
    return T('%s cannot be placed: its sound has nothing in common '
             'with the rest of the material, and the file carries no '
             'timecode. It needs one that fits the other recordings, '
             'and that has to be set with another program.') % name


def timecode_seconds(info):
    """The timecode in a video's facts, in seconds, or nothing."""
    if not (info or {}).get("tc"):
        return None
    try:
        return parse_timecode(info["tc"], max(1.0, info.get("fps") or 30.0))
    except (ValueError, TypeError):
        return None


OUTLIER_SIGMA = 3.0
OUTLIER_FLOOR_S = 0.020
OUTLIER_ROUNDS = 6


def _spans_share(tv, duration_v):
    """How much of the runtime the surviving points still cover.

    A set that has been cleaned down to one corner of the recording
    looks tidy and says nothing about the rest of it.
    """
    if len(tv) < 2 or duration_v <= 0:
        return 0.0
    return float((max(tv) - min(tv)) / duration_v)


def without_outliers(tv, dt):
    """Throw away points that lie far from the others. (tv, dt, dropped).

    The anchor is the median, not the line: a single outlier tips the
    line, and then the wrong points look like the odd ones out. The
    scatter is measured as the median absolute deviation, scaled by
    1.4826 so it means the same as a standard deviation on ordinary
    data.

    Six rounds at most, and never below three points -- two points
    always fit a line perfectly, which would turn a broken measurement
    into a confident one. Every point thrown away is named in the log:
    a run that cleans up in silence cannot be checked afterwards.
    """
    kept_t, kept_d = np.asarray(tv, float), np.asarray(dt, float)
    dropped = []
    for _ in range(OUTLIER_ROUNDS):
        if len(kept_t) < 4:
            break
        b, a = np.polyfit(kept_t, kept_d, 1)
        rest = kept_d - (a + b * kept_t)
        middle = float(np.median(rest))
        mad = float(np.median(np.abs(rest - middle))) * 1.4826
        limit = max(OUTLIER_SIGMA * mad, OUTLIER_FLOOR_S)
        keep = np.abs(rest - middle) <= limit
        if keep.all() or int(keep.sum()) < 3:
            break
        for i in np.flatnonzero(~keep):
            dropped.append((float(kept_t[i]), float(rest[i]) * 1000))
        kept_t, kept_d = kept_t[keep], kept_d[keep]
    return kept_t, kept_d, dropped


def align_envelopes(env_video, env_audio, HOP=5.0, sample_points=None, window_s=20.0,
                       distance_s=120.0, points_off="video", warn=True):
    """The same on ready-made envelopes.

    Which way round: the second curve's time = a + b * the first
    curve's time. Said without the word "reference" on purpose --
    align_cameras calls the *first* of its two the reference, and
    reading this line with that meaning turns the pair round.

    *points_off* decides which of the two curves the sample points are
    picked on; the first by default. For a de-bled speaker track it has to
    be the second: only one speaker is left there, and only where they speak
    is there anything to compare. Picking the spots on the camera track
    would land mostly in passages where somebody else talks.

    The number of sample points grows with the runtime -- about one every
    two minutes, at least nine. More points make the slope more certain, and
    the slope is the clock drift. The envelopes are in memory anyway, so an
    extra point costs almost nothing. Kept separate from align_audio_to_video
    so two cameras can be compared without reading the large files twice.
    """
    if len(env_video) < 10 or len(env_audio) < 10:
        raise RuntimeError(T('too little audio to align'))
    if points_off == "audio":
        a, b, st = align_envelopes(env_audio, env_video, HOP, sample_points, window_s,
                                      distance_s, warn=warn)
        return -a / b, 1.0 / b, st
    k, g = cross_correlate(env_video, env_audio)
    coarse = k * HOP / 1000.0
    # Signed, not by size: see cross_correlate. Said out loud even
    # where it passes, because "found something" and "found it barely"
    # look the same from outside. A second try on the same two files
    # has heard it once and asks for silence.
    if warn and g < WEAK_MATCH:
        # warn carries the name where the caller has one. Without it
        # a run with several recordings prints a heap of warnings
        # nobody can put back against a file.
        print(as_warn(T('      WARNING: weak match for %s (%s, %s is '
                        'the floor). The two may not belong together.')
                      % (warn if isinstance(warn, str)
                         else T('this pair of files'),
                         decimal_text("%.3f" % g),
                         decimal_text("%.2f" % WEAK_MATCH))))

    duration_v = len(env_video) * HOP / 1000.0
    W = int(window_s * 1000 / HOP)
    # Create twice as many candidates as needed -- the uninteresting ones drop
    # out immediately, and too many beats too few.
    if sample_points is None:
        sample_points = max(9, min(80, int(duration_v / distance_s) + 1))
    candidates = max(sample_points * 2, 12)
    spread_total = float(np.std(env_video)) or 1.0

    points, with_signal = [], 0
    for i in range(candidates):
        t = duration_v * (i + 0.5) / candidates
        i0 = int(t * 1000 / HOP) - W // 2
        if i0 < 0 or i0 + W > len(env_video):
            continue
        seg = env_video[i0:i0 + W]
        # Silence or steady noise is no use for comparison: there are no edges
        # to align on.
        if float(np.std(seg)) < 0.35 * spread_total:
            continue
        with_signal += 1
        j0 = i0 + int(round(coarse * 1000 / HOP))
        pad = int(2000 / HOP)
        if j0 - pad < 0 or j0 + W + pad > len(env_audio):
            continue
        around = env_audio[j0 - pad:j0 + W + pad]
        nf = 1 << int(np.ceil(np.log2(len(around) + len(seg))))
        cc = np.fft.irfft(np.fft.rfft(around, nf) * np.conj(np.fft.rfft(seg, nf)), nf)
        kk = int(np.argmax(cc[:2 * pad + 1])) - pad
        label_text = np.sqrt((seg ** 2).sum() * (around[pad + kk:pad + kk + W] ** 2).sum())
        if label_text <= 0:
            continue
        if float(cc[kk + pad] / label_text) > 0.2:
            points.append((t, coarse + kk * HOP / 1000.0))
    count_n = {"candidates": candidates, "with_signal": with_signal,
                "points": len(points)}

    if len(points) >= 3:
        tv = np.array([p[0] for p in points])
        dt = np.array([p[1] for p in points])
        # What the raw points say, before anything is thrown away. It
        # stays in the report: a run that quietly cleans itself up and
        # then calls the result good has traded a loud fault for a
        # quiet one.
        b0, a0 = np.polyfit(tv, dt, 1)
        raw_spread = float(np.std(dt - (a0 + b0 * tv)) * 1000)
        tv, dt, dropped = without_outliers(tv, dt)
        b, a = np.polyfit(tv, dt, 1)
        rest = dt - (a + b * tv)
        n = len(tv)
        sxx = float(((tv - tv.mean()) ** 2).sum())
        s2 = float((rest ** 2).sum()) / max(1, n - 2)
        se_b = (s2 / sxx) ** 0.5 if sxx > 0 else float("inf")
        count_n.update({"ppm": b * 1e6, "ppm_error": se_b * 1e6,
                         "spread_ms": float(np.std(rest) * 1000), "quality": g,
                         "raw_spread_ms": raw_spread,
                         "dropped": dropped,
                         "spans_share": _spans_share(tv, duration_v),
                         "offsets": [float(x) for x in dt],
                         "times": [float(x) for x in tv]})
        return a, 1.0 + b, count_n
    count_n["quality"] = g
    return coarse, 1.0, count_n
