# -*- coding: utf-8 -*-
"""What the run promises as audio tracks is what it writes.

Before it writes anything the run prints a plan: one line per camera
file and under it every audio track that file is to carry. That is what
a user reads to see whether the settings are right, so it has to say
what the file says. The sections: four runs go through with nothing
leaving the house; the plan, the run's own report afterwards and
ffprobe name the same tracks in the same order; and the camera files in
the folder are the ones the plan promised, none of them appearing
unannounced and none going missing without a word.

One thing the run says differently today, and the judgement stays true
when it is put right: the plan names the camera's own track under every
camera while the run writes it only where the camera has sound and
--no-camera-audio was not given, so exactly that one name may be
promised and not delivered. Every other name has to match letter for
letter -- the overall mix included, which is why it is asked about on
its own as well.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import glob
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import time
import wave

import numpy as np

# Qt comes up with the program and must not want a screen; the speaker
# separation fetches a machine-learning environment and is not what is
# asked here.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("VPM_NO_SPEAKER_SPLIT", "1")
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
vpm.set_language("en")

# The same environment the suite gives every test, so a run by hand
# measures the same thing. PIP_NO_INDEX shuts the road out of the house
# that is left: the program fetches numpy and PySide6 into this Python
# where they are missing, and a test must not install anything. ffmpeg
# is not among them any more -- the program says what is missing and
# stops, which run_ffmpeg_not_fetched_test.py holds it to.
# VPM_INSTALL_TOOLS would let it install over the package manager, so it
# goes out of the environment whatever the caller set.
ENV = dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="en",
           VPM_SILENT="1", VPM_NO_UPDATE_CHECK="1",
           VPM_NO_SPEAKER_SPLIT="1", QT_QPA_PLATFORM="offscreen",
           PIP_NO_INDEX="1")
ENV.pop("VPM_INSTALL_TOOLS", None)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stop():
    """Nothing further can be asked, so count what there is and go."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


def tail(text, n=2):
    rows = [x.strip() for x in text.splitlines() if x.strip()]
    return (" | ".join(rows[-n:]))[:100]


#------------------------------------------------------------- Material

RATE = 48000
# 36 s, and not less. The run stops below a common window of 30 s, and
# the common window is LENGTH minus the latest camera start.
LENGTH = 36.0
# Where each camera's picture starts inside the recording. None of them
# is zero, so no arithmetic in the run is tested against nothing.
LATE = {"WideCam": 4.0, "GuestCam": 3.0, "PresenterCam": 5.0}
# Turns with a pause of at least a second around each. Speech-like
# noise, because the alignment lives on the envelope of speech; a steady
# tone would align by luck.
TURNS = {"Guest": [(4, 9), (16, 21), (27, 32)],
         "Presenter": [(10, 14.5), (22.5, 26)]}


def voice(turns, seed):
    rng = np.random.default_rng(seed)
    x = np.zeros(int(LENGTH * RATE))
    for a, b in turns:
        n = int((b - a) * RATE)
        env = 0.3 + 0.7 * np.abs(np.sin(np.linspace(0, 50, n)))
        x[int(a * RATE):int(a * RATE) + n] = rng.normal(0, 0.25, n) * env
    return x


def write_wav(path, x):
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())


D = tempfile.mkdtemp(prefix="vpm_promise_")
guest, presenter = voice(TURNS["Guest"], 1), voice(TURNS["Presenter"], 2)
bleed = 10 ** (-8.0 / 20)            # under the 3:1 rule on purpose
noise = np.random.default_rng(9).normal(0, 0.0004, len(guest))
write_wav(D + "/Guest.wav", guest + bleed * presenter + noise)
write_wav(D + "/Presenter.wav", presenter + bleed * guest + noise)
write_wav(D + "/room.wav", 0.6 * guest + 0.6 * presenter + noise)

# One ffmpeg call for all four cameras, because a process start is what
# the Windows builder charges for. Colour bars at ultrafast: the run
# never decodes a video frame, it reads the packet times and copies the
# picture through, so the picture only has to exist. MuteCam is the same
# picture with no sound track at all -- the camera that filmed silently.
build = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
         "smptebars=size=320x180:rate=25:duration=%.1f" % LENGTH,
         "-i", D + "/room.wav"]
