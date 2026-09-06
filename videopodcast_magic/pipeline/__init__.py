# -*- coding: utf-8 -*-
"""The chain: the recordings become the finished camera files.

A piece of the program, read out of the folder beside it by beside().
It cannot import the file it was cut out of, because that file is
still being read while this one is; the program is handed in instead,
and every name this piece uses out of it is bound below, by name.
"""

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

# What the program has and this piece uses, bound once so that the
# chain reads as it did in the one file. None is missing and none is
# read late: not one of the names below is bent while the run goes on,
# so a copy taken here cannot go stale under it.

AUDIO_SUFFIXES = PROGRAM.AUDIO_SUFFIXES
AXIS_MIN_WINDOW_S = PROGRAM.AXIS_MIN_WINDOW_S
ByFile = PROGRAM.ByFile
MIX_ONLY = PROGRAM.MIX_ONLY
MIX_TRACK_NAME = PROGRAM.MIX_TRACK_NAME
SR = PROGRAM.SR
Share = PROGRAM.Share
SharedProgressBar = PROGRAM.SharedProgressBar
T = PROGRAM.T
THREAD_BUFFER = PROGRAM.THREAD_BUFFER
THREAD_SHARE = PROGRAM.THREAD_SHARE
TN = PROGRAM.TN
TRAILING_NUMBER = PROGRAM.TRAILING_NUMBER
ThreadOutput = PROGRAM.ThreadOutput
WEAK_MATCH = PROGRAM.WEAK_MATCH
_logs_atom_text = PROGRAM._logs_atom_text
align_audio_to_video = PROGRAM.align_audio_to_video
align_cameras = PROGRAM.align_cameras
align_envelopes = PROGRAM.align_envelopes
api_key_from_anywhere = PROGRAM.api_key_from_anywhere
append_ixml = PROGRAM.append_ixml
as_bad = PROGRAM.as_bad
as_data_size = PROGRAM.as_data_size
as_head = PROGRAM.as_head
as_hms = PROGRAM.as_hms
as_warn = PROGRAM.as_warn
atexit = PROGRAM.atexit
bext_time_reference = PROGRAM.bext_time_reference
build_ixml = PROGRAM.build_ixml
camera_stamp = PROGRAM.camera_stamp
camera_window_cut = PROGRAM.camera_window_cut
cannot_be_placed = PROGRAM.cannot_be_placed
channel_count = PROGRAM.channel_count
channel_facts_cached = PROGRAM.channel_facts_cached
channel_text = PROGRAM.channel_text
check_camera_metadata = PROGRAM.check_camera_metadata
check_colour_survived = PROGRAM.check_colour_survived
check_data_tracks = PROGRAM.check_data_tracks
choose_preset = PROGRAM.choose_preset
common_window = PROGRAM.common_window
copy_mov_atoms = PROGRAM.copy_mov_atoms
cross_correlate = PROGRAM.cross_correlate
decimal_text = PROGRAM.decimal_text
decode_audio = PROGRAM.decode_audio
decode_audio_tracks = PROGRAM.decode_audio_tracks
envelope = PROGRAM.envelope
ffprobe_json = PROGRAM.ffprobe_json
file_frame_rate = PROGRAM.file_frame_rate
file_timecode = PROGRAM.file_timecode
find_master_file = PROGRAM.find_master_file
finish_without_auphonic = PROGRAM.finish_without_auphonic
format_complaint = PROGRAM.format_complaint
futures = PROGRAM.futures
group_recording_parts = PROGRAM.group_recording_parts
group_text = PROGRAM.group_text
guess_camera_name = PROGRAM.guess_camera_name
guess_production_name = PROGRAM.guess_production_name
guess_speaker_name = PROGRAM.guess_speaker_name
how_many_processors = PROGRAM.how_many_processors
is_drop_frame = PROGRAM.is_drop_frame
join_with_report = PROGRAM.join_with_report
json = PROGRAM.json
kept_channels = PROGRAM.kept_channels
known_frame_rate = PROGRAM.known_frame_rate
label_of = PROGRAM.label_of
log_curve_from_atom = PROGRAM.log_curve_from_atom
lufs_does_nothing = PROGRAM.lufs_does_nothing
mix_tracks = PROGRAM.mix_tracks
mix_width = PROGRAM.mix_width
no_place_message = PROGRAM.no_place_message
normalise_loudness = PROGRAM.normalise_loudness
number_text = PROGRAM.number_text
os = PROGRAM.os
parse_time_point = PROGRAM.parse_time_point
parse_timecode = PROGRAM.parse_timecode
path_key = PROGRAM.path_key
pcm_kind = PROGRAM.pcm_kind
place_track_on_axis = PROGRAM.place_track_on_axis
recognise_speech = PROGRAM.recognise_speech
report_picture_comparison = PROGRAM.report_picture_comparison
resolve_timeline_rate = PROGRAM.resolve_timeline_rate
roles_report = PROGRAM.roles_report
run_multitrack_production = PROGRAM.run_multitrack_production
run_single_production = PROGRAM.run_single_production
safe_filename = PROGRAM.safe_filename
sample_count = PROGRAM.sample_count
separation_for_run = PROGRAM.separation_for_run
shell_quote = PROGRAM.shell_quote
show_progress = PROGRAM.show_progress
shutil = PROGRAM.shutil
similarity = PROGRAM.similarity
size_in_mb = PROGRAM.size_in_mb
speakers_for_the_cut = PROGRAM.speakers_for_the_cut
split_channels = PROGRAM.split_channels
split_target = PROGRAM.split_target
step_begin = PROGRAM.step_begin
sys = PROGRAM.sys
tempfile = PROGRAM.tempfile
threading = PROGRAM.threading
timecode_seconds = PROGRAM.timecode_seconds
timecode_string = PROGRAM.timecode_string
timeline_frame_rate = PROGRAM.timeline_frame_rate
track_order_for_camera = PROGRAM.track_order_for_camera
tracks_folder = PROGRAM.tracks_folder
tracks_to_split = PROGRAM.tracks_to_split
verify_alignment = PROGRAM.verify_alignment
verify_returned_tracks = PROGRAM.verify_returned_tracks
video_envelope = PROGRAM.video_envelope
video_facts = PROGRAM.video_facts
voice_names_report = PROGRAM.voice_names_report
wav_safe = PROGRAM.wav_safe
which_way_placed = PROGRAM.which_way_placed
who_asks = PROGRAM.who_asks
write_camera_file = PROGRAM.write_camera_file
write_cut_list = PROGRAM.write_cut_list
write_handover = PROGRAM.write_handover
write_metrics_csv = PROGRAM.write_metrics_csv
write_transcript_files = PROGRAM.write_transcript_files


# =====================================================================
#  The chain, in the order a run takes it: the camera audio out of the
#  pictures, one axis under them all, the tracks back onto the cameras.
# =====================================================================


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
          % (os.path.basename(file_path), channel_text(channels)))
    command = ["ffmpeg", "-v", "error", "-i", file_path, "-map", "0:a:0",
              "-ar", str(SR), "-c:a", unpack_kind(file_path),
              "-write_bext", "1"]
    if info.get("tc"):
        # The audio starts where the picture starts. Passing the timecode along
        # saves the alignment from guessing.
        try:
            t0 = parse_timecode(info["tc"], max(1.0, info["fps"]))
            command += ["-metadata",
                       "time_reference=%d" % int(round(t0 * SR))]
            print("  Timecode %s" % info["tc"])
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
                  % (os.path.basename(v), ex))
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
                  % (e["speakers"], os.path.basename(e["camera"])))
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
        reason, cam = name, 2
        while name in taken:
            name = "%s %d" % (reason, cam)
            cam += 1
        taken.add(name)
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
                  % (os.path.basename(v), e))
            continue
        for piece, label in camera_audio_tracks(target, name, tmpdir):
            plan.append({"audio": piece, "blocks": [piece],
                         "speakers": label, "camera": v,
                         "from_camera": v})
    show_progress(T('Camera audio'), 1.0)
    for e in plan:
        print(T('  %-24s from %s') % (e["speakers"],
                                  os.path.basename(e["camera"])))
    if len(plan) < 2:
        print(T('  Fewer than two cameras with sound -- too few for '
                'Multitrack.'))
    return plan


