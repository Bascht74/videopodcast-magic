# -*- coding: utf-8 -*-
"""Put the installed command where a person looks for programs.

A piece of the program, read out of the folder beside it by beside().
No software is installed here: pip has already put a starter into a
bin folder, and everything below lays a pointer to that starter where
the system shows programs. Nothing in here may stop a start -- every
way it can go wrong ends in one sentence and a program that runs.
"""
# Nothing is imported at the top. plistlib, sysconfig and collections
# are not loaded by the rest of the program, and asking for the three
# of them costs 2.5 to 3.5 ms on every start -- ten times what reading
# this file costs -- for code that runs once. They are asked for below.

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

T = PROGRAM.T
VERSION = PROGRAM.VERSION
keep_setting = PROGRAM.keep_setting
installed_by_a_package_manager = PROGRAM.installed_by_a_package_manager
log_aside = PROGRAM.log_aside
os = PROGRAM.os
settings = PROGRAM.settings
shutil = PROGRAM.shutil
struct = PROGRAM.struct
subprocess = PROGRAM.subprocess
sys = PROGRAM.sys


# The name pip writes into bin/, and the name a person reads under the
# icon. Both spellings are needed and they are deliberately the same.
COMMAND = "videopodcast-magic"
IDENTIFIER = "com.github.bascht74.videopodcast-magic"
SAYS = "Raw material from a video podcast becomes an edited episode"

# What is written down between two starts. The value is the path that
# was laid, not True: a boolean cannot tell "never made" from "made and
# thrown away", and that difference is the whole of the second question.
KEPT = "shortcut_laid"

# The picture, in this folder rather than written out as text inside
# it. It has to be named in [tool.setuptools.package-data] as well, or
# the wheel carries the reader and not the picture -- the way round the
# nine translations were missing until 5.9.2026.
ICON_FILE = "icon.png"


class Laid(object):
    """What one attempt to lay the pointer came to.

    *where* is the path that was laid, or would be, or was found gone.
    *made* is True only where something was written in this call.
    *say* is the finished line, and empty wherever the right answer is
    to leave the person alone.
    """

    def __init__(self, where, made, say):
        self.where = where
        self.made = made
        self.say = say


def lay_on_first_start():
    """Lay the pointer if this start is the first one, and say so.

    Only an installed copy lays anything; VPM_SHORTCUT stands in for
    the home folder the way VPM_LOGS does for the log folder. The
    condition is positive on purpose -- development/decisions.md says
    what it cost to learn that. And the line goes into the log, never
    onto the console: this runs before the window opens.
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
                  write_down=None, system=None):
    """Lay the pointer down, or say why nothing was laid.

    *root* stands in for the home folder and every path is built under
    it, so a measurement never reaches the account it runs in. *target*
    is the starter it points at, *png* the picture as PNG bytes, *kept*
    what earlier runs wrote down and *write_down(name, value)* the way
    one thing is written down.
    """
    system = system or _system()
    kept = {} if kept is None else kept
    where = place(root, system)

    if _thrown_away(kept.get(KEPT), where):
        return Laid(where, False, "")

    # What is already there is asked before the starter is looked up,
    # and that order is the whole cost of this on every start after the
    # first: an entry that still runs is finished business.
    there = os.path.exists(where)
    if there:
        old = _points_at(where, system)
        if old and _is_a_starter(old):
            # Written down although nothing was laid. Settings that were
            # reset would otherwise hold a working entry and no note, and
            # the next one taken away by hand would come back -- against
            # the one promise this makes.
            if write_down is not None and kept.get(KEPT) != where:
                write_down(KEPT, where)
            return Laid(where, False, "")

    if target is None:
        target = _starter_or_nothing()
    if not target:
        # No starter means this copy was not installed by pip -- it is
        # a checkout somebody is working in, and a checkout has no
        # business in the program list. Written down, never printed:
        # a line on every start of every working copy is noise.
        log_aside("shortcut -- no starter found to point at")
        return Laid(where, False, "")

    if there and system == "darwin":
        # A bundle is a folder, and writing into the old one would
        # leave whatever the old one had beside the new.
        shutil.rmtree(where, ignore_errors=True)

    png = icon_bytes() if png is None else png
    why = _write_it(where, target, png, root, system)
    if why:
        return Laid(where, False,
                    T('No shortcut to this program was made: %s') % why)
    if write_down is not None:
        write_down(KEPT, where)
    return Laid(where, True,
                T('A shortcut to this program was made: %s') % where)


def _write_it(where, target, png, root, system):
    """Write the one entry this system reads, or say what stopped it."""
    try:
        os.makedirs(os.path.dirname(where), exist_ok=True)
        if system == "darwin":
            _bundle(where, target, png)
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

    Absence alone says nothing: on a second machine, or under another
    root, the same absence means "never laid here". So the folder is
    asked as well. Where the folder stands and the thing in it does
    not, somebody took it out, and it does not come back.
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

    Four places are asked, in the order in which they are trustworthy
    rather than the order in which they are quick. The search path is
    asked last: it answers for whichever installation stands in front,
    which need not be the one this file was read out of.
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

    Asking for a scheme this Python does not know raises, so the list
    is cut against what it does know. get_default_scheme came in 3.10
    and pyproject.toml asks for 3.10, so it is called outright; the
    caller of all this catches whatever comes out of it anyway.
    """
    here = sysconfig.get_default_scheme()
    user = "nt_user" if os.name == "nt" else (
        "osx_framework_user" if sys.platform == "darwin" else "posix_user")
    known = set(sysconfig.get_scheme_names())
    return [s for s in (here, user, "posix_user", "nt_user") if s in known]


