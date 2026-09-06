# -*- coding: utf-8 -*-
"""Getting the tools in place, before the first sound is touched.

A piece of the program, read out of the folder beside it by beside().
It cannot import the file it was cut out of, because that file is
still being read while this one is; the program is handed in instead,
and every name this piece uses out of it is bound below, by name. The
credential store stands under the same heading: without the key there
is nothing to send a production to.
"""

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

# What the program has and this piece uses, bound once so that the
# setting up reads as it did in the one file. Two names are missing,
# and the two blocks under the list say which and why.

FFMPEG_FLOOR = PROGRAM.FFMPEG_FLOOR
INSTALL_TOOLS = PROGRAM.INSTALL_TOOLS
T = PROGRAM.T
ctypes = PROGRAM.ctypes
group_text = PROGRAM.group_text
json = PROGRAM.json
os = PROGRAM.os
platform = PROGRAM.platform
re = PROGRAM.re
shutil = PROGRAM.shutil
subprocess = PROGRAM.subprocess
sys = PROGRAM.sys
tempfile = PROGRAM.tempfile
threading = PROGRAM.threading
time = PROGRAM.time

# as_warn stands further down the file this was cut out of, and a copy
# taken up here would be an AttributeError while that file is still
# being read. It is reached through PROGRAM where it is used.

# __file__ is the other one, and it is the reason this piece has a
# rule of its own: a build laid beside the program lies beside the
# program, not beside this folder, so the place is asked of
# PROGRAM.__file__ and never of the name this file carries.


def version_text(numbers):
    """A version as people write it."""
    return ".".join(str(x) for x in numbers)


def version_from_line(line):
    """Read a version off the first line an ffmpeg-family tool prints.

    Every build writes it the same way -- "ffmpeg version 9.0.1
    Copyright ..." -- and what follows the number differs from build to
    build, which does not matter. One out of git carries a commit where
    the number should be, and then no numbers come back: a version that
    cannot be read is not one above the floor. The word the build calls
    itself comes back beside them, to be quoted rather than a number.
    """
    line = (line or "").strip()
    said = (line.split(" version ", 1)[-1].split(" ")[0][:40]
            if " version " in line else "")
    hit = re.match(r"^\S+ version n?(\d+)\.(\d+)(?:\.(\d+))?", line)
    if not hit:
        return None, said
    return tuple(int(x or 0) for x in hit.groups()), said


def tool_version(command):
    """Ask an ffmpeg-family tool what version it is."""
    try:
        p = subprocess.run([command, "-version"], capture_output=True,
                           timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None, ""
    return version_from_line(
        (p.stdout or b"").decode("utf-8", "replace").split("\n")[0])


def tools_below_floor():
    """Which of the two tools is under the floor, and what it answered.

    Both are asked and not only one: they are found by name, so with one
    of them lying beside the script and the other in the search path
    they can be different builds -- and then the message has to say
    which of the two is the old one.
    """
    out = []
    for tool in ("ffmpeg", "ffprobe"):
        numbers, said = tool_version(tool)
        if numbers is None or numbers < FFMPEG_FLOOR:
            out.append((tool, said or T('no answer')))
    return out


_SOXR = None


def _have_soxr():
    """Report whether this ffmpeg was built with soxr."""
    try:
        p = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                            "anullsrc=r=48000:cl=mono", "-t", "0.05", "-af",
                            "aresample=resampler=soxr:osr=48001",
                            "-f", "null", "-"], capture_output=True)
        return p.returncode == 0
    except Exception:
        return False


def soxr_available():
    """Whether this ffmpeg can resample with soxr, asked once.

    One caller, the filter chain, and it asks per track -- so the
    answer is kept rather than measured again. The measurement costs
    23 ms.
    """
    global _SOXR
    if _SOXR is None:
        _SOXR = _have_soxr()
    return _SOXR


def forget_soxr():
    """Measure soxr again the next time it is asked for.

    An install puts another ffmpeg in place, and the answer kept from
    before it is then a statement about the build that is gone. Every
    place that installs one forgets this, so that what is reported
    afterwards is what really arrived.
    """
    global _SOXR
    _SOXR = None


def tools_folder(make=False):
    """Where a build this program fetched itself lives, or None.

    Not the cache: that is the one folder everybody is told may be
    deleted, and deleting it must not take ffmpeg with it. Not beside
    the program either -- an installed copy sits in site-packages,
    which pip owns and writes over. VPM_TOOLS points it somewhere
    else; a test run has no place here at all.
    """
    base = os.environ.get("VPM_TOOLS") or ""
    if not base:
        if os.environ.get("VPM_SILENT"):
            # A test run fetches nothing and keeps nothing, so it has
            # no folder to keep it in either. The same rule the
            # settings store is under, and for the same reason.
            return None
        if sys.platform == "darwin":
            base = os.path.expanduser("~/Library/Application Support")
        elif os.name == "nt":
            # LOCALAPPDATA and not APPDATA: a fetched ffmpeg is
            # bigger than a roaming profile has any business
            # carrying from machine to machine.
            base = (os.environ.get("LOCALAPPDATA")
                    or os.path.expanduser("~"))
        else:
            base = (os.environ.get("XDG_DATA_HOME")
                    or os.path.expanduser("~/.local/share"))
    folder = os.path.join(base, "videopodcast-magic", "tools")
    if not make:
        return folder
    try:
        os.makedirs(folder, exist_ok=True)
    except OSError:
        return None
    return folder