for cam in sorted(LATE):
    build += ["-ss", "%.2f" % LATE[cam],
              "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
              "-preset", "ultrafast", "-pix_fmt", "yuv420p",
              "-c:a", "pcm_s16le", "-shortest", D + "/" + cam + ".mov"]
build += ["-ss", "4.00", "-map", "0:v", "-c:v", "libx264",
          "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-an",
          "-t", "%.2f" % (LENGTH - 4.0), D + "/MuteCam.mov"]
subprocess.run(build, check=True)

# The file format number is read out of the program's own constant, so
# an assignment file written here is one the run accepts.
CAMERA_TRACK = vpm.build_argument_parser().get_default("name_camera")
MIX = vpm.MIX_TRACK_NAME


def assignment(path, seating, cameras):
    """Write an assignment file: who sits on which camera."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"format": vpm.FILE_FORMAT, "created_by": "test",
                   "tracks_of": [
                       {"audio": D + "/" + who + ".wav",
                        "blocks": [D + "/" + who + ".wav"],
                        "speakers": who, "camera": D + "/" + cam + ".mov",
                        "camera_audio": False}
                       for who, cam in seating],
                   "cameras": [{"video": D + "/" + c + ".mov", "name": c}
                               for c in cameras]}, f)


assignment(D + "/apart.json",
           [("Guest", "GuestCam"), ("Presenter", "PresenterCam")],
           ["GuestCam", "PresenterCam", "WideCam"])
assignment(D + "/together.json",
           [("Guest", "WideCam"), ("Presenter", "WideCam")], ["WideCam"])


#-------------------------------------------------------------- The runs

# Half an hour for a run that takes a second and a half here. It is
# never reached on a machine that works and therefore costs nothing; a
# run that hangs comes back as a failed run with the wait in its line,
# rather than ending the test in a traceback before it has counted.
PATIENCE = 1800.0


def run(out, *extra):
    """One run on this material, and what it printed."""
    try:
        answer = subprocess.run(
            [sys.executable, SCRIPT, "--without-auphonic", "--no-metrics",
             "--no-speech-recognition", "--no-transcript-file",
             "--no-wide-edges", "--out", D + "/" + out]
            + [str(x) for x in extra],
            capture_output=True, text=True, timeout=PATIENCE, env=ENV)
    except subprocess.TimeoutExpired:
        return -1, "the run did not come back within %.0f s" % PATIENCE
    return answer.returncode, (answer.stdout or "") + (answer.stderr or "")


rc, log = {}, {}
# nocam: the switch that takes the camera's own track out of the file,
# while the plan goes on announcing it.
rc["nocam"], log["nocam"] = run(
    "nocam", "--no-camera-audio", D + "/Guest.wav", D + "/Presenter.wav",
    D + "/WideCam.mov")
# mute: a camera that filmed without sound, beside one that did not.
rc["mute"], log["mute"] = run(
    "mute", D + "/Guest.wav", D + "/Presenter.wav", D + "/WideCam.mov",
    D + "/MuteCam.mov")
# apart: one speaker per camera and a wide shot with nobody on it -- the
# only shape in which an overall mix track is written at all.
rc["apart"], log["apart"] = run(
    "apart", "--assign", D + "/apart.json", D + "/Guest.wav",
    D + "/Presenter.wav", D + "/GuestCam.mov", D + "/PresenterCam.mov",
    D + "/WideCam.mov")
# together: two microphones, one camera. The everyday shape, and the one
# where neither side writes an overall mix.
rc["together"], log["together"] = run(
    "together", "--assign", D + "/together.json", D + "/Guest.wav",
    D + "/Presenter.wav", D + "/WideCam.mov")

RUNS = ("nocam", "mute", "apart", "together")


#--------------------------------------------------- Reading the two lists

# Every wording comes out of the catalogue, so the reading does not tie
# itself to one language.
HEAD = vpm.T('\n  This produces:').strip()
PROMISED_TRACK = vpm.T('        Track %d: %s').split("%d")[0]
MARK = vpm.T('\nPROCESSING: %s').strip().split("%s")[0]
WROTE_TRACK = vpm.T('  Audio track %d:   %s').split("%d")[0]
NO_SOUND = vpm.T('  %s has no camera sound -- without it nothing can be '
                 'aligned').split("%s")[1].strip()


def plan_of(text):
    """The plan block: (source, file) pairs and the tracks under each.

    The block reads "    <source>  ->  <name>.mov" and under each of
    them one line per audio track. The pairs are kept whole, because the
    source name is what the written file is looked up by.
    """
    at = text.find(HEAD)
    pairs, tracks = [], {}
    if at < 0:
        return pairs, tracks
    for line in text[at + len(HEAD):].splitlines()[1:]:
        if "  ->  " in line:
            pairs.append(tuple(x.strip() for x in line.split("  ->  ")))
            tracks[pairs[-1][0]] = []
        elif line.startswith(PROMISED_TRACK) and pairs:
            tracks[pairs[-1][0]].append(line.split(":", 1)[1].strip())
        elif line.strip() and not line.startswith(" "):
            break
    return pairs, tracks


def reported(text):
    """Per camera, the tracks the run says afterwards that it wrote."""
    said = {}
    for block in text.split(MARK)[1:]:
        lines = block.splitlines()
        said[lines[0].strip()] = [l.split(":", 1)[1].strip() for l in lines
                                  if l.startswith(WROTE_TRACK)]
    return said


def tracks_in_file(path):
    """The names of the audio tracks of one file, in file order.

    A track name in a MOV file lives in handler_name; the title tag
    ffprobe would rather show is not written into this container.
    """
    answer = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream_tags=handler_name",
         "-of", "csv=p=0", path], capture_output=True, text=True)
    return [l.strip() for l in answer.stdout.splitlines() if l.strip()]


def names_it(promise, held):
    """Does one promised line name the track the file carries?

    Letter for letter, the overall mix included: the plan is read
    before the run to see whether the settings are right, and a name
    that is spelt one way there and another way in Resolve is two
    names to whoever reads both.
    """
    return promise == held


#----------------------------------------------------------- The answers

print("1. The four runs go through with nothing leaving the house")
fell = [name for name in RUNS if rc[name] != 0]
check("every run comes back with 0", not fell,
      "%d of %d did not: %s"
      % (len(fell), len(RUNS),
         " ; ".join("%s returned %d, ends: %s"
                    % (n, rc[n], tail(log[n], 1)[:60]) for n in fell)[:200]))
broke = [name for name in RUNS if "Traceback" in log[name]]
check("and none of them ended in a traceback", not broke,
      "%d of %d did: %s"
      % (len(broke), len(RUNS),
         " ; ".join("%s at character %d: %s"
                    % (n, log[n].find("Traceback"),
                       " ".join(log[n][log[n].find("Traceback"):][:120]
                                .split()))
                    for n in broke)[:200]))
spoke = [(name, log[name].count("auphonic.com/api"),
          log[name].count("Uploading")) for name in RUNS
         if log[name].count("auphonic.com/api")
         or log[name].count("Uploading")]
check("and none of them mentioned auphonic.com", not spoke,
      "%d of %d did, wanted 0 and 0 in each: %s"
      % (len(spoke), len(RUNS), spoke))
if fell or broke:
    stop()

PLAN = {name: plan_of(log[name]) for name in RUNS}
SAID = {name: reported(log[name]) for name in RUNS}
empty = [name for name in RUNS if not PLAN[name][0]
         or not any(PLAN[name][1].values())]
check("every run printed the plan's track list", not empty,
      "%d of %d printed none: %s -- %s"
      % (len(empty), len(RUNS), empty,
         " ; ".join("%s promises %d files" % (n, len(PLAN[n][0]))
                    for n in RUNS)))
if empty:
    stop()

# One row per camera that was really written: what the plan promised,
# what the run said afterwards, what ffprobe finds.
rows = []
for name in RUNS:
    pairs, promised_tracks = PLAN[name]
    for source, made in pairs:
        path = os.path.join(D, name, made)
        if os.path.exists(path):
            rows.append((name, source, promised_tracks.get(source, []),
                         SAID[name].get(source, []), tracks_in_file(path)))

print("\n2. The plan and the written file name the same tracks")
check("there is a written file to hold the plan against", len(rows) >= 5,
      "%d camera files over %d runs, wanted at least 5"
      % (len(rows), len(RUNS)))
if not rows:
    stop()
# The camera's own track is the one name the plan may promise without
# the file carrying it: it is announced under every camera and written
# only where the camera has sound and --no-camera-audio was not given.
# Where that is put right the exception is simply never used, and the
# judgement stays true.
over = [(name, source, line, held)
        for name, source, promise, _said, held in rows
        for line in promise
        if line != CAMERA_TRACK
        and not any(names_it(line, one) for one in held)]
check("the plan names no track the file lacks beyond the camera's own",
      not over,
      "%d over %d camera files, the first: %s"
      % (len(over), len(rows), over[0] if over else ()))
short = [(name, source, one, promise)
         for name, source, promise, _said, held in rows
         for one in held
         if not any(names_it(line, one) for line in promise)]
check("and the file holds no track the plan did not name", not short,
      "%d over %d camera files, the first: %s"
      % (len(short), len(rows), short[0] if short else ()))
# Order, not only membership: the file's tracks have to turn up in the
# plan in the order the file carries them.
out_of_order = []
for name, source, promise, _said, held in rows:
    at = 0
    for one in held:
        while at < len(promise) and not names_it(promise[at], one):
            at += 1
        if at >= len(promise):
            out_of_order.append((name, source, promise, held))
            break
        at += 1
check("and the file's tracks come in the order the plan named them",
      not out_of_order,
      "%d of %d camera files differ, the first: %s"
      % (len(out_of_order), len(rows),
         out_of_order[0] if out_of_order else ()))
# The mix on its own, because it is the line that used to be spelt one
# way in the plan and another in the file, and the rule above would let
# a decorated name back in the day somebody decorates the file too.
mix_named = [(name, source, line)
             for name, source, promise, _said, held in rows
             for line in promise
             if line.startswith(MIX) and line != MIX]
check("the overall mix is named in the plan as the file names it",
      bool(rows) and not mix_named,
      "%d lines over %d camera files are not exactly %r, the first: %s"
      % (len(mix_named), len(rows), MIX,
         mix_named[0] if mix_named else ()))
# And the run's own report of what it wrote, against the file itself. No
# exception here: this list is printed after the writing, so it has
# nothing left to be uncertain about.
lied = [(name, source, said, held)
        for name, source, _promise, said, held in rows if said != held]
check("and the run's own list of what it wrote is what the file holds",
      not lied,
      "%d of %d camera files differ, the first: %s"
      % (len(lied), len(rows), lied[0] if lied else ()))

print("\n3. Every camera file the plan promised is accounted for")
# A camera the run cannot place writes no file. That may happen -- what
# must not happen is that it happens in silence, after the plan has
# named the file.
missing, unpromised = [], []
for name in RUNS:
    pairs, _tracks = PLAN[name]
    folder = os.path.join(D, name)
    there = sorted(os.path.basename(p)
                   for p in glob.glob(folder + "/*.mov"))
    for source, made in pairs:
        if made not in there and not re.search(
                re.escape(source) + r".{0,4}" + re.escape(NO_SOUND),
                log[name]):
            missing.append((name, source, made, there))
    unpromised += [(name, one) for one in there
                   if one not in [b for _a, b in pairs]]
check("no camera file the plan promised goes missing without a word",
      not missing,
      "%d over %d runs, the first: %s"
      % (len(missing), len(RUNS), missing[0] if missing else ()))
check("and no camera file was written that the plan did not promise",
      not unpromised,
      "%d over %d runs, the first: %s"
      % (len(unpromised), len(RUNS), unpromised[0] if unpromised else ()))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
