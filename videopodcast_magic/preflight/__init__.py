# -*- coding: utf-8 -*-
"""The preflight: does the material fit together before the long run?

A piece of the program, read by beside(). It cannot import the file it
was cut out of, so the program is handed in and every name used out of
it is bound below. run_ffmpeg_with_progress at the end does not check:
it is what the long steps run ffmpeg through.
"""

# beside() puts the program here before this file is read.
PROGRAM = PROGRAM

# What this piece uses out of the program, bound once. Nine names are
# missing, and the three blocks under the list say which and why.

ByFile = PROGRAM.ByFile
CAMERA_MARGIN_S = PROGRAM.CAMERA_MARGIN_S
RUN_STOP = PROGRAM.RUN_STOP
SR = PROGRAM.SR
Stopped = PROGRAM.Stopped
T = PROGRAM.T
THREAD_SHARE = PROGRAM.THREAD_SHARE
TN = PROGRAM.TN
TRAILING_NUMBER = PROGRAM.TRAILING_NUMBER
VERSION = PROGRAM.VERSION
_block_levels = PROGRAM._block_levels
_logs_atom_text = PROGRAM._logs_atom_text
_windows_for_pair = PROGRAM._windows_for_pair
as_bad = PROGRAM.as_bad
as_data_size = PROGRAM.as_data_size
as_head = PROGRAM.as_head
as_hms = PROGRAM.as_hms
as_warn = PROGRAM.as_warn
as_written = PROGRAM.as_written
cache_folder = PROGRAM.cache_folder
channel_text = PROGRAM.channel_text
clean_old_files = PROGRAM.clean_old_files
clipping_facts = PROGRAM.clipping_facts
clocks_apart = PROGRAM.clocks_apart
decode_audio = PROGRAM.decode_audio
ffprobe_json = PROGRAM.ffprobe_json
file_timecode = PROGRAM.file_timecode
group_recording_parts = PROGRAM.group_recording_parts
json = PROGRAM.json
log_curve_from_atom = PROGRAM.log_curve_from_atom
math = PROGRAM.math
mov_colour_tags = PROGRAM.mov_colour_tags
number_text = PROGRAM.number_text
os = PROGRAM.os
parallel_map = PROGRAM.parallel_map
parse_time_point = PROGRAM.parse_time_point
path_key = PROGRAM.path_key
progress_from_line = PROGRAM.progress_from_line
show_progress = PROGRAM.show_progress
shutil = PROGRAM.shutil
stop_wanted = PROGRAM.stop_wanted
subprocess = PROGRAM.subprocess
sys = PROGRAM.sys
tempfile = PROGRAM.tempfile
textwrap = PROGRAM.textwrap
threading = PROGRAM.threading
time = PROGRAM.time
timecode_string = PROGRAM.timecode_string
unwrap_day = PROGRAM.unwrap_day
write_beside_then_move = PROGRAM.write_beside_then_move

# Six stand in a piece read after this one: read_preset in the
# processing (a circle: choose_preset there asks check_preset here),
# MATRIX_BT2020 in the project, caption_room, hint, label, speaks_as.

# Three are bent while the run goes on, and a copy taken here would
# answer with the run before: set_language rebinds LANG, and the window
# sets GUI_RUNNING and OUTPUT_SINK on the program object.

# numpy is the tenth: the program holds a stand-in until the first sum
# asks and binds the real module then, which a copy taken up here would
# never see. So this asks the program instead, the same way.
class LateNumpy:
    """Stands in for the program's numpy until a sum wants it."""

    def __getattr__(self, name):
        global np
        got = getattr(PROGRAM.np, name)
        np = PROGRAM.np
        return got


np = LateNumpy()


# Before the first long step: does the material fit together? A two
# hour run that fails at the end over a detail costs more than a minute
# of checking, and a wrong upload to auphonic.com costs credit on top.

# How much separation the 3:1 rule asks for: with the other microphone
# three times as far away as the speaker's own, the neighbouring voice
# is about 9.5 dB quieter -- 20*log10(3). Below that it combs the mix.
THREE_TO_ONE_DB = 9.5

class Finding(object):
    """One item from the preflight report.

    Four kinds, and the kind decides what happens next: "good" is only
    counted, "hint" appears in the report, "fixed" says the script fixed
    it itself, and "abort" stops the run unless --anyway is given.
    """

    def __init__(self, kind, field, text, advice="", file=""):
        self.kind = kind
        self.field = field
        self.text = text
        self.advice = advice
        # Which file the finding belongs to; empty means it arises from
        # comparing several. The interface hangs the mark on it.
        self.file = file
        # A file that does not take part is checked anyway -- a row with
        # no mark looks forgotten -- but its finding holds nothing up.
        self.set_aside = False

    def line(self, width=17):
        label = {"good": "", "hint": T('Note: '), "fixed": T('fixed: '),
                 "abort": T('Caution: ')}[self.kind]
        out = "    %-*s %s%s" % (width, self.field, label, self.text)
        return as_warn(out) if self.kind == "abort" else out


# What a cached measurement holds changes with the program. This number
# is part of the fingerprint: raising it makes every old measurement
# stale, and without it the window shows the old result for weeks.
MEASUREMENT_VERSION = 2


def _fingerprint(paths):
    """Return a fingerprint: version, language, path, size and mtime.

    A changed file gets a different fingerprint and is measured again.
    The language belongs in it because a stored finding holds its text
    ready-made, and a run in one language would else serve the other's.
    """
    if isinstance(paths, str):
        paths = [paths]
    parts = ["format %d %s" % (MEASUREMENT_VERSION, PROGRAM.LANG)]
    for x in sorted(paths):
        try:
            s = os.stat(x)
            parts.append("%s|%d|%d" % (os.path.abspath(x), s.st_size,
                                       int(s.st_mtime)))
        except OSError:
            parts.append("%s|?" % os.path.abspath(x))
    import hashlib
    return hashlib.sha1("\n".join(parts).encode("utf-8")).hexdigest()[:16]


def cache_path(fingerprint):
    """Return where a cached measurement lives, or None."""
    folder = cache_folder("preflight")
    return os.path.join(folder, fingerprint + ".json") if folder else None


def cache_read(fingerprint):
    """Read a cached measurement. None means: measure again."""
    file_path = cache_path(fingerprint)
    if not file_path or not os.path.exists(file_path):
        return None
    try:
        with open(file_path, encoding="utf-8") as f:
            d = json.load(f)
    except (ValueError, OSError):
        return None
    if d.get("version") != VERSION:
        return None            # a new version may check differently
    return d


