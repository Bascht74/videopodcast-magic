# -*- coding: utf-8 -*-
"""Room for the run is judged with a margin, and on both disks at once.

"The verdict" holds a rough estimate against what is free, "the margin"
is the band where the numbers fit but only just, "the second disk" is
the temporary files eating the same space twice, and "two folders, one
disk" is how that is told. "What the run really writes" is what the
estimate has to cover -- the whole length, every camera, every track,
and with a time window the stretch each camera is cut down to rather
than the whole shoot. "The folder that is asked about" is the one the
answer is about.

What free space really is comes from the system, so it is replaced
here: the check is about the judgement, not about this machine's disk.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import collections
import subprocess, sys, tempfile, time, wave
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


WORK = tempfile.mkdtemp(prefix="vpm_space_")
video = os.path.join(WORK, "Camera.mov")
audio = os.path.join(WORK, "Sound.wav")
subprocess.run(
    ["ffmpeg", "-v", "error", "-f", "lavfi",
     "-i", "testsrc=size=160x90:rate=25:duration=2",
     "-f", "lavfi", "-i", "sine=frequency=300:duration=2",
     "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-shortest", "-y", video],
    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
with wave.open(audio, "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(48000)
    f.writeframes(b"\0\0" * 48000 * 2)
# A precondition of the material, not a statement about the program.
assert os.path.getsize(video) > 0 and os.path.getsize(audio) > 0

# A long camera for the section about what is really written: a shoot of
# an hour against a window of five minutes, at a sixtieth of the length
# so that building it costs nothing. Few frames a second keep the
# encoding cheap; only the length and the size are read off it.
long_video = os.path.join(WORK, "LongCamera.mov")
subprocess.run(
    ["ffmpeg", "-v", "error", "-f", "lavfi",
     "-i", "testsrc=size=160x90:rate=5:duration=60",
     "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
     "-y", long_video],
    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
second_camera = os.path.join(WORK, "LongCamera2.mov")
third_camera = os.path.join(WORK, "LongCamera3.mov")
vpm.shutil.copy(long_video, second_camera)
vpm.shutil.copy(long_video, third_camera)
three_cameras = [long_video, second_camera, third_camera]
# The window the owner's run was given, as a share: five minutes of an
# hour. Written as two ends of a timecode because that is how the call
# carries it.
WINDOW_IN, WINDOW_OUT = "17:16:36:04", "17:16:41:04"
# How long that window is. Written out rather than computed from the two
# timecodes: what the estimate is held against must not be arrived at by
# the program's own route.
WINDOW_S = 5.0
# How long the long camera really is, asked of ffprobe directly rather
# than of the program being checked. A precondition of the material: the
# window has to be a small part of it, or the section below would compare
# two numbers that are nearly the same anyway.
material_s = float(subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
     "-of", "default=nw=1:nk=1", long_video],
    check=True, capture_output=True, text=True).stdout.strip())
assert material_s > 40.0

# What one second of the added sound costs on disk. Uncompressed, 48 kHz,
# 24 bit, two channels; every camera gets two of those tracks laid into
# the copy. Written out as a value, so the test does not repeat the
# program's arithmetic.
SOUND_MB_PER_SECOND = 0.288
TRACKS_PER_CAMERA = 2

Usage = collections.namedtuple("Usage", "total used free")
real_usage = vpm.shutil.disk_usage
real_one_disk = vpm.on_one_disk


def judge(free_mb, one_disk=False, videos=None, multitrack=False):
    """The finding for a made-up amount of free space."""
    vpm.shutil.disk_usage = lambda _p: Usage(0, 0, free_mb * 1e6)
    vpm.on_one_disk = lambda _a, _b: one_disk
    try:
        return vpm.check_disk_space(WORK, [audio], videos or [video],
                                    multitrack)[0]
    finally:
        vpm.shutil.disk_usage = real_usage
        vpm.on_one_disk = real_one_disk


def needed_mb(one_disk=False):
    """The estimate itself, read back out of the sentence."""
    return judge(1e9, one_disk).text


def bisect_estimate(finding_for):
    """The estimate in MB, from a function that judges an amount free.

    An abort is exactly the case where what is free falls short of the
    estimate, so the amount of free space at which the verdict turns is
    the estimate itself. Read that way rather than by repeating the
    program's arithmetic.
    """
    lo, hi = 0.0, 1e6
    for _ in range(40):
        mid = (lo + hi) / 2.0
        if finding_for(mid).kind == "abort":
            lo = mid
        else:
            hi = mid
    return hi


class Call(object):
    """What the preflight sees of a call: a time window and an out folder."""

    def __init__(self, first="", last=""):
        self.in_point = first
        self.out_point = last
        self.fps = 25.0
        self.out = WORK
        self.multitrack = False
        self.anyway = False


def preflight_space(free_mb, first="", last=""):
    """The disk-space finding the preflight arrives at for a call.

    Everything the preflight does with the material itself is replaced,
    so that what is left is the one line that turns a call into a
    question about room. The call is the only place a time window is
    written down, and this asks what the window does to that line.
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
        vpm.run_preflight(Call(first, last), [audio], [long_video])
    finally:
        (vpm.collect_findings, vpm.report_findings,
         vpm.check_loudness_target) = keep
        vpm.shutil.disk_usage = real_usage
        vpm.on_one_disk = real_one_disk
    for found in seen:
        if found.field == vpm.T('Disk space'):
            return found
    return None


