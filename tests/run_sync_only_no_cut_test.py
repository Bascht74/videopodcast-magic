# -*- coding: utf-8 -*-
"""A Sync only run leaves no cut, no speaker and no transcript behind.

One recording and every camera of the interview fixture, started the
way the command line starts it with the project type "sync", nothing on
the network. Afterwards the files and the log are asked, not the
program. The sections: the run goes through and says at the top what it
is; the folder holds a camera file per camera, the metrics and the
handover, and no cut list, no speaker list, no transcript; the handover
carries the project type, empty cut, speakers and words, and every
camera plain, its track named after the file or as the line named it;
the log holds no speaker statistics and the metrics no speech time.

The limit of the method: the microphone and the cameras of that folder
share no signal, so nothing here says where the axis landed.
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
# sign of life and not a clock: a builder several times slower than this
# machine still says something every few seconds.
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


MEDIA = fixture("interview")
# One recording: Sync only takes a single audio recording, and the
# fixture's guest microphone is the one that runs the whole length.
RECORDING = sorted(glob.glob(os.path.join(MEDIA, "Guest_*.wav")))[:1]
CAMERAS = sorted(glob.glob(os.path.join(MEDIA, "*.mov")))
OUT = tempfile.mkdtemp(prefix="vpm_synconly_")

print("1. The run goes through and says what it is")
check("the fixture holds one recording and the cameras of a whole job",
      len(RECORDING) == 1 and len(CAMERAS) >= 2,
      "%d recording and %d cameras under %s -- 'cd tests && bash "
      "fixtures.sh' builds them"
      % (len(RECORDING), len(CAMERAS), MEDIA))
if len(RECORDING) != 1 or len(CAMERAS) < 2:
    stop()

# No --no-speech-recognition and no --no-transcript-file on purpose:
# leaving both out is what the project type is for. One camera gets a
# name on the line, the way the window sends its field without a plan;
# the others keep the file's stem.
NAMED_CAM = CAMERAS[0]
ARGV = ([sys.executable, SCRIPT, "--project-type", "sync",
         "--without-auphonic", "--out", OUT,
         "--new-name", NAMED_CAM, "Presenter"] + RECORDING + CAMERAS)
code, said, stuck, took = run_and_watch(ARGV)
print("    %d recording, %d cameras, %.1f s"
      % (len(RECORDING), len(CAMERAS), took))
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
SAID_SO = vpm.T('Project type: Sync only -- no speakers, no transcript, '
                'no cut; the handover carries the multicam timeline '
                'alone.')
PLAN = vpm.T('RECOGNISED PLAN')
check("the log says at the top that this run only synchronises",
      0 <= said.find(SAID_SO) < said.find(PLAN),
      "the sentence stands at character %d, the plan heading at %d"
      % (said.find(SAID_SO), said.find(PLAN)))

print("\n2. The folder holds the cameras, the metrics and the handover, "
      "and nothing of a cut")
written = sorted(os.path.basename(p) for p in glob.glob(OUT + "/*.mov"))
check("a camera file lies in the folder for every camera",
      len(written) == len(CAMERAS),
      "%d files against %d cameras: %s" % (len(written), len(CAMERAS),
                                           written))
found = sorted(glob.glob(OUT + "/*_resolve.json"))
check("the handover lies in the output folder", len(found) == 1,
      "%d found in %s" % (len(found), OUT))
if len(found) != 1:
    stop()
STEM = found[0][:-len("_resolve.json")]
LISTS = ["_cameracut.csv", "_cameracut.edl", "_speakers.csv",
         "_speakers.edl"]
there = [tail for tail in LISTS if os.path.exists(STEM + tail)]
check("no cut list and no speaker list lie beside the handover",
      not there, "%d of %d written: %s" % (len(there), len(LISTS), there))
TRANSCRIPT = [".json", ".srt", ".txt"]
spoken = [tail for tail in TRANSCRIPT if os.path.exists(STEM + tail)]
check("and no transcript", not spoken,
      "%d of %d written: %s" % (len(spoken), len(TRANSCRIPT), spoken))
metrics = STEM + "_metrics.csv"
check("the metrics file is still written", os.path.exists(metrics),
      "%s is %s" % (os.path.basename(metrics),
                    "there" if os.path.exists(metrics) else "missing"))
rows = (list(csv.DictReader(open(metrics, encoding="utf-8")))
        if os.path.exists(metrics) else [])
speech = [r for r in rows if r.get("Area") in ("Cut", "Speech time")]
check("and it holds no cut row and no speech time",
      bool(rows) and not speech,
      "%d rows, %d of them about the cut or speech time: %s"
      % (len(rows), len(speech),
         [(r.get("Area"), r.get("Metric")) for r in speech][:3]))

print("\n3. The handover says sync, knows nobody, and names the tracks "
      "after the files")
hand = json.load(open(found[0], encoding="utf-8"))
cameras = hand.get("cameras") or []
check("the handover says the project type is sync",
      hand.get("project_type") == "sync",
      "project_type is %r" % (hand.get("project_type"),))
check("its cut, speakers and words are empty",
      hand.get("cut") == [] and hand.get("speakers") == []
      and hand.get("words") == [],
      "%d shots, %d speakers, %d words"
      % (len(hand.get("cut") or []), len(hand.get("speakers") or []),
         len(hand.get("words") or [])))
check("it knows a camera for every camera file the run wrote",
      sorted(os.path.basename(c.get("file") or "") for c in cameras)
      == written,
      "%d in the handover against %d in the folder"
      % (len(cameras), len(written)))
named = [(c.get("camera"), c.get("speakers"), c.get("wide"))
         for c in cameras if c.get("speakers") or not c.get("wide")]
check("every camera is a plain camera, nobody on it",
      bool(cameras) and not named,
      "%d of %d carry a name or are not wide: %s"
      % (len(named), len(cameras), named[:3]))
STEMS = sorted(os.path.splitext(os.path.basename(p))[0] for p in CAMERAS
               if p != NAMED_CAM)
unnamed = [c for c in cameras
           if os.path.basename(c.get("source") or "")
           != os.path.basename(NAMED_CAM)]
misnamed = [(c.get("track"), c.get("source")) for c in unnamed
            if c.get("track")
            != os.path.splitext(os.path.basename(c.get("source") or ""))[0]]
check("every track not named on the line is named after its camera file",
      bool(unnamed) and not misnamed
      and sorted(c.get("track") for c in unnamed) == STEMS,
      "%d of %d differ from the file's stem, the first: %s; tracks %s "
      "against files %s"
      % (len(misnamed), len(unnamed), (misnamed + [()])[0],
         sorted(c.get("track") for c in unnamed), STEMS))
given = [c.get("track") for c in cameras
         if os.path.basename(c.get("source") or "")
         == os.path.basename(NAMED_CAM)]
check("and the one named on the line carries that name, under Sync only",
      given == ["Presenter"],
      "%r against ['Presenter'] for %s -- the file's stem is %r"
      % (given, os.path.basename(NAMED_CAM),
         os.path.splitext(os.path.basename(NAMED_CAM))[0]))

print("\n4. The log holds no speaker statistics")
SPEAKER_HEADS = [vpm.T('\nSPEAKERS -- MEASURED HERE').strip(),
                 vpm.T('\nSPEAKERS -- SEPARATED BY VOICE').strip(),
                 vpm.T('\nSPEAKERS\n  Nobody was heard -- no camera '
                       'cut from this.').strip().splitlines()[0]]
heads = [h for h in SPEAKER_HEADS if h in said]
check("no speaker heading stands in the log", not heads,
      "%d of %d headings found: %s" % (len(heads), len(SPEAKER_HEADS),
                                       heads))
TRANSCRIPT_HEAD = vpm.T('\nTRANSCRIPT').strip()
check("and no transcript heading",
      TRANSCRIPT_HEAD not in said,
      "the heading stands at character %d of %d"
      % (said.find(TRANSCRIPT_HEAD), len(said)))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
