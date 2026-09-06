# -*- coding: utf-8 -*-
"""The order a run is given: out of the window, and read back off the line.

slider_argv and run_argv write what the window holds as a command line;
build_argument_parser reads one back. A piece of the program, read in
by beside(): the program is handed in and bound below by name.
"""

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# Bound above the seam, so the order reads as it did in the window.
# Not one is a name the program binds again while it runs.
CUT_CHOICES = PROGRAM.CUT_CHOICES
CUT_FIELDS = PROGRAM.CUT_FIELDS
FILE_FORMAT = PROGRAM.FILE_FORMAT
IGNORE_AUDIO = PROGRAM.IGNORE_AUDIO
MIN_EDIT_DURATION_S = PROGRAM.MIN_EDIT_DURATION_S
MIN_SPEECH_TO_SWITCH_S = PROGRAM.MIN_SPEECH_TO_SWITCH_S
ONLY_MULTITRACK = PROGRAM.ONLY_MULTITRACK
PLATFORMS = PROGRAM.PLATFORMS
SILENCE_HOLD_S = PROGRAM.SILENCE_HOLD_S
T = PROGRAM.T
TYPE_IGNORED = PROGRAM.TYPE_IGNORED
TYPE_INTRO = PROGRAM.TYPE_INTRO
TYPE_OUTRO = PROGRAM.TYPE_OUTRO
TYPE_WIDE = PROGRAM.TYPE_WIDE
VERSION = PROGRAM.VERSION
VIDEO_SUFFIXES = PROGRAM.VIDEO_SUFFIXES
WIDE_AFTER_S = PROGRAM.WIDE_AFTER_S
argparse = PROGRAM.argparse
label_of = PROGRAM.label_of
languages = PROGRAM.languages
number_text = PROGRAM.number_text
os = PROGRAM.os
python_note = PROGRAM.python_note
separation_has_voices = PROGRAM.separation_has_voices


#--------------------------------------- Out of the window into an order
# What the window holds, written as the command line a run is given.
# Nothing here is Qt: plain values in, a list of strings out.


def slider_numbers(values):
    """Read the cut sliders as numbers.

    An empty field means the default and a comma a decimal point: "1,2"
    means 1.2. Returns ({field: (text, number)}, the first field that is
    not a number, or None); the text comes back because a message quotes it.
    """
    out = {}
    for api_key, _b, default_value, _e, _k, _l in CUT_FIELDS:
        raw = str((values or {}).get(api_key, "")).strip()
        raw = raw.replace(",", ".") or default_value
        try:
            out[api_key] = (raw, float(raw))
        except ValueError:
            return out, api_key
    return out, None


def voices_of_values(values):
    """Name -> camera file, out of what the interface holds.

    The window knows a camera by the name of its file; the run wants the
    file. A voice set to "no camera of its own" or left out is not in
    the answer -- it keeps its name in the markers and takes no picture.
    """
    where = {}
    for cam in (values.get("cameras") or ()):
        if not cam.get("path"):
            continue
        where[os.path.basename(cam["path"])] = cam["path"]
        if (cam.get("name") or "").strip():
            where[cam["name"].strip()] = cam["path"]
    out = {}
    for row in (values.get("voices") or ()):
        name = (row.get("name") or "").strip()
        pick = row.get("camera") or ""
        if name and pick in where:
            out[name] = where[pick]
    return out


def slider_argv(values):
    """Return the cut sliders as command line switches.

    Returns (switch list, the first field that is not a number, or None).
    The switches for the fields before the bad one are already in it.
    """
    numbers, bad = slider_numbers(values)
    out = []
    for api_key, _b, _v, _e, _k, _l in CUT_FIELDS:
        if api_key not in numbers:
            break
        out += ["--" + api_key, numbers[api_key][0]]
    for api_key, _b, default_value, allowed, _k, _l in CUT_CHOICES:
        picked = str((values or {}).get(api_key, "")).strip()
        out += ["--" + api_key,
                picked if picked in allowed else default_value]
    return out, bad


