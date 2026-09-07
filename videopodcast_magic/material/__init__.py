# -*- coding: utf-8 -*-
"""The material: which files belong together, and what they measure.

Read out of the folder beside the program by beside(). It cannot import
the file it was cut out of -- that file is still being read -- so the
program is handed in and every name used out of it is bound below.
"""

# beside() puts the program here before this file is read.
PROGRAM = PROGRAM

# What this piece uses out of the program, bound once. Eight names are
# missing; the four blocks under the list say which and why.

AUDIO_SUFFIXES = PROGRAM.AUDIO_SUFFIXES
CAMERA_MATCH_ENOUGH = PROGRAM.CAMERA_MATCH_ENOUGH
COLOURS = PROGRAM.COLOURS
FILE_FORMAT = PROGRAM.FILE_FORMAT
LIKES_PYTHON = PROGRAM.LIKES_PYTHON
MIX_TRACK_NAME = PROGRAM.MIX_TRACK_NAME
SR = PROGRAM.SR
T = PROGRAM.T
TN = PROGRAM.TN
TRAILING_NUMBER = PROGRAM.TRAILING_NUMBER
TYPE_INTRO = PROGRAM.TYPE_INTRO
TYPE_OUTRO = PROGRAM.TYPE_OUTRO
VIDEO_SUFFIXES = PROGRAM.VIDEO_SUFFIXES
align_envelopes = PROGRAM.align_envelopes
as_bad = PROGRAM.as_bad
as_head = PROGRAM.as_head
as_hms = PROGRAM.as_hms
as_warn = PROGRAM.as_warn
bext_time_reference = PROGRAM.bext_time_reference
cannot_be_placed = PROGRAM.cannot_be_placed
colour_arguments = PROGRAM.colour_arguments
data_track_maps = PROGRAM.data_track_maps
datetime = PROGRAM.datetime
decode_audio = PROGRAM.decode_audio
envelope = PROGRAM.envelope
ffprobe_json = PROGRAM.ffprobe_json
file_timecode = PROGRAM.file_timecode
fit_places_it = PROGRAM.fit_places_it
gcc_phat_offset = PROGRAM.gcc_phat_offset
hashlib = PROGRAM.hashlib
math = PROGRAM.math
no_place_message = PROGRAM.no_place_message
number_text = PROGRAM.number_text
os = PROGRAM.os
probe_has = PROGRAM.probe_has
probe_remember = PROGRAM.probe_remember
progress_from_line = PROGRAM.progress_from_line
re = PROGRAM.re
recipe_mark = PROGRAM.recipe_mark
safe_filename = PROGRAM.safe_filename
sample_count = PROGRAM.sample_count
shell_quote = PROGRAM.shell_quote
show_progress = PROGRAM.show_progress
soxr_available = PROGRAM.soxr_available
stop_wanted = PROGRAM.stop_wanted
subprocess = PROGRAM.subprocess
sys = PROGRAM.sys
tempfile = PROGRAM.tempfile
threading = PROGRAM.threading
timecode_moved = PROGRAM.timecode_moved
timecode_seconds = PROGRAM.timecode_seconds
timecode_string = PROGRAM.timecode_string
video_envelope = PROGRAM.video_envelope
video_facts = PROGRAM.video_facts

# Two of the eight stand in a piece read after this one and go through
# PROGRAM: run_ffmpeg_with_progress, and tracks_folder behind it.

# Three are the window's, and channel_rows_build below reaches them
# through PROGRAM where it calls them: channel_rows_fit is the
# window's own, hint and label it takes out of the fittings. None of
# the three stands on the program until a window has been asked for.

# Two are bent while the run goes on: the window sets OUTPUT_SINK and
# ASK_SINK on the program object, a write the pieces are never told
# about, so a copy taken here would hold the value of the run before.

# numpy is the eighth: the program binds the real module only when the
# first sum asks, which a copy taken up there would never see.
class LateNumpy:
    """Stands in for the program's numpy until a sum wants it."""

    def __getattr__(self, name):
        global np
        got = getattr(PROGRAM.np, name)
        np = PROGRAM.np
        return got


np = LateNumpy()


# What the loudness may come to, and how much of it the limiter may
# take off. Nothing else in the program reads either one.
CEILING_DBTP = -1.0       # true-peak ceiling of the result
LIMIT_MAX_DB = 6.0        # most the limiter may take off


#---------------------------------------- Which files belong together

# Date and time in a file name: "r_260808_185628" is the eighth of August
# 2026 at 18:56:28. Six digits for the date or eight, six for the time.
NAME_CLOCK = re.compile(r"(?<![0-9])([0-9]{6}|[0-9]{8})[_\-. ]([0-9]{6})"
                        r"(?![0-9])")
# How far the clock in the name may sit from where the previous block
# ends. Recorders write whole seconds and a block is rarely a whole one,
# so two seconds of slack are needed and no real pair is further apart.
CLOCK_SLACK = 2.0
# How far two blocks of one recording may sit apart per timecode. Half
# an hour is the fence: a clock is set wrong by whole hours, so half of
# the smallest of those catches every one and lets a real pause through.
BLOCK_GAP_MAX_S = 1800.0
# What a track cut out of a multichannel file is called at the end. The
# search for continuations leaves those alone: the number is a channel.
SPLIT_MARK = re.compile(r"_Channel\d+(?:\+\d+)?$")


def clock_in_name(name):
    """Return the moment a file name carries: (seconds, before, after).

    A mixer writes the date and time of day instead of a counter, so it
    is read as a clock and held against the block before it. *before*
    and *after* are the rest of the name, so only like names compare.
    """
    m = NAME_CLOCK.search(name)
    if not m:
        return None
    day, clock = m.group(1), m.group(2)
    shape = "%y%m%d" if len(day) == 6 else "%Y%m%d"
    try:
        when = datetime.datetime.strptime(day + clock, shape + "%H%M%S")
    except ValueError:
        return None
    # Naive on purpose: only the difference between two names is used.
    return (when.replace(tzinfo=datetime.timezone.utc).timestamp(),
            name[:m.start()], name[m.end():])


def blocks_by_clock(file_path):
    """Find the blocks of one recording by the clock in their names.

    Only files built alike count, and the next is the one whose clock
    sits where the previous block ends.
    """
    folder = os.path.dirname(file_path) or "."
    name, ext = os.path.splitext(os.path.basename(file_path))
    mine = clock_in_name(name)
    if not mine:
        return [file_path], []
    when, before, after = mine
    family = {}
    try:
        every = os.listdir(folder)
    except OSError:
        return [file_path], []
    doubled, both = set(), {}
    for f in sorted(every):
        stem, kind = os.path.splitext(f)
        if kind.lower() != ext.lower():
            continue
        other = clock_in_name(stem)
        if not other or other[1] != before or other[2] != after:
            continue
        if other[0] in family:
            # Two files claiming the same moment -- "260808" and
            # "20260808" spell the same day, so neither of them is taken.
            doubled.add(other[0])
            both.setdefault(other[0],
                            [os.path.basename(family[other[0]])]).append(f)
            continue
        family[other[0]] = os.path.join(folder, f)
    said = []
    for moment in doubled:
        family.pop(moment, None)
        for name in both.get(moment, []):
            said.append((name, T('two file names for the same moment -- '
                                 'neither of them is taken')))
    if len(family) < 2 or when not in family:
        return [file_path], said
    row, discarded = [file_path], list(said)

    def follows(a, b):
        """Does the block at moment b start where the one at a ends?"""
        fits, _why = shapes_match(family[a], family[b])
        if not fits:
            return False
        length = sample_count(family[a]) / float(SR)
        return abs((a + length) - b) <= CLOCK_SLACK

    times = sorted(family)
    here = when
    while True:                                   # forwards
        later = [t for t in times if t > here]
        if not later:
            break
        step = later[0]
        if not follows(here, step):
            fits, why = shapes_match(family[here], family[step])
            discarded.append((os.path.basename(family[step]),
                              why if not fits else
                              T('does not start where the block before it '
                                'ends')))
            break
        row.append(family[step])
        here = step
    here = when
    while True:                                   # backwards
        earlier = [t for t in times if t < here]
        if not earlier:
            break
        step = earlier[-1]
        if not follows(step, here):
            fits, why = shapes_match(family[step], family[here])
            discarded.append((os.path.basename(family[step]),
                              why if not fits else
                              T('ends before the next block starts')))
            break
        row.insert(0, family[step])
        here = step
    return row, discarded


def _joins_seamlessly(before, after, row):
    """Report whether `after` continues `before` seamlessly.

    Returns (yes, reason). With timecode the next block has to start
    where the previous ends; without one only the block size is left.
    """
    fits, why = shapes_match(before, after)
    if not fits:
        return False, why
    t_before, t_after = file_timecode(before), file_timecode(after)
    if t_before is not None and t_after is not None:
        gap = t_after - (t_before + sample_count(before) / float(SR))
        # A short pause is filled with silence on assembly. A long one
        # is a clock that was never set: joined, it becomes hours of
        # silence inside the file that nothing afterwards takes out.
        if gap > BLOCK_GAP_MAX_S:
            return False, (T('gap of %s per timecode, too far apart for '
                             'one recording') % as_hms(gap))
        return gap > -1.0, (T('overlap of %s per timecode')
                               % as_hms(abs(gap)))
    # The candidate belongs in the comparison, or the first step compares
    # a block with itself and a short take before the take is glued on.
    sizes = [os.path.getsize(p) for p in row]
    sizes += [os.path.getsize(before), os.path.getsize(after)]
    return (os.path.getsize(before) >= 0.98 * max(sizes),
            T('previous block is shorter than the rest'))


def find_continuation_files(file_path):
    """Find every block of the same recording, forwards and backwards.

    Only seamless continuations are appended, and the same test applies
    both ways, so it makes no difference which block is picked.
    """
    folder = os.path.dirname(file_path) or "."
    name, ext = os.path.splitext(os.path.basename(file_path))
    # A track cut out of a multichannel file ends in a channel number,
    # and the next number is another microphone, not the next block.
    if SPLIT_MARK.search(name):
        return [file_path], []
    # A clock in the name is the more specific reading and comes first:
    # stepping a time of day by one looks for a file a second later.
    by_clock = None
    if clock_in_name(name):
        row, discarded = blocks_by_clock(file_path)
        if len(row) > 1:
            return row, discarded
        # Nothing joined by the clock -- it may be the session start,
        # written into every block, with the real index behind it. So
        # the counter rule gets its turn, and the clock's find is kept.
        by_clock = (row, discarded)
    m = TRAILING_NUMBER.match(name)
    if not m:
        return by_clock or ([file_path], [])
    stem, digits = m.group(1), m.group(2)
    width = len(digits)
    row, discarded = [file_path], []
    # Exactly as written, no other spelling: on a case-sensitive disc
    # REC0002.wav and rec0002.wav are two files, and taking one for the
    # other answers differently depending on the folder listing.
    every = set(os.listdir(folder))

    def neighbour(index_number):
        for b in (width, 0):
            nm = ("%s%0*d%s" % (stem, b, index_number, ext)) if b else\
                 ("%s%d%s" % (stem, index_number, ext))
            if nm in every:
                return os.path.join(folder, nm)
        return None

    index_number = int(digits)
    while True:                                   # forwards
        index_number += 1
        candidate = neighbour(index_number)
        if not candidate:
            break
        matches, reason = _joins_seamlessly(row[-1], candidate, row)
        if not matches:
            discarded.append((os.path.basename(candidate), reason))
            break
        row.append(candidate)

    index_number = int(digits)
    while index_number > 0:                             # backwards
        index_number -= 1
        candidate = neighbour(index_number)
        if not candidate:
            break
        matches, reason = _joins_seamlessly(candidate, row[0], row)
        if not matches:
            discarded.append((os.path.basename(candidate), reason))
            break
        row.insert(0, candidate)
    if len(row) == 1 and by_clock and by_clock[1]:
        # The counter found nothing either, so the clock's answer wins.
        return by_clock
    return row, discarded


