# -*- coding: utf-8 -*-
"""The preflight: does the material fit together before the long run?

A piece of the program, read out of the folder beside it by beside().
It cannot import the file it was cut out of, because that file is
still being read while this one is; the program is handed in instead,
and every name this piece uses out of it is bound below, by name.
run_ffmpeg_with_progress at the end is not checking: it is what the
long steps run ffmpeg through, and it stands under the same heading.
"""

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

# What the program has and this piece uses, bound once so that the
# checking reads as it did in the one file. Nine names are missing,
# and the three blocks under the list say which and why.

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
cache_folder = PROGRAM.cache_folder
channel_text = PROGRAM.channel_text
clean_old_files = PROGRAM.clean_old_files
clipping_facts = PROGRAM.clipping_facts
clocks_apart = PROGRAM.clocks_apart
decimal_text = PROGRAM.decimal_text
decode_audio = PROGRAM.decode_audio
ffprobe_json = PROGRAM.ffprobe_json
file_timecode = PROGRAM.file_timecode
group_recording_parts = PROGRAM.group_recording_parts
group_text = PROGRAM.group_text
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

# Six of the ten stand in a piece read after this one: read_preset in
# the processing -- a circle, because choose_preset over there asks
# check_preset here -- MATRIX_BT2020 in the project, and caption_room,
# hint, label and speaks_as in the window. All through PROGRAM.

# Three of the ten are bent while the run goes on, and a copy taken here
# would answer with the value of the run before: set_language rebinds
# LANG, and the window sets GUI_RUNNING and OUTPUT_SINK on the program
# object, which is a write the pieces are never told about.

# numpy is the tenth, and the one name here that the program has still
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


# =====================================================================
#  Preflight
#  ---------
#  Before the first long step begins: does the material fit together?
#  A two hour run that fails at the end over a detail is more
#  expensive than a minute of checking -- and a production uploaded to
#  auphonic.com with the wrong settings costs credit on top.
#
#  The report is the same for both modes and is called from one place,
#  before the fork. What needs several tracks -- the crosstalk -- simply
#  falls away with one track.
# =====================================================================

# How much separation the 3:1 rule asks for: with the other microphone three
# times as far away as the speaker's own, the neighbouring voice is about 9.5
# dB quieter -- 20*log10(3). Below that, crosstalk starts to be audible in the
# mix as a comb filter.
THREE_TO_ONE_DB = 9.5

# The kind of a video file in the project. Content is a camera like any
# other; intro and outro are finished clips that are neither aligned nor
# processed -- they only go into the timeline.


class Finding(object):
    """One item from the preflight report.

    Four kinds, and the kind decides what happens next: "good" is only
    counted, "hint" appears in the report, "fixed" says the script
    fixed it itself, and "abort" stops the run unless --anyway is
    given.
    """

    def __init__(self, kind, field, text, advice="", file=""):
        self.kind = kind
        self.field = field
        self.text = text
        self.advice = advice
        # Which file the finding belongs to. Empty means it only arises from
        # comparing several files. The interface hangs the mark on it; a name
        # comparison would be too imprecise here.
        self.file = file
        # Belongs to a file that does not take part. It is checked anyway -- a
        # row without a mark looks forgotten -- but its finding does not count
        # towards the balance and holds nothing up.
        self.set_aside = False

    def line(self, width=17):
        label = {"good": "", "hint": T('Note: '), "fixed": T('fixed: '),
                 "abort": T('Caution: ')}[self.kind]
        out = "    %-*s %s%s" % (width, self.field, label, self.text)
        return as_warn(out) if self.kind == "abort" else out


# What a cached measurement contains changes with the script. This number is
# part of the fingerprint: raising it makes all old measurements stale and they
# are taken once more. Without it the interface would show the old result for
# weeks after an extension.
#   2  the recording curve from the logs atom was added
MEASUREMENT_VERSION = 2


