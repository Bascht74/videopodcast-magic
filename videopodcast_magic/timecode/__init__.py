# -*- coding: utf-8 -*-
"""Time and timecode: reading a clock off a file, and writing one.

A piece of the program, read in by beside(): it cannot import the file
it was cut out of, so the program is handed in and bound below by name.
"""

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# Bound above the seam, so each is a copy and none is read late.

PROGRAM_NAME = PROGRAM.PROGRAM_NAME
SR = PROGRAM.SR
T = PROGRAM.T
ffprobe_json = PROGRAM.ffprobe_json
math = PROGRAM.math
number_text = PROGRAM.number_text
os = PROGRAM.os
path_key = PROGRAM.path_key
probe_remember = PROGRAM.probe_remember
struct = PROGRAM.struct


# =====================================================================
#  Time and timecode
#  -----------------

def timecode_string(seconds, fps=30.0, drop_frame=False):
    """A time of day since midnight as a timecode label.

    The digits are the same on both clocks (a drop-frame label reads as
    time of day; that is what the dropped numbers buy), so *drop_frame*
    decides the separator alone: a semicolon before the frames, by which
    timecode_to_frames counts the label. A colon on a drop-frame count
    lands frame zero 3.6 s per hour since midnight off the camera's clock.
    """
    if seconds < 0:
        seconds = 0.0
    f = int(round((seconds - int(seconds)) * fps))
    s = int(seconds)
    if f >= int(round(fps)):
        f, s = 0, s + 1
    return "%02d:%02d:%02d%s%02d" % (s // 3600 % 24, s % 3600 // 60, s % 60,
                                     ";" if drop_frame else ":", f)


def parse_timecode(s, fps=30.0):
    """Parse '6.4087', '0:06', '1:23:45' or '17:15:56:12' into seconds.

    Drop frame writes the last colon as a semicolon, '17:15:56;12' --
    the same value; how frames are counted is timecode_to_frames's.
    """
    t = str(s).strip().replace(";", ":")
    p = t.split(":")
    if len(p) == 4:
        return float(p[0]) * 3600 + float(p[1]) * 60 + float(p[2]) + float(p[3]) / fps
    if len(p) == 3:
        return float(p[0]) * 3600 + float(p[1]) * 60 + float(p[2])
    if len(p) == 2:
        return float(p[0]) * 60 + float(p[1])
    return float(t)


def frame_rate_fraction(fps):
    """Return a frame rate as a fraction: 29.97 -> 30000/1001.

    iXML requires a fraction rather than a decimal.
    """
    for whole, num, the_one in ((23.976, 24000, 1001), (29.97, 30000, 1001),
                           (47.952, 48000, 1001), (59.94, 60000, 1001),
                           (119.88, 120000, 1001)):
        if abs(fps - whole) < 0.02:
            return num, the_one
    return int(round(fps)), 1


def is_drop_frame(tc):
    """Report whether a timecode string is drop frame.

    The notation decides, not the frame rate: 29.97 exists in both
    flavours. A semicolon before the frames means drop, nothing non-drop.
    """
    return ";" in str(tc or "")


def timecode_moved(tc, by_s, fps=30.0):
    """A timecode string moved on by *by_s* seconds.

    Cutting a head moves the moment the first frame was taken. The
    drop-frame semicolon is kept, or the frame reads as another time.
    """
    return timecode_string(parse_timecode(tc, fps) + by_s, fps,
                           drop_frame=is_drop_frame(tc))


