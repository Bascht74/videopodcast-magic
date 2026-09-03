# -*- coding: utf-8 -*-
"""A recording made of blocks is placed as one recording.

A tail of a few minutes has too little in common with an hour of
material to be placed by its sound, and weighed on its own it was
turned down -- so the whole recording carried "the sound is not usable"
while its head block lay exactly right on the axis. Files the window
holds as one recording are taken to fit: the head is measured, and what
follows it takes its place from the head.

Two cases, and telling them apart is the point. The same file put in on
its own is no continuation: it is measured like anything else and may
be turned down, and that is the way back for anybody who wants it
weighed.

The measurement is replaced by one that answers at once and writes down
which files it was handed, so what reaches it is a number rather than a
guess. What is asked is where the recording ends up, never how that
place was arrived at.
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")

import importlib.util

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


# ------------------------------------------------------------- the material
# A recording of two blocks beside two other files. Nothing is opened:
# the measurement below answers for them.
FOLDER = "/tmp/vpm-blocks-nothing-is-opened"
HEAD = os.path.join(FOLDER, "Presenter_REC0018.wav")
TAIL = os.path.join(FOLDER, "Presenter_REC0019.wav")
GUEST = os.path.join(FOLDER, "Guest_Take0021A_Timecode.wav")
CAMERA = os.path.join(FOLDER, "WideCam_01011855_C001.mov")
EVERY = [HEAD, TAIL, GUEST, CAMERA]

# The head runs an hour, the tail seven minutes, and the recorder
# writes them without a gap between.
RUNS = {HEAD: 3721.0, TAIL: 439.0, GUEST: 4000.0, CAMERA: 4000.0}
HEAD_AT = 57223.6086
ELSEWHERE = 12000.0    # where a measurement of the tail alone would land
CLOSE_ENOUGH = 0.1     # seconds -- well inside a frame

AS_ONE = {HEAD: [HEAD, TAIL]}
ON_ITS_OWN = {HEAD: [HEAD], TAIL: [TAIL]}


def runs_for(path):
    return RUNS.get(path, 0.0)


handed = []


def measure_stand_in(paths, tc_of=None, HOP=5.0):
    """A measurement that cannot place the tail, and says which it saw.

    Whatever it is handed except the tail gets a place; the tail is
    turned down in all four lists at once, which is what the real one
    does to a file neither its sound nor a clock can place.
    """
    handed.append([os.path.basename(p) for p in paths])
    on = [p for p in paths if p != TAIL]
    off = [p for p in paths if p == TAIL]
    return ({"axis": dict((vpm.path_key(p), HEAD_AT) for p in on),
             "clock": dict((vpm.path_key(p), 1.0) for p in on),
             "absolute": True, "weak": off, "unplaceable": off,
             "brief": off, "no_place": off},
            vpm.T('time axis measured and tied to the timecode'))


def measure_places_the_tail(paths, tc_of=None, HOP=5.0):
    """The same, but it does place the tail -- somewhere else entirely."""
    handed.append([os.path.basename(p) for p in paths])
    at = dict((vpm.path_key(p), HEAD_AT) for p in paths)
    at[vpm.path_key(TAIL)] = ELSEWHERE
    return ({"axis": at,
             "clock": dict((vpm.path_key(p), 1.0) for p in paths),
             "absolute": True, "weak": [], "unplaceable": [],
             "brief": [], "no_place": []},
            vpm.T('time axis measured and tied to the timecode'))


def answer_for(blocks, measure=measure_stand_in):
    """The window's own route, with the measurement replaced."""
    was = vpm.measure_time_axis
    del handed[:]
    try:
        vpm.measure_time_axis = measure
        return vpm.axis_with_blocks(EVERY, lambda p: None, 5.0, blocks,
                                    runs_for)
    finally:
        vpm.measure_time_axis = was


print("1. Held as one recording")
data, text = answer_for(AS_ONE)
axis = data.get("axis") or {}
saw = handed[0] if handed else []
check("a continuation is never weighed on its own",
      os.path.basename(TAIL) not in saw,
      "the measurement was handed %d files: %r" % (len(saw), saw))
where = axis.get(vpm.path_key(TAIL))
check("the recording is on the axis with its continuation",
      where is not None,
      "the tail sits at %r, %d files on the axis" % (where, len(axis)))
wanted = HEAD_AT + RUNS[HEAD]
check("and the continuation lies where its head block runs out",
      where is not None and abs(where - wanted) <= CLOSE_ENOUGH,
      "%r against %.4f s, allowed %.2f s apart"
      % (where, wanted, CLOSE_ENOUGH))
refused = [name for name in ("weak", "no_place", "unplaceable", "brief")
           if TAIL in (data.get(name) or ())]
check("and the recording carries no refusal", not refused,
      "turned down in %d of 4 lists: %r, the line says %r"
      % (len(refused), refused, text))

print("\n2. The same file, put in on its own")
data, _text = answer_for(ON_ITS_OWN)
axis = data.get("axis") or {}
saw = handed[0] if handed else []
check("a file put in on its own is measured and may be turned down",
      os.path.basename(TAIL) in saw
      and vpm.path_key(TAIL) not in axis
      and TAIL in (data.get("no_place") or ()),
      "handed to the measurement %s, on the axis %s, in no_place %s"
      % (os.path.basename(TAIL) in saw, vpm.path_key(TAIL) in axis,
         TAIL in (data.get("no_place") or ())))

print("\n3. A measurement that puts the continuation somewhere else")
data, _text = answer_for(AS_ONE, measure_places_the_tail)
axis = data.get("axis") or {}
check("the grouping settles the place, not a reading of the tail",
      abs((axis.get(vpm.path_key(TAIL)) or 0.0) - wanted) <= CLOSE_ENOUGH,
      "the tail sits at %r against %.4f s, and %.1f s was offered"
      % (axis.get(vpm.path_key(TAIL)), wanted, ELSEWHERE))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
