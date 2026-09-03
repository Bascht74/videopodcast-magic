# -*- coding: utf-8 -*-
"""#66: Where does programme time start on the clock, and what hangs on it?"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast_magic.py")
import copy, sys, inspect, importlib.util, time
# A test must never play sound at somebody working next to it. The
# program reads the variable with bool(), so even "0" silences it.
os.environ.setdefault("VPM_SILENT", "1")
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

began = time.time()
done = 0
error = []
def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-56s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

# Audio runs from 17:00:00 (61200 s); the In point below is ten minutes
# later.
AUDIO0 = 61200.0
D = {"start_s": AUDIO0, "length_s": 3600.0, "fps": 30.0,
     "speakers": [{"name": "A", "sections": [[0.0, 30.0], [600.0, 660.0],
                                               [1200.0, 1260.0]]}],
     "cameras": [
         {"track": "Wide", "start_s": 61100.0, "file": "W.mov"},
         {"track": "Guest", "start_s": 61500.0, "file": "G.mov"}]}

print("1. Without a window everything stays as it is")
n, _complaint = vpm.apply_time_window(dict(D), "", "")
check("unchanged", n["start_s"] == AUDIO0 and n["length_s"] == 3600.0,
        "start_s %s and length_s %s, wanted %.1f and 3600.0"
        % (n["start_s"], n["length_s"], AUDIO0))

print("\n2. With the In point at 17:10:00 the zero point moves along")
n, _complaint = vpm.apply_time_window(dict(D), "17:10:00:00", "")
check("start_s is the In point now", n["start_s"] == 61800.0,
        str(n["start_s"]))
check("length shorter by 600 s", abs(n["length_s"] - 3000.0) < 0.01,
        str(n["length_s"]))
segs = n["speakers"][0]["sections"]
print("    sections:", segs)
check("the section at 600 sits at 0 now", abs(segs[0][0]) < 0.01,
        str(segs[0]))
check("the section at 1200 sits at 600 now",
        abs(segs[1][0] - 600.0) < 0.01, str(segs[1]))

print("\n3. The camera offset counts against the zero point")
camera_offset = vpm.camera_offset

off = camera_offset(D["cameras"], n["start_s"])
print("    ", off)
check("Wide started 700 s before the In point",
        abs(off["Wide"] - (-700.0)) < 0.01, str(off["Wide"]))
check("Guest started 300 s before the In point",
        abs(off["Guest"] - (-300.0)) < 0.01, str(off["Guest"]))
check("both negative -- as in the handover file",
        all(x < 0 for x in off.values()),
        "%s, every one wanted below 0" % (off,))

print("\n4. Without a zero point the earliest camera holds")
off = camera_offset(D["cameras"], None)
check("the earliest is zero", off == {"Wide": 0.0, "Guest": 400.0},
        str(off))

print("\n5. The handover file still wins")
real = [{"track": "Wide", "offset": -534.2},
        {"track": "Guest", "offset": -331.7}]
off = camera_offset(real, 99999.0)
check("the zero point is ignored where an offset stands",
        off == {"Wide": -534.2, "Guest": -331.7}, str(off))

print("\n6. The place in the file is right in the example")
t = 100.0
off = camera_offset(D["cameras"], 61800.0)
spot = t - off["Wide"]
check("Wide: 100 s programme time = 800 s into the file",
        abs(spot - 800.0) < 0.01, str(spot))
# Counter-check on the clock: 61800 + 100 = 61900; the file began at 61100.
check("matches the clock", abs(spot - (61900.0 - 61100.0)) < 0.01,
        "%.2f s into the file against %.2f s off the clock"
        % (spot, 61900.0 - 61100.0))

print("\n7. In point given as a relative time")
n, _complaint = vpm.apply_time_window(dict(D), "+0:10:00", "")
check("start_s is 61800", abs(n["start_s"] - 61800.0) < 0.01,
        str(n["start_s"]))

print("\n8. Without start_s nothing is invented")
without = dict(D); without["start_s"] = None
n, _complaint = vpm.apply_time_window(without, "+0:10:00", "")
check("start_s stays None", n.get("start_s") is None, str(n.get("start_s")))
check("but the window takes effect all the same",
        abs(n["length_s"] - 3000.0) < 0.01, str(n["length_s"]))

print("\n9. An impossible window is said out loud, not swallowed")
n, complaint = vpm.apply_time_window(dict(D), "+2:00:00", "+1:00:00")
check("Out point before In point is complained about",
        bool(complaint), complaint)
check("and the handover comes back untrimmed",
        n["length_s"] == 3600.0, str(n["length_s"]))
n, complaint = vpm.apply_time_window(dict(D), "+0:00:00", "+0:00:03")
check("under five seconds too", bool(complaint), complaint)
n, complaint = vpm.apply_time_window(dict(D), "", "")
check("no window, no complaint", not complaint, complaint)

print("\n10. A window shifts nothing against anything else")
# The invariant: the spot in a camera file is the section start minus
# that camera's offset. A window cuts off front and back but must not
# move the two against each other, so every spot comes out unchanged.
INSIDE = {"start_s": AUDIO0, "length_s": 3600.0, "fps": 30.0,
          "speakers": [{"name": "A", "sections": [[700.0, 760.0],
                                                    [1500.0, 1560.0]]},
                       {"name": "B", "sections": [[2400.0, 2460.0]]}],
          "words": [[705.0, 705.4, "so"], [2405.0, 2405.6, "then"]],
          "cameras": [
              {"track": "Wide", "start_s": 61100.0, "file": "W.mov"},
              {"track": "Guest", "start_s": 61500.0, "file": "G.mov"}]}
# The other shape a camera comes in: a measured offset instead of a
# wall clock start. Both describe the same setting and must agree.
INSIDE_OFF = copy.deepcopy(INSIDE)
INSIDE_OFF["cameras"] = [
    {"track": "Wide", "offset": -100.0, "file": "W.mov"},
    {"track": "Guest", "offset": 300.0, "file": "G.mov"}]
SHAPES = (("wall clock start", INSIDE), ("measured offset", INSIDE_OFF))
# Both windows name the same piece, once relatively and once on the clock.
WINDOWS = (("relative", "+0:10:00", "-0:05:00"),
           ("absolute", "17:10:00:00", "17:55:00:00"))


def spots(h):
    """Where every section and word sits inside each camera file."""
    off = camera_offset(h.get("cameras") or [], h.get("start_s"))
    out = {}
    for sp in (h.get("speakers") or []):
        for i, seg in enumerate(sp.get("sections") or []):
            for track in sorted(off):
                out["%s#%d in %s" % (sp.get("name"), i, track)] = \
                    seg[0] - off[track]
    for i, w in enumerate(h.get("words") or []):
        for track in sorted(off):
            out["word%d in %s" % (i, track)] = w[0] - off[track]
    return out


def same_spots(name, before, after):
    """Compare two spot tables and say how far the worst one wandered."""
    lost = [k for k in before if k not in after]
    moved = dict((k, after[k] - before[k]) for k in before
                 if k in after and abs(after[k] - before[k]) > 0.001)
    worst = max(moved.values(), key=abs) if moved else 0.0
    check(name, not lost and not moved,
          "%d lost, %d moved, worst %+.3f s" % (len(lost), len(moved), worst))


check("both camera shapes describe the same setting",
        camera_offset(INSIDE["cameras"], AUDIO0) ==
        camera_offset(INSIDE_OFF["cameras"], AUDIO0),
        str(camera_offset(INSIDE_OFF["cameras"], AUDIO0)))
for shape, source in SHAPES:
    before = spots(source)
    for kind, in_p, out_p in WINDOWS:
        n, complaint = vpm.apply_time_window(copy.deepcopy(source),
                                             in_p, out_p)
        check("%s, %s: no complaint" % (shape, kind), not complaint,
                complaint)
        kept = [len(s["sections"]) for s in n["speakers"]]
        check("%s, %s: no section fell out of the window"
                % (shape, kind), kept == [2, 1], str(kept))
        check("%s, %s: no word fell out either" % (shape, kind),
                len(n.get("words") or []) == 2,
                str(len(n.get("words") or [])))
        same_spots("%s, %s: the spot in the file is unchanged"
                   % (shape, kind), before, spots(n))

print("\n11. The window does not act a second time")
# The second pass must find nothing to do: a number that moves here
# would move again on every further pass.
for shape, source in SHAPES:
    once, _complaint = vpm.apply_time_window(copy.deepcopy(source),
                                             "17:10:00:00", "17:55:00:00")
    again, complaint = vpm.apply_time_window(copy.deepcopy(once),
                                             "17:10:00:00", "17:55:00:00")
    check("%s: no complaint on the second pass" % shape, not complaint,
            complaint)
    check("%s: the zero point stays put" % shape,
            abs(float(again["start_s"]) - float(once["start_s"])) < 0.001,
            "%s -> %s" % (once["start_s"], again["start_s"]))
    check("%s: the length stays" % shape,
            abs(again["length_s"] - once["length_s"]) < 0.001,
            "%.3f -> %.3f" % (once["length_s"], again["length_s"]))
    check("%s: the sections stay" % shape,
            [s["sections"] for s in again["speakers"]] ==
            [s["sections"] for s in once["speakers"]],
            str([s["sections"] for s in again["speakers"]]))
    check("%s: the camera offsets stay" % shape,
            camera_offset(again["cameras"], again["start_s"]) ==
            camera_offset(once["cameras"], once["start_s"]),
            str(camera_offset(again["cameras"], again["start_s"])))
    same_spots("%s: and the spot in the file stays" % shape,
               spots(once), spots(again))
# The quiet way a window acts twice: the handover is changed under the
# caller's hands and the next holder works on something already trimmed.
for shape, source in SHAPES:
    handed = copy.deepcopy(source)
    vpm.apply_time_window(handed, "+0:10:00", "-0:05:00")
    check("%s: the handover handed in is left alone" % shape,
            handed == source, "changed" if handed != source else "")

print("\n12. Relative In and Out points give a length that makes sense")
# This pair once came out as 18 hours and once as zero, both unnoticed.
n, complaint = vpm.apply_time_window(copy.deepcopy(INSIDE),
                                     "+0:10:00", "-0:05:00")
check("no complaint", not complaint, complaint)
check("2700 s -- ten minutes off the front, five off the back",
        abs(n["length_s"] - 2700.0) < 0.001, "%.3f" % n["length_s"])
check("neither zero nor longer than the material",
        0.0 < n["length_s"] <= 3600.0, "%.3f" % n["length_s"])
check("the zero point moved by the head only",
        abs(n["start_s"] - 61800.0) < 0.001, str(n["start_s"]))
absolute, _complaint = vpm.apply_time_window(copy.deepcopy(INSIDE),
                                             "17:10:00:00", "17:55:00:00")
keys = sorted(set(n) | set(absolute))
apart = [k for k in keys if n.get(k) != absolute.get(k)]
check("and it says the same as the absolute window", n == absolute,
        "%d of %d fields differ: %s" % (len(apart), len(keys), apart))
n, complaint = vpm.apply_time_window(copy.deepcopy(INSIDE), "", "-0:05:00")
check("Out point alone: 3300 s", abs(n["length_s"] - 3300.0) < 0.001,
        "%.3f" % n["length_s"])
check("Out point alone leaves the zero point where it was",
        abs(n["start_s"] - AUDIO0) < 0.001, str(n["start_s"]))
n, complaint = vpm.apply_time_window(copy.deepcopy(INSIDE), "+0:10:00", "")
check("In point alone: 3000 s", abs(n["length_s"] - 3000.0) < 0.001,
        "%.3f" % n["length_s"])
n, complaint = vpm.apply_time_window(copy.deepcopy(INSIDE), "+60", "+120")
check("bare seconds are seconds: a minute",
        abs(n["length_s"] - 60.0) < 0.001, "%.3f" % n["length_s"])

print("\n13. No window is a case of its own")
for shape, source in SHAPES:
    for text in ("", None, "   "):
        n, complaint = vpm.apply_time_window(copy.deepcopy(source),
                                             text, text)
        check("%s, %r: no complaint" % (shape, text), not complaint,
                complaint)
        check("%s, %r: nothing changed" % (shape, text), n == source,
                "changed" if n != source else "")
        same_spots("%s, %r: the spot in the file stays" % (shape, text),
                   spots(source), spots(n))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(error) if error else "ALL OK")
sys.exit(1 if error else 0)