def run_argv(values, assignment_file_path=""):
    """Build the command line from what the interface holds.

    Nothing here is Qt: a dict of plain values in, a list of strings out.

    Returns (argv, plan, messages)

      argv      the command line, or None if something is missing
      plan      what goes into the assignment file, or None
      messages  list of (kind, title, text, button) in the order the
                interface should present them. "error" means show and
                abort, "question" means ask and abort on no.

    The order matters: the query about camera audio first, then the
    checks on the assignment, then the key.
    """
    messages = []

    def error(title, text):
        messages.append(("error", title, text, ""))
        return None, None, messages

    files = list(values.get("files") or [])
    clip_kind = dict(values.get("clip_kinds") or {})
    # Intro and outro are not cameras: they go as their own switch.
    edge = {}
    # One intro and one outro. Two of a kind would go into the same
    # switch and the last would silently win, so the run stops.
    doubled = []
    for file_path, kind in sorted(clip_kind.items()):
        switch = ("--intro" if kind == TYPE_INTRO
                  else "--outro" if kind == TYPE_OUTRO else None)
        if switch is None:
            continue
        if switch in edge:
            doubled.append((kind, edge[switch], file_path))
        edge[switch] = file_path
    if doubled:
        kind, first, second = doubled[0]
        return error(
            T('Two files as %s') % label_of(kind),
            T('%s and %s are both set to %s. Only one file can be that '
              '-- please set the other one back to content.')
            % (os.path.basename(first), os.path.basename(second),
               label_of(kind)))
    # Anything set to "ignore this video" does not come along at all.
    off = set(p for p, a in clip_kind.items() if a == TYPE_IGNORED)
    argv = ["videopodcast_magic.py"] + [p for p, _a in files
                                        if p not in edge.values()
                                        and p not in off]
    for switch, file_path in sorted(edge.items()):
        argv += [switch, file_path]
    # The wide shots stay in the file list: they are cameras like any
    # other, and the switch says only that no speaker belongs to them.
    for file_path in sorted(p for p, a in clip_kind.items()
                            if a == TYPE_WIDE and p not in off):
        argv += ["--wide-shot", file_path]
    if values.get("out_folder"):
        argv += ["--out", values["out_folder"]]
    # No switch means "take it from the source files", as on the line.
    if values.get("lufs") is not None:
        argv += ["--lufs", "%g" % values["lufs"]]
    if (values.get("speech_language") or "").strip():
        argv += ["--speech-language", values["speech_language"].strip()]
    # Blocks taken out by hand; without this the run joins them again.
    for p in sorted(values.get("apart") or ()):
        argv += ["--apart", p]
    # Files put into a recording by hand: the search would not find them.
    for group in (values.get("together") or ()):
        if len(group) > 1:
            argv += ["--together"] + list(group)
    if values.get("dry_run"):
        argv += ["--dry-run"]

    # The last net under the window's own mark: a voice whose name is on
    # somebody else already. Refused and not asked -- to the cut two
    # voices of one name are one person.
    voices = [(r.get("name") or "").strip()
              for r in (values.get("voices") or ())
              if r.get("camera") != IGNORE_AUDIO
              and (r.get("name") or "").strip()]
    twice = sorted(set(n for n in voices if voices.count(n) > 1))
    if twice:
        return error(
            T('One name for two voices'),
            T('%s stands on more than one voice. A name is a person, and '
              'the cut puts a person on one camera -- two voices of one '
              'name would be one person in two places.')
            % ", ".join(twice))

    plan = None
    if values.get("multitrack"):
        only_video = bool(values.get("camera_audio_only"))
        lines = [r for r in (values.get("rows") or [])
                  if r.get("camera_choice") != IGNORE_AUDIO]
        if only_video:
            messages.append((
                "question", T('Cameras only'),
                T('There are no separate audio recordings. Then the audio '
                  'of the %s cameras is used -- each becomes a track, and '
                  'Auphonic removes the bleed.')
                % number_text(len(values.get("rows") or []), 0),
                T('Take the camera audio')))
        if len(lines) < 2:
            return error(
                T('Multitrack needs several tracks'),
                T('Multitrack needs at least two input tracks. A track is '
                  'a recording of its own, a channel of a multichannel '
                  'recorder, or the audio of a video file set to "use the '
                  'audio". Several blocks of the same recording count as '
                  'one, tracks set aside not at all.'))
        names = [(r.get("speakers") or "").strip() for r in lines]
        if not all(names):
            return error(
                T('Speaker names'),
                T('Every row needs a name -- at Auphonic it becomes the '
                  'track ID.'))
        duplicate = sorted(set(n for n in names if names.count(n) > 1))
        if duplicate and len(set(names)) < 2:
            return error(
                T('Only one speaker'),
                T('All rows carry the same name -- that makes a single '
                  'track, and Multitrack needs at least two.'))
        if duplicate:
            messages.append((
                "question", T('Names used more than once'),
                T('These names occur more than once:\n\n  %s\n\nThe recordings '
                  'are merged into one track and laid end to end by their '
                  'timecode. That is right if recording was stopped in '
                  'between.')
                % "\n  ".join(duplicate), T('Merge them')))
        tracks = []
        for r in lines:
            blocks = list(r.get("blocks") or [])
            target = r.get("camera_choice") or ""
            full = ""
            for p, a in files:
                if a == "video" and os.path.basename(p) == target:
                    full = p
                    break
            camera_track = bool(r.get("own_audio"))
            # Two different things, kept apart: where the audio comes
            # from, and which camera the speaker is on. A clip-on plugged
            # into one camera may film a person another one carries.
            source = r.get("from_camera") or ""
            straight = bool(blocks) and os.path.splitext(
                blocks[0])[1].lower() in VIDEO_SUFFIXES
            entry = {"audio": blocks[0] if blocks else "",
                       "blocks": blocks,
                       "speakers": (r.get("speakers") or "").strip(),
                       "camera": full,
                       "camera_audio": bool(only_video or
                                            (camera_track and straight))}
            if camera_track or only_video:
                if not full:
                    # No camera picked: it belongs to the one it came from.
                    entry["camera"] = os.path.abspath(source or (
                        blocks[0] if blocks else ""))
                entry["from_camera"] = os.path.abspath(
                    source or (blocks[0] if blocks else ""))
                # What the background thread fetched is not fetched again.
                if r.get("audio_done"):
                    entry["audio_done"] = r["audio_done"]
            tracks.append(entry)
        cameras = [{"video": cam.get("path"),
                    "name": (cam.get("name") or "").strip()
                    or os.path.splitext(os.path.basename(
                        cam.get("path") or ""))[0]}
                   for cam in (values.get("cameras") or [])]
        if len(set(cam["name"] for cam in cameras)) != len(cameras):
            return error(
                T('File names'),
                T('Two cameras would produce the same new file. Please '
                  'give different names.'))
        plan = {"format": FILE_FORMAT,
                "created_by": "videopodcast-magic %s" % VERSION,
                "production": (values.get("production") or "").strip()
                or 'Production', "tracks_of": tracks, "cameras": cameras}
        # What the separation heard travels with the assignment. Raw and
        # in the time of its own file -- the run puts it on the axis.
        if separation_has_voices(values.get("speakers_of")):
            plan["speakers_of"] = values["speakers_of"]
            # And which camera each voice belongs to; without it the run
            # knows the voices and not where they sit.
            plan["voices_of"] = voices_of_values(values)
        argv += ["--multitrack", "--assign", assignment_file_path]
        if values.get("speakers_wanted") is False:
            argv += ["--no-speakers-local"]
    elif separation_has_voices(values.get("speakers_of")) \
            and assignment_file_path:
        # One track, and the voices in it already told apart. It travels
        # the way the multitrack path sends it, so the run does not spend
        # the minutes twice -- with the cameras, and with the sliders.
        plan = {"format": FILE_FORMAT,
                "created_by": "videopodcast-magic %s" % VERSION,
                "speakers_of": values["speakers_of"],
                "voices_of": voices_of_values(values)}
        argv += ["--speakers-from", assignment_file_path]
    if values.get("speakers_wanted") is False \
            and not values.get("multitrack"):
        argv += ["--no-speakers-local"]

    # The time window and the cut numbers belong to every run, not only
    # the two that carry an assignment file: In point and Out point are
    # a window over the material, and the preview is computed from these.
    if (values.get("in_point") or "").strip():
        argv += ["--in-point", values["in_point"].strip()]
    if (values.get("out_point") or "").strip():
        argv += ["--out-point", values["out_point"].strip()]
    part, bad = slider_argv(values.get("cut"))
    if bad:
        return error(
            T('Camera cut'),
            T('%r is not a number.') % (values.get("cut") or {})[bad])
    argv += part
    if not values.get("wide_at_edges"):
        argv += ["--no-wide-edges"]

    # Finished tracks lie in a folder and nothing is sent anywhere to
    # use them, so this stands outside "if key:".
    if values.get("done_folder"):
        argv += ["--auphonic-done", values["done_folder"]]

    key = (values.get("key") or "").strip()
    if key:
        selected = (values.get("preset") or "").strip()
        if not selected:
            return error(
                T('Preset missing'),
                T('Load Presets and pick one, or leave the API Key empty.'))
        argv += ["--auphonic-api-key", key, "--auphonic-preset", selected]
        # Only with a key: without auphonic.com there is nobody to
        # transcribe, and the switch would promise what cannot happen.
    elif values.get("multitrack"):
        # No key, no preset: it runs locally. Everything that only
        # auphonic.com can do is missing, and the run says so.
        argv += ["--without-auphonic"]
    return argv, plan, messages


