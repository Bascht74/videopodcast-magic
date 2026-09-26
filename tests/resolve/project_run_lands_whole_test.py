# -*- coding: utf-8 -*-
"""A real run's handover lands at the clocks of its material, at both doors.

On way_ground's production, a real run through each door -- the line
the test writes, the window's own Start offscreen -- and each handover
built into both Timelines on a stand-in keeping where each clip lies.
Per door: the run ends with a handover that builds; the camera Timeline
starts on the first camera's clock, each camera at the frame its clock
names; every shot is laid and shows the programme moment its place
names. Then both doors lay the same. The limit: a stand-in, not Resolve,
and "Create Resolve project" is not pressed.
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
import way_ground as ground

SCRIPT = the_program.SCRIPT
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


if ground.missing():
    print("SKIPPED: " + ground.missing())
    stop()

STORE = tempfile.mkdtemp(prefix="vpm_way_store_")
os.environ["VPM_CACHE"] = STORE
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtWidgets
app = QtWidgets.QApplication(sys.argv[:1])
vpm = the_program.load()
vpm.set_language("en")
vpm.list_presets = lambda key: []
vpm.load_api_key = lambda: ""
# Nothing is written down from speech: that would fetch a model, and
# no judgement here is about words.
vpm.words_at_hand = lambda *a, **k: []
vpm.recognise_speech = lambda *a, **k: ([], "")

# The cut Timeline, out of fixtures.sh: it begins where the last camera
# rolls, 5.5 s into the programme, at 10:00:05:15 -- frame 1080165 at
# thirty labels a second -- and runs at the guest camera's 30000/1001.
TIMELINE_AT, TIMELINE_FRAME, TIMELINE_RATE = 5.5, 1080165, 30000 / 1001.0


def camera_of(d):
    """File name of each camera file in a handover -> its camera."""
    return dict((os.path.basename(c.get("file") or ""), c.get("camera"))
                for c in (d or {}).get("cameras") or [])


def lying(d, tl):
    """Camera -> the frames its picture was laid at on a Timeline."""
    named, out = camera_of(d), {}
    for track in tl.tracks["video"]:
        for item in track:
            out.setdefault(named.get(item.name, item.name), []).append(
                item.frame)
    return out


def shown(d, tl):
    """Every shot on the cut Timeline: (camera, programme s, off by s).

    Where it lies on the Timeline in seconds of the programme, and how
    far the picture it shows is from that moment: the camera's first
    frame is where that camera rolls, the table's other clock.
    """
    named, out = camera_of(d), []
    for track in tl.tracks["video"]:
        for item in track:
            cam = named.get(item.name, item.name)
            at = TIMELINE_AT + (item.frame - TIMELINE_FRAME) / TIMELINE_RATE
            picture = ground.ROLLS.get(cam, -99.0) + \
                (item.first or 0) / ground.RATE.get(cam, 1.0)
            out.append((cam, round(at, 3), round(picture - at, 3)))
    return out


WORK = ground.own_folder("lands")
OUT_LINE = os.path.join(WORK, "line")
OUT_WINDOW = os.path.join(WORK, "window")
os.makedirs(OUT_WINDOW)
os.makedirs(os.path.join(WORK, "project"))

print("1. The command line, as a test writes it")
code, said, stuck = ground.line_run(
    ground.line(SCRIPT, ground.separation_file(vpm, WORK), OUT_LINE), STORE)
by_line = ground.handover(OUT_LINE)
tail = [x.strip() for x in said.replace(WORK, "<work>").splitlines()
        if x.strip()][-3:]
check("the line's run came back with 0 and wrote its handover",
      not stuck and code == 0 and by_line is not None,
      "return code %s%s, handover %s -- the log ends: %s"
      % (code, " after standing still" if stuck else "",
         "there" if by_line else "missing", " / ".join(tail)[-240:]))
line_cut, line_cams, line_broke = ground.lay(vpm, by_line) \
    if by_line else (ground.Timeline(""), ground.Timeline(""), "no handover")
check("the line's handover builds both Timelines",
      not line_broke, line_broke)
check("the line's camera Timeline starts on the first camera's clock",
      line_cams.starts[-1:] == [ground.CLOCK[ground.WIDE]],
      "starts set %s, wanted %s last"
      % (line_cams.starts, ground.CLOCK[ground.WIDE]))
laid = lying(by_line, line_cams)
check("at the line, every camera sits at its own clock",
      laid == dict((k, [v]) for k, v in ground.FRAME_OF.items()),
      "%s, wanted %s" % (laid, ground.FRAME_OF))
cuts = shown(by_line, line_cut)
check("at the line, every shot of the cut is laid",
      len(cuts) == len((by_line or {}).get("cut") or []) > 0,
      "%d laid of %d shots"
      % (len(cuts), len((by_line or {}).get("cut") or [])))
off = [c for c in cuts if abs(c[2]) > 1.0 / ground.RATE.get(c[0], 1.0)]
check("at the line, every shot shows the moment it is laid at",
      bool(cuts) and not off,
      "%d of %d shots more than a frame of their camera out, the "
      "largest %.3f s (camera, programme s, off by s): %s"
      % (len(off), len(cuts), max([abs(c[2]) for c in cuts] or [0]), off))

print("\n2. The window, opened on the same production and started")
PROJECT = ground.project_file(vpm, os.path.join(WORK, "project"), OUT_WINDOW)
kept = ground.window_run(vpm, app, PROJECT, {})
by_window = ground.handover(OUT_WINDOW)
check("the window's Start ran a run to its end, with a handover",
      kept["ended"] and not kept["why"] and by_window is not None,
      "loop %s, %s, handover %s"
      % ("came back" if kept["ended"] else "never came back",
         kept["why"] or "nothing given up",
         "there" if by_window else "missing"))
win_cut, win_cams, win_broke = ground.lay(vpm, by_window) \
    if by_window else (ground.Timeline(""), ground.Timeline(""), "no handover")
check("the window's handover builds both Timelines",
      not win_broke, win_broke)
check("the window's camera Timeline starts on the first camera's clock",
      win_cams.starts[-1:] == [ground.CLOCK[ground.WIDE]],
      "starts set %s, wanted %s last"
      % (win_cams.starts, ground.CLOCK[ground.WIDE]))
laid_w = lying(by_window, win_cams)
check("from the window, every camera sits at its own clock",
      laid_w == dict((k, [v]) for k, v in ground.FRAME_OF.items()),
      "%s, wanted %s" % (laid_w, ground.FRAME_OF))
cuts_w = shown(by_window, win_cut)
check("from the window, every shot of the cut is laid",
      len(cuts_w) == len((by_window or {}).get("cut") or []) > 0,
      "%d laid of %d shots"
      % (len(cuts_w), len((by_window or {}).get("cut") or [])))
off_w = [c for c in cuts_w if abs(c[2]) > 1.0 / ground.RATE.get(c[0], 1.0)]
check("from the window, every shot shows the moment it is laid at",
      bool(cuts_w) and not off_w,
      "%d of %d shots more than a frame of their camera out, the "
      "largest %.3f s (camera, programme s, off by s): %s"
      % (len(off_w), len(cuts_w), max([abs(c[2]) for c in cuts_w] or [0]),
         off_w))

print("\n3. The two doors against each other")
ours = [(i.name, i.frame, i.first, i.after)
        for track in line_cut.tracks["video"] for i in track]
theirs = [(i.name, i.frame, i.first, i.after)
          for track in win_cut.tracks["video"] for i in track]
check("both doors lay the same shots at the same frames",
      bool(ours) and ours == theirs and laid == laid_w,
      "line %d pieces, window %d; first to differ: %s; cameras %s / %s"
      % (len(ours), len(theirs),
         next(((a, b) for a, b in zip(ours, theirs) if a != b), "none"),
         laid, laid_w))

shutil.rmtree(WORK, ignore_errors=True)
shutil.rmtree(STORE, ignore_errors=True)
stop()
