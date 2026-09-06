# -*- coding: utf-8 -*-
"""What the window holds, read as the order the run is given.

A piece of the program, read out of the folder beside the way in by
beside(). It cannot import the file it was cut out of, because that
file is still being read while this one is; the program is handed in
instead, and every name this piece uses out of it is bound below, by
name. What the window still calls out of it, it binds there in turn.
"""

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

# What the program has and this piece uses, bound once so that the
# order reads as it did in the window. Not one of them is a name the
# program binds again while it runs -- such a name is read through
# PROGRAM. where it is used, and there is none of that sort in here.
CUT_CHOICES = PROGRAM.CUT_CHOICES
CUT_FIELDS = PROGRAM.CUT_FIELDS
FILE_FORMAT = PROGRAM.FILE_FORMAT
IGNORE_AUDIO = PROGRAM.IGNORE_AUDIO
T = PROGRAM.T
TYPE_IGNORED = PROGRAM.TYPE_IGNORED
TYPE_INTRO = PROGRAM.TYPE_INTRO
TYPE_OUTRO = PROGRAM.TYPE_OUTRO
TYPE_WIDE = PROGRAM.TYPE_WIDE
VERSION = PROGRAM.VERSION
VIDEO_SUFFIXES = PROGRAM.VIDEO_SUFFIXES
group_text = PROGRAM.group_text
label_of = PROGRAM.label_of
os = PROGRAM.os
separation_has_voices = PROGRAM.separation_has_voices