def speakers_to_cameras(assign_lines, voice_lines, voiced=()):
    """Who is on which camera, out of the two tables that say so.

    *assign_lines* are the recording rows, *voice_lines* the voices a
    separation found under one of them, *voiced* the recordings whose
    voices stand underneath. Where the voices stand under a recording
    they carry the camera and the recording does not, or two answers
    could say different things about the same camera.
    """
    where_to = {}
    for chain, name_value, camera_value in assign_lines:
        if os.path.abspath(chain[0]) in (voiced or ()):
            continue
        n = name_value.get()
        if n and camera_value.get() != IGNORE_AUDIO:
            where_to[n] = camera_value.get()
    for _label, name_value, camera_value in voice_lines:
        n = name_value.get().strip()
        if n and camera_value.get() != IGNORE_AUDIO:
            where_to[n] = camera_value.get()
    return where_to


#---------------------------------------------------- An order read back
# The same switches the other way about. slider_argv writes them and
# this declares them, both out of CUT_FIELDS and CUT_CHOICES.


def build_argument_parser():
    """Define all command line switches."""
    ap = argparse.ArgumentParser(
        prog="videopodcast-magic",
        description="videopodcast-magic %s -- put processed audio into "
                    "video files as the first audio track" % VERSION)
    ap.add_argument("--version", action="version",
                    version="videopodcast-magic %s   %s"
                            % (VERSION, python_note()))
    ap.add_argument("--lang", choices=languages(), default=None,
                    help="language of the messages (default: the system's)")
    ap.add_argument("files", nargs="*",
                    help="audio and video files, told apart by extension. "
                         "Audio only = join and write.")
    ap.add_argument("--out", default=None,
                    help="output folder (default: next to each video)")
    ap.add_argument("--auphonic-api-key", dest="auphonic_key",
                    default=None, metavar="KEY",
                    help="API key from the Auphonic account settings. Turns "
                         "processing on. Without files it only lists the "
                         "presets.")
    ap.add_argument("--auphonic-preset", default=None, metavar="NAME",
                    help="preset name or id (default: asked for)")
    ap.add_argument("--auphonic-wait", dest="auphonic_wait", type=int,
                    default=7200, metavar="SECONDS",
                    help="how long to wait for Auphonic (default: 7200)")
    ap.add_argument("--suffix", default="_audio",
                    help="added to the file name (default: _audio)")
    ap.add_argument("--name-camera", dest="name_camera",
                    default="Camera Original",
                    help="name of the camera track (default: Camera Original)")
    ap.add_argument("--no-camera-audio", dest="no_camera_audio",
                    action="store_true",
                    help="drop the camera's own audio instead of keeping it")
    ap.add_argument("--no-follow-ups", dest="no_follow_ups",
                    action="store_true",
                    help="do not look for numbered continuation files "
                         "(default: they are looked for)")
    ap.add_argument("--apart", action="append", default=[], metavar="FILE",
                    help="this block stands on its own and is not joined "
                         "to a recording, even where its name says it is a "
                         "continuation. May be given several times. The "
                         "interface sets it when a single block is taken "
                         "out of a recording by hand.")
    ap.add_argument("--no-drift", dest="no_drift", action="store_true",
                    help="measure and report clock drift, but do not take "
                         "it out")
    ap.add_argument("--tc", default=None, metavar="HH:MM:SS:FF",
                    help="start timecode of the picture. Used to compare "
                         "against the audio and written into the result. "
                         "Needed where the camera wrote none or a wrong one. "
                         "(default: from the video file)")
    ap.add_argument("--fps", type=float, default=None, metavar="NUMBER",
                    help="frame rate to assume. Decides what a frame is -- "
                         "the frame counts and the threshold above which "
                         "clock drift is taken out. Needed only where "
                         "ffprobe reports a wrong rate. "
                         "(default: from the video file)")
    ap.add_argument("--speech-language", dest="speech_language",
                    default="", metavar="CODE",
                    help="language tag of the audio tracks, three letters "
                         "per ISO 639-2/B -- ger, eng, fra. Careful: ffmpeg "
                         "drops 'deu' silently. Empty means no tag. "
                         "(default: none)")
    ap.add_argument("--speakers-local", dest="speakers_local", default=None,
                    metavar="FILE",
                    help="take exactly that recording apart by voice, "
                         "instead of the one the run would pick itself. A "
                         "run picks a single audio recording, or the "
                         "longest camera track where there is none, and "
                         "takes it apart on its own. What it needs came "
                         "with the program; the run takes minutes. "
                         "(default: whatever the run picks)")
    ap.add_argument("--update", dest="update_now",
                    action="store_true", default=False,
                    help="let pip fetch the newer version, in the Python "
                         "this is running in, and write what pip says "
                         "here. A run only ever says that one is out; "
                         "nothing is fetched without this. (default: off)")
    ap.add_argument("--speakers-from", dest="speakers_from", default=None,
                    metavar="FILE",
                    help="take a finished separation out of a project or "
                         "assignment file instead of computing one. "
                         "(default: none)")
    ap.add_argument("--speakers-count", dest="speakers_count", type=int,
                    default=0, metavar="NUMBER",
                    help="how many people --speakers-local should find. A "
                         "given number improves the recognition and "
                         "quadruples the picture time on the wrong person, "
                         "so it is set only where it is known. "
                         "(default: work it out)")
    ap.add_argument("--no-speakers-local", dest="no_speakers_local",
                    action="store_true",
                    help="never take a recording apart by voice in this "
                         "run, whatever else says so. (default: off)")
    ap.add_argument("--no-speech-recognition", dest="no_speech_recognition",
                    action="store_true",
                    help="do not write down what is said. The cut then has "
                         "no sentence boundaries and the wide shot goes to "
                         "the longest pause nearby. (default: off)")
    ap.add_argument("--no-transcript-file", dest="no_transcript_file",
                    action="store_true",
                    help="write no transcript beside the result. Normally "
                         "the words that were heard go into the output "
                         "folder as json, srt and txt. (default: off)")
    ap.add_argument("--auphonic-resume", dest="auphonic_resume", default=None,
                    choices=("result", "rerun", "adopt", "upload", "abort"),
                    help="what to do when the production is already there: "
                         "result = take the existing one, rerun = compute "
                         "again with the chosen preset without a new upload "
                         "(costs nothing), adopt = the same, but take the "
                         "track names there as speaker names, upload = "
                         "everything again, abort = stop. Without this it "
                         "asks. (default: ask)")
    ap.add_argument("--auphonic-done", dest="auphonic_done", default=None,
                    metavar="FOLDER",
                    help="folder holding tracks Auphonic has already "
                         "processed (files named after the speakers). Then "
                         "nothing is uploaded and no credit is spent -- for "
                         "a second run on the same audio. (default: none)")
    ap.add_argument("--min-edit-duration", dest="min_edit_duration", type=float,
                    default=MIN_EDIT_DURATION_S, metavar="SECONDS",
                    help="shortest a shot may stand. Anything shorter is "
                         "merged into the one that follows; 0 turns it "
                         "off. Three "
                         "seconds is what interview cutting practice asks "
                         "for -- a camera that changes faster than the "
                         "viewer can settle on a face reads as nervous. "
                         "SmartSwitch calls the same thing 1.00, which is "
                         "why this used to be 1.2. (default: 3)")
    ap.add_argument("--min-speech-to-switch", dest="min_speech_to_switch",
                    type=float, default=MIN_SPEECH_TO_SWITCH_S,
                    metavar="SECONDS",
                    help="how long somebody has to hold the floor before "
                         "the camera follows them. Below it the picture "
                         "stays where it is: a short \"yes\" is not a "
                         "change of speaker, and without this the minimum "
                         "edit duration then holds the wrong person on "
                         "screen for seconds. 0 turns it off. (default: "
                         "1.5)")
    ap.add_argument("--silence-hold", dest="silence_hold", type=float,
                    default=SILENCE_HOLD_S, metavar="SECONDS",
                    help="how long a silence may be and still count as a "
                         "breath rather than an end. Only where "
                         "--on-silence hold-brief asks for it: up to here "
                         "the picture stays, beyond it the wide shot "
                         "comes. (default: 1.0)")
    ap.add_argument("--edit-change-delay", dest="delay", type=float,
                    default=0.3, metavar="SECONDS",
                    help="how much later than the audio the picture cuts. "
                         "Negative lets the picture lead. (default: 0.3)")
    ap.add_argument("--reaction-lead", dest="reaction_lead", type=float,
                    default=1.5, metavar="SECONDS",
                    help="how much earlier the picture goes to the answer "
                         "after a question. Only where --on-question asks "
                         "for it. (default: 1.5)")
    ap.add_argument("--reaction-gap", dest="reaction_gap", type=float,
                    default=3.0, metavar="SECONDS",
                    help="how soon the answer has to follow the question "
                         "for the reaction cut to fire. (default: 3)")
    ap.add_argument("--reaction-hold", dest="reaction_hold", type=float,
                    default=0.7, metavar="SHARE",
                    help="how much of the ten seconds after the question "
                         "the answering speaker has to hold, as a share "
                         "between 0 and 1. (default: 0.7)")
    for switch, _caption, default_value, values, _short, _long in CUT_CHOICES:
        ap.add_argument("--" + switch, dest=switch.replace("-", "_"),
                        choices=list(values), default=default_value,
                        help="what is shown where the speech does not say "
                             "it: %s. (default: %s)"
                             % (", ".join(values), default_value))
    ap.add_argument("--wide-after", dest="wide_after", type=float,
                    default=WIDE_AFTER_S, metavar="SECONDS",
                    help="from this hold time on, a shot is broken up by "
                         "leaving the speaker for a while -- placed on a "
                         "sentence boundary nearby, not by the clock. "
                         "0 turns it off. (default: 70)")
    ap.add_argument("--wide-length", dest="wide_length", type=float,
                    default=5.0, metavar="SECONDS",
                    help="how long such an interposed shot stands at "
                         "least; it then runs to the end of the sentence. "
                         "(default: 5)")
    ap.add_argument("--wide-most", dest="wide_most", type=float,
                    default=15.0, metavar="SECONDS",
                    help="how long it stands at most. Where the end of the "
                         "sentence lies beyond it, the last clause break "
                         "before it ends the shot. (default: 15)")
    ap.add_argument("--wide-latest", dest="wide_latest", type=float,
                    default=120.0, metavar="SECONDS",
                    help="upper limit: longest one camera may stand without "
                         "a cut. Where no good pause turns up, it cuts "
                         "anyway. (default: 120)")
    ap.add_argument("--no-wide-edges", dest="no_wide_edges",
                    action="store_true",
                    help="do NOT hold the wide shot at the beginning and the "
                         "end. By default the picture stays wide while the "
                         "greeting and the goodbye are spoken.")
    ap.add_argument("--parallel", type=int, default=0, metavar="COUNT",
                    help="process this many video files at once. 0 = decide "
                         "for me, 1 = one after another. (default: 0)")
    ap.add_argument("--no-metrics", dest="no_metrics", action="store_true",
                    help="measure no metrics at the end and compare no "
                         "camera colours. Saves a few minutes on long "
                         "recordings.")
    ap.add_argument("--intro", default=None, metavar="FILE",
                    help="video file laid over the beginning. It sits on the "
                         "second picture and audio track, so its sound "
                         "carries on under the first words. It is neither "
                         "aligned nor processed. (default: none)")
    ap.add_argument("--outro", default=None, metavar="FILE",
                    help="the same for the end: it starts where the last "
                         "word ends. (default: none)")
    ap.add_argument("--wide-shot", dest="wide_shot", action="append",
                    default=None, metavar="FILE",
                    help="this video file is a wide shot: a camera nobody "
                         "sits in front of. It is filmed, aligned and cut "
                         "to like any other, it just takes no speaker. May "
                         "be given several times. Without it the cameras "
                         "no speaker is assigned to are the wide shots. "
                         "(default: none, so derived)")
    ap.add_argument("--no-single-tracks", dest="no_single_tracks",
                    action="store_true",
                    help="put only the mix into the video, not the single "
                         "recordings beside it. Without Multitrack several "
                         "recordings running at the same time are mixed "
                         "into one track; by default each also goes in on "
                         "its own, unprocessed, so the edit can reach for "
                         "one voice. That costs about 520 MB per track and "
                         "hour.")
    ap.add_argument("--together", action="append", nargs="+",
                    default=[], metavar="FILE",
                    help="these files are one recording, in this order. The "
                         "counterpart to --apart, for blocks the search "
                         "cannot recognise as belonging together -- a "
                         "recorder whose file names carry neither a counter "
                         "nor a clock. Repeatable for several recordings.")
    ap.add_argument("--no-preflight", dest="no_preflight",
                    action="store_true",
                    help="skip the preflight report. By default the material "
                         "is checked before the first long step starts.")
    ap.add_argument("--preflight-again", dest="preflight_again",
                    action="store_true",
                    help="measure the preflight again instead of taking the "
                         "stored measurement. Not needed: a changed file is "
                         "measured again anyway.")
    ap.add_argument("--anyway", action="store_true",
                    help="run even where the preflight found a reason to "
                         "stop.")
    ap.add_argument("--lufs", type=float, default=None,
                    help="loudness the sum of all speaker tracks is brought "
                         "to. The same gain goes on every track, so their "
                         "balance is kept. Usual values: %s. Without it "
                         "nothing is adjusted: the sound is taken from the "
                         "source files as it is, and auphonic.com goes on "
                         "doing what its preset says. (default: none)"
                    % ", ".join("%.0f = %s" % (lufs, what)
                                for lufs, what in PLATFORMS.values()))
    ap.add_argument("--assign", default=None, metavar="FILE",
                    help="JSON file holding which audio track belongs to "
                         "which camera. The interface writes it; this is how "
                         "the assignment reaches a run without it. "
                         "(default: none)")
    ap.add_argument("--without-auphonic", dest="without_auphonic",
                    action="store_true",
                    help="run without auphonic.com: align, mix and write "
                         "locally. The camera cut then comes from a speech "
                         "detection of our own. No de-bleed, no leveler, no "
                         "noise removal.")
    ap.add_argument("--multitrack", action="store_true",
                    help="send every audio file to Auphonic as its own "
                         "track, so the bleed between the microphones can be "
                         "removed. Needs two input tracks -- a recording "
                         "of its own, a channel of a multichannel "
                         "recorder, or the audio of a camera -- and a "
                         "multitrack preset. Which audio belongs to which "
                         "camera comes from --assign; the interface writes "
                         "that file.")
    ap.add_argument("--speech-language-camera", dest="speech_language_camera",
                    default="", metavar="CODE",
                    help="the same for the camera track. Empty means no tag "
                         "-- that is what makes the QuickTime player tell "
                         "the two entries in its audio menu apart at all "
                         "(default: empty)")
    ap.add_argument("--in-point", dest="in_point", default=None, metavar="TIME",
                    help="start of the time window. A timecode like 17:20:14 "
                         "or 17:20:14:00 is absolute, +12:30 or 90 counts "
                         "from the start of the measured window. "
                         "(default: from the video files)")
    ap.add_argument("--out-point", dest="out_point", default=None, metavar="TIME",
                    help="end of the time window, same notation. A negative "
                         "value like -30 counts back from the end. "
                         "(default: from the video files)")
    ap.add_argument("--resolve", action="store_true",
                    help="afterwards create the project in DaVinci Resolve, "
                         "import the finished files and build the timelines. "
                         "Resolve has to be running. (default: off)")
    ap.add_argument("--hdr-check", dest="hdr_check", default=None,
                    metavar="FILE",
                    help="only look: does this finished file carry "
                         "everything that marks it as HDR? Checks primaries, "
                         "curve, matrix, bit depth, codec profile and the "
                         "static metadata. Changes nothing.")
    ap.add_argument("--resolve-json", dest="resolve_json", default=None,
                    metavar="FILE",
                    help="run only the Resolve part, from a "
                         "Production_resolve.json that is already there. "
                         "Then nothing is measured and nothing written.")
    ap.add_argument("--resolve-audio-tracks", dest="resolve_audio_tracks",
                    action="store_true",
                    help="only look: for the project open in Resolve, print "
                         "the audio channel mapping of every clip and the "
                         "tracks of every timeline. Changes nothing.")
    ap.add_argument("--resolve-project", dest="resolve_project", default=None,
                    choices=("update", "keep", "new", "abort"),
                    help="what to do when the Resolve project is already "
                         "there: update = delete both timelines and build "
                         "them again, keep = put the new ones beside them, "
                         "new = a second project alongside, abort = stop. "
                         "Without this it asks.")
    ap.add_argument("--dry-run", action="store_true",
                    help="only measure and report, write nothing")
    # A switch that needs several recordings says so, or it would be
    # taken and do nothing. Marked here rather than at the call site:
    # --help builds its own parser and never reaches that one.
    for entry in ap._actions:
        if entry.dest in ONLY_MULTITRACK:
            entry.help = (entry.help or "") + "  [multitrack only]"
    return ap