def cache_write(fingerprint, content):
    """Store a measurement so the next run need not repeat it."""
    d = dict(content)
    d["version"] = VERSION
    d.setdefault("when", time.time())
    write_beside_then_move(
        cache_path(fingerprint),
        json.dumps(d, ensure_ascii=False).encode("utf-8"))


def clean_preflight_cache(days=30):
    """Discard stale measurements; once per run is enough.

    Every entry names the version that wrote it and is refused after an
    update, so without this the folder keeps a layer per release.
    """
    clean_old_files(cache_folder("preflight"), days)


def _findings_to_json(findings):
    return [{"kind": b.kind, "field": b.field, "text": b.text, "advice": b.advice,
             "file": b.file} for b in findings]


def _findings_from_json(raw):
    return [Finding(b["kind"], b["field"], b["text"], b.get("advice", ""),
                   b.get("file", "")) for b in (raw or [])]


def measure_cached(file_path, label, measure, fresh=False):
    """Measure *one* file, from the cache or freshly.

    Cached per file, not per selection: adding the fifth must not wait
    for the first four. Returns {"findings": [...], "data": {...}}, the
    data feeding the comparison across all files.
    """
    fingerprint = "%s_%s" % (label, _fingerprint(file_path))
    d = None if fresh else cache_read(fingerprint)
    if d is None:
        try:
            findings, data = measure(file_path)
        except Exception as e:
            findings = [Finding("hint", os.path.basename(file_path)[:24],
                              T('not readable: %s') % str(e)[:80])]
            data = {}
        d = {"findings": _findings_to_json(findings), "data": data}
        cache_write(fingerprint, d)
    findings = _findings_from_json(d.get("findings"))
    for b in findings:
        b.file = os.path.abspath(file_path)
    return findings, (d.get("data") or {})


def sample_frame_intervals(file_path, duration, spots=5, window_s=2.0):
    """Sample the intervals between frames at several points in the file.

    Returns one list of intervals in seconds per point. The *packets*
    are queried, not the frames: ffprobe decodes nothing for a packet,
    which on a 4K file is a blink against half a minute. In time windows
    rather than packet counts, because ffprobe resumes at the keyframe
    before a seek and 48 packets can lie before the spot.
    """
    if not duration or duration <= 0:
        points = [0.0]
    else:
        points = [duration * k / float(spots) for k in range(spots)]
    # All the points in one call: every call is a process, and one costs
    # 1.8 seconds on the Windows builder. 62 of them take two seconds
    # here and 126 there.
    reading = ",".join("%.3f%%+%.1f" % (t0, window_s) for t0 in points)
    try:
        p = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "packet=pts_time", "-of", "csv=p=0",
             "-read_intervals", reading, file_path],
            capture_output=True, timeout=60)
    except Exception:
        return []
    times = []
    for line in p.stdout.decode("utf-8", "replace").splitlines():
        line = line.strip().rstrip(",")
        if not line or line == "N/A":
            continue
        try:
            times.append(float(line))
        except ValueError:
            pass
    # Packets arrive in decoding order, which with H.264 B-frames is not
    # display order. Sort first, or the codec's picture structure reads
    # as a variable frame rate. Sorting orders the windows too.
    times.sort()
    out, window = [], []
    for a, b in zip(times, times[1:]):
        step = b - a
        if 0 < step < 0.25:
            window.append(step)
            continue
        if len(window) >= 8:
            out.append(window)
        window = []
    if len(window) >= 8:
        out.append(window)
    return out


