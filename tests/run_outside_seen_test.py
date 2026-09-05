# -*- coding: utf-8 -*-
"""Every call to another program is in the log, and none in the output.

ffmpeg and ffprobe are where a run spends its minutes, and from
outside a file read once and a file read four times look the same. So
each call is written down with its duration -- and where a measurement
was already at hand, the line says that instead.

The lines go into the log file only. A run's output is read by a
person and by the window, and a diagnostic line landing between two
progress bars tears them apart.

The last section is about the store that makes a measurement outlive
the program: what it is filed under is built in one place, because
the day it was spelled out twice the answer became "not measured" for
ever and the work went back in the queue on every redraw.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import ast, io, json, subprocess, sys, tempfile, time

vpm = the_program.load()

WORK = tempfile.mkdtemp(prefix="outsideseen_")
began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def said(work, *more):
    """Run *work* with the log going into a file, and return the lines."""
    where = os.path.join(WORK, "aside_%d.log" % len(os.listdir(WORK)))
    was, vpm._LOG_ASIDE[:] = list(vpm._LOG_ASIDE), []
    vpm._LOG_ASIDE.append(io.open(where, "w", encoding="utf-8"))
    try:
        work(*more)
        vpm.outside_flush()
    finally:
        try:
            vpm._LOG_ASIDE[0].close()
        except Exception:
            pass
        vpm._LOG_ASIDE[:] = was
    return io.open(where, encoding="utf-8").read().splitlines()


#------------------------------------------- 1. What one line says
print("1. A call is written down with its tool, its time and its file")

lines = said(lambda: vpm.outside_say("ffprobe", "Guest_0001.wav", 0.03))
check("one call is one line", len(lines) == 1, "%d lines" % len(lines))
one = lines[0] if lines else ""
check("the line carries the tool", "ffprobe" in one, repr(one[:70]))
check("and the file it is about", "Guest_0001.wav" in one, repr(one[:70]))
check("and how long it took", "0.03 s" in one, repr(one[:70]))

lines = said(lambda: vpm.outside_say("channelfacts", "Guest_0001.wav",
                                     what="read back from the store"))
check("a measurement already at hand says so instead of a duration",
      len(lines) == 1 and "read back from the store" in lines[0]
      and " s " not in lines[0],
      repr((lines or [""])[0][:70]))


#------------------------------ 2. The same call over and over: one line
print("\n2. The same call over and over is held back and summed up")


def twenty_then_one():
    for _ in range(20):
        vpm.outside_say("ffmpeg", "Guest_0001.wav", 0.055)
    vpm.outside_say("ffprobe", "Guest_0001.wav", 0.03)


lines = said(twenty_then_one)
check("twenty of the same and one other make two lines",
      len(lines) == 2, "%d lines: %r" % (len(lines), lines[:2]))
first = lines[0] if lines else ""
check("the held-back line carries the count", "20 calls" in first,
      repr(first[:70]))
check("and the time they took together, not one of them",
      "1.10 s" in first, repr(first[:70]))


#--------------------------------- 3. The output of a run stays clean
print("\n3. A run writes none of this into its own output")

# The fixtures the suite builds: two recordings and a camera are
# enough to make a run measure something and call ffmpeg for it.
media = os.environ.get("VPM_FIXTURES") or ""
job = os.path.join(media, "interview") if media else ""
files = sorted(os.path.join(job, f) for f in os.listdir(job)
               if f.lower().endswith((".wav", ".mov"))) if os.path.isdir(job) else []
if len(files) < 2:
    print("SKIPPED: no material under %s -- run this through run.sh, which "
          "builds the fixtures and points VPM_FIXTURES at them" % (media or "-"))
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "Good as far as it went.")
    sys.exit(1 if bad else 0)

out = subprocess.run(
    [sys.executable, SCRIPT, "--dry-run", "--no-preflight", "--no-metrics"]
    + files, capture_output=True, text=True,
    env=dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="en",
             VPM_NO_UPDATE_CHECK="1", VPM_NO_SPEAKER_SPLIT="1"))
whole = out.stdout + out.stderr
marks = [l for l in whole.splitlines()
         if l.startswith((vpm.EXT_MARK, vpm.ENV_MARK, vpm.BAD_MARK))]
check("the run itself came through", out.returncode == 0,
      "return code %d" % out.returncode)
check("and its output holds no diagnostic line", not marks,
      "%d of %d lines: %r" % (len(marks), len(whole.splitlines()),
                              marks[:1]))


#------------------- 4. The store that outlives the program, by one name
print("\n4. What the store is filed under is built in one place")

# The bug this is about: the name was spelled out with the recipe mark
# in the one place that stores, and without it in the two that ask
# whether something was measured. Both must come from the same call.
source = the_program.whole()
tree = ast.parse(the_program.text())
spelt = source.count('"channelfacts')
check("the name of the store is not spelled out beside its maker",
      spelt <= 1, "%d places write it as text, wanted at most 1" % spelt)

mark = vpm.channel_facts_name()
check("and the name it makes carries a recipe mark",
      mark.startswith("channelfacts-") and len(mark) > len("channelfacts-"),
      repr(mark))

# Measured, not reasoned: the same file in a second process. The store
# lives beside the user's caches, so a fresh process finds it.
probe = os.path.join(WORK, "Guest_REC00001.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                "anoisesrc=d=8:c=pink:r=48000:a=0.5", "-ac", "2",
                "-c:a", "pcm_s16le", probe], capture_output=True)
ask = os.path.join(WORK, "ask.py")
io.open(ask, "w", encoding="utf-8").write(
    "import importlib.util, sys, time\n"
    "spec = importlib.util.spec_from_file_location('vpm', %r)\n"
    "vpm = importlib.util.module_from_spec(spec); sys.modules['vpm'] = vpm\n"
    "spec.loader.exec_module(vpm)\n"
    "t = time.monotonic(); got = vpm.channel_facts_cached(%r)\n"
    "print('%%.4f %%d' %% (time.monotonic() - t, got.get('channels', 0)))\n"
    % (SCRIPT, probe))
takes = []
for _ in range(2):
    got = subprocess.run([sys.executable, ask], capture_output=True, text=True,
                         env=dict(os.environ, LANG="C", LC_ALL="C",
                                  LANGUAGE="en", VPM_NO_UPDATE_CHECK="1"))
    parts = (got.stdout or "").split()
    takes.append((float(parts[0]), int(parts[1])) if len(parts) == 2
                  else (None, 0))
check("a fresh process measures the file the first time",
      takes[0][0] is not None and takes[0][1] == 2,
      "%r s, %d channels" % takes[0])
check("and the next process reads it back instead of measuring again",
      takes[1][0] is not None and takes[0][0] is not None
      and takes[1][0] < takes[0][0] / 2.0,
      "%.4f s against %.4f s the first time" % (takes[1][0] or -1,
                                                takes[0][0] or -1))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
