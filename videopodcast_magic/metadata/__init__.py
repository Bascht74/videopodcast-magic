# -*- coding: utf-8 -*-
"""What a file says of itself: its size, its atoms, its colour, its keys.

A piece of the program, read out of the folder beside it by beside().
It cannot import the file it was cut out of, because that file is
still being read while this one is; the program is handed in instead,
and every name this piece uses out of it is bound below, by name.
"""

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

# What the program has and this piece uses, bound once so that the
# reading reads as it did in the one file. Seven names are missing,
# and the two blocks under the list say which and why.

SR = PROGRAM.SR
T = PROGRAM.T
TN = PROGRAM.TN
as_hms = PROGRAM.as_hms
as_warn = PROGRAM.as_warn
channel_text = PROGRAM.channel_text
decimal_text = PROGRAM.decimal_text
ffprobe_json = PROGRAM.ffprobe_json
file_timecode = PROGRAM.file_timecode
group_text = PROGRAM.group_text
math = PROGRAM.math
number_text = PROGRAM.number_text
os = PROGRAM.os
parse_timecode = PROGRAM.parse_timecode
picture_rate = PROGRAM.picture_rate
sample_count = PROGRAM.sample_count
struct = PROGRAM.struct
subprocess = PROGRAM.subprocess
sys = PROGRAM.sys
timecode_string = PROGRAM.timecode_string
unwrap_day = PROGRAM.unwrap_day

# Six of the seven stand in the project, which is read far below this
# piece: MATRIX_BT2020, PRIMARIES_BT2020, camera_text, colour_text,
# file_frame_rate and known_frame_rate. A copy taken here would find
# nothing, so each is read as PROGRAM.<name> where it is used.

# GUI_RUNNING is the seventh. The window sets it on the program
# object, which is a write no piece is told about, so a copy taken
# here would answer with the value of the run before. It stays over
# there and is read as PROGRAM.GUI_RUNNING as well.


# =====================================================================
#  What a file says
#  ----------------

def size_in_mb(file_path):
    try:
        return os.path.getsize(file_path) / 1e6
    except OSError:
        return 0.0


def as_data_size(mb_value):
    """Format a byte count for reading: 542 MB, 1,024 MB, 28.9 GB."""
    if mb_value >= 1000:
        return decimal_text("%.1f GB" % (mb_value / 1000.0))
    return "%s MB" % group_text(math.ceil(mb_value))


def audio_summary(file_path):
    """Return key facts about an audio file as (label, value) pairs."""
    d = ffprobe_json(file_path)
    a = next((x for x in d.get("streams", []) if x.get("codec_type") == "audio"), {})
    if str(a.get("sample_fmt", "")).startswith("flt"):
        depth = "32 bit float"
    else:
        depth = "%s bit" % (a.get("bits_per_raw_sample")
                            or a.get("bits_per_sample") or "?")
    channels = channel_text(a.get("channels"))
    tc = file_timecode(file_path)
    # Read at the file's own rate, so shown at it too: at 25 the frames
    # of the timecode are worth 1/25 s, and a line printed at 30 would
    # give the file back a timecode it never carried.
    rate = picture_rate(d) or 30.0
    return [("Format", "%s, %s, %s Hz, %s" % (a.get("codec_name", "?"), depth,
                                              a.get("sample_rate", "?"), channels)),
            (T('Length'), "%s  (%s)  --  %s"
             % (as_hms(sample_count(file_path) / float(SR)), as_data_size(size_in_mb(file_path)),
                "Timecode %s" % timecode_string(tc, rate) if tc is not None
                else T('no timecode')))]


MOV_CONTAINERS = (b"moov", b"trak", b"mdia", b"minf", b"stbl", b"wave")


def _mov_atoms(f, end):
    """Enumerate atoms between the current offset and end.

    Yields (kind, start of payload, end of atom) per atom.
    """
    while True:
        begin = f.tell()
        if begin + 8 > end:
            return
        head = f.read(8)
        if len(head) < 8:
            return
        size = struct.unpack(">I", head[:4])[0]
        kind = head[4:8]
        if size == 1:
            raw = f.read(8)
            if len(raw) < 8:
                return
            size = struct.unpack(">Q", raw)[0]
        elif size == 0:
            size = end - begin
        if size < 8:
            return
        stop = min(end, begin + size)
        yield kind, f.tell(), stop
        f.seek(stop)