def track_order_for_camera(own, every, singles=()):
    """Return the audio tracks for one camera, in order.

    Track 1 is the finished mix for this camera, so taking only the first
    is correct; then the same speakers, the overall mix minus the
    crosstalk, and last the camera microphone.
    """
    sequence = []
    if own:
        sequence.append('Mix %s' % " + ".join(own)
                     if len(own) > 1 else own[0])
        if len(own) > 1:
            sequence += list(own)
    else:
        sequence.append(MIX_TRACK_NAME)
        sequence += list(singles)
    if every and own and set(own) != set(every):
        sequence.append(MIX_TRACK_NAME)
    sequence.append("Camera Original")
    return sequence


def find_pauses(tracks):
    """Merge all speech blocks and return the gaps between them."""
    every = sorted((a, b) for _, segs in tracks for a, b in segs)
    merged = []
    for a, b in every:
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    pauses = [(merged[i][1], merged[i + 1][0])
              for i in range(len(merged) - 1)]
    entries_in = {n: sorted(a for a, _ in segs) for n, segs in tracks}
    return pauses, entries_in


# =====================================================================
#  What the cut is decided by -- the rules a human editor follows on
#  top of "whoever speaks is on screen". Every number is adjustable.
# =====================================================================


def format_complaint(d):
    """Say why a stored file cannot be used, or return "".

    Where the format number differs the keys inside mean something else,
    and reading it anyway would quietly assign the wrong things.
    """
    if not isinstance(d, dict):
        return T("This is not a file of this program.")
    present = int(d.get("format") or 1)
    if present == FILE_FORMAT:
        return ""
    return T("This file was written by version %s in format %d; this one "
             "writes format %d. The names inside have changed since, so it "
             "cannot be read. Please set the run up again.",
             d.get("version") or "?", present, FILE_FORMAT)


def ask_choice(possible, heading, title=T('Question'), default_value=None,
               switch="--auphonic-resume"):
    """Ask a question -- in the terminal, in the GUI or via a switch.

    *options* is [(key, text)] and the key comes back. *switch* preselects
    the answer and is named where nobody is there to answer.
    """
    print("\n  %s" % heading)
    for i, (_, text) in enumerate(possible, 1):
        print("    %d  %s" % (i, text))
    api_key = [k for k, _ in possible]

    def write_out(label, choice):
        """Show the visible text rather than the internal key."""
        for i, (k, text) in enumerate(possible, 1):
            if k == choice:
                print("  %s: %d  %s" % (label, i, text.split("\n")[0]))
                return
        print("  %s: %s" % (label, choice))

    if default_value in api_key:
        write_out(T('Given'), default_value)
        return default_value
    if PROGRAM.ASK_SINK is not None:
        choice = PROGRAM.ASK_SINK(possible, title)
        write_out(T('Chosen'), choice)
        return choice
    if not sys.stdin.isatty():
        raise RuntimeError(
            T('No input possible. Use %s %s to set what should happen.') % (switch, "|".join(api_key)))
    while True:
        answer = input(T('  Number: ')).strip()
        if answer.isdigit() and 1 <= int(answer) <= len(possible):
            write_out(T('Chosen'), possible[int(answer) - 1][0])
            return possible[int(answer) - 1][0]
        print(T('  Please give a number between 1 and %d.') % len(possible))


# What a camera carries beyond the time window at each end. A second is
# more than twenty times the error the run's own cross-check tolerates,
# and at the front the key frame usually swallows it anyway.
CAMERA_MARGIN_S = 1.0


def key_frame_at_or_before(video, when):
    """Where the last key frame at or before *when* seconds sits.

    A stream copy starting between two key frames takes the picture from
    the one before while the sound starts where asked, a group of
    pictures apart. So the cut goes back, never forward; 0.0 if none.
    """
    if when <= 0:
        return 0.0
    for reach in (10.0, 120.0, 1200.0):
        begin = max(0.0, when - reach)
        try:
            p = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "v:0",
                 "-skip_frame", "nokey", "-show_entries", "frame=pts_time",
                 "-of", "csv=p=0", "-read_intervals",
                 "%.3f%%%.3f" % (begin, when + 0.001), video],
                capture_output=True, timeout=300)
        except Exception as e:
            print(T('  Key frames of %s cannot be read (%s) -- the copy '
                    'starts at the beginning of the file.')
                  % (os.path.basename(video), str(e)[:60]))
            return 0.0
        found = []
        for line in p.stdout.decode("utf-8", "replace").splitlines():
            try:
                seconds = float(line.strip().rstrip(","))
            except ValueError:
                continue
            if seconds <= when + 1e-6:
                found.append(seconds)
        if found:
            return max(found)
        if begin <= 0:
            break
    return 0.0


def camera_window_cut(video, duration, offset, window_s):
    """Which stretch of a camera a time window leaves: (cut_at, keep_s).

    *offset* is where the camera's first frame sits in programme time.
    The copy starts on the key frame before the window, the end is cut
    where the window ends, and keep_s is None where neither end gives.
    """
    first = max(0.0, -offset - CAMERA_MARGIN_S)
    last = min(duration, window_s - offset + CAMERA_MARGIN_S)
    cut_at = key_frame_at_or_before(video, first)
    if cut_at <= 0 and last >= duration - 0.001:
        return 0.0, None
    return cut_at, max(1.0, last - cut_at)


def camera_stamp(info, cut_at, at_s):
    """The timecode a written camera file carries, or nothing.

    *at_s* is where its first frame sits on the wall clock, the reckoning
    every camera gets, written at this camera's own rate. Without it the
    camera's own timecode is moved by the cut and stands alone again.
    """
    fps = max(1.0, info.get("fps") or 30.0)
    if at_s is not None:
        return timecode_string(at_s, fps)
    return timecode_moved(info["tc"], cut_at, fps) if info.get("tc") else ""


def write_camera_file(video, info, audio_tracks, target, a, b, drift, args,
                 head_s=0, tail_s=0, cut_at=0.0, keep_s=None, at_s=None):
    """Write a new video file carrying several audio tracks.

    *audio_tracks* is [(name, path)]; all get the same offset and clock
    correction, so they stay as aligned as they were. *head_s* and
    *tail_s* trim samples front and back before the offset; *cut_at* and
    *keep_s* say which stretch of the camera is written.
    """
    kept = keep_s if keep_s else info["duration"] - cut_at
    n_video = int(round(kept * SR))
    if drift and abs(b - 1.0) > 1e-7:
        intro = rate_filter_chain(b) + ","
        k = int(round(a / b * SR))
    else:
        intro, k = "", int(round(a * SR))
    cut = ("atrim=start_sample=%d,asetpts=N/SR/TB," % k) if k > 0 else\
              ("adelay=delays=%dS:all=1," % (-k)) if k < 0 else ""
    cmd = ["ffmpeg", "-v", "warning", "-nostats"]
    # Both in front of the input, so they cut the camera alone: the
    # tracks that follow are inputs of their own.
    if cut_at > 0:
        cmd += ["-ss", "%.6f" % cut_at]
    if keep_s:
        cmd += ["-t", "%.6f" % keep_s]
    cmd += ["-i", video]
    chains, map_args = [], ["-map", "0:v"]
    for i, (_, file_path) in enumerate(audio_tracks):
        cmd += ["-i", file_path]
        edge = ""
        if head_s or tail_s:
            edge = ("atrim=start_sample=%d:end_sample=%d,asetpts=N/SR/TB,"
                    % (head_s, sample_count(file_path) - tail_s))
        chains.append("[%d:a]%s%s%sapad=whole_len=%d,atrim=end_sample=%d,"
                      "asetpts=N/SR/TB[t%d]"
                      % (i + 1, edge, intro, cut, n_video, n_video, i))
        map_args += ["-map", "[t%d]" % i]
    n_camera = 0
    if not args.no_camera_audio:
        for i in range(len(info["audio"])):
            map_args += ["-map", "0:a:%d" % i]
        n_camera = len(info["audio"])
    # Behind the audio, so every track above keeps its place.
    data_maps = data_track_maps(video)
    map_args += data_maps
    cmd += ["-filter_complex", ";".join(chains)] + map_args
    if data_maps:
        cmd += ["-c:d", "copy"]
    # use_metadata_tags keeps the camera's QuickTime keys, where Resolve
    # reads device and input colour space. No write_colr: a colr box
    # travels either way, and the switch invents 2/2/2 where none is.
    cmd += ["-c:v", "copy"] + colour_arguments(video)
    cmd += ["-map_metadata", "0", "-movflags", "+use_metadata_tags"]
    for i in range(len(audio_tracks)):
        cmd += ["-c:a:%d" % i, "pcm_s24le"]
    for i in range(n_camera):
        cmd += ["-c:a:%d" % (len(audio_tracks) + i), "copy"]
    for i, (name, _) in enumerate(audio_tracks):
        cmd += ["-metadata:s:a:%d" % i, "title=%s" % name,
                "-metadata:s:a:%d" % i, "handler_name=%s" % name,
                "-disposition:a:%d" % i, "default" if i == 0 else "0"]
        if args.speech_language:
            cmd += ["-metadata:s:a:%d" % i, "language=%s" % args.speech_language]
    for i in range(n_camera):
        nm = args.name_camera if n_camera == 1 else "%s %d" % (args.name_camera,
                                                               i + 1)
        j = len(audio_tracks) + i
        cmd += ["-metadata:s:a:%d" % j, "title=%s" % nm,
                "-metadata:s:a:%d" % j, "handler_name=%s" % nm,
                "-disposition:a:%d" % j, "0"]
        if args.speech_language_camera:
            cmd += ["-metadata:s:a:%d" % j, "language=%s" % args.speech_language_camera]
    stamp = camera_stamp(info, cut_at, at_s)
    if stamp:
        # ffmpeg carries the source timecode through unchanged however
        # much is cut off the front, so the real start is written here.
        cmd += ["-timecode", stamp]
    cmd += ["-y", target]
    PROGRAM.run_ffmpeg_with_progress(
        cmd, kept, T('Writing %s') % os.path.basename(target))


