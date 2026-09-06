# -*- coding: utf-8 -*-
"""The material: which files belong together, and what they measure.

A piece of the program, read out of the folder beside it by beside().
It cannot import the file it was cut out of, because that file is
still being read while this one is; the program is handed in instead,
and every name this piece uses out of it is bound below, by name.
"""

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

# What the program has and this piece uses, bound once so that the
# material reads as it did in the one file. Five names are missing,
# and the three blocks under the list say which and why.

AUDIO_SUFFIXES = PROGRAM.AUDIO_SUFFIXES
CAMERA_MATCH_ENOUGH = PROGRAM.CAMERA_MATCH_ENOUGH
CEILING_DBTP = PROGRAM.CEILING_DBTP
FILE_FORMAT = PROGRAM.FILE_FORMAT
LIKES_PYTHON = PROGRAM.LIKES_PYTHON
LIMIT_MAX_DB = PROGRAM.LIMIT_MAX_DB
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
decimal_text = PROGRAM.decimal_text
decode_audio = PROGRAM.decode_audio
envelope = PROGRAM.envelope
ffprobe_json = PROGRAM.ffprobe_json
file_timecode = PROGRAM.file_timecode
fit_places_it = PROGRAM.fit_places_it
gcc_phat_offset = PROGRAM.gcc_phat_offset
group_text = PROGRAM.group_text
hashlib = PROGRAM.hashlib
math = PROGRAM.math
no_place_message = PROGRAM.no_place_message
os = PROGRAM.os
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

# Two of the five stand in a piece read after this one:
# run_ffmpeg_with_progress in the checking, which binds the margin and
# parallel_map out of here, and tracks_folder in the processing, which
# is read after that. Both through PROGRAM.

# Two of the five are bent while the run goes on, and a copy taken here
# would answer with the value of the run before: the window sets
# OUTPUT_SINK and ASK_SINK on the program object, which is a write the
# pieces are never told about. ASK_SINK stays over there for that.

# numpy is the fifth, and the one name here that the program has still
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


#---------------------------------------- Which files belong together

# Date and time in a file name: "r_260808_185628" is the eighth of August
# 2026 at 18:56:28. Six digits for the date or eight, six for the time.
NAME_CLOCK = re.compile(r"(?<![0-9])([0-9]{6}|[0-9]{8})[_\-. ]([0-9]{6})"
                        r"(?![0-9])")
# How far the clock in the name may sit from where the previous block ends.
# Recorders write whole seconds, and the length of a block is rarely a
# whole one, so two seconds of slack are needed -- and two blocks that
# really follow one another are never further apart than that.
CLOCK_SLACK = 2.0
# How far two blocks of one recording may sit apart per timecode. A
# recorder that closes one file and opens the next needs a fraction of
# a second; one that stood between the two can be minutes.

# Half an hour is the fence because a clock is set wrong by whole
# hours -- a time zone, or the twelve of AM against PM -- so half of
# the smallest of those catches every one and still lets a real pause
# through. Without a fence a gap of 12:19:48 joined (1.9.2026).
BLOCK_GAP_MAX_S = 1800.0
# What a track cut out of a multichannel file is called at the end. The
# search for continuation blocks has to leave those alone: the number in
# them is a channel, not a block.
SPLIT_MARK = re.compile(r"_Channel\d+(?:\+\d+)?$")


def clock_in_name(name):
    """Return the moment a file name carries: (seconds, before, after).

    Recorders that number their files leave a counter the search for
    continuations can step; mixers write the date and time of day
    instead, which is not a counter and has to be read as a clock and
    held against the length of the block before it. *before* and *after*
    are the rest of the name, so only names built alike are compared.
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
    # Naive on purpose: both names come from the same recorder and the
    # same evening, and only their difference is used.
    return (when.replace(tzinfo=datetime.timezone.utc).timestamp(),
            name[:m.start()], name[m.end():])


def blocks_by_clock(file_path):
    """Find the blocks of one recording by the clock in their names.

    Only files built exactly the same way count: same folder, same
    extension, the same text before and after the clock. Of those, the
    one whose clock sits where the previous block ends is the next.
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
            # "20260808" spell the same day. Which one is meant cannot be
            # decided here, so neither is taken.
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

    Returns (yes, reason). With timecode: the next block starts where the
    previous one ends. Without timecode only the block size is left -- a
    block short of full size is an end of recording, followed by a pause of
    unknown length.
    """
    fits, why = shapes_match(before, after)
    if not fits:
        return False, why
    t_before, t_after = file_timecode(before), file_timecode(after)
    if t_before is not None and t_after is not None:
        gap = t_after - (t_before + sample_count(before) / float(SR))
        # A pause is known and filled with silence on assembly, so a
        # short one is no problem. A long one is not a pause but a
        # clock that was never set: joined, it becomes hours of silence
        # inside the file, and nothing afterwards takes it out again.
        if gap > BLOCK_GAP_MAX_S:
            return False, (T('gap of %s per timecode, too far apart for '
                             'one recording') % as_hms(gap))
        return gap > -1.0, (T('overlap of %s per timecode')
                               % as_hms(abs(gap)))
    # The candidate belongs in the comparison, or the very first step
    # compares a block with itself and always says yes: a finished short
    # take before the real recording would be glued on.
    sizes = [os.path.getsize(p) for p in row]
    sizes += [os.path.getsize(before), os.path.getsize(after)]
    return (os.path.getsize(before) >= 0.98 * max(sizes),
            T('previous block is shorter than the rest'))


def find_continuation_files(file_path):
    """Find every block of the same recording, forwards and backwards.

    Only seamless continuations are appended, and the same test applies
    both ways, so it makes no difference whether the first block or a
    middle one is picked.
    """
    folder = os.path.dirname(file_path) or "."
    name, ext = os.path.splitext(os.path.basename(file_path))
    # A track cut out of a multichannel file ends in a channel number,
    # and looking for the next number would find the next channel. Those
    # are not blocks of one recording, they are different microphones.
    if SPLIT_MARK.search(name):
        return [file_path], []
    # A clock in the name is the more specific reading and comes first:
    # where it is there, the trailing digits are a time of day and
    # stepping them by one would look for a file a second later.
    by_clock = None
    if clock_in_name(name):
        row, discarded = blocks_by_clock(file_path)
        if len(row) > 1:
            return row, discarded
        # Nothing joined by the clock. It may be the session start,
        # written into every block, with the real index in a counter
        # behind it. So the counter rule gets its turn; what the clock
        # found is kept in case the counter finds nothing either.
        by_clock = (row, discarded)
    m = TRAILING_NUMBER.match(name)
    if not m:
        return by_clock or ([file_path], [])
    stem, digits = m.group(1), m.group(2)
    width = len(digits)
    row, discarded = [file_path], []
    # Exactly as they are written, and no other spelling: on a
    # case-sensitive disc REC0002.wav and rec0002.wav are two files, and
    # taking one for the other answers differently depending on the
    # folder listing. Two spellings in a row is two naming logics.
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
        # The counter found nothing either; then what the clock had to
        # say about the neighbours is the better answer.
        return by_clock
    return row, discarded


def track_order_for_camera(own, every, singles=()):
    """Return the audio tracks for one camera, in order.

    Track 1 is the finished mix of what belongs to this camera, so
    taking only the first is correct. Then the same speakers, the
    overall mix minus the crosstalk, and last the camera microphone.
    *singles* get a line of their own where nobody was assigned here;
    every line is the name the track carries in the written file.
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

    The file carries the number of the naming it was written with. Where
    that differs, the keys inside mean something else -- reading it anyway
    would look like it worked and quietly assign the wrong things.
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

    *options* is a list of (key, text) and the key is returned. *switch* is
    the command line switch that preselects the answer; it appears in the
    error message when nobody is there to answer.
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


