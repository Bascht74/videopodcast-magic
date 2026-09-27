# -*- coding: utf-8 -*-
"""The hearing: what a file sounds like, and where that puts it.

A piece read out of the folder beside it by beside(). It cannot import
the file it was cut out of -- that file is still being read -- so the
program is handed in and every name is bound below, by name.
"""

# beside() puts the program here before this file is read.
PROGRAM = PROGRAM

# What this piece uses out of the program. Eight names are missing, and
# the blocks under the list say which and why.

ENV_MARK = PROGRAM.ENV_MARK
SOUND_MIXED = PROGRAM.SOUND_MIXED
SOUND_SPEECH = PROGRAM.SOUND_SPEECH
SR = PROGRAM.SR
T = PROGRAM.T
THREAD_SHARE = PROGRAM.THREAD_SHARE
VERSION = PROGRAM.VERSION
as_hms = PROGRAM.as_hms
as_warn = PROGRAM.as_warn
bext_time_reference = PROGRAM.bext_time_reference
cache_folder = PROGRAM.cache_folder
clean_old_files = PROGRAM.clean_old_files
ffprobe_json = PROGRAM.ffprobe_json
hashlib = PROGRAM.hashlib
log_aside = PROGRAM.log_aside
number_text = PROGRAM.number_text
os = PROGRAM.os
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
wav_rate = PROGRAM.wav_rate


# Six of the eight are read further down than this piece, so a copy
# taken here would find nothing: channel filter, kept channels, the
# Python note, the quiet remove, the safe wav name, the widest track.

# OUTPUT_SINK is the seventh: the window writes it on the program
# object without telling the pieces, so a copy here would answer with
# the run before. Read as PROGRAM.OUTPUT_SINK where a line is written.

# numpy is the eighth: the program holds a stand-in until the first sum
# asks and binds the real module then, which a copy taken up here would
# never see. So this asks the program once, the same way.
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
    begins with samples marked as not to be played; both go into this
    number. Read out of the file, never assumed -- one camera of three
    on one shoot carried 60,375 ms of it and the other two none.
    """
    # A stream whose lead-in is nowhere declared comes back that much
    # too late, and nothing in it says by how much.
    try:
        rows = [s for s in (ffprobe_json(path).get("streams") or [])
                if s.get("codec_type") == "audio"]
        row = rows[stream or 0] if rows else {}
        return float(row.get("start_time") or 0.0)
    except (IndexError, TypeError, ValueError):
        return 0.0


def audio_on_the_picture(x, path, rate, stream=None):
    """Put decoded samples where the file says they are to be heard.

    Silence in front where the track starts after the picture, the head
    cut away where it starts before it. Only for a decode from the
    front: with -ss ffmpeg already counts from the presentation time.
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

    ffmpeg writes float32 and the default widens it to float64; asking
    for float32 saves a copy of the largest block the program holds.
    The default is None because numpy is fetched at the end of this
    file and cannot stand in a signature.
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
    # What comes back begins where the file says the track begins. With
    # -ss it already does: ffmpeg counts from the presentation time.
    return x if ss is not None else audio_on_the_picture(x, path, rate,
                                                         stream)


_ENV = {}


def decode_audio_long(path, rate, duration, text, stream=None, report=None):
    """Decode audio with progress: a 30 GB file takes minutes."""
    return decode_audio_tracks(path, rate, duration, text, [stream],
                               report)[0]


