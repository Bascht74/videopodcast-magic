# -*- coding: utf-8 -*-
"""Getting the tools in place, before the first sound is touched.

A piece read out of the folder beside it by beside(). It cannot import
the file it was cut out of -- that file is still being read -- so the
program is handed in and every name is bound below, by name. The
credential store stands under the same heading: without the key there
is nothing to send a production to.
"""

# beside() puts the program here before this file is read.
PROGRAM = PROGRAM

# What this piece uses out of the program. Two names are missing, and
# the blocks under the list say which and why.

FFMPEG_FLOOR = PROGRAM.FFMPEG_FLOOR
INSTALL_TOOLS = PROGRAM.INSTALL_TOOLS
T = PROGRAM.T
ctypes = PROGRAM.ctypes
json = PROGRAM.json
number_text = PROGRAM.number_text
os = PROGRAM.os
platform = PROGRAM.platform
re = PROGRAM.re
shutil = PROGRAM.shutil
subprocess = PROGRAM.subprocess
sys = PROGRAM.sys
tempfile = PROGRAM.tempfile
threading = PROGRAM.threading
time = PROGRAM.time

# as_warn stands further down the file this was cut out of, so a copy
# here would be an AttributeError. It is reached through PROGRAM.

# __file__ is the other: a build laid beside the program lies beside
# the program, so the place is asked of PROGRAM.__file__, never of this.


def version_text(numbers):
    """A version as people write it."""
    return ".".join(str(x) for x in numbers)


def version_from_line(line):
    """Read a version off the first line an ffmpeg-family tool prints.

    Every build writes it the same way -- "ffmpeg version 9.0.1
    Copyright ..." -- and what follows differs. One out of git carries
    a commit where the number should be, and then nothing comes back.
    The word the build calls itself comes back beside it, to be quoted.
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

    Both are asked: they are found by name, so one beside the script
    and one on the search path can be different builds.
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

    The filter chain asks per track and the measurement costs 23 ms.
    """
    global _SOXR
    if _SOXR is None:
        _SOXR = _have_soxr()
    return _SOXR


def forget_soxr():
    """Measure soxr again the next time it is asked for.

    An install puts another ffmpeg in place; the kept answer is stale.
    """
    global _SOXR
    _SOXR = None


