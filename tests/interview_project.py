"""Write the project file for the interview fixture.

A run moves the project file into the output folder. Written afresh
before every suite, so the fixture still has one to open.
"""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(
    os.path.abspath(__file__)))
from fixture_root import fixture

folder = sys.argv[1] if len(sys.argv) > 1 else fixture("interview")
if os.path.isdir(folder):
    files = [{"path": p, "kind": "audio"}
             for p in sorted(glob.glob(folder + "/*.wav"))]
    files += [{"path": p, "kind": "video"}
              for p in sorted(glob.glob(folder + "/*.mov"))]
    with open(folder + "/videopodcast-magic_Interview_2.json", "w") as f:
        json.dump({"format": 3, "version": "fixture", "files": files,
                   "timeline": [], "timeline_absolute": False, "call": [],
                   "production": "Interview 2",
                   "out_folder": folder + "/Ergebnis",
                   "multitrack": True, "wide_at_edges": True,
                   "camera_cut": {}, "in_point": "", "out_point": "",
                   "assignment": {}, "preset": ""}, f, indent=1)
