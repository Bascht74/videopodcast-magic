# -*- coding: utf-8 -*-
"""Room for the run is judged with a margin, and on both disks at once.

Four sections. "The verdict" holds a rough estimate against what is
free; "the margin" is the band where the numbers fit but only just;
"the second disk" is the temporary files, which go into the system temp
folder and eat the same space twice where that folder sits on the same
disk as the output; "the sentence" is what a person is told.

What free space really is comes from the system, so it is replaced
here: the check is about the judgement, not about this machine's disk.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import collections
import importlib.util, subprocess, sys, tempfile, time, wave
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
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

Usage = collections.namedtuple("Usage", "total used free")
real_usage = vpm.shutil.disk_usage
real_one_disk = vpm.on_one_disk


def judge(free_mb, one_disk=False):
    """The finding for a made-up amount of free space."""
    vpm.shutil.disk_usage = lambda _p: Usage(0, 0, free_mb * 1e6)
    vpm.on_one_disk = lambda _a, _b: one_disk
    try:
        return vpm.check_disk_space(WORK, [audio], [video], False)[0]
    finally:
        vpm.shutil.disk_usage = real_usage
        vpm.on_one_disk = real_one_disk


def needed_mb(one_disk=False):
    """The estimate itself, read back out of the sentence."""
    return judge(1e9, one_disk).text


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

vpm.shutil.rmtree(WORK, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