def _beside_the_module():
    """Folders that could hold the starter, read off this file's place.

    site-packages lies under the prefix as lib/pythonX.Y/site-packages,
    and the starters lie under the same prefix in bin. Walking up to
    the prefix and down again finds them without asking anything about
    the environment this start happens to have.
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

    One line per system, and they are not variations of one shape: a
    bundle is a folder, a Start menu entry is a file with a suffix, a
    launcher is a text file in a folder the desktop reads.
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
    is a measurement, and APPDATA would lead straight back into the
    account it is meant to keep out of.
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

    Every way this can go wrong ends in the same answer, and that
    answer is a working entry without a picture. The bytes are read
    rather than trusted: a half-written file would otherwise reach
    three different icon formats and be found out three times.
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

    Read back out of the thing itself and not out of what was written
    down: an interpreter that moved -- a Python upgraded from 3.13 to
    3.14 is the usual way -- leaves an entry that still exists and no
    longer starts anything, and the only place that shows is inside it.
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
                return line[5:].strip().split('" "')[0].strip('"')
    return ""


def _out_of_launcher(where):
    """The starter a .desktop file names on its Exec line.

    Undoing exactly what _exec_quote did. Splitting on the next double
    quote instead would stop at an escaped one and hand back half a
    path -- and a backslash would come back doubled.
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
# macOS: a bundle
# ---------------------------------------------------------------------------

