# -*- coding: utf-8 -*-
"""The program fetches no ffmpeg of its own: it finds one, or says how.

Where nothing else worked, ffmpeg used to be fetched with pip -- a
wheel carrying the two programs inside itself. It wrote into whatever
Python happened to be running, a system one included, and nobody had
been asked. The sections: the source, where no install of ffmpeg is
left to find; a search with an empty path, which has to come back
saying both are missing and try nothing on the way, and the saying of
it, which has to carry the advice for this machine; and where it looks
beside the path, which is where the package managers of each system
leave a program -- found with nothing on the path, behind whatever is
on it already, and only where a folder really is. The probe puts a
recorder in place of the two installers, so it says what the program
asked for, not what pip would have made of it.
"""
import os
import the_program
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = the_program.SCRIPT
import ast
import io
import shutil
import sys
import tempfile
import time

# Qt comes up with the program and must not want a screen; the speaker
# separation fetches a machine-learning environment and is not asked
# for here.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("VPM_NO_SPEAKER_SPLIT", "1")
vpm = the_program.load()
vpm.set_language("en")

began = time.time()
done = 0
bad = []


def check(name, ok, extra=""):
    global done
    done += 1
    print("  %-58s %s %s" % (name, "ok" if ok else "FAIL", extra))
    if not ok:
        bad.append("%s [%s]" % (name, extra or "no numbers"))


def stop():
    """Nothing further can be asked, so count what there is and go."""
    print("\n%d checks in %.2f s" % (done, time.time() - began))
    print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
    sys.exit(1 if bad else 0)


#--------------------------------------------------------- 1. The source

# Every piece of the program: a pip call that moved into the window
# would otherwise not be looked at, and this check is about there being
# none anywhere.
TREES = [(name, ast.parse(body, filename=name))
         for name, body in the_program.pieces()]

INSTALLER = "_pip_install"


def installs_in(node):
    """Every call to the pip installer under this node, with its words.

    A call is kept as (line, the words it names), so a fresh install
    can be pointed at rather than only counted. Anything that is not a
    plain string -- a variable, a computed name -- comes back as the
    source of that argument, which is what somebody would have to read
    anyway.
    """
    out = []
    for one in ast.walk(node):
        if not isinstance(one, ast.Call):
            continue
        called = one.func
        name = getattr(called, "id", None) or getattr(called, "attr", None)
        if name != INSTALLER:
            continue
        words = [a.value if isinstance(a, ast.Constant)
                 else ast.dump(a)[:40] for a in one.args]
        out.append((one.lineno, words))
    return out


SEARCH = [n for _piece, tree in TREES for n in ast.walk(tree)
          if isinstance(n, ast.FunctionDef)
          and n.name == "find_required_tools"]

print("1. The source of the search for the two programs")
check("the search for the two programs is in the file", len(SEARCH) == 1,
      "%d functions called find_required_tools, wanted 1" % len(SEARCH))
if not SEARCH:
    stop()

inside = installs_in(SEARCH[0])
check("no pip install stands in the search for the two programs",
      not inside,
      "%d calls to %s in find_required_tools, wanted 0: %s"
      % (len(inside), INSTALLER, inside[:3]))

everywhere = [one for _piece, tree in TREES
              for one in installs_in(tree)]
named = [one for one in everywhere
         if any("ffmpeg" in str(w).lower() for w in one[1])]
check("and no pip install anywhere in the program names ffmpeg",
      not named,
      "%d of %d calls to %s name it, wanted 0 of %d: %s"
      % (len(named), len(everywhere), INSTALLER, len(everywhere),
         named[:3]))


#---------------------------------------------- 2. A search with nothing

# An empty folder as the whole search path, so the search finds
# nothing and has to do whatever it does when the machine is bare.
# Both installers are replaced first: the recorder says what was asked
# for and refuses it, so this test can install nothing on the machine
# it runs on -- which is the very thing it is about.
EMPTY = tempfile.mkdtemp(prefix="vpm_nopath_")
# The search prepends the program's own folder before it gives up, so
# that folder belongs to what the probe looks in.
PROBE_PATH = EMPTY + os.pathsep + os.path.dirname(os.path.abspath(SCRIPT))

asked_pip = []


def no_install(*packages):
    asked_pip.append(packages)
    return False


def no_manager(update=False, asked=False, say=None, started=None):
    """The package manager is never really asked from a test.

    The same arguments as the real one, so a call the real one would
    take and this one would not shows up as a TypeError here rather
    than as a check that quietly stopped biting.
    """
    asked_manager.append((update, asked))
    return False


