# -*- coding: utf-8 -*-
"""The common time axis, measured out of the sound and without a window.

Where a file sits, and how fast the recorder that wrote it ran. The
second is what the run divides the offset by before it writes a track,
so the axis has to carry it and the project file has to keep it: with
it thrown away the window measured the speakers on one clock and the
run on another.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import sys, importlib.util, time
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))

D = "/tmp/axis"
A, B, C = D + "/A.wav", D + "/B.wav", D + "/C.wav"
FOREIGN = D + "/foreign.wav"

def build_material():
    """Three excerpts of the same event, plus a file that does not fit.

    Built here when needed -- a test that hangs on material from an
    earlier run reports an error at some point that does not exist.
    """
    import os, wave
    import numpy as np
    if all(os.path.exists(x) for x in (A, B, C, FOREIGN)):
        return
    os.makedirs(D, exist_ok=True)
    r, n = 48000, 45 * 48000
    rng = np.random.default_rng(7)
    x = (rng.standard_normal(n) * 0.004).astype(np.float32)
    # Irregular events make the envelope unambiguous: with an even
    # pattern the cross correlation finds many equally good places.
    t = 0.3
    while t < 44.0:
        length = float(rng.uniform(0.15, 0.9))
        f = float(rng.uniform(180, 900))
        i0, i1 = int(t * r), min(n, int(t * r) + int(length * r))
        tt = np.arange(i1 - i0) / r
        h = np.hanning(len(tt)) if len(tt) > 2 else 1.0
        x[i0:i1] += (0.45 * h * np.sin(2 * np.pi * f * tt)).astype(np.float32)
        t += length + float(rng.uniform(0.2, 1.6))

    def write(file_path, samples):
        with wave.open(file_path, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(r)
            w.writeframes((np.clip(samples, -1, 1) * 32767)
                          .astype("<i2").tobytes())

    for file_path, from_s, until in ((A, 0, 30), (B, 5, 35), (C, 8, 38)):
        write(file_path, x[int(from_s * r):int(until * r)])
    tt = np.arange(30 * r) / r
    write(FOREIGN, 0.3 * np.sin(2 * np.pi * 200 * tt))

build_material()
# The axis names its files the way path_key does: on a Mac that is the
# path itself, on Windows the case and the separator are settled with
# it, and a plain string would find nothing there.
KA, KB, KC = vpm.path_key(A), vpm.path_key(B), vpm.path_key(C)
# A, B and C start 0, 5 and 8 s in: whoever starts later sits further
# along the common axis.
print("1. Three recordings of the same event")
d, text = vpm.measure_time_axis([A, B, C])
check("an axis comes out", bool(d), text)
if d:
    a = d["axis"]
    print("   %s" % {k.rsplit("/", 1)[-1]: round(v, 2) for k, v in a.items()})
    check("all three in it", len(a) == 3,
            "%d on the axis: %s" % (len(a), sorted(
                k.rsplit("/", 1)[-1] for k in a)))
    check("B lies 5 s from A", abs(abs(a[KB]-a[KA]) - 5.0) < 0.2,
            "%.2f" % abs(a[KB]-a[KA]))
    check("C lies 8 s from A", abs(abs(a[KC]-a[KA]) - 8.0) < 0.2,
            "%.2f" % abs(a[KC]-a[KA]))
    check("zero point is 0", abs(min(a.values())) < 1e-6,
            "the earliest sits at %.6f s, wanted 0" % min(a.values()))
    check("without a timecode not absolute", d["absolute"] is False,
            "absolute is %s, wanted False" % (d["absolute"],))
    check("none weak", d["weak"] == [],
            "%d do not fit: %s" % (len(d["weak"]), d["weak"]))
    check("the text says so", "the same point" in text, text)

print("\n2. A file that does not belong")
d, text = vpm.measure_time_axis([A, B, FOREIGN])
check("the others stay", bool(d) and len(d["axis"]) == 2, text)
check("the foreign one is named", d and d["weak"] == [FOREIGN],
        str(d.get("weak")))
check("and counted in the text", "1 file does not fit" in text, text)

print("\n3. With a timecode the axis hangs off the clock")
d, text = vpm.measure_time_axis(
    [A, B, C], tc_of=lambda p: 61200.0 if p == A else None)
check("absolute", d["absolute"] is True,
        "absolute is %s, wanted True" % (d["absolute"],))
check("A sits on its timecode", abs(d["axis"][KA] - 61200.0) < 0.01,
        "%.2f" % d["axis"][KA])
check("the distances stay",
        abs(abs(d["axis"][KB]-d["axis"][KA]) - 5.0) < 0.2,
        "B lies %.2f s from A, wanted 5.00"
        % abs(d["axis"][KB]-d["axis"][KA]))
check("the text says so", "tied to the timecode" in text, text)

print("\n4. One outlier in the timecode does not skew everything")
# Two matching entries, one grossly wrong -- the median wins.
tc = {A: 61200.0, B: 61205.0, C: 99999.0}
d, _t = vpm.measure_time_axis([A, B, C], tc_of=lambda p: tc.get(p))
check("A stays on its timecode", abs(d["axis"][KA] - 61200.0) < 1.0,
        "%.1f" % d["axis"][KA])

print("\n5. When it does not work")
d, text = vpm.measure_time_axis([])
check("nothing in -> nothing out", d == {},
        "the axis holds %d files, wanted none: %s"
        % (len(d.get("axis") or {}), d))
check("and a reason", text == "time axis not measurable", text)
d, text = vpm.measure_time_axis([A])
check("one alone is no axis", d == {},
        "the axis holds %d files, wanted none: %s"
        % (len(d.get("axis") or {}), d))
check("and no blame for it", text == "", repr(text))
d, text = vpm.measure_time_axis(["/nothere.wav", "/neitherthis.wav"])
check("paths into the void -> no crash", d == {},
        "the axis holds %d files, wanted none: %s"
        % (len(d.get("axis") or {}), d))

print("\n6. The interface really calls this path")
source = open(SCRIPT, encoding="utf-8").read()
PASSED_ON = "return axis_with_blocks(paths, real_tc, HOP, blocks_of)"
check("axis_measure only passes it on",
        PASSED_ON in source,
        "the line stands %d times in %d characters of source"
        % (source.count(PASSED_ON), len(source)))
in_source = source.count("reference = max(envelopes, "
        "key=lambda p: len(envelopes[p]))")
check("the computation is no longer in gui()", in_source == 1,
        "the line stands %d times in the source, wanted once" % in_source)

print("\n7. How fast each recorder ran")
# Only that the number is there and comes back. The value cannot be
# checked on this material: the regression that finds the speed wants
# sample points spread over the runtime, and half a minute holds too
# few of them, so every file here answers 1. A drift is measured on an
# episode, not on thirty seconds.
d, _t = vpm.measure_time_axis([A, B, C])
speed = (d or {}).get("clock") or {}
check("a speed for every file on the axis",
        sorted(speed) == sorted((d or {}).get("axis") or {}),
        "%d speeds against %d places"
        % (len(speed), len((d or {}).get("axis") or {})))
# Made up, not measured: with the measured ones all at 1 the road
# through the file would be green even where nothing travelled it.
made_up = dict((vpm.path_key(p), b) for p, b in
               ((A, 1.0), (B, 0.999969035), (C, 1.000031)))
places = dict((p, d["axis"][vpm.path_key(p)]) for p in (A, B, C))
entries = vpm.timeline_entries(places, made_up)
back = vpm.axis_still_valid({"timeline": entries}, [A, B, C])
check("the speed survives the project file",
        back is not None and all(
            abs(back["clock"][k] - made_up[k]) < 1e-8 for k in made_up),
        "put in %s, read back %s"
        % ({k.rsplit("/", 1)[-1]: v for k, v in made_up.items()},
           {k.rsplit("/", 1)[-1]: v
            for k, v in ((back or {}).get("clock") or {}).items()}))
older = [dict((k, v) for k, v in e.items() if k != "clock") for e in entries]
check("and a file stored without one comes back at 1",
        vpm.axis_still_valid({"timeline": older}, [A, B, C])["clock"]
        == dict((vpm.path_key(p), 1.0) for p in (A, B, C)),
        "a project file written before the speed was kept says %s"
        % vpm.axis_still_valid({"timeline": older}, [A, B, C])["clock"])

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