def tools_folder(make=False):
    """Where a build this program fetched itself lives, or None.

    Not the cache: everybody is told that folder may be deleted, and
    deleting it must not take ffmpeg with it. Not site-packages either,
    which pip writes over. VPM_TOOLS points it elsewhere.
    """
    base = os.environ.get("VPM_TOOLS") or ""
    if not base:
        if os.environ.get("VPM_SILENT"):
            # A test run fetches nothing and keeps nothing, so it has no
            # folder to keep it in. Same rule as the settings store.
            return None
        if sys.platform == "darwin":
            base = os.path.expanduser("~/Library/Application Support")
        elif os.name == "nt":
            # LOCALAPPDATA, not APPDATA: a fetched ffmpeg must not roam.
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

    A python.org build was handed no certificates at all.
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

    Started from the Dock or the Finder, a program inherits almost no
    search path, so an ffmpeg a manager installed is out of reach.
    """
    if sys.platform == "darwin":
        # Homebrew on Apple silicon, Homebrew on Intel, MacPorts.
        return ["/opt/homebrew/bin", "/usr/local/bin", "/opt/local/bin"]
    if sys.platform == "win32":
        # Chocolatey, Scoop, winget -- none is on a clicked path.
        home = os.path.expanduser("~")
        data = os.environ.get("ProgramData") or "C:\\ProgramData"
        local = os.environ.get("LOCALAPPDATA") or home
        return [os.path.join(data, "chocolatey", "bin"),
                os.path.join(home, "scoop", "shims"),
                os.path.join(local, "Microsoft", "WindowsApps")]
    # By hand, snap, and what pip and pipx write for one user.
    # Homebrew on Apple silicon has no business here.
    return ["/usr/local/bin", "/snap/bin",
            os.path.expanduser("~/.local/bin")]


def find_required_tools():
    """Locate ffmpeg and ffprobe, and check they are new enough.

    soxr is no part of it: without it the clock drift comes out a
    hundred times coarser, and coarser is not broken. Returns ("", "")
    where all is well, else "missing" or "old" and the sentence for it.
    Nothing is printed: console or window is not yet known.
    """
    # Beside the program and not beside this piece: what somebody laid
    # next to the program lies in the first of the two folders.
    here = os.path.dirname(os.path.abspath(PROGRAM.__file__))
    # A build this program fetched goes in front of the search path:
    # behind it a distribution's ffmpeg 6.1.1 would keep answering.
    ours = tools_folder()
    was = os.environ.get("PATH", "")
    if ours and shutil.which("ffmpeg", path=ours) \
            and ours not in was.split(os.pathsep):
        os.environ["PATH"] = ours + os.pathsep + was
    # Behind the search path, never in front: whoever has an ffmpeg on
    # the path keeps it. Only folders that are there go in.
    path = os.environ.get("PATH", "")
    known = path.split(os.pathsep)
    # A test that has to act as though no ffmpeg lay anywhere sets
    # VPM_NO_MANAGER_PATH: an empty search path is not empty on a
    # machine where a manager installed one. The program never sets it.
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
    print, so it lands wherever this run shows its output. *asked* says
    the question was already put somewhere else.
    """
    print(PROGRAM.as_warn(says))
    if install_ffmpeg(update=kind != "missing", asked=asked):
        # Asked again: a manager reports success on a too-old ffmpeg.
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
    # update is left on: without it the install runs off a stale index.
    "brew": {"NONINTERACTIVE": "1", "HOMEBREW_NO_ENV_HINTS": "1"},
    # Without this apt opens full-screen dialogs of its own.
    "apt-get": {"DEBIAN_FRONTEND": "noninteractive"},
}


# homebrew/core builds ffmpeg without soxr in every version there is,
# and only this tap has libsoxr. It has no bottle, so the button
# compiles: two to three minutes for the fine clock correction.
BREW_FFMPEG = ("homebrew-ffmpeg/ffmpeg/ffmpeg", "--with-libsoxr")