def measure_loudness(file_path, duration=None, text_progress_bar=None):
    """Measure programme loudness and true peak to EBU R128."""
    cmd = ["ffmpeg", "-nostats", "-i", file_path, "-af", "ebur128=peak=true",
           "-f", "null", "-"]
    if not text_progress_bar:
        p = subprocess.run(cmd, capture_output=True)
        text = p.stderr.decode("utf-8", "replace")
    else:
        # ebur128 writes one line per second to stderr, so reading stdout
        # first would fill its buffer: stderr goes to a file, not a pipe.
        cmd = cmd[:1] + ["-progress", "pipe:1"] + cmd[1:]
        fd, log = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        try:
            with open(log, "wb") as f:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=f)
                show_progress(text_progress_bar, 0.0)
                for line in proc.stdout:
                    share = progress_from_line(line, duration)
                    if share is not None:
                        show_progress(text_progress_bar, share)
                proc.wait()
            with open(log, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        finally:
            try:
                os.unlink(log)
            except OSError:
                pass
        show_progress(text_progress_bar, 1.0)
        if PROGRAM.OUTPUT_SINK:
            PROGRAM.OUTPUT_SINK("\n")
        else:
            sys.stdout.write("\n")
    def get(label):
        hit = re.findall(label + r":\s*(-?\d+(?:\.\d+)?)", text)
        return float(hit[-1]) if hit else None
    # LRA comes from the same pass: how far quiet and loud passages lie
    # apart. For speech 3 to 7 LU is usual; below that it sounds squashed.
    return get(r"I"), get(r"Peak"), get(r"LRA")


def remove_slow_level_drift(env, window=600):
    """Remove slow level changes from an envelope.

    A leveler changes loudness over time, so envelopes from before and
    after look like different signals though the onsets sit in the same
    places. Subtracting the moving average leaves the onsets.
    """
    if len(env) < window * 2:
        return env
    kernel = np.ones(window) / window
    return env - np.convolve(env, kernel, mode="same")


def refine_offset(axis, done, a, b, rate=16000, how_many=9):
    """Measure the remaining offset between upload and returned file.

    Envelopes on a 5 ms grid get no closer than a few milliseconds, so
    the same voice is compared directly in both files: the runtime is
    split into sections and the loudest second of each used. In ms.
    """
    try:
        coarse = np.asarray(decode_audio(axis, rate=4000), dtype=np.float64)
    except Exception:
        return None
    nb = 4000
    count = len(coarse) // nb
    if count < how_many:
        return None
    level = np.array([float(np.sqrt((coarse[k * nb:(k + 1) * nb] ** 2).mean()))
                      for k in range(count)])
    loud = float(np.percentile(level[level > 0], 90)) if (level > 0).any() \
        else 0.0
    if loud <= 0:
        return None
    spots = []
    for k in range(how_many):
        begins, until = count * k // how_many, count * (k + 1) // how_many
        if until <= begins:
            continue
        best = begins + int(np.argmax(level[begins:until]))
        if level[best] > loud * 0.3:
            spots.append(best)
    values = []
    for t in spots:
        try:
            x = decode_audio(axis, rate=rate, ss=max(0.0, t - 0.5), duration=2.0)
            y = decode_audio(done, rate=rate,
                           duration=2.0, ss=max(0.0, a + b * (t - 0.5)))
        except Exception:
            continue
        n = min(len(x), len(y))
        if n < rate:
            continue
        x = np.asarray(x[:n], dtype=np.float64)
        y = np.asarray(y[:n], dtype=np.float64)
        ms, sharpness = gcc_phat_offset(x, y, rate)
        if sharpness >= 10:
            values.append(ms)
    if len(values) < 3:
        return None
    return float(np.median(values))


def verify_returned_tracks(tracks, window_length2, tmpdir):   # noqa: C901
    """Check what Auphonic returns against what was uploaded.

    The service can prepend material and change the length, either of
    which would undo the alignment. De-bleeding and the leveler change
    the signal, so the sample points are picked on the processed track,
    the envelopes flattened, and the estimate a median.
    """
    print(as_head(T('\nCHECK THE RETURN')))
    HOP, rate = 5.0, 4000
    shaky = []
    # A stereo track coming back with one channel was folded at
    # auphonic.com, and no later step can undo that. Not an error, but
    # it has to be said: the two microphones' difference is gone.
    folded = [track["name"] for track in tracks
              if track.get("done") and kept_channels(track["axis"]) == 2
              and kept_channels(track["done"]) == 1]
    if folded:
        print(as_warn(TN(len(folded),
                         '  %s went up in stereo and came back in one '
                         'channel.',
                         '  %s went up in stereo and came back in one '
                         'channel each.') % ", ".join(folded)))
        print(T('  auphonic.com folded them. The mix keeps the two '
                'channels; what is gone is the\n  difference between the '
                'two microphones of that track.'))
    for track in tracks:
        done = track.get("done")
        if not done:
            continue
        n_fresh = sample_count(done) / float(SR)
        try:
            env_old = remove_slow_level_drift(envelope(decode_audio(track["axis"], rate=rate),
                                         HOP, rate))
            env_fresh = remove_slow_level_drift(envelope(decode_audio(done, rate=rate),
                                         HOP, rate))
            # Sample points on the processed track, not the uploaded
            # one: after de-bleeding only one speaker is left, and the
            # passages now empty would dominate a whole-length compare.
            density = int(max(20, min(120, len(env_fresh) * HOP / 1000.0 / 30.0)))
            a_corr, b_corr, st = align_envelopes(env_old, env_fresh, HOP,
                                                sample_points=density,
                                                distance_s=30.0,
                                                warn=os.path.basename(done),
                                                points_off="audio")
        except Exception as e:
            print(T('  %-20s not measurable: %s') % (track["name"], e))
            if track.get("edge"):
                # Without a measurement only the computed edge is left.
                target = os.path.join(tmpdir,
                                    "ready_%s.wav" % safe_filename(track["name"]))
                track["ready"] = place_track_on_axis(done, target, track["edge"], 1.0,
                                              0.0, window_length2, drift=False)
            else:
                track["ready"] = done
            continue
        # Median, not a regression line: Auphonic shifts a track as a
        # whole or not at all, so there is no slope to estimate.
        offsets = st.get("offsets") or []
        times = st.get("times") or []
        clock_drift, clock_drift_ppm = 1.0, 0.0
        if offsets:
            v = np.array(offsets)
            a_corr = -float(np.median(v))
            spread = float(np.median(np.abs(v - np.median(v))) * 1000)
            # A returned file drifting against the uploaded one carries
            # clock drift, which a fixed offset cannot mend.
            if len(v) >= 20 and len(times) == len(v):
                t = np.array(times)
                slope, axis = np.polyfit(t, v, 1)
                rest = v - (axis + slope * t)
                if (abs(slope) * 1e6 > 2.0
                        and float(np.std(rest) * 1000) < 30.0):
                    clock_drift = 1.0 / (1.0 + slope)
                    clock_drift_ppm = (clock_drift - 1.0) * 1e6
                    a_corr = -axis / (1.0 + slope)
                    spread = float(np.median(np.abs(rest)) * 1000)
        else:
            spread = st.get("spread_ms", 0.0)
        # Where the file was coarsely trimmed to a window set later there
        # is deliberate slack at both ends. Measured on the voice, not the
        # envelope: a second voice becomes audible from about 20 ms.
        fine = refine_offset(track["axis"], done, a_corr, clock_drift)
        if fine is not None and abs(fine) < 500.0:
            a_corr += fine / 1000.0
        edge = track.get("edge", 0.0)
        ms = (a_corr - edge) * 1000.0
        track["drift_ppm"] = clock_drift_ppm
        track["offset_ms"] = ms
        track["residual_ms"] = spread
        length = n_fresh - 2 * edge - window_length2
        remark = ""
        if edge or abs(ms) > 5 or abs(length) > 0.05 or clock_drift_ppm:
            target = os.path.join(tmpdir, "ready_%s.wav" % safe_filename(track["name"]))
            place_track_on_axis(done, target, a_corr, clock_drift, 0.0, window_length2,
                           drift=bool(clock_drift_ppm))
            track["ready"] = target
            remark = (T('  -->  aligned, clock drift %s ppm taken out')
                      % number_text(clock_drift_ppm, 1, plus=True)) \
                if clock_drift_ppm \
                else T('  -->  aligned')
        else:
            track["ready"] = done
        uncertain = st.get("points", 0) < 5 or spread > 150.0
        line = (T('  %-20s offset %s ms%s, length %s s, spread %s '
                  'ms, %s of %s points%s%s')
                % (track["name"], number_text(ms, plus=True),
                   "" if fine is None else T(' (fine: %s ms)')
                   % number_text(fine, 1, plus=True),
                   number_text(length, 3, plus=True),
                   number_text(spread, 0),
                   number_text(st.get("points", 0), 0),
                   number_text(st.get("candidates", 0), 0), remark,
                   T('   Caution: measurement unusable') if uncertain else ""))
        print(as_warn(line) if uncertain else line)
        if uncertain:
            shaky.append(track["name"])
    if shaky:
        print(T('\n  For %s it could not be established whether the return '
                'matches the\n  upload. Better to stop than to write '
                'something wrong.') % ", ".join(shaky))
        return False
    return True


def find_master_file(*places):
    """Find the finished mixdown from auphonic.com, if it came along."""
    for place in places:
        if not place:
            continue
        for folder in (PROGRAM.tracks_folder(place, create=False), place):
            try:
                names = sorted(os.listdir(folder))
            except OSError:
                continue
            for n in names:
                small = n.lower()
                if ("master" in small and small.endswith(".wav")
                        and not small.startswith("final_")):
                    return os.path.join(folder, n)
    return None


def remove_quietly(path):
    """Delete a working file. Returns whether it went.

    A file already gone is not a fault, but the answer is handed back
    rather than swallowed, for a caller that does care.
    """
    try:
        os.unlink(path)
    except OSError:
        return False
    return True


def normalise_loudness(tracks, target_lufs, tmpdir, master=None, channels=1):
    """Compute one common gain for all tracks.

    The sum is measured, not the single track, and the same gain goes on
    every track so the speakers keep the balance Auphonic set. The
    finished mixdown is the yardstick; *target_lufs* None still measures.
    """
    print(as_head(T('\nNORMALISE')))
    keep = target_lufs is None
    after_yardstick = False
    if master and os.path.exists(master) and not keep:
        m_have, m_peak, _m_lra = measure_loudness(master, None, T('Measuring the '
                                                                  'yardstick'))
        if m_have is not None:
            after_yardstick = True
            print(T('  Mixdown from auphonic.com: %s LUFS, peak %s '
                    'dBTP (%s)')
                  % (number_text(m_have, 1),
                     number_text(m_peak if m_peak is not None else 0.0, 1),
                     os.path.basename(master)))
            target_lufs = m_have
    total_sum = os.path.join(tmpdir, "measure_sum.wav")
    ready = [track["ready"] for track in tracks]
    # Measured in the form it is delivered in: a two channel mix sits a
    # good three decibels above the same mix as one track, and a stereo
    # track raises the count on its own.
    channels = max(channels, widest_track(ready))
    parts, chains, markers = [], [], []
    for i, path in enumerate(ready):
        parts += ["-i", path]
        chains.append("[%d:a]%s[m%d]"
                      % (i, channel_filter(kept_channels(path), channels), i))
        markers.append("[m%d]" % i)
    fc = ";".join(chains) + ";" + "".join(markers) +\
        "amix=inputs=%d:normalize=0[out]" % len(markers)
    duration = sample_count(tracks[0]["ready"]) / float(SR)
    # One track with nothing to do to its channels is its own sum, and
    # summing it copies hours of audio for the same samples. *ours* says
    # whether this run made the file -- only then may it be deleted.
    ours = not (len(ready) == 1 and "anull" in chains[0])
    measured_on = total_sum if ours else ready[0]
    if ours:
        PROGRAM.run_ffmpeg_with_progress(
            ["ffmpeg", "-v", "error"] + parts + ["-filter_complex", fc,
             "-map", "[out]", "-c:a", "pcm_s24le"]
                + wav_safe(total_sum) + ["-y", total_sum],
            duration, T('Building the sum'))
    have, peak, lra_range = measure_loudness(measured_on, duration,
                                            T('Measuring loudness'))
    if have is None:
        print(T('  Loudness not measurable -- it stays as it is.'))
        return 0.0, None
    if keep:
        print(T('  Sum of tracks:     %s LUFS, peak %s dBTP%s')
              % (number_text(have, 1),
                 number_text(peak if peak is not None else 0.0, 1),
                 T(', range %s LU') % number_text(lra_range, 1)
                 if lra_range is not None else ""))
        print(T('  Not adjusted:      taken from the source files -- no gain '
                'on any track and no\n                     limiter. The '
                'sound leaves exactly as it came in.'))
        if ours:
            remove_quietly(total_sum)
        return 0.0, None
    gain = target_lufs - have
    print(T('  Sum of tracks:     %s LUFS, peak %s dBTP%s')
          % (number_text(have, 1),
             number_text(peak if peak is not None else 0.0, 1),
             T(', range %s LU') % number_text(lra_range, 1)
             if lra_range is not None else ""))
    print(T('  Target:            %s LUFS  ->  %s dB on every track')
          % (number_text(target_lufs, 1),
             number_text(gain, 1, plus=True)))
    # Without a ceiling the gain would have to drop for the loudest peak
    # alone -- a scraping chair costs eight decibels. So a limiter.
    if peak is not None and gain > CEILING_DBTP - peak:
        print(T('  Peaks:             %s dB above %s dBTP -- the '
                'limiter catches them')
              % (number_text(peak + gain - CEILING_DBTP, 1, plus=True),
                 number_text(CEILING_DBTP, 1)))
    # How much the limiter takes off is known only once the curve is
    # computed. More than a handful of decibels means the target does not
    # fit the material, and then quieter beats squashed.
    curve, gone = limiter_curve(measured_on, tmpdir, gain)
    # With the finished mixdown from auphonic.com beside it, that is how
    # much limiting it needed itself, so nothing here needs capping.
    limit = 12.0 if after_yardstick else LIMIT_MAX_DB
    if gone > limit + 0.05:
        back = gone - limit
        print(T('  Too much:          the limiter would have to take %s '
                'dB away. More than %s dB\n                     sounds '
                'squashed -- %s dB less gain.')
              % (number_text(gone, 1), number_text(limit, 0),
                 number_text(back, 1)))
        gain -= back
        curve, gone = limiter_curve(measured_on, tmpdir, gain)
        print(T('  Remains:           %s dB on every track, that is '
                '%s LUFS instead of %s')
              % (number_text(gain, 1, plus=True),
                 number_text(have + gain, 1),
                 number_text(target_lufs, 1)))
    if gone > 0.05:
        print(T('  Limiter:           at most %s dB, the same curve on '
                'every track%s')
              % (number_text(gone, 1),
                 T(' (auphonic.com takes the same amount)')
                 if after_yardstick else ""))
    # For checking in the editor. -16 LUFS is the figure for web and
    # podcast; broadcast measures against -23 and the meter reads higher.
    print(T('  Result:            about %s LUFS, peak %s dBTP')
          % (number_text(have + gain, 1),
             number_text(CEILING_DBTP if gone > 0.05
                         else min(CEILING_DBTP, (peak or 0.0) + gain), 1)))
    # The loudness range measures whether any dynamics are left, and
    # where it gets small something before the limiter squashed it.
    if lra_range is not None:
        if lra_range < 2.0:
            print(as_warn(T('  Caution: range      only %s LU -- very '
                            'tight. Speech is usually 3 to 7 LU;\n          '
                            '           below that it sounds squashed. '
                            'Check how strongly the leveler\n               '
                            '      is set at auphonic.com.')
                          % number_text(lra_range, 1)))
        else:
            print(T('  Range:             %s LU (speech is usually 3 to '
                    '7 LU)') % number_text(lra_range, 1))
    if ours:
        remove_quietly(total_sum)
    return gain, curve


def limiter_curve(total_sum, tmpdir, gain, ceiling=CEILING_DBTP):
    """Compute the limiter gain curve once, on the sum.

    The same curve goes on every track, so they add up to exactly the mix
    again: (a+b)*g equals a*g + b*g, where a limiter per track would
    clamp the loud one harder. Block by block with one block of lookahead
    and a linear cross-fade, or it clicks. Returns (path, reduction dB).
    """
    if np is None:
        return None, 0.0
    channels = max(1, channel_count(total_sum))
    limit = 10.0 ** (ceiling / 20.0)
    BLOCK = 256                       # 5.3 ms at 48 kHz
    RECOVERY = math.exp(-BLOCK / (SR * 0.050))    # 50 ms back up
    source = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", total_sum,
         "-af", "volume=%.3fdB" % gain,
         "-f", "f32le", "-ac", str(channels), "-ar", str(SR), "-"],
        stdout=subprocess.PIPE)
    raw = os.path.join(tmpdir, "level_curve.raw")
    target = os.path.join(tmpdir, "level_curve.wav")
    smallest, status, rest, done = 1.0, 1.0, b"", False
    frame_bytes = 4 * channels
    try:
        with open(raw, "wb") as f:
            while not done:
                chunk = source.stdout.read(1 << 20)
                done = not chunk
                data = rest + chunk
                whole_blocks = len(data) // (frame_bytes * BLOCK)
                if not done:
                    # The last block waits for the next chunk: without
                    # it the peak comes through a tenth of a second early.
                    whole_blocks = max(0, whole_blocks - 1)
                    full = whole_blocks * frame_bytes * BLOCK
                else:
                    full = len(data) - len(data) % frame_bytes
                rest = data[full:]
                if full <= 0:
                    continue
                frames = np.frombuffer(data[:full],
                                       dtype="<f4").reshape(-1, channels)
                count = int(math.ceil(frames.shape[0] / float(BLOCK)))
                needed = np.ones(count, dtype=np.float64)
                for k in range(count):
                    piece = frames[k * BLOCK:(k + 1) * BLOCK]
                    peak = (float(np.max(np.abs(piece)))
                              if piece.size else 0.0)
                    if peak > limit:
                        needed[k] = limit / peak
                # One block of lookahead: the reduction is in place first.
                before = np.minimum(needed, np.roll(needed, -1))
                before[-1] = needed[-1]
                g = np.empty(frames.shape[0], dtype=np.float32)
                for k in range(count):
                    want = before[k]
                    if want > status:      # back up, but slowly
                        want = min(want, status * RECOVERY + (1.0 - RECOVERY))
                    a0 = k * BLOCK
                    a1 = min(frames.shape[0], a0 + BLOCK)
                    g[a0:a1] = np.linspace(status, want, a1 - a0,
                                           endpoint=False)
                    status = want
                    smallest = min(smallest, want)
                f.write((np.repeat(g, channels) if channels > 1 else g)
                        .astype("<f4").tobytes())
    except Exception as e:
        print(T('  Level curve not possible (%s) -- without limiter') % e)
        return None, 0.0
    finally:
        try:
            source.stdout.close()
            source.wait(timeout=30)
        except Exception:
            pass
    gone = -20.0 * math.log10(max(1e-6, smallest))
    if gone <= 0.001:
        try:
            os.unlink(raw)
        except OSError:
            pass
        return None, 0.0
    try:
        subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le",
                        "-ar", str(SR), "-ac", str(channels), "-i", raw,
                        "-c:a", "pcm_f32le"]
                            + wav_safe(target)
                            + ["-y", target], check=True)
        os.unlink(raw)
    except Exception as e:
        print(T('  Level curve not possible (%s) -- without limiter') % e)
        return None, 0.0
    return target, gone


