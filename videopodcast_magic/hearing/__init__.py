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
    k = int(np.argmax(line))
    if k > n // 2:
        k -= n
    if most_s is not None and abs(k) / float(rate) > most_s:
        return 0.0, 0.0
    sharp = float(line.max() / (line.std() or 1.0))
    return k / float(rate), sharp


def cross_correlate(a, b):
    """Where b sits against a, and how well it fits there.

    The peak is the largest positive one, not the largest by size. An
    envelope is log loudness with its mean taken out, so it swings
    either side of zero; two that belong together rise and fall
    together. A strong negative peak is loud where the other is quiet,
    and that is never where they belong, however large.
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

    Both paths report through here: how many blocks went together,
    where the gaps are, and whether two overlap instead of following
    each other. A ten-second hole must not pass without a word.
    """
    source, join_info = join_audio_parts(paths, target, keep_parts=keep_parts)
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

    With timecodes on a common axis, gaps filled with silence; without,
    end to end in the order they came in. As many channels as the
    widest, mono copied to both sides here rather than by ffmpeg, which
    would take 3 dB off. With *keep_parts* each recording is written
    alone too, but only where they overlap.
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
    if having_tc and len(set(trs)) != len(trs):
        order = sorted(range(len(paths)),
                       key=lambda i: (trs[i], os.path.basename(paths[i]).lower()))
        paths = [paths[i] for i in order]
        lengths = [lengths[i] for i in order]
        trs = [trs[i] for i in order]
        same = [same[i] for i in order]

    if having_tc:
        # A stamp counts at its file's own rate, a length at the working
        # one: laid against each other in working samples, each put back
        # at its own rate in the graph -- or two 96 kHz blocks in a row
        # come out a quarter short, with a hole said between them.
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
                      "parts": alone}

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
    if st.get("quality", 0.0) >= WEAK_MATCH and not fit_speaks_against(st):
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
    # Both curves came up empty. The phase way runs only here, where
    # the answer was wrong anyway, no sample point backs it up, and only
    # where the sound was said to be mixed: on speech it lays foreign
    # recordings a hundred seconds out.
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


# Below this the agreement between two envelopes is not worth calling a
# match. A floor, not a measured threshold: a good alignment measures
# 0.5 to 0.9, and 25 of 293 foreign pairs still exceed 0.05, the
# highest at 0.124 (measured 9.2026).
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
# Over 85 pairs that belong together against 293 that do not: the
# correlation overlaps (worst real 0.203, best foreign 0.124), the fit
# does not (62 against 43 points, 11.3 against 22.4 ms).
FIT_POINTS_ENOUGH = 50
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


def timecode_seconds(info):
    """The timecode in a video's facts, in seconds, or nothing."""
    if not (info or {}).get("tc"):
        return None
    try:
        return parse_timecode(info["tc"], max(1.0, info.get("fps") or 30.0))
    except (ValueError, TypeError):
        return None


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


def align_envelopes(env_video, env_audio, HOP=5.0, sample_points=None, window_s=20.0,
                       distance_s=120.0, points_off="video", warn=True):
    """The same on ready-made envelopes.

    Which way round: the second curve's time = a + b * the first
    curve's time. Not "reference": align_cameras calls the *first* of
    its two the reference, and that meaning turns the pair round.
    *points_off* picks the curve the sample points come off; for a
    de-bled speaker track the second, where one speaker is left.
    """
    if len(env_video) < 10 or len(env_audio) < 10:
        raise RuntimeError(T('too little audio to align'))
    if points_off == "audio":
        a, b, st = align_envelopes(env_audio, env_video, HOP, sample_points, window_s,
                                      distance_s, warn=warn)
        return -a / b, 1.0 / b, st
    k, g = cross_correlate(env_video, env_audio)
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
                "points": len(points)}

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
