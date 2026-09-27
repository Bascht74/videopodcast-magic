# -*- coding: utf-8 -*-
"""The chain: the recordings become the plan the time base runs.

A piece of the program, read out of the folder beside it by beside().
It cannot import the file it was cut out of, because that file is
still being read while this one is; the program is handed in instead,
and every name this piece uses out of it is bound below, by name.
"""

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

# What the program has and this piece uses, bound once so the chain
# reads as in the one file. None is missing or read late: none is bent
# while the run goes on, so a copy taken here cannot go stale.

ByFile = PROGRAM.ByFile
MIX_ONLY = PROGRAM.MIX_ONLY
SR = PROGRAM.SR
T = PROGRAM.T
as_bad = PROGRAM.as_bad
as_head = PROGRAM.as_head
as_hms = PROGRAM.as_hms
atexit = PROGRAM.atexit
bext_time_reference = PROGRAM.bext_time_reference
build_common_timebase = PROGRAM.build_common_timebase
camera_targets = PROGRAM.camera_targets
channel_count = PROGRAM.channel_count
channel_facts_cached = PROGRAM.channel_facts_cached
channel_text = PROGRAM.channel_text
format_complaint = PROGRAM.format_complaint
group_recording_parts = PROGRAM.group_recording_parts
guess_camera_name = PROGRAM.guess_camera_name
guess_speaker_name = PROGRAM.guess_speaker_name
json = PROGRAM.json
label_of = PROGRAM.label_of
number_text = PROGRAM.number_text
os = PROGRAM.os
parse_timecode = PROGRAM.parse_timecode
path_key = PROGRAM.path_key
pcm_kind = PROGRAM.pcm_kind
safe_filename = PROGRAM.safe_filename
sample_count = PROGRAM.sample_count
shell_quote = PROGRAM.shell_quote
show_progress = PROGRAM.show_progress
shutil = PROGRAM.shutil
split_channels = PROGRAM.split_channels
split_target = PROGRAM.split_target
step_begin = PROGRAM.step_begin
sync_only = PROGRAM.sync_only
tempfile = PROGRAM.tempfile
track_name_of = PROGRAM.track_name_of
track_order_for_camera = PROGRAM.track_order_for_camera
tracks_per_camera = PROGRAM.tracks_per_camera
tracks_to_split = PROGRAM.tracks_to_split
video_facts = PROGRAM.video_facts
wav_safe = PROGRAM.wav_safe


# ================  The chain, in the order a run takes it  ==========
#  The camera audio out of the pictures, and the plan timebase/ puts
#  on one axis and back on them.


def unpack_kind(file_path):
    """The depth to unpack a video's audio at: the one it is in.

    pcm_kind measures it; this caps the one answer that cannot be taken
    literally. AAC probes as floating point, and unpacking it as float
    costs a third more room for nothing that was ever in the file. 24
    bit holds everything a camera delivers, and where nothing can be
    measured pcm_kind already answers 24 bit.
    """
    deep = pcm_kind(file_path)
    return "pcm_s24le" if deep == "pcm_f32le" else deep


def extract_audio_from_video(file_path, tmpdir):
    """Extract one camera's audio unchanged.

    Nothing is folded to mono: a single file may carry different
    material left and right, and that should not be lost.
    """
    file_path = os.path.abspath(file_path)
    stem = os.path.splitext(os.path.basename(file_path))[0]
    target = os.path.join(tmpdir, "%s.wav" % safe_filename(stem))
    info = video_facts(file_path)
    if not info["audio"]:
        raise RuntimeError(T('%s has no audio track.') % os.path.basename(file_path))
    channels = int((info["audio"][0] or {}).get("channels") or 1)
    print(as_head(T('NO AUDIO FILE -- USING THE CAMERA AUDIO')))
    print(T('  from %s, %s')
          % (PROGRAM.camera_shown(file_path), channel_text(channels)))
    command = ["ffmpeg", "-v", "error", "-i", file_path, "-map", "0:a:0",
              "-ar", str(SR), "-c:a", unpack_kind(file_path),
              "-write_bext", "1"]
    if info.get("tc"):
        # The audio starts where the picture starts. Passing the timecode along
        # saves the alignment from guessing.
        try:
            t0 = parse_timecode(info["tc"], max(1.0, info["fps"]))
            # A field of the BWF header, counted in samples and read
            # by the editor, never by a person: plain digits.
            command += ["-metadata",
                       "time_reference=%d" % int(round(t0 * SR))]
            print("  " + T('Timecode %s') % info["tc"])
        except Exception:
            pass
    show_progress(T('Camera audio'), 0.0)
    shell_quote(command + wav_safe(target) + ["-y", target])
    show_progress(T('Camera audio'), 1.0)
    print("  %s" % os.path.basename(target))
    return target


