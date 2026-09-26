# -*- coding: utf-8 -*-
"""Under Sync only every camera is offered its own file name.

The sections: the name the table offers a camera with a speaker on it,
under Sync only and in a cut project; a stem kept from Sync only, which
counts as offered and not typed; the command line with cameras only;
and two cameras with one stem, which keep two names, alone and beside
recordings. The run's plan has its measuring replaced, so the naming is
asked and not the material. What this cannot show is that the window
hands its project type in; that is one argument at one call.
"""
PLATFORM_BOUND = True
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import json
import shutil
import tempfile
import time
import the_program

SCRIPT = the_program.SCRIPT
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


CAMERA = "PresentersCam_01011855_C002.mov"
STEM = "PresentersCam_01011855_C002"
# A speaker hidden in the column Sync only does not show, and the
# camera's own sound on "use": both stand in the fields handed in.
ROWS = [vpm.SpeakerName("Guest"), vpm.SpeakerName("", "PresentersCam")]

print("1. The name the table offers")
sync = vpm.camera_name_suggestion("Interview", CAMERA, ROWS, False, True)
check("under Sync only a camera with a speaker is offered its stem",
      sync == STEM, "%r against %r" % (sync, STEM))
cut = vpm.camera_name_suggestion("Interview", CAMERA, ROWS, False)
check("and in a cut project the same rows still name the speaker",
      "Guest" in cut and cut != STEM, "%r -- wanted 'Guest' in it" % cut)

print("\n2. A name kept from Sync only")
known = vpm.camera_names_offered("Interview", CAMERA, ROWS)
check("a stem kept from Sync only counts as offered, not typed",
      STEM in known, "%r not among %s" % (STEM, sorted(known)))

print("\n3. The command line with cameras only")
HERE = tempfile.mkdtemp(prefix="vpm_syncstem_")
VIDEO = os.path.join(HERE, CAMERA)
SOUND = os.path.join(HERE, "cameraaudio.wav")
handed = {}


def two_tracks(video_paths, tmpdir, cameras=None, title=""):
    """Two voices off the one camera, as a camera with two mics gives."""
    return [{"audio": SOUND, "blocks": [SOUND], "speakers": who,
             "camera": VIDEO, "from_camera": VIDEO}
            for who in ("Presenter", "Guest")]


def kept(args, plan, cameras, video_paths, title):
    """Where the plan hands on: keep its cameras and stop there."""
    handed["cameras"] = cameras
    return 0


vpm.plan_from_camera_audio = two_tracks
vpm.sample_count = lambda path: 48000 * 60
vpm.build_common_timebase = kept
args = vpm.build_argument_parser().parse_args(
    ["--project-type", "sync", "--multitrack", "--dry-run", VIDEO])
args.name_camera = "Camera Original"
code = vpm.show_multitrack_plan(args, [], [VIDEO])
named = [c.get("name") for c in handed.get("cameras") or []]
check("under Sync only the run names a camera after its own file",
      code == 0 and named == [STEM],
      "rc %s, cameras named %s, wanted [%r]" % (code, named, STEM))

print("\n4. Two cameras with one file name")
# Two cameras of one make both write C003 into their own folders. The
# handover finds each written file by its camera's name, so the two
# names must differ -- told apart as the plan tells their tracks apart.
A, B = (os.path.join(HERE, side, CAMERA) for side in ("a", "b"))
APART = [STEM, STEM + " 2"]


def one_each(video_paths, tmpdir, cameras=None, title=""):
    """One voice off each camera, named apart as the plan names them."""
    return [{"audio": SOUND, "blocks": [SOUND], "speakers": who,
             "camera": v, "from_camera": v} for v, who in zip((A, B), APART)]


vpm.plan_from_camera_audio = one_each
handed.clear()
args = vpm.build_argument_parser().parse_args(
    ["--project-type", "sync", "--multitrack", "--dry-run", A, B])
args.name_camera = "Camera Original"
code = vpm.show_multitrack_plan(args, [], [A, B])
named = [c.get("name") for c in handed.get("cameras") or []]
check("two cameras with one stem keep two names, cameras alone",
      code == 0 and named == APART,
      "rc %s, cameras named %s, wanted %s" % (code, named, APART))
PLAN = os.path.join(HERE, "recordings.json")
with open(PLAN, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "tracks_of": [
        {"audio": SOUND, "blocks": [SOUND], "speakers": who, "camera": ""}
        for who in ("Guest", "Presenter")]}, f)
handed.clear()
args = vpm.build_argument_parser().parse_args(
    ["--project-type", "sync", "--multitrack", "--dry-run",
     "--assign", PLAN, A, B])
args.name_camera = "Camera Original"
code = vpm.show_multitrack_plan(args, [], [A, B])
named = [c.get("name") for c in handed.get("cameras") or []]
check("and beside recordings, where each camera is named after its file",
      code == 0 and named == APART,
      "rc %s, cameras named %s, wanted %s" % (code, named, APART))
shutil.rmtree(HERE, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
