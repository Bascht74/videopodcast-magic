# -*- coding: utf-8 -*-
"""The bearings: where each thing sits, and how each one reads.

Read out of the folder beside the program by beside(). It cannot import
the file it was cut out of -- that file is still being read -- so the
program is handed in and every name used out of it is bound below.
"""

# beside() puts the program here before this file is read.
PROGRAM = PROGRAM

# What this piece uses out of the program, bound once. Seven names are
# missing; the two blocks under the list say which and why.

AUDIO_SUFFIXES = PROGRAM.AUDIO_SUFFIXES
ByFile = PROGRAM.ByFile
CAMERA_MATCH_ENOUGH = PROGRAM.CAMERA_MATCH_ENOUGH
COLOURS = PROGRAM.COLOURS
COLOURS_DARK = PROGRAM.COLOURS_DARK
COLOURS_LIGHT = PROGRAM.COLOURS_LIGHT
CUT_CHOICES = PROGRAM.CUT_CHOICES
CUT_FIELDS = PROGRAM.CUT_FIELDS
FileSet = PROGRAM.FileSet
IGNORE_AUDIO = PROGRAM.IGNORE_AUDIO
MIX_ONLY = PROGRAM.MIX_ONLY
SOUND_MATCH_ENOUGH = PROGRAM.SOUND_MATCH_ENOUGH
T = PROGRAM.T
TN = PROGRAM.TN
TRAILING_NUMBER = PROGRAM.TRAILING_NUMBER
VERSION = PROGRAM.VERSION
VIDEO_SUFFIXES = PROGRAM.VIDEO_SUFFIXES
WEAK_MATCH = PROGRAM.WEAK_MATCH
align_envelopes = PROGRAM.align_envelopes
as_head = PROGRAM.as_head
as_hms = PROGRAM.as_hms
as_warn = PROGRAM.as_warn
cannot_be_placed = PROGRAM.cannot_be_placed
channel_count = PROGRAM.channel_count
decode_audio = PROGRAM.decode_audio
expand_chains_to_tracks = PROGRAM.expand_chains_to_tracks
ffprobe_json = PROGRAM.ffprobe_json
files_with_no_place = PROGRAM.files_with_no_place
find_continuation_files = PROGRAM.find_continuation_files
finished_tracks_find = PROGRAM.finished_tracks_find
fit_places_it = PROGRAM.fit_places_it
format_complaint = PROGRAM.format_complaint
gcc_phat_offset = PROGRAM.gcc_phat_offset
glob = PROGRAM.glob
json = PROGRAM.json
number_text = PROGRAM.number_text
os = PROGRAM.os
parallel_map = PROGRAM.parallel_map
parse_timecode = PROGRAM.parse_timecode
path_key = PROGRAM.path_key
place_track_on_axis = PROGRAM.place_track_on_axis
re = PROGRAM.re
shapes_match = PROGRAM.shapes_match
subprocess = PROGRAM.subprocess
sys = PROGRAM.sys
time = PROGRAM.time
timecode_string = PROGRAM.timecode_string
video_envelope = PROGRAM.video_envelope
words_from_handover = PROGRAM.words_from_handover


# Six of the seven stand below the place this piece is read, so a copy
# taken here would find nothing: they are read as PROGRAM.<name>.

# numpy is the seventh: the program binds the real module only when
# the first sum asks, which a copy taken up there would never see.
class LateNumpy:
    """Stands in for the program's numpy until a sum wants it."""

    def __getattr__(self, name):
        global np
        got = getattr(PROGRAM.np, name)
        np = PROGRAM.np
        return got


np = LateNumpy()


#---------------------------------------- What a run works out

# =====================================================================
#  Metrics and colour comparison -- what was measured at the end of an
#  episode belongs in a file, not only in the log the next run wipes.
# =====================================================================

def measure_picture_levels(file_path, spots=5, t0=0.0, t1=None):
    """Measure brightness and colour balance of a camera file from samples.

    Returns {"y", "u", "v", "sat"} or None. U and V are the colour
    differences -- 128 is neutral, above and below is the cast. A few
    frames are enough to compare cameras.
    """
    if t1 is None or t1 <= t0:
        try:
            t1 = float(ffprobe_json(file_path).get("format", {}).get("duration") or 0.0)
        except Exception:
            t1 = 0.0
    if t1 <= t0:
        return None
    points = [t0 + (t1 - t0) * (k + 0.5) / spots for k in range(spots)]
    values = {"y": [], "u": [], "v": [], "sat": []}
    for time in points:
        try:
            # A seek point handed to ffmpeg. A German decimal comma
            # here is a different second, or none it will accept.
            p = subprocess.run(
                ["ffmpeg", "-v", "error", "-ss", "%.3f" % time, "-i", file_path,
                 "-frames:v", "1", "-vf", "signalstats,metadata=print:file=-",
                 "-f", "null", "-"], capture_output=True, timeout=120)
        except Exception:
            continue
        text = p.stdout.decode("utf-8", "replace")
        for api_key, label in (("y", "YAVG"), ("u", "UAVG"),
                                  ("v", "VAVG"), ("sat", "SATAVG")):
            hit = re.search(r"signalstats\.%s=([\d.]+)" % label, text)
            if hit:
                values[api_key].append(float(hit.group(1)))
    if not values["y"]:
        return None
    return dict((k, sum(v) / len(v)) for k, v in values.items() if v)


def compare_picture_levels(cameras, t0=0.0, t1=None):
    """Report how far the cameras sit apart in colour.

    Compared with the average of all, not with a target: which brightness
    is right is for the grade, what shows in the edit is the distance
    between cameras. Returns [(name, values, deviations)] and the means.
    """
    measured = []
    for cam in cameras:
        file_path = cam.get("file") or cam.get("source")
        if not file_path or not os.path.exists(file_path):
            continue
        values = measure_picture_levels(file_path, t0=t0, t1=t1)
        if values:
            measured.append((cam.get("track") or cam.get("camera") or
                             os.path.basename(file_path), values))
    if len(measured) < 2:
        return measured, None
    middle = {}
    for api_key in ("y", "u", "v", "sat"):
        every = [values[api_key] for _n, values in measured if api_key in values]
        if every:
            middle[api_key] = sum(every) / len(every)
    return measured, middle


def report_picture_comparison(cameras, t0=0.0, t1=None):
    """Write the colour comparison to the log. Returns the measurements."""
    measured, middle = compare_picture_levels(cameras, t0, t1)
    if not measured:
        return []
    print(as_head(T('\nCAMERA COLOUR COMPARISON')))
    print("  %-24s %8s %8s %8s   %s"
          % (T('Camera'), T('Bright.'), T('Colour U'), T('Colour V'),
             T('Distance to mean')))
    lines = []
    for name, values in measured:
        if middle:
            dy = values.get("y", 0) - middle.get("y", 0)
            du = values.get("u", 0) - middle.get("u", 0)
            dv = values.get("v", 0) - middle.get("v", 0)
            # Padded as text, not formatted as a number: the widths are
            # what keep this a table. Levels up to 1023 keep their
            # columns, and only the last field can grow.
            distance = "%6s  %5s  %5s" % (number_text(dy, 1, plus=True),
                                          number_text(du, 1, plus=True),
                                          number_text(dv, 1, plus=True))
        else:
            dy = du = dv = 0.0
            distance = T('-- only one camera')
        print("  %-24s %8s %8s %8s   %s"
              % (name[:24], number_text(values.get("y", 0), 1),
                 number_text(values.get("u", 0), 1),
                 number_text(values.get("v", 0), 1), distance))
        lines.append((name, values, (dy, du, dv)))
    if middle:
        spread = max(abs(line[2][0]) for line in lines)
        if spread > 12:
            print(as_warn(T('  Caution: %s steps of brightness '
                            'difference -- visible when switching.')
                          % number_text(spread, 0)))
        else:
            print(T('  The cameras lie close together (at most %s steps '
                    'of brightness).') % number_text(spread, 0))
    return lines


def preview_handover(state):
    """Read the run's handover for the preview, or answer None.

    A finished run beats what the window worked out: its tracks lie on
    one axis and auphonic.com has de-bled them. So the measurement taken
    from the raw tracks is dropped rather than shown beside it.
    """
    d, js = None, state.get("resolve_json")
    state["preview_from"] = None
    if js:
        try:
            with open(js, encoding="utf-8") as f:
                d = json.load(f)
            state["preview_from"] = handover_mark(js)
        except (OSError, ValueError):
            d = None
    state["cut_basis"] = (("auphonic" if state.get("run_auphonic")
                           else "run") if d is not None else "measured")
    if d is not None:
        state["tracks_left"] = []
        state["stat_measured"] = "run"
    return d


def preview_out_of_date(state, multitrack_on):
    """Whether the preview has to be worked out from the handover again.

    Stale again when the same file is rewritten: "Create Resolve project"
    works the cut out from the numbers set now and writes it back under
    the name it had.
    """
    if state.get("running") or not multitrack_on:
        return False
    js = state.get("resolve_json")
    return bool(js) and (not state.get("statistics")
                         or handover_mark(js) != state.get("preview_from"))


def handover_mark(file_path):
    """What tells one state of a handover file from the next.

    The path alone does not: "Create Resolve project" writes the same
    file again, and a preview going by the name would keep showing the
    cut from before.
    """
    try:
        s = os.stat(file_path)
        return (os.path.abspath(file_path), s.st_mtime_ns, s.st_size)
    except OSError:
        return None