def extract_audio_for_plan(plan, tmpdir):
    """Extract the camera audio for a finished plan.

    The names come from the interface, one row per camera. The channels
    are the camera's own: two clip-on microphones have already been cut
    into two rows by then, and a real stereo pair should keep its sides.
    """
    pending = [e for e in plan if e.get("camera_audio")]
    if not pending:
        return list(plan)
    step_begin("camera audio")
    # Where the interface has already extracted everything there is nothing to
    # show -- the prework belongs in the interface, not in the log of the run.
    to_fetch = [e for e in pending
                if not (e.get("audio_done")
                        and os.path.exists(e["audio_done"]))]
    if to_fetch:
        print(as_head(T('EXTRACTING CAMERA AUDIO')))
    done = []
    for i, e in enumerate(plan):
        if not e.get("camera_audio"):
            # An ordinary audio recording stays as it is.
            done.append(dict(e))
            continue
        # Where the audio is pulled from is the camera it was recorded on,
        # not the camera the speaker is assigned to.
        v = os.path.abspath(e.get("from_camera") or e["camera"] or e["audio"])
        name = e.get("speakers") or guess_camera_name(v)
        # The interface extracts the audio while names are still being typed.
        # Whatever is there is used.
        already = e.get("audio_done")
        if already and os.path.exists(already) and sample_count(already) > 0:
            fresh = dict(e)
            fresh.update({"audio": already, "blocks": [already],
                        "speakers": name, "upfront": True})
            fresh.setdefault("camera", v)
            done.append(fresh)
            continue
        target = os.path.join(tmpdir, "cameraaudio_%s.wav" % safe_filename(name))
        show_progress(T('Camera audio %s') % name, i / float(len(plan)))
        try:
            shell_quote(["ffmpeg", "-v", "error", "-i", v, "-map", "0:a:0",
                "-ac", str(max(1, channel_count(v))), "-ar", str(SR),
                "-c:a", unpack_kind(v)]
                + wav_safe(target) + ["-y", target])
        except Exception as ex:
            print(T('\n  %s: no audio to extract (%s)')
                  % (PROGRAM.camera_shown(v), ex))
            continue
        pieces = camera_audio_tracks(target, name, tmpdir)
        for piece, label in pieces:
            fresh = dict(e)
            fresh.update({"audio": piece, "blocks": [piece],
                          "speakers": label if len(pieces) > 1 else name})
            fresh.setdefault("camera", v)
            fresh.setdefault("from_camera", v)
            done.append(fresh)
    if to_fetch:
        show_progress(T('Camera audio'), 1.0)
        for e in done:
            if not e.get("camera_audio") or e.get("upfront"):
                continue
            print(T('  %-24s from %s')
                  % (e["speakers"], PROGRAM.camera_shown(
                      e.get("from_camera") or e["camera"])))
    if len(done) < 2:
        print(T('  Fewer than two cameras with sound -- too few for '
                'Multitrack.'))
    return done


def camera_audio_tracks(audio, name, folder):
    """Cut a camera's audio into the tracks it holds.

    A camera is not automatically one track: two clip-on microphones on
    one channel each are two people, judged by the same measurement as a
    recorder file. The audio is extracted with every channel it has --
    folding first and then asking what is on it always answers "one
    voice". Returns [(file, name)], one entry where nothing is cut.
    """
    try:
        facts = channel_facts_cached(audio)
        want = tracks_to_split(audio, facts, name=name)
    except Exception:
        want = []
    if not want:
        return [(audio, name)]
    out = []
    for chs, label in want:
        target = split_target(audio, chs, folder)
        try:
            if not os.path.exists(target) or not os.path.getsize(target):
                split_channels(audio, chs, target, rate=SR)
        except Exception as e:
            print(T('  %s: channel %s cannot be cut out (%s)')
                  % (name, "+".join(str(c + 1) for c in chs), e))
            return [(audio, name)]
        out.append((target, label))
    return out


def name_apart(name, taken):
    """*name*, or with 2, 3 ... hung on where it is taken; then taken too.

    The name is an identifier: it goes to Auphonic as the track id, into
    the written file's name and the handover's track. Plain digits, or
    the three would not match; and "Cam" takes "cam", as a disc that
    does not tell case apart holds one file for both.
    """
    wanted, count = name, 2
    while name.lower() in taken:
        name = "%s %d" % (wanted, count)
        count += 1
    taken.add(name.lower())
    return name