print("1. The verdict")
plenty = judge(1e9)
check("plenty of room is called good", plenty.kind == "good",
      "the verdict is %r" % plenty.kind)
none_at_all = judge(1.0)
check("far too little is called an abort", none_at_all.kind == "abort",
      "the verdict is %r" % none_at_all.kind)
check("and the sentence says how much is missing",
      "missing" in (none_at_all.advice or ""),
      "the advice reads %r" % (none_at_all.advice or "")[:60])

print("\n2. The margin")
# What the estimate comes to for this material, found by bisection on
# the verdict itself rather than by repeating the program's arithmetic.
lo, hi = 0.0, 1e6
for _ in range(40):
    mid = (lo + hi) / 2.0
    if judge(mid).kind == "abort":
        lo = mid
    else:
        hi = mid
estimate = hi
# The picture is copied, so the estimate can never be under the size of
# the material itself. Against nought a bisection lands just above nought
# and would still pass.
material_mb = (os.path.getsize(video) + os.path.getsize(audio)) / 1e6
check("the estimate is at least as big as the material",
      estimate >= material_mb,
      "the estimate came to %.3f MB against %.3f MB of material"
      % (estimate, material_mb))
check("room that only just covers the estimate is not called good",
      judge(estimate * 1.01).kind != "good",
      "1 %% over the estimate was called %r" % judge(estimate * 1.01).kind)
check("and it is not called an abort either -- it may still fit",
      judge(estimate * 1.01).kind != "abort",
      "1 %% over the estimate was called %r" % judge(estimate * 1.01).kind)
check("well over the estimate is called good",
      judge(estimate * 2.0).kind == "good",
      "twice the estimate was called %r" % judge(estimate * 2.0).kind)

print("\n3. The second disk")
apart_ = needed_mb(False)
together = needed_mb(True)
check("the temporary files on the same disk raise what is needed",
      apart_ != together,
      "with the temp folder elsewhere %r, on the same disk %r"
      % (apart_, together))

print("\n4. Two folders, one disk")
check("a folder is on the same disk as itself",
      real_one_disk(WORK, WORK) is True, "said %r" % real_one_disk(WORK, WORK))
check("a folder that is not there counts as another disk",
      real_one_disk(os.path.join(WORK, "nowhere"), WORK) is False,
      "said %r" % real_one_disk(os.path.join(WORK, "nowhere"), WORK))