def _read_colr_atom(f, end, depth=0):
    if depth > 8:
        return None
    for kind, content, stop in _mov_atoms(f, end):
        if kind == b"colr":
            f.seek(content)
            raw = f.read(min(19, stop - content))
            if len(raw) >= 10 and raw[:4] in (b"nclc", b"nclx"):
                prim, trc, mat = struct.unpack(">HHH", raw[4:10])
                full = (bool(raw[10] & 0x80)
                        if raw[:4] == b"nclx" and len(raw) >= 11 else None)
                return prim, trc, mat, full
            continue
        if kind in MOV_CONTAINERS:
            f.seek(content)
            hit = _read_colr_atom(f, stop, depth + 1)
            if hit:
                return hit
        elif kind == b"stsd":
            # Version, flags, count, then the entries.
            f.seek(content + 8)
            for _kind2, content2, end2 in _mov_atoms(f, stop):
                # Video entry: 78 bytes of fixed header, then sub-atoms.
                if end2 - content2 <= 78:
                    continue
                f.seek(content2 + 78)
                hit = _read_colr_atom(f, end2, depth + 1)
                if hit:
                    return hit
    return None


def colour_arguments(source, extend=False):
    """Pass the source colour tags through explicitly.

    With -c:v copy ffmpeg rewrites the colr box from its own values and
    replaces anything it does not know, so Resolve no longer recognises
    the input colour space. With fill_gaps=True one gap some cameras
    leave is closed: a BT.2020 matrix with unspecified primaries makes
    the primaries BT.2020 too. Nothing is invented.
    """
    values = mov_colour_tags(source)
    if not values:
        return []
    prim, trc, mat, full = values
    if extend and prim == 2 and mat == PROGRAM.MATRIX_BT2020:
        prim = PROGRAM.PRIMARIES_BT2020
    opts = ["-color_primaries", str(prim), "-color_trc", str(trc),
          "-colorspace", str(mat)]
    if full is not None:
        opts += ["-color_range", "pc" if full else "tv"]
    return opts


def camera_metadata(file_path):
    """Read the camera's QuickTime metadata keys.

    They name the device and app used. Resolve reads them; without them
    it cannot tell that a phone recorded in log, because the colr box of
    those files reports the transfer function as unspecified. Only the
    com. keys, because these have to reach the new file unchanged, and a
    plain key such as encoder is rewritten by whatever wrote it.
    """
    try:
        d = ffprobe_json(file_path)
    except Exception:
        return {}
    tags = ((d or {}).get("format") or {}).get("tags") or {}
    return {k: v for k, v in tags.items() if k.startswith("com.")}


# The one data track ffmpeg writes whole. mebx -- what an iPhone writes
# -- and camm, rtmd and fdsc arrive with an empty sample description.
# And never tmcd: ffmpeg then drops the timecode this program worked
# out, and the camera lands in the wrong place on the common axis.
DATA_TAGS_TO_KEEP = ("gpmd",)


def data_track_tags(file_path):
    """The tags of the file's data tracks, in the order ffprobe gives them."""
    try:
        d = ffprobe_json(file_path)
    except Exception:
        return []
    return [(s.get("codec_tag_string") or "?").strip()
            for s in (d or {}).get("streams", [])
            if s.get("codec_type") == "data"]


def data_track_maps(file_path):
    """The -map arguments for the data tracks that may be carried over."""
    out = []
    for i, tag in enumerate(data_track_tags(file_path)):
        if tag in DATA_TAGS_TO_KEEP:
            out += ["-map", "0:d:%d" % i]
    return out


def check_data_tracks(source, target):
    """Report which of the camera's data tracks reached the new file.

    The timecode track is not counted: this program writes one of its
    own, so it is replaced rather than lost.
    """
    a = [t for t in data_track_tags(source) if t != "tmcd"]
    if not a:
        return
    b = data_track_tags(target)
    kept = [t for t in a if t in b]
    left = [t for t in a if t not in DATA_TAGS_TO_KEEP]
    if left:
        print(as_warn(T('  Data tracks:     %s left out -- ffmpeg cannot '
                        'write it') % ", ".join(left)))
    if kept:
        print(T('  Data tracks:     %s carried over') % ", ".join(kept))


# What the container says about itself and who wrote it. Every rewrite
# moves these, and none of them came off a camera, so counting them
# would claim camera data the camera never wrote.
CONTAINER_TAGS = ("major_brand", "minor_version", "compatible_brands",
                  "encoder")


