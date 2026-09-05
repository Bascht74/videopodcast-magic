# -*- coding: utf-8 -*-
"""A measured time axis answers to the same name as a remembered one.

Two things fill that one dictionary -- the measurement, and the project
file read back -- and whoever looks a file up in it cannot tell which of
the two it was. So both have to name a file the same way, or half the
program finds nothing while the other half finds everything.

A needless step in the middle of a path, /tmp/x/./A.wav, does here what
a drive letter and a backslash do on Windows: two names for one file
that compare unequal. No Windows machine is needed to see it.

The sections: what the measurement hands back, what the project file
hands back, that the readers find a file under either name, and that
the window has no reader of its own.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import shutil, subprocess, sys, tempfile, time, wave
vpm = the_program.load()
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

D = tempfile.mkdtemp(prefix="axiskeys_")
RATE = 48000


def build():
    """Three excerpts of one event, and a short video beside them.

    Irregular events make the envelope unambiguous: with an even
    pattern the cross correlation finds many equally good places.
    """
    n = 45 * RATE
    rng = np.random.default_rng(7)
    x = (rng.standard_normal(n) * 0.004).astype(np.float32)
    t = 0.3
    while t < 44.0:
        long_s = float(rng.uniform(0.15, 0.9))
        hz = float(rng.uniform(180, 900))
        i0 = int(t * RATE)
        i1 = min(n, i0 + int(long_s * RATE))
        tt = np.arange(i1 - i0) / float(RATE)
        shape = np.hanning(len(tt)) if len(tt) > 2 else 1.0
        x[i0:i1] += (0.45 * shape * np.sin(2 * np.pi * hz * tt)) \
            .astype(np.float32)
        t += long_s + float(rng.uniform(0.2, 1.6))
    for name, from_s, until in (("A", 0, 30), ("B", 5, 35), ("C", 8, 38)):
        with wave.open(os.path.join(D, name + ".wav"), "wb") as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
            f.writeframes((np.clip(x[int(from_s * RATE):int(until * RATE)],
                                   -1, 1) * 32767).astype("<i2").tobytes())
    # One picture file, for the reader that asks a video where it sits.
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "smptebars=size=160x90:rate=25:duration=2",
                    "-c:v", "libx264", "-preset", "ultrafast",
                    "-pix_fmt", "yuv420p", os.path.join(D, "Cam.mov")],
                   check=True)


build()
A, B, C = [os.path.join(D, x + ".wav") for x in ("A", "B", "C")]
CAM = os.path.join(D, "Cam.mov")
# The same four files, named the long way round.
A2, B2, C2, CAM2 = [os.path.join(D, ".", os.path.basename(p))
                    for p in (A, B, C, CAM)]


def tail(p):
    """The path without the temporary folder, so a line stays readable."""
    return p[len(D):] if p.startswith(D) else p


#---------------------------------------------- 1. What the measurement says

print("1. The axis that was just measured")
check("the long name and the short one are different strings", A != A2,
      "%s against %s" % (tail(A), tail(A2)))
check("and they name one file", os.path.samefile(A, A2),
      "%s and %s" % (tail(A), tail(A2)))
data, text = vpm.measure_time_axis([A2, B2, C2])
axis = (data or {}).get("axis") or {}
wanted = set(vpm.path_key(p) for p in (A2, B2, C2))
print("   %s" % text)
check("a measured axis names its files the way path_key does",
      set(axis) == wanted,
      "%d of 3 named that way, %d names in all"
      % (len(set(axis) & wanted), len(axis)))
check("and holds no second entry under the name it was given",
      A2 not in axis and len(axis) == 3,
      "%d entries, wanted 3" % len(axis))


#--------------------------------------------- 2. What the project file says

print("\n2. The axis read back out of the project file")


def stored(file_path, start, path=None):
    """One line of the timeline as axis_store writes it."""
    k = vpm.file_fingerprint(file_path)
    return {"path": path if path is not None else k[0],
            "mtime": k[1], "size": k[2], "start_s": start}


back = vpm.axis_still_valid(
    {"timeline": [stored(A, 0.0), stored(B, 5.0), stored(C, 8.0)]},
    [A2, B2, C2])
check("a remembered axis names its files like a measured one",
      back is not None and set(back["axis"]) == set(axis),
      "%s against %s" % (sorted(tail(p) for p in (back or {})
                                .get("axis", ())),
                         sorted(tail(p) for p in axis)))
older = vpm.axis_still_valid(
    {"timeline": [stored(A, 0.0, path=A2), stored(B, 5.0, path=B2),
                  stored(C, 8.0, path=C2)]},
    [A, B, C])
check("a project file written the long way round still matches",
      older is not None and set(older["axis"]) == wanted,
      "%d files matched, wanted 3"
      % len((older or {}).get("axis") or {}))
changed = vpm.axis_still_valid(
    {"timeline": [stored(A, 0.0), dict(stored(B, 5.0), mtime=1),
                  stored(C, 8.0)]},
    [A2, B2, C2])
check("a file that really changed still throws the whole axis away",
      changed is None,
      "one file dated 1 in the store, and %s came back"
      % ("nothing" if changed is None else "an axis of %d"
         % len(changed["axis"])))


#------------------------------------------------- 3. The readers find it

print("\n3. Reading a file's place off that axis")
start_long = vpm.audio_start_of(B2, axis)
start_short = vpm.audio_start_of(B, axis)
check("audio_start_of finds a recording named the long way round",
      start_long is not None, "answered %s" % start_long)
check("and gives the same second for both names of it",
      start_long is not None and start_short == start_long,
      "%s against %s" % (start_long, start_short))
check("the two recordings still lie five seconds apart",
      start_long is not None
      and abs(abs(start_long - (vpm.audio_start_of(A2, axis) or 0.0)) - 5.0)
      < 0.2,
      "%.3f s against 5.0 s"
      % abs((start_long or 0.0) - (vpm.audio_start_of(A2, axis) or 0.0)))

span = vpm.file_span(CAM2, {vpm.path_key(CAM): 12.5})
check("file_span finds the video the measurement placed",
      span is not None and span["axis"] == 12.5,
      "answered %s" % (span or {}).get("axis"))

state = {"axis": axis, "speakers_source": C2}
lines = [((A2,), None, vpm.Value("keep")), ((B2,), None, vpm.Value("keep"))]
offset = vpm.voice_axis_offset(state, lines)
check("the separated recording is placed against the earliest of them",
      abs(offset - 8.0) < 0.2, "%.3f s against 8.0 s" % offset)


#--------------------------------------------- 4. And the window agrees

print("\n4. The window has no reader of its own")
source = the_program.whole()
asks = [ln.strip() for ln in source.splitlines()
        if '["axis"].get(' in ln or '(axis or {}).get(' in ln
        or '("axis") or {}).get(' in ln]
raw = [ln for ln in asks if "path_key(" not in ln]
check("every reader of the time axis asks for it in the one shape",
      len(asks) >= 5 and not raw,
      "%d readers, %d of them not in shape: %s"
      % (len(asks), len(raw), raw[:2]))

shutil.rmtree(D, ignore_errors=True)
print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