def slider_numbers(values):
    """Read the cut sliders as numbers.

    An empty field means the default and a comma means a decimal point --
    typing "1,2" means 1.2 and should not produce an error.

    Returns ({field: (text, number)}, the first field that is not a number, or
    None). The text comes back too because the command line passes it on
    unchanged and the message quotes it.
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

    The window knows a camera by the name of its file; the run wants
    the file. A voice set to "no camera of its own" or left out is not
    in the answer -- it keeps its name in the markers and takes no
    picture.
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

    Returns (switch list, the first field that is not a number, or None). The
    switches for the fields before the bad one are already in the list.
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

    This part has nothing to do with Qt: a dict of plain values goes in, a
    list of strings comes out. It decides what a run does, and can be
    tested without opening a window.

    Returns (argv, plan, messages)

      argv      the command line, or None if something is missing
      plan      what goes into the assignment file, or None
      messages  list of (kind, title, text, button) in the order the
                interface should present them. "error" means show and
                abort, "question" means ask and abort on no.

    The order matters: first the query about camera audio, then the checks on
    the assignment, then the key. Answering the first query with no means the
    later messages are never seen.
    """
    messages = []

    def error(title, text):
        messages.append(("error", title, text, ""))
        return None, None, messages

    files = list(values.get("files") or [])
    clip_kind = dict(values.get("clip_kinds") or {})
    # Intro and outro are not cameras: they do not go into the file list but
    # along as their own switch.
    edge = {}
    # One intro and one outro. Two files of the same kind would go into
    # the same switch and the last one would silently win, so the run
    # stops and names the two that are meant.
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
    # The wide shots stay in the file list -- they are cameras, and the
    # run films, aligns and renders them like any other. The switch
    # only says that no speaker belongs to them.
    for file_path in sorted(p for p, a in clip_kind.items()
                            if a == TYPE_WIDE and p not in off):
        argv += ["--wide-shot", file_path]
    if values.get("out_folder"):
        argv += ["--out", values["out_folder"]]
    # No switch means "take it from the source files", the same as on the
    # command line. So the entry that adjusts nothing adds nothing here.
    if values.get("lufs") is not None:
        argv += ["--lufs", "%g" % values["lufs"]]
    if (values.get("speech_language") or "").strip():
        argv += ["--speech-language", values["speech_language"].strip()]
    # Blocks taken out of a recording by hand. Without this the run
    # searches the folder and joins them up again.
    for p in sorted(values.get("apart") or ()):
        argv += ["--apart", p]
    # Files put into a recording by hand. The search would not find them
    # together, so the run has to be told.
    for group in (values.get("together") or ()):
        if len(group) > 1:
            argv += ["--together"] + list(group)
    if values.get("dry_run"):
        argv += ["--dry-run"]

    # The last net under the window's own mark: a voice whose name is
    # on somebody else already. Refused and not asked -- to the cut two
    # voices of one name are one person, and there is nothing sensible
    # to do with the answer "yes, merge them".
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
                % group_text(len(values.get("rows") or [])),
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
            # Two different things, kept apart: where the audio comes from,
            # and which camera the speaker is on. For a clip-on microphone
            # plugged into one camera they need not be the same -- the
            # person may well be filmed by another one.
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
                    # No camera picked: the track belongs to the one it
                    # came out of.
                    entry["camera"] = os.path.abspath(source or (
                        blocks[0] if blocks else ""))
                entry["from_camera"] = os.path.abspath(
                    source or (blocks[0] if blocks else ""))
                # What the background thread has already fetched the run
                # need not fetch again.
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
            # And which camera each voice belongs to. The simple path
            # has sent this along since it learned to cut; multitrack
            # never did, so the run knew the voices and not where they
            # sit.
            plan["voices_of"] = voices_of_values(values)
        argv += ["--multitrack", "--assign", assignment_file_path]
        if values.get("speakers_wanted") is False:
            argv += ["--no-speakers-local"]
    elif separation_has_voices(values.get("speakers_of")) \
            and assignment_file_path:
        # One track, and the voices in it already told apart. It
        # travels the way the multitrack path sends it, so the run does
        # not spend the minutes twice -- and with it which camera each
        # voice belongs to, which only the window knows. The sliders go
        # too: since 24.8.2026 this path cuts as well, and numbers that
        # do not reach the run are numbers that do nothing.
        plan = {"format": FILE_FORMAT,
                "created_by": "videopodcast-magic %s" % VERSION,
                "speakers_of": values["speakers_of"],
                "voices_of": voices_of_values(values)}
        argv += ["--speakers-from", assignment_file_path]
    if values.get("speakers_wanted") is False \
            and not values.get("multitrack"):
        argv += ["--no-speakers-local"]

    # The time window and the cut numbers belong to every run, not only
    # to the two that carry an assignment file. They hang on no
    # speaker: In point and Out point are a window over the material,
    # and docs/simple-path.md promises them to the simple way in so
    # many words. The cut numbers are what the preview beside them is
    # computed from, and a preview that is computed from other numbers
    # than the run uses is worse than none.
    #
    # Until 2.10.1-beta these sat inside the two branches above. On the
    # third way -- no Multitrack, no separation in the window -- In
    # point, Out point, the numbers, the choices and the wide shot tick
    # all stayed in the window, the run cut with the built-in defaults,
    # and nothing said so.
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

    # Finished tracks lie in a folder, and nothing is sent anywhere to
    # use them. This used to hang inside "if key:", so a run without a
    # key never saw the folder -- the same lock as on the command line,
    # found on 23.8.2026 while opening that one.
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
        # transcribe, and the switch would promise something that
        # cannot happen.
    elif values.get("multitrack"):
        # No key, no preset: it runs locally. Everything that only
        # auphonic.com can do is missing, and the run says so.
        argv += ["--without-auphonic"]
    return argv, plan, messages


def speakers_to_cameras(assign_lines, voice_lines, voiced=()):
    """Who is on which camera, out of the two tables that say so.

    *assign_lines* are the recording rows, *voice_lines* the voices a
    separation found under one of them, *voiced* the recordings whose
    voices stand underneath.

    The assignment has exactly one level. Where the voices of a
    recording stand under it, they carry the camera and the recording
    does not -- two answers one above the other could say different
    things about the same camera. Two voices on one camera are one
    condition and not two; segments_per_camera folds them together.
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
