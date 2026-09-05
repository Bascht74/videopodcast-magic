# -*- coding: utf-8 -*-
"""The project in DaVinci Resolve: timelines, colour, render, markers.

A piece of the program, read out of the folder beside it by beside().
It cannot import the file it was cut out of, because that file is
still being read while this one is; the program is handed in instead,
and every name this piece uses out of it is bound below, by name, so
that nothing in here comes from nowhere.
"""

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

# What the program has and this piece uses, bound once so that the
# project building reads as it did in the one file. Not one of them is
# a name the program rebinds while it runs, so none of them has to
# stay PROGRAM.something the way a few of the window's do.
ByFile = PROGRAM.ByFile
Finding = PROGRAM.Finding
HINT_MULTICAM = PROGRAM.HINT_MULTICAM
SR = PROGRAM.SR
T = PROGRAM.T
TN = PROGRAM.TN
TYPE_INTRO = PROGRAM.TYPE_INTRO
TYPE_OUTRO = PROGRAM.TYPE_OUTRO
_logs_atom_text = PROGRAM._logs_atom_text
_meeting_point = PROGRAM._meeting_point
as_bad = PROGRAM.as_bad
as_head = PROGRAM.as_head
as_hms = PROGRAM.as_hms
as_warn = PROGRAM.as_warn
ask_choice = PROGRAM.ask_choice
camera_metadata = PROGRAM.camera_metadata
decimal_text = PROGRAM.decimal_text
ffprobe_json = PROGRAM.ffprobe_json
first_and_last_word = PROGRAM.first_and_last_word
format_complaint = PROGRAM.format_complaint
group_text = PROGRAM.group_text
json = PROGRAM.json
label_of = PROGRAM.label_of
lead_in_offset = PROGRAM.lead_in_offset
log_curve_from_atom = PROGRAM.log_curve_from_atom
math = PROGRAM.math
mix_file_from_handover = PROGRAM.mix_file_from_handover
mov_colour_tags = PROGRAM.mov_colour_tags
os = PROGRAM.os
path_key = PROGRAM.path_key
refresh_cut_list = PROGRAM.refresh_cut_list
strip_marks = PROGRAM.strip_marks
subprocess = PROGRAM.subprocess
sys = PROGRAM.sys
textwrap = PROGRAM.textwrap

# ------------------------------------------------------------ Resolve
#
# The scripting interface has no multicam: project, import, timelines,
# track names and markers can be driven remotely, converting to a
# multicam clip stays a right click. The track name becomes the angle
# name, and this whole part rests on that.

MARKER_COLOURS = ["Blue", "Cyan", "Green", "Yellow", "Red", "Pink", "Purple",
                 "Fuchsia", "Rose", "Lavender", "Sky", "Mint", "Lemon",
                 "Sand", "Cocoa", "Cream"]


def resolve_module_paths():
    """Return the possible locations of the Resolve scripting interface."""
    api = os.environ.get("RESOLVE_SCRIPT_API")
    lib = os.environ.get("RESOLVE_SCRIPT_LIB")
    if api and lib:
        return api, lib
    if sys.platform == "darwin":
        api = ("/Library/Application Support/Blackmagic Design/"
               "DaVinci Resolve/Developer/Scripting")
        for app in ("DaVinci Resolve", "DaVinci Resolve Studio"):
            lib = ("/Applications/DaVinci Resolve/%s.app/Contents/Libraries/"
                   "Fusion/fusionscript.so" % app)
            if os.path.exists(lib):
                return api, lib
        return api, lib
    if os.name == "nt":
        pd = os.environ.get("PROGRAMDATA", r"C:\ProgramData")
        pf = os.environ.get("PROGRAMFILES", r"C:\Program Files")
        return (os.path.join(pd, "Blackmagic Design", "DaVinci Resolve",
                             "Support", "Developer", "Scripting"),
                os.path.join(pf, "Blackmagic Design", "DaVinci Resolve",
                             "fusionscript.dll"))
    return ("/opt/resolve/Developer/Scripting",
            "/opt/resolve/libs/Fusion/fusionscript.so")


def resolve_installed():
    """Report whether Resolve is installed.

    Only the files are checked; this says nothing about whether the
    program is running. Enough to disable a control that would go nowhere.
    """
    api, lib = resolve_module_paths()
    return os.path.isdir(api) and os.path.exists(lib)


def connect_to_resolve():
    api, lib = resolve_module_paths()
    if not os.path.isdir(api) or not os.path.exists(lib):
        raise RuntimeError(T('The Resolve interface is not where I expect '
                             'it:\n  %s\n  %s') % (api, lib))
    os.environ["RESOLVE_SCRIPT_API"] = api
    os.environ["RESOLVE_SCRIPT_LIB"] = lib
    modules_path = os.path.join(api, "Modules")
    if modules_path not in sys.path:
        sys.path.append(modules_path)
    try:
        import DaVinciResolveScript as drs
    except ImportError as e:
        raise RuntimeError(T('Module DaVinciResolveScript cannot be loaded: %s') % e)
    r = drs.scriptapp("Resolve")
    if r is None:
        raise RuntimeError(
            T('No connection to Resolve.\n  Is the program running? Is '
              "external scripting set to 'Local'\n  under Preferences > "
              'System > General?'))
    return r


# Why the connection can fail. The third point is uncertain: a statement by
# Blackmagic that external scripting is reserved for the Studio edition appears
# neither in the interface README nor in the official documentation. It is
# reported for version 19.1 and later.
RESOLVE_REASONS = (
    ('Possible reasons:\n  1. Resolve is not running -- the interface '
     'answers only while the program runs.\n  2. Preferences > System > '
     'General: external scripting is set to "None" instead of "Local".\n  '
     '3. Free edition: external scripting is reported to be reserved for '
     'the Studio edition since version 19.1. I found no official '
     'statement -- this check measures it instead of claiming it.'))


def check_resolve():
    """Report what can be reached of Resolve. Returns (works, lines).

    In order: is the interface there, does the program answer, which edition
    is it, which project is open. Each stage reports separately, so the
    result says not just that it failed but how far it got.
    """
    api, lib = resolve_module_paths()
    lines = [T('Interface:      %s%s') % (api, "" if os.path.isdir(api)
                                        else T('   -- not found')),
              T('Library:        %s%s') % (lib, "" if os.path.exists(lib)
                                        else T('   -- not found'))]
    if not (os.path.isdir(api) and os.path.exists(lib)):
        return False, lines + ["", T('Without these two nothing works. Is '
                                     'Resolve installed?')]
    try:
        r = connect_to_resolve()
    except RuntimeError as e:
        return False, lines + ["", str(e), "", T(RESOLVE_REASONS)]

    def ask(how):
        try:
            return str(how()) or ""
        except Exception:
            return ""

    # Where it works, one bracket is enough. The paths only matter where it
    # does not.
    what = " ".join(x for x in (ask(r.GetProductName),
                               ask(r.GetVersionString)) if x)
    return True, [what]


def seconds_to_frames(seconds, fps):
    """Convert a duration to frames using the true rate; 29.97 stays 29.97."""
    return int(round(seconds * fps))


def frames_of_the_file(length, fps, own):
    """How many frames of a file fit into *length* frames of the Timeline.

    The most that fit and never one more, so a shot never runs into the
    next one: Resolve pushes what overlaps, and the pushes add up. What
    a shot leaves uncovered is picked up by the one after it, which
    begins that much earlier. One frame is the floor -- a shot shorter
    than a single frame of its file cannot be had.
    """
    # A whole number of frames that a division misses by a billionth is
    # that whole number: 23.976 in a 23.976 Timeline asked for one frame
    # more than the shot has, and pushed the next one along for nothing.
    return max(1, int(math.ceil((length + 1) * own / float(fps) - 1e-9)) - 1)


def timeline_frames_of(count, fps, own):
    """How many frames of the Timeline a span of *count* file frames fills.

    Resolve matches a foreign rate over the duration and keeps whole
    Timeline frames, so the last part frame does not count. Measured on
    21.0.4.5: 175 frames of a 24 file fill 218 frames of a 30 Timeline,
    176 fill 220 -- 219 is not reachable at all.
    """
    return int(count * fps / float(own) + 1e-9)


# Every rate Resolve offers a Timeline, and no other.
RESOLVE_FRAME_RATES = (16.0, 18.0, 23.976, 24.0, 25.0, 29.97, 30.0, 47.952,
                 48.0, 50.0, 59.94, 60.0, 72.0, 90.0, 95.904, 96.0, 100.0,
                 119.88, 120.0)

# How far a measured rate may sit from one of those and still be it.
# Relative: one frame at 120 is a fifth of one at 24. A container names
# its rate to within a millionth and an averaged reading strays a few
# ten-thousandths, while the nearest foreign rate lies four times out.
FRAME_RATE_TOLERANCE = 0.01


def nearest_known_frame_rate(fps):
    """Round a frame rate to one Resolve knows.

    ffprobe measures averaged values for some files. Resolve rejects
    those and picks something itself, so it is decided here and said.
    Whether it is one of Resolve's rates at all is known_frame_rate.
    """
    if not fps:
        return 30.0
    return min(RESOLVE_FRAME_RATES, key=lambda r: abs(r - fps))


def known_frame_rate(fps):
    """The Resolve rate this one is, allowing for a measured reading.

    A rate this answers None for is not one Resolve gives a Timeline.
    The file is used all the same: the Timeline takes a rate Resolve
    does have, and the file keeps counting in its own.
    """
    if not fps:
        return None
    near = min(RESOLVE_FRAME_RATES, key=lambda r: abs(r - fps))
    return near if abs(near - fps) <= near * FRAME_RATE_TOLERANCE else None


def own_frame_rate(fps):
    """The rate a file's own frames are counted at.

    A measured reading strays a few ten-thousandths from the format it
    means, so where it means one of Resolve's rates that is the answer.
    Where it means none of them the reading itself is the answer, and
    it is not moved to the nearest: a file at 15 counts fifteen frames
    to the second, and its length, its timecode and its cut all say so.
    """
    return known_frame_rate(fps) or float(fps or 30.0)


def resolve_timeline_rate(fps):
    """The rate a Timeline gets for material running at this one.

    Not the nearest but the next one up: upwards Resolve repeats
    frames, downwards it throws them away. Above the fastest rate it
    has there is no higher one, so that is where it stops. Measured on
    21.0.4.5: 15 and 240 are refused as project rates, 16 and 120 are
    the ends -- and a 15 file in a 16 Timeline keeps its length to the
    millisecond, every shot on the source frame the cut names.
    """
    known = known_frame_rate(fps)
    if known is not None:
        return known
    if not fps:
        return 30.0
    return next((r for r in RESOLVE_FRAME_RATES if r > fps),
                RESOLVE_FRAME_RATES[-1])


def file_frame_rate(info):
    """The rate a video file runs at: the one its container declares.

    An averaged reading is not a format -- a file whose rate varies
    averages to something that is no rate at all -- so the container's
    own figure decides, and the average stands in only where the
    container names none.
    """
    return (info or {}).get("nominal") or (info or {}).get("fps") or 0.0


def timeline_frame_rate(args, videos, ref_clip):
    """The rate the Timeline runs at: the highest one in the material.

    Converted upwards Resolve repeats frames, downwards it throws them
    away, so the fastest camera decides. Intro and outro are finished
    clips and no cameras of the episode, so they do not count; where no
    camera is left the longest recording decides, as it did before.
    """
    edges = {path_key(p) for p in (getattr(args, "intro", None),
                                   getattr(args, "outro", None)) if p}
    rates = [(e or {}).get("fps") or 0.0 for v, e in (videos or ())
             if path_key(v) not in edges]
    return max(rates) if any(rates) else (
        ref_clip[1]["fps"] if ref_clip else 30.0)