asked_manager = []


was_path = os.environ.get("PATH", "")
was_pip = vpm._pip_install
was_manager = vpm.install_over_package_manager
was_folders = vpm.manager_folders
ended, said = ("", ""), ""
try:
    vpm._pip_install = no_install
    vpm.install_over_package_manager = no_manager
    # The search looks in the folders a package manager installs into
    # as well, and on the machine running this one of them holds an
    # ffmpeg. Driven away, or the empty path would not be empty and
    # this section would measure the machine instead of the program.
    vpm.manager_folders = lambda: []
    os.environ["PATH"] = EMPTY
    ended = vpm.find_required_tools()
    # And what the run makes of it. Said with print, so it lands
    # wherever the run is showing its output; caught here to read.
    keep_out, sys.stdout = sys.stdout, io.StringIO()
    try:
        vpm.tools_repaired(*ended)
        said = sys.stdout.getvalue()
    finally:
        sys.stdout = keep_out
finally:
    os.environ["PATH"] = was_path
    vpm._pip_install = was_pip
    vpm.install_over_package_manager = was_manager
    vpm.manager_folders = was_folders
    # ignore_errors, because a folder that would not go must not end the
    # test before it has counted what it found.
    shutil.rmtree(EMPTY, ignore_errors=True)

# Out of the catalogue, so the reading does not tie itself to one
# language.
IS_MISSING = vpm.T('%s is missing.').split("%s")[-1].strip(" .")
NOTHING_RUNS = vpm.T(
    'Nothing runs until that is put right. This way: %s').split("%s")[0]

print("\n2. A search that has nothing to find")
on_hand = [tool for tool in ("ffmpeg", "ffprobe")
           if shutil.which(tool, path=PROBE_PATH) is not None]
check("the probe really looked where neither program is",
      not on_hand,
      "%d of 2 were within reach of the probe after all: %s"
      % (len(on_hand), on_hand))
check("a search that finds no ffmpeg installs nothing",
      not asked_pip,
      "%d installs asked for, wanted 0: %s"
      % (len(asked_pip), asked_pip[:3]))
check("and it comes back saying both of them are missing",
      ended[0] == "missing" and IS_MISSING in ended[1]
      and "ffmpeg" in ended[1] and "ffprobe" in ended[1],
      "it came back with %r, wanted 'missing' and both named" % (ended,))
# Nothing is said inside the search itself: at that point in the run it
# is not known whether there is a console to say it in, and a sentence
# written where nobody is looking is the same as no sentence.
check("saying it carries the advice for this machine",
      NOTHING_RUNS in said and ("ffmpeg" in said),
      "the saying was %r, wanted %r in it"
      % (" ".join(said.split())[:90], NOTHING_RUNS))
check("and it asked the package manager exactly once",
      len(asked_manager) == 1,
      "the manager was asked %d times, wanted 1: %s"
      % (len(asked_manager), asked_manager[:3]))


#------------------------- 3. Where a package manager leaves its things

# The other half of the first line: what the search does find, and
# where. Started out of the Dock or the Finder rather than a terminal,
# a program on macOS inherits /usr/bin:/bin:/usr/sbin:/sbin and no
# more, so an ffmpeg under /opt/homebrew/bin is on the disc and out of
# reach. The folders are made here and the program is told they are
# the ones a manager uses, so the judgements are about the program and
# not about what this machine happens to have installed. The empty
# path is a folder of this test's own and not /usr/bin:/bin: on a
# Linux builder /usr/bin holds an ffmpeg, and the Dock case would then
# be measured against the wrong one.
ROOM = tempfile.mkdtemp(prefix="vpm_managers_")
NO_PATH = os.path.join(ROOM, "empty")
BY_MANAGER = os.path.join(ROOM, "manager_bin")
ON_PATH = os.path.join(ROOM, "path_bin")
GONE = os.path.join(ROOM, "no_such_folder")
# Windows starts a file by its ending and nothing else, so the two
# stand-ins carry the ending the real builds carry there.
EXE = ".exe" if sys.platform == "win32" else ""


def as_compared(where):
    """A path the way this system tells two of them apart.

    shutil.which builds the ending out of PATHEXT, which is written in
    capitals on Windows, so a file laid down as ffmpeg.exe comes back as
    ffmpeg.EXE. Comparing the two letter for letter measures PATHEXT.
    """
    return os.path.normcase(where) if where else where


