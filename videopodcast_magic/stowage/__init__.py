# -*- coding: utf-8 -*-
"""Where the program puts things down between one run and the next.

The folder a run may sweep out again, the file that holds what somebody
chose, and the write that goes beside a file and is moved into place.
A piece of the program; the program is handed in and bound below.
"""

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# Bound above the seam, so each is a copy and none is read late.
FILE_FORMAT = PROGRAM.FILE_FORMAT
FROZEN_NAME = PROGRAM.FROZEN_NAME
T = PROGRAM.T
VERSION = PROGRAM.VERSION
hashlib = PROGRAM.hashlib
json = PROGRAM.json
path_key = PROGRAM.path_key
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
    folder = os.path.join(base, FROZEN_NAME, sub)
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


def kept_in_use(file_path):
    """Date a stored entry to now, because it was just read.

    The store is swept by age, so the age has to be the last use, not
    the writing: a transcript read every week would otherwise go after
    thirty days and the recording be listened to again.
    """
    try:
        os.utime(file_path, None)
    except (OSError, TypeError):
        return


def keep_newest_build(folder, prefix):
    """Discard every file under *prefix* but the one written last.

    Each build is named after what it was built from, so a program or
    compiler that changed leaves the old one behind, never used again;
    so does the note that a build was refused. The newest is the current
    one: a new build is only made when the current one is missing. What
    lacks the prefix -- a build under way in another copy -- stays.
    """
    try:
        names = [n for n in os.listdir(folder or "") if n.startswith(prefix)]
        ages = dict((n, os.path.getmtime(os.path.join(folder, n)))
                    for n in names)
    except OSError:
        return
    newest = max(names, key=lambda n: ages[n], default=None)
    for name in names:
        if name != newest:
            try:
                os.unlink(os.path.join(folder, name))
            except OSError:
                continue


def clean_kept_stores(days=30):
    """Let the stores of words, voices and recognisers go again.

    Words and separations by the time they were last read (see
    kept_in_use); the project file carries its separation itself. The
    speech recogniser not by age -- it is used on every run that
    listens -- but its old builds beside the current one.
    """
    clean_old_files(cache_folder("words"), days)
    clean_old_files(cache_folder("speakers"), days)
    clean_stage_store(days)
    keep_newest_build(cache_folder("speech"), "recogniser_")


def write_beside_then_move(file_path, data):
    """Write bytes so that no half-written file is ever read.

    Beside it and then moved into place: these files are read as
    measurements on every later start, and two runs writing one at the
    same moment still leave it whole -- one of them wins.
    """
    if not file_path:
        return
    beside = None
    try:
        fd, beside = tempfile.mkstemp(dir=os.path.dirname(file_path),
                                      prefix=".vpm_", suffix=".part")
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(beside, file_path)
    except OSError:
        # A write that did not arrive leaves no half file lying beside.
        try:
            os.unlink(beside or "")
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
    folder = os.path.join(base, FROZEN_NAME)
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


#------------------------------------------ What a stage worked out, kept

# Beyond this many the stage store keeps only the ones used last.
STAGE_KEEP_COUNT = 200


def stage_input(o):
    """A set in a stage's inputs, in an order that does not wander."""
    if isinstance(o, (set, frozenset)):
        return sorted(o, key=repr)
    raise TypeError("a stage input json cannot hold: %r" % type(o))


def stage_key(stage, files=(), **inputs):
    """The name a stage's result is kept under, or None if it has none.

    Built from everything the stage depends on: each file by its place,
    time and size (the place as path_key spells it, so one file reached
    two ways is one input), and every other input as it is given.
    Anything that changes changes the key.
    """
    # The stage names the file, so it may not lead out of the folder.
    if not str(stage).replace("_", "").isalnum():
        return None
    marks = []
    for p in files or ():
        seen = PROGRAM.file_fingerprint(p) or [None, None, None]
        marks.append([path_key(p), seen[1], seen[2]])
    try:
        body = json.dumps({"stage": stage, "files": marks,
                           "inputs": inputs}, sort_keys=True,
                          default=stage_input)
    except (TypeError, ValueError):
        return None
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()[:40]
    return "%s_%s" % (stage, digest)


def stage_file(key):
    """Where the entry under *key* lies in the cache, or None."""
    folder = cache_folder("stages") if key else None
    return os.path.join(folder, key + ".json") if folder else None


def stage_get(key, schema=1):
    """What was kept under *key*, or None wherever it cannot be trusted.

    A missing, broken or foreign entry is None, and so is one another
    version of the program or another shape of the stage wrote: the
    caller works the stage out again rather than read the wrong thing.
    """
    path = stage_file(key)
    try:
        with open(path or "", "rb") as f:
            kept = json.loads(f.read().decode("utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return None
    if not isinstance(kept, dict) or kept.get("key") != key \
            or kept.get("version") != VERSION \
            or kept.get("schema") != schema:
        return None
    kept_in_use(path)
    return kept.get("result")


def stage_put(key, result, schema=1):
    """Keep *result* under *key* for the next run. True if it went.

    Written beside and moved into place, so a reader never meets half
    an entry; the store is trimmed to its count on the way out.
    """
    path = stage_file(key)
    if not path or result is None:
        return False
    try:
        data = json.dumps({"key": key, "version": VERSION, "schema": schema,
                           "result": result}, sort_keys=True).encode("utf-8")
    except (TypeError, ValueError):
        return False
    write_beside_then_move(path, data)
    clean_stage_store()
    return os.path.isfile(path)


def clean_stage_store(days=None):
    """Let stage entries go by age, and beyond STAGE_KEEP_COUNT by use.

    The age as the other stores have it; the count because every slider
    moved in the window writes an entry of its own.
    """
    folder = cache_folder("stages")
    if days is not None:
        clean_old_files(folder, days)
    try:
        names = [n for n in os.listdir(folder or "") if n.endswith(".json")]
        ages = dict((n, os.path.getmtime(os.path.join(folder, n)))
                    for n in names)
    except OSError:
        return
    for name in sorted(names, key=lambda n: -ages[n])[STAGE_KEEP_COUNT:]:
        try:
            os.unlink(os.path.join(folder, name))
        except OSError:
            continue


#-------------------------------------- Whether a stored file may be read

def format_complaint(d):
    """Say why a stored file cannot be used, or return "".

    Where the format number differs the keys inside mean something else,
    and reading it anyway would quietly assign the wrong things.
    """
    if not isinstance(d, dict):
        return T("This is not a file of this program.")
    present = int(d.get("format") or 1)
    if present == FILE_FORMAT:
        return ""
    return T("This file was written by version %s in format %d; this one "
             "writes format %d. The names inside have changed since, so it "
             "cannot be read. Please set the run up again.",
             d.get("version") or "?", present, FILE_FORMAT)
