"""Write the project file for the interview fixture.

A run moves the project file into the output folder. Written afresh
before every suite, so the fixture still has one to open -- and in one
step, under a name of its own first and then moved over the old one, so
a suite already reading the fixture never opens half a file.
"""
import glob, json, os, sys, tempfile
sys.path.insert(0, os.path.dirname(
    os.path.abspath(__file__)))
from fixture_root import fixture

folder = sys.argv[1] if len(sys.argv) > 1 else fixture("interview")
if os.path.isdir(folder):
    files = [{"path": p, "kind": "audio"}
             for p in sorted(glob.glob(folder + "/*.wav"))]
    files += [{"path": p, "kind": "video"}
              for p in sorted(glob.glob(folder + "/*.mov"))]
    fd, part = tempfile.mkstemp(prefix=".interview_project_", suffix=".part",
                                dir=folder)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump({"format": 3, "version": "fixture", "files": files,
                       "timeline": [], "timeline_absolute": False,
                       "production": "Interview 2",
                       "out_folder": folder + "/Ergebnis",
                       "multitrack": True, "wide_at_edges": True,
                       "camera_cut": {}, "in_point": "", "out_point": "",
                       "assignment": {}, "preset": ""}, f, indent=1)
        # mkstemp makes it for its owner alone; open() made it 644.
        os.chmod(part, 0o644)
        os.replace(part, folder + "/videopodcast-magic_Interview_2.json")
    finally:
        if os.path.exists(part):
            os.remove(part)
