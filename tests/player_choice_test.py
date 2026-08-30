# -*- coding: utf-8 -*-
"""#62: The player takes the file that holds the In point and the Out point."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import sys, importlib.util
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("VPM_SILENT", "1")   # never beep at a person
from PySide6 import QtWidgets, QtCore
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
vpm = importlib.util.module_from_spec(spec); sys.modules["vpm"] = vpm
spec.loader.exec_module(vpm)

error = []
def check(name, ok, extra=""):
    print("  %-52s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        error.append(name)

# Four files on one time axis: a wide shot over the whole hour, a guest
# inside it, a short one late, and an intro that never comes into question.
SPANS = {
    "/x/Wide.mov":   {"duration": 3600.0, "fps": 30.0,
                      "tc0": 17 * 3600.0, "axis": 0.0},
    "/x/Guest.mov":  {"duration": 1800.0, "fps": 30.0,
                      "tc0": 17 * 3600.0 + 600.0, "axis": 600.0},
    "/x/Short.mov":  {"duration": 60.0, "fps": 30.0,
                      "tc0": 17 * 3600.0 + 3000.0, "axis": 3000.0},
    "/x/Jingle.mp4": {"duration": 10.0, "fps": 30.0,
                      "tc0": None, "axis": None},
}

# Rebuild the interface: only what the four functions touch.
class Value(object):
    def __init__(self, v=""): self.v = v
    def get(self): return self.v
    def set(self, v): self.v = v

files = [(p, "video") for p in SPANS]
clip_kind_values = {"/x/Jingle.mp4": Value(vpm.TYPE_INTRO)}
assign_lines = [(["/x/t1.wav"], Value("Tr1"), Value("Guest.mov"))]
remembered = {}
start_var, end_var = Value(""), Value("")

TYPE_CONTENT = vpm.TYPE_CONTENT if hasattr(vpm, "TYPE_CONTENT") else "content"

def picture_span(file_path):
    return SPANS.get(file_path)

def covers(file_path, text):
    if not (text or "").strip():
        return None
    sp = picture_span(file_path)
    if not sp or not sp["duration"]:
        return None
    try:
        value, absolute = vpm.parse_time_point(text, sp["fps"])
    except Exception:
        return None
    if value is None:
        return None
    if absolute:
        if sp["tc0"] is None:
            return None
        value -= sp["tc0"]
    elif value >= 0:
        if sp["axis"] is None:
            return None
        value -= sp["axis"]
    else:
        value = sp["duration"] + value
    return -0.05 <= value <= sp["duration"] + 0.05

def player_candidates():
    out = []
    for file_path, kind in files:
        if kind != "video":
            continue
        w = clip_kind_values.get(file_path)
        if w is not None and w.get() != TYPE_CONTENT:
            continue
        out.append(file_path)
    return sorted(out, key=lambda x: os.path.basename(x).lower())

def player_suggestion():
    videos = player_candidates()
    if not videos:
        return None
    taken = set(kv.get() for _r, _nv, kv in assign_lines)
    def hit(file_path):
        return sum(1 for t in (start_var.get(), end_var.get())
                   if covers(file_path, t) is True)
    def quality(file_path):
        free = 0 if os.path.basename(file_path) in taken else 1
        sp = picture_span(file_path)
        return (hit(file_path), free, (sp or {}).get("duration") or 0.0)
    last_time = remembered.get("player_file")
    if last_time in videos and hit(last_time) == max(hit(b)
                                                     for b in videos):
        return last_time
    return max(videos, key=quality)

print("0. The rebuild matches the script")
import inspect
source = inspect.getsource(vpm.gui)
for name in ("def covers(file_path, text):",
             "def player_candidates():",
             "def player_suggestion():",
             "def player_follow_up(spot_also=False):",
             "def main_track_show(force=False):"):
    check("in the script: %s" % name.split("(")[0][4:],
            name in source)

print("\n1. Without In/Out point: the camera with no speaker wins (Wide)")
check("Wide", player_suggestion() == "/x/Wide.mov",
        str(player_suggestion()))

print("\n2. In/Out point only inside the wide shot")
start_var.set("17:05:00:00"); end_var.set("17:55:00:00")
check("Wide", player_suggestion() == "/x/Wide.mov",
        str(player_suggestion()))

print("\n3. In/Out point only inside the guest -- that beats the wide shot")
start_var.set("17:15:00:00"); end_var.set("17:35:00:00")
check("both inside the wide shot?", covers("/x/Wide.mov", "17:15:00:00"))
check("Wide (both cover it, Wide has no speaker)",
        player_suggestion() == "/x/Wide.mov", str(player_suggestion()))

print("\n4. Out point beyond the wide shot -> the file that has both")
SPANS["/x/Wide.mov"]["duration"] = 900.0     # Wide ends 17:15
start_var.set("17:20:00:00"); end_var.set("17:30:00:00")
check("Guest", player_suggestion() == "/x/Guest.mov",
        str(player_suggestion()))
SPANS["/x/Wide.mov"]["duration"] = 3600.0

print("\n5. An intro never comes into question")
check("Jingle not among the candidates",
        "/x/Jingle.mp4" not in player_candidates(),
        str(player_candidates()))

print("\n6. 'ignore this video' never comes into question")
clip_kind_values["/x/Wide.mov"] = Value(vpm.TYPE_IGNORED)
start_var.set(""); end_var.set("")
check("Wide is out", "/x/Wide.mov" not in player_candidates())
check("instead the one with no speaker (Short)",
        player_suggestion() == "/x/Short.mov",
        str(player_suggestion()))
del clip_kind_values["/x/Wide.mov"]

print("\n7. The file chosen last keeps its place on a tie")
start_var.set(""); end_var.set("")
remembered["player_file"] = "/x/Short.mov"
check("Short stays", player_suggestion() == "/x/Short.mov",
        str(player_suggestion()))

print("\n8. ... but not when it does not hold the boundaries")
start_var.set("17:20:00:00"); end_var.set("17:30:00:00")
check("no longer Short", player_suggestion() != "/x/Short.mov",
        str(player_suggestion()))
remembered.pop("player_file")

print("\n9. Relative values need the time axis")
start_var.set("+0:15:00")
end_var.set("")
check("Wide covers it", covers("/x/Wide.mov", "+0:15:00") is True)
check("Short does not cover it", covers("/x/Short.mov", "+0:15:00") is False)
SPANS["/x/Wide.mov"]["axis"] = None
check("no axis: no claim",
        covers("/x/Wide.mov", "+0:15:00") is None)
SPANS["/x/Wide.mov"]["axis"] = 0.0

print("\n10. No timecode, no claim for an absolute value")
check("Jingle: None", covers("/x/Jingle.mp4", "17:20:00:00") is None)

print("\n%s" % ("ALL OK" if not error else "FAIL: " + ", ".join(error)))
sys.exit(1 if error else 0)
