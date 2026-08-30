"""Hand out a private copy of the fixture project.

Opening a project does two things to its surroundings: it moves the
project file into the output folder, and it deletes copies of it lying
anywhere else. Both are right for a real job and fatal for a shared
fixture -- the second test then finds nothing to open, and finds it
quietly, because an empty window draws just as well as a full one.

So the project file and the output folder are private to each caller.
The material itself is only ever read and stays where it is.

The links to that material are the other way round: they lie in one
folder that every caller and every run shares. The program keeps what
ffprobe said about a file on disc, and it files that answer under the
path it was asked about. A folder with a fresh random name each time
means every file looks new to it at every start, so nothing kept is
ever found again -- measured on 30.8.2026: forty different paths for
ten real files in one run of interface_test.py, and not one of the
kept answers used. With one folder for the links, the same run over
material already measured starts 12 processes instead of 205, and not
one of them is an ffprobe.

Sharing only the links leaves the trap where it was: what a project
tidies up is the folder its own file lies in, and that one is still
private to the caller.
"""
import hashlib, json, os, tempfile

NAME = "videopodcast-magic_Interview_2.json"


def link_folder(folder):
    """The shared folder of links into *folder*, made if it is not there.

    Named after the material it points at, so two different sets of
    fixtures do not land in the same place. It lies where Python puts
    its temporary things, which run.sh points at one folder per suite
    run and removes afterwards: within a run everything shares the
    links, and nothing is left behind.
    """
    mark = hashlib.sha1(os.path.abspath(folder).encode("utf-8")).hexdigest()
    who = os.getuid() if hasattr(os, "getuid") else 0
    own = os.path.join(tempfile.gettempdir(),
                       "vpm_links_%s_%s" % (who, mark[:12]))
    os.makedirs(own, exist_ok=True)
    return own


def point_at(link, target):
    """Make *link* point at *target*, whoever else is doing the same.

    Several tests run side by side and want the same links. Making one
    is a single step for the file system, so the loser of a race gets
    an error rather than half a link, and a link that already points
    the right way is simply left alone. Nothing here removes anything:
    a link another test is reading through must survive.
    """
    try:
        if os.readlink(link) == target:
            return
    except OSError:
        pass
    try:
        os.symlink(target, link)
        return
    except FileExistsError:
        pass
    # Something else stands there -- a link left over from material that
    # has since moved. Build the right one beside it and let it take the
    # name in one step, so nobody ever sees the name empty.
    beside = "%s.%d" % (link, os.getpid())
    try:
        os.symlink(target, beside)
        os.replace(beside, link)
    except OSError:
        try:
            os.unlink(beside)
        except OSError:
            pass


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
    shared = link_folder(folder)
    for entry in d.get("files") or []:
        link = os.path.join(shared, os.path.basename(entry["path"]))
        point_at(link, entry["path"])
        entry["path"] = link
    d["out_folder"] = os.path.join(own, "Ergebnis")
    os.makedirs(d["out_folder"], exist_ok=True)
    path = os.path.join(own, NAME)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1)
    return path, folder
