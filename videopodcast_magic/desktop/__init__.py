# -*- coding: utf-8 -*-
"""Put the installed command where a person looks for programs.

A piece of the program, read in by beside(). No software is installed
here: pip has already put a starter into a bin folder, and everything
below lays a pointer to it. Nothing in here may stop a start. On macOS
the pointer names the architecture as well, where the interpreter
carries two and the installed packages fit only one of them.
"""
# Nothing is imported at the top: plistlib, sysconfig and collections
# cost 2.5 to 3.5 ms on every start, for code that runs once.

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

T = PROGRAM.T
VERSION = PROGRAM.VERSION
ctypes = PROGRAM.ctypes
keep_setting = PROGRAM.keep_setting
installed_by_a_package_manager = PROGRAM.installed_by_a_package_manager
log_aside = PROGRAM.log_aside
os = PROGRAM.os
platform = PROGRAM.platform
settings = PROGRAM.settings
shutil = PROGRAM.shutil
struct = PROGRAM.struct
subprocess = PROGRAM.subprocess
sys = PROGRAM.sys

# pip's name in bin/ and the name under the icon, deliberately the same.
COMMAND = "videopodcast-magic"
IDENTIFIER = "com.github.bascht74.videopodcast-magic"
SAYS = "Raw material from a video podcast becomes an edited episode"

# What is written down between two starts: the path that was laid, not
# True -- a boolean cannot tell "never made" from "thrown away".
KEPT = "shortcut_laid"

# The picture, in this folder rather than as text. Named in
# [tool.setuptools.package-data] too, or the wheel carries no picture.
ICON_FILE = "icon.png"


class Laid(object):
    """What one attempt to lay the pointer came to.

    *where* is the path that was laid, or would be, or was found gone.
    *made* is True only where something was written in this call. *say*
    is the finished line, empty where the person is to be left alone.
    """

    def __init__(self, where, made, say):
        self.where = where
        self.made = made
        self.say = say


def lay_on_first_start():
    """Lay the pointer if this start is the first one, and say so.

    Only an installed copy lays anything; VPM_SHORTCUT stands in for the
    home folder. The line goes into the log: this runs before the window.
    """
    root = os.environ.get("VPM_SHORTCUT") or ""
    if not root and not installed_by_a_package_manager():
        return Laid("", False, "")
    laid = make_shortcut(root=root or None, kept=settings(),
                         write_down=keep_setting)
    if laid.say:
        log_aside("shortcut -- %s" % laid.say)
    return laid


def make_shortcut(root=None, target=None, png=None, kept=None,
                  write_down=None, system=None, run_as=None):
    """Lay the pointer down, or say why nothing was laid.

    *root* stands in for the home folder and every path is built under
    it, so a measurement never reaches the account it runs in. *target*
    is the starter, *png* the picture, *kept* what earlier runs wrote
    down, *write_down(name, value)* how one thing is written down, and
    *run_as* the architecture the entry asks for.
    """
    system = system or _system()
    kept = {} if kept is None else kept
    where = place(root, system)

    if _thrown_away(kept.get(KEPT), where):
        return Laid(where, False, "")

    # What is already there is asked before the starter is looked up:
    # an entry that still runs is finished business, unless it is one
    # of ours from before the architecture was named in it.
    there = os.path.exists(where)
    stands = there and _is_a_starter(_points_at(where, system) or "")
    if stands:
        run_as = _lay_again_as(where, system, run_as)
    if stands and not run_as:
        # Written down although nothing was laid: reset settings
        # would otherwise hold a working entry and no note.
        if write_down is not None and kept.get(KEPT) != where:
            write_down(KEPT, where)
        return Laid(where, False, "")

    if target is None:
        target = _starter_or_nothing()
    if not target:
        # No starter means a checkout, not a pip install, and a checkout
        # has no business in the program list. Written down, not printed.
        log_aside("shortcut -- no starter found to point at")
        return Laid(where, False, "")

    if there and system == "darwin":
        # A bundle is a folder: writing into the old one keeps its old.
        shutil.rmtree(where, ignore_errors=True)

    png = icon_bytes() if png is None else png
    if run_as is None:
        run_as = architecture_to_ask_for() if system == "darwin" else ""
    why = _write_it(where, target, png, root, system, run_as)
    if why:
        return Laid(where, False,
                    T('No shortcut to this program was made: %s') % why)
    if write_down is not None:
        write_down(KEPT, where)
    return Laid(where, True,
                T('A shortcut to this program was made: %s') % where)


