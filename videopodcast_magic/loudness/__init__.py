# -*- coding: utf-8 -*-
"""Loudness and mixing: measured, matched, limited, and summed into one.

EBU R128 measured by ffmpeg, the speakers brought to one level, the
whole brought to a target under a true-peak ceiling, and the tracks
summed into a mix. A piece of the program, read in by beside(): it
cannot import the file it was cut out of, so the program is handed in
and every name used out of it is bound below.
"""

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# What this piece uses out of the program, bound once. Read after the
# material, whose channel names five of these are; the cut and the time
# base, read after it, bind its names at their heads.

MIX_TRACK_NAME = PROGRAM.MIX_TRACK_NAME
SR = PROGRAM.SR
T = PROGRAM.T
as_head = PROGRAM.as_head
as_warn = PROGRAM.as_warn
bext_time_reference = PROGRAM.bext_time_reference
channel_count = PROGRAM.channel_count
channel_filter = PROGRAM.channel_filter
kept_channels = PROGRAM.kept_channels
math = PROGRAM.math
number_text = PROGRAM.number_text
os = PROGRAM.os
progress_from_line = PROGRAM.progress_from_line
re = PROGRAM.re
remove_quietly = PROGRAM.remove_quietly
safe_filename = PROGRAM.safe_filename
sample_count = PROGRAM.sample_count
show_progress = PROGRAM.show_progress
subprocess = PROGRAM.subprocess
sys = PROGRAM.sys
tempfile = PROGRAM.tempfile
wav_safe = PROGRAM.wav_safe
widest_track = PROGRAM.widest_track

# Two are read at the use instead: OUTPUT_SINK, which the window sets on
# the program object without telling the pieces, and run_ffmpeg_with_progress,
# whose piece is read after this one.


# numpy is fetched by the program on the first sum, which a copy taken
# up there would miss; this asks the program instead, the same way.
class LateNumpy:
    """Stands in for the program's numpy until a sum wants it."""

    def __getattr__(self, name):
        """The name asked for, off the program's numpy, which is kept."""
        global np
        got = getattr(PROGRAM.np, name)
        np = PROGRAM.np
        return got


np = LateNumpy()


# What the loudness may come to, and how much of it the limiter may
# take off. Nothing else in the program reads either one.
CEILING_DBTP = -1.0       # true-peak ceiling of the result
LIMIT_MAX_DB = 6.0        # most the limiter may take off
SPEAKER_FLOOR_LUFS = -50.0  # under it a track carries no voice to match