def decode_audio_tracks(path, rate, duration, text, streams, report=None):
    """Decode several tracks of one file in one pass over the container.

    Track by track reads a 36 GB camera file once per track, and that
    pass is the whole of the waiting; one ffmpeg with a -map per track
    reads it once. One process has one progress stream, so the text has
    to name every track.
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
        # Each track on the time of its own start: a big file must not
        # be placed differently only because it came through here.
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

    A number counted by hand is forgotten, and then the store hands
    back a measurement another recipe wrote. The source of the
    deciding functions is hashed instead: it cannot change silently.
    """
    if name not in _RECIPE_MARKS:
        try:
            import inspect
            text = "".join(inspect.getsource(f) for f in work)
        except Exception:
            # No source to read. The version is coarse -- every release
            # throws the store away -- but never another recipe's.
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

    Or the recipe changes: without that mark a changed recipe reads
    old curves back and compares two never measured the same way.
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

    A curve costs minutes on a large file and nothing when it is found,
    and which of the two happened is invisible from outside. The
    numbers are in the line because the same file at another hop or
    rate is another curve.
    """
    log_aside("%s %s  %-30s %g/%d  %s"
              % (ENV_MARK, time.strftime("%H:%M:%S"),
                 os.path.basename(path)[:30], hop_ms, rate, what))


def video_envelope(path, hop_ms=5.0, rate=4000, report=None):
    """Return the envelope of the video audio track, once per file.

    The cache survives the whole run; the interface warms it while the
    user is still typing. Kept under path_key: the prework warms it
    under the absolute path and the time axis asks under the name the
    file dialog gave, and where those differ the file is read twice.
    """
    api_key = (path_key(path), hop_ms, rate)
    if api_key not in _ENV:
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
            # ffmpeg delivered nothing. Caching that would mark the file
            # unalignable until it next changes, without saying why.
            _ENV.pop(api_key, None)
            raise ValueError(T('no audio data from %s')
                             % os.path.basename(path))
        if cache:
            # Beside it and then moved: two runs at once, or one broken
            # off, must not leave half a curve to be read as a curve.
            try:
                # The suffix has to be .npy: np.save appends one
                # otherwise and the move would miss the file.
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
# How long one band level is read over. 64 ms tells 50 Hz from 100 Hz;
# in the plain curve's 5 ms box hum and voice land in the same value.
BAND_WINDOW_S = 0.064
# A band counts if its loudness moves at least half as much as the
# liveliest band of the recording. Over 38 tracks from four productions
# the mains hum drops out of every one and no real pair got worse.
BAND_MOVES_ENOUGH = 0.5


def band_powers(x, hop_ms=5.0, rate=SR):
    """How much power each band holds at every step of the curve.

    One short spectrum every hop, its bins summed inside the band
    edges. In blocks: a whole episode at once is a matrix of some
    gigabytes, and the answer is the same either way.
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

    A band whose level never changes places nothing, however loud --
    mains hum says the same from the first second to the last. Asked of
    the recording, so no frequency has to be set from outside.
    """
    if not power.size:
        return np.zeros(len(power), dtype=bool)
    move = np.array([float(np.log(np.sqrt(np.asarray(p, float)) + 1e-9).std())
                     for p in power])
    return move >= BAND_MOVES_ENOUGH * (float(move.max()) or 1.0)


def band_envelope(x, hop_ms=5.0, rate=SR):
    """The loudness curve without the bands that carry no movement.

    What envelope() reads in one piece, band by band with the still
    ones left out. Where every band moves alike nothing is left out,
    and this is the same curve through a longer window.
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

    The envelope way needs something loud and quiet to work on, and a
    mixed song holds the same loudness for minutes. This keeps only the
    phase, which a re-recording through a room survives -- on such a
    pair it hit 569.2 s to twelve milliseconds. The sharpness is the
    peak against its neighbours, and the only measure of the answer.
    """
    if len(a) < rate or len(b) < rate:
        return 0.0, 0.0
    n = 1 << int(np.ceil(np.log2(len(a) + len(b))))
    fa = np.fft.rfft(np.asarray(a, float) - np.mean(a), n)
    fb = np.fft.rfft(np.asarray(b, float) - np.mean(b), n)
    both = fb * np.conj(fa)
    # The whitening is the point: every frequency counts the same, so a
    # loud bass drum does not drown out the rest.
    line = np.fft.irfft(both / (np.abs(both) + 1e-12), n)
    # Only lags from -len(a) to +len(b) can be; cutting at n/2 instead
    # put a file starting more than n/2 samples late n samples out.
    k = int(np.argmax(np.concatenate((line[:len(b)],
                                      line[n - len(a) + 1:]))))
    if k >= len(b):
        k -= len(a) + len(b) - 1
    if most_s is not None and abs(k) / float(rate) > most_s:
        return 0.0, 0.0
    sharp = float(line[k] / (line.std() or 1.0))
    return k / float(rate), sharp


def cross_correlate(a, b):
    """Where b sits against a, and how well it fits there.

    The peak is the largest positive one, not the largest by size: an
    envelope is log loudness less its mean, and two that belong together
    rise and fall together. A negative peak is loud where the other is
    quiet, never where they belong, however large. The shorter is looked
    for along the whole of the longer: see stretch_match.
    """
    return best_and_next(a, b)[:2]


def best_and_next(a, b, apart=2000, hop_ms=5.0, with_shared=False,
                  near=None, reach=0):
    """Where b fits a best, and how well the best place elsewhere fits.

    (shift, match, next match): the second is the highest more than
    *apart* steps from the first, 0.0 where there is none. *hop_ms* is
    the curves' step; *with_shared* adds the steps the best place shares;
    *near* and *reach*, in steps, look only that far about one shift.
    """
    a, b = np.asarray(a, float), np.asarray(b, float)
    if min(len(a), len(b)) < 10:
        return (0, 0.0, 0.0, 0) if with_shared else (0, 0.0, 0.0)
    lags, match, shared = stretch_match(a, b, hop_ms, with_shared=True)
    # Ranked by the match weighed by the share of the shorter curve, as
    # ever; weighed by its root, a chance fit over 25 s outranked a true
    # one over 100 s (interview fixture). Reported: the shared match.
    whole = float(max(1, shared.max()))
    score = match * (shared / whole)
    if near is not None:
        score = np.where(np.abs(lags - near) <= reach, score, -np.inf)
    i = int(np.argmax(score))
    if not np.isfinite(score[i]):
        return (0, 0.0, 0.0, 0) if with_shared else (0, 0.0, 0.0)
    far = (np.abs(lags - lags[i]) > apart) & np.isfinite(score)
    # The next place in the best one's terms, so the two compare as scores.
    at_best = shared[i] / whole or 1.0
    found = (int(lags[i]), float(match[i]),
             float(score[far].max() / at_best) if far.any() else 0.0)
    return found + (int(shared[i]),) if with_shared else found


# A camera's match must stand this far above its best place elsewhere.
# Synthetic only, 26.9.2026: unrelated cameras (20 s-2 min vs 6/60 min)
# peaked at 1.44; right ones (40 s+) fell under 1.5 only at a match <=0.52.
MATCH_STANDS_OUT = 1.5

# Hanging over an end, the match times the root of the seconds shared
# has to reach this: 20 s need 0.89, a minute 0.52. Synthetic, 27.9.2026:
# 35 of 415 strangers cleared the two rules above there, none this one.
MATCH_SURE = 4.0


def match_places_it(st):
    """Report whether the loudness curve alone places a camera.

    Its match has to reach the floor and stand clear of the best place
    elsewhere: a short camera finds a chance fit somewhere along an
    hour, and a second place fits nearly as well. A place hanging over
    an end also has to clear chance for what it shares (MATCH_SURE).
    """
    q = st.get("quality", 0.0)
    shared = st.get("shared_s")
    return (q >= CAMERA_MATCH_ENOUGH
            and q >= MATCH_STANDS_OUT * st.get("next_best", 0.0)
            and (not st.get("hangs_over") or shared is None
                 or q * shared ** 0.5 >= MATCH_SURE))


# The least sound a place has to share before it is judged at all, where
# one curve hangs over the other's end. Measured 27.9.2026 on synthetic
# recordings at a camera's edge: 10 s and 20 s placed the same ones.
SHARED_LEAST_S = 20.0


def stretch_match(a, b, hop_ms=5.0, with_shared=False):
    """How well b fits against a at every shift: (shifts, match).

    Each place is judged on the sound the two share there alone, mean
    and loudness taken over that part: counted whole, the part hanging
    over an end drowned a recording sharing a camera's last minute. Less
    than SHARED_LEAST_S or half the shorter matches nothing; *with_shared*
    adds the steps each place shares."""
    nf = 1 << int(np.ceil(np.log2(len(a) + len(b))))
    lags = np.arange(-(len(a) - 1), len(b))
    if len(a) <= len(b):
        a = a - a.mean()
        short, long_, at = a, b, lags
    else:
        b = b - b.mean()
        short, long_, at = b, a, -lags
    m, n = len(short), len(long_)
    cc = np.fft.irfft(np.fft.rfft(b, nf) * np.conj(np.fft.rfft(a, nf)), nf)
    # Where the short curve begins in the long one, and the stretch of
    # each the two share there: short[i0:i1] against long[at+i0:at+i1].
    i0 = np.clip(-at, 0, m)
    i1 = np.clip(n - at, 0, m)
    k = np.maximum(i1 - i0, 0)
    j0, j1 = np.clip(at + i0, 0, n), np.clip(at + i1, 0, n)

    def sums(x, lo, hi):
        """The sum and the sum of squares of x[lo:hi], for every place."""
        c1 = np.concatenate(([0.0], np.cumsum(x)))
        c2 = np.concatenate(([0.0], np.cumsum(x ** 2)))
        return c1[hi] - c1[lo], c2[hi] - c2[lo]

    s1, s2 = sums(short, i0, i1)
    l1, l2 = sums(long_, j0, j1)
    kk = np.maximum(k, 1).astype(float)
    # Each side less its own mean over the shared stretch: cc summed the
    # products there, and the means are taken out of it afterwards.
    shared = cc[lags % nf] - s1 * l1 / kk
    moves_short = s2 - s1 ** 2 / kk
    moves_long = l2 - l1 ** 2 / kk
    # A stretch that does not move -- digital silence -- matches nothing.
    floor = 1e-9 * kk
    still = ((moves_long <= floor * max(float(np.var(long_)), 1e-12))
             | (moves_short <= floor * max(float(np.var(short)), 1e-12)))
    # Of two short curves half the shorter will do: two cameras of twenty
    # seconds rolling two apart share eighteen, and belong together.
    least = max(1, min(int(round(SHARED_LEAST_S * 1000.0 / hop_ms)),
                       m // 2))
    off = still | (k < least)
    scale = np.sqrt(np.where(off, 1.0, moves_short * moves_long))
    match = np.where(off, 0.0, shared / scale)
    return (lags, match, np.where(off, 0, k)) if with_shared else (lags, match)


# How far two blocks of one recording may sit apart by timecode, for
# finding them (material) and joining them: a clock is set wrong by whole
# hours, so half of one catches every such error and lets a real pause by.
BLOCK_GAP_MAX_S = 1800.0


def blocks_within_reach(paths, trs, lengths):
    """Which blocks one recording can reach: (kept indices, [(name, s)]).

    The fence block detection draws, BLOCK_GAP_MAX_S of timecode: past it
    a clock was set wrong, and a join would write hours of silence. Kept
    is the run around the first block handed in -- detection too keeps
    the run around the file it starts from. Each block left out comes
    with how far it lies from that run, in seconds.
    """
    start = [t / float(wav_rate(p) or SR) for t, p in zip(trs, paths)]
    end = [s + n / float(SR) for s, n in zip(start, lengths)]
    runs, reach = [], None
    for i in sorted(range(len(paths)), key=lambda i: start[i]):
        if reach is None or start[i] - reach > BLOCK_GAP_MAX_S:
            runs.append([])
            reach = end[i]
        runs[-1].append(i)
        reach = max(reach, end[i])
    run = [r for r in runs if 0 in r][0]
    first, last = min(start[i] for i in run), max(end[i] for i in run)
    return sorted(run), [(os.path.basename(paths[i]),
                          start[i] - last if start[i] >= last
                          else first - end[i])
                         for i in range(len(paths)) if i not in run]


def join_with_report(paths, target, keep_parts=False):
    """Join the blocks of one recording and say what was found.

    Both paths report through here: how many blocks went together,
    where the gaps are, and whether two overlap instead of following
    each other. A ten-second hole must not pass without a word.
    """
    source, join_info = join_audio_parts(paths, target, keep_parts=keep_parts)
    for name, far in join_info.get("dropped", []):
        print(T('  %s left out -- %s per timecode away from the other '
                'blocks, too far apart for one recording')
              % (name, as_hms(far)))
    if join_info["blocks"] < 2:
        return source, join_info
    if join_info.get("tc"):
        print(T('  %s blocks joined via timecode, start %s')
              % (number_text(join_info["blocks"], 0),
                 timecode_string(join_info["start_s"])))
        for at_s, g in join_info.get("gaps_found", []):
            if g > 0:
                print(T('  Gap of %s at %s -- filled with silence')
                      % (as_hms(g / float(SR)), as_hms(at_s / float(SR))))
            else:
                # A negative gap is an overlap: nothing is filled there,
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
              % number_text(join_info["blocks"], 0))
    return source, join_info


def join_audio_parts(paths, target, keep_parts=False):
    """Join several audio files into one.

    With timecodes on a common axis, gaps filled with silence, a block
    past BLOCK_GAP_MAX_S left out; without, end to end in given order.
    As many channels as the widest, mono copied to both sides here, not
    by ffmpeg, which would take 3 dB off. *keep_parts* writes each
    recording alone too, but only where they overlap.
    """
    paths = list(paths)
    if len(paths) == 1:
        return paths[0], {"blocks": 1, "parts": []}
    channels = PROGRAM.widest_track(paths)
    same = [PROGRAM.channel_filter(PROGRAM.kept_channels(p), channels)
            for p in paths]
    lengths = [sample_count(p) for p in paths]
    trs = [bext_time_reference(p) for p in paths]
    # Two recorders started together write the same number, and a sort
    # by it would then depend on the order the files came in. Equal
    # times mean at the same time, not end to end.
    having_tc = all(t is not None for t in trs)
    # A block hours away is another recording or a clock set wrong: it
    # stays out, as block detection keeps it out, and is said.
    dropped = []
    if having_tc:
        keep, dropped = blocks_within_reach(paths, trs, lengths)
        paths, same, lengths, trs = ([x[i] for i in keep]
                                     for x in (paths, same, lengths, trs))
        if len(paths) == 1:
            return paths[0], {"blocks": 1, "parts": [], "dropped": dropped}
    if having_tc and len(set(trs)) != len(trs):
        order = sorted(range(len(paths)),
                       key=lambda i: (trs[i], os.path.basename(paths[i]).lower()))
        paths = [paths[i] for i in order]
        lengths = [lengths[i] for i in order]
        trs = [trs[i] for i in order]
        same = [same[i] for i in order]

    if having_tc:
        # Stamps count at their file's rate, lengths at the working one,
        # compared in working samples and put back per file in the graph; else
        # two 96 kHz blocks in a row lose a quarter and report a hole between.
        own = dict((p, float(wav_rate(p) or SR)) for p in paths)
        stamp = dict(zip(paths, trs))
        at = [t * SR / own[p] for t, p in zip(trs, paths)]
        entries = list(zip(at, paths, lengths)) if len(set(trs)) != len(trs) \
            else sorted(zip(at, paths, lengths))
        t0, first = entries[0][0], stamp[entries[0][1]]
        total = max(t + n for t, _, n in entries) - t0
        gaps = []
        for (ta, _, na), (tb, _, _) in zip(entries, entries[1:]):
            g = tb - (ta + na)
            if abs(g) > SR // 100:
                gaps.append((int(round(ta + na - t0)), int(round(g))))
        # Overlapping means several microphones ran at once, and then
        # each one is worth a track of its own.
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
            d = int(round((t - t0) * own[p] / SR))
            whole = int(round(total * own[p] / SR))
            f = [PROGRAM.channel_filter(PROGRAM.kept_channels(p), channels)]
            f += ["adelay=delays=%dS:all=1" % d] if d else []
            f += ["apad=whole_len=%d" % whole, "atrim=end_sample=%d" % whole,
                  "asetpts=N/SR/TB"]
            # One decode, two uses: the sum and the track beside it. A
            # filter output can only be read once, hence the split.
            tail = ",asplit=2[t%d][s%d]" % (i, i) if alone else "[t%d]" % i
            chains.append("[%d:a]%s%s" % (i, ",".join(f), tail))
            markers.append("[t%d]" % i)
            if alone:
                writes += (["-map", "[s%d]" % i, "-c:a", "pcm_s24le",
                            "-write_bext", "1", "-metadata",
                            "time_reference=%d" % first]
                           + PROGRAM.wav_safe(alone[i][1])
                           + ["-y", alone[i][1]])
        fc = ";".join(chains) + ";" + "".join(markers) +\
             "amix=inputs=%d:normalize=0[out]" % len(markers)
        shell_quote(["ffmpeg", "-v", "error"] + parts + ["-filter_complex", fc,
            "-map", "[out]", "-c:a", "pcm_s24le", "-write_bext", "1",
            "-metadata", "time_reference=%d" % first]
            + PROGRAM.wav_safe(target) + ["-y", target] + writes)
        # The stamp is counted at the first block's own rate, the way its
        # recorder wrote it: read at SR, a 44.1 kHz 01:00:00:00 is 00:55:07.
        start_s = first / own[entries[0][1]]
        return target, {"blocks": len(paths), "tc": True, "gaps_found": gaps,
                      "start": first, "start_s": start_s,
                      "side_by_side": side_by_side,
                      "parts": alone, "dropped": dropped}

    # In the order they came in: without a timecode that order is the
    # only one there is, and it may come from a hand rather than from a
    # name. Sorting by name again would throw that away.
    row = list(zip(paths, lengths))
    if len(set(same)) == 1 and same[0] == "anull":
        # All alike: the concat demuxer is cheapest and needs no graph.
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
    # Different channel counts: the concat demuxer refuses those, so
    # the blocks are widened first and strung together in the graph.
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


# What the phase way has to beat before it is believed instead of the
# plain one. A floor, not a measured threshold: the one case measured
# came out at 28.7, and the log prints the number every time.
PHASE_SHARP_ENOUGH = 8.0


def align_on_moving_bands(x_video, x_audio, HOP, rate, sample_points,
                          window_s, distance_s):
    """The same way again, on the bands that carry movement.

    Returns what align_envelopes returns, or None where a curve is too
    short. The numbers are the ordinary ones, so the gate that judges
    the first answer judges this one by the same rule.
    """
    curve_video = band_envelope(x_video, HOP, rate)
    curve_audio = band_envelope(x_audio, HOP, rate)
    if len(curve_video) < 10 or len(curve_audio) < 10:
        return None
    return align_envelopes(curve_video, curve_audio, HOP, sample_points,
                           window_s, distance_s, warn=False)


def align_audio_to_video(audio, video, sample_points=None, window_s=20.0,
               distance_s=120.0, phase=True):
    """Return a, b with audio time = a + b * video time.

    *phase* lets the phase way answer where both curves came up empty;
    the caller asks phase_way_on, which is the person's say.
    """
    HOP, rate = 5.0, 4000
    env_video = video_envelope(video, HOP, rate)
    x_audio = decode_audio(audio, rate=rate)
    env_audio = envelope(x_audio, HOP, rate)
    a, b, st = align_envelopes(env_video, env_audio, HOP, sample_points,
                               window_s, distance_s,
                               warn=os.path.basename(audio))
    if sound_places_recording(st):
        return a, b, st
    # The plain way found nothing worth having. Read once here for the
    # second try and for the phase way under it.
    x_video = decode_audio(video, rate=rate)
    second = align_on_moving_bands(x_video, x_audio, HOP, rate,
                                   sample_points, window_s, distance_s)
    if second is not None and fit_places_it(second[2]):
        # Enough sample points, close enough to one line: of 293 foreign
        # pairs not one gets that far, and all 85 real ones do.
        second[2]["from_bands"] = True
        return second
    # Both curves came up empty. The phase way runs only here (the answer
    # was wrong anyway, no sample point backs it) and only on sound said
    # to be mixed: on speech it lays foreign recordings 100 s out.
    if phase:
        where, sharp = phase_align(x_video, x_audio, rate)
        st["phase_s"], st["phase_sharp"] = where, sharp
        if sharp >= PHASE_SHARP_ENOUGH:
            st["from_phase"] = True
            # No drift from this one: it answers where, not how fast, so
            # the factor stays 1.0 and the report calls the drift unknown.
            return where, 1.0, st
    # Both ways came up empty. The numbers still travel back for the
    # log, marked for what they are: a guess, not an alignment. What to
    # do with a file that has no place: see cannot_be_placed.
    st["unplaceable"] = True
    return a, b, st


def phase_way_on(paths, project_type="cut", every=SOUND_SPEECH, each=()):
    """Whether the phase way may place the recording made of *paths*.

    Only a person says so: *each* is {path: value} or (path, value) as
    the file list and --sound-of give it, a mark on any block standing
    for the recording, and *every* the value where none is marked. A
    project that only synchronises takes mixed sound whatever is marked.
    """
    if project_type == "sync":
        return True
    pairs = each.items() if isinstance(each, dict) else (each or ())
    marked = dict((path_key(p), v) for p, v in pairs)
    for p in paths or ():
        if path_key(p) in marked:
            return marked[path_key(p)] == SOUND_MIXED
    return every == SOUND_MIXED


# Below this two envelopes are no match. A floor, not a measured
# threshold: good alignments measure 0.5 to 0.9, and 25 of 293 foreign
# pairs still exceed 0.05, the highest at 0.124 (measured 9.2026).
WEAK_MATCH = 0.05

# The shortest stretch of shared sound and picture a run works with
# when the alignment placed no sample point in it. Ten seconds: 26 s
# of picture comes out exact, and the spacing is a couple of seconds.
AXIS_MIN_WINDOW_S = 10.0

# What one camera has to match another by before it is laid on the
# axis. Far above WEAK_MATCH: between two cameras there is no phase way
# to fall back on, so the envelopes are the whole measurement.

#   camera against camera, 21 s against 26 s      0.837   right
#   camera against camera, 68 min against 68 min  0.811   right
#   an 18-second jingle against 68 min of camera  0.210   nonsense

# A real match sits above 0.8, unrelated material with structure near
# 0.25, and half is the middle of the gap.
CAMERA_MATCH_ENOUGH = 0.5
# The spread separates, not the count: on real cameras 1353 wrong pairs
# never kept more than 10 points within 15 ms, and a right pair shorter
# than about seven minutes cannot reach 50 -- measured 26.9.2026.
FIT_POINTS_ENOUGH = 20
FIT_SPREAD_MS = 15.0


def fit_places_it(st):
    """Report whether the sample points alone place this file.

    The correlation compares two curves over the whole runtime, and a
    steady tone -- mains hum -- pushes it down without moving where the
    file belongs. The fit does move with the answer: many points spread
    over the runtime, all on one line. A file that fits nowhere gets
    neither.
    """
    spread = st.get("spread_ms")
    return (st.get("points", 0) >= FIT_POINTS_ENOUGH
            and spread is not None and spread <= FIT_SPREAD_MS)


# How far one recorder's clock may run from another's before a fit is
# not believed. Right pairs measured at most 133 ppm (synthetic, drift
# 40/60 ppm), wrong ones 484 to 35,000. Only beside the spread.
CLOCK_SPEED_BELIEVED_PPM = 1000.0


def fit_speaks_against(st):
    """Report whether the sample points contradict where the curve put a file.

    Three points or more that scatter beyond FIT_SPREAD_MS, or that lie
    on a line no recorder runs at. Fewer than three say nothing either
    way: short material has none and is still placed right.
    """
    spread = st.get("spread_ms")
    if st.get("points", 0) < 3 or spread is None:
        return False
    return bool(spread > FIT_SPREAD_MS
                or abs(st.get("ppm", 0.0)) > CLOCK_SPEED_BELIEVED_PPM)


# Points on one line that bear out a recording whose match does not
# stand out. 26.9.2026, blocks of 40 s to 10 min: generated, wrong ones
# kept up to 6, none from 7; the fixture's whole recordings reach 18.
RECORDING_POINTS_ENOUGH = 8


def sound_places_recording(st):
    """Report whether the plain loudness curve places a recording.

    Over the floor, not spoken against, and borne out: its match stands
    clear as a camera's does, or enough sample points lie on its line.
    A block of a turn or two finds a place nearly as good elsewhere,
    one or two points agree with anything, and it is refused.
    """
    return (st.get("quality", 0.0) >= WEAK_MATCH
            and not fit_speaks_against(st)
            and (match_places_it(st)
                 or st.get("points", 0) >= RECORDING_POINTS_ENOUGH))


# Against a sound recording a real match reads far lower, so this floor
# only tells a measurement from noise.
SOUND_MATCH_ENOUGH = 0.15
# Not the count of sample points: they are set 30 seconds apart, so
# shorter material has none at all and is still placed exactly right.


def timecode_places_it(own, others):
    """Report whether a timecode can put this file among the others.

    A timecode alone places nothing: it is a reading of a clock, and a
    reading only says something next to a second one. Where a single
    file has one and no other does, it is as unplaced as if it had
    none.
    """
    return own is not None and any(t is not None for t in others)


def clock_base(own, placed):
    """Which camera's clock places one the sound could not place.

    *placed* is [(camera, its clock)] of those the sound put on the
    axis, the reference first; the first carrying a clock is the base,
    never a middle of several, which one wrong clock among two carries
    off. None where *own* is None or no placed camera has a clock.
    """
    if own is None:
        return None
    return next((w for w, t in placed if t is not None), None)


def camera_places_camera(st):
    """Report whether one camera's sound places another: the run's rule.

    Between two cameras there is no phase way, so the curve has to stand
    clear of every other place, or the sample points have to lie on one
    line (match_places_it, fit_places_it).
    """
    return bool(st) and (match_places_it(st) or fit_places_it(st))


def cameras_on_one_axis(curves, clocks=None, warn=True, spread=None,
                        hop_ms=5.0):
    """Which heard camera carries the axis, and where the others sit.

    The run's align_cameras and the window's measure_time_axis both ask
    this. Returns (reference, placed {path: (a, b, st)}, left {path: st}
    of those nothing placed); camera time = a + b * reference time,
    st["via"] the camera a chained one was placed through. *spread* maps
    a function over a list, in parallel where given."""
    # The reference: the longest; of several as long, the one placing
    # most others, then one with a clock, then by path -- never the order
    # given. Unplaced ones are measured against each placed camera.
    clocks = clocks or {}
    spread = spread or (lambda fn, xs: [fn(x) for x in xs])
    heard = sorted(curves, key=path_key)
    if not heard:
        return None, {}, {}
    measured, quiet = {}, set()

    def measure(pair):
        """One camera measured against another: align_envelopes' answer."""
        via, p = pair
        density = int(max(20, min(120, len(curves[via]) * hop_ms
                                  / 1000.0 / 30.0)))
        # Where both clocks read they say where to look first: the second
        # curve's time is the first's plus the first clock less the second.
        hint = (clocks[via] - clocks[p] if clocks.get(via) is not None
                and clocks.get(p) is not None else None)
        try:
            return align_envelopes(
                curves[via], curves[p], hop_ms, sample_points=density,
                distance_s=30.0, near_s=hint,
                warn=(os.path.basename(p) if warn is True
                      and pair not in quiet else False))
        except Exception as e:
            return 0.0, 1.0, {"quality": 0.0, "points": 0,
                              "error": str(e)}

    def fetch(pairs):
        """Measure the pairs not measured yet, together."""
        pairs = [q for q in pairs if q not in measured]
        for q, got in zip(pairs, spread(measure, pairs)):
            measured[q] = got

    longest = max(len(curves[p]) for p in heard)
    tied = [p for p in heard if len(curves[p]) == longest]
    if len(tied) > 1:
        # Only here are several measured as the reference: a tie between
        # whole files is rare, and every pair costs a reading.
        pairs = [(c, p) for c in tied for p in heard if p != c]
        quiet.update(pairs)
        fetch(pairs)

        def standing(c):
            """How a tied camera ranks: most placed, a clock, its path."""
            hits = sum(1 for p in heard if p != c
                       and camera_places_camera(measured[(c, p)][2]))
            return (-hits, clocks.get(c) is None, path_key(c))
        reference = min(tied, key=standing)
    else:
        reference = tied[0]
    placed = {reference: (0.0, 1.0, {"points": 0})}
    fetch([(reference, p) for p in heard if p != reference])
    tried = set([reference])
    while True:
        waiting = [p for p in heard if p not in placed]
        fresh = [w for w in heard if w in placed and w not in tried]
        if not waiting:
            break
        # The ones placed in the round before are asked now; the first
        # round asked the reference.
        if fresh:
            # The weak-match warning was said against the reference.
            pairs = [(w, p) for w in fresh for p in waiting]
            quiet.update(pairs)
            fetch(pairs)
            tried.update(fresh)
        found = {}
        for p in waiting:
            best = None
            for w in sorted(tried, key=path_key):
                if w not in placed or (w, p) not in measured:
                    continue
                st = measured[(w, p)][2]
                if not camera_places_camera(st):
                    continue
                rank = (st.get("quality", 0.0), st.get("points", 0))
                if best is None or rank > best[0]:
                    best = (rank, w)
            if best is not None:
                found[p] = best[1]
        if not found:
            break
        for p, w in found.items():
            a1, b1, st = measured[(w, p)]
            if w == reference:
                placed[p] = (a1, b1, st)
                continue
            av, bv, stv = placed[w]
            st = dict(st)
            st["via"] = w
            b = b1 * bv
            # The drift of the chain: both steps, their errors together.
            if "ppm" in st:
                st["ppm"] = (b - 1.0) * 1e6
                st["ppm_error"] = (st.get("ppm_error", 0.0) ** 2
                                   + stv.get("ppm_error", 0.0) ** 2) ** 0.5
            placed[p] = (a1 + b1 * av, b, st)
    left = dict((p, measured.get((reference, p), (0, 1, {}))[2])
                for p in heard if p not in placed)
    ordered = dict((p, placed[p]) for p in
                   sorted(placed, key=lambda q: (q != reference,
                                                 path_key(q))))
    return reference, ordered, left