# What a camera carries beyond the time window at each end. The run's
# own cross-check calls an offset wrong past a single frame, so a second
# is more than twenty times the error it tolerates -- and at the front
# the key frame the copy has to start on usually swallows it anyway.
CAMERA_MARGIN_S = 1.0


def key_frame_at_or_before(video, when):
    """Where the last key frame at or before *when* seconds sits.

    A stream copy that starts between two key frames takes the picture
    from the key frame before it while the sound starts where it was
    asked, and the two then sit up to one group of pictures apart. So
    the cut goes back to a key frame, never forward. Nothing found means
    0.0, which cuts nothing off the front.
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
    The copy starts on the key frame before the window, so the picture
    is not taken from between two of them; the end is cut wherever the
    window ends, whether or not that key frame could be found. keep_s is
    None where neither end has anything to give up.
    """
    first = max(0.0, -offset - CAMERA_MARGIN_S)
    last = min(duration, window_s - offset + CAMERA_MARGIN_S)
    cut_at = key_frame_at_or_before(video, first)
    if cut_at <= 0 and last >= duration - 0.001:
        return 0.0, None
    return cut_at, max(1.0, last - cut_at)


def camera_stamp(info, cut_at, at_s):
    """The timecode a written camera file carries, or nothing.

    *at_s* is where its first frame sits on the wall clock, out of the
    measurement -- the same reckoning every camera gets, so they agree
    with each other. Written at this camera's own rate. Without it, the
    camera's own timecode moved by what was cut off the front is what
    is left, and then each stands on its own clock again.
    """
    fps = max(1.0, info.get("fps") or 30.0)
    if at_s is not None:
        return timecode_string(at_s, fps)
    return timecode_moved(info["tc"], cut_at, fps) if info.get("tc") else ""


def write_camera_file(video, info, audio_tracks, target, a, b, drift, args,
                 head_s=0, tail_s=0, cut_at=0.0, keep_s=None, at_s=None):
    """Write a new video file carrying several audio tracks.

    *audio_tracks* is a list of (name, path). They all sit on the same
    axis and get the same offset and clock correction, so they stay as
    precisely aligned to each other as they were. *head_s* and *tail_s*
    trim samples from the front and back before the offset is applied.
    *cut_at* and *keep_s* say which stretch of the camera is written;
    *a* then counts from there, and the timecode moves with it.
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
    # tracks that follow are inputs of their own and keep their length.
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
    # Behind the audio, so every track above keeps the place the rest of
    # the program counts on.
    data_maps = data_track_maps(video)
    map_args += data_maps
    cmd += ["-filter_complex", ";".join(chains)] + map_args
    if data_maps:
        cmd += ["-c:d", "copy"]
    # use_metadata_tags: keep the camera's QuickTime keys -- Resolve
    #                    reads device and input colour space from them.
    # No write_colr: a colr box that is there travels either way, and
    # where there is none the switch invents 2/2/2, "unspecified".
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
        # much is cut off the front, so the moment this file really
        # begins has to be written here. Whoever plays it reads the
        # camera's place off that.
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
        # ebur128 writes one line per second to stderr. Reading stdout line by
        # line and stderr only afterwards fills its buffer and both wait for
        # each other, so stderr goes to a file rather than a pipe.
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
    # LRA comes from the same pass: the loudness range says how far quiet and
    # loud passages lie apart. For speech 3 to 7 LU is usual; below that it
    # sounds squashed.
    return get(r"I"), get(r"Peak"), get(r"LRA")


def remove_slow_level_drift(env, window=600):
    """Remove slow level changes from an envelope.

    A leveler changes loudness over time, so envelopes from before and
    after look like different signals even though the onsets sit in the
    same places. Subtracting the moving average leaves the onsets and
    drops the level shaping.
    """
    if len(env) < window * 2:
        return env
    kernel = np.ones(window) / window
    return env - np.convolve(env, kernel, mode="same")


def refine_offset(axis, done, a, b, rate=16000, how_many=9):
    """Measure the remaining offset between upload and returned file.

    Envelopes on a 5 ms grid get no closer than a few milliseconds; here
    the same voice is compared directly in both files. Where to measure
    is decided by level -- the runtime is split into sections and the
    loudest second of each used, since somebody speaking rarely is
    silent at almost any fixed spot. Returns milliseconds, or None.
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

    The service can prepend material and change the length; either would
    shift the tracks against each other and undo the alignment.
    De-bleeding removes the other speakers and the leveler bends the
    levels, so the sample points are picked on the processed track, the
    envelopes flattened, and the estimate a median, not a regression.
    """
    print(as_head(T('\nCHECK THE RETURN')))
    HOP, rate = 5.0, 4000
    shaky = []
    # A stereo track that comes back with one channel has been folded at
    # auphonic.com, and no later step can undo that. It is not an error --
    # the run carries on -- but it has to be said, because the difference
    # between the two microphones is then gone from the mix.
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
            # Pick the sample points on the processed track, not the
            # uploaded one: after de-bleeding only one speaker is left,
            # and one comparison over the whole length would be
            # dominated by the passages where the track is now empty.
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
        # Median rather than a regression line: Auphonic shifts a track as a
        # whole or not at all, so there is no slope to estimate here.
        offsets = st.get("offsets") or []
        times = st.get("times") or []
        clock_drift, clock_drift_ppm = 1.0, 0.0
        if offsets:
            v = np.array(offsets)
            a_corr = -float(np.median(v))
            spread = float(np.median(np.abs(v - np.median(v))) * 1000)
            # A returned file drifting against the uploaded one carries
            # clock drift -- an older production reused whose tracks came
            # from a run with a different correction. A fixed offset is
            # then not enough and the crossing voice becomes audible.
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
        # Where the file was coarsely trimmed to a window set later,
        # there is deliberate slack at both ends and the offset should be
        # exactly that. Measured on the voice rather than the envelope:
        # between tracks, a second voice becomes audible from about 20 ms.
        fine = refine_offset(track["axis"], done, a_corr, clock_drift)
        if fine is not None and abs(fine) < 500.0:
            a_corr += fine / 1000.0
        edge = track.get("edge", 0.0)
        ms = (a_corr - edge) * 1000.0
        # Record what was measured here for the metrics.
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
                      % decimal_text("%+.1f" % clock_drift_ppm)) \
                if clock_drift_ppm \
                else T('  -->  aligned')
        else:
            track["ready"] = done
        uncertain = st.get("points", 0) < 5 or spread > 150.0
        line = (T('  %-20s offset %s ms%s, length %s s, spread %s '
                  'ms, %s of %s points%s%s')
                % (track["name"], decimal_text("%+.1f" % ms),
                   "" if fine is None else T(' (fine: %s ms)')
                   % decimal_text("%+.1f" % fine),
                   decimal_text("%+.3f" % length),
                   decimal_text("%.0f" % spread),
                   group_text(st.get("points", 0)),
                   group_text(st.get("candidates", 0)), remark,
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

    The measuring sum is several hundred megabytes and the run carries
    on long after it. A file already gone is not a fault, but the answer
    is handed back rather than swallowed, for a caller that does care.
    """
    try:
        os.unlink(path)
    except OSError:
        return False
    return True


