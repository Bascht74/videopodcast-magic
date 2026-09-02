# -*- coding: utf-8 -*-
"""A switch that is taken changes the result, not only the parser.

One table, one row a switch: what it puts on the command line, the
ground it runs on, and the reading that has to come back different with
it and without it. In order: the table names only switches the program
hands out, every run answered and left a reading, then one judgement a
switch. Covered are --wide-shot, --min-edit-duration, --wide-after,
--no-wide-edges, --tc and --fps over a whole local run, --apart over the
plan of a dry run, --version and --hdr-check over the answer itself.
Left out is everything that would reach auphonic.com or wants Resolve
running. Whether the cut is right is not asked here, only that the
switch moves it.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import concurrent.futures
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import time
import wave

import numpy as np

spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec)
sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
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


def short(reading):
    """The start of a reading, cut to fit into the failure line."""
    if not reading:
        return "nothing"
    head = reading[0]
    return repr(head[:40] + ("..." if len(head) > 40 else ""))


# ---------------------------------------------------------------- material
#
# Two folders, because the two grounds must not see each other: the
# search for continuation files looks in the folder a block sits in, and
# the camera material beside it would be pulled into that plan.
FOLDER = tempfile.mkdtemp(prefix="vpm_switch_")
CAMERA_FOLDER = os.path.join(FOLDER, "cameras")
BLOCK_FOLDER = os.path.join(FOLDER, "blocks")
for made in (CAMERA_FOLDER, BLOCK_FOLDER, os.path.join(FOLDER, "cache")):
    os.makedirs(made)

# The runs go through a subprocess, so the environment is set here and
# not left to whoever started the test: English messages, the program's
# own cache inside the temporary folder, and no question asked over the
# network. --without-auphonic and no key stand on every command line
# below, so nothing is uploaded either.
ENV = dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="en",
           VPM_SILENT="1", VPM_NO_SPEAKER_SPLIT="1",
           VPM_NO_UPDATE_CHECK="1",
           VPM_CACHE=os.path.join(FOLDER, "cache"))

RATE, LENGTH = 48000, 70.0
# Two speakers taking turns. The times are what the wide shot settings
# need to have anything to work on, and each of them is a decision:
#
#   * The first handover ends at 13.0 s and the last begins at 55.5 s,
#     both inside a third of the length -- over a third the edge rule
#     calls it a conversation rather than a greeting and stands off.
#   * Between 14.5 s and 41.0 s the host holds the floor through three
#     breaths. That is one shot of 28 s with pauses in it, which is what
#     --wide-after needs: a shot to break up, and a boundary to break it
#     at. Without a transcript the pauses are the only boundaries there
#     are.
#   * Every turn is 5.0 or 5.5 s: over the 3 s a shot must stand, so
#     nothing is merged away by itself, and under the 8 s handed to
#     --min-edit-duration, so with it everything is.
TURNS = {"Host": [(1.5, 6.5), (14.5, 20.0), (21.5, 27.0), (28.5, 34.0),
                  (35.5, 41.0), (49.0, 54.0), (62.0, 67.0)],
         "Guest": [(8.0, 13.0), (42.5, 47.5), (55.5, 60.5)]}


def voice(turns, seed):
    """Bursts of noise where somebody speaks, silence in between."""
    rng = np.random.default_rng(seed)
    x = np.zeros(int(LENGTH * RATE))
    for a, b in turns:
        n = int((b - a) * RATE)
        env = 0.3 + 0.7 * np.abs(np.sin(np.linspace(0, 50, n)))
        x[int(a * RATE):int(a * RATE) + n] = rng.normal(0, 0.25, n) * env
    return x


def write_wave(path, x):
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())
    return path


host, guest = voice(TURNS["Host"], 1), voice(TURNS["Guest"], 2)
# Each microphone hears the other speaker 8 dB down. That is what lets
# the alignment find the recorder tracks in the camera sound at all:
# with two separated tracks the correlation has nothing in common to
# lock onto and lands on a wrong peak.
BLEED = 10 ** (-8.0 / 20)
noise = np.random.default_rng(9).normal(0, 0.0004, len(host))
HOST_WAV = write_wave(os.path.join(CAMERA_FOLDER, "Host.wav"),
                      host + BLEED * guest + noise)
GUEST_WAV = write_wave(os.path.join(CAMERA_FOLDER, "Guest.wav"),
                       guest + BLEED * host + noise)
ROOM_WAV = write_wave(os.path.join(CAMERA_FOLDER, "room.wav"),
                      0.6 * host + 0.6 * guest + noise)

# Three cameras: one for each speaker and one nobody sits in front of,
# which is the wide shot the run derives when no switch says otherwise.
# Colour bars at the fastest preset -- the run never decodes a picture,
# it reads packet times and copies the frames through, so the picture
# only has to be there. One ffmpeg call writes all three.
CAM_HOST = os.path.join(CAMERA_FOLDER, "CamHost.mov")
CAM_GUEST = os.path.join(CAMERA_FOLDER, "CamGuest.mov")
CAM_WIDE = os.path.join(CAMERA_FOLDER, "CamWide.mov")
build = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
         "smptebars=size=160x90:rate=25:duration=%.1f" % LENGTH,
         "-i", ROOM_WAV]
for target in (CAM_HOST, CAM_GUEST, CAM_WIDE):
    build += ["-map", "0:v", "-map", "1:a", "-c:v", "libx264",
              "-preset", "ultrafast", "-pix_fmt", "yuv420p",
              "-c:a", "pcm_s16le", "-shortest", target]
# A precondition of the material, not a statement about the program:
# without the three files nothing below can be run at all.
assert subprocess.run(build).returncode == 0, "ffmpeg wrote no cameras"

PRODUCTION = "Switch"
ASSIGN = os.path.join(CAMERA_FOLDER, "assign.json")
with io.open(ASSIGN, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "created_by": "test",
               "production": PRODUCTION,
               "tracks_of": [
                   {"audio": HOST_WAV, "blocks": [HOST_WAV],
                    "speakers": "Host", "camera": CAM_HOST,
                    "camera_audio": False},
                   {"audio": GUEST_WAV, "blocks": [GUEST_WAV],
                    "speakers": "Guest", "camera": CAM_GUEST,
                    "camera_audio": False}],
               "cameras": [{"video": CAM_HOST, "name": "CamHost"},
                           {"video": CAM_GUEST, "name": "CamGuest"},
                           {"video": CAM_WIDE, "name": "CamWide"}]}, f)

# The second ground: one recorder that wrote three numbered blocks, and
# a second recording beside it so the plan has more than one row.
BLOCKS = []
for index, hz in ((1, 300.0), (2, 300.0), (3, 300.0)):
    t = np.arange(int(4.0 * RATE)) / float(RATE)
    BLOCKS.append(write_wave(
        os.path.join(BLOCK_FOLDER, "REC000%d.wav" % index),
        0.4 * np.sin(2 * np.pi * hz * t)))
t = np.arange(int(4.0 * RATE)) / float(RATE)
BLOCKS.append(write_wave(os.path.join(BLOCK_FOLDER, "Guest0001.wav"),
                         0.4 * np.sin(2 * np.pi * 700.0 * t)))
BLOCK_TWO = BLOCKS[1]

# ------------------------------------------------------------- the grounds
#
# A ground is the command line a case is measured on, twice: once as it
# stands and once with the switch in front of it. Nothing here reaches
# the network -- no key, no preset, no update check.
LOCAL = ["--multitrack", "--without-auphonic", "--no-preflight",
         "--no-metrics", "--no-speech-recognition", "--no-transcript-file",
         # The camera's own sound is still read -- the alignment locks
         # onto it -- it is only not copied into the written camera file
         # as a third track. Nothing below reads the tracks of a written
         # camera file, and the camera cut comes back byte for byte the
         # same with the switch and without it; measured on 2.9.2026 it
         # takes a good quarter off the processor time a run costs
         # (4.30 s against 3.14 s), seven runs long.
         "--no-camera-audio",
         "--assign", ASSIGN]
CAMERA_FILES = [HOST_WAV, GUEST_WAV, CAM_HOST, CAM_GUEST, CAM_WIDE]


def whole_run(extra, out):
    """A run that finishes here: mix, write the files, write the cut."""
    return extra + LOCAL + ["--out", out] + CAMERA_FILES


def only_look(extra, out):
    """The same material, measured and not written."""
    return extra + ["--dry-run"] + LOCAL + ["--out", out] + CAMERA_FILES


def only_plan(extra, out):
    """A dry run over the four blocks: the plan is what is read off it."""
    return (extra + ["--dry-run", "--without-auphonic", "--no-preflight",
                     "--out", out] + BLOCKS)


# ------------------------------------------------------------ the readings
def cut_rows(said, out):
    """The camera cut the run wrote out: one row a shot."""
    path = os.path.join(out, PRODUCTION + "_cameracut.csv")
    if not os.path.exists(path):
        return []
    return io.open(path, encoding="utf-8").read().splitlines()[1:]


def cameras_shown(said, out):
    """Which camera each shot of that cut shows."""
    return [row.split(",")[1] for row in cut_rows(said, out)]


def start_times(said, out):
    """The timecode each shot of that cut starts at."""
    return [row.split(",")[3] for row in cut_rows(said, out)]


def plan_rows(said, out):
    """The rows of the recognised plan: one a recording."""
    rows, keep = [], False
    for line in said.splitlines():
        if vpm.T('RECOGNISED PLAN') in line:
            keep = True
        elif keep and line.startswith("  ") and ".wav" in line:
            rows.append(" ".join(line.split()))
        elif keep and line.strip() and not line.startswith(" "):
            break
    return rows


def headings(said, out):
    """What the answer is built of: the lines that begin at the margin.

    Everything the run says about its progress is indented, and it is
    also the only part that can differ between two runs of the same
    command line. So the headings, and nothing under them.
    """
    return [" ".join(line.split()) for line in said.splitlines()
            if line.strip() and line[:1] not in (" ", "\t", "\r")]


# --------------------------------------------------------------- the table
#
# One row a switch: what it puts on the command line, the ground, and
# what is read back off the run. A new switch is a row, not a function.
CASES = [
    ("--wide-shot", ["--wide-shot", CAM_HOST], whole_run, cameras_shown),
    ("--min-edit-duration", ["--min-edit-duration", "8"], whole_run, cut_rows),
    ("--wide-after", ["--wide-after", "6"], whole_run, cut_rows),
    ("--no-wide-edges", ["--no-wide-edges"], whole_run, cameras_shown),
    ("--tc", ["--tc", "10:00:00:00"], whole_run, start_times),
    ("--fps", ["--fps", "50"], whole_run, start_times),
    ("--apart", ["--apart", BLOCK_TWO], only_plan, plan_rows),
    ("--version", ["--version"], only_look, headings),
    # An SDR camera file is enough: what the switch changes is that the
    # program answers about HDR instead of doing the run. Whether it
    # reads a real HDR file right is files_hdr_complete_test.py's.
    ("--hdr-check", ["--hdr-check", CAM_HOST], only_look, headings),
]

print("1. The table names switches the program hands out")
# A switch that was renamed leaves its row testing nothing -- argparse
# would refuse the old name, both runs would fall over the same way, and
# a comparison of two failures says nothing. So this stands first.
offered = set()
for entry in vpm.build_argument_parser()._actions:
    offered.update(entry.option_strings)
missing = sorted(switch for switch, _e, _g, _r in CASES
                 if switch not in offered)
check("every switch in the table is one the program hands out",
      not missing, "%d of %d are not in the parser: %s"
      % (len(missing), len(CASES), ", ".join(missing) or "none"))

print("\n2. Every run answered, and left something to read")
# The run without the switch is shared by every case that stands on the
# same ground: three of those, not nine.
runs = {}


def started(tag, ground, extra):
    """Start the program once, and keep what it printed and where."""
    out = os.path.join(FOLDER, "out_" + tag)
    called = subprocess.run([sys.executable, SCRIPT] + ground(extra, out),
                            capture_output=True, text=True, env=ENV)
    runs[tag] = ((called.stdout or "") + (called.stderr or ""), out,
                 called.returncode)
    return runs[tag]


# No start below needs what another one found, so they go side by side
# instead of one after the other. The bare run on the camera ground goes
# first and by itself: it leaves the probes and the envelopes of the
# camera files in the shared cache, and the ones behind it read them
# instead of measuring them again. Starting them all at once costs a
# fifth more processor time for the same waiting -- measured here on
# 2.9.2026, 26 s against 22 s.
started("cut", whole_run, [])
LEFT = [("plan", only_plan, []), ("look", only_look, [])]
LEFT += [(switch.lstrip("-"), ground, extra)
         for switch, extra, ground, _reading in CASES]
# As many at once as the machine has cores, and at most six. Measured
# here on 2.9.2026, this section takes 7.1 s at two, 5.5 at three, 4.8
# at four, 4.1 at six and 3.7 at eleven, while the processor time it
# costs stays between 21 and 22 s throughout. Past six the waiting
# hardly falls any further and every further start wants its own 200 MB.
AT_ONCE = max(2, min(6, os.cpu_count() or 2))
with concurrent.futures.ThreadPoolExecutor(max_workers=AT_ONCE) as side:
    list(side.map(lambda one: started(*one), LEFT))

fell = sorted(tag for tag, (said, _o, _rc) in runs.items()
              if "Traceback" in said)
check("every run came back without a traceback", not fell,
      "%d of %d fell over: %s" % (len(fell), len(runs),
                                  ", ".join(fell) or "none"))

BARE = {whole_run: "cut", only_plan: "plan", only_look: "look"}
readings = {}
for switch, extra, ground, reading in CASES:
    without = runs[BARE[ground]]
    with_it = runs[switch.lstrip("-")]
    readings[switch] = (reading(without[0], without[1]),
                        reading(with_it[0], with_it[1]))
nothing = sorted(switch for switch, (a, b) in readings.items()
                 if not a or not b)
check("and every run left a reading to compare", not nothing,
      "%d of %d read as nothing: %s"
      % (len(nothing), 2 * len(CASES), ", ".join(nothing) or "none"))

print("\n3. Each switch changes what comes back")
# One judgement a switch, and each one written out. The name of a check
# is what the register of counter-proofs holds a row by, and it reads
# the first argument of every check out of the source: a name put
# together while the test runs stands there as "%s changes the result"
# and folds nine judgements into one row. So the switch is in the name,
# spelled out, and the numbers are below.
#
# A new switch is therefore two things: a row in the table above and a
# check of its own down here.


def moved(switch):
    """Whether that switch changed the reading, and the numbers for it."""
    without, with_it = readings[switch]
    return (without != with_it,
            "%d readings without and %d with; without begins %s, with %s"
            % (len(without), len(with_it), short(without), short(with_it)))


check("--wide-shot changes the result, not only the parser",
      *moved("--wide-shot"))
check("--min-edit-duration changes the result, not only the parser",
      *moved("--min-edit-duration"))
check("--wide-after changes the result, not only the parser",
      *moved("--wide-after"))
check("--no-wide-edges changes the result, not only the parser",
      *moved("--no-wide-edges"))
check("--tc changes the result, not only the parser",
      *moved("--tc"))
check("--fps changes the result, not only the parser",
      *moved("--fps"))
check("--apart changes the result, not only the parser",
      *moved("--apart"))
check("--version changes the result, not only the parser",
      *moved("--version"))
check("--hdr-check changes the result, not only the parser",
      *moved("--hdr-check"))

shutil.rmtree(FOLDER, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
