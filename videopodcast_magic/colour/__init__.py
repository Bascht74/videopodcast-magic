# -*- coding: utf-8 -*-
"""What a video file says about its colour, and whether it is HDR.

A piece of the program, read in by beside(): it cannot import the file
it was cut out of, so the program is handed in and bound below by name.
"""

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# Bound above the seam, so each is a copy and none is read late.
Finding = PROGRAM.Finding
T = PROGRAM.T
TN = PROGRAM.TN
_logs_atom_text = PROGRAM._logs_atom_text
camera_metadata = PROGRAM.camera_metadata
ffprobe_json = PROGRAM.ffprobe_json
json = PROGRAM.json
log_curve_from_atom = PROGRAM.log_curve_from_atom
mov_colour_tags = PROGRAM.mov_colour_tags
number_text = PROGRAM.number_text
os = PROGRAM.os
subprocess = PROGRAM.subprocess
textwrap = PROGRAM.textwrap


# Transfer characteristic codes per ITU-T H.273. 16 is PQ, 18 is HLG, both HDR
# markers. 9 as colour space is BT.2020.
TRC_HDR = {16: "PQ", 18: "HLG"}
# Log is a recording curve, not a display one: it keeps the range the
# camera sees. For output that means the same as HDR -- eight bit bands.
TRC_LOG = {21: "Apple Log"}
PRIMARIES_BT2020 = 9
# Another way to spot log: the cameras write it into their QuickTime keys.
# Searched by word markers, not by "log", which hides in harmless words.
LOG_MARKERS = ("apple log", "applelog", "s-log", "slog", "v-log", "vlog",
              "log3", "logc", "c-log", "clog", "f-log", "flog",
              "blackmagic design film", "bmd film", "arri logc",
              "redlogfilm", "log gamma")


def _marker_stands_alone(hay, label):
    """Say whether a marker is a word of its own, not a piece of one.

    A version digit may follow it -- slog3, logc4 -- a letter may not,
    or the word "Vlogger" would name a recording curve.
    """
    at = hay.find(label)
    while at >= 0:
        after = hay[at + len(label):at + len(label) + 1]
        if (not (at and hay[at - 1].isalnum())
                and (after.isdigit() or not after.isalnum())):
            return True
        at = hay.find(label, at + 1)
    return False


# Names for the ITU-T H.273 codes. Anything not listed is shown as a
# number rather than guessed. 2 means "unspecified": nothing is said.
PRIMARIES_NAMES = {0: 'reserved', 1: "BT.709", 2: 'unspecified',
                   4: "BT.470 M", 5: "BT.470 B/G", 6: "BT.601 (SMPTE 170M)",
                   7: "SMPTE 240M", 8: "Film", 9: "BT.2020", 10: "XYZ",
                   11: "DCI-P3", 12: "Display P3", 22: "EBU 3213-E"}
MATRIX_NAMES = {0: "GBR", 1: "BT.709", 2: 'unspecified', 4: "FCC",
                5: "BT.470 B/G", 6: "BT.601 (SMPTE 170M)", 7: "SMPTE 240M",
                8: "YCgCo", 9: "BT.2020", 10: 'BT.2020 constant',
                11: "SMPTE ST 2085", 14: "ICtCp"}
MATRIX_BT2020 = 9
TRC_NAMES = {0: 'reserved', 1: "BT.709", 2: 'unspecified',
             4: "Gamma 2.2", 5: "Gamma 2.8", 6: "BT.601 (SMPTE 170M)",
             7: "SMPTE 240M", 8: "linear", 11: "xvYCC", 13: "sRGB",
             14: "BT.2020 10 bit", 15: "BT.2020 12 bit", 16: "PQ (HDR10)",
             17: "SMPTE ST 428-1", 18: "HLG", 21: "Apple Log"}