def lay_down(folder):
    """Put something shutil.which can find under both tool names."""
    os.makedirs(folder)
    for tool in ("ffmpeg", "ffprobe"):
        where = os.path.join(folder, tool + EXE)
        with open(where, "w") as out:
            out.write("")
        os.chmod(where, 0o755)


os.makedirs(NO_PATH)
lay_down(BY_MANAGER)
lay_down(ON_PATH)

held_folders = vpm.manager_folders
held_version = vpm.tool_version
held_path = os.environ.get("PATH", "")
dock, dock_at, dock_path, twice_path, kept_at = None, None, "", "", None
try:
    # The stand-ins answer nothing when they are run, so the version is
    # driven: what is measured here is where the two were found, and
    # reading a version off them is a different test's business.
    vpm.tool_version = lambda tool: ((9, 0, 1), "9.0.1")
    os.environ["PATH"] = NO_PATH
    vpm.manager_folders = lambda: [BY_MANAGER, GONE]
    dock = vpm.find_required_tools()
    dock_at = shutil.which("ffmpeg")
    dock_path = os.environ.get("PATH", "")
    vpm.find_required_tools()
    twice_path = os.environ.get("PATH", "")
    # And the other way round: one on the path, one where a manager
    # would have left it, and the path has to win.
    os.environ["PATH"] = ON_PATH
    vpm.manager_folders = lambda: [BY_MANAGER]
    vpm.find_required_tools()
    kept_at = shutil.which("ffmpeg")
finally:
    os.environ["PATH"] = held_path
    vpm.manager_folders = held_folders
    vpm.tool_version = held_version
    shutil.rmtree(ROOM, ignore_errors=True)


def folders_on(system):
    """What the program would look in on that system, separators flat."""
    was = vpm.sys.platform
    vpm.sys.platform = system
    try:
        return [one.replace("\\", "/") for one in vpm.manager_folders()]
    finally:
        vpm.sys.platform = was


MAC = folders_on("darwin")
LINUX = folders_on("linux")
WINDOWS = folders_on("win32")
HOME_BIN = os.path.expanduser("~/.local/bin").replace("\\", "/")
TAILS = ["chocolatey/bin", "scoop/shims", "Microsoft/WindowsApps"]
astray = [tail for tail in TAILS
          if not [one for one in WINDOWS if one.endswith(tail)]]

print("\n3. Where a package manager leaves its things")
check("a manager's ffmpeg is found with nothing on the path",
      dock == ("", "")
      and as_compared(dock_at)
      == as_compared(os.path.join(BY_MANAGER, "ffmpeg" + EXE)),
      "the search came back %r and found ffmpeg at %r, wanted no "
      "complaint and the one under %r -- this is the program started "
      "from the Dock" % (dock, dock_at, BY_MANAGER))
check("a folder that is not on the disc stays out of the path",
      GONE not in dock_path.split(os.pathsep),
      "the path came back %r, and %r is no folder on this machine"
      % (dock_path[-70:], GONE))
check("the path does not grow when the search runs twice",
      twice_path.split(os.pathsep).count(BY_MANAGER) == 1,
      "%r stands %d times in the path after two searches, wanted once"
      % (BY_MANAGER, twice_path.split(os.pathsep).count(BY_MANAGER)))
check("an ffmpeg already on the path is the one that answers",
      as_compared(kept_at)
      == as_compared(os.path.join(ON_PATH, "ffmpeg" + EXE)),
      "it answered with %r, wanted the one under %r -- what a manager "
      "left goes behind the path, never in front of it"
      % (kept_at, ON_PATH))
check("a Mac is looked in where Homebrew and MacPorts install",
      set(["/opt/homebrew/bin", "/usr/local/bin",
           "/opt/local/bin"]) <= set(MAC),
      "it looks in %r -- Homebrew is /opt/homebrew/bin on Apple "
      "silicon and /usr/local/bin on Intel, MacPorts /opt/local/bin"
      % (MAC,))
check("a Linux machine is looked in where its own managers install",
      "/snap/bin" in LINUX and HOME_BIN in LINUX
      and "/opt/homebrew/bin" not in LINUX,
      "it looks in %r, wanted /snap/bin and %r among them and no "
      "folder belonging to another system" % (LINUX, HOME_BIN))
check("Windows is looked in where Chocolatey, Scoop and winget put it",
      not astray,
      "%d of %d wanted endings are missing: %s -- it looks in %r"
      % (len(astray), len(TAILS), astray, WINDOWS))

print("\n%d checks in %.2f s" % (done, time.time() - began))
print("FAIL: " + " | ".join(bad) if bad else "ALL OK")
sys.exit(1 if bad else 0)