def cameras_plainly_named(cameras):
    """Make every camera's name a plain file name, and say where it moved.

    The name becomes the written file, the handover's camera and the
    cut list's reel, so it is changed once, here, for all three. A
    separator made a folder of it, and a leading one wrote the file
    beside the source instead of into the result folder. --new-name
    refuses the same three signs; a name from the window is not asked.
    """
    taken = {cam["name"].lower() for cam in cameras}
    for cam in cameras:
        plain = cam["name"].translate({ord(c): "_" for c in "/\\:"})
        if plain != cam["name"]:
            plain = name_apart(plain, taken)
            print(T('  The camera name "%s" holds a folder or drive '
                    'separator; it is written as "%s".')
                  % (cam["name"], plain))
            cam["name"] = plain
    return cameras


def plan_from_camera_audio(video_paths, tmpdir, cameras=None, title=""):
    """Use each video file's own audio as a track.

    For the case where there are no separate audio recordings, only
    cameras with a built-in or clip-on microphone: each camera becomes a
    track and the crosstalk from the others is removed. A camera
    carrying two microphones becomes two tracks, as a recorder file does.
    """
    step_begin("camera audio")
    plan = []
    prefixes = [t + "_" for t in {title, safe_filename(title)} if t]
    named = ByFile((cam["video"], cam["name"])
                   for cam in (cameras or []) if cam.get("video"))
    taken = set()
    print(as_head(T('NO SEPARATE AUDIO RECORDINGS -- USING THE CAMERA AUDIO')))
    for i, v in enumerate(video_paths, 1):
        v = os.path.abspath(v)
        # The name has to differ per camera: it becomes the track identifier at
        # Auphonic. The file stem serves; nothing is guessed here.
        name = named.get(v) or os.path.splitext(os.path.basename(v))[0]
        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):]
                break
        name = name_apart(name, taken)
        target = os.path.join(tmpdir, "cameraaudio_%s.wav" % safe_filename(name))
        show_progress(T('Camera audio %s') % name, (i - 1) / float(
            len(video_paths)))
        try:
            shell_quote(["ffmpeg", "-v", "error", "-i", v, "-map", "0:a:0",
                "-ac", str(max(1, channel_count(v))), "-ar", str(SR),
                "-c:a", unpack_kind(v)]
                + wav_safe(target) + ["-y", target])
        except Exception as e:
            print(T('\n  %s: no audio to extract (%s)')
                  % (PROGRAM.camera_shown(v), e))
            continue
        for piece, label in camera_audio_tracks(target, name, tmpdir):
            plan.append({"audio": piece, "blocks": [piece],
                         "speakers": label, "camera": v,
                         "from_camera": v})
    show_progress(T('Camera audio'), 1.0)
    for e in plan:
        print(T('  %-24s from %s') % (e["speakers"],
                                  PROGRAM.camera_shown(e["camera"])))
    if len(plan) < 2:
        print(T('  Fewer than two cameras with sound -- too few for '
                'Multitrack.'))
    return plan


def merge_plan_entries(plan):
    """Merge plan rows that share a speaker name into one track.

    Stopping the recording in between leaves several files for the same
    person; their timecodes place them anyway, and as one track it stays
    one person at Auphonic. A row marked "apart" stays put and is no
    target either: two blocks of one recorder guess the same name, so
    without that mark this undid what --apart had separated.
    """
    combined = []
    after_name = {}
    for e in plan:
        name = (e.get("speakers") or "").strip()
        blocks = list(e.get("blocks") or [e["audio"]])
        if name and name in after_name and not e.get("apart"):
            old = after_name[name]
            old["blocks"] += blocks
            if not old.get("camera") and e.get("camera"):
                old["camera"] = e["camera"]
            elif (e.get("camera") and old.get("camera")
                  and os.path.abspath(e["camera"])
                  != os.path.abspath(old["camera"])):
                print(T('  %s appears twice with different cameras -- %s '
                        'is used')
                      % (name, PROGRAM.camera_shown(old["camera"])))
            continue
        fresh = dict(e)
        fresh["blocks"] = blocks
        fresh["speakers"] = name
        combined.append(fresh)
        if name and not fresh.get("apart"):
            after_name[name] = fresh
    for e in combined:
        e["blocks"] = sort_by_time(e["blocks"])
        e["audio"] = e["blocks"][0]
    more = [(e["speakers"], len(e["blocks"])) for e in combined
            if len(e["blocks"]) > 1]
    if len(combined) < len(plan):
        print(T('  In summary: %s')
              % ", ".join(T('%s from %s recordings') % (n, number_text(k, 0))
                           for n, k in more))
    return combined


