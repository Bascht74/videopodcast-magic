"""Does speakers_from_tracks() find the speech sections again?"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys, subprocess
import numpy as np
sys.path.insert(0, os.path.dirname(
    os.path.abspath(__file__)))
from fixture_root import fixture
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
m = importlib.util.module_from_spec(spec); sys.modules["vpm"] = m
spec.loader.exec_module(m)

D = fixture("speakertest"); os.makedirs(D, exist_ok=True)
SR = 48000
# Two tracks that take turns "talking" (noise) over a quiet floor.
want = {"A": [(1.0, 4.0), (8.0, 11.5), (16.0, 18.0)],
        "B": [(5.0, 7.5), (12.0, 15.0), (19.0, 22.0)]}
rng = np.random.default_rng(3)
for name, parts in want.items():
    x = rng.normal(0, 0.002, int(24 * SR))          # noise floor
    for a, b in parts:
        n = int((b - a) * SR)
        # Speech: modulated noise, clearly louder
        x[int(a*SR):int(a*SR)+n] += rng.normal(0, 0.12, n) * (
            0.6 + 0.4 * np.sin(np.linspace(0, 40, n)))
    p = "%s/%s.wav" % (D, name)
    import wave, struct
    with wave.open(p, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())

out = m.speakers_from_tracks([("A", "%s/A.wav" % D, 0.0),
                              ("B", "%s/B.wav" % D, 0.0)], report=print)
error = 0
for name, segs in out:
    print("%s: %s" % (name, [("%.2f-%.2f" % (a, b)) for a, b in segs]))
    assert len(segs) == len(want[name]), "%s: %d sections instead of %d" % (
        name, len(segs), len(want[name]))
    for (a, b), (sa, sb) in zip(segs, want[name]):
        if abs(a - sa) > 0.3 or abs(b - sb) > 0.3:
            print("   off: %.2f-%.2f instead of %.2f-%.2f"
                  % (a, b, sa, sb))
            error += 1
assert not error, "%d edges off" % error
print("\n== the offset is added on ==")
v = m.speakers_from_tracks([("A", "%s/A.wav" % D, 100.0)])
print("A with offset:", v[0][1][:2])
assert abs(v[0][1][0][0] - 101.0) < 0.3
print("\nall good")
