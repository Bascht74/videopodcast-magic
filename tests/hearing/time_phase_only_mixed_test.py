# -*- coding: utf-8 -*-
"""The phase way places a recording only where its sound was said mixed.

A person says what a recording's sound holds, speech or mixed; the
program no longer guesses. In order: the rule itself; the command line
that carries it; the order the window writes; an old project; a run on
the interview material, whose recordings share nothing with the
cameras and which the phase way lays a hundred seconds out; the preview
on the same; and the phase way not even asked under speech.
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
import argparse
import contextlib
import io
import shutil
import subprocess
import tempfile
import time
import the_program
from fixture_root import fixture

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


# ---------------------------------------------------------------------
# The material: the interview fixture, built once before the fan-out.
# Its two recordings share nothing with the cameras; the phase way,
# asked, lays them anyway -- measured 26.9.2026, 102 and 115 s out.
# ---------------------------------------------------------------------
F = fixture("interview")
CAMS = [os.path.join(F, n) for n in ("WideCam_01011855_C001.mov",
                                     "PresentersCam_01011855_C002.mov",
                                     "GuestCam_01011858_C003.mov")]
REC = os.path.join(F, "Presenter_REC00021.wav")
REC_LATER = os.path.join(F, "Presenter_REC00022.wav")
OTHER = os.path.join(F, "CoPresenter_REC00018.wav")
if not all(os.path.isfile(p) for p in CAMS + [REC, REC_LATER, OTHER]):
    print("SKIPPED: the interview fixture is missing -- run the suite "
          "through run.sh, which builds it into VPM_FIXTURES")
    sys.exit(0)


def read_back(line):
    """Parse a command line; (namespace, refusal) -- a refusal is caught.

    What argparse writes on its way out is kept, not printed: a line
    with "error" in it reads to run.sh as a crash.
    """
    kept = io.StringIO()
    try:
        with contextlib.redirect_stderr(kept):
            return vpm.build_argument_parser().parse_args(line), ""
    except SystemExit:
        return argparse.Namespace(), kept.getvalue().strip()[-80:] or "out"


print("1. The rule")
check("a recording nobody marked holds speech, the phase way off",
      vpm.phase_way_on([REC]) is False,
      "phase_way_on said %r for an unmarked recording, wanted False"
      % vpm.phase_way_on([REC]))
check("a recording marked mixed lets the phase way place it",
      vpm.phase_way_on([REC], "cut", "speech", {REC: "mixed"}) is True,
      "phase_way_on said %r, wanted True"
      % vpm.phase_way_on([REC], "cut", "speech", {REC: "mixed"}))
check("a mark on a later block counts for the whole recording",
      vpm.phase_way_on([REC, REC_LATER], "cut", "speech",
                       {REC_LATER: "mixed"}) is True,
      "phase_way_on said %r for the mark on block two, wanted True"
      % vpm.phase_way_on([REC, REC_LATER], "cut", "speech",
                         {REC_LATER: "mixed"}))
check("a project that only syncs takes mixed whatever is marked",
      vpm.phase_way_on([REC], "sync", "speech", {REC: "speech"}) is True,
      "phase_way_on said %r under sync with speech marked, wanted True"
      % vpm.phase_way_on([REC], "sync", "speech", {REC: "speech"}))
check("a mark for one recording beats the value for all",
      vpm.phase_way_on([REC], "cut", "mixed", {REC: "speech"}) is False,
      "phase_way_on said %r with mixed for all and speech marked, "
      "wanted False"
      % vpm.phase_way_on([REC], "cut", "mixed", {REC: "speech"}))

print("\n2. The command line")
ns, refused = read_back([REC, "--sound-of", REC_LATER, "mixed"])
check("--sound-of reaches the run as the mark for that recording",
      refused == "" and vpm.phase_of_run(ns, [REC, REC_LATER]) is True
      and vpm.phase_of_run(ns, [OTHER]) is False,
      "marked recording %r, the other %r, wanted True and False %s"
      % (vpm.phase_of_run(ns, [REC, REC_LATER]),
         vpm.phase_of_run(ns, [OTHER]), refused))
ns, refused = read_back([REC, "--sound", "mixed"])
check("--sound mixed reaches the run as the value for all",
      refused == "" and vpm.phase_of_run(ns, [OTHER]) is True,
      "the unmarked recording %r, wanted True %s"
      % (vpm.phase_of_run(ns, [OTHER]), refused))
_ns, refused = read_back([REC, "--sound-of", REC, "loud"])
check("a word that is no sound is refused on the line", refused != "",
      "'--sound-of FILE loud' was taken, sound_of %r"
      % ([[os.path.basename(p), w] for p, w
          in getattr(_ns, "sound_of", None) or ()],))

print("\n3. The order the window writes")
FILES = [(p, "video") for p in CAMS] + [(REC, "audio"), (OTHER, "audio")]
argv, _plan, _msgs = vpm.run_argv(
    {"files": FILES, "sound": {REC: "mixed", OTHER: "speech"}})
said = [[os.path.basename(argv[i + 1]), argv[i + 2]]
        for i, w in enumerate(argv or []) if w == "--sound-of"]
check("the window sends a recording set to mixed as --sound-of",
      said[:1] == [[os.path.basename(REC), "mixed"]],
      "--sound-of on the line: %r, wanted [%r, 'mixed']"
      % (said, os.path.basename(REC)))
check("and sends nothing for one left on speech",
      all(os.path.basename(OTHER) != pair[0] for pair in said),
      "--sound-of on the line: %r" % (said,))

print("\n4. An old project, written before the field")
# What project_open makes of a file without "sound": nothing marked.
OLD_CUT = {"project_type": "cut"}
OLD_SYNC = {"project_type": "sync"}
argv, _plan, _msgs = vpm.run_argv(
    {"files": FILES, "project_type": OLD_CUT["project_type"],
     "sound": dict(OLD_CUT.get("sound") or {})})
ns, refused = read_back(list(argv or ["x"])[1:])
check("an old project without the field hands the run speech",
      refused == "" and vpm.phase_of_run(ns, [REC]) is False,
      "phase way %r for a cut project, wanted False %s"
      % (vpm.phase_of_run(ns, [REC]), refused))
argv, _plan, _msgs = vpm.run_argv(
    {"files": FILES, "project_type": OLD_SYNC["project_type"],
     "sound": dict(OLD_SYNC.get("sound") or {})})
ns, refused = read_back(list(argv or ["x"])[1:])
check("an old Sync only project hands the run mixed",
      refused == "" and vpm.phase_of_run(ns, [REC]) is True,
      "phase way %r for a Sync only project, wanted True %s"
      % (vpm.phase_of_run(ns, [REC]), refused))

print("\n5. A run on the interview material")
TMP = tempfile.mkdtemp(prefix="vpm_phase_mixed_")
REFUSED = vpm.no_place_message("Presenter")
BY_PHASE = vpm.T('placed by phase, sharpness %s against a floor of %s, '
                 'drift unknown').split(",")[0]


def run(*extra):
    """One dry run on the material; every line it wrote, as one text."""
    out = tempfile.mkdtemp(dir=TMP)
    r = subprocess.run([sys.executable, SCRIPT] + CAMS + [REC, OTHER]
                       + ["--dry-run", "--out", out, "--without-auphonic"]
                       + list(extra), capture_output=True, text=True)
    return r.stdout + r.stderr


def how_placed(text, name):
    """What the run said of *name*: 'by phase', 'refused', or 'neither'.

    Read off the run's own two sentences, the refusal and the note on
    the line of a recording the phase placed.
    """
    lines = text.replace("\r", "\n").splitlines()
    if any(line.strip().startswith(name + " ") and BY_PHASE in line
           for line in lines):
        return "by phase"
    return "refused" if vpm.no_place_message(name) in text else "neither"


said = run("--project-type", "cut")
check("under speech the run refuses what shares nothing",
      how_placed(said, "Presenter") == "refused",
      "Presenter %s, wanted refused" % how_placed(said, "Presenter"))
said = run("--project-type", "cut", "--sound-of", REC_LATER, "mixed")
check("marked mixed on a block, the run lays it by phase",
      how_placed(said, "Presenter") == "by phase",
      "Presenter %s, wanted by phase" % how_placed(said, "Presenter"))
check("and leaves the recording nobody marked refused",
      how_placed(said, "CoPresenter") == "refused",
      "CoPresenter %s, wanted refused" % how_placed(said, "CoPresenter"))
said = run("--project-type", "sync")
check("a run that only syncs lays both by phase",
      how_placed(said, "Presenter") == "by phase"
      and how_placed(said, "CoPresenter") == "by phase",
      "Presenter %s, CoPresenter %s, wanted both by phase"
      % (how_placed(said, "Presenter"), how_placed(said, "CoPresenter")))

print("\n6. The preview on the same material")
PATHS = CAMS + [REC, OTHER]


def preview(holds, kind="cut"):
    """The preview's axis, asked as the window asks it."""
    on = vpm.axis_phase_on({"project_type": kind, "sound_holds": holds},
                           PATHS, {})
    data, _text = vpm.measure_time_axis(
        PATHS, vpm.file_timecode,
        phase_of=lambda p: vpm.path_key(p) in set(map(vpm.path_key, on)))
    return data


data = preview({})
check("under speech the preview refuses them as the run does",
      REC in (data.get("no_place") or ())
      and vpm.path_key(REC) not in (data.get("axis") or {}),
      "no place: %r" % [os.path.basename(p)
                        for p in data.get("no_place") or ()])
data = preview({REC: "mixed"})
check("marked mixed, the preview lays it where the run does",
      vpm.path_key(REC) in (data.get("axis") or {})
      and OTHER in (data.get("no_place") or ()),
      "on the axis: %r" % sorted(os.path.basename(p)
                                 for p in data.get("axis") or {}))

print("\n7. The phase way itself")
_a, _b, st = vpm.align_audio_to_video(REC, CAMS[1], distance_s=30.0,
                                      sample_points=20, phase=False)
check("under speech the phase way is not even asked",
      st.get("unplaceable") is True and "phase_sharp" not in st,
      "unplaceable %r, phase sharpness %r -- wanted True and none"
      % (st.get("unplaceable"), st.get("phase_sharp")))

shutil.rmtree(TMP, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