def sort_by_time(paths):
    """Sort blocks into recording order: bext timecode, else file name."""
    def api_key(p):
        try:
            tr = bext_time_reference(p)
        except Exception:
            tr = None
        return (0, tr, "") if tr is not None else (1, 0, os.path.basename(p))
    return sorted(paths, key=api_key)


def one_track_left(plan):
    """What to do when the camera audio holds fewer than two tracks.

    Nothing: a single recording is a special case of several, not a
    different kind of job, and it goes the same way. What falls away is
    only the multitrack production, decided where the upload happens.
    Returns 1 for the one case that cannot go on -- no camera had a
    microphone and there is no sound at all -- and None otherwise.
    """
    if not [e["audio"] for e in plan if e.get("audio")]:
        print(as_bad(T('No sound in the cameras -- nothing to work with.')))
        return 1
    return None


def names_given(args, video_paths):
    """The names --new-name gives, by file, or why they cannot be used.

    Before anything is written: a plain file name, for a camera of the
    run, one name per file, no two cameras in one file -- without case,
    as the writer and the disks compare; the window asks that too, a
    command line never passes it. Two unnamed cameras sharing a stem
    pass: named after their files, name_apart numbers them apart.
    """
    cameras = {path_key(p): p for p in video_paths}
    called = {}
    for file, name in (getattr(args, "new_name", None) or ()):
        name, shown = (name or "").strip(), os.path.basename(file)
        if path_key(file) not in cameras:
            return {}, T('--new-name names %s, which is not one of the '
                         'camera files of this run.') % shown
        if not name:
            return {}, T('The new name for %s is empty; give a plain file '
                         'name or leave --new-name out.') % shown
        sign = [c for c in "/\\:" if c in name]
        if sign:
            return {}, T('The new name "%s" for %s holds "%s", a folder or '
                         'drive separator; give a plain file name.') % (
                name, shown, sign[0])
        if name.startswith("."):
            return {}, T('The new name "%s" for %s begins with a dot, which '
                         'makes a hidden file or a folder; give a plain file '
                         'name.') % (name, shown)
        if called.get(path_key(file), name) != name:
            return {}, T('--new-name gives %s two names, "%s" and "%s"; '
                         'give each file one.') % (
                shown, called[path_key(file)], name)
        called[path_key(file)] = name
    seen = {}
    for key, path in cameras.items():
        name = called.get(key) or os.path.splitext(os.path.basename(path))[0]
        other, first = seen.setdefault(name.lower(), (key, name))
        if other != key and (key in called or other in called):
            return {}, T('Two cameras would be written as one file, %s: '
                         '%s and %s.') % (
                first + (getattr(args, "suffix", "") or "_audio") + ".mov",
                os.path.basename(cameras[other]), os.path.basename(path))
    return called, ""


def speakers_given(args, audio_paths):
    """The names --speaker-name gives, by block, or why they cannot be used.

    Before anything is written: for a recording of this run, not empty,
    and one name per file. Beside --assign it would be dropped without
    a word, since the assignment file names the rows itself, so it is
    refused there. What no switch names is guessed from the file name.
    """
    given = getattr(args, "speaker_name", None) or ()
    if given and getattr(args, "assign", None):
        return {}, T('The assignment file names the recordings here, so '
                     '--speaker-name would be dropped; give the names '
                     'there or leave --speaker-name out.')
    ours = set(path_key(p) for p in audio_paths)
    called = {}
    for file, name in given:
        name, shown = (name or "").strip(), os.path.basename(file)
        if path_key(file) not in ours:
            return {}, T('--speaker-name names %s, which is not one of the '
                         'recordings of this run.') % shown
        if not name:
            return {}, T('The speaker name for %s is empty; give a name or '
                         'leave --speaker-name out.') % shown
        if called.get(path_key(file), name) != name:
            return {}, T('--speaker-name gives %s two names, "%s" and "%s"; '
                         'give each recording one.') % (
                shown, called[path_key(file)], name)
        called[path_key(file)] = name
    return called, ""