def _rate_is_variable(window):
    """Report whether the frame timing varies, and how strongly.

    A single doubled interval means nothing: the sample cuts into a
    group of pictures, and the interval beside the missing frame is
    exactly twice as large. Counted as variable only: a noticeable share
    of intervals that are no whole multiple of the frame duration, or
    different frame durations at different points in the file.
    """
    if not window:
        return False, 0.0
    middles = []
    odd = total = 0
    for intervals in window:
        middle = sorted(intervals)[len(intervals) // 2]
        if middle <= 0:
            continue
        middles.append(middle)
        for d in intervals:
            multiple = d / middle
            if abs(multiple - round(multiple)) > 0.1:
                odd += 1
            total += 1
    if not middles or not total:
        return False, 0.0
    odd_share = odd / float(total)
    # A frame duration that wanders over the file is a variable rate.
    drift = (max(middles) - min(middles)) / min(middles) if len(middles) > 1\
        else 0.0
    return (odd_share > 0.05 or drift > 0.02,
            max(odd_share, drift))


def inspect_frame_rate(file_path):
    """Report whether the frame rate is fixed or variable, and what it costs.

    Two questions, two routes: *whether* the intervals vary is what the
    sample shows, *how far* the file is off over its length is in the
    container. An even deviation -- the file says 30, it is constantly
    29.98 -- is clock drift and is compensated during alignment. Only
    *uneven* timing cannot be: the average fits the ends, not the middle.
    """
    d = ffprobe_json(file_path)
    v = next((s for s in d.get("streams", [])
              if s.get("codec_type") == "video"), None)
    if v is None:
        return None

    def rate(field):
        try:
            num, the_one = (float(x) for x in str(v.get(field) or "0/0").split("/"))
            return num / the_one if the_one else 0.0
        except Exception:
            return 0.0

    label_text = rate("r_frame_rate") or rate("avg_frame_rate")
    duration = float(d.get("format", {}).get("duration")
                  or v.get("duration") or 0.0)
    try:
        videos = int(v.get("nb_frames") or 0)
    except ValueError:
        videos = 0
    mean = (videos / duration) if (videos and duration) else rate("avg_frame_rate")
    window = sample_frame_intervals(file_path, duration)
    varies, spread = _rate_is_variable(window)
    # How far does the file drift by the end when a program plays it at the
    # nominal rate?
    offset = (duration - videos / label_text) if (videos and label_text) else 0.0
    return {"path": file_path, "nominal": label_text, "mean": mean, "duration": duration,
            "videos": videos, "varies": varies, "spread": spread,
            "offset_s": offset, "codec": v.get("codec_name"),
            "width": v.get("width"), "height": v.get("height"),
            "gaps": sum(len(x) for x in window)}


def check_camera_file(file_path):
    """Report what the preflight has to say about *one* camera.

    Returns (findings, data), the data being what the comparison across
    cameras needs, so no file is touched a second time.
    """
    name = os.path.basename(file_path)
    b = inspect_frame_rate(file_path)
    if not b:
        return [Finding("hint", name[:24], T('no video track'))], {}
    out = [Finding("good", name[:24], T('%s fps -- %s, %dx%d, %s frames in %s')
                   % (number_text(b["nominal"], 3),
                      b["codec"] or "?", b["width"] or 0, b["height"] or 0,
                      number_text(b["videos"], 0),
                      as_hms(b["duration"])))]
    # A few frames between frame count times nominal rate and the track
    # duration are on every camera and mean nothing -- alignment measures
    # the camera audio. A whole second is a statement.
    noticeable = abs(b["offset_s"]) > 1.0
    if b["varies"]:
        out.append(Finding(
            "hint", "",
            T('Frame spacing varies by %s %% -- the frame timing is uneven.')
            % number_text(100 * b["spread"], 0),
            T('Uneven frame timing cannot be evened out through the '
              'audio. If the sample points spread during alignment as '
              'well, convert to a fixed frame rate.')))
    elif noticeable:
        # Which way round it runs decides both sentences: as an amount,
        # slower than the label reads as faster and both are wrong.
        quicker = b["offset_s"] < 0
        spare = abs(b["offset_s"]) * b["nominal"]
        out.append(Finding(
            "hint", "",
            (T('%s fps, not the %s in the file -- %s more frames in '
               'the same length.') if quicker else
             T('%s fps, not the %s in the file -- %s fewer frames in '
               'the same length.'))
            % (number_text(b["mean"], 4),
               number_text(b["nominal"], 3),
               number_text(spare, 0)),
            (T('The frames stand a little shorter; the file is not any '
               'longer for it. Editing software leaves out about one '
               'frame every %s s, and picture and camera audio stay '
               'together.') if quicker else
             T('The frames stand a little longer; the file is not any '
               'shorter for it. Editing software repeats about one '
               'frame every %s s, and picture and camera audio stay '
               'together.'))
            % number_text(b["duration"] / max(1.0, spare), 0)))
    return out, {"name": name, "nominal": b["nominal"], "mean": b["mean"],
                  "duration": b["duration"], "width": b["width"],
                  "height": b["height"], "path": os.path.abspath(file_path),
                  "tc": file_timecode(file_path), "colour": list(mov_colour_tags(file_path) or ()),
                  "logs": log_curve_from_atom(_logs_atom_text(file_path))}


def compare_cameras(data):
    """What only shows when several cameras are compared."""
    out = []
    different = sorted({round(d["nominal"], 3) for d in data if d.get("nominal")})
    if len(different) > 1:
        out.append(Finding(
            "hint", T('Frame rates'),
            T('the video files run at different rates: %s')
            % ", ".join(number_text(r, 3) for r in different),
            T('The Timeline gets one fixed rate -- the highest of them, '
              'or the next rate Resolve has above it. It converts the '
              'others; with 23.976 against 24 that is where its audio '
              'analysis tends to stall.')))
    # With Apple the recording curve is in the logs atom, not the colr
    # box: where it is there, nothing is guessed and nothing reported.
    curves = {}
    for d in data:
        if d.get("logs"):
            curves.setdefault(d["logs"], []).append(d.get("name") or "?")
    # Curve and primaries unset: said once for all, being a property of
    # the camera and not of the recording.
    without_colour = [d for d in data
                  if not d.get("logs")
                  and len(d.get("colour") or ()) >= 2
                  and d["colour"][0] == 2 and d["colour"][1] == 2]
    if without_colour:
        matrix = {d["colour"][2] for d in without_colour if len(d["colour"]) > 2}
        out.append(Finding(
            "hint", T('Colour space'),
            T('%s of %s video files carry no curve and no colour space in '
              'the colr box%s -- probably log material.')
            % (number_text(len(without_colour), 0), number_text(len(data), 0),
               T(' -- only the matrix says BT.2020')
               if matrix == {PROGRAM.MATRIX_BT2020} else ""),
            T('Used as it stands -- nothing is invented. Check in Resolve '
              'under Clip Attributes, tab Color Space: if it says '
              '"Project" there, the input colour space was not recognised '
              'and has to be set by hand.')))
    # Differing curves are worth a message; the same one everywhere is
    # already in the colour line of every file.
    if len(curves) > 1:
        out.append(Finding(
            "hint", T('Capture curve'),
            T('the video files carry different recording curves: %s')
            # One per line, or three camera names in a row run past the
            # end of the column and the file name is what is cut off.
            % "\n      ".join(T('%s in %s') % (k, ", ".join(v))
                              for k, v in sorted(curves.items())),
            T('It is in the logs atom of the picture description -- that '
              'is how Resolve recognises the input colour space. Different '
              'curves mean different input colour spaces.')))
    # Differently tagged cameras need different input colour spaces in
    # Resolve, which otherwise shows once one looks unlike the other.
    # Where the logs atom says the same for all, Resolve goes by that.
    tags = {}
    for d in data:
        f = d.get("colour") or ()
        if len(f) >= 3:
            tags.setdefault("%d/%d/%d" % tuple(f[:3]),
                                 []).append(d.get("name") or "?")
    every_having_curve = (len(curves) == 1
                      and sum(len(v) for v in curves.values()) == len(data))
    if len(tags) > 1 and not every_having_curve:
        out.append(Finding(
            "hint", T('Colour tag'),
            T('the video files are tagged differently: %s')
            # One tag per line, as with the curves above: two of them
            # in a row are cut off inside the first camera's name.
            % "\n      ".join(T('%s in %s') % (k, ", ".join(v))
                              for k, v in sorted(tags.items())),
            T('The three numbers are primaries, curve and matrix. '
              'Different tags need different input colour spaces in '
              'Resolve -- otherwise one camera looks unlike the other.')))
    sizes = sorted({(d.get("width"), d.get("height")) for d in data
                       if d.get("width")})
    if len(sizes) > 1:
        out.append(Finding(
            "hint", T('Resolutions'),
            T('the video files have different picture sizes: %s')
            % ", ".join("%dx%d" % g for g in sizes),
            T('Resolve scales to the Timeline resolution. Anything smaller '
              'is scaled up and gets softer.')))
    return out


def find_camera_gaps(video_paths):
    """Find cameras that stopped in between.

    Numbered blocks belong together only if the next starts where the
    one before ends. A gap means the camera stopped, and a piece of
    picture is missing exactly where the audio keeps running.
    """
    groups = {}
    for p in video_paths:
        name, _ = os.path.splitext(os.path.basename(p))
        m = TRAILING_NUMBER.match(name)
        if not m:
            continue
        groups.setdefault(m.group(1), []).append((int(m.group(2)), p))
    out = []
    for stem, parts in sorted(groups.items()):
        if len(parts) < 2:
            continue
        parts.sort()
        for (n1, p1), (n2, p2) in zip(parts, parts[1:]):
            t1, t2 = file_timecode(p1), file_timecode(p2)
            if t1 is None or t2 is None:
                out.append(Finding(
                    "hint", stem[:17],
                    T('multi-part, no timecode -- gaps in between cannot '
                      'be detected.'), "",
                    os.path.abspath(p2)))
                break
            try:
                d1 = float(ffprobe_json(p1).get("format", {}).get("duration") or 0.0)
            except Exception:
                d1 = 0.0
            gap = unwrap_day(t2, t1 + d1) - (t1 + d1)
            if gap > 0.5:
                out.append(Finding(
                    "hint", stem[:17],
                    T('Gap of %s between block %d and %d -- the camera '
                      'stopped.') % (as_hms(gap), n1, n2),
                    T('The cut has no picture there. When the Timeline is '
                      'built the spot stays empty, the audio runs on.'),
                    os.path.abspath(p2)))
    return out


def check_audio_file(file_path):
    """Report sample rate, bit depth, channels and length of one recording."""
    name = os.path.basename(file_path)
    d = ffprobe_json(file_path)
    a = next((s for s in d.get("streams", [])
              if s.get("codec_type") == "audio"), {})
    rate = int(a.get("sample_rate") or 0)
    channels = int(a.get("channels") or 0)
    depth = a.get("bits_per_raw_sample") or a.get("bits_per_sample") or "?"
    if str(a.get("sample_fmt", "")).startswith("flt"):
        depth = "32f"
    duration = float(d.get("format", {}).get("duration") or 0.0)
    out = [Finding("good", name[:24], "%s kHz, %s bit, %s, %s"
                   % (number_text(rate / 1000.0, None), depth,
                      channel_text(channels),
                      as_hms(duration)))]
    if rate and rate != SR:
        out.append(Finding(
            "fixed", "",
            T('%s kHz instead of %s kHz -- converted during processing.')
            % (number_text(rate / 1000.0, None),
               number_text(SR / 1000.0, None))))
    if channels > 2:
        out.append(Finding(
            "good", "",
            T('%s channels -- cut into tracks, see the rows above.')
            % number_text(channels, 0),
            T('Every pair of channels is judged on its own: one stereo '
              'track, or two microphones and therefore two tracks. Silent '
              'inputs drop out. The rows under the file say what was '
              'measured, and the tick overrules it.')))
    # Otherwise invisible: the master is measured as a sum and a limiter
    # pulls it under -1 dBTP, so a microphone against the stop all
    # evening looks clean. A hint, never a stop.
    for channel, facts_ in sorted(clipping_facts(file_path).items()):
        runs, longest, milliseconds, first = facts_
        out.append(Finding(
            "hint", "",
            T('Channel %d is against the stop: %s times three samples or '
              'more in a row, the longest %s (%s ms), the first at %s.')
            % (channel + 1, number_text(runs, 0), number_text(longest, 0),
               number_text(milliseconds), as_hms(first)),
            T('Counted here, sample by sample, at the rate the file was '
              'recorded at: a run of three or more samples on the highest '
              'value an integer format can hold. One or two are rounding '
              'and are not reported. What is cut off there is gone and no '
              'processing brings it back -- but the recording is still the '
              'recording, and this holds nothing up. Only integer formats '
              'are counted. 32 bit float has no stop at full scale, so '
              'there is nothing there to count.'),
            os.path.abspath(file_path)))
    return out, {"name": name, "duration": duration, "rate": rate,
                  "channel_count": channels, "path": os.path.abspath(file_path),
                  "tc": file_timecode(file_path)}


def by_recording(audio_data, chains):
    """Turn per-block data into per-recording data.

    A block is not a recording: several in a row make one long one.
    Recordings are compared, or every block counts as too short.
    """
    after_file_path = ByFile((d.get("path"), d)
                            for d in audio_data if d.get("path"))
    out = []
    for row, _rest in chains:
        parts = [after_file_path[x] for x in row
                 if x in after_file_path]
        if not parts:
            continue
        head = dict(parts[0])
        head["duration"] = sum(t.get("duration") or 0.0 for t in parts)
        if len(parts) > 1:
            head["name"] = "%s +%d" % (head.get("name") or "?",
                                       len(parts) - 1)
        out.append(head)
    return out


def compare_audio_tracks(data):
    """Find tracks that stand out against the others."""
    lengths = [(d.get("name") or "?", d.get("duration") or 0.0,
                d.get("path") or "") for d in data]
    if len(lengths) < 2:
        return []
    longer = max(d for _, d, _p in lengths)
    out = []
    for name, d, file_path in lengths:
        if longer > 0 and d < 0.5 * longer:
            out.append(Finding(
                "hint", name[:17],
                T('only %s long, the longest recording has %s.')
                % (as_hms(d), as_hms(longer)),
                T('Started late or stopped early -- this voice is then '
                  'missing from the mix in places.'), file_path))
    return out


def timecode_comparison(data):
    """Find files whose timecode belongs to an entirely different time.

    Material from one recording runs at the same time, so the windows
    overlap; a file overlapping none of the others had an unset clock.
    The rule itself is clocks_apart and only there: what is decided here
    also decides the zero point of the cut, and the two must not
    disagree about one clock.
    """
    rows = [d for d in data if d.get("tc") is not None]
    apart, moved, placed = clocks_apart(
        [(d["tc"], max(1.0, d.get("duration") or 0.0), i)
         for i, d in enumerate(rows)])
    out = []
    if moved:
        out.append(Finding(
            "hint", T('Midnight'),
            T('%s carries a timecode from the other side of midnight -- '
              'counted as one night, not as a day apart.')
            % ", ".join(sorted(rows[i].get("name") or "?"
                               for i in moved)[:3]),
            T('A timecode counts from midnight and starts over there. '
              'The files are put on one axis before anything is '
              'subtracted, otherwise the recording after midnight looks '
              'almost a day away from the one before. If these really '
              'were recorded on different days, the alignment is wrong '
              'and the measured offset is the one to trust.')))
    for a0, _n, i in placed:
        if i not in apart:
            continue
        # Each value goes back into a timecode at its own file's rate:
        # printing a 25 fps camera at 30 moves it by two frames.
        other = sorted((b0, j) for b0, _m, j in placed if j != i)
        middle, other_row = other[len(other) // 2]
        out.append(Finding(
            "hint", (rows[i].get("name") or "?")[:17],
            T('Timecode %s, the other files are at %s -- this clock was '
              'not set.')
            % (timecode_string(a0, rows[i].get("nominal") or 30.0),
               timecode_string(middle, rows[other_row].get("nominal") or 30.0)),
            T('Alignment goes by the measured offset; the timecode is only '
              'the cross-check.'), rows[i].get("path") or ""))
    return out


# How far into a recording the bleed windows may reach before reading
# the whole thing once beats seeking into it five times. Five minutes
# at 16 kHz mono is 19 MB, a two-hour interview 460.
WHOLE_READ_S = 300.0


def crosstalk_apart(audio_paths, rate=16000, window=5, long=20.0,
                    min_len_long=4.0):
    """Measure how loudly each voice appears in the others' microphones.

    A few windows over the shared time, not the whole recording, which
    would be too slow for a preflight. Returns ([(who, in whose
    microphone, dB), ...], plus why not. Two readers: the preflight
    makes sentences of it, the separation asks whether the tracks tell.
    """
    if len(audio_paths) < 2:
        return [], ""
    starts = [file_timecode(p) for p in audio_paths]
    takes = []
    for p in audio_paths:
        try:
            takes.append(float(ffprobe_json(p).get("format", {})
                                .get("duration") or 0.0))
        except Exception:
            takes.append(0.0)
    if all(s is not None for s in starts):
        # Shared absolute time: measure only where all of them run.
        t0 = max(starts)
        t1 = min(s + d for s, d in zip(starts, takes))
        # With short material use smaller windows rather than giving up.
        long = max(min_len_long, min(long, (t1 - t0) / (window + 1.0)))
        if t1 - t0 < 2 * long:
            return [], T('the recordings overlap only %s -- too little '
                         'to measure.') % as_hms(max(0.0, t1 - t0))
        points = [t0 + (t1 - t0 - long) * k / float(max(1, window - 1))
                  for k in range(window)]
        offset = [[p - s for s in starts] for p in points]
    else:
        shortest = min(d for d in takes if d) if any(takes) else 0.0
        long = max(min_len_long, min(long, shortest / (window + 1.0)))
        if shortest < 2 * long:
            return [], T('the shortest recording has only %s -- too '
                         'little to measure.') % as_hms(shortest)
        points = [(shortest - long) * k / float(max(1, window - 1))
                  for k in range(window)]
        offset = [[p] * len(audio_paths) for p in points]
    data = []
    for i, p in enumerate(audio_paths):
        pieces = []
        # Five windows out of a 34-second recording is the whole file
        # read in five processes. Where they reach no further than a
        # few minutes in it is read once and cut up here.
        reach = max(max(0.0, row[i]) for row in offset) + long
        if reach <= WHOLE_READ_S:
            try:
                whole = decode_audio(p, rate=rate)
                for row in offset:
                    at = int(max(0.0, row[i]) * rate)
                    piece = whole[at:at + int(long * rate)]
                    if len(piece):
                        pieces.append(piece)
            except Exception:
                pieces = []
        for row in (offset if not pieces else ()):
            try:
                pieces.append(decode_audio(p, rate=rate, ss=max(0.0, row[i]),
                                          duration=long))
            except Exception:
                pass
        if not pieces:
            return [], T('not measurable.')
        data.append(np.concatenate(pieces))
    short = min(len(x) for x in data)
    data = [np.asarray(x[:short], dtype=np.float64) for x in data]
    level, speech = _block_levels(data, rate)
    rows = []
    for i in range(len(data)):
        for j in range(len(data)):
            if i == j:
                continue
            blocks = _windows_for_pair(level, speech, i, j, at_most=30)
            if len(blocks) < 3:
                continue
            own_flag = float(np.median([level[i][b] for b in blocks]))
            others = float(np.median([level[j][b] for b in blocks]))
            if own_flag <= 0 or others <= 0:
                continue
            rows.append((i, j, 20.0 * math.log10(own_flag / others)))
    return rows, ""


def microphones_apart_db(audio_paths):
    """How far the closest pair of these microphones stands apart, in dB.

    The worst of every recording against every other, both ways round;
    None where it could not be measured. The separation asks it before
    trusting the tracks to say who is speaking.
    """
    try:
        rows, _why = crosstalk_apart(audio_paths)
    except Exception:
        return None
    return min((db for _i, _j, db in rows), default=None)


def check_crosstalk(audio_paths, rate=16000, window=5, long=20.0,
                    min_len_long=4.0):
    """Say in words how much of each voice sits in the other microphones.

    The yardstick is the 3:1 rule: with the other microphone three times
    as far from the speaker as their own, the neighbouring voice is
    about 9.5 dB quieter. A statement about the *room* and about nothing
    afterwards; it can only be changed next time.
    """
    if len(audio_paths) < 2:
        return []
    rows, why = crosstalk_apart(audio_paths, rate, window, long,
                                min_len_long)
    if why:
        return [Finding("hint", T('Bleed'), why)]
    names = [os.path.splitext(os.path.basename(p))[0][:28] for p in audio_paths]
    out, bad = [], 0
    for i, j, separation in rows:
        good = separation >= THREE_TO_ONE_DB
        if not good:
            bad += 1
        out.append(Finding(
            "good" if good else "hint", T('Bleed'),
            T("%s%s in %s's microphone only %s dB quieter")
            % ("" if good else T('Limits the de-bleed: '),
               names[i], names[j], number_text(separation, 1))
            if not good else
            T("%s in %s's microphone: %s dB quieter than in their own.")
            % (names[i], names[j], number_text(separation, 1)),
            "" if good else
            T('It arose during the recording and cannot be changed '
              'now. The less the microphones are separated, the more '
              'cautiously De-Bleed at auphonic.com can work. Next '
              'time: three times as far from the neighbouring '
              'microphone as from your own mouth, then the '
              'neighbouring voice sits about %s dB lower.')
            % number_text(THREE_TO_ONE_DB, 1),
            os.path.abspath(audio_paths[j])))
    if not out:
        return [Finding("hint", T('Bleed'),
                       T('no place found where exactly one person speaks '
                         '-- the separation cannot be measured.'))]
    if bad:
        out.append(Finding(
            "hint", T('3:1 rule'),
            T('%s of %s comparisons are below %s dB -- every recording '
              'against every other, in both directions.')
            % (number_text(bad, 0), number_text(len(out), 0),
               number_text(THREE_TO_ONE_DB, 1)),
            T('This comes from the recording, not afterwards: the '
              'microphones sit too close together or too far from the '
              'mouth.')))
    return out


# What the room has to be over the estimate before the run is called
# safe: a rough estimate passed by one per cent is not a pass -- 1.1 GB
# of 96.6 spare, and the run dies at 88 per cent.
SPACE_MARGIN = 1.15


def on_one_disk(one, other):
    """Whether two folders live on the same disk.

    Unknown counts as no: a wrong yes would double an estimate that is
    already erring upward, and refuse a run that would have fitted.
    """
    try:
        return os.stat(one).st_dev == os.stat(other).st_dev
    except Exception:
        return False


def window_between(in_point, out_point, fps=30.0):
    """How long the delivered cameras are, out of In point and Out point.

    Only where both are given and count the same way is the length known
    before the axis is measured; one point alone answers None.
    """
    begin, begin_abs = parse_time_point(in_point or "", fps)
    end, end_abs = parse_time_point(out_point or "", fps)
    if begin is None or end is None or begin_abs != end_abs or end <= begin:
        return None
    return end - begin


def window_from_points(args, fps=30.0):
    """The same length, out of the In point and Out point of a call."""
    return window_between(getattr(args, "in_point", None),
                          getattr(args, "out_point", None), fps)


def space_needed_mb(audio_paths, video_paths, multitrack, window_s=None):
    """What a run writes, and how much of that goes to the temp folder too.

    Erring upward: every camera is copied and gets audio tracks added,
    plus the processed tracks and the mix. With a window each camera
    shrinks by its own share, not by the longest one's. In megabytes.
    """
    video_mb, delivered = 0.0, 0.0
    for p in video_paths:
        try:
            running = float((ffprobe_json(p).get("format")
                             or {}).get("duration") or 0.0)
        except Exception:
            running = 0.0
        share = 1.0
        if window_s and running > 0:
            share = min(1.0, (window_s + 4 * CAMERA_MARGIN_S) / running)
        delivered = max(delivered, running * share)
        video_mb += os.path.getsize(p) / 1e6 * share
    audio_mb = sum(os.path.getsize(p) for p in audio_paths) / 1e6
    # The picture is copied unchanged; the audio grows the file and is
    # written uncompressed: 48 kHz, 24 bit, two channels are 0.29 MB per
    # second and per track. The given audio files are no measure of it.
    per_second = 48000 * 3 * 2 / 1e6
    if multitrack:
        # Every camera carries its own mix, its speakers, the overall mix
        # and the camera original. Two plus the speakers is the upper end.
        per_camera = 2 + (len(audio_paths) or 1)
    else:
        per_camera = 2
    added = delivered * per_second * per_camera * max(1, len(video_paths))
    # The processed tracks come back and are mixed once more.
    return (video_mb * 1.05 + added
            + audio_mb * (3.0 if multitrack else 2.0)), added


def space_summary_lines(target, audio_paths, video_paths, multitrack,
                        in_point="", out_point=""):
    """What the run writes and what is free, for the summary before it.

    The preflight's own reckoning, so the two numbers agree and a time
    window shortens both. Only what lands in the target folder counts;
    where the disk cannot be read, only the target is named.
    """
    where = target or T('the source folder')
    try:
        needed, _temporary = space_needed_mb(
            audio_paths, video_paths, multitrack,
            window_between(in_point, out_point))
        free = shutil.disk_usage(target or ".").free / 1e6
    except Exception:
        return [T('Target: %s') % where]
    return [TN(len(video_paths),
               'This makes %s video file, about %s. Target: %s',
               'This makes %s video files, about %s. Target: %s')
            % (number_text(len(video_paths), 0), as_data_size(needed), where),
            T('Free space there: %s') % as_data_size(free)]


def check_disk_space(target_folder, audio_paths, video_paths, multitrack,
                        window_s=None):
    """Report whether there is enough disk space for what will be created.

    Rough but erring upward, so a run stops before it starts rather than
    halfway. *window_s* shortens the cameras and the estimate follows
    it, generously, or a run that fits is refused.
    """
    folder = target_folder or (os.path.dirname(os.path.abspath(video_paths[0]))
                            if video_paths else os.getcwd())
    while folder and not os.path.isdir(folder):
        fresh = os.path.dirname(folder)
        if fresh == folder:
            break
        folder = fresh
    try:
        free = shutil.disk_usage(folder or ".").free / 1e6
    except Exception:
        return []
    needed, added = space_needed_mb(audio_paths, video_paths, multitrack,
                                    window_s)
    # The temporary files go to the system temp folder, and on the same
    # disk as the output they eat the same space twice.
    if on_one_disk(tempfile.gettempdir(), folder or "."):
        needed += added
    # "hint", not "abort": the numbers fit and the estimate errs upward,
    # so refusing would be wrong. But a rough estimate cleared by one
    # per cent is not room enough -- such a run dies at 88 per cent.
    kind = ("abort" if free < needed
            else "hint" if free < needed * SPACE_MARGIN else "good")
    advice = ""
    if kind == "abort":
        advice = (T('About %s missing. Free up space or choose another folder '
                 'with --out. The temporary files during the run go '
                 'somewhere else again, into the system temp folder.')
               % as_data_size(needed - free))
    elif kind == "hint":
        advice = T('The estimate is rough, so this is not room enough. Free '
                   'up space or choose another folder with --out.')
    return [Finding(kind, T('Disk space'),
                   T('free %s, about %s needed (%s)')
                   % (as_data_size(free), as_data_size(needed), folder), advice)]


# What the platforms expect: -16 LUFS for stereo and -19 for mono in
# the podcast directories, and YouTube turns down to -14, never up.
PLATFORMS = {
    "podcast": (-16.0, 'Podcast directories, stereo'),
    "podcast-mono": (-19.0, 'Podcast directories, mono'),
    "youtube": (-14.0, 'YouTube -- turns down only, never up'),
    "broadcast": (-23.0, 'EBU R128, broadcast'),
}


def loudness_choices():
    """The loudness targets to pick from: (value, caption).

    The caption carries the number and, in brackets, what it is the
    standard for: the number alone says nothing to anybody who has not
    learnt the four by heart. None is the fifth answer and not a fifth
    number -- nothing of ours adjusts. The caption goes through
    as_written, its minus sign being the difference between -16 and 16.
    """
    out = [(target, as_written("%.0f LUFS (%s)" % (target, T(what_for))))
           for target, what_for in PLATFORMS.values()]
    out.append((None, T('Take from source files')))
    return out


def loudness_answer_file():
    """Where the loudness last chosen in the window is kept."""
    folder = cache_folder()
    return os.path.join(folder, "loudness_target") if folder else ""


def loudness_last():
    """The loudness last chosen in the window; -16 LUFS if never chosen.

    One small file in the cache folder, the way the answer about updates
    is kept, so whoever delivers to the same place every week need not
    pick the same entry every week. A project file's own value beats it:
    what was saved with a production belongs to that production.
    """
    where = loudness_answer_file()
    if not where or not os.path.exists(where):
        return -16.0
    try:
        with open(where, encoding="utf-8") as f:
            text = f.read().strip()
    except OSError:
        return -16.0
    if text == "source":
        return None
    try:
        return float(text)
    except ValueError:
        return -16.0


def loudness_last_set(value):
    """Remember the choice, so it holds for the next new project.

    Returns whether it could be written. Nothing is lost where it
    cannot: the value is in the window and in the project file.
    """
    where = loudness_answer_file()
    if not where:
        return False
    try:
        with open(where, "w", encoding="utf-8") as f:
            f.write("source" if value is None else "%g" % value)
    except OSError:
        return False
    return True


def loudness_field_build(into, value):
    """Build the loudness row of the Production box.

    Out here for the reason cut_fields_build gives: the window is long
    enough without another stretch of widget assembly. In the Production
    box and not behind "Settings ...": it is a property of this episode
    the way the name and the output folder are, and whoever delivers
    somewhere else next month has to trip over it, not go looking.
    """
    from PySide6 import QtWidgets as _qw
    row = _qw.QHBoxLayout()
    into.addLayout(row)
    row.addWidget(PROGRAM.label(T('Loudness')))
    box = _qw.QComboBox()
    for target, caption in loudness_choices():
        box.addItem(caption, target)
    box.setMinimumWidth(PROGRAM.caption_room(
        box, 300, [c for _v, c in loudness_choices()]))

    def row_of(want):
        """Which row carries *want*, or -1.

        Compared as a number, not as an object: one of the two being an
        int would put the list on the wrong row.
        """
        for i in range(box.count()):
            here = box.itemData(i)
            if here is None and want is None:
                return i
            if here is not None and want is not None \
                    and abs(here - want) < 0.05:
                return i
        return -1

    def show():
        """Put the stored value onto the list."""
        i = row_of(value.get())
        if i < 0:
            # A value nobody can pick here, out of a project file or a
            # run with its own --lufs. Added rather than replaced:
            # opening a project must not change what it was set to.
            box.addItem("%.0f LUFS" % value.get(), value.get())
            i = box.count() - 1
        if box.currentIndex() != i:
            box.setCurrentIndex(i)

    def chosen(*_):
        """The list changed: remember it for the next new project."""
        value.set(box.currentData())
        loudness_last_set(box.currentData())

    box.currentIndexChanged.connect(chosen)
    value.listen(lambda *_: show())
    show()
    PROGRAM.speaks_as(box, T('Loudness of the finished episode'))
    # The name of the last entry stands inside the sentence rather than
    # in a slot: in German it carries an article, and a piece cannot
    # settle its own case before it knows the slot.
    row.addWidget(PROGRAM.hint(
        box,
        T('How loud the finished episode is made. The same gain goes on '
          'every\ntrack, so the balance between the speakers is kept.\n'
          '"Take from source files" adjusts nothing at all: auphonic.com '
          'goes\non doing what its preset says, and without auphonic.com '
          'the sound\nstays as it is in the source files.')))
    row.addStretch(1)
    return box


def lufs_does_nothing(args, videos):
    """Whether --lufs changes anything on the path this run takes.

    Several voices and no picture: the tracks leave as recorded, a gain
    per track being what would put the voices out of balance, and that
    balance is what the path exists to keep. The number still travels to
    auphonic.com, which masters the mix, so a key puts it back in force.
    """
    return (not videos and bool(getattr(args, "multitrack", False))
            and getattr(args, "lufs", None) is not None
            and not getattr(args, "auphonic_key", None))


def check_loudness_target(args, videos=()):
    """Report the loudness target in force. It only reports.

    It sets nothing: a check that quietly changes what it is checking
    lets the report and the run come apart. Where the number does
    nothing the report says so, or the log names a target that is
    contradicted further down.
    """
    if getattr(args, "lufs", None) is None:
        return [Finding("good", T('Loudness'),
                       T('taken from the source files, no --lufs given -- '
                         'nothing is adjusted'))]
    near = [n for n, (lufs, _) in PLATFORMS.items() if abs(lufs - args.lufs) < 0.05]
    text = "%.0f LUFS%s" % (args.lufs,
                            "  (%s)" % T(PLATFORMS[near[0]][1]) if near else "")
    if lufs_does_nothing(args, videos):
        return [Finding("good", T('Loudness'),
                       T('%s is set, and nothing is adjusted here: the '
                         'tracks leave as they were recorded, and the '
                         'loudness is set where they are mixed.') % text)]
    return [Finding("good", T('Loudness'), text)]


def check_preset(key, uuid, presetname, lufs, multitrack):
    """Check the chosen preset against what the run needs.

    Uploading costs credit and time, so what would be wrong afterwards has
    to surface first. The preset is read out rather than trusted by name.
    """
    try:
        p = PROGRAM.read_preset(key, uuid)
    except Exception as e:
        return [Finding("hint", T('Preset'),
                       T('not readable (%s) -- unchecked.') % str(e)[:60])]
    alg = dict(p.get("algorithms") or {})
    out = [Finding("good", T('Preset'), "%s" % presetname)]
    switched_on = sorted("%s=%s" % (k, v) for k, v in alg.items()
                if v not in (False, None, "", 0))
    out.append(Finding("good", T('Algorithms'),
                       ", ".join(switched_on)[:300] or T('none switched on')))
    target = alg.get("loudnesstarget")
    try:
        target = float(target) if target is not None else None
    except (TypeError, ValueError):
        target = None
    if lufs is None:
        # Nothing of ours adjusts, so there is nothing to compare the
        # preset against: what it masters to is what comes out. Said,
        # not complained about.
        if target is not None:
            out.append(Finding(
                "good", T('Loudness'),
                T('the preset masters to %s LUFS -- that stands, nothing '
                  'of ours adjusts.') % number_text(target, 0)))
    elif target is not None and abs(target - float(lufs)) > 0.05:
        out.append(Finding(
            "abort", T('Loudness'),
            T('the preset masters to %s LUFS, the calculation uses %s.')
            % (number_text(target, 0), number_text(lufs, 0)),
            T('Both at once does not work: the returning tracks would go '
              'to one value, our own mix to the other. Either set --lufs '
              '%.0f or change the preset.')
            % target))
    if multitrack:
        template = p.get("multi_input_files") or []
        if not template:
            out.append(Finding(
                "abort", T('Track template'),
                T('the Multitrack preset has no track stored.'),
                T('The first preset track sets the settings for all our '
                  'tracks. Otherwise they come back unprocessed. Create a '
                  'track in the preset in the web interface.')))
        else:
            track_alg = dict((template[0].get("algorithms") or {}))
            switched_on = sorted("%s=%s" % (k, v) for k, v in track_alg.items()
                        if v not in (False, None, "", 0))
            out.append(Finding("good", T('per track'),
                               ", ".join(switched_on)[:300] or T('none switched on')))
            if not switched_on:
                out.append(Finding(
                    "hint", "",
                    T('the track template has nothing switched on -- the '
                      'tracks would come back exactly as uploaded.')))
    return out


def report_findings(findings, heading, anyway=False):
    """Print the report. Returns True when the run should be aborted."""
    if not findings:
        return False
    print(as_head(T('\nPREFLIGHT -- %s') % heading))
    for b in findings:
        print(b.line())
        # In the window the finding stands on its file and the advice
        # on the mark; the log has neither, so only the advice waits.
        if b.advice and not PROGRAM.GUI_RUNNING:
            for line in textwrap.wrap(b.advice, 70):
                print("      %s" % line)
    abort = [b for b in findings if b.kind == "abort"]
    hints = [b for b in findings if b.kind == "hint"]
    fixed = [b for b in findings if b.kind == "fixed"]
    parts = [T('%s checked') % number_text(len(findings), 0)]
    if fixed:
        parts.append(TN(len(fixed), '%s fixed on its own',
                        '%s fixed on their own') % number_text(len(fixed), 0))
    if hints:
        parts.append(TN(len(hints), '%s hint', '%s hints')
                     % number_text(len(hints), 0))
    if abort:
        parts.append(TN(len(abort), '%s reason to stop',
                        '%s reasons to stop') % number_text(len(abort), 0))
    print("    %s" % ", ".join(parts))
    if abort and not anyway:
        print(as_bad(T('\nStopped before the first long step. With --anyway '
                       'it runs regardless.')))
        return True
    if abort:
        print(T('    --anyway is set: it runs despite the points above.'))
    return False


def collect_findings(audio_paths, video_paths, fresh=False, crosstalk=True,
                    set_aside=(), apart=(), together=()):
    """Collect all findings about the material.

    Each file is measured and cached on its own, so adding one measures
    only that one; what shows in comparison comes off the cached data.
    *set_aside* are files that do not take part -- ignored ones, intro,
    outro. They are checked so their row is not the only one without a
    mark, and stay out of the comparisons.
    """
    set_aside = {path_key(x) for x in (set_aside or ())}

    def counts_not(findings_, file_path):
        if path_key(file_path) in set_aside:
            for b in findings_:
                b.set_aside = True
        return findings_

    findings, video_data, audio_data = [], [], []
    # All at once: each has its own cache entry and knows nothing of the
    # others, so there is nothing to wait for.
    for p, (b, d) in zip(video_paths, parallel_map(
            video_paths,
            lambda x: measure_cached(x, "video", check_camera_file, fresh))):
        findings += counts_not(b, p)
        if d and path_key(p) not in set_aside:
            video_data.append(d)
    findings += compare_cameras(video_data)
    having_video = [p for p in video_paths if path_key(p) not in set_aside]
    if having_video:
        findings += find_camera_gaps(having_video)
    for p, (b, d) in zip(audio_paths, parallel_map(
            audio_paths,
            lambda x: measure_cached(x, "audio", check_audio_file, fresh))):
        findings += counts_not(b, p)
        if d and path_key(p) not in set_aside:
            audio_data.append(d)
    # Comparisons work with recordings, not with blocks: two blocks of
    # one recording run in turn, are each shorter and never overlap.
    audio_paths = [p for p in audio_paths if path_key(p) not in set_aside]
    chains = (group_recording_parts(audio_paths, apart=apart,
                                    together=together)
              if audio_paths else [])
    recordings = by_recording(audio_data, chains)
    findings += compare_audio_tracks(recordings)
    findings += timecode_comparison(video_data + recordings)
    heads = [row[0] for row, _rest in chains]
    if crosstalk and len(heads) > 1:
        # Crosstalk is about the interplay, so it is cached per set.
        audio_paths = heads
        fingerprint = 'crosstalk_%s' % _fingerprint(audio_paths)
        d = None if fresh else cache_read(fingerprint)
        if d is None:
            try:
                found = check_crosstalk(audio_paths)
            except Exception as e:
                found = [Finding("hint", T('Bleed'),
                                   T('not measurable: %s') % str(e)[:80])]
            d = {"findings": _findings_to_json(found)}
            cache_write(fingerprint, d)
        findings += _findings_from_json(d.get("findings"))
    return findings


def run_preflight(args, audio_paths, video_paths):
    """Run the preflight report on the material. Returns 1 to abort.

    Called once for both modes, before the fork in main(). What needs
    several tracks falls away with one.
    """
    if getattr(args, "no_preflight", False):
        return 0
    findings = collect_findings(audio_paths, video_paths,
                              bool(getattr(args, "preflight_again", False)),
                              bool(getattr(args, "multitrack", False)),
                              apart=getattr(args, "apart", ()),
                              together=getattr(args, "together", ()))
    # These two depend on the call and the machine, not the material.
    findings += check_disk_space(getattr(args, "out", None), audio_paths, video_paths,
                             bool(getattr(args, "multitrack", False)),
                             window_from_points(args))
    findings += check_loudness_target(args, video_paths)
    return 1 if report_findings(findings, T('does the material fit together?'),
                               getattr(args, "anyway", False)) else 0


def run_ffmpeg_with_progress(cmd, duration, text):
    """Run ffmpeg and show its progress.

    Errors go to a file, not to a pipe: stdout is read to the end, and
    an unread stderr pipe fills up and stops ffmpeg in mid-run.
    """
    cmd = cmd[:1] + ["-nostats", "-progress", "pipe:1"] + cmd[1:]
    fd, log = tempfile.mkstemp(prefix="vpm_ff_", suffix=".txt")
    os.close(fd)
    try:
        with open(log, "wb") as fh:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=fh)
            # This is where a run spends its minutes, so this is where
            # breaking off has to reach. The window ends the child.
            RUN_STOP["children"].add(proc)
            try:
                show_progress(text, 0.0)
                for line in proc.stdout:
                    share = progress_from_line(line, duration)
                    if share is not None:
                        show_progress(text, share)
                proc.wait()
            finally:
                RUN_STOP["children"].discard(proc)
        if stop_wanted():
            # Ended by us, so the error it left behind says nothing.
            raise Stopped(RUN_STOP["at"] or text)
        show_progress(text, 1.0)
        if THREAD_SHARE.get(threading.get_ident()) is None:
            if PROGRAM.OUTPUT_SINK:
                PROGRAM.OUTPUT_SINK("\n")
            else:
                sys.stdout.write("\n")
        if proc.returncode:
            with open(log, "r", encoding="utf-8", errors="replace") as fh:
                raise RuntimeError(fh.read()[-2000:])
    finally:
        try:
            os.unlink(log)
        except OSError:
            pass
