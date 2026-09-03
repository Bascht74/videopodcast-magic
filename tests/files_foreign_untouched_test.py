# -*- coding: utf-8 -*-
"""Copying atoms over onto everything that is not a camera file.

The expectation is the same everywhere: no crash, no byte changed, [].
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import sys, shutil, subprocess, importlib.util, hashlib, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixture_root import fixture
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

# The read-only material fixtures.sh built, and a scratch folder of our
# own. A fixed /tmp path for either is a trap on a machine with two
# users: the second run deletes the first one's material.
D = fixture("foreign")
WORK = tempfile.mkdtemp(prefix="foreign_work_")

began = time.time()
done = 0
error = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append("%s [%s]" % (name, extra or "no numbers"))

def checksum(file_path):
    try:
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        return "?" + type(e).__name__

# A real source with a logs atom, so there is something to carry over.
SOURCE = WORK + "/source.mov"
subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi",
                "-i", "testsrc=size=64x36:rate=30:duration=1",
                "-c:v", "libx265", "-tag:v", "hvc1", SOURCE, "-y"],
               check=True)
import struct
def insert_logs(file_path, text):
    data = bytearray(open(file_path, "rb").read())
    i, size = next((p, g) for a, p, g
                   in vpm._top_level_boxes(file_path) if a == b"moov")
    moov = bytearray(data[i:i + size])
    chain = vpm._video_track_chain(moov, 0, len(moov), 8)
    e_i, _ = chain[-1]
    e_size = struct.unpack(">I", bytes(moov[e_i:e_i + 4]))[0]
    raw = text.encode("latin1")
    box = struct.pack(">I", 8 + len(raw)) + b"logs" + raw
    moov[e_i + e_size:e_i + e_size] = box
    for bi, _bk in chain:
        a = struct.unpack(">I", bytes(moov[bi:bi + 4]))[0]
        moov[bi:bi + 4] = struct.pack(">I", a + len(box))
    open(file_path, "wb").write(bytes(data[:i]) + bytes(moov)
                                + bytes(data[i + size:]))
insert_logs(SOURCE, "com.apple.apple-wide-gamut.apple-log")

FOREIGN = ["v.mp4", "audio.wav", "audioonly.mov", "frag.mp4", "v.mkv",
           "image.png", "text.txt", "empty.bin", "junk.mov", "folder"]

print("A. As TARGET: a foreign file must not be touched")
for n in FOREIGN:
    source = os.path.join(D, n)
    target = os.path.join(WORK, n)
    if os.path.isdir(source):
        os.makedirs(target, exist_ok=True)
    else:
        shutil.copy2(source, target)
    before_value = checksum(target)
    try:
        out = vpm.copy_mov_atoms(SOURCE, target)
        crashed = ""
    except Exception as e:
        out, crashed = "CRASH", "%s: %s" % (type(e).__name__, str(e)[:40])
    check("target %-13s -> nothing done" % n,
            out == [] and checksum(target) == before_value,
            crashed or str(out))

print("\nB. As SOURCE: nothing to fetch, the target stays whole")
good_target = WORK + "/target.mov"
for n in FOREIGN:
    subprocess.run(["ffmpeg", "-v", "error", "-i", SOURCE, "-c", "copy",
                    good_target, "-y"], check=True)
    before_value = checksum(good_target)
    try:
        out = vpm.copy_mov_atoms(os.path.join(D, n), good_target)
        crashed = ""
    except Exception as e:
        out, crashed = "CRASH", "%s: %s" % (type(e).__name__, str(e)[:40])
    check("source %-13s -> nothing done" % n,
            out == [] and checksum(good_target) == before_value,
            crashed or str(out))

print("\nC. Paths that do not exist at all")
for source, target, what in (
        (SOURCE, WORK + "/notthere.mov", "target missing"),
        (WORK + "/gone.mov", good_target, "source missing"),
        ("", "", "both empty")):
    before_value = checksum(target)
    try:
        out = vpm.copy_mov_atoms(source, target)
        crashed = ""
    except Exception as e:
        out, crashed = "CRASH", "%s: %s" % (type(e).__name__, str(e)[:40])
    check("%-14s -> nothing done" % what,
            out == [] and checksum(target) == before_value,
            crashed or str(out))

print("\nD. And the reading side: _logs_atom_text and colour_text on"
      " foreign stuff")
for n in FOREIGN + ["notthere.mov"]:
    source = os.path.join(D, n)
    try:
        t = vpm._logs_atom_text(source)
        k = vpm.log_curve_from_atom(t)
        check("_logs_atom_text %-13s empty, no crash" % n, t == "", repr(t))
    except Exception as e:
        check("_logs_atom_text %-13s empty, no crash" % n, False,
                "%s: %s" % (type(e).__name__, str(e)[:40]))

print("\nE. Colour line on a file that has nothing")
try:
    info = vpm.video_facts(os.path.join(D, "v.mp4"))
    t = vpm.colour_text(os.path.join(D, "v.mp4"), info["video"],
                      info.get("tags") or {})
    check("colour_text returns something readable", bool(t), t)
except Exception as e:
    check("colour_text returns something readable", False,
            "%s: %s" % (type(e).__name__, str(e)[:60]))

print("\nF. The real source still works")
subprocess.run(["ffmpeg", "-v", "error", "-i", SOURCE, "-c", "copy",
                good_target, "-y"], check=True)
out = vpm.copy_mov_atoms(SOURCE, good_target)
check("logs carried over", out == ["logs"], str(out))
curve = vpm.log_curve_from_atom(vpm._logs_atom_text(good_target))
check("text is there", curve == "Apple Log",
        "read back %r, wanted %r" % (curve, "Apple Log"))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