def _fingerprint(paths):
    """Return a fingerprint: version, language, path, size and mtime.

    A changed file gets a different fingerprint and is measured again.
    Unchanged, the earlier measurement stands.

    The language belongs in it because a stored finding holds its text
    ready-made. Without it a run in one language would serve the report of
    the last run in the other.
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
    update, so without this the folder keeps a dead layer for every
    release it has lived through.
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

    Cached per file, not per selection: in the interface files arrive one
    after another, and adding the fifth should not wait for the first four
    to be measured. Returns {"findings": [...], "data": {...}}; the data
    feeds the comparison across all files.
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

    Returns one list of intervals in seconds per point. The *packets* are
    queried, not the frames: a packet is a frame, its timestamp is in the
    container, and ffprobe decodes nothing for it. On a 4K file that is the
    difference between a blink and half a minute.

    Read in time windows rather than packet counts: ffprobe always resumes
    at the keyframe before a seek, and with long groups of pictures a window
    of 48 packets would still lie entirely before the intended spot. Without
    this sample only the average would be known, and that looks the same for
    a variable rate as for a fixed one.
    """
    if not duration or duration <= 0:
        points = [0.0]
    else:
        points = [duration * k / float(spots) for k in range(spots)]
    # All the points in one call. ffprobe takes a comma separated list of
    # intervals, and every call is a process: five per file cost nothing
    # here and 1.8 seconds each on the Windows builder, where starting a
    # process is the expensive part. Measured 30.8.2026: this test made
    # 62 of them and took two seconds on this Mac and 126 on the builder.
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
    # Packets arrive in decoding order, and with H.264 B-frames that is not
    # display order: the timestamps then jump back and forth. Sort first,
    # or one measures the codec's picture structure and takes it for a
    # variable frame rate.
    #
    # Sorting also puts the windows back in order, since they do not
    # overlap: what separates them is a gap of seconds, and the same
    # test that throws away an interval too long to be one frame is what
    # cuts one window from the next.
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

    Two questions, because a single doubled interval means nothing. The
    sample cuts into the middle of a group of pictures; a frame is then
    missing at the edge and the interval beside it is exactly twice as
    large. That is an artefact of sampling, not a variable rate.

    Counted as variable only:
      * a noticeable share of odd intervals -- ones that are not a whole
        multiple of the frame duration, or
      * different frame durations at different points in the file.
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
    # Where the frame duration wanders over the file, the rate is variable,
    # even if every single interval looks clean on its own.
    drift = (max(middles) - min(middles)) / min(middles) if len(middles) > 1\
        else 0.0
    return (odd_share > 0.05 or drift > 0.02,
            max(odd_share, drift))