def normalise_loudness(tracks, target_lufs, tmpdir, master=None, channels=1):
    """Compute one common gain for all tracks.

    The sum is measured, not the single track, because only the sum is
    heard; the same gain goes on every track so the speakers keep the
    balance Auphonic set. Where the finished mixdown is present it is
    the yardstick. *target_lufs* None means adjust nothing -- the sum is
    still measured, or an omitted adjustment looks like a fault later.
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
                  % (decimal_text("%.1f" % m_have),
                     decimal_text("%.1f" % (m_peak if m_peak is not None
                                            else 0.0)),
                     os.path.basename(master)))
            target_lufs = m_have
    total_sum = os.path.join(tmpdir, "measure_sum.wav")
    ready = [track["ready"] for track in tracks]
    # Measured in the form it is delivered in: a two channel mix sits a good
    # three decibels above the same mix as one track. A stereo track raises
    # the count on its own -- the mix it goes into has two channels, so the
    # measurement has to have them too.
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
    # summing it anyway copies hours of audio to arrive at the same
    # samples. *ours* says whether this run made that file: only a file
    # of our own may be deleted by the clean-ups further down.
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
              % (decimal_text("%.1f" % have),
                 decimal_text("%.1f" % (peak if peak is not None else 0.0)),
                 T(', range %s LU') % decimal_text("%.1f" % lra_range)
                 if lra_range is not None else ""))
        print(T('  Not adjusted:      taken from the source files -- no gain '
                'on any track and no\n                     limiter. The '
                'sound leaves exactly as it came in.'))
        if ours:
            remove_quietly(total_sum)
        return 0.0, None
    gain = target_lufs - have
    print(T('  Sum of tracks:     %s LUFS, peak %s dBTP%s')
          % (decimal_text("%.1f" % have),
             decimal_text("%.1f" % (peak if peak is not None else 0.0)),
             T(', range %s LU') % decimal_text("%.1f" % lra_range)
             if lra_range is not None else ""))
    print(T('  Target:            %s LUFS  ->  %s dB on every track')
          % (decimal_text("%.1f" % target_lufs),
             decimal_text("%+.1f" % gain)))
    # Without a ceiling the gain would have to drop far enough for the loudest
    # peak to fit -- a single scraping chair can cost eight decibels. So the
    # gain stays and a limiter catches the peaks.
    if peak is not None and gain > CEILING_DBTP - peak:
        print(T('  Peaks:             %s dB above %s dBTP -- the '
                'limiter catches them')
              % (decimal_text("%+.1f" % (peak + gain - CEILING_DBTP)),
                 decimal_text("%.1f" % CEILING_DBTP)))
    # How much the limiter would have to take off is only known once the curve
    # is computed. Taking off more than a handful of decibels means not that
    # the peak does not fit the target but that the target does not fit the
    # material; then quieter beats squashed.
    curve, gone = limiter_curve(measured_on, tmpdir, gain)
    # With the finished mixdown from auphonic.com beside it the question is
    # answered: that is how much limiting auphonic.com itself needed to reach
    # this loudness from the same tracks, so nothing needs capping.
    limit = 12.0 if after_yardstick else LIMIT_MAX_DB
    if gone > limit + 0.05:
        back = gone - limit
        print(T('  Too much:          the limiter would have to take %s '
                'dB away. More than %s dB\n                     sounds '
                'squashed -- %s dB less gain.')
              % (decimal_text("%.1f" % gone), decimal_text("%.0f" % limit),
                 decimal_text("%.1f" % back)))
        gain -= back
        curve, gone = limiter_curve(measured_on, tmpdir, gain)
        print(T('  Remains:           %s dB on every track, that is '
                '%s LUFS instead of %s')
              % (decimal_text("%+.1f" % gain),
                 decimal_text("%.1f" % (have + gain)),
                 decimal_text("%.1f" % target_lufs)))
    if gone > 0.05:
        print(T('  Limiter:           at most %s dB, the same curve on '
                'every track%s')
              % (decimal_text("%.1f" % gone),
                 T(' (auphonic.com takes the same amount)')
                 if after_yardstick else ""))
    # For checking in the editor. -16 LUFS is the figure for web and podcast;
    # broadcast measures against -23, where the meter reads correspondingly
    # higher.
    print(T('  Result:            about %s LUFS, peak %s dBTP')
          % (decimal_text("%.1f" % (have + gain)),
             decimal_text("%.1f" % (CEILING_DBTP if gone > 0.05
                                    else min(CEILING_DBTP,
                                             (peak or 0.0) + gain)))))
    # The loudness range measures whether any dynamics are left. A limiter that
    # only catches peaks leaves it almost untouched; where it gets small,
    # something was squashed -- and then not by the limiter but by whatever was
    # done before.
    if lra_range is not None:
        if lra_range < 2.0:
            print(as_warn(T('  Caution: range      only %s LU -- very '
                            'tight. Speech is usually 3 to 7 LU;\n          '
                            '           below that it sounds squashed. '
                            'Check how strongly the leveler\n               '
                            '      is set at auphonic.com.')
                          % decimal_text("%.1f" % lra_range)))
        else:
            print(T('  Range:             %s LU (speech is usually 3 to '
                    '7 LU)') % decimal_text("%.1f" % lra_range))
    if ours:
        remove_quietly(total_sum)
    return gain, curve


def limiter_curve(total_sum, tmpdir, gain, ceiling=CEILING_DBTP):
    """Compute the limiter gain curve once, on the sum.

    The same curve goes on every single track, so the tracks add up to
    exactly the mix again: (a+b)*g equals a*g + b*g. A limiter per track
    would follow its own level and clamp the loud one harder. Block by
    block, with one block of lookahead and a linear cross-fade, or it
    clicks; the audio streams. Returns (path, reduction in dB).
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
                    # The last block waits for the next chunk: without it there
                    # would be no lookahead there and the peak would come
                    # through a tenth of a second early.
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
                # One block of lookahead: the reduction is in place before the
                # peak.
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

    A stereo track is stereo because two microphones stand apart, and
    folding it to one throws that difference away for good. So the rule
    is "keep what the source has". More than two channels is a recorder
    file, not a track; those are cut into tracks before they get here,
    and anything still arriving with more is folded.
    """
    try:
        return 2 if channel_count(file_path) == 2 else 1
    except Exception:
        return 1


def channel_filter(have, want):
    """The filter that brings *have* channels to *want*, without a level jump.

    Both directions are written out rather than left to ffmpeg, whose
    equal-power law lands three decibels out either way -- inaudible in
    a single listen and wrong in every meter. Worse, it depends on the
    output format, so the same call is right in one place and out in the
    next. Here one to two is a copy and two to one a half-and-half sum.
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
    allowed: held to two of thirty-two, a pool sized by the thirty-two
    means threads taking turns. process_cpu_count arrived in Python
    3.13, so the older one stays as the fallback.
    """
    ask = getattr(os, "process_cpu_count", None) or os.cpu_count
    try:
        return max(1, int(ask() or 2))
    except Exception:
        return 2


def python_note():
    """One line about the Python this is running on, for the log.

    Said rather than assumed: a report that opens with the version it ran
    under saves the first three questions when something behaves oddly.
    """
    now = "%d.%d.%d" % sys.version_info[:3]
    if now == LIKES_PYTHON:
        return "Python %s" % now
    return "Python %s  (recommended version %s)" % (now, LIKES_PYTHON)


def prework_standing(shares):
    """How far the prework has got, and one line per file still at it.

    Every task of a file counts the same, and every file counts the
    same however many tasks it has. What is finished leaves the list:
    the row has served its purpose and the list stays short.
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

    Pulling the audio out of an hour of 4K and reading a wav file are
    one step each. Equal shares would make the bar say nothing: it would
    stand still through the long one and jump through the short ones.
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
    ffmpeg or numpy, and both let other threads run. Where a thread
    cannot be started the rest is worked through here. An error inside
    the work is raised after all of it is done, so one unreadable file
    does not leave threads running behind a traceback.
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

    Everything the interface needs before it can draw a row is measured
    here in parallel, and the rows are then built from memory. On an
    external volume, asking one after another is the difference between
    a window that stands still for minutes and one that does not.
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
                # A file that cannot be measured is reported where its
                # row is drawn. Here it must not stop the rest.
                pass

    parallel_map(todo, one, workers)