def names_have_no_place(called, cameras, plan, audio_paths):
    """Why the names --new-name gives would go unused here, or "".

    They act where each camera is named after its file. An assignment
    file listing the cameras names them itself, and cameras alone are
    named after the tracks taken from their sound: there a name would be
    dropped without a word, so it is refused before anything is written.
    """
    if called and cameras:
        return T('The assignment file names the cameras here, so '
                 '--new-name would be dropped; give the names there or '
                 'leave --new-name out.')
    if called and not plan and not audio_paths:
        return T('With cameras only, each file is named after the tracks '
                 'taken from its sound, so --new-name would be dropped; '
                 'leave --new-name out.')
    return ""


def cameras_named_by_tracks(plan, sync=False):
    """One entry per camera, named after the tracks taken from its sound.

    Not one per track: a camera whose two channels carry two microphones
    is still one camera and writes one file, and both names go into it.
    Sync only knows nobody: there a camera keeps its own stem, and two
    cameras with one stem are told apart the way the plan tells them.
    """
    taken = set()
    return [{"video": v,
             "name": (name_apart(os.path.splitext(os.path.basename(v))[0],
                                 taken) if sync
                      else "+".join(track_name_of(e) for e in own))}
            for v, own in tracks_per_camera(plan).items()]


def show_multitrack_plan(args, audio_paths, video_paths):
    """Show the detected plan without doing anything yet."""
    step_begin("plan")
    called, complaint = names_given(args, video_paths)
    if not complaint:
        spoken, complaint = speakers_given(args, audio_paths)
    if complaint:
        print(as_bad(T('Abort: %s') % complaint))
        return 1
    # Said once, at the top: everything the log then does not show --
    # no speakers, no transcript, no cut -- was left out on purpose.
    if sync_only(args):
        print(T('Project type: Sync only -- no speakers, no transcript, '
                'no cut; the handover carries the multicam timeline '
                'alone.'))
    plan, cameras, title = [], [], ""
    if args.assign and os.path.exists(args.assign):
        try:
            with open(args.assign, encoding="utf-8") as f:
                d = json.load(f)
        except ValueError as e:
            print(T('Assignment file not readable: %s') % e)
            return 1
        if isinstance(d, dict):
            complaint = format_complaint(d)
            if complaint:
                print(as_bad(T('Abort: %s') % complaint))
                return 1
            plan = d.get("tracks_of") or []
            cameras = d.get("cameras") or []
            # What the window already had taken apart by voice. Carried
            # over rather than computed again: three minutes of the
            # graphics unit for a result that is already there.
            args._speakers_of = d.get("speakers_of") or {}
            title = d.get("production") or ""
            args.production = title
        else:
            plan = d
    complaint = names_have_no_place(called, cameras, plan, audio_paths)
    if complaint:
        print(as_bad(T('Abort: %s') % complaint))
        return 1
    named_here = not cameras
    print(as_head(T('RECOGNISED PLAN')))
    if title:
        print(T('  Production at auphonic.com:   %s') % title)
    if not plan and audio_paths:
        # A block taken out by hand is carried as such into the plan: rows
        # merge by speaker name below, and two blocks of one recorder guess the
        # same name, so grouping alone would join again what was split here.
        kept_apart = {path_key(x)
                      for x in (getattr(args, "apart", ()) or ())}
        for row, _ in group_recording_parts(audio_paths,
                                            args.no_follow_ups,
                                            getattr(args, "apart", ()),
                                            getattr(args, "together", ())):
            # The name typed for the recording, on whichever block it
            # came; the file name is only the proposal.
            typed = [spoken[path_key(b)] for b in row
                     if path_key(b) in spoken] + [guess_speaker_name(row[0])]
            plan.append({"audio": row[0], "blocks": row,
                         "speakers": typed[0],
                         "camera": "",
                         "apart": any(path_key(b) in kept_apart
                                      for b in row)})
    if any(e.get("camera_audio") for e in plan):
        # The interface sent cameras rather than audio recordings: names and
        # assignment are settled, only the audio is extracted now.
        args._camera_audio = tempfile.mkdtemp(prefix="vpm_camaudio_")
        atexit.register(shutil.rmtree, args._camera_audio, True)
        plan = extract_audio_for_plan(plan, args._camera_audio)
        if len(plan) < 2:
            stop = one_track_left(plan)
            if stop is not None:
                return stop
    elif not plan:
        # Only video files on the command line: guess the names ourselves.
        args._camera_audio = tempfile.mkdtemp(prefix="vpm_camaudio_")
        atexit.register(shutil.rmtree, args._camera_audio, True)
        plan = plan_from_camera_audio(video_paths, args._camera_audio, cameras, title)
        if len(plan) < 2:
            stop = one_track_left(plan)
            if stop is not None:
                return stop
        if not cameras:
            cameras = cameras_named_by_tracks(plan, sync_only(args))
    if named_here and video_paths:
        # One entry per video file nothing names yet (every file, or a mute one
        # no track names), by --new-name or its written stem, ending put last;
        # equal names told apart, or two handover tracks hit one written file.
        taken = {cam["name"].lower() for cam in cameras}
        have = {path_key(cam["video"]) for cam in cameras}
        cameras = cameras + [
            {"video": os.path.abspath(path),
             "name": name_apart(
                 called.get(path_key(path))
                 or os.path.splitext(os.path.basename(path))[0], taken)}
            for path in video_paths if path_key(path) not in have]
    cameras = cameras_plainly_named(cameras)
    # One name on a recording and on a voice: the window refuses it,
    # and so does the line -- merged, each turn would count twice.
    clash = PROGRAM.voices_clashing_of_run(args, plan)
    if clash:
        print(as_bad(T('Abort: %s') % PROGRAM.names_clash_said(clash)))
        return 1
    plan = merge_plan_entries(plan)
    for e in plan:
        blocks = e.get("blocks") or [e["audio"]]
        total = sum(sample_count(b) for b in blocks) / float(SR)
        target = PROGRAM.camera_shown(e["camera"]) if e.get("camera")\
            else label_of(MIX_ONLY)
        print("  %-20s %-34s %s%s"
              % (e.get("speakers") or T('unnamed'),
                 os.path.basename(blocks[0])
                 + ("  (+%s)" % number_text(len(blocks) - 1, 0)
                    if len(blocks) > 1 else ""),
                 as_hms(total), "  ->  " + target))
    combined = ByFile(
        (cam, [track_name_of(e) for e in own])
        for cam, own in tracks_per_camera(plan).items())
    multiple = {cam: v for cam, v in combined.items() if len(v) > 1}
    for cam, v in multiple.items():
        print(T('  %s gets %s tracks mixed together: %s')
              % (PROGRAM.camera_shown(cam), number_text(len(v), 0),
                 ", ".join(v)))
    if cameras:
        print(T('\n  This produces:'))
        # Named by the function the run writes by, so a camera whose own
        # stem is taken reads here under the name it really gets.
        written = {path_key(v): t for v, t in camera_targets(
            video_paths or [c["video"] for c in cameras],
            {path_key(c["video"]): c["name"] for c in cameras},
            args.out, args.suffix).items()}
        every = [track_name_of(e) for e in plan]
        # The same rule the writer follows: a recording gets a line of
        # its own only where no camera has a track at all, there is more
        # than one recording, and --no-single-tracks was not given.
        singles = ([] if any(k for k in combined) or len(every) < 2
                   or getattr(args, "no_single_tracks", False) else every)
        for cam in cameras:
            own = combined.get(cam["video"]) or []
            # How many camera tracks the file will carry: as many as the
            # camera brought, none with --no-camera-audio. The probe is
            # remembered, so the writer asks it no second time.
            try:
                heard = len(video_facts(cam["video"], args.fps,
                                        args.tc)["audio"])
            except Exception:
                heard = 1
            camera_tracks = 0 if args.no_camera_audio else heard
            print("    %s  ->  %s"
                  % (PROGRAM.camera_shown(cam["video"]),
                     os.path.basename(written.get(
                         path_key(cam["video"]), ("", cam["name"] + (
                             args.suffix or "_audio") + ".mov"))[1])))
            for idx, what in enumerate(
                    track_order_for_camera(own, every, singles,
                                           camera_tracks,
                                           args.name_camera), 1):
                # The track number names the track, counts nothing: it is
                # what the editor sees in the strip and what the writer below
                # numbers by -- plain digits, as Resolve's own stay plain.
                print(T('        Track %d: %s') % (idx, what))
    return build_common_timebase(args, plan, cameras, video_paths, title)


def multitrack_or_single(args, ap, audio_paths, video_paths):
    """Take the multitrack path, or the ordinary one where one track is left.

    How many tracks there are is not how many files there are: a camera
    carrying two clip-on microphones is two. That is measured while the
    plan is built, so the decision falls after the plan and not on a
    file count before anybody has looked.
    """
    return show_multitrack_plan(args, audio_paths, video_paths)