def _write_it(where, target, png, root, system, run_as=""):
    """Write the one entry this system reads, or say what stopped it."""
    try:
        os.makedirs(os.path.dirname(where), exist_ok=True)
        if system == "darwin":
            _bundle(where, target, png, run_as)
        elif system == "nt":
            _link(where, target, png, root)
        else:
            _launcher(where, target, png, root)
    except Exception as e:
        return "%s: %s" % (type(e).__name__, e)
    if not os.path.exists(where):
        return T('it was written and was not there afterwards')
    return ""


def _starter_or_nothing():
    """The starter pip laid down, and never an exception."""
    try:
        return command_path()
    except Exception as e:
        log_aside("shortcut -- could not look for the starter: %s" % e)
        return ""


def _thrown_away(remembered, where):
    """Did somebody take away what an earlier run laid down?

    Absence alone says nothing -- under another root it means "never
    laid here" -- so the folder is asked too and must stand.
    """
    if not remembered or os.path.exists(remembered):
        return False
    folder = os.path.dirname(remembered)
    return os.path.isdir(folder) and os.path.dirname(where) == folder


# ---------------------------------------------------------------------------
# Where the starter is
# ---------------------------------------------------------------------------

def command_path(name=COMMAND):
    """The absolute path of the starter pip laid down, or "".

    Four places are asked, trustworthiest first. The search path is
    last: it answers for whichever installation stands in front.
    """
    import sysconfig
    tries = [os.path.join(
        os.path.dirname(os.path.abspath(sys.executable)), name)]
    for scheme in _schemes(sysconfig):
        try:
            folder = sysconfig.get_path("scripts", scheme)
        except (KeyError, ValueError):
            continue
        if folder:
            tries.append(os.path.join(folder, name))
    for folder in _beside_the_module():
        tries.append(os.path.join(folder, name))
    found = shutil.which(name)
    if found:
        tries.append(found)

    for path in tries:
        for spelling in _spellings(path):
            if _is_a_starter(spelling):
                return os.path.abspath(spelling)
    return ""


def _schemes(sysconfig):
    """The installation schemes worth asking, this system's first.

    Asking for a scheme this Python does not know raises, so the list is
    cut against what it does know. get_default_scheme came in 3.10.
    """
    here = sysconfig.get_default_scheme()
    user = "nt_user" if os.name == "nt" else (
        "osx_framework_user" if sys.platform == "darwin" else "posix_user")
    known = set(sysconfig.get_scheme_names())
    return [s for s in (here, user, "posix_user", "nt_user") if s in known]


def _beside_the_module():
    """Folders that could hold the starter, read off this file's place.

    site-packages lies under the prefix as lib/pythonX.Y/site-packages,
    the starters under the same prefix in bin. No environment is asked.
    """
    folders = []
    up = os.path.dirname(os.path.abspath(__file__))
    tail = "Scripts" if os.name == "nt" else "bin"
    for _ in range(6):
        up = os.path.dirname(up)
        if not up or up == os.path.dirname(up):
            break
        beside = os.path.join(up, tail)
        if os.path.isdir(beside):
            folders.append(beside)
    return folders


def _spellings(path):
    """That path, under every ending a starter carries on this system."""
    if os.name != "nt":
        return [path]
    return [path + ".exe", path + ".cmd", path + ".bat", path]


def _is_a_starter(path):
    """A file that exists and may be run."""
    if not os.path.isfile(path):
        return False
    return os.name == "nt" or os.access(path, os.X_OK)


# ---------------------------------------------------------------------------
# Where the pointer goes, and what the picture is
# ---------------------------------------------------------------------------