def build_ixml(name, tr, fps, bits=24, channels=1, df=False):
    """Build the iXML block for one track.

    Resolve is happy with bext alone; Premiere and Media Composer need iXML.
    """
    num, the_one = frame_rate_fraction(fps)
    ndf = not df
    tracks = "".join(
        "    <TRACK>\n      <CHANNEL_INDEX>%d</CHANNEL_INDEX>\n"
        "      <INTERLEAVE_INDEX>%d</INTERLEAVE_INDEX>\n"
        "      <NAME>%s</NAME>\n    </TRACK>\n" % (k, k, _xml_escape(name))
        for k in range(1, max(1, channels) + 1))
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n<BWFXML>\n'
        '  <IXML_VERSION>1.5</IXML_VERSION>\n'
        '  <PROJECT>%s</PROJECT>\n'
        '  <TAPE>%s</TAPE>\n'
        '  <TAKE>1</TAKE>\n'
        '  <SPEED>\n'
        '    <NOTE>%s</NOTE>\n'
        '    <MASTER_SPEED>%d/%d</MASTER_SPEED>\n'
        '    <CURRENT_SPEED>%d/%d</CURRENT_SPEED>\n'
        '    <TIMECODE_RATE>%d/%d</TIMECODE_RATE>\n'
        '    <TIMECODE_FLAG>%s</TIMECODE_FLAG>\n'
        '    <FILE_SAMPLE_RATE>%d</FILE_SAMPLE_RATE>\n'
        '    <AUDIO_BIT_DEPTH>%d</AUDIO_BIT_DEPTH>\n'
        '    <TIMESTAMP_SAMPLES_SINCE_MIDNIGHT_HI>%d'
        '</TIMESTAMP_SAMPLES_SINCE_MIDNIGHT_HI>\n'
        '    <TIMESTAMP_SAMPLES_SINCE_MIDNIGHT_LO>%d'
        '</TIMESTAMP_SAMPLES_SINCE_MIDNIGHT_LO>\n'
        '  </SPEED>\n'
        '  <TRACK_LIST>\n    <TRACK_COUNT>%d</TRACK_COUNT>\n%s'
        '  </TRACK_LIST>\n</BWFXML>\n'
        % (_xml_escape(name), _xml_escape(name), PROGRAM_NAME,
           num, the_one, num, the_one, num, the_one,
           "NDF" if ndf else "DF", SR, bits,
           tr >> 32, tr & 0xFFFFFFFF, max(1, channels), tracks))


