# -*- coding: utf-8 -*-
"""A camera whose audio is in use is an audio file like any other.

The field on the video file says no more than "use the audio"; what
that audio becomes is decided by the same measurement as for a recorder
file. So the same sound is offered twice, once inside the camera and
once as a recording beside it, and both have to come out with the same
verdict and the same tracks. With nothing chosen there is no audio from
a camera at all, and nothing here reads the interface.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
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


def sound_out_of(video, name, channels=2):
    """The audio of that video, on its own, as a recording would be."""
    path = os.path.join(WORK, name)
    subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-map", "0:a:0",
                    "-ac", str(channels), "-ar", str(SR), "-c:a",
                    "pcm_s16le", "-y", path], check=True)
    return path


cam = camera("Camera1.mov")
other = camera("Camera2.mov")
check("the camera has two channels", vpm.channel_count(cam) == 2,
      str(vpm.channel_count(cam)))
check("and records at 44.1 kHz", vpm.audio_shape(cam)[1] == 44100,
      str(vpm.audio_shape(cam)))

#----------------------------------------- the channels are judged as usual
facts = vpm.channel_facts_cached(cam)
check("a video's channels can be measured", facts["readable"] is True)
pairs = vpm.channel_joins(facts)
check("one pair is judged", len(pairs) == 1, str(len(pairs)))
check("two separate tones are not read as one stereo track",
      pairs[0][1] is False, str(pairs[0]))
want = vpm.tracks_to_split(cam, facts)
check("so the camera is cut into two tracks", len(want) == 2, str(want))

#------------------------- the same sound as a recording is judged the same
# The audio out of the camera and the audio in a file beside it are one
# and the same signal, so every step has to answer the same about both.
# Where they part company, "treated like a normal audio file" has
# stopped being true.
recorded = sound_out_of(cam, "Osmo_recording.wav")
facts_rec = vpm.channel_facts_cached(recorded)
check("the recording of it can be measured too",
      facts_rec["readable"] is True)
pairs_rec = vpm.channel_joins(facts_rec)
check("and its pair is judged the same way",
      len(pairs_rec) == len(pairs) and pairs_rec[0][1] == pairs[0][1],
      str(pairs_rec))
want_rec = vpm.tracks_to_split(recorded, facts_rec)
check("camera and recording give the same number of tracks",
      len(want_rec) == len(want), "%d vs %d" % (len(want_rec), len(want)))
check("and cut at the same channels",
      [chs for chs, _l in want_rec] == [chs for chs, _l in want],
      str([chs for chs, _l in want_rec]))

#------------------------------------------------- cutting brings the rate over
pieces = []
for chs, label in want:
    target = vpm.split_target(cam, chs, WORK)
    vpm.split_channels(cam, chs, target, rate=SR)
    pieces.append((target, label))
check("both pieces are there", all(os.path.exists(p) for p, _l in pieces))
check("each holds one channel",
      all(vpm.channel_count(p) == 1 for p, _l in pieces))
check("and both are at the run's sample rate",
      all(vpm.audio_shape(p)[1] == SR for p, _l in pieces),
      str([vpm.audio_shape(p) for p, _l in pieces]))


def has_tone(path, hz):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le",
                          "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype="<f4")
    spectrum = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    k = int(round(hz * len(x) / float(SR)))
    return float(spectrum[k]) / (float(np.max(spectrum)) or 1.0)


check("the first piece is the first channel",
      has_tone(pieces[0][0], 500) > 0.9 and has_tone(pieces[0][0], 900) < 0.1,
      "%.2f / %.2f" % (has_tone(pieces[0][0], 500),
                       has_tone(pieces[0][0], 900)))
check("the second the other one",
      has_tone(pieces[1][0], 900) > 0.9 and has_tone(pieces[1][0], 500) < 0.1)

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
      rows == [] and own == {}, str(rows))
third = camera("Camera3.mov")
rows, _flag, own = vpm.assignment_rows([], [cam, other, third],
                                       split_of=uncut)
check("three of them make no difference", rows == [] and own == {},
      str(rows))
rows, _flag, own = vpm.assignment_rows([recorded], [cam, other],
                                       split_of=uncut)
check("a recording beside them is the only row",
      named(rows) == [os.path.basename(recorded)], str(named(rows)))
check("and no camera is noted as contributing", own == {}, str(own))

#------------------------- the choice made: the camera goes the recording's way
rows, _flag, own = vpm.assignment_rows(
    [], [cam, other], own_flag_cameras=[cam],
    split_of=cut_into({cam: [p for p, _l in pieces]}))
check("the chosen camera brings its pieces as rows",
      sorted(named(rows))
      == sorted(os.path.basename(p) for p, _l in pieces),
      str(named(rows)))
check("both point back at the camera they came from",
      set(own.values()) == {os.path.abspath(cam)}, str(own))
check("and the camera nobody chose stays out",
      os.path.abspath(other) not in own.values(), str(own))

# A camera in use is not a special row appended somewhere: it goes
# through the same splitting as the recording, so two files give four.
rec_pieces = []
for chs, _label in want_rec:
    target = vpm.split_target(recorded, chs, WORK)
    vpm.split_channels(recorded, chs, target, rate=SR)
    rec_pieces.append(target)
rows, _flag, own = vpm.assignment_rows(
    [recorded], [cam], own_flag_cameras=[cam],
    split_of=cut_into({cam: [p for p, _l in pieces],
                       recorded: rec_pieces}))
check("recording and camera are cut by the same rule",
      len(rows) == 4, "%d rows" % len(rows))
check("and only the camera's rows point at a camera",
      sorted(os.path.basename(k) for k in own)
      == sorted(os.path.basename(p) for p, _l in pieces), str(own))

#------------------------------------------- a camera that stays one track
rows, _flag, own = vpm.assignment_rows([], [cam, other],
                                       own_flag_cameras=[other],
                                       split_of=uncut)
check("a camera that is not cut gives one row", len(rows) == 1,
      str(named(rows)))
check("and points at itself",
      own == {os.path.abspath(other): os.path.abspath(other)}, str(own))

#-------------------------------- the one case nobody has to decide
# One video with sound and no recording beside it: that sound is the
# only sound there is, so it is in use without being chosen. As soon as
# a second camera or a recording joins, the answer falls back to no.
alone, forced = vpm.cameras_with_own_audio([cam], [], sound_of=vpm.has_sound)
check("one camera with sound and nothing else -> in use by itself",
      [os.path.abspath(b) for b in alone] == [os.path.abspath(cam)],
      str(alone))
check("and it is marked as settled, not as chosen",
      [os.path.abspath(b) for b in forced] == [os.path.abspath(cam)],
      str(forced))
used, why = vpm.audio_use_settled(cam, alone, forced)
check("so the field shows it in use and says why", used is True and why,
      "%s / %r" % (used, why))
check("two cameras are a question again",
      vpm.cameras_with_own_audio([cam, other], [],
                                 sound_of=vpm.has_sound) == ([], []))
check("and so is one camera beside a recording",
      vpm.cameras_with_own_audio([cam], [recorded],
                                 sound_of=vpm.has_sound) == ([], []))
check("a camera without any sound is not the exception",
      vpm.cameras_with_own_audio([cam], [], sound_of=lambda p: False)
      == ([], []))
free_used, free_why = vpm.audio_use_settled(cam, [], [])
check("where there is a choice the field is not settled",
      free_used is False and free_why == "", repr(free_why))

#------------------------------------------------- the camera is a preselection
# A microphone plugged into one camera may be on a person another camera
# is filming, so the camera the audio came out of is a starting point.
targets = [os.path.basename(cam), os.path.basename(other), vpm.MIX_ONLY]
check("without a setting the track starts on its own camera",
      vpm.preselected_camera(None, targets, "Guest", [cam, other],
                             own_camera=os.path.basename(cam))
      == os.path.basename(cam))
check("but it can be moved to the other one",
      vpm.preselected_camera(os.path.basename(other), targets, "Guest",
                             [cam, other],
                             own_camera=os.path.basename(cam))
      == os.path.basename(other))

#--------------------------------------------- and on the command line too
# The interface cuts the camera in the background; a run started from
# the command line has to do it itself, or the two ways would disagree.
sound = sound_out_of(cam, "cameraaudio_Osmo.wav")
made = vpm.camera_audio_tracks(sound, "Osmo", WORK)
check("the camera gives two tracks on the command line as well",
      len(made) == 2, str(made))
check("named after the camera, not after the temporary file",
      [n for _p, n in made] == ["Osmo Channel 1", "Osmo Channel 2"],
      str([n for _p, n in made]))
check("each piece is one channel and at the run's rate",
      all(vpm.channel_count(p) == 1 and vpm.audio_shape(p)[1] == SR
          for p, _n in made),
      str([vpm.audio_shape(p) for p, _n in made]))

mono_cam = sound_out_of(other, "cameraaudio_Wide.wav", channels=1)
one = vpm.camera_audio_tracks(mono_cam, "Wide", WORK)
check("a camera with one channel stays one track", len(one) == 1)
check("and keeps its own name", one[0][1] == "Wide", str(one))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