def certificate_file():
    """Return the bundle HTTPS connections are verified against.

    A Python installed from python.org brings no certificates of its
    own, and every download then fails with CERTIFICATE_VERIFY_FAILED.
    certifi is the bundle; it is already on disc wherever pip has run
    once, and it is installed if it is not.
    """
    import importlib
    certifi = _really_there("certifi")
    if certifi is None:
        if not _pip_install("certifi"):
            return None
        importlib.invalidate_caches()
        certifi = _really_there("certifi")
        if certifi is None:
            return None
    try:
        where = certifi.where()
    except Exception:
        return None
    return where if os.path.exists(where) else None


def https_context():
    """An SSL context that can verify, not the default one.

    The default context trusts whatever this Python was handed on
    the way in, and this one was handed nothing.
    """
    import ssl
    bundle = certificate_file()
    if not bundle:
        print(T('  No certificate bundle found -- an HTTPS download '
                'may fail.'))
        return ssl.create_default_context()
    return ssl.create_default_context(cafile=bundle)


def manager_folders():
    """Where a package manager on this system usually leaves a program.

    Started from the Dock or the Finder rather than from a terminal, a
    program inherits almost no search path, so an ffmpeg a manager
    installed is out of reach although it is on the disc. Whether these
    are really there is not asked here; the caller drops the rest.
    """
    if sys.platform == "darwin":
        # Homebrew on Apple silicon, Homebrew on Intel, MacPorts.
        return ["/opt/homebrew/bin", "/usr/local/bin", "/opt/local/bin"]
    if sys.platform == "win32":
        # Chocolatey, Scoop, winget -- none of the three is on the
        # path of a program somebody double-clicked.
        home = os.path.expanduser("~")
        data = os.environ.get("ProgramData") or "C:\\ProgramData"
        local = os.environ.get("LOCALAPPDATA") or home
        return [os.path.join(data, "chocolatey", "bin"),
                os.path.join(home, "scoop", "shims"),
                os.path.join(local, "Microsoft", "WindowsApps")]
    # A build installed by hand, snap, and what pip and pipx write for
    # one user. Homebrew on Apple silicon has no business here.
    return ["/usr/local/bin", "/snap/bin",
            os.path.expanduser("~/.local/bin")]


def find_required_tools():
    """Locate ffmpeg and ffprobe, and check they are new enough.

    soxr is no part of it: a build without soxr takes the clock drift
    out a hundred times more coarsely, and coarser is not broken --
    rate_filter_chain says so once where it matters. Returns ("", "")
    where all is well, else which of "missing" and "old" it is and the
    sentence for it. Nothing is printed here: whether a console or the
    window will show it is not yet known.
    """
    # Beside the program and not beside this piece: the two are
    # different folders, and what somebody laid next to the
    # program lies in the first of them.
    here = os.path.dirname(os.path.abspath(PROGRAM.__file__))
    # A build this program fetched goes in front of the search path,
    # not behind it. Behind it, a distribution's ffmpeg 6.1.1 would
    # keep answering and the fetched 9.0.1 would never be reached.
    # Nothing lies in that folder that this program did not put there.
    ours = tools_folder()
    was = os.environ.get("PATH", "")
    if ours and shutil.which("ffmpeg", path=ours) \
            and ours not in was.split(os.pathsep):
        os.environ["PATH"] = ours + os.pathsep + was
    # Behind the search path and never in front of it: whoever has an
    # ffmpeg on the path keeps that one. Only folders that are there
    # go in, or the path grows by three at every start.
    path = os.environ.get("PATH", "")
    known = path.split(os.pathsep)
    # A test that has to act as though no ffmpeg lay anywhere sets
    # VPM_NO_MANAGER_PATH: an empty search path is no longer empty on a
    # machine where a manager has installed one. Nothing else reads it,
    # and the program never sets it itself.
    look_in = [] if os.environ.get("VPM_NO_MANAGER_PATH") \
        else manager_folders()
    more = [one for one in look_in
            if one not in known and os.path.isdir(one)]
    if more:
        os.environ["PATH"] = os.pathsep.join(
            ([path] if path else []) + more)
    missing = [tool for tool in ("ffmpeg", "ffprobe") if shutil.which(tool) is None]
    if missing and os.path.isdir(here):
        os.environ["PATH"] = here + os.pathsep + os.environ.get("PATH", "")
        missing = [tool for tool in missing if shutil.which(tool) is None]
    if missing:
        return "missing", T('%s is missing.') % ", ".join(missing)
    old = tools_below_floor()
    if old:
        return "old", T('Here: %s. Needed: %s or newer.') % (
            ", ".join("%s %s" % (tool, says) for tool, says in old),
            version_text(FFMPEG_FLOOR))
    return "", ""