def home(root=None):
    """The folder everything is built under."""
    return os.path.abspath(root) if root else os.path.expanduser("~")


def place(root=None, system=None):
    """The full path of the thing that would be laid down.

    One line per system, and not variations of one shape: a bundle is a
    folder, a Start menu entry a file, a launcher a text file.
    """
    system = system or _system()
    if system == "darwin":
        return os.path.join(home(root), "Applications", COMMAND + ".app")
    if system == "nt":
        return os.path.join(_roaming(root), "Microsoft", "Windows",
                            "Start Menu", "Programs", COMMAND + ".lnk")
    return os.path.join(_share(root), "applications", COMMAND + ".desktop")


def _roaming(root):
    """The roaming profile folder -- APPDATA, or built under *root*.

    Asked of the system only where no root was given: under a root this
    is a measurement, and APPDATA leads back into the account.
    """
    if root is None and os.environ.get("APPDATA"):
        return os.environ["APPDATA"]
    return os.path.join(home(root), "AppData", "Roaming")


def _share(root):
    """The folder a desktop reads programs and icons out of."""
    return (os.environ.get("XDG_DATA_HOME") if root is None else "") \
        or os.path.join(home(root), ".local", "share")


def _system():
    """Which of the three shapes this machine reads."""
    if sys.platform == "darwin":
        return "darwin"
    if os.name == "nt":
        return "nt"
    return "posix"


def icon_bytes(folder=None):
    """The program's picture as PNG bytes, or b"".

    Every way this can go wrong ends in the same answer: a working entry
    without a picture. The bytes are read rather than trusted.
    """
    where = os.path.join(folder or os.path.dirname(os.path.abspath(__file__)),
                         ICON_FILE)
    try:
        with open(where, "rb") as f:
            png = f.read()
    except OSError:
        return b""
    return png if _png_size(png) != (0, 0) else b""


def _png_size(png):
    """(width, height) of a PNG held as bytes, or (0, 0)."""
    if not png or png[:8] != b"\x89PNG\r\n\x1a\n" or len(png) < 24:
        return (0, 0)
    return struct.unpack(">II", png[16:24])


def _points_at(where, system):
    """The starter an entry that is already there points at, or "".

    Read back out of the thing itself, not out of what was written down:
    an interpreter that moved leaves an entry that starts nothing.
    """
    try:
        if system == "darwin":
            return _out_of_stub(where)
        if system == "nt":
            return _powershell(
                "$s=(New-Object -ComObject WScript.Shell)."
                "CreateShortcut(%s); Write-Output $s.TargetPath"
                % _ps_quote(where)).strip()
        return _out_of_launcher(where)
    except Exception:
        return ""


