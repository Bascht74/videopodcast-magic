# -*- coding: utf-8 -*-
"""One simple-path run end to end: every promise kept, and it agrees.

The run without Multitrack, started the way the command line starts it,
over the interview fixture -- three microphones, three cameras, no
window, nothing on the network. Afterwards the files are asked, not the
program. The sections: the material is there and the run came back
without standing still and without a line that reads like a fault; what
the plan promised lies in the folder and nothing else does; the camera
files carry the tracks the plan and the run each named, in that order;
the handover lies beside its two lists and their EDLs, is stamped, and
names the same files, the same tracks in them and the same cameras as
the cut list, and its cut covers the window without gap or overlap;
cut list, EDL and handover hold the same shots, and the speaker list,
its EDL and the handover the same passages; and the log's own count is
what the files hold.

The limit of the method: the cameras and the microphones of that folder
share no signal, so every offset measured over it is arbitrary. Nothing
here is a claim about where the axis landed, only about the results
agreeing with each other.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import csv
import glob
import json
import subprocess
import sys
import tempfile
import threading
import time

sys.path.insert(0, HERE)
from fixture_root import fixture

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
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
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


# No output at all for this long, and the run is stuck rather than slow.
# The program writes a progress bar while it works, so silence is the
# sign of life and not a clock: a builder three times slower than this
# machine still says something every few seconds, so the bound costs
# nothing and is never reached in a run that is merely slow.
STILL = 120.0
STEP = 0.25


def run_and_watch(argv):
    """Start the program, watch it work, hand back what it printed.

    Returns (return code, everything it printed, whether it stood
    still, how long it took).
    """
    kid = subprocess.Popen(argv, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           env=dict(os.environ,
                                    QT_QPA_PLATFORM="offscreen"))
    pieces = []

    def read():
        while True:
            try:
                piece = os.read(kid.stdout.fileno(), 65536)
            except OSError:
                break
            if not piece:
                break
            pieces.append(piece)

    reader = threading.Thread(target=read)
    reader.daemon = True
    reader.start()
    started, last, seen, stuck = time.time(), time.time(), 0, False
    while kid.poll() is None:
        time.sleep(STEP)
        if len(pieces) != seen:
            seen, last = len(pieces), time.time()
        if time.time() - last > STILL:
            stuck = True
            kid.kill()
            break
    took = time.time() - started
    reader.join(10)
    try:
        kid.stdout.close()
    except Exception:
        pass
    kid.wait()
    return (kid.returncode, b"".join(pieces).decode("utf-8", "replace"),
            stuck, took)


def seconds_of_timecode(text, fps):
    """A timecode back to seconds, counting the frames by hand.

    Not the program's own converter: two files that disagree only show
    it where the second reading takes another route than the first.
    """
    hour, minute, second, frame = [int(x) for x in text.split(":")]
    return hour * 3600 + minute * 60 + second + frame / float(fps)


def edl_events(path):
    """(record in, record out, clip name) for every event of an EDL."""
    events, times = [], None
    for line in open(path, encoding="utf-8").read().splitlines():
        part = line.split()
        if len(part) == 8 and part[0].isdigit():
            times = (part[6], part[7])
        elif line.startswith("*") and times:
            events.append((times[0], times[1], line.split(":", 1)[1].strip()))
            times = None
    return events


def first_of(rows):
    """The first row that differed, or nothing where none did."""
    return rows[0] if rows else ()


def tracks_in_file(path):
    """The names of the audio tracks of one file, in file order."""
    answer = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream_tags=handler_name",
         "-of", "csv=p=0", path], capture_output=True, text=True)
    return [l.strip() for l in answer.stdout.splitlines() if l.strip()]


MEDIA = fixture("interview")
RECORDINGS = sorted(glob.glob(os.path.join(MEDIA, "*.wav")))
CAMERAS = sorted(glob.glob(os.path.join(MEDIA, "*.mov")))
OUT = tempfile.mkdtemp(prefix="vpm_simplepath_")

print("1. The run goes through, the way the command line starts it")
check("the fixture holds the microphones and cameras of a whole job",
      len(RECORDINGS) >= 2 and len(CAMERAS) >= 2,
      "%d recordings and %d cameras under %s -- 'cd tests && bash "
      "fixtures.sh' builds them"
      % (len(RECORDINGS), len(CAMERAS), MEDIA))
if len(RECORDINGS) < 2 or len(CAMERAS) < 2:
    stop()

ARGV = ([sys.executable, SCRIPT, "--without-auphonic", "--out", OUT,
         "--no-metrics", "--no-speech-recognition", "--no-transcript-file"]
        + RECORDINGS + CAMERAS)
code, said, stuck, took = run_and_watch(ARGV)
print("    %d recordings, %d cameras, %.1f s"
      % (len(RECORDINGS), len(CAMERAS), took))
check("the run kept working and never stood still", not stuck,
      "nothing printed for %.0f s in the %.0f s it ran" % (STILL, took))
if stuck:
    stop()
check("the run came back with 0", code == 0, "return code %d" % code)
check("and it broke off nowhere", "Traceback" not in said,
      "the traceback begins at character %d of %d"
      % (said.find("Traceback"), len(said)))
error_lines = [l.strip() for l in said.splitlines() if "rror" in l]
check("and no line of its log reads as an error", not error_lines,
      "%d of %d lines, the first: %s"
      % (len(error_lines), len(said.splitlines()),
         (error_lines + [""])[0][:90]))

print("\n2. What the plan promised is what the folder holds")
# The plan block reads "    <source>  ->  <name>.mov" and under each of
# them one line per audio track. Both wordings come out of the
# catalogue, so the reading does not tie itself to one language, and
# the pairs are kept whole: the source name is the key section 3 looks
# the written file up by.
head = vpm.T('\n  This produces:').strip()
track_head = vpm.T('        Track %d: %s').split("%d")[0]
promised, promised_tracks, at = [], {}, said.find(head)
if at >= 0:
    for line in said[at + len(head):].splitlines()[1:]:
        if "  ->  " in line:
            promised.append(tuple(x.strip() for x in line.split("  ->  ")))
        elif line.startswith(track_head) and promised:
            promised_tracks.setdefault(promised[-1][0], []).append(
                line.split(":", 1)[1].strip())
        elif line.strip() and not line.startswith(" "):
            break
want = [b for _a, b in promised]
written = sorted(os.path.basename(p) for p in glob.glob(OUT + "/*.mov"))
check("the plan promises a file for every camera it was given",
      len(promised) == len(CAMERAS),
      "%d promised against %d cameras" % (len(promised), len(CAMERAS)))
check("every file the plan promised lies in the output folder",
      not (set(want) - set(written)),
      "%d of %d missing: %s"
      % (len(set(want) - set(written)), len(want),
         sorted(set(want) - set(written))[:3]))
check("and the folder holds no camera file the plan did not promise",
      not (set(written) - set(want)),
      "%d of %d were never promised: %s"
      % (len(set(written) - set(want)), len(written),
         sorted(set(written) - set(want))[:3]))

print("\n3. The camera files carry the tracks the plan and the run named")
# Three routes to one list. What the plan promised before the run, what
# the run says it wrote afterwards, and what ffprobe finds in the file
# -- and the file is the one that decides: a run that lies about itself
# is what this is for.
mark = vpm.T('\nPROCESSING: %s').strip().split("%s")[0]
track_said = vpm.T('  Audio track %d:   %s').split("%d")[0]
named = {}
for block in said.split(mark)[1:]:
    lines = block.splitlines()
    named[lines[0].strip()] = [l.split(":", 1)[1].strip() for l in lines
                               if l.startswith(track_said)]
check("the run named the audio tracks of every camera it wrote",
      len(named) == len(CAMERAS) and all(named.values()),
      "%d cameras spoken of against %d given, %d of them without a track"
      % (len(named), len(CAMERAS), len([v for v in named.values() if not v])))
holds = {name: tracks_in_file(os.path.join(OUT, name))
         for name in written}
different = [(a, named.get(a), holds.get(b)) for a, b in promised
             if named.get(a) != holds.get(b)]
check("and every camera file holds those tracks, in that order",
      bool(promised) and not different,
      "%d of %d differ, the first: %s"
      % (len(different), len(promised), first_of(different)))
misnamed = [(a, promised_tracks.get(a), holds.get(b)) for a, b in promised
            if promised_tracks.get(a) != holds.get(b)]
check("and the plan named the tracks that file holds, in that order",
      bool(promised) and not misnamed,
      "%d of %d differ, the first: %s"
      % (len(misnamed), len(promised), first_of(misnamed)))

print("\n4. The handover knows those files and covers the window")
found = sorted(glob.glob(OUT + "/*_resolve.json"))
check("the handover lies in the output folder", len(found) == 1,
      "%d found in %s" % (len(found), OUT))
if len(found) != 1:
    stop()
STEM = found[0][:-len("_resolve.json")]
BESIDE = ["_cameracut.csv", "_cameracut.edl", "_speakers.csv",
          "_speakers.edl"]
gone = [tail for tail in BESIDE if not os.path.exists(STEM + tail)]
check("and the two lists and their two EDLs lie beside it", not gone,
      "%d of %d missing: %s" % (len(gone), len(BESIDE), gone))
if gone:
    stop()
hand = json.load(open(found[0], encoding="utf-8"))
FPS = hand.get("fps") or 25.0
FRAME = 1.0 / FPS
cameras = hand.get("cameras") or []
cut = hand.get("cut") or []
check("and it is stamped with the file format of the day",
      hand.get("format") == vpm.FILE_FORMAT,
      "stamped %r, the format of the day is %r"
      % (hand.get("format"), vpm.FILE_FORMAT))
check("the handover knows exactly the camera files the run wrote",
      sorted(os.path.basename(c.get("file") or "") for c in cameras)
      == written,
      "%d in the handover against %d in the folder: %s"
      % (len(cameras), len(written),
         sorted(os.path.basename(c.get("file") or "") for c in cameras)))
CAMERA_TRACK = vpm.build_argument_parser().get_default("name_camera")
off = [(os.path.basename(c.get("file") or ""),
        list(c.get("audio_tracks") or []) + [CAMERA_TRACK],
        holds.get(os.path.basename(c.get("file") or "")))
       for c in cameras
       if list(c.get("audio_tracks") or []) + [CAMERA_TRACK]
       != holds.get(os.path.basename(c.get("file") or ""))]
check("and the tracks it names for each are the tracks in that file",
      bool(cameras) and not off,
      "%d of %d differ, the first: %s"
      % (len(off), len(cameras), first_of(off)))
shots = list(csv.DictReader(open(STEM + "_cameracut.csv", encoding="utf-8")))
seen_cameras = sorted({r["Camera"] for r in shots})
check("every camera the cut list names is one the handover knows",
      set(seen_cameras) <= {c.get("camera") for c in cameras},
      "%s in the cut list against %s in the handover"
      % (seen_cameras,
         sorted(c.get("camera") for c in cameras)))
length = hand.get("length_s") or 0.0
check("the handover's cut covers the window from end to end",
      bool(cut) and abs(cut[0].get("start", -1) - 0.0) <= FRAME
      and abs(cut[-1].get("end", -1) - length) <= FRAME,
      "%d shots from %.3f to %.3f, the window is 0.000 to %.3f, a frame "
      "is %.3f s" % (len(cut), (cut or [{}])[0].get("start", -1),
                     (cut or [{}])[-1].get("end", -1), length, FRAME))
seams = [abs(cut[i]["end"] - cut[i + 1]["start"]) for i in range(len(cut) - 1)]
check("and it leaves no gap and no overlap between two shots",
      bool(seams) and max(seams) < 1e-6,
      "%d seams, the worst is %.6f s apart" % (len(seams),
                                               max(seams or [0.0])))

print("\n5. Cut list, EDL and handover hold the same shots")
shot_edl = edl_events(STEM + "_cameracut.edl")
check("cut list, EDL and handover count the same shots",
      len(shots) == len(shot_edl) == len(cut),
      "%d in the cut list, %d in the EDL, %d in the handover"
      % (len(shots), len(shot_edl), len(cut)))
ZERO = seconds_of_timecode(hand.get("start_tc") or "00:00:00:00", FPS)
drift = [(r["Shot"],
          round(seconds_of_timecode(r["Start TC"], FPS) - ZERO
                - c["start"], 3),
          round(seconds_of_timecode(r["End TC"], FPS) - ZERO - c["end"], 3))
         for r, c in zip(shots, cut)
         if abs(seconds_of_timecode(r["Start TC"], FPS) - ZERO
                - c["start"]) > FRAME
         or abs(seconds_of_timecode(r["End TC"], FPS) - ZERO
                - c["end"]) > FRAME]
check("and shot for shot the cut list and the handover agree",
      bool(shots) and not drift,
      "%d of %d shots more than one frame (%.3f s) apart, the first "
      "(shot, start, end): %s" % (len(drift), len(shots), FRAME,
                                  first_of(drift)))
apart = [(r["Shot"], e, (r["Start TC"], r["End TC"],
                         r["Speaker"] or r["Camera"]))
         for r, e in zip(shots, shot_edl)
         if e != (r["Start TC"], r["End TC"], r["Speaker"] or r["Camera"])]
check("and the EDL says the same as the cut list, shot for shot",
      bool(shots) and not apart,
      "%d of %d differ, the first (shot, EDL, cut list): %s"
      % (len(apart), len(shots), first_of(apart)))

print("\n6. Speaker list, EDL and handover hold the same passages")
turns = list(csv.DictReader(open(STEM + "_speakers.csv", encoding="utf-8")))
turn_edl = edl_events(STEM + "_speakers.edl")
sections = [(s["name"], a, b) for s in (hand.get("speakers") or [])
            for a, b in s.get("sections") or []]
check("speaker list, EDL and handover count the same passages",
      len(turns) == len(turn_edl) == len(sections),
      "%d in the speaker list, %d in the EDL, %d in the handover"
      % (len(turns), len(turn_edl), len(sections)))
# Both lists in the same order, so passage n is passage n: the speaker
# list is written in time order and the handover groups by speaker.
mine = sorted((r["Speaker"],
               round(seconds_of_timecode(r["Start TC"], FPS) - ZERO, 2),
               round(seconds_of_timecode(r["End TC"], FPS) - ZERO, 2))
              for r in turns)
theirs = sorted((n, round(a, 2), round(b, 2)) for n, a, b in sections)
elsewhere = [(x, y) for x, y in zip(mine, theirs)
             if x[0] != y[0] or abs(x[1] - y[1]) > FRAME
             or abs(x[2] - y[2]) > FRAME]
check("and passage for passage the speaker list and the handover agree",
      bool(turns) and not elsewhere,
      "%d of %d more than one frame (%.3f s) apart, the first (list, "
      "handover): %s" % (len(elsewhere), len(turns), FRAME,
                         first_of(elsewhere)))
other = [(e, (r["Start TC"], r["End TC"], r["Speaker"]))
         for r, e in zip(turns, turn_edl)
         if e != (r["Start TC"], r["End TC"], r["Speaker"])]
check("and the EDL says the same as the speaker list, passage for passage",
      bool(turns) and not other,
      "%d of %d differ, the first (EDL, speaker list): %s"
      % (len(other), len(turns), first_of(other)))

print("\n7. The log counts what the files hold")
people = sorted({r["Speaker"] for r in turns})
shortest = min([float(r["Duration s"]) for r in shots] or [0.0])
sentence = vpm.T('  %s speakers, %s shots, shortest %s s') % (
    vpm.group_text(len(people)), vpm.group_text(len(shots)),
    vpm.decimal_text("%.1f" % shortest))
piece = vpm.T('  %s speakers, %s shots, shortest %s s').split("%s")[1]
its_own = next((l.strip() for l in said.splitlines() if piece in l), "")
check("the log's count of speakers and shots is what the files hold",
      sentence in said,
      "the files hold %d speakers and %d shots, the shortest %.2f s; "
      "the log says %r" % (len(people), len(shots), shortest, its_own))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
