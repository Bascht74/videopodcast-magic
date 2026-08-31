# -*- coding: utf-8 -*-
"""The common time axis, measured out of the sound and without a window."""
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
    check("all three in it", len(a) == 3)
    check("B lies 5 s from A", abs(abs(a[KB]-a[KA]) - 5.0) < 0.2,
            "%.2f" % abs(a[KB]-a[KA]))
    check("C lies 8 s from A", abs(abs(a[KC]-a[KA]) - 8.0) < 0.2,
            "%.2f" % abs(a[KC]-a[KA]))
    check("zero point is 0", abs(min(a.values())) < 1e-6)
    check("without a timecode not absolute", d["absolute"] is False)
    check("none weak", d["weak"] == [])
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
check("absolute", d["absolute"] is True)
check("A sits on its timecode", abs(d["axis"][KA] - 61200.0) < 0.01,
        "%.2f" % d["axis"][KA])
check("the distances stay",
        abs(abs(d["axis"][KB]-d["axis"][KA]) - 5.0) < 0.2)
check("the text says so", "tied to the timecode" in text, text)

print("\n4. One outlier in the timecode does not skew everything")
# Two matching entries, one grossly wrong -- the median wins.
tc = {A: 61200.0, B: 61205.0, C: 99999.0}
d, _t = vpm.measure_time_axis([A, B, C], tc_of=lambda p: tc.get(p))
check("A stays on its timecode", abs(d["axis"][KA] - 61200.0) < 1.0,
        "%.1f" % d["axis"][KA])

print("\n5. When it does not work")
d, text = vpm.measure_time_axis([])
check("nothing in -> nothing out", d == {})
check("and a reason", text == "time axis not measurable", text)
d, text = vpm.measure_time_axis([A])
check("one alone is no axis", d == {})
check("and no blame for it", text == "", repr(text))
d, text = vpm.measure_time_axis(["/nothere.wav", "/neitherthis.wav"])
check("paths into the void -> no crash", d == {})

print("\n6. The interface really calls this path")
source = open(SCRIPT, encoding="utf-8").read()
check("axis_measure only passes it on",
        "return measure_time_axis(paths, real_tc, HOP)" in source)
check("the computation is no longer in gui()",
        source.count("reference = max(envelopes, "
                "key=lambda p: len(envelopes[p]))") == 1)

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