def file_metadata(file_path):
    """Every metadata key of the file, minus what the container owns."""
    try:
        d = ffprobe_json(file_path)
    except Exception:
        return {}
    tags = ((d or {}).get("format") or {}).get("tags") or {}
    return {k: v for k, v in tags.items() if k.lower() not in CONTAINER_TAGS}


def check_camera_metadata(source, target):
    """Report whether the camera metadata keys survived the copy.

    Every key the source carries, not only the Apple ones: a camera
    writing none of those used to get no line at all. Presence is
    compared and not the value, because some values change on purpose
    -- the timecode is worked out afresh -- and a check reading those
    as a loss would cry wolf on every run.
    """
    a, b = file_metadata(source), file_metadata(target)
    if not a:
        print(T('  Camera data:     the source carries none'))
        return
    missing = [k for k in a if k not in b]
    if not missing:
        print(T('  Camera data:     %s keys carried over (%s)')
              % (group_text(len(a)), a.get("com.apple.quicktime.model")
                 or a.get("model")
                 or a.get("com.apple.quicktime.software") or "..."))
    else:
        print(as_warn(T('  Camera data:     Caution, %s of %s keys are '
                        'missing in the new file: %s')
                      % (group_text(len(missing)), group_text(len(a)),
                         ", ".join(missing[:4]))))
        print(T('                   Resolve may then not recognise the '
                'input colour space.'))


# Atoms in the sample description that ffmpeg drops when copying but
# Resolve reads. For iPhone recordings "logs" holds the recording
# curve, e.g. "com.apple.apple-wide-gamut.apple-log", which is how
# Resolve recognises Apple Log 2. The colr box says nothing about it.

# "gama" is the curve of older QuickTime recordings, "dvcC" and "dvvC"
# the Dolby Vision set. Not "st3d": ffmpeg writes a vexu box of its own
# beside it, and the two together make a file nothing will open, while
# every check in copy_mov_atoms passes.
ATOMS_TO_COPY = (b"logs", b"gama", b"dvcC", b"dvvC")


def _atom_boxes(data, start, end):
    """Return the boxes of one MOV level.

    Yields (start, size, kind, header length) per box.
    """
    i = start
    while i + 8 <= end:
        size = struct.unpack(">I", data[i:i + 4])[0]
        kind = data[i + 4:i + 8]
        head = 8
        if size == 1:
            if i + 16 > end:
                return
            size = struct.unpack(">Q", data[i + 8:i + 16])[0]
            head = 16
        elif size == 0:
            size = end - i
        if size < head or i + size > end:
            return
        yield i, size, kind, head
        i += size


def _find_atom(data, start, end, kind):
    for i, size, a, head in _atom_boxes(data, start, end):
        if a == kind:
            return i, size, head
    return None


def _video_track_chain(data, moov_i, moov_size, moov_head):
    """Return the video trak box and the chain down to its sample entry."""
    for t_i, t_size, t_kind, t_head in _atom_boxes(data, moov_i + moov_head,
                                           moov_i + moov_size):
        if t_kind != b"trak":
            continue
        mdia = _find_atom(data, t_i + t_head, t_i + t_size, b"mdia")
        if not mdia:
            continue
        hdlr = _find_atom(data, mdia[0] + mdia[2], mdia[0] + mdia[1],
                           b"hdlr")
        # hdlr: four bytes version and flags, four reserved, then the kind
        # of track.
        if not hdlr or data[hdlr[0] + hdlr[2] + 8:
                             hdlr[0] + hdlr[2] + 12] != b"vide":
            continue
        minf = _find_atom(data, mdia[0] + mdia[2], mdia[0] + mdia[1],
                           b"minf")
        if not minf:
            continue
        stbl = _find_atom(data, minf[0] + minf[2], minf[0] + minf[1],
                           b"stbl")
        if not stbl:
            continue
        stsd = _find_atom(data, stbl[0] + stbl[2], stbl[0] + stbl[1],
                           b"stsd")
        if not stsd:
            continue
        # In stsd: four bytes version/flags, four bytes count, then entries.
        entry = next(_atom_boxes(data, stsd[0] + stsd[2] + 8,
                              stsd[0] + stsd[1]), None)
        if not entry:
            continue
        return [(moov_i, moov_head), (t_i, t_head), (mdia[0], mdia[2]),
                (minf[0], minf[2]), (stbl[0], stbl[2]), (stsd[0], stsd[2]),
                (entry[0], entry[3])]
    return None


