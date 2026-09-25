# -*- coding: utf-8 -*-
"""A dry run short of disk space is told so and goes on; a real run stops.

A dry run writes no camera file, so refusing it for room it never uses
held up a trial that would have shown everything else. "The verdict"
holds one shortage against both kinds of run, "room enough" makes sure
the dry run is not warned where nothing is short, and "through the
preflight" asks whether the call's dry run reaches the check at all.

What free space really is comes from the system, so it is replaced
here: the check is about the judgement, not about this machine's disk.
"""
import os
import sys
# tests/, where the helpers and state/ lie; this file may stand in a
# folder under it, or in one under that.
HERE = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(HERE, "the_program.py")) \
        and os.path.dirname(HERE) != HERE:
    HERE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import collections
import subprocess
import tempfile
import time
import the_program

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


WORK = tempfile.mkdtemp(prefix="vpm_dry_space_")
video = os.path.join(WORK, "Camera.mov")
audio = os.path.join(WORK, "Sound.wav")
subprocess.run(
    ["ffmpeg", "-v", "error", "-f", "lavfi",
     "-i", "testsrc=size=160x90:rate=25:duration=2",
     "-f", "lavfi", "-i", "sine=frequency=300:duration=2",
     "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
     "-c:a", "pcm_s16le", video], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi",
                "-i", "sine=frequency=300:duration=2", audio], check=True)

Usage = collections.namedtuple("Usage", "total used free")
real_usage = vpm.shutil.disk_usage
real_one_disk = vpm.on_one_disk
SHORT_MB = 0.001        # far under anything two seconds of material need
PLENTY_MB = 1e9


def judge(free_mb, dry_run):
    """The disk-space finding for a made-up amount of free space."""
    vpm.shutil.disk_usage = lambda _p: Usage(0, 0, free_mb * 1e6)
    vpm.on_one_disk = lambda _a, _b: False
    try:
        return vpm.check_disk_space(WORK, [audio], [video], False,
                                    dry_run=dry_run)[0]
    finally:
        vpm.shutil.disk_usage = real_usage
        vpm.on_one_disk = real_one_disk


class Call(object):
    """What the preflight sees of a call: an out folder, and a dry run or not."""

    def __init__(self, dry_run):
        self.in_point = ""
        self.out_point = ""
        self.fps = 25.0
        self.out = WORK
        self.multitrack = False
        self.anyway = False
        self.dry_run = dry_run


def preflight_space(free_mb, dry_run):
    """The disk-space finding the preflight arrives at for a call.

    Everything else the preflight does is replaced, so what is left is
    the one line that turns a call into a question about room.
    """
    seen = []
    keep = (vpm.collect_findings, vpm.report_findings,
            vpm.check_loudness_target)
    vpm.collect_findings = lambda *a, **k: []
    vpm.check_loudness_target = lambda *a, **k: []
    vpm.report_findings = lambda found, *a, **k: (seen.extend(found), False)[1]
    vpm.shutil.disk_usage = lambda _p: Usage(0, 0, free_mb * 1e6)
    vpm.on_one_disk = lambda _a, _b: False
    try:
        vpm.run_preflight(Call(dry_run), [audio], [video])
    finally:
        (vpm.collect_findings, vpm.report_findings,
         vpm.check_loudness_target) = keep
        vpm.shutil.disk_usage = real_usage
        vpm.on_one_disk = real_one_disk
    for found in seen:
        if found.field == vpm.T('Disk space'):
            return found
    return None


print("\n1. The verdict")
real = judge(SHORT_MB, False)
dry = judge(SHORT_MB, True)
check("a real run short of room is stopped", real.kind == "abort",
      "kind %r for %s MB free" % (real.kind, SHORT_MB))
check("a dry run short of room is only noted", dry.kind == "hint",
      "kind %r for %s MB free" % (dry.kind, SHORT_MB))
check("the note still says what the real run would lack",
      bool(real.advice) and dry.advice == real.advice,
      "dry run %r, real run %r" % (dry.advice[:70], real.advice[:70]))

print("\n2. Room enough")
roomy = judge(PLENTY_MB, True)
check("a dry run with room enough is called good", roomy.kind == "good",
      "kind %r for %s MB free" % (roomy.kind, PLENTY_MB))

print("\n3. Through the preflight")
# A precondition, so that a missing line does not read as a wrong kind.
through_dry = preflight_space(SHORT_MB, True)
through_real = preflight_space(SHORT_MB, False)
check("the preflight hands a dry run on to the disk check",
      through_dry is not None and through_dry.kind == "hint",
      "the disk-space finding reads %r"
      % (through_dry.kind if through_dry is not None else None,))
check("and it still stops a real run",
      through_real is not None and through_real.kind == "abort",
      "the disk-space finding reads %r"
      % (through_real.kind if through_real is not None else None,))

vpm.shutil.rmtree(WORK, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