def brew_ffmpeg_from_elsewhere():
    """True where a brew ffmpeg from another tap is standing in the way.

    With homebrew/core's ffmpeg installed, brew refuses the tap
    outright. Asked out of the keg's receipt: a file answers at once.
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
            # An unreadable receipt is still a keg in the way.
            return True
        if (came.get("source") or {}).get("tap") != "homebrew-ffmpeg/ffmpeg":
            return True
    return False


def package_manager_command(update=False):
    """How this system installs ffmpeg, or () where none of them is here.

    The first manager found, each with the switch that stops it asking
    again, on Linux with sudo unless the run is root already. *update*
    asks for the other command: told to install what is already there a
    manager does nothing, and building again is what puts an option in.
    """
    if sys.platform == "darwin":
        if shutil.which("brew"):
            # --yes is brew's own; NONINTERACTIVE no longer covers the
            # confirmation. Rebuild only where the tap's build is in.
            if update and not brew_ffmpeg_from_elsewhere():
                return ("brew", "reinstall", "--yes") + BREW_FFMPEG
            return ("brew", "install", "--yes") + BREW_FFMPEG
        return ()
    if sys.platform == "win32":
        # No manager here; install_ffmpeg fetches a built one instead.
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


# What a package manager says just before it goes quiet: "==> " and the
# command it runs. brew then writes its output into a log (Formula#system).
BUILD_TOOLS = ("configure", "make", "gmake", "cmake", "meson", "ninja",
               "cargo", "autoreconf", "bootstrap")


def build_begins(line):
    """True where this line is a package manager starting to compile.

    The silence starts under this line, and only build commands count.
    """
    words = line.strip().split()
    if len(words) < 2 or words[0] != "==>":
        return False
    return os.path.basename(words[1]) in BUILD_TOOLS


def sign_of_life(line, mark, every=5.0):
    """Keep the pane moving while the package manager says nothing.

    A build log goes 36 seconds without a line on a fast Mac and a
    multiple of that on an older one, so the movement comes from here.
    The sentence that says what is happening hangs on the manager's own
    first build line. Hands back the sink, and the way to stop the dots.
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

    A manager's own output is the only sign anything is happening, so
    stderr is folded into stdout and each line goes out as it arrives
    -- newline and all, because the pane breaks its blocks on those.
    Returns the exit code, or None where it could not be started.
    """
    # Nothing is piped where nobody is listening: a pipe would also
    # take sudo's password prompt, which carries no newline and would
    # sit unseen in a buffer while the terminal waits for it.
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
            # Silence here would read as a command that said nothing.
            say(T('  That did not work: %s') % e)
    return child.wait()


def install_over_package_manager(update=False, asked=False, say=None,
                                 started=None):
    """Offer the package manager, and run it if that is wanted.

    True when ffmpeg was installed. Asked only where somebody can
    answer: a window started from the desktop has no console, and a
    question nobody sees would hang the start for good. *say* takes
    every line; without one they go to print.
    """
    tell = (lambda text: say(text + "\n")) if say else print
    if os.environ.get("VPM_SILENT"):
        # A test run installs nothing and asks nobody. Before the
        # platforms, because the Windows branch asks a question too.
        return False
    command = package_manager_command(update)
    if not command:
        # No manager here; install_ffmpeg goes on from this point.
        return False
    printed = " ".join(command)
    if INSTALL_TOOLS or asked:
        # VPM_INSTALL_TOOLS: whoever set it answered in advance.
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
        # Room first, or brew refuses the tap. Said out loud: for a
        # moment afterwards this machine has no ffmpeg at all.
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

    Always False: a browser download is not done when this returns.
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
# none. win64 and linux64 are both n9.0.1-11-ge47273f4d9, both carry
# --enable-libsoxr, 121 and 161 MB.

# "latest" is a moving tag on the 9.0 line, so what arrived is asked
# afterwards rather than promised here. Name: line, machine, licence,
# line, kind of archive.
FFMPEG_BUILD_PLACE = ("https://github.com/BtbN/FFmpeg-Builds/releases"
                      "/download/latest/ffmpeg-n9.0-latest-%s-gpl-9.0.%s")


def ffmpeg_build_url():
    """Where the built ffmpeg for this machine is, or "".

    macOS gets none on purpose: there is no native arm64 build and this
    program does not run under Rosetta, so a Mac compiles its own out
    of the tap. A 32-bit machine gets none either: there is no build.
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

    A package manager, or a built one to fetch; else no button at all.
    """
    return bool(package_manager_command() or ffmpeg_build_url())


def fetch_archive(url, where, say=None):
    """Fetch that address into that file. "" when it arrived.

    The one place that opens a connection, so a test can replace it.
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
                    # Every ten of them: the pane breaks on newlines,
                    # and a line per block would be a hundred and fifty.
                    if say and out.tell() - said >= 10 << 20:
                        said = out.tell()
                        say(T('  %s of %s MB')
                            % (number_text(said >> 20, 0),
                               number_text(whole >> 20, 0)) + "\n")
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

    Windows and Linux go this way: Windows has no manager to ask, and a
    distribution's is under the floor -- Ubuntu 24.04 carries 6.1.1.
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
             % number_text(came, 0))
        return False
    # In front of the search path, so the fetched one answers rather
    # than whatever the system had. Next start: find_required_tools.
    if folder not in os.environ.get("PATH", "").split(os.pathsep):
        os.environ["PATH"] = folder + os.pathsep + os.environ.get("PATH", "")
    forget_soxr()
    tell(T('  It is here: %s') % folder)
    return True


