# -*- coding: utf-8 -*-
"""A camera whose audio is in use is an audio file like any other.

The field on the video file says no more than "use the audio"; the same
measurement as for a recorder file decides what it becomes. The sound is
offered twice, inside the camera and as a recording beside it, for the
same verdict and the same tracks; the cutting carries the rate over and
each channel into a piece of its own. Nothing chosen puts no camera in
the table, a chosen one goes in as a recording does, cut or whole. A
lone camera with sound is settled without being chosen, a track starts
on the camera it came out of, and the command line cuts what the
interface would. None of it goes through the interface itself.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import importlib.util, subprocess, sys, tempfile, time
import numpy as np
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
SR = vpm.SR
WORK = tempfile.mkdtemp(prefix="camerachannels_")
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def camera(name, seconds=6.0, rate=44100):
    """A short video whose two channels carry two different tones.

    44.1 kHz on purpose: cameras record at that rate and the run works at
    48, so the cutting has to bring the pieces over.
    """
    path = os.path.join(WORK, name)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y",
         "-f", "lavfi", "-i",
         "testsrc=size=320x180:rate=25:duration=%.1f" % seconds,
         "-f", "lavfi", "-i",
         "sine=frequency=500:sample_rate=%d:duration=%.1f" % (rate, seconds),
         "-f", "lavfi", "-i",
         "sine=frequency=900:sample_rate=%d:duration=%.1f" % (rate, seconds),
         "-filter_complex", "[1:a][2:a]join=inputs=2:channel_layout=stereo[o]",
         "-map", "0:v", "-map", "[o]",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le",
         path], check=True)
    return path


def sound_out_of(video, name, channels=2, rate=SR):
    """The audio of that video, on its own, as a recording would be.

    *rate* is 44.1 kHz where the piece stands for audio handed over
    straight out of a camera: at the run's rate the cutting has nothing
    to carry over, and a lost rate conversion would go unnoticed.
    """
    path = os.path.join(WORK, name)
    subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-map", "0:a:0",
                    "-ac", str(channels), "-ar", str(rate), "-c:a",
                    "pcm_s16le", "-y", path], check=True)
    return path


def pair_of(judged):
    """(how many pairs, what the first one says) -- and None where none is.

    Read out rather than indexed: where no pair was judged at all the
    indexing would end the file in a traceback, and a traceback carries
    neither the count nor a name.
    """
    return len(judged), (judged[0][1] if judged else None)


cam = camera("Camera1.mov")
other = camera("Camera2.mov")
check("the camera has two channels", vpm.channel_count(cam) == 2,
      "%d channels against 2" % vpm.channel_count(cam))
check("and records at 44.1 kHz", vpm.audio_shape(cam)[1] == 44100,
      "%d Hz against 44100" % vpm.audio_shape(cam)[1])

#----------------------------------------- the channels are judged as usual
facts = vpm.channel_facts_cached(cam)
check("a video's channels can be measured", facts.get("readable") is True,
      "readable %r against True, over %s channels"
      % (facts.get("readable"), facts.get("channels")))
pairs = vpm.channel_joins(facts)
how_many, first_says = pair_of(pairs)
check("one pair is judged", how_many == 1, "%d pairs against 1" % how_many)
check("two separate tones are not read as one stereo track",
      first_says is False,
      "stereo %r against False, over %d pairs" % (first_says, how_many))
want = vpm.tracks_to_split(cam, facts)
check("so the camera is cut into two tracks", len(want) == 2,
      "%d tracks against 2: %s" % (len(want), [chs for chs, _l in want]))

#------------------------- the same sound as a recording is judged the same
# The audio out of the camera and the audio in a file beside it are one
# and the same signal, so every step has to answer the same about both.
# Where they part company, "treated like a normal audio file" has
# stopped being true. Whether it really is the same signal is asked
# first: otherwise a red line below blames the program for material
# that never matched.
recorded = sound_out_of(cam, "Osmo_recording.wav")
check("the recording beside it is the same two channels",
      vpm.channel_count(recorded) == 2,
      "%d channels against 2, at %d Hz"
      % (vpm.channel_count(recorded), vpm.audio_shape(recorded)[1]))
facts_rec = vpm.channel_facts_cached(recorded)
check("the recording of it can be measured too",
      facts_rec.get("readable") is True,
      "readable %r against True, over %s channels"
      % (facts_rec.get("readable"), facts_rec.get("channels")))
pairs_rec = vpm.channel_joins(facts_rec)
rec_how_many, rec_first_says = pair_of(pairs_rec)
check("and its pair is judged the same way",
      rec_how_many == how_many and rec_first_says is first_says,
      "%d pairs against %d, stereo %r against %r"
      % (rec_how_many, how_many, rec_first_says, first_says))
want_rec = vpm.tracks_to_split(recorded, facts_rec)
check("camera and recording give the same number of tracks",
      len(want_rec) == len(want), "%d against %d" % (len(want_rec), len(want)))
check("and cut at the same channels",
      [chs for chs, _l in want_rec] == [chs for chs, _l in want],
      "%s against %s" % ([chs for chs, _l in want_rec],
                         [chs for chs, _l in want]))

#------------------------------------------------- cutting brings the rate over
def channels_of(path):
    """How many channels that file has; 0 where it cannot be read at all.

    The 0 is not swallowed: it is printed in the failure line, and the
    check before the caller has already named the piece that is missing.
    """
    try:
        return vpm.channel_count(path)
    except Exception:
        return 0


def cut(source, chs, refused):
    """Cut those channels out into a file of their own; the target either way.

    A cut that throws is counted rather than allowed to end the run:
    the file would otherwise stop before the line that says how many
    judgements it reached, which is the one line nobody can do without.
    """
    target = vpm.split_target(source, chs, WORK)
    try:
        vpm.split_channels(source, chs, target, rate=SR)
    except Exception:
        refused.append(target)
    return target


refused = []
pieces = [(cut(cam, chs, refused), label) for chs, label in want]
on_disk = [p for p, _l in pieces if os.path.exists(p) and os.path.getsize(p)]
check("both pieces are there", len(pieces) == 2 and len(on_disk) == 2,
      "%d pieces asked for, %d written, %d refused, want 2, 2 and 0"
      % (len(pieces), len(on_disk), len(refused)))
counts = [channels_of(p) for p in on_disk]
check("each holds one channel", counts == [1] * len(pieces),
      "%s against %s" % (counts, [1] * len(pieces)))
rates = [vpm.audio_shape(p)[1] for p in on_disk]
check("and both are at the run's sample rate", rates == [SR] * len(pieces),
      "%s against %s" % (rates, [SR] * len(pieces)))


def has_tone(path, hz):
    """How strong that tone is against the loudest one in the file.

    0.0 where there is no file to read or ffmpeg hands nothing back --
    the number is printed, so a missing piece shows as 0.00 in the
    failure line rather than ending the run in a traceback.
    """
    if not os.path.exists(path) or not os.path.getsize(path):
        return 0.0
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le",
                          "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True).stdout
    x = np.frombuffer(raw, dtype="<f4")
    if not len(x):
        return 0.0
    spectrum = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    k = int(round(hz * len(x) / float(SR)))
    return float(spectrum[k]) / (float(np.max(spectrum)) or 1.0)


def tone_of(which, hz):
    """How much of that tone is in piece *which*; 0.0 where it is missing."""
    return has_tone(pieces[which][0], hz) if which < len(pieces) else 0.0


one_500, one_900 = tone_of(0, 500), tone_of(0, 900)
two_900, two_500 = tone_of(1, 900), tone_of(1, 500)
check("the first piece is the first channel",
      one_500 > 0.9 and one_900 < 0.1,
      "500 Hz %.2f against > 0.90, 900 Hz %.2f against < 0.10"
      % (one_500, one_900))
check("the second the other one", two_900 > 0.9 and two_500 < 0.1,
      "900 Hz %.2f against > 0.90, 500 Hz %.2f against < 0.10"
      % (two_900, two_500))

#--------------------------------------- no choice made: no sound from a camera
# With nothing chosen the cameras are not in the table at all. Two
# cameras, three of them and a camera beside a recording are asked
# separately: a program deciding by itself turns on those numbers.
def cut_into(plan):
    """A split_of that cuts the named files and nothing else."""
    wanted = {os.path.abspath(k): v for k, v in plan.items()}
    return lambda x: wanted.get(os.path.abspath(x), [])


def uncut(_x):
    """A split_of that cuts nothing at all."""
    return []


def named(rows):
    """The file each row starts with, by name, in order."""
    return [os.path.basename(row[0]) for row, _discarded in rows]


rows, _flag, own = vpm.assignment_rows([], [cam, other], split_of=uncut)
check("two cameras, no recording, no choice -> no rows",
      rows == [] and own == {},
      "%d rows against 0, %d cameras noted against 0: %s"
      % (len(rows), len(own), named(rows)))
third = camera("Camera3.mov")
rows, _flag, own = vpm.assignment_rows([], [cam, other, third],
                                       split_of=uncut)
check("three of them make no difference", rows == [] and own == {},
      "%d rows against 0, %d cameras noted against 0: %s"
      % (len(rows), len(own), named(rows)))
rows, _flag, own = vpm.assignment_rows([recorded], [cam, other],
                                       split_of=uncut)
check("a recording beside them is the only row",
      named(rows) == [os.path.basename(recorded)],
      "%s against %s" % (named(rows), [os.path.basename(recorded)]))
check("and no camera is noted as contributing", own == {},
      "%d noted against 0: %s"
      % (len(own), sorted(os.path.basename(k) for k in own)))

#------------------------- the choice made: the camera goes the recording's way
rows, _flag, own = vpm.assignment_rows(
    [], [cam, other], own_flag_cameras=[cam],
    split_of=cut_into({cam: [p for p, _l in pieces]}))
check("the chosen camera brings its pieces as rows",
      sorted(named(rows))
      == sorted(os.path.basename(p) for p, _l in pieces),
      "%s against %s" % (sorted(named(rows)),
                         sorted(os.path.basename(p) for p, _l in pieces)))
check("both point back at the camera they came from",
      set(own.values()) == {os.path.abspath(cam)},
      "%d rows point at %s, want all at %s"
      % (len(own), sorted({os.path.basename(v) for v in own.values()}),
         os.path.basename(cam)))
check("and the camera nobody chose stays out",
      os.path.abspath(other) not in own.values(),
      "%s against never, among %s"
      % (os.path.basename(other),
         sorted({os.path.basename(v) for v in own.values()})))

# A camera in use is not a special row appended somewhere: it goes
# through the same splitting as the recording, so two files give four.
rec_pieces = [cut(recorded, chs, refused) for chs, _label in want_rec]
rows, _flag, own = vpm.assignment_rows(
    [recorded], [cam], own_flag_cameras=[cam],
    split_of=cut_into({cam: [p for p, _l in pieces],
                       recorded: rec_pieces}))
check("recording and camera are cut by the same rule",
      len(rows) == 4, "%d rows against 4: %s" % (len(rows), named(rows)))
check("and only the camera's rows point at a camera",
      sorted(os.path.basename(k) for k in own)
      == sorted(os.path.basename(p) for p, _l in pieces),
      "%s against %s" % (sorted(os.path.basename(k) for k in own),
                         sorted(os.path.basename(p) for p, _l in pieces)))

#------------------------------------------- a camera that stays one track
rows, _flag, own = vpm.assignment_rows([], [cam, other],
                                       own_flag_cameras=[other],
                                       split_of=uncut)
check("a camera that is not cut gives one row", len(rows) == 1,
      "%d rows against 1: %s" % (len(rows), named(rows)))
check("and points at itself",
      own == {os.path.abspath(other): os.path.abspath(other)},
      "%s against {%s: %s}"
      % (sorted((os.path.basename(k), os.path.basename(v))
                for k, v in own.items()),
         os.path.basename(other), os.path.basename(other)))

#-------------------------------- the one case nobody has to decide
# One video with sound and no recording beside it: that sound is the
# only sound there is, so it is in use without being chosen. As soon as
# a second camera or a recording joins, the answer falls back to no.
# Whether the camera is heard to carry sound at all is asked first, or
# the lines below report a rule that never came into play.
check("the camera is seen to carry sound at all",
      vpm.has_sound(cam) is True,
      "%r against True, over %d audio channels"
      % (vpm.has_sound(cam), vpm.audio_shape(cam)[0]))
alone, forced = vpm.cameras_with_own_audio([cam], [], sound_of=vpm.has_sound)
check("one camera with sound and nothing else -> in use by itself",
      [os.path.abspath(b) for b in alone] == [os.path.abspath(cam)],
      "%s against %s" % ([os.path.basename(b) for b in alone],
                         [os.path.basename(cam)]))
check("and it is marked as settled, not as chosen",
      [os.path.abspath(b) for b in forced] == [os.path.abspath(cam)],
      "%s against %s" % ([os.path.basename(b) for b in forced],
                         [os.path.basename(cam)]))
used, why = vpm.audio_use_settled(cam, alone, forced)
check("so the field shows it in use and says why", used is True and bool(why),
      "used %r against True, reason %r against a sentence" % (used, why))
two = vpm.cameras_with_own_audio([cam, other], [], sound_of=vpm.has_sound)
check("two cameras are a question again", two == ([], []),
      "%d and %d against 0 and 0" % (len(two[0]), len(two[1])))
beside = vpm.cameras_with_own_audio([cam], [recorded], sound_of=vpm.has_sound)
check("and so is one camera beside a recording", beside == ([], []),
      "%d and %d against 0 and 0" % (len(beside[0]), len(beside[1])))
mute = vpm.cameras_with_own_audio([cam], [], sound_of=lambda p: False)
check("a camera without any sound is not the exception", mute == ([], []),
      "%d and %d against 0 and 0" % (len(mute[0]), len(mute[1])))
free_used, free_why = vpm.audio_use_settled(cam, [], [])
check("where there is a choice the field is not settled",
      free_used is False and free_why == "",
      "used %r against False, reason %r against no reason at all"
      % (free_used, free_why))

#------------------------------------------------- the camera is a preselection
# A microphone plugged into one camera may be on a person another camera
# is filming, so the camera the audio came out of is a starting point.
targets = [os.path.basename(cam), os.path.basename(other), vpm.MIX_ONLY]
starts_on = vpm.preselected_camera(None, targets, "Guest", [cam, other],
                                   own_camera=os.path.basename(cam))
check("without a setting the track starts on its own camera",
      starts_on == os.path.basename(cam),
      "%s against %s" % (starts_on, os.path.basename(cam)))
moved = vpm.preselected_camera(os.path.basename(other), targets, "Guest",
                               [cam, other],
                               own_camera=os.path.basename(cam))
check("but it can be moved to the other one",
      moved == os.path.basename(other),
      "%s against %s" % (moved, os.path.basename(other)))

#--------------------------------------------- and on the command line too
# The interface cuts the camera in the background; a run started from
# the command line has to do it itself, or the two ways would disagree.
sound = sound_out_of(cam, "cameraaudio_Osmo.wav", rate=44100)
made = vpm.camera_audio_tracks(sound, "Osmo", WORK)
check("the camera gives two tracks on the command line as well",
      len(made) == 2,
      "%d tracks against 2: %s"
      % (len(made), [os.path.basename(p) for p, _n in made]))
check("named after the camera, not after the temporary file",
      [n for _p, n in made] == ["Osmo Channel 1", "Osmo Channel 2"],
      "%s against %s" % ([n for _p, n in made],
                         ["Osmo Channel 1", "Osmo Channel 2"]))
shapes = [(channels_of(p), vpm.audio_shape(p)[1]) for p, _n in made]
check("each piece is one channel and at the run's rate",
      shapes == [(1, SR)] * len(made),
      "%s against %s" % (shapes, [(1, SR)] * len(made)))

mono_cam = sound_out_of(other, "cameraaudio_Wide.wav", channels=1)
one = vpm.camera_audio_tracks(mono_cam, "Wide", WORK)
check("a camera with one channel stays one track", len(one) == 1,
      "%d tracks against 1: %s"
      % (len(one), [os.path.basename(p) for p, _n in one]))
check("and keeps its own name", len(one) == 1 and one[0][1] == "Wide",
      "%s against ['Wide']" % [n for _p, n in one])

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