def _top_level_boxes(file_path):
    out = []
    total = os.path.getsize(file_path)
    with open(file_path, "rb") as f:
        pos = 0
        while pos < total - 8:
            f.seek(pos)
            head = f.read(8)
            if len(head) < 8:
                break
            size, kind = struct.unpack(">I4s", head)
            if size == 1:
                size = struct.unpack(">Q", f.read(8))[0]
            elif size == 0:
                size = total - pos
            if size < 8:
                break
            out.append((kind, pos, size))
            pos += size
    return out


# A sample description atom is an identifier, not a payload. Anything
# larger is left alone, because then the assumption no longer holds.
ATOM_LIMIT = 64 * 1024


def _verify_mov_after_edit(file_path, moov_pos, moov_old_size, above_before_value, for_it):
    """Verify the file survived the edit. An empty result means it did.

    Checked against the state before: same top level boxes at the same
    offsets, moov still last and reaching the end of file, the chain down to
    the video sample entry readable again, and the intended atoms present.
    """
    try:
        total = os.path.getsize(file_path)
        above = _top_level_boxes(file_path)
        if not above:
            return T('boxes no longer readable')
        if above[-1][0] != b"moov" or above[-1][1] != moov_pos:
            return T('moov is no longer in its place')
        if above[-1][1] + above[-1][2] != total:
            return T('moov no longer ends at the end of the file')
        if [(a, i, g) for a, i, g in above[:-1]] != \
                [(a, i, g) for a, i, g in above_before_value[:-1]]:
            return T('the media data is no longer where it was')
        if above[-1][2] <= moov_old_size:
            return T('moov has not grown')
        with open(file_path, "rb") as f:
            f.seek(above[-1][1])
            moov = f.read(above[-1][2])
        chain = _video_track_chain(moov, 0, len(moov), 8)
        if not chain:
            return T('the video track can no longer be found')
        e_i, e_head = chain[-1]
        e_size = struct.unpack(">I", moov[e_i:e_i + 4])[0]
        present = {bytes(a) for _i, _g, a, _k
                in _atom_boxes(moov, e_i + e_head + 78, e_i + e_size)}
        missing = [a.decode("latin1") for a in for_it if a not in present]
        if missing:
            return T('did not arrive: %s') % ", ".join(missing)
        # Every level has to fit exactly inside its parent, otherwise some
        # size field is wrong.
        for idx in range(len(chain) - 1):
            i, head = chain[idx]
            size = struct.unpack(">I", moov[i:i + 4])[0]
            kind_i, kind_head = chain[idx + 1]
            kind_size = struct.unpack(">I", moov[kind_i:kind_i + 4])[0]
            if not (i + head <= kind_i and kind_i + kind_size <= i + size):
                return T('a box no longer fits into its parent')
    except Exception as e:
        return T('cannot be read back (%s)') % str(e)[:60]
    return ""


