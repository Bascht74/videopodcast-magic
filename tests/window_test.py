"""Does the window show its length -- even if the file starts later?"""
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

# Rebuild only the calculation, without the whole interface
def duration(in_point, out_point, fps=30.0):
    a, abs_a = m.parse_time_point(in_point, fps)
    b, abs_b = m.parse_time_point(out_point, fps)
    if a is None or b is None or abs_a != abs_b or b <= a:
        return ""
    return m.as_hms(b - a)

CASES = [("17:02:16:17", "18:23:14:04", "1:20:57.567"),
         ("17:20:56:16", "18:17:06:15", "0:56:09.967"),
         ("+0:00:10.000", "+0:01:10.000", "0:01:00.000"),
         ("", "18:00:00:00", ""),
         ("18:00:00:00", "17:00:00:00", "")]
error = 0
for a, b, want in CASES:
    have = duration(a, b)
    ok = have == want
    error += 0 if ok else 1
    print("  %-16s %-16s -> %-14s %s"
          % (a or "(empty)", b, have or "(empty)",
             "ok" if ok else "FAIL, expected %s" % want))
assert not error
# And the old way, which took the file as the yardstick:
tc0 = m.parse_timecode("17:06:35:20", 30.0)
old = (m.parse_timecode("18:23:14:04", 30.0) - tc0) - max(
    0.0, m.parse_timecode("17:02:16:17", 30.0) - tc0)
print("\n  the old way would have shown:", m.as_hms(old))
assert m.as_hms(old) == "1:16:38.467", m.as_hms(old)
# ----------------------------------------------------------------------
# No boundary inside a jingle
#
# An intro is set in front of the material, not cut into it, so no point
# inside it can be a boundary of the episode.
print("\n  no boundary inside what is not on the axis")
CASES = [
    ("Interview_C002.mov", m.TYPE_CONTENT, False),
    ("Totale_C003.mov", m.TYPE_WIDE, False),
    ("Jingle.mp4", m.TYPE_INTRO, True),
    ("Abspann.mp4", m.TYPE_OUTRO, True),
    ("Fehlstart.mov", m.TYPE_IGNORED, True),
]
error = 0
for name, kind, barred in CASES:
    said = m.not_on_the_axis("/tmp/%s" % name, {}, {"kind:/tmp/%s" % name: kind})
    ok = bool(said) is barred
    error += 0 if ok else 1
    # A reason is as much part of this as the greying out: greyed out
    # with nothing beside it reads as a fault in the program.
    if barred and ok:
        ok = name in said
        error += 0 if ok else 1
    print("  %-22s %-10s -> %-8s %s"
          % (name, kind, "barred" if said else "usable",
             "ok" if ok else "FAIL, wanted %s and its name in the reason"
             % ("barred" if barred else "usable")))
assert not error
# Nothing in the player bars nothing: the four buttons are then held by
# the axis alone, which is the older rule and still the one that counts.
assert m.not_on_the_axis(None, {}, {}) == ""
assert m.not_on_the_axis("", {}, {}) == ""
# A file nobody has answered for counts as content, or opening a project
# would bar the buttons until every Kind has been looked at once.
assert m.not_on_the_axis("/tmp/unanswered.mov", {}, {}) == ""
print("  a file nobody answered for counts as content     ok")

print("\nall good")