def install_ffmpeg(update=False, asked=False, say=None, started=None):
    """Get an ffmpeg, whichever way this machine has. True when it came.

    The one door, and the order in it is the point: the package manager
    first, then the tools asked again -- a manager can report success
    having laid down 6.1.1 -- and only then a built one fetched.
    """
    if install_over_package_manager(update=update, asked=asked,
                                   say=say, started=started):
        forget_soxr()
        if not find_required_tools()[0]:
            return True
    return fetch_ffmpeg_build(asked=asked, say=say)


def how_to_get_ffmpeg(update=False):
    """The advice for the machine in hand, in one sentence.

    One place for three readers, so none can say what the others do not.
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

    Said, never demanded. Without soxr the drift comes out in steps of
    21 ppm instead of 0.21, which is coarser but not broken.
    """
    if soxr_available():
        return T('This ffmpeg has soxr: the clock drift between cameras '
                 'comes out in steps of 0.21 ppm.')
    return T('This ffmpeg has no soxr: the clock drift between cameras '
             'comes out in steps of 21 ppm instead of 0.21.')


# The API key lives in the OS credential store -- macOS keychain,
# Windows registry under HKEY_CURRENT_USER. Never in a file: the script
# gets copied around. All three names of the place stand only here.
KEY_STORE_REAL = ("videopodcast-magic", "auphonic",
                  r"Software\videopodcast-magic")
KEY_SERVICE, KEY_ACCOUNT, REG_PATH = KEY_STORE_REAL


def key_store_off_limits():
    """True where this run may not go near the credential store at all.

    A test run marks itself with VPM_SILENT, and a test with business
    in the store points KEY_SERVICE, KEY_ACCOUNT or REG_PATH at a
    throwaway name first. One that forgets would overwrite the key this
    machine really uses, so the store refuses. Reading is refused with
    writing: a test that reads the key prints it in a failure line.
    """
    if not os.environ.get("VPM_SILENT"):
        return False
    return (KEY_SERVICE, KEY_ACCOUNT, REG_PATH) == KEY_STORE_REAL


def store_api_key(key):
    """Store the API key in the OS credential store. True on success.

    On a Mac the key goes to "security" over its input, never as an
    argument that would stand in the process list. It needs a session
    of its own, and the word is sent twice because it asks to confirm.
    """
    forget_api_key()   # or the old one would still answer
    if key_store_off_limits():
        return False
    # Looked at first: a locked keychain leaves "security" standing for
    # its whole limit, and a frozen window says less than the lock does.
    if key_store_locked():
        return False
    # A pasted key carries blanks and a newline, and goes as a line.
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
            # A locked keychain leaves the question standing. Handing
            # the key over as an argument instead would put it in the
            # process list, where every user of the machine reads it.
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
# carries. If SecKeychainGetStatus goes, ask nothing: the item query
# answers alike whether the store is shut or empty.
SECURITY_LIBRARY = "/System/Library/Frameworks/Security.framework/Security"
KEYCHAIN_IS_OPEN = 1          # the bit that stands for "not locked"


def key_store_locked():
    """Say whether the macOS keychain is locked: True, False or None.

    None where the question was not put. It asks nothing and starts
    nothing -- the command-line way puts a password window up.
    """
    if sys.platform != "darwin":
        return None
    try:
        library = ctypes.CDLL(SECURITY_LIBRARY)
        bits = ctypes.c_uint32(0)
        failed = library.SecKeychainGetStatus(None, ctypes.byref(bits))
    except (OSError, AttributeError):
        # Nothing said here: unknown leaves the button live, and a save
        # that then fails says what happened once, not every tick.
        return None
    return None if failed else not bits.value & KEYCHAIN_IS_OPEN


