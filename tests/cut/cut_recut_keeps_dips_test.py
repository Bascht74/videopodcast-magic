# -*- coding: utf-8 -*-
"""A slider's recut cuts at the same sound dips a full dry run cuts at.

The interview fixture with a plan, dry run twice in this process, the
window's way: under a handover key each, a second wide-shot deadline in
the second. Then the first handover cut again by the second's numbers,
the way a moved slider does. Sections: the envelope kept (named by the
handover, one entry for one material, read by the preview), the ground
(without it the recut lands elsewhere), and the recut against the run.
The limit: the dips come from the fixture's synthetic voices.
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
import glob
import json
import shutil
import tempfile
import time
import the_program
from fixture_root import fixture

WORK = tempfile.mkdtemp(prefix="vpm_recutdips_")
os.environ["VPM_CACHE"] = os.path.join(WORK, "cache")
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


def stop():
    """Nothing further can be asked, so count what there is and go."""
    shutil.rmtree(WORK, ignore_errors=True)
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


MEDIA = fixture("interview")


def found(pattern):
    """The fixture's files by a pattern, sorted."""
    return sorted(glob.glob(os.path.join(MEDIA, pattern)))


if not (found("GuestCam_*.mov") and found("PresentersCam_*.mov")
        and found("WideCam_*.mov") and found("Guest_*.wav")):
    print("SKIPPED: no interview fixture -- tests/fixtures.sh builds it "
          "under VPM_FIXTURES (looked in %s)" % MEDIA)
    stop()

# Guest on the guest's camera, both presenters on theirs, the wide one
# free: three pictures to cut between.
PLAN = os.path.join(WORK, "assign.json")
with open(PLAN, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "created_by": "test",
               "production": "P", "tracks_of": [
                   {"audio": found(pattern)[0], "blocks": found(pattern),
                    "speakers": who, "camera": found(cam)[0],
                    "camera_audio": False}
                   for who, pattern, cam in (
                       ("Guest", "Guest_*.wav", "GuestCam_*.mov"),
                       ("Presenter", "Presenter_*.wav",
                        "PresentersCam_*.mov"),
                       ("CoPresenter", "CoPresenter_*.wav",
                        "PresentersCam_*.mov"))]}, f)
# Short turns here, so a wide shot every few seconds: each one's point
# is set by the clock and then moved onto the nearest dip in the sound.
LINE = (["videopodcast_magic.py"] + found("*.wav") + found("*.mov")
        + ["--out", os.path.join(WORK, "out"), "--dry-run",
           "--without-auphonic", "--no-metrics", "--no-speech-recognition",
           "--no-transcript-file", "--multitrack", "--assign", PLAN,
           "--wide-after", "4", "--wide-length", "1.5",
           "--min-edit-duration", "1.0"])
FIRST = LINE + ["--wide-latest", "5"]
SECOND = LINE + ["--wide-latest", "4.5"]


def dry_run(argv, key):
    """A dry run of *argv* keeping its handover under *key*: its code."""
    ap = vpm.build_argument_parser()
    args = ap.parse_args(vpm.time_values_joined(list(argv[1:])))
    args._handover_key = key
    old = sys.argv
    sys.argv = list(argv)
    try:
        return vpm.run_from_command_line(args, ap)
    finally:
        sys.argv = old


def shots(d):
    """The cut of a handover as (from, to, camera)."""
    return [(x["start"], x["end"], x["camera"]) for x in (d or {}).get(
        "cut") or []]


def apart(a, b):
    """How many shots of cut *a* the cut *b* does not hold, and the first."""
    missing = [x for x in a if x not in b]
    return len(missing), (missing[:1] or [None])[0]


codes = (dry_run(FIRST, "handover_first"), dry_run(SECOND, "handover_second"))
kept = vpm.stage_get("handover_first")
full = vpm.stage_get("handover_second")
if codes != (0, 0) or not kept or not full:
    check("both dry runs of the fixture end with a handover kept", False,
          "return codes %s, handovers kept: first %s, second %s"
          % (codes, bool(kept), bool(full)))
    stop()

print("The envelope kept")
levels = vpm.kept_levels(kept)
length = float(kept.get("length_s") or 0.0)
check("a dry run keeps its level envelope with the handover",
      abs(len(levels) - length / 0.01) <= 2.0,
      "%d values kept for %.2f s, %d wanted"
      % (len(levels), length, round(length / 0.01)))
entries = glob.glob(os.path.join(WORK, "cache", "*", "stages", "levels_*"))
check("two dry runs of one material keep one envelope",
      len(entries) == 1 and kept.get("levels_key") == full.get("levels_key"),
      "%d entries, the two handovers name %s and %s"
      % (len(entries), kept.get("levels_key"), full.get("levels_key")))
read = vpm.sound_levels_for(kept)
check("the preview reads the kept envelope where no file is left",
      len(read) == len(levels) and read == levels,
      "%d values read, %d kept" % (len(read), len(levels)))

print("\nThe ground")
bare = json.loads(json.dumps(kept))
bare.pop("levels_key", None)
vpm.handover_recut(bare, SECOND, "handover_bare")
off, first_off = apart(shots(full), shots(vpm.stage_get("handover_bare")))
check("without the envelope the recut lands off the run's dips",
      off > 0, "%d of %d shots apart, the first %s"
      % (off, len(shots(full)), first_off))

print("\nThe recut against the run")
recut_ok = vpm.handover_recut(kept, SECOND, "handover_recut")
again = shots(vpm.stage_get("handover_recut"))
off, first_off = apart(shots(full), again)
check("a recut over the kept handover cuts where a full dry run cuts",
      recut_ok and off == 0 and len(again) == len(shots(full)),
      "kept %s, %d of %d shots apart (the recut has %d), the first %s"
      % (recut_ok, off, len(shots(full)), len(again), first_off))

stop()
