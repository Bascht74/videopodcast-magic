# -*- coding: utf-8 -*-
"""Preview and Resolve put a camera at the same offset.

Both take it out of the handover file: the player through
camera_offset, the Resolve build by putting cam["offset"] into
recordFrame. They once came apart away from the reference camera.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, io, json, struct, sys, tempfile, time
import contextlib
began = time.time()
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
WORK = tempfile.mkdtemp(prefix="sameoffset_")
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def spoken(call, *a, **k):
    """Run something and hand back what it printed."""
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        out = call(*a, **k)
    return out, said.getvalue()


class Args(object):
    production = "Test"
    resolve = False
    lufs = -16.0
    intro = None
    outro = None


def stamped(path, seconds):
    """Write a file that carries *seconds* as its own start time.

    A bext chunk, which is where file_timecode looks first -- so this
    costs no ffprobe and no camera.
    """
    body = (b"\0" * 338 + struct.pack("<Q", int(round(seconds * vpm.SR)))
            + b"\0" * 8)
    with open(path, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 4 + 8 + len(body)) + b"WAVE")
        f.write(b"bext" + struct.pack("<I", len(body)) + body)
    return path


ZERO = 68100.0                                   # 18:55:00:00, the wide shot
# Three cameras of one evening: timecode, and what the alignment
# measured. The reference agrees, the other two do not.
NIGHT = [("Wide", 68100.0, 0.0),
         ("Hosts", 68104.0, 4.0 - 37.34),
         ("Guest", 68117.4, 17.4 - 77.51)]

night = os.path.join(WORK, "night")
os.makedirs(night)
n_cameras, n_videos, n_results, n_offsets = [], [], [], {}
for name, tc, measured in NIGHT:
    src = os.path.join(WORK, name + "_source.mov")
    open(src, "w").write("x")
    rendered = stamped(os.path.join(WORK, name + ".wav"), tc)
    n_cameras.append({"name": name, "video": src})
    n_videos.append((src, {"fps": 30.0, "width": 1920, "height": 1080,
                           "duration": 300.0,
                           "tc": vpm.timecode_string(tc, 30.0)}))
    n_results.append(rendered)
    n_offsets[os.path.abspath(rendered)] = measured

with contextlib.redirect_stdout(io.StringIO()):
    vpm.write_handover(Args(), [], n_cameras, n_videos, night, ZERO,
                       (n_cameras[0]["video"], n_videos[0][1]), n_results,
                       None, None, 300.0, None, None, n_offsets)
written = json.load(io.open(os.path.join(night, "Test_resolve.json"),
                            encoding="utf-8"))
a_frame = 1.0 / max(1.0, float(written["fps_measured"]))

for_player, said = spoken(vpm.camera_offset, written["cameras"],
                          written["start_s"], written["fps_measured"])
for_resolve = dict((cam["track"], cam["offset"])
                   for cam in written["cameras"])
check("both know the same tracks",
      sorted(for_player) == sorted(for_resolve),
      "%s / %s" % (sorted(for_player), sorted(for_resolve)))
for track in sorted(for_resolve):
    check("%s: player and Resolve agree" % track,
          abs(for_player[track] - for_resolve[track]) <= a_frame,
          "%.4f against %.4f" % (for_player[track], for_resolve[track]))
check("and there was nothing to put right", not said.strip(),
      said.strip()[:70])

# An old handover, or one edited by hand, carrying the wrong numbers.
# The timecode keeps precedence, and both numbers go into the log.
poisoned = [dict(cam, offset=cam["sound_against_picture"])
            for cam in written["cameras"]]
after, said = spoken(vpm.camera_offset, poisoned, written["start_s"],
                     written["fps_measured"])
check("the timecode wins over a stored measurement",
      all(abs(after[t] - for_resolve[t]) <= a_frame for t in for_resolve),
      str(after))
check("and both numbers are said out loud",
      "+4.000" in said and "-33.340" in said, repr(said[:90]))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
