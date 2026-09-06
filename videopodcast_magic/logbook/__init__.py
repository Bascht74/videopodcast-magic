# -*- coding: utf-8 -*-
"""The log this run leaves behind: where it goes, and what goes into it.

A piece of the program, read in by beside(): it cannot import the file
it was cut out of, so the program is handed in and bound below by name.
"""

# Put here by beside() before this file is read.
PROGRAM = PROGRAM

# Bound above the seam, so each is a copy and none is read late.
cache_folder = PROGRAM.cache_folder
os = PROGRAM.os
sys = PROGRAM.sys
time = PROGRAM.time

# __file__ is not among them: in here it names this file, while both
# places below mean the program, and read PROGRAM.__file__ to say so.

EXT_MARK = "[EXT]"

ENV_MARK = "[ENV]"

BAD_MARK = "[BAD]"

TIME_MARK = "[TIME]"

# When this run began. The bundle a Dock start goes through puts its
# own second into VPM_STARTED first: what happens before Python runs
# cannot be timed from inside it, and that is about ten seconds.
_BEGAN = time.time()


def mark_time(what):
    """Write down how far into the start this is, into the log only."""
    began, whence = _BEGAN, "this program"
    outside = (os.environ.get("VPM_STARTED") or "").strip()
    if outside.replace(".", "", 1).isdigit():
        began, whence = float(outside), "the click"
    log_aside("%s %s  %6.2f s since %s  %s"
              % (TIME_MARK, time.strftime("%H:%M:%S"),
                 time.time() - began, whence, what))


_LOG_ASIDE = []


def inside_folder(here, folder, paths=os.path):
    """Is that file inside this folder, however the two are spelled?

    One folder answers to more than one name: a link leads to it under
    another, and Python 3.10 on Windows spells the library folder lib
    where sysconfig spells it Lib. The path module is an argument so
    this machine can be asked what another makes of two names.
    """
    here = paths.normcase(paths.realpath(here))
    folder = paths.normcase(paths.realpath(folder))
    return here.startswith(folder + paths.sep)


def installed_by_a_package_manager():
    """The folder a package manager owns this file in, or "".

    Two things hang on it: an installed copy is not written over by
    the self-update, because something else keeps the record of which
    version is there; and it does not keep its log in pip's folder.
    """
    import sysconfig
    import site
    # site.USER_SITE, not getusersitepackages(): the call raises where
    # the user folder is switched off; the name is always there.
    owned = [sysconfig.get_paths().get(k) for k in ("purelib", "platlib")]
    owned.append(site.USER_SITE)
    for folder in owned:
        if folder and inside_folder(PROGRAM.__file__, folder):
            return folder
    return ""


def log_folder():
    """The folder a log belongs in on this system, or None.

    Neither the cache nor the settings: the cache is the one folder
    everybody may delete, and a setting follows somebody to the next
    machine while a log says what happened on this one. Every platform
    keeps a third place, named beside each branch below.
    """
    base = os.environ.get("VPM_LOGS") or ""
    if base:
        folder = os.path.join(base, "videopodcast-magic")
    elif os.environ.get("VPM_SILENT"):
        # A test run has no business in the log folder of whoever
        # started it; a test that does names its own VPM_LOGS.
        return cache_folder("logs")
    elif sys.platform == "darwin":
        # What Console.app shows.
        folder = os.path.expanduser("~/Library/Logs/videopodcast-magic")
    elif os.name == "nt":
        # LOCALAPPDATA, not APPDATA: a log must not travel with a
        # roaming profile. Its own folder, so emptying the cache keeps it.
        folder = os.path.join(os.environ.get("LOCALAPPDATA")
                              or os.path.expanduser("~"),
                              "videopodcast-magic", "Logs")
    else:
        # XDG names this one for logs in so many words.
        folder = os.path.join(os.environ.get("XDG_STATE_HOME")
                              or os.path.expanduser("~/.local/state"),
                              "videopodcast-magic")
    try:
        os.makedirs(folder, exist_ok=True)
    except OSError:
        return None
    return folder


def log_path():
    """Where the log goes: beside the program, or in the user's place.

    Beside the program it is found without searching. For an installed
    copy that is site-packages, which pip owns and writes over at the
    next install, so such a run -- or one that cannot write -- uses the
    place this system keeps logs.
    """
    if not installed_by_a_package_manager():
        here = os.path.dirname(os.path.abspath(PROGRAM.__file__))
        if os.path.isdir(here) and os.access(here, os.W_OK):
            return os.path.join(here, "videopodcast-magic.log")
    folder = log_folder()
    return os.path.join(folder, "videopodcast-magic.log") if folder else None


def log_aside(text):
    """Write one line into the log file only, never to the console.

    A diagnostic line landing between two progress bars tears them
    apart, so this goes past both descriptors into the file itself.
    """
    if not _LOG_ASIDE:
        try:
            where = log_path()
            _LOG_ASIDE.append(open(where, "a", buffering=1,
                                   encoding="utf-8", errors="replace")
                              if where else None)
        except Exception:
            _LOG_ASIDE.append(None)
    if _LOG_ASIDE[0] is None:
        return
    try:
        _LOG_ASIDE[0].write(text + "\n")
    except Exception:
        # A failed write fails again; stop rather than throw per line.
        _LOG_ASIDE[0] = None

# The same tool on the same file over and over -- nine stretches out
# of two files -- is held back and written as one line with totals.
_SAME_AGAIN = {"what": None, "times": 0, "seconds": 0.0}


def outside_say(tool, about, seconds=None, what=None):
    """One line about work that happens outside this program's own code.

    ffmpeg, ffprobe and the two models are where a run spends its
    minutes, and from outside one read and four reads look the same. So
    every measurement in the log is a call, or the line saying why not.
    """
    same = (tool, about, what)
    if _SAME_AGAIN["what"] == same and seconds is not None:
        _SAME_AGAIN["times"] += 1
        _SAME_AGAIN["seconds"] += seconds
        return
    outside_flush()
    if seconds is None:
        log_aside("%s %s  %-13s %-22s %s"
                  % (EXT_MARK, time.strftime("%H:%M:%S"), tool,
                     what or "started", about))
        return
    _SAME_AGAIN.update({"what": same, "times": 1, "seconds": seconds})

def outside_flush():
    """Write out what was held back, as one line."""
    held = _SAME_AGAIN["what"]
    if not held:
        return
    tool, about, what = held
    times, seconds = _SAME_AGAIN["times"], _SAME_AGAIN["seconds"]
    log_aside("%s %s  %-13s %-22s %s"
              % (EXT_MARK, time.strftime("%H:%M:%S"), tool,
                 what or ("%.2f s" % seconds if times == 1
                          else "%d calls, %.2f s" % (times, seconds)),
                 about))
    _SAME_AGAIN.update({"what": None, "times": 0, "seconds": 0.0})