# A channel counts as silent when it stays this far under the loudest
# channel of the same file. A recorder writes four channels whether or
# not anything was plugged in, and an empty one must not become a
# speaker.
SILENT_BELOW_DB = 45.0
# Absolute floor for a channel that carries anything at all. Under this
# there is only the noise floor of the converter, and a judgement made
# there is comparing dither rather than signal.
QUIET_BELOW_DBFS = -70.0

# Two channels count as the same signal from here up. Mono panned to
# both sides gives exactly 1.0; a hair less allows for lossy coding.
SAME_SIGNAL = 0.999

# How far off zero a shared sound may arrive and still count as coming
# through one pair of microphones. Sound travels 34 cm in a
# millisecond, so this covers every usual stereo spacing and no pair of
# clip-on microphones on two people.
PAIR_DELAY_MS = 1.0

# This much of the strongest common component has to sit inside that
# window for the two channels to be one pair. Every stereo technique
# scores near 1, two clip-ons near 0.1; nothing lands in the middle.
PAIR_AT_ZERO = 0.5

# Two more legs under the same judgement. The share says the two
# channels hear the same thing at the same moment, and in one room
# every microphone does that, so the share alone cannot tell a pair
# from a neighbour. First leg: the spacing measured has to be small.
PAIR_APART_METRES = 0.3
# And it may only be formed where it stands on something. The delay is
# read off the places whose peak missed the zero window; a real spacing
# turns up at nearly every place, so a single one is not enough to
# throw a plain stereo track away.
PAIR_APART_SHARE = 0.25