def files_with_no_place(weak, clocks):
    """Which of the badly fitting recordings no clock places either.

    The one reading of "it fits nowhere" for a recording; a camera goes
    by clock_base. Weak alone is not it -- a file whose sound says
    nothing is still placed by its timecode -- and below the floor is
    not it either, because a jingle lands above that.
    """
    return [p for p in weak
            if not timecode_places_it(
                clocks.get(p), [t for q, t in clocks.items() if q != p])]


def cannot_be_placed(st, own_tc, other_tcs):
    """Report whether an alignment left a file with no place at all.

    Two ways lead to a place and either is enough: the clock, and the
    measurement, whose verdict "unplaceable" stands in *st*. Never the
    count of sample points -- a measurement with none is still a
    measurement, only without a drift. Where the clock answers the
    sound is not asked, and only where neither does is the file refused.
    """
    if not (st or {}).get("unplaceable"):
        return False
    return not timecode_places_it(own_tc, other_tcs)


def which_way_placed(st, hint=""):
    """Add to a track's note which way put it on the axis.

    The plain loudness curve says nothing, being the ordinary answer;
    the two later ways do, and both report lines use this function so
    they say the same thing. The phase says the drift is unknown
    because the line beside it prints +0.00 ppm, which would otherwise
    read as a drift measured at zero.
    """
    if (st or {}).get("from_bands"):
        hint = (hint + ", " if hint else "") + T('placed on the bands '
                                                 'that move')
    if (st or {}).get("from_phase"):
        hint = (hint + ", " if hint else "") + (
            T('placed by phase, sharpness %s against a floor of %s, '
              'drift unknown')
            % (number_text(float(st.get("phase_sharp") or 0.0), 1),
               number_text(PHASE_SHARP_ENOUGH, 1)))
    return hint