def _bundle(where, target, png):
    """A .app -- a folder the Finder and the Dock read as one program.

    The Dock takes bundles and nothing else: a file in bin/ cannot be
    kept there, cannot be found by name in Spotlight and does not show
    up in the program list. That is the whole reason this is a folder
    with four files in it rather than a link.
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
        # Without this the window is drawn at one pixel per point and
        # blown up, which on every Mac sold this decade is a blurred
        # interface. It costs one line.
        "NSHighResolutionCapable": True,
    }
    icon = os.path.join(resources, COMMAND + ".icns")
    if png and _icns(icon, png):
        facts["CFBundleIconFile"] = COMMAND + ".icns"

    with open(os.path.join(contents, "Info.plist"), "wb") as f:
        plistlib.dump(facts, f)
    # Eight bytes and no newline. Modern macOS reads the plist, but
    # older Finder paths still look here first, and a bundle without
    # it is shown as a plain folder.
    with open(os.path.join(contents, "PkgInfo"), "w", encoding="ascii") as f:
        f.write("APPL????")

    stub = os.path.join(macos, COMMAND)
    with open(stub, "w", encoding="utf-8") as f:
        f.write(_stub_text(target))
    os.chmod(stub, 0o755)


def _stub_text(target):
    """The little runner inside the bundle.

    The search path is set here and not left alone. A program started
    from the Dock inherits the one launchd holds, which is
    /usr/bin:/bin:/usr/sbin:/sbin -- so ffmpeg from Homebrew would
    simply not be found, and from a terminal it would.
    """
    folder = os.path.dirname(target)
    return (
        "#!/bin/sh\n"
        "# Written by videopodcast-magic. Points at the starter pip\n"
        "# laid down; delete this bundle and the program is untouched.\n"
        'PATH="%s:/opt/homebrew/bin:/usr/local/bin:$PATH"\n'
        "export PATH\n"
        "# The second this was clicked. Everything before Python is\n"
        "# running cannot be timed from inside it, and that is where a\n"
        "# slow start hides.\n"
        "VPM_STARTED=$(date +%%s)\n"
        "export VPM_STARTED\n"
        'exec "%s" "$@"\n' % (folder.replace('"', '\\"'),
                              target.replace('"', '\\"')))


# The square sizes an .icns has a slot for. Anything else has no slot
# and cannot be written down as itself, which is why the picture this
# program ships is one of them.
SLOTS = {16: b"icp4", 32: b"icp5", 64: b"icp6", 128: b"ic07",
         256: b"ic08", 512: b"ic09", 1024: b"ic10"}


def _icns(path, png):
    """Write a one-image .icns beside the stub. True where it went.

    The format is a header and a list of chunks, and one chunk holding
    a PNG is a whole valid file -- so this needs nothing but struct, on
    any system. One slot and not seven: the other sizes could only hold
    blown-up copies, and macOS scales as well as anything else does.
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
    PowerShell. pywin32 would do it in process and would put a compiled
    package into every installation for one line that runs once.
    """
    icon = ""
    if png:
        # The same roaming folder the settings file is in, reached the
        # way place() reaches it: a link under APPDATA and an icon under
        # a home folder worked out by hand would be two answers to one
        # question, and the second is wrong often enough.
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

    Single quotes: inside them PowerShell expands nothing, so a path
    holding a dollar or a backtick stays a path. The only character
    that has to be handled is the single quote, written twice.
    """
    return "'" + str(text).replace("'", "''") + "'"


def _powershell(script):
    """Run that script and give back what it printed.

    Fed through the standard input rather than put on a command line: a
    command line is parsed twice on Windows, and a path with a space in
    it is where that goes wrong. No profile, because somebody's profile
    must not change what this does, and no console window either.
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
    this is a header and a directory entry in front of bytes that are
    already there. Width and height are one byte each and 256 is
    written as 0 -- the one trap in the format.
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

    The icon is named by a bare name and the file is put where the icon
    theme looks for that name. That is the way round the standard asks
    for, and the only one under which the same entry keeps its picture
    when the desktop switches theme or scale.
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
        # NOT MEASURED: what Qt reports as the window class has not
        # been seen on a Linux desktop from here. A wrong line costs a
        # doubled task bar entry and nothing else.
        "StartupWMClass=%s" % COMMAND,
    ]
    if icon:
        lines.append("Icon=%s" % icon)
    with open(where, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _theme_icon(png, root):
    """Write the picture where the icon theme looks, and name it.

    A square image goes into the theme under a bare name. Anything else
    -- artwork that is not square, or a theme folder that cannot be
    written -- still gets a picture, named by its full path, which the
    standard allows too. A missing one must not stop the entry.
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

    Double quotes, and inside them a backslash in front of a backslash,
    a double quote, a dollar and a backtick. A path with a space in it
    and no quotes is read as two arguments, which is the ordinary way
    this fails for anybody whose folder is called "My Programs".
    """
    out = str(target)
    for char in ("\\", '"', "$", "`"):
        out = out.replace(char, "\\" + char)
    return '"%s"' % out