# Second leg: a pair has to stand out from the two pairs that share a
# channel with it. Pairs running across every pair boundary can score
# as high as the real ones; where nothing stands out, nothing is said.
PAIR_STANDS_OUT = 0.15

# The delay is measured on this many places spread over the file. More
# does not change the figure; on an hour of audio it would only cost
# time while somebody waits for the file list.
PAIR_PLACES = 120

# Below this many usable places the median means nothing, and the row
# says so with the number instead of claiming anything.
PAIR_ENOUGH_PLACES = 8

# Which level counts as "the loud part of this file". The gate below
# hangs on it, so it has to be a level the recording really reaches
# and has to survive a single loud moment. A decile of the places does
# both, where the file's peak would move by tens of decibels.
PAIR_LOUD_PERCENTILE = 90.0

# And the gate sits this far under it. Not a threshold for silence --
# that job belongs to the correlation height further down. What this
# does is hold a recording's own pauses out of the median: much deeper
# and the answer is read from room tone.
PAIR_GATE_UNDER_DB = 20.0


def channel_rate(file_path, channels, want=16000):
    """Pick a working rate that fits the file in memory.

    16 kHz gives the delay measurement a sixteenth of a millisecond,
    which is what it wants; an hour of four channels at that rate is a
    gigabyte, so a long or wide file is read more coarsely. Halving the
    rate halves the resolution.
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
# How many samples in a row on the stop make one event. One is
# rounding, two is rounding twice; three in a row is a crest the
# converter could not follow, and that is what is heard. It holds for
# speech and music, not for rumble under about 50 Hz.
CLIP_RUN_SAMPLES = 3


def clipping_facts(file_path, stream=0, least=CLIP_RUN_SAMPLES):
    """Count the runs of samples sitting on the stop, per channel.

    Counted here rather than asked of ffmpeg: ``astats`` reports how
    many samples equal the loudest and quietest value *in this file*,
    wherever those lie, so it cannot tell single samples from runs and
    counts files that never reach full scale. Integer formats only --
    float has no stop. Returns {channel: (runs, longest, ms, first s)}.
    """
    if np is None or pcm_kind(file_path, stream) == "pcm_f32le":
        return {}
    try:
        # The stream that was asked about. Reading the rate and the
        # channel count off the first one while the format comes from
        # the nth would count the samples of one stream against the
        # shape of another.
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

    At the full rate, not the 16 kHz the levels are measured at: a run
    of three samples does not survive resampling. Read block by block,
    because an hour of stereo does not belong in memory at once. Through
    s16le on purpose -- 16 and 24 bit give the same count that way,
    while s32le needs a threshold depending on the original's depth.
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
                        # It ended exactly on the block boundary while
                        # this block has a hit further along. Without
                        # this the run would be dropped: the loop above
                        # skipped the column, and the join does not
                        # apply either.
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
        # Closed rather than guarded: a pipe being read to its end
        # closes without complaint, and a reader that stopped early
        # would leave ffmpeg writing into a pipe nobody empties.
        p.stdout.close()
        try:
            p.wait(timeout=20)
        except Exception:
            p.kill()
            p.wait()
    if p.returncode:
        # Half a file read is worse than none: the answer would be
        # given on the part that arrived.
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
    pan filter decodes the whole file again for every channel. What
    comes out is 32 bit floats whatever the file was, and nothing
    measured here needs more. Empty rows come back where ffmpeg failed,
    since half a file read would be judged as if it were whole.
    """
    n = max(1, channel_count(file_path))
    # One pass, not one per channel: everything comes out interleaved
    # and is taken apart here.
    p = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", file_path,
         "-map", "0:a:%d" % stream, "-ar", str(rate), "-f", "f32le", "-"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    parts = [[] for _ in range(n)]
    rest = b""
    frame = 4 * n
    try:
        while True:
            # A block of whole frames at a time. Reading the lot into one
            # array first would double the memory of a long wide file.
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
        # A reader that stopped early leaves ffmpeg writing into a pipe
        # nobody empties, and it would sit there for ever.
        try:
            p.wait(timeout=20)
        except Exception:
            p.kill()
            p.wait()
    if p.returncode:
        # Half a file read is worse than none: the judgement would be
        # made on the part that arrived and then stored under the file's
        # size and time, so it would never be measured again.
        return [np.zeros(0, dtype=np.float32) for _ in range(n)]
    # Joined one channel at a time, and each list of pieces dropped as
    # soon as it has been joined. Building them all first would hold the
    # whole recording twice -- which is what the chunked read is for.
    out = []
    for k in range(n):
        out.append(np.concatenate(parts[k]) if parts[k]
                   else np.zeros(0, dtype=np.float32))
        parts[k] = None
    return out