def tools_repaired(kind, says, asked=False):
    """Say what is wrong with ffmpeg, offer the repair, report what is left.

    True where the tools are good afterwards. Everything is said with
    print, so it lands wherever this run shows its output -- the console
    where somebody typed a command line, the log where nobody is
    sitting. *asked* says the question has already been put somewhere
    else, so it is not put a second time.
    """
    print(PROGRAM.as_warn(says))
    if install_ffmpeg(update=kind != "missing", asked=asked):
        # Asked again, not taken on trust: a package manager can report
        # success having just laid down an ffmpeg that is still too old
        # for this.
        forget_soxr()
        kind, says = find_required_tools()
        if not kind:
            print(T('That worked.'))
            print("  " + soxr_note())
            return True
        print(PROGRAM.as_warn(says))
    print(T('Nothing runs until that is put right. This way: %s')
          % how_to_get_ffmpeg(kind != "missing"))
    return False


# What each manager needs so that it does not ask a second time: the
# question was already asked here, in this program's own wording.
QUIET_MANAGER = {
    # Homebrew reads NONINTERACTIVE the way its own installer does. Its
    # update is deliberately left on: it costs minutes, but without it
    # the install runs off a stale formula index and fails on a
    # dependency that has since moved.
    "brew": {"NONINTERACTIVE": "1", "HOMEBREW_NO_ENV_HINTS": "1"},
    # Without this apt opens full-screen dialogs of its own.
    "apt-get": {"DEBIAN_FRONTEND": "noninteractive"},
}


# Measured 4.9.2026: homebrew/core builds ffmpeg without soxr in every
# version there is, and only this tap has libsoxr, by name. It has no
# bottle, so the button compiles: two to three minutes, and the price
# of the fine clock correction where nothing can be fetched instead.
BREW_FFMPEG = ("homebrew-ffmpeg/ffmpeg/ffmpeg", "--with-libsoxr")


def brew_ffmpeg_from_elsewhere():
    """True where a brew ffmpeg from another tap is standing in the way.

    Measured 4.9.2026: with homebrew/core's ffmpeg installed, brew
    refuses the tap outright and names uninstalling as the way. So it
    is asked rather than guessed, out of the keg's own receipt -- a
    file answers at once and brew takes seconds.
    """
    brew = shutil.which("brew")
    if not brew:
        return False
    cellar = os.path.join(os.path.dirname(os.path.dirname(brew)),
                          "Cellar", "ffmpeg")
    try:
        kegs = sorted(os.listdir(cellar))
    except OSError:
        return False
    for keg in kegs:
        try:
            with open(os.path.join(cellar, keg, "INSTALL_RECEIPT.json"),
                      "rb") as f:
                came = json.loads(f.read().decode("utf-8"))
        except (OSError, ValueError, UnicodeDecodeError):
            # A keg whose receipt cannot be read is still a keg in the
            # way, and brew will say so. Better to make room for
            # nothing than to run a command that cannot work.
            return True
        if (came.get("source") or {}).get("tap") != "homebrew-ffmpeg/ffmpeg":
            return True
    return False


def package_manager_command(update=False):
    """How this system installs ffmpeg, or () where none of them is here.

    The first manager found, each with the switch that stops it asking
    again, on Linux with sudo unless the run is root already. *update*
    asks for the other command, for tools that are there and wrong:
    told to install what is already there a manager answers "already
    installed" and does nothing, and building it again is what puts a
    missing option in.
    """
    if sys.platform == "darwin":
        if shutil.which("brew"):
            # --yes is brew's own, and NONINTERACTIVE no longer
            # covers the confirmation. Building again is only that
            # where the tap's own build is installed: anything else
            # is taken out of the way, and then there is nothing left.
            if update and not brew_ffmpeg_from_elsewhere():
                return ("brew", "reinstall", "--yes") + BREW_FFMPEG
            return ("brew", "install", "--yes") + BREW_FFMPEG
        return ()
    if sys.platform == "win32":
        # No manager here. What Windows gets instead is a built ffmpeg
        # fetched by install_ffmpeg, which is the door both roads go
        # through.
        return ()
    for tool, rest, lift in (
            ("apt-get", ("install", "-y", "ffmpeg"),
             ("install", "--only-upgrade", "-y", "ffmpeg")),
            ("dnf", ("install", "-y", "ffmpeg"),
             ("upgrade", "-y", "ffmpeg")),
            ("zypper", ("--non-interactive", "install", "ffmpeg"),
             ("--non-interactive", "update", "ffmpeg")),
            # pacman's -S is both, so there is nothing else to say.
            ("pacman", ("-S", "--noconfirm", "ffmpeg"),
             ("-S", "--noconfirm", "ffmpeg"))):
        if shutil.which(tool):
            whole = (tool,) + (lift if update else rest)
            if hasattr(os, "geteuid") and os.geteuid() == 0:
                return whole
            return ("sudo",) + whole if shutil.which("sudo") else whole
    return ()


def manager_environment(command):
    """The environment that manager runs in, quietened.

    The key never travels into it, the same rule pip is handed.
    """
    clean = dict(os.environ)
    clean.pop("AUPHONIC_TOKEN", None)
    for part in command:
        clean.update(QUIET_MANAGER.get(part, {}))
    return clean


