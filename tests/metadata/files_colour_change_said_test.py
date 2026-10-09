# -*- coding: utf-8 -*-
"""The log says whether the colour box arrived as meant, and warns if not.

check_colour_survived holds the box of the written file against the
source's. One short clip is written with a colr box, and copies of it
get other numbers written into that box by hand, or lose the box. In
order: the material, then the same box on both sides is carried over,
primaries filled in from the matrix are said as such when that was
asked, and warned about when it was not, a changed curve is warned
about with both sides named, and a box invented where the source had
none is warned about too.
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


folder = tempfile.mkdtemp(prefix="vpm_colrsaid_")
raw = os.path.join(folder, "raw.mp4")
plain = os.path.join(folder, "plain.mp4")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "testsrc=size=64x36:rate=30:duration=0.1",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-x264opts", "colorprim=bt709:transfer=bt709:colormatrix=bt709",
                raw], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-c", "copy",
                "-movflags", "+write_colr", plain],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def boxed(name, values):
    """A copy whose nclx box carries *values*, or has no colr box at all."""
    if not os.path.exists(plain):
        return None
    data = bytearray(open(plain, "rb").read())
    at = data.find(b"colrnclx")
    if at < 0:
        return None
    if values is None:
        # The box renamed to free space: same size, nothing to read.
        data[at:at + 4] = b"free"
    else:
        struct.pack_into(">HHHB", data, at + 8, *(values + (0,)))
    out = os.path.join(folder, name)
    open(out, "wb").write(bytes(data))
    return out


cases = {"sdr": (1, 1, 1), "pq": (9, 16, 9), "matrix": (2, 1, 9),
         "filled": (9, 1, 9), "none": None}
made = {}
for name, values in cases.items():
    out = boxed(name + ".mp4", values)
    got = vpm.mov_colour_tags(out) if out else "unbuilt"
    if out and (got[:3] if got else None) == values:
        made[name] = out
check("every clip carries the colr box it was given, or none",
      len(made) == 5, "%d of 5 read back as written: %s"
      % (len(made), ", ".join(sorted(made)) or "none"))


def said(source, target, extend=False):
    """What check_colour_survived prints for these two, as one string."""
    if source not in made or target not in made:
        return "no clip"
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        vpm.check_colour_survived(made[source], made[target], extend)
    return " ".join(out.getvalue().split())


def plain_text(text):
    return " ".join(text.split())


got = said("sdr", "sdr")
want = plain_text(T('  Colour:          %d/%d/%d carried over') % (1, 1, 1))
check("the same box on both sides is said to be carried over",
      got == want, "%r, wanted %r" % (got, want))
got = said("matrix", "filled", extend=True)
want = plain_text(T('  Colour:          %d/%d/%d -- primaries filled in from '
                    'the matrix (source: %d)') % (9, 1, 9, 2))
check("primaries filled in from the matrix are said as such",
      got == want, "%r, wanted %r" % (got, want))
got = said("matrix", "filled", extend=False)
want = plain_text(vpm.as_warn(T('  Colour:          Caution, %s in the source, %s in '
                    'the new file') % ((2, 1, 9), (9, 1, 9))))
check("primaries filled in that were not asked for are warned about",
      want in got, "%r, wanted %r in it" % (got, want))
got = said("pq", "filled")
want = plain_text(vpm.as_warn(T('  Colour:          Caution, %s in the source, %s in '
                    'the new file') % ((9, 16, 9), (9, 1, 9))))
check("a curve that changed is warned about, both sides named",
      want in got, "%r, wanted %r in it" % (got, want))
got = said("none", "pq")
want = plain_text(vpm.as_warn(T('  Colour:          Caution, %s in the source, %s in '
                    'the new file') % (T('nothing'), (9, 16, 9))))
check("a box the source never had is warned about",
      want in got, "%r, wanted %r in it" % (got, want))

shutil.rmtree(folder, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