def channel_at_zero(first, second, rate, most=PAIR_PLACES, window=2048):
    """How much of what two channels share arrives at the same time.

    One pair of microphones hears everything at nearly the same moment;
    two on two people hear each other late. So the question is not how
    alike the channels are but *when* what they share arrives. Returns
    (share, places, apart, agreed). Plain correlation, not PHAT, which
    turns the silences speech leaves in both channels into a spike.
    """
    # Both legs come off the same places, and only one off all of them:
    # the share is the median over every usable place, the distance
    # only over those whose peak missed the window -- see pair_spacing.
    width = min(len(first), len(second))
    if width < window * 2:
        return 0.0, 0, 0.0, 0
    reach = max(4, int(0.020 * rate))
    close = max(1, int(PAIR_DELAY_MS * rate / 1000.0))
    spots = np.linspace(0, width - window - 1, most).astype(int)
    # How loud each place is, all of them before any is judged: the gate
    # is a level of this file and cannot be known one place at a time.
    # A peak is not a level, which is why the gate hangs on the places
    # and not on the loudest sample.
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
    # out of, and the highest point of the correlation is wherever the
    # noise happens to be tallest.
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

    *away* is how late the strongest shared sound was where it missed
    the zero window. A spacing is a fixed length of air and turns up as
    the same delay again and again; where the delays scatter there is
    none, only a correlation wandering about a room. So the median
    counts only if most agree within one window, and over enough places.
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

    Two rules, and a channel need fail only one: far enough under the
    loudest is an input nobody plugged anything into, and under the
    absolute floor there is only converter noise. The absolute rule
    applies only where one channel is above it. Returns ([silent],
    [reason]), the reason naming which rule caught it and by how much.
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

    Built in one place because three ask for it: the one that stores,
    and the two that ask whether it is there. Spelled out twice, the
    recipe mark went into the store and not into the question -- and
    the answer was then "not measured" for ever, which put the work
    back in the queue every time the rows were drawn.
    """
    return "channelfacts-" + channel_recipe_mark()


def channel_facts(file_path, rate=None, stream=0):
    """Measure the channels of one file: how loud, how empty, how alike.

    Every neighbouring pair is measured, not every second one: on a
    mixer, channels 2 and 3 can be the stereo pair as well as 1 and 2.
    So entry k of *pair_same* and *pair_zero* is about channels k and
    k+1, and those lists are one shorter than the channel count.
    *pair_places* says how many places could be measured at all.
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

    Two rules catch a channel and they are different recording faults:
    nothing plugged in, against a level so low that only the converter's
    own noise is left. One wording for both would be wrong for the
    first -- a channel far under the loudest can still be well above it.
    """
    reason = why[which - 1] if 0 < which <= len(why) else None
    if reason and reason[0] == "under" and reason[1] < float("inf"):
        return T('Channel %d is %s dB under the loudest -- nothing '
                 'plugged in') % (which, decimal_text("%.0f" % reason[1]))
    if reason and reason[1] > float("-inf"):
        return T('Channel %d at %s dBFS -- only converter noise '
                 'left') % (which, decimal_text("%.0f" % reason[1]))
    return T('Channel %d is silent -- unused input') % which



def kind_makes_stereo(kind, channels):
    """Is a two-channel file stereo because of what it is?

    An intro or an outro is a finished stereo mix, not two microphones,
    and the measurement is at its weakest on exactly that material:
    music has no speech pauses and an effect laid on afterwards can
    produce any correlation. Two channels only -- with three or more
    the measurement decides again.
    """
    return (kind in (TYPE_INTRO, TYPE_OUTRO)
            and int(channels or 0) == 2)


def apart_places(agreed, places):
    """How many places the spacing rests on, as a piece of the line.

    Empty where there is nothing to say. Without it a distance out of
    one place of a hundred reads exactly like one out of all of them.
    """
    if not agreed or not places:
        return ""
    return T(', agreed at %s of %s places') % (group_text(agreed),
                                              group_text(places))


def channel_joins(facts, kind=None):
    """Judge every pair of neighbours: could these two be one stereo track?

    Returns [(k, stereo, certain, reason)], k the left channel. Every
    neighbour is asked, not every second one -- fixed pairs would get a
    confident wrong answer. What decides is *when* the two channels hear
    the same thing, not how alike. Where nothing can be measured no pair
    is proposed: two speakers in one track is the error nobody sees.
    """
    # Not seen by this: two recordings laid on a common time axis
    # before being put into one file. Aligning them removes the very
    # delay measured here, and the pair then looks like one.
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
        # were usable at all. A distance is only worth naming when it
        # turns up over and over -- see pair_spacing.
        stood_on = apart_places(
            from_agreed[k] if k < len(from_agreed) else None, places)
        # What belongs on a row in the file list is the answer, not the
        # arithmetic behind it. What was measured is in channel_at_zero.
        if silent[k] or silent[k + 1]:
            which = (k + 2) if silent[k + 1] else (k + 1)
            out.append((k, False, True, hush_reason(which, why)))
        elif r is not None and r >= SAME_SIGNAL:
            out.append((k, True, True,
                        T('both channels identical -- mono laid on both '
                          'sides')))
        elif at_zero is not None and at_zero < PAIR_AT_ZERO:
            # 343 m/s: the delay is the spacing, and giving it in
            # metres is what lets anyone check the answer against the
            # room the recording was made in.
            out.append((k, False, True,
                        T('probably two microphones -- about %s m '
                          'apart%s')
                        % (decimal_text("%.1f" % ((late or 0.0) * 0.343)),
                           stood_on)))
        elif at_zero is not None and at_zero >= PAIR_AT_ZERO:
            # The share is high enough. Two more questions before this
            # is called a pair, because the share alone answers "yes"
            # for every microphone in the same room.
            metres = (late or 0.0) * 0.343
            beside = [zero[j] for j in (k - 1, k + 1)
                      if 0 <= j < len(zero) and zero[j] is not None]
            if metres > PAIR_APART_METRES:
                # Measured apart, so not one place, however well the two
                # agree. Same wording as the plain two-microphone case:
                # it is the same finding, reached the long way round.
                out.append((k, False, True,
                            T('probably two microphones -- about %s m '
                              'apart%s')
                            % (decimal_text("%.1f" % metres), stood_on)))
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
            # the two channels have in common: the number is what tells
            # a quiet recording from two channels that really share
            # nothing.
            out.append((k, False, False,
                        T('not recognisable -- only %s of %s places '
                          'where both channels carry sound, %s needed')
                        % (group_text(places or 0), group_text(PAIR_PLACES),
                           group_text(PAIR_ENOUGH_PLACES))))
    return out


def joined_channels(facts, choice=None, kind=None):
    """Which neighbours are actually joined, after the ticks.

    A channel belongs to at most one pair, so the answer has to be a set
    that does not overlap. Walking from the left and taking the first
    join that fits is what the interface shows too. Returns
    {left channel: True} for every pair that is joined.
    """
    judged = {k: stereo
              for k, stereo, _sure, _why in channel_joins(facts, kind)}
    picked = dict(choice or {})
    n = int(facts.get("channels") or 0)
    silent = list(facts.get("silent") or [])

    def possible(k):
        """An unused input cannot be one side of a stereo track.

        The interface offers no tick where one of the two is silent, but
        a tick made earlier outlives the measurement it was made under:
        take a block away and what carried something may not any more.
        """
        return not ((k < len(silent) and silent[k])
                    or (k + 1 < len(silent) and silent[k + 1]))

    # First what the measurement proposes, on its own: from the left,
    # each pair it found, skipping what is already spoken for.
    out, taken = {}, set()
    for k in range(max(0, n - 1)):
        if k in taken or (k + 1) in taken or not possible(k):
            continue
        if judged.get(k, False):
            out[k] = True
            taken.update((k, k + 1))
    # Then the hand, as a correction of that proposal rather than an
    # exception inside it. A tick taken away means one pair fewer and
    # nothing else; a tick set means one pair more, and its two
    # neighbours lose theirs.
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

    "Channel" stays English in every language: it is the word on the
    recorder and in every manual, and translating it would mean the
    interface and the hardware no longer match. A plus joins a pair
    rather than an ampersand, which splits a command in every shell.
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

    A plain WAV keeps its sizes in 32 bit and stops at 4 GiB. Past that
    ffmpeg writes a header naming less than what is there, every reader
    believes the header, and the tail is gone with nothing saying so.
    RF64 is the same file with 64 bit sizes, and "auto" only switches
    when needed. Only for WAV: ffmpeg refuses the option elsewhere.
    """
    return (["-rf64", "auto"]
            if os.path.splitext(target)[1].lower() == ".wav" else [])


