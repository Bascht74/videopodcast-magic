# -*- coding: utf-8 -*-
"""The colr box decides the colour line and whether a source counts as HDR.

One short clip is written with a colr box, and copies of it get other
numbers written into that box by hand -- primaries, curve, matrix and
the range bit -- so each case is the box and nothing else. In order:
the material, then the colour line for PQ at full range, a matrix
standing alone, a box that says nothing, numbers without a name, and log
named only by a camera key; then the HDR verdict for PQ behind an SDR
file, Apple Log, BT.2020 as primaries and as matrix alone, log from the
camera key, and a plain SDR file that is not HDR.
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
import shutil
import struct
import subprocess
import tempfile
import time
import the_program

SCRIPT = the_program.SCRIPT
os.environ["VPM_NO_UPDATE_CHECK"] = "1"
vpm = the_program.load()
vpm.set_language("en")
T = vpm.T

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


folder = tempfile.mkdtemp(prefix="vpm_colr_")
KEY, GAMMA = "com.camera.gamma", "S-Log3"


def clip(name, more):
    """A tenth of a second in ten bit, repacked so the colr box is written."""
    raw = os.path.join(folder, "raw_" + name)
    out = os.path.join(folder, name)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "testsrc=size=64x36:rate=30:duration=0.1",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p10le",
                    "-x264opts",
                    "colorprim=bt709:transfer=bt709:colormatrix=bt709",
                    raw], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-c", "copy"]
                   + more + ["-movflags", "+write_colr+use_metadata_tags",
                             out], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    return out


def boxed(source, name, prim, trc, mat, full):
    """A copy of *source* whose nclx box carries these four values."""
    data = bytearray(open(source, "rb").read())
    at = data.find(b"colrnclx")
    if at < 0:
        return None
    struct.pack_into(">HHHB", data, at + 8, prim, trc, mat,
                     0x80 if full else 0)
    out = os.path.join(folder, name)
    open(out, "wb").write(bytes(data))
    return out


plain = clip("plain.mp4", [])
keyed = clip("keyed.mp4", ["-metadata", "%s=%s" % (KEY, GAMMA)])
made = {}
for name, src, values in (
        ("pq.mp4", plain, (9, 16, 9, True)),
        ("matrix.mp4", plain, (2, 2, 9, False)),
        ("silent.mp4", plain, (2, 2, 2, False)),
        ("unnamed.mp4", plain, (12, 10, 13, False)),
        ("sdr.mp4", plain, (1, 1, 1, False)),
        ("applelog.mp4", plain, (2, 21, 2, False)),
        ("wide.mp4", plain, (9, 1, 9, False)),
        ("onlymatrix.mp4", plain, (2, 1, 9, False)),
        ("slog.mp4", keyed, (1, 1, 1, False))):
    out = boxed(src, name, *values) if os.path.exists(src) else None
    if out and vpm.mov_colour_tags(out) == values:
        made[name] = out
check("every clip carries the colr box it was given", len(made) == 9,
      "%d of 9 read back as written: %s"
      % (len(made), ", ".join(sorted(made)) or "none"))

TEN = {"pix_fmt": "yuv420p10le"}


def line(name, tags=None):
    """The colour line for one clip, or why there is none."""
    if name not in made:
        return "no clip %s" % name
    return vpm.colour_text(made[name], TEN, tags or {})


got = line("pq.mp4")
want = ", ".join(["PQ (HDR10)", "BT.2020", T('full range'),
                  T('%d bit') % 10, "HDR"])
check("PQ in BT.2020 at full range is named, and HDR", got == want,
      "%r, wanted %r" % (got, want))
got = line("matrix.mp4")
want = ", ".join([T('Matrix %s') % "BT.2020", T('%d bit') % 10, "HDR"])
check("a BT.2020 matrix standing alone is named, and HDR", got == want,
      "%r, wanted %r" % (got, want))
got = line("silent.mp4")
want = ", ".join([T('Curve and colour space are missing from the file'),
                  T('%d bit') % 10])
check("a box saying unspecified three times says that it is missing",
      got == want, "%r, wanted %r" % (got, want))
got = line("unnamed.mp4")
want = ", ".join([T('Curve number %d') % 10, "Display P3",
                  T('Matrix %s') % (T('Number %d') % 13), T('%d bit') % 10])
check("a curve and a matrix without a name are given by number",
      got == want, "%r, wanted %r" % (got, want))
got = line("sdr.mp4", {KEY: GAMMA})
want = ", ".join(["BT.709", "BT.709", T('%d bit') % 10,
                  T('Log according to camera data'), "HDR"])
check("log named only by a camera key still makes the line HDR",
      got == want, "%r, wanted %r" % (got, want))


def verdict(*names):
    """hdr_from_sources over these clips, in this order."""
    if not all(n in made for n in names):
        return (None, "missing clip")
    return vpm.hdr_from_sources([made[n] for n in names])


got = verdict("sdr.mp4", "pq.mp4")
check("PQ is found behind an SDR file in the list",
      got == (True, "transfer function 16 (PQ) in pq.mp4"), "%r" % (got,))
got = verdict("applelog.mp4")
check("Apple Log as the curve makes the source HDR",
      got == (True, "transfer function 21 (Apple Log) in applelog.mp4"),
      "%r" % (got,))
got = verdict("wide.mp4")
check("BT.2020 primaries under an SDR curve make the source HDR",
      got == (True, "BT.2020 in wide.mp4"), "%r" % (got,))
got = verdict("onlymatrix.mp4")
check("a BT.2020 matrix with unspecified primaries makes it HDR",
      got == (True, "BT.2020 as matrix in onlymatrix.mp4"), "%r" % (got,))
got = verdict("slog.mp4")
check("a log camera key under an SDR box makes the source HDR",
      got == (True, "log according to camera data: %s = %s (slog.mp4)"
              % (KEY, GAMMA)), "%r" % (got,))
got = verdict("sdr.mp4")
check("a plain BT.709 file is not HDR", got == (False, ""), "%r" % (got,))

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