# What a package manager says just before it goes quiet: "==> " and
# the command it is about to run. brew then writes that command's own
# output into a log file and prints nothing at all until it is over --
# read out of Homebrew 6.0.21, Formula#system.
BUILD_TOOLS = ("configure", "make", "gmake", "cmake", "meson", "ninja",
               "cargo", "autoreconf", "bootstrap")


def build_begins(line):
    """True where this line is a package manager starting to compile.

    The one line worth hanging a sentence on, because the silence
    starts under it. Fetching and pouring look much the same and are
    over in seconds, so only the build commands count.
    """
    words = line.strip().split()
    if len(words) < 2 or words[0] != "==>":
        return False
    return os.path.basename(words[1]) in BUILD_TOOLS


def sign_of_life(line, mark, every=5.0):
    """Keep the pane moving while the package manager says nothing.

    Measured on the build logs of one ffmpeg: 36 and 34 seconds
    without a single line on a fast Mac, and an older machine takes a
    multiple of that. So the movement comes from here -- a dot every
    few seconds -- while the sentence that says what is happening
    hangs on the manager's own first build line. Hands back the sink
    to give the manager, and the way to stop the dots.
    """
    seen = [time.time()]
    dotted = [False]
    told = [False]
    over = threading.Event()

    def close():
        """End the row of dots, so the next real line starts its own."""
        if dotted[0]:
            dotted[0] = False
            mark("\n")

    def watched(text):
        close()
        seen[0] = time.time()
        line(text)
        if not told[0] and build_begins(text):
            told[0] = True
            line(T('Now it is being compiled, and that is the long '
                   'part: minutes on a fast machine and a good deal '
                   'longer on an older one. Nothing is stuck -- a dot '
                   'appears every few seconds for as long as it '
                   'works.'))

    def turn():
        beat = min(0.5, every / 2.0)
        while not over.wait(beat):
            if time.time() - seen[0] >= every:
                seen[0] = time.time()
                dotted[0] = True
                mark(".")
        close()

    wheel = threading.Thread(target=turn, daemon=True)
    wheel.start()

    def stop():
        over.set()
        wheel.join(3.0)

    return watched, stop


def run_watched(command, env=None, say=None, started=None):
    """Run a command and hand out what it says while it says it.

    A package manager's own output is the only sign that anything is
    happening, so stderr is folded into stdout and each line goes out
    as it arrives -- newline and all, because the window's pane breaks
    its blocks on those. *started* is handed the process, so whoever
    asked can reach it. Returns the exit code, or None where the
    command could not be started at all.
    """
    # Nothing is piped where nobody is listening, and that is not
    # laziness: a pipe would also take sudo's password prompt, which
    # carries no newline and would sit unseen in a buffer while the
    # terminal waits for a password nobody has been asked for.
    piped = ({"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT,
              "bufsize": 1, "universal_newlines": True,
              "errors": "replace"} if say else {})
    try:
        child = subprocess.Popen(list(command), env=env, **piped)
    except OSError as e:
        (say or print)(T('  That did not work: %s') % e)
        return None
    if started:
        started(child)
    if say:
        try:
            for line in child.stdout:
                say(line)
            child.stdout.close()
        except Exception as e:
            # A pipe that breaks mid-command is worth a line: silence
            # here reads as a command that said nothing. The handle is
            # left to be collected -- closing it is what just failed.
            say(T('  That did not work: %s') % e)
    return child.wait()


def install_over_package_manager(update=False, asked=False, say=None,
                                 started=None):
    """Offer the package manager, and run it if that is wanted.

    True when ffmpeg was installed. Asked only where somebody can
    answer: a window started from the desktop has no console, and a
    question nobody sees would hang the start for good. *asked* says
    it was already put in the window. *say* takes every line, the
    program's own and the manager's; without one they go to print,
    which is where a command line shows its output.
    """
    tell = (lambda text: say(text + "\n")) if say else print
    if os.environ.get("VPM_SILENT"):
        # A test run installs nothing and asks nobody. Before the
        # platforms, because the Windows branch asks a question too.
        return False
    command = package_manager_command(update)
    if not command:
        # Windows has no manager, and a Mac without brew has none
        # either. install_ffmpeg goes on from here.
        return False
    printed = " ".join(command)
    if INSTALL_TOOLS or asked:
        # VPM_INSTALL_TOOLS: whoever set it has answered in advance.
        # For a test, a build machine, anything with nobody in front
        # of it -- and it still says what it is doing.
        tell(T('  Installing it: %s') % printed)
    elif not sys.stdin.isatty():
        tell(T('  On this machine: %s') % printed)
        return False
    else:
        tell(T('  This machine can install it properly: %s') % printed)
        answer = input(T('  Run that now? [Y/n] ')).strip().lower()
        if answer and not answer.startswith(("y", "j")):
            return False
    if command[0] == "brew" and brew_ffmpeg_from_elsewhere():
        # Room first, or brew refuses the tap outright. Said out loud,
        # because for a moment afterwards this machine has no ffmpeg at
        # all and somebody reading the pane should know why.
        room = ("brew", "uninstall", "--ignore-dependencies", "ffmpeg")
        tell(T('  Taking the ffmpeg that is there out of the way first: '
               '%s') % " ".join(room))
        run_watched(room, manager_environment(room), say, started)
    return run_watched(command, manager_environment(command),
                       say, started) == 0


