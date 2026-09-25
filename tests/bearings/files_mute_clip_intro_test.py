# -*- coding: utf-8 -*-
"""A mute clip is proposed as intro by a length that judges it alone.

A clip with no audio track has no envelope, so its length cannot be
read off one; the container says how long it runs. Sections: two
cameras with sound, a five-second clip with no sound and no timecode,
and a camera as long as the others that heard nothing either -- what
the measurement counts as far shorter, and what the proposal makes of
it; then one camera, a sounding jingle and two short mute clips, whose
container lengths must not stand in the middle the jingle is held
against. The rule is the length one of files_intro_proposed; only where
the length comes from, and what it may judge, is new here.
"""
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import the_program
import contextlib
import io
import subprocess
import tempfile
import time
import wave
import numpy as np

vpm = the_program.load()
vpm.set_language("en")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


#------------------------------------------------------------- Material

RATE = 48000
CAM_LEN, CLIP_LEN = 60.0, 5.0
# Shorter than both mute clips beside it, so it is the one proposed.
JINGLE_LEN, INSERT_LEN = 4.0, 6.0


def turns(seconds, seed):
    """Speech-like turns: noise in irregular pieces with pauses between."""
    rng = np.random.default_rng(seed)
    n = int(seconds * RATE)
    x = np.zeros(n)
    t = 0.2
    while t < seconds - 1.0:
        long_s = float(rng.uniform(0.25, 0.9))
        k, i0 = int(long_s * RATE), int(t * RATE)
        x[i0:i0 + k] = rng.normal(0, 0.25, k) * np.hanning(k)
        t += long_s + float(rng.uniform(0.2, 1.1))
    return x


# Its own folder under the run's TMPDIR, which the run throws away.
D = tempfile.mkdtemp(prefix="vpm_muteclip_")
with wave.open(os.path.join(D, "room.wav"), "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(RATE)
    f.writeframes((np.clip(turns(CAM_LEN + 10, 1), -1, 1) * 32000)
                  .astype("<i2").tobytes())
# A jingle: music, loud all the way through, with no turns to align on.
t = np.arange(int(JINGLE_LEN * RATE)) / float(RATE)
music = 0.1 * (np.sin(2 * np.pi * 220 * t) + np.sin(2 * np.pi * 277 * t)
               + np.sin(2 * np.pi * 330 * t))
with wave.open(os.path.join(D, "music.wav"), "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(RATE)
    f.writeframes((np.clip(music * (1.0 + 0.3 * np.sin(2 * np.pi * 2.0 * t)),
                           -1, 1) * 32000).astype("<i2").tobytes())

GUEST = os.path.join(D, "GuestCam_C001.mov")
PRESENTER = os.path.join(D, "PresenterCam_C002.mov")
CLIP = os.path.join(D, "Jingle_C003.mov")
MUTE = os.path.join(D, "WideCam_C004.mov")
SOUNDING = os.path.join(D, "Jingle_C005.mov")
INSERT = os.path.join(D, "Insert_C006.mov")
# One ffmpeg call for all six: colour bars at ultrafast, since no frame
# is decoded. No -timecode anywhere, and -an on the three with no sound.
PICTURE = ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p"]
command = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
           "smptebars=size=160x90:rate=25:duration=%.1f" % (CAM_LEN + 10),
           "-i", os.path.join(D, "room.wav"),
           "-i", os.path.join(D, "music.wav")]
for path, from_s in ((GUEST, 0.0), (PRESENTER, 4.0)):
    command += ["-map", "0:v", "-map", "1:a", "-ss", "%.2f" % from_s,
                "-t", "%.2f" % CAM_LEN] + PICTURE + ["-c:a", "pcm_s16le",
                                                     path]
command += ["-map", "0:v", "-t", "%.2f" % CLIP_LEN, "-an"] + PICTURE + [CLIP]
command += ["-map", "0:v", "-t", "%.2f" % CAM_LEN, "-an"] + PICTURE + [MUTE]
command += ["-map", "0:v", "-map", "2:a", "-t", "%.2f" % JINGLE_LEN] \
    + PICTURE + ["-c:a", "pcm_s16le", SOUNDING]
command += ["-map", "0:v", "-t", "%.2f" % INSERT_LEN, "-an"] + PICTURE \
    + [INSERT]
subprocess.run(command, check=True)
FILES = [GUEST, PRESENTER, CLIP, MUTE]
# A precondition of the material, not a judgement: none of the three
# carries a sound track for an envelope to come off.
for p in (CLIP, MUTE, INSERT):
    assert not vpm.video_facts(p)["audio"], p


def short(row):
    return sorted(os.path.basename(p) for p in (row or []))


#------------------------------------------- 1. What the measurement says

print("1. Two cameras with sound, a mute clip and a mute camera")
said = io.StringIO()
with contextlib.redirect_stdout(said):
    data, text = vpm.measure_time_axis(FILES)
print("   no place: %s   unplaceable: %s   brief: %s"
      % (short(data.get("no_place")), short(data.get("unplaceable")),
         short(data.get("brief"))))
check("the mute clip counts as far shorter than the rest",
      os.path.basename(CLIP) in short(data.get("brief")),
      "brief %s, no place %s, wanted %s among the brief"
      % (short(data.get("brief")), short(data.get("no_place")),
         os.path.basename(CLIP)))
check("a mute camera as long as the others does not",
      os.path.basename(MUTE) not in short(data.get("brief")),
      "brief %s, wanted %s not among them"
      % (short(data.get("brief")), os.path.basename(MUTE)))

#------------------------------------------------- 2. What is proposed

print("\n2. The proposal")
kinds = dict((p, vpm.Value(vpm.TYPE_CONTENT)) for p in FILES)
vpm.kind_proposal_apply(kinds, data.get("unplaceable"), data.get("brief"))
print("   %s" % dict((os.path.basename(p), kinds[p].get()) for p in FILES))
check("the mute clip is proposed as the intro",
      kinds[CLIP].get() == vpm.TYPE_INTRO,
      "%s, wanted %s" % (kinds[CLIP].get(), vpm.TYPE_INTRO))

#------------------------------- 3. Mute lengths stand for themselves

# One camera with sound, so the two mute clips would be the middle a
# sounding jingle is held against, if their lengths stood in it.
print("\n3. One camera, a sounding jingle and two short mute clips")
BESIDE = [GUEST, SOUNDING, CLIP, INSERT]
said = io.StringIO()
with contextlib.redirect_stdout(said):
    data, text = vpm.measure_time_axis(BESIDE)
print("   no place: %s   brief: %s"
      % (short(data.get("no_place")), short(data.get("brief"))))
check("a sounding jingle beside two mute clips still counts as short",
      os.path.basename(SOUNDING) in short(data.get("brief")),
      "brief %s, no place %s, wanted %s among the brief"
      % (short(data.get("brief")), short(data.get("no_place")),
         os.path.basename(SOUNDING)))
kinds = dict((p, vpm.Value(vpm.TYPE_CONTENT)) for p in BESIDE)
vpm.kind_proposal_apply(kinds, data.get("unplaceable"), data.get("brief"))
print("   %s" % dict((os.path.basename(p), kinds[p].get()) for p in BESIDE))
check("and it is the one proposed as the intro, not a mute clip",
      kinds[SOUNDING].get() == vpm.TYPE_INTRO,
      "%s, wanted %s; intro went to %s"
      % (kinds[SOUNDING].get(), vpm.TYPE_INTRO,
         sorted(os.path.basename(p) for p in BESIDE
                if kinds[p].get() == vpm.TYPE_INTRO)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
