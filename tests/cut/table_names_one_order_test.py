# -*- coding: utf-8 -*-
"""Two speakers on one camera stand in one order in its file and track.

The sections: the file name the table offers, the label of the Resolve
track the handover writes, the name the command line gives a camera
alone after the tracks off its sound, a name the table offered in row
order, still known as offered; the first three, the window's newer
answer and the run's handover over names plain sorting misplaces; in a
real run the tracks in the camera's file, one nobody named among them,
and the plan's preview. The rows are never in alphabetical order.
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
import re
import subprocess
import tempfile
import threading
import time
import the_program

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


CAMERA = "CamB_0001.mov"
# The recording's row stands above the camera's own sound: Presenter
# first, Guest second -- not alphabetical, on purpose.
ROWS = [vpm.SpeakerName("Presenter"), vpm.SpeakerName("", "Guest")]

print("1. The file name the table offers")
offered = vpm.camera_name_suggestion("Interview", CAMERA, ROWS)
check("a camera's file name lists its speakers alphabetically",
      offered == "CamB_Guest+Presenter_0001",
      "%r against 'CamB_Guest+Presenter_0001'" % offered)

print("\n2. The label of the camera's Resolve track")
handover, why = vpm.build_handover(
    [("Presenter", [(0.0, 5.0)]), ("Guest", [(5.0, 10.0)])], 10.0,
    {"Presenter": CAMERA, "Guest": CAMERA},
    [{"track": "CamB_0001", "file": os.path.join(HERE, CAMERA)}])
labels = vpm.legend_names((handover or {}).get("cameras") or [])
check("and its track label lists them in the same order",
      labels.get("CamB_0001") == "Guest + Presenter",
      "%r against 'Guest + Presenter' -- %s" % (labels, why or "built"))

print("\n3. The name the command line gives a camera alone")
VIDEO = os.path.join(HERE, CAMERA)
alone = vpm.cameras_named_by_tracks(
    [{"camera": VIDEO, "speakers": "Presenter"},
     {"camera": VIDEO, "speakers": "Guest"}])
names = [c.get("name") for c in alone]
check("a camera named by its tracks lists them alphabetically too",
      names == ["Guest+Presenter"],
      "%s against ['Guest+Presenter']" % names)

print("\n4. A name offered before the order was one")
old = "CamB_Presenter+Guest_0001"
known = vpm.camera_names_offered("Interview", CAMERA, ROWS)
check("a name offered in the order of the rows counts as never typed",
      old in known, "%r not among %s" % (old, sorted(known)))

print("\n5. Names a plain sort puts elsewhere")
# Rows Paul, Ozlem with an umlaut on its O, anna, Bob. Sorted as a
# reader sorts them: anna, Bob, the umlaut name, Paul. Plain sorting
# puts Bob before anna and the umlaut after Paul, and sorting without
# case alone still puts it after Paul.
UMLAUT = "\u00d6zlem"
MIXED = ["Paul", UMLAUT, "anna", "Bob"]
READ = ["anna", "Bob", UMLAUT, "Paul"]
VIDEO = os.path.join(HERE, CAMERA)
offered = vpm.camera_name_suggestion(
    "Interview", CAMERA, [vpm.SpeakerName(n) for n in MIXED])
check("lower case and an umlaut stand where a reader expects them",
      offered == "CamB_" + "+".join(READ) + "_0001",
      "%r against %r" % (offered, "CamB_" + "+".join(READ) + "_0001"))
handover, why = vpm.build_handover(
    [(n, [(i * 2.0, i * 2.0 + 2.0)]) for i, n in enumerate(MIXED)], 8.0,
    dict((n, CAMERA) for n in MIXED),
    [{"track": "CamB_0001", "file": VIDEO}])
labels = vpm.legend_names((handover or {}).get("cameras") or [])
check("and the handover's track label sorts them the same way",
      labels.get("CamB_0001") == " + ".join(READ),
      "%r against %r -- %s" % (labels, " + ".join(READ), why or "built"))
alone = [c.get("name") for c in vpm.cameras_named_by_tracks(
    [{"camera": VIDEO, "speakers": n} for n in MIXED])]
check("and so does the name the command line gives the camera",
      alone == ["+".join(READ)], "%s against %r" % (alone, "+".join(READ)))
fresh = vpm.wide_marks_applied({"cameras": [{"source": VIDEO}]}, [],
                               dict((n, CAMERA) for n in MIXED), False)
fresh = [c.get("speakers") for c in fresh.get("cameras") or []]
check("and so does the window's newer answer in a handover",
      fresh == [READ], "%s against %s" % (fresh, [READ]))


class Args(object):
    """What write_handover asks a run's arguments for, and no more."""
    production = "Interview"
    resolve = False
    lufs = None
    intro = None
    outro = None


WROTE = tempfile.mkdtemp(prefix="vpm_oneorder_")
with contextlib.redirect_stdout(io.StringIO()):
    vpm.write_handover(Args(), [{"name": n, "camera": VIDEO} for n in MIXED],
                       [{"name": "CamB_0001", "video": VIDEO}],
                       [(VIDEO, {"fps": 25.0, "duration": 8.0})], WROTE,
                       None, None, length=8.0)
try:
    with open(os.path.join(WROTE, "Interview_resolve.json"),
              encoding="utf-8") as f:
        written = [c.get("track") for c in json.load(f).get("cameras") or []]
