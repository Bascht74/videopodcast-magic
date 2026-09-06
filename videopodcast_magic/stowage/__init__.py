# -*- coding: utf-8 -*-
"""Where the program puts things down between one run and the next.

The folder a run may sweep out again, the file that holds what somebody
chose, and the write that goes beside a file and is moved into place.
A piece of the program; the program is handed in and bound below.
"""

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# Bound above the seam, so each is a copy and none is read late.
json = PROGRAM.json
os = PROGRAM.os
sys = PROGRAM.sys
tempfile = PROGRAM.tempfile
time = PROGRAM.time

# __file__ is not among them: no line below reads it, so nothing here
# can quietly answer with this folder instead of the program's own.


def cache_folder(sub=""):
    """Return the folder the program may keep its intermediate state in."""
    # VPM_CACHE points the whole thing somewhere else. The suite sets
    # it: a test run has no business leaving envelopes, measurements
    # and a compiled recogniser in the cache of whoever runs it.
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

    One reader for both stores. A cache that only grows is one nobody
    dares to delete.
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

    Beside it and then moved into place: these files are read as
    measurements on every later start, and two runs writing one at the
    same moment still leave it whole -- one of them wins.
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

    Not the cache: that is the folder everybody may delete, and
    deleting it must not change the language the window speaks. So
    Application Support, not Caches; APPDATA, not LOCALAPPDATA.
    """
    base = os.environ.get("VPM_SETTINGS") or ""
    if not base:
        # A test run marks itself with VPM_SILENT and has no business in
        # the settings of whoever started it; a test with business here
        # names its own. Same guard as key_store_off_limits().
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
    # Only a write asks for the folder to be built: a run in which
    # nobody chooses must not leave an empty folder behind for looking.
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

# Kept under the file it was read from: fixed within a run, not
# within a test that repoints VPM_SETTINGS. Same shape as _API_KEY.
_SETTINGS = {}


def forget_settings():
    """Read the settings file again the next time it is asked for."""
    _SETTINGS.clear()


def read_settings(path):
    """That file as a dictionary, empty wherever it cannot be had.

    Every way this can go wrong ends in the same answer -- ask the
    system. A convenience that can stop a start is worse than none.
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

    The whole file is written back, so an entry this version knows
    nothing about survives it: an older copy started by accident does
    not throw away what a newer one wrote.
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