def handover_over_this_material(d, ours):
    """Whether this handover names exactly the cameras in hand.

    One lying in a result folder may be days old or from another
    production, and looks exactly like a fresh one. A camera too few is
    as wrong as one too many, so the two lists have to be the same list.
    """
    mine = set(path_key(p) for p in ours or () if p)
    theirs = set(path_key(c.get("source") or c.get("camera") or "")
                 for c in (d.get("cameras") or [])
                 if (c.get("source") or c.get("camera")))
    return bool(theirs) and theirs == mine


def find_handover_file(*places, deeper=False, ours=None):
    """Find the newest usable ..._resolve.json in these folders.

    *deeper* includes subfolders, where the result of an earlier run
    often sits. *ours* is the material in hand; a handover naming
    anything else is passed over, and one an older version wrote is
    skipped -- read, it would report the material as empty.
    """
    look = []
    for place in places:
        if not place or not os.path.isdir(place):
            continue
        place = os.path.abspath(place)
        if place not in look:
            look.append(place)
        if not deeper:
            continue
        try:
            for name in sorted(os.listdir(place)):
                below = os.path.join(place, name)
                if os.path.isdir(below) and not name.startswith("."):
                    if below not in look:
                        look.append(below)
        except OSError:
            pass
    hit = []
    for place in look:
        try:
            names = os.listdir(place)
        except OSError:
            continue
        for name in names:
            if name.lower().endswith("_resolve.json"):
                file_path = os.path.join(place, name)
                try:
                    with open(file_path, encoding="utf-8") as f:
                        d = json.load(f)
                    if format_complaint(d):
                        continue
                    if ours is not None and not handover_over_this_material(
                            d, ours):
                        continue
                    hit.append((os.path.getmtime(file_path), file_path))
                except (OSError, ValueError):
                    pass
    return max(hit)[1] if hit else None


def colours_pick(dark):
    """Fill COLOURS with the set this desktop asks for.

    Refilled in place rather than replaced: every module holds on to
    this one dictionary, and a new object would leave them all reading
    the old one.
    """
    COLOURS.clear()
    COLOURS.update(COLOURS_DARK if dark else COLOURS_LIGHT)
    PROGRAM.ON_DARK[0] = bool(dark)


def sheet_recoloured(sheet, dark):
    """Return one style sheet with the colours of the other set in it.

    Both palettes carry the same roles, so a value is swapped for the one
    its role holds in the other set. No two roles share a value and no
    value stands in both sets, so a swap cannot be applied twice. A
    colour in neither set is left alone -- the black behind a video is
    not a role.
    """
    leaving = COLOURS_LIGHT if dark else COLOURS_DARK
    entering = COLOURS_DARK if dark else COLOURS_LIGHT
    for role, value in leaving.items():
        if value in sheet:
            sheet = sheet.replace(value, entering[role])
    return sheet


def app_style_set(app):
    """Put the palette into the style sheet of the whole program.

    Its own function so it can be set again when the desktop switches
    between light and dark.
    """
    app.setStyleSheet("""
    QGroupBox {
        border: 1px solid %(frame)s; border-radius: 6px;
        /* The top margin is half the height of the heading, so the
           line runs through the middle of the text. */
        margin-top: 10px; padding-top: 14px; background: %(box)s;
    }
    QGroupBox::title {
        subcontrol-origin: margin; subcontrol-position: top left;
        left: 12px; top: 2px; padding: 0 8px; background: %(box)s;
        color: %(heading)s; font-weight: bold;
    }
    QTabWidget::pane {
        border: 1px solid %(frame)s; border-radius: 6px; top: -1px;
        background: %(sheet)s;
    }
    QTabWidget::tab-bar { alignment: left; left: 6px; }
    QTabBar::tab {
        background: %(head)s; color: %(quiet)s;
        border: 1px solid %(frame)s; border-bottom: none;
        border-top-left-radius: 6px; border-top-right-radius: 6px;
        padding: 8px 22px; margin-right: 3px; font-weight: bold;
    }
    QTabBar::tab:selected { background: %(heading)s; color: %(sheet)s; }
    QTabBar::tab:hover:!selected { background: %(stripe)s; }
    QHeaderView::section {
        background: %(head)s; color: %(heading)s; font-weight: bold;
        border: 0px; border-bottom: 1px solid %(frame)s; padding: 4px;
    }
    QTableWidget, QTreeView, QTextEdit, QListWidget {
        background: %(sheet)s; alternate-background-color: %(head)s;
        color: %(text)s;
    }
""" % {k: COLOURS[k] for k in ("frame", "box", "heading", "head",
                              "quiet", "sheet", "stripe", "text")})


def styles_follow_scheme(app, dark):
    """Recolour every widget that styled itself, and say how many.

    What a widget wrote into its own style sheet is out of reach of the
    program's: setting that again leaves those rows in the colours they
    were born in. Which ones they are need not be remembered -- a widget
    with a sheet of its own is one whose ``styleSheet()`` is not empty.
    """
    changed = 0
    for widget in app.allWidgets():
        try:
            sheet = widget.styleSheet()
        except RuntimeError:
            continue                  # gone while we were walking
        if not sheet:
            continue
        fresh = sheet_recoloured(sheet, dark)
        if fresh == sheet:
            continue
        try:
            widget.setStyleSheet(fresh)
        except RuntimeError:
            continue
        changed += 1
    return changed


def clip_colour_rgb(name):
    """Return the RGB approximation of a clip colour for this background."""
    exception = (PROGRAM.CLIP_COLOURS_RGB_DARK if PROGRAM.ON_DARK[0]
                 else PROGRAM.CLIP_COLOURS_RGB_LIGHT)
    if name in exception:
        return exception[name]
    return PROGRAM.CLIP_COLOURS_RGB.get(name, "#888888")


def mix_file_from_handover(d):
    """Return the file carrying the overall mix.

    Preferably the separate file, which is unambiguous. Otherwise the wide
    shot, where the mix is the first audio track. Otherwise any camera with
    a track of that name.
    """
    for name, file_path in (d.get("audio_files") or {}).items():
        if "full" in name.lower() and file_path and os.path.exists(file_path):
            return file_path, T('stored file %s') % os.path.basename(file_path)
    for cam in (d.get("cameras") or []):
        if cam.get("wide") and cam.get("file") and os.path.exists(cam["file"]):
            return cam["file"], (T('wide shot %s, the mix is its first audio '
                                 'track') % cam["camera"])
    for cam in (d.get("cameras") or []):
        names = [n.lower() for n in (cam.get("audio_tracks") or [])]
        if any("full" in n for n in names) and os.path.exists(
                cam.get("file") or ""):
            idx = [i for i, n in enumerate(names, 1) if "full" in n][0]
            # The track number names the track in that file, the way
            # the editor counts them: plain digits.
            return cam["file"], (T('%s, audio track %d') % (cam["camera"], idx))
    return None, ""


def first_and_last_word(d):
    """Return when the first word falls and when the last one ends.

    Out of the speaker statistics in the handover file, the same source
    the camera cut came from. Returns seconds from the start of the
    timeline, or (None, None).
    """
    starts, ends = [], []
    for speaker in (d.get("speakers") or []):
        for a, b in (speaker.get("sections") or []):
            starts.append(float(a))
            ends.append(float(b))
    if not starts:
        return None, None
    return min(starts), max(ends)


def _meeting_point(entry, kind):
    """Return the point in the clip that should meet the word.

    For the intro the end of its audible audio, where the first word
    starts; for the outro the start of its audio. A clip without audio
    uses its end for the intro and its start for the outro. Nothing is
    cut -- only the position moves, and the picture overlap is where the
    dissolve goes.
    """
    entry = entry or {}
    duration = float(entry.get("duration") or 0.0)
    if kind == "intro":
        value = entry.get("audio_to")
        return float(value) if value is not None else duration
    value = entry.get("audio_from")
    return float(value) if value is not None else 0.0


def lead_in_offset(mp, tl, d, clips, fps, origin):
    """Place intro and outro on the second video and audio track.

    The intro's end falls on the first spoken word, the outro starts
    where the last one ends. The scripting interface knows no
    transitions, so the intro lies *over* the content rather than beside
    it: one drag on the clip corner and the dissolve is there. Returns
    by how many frames the content has to move back.
    """
    intro = d.get("intro")
    if not intro:
        return 0
    word0, _word1 = first_and_last_word(d)
    W = word0 if word0 is not None else 0.0
    # The content moves as far as the intro reaches past the start,
    # measured where its audio stops, not at its file length.
    return PROGRAM.seconds_to_frames(
        max(0.0, _meeting_point(intro, "intro") - W), fps)


HINT_MULTICAM = ('\n  To convert: in the media pool right-click "%s '
                 'Multicam" >\n  "Convert Timeline to Multicam Clip" > '
                 '"Use Source Audio Channels".\n  One way only -- but a '
                 'new run rebuilds the Timeline at any time.\n  Angles:%s\n '
                 ' Everything else -- audio choice, colour groups, '
                 'framing -- is in the\n  manual, docs/resolve.md.\n')


# How the command line switch is named and how the field behind it. All others
# are named alike, with an underscore instead of a hyphen.
SLIDER_TO_DEST = {"edit-change-delay": "delay"}