def frames_to_timecode(frames, fps, drop_frame=False):
    """The other way round: a frame number since midnight as a timecode.

    Counts on the timecode clock, like timecode_to_frames -- dividing by
    the true rate instead is off by about a minute per hour.
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


def open_or_create_project(pm, name, carry_on=None):
    """Create or open a project, asking if one already exists.

    Returns (project, kind), where kind says what to do with it:
    "created", "update" or "keep".
    """
    existing = pm.GetProjectListInCurrentFolder() or []
    if name not in existing:
        p = pm.CreateProject(name)
        if p is None:
            raise RuntimeError(T('Project %r could not be created. Is the '
                                 'name already in another folder?') % name)
        print(T('  Project %r created.') % name)
        return p, "created"
    print(T('\n  A PROJECT WITH THIS NAME ALREADY EXISTS: %r') % name)
    choice = ask_choice(
        [("update",
          T('bring up to date -- both Timelines are deleted and\n       '
            'rebuilt, the media pool stays as it is')),
         ("keep", T('leave it and put the new Timelines alongside --\n      '
                    ' the existing ones stay')),
         ("new", T('create a new project alongside (name with suffix)')),
         ("abort", T('cancel'))],
        T('What should happen with it?'), T('This Resolve project already exists'),
        carry_on, "--resolve-project")
    if choice == "abort":
        raise RuntimeError(T('Stopped. Nothing was created.'))
    if choice in ("update", "keep"):
        p = pm.LoadProject(name)
        if p is None:
            raise RuntimeError(T('Project %r could not be opened.') % name)
        print(T('  Project %r opened.') % name)
        return p, choice
    for k in range(2, 100):
        fresh = "%s %d" % (name, k)
        if fresh not in existing:
            p = pm.CreateProject(fresh)
            if p is None:
                raise RuntimeError(T('Project %r could not be created.') % fresh)
            print(T('  Project %r created.') % fresh)
            return p, "created"
    raise RuntimeError(T('Too many projects with this name.'))


def same_setting_value(a, b):
    """Report whether two setting values are the same.

    Resolve returns 30.0 when 30 was set, and comparing text fails, so
    they are compared as numbers and only as text when that cannot work.
    """
    try:
        return abs(float(a) - float(b)) < 1e-6
    except (TypeError, ValueError):
        return str(a).strip() == str(b).strip()


def apply_project_settings(p, d):
    """Set frame rate, drop frame and resolution, then verify they took."""
    value = "%g" % resolve_timeline_rate(d.get("fps") or 30.0)
    if d.get("fps_measured") and abs(d["fps_measured"]
                                     - resolve_timeline_rate(d["fps"])) > 0.001:
        print(T('    Measured %s frames/s -- Resolve only knows fixed '
                'rates,\n    %s is used.')
              % (decimal_text("%g" % d["fps_measured"]),
                 decimal_text(value)))
    applied = []
    for api_key, value in (("timelineFrameRate", value),
                          ("timelinePlaybackFrameRate", value),
                          ("timelineDropFrameTimecode",
                           "1" if d.get("drop_frame") else "0"),
                          ("timelineResolutionWidth",
                           str(d.get("width") or "")),
                          ("timelineResolutionHeight",
                           str(d.get("height") or ""))):
        if not value:
            continue
        p.SetSetting(api_key, value)
        now = p.GetSetting(api_key)
        applied.append((api_key, value, now, same_setting_value(now, value)))
    for api_key, value, now, matches in applied:
        print("    %-28s %-10s %s" % (api_key, now,
                                      "" if matches else T('(wanted %s)') % value))
    if any(not x[3] for x in applied):
        print(T('    Not everything could be set. Resolve takes some '
                'values only\n    while the Timeline is still empty -- '
                'please compare above.'))


def set_remote_grades(p, on=False):
    """Turn remote grades off, and keep them off.

    Remote grades tie every clip of the same source file together, so a
    single cut can no longer be corrected on its own; colour groups do
    the same more finely. Set on every run and before anything is built,
    because it only affects clips added to a timeline afterwards. The
    setting's name is not documented, so it is looked up, not guessed.
    """
    try:
        every = p.GetSetting("")
    except Exception:
        every = None
    if not isinstance(every, dict):
        print(T('    Settings not listable -- please set by hand:\n    '
                "Project Settings > General Options > Color > 'Use local "
                "version for new clips' %s.") % (T('off') if on else T('on')))
        return None
    hit = [k for k in every
               if "local" in k.lower() and "version" in k.lower()]
    if not hit:
        print(T('    No setting for the versions found -- please set by '
                'hand:\n    Project Settings > General Options > Color > '
                "'Use local version for new clips' %s.")
              % (T('off') if on else T('on')))
        return None
    api_key = hit[0]
    wanted = "0" if on else "1"
    p.SetSetting(api_key, wanted)
    now = p.GetSetting(api_key)
    matches = same_setting_value(now, wanted)
    print("    %-28s %-10s %s" % (api_key, now,
                                  "" if matches else T('(wanted %s)') % wanted))
    if not matches:
        return matches
    if on:
        print(T('    Remote grades are on: one colour correction per '
                'camera applies\n    to all its cuts -- a single cut can '
                'then no longer be corrected\n    on its own.'))
    else:
        print(T('    Local versions: in the node editor "Group Pre-Clip" '
                'applies to the\n    whole camera, "Clip" only to the one '
                'cut. One does not exclude\n    the other.'))
    return matches


# What YouTube recommends for upload, in kbit/s. For ranges the upper value is
# used: the upload happens once, and what is lost in their re-encode nobody
# gets back. HFR means high frame rates -- 48, 50, 60.
#                    height  SDR    SDR-HFR  HDR    HDR-HFR
RENDER_BITRATE = ((4320, 160000, 240000, 200000, 300000),
                  (2160,  45000,  68000,  56000,  85000),
                  (1440,  16000,  24000,  20000,  30000),
                  (1080,   8000,  12000,  10000,  15000),
                  (720,    5000,   7500,   6500,   9500),
                  (0,      2500,   4000,   3000,   4500))
# Stereo -- and we output two channels, see the mix.
RENDER_AUDIO_KBIT = 384


def bitrate_for(height, fps=30.0, hdr=False):
    """Return the bitrate in kbit/s for height, frame rate and HDR."""
    column = (3 if hdr else 1) + (1 if (fps or 0) > 30.5 else 0)
    for row in RENDER_BITRATE:
        if (height or 0) >= row[0]:
            return row[column]
    return RENDER_BITRATE[-1][column]


# Transfer characteristic codes per ITU-T H.273. 16 is PQ, 18 is HLG, both HDR
# markers. 9 as colour space is BT.2020.
TRC_HDR = {16: "PQ", 18: "HLG"}
# Log is not a display curve but a recording curve: it preserves the dynamic
# range the camera sees and is converted to something else for delivery. For
# output that means the same as HDR -- eight bit is not enough and gradients
# would band. 21 is the code Apple Log carries in the file.
TRC_LOG = {21: "Apple Log"}
PRIMARIES_BT2020 = 9
# Another way to spot log: the cameras write it into their QuickTime keys.
# Searched by word markers rather than by "log", which hides in too many
# harmless words.
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


# Names for the ITU-T H.273 codes. Anything not in the list is shown as a
# number rather than guessed. 2 means "unspecified" in both lists: the file
# says nothing about its colour.
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
    # Apple writes the recording curve into the logs atom of the sample
    # description rather than into the colr box. That is the only way Resolve
    # knows Apple Log is present; colr says nothing about it.
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
            parts.append("Matrix %s"
                         % MATRIX_NAMES.get(mat, T('Number %d') % mat))
        if not parts:
            parts.append(T('Curve and colour space are missing from the file'))
        # The matrix counts too: some cameras write only that and leave curve
        # and primaries empty. BT.2020 as a matrix is still a statement about
        # the range of the material.
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
        parts.append("%d bit" % n)
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
    # Last of all what wrote the file: some cameras put their own name in
    # "encoder" and say it in no other key.
    software = d.get("software") or d.get("firmware") or d.get("encoder") or ""
    if device and software:
        return "%s  --  Software %s" % (device, software)
    return device or software or T('no information in the file')


# What a finished file has to carry for a player to recognise HDR -- the ITU-T
# H.273 codes. 9 as primaries is BT.2020, 16 is PQ (SMPTE ST 2084), 18 is HLG,
# 9 as matrix is BT.2020 non-constant luminance. 14 looks similar but is SDR in
# the BT.2020 space and does not qualify.
HDR_PRIMARIES = 9
HDR_MATRIX = 9
HDR_CURVES = {16: "PQ (HDR10)", 18: "HLG"}


def hdr_static_metadata(file_path):
    """Return which HDR static metadata a file carries.

    ffprobe attaches mastering display and content light level to the
    first frame rather than to the stream, and they appear as a
    container box or as SEI depending on the file. So the first frame is
    what gets queried. Returns the set of kinds found.
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
            "abort", "colr box",
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
        "%d bit%s" % (depth, "" if depth else T(' -- not readable')),
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
            "hint" if depth < 10 else "good", "Codec",
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
        % group_text(len(hints)) if have_hdr
        else T('The file is NOT recognised as HDR.')))
    return 0 if have_hdr else 1