def copy_mov_atoms(source, target, kinds=ATOMS_TO_COPY):
    """Copy sample description atoms from the source into the new file.

    Copied byte for byte, nothing synthesised, and only where moov sits
    at the end of the target: growing it then moves no media data and
    every offset stays valid. The result is verified and the old moov
    put back on any mismatch -- better without the atom than with a file
    nothing will open. Returns the atoms copied, [] where none were.
    """
    # Folders, missing paths and empty names occur here, and copying
    # atoms is a side step: they end it quietly rather than raise.
    for file_path in (source, target):
        if not file_path or not os.path.isfile(file_path):
            return []
    absent = []
    src_top = _top_level_boxes(source)
    src_moov = next(((p, g) for a, p, g in src_top if a == b"moov"), None)
    if not src_moov:
        return []
    with open(source, "rb") as f:
        f.seek(src_moov[0])
        src = f.read(src_moov[1])
    chain = _video_track_chain(src, 0, len(src), 8)
    if not chain:
        return []
    e_i, e_head = chain[-1]
    e_size = struct.unpack(">I", src[e_i:e_i + 4])[0]
    src_kind = bytes(src[e_i + 4:e_i + 8])       # hvc1, avc1, apcn ...
    existing = {}
    # The sub-atoms sit behind the box header and 78 bytes of fixed
    # fields of the video entry.
    for i, size, kind, head in _atom_boxes(src, e_i + e_head + 78,
                                   e_i + e_size):
        if kind not in kinds:
            continue
        if size > ATOM_LIMIT:
            print(T('  Atom %s skipped: %s bytes are too much for it.')
                  % (kind.decode("latin1"), group_text(size)))
            continue
        existing[kind] = src[i:i + size]
    if not existing:
        return []

    dst_top = _top_level_boxes(target)
    if not dst_top or dst_top[-1][0] != b"moov":
        print(T('  Cannot add atoms: moov is not at the end.'))
        return []
    dst_pos, dst_size = dst_top[-1][1], dst_top[-1][2]
    with open(target, "rb") as f:
        f.seek(dst_pos)
        dst = bytearray(f.read(dst_size))
    if len(dst) != dst_size:
        return []
    # The old moov stays in place: if the verification fails, it comes
    # back exactly as it was.
    old_moov = bytes(dst)
    chain = _video_track_chain(dst, 0, len(dst), 8)
    if not chain:
        return []
    e_i, e_head = chain[-1]
    e_size = struct.unpack(">I", dst[e_i:e_i + 4])[0]
    dst_kind = bytes(dst[e_i + 4:e_i + 8])
    if dst_kind != src_kind:
        # An atom from an HEVC description does not belong in an H.264 one.
        # The boxes fit, the contents do not.
        print(T('  Cannot add atoms: the source is %s, the target %s.') % (src_kind.decode("latin1", "replace"),
                       dst_kind.decode("latin1", "replace")))
        return []
    already = {bytes(kind) for _i, _g, kind, _k
             in _atom_boxes(dst, e_i + e_head + 78, e_i + e_size)}
    fresh = b"".join(v for k, v in existing.items() if k not in already)
    if not fresh:
        return []
    # Every box enclosing the entry grows.
    for i, _head in chain:
        size = struct.unpack(">I", dst[i:i + 4])[0]
        if size == 1:
            print(T('  Cannot add atoms: a 64 bit box is in the way.'))
            return []
        struct.pack_into(">I", dst, i, size + len(fresh))
    insert = e_i + e_size

    def moov_write(content):
        with open(target, "r+b") as f:
            f.seek(dst_pos)
            f.write(content)
            f.truncate(dst_pos + len(content))
            f.flush()
            os.fsync(f.fileno())

    for_it = [k for k in existing if k not in already]
    try:
        moov_write(bytes(dst[:insert]) + fresh + bytes(dst[insert:]))
        damage = _verify_mov_after_edit(target, dst_pos, dst_size, dst_top, for_it)
    except Exception as e:
        damage = T('while writing: %s') % str(e)[:60]
    if damage:
        try:
            moov_write(old_moov)
            back = T('the old moov is back in place')
        except Exception as e:
            back = T('ROLLBACK FAILED (%s)') % str(e)[:60]
        print(T('  Adding atoms taken back -- %s. %s')
              % (damage, back))
        return []
    return [k.decode("latin1") for k in for_it]


def _logs_atom_text(file_path):
    """Return the text of the video track logs atom, or ""."""
    try:
        above = _top_level_boxes(file_path)
        spot = next(((p, g) for a, p, g in above if a == b"moov"), None)
        if not spot:
            return ""
        with open(file_path, "rb") as f:
            f.seek(spot[0])
            moov = f.read(spot[1])
        chain = _video_track_chain(moov, 0, len(moov), 8)
        if not chain:
            return ""
        e_i, e_head = chain[-1]
        e_size = struct.unpack(">I", moov[e_i:e_i + 4])[0]
        for i, size, kind, head in _atom_boxes(moov, e_i + e_head + 78, e_i + e_size):
            if kind == b"logs":
                return moov[i + head:i + size].decode("latin1", "replace")
    except Exception:
        pass
    return ""


# The atom holds a reverse domain name whose middle piece is the colour
# space; no digit anywhere says which of the two curves it is.
LOG_ATOM_NAMES = {"com.apple.rec2020.apple-log": "Apple Log (Rec.2020)",
                  "com.apple.apple-wide-gamut.apple-log":
                      "Apple Log 2 (Apple Wide Gamut)"}


def log_curve_from_atom(text):
    """Return the recording curve named by the logs atom.

    The name carries the colour space too: the same curve is recorded in
    two of them, and a table built for one lays the wrong space on the
    other. Known identifiers get a plain name, anything else is shown
    verbatim -- an unknown identifier is information, an invented name
    would not be.
    """
    raw = (text or "").replace("\x00", " ").strip()
    if not raw:
        return ""
    return LOG_ATOM_NAMES.get(raw.lower(), raw)


