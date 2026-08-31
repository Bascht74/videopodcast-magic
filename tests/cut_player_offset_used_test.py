# -*- coding: utf-8 -*-
"""#63: The player has to take the measured offset, not zero."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import sys, importlib.util, inspect, re, time
# A test must never play sound at somebody working next to it. The program
# reads the variable with bool(), so any value silences it, "0" as well.
os.environ.setdefault("VPM_SILENT", "1")
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

# The function itself, not a copy cut out of the source of gui().
camera_offset = vpm.camera_offset
# Three checks further down read the text of gui(), so it is still needed.
source = inspect.getsource(vpm.gui) + inspect.getsource(vpm.camera_offset)

print("1. Handover file of a run -- the offset is taken")
cameras = [{"track": "Wide", "offset": -534.2, "file": "W.mov"},
           {"track": "Guest", "offset": -331.7, "file": "G.mov"},
           {"track": "Hosts", "offset": -516.9, "file": "H.mov"}]
off = camera_offset(cameras)
check("values taken over unchanged",
        off == {"Wide": -534.2, "Guest": -331.7, "Hosts": -516.9},
        str(off))
check("not all zero", any(x != 0.0 for x in off.values()))

print("\n2. Even when one camera has offset 0")
cameras = [{"track": "A", "offset": 0.0}, {"track": "B", "offset": -12.5}]
off = camera_offset(cameras)
check("both values there", off == {"A": 0.0, "B": -12.5}, str(off))

print("\n3. Preview from the statistics -- start_s, the earliest is zero")
cameras = [{"track": "Wide", "start_s": 61200.0},
           {"track": "Guest", "start_s": 61380.5},
           {"track": "Hosts", "start_s": 61200.0}]
off = camera_offset(cameras)
check("without a zero point: counted against the earliest",
        off == {"Wide": 0.0, "Guest": 180.5, "Hosts": 0.0}, str(off))

print("\n4. Nothing known at all -> zero everywhere, no crash")
off = camera_offset([{"track": "A"}, {"track": "B"}])
check("zero", off == {"A": 0.0, "B": 0.0}, str(off))
check("empty list", camera_offset([]) == {})

print("\n5. The formula matches the cut timeline in Resolve")
# Resolve: start_frame = t0 - offset. The player: want = t - offset.
tl = inspect.getsource(vpm.build_cut_timeline)
check("Resolve computes t0 - offset", "t0 - offset" in tl)
player_source = inspect.getsource(vpm.qt_cut_player)
check("the player computes t - offset",
        "t - self.offset.get(who, 0.0)" in player_source)

print("\n6. The audio comes from the camera with the Full-Mix")
check("cameras_in_track_order is used",
        "cameras_in_track_order(cameras)" in source)
mix = [{"camera": "Guest", "track": "Guest", "audio_tracks": ["Guest"]},
       {"camera": "Wide", "track": "Wide",
        "audio_tracks": ["Full-Mix", "Guest"], "wide": True}]
check("the Wide shot with the Full-Mix comes first",
        vpm.cameras_in_track_order(mix)[0]["track"] == "Wide",
        vpm.cameras_in_track_order(mix)[0]["track"])

print("\n7. And the audio offset is the one of that same camera")
check("offset.get(first[track]) instead of start_s",
        'offset.get(first.get("track"), 0.0)' in source)
check("no start_s left in the player build",
        'x.get("start_s")' not in source.split("def player_load_cut")[1]
        .split("def ")[0])

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
