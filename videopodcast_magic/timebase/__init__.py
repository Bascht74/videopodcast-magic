# -*- coding: utf-8 -*-
"""The time base and the camera files: one axis, the tracks back on it.

A piece of the program, read out of the folder beside it by beside().
It takes the plan pipeline/ made of the recordings, puts every track
and camera on one time axis, and writes the camera files a run ends
in. The program is handed in, and every name this piece uses out of it
is bound below, by name.
"""

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

# What the program has and this piece uses, bound once. Not one of the
# names below is bent while the run goes on, so a copy taken here
# cannot go stale under it.
AUDIO_SUFFIXES = PROGRAM.AUDIO_SUFFIXES
AXIS_MIN_WINDOW_S = PROGRAM.AXIS_MIN_WINDOW_S
ByFile = PROGRAM.ByFile
CAMERA_MARGIN_S = PROGRAM.CAMERA_MARGIN_S
MIX_TRACK_NAME = PROGRAM.MIX_TRACK_NAME
SOUND_FINISHED = PROGRAM.SOUND_FINISHED
SOUND_SPEECH = PROGRAM.SOUND_SPEECH
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
axis_stage_key = PROGRAM.axis_stage_key
build_ixml = PROGRAM.build_ixml
cameras_heard = PROGRAM.cameras_heard
cannot_be_placed = PROGRAM.cannot_be_placed
channel_count = PROGRAM.channel_count
check_camera_metadata = PROGRAM.check_camera_metadata
check_colour_survived = PROGRAM.check_colour_survived
check_data_tracks = PROGRAM.check_data_tracks
clock_apart_lines = PROGRAM.clock_apart_lines
clock_base = PROGRAM.clock_base
choose_preset = PROGRAM.choose_preset
colour_arguments = PROGRAM.colour_arguments
copy_mov_atoms = PROGRAM.copy_mov_atoms
cross_correlate = PROGRAM.cross_correlate
cut_list_of = PROGRAM.cut_list_of
data_track_maps = PROGRAM.data_track_maps
decode_audio = PROGRAM.decode_audio
decode_audio_tracks = PROGRAM.decode_audio_tracks
envelope = PROGRAM.envelope
ffprobe_json = PROGRAM.ffprobe_json
file_frame_rate = PROGRAM.file_frame_rate
file_timecode = PROGRAM.file_timecode
find_master_file = PROGRAM.find_master_file
finish_without_auphonic = PROGRAM.finish_without_auphonic
futures = PROGRAM.futures
guess_production_name = PROGRAM.guess_production_name
handover_of = PROGRAM.handover_of
how_many_processors = PROGRAM.how_many_processors
is_drop_frame = PROGRAM.is_drop_frame
join_with_report = PROGRAM.join_with_report
json = PROGRAM.json
kept_channels = PROGRAM.kept_channels
label_of = PROGRAM.label_of
known_frame_rate = PROGRAM.known_frame_rate
log_curve_from_atom = PROGRAM.log_curve_from_atom
lufs_does_nothing = PROGRAM.lufs_does_nothing
mix_tracks = PROGRAM.mix_tracks
mix_width = PROGRAM.mix_width
name_order = PROGRAM.name_order
no_base_message = PROGRAM.no_base_message
no_place_message = PROGRAM.no_place_message
normalise_loudness = PROGRAM.normalise_loudness
number_text = PROGRAM.number_text
os = PROGRAM.os
parse_time_point = PROGRAM.parse_time_point
parse_timecode = PROGRAM.parse_timecode
path_key = PROGRAM.path_key
phase_way_on = PROGRAM.phase_way_on
place_track_on_axis = PROGRAM.place_track_on_axis
rate_filter_chain = PROGRAM.rate_filter_chain
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
stage_get = PROGRAM.stage_get
stage_key = PROGRAM.stage_key
stage_put = PROGRAM.stage_put
step_begin = PROGRAM.step_begin
subprocess = PROGRAM.subprocess
sync_only = PROGRAM.sync_only
sys = PROGRAM.sys
tempfile = PROGRAM.tempfile
threading = PROGRAM.threading
timecode_moved = PROGRAM.timecode_moved
timecode_seconds = PROGRAM.timecode_seconds
timecode_string = PROGRAM.timecode_string
timeline_frame_rate = PROGRAM.timeline_frame_rate
tracks_folder = PROGRAM.tracks_folder
verify_alignment = PROGRAM.verify_alignment
verify_returned_tracks = PROGRAM.verify_returned_tracks
video_envelope = PROGRAM.video_envelope
video_facts = PROGRAM.video_facts
voice_names_report = PROGRAM.voice_names_report
voices_reported = PROGRAM.voices_reported
where_it_sounds = PROGRAM.where_it_sounds
which_way_placed = PROGRAM.which_way_placed
who_asks = PROGRAM.who_asks
write_cut_list = PROGRAM.write_cut_list
write_handover = PROGRAM.write_handover
write_metrics_csv = PROGRAM.write_metrics_csv
write_transcript_files = PROGRAM.write_transcript_files


# =====================  The time base  ==============================
#  Every track and camera on one axis, then the tracks put back onto
#  each camera and the camera files written.