def cut_slider_defaults():
    """Return the camera cut sliders with their defaults.

    Derived from CUT_FIELDS so there is a single source: the same number
    in three places drifts apart, and then one path cuts differently
    from the next.
    """
    out = []
    for api_key, _b, default_value, _e, _k, _l in CUT_FIELDS:
        field = SLIDER_TO_DEST.get(api_key, api_key.replace("-", "_"))
        try:
            out.append(("--" + api_key, field, float(default_value)))
        except ValueError:
            continue
    # None like the switch itself: no --lufs in the stored call means the
    # run took the loudness from the source files, not that it took -16.
    out.append(("--lufs", "lufs", None))
    # And two numbers the run takes that the window has no field for.
    # Out of CUT_FIELDS alone they are not recovered, and the rules fall
    # back to their own default -- "--reaction-gap 8" arrives as 3.0.
    out.append(("--reaction-gap", "reaction_gap", 3.0))
    out.append(("--reaction-hold", "reaction_hold", 0.7))
    return out


def _sliders_from_command_line(call, production):
    """Recover the sliders from the stored call, for write_cut_list."""
    class Sliders(object):
        pass
    e = Sliders()
    e.production = production
    e.no_wide_edges = "--no-wide-edges" in (call or [])
    # Every --wide-shot in the stored call, not only the first: the mark
    # may stand on several cameras, and without this the button builds a
    # cut with no wide shot while the window above shows one marked.
    e.wide_shot = [(call or [])[i + 1] for i, x in enumerate(call or [])
                   if x == "--wide-shot" and i + 1 < len(call or [])]
    # And the file saying which voice was heard on which camera. Without
    # it every separate voice falls back to the wide shot after all.
    for switch in ("--assign", "--speakers-from"):
        value = ""
        if call and switch in call:
            i = call.index(switch)
            if i + 1 < len(call):
                value = call[i + 1]
        setattr(e, switch[2:].replace("-", "_"), value)
    for switch, field, default_value in cut_slider_defaults():
        value = default_value
        if call and switch in call:
            i = call.index(switch)
            if i + 1 < len(call):
                try:
                    value = float(call[i + 1])
                except ValueError:
                    pass
        setattr(e, field, value)
    for switch, _caption, default_value, values, _k, _l in CUT_CHOICES:
        value = default_value
        if call and "--" + switch in call:
            i = call.index("--" + switch)
            if i + 1 < len(call) and call[i + 1] in values:
                value = call[i + 1]
        setattr(e, switch.replace("-", "_"), value)
    return e