def open_page(url):
    """Hand an address to whatever the system opens addresses with.

    Every desktop has its own way and none of them is Python's: the
    Windows shell, the open command on a Mac, xdg-open elsewhere.
    """
    try:
        if os.name == "nt":
            os.startfile(url)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", url])
        else:
            subprocess.Popen(["xdg-open", url])
        return True
    except Exception as e:
        # Silence would leave somebody waiting for a page that is not
        # coming, so the address goes out to be opened by hand.
        print(T('  The page could not be opened: %s') % e)
        print("  %s" % url)
        return False


def open_ffmpeg_page():
    """Offer to open ffmpeg.org. The last way out where nothing else works.

    Always False: a download in a browser is not finished when this
    returns, so the run cannot go on as though ffmpeg were there.
    """
    if INSTALL_TOOLS or not sys.stdin.isatty():
        return False
    print(T('  ffmpeg.org has builds for Windows. The folder with '
            'ffmpeg.exe then has to go into PATH, or the files next to '
            'this program.'))
    answer = input(T('  Open the page? [Y/n] ')).strip().lower()
    if answer and not answer.startswith(("y", "j")):
        return False
    open_page("https://ffmpeg.org/download.html")
    return False


# Where a built ffmpeg comes from for the two systems that compile
# none. Measured 4.9.2026 by fetching both archives and reading the
# configure line out of the binary: win64 and linux64 are both
# n9.0.1-11-ge47273f4d9, both carry --enable-libsoxr, 121 and 161 MB.

# "latest" is a moving tag on the 9.0 line, so what arrived is asked
# afterwards rather than promised here, and no size goes into a text.
# Every archive is named the same way: the line, the machine, the
# licence, the line again, the kind of archive.
FFMPEG_BUILD_PLACE = ("https://github.com/BtbN/FFmpeg-Builds/releases"
                      "/download/latest/ffmpeg-n9.0-latest-%s-gpl-9.0.%s")


def ffmpeg_build_url():
    """Where the built ffmpeg for this machine is, or "".

    macOS gets none on purpose. There is no native arm64 build to
    fetch, and this program does not run under Rosetta -- so a Mac
    compiles its own out of the tap, which is what BREW_FFMPEG is for.
    A 32-bit machine gets none either: there is no build for one, and
    a name that answers nothing is worse than no name.
    """
    arch = platform.machine().lower()
    arm = arch.startswith("arm") or arch == "aarch64"
    if "64" not in arch:
        return ""
    if sys.platform.startswith("linux"):
        return FFMPEG_BUILD_PLACE % ("linuxarm64" if arm else "linux64",
                                     "tar.xz")
    if sys.platform == "win32":
        return FFMPEG_BUILD_PLACE % ("winarm64" if arm else "win64", "zip")
    return ""


def ffmpeg_can_be_had():
    """True where this machine has a way of getting ffmpeg at all.

    A package manager, or a built one to fetch. Where neither answers
    there is no button to press, only a sentence saying where to look.
    """
    return bool(package_manager_command() or ffmpeg_build_url())


def fetch_archive(url, where, say=None):
    """Fetch that address into that file. "" when it arrived.

    The one place in this road that opens a connection, so a test
    replaces this one function and then measures what the program does
    with the answer instead of the weather.
    """
    import urllib.request
    said = 0
    try:
        with urllib.request.urlopen(url, context=https_context(),
                                    timeout=120) as answer:
            whole = int(answer.headers.get("Content-Length") or 0)
            with open(where, "wb") as out:
                while True:
                    block = answer.read(1 << 20)
                    if not block:
                        break
                    out.write(block)
                    # Every ten of them, not every block: the pane
                    # breaks its blocks on newlines, and a line per
                    # block would be a hundred and fifty of them.
                    if say and out.tell() - said >= 10 << 20:
                        said = out.tell()
                        say(T('  %s of %s MB')
                            % (group_text(said >> 20),
                               group_text(whole >> 20)) + "\n")
    except Exception as e:
        return T('The build could not be fetched: %s') % e
    return ""


def unpack_tools(archive, folder):
    """Take ffmpeg and ffprobe out of that archive into that folder.

    Only those two, by their bare name, and only regular files: an
    archive is a list of paths somebody else wrote, and nothing in it
    decides where anything lands here. Returns how many arrived.
    """
    wanted = ("ffmpeg", "ffprobe", "ffmpeg.exe", "ffprobe.exe")
    done = 0

    def put(name, stream):
        where = os.path.join(folder, os.path.basename(name))
        with open(where, "wb") as out:
            shutil.copyfileobj(stream, out)
        os.chmod(where, 0o755)

    if archive.endswith(".zip"):
        import zipfile
        with zipfile.ZipFile(archive) as zf:
            for one in zf.infolist():
                if not one.is_dir() \
                        and os.path.basename(one.filename) in wanted:
                    with zf.open(one) as stream:
                        put(one.filename, stream)
                    done += 1
        return done
    import tarfile
    with tarfile.open(archive) as tf:
        for one in tf:
            if one.isfile() and os.path.basename(one.name) in wanted:
                stream = tf.extractfile(one)
                if stream is not None:
                    put(one.name, stream)
                    done += 1
    return done


