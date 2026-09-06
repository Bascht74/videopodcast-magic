# -*- coding: utf-8 -*-
"""Time and timecode: reading a clock off a file, and writing one.

A piece of the program, read in by beside(): it cannot import the file
it was cut out of, so the program is handed in and bound below by name.
"""

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# Bound above the seam, so each is a copy and none is read late.

SR = PROGRAM.SR
T = PROGRAM.T
ffprobe_json = PROGRAM.ffprobe_json
os = PROGRAM.os
probe_remember = PROGRAM.probe_remember
struct = PROGRAM.struct


# =====================================================================
#  Time and timecode
#  -----------------

def timecode_string(seconds, fps=30.0):
    if seconds < 0:
        seconds = 0.0
    f = int(round((seconds - int(seconds)) * fps))
    s = int(seconds)
    if f >= int(round(fps)):
        f, s = 0, s + 1
    return "%02d:%02d:%02d:%02d" % (s // 3600 % 24, s % 3600 // 60, s % 60, f)


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
    moved = timecode_string(parse_timecode(tc, fps) + by_s, fps)
    if is_drop_frame(tc):
        head, _sep, frames = moved.rpartition(":")
        moved = head + ";" + frames
    return moved


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
        '    <NOTE>videopodcast-magic</NOTE>\n'
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
        % (_xml_escape(name), _xml_escape(name), num, the_one, num, the_one, num, the_one,
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
    # Out of the one description of the file, not a second call:
    # duration_ts counts samples exactly, a duration in seconds is rounded.
    d = ffprobe_json(path)
    a = next((x for x in d.get("streams", [])
              if x.get("codec_type") == "audio"), {})
    try:
        n, sr = int(a["duration_ts"]), int(a.get("sample_rate") or SR)
        return int(round(n * SR / sr)) if sr and sr != SR else n
    except (KeyError, TypeError, ValueError):
        pass
    duration = float(a.get("duration") or d.get("format", {}).get("duration") or 0)
    return int(round(duration * SR))


def bext_time_reference(path):
    """Return TimeReference from the bext chunk in samples, or None."""
    return probe_remember("bext", path, lambda: _bext_time_reference(path))


def _bext_time_reference(path):
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
            if cid == b"bext":
                b = f.read(sz)
                return struct.unpack("<Q", b[338:346])[0] if len(b) >= 346 else None
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


def picture_rate(probed):
    """The frame rate of the picture in an ffprobe answer, or nothing.

    ffprobe writes it as a fraction, '30000/1001' for 29.97. The mean
    over the file comes first -- frames over duration, always real; the
    nominal rate is what the container claims, a timebase in odd files.
    """
    v = next((s for s in probed.get("streams", ())
              if s.get("codec_type") == "video"), None)
    for key in ("avg_frame_rate", "r_frame_rate"):
        parts = str((v or {}).get(key) or "").split("/")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            if int(parts[0]) and int(parts[1]):
                return int(parts[0]) / float(int(parts[1]))
    return None


def file_timecode(path, fps=None):
    """Return the start time in seconds from bext or a timecode track.

    The frames of a timecode are frames, so the rate decides what they
    are worth: at the wrong rate the start lands whole frames out. A
    sound file has none of its own; without one passed in, 30.
    """
    tr = bext_time_reference(path)
    if tr is not None:
        return tr / float(SR)
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
