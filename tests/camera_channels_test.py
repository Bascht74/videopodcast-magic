# -*- coding: utf-8 -*-
"""A camera ticked "as a track" is an audio candidate like any other.

The tick says no more than "do not throw this audio away". What the audio
becomes is then decided by the same measurement as for a recorder file: a
camera whose two channels carry two clip-on microphones -- a DJI Osmo does
that -- gives two tracks with two speaker names, and one carrying a real
stereo pair keeps it as one two channel track.

Which camera such a track belongs to is a separate question. A microphone
plugged into one camera may well be on a person another camera is
filming, so the camera the audio came out of is the preselection and
nothing more.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, subprocess, sys, tempfile
import numpy as np
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
SR = vpm.SR
WORK = tempfile.mkdtemp(prefix="camerachannels_")
bad = []


def check(what, ok, detail=""):
    print("%-58s %s%s" % (what, "ok" if ok else "FAIL",
                          "" if ok else "   " + detail))
    if not ok:
        bad.append(what)


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


cam = camera("Camera1.mov")
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

#------------------------------------------------- and they become two rows
other = camera("Camera2.mov")
rows, camera_audio, own = vpm.assignment_rows(
    [], [cam, other], own_flag_cameras=[cam],
    split_of=lambda x: [p for p, _l in pieces]
    if os.path.abspath(x) == os.path.abspath(cam) else [])
check("ticking one camera ends the cameras-only case",
      camera_audio is False)
check("a camera cut in two gives two rows", len(rows) == 2, str(len(rows)))
check("both point back at the camera they came from",
      set(own.values()) == {os.path.abspath(cam)}, str(own))
check("and the rows are the pieces, not the video",
      sorted(os.path.basename(r[0][0]) for r in rows)
      == sorted(os.path.basename(p) for p, _l in pieces),
      str([os.path.basename(r[0][0]) for r in rows]))

#------------------------------------------- a camera that stays one track
rows2, _c2, own2 = vpm.assignment_rows(
    [], [cam, other], own_flag_cameras=[other], split_of=lambda x: [])
check("a camera that is not cut gives one row", len(rows2) == 1)
check("and points at itself",
      own2 == {os.path.abspath(other): os.path.abspath(other)}, str(own2))

#------------------------------------------------- the camera is a preselection
targets = [os.path.basename(cam), os.path.basename(other), vpm.MIX_ONLY]
#------------------------------------------- nothing ticked: every camera
rows3, camera_audio3, own3 = vpm.assignment_rows(
    [], [cam, other], own_flag_cameras=[], split_of=lambda x: [])
check("with nothing ticked every camera is a track",
      camera_audio3 is True and len(rows3) == 2, str(len(rows3)))
check("and each points at itself", len(own3) == 2, str(own3))

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
# The interface cuts the camera in the background; a run started from the
# command line has to do it for itself, or the DJI case would work in one
# place and not in the other.
sound = os.path.join(WORK, "cameraaudio_Osmo.wav")
subprocess.run(["ffmpeg", "-v", "error", "-i", cam, "-map", "0:a:0",
                "-ac", "2", "-ar", str(SR), "-c:a", "pcm_s16le", "-y",
                sound], check=True)
pieces = vpm.camera_audio_tracks(sound, "Osmo", WORK)
check("the camera gives two tracks on the command line as well",
      len(pieces) == 2, str(pieces))
check("named after the camera, not after the temporary file",
      [n for _p, n in pieces] == ["Osmo Channel 1", "Osmo Channel 2"],
      str([n for _p, n in pieces]))
check("each piece is one channel and at the run's rate",
      all(vpm.channel_count(p) == 1 and vpm.audio_shape(p)[1] == SR
          for p, _n in pieces),
      str([vpm.audio_shape(p) for p, _n in pieces]))

mono_cam = os.path.join(WORK, "cameraaudio_Wide.wav")
subprocess.run(["ffmpeg", "-v", "error", "-i", other, "-map", "0:a:0",
                "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le", "-y",
                mono_cam], check=True)
one = vpm.camera_audio_tracks(mono_cam, "Wide", WORK)
check("a camera with one channel stays one track", len(one) == 1)
check("and keeps its own name", one[0][1] == "Wide", str(one))

print()
if bad:
    print("FAIL: %d of the checks" % len(bad))
    sys.exit(1)
print("all checks passed")
