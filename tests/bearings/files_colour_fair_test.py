# -*- coding: utf-8 -*-
"""Cameras are compared in colour like for like: one scale, each file once.

One picture reads the same brightness and colour at 8, 10 and 12 bit,
though signalstats answers in each file's own depth, so a pair that
differs in depth alone draws no warning. One file under two names keeps
a row under each and is one camera in the mean.

Sections: one picture at 8, 10 and 12 bit; the 8 and 10 bit pair
through the report; one file under two names.
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
import the_program
SCRIPT = the_program.SCRIPT
import subprocess, sys, tempfile, time

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


#------------------------------------------------------------- Material

D = os.path.join(tempfile.mkdtemp(prefix="vpm_run_"), "colour")
os.makedirs(D)


def made(name, source, pix_fmt):
    """Two seconds of an ffmpeg source written at this depth; its path."""
    path = os.path.join(D, name)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    source + "size=160x90:rate=25:duration=2", "-c:v",
                    "ffv1", "-pix_fmt", pix_fmt, path], check=True)
    return path


PICTURE = "testsrc2="
EIGHT = made("Wide8.mkv", PICTURE, "yuv420p")
TEN = made("Wide10.mkv", PICTURE, "yuv420p10le")
TWELVE = made("Wide12.mkv", PICTURE, "yuv420p12le")
GREY = made("Close8.mkv", "color=c=0x202020:", "yuv420p")


def level(path, key):
    """One value the program measures in the picture, -1 where none came."""
    got = vpm.measure_picture_levels(path) or {}
    return float(got.get(key, -1.0))

#------------------------------------------- 1. One picture, three depths

print("1. One picture at 8, 10 and 12 bit")
y8, y10, y12 = level(EIGHT, "y"), level(TEN, "y"), level(TWELVE, "y")
print("   brightness %.2f, %.2f, %.2f" % (y8, y10, y12))
check("a 10-bit file reads the brightness of its 8-bit twin",
      y8 > 0 and abs(y10 - y8) < 1.0,
      "%.2f at 10 bit against %.2f at 8 bit" % (y10, y8))
u8, u10 = level(EIGHT, "u"), level(TEN, "u")
check("and the colour difference of its 8-bit twin",
      u8 > 0 and abs(u10 - u8) < 1.0,
      "U %.2f at 10 bit against %.2f at 8 bit" % (u10, u8))
check("a 12-bit file reads on the same scale",
      y8 > 0 and abs(y12 - y8) < 1.0,
      "%.2f at 12 bit against %.2f at 8 bit" % (y12, y8))

#-------------------------------------------- 2. The pair in the report

print("\n2. The 8 and 10 bit pair through the report")
said = io.StringIO()
with contextlib.redirect_stdout(said):
    lines = vpm.report_picture_comparison(
        [{"track": "Wide", "file": EIGHT}, {"track": "Close", "file": TEN}])
print(said.getvalue().rstrip())
widest = max([abs(row[2][0]) for row in lines] or [-1.0])
CAUTION = vpm.T('  Caution: %s steps of brightness difference -- '
                'visible when switching.').split("%s")[0]
check("one picture at 8 and 10 bit is not warned about",
      lines and CAUTION not in said.getvalue(),
      "widest distance to the mean %.2f steps, %d rows" % (widest,
                                                           len(lines)))

#------------------------------------------ 3. One file, two names

print("\n3. One file under two names")
TWIN = os.path.join(D, "Speaker8.mkv")
os.link(EIGHT, TWIN)
measured, middle = vpm.compare_picture_levels(
    [{"track": "Wide", "file": EIGHT}, {"track": "Speaker", "file": TWIN}])
check("one file under two names counts as one camera",
      middle is None, "mean %s, wanted none: one camera has no mean"
      % (middle,))
check("and keeps a row under each name",
      sorted(n for n, _v in measured) == ["Speaker", "Wide"],
      "rows %s" % sorted(n for n, _v in measured))
y_grey = level(GREY, "y")
measured, middle = vpm.compare_picture_levels(
    [{"track": "Wide", "file": EIGHT}, {"track": "Speaker", "file": TWIN},
     {"track": "Close", "file": GREY}])
got = (middle or {}).get("y", -1.0)
check("the mean holds one file under two names once",
      abs(got - (y8 + y_grey) / 2.0) < 0.5,
      "mean %.2f, wanted %.2f -- %.2f with it counted twice"
      % (got, (y8 + y_grey) / 2.0, (2 * y8 + y_grey) / 3.0))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