def channel_count(file_path):
    """Return the channel count of a file."""
    return probe_remember("channels", file_path,
                          lambda: _channel_count(file_path))


def kept_channels(file_path):
    """How many channels a track keeps on its way through: one or two.

    Folding a stereo track to one throws away the difference between two
    microphones for good, so the rule is "keep what the source has". More
    than two channels is a recorder file, and anything so wide is folded.
    """
    try:
        return 2 if channel_count(file_path) == 2 else 1
    except Exception:
        return 1


def channel_filter(have, want):
    """The filter that brings *have* channels to *want*, without a level jump.

    Written out rather than left to ffmpeg, whose equal-power law lands
    three decibels out either way and depends on the output format. One
    to two is a copy here, two to one a half-and-half sum.
    """
    if have == want:
        return "anull"
    if want == 2:
        return "pan=stereo|c0=c0|c1=c0"
    return "pan=mono|c0=0.5*c0+0.5*c1"


def widest_track(paths):
    """Two if any of these files is stereo, otherwise one."""
    return max([1] + [kept_channels(p) for p in paths])


def _channel_count(file_path):
    try:
        a = next((x for x in ffprobe_json(file_path).get("streams", [])
                  if x.get("codec_type") == "audio"), {})
        return int(a.get("channels") or 1)
    except Exception:
        return 1


def how_many_processors():
    """How many processors this process may actually use.

    os.cpu_count() counts what the machine has, not what this process is
    allowed: held to two of thirty-two, a pool of thirty-two means
    threads taking turns. process_cpu_count needs Python 3.13.
    """
    ask = getattr(os, "process_cpu_count", None) or os.cpu_count
    try:
        return max(1, int(ask() or 2))
    except Exception:
        return 2


def python_note():
    """One line about the Python this is running on, for the log."""
    now = "%d.%d.%d" % sys.version_info[:3]
    if now == LIKES_PYTHON:
        return "Python %s" % now
    return "Python %s  (recommended version %s)" % (now, LIKES_PYTHON)


def prework_standing(shares):
    """How far the prework has got, and one line per file still at it.

    Every task of a file counts the same, and every file the same
    however many tasks it has. What is finished leaves the list.
    """
    per_file = {}
    for (path, _task), value in shares.items():
        per_file.setdefault(path, []).append(value)
    got = dict((p, sum(v) / len(v)) for p, v in per_file.items())
    total = sum(got.values()) / len(got)
    lines = ["%s   %3.0f %%" % (os.path.basename(p), 100.0 * got[p])
             for p in sorted(got, key=os.path.basename) if got[p] < 0.999]
    return total, lines


def prework_weight(file_path, task):
    """How much of the bar a piece of prework is worth.

    Pulling audio out of an hour of 4K and reading a wav file are one
    step each; equal shares would make the bar stand still and jump.
    """
    video = os.path.splitext(file_path)[1].lower() in VIDEO_SUFFIXES
    if task == "audio":
        return 8.0 if video else 2.0
    if task == "channels":
        return 6.0 if video else 1.5
    if task == "split":
        return 4.0 if video else 2.0
    return 6.0 if video else 1.0


def parallel_map(items, work, workers=None):
    """Run *work* over all *items* at once; answers come back in order.

    Threads rather than processes: everything this is used for waits on
    ffmpeg or numpy, and both let other threads run. Where none can be
    started the rest is worked here; an error is raised at the end.
    """
    items = list(items)
    if len(items) < 2:
        return [work(x) for x in items]
    if workers is None:
        workers = max(2, min(8, how_many_processors()))
    out = [None] * len(items)
    todo = list(range(len(items)))
    trouble = []

    def work_loop():
        while True:
            if stop_wanted():
                return
            try:
                i = todo.pop()
            except IndexError:
                return
            try:
                out[i] = work(items[i])
            except BaseException as e:      # noqa: BLE001 -- passed on below
                trouble.append(e)

    threads = []
    for _ in range(max(1, min(workers, len(items)))):
        thread = threading.Thread(target=work_loop, daemon=True)
        try:
            thread.start()
        except Exception:
            break
        threads.append(thread)
    for thread in threads:
        try:
            thread.join()
        except Exception:
            pass
    work_loop()             # whatever no thread got to
    if trouble:
        raise trouble[0]
    return out


def probe_warm(paths, workers=None):
    """Ask about several files at once, so the answers are there later.

    Everything the interface needs to draw a row is measured here in
    parallel and the rows built from memory. On an external volume,
    asking one after another costs minutes of a standing window.
    """
    todo = [p for p in dict.fromkeys(paths) if p and os.path.exists(p)]
    if len(todo) < 2:
        return

    def one(file_path):
        work = [lambda: ffprobe_json(file_path),
                lambda: channel_count(file_path)]
        if os.path.splitext(file_path)[1].lower() in AUDIO_SUFFIXES:
            work += [lambda: sample_count(file_path),
                     lambda: bext_time_reference(file_path)]
        for task in work:
            try:
                task()
            except Exception:
                # A file that cannot be measured is reported at its row.
                pass

    parallel_map(todo, one, workers)


# A channel counts as silent when it stays this far under the loudest
# channel of the same file. A recorder writes four channels whether or
# not anything was plugged in, and an empty one is not a speaker.
SILENT_BELOW_DB = 45.0
# Absolute floor for a channel that carries anything at all. Under this
# a judgement is comparing the converter's dither rather than signal.
QUIET_BELOW_DBFS = -70.0

# Two channels count as the same signal from here up. Mono panned to
# both sides gives exactly 1.0; a hair less allows for lossy coding.
SAME_SIGNAL = 0.999

# How far off zero a shared sound may arrive and still count as one
# pair. Sound travels 34 cm in a millisecond, which covers every
# stereo spacing and no pair of clip-ons on two people.
PAIR_DELAY_MS = 1.0

# This much of the strongest common component has to sit inside that
# window. Stereo scores near 1, two clip-ons near 0.1, nothing between.
PAIR_AT_ZERO = 0.5

# Two more legs under the same judgement: in one room every microphone
# hears the same thing at the same moment, so the share alone cannot
# tell a pair from a neighbour. First leg: the spacing has to be small.
PAIR_APART_METRES = 0.3
# And only where it stands on something: a real spacing turns up at
# nearly every place, so one is not enough to throw stereo away.
PAIR_APART_SHARE = 0.25

# Second leg: a pair has to stand out from the two pairs that share a
# channel with it, or a pair across a boundary scores as high.
PAIR_STANDS_OUT = 0.15