print("\n5. What the run really writes")
one_camera = bisect_estimate(lambda free: judge(free, False, [long_video]))
# The added sound alone, over the full length of the shoot, is a floor
# the estimate cannot fall below: it is written uncompressed and it is
# written for as long as the camera runs.
sound_floor = material_s * SOUND_MB_PER_SECOND * TRACKS_PER_CAMERA
check("the added sound is counted over the whole shoot",
      one_camera >= sound_floor,
      "the estimate is %.3f MB, and %.1f s of two uncompressed tracks are "
      "%.3f MB on their own" % (one_camera, material_s, sound_floor))
three = bisect_estimate(lambda free: judge(free, False, three_cameras))
check("every camera is counted, not only the longest one",
      three >= one_camera * 2.5,
      "three cameras want %.3f MB against %.3f MB for one of them"
      % (three, one_camera))
several = bisect_estimate(lambda free: judge(free, False, [long_video], True))
check("several tracks in the file ask for more room than one",
      several >= one_camera * 1.4,
      "with the tracks kept apart %.3f MB against %.3f MB for one mix"
      % (several, one_camera))
# A precondition: without this line there is nothing to compare below,
# and "the window changed nothing" would be true of two empty hands.
handed_on = preflight_space(1e9)
check("the preflight reaches the disk-space line at all",
      handed_on is not None,
      "the disk-space finding the preflight handed on reads %r"
      % (handed_on.text if handed_on is not None else None,))
# The time window now bounds the camera files as well as the cut, and
# this check was once the other way round. The history, so that nobody
# turns it back a second time: the shrinking estimate was built on
# 31.8.2026 and withdrawn the same day, because the cameras were still
# written whole -- with --in-point 17:16:36:04 --out-point 17:21:36:04
# the three came out 4098.208 s long, exactly as long as the sources, and
# 83.6 GB. The estimate lied, and this check was written to hold the
# withdrawal. Since the cameras really are cut down to the window, the
# lie is the other one: an estimate over the whole shoot refuses a run
# that fits easily -- 11.2 GB asked for where 1.3 GB is written. So the
# estimate has to follow the window down, and it may not fall under what
# the window itself costs.
open_end = bisect_estimate(lambda free: preflight_space(free))
windowed = bisect_estimate(
    lambda free: preflight_space(free, WINDOW_IN, WINDOW_OUT))
check("a time window shrinks what the run needs on disk",
      windowed < open_end / 2.0,
      "a window of %s to %s -- %.1f s of %.1f -- wants %.3f MB against "
      "%.3f MB with no window"
      % (WINDOW_IN, WINDOW_OUT, WINDOW_S, material_s, windowed, open_end))
# Against nought a shrinking estimate would pass the line above with the
# best number in the file. The floor is the same one section 5 opened
# with, only over the window instead of the shoot: two uncompressed
# tracks are laid into the copy for as long as it runs, and it runs at
# least the length of the window. The picture and the margin at each end
# come on top and are not counted here.
window_floor = WINDOW_S * SOUND_MB_PER_SECOND * TRACKS_PER_CAMERA
check("and it does not fall under what the window itself costs",
      windowed >= window_floor,
      "the estimate came to %.3f MB, and %.1f s of two uncompressed tracks "
      "are %.3f MB on their own" % (windowed, WINDOW_S, window_floor))

print("\n6. The folder that is asked about")
# The real disk_usage here, not the made-up one: what is asked is which
# folder the answer is about, not how much is free on it.
not_made_yet = os.path.join(WORK, "not", "made", "yet")
about = vpm.check_disk_space(not_made_yet, [audio], [video], False)
check("a folder not there yet is judged by the one above it",
      len(about) == 1 and WORK in (about[0].text if about else ""),
      "findings: %d, and the sentence reads %r"
      % (len(about), about[0].text if about else ""))

vpm.shutil.rmtree(WORK, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
