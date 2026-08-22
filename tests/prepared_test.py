# -*- coding: utf-8 -*-
"""Does the preview take the prepared track where there is one?"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import sys, shutil, inspect, importlib.util
sys.path.insert(0, os.path.dirname(
    os.path.abspath(__file__)))
from fixture_root import fixture
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
def check(name, ok, extra=""):
    print("  %-54s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

D = fixture("prepared"); shutil.rmtree(D, ignore_errors=True)
os.makedirs(os.path.join(D, "auphonic-tracks"))
def empty(file_path):
    open(file_path, "wb").write(b"RIFF\x00\x00\x00\x00WAVE")
for n in ("final_Guest_19-04-27-00.wav", "final_Host_19-04-27-00.wav",
          "final_Full-Mix_19-04-27-00.wav", "Guest.wav",
          "Interview_master.wav", "Interview_statistics.json"):
    empty(os.path.join(D, "auphonic-tracks", n))
for n in ("Guest_raw.wav", "Host_raw.wav"):
    empty(os.path.join(D, n))

# Take the two functions out of gui() and run them on their own.
source = inspect.getsource(vpm.gui)
a = source.index("    def prepared_tracks():")
b = source.index("    def line_show(table, file_list):")
piece = "\n".join(line[4:] if line.startswith("    ") else line
                   for line in source[a:b].split("\n"))

class Value(object):
    def __init__(self, v=""): self.v = v
    def get(self): return self.v
    def set(self, v): self.v = v

environment = {
    "os": os, "AUDIO_SUFFIXES": vpm.AUDIO_SUFFIXES, "sorted": sorted,
    "OSError": OSError, "len": len, "print": print,
    "done_folder": Value(os.path.join(D, "auphonic-tracks")),
    "out_folder": Value(D), "commonest_folder": lambda: D,
    "finished_tracks_find": lambda b: None,
    "finished_tracks_deeper": lambda b: None,
    "assign_lines": [],
}
space = {}
exec(piece, environment, space)
environment.update(space)
prepared_tracks = space["prepared_tracks"]
audio_for_camera = space["audio_for_camera"]

print("1. The finished tracks are found")
f = prepared_tracks()
print("   ", {k: os.path.basename(v) for k, v in f.items()})
check("Guest, Host, Full-Mix",
        sorted(f) == ["Full-Mix", "Guest", "Host"], str(sorted(f)))
check("the raw return 'Guest.wav' does not count",
        not any(os.path.basename(v) == "Guest.wav" for v in f.values()))
check("master and statistics do not count",
        not any("master" in v or "statistics" in v for v in f.values()))

print("\n2. The camera with an assigned speaker gets the finished track")
environment["assign_lines"][:] = [
    ([os.path.join(D, "Guest_raw.wav")], Value("Guest"),
     Value("Camera_G.mov")),
    ([os.path.join(D, "Host_raw.wav")], Value("Host"),
     Value("Camera_H.mov"))]
p = audio_for_camera("/x/Camera_G.mov")
check("Guest -> final_", os.path.basename(p or "").startswith("final_"),
        os.path.basename(p or "-"))
check("and it is his own", "Guest" in os.path.basename(p or ""))

print("\n3. Without a finished track the raw recording")
os.rename(os.path.join(D, "auphonic-tracks",
                       "final_Guest_19-04-27-00.wav"),
          os.path.join(D, "auphonic-tracks", "aside.wav"))
p = audio_for_camera("/x/Camera_G.mov")
check("raw recording", os.path.basename(p or "") == "Guest_raw.wav",
        os.path.basename(p or "-"))
os.rename(os.path.join(D, "auphonic-tracks", "aside.wav"),
          os.path.join(D, "auphonic-tracks",
                       "final_Guest_19-04-27-00.wav"))

print("\n4. The wide shot without a speaker gets the Full-Mix")
p = audio_for_camera("/x/Wide.mov")
check("Full-Mix", "Full-Mix" in os.path.basename(p or ""),
        os.path.basename(p or "-"))

print("\n5. Nothing there at all -> nothing")
environment["done_folder"].set("")
environment["out_folder"].set("/does/not/exist")
environment["commonest_folder"] = lambda: "/does/not/exist"
p = audio_for_camera("/x/Wide.mov")
check("no audio for the wide shot", p is None, str(p))
p = audio_for_camera("/x/Camera_G.mov")
check("but the raw recording for the guest",
        os.path.basename(p or "") == "Guest_raw.wav",
        os.path.basename(p or "-"))

print("\n6. The Resolve player takes the finished mix as well")
environment["done_folder"].set(os.path.join(D, "auphonic-tracks"))
environment["out_folder"].set(D)
environment["commonest_folder"] = lambda: D
a2 = source.index("    def audio_for_cut(d, cameras, offset):")
b2 = source.index("    def player_load_cut(numbers):")
piece2 = "\n".join(line[4:] if line.startswith("    ") else line
                for line in source[a2:b2].split("\n"))
environment["file_timecode"] = lambda p: 68667.0 if "final_" in p else None
environment["cameras_in_track_order"] = vpm.cameras_in_track_order
environment["next"] = next
environment["float"] = float
environment["Exception"] = Exception
space2 = {}
exec(piece2, environment, space2)
audio_for_cut = space2["audio_for_cut"]

CAM = [{"track": "Wide", "file": "/x/W.mov", "wide": True,
        "audio_tracks": ["Full-Mix"]},
       {"track": "Guest", "file": "/x/G.mov", "audio_tracks": ["Guest"]}]
OFF = {"Wide": -534.2, "Guest": -331.7}
file, off = audio_for_cut({"start_s": 68667.0}, CAM, OFF)
check("takes the finished Full-Mix",
        "final_Full-Mix" in os.path.basename(file or ""),
        os.path.basename(file or "-"))
check("offset zero, because it starts at the In point", abs(off) < 0.001,
        str(off))

file, off = audio_for_cut({"start_s": 68667.0 + 300.0}, CAM, OFF)
check("In point 300 s later -> offset -300",
        abs(off - (-300.0)) < 0.001, str(off))

environment["done_folder"].set("")
environment["out_folder"].set("/does/not/exist")
environment["commonest_folder"] = lambda: "/does/not/exist"
file, off = audio_for_cut({"start_s": 68667.0}, CAM, OFF)
check("without a mix the camera carrying it on track one",
        file == "/x/W.mov", str(file))
check("and that camera's offset", abs(off - (-534.2)) < 0.001, str(off))

file, off = audio_for_cut({"start_s": None}, CAM, OFF)
check("without a zero point the camera as well", file == "/x/W.mov",
        str(file))

print("\n7. The tick says what is playing")
widget_source = inspect.getsource(vpm.make_player_widgets)
check("label present", "_label_track" in widget_source)
check("names the raw recording", "the raw recording" in widget_source)
check("names the prepared track",
        "brought to broadcast level" in widget_source)

print("\n%s" % ("ALL OK" if not error else "FAIL: " + ", ".join(error)))
sys.exit(1 if error else 0)