def _xml_escape(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def append_ixml(file_path, xml):
    """Append the iXML block as a RIFF chunk and fix up the RIFF size."""
    payload = xml.encode("utf-8")
    if len(payload) % 2:
        payload += b"\x00"
    with open(file_path, "r+b") as f:
        f.seek(0, os.SEEK_END)
        end = f.tell()
        f.write(b"iXML" + struct.pack("<I", len(payload)) + payload)
        f.seek(4)
        f.write(struct.pack("<I", end + len(payload)))


def parse_time_point(s, fps=30.0):
    """Parse a --in-point/--out-point time.

    Returns (seconds, absolute): absolute is wall clock since midnight,
    a timecode; everything else counts from the start of the window. A
    negative value measures back from its end, only for --out-point.
    """
    t = str(s).strip()
    if not t:
        return None, False
    minus = t.startswith("-")
    absolute = t.count(":") >= 2 and not t.startswith(("+", "-"))
    value = parse_timecode(t.lstrip("+-"), fps)
    return (-value if minus else value), absolute


def as_relative_time(seconds):
    """Format a position the way --in-point expects it."""
    ms = int(round(max(0.0, seconds) * 1000))
    s = ms // 1000
    return "+%d:%02d:%02d.%03d" % (s // 3600, s % 3600 // 60, s % 60,
                                   ms % 1000)


def as_hms(sec, mark=None):
    """Write a duration as h:mm:ss with milliseconds.

    *mark* overrides the decimal point. A file that other programs read
    passes ".", so what is in it does not depend on the language.
    """
    # Round to milliseconds first, then split -- otherwise 119.9995 s
    # comes out as "0:01:59.1000".
    ms = int(round(abs(sec) * 1000))
    s = ms // 1000
    return "%s%d:%02d:%02d%s%03d" % ("-" if sec < 0 else "", s // 3600,
                                     s % 3600 // 60, s % 60,
                                     T(".") if mark is None else mark,
                                     ms % 1000)


def sample_count(path):
    """Return the length of a file in samples at the working rate."""
    return probe_remember("samples", path, lambda: _sample_count(path))


def _sample_count(path):
    # From the one description, exactly: duration_ts in the stream's time
    # base, a sample in a WAV but 1/14112000 s in an MP3, where a 20 s
    # file read as samples measured 5880 s (27.9.2026).
    d = ffprobe_json(path)
    a = next((x for x in d.get("streams", [])
              if x.get("codec_type") == "audio"), {})
    try:
        n, sr = int(a["duration_ts"]), int(a.get("sample_rate") or SR)
        over, under = (int(x) for x in (a.get("time_base") or "1/%d" % sr)
                       .split("/"))
        return (n * over * SR + under // 2) // under
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        pass
    duration = float(a.get("duration") or d.get("format", {}).get("duration") or 0)
    return int(round(duration * SR))


def bext_time_reference(path):
    """Return TimeReference from the bext chunk in samples, or None.

    Samples at the file's own rate, which wav_rate names: 01:00:00 is
    158760000 in a 44.1 kHz file and 172800000 in a 48 kHz one.
    """
    return probe_remember("bext", path, lambda: _bext_time_reference(path))


def _bext_time_reference(path):
    b = _riff_chunk(path, b"bext")
    return struct.unpack("<Q", b[338:346])[0] \
        if b is not None and len(b) >= 346 else None


def wav_rate(path):
    """The sample rate a WAV's own fmt chunk names, or None."""
    return probe_remember("wav_rate", path, lambda: _wav_rate(path))


def _wav_rate(path):
    """nSamplesPerSec, four bytes into the fmt chunk; 0 there is none."""
    b = _riff_chunk(path, b"fmt ")
    rate = struct.unpack("<I", b[4:8])[0] \
        if b is not None and len(b) >= 8 else 0
    return rate or None


def _riff_chunk(path, wanted):
    """The body of the first chunk named *wanted* in a WAV, or None."""
    try:
        f = open(path, "rb")
    except OSError:
        return None
    with f:
        if f.read(4) not in (b"RIFF", b"RF64"):
            return None
        f.seek(12)
        while True:
            h = f.read(8)
            if len(h) < 8:
                return None
            cid, sz = h[:4], struct.unpack("<I", h[4:8])[0]
            if cid == wanted:
                return f.read(sz)
            f.seek(sz + (sz & 1), os.SEEK_CUR)

DAY_S = 24 * 60 * 60


def unwrap_day(value, near):
    """Move *value* by whole days until it sits closest to *near*.

    A timecode starts over at midnight, so a recording running across
    it looks 23 hours away. Nothing is added to either axis, so the two
    meet only where they are compared. Half a day is the fence: past it
    a night is indistinguishable from a day's gap.
    """
    if value is None or near is None:
        return value
    return value - DAY_S * round((value - near) / float(DAY_S))


def clocks_apart(spans):
    """Which of these time windows share their time with no other.

    *spans* is [(start, length, key), ...] read off the timecode; all
    are first brought onto one axis around the middle. A window that
    overlaps none came off a clock never set. Fewer than three say
    nothing. Returns (apart, moved, placed).
    """
    spans = [(float(a), max(1.0, float(n or 0.0)), k) for a, n, k in spans]
    if len(spans) < 3:
        return set(), [], spans

    def alone(mine, start, wide, among):
        return not any(i != mine and start < b + m and b < start + wide
                       for i, (b, m, _k) in enumerate(among))

    middle = sorted(a for a, _n, _k in spans)[len(spans) // 2]
    moved, placed = [], []
    for i, (a, n, k) in enumerate(spans):
        shifted = unwrap_day(a, middle)
        # A file starting at 00:00:00 is a clock never set, not a run
        # begun after midnight; unwrapping it would hide that fault.
        if a < 1.0:
            shifted = a
        # Moving a file a whole day is a claim, worth making only if it
        # then lands among the others; otherwise the move is taken back.
        if shifted != a and not alone(i, shifted, n, spans):
            moved.append(k)
            placed.append((shifted, n, k))
        else:
            placed.append((a, n, k))
    return (set(k for i, (a, n, k) in enumerate(placed)
                if alone(i, a, n, placed)), moved, placed)


# The rates a camera is built to run at. A container naming one of these
# means it; any other figure it names may be a timebase, not a format.
STANDARD_FRAME_RATES = (23.976, 24.0, 25.0, 29.97, 30.0, 50.0, 59.94, 60.0)


def stream_frame_rate(v):
    """The frame rate one video stream of an ffprobe answer runs at, or None.

    The one rule for every place that reads a rate. The nominal rate
    (r_frame_rate) where it is a standard one, within a thousandth; else
    the mean over the file (avg_frame_rate). A phone recording with a
    variable rate says 30 and averages 29.99 or, in low light, 24: its
    timecode track counts at 30, and so does an editor.
    """
    def fraction(key):
        """One of ffprobe's fractions as a number; None where it names none."""
        parts = str((v or {}).get(key) or "").split("/")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit() \
                and int(parts[0]) and int(parts[1]):
            return int(parts[0]) / float(int(parts[1]))
        return None

    nominal, mean = fraction("r_frame_rate"), fraction("avg_frame_rate")
    if nominal and any(abs(nominal - r) <= r * 0.001
                       for r in STANDARD_FRAME_RATES):
        return nominal
    return mean or nominal


def picture_rate(probed):
    """The frame rate of the picture in an ffprobe answer, or nothing.

    ffprobe writes it as a fraction, '30000/1001' for 29.97; which of its
    two figures counts is stream_frame_rate's.
    """
    return stream_frame_rate(next((s for s in probed.get("streams", ())
                                   if s.get("codec_type") == "video"), None))


def file_timecode(path, fps=None):
    """Return the start time in seconds from bext or a timecode track.

    The frames of a timecode are frames, so the rate decides what they
    are worth: at the wrong rate the start lands whole frames out. A
    sound file has none of its own; without one passed in, 30.
    """
    tr = bext_time_reference(path)
    if tr is not None:
        # Counted at the file's own rate: read at 48 kHz, a 44.1 kHz
        # recorder's 01:00:00:00 lands at 00:55:07. No fmt chunk: SR.
        return tr / float(wav_rate(path) or SR)
    d = ffprobe_json(path)
    rate = float(fps) if fps else (picture_rate(d) or 30.0)
    # The tracks before the file: a track's clock is what the camera
    # wrote, the file level what ffmpeg made of it, and the camera wins.
    # A file that keeps one nowhere else -- MXF, AVI -- is read after.
    for source in [s.get("tags", {}) or {} for s in d.get("streams", [])] +\
                  [d.get("format", {}).get("tags", {})]:
        if source.get("timecode"):
            try:
                return parse_timecode(source["timecode"], rate)
            except Exception:
                pass
    return None


# =====================================================================
#  Frame rates and frames
#  ----------------------

# The rate a file runs at and the rate a Timeline gets, and seconds,
# frames and timecode turned into one another; none of it asks Resolve.

def seconds_to_frames(seconds, fps):
    """Convert a duration to frames using the true rate; 29.97 stays 29.97."""
    return int(round(seconds * fps))


def frames_of_the_file(length, fps, own):
    """How many frames of a file fit into *length* frames of the Timeline.

    The most that fit and never one more, or a shot runs into the next
    one: Resolve pushes what overlaps, and the pushes add up. What a
    shot leaves uncovered the one after it picks up; one frame is floor.
    """
    # A whole number of frames a division misses by a billionth is that
    # whole number: 23.976 in a 23.976 Timeline asks one frame too many.
    return max(1, int(math.ceil((length + 1) * own / float(fps) - 1e-9)) - 1)


def timeline_frames_of(count, fps, own):
    """How many frames of the Timeline a span of *count* file frames fills.

    Resolve keeps whole Timeline frames, so the last part frame is lost:
    175 frames of a 24 file fill 218 of a 30 Timeline, 176 fill 220.
    """
    return int(count * fps / float(own) + 1e-9)


# Every rate Resolve offers a Timeline, and no other.
RESOLVE_FRAME_RATES = (16.0, 18.0, 23.976, 24.0, 25.0, 29.97, 30.0, 47.952,
                 48.0, 50.0, 59.94, 60.0, 72.0, 90.0, 95.904, 96.0, 100.0,
                 119.88, 120.0)


# How far a measured rate may sit from one of those and still be it.
# Relative: one frame at 120 is a fifth of one at 24. An averaged
# reading strays a few ten-thousandths, a foreign rate four times that.
FRAME_RATE_TOLERANCE = 0.01


def known_frame_rate(fps):
    """The Resolve rate this one is, allowing for a measured reading.

    A rate this answers None for is not one Resolve gives a Timeline.
    The file is used all the same, counting in its own.
    """
    if not fps:
        return None
    near = min(RESOLVE_FRAME_RATES, key=lambda r: abs(r - fps))
    return near if abs(near - fps) <= near * FRAME_RATE_TOLERANCE else None


def own_frame_rate(fps):
    """The rate a file's own frames are counted at.

    A measured reading strays a few ten-thousandths from the format it
    means, so a Resolve rate answers where it means one. Where it means
    none the reading itself does: a file at 15 counts fifteen a second.
    """
    return known_frame_rate(fps) or float(fps or 30.0)


def resolve_timeline_rate(fps):
    """The rate a Timeline gets for material running at this one.

    Not the nearest but the next one up: upwards Resolve repeats frames,
    downwards it throws them away. 16 and 120 are the ends -- 15 and 240
    are refused -- and a 15 file in a 16 Timeline keeps its length.
    """
    known = known_frame_rate(fps)
    if known is not None:
        return known
    if not fps:
        return 30.0
    return next((r for r in RESOLVE_FRAME_RATES if r > fps),
                RESOLVE_FRAME_RATES[-1])


def file_frame_rate(info):
    """The rate a video file runs at, by stream_frame_rate's one rule.

    video_facts keeps it as "nominal": the file's own rate, which --fps
    does not touch.
    """
    return (info or {}).get("nominal") or (info or {}).get("fps") or 0.0


def timeline_frame_rate(args, videos, ref_clip):
    """The rate the Timeline runs at: the highest one in the material.

    Converted upwards Resolve repeats frames, downwards it throws them
    away, so the fastest camera decides. Intro and outro do not count.
    """
    edges = {path_key(p) for p in (getattr(args, "intro", None),
                                   getattr(args, "outro", None)) if p}
    rates = [(e or {}).get("fps") or 0.0 for v, e in (videos or ())
             if path_key(v) not in edges]
    return max(rates) if any(rates) else (
        ref_clip[1]["fps"] if ref_clip else 30.0)


def frames_to_timecode(frames, fps, drop_frame=False):
    """The other way round: a frame number since midnight as a timecode.

    On the timecode clock, like timecode_to_frames: the true rate is
    off by about a minute per hour.
    """
    full = int(round(own_frame_rate(fps)))
    n = max(0, int(frames)) % (full * 86400)
    if drop_frame:
        dropped = 2 * full // 30
        per_ten = full * 600 - dropped * 9
        tens, rest = divmod(n, per_ten)
        per_minute = full * 60 - dropped
        # The first minute of every ten drops nothing, the nine after it do.
        n += dropped * 9 * tens
        if rest >= dropped:
            n += dropped * ((rest - dropped) // per_minute)
    f = n % full
    s = n // full
    return "%02d:%02d:%02d%s%02d" % (s // 3600 % 24, s % 3600 // 60, s % 60,
                                     ";" if drop_frame else ":", f)


def timecode_to_frames(tc, fps):
    """Convert a timecode to a frame number since midnight.

    Not with the true rate: a non-drop timecode still counts thirty
    frames per second at 29.97. Drop frame skips numbers instead.
    """
    if not tc:
        return 0
    df = ";" in str(tc)
    t = str(tc).replace(";", ":").split(":")
    if len(t) != 4:
        return 0
    h, m, s, f = (int(x) for x in t)
    full = int(round(own_frame_rate(fps)))                    # 30 at 29.97
    n = ((h * 3600 + m * 60 + s) * full) + f
    if df:
        # Two numbers dropped per minute, except every tenth minute.
        dropped = 2 * full // 30
        minutes = h * 60 + m
        n -= dropped * (minutes - minutes // 10)
    return n


def cameras_frame_rate(cameras):
    """The rate the cut has to be read at, measured on a camera.

    The frames of a timecode are frames, so one read at the wrong rate
    lands whole frames out and the picture runs ahead of the sound on
    every camera whose timecode has a frame part. Cameras ending :00 are
    exact either way, which is how this sits unseen.
    """
    for cam in cameras or ():
        path = cam.get("file") or ""
        if path and os.path.exists(path):
            rate = picture_rate(ffprobe_json(path))
            if rate:
                return float(rate)
    return 0.0


def timeline_timecode(seconds, zero, fps, drop_frame=False):
    """The timecode a moment of programme time carries on the Timeline.

    Frame zero of the Timeline, then the frames since it -- the two steps
    build_cut_timeline takes, or the paper and the Timeline name frames
    one apart wherever the zero does not sit on a whole one. *drop_frame*
    is the Timeline's own setting: the same frame reads differently on
    the two clocks, and Resolve reads what is written on the one it runs.
    """
    return frames_to_timecode(zero + seconds_to_frames(seconds, fps), fps,
                              drop_frame)


def timecode_seconds(info):
    """The timecode in a video's facts, in seconds, or nothing."""
    if not (info or {}).get("tc"):
        return None
    try:
        return parse_timecode(info["tc"], max(1.0, info.get("fps") or 30.0))
    except (ValueError, TypeError):
        return None


def report_timecode_check(audio_start, info, measured, indent="  "):
    """Compare what the timecode says with what can be heard."""
    if audio_start is None or not info["tc"]:
        return
    fps = max(1.0, info["fps"])
    loud_tc = unwrap_day(parse_timecode(info["tc"], fps),
                         audio_start) - audio_start
    deviation = measured - loud_tc
    print(T('%sTimecode check of the audio file') % indent)
    if not PROGRAM.GUI_RUNNING:
        print(T('%s  Audio starts per timecode at    %s')
              % (indent, timecode_string(audio_start, fps)))
        print(T('%s  Picture starts per timecode at  %s')
              % (indent, timecode_string(parse_timecode(info["tc"], fps), fps)))
    print(T('%s  Offset per timecode:            %s') % (indent, as_hms(loud_tc)))
    print(T('%s  Offset measured:                %s') % (indent, as_hms(measured)))
    if abs(deviation) > 60:
        print(T('%s  Deviation:                      %s') % (indent, as_hms(deviation)))
        print(T('%s  The audio timecode does not fit the picture at all -- '
                'probably a clock never set. The measurement is used.')
              % indent)
    elif abs(deviation) > 0.5 / fps:
        print(T('%s  Deviation:                      %s  (%s frames)')
              % (indent, as_hms(deviation),
                 number_text(abs(deviation) * fps)))
        print(T('%s  The timecode does not fit what is heard. The '
                'measurement is used.') % indent)
    else:
        print(T('%s  Deviation:                      %s  (%s frames) -- fits')
              % (indent, as_hms(deviation),
                 number_text(abs(deviation) * fps)))