def _log_in_colour_tags(tags):
    """Report whether the colour tags say the source was recorded in log."""
    for api_key, value in (tags or {}).items():
        if not str(api_key).startswith("com."):
            continue
        hay = ("%s %s" % (api_key, value)).lower()
        for label in LOG_MARKERS:
            if _marker_stands_alone(hay, label):
                return "%s = %s" % (api_key, value)
    return ""


def _log_gamma_in_metadata(file_path):
    """Report whether the camera metadata says log was recorded."""
    try:
        return _log_in_colour_tags(camera_metadata(file_path))
    except Exception:
        return ""


def bit_depth(v):
    """Return the bits per colour channel of the video track."""
    n = v.get("bits_per_raw_sample")
    if n:
        try:
            return int(n)
        except (TypeError, ValueError):
            pass
    fmt = str(v.get("pix_fmt") or "")
    for k in (16, 14, 12, 10):
        if "p%d" % k in fmt:
            return k
    return 8 if fmt else 0


def colour_text(file_path, v, tags):
    """Describe colour space, curve and bit depth of a video file in one line.

    The numbers come from the colr box, not from ffprobe's names: for Apple
    Log ffprobe reports a curve that is wrong.
    """
    values = mov_colour_tags(file_path)
    # Apple writes the recording curve into the logs atom, not into the
    # colr box, and that is the only way Apple Log shows.
    curve = log_curve_from_atom(_logs_atom_text(file_path))
    parts, hdr = [], bool(curve)
    if curve:
        parts.append(curve)
    if values:
        prim, trc, mat, full = values
        if trc != 2:
            parts.append(T(TRC_NAMES.get(trc, ''))
                         or T('Curve number %d') % trc)
        if prim != 2:
            parts.append(PRIMARIES_NAMES.get(prim,
                                             T('Primaries number %d') % prim))
        # Where the matrix says the same as the primaries, once is enough.
        if (mat and mat != 2
                and MATRIX_NAMES.get(mat) != PRIMARIES_NAMES.get(prim)):
            parts.append(T('Matrix %s')
                         % MATRIX_NAMES.get(mat, T('Number %d') % mat))
        if not parts:
            parts.append(T('Curve and colour space are missing from the file'))
        # The matrix counts too: some cameras write only that, and
        # BT.2020 as a matrix still states the range of the material.
        hdr = hdr or (trc in TRC_HDR or trc in TRC_LOG
                      or prim == PRIMARIES_BT2020 or mat == MATRIX_BT2020)
        if full:
            parts.append(T('full range'))
    else:
        for api_key in ("color_transfer", "color_primaries"):
            if v.get(api_key):
                parts.append(str(v[api_key]))
    n = bit_depth(v)
    if n:
        parts.append(T('%d bit') % n)
    source_text = _log_in_colour_tags(tags)
    if source_text and not hdr:
        parts.append(T('Log according to camera data'))
        hdr = True
    if hdr:
        parts.append("HDR")
    return ", ".join(parts) if parts else T('no information in the file')


def camera_text(tags):
    """Return the device and recording app, as far as the file names them."""
    d = {}
    for api_key, value in sorted((tags or {}).items()):
        short = str(api_key).rsplit(".", 1)[-1].lower()
        if (short in ("make", "model", "software", "firmware", "encoder")
                and str(value).strip()):
            d.setdefault(short, str(value).strip())
    maker, model = d.get("make", ""), d.get("model", "")
    if model.lower().startswith(maker.lower()) and maker:
        device = model           # some write the manufacturer into it as well
    else:
        device = " ".join(x for x in (maker, model) if x)
    # Some cameras put their own name in "encoder" and in no other key.
    software = d.get("software") or d.get("firmware") or d.get("encoder") or ""
    if device and software:
        return T('%s  --  Software %s') % (device, software)
    return device or software or T('no information in the file')