def fetch_ffmpeg_build(asked=False, say=None):
    """Fetch a built ffmpeg into this program's own folder. True if it came.

    Windows and Linux go this way: Windows has no package manager to
    ask, and what a distribution's manager holds is under the floor --
    Ubuntu 24.04 carries 6.1.1. macOS never comes here; it builds its
    own out of the tap.
    """
    tell = (lambda text: say(text + "\n")) if say else print
    if os.environ.get("VPM_SILENT"):
        # A test run fetches nothing. First line, before the address is
        # so much as built: no test of this program goes to the network.
        return False
    url = ffmpeg_build_url()
    folder = tools_folder(make=True)
    if not url or not folder:
        return open_ffmpeg_page() if sys.platform == "win32" else False
    name = url.rsplit("/", 1)[-1]
    if not (INSTALL_TOOLS or asked):
        if not sys.stdin.isatty():
            tell(T('  On this machine: %s') % url)
            return False
        tell(T('  A built ffmpeg 9.0.1 with soxr can be fetched: %s') % url)
        answer = input(T('  Fetch it now? [Y/n] ')).strip().lower()
        if answer and not answer.startswith(("y", "j")):
            return False
    tell(T('  Fetching a built ffmpeg. It is a big one, so this takes '
           'a few minutes: %s') % url)
    keep = tempfile.mkdtemp(prefix="vpm_ffmpeg_")
    archive = os.path.join(keep, name)
    try:
        trouble = fetch_archive(url, archive, say)
        if trouble:
            tell("  " + trouble)
            return open_ffmpeg_page() if sys.platform == "win32" else False
        try:
            came = unpack_tools(archive, folder)
        except Exception as e:
            tell(T('  The build could not be unpacked: %s') % e)
            return False
    finally:
        shutil.rmtree(keep, ignore_errors=True)
    if came < 2:
        tell(T('  The archive held %s of the two programs.')
             % group_text(came))
        return False
    # In front of the search path, so the fetched one answers rather
    # than whatever the system had. find_required_tools does the same
    # on the next start; this makes it true within this run as well.
    if folder not in os.environ.get("PATH", "").split(os.pathsep):
        os.environ["PATH"] = folder + os.pathsep + os.environ.get("PATH", "")
    forget_soxr()
    tell(T('  It is here: %s') % folder)
    return True


def install_ffmpeg(update=False, asked=False, say=None, started=None):
    """Get an ffmpeg, whichever way this machine has. True when it came.

    The one door, and the order in it is the point. The package
    manager first, because on some systems it is already right and it
    is the tidier answer where it is. Then the tools are asked again --
    a manager can report success having laid down 6.1.1 -- and only
    where that is still not enough is a built one fetched.
    """
    if install_over_package_manager(update=update, asked=asked,
                                   say=say, started=started):
        forget_soxr()
        if not find_required_tools()[0]:
            return True
    return fetch_ffmpeg_build(asked=asked, say=say)


def how_to_get_ffmpeg(update=False):
    """The advice for the machine in hand, in one sentence.

    One place, three readers -- the console, the box on the window and
    the job behind its button -- so none of the three can say something
    the other two do not.
    """
    command = " ".join(package_manager_command(update))
    if command:
        return command
    url = ffmpeg_build_url()
    if url:
        return url
    if sys.platform == "darwin":
        return T('install Homebrew from brew.sh, then this again')
    if sys.platform == "win32":
        return T('from ffmpeg.org, and the folder into PATH')
    return T('over the package manager: apt install ffmpeg, '
             'dnf install ffmpeg')


def soxr_note():
    """What this ffmpeg does to the clock drift, in one sentence.

    Said, never demanded. Without soxr the drift between two cameras
    comes out in steps of 21 ppm instead of 0.21 -- a hundred times
    coarser, and coarser is not broken.
    """
    if soxr_available():
        return T('This ffmpeg has soxr: the clock drift between cameras '
                 'comes out in steps of 0.21 ppm.')
    return T('This ffmpeg has no soxr: the clock drift between cameras '
             'comes out in steps of 21 ppm instead of 0.21.')


# The API key lives in the OS credential store -- macOS keychain, Windows
# registry under HKEY_CURRENT_USER -- both owned by the logged-in user.
# Never in a file: the script gets copied around, and a plaintext key would
# travel with it. All three names of the place stand here, and only here.
KEY_STORE_REAL = ("videopodcast-magic", "auphonic",
                  r"Software\videopodcast-magic")
KEY_SERVICE, KEY_ACCOUNT, REG_PATH = KEY_STORE_REAL


def key_store_off_limits():
    """True where this run may not go near the credential store at all.

    A test run marks itself with VPM_SILENT, and a test with business
    in the store points KEY_SERVICE, KEY_ACCOUNT or REG_PATH at a
    throwaway name first. One that forgets would overwrite the key
    this machine really uses, so the store refuses rather than every
    test file having to remember. Reading is refused with writing: a
    test that reads the key prints it in a failure line.
    """
    if not os.environ.get("VPM_SILENT"):
        return False
    return (KEY_SERVICE, KEY_ACCOUNT, REG_PATH) == KEY_STORE_REAL