def _out_of_stub(where):
    """The starter the little runner inside a bundle calls."""
    stub = os.path.join(where, "Contents", "MacOS", COMMAND)
    with open(stub, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("exec "):
                return _past_the_arch(
                    line[5:].strip()).split('" "')[0].strip('"')
    return ""


def _past_the_arch(rest):
    """What an exec line names, past a request for an architecture.

    Ours asks on a line of its own, but somebody who put the request
    into this line by hand still has an entry that names a starter.
    """
    words = rest.split(" ", 2)
    if len(words) == 3 and words[1][:1] == "-" \
            and os.path.basename(words[0]) == "arch":
        return words[2]
    return rest


def _out_of_launcher(where):
    """The starter a .desktop file names on its Exec line.

    Undoing exactly what _exec_quote did. Splitting on the next double
    quote would stop at an escaped one and hand back half a path.
    """
    with open(where, encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line.startswith("Exec="):
                continue
            rest = line[5:].strip()
            if not rest.startswith('"'):
                return rest.split(" ")[0]
            out, i = [], 1
            while i < len(rest) and rest[i] != '"':
                if rest[i] == "\\" and i + 1 < len(rest):
                    i += 1
                out.append(rest[i])
                i += 1
            return "".join(out)
    return ""


# ---------------------------------------------------------------------------
# Which architecture everything agrees on
# ---------------------------------------------------------------------------

# The one program that can grant an architecture. Without it there is
# nothing to ask with, and the Dock's choice stands.
ARCH_TOOL = "/usr/bin/arch"

# The line that says a runner inside an entry is this program's own.
# Written into every one, and the only thing that may be laid again.
WRITTEN_BY = "# Written by videopodcast-magic."

# What a Mach-O header calls a processor, under the names ARCH_TOOL
# takes. A file names one of these per architecture it carries.
CPU_NAMES = {0x01000007: "x86_64", 0x0100000C: "arm64",
             7: "i386", 12: "arm"}

# A fat header, big-endian, and how wide one entry in it is. A thin
# file has one of the two magics below and its own byte order.
FAT_MAGIC = {0xCAFEBABE: 20, 0xCAFEBABF: 32}
THIN_MAGIC = (0xFEEDFACE, 0xFEEDFACF)

# How many entries of a fat header are read at most: a file claiming
# more than this is not a program, and the count comes out of the file.
FAT_MOST = 32


def architectures_of(path):
    """The architectures one Mach-O file carries, as a set of names.

    A fat file lists them in its header, a thin one names the single
    one it is. Anything else -- a script, a folder, a file that is not
    there -- carries none, and the answer is the empty set.
    """
    try:
        with open(path, "rb") as f:
            head = f.read(8 + FAT_MOST * 32)
    except OSError:
        return set()
    if len(head) < 8:
        return set()
    fat = struct.unpack(">I", head[:4])[0]
    if fat in FAT_MAGIC:
        return _fat_architectures(head, FAT_MAGIC[fat])
    for order in ("<", ">"):
        magic, cpu = struct.unpack(order + "II", head[:8])
        if magic in THIN_MAGIC and cpu in CPU_NAMES:
            return set([CPU_NAMES[cpu]])
    return set()


def _fat_architectures(head, step):
    """The names a fat header lists, one cputype per entry."""
    out = set()
    count = struct.unpack(">I", head[4:8])[0]
    for i in range(min(count, FAT_MOST)):
        at = 8 + i * step
        if at + 4 > len(head):
            break
        cpu = struct.unpack(">I", head[at:at + 4])[0]
        if cpu in CPU_NAMES:
            out.add(CPU_NAMES[cpu])
    return out


def installed_architectures(folder=None):
    """The architectures every compiled package installed here fits.

    The cut, not the sum: one package that cannot run in an
    architecture is enough to rule it out for the whole start. One
    module per package is asked -- a wheel is built for one.
    """
    import sysconfig
    folder = folder or sysconfig.get_path("platlib")
    out = None
    for where in _one_module_per_package(folder):
        carried = architectures_of(where)
        if carried:
            out = carried if out is None else out & carried
    return out or set()


def _one_module_per_package(folder):
    """The path of one compiled module out of each package there.

    Only the top level of each package, so a folder with thousands of
    files in it costs one listing and not a walk.
    """
    out = []
    for name in sorted(_listing(folder)):
        where = os.path.join(folder, name)
        if name.endswith(".so"):
            out.append(where)
        elif not name.endswith(".dist-info") and os.path.isdir(where):
            inside = [one for one in sorted(_listing(where))
                      if one.endswith(".so")]
            if inside:
                out.append(os.path.join(where, inside[0]))
    return out


def _listing(folder):
    """What lies in that folder, and [] where it cannot be read."""
    try:
        return os.listdir(folder)
    except OSError:
        return []


def machine_architecture():
    """What this machine is, not what this process was started as.

    Under Rosetta every ordinary question answers x86_64, so the kernel
    is asked as well: it says 1 while it is translating this process.
    """
    now = platform.machine()
    return "arm64" if now == "x86_64" and _being_translated() else now


def _being_translated():
    """True where this process is an x86_64 one on an Apple Silicon Mac."""
    try:
        out = ctypes.c_int(0)
        size = ctypes.c_size_t(ctypes.sizeof(out))
        got = ctypes.CDLL(None).sysctlbyname(
            b"sysctl.proc_translated", ctypes.byref(out),
            ctypes.byref(size), None, 0)
    except Exception:
        return False
    return got == 0 and out.value == 1


def architecture_that_fits(carries, installed, machine):
    """Which architecture the interpreter, the packages and the machine share.

    "" wherever there is nothing to choose: one architecture in the
    interpreter, none that all the packages fit, or two that all fit
    and no reason to prefer either. The machine breaks that last tie.
    """
    carries, installed = set(carries), set(installed)
    if len(carries) < 2:
        return ""
    fits = carries & installed
    if machine in fits:
        return machine
    return sorted(fits)[0] if len(fits) == 1 else ""


def _may_ask(system, tool):
    """Whether an architecture can be asked for on this system at all.

    Nowhere but macOS: only there does one file carry two of them, and
    only there is there a program that grants one.
    """
    return system == "darwin" and os.access(tool, os.X_OK)


def architecture_to_ask_for():
    """The architecture a start of this program has to ask for, or "".

    Empty where nothing can be asked for and where nothing needs to be;
    the entry is then written exactly as it was written before.
    """
    if not _may_ask(sys.platform, ARCH_TOOL):
        return ""
    return architecture_that_fits(architectures_of(sys.executable),
                                  installed_architectures(),
                                  machine_architecture())


def _lay_again_as(where, system, run_as):
    """The architecture an entry that stands is to be laid again for.

    "" is the ordinary answer and leaves the entry alone. Only one of
    ours that names none while one is asked for now is out of date, and
    the entry it writes names one, so this cannot ask twice.
    """
    if system != "darwin" or not _ours_and_silent(where):
        return ""
    return architecture_to_ask_for() if run_as is None else run_as


def _ours_and_silent(where):
    """Whether the runner inside an entry is ours and names none.

    A runner this program did not write, and one somebody has put an
    architecture into since, are both left exactly as they are.
    """
    try:
        with open(os.path.join(where, "Contents", "MacOS", COMMAND),
                  encoding="utf-8", errors="replace") as f:
            runner = f.read()
    except OSError:
        return False
    return WRITTEN_BY in runner and ARCH_TOOL not in runner


def architecture_mismatch(running, installed):
    """The sentence for a process that cannot load what is installed.

    Both architectures are named and so is the way out: "not available"
    sends somebody to reinstall packages that are already there.
    """
    installed = set(installed)
    if not installed or running in installed:
        return ""
    return T('This program is running as %s and the packages installed '
             'for it are %s, so none of them can be loaded. This starts '
             'it right: %s') % (
        running, ", ".join(sorted(installed)),
        "arch -%s %s" % (sorted(installed)[0], COMMAND))


def architecture_trouble():
    """The sentence where this process cannot load what is installed, or "".

    Asked of the process, not of the machine: the fault is that the two
    are different, and platform.machine() is what the process came up as.
    """
    if sys.platform != "darwin":
        return ""
    return architecture_mismatch(platform.machine(),
                                 installed_architectures())


# ---------------------------------------------------------------------------
# macOS: a bundle
# ---------------------------------------------------------------------------

def _bundle(where, target, png, run_as=""):
    """A .app -- a folder the Finder and the Dock read as one program.

    The Dock takes bundles and nothing else: a file in bin/ cannot be
    kept there, found in Spotlight, or shown in the program list.
    """
    import plistlib
    contents = os.path.join(where, "Contents")
    macos = os.path.join(contents, "MacOS")
    resources = os.path.join(contents, "Resources")
    for folder in (macos, resources):
        os.makedirs(folder, exist_ok=True)

    facts = {
        "CFBundleName": COMMAND,
        "CFBundleDisplayName": COMMAND,
        "CFBundleIdentifier": IDENTIFIER,
        "CFBundleExecutable": COMMAND,
        "CFBundlePackageType": "APPL",
        "CFBundleInfoDictionaryVersion": "6.0",
        "CFBundleShortVersionString": VERSION,
        "CFBundleVersion": VERSION,
        # Without this the window is blown up and blurred on any Mac.
        "NSHighResolutionCapable": True,
    }
    icon = os.path.join(resources, COMMAND + ".icns")
    if png and _icns(icon, png):
        facts["CFBundleIconFile"] = COMMAND + ".icns"

    with open(os.path.join(contents, "Info.plist"), "wb") as f:
        plistlib.dump(facts, f)
    # Eight bytes and no newline. Modern macOS reads the plist, but older
    # Finder paths look here first and show a bundle without it as a folder.
    with open(os.path.join(contents, "PkgInfo"), "w", encoding="ascii") as f:
        f.write("APPL????")

    stub = os.path.join(macos, COMMAND)
    with open(stub, "w", encoding="utf-8") as f:
        f.write(_stub_text(target, run_as))
    os.chmod(stub, 0o755)


def _stub_text(target, run_as=""):
    """The little runner inside the bundle.

    The search path is set here and not left alone: a program started
    from the Dock inherits launchd's, /usr/bin:/bin:/usr/sbin:/sbin, so
    ffmpeg from Homebrew would not be found. *run_as* is the
    architecture to ask for, and "" leaves the choice where it was.
    """
    folder = os.path.dirname(target)
    quoted = target.replace('"', '\\"')
    return (
        "#!/bin/sh\n"
        "%s Points at the starter pip\n"
        "# laid down; delete this bundle and the program is untouched.\n"
        'PATH="%s:/opt/homebrew/bin:/usr/local/bin:$PATH"\n'
        "export PATH\n"
        "# The second this was clicked. Everything before Python is\n"
        "# running cannot be timed from inside it, and that is where a\n"
        "# slow start hides.\n"
        "VPM_STARTED=$(date +%%s)\n"
        "export VPM_STARTED\n"
        % (WRITTEN_BY, folder.replace('"', '\\"'))
    ) + _ask_for_arch(quoted, run_as) + ('exec "%s" "$@"\n' % quoted)


def _ask_for_arch(quoted, run_as):
    """The line that names an architecture, or "" where none was chosen.

    It gives way rather than failing: the plain exec stands under it,
    and a machine without the tool falls through to it untouched.
    """
    if not run_as:
        return ""
    return ("# The interpreter carries two architectures and the\n"
            "# installed packages fit this one; the Dock would pick.\n"
            '[ -x %s ] && exec %s -%s "%s" "$@"\n'
            % (ARCH_TOOL, ARCH_TOOL, run_as, quoted))

# The square sizes an .icns has a slot for. Anything else cannot be
# written down as itself, which is why the shipped picture is one.
SLOTS = {16: b"icp4", 32: b"icp5", 64: b"icp6", 128: b"ic07",
         256: b"ic08", 512: b"ic09", 1024: b"ic10"}


def _icns(path, png):
    """Write a one-image .icns beside the stub. True where it went.

    The format is a header and a list of chunks, and one chunk holding a
    PNG is a whole valid file, so this needs nothing but struct.
    """
    width, height = _png_size(png)
    if width != height or width not in SLOTS:
        return False
    chunk = SLOTS[width] + struct.pack(">I", len(png) + 8) + png
    with open(path, "wb") as f:
        f.write(b"icns" + struct.pack(">I", len(chunk) + 8) + chunk)
    return True


# ---------------------------------------------------------------------------
# Windows: an entry in the Start menu
# ---------------------------------------------------------------------------

def _link(where, target, png, root):
    """A .lnk, written by the shell object that owns the format.

    Writing one by hand is a page of struct that would have to be
    maintained; Windows brings the writer with it, reachable from
    PowerShell. pywin32 would add a compiled package for one line.
    """
    icon = ""
    if png:
        # The same roaming folder the settings file is in, reached the
        # way place() reaches it: two answers would be one too many.
        folder = os.path.join(_roaming(root), COMMAND)
        os.makedirs(folder, exist_ok=True)
        icon = os.path.join(folder, COMMAND + ".ico")
        if not _ico(icon, png):
            icon = ""

    lines = [
        "$s = (New-Object -ComObject WScript.Shell).CreateShortcut(%s)"
        % _ps_quote(where),
        "$s.TargetPath = %s" % _ps_quote(target),
        "$s.WorkingDirectory = %s" % _ps_quote(os.path.dirname(target)),
        "$s.Description = %s" % _ps_quote(SAYS),
    ]
    if icon:
        lines.append("$s.IconLocation = %s" % _ps_quote(icon + ",0"))
    lines.append("$s.Save()")
    _powershell("\n".join(lines))


def _ps_quote(text):
    """One PowerShell string, with nothing in it read as code.

    Single quotes: inside them PowerShell expands nothing, so a dollar
    or a backtick stays a character. A single quote is written twice.
    """
    return "'" + str(text).replace("'", "''") + "'"


def _powershell(script):
    """Run that script and give back what it printed.

    Fed through standard input rather than a command line: a command
    line is parsed twice on Windows, and a path with a space is where
    that goes wrong. No profile, and no console window.
    """
    shell = shutil.which("powershell") or shutil.which("pwsh")
    if not shell:
        raise OSError("no PowerShell to write the link with")
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    done = subprocess.run([shell, "-NoProfile", "-NonInteractive",
                           "-Command", "-"],
                          input=script.encode("utf-8"),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          creationflags=flags)
    if done.returncode != 0:
        raise OSError(done.stderr.decode("utf-8", "replace").strip()
                      or "PowerShell said %d" % done.returncode)
    return done.stdout.decode("utf-8", "replace")


def _ico(path, png):
    """Write a one-image .ico. True where it went.

    A PNG may stand inside an .ico unchanged since Windows Vista, so
    this is a header and a directory entry in front of bytes already
    there. Width and height are one byte each, and 256 is written as 0.
    """
    width, height = _png_size(png)
    if not width or width > 256 or height > 256:
        return False
    head = struct.pack("<HHH", 0, 1, 1)
    entry = struct.pack("<BBBBHHII", width % 256, height % 256, 0, 0,
                        1, 32, len(png), 6 + 16)
    with open(path, "wb") as f:
        f.write(head + entry + png)
    return True


# ---------------------------------------------------------------------------
# Linux: a launcher the desktop reads
# ---------------------------------------------------------------------------

def _launcher(where, target, png, root):
    """A .desktop file, and the icon under the name the theme knows.

    The icon is named by a bare name and the file put where the icon
    theme looks for that name. That is the way round the standard asks
    for, and the only one that survives a theme or scale change.
    """
    icon = _theme_icon(png, root)
    lines = [
        "[Desktop Entry]",
        "Type=Application",
        "Version=1.0",
        "Name=%s" % COMMAND,
        "Comment=%s" % SAYS,
        "Exec=%s %%F" % _exec_quote(target),
        "Terminal=false",
        "Categories=AudioVideo;AudioVideoEditing;",
        # NOT MEASURED: what Qt reports as the window class has not been
        # seen on a Linux desktop. A wrong line costs a doubled entry.
        "StartupWMClass=%s" % COMMAND,
    ]
    if icon:
        lines.append("Icon=%s" % icon)
    with open(where, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _theme_icon(png, root):
    """Write the picture where the icon theme looks, and name it.

    A square image goes into the theme under a bare name. Anything else
    -- not square, or an unwritable theme folder -- still gets a
    picture, named by its full path, which the standard allows too.
    """
    width, height = _png_size(png)
    if not width:
        return ""
    named = COMMAND
    where = os.path.join(_share(root), "icons", "hicolor",
                         "%dx%d" % (width, height), "apps", COMMAND + ".png")
    if width != height:
        where = os.path.join(_share(root), COMMAND, COMMAND + ".png")
        named = where
    try:
        os.makedirs(os.path.dirname(where), exist_ok=True)
        with open(where, "wb") as f:
            f.write(png)
    except OSError:
        return ""
    return named


def _exec_quote(target):
    """One argument of an Exec line, as the standard spells it.

    Double quotes, and inside them a backslash before a backslash, a
    double quote, a dollar and a backtick. A path with a space and no
    quotes is read as two arguments.
    """
    out = str(target)
    for char in ("\\", '"', "$", "`"):
        out = out.replace(char, "\\" + char)
    return '"%s"' % out
