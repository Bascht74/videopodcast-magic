# -*- coding: utf-8 -*-
"""Where the program puts things down between one run and the next.

The folder a run may work in and have swept out again, the file that
holds what somebody chose, and the write that goes beside a file and
is moved into place, so that nothing is ever left half written.

A piece of the program, read out of the folder beside it by beside().
The program is handed in, and every name used out of it bound below.
"""

# The program itself. beside() puts it here before this file is read,
# and the line under that binds it to a name of this file's own.
PROGRAM = PROGRAM

# What the program has and this piece uses. All five are imports and
# stand far above the seam, so each is a copy of what was there and
# none is read late.

json = PROGRAM.json
os = PROGRAM.os
sys = PROGRAM.sys
tempfile = PROGRAM.tempfile
time = PROGRAM.time

# __file__ is not among them, and it is counted rather than looked
# for: no line below reads it, so nothing here would quietly answer
# with this folder instead of the program's own.


def cache_folder(sub=""):
    """Return the folder the program may keep its intermediate state in."""
    # VPM_CACHE points the whole thing somewhere else. The test suite
    # sets it: a test run has no business leaving envelopes, preflight
    # measurements and a compiled recogniser in the cache of whoever
    # happens to run it.
    base = os.environ.get("VPM_CACHE") or ""
    if not base:
        if sys.platform == "darwin":
            base = os.path.expanduser("~/Library/Caches")
        elif os.name == "nt":
            base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        else:
            base = (os.environ.get("XDG_CACHE_HOME")
                     or os.path.expanduser("~/.cache"))
    folder = os.path.join(base, "videopodcast-magic", sub)
    try:
        os.makedirs(folder, exist_ok=True)
    except OSError:
        return None
    return folder


def clean_old_files(folder, days=30):
    """Discard what has lain in this folder untouched for that long.

    One reader for both stores. A cache folder that only ever grows is
    a folder somebody finds one day and does not dare to delete.
    """
    if not folder:
        return
    limit = time.time() - days * 86400
    try:
        names = os.listdir(folder)
    except OSError:
        return
    for name in names:
        one = os.path.join(folder, name)
        try:
            if os.path.getmtime(one) < limit:
                os.unlink(one)
        except OSError:
            continue


def write_beside_then_move(file_path, data):
    """Write bytes so that no half-written file is ever read.

    Beside it and then moved into place: a run broken off halfway would
    otherwise leave half a file behind, and these files are read as
    measurements on every later start. Two runs writing the same one at
    the same moment is fine as well -- one of them wins whole.
    """
    if not file_path:
        return
    try:
        fd, beside = tempfile.mkstemp(dir=os.path.dirname(file_path),
                                      prefix=".vpm_", suffix=".part")
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(beside, file_path)
    except OSError:
        return


def settings_folder(make=False):
    """The folder somebody's own choices are kept in, or None.

    Not the cache: that is the one folder everybody is told may be
    deleted, and deleting it must not change the language the window
    speaks. So Application Support and not Caches, APPDATA and not
    LOCALAPPDATA -- a choice follows somebody onto the next machine,
    a measurement does not. VPM_SETTINGS points it somewhere else.
    """
    base = os.environ.get("VPM_SETTINGS") or ""
    if not base:
        # A test run marks itself with VPM_SILENT and has no business
        # in the settings of whoever started it -- the guard
        # key_store_off_limits() puts before the credential store, for
        # the same reason. A test with business here names its own.
        if os.environ.get("VPM_SILENT"):
            return None
        if sys.platform == "darwin":
            base = os.path.expanduser("~/Library/Application Support")
        elif os.name == "nt":
            base = os.environ.get("APPDATA") or os.path.expanduser("~")
        else:
            base = (os.environ.get("XDG_CONFIG_HOME")
                    or os.path.expanduser("~/.config"))
    folder = os.path.join(base, "videopodcast-magic")
    # Only a write asks for the folder to be built. Reading is what
    # every start does, and a run in which nobody chooses anything
    # must not leave an empty folder behind for having looked.
    if not make:
        return folder
    try:
        os.makedirs(folder, exist_ok=True)
    except OSError:
        return None
    return folder


def settings_file(make=False):
    """The file those choices stand in, or None where there is no place."""
    folder = settings_folder(make)
    return os.path.join(folder, "settings.json") if folder else None


# Read once and kept, under the file it was read from: that file is
# fixed within a run but not within a test, which points VPM_SETTINGS
# somewhere else and asks again. The same shape as _API_KEY.
_SETTINGS = {}


def forget_settings():
    """Read the settings file again the next time it is asked for."""
    _SETTINGS.clear()


def read_settings(path):
    """That file as a dictionary, empty wherever it cannot be had.

    Every way this can go wrong ends in the same answer, because that
    answer is what the program does with no file at all: ask the
    system. A remembered choice is a convenience, and a convenience
    that can stop a start is worse than no convenience.
    """
    if not path:
        return {}
    try:
        with open(path, "rb") as f:
            kept = json.loads(f.read().decode("utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return {}
    # A file holding a list or a number parses and is still not a
    # settings file; without this the first .get() on it raises.
    return kept if isinstance(kept, dict) else {}


def settings():
    """Everything kept from earlier runs, as a dictionary."""
    path = settings_file()
    if path not in _SETTINGS:
        _SETTINGS[path] = read_settings(path)
    return _SETTINGS[path]


def keep_setting(name, value):
    """Write one choice down for the next run. True if it went.

    Read, change the one entry, write the whole file back: an entry
    this version knows nothing about survives a version that does not
    know it, so an older copy started by accident does not throw away
    what a newer one wrote. That is what leaves room for the second
    setting and the third, and the language is only the first.
    """
    path = settings_file(make=True)
    if not path:
        return False
    kept = dict(settings())
    kept[name] = value
    try:
        data = json.dumps(kept, indent=1, sort_keys=True).encode("utf-8")
    except (TypeError, ValueError):
        return False
    write_beside_then_move(path, data)
    forget_settings()
    return read_settings(path).get(name) == value
