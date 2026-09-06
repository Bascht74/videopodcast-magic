# -*- coding: utf-8 -*-
"""What has been measured of a file, taken once and kept.

A piece of the program, read in by beside(): it cannot import the file
it was cut out of, so the program is handed in and bound below by name.
"""

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# Bound above the seam, so each is a copy and none is read late.
cache_folder = PROGRAM.cache_folder
clean_old_files = PROGRAM.clean_old_files
hashlib = PROGRAM.hashlib
json = PROGRAM.json
os = PROGRAM.os
outside_say = PROGRAM.outside_say
subprocess = PROGRAM.subprocess
write_beside_then_move = PROGRAM.write_beside_then_move


# =====================================================================
#  What has been measured of a file
#  --------------------------------

# An ffprobe call costs a process start and, on an external volume, a
# seek out to the disc; the interface asks the same thing over and over.
_PROBE = {}


def file_stamp(path):
    """Identify a file by what changes when it is written to.

    By the real path, not the one the caller typed: a symbolic link
    otherwise gives one file two names and has it measured twice. The
    result is a key and nothing else; no line reads the path back out.
    """
    try:
        s = os.stat(path)
    except OSError:
        return None
    return (os.path.realpath(path), int(s.st_mtime_ns), int(s.st_size))


def _ffprobe_text(path):
    return subprocess.run(["ffprobe", "-v", "error", "-print_format", "json",
                           "-show_format", "-show_streams", path],
                          capture_output=True).stdout


def probe_cache_path(api_key):
    """Where a measurement of a file is kept between runs, or None."""
    folder = cache_folder("probes")
    if not folder:
        return None
    mark = hashlib.sha1(repr(api_key).encode("utf-8")).hexdigest()[:32]
    return os.path.join(folder, mark + ".bin")


def probe_kept(api_key):
    """What was measured of this file before, or None to measure again."""
    file_path = probe_cache_path(api_key)
    if not file_path:
        return None
    try:
        with open(file_path, "rb") as f:
            got = f.read()
    except OSError:
        return None
    # An empty file is a write that was cut off, not a measurement.
    return got or None


def probe_keep(api_key, got):
    """Keep a measurement for the next run."""
    if got:
        write_beside_then_move(probe_cache_path(api_key), got)


def clean_probe_cache(days=30):
    """Discard stale probes; once per run is enough."""
    clean_old_files(cache_folder("probes"), days)


def probe_remember(name, path, work, keep=False, as_json=False):
    """Return a measured property of a file, asking only once.

    Keyed on size and modification time. *keep* makes the answer
    outlive the run, *as_json* is for one that is not text, and a kept
    answer carries the recipe in its *name* -- see recipe_mark.
    """
    stamp = file_stamp(path)
    if stamp is None:
        return work()
    api_key = (name,) + stamp
    if api_key in _PROBE:
        # Not said: asked thousands of times in a table rebuild, and a
        # line each would drown the log and cost more than the lookup.
        return _PROBE[api_key]
    got = probe_kept(api_key) if keep else None
    if got is not None and as_json:
        try:
            got = json.loads(got)
        except Exception:
            got = None          # half a write, or another version
    if got is not None:
        # Worth a line: this is the measurement that cost seconds.
        outside_say(name.split("-")[0], os.path.basename(path),
                    what="read back from the store")
    if got is None:
        got = work()
        if keep:
            probe_keep(api_key, json.dumps(got).encode("utf-8")
                       if as_json else got)
    if len(_PROBE) > 4000:
        _PROBE.clear()
    _PROBE[api_key] = got
    return _PROBE[api_key]


def probe_has(name, path):
    """Report whether this measurement of this file is already there."""
    stamp = file_stamp(path)
    return stamp is not None and (name,) + stamp in _PROBE


def ffprobe_json(path):
    """Return what ffprobe says about a file.

    Parsed afresh each time; a caller may change what it gets back.
    """
    out = probe_remember("ffprobe", path, lambda: _ffprobe_text(path),
                         keep=True)
    return json.loads(out or b"{}")
