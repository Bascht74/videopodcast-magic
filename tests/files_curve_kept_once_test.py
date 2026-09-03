# -*- coding: utf-8 -*-
"""One file leaves one envelope, whatever name it was asked for.

The envelope of a recording is read once and then kept for the whole
run: reading an hour of 4K takes minutes. Two parts of the program ask
for it -- the prework warms it under the absolute path, the time axis
asks for it under the name the file dialog handed out -- so the store
has to answer to one name or the file is read twice and the first curve
is never given back.

A needless step in the middle of a path, /tmp/x/./A.wav, does here what
a drive letter and a backslash do on Windows: two names for one file
that compare unequal.

The sections: the store in memory, the curve saved beside it on disc,
and that the window looks for both under the same name. The clean-up
itself lives inside the window and is read out of the source.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import importlib.util, shutil, subprocess, sys, tempfile, time, wave
spec = importlib.util.spec_from_file_location("vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)
import numpy as np

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

D = tempfile.mkdtemp(prefix="onecurve_")
# A cache folder of its own: the suite hands every test the same one,
# and a curve another test left there would answer for this one.
os.environ["VPM_CACHE"] = tempfile.mkdtemp(prefix="onecurve_cache_")
RATE, SECONDS = 4000, 20.0

rng = np.random.default_rng(3)
x = (rng.standard_normal(int(SECONDS * RATE)) * 0.2).astype(np.float32)
STRAIGHT = os.path.join(D, "A.wav")
with wave.open(STRAIGHT, "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
    f.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
LONG_WAY = os.path.join(D, ".", "A.wav")

# Counting the readings, the way files_probed_once counts the probes.
run_real = subprocess.run
count = {"n": 0}


def run_counted(cmd, *args, **kwargs):
    if cmd and str(cmd[0]).endswith("ffmpeg"):
        count["n"] += 1
    return run_real(cmd, *args, **kwargs)


subprocess.run = run_counted


#-------------------------------------------------- 1. The store in memory

def tail(p):
    """The path without the temporary folder, so a line stays readable."""
    return p[len(D):] if p.startswith(D) else p


print("1. One file asked for under two names")
check("the long name and the short one are different strings",
      STRAIGHT != LONG_WAY,
      "%s against %s" % (tail(STRAIGHT), tail(LONG_WAY)))
check("and they name one file", os.path.samefile(STRAIGHT, LONG_WAY),
      "%s and %s" % (tail(STRAIGHT), tail(LONG_WAY)))

# Without the saved curve, so that a second reading shows up as a
# second process rather than as a cheap load from disc.
folder_real = vpm.envelope_cache_folder
vpm.envelope_cache_folder = lambda: None
vpm._ENV.clear()
count["n"] = 0
first = vpm.video_envelope(STRAIGHT)
again = vpm.video_envelope(LONG_WAY)
readings = count["n"]
print("   %d values, %s, %.2f MB per hour of material"
      % (len(first), first.dtype,
         first.nbytes / SECONDS * 3600.0 / 1e6))
check("the file is read once, not once per name", readings == 1,
      "%d ffmpeg processes, wanted 1" % readings)
check("two names for one file leave one curve in memory",
      len(vpm._ENV) == 1, "%d curves, wanted 1" % len(vpm._ENV))
check("and the second name is handed the very curve the first built",
      again is first, "%s" % ("the same one" if again is first
                              else "a second array"))
check("the curve is kept under the name path_key makes",
      (vpm.path_key(LONG_WAY), 5.0, 4000) in vpm._ENV,
      "kept under %s" % sorted(k[0][len(D):] for k in vpm._ENV))


#--------------------------------------------- 2. The curve saved on disc

print("\n2. The curve saved beside it")
vpm.envelope_cache_folder = folder_real
here = vpm.envelope_cache_path(STRAIGHT, 5.0, 4000)
there = vpm.envelope_cache_path(LONG_WAY, 5.0, 4000)
check("both names lead to one saved curve", here == there,
      "%s against %s" % (os.path.basename(here or ""),
                         os.path.basename(there or "")))

vpm._ENV.clear()
vpm.video_envelope(STRAIGHT)             # writes it out
vpm._ENV.clear()
count["n"] = 0
off_disc = vpm.video_envelope(LONG_WAY)  # has to come off disc
check("a curve read back off disc costs no reading of the file",
      count["n"] == 0, "%d ffmpeg processes, wanted 0" % count["n"])
check("and it goes into the store under that same name",
      (vpm.path_key(LONG_WAY), 5.0, 4000) in vpm._ENV
      and len(vpm._ENV) == 1,
      "%d curves, kept under %s"
      % (len(vpm._ENV), sorted(k[0][len(D):] for k in vpm._ENV)))
check("and it is the curve that was worked out",
      len(off_disc) == len(first)
      and float(np.max(np.abs(off_disc - first))) < 1e-4,
      "%d values against %d, largest difference %.2e"
      % (len(off_disc), len(first),
         float(np.max(np.abs(off_disc[:len(first)] - first[:len(off_disc)])))
         if len(off_disc) and len(first) else -1.0))


#------------------------------------------ 3. And the window looks there

print("\n3. What the window does with a file that leaves the list")
source = open(SCRIPT, encoding="utf-8").read()
clears = ("keys = set(path_key(p) for p in gone)" in source
          and "for api_key in [k for k in _ENV if k[0] in keys]" in source)
check("the clean-up looks for the curve under that same name", clears,
      "the two lines the removal needs are %s"
      % ("both there" if clears else "not both there"))
asks = (source.count("if (path_key(file_path), 5.0, 4000) in _ENV")
        + source.count("lambda a: (path_key(a), 5.0, 4000) in _ENV"))
check("and the prework asks the store the same way", asks == 2,
      "%d of the 2 questions go through path_key" % asks)

subprocess.run = run_real
shutil.rmtree(D, ignore_errors=True)
shutil.rmtree(os.environ["VPM_CACHE"], ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
