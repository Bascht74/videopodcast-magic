# -*- coding: utf-8 -*-
"""The EDL head says which clock the Timeline runs on, and so do its times.

First write_edl on its own: with the drop-frame flag the head says DROP
FRAME, the semicolon stands before the frames and the reading skips the
dropped numbers; without it the head says NON-DROP FRAME and the colon
stays. Then the run: write_cut_list reads the flag off the reference
clip's timecode and feeds both EDL files from it, and the speaker CSV
beside them reads the same clock. Whether Resolve puts the markers where
the head says is not measured here; the head and the semicolon are what
it reads.
"""
import contextlib
import csv
import io
import os
import re
import shutil
import sys
import tempfile
import time
import the_program

HERE = os.path.dirname(os.path.abspath(__file__))
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


W = tempfile.mkdtemp(prefix="vpmedl_")
FPS = 29.97
# Ten hours on the drop-frame clock: 1,080,000 numbers less the two
# skipped in each of the 540 minutes that are not a tenth -- the frame
# the label 10:00:00;00 names, what the run reads back out of that start,
# and the zero every EDL below counts from.
ZERO = 1078920


def lines_of(path):
    return io.open(path, encoding="utf-8").read().splitlines()


def timecodes_in(lines):
    """Every timecode in the event lines, in order."""
    events = [l for l in lines if l[:3].isdigit()]
    return re.findall(r"\d\d:\d\d:\d\d[:;]\d\d", " ".join(events))


print("1. WRITE_EDL ON ITS OWN")
segments = [(0.0, 10.0, "Guest"), (60.0, 70.0, "Presenter")]
drop = os.path.join(W, "drop.edl")
vpm.write_edl(drop, "Speakers", segments, ZERO, FPS, drop_frame=True)
head = lines_of(drop)[1]
check("a drop-frame EDL announces DROP FRAME in its head",
      head == "FCM: DROP FRAME", "the head reads %r" % head)
times = timecodes_in(lines_of(drop))
check("and every timecode in it carries the semicolon before the frames",
      bool(times) and all(";" in t for t in times), "timecodes %s" % times)
# Sixty seconds at 29.97 are 1,798 frames, so the second event begins
# at frame 1,080,718. Worked out by hand on the drop-frame clock: the
# minute 10:00 is a tenth minute and skips nothing, so 1,798 frames into
# it is the label 10:00:59;28 -- 10:01:00;00 is a skipped number and no
# label at all. Non-drop reads the same frame 10:00:23:28: thirty-six
# seconds, the 1,080 numbers the drop-frame clock has skipped by then.
# Four timecodes an event, so the second event's first is the fifth.
check("the drop-frame reading skips the dropped numbers",
      times[4:5] == ["10:00:59;28"], "the second event begins at %s"
      % (times[4] if len(times) > 4 else "nothing"))
plain = os.path.join(W, "plain.edl")
vpm.write_edl(plain, "Speakers", segments, ZERO, FPS)
head = lines_of(plain)[1]
check("without the flag the head says NON-DROP FRAME",
      head == "FCM: NON-DROP FRAME", "the head reads %r" % head)
times = timecodes_in(lines_of(plain))
check("and the colon stays before the frames",
      bool(times) and not any(";" in t for t in times), "timecodes %s" % times)

print("\n2. THE RUN FEEDS BOTH EDL FILES FROM THE REFERENCE CLIP")
PATH = {}
for _name in ("CamA", "CamB"):
    PATH[_name] = os.path.join(W, _name + ".mov")
    with open(PATH[_name], "w") as _f:
        _f.write("x")
ON = {"Anna": "CamA", "Bert": "CamB"}
SPEECH = [("Anna", [(0.0, 10.0), (20.0, 30.0)]), ("Bert", [(10.0, 20.0)])]
LENGTH = 30.0


def a_run(tc):
    """The cut as a run writes it. Returns the folder written into."""
    args = vpm.build_argument_parser().parse_args([])
    args.production = "Clock"
    folder = tempfile.mkdtemp(prefix="out_", dir=W)
    with contextlib.redirect_stdout(io.StringIO()):
        vpm.write_cut_list(
            args, SPEECH,
            [{"name": who, "camera": PATH[cam]} for who, cam in ON.items()],
            [{"video": PATH[n], "name": n} for n in PATH],
            [(PATH[n], {"width": 1280, "height": 720, "fps": FPS,
                        "duration": LENGTH, "tc": tc}) for n in PATH],
            folder, 36000.0, (PATH["CamA"], {"fps": FPS, "tc": tc}),
            LENGTH, words=(), sound_source="")
    return folder


folder = a_run("10:00:00;00")
speakers = lines_of(os.path.join(folder, "Clock_speakers.edl"))
cameracut = lines_of(os.path.join(folder, "Clock_cameracut.edl"))
check("a semicolon in the reference makes the speaker EDL drop frame",
      speakers[1] == "FCM: DROP FRAME", "the head reads %r" % speakers[1])
check("and the camera cut EDL with it",
      cameracut[1] == "FCM: DROP FRAME", "the head reads %r" % cameracut[1])
# The CSV beside the EDL names the same moment; on two clocks it would
# name two. Through the csv module: a semicolon puts the field in quotes.
first_csv = next(csv.reader(
    lines_of(os.path.join(folder, "Clock_speakers.csv"))[1:2]))
first_edl = timecodes_in(speakers)[:1]
check("the speaker CSV reads the same clock as the EDL",
      first_csv[1:2] == first_edl,
      "CSV start %s against EDL %s" % (first_csv[1:2], first_edl))
folder = a_run("10:00:00:00")
speakers = lines_of(os.path.join(folder, "Clock_speakers.edl"))
cameracut = lines_of(os.path.join(folder, "Clock_cameracut.edl"))
check("a colon in the reference leaves both EDL files non-drop",
      speakers[1] == "FCM: NON-DROP FRAME"
      and cameracut[1] == "FCM: NON-DROP FRAME",
      "the heads read %r and %r" % (speakers[1], cameracut[1]))
shutil.rmtree(W, ignore_errors=True)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
