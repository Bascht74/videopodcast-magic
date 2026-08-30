"""Hand out a private copy of the fixture project.

Opening a project moves its file into the output folder and deletes
copies lying elsewhere. On a shared fixture that leaves the next test
nothing to open, and it fails quietly: an empty window draws as well as
a full one. So every caller gets a folder of its own, with the material
linked in and only ever read.
"""
import json, os, tempfile

NAME = "videopodcast-magic_Interview_2.json"


def fixture_project(tag="vpm"):
    """Return (project file, media folder).

    The project file is None when there is no material to point at, so
    the caller can say it is skipping rather than fail later for a
    reason that has nothing to do with what it tests.
    """
    folder = os.environ.get("VPM_MEDIA") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "media")
    source = os.path.join(folder, NAME)
    if not os.path.isdir(folder) or not os.path.exists(source):
        return None, folder
    with open(source, encoding="utf-8") as f:
        d = json.load(f)
    own = tempfile.mkdtemp(prefix="vpm_%s_" % tag)
    for entry in d.get("files") or []:
        link = os.path.join(own, os.path.basename(entry["path"]))
        if not os.path.exists(link):
            os.symlink(entry["path"], link)
        entry["path"] = link
    d["out_folder"] = os.path.join(own, "Ergebnis")
    os.makedirs(d["out_folder"], exist_ok=True)
    path = os.path.join(own, NAME)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1)
    return path, folder