def hdr_from_sources(video_paths):
    """Report whether the source material is HDR. Returns (yes, reason).

    The camera file's colr box is read, not guessed. Three things count
    as HDR: PQ or HLG, the two display curves; log, a recording curve
    HDR is graded from; and BT.2020 as the colour space. Log belongs
    there because ungraded it looks flat but carries the full range, and
    in eight bit it bands. The reason stays English: it goes into a file.
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
        # Some cameras write nothing usable into the colr box; for those it is
        # in the QuickTime keys.
        source_text = _log_gamma_in_metadata(file_path)
        if source_text:
            return True, ("log according to camera data: %s (%s)"
                          % (source_text[:60], name))
    return False, ""


# How Resolve writes the two tags in the Deliver tab depends on the version. So
# do not bet on one spelling: try them in turn and read back what arrived.
HDR_TAGS = {
    "pq": (("Rec.2020", "Rec. 2020", "Rec2020"),
           ("ST.2084", "ST2084", "PQ", "SMPTE ST 2084")),
    "hlg": (("Rec.2020", "Rec. 2020", "Rec2020"),
            ("HLG", "Rec.2100 HLG", "ARIB STD-B67")),
}

# The same for a delivery that is not HDR. Without it the render stays
# at "Same as Project", and an HDR project would put an HDR colr box on
# an eight bit file. The order of the gamma spellings matters: the one
# that lands right comes first, the others write "unspecified".
SDR_TAGS = (("Rec.709", "Rec. 709", "Rec709"),
            ("Rec.709", "Gamma 2.4", "Rec.709 Gamma 2.4", "Gamma2.4"))


def hdr_kind_from_project(p):
    """Return the HDR curve the project outputs: PQ, HLG or none.

    The output colour space is read as Resolve enumerates it. Nothing is
    guessed: unrecognisable means None and "Same as Project" stands.
    """
    try:
        every = p.GetSetting("")
    except Exception:
        return None, ""
    if not isinstance(every, dict):
        return None, ""
    for api_key, value in every.items():
        k = api_key.lower()
        if "color" not in k or "output" not in k:
            continue
        value = str(value)
        wl = value.lower().replace(" ", "").replace(".", "")
        if "st2084" in wl or wl.endswith("pq"):
            return "pq", "%s = %s" % (api_key, value)
        if "hlg" in wl:
            return "hlg", "%s = %s" % (api_key, value)
    return None, ""


def hdr_from_project(p):
    """Report whether the Resolve project settings say HDR is being output.

    The setting's name is not guessed but looked up among all settings.
    Finding nothing, this says nothing and the material decides.
    """
    try:
        every = p.GetSetting("")
    except Exception:
        return None, ""
    if not isinstance(every, dict):
        return None, ""
    for api_key, value in every.items():
        k = api_key.lower()
        if "color" not in k or "output" not in k:
            continue
        value = str(value)
        wl = value.lower()
        if any(x in wl for x in ("2100", "st2084", "pq", "hlg", "hdr")):
            return True, "%s = %s" % (api_key, value)
        if "2020" in wl or any(_marker_stands_alone(wl, m)
                               for m in LOG_MARKERS):
            return True, "%s = %s" % (api_key, value)
        if wl and wl not in ("", "none"):
            return False, "%s = %s" % (api_key, value)
    return None, ""


def _first_match(pairs, wanted_name):
    """Return the first identifier from {description: identifier} that matches.

    Neither the format nor the codec names are documented and they
    change between versions, so both are enumerated and searched.
    """
    if not isinstance(pairs, dict):
        return None, None
    for search_word in wanted_name:
        hit = [(b, k) for b, k in pairs.items()
                   if search_word.lower() in ("%s %s" % (b, k)).lower()]
        if hit:
            # The shortest name is the plain one: "H.265" before "H.265
            # (NVIDIA)". The variants with a GPU in the name are not available
            # everywhere and produce different results.
            hit.sort(key=lambda x: len(x[0]) + len(x[1]))
            return hit[0]
    return None, None


def output_folder_from(d):
    """Return the render target: where the finished files are."""
    for cam in (d.get("cameras") or []):
        for api_key in ("file", "source"):
            file_path = cam.get(api_key)
            if file_path and os.path.isdir(os.path.dirname(file_path)):
                return os.path.dirname(file_path)
    for file_path in (d.get("audio_files") or {}).values():
        if file_path and os.path.isdir(os.path.dirname(file_path)):
            return os.path.dirname(file_path)
    return os.getcwd()


def free_render_name(folder, name, extension=".mp4"):
    """Return a name in this folder that no file carries yet.

    Resolve renders over an existing file without asking, and a delivery
    is the one file nobody keeps a copy of.
    """
    if not os.path.exists(os.path.join(folder, name + extension)):
        return name
    for k in range(2, 1000):
        candidate = "%s_%d" % (name, k)
        if not os.path.exists(os.path.join(folder,
                                           candidate + extension)):
            return candidate
    return name


def hdr_says(value):
    """Report whether a colour space name means HDR.

    Read on the answer Resolve gives, which is its internal name --
    "Rec.2100 ST2084", "Rec.709 (Scene)". The dropdown names carry the
    answer in front ("SDR Rec.2020"), so those are read from the front.
    """
    wl = str(value).strip().lower()
    if wl.startswith("sdr"):
        return False
    if wl.startswith("hdr"):
        return True
    return any(x in wl for x in ("2100", "st2084", "pq", "hlg", "2020"))


def project_colour_to_material(p, hdr):
    """Bring a project we made ourselves to the colour space of the material.

    A project created a minute ago carries whatever this machine
    defaults to, and machines differ; one somebody set up is never
    touched. Only the output space is set -- a wide gamut working space
    under an SDR output is a state Resolve offers on purpose -- and
    `isAutoColorManage` stays untouched. Returns (stands, "") or ("", why).
    """
    try:
        every = p.GetSetting("")
    except Exception:
        return "", ""
    if not isinstance(every, dict):
        return "", ""
    # Two namespaces, and they exclude each other: with automatic colour
    # management on, only the dropdown names are taken and the internal
    # one comes back; with it off, only the internal names. So both are
    # tried, and success is judged by what the setting says afterwards.
    if hdr:
        values = ["HDR PQ", "Rec.2100 ST2084", "HDR HLG", "Rec.2100 HLG"]
    else:
        values = ["SDR Rec.709", "Rec.709 (Scene)", "Rec.709 Gamma 2.4",
                  "Rec.709"]
    done, missed = [], []
    name = "colorSpaceOutput"
    if name in every:
        got = ""
        for value in values:
            try:
                if not p.SetSetting(name, value):
                    continue
                back = str(p.GetSetting(name))
                if hdr_says(back) == hdr:
                    got = back
                    break
            except Exception:
                continue
        if got:
            done.append("%s = %s" % (name, got))
        else:
            missed.append("%s = %s" % (name, every[name]))
    if not hdr and str(every.get("hdr10PlusControlsOn", "")) in ("1", "True"):
        # Only ever off, never on: switching on a delivery feature
        # nobody asked for is not this program's business, while leaving
        # it on in an SDR delivery is a contradiction.
        try:
            p.SetSetting("hdr10PlusControlsOn", "0")
        except Exception:
            pass
    if missed:
        return "", ", ".join(missed)
    return ", ".join(done) or T('already right'), ""


def queue_render_job(p, tl, d, folder, name, project_is_new=False):
    """Set the render profile and queue the job.

    After this only "Render All" is left to press in Resolve. Whatever
    the interface accepts is set; whatever it rejects appears in the log
    so nobody has to hunt for it. HDR or SDR is decided by the material
    and the project, not by preference: an HDR picture in eight bit
    H.264 bands in every gradient.
    """
    print(T('\n  Render job'))
    try:
        p.SetCurrentTimeline(tl)
    except Exception:
        pass
    hdr = bool(d.get("hdr"))
    reason = d.get("hdr_reason") or ""
    off_project, project_reason = hdr_from_project(p)
    if project_is_new and off_project is not None and off_project != hdr:
        # Our own project, and its colour space says something other
        # than the material. Whatever it says was not chosen for this
        # job, so the material decides -- in both directions.
        stands, instead = project_colour_to_material(p, hdr)
        if stands:
            print("    %-22s %s" % (T('Colour space'), stands))
        else:
            print(as_warn(T('    Caution: the project stands at %s, the '
                            'material is %s.\n             The delivery '
                            'carries the tags of the material. To bring '
                            'the\n             project along: Project '
                            'Settings > Color Management >\n             '
                            'Output Color Space = %s.')
                          % (instead or project_reason,
                             "HDR" if hdr else "SDR",
                             "HDR PQ" if hdr else "SDR Rec.709")))
    elif off_project is not None and off_project != hdr:
        # The project wins: it says what actually comes out.
        hdr, reason = off_project, project_reason
    elif off_project is not None and project_reason:
        reason = reason or project_reason
    print("    %-22s %s%s" % (T('Dynamic range'), "HDR" if hdr else "SDR",
                              "  (%s)" % reason if reason else ""))

    formats = None
    try:
        formats = p.GetRenderFormats()
    except Exception as e:
        print(T('    Format list not readable: %s') % e)
    fname, format_id = _first_match(formats, ["mp4"])
    if not format_id:
        print(T('    No MP4 format found. Available: %s')
              % ", ".join(sorted(formats or {}))[:200])
        return False
    codecs = None
    try:
        codecs = p.GetRenderCodecs(format_id)
    except Exception as e:
        print(T('    Codec list not readable: %s') % e)
    wanted_name = (["h.265", "h265", "hevc"] if hdr else [])\
        + ["h.264", "h264", "avc"]
    cname, codec_id = _first_match(codecs, wanted_name)
    if not codec_id:
        print(T('    No matching codec found. Available: %s')
              % ", ".join(sorted(codecs or {}))[:200])
        return False
    if hdr and not any(x in ("%s %s" % (cname, codec_id)).lower()
                       for x in ("265", "hevc")):
        print(as_warn(T('    Caution: no H.265 available -- it will be '
                        'H.264 with eight bits.\n             Too little '
                        'for HDR; gradients will show banding.')))
    try:
        if not p.SetCurrentRenderFormatAndCodec(format_id, codec_id):
            print(T('    Format and codec could not be set.'))
            return False
    except Exception as e:
        print(T('    Format and codec could not be set: %s') % e)
        return False
    try:
        # Said out loud when it does not take: refused, the delivery
        # quietly becomes one file per clip, and somebody looking for
        # one episode finds a folder full of shots instead.
        if p.SetCurrentRenderMode(1) is False:   # 1 = one file, not per clip
            print(T('    One file per delivery was refused; Resolve will '
                    'write one file per clip.'))
    except Exception as e:
        print(T('    One file per delivery could not be asked for: %s') % e)
    height = int(d.get("height") or 1080)
    width = int(d.get("width") or 1920)
    fps = float(d.get("fps") or 30.0)
    bitrate = bitrate_for(height, fps, hdr)
    taken = free_render_name(folder, name)
    if taken != name:
        print(T('    %-22s %s exists already -- rendered to %s instead, '
                'so the\n%searlier delivery stays.')
              % (T('Target'), name + ".mp4", taken + ".mp4", " " * 28))
        name = taken
    settings = {
        "SelectAllFrames": True,
        "TargetDir": folder,
        "CustomName": name,
        "ExportVideo": True,
        "ExportAudio": True,
        "FormatWidth": width,
        "FormatHeight": height,
        "FrameRate": fps,
        "VideoQuality": bitrate,
        "AudioCodec": "aac",
        "AudioBitDepth": 16,
        "AudioSampleRate": SR,
    }
    # Ten bit has no switch of its own, only the profile. Whether this Resolve
    # knows the name shows only on setting it, so it is tried with and, if
    # rejected, without.
    extra_text = {"EncodingProfile": "Main10"} if hdr else {}
    # And the tagging: without it the finished file carries no HDR however
    # cleanly it was graded. Which curve is what the project says; nothing is
    # guessed.
    kind, kind_reason = hdr_kind_from_project(p)
    tag_pairs = []
    if hdr and kind in HDR_TAGS:
        clear, curves = HDR_TAGS[kind]
        tag_pairs = [{"ColorSpaceTag": r, "GammaTag": g}
                     for r in clear for g in curves]
    elif not hdr:
        clear, curves = SDR_TAGS
        tag_pairs = [{"ColorSpaceTag": r, "GammaTag": g}
                     for r in clear for g in curves]
    if hdr and kind not in HDR_TAGS:
        print(T('    %-22s stays at "Same as Project" -- the project '
                'names\n%sno HDR curve. To check in Resolve under\n%sProject '
                'Settings > Color Management > Output Color Space.') % (T('Tagging'), " " * 28, " " * 28))
    applied, accepted = False, None
    attempts = [dict(settings, **dict(extra_text, **t)) for t in tag_pairs]
    if extra_text:
        attempts.append(dict(settings, **extra_text))
    attempts.append(settings)
    for attempt in attempts:
        try:
            applied = bool(p.SetRenderSettings(attempt))
        except Exception:
            applied = False
        if applied:
            accepted = attempt
            break
    if not applied:
        print(T('    Render settings rejected.'))
        return False
    if extra_text:
        print("    %-22s %s" % (T('Profile'), T('Main10 (ten bit)')
                                if "EncodingProfile" in accepted
                                else T('Main10 rejected -- the default stays')))
    if tag_pairs:
        if "ColorSpaceTag" in accepted:
            # The reason names the HDR curve the project outputs, so it
            # belongs to the HDR tags alone. An SDR delivery has none:
            # beside Rec.709 the setting would explain a curve that was
            # not applied, and empty brackets read as a failed lookup.
            print("    %-22s %s / %s%s"
                  % (T('Tagging'), accepted["ColorSpaceTag"],
                     accepted["GammaTag"],
                     "  (%s)" % kind_reason if hdr and kind_reason else ""))
        else:
            print(T('    %-22s rejected -- no spelling was accepted.\n%sSet '
                    'by hand in Resolve under Deliver > '
                    'Advanced\n%sSettings: Color space tag Rec.2020, Gamma '
                    'tag %s.')
                  % (T('Tagging'), " " * 28, " " * 28,
                     "ST.2084" if kind == "pq" else "HLG"))
    print("    %-22s %s / %s" % ("Format", fname or format_id,
                                 cname or codec_id))
    print("    %-22s %dx%d, %g fps" % (T('Video'), width, height, fps))
    print(T('    %-22s %s kbit/s  (YouTube recommendation for %s%s)')
          % ("Bitrate", group_text(bitrate),
             "HDR" if hdr else "SDR", T(' at high frame rates') if fps > 30.5
             else ""))
    # The interface has no key for the audio bitrate. So write down what should
    # be there, and nobody has to look for it.
    print(T('    %-22s AAC, %s Hz, two channel  (bitrate cannot be set '
            'remotely --\n%s%s kbit/s are the recommendation for stereo)')
          % (T('Audio'), group_text(SR), " " * 28,
             RENDER_AUDIO_KBIT))
    print("    %-22s %s" % (T('Target'),
                            os.path.join(folder, name + ".mp4")))
    try:
        job = p.AddRenderJob()
    except Exception as e:
        print(T('    Render job could not be created: %s') % e)
        return False
    if not job:
        print(T('    Render job could not be created.'))
        return False
    print(T('    Queued -- in Resolve only "Render All" is left.'))
    if hdr:
        print(T('    Whether the finished file passes as HDR:\n      '
                'videopodcast-magic --hdr-check %s')
              % os.path.join(folder, name + ".mp4"))
    return True


def set_loudness_target(p, target_lufs):
    """Set the loudness meter target to ours.

    Resolve measures against -23 LUFS by default, the broadcast value. We
    deliver for web and podcast and normalise to -16, where the meter would
    permanently read +7. The setting's name is not guessed but looked up
    among all project settings.
    """
    try:
        every = p.GetSetting("")
    except Exception:
        every = None
    if not isinstance(every, dict):
        return None
    hit = [k for k in every
               if "loudness" in k.lower() and ("target" in k.lower()
                                               or "level" in k.lower())]
    # "audioMeterLoudnessScale" is the scale, not the target.
    hit = [k for k in hit if "scale" not in k.lower()]
    if not hit:
        print(T('    Loudness meter target level not found -- please set '
                'it by hand:\n    Project Settings > Fairlight > Target '
                'Loudness Level %s LUFS.')
              % decimal_text("%g" % target_lufs))
        return None
    api_key = hit[0]
    wanted = "%g" % target_lufs
    p.SetSetting(api_key, wanted)
    now = p.GetSetting(api_key)
    matches = same_setting_value(now, wanted)
    print("    %-28s %-10s %s" % (api_key, now,
                                  "" if matches else T('(wanted %s)') % wanted))
    return matches


def import_media(mp, paths):
    """Import files and find them again by their path."""
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        raise RuntimeError(T('These files do not exist:\n  ')
                           + "\n  ".join(missing))
    fresh = mp.ImportMedia(list(paths)) or []
    print(T('  %s of %s files imported.')
          % (group_text(len(fresh)), group_text(len(paths))))
    # Two cameras can write C0001.MP4 in two folders. Looked up by name
    # both land on one media pool item, and the second camera then gets the
    # first one's picture without a word. Resolve reports the real path, so
    # that is the key; the name stays as a fallback for versions that do
    # not, and a collision there stops the run instead of wiring it wrong.
    after_path, after_name = ByFile(), {}
    for c in (mp.GetRootFolder().GetClipList() or []):
        try:
            where = c.GetClipProperty("File Path") or ""
        except Exception:
            where = ""
        if where:
            after_path.setdefault(where, c)
        after_name.setdefault(c.GetName(), c)
    assignment, claimed = {}, {}
    for p in paths:
        c = (after_path.get(p)
             or after_name.get(os.path.basename(p)))
        if c is None:
            raise RuntimeError(T('Not found again after import: %s')
                               % os.path.basename(p))
        if id(c) in claimed and claimed[id(c)] != p:
            raise RuntimeError(
                T('%s and %s carry the same file name, and Resolve '
                  'reports no\n  path for them. Rename one of the two.')
                % (claimed[id(c)], p))
        claimed[id(c)] = p
        assignment[p] = c
    return assignment


def create_timeline(mp, name):
    """Create an empty timeline; an existing one of that name gets a suffix."""
    tl = mp.CreateEmptyTimeline(name)
    if tl is None:
        for k in range(2, 100):
            tl = mp.CreateEmptyTimeline("%s %d" % (name, k))
            if tl is not None:
                print(T('  A Timeline %r existed already -- the new one is '
                        'called %r.')
                      % (name, tl.GetName()))
                break
    if tl is None:
        raise RuntimeError(T('Timeline %r could not be created.') % name)
    return tl


def find_timeline(p, name):
    """Find the timeline of this name in the project."""
    for i in range(1, (p.GetTimelineCount() or 0) + 1):
        tl = p.GetTimelineByIndex(i)
        if tl is not None and (tl.GetName() or "") == name:
            return tl
    return None


def refresh_resolve_timelines(p, mp, names):
    """Delete these timelines so they can be built again.

    Everything else stays: the media pool and whatever else is in the
    project. Updating means a fresh cut, not an empty project.

    Returns (what was removed, what stayed).
    """
    existing = {}
    for i in range(1, (p.GetTimelineCount() or 0) + 1):
        tl = p.GetTimelineByIndex(i)
        if tl is not None:
            existing.setdefault(tl.GetName() or "", tl)
    duplicate = [n for n in names if n in existing]
    if not duplicate:
        return [], []
    # The open timeline cannot be deleted, so switch to another one first where
    # there is one.
    other = next((tl for n, tl in existing.items() if n not in names), None)
    if other is not None:
        try:
            p.SetCurrentTimeline(other)
        except Exception:
            pass
    targets = [existing[n] for n in duplicate]
    try:
        mp.DeleteTimelines(targets)
    except Exception:
        # Some versions want them one at a time.
        for tl in targets:
            try:
                mp.DeleteTimelines([tl])
            except Exception:
                pass
    # Check what really went: the interface's answer alone is not enough -- it
    # reports success even where nothing happened.
    gone = [n for n in duplicate if find_timeline(p, n) is None]
    stayed = [n for n in duplicate if n not in gone]
    return gone, stayed


def multicam_timeline_unchanged(p, name, cameras):
    """Report whether the multicam timeline already looks the way it should.

    The cut timeline may be rebuilt every run -- it is cheap and changes
    with every number. The multicam timeline carries manual work: the
    multicam clip is converted from it by hand, so it stays as long as the
    same cameras sit on it in the same order.
    """
    tl = find_timeline(p, name)
    if tl is None:
        return None
    try:
        if tl.GetTrackCount("video") != len(cameras):
            return None
        for i, cam in enumerate(cameras, 1):
            item = tl.GetItemListInTrack("video", i) or []
            want = os.path.basename(cam.get("file") or cam.get("source") or "")
            if len(item) != 1 or (item[0].GetName() or "") != want:
                return None
    except Exception:
        return None
    return tl


def cameras_in_track_order(cameras):
    """Put the camera carrying the overall mix on track one.

    Converting to a multicam clip makes video track 1 angle 1, and its first
    audio track is the one Resolve falls back to. The overall mix belongs
    there -- that is the wide shot, which carries exactly that as its first
    track. The rest keep their order.
    """
    def first_of(cam):
        names = [n.lower() for n in (cam.get("audio_tracks") or [])]
        if names and "full" in names[0]:
            return 0
        return 0 if (cam.get("wide") and not names) else 1
    return sorted(cameras, key=first_of)


# Where a new Resolve timeline starts when nobody says otherwise:
# 01:00:00:00. Material without a timecode is laid down there rather
# than at frame 0, which would be eighteen hours before the beginning.
TIMELINE_START_HOUR = 1


def timeline_origin(d):
    """Return where frame zero of the timeline sits and how fast it runs.

    Resolve counts recordFrame from midnight, not from the start of the
    timeline. Passing zero puts the clip 18 hours before the beginning: it
    is there, but not visible.

    Where the handover carries no timecode, the timeline's own start is
    used. Measured on a screen recording: at frame 0 the clips sit
    outside a timeline that begins at 01:00:00:00, and the delivery is a
    single frame while the log says six seconds.
    """
    fps = resolve_timeline_rate(d.get("fps") or 30.0)
    if not d.get("start_tc"):
        return fps, int(round(TIMELINE_START_HOUR * 3600 * fps))
    return fps, timecode_to_frames(d.get("start_tc"), fps)


def set_timeline_start(tl, tc):
    """Give the Timeline its start timecode, and check that it took.

    Every shot is placed by a frame number counted from midnight. Where
    the start does not take, the Timeline keeps the 01:00:00:00 a new
    one is born with, and the whole episode sits fifteen hours into it:
    the shots right against each other, and the clock an hour out. The
    interface answers, so the answer is read.
    """
    if not tc:
        return True
    took = False
    try:
        took = bool(tl.SetStartTimecode(tc))
    except Exception as e:
        print(as_warn(T('  The Timeline start %s was refused: %s') % (tc, e)))
    try:
        now = tl.GetStartTimecode()
    except Exception:
        now = None
    if now and str(now) != str(tc):
        print(as_warn(T('  The Timeline starts at %s, not at %s -- every '
                        'shot sits that much further in.') % (now, tc)))
        return False
    if not took and now is None:
        print(as_warn(T('  The Timeline start %s was not accepted.') % tc))
    return took


def audio_track_count(cam):
    """Return how many audio tracks this camera file carries.

    Counted in the file, not in the handover, which lists only the processed
    tracks and omits the camera microphone. That difference used to leave no
    room for the last camera, which then vanished along with its picture.
    """
    file_path = cam.get("file") or cam.get("source")
    try:
        d = ffprobe_json(file_path)
        n = len([s for s in (d.get("streams") or [])
                 if s.get("codec_type") == "audio"])
        if n:
            return n
    except Exception:
        pass
    return max(1, len(cam.get("audio_tracks") or [1]) + 1)


def build_camera_timeline(mp, tl, cameras, clips, d, every_tracks=False):
    """Lay all cameras side by side, one per video track, one audio track each.

    With all_tracks every audio track stays instead. That is the single
    camera case: there is nothing to untangle and the individual speakers
    plus the mix belong in the timeline.

    Uncut and at full length -- exactly how a timeline destined to become a
    multicam clip has to look.

    Clips are inserted with all their audio, because there is no way to
    choose which audio track comes along. Then it is cleaned up: unlink
    audio from video, delete all but the first audio track of each camera,
    remove the empty tracks, and link picture and remaining audio again --
    V1 to A1, V2 to A2. Unlinking is required, otherwise deleting an audio
    track takes its picture with it.

    For these files the first audio track is the right one: it holds this
    camera's speaker, with the overall mix and the camera microphone behind
    it.
    """
    set_timeline_start(tl, d.get("start_tc"))
    fps, origin = timeline_origin(d)
    while tl.GetTrackCount("video") < len(cameras):
        # Checked like the audio loop below it: an AddTrack that refuses
        # would otherwise be asked again for ever, and every ask is a call
        # into Resolve. The window would look frozen with nothing said.
        if not tl.AddTrack("video"):
            print(as_warn(T('  Resolve refuses more video tracks -- '
                            '%s of %s cameras fit.')
                          % (group_text(tl.GetTrackCount("video")),
                             group_text(len(cameras)))))
            break
    # Room for the audio: the cameras run simultaneously, so their audio tracks
    # all need room side by side. Otherwise Resolve places only what fits and
    # silently drops the rest. With some slack: what Resolve actually occupies
    # is not known in advance, and the cleanup removes empty tracks afterwards.
    needed = sum(audio_track_count(cam) for cam in cameras) + len(cameras)
    while tl.GetTrackCount("audio") < needed:
        if not tl.AddTrack("audio"):
            break
    print(T('  %s video tracks, %s audio tracks created (%s)')
          % (group_text(tl.GetTrackCount("video")),
             group_text(tl.GetTrackCount("audio")),
             " + ".join("%s %d" % (cam["track"], audio_track_count(cam))
                        for cam in cameras)))

    # This timeline starts at the earliest camera, not at In point. Otherwise
    # every camera would lie before the timeline start -- a negative position
    # Resolve sometimes accepts and sometimes silently discards.
    early = earliest_offset(cameras)
    # Where the timeline really begins. The report further down measures
    # against it, and once the start has moved the In point is no longer that
    # point -- a distance counted from there would send the search for a
    # missing camera after the wrong number.
    start_frame, begin = origin, d.get("start_tc") or "?"
    if early < 0:
        start_frame = origin + seconds_to_frames(early, fps)
        begin = frames_to_timecode(start_frame, fps,
                                   bool(d.get("drop_frame")))
        set_timeline_start(tl, begin)
        print(T('  Start %s (earliest camera) -- otherwise everything '
                'would lie before the Timeline start.') % begin)
    entry = {}
    for i, cam in enumerate(cameras, 1):
        c = clips.get(cam["file"])
        if c is None:
            continue
        # Each camera at its measured position in the window, not all at the
        # same point. They started at different times.
        entry[cam["track"]] = {
            "mediaPoolItem": c, "trackIndex": i,
            "recordFrame": origin + seconds_to_frames(cam.get("offset") or 0.0, fps)}
    # One after another, not all at once. Given a batch, Resolve places what
    # fits and drops the rest without a word -- and the audio tracks the
    # skipped camera would have needed are then taken by the next.
    for cam in cameras:
        if cam["track"] not in entry:
            continue
        e = entry[cam["track"]]
        mp.AppendToTimeline([e])
        if timeline_items_per_camera(tl, cameras).get(cam["track"]):
            continue
        # Without mediaType Resolve puts picture *and* audio on the same track
        # number. The second camera should go to V2, but the first camera's
        # second audio channel is long since there, and Resolve refuses without
        # a word. So separately: picture to its video track, audio to the first
        # free audio track.
        free = first_free_audio_track(tl)
        mp.AppendToTimeline([dict(e, mediaType=1)])
        mp.AppendToTimeline([{"mediaPoolItem": e["mediaPoolItem"],
                              "trackIndex": free,
                              "recordFrame": e["recordFrame"],
                              "mediaType": 2}])
        if timeline_items_per_camera(tl, cameras).get(cam["track"]):
            print(T('    %s: picture and audio inserted separately (audio '
                    'from A%d).')
                  % (cam["track"], free))
    present = timeline_items_per_camera(tl, cameras)
    absent = [cam["track"] for cam in cameras if not present.get(cam["track"])]
    if absent:
        # When Resolve inserts nothing it does not say why. So write down the
        # numbers it was called with; that shows afterwards what it was.
        print(T('    For checking -- Timeline starts at frame %d (%s):')
              % (start_frame, begin))
        for cam in cameras:
            if cam["track"] not in entry:
                print(T('      %-24s no file in the media pool') % cam["track"])
                continue
            rf = entry[cam["track"]]["recordFrame"]
            print(T('      %-24s track V%d, from frame %d (%+.1f s to the '
                    'start), %s%s') % (cam["track"], entry[cam["track"]]["trackIndex"], rf,
                            (rf - start_frame) / max(1.0, fps),
                            T('Duration %s') % as_hms(cam.get("duration") or 0.0),
                            T('   NOT INSERTED')
                            if cam["track"] in absent else ""))
            print("        %s" % clip_signature(clips.get(cam["file"])))

    for i, cam in enumerate(cameras, 1):
        if not tl.SetTrackName("video", i, cam["track"]):
            print(T('    Video track %d could not be renamed.') % i)
    print(T('  %s video tracks, named after the speakers:')
          % group_text(len(cameras)))
    for i, cam in enumerate(cameras, 1):
        # The track carries the file's name, so printing both says the
        # same thing twice -- and these names run long.
        name = os.path.basename(cam["file"] or cam["source"])
        print("    V%-3d %s%s%s"
              % (i, cam["track"],
                 "" if os.path.splitext(name)[0] == cam["track"]
                 else "   %s" % name,
                 T('   MISSING') if cam["track"] in absent else ""))
    if absent:
        print(as_warn(TN(len(absent),
                         '  Caution: %s not inserted. Without this angle the'
                         '\n  Timeline is no good for converting.',
                         '  Caution: %s not inserted. Without these angles '
                         'the\n  Timeline is no good for converting.')
                      % ", ".join(absent)))

    if every_tracks:
        # Nothing to untangle with one camera: every audio track stays.
        remove_empty_audio_tracks(tl)
        names = (cameras[0].get("audio_tracks") or []) if cameras else []
        for track in range(1, tl.GetTrackCount("audio") + 1):
            if track <= len(names):
                tl.SetTrackName("audio", track, names[track - 1])
        print(TN(tl.GetTrackCount("audio"),
                 '  %s audio track stays: %s',
                 '  %s audio tracks stay: %s')
              % (group_text(tl.GetTrackCount("audio")),
                 ", ".join(names[:tl.GetTrackCount("audio")]) or T('unnamed')))
    else:
        trim_audio_tracks(tl, cameras, present)
    return tl


def cameras_by_file_name(cameras):
    """Map file name to camera, and say so where two names collide.

    A timeline item reports its name, never its path, so the file name is
    the only key there is. Two cameras writing C0001.MP4 in different
    folders would land on one entry, and the second would quietly take
    over the first one's clips.
    """
    after_file = {}
    for cam in cameras:
        api_key = os.path.basename(cam["file"] or cam["source"])
        if api_key in after_file:
            print(as_warn(T('  Caution: %s and %s are both called %s. On '
                            'the Timeline\n  Resolve reports only the '
                            'name, so their clips cannot be told\n  apart '
                            '-- rename one of the two files.')
                          % (after_file[api_key]["track"], cam["track"],
                             api_key)))
        after_file[api_key] = cam
    return after_file


def audio_tracks_per_camera(tl, cameras):
    """Return which audio items belong to which camera, in track order."""
    after_file = cameras_by_file_name(cameras)
    assignment = {}
    for track in range(1, tl.GetTrackCount("audio") + 1):
        for item in (tl.GetItemListInTrack("audio", track) or []):
            try:
                name = item.GetName() or ""
            except Exception:
                continue
            cam = after_file.get(name)
            if cam:
                assignment.setdefault(cam["track"], []).append((track, item))
    return assignment


def trim_audio_tracks(tl, cameras, video_items):
    """Keep only the first audio track per camera and link it to its picture.

    Conversion turns every track into an angle. Leaving the overall mix and
    the camera microphone in place creates angles without picture, and
    SmartSwitch then hears every speaker on every camera.
    """
    audio = audio_tracks_per_camera(tl, cameras)
    if not audio:
        print(T('  No audio on the Timeline -- nothing to clean up.'))
        return
    print(T('\n  CLEAN UP AUDIO TRACKS'))
    kept = {}
    for cam in cameras:
        # By the track number alone. The entries are (track, item), and
        # two cameras whose files carry the same name put two items on
        # the same track -- then Python compares the items themselves,
        # and two Resolve objects cannot be put in an order. Measured
        # against the running Resolve: it raised there and took the
        # whole Resolve part down after the collision had been
        # reported.
        entries = sorted(audio.get(cam["track"]) or [],
                         key=lambda pair: pair[0])
        if not entries:
            print(T('    %-24s no audio inserted') % cam["track"])
            continue
        video = (video_items.get(cam["track"]) or [None])[0]
        every = [p for _, p in entries]
        # Unlink first, otherwise deleting an audio track takes the linked
        # picture with it.
        separate = False
        try:
            separate = bool(tl.SetClipsLinked(
                ([video] if video else []) + every, False))
        except Exception as e:
            print(T('    %-24s could not be unlinked: %s') % (cam["track"], e))
        gone = every[1:]
        if gone and not separate:
            # Resolve reports failure only as False. Deleting now would take
            # the linked picture along -- exactly the damage unlinking
            # prevents.
            print(T('    %-24s Unlinking had no effect -- the surplus '
                    'audio tracks\n    %-24s stay in place.')
                  % (cam["track"], ""))
            gone = []
        if gone:
            try:
                if not tl.DeleteClips(gone):
                    print(T('    %-24s Deleting failed.') % cam["track"])
                    gone = []
            except Exception as e:
                print(T('    %-24s Deleting failed: %s') % (cam["track"], e))
                gone = []
        kept[cam["track"]] = (video, every[0], entries[0][0])
        print(T('    %-24s audio from A%d kept, %d more deleted')
              % (cam["track"], entries[0][0], len(gone)))

    remove_empty_audio_tracks(tl)

    # Link them again: picture and its audio belong together, otherwise editing
    # moves only half of it.
    linked = 0
    for cam in cameras:
        entry = kept.get(cam["track"])
        if not entry or not entry[0]:
            continue
        video, audio_item, _ = entry
        try:
            if tl.SetClipsLinked([video, audio_item], True):
                linked += 1
            else:
                print(T('    %-24s could not be linked again')
                      % cam["track"])
        except Exception as e:
            print(T('    %-24s Linking failed: %s') % (cam["track"], e))
    if linked:
        print(TN(linked, '    Picture and audio linked again: %s angle',
                 '    Picture and audio linked again: %s angles')
              % group_text(linked))
    # Name the audio tracks like the video tracks; the order is right now.
    n = tl.GetTrackCount("audio")
    row = []
    for track in range(1, n + 1):
        item = tl.GetItemListInTrack("audio", track) or []
        name = ""
        if item:
            for cam in cameras:
                if os.path.basename(cam["file"] or cam["source"]) ==\
                        (item[0].GetName() or ""):
                    name = cam["track"]
                    break
        if name:
            tl.SetTrackName("audio", track, name)
        row.append((track, name or (tl.GetTrackName("audio", track) or ""),
                      len(item)))
    print(TN(n, '  %s audio track remains:',
             '  %s audio tracks remain:') % group_text(n))
    for track, name, count in row:
        print("    A%-3d %-30s %s" % (track, name,
                                       TN(count, '%s clip', '%s clips')
                                       % group_text(count)))


def remove_empty_audio_tracks(tl):
    """Remove audio tracks while they are empty.

    A new timeline brings one along, and that too would become an angle on
    conversion. Sound only: a file carries several audio tracks and only
    some of them are taken, so an empty one is the ordinary case. An empty
    video track is not -- a camera is missing, and the run says so loudly
    rather than tidying the evidence away.
    """
    gone = 0
    for i in range(tl.GetTrackCount("audio"), 0, -1):
        if tl.GetItemListInTrack("audio", i):
            continue
        try:
            if tl.DeleteTrack("audio", i):
                gone += 1
        except Exception:
            pass
    if gone:
        print(TN(gone, '    %s empty audio track removed',
                 '    %s empty audio tracks removed') % group_text(gone))


def source_channel_count(clip):
    """Return how many audio tracks this media pool clip carries.

    The mapping is read from the clip properties rather than from the file,
    so a clip reduced to one track shows as one. Resolve answers like this:

        {"embedded_audio_channels": 4,
         "linked_audio": {},
         "track_mapping": {"1": {"channel_idx": [1], "mute": false,
                                 "type": "mono"}}}

    So: four channels embedded, one track used, from channel 1. Returns
    (tracks, embedded channels).
    """
    try:
        raw = clip.GetAudioMapping()
    except Exception:
        return None, None
    if not raw:
        return None, None
    try:
        m = json.loads(raw) if isinstance(raw, str) else raw
    except ValueError:
        return None, None
    if isinstance(m, list):
        return len(m), None
    if not isinstance(m, dict):
        return None, None
    channels = m.get("embedded_audio_channels")
    if not isinstance(channels, int):
        channels = None
    # Do not rely on the name "track_mapping" alone -- it appears in no
    # description I know of, only in the response itself.
    for api_key, value in m.items():
        s = str(api_key).lower()
        if "linked" in s or not any(word in s for word in ("track", "mapping")):
            continue
        if isinstance(value, (dict, list)) and len(value):
            return len(value), channels
    # Or the mapping is already the outermost level: {"1": ..., "2": ...}
    if m and all(str(k).strip().isdigit() for k in m):
        return len(m), channels
    return None, channels


def print_audio_track_mapping():
    """Print what Resolve reports about the audio tracks, changing nothing.

    For the open project: the raw channel mapping of every media pool clip,
    plus each timeline with its tracks. Enough to check whether a change in
    the clip attributes arrived.
    """
    print(as_head(T('\nRESOLVE -- INSPECT ONLY')))
    r = connect_to_resolve()
    print("  %s %s" % (r.GetProductName(), r.GetVersionString()))
    p = r.GetProjectManager().GetCurrentProject()
    if p is None:
        raise RuntimeError(T('No project open.'))
    print(T('  Project %r') % p.GetName())

    print(T('\n  CLIPS IN THE MEDIA POOL'))
    mp = p.GetMediaPool()
    folder = [mp.GetRootFolder()]
    seen = 0
    while folder:
        f = folder.pop(0)
        if f is None:
            continue
        folder += list(f.GetSubFolderList() or [])
        for c in (f.GetClipList() or []):
            try:
                kind = (c.GetClipProperty("Type") or "").lower()
            except Exception:
                kind = ""
            if "timeline" in kind:
                continue
            seen += 1
            print("\n    %s" % (c.GetName() or "?"))
            for api_key in ("Audio Ch", "Audio Codec", "Audio Bit Depth",
                               "Sample Rate", "Type"):
                try:
                    value = c.GetClipProperty(api_key)
                except Exception:
                    value = None
                if value not in (None, ""):
                    print("      %-16s %s" % (api_key, value))
            try:
                raw = c.GetAudioMapping()
            except Exception as e:
                print(T('      GetAudioMapping   fails: %s') % e)
                continue
            if not raw:
                print(T('      GetAudioMapping   empty (%r)') % raw)
                continue
            print("      GetAudioMapping   %s" % type(raw).__name__)
            text = raw if isinstance(raw, str) else json.dumps(raw)
            try:
                pretty = json.dumps(json.loads(text), indent=2,
                                    ensure_ascii=False)
            except (ValueError, TypeError):
                pretty = text
            for line in pretty.splitlines():
                print("        %s" % line)
            n, channels = source_channel_count(c)
            print(TN(n if isinstance(n, int) else 0,
                     '      --> interpreted as %s audio track%s',
                     '      --> interpreted as %s audio tracks%s')
                  % (n if n is not None else T('not readable'),
                     TN(channels, ' of %s embedded channel',
                        ' of %s embedded channels') % group_text(channels)
                     if channels else ""))
    if not seen:
        print(T('    No clips found.'))

    print("\n  TIMELINES")
    for i in range(1, (p.GetTimelineCount() or 0) + 1):
        tl = p.GetTimelineByIndex(i)
        if tl is None:
            continue
        nv, na = tl.GetTrackCount("video"), tl.GetTrackCount("audio")
        print(T('\n    %s  --  %s, %s')
              % (tl.GetName(),
                 TN(nv, '%s video track', '%s video tracks')
                 % group_text(nv),
                 TN(na, '%s audio track', '%s audio tracks')
                 % group_text(na)))
        for s in range(1, nv + 1):
            item = tl.GetItemListInTrack("video", s) or []
            print("      V%-3d %-24s %s"
                  % (s, (tl.GetTrackName("video", s) or "")[:24],
                     TN(len(item), '%s clip', '%s clips')
                     % group_text(len(item))))
        for s in range(1, na + 1):
            item = tl.GetItemListInTrack("audio", s) or []
            first_one = ""
            if item:
                try:
                    first_one = item[0].GetName() or ""
                except Exception:
                    first_one = "?"
            print("      A%-3d %-24s %-11s %s"
                  % (s, (tl.GetTrackName("audio", s) or "")[:24],
                     TN(len(item), '%s clip', '%s clips')
                     % group_text(len(item)),
                     first_one[:40]))
    print(T('\n  Nothing was changed.'))
    return 0


def first_free_audio_track(tl):
    """Return the first audio track with nothing on it."""
    for i in range(1, tl.GetTrackCount("audio") + 1):
        if not (tl.GetItemListInTrack("audio", i) or []):
            return i
    return tl.GetTrackCount("audio") + 1


def clip_signature(c):
    """Return the properties Resolve might reject a file for.

    Resolve does not say why it refuses to insert something. The only way
    left is to put the cameras side by side and see how the rejected one
    differs from the accepted ones.
    """
    if c is None:
        return T('not in the media pool')
    try:
        p = c.GetClipProperty() or {}
    except Exception:
        return T('no information')
    if not isinstance(p, dict):
        return str(p)[:120]
    parts = []
    for name in ("Format", "Video Codec", "Resolution", "FPS", "Audio Codec",
                 "Audio Ch", "Frames", "Duration", 'Start TC', "End TC"):
        if p.get(name):
            parts.append("%s %s" % (name, p[name]))
    return ", ".join(parts) or T('no information')


def timeline_items_per_camera(tl, cameras):
    """Return which timeline clip belongs to which camera.

    Returns {camera track name: [TimelineItem, ...]}.

    Where two cameras write the same file name the name cannot tell them
    apart, and the last one read would take both. What can tell them
    apart here is the video track: every camera gets one of its own, in
    the order they were inserted -- the same order the renaming below
    goes by. Without that the first of the two was reported as not
    inserted although its clip was on the timeline, so the collision
    arrived twice: once correctly, and once as a false alarm.
    """
    after_file = cameras_by_file_name(cameras)
    doubled = {}
    for cam in cameras:
        doubled.setdefault(
            os.path.basename(cam["file"] or cam["source"]), []).append(cam)
    by_track = dict(enumerate(cameras, 1))
    assignment = {}
    for track in range(1, tl.GetTrackCount("video") + 1):
        for item in (tl.GetItemListInTrack("video", track) or []):
            try:
                name = item.GetName() or ""
            except Exception:
                continue
            cam = after_file.get(name)
            if cam is not None and len(doubled.get(name) or []) > 1:
                cam = by_track.get(track, cam)
            if cam:
                assignment.setdefault(cam["track"], []).append(item)
    return assignment


# Resolve's clip colours, sorted by distinguishability. With two speakers the
# first two should lie as far apart as possible; a third should stand out from
# both, and so on.
#
# Which names Resolve accepts appears in no documentation I know of. So nothing
# is guessed: SetClipColor reports whether it worked, and one pass establishes
# the usable list.
CLIP_COLOURS = ["Blue", "Orange", "Green", "Pink", "Yellow", "Violet",
              "Teal", "Brown", "Lime", "Navy", "Apricot", "Purple",
              "Olive", "Chocolate", "Beige", "Tan"]
# The wide shot is not a voice but the fallback, so it gets a calm colour that
# stays out of the speakers' way. In Resolve that remains "Tan": the clip
# colour should not shift under already graded projects. On a dark background
# the interface uses a different shade -- see CLIP_COLOURS_RGB_DARK.
COLOUR_WIDE_SHOT = "Tan"
# Approximations of the clip colours for the cut band in the interface. They
# should be recognisable, not exact -- what Resolve makes of them is what
# counts.
CLIP_COLOURS_RGB = {
    "Blue": "#3f7fbf", "Cyan": "#3fbfbf", "Green": "#3fbf5f",
    "Yellow": "#d9c23a", "Red": "#bf3f3f", "Pink": "#d98fbf",
    "Purple": "#8f5fbf", "Fuchsia": "#bf3f8f", "Rose": "#d99f9f",
    "Lavender": "#a89fd9", "Sky": "#7fbfd9", "Mint": "#7fd9a8",
    "Lemon": "#d9d97f", "Sand": "#d9bf8f", "Cocoa": "#8f6f4f",
    "Cream": "#e8dfc0", "Orange": "#d98f3f", "Violet": "#7f5fbf",
    "Teal": "#3f8f8f", "Brown": "#8f5f3f", "Lime": "#9fd93f",
    "Navy": "#3f4f8f", "Apricot": "#e8b07f", "Olive": "#7f8f3f",
    "Chocolate": "#6f4f3f", "Beige": "#ddd0b0", "Tan": "#c8b088"}
# On a dark background the dark shades all but vanish. These are lightened far
# enough to sit at least 50 CIE76 from the sheet -- computed, not by feel. All
# others stay as they are.
#
# "Tan" is there for a different reason: as a warm sand brown it sits too close
# to the orange of the second camera (34.9 CIE76), and that shows even more on
# dark than on light. The pale sage keeps at least 52.9 from every speaker
# colour and still stays calm. In Resolve the clip is still called Tan; this is
# only the display.
CLIP_COLOURS_RGB_DARK = {
    "Brown": "#9d6945", "Chocolate": "#a57760", "Cocoa": "#9d7a57",
    "Navy": "#4c5fac", "Teal": "#429696", "Tan": "#b5c9b1"}
# And the other way round: on white the lightest shade disappears.
CLIP_COLOURS_RGB_LIGHT = {"Beige": "#ccb989"}
# Set by the interface when the system is in dark mode.
ON_DARK = [False]


def usable_clip_colours(item, wanted):
    """Return the clip colour names this Resolve accepts.

    Tried on a single clip whose original colour is restored afterwards.
    Better to look once than to guess a list that changes between versions.
    """
    try:
        before_value = item.GetClipColor()
    except Exception:
        return list(wanted)
    good = []
    for name in wanted:
        try:
            if item.SetClipColor(name):
                good.append(name)
        except Exception:
            pass
    try:
        if before_value:
            item.SetClipColor(before_value)
        else:
            item.ClearClipColor()
    except Exception:
        pass
    return good or list(wanted)


def colour_per_camera(cameras, colours):
    """Assign a colour to each camera.

    The wide shot colour is set aside first so no speaker gets the same one,
    which would make the fallback look like a person. The rest are handed
    out in order, and that order is sorted so the first two lie furthest
    apart.

    Only the first wide shot gets that colour. Two of them used to share
    it, and the legend then showed "Wide shot 1" and "Wide shot 2"
    behind two squares of the same colour -- two names for what looked
    like one camera. The second one takes a speaker colour instead: it
    is a camera of its own in the band, which is what it is.
    """
    if not colours:
        return {}, 0
    wide_shot_colour = COLOUR_WIDE_SHOT if COLOUR_WIDE_SHOT in colours else colours[-1]
    rest = [f for f in colours if f != wide_shot_colour] or [wide_shot_colour]
    wides = [cam for cam in cameras if cam.get("wide")]
    # The further wide shots go to the back of the queue, so nobody's
    # colour moves because a second wide shot appeared.
    row = [cam for cam in cameras if not cam.get("wide")] + wides[1:]
    assigned = {}
    for i, cam in enumerate(row):
        assigned[cam["track"]] = rest[i % len(rest)]
    for cam in wides[:1]:
        assigned[cam["track"]] = wide_shot_colour
    # More angles than colours means the sequence repeats. That should not
    # happen silently.
    duplicate = max(0, len(row) - len(rest))
    return assigned, duplicate


def colour_clips_by_camera(tl, cameras):
    """Colour every cut in the colour of its camera.

    The edit window then shows at a glance who is on screen when and how the
    rhythm runs, without a single marker.
    """
    assignment = timeline_items_per_camera(tl, cameras)
    if not assignment:
        return
    first_one = next(iter(next(iter(assignment.values()))), None)
    if first_one is None:
        return
    colours = usable_clip_colours(first_one, CLIP_COLOURS)
    assigned, duplicate = colour_per_camera(cameras, colours)
    applied, failed = {}, 0
    for track, item in assignment.items():
        colour = assigned.get(track)
        if not colour:
            continue
        for x in item:
            try:
                if x.SetClipColor(colour):
                    applied[track] = applied.get(track, 0) + 1
                else:
                    failed += 1
            except Exception:
                failed += 1
    if not applied:
        print(T('    Clip colours could not be set.'))
        return
    print(T('    Colours per angle:'))
    for track in sorted(applied, key=lambda s: -applied[s]):
        print("      %-28s %-10s %s"
              % (track, assigned.get(track) or "?",
                 TN(applied[track], '%s clip', '%s clips')
                 % group_text(applied[track])))
    if duplicate:
        print(TN(duplicate,
                 '      More angles than colours -- %s colour occurs twice.',
                 '      More angles than colours -- %s colours occur twice.')
              % group_text(duplicate))
    if failed:
        print(TN(failed, '      %s clip left without a colour.',
                 '      %s clips left without a colour.')
              % group_text(failed))


def create_colour_groups(p, tl, cameras):
    """Create one colour group per camera and put all its clips in.

    That means grading once per camera instead of once per cut: switch the
    node editor to "Group Pre-Clip" and the correction applies to every clip
    of the group. Switched to "Clip" it applies to that one cut only -- both
    side by side, computed in that order. This is why remote grades stay
    off: they would glue the clip level together as well.

    Groups can still be changed later, unlike remote grades, which would
    have to be set before inserting.
    """
    existing = {}
    try:
        for g in (p.GetColorGroupsList() or []):
            existing[g.GetName()] = g
    except Exception:
        pass
    assignment = timeline_items_per_camera(tl, cameras)
    if not assignment:
        print(T('  No clips found for colour groups.'))
        return
    done = {}
    for name in sorted(assignment):
        group = existing.get(name)
        if group is None:
            try:
                group = p.AddColorGroup(name)
            except Exception as e:
                print(T('  Colour group %r cannot be created: %s') % (name, e))
                continue
        if not group:
            print(T('  Colour group %r cannot be created.') % name)
            continue
        existing[name] = group
        good = 0
        for item in assignment[name]:
            try:
                if item.AssignToColorGroup(group):
                    good += 1
            except Exception:
                pass
        done[name] = (good, len(assignment[name]))
    # One line is enough: the clip counts are already with the colours.
    incomplete = [n for n, (g, total) in done.items() if g < total]
    if done and not incomplete:
        print(T('    Colour groups: %s -- all clips assigned')
              % ", ".join(sorted(done)))
    for n in incomplete:
        print(T('    Colour group %-24s only %s of %s clips')
              % (n, group_text(done[n][0]), group_text(done[n][1])))


def insert_intro_and_outro(mp, tl, d, clips, fps, origin, lead_in):
    """Insert the two clips, after the content.

    The content has to be in place first, otherwise the second track they
    belong on does not exist yet.
    """
    applied = []
    # The second video track does not appear by itself. Without it
    # AppendToTimeline accepts the clip and puts it nowhere.
    needs_audio = any((d.get(a) or {}).get("has_audio")
                      for a in ("intro", "outro"))
    for kind_track, at_least in (("video", 2), ("audio", 2 if needs_audio
                                                else 0)):
        try:
            while at_least and tl.GetTrackCount(kind_track) < at_least:
                if not tl.AddTrack(kind_track):
                    print(T('    %s track %d could not be created.')
                          % (kind_track, at_least))
                    break
        except Exception as e:
            print(T('    %s track could not be created: %s') % (kind_track, e))
    for kind, where_to in ((TYPE_INTRO, label_of(TYPE_INTRO)),
                           (TYPE_OUTRO, label_of(TYPE_OUTRO))):
        entry = d.get(kind)
        if not entry:
            continue
        clip = clips.get(entry["source"])
        if clip is None:
            print(T('    %s could not be imported.') % where_to)
            continue
        L = float(entry.get("duration") or 0.0)
        meeting_point = _meeting_point(entry, kind)
        word0, word1 = first_and_last_word(d)
        if kind == "intro":
            W = word0 if word0 is not None else 0.0
            # The end of the intro audio meets the first word.
            spot = seconds_to_frames(max(0.0, W - meeting_point), fps)
        else:
            # The start of the outro audio meets the end of the last word.
            end = word1 if word1 is not None else float(d.get("length_s") or 0)
            spot = max(0, lead_in + seconds_to_frames(end - meeting_point, fps))
        item = [{"mediaPoolItem": clip, "trackIndex": 2,
                   "recordFrame": origin + spot, "mediaType": 1}]
        if entry.get("has_audio"):
            item.append({"mediaPoolItem": clip, "trackIndex": 2,
                           "recordFrame": origin + spot, "mediaType": 2})
        if not mp.AppendToTimeline(item):
            print(T('    %s could not be inserted.') % where_to)
            continue
        applied.append((kind, where_to, spot, L, bool(entry.get("has_audio")),
                        meeting_point))
    if not applied:
        return
    try:
        tl.SetTrackName("video", 2, "Intro / Outro")
        tl.SetTrackName("audio", 2, "Audio Intro / Outro")
    except Exception:
        pass
    # Check rather than trust: the interface reports success even when the clip
    # lands somewhere else.
    try:
        up_v2 = tl.GetItemListInTrack("video", 2) or []
        print(TN(len(up_v2), '    V2 now holds %s clip: %s',
                 '    V2 now holds %s clips: %s')
              % (group_text(len(up_v2)),
                 ", ".join((x.GetName() or "?") for x in up_v2) or T('none')))
    except Exception as e:
        print(T('    V2 could not be read back: %s') % e)
    for kind, where_to, spot, L, having_audio, meeting_point in applied:
        print(T('    %-10s from %s, %s long%s')
              % (where_to, as_hms(spot / float(fps)), as_hms(L),
                 T(', audio on A2') if having_audio else T(', no audio')))
        if having_audio:
            print(T('               Audio %s at %s -- there it meets the '
                    '%s word.')
                  % (T('ends') if kind == TYPE_INTRO else T('begins'),
                     as_hms((spot / float(fps)) + meeting_point),
                     T('first') if kind == TYPE_INTRO else T('last')))
    print(T('      Both clips stay uncut; they overlap the content.\n      '
            'The dissolve sits in the overlap -- exactly where is your '
            'decision in Resolve.\n      (The Resolve scripting interface '
            'cannot create transitions.)'))


def build_cut_timeline(mp, tl, cut, cameras, clips, d, mix=None,
                             lead_in=0):
    """Build the finished camera cut.

    Picture comes from the cameras, audio from the mix. The picture pieces
    go onto the timeline without their audio, otherwise a different audio
    track would sit under every cut and the sound would jump. The overall
    mix runs underneath in one piece.
    """
    fps, origin = timeline_origin(d)
    set_timeline_start(tl, d.get("start_tc"))
    print(T('  Start %s -- every shot is placed against it.')
          % frames_to_timecode(origin, fps, bool(d.get("drop_frame"))))
    after_camera = {}
    for cam in cameras:
        c = clips.get(cam["file"])
        if c is not None:
            after_camera[cam["camera"]] = (c, cam.get("offset") or 0.0,
                                        cam.get("duration") or 0.0,
                                        own_frame_rate(
                                            cam.get("fps") or fps))
    # Fallback order: the wide shot first, then the rest.
    fallback = cameras_in_track_order(cameras)
    item, skipped, replaced = [], set(), 0

    def piece(name, t0, length):
        """Return the piece if it fits this camera, otherwise nothing.

        *length* arrives in Timeline frames and is converted to the
        camera's own. Rounding both separately mostly works and is
        occasionally one frame off, and then the cut has a gap.
        """
        entry = after_camera.get(name)
        if entry is None:
            return None
        c, offset, duration, own = entry
        # Counted in the camera's own rate, not the Timeline's: at the
        # Timeline's, a 24 camera in a 30 Timeline shows a quarter of the
        # running time too late and the shot comes out a quarter too long.
        start_frame = seconds_to_frames(t0 - offset, own)
        end_frame = start_frame + frames_of_the_file(length, fps, own)
        if length <= 0 or start_frame < 0:
            return None
        if duration and end_frame > seconds_to_frames(duration, own):
            return None
        # endFrame counts exclusively -- with end_frame - 1 exactly one frame
        # was missing at the end of every cut and a gap opened between them.
        return {"mediaPoolItem": c, "startFrame": start_frame, "endFrame": end_frame}

    # What the shot before left uncovered on the Timeline. A camera's own
    # frames rarely divide the Timeline's, so a shot stops a little short
    # of its place; the next one starts there instead of at the frame the
    # cut names, and nothing is ever left black or pushed along.
    carry = 0
    for e in cut:
        a, b = seconds_to_frames(e["start"], fps), seconds_to_frames(e["end"], fps)
        if b <= a:
            continue
        at = a - carry
        length = b - at
        began = e["start"] - carry / float(fps)
        # In the timeline: from the window start. In the file: later by as much
        # as this camera started later. Where it was not yet or no longer
        # running, the wide shot takes the place, otherwise a gap would open.
        used = e["camera"]
        part = piece(used, began, length)
        if part is None:
            for cam in fallback:
                if cam["camera"] == e["camera"]:
                    continue
                part = piece(cam["camera"], began, length)
                if part is not None:
                    used, replaced = cam["camera"], replaced + 1
                    break
        if part is None:
            skipped.add(T('%s (%s to %s)')
                              % (e["camera"], as_hms(e["start"]), as_hms(e["end"])))
            carry = 0
            continue
        part.update({"trackIndex": 1, "recordFrame": origin + lead_in + at,
                     "mediaType": 1})
        item.append(part)
        carry = length - timeline_frames_of(
            part["endFrame"] - part["startFrame"], fps,
            after_camera[used][3])
    if replaced:
        print(T('    %sx the intended camera was not running -- a '
                'different one is there.') % group_text(replaced))
    for e in sorted(skipped):
        print(T('    Left without picture: %s') % e)
    if not item:
        print(T('  No cut left -- the Timeline stays empty.'))
        return tl
    put = mp.AppendToTimeline(item)
    tl.SetTrackName("video", 1, "Camera cut")
    # Counted from what is on the timeline, not from what was sent. The
    # camera timeline checks every insert; this one used to report the
    # length of the whole cut list even where Resolve had taken nothing,
    # so a timeline that was black for its whole length was announced as
    # finished.
    landed = tl.GetItemListInTrack("video", 1) or []
    if not landed:
        print(as_warn(T('  Resolve took no picture at all -- the Timeline '
                        'is empty. Nothing\n  else is built on it.')))
        return tl
    if len(landed) < len(item):
        print(as_warn(T('  Only %s of %s shots are on the Timeline.')
                      % (group_text(len(landed)), group_text(len(item)))))
    on_it = sum(float(x.GetDuration() or 0) for x in landed) / max(
        1.0, float(resolve_timeline_rate(d.get("fps"))))
    print(T('  %s shots, %s s in total, without their audio.')
          % (group_text(len(landed)), decimal_text("%.1f" % on_it)))

    if mix is None:
        print(T('  No Full-Mix found -- the Timeline stays silent.'))
        return tl
    file_path, source_text = mix
    c = clips.get(file_path)
    if c is None:
        print(T('  The Full-Mix could not be imported.'))
        return tl
    # Only the stored mix begins at the In point. The two fallbacks are camera
    # files, and a camera that was already rolling carries that much extra
    # sound at its head; laid down untrimmed the whole mix would run
    # against the picture by exactly that camera's offset.
    mix_cam = next((cam for cam in (d.get("cameras") or [])
                    if cam.get("file") == file_path), None)
    # A camera file again, so its frames are its own as well.
    mix_fps = own_frame_rate(
        (mix_cam.get("fps") or fps) if mix_cam else fps)
    head = (seconds_to_frames(-(mix_cam.get("offset") or 0.0), mix_fps)
            if mix_cam else 0)
    place = {"mediaPoolItem": c, "trackIndex": 1,
             "recordFrame": origin + lead_in, "mediaType": 2}
    if head > 0:
        # endFrame counts exclusively, as for the picture pieces above.
        last = seconds_to_frames(mix_cam.get("duration") or 0.0, mix_fps)
        place["startFrame"] = head
        if last > head:
            place["endFrame"] = last
    applied = mp.AppendToTimeline([place])
    if not applied:
        print(T('  The Full-Mix could not be inserted.'))
        return tl
    tl.SetTrackName("audio", 1, "Audio-Full-Mix")
    print(T('  Audio: Full-Mix in one piece on A1 (%s).') % source_text)
    return tl


def earliest_offset(cameras):
    """Return how far before the In point the earliest camera starts (<= 0)."""
    return min([cam.get("offset") or 0.0 for cam in (cameras or [])] + [0.0])


def add_speaker_markers(tl, speaker, d, from_s=0.0):
    """Add the speaker segments as markers, one colour per person.

    *from_s* is the start of the timeline relative to the In point; negative on
    the multicam timeline, which begins at the earliest camera.
    """
    fps, _origin = timeline_origin(d)
    # Markers count differently from clips: from the start of the timeline
    # rather than from midnight, so no offset here. Resolve allows only one
    # marker per frame. Two speakers starting at once would be a silent loss,
    # so they are collected first, the names merged, and moved on by a frame
    # where necessary.
    on_spot, colour_of = {}, {}
    for idx, s in enumerate(speaker):
        colour_of[s["name"]] = MARKER_COLOURS[idx % len(MARKER_COLOURS)]
        for a, b in s["sections"]:
            e = on_spot.setdefault(seconds_to_frames(a - from_s, fps),
                                     {"names": [], "length": 1})
            e["names"].append(s["name"])
            e["length"] = max(e["length"], seconds_to_frames(b - a, fps))
    applied, lost = 0, 0
    for frames in sorted(on_spot):
        e = on_spot[frames]
        colour = colour_of.get(e["names"][0], MARKER_COLOURS[0])
        for shift in range(0, 10):
            if tl.AddMarker(frames + shift, colour, " + ".join(e["names"]),
                            "", max(1, e["length"])):
                applied += 1
                break
        else:
            lost += 1
    print(TN(applied, '  %s marker set%s.', '  %s markers set%s.')
          % (group_text(applied),
             T(', %s not (no free picture)') % group_text(lost)
             if lost else ""))
    return applied


class Transcript(object):
    """Write everything printed to a file as well.

    A lot goes wrong in the Resolve part that only shows afterwards: which
    timeline was created, which settings Resolve accepted, which file was
    not found again.
    """

    def __init__(self, file_path):
        self.file = open(file_path, "w", encoding="utf-8")
        self.old = sys.stdout

    def write(self, text):
        self.old.write(text)
        # The kind marker is for the screen; the file gets plain text.
        self.file.write(strip_marks(text))

    def flush(self):
        self.old.flush()
        self.file.flush()

    def __enter__(self):
        sys.stdout = self
        return self

    def __exit__(self, *_):
        sys.stdout = self.old
        self.file.close()


def build_resolve_project(source, project_carry_on=None, project_name=None,
                  sources=False, log=None):
    """Build a Resolve project from the handover file.

    *source* is the path to the ..._resolve.json or its parsed contents.
    """
    d = source
    source_path = None
    if not isinstance(d, dict):
        source_path = source
        with open(source, encoding="utf-8") as f:
            d = json.load(f)
        if log is None:
            log = os.path.splitext(source)[0] + "_log.txt"
        complaint = format_complaint(d)
        if complaint:
            print(as_bad(T('Abort: %s') % complaint))
            return 1
        d["_source_path"] = source_path
    if log:
        # Only opening the file may fail here. Wrapping the build itself
        # would run it a second time on any disk error.
        try:
            written = Transcript(log)
        except OSError as e:
            written = None
            print(T('  Transcript not possible (%s) -- it runs anyway.')
                  % e)
        if written is not None:
            with written:
                code = build_resolve_project(d, project_carry_on, project_name,
                                     sources, "")
            print(T('  Transcript: %s') % log)
            return code
    source_path = d.pop("_source_path", None)
    if source_path:
        bad = refresh_cut_list(d, source_path)
        if bad:
            print(T('\n  STOPPED: %s') % bad)
            return 1
    name = project_name or d.get("production") or 'Production'
    cameras = []
    for cam in (d.get("cameras") or []):
        file_path = cam.get("source") if sources else (cam.get("file")
                                                or cam.get("source"))
        if not file_path:
            continue
        e = dict(cam)
        e["file"] = file_path
        cameras.append(e)
    if not cameras:
        print(T('  No cameras in the handover -- nothing to build.'))
        return 1

    print(as_head("\nRESOLVE"))
    r = connect_to_resolve()
    print("  %s %s" % (r.GetProductName(), r.GetVersionString()))
    pm = r.GetProjectManager()
    p, kind = open_or_create_project(pm, name, project_carry_on)
    # Held under its own name: the loop over intro and outro further down
    # binds "kind" again, and the render job still has to know whether this
    # project is one from a minute ago or one somebody set up.
    project_is_new = kind == "created"
    if kind == "update":
        # Only the cut timeline. The multicam one is not touched here: it
        # carries manual work -- the multicam clip is converted from it by
        # hand -- and further down there is a check that leaves it alone
        # when the same cameras still sit on it in the same order. Deleting
        # it up here made that check unreachable and threw the work away.
        gone, stayed = refresh_resolve_timelines(
            p, p.GetMediaPool(), ["%s Cut" % name])
        if gone:
            print(T('  Deleted: %s -- being rebuilt now.')
                  % ", ".join(repr(n) for n in gone))
        if stayed:
            print(as_warn(T('  Caution: %s could not be deleted -- the new '
                            'Timeline therefore gets\n  an addition to its '
                            'name.')
                          % ", ".join(repr(n) for n in stayed)))
        if not gone and not stayed:
            print(T('  No such Timeline existed yet -- it is only built.'))
        print(T('  The media pool stays as it is.'))

    print(T('\n  Settings'))
    apply_project_settings(p, d)
    # The meter needs a scale even where nothing was adjusted, and -16 is the
    # one for web and podcast. A display adjusts nothing, so it may stand
    # there -- but it must not read as if the run had normalised to it, so
    # the line above says what happened.
    if d.get("lufs") is None:
        print(T('    Loudness was not adjusted -- the target below is only '
                'what the meter\n    measures against.'))
    set_loudness_target(p, d.get("lufs") or -16.0)
    # Always set, never skipped: a project from an earlier run would still have
    # remote grades on.
    set_remote_grades(p)
    if kind == "keep":
        # The setting only takes effect for clips added afterwards. What is
        # already there keeps its remote grade.
        print(T('    Clips from an earlier run are still tied to their '
                'remote grades. On the\n    colour page right-click a '
                'thumbnail > '
                '"Copy Remote Grades to Local"\n    (takes the correction '
                'along) or "Use Local Grades". New Timelines\n    do not '
                'need this.'))

    print("\n  Import")
    mp = p.GetMediaPool()
    # The overall mix comes along as its own file where it exists, so nobody
    # has to guess which audio track in which camera is the right one.
    mix = mix_file_from_handover(d)
    to_insert = [cam["file"] for cam in cameras]
    if mix[0] and mix[0] not in to_insert:
        to_insert.append(mix[0])
    for kind in ("intro", "outro"):
        entry = d.get(kind)
        if entry and entry.get("source") not in to_insert:
            to_insert.append(entry["source"])
    clips = import_media(mp, to_insert)

    # What gets built depends on what is there. A camera cut needs the speaker
    # statistics; a multicam clip needs more than one camera. Missing either,
    # that timeline is not created at all -- an empty one helps nobody.
    only_one = len(cameras) < 2
    tl = None
    if d.get("cut"):
        print(T('\n  Timeline with the finished cut'))
        tl = create_timeline(mp, "%s Cut" % name)
        # No speaker markers on a cut of several cameras: the picture
        # already says who speaks, and they would only sit around under
        # the clips. With one camera it is the other way round, and the
        # only_one branch below sets them on this very timeline.
        _fps, _origin = timeline_origin(d)
        lead_in = lead_in_offset(mp, tl, d, clips, _fps, _origin)
        build_cut_timeline(mp, tl, d["cut"], cameras, clips, d,
                                 mix if mix[0] else None, lead_in)
        colour_clips_by_camera(tl, cameras)
        insert_intro_and_outro(mp, tl, d, clips, _fps, _origin, lead_in)
        create_colour_groups(p, tl, cameras)
        queue_render_job(p, tl, d, output_folder_from(d), name,
                         project_is_new)
    elif only_one:
        # One camera, one audio track: nothing to switch between. The straight
        # timeline is then the right one -- picture in one piece, mix beneath.
        print(T('\n  Timeline: the camera in one piece, the mix below'))
        tl = create_timeline(mp, "%s Cut" % name)
        length = float(d.get("length_s") or 0.0) or float(
            cameras[0].get("duration") or 0.0)
        _fps, _origin = timeline_origin(d)
        lead_in = lead_in_offset(mp, tl, d, clips, _fps, _origin)
        build_cut_timeline(
            mp, tl, [{"start": 0.0, "end": length,
                      "camera": cameras[0]["camera"]}],
            cameras, clips, d, mix if mix[0] else None, lead_in)
        colour_clips_by_camera(tl, cameras)
        insert_intro_and_outro(mp, tl, d, clips, _fps, _origin, lead_in)
        create_colour_groups(p, tl, cameras)
        queue_render_job(p, tl, d, output_folder_from(d), name,
                         project_is_new)
    else:
        print(T('\n  No camera cut in the handover -- without speaker '
                'statistics there is none.\n  Only the Timeline for the '
                'multicam clip is built.'))

    if only_one:
        print(T('\n  Only one camera -- a multicam clip would be pointless.'))
        # The markers then belong on the cut timeline. They sat on the
        # multicam timeline alone, and with one camera there is none, so
        # a single-camera run said the passages travelled as markers and
        # set not one. Whoever reframes a 360 shot by hand needs to see
        # where each person speaks.
        if tl is not None:
            if d.get("speakers"):
                add_speaker_markers(tl, d["speakers"], d)
            p.SetCurrentTimeline(tl)
        return 0

    print(T('\n  Timeline for the multicam clip: all cameras, uncut'))
    ordered = cameras_in_track_order(cameras)
    existing = multicam_timeline_unchanged(p, "%s Multicam" % name, ordered)
    if existing is not None:
        print(T('  It already exists, with the same cameras in the same '
                'order -- it stays\n  untouched. Whoever wants a new one '
                'deletes it in Resolve.'))
        if tl is not None:
            p.SetCurrentTimeline(tl)
        print(T(HINT_MULTICAM)
              % (name, "".join("\n    V%-3d %s" % (i, cam["track"])
                               for i, cam in enumerate(ordered, 1))))
        return 0
    if find_timeline(p, "%s Multicam" % name) is not None:
        # It is there but holds other cameras. It is not deleted: whatever
        # was done to it by hand is worth more than a tidy name, and the
        # multicam clip made from it would be gone with it.
        print(as_warn(T('  A Timeline of this name is there with other '
                        'cameras on it. It stays;\n  the new one is built '
                        'beside it under a name of its own.')))
    tl2 = create_timeline(mp, "%s Multicam" % name)
    if ordered and ordered[0] is not cameras[0]:
        print(T('  %s goes on video track 1 -- there the first audio track '
                'carries the\n  Full-Mix, and video track 1 becomes angle 1.')
              % ordered[0]["camera"])
    build_camera_timeline(mp, tl2, ordered, clips, d)
    colour_clips_by_camera(tl2, ordered)
    create_colour_groups(p, tl2, ordered)
    # Converting to a multicam clip is a one-way operation; a new run
    # rebuilds this timeline from the handover file.
    if d.get("speakers"):
        add_speaker_markers(tl2, d["speakers"], d, from_s=earliest_offset(ordered))

    p.SetCurrentTimeline(tl if tl is not None else tl2)
    print(T(HINT_MULTICAM)
          % (name, "".join("\n    V%-3d %s" % (i, cam["track"])
                           for i, cam in enumerate(ordered, 1))))
    return 0