# The delay is measured on this many places spread over the file. More
# does not change the figure and costs time while the list is waited on.
PAIR_PLACES = 120

# Below this many usable places the median means nothing, and the row
# says so with the number instead of claiming anything.
PAIR_ENOUGH_PLACES = 8

# Which level counts as "the loud part of this file". The gate below
# hangs on it, so it must be a level the recording really reaches and
# must survive one loud moment; a decile of the places does both.
PAIR_LOUD_PERCENTILE = 90.0

# And the gate sits this far under it. Not a threshold for silence --
# that is the correlation height -- but what holds the pauses out.
PAIR_GATE_UNDER_DB = 20.0


def channel_rate(file_path, channels, want=16000):
    """Pick a working rate that fits the file in memory.

    16 kHz gives the delay measurement a sixteenth of a millisecond; an
    hour of four channels at that rate is a gigabyte, so a long or wide
    file is read more coarsely, and halving the rate halves the detail.
    """
    try:
        seconds = float(ffprobe_json(file_path).get("format", {})
                        .get("duration") or 0.0)
    except Exception:
        seconds = 0.0
    while want > 4000 and seconds * max(1, channels) * want > 6e8:
        want //= 2
    return want


# Peak level has to be this close to the top before counting starts.
CLIP_NEAR_TOP_DB = -0.1
# How many samples in a row on the stop make one event. One is rounding,
# two is rounding twice; three in a row is a crest the converter could
# not follow. Holds for speech and music, not for rumble under 50 Hz.
CLIP_RUN_SAMPLES = 3


def clipping_facts(file_path, stream=0, least=CLIP_RUN_SAMPLES):
    """Count the runs of samples sitting on the stop, per channel.

    Counted here rather than asked of ffmpeg: ``astats`` reports samples
    equal to this file's own loudest value, so it cannot tell single
    samples from runs. Integer only. {channel: (runs, longest, ms, s)}.
    """
    if np is None or pcm_kind(file_path, stream) == "pcm_f32le":
        return {}
    try:
        # The stream that was asked about: rate and channel count off the
        # first would be counted against the nth stream's format.
        a = audio_stream_facts(file_path, stream)
        rate = int(a.get("sample_rate") or 0)
        n = int(a.get("channels") or 0)
    except Exception:
        return {}
    if not rate or not n:
        return {}
    return clipping_runs_count(file_path, stream, rate, n, least)


