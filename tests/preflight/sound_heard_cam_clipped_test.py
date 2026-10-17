# -*- coding: utf-8 -*-
"""A camera whose own sound is a track is counted for clipping, no other.

The preflight counts samples on the stop in every recording, and a
camera's own sound is a recording wherever it is used as a track.
Cameras written here: two seconds of a test picture with a tone driven
past the stop, in 24 bit PCM, and once in AAC. In order: the window's
road, where of two such cameras only the one whose sound is a track
gets the hint, and an AAC one none, there being no stop to count; and
the run's road, which takes the cameras from the plan the window
writes, and with no plan and no recording takes every camera's sound.
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
import json
import shutil
import subprocess
import tempfile
import time
import the_program

began = time.time()
vpm = the_program.load()
vpm.set_language("en")
os.environ["VPM_CACHE"] = tempfile.mkdtemp(prefix="vpm_heard_cam_store_")

done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-62s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


ROOM = tempfile.mkdtemp(prefix="vpm_heard_cam_")


def camera(name, codec):
    """A two-second camera file whose tone stands against the stop."""
    path = os.path.join(ROOM, name)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "testsrc=size=160x120:rate=25:duration=2", "-f", "lavfi",
                    "-i", "sine=frequency=440:duration=2:sample_rate=48000",
                    "-af", "volume=24dB", "-c:v", "libx264", "-pix_fmt",
                    "yuv420p", "-c:a", codec, "-shortest", path], check=True)
    return os.path.abspath(path)


GUEST = camera("GuestCam.mov", "pcm_s24le")
WIDE = camera("WideCam.mov", "pcm_s24le")
PHONE = camera("PhoneCam.mov", "aac")
# The hint's own opening, cut where its numbers begin.
OPENING = vpm.T('Channel %d is against the stop: %s times three samples or '
                'more in a row, the longest %s (%s ms), the first at %s.'
                ).split("%s")[0] % 1


def clipped(findings):
    """The cameras a clipping hint was raised for, by file name."""
    return sorted(os.path.basename(b.file or "") for b in findings
                  if b.kind == "hint" and b.text.startswith(OPENING))


print("1. The window's road")
got = clipped(vpm.collect_findings([], [GUEST, WIDE], fresh=True,
                                   crosstalk=False, heard=[GUEST]))
check("the camera whose own sound is a track is counted for clipping",
      got.count("GuestCam.mov") == 1,
      "hints for %s, wanted one for GuestCam.mov" % got)
check("and the camera whose sound is no track is not",
      "WideCam.mov" not in got,
      "hints for %s, wanted none for WideCam.mov" % got)
got = clipped(vpm.collect_findings([], [PHONE], fresh=True,
                                   crosstalk=False, heard=[PHONE]))
check("a camera whose sound is AAC is not counted, as float is not",
      got == [], "hints for %s, wanted none" % got)


class Call(object):
    """As much of a parsed command line as the preflight reads."""

    def __init__(self, assign=None):
        self.out = ROOM
        self.dry_run = True
        self.anyway = False
        self.lufs = None
        self.assign = assign


def run(assign=None):
    """The run's own check over the two loud cameras: whom it counted."""
    seen = []
    keep = (vpm.check_disk_space, vpm.report_findings, vpm.check_account)
    vpm.check_disk_space = lambda *a, **k: []
    vpm.check_account = lambda *a, **k: []
    vpm.report_findings = lambda found, *a, **k: (seen.extend(found), 0)[1]
    try:
        vpm.run_preflight(Call(assign), [], [GUEST, WIDE])
    finally:
        vpm.check_disk_space, vpm.report_findings, vpm.check_account = keep
    return clipped(seen)


print("\n2. The run's road")
plan = os.path.join(ROOM, "plan.json")
with open(plan, "w", encoding="utf-8") as f:
    json.dump({"tracks_of": [
        {"audio": GUEST, "blocks": [GUEST], "speakers": "Guest",
         "camera": GUEST, "camera_audio": True, "from_camera": GUEST}]}, f)
got = run(plan)
check("the run counts the camera its plan takes the sound of, no other",
      got == ["GuestCam.mov"], "hints for %s, wanted ['GuestCam.mov']" % got)
got = run()
check("with no plan and no recording it counts every camera",
      got == ["GuestCam.mov", "WideCam.mov"],
      "hints for %s, wanted both" % got)

shutil.rmtree(ROOM, ignore_errors=True)
shutil.rmtree(os.environ["VPM_CACHE"], ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