def _read_project_file(folder):
    for file_path in sorted(glob.glob(os.path.join(folder,
                                              "videopodcast-magic_*.json"))):
        try:
            with open(file_path, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            continue
    return {}


def refresh_cut_list(d, file_path):
    """Check the cut list is still valid before building.

    Who speaks when is in the handover already, so turning the cut values
    costs no run. Only a new run can mend a changed In or Out point --
    the audio inside the videos then belongs to another window. Returns
    that reason as text.
    """
    folder = os.path.dirname(os.path.abspath(file_path))
    project = _read_project_file(folder)
    speakers = [(x.get("name") or "", [tuple(v) for v in
                                       (x.get("sections") or [])])
                for x in (d.get("speakers") or [])]
    if not speakers or not project or d.get("start_s") is None:
        return None
    fps = max(1.0, float(d.get("fps_measured") or d.get("fps") or 30.0))
    call = project.get("call") or []

    # Does the project file now hold a different time window from the handover?
    # Then the audio files no longer match it.
    def tc_value(switch):
        if switch not in call:
            return None
        i = call.index(switch)
        if i + 1 >= len(call):
            return None
        try:
            return parse_timecode(call[i + 1], fps)
        except Exception:
            return None
    in_point, out_point = tc_value("--in-point"), tc_value("--out-point")

    def then(key):
        """The window the existing files were made with, in seconds."""
        raw = d.get(key)
        if not raw:
            return None
        try:
            return parse_timecode(raw, fps)
        except Exception:
            return None

    made_in, made_out = then("in_point"), then("out_point")
    # Both complaints hold the setting against the window the handover
    # was made with, and stay silent where it carries none. Only the
    # complaints: the cut list is worked out again either way.
    if (in_point is not None and made_in is not None
            and abs(in_point - made_in) > 0.5):
        return (T('In point is now %s, but the existing files belong to %s.\n '
                  ' The audio in the videos is cut to the old window -- '
                  'press Start\n  above again.')
                % (timecode_string(in_point, fps),
                   timecode_string(made_in, fps)))
    # The old window's length, and only where both its ends are written
    # down. length_s is no substitute: that is the axis, the whole of
    # the material, and an unchanged window would read minutes short.
    length = ((made_out - made_in)
              if made_in is not None and made_out is not None else 0.0)
    if (in_point is not None and out_point is not None
            and length and abs((out_point - in_point) - length) > 0.5):
        return (T('Out point is now %s; the window would be %s long, the '
                  'existing\n  files are %s -- press Start above again.') % (timecode_string(out_point, fps), as_hms(out_point - in_point),
                            as_hms(length)))

    print(T('\n  REFRESH THE CUT LIST'))
    # The sliders come from the interface, otherwise from the project
    # file -- or the button carries on with the values of the last run.
    command_line = [a for a in sys.argv[1:]]
    own_measure = any(a.startswith("--wide-")
                 or a in ("--min-edit-duration", "--edit-change-delay")
                 for a in command_line)
    settings = _sliders_from_command_line(command_line + call,
                                          d.get("production"))
    if own_measure:
        settings.no_wide_edges = "--no-wide-edges" in command_line
    cameras = [{"video": cam["source"], "name": cam["camera"]}
               for cam in (d.get("cameras") or []) if cam.get("source")]
    videos = [(cam["video"], None) for cam in cameras]
    tracks = [{"name": n, "camera": cam["source"]}
              for cam in (d.get("cameras") or [])
              for n in (cam.get("speakers") or [])]
    ref_clip = (cameras[0]["video"] if cameras else "",
                {"fps": fps, "tc": d.get("start_tc")})
    # The handover file carries what was said and where the sound is:
    # the cut points come from those two, not from the clock.
    cut, segs = PROGRAM.write_cut_list(
        settings, speakers, tracks, cameras, videos, folder,
        float(d["start_s"]), ref_clip, length,
        words=words_from_handover(d),
        sound_source=(d.get("audio_files") or {}).get("Full-Mix", ""))
    if not cut:
        return T('That produced no cut -- press Start above again.')
    before_value = d.get("cut") or []
    d["cut"] = [{"start": round(a, 3), "end": round(b, 3), "camera": n}
                    for a, b, n in cut]
    if d["cut"] == before_value:
        print(T('  The cut stays as it was.'))
    else:
        print(T('  The cut has changed: %s shots instead of %s.')
              % (number_text(len(d["cut"]), 0),
                 number_text(len(before_value), 0)))
    d["speakers"] = [{"name": n, "sections": [[round(a, 3), round(b, 3)]
                                                for a, b in segs2]}
                     for n, segs2 in segs]
    d["created_by"] = ('videopodcast-magic %s (cut list refreshed)'
                       % VERSION)
    # Written beside it and moved into place: writing straight onto it,
    # a failure half way leaves a fragment the next run silently skips.
    beside = file_path + ".new"
    try:
        with open(beside, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        os.replace(beside, file_path)
    except OSError as e:
        try:
            os.unlink(beside)
        except OSError:
            pass
        print(T('  %s could not be rewritten: %s')
              % (os.path.basename(file_path), e))
    return None


def voices_on_cameras(segment_list, videos, wanted=None, fallback=""):
    """One pseudo track per voice, so write_cut_list can read the cameras.

    The cut asks the tracks which camera a name belongs to; on the simple
    path one track holds several voices, so the voices stand in for
    tracks. *wanted* is name -> camera, and anything it does not know
    falls back to *fallback*. All on one camera is not a defect -- the
    cut then falls at the change of speaker instead of between cameras.
    """
    wanted = dict(wanted or {})
    after_name = dict((os.path.basename(v), v) for v, _info in videos)
    after_file = ByFile((v, v) for v, _info in videos)
    out = []
    for name, _segs in segment_list or ():
        pick = wanted.get(name) or ""
        camera = after_name.get(pick) or after_file.get(pick) \
            if pick else ""
        out.append({"name": name, "camera": camera or fallback})
    return out


def widest_frame(sizes):
    """Pick the largest frame that a camera really recorded.

    Not the largest width beside the largest height: a landscape and a
    portrait camera in one production would then give a square frame that
    no camera has, and Resolve scales everything into it.
    """
    if not sizes:
        return (None, None)
    return max(sizes, key=lambda wh: (wh[0] * wh[1], wh[0]))


def _block_levels(data, rate, block=1.0):
    """Return the level per second and each track's own speech level.

    A fixed threshold fails because the recorders are set to different
    gains: it would treat the loudest track as always active and the
    quietest as never.
    """
    nb = int(block * rate)
    count = min(len(x) for x in data) // nb
    level = np.array([[float(np.sqrt((x[j * nb:(j + 1) * nb] ** 2).mean()))
                       for j in range(count)] for x in data])
    speech = []
    for row in level:
        present = row[row > 0]
        speech.append(float(np.percentile(present, 90)) if len(present) else 0.0)
    return level, np.array(speech)


def _windows_for_pair(level, speech, i, j, loud=10.0, faint=6.0,
                       at_most=14):
    """Return the blocks in which i speaks and j does not.

    Each track is measured against its *own* speech level, not against the
    others. Otherwise every quietly recorded track would drop out.
    """
    limit_i = max(speech[i] * (10 ** (-loud / 20.0)), 10 ** (-50 / 20.0))
    limit_j = speech[j] * (10 ** (-faint / 20.0))
    good = np.where((level[i] > limit_i) & (level[j] < limit_j))[0]
    if len(good) <= at_most:
        return list(good)
    step = len(good) / float(at_most)
    return [good[int(k * step)] for k in range(at_most)]


# Three points is the least a line through three unknowns can be drawn
# through, and it goes exactly -- so this is the floor, not a good one.
ENOUGH_WINDOWS = 3
# How far the phase peak has to stand out of the noise around it before
# a second of bleed counts as measured.
SHARP_ENOUGH = 10.0


def measure_offsets_by_crosstalk(tracks, rate=16000):
    """Measure the crosstalk window by window.

    When one person speaks, their voice is faintly in the other microphones
    too -- always a few milliseconds *later*, the time sound takes to travel.
    Returns {(i, j): [(time, milliseconds), ...]} for "i speaks, measured in
    j", plus a list of what failed.
    """
    data = parallel_map(
        tracks,
        lambda track: np.asarray(decode_audio(track["axis"], rate=rate),
                                 dtype=np.float64))
    level, speech = _block_levels(data, rate)
    measurements, lines, nb = {}, [], int(rate)
    for i, track in enumerate(tracks):
        for j in range(len(tracks)):
            if j == i:
                continue
            window = _windows_for_pair(level, speech, i, j)
            # Both failures below carry their number: two different
            # recording faults, and the line cannot tell them apart.
            if len(window) < ENOUGH_WINDOWS:
                lines.append((track["name"], tracks[j]["name"],
                               T('only %s seconds where %s speaks alone, '
                                 '%s needed')
                               % (number_text(len(window), 0),
                                  track["name"],
                                  number_text(ENOUGH_WINDOWS, 0))))
                continue
            values, best = [], 0.0
            for f in window:
                a = data[i][f * nb:(f + 1) * nb]
                b = data[j][f * nb:(f + 1) * nb]
                ms, sharp = gcc_phat_offset(a, b, rate)
                best = max(best, sharp)
                if sharp >= SHARP_ENOUGH:
                    values.append((f + 0.5, ms))
            if len(values) >= ENOUGH_WINDOWS:
                measurements[(i, j)] = values
            else:
                lines.append((track["name"], tracks[j]["name"],
                               T('bleed too indistinct: %s of %s seconds '
                                 'usable, sharpest %s of %s needed')
                               % (number_text(len(values), 0),
                                  number_text(len(window), 0),
                                  number_text(best, 1),
                                  number_text(SHARP_ENOUGH, 0))))
    return measurements, lines


def solve_pair_offsets(measurements, i, j, highest_clock_drift=100.0):
    """Solve one pair for sound path, offset and clock drift.

    i heard in j gives sound path + offset(t), the reverse sound path -
    offset(t), with offset(t) = d0 + k*t: three unknowns in one least
    squares fit. Returns (path_ms, d0_ms, k_ppm, points, residual_ms), or
    None where a direction is missing. Three points fit three unknowns
    exactly, so a residual of zero means nothing.
    """
    forward, backward = measurements.get((i, j)), measurements.get((j, i))
    if not forward or not backward:
        return None
    lines, values = [], []
    for t, ms in forward:
        lines.append([1.0, 1.0, t])
        values.append(ms)
    for t, ms in backward:
        lines.append([1.0, -1.0, -t])
        values.append(ms)
    A = np.array(lines)
    y = np.array(values)
    with_slope = len(forward) >= 6 and len(backward) >= 6
    if not with_slope:
        A = A[:, :2]
    solution, *_ = np.linalg.lstsq(A, y, rcond=None)
    gone, d0 = float(solution[0]), float(solution[1])
    k = float(solution[2]) * 1000.0 if with_slope else 0.0   # ms/s -> ppm
    if abs(k) > highest_clock_drift:
        # No two clocks drift that fast, so the slope is guesswork. Better to
        # take the fixed offset alone.
        A = A[:, :2]
        solution, *_ = np.linalg.lstsq(A, y, rcond=None)
        gone, d0, k = float(solution[0]), float(solution[1]), 0.0
    left = y - A.dot(solution)
    over = max(1, len(y) - A.shape[1])
    rest = float(np.sqrt(float(np.dot(left, left)) / over))
    return gone, d0, k, len(forward) + len(backward), rest


def verify_alignment(tracks, t0=None, t1=None, limit_ms=1.0,
                      limit_ppm=0.5, drift_allowed=True):
    """Verify the tracks line up, and straighten them if not.

    Measured on the crosstalk in both directions: the sound path is
    symmetric and cancels out, leaving the fixed offset and the clock
    drift, and both are removed by rewriting the track. From about 20 ms
    on the crossing voice is audible as a second one.
    """
    if len(tracks) < 2:
        return
    print(T('\n  Check against the bleed -- reference is %s:')
          % tracks[0]["name"])
    try:
        measurements, lines = measure_offsets_by_crosstalk(tracks)
    except Exception as e:
        print(T('    not possible: %s') % e)
        return
    for a, b, value in lines:
        print("    %-14s -> %-14s %s" % (a, b, value))

    pairs = {}
    for i in range(len(tracks)):
        for j in range(i + 1, len(tracks)):
            solution = solve_pair_offsets(measurements, i, j)
            if solution is None:
                continue
            pairs[(i, j)] = solution
            gone, d0, k, n, rest = solution
            print(T('    %-14s <-> %-14s sound path %4s ms (%s m), '
                    'offset %6s ms, drift %5s ppm '
                    '(%s points, %s ms left over)%s')
                  % (tracks[i]["name"], tracks[j]["name"],
                     number_text(gone, 1),
                     number_text(max(0.0, gone) / 1000.0 * 343.0, 2),
                     number_text(d0, 1, plus=True),
                     number_text(k, 1, plus=True),
                     number_text(n, 0), number_text(rest, 1),
                     T('   (sound path negative -- something is wrong)')
                     if gone < -1.0 else ""))
    if not pairs:
        print(T('    No pair measurable -- it stays as it is.'))
        return

    # Position of every track against the first: offset and drift.
    position = {0: (0.0, 0.0)}
    for i in range(1, len(tracks)):
        for j in list(position):
            found = pairs.get((j, i)) or pairs.get((i, j))
            if not found:
                continue
            d0, k = found[1], found[2]
            if (i, j) in pairs:          # measured as (i against j)
                d0, k = -d0, -k
            position[i] = (position[j][0] + d0, position[j][1] + k)
            break
    if t0 is None or t1 is None:
        return

    shifted = []
    for i, track in enumerate(tracks):
        d0, k = position.get(i, (0.0, 0.0))
        if not drift_allowed:
            # --no-drift means the running time stays as recorded. The
            # offset is still corrected; stretching the track is not.
            k = 0.0
        if not track.get("source"):
            continue
        if abs(d0) < limit_ms and abs(k) < limit_ppm:
            continue
        if abs(k) < limit_ppm:
            k = 0.0
        if abs(d0) > 250.0 or abs(k) > 100.0:
            print(T('    %-20s %s ms / %s ppm -- that cannot be '
                    'right, track\n    %-20s stays where it is.')
                  % (track["name"], number_text(d0, 0, plus=True),
                     number_text(k, 0, plus=True), ""))
            continue
        # "audio time = a + b * reference time": read d0 too early means
        # shifting a by b*d0, and the drift multiplies b.
        track["a"] = track["a"] + (d0 / 1000.0) * track.get("b", 1.0)
        # The output is compressed by b. A track running too fast -- k
        # negative, the offset shrinking over time -- needs b lowered.
        track["b"] = track.get("b", 1.0) * (1.0 + k * 1e-6)
        track["drift"] = bool(drift_allowed
                           and (track.get("drift")
                                or abs(track["b"] - 1.0) > 1e-7))
        place_track_on_axis(track["source"], track["axis"], track["a"], track["b"], t0, t1,
                       track.get("drift", False))
        shifted.append((track["name"], d0, k))
    if not shifted:
        print(T('    All tracks are in place -- nothing to move.'))
        return
    for name, d0, k in shifted:
        print(T('    %-20s shifted by %s ms%s')
              % (name, number_text(-d0, 1, plus=True),
                 T(', clock drift %s ppm taken out')
                 % number_text(-k, 1, plus=True)
                 if abs(k) >= limit_ppm else ""))
    try:
        measurements2, _ = measure_offsets_by_crosstalk(tracks)
    except Exception as e:
        print(T('    Cross-check not possible: %s') % e)
        return
    parts = []
    for i in range(len(tracks)):
        for j in range(i + 1, len(tracks)):
            found = solve_pair_offsets(measurements2, i, j)
            if found:
                parts.append("%s/%s %s ms %s ppm"
                             % (tracks[i]["name"], tracks[j]["name"],
                                number_text(found[1], 1, plus=True),
                                number_text(found[2], 1, plus=True)))
    if not parts:
        print(T('    Cross-check: not measurable'))
        return
    print(T('    Cross-check:'))
    for t in parts:
        print("      %s" % t)


def similarity(a, b):
    """Return how similar two names are, 0 to 1, forgiving of typos."""
    import difflib
    return difflib.SequenceMatcher(None, (a or "").lower(),
                                   (b or "").lower()).ratio()


def without_repeated_words(name):
    """Drop name parts already present, case insensitively; order kept."""
    seen, parts = set(), []
    for t in name.split("_"):
        if t and t.lower() in seen:
            continue
        seen.add(t.lower())
        parts.append(t)
    return "_".join(parts)


def counting_digits_off(name):
    """A name without the digits a device counts its files with.

    "Presenter00018" is a recorder's eighteenth file: the numbers say
    which file, never who. Kept where nothing is left without them --
    "0008A" is a poor name, but it is the only one that file has.
    """
    bare = re.sub(r"[\s_\-.]*\d+[A-Za-z]?$", "", (name or "").strip())
    return bare if len(bare) >= 3 else (name or "").strip()


def camera_for_speaker(speaker, cameras):
    """Return the camera whose name matches this speaker.

    Compared with the parts of the camera file name, forgiving of typos.
    Without a match there is no suggestion: a guessed assignment is worse
    than none.
    """
    wanted = (speaker or "").strip().lower()
    if len(wanted) < 3:
        return None
    # A recorder counts its files and so does a camera, and the two
    # counts mean nothing to each other. Measured: "Name00018" against
    # "Names" scored 0.72 and found nothing, the bare name 0.9.
    bare = counting_digits_off(wanted)
    best, best_value = None, 0.0
    for cam in cameras:
        stem = os.path.splitext(os.path.basename(cam))[0]
        for part in [t for t in re.split(r"[_\-. ]", stem) if len(t) >= 3]:
            value = max(similarity(wanted, part),
                        similarity(bare, counting_digits_off(part)))
            # Word starts count too: "Host" is inside "Hosts".
            if part.lower().startswith(wanted) or wanted.startswith(part.lower()):
                value = max(value, 0.9)
            if value > best_value:
                best, best_value = cam, value
    return best if best_value >= 0.8 else None


def guess_camera_name(file_path):
    """Guess a usable track name from a video file name.

    Pure digit groups and the trailing camera identifier drop out, and of
    the rest the last part carries the most meaning. If nothing is left,
    the whole stem is used.
    """
    stem = os.path.splitext(os.path.basename(file_path))[0]
    parts = [t for t in stem.split("_") if t.strip()]
    left_over = [t for t in parts
              if not re.fullmatch(r"\d+", t)
              and not re.fullmatch(r"[A-Za-z]\d{3,}", t)]
    # Only a fragment left? Then the name was short anyway; better to show the
    # whole stem than one syllable of it.
    return left_over[-1] if len(left_over) >= 2 else stem


def guess_speaker_name(file_path):
    """Guess a usable speaker name from a file name.

    The first name part usually hits; if it is very short the whole stem
    without its trailing number is used.
    """
    stem = os.path.splitext(os.path.basename(file_path))[0]
    m = TRAILING_NUMBER.match(stem)
    without_index_number = m.group(1).rstrip("_-. ") if m else stem
    first_one = re.split(r"[_\-. ]", without_index_number)[0]
    return first_one if len(first_one) >= 3 else without_index_number


# The standard folders of a home directory. macOS and Windows keep the
# English names on disk; Linux writes its own into user-dirs.dirs.
GENERAL_FOLDERS = ("desktop", "downloads", "documents", "movies", "music",
                   "pictures", "videos", "public", "temp", "tmp")
_general_extra = []


def general_folder_names():
    """Folder names that say nothing about which production this is."""
    if not _general_extra:
        _general_extra.append(set(GENERAL_FOLDERS))
        config = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser(
            os.path.join("~", ".config"))
        try:
            with open(os.path.join(config, "user-dirs.dirs"),
                      encoding="utf-8", errors="replace") as f:
                for line in f:
                    if not line.startswith("XDG_") or "=" not in line:
                        continue
                    where = line.split("=", 1)[1].strip().strip('"')
                    name = os.path.basename(where.rstrip("/"))
                    if name and name != "$HOME":
                        _general_extra[0].add(name.lower())
        except Exception:
            pass
    return _general_extra[0]


def guess_production_name(file_path):
    """Return the production name from the folder holding the files.

    Files sitting directly on a volume or in the home folder have a
    meaningless folder name; then date and time are used instead.
    """
    folder = os.path.dirname(os.path.abspath(file_path))
    name = os.path.basename(folder)
    parent = os.path.dirname(folder)
    general = general_folder_names()
    meaningless = (not name
                    or folder == os.sep                  # root
                    or parent == "/Volumes"              # volume root
                    or folder == os.path.expanduser("~")  # home folder
                    or name.lower() in general)
    if meaningless:
        return 'Production ' + time.strftime("%Y-%m-%d %H-%M")
    return name


# How much shorter than the rest a file has to be before one with no
# place is a jingle rather than a recording that merely fits nothing.
INTRO_SHORT_ENOUGH = 0.1


def files_far_shorter(some, length_of):
    """Which of *some* are far shorter than the material around them.

    Held against the middle of the others rather than a written-down
    length: what counts as short is what the rest of the shoot is.
    Shortest first.
    """
    out = []
    for p in some:
        others = sorted(s for q, s in length_of.items() if q != p)
        if p not in length_of or not others:
            continue
        middle = others[len(others) // 2]
        if middle > 0 and length_of[p] <= middle * INTRO_SHORT_ENOUGH:
            out.append(p)
    return sorted(out, key=lambda p: length_of[p])


def axis_text(data):
    """The line under the axis: how it was found, and what did not fit.

    Read off the finished answer rather than put together beside it, so
    the count and the list it counts cannot drift apart.
    """
    text = (T('time axis measured and tied to the timecode')
            if (data or {}).get("absolute")
            else T('time axis measured -- jumps land at the same point'))
    weak = (data or {}).get("weak") or ()
    if weak:
        text += TN(len(weak), ', %s file does not fit',
                   ', %s files do not fit') % number_text(len(weak), 0)
    return text


def measure_time_axis(paths, tc_of=lambda p: None, HOP=5.0):
    """Determine how all files sit relative to each other.

    The longest recording is the reference; a timecode from *tc_of* hangs
    the whole axis off it. Returns (result, text), keyed by path_key:
    "axis", "clock" (recorder speed), and four narrowing lists -- "weak"
    fits badly, "no_place" has no timecode either, "unplaceable" is under
    the floor as well, "brief" is far shorter than the rest.
    """
    # Every file at once: each envelope is read on its own, and over
    # hours of 4K this is the longest part of the measurement.
    def curve_of(file_path):
        try:
            return video_envelope(file_path, HOP, 4000)
        except Exception:
            return None

    envelopes = {}
    for p, env in zip(paths, parallel_map(paths, curve_of)):
        if env is not None and len(env) > 200:
            envelopes[p] = env
    if len(envelopes) < 2:
        return ({}, "" if envelopes else T('time axis not measurable'))
    reference = max(envelopes, key=lambda p: len(envelopes[p]))
    axis, weak, lost = {reference: 0.0}, [], []
    # Not "clocks": that one holds timecodes a few lines down.
    clock_speed = {reference: 1.0}
    others = [p for p in envelopes if p != reference]
    clocks = dict((p, tc_of(p)) for p in paths)

    def against_reference(file_path):
        try:
            # The same method as the run: sample points over the whole
            # runtime, a regression line, the median.
            a_s, b, st = align_envelopes(envelopes[reference],
                                          envelopes[file_path], HOP,
                                          warn=os.path.basename(file_path))
            return a_s, b, st.get("quality", 0.0)
        except Exception:
            return None

    for p, answer in zip(others, parallel_map(others, against_reference)):
        if answer is None:
            continue
        a_s, b, g = answer
        if abs(g) < SOUND_MATCH_ENOUGH:
            # No phase way here: laid in at this floor it places files
            # hours out. See align_audio_to_video.
            weak.append(p)
            if cannot_be_placed({"unplaceable": g < WEAK_MATCH}, clocks.get(p),
                                [t for q, t in clocks.items() if q != p]):
                lost.append(p)
            continue
        # Divided by b, as the run does before writing the track: a is
        # where the recording sits in its own time, and that runs at b.
        axis[p] = -a_s / b
        clock_speed[p] = b
    # Held against a camera too: against a sound recording a jingle and
    # a camera read too close together to tell apart (measurements.md).
    cameras = [p for p in envelopes if p.lower().endswith(VIDEO_SUFFIXES)]
    if len(cameras) > 1:
        camera_ref = max(cameras, key=lambda p: len(envelopes[p]))
        for p in cameras:
            if p == camera_ref or p in weak:
                continue
            try:
                _a, _b, st = align_envelopes(envelopes[camera_ref],
                                             envelopes[p], HOP,
                                             warn=os.path.basename(p))
            except Exception:
                continue
            if (st.get("quality", 0.0) < CAMERA_MATCH_ENOUGH
                    and not fit_places_it(st)):
                # The second way the run leaves open at this floor:
                # where a clock places the file the sound is not asked.
                st["unplaceable"] = True
                weak.append(p)
                if cannot_be_placed(st, clocks.get(p),
                                    [t for q, t in clocks.items()
                                     if q != p]):
                    axis.pop(p, None)
                    clock_speed.pop(p, None)
    # A file that fits nothing and is far shorter than everything around
    # it is a jingle, not a camera; a clock that places it beats sound.
    nowhere = files_with_no_place(weak, clocks)
    brief = files_far_shorter(
        nowhere, dict((p, len(e) * HOP / 1000.0)
                      for p, e in envelopes.items()))
    if len(axis) < 2:
        # No axis, but the measurement did happen and knows which files
        # it could not place. Thrown away here, the one file that fits
        # nothing would come out of a two-file production unmarked.
        return ({"axis": {}, "clock": {}, "absolute": False, "weak": weak,
                 "unplaceable": lost, "brief": brief,
                 "no_place": nowhere},
                T('time axis not measurable'))
    origin = min(axis.values())
    for p in axis:
        axis[p] -= origin
    # The median offset is used so one outlier cannot skew everything.
    offsets = sorted(t - axis[p] for p in axis
                       for t in [tc_of(p)] if t is not None)
    absolute = bool(offsets)
    if absolute:
        middle = offsets[len(offsets) // 2]
        for p in axis:
            axis[p] += middle
    # Not before here: everything above reads the file itself, and the
    # timecode is asked for under the name that was passed in.
    axis = dict((path_key(p), t) for p, t in axis.items())
    speed = dict((path_key(p), b) for p, b in clock_speed.items()
                 if path_key(p) in axis)
    answer = {"axis": axis, "clock": speed, "absolute": absolute,
              "weak": weak, "unplaceable": lost, "brief": brief,
              "no_place": nowhere}
    return answer, axis_text(answer)


def envelope_seconds(path, HOP=5.0):
    """How long a file runs, out of the envelope already measured.

    No second reading: the curve is in memory or in the cache by then,
    and it holds one value every HOP milliseconds. 0.0 where none.
    """
    try:
        return len(video_envelope(path, HOP, 4000)) * HOP / 1000.0
    except Exception:
        return 0.0


def block_at(blocks, when, begins):
    """Which block of a recording holds a moment, and how far into it.

    Every piece has a place of its own, so the piece holding a moment is
    the last one that starts before it. *begins* answers where a piece
    starts, which lets the same walk serve the measured axis and the
    files' own clocks. Returns (path, seconds into it), or (None, None).
    """
    before = [(begins(p), p) for p in blocks or ()]
    before = [(t, p) for t, p in before if t is not None and t <= when]
    if not before:
        # Nothing of this recording had started yet. Playing its front
        # here would sound it against a picture it does not belong to.
        return None, None
    t, p = max(before)
    return p, when - t


def blocks_after_their_head(data, blocks, length_of=envelope_seconds):
    """Put a continuation behind its head block.

    The grouping settles where the parts lie: the head's place plus what
    runs before. *blocks* is {head: [head, second, ...]} and is the whole
    of the distinction -- a block taken out and put back in on its own is
    not in there, so it is a recording of its own and measured.
    """
    axis = (data or {}).get("axis") or {}
    speed = (data or {}).get("clock") or {}
    put = {}
    for row in (blocks or {}).values():
        keys = [path_key(p) for p in row or ()]
        if len(keys) < 2 or keys[0] not in axis:
            continue
        at = axis[keys[0]]
        for before, key in zip(row, keys[1:]):
            runs = float(length_of(before) or 0.0)
            if runs <= 0.0:
                # Without the length of the block in front there is no
                # place to work out. Guessing one would put the rest of
                # the recording somewhere and call it measured.
                break
            at += runs
            put[key] = (at, speed.get(keys[0], 1.0))
    if not put:
        return data
    axis.update((k, v[0]) for k, v in put.items())
    speed.update((k, v[1]) for k, v in put.items())
    data["axis"], data["clock"] = axis, speed
    return data


def axis_with_blocks(paths, tc_of=lambda p: None, HOP=5.0, blocks=None,
                     length_of=envelope_seconds):
    """Measure a recording made of blocks as one recording.

    The head is measured like any other file; the continuations are
    taken to fit and their place follows from the head, so a tail of a
    few minutes cannot turn down an hour of material. One taken out of
    the recording and put back in as a file is measured again.
    """
    tails = set(path_key(p) for row in (blocks or {}).values()
                for p in (row or ())[1:])
    data, text = measure_time_axis(
        [p for p in paths if path_key(p) not in tails], tc_of, HOP)
    return blocks_after_their_head(data, blocks, length_of), text


def file_fingerprint(file_path):
    """Return what identifies a file again: path, mtime, size.

    No hash: over hours of material it would take longer than what it
    secures, and a replaced file practically always changes one of the two.
    """
    try:
        st = os.stat(file_path)
        return [os.path.abspath(file_path), int(st.st_mtime), st.st_size]
    except OSError:
        return None


def timeline_entries(axis, clocks):
    """The measured place of every file, as the project file keeps it.

    The clock speed rides along: measuring it again costs the same
    minutes, and a changed file is caught by its size and time anyway.
    """
    out = []
    for p, start in (axis or {}).items():
        k = file_fingerprint(p)
        if k:
            out.append({"path": k[0], "mtime": k[1], "size": k[2],
                        "start_s": round(start, 3),
                        "clock": round(float(
                            (clocks or {}).get(path_key(p), 1.0)), 9)})
    return out


def axis_still_valid(d, paths, fingerprint=file_fingerprint):
    """Report whether a measured axis still applies to these files.

    All or nothing: the axis is a statement about their relationship, and
    a half valid one would be worse than none because it would look
    right. Returns {"axis", "clock", "weak", "absolute"} or None, keyed
    by path_key; without a stored clock speed a file comes back at 1.0.
    """
    known = {}
    for e in ((d or {}).get("timeline") or []):
        stored = e.get("path")
        if stored:
            known[path_key(stored)] = e
    axis, speed = {}, {}
    for file_path in paths:
        k = fingerprint(file_path)
        e = known.get(path_key(k[0])) if k else None
        if not e or e.get("mtime") != k[1] or e.get("size") != k[2]:
            return None
        axis[path_key(k[0])] = float(e.get("start_s") or 0.0)
        speed[path_key(k[0])] = float(e.get("clock") or 1.0)
    if not axis:
        return None
    return {"axis": axis, "clock": speed, "weak": [],
            "absolute": bool((d or {}).get("timeline_absolute"))}


def axis_worth_measuring(files, every, state, fingerprint=file_fingerprint):
    """Whether the time axis still has something new to say.

    The tables ask on every rebuild, and the answer moves the Kind of a
    file with no place, which rebuilds the tables. Unchanged material
    already answered leaves nothing to measure. The list handed in is no
    mark -- a file whose Kind is not a camera drops out of it.
    """
    mark = frozenset(tuple(fingerprint(p) or (p, 0, 0)) for p, _a in files)
    want = set(path_key(p) for p in every)
    if (state.get("axis_answered") == mark
            and want <= (state.get("axis_covered") or set())):
        return False
    if not state.get("axis_running"):
        state["axis_asked"], state["axis_asking"] = mark, want
    return True


def axis_answer_kept(state):
    """Note what the answer just given was about.

    Material that changed meanwhile starts the list of files reached
    afresh; otherwise two questions over one unchanged set add up.
    """
    if state.get("axis_answered") != state.get("axis_asked"):
        state["axis_covered"] = set()
    state["axis_answered"] = state.get("axis_asked")
    state["axis_covered"] = ((state.get("axis_covered") or set())
                             | (state.get("axis_asking") or set()))


def recordings_text(chains, file_count):
    """Return the header line of the audio group.

    While both counts agree the file count is enough; otherwise the line
    would draw a distinction that does not exist.
    """
    if chains == file_count:
        return (TN(file_count, '%s file', '%s files')
                % number_text(file_count, 0))
    return TN(chains, '%s recording from %s files',
              '%s recordings from %s files') % (number_text(chains, 0),
                                                number_text(file_count, 0))


def pending_prework(paths, having_audio=(), has_audio=lambda p: False,
                    has_env_curve=lambda p: False,
                    has_channels=lambda p: False,
                    has_tracks=lambda p: True):
    """Return the prework still to be done: envelopes for all, audio for some.

    Asked rather than queued blindly, and separate: the envelope may be
    there while the audio is missing. *has_audio* may return None -- the
    file cannot be queried at all and stays out entirely. A file of more
    than one channel is measured too, its channels deciding which tabs
    are offered. Returns (path, task): "audio", "envelope", "channels".
    """
    wants_audio = set(os.path.abspath(p) for p in having_audio)
    out = []
    for file_path in paths:
        a = os.path.abspath(file_path)
        if not os.path.exists(a):
            continue
        if a in wants_audio:
            present = has_audio(a)
            if present is None:
                continue
            if not present:
                out.append((a, "audio"))
        if not has_env_curve(a):
            out.append((a, "envelope"))
        try:
            wide = channel_count(a) > 1
        except Exception as e:
            # Swallowing this leaves the file list saying "being looked
            # at" for ever with no bar -- it looks exactly like a crash.
            print(as_warn(T('  %s: how many channels it has cannot be '
                            'determined (%s) -- it is not measured')
                          % (os.path.basename(a), str(e).strip()[:60])))
            wide = False
        if wide:
            if not has_channels(a):
                out.append((a, "channels"))
            elif not has_tracks(a):
                # Only once the channels are known: what has to be cut
                # out follows from that measurement.
                out.append((a, "split"))
    return out


def every_audio_block(files, blocks_of, using_audio=()):
    """Every file a run would listen to, blocks included.

    *files* is the selection as (path, kind) pairs, *blocks_of* what the
    search found per recording: continuations are not in the selection
    but still have to be measured and cut, or a multi-part recording
    would give only its first block. *using_audio* are the video files
    whose sound was set to "use", and they belong in this same list.
    """
    out = [os.path.abspath(p) for p, a in files if a == "audio"]
    for p in using_audio:
        if os.path.abspath(p) not in out:
            out.append(os.path.abspath(p))
    for row in blocks_of.values():
        for x in row:
            if x not in out:
                out.append(x)
    return out


def window_suggestion(entries, fps=30.0):
    """Suggest the In point and the Out point from what the cameras offer.

    As far as the cameras reach -- what happens without an entry anyway,
    made visible so it can be adjusted. *entries* is [(start on the clock
    or None, duration)]. Returns (in_point, out_point, absolute); with no
    start time anywhere the suggestion is relative, and without a usable
    entry ("", "", False).
    """
    starts = [(t, d) for t, d in entries if t is not None]
    if starts:
        return (timecode_string(min(t for t, _d in starts), fps),
                timecode_string(max(t + (d or 0.0) for t, d in starts), fps),
                True)
    lengths = [d for _t, d in entries if d]
    if not lengths or max(lengths) <= 0:
        return "", "", False
    # Whole seconds are enough here, and the mark depends on the
    # language, so it is asked for explicitly.
    return "+0:00", "+%s" % as_hms(max(lengths), ".").split(".")[0], False


def has_sound(file_path):
    """Whether this file carries an audio stream at all.

    Asked before a camera's audio is made a track of its own: a camera
    nobody plugged a microphone into is no answer.
    """
    try:
        return any(s.get("codec_type") == "audio"
                   for s in ffprobe_json(file_path).get("streams") or [])
    except Exception:
        return False


def cameras_with_own_audio(videos, audio_files, ticked=(), sound_of=None):
    """Which cameras contribute their audio as a track, and which by rule.

    A field set by hand decides, with one exception: a single video that
    carries sound and no audio recording beside it -- that sound is then
    the only sound there is. Two cameras are a choice again. Derived,
    never stored, so the exception falls away by itself. *sound_of* says
    whether a video carries audio. Returns (cameras, the ones not ticked).
    """
    wanted = {os.path.abspath(b) for b in (ticked or ())}
    by_hand = [b for b in videos if os.path.abspath(b) in wanted]
    if by_hand or audio_files or len(videos) != 1:
        return by_hand, []
    if sound_of is not None and not sound_of(videos[0]):
        return [], []
    return list(videos), list(videos)


def assignment_rows(audio_files, videos, own_flag_cameras=(),
                    split_of=None, apart=(), together=()):
    """Return the rows for the upper table.

    One row per audio recording or chain of blocks, plus the cameras
    contributing their audio -- input tracks like any other, channels
    included: two clip-ons on a camera's two channels give two rows.
    Nothing tells a radio microphone from a room one, so the field on
    each camera is the whole answer. Returns (chains, False, {track: camera}).
    """
    chains = (list(group_recording_parts(audio_files, apart=apart,
                                         together=together))
              if audio_files else [])
    if split_of:
        chains = expand_chains_to_tracks(chains, split_of)
    rows, own = [], ByFile()
    for b in list(own_flag_cameras or ()):
        pieces = [x for x in (split_of(b) or ())] if split_of else []
        for piece in (pieces or [b]):
            rows.append(([piece], []))
            own[piece] = os.path.abspath(b)
    return chains + rows, False, own


def preselected_camera(old, targets, speaker, videos, own_camera=""):
    """Return the camera an audio track is preselected to.

    A manual setting applies while that camera exists; otherwise the
    speaker name is searched for, and without a match it stays on the mix
    -- a wrongly guessed camera looks like a decision. *own_camera*, the
    camera audio came out of, is a preselection and not a rule: a clip-on
    on one camera may belong to a person another is filming.
    """
    if old and old in targets:
        return old
    if own_camera:
        return own_camera
    hit = camera_for_speaker(speaker, videos)
    return os.path.basename(hit) if hit else MIX_ONLY


def camera_to_remember(camera, derived, keep=None):
    """What of an audio row's camera is written into the project.

    Only a real override. One the program worked out goes back as
    nothing, so the next rebuild works it out again -- stored, a name
    changed afterwards no longer moves the camera. *keep* is what a quiet
    row falls back on: there the mix is the absence of a choice.
    """
    if camera == MIX_ONLY and keep:
        return keep
    return None if camera == derived else camera


def camera_row_cameras(old, targets, speaker, videos, own_camera=""):
    """The camera a row shows, and the one the program would give alone.

    Two answers to one question: the second is asked with nothing
    remembered, and only a camera that differs from it is written down.
    """
    return (preselected_camera(old, targets, speaker, videos, own_camera),
            preselected_camera(None, targets, speaker, videos, own_camera))


def camera_shortfall_lines(who, rows, voices):
    """What to say about speakers who get no shot of their own.

    Nothing where there are none. Where it is everybody, a second line:
    every shot is then the same one and the cut says nothing -- worth
    knowing before the hours of computing rather than after.
    """
    if not who:
        return []
    out = [T('No camera of their own: %s') % ", ".join(who)]
    if len(who) >= len(rows) + len(voices):
        out.append(T('   -- that is everybody, so every shot goes to the '
                     'same camera.'))
    return out


def without_own_camera(rows, voices, multitrack_on, voiced=()):
    """Who goes into the mix but gets no shot of their own.

    Information, not a complaint: whoever set somebody to "no camera of
    its own" wanted it that way, and this is the list of them in one
    place before the hours of computing. Passed over, as nobody left out
    of the picture: a recording whose voices stand under it, and every
    recording at all without multitrack. *rows* are (blocks, name, camera).
    """
    voiced = set(voiced or ())
    pairs = [(name, camera) for blocks, name, camera in rows
             if multitrack_on and os.path.abspath(blocks[0]) not in voiced]
    out = []
    for name, camera in pairs + list(voices):
        name = (name or "").strip()
        if camera == MIX_ONLY and name and name not in out:
            out.append(name)
    return out


def name_already_in(stem, speaker):
    """Whether the speakers' names already stand in the camera's name.

    "Guest" in "GuestCam001" -- saying it again puts one word twice into
    a name that travels into Resolve. Every one of them has to be there:
    "Hosts" carrying "Host" and "Co-host" says nothing about the second.
    """
    low = (stem or "").lower()
    names = [x.strip().lower() for x in speaker or () if (x or "").strip()]
    return bool(names) and all(n and n in low for n in names)


def camera_output_name(production, camera, speaker=()):
    """Build the name of the new video file.

    The speakers sit in the middle, behind the first part of the camera
    name, so the front reads as which camera it was and the identifier
    stays at the back. Where the camera is already named almost like
    the speaker it is not said twice, forgivingly enough that a typo
    counts as the same. *production* only recognises older material.
    """
    stem = os.path.splitext(os.path.basename(camera))[0]
    # Split only where what follows carries a number: that is a counter
    # and the speaker belongs in front of it, never inside a name.
    parts = re.split(r"[_\-. ]", stem, maxsplit=1)
    if len(parts) == 2 and not re.search(r"\d", parts[1]):
        parts = [stem]
    who = "+".join(x.strip() for x in speaker if (x or "").strip())
    if parts and who and (similarity(parts[0], who) >= 0.85
                          or name_already_in(stem, speaker)):
        who = ""
    front = (production or "").strip() or 'Production'
    # Earlier versions put the production in front, and their files come
    # back through here. Such a stem is not split further, or the speaker
    # lands inside the production's own name.
    if front and stem.lower().startswith(front.lower()):
        parts = [stem]
    if len(parts) == 2 and who:
        name = "%s_%s_%s" % (parts[0], who, parts[1])
    else:
        name = "_".join(x for x in (stem, who) if x)
    return without_repeated_words(name)


def together_chains(together):
    """Bring the by-hand groupings into one ordered list per recording.

    Given as [[a, b], [b, c]] they mean one recording a, b, c: naming a
    file in two groups joins those groups. Order is kept -- the first
    time a file is named is where it sits.
    """
    rows = []
    for group in (together or ()):
        wanted = [os.path.abspath(x) for x in group if x]
        if len(wanted) < 2:
            continue
        hit = [r for r in rows if any(x in r for x in wanted)]
        if not hit:
            rows.append(list(dict.fromkeys(wanted)))
            continue
        first = hit[0]
        for other in hit[1:]:
            first += [x for x in other if x not in first]
            rows.remove(other)
        first += [x for x in wanted if x not in first]
    return rows


def group_recording_parts(paths, no_followups=False, apart=(), together=()):
    """Group the selected audio files into recordings.

    Numbered continuations are searched from the first block and only
    seamless ones appended. *apart* names blocks that must stand alone,
    or the search, looking in the folder and not in the selection, finds
    them again on the next rebuild. *together* is the other way, each
    named file bringing the blocks already found for it; *apart* wins.
    """
    apart = FileSet(apart or ())

    def with_its_blocks(row):
        """Each named file plus the blocks already found for it.

        Only what fits: channel count and sample rate have to match the
        first block, since everything after the join treats them as one
        recording.
        """
        out, refused = [], []
        for x in row:
            if not os.path.exists(x):
                refused.append((os.path.basename(x), T('not found')))
                continue
            found = [x]
            if not no_followups and x not in apart:
                try:
                    found, _ = find_continuation_files(x)
                except Exception:
                    found = [x]
            for y in found:
                y = os.path.abspath(y)
                if y in apart or y in out:
                    continue
                if out:
                    fits, why = shapes_match(out[0], y)
                    if not fits:
                        refused.append((os.path.basename(y), why))
                        continue
                out.append(y)
        return out, refused

    made = [with_its_blocks(row) for row in together_chains(together)]
    # Two groups can end up holding the same block. A block belongs to
    # one recording, so the first group to claim it keeps it.
    by_hand, turned_away, claimed = [], {}, set()
    homeless = {}
    for row, refused in made:
        mine = [x for x in row if x not in claimed]
        notes = list(refused) + [
            (os.path.basename(x), T('already in another recording'))
            for x in row if x not in mine]
        if len(mine) < 2:
            # Nothing left to group, but the notes still have to reach
            # somebody: the recording the one remaining file ends up in.
            for x in mine or row:
                homeless.setdefault(x, []).extend(notes)
            continue
        claimed.update(mine)
        turned_away[len(by_hand)] = notes
        by_hand.append(mine)
    put = {}
    for i, row in enumerate(by_hand):
        for x in row:
            put[x] = i
    pending = sorted(paths, key=lambda x: os.path.basename(x).lower())
    chains, taken, done_by_hand = [], set(), set()
    for p in pending:
        a = os.path.abspath(p)
        if a in taken:
            continue
        if a in put:
            # A grouping made by hand: exactly these files, in the order
            # they were named, and nothing searched in the folder.
            i = put[a]
            if i in done_by_hand:
                continue
            done_by_hand.add(i)
            row, discarded = list(by_hand[i]), list(turned_away.get(i) or [])
            for path in row:
                taken.add(path)
                discarded = discarded + homeless.pop(path, [])
            chains.append((row, discarded))
            continue
        if no_followups or a in apart:
            row, discarded = [a], []
        else:
            try:
                row, discarded = find_continuation_files(a)
            except Exception:
                row, discarded = [a], []
            row = [x for x in row if os.path.abspath(x) not in apart
                   and os.path.abspath(x) not in put]
        for path in row:
            taken.add(os.path.abspath(path))
            discarded = discarded + homeless.pop(path, [])
        chains.append((row, discarded))
    # A note whose file never reached a recording of its own: claimed by
    # another group, or not in the list at all. It still has to be read,
    # so it goes to the first recording rather than nowhere.
    if homeless and chains:
        left = [note for notes in homeless.values() for note in notes]
        chains[0] = (chains[0][0], list(chains[0][1]) + left)
    return chains


def recording_family(file_path):
    """Every block that would belong to this recording, marks aside.

    Used when a whole recording leaves the list: the marks of its blocks
    go with it, so adding the files again joins them up as before.
    """
    try:
        row, _discarded = find_continuation_files(os.path.abspath(file_path))
    except Exception:
        row = [os.path.abspath(file_path)]
    return {os.path.abspath(x) for x in row} | {os.path.abspath(file_path)}


def cameras_as_tracks(args):
    """How many cameras contribute their own audio as a track.

    Not a property of the command line but of the material: the answer
    travels in the assignment file, and without one it is none.
    """
    path = getattr(args, "assign", None)
    if not path or not os.path.exists(path):
        return 0
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except (ValueError, OSError):
        return 0
    rows = (d.get("tracks_of") if isinstance(d, dict) else d) or []
    return sum(1 for e in rows if isinstance(e, dict)
               and (e.get("camera_audio") or e.get("own_audio")
                    or e.get("from_camera")))


def check_mode_fits_input(audio_paths, args):
    """Report whether the selection fits the mode. Returns a message or None.

    Recordings are counted, not files: three blocks from one recorder are
    one source. A camera counts once the assignment marks its audio as a
    track, so one microphone recording and two cameras with their own
    sound are three tracks. Several cameras are allowed but not required.
    """
    if not args.multitrack:
        return None
    chains = len(group_recording_parts(audio_paths, args.no_follow_ups,
                                       getattr(args, "apart", ()),
                                       getattr(args, "together", ())))
    chains += cameras_as_tracks(args)
    if chains < 2:
        return as_warn(
            T('MULTITRACK NOT POSSIBLE\n  At least two input tracks are '
              'needed, and only %s was found.\n  A track is a recording of '
              'its own, a channel of a multichannel\n  recorder, or the '
              'audio of a camera -- that counts as soon as its\n  Camera '
              'audio says "use the audio". Without two of them there\n  '
              'is nothing to decouple, and the same file runs through as an\n'
              '  ordinary production.')
            % number_text(chains, 0))
    # A key is only needed where something is going to be sent. With
    # --auphonic-done the tracks are finished and lie in a folder.
    brings_own = bool(getattr(args, "auphonic_done", None))
    if (not args.auphonic_key
            and not getattr(args, "without_auphonic", False)
            and not brings_own):
        return as_warn(T('MULTITRACK NOT POSSIBLE\n  Without an API key '
                         'there is nothing to send to auphonic.com.\n  With '
                         '--without-auphonic it runs locally instead: '
                         'aligned,\n  mixed and cut, but without de-bleed '
                         'and leveler.'))
    return None


def named_people(pairs):
    """The people in these (name, camera) pairs who have both.

    A name without a camera is somebody in the mix, not somebody on
    screen, and the same name twice is one person.
    """
    return set((n or "").strip() for n, c in pairs
               if (n or "").strip()
               and c not in (IGNORE_AUDIO, MIX_ONLY))


def cut_has_people(pairs, cameras=0):
    """Whether these (name, camera) pairs give a camera cut.

    Two people with a name and a camera, Multitrack no part of it: the
    cut reads one list, and whether the people were told apart by a
    microphone each or by the separation makes no difference. The cameras
    may be the same one -- nothing is switched, but the cut still falls
    at every speaker change. One person alone needs a second camera.
    """
    named = named_people(pairs)
    return len(named) >= 2 or (len(named) == 1 and cameras >= 2)


def finished_tracks_deeper(base):
    """Look in the subfolders too, "Result" for instance.

    A folder that cannot be read answers like an empty one: whoever
    asks wants finished tracks, and there are none either way.
    """
    if not base or not os.path.isdir(base):
        return None
    try:
        names = sorted(os.listdir(base))
    except OSError:
        return None
    for name in names:
        below = os.path.join(base, name)
        if os.path.isdir(below) and not name.startswith("."):
            hit = finished_tracks_find(below)
            if hit:
                return hit
    return None


def assignment_pairs(voice_rows, assign_rows=()):
    """Every (name, camera) the assignment sheet holds.

    Both levels of it: the voices of a separation carry their own camera,
    and so does a recording with none underneath it. A recording whose
    voices are on screen answers MIX_ONLY, so it falls out wherever a
    camera is what counts and nobody is counted twice.
    """
    return ([(nv.get(), cv.get()) for _k, nv, cv in voice_rows]
            + [(nv.get(), cv.get()) for _r, nv, cv in assign_rows])


def cut_title_of(voice_rows, multitrack_on, assign_rows=(), cameras=0):
    """The name the cut box carries, read off the assignment sheet.

    The preview box stands beside it and has to say the same, so both
    names are worked out in one place.
    """
    return cut_box_title(assignment_pairs(voice_rows, assign_rows),
                         bool(multitrack_on), cameras)


def cut_kind_of(pairs, multitrack_on=False, cameras=0):
    """Which of the three things this cut is: "cameras", "wide", "speakers".

    Between two cameras the picture changes hands; on one camera the cut
    falls at every change of speaker instead, and a 360 degree camera is
    reframed rather than switched. With one person there is no change of
    speaker either -- their camera stands and the wide shot cuts in. The
    case is worked out here and nowhere else, but only the case.
    """
    on_camera = set(c for n, c in pairs
                    if (n or "").strip()
                    and c not in (IGNORE_AUDIO, MIX_ONLY))
    # Nothing separated yet says nothing about what will come of it, and
    # with Multitrack the pairs hold only the voices of the separation.
    if multitrack_on or not on_camera or len(on_camera) > 1:
        return "cameras"
    if len(named_people(pairs)) < 2 and cameras >= 2:
        return "wide"
    return "speakers"


def cut_box_title(pairs, multitrack_on=False, cameras=0):
    """What the cut box in the window is called."""
    return {"cameras": T('Camera cut'),
            "wide": T('Cut with the wide shot'),
            "speakers": T('First cut by speaker')}[
                cut_kind_of(pairs, multitrack_on, cameras)]


def cut_log_heading(pairs, cameras=0):
    """The same thing as the heading over the log section.

    Nobody on a camera at all is the one case the two places read
    differently: in the window the question is not answered yet, here
    the answer is no. So it is settled before asking, because
    cut_kind_of cannot tell "not yet" from "never".
    """
    kind = ("speakers" if not named_people(pairs)
            else cut_kind_of(pairs, False, cameras))
    return {"cameras": T('\nCAMERA CUT'),
            "wide": T('\nCUT WITH THE WIDE SHOT'),
            "speakers": T('\nFIRST CUT BY SPEAKER')}[kind]


def multitrack_state_note(tracks, cameras_left):
    """Why Multitrack is not on offer here, in one line, or "".

    The tick stays clickable: a greyed out control without a reason is a
    dead end, so the line beside it says what is missing instead.
    *tracks* is how many assignment rows are not set aside,
    *cameras_left* how many cameras could still give their audio. Nothing
    is said where nothing is known yet, or where two tracks are there.
    """
    if tracks >= 2:
        return ""
    if not tracks:
        return ""
    if cameras_left:
        return T('One track only -- set a camera\'s Camera audio to '
                 '"use the audio" for a second.')
    return T('One track only, and no camera audio left to take.')


def split_audio_and_video(paths):
    audio, video, other = [], [], []
    for p in paths:
        e = os.path.splitext(p)[1].lower()
        if e in AUDIO_SUFFIXES:
            audio.append(p)
        elif e in VIDEO_SUFFIXES:
            video.append(p)
        else:
            other.append(p)
    return audio, video, other