def no_place_message(name):
    """Say that a file cannot be placed, and what would fix it."""
    return T('%s cannot be placed: its sound has nothing in common '
             'with the rest of the material, and the file carries no '
             'timecode. It needs one that fits the other recordings, '
             'and that has to be set with another program.') % name


# How far a point may sit from the middle before it is thrown away. 3
# is the ordinary robust choice; the 20 ms floor is four times HOP --
# what the envelope can resolve -- and saves a tight set from itself.
OUTLIER_SIGMA = 3.0
OUTLIER_FLOOR_S = 0.020
OUTLIER_ROUNDS = 6


def _spans_share(tv, duration_v):
    """How much of the runtime the surviving points still cover.

    A set cleaned down to one corner looks tidy and says nothing about
    the rest of the recording.
    """
    if len(tv) < 2 or duration_v <= 0:
        return 0.0
    return float((max(tv) - min(tv)) / duration_v)


def without_outliers(tv, dt):
    """Throw away points that lie far from the others. (tv, dt, dropped).

    The anchor is the median, not the line: a single outlier tips the
    line and then the wrong points look like the odd ones out. The
    scatter is the median absolute deviation, scaled by 1.4826 to mean
    a standard deviation. Never below three points -- two always fit a
    line perfectly. Every point thrown away is named in the log.
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


# How far either side of where two clocks put a file the search looks
# when the whole of it found no place: clocks were measured two seconds
# apart (E-190), and ten more keep a second place in view to judge by.
CLOCK_HINT_REACH_S = 30.0


def align_envelopes(env_video, env_audio, HOP=5.0, sample_points=None, window_s=20.0,
                       distance_s=120.0, points_off="video", warn=True,
                       near_s=None):
    """The same on ready-made envelopes.

    The second curve's time = a + b * the first curve's time; the first
    is what align_cameras calls the reference. *points_off* picks the
    curve the sample points come off, for a de-bled speaker track the
    second. *near_s*, where two clocks put the second: a hint, asked
    only where the whole search places nothing.
    """
    if len(env_video) < 10 or len(env_audio) < 10:
        raise RuntimeError(T('too little audio to align'))
    if points_off == "audio":
        a, b, st = align_envelopes(env_audio, env_video, HOP, sample_points, window_s,
                                      distance_s, warn=warn)
        return -a / b, 1.0 / b, st
    # The best place elsewhere ten seconds or more away: match_places_it.
    k, g, g_next, shared = best_and_next(env_video, env_audio,
                                         int(round(10000.0 / HOP)), HOP,
                                         with_shared=True)
    hinted = False
    whole_len = min(len(env_video), len(env_audio))
    if near_s is not None and not match_places_it(
            {"quality": g, "next_best": g_next, "shared_s": shared * HOP
             / 1000.0, "hangs_over": shared < whole_len}):
        # The clocks as a hint: the whole search found two places nearly
        # as good, or none; around where the clocks put it, one may stand
        # clear. What is used is still the measurement at that place.
        found = best_and_next(env_video, env_audio,
                              int(round(10000.0 / HOP)), HOP,
                              with_shared=True,
                              near=int(round(near_s * 1000.0 / HOP)),
                              reach=int(round(CLOCK_HINT_REACH_S * 1000.0
                                              / HOP)))
        if match_places_it({"quality": found[1], "next_best": found[2],
                            "shared_s": found[3] * HOP / 1000.0,
                            "hangs_over": found[3] < whole_len}):
            k, g, g_next, shared = found
            hinted = True
    coarse = k * HOP / 1000.0
    # Signed, not by size: see cross_correlate. Said out loud because
    # "found something" and "found it barely" look the same from
    # outside; a second try on the same files asks for silence.
    if warn and g < WEAK_MATCH:
        # warn carries the name where the caller has one. Without it a
        # run with several recordings prints warnings nobody can place.
        print(as_warn(T('      WARNING: weak match for %s (%s, %s is '
                        'the floor). The two may not belong together.')
                      % (warn if isinstance(warn, str)
                         else T('this pair of files'),
                         number_text(g, 3),
                         number_text(WEAK_MATCH, 2))))

    duration_v = len(env_video) * HOP / 1000.0
    W = int(window_s * 1000 / HOP)
    # Twice as many candidates as needed: the uninteresting ones drop
    # out at once, and too many beats too few.
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
        # Silence or steady noise has no edges to align on.
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
                "points": len(points), "next_best": g_next,
                "shared_s": shared * HOP / 1000.0,
                "hangs_over": shared < whole_len}
    if hinted:
        count_n["clock_hint"] = True

    if len(points) >= 3:
        tv = np.array([p[0] for p in points])
        dt = np.array([p[1] for p in points])
        tv, dt, dropped = without_outliers(tv, dt)
        b, a = np.polyfit(tv, dt, 1)
        rest = dt - (a + b * tv)
        n = len(tv)
        sxx = float(((tv - tv.mean()) ** 2).sum())
        s2 = float((rest ** 2).sum()) / max(1, n - 2)
        se_b = (s2 / sxx) ** 0.5 if sxx > 0 else float("inf")
        count_n.update({"ppm": b * 1e6, "ppm_error": se_b * 1e6,
                         "spread_ms": float(np.std(rest) * 1000), "quality": g,
                         "dropped": dropped,
                         "offsets": [float(x) for x in dt],
                         "times": [float(x) for x in tv]})
        return a, 1.0 + b, count_n
    count_n["quality"] = g
    return coarse, 1.0, count_n