def clipping_runs_count(file_path, stream, rate, n, least):
    """Stream the audio at its own rate and count the runs.

    At the full rate, not the 16 kHz the levels use: a run of three
    samples does not survive resampling. Block by block, since an hour of
    stereo does not fit memory. Through s16le, or 16 and 24 bit differ.
    """
    top, bottom, width = 32767, -32768, 2
    try:
        p = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-i", file_path,
             "-map", "0:a:%d" % stream, "-c:a", "pcm_s16le",
             "-f", "s16le", "-"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except OSError:
        return {}
    frame = width * n
    want = max(frame, (8 << 20) // frame * frame)
    total = np.zeros(n, dtype=np.int64)
    runs = np.zeros(n, dtype=np.int64)
    longest = np.zeros(n, dtype=np.int64)
    first = np.full(n, -1, dtype=np.int64)
    open_len = np.zeros(n, dtype=np.int64)
    open_at = np.zeros(n, dtype=np.int64)

    def close(k, how_long, where):
        """A run that has ended: count it if it is long enough."""
        if how_long >= least:
            runs[k] += 1
            if first[k] < 0:
                first[k] = where
        if how_long > longest[k]:
            longest[k] = how_long

    rest, base = b"", 0
    try:
        while True:
            raw = p.stdout.read(want)
            if not raw:
                break
            raw = rest + raw
            keep = len(raw) - (len(raw) % frame)
            rest = raw[keep:]
            if not keep:
                continue
            block = np.frombuffer(raw[:keep], dtype=np.int16).reshape(-1, n)
            here = block.shape[0]
            # Two comparisons and not one on the absolute value: int16
            # has no room for the absolute of its own lowest number.
            hit = (block >= top) | (block <= bottom)
            columns = ([int(k) for k in np.flatnonzero(hit.any(axis=0))]
                       if hit.any() else [])
            if columns:
                total += hit.sum(axis=0)
            standing = set(columns)
            for k in np.flatnonzero(open_len):
                k = int(k)
                if k not in standing:
                    close(k, open_len[k], open_at[k])
                    open_len[k] = 0
            for k in columns:
                edge = np.ascontiguousarray(hit[:, k]).view(np.int8)
                step = np.diff(edge, prepend=np.int8(0), append=np.int8(0))
                on = np.flatnonzero(step == 1)
                off = np.flatnonzero(step == -1)
                length = (off - on).astype(np.int64)
                start = base + on.astype(np.int64)
                if open_len[k]:
                    if on[0] == 0:
                        length[0] += open_len[k]
                        start[0] = open_at[k]
                    else:
                        # It ended on the block boundary while this
                        # block has a hit further along.
                        close(k, open_len[k], open_at[k])
                    open_len[k] = 0
                if off[-1] == here:
                    open_len[k] = length[-1]
                    open_at[k] = start[-1]
                    length, start = length[:-1], start[:-1]
                if length.size:
                    longest[k] = max(longest[k], int(length.max()))
                    enough = np.flatnonzero(length >= least)
                    if enough.size:
                        runs[k] += enough.size
                        if first[k] < 0:
                            first[k] = start[enough[0]]
            base += here
    finally:
        # Closed rather than guarded: a reader that stopped early would
        # leave ffmpeg writing into a pipe nobody empties.
        p.stdout.close()
        try:
            p.wait(timeout=20)
        except Exception:
            p.kill()
            p.wait()
    if p.returncode:
        # Half a file read is worse than none: the answer would be given
        # on the part that arrived.
        return {}
    for k in range(n):
        if open_len[k]:
            close(k, open_len[k], open_at[k])
    return {k: (int(runs[k]), int(longest[k]),
                float(1000.0 * longest[k] / rate),
                float(first[k]) / float(rate))
            for k in range(n) if runs[k]}


def channel_levels(file_path, rate=16000, stream=0):
    """Return each audio channel of one file on its own.

    One pass through ffmpeg, taken apart here: asking per channel with a
    pan filter decodes the whole file again each time. Empty rows where
    ffmpeg failed, since half a file would be judged as if it were whole.
    """
    n = max(1, channel_count(file_path))
    p = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", file_path,
         "-map", "0:a:%d" % stream, "-ar", str(rate), "-f", "f32le", "-"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    parts = [[] for _ in range(n)]
    rest = b""
    frame = 4 * n
    try:
        while True:
            # A block of whole frames at a time: the lot at once would
            # double the memory of a long wide file.
            raw = p.stdout.read(frame * 65536)
            if not raw:
                break
            raw = rest + raw
            keep = len(raw) - (len(raw) % frame)
            rest = raw[keep:]
            if not keep:
                continue
            block = np.frombuffer(raw[:keep], dtype=np.float32).reshape(-1, n)
            for k in range(n):
                parts[k].append(np.ascontiguousarray(block[:, k]))
    finally:
        try:
            p.stdout.close()
        except OSError:
            pass
        # A reader that stopped early leaves ffmpeg writing for ever
        # into a pipe nobody empties.
        try:
            p.wait(timeout=20)
        except Exception:
            p.kill()
            p.wait()
    if p.returncode:
        # Half a file read is worse than none: the judgement would be
        # stored under the file's size and time and never made again.
        return [np.zeros(0, dtype=np.float32) for _ in range(n)]
    # Joined one channel at a time, each list of pieces dropped as soon
    # as it is joined: all at once would hold the recording twice.
    out = []
    for k in range(n):
        out.append(np.concatenate(parts[k]) if parts[k]
                   else np.zeros(0, dtype=np.float32))
        parts[k] = None
    return out


def channel_at_zero(first, second, rate, most=PAIR_PLACES, window=2048):
    """How much of what two channels share arrives at the same time.

    One pair of microphones hears everything at nearly the same moment,
    two on two people hear each other late: the question is not how alike
    the channels are but *when*. Returns (share, places, apart, agreed).
    Plain correlation, not PHAT, which spikes on shared silence.
    """
    # Both legs come off the same places, but the share is the median
    # over all of them and the distance only over those that missed.
    width = min(len(first), len(second))
    if width < window * 2:
        return 0.0, 0, 0.0, 0
    reach = max(4, int(0.020 * rate))
    close = max(1, int(PAIR_DELAY_MS * rate / 1000.0))
    spots = np.linspace(0, width - window - 1, most).astype(int)
    # How loud each place is, all of them before any is judged: the gate
    # is a level of this file, and a peak is not a level.
    strong = np.zeros(len(spots))
    for j, i in enumerate(spots):
        a = first[i:i + window].astype(np.float64)
        b = second[i:i + window].astype(np.float64)
        strong[j] = max(math.sqrt(float((a ** 2).mean())),
                        math.sqrt(float((b ** 2).mean())))
    loud = float(np.percentile(strong, PAIR_LOUD_PERCENTILE))
    if loud <= 0:
        return 0.0, 0, 0.0, 0
    gate = loud * 10 ** (-PAIR_GATE_UNDER_DB / 20.0)
    n = 1 << int(math.ceil(math.log(window * 2, 2)))
    # Below this the two channels share nothing worth reading a delay
    # out of, and the correlation peaks wherever the noise is tallest.
    shared_enough = 0.10
    out, away = [], []
    for j, i in enumerate(spots):
        if strong[j] < gate:
            continue
        a = first[i:i + window]
        b = second[i:i + window]
        a = a.astype(np.float64) - float(a.mean())
        b = b.astype(np.float64) - float(b.mean())
        size = math.sqrt(float((a ** 2).sum()) * float((b ** 2).sum()))
        if size <= 0:
            continue
        cc = np.fft.irfft(np.fft.rfft(a, n) * np.conj(np.fft.rfft(b, n)), n)
        band = np.abs(np.concatenate((cc[-reach:], cc[:reach + 1]))) / size
        highest = float(band.max())
        if highest < shared_enough:
            continue
        out.append(float(band[reach - close:reach + close + 1].max())
                   / highest)
        where = int(np.argmax(band)) - reach
        if abs(where) > close:
            away.append(abs(where) * 1000.0 / float(rate))
    if len(out) < PAIR_ENOUGH_PLACES:
        return 0.0, len(out), 0.0, 0
    apart, agreed = pair_spacing(away, len(out))
    return float(np.median(out)), len(out), apart, agreed


def pair_spacing(away, places=0):
    """The one delay the late arrivals agree on, and how many agree.

    *away* is how late the strongest shared sound was where it missed the
    zero window. A spacing is a fixed length of air and turns up as the
    same delay again and again, so the median counts only if most agree.
    """
    if not away or len(away) < PAIR_APART_SHARE * max(0, places):
        return 0.0, 0
    middle = float(np.median(away))
    near = [x for x in away if abs(x - middle) <= PAIR_DELAY_MS / 2.0]
    if len(near) * 2 > len(away):
        return middle, len(near)
    return 0.0, 0


def channel_hush(level):
    """Which channels carry nothing, and by how much they missed.

    Two rules, and a channel need fail only one: far under the loudest is
    an input nobody plugged into, under the absolute floor only converter
    noise. Returns ([silent], [reason]) with the rule and the amount.
    """
    if not level:
        return [], []
    highest = max(level)
    floor = QUIET_BELOW_DBFS if highest > QUIET_BELOW_DBFS else float("-inf")
    silent, why = [], []
    for x in level:
        gap = (highest - x) if x > float("-inf") else float("inf")
        if not (x > float("-inf")):
            silent.append(True), why.append(("quiet", float("-inf")))
        elif gap > SILENT_BELOW_DB:
            silent.append(True), why.append(("under", gap))
        elif x < floor:
            silent.append(True), why.append(("quiet", x))
        else:
            silent.append(False), why.append(None)
    return silent, why


def channel_recipe_mark():
    """The mark for the channel measurement, so a change throws it away."""
    return recipe_mark("channels", channel_facts, channel_levels,
                       channel_hush, channel_rate)


def channel_facts_name():
    """The one name the channel measurement is stored under.

    Built in one place because three ask for it: the one that stores and
    the two that ask whether it is there. Spelled out twice, the recipe
    mark reaches one and not the other, and nothing is ever measured.
    """
    return "channelfacts-" + channel_recipe_mark()


def channel_facts(file_path, rate=None, stream=0):
    """Measure the channels of one file: how loud, how empty, how alike.

    Every neighbouring pair, not every second one: on a mixer, channels 2
    and 3 can be the pair as well as 1 and 2. So entry k of *pair_same*
    and *pair_zero* is about k and k+1, one shorter than the channels.
    """
    if rate is None:
        rate = channel_rate(file_path, channel_count(file_path))
    try:
        rows = channel_levels(file_path, rate, stream)
    except Exception:
        rows = []
    n = len(rows)
    width = min((len(x) for x in rows), default=0)
    if not n or width < rate // 4:
        return {"channels": n, "level": [], "silent": [], "pair_same": [],
                "pair_zero": [], "pair_apart": [], "pair_places": [],
                "pair_agreed": [], "readable": False}
    rows = [x[:width] for x in rows]
    level = []
    for x in rows:
        top = float(np.percentile(np.abs(x), 99))
        level.append(20.0 * math.log10(top) if top > 0 else float("-inf"))
    highest = max(level)
    silent, why = channel_hush(level)
    pair_same, pair_zero, pair_apart = [], [], []
    pair_places, pair_agreed = [], []
    for a in range(0, n - 1):
        b = a + 1
        if silent[a] or silent[b]:
            pair_same.append(None)
            pair_zero.append(None)
            pair_apart.append(None)
            pair_places.append(None)
            pair_agreed.append(None)
            continue
        with np.errstate(invalid="ignore"):
            r = np.corrcoef(rows[a], rows[b])[0, 1]
        pair_same.append(float(r) if np.isfinite(r) else None)
        share, places, apart, agreed = channel_at_zero(
            rows[a], rows[b], rate)
        enough = places >= PAIR_ENOUGH_PLACES
        pair_zero.append(share if enough else None)
        pair_apart.append(apart if enough else None)
        pair_places.append(places)
        pair_agreed.append(agreed)
    return {"channels": n, "level": level, "silent": silent,
            "pair_same": pair_same, "pair_zero": pair_zero,
            "pair_apart": pair_apart, "pair_places": pair_places,
            "pair_agreed": pair_agreed, "readable": True}


def hush_reason(which, why):
    """Say why a channel counts as carrying nothing, with the number.

    The two rules are different recording faults: nothing plugged in,
    against only converter noise left. One wording for both would be
    wrong -- a channel far under the loudest can still be well above it.
    """
    reason = why[which - 1] if 0 < which <= len(why) else None
    if reason and reason[0] == "under" and reason[1] < float("inf"):
        return T('Channel %d is %s dB under the loudest -- nothing '
                 'plugged in') % (which, number_text(reason[1], 0))
    if reason and reason[1] > float("-inf"):
        return T('Channel %d at %s dBFS -- only converter noise '
                 'left') % (which, number_text(reason[1], 0))
    return T('Channel %d is silent -- unused input') % which


def kind_makes_stereo(kind, channels):
    """Is a two-channel file stereo because of what it is?

    An intro or outro is a finished stereo mix, and the measurement is at
    its weakest there: music has no speech pauses and an effect can
    produce any correlation. Two channels only.
    """
    return (kind in (TYPE_INTRO, TYPE_OUTRO)
            and int(channels or 0) == 2)


def apart_places(agreed, places):
    """How many places the spacing rests on, as a piece of the line.

    Without it a distance out of one place of a hundred reads exactly
    like one out of all of them.
    """
    if not agreed or not places:
        return ""
    return T(', agreed at %s of %s places') % (number_text(agreed, 0),
                                              number_text(places, 0))


def channel_joins(facts, kind=None):
    """Judge every pair of neighbours: could these two be one stereo track?

    Returns [(k, stereo, certain, reason)], k the left channel. Every
    neighbour is asked, since fixed pairs get a confident wrong answer,
    and what decides is *when* the two hear the same thing.
    """
    # Not seen by this: two recordings laid on a common time axis before
    # being put into one file, which removes the delay measured here.
    n = int(facts.get("channels") or 0)
    if not facts.get("readable") or n <= 1:
        return []
    if kind_makes_stereo(kind, n):
        return [(0, True, True,
                 T('an intro or outro with two channels is a stereo '
                   'mix -- not measured'))]
    silent = list(facts.get("silent") or [False] * n)
    _, why = channel_hush(list(facts.get("level") or []))
    same = list(facts.get("pair_same") or [])
    zero = list(facts.get("pair_zero") or [])
    apart = list(facts.get("pair_apart") or [])
    counted = list(facts.get("pair_places") or [])
    from_agreed = list(facts.get("pair_agreed") or [])
    out = []
    for k in range(n - 1):
        r = same[k] if k < len(same) else None
        at_zero = zero[k] if k < len(zero) else None
        late = apart[k] if k < len(apart) else None
        places = counted[k] if k < len(counted) else None
        # How many places the spacing was read from, against how many
        # were usable: a distance is worth naming only if it repeats.
        stood_on = apart_places(
            from_agreed[k] if k < len(from_agreed) else None, places)
        # A row in the file list carries the answer, not the arithmetic.
        if silent[k] or silent[k + 1]:
            which = (k + 2) if silent[k + 1] else (k + 1)
            out.append((k, False, True, hush_reason(which, why)))
        elif r is not None and r >= SAME_SIGNAL:
            out.append((k, True, True,
                        T('both channels identical -- mono laid on both '
                          'sides')))
        elif at_zero is not None and at_zero < PAIR_AT_ZERO:
            # 343 m/s: in metres the answer can be checked against the
            # room the recording was made in.
            out.append((k, False, True,
                        T('probably two microphones -- about %s m '
                          'apart%s')
                        % (number_text((late or 0.0) * 0.343, 1),
                           stood_on)))
        elif at_zero is not None and at_zero >= PAIR_AT_ZERO:
            # The share is high enough, but it answers "yes" for every
            # microphone in one room, so two more questions follow.
            metres = (late or 0.0) * 0.343
            beside = [zero[j] for j in (k - 1, k + 1)
                      if 0 <= j < len(zero) and zero[j] is not None]
            if metres > PAIR_APART_METRES:
                # Measured apart, so not one place however well the two
                # agree -- the same finding, reached the long way round.
                out.append((k, False, True,
                            T('probably two microphones -- about %s m '
                              'apart%s')
                            % (number_text(metres, 1), stood_on)))
            elif beside and at_zero - max(beside) < PAIR_STANDS_OUT:
                out.append((k, False, False,
                            T('not recognisable -- these two agree no '
                              'better than each does with the channel '
                              'beside it')))
            else:
                out.append((k, True, True,
                            T('probably one stereo track -- both '
                              'microphones in the same place')))
        else:
            # Nothing was measured here, so nothing is said about what
            # the two share -- the number tells a quiet recording apart.
            out.append((k, False, False,
                        T('not recognisable -- only %s of %s places '
                          'where both channels carry sound, %s needed')
                        % (number_text(places or 0, 0),
                           number_text(PAIR_PLACES, 0),
                           number_text(PAIR_ENOUGH_PLACES, 0))))
    return out


def joined_channels(facts, choice=None, kind=None):
    """Which neighbours are actually joined, after the ticks.

    A channel belongs to at most one pair, so the answer must not
    overlap: from the left, taking the first join that fits, which is
    what the interface shows too. Returns {left channel: True}.
    """
    judged = {k: stereo
              for k, stereo, _sure, _why in channel_joins(facts, kind)}
    picked = dict(choice or {})
    n = int(facts.get("channels") or 0)
    silent = list(facts.get("silent") or [])

    def possible(k):
        """An unused input cannot be one side of a stereo track.

        The interface offers no tick where one of the two is silent, but
        a tick made earlier outlives the measurement it was made under.
        """
        return not ((k < len(silent) and silent[k])
                    or (k + 1 < len(silent) and silent[k + 1]))

    # First what the measurement proposes: from the left, each pair it
    # found, skipping what is already spoken for.
    out, taken = {}, set()
    for k in range(max(0, n - 1)):
        if k in taken or (k + 1) in taken or not possible(k):
            continue
        if judged.get(k, False):
            out[k] = True
            taken.update((k, k + 1))
    # Then the hand, correcting that proposal: a tick away is one pair
    # fewer, a tick set one more, and its two neighbours lose theirs.
    for k in sorted(picked):
        if not (0 <= k < n - 1):
            continue
        if not picked[k]:
            out.pop(k, None)
            continue
        if not possible(k):
            continue
        out.pop(k - 1, None)
        out.pop(k + 1, None)
        out[k] = True
    return out


def channel_name(name, channels):
    """What a track cut out of a file is called: "Mixer Channel 1+2".

    "Channel" stays English in every language -- it is the word on the
    recorder and in every manual. A plus joins a pair, not an ampersand,
    which splits a command in every shell.
    """
    return "%s Channel %s" % (name, "+".join(str(c + 1) for c in channels))


def _level_of(facts, k):
    """Return the level of one channel, a low number where there is none."""
    row = facts.get("level") or []
    if k >= len(row) or row[k] == float("-inf"):
        return -120.0
    return float(row[k])


def wav_safe(target):
    """["-rf64", "auto"] where the target is a WAV, [] where it is not.

    A plain WAV keeps its sizes in 32 bit and stops at 4 GiB; past that
    the header names less than is there and the tail is gone silently.
    RF64 is the same with 64 bit sizes; ffmpeg refuses it on other kinds.
    """
    return (["-rf64", "auto"]
            if os.path.splitext(target)[1].lower() == ".wav" else [])


def audio_stream_facts(file_path, stream=0):
    """What ffprobe says about one audio stream, counted among its own.

    *stream* is the nth audio stream, 0:a:N to ffmpeg, not the position
    in the whole stream list. Nothing there means an empty answer.
    """
    try:
        only_audio = [x for x in ffprobe_json(file_path).get("streams", [])
                      if x.get("codec_type") == "audio"]
    except Exception:
        return {}
    if not only_audio:
        return {}
    return only_audio[stream] if 0 <= stream < len(only_audio) else {}


def pcm_kind(file_path, stream=0):
    """Return the wav sample format to write a copy of this audio in.

    As deep as the original, no deeper: a 16 bit recorder file written as
    24 bit costs half again in size and adds nothing. Asked about the
    stream it was given, not the first one in the file.
    """
    a = audio_stream_facts(file_path, stream)
    if str(a.get("sample_fmt") or "").startswith(("flt", "dbl")):
        return "pcm_f32le"
    # bits_per_raw_sample is missing for 16 bit files, so
    # bits_per_sample answers as well. Both absent means unknown, and 24
    # bit is the safe guess: too shallow throws away what was recorded.
    deep = 0
    for key in ("bits_per_raw_sample", "bits_per_sample"):
        try:
            deep = int(a.get(key) or 0)
        except (TypeError, ValueError):
            deep = 0
        if deep:
            break
    return "pcm_s16le" if 0 < deep <= 16 else "pcm_s24le"


def split_target(file_path, channels, folder):
    """Where the track made of these channels is written.

    Two things must be unique: the channels, or channel 12 lands on the
    file of 1 and 2; and the source, since two cards with the same file
    name share a folder. The trailing digit is a mark, not a counter.
    """
    stem = os.path.splitext(os.path.basename(file_path))[0]
    tag = "+".join(str(c + 1) for c in channels)
    mark = hashlib.sha1(os.path.abspath(file_path).encode(
        "utf-8", "replace")).hexdigest()[:8]
    return os.path.join(folder, "%s_%s_Channel%s.wav"
                        % (safe_filename(stem)[:60], mark, tag))


def split_channels(file_path, channels, target, stream=0, rate=None):
    """Write one track of a multichannel file into a file of its own.

    Everything else stays as recorded; *rate* forces a sample rate,
    needed for camera audio at 44.1 kHz while the run is at 48. The
    recording time goes with the piece, or a real pause is swallowed.
    """
    channels = tuple(channels)
    if len(channels) == 1:
        pan = "pan=mono|c0=c%d" % channels[0]
    else:
        pan = "pan=stereo|c0=c%d|c1=c%d" % (channels[0], channels[1])
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    stamp = []
    start = bext_time_reference(file_path)
    if start is not None:
        # Counted in samples, so a changed rate changes the number.
        try:
            was = int(ffprobe_json(file_path)["streams"][stream_index_of(
                file_path, stream)]["sample_rate"])
        except Exception:
            was = SR
        now = int(rate or was)
        stamp = ["-write_bext", "1", "-metadata", "time_reference=%d"
                 % int(round(start * now / float(was or now)))]
    shell_quote(["ffmpeg", "-v", "error", "-i", file_path,
                 "-filter_complex", "[0:a:%d]%s[o]" % (stream, pan),
                 "-map", "[o]"]
                + (["-ar", str(rate)] if rate else [])
                + stamp
                + ["-c:a", pcm_kind(file_path, stream)]
                    + wav_safe(target) + ["-y", target])
    return target


def stream_index_of(file_path, audio_number=0):
    """Return the index in the stream list of this audio stream."""
    every = ffprobe_json(file_path).get("streams", []) or []
    seen = -1
    for i, x in enumerate(every):
        if x.get("codec_type") == "audio":
            seen += 1
            if seen == audio_number:
                return i
    return 0


def tracks_to_split(file_path, facts, choice=None, name=None):
    """Return the tracks a file has to be cut into, as [(channels, label)].

    Empty where nothing has to happen. Silent channels are not in the
    answer -- an unused recorder input must not become a speaker. *name*
    is what the tracks are called; without it the file name does.
    """
    rows = channel_tracks(facts, name or os.path.splitext(
        os.path.basename(file_path))[0], choice)
    if len(rows) <= 1 and not any(silent for _c, _l, silent in rows):
        return []
    return [(chs, label) for chs, label, silent in rows
            if not silent and chs]


def expand_chains_to_tracks(chains, split_of):
    """Turn recordings into tracks where one file holds several.

    Four channels give four tracks and three blocks three per track, so
    the blocks are cut first and the pieces regrouped -- but grouped on
    the original files, or channel two would read as the next block.
    """
    out = []
    for row, discarded in chains:
        pieces = [list(split_of(x) or []) for x in row]
        how_many = max((len(x) for x in pieces), default=0)

        def which(row_of_pieces):
            """The channels each piece is made of, in order.

            Counting them is not enough: [1][2][3+4] and [1+2][3][4]
            both give three, and zipping them mixes two signals.
            """
            out = []
            for x in row_of_pieces:
                stem = os.path.splitext(os.path.basename(x))[0]
                mark = SPLIT_MARK.search(stem)
                out.append(mark.group(0) if mark else stem)
            return out

        # A recording whose blocks did not all come apart the same way
        # stays whole: two signals on one row is worse than no split.
        if not how_many or any(len(x) != how_many for x in pieces) \
                or any(which(x) != which(pieces[0]) for x in pieces):
            out.append((row, discarded))
            continue
        for k in range(how_many):
            out.append(([x[k] for x in pieces],
                        discarded if k == 0 else []))
    return out


def audio_shape(file_path):
    """Return (channels, sample rate) -- what has to match to join."""
    try:
        a = next((x for x in ffprobe_json(file_path).get("streams", [])
                  if x.get("codec_type") == "audio"), {})
        return (int(a.get("channels") or 0), int(a.get("sample_rate") or 0))
    except Exception:
        return (0, 0)


def shapes_match(first, second):
    """Report whether two files can be laid end to end at all.

    Channel count and sample rate have to match, or a channel third in
    one block and fourth in the next mixes the tracks up. Depth may vary.
    """
    a, b = audio_shape(first), audio_shape(second)
    if not a[0] or not b[0]:
        return True, ""
    if a == b:
        return True, ""
    if a[0] != b[0]:
        return False, (T('%s channels against %s')
                       % (number_text(a[0], 0), number_text(b[0], 0)))
    return False, (T('%s kHz against %s kHz')
                   % (number_text(a[1] / 1000.0, None),
                      number_text(b[1] / 1000.0, None)))


def blocks_facts(paths):
    """Judge the channels over a whole recording, not over one block.

    The channels are the same throughout, but the first block alone can
    be badly wrong -- a soundcheck reads as one pair where the show reads
    as ten. Each block is measured, the pair judged where it is loudest.
    """
    rows = [x for x in (paths or []) if x]
    if not rows:
        return {"channels": 0, "level": [], "silent": [], "pair_same": [],
                "pair_zero": [], "pair_apart": [], "pair_places": [],
                "pair_agreed": [], "readable": False}
    if len(rows) == 1:
        return channel_facts_cached(rows[0])
    return blocks_facts_from([channel_facts_cached(x) for x in rows])


def blocks_facts_from(every):
    """Combine what was measured per block into one answer.

    Apart from blocks_facts so it can be held against made-up numbers.
    """
    every = [f for f in (every or []) if isinstance(f, dict)]
    if not every:
        return {"channels": 0, "level": [], "silent": [], "pair_same": [],
                "pair_zero": [], "pair_apart": [], "pair_places": [],
                "pair_agreed": [], "readable": False}
    usable = [f for f in every if f.get("readable")]
    if not usable:
        return every[0]
    n = max(int(f.get("channels") or 0) for f in usable)
    usable = [f for f in usable if int(f.get("channels") or 0) == n]
    level = []
    for k in range(n):
        seen = [f["level"][k] for f in usable if k < len(f.get("level") or [])]
        level.append(max(seen) if seen else float("-inf"))
    silent, why = channel_hush(level)
    same, zero, apart, counted = [], [], [], []
    agreed = []
    for i, a in enumerate(range(0, n - 1)):
        b = a + 1
        if silent[a] or silent[b]:
            same.append(None), zero.append(None), apart.append(None)
            counted.append(None)
            continue
        # The block where this pair is loudest: judged where it is
        # silent, the measurement is of the converter's noise.
        best, loudest = None, float("-inf")
        for f in usable:
            measured = f.get("pair_zero") or []
            if i >= len(measured) or measured[i] is None:
                # This block did not measure the pair -- one of the two
                # was silent in it, so it has no answer to take.
                continue
            here = min(_level_of(f, a), _level_of(f, b))
            if here > loudest:
                best, loudest = f, here
        def of(name):
            """Entry i of one of the block's lists, or nothing.

            Guarded one by one: in hand-made facts the three lists can
            be of different lengths.
            """
            row = (best or {}).get(name) or []
            return row[i] if i < len(row) else None

        same.append(of("pair_same"))
        zero.append(of("pair_zero"))
        apart.append(of("pair_apart"))
        agreed.append(of("pair_agreed"))
        # The place count comes from the block the answer comes from;
        # with no such block, the best any reached -- not zero.
        if best is not None:
            counted.append(of("pair_places"))
        else:
            reached = [(f.get("pair_places") or [])[i] for f in usable
                       if i < len(f.get("pair_places") or [])]
            reached = [x for x in reached if x is not None]
            counted.append(max(reached) if reached else None)
    return {"channels": n, "level": level, "silent": silent,
            "pair_same": same, "pair_zero": zero, "pair_apart": apart,
            "pair_places": counted, "pair_agreed": agreed,
            "readable": True}


def channel_facts_cached(file_path):
    """Measure a file's channels once, not once per redraw.

    Keyed on size and modification time, so a changed file is measured
    again. The file list is rebuilt on every change.
    """
    # Kept on disc, unlike most: reading every channel of an hour of
    # audio takes 20 to 50 seconds, and every start would do it again.
    return probe_remember(channel_facts_name(), file_path,
                          lambda: channel_facts(file_path),
                          keep=True, as_json=True)


def channel_tracks(facts, name="Track", choice=None):
    """Return the tracks one file contributes, after the pair judgement.

    *choice* overrides the proposal per pair, {left channel: joined}, as
    the tick in the file list writes it. Returns [(channels, label,
    silent)], *channels* two indices for a pair and one otherwise.
    """
    n = int(facts.get("channels") or 0)
    if not facts.get("readable") or n <= 1:
        silent = (facts.get("silent") or [False])
        return [((), name, bool(silent and silent[0]))]
    silent = list(facts.get("silent") or [False] * n)
    joined = joined_channels(facts, choice)
    out, k = [], 0
    while k < n:
        if joined.get(k):
            out.append(((k, k + 1), channel_name(name, (k, k + 1)),
                        silent[k] and silent[k + 1]))
            k += 2
            continue
        out.append(((k,), channel_name(name, (k,)), silent[k]))
        k += 1
    # One track left over means the numbering says nothing, and the
    # file name alone is the better label.
    awake = [t for t in out if not t[2]]
    if len(awake) == 1:
        out = [(t[0], name if t is awake[0] else t[1], t[2]) for t in out]
    return out


def channel_rows_build(node, path, Qt, QtCore, QtWidgets, blocks_of,
                       channel_choice, channel_node, channels_arrived,
                       clip_kind_values, items, remembered, split_files):
    """Build the channel rows under one recording.

    Here and not in the window because it holds no state: what it needs
    comes in as arguments, in the order the window has them.
    """
    api_key = os.path.abspath(path)
    channel_node[api_key] = (node, path)
    row = blocks_of.get(api_key) or [api_key]
    # Where the list stands, kept over the rebuild: ticking a channel
    # replaces every row below the file, and the list would jump to top.
    bar_was = items.verticalScrollBar().value()
    QtCore.QTimer.singleShot(
        0, lambda: items.verticalScrollBar().setValue(bar_was))
    for k in range(node.childCount() - 1, -1, -1):
        kid = node.child(k)
        if kid.data(0, Qt.UserRole + 2) == "channel":
            node.removeChild(kid)
    try:
        how_many = channel_count(path)
    except Exception:
        how_many = 1
    if how_many <= 1:
        return

    spot = [0]

    def channel_row(text, value):
        kid = QtWidgets.QTreeWidgetItem([text, "", value])
        kid.setData(0, Qt.UserRole + 2, "channel")
        node.insertChild(spot[0], kid)
        spot[0] += 1
        return kid

    if not all(probe_has(channel_facts_name(), x) for x in row):
        channel_row(T('      %s channels') % number_text(how_many, 0),
                    T('measurement running ...'))
        return
    # Over the whole recording: the first block can be the soundcheck,
    # and then it says nothing about what the channels carry.
    facts = blocks_facts(row)
    silent = list(facts.get("silent") or [])
    picked = channel_choice.get(api_key) or {}
    # What the file is decides before the measurement does, and only for
    # a two channel intro or outro -- see kind_makes_stereo.
    of_kind = clip_kind_values.get(api_key)
    kind = (of_kind.get() if of_kind is not None
            else remembered.get("kind:" + api_key))
    joined = joined_channels(facts, picked, kind)
    judged = {k: (stereo, sure, why)
              for k, stereo, sure, why in channel_joins(facts, kind)}
    # One row per channel; the tick says "this one and the next make one
    # stereo track". On a mixer, channels 2 and 3 can be the pair.
    second = {k + 1 for k in joined}
    for k in range(how_many):
        kid = channel_row(T('      Channel %d') % (k + 1), "")
        if k in second:
            kid.setText(2, T('with Channel %d one stereo track') % k)
            continue
        if silent[k:k + 1] == [True]:
            kid.setText(2, T('unused input -- ignored'))
            continue
        if k >= how_many - 1 or silent[k + 1:k + 2] == [True]:
            kid.setText(2, T('a track of its own'))
            continue
        stereo, sure, why = judged.get(k, (False, False, ""))
        measured_stereo = stereo         # before any hand overrides it
        if picked.get(k) is not None:
            stereo = bool(picked[k])
            why = T('set by hand -- overrides the measurement')
            sure = True
        # The tick and its reason side by side in the wide column: in the
        # narrow one the word beside the box is cut off after one letter.
        beside = QtWidgets.QWidget()
        in_a_row = QtWidgets.QHBoxLayout(beside)
        in_a_row.setContentsMargins(0, 0, 0, 0)
        in_a_row.setSpacing(8)
        # An offer, not a statement: a channel already spoken for says
        # "with Channel N one stereo track" instead.
        box = QtWidgets.QCheckBox(
            T('join with Channel %d') % (k + 2))
        box.setChecked(bool(joined.get(k)))
        said = PROGRAM.label(why if sure else T('uncertain -- %s') % why,
                             COLOURS["quiet"])
        # German writes the finding half as long again as English, so it
        # wraps: what would run past the edge is the finding itself.
        said.setWordWrap(True)
        in_a_row.addWidget(box)
        in_a_row.addWidget(said, 1)
        PROGRAM.hint(box, T('On makes one stereo track out of this channel '
                            'and the next.\nThe next one then has no tick of '
                            'its own -- it is spoken for.\nWhat was measured '
                            'is in the line beside it.'))

        def chosen(on, file_path=api_key, number=k,
                   measured=measured_stereo):
            # Only a real override is remembered: ticking a pair the
            # measurement already found puts the row back to measured.
            by_hand = channel_choice.setdefault(file_path, {})
            if bool(on) == bool(measured):
                by_hand.pop(number, None)
            else:
                by_hand[number] = bool(on)
            # The cut tracks follow the old answer, so every block goes:
            # block one's channel 1 beside block two's 1+2 otherwise.
            for block in blocks_of.get(file_path) or [file_path]:
                split_files.pop(block, None)
            QtCore.QTimer.singleShot(
                0, lambda: channels_arrived(file_path))

        box.toggled.connect(chosen)
        items.setItemWidget(kid, 2, beside)
    # A moment later: the column still answers with its old width while
    # it is saying that the width has changed.
    def when_settled(*_a):
        QtCore.QTimer.singleShot(
            0, lambda: PROGRAM.channel_rows_fit(items, Qt, QtCore, QtWidgets))

    head = items.header()
    if not head.property("channel_rows_fit"):
        head.setProperty("channel_rows_fit", True)
        head.sectionResized.connect(when_settled)
    when_settled()


def mix_width(tracks):
    """How many channels a mix of these tracks is delivered in.

    Two where there are several, that being the form a mix is delivered
    in. One recording is the exception -- nothing to mix, so nothing is
    widened. A stereo source raises the count on its own either way.
    """
    if len(tracks) > 1:
        return 2
    return max(1, widest_track([track.get("ready") or track.get("axis")
                                for track in tracks])) if tracks else 1


def mix_tracks(sources, target, gain=0.0, curve=None, channels=1):
    """Sum several equally long tracks into one.

    Gain and limiter curve are the same for all tracks, so the single
    tracks add up to exactly the mix again. The widening happens before
    the sum and by "c1=c0" -- a plain conversion loses three decibels.
    """
    have = [kept_channels(p) for p in sources]
    channels = max(channels, max(have) if have else 1)
    if (len(sources) == 1 and abs(gain) < 0.01 and not curve
            and have[0] == channels):
        return sources[0]
    parts, chains, markers = [], [], []
    for i, path in enumerate(sources):
        parts += ["-i", path]
        chains.append("[%d:a]%s[m%d]"
                      % (i, channel_filter(have[i], channels), i))
        markers.append("[m%d]" % i)
    fc = ";".join(chains) + ";" + "".join(markers) +\
        "amix=inputs=%d:normalize=0" % len(markers)
    if abs(gain) >= 0.01:
        fc += ",volume=%.3fdB" % gain
    if curve:
        # The same gain curve as on all other tracks, hence a second
        # input: ffmpeg's equal-power law would cost another 3 dB.
        fc += "[both]"
        parts += ["-i", curve]
        fc += ";[both]aformat=sample_fmts=fltp:sample_rates=%d[gm];" % SR
        fc += "[%d:a]%s,aformat=sample_fmts=fltp:sample_rates=%d[gc];" % (
            len(sources), channel_filter(kept_channels(curve), channels), SR)
        fc += "[gm][gc]amultiply[out]"
    else:
        fc += "[out]"
    # The clock of the first source goes with the mix: without it the
    # levelled file has no timecode, and a recording with no clock
    # cannot be placed against anything afterwards.
    clock = []
    start = bext_time_reference(sources[0])
    if start is not None:
        clock = ["-write_bext", "1", "-metadata",
                 "time_reference=%d" % int(round(start))]
    PROGRAM.run_ffmpeg_with_progress(
        ["ffmpeg", "-v", "error"] + parts + ["-filter_complex", fc,
         "-map", "[out]", "-c:a", "pcm_s24le"] + clock
        + wav_safe(target) + ["-y", target],
        sample_count(sources[0]) / float(SR),
        T('Mixing %s') % (os.path.splitext(os.path.basename(target))[0]
                       .replace("mix_", "").replace("single_", "")
                       .replace("full", "Full-Mix")))
    return target


def rate_filter_chain(b):
    """Build a filter chain that compresses a track by factor b.

    The obvious chain rounds to whole sample rates, at 48 kHz steps of
    20.8 ppm -- enough for the coarse correction, not the fine one. So
    the rate is a hundred times higher, which needs soxr to hold.
    """
    if soxr_available():
        return ("asetrate=%d,aresample=resampler=soxr:osr=%d,asetrate=%d"
                % (SR * 100, int(round(SR * 100 / b)), SR))
    if abs(b - 1.0) > 1e-7 and not getattr(rate_filter_chain, "warned", False):
        rate_filter_chain.warned = True
        print(T('  Note: this ffmpeg has no soxr -- clock drift can only '
                'be taken out in\n  steps of 21 ppm.'))
    return "asetrate=%d,aresample=%d,asetrate=%d" % (SR, int(round(SR / b)),
                                                     SR)


def place_track_on_axis(source, target, a, b, t0, t1, drift=True):
    """Place an audio track on the reference axis and clip it to [t0, t1].

    Audio time = a + b * reference time: the drift is removed first, then
    the offset divided by b, and the track padded to its full length.
    Every track gets the same window, or the crosstalk cannot be removed.
    """
    n_window = int(round((t1 - t0) * SR))
    keep = kept_channels(source)
    af = []
    if drift and abs(b - 1.0) > 1e-7:
        af.append(rate_filter_chain(b))
        start = a / b + t0
    else:
        start = a + t0
    k = int(round(start * SR))
    if k > 0:
        af.append("atrim=start_sample=%d" % k)
        af.append("asetpts=N/SR/TB")
    elif k < 0:
        af.append("adelay=delays=%dS:all=1" % (-k))
    af.append("apad=whole_len=%d" % n_window)
    af.append("atrim=end_sample=%d" % n_window)
    af.append("asetpts=N/SR/TB")
    shell_quote(["ffmpeg", "-v", "error", "-i", source, "-af", ",".join(af),
        "-ac", str(keep), "-c:a", "pcm_s24le"]
            + wav_safe(target) + ["-y", target])
    return target


def envelope_heard(path):
    """The curve of a file's audio, or None where there is none to read.

    A camera that gives nothing is ordinary material -- sound that broke
    off, or a track lost in a copy -- and not a fault of the run, so it
    is answered rather than raised and the caller places it by its clock.
    """
    try:
        return video_envelope(path)
    except Exception:
        return None


def place_camera_by_clock(v, position, clocks, reference):
    """Place a camera that gives no sound, by its clock, and say so.

    The offset is the reference clock less this camera's own, so both
    ends come from the one reckoning. Where either clock is missing there
    is nothing to place it with, and it is refused rather than laid down.
    """
    own, base = clocks.get(v), clocks.get(reference)
    st = {"points": 0, "unplaceable": True, "by_clock_only": True}
    if own is None or base is None or cannot_be_placed(
            st, own, [t for w, t in clocks.items() if w != v]):
        print(as_bad("  " + no_place_message(os.path.basename(v))))
        return
    print(T('  %s gives no sound to measure -- placed by its clock '
            'alone, and nothing was found to check it against')
          % os.path.basename(v))
    position[v] = (base - own, 1.0, st)


def align_cameras(videos):
    """Put all cameras on the time axis of the longest one.

    The longest covers the widest range and offers the most sample
    points. A camera matching nothing and carrying no timecode is left
    out: one laid down at a guess is worse than a missing one, which the
    log names. Returns (reference, {path: (a, b, count)}).
    """
    heard = dict((v, envelope_heard(v)) for v, _info in videos)
    # The reference has to be one there is something to measure against,
    # and the longest is the likeliest one.
    speaking = [(v, i) for v, i in videos if heard[v] is not None]
    ref_clip = max(speaking or videos, key=lambda v: v[1]["duration"])
    # The reference sits at zero against itself, unmeasured.
    position = {ref_clip[0]: (0.0, 1.0, {"points": 0})}
    env_ref = heard[ref_clip[0]]
    clocks = dict((v, timecode_seconds(i)) for v, i in videos)
    for v, info in videos:
        if v == ref_clip[0]:
            continue
        env = heard[v]
        if env is None or env_ref is None:
            place_camera_by_clock(v, position, clocks, ref_clip[0])
            continue
        # Sample more densely than for audio against video: two cameras
        # often overlap only partly. Every 30 seconds instead of every
        # two minutes, at least 20 points.
        duration = len(env_ref) * 5.0 / 1000.0
        density = int(max(20, min(120, duration / 30.0)))
        try:
            a, b, st = align_envelopes(env_ref, env, sample_points=density,
                                          distance_s=30.0,
                                          warn=os.path.basename(v))
        except Exception as e:
            print(T('  %s cannot be classified: %s')
                  % (os.path.basename(v), e))
            continue
        # There is no phase way between two cameras, so the envelopes are
        # the whole measurement and the floor is higher than anywhere
        # else: a short jingle otherwise gets a number too.
        if (st.get("quality", 0.0) < CAMERA_MATCH_ENOUGH
                and not fit_places_it(st)):
            st["unplaceable"] = True
        if cannot_be_placed(st, clocks.get(v),
                            [t for w, t in clocks.items() if w != v]):
            print(as_bad("  " + no_place_message(os.path.basename(v))))
            continue
        position[v] = (a, b, st)
    return ref_clip, position


def audible_range(file_path, rate=8000, block=0.05, below_db=40.0):
    """Return where audible sound starts and ends in a file.

    Not file length: a jingle can sit in a longer file with silence at
    the end. The threshold sits 40 dB below the file's own loudest point,
    a fixed one being silent throughout on a quiet master. In seconds.
    """
    try:
        x = decode_audio(file_path, rate=rate)
    except Exception:
        return None, None
    if x is None or len(x) < rate // 4:
        return None, None
    nb = max(1, int(block * rate))
    count = len(x) // nb
    if count < 2:
        return None, None
    level = np.sqrt((np.asarray(x[:count * nb], dtype=np.float64)
                     .reshape(-1, nb) ** 2).mean(1))
    highest = float(level.max())
    if highest <= 0:
        return None, None
    loud = np.where(level > highest * (10 ** (-below_db / 20.0)))[0]
    if not len(loud):
        return None, None
    return (float(loud[0]) * block, float(loud[-1] + 1) * block)


def _intro_outro_entry(file_path):
    """Build the intro or outro entry for the handover file."""
    if not file_path or not os.path.exists(file_path):
        return None
    try:
        info = video_facts(file_path)
    except Exception:
        return None
    duration = round(float(info.get("duration") or 0.0), 3)
    has_audio = bool(info.get("audio"))
    audio_from, audio_until = (audible_range(file_path) if has_audio else (None, None))
    return {"source": os.path.abspath(file_path),
            "duration": duration,
            "has_audio": has_audio,
            # The position follows the audible sound, not the length.
            "audio_from": round(audio_from, 3) if audio_from is not None else None,
            "audio_to": round(audio_until, 3) if audio_until is not None else None}