def open_key_store_app():
    """Bring up the app that unlocks the keychain. True if it started.

    By bundle name, not by a path: the app moves between folders.
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
# settings sheet asks several times over. Storing or deleting empties it.
_API_KEY = {}


def forget_api_key():
    """Ask the key store again next time."""
    _API_KEY.clear()


def load_api_key():
    """Read the stored API key, or "" if there is none."""
    # Keyed on the place it is kept, not just the machine: a test
    # points the store at a throwaway name and asks again.
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
            # keychain can leave "security" waiting for good. The empty
            # input keeps it off this program's standard input.
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

    The same guards as the write: this hangs off a click on a checkbox,
    and a locked keychain can leave "security" waiting.
    """
    forget_api_key()
    if key_store_off_limits():
        return False
    # Unticking lands here, and again when a failed write puts the tick
    # back -- so the same look before it as the write has.
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


def pip_repair(packages):
    """Let pip put those packages back, unasked. True where it went through.

    For something that was installed once and does not import any
    more: the question was answered at installing, so it is not put
    again. Plain and then --user, no third, the same two the ordinary
    install takes. What it says goes through print, which in a window
    lands in the log.
    """
    if os.environ.get("VPM_SILENT"):
        # A test run installs nothing. Before everything else, so that
        # no path around it can exist.
        return False
    print(T('  Putting it back: %s') % " ".join(packages))
    # pip runs code out of what it installs, so the key does not
    # travel into it -- the same rule the ordinary install is handed.
    clean = dict(os.environ)
    clean.pop("AUPHONIC_TOKEN", None)
    last = ""
    for extra_text in ([], ["--user"]):
        try:
            p = subprocess.run([sys.executable, "-m", "pip", "install",
                                "-U"] + extra_text + list(packages),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, env=clean)
        except OSError as e:
            print(T('  That did not work: %s') % e)
            return False
        if p.returncode == 0:
            return True
        last = (p.stdout or b"").decode("utf-8", "replace").strip()
    # Why it failed: else the sentence the window shows next is the
    # same command again, and nobody learns anything.
    for line in last.splitlines()[-4:]:
        print("    %s" % line)
    return False


def _pip_install(*packages):
    """Ask, then run pip. False where the answer is no.

    Nothing is installed unasked: this writes into a Python other
    things use. Plain and --user, no third: --break-system-packages
    defeats the barrier a system puts up against exactly this.
    """
    printed = " ".join(packages)
    if INSTALL_TOOLS:
        # VPM_INSTALL_TOOLS: whoever set it has answered in advance.
        print(T('  Installing it: pip install %s') % printed)
    elif not sys.stdin.isatty():
        # Nobody to answer, so nothing is asked and nothing is said: a
        # question where it cannot be answered is noise on every start.
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
            # stdout stays visible: PySide6 is a few hundred megabytes
            # and silence that long looks like a hang. stderr is caught
            # because a rejected attempt is followed by the next.
            p = subprocess.run([sys.executable, "-m", "pip", "install"]
                               + extra_text + list(packages),
                               stderr=subprocess.PIPE, env=clean)
        except OSError:
            return False
        if p.returncode == 0:
            return True
        last = (p.stderr or b"").decode("utf-8", "replace").strip()
    # Why it failed: else the advice below is the same command again.
    for line in last.splitlines()[-4:]:
        print("    %s" % line)
    return False


def _really_there(module):
    """Import a module, or None -- and a hollow one counts as missing.

    pip leaves a package's __pycache__ behind on uninstall and Python
    reads it as a namespace package: the import succeeds, empty.
    """
    import importlib
    try:
        got = importlib.import_module(module)
    except ImportError:
        return None
    # A namespace package has no origin; a real module names its file.
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
    # Not "installing it": the install below may still be refused.
    print(T('%s is missing. The first time it takes a few minutes.') % pkg)
    if _pip_install(pkg):
        importlib.invalidate_caches()
        got = _really_there(module)
        if got is not None:
            return got
    sys.exit(T('%s could not be installed.\nBy hand:  %s -m pip install %s') % (pkg, sys.executable, pkg))
