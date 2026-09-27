# -*- coding: utf-8 -*-
"""The Kind field calls the camera the wide shot that the run cuts as one.

One production, three cameras: one filmed with a recorder's speaker on
it, one whose own sound is a speaker's and whose card-number file name
gives no name to offer, so the name field stays empty, and one nobody
sits in front of. The window's rows, built as the assignment table
builds them, go once into the run's side -- run_plan, the assignment
file, write_handover -- and once into the Kind field's: the window's
reading of the wide shot, and kind_on_show per camera. Held against
each other: that the run seats the guessed name on the camera with its
own sound, and which cameras each side calls the wide shot. The limit:
the window itself is not opened, so its hand-on of the rows is taken
on trust.
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


ROOM = tempfile.mkdtemp(prefix="wide_is_run_")
PRESENTER = os.path.join(ROOM, "Presenter.mov")
# A card number: the name guess out of it begins with a digit, so the
# name field offers nothing and stays empty.
CARD = os.path.join(ROOM, "0008A.MP4")
WIDE = os.path.join(ROOM, "WideCam.mov")
CAMERAS = [PRESENTER, CARD, WIDE]
RECORDER = os.path.join(ROOM, "ZOOM0001_Tr1.WAV")
LENGTH = 60.0
OWN = {CARD: CARD}

# The rows as the assignment table builds them: a name field with the
# guess behind it, and the camera the row is on -- a camera's own sound
# on its own camera.
ROWS = [([CARD], vpm.SpeakerName("", vpm.guess_camera_name(CARD)),
         vpm.Value(CARD)),
        ([RECORDER], vpm.SpeakerName("Presenter"), vpm.Value(PRESENTER))]
# Precondition of the material, not a verdict: the card name gives no
# guess the field would offer, which is the case this file is about.
assert ROWS[0][1].get() == "", ROWS[0][1].get()


def settings(name, assign):
    """The run's settings, as far as write_handover reads them."""
    return types.SimpleNamespace(
        production=name, assign=assign, wide_shot=[], project_type="cut",
        suffix="_audio", in_point=None, out_point=None, intro=None,
        outro=None, resolve=False, lufs=None)


def the_run():
    """{camera file: (who sits there, wide)} out of the run's handover."""
    where = tempfile.mkdtemp(prefix="run_", dir=ROOM)
    values = {
        "files": [(p, "video") for p in CAMERAS] + [(RECORDER, "audio")],
        "rows": [{"blocks": list(blocks), "speakers": nv.get(),
                  "camera_choice": cv.get(), "own_audio": blocks[0] in OWN,
                  "from_camera": OWN.get(blocks[0], "")}
                 for blocks, nv, cv in ROWS],
        "cameras": [{"path": p, "name": ""} for p in CAMERAS],
        "voices": [], "production": "Card"}
    cameras = [{"video": p, "name": os.path.splitext(os.path.basename(p))[0]}
               for p in CAMERAS]
    plan = vpm.run_plan(values, values["rows"], cameras, False)
    assign = os.path.join(where, "assign.json")
    with open(assign, "w", encoding="utf-8") as f:
        json.dump(plan, f)
    tracks = [{"name": e["speakers"], "camera": e["camera"]}
              for e in plan["tracks_of"]]
    speech = [(t["name"], [(30.0 * i, 30.0 * i + 30.0)])
              for i, t in enumerate(tracks)]
    videos = [(p, {"fps": 25.0, "width": 1920, "height": 1080,
                   "duration": LENGTH}) for p in CAMERAS]
    with contextlib.redirect_stdout(io.StringIO()):
        vpm.write_handover(settings("Card", assign), tracks, cameras, videos,
                           where, 36000.0,
                           (PRESENTER, {"fps": 25.0, "tc": "10:00:00:00"}),
                           results=[], cut=[], segment_list=speech,
                           length=LENGTH)
    with open(os.path.join(where, "Card_resolve.json"),
              encoding="utf-8") as f:
        d = json.load(f)
    return dict((os.path.basename(c["source"]),
                 (sorted(c.get("speakers") or []), bool(c.get("wide"))))
                for c in d.get("cameras") or ())


def the_field():
    """The cameras whose Kind field shows the wide shot, by file name."""
    files = [(p, "video") for p in CAMERAS] + [(RECORDER, "audio")]
    wides, said = vpm.wide_cameras_seen(files, {}, {}, ROWS, [], OWN, False)
    return sorted(os.path.basename(p) for p in CAMERAS
                  if vpm.kind_on_show(vpm.TYPE_CONTENT, p, wides, said)[0]
                  == vpm.TYPE_WIDE)


print("A camera whose own sound carries a speaker with no name typed")
try:
    run = the_run()
except Exception as e:
    run = {"-": (["%s: %s" % (type(e).__name__, e)], None)}
try:
    field = the_field()
except Exception as e:
    field = ["%s: %s" % (type(e).__name__, e)]
seated = run.get(os.path.basename(CARD), ([], None))[0]
check("the run seats the guessed name on the camera with its sound",
      any(n.strip() for n in seated), "%s carries %r in the run; all: %r"
      % (os.path.basename(CARD), seated, run))
in_run = sorted(cam for cam, (_who, wide) in run.items() if wide)
check("the Kind field shows the wide shot the run cuts to",
      field == in_run and bool(in_run),
      "Wide shot in the Kind field: %r, in the run: %r" % (field, in_run))

shutil.rmtree(ROOM, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
