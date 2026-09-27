# -*- coding: utf-8 -*-
"""A camera's own sound on "no camera of its own" seats nobody there.

The wide camera's own sound goes into the run through run_plan, the
assignment file and write_handover, as the window hands it over. In
order: with voices told apart under it and the row on "no camera of its
own", as the window sets it by itself; the same row on it by hand with
no voices; the row with no camera picked, which still seats its name
on the camera the sound came from; and the sound is still taken from
that camera either way. The limit: the window is not opened, and
nothing is aligned or rendered -- write_handover is handed the tracks.
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


ROOM = tempfile.mkdtemp(prefix="no_own_camera_")
PRESENTER = os.path.join(ROOM, "PresentersCam_01011855_C002.mov")
GUEST = os.path.join(ROOM, "GuestCam_01011858_C003.mov")
WIDE = os.path.join(ROOM, "WideCam_01011855_C001.mov")
CAMERAS = [PRESENTER, GUEST, WIDE]
PRESENTER_MIC = os.path.join(ROOM, "Presenter_REC00021.wav")
GUEST_MIC = os.path.join(ROOM, "Guest_Take0021A_Timecode.wav")
LENGTH = 60.0
SPEECH = [("Presenter", [(0.0, 30.0)]), ("Guest", [(30.0, 60.0)])]


def the_run(name, rows, voices=()):
    """The run's plan and what write_handover makes of it.

    *rows* are (first file, name, camera choice); the wide camera's
    file is its own sound. Returns (the plan's entry for that sound,
    {camera file name: (who sits on it, whether it is wide)}).
    """
    where = tempfile.mkdtemp(prefix=name + "_", dir=ROOM)
    own = {WIDE: WIDE}
    values = {
        "files": [(p, "video") for p in CAMERAS]
                 + [(p, "audio") for p in (PRESENTER_MIC, GUEST_MIC)],
        "rows": [{"blocks": [first], "speakers": who, "camera_choice": cam,
                  "own_audio": first in own, "from_camera": own.get(first, "")}
                 for first, who, cam in rows],
        "cameras": [{"path": p, "name": ""} for p in CAMERAS],
        "voices": [{"name": who, "camera": cam} for who, cam in voices],
        "production": name}
    if voices:
        values["speakers_of"] = {"segments": [[0.0, 60.0, "SPEAKER_00"]]}
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
    settings = types.SimpleNamespace(
        production=name, assign=assign, wide_shot=[], project_type="cut",
        suffix="_audio", in_point=None, out_point=None, intro=None,
        outro=None, resolve=False, lufs=None)
    with contextlib.redirect_stdout(io.StringIO()):
        vpm.write_handover(settings, tracks, cameras, videos, where, 36000.0,
                           (PRESENTER, {"fps": 25.0, "tc": "10:00:00:00"}),
                           results=[], cut=[], segment_list=SPEECH,
                           length=LENGTH)
    with open(os.path.join(where, name + "_resolve.json"),
              encoding="utf-8") as f:
        d = json.load(f)
    entry = next((e for e in plan["tracks_of"]
                  if e["blocks"][:1] == [WIDE]), {})
    return entry, dict((os.path.basename(c["source"]),
                        (sorted(c.get("speakers") or []), bool(c.get("wide"))))
                       for c in d.get("cameras") or ())


def on_wide(handover):
    """Who sits on the wide camera, and whether it is the wide shot."""
    return handover.get(os.path.basename(WIDE), (["(no such camera)"], None))


def tried(name, rows, voices=()):
    """the_run, with a crash as an answer the checks can print."""
    try:
        return the_run(name, rows, voices)
    except Exception as e:
        return {}, {os.path.basename(WIDE): (
            ["%s: %s" % (type(e).__name__, e)], None)}


print("Voices told apart under the wide camera's own sound")
entry_voiced, handover = tried(
    "Voiced", [(WIDE, "Room", vpm.MIX_ONLY)],
    [("Presenter", PRESENTER), ("Guest", GUEST)])
who, wide = on_wide(handover)
check("under its voices, the camera whose sound it is seats nobody",
      who == [], "wide camera seats %r, wanted []" % (who,))
check("that camera is the wide shot although its sound is heard",
      wide is True, "wide %r, wanted True; seats %r" % (wide, who))

print("\nThe wide camera's own sound on no camera of its own by hand")
MICS = [(PRESENTER_MIC, "Presenter", PRESENTER),
        (GUEST_MIC, "Guest", GUEST)]
entry_by_hand, handover = tried(
    "ByHand", MICS + [(WIDE, "Room", vpm.MIX_ONLY)])
who, wide = on_wide(handover)
check("a camera's own sound set so by hand seats its name nowhere",
      who == [] and wide is True,
      "wide camera seats %r, wide %r; wanted [] and True" % (who, wide))

print("\nThe wide camera's own sound with no camera picked")
_entry, handover = tried("Unpicked", MICS + [(WIDE, "Room", "")])
who, wide = on_wide(handover)
check("a camera's own sound with no camera picked sits on its own",
      who == ["Room"] and wide is False,
      "wide camera seats %r, wide %r; wanted ['Room'] and False"
      % (who, wide))

print("\nWhere the sound comes from")
came = [(e.get("from_camera"), e.get("camera_audio"))
        for e in (entry_voiced, entry_by_hand)]
check("the sound is still taken from the camera it was recorded on",
      came == [(WIDE, True)] * 2,
      "(from_camera, camera_audio) %r, wanted the wide camera and True "
      "twice" % ([(os.path.basename(f or ""), a) for f, a in came],))

shutil.rmtree(ROOM, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