def audio_stream_facts(file_path, stream=0):
    """What ffprobe says about one audio stream, counted among its own.

    *stream* is the number the rest of the program uses -- the nth audio
    stream, 0:a:N to ffmpeg -- not the position in the whole stream
    list. Nothing there means an empty answer, read the same way by all.
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

    As deep as the original, no deeper: writing a 16 bit recorder file
    as 24 bit costs half again in size and adds nothing. Asked about the
    stream it was given -- a camera file with a 16 bit mix first and 24
    bit takes behind it was being copied out at the depth of the mix.
    """
    a = audio_stream_facts(file_path, stream)
    if str(a.get("sample_fmt") or "").startswith(("flt", "dbl")):
        return "pcm_f32le"
    # bits_per_raw_sample is missing for 16 bit files, so
    # bits_per_sample answers as well. Both absent means unknown, and
    # 24 bit is the safe guess: too deep costs space, too shallow
    # throws away what was recorded.
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

    The name says which channels are in it, in the words the file list
    uses. Two things must be unique: the channels, or channel 12 lands
    on the file of 1 and 2; and the source, since every piece goes into
    one folder and two cards with the same file name would overwrite.
    The trailing digit carries a mark, or it would read as a counter.
    """
    stem = os.path.splitext(os.path.basename(file_path))[0]
    tag = "+".join(str(c + 1) for c in channels)
    mark = hashlib.sha1(os.path.abspath(file_path).encode(
        "utf-8", "replace")).hexdigest()[:8]
    return os.path.join(folder, "%s_%s_Channel%s.wav"
                        % (safe_filename(stem)[:60], mark, tag))


def split_channels(file_path, channels, target, stream=0, rate=None):
    """Write one track of a multichannel file into a file of its own.

    *channels* is which channels the track is made of. Everything else
    stays as recorded; *rate* forces a sample rate, needed for camera
    audio at 44.1 kHz while the rest of the run is at 48. The recording
    time goes with the piece: everything after this asks the piece, and
    without it a real pause between blocks would be swallowed.
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

    Empty where nothing has to happen: a single channel, or one pair
    that stays together. Silent channels are not in the answer -- an
    unused recorder input must not become a speaker. *name* is what the
    tracks are called; without it the file name does the work.
    """
    rows = channel_tracks(facts, name or os.path.splitext(
        os.path.basename(file_path))[0], choice)
    if len(rows) <= 1 and not any(silent for _c, _l, silent in rows):
        return []
    return [(chs, label) for chs, label, silent in rows
            if not silent and chs]


def expand_chains_to_tracks(chains, split_of):
    """Turn recordings into tracks where one file holds several.

    A recorder writing four channels gives four tracks, and a recording
    of three blocks gives three blocks per track, so the blocks are cut
    first and the pieces regrouped. Grouped on the original files, never
    on the pieces: those are named after their channel, and the search
    for continuations would take channel two for the next block.
    """
    out = []
    for row, discarded in chains:
        pieces = [list(split_of(x) or []) for x in row]
        how_many = max((len(x) for x in pieces), default=0)

        def which(row_of_pieces):
            """The channels each piece is made of, in order.

            Counting the pieces is not enough: one block cut into
            [1][2][3+4] and the next into [1+2][3][4] both give three,
            and zipping them would put two different signals on one row.
            """
            out = []
            for x in row_of_pieces:
                stem = os.path.splitext(os.path.basename(x))[0]
                mark = SPLIT_MARK.search(stem)
                out.append(mark.group(0) if mark else stem)
            return out

        # A recording whose blocks did not all come apart the same way
        # stays whole: two different signals on one row would be worse
        # than not splitting at all.
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

    Channel count and sample rate have to be the same: the channels are
    judged across all blocks, and one that is number three in one block
    and four in the next makes nonsense of that. Bit depth may differ.
    """
    a, b = audio_shape(first), audio_shape(second)
    if not a[0] or not b[0]:
        return True, ""
    if a == b:
        return True, ""
    if a[0] != b[0]:
        return False, (T('%s channels against %s')
                       % (group_text(a[0]), group_text(b[0])))
    return False, (T('%s Hz against %s Hz')
                   % (group_text(a[1]), group_text(b[1])))


def blocks_facts(paths):
    """Judge the channels over a whole recording, not over one block.

    A recording made of blocks is one recording and its channels are the
    same throughout, but the first block alone can be badly wrong -- a
    soundcheck reads as one pair where the show reads as ten tracks. So
    each block is measured on its own and the answers combined, the pair
    judgement taken from the block where that pair is loudest.
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
        # The block where this pair is loudest: judging a pair on the
        # block where it is silent measures the converter's noise.
        best, loudest = None, float("-inf")
        for f in usable:
            measured = f.get("pair_zero") or []
            if i >= len(measured) or measured[i] is None:
                # This block did not measure the pair -- one of the two
                # was silent in it. Taking its answer would mean taking
                # no answer at all.
                continue
            here = min(_level_of(f, a), _level_of(f, b))
            if here > loudest:
                best, loudest = f, here
        def of(name):
            """Entry i of one of the block's lists, or nothing.

            Guarded one by one: hand-made facts are this function's
            documented input, and there the three lists can be of
            different lengths.
            """
            row = (best or {}).get(name) or []
            return row[i] if i < len(row) else None

        same.append(of("pair_same"))
        zero.append(of("pair_zero"))
        apart.append(of("pair_apart"))
        agreed.append(of("pair_agreed"))
        # The place count comes from the block the answer comes from.
        # Where no block could measure the pair there is no such block,
        # and the number to report is the one the best of them reached
        # -- the row says how close it came, not zero.
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

    Reading every channel of an hour of audio takes seconds, and the
    file list is rebuilt on every change. Keyed on size and modification
    time, so a changed file is measured again.
    """
    # Kept on disc, unlike most: reading every channel of an hour of
    # audio takes 20 to 50 seconds, and without this every start of
    # the program does it again. "channels" alone is the plain count.
    return probe_remember(channel_facts_name(), file_path,
                          lambda: channel_facts(file_path),
                          keep=True, as_json=True)