def clocks_on_the_axis(videos, position, tracks, ref_clip):
    """Every file besides the reference that knows the time of day.

    One entry per file that carries a timecode and whose place on the
    axis was measured: the name to say it by, the clock in seconds, and
    the place (file time = a + b * axis time). A file that was never
    placed is left out -- its clock says when it was recorded but not
    where it sits, and only the two together say what the reference's
    first frame reads.
    """
    found = []
    for v, info in videos:
        if v == ref_clip[0] or v not in position:
            continue
        when = timecode_seconds(info)
        if when is None:
            continue
        a, b, _st = position[v]
        found.append({"name": os.path.basename(v), "tc": when,
                      "a": a, "b": b})
    for track in (tracks or []):
        blocks = track.get("blocks") or []
        # The blocks were sorted by time and joined on one axis, so the
        # first one's clock is the clock of the joined recording.
        # A recorder writes no frames, so the frames of a timecode track
        # belong to the reference picture and are read at its rate.
        when = file_timecode(blocks[0], ref_clip[1]["fps"]) if blocks else None
        if when is None:
            continue
        found.append({"name": os.path.basename(blocks[0]), "tc": when,
                      "a": track["a"], "b": track["b"]})
    return found


def axis_starts_at(clocks):
    """What the reference camera's first frame reads on the clock.

    Every file that carries a timecode answers on its own: its clock
    less its own place on the axis. Nothing, where none answers.
    """
    # File time = a + b * axis time, so the file's own zero sits at
    # -a / b on the axis, and the reference's zero reads that much
    # earlier on the file's clock.
    says = sorted(float(c["tc"]) + float(c["a"]) / float(c["b"])
                  for c in clocks)
    # The median, so one clock never set right cannot move the window:
    # in one production two cameras disagreed by two seconds. It is
    # also the rule measure_time_axis ties the preview's axis by, so
    # what is marked in the player and what the run makes of it agree.
    return says[len(says) // 2] if says else None


def clip_to_time_window(args, t0, t1, ref_clip, clocks=()):
    """Apply the In point and the Out point to the measured window.

    The window lives in reference camera time. An absolute value is
    converted through a timecode; a relative one counts from the window
    start, a negative one back from the window end. *clocks* is what
    else on the axis knows the time of day, in the shape axis_starts_at
    wants -- the reference is the longest camera and need not carry a
    clock of its own.
    """
    start = getattr(args, "in_point", None)
    end = getattr(args, "out_point", None)
    if not start and not end:
        return t0, t1
    fps = max(1.0, ref_clip[1]["fps"]) if ref_clip else 30.0
    tc_ref, tc_from = None, ""
    if ref_clip and ref_clip[1].get("tc"):
        tc_ref = parse_timecode(ref_clip[1]["tc"], fps)
    elif clocks:
        # No clock of its own, but the axis hangs on the clocks around
        # it, and that is a number the alignment has already measured.
        tc_ref = axis_starts_at(clocks)
        tc_from = ", ".join(sorted(c["name"] for c in clocks))

    def convert(value_text, from_the_end):
        value, absolute = parse_time_point(value_text, fps)
        if value is None:
            return None
        if absolute:
            # Two different situations, and one message for both used to
            # name a reference camera that does not exist on the path
            # without a picture.
            if tc_ref is None and not ref_clip:
                raise RuntimeError(
                    T('%r is a Timecode, but there is no picture here and '
                      'so no camera to count it from. Then only a value '
                      'from the window start works, such as +12:30.')
                    % value_text)
            if tc_ref is None:
                raise RuntimeError(
                    T('%r is a Timecode, but the time axis hangs on no '
                      'clock: no file here carries one, the reference '
                      'camera %s included. Then only a value from the '
                      'window start works, such as +12:30.')
                    % (value_text, os.path.basename(ref_clip[0])))
            return value - tc_ref
        if value < 0:
            if not from_the_end:
                raise RuntimeError(
                    T('%r counts from the end -- that only works '
                      'for Out point.') % value_text)
            return t1 + value
        return t0 + value

    try:
        new0 = convert(start, False) if start else t0
        new1 = convert(end, True) if end else t1
    except RuntimeError as e:
        print("\n%s" % e)
        return None, None
    print(T('\n  Time window by hand:'))
    if tc_from:
        # Which clocks the axis was hung on, and what it makes the
        # reference's first frame read. Without this the two lines below
        # are a number nobody can check: the reference camera carries no
        # timecode, so a reader would look for one there and find none.
        print(T('    The reference camera carries no Timecode. The axis '
                'hangs on the clock of %s, and its first frame reads %s.')
              % (tc_from, timecode_string(tc_ref, fps)))
    if tc_ref is not None:
        # The reference camera's rate, the same one the axis runs at:
        # the two lines say back what was typed in, and at 25 a line
        # printed at 30 would name a different frame.
        print(T('    In point   %s   (Timecode %s)')
              % (as_hms(new0), timecode_string(tc_ref + new0, fps)))
        print(T('    Out point  %s   (Timecode %s)')
              % (as_hms(new1), timecode_string(tc_ref + new1, fps)))
    else:
        print(T('    In point   %s\n    Out point  %s')
              % (as_hms(new0), as_hms(new1)))
    if new1 <= new0:
        print(T('    Out point lies before In point -- that does not work.'))
        return None, None
    outside = []
    if new0 < t0 - 0.001:
        outside.append(T('In point is %s before the first frame')
                          % as_hms(t0 - new0))
    if new1 > t1 + 0.001:
        outside.append(T('Out point is %s after the last frame')
                          % as_hms(new1 - t1))
    if outside:
        print(T('    Careful: %s. There is no picture there;') % T(' and ').join(
            outside))
        print(T('    the measured window is therefore kept.'))
        new0, new1 = max(new0, t0), min(new1, t1)
    if new1 - new0 < 5:
        print(T('    The window would be only %s long -- that cannot be '
                'intended.') % as_hms(max(0, new1 - new0)))
        return None, None
    kept, measured = as_hms(new1 - new0), as_hms(t1 - t0)
    # The bracket is there to say "yours instead of the measured one".
    # Where a point was pulled back the two are the same length, and
    # "1:26:31 (instead of 1:26:31)" says nothing twice.
    print(T('    Length  %s  (instead of %s)') % (kept, measured)
          if kept != measured else T('    Length  %s') % kept)
    return new0, new1


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
                      % (name, os.path.basename(old["camera"])))
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
              % ", ".join(T('%s from %s recordings') % (n, group_text(k))
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


def show_multitrack_plan(args, audio_paths, video_paths):
    """Show the detected plan without doing anything yet."""
    step_begin("plan")
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
    print(as_head(T('RECOGNISED PLAN')))
    if title:
        print(T('  Production at auphonic.com:   %s') % title)
    if not plan and audio_paths:
        # A block taken out by hand is carried as such into the plan.
        # Grouping alone was not enough: the rows are merged by speaker
        # name further down, and two blocks of one recorder guess the
        # same name, so what was separated here was joined again there.
        kept_apart = {path_key(x)
                      for x in (getattr(args, "apart", ()) or ())}
        for row, _ in group_recording_parts(audio_paths,
                                            args.no_follow_ups,
                                            getattr(args, "apart", ()),
                                            getattr(args, "together", ())):
            plan.append({"audio": row[0], "blocks": row,
                         "speakers": guess_speaker_name(row[0]), "camera": "",
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
            # One entry per camera, not per track: a camera whose two
            # channels carry two microphones is still one camera and
            # still writes one file. Both names go into that file name.
            who = ByFile()
            for e in plan:
                who.setdefault(e["camera"], []).append(
                    e["speakers"])
            cameras = [{"video": v, "name": "%s_%s"
                        % (safe_filename(title or 'Production'),
                           "+".join(names))}
                       for v, names in who.items()]
    if not cameras and video_paths:
        # No assignment file and no names from the plan: one entry per
        # video file, named after the file plus the suffix. Without this
        # the run wrote camera files under the source's own name and no
        # handover at all, which is what the whole run is for.
        cameras = [{"video": os.path.abspath(path),
                    "name": os.path.splitext(os.path.basename(path))[0]
                            + (args.suffix or "_audio")}
                   for path in video_paths]
    plan = merge_plan_entries(plan)
    for e in plan:
        blocks = e.get("blocks") or [e["audio"]]
        total = sum(sample_count(b) for b in blocks) / float(SR)
        target = os.path.basename(e["camera"]) if e.get("camera")\
            else label_of(MIX_ONLY)
        print("  %-20s %-34s %s%s"
              % (e.get("speakers") or T('unnamed'),
                 os.path.basename(blocks[0])
                 + ("  (+%d)" % (len(blocks) - 1) if len(blocks) > 1 else ""),
                 as_hms(total), "  ->  " + target))
    combined = {}
    for e in plan:
        combined.setdefault(e.get("camera") or "", []).append(
            e.get("speakers") or "?")
    multiple = {cam: v for cam, v in combined.items() if len(v) > 1 and cam}
    for cam, v in multiple.items():
        print(T('  %s gets %s tracks mixed together: %s')
              % (os.path.basename(cam), group_text(len(v)), ", ".join(v)))
    if cameras:
        print(T('\n  This produces:'))
        every = [e.get("speakers") or "?" for e in plan]
        # The same rule the writer follows: a recording gets a line of
        # its own only where no camera has a track at all, there is more
        # than one recording, and --no-single-tracks was not given.
        singles = ([] if any(k for k in combined) or len(every) < 2
                   or getattr(args, "no_single_tracks", False) else every)
        for cam in cameras:
            own = combined.get(cam["video"]) or []
            print("    %s  ->  %s" % (os.path.basename(cam["video"]),
                                      cam["name"] + ".mov"))
            for idx, what in enumerate(
                    track_order_for_camera(own, every, singles), 1):
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


def join_the_plan(plan, tmpdir):
    """Join the blocks of every track. No camera is needed for that."""
    made = []
    for e in plan:
        blocks = e.get("blocks") or [e["audio"]]
        name = e.get("speakers") or os.path.basename(blocks[0])
        if len(blocks) > 1:
            source, join_info = join_with_report(
                blocks, os.path.join(tmpdir,
                                     "raw_%s.wav" % safe_filename(name)))
            hint = T('%s blocks') % group_text(join_info["blocks"])
        else:
            source, hint = blocks[0], ""
        made.append({"name": name, "source": source, "hint": hint,
                     "blocks": list(blocks), "camera": e.get("camera") or ""})
    return made


def join_only(args, tracks, tmpdir, title=""):
    """Join the blocks and stop: there is no picture to lay them on.

    Joining the blocks of a recording needs no camera, and one file out
    of several is a whole result.
    """
    first = tracks[0]["blocks"][0]
    folder = os.path.abspath(args.out) if args.out else os.path.dirname(
        os.path.abspath(first))
    # Measured, said, and adjusted where a target was given -- the same
    # as on any run with a picture. One gain per recording, because
    # without a picture they are not laid against each other and there
    # is no balance between them to keep.
    for track in tracks:
        try:
            gain, curve = normalise_loudness(
                [{"name": track["name"], "axis": track["source"],
                  "ready": track["source"]}], args.lufs, tmpdir, None,
                channels=channel_count(track["source"]))
        except Exception as e:
            gain, curve = 0.0, None
            print(T('  Loudness not measurable: %s') % str(e)[:60])
        if gain or curve:
            track["source"] = mix_tracks(
                [track["source"]],
                os.path.join(tmpdir, "level_%s.wav"
                             % safe_filename(track["name"])),
                gain, curve, channels=channel_count(track["source"]))
    if args.auphonic_key:
        key = api_key_from_anywhere(args)
        preset, presetname = choose_preset(
            key, args.auphonic_preset, len(tracks) > 1, lufs=args.lufs,
            anyway=getattr(args, "anyway", False))
        for track in tracks:
            track["axis"] = track["source"]
            track["done"] = run_single_production(
                track["source"], preset, presetname, key, folder,
                args.auphonic_wait, args.dry_run, title or track["name"])
        if args.dry_run:
            return 0
        # What came back is held against what went up, the same as on a
        # run with a picture. The service can prepend material and
        # change the length, and nothing else here would notice.
        longest = max(sample_count(t["source"]) for t in tracks) / float(SR)
        return 0 if verify_returned_tracks(tracks, longest, tmpdir) else 1
    if len(tracks) == 1 and len(tracks[0]["blocks"]) < 2:
        print(T('Only one audio file and no picture -- nothing to do.'))
        return 0
    os.makedirs(folder, exist_ok=True)
    written = []
    for track in tracks:
        stem = os.path.splitext(os.path.basename(track["blocks"][0]))[0]
        counted = TRAILING_NUMBER.match(stem)
        if counted:
            stem = counted.group(1).rstrip("_-. ")
        target = os.path.join(folder, stem + "_joined.wav")
        if args.dry_run:
            print(T('Would write: %s') % target)
            continue
        shell_quote(["ffmpeg", "-v", "error", "-i", track["source"],
                     "-c:a", "copy", "-y", target])
        written.append(target)
    if written:
        print(as_head(T('RESULT')))
        for target in written:
            print("  %s  (%s)"
                  % (target, as_hms(sample_count(target) / float(SR))))
    return 0


def measure_tracks_against_each_other(tracks):
    """Put every track on the time axis of the longest one.

    The longest recording is the reference for the same reason the
    longest camera is: it overlaps most with the others. Returns the
    tracks that found a place, each carrying a and b.
    """
    reference = max(tracks, key=lambda t: sample_count(t["source"]))
    length = sample_count(reference["source"]) / float(SR)
    print(T('  Reference: %s (%s, longest running time)')
          % (reference["name"], as_hms(length)))
    placed = []
    for track in tracks:
        if track is reference:
            track["a"], track["b"] = 0.0, 1.0
            placed.append(track)
            continue
        try:
            # The same measurement as against a camera, which reads the
            # audio of whatever it is handed and never the picture. A
            # second way of aligning would be a second answer to one
            # question.
            a, b, st = align_audio_to_video(
                track["source"], reference["source"], 0,
                sample_points=int(max(20, min(120, length / 30.0))),
                distance_s=30.0)
        except Exception as e:
            print(T('  %-20s cannot be aligned: %s') % (track["name"], e))
            continue
        if st.get("unplaceable"):
            print(as_bad("  " + no_place_message(track["name"])))
            continue
        track["a"], track["b"] = a, b
        placed.append(track)
        # The same note as on the path with a picture: which way placed
        # it. Without it a track put there by phase shows +0.00 ppm and
        # nothing else, and that reads as a drift measured at zero.
        track["hint"] = which_way_placed(st, track.get("hint") or "")
        print(T('  %-20s offset %s, clock drift %s ppm (+/- %s), '
                'residual spread %s ms, %s of %s points%s')
              % (track["name"], as_hms(a),
                 number_text(st.get("ppm", 0.0), 2, plus=True),
                 number_text(st.get("ppm_error", 0.0), 2),
                 number_text(st.get("spread_ms", 0.0)),
                 group_text(st.get("points", 0)),
                 group_text(st.get("candidates", 0)),
                 "  [" + track["hint"] + "]" if track.get("hint") else ""))
    return placed


def align_tracks_only(args, tracks, tmpdir, title=""):
    """Lay the tracks against each other where there is no picture.

    Equally long and with the same start point, which is what a
    multitrack production needs. The window holds everything any track
    heard: a silent edge costs less than a recording cut short.
    """
    step_begin("time base")
    print(as_head(T('\nMEASURING THE TIME AXIS')))
    print(T('  No picture: the tracks are laid against each other.'))
    placed = measure_tracks_against_each_other(tracks)
    if len(placed) < 2:
        print(T('\nOnly one track found a place -- there is nothing left '
                'to lay it against.'))
        return 1
    areas = [((0.0 - t["a"]) / t["b"],
              (sample_count(t["source"]) / float(SR) - t["a"]) / t["b"])
             for t in placed]
    first = min(b0 for b0, _ in areas)
    last = max(b1 for _, b1 in areas)
    # Zero is the start of the window, not the reference: a recording
    # that began earlier would otherwise stand at a negative time, and
    # that is nobody's time.
    for track, (b0, b1) in zip(placed, areas):
        track["a"] = track["a"] + track["b"] * first
        track["silence_head"], track["silence_tail"] = b0 - first, last - b1
    print(T('  Window:              %s -- everything any track heard')
          % as_hms(last - first))
    for track in placed:
        if max(track["silence_head"], track["silence_tail"]) <= 0.25:
            continue
        print(T('    %s: silence for %s at the front and %s at the back')
              % (track["name"], as_hms(track["silence_head"]),
                 as_hms(track["silence_tail"])))
    t0, t1 = clip_to_time_window(args, 0.0, last - first, None)
    if t0 is None:
        return 1
    folder = os.path.abspath(args.out) if args.out else os.path.dirname(
        os.path.abspath(placed[0]["blocks"][0]))
    if lufs_does_nothing(args, ()):
        print(T('  --lufs does nothing here: the tracks leave as they '
                'were recorded, and the loudness is set where they are '
                'mixed.'))
    if not args.dry_run:
        os.makedirs(folder, exist_ok=True)
    print(as_head(T('\nWRITING TRACKS TO THE AXIS')))
    for track in placed:
        target = os.path.join(tmpdir if args.dry_run else folder,
                              "%s_aligned.wav" % safe_filename(track["name"]))
        track["drift"] = (not args.no_drift
                          and abs(track["b"] - 1.0) > 1e-7)
        show_progress(track["name"], 0.0)
        place_track_on_axis(track["source"], target, track["a"], track["b"],
                            t0, t1, track["drift"])
        show_progress(track["name"], 1.0)
        print()
        track["axis"] = target
        print("    %s, %s" % (as_hms(sample_count(target) / float(SR)),
                              as_data_size(size_in_mb(target))))
    verify_alignment(placed, t0, t1, drift_allowed=not args.no_drift)
    if args.auphonic_key and not getattr(args, "without_auphonic", False):
        stop = send_aligned_tracks(args, placed, folder, tmpdir, t1 - t0,
                                   title)
        if stop is not None:
            return stop
    if args.dry_run:
        print(T('\n  (measuring only: nothing written)'))
        return 0
    print(as_head(T('RESULT')))
    for track in placed:
        print("  %s  (%s)" % (track["axis"],
                              as_hms(sample_count(track["axis"])
                                     / float(SR))))
    return 0


def send_aligned_tracks(args, tracks, folder, tmpdir, window, title=""):
    """Send the aligned tracks up as one multitrack production.

    Returns a return code where the run is over, and None where it goes
    on. Nothing leaves this machine unless a key was given: that is what
    asking for it looks like on the command line.
    """
    key = api_key_from_anywhere(args)
    try:
        preset, _name = choose_preset(key, args.auphonic_preset, True,
                                      lufs=args.lufs,
                                      anyway=getattr(args, "anyway", False))
    except Exception as e:
        print(T('\nNo preset chosen: %s') % e)
        return 1
    try:
        done = run_multitrack_production(
            key, preset, title or 'Production', tracks, folder,
            args.auphonic_wait, args.dry_run, args.auphonic_resume)
    except Exception as e:
        print(as_bad(T('Processing failed: %s') % e))
        return 1
    if args.dry_run:
        return None
    for track in tracks:
        track["done"] = done.get(track["name"])
    missing = [t["name"] for t in tracks if not t.get("done")]
    if missing:
        print(T('\nEnded without a result: %s') % ", ".join(missing))
        return 1
    return None if verify_returned_tracks(tracks, window, tmpdir) else 1


def build_common_timebase(args, plan, cameras, video_paths, title=""):
    """Put all audio tracks on one common time axis.

    Equally long files with the same start point -- what Auphonic
    requires, and what makes crosstalk removal worth anything.
    """
    step_begin("time base")
    videos = []
    for v in video_paths:
        v = os.path.abspath(v)
        try:
            info = video_facts(v, args.fps, args.tc)
        except Exception as e:
            print(T('  %s: %s, skipped') % (os.path.basename(v), e))
            continue
        if not info["audio"]:
            print(T('  %s has no camera sound -- without it nothing can be '
                    'aligned') % os.path.basename(v))
            continue
        if known_frame_rate(file_frame_rate(info)) is None:
            # Said, not refused: the Timeline takes a rate Resolve has
            # and the file is converted into it. Which rate that is says
            # the note below, where every camera has been read.
            print(T('  %s runs at %s frames/s, a rate Resolve has no '
                    'Timeline for -- it is converted, not left out')
                  % (os.path.basename(v),
                     decimal_text("%.3f" % file_frame_rate(info))))
        videos.append((v, info))
    if videos and not getattr(args, "production", ""):
        # The same name the ordinary path gives a production: the folder
        # the material sits in. Without it two jobs from two shoots
        # wrote the same handover and the second took the first's place.
        args.production = guess_production_name(videos[0][0])
    if not videos:
        if video_paths:
            print(T('\nNo usable video file -- without camera audio there '
                    'is no common time axis.'))
            return 1
        if args.multitrack and len(plan) < 2:
            # Multitrack means one track per voice. Joining what is
            # left would glue two people into one file, so it is not
            # even begun.
            print(T('\nOnly one track is left once the blocks are joined, '
                    'and multitrack needs one per voice. Where two people '
                    'were taken for one recording, --apart keeps a block '
                    'out of it.'))
            return 1
        tmpdir = tempfile.mkdtemp(prefix="vpm_mt_")
        atexit.register(shutil.rmtree, tmpdir, True)
        made = join_the_plan(plan, tmpdir)
        if args.multitrack:
            # Several separate voices and no picture: they are laid
            # against each other instead of against a camera.
            return align_tracks_only(args, made, tmpdir, title)
        # No picture and nobody asked for multitrack: the blocks of one
        # recording become one file, and that is the whole job.
        return join_only(args, made, tmpdir, title)

    # The nominal rates from the container are compared. The measured ones
    # differ by a few ten-thousandths on every camera; no editor goes by that,
    # and a warning about it would be a false alarm every time.
    rates = sorted({round(i.get("nominal") or i["fps"], 3) for _, i in videos})
    sizes = sorted({"%sx%s" % ((i["video"] or {}).get("width"),
                                  (i["video"] or {}).get("height"))
                       for _, i in videos})
    if len(rates) > 1:
        print(as_head(T('\nDIFFERENT FRAME RATES: %s')
                      % ", ".join("%.3f" % r for r in rates)))
        print(T('  The Timeline gets %s: the highest of them, or the '
                'next rate Resolve\n  has above it. Converted upwards '
                'Resolve repeats frames, downwards it\n  throws them '
                'away. Every camera keeps its own rate, and the cut '
                'counts\n  in that one.')
              % decimal_text("%g" % resolve_timeline_rate(
                  timeline_frame_rate(args, videos, None))))
    if len(sizes) > 1:
        print(as_head(T('\nDIFFERENT FRAME SIZES: %s') % ", ".join(sizes)))
        print(T('  Of no consequence for the sound.'))

    print(as_head(T('\nMEASURING THE TIME AXIS')))
    ref_clip, position = align_cameras(videos)
    print(T('  Reference: %s (%s, longest running time)')
          % (os.path.basename(ref_clip[0]), as_hms(ref_clip[1]["duration"])))
    for v, info in videos:
        if v == ref_clip[0]:
            continue
        if v not in position:
            continue
        a, b, st = position[v]
        print(T('  %-20s offset %s, clock drift %s ppm (+/- %s), '
                'residual spread %s ms, %s of %s points')
              % (os.path.basename(v), as_hms(a),
                 number_text(st.get("ppm", 0.0), 2, plus=True),
                 number_text(st.get("ppm_error", 0.0), 2),
                 number_text(st.get("spread_ms", 0.0)),
                 group_text(st.get("points", 0)),
                 group_text(st.get("candidates", 0))))

    tmpdir = tempfile.mkdtemp(prefix="vpm_mt_")
    # A dozen paths leave this function before the folder is removed at the
    # end; without this a failed run keeps gigabytes of WAV.
    atexit.register(shutil.rmtree, tmpdir, True)
    joined = join_the_plan(plan, tmpdir)
    tracks = []
    # The same rule the cameras follow: where every way of measuring
    # came up empty and no clock places it either, a recording is
    # refused rather than laid down somewhere -- laid down somewhere it
    # looks exactly like one that fits.
    camera_clocks = [timecode_seconds(i) for _v, i in videos]
    for e, made in zip(plan, joined):
        blocks, name = made["blocks"], made["name"]
        source, hint = made["source"], made["hint"]
        try:
            a, b, st = align_audio_to_video(source, ref_clip[0], 0,
                                  sample_points=int(max(20, min(120,
                                      ref_clip[1]["duration"] / 30.0))),
                                  distance_s=30.0)
        except Exception as ex:
            print(T('  %-20s cannot be aligned: %s') % (name, ex))
            continue
        hint = which_way_placed(st, hint)
        if cannot_be_placed(st, file_timecode(blocks[0]) if blocks else None,
                            camera_clocks):
            print(as_bad("  " + no_place_message(name)))
            continue
        tracks.append({"name": name, "source": source, "a": a, "b": b,
                       "st": st, "camera": e.get("camera") or "",
                       # Which recording the sound came out of, kept
                       # apart from the camera the speaker is on: a
                       # camera's audio is extracted into a file of its
                       # own, and only this still names the recording.
                       "from_camera": e.get("from_camera") or "",
                       "blocks": list(blocks), "hint": hint})
        print(T('  %-20s offset %s, clock drift %s ppm (+/- %s), '
                'residual spread %s ms, %s of %s points%s')
              % (name, as_hms(a),
                 number_text(st.get("ppm", 0.0), 2, plus=True),
                 number_text(st.get("ppm_error", 0.0), 2),
                 number_text(st.get("spread_ms", 0.0)),
                 group_text(st.get("points", 0)),
                 group_text(st.get("candidates", 0)),
                 "  [" + hint + "]" if hint else ""))
    if not tracks:
        print(T('\nNo audio track could be aligned -- there is nothing to '
                'put on the axis.'))
        return 1

    # Window: what every camera saw, limited to what there is audio for.
    # Anything outside would be uploaded silence.
    camera_areas = []
    for v, info in videos:
        if v not in position:
            continue
        a, b, _ = position[v]
        camera_areas.append(((0.0 - a) / b, (info["duration"] - a) / b,
                             os.path.basename(v)))
    audio_areas = []
    for track in tracks:
        n = sample_count(track["source"]) / float(SR)
        audio_areas.append(((0.0 - track["a"]) / track["b"],
                             (n - track["a"]) / track["b"]))
    # The window comes from the cameras alone: what has no picture needs no
    # audio. Where audio is missing it is padded with silence -- a silent
    # stretch beats a shifted one.
    t0, late, t1, early = common_window(camera_areas)
    for track, (b0, b1) in zip(tracks, audio_areas):
        missing_front, missing_back = max(0.0, b0 - t0), max(0.0, t1 - b1)
        # Report only what is really missing inside the chosen window: a camera
        # running before the recorder was switched on is the normal case and
        # irrelevant to the cut.
        track["missing_head"], track["missing_tail"] = missing_front, missing_back
        # And the other way round: what the recording has outside the
        # window and therefore loses. Not the same question, and it is
        # the one somebody asks when the episode comes out shorter than
        # the recording.
        track["dropped_head"], track["dropped_tail"] = (max(0.0, t0 - b0),
                                                        max(0.0, b1 - t1))

    # Not a length in seconds. What decides is how much the alignment
    # could see: it takes a sample point every couple of seconds, and a
    # window holding none of them is the one that says nothing. One rule
    # for both paths, and the number goes into the message to be checked.
    seen = min([st.get("points", 0) for v, (_a, _b, st) in position.items()
                if v != ref_clip[0]] or [0])
    if t1 - t0 <= 0 or (seen == 0 and t1 - t0 < AXIS_MIN_WINDOW_S):
        print(T('\nSound and picture have only %s in common, and the '
                'alignment found %s sample points in it. That is too '
                'little to place anything on.')
              % (as_hms(max(0, t1 - t0)), group_text(seen)))
        return 1
    print(T('  Common window:       %s to %s (%s)')
          % (as_hms(t0), as_hms(t1), as_hms(t1 - t0)))
    # Name the two cameras that decide it. Without this the window is a
    # number nobody can check, and the question "why is my episode
    # shorter than the material" has no answer in the log.
    print(T('    it begins with %s and ends with %s -- the stretch every '
            'camera saw')
          % (late, early))
    # What falls away, said out loud: the numbers were computed above
    # and printed nowhere, so a run that dropped eight seconds looked
    # like one that dropped nothing.
    for track in tracks:
        front, back = track["dropped_head"], track["dropped_tail"]
        if front <= 0.25 and back <= 0.25:
            continue
        print(T('    %s: %s at the front and %s at the back have no '
                'picture and are left out')
              % (track["name"], as_hms(front), as_hms(back)))
    # Remember the measured window: already processed tracks come from a run
    # without In point and Out point and are therefore exactly that long.
    full0, full1 = t0, t1
    t0, t1 = clip_to_time_window(args, t0, t1, ref_clip,
                                 clocks_on_the_axis(videos, position, tracks,
                                                    ref_clip))
    if t0 is None:
        return 1
    # Only count now: what lies before In point is not missing. Where the
    # window covers only stretches that have audio, nothing appears here -- a
    # message about something that is not missing is noise.
    names = [track["name"] for track in tracks]
    starts = [b0 for b0, _ in audio_areas]
    ends = [b1 for _, b1 in audio_areas]

    def silence_report(missing, points, shape):
        """Report one side, front and back separately.

        Where all tracks are affected equally, one line for the worst case is
        enough. Only a track that stands out is named.
        """
        if max(missing) <= 1:
            return
        def sentence(how_much, point):
            return (T('Missing audio %s filled with silence%s')
                    % (shape % as_hms(point),
                       T(' -- an In or Out point saves the upload')
                       if how_much > 30 else ""))
        if max(missing) - min(missing) < 15:
            print("  %s" % sentence(max(missing), points[missing.index(max(missing))]))
            return
        for name, how_much, point in zip(names, missing, points):
            if how_much > 1:
                print("  %-20s %s" % (name, sentence(how_much, point)))

    silence_report([max(0.0, b - t0) for b in starts], starts, T('up to %s'))
    silence_report([max(0.0, t1 - b) for b in ends], ends,
                   T('from %s'))

    print(as_head(T('\nWRITING TRACKS TO THE AXIS')))
    for track in tracks:
        target = os.path.join(tmpdir, "axis_%s.wav" % safe_filename(track["name"]))
        drift = not args.no_drift and abs(track["b"] - 1.0) > 1e-7
        show_progress("%s" % track["name"], 0.0)
        place_track_on_axis(track["source"], target, track["a"], track["b"], t0, t1, drift)
        show_progress("%s" % track["name"], 1.0)
        print()
        track["axis"] = target
        track["drift"] = drift
        clock_drift = (track["b"] - 1.0) * 1e6
        print("    %s, %s%s" % (as_hms(sample_count(target) / float(SR)),
                                as_data_size(size_in_mb(target)),
                                T(', clock drift %s ppm taken out')
                                % number_text(clock_drift, 1, plus=True)
                                if drift else T(', clock drift left in')))
    verify_alignment(tracks, t0, t1,
                     drift_allowed=not getattr(args, "no_drift", False))

    # Who speaks when, before anything is uploaded and before the audio
    # is processed: the axis stands now, so a separation can be placed
    # on it -- and only on the cameras that have a place, as in the
    # window: the segments of a file that sits nowhere land nowhere.
    args._speakers = separation_for_run(
        args, tracks, position, t0, t1,
        [ref_clip[0]] + [v for v, _e in videos
                         if v != ref_clip[0] and v in position])

    #--------------------------------------------------- Processing
    # --auphonic-done first, and on purpose. It names a folder: an
    # instruction about this run, not a mode. Read the other way round
    # the folder is never looked at and the run mixes the raw recordings.
    if getattr(args, "without_auphonic", False) and args.auphonic_done:
        print(as_warn(T('  --without-auphonic and --auphonic-done were '
                        'both given. The finished tracks win: there is '
                        'nothing left to send anywhere.')))
    if getattr(args, "without_auphonic", False) and not args.auphonic_done:
        return finish_without_auphonic(args, tracks, cameras, videos, tmpdir,
                                       position, t0, t1, ref_clip)
    if args.auphonic_done:
        # Already processed: the files are there. Saves a second upload and,
        # more to the point, the credit.
        folder = os.path.abspath(args.auphonic_done)
        print(as_head(T('\nALREADY PROCESSED')))
        print(T('  From %s') % folder)
        existing = [f for f in os.listdir(folder)
                     if os.path.splitext(f)[1].lower() in AUDIO_SUFFIXES]
        window = t1 - t0                       # what this run needs
        measured = full1 - full0        # the window without In point/Out point
        trimmed = abs(window - measured) > 0.001
        # Trimming leaves slack at both ends, so nothing is lost even where a
        # jingle was prepended. The return check finds the exact position
        # anyway and trims to the sample.
        MARGIN = 30.0
        shift = t0 - full0
        bad = []
        for track in tracks:
            best = max(existing, key=lambda f: similarity(
                track["name"], os.path.splitext(f)[0])) if existing else None
            quality = similarity(track["name"],
                             os.path.splitext(best)[0]) if best else 0.0
            if not best or quality < 0.6:
                print(T('    %-20s no file with a matching name') % track["name"])
                bad.append(track["name"])
                continue
            file_path = os.path.join(folder, best)
            length = sample_count(file_path) / float(SR)
            # The length may differ by a jingle but not by minutes, or
            # the file belongs to a different run. Two lengths qualify:
            # this run's window, and the measured one without In and Out
            # point, which is longer and gets trimmed.
            if abs(length - window) <= 60:
                track["done"] = file_path
                existing.remove(best)
                print(T('    %-20s <- %s  (%s, name similarity %s)')
                      % (track["name"], best, as_hms(length),
                         decimal_text("%.2f" % quality)))
                continue
            if trimmed and abs(length - measured) <= 60:
                # A prepended jingle lengthens the file; everything sits
                # further back by the same amount.
                front = shift + max(0.0, length - measured)
                target = os.path.join(tmpdir,
                                    "window_%s.wav" % safe_filename(track["name"]))
                place_track_on_axis(file_path, target, front - MARGIN, 1.0, 0.0,
                               window + 2 * MARGIN, drift=False)
                track["done"] = target
                track["edge"] = MARGIN
                existing.remove(best)
                print(T('    %-20s <- %s  (%s, trimmed to the time window, '
                        'name similarity %s)')
                      % (track["name"], best, as_hms(length),
                         decimal_text("%.2f" % quality)))
                continue
            print(T('    %-20s <- %s  BUT %s -- neither the time window '
                    '(%s) nor the\n    %-20s    whole measured range (%s). '
                    'This belongs to another run.')
                  % (track["name"], best, as_hms(length), as_hms(window), "",
                     as_hms(measured)))
            bad.append(track["name"])
        if bad:
            print(T('\n  Not usable: %s') % ", ".join(bad))
            print(T('  The files in the folder must be named after the '
                    'speakers and belong\n  to this run. Without the folder '
                    'it goes through auphonic.com again.'))
            return 1
        if args.dry_run:
            print(T('\n  (measuring only: nothing written)'))
            return 0
        if not verify_returned_tracks(tracks, t1 - t0, tmpdir):
            return 1
        gain, curve = normalise_loudness(
            tracks, args.lufs, tmpdir,
            find_master_file(folder, args.out, os.path.dirname(video_paths[0])),
            channels=mix_width(tracks))
        return distribute_tracks_to_cameras(
            args, tracks, cameras, videos, tmpdir, gain, position, t0,
            ref_clip, t1, curve)

    if args.dry_run and not args.auphonic_key:
        print(T('\n  (measuring only: without an API key it stops here)'))
        return 0
    key = api_key_from_anywhere(args)
    # The one place where a single recording really needs something
    # else. Only auphonic.com has two kinds of production, and a
    # multitrack preset holding one track is not what anybody wants, so
    # the preset follows the count and so does the production.
    alone = len(tracks) < 2
    try:
        preset, presetname = choose_preset(
            key, args.auphonic_preset, not alone, lufs=args.lufs,
            anyway=getattr(args, "anyway", False))
    except Exception as e:
        print(T('\nNo preset chosen: %s') % e)
        return 1
    folder = os.path.abspath(args.out) if args.out else os.path.dirname(
        os.path.abspath(video_paths[0]))
    print()
    try:
        if alone:
            one = run_single_production(
                tracks[0]["axis"], preset, presetname, key, folder,
                args.auphonic_wait, args.dry_run, title or 'Production')
            done = {tracks[0]["name"]: one} if one else {}
        else:
            done = run_multitrack_production(
                key, preset, title or 'Production', tracks, folder,
                args.auphonic_wait, args.dry_run, args.auphonic_resume)
    except Exception as e:
        print(as_bad(T('Processing failed: %s') % e))
        return 1
    for track in tracks:
        track["done"] = done.get(track["name"])
    missing = [track["name"] for track in tracks if not track.get("done")]
    if missing and not args.dry_run:
        print(T('\nEnded without a result: %s') % ", ".join(missing))
        return 1

    if args.dry_run:
        print(T('\n  (measuring only: nothing written)'))
        return 0

    if not verify_returned_tracks(tracks, t1 - t0, tmpdir):
        return 1
    gain, curve = normalise_loudness(
        tracks, args.lufs, tmpdir,
        find_master_file(folder, args.out, os.path.dirname(video_paths[0])),
        channels=mix_width(tracks))
    return distribute_tracks_to_cameras(
        args, tracks, cameras, videos, tmpdir, gain, position, t0, ref_clip,
        t1, curve=curve)


def check_written_file(target, items, n_camera, args, fps):
    """Measure in the finished file whether the new audio sits on the picture.

    Compared against the camera track using the overall mix, which
    carries the same voices as the camera microphone. A de-bled single
    track will not do: the other speakers are missing from it.
    """
    if args.no_camera_audio or not n_camera:
        return
    index_number = next((i for i, (name, _) in enumerate(items)
                   if name.startswith(MIX_TRACK_NAME)), 0)
    try:
        HOP, rate = 5.0, 4000
        duration = float(ffprobe_json(target).get("format", {}).get("duration") or 0)
        fresh, cam = decode_audio_tracks(
            target, rate, duration,
            T('Check: %s and camera track') % items[index_number][0],
            [index_number, len(items)])
        if not len(fresh) or not len(cam):
            print(T('  Check:           one of the two tracks is not in the '
                    'written file, so nothing was measured.'))
            return
        k, g = cross_correlate(envelope(cam, HOP, rate),
                               envelope(fresh, HOP, rate))
    except Exception as e:
        print(T('  Check:           not possible (%s)') % e)
        return
    # Whether the number means anything at all. Where the new track is
    # mostly silence there is nothing to line up against and the
    # arithmetic answers all the same. A check that cries wolf is worse
    # than none, because it is read as evidence.
    if g < WEAK_MATCH:
        print(T('  Check:           the two tracks cannot be compared '
                '(match %s, %s is the floor). This says nothing '
                'about the timing.')
              % (decimal_text("%.2f" % g), decimal_text("%.2f" % WEAK_MATCH)))
        return
    ms = k * HOP
    off = abs(ms) > 1000.0 / fps
    line = (T('  Check:           %s against the camera track %s ms '
              '(match %s)%s')
            % (items[index_number][0], number_text(ms, 0, plus=True),
               decimal_text("%.2f" % g),
               T('   Caution: more than one frame') if off else ""))
    print(as_warn(line) if off else line)


def finish_camera_file(source, info, target, items, args, fps):
    """Everything that happens to a camera file once it is written.

    The colour, the camera's own QuickTime keys, its metadata, and the
    measurement of whether the new audio sits on the picture. Four
    things in a fixed order, the same on both paths.
    """
    check_colour_survived(source, target)
    # ffmpeg drops what it does not know. For iPhone recordings "logs"
    # holds the recording curve, which is how Resolve recognises Apple
    # Log. It is copied byte for byte from the source.
    try:
        after = copy_mov_atoms(source, target)
    except Exception as e:
        after = []
        print(T('  Camera atoms:    cannot be added (%s)') % str(e)[:60])
    if after:
        print(T('  Camera atoms:    %s added -- %s')
              % (", ".join(after),
                 log_curve_from_atom(_logs_atom_text(target)) or T('no text')))
    check_camera_metadata(source, target)
    check_data_tracks(source, target)
    check_written_file(target, items, len(info["audio"]), args, fps)


def distribute_tracks_to_cameras(args, tracks, cameras, videos, tmpdir, gain,
              position, t0, ref_clip=None, t1=None, curve=None,
              segment_list=None):
    """Place the processed tracks onto the cameras.

    Without *segment_list* the speakers are worked out here: the tracks
    from auphonic.com are cleaner to measure than the raw ones.
    """
    step_begin("cameras")
    if segment_list is None:
        step_begin("speakers")
        segment_list = speakers_for_the_cut(args, tracks)
    names_every = [track["name"] for track in tracks]
    after_camera = ByFile()
    for track in tracks:
        if track.get("camera"):
            after_camera.setdefault(track["camera"], []).append(track)

    track_names = ByFile()    # output file -> names of its audio tracks
    offsets = ByFile()        # output file -> measured offset in seconds
    print(as_head(T('\nMIXING')))
    # Mixes of several tracks go out in two channels, single tracks in
    # as many as they were recorded with: the mix is what is delivered
    # and measured, the single track what is worked with in the edit.
    # One recording is the exception -- nothing to mix, nothing widened.
    wide = mix_width(tracks)
    full_mix = mix_tracks([track["ready"] for track in tracks],
                        os.path.join(tmpdir, "mix_full.wav"), gain,
                        curve, channels=wide)
    print(TN(wide, '  Full-Mix from %s tracks, %s channel',
             '  Full-Mix from %s tracks, %s channels')
          % (group_text(len(tracks)), group_text(wide)))

    # What is said and when, out of the finished mix. It runs beside the
    # cameras rather than in front of them: the words are needed only
    # when the cut is built at the end, and without them the wide shot
    # looks for the longest pause instead of the end of a sentence.
    heard = {}

    def listen_to_the_mix():
        """Write down the words of the mix, in a thread of its own."""
        words, _way = recognise_speech(
            full_mix, getattr(args, "speech_language", "") or "")
        heard["words"] = words or []

    listening = None
    if not getattr(args, "no_speech_recognition", False):
        listening = threading.Thread(target=listen_to_the_mix, daemon=True)
        listening.start()

    def heard_words():
        """Wait for the recognition and return what it heard."""
        if listening is not None:
            listening.join()
        return heard.get("words") or []

    single, in_stereo = {}, []
    for track in tracks:
        single[track["name"]] = mix_tracks(
            [track["ready"]],
            os.path.join(tmpdir, "single_%s.wav" % safe_filename(track["name"])),
            gain, curve)
        if kept_channels(single[track["name"]]) == 2:
            in_stereo.append(track["name"])
    if in_stereo:
        print(TN(len(in_stereo), '  %s stays in two channels',
                 '  %s stay in two channels') % ", ".join(in_stereo))
    # Filled from the keys of a ByFile and read back under abspath, so
    # it is one too. A plain dict here loses what the type settles: on
    # Windows the two spellings differ, the lookup raises, and every
    # camera with a track assigned goes unwritten without a word.
    camera_mix = ByFile()
    for file_path, own in after_camera.items():
        camera_mix[file_path] = mix_tracks(
            [track["ready"] for track in own],
            os.path.join(tmpdir, "mix_%s.wav"
                         % safe_filename(os.path.basename(file_path))), gain,
            curve, channels=mix_width(own))
        print(T('  %s: %s mixed together')
              % (os.path.basename(file_path),
                 " + ".join(track["name"] for track in own)))

    # Through path_key, both sides: a camera whose path arrives in
    # another shape than the same file in the video list loses the name
    # given here, writes itself under the bare file name, and then
    # misses its measured offset, which is kept under the file written.
    output_name = {path_key(cam["video"]): cam["name"] for cam in cameras}
    # The target names are settled before the threads start. Without a name
    # of its own a camera would write over an original -- its own or another
    # camera's, which a second thread may be reading at that moment -- and
    # two cameras with the same file name would write the same file at once.
    output_path, taken = {}, set()
    sources = set(os.path.abspath(_v).lower() for _v, _i in videos)
    for _v, _info in videos:
        _v = os.path.abspath(_v)
        stem = output_name.get(path_key(_v)) or os.path.splitext(
            os.path.basename(_v))[0]
        outdir = os.path.abspath(args.out) if args.out else os.path.dirname(_v)
        target = os.path.join(outdir, stem + ".mov")
        count = 1
        while target.lower() in sources or target.lower() in taken:
            count += 1
            tail = args.suffix or "_audio"
            target = os.path.join(outdir, "%s%s%s.mov"
                                  % (stem, tail,
                                     "" if count == 2 else "_%d" % count))
        taken.add(target.lower())
        output_path[_v] = (outdir, target)
    results, error = [], 0
    lengths = ByFile()    # output file -> running time delivered
    # An In or Out point is what makes the cameras carry a stretch
    # rather than the whole shoot. Without one they stay as they were,
    # so a run that sets no window writes exactly what it wrote before.
    window_s = (t1 - t0 if t1 is not None
                and ((getattr(args, "in_point", None) or "").strip()
                     or (getattr(args, "out_point", None) or "").strip())
                else None)
    # Programme time on the wall clock: the reference camera's clock
    # plus where the window starts. Every stamp is measured from here,
    # so they agree -- off each camera's own clock they did not, by
    # however much those disagreed.
    tc_start = None
    if ref_clip and ref_clip[1].get("tc") and t0 is not None:
        tc_start = parse_timecode(
            ref_clip[1]["tc"], max(1.0, ref_clip[1]["fps"])) + t0

    def one_camera(v, info, share):
        """Finish one camera: measure, write, verify.

        Runs in its own thread. Everything printed here collects in that
        thread's buffer and comes out in one piece once the file is
        done; progress goes to the shared bar instead.
        """
        v = os.path.abspath(v)
        own = after_camera.get(v, [])
        print(as_head(T('\nPROCESSING: %s') % os.path.basename(v)))
        items = []
        if own:
            items.append(('Mix ' + " + ".join(track["name"] for track in own)
                          if len(own) > 1 else own[0]["name"],
                          camera_mix[v]))
            if len(own) > 1:
                for track in own:
                    items.append((track["name"], single[track["name"]]))
            if set(track["name"] for track in own) != set(names_every):
                items.append((MIX_TRACK_NAME, full_mix))
        else:
            items.append((MIX_TRACK_NAME, full_mix))
            # And the recordings the mix was made of, each on a line of
            # its own, so the edit can reach one voice without importing
            # anything else. Only where no track has a camera at all --
            # with an assignment the wide shot gets the mix and nothing else.
            if (not after_camera and len(tracks) > 1
                    and not getattr(args, "no_single_tracks", False)):
                for track in tracks:
                    items.append((track["name"], single[track["name"]]))
        # Where the camera sits on the axis is already known from
        # building the time axis. Repeating it against a de-bled speaker
        # track would be worse: one speaker is left on it while the
        # camera microphone hears them all.
        if v not in position:
            print(T('  This camera could not be placed -- skipped'))
            return None
        a_cam, b_cam, st = position[v]
        a = -a_cam / b_cam - t0
        b = 1.0 / b_cam
        # Cross-check: the same offset, this time from the overall mix. That is
        # identical on every camera and holds the same voices as the camera
        # microphone. Where the two routes disagree something is wrong, and
        # that should show here rather than on playback.
        share.segment(0.0, 0.30)
        check = next((p for n, p in items
                      if n.startswith(MIX_TRACK_NAME)),
                     items[0][1])
        try:
            HOP, rate = 5.0, 4000
            env_video = video_envelope(v, HOP, rate)
            env_audio = envelope(decode_audio(check, rate=rate), HOP, rate)
            density = int(max(20, min(120, info["duration"] / 30.0)))
            a2, b2, st2 = align_envelopes(env_video, env_audio, HOP,
                                             sample_points=density,
                                             distance_s=30.0,
                                             points_off="audio",
                                             warn=os.path.basename(check))
            deviation = a2 - a
        except Exception as e:
            a2, st2, deviation = None, {}, None
            print(T('  Cross-check:     not possible (%s)') % e)
        fps = max(1.0, info["fps"])
        total = (b - 1.0) * info["duration"]
        uncertainty = st.get("ppm_error", 0.0) / 1e6 * info["duration"]
        threshold = max(0.010, 0.5 / fps)
        drift = (not args.no_drift
                 and abs(total) > 4 * uncertainty and abs(total) > threshold
                 and abs(st.get("ppm", 0.0)) < 500 and info["duration"] >= 120)
        print(T('  Offset:          %s   (from the camera comparison)') % as_hms(a))
        if a2 is not None:
            serious = abs(deviation) > 1.0 / fps
            print(T('  Cross-check:     %s from the Full-Mix, deviation '
                    '%s ms (%s of %s points)%s')
                  % (as_hms(a2),
                     number_text(deviation * 1000.0, 0, plus=True),
                     group_text(st2.get("points", 0)),
                     group_text(st2.get("candidates", 0)),
                     T('   Caution: more than one frame') if serious else ""))
        # The reference camera is what the others were measured
        # against, so there is nothing here that was measured. The line
        # of noughts it used to print -- "+0.00 ppm (+/- 0.00), 0 of 0
        # points" -- read like a measurement and was none.
        if ref_clip and path_key(ref_clip[0]) == path_key(v):
            print(T('  Clock drift:     nothing measured -- this is the '
                    'reference the others are held against'))
        else:
            print(T('  Clock drift:     %s ppm (+/- %s), residual spread '
                    '%s ms, %s of %s points')
                  % (number_text((b - 1.0) * 1e6, 2, plus=True),
                     number_text(st.get("ppm_error", 0.0), 2),
                     number_text(st.get("spread_ms", 0.0)),
                     group_text(st.get("points", 0)),
                     group_text(st.get("candidates", 0) or 0)))
            print(T('  Drift over the running time: %s s = %s frames  -->  %s')
                  % (number_text(total, 3, plus=True),
                     number_text(abs(total) * fps),
                     T('is actively taken out') if drift
                     else T('is left in')))
        print()
        outdir, target = output_path[v]
        os.makedirs(outdir, exist_ok=True)
        # What lies before the In point and after the Out point appears
        # in no cut, and on a long shoot it is the bulk of the file. So
        # the camera is written from the key frame before the window to
        # a margin past its end; without a window nothing is cut.
        cut_at, keep_s = 0.0, None
        if window_s is not None:
            cut_at, keep_s = camera_window_cut(v, info["duration"], a,
                                               window_s)
            a += cut_at
        # Where this file's first frame sits on the wall clock. a is
        # the measured place of that frame in programme time, so this
        # is the one number every camera's stamp comes from.
        at_s = None if tc_start is None else tc_start + a
        share.segment(0.30, 0.85)
        try:
            write_camera_file(v, info, items, target, a, b, drift, args,
                              cut_at=cut_at, keep_s=keep_s, at_s=at_s)
        except Exception as e:
            print(as_bad(T('  Error while writing: %s') % e))
            return None
        track_names = [name for name, _ in items]
        for i, (name, _) in enumerate(items, 1):
            print(T('  Audio track %d:   %s') % (i, name))
        if not args.no_camera_audio and info["audio"]:
            print(T('  Audio track %d:   %s') % (len(items) + 1,
                                              args.name_camera))
        stamp = camera_stamp(info, cut_at, at_s)
        if stamp:
            print("  Timecode:        %s" % stamp)
        if keep_s:
            print(T('  Time window:     %s of %s written, from %s of the '
                    'camera') % (as_hms(keep_s), as_hms(info["duration"]),
                                 as_hms(cut_at)))
        share.segment(0.85, 1.0)
        finish_camera_file(v, info, target, items, args, fps)
        return target, track_names, a, (keep_s or info["duration"])

    # The expensive part is the cross-check, and that only computes. ffmpeg
    # merely copies the picture and waits on the disk. Together they saturate
    # a machine only with several files running at once.
    how_many = getattr(args, "parallel", 0) or min(
        len(videos), max(1, min(4, how_many_processors() // 2)))
    how_many = max(1, min(how_many, len(videos)))
    progress_bar = SharedProgressBar(T('Processing'), len(videos))

    def one(v, info):
        ident = threading.get_ident()
        THREAD_BUFFER[ident] = []
        THREAD_SHARE[ident] = Share(progress_bar, v)
        try:
            return one_camera(os.path.abspath(v), info, THREAD_SHARE[ident])
        except Exception as e:
            print(T('\n  Stopped: %s') % e)
            return None
        finally:
            THREAD_SHARE[ident].report(1.0)
            THREAD_SHARE.pop(ident, None)
            one_camera.texts[v] = "".join(THREAD_BUFFER.pop(ident, []))

    one_camera.texts = {}
    old_off = sys.stdout
    progress_bar.stream = old_off
    sys.stdout = ThreadOutput(old_off)
    try:
        with futures.ThreadPoolExecutor(max_workers=how_many) as pool:
            job = {pool.submit(one, v, info): v for v, info in videos}
            for done_future in futures.as_completed(job):
                v = job[done_future]
                sys.stdout.write("\n" + one_camera.texts.get(v, ""))
                what = done_future.result()
                if what is None:
                    error += 1
                    continue
                target, names, offset, delivered = what
                track_names[target] = names
                offsets[target] = offset   # camera position in the window
                lengths[target] = delivered
                results.append(target)
    finally:
        sys.stdout = old_off
    progress_bar.stop()
    # Back in file order, not in the order of completion.
    order = [os.path.abspath(x) for x, _ in videos]
    results.sort(key=lambda path: order.index(os.path.abspath(path))
                    if os.path.abspath(path) in order else len(order))

    # --- keep the finished tracks, not only hidden inside the videos
    folder = os.path.abspath(args.out) if args.out else os.path.dirname(
        os.path.abspath(videos[0][0]))
    cache = tracks_folder(folder)
    print(as_head(T('\nSAVING TRACKS')))
    # The stored tracks belong to programme time, not to a camera, so
    # their timecode is written at the rate the Timeline runs at.
    tc_fps = max(1.0, timeline_frame_rate(args, videos, ref_clip))
    stored = []
    single_files = {}      # speaker name -> stored WAV
    tc_name = ("_" + timecode_string(tc_start, tc_fps).replace(":", "-"))\
        if tc_start is not None else ""
    for name, source in ([(track["name"], single[track["name"]]) for track in tracks]
                         + [(MIX_TRACK_NAME, full_mix)]):
        target = os.path.join(cache,
                            "final_%s%s.wav" % (safe_filename(name), tc_name))
        show_progress(T('Saving %s') % name, 0.0)
        command = ["ffmpeg", "-v", "error", "-i", source, "-c:a", "copy"]
        if tc_start is not None:
            command += ["-write_bext", "1", "-metadata",
                       "time_reference=%d" % int(round(tc_start * SR))]
        shell_quote(command + ["-y", target])
        if tc_start is not None:
            # Resolve reads bext; Premiere and Media Composer read iXML.
            try:
                append_ixml(target, build_ixml(
                    name, int(round(tc_start * SR)), tc_fps, 24, 1,
                    is_drop_frame(ref_clip[1].get("tc") if ref_clip else None)))
            except Exception as e:
                print(T('  iXML for %s not written: %s')
                      % (os.path.basename(target), e))
        stored.append(target)
        single_files[name] = target
        show_progress(T('Saving %s') % name, 1.0)
        print("\r  %-24s %s%s" % (os.path.basename(target),
                                  as_hms(sample_count(target) / float(SR)),
                                  " " * 20))
    if tc_start is not None:
        print(T('  Timecode %s written as bext and iXML (reference: %s)')
              % (timecode_string(tc_start, tc_fps),
                 os.path.basename(ref_clip[0])))

    if results:
        print(as_head(T('\nRESULT')))
        for path in results:
            print("  %s" % path)
        for path in stored:
            print("  %s" % path)
        # What is in the folder is no longer the whole shoot, and that is
        # worth a sentence: whoever wants more of it than the window
        # holds sets the In and Out point wider and runs again.
        if window_s is not None and lengths:
            print(T('  The cameras carry the time window and a second at '
                    'each end: %s written for %s of the %s recorded.')
                  % (as_data_size(sum(size_in_mb(p) for p in results)),
                     as_hms(sum(lengths.values())),
                     as_hms(sum(i["duration"] for _v, i in videos))))

    # The last stage: the cut list, the handover, the result. The bar
    # lists it, so it is announced here too.
    step_begin("result")
    cut, segment_list = write_cut_list(
        args, segment_list, tracks, cameras, videos, folder, tc_start,
        ref_clip, t1 - t0 if t1 is not None else 0,
        words=heard_words(), sound_source=single_files.get(MIX_TRACK_NAME, ""))
    # Who does the asking. Said, not acted on: the order is what the
    # measurement supports, and a name in the interface is a person's
    # decision.
    asking = who_asks(segment_list, heard_words())
    for line in (roles_report(asking, segment_list)
                 + voice_names_report(asking)):
        print(line)
    if not getattr(args, "no_transcript_file", False) and heard_words():
        print(as_head(T('\nTRANSCRIPT')))
        for path in write_transcript_files(
                folder, safe_filename(args.production or 'Production'),
                heard_words(), segment_list):
            print("  %s" % path)
    # Content and wide shot, and nothing else. The comparison exists to
    # show what a cut between two cameras looks like, so a file that is
    # never cut against them does not belong in it: an 18-second jingle
    # raised a caution about 357 steps of brightness (31.8.2026).
    placed_cameras = {path_key(k) for k in (position or {})}
    at_the_edges = set(path_key(p) for p in
                       (getattr(args, "intro", None), getattr(args, "outro", None))
                       if p)

    def cut_against_the_others(cam):
        where = path_key(cam.get("video") or "")
        return where in placed_cameras and where not in at_the_edges

    colours = []
    if not getattr(args, "no_metrics", False):
        made = (results if len(results) == len(cameras)
                else [cam.get("video") for cam in cameras])
        try:
            colours = report_picture_comparison(
                [{"track": cam.get("name"), "file": p}
                 for cam, p in zip(cameras, made)
                 if cut_against_the_others(cam)])
        except Exception as e:
            print(T('  Colour comparison not possible: %s') % e)
        print(as_head(T('\nMETRICS')))
        target = write_metrics_csv(
            os.path.join(folder, "%s_metrics.csv"
                         % safe_filename(args.production or 'Production')),
            tracks, cut, segment_list, cameras, args, colours, gain)
        if target:
            print("  %s" % target)
    write_handover(args, tracks, cameras, videos, folder, tc_start,
                      ref_clip, results, cut, segment_list,
                      t1 - t0 if t1 is not None else 0, track_names,
                      single_files, offsets, lengths, words=heard_words(),
                      unplaceable=[cam["video"] for cam in cameras
                                   if path_key(cam["video"])
                                   not in placed_cameras])
    shutil.rmtree(tmpdir, ignore_errors=True)
    return 1 if error else 0
