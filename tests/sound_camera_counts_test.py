# -*- coding: utf-8 -*-
"""A camera counts as a track once the assignment says so.

A camera with its own microphone is a track like any other, and that is
settled in the assignment, not on the command line: one microphone plus two
cameras with sound is three tracks, and Multitrack has to be allowed.
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


one = silence("one.wav")
two = silence("two.wav")

args = Args()
check("one recording alone is not enough for Multitrack",
      "MULTITRACK" in (vpm.check_mode_fits_input([one], args) or ""))
check("two recordings are",
      vpm.check_mode_fits_input([one, two], args) is None)

args.assign = assignment([
    {"blocks": [one], "speakers": "Mic", "own_audio": False},
    {"blocks": ["/x/cam1.mov"], "speakers": "Cam 1", "own_audio": True},
])
check("cameras_as_tracks counts the marked camera",
      vpm.cameras_as_tracks(args) == 1,
      "got %d" % vpm.cameras_as_tracks(args))
check("one recording plus one camera track is enough",
      vpm.check_mode_fits_input([one], args) is None,
      (vpm.check_mode_fits_input([one], args) or "").split("\n")[0])

args.assign = assignment([
    {"blocks": ["/x/cam1.mov"], "speakers": "Cam 1", "camera_audio": True},
    {"blocks": ["/x/cam2.mov"], "speakers": "Cam 2", "camera_audio": True},
])
check("two cameras and no microphone are enough as well",
      vpm.check_mode_fits_input([], args) is None)
check("the older key camera_audio counts too",
      vpm.cameras_as_tracks(args) == 2)

args.assign = assignment([
    {"blocks": [one], "speakers": "Mic", "own_audio": False},
])
check("an assignment with nothing marked changes nothing",
      "MULTITRACK" in (vpm.check_mode_fits_input([one], args) or ""))

args.assign = os.path.join(WORK, "not_there.json")
check("a missing assignment file is not an error",
      vpm.cameras_as_tracks(args) == 0)
broken = os.path.join(WORK, "broken.json")
open(broken, "w").write("{not json")
args.assign = broken
check("nor is an unreadable one", vpm.cameras_as_tracks(args) == 0)

args.assign = None
args.multitrack = False
check("without the tick nothing is checked at all",
      vpm.check_mode_fits_input([one], args) is None)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