def store_api_key(key):
    """Store the API key in the OS credential store. True on success.

    On a Mac the key goes to "security" over its input, never as an
    argument that would stand in the process list. "security" needs a
    session of its own -- it prompts on /dev/tty -- and the word is sent
    twice, because it asks once and once to confirm.
    """
    forget_api_key()   # or the old one would still answer
    if key_store_off_limits():
        return False
    # Looked at first: a locked keychain leaves "security" standing for
    # its whole limit, and twenty seconds of a frozen window say less
    # than a sentence naming the lock.
    if key_store_locked():
        return False
    # A pasted key carries blanks and a newline more often than not, and
    # it goes down the pipe as a line -- so it is made one before it
    # goes. The store takes the edges off on the way back regardless.
    key = key.strip()
    if sys.platform == "darwin":
        where = ["-s", KEY_SERVICE, "-a", KEY_ACCOUNT]
        try:
            p = subprocess.run(["security", "add-generic-password", "-U"]
                               + where + ["-w"],
                               input=(key + "\n" + key + "\n").encode("utf-8"),
                               capture_output=True, timeout=20,
                               start_new_session=True)
        except OSError:
            return False              # no "security" on this machine
        except subprocess.TimeoutExpired:
            # A locked keychain leaves the question standing. There is no
            # second way round: handing the key over as an argument would
            # put it in the process list, where every user of the machine
            # can read it.
            return False
        return p.returncode == 0 and load_api_key() == key
    if os.name == "nt":
        try:
            import winreg
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH) as k:
                winreg.SetValueEx(k, "auphonic_api_key", 0, winreg.REG_SZ, key)
            return True
        except Exception:
            return False
    return False


# Whether the keychain is open, read out of the library every Mac
# carries. If Apple ever withdraws SecKeychainGetStatus, the way back is
# not the modern item query -- that answers the same whether the store is
# shut or empty -- but to ask nothing and say why a save failed.
SECURITY_LIBRARY = "/System/Library/Frameworks/Security.framework/Security"
KEYCHAIN_IS_OPEN = 1          # the bit that stands for "not locked"


def key_store_locked():
    """Say whether the macOS keychain is locked: True, False or None.

    None where the question was not put: not a Mac, or the library did
    not answer. It asks the user nothing and starts nothing -- the
    command-line way puts a password window on the screen, which is the
    one thing a question asked twice a second must not do.
    """
    if sys.platform != "darwin":
        return None
    try:
        library = ctypes.CDLL(SECURITY_LIBRARY)
        bits = ctypes.c_uint32(0)
        failed = library.SecKeychainGetStatus(None, ctypes.byref(bits))
    except (OSError, AttributeError):
        # Nothing said here: unknown leaves the button live, and a save
        # that then fails says what happened once, instead of this line
        # saying it twice a second.
        return None
    return None if failed else not bits.value & KEYCHAIN_IS_OPEN


def open_key_store_app():
    """Bring up the app that unlocks the keychain. True if it started.

    By its bundle name and not by a path: the app has moved between
    system folders, so a path written down here is a guess about where
    it will be kept next.
    """
    if sys.platform != "darwin":
        return False
    try:
        subprocess.Popen(["open", "-b", "com.apple.keychainaccess"])
    except OSError as e:
        print(T('  Keychain Access could not be opened: %s') % e)
        return False
    return True


def key_store_trouble():
    """Say why a key did not go into the store on this machine."""
    if key_store_off_limits():
        return T('This run is a test run and the store still carries its '
                 'real name, so nothing was written. Point KEY_SERVICE, '
                 'KEY_ACCOUNT or REG_PATH somewhere else first.')
    if sys.platform == "darwin":
        if key_store_locked():
            return T('The keychain is locked. Unlock it and try again.')
        return T('The keychain did not take the key. Keychain Access can '
                 'say why.')
    if os.name == "nt":
        return T('The registry did not take the key.')
    return T('The key can only be stored on Mac and Windows -- in the '
             'keychain or the registry. It does not go into a file.')


# What the key store last said: every ask is a process, and drawing the
# settings sheet asks several times over. The key is in memory the
# moment it is read at all, so this puts it nowhere new; storing or
# deleting it empties this again.
_API_KEY = {}


def forget_api_key():
    """Ask the key store again next time."""
    _API_KEY.clear()


def load_api_key():
    """Read the stored API key, or "" if there is none."""
    # Keyed on the place it is kept, not just on the machine: the place
    # is fixed in a run but not in a test, which points the store at a
    # throwaway name and asks again. All three names are in the key --
    # on a Mac the registry path decides nothing.
    where = (sys.platform, KEY_SERVICE, KEY_ACCOUNT, REG_PATH)
    if where not in _API_KEY:
        _API_KEY[where] = _ask_key_store()
    return _API_KEY[where]


