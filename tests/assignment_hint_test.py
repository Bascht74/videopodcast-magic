"""Does the suggestion find the right camera for the speaker?"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("VPM_SCRIPT") or os.path.join(
    os.path.dirname(HERE), "videopodcast-magic.py")
import importlib.util, sys
spec = importlib.util.spec_from_file_location(
    "vpm", SCRIPT)
m = importlib.util.module_from_spec(spec); sys.modules["vpm"] = m
spec.loader.exec_module(m)

CAMERAS = ["/x/Colourchart.mov", "/x/Colourchart2.mov", "/x/Jingle.mp4",
           "/x/Guset_08141714_C003.mov",
           "/x/Hosts_08141714_C002.mov",
           "/x/Wide_08141714_C007.mov"]
CASES = [("Guest", "Guset_08141714_C003.mov"),  # typo in the file name
         ("Host", "Hosts_08141714_C002.mov"),
         # Not "Co-host": that scores 0.67 against "Hosts" and would
         # turn this fuzzy-match case into a no-match case.
         ("Cohosts", "Hosts_08141714_C002.mov"),
         ("Full-Mix", None),                    # belongs to no camera
         ("Wide", "Wide_08141714_C007.mov"),
         ("", None), ("Xy", None)]
error = 0
for speaker, expected in CASES:
    t = m.camera_for_speaker(speaker, CAMERAS)
    got = os.path.basename(t) if t else None
    ok = got == expected
    error += 0 if ok else 1
    print("  %-14s -> %-34s %s"
          % (speaker or "(empty)", got,
             "ok" if ok else "FAIL, expected %s" % expected))
assert not error, "%d cases wrong" % error
print("\nall good")