def measure_loudness(file_path, duration=None, text_progress_bar=None):
    """Measure programme loudness and true peak to EBU R128."""
    cmd = ["ffmpeg", "-nostats", "-i", file_path, "-af", "ebur128=peak=true",
           "-f", "null", "-"]
    if not text_progress_bar:
        p = subprocess.run(cmd, capture_output=True)
        text = p.stderr.decode("utf-8", "replace")
    else:
        # ebur128 writes one line per second to stderr, so reading stdout
        # first would fill its buffer: stderr goes to a file, not a pipe.
        cmd = cmd[:1] + ["-progress", "pipe:1"] + cmd[1:]
        fd, log = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        try:
            with open(log, "wb") as f:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=f)
                show_progress(text_progress_bar, 0.0)
                for line in proc.stdout:
                    share = progress_from_line(line, duration)
                    if share is not None:
                        show_progress(text_progress_bar, share)
                proc.wait()
            with open(log, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        finally:
            try:
                os.unlink(log)
            except OSError:
                pass
        show_progress(text_progress_bar, 1.0)
        if PROGRAM.OUTPUT_SINK:
            PROGRAM.OUTPUT_SINK("\n")
        else:
            sys.stdout.write("\n")
    def get(label):
        hit = re.findall(label + r":\s*(-?\d+(?:\.\d+)?)", text)
        return float(hit[-1]) if hit else None
    # LRA comes from the same pass: how far quiet and loud passages lie
    # apart. For speech 3 to 7 LU is usual; below that it sounds squashed.
    return get(r"I"), get(r"Peak"), get(r"LRA")


def match_speakers(tracks, tmpdir):
    """Bring the speaker tracks to one level, each with a gain of its own.

    Only where auphonic.com set no balance: one common gain keeps voices
    six decibels apart six apart. Each is measured as normalise_loudness
    does and moved to the voices' median; one under SPEAKER_FLOOR_LUFS
    has no voice and stays: lifting silence lifts only noise. The moved
    copy is its "ready". Returns [(name, LUFS, gain dB)], per track in order.
    """
    if len(tracks) < 2:
        return [(track["name"], None, 0.0) for track in tracks]
    print(as_head(T('\nSPEAKER LEVELS')))
    heard = []
    for track in tracks:
        have, _peak, _lra = measure_loudness(
            track["ready"], sample_count(track["ready"]) / float(SR),
            T('Measuring %s') % track["name"])
        heard.append(have)
    voices = sorted(have for have in heard
                    if have is not None and have > SPEAKER_FLOOR_LUFS)
    # The median: the fewest decibels moved in all, and one quiet
    # microphone drags nobody else down with it.
    middle = len(voices) // 2
    level = None
    if len(voices) >= 2:
        level = (voices[middle] if len(voices) % 2
                 else (voices[middle - 1] + voices[middle]) / 2.0)
    moved = []
    for track, have in zip(tracks, heard):
        gain = 0.0
        if have is None:
            print(T('  %-20s not measurable -- left as it is')
                  % track["name"])
        elif have <= SPEAKER_FLOOR_LUFS:
            print(T('  %-20s %s LUFS -- nothing on it, left as it is')
                  % (track["name"], number_text(have, 1)))
        else:
            if level is not None:
                gain = level - have
            print(T('  %-20s %s LUFS  ->  %s dB')
                  % (track["name"], number_text(have, 1),
                     number_text(gain, 1, plus=True)))
            track["ready"] = mix_tracks(
                [track["ready"]],
                os.path.join(tmpdir, "level_%s.wav"
                             % safe_filename(track["name"])),
                gain, None, channels=kept_channels(track["ready"]))
        moved.append((track["name"], have, gain))
    if level is None:
        print(T('  Only one voice -- nothing to match it against.'))
    else:
        print(T('  Common level:      %s LUFS, the median of the voices')
              % number_text(level, 1))
    return moved


def normalise_loudness(tracks, target_lufs, tmpdir, master=None, channels=1):
    """Compute one common gain for all tracks.

    The sum is measured, not the single track, and the same gain goes on
    every track so the speakers keep their balance -- set by auphonic.com,
    or by match_speakers on the path without it. The finished mixdown is
    the yardstick; *target_lufs* None still measures.
    """
    print(as_head(T('\nNORMALISE')))
    keep = target_lufs is None
    after_yardstick = False
    if master and os.path.exists(master) and not keep:
        m_have, m_peak, _m_lra = measure_loudness(master, None, T('Measuring the '
                                                                  'yardstick'))
        if m_have is not None:
            after_yardstick = True
            print(T('  Mixdown from auphonic.com: %s LUFS, peak %s '
                    'dBTP (%s)')
                  % (number_text(m_have, 1),
                     number_text(m_peak if m_peak is not None else 0.0, 1),
                     os.path.basename(master)))
            target_lufs = m_have
    total_sum = os.path.join(tmpdir, "measure_sum.wav")
    ready = [track["ready"] for track in tracks]
    # Measured in the form it is delivered in: a two channel mix sits a
    # good three decibels above the same mix as one track, and a stereo
    # track raises the count on its own.
    channels = max(channels, widest_track(ready))
    parts, chains, markers = [], [], []
    for i, path in enumerate(ready):
        parts += ["-i", path]
        chains.append("[%d:a]%s[m%d]"
                      % (i, channel_filter(kept_channels(path), channels), i))
        markers.append("[m%d]" % i)
    fc = ";".join(chains) + ";" + "".join(markers) +\
        "amix=inputs=%d:normalize=0[out]" % len(markers)
    duration = sample_count(tracks[0]["ready"]) / float(SR)
    # One track with nothing to do to its channels is its own sum, and
    # summing it copies hours of audio for the same samples. *ours* says
    # whether this run made the file -- only then may it be deleted.
    ours = not (len(ready) == 1 and "anull" in chains[0])
    measured_on = total_sum if ours else ready[0]
    if ours:
        PROGRAM.run_ffmpeg_with_progress(
            ["ffmpeg", "-v", "error"] + parts + ["-filter_complex", fc,
             "-map", "[out]", "-c:a", "pcm_s24le"]
                + wav_safe(total_sum) + ["-y", total_sum],
            duration, T('Building the sum'))
    have, peak, lra_range = measure_loudness(measured_on, duration,
                                            T('Measuring loudness'))
    if have is None:
        print(T('  Loudness not measurable -- it stays as it is.'))
        return 0.0, None
    if keep:
        print(T('  Sum of tracks:     %s LUFS, peak %s dBTP%s')
              % (number_text(have, 1),
                 number_text(peak if peak is not None else 0.0, 1),
                 T(', range %s LU') % number_text(lra_range, 1)
                 if lra_range is not None else ""))
        print(T('  Not adjusted:      taken from the source files -- no gain '
                'on any track and no\n                     limiter. The '
                'sound leaves exactly as it came in.'))
        if ours:
            remove_quietly(total_sum)
        return 0.0, None
    gain = target_lufs - have
    print(T('  Sum of tracks:     %s LUFS, peak %s dBTP%s')
          % (number_text(have, 1),
             number_text(peak if peak is not None else 0.0, 1),
             T(', range %s LU') % number_text(lra_range, 1)
             if lra_range is not None else ""))
    print(T('  Target:            %s LUFS  ->  %s dB on every track')
          % (number_text(target_lufs, 1),
             number_text(gain, 1, plus=True)))
    # Without a ceiling the gain would have to drop for the loudest peak
    # alone -- a scraping chair costs eight decibels. So a limiter.
    if peak is not None and gain > CEILING_DBTP - peak:
        print(T('  Peaks:             %s dB above %s dBTP -- the '
                'limiter catches them')
              % (number_text(peak + gain - CEILING_DBTP, 1, plus=True),
                 number_text(CEILING_DBTP, 1)))
    # How much the limiter takes off is known only once the curve is
    # computed. More than a handful of decibels means the target does not
    # fit the material, and then quieter beats squashed.
    curve, gone = limiter_curve(measured_on, tmpdir, gain)
    # With the finished mixdown from auphonic.com beside it, that is how
    # much limiting it needed itself, so nothing here needs capping.
    limit = 12.0 if after_yardstick else LIMIT_MAX_DB
    if gone > limit + 0.05:
        back = gone - limit
        print(T('  Too much:          the limiter would have to take %s '
                'dB away. More than %s dB\n                     sounds '
                'squashed -- %s dB less gain.')
              % (number_text(gone, 1), number_text(limit, 0),
                 number_text(back, 1)))
        gain -= back
        curve, gone = limiter_curve(measured_on, tmpdir, gain)
        print(T('  Remains:           %s dB on every track, that is '
                '%s LUFS instead of %s')
              % (number_text(gain, 1, plus=True),
                 number_text(have + gain, 1),
                 number_text(target_lufs, 1)))
    if gone > 0.05:
        print(T('  Limiter:           at most %s dB, the same curve on '
                'every track%s')
              % (number_text(gone, 1),
                 T(' (auphonic.com takes the same amount)')
                 if after_yardstick else ""))
    # For checking in the editor. -16 LUFS is the figure for web and
    # podcast; broadcast measures against -23 and the meter reads higher.
    print(T('  Result:            about %s LUFS, peak %s dBTP')
          % (number_text(have + gain, 1),
             number_text(CEILING_DBTP if gone > 0.05
                         else min(CEILING_DBTP, (peak or 0.0) + gain), 1)))
    # The loudness range measures whether any dynamics are left, and
    # where it gets small something before the limiter squashed it.
    if lra_range is not None:
        if lra_range < 2.0:
            print(as_warn(T('  Caution: range      only %s LU -- very '
                            'tight. Speech is usually 3 to 7 LU;\n          '
                            '           below that it sounds squashed. '
                            'Check how strongly the leveler\n               '
                            '      is set at auphonic.com.')
                          % number_text(lra_range, 1)))
        else:
            print(T('  Range:             %s LU (speech is usually 3 to '
                    '7 LU)') % number_text(lra_range, 1))
    if ours:
        remove_quietly(total_sum)
    return gain, curve


def limiter_curve(total_sum, tmpdir, gain, ceiling=CEILING_DBTP):
    """Compute the limiter gain curve once, on the sum.

    The same curve goes on every track, so they add up to exactly the mix
    again: (a+b)*g equals a*g + b*g, where a limiter per track would
    clamp the loud one harder. Block by block with one block of lookahead
    and a linear cross-fade, or it clicks. Returns (path, reduction dB).
    """
    if np is None:
        return None, 0.0
    channels = max(1, channel_count(total_sum))
    limit = 10.0 ** (ceiling / 20.0)
    BLOCK = 256                       # 5.3 ms at 48 kHz
    RECOVERY = math.exp(-BLOCK / (SR * 0.050))    # 50 ms back up
    source = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", total_sum,
         "-af", "volume=%.3fdB" % gain,
         "-f", "f32le", "-ac", str(channels), "-ar", str(SR), "-"],
        stdout=subprocess.PIPE)
    raw = os.path.join(tmpdir, "level_curve.raw")
    target = os.path.join(tmpdir, "level_curve.wav")
    # No status before the first block: it starts where it must, or a
    # peak in the first 5 ms goes through at full gain.
    smallest, status, rest, done = 1.0, None, b"", False
    frame_bytes = 4 * channels
    try:
        with open(raw, "wb") as f:
            while not done:
                chunk = source.stdout.read(1 << 20)
                done = not chunk
                data = rest + chunk
                whole_blocks = len(data) // (frame_bytes * BLOCK)
                if not done:
                    # The last block waits for the next chunk: without
                    # it the peak comes through a tenth of a second early.
                    whole_blocks = max(0, whole_blocks - 1)
                    full = whole_blocks * frame_bytes * BLOCK
                else:
                    full = len(data) - len(data) % frame_bytes
                rest = data[full:]
                if full <= 0:
                    continue
                # The block kept back is read too, as the lookahead of the
                # last one here, or a peak just after a seam goes through.
                seen = full if done else full + frame_bytes * BLOCK
                frames = np.frombuffer(data[:seen],
                                       dtype="<f4").reshape(-1, channels)
                n = full // frame_bytes
                count = int(math.ceil(n / float(BLOCK)))
                blocks = int(math.ceil(frames.shape[0] / float(BLOCK)))
                needed = np.ones(blocks, dtype=np.float64)
                for k in range(blocks):
                    piece = frames[k * BLOCK:(k + 1) * BLOCK]
                    peak = (float(np.max(np.abs(piece)))
                              if piece.size else 0.0)
                    if peak > limit:
                        needed[k] = limit / peak
                # One block of lookahead: the reduction is in place first.
                before = np.minimum(needed, np.append(needed[1:], needed[-1]))
                status = before[0] if status is None else status
                g = np.empty(n, dtype=np.float32)
                for k in range(count):
                    want = before[k]
                    if want > status:      # back up, but slowly
                        want = min(want, status * RECOVERY + (1.0 - RECOVERY))
                    a0 = k * BLOCK
                    a1 = min(n, a0 + BLOCK)
                    g[a0:a1] = np.linspace(status, want, a1 - a0,
                                           endpoint=False)
                    status = want
                    smallest = min(smallest, want)
                f.write((np.repeat(g, channels) if channels > 1 else g)
                        .astype("<f4").tobytes())
    except Exception as e:
        print(T('  Level curve not possible (%s) -- without limiter') % e)
        return None, 0.0
    finally:
        try:
            source.stdout.close()
            source.wait(timeout=30)
        except Exception:
            pass
    gone = -20.0 * math.log10(max(1e-6, smallest))
    if gone <= 0.001:
        try:
            os.unlink(raw)
        except OSError:
            pass
        return None, 0.0
    try:
        subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le",
                        "-ar", str(SR), "-ac", str(channels), "-i", raw,
                        "-c:a", "pcm_f32le"]
                            + wav_safe(target)
                            + ["-y", target], check=True)
        os.unlink(raw)
    except Exception as e:
        print(T('  Level curve not possible (%s) -- without limiter') % e)
        return None, 0.0
    return target, gone


