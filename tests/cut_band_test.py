"""Does the cut band show the computed cut correctly?"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import sys, importlib.util
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6 import QtWidgets, QtCore, QtGui
app = QtWidgets.QApplication(sys.argv[:1])
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
m = importlib.util.module_from_spec(spec); sys.modules["vpm"] = m
spec.loader.exec_module(m)

# A conversation of three voices, taking turns, over ten minutes.
import random
random.seed(7)
names = ["Host", "Co-host", "Guest"]
segs = {n: [] for n in names}
t = 0.0
while t < 600:
    who = names[random.randrange(3)]
    d = random.uniform(1.5, 14.0)
    segs[who].append((round(t, 2), round(min(600.0, t + d), 2)))
    t += d + random.uniform(0.1, 0.8)
d = {"speakers": [{"name": n, "sections": segs[n]} for n in names],
     "cameras": [{"track": "Hosts", "speakers": ["Host", "Co-host"]},
                 {"track": "Guest", "speakers": ["Guest"]},
                 {"track": "Wide", "speakers": []}],
     "length_s": 600.0}
numbers = m.cut_statistics(d, 1.2, 0.3, 45.0, 2.5, 120.0, True)
print("Shots:", numbers["shots"])
print("Colours:", numbers["colours"])
assert numbers.get("cut"), "no cut list came back"
assert len(numbers["cut"]) == numbers["shots"]
assert set(numbers["colours"]) == {"Hosts", "Guest", "Wide"}
assert len(set(numbers["colours"].values())) == 3, "colours handed out twice"
print("Wide has", numbers["colours"]["Wide"], "-- expected",
      m.CLIP_COLOURS_RGB["Tan"])
assert numbers["colours"]["Wide"] == m.CLIP_COLOURS_RGB["Tan"]

CutBand = m.qt_cut_band(QtCore, QtGui, QtWidgets, QtCore.Qt)
band = CutBand()
band.resize(1200, 46)
band.set(numbers["cut"], numbers["colours"], 600.0)
band.label_set(210.0)
# A by-product for looking at, not part of the check. Same place as the
# window scripts write to, so the pictures of one run sit together.
shots = os.environ.get("VPM_SHOTS") or os.path.join(HERE, "shots")
os.makedirs(shots, exist_ok=True)
band.grab().save(os.path.join(shots, "5_cut_band.png"))
# The band may claim three colours and still paint only two, so count
# them in the picture itself.
video = band.grab().toImage()
seen = set()
for x in range(0, 1200, 3):
    seen.add(video.pixelColor(x, 20).name())
print("Colours in the picture:", sorted(seen))
assert len(seen) >= 3, seen
print("\nall good")