def inspect_frame_rate(file_path):
    """Report whether the frame rate is fixed or variable, and what it costs.

    Two questions, two routes. *Whether* the intervals between frames vary
    is what the sample shows. *How far* the file is off over its whole
    length is in the container: frame count against duration.

    The distinction matters because it decides whether anything needs doing
    at all. An even deviation -- the file says 30, it is constantly 29.98 --
    is the same as clock drift in the audio and is compensated during
    alignment. Only *uneven* frame timing cannot be caught that way: pulling
    the audio onto the average fits at the start and the end, not in the
    middle.
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

    Returns (findings, data). The data is what the comparison across all
    cameras needs, so no file has to be touched a second time for it.
    """
    name = os.path.basename(file_path)
    b = inspect_frame_rate(file_path)
    if not b:
        return [Finding("hint", name[:24], T('no video track'))], {}
    out = [Finding("good", name[:24], T('%s fps -- %s, %dx%d, %s frames in %s')
                   % (decimal_text("%.3f" % b["nominal"]),
                      b["codec"] or "?", b["width"] or 0, b["height"] or 0,
                      group_text(b["videos"]),
                      as_hms(b["duration"])))]
    # From when is it worth mentioning? The difference between frame count
    # times nominal rate and the track duration is a few frames on every camera
    # and has no consequences -- alignment measures against the camera audio,
    # not against this number. A whole second is a statement.
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
        # Which way round it runs decides both sentences. Taken as an
        # amount, a file that runs slower than its label reads as one
        # that runs faster, and then both halves say the opposite.
        quicker = b["offset_s"] < 0
        spare = abs(b["offset_s"]) * b["nominal"]
        out.append(Finding(
            "hint", "",
            (T('%s fps, not the %s in the file -- %s more frames in '
               'the same length.') if quicker else
             T('%s fps, not the %s in the file -- %s fewer frames in '
               'the same length.'))
            % (decimal_text("%.4f" % b["mean"]),
               decimal_text("%.3f" % b["nominal"]),
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
            % ", ".join(decimal_text("%.3f" % r) for r in different),
            T('The Timeline gets one fixed rate -- the highest of them, '
              'or the next rate Resolve has above it. It converts the '
              'others; with 23.976 against 24 that is where its audio '
              'analysis tends to stall.')))
    # With Apple the recording curve is not in the colr box but in the logs
    # atom. Where that is present there is nothing to guess and nothing to
    # report -- it is read out and carried along byte for byte.
    curves = {}
    for d in data:
        if d.get("logs"):
            curves.setdefault(d["logs"], []).append(d.get("name") or "?")
    # Curve and primaries unset: say it once for all rather than per file -- it
    # is a property of the camera, not of the recording.
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
            % (group_text(len(without_colour)), group_text(len(data)),
               T(' -- only the matrix says BT.2020')
               if matrix == {PROGRAM.MATRIX_BT2020} else ""),
            T('Used as it stands -- nothing is invented. Check in Resolve '
              'under Clip Attributes, tab Color Space: if it says '
              '"Project" there, the input colour space was not recognised '
              'and has to be set by hand.')))
    # Differing recording curves would be worth a message; the same one
    # everywhere is not, since it is already in the colour line of every file.
    if len(curves) > 1:
        out.append(Finding(
            "hint", T('Capture curve'),
            T('the video files carry different recording curves: %s')
            # One per line: the names of three cameras behind one
            # another ran past the end of the column, and what was cut
            # off was the file name the reader needed.
            % "\n      ".join(T('%s in %s') % (k, ", ".join(v))
                              for k, v in sorted(curves.items())),
            T('It is in the logs atom of the picture description -- that '
              'is how Resolve recognises the input colour space. Different '
              'curves mean different input colour spaces.')))
    # Differently tagged cameras need different input colour spaces in Resolve.
    # That otherwise only shows once one camera looks unlike the other. Where
    # the logs atom says the same for all, the case is closed; Resolve goes by
    # that.
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
            # One tag per line, as with the curves above: "2/2/9 in
            # <camera>; 2/2/1 in <camera>" was cut off inside the first
            # camera's name.
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

    A camera splitting its recording into numbered blocks means they belong
    together -- but only if the next block starts where the previous one
    ends. A gap means the camera stopped, and then a piece of picture is
    missing exactly where the audio keeps running.
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
    out = [Finding("good", name[:24], "%s Hz, %s bit, %s, %s"
                   % (group_text(rate), depth,
                      channel_text(channels),
                      as_hms(duration)))]
    if rate and rate != SR:
        out.append(Finding(
            "fixed", "",
            T('%s Hz instead of %s Hz -- converted during processing.')
            % (group_text(rate), group_text(SR))))
    if channels > 2:
        out.append(Finding(
            "good", "",
            T('%s channels -- cut into tracks, see the rows above.')
            % group_text(channels),
            T('Every pair of channels is judged on its own: one stereo '
              'track, or two microphones and therefore two tracks. Silent '
              'inputs drop out. The rows under the file say what was '
              'measured, and the tick overrules it.')))
    # Clipping is invisible here otherwise, and actively so: the master
    # is measured as a sum and a limiter pulls it under -1 dBTP, so a
    # lapel microphone that was against the stop all evening comes out
    # looking clean. A hint, never a stop -- an overdriven recording is
    # sometimes the only recording there is.
    for channel, facts_ in sorted(clipping_facts(file_path).items()):
        runs, longest, milliseconds, first = facts_
        out.append(Finding(
            "hint", "",
            T('Channel %d is against the stop: %s times three samples or '
              'more in a row, the longest %s (%s ms), the first at %s.')
            % (channel + 1, group_text(runs), group_text(longest),
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

    A block is not a recording: several blocks in a row make one long
    recording. Recordings are compared, otherwise every block would count
    as too short.
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

    Material from one recording runs simultaneously, so the timecode windows
    overlap. A file overlapping with none of the others had an unset clock --
    typical for a recorder starting at 00:00:00 while the cameras write time
    of day.

    The rule itself is clocks_apart, and only there: what is decided
    here also decides the zero point of the cut, so the two must not
    be able to disagree about the same clock.
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
        # Each value goes back into a timecode at the rate of the file it
        # came off. A camera running at 25 counts 25 frames to the second,
        # and printing its timecode at 30 would move it by two frames.
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


# How far into a recording the bleed windows may reach before it is
# cheaper to read the whole thing once than to seek into it five times.
# Five minutes at 16 kHz mono is 19 MB; a two-hour interview would be
# 460, which is the reason the sampling exists at all. What this buys is
# process starts, and those are what a Windows builder charges for:
# local_run made 62 of them and took two seconds here and 126 there.
WHOLE_READ_S = 300.0


def crosstalk_apart(audio_paths, rate=16000, window=5, long=20.0,
                    min_len_long=4.0):
    """Measure how loudly each voice appears in the others' microphones.

    Not the whole recording -- too slow for a preflight -- but a few
    windows over the shared time, enough for a level ratio. Returns
    ([(who, in whose microphone, dB), ...], indices into *audio_paths*,
    plus why not. One measurement, two readers: the preflight makes
    sentences of it, the separation asks whether the tracks still tell.
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
        # Five windows of 5.7 seconds out of a 34-second recording is the
        # whole file read in five processes, and the pieces are joined
        # again on the next line anyway. Where the windows reach no
        # further than a few minutes in, it is read once and cut up
        # here. Not for a two-hour interview: at this rate the whole of
        # one is 460 MB, which is what the sampling is for.
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
    None where it could not be measured. That is the number the
    separation asks before it decides whether the tracks can still say
    who is speaking on their own.
    """
    try:
        rows, _why = crosstalk_apart(audio_paths)
    except Exception:
        return None
    return min((db for _i, _j, db in rows), default=None)


def check_crosstalk(audio_paths, rate=16000, window=5, long=20.0,
                    min_len_long=4.0):
    """Say in words how much of each voice sits in the other microphones.

    The yardstick is the 3:1 rule of audio recording: with the other
    microphone three times as far from the speaker as their own, the
    neighbouring voice is about 9.5 dB quieter. That is a statement
    about the *setup in the room*, not about post-production; it can
    only be changed next time.
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
               names[i], names[j], decimal_text("%.1f" % separation))
            if not good else
            T("%s in %s's microphone: %s dB quieter than in their own.")
            % (names[i], names[j], decimal_text("%.1f" % separation)),
            "" if good else
            T('It arose during the recording and cannot be changed '
              'now. The less the microphones are separated, the more '
              'cautiously De-Bleed at auphonic.com can work. Next '
              'time: three times as far from the neighbouring '
              'microphone as from your own mouth, then the '
              'neighbouring voice sits about %s dB lower.')
            % decimal_text("%.1f" % THREE_TO_ONE_DB),
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
            % (group_text(bad), group_text(len(out)),
               decimal_text("%.1f" % THREE_TO_ONE_DB)),
            T('This comes from the recording, not afterwards: the '
              'microphones sit too close together or too far from the '
              'mouth.')))
    return out


# What the room has to be over the estimate before the run is called
# safe. The estimate is a rough one and says so, and a rough estimate
# passed by one per cent is not a pass: a real run cleared the old check
# by 1.1 GB of 96.6 and died at 88 per cent.
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
    before the axis has been measured. One point alone leaves the other
    end open, and then the answer is None and nothing is scaled.
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
    carries that stretch and no more, so it shrinks by its own share and
    not by the longest camera's. Both numbers are megabytes.
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
    # The picture is copied unchanged; what grows the file is the audio,
    # and it is written uncompressed: 48 kHz, 24 bit, two channels are
    # 0.29 MB per second and per track. Counting it from the sizes of the
    # given audio files was far too low wherever the cameras bring their
    # own sound and no separate recording exists at all.
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

    The size is the preflight's own reckoning, so the two numbers agree
    and a time window shortens both. Only what lands in the target
    folder counts here; the temporary files are the preflight's
    question. Where the disk cannot be read, only the target is named.
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
            % (group_text(len(video_paths)), as_data_size(needed), where),
            T('Free space there: %s') % as_data_size(free)]


def check_disk_space(target_folder, audio_paths, video_paths, multitrack,
                        window_s=None):
    """Report whether there is enough disk space for what will be created.

    Roughly calculated but erring upward, so that a run stops before it
    starts rather than halfway. *window_s* shortens the cameras, so the
    estimate follows it -- generously, or a run that fits is refused.
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
    # The temporary files go into the system temp folder, and where that
    # sits on the same disk as the output they eat the same space twice.
    # Counted once the check passed a real run by 1.1 GB and the run
    # died at 88 per cent with nothing said (31.8.2026).
    if on_one_disk(tempfile.gettempdir(), folder or "."):
        needed += added
    # "hint", not "abort": the numbers do fit, and the estimate errs
    # upward, so refusing the run would be wrong. But an estimate that
    # calls itself rough, cleared by one per cent, is not room enough --
    # a real run passed that way and died at 88 per cent.
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


# What the platforms expect as loudness. The podcast directories work with -16
# LUFS for stereo and -19 for mono; YouTube turns loud material down to about
# -14 LUFS but does not turn quiet material up.
PLATFORMS = {
    "podcast": (-16.0, 'Podcast directories, stereo'),
    "podcast-mono": (-19.0, 'Podcast directories, mono'),
    "youtube": (-14.0, 'YouTube -- turns down only, never up'),
    "broadcast": (-23.0, 'EBU R128, broadcast'),
}


def loudness_choices():
    """The loudness targets to pick from: (value, caption).

    The caption carries the number and, in brackets, what that number is
    the standard for. The number on its own says nothing to anybody who
    has not learnt the four by heart, and the brackets are what makes
    the list readable without a manual.

    None is the fifth answer and not a fifth number: nothing of ours
    adjusts at all. auphonic.com goes on doing what its preset says --
    anything else would be a silent remote control of somebody else's
    service -- and without auphonic.com the sound stays as it is in the
    source files.
    """
    out = [(target, "%.0f LUFS (%s)" % (target, T(what_for)))
           for target, what_for in PLATFORMS.values()]
    out.append((None, T('Take from source files')))
    return out


def loudness_answer_file():
    """Where the loudness last chosen in the window is kept."""
    folder = cache_folder()
    return os.path.join(folder, "loudness_target") if folder else ""


def loudness_last():
    """The loudness last chosen in the window; -16 LUFS if never chosen.

    Remembered the way the answer about looking for updates is: one
    small file in the cache folder, and no second mechanism beside it.
    Whoever delivers to the same place every week should not have to
    pick the same entry every week. A project file carrying its own
    value beats this one -- what was saved with a production belongs to
    that production.
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
    cannot -- the value is in the window and in the project file -- but
    a caller that wants to know is told rather than left guessing.
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

    Out here and not inside the window, for the reason
    cut_fields_build gives: the window is long enough without another
    stretch of widget assembly. It is a builder and nothing else --
    the value it binds to comes in, the drop-down comes back.

    It belongs in the Production box, on the page and not behind
    "Settings ...": it is a property of this episode the way the name
    and the output folder are, and whoever delivers somewhere else next
    month has to trip over it rather than go looking for it. Until this
    was built no widget was bound to the loudness at all, and every
    episode out of the window came out at -16 LUFS whatever it was for.
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

        Compared as a number, not as an object: the same target arrives
        as -16.0 from the list and out of a project file, and one of
        them being an int would put the list on the wrong row.
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
            # A value nobody can pick here -- out of a project file
            # written by hand, or by a run with its own --lufs. It is
            # added rather than replaced: opening a project must not
            # quietly change what it was set to.
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
    # being dropped into a slot: in German it carries an article, and a
    # piece that settles its own case before it knows the slot is how a
    # wrong sentence gets built. Both halves are translated together.
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

    Several voices and no picture: the tracks leave as they were
    recorded, because a gain per track would put the voices out of
    balance with each other, and that balance is the one thing that
    path exists to keep. The number still travels to auphonic.com,
    which masters the mix, so a key puts it back in force. One place,
    because the preflight and the run both say it.
    """
    return (not videos and bool(getattr(args, "multitrack", False))
            and getattr(args, "lufs", None) is not None
            and not getattr(args, "auphonic_key", None))


def check_loudness_target(args, videos=()):
    """Report the loudness target in force. It only reports.

    It used to set args.lufs from --platform on the side, and a check
    that quietly changes what it is checking was the cause of the old
    fault: the report and the run could come apart. --platform is gone;
    the four numbers are a list in the window now. Where the number
    does nothing the report says so, or the log names a target that is
    then contradicted further down.
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
        # preset against: what it masters to is what comes out. That is
        # said, not complained about -- a check with no second value has
        # no verdict to give.
        if target is not None:
            out.append(Finding(
                "good", T('Loudness'),
                T('the preset masters to %s LUFS -- that stands, nothing '
                  'of ours adjusts.') % decimal_text("%.0f" % target)))
    elif target is not None and abs(target - float(lufs)) > 0.05:
        out.append(Finding(
            "abort", T('Loudness'),
            T('the preset masters to %s LUFS, the calculation uses %s.')
            % (decimal_text("%.0f" % target), decimal_text("%.0f" % lufs)),
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
        # In the window the finding stands on its file and the advice on
        # the mark. The log has neither, and a count with no findings
        # under it names none of them -- so only the advice is held back.
        if b.advice and not PROGRAM.GUI_RUNNING:
            for line in textwrap.wrap(b.advice, 70):
                print("      %s" % line)
    abort = [b for b in findings if b.kind == "abort"]
    hints = [b for b in findings if b.kind == "hint"]
    fixed = [b for b in findings if b.kind == "fixed"]
    parts = [T('%s checked') % group_text(len(findings))]
    if fixed:
        parts.append(TN(len(fixed), '%s fixed on its own',
                        '%s fixed on their own') % group_text(len(fixed)))
    if hints:
        parts.append(TN(len(hints), '%s hint', '%s hints')
                     % group_text(len(hints)))
    if abort:
        parts.append(TN(len(abort), '%s reason to stop',
                        '%s reasons to stop') % group_text(len(abort)))
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

    Each file is measured and cached individually. Adding a file measures
    only that one; the others are already there. What shows only in
    comparison is derived from the cached data and costs nothing.

    *set_aside* are files that do not take part -- ignored ones, intro,
    outro. They are still checked so their row is not the only one without a
    mark, but they stay out of the comparisons. A colour chart has different
    dimensions from the cameras, and turning that into a hint helps nobody.
    """
    set_aside = {path_key(x) for x in (set_aside or ())}

    def counts_not(findings_, file_path):
        if path_key(file_path) in set_aside:
            for b in findings_:
                b.set_aside = True
        return findings_

    findings, video_data, audio_data = [], [], []
    # The files are measured all at once. Each has its own cache entry
    # and knows nothing of the others, so there is nothing to wait for;
    # what compares them happens below, on the results.
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
    # Everything comparing audio recordings works with recordings, not with
    # blocks: two blocks of the same recording run one after another, are
    # individually shorter and never overlap.
    audio_paths = [p for p in audio_paths if path_key(p) not in set_aside]
    chains = (group_recording_parts(audio_paths, apart=apart,
                                    together=together)
              if audio_paths else [])
    recordings = by_recording(audio_data, chains)
    findings += compare_audio_tracks(recordings)
    findings += timecode_comparison(video_data + recordings)
    heads = [row[0] for row, _rest in chains]
    if crosstalk and len(heads) > 1:
        # Crosstalk is a statement about the interplay, not about a single
        # file, so it is cached for exactly this set.
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
    several tracks only checks itself then; everything else applies to a
    single track just as well.
    """
    if getattr(args, "no_preflight", False):
        return 0
    findings = collect_findings(audio_paths, video_paths,
                              bool(getattr(args, "preflight_again", False)),
                              bool(getattr(args, "multitrack", False)),
                              apart=getattr(args, "apart", ()),
                              together=getattr(args, "together", ()))
    # These two depend not on the material but on the call and the machine, so
    # they are determined afresh every time.
    findings += check_disk_space(getattr(args, "out", None), audio_paths, video_paths,
                             bool(getattr(args, "multitrack", False)),
                             window_from_points(args))
    findings += check_loudness_target(args, video_paths)
    return 1 if report_findings(findings, T('does the material fit together?'),
                               getattr(args, "anyway", False)) else 0


def run_ffmpeg_with_progress(cmd, duration, text):
    """Run ffmpeg and show its progress.

    Errors go to a file, not to a pipe. Progress is read from stdout until
    it ends, so an unread stderr pipe would fill up and ffmpeg would stop
    in the middle of the run, waiting for someone to empty it.
    """
    cmd = cmd[:1] + ["-nostats", "-progress", "pipe:1"] + cmd[1:]
    fd, log = tempfile.mkstemp(prefix="vpm_ff_", suffix=".txt")
    os.close(fd)
    try:
        with open(log, "wb") as fh:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=fh)
            # This is where a run spends its minutes, so this is where
            # breaking off has to reach. The child says it is here; the
            # window ends it, and the loop below falls out of itself.
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