def _ask_key_store():
    """Go to the keychain or the registry, whatever this machine has."""
    if key_store_off_limits():
        return ""
    if sys.platform == "darwin":
        try:
            # A limit for the same reason the write has one: a locked
            # keychain can leave "security" waiting, and a window that
            # waits for good is worse than a key that is not found. The
            # empty input keeps it off this program's own standard input.
            p = subprocess.run(
                ["security", "find-generic-password", "-s", KEY_SERVICE,
                 "-a", KEY_ACCOUNT, "-w"],
                input=b"", capture_output=True, timeout=20,
                start_new_session=True)
        except (OSError, subprocess.TimeoutExpired):
            return ""
        return p.stdout.decode("utf-8", "replace").strip()\
            if not p.returncode else ""
    if os.name == "nt":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH) as k:
                value, _ = winreg.QueryValueEx(k, "auphonic_api_key")
                return (value or "").strip()
        except Exception:
            return ""
    return ""


def delete_api_key():
    """Take the key out of the OS credential store. True if one went.

    The same three guards as the write, and for the same reason: this
    hangs off a click on a checkbox, where nothing catches a fault, and
    a locked keychain can leave "security" waiting on a question.
    """
    forget_api_key()
    if key_store_off_limits():
        return False
    # Unticking the box lands here, and it lands here again the moment a
    # failed write puts the tick back -- so the same look as the write.
    if key_store_locked():
        return False
    if sys.platform == "darwin":
        try:
            p = subprocess.run(["security", "delete-generic-password",
                                "-s", KEY_SERVICE, "-a", KEY_ACCOUNT],
                               input=b"", capture_output=True, timeout=20,
                               start_new_session=True)
        except (OSError, subprocess.TimeoutExpired):
            return False
        return p.returncode == 0
    if os.name == "nt":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0,
                                winreg.KEY_SET_VALUE) as k:
                winreg.DeleteValue(k, "auphonic_api_key")
            return True
        except Exception:
            return False
    return False


def _pip_install(*packages):
    """Ask, then run pip. False where the answer is no.

    Nothing is installed unasked: this writes into a Python other
    things use. The question sits in this one place, so no caller
    can skip it.

    Plain and --user, no third: --break-system-packages defeats the
    barrier a system puts up against exactly this.
    """
    printed = " ".join(packages)
    if INSTALL_TOOLS:
        # VPM_INSTALL_TOOLS: whoever set it has answered in advance.
        print(T('  Installing it: pip install %s') % printed)
    elif not sys.stdin.isatty():
        # Nobody to answer, so nothing is asked and nothing is said:
        # the caller knows what it wanted and says that in its own
        # words. A question printed where it cannot be answered is
        # noise on every start.
        return False
    else:
        print(T('  %s would be installed into this Python: %s')
              % (printed, sys.executable))
        answer = input(T('  Run that now? [Y/n] ')).strip().lower()
        if answer and not answer.startswith(("y", "j")):
            print(T('  By hand:  %s -m pip install %s')
                  % (sys.executable, printed))
            return False
    # pip runs code from the packages it installs, so it is not given the
    # environment this program runs in: an API key in AUPHONIC_TOKEN would
    # otherwise be readable by every setup script in the dependency chain.
    clean = dict(os.environ)
    clean.pop("AUPHONIC_TOKEN", None)
    last = ""
    for extra_text in ([], ["--user"]):
        try:
            # stdout stays visible: PySide6 is a download of a few
            # hundred megabytes, and silence for that long looks like a
            # hang. stderr is captured because a rejected attempt is
            # followed by the next one.
            p = subprocess.run([sys.executable, "-m", "pip", "install"]
                               + extra_text + list(packages),
                               stderr=subprocess.PIPE, env=clean)
        except OSError:
            return False
        if p.returncode == 0:
            return True
        last = (p.stderr or b"").decode("utf-8", "replace").strip()
    # Why it failed, not just that it did. Without this the advice below
    # is the same command again, and it fails the same way again.
    for line in last.splitlines()[-4:]:
        print("    %s" % line)
    return False


def _really_there(module):
    """Import a module, or None -- and a hollow one counts as missing.

    pip leaves a package's __pycache__ folder behind on uninstall, and
    Python reads it as a namespace package: the import succeeds and the
    module is empty. Taken for the real package it fails much later,
    somewhere that says nothing about the cause.
    """
    import importlib
    try:
        got = importlib.import_module(module)
    except ImportError:
        return None
    # A namespace package -- what the empty folder reads as -- has no
    # origin. A real module names the file it was read from.
    spec = got.__spec__
    return got if spec is not None and spec.origin else None


def _require_module(module, package=None):
    """Import a module, installing its package once if it is missing.

    Exits the process if the module is still unavailable after install.
    """
    import importlib
    got = _really_there(module)
    if got is not None:
        return got
    pkg = package or module
    # Not "installing it": the install is asked for below and may be
    # refused, and a line that promises what has not been decided is
    # worse than one that only says what is known.
    print(T('%s is missing. The first time it takes a few minutes.') % pkg)
    if _pip_install(pkg):
        importlib.invalidate_caches()
        got = _really_there(module)
        if got is not None:
            return got
    sys.exit(T('%s could not be installed.\nBy hand:  %s -m pip install %s') % (pkg, sys.executable, pkg))