# What a finished file has to carry for a player to recognise HDR -- the ITU-T
# H.273 codes. 9 as primaries is BT.2020, 16 is PQ, 18 is HLG, 9 as matrix is
# BT.2020 non-constant luminance. 14 looks similar but is SDR and does not.
HDR_PRIMARIES = 9
HDR_MATRIX = 9
HDR_CURVES = {16: "PQ (HDR10)", 18: "HLG"}


def hdr_static_metadata(file_path):
    """Return which HDR static metadata a file carries.

    ffprobe attaches mastering display and content light level to the
    first frame rather than to the stream, so the first frame is what
    gets queried. Returns the set of kinds found.
    """
    try:
        raw = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-read_intervals", "%+#1", "-show_frames",
             "-show_entries", "frame=side_data_list",
             "-print_format", "json", file_path],
            capture_output=True).stdout
        d = json.loads(raw or b"{}")
    except Exception:
        return set()
    out = set()
    for video in (d.get("frames") or []):
        for part in (video.get("side_data_list") or []):
            kind = str(part.get("side_data_type") or "").lower()
            if "mastering display" in kind:
                out.add("mdcv")
            elif "content light" in kind:
                out.add("clli")
    return out


def hdr_findings(file_path):
    """Check whether a finished file carries everything that marks it HDR.

    Checked against the file, not against the intent: primaries, curve,
    matrix and bit depth. Returns a list of Finding.
    """
    out = []
    if not file_path or not os.path.isfile(file_path):
        return [Finding("abort", T('File'), T('does not exist: %s') % file_path)]
    values = mov_colour_tags(file_path)
    if not values:
        out.append(Finding(
            "abort", T('colr box'),
            T('missing -- the container carries no colour tagging'),
            T('Without it every player has to guess, and all guess SDR. In '
              'Resolve under Deliver > Advanced Settings set the Color '
              'space tag and the Gamma tag instead of leaving them at '
              '"Same as Project".')))
        prim = trc = mat = None
    else:
        prim, trc, mat, full = values
        out.append(Finding(
            "good" if prim == HDR_PRIMARIES else "hint", T('Primaries'),
            "%d (%s)" % (prim, T(PRIMARIES_NAMES.get(prim, 'unknown'))),
            "" if prim == HDR_PRIMARIES else
            T('HDR needs 9 here (BT.2020). In Resolve: Color space tag = '
              'Rec.2020.')))
        out.append(Finding(
            "good" if trc in HDR_CURVES else "hint", T('Curve'),
            "%d (%s)" % (trc, HDR_CURVES.get(trc)
                         or T(TRC_NAMES.get(trc, 'unknown'))),
            "" if trc in HDR_CURVES else
            T('HDR needs 16 here (PQ, that is HDR10) or 18 (HLG). In '
              'Resolve: Gamma tag = ST.2084 or HLG. 14 is not an HDR curve '
              'but SDR in the BT.2020 space.')))
        out.append(Finding(
            "good" if mat == HDR_MATRIX else "hint", "Matrix",
            "%d (%s)" % (mat, T(MATRIX_NAMES.get(mat, 'unknown'))),
            "" if mat == HDR_MATRIX else
            T('HDR needs 9 here (BT.2020, non-constant luminance).')))
        if full is not None:
            out.append(Finding(
                "good", T('Value range'),
                T('full range') if full else T('limited (Video/TV)'),
                "" if not full else
                T('Delivery usually takes the limited range. Full is not '
                  'wrong, but some players misread it.')))
    try:
        d = ffprobe_json(file_path)
    except Exception:
        d = {}
    track = next((x for x in (d.get("streams") or [])
                 if x.get("codec_type") == "video"), {})
    depth = bit_depth(track)
    out.append(Finding(
        "good" if depth >= 10 else "abort", T('Bit depth'),
        T('%d bit') % depth if depth
        else T('%d bit -- not readable') % depth,
        "" if depth >= 10 else
        T('Eight bits are not enough for HDR: every gradient bands, and '
          'YouTube requires ten or twelve.')))
    codec = str(track.get("codec_name") or "").lower()
    profile = str(track.get("profile") or "")
    if codec in ("hevc", "h265"):
        out.append(Finding(
            "good" if "10" in profile else "hint", T('Codec profile'),
            "%s %s" % (codec.upper(), profile or "?"),
            "" if "10" in profile else
            T('For ten bits HEVC needs the Main 10 profile. In Resolve it '
              'sits under Deliver as "Profile".')))
    elif codec:
        out.append(Finding(
            "hint" if depth < 10 else "good", T('Codec'),
            "%s %s" % (codec.upper(), profile),
            T('For HDR the usual choice is HEVC (Main 10), AV1 or VP9 '
              'Profile 2. YouTube takes H.264 too, but it needs more '
              'bitrate.')))
    static_meta = hdr_static_metadata(file_path)
    if trc == 18:
        out.append(Finding(
            "good", T('Static metadata'),
            T('not needed with HLG'),
            T('HLG is display-referred -- it has no entry for the '
              'mastering display.')))
    else:
        missing = [n for n, k in (("Mastering-Display (ST 2086)", "mdcv"),
                                ("MaxCLL/MaxFALL", "clli")) if k not in static_meta]
        out.append(Finding(
            "good" if not missing else "hint", T('Static metadata'),
            T('complete') if not missing else T('missing: %s') % ", ".join(missing),
            "" if not missing else
            T('Not mandatory -- YouTube then applies default values (Sony '
              'BVM-X300). To get them: in Resolve switch on HDR10+ under '
              'Color Management, run "Analyze All Shots" on the Color page '
              'and tick "Embed HDR10 Metadata" when rendering.')))
    return out


