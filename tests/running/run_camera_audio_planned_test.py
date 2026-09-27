# -*- coding: utf-8 -*-
"""The bar plans the camera-audio stage exactly when the run pulls it.

The run pulls a camera's audio wherever the window's plan makes it a
track, with the Multitrack tick or without it; the bar used to plan the
stage by the tick. Planned by the tick and not pulled, the bar held a
share nobody reported; pulled and not planned, the unknown stage came
last in the order, and beginning it marked every stage done -- the bar
stood at nearly all of it from the first minute. The plan is built by
the window's own builder, run_argv, and handed to the count Start uses:

  * tick off, a camera set to its own sound: pulled, and planned
  * tick on, two recordings and no camera sound: neither

The window's bar itself is not opened here: that the window hands this
count to run_stages is one line in fittings.run_plan_build.
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
import shutil
import tempfile
import time
import the_program

vpm = the_program.load()

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


folder = tempfile.mkdtemp(prefix="vpm_camaudio_plan_")


def empty(name):
    """A file of that name; the builder reads names, not sound."""
    path = os.path.join(folder, name)
    open(path, "wb").close()
    return path


GUEST = empty("Guest_Take0021A_Timecode.wav")
PRESENTER = empty("Presenter_REC00021.wav")
GUEST_CAM = empty("GuestCam_01011858_C003.mov")
WIDE_CAM = empty("WideCam_01011855_C001.mov")
CAMERAS = [(GUEST_CAM, "video"), (WIDE_CAM, "video")]


def plan_of(multitrack, rows, sounds):
    """The plan the window hands the run, by the window's own builder."""
    _argv, plan, messages = vpm.run_argv({
        "files": [(p, "audio") for p in sounds] + CAMERAS,
        "clip_kinds": {}, "out_folder": folder, "dry_run": True,
        "multitrack": multitrack, "camera_audio_only": False,
        "project_type": "cut", "rows": rows,
        "cameras": [{"path": p, "name": ""} for p, _k in CAMERAS],
        "production": "Planned", "in_point": "", "out_point": "",
        "cut": {}, "wide_at_edges": True, "key": "", "preset": "",
        "done_folder": ""}, os.path.join(folder, "plan.json"))
    return plan, messages


def stages_for(plan):
    """What the bar is planned with for that plan: stage names."""
    return [n for n, _w, _c in vpm.run_stages(
        vpm.camera_audio_pulled(plan), len(CAMERAS), False)]


print("1. Tick off, the guest camera set to its own sound")
plan, said = plan_of(False, [
    {"blocks": [GUEST], "speakers": "Guest",
     "camera_choice": os.path.basename(GUEST_CAM)},
    {"blocks": [GUEST_CAM], "speakers": "GuestCam", "own_audio": True,
     "from_camera": GUEST_CAM,
     "camera_choice": os.path.basename(GUEST_CAM)}], [GUEST])
marked = [os.path.basename(t.get("audio") or "")
          for t in (plan or {}).get("tracks_of") or ()
          if t.get("camera_audio")]
pulled = vpm.camera_audio_pulled(plan)
check("a camera set to its own sound is pulled with the tick off",
      pulled == 1, "%d camera(s) counted, wanted 1; the plan marks %s for "
      "extraction, the builder said %r" % (pulled, marked, said))
names = stages_for(plan)
check("and the bar plans the camera-audio stage for it",
      "camera audio" in names, "planned: %s" % names)

print("\n2. Tick on, two recordings, no camera sound")
plan, said = plan_of(True, [
    {"blocks": [GUEST], "speakers": "Guest",
     "camera_choice": os.path.basename(GUEST_CAM)},
    {"blocks": [PRESENTER], "speakers": "Presenter",
     "camera_choice": os.path.basename(WIDE_CAM)}], [GUEST, PRESENTER])
pulled = vpm.camera_audio_pulled(plan)
check("two recordings with the tick on pull no camera",
      pulled == 0, "%d camera(s) counted, wanted 0 among %d tracks; the "
      "builder said %r" % (pulled, len((plan or {}).get("tracks_of") or ()),
                           said))
names = stages_for(plan)
check("and the bar plans no camera-audio stage there",
      "camera audio" not in names, "planned: %s" % names)

shutil.rmtree(folder, True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