def channel_tracks(facts, name="Track", choice=None):
    """Return the tracks one file contributes, after the pair judgement.

    *choice* overrides the proposal per pair, {left channel: joined},
    which is what the tick in the file list writes. Returns
    [(channels, label, silent)]; *channels* is a tuple of indices, two
    for a stereo pair and one otherwise, or empty where the file has
    only one channel and stays as it is.
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
    # One track left over means the numbering says nothing -- then the
    # file name alone is the better label.
    awake = [t for t in out if not t[2]]
    if len(awake) == 1:
        out = [(t[0], name if t is awake[0] else t[1], t[2]) for t in out]
    return out


def mix_width(tracks):
    """How many channels a mix of these tracks is delivered in.

    Two where there are several: a mix is what is listened to and
    measured, and two channels is the form it is delivered in. One
    recording is the exception -- nothing to mix, so nothing is widened.
    A stereo source raises the count on its own either way.
    """
    if len(tracks) > 1:
        return 2
    return max(1, widest_track([track.get("ready") or track.get("axis")
                                for track in tracks])) if tracks else 1


def mix_tracks(sources, target, gain=0.0, curve=None, channels=1):
    """Sum several equally long tracks into one.

    The gain and the limiter curve are the same for all tracks, so the
    single tracks add up to exactly the mix again. channels=2 asks for
    two, and a stereo source raises that on its own. The widening
    happens before the sum, the only way a stereo source keeps its
    sides, and by "c1=c0" -- a plain conversion loses three decibels.
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
        # The same gain curve as on all other tracks, hence a second input
        # rather than a limiter of its own. The curve is brought to the
        # channel count by hand: left to ffmpeg, one curve channel against
        # two of signal would come with the equal-power law and quietly take
        # another 3 dB off everything.
        fc += "[both]"
        parts += ["-i", curve]
        fc += ";[both]aformat=sample_fmts=fltp:sample_rates=%d[gm];" % SR
        fc += "[%d:a]%s,aformat=sample_fmts=fltp:sample_rates=%d[gc];" % (
            len(sources), channel_filter(kept_channels(curve), channels), SR)
        fc += "[gm][gc]amultiply[out]"
    else:
        fc += "[out]"
    # The clock of the first source goes with the mix. Without it a
    # levelled file came out with no timecode at all, and a recording
    # with no clock cannot be placed against anything afterwards -- so
    # the level was left alone wherever the clock still mattered.
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

    The obvious chain rounds to whole sample rates, which at 48 kHz
    means steps of 20.8 ppm -- coarse correction can live with that, the
    fine correction cannot. So the intermediate rate is a hundred times
    higher. The built-in resampler sometimes fails at such ratios and
    soxr does not; without soxr the coarse path is used.
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

    Audio time = a + b * reference time. The drift is removed first,
    then the offset divided by b; the track is cut to the window start
    and padded with silence to its full length. Every track gets the
    same window, or Auphonic cannot remove the crosstalk. The channel
    count is the source's; only more than two is folded.
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

    A camera that gives nothing is ordinary material: one whose sound
    broke off after a moment, or a file that lost its track in a copy.
    That is not a fault of the run, so it is answered rather than
    raised -- and the caller places the camera by its clock and says
    so, instead of the run stopping on the first line.
    """
    try:
        return video_envelope(path)
    except Exception:
        return None


def place_camera_by_clock(v, position, clocks, reference):
    """Place a camera that gives no sound, by its clock, and say so.

    The measured offset is the reference clock less this camera's own
    -- measured on 3.9.2026 against two cameras five seconds apart,
    a = -5.000 at a quality of 0.912. Both ends therefore come from
    the one reckoning, and where either clock is missing there is
    nothing to place it with and it is refused rather than laid down.
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

    The longest is the reference because it covers the widest range and
    offers the most sample points. A camera that matches nothing and
    carries no timecode is left out rather than placed: a camera laid
    down at a guess is worse than a missing one, which the log names.
    Returns (reference, {path: (a, b, count)}), camera time = a + b * t.
    """
    heard = dict((v, envelope_heard(v)) for v, _info in videos)
    # The reference has to be one there is something to measure
    # against. The longest of the others otherwise stops the run on
    # its first line -- and the longest is the likeliest reference.
    speaking = [(v, i) for v, i in videos if heard[v] is not None]
    ref_clip = max(speaking or videos, key=lambda v: v[1]["duration"])
    # The reference sits at zero against itself, and nothing had to be
    # measured to find that out.
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
        # Sample more densely than for audio against video: two cameras often
        # overlap only partly, and what lies outside the overlap drops out as a
        # sample point anyway. Every 30 seconds instead of every two minutes,
        # at least 20 points.
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
        # There is no phase way between two cameras, so the envelopes
        # are the whole measurement and the floor is higher than
        # anywhere else. A short jingle otherwise gets a number too, and
        # on the axis it shrinks the common window to nothing.
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

    Audible sound, not file length: a jingle can sit in a longer file
    with silence at the end, and what counts is when it stops. The
    threshold sits 40 dB below the loudest point of the file itself, a
    fixed value being silent throughout on a quietly mastered jingle.
    Returns (start, end) in seconds, or (None, None).
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
            # When the audible sound starts and stops. The position follows
            # that, not the file length.
            "audio_from": round(audio_from, 3) if audio_from is not None else None,
            "audio_to": round(audio_until, 3) if audio_until is not None else None}