def mix_width(tracks):
    """How many channels a mix of these tracks is delivered in.

    Two where there are several, that being the form a mix is delivered
    in. One recording is the exception -- nothing to mix, so nothing is
    widened. A stereo source raises the count on its own either way.
    """
    if len(tracks) > 1:
        return 2
    return max(1, widest_track([track.get("ready") or track.get("axis")
                                for track in tracks])) if tracks else 1


def mix_tracks(sources, target, gain=0.0, curve=None, channels=1):
    """Sum several equally long tracks into one.

    Gain and limiter curve are the same for all tracks, so the single
    tracks add up to exactly the mix again. The widening happens before
    the sum and by "c1=c0" -- a plain conversion loses three decibels.
    """
    have = [kept_channels(p) for p in sources]
    channels = max(channels, max(have) if have else 1)
    if (len(sources) == 1 and abs(gain) < 0.01 and not curve
            and have[0] == channels):
        return sources[0]
    parts, chains, markers = [], [], []
    for i, path in enumerate(sources):
        parts += ["-i", path]
        chains.append("[%d:a]%s[m%d]"
                      % (i, channel_filter(have[i], channels), i))
        markers.append("[m%d]" % i)
    fc = ";".join(chains) + ";" + "".join(markers) +\
        "amix=inputs=%d:normalize=0" % len(markers)
    if abs(gain) >= 0.01:
        fc += ",volume=%.3fdB" % gain
    if curve:
        # The same gain curve as on all other tracks, hence a second
        # input: ffmpeg's equal-power law would cost another 3 dB.
        fc += "[both]"
        parts += ["-i", curve]
        fc += ";[both]aformat=sample_fmts=fltp:sample_rates=%d[gm];" % SR
        fc += "[%d:a]%s,aformat=sample_fmts=fltp:sample_rates=%d[gc];" % (
            len(sources), channel_filter(kept_channels(curve), channels), SR)
        fc += "[gm][gc]amultiply[out]"
    else:
        fc += "[out]"
    # The clock of the first source goes with the mix: without it the
    # levelled file has no timecode, and a recording with no clock
    # cannot be placed against anything afterwards.
    clock = []
    start = bext_time_reference(sources[0])
    if start is not None:
        clock = ["-write_bext", "1", "-metadata",
                 "time_reference=%d" % int(round(start))]
    PROGRAM.run_ffmpeg_with_progress(
        ["ffmpeg", "-v", "error"] + parts + ["-filter_complex", fc,
         "-map", "[out]", "-c:a", "pcm_s24le"] + clock
        + wav_safe(target) + ["-y", target],
        sample_count(sources[0]) / float(SR),
        T('Mixing %s') % mixing_label(target))
    return target


def mixing_label(target):
    """The name the progress line gives a mix: the track, not the file.

    The targets are mix_full, single_<speaker> and mix_<camera file>.
    Only the overall mix is announced as the mix, and only a leading
    prefix comes off: replacing "full" and "mix_" anywhere announced a
    speaker Carefully as CareFull-Mixy. The overall mix is asked for
    first, or a speaker called full would be announced as the mix again.
    """
    stem = os.path.splitext(os.path.basename(target))[0]
    if stem == "mix_full":
        return MIX_TRACK_NAME
    for prefix in ("mix_", "single_"):
        if stem.startswith(prefix):
            return stem[len(prefix):]
    return stem