def check_colour_survived(source, target, extend=False):
    """Report whether the written file carries the intended colour tags.

    Compared against the intended values, not against the source: missing
    primaries are filled in from the matrix, so the box is meant to differ.
    """
    a, b = mov_colour_tags(source), mov_colour_tags(target)
    if a is None and b is None:
        return
    want = a
    if a and extend and a[0] == 2 and a[2] == PROGRAM.MATRIX_BT2020:
        want = (PROGRAM.PRIMARIES_BT2020,) + tuple(a[1:])
    if b == want and want != a:
        print(T('  Colour:          %d/%d/%d -- primaries filled in from '
                'the matrix (source: %d)') % (want[0], want[1], want[2], a[0]))
        return
    if a == b:
        print(T('  Colour:          %d/%d/%d carried over') % a[:3])
        return
    print(as_warn(T('  Colour:          Caution, %s in the source, %s in '
                    'the new file') % (a[:3] if a else T('nothing'), b[:3] if b else T('nothing'))))
    print(T('                   Resolve may then not recognise the input '
            'colour space.'))


def mov_colour_tags(file_path):
    """Read the colr box of a MOV file.

    Returns (primaries, transfer, matrix, full range) or None. ffprobe
    is not used: it reports names rather than numbers and names a wrong
    one for values it does not know, Apple Log among them. Only the atom
    tree is walked, so a huge recording is skipped over rather than read.
    """
    try:
        size = os.path.getsize(file_path)
        with open(file_path, "rb") as f:
            return _read_colr_atom(f, size)
    except (OSError, struct.error):
        return None


def video_summary(file_path, info):
    v = info["video"]
    tags = info.get("tags") or {}
    # The nominal rate comes first: editors use it. The measured one
    # beside it where it differs -- frame count over track duration, so a
    # property of the container.
    label_text, measured = info.get("nominal") or info["fps"], info["fps"]
    lines = [("Video", "%s, %sx%s, %s fps%s%s"
               % (v.get("codec_name", "?"), v.get("width"), v.get("height"),
                  decimal_text("%.3f" % label_text),
                  "" if abs(measured - label_text) < 0.0005
                  else T('  (container; measured %s)')
                  % decimal_text("%.4f" % measured),
                  "" if PROGRAM.known_frame_rate(
                      PROGRAM.file_frame_rate(info))
                  else T('  --  no Resolve Timeline runs at this rate; '
                         'it is converted'))),
              (T('Length'), "%s  (%s)  --  %s"
               % (as_hms(info["duration"]), as_data_size(size_in_mb(file_path)),
                  "Timecode %s" % info["tc"] if info["tc"]
                  else T('no timecode'))),
              (T('Colour'), PROGRAM.colour_text(file_path, v, tags)),
              (T('Camera'), PROGRAM.camera_text(tags))]
    if info["audio"]:
        a = info["audio"][0]
        channels = channel_text(a.get("channels"))
        count = len(info["audio"])
        lines.append((T('Camera audio'),
                      TN(count, '%s track, %s, %s Hz, %s',
                         '%s tracks, %s, %s Hz, %s')
                      % (group_text(count), a.get("codec_name", "?"),
                         a.get("sample_rate", "?"), channels)))
    else:
        lines.append((T('Camera audio'), T('no audio track present')))
    return lines


def print_key_values(lines, indent="  "):
    # The column follows the longest label, so it holds in every language.
    width = max([len(k) for k, _ in lines] or [9]) + 1
    for k, value in lines:
        print("%s%-*s %s" % (indent, width, k + ":", value))


def print_audio_details(file_path, indent="  "):
    print_key_values(audio_summary(file_path), indent)


def print_video_details(file_path, info, indent="  "):
    print_key_values(video_summary(file_path, info), indent)


def open_in_file_manager(file_path):
    """Show a folder in Finder, Explorer or the desktop file manager."""
    folder = file_path if os.path.isdir(file_path) else os.path.dirname(file_path)
    try:
        if sys.platform == "darwin":
            if os.path.isdir(file_path):
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["open", "-R", file_path])
        elif os.name == "nt":
            if os.path.isdir(file_path):
                os.startfile(folder)
            else:
                # The switch and the path have to be one single argument,
                # otherwise Explorer opens the documents folder.
                subprocess.Popen('explorer /select,"%s"'
                                 % os.path.normpath(file_path))
        else:
            subprocess.Popen(["xdg-open", folder])
        return True
    except Exception:
        return False


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