except (OSError, ValueError) as e:
    written = ["no handover: %s" % e]
check("and so does the handover the run writes",
      written == [" + ".join(READ)],
      "%s against %r" % (written, " + ".join(READ)))

print("\n6. The tracks inside the camera's file")
# A real run, Sync only and --without-auphonic: three recordings on one
# camera in row order Presenter, one nobody named, Guest. The file the
# run writes is asked with ffprobe, and the plan's preview beside it.
ASK = 120.0
STILL = 120.0
HOME = tempfile.mkdtemp(prefix="vpm_oneorder_")
LENGTH = 2 * vpm.AXIS_MIN_WINDOW_S
# The tone in bursts of one uneven pattern, so the sound places every
# recording against the camera it was taken out of.
BURSTS = [(0.6, 1.3), (1.9, 2.1), (2.9, 3.2), (3.7, 8.9), (9.6, 10.0),
          (10.8, 11.9), (12.3, 12.45), (13.4, 14.3), (15.1, 15.35),
          (16.2, 17.8), (18.5, 18.65), (19.3, 20.3), (21.0, 21.4),
          (21.9, 22.2)]


def make(argv, path):
    """Material made with ffmpeg; a precondition, not a judgement."""
    made = subprocess.run(["ffmpeg", "-v", "error"] + argv + [path, "-y"],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          timeout=ASK)
    assert made.returncode == 0 and os.path.exists(path), made.stdout
    return path


def run(argv):
    """Start the program and watch it: (code, what it said, stuck)."""
    kid = subprocess.Popen(argv, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           env=dict(os.environ, QT_QPA_PLATFORM="offscreen"))
    pieces = []

    def read():
        """Collect what the program writes until it closes the pipe."""
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
    last, seen, stuck = time.time(), 0, False
    while kid.poll() is None:
        time.sleep(0.25)
        if len(pieces) != seen:
            seen, last = len(pieces), time.time()
        if time.time() - last > STILL:
            stuck = True
            kid.kill()
            break
    reader.join(10)
    kid.wait()
    text = b"".join(pieces).decode("utf-8", "replace")
    return kid.returncode, re.sub(r"\x1b\[[0-9;]*m", "", text), stuck


gate = "+".join("between(t,%g,%g)" % burst for burst in BURSTS)
FILMED = make(["-f", "lavfi", "-i",
               "testsrc=size=160x90:rate=25:duration=%g" % LENGTH,
               "-f", "lavfi", "-i",
               "aevalsrc='0.5*sin(2*PI*330*t)*(%s)':s=48000:d=%g"
               % (gate, LENGTH), "-c:v", "libx264", "-preset", "ultrafast",
               "-pix_fmt", "yuv420p", "-c:a", "aac", "-timecode",
               "18:55:04:00", "-shortest"], os.path.join(HOME, CAMERA))
# Three recorders, not three channels of one: those would be one track.
TAKEN = [make(["-i", FILMED, "-vn", "-c:a", "pcm_s16le"],
              os.path.join(HOME, name))
         for name in ("TASCAM_0001.wav", "ZOOM0001.wav", "DR10L_0001.wav")]
PLAN = os.path.join(HOME, "plan.json")
with open(PLAN, "w", encoding="utf-8") as f:
    json.dump({"format": vpm.FILE_FORMAT, "created_by": "test",
               "production": "Interview",
               "tracks_of": [{"audio": path, "blocks": [path],
                              "speakers": who, "camera": FILMED}
                             for path, who in zip(
                                 TAKEN, ("Presenter", "", "Guest"))],
               "cameras": [{"video": FILMED, "name": "CamB_0001"}]}, f)
code, said, stuck = run([sys.executable, SCRIPT, "--project-type", "sync",
                         "--without-auphonic", "--multitrack", "--assign",
                         PLAN, "--out", os.path.join(HOME, "out")]
                        + TAKEN + [FILMED])
WRITTEN = os.path.join(HOME, "out", "CamB_0001_audio.mov")
try:
    probed = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
         "stream_tags=handler_name", "-of", "json", WRITTEN],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        timeout=ASK).stdout
except subprocess.TimeoutExpired:
    probed = b""
held = [(st.get("tags") or {}).get("handler_name", "") for st in
        json.loads(probed.decode("utf-8") or "{}").get("streams", [])]
check("and the tracks in its file follow them, the mix's label first",
      code == 0 and not stuck and held[:4] == [
          "Mix Guest + Presenter + ZOOM0001.wav", "Guest", "Presenter",
          "ZOOM0001.wav"],
      "rc %s, stood still %s, the file holds %s" % (code, stuck, held))
track = re.escape(vpm.T("        Track %d: %s").strip()).replace(
    re.escape("%d"), r"\d+").replace(re.escape("%s"), "(.*)")
# Windows ends each printed line in \r\n, and (.*) would keep the \r.
preview = [p.rstrip("\r") for p in re.findall(track, said)[:4]]
# The preview says ? for a track nobody named, the file its file name;
# either stands where the file has it.
check("and the plan's preview lists them in the file's order",
      preview in (["Mix Guest + Presenter + ?", "Guest", "Presenter", "?"],
                  ["Mix Guest + Presenter + ZOOM0001.wav", "Guest",
                   "Presenter", "ZOOM0001.wav"]),
      "the preview lists %s, the file holds %s" % (preview, held[:4]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
