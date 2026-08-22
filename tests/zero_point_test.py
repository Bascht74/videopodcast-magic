# -*- coding: utf-8 -*-
"""#66: Where does programme time start on the clock, and what hangs on it?"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import sys, inspect, importlib.util
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
def check(name, ok, extra=""):
    print("  %-56s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

# Setting: audio runs from 17:00:00 (61200 s), In point at 17:10:00 (61800 s).
# So the statistics count from 61200; the window starts 600 s later.
AUDIO0 = 61200.0
D = {"start_s": AUDIO0, "length_s": 3600.0, "fps": 30.0,
     "speakers": [{"name": "A", "sections": [[0.0, 30.0], [600.0, 660.0],
                                               [1200.0, 1260.0]]}],
     "cameras": [
         {"track": "Wide", "start_s": 61100.0, "file": "W.mov"},
         {"track": "Guest", "start_s": 61500.0, "file": "G.mov"}]}

print("1. Without a window everything stays as it is")
n, _complaint = vpm.apply_time_window(dict(D), "", "")
check("unchanged", n["start_s"] == AUDIO0 and n["length_s"] == 3600.0)

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
source = inspect.getsource(vpm.gui)
a = source.index("    def camera_offset(cameras, origin=None):")
b = source.index("    def player_load_cut(numbers):")
piece = "\n".join(line[4:] if line.startswith("    ") else line
                   for line in source[a:b].split("\n"))
space = {}
exec(piece, {"min": min, "float": float, "any": any}, space)
camera_offset = space["camera_offset"]

off = camera_offset(D["cameras"], n["start_s"])
print("    ", off)
check("Wide started 700 s before the In point",
        abs(off["Wide"] - (-700.0)) < 0.01, str(off["Wide"]))
check("Guest started 300 s before the In point",
        abs(off["Guest"] - (-300.0)) < 0.01, str(off["Guest"]))
check("both negative -- as in the handover file",
        all(x < 0 for x in off.values()))

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
# Programme time 100 s after the In point -> in Wide 800 s after the
# file start.
t = 100.0
off = camera_offset(D["cameras"], 61800.0)
spot = t - off["Wide"]
check("Wide: 100 s programme time = 800 s into the file",
        abs(spot - 800.0) < 0.01, str(spot))
# Counter-check on the clock: 61800 + 100 = 61900; the file began at 61100.
check("matches the clock", abs(spot - (61900.0 - 61100.0)) < 0.01)

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

print("\n%s" % ("ALL OK" if not error else "FAIL: " + ", ".join(error)))
sys.exit(1 if error else 0)