def check_hdr(file_path):
    """Print the HDR report for a finished file. 0 means everything is fine."""
    print(T('\nHDR CHECK  %s') % os.path.basename(file_path))
    findings = hdr_findings(file_path)
    for b in findings:
        print(b.line(20))
        if b.kind != "good" and b.advice:
            for line in textwrap.wrap(b.advice, 74):
                print("      %s" % line)
    serious = [b for b in findings if b.kind == "abort"]
    hints = [b for b in findings if b.kind == "hint"]
    curve = next((b for b in findings if b.field == T('Curve')), None)
    have_hdr = bool(curve and curve.kind == "good") and not serious
    print("\n  %s" % (
        T('The file is tagged as HDR.') if have_hdr and not hints
        else TN(len(hints), 'The file is tagged as HDR, with %s note.',
                'The file is tagged as HDR, with %s notes.')
        % number_text(len(hints), 0) if have_hdr
        else T('The file is NOT recognised as HDR.')))
    return 0 if have_hdr else 1


def hdr_from_sources(video_paths):
    """Report whether the source material is HDR. Returns (yes, reason).

    The colr box is read, not guessed: PQ or HLG, log (flat ungraded but
    carrying the full range, and it bands in eight bit), or BT.2020. The
    reason stays English -- it goes into a file.
    """
    for file_path in video_paths or []:
        name = os.path.basename(file_path)
        values = mov_colour_tags(file_path)
        if values:
            prim, trc, _mat, _full = values
            if trc in TRC_HDR:
                return True, ("transfer function %d (%s) in %s"
                              % (trc, TRC_HDR[trc], name))
            if trc in TRC_LOG:
                return True, ("transfer function %d (%s) in %s"
                              % (trc, TRC_LOG[trc], name))
            if prim == PRIMARIES_BT2020:
                return True, ("BT.2020 in %s" % name)
            if _mat == MATRIX_BT2020:
                return True, ("BT.2020 as matrix in %s" % name)
        # Where the colr box says nothing usable, the QuickTime keys do.
        source_text = _log_gamma_in_metadata(file_path)
        if source_text:
            return True, ("log according to camera data: %s (%s)"
                          % (source_text[:60], name))
    return False, ""
