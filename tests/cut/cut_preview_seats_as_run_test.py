# -*- coding: utf-8 -*-
"""The preview seats every speaker on the camera the run seats them on.

Two productions, each with voices told apart under one recording whose
row still carries a name of its own and "no camera of its own", and a
second row set that way too: first under a recorder's file, then under
a camera's own sound. Per production the run's side -- run_plan, the
assignment file, write_handover -- against the preview's, driven the
way preview_compute drives it: speakers_to_cameras, build_handover and
wide_marks_applied. Held against each other: who sits on each camera,
and which cameras count as the wide shot. The limit: the window itself
is not opened, so its two calls are taken on trust.
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
import contextlib
import io
import json
import shutil
import tempfile
import time
import types

import the_program

began = time.time()
vpm = the_program.load()
vpm.set_language("en")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


ROOM = tempfile.mkdtemp(prefix="preview_seats_")
PRESENTER = os.path.join(ROOM, "Presenter.mov")
GUEST = os.path.join(ROOM, "Guest.mov")
WIDE = os.path.join(ROOM, "WideCam.mov")
CAMERAS = [PRESENTER, GUEST, WIDE]
RECORDER = os.path.join(ROOM, "ZOOM0001_Tr1.WAV")
MUSIC = os.path.join(ROOM, "ZOOM0001_Tr2.WAV")
LENGTH = 60.0
SPEECH = [("Presenter", [(0.0, 30.0)]), ("Guest", [(30.0, 60.0)])]
VOICES = [("Presenter", PRESENTER), ("Guest", GUEST)]


def settings(name, assign):
    """The run's settings, as far as write_handover reads them."""
    return types.SimpleNamespace(
        production=name, assign=assign, wide_shot=[], project_type="cut",
        suffix="_audio", in_point=None, out_point=None, intro=None,
        outro=None, resolve=False, lufs=None)


def the_run(name, rows, own):
    """Who the run seats on each camera, and which ones are wide.

    The window's values as the run is handed them, run_plan's tracks as
    the time base passes them on, the assignment file carrying the
    voices, and the handover write_handover leaves: {camera: (who, wide)}.
    """
    where = tempfile.mkdtemp(prefix=name + "_", dir=ROOM)
    values = {
        "files": [(p, "video") for p in CAMERAS]
                 + [(p, "audio") for p in (RECORDER, MUSIC)],
        "rows": [{"blocks": [first], "speakers": who, "camera_choice": cam,
                  "own_audio": first in own, "from_camera": own.get(first, "")}
                 for first, who, cam in rows],
        "cameras": [{"path": p, "name": ""} for p in CAMERAS],
        "voices": [{"name": who, "camera": cam} for who, cam in VOICES],
        "speakers_of": {"segments": [[0.0, 60.0, "SPEAKER_00"]]},
        "production": name}
    cameras = [{"video": p, "name": os.path.splitext(os.path.basename(p))[0]}
               for p in CAMERAS]
    plan = vpm.run_plan(values, values["rows"], cameras, False)
    assign = os.path.join(where, "assign.json")
    with open(assign, "w", encoding="utf-8") as f:
        json.dump(plan, f)
    tracks = [{"name": e["speakers"], "camera": e["camera"]}
              for e in plan["tracks_of"]]
    videos = [(p, {"fps": 25.0, "width": 1920, "height": 1080,
                   "duration": LENGTH}) for p in CAMERAS]
    with contextlib.redirect_stdout(io.StringIO()):
        vpm.write_handover(settings(name, assign), tracks, cameras, videos,
                           where, 36000.0,
                           (PRESENTER, {"fps": 25.0, "tc": "10:00:00:00"}),
                           results=[], cut=[], segment_list=SPEECH,
                           length=LENGTH)
    with open(os.path.join(where, name + "_resolve.json"),
              encoding="utf-8") as f:
        d = json.load(f)
    return dict((os.path.basename(c["source"]),
                 (sorted(c.get("speakers") or []), bool(c.get("wide"))))
                for c in d.get("cameras") or ())


def the_preview(rows, own):
    """The same answer from the preview, in preview_compute's order."""
    assign_lines = [([first], vpm.Value(who), vpm.Value(cam))
                    for first, who, cam in rows]
    voice_lines = [("SPEAKER_%02d" % i, vpm.Value(who), vpm.Value(cam))
                   for i, (who, cam) in enumerate(VOICES)]
    seats = vpm.speakers_to_cameras(assign_lines, voice_lines, own, CAMERAS,
                                    False)
    d, _why = vpm.build_handover(
        SPEECH, LENGTH, seats,
        [{"track": os.path.splitext(os.path.basename(p))[0], "file": p,
          "start_s": 0.0, "wide_marked": False} for p in CAMERAS])
    d = vpm.wide_marks_applied(d, [], seats, False)
    return dict((os.path.basename(c["file"]),
                 (sorted(c.get("speakers") or []), bool(c.get("wide"))))
                for c in (d or {}).get("cameras") or ())


def compared(run, preview, part):
    """Where the two answers part: *part* 0 is who, 1 is wide."""
    apart = ["%s: %r in the run, %r in the preview"
             % (cam, run.get(cam, ((), None))[part],
                preview.get(cam, ((), None))[part])
             for cam in sorted(set(run) | set(preview))
             if run.get(cam, ((), None))[part]
             != preview.get(cam, ((), None))[part]]
    return not apart and bool(run), "; ".join(apart) or (
        "%d cameras alike" % len(run))


print("1. Voices told apart under a recorder's file")
RECORDER_ROWS = [(RECORDER, "CoPresenter", vpm.MIX_ONLY),
                 (MUSIC, "Music", vpm.MIX_ONLY)]
try:
    run, preview = the_run("Recorder", RECORDER_ROWS, {}), \
        the_preview(RECORDER_ROWS, {})
except Exception as e:
    run, preview = {}, {"-": (("%s: %s" % (type(e).__name__, e),), None)}
ok, why = compared(run, preview, 0)
check("a recorder's voices: the preview seats each camera as the run",
      ok, why)
ok, why = compared(run, preview, 1)
check("a recorder's voices: the same cameras count as the wide shot",
      ok, why)

print("\n2. Voices told apart under a camera's own sound")
CAMERA_ROWS = [(WIDE, "CoPresenter", vpm.MIX_ONLY),
               (MUSIC, "Music", vpm.MIX_ONLY)]
try:
    run, preview = the_run("Camera", CAMERA_ROWS, {WIDE: WIDE}), \
        the_preview(CAMERA_ROWS, {WIDE: WIDE})
except Exception as e:
    run, preview = {}, {"-": (("%s: %s" % (type(e).__name__, e),), None)}
ok, why = compared(run, preview, 0)
check("a camera's own voices: the preview seats each camera as the run",
      ok, why)
ok, why = compared(run, preview, 1)
check("a camera's own voices: the same cameras count as the wide shot",
      ok, why)

shutil.rmtree(ROOM, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