def clocks_on_the_axis(videos, position, tracks, ref_clip):
    """Every file besides the reference that knows the time of day.

    One entry per file with a timecode and a measured place on the axis:
    the name to say it by, the clock in seconds, and the place (file
    time = a + b * axis time). Left out: a file never placed -- its clock
    says when, not where -- and one placed by its clock, which only
    repeats its base's clock. The preview counts neither (measure_time_axis).
    """
    found = []
    for v, info in videos:
        if v == ref_clip[0] or v not in position:
            continue
        when = timecode_seconds(info)
        if when is None:
            continue
        a, b, st = position[v]
        if (st or {}).get("by_clock_only"):
            continue
        found.append({"name": PROGRAM.camera_shown(v), "tc": when,
                      "a": a, "b": b})
    for track in (tracks or []):
        blocks = track.get("blocks") or []
        if (track.get("st") or {}).get("by_clock_only"):
            continue
        # The blocks were sorted and joined on one axis, so the first one's
        # clock is the joined recording's. A recorder writes no frames, so a
        # timecode track's frames are read at the reference picture's rate.
        when = file_timecode(blocks[0], ref_clip[1]["fps"]) if blocks else None
        if when is None:
            continue
        found.append({"name": PROGRAM.recording_shown(blocks[0]), "tc": when,
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
    # The median, so one clock set wrong cannot move the window: in one
    # production two cameras disagreed by two seconds. measure_time_axis
    # ties the preview's axis by the same rule, so player and run agree.
    return says[len(says) // 2] if says else None


def clip_to_time_window(args, t0, t1, ref_clip, clocks=()):
    """Apply the In point and the Out point to the measured window.

    The window lives in reference camera time. An absolute value goes
    through a timecode; a relative one counts from the window start, a
    negative one back from its end. *clocks* is what else on the axis
    knows the time of day, shaped as axis_starts_at wants -- the
    reference is the longest camera and need not carry a clock.
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
                    % (value_text, PROGRAM.camera_shown(ref_clip[0])))
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
        # Which clocks the axis hangs on, and what the reference's first frame
        # reads. The reference carries no timecode, so without this the two
        # lines below are a number nobody can check.
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


def track_name_of(e):
    """The name a track carries: its own, its speaker's, else its file's.

    One answer for a plan's entry and for the track made of it, so the
    plan's preview and the writer sort a camera's tracks by one key --
    a track nobody named included, which carries its first file's name.
    """
    blocks = e.get("blocks") or [e.get("audio") or ""]
    return (e.get("name") or e.get("speakers")
            or os.path.basename(blocks[0]))


def tracks_per_camera(entries):
    """What each camera carries, {camera: [entry, ...]}, in name order.

    The one order for several names on one camera, set here: the name
    the command line gives a camera, the mix's label, the tracks under
    it and the log lines all come out of this, track_name_of sorted by
    name_order as the window's file name and the Resolve track sort
    them. An entry with no camera belongs to none and is left out.
    """
    out = ByFile()
    for e in entries:
        if e.get("camera"):
            out.setdefault(e["camera"], []).append(e)
    for own in out.values():
        own.sort(key=lambda e: name_order(track_name_of(e)))
    return out


def join_the_plan(plan, tmpdir):
    """Join the blocks of every track. No camera is needed for that.

    A track keeps only the blocks the join kept: one left out as too far
    apart is in neither the sound nor the list. The first always stays.
    """
    made = []
    for e in plan:
        blocks = e.get("blocks") or [e["audio"]]
        name = track_name_of(e)
        if len(blocks) > 1:
            source, join_info = join_with_report(
                blocks, os.path.join(tmpdir,
                                     "raw_%s.wav" % safe_filename(name)))
            out = {n for n, _far in join_info.get("dropped", [])}
            blocks = [b for i, b in enumerate(blocks)
                      if not i or PROGRAM.recording_shown(b) not in out]
            hint = T('%s blocks') % number_text(join_info["blocks"], 0) \
                if len(blocks) > 1 else ""
        else:
            source, hint = blocks[0], ""
        made.append({"name": name, "source": source, "hint": hint,
                     "blocks": list(blocks), "camera": e.get("camera") or ""})
    return made


def join_only(args, tracks, tmpdir, title=""):
    """Join the blocks and stop: there is no picture to lay them on.

    Joining the blocks of a recording needs no camera, and one file out
    of several is a whole result. One recording: several go onto one
    axis, align_tracks_only, whatever --multitrack says.
    """
    first = tracks[0]["blocks"][0]
    folder = PROGRAM.output_folder(args, first)
    # Measured, said, and adjusted to a target as on any run with a
    # picture. One gain per recording: without a picture they are not laid
    # against each other, so there is no balance between them to keep.
    for track in tracks:
        try:
            gain, curve = normalise_loudness(
                [{"name": track["name"], "axis": track["source"],
                  "ready": track["source"]}], args.lufs, tmpdir, None,
                channels=channel_count(track["source"]))
        except PROGRAM.Stopped:
            # Stop ends the run; it is no failure of this step.
            raise
        except Exception as e:
            gain, curve = 0.0, None
            print(T('  Loudness not measurable: %s') % str(e)[:60])
        if gain or curve:
            track["source"] = mix_tracks(
                [track["source"]],
                os.path.join(tmpdir, "level_%s.wav"
                             % safe_filename(track["name"])),
                gain, curve, channels=channel_count(track["source"]))
    # Said, not dropped in silence: nothing here is cut to a window.
    if getattr(args, "in_point", None) or getattr(args, "out_point", None):
        print(T('  In point and Out point do nothing here: one recording '
                'without a picture is joined whole.'))
    if args.auphonic_done or (args.auphonic_key and run_uploads(args)):
        # What came back is held against what went up, the same as on a
        # run with a picture: --auphonic-done in place of the upload.
        for track in tracks:
            track["axis"] = track["source"]
        longest = max(sample_count(t["source"]) for t in tracks) / float(SR)
        if args.auphonic_done:
            if not processed_tracks_taken(args, tracks, tmpdir, dict(
                    (t["name"], sample_count(t["source"]) / float(SR))
                    for t in tracks)):
                return 1
            return 0 if args.dry_run or verify_returned_tracks(
                tracks, longest, tmpdir) else 1
        return send_to_auphonic(args, tracks, folder, tmpdir, longest,
                                title, together=False) or 0
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


def drift_measured(st):
    """Whether a placing measured a drift, and not only where a file sits.

    A fit over the sample points gives one. The reference, a clock, the
    phase and too few points give none, and their noughts -- "+0.00
    ppm ... 0 of 40 points" -- read like a drift measured at zero.
    """
    return "ppm" in (st or {}) and not (st or {}).get("from_phase")


# A drift is taken out only at this many times its own uncertainty:
# the fixture's four turns gave +67.6 +/- 40 ppm, real material 12-56 +/- 0.5.
DRIFT_OVER_ERROR = 3.0


def drift_clear(b, st):
    """Whether the clock drift in *b* stands clear of its uncertainty.

    Every path asks this one question: the drift is taken out only where
    it is at least DRIFT_OVER_ERROR times the slope's standard error the
    fit gave. A placing that measured no drift has none to take out.
    """
    ppm = (b - 1.0) * 1e6
    return bool(drift_measured(st) and abs(b - 1.0) > 1e-7
                and abs(ppm) >= DRIFT_OVER_ERROR
                * (st or {}).get("ppm_error", float("inf")))


def drift_note(b, st, drift):
    """What the axis line says about a track's clock drift.

    Taken out, left in because nothing asked for it, or left in with
    both numbers where a drift was measured but did not stand clear.
    """
    ppm = (b - 1.0) * 1e6
    if drift:
        return T(', clock drift %s ppm taken out') % number_text(
            ppm, 1, plus=True)
    if drift_measured(st) and abs(b - 1.0) > 1e-7 and not drift_clear(b, st):
        return T(', clock drift %s ppm left in: not %s times its '
                 'uncertainty of %s ppm') % (
            number_text(ppm, 1, plus=True),
            number_text(DRIFT_OVER_ERROR, 0),
            number_text((st or {}).get("ppm_error", 0.0), 1))
    return T(', clock drift left in')


def phase_of_run(args, paths):
    """Whether this run lets the phase way place the recording of *paths*.

    What --sound, --sound-of and --project-type said, read in one place;
    a run that said nothing takes speech, so the phase way stays off.
    """
    return phase_way_on(paths, getattr(args, "project_type", "cut"),
                        getattr(args, "sound", None) or SOUND_SPEECH,
                        getattr(args, "sound_of", None) or ())


def camera_hint(st):
    """What a camera's axis line adds about how it was placed.

    Through which camera, where the reference could not place it (the
    chain of cameras_on_one_axis), and whether its clock showed the
    search where to look.
    """
    said = []
    if (st or {}).get("via"):
        said.append(T('placed through %s') % PROGRAM.camera_shown(st["via"]))
    if (st or {}).get("clock_hint"):
        said.append(T('found where its timecode pointed'))
    return ", ".join(said)


def offset_line(name, a, st, hint=""):
    """Say where one file sits on the axis: offset, and the drift if any.

    Cameras and recordings, with a picture and without, say it in this
    one line, so a placing reads the same whichever path made it.
    """
    note = "  [" + hint + "]" if hint else ""
    if not drift_measured(st):
        print(T('  %-20s offset %s, clock drift not measured%s')
              % (name, as_hms(a), note))
        return
    print(T('  %-20s offset %s, clock drift %s ppm (+/- %s), '
            'residual spread %s ms, %s of %s points%s')
          % (name, as_hms(a),
             number_text(st.get("ppm", 0.0), 2, plus=True),
             number_text(st.get("ppm_error", 0.0), 2),
             number_text(st.get("spread_ms", 0.0)),
             number_text(st.get("points", 0), 0),
             number_text(st.get("candidates", 0), 0), note))


def sound_places(name, source, reference, length, phase):
    """Where its sound puts one recording against *reference*, or None.

    The one measurement both paths take, a camera's sound or the
    longest recording as *reference*; a failure is said, not raised.
    """
    try:
        return align_audio_to_video(
            source, reference,
            sample_points=int(max(20, min(120, length / 30.0))),
            distance_s=30.0, phase=phase)
    except Exception as e:
        print(T('  %-20s cannot be aligned: %s') % (name, e))
        return None


def sound_or_clock(name, placing, hint, own_tc, other_tcs, at_clock,
                   no_base=no_base_message):
    """The place the sound gave, or the clock's where the sound found none.

    One rule with a picture and without: a recording the sound cannot
    place stands at its timecode where *at_clock* finds a base, and is
    refused, said, where neither answers. Returns (a, b, st, hint).
    """
    a, b, st = placing
    hint = which_way_placed(st, hint)
    if not st.get("unplaceable"):
        return a, b, st, hint
    if cannot_be_placed(st, own_tc, other_tcs):
        print(as_bad("  " + no_place_message(name)))
        return None
    at = at_clock(own_tc)
    if at is None:
        print(as_bad("  " + no_base(name)))
        return None
    return at + ((hint + ", " if hint else "") + T(
        'sound not recognised, placed by its timecode'),)


def no_recording_base_message(name):
    """no_base_message without a picture: the base is a recording."""
    return T('%s cannot be placed: its sound has nothing in common with '
             'the rest of the material, and no recording the sound placed '
             'carries a timecode to set its own against. One of those '
             'needs a timecode that fits this one, and that has to be set '
             'with another program.') % name


def measure_tracks_against_each_other(tracks, phase_of=lambda paths: True):
    """Put every track on the time axis of the longest one.

    The longest recording is the reference for the same reason the
    longest camera is: it overlaps most with the others. A track the
    sound cannot place stands at its clock, as with a picture. Returns
    the tracks that found a place, each carrying a and b. *phase_of*
    says of a track's blocks whether the phase way may place it.
    """
    reference = max(tracks, key=lambda t: sample_count(t["source"]))
    length = sample_count(reference["source"]) / float(SR)
    print(T('  Reference: %s (%s, longest running time)')
          % (reference["name"], as_hms(length)))
    measured = dict(
        (id(t), sound_places(t["name"], t["source"], reference["source"],
                             length, bool(phase_of(t.get("blocks")
                                                   or [t["source"]]))))
        for t in tracks if t is not reference)
    # The clock of each, read off its first block, and the base the
    # cameras' rule picks: the first the sound placed, reference first.
    clocks = dict((id(t), file_timecode((t.get("blocks") or [t["source"]])[0]))
                  for t in tracks)
    position = {id(reference): (0.0, 1.0, {})}
    position.update((k, m) for k, m in measured.items()
                    if m and not m[2].get("unplaceable"))
    placed = []
    for track in tracks:
        if track is reference:
            track["a"], track["b"] = 0.0, 1.0
            placed.append(track)
            continue
        got = measured.get(id(track)) and sound_or_clock(
            track["name"], measured[id(track)], track.get("hint") or "",
            clocks[id(track)],
            [c for k, c in clocks.items() if k != id(track)],
            lambda tc: recording_at_its_clock(tc, position, clocks),
            no_recording_base_message)
        if not got:
            continue
        track["a"], track["b"], track["st"], track["hint"] = got
        placed.append(track)
        offset_line(track["name"], track["a"], track["st"], track["hint"])
    return placed


def tracks_onto_axis(args, tracks, t0, t1, folder, pattern):
    """Write every track onto the axis from *t0* to *t1*, into *folder*.

    Both paths write with this, a picture's into the temp folder and
    the one without under *pattern* into the output; the drift is taken
    out only where it stands clear, and the line under each says so.
    """
    print(as_head(T('\nWRITING TRACKS TO THE AXIS')))
    for track in tracks:
        target = os.path.join(folder, pattern % safe_filename(track["name"]))
        track["drift"] = (not getattr(args, "no_drift", False)
                          and drift_clear(track["b"], track.get("st")))
        show_progress(track["name"], 0.0)
        place_track_on_axis(track["source"], target, track["a"], track["b"],
                            t0, t1, track["drift"])
        show_progress(track["name"], 1.0)
        print()
        track["axis"] = target
        print("    %s, %s%s" % (as_hms(sample_count(target) / float(SR)),
                                as_data_size(size_in_mb(target)),
                                drift_note(track["b"], track.get("st"),
                                           track["drift"])))
    verify_alignment(tracks, t0, t1,
                     drift_allowed=not getattr(args, "no_drift", False))


def align_tracks_only(args, tracks, tmpdir, title=""):
    """Lay the tracks against each other where there is no picture.

    Equally long and with the same start point, which is what a
    multitrack production needs. The window holds everything any track
    heard: a silent edge costs less than a recording cut short.
    """
    step_begin("time base")
    print(as_head(T('\nMEASURING THE TIME AXIS')))
    print(T('  No picture: the tracks are laid against each other.'))
    placed = measure_tracks_against_each_other(
        tracks, lambda paths: phase_of_run(args, paths))
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
    folder = PROGRAM.output_folder(args, placed[0]["blocks"][0])
    if lufs_does_nothing(args, (), len(placed)):
        print(T('  --lufs does nothing here: the tracks leave as they '
                'were recorded, and the loudness is set where they are '
                'mixed.'))
    if not args.dry_run:
        os.makedirs(folder, exist_ok=True)
    tracks_onto_axis(args, placed, t0, t1,
                     tmpdir if args.dry_run else folder, "%s_aligned.wav")
    stop = None
    if args.auphonic_done:
        # Already processed: taken as the run with a picture takes them.
        stop = None if processed_tracks_taken(
            args, placed, tmpdir, dict((t["name"], t1 - t0) for t in placed),
            last - first, t0) and (args.dry_run or verify_returned_tracks(
                placed, t1 - t0, tmpdir)) else 1
    elif args.auphonic_key and run_uploads(args):
        stop = send_to_auphonic(args, placed, folder, tmpdir, t1 - t0, title)
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


def preset_for_run(args, key, multitrack):
    """The preset of the kind asked for, chosen once for the whole run.

    Asked before the time axis and again where the tracks go up; the
    second time answers from the first unless the kind changed, as it
    does where a track found no place. Returns (uuid, name).
    """
    kept = getattr(args, "_preset", None)
    if kept and kept[0] == multitrack:
        return kept[1:]
    preset, name = choose_preset(key, args.auphonic_preset, multitrack,
                                 lufs=args.lufs,
                                 anyway=getattr(args, "anyway", False))
    args._preset = (multitrack, preset, name)
    return preset, name


def preset_before_the_axis(args, count, together):
    """Choose the preset before the time axis, by the rule sending follows.

    A preset of the wrong kind stopped the run only once the axis was
    measured. *count* tracks in the plan, *together* on one axis. Returns
    1 where the run ends, None where it goes on; a run that sends
    nothing asks nothing.
    """
    if not (args.auphonic_key and run_uploads(args)):
        return None
    try:
        preset_for_run(args, api_key_from_anywhere(args),
                       PROGRAM.production_is_multitrack(count, together))
    except PROGRAM.Stopped:
        # Stop ends the run; it is no failure of this step.
        raise
    except Exception as e:
        print(T('\nNo preset chosen: %s') % e)
        return 1
    return None


def send_to_auphonic(args, tracks, folder, tmpdir, window, title="",
                     together=True):
    """Send the tracks to auphonic.com and hold what comes back.

    The one road up, for every path; how the tracks go up is
    production_is_multitrack's answer. Each result lands in the track's
    "done", checked against *window* seconds. Returns 1 where the run is
    over, None where it goes on -- on a dry run too, which checks nothing.
    """
    key = api_key_from_anywhere(args)
    multitrack = PROGRAM.production_is_multitrack(len(tracks), together)
    try:
        preset, presetname = preset_for_run(args, key, multitrack)
    except PROGRAM.Stopped:
        # Stop ends the run; it is no failure of this step.
        raise
    except Exception as e:
        print(T('\nNo preset chosen: %s') % e)
        return 1
    try:
        if multitrack:
            done = run_multitrack_production(
                key, preset, title or 'Production', tracks, folder,
                args.auphonic_wait, args.dry_run, args.auphonic_resume)
        else:
            done = dict((track["name"], run_single_production(
                track["axis"], preset, presetname, key, folder,
                args.auphonic_wait, args.dry_run, title or track["name"]))
                for track in tracks)
    except PROGRAM.Stopped:
        # Stop ends the run; it is no failure of this step.
        raise
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


def processed_tracks_taken(args, tracks, tmpdir, lengths, measured=None,
                           shift=0.0):
    """Take the tracks --auphonic-done hands in, in place of an upload.

    Each finds its file by name, as long as *lengths* says for it, give
    or take a jingle -- or as long as *measured*, the range without In and
    Out point, *shift* seconds before the window: then it is trimmed.
    Sets "done"; False, and said, where one found none.
    """
    if getattr(args, "without_auphonic", False):
        print(as_warn(T('  --without-auphonic and --auphonic-done were '
                        'both given. The finished tracks win: there is '
                        'nothing left to send anywhere.')))
    folder = os.path.abspath(args.auphonic_done)
    print(as_head(T('\nALREADY PROCESSED')))
    print(T('  From %s') % folder)
    existing = [f for f in os.listdir(folder)
                if os.path.splitext(f)[1].lower() in AUDIO_SUFFIXES]
    # Trimming leaves slack at both ends, so nothing is lost even where a
    # jingle was prepended. The return check finds the exact position
    # anyway and trims to the sample.
    MARGIN = 30.0
    bad = []
    for track in tracks:
        window = lengths[track["name"]]
        whole = window if measured is None else measured
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
        # The length may differ by a jingle, not by minutes, or the file is
        # from another run. Two lengths qualify: this run's window, and the
        # longer measured one without In and Out point, which gets trimmed.
        if abs(length - window) <= 60:
            track["done"] = file_path
            existing.remove(best)
            print(T('    %-20s <- %s  (%s, name similarity %s)')
                  % (track["name"], best, as_hms(length),
                     number_text(quality, 2)))
            continue
        if abs(window - whole) > 0.001 and abs(length - whole) <= 60:
            # A prepended jingle lengthens the file; everything sits
            # further back by the same amount.
            front = shift + max(0.0, length - whole)
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
                     number_text(quality, 2)))
            continue
        print(T('    %-20s <- %s  BUT %s -- neither the time window '
                '(%s) nor the\n    %-20s    whole measured range (%s). '
                'This belongs to another run.')
              % (track["name"], best, as_hms(length), as_hms(window), "",
                 as_hms(whole)))
        bad.append(track["name"])
    if bad:
        print(T('\n  Not usable: %s') % ", ".join(bad))
        print(T('  The files in the folder must be named after the '
                'speakers and belong\n  to this run. Without the folder '
                'it goes through auphonic.com again.'))
        return False
    return True


def common_window(camera_areas):
    """The stretch every camera saw, and the two that decide it.

    *camera_areas* is (from, to, name) per camera, in reference camera
    time. Returns (t0, begins_with, t1, ends_with).

    Every camera, not any camera. A window wider than a camera reaches
    has a stretch where a cut to that camera finds no picture, and the
    episode then comes out shorter than the window said it would.
    Measured on 26.8.2026 over the test interview: the beginning lay
    12.567 s before one of three cameras began, and on the fixture the
    window even began at -0.180 s -- before its own zero. Whoever wants
    that stretch anyway sets an In point of their own; what is derived
    is a window every camera can fill. Decided on 29.8.2026.

    A function of its own rather than a step inside the timebase: it is
    arithmetic and nothing else, and arithmetic can be held against
    numbers without building a window and an hour of sound first.
    """
    t0, begins_with = max((x, name) for x, _y, name in camera_areas)
    t1, ends_with = min((y, name) for _x, y, name in camera_areas)
    return t0, begins_with, t1, ends_with


def run_uploads(args):
    """Whether this run sends its tracks to auphonic.com.

    Not with --without-auphonic, and not with --auphonic-done, which
    hands in tracks that are processed already.
    """
    return (not getattr(args, "without_auphonic", False)
            and not getattr(args, "auphonic_done", None))


def silence_sentence(where, how_much, uploading):
    """The line for missing audio that was filled with silence.

    Past half a minute an In or Out point would have kept that silence
    out of the upload, and the line says so -- but only where there is
    an upload to save. A run with --without-auphonic was told it would
    save one it never makes.
    """
    return (T('Missing audio %s filled with silence%s')
            % (where, T(' -- an In or Out point saves the upload')
               if how_much > 30 and uploading else ""))


def recording_at_its_clock(own_tc, position, clocks):
    """Where a recording no measurement placed stands by its clock.

    The camera's rule: the base is the one clock_base picks among what
    the sound placed -- cameras, or recordings without a picture --
    reference first, and the recording sits its clock less the base's
    from it. *clocks* maps what *position* holds to its clock. Returns
    (a, b, st) as a measurement does, or None with no base.
    """
    w = clock_base(own_tc, [(c, clocks.get(c)) for c, (_a, _b, st_c)
                            in position.items()
                            if not st_c.get("by_clock_only")])
    if w is None:
        return None
    return (position[w][0] + clocks[w] - own_tc, 1.0,
            {"points": 0, "unplaceable": True, "by_clock_only": True})


def run_axis_key(args, plan, video_paths):
    """The name the run's axis is kept under: the window's, axis_stage_key.

    Every camera and block, the recordings made of blocks, the files the
    phase way may place, each asked with all its blocks; a camera's own
    sound is its camera. --tc and --fps go in, and the window gives
    none, so without them the two name one axis alike.
    """
    rows = dict((os.path.abspath(e["blocks"][0]),
                 [os.path.abspath(b) for b in e["blocks"]])
                for e in plan if len(e.get("blocks") or ()) > 1
                and not e.get("from_camera"))
    paths = [os.path.abspath(v) for v in video_paths] + [
        os.path.abspath(b) for e in plan if not e.get("from_camera")
        for b in (e.get("blocks") or [e["audio"]])]
    row_of = ByFile(rows)
    return axis_stage_key(
        paths, rows,
        [p for p in paths if phase_of_run(args, row_of.get(p) or [p])],
        tc=getattr(args, "tc", None), fps=getattr(args, "fps", None))


def raw_place(blocks):
    """Where a recording's own measurement stands in a kept axis.

    Joined and alone are two measurements of one head, kept apart.
    """
    return ("joined" if len(blocks) > 1 else "recordings",
            path_key(blocks[0]))


def axis_raw(heard, videos):
    """What the cameras' sound said, as the stage store keeps it.

    By path_key, so the window finds it under its own spelling: the
    reference, the placed cameras, those left and those not heard.
    """
    ref, placed, left = heard
    return {"reference": path_key(ref),
            "cameras": dict((path_key(v), list(at))
                            for v, at in placed.items()),
            "left": dict((path_key(v), dict(st)) for v, st in left.items()),
            "unheard": [path_key(v) for v, _i in videos
                        if v not in placed and v not in left],
            "recordings": {}, "joined": {}}


def axis_raw_taken(raw, videos, plan):
    """The kept measurement, where it answers everything this run asks.

    Returns (what cameras_heard would say, one placing per plan entry)
    or None: every camera heard, left or unheard in it and no other, and
    every recording not a camera's own sound measured -- a placing may
    be None, a measurement that failed. Whoever measured it, the window
    or a run, the rest is worked out here as after measuring.
    """
    try:
        found = dict((path_key(v), v) for v, _i in videos)
        placed, left = raw["cameras"], raw.get("left") or {}
        heard = set(placed) | set(left)
        if raw["reference"] not in placed or not heard <= set(found) \
                or set(found) - heard - set(raw.get("unheard") or ()):
            return None
        placings = []
        for e in plan:
            part, head = raw_place(e.get("blocks") or [e["audio"]])
            if not e.get("from_camera") and head not in raw[part]:
                return None
            placings.append(None if e.get("from_camera")
                            else raw[part][head])
    except (TypeError, KeyError, AttributeError):
        return None
    return ((found[raw["reference"]],
             dict((found[k], tuple(at)) for k, at in placed.items()),
             dict((found[k], dict(st)) for k, st in left.items())),
            placings)


def tracks_placed(args, plan, joined, ref_clip, position, clocks, kept=None):
    """Put every joined recording of the plan on the axis the cameras hold.

    A recording no measurement and no clock places is refused rather
    than laid down somewhere, where it would look exactly like one that
    fits. *kept* is one measurement per entry out of the stage store,
    used instead of measuring. Returns the tracks and the measurements.
    """
    tracks, placings = [], []
    placed = ByFile(position)
    for i, (e, made) in enumerate(zip(plan, joined)):
        blocks, name = made["blocks"], made["name"]
        source, hint = made["source"], made["hint"]
        placings.append(None)
        # A camera's own sound stands with its camera, whichever way the
        # camera was placed: measured again it is the same sound, or a
        # steady tone lands wherever the phase finds a peak.
        own = placed.get(e["from_camera"]) if e.get("from_camera") else None
        if own is not None:
            a, b, st = own[0], own[1], dict(own[2])
            hint = (hint + ", " if hint else "") + (
                T("placed with its camera, by that camera's clock")
                if st.get("by_clock_only") else T("placed with its camera"))
        elif e.get("from_camera"):
            # Its camera got no place: laid on its own it would stand on
            # the axis beside a picture handed over nowhere.
            print(as_bad("  " + no_place_message(name)))
            continue
        else:
            # Every way came up empty and the clock answers: it stands
            # there, never at the failed measurement -- as without one.
            got = kept[i] if kept else sound_places(
                name, source, ref_clip[0], ref_clip[1]["duration"],
                phase_of_run(args, blocks or [source]))
            placings[-1] = list(got) if got else None
            got = got and sound_or_clock(
                name, got, hint,
                (file_timecode(blocks[0], ref_clip[1]["fps"])
                 if blocks else None), list(clocks.values()),
                lambda tc: recording_at_its_clock(tc, position, clocks))
            if not got:
                continue
            a, b, st, hint = got
        tracks.append({"name": name, "source": source, "a": a, "b": b,
                       "st": st, "camera": e.get("camera") or "",
                       # Which recording the sound came from, apart from
                       # the speaker's camera: a camera's audio goes to a
                       # file of its own, and only this names the recording.
                       "from_camera": e.get("from_camera") or "",
                       "blocks": list(blocks), "hint": hint})
        offset_line(name, a, st, hint)
    return tracks, placings


def speakers_key(args, tracks, window):
    """The name who speaks when is kept under in the stage store.

    What the measurement reads: each recording by its blocks and where
    it lies on the axis, the window, and what a separation handed on.
    """
    return stage_key(
        "speakers", [b for t in tracks for b in t.get("blocks") or ()],
        tracks=[[t["name"], t.get("a"), t.get("b"), bool(t.get("drift")),
                 len(t.get("blocks") or ())] for t in tracks],
        window=list(window or ()),
        voices=getattr(args, "_speakers", None),
        separated=sorted(path_key(p) for p in
                         getattr(args, "_separated", None) or ()),
        mixed=bool(getattr(args, "_speakers_mixed", False)))


def speakers_of_the_run(args, tracks, window):
    """Who speaks when, measured once for the same recordings and window.

    Out of the stage store where a dry run or an earlier run measured
    the same inputs, and said so; else measured and kept there.
    """
    key = speakers_key(args, tracks, window)
    kept = stage_get(key)
    if kept is not None:
        segments = [(name, [tuple(s) for s in segs]) for name, segs in kept]
        print(as_head(T('\nSPEAKERS -- MEASURED BEFORE')))
        print(T('  Taken from the measurement kept on this machine: the '
                'same recordings, places and window.'))
        voices_reported(segments)
        return segments
    segments = speakers_for_the_cut(args, tracks, window=window)
    stage_put(key, segments)
    return segments


def programme_start(ref_clip, t0):
    """Programme time on the wall clock: the reference's clock at *t0*.

    Every stamp counts from here, so they agree; off each camera's own
    clock they differed by as much as those clocks did. None without one.
    """
    if ref_clip and ref_clip[1].get("tc") and t0 is not None:
        return parse_timecode(ref_clip[1]["tc"],
                              max(1.0, ref_clip[1]["fps"])) + t0
    return None


def placing_notes(cameras, position):
    """What the handover says of how the cameras were placed.

    The cameras no measurement placed, and {camera: how well its sound
    matched} for those placed by their clock alone.
    """
    placed = {path_key(k) for k in (position or {})}
    return ([cam["video"] for cam in cameras
             if path_key(cam["video"]) not in placed],
            {v: st.get("quality") for v, (_a, _b, st)
             in (position or {}).items() if st.get("by_clock_only")})


def roles_said(segment_list, words):
    """Who does the asking. Said, not acted on.

    The order is what the measurement supports, and a name in the
    interface is a person's decision.
    """
    asking = who_asks(segment_list, words)
    for line in (roles_report(asking, segment_list)
                 + voice_names_report(asking)):
        print(line)


def dropped_said(tracks):
    """Say what each track loses outside the window, end by end.

    The numbers were computed and printed nowhere, so a run that dropped
    eight seconds looked like one that dropped nothing. Only the end that
    loses something is named: "0:00:00.000 at the front" is a stretch
    that is not there.
    """
    for track in tracks:
        front, back = track["dropped_head"], track["dropped_tail"]
        if front > 0.25 and back > 0.25:
            print(T('    %s: %s at the front and %s at the back have no '
                    'picture and are left out')
                  % (track["name"], as_hms(front), as_hms(back)))
        elif front > 0.25:
            print(T('    %s: %s at the front has no picture and is left '
                    'out') % (track["name"], as_hms(front)))
        elif back > 0.25:
            print(T('    %s: %s at the back has no picture and is left '
                    'out') % (track["name"], as_hms(back)))


def finished_mix_homeless(args):
    """Whether a finished mix was given to a run with no picture: said.

    The preflight says it first; this is the net under --anyway.
    """
    if not getattr(args, "finished_mix", None):
        return False
    print(as_bad("\n" + T('the finished mix takes the place of the mix in '
                          'the camera files, and without a video file '
                          'there are none.')))
    return True


def finished_mix_placed(args, ref_clip, position, clocks, tmpdir):
    """Put the finished mix on the axis the cameras hold, as a recording.

    Its blocks joined as a recording's are, placed with the phase way on
    as mixed sound is, and by its clock where the sound finds nothing.
    The placing is kept by its blocks and the reference, so a dry run
    for the preview does not measure it again. None without one, False
    where nothing places it: the run stops rather than lay it anywhere.
    """
    blocks = [os.path.abspath(p) for p in
              getattr(args, "finished_mix", None) or ()]
    if not blocks:
        return None
    name = label_of(SOUND_FINISHED)
    print(T('  %s takes the place of the mix this run would build.')
          % PROGRAM.recording_shown(blocks[0]))
    made = join_the_plan([{"blocks": blocks, "name": name}], tmpdir)[0]
    key = stage_key("finished", made["blocks"] + [ref_clip[0]])
    got = stage_get(key)
    if got is None:
        got = sound_places(name, made["source"], ref_clip[0],
                           ref_clip[1]["duration"], True)
        stage_put(key, list(got) if got else None)
    got = got and sound_or_clock(
        name, got, made["hint"],
        file_timecode(made["blocks"][0], ref_clip[1]["fps"]),
        list(clocks.values()),
        lambda tc: recording_at_its_clock(tc, position, clocks))
    if not got:
        print(as_bad(T('  The finished mix found no place on the time axis: '
                       'it shares no sound with the cameras. The run stops '
                       'rather than lay it anywhere.')))
        return False
    a, b, st, hint = got
    offset_line(name, a, st, hint)
    return {"name": name, "source": made["source"], "a": a, "b": b,
            "st": st, "blocks": made["blocks"], "hint": hint}


def finished_mix_onto_axis(args, finished, t0, t1, tmpdir):
    """Lay the finished mix onto the window from *t0* to *t1*.

    What it leaves silent at either end is said; one that has nothing
    in the window stops the run. A dry run measures, and writes nothing.
    Kept in args for distribute_tracks_to_cameras. False to stop.
    """
    args._finished = None
    if not finished:
        return True
    n = sample_count(finished["source"]) / float(SR)
    b0 = -finished["a"] / finished["b"]
    b1 = (n - finished["a"]) / finished["b"]
    if b1 <= t0 or b0 >= t1:
        print(as_bad(T('  The finished mix has nothing in the window from %s '
                       'to %s: it lies from %s to %s. The run stops.')
                     % (as_hms(t0), as_hms(t1), as_hms(max(0.0, b0)),
                        as_hms(max(0.0, b1)))))
        return False
    front, back = max(0.0, b0 - t0), max(0.0, t1 - b1)
    if max(front, back) > 0.25:
        print(as_warn(T('  The finished mix leaves %s at the front and %s '
                        'at the back of the window silent.')
                      % (as_hms(front), as_hms(back))))
    if args.dry_run:
        return True
    finished["drift"] = (not getattr(args, "no_drift", False)
                         and drift_clear(finished["b"], finished.get("st")))
    finished["axis"] = place_track_on_axis(
        finished["source"], os.path.join(tmpdir, "axis_finished_mix.wav"),
        finished["a"], finished["b"], t0, t1, finished["drift"])
    args._finished = finished
    return True


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
            print(T('  %s: %s, skipped') % (PROGRAM.camera_shown(v), e))
            continue
        # A camera with no sound but a clock goes on: align_cameras
        # places it by that clock. With neither, nothing can place it.
        if not info["audio"] and timecode_seconds(info) is None:
            print(T('  %s has no camera sound -- without it nothing can be '
                    'aligned') % PROGRAM.camera_shown(v))
            continue
        if known_frame_rate(file_frame_rate(info)) is None:
            # Said, not refused: the Timeline takes a rate Resolve has
            # and the file is converted into it. Which rate that is says
            # the note below, where every camera has been read.
            print(T('  %s runs at %s frames/s, a rate Resolve has no '
                    'Timeline for -- it is converted, not left out')
                  % (PROGRAM.camera_shown(v),
                     number_text(file_frame_rate(info), 3)))
        videos.append((v, info))
    if not any(i["audio"] for _v, i in videos):
        # Clocks alone are no axis: the tracks are laid against sound.
        videos = []
    if videos and not getattr(args, "production", ""):
        # The same name the ordinary path gives a production: the folder
        # the material sits in. Without it two jobs from two shoots
        # wrote the same handover and the second took the first's place.
        args.production = guess_production_name(videos[0][0])
    # The preset before the axis, so a wrong kind stops the run here. Two
    # recordings or more share one axis even without a picture or tick.
    stop = preset_before_the_axis(args, len(plan),
                                  bool(videos) or len(plan) > 1)
    if stop is not None:
        return stop
    if not videos:
        if video_paths:
            print(T('\nNo usable video file -- without camera audio there '
                    'is no common time axis.'))
            return 1
        if finished_mix_homeless(args):
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
        if len(made) > 1:
            # Several recordings and no picture: they are laid against
            # each other instead of against a camera, whatever the tick.
            return align_tracks_only(args, made, tmpdir, title)
        # One recording and no picture: its blocks become one file, and
        # that is the whole job.
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
                      % ", ".join(number_text(r, 3) for r in rates)))
        print(T('  The Timeline gets %s: the highest of them, or the '
                'next rate Resolve\n  has above it. Converted upwards '
                'Resolve repeats frames, downwards it\n  throws them '
                'away. Every camera keeps its own rate, and the cut '
                'counts\n  in that one.')
              % number_text(resolve_timeline_rate(
                  timeline_frame_rate(args, videos, None)), None))
    if len(sizes) > 1:
        print(as_head(T('\nDIFFERENT FRAME SIZES: %s') % ", ".join(sizes)))
        print(T('  Of no consequence for the sound.'))

    print(as_head(T('\nMEASURING THE TIME AXIS')))
    key = run_axis_key(args, plan, video_paths)
    kept = axis_raw_taken((stage_get(key) or {}).get("raw"), videos, plan)
    if kept:
        heard = kept[0]
        print(T('  Taken from the measurement kept on this machine: the '
                'same files and settings, so nothing is measured again.'))
    else:
        heard = cameras_heard(videos)
        # Before align_cameras lays the rest down by their clocks.
        raw = axis_raw(heard, videos)
    ref_clip, position = align_cameras(videos, heard)
    print(T('  Reference: %s (%s, longest running time)')
          % (PROGRAM.camera_shown(ref_clip[0]),
             as_hms(ref_clip[1]["duration"])))
    for v, info in videos:
        if v == ref_clip[0]:
            continue
        if v not in position:
            continue
        a, b, st = position[v]
        offset_line(PROGRAM.camera_shown(v), a, st, camera_hint(st))

    tmpdir = tempfile.mkdtemp(prefix="vpm_mt_")
    # A dozen paths leave this function before the folder is removed at the
    # end; without this a failed run keeps gigabytes of WAV.
    atexit.register(shutil.rmtree, tmpdir, True)
    joined = join_the_plan(plan, tmpdir)
    clocks = dict((v, timecode_seconds(i)) for v, i in videos)
    tracks, placings = tracks_placed(args, plan, joined, ref_clip, position,
                                     clocks, kept and kept[1])
    if not kept:
        # Only what was measured: the window works its view out of it,
        # and one it kept before is no longer this measurement's.
        for e, got in zip(plan, placings):
            if not e.get("from_camera"):
                part, head = raw_place(e.get("blocks") or [e["audio"]])
                raw[part][head] = got
        stage_put(key, {"raw": raw})
    if not tracks:
        print(T('\nNo audio track could be aligned -- there is nothing to '
                'put on the axis.'))
        return 1
    finished = finished_mix_placed(args, ref_clip, position, clocks, tmpdir)
    if finished is False:
        return 1
    # Where a clock and the measurement part, one line each: the window
    # says the same through the same function (clock_apart_lines).
    read = clocks_on_the_axis(videos, position, tracks, ref_clip)
    for line in clock_apart_lines(
            dict((c["name"], -c["a"] / c["b"]) for c in read),
            dict([(c["name"], c["tc"]) for c in read]
                 + [(PROGRAM.camera_shown(ref_clip[0]),
                     timecode_seconds(ref_clip[1]))]),
            PROGRAM.camera_shown(ref_clip[0]), ref_clip[1]["fps"]):
        print(line)

    # Window: what every camera saw, limited to what there is audio for.
    # Anything outside would be uploaded silence.
    camera_areas = []
    for v, info in videos:
        if v not in position:
            continue
        a, b, _ = position[v]
        camera_areas.append(((0.0 - a) / b, (info["duration"] - a) / b,
                             PROGRAM.camera_shown(v)))
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
        # And the other way round: what the recording loses outside the
        # window -- the question asked when the episode comes out shorter
        # than the recording.
        track["dropped_head"], track["dropped_tail"] = (max(0.0, t0 - b0),
                                                        max(0.0, b1 - t1))

    # Not a length in seconds: what decides is how many sample points the
    # alignment (one every couple of seconds) saw; a window with none says
    # nothing. One rule for both paths; the message carries the number.
    seen = min([st.get("points", 0) for v, (_a, _b, st) in position.items()
                if v != ref_clip[0]] or [0])
    if t1 - t0 <= 0 or (seen == 0 and t1 - t0 < AXIS_MIN_WINDOW_S):
        print(T('\nSound and picture have only %s in common, and the '
                'alignment found %s sample points in it. That is too '
                'little to place anything on.')
              % (as_hms(max(0, t1 - t0)), number_text(seen, 0)))
        return 1
    print(T('  Common window:       %s to %s (%s)')
          % (as_hms(t0), as_hms(t1), as_hms(t1 - t0)))
    # Name the two cameras that decide it. Without this the window is a
    # number nobody can check, and the question "why is my episode
    # shorter than the material" has no answer in the log.
    print(T('    it begins with %s and ends with %s -- the stretch every '
            'camera saw')
          % (late, early))
    dropped_said(tracks)
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
            return silence_sentence(shape % as_hms(point), how_much,
                                    run_uploads(args))
        if max(missing) - min(missing) < 15:
            print("  %s" % sentence(max(missing), points[missing.index(max(missing))]))
            return
        for name, how_much, point in zip(names, missing, points):
            if how_much > 1:
                print("  %-20s %s" % (name, sentence(how_much, point)))

    silence_report([max(0.0, b - t0) for b in starts], starts, T('up to %s'))
    silence_report([max(0.0, t1 - b) for b in ends], ends,
                   T('from %s'))

    tracks_onto_axis(args, tracks, t0, t1, tmpdir, "axis_%s.wav")
    if not finished_mix_onto_axis(args, finished, t0, t1, tmpdir):
        return 1

    # Who speaks when, before any upload or processing: the axis stands,
    # so a separation can be placed on it -- only on cameras that have a
    # place, as in the window; a file that sits nowhere gets no segments.
    if sync_only(args):
        # Sync only asks nobody who speaks: no separation is read, none
        # is made, and the cut further down has nothing to go by.
        args._speakers = None
    else:
        args._speakers = separation_for_run(
            args, tracks, position, t0, t1,
            [ref_clip[0]] + [v for v, _e in videos
                             if v != ref_clip[0] and v in position])

    #--------------------------------------------------- Processing
    # --auphonic-done first: its folder is an instruction about this run,
    # not a mode; the other order ignores it and mixes the raw recordings.
    rest = (args, tracks, cameras, videos, tmpdir, position, t0, t1,
            ref_clip)
    if getattr(args, "without_auphonic", False) and not args.auphonic_done:
        if args.dry_run:
            return dry_run_ends(*rest, axis=key)
        return finish_without_auphonic(*rest)
    if args.auphonic_done:
        # Already processed: the files are there. Saves a second upload and,
        # more to the point, the credit.
        if not processed_tracks_taken(
                args, tracks, tmpdir,
                dict((t["name"], t1 - t0) for t in tracks), full1 - full0,
                t0 - full0):
            return 1
        if args.dry_run:
            return dry_run_ends(*rest, axis=key)
        if not verify_returned_tracks(tracks, t1 - t0, tmpdir):
            return 1
        folder = os.path.abspath(args.auphonic_done)
        gain, curve = normalise_loudness(
            tracks, args.lufs, tmpdir,
            find_master_file(folder, args.out, os.path.dirname(video_paths[0])),
            channels=mix_width(tracks))
        return distribute_tracks_to_cameras(
            args, tracks, cameras, videos, tmpdir, gain, position, t0,
            ref_clip, t1, curve)

    folder = PROGRAM.output_folder(args, video_paths[0])
    # A dry run with a key says what would go up, and sends nothing.
    if args.auphonic_key or not args.dry_run:
        print()
        stop = send_to_auphonic(args, tracks, folder, tmpdir, t1 - t0, title)
        if stop is not None:
            return stop
    if args.dry_run:
        return dry_run_ends(*rest, axis=key)
    gain, curve = normalise_loudness(
        tracks, args.lufs, tmpdir,
        find_master_file(folder, args.out, os.path.dirname(video_paths[0])),
        channels=mix_width(tracks))
    return distribute_tracks_to_cameras(
        args, tracks, cameras, videos, tmpdir, gain, position, t0, ref_clip,
        t1, curve=curve)


def line_words(argv, plan=None):
    """What of a run's command line decides its handover: (words, plan).

    Out go --dry-run and the switches about auphonic.com -- asked or
    not, and what it returned -- which change the sound and not the cut;
    the plan file's path goes for what it holds -- *plan*, where the
    window has not written it yet. The cut numbers and In and Out stay.
    """
    words, rest = [], list(argv[1:])
    while rest:
        word = rest.pop(0)
        if word in ("--dry-run", "--without-auphonic"):
            continue
        if word in ("--auphonic-preset", "--auphonic-done", "--assign") \
                and rest:
            path = rest.pop(0)
            if word == "--assign":
                words.append(word)
                plan = plan if plan is not None else plan_read(path)
            continue
        words.append(word)
    return words, plan


def plan_read(path):
    """What an assignment file holds, or None where it cannot be read."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def handover_key(words, plan=None):
    """The name a dry run keeps its handover under: its line and plan.

    Out of line_words, so the window, which knows its line before
    anything is measured, finds what a dry run of that line worked out:
    the dict the run writes, less rendered files and tracks. Every file
    the line names goes in by place, time and size.
    """
    return stage_key("handover", [w for w in words if os.path.isfile(w)],
                     line=list(words), plan=plan)


def dry_run_ends(args, tracks, cameras, videos, tmpdir, position, t0, t1,
                 ref_clip, axis=None):
    """The rest of a dry run once the axis stands: who speaks, the cut.

    Everything a run works out before it writes, the handover included,
    and nothing it writes: no camera file, mix, single track or loudness,
    no upload, metrics, colour comparison or Resolve. A separation is
    only read where one is kept, and no speech is recognised. The level
    dips come from a sum of the raw tracks; *axis* is the axis's key.
    """
    sync = sync_only(args)
    segment_list, cut = [], []
    tc_start = programme_start(ref_clip, t0)
    if not sync:
        step_begin("speakers")
        segment_list = speakers_of_the_run(args, tracks, (t0, t1))
    step_begin("result")
    if not sync:
        levels = mix_tracks([t["axis"] for t in tracks],
                            os.path.join(tmpdir, "levels.wav"))
        work = cut_list_of(args, segment_list, tracks, cameras, videos,
                           tc_start, ref_clip, t1 - t0, sound_source=levels)
        cut, segment_list = ((work["cut"], work["segments"]) if work
                             else ([], []))
        roles_said(segment_list, ())
    # The handover with nothing written. With no camera file the offsets
    # are the sources', as one_camera takes them; the axis it stands on
    # goes with it, so a reader can tell it is still this material's.
    unplaceable, clocked = placing_notes(cameras, position)
    handover = handover_of(
        args, tracks, cameras, videos, tc_start, ref_clip, cut=cut,
        segment_list=segment_list, length=t1 - t0,
        offsets=ByFile((v, -a / b - t0) for v, (a, b, _s)
                       in position.items()),
        unplaceable=unplaceable, clocked=clocked)
    handover["axis_key"] = axis
    # The window hands its key in; any other line is read off sys.argv,
    # which the command line and the window's own run both set.
    stage_put(getattr(args, "_handover_key", None)
              or handover_key(*line_words(sys.argv)), handover)
    shutil.rmtree(tmpdir, ignore_errors=True)
    print(T('\n  (measuring only: nothing written)'))
    return 0


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
        fresh, cam = where_it_sounds(fresh, cam)
        k, g = cross_correlate(envelope(cam, HOP, rate),
                               envelope(fresh, HOP, rate))
    except Exception as e:
        print(T('  Check:           not possible (%s)') % e)
        return
    # Whether the number means anything: where the new track is mostly
    # silence the arithmetic answers all the same. A check that cries wolf
    # is worse than none, because it is read as evidence.
    if g < WEAK_MATCH:
        print(T('  Check:           the two tracks cannot be compared '
                '(match %s, %s is the floor). This says nothing '
                'about the timing.')
              % (number_text(g, 2), number_text(WEAK_MATCH, 2)))
        return
    ms = k * HOP
    off = abs(ms) > 1000.0 / fps
    line = (T('  Check:           %s against the camera track %s ms '
              '(match %s)%s')
            % (items[index_number][0], number_text(ms, 0, plus=True),
               number_text(g, 2),
               T('   Caution: more than one frame') if off else ""))
    print(as_warn(line) if off else line)


def finish_camera_file(source, info, target, items, args, fps,
                       measured=True):
    """Everything that happens to a camera file once it is written.

    The colour, the camera's own QuickTime keys, its metadata, and the
    measurement of whether the new audio sits on the picture -- not
    where *measured* is False: a camera its clock placed had no sound
    worth measuring. Four things in a fixed order.
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
    if measured:
        check_written_file(target, items, len(info["audio"]), args, fps)


def camera_targets(videos, names, out, suffix=""):
    """Where each camera's file is written: {video: (folder, file)}.

    One answer for the run, which writes there, and for the window,
    which asks before it writes over a file already lying at one.
    *names* holds the new names under path_key; a camera without one
    is named after its file. Without a name of its own it would write
    over an original, and two of one name would write one file at once.
    """
    targets, taken = {}, set()
    sources = set(os.path.abspath(v).lower() for v in videos)
    # The ending is always hung on: without it a camera's new name can
    # be its source's own stem, and beside it that is the source itself.
    tail = suffix or "_audio"
    for v in videos:
        v = os.path.abspath(v)
        stem = names.get(path_key(v)) or os.path.splitext(
            os.path.basename(v))[0]
        outdir = os.path.abspath(out) if out else os.path.dirname(v)
        target = os.path.join(outdir, stem + tail + ".mov")
        count = 1
        while target.lower() in sources or target.lower() in taken:
            count += 1
            # Plain digits, the way every other name this program writes
            # keeps them.
            target = os.path.join(outdir, "%s%s_%d.mov"
                                  % (stem, tail, count))
        taken.add(target.lower())
        targets[v] = (outdir, target)
    return targets


def written_before_here(folder, production):
    """What this production's own record says an earlier run wrote here.

    The handover file is the only honest answer to "did we make this?".
    A target standing in it is our own earlier delivery and may be
    replaced quietly; anything else at a target belongs to somebody,
    and a run about to walk over it has to say so out loud.
    """
    js = os.path.join(folder, "%s_resolve.json"
                      % safe_filename(production or 'Production'))
    if not os.path.exists(js):
        return set()
    try:
        with open(js, encoding="utf-8") as f:
            written = (json.load(f) or {}).get("cameras") or []
    except (OSError, ValueError) as e:
        print(T('  The record of earlier runs here cannot be read (%s), so '
                'everything already in place is reported.') % e)
        return set()
    # The record stands beside the lists it was written with, so a
    # readable one vouches for all six production files of its name.
    return (set(path_key(c["file"]) for c in written if c.get("file"))
            | set(path_key(p) for p in production_files(folder,
                                                        production)))


def production_files(folder, production):
    """The six files a run names after its production, in *folder*."""
    stem = os.path.join(folder, safe_filename(production or 'Production'))
    return [stem + end for end in ("_resolve.json", "_speakers.csv",
                                   "_speakers.edl", "_cameracut.csv",
                                   "_cameracut.edl", "_metrics.csv")]


def foreign_targets(targets, ours):
    """The targets a file is lying at that this production did not make.

    The one rule for writing over: the window asks about these and the
    run marks them, while our own earlier delivery goes quietly.
    """
    return [t for t in targets
            if os.path.exists(t) and path_key(t) not in ours]


def targets_to_ask(videos, names, out, production, suffix=""):
    """What a run would write over that the window has to ask about first.

    The camera files as camera_targets names them and the six production
    files, beside the first camera where no folder is given, the way
    the run places them; foreign_targets decides.
    """
    targets = [t for _o, t in camera_targets(videos, names, out,
                                             suffix).values()]
    folder = (os.path.abspath(out) if out else
              os.path.dirname(os.path.abspath(videos[0])) if videos
              else "")
    if folder:
        targets += production_files(folder, production)
    return foreign_targets(targets, written_before_here(folder, production)
                           if folder else set())


def replacement_lines(targets, ours):
    """What to say about targets a file is already lying at.

    Out here because it is a reading and nothing else, and a reading can
    be held against files without an hour of sound first. Our own
    earlier delivery goes quietly: running a production again is the
    everyday case, and a mark there would teach people to skip marks.
    Anything else is marked and named whole.
    """
    out, strange = [], set(foreign_targets(targets, ours))
    for target in targets:
        if not os.path.exists(target):
            continue
        if target not in strange:
            out.append(T('  %s is there from an earlier run of this '
                         'production and is replaced.')
                       % os.path.basename(target))
        else:
            out.append(as_bad(T('  %s is already there and is written over '
                                '-- this production has no record of making '
                                'it.') % target))
    return out


def key_frame_at_or_before(video, when):
    """Where the last key frame at or before *when* seconds sits.

    A stream copy starting between two key frames takes the picture from
    the one before while the sound starts where asked, a group of
    pictures apart. So the cut goes back, never forward; 0.0 if none.
    """
    if when <= 0:
        return 0.0
    for reach in (10.0, 120.0, 1200.0):
        begin = max(0.0, when - reach)
        try:
            p = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "v:0",
                 "-skip_frame", "nokey", "-show_entries", "frame=pts_time",
                 "-of", "csv=p=0", "-read_intervals",
                 "%.3f%%%.3f" % (begin, when + 0.001), video],
                capture_output=True, timeout=300)
        except Exception as e:
            print(T('  Key frames of %s cannot be read (%s) -- the copy '
                    'starts at the beginning of the file.')
                  % (PROGRAM.camera_shown(video), str(e)[:60]))
            return 0.0
        found = []
        for line in p.stdout.decode("utf-8", "replace").splitlines():
            try:
                seconds = float(line.strip().rstrip(","))
            except ValueError:
                continue
            if seconds <= when + 1e-6:
                found.append(seconds)
        if found:
            return max(found)
        if begin <= 0:
            break
    return 0.0


def camera_window_cut(video, duration, offset, window_s):
    """Which stretch of a camera a time window leaves: (cut_at, keep_s).

    *offset* is where the camera's first frame sits in programme time.
    The copy starts on the key frame before the window, the end is cut
    where the window ends, and keep_s is None where neither end gives.
    """
    first = max(0.0, -offset - CAMERA_MARGIN_S)
    last = min(duration, window_s - offset + CAMERA_MARGIN_S)
    cut_at = key_frame_at_or_before(video, first)
    if cut_at <= 0 and last >= duration - 0.001:
        return 0.0, None
    return cut_at, max(1.0, last - cut_at)


def camera_stamp(info, cut_at, at_s):
    """The timecode a written camera file carries, or nothing.

    *at_s* is where its first frame sits on the wall clock, the reckoning
    every camera gets, written at this camera's own rate -- off the
    reference's clock, or from 00:00:00 where it has none. Without it
    the camera's own timecode is moved by the cut and stands alone.
    """
    fps = max(1.0, info.get("fps") or 30.0)
    if at_s is not None:
        return timecode_string(at_s, fps)
    return timecode_moved(info["tc"], cut_at, fps) if info.get("tc") else ""


def write_camera_file(video, info, audio_tracks, target, a, b, drift, args,
                 head_s=0, tail_s=0, cut_at=0.0, keep_s=None, at_s=None):
    """Write a new video file carrying several audio tracks.

    *audio_tracks* is [(name, path)]; all get the same offset and clock
    correction, so they stay as aligned as they were. *head_s* and
    *tail_s* trim samples front and back before the offset; *cut_at* and
    *keep_s* say which stretch of the camera is written.
    """
    kept = keep_s if keep_s else info["duration"] - cut_at
    n_video = int(round(kept * SR))
    if drift and abs(b - 1.0) > 1e-7:
        intro = rate_filter_chain(b) + ","
        k = int(round(a / b * SR))
    else:
        intro, k = "", int(round(a * SR))
    cut = ("atrim=start_sample=%d,asetpts=N/SR/TB," % k) if k > 0 else\
              ("adelay=delays=%dS:all=1," % (-k)) if k < 0 else ""
    cmd = ["ffmpeg", "-v", "warning", "-nostats"]
    # Both in front of the input, so they cut the camera alone: the
    # tracks that follow are inputs of their own.
    if cut_at > 0:
        cmd += ["-ss", "%.6f" % cut_at]
    if keep_s:
        cmd += ["-t", "%.6f" % keep_s]
    cmd += ["-i", video]
    chains, map_args = [], ["-map", "0:v"]
    for i, (_, file_path) in enumerate(audio_tracks):
        cmd += ["-i", file_path]
        edge = ""
        if head_s or tail_s:
            edge = ("atrim=start_sample=%d:end_sample=%d,asetpts=N/SR/TB,"
                    % (head_s, sample_count(file_path) - tail_s))
        chains.append("[%d:a]%s%s%sapad=whole_len=%d,atrim=end_sample=%d,"
                      "asetpts=N/SR/TB[t%d]"
                      % (i + 1, edge, intro, cut, n_video, n_video, i))
        map_args += ["-map", "[t%d]" % i]
    n_camera = 0
    if not args.no_camera_audio:
        for i in range(len(info["audio"])):
            map_args += ["-map", "0:a:%d" % i]
        n_camera = len(info["audio"])
    # Behind the audio, so every track above keeps its place.
    data_maps = data_track_maps(video)
    map_args += data_maps
    cmd += ["-filter_complex", ";".join(chains)] + map_args
    if data_maps:
        cmd += ["-c:d", "copy"]
    # use_metadata_tags keeps the camera's QuickTime keys, where Resolve
    # reads device and input colour space. No write_colr: a colr box
    # travels either way, and the switch invents 2/2/2 where none is.
    cmd += ["-c:v", "copy"] + colour_arguments(video)
    cmd += ["-map_metadata", "0", "-movflags", "+use_metadata_tags"]
    for i in range(len(audio_tracks)):
        cmd += ["-c:a:%d" % i, "pcm_s24le"]
    for i in range(n_camera):
        cmd += ["-c:a:%d" % (len(audio_tracks) + i), "copy"]
    for i, (name, _) in enumerate(audio_tracks):
        cmd += ["-metadata:s:a:%d" % i, "title=%s" % name,
                "-metadata:s:a:%d" % i, "handler_name=%s" % name,
                "-disposition:a:%d" % i, "default" if i == 0 else "0"]
        if args.speech_language:
            cmd += ["-metadata:s:a:%d" % i, "language=%s" % args.speech_language]
    for i in range(n_camera):
        nm = args.name_camera if n_camera == 1 else "%s %d" % (args.name_camera,
                                                               i + 1)
        j = len(audio_tracks) + i
        cmd += ["-metadata:s:a:%d" % j, "title=%s" % nm,
                "-metadata:s:a:%d" % j, "handler_name=%s" % nm,
                "-disposition:a:%d" % j, "0"]
        if args.speech_language_camera:
            cmd += ["-metadata:s:a:%d" % j, "language=%s" % args.speech_language_camera]
    stamp = camera_stamp(info, cut_at, at_s)
    if stamp:
        # ffmpeg carries the source timecode through unchanged however
        # much is cut off the front, so the real start is written here.
        cmd += ["-timecode", stamp]
    cmd += ["-y", target]
    PROGRAM.run_ffmpeg_with_progress(
        cmd, kept, T('Writing %s') % os.path.basename(target))


def camera_drift(args, b, st, info):
    """Whether a camera's clock drift is taken out, and the line saying so.

    The rule is drift_clear's, the one every recording answers to, with
    one bound of the camera's own. The line gives the drift over the
    running time and, where it stays in, why.
    """
    fps = max(1.0, info["fps"])
    total = (b - 1.0) * info["duration"]
    ppm = (b - 1.0) * 1e6
    # 500 ppm is 1.8 s an hour: rather a failed measurement than a clock.
    # No floor for length (120 s) or effect (10 ms, half a frame): the
    # picture is copied (write_camera_file, -c:v copy), only sound stretched.
    if args.no_drift or abs(b - 1.0) <= 1e-7:
        drift, why = False, T('is left in')
    elif abs(ppm) >= 500:
        drift, why = False, T('is left in: %s ppm or more is rather a '
                              'measuring error') % number_text(500, 0)
    elif not drift_clear(b, st):
        drift, why = False, T('is left in: not %s times its '
                              'uncertainty') % number_text(DRIFT_OVER_ERROR, 0)
    else:
        drift, why = True, T('is actively taken out')
    return drift, (T('  Drift over the running time: %s s = %s frames  -->  %s')
                   % (number_text(total, 3, plus=True),
                      number_text(abs(total) * fps), why))


def distribute_tracks_to_cameras(args, tracks, cameras, videos, tmpdir, gain,
              position, t0, ref_clip=None, t1=None, curve=None,
              segment_list=None):
    """Place the processed tracks onto the cameras.

    Without *segment_list* the speakers are worked out here, off the raw
    tracks on the axis; what auphonic.com returned is only the sound.
    """
    step_begin("cameras")
    sync = sync_only(args)
    if segment_list is None and sync:
        segment_list = []
    elif segment_list is None:
        step_begin("speakers")
        segment_list = speakers_of_the_run(
            args, tracks, (t0, t1) if t1 is not None else None)
    names_every = [track["name"] for track in tracks]
    after_camera = ByFile(tracks_per_camera(tracks))

    track_names = ByFile()    # output file -> names of its audio tracks
    offsets = ByFile()        # output file -> measured offset in seconds
    print(as_head(T('\nMIXING')))
    # Mixes of several tracks go out in two channels, single tracks with
    # as many as recorded: the mix is delivered and measured, the single
    # track worked with in the edit. One recording: nothing mixed or widened.
    wide = mix_width(tracks)
    finished = getattr(args, "_finished", None)
    if finished:
        # Finished elsewhere, so taken as it came: no gain, no limiter.
        full_mix = finished["axis"]
        print(T('  Full-Mix: the finished mix, as it came -- no gain on '
                'it and no limiter'))
    else:
        full_mix = mix_tracks([track["ready"] for track in tracks],
                              os.path.join(tmpdir, "mix_full.wav"), gain,
                              curve, channels=wide)
        print(TN(wide, '  Full-Mix from %s tracks, %s channel',
                 '  Full-Mix from %s tracks, %s channels')
              % (number_text(len(tracks), 0), number_text(wide, 0)))

    # What is said and when, from the finished mix, beside the cameras:
    # the words are needed only when the cut is built, and without them
    # the wide shot looks for the longest pause, not a sentence's end.
    heard = {}

    def listen_to_the_mix():
        """Write down the words of the mix, in a thread of its own."""
        words, _way = recognise_speech(
            full_mix, getattr(args, "speech_language", "") or "")
        heard["words"] = words or []

    listening = None
    if not sync and not getattr(args, "no_speech_recognition", False):
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
    # Filled from a ByFile's keys and read back under abspath, so a ByFile
    # too. A plain dict breaks on Windows: the spellings differ, the lookup
    # raises, and every camera with a track goes unwritten without a word.
    camera_mix = ByFile()
    for file_path, own in after_camera.items():
        camera_mix[file_path] = mix_tracks(
            [track["ready"] for track in own],
            os.path.join(tmpdir, "mix_%s.wav"
                         % safe_filename(os.path.basename(file_path))), gain,
            curve, channels=mix_width(own))
        print(T('  %s: %s mixed together')
              % (PROGRAM.camera_shown(file_path),
                 " + ".join(track["name"] for track in own)))

    # path_key on both sides: a camera path in another shape than in the
    # video list loses its name, is written under the bare file name, and
    # then misses its measured offset, kept under the file written.
    output_name = {path_key(cam["video"]): cam["name"] for cam in cameras}
    # The target names are settled before the threads start, and by the
    # function the window asks before it offers to write over them.
    output_path = camera_targets([_v for _v, _i in videos], output_name,
                                 args.out, args.suffix)
    # Up here rather than beside the tracks it also names: what a target
    # would replace is asked of the record lying in it.
    folder = PROGRAM.output_folder(args, videos and videos[0][0])
    # Before the first camera is written, so a run about to walk over
    # somebody's file can still be stopped.
    for line in replacement_lines(
            [p for _o, p in output_path.values()],
            written_before_here(folder,
                                getattr(args, "production", ""))):
        print(line)
    results, error = [], 0
    lengths = ByFile()    # output file -> running time delivered
    written = ByFile()    # camera source -> the file written of it
    # An In or Out point is what makes the cameras carry a stretch
    # rather than the whole shoot. Without one they stay as they were,
    # so a run that sets no window writes exactly what it wrote before.
    window_s = (t1 - t0 if t1 is not None
                and ((getattr(args, "in_point", None) or "").strip()
                     or (getattr(args, "out_point", None) or "").strip())
                else None)
    tc_start = programme_start(ref_clip, t0)
    # No clock on the reference: every camera is stamped by its measured
    # place from 00:00:00 at the first frame any camera shows, never by
    # its own clock, which may be the one set wrong.
    stamp_from = tc_start
    if stamp_from is None and t0 is not None:
        stamp_from = -min([-position[v][0] / position[v][1] - t0
                           for v, _i in videos if v in position] + [0.0])

    def one_camera(v, info, share):
        """Finish one camera: measure, write, verify.

        Runs in its own thread. Everything printed here collects in that
        thread's buffer and comes out in one piece once the file is
        done; progress goes to the shared bar instead.
        """
        v = os.path.abspath(v)
        own = after_camera.get(v, [])
        print(as_head(T('\nPROCESSING: %s') % PROGRAM.camera_shown(v)))
        items = []
        if own:
            items.append(('Mix ' + " + ".join(track["name"] for track in own)
                          if len(own) > 1 else own[0]["name"],
                          camera_mix[v]))
            if len(own) > 1:
                for track in own:
                    items.append((track["name"], single[track["name"]]))
            # The Full-Mix goes onto every camera, also onto the one that
            # carries every speaker: the manual promises it, and cut/ and
            # resolve/ look it up by name.
            items.append((MIX_TRACK_NAME, full_mix))
        else:
            items.append((MIX_TRACK_NAME, full_mix))
            # And the mix's recordings, each on its own line, so the edit
            # can reach one voice without importing more. Only where no
            # track has a camera: else the wide shot gets the mix alone.
            if (not after_camera and len(tracks) > 1
                    and not getattr(args, "no_single_tracks", False)):
                for track in tracks:
                    items.append((track["name"], single[track["name"]]))
        # The camera's place on the axis is known from building it. Measuring
        # again against a de-bled speaker track would be worse: it holds one
        # speaker, while the camera microphone hears them all.
        if v not in position:
            print(T('  This camera could not be placed -- skipped'))
            return None
        a_cam, b_cam, st = position[v]
        a = -a_cam / b_cam - t0
        b = 1.0 / b_cam
        # Cross-check: the same offset from the overall mix, which is the same
        # on every camera and holds the camera microphone's voices. Where the
        # routes disagree it should show here rather than on playback.
        share.segment(0.0, 0.30)
        check = next((p for n, p in items
                      if n.startswith(MIX_TRACK_NAME)),
                     items[0][1])
        clocked = bool(st.get("by_clock_only"))
        a2, st2, deviation = None, {}, None
        try:
            # A camera its clock placed: its sound was already found
            # unusable, and measured again it gives a number meaning nothing.
            if not clocked:
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
        drift, running = camera_drift(args, b, st, info)
        if clocked:
            print(T('  Offset:          %s   (from its timecode alone -- '
                    'its sound could not place it, so nothing is checked)')
                  % as_hms(a))
        else:
            print(T('  Offset:          %s   (from the camera comparison)')
                  % as_hms(a))
        if a2 is not None:
            serious = abs(deviation) > 1.0 / fps
            print(T('  Cross-check:     %s from the Full-Mix, deviation '
                    '%s ms (%s of %s points)%s')
                  % (as_hms(a2),
                     number_text(deviation * 1000.0, 0, plus=True),
                     number_text(st2.get("points", 0), 0),
                     number_text(st2.get("candidates", 0), 0),
                     T('   Caution: more than one frame') if serious else ""))
        # The reference is what the others were measured against, and a camera
        # placed by its clock was measured against nothing: printing "+0.00 ppm
        # (+/- 0.00), 0 of 0 points" would read as a measurement that is none.
        if ref_clip and path_key(ref_clip[0]) == path_key(v):
            print(T('  Clock drift:     nothing measured -- this is the '
                    'reference the others are held against'))
        elif not clocked and not drift_measured(st):
            print(T('  Clock drift:     not measured -- too few points of '
                    'its sound held for one'))
        elif not clocked:
            print(T('  Clock drift:     %s ppm (+/- %s), residual spread '
                    '%s ms, %s of %s points')
                  % (number_text((b - 1.0) * 1e6, 2, plus=True),
                     number_text(st.get("ppm_error", 0.0), 2),
                     number_text(st.get("spread_ms", 0.0)),
                     number_text(st.get("points", 0), 0),
                     number_text(st.get("candidates", 0) or 0, 0)))
            print(running)
        print()
        outdir, target = output_path[v]
        os.makedirs(outdir, exist_ok=True)
        # What lies outside In and Out point is in no cut, and on a long shoot
        # it is most of the file: the camera is written from the key frame
        # before the window to a margin past its end. Without a window, no cut.
        cut_at, keep_s = 0.0, None
        if window_s is not None:
            cut_at, keep_s = camera_window_cut(v, info["duration"], a,
                                               window_s)
            a += cut_at
        # Where this file's first frame sits on the wall clock. a is
        # the measured place of that frame in programme time, so this
        # is the one number every camera's stamp comes from.
        at_s = None if stamp_from is None else stamp_from + a
        share.segment(0.30, 0.85)
        try:
            write_camera_file(v, info, items, target, a, b, drift, args,
                              cut_at=cut_at, keep_s=keep_s, at_s=at_s)
        except PROGRAM.Stopped:
            # Stop is no writing error: it ends the run, not this camera.
            raise
        except Exception as e:
            print(as_bad(T('  Error while writing: %s') % e))
            # A full disk leaves a cut-short file under the finished
            # name, and from outside it looks like a result.
            PROGRAM.remove_quietly(target)
            return None
        track_names = [name for name, _ in items]
        # The track number names the track in the finished file -- what
        # the editor clicks on, not a count of anything. Plain digits.
        for i, (name, _) in enumerate(items, 1):
            print(T('  Audio track %d:   %s') % (i, name))
        if not args.no_camera_audio and info["audio"]:
            print(T('  Audio track %d:   %s') % (len(items) + 1,
                                              args.name_camera))
        stamp = camera_stamp(info, cut_at, at_s)
        if stamp:
            print(T('  Timecode:        %s') % stamp)
        if keep_s:
            print(T('  Time window:     %s of %s written, from %s of the '
                    'camera') % (as_hms(keep_s), as_hms(info["duration"]),
                                 as_hms(cut_at)))
        share.segment(0.85, 1.0)
        finish_camera_file(v, info, target, items, args, fps,
                           measured=not clocked)
        return target, track_names, a, (keep_s or info["duration"])

    # The expensive part is the cross-check, and that only computes. ffmpeg
    # merely copies the picture and waits on the disk. Together they saturate
    # a machine only with several files running at once.
    how_many = getattr(args, "parallel", 0) or min(
        len(videos), max(1, min(4, how_many_processors() // 2)))
    how_many = max(1, min(how_many, len(videos)))
    progress_bar = SharedProgressBar(T('Processing'), len(videos))

    def one(v, info):
        # A camera still queued when Stop came is not begun: with fewer
        # workers than cameras the pool starts it after the others end.
        if PROGRAM.stop_wanted():
            raise PROGRAM.Stopped(PROGRAM.RUN_STOP["at"])
        ident = threading.get_ident()
        THREAD_BUFFER[ident] = []
        THREAD_SHARE[ident] = Share(progress_bar, v)
        try:
            return one_camera(os.path.abspath(v), info, THREAD_SHARE[ident])
        except PROGRAM.Stopped:
            raise
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
                written[v] = target
    finally:
        sys.stdout = old_off
    progress_bar.stop()
    # Back in file order, not in the order of completion: each file is
    # found by the camera it was written of, never by where it landed.
    results = [written[v] for v, _ in videos if v in written]

    # --- keep the finished tracks, not only hidden inside the videos
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
            # Same field, same reason as above: the BWF header is a
            # file format, and a thousands mark in it is a broken file.
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
                 PROGRAM.camera_shown(ref_clip[0])))

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
    if sync:
        # Sync only: no cut list, no roles, no transcript. The plan said
        # so at the top; here the lists are simply empty, and the
        # metrics and the handover below take them as they are.
        cut, segment_list = [], []
    else:
        cut, segment_list = write_cut_list(
            args, segment_list, tracks, cameras, videos, folder, tc_start,
            ref_clip, t1 - t0 if t1 is not None else 0,
            words=heard_words(),
            sound_source=single_files.get(MIX_TRACK_NAME, ""),
            unwritten=[v for v, _ in videos if v not in written])
        roles_said(segment_list, heard_words())
        if not getattr(args, "no_transcript_file", False) and heard_words():
            print(as_head(T('\nTRANSCRIPT')))
            for path in write_transcript_files(
                    folder, safe_filename(args.production or 'Production'),
                    heard_words(), segment_list):
                print("  %s" % path)
    # Content and wide shot only: the comparison shows what a cut between
    # two cameras looks like, and a file never cut against them does not
    # belong -- an 18 s jingle raised 357 steps of brightness (31.8.2026).
    placed_cameras = {path_key(k) for k in (position or {})}
    at_the_edges = set(path_key(p) for p in
                       (getattr(args, "intro", None), getattr(args, "outro", None))
                       if p)

    def cut_against_the_others(cam):
        where = path_key(cam.get("video") or "")
        return where in placed_cameras and where not in at_the_edges

    colours = []
    if not getattr(args, "no_metrics", False):
        # Each camera beside its own written file, found by the camera
        # and never by place; with one camera unwritten, all by source.
        whole = len(results) == len(cameras)
        try:
            colours = report_picture_comparison(
                [{"track": cam.get("name"),
                  "file": (written.get(cam.get("video") or "",
                                       cam.get("video")) if whole
                           else cam.get("video"))}
                 for cam in cameras if cut_against_the_others(cam)])
        except Exception as e:
            print(T('  Colour comparison not possible: %s') % e)
        print(as_head(T('\nMETRICS')))
        target = write_metrics_csv(
            os.path.join(folder, "%s_metrics.csv"
                         % safe_filename(args.production or 'Production')),
            tracks, cut, segment_list, cameras, args, colours, gain)
        if target:
            print("  %s" % target)
    # The Resolve build's code is the run's: a track Resolve refused
    # twice or a camera it would not insert is no finished project, and
    # thrown away here the run would end in 0 and the window say Done.
    unplaceable, clocked = placing_notes(cameras, position)
    if write_handover(args, tracks, cameras, videos, folder, tc_start,
                      ref_clip, results, cut, segment_list,
                      t1 - t0 if t1 is not None else 0, track_names,
                      single_files, offsets, lengths, words=heard_words(),
                      unplaceable=unplaceable, clocked=clocked):
        error += 1
    shutil.rmtree(tmpdir, ignore_errors=True)
    return 1 if error else 0
