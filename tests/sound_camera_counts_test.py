# -*- coding: utf-8 -*-
"""A camera counts as a track once the assignment says so.

A camera with its own microphone is a track like any other, and that is
settled in the assignment, not on the command line. In order: the
material each claim rests on, recordings counted on their own, a camera
beside a microphone, cameras without one, the three keys that mark a
camera -- own_audio, camera_audio, from_camera -- an assignment that
marks nothing, one that is missing and one that cannot be read, and the
tick that turns the whole question off.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, json, struct, sys, tempfile, time
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
WORK = tempfile.mkdtemp(prefix="cameratrack_")
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def answer(msg):
    """What the mode check replied, in one line, for the failure line."""
    if msg is None:
        return "nothing to report"
    return vpm.strip_marks(msg).split("\n")[0]


def size(path):
    """How many bytes lie there, and 0 where nothing does."""
    return os.path.getsize(path) if os.path.exists(path) else 0


def silence(name, seconds=1.0):
    """A short wav, enough to be counted as a recording."""
    path = os.path.join(WORK, name)
    n = int(seconds * vpm.SR)
    b = b"\x00\x00" * n
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 36 + len(b)) + b"WAVE")
        f.write(b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, vpm.SR,
                                      vpm.SR * 2, 2, 16))
        f.write(b"data" + struct.pack("<I", len(b)) + b)
    return path


class Args(object):
    multitrack = True
    no_follow_ups = True
    apart = ()
    assign = None
    auphonic_key = "x"
    without_auphonic = False


def assignment(rows):
    path = os.path.join(WORK, "assign_%d.json" % len(os.listdir(WORK)))
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"tracks_of": rows, "cameras": []}, f)
    return path


def wrote(name, rows):
    """The assignment a claim below rests on, and that it really got there.

    Without this the run below reads no rows out of a file that was
    never written, counts no camera, and the red line blames the
    program for what the material never offered it.
    """
    path = assignment(rows)
    try:
        with open(path, encoding="utf-8") as f:
            back = json.load(f).get("tracks_of") or []
    except (ValueError, OSError):
        back = []
    check(name, len(back) == len(rows),
          "%d rows written, %d read back from %s"
          % (len(rows), len(back), os.path.basename(path)))
    return path


one = silence("one.wav")
two = silence("two.wav")
there = [p for p in (one, two) if os.path.exists(p)]
check("both test recordings are there before anything is asked of them",
      len(there) == 2 and min([os.path.getsize(p) for p in there] or [0]) > 44,
      "2 wanted, %d there, sizes %s bytes against a 44 byte header"
      % (len(there), [os.path.getsize(p) for p in there]))

args = Args()
alone = vpm.check_mode_fits_input([one], args)
check("one recording alone is not enough for Multitrack",
      "MULTITRACK" in (alone or ""),
      "1 recording and %d camera tracks, the answer was: %s"
      % (vpm.cameras_as_tracks(args), answer(alone)))
pair = vpm.check_mode_fits_input([one, two], args)
check("two recordings are",
      pair is None,
      "2 recordings and %d camera tracks, the answer was: %s"
      % (vpm.cameras_as_tracks(args), answer(pair)))

args.assign = wrote("the assignment that marks one camera was written", [
    {"blocks": [one], "speakers": "Mic", "own_audio": False},
    {"blocks": ["/x/cam1.mov"], "speakers": "Cam 1", "own_audio": True},
])
marked = vpm.cameras_as_tracks(args)
check("cameras_as_tracks counts the marked camera",
      marked == 1,
      "1 wanted, got %d out of 2 rows, 1 of them marked" % marked)
with_cam = vpm.check_mode_fits_input([one], args)
check("one recording plus one camera track is enough",
      with_cam is None,
      "1 recording and %d camera tracks, the answer was: %s"
      % (marked, answer(with_cam)))

args.assign = wrote("the assignment that marks two cameras was written", [
    {"blocks": ["/x/cam1.mov"], "speakers": "Cam 1", "camera_audio": True},
    {"blocks": ["/x/cam2.mov"], "speakers": "Cam 2", "camera_audio": True},
])
two_cams = vpm.cameras_as_tracks(args)
no_mic = vpm.check_mode_fits_input([], args)
check("two cameras and no microphone are enough as well",
      no_mic is None,
      "0 recordings and %d camera tracks, the answer was: %s"
      % (two_cams, answer(no_mic)))
check("the older key camera_audio counts too",
      two_cams == 2,
      "2 wanted, got %d out of 2 rows carrying camera_audio" % two_cams)

args.assign = wrote(
    "the assignment that marks a camera the third way was written",
    [{"blocks": ["/x/cam3.wav"], "speakers": "Cam 3",
      "from_camera": "/x/cam3.mov"}])
third = vpm.cameras_as_tracks(args)
check("the third key from_camera counts too",
      third == 1,
      "1 wanted, got %d out of 1 row carrying from_camera" % third)

args.assign = wrote("the assignment that marks nothing was written", [
    {"blocks": [one], "speakers": "Mic", "own_audio": False},
])
nothing = vpm.check_mode_fits_input([one], args)
check("an assignment with nothing marked changes nothing",
      "MULTITRACK" in (nothing or ""),
      "1 recording and %d camera tracks, the answer was: %s"
      % (vpm.cameras_as_tracks(args), answer(nothing)))

args.assign = os.path.join(WORK, "not_there.json")
gone = vpm.cameras_as_tracks(args)
check("a missing assignment file is not an error",
      gone == 0,
      "0 wanted, got %d from a path that is not there" % gone)
broken = os.path.join(WORK, "broken.json")
open(broken, "w").write("{not json")
check("the unreadable assignment is there to be read",
      size(broken) > 0,
      "%d bytes at %s, and more than 0 wanted -- a file that is not "
      "there is counted by the check above, not by this one"
      % (size(broken), os.path.basename(broken)))
args.assign = broken
unreadable = vpm.cameras_as_tracks(args)
check("nor is an unreadable one",
      unreadable == 0,
      "0 wanted, got %d from %d bytes that are no json"
      % (unreadable, size(broken)))

args.assign = None
args.multitrack = False
off = vpm.check_mode_fits_input([one], args)
check("without the tick nothing is checked at all",
      off is None,
      "multitrack off, 1 recording, the answer was: %s" % answer(off))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
