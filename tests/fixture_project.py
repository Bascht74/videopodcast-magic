"""Hand out a private copy of the fixture project.

Opening a project does two things to its surroundings: it moves the
project file into the output folder, and it deletes copies of it lying
anywhere else. Both are right for a real job and fatal for a shared
fixture -- the second test then finds nothing to open, and finds it
quietly, because an empty window draws just as well as a full one.

So every caller gets a folder of its own: the material linked in, a
project file pointing at those links, and an output folder beside it.
The material itself is only ever read and stays where it is.
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
